#!/usr/bin/env python3
"""Analyze the 30-auto-drop run on near-real specimen ``RW5F61`` (PR #67).

Follow-up to the two ``prc1kn`` drift-calibration runs
(``drop_test_drift_calibration_analysis.py``, ``..._calibration2_...``), now on
a **near-real specimen** (``RW5F61``: key-seat housings printed at both the top
and a bottom vertex; small TPU bubbles on the top tendon so still classed a
failed print) and with a **third accelerometer**: a low-sensitivity tri-axis
unit (9-10.5 mV/G) in the **bottom-vertex housing** on CH6/CH7/CH8.

Channel map (extends the input-output series):
  * CH5           — single-axis accelerometer wax-mounted on the **base plate**
    = nominal INPUT; the triggered channel (1000 G).  **This sensor fell off
    the plate during the campaign**, so part of this analysis is deciding
    per-capture whether CH5 is trustworthy.
  * CH2, CH3, CH4 — tri-axis in the **top-vertex key-seat** (wax + cable tie)
    = OUTPUT ("TOP").
  * CH6, CH7, CH8 — new tri-axis in the **bottom-vertex housing** (cable tie)
    = alternate input reference at the specimen base ("BOT").

32 captures exist for 30 conducted drops: the detached CH5 sensor produced
spurious triggers.  Deliverables:
  1. classify every capture (real impact vs spurious trigger) and locate the
     CH5 fall-off;
  2. burn-in detection + stabilized-phase OLS drift (per the drift-calibration
     request), run on the channels that stayed valid — TOP output, BOT input,
     and the fall-off-immune transmissibility T* = TOP/BOT;
  3. regression reliability (Durbin-Watson, Shapiro-Wilk, start sweep);
  4. mount-robust specimen damage indicators for RW5F61 (pulse width,
     rotation-invariant ringdown spectrum, per-axis migration, noise floors).

A capture is a REAL drop iff the top tri-axis resultant shows a genuine
impact (raw peak >= 500 G — real drops sit at ~4,700-5,100 G, spurious
captures at <= ~110 G, three orders of magnitude apart).
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, optimize, signal, stats

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "drop-tests" / "30drops-real" / "raw"
FIG = REPO / "data" / "drop-tests" / "30drops-real" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

TOP_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output, top-vertex key-seat
CH5 = 3  # single-axis on the base plate (triggered; fell off mid-campaign)
BOT_COLS = (4, 5, 6)  # CH6, CH7, CH8 — tri-axis, bottom-vertex housing

IMPACT_HALF_WIN_S = 0.0015  # +-1.5 ms window around the impact for peak search
BASELINE_S = 0.0028  # pre-trigger baseline window (nominal impact ~3.9 ms)
TP4_HEADER_LINES = 9  # TP4 CSV export: 8 metadata rows + 1 column-name row

RING_BAND_HZ = (100.0, 2000.0)  # structural ringdown band
RING_START_AFTER_IMPACT_S = 0.002
RING_LEN_S = 0.080

SPECIMEN = "RW5F61"  # near-real specimen (top+bottom housings, top-tendon bubbles)
N_CAPTURES = 32
N_DROPS_CONDUCTED = 30
REAL_IMPACT_FLOOR_G = 500.0  # real drops: TOP raw >= ~4,700 G; spurious: <= ~110 G
CH5_FULL_SCALE_G = 9442.9

# prc1kn drift-calibration #2 stabilized numbers for cross-run context
RUN2 = {"in_mean": 223.6, "in_cv": 1.74, "out_mean": 241.0, "out_cv": 0.64,
        "t_mean": 1.078, "t_cv": 1.95}


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (t, channels[N, 7]) = (time, [CH2..CH8])."""
    d = np.genfromtxt(path, skip_header=TP4_HEADER_LINES, delimiter=",",
                      usecols=(0, 1, 2, 3, 4, 5, 6, 7))
    return d[:, 0], d[:, 1:8]


def cfc_filter(x: np.ndarray, fs: float, cfc: int) -> np.ndarray:
    """SAE J211 phaseless Butterworth low-pass for a given CFC class."""
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


