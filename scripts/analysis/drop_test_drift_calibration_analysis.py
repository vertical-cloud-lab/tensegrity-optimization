#!/usr/bin/env python3
"""Analyze the 30-auto-drop **drift-calibration** run (PR #67).

Follow-up to ``drop_test_burn_in_wax_analysis.py``. Same input-output pair
@ctrhjk has been using — a single-axis accelerometer wax-mounted on the bottom
acrylic plate is the **input** (CH5, triggered), a tri-axis accelerometer in the
top-vertex **key-seat** (wax-retained) is the **output** (CH2/CH3/CH4), bungees
removed — and the same dummy specimen (failed print ``prc1kn``), used to
exercise the mount/DAQ, not to compare geometry.

This run is the **drift-calibration** experiment: 30 drops conducted
*automatically* at 13 in (~15 s cadence, from the per-file TP4 ``EventTime``
stamps), designed to (1) define the burn-in drop count from where the initial
seating transient flattens, (2) measure the system's inherent post-burn-in
drift rate by OLS, and (3) qualify the reliability of that regression. During
the run the tri-axis output sensor **fell off the key-seat housing** at an
unknown drop (~26th per @ctrhjk); this script detects the fall-off from the
data.

Channel map (identical to the input-output / key-seat / wax series):
  * CH5            — single-axis accelerometer wax-mounted on the **base plate**
    = INPUT; the triggered channel (1000 G trigger, 9442.9 G full scale).
  * CH2, CH3, CH4  — tri-axis accelerometer in the vertex **key-seat** (wax-
    retained) = OUTPUT (full scales 14492.8 / 14992.5 / 13624.0 G); trigger OFF.

``Signal{1..30}`` = drops 1..30 (contiguous captures).

Pipeline per drop mirrors the burn-in script: locate the impact on the
triggered CH5 within the first 10 ms (windowed, not a global 0.2 s max),
baseline-correct, report raw / SAE J211 CFC-1000 / CFC-180 peaks for input
(CH5) and the tri-axis output resultant, transmissibility T = output / input,
pulse width and Delta-v. On top of that this script adds:

  * **fall-off detection** — the output resultant collapses to noise once the
    sensor detaches; flag every drop whose raw output peak is below a floor
    that sits orders of magnitude under any attached-sensor impact;
  * **per-axis peak tracking** (CH2/CH3/CH4) — a slow redistribution of the
    impact between axes at near-constant resultant is the signature of the
    sensor *rotating / working loose* in the seat, an early warning the
    resultant alone cannot see;
  * **burn-in changepoint scan** — for each candidate burn-in count k, OLS the
    output over drops k+1..last-stable and find the smallest k where the
    seating trend is gone (slope n.s.), plus an exponential-approach fit
    y = a - b*exp(-drop/tau) whose time constant gives an independent estimate;
  * **stabilized-phase OLS** — slope, %/drop, p, R^2, 95% CI on input, output
    and T, with reliability checks: Durbin-Watson autocorrelation, Shapiro-Wilk
    residual normality, and a start-drop sensitivity sweep.
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
RAW = REPO / "data" / "drop-tests" / "drift-calibration" / "raw"
FIG = REPO / "data" / "drop-tests" / "drift-calibration" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

OUT_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output in the vertex key-seat
CH5 = 3  # single-axis input wax-mounted on the base plate (triggered channel)

IMPACT_SEARCH_S = 0.010  # look for the impact within the first 10 ms
IMPACT_HALF_WIN_S = 0.0015  # +-1.5 ms window around the impact for peak search
BASELINE_S = 0.0028  # pre-impact baseline window (impact lands ~3.9 ms)
TP4_HEADER_LINES = 9  # TP4 CSV export: 8 metadata rows + 1 column-name row

SPECIMEN = "prc1kn"  # dummy specimen (failed print) — exercises the mount/DAQ
N_DROPS = 30
# An attached sensor never peaked below ~5,600 G raw in this series; a detached
# one never above ~30 G. Any raw output peak below this floor = fallen off.
FALLOFF_FLOOR_G = 500.0


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
        "in_dv_ms": m_in_180["delta_v_ms"],
        "ch2_pk_g": axis_pk[0],
        "ch3_pk_g": axis_pk[1],
        "ch4_pk_g": axis_pk[2],
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
        row, traces = analyze_drop(RAW / f"drift_calibration_Signal{drop}.csv")
        row["drop"] = drop
        rows.append(row)
        all_traces[drop] = traces

    # ---------------- fall-off detection ----------------------------
    detached = [r["drop"] for r in rows if not r["attached"]]
    falloff_drop = min(detached) if detached else None
    attached_rows = [r for r in rows if r["attached"]]
    last_attached = max(r["drop"] for r in attached_rows)
    print(f"\nfall-off: output detached from drop {falloff_drop} onward "
          f"(detached drops: {detached}); last attached drop = {last_attached}")

    # Drop 25 pre-fall-off anomaly: resultant / axis spike right before detach
    stable_ref = [r["out_180_g"] for r in attached_rows if r["drop"] <= last_attached - 1]
    ref_mean, ref_sd = np.mean(stable_ref), np.std(stable_ref, ddof=1)
    last_row = next(r for r in rows if r["drop"] == last_attached)
    z_last = (last_row["out_180_g"] - ref_mean) / ref_sd
    anomalous_last = abs(z_last) > 4.0
    print(f"last attached drop {last_attached}: OUT180 = {last_row['out_180_g']:.0f} G "
          f"(z = {z_last:+.1f} vs drops <= {last_attached - 1}) "
          f"{'-> PRE-FALL-OFF ANOMALY, excluded from drift fits' if anomalous_last else ''}")

    valid = [r for r in attached_rows if not (anomalous_last and r["drop"] == last_attached)]
    vdrops = np.array([r["drop"] for r in valid], float)
    vout = np.array([r["out_180_g"] for r in valid], float)
    vin = np.array([r["in_180_g"] for r in valid], float)
    vt = np.array([r["transmiss"] for r in valid], float)
    last_valid = int(vdrops[-1])

    # ---------------- per-drop table ---------------------------------
    hdr = (
        f"{'drop':>4s} {'t_imp':>6s} {'IN raw':>7s} {'IN 1k':>6s} {'IN 180':>7s} "
        f"{'OUT raw':>8s} {'OUT 1k':>7s} {'OUT 180':>8s} {'T(180)':>7s} "
        f"{'CH2pk':>6s} {'CH3pk':>6s} {'CH4pk':>6s} {'wid':>5s} {'Δv':>5s} {'state':>9s}"
    )
    print(f"\n=== drift calibration, 30 auto-drops ({SPECIMEN}) ===\n")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        state = "attached" if r["attached"] else "FELL OFF"
        if anomalous_last and r["drop"] == last_attached:
            state = "anomaly"
        print(
            f"{r['drop']:4d} {r['t_imp_ms']:6.2f} {r['in_raw_g']:7.0f} {r['in_1000_g']:6.0f} "
            f"{r['in_180_g']:7.0f} {r['out_raw_g']:8.0f} {r['out_1000_g']:7.0f} "
            f"{r['out_180_g']:8.0f} {r['transmiss']:7.2f} {r['ch2_pk_g']:6.0f} "
            f"{r['ch3_pk_g']:6.0f} {r['ch4_pk_g']:6.0f} {r['in_width_ms']:5.2f} "
            f"{r['in_dv_ms']:5.2f} {state:>9s}"
        )

    # ---------------- burn-in changepoint scan -----------------------
    print("\n=== burn-in changepoint scan (output CFC-180, OLS on drops k+1..%d) ===\n"
          % last_valid)
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
    print(f"\n-> smallest k with n.s. seating trend: burn-in = {burn_in_k} drops")

    # exponential-approach fit: out(drop) = a - b * exp(-drop / tau)
    def expo(d, a, b, tau):
        return a - b * np.exp(-d / tau)

    p0 = (vout[-5:].mean(), vout[-5:].mean() - vout[0], 2.0)
    popt, _ = optimize.curve_fit(expo, vdrops, vout, p0=p0, maxfev=20000)
    a_fit, b_fit, tau = popt
    print(f"exponential-approach fit: plateau a = {a_fit:.1f} G, amplitude b = {b_fit:.1f} G, "
          f"tau = {tau:.1f} drops  (95% seated after ~3*tau = {3 * tau:.0f} drops)")

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
    for k in range(max(1, burn_in_k - 3), burn_in_k + 5):
        m = vdrops > k
        if m.sum() < 5:
            break
        o = ols_full(vdrops[m], vout[m])
        sens[k] = o
        print(f"    start {k + 1:2d}: {o['slope_pct']:+.3f}%/drop  (p = {o['p']:.3f})")

    # per-axis migration rates over the attached window
    print("\n=== per-axis peak migration (attached drops, raw |peak|) ===\n")
    for name, key in [("CH2", "ch2_pk_g"), ("CH3", "ch3_pk_g"), ("CH4", "ch4_pk_g")]:
        y = np.array([r[key] for r in valid], float)
        o = ols_full(vdrops, y)
        print(f"  {name}: {y[0]:6.0f} G (drop 1) -> {y[-1]:6.0f} G (drop {last_valid})   "
              f"slope {o['slope']:+7.1f} G/drop ({o['slope_pct']:+.2f}%/drop)  p = {o['p']:.1e}")

    # ---------------- figures ---------------------------------------
    drops_all = np.array([r["drop"] for r in rows], float)
    out_all = np.array([r["out_180_g"] for r in rows], float)
    in_all = np.array([r["in_180_g"] for r in rows], float)

    # Fig 1: full-series input/output peaks with burn-in + fall-off shading
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.axvspan(0.5, burn_in_k + 0.5, color="0.85", label=f"burn-in (drops 1-{burn_in_k})")
    ax.axvspan(falloff_drop - 0.5, N_DROPS + 0.5, color="mistyrose",
               label=f"sensor fell off (drops {falloff_drop}-{N_DROPS})")
    ax.plot(drops_all, in_all, "o-", color="tab:blue", ms=4, label="input CH5 (base, wax)")
    ax.plot(drops_all, out_all, "s-", color="tab:red", ms=4,
            label="output |tri-axis| (key-seat + wax)")
    if anomalous_last:
        ax.plot(last_attached, last_row["out_180_g"], "s", ms=11, mfc="none", mec="k",
                mew=1.5, label=f"drop {last_attached}: pre-fall-off anomaly")
    ax.set(xlabel="drop #", ylabel="CFC-180 peak |g| (G)",
           title=f"{SPECIMEN}: 30-auto-drop drift calibration — input / output per drop")
    ax.legend(fontsize=8, loc="center left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_full_series.png", dpi=130)
    plt.close(fig)

    # Fig 2: stabilized-phase OLS with 95% CI band (output + T)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))
    xs = vdrops[stable]
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
    fig.suptitle(f"{SPECIMEN}: stabilized-phase drift "
                 f"(drops {burn_in_k + 1}-{last_valid}, anomalous drop {last_attached} excluded)")
    fig.tight_layout()
    fig.savefig(FIG / "02_stabilized_ols.png", dpi=130)
    plt.close(fig)

    # Fig 3: per-axis migration — the sensor working loose in the seat
    fig, ax = plt.subplots(figsize=(11, 5.5))
    for key, name, col in [("ch2_pk_g", "CH2", "tab:green"),
                           ("ch3_pk_g", "CH3", "tab:orange"),
                           ("ch4_pk_g", "CH4", "tab:red")]:
        ax.plot(vdrops, [r[key] for r in valid], "o-", ms=4, color=col, label=f"{name} raw |peak|")
    ax.plot([r["drop"] for r in valid], [r["out_raw_g"] for r in valid], "k--", lw=1,
            label="|resultant| raw peak (near-constant)")
    ax.axvline(falloff_drop - 0.5, color="r", ls=":", lw=1.5,
               label=f"fall-off (drop {falloff_drop})")
    ax.set(xlabel="drop #", ylabel="raw |peak| per axis (G)",
           title=f"{SPECIMEN}: per-axis impact peak — sensor rotating in the seat "
                 "before falling off")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_axis_migration.png", dpi=130)
    plt.close(fig)

    # Fig 4: traces around the fall-off (last valid, anomaly, first detached)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    for ax_, drop, label in [
        (axes[0], last_attached - 1, f"drop {last_attached - 1} (attached)"),
        (axes[1], last_attached, f"drop {last_attached} (anomaly — letting go)"),
        (axes[2], falloff_drop, f"drop {falloff_drop} (fell off)"),
    ]:
        t, ch5_180, _res_raw, res_180, i_imp, _fs = all_traces[drop]
        t0 = t[i_imp] * 1e3
        w = (t * 1e3 > t0 - 3) & (t * 1e3 < t0 + 8)
        ax_.plot(t[w] * 1e3, ch5_180[w], color="tab:blue", lw=1, label="input CH5")
        ax_.plot(t[w] * 1e3, res_180[w], color="tab:red", lw=1, label="output |tri-axis|")
        ax_.set(xlabel="time (ms)", title=label)
        ax_.grid(alpha=0.3)
    axes[0].set_ylabel("CFC-180 a (G)")
    axes[0].legend(fontsize=8)
    fig.suptitle(f"{SPECIMEN}: output collapse at the fall-off")
    fig.tight_layout()
    fig.savefig(FIG / "04_falloff_traces.png", dpi=130)
    plt.close(fig)

    # ---------------- machine-readable summary -----------------------
    summary = {
        "falloff_drop": falloff_drop,
        "last_attached_drop": last_attached,
        "anomalous_last_attached": bool(anomalous_last),
        "z_last_attached": float(z_last),
        "burn_in_drops": burn_in_k,
        "expo_fit": {"plateau_g": float(a_fit), "amplitude_g": float(b_fit),
                     "tau_drops": float(tau)},
        "stabilized_window": [int(burn_in_k) + 1, last_valid],
        "stabilized_ols": results,
        "burn_in_scan": {str(k): v for k, v in scan.items()},
        "start_drop_sensitivity": {str(k): v for k, v in sens.items()},
        "per_drop": [{k: v for k, v in r.items()} for r in rows],
    }
    with open(FIG / "drift_calibration_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)

    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
