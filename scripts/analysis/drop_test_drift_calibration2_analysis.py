#!/usr/bin/env python3
"""Analyze the second drift-calibration run: **50 auto-drops** (PR #67).

Follow-up to ``drop_test_drift_calibration_analysis.py`` (30 auto-drops).
Same input-output pair @ctrhjk has been using — a single-axis accelerometer
wax-mounted on the bottom acrylic plate is the **input** (CH5, triggered), a
tri-axis accelerometer in the top-vertex **key-seat** (wax-retained) is the
**output** (CH2/CH3/CH4), bungees removed — and the same dummy specimen
(failed print ``prc1kn``). New this run: the output sensor's cable is tied to
the iron rod so cable pull can't drag the sensor out of the seat, and the
sensor **did not fall off** across all 50 drops.

Deliverables mirror the first drift-calibration request:
  1. burn-in / stabilization detection (changepoint scan + exponential fit);
  2. stabilized-phase OLS drift rate on input / output / T with 95% CI;
  3. regression reliability (Durbin-Watson, Shapiro-Wilk, start-drop sweep);
plus the **specimen damage / limitation check** @ctrhjk asked for, using the
mount-robust indicators from ``drop_test_prc1kn_health_check.py``:
  * output half-amplitude pulse width (a cracked / softened structure
    lengthens the pulse);
  * rotation-invariant ringdown spectrum of the tri-axis output (dominant
    frequency + spectral centroid of the *sum* of per-axis PSDs — the trace of
    the spectral matrix, invariant under any rigid rotation of the sensor in
    its seat, so seat wiggle cannot fake a structural frequency shift);
  * per-axis peak migration (sensor rotating / working loose — the early
    warning that preceded the drop-26 fall-off in run #1);
  * pre-impact noise floor per output axis (sensor health).

Channel map (identical to the input-output / key-seat / wax series):
  * CH5            — single-axis accelerometer wax-mounted on the **base plate**
    = INPUT; the triggered channel (1000 G trigger, 9442.9 G full scale).
  * CH2, CH3, CH4  — tri-axis accelerometer in the vertex **key-seat** (wax-
    retained, cable tied off) = OUTPUT (full scales 14492.8 / 14992.5 /
    13624.0 G); trigger OFF.

``Signal{1..50}`` = drops 1..50 (contiguous captures).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, optimize, signal, stats

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "drop-tests" / "drift-calibration2" / "raw"
FIG = REPO / "data" / "drop-tests" / "drift-calibration2" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

OUT_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output in the vertex key-seat
CH5 = 3  # single-axis input wax-mounted on the base plate (triggered channel)

IMPACT_SEARCH_S = 0.010  # look for the impact within the first 10 ms
IMPACT_HALF_WIN_S = 0.0015  # +-1.5 ms window around the impact for peak search
BASELINE_S = 0.0028  # pre-impact baseline window (impact lands ~3.9 ms)
TP4_HEADER_LINES = 9  # TP4 CSV export: 8 metadata rows + 1 column-name row

RING_BAND_HZ = (100.0, 2000.0)  # structural ringdown band
RING_START_AFTER_IMPACT_S = 0.002
RING_LEN_S = 0.080

SPECIMEN = "prc1kn"  # dummy specimen (failed print) — exercises the mount/DAQ
N_DROPS = 50
FALLOFF_FLOOR_G = 500.0  # attached >= ~5,600 G raw; detached <= ~30 G

# Headline numbers from drift-calibration run #1 (30 auto-drops, drops 6-24
# stabilized; see data/drop-tests/drift-calibration/figures/*.json) for the
# cross-run comparison printed at the end.
RUN1 = {
    "burn_in": 5,
    "in_mean": 215.2, "in_cv": 2.57,
    "out_mean": 261.4, "out_cv": 0.53, "out_slope_pct": +0.033, "out_p": 0.135,
    "t_mean": 1.215, "t_cv": 2.88,
    "pulse_ms": 1.51,
}


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (t, channels[N, 4]) = (time, [CH2, CH3, CH4, CH5])."""
    d = np.genfromtxt(path, skip_header=TP4_HEADER_LINES, delimiter=",", usecols=(0, 1, 2, 3, 4))
    return d[:, 0], d[:, 1:5]