def windowed_peak(t: np.ndarray, a_g: np.ndarray, i_imp: int, dt: float) -> dict:
    """Peak |g|, peak time, half-amplitude width and Delta-v near the impact."""
    half = max(1, int(IMPACT_HALF_WIN_S / dt))
    lo0, hi0 = max(0, i_imp - half), min(len(a_g), i_imp + half)
    seg = a_g[lo0:hi0]
    j = int(np.argmax(np.abs(seg)))
    idx = lo0 + j
    peak = a_g[idx]
    peak_abs = abs(peak)

    thr = peak_abs / 2.0
    sign = np.sign(peak)
    over = (sign * a_g) >= thr
    lo = idx
    while lo > lo0 and over[lo - 1]:
        lo -= 1
    hi = idx
    while hi < hi0 - 1 and over[hi + 1]:
        hi += 1
    width = t[hi] - t[lo]
    a_ms2 = a_g * GRAVITY
    dv = integrate.trapezoid(a_ms2[lo : hi + 1], t[lo : hi + 1])
    return {
        "peak_abs_g": peak_abs,
        "t_peak_ms": t[idx] * 1e3,
        "pulse_width_ms": width * 1e3,
        "delta_v_ms": abs(dv),
    }


def ringdown_spectrum(t: np.ndarray, tri: np.ndarray, i_imp: int, fs: float) -> dict:
    """Rotation-invariant ringdown spectral indicators of a tri-axis block."""
    i0 = i_imp + int(RING_START_AFTER_IMPACT_S * fs)
    i1 = min(len(t), i0 + int(RING_LEN_S * fs))
    nper = min(4096, i1 - i0)
    psd_sum = None
    for c in range(tri.shape[1]):
        seg = tri[i0:i1, c] - np.mean(tri[i0:i1, c])
        f, p = signal.welch(seg, fs=fs, nperseg=nper)
        psd_sum = p if psd_sum is None else psd_sum + p
    band = (f >= RING_BAND_HZ[0]) & (f <= RING_BAND_HZ[1])
    fb, pb = f[band], psd_sum[band]
    return {
        "dom_freq_hz": float(fb[np.argmax(pb)]),
        "centroid_hz": float(np.sum(fb * pb) / np.sum(pb)),
    }


def resultant(tri: np.ndarray) -> np.ndarray:
    return np.sqrt(np.sum(tri**2, axis=1))


def cv(vals) -> float:
    a = np.asarray(vals, float)
    m = a.mean()
    return float(100.0 * a.std(ddof=1) / m) if m else float("nan")


def event_time(path: Path) -> datetime:
    with open(path) as fh:
        for line in fh:
            if line.startswith("EventTime:"):
                return datetime.strptime(line.split(":", 1)[1].strip(),
                                         "%m/%d/%Y %I:%M:%S %p")
    raise ValueError(f"no EventTime in {path}")


