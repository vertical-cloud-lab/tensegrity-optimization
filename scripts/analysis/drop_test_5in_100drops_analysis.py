#!/usr/bin/env python3
"""Analyze the 5-in 100-drop campaign (PR #67, "5 in height 100 drops").

@ctrhjk lowered the drop height from 13 in to 5 in — the "Option A" fix for
the under-ranged low-range bottom tri-axis (CH6-8, ~1 kG FS), which exceeded
its full scale on 85/100 (13-in 100-drop run) and 40/50 (CH4-trigger run)
drops. Everything else matches the CH4-trigger campaign: specimen ``RW5F61``,
trigger on CH4 at 1000 G, taped CH5 on the base plate, taped housing
entrances on both key-seats, 200 ms / 125 kHz / 2% (4 ms) pre-trigger.

Channel map:
  * CH2, CH3, CH4 — tri-axis in the **top-vertex key-seat** = OUTPUT ("TOP");
    **CH4 is the trigger channel (1000 G)**.
  * CH5           — single-axis on the **base plate** (taped) = plate input.
  * CH6, CH7, CH8 — low-range tri-axis in the **bottom-vertex housing**
    ("BOT") = specimen-base input reference.

Deliverables:
  1. capture classification + trigger health at the reduced severity (the
     CH4 margin over 1000 G was predicted ~2.0x at 5 in — verify);
  2. saturation audit — does 5 in bring CH8 inside its full scale, and how
     do the measured levels compare with the sqrt(h) prediction?
  3. burn-in + stabilized-phase OLS drift on TOP, CH5, BOT, T = TOP/CH5,
     T* = TOP/BOT, with reliability checks;
  4. mount-robust specimen damage indicators (RW5F61 cumulative history).
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
RAW = REPO / "data" / "drop-tests" / "5in-100drops" / "raw"
FIG = REPO / "data" / "drop-tests" / "5in-100drops" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

TOP_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output, top-vertex key-seat
CH4 = 2  # trigger channel (1000 G)
CH5 = 3  # single-axis on the base plate (taped)
BOT_COLS = (4, 5, 6)  # CH6, CH7, CH8 — low-range tri-axis, bottom-vertex housing

FULL_SCALE_G = {"CH2": 14492.8, "CH3": 14992.5, "CH4": 13624.0, "CH5": 9442.9,
                "CH6": 1002.0, "CH7": 991.1, "CH8": 989.1}

TRIGGER_LEVEL_G = 1000.0
PRETRIGGER_S = 0.004  # 2% of 200 ms

IMPACT_HALF_WIN_S = 0.0015  # +-1.5 ms window around the impact for peak search
BASELINE_S = 0.0028  # pre-trigger baseline window (nominal impact ~4.0 ms)
TP4_HEADER_LINES = 9  # TP4 CSV export: 8 metadata rows + 1 column-name row

RING_BAND_HZ = (100.0, 2000.0)  # structural ringdown band
RING_START_AFTER_IMPACT_S = 0.002
RING_LEN_S = 0.080

N_CAPTURES = 100
REAL_IMPACT_FLOOR_G = 300.0  # at 5 in the TOP raw resultant is still ~kG scale

HEIGHT_RATIO = (5.0 / 13.0) ** 0.5  # sqrt(h) severity prediction vs the 13-in runs

# CH4-trigger 50-drop campaign at 13 in (same rig/trigger config), stabilized phase
RUN13 = {"top_mean": 226.7, "top_cv": 1.55, "ch5_mean": 236.3, "ch5_cv": 1.15,
         "t_ch5_mean": 0.960, "t_ch5_cv": 1.20, "ch4_raw_mean": 3472.0,
         "ch5_raw_max": 8100.0, "ch8_median_fs": 1.050, "top_width_ms": 1.514,
         "burn_in": 10}


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
    ch4 = top[:, 2]  # baseline-corrected trigger channel
    ch5 = ch[:, CH5] - np.median(ch[:nb, CH5])
    bot = ch[:, BOT_COLS] - np.median(ch[:nb, BOT_COLS], axis=0)

    top_res_raw = resultant(top)
    bot_res_raw = resultant(bot)

    i_imp = int(np.argmax(top_res_raw))
    top_raw_pk = float(top_res_raw[i_imp])
    is_real = top_raw_pk >= REAL_IMPACT_FLOOR_G

    # trigger forensics on CH4: first |crossing| of the 1000 G level.
    # With a 2% pre-trigger that crossing should sit at ~4.000 ms.
    over = np.abs(ch4) >= TRIGGER_LEVEL_G
    i_x = int(np.argmax(over)) if over.any() else -1
    t_x_ms = float(t[i_x] * 1e3) if i_x >= 0 else float("nan")
    # quiet check ends at 3.5 ms so the impact's own rising edge (which by
    # construction approaches the level just before the crossing) is excluded
    pre = np.abs(ch4[t < 0.0035])
    pre_max_g = float(pre.max()) if len(pre) else 0.0

    sat = {}
    for name, col in [("CH2", 0), ("CH3", 1), ("CH4", 2), ("CH5", 3),
                      ("CH6", 4), ("CH7", 5), ("CH8", 6)]:
        x = np.abs(ch[:, col] - np.median(ch[:nb, col]))
        pk = float(x.max())
        sat[name] = {
            "peak_g": pk,
            "frac_fs": pk / FULL_SCALE_G[name],
            "n_pinned": int((x >= 0.995 * pk).sum()) if pk >= 0.95 * FULL_SCALE_G[name] else 0,
        }

    row = {
        "signal": None,  # filled by caller
        "event_time": event_time(path).isoformat(),
        "real_impact": bool(is_real),
        "t_imp_ms": float(t[i_imp] * 1e3),
        "trig_cross_ms": t_x_ms,
        "pre_trigger_max_g": pre_max_g,
        "ch4_raw_g": float(np.max(np.abs(ch4))),
        "top_raw_g": top_raw_pk,
        "ch5_raw_g": float(np.max(np.abs(ch5))),
        "bot_raw_g": float(np.max(bot_res_raw)),
        "sat": sat,
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

    half = max(1, int(IMPACT_HALF_WIN_S / dt))
    lo, hi = max(0, i_imp - half), min(len(t), i_imp + half)
    top_axis_pk = [float(np.max(np.abs(top[lo:hi, j]))) for j in range(3)]
    bot_axis_pk = [float(np.max(np.abs(bot[lo:hi, j]))) for j in range(3)]
    ring = ringdown_spectrum(t, top, i_imp, fs)
    noise_top = [float(np.std(top[:nb, j])) for j in range(3)]
    noise_bot = [float(np.std(bot[:nb, j])) for j in range(3)]

    row.update({
        "top_180_g": m_top["peak_abs_g"],
        "bot_180_g": m_bot["peak_abs_g"],
        "ch5_180_g": m_ch5["peak_abs_g"],
        "t_star": m_top["peak_abs_g"] / m_bot["peak_abs_g"],
        "t_ch5": m_top["peak_abs_g"] / m_ch5["peak_abs_g"],
        "top_width_ms": m_top["pulse_width_ms"],
        "bot_dv_ms": m_bot["delta_v_ms"],
        "ch5_dv_ms": m_ch5["delta_v_ms"],
        "ch2_pk_g": top_axis_pk[0],
        "ch3_pk_g": top_axis_pk[1],
        "ch4_pk_g": top_axis_pk[2],
        "ch6_pk_g": bot_axis_pk[0],
        "ch7_pk_g": bot_axis_pk[1],
        "ch8_pk_g": bot_axis_pk[2],
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
        row = analyze_capture(RAW / f"5in_100drops_Signal{sig}.csv")
        row["signal"] = sig
        rows.append(row)

    # ---------------- capture classification + trigger health --------
    spurious = [r["signal"] for r in rows if not r["real_impact"]]
    real = [r for r in rows if r["real_impact"]]
    for k, r in enumerate(real, start=1):
        r["drop"] = k
    times = [datetime.fromisoformat(r["event_time"]) for r in rows]
    gaps = np.array([(b - a).total_seconds() for a, b in zip(times, times[1:])])
    t_imps = np.array([r["t_imp_ms"] for r in real])
    t_cross = np.array([r["trig_cross_ms"] for r in real])
    ch4_pks = np.array([r["ch4_raw_g"] for r in real])
    pre_max = np.array([r["pre_trigger_max_g"] for r in real])

    print("=== 5-in 100-drop campaign: capture classification + trigger health ===\n")
    print(f"captures: {N_CAPTURES} total = {len(real)} real drops + "
          f"{len(spurious)} spurious {spurious}")
    print(f"cadence: median {np.median(gaps):.0f} s (range {gaps.min():.0f}-{gaps.max():.0f} s); "
          f"campaign span {(times[-1] - times[0]).total_seconds() / 60:.0f} min")
    print(f"CH4 first crossing of {TRIGGER_LEVEL_G:.0f} G: "
          f"{t_cross.mean():.3f} +- {t_cross.std():.3f} ms "
          f"(range {t_cross.min():.3f}-{t_cross.max():.3f}; nominal pre-trigger 4.000 ms)")
    print(f"impact (TOP resultant argmax): {t_imps.mean():.2f} +- {t_imps.std():.2f} ms")
    print(f"CH4 raw |peak|: {ch4_pks.mean():.0f} +- {ch4_pks.std():.0f} G "
          f"(range {ch4_pks.min():.0f}-{ch4_pks.max():.0f}) -> trigger margin "
          f"{(ch4_pks / TRIGGER_LEVEL_G).min():.2f}-{(ch4_pks / TRIGGER_LEVEL_G).max():.2f}x")
    print(f"pre-impact quiet: max |CH4| before 3.5 ms "
          f"{pre_max.max():.0f} G ({100 * pre_max.max() / TRIGGER_LEVEL_G:.0f}% of level)")

    # ---------------- saturation audit + sqrt(h) check ---------------
    print("\n=== saturation audit (raw |peak| vs nominal full scale) ===\n")
    sat_summary = {}
    for name in FULL_SCALE_G:
        fr = np.array([r["sat"][name]["frac_fs"] for r in rows])
        n95 = int((fr >= 0.95).sum())
        n_over = int((fr > 1.0).sum())
        pin_max = max(r["sat"][name]["n_pinned"] for r in rows)
        sat_summary[name] = {"full_scale_g": FULL_SCALE_G[name],
                             "median_frac_fs": float(np.median(fr)),
                             "max_frac_fs": float(fr.max()),
                             "n_ge_95pct_fs": n95, "n_over_fs": n_over,
                             "max_pinned_samples": pin_max}
        print(f"  {name}: FS {FULL_SCALE_G[name]:8.1f} G   median {100 * np.median(fr):5.1f}% FS   "
              f"max {100 * fr.max():5.1f}% FS   >=95% FS on {n95:3d}/{N_CAPTURES}   "
              f">FS on {n_over:3d}/{N_CAPTURES}   worst flat-top {pin_max} samples")

    print(f"\n  sqrt(h) severity check vs the 13-in CH4-trigger run "
          f"(predicted ratio {HEIGHT_RATIO:.2f}):")
    ch5_raw = np.array([r["ch5_raw_g"] for r in real])
    ch8_fs = np.array([r["sat"]["CH8"]["frac_fs"] for r in rows])
    print(f"    CH4 raw |peak| : {RUN13['ch4_raw_mean']:.0f} G -> {ch4_pks.mean():.0f} G "
          f"(measured ratio {ch4_pks.mean() / RUN13['ch4_raw_mean']:.2f})")
    print(f"    CH8 median %FS : {100 * RUN13['ch8_median_fs']:.0f}% -> "
          f"{100 * np.median(ch8_fs):.0f}%")

    drops = np.array([r["drop"] for r in real], float)
    top = np.array([r["top_180_g"] for r in real], float)
    bot = np.array([r["bot_180_g"] for r in real], float)
    tst = np.array([r["t_star"] for r in real], float)
    ch5v = np.array([r["ch5_180_g"] for r in real], float)
    tch5 = np.array([r["t_ch5"] for r in real], float)
    last = int(drops[-1])

    # ---------------- burn-in changepoint scan (TOP output) ----------
    print(f"\n=== burn-in changepoint scan (TOP CFC-180, OLS on drops k+1..{last}) ===\n")
    print(f"{'burn-in k':>9s} {'n':>3s} {'slope G/drop':>13s} {'%/drop':>8s} {'p':>7s}")
    scan = {}
    burn_in_k = None
    for k in range(0, 21):
        m = drops > k
        if m.sum() < 5:
            break
        o = ols_full(drops[m], top[m])
        scan[k] = o
        print(f"{k:9d} {o['n']:3d} {o['slope']:+13.3f} {o['slope_pct']:+8.3f} {o['p']:7.3f}")
        if burn_in_k is None and o["p"] > 0.05:
            burn_in_k = k
    if burn_in_k is None:
        burn_in_k = 10
        print(f"\n-> no k in 0..20 yields an n.s. trend; using SOP burn-in = {burn_in_k} "
              "(trend is campaign-scale, not a seating transient — see OLS section)")
    else:
        print(f"\n-> smallest k with n.s. seating trend: burn-in = {burn_in_k} drops")

    def expo(d, a, b, tau):
        return a - b * np.exp(-d / tau)

    p0 = (top[-10:].mean(), top[-10:].mean() - top[0], 3.0)
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
                    ("T* TOP/BOT", tst[stable]), ("CH5 plate", ch5v[stable]),
                    ("T TOP/CH5", tch5[stable])]:
        o = ols_full(xs, y)
        results[name] = o
        print(f"  {name:13s}: mean {o['mean']:8.3f}  CV {o['cv']:6.2f}%   "
              f"slope {o['slope']:+9.4f}/drop ({o['slope_pct']:+.3f}%/drop)   "
              f"95% CI [{o['ci_lo']:+.4f}, {o['ci_hi']:+.4f}]   "
              f"p = {o['p']:.2e}  R² = {o['r2']:.3f}  DW = {o['dw']:.2f}  "
              f"Shapiro p = {o['shapiro_p']:.2f}")

    print("\n  start-drop sensitivity (TOP output %/drop):")
    sens = {}
    for k in range(0, 51, 10):
        m = drops > k
        if m.sum() < 10:
            break
        o = ols_full(drops[m], top[m])
        sens[k] = o
        print(f"    start {k + 1:2d}: {o['slope_pct']:+.3f}%/drop  (p = {o['p']:.2e})")

    mid = xs[len(xs) // 2]
    o_h1 = ols_full(xs[xs <= mid], top[stable][xs <= mid])
    o_h2 = ols_full(xs[xs > mid], top[stable][xs > mid])
    print(f"\n  split-half check (TOP): drops {int(xs[0])}-{int(mid)}: "
          f"{o_h1['slope_pct']:+.3f}%/drop (p = {o_h1['p']:.2e}); "
          f"drops {int(mid) + 1}-{last}: {o_h2['slope_pct']:+.3f}%/drop "
          f"(p = {o_h2['p']:.2e})")

    # ---------------- per-axis migration (seat health) ---------------
    print("\n=== per-axis raw |peak| migration ===\n")
    axis_ols = {}
    for name, key in [("CH2", "ch2_pk_g"), ("CH3", "ch3_pk_g"), ("CH4", "ch4_pk_g"),
                      ("CH6", "ch6_pk_g"), ("CH7", "ch7_pk_g"), ("CH8", "ch8_pk_g")]:
        y = np.array([r[key] for r in real], float)
        o = ols_full(drops, y)
        axis_ols[name] = o
        print(f"  {name}: {y[:5].mean():6.0f} G (first 5) -> {y[-5:].mean():6.0f} G (last 5)   "
              f"slope {o['slope']:+7.1f} G/drop ({o['slope_pct']:+.2f}%/drop)  p = {o['p']:.1e}")

    # ---------------- specimen damage indicators ---------------------
    print("\n=== specimen damage indicators (mount-robust) ===\n")
    dmg = {}
    for key, label in [("top_width_ms", "output pulse width (ms)"),
                       ("dom_freq_hz", "ringdown dominant freq (Hz)"),
                       ("centroid_hz", "ringdown spectral centroid (Hz)"),
                       ("ch5_dv_ms", "plate input Δv (m/s)")]:
        y = np.array([r[key] for r in real], float)
        o = ols_full(drops, y)
        dmg[key] = o
        print(f"  {label:34s}: mean {o['mean']:8.2f}  CV {o['cv']:5.2f}%  "
              f"slope {o['slope_pct']:+.3f}%/drop  p = {o['p']:.2e}")
    ntop = np.array([r["noise_top_g"] for r in real], float)
    nbot = np.array([r["noise_bot_g"] for r in real], float)
    print(f"  pre-impact noise RMS TOP (CH2/3/4): first 5 "
          f"{ntop[:5].mean(axis=0).round(2).tolist()} G -> last 5 "
          f"{ntop[-5:].mean(axis=0).round(2).tolist()} G")
    print(f"  pre-impact noise RMS BOT (CH6/7/8): first 5 "
          f"{nbot[:5].mean(axis=0).round(2).tolist()} G -> last 5 "
          f"{nbot[-5:].mean(axis=0).round(2).tolist()} G")

    print(f"\n=== vs RW5F61 CH4-trigger run at 13 in (stabilized) ===\n")
    print(f"  TOP   : {RUN13['top_mean']:.1f} G (CV {RUN13['top_cv']:.2f}%) -> "
          f"{results['TOP output']['mean']:.1f} G (CV {results['TOP output']['cv']:.2f}%)")
    print(f"  CH5   : {RUN13['ch5_mean']:.1f} G (CV {RUN13['ch5_cv']:.2f}%) -> "
          f"{results['CH5 plate']['mean']:.1f} G (CV {results['CH5 plate']['cv']:.2f}%)")
    print(f"  T/CH5 : {RUN13['t_ch5_mean']:.3f} (CV {RUN13['t_ch5_cv']:.2f}%) -> "
          f"{results['T TOP/CH5']['mean']:.3f} (CV {results['T TOP/CH5']['cv']:.2f}%)")

    # ---------------- figures ---------------------------------------
    # Fig 1: full-series raw peaks + trigger health
    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(12, 10.5), sharex=True,
                                     gridspec_kw={"height_ratios": [3, 1.4, 1]})
    s_all = np.array([r["signal"] for r in rows], float)
    a1.plot(s_all, [r["top_raw_g"] for r in rows], "s-", ms=3.5, color="tab:red",
            label="TOP |tri-axis| raw peak (CH2-4, key-seat)")
    a1.plot(s_all, [r["ch4_raw_g"] for r in rows], "x-", ms=4, color="tab:brown",
            label="CH4 raw |peak| (trigger channel)")
    a1.plot(s_all, [r["ch5_raw_g"] for r in rows], "o-", ms=3.5, color="tab:blue",
            label="CH5 raw |peak| (base plate, taped)")
    a1.plot(s_all, [r["bot_raw_g"] for r in rows], "^-", ms=3.5, color="tab:green",
            label="BOT |tri-axis| raw peak (CH6-8, low-range)")
    a1.axhline(TRIGGER_LEVEL_G, color="k", ls=":", lw=1.2, label="1000 G trigger level")
    a1.set(ylabel="raw |peak| (G)", yscale="log",
           title="5-in 100-drop campaign (RW5F61, CH4 trigger @ 1000 G)")
    a1.legend(fontsize=8)
    a1.grid(alpha=0.3)
    a2.plot([r["signal"] for r in real], t_cross, "x-", ms=4, color="tab:brown",
            label="CH4 first crossing of 1000 G")
    a2.plot([r["signal"] for r in real], t_imps, "s", ms=3, color="tab:red",
            label="impact (TOP resultant argmax)")
    a2.axhline(4.0, color="k", ls=":", lw=1.2, label="nominal pre-trigger 4.000 ms")
    a2.set(ylabel="time into record (ms)", title="trigger timing")
    a2.legend(fontsize=8)
    a2.grid(alpha=0.3)
    a3.plot(s_all[1:], gaps, "k.-", ms=3)
    a3.set(xlabel="capture (Signal #)", ylabel="gap to previous (s)",
           title="release cadence")
    a3.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_full_series.png", dpi=130)
    plt.close(fig)

    # Fig 2: BOT saturation before/after the height change
    fig, ax = plt.subplots(figsize=(11, 5))
    for name, col in [("CH6", "tab:green"), ("CH7", "tab:orange"), ("CH8", "tab:red")]:
        fr = 100 * np.array([r["sat"][name]["frac_fs"] for r in rows])
        ax.plot(s_all, fr, "o-", ms=3, color=col,
                label=f"{name} raw |peak| (%FS, FS = {FULL_SCALE_G[name]:.0f} G)")
    ax.axhline(100, color="k", ls="-", lw=1.2, label="full scale")
    ax.axhline(95, color="k", ls=":", lw=1, label="95% FS")
    ax.axhline(100 * RUN13["ch8_median_fs"], color="tab:red", ls="--", lw=1.2,
               label="CH8 median at 13 in (105% FS)")
    ax.set(xlabel="capture (Signal #)", ylabel="raw |peak| (% of full scale)",
           title="bottom tri-axis headroom at 5 in — the reason for the height change")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "02_bot_headroom.png", dpi=130)
    plt.close(fig)

    # Fig 3: per-drop CFC-180 peaks + transmissibilities
    fig, (b1, b2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    b1.plot(drops, top, "s-", ms=3.5, color="tab:red", label="TOP CFC-180 (CH2-4 resultant)")
    b1.plot(drops, ch5v, "o-", ms=3.5, color="tab:blue", label="CH5 CFC-180 (base plate, taped)")
    b1.plot(drops, bot, "^-", ms=3.5, color="tab:green", label="BOT CFC-180 (CH6-8 resultant)")
    b1.set(ylabel="CFC-180 peak |g| (G)", title="per-drop CFC-180 peaks")
    b1.legend(fontsize=8)
    b1.grid(alpha=0.3)
    b2.plot(drops, tch5, "o-", ms=3.5, color="tab:blue", label="T = TOP/CH5 (plate input)")
    b2.plot(drops, tst, "d-", ms=3.5, color="tab:purple", label="T* = TOP/BOT (bottom vertex)")
    b2.set(xlabel="drop #", ylabel="transmissibility")
    b2.legend(fontsize=8)
    b2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_cfc180_series.png", dpi=130)
    plt.close(fig)

    # Fig 4: stabilized-phase OLS (TOP output + T + T*)
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5))
    for ax_, y, name, col in [(axes[0], top[stable], "TOP output CFC-180 (G)", "tab:red"),
                              (axes[1], tch5[stable], "T = TOP/CH5 (CFC-180)", "tab:blue"),
                              (axes[2], tst[stable], "T* = TOP/BOT (CFC-180)", "tab:purple")]:
        o = ols_full(xs, y)
        ax_.plot(xs, y, "o", ms=4, color=col)
        fit = o["mean"] - o["slope"] * xs.mean() + o["slope"] * xs
        ax_.plot(xs, fit, "-", color="k", lw=1.5,
                 label=f"OLS {o['slope']:+.4f}/drop ({o['slope_pct']:+.3f}%/drop)\n"
                       f"p = {o['p']:.1e}, R² = {o['r2']:.2f}")
        lo_fit = o["mean"] - o["ci_lo"] * xs.mean() + o["ci_lo"] * xs
        hi_fit = o["mean"] - o["ci_hi"] * xs.mean() + o["ci_hi"] * xs
        ax_.fill_between(xs, np.minimum(lo_fit, hi_fit), np.maximum(lo_fit, hi_fit),
                         color=col, alpha=0.15, label="95% CI on slope")
        ax_.set(xlabel="drop #", ylabel=name)
        ax_.legend(fontsize=8)
        ax_.grid(alpha=0.3)
    fig.suptitle(f"stabilized-phase drift (drops {burn_in_k + 1}-{last})")
    fig.tight_layout()
    fig.savefig(FIG / "04_stabilized_ols.png", dpi=130)
    plt.close(fig)

    # Fig 5: damage indicators
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))
    for ax_, key, label in [(axes[0], "top_width_ms", "output half-amplitude\npulse width (ms)"),
                            (axes[1], "dom_freq_hz",
                             "ringdown dominant freq (Hz)\n100–2000 Hz, rotation-invariant"),
                            (axes[2], "centroid_hz", "ringdown spectral centroid (Hz)")]:
        y = np.array([r[key] for r in real], float)
        o = dmg[key]
        ax_.plot(drops, y, "o-", ms=3, color="tab:red")
        ax_.set(xlabel="drop #",
                title=f"{label}\nslope {o['slope_pct']:+.3f}%/drop, p = {o['p']:.1e}")
        ax_.grid(alpha=0.3)
    fig.suptitle("mount-robust specimen damage indicators — 5-in 100-drop campaign")
    fig.tight_layout()
    fig.savefig(FIG / "05_damage_indicators.png", dpi=130)
    plt.close(fig)

    # Fig 6: per-axis migration (both seats)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharex=True)
    for key, name, col in [("ch2_pk_g", "CH2", "tab:green"),
                           ("ch3_pk_g", "CH3", "tab:orange"),
                           ("ch4_pk_g", "CH4", "tab:red")]:
        axes[0].plot(drops, [r[key] for r in real], "o-", ms=3, color=col,
                     label=f"{name} raw |peak|")
    axes[0].set(xlabel="drop #", ylabel="raw |peak| per axis (G)",
                title="top seat (CH2-4, taped housing entrance)")
    for key, name, col in [("ch6_pk_g", "CH6", "tab:green"),
                           ("ch7_pk_g", "CH7", "tab:orange"),
                           ("ch8_pk_g", "CH8", "tab:red")]:
        axes[1].plot(drops, [r[key] for r in real], "o-", ms=3, color=col,
                     label=f"{name} raw |peak|")
    axes[1].set(xlabel="drop #", title="bottom seat (CH6-8, low-range)")
    for ax_ in axes:
        ax_.legend(fontsize=8)
        ax_.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "06_axis_migration.png", dpi=130)
    plt.close(fig)

    # ---------------- machine-readable summary -----------------------
    summary = {
        "n_captures": N_CAPTURES,
        "spurious_captures": spurious,
        "n_real_drops_captured": len(real),
        "drop_height_in": 5.0,
        "trigger": {
            "channel": "CH4",
            "level_g": TRIGGER_LEVEL_G,
            "cross_ms": {"mean": float(t_cross.mean()), "std": float(t_cross.std()),
                         "min": float(t_cross.min()), "max": float(t_cross.max())},
            "impact_ms": {"mean": float(t_imps.mean()), "std": float(t_imps.std())},
            "ch4_raw_peak_g": {"mean": float(ch4_pks.mean()), "min": float(ch4_pks.min()),
                               "max": float(ch4_pks.max())},
            "margin_x": {"min": float((ch4_pks / TRIGGER_LEVEL_G).min()),
                         "max": float((ch4_pks / TRIGGER_LEVEL_G).max())},
            "pre_cross_max_g": float(pre_max.max()),
        },
        "cadence_s": {"median": float(np.median(gaps)), "min": float(gaps.min()),
                      "max": float(gaps.max())},
        "saturation": sat_summary,
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
    with open(FIG / "5in_100drops_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)

    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