def cfc_filter(x: np.ndarray, fs: float, cfc: int) -> np.ndarray:
    """SAE J211 phaseless Butterworth low-pass for a given CFC class."""
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


def impact_index(t: np.ndarray, trig: np.ndarray, dt: float) -> int:
    """Index of the trigger-channel (CH5 input) impact inside the first 10 ms."""
    nb = max(1, int(BASELINE_S / dt))
    base = np.median(trig[:nb])
    search = t < IMPACT_SEARCH_S
    rel = np.abs(trig - base)
    rel[~search] = -np.inf
    return int(np.argmax(rel))


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


def ringdown_spectrum(t: np.ndarray, out: np.ndarray, i_imp: int, fs: float) -> dict:
    """Rotation-invariant ringdown spectral indicators of the tri-axis output."""
    i0 = i_imp + int(RING_START_AFTER_IMPACT_S * fs)
    i1 = min(len(t), i0 + int(RING_LEN_S * fs))
    nper = min(4096, i1 - i0)
    psd_sum = None
    for c in OUT_COLS:
        seg = out[i0:i1, c] - np.mean(out[i0:i1, c])
        f, p = signal.welch(seg, fs=fs, nperseg=nper)
        psd_sum = p if psd_sum is None else psd_sum + p
    band = (f >= RING_BAND_HZ[0]) & (f <= RING_BAND_HZ[1])
    fb, pb = f[band], psd_sum[band]
    return {
        "dom_freq_hz": float(fb[np.argmax(pb)]),
        "centroid_hz": float(np.sum(fb * pb) / np.sum(pb)),
    }


def resultant(out: np.ndarray) -> np.ndarray:
    """Magnitude of the tri-axis (CH2, CH3, CH4) vector at each sample."""
    return np.sqrt(np.sum(out**2, axis=1))


def cv(vals) -> float:
    """Coefficient of variation (%) = 100 * std / mean."""
    a = np.asarray(vals, float)
    m = a.mean()
    return float(100.0 * a.std(ddof=1) / m) if m else float("nan")


def event_time(path: Path) -> str:
    """The TP4 'EventTime:' stamp from the file header."""
    with open(path) as fh:
        for line in fh:
            if line.startswith("EventTime:"):
                return line.split(":", 1)[1].strip()
    return ""