def analyze_capture(path: Path) -> dict:
    t, ch = load(path)
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    nb = max(1, int(BASELINE_S / dt))

    top = ch[:, TOP_COLS] - np.median(ch[:nb, TOP_COLS], axis=0)
    ch5 = ch[:, CH5] - np.median(ch[:nb, CH5])
    bot = ch[:, BOT_COLS] - np.median(ch[:nb, BOT_COLS], axis=0)

    top_res_raw = resultant(top)
    bot_res_raw = resultant(bot)

    # The impact is located on the TOP resultant over the whole record (NOT on
    # CH5 and NOT only in the first 10 ms): the detached CH5 sensor triggered
    # early on several captures, pushing the real impact to 5-35 ms.
    i_imp = int(np.argmax(top_res_raw))
    top_raw_pk = float(top_res_raw[i_imp])
    is_real = top_raw_pk >= REAL_IMPACT_FLOOR_G

    row = {
        "signal": None,  # filled by caller
        "event_time": event_time(path).isoformat(),
        "real_impact": bool(is_real),
        "t_imp_ms": float(t[i_imp] * 1e3),
        "top_raw_g": top_raw_pk,
        "ch5_raw_g": float(np.max(np.abs(ch5))),
        "bot_raw_g": float(np.max(bot_res_raw)),
    }
    if not is_real:
        return row

    top180 = np.stack([cfc_filter(top[:, j], fs, 180) for j in range(3)], axis=1)
    bot180 = np.stack([cfc_filter(bot[:, j], fs, 180) for j in range(3)], axis=1)
    res_top_180 = resultant(top180)
    res_bot_180 = resultant(bot180)
    ch5_180 = cfc_filter(ch5, fs, 180)

    m_top = windowed_peak(t, res_top_180, i_imp, dt)
    m_bot = windowed_peak(t, res_bot_180, i_imp, dt)
    m_ch5 = windowed_peak(t, ch5_180, i_imp, dt)
    top1000 = windowed_peak(
        t, resultant(np.stack([cfc_filter(top[:, j], fs, 1000) for j in range(3)], axis=1)),
        i_imp, dt)["peak_abs_g"]

    half = max(1, int(IMPACT_HALF_WIN_S / dt))
    lo, hi = max(0, i_imp - half), min(len(t), i_imp + half)
    axis_pk = [float(np.max(np.abs(top[lo:hi, j]))) for j in range(3)]
    ring = ringdown_spectrum(t, top, i_imp, fs)
    noise_top = [float(np.std(top[:nb, j])) for j in range(3)]
    noise_bot = [float(np.std(bot[:nb, j])) for j in range(3)]

    row.update({
        "top_1000_g": top1000,
        "top_180_g": m_top["peak_abs_g"],
        "bot_180_g": m_bot["peak_abs_g"],
        "ch5_180_g": m_ch5["peak_abs_g"],
        "t_star": m_top["peak_abs_g"] / m_bot["peak_abs_g"],
        "t_ch5": m_top["peak_abs_g"] / m_ch5["peak_abs_g"],
        "top_width_ms": m_top["pulse_width_ms"],
        "bot_dv_ms": m_bot["delta_v_ms"],
        "ch2_pk_g": axis_pk[0],
        "ch3_pk_g": axis_pk[1],
        "ch4_pk_g": axis_pk[2],
        "dom_freq_hz": ring["dom_freq_hz"],
        "centroid_hz": ring["centroid_hz"],
        "noise_top_g": noise_top,
        "noise_bot_g": noise_bot,
    })
    return row


def ols_full(x, y) -> dict:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    res = stats.linregress(x, y)
    resid = y - (res.intercept + res.slope * x)
    dw = float(np.sum(np.diff(resid) ** 2) / np.sum(resid**2)) if np.any(resid) else float("nan")
    sh_p = float(stats.shapiro(resid).pvalue) if n >= 3 else float("nan")
    tcrit = stats.t.ppf(0.975, n - 2)
    mean = float(np.mean(y))
    return {
        "n": n,
        "slope": float(res.slope),
        "slope_pct": float(100.0 * res.slope / mean),
        "ci_lo": float(res.slope - tcrit * res.stderr),
        "ci_hi": float(res.slope + tcrit * res.stderr),
        "p": float(res.pvalue),
        "r2": float(res.rvalue**2),
        "dw": dw,
        "shapiro_p": sh_p,
        "mean": mean,
        "cv": cv(y),
    }


def main() -> int:
    rows: list[dict] = []
    for sig in range(1, N_CAPTURES + 1):
        row = analyze_capture(RAW / f"30drops_with_real_Signal{sig}.csv")
        row["signal"] = sig
        rows.append(row)

    # ---------------- capture classification / fall-off forensics ----
    spurious = [r["signal"] for r in rows if not r["real_impact"]]
    real = [r for r in rows if r["real_impact"]]
    # number the real drops 1..len(real) in capture order
    for k, r in enumerate(real, start=1):
        r["drop"] = k
    print(f"\ncaptures: {N_CAPTURES} total = {len(real)} real drops + "
          f"{len(spurious)} spurious triggers {spurious}")
    print(f"conducted {N_DROPS_CONDUCTED} drops -> "
          f"{N_DROPS_CONDUCTED - len(real)} drop(s) never captured cleanly")

    # CH5 trustworthiness per real capture: with the sensor detached, its level
    # decouples from the structural response. Judge by T_ch5 = TOP180/CH5180
    # relative to the pre-fall-off captures, by trigger-to-impact latency, and
    # by proximity to CH5 full scale.
    print(f"\n{'sig':>3} {'drop':>4} {'t_imp':>6} {'CH5raw':>7} {'CH5/FS':>6} "
          f"{'CH5-180':>8} {'TOP180':>7} {'BOT180':>7} {'T*=T/B':>7} {'T/CH5':>6}")
    for r in rows:
        if not r["real_impact"]:
            print(f"{r['signal']:3d} {'--':>4} {r['t_imp_ms']:6.1f} {r['ch5_raw_g']:7.0f} "
                  f"{r['ch5_raw_g'] / CH5_FULL_SCALE_G:6.2f} {'--':>8} "
                  f"{r['top_raw_g']:7.0f} {r['bot_raw_g']:7.0f} {'--':>7} {'--':>6}   "
                  f"<- SPURIOUS (no impact)")
        else:
            print(f"{r['signal']:3d} {r['drop']:4d} {r['t_imp_ms']:6.1f} {r['ch5_raw_g']:7.0f} "
                  f"{r['ch5_raw_g'] / CH5_FULL_SCALE_G:6.2f} {r['ch5_180_g']:8.0f} "
                  f"{r['top_180_g']:7.0f} {r['bot_180_g']:7.0f} {r['t_star']:7.2f} "
                  f"{r['t_ch5']:6.2f}")

    drops = np.array([r["drop"] for r in real], float)
    top = np.array([r["top_180_g"] for r in real], float)
    bot = np.array([r["bot_180_g"] for r in real], float)
    tst = np.array([r["t_star"] for r in real], float)
    ch5v = np.array([r["ch5_180_g"] for r in real], float)
    tch5 = np.array([r["t_ch5"] for r in real], float)
    sigs = np.array([r["signal"] for r in real], int)
    last = int(drops[-1])

    # CH5 stability contrast: pre- vs post-first-spurious-capture
    first_spur = min(spurious) if spurious else None
    pre = sigs < first_spur
    print(f"\nCH5 CFC-180 pre-fall-off (signals < {first_spur}): "
          f"{ch5v[pre].mean():.0f} G, CV {cv(ch5v[pre]):.1f}%")
    print(f"CH5 CFC-180 post-fall-off: {ch5v[~pre].mean():.0f} G, CV {cv(ch5v[~pre]):.1f}%")
    print(f"BOT CFC-180 same split    : {bot[pre].mean():.0f} G (CV {cv(bot[pre]):.1f}%) -> "
          f"{bot[~pre].mean():.0f} G (CV {cv(bot[~pre]):.1f}%)")
    print(f"CH5 raw near full scale   : max {max(r['ch5_raw_g'] for r in real):.0f} G = "
          f"{max(r['ch5_raw_g'] for r in real) / CH5_FULL_SCALE_G * 100:.0f}% of "
          f"{CH5_FULL_SCALE_G:.0f} G")

    # ---------------- burn-in changepoint scan (TOP output) ----------
    print(f"\n=== burn-in changepoint scan (TOP CFC-180, OLS on drops k+1..{last}) ===\n")
    print(f"{'burn-in k':>9s} {'n':>3s} {'slope G/drop':>13s} {'%/drop':>8s} {'p':>7s}")
    scan = {}
    burn_in_k = None
    for k in range(0, 13):
        m = drops > k
        if m.sum() < 5:
            break
        o = ols_full(drops[m], top[m])
        scan[k] = o
        print(f"{k:9d} {o['n']:3d} {o['slope']:+13.3f} {o['slope_pct']:+8.3f} {o['p']:7.3f}")
        if burn_in_k is None and o["p"] > 0.05:
            burn_in_k = k
    if burn_in_k is None:
        burn_in_k = 5
        print(f"\n-> no k in 0..12 yields an n.s. trend; using SOP burn-in = {burn_in_k}")
    else:
        print(f"\n-> smallest k with n.s. seating trend: burn-in = {burn_in_k} drops")

    def expo(d, a, b, tau):
        return a - b * np.exp(-d / tau)

    p0 = (top[-5:].mean(), top[-5:].mean() - top[0], 2.0)
    try:
        popt, _ = optimize.curve_fit(expo, drops, top, p0=p0, maxfev=20000)
        a_fit, b_fit, tau = (float(v) for v in popt)
        print(f"exponential-approach fit: plateau {a_fit:.1f} G, amplitude {b_fit:.1f} G, "
              f"tau = {tau:.1f} drops")
    except RuntimeError:
        a_fit = b_fit = tau = float("nan")
        print("exponential-approach fit did not converge (no seating transient?)")

    # ---------------- stabilized-phase OLS ---------------------------
    stable = drops > burn_in_k
    xs = drops[stable]
    print(f"\n=== stabilized-phase OLS (drops {burn_in_k + 1}..{last}, "
          f"n = {int(stable.sum())}) ===\n")
    results = {}
    for name, y in [("BOT input", bot[stable]), ("TOP output", top[stable]),
                    ("T* TOP/BOT", tst[stable]), ("CH5 (suspect)", ch5v[stable]),
                    ("T TOP/CH5", tch5[stable])]:
        o = ols_full(xs, y)
        results[name] = o
        print(f"  {name:13s}: mean {o['mean']:8.3f}  CV {o['cv']:6.2f}%   "
              f"slope {o['slope']:+9.4f}/drop ({o['slope_pct']:+.3f}%/drop)   "
              f"95% CI [{o['ci_lo']:+.4f}, {o['ci_hi']:+.4f}]   "
              f"p = {o['p']:.3f}  R² = {o['r2']:.3f}  DW = {o['dw']:.2f}  "
              f"Shapiro p = {o['shapiro_p']:.2f}")

    print("\n  start-drop sensitivity (TOP output %/drop):")
    sens = {}
    for k in range(max(1, burn_in_k - 3), burn_in_k + 7):
        m = drops > k
        if m.sum() < 5:
            break
        o = ols_full(drops[m], top[m])
        sens[k] = o
        print(f"    start {k + 1:2d}: {o['slope_pct']:+.3f}%/drop  (p = {o['p']:.3f})")

    mid = xs[len(xs) // 2]
    o_h1 = ols_full(xs[xs <= mid], top[stable][xs <= mid])
    o_h2 = ols_full(xs[xs > mid], top[stable][xs > mid])
    print(f"\n  split-half check (TOP): drops {int(xs[0])}-{int(mid)}: "
          f"{o_h1['slope_pct']:+.3f}%/drop (p = {o_h1['p']:.2f}); "
          f"drops {int(mid) + 1}-{last}: {o_h2['slope_pct']:+.3f}%/drop "
          f"(p = {o_h2['p']:.2f})")

    # ---------------- per-axis migration (top seat health) -----------
    print("\n=== per-axis peak migration, TOP tri-axis (raw |peak|) ===\n")
    axis_ols = {}
    for name, key in [("CH2", "ch2_pk_g"), ("CH3", "ch3_pk_g"), ("CH4", "ch4_pk_g")]:
        y = np.array([r[key] for r in real], float)
        o = ols_full(drops, y)
        axis_ols[name] = o
        print(f"  {name}: {y[0]:6.0f} G (drop 1) -> {y[-1]:6.0f} G (drop {last})   "
              f"slope {o['slope']:+7.1f} G/drop ({o['slope_pct']:+.2f}%/drop)  p = {o['p']:.1e}")

    # ---------------- specimen damage indicators ---------------------
    print("\n=== specimen damage indicators (mount-robust) ===\n")
    dmg = {}
    for key, label in [("top_width_ms", "output pulse width (ms)"),
                       ("dom_freq_hz", "ringdown dominant freq (Hz)"),
                       ("centroid_hz", "ringdown spectral centroid (Hz)"),
                       ("bot_dv_ms", "BOT input Δv (m/s)")]:
        y = np.array([r[key] for r in real], float)
        o = ols_full(drops, y)
        dmg[key] = o
        print(f"  {label:34s}: mean {o['mean']:8.2f}  CV {o['cv']:5.2f}%  "
              f"slope {o['slope_pct']:+.3f}%/drop  p = {o['p']:.3f}")
    ntop = np.array([r["noise_top_g"] for r in real], float)
    nbot = np.array([r["noise_bot_g"] for r in real], float)
    print(f"  pre-impact noise RMS TOP (CH2/3/4): first 5 "
          f"{ntop[:5].mean(axis=0).round(2).tolist()} G -> last 5 "
          f"{ntop[-5:].mean(axis=0).round(2).tolist()} G")
    print(f"  pre-impact noise RMS BOT (CH6/7/8): first 5 "
          f"{nbot[:5].mean(axis=0).round(2).tolist()} G -> last 5 "
          f"{nbot[-5:].mean(axis=0).round(2).tolist()} G")

    print(f"\n=== vs prc1kn drift-calibration #2 (stabilized) ===\n")
    print(f"  input : {RUN2['in_mean']:.1f} G (CV {RUN2['in_cv']:.2f}%) [CH5 base plate] -> "
          f"{results['BOT input']['mean']:.1f} G (CV {results['BOT input']['cv']:.2f}%) "
          f"[CH6-8 bottom vertex]")
    print(f"  output: {RUN2['out_mean']:.1f} G (CV {RUN2['out_cv']:.2f}%) -> "
          f"{results['TOP output']['mean']:.1f} G (CV {results['TOP output']['cv']:.2f}%)")
    print(f"  T     : {RUN2['t_mean']:.3f} (CV {RUN2['t_cv']:.2f}%) [OUT/base] -> "
          f"{results['T* TOP/BOT']['mean']:.3f} (CV {results['T* TOP/BOT']['cv']:.2f}%) "
          f"[TOP/BOT]")

    # ---------------- figures ---------------------------------------
    # Fig 1: capture classification — raw peaks per capture, spurious flagged
    fig, ax = plt.subplots(figsize=(11.5, 5.5))
    s_all = np.array([r["signal"] for r in rows], float)
    ax.semilogy(s_all, [r["top_raw_g"] for r in rows], "s-", ms=5, color="tab:red",
                label="TOP |tri-axis| raw peak (CH2-4, key-seat)")
    ax.semilogy(s_all, [r["bot_raw_g"] for r in rows], "^-", ms=5, color="tab:green",
                label="BOT |tri-axis| raw peak (CH6-8, bottom housing)")
    ax.semilogy(s_all, [r["ch5_raw_g"] for r in rows], "o-", ms=5, color="tab:blue",
                label="CH5 raw |peak| (base plate, trigger — fell off)")
    ax.axhline(REAL_IMPACT_FLOOR_G, color="k", ls=":", lw=1,
               label=f"real-impact floor ({REAL_IMPACT_FLOOR_G:.0f} G on TOP)")
    for s in spurious:
        ax.axvspan(s - 0.4, s + 0.4, color="orange", alpha=0.25)
    ax.set(xlabel="capture (Signal #)", ylabel="raw |peak| (G, log scale)",
           title=f"{SPECIMEN}: 32 captures for 30 drops — spurious triggers "
                 f"{spurious} (shaded) carry no specimen impact")
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(FIG / "01_capture_classification.png", dpi=130)
    plt.close(fig)

    # Fig 2: CH5 vs BOT as input reference across the campaign
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11.5, 7.5), sharex=True)
    a1.plot(drops, ch5v, "o-", ms=4, color="tab:blue", label="CH5 CFC-180 (base plate, detached)")
    a1.plot(drops, bot, "^-", ms=4, color="tab:green", label="BOT CFC-180 (CH6-8 resultant)")
    a1.plot(drops, top, "s-", ms=4, color="tab:red", label="TOP CFC-180 (CH2-4 resultant)")
    for s in spurious:
        k = np.searchsorted(sigs, s)
        a1.axvline(k + 0.5, color="orange", ls="--", lw=1)
    a1.set(ylabel="CFC-180 peak |g| (G)",
           title=f"{SPECIMEN}: per-drop peaks — CH5 steps between levels after fall-off "
                 "(orange dashes = spurious-trigger instants) while TOP/BOT stay flat")
    a1.legend(fontsize=8)
    a1.grid(alpha=0.3)
    a2.plot(drops, tch5, "o-", ms=4, color="tab:blue", label="T = TOP/CH5 (input fell off)")
    a2.plot(drops, tst, "d-", ms=4, color="tab:purple", label="T* = TOP/BOT (fall-off-immune)")
    a2.set(xlabel="real drop # (capture order)", ylabel="transmissibility",
           title="T on the detached CH5 is not usable; T* = TOP/BOT stays tight")
    a2.legend(fontsize=8)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "02_ch5_vs_bot_input.png", dpi=130)
    plt.close(fig)

    # Fig 3: stabilized-phase OLS (TOP output + T*)
    fig, (b1, b2) = plt.subplots(1, 2, figsize=(12, 5))
    for ax_, y, name, col in [(b1, top[stable], "TOP output CFC-180 (G)", "tab:red"),
                              (b2, tst[stable], "T* = TOP/BOT (CFC-180)", "tab:purple")]:
        o = ols_full(xs, y)
        ax_.plot(xs, y, "o", color=col)
        fit = o["mean"] - o["slope"] * xs.mean() + o["slope"] * xs
        ax_.plot(xs, fit, "-", color="k", lw=1.5,
                 label=f"OLS {o['slope']:+.3f}/drop ({o['slope_pct']:+.3f}%/drop)\n"
                       f"p = {o['p']:.2f}, R² = {o['r2']:.2f}")
        lo_fit = o["mean"] - o["ci_lo"] * xs.mean() + o["ci_lo"] * xs
        hi_fit = o["mean"] - o["ci_hi"] * xs.mean() + o["ci_hi"] * xs
        ax_.fill_between(xs, np.minimum(lo_fit, hi_fit), np.maximum(lo_fit, hi_fit),
                         color=col, alpha=0.15, label="95% CI on slope")
        ax_.set(xlabel="real drop #", ylabel=name)
        ax_.legend(fontsize=8)
        ax_.grid(alpha=0.3)
    fig.suptitle(f"{SPECIMEN}: stabilized-phase drift (drops {burn_in_k + 1}-{last})")
    fig.tight_layout()
    fig.savefig(FIG / "03_stabilized_ols.png", dpi=130)
    plt.close(fig)

    # Fig 4: damage indicators + top-seat axis migration
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))
    for ax_, key, label in [(axes[0], "top_width_ms", "output half-amplitude\npulse width (ms)"),
                            (axes[1], "dom_freq_hz",
                             "ringdown dominant freq (Hz)\n100–2000 Hz, rotation-invariant"),
                            (axes[2], "centroid_hz", "ringdown spectral centroid (Hz)")]:
        y = np.array([r[key] for r in real], float)
        o = dmg[key]
        ax_.plot(drops, y, "o-", ms=4, color="tab:red")
        ax_.set(xlabel="real drop #",
                title=f"{label}\nslope {o['slope_pct']:+.3f}%/drop, p = {o['p']:.2f}")
        ax_.grid(alpha=0.3)
    fig.suptitle(f"{SPECIMEN}: mount-robust specimen damage indicators — 30-drop campaign")
    fig.tight_layout()
    fig.savefig(FIG / "04_damage_indicators.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 5.5))
    for key, name, col in [("ch2_pk_g", "CH2", "tab:green"),
                           ("ch3_pk_g", "CH3", "tab:orange"),
                           ("ch4_pk_g", "CH4", "tab:red")]:
        ax.plot(drops, [r[key] for r in real], "o-", ms=4, color=col, label=f"{name} raw |peak|")
    ax.plot(drops, [r["top_raw_g"] for r in real], "k--", lw=1, label="|resultant| raw peak")
    ax.set(xlabel="real drop #", ylabel="raw |peak| per axis (G)",
           title=f"{SPECIMEN}: top-seat per-axis impact peak (wax + cable tie)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "05_axis_migration.png", dpi=130)
    plt.close(fig)

    # ---------------- machine-readable summary -----------------------
    summary = {
        "specimen": SPECIMEN,
        "n_captures": N_CAPTURES,
        "n_drops_conducted": N_DROPS_CONDUCTED,
        "spurious_captures": spurious,
        "n_real_drops_captured": len(real),
        "burn_in_drops": burn_in_k,
        "expo_fit": {"plateau_g": a_fit, "amplitude_g": b_fit, "tau_drops": tau},
        "stabilized_window": [int(burn_in_k) + 1, last],
        "stabilized_ols": results,
        "split_half": {"first": o_h1, "second": o_h2},
        "burn_in_scan": {str(k): v for k, v in scan.items()},
        "start_drop_sensitivity": {str(k): v for k, v in sens.items()},
        "axis_migration": axis_ols,
        "damage_indicators": dmg,
        "per_capture": rows,
    }
    with open(FIG / "30drops_real_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)

    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