def analyze_drop(path: Path) -> tuple[dict, dict]:
    """Return (metrics row, traces) for one capture."""
    t, ch = load(path)
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    nb = max(1, int(BASELINE_S / dt))

    ch5 = ch[:, CH5] - np.median(ch[:nb, CH5])  # input (base plate)
    out = ch[:, OUT_COLS] - np.median(ch[:nb, OUT_COLS], axis=0)
    i_imp = impact_index(t, ch5, dt)

    in_raw = windowed_peak(t, ch5, i_imp, dt)["peak_abs_g"]
    ch5_180 = cfc_filter(ch5, fs, 180)
    m_in_1000 = windowed_peak(t, cfc_filter(ch5, fs, 1000), i_imp, dt)
    m_in_180 = windowed_peak(t, ch5_180, i_imp, dt)

    res_raw = resultant(out)
    out180 = np.stack([cfc_filter(out[:, j], fs, 180) for j in range(out.shape[1])], axis=1)
    res_180 = resultant(out180)
    res_1000 = resultant(
        np.stack([cfc_filter(out[:, j], fs, 1000) for j in range(out.shape[1])], axis=1)
    )
    out_raw_peak = windowed_peak(t, res_raw, i_imp, dt)["peak_abs_g"]
    m_out_1000 = windowed_peak(t, res_1000, i_imp, dt)
    m_out_180 = windowed_peak(t, res_180, i_imp, dt)

    in180 = m_in_180["peak_abs_g"]
    out180_pk = m_out_180["peak_abs_g"]

    half = max(1, int(IMPACT_HALF_WIN_S / dt))
    lo, hi = max(0, i_imp - half), min(len(t), i_imp + half)
    axis_pk = [float(np.max(np.abs(out[lo:hi, j]))) for j in range(3)]
    ring = ringdown_spectrum(t, out, i_imp, fs)
    noise = [float(np.std(out[:nb, j])) for j in range(3)]

    row = {
        "drop": None,  # filled by caller
        "event_time": event_time(path),
        "t_imp_ms": t[i_imp] * 1e3,
        "in_raw_g": in_raw,
        "in_1000_g": m_in_1000["peak_abs_g"],
        "in_180_g": in180,
        "out_raw_g": out_raw_peak,
        "out_1000_g": m_out_1000["peak_abs_g"],
        "out_180_g": out180_pk,
        "transmiss": out180_pk / in180 if in180 else float("nan"),
        "in_width_ms": m_in_180["pulse_width_ms"],
        "out_width_ms": m_out_180["pulse_width_ms"],
        "in_dv_ms": m_in_180["delta_v_ms"],
        "ch2_pk_g": axis_pk[0],
        "ch3_pk_g": axis_pk[1],
        "ch4_pk_g": axis_pk[2],
        "dom_freq_hz": ring["dom_freq_hz"],
        "centroid_hz": ring["centroid_hz"],
        "noise_rms_g": noise,
        "attached": bool(out_raw_peak >= FALLOFF_FLOOR_G),
    }
    traces = (t, ch5_180, res_raw, res_180, i_imp, fs)
    return row, traces


def ols_full(x, y) -> dict:
    """OLS with slope CI, R^2, Durbin-Watson and Shapiro residual normality."""
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
    all_traces: dict = {}
    for drop in range(1, N_DROPS + 1):
        row, traces = analyze_drop(RAW / f"drift_calibration2_Signal{drop}.csv")
        row["drop"] = drop
        rows.append(row)
        all_traces[drop] = traces

    # ---------------- attachment check ------------------------------
    detached = [r["drop"] for r in rows if not r["attached"]]
    print(f"\nattachment: {N_DROPS - len(detached)}/{N_DROPS} drops with the output "
          f"sensor attached" + (f"; detached drops: {detached}" if detached else
                                " — cable tie-off worked, no fall-off"))
    valid = [r for r in rows if r["attached"]]
    vdrops = np.array([r["drop"] for r in valid], float)
    vout = np.array([r["out_180_g"] for r in valid], float)
    vin = np.array([r["in_180_g"] for r in valid], float)
    vt = np.array([r["transmiss"] for r in valid], float)
    last_valid = int(vdrops[-1])

    # ---------------- per-drop table ---------------------------------
    hdr = (
        f"{'drop':>4s} {'t_imp':>6s} {'IN raw':>7s} {'IN 1k':>6s} {'IN 180':>7s} "
        f"{'OUT raw':>8s} {'OUT 1k':>7s} {'OUT 180':>8s} {'T(180)':>7s} "
        f"{'CH2pk':>6s} {'CH3pk':>6s} {'CH4pk':>6s} {'wid':>5s} {'Δv':>5s} "
        f"{'fdom':>5s} {'fcent':>5s}"
    )
    print(f"\n=== drift calibration #2, 50 auto-drops ({SPECIMEN}) ===\n")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(
            f"{r['drop']:4d} {r['t_imp_ms']:6.2f} {r['in_raw_g']:7.0f} {r['in_1000_g']:6.0f} "
            f"{r['in_180_g']:7.0f} {r['out_raw_g']:8.0f} {r['out_1000_g']:7.0f} "
            f"{r['out_180_g']:8.0f} {r['transmiss']:7.2f} {r['ch2_pk_g']:6.0f} "
            f"{r['ch3_pk_g']:6.0f} {r['ch4_pk_g']:6.0f} {r['out_width_ms']:5.2f} "
            f"{r['in_dv_ms']:5.2f} {r['dom_freq_hz']:5.0f} {r['centroid_hz']:5.0f}"
        )

    # ---------------- burn-in changepoint scan -----------------------
    print(f"\n=== burn-in changepoint scan (output CFC-180, OLS on drops k+1..{last_valid}) ===\n")
    print(f"{'burn-in k':>9s} {'n':>3s} {'slope G/drop':>13s} {'%/drop':>8s} {'p':>7s}")
    scan = {}
    burn_in_k = None
    for k in range(0, 13):
        m = vdrops > k
        if m.sum() < 5:
            break
        o = ols_full(vdrops[m], vout[m])
        scan[k] = o
        print(f"{k:9d} {o['n']:3d} {o['slope']:+13.3f} {o['slope_pct']:+8.3f} {o['p']:7.3f}")
        if burn_in_k is None and o["p"] > 0.05:
            burn_in_k = k
    if burn_in_k is None:
        burn_in_k = 5  # fall back to the SOP count from run #1
        print("\n-> no k in 0..12 yields an n.s. trend; falling back to the "
              f"SOP burn-in = {burn_in_k} (see start-drop sensitivity below)")
    else:
        print(f"\n-> smallest k with n.s. seating trend: burn-in = {burn_in_k} drops")

    # exponential-approach fit: out(drop) = a - b * exp(-drop / tau)
    def expo(d, a, b, tau):
        return a - b * np.exp(-d / tau)

    p0 = (vout[-5:].mean(), vout[-5:].mean() - vout[0], 2.0)
    try:
        popt, _ = optimize.curve_fit(expo, vdrops, vout, p0=p0, maxfev=20000)
        a_fit, b_fit, tau = (float(v) for v in popt)
        print(f"exponential-approach fit: plateau a = {a_fit:.1f} G, amplitude b = {b_fit:.1f} G, "
              f"tau = {tau:.1f} drops  (95% seated after ~3*tau = {3 * tau:.0f} drops)")
    except RuntimeError:
        a_fit = b_fit = tau = float("nan")
        print("exponential-approach fit did not converge (no seating transient?)")

    # ---------------- stabilized-phase drift (the deliverable) -------
    stable = vdrops > burn_in_k
    print(f"\n=== stabilized-phase OLS (drops {burn_in_k + 1}..{last_valid}, "
          f"n = {int(stable.sum())}) ===\n")
    results = {}
    for name, y in [("input", vin[stable]), ("output", vout[stable]), ("T", vt[stable])]:
        o = ols_full(vdrops[stable], y)
        results[name] = o
        print(f"  {name:7s}: mean {o['mean']:8.3f}  CV {o['cv']:5.2f}%   "
              f"slope {o['slope']:+9.4f}/drop ({o['slope_pct']:+.3f}%/drop)   "
              f"95% CI [{o['ci_lo']:+.4f}, {o['ci_hi']:+.4f}]   "
              f"p = {o['p']:.3f}  R² = {o['r2']:.3f}  DW = {o['dw']:.2f}  "
              f"Shapiro p = {o['shapiro_p']:.2f}")

    # sensitivity of the drift estimate to the start drop
    print("\n  start-drop sensitivity (output %/drop):")
    sens = {}
    for k in range(max(1, burn_in_k - 3), burn_in_k + 7):
        m = vdrops > k
        if m.sum() < 5:
            break
        o = ols_full(vdrops[m], vout[m])
        sens[k] = o
        print(f"    start {k + 1:2d}: {o['slope_pct']:+.3f}%/drop  (p = {o['p']:.3f})")

    # first-half vs second-half of the stabilized phase (50-drop bonus:
    # enough n to see a late-campaign trend the 30-drop run couldn't)
    xs = vdrops[stable]
    mid = xs[len(xs) // 2]
    o_h1 = ols_full(xs[xs <= mid], vout[stable][xs <= mid])
    o_h2 = ols_full(xs[xs > mid], vout[stable][xs > mid])
    print(f"\n  split-half check (output): drops {int(xs[0])}-{int(mid)}: "
          f"{o_h1['slope_pct']:+.3f}%/drop (p = {o_h1['p']:.2f}); "
          f"drops {int(mid) + 1}-{last_valid}: {o_h2['slope_pct']:+.3f}%/drop "
          f"(p = {o_h2['p']:.2f})")

    # ---------------- per-axis migration (seat health) ---------------
    print("\n=== per-axis peak migration (raw |peak|) ===\n")
    axis_ols = {}
    for name, key in [("CH2", "ch2_pk_g"), ("CH3", "ch3_pk_g"), ("CH4", "ch4_pk_g")]:
        y = np.array([r[key] for r in valid], float)
        o = ols_full(vdrops, y)
        axis_ols[name] = o
        print(f"  {name}: {y[0]:6.0f} G (drop 1) -> {y[-1]:6.0f} G (drop {last_valid})   "
              f"slope {o['slope']:+7.1f} G/drop ({o['slope_pct']:+.2f}%/drop)  p = {o['p']:.1e}")

    # ---------------- specimen damage / limitation check -------------
    print("\n=== specimen damage indicators (mount-robust) ===\n")
    dmg = {}
    for key, label in [("out_width_ms", "output pulse width (ms)"),
                       ("dom_freq_hz", "ringdown dominant freq (Hz)"),
                       ("centroid_hz", "ringdown spectral centroid (Hz)"),
                       ("in_dv_ms", "input Δv (m/s)")]:
        y = np.array([r[key] for r in valid], float)
        o = ols_full(vdrops, y)
        dmg[key] = o
        print(f"  {label:34s}: mean {o['mean']:8.2f}  CV {o['cv']:5.2f}%  "
              f"slope {o['slope_pct']:+.3f}%/drop  p = {o['p']:.3f}")
    noise = np.array([r["noise_rms_g"] for r in rows], float)
    print(f"  pre-impact noise RMS (CH2/CH3/CH4): first 5 drops "
          f"{noise[:5].mean(axis=0).round(2).tolist()} G -> last 5 drops "
          f"{noise[-5:].mean(axis=0).round(2).tolist()} G")

    # cross-run comparison vs drift-calibration #1
    print("\n=== vs drift-calibration #1 (30 drops, stabilized 6-24) ===\n")
    print(f"  input : {RUN1['in_mean']:.1f} G (CV {RUN1['in_cv']:.2f}%) -> "
          f"{results['input']['mean']:.1f} G (CV {results['input']['cv']:.2f}%)")
    print(f"  output: {RUN1['out_mean']:.1f} G (CV {RUN1['out_cv']:.2f}%) -> "
          f"{results['output']['mean']:.1f} G (CV {results['output']['cv']:.2f}%)")
    print(f"  T     : {RUN1['t_mean']:.3f} (CV {RUN1['t_cv']:.2f}%) -> "
          f"{results['T']['mean']:.3f} (CV {results['T']['cv']:.2f}%)")

    # ---------------- figures ---------------------------------------
    drops_all = np.array([r["drop"] for r in rows], float)
    out_all = np.array([r["out_180_g"] for r in rows], float)
    in_all = np.array([r["in_180_g"] for r in rows], float)

    # Fig 1: full-series input/output peaks with burn-in shading
    fig, ax = plt.subplots(figsize=(11, 5.5))
    if burn_in_k:
        ax.axvspan(0.5, burn_in_k + 0.5, color="0.85", label=f"burn-in (drops 1-{burn_in_k})")
    ax.plot(drops_all, in_all, "o-", color="tab:blue", ms=4, label="input CH5 (base, wax)")
    ax.plot(drops_all, out_all, "s-", color="tab:red", ms=4,
            label="output |tri-axis| (key-seat + wax, cable tied)")
    ax.set(xlabel="drop #", ylabel="CFC-180 peak |g| (G)",
           title=f"{SPECIMEN}: 50-auto-drop drift calibration #2 — input / output per drop "
                 "(no fall-off)")
    ax.legend(fontsize=8, loc="center left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_full_series.png", dpi=130)
    plt.close(fig)

    # Fig 2: stabilized-phase OLS with 95% CI band (output + T)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))
    for ax_, y, name, col in [(a1, vout[stable], "output CFC-180 (G)", "tab:red"),
                              (a2, vt[stable], "T = OUT/IN (CFC-180)", "tab:purple")]:
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
        ax_.set(xlabel="drop #", ylabel=name)
        ax_.legend(fontsize=8)
        ax_.grid(alpha=0.3)
    fig.suptitle(f"{SPECIMEN}: stabilized-phase drift (drops {burn_in_k + 1}-{last_valid})")
    fig.tight_layout()
    fig.savefig(FIG / "02_stabilized_ols.png", dpi=130)
    plt.close(fig)

    # Fig 3: per-axis migration — is the sensor working loose in the seat?
    fig, ax = plt.subplots(figsize=(11, 5.5))
    for key, name, col in [("ch2_pk_g", "CH2", "tab:green"),
                           ("ch3_pk_g", "CH3", "tab:orange"),
                           ("ch4_pk_g", "CH4", "tab:red")]:
        ax.plot(vdrops, [r[key] for r in valid], "o-", ms=4, color=col, label=f"{name} raw |peak|")
    ax.plot(vdrops, [r["out_raw_g"] for r in valid], "k--", lw=1, label="|resultant| raw peak")
    ax.set(xlabel="drop #", ylabel="raw |peak| per axis (G)",
           title=f"{SPECIMEN}: per-axis impact peak across 50 drops (cable tied to rod)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_axis_migration.png", dpi=130)
    plt.close(fig)

    # Fig 4: specimen damage indicators per drop
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))
    for ax_, key, label in [(axes[0], "out_width_ms", "output half-amplitude\npulse width (ms)"),
                            (axes[1], "dom_freq_hz",
                             "ringdown dominant freq (Hz)\n100–2000 Hz, rotation-invariant"),
                            (axes[2], "centroid_hz", "ringdown spectral centroid (Hz)")]:
        y = np.array([r[key] for r in valid], float)
        o = dmg[key]
        ax_.plot(vdrops, y, "o-", ms=4, color="tab:red")
        ax_.set(xlabel="drop #", title=f"{label}\nslope {o['slope_pct']:+.3f}%/drop, p = {o['p']:.2f}")
        ax_.grid(alpha=0.3)
    fig.suptitle(f"{SPECIMEN}: mount-robust specimen damage indicators — 50-drop campaign")
    fig.tight_layout()
    fig.savefig(FIG / "04_damage_indicators.png", dpi=130)
    plt.close(fig)

    # ---------------- machine-readable summary -----------------------
    summary = {
        "n_drops": N_DROPS,
        "detached_drops": detached,
        "burn_in_drops": burn_in_k,
        "expo_fit": {"plateau_g": a_fit, "amplitude_g": b_fit, "tau_drops": tau},
        "stabilized_window": [int(burn_in_k) + 1, last_valid],
        "stabilized_ols": results,
        "split_half": {"first": o_h1, "second": o_h2},
        "burn_in_scan": {str(k): v for k, v in scan.items()},
        "start_drop_sensitivity": {str(k): v for k, v in sens.items()},
        "axis_migration": axis_ols,
        "damage_indicators": dmg,
        "per_drop": [{k: v for k, v in r.items()} for r in rows],
    }
    with open(FIG / "drift_calibration2_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)

    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
