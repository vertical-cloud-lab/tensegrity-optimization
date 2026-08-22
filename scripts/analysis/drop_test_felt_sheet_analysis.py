#!/usr/bin/env python3
"""Felt-sheet cushioning / accelerometer-saturation sweep (CH5 trigger @ 300 G).

@ctrhjk ran a dedicated saturation-characterisation sweep on the same
downscaled #35 specimen used in the two 500-drop campaigns
(PR #82 comment 5007713855). The rig was unchanged from the second 500-drop
run — the bottom tri-axis (CH6-8) was removed, leaving **CH2-CH4** on the
top-vertex key-seat (tri-axis "TOP" output) and the single-axis **CH5** taped
to the base plate as the trigger channel (level lowered to **300 G**).

The one thing under test is the *impact severity*: the drop height was stepped
20 -> 30 -> 40 -> 50 -> 60 in and, at each level, felt sheets were stacked
beneath the drop block to cushion the hit. Nine (height, n_felt) conditions
were run, five drops each (Signal1-45):

    20 in / 1 felt   20 in / 2 felt
    30 in / 2 felt   30 in / 3 felt
    40 in / 3 felt   40 in / 4 felt
    50 in / 4 felt   50 in / 5 felt
    60 in / 5 felt

Questions this script answers:

  1. **Did the accelerometers saturate?** Raw |peak| vs each channel's full
     scale, per condition, with over-FS and flat-top (clipped-sample) counts.
     The single-axis CH5 (FS 9442.9 G) is the suspected bottleneck.
  2. **How do height and cushioning trade off?** A multiple OLS regression of
     log10(peak) on drop height and felt-sheet count separates the two
     effects (they are confounded in the as-run diagonal design): height adds
     energy, each felt sheet attenuates by a roughly constant factor.
  3. **What height + felt count is the sweet spot** for the BO campaign — a
     strong, repeatable signal that keeps the CH5 bottleneck below full scale
     with enough head-room that stiffer/larger designs in the search space
     won't clip.

Emits ``figures/felt_sheet_metrics.json`` consumed by
``docs/drop-test-felt-sheet-analysis.md``.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, signal, stats

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "drop-tests" / "felt-sheet" / "raw"
FIG = REPO / "data" / "drop-tests" / "felt-sheet" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

# This run kept only CH2-CH5 (bottom tri-axis CH6-8 removed, as in 500drops-nobot).
TOP_COLS = (0, 1, 2)  # CH2, CH3, CH4 — tri-axis output, top-vertex key-seat
CH5 = 3  # single-axis on the base plate — the trigger channel

FULL_SCALE_G = {"CH2": 14492.8, "CH3": 14992.5, "CH4": 13624.0, "CH5": 9442.9}

TRIGGER_LEVEL_G = 300.0  # lowered to 300 G for this specimen (per PR #82)
IMPACT_HALF_WIN_S = 0.0015
BASELINE_S = 0.0028
TP4_HEADER_LINES = 9

RING_BAND_HZ = (100.0, 2000.0)
RING_START_AFTER_IMPACT_S = 0.002
RING_LEN_S = 0.080

# (height_in, n_felt) -> Signal indices (chronological, five drops each).
CONDITIONS = [
    (20, 1, range(1, 6)),
    (20, 2, range(6, 11)),
    (30, 2, range(11, 16)),
    (30, 3, range(16, 21)),
    (40, 3, range(21, 26)),
    (40, 4, range(26, 31)),
    (50, 4, range(31, 36)),
    (50, 5, range(36, 41)),
    (60, 5, range(41, 46)),
]

REAL_IMPACT_FLOOR_G = 200.0  # CH5 raw floor for a captured impact (>> 300 G on hits)


def load(path: Path) -> tuple[np.ndarray, np.ndarray]:
    d = np.genfromtxt(path, skip_header=TP4_HEADER_LINES, delimiter=",",
                      usecols=(0, 1, 2, 3, 4))
    return d[:, 0], d[:, 1:5]


def cfc_filter(x: np.ndarray, fs: float, cfc: int) -> np.ndarray:
    cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
    b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
    return signal.filtfilt(b, a, x)


def windowed_peak(t: np.ndarray, a_g: np.ndarray, i_imp: int, dt: float) -> dict:
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
    return {"peak_abs_g": peak_abs, "t_peak_ms": t[idx] * 1e3,
            "pulse_width_ms": width * 1e3, "delta_v_ms": abs(dv)}


def ringdown_dom_freq(t: np.ndarray, tri: np.ndarray, i_imp: int, fs: float) -> float:
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
    return float(fb[np.argmax(pb)])


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

    # Locate the impact on the triggered channel (CH5), like the input-output
    # and vertex-acrylic scripts — not a global argmax on the output.
    i_imp = int(np.argmax(np.abs(ch5)))
    ch5_raw_pk = float(np.abs(ch5[i_imp]))
    is_real = ch5_raw_pk >= REAL_IMPACT_FLOOR_G

    over = np.abs(ch5) >= TRIGGER_LEVEL_G
    i_x = int(np.argmax(over)) if over.any() else -1
    t_x_ms = float(t[i_x] * 1e3) if i_x >= 0 else float("nan")

    # Saturation audit: raw |peak| vs full scale, plus a flat-top count that
    # catches analog clipping (many consecutive samples pinned near the peak).
    sat = {}
    for name, col in [("CH2", 0), ("CH3", 1), ("CH4", 2), ("CH5", 3)]:
        x = np.abs(ch[:, col] - np.median(ch[:nb, col]))
        pk = float(x.max())
        near = x >= 0.98 * FULL_SCALE_G[name]
        # longest run of samples pinned at/above 98% of full scale
        run = best = 0
        for v in near:
            run = run + 1 if v else 0
            best = max(best, run)
        sat[name] = {
            "peak_g": pk,
            "frac_fs": pk / FULL_SCALE_G[name],
            "over_fs": bool(pk >= FULL_SCALE_G[name]),
            "clip_run_samples": int(best),
        }

    row = {
        "signal": None,
        "event_time": event_time(path).isoformat(),
        "real_impact": bool(is_real),
        "t_imp_ms": float(t[i_imp] * 1e3),
        "trig_cross_ms": t_x_ms,
        "ch5_raw_g": ch5_raw_pk,
        "top_raw_g": float(np.max(resultant(top))),
        "ch4_raw_g": float(np.max(np.abs(top[:, 2]))),
        "sat": sat,
    }
    if not is_real:
        return row

    top180 = np.stack([cfc_filter(top[:, j], fs, 180) for j in range(3)], axis=1)
    m_top = windowed_peak(t, resultant(top180), i_imp, dt)
    m_ch5_180 = windowed_peak(t, cfc_filter(ch5, fs, 180), i_imp, dt)
    m_ch5_1000 = windowed_peak(t, cfc_filter(ch5, fs, 1000), i_imp, dt)

    row.update({
        "top_180_g": m_top["peak_abs_g"],
        "ch5_180_g": m_ch5_180["peak_abs_g"],
        "ch5_1000_g": m_ch5_1000["peak_abs_g"],
        "t_ch5": m_top["peak_abs_g"] / m_ch5_180["peak_abs_g"],
        "top_width_ms": m_top["pulse_width_ms"],
        "ch5_width_ms": m_ch5_180["pulse_width_ms"],
        "ch5_dv_ms": m_ch5_180["delta_v_ms"],
        "dom_freq_hz": ringdown_dom_freq(t, top, i_imp, fs),
    })
    # Retain a short CH5 window around the impact for the trace figure so the
    # analog flat-topping at the saturating conditions is visible.
    half = int(0.0025 / dt)
    lo, hi = max(0, i_imp - half), min(len(t), i_imp + half)
    row["ch5_trace_ms"] = ((t[lo:hi] - t[i_imp]) * 1e3).tolist()
    row["ch5_trace_g"] = ch5[lo:hi].tolist()
    return row


def ols_multi(X: np.ndarray, y: np.ndarray, names: list[str]) -> dict:
    """Ordinary least squares with an intercept; returns per-term stats."""
    n, k = X.shape
    A = np.column_stack([np.ones(n), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    dof = n - (k + 1)
    sigma2 = float(resid @ resid) / dof
    cov = sigma2 * np.linalg.inv(A.T @ A)
    se = np.sqrt(np.diag(cov))
    tvals = beta / se
    pvals = 2.0 * stats.t.sf(np.abs(tvals), dof)
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - float(resid @ resid) / ss_tot if ss_tot else float("nan")
    r2_adj = 1.0 - (1.0 - r2) * (n - 1) / dof if dof else float("nan")
    terms = ["intercept"] + names
    return {
        "n": n, "r2": r2, "r2_adj": r2_adj, "sigma": float(np.sqrt(sigma2)),
        "coef": {t: {"beta": float(b), "se": float(s), "t": float(tv),
                     "p": float(p)}
                 for t, b, s, tv, p in zip(terms, beta, se, tvals, pvals)},
    }


def arr(rows, key):
    return np.array([r[key] for r in rows], float)


def main() -> int:
    conds = []
    for h, felt, sigs in CONDITIONS:
        rows = []
        for k, sig in enumerate(sigs, start=1):
            row = analyze_capture(RAW / f"height_level_Signal{sig}.csv")
            row["signal"] = sig
            row["drop"] = k
            row["height_in"] = h
            row["n_felt"] = felt
            rows.append(row)
        conds.append({"height_in": h, "n_felt": felt,
                      "signals": [int(min(sigs)), int(max(sigs))], "rows": rows})

    print("=== Felt-sheet cushioning / saturation sweep (CH5 trigger @ 300 G) ===\n")
    print(f"{'height':>6} {'felt':>4} {'n':>2}  {'CH5 raw G':>18}  {'CH5 %FS':>8}  "
          f"{'CH4 %FS':>8}  {'TOP180 G':>9}  {'CH5-180 G':>9}  {'T':>5}  clip")

    summary = {"trigger_level_g": TRIGGER_LEVEL_G, "full_scale_g": FULL_SCALE_G,
               "conditions": []}
    for c in conds:
        real = [r for r in c["rows"] if r["real_impact"]]
        ch5_raw = arr(real, "ch5_raw_g")
        ch5_fs = ch5_raw / FULL_SCALE_G["CH5"]
        ch4_fs = arr(real, "ch4_raw_g") / FULL_SCALE_G["CH4"]
        top180 = arr(real, "top_180_g")
        ch5_180 = arr(real, "ch5_180_g")
        tch5 = arr(real, "t_ch5")
        clip_ch5 = max(r["sat"]["CH5"]["clip_run_samples"] for r in real)
        n_over = sum(r["sat"]["CH5"]["over_fs"] for r in real)

        cd = {
            "height_in": c["height_in"], "n_felt": c["n_felt"],
            "signals": c["signals"], "n_real": len(real),
            "ch5_raw_g": {"mean": float(ch5_raw.mean()), "std": float(ch5_raw.std(ddof=1)),
                          "max": float(ch5_raw.max()), "cv": cv(ch5_raw)},
            "ch5_frac_fs": {"mean": float(ch5_fs.mean()), "max": float(ch5_fs.max())},
            "ch4_frac_fs": {"mean": float(ch4_fs.mean()), "max": float(ch4_fs.max())},
            "ch5_over_fs_count": int(n_over),
            "ch5_clip_run_samples": int(clip_ch5),
            "top_180_g": {"mean": float(top180.mean()), "cv": cv(top180)},
            "ch5_180_g": {"mean": float(ch5_180.mean()), "cv": cv(ch5_180)},
            "t_ch5": {"mean": float(tch5.mean()), "cv": cv(tch5)},
            "per_capture": c["rows"],
        }
        summary["conditions"].append(cd)
        flag = "  <-- CLIP" if (n_over or clip_ch5 > 3) else ""
        print(f"{c['height_in']:>4}in {c['n_felt']:>4} {len(real):>2}  "
              f"{ch5_raw.mean():>7.0f}+-{ch5_raw.std(ddof=1):<3.0f} "
              f"(max {ch5_raw.max():>5.0f})  {100*ch5_fs.mean():>6.1f}%  "
              f"{100*ch4_fs.mean():>6.1f}%  {top180.mean():>9.0f}  "
              f"{ch5_180.mean():>9.0f}  {tch5.mean():>5.3f}  {clip_ch5:>2}{flag}")

    # ------------------- saturation verdict -------------------------------
    sat_conds = [cd for cd in summary["conditions"]
                 if cd["ch5_over_fs_count"] or cd["ch5_clip_run_samples"] > 3
                 or cd["ch5_frac_fs"]["max"] >= 0.98]
    print("\n=== saturation verdict ===")
    print(f"CH5 single-axis full scale: {FULL_SCALE_G['CH5']:.1f} G "
          f"(the low-ceiling channel); CH4 (output trigger axis) FS "
          f"{FULL_SCALE_G['CH4']:.1f} G")
    if sat_conds:
        for cd in sat_conds:
            print(f"  SATURATED/near-FS: {cd['height_in']}in / {cd['n_felt']} felt "
                  f"-> CH5 max {100*cd['ch5_frac_fs']['max']:.1f}% FS, "
                  f"over-FS on {cd['ch5_over_fs_count']}/{cd['n_real']} drops, "
                  f"worst flat-top {cd['ch5_clip_run_samples']} samples")
    else:
        print("  no condition saturated CH5")
    summary["saturated_conditions"] = [
        {"height_in": cd["height_in"], "n_felt": cd["n_felt"],
         "ch5_max_frac_fs": cd["ch5_frac_fs"]["max"],
         "ch5_over_fs_count": cd["ch5_over_fs_count"]}
        for cd in sat_conds]

    # ------------------- OLS: height + felt separation --------------------
    all_real = [r for c in conds for r in c["rows"] if r["real_impact"]]
    H = arr(all_real, "height_in")
    F = arr(all_real, "n_felt")
    ch5 = arr(all_real, "ch5_raw_g")
    log_ch5 = np.log10(ch5)

    print("\n=== OLS regression (n = %d captured drops) ===" % len(all_real))
    print("model A: log10(CH5 raw peak) ~ height_in + n_felt")
    olsA = ols_multi(np.column_stack([H, F]), log_ch5, ["height_in", "n_felt"])
    for term, s in olsA["coef"].items():
        print(f"  {term:11s}: beta {s['beta']:+.4f}  (SE {s['se']:.4f}, "
              f"t {s['t']:+.2f}, p {s['p']:.2e})")
    print(f"  R^2 {olsA['r2']:.3f} (adj {olsA['r2_adj']:.3f})")
    b_h = olsA["coef"]["height_in"]["beta"]
    b_f = olsA["coef"]["n_felt"]["beta"]
    print(f"  => each +10 in raises CH5 peak x{10**(10*b_h):.2f}; "
          f"each +1 felt sheet multiplies it x{10**b_f:.2f} "
          f"({(1-10**b_f)*100:.0f}% attenuation per sheet)")

    # linear (not log) model for a direct G/in and G/sheet reading
    olsB = ols_multi(np.column_stack([H, F]), ch5, ["height_in", "n_felt"])
    print("model B: CH5 raw peak (G) ~ height_in + n_felt")
    for term, s in olsB["coef"].items():
        print(f"  {term:11s}: beta {s['beta']:+.1f} G  (p {s['p']:.2e})")
    print(f"  R^2 {olsB['r2']:.3f} (adj {olsB['r2_adj']:.3f})")

    # output (TOP CFC-180, the BO objective surrogate) vs the same predictors
    top = arr(all_real, "top_180_g")
    olsC = ols_multi(np.column_stack([H, F]), np.log10(top),
                     ["height_in", "n_felt"])
    summary["ols"] = {"log10_ch5_vs_height_felt": olsA,
                      "ch5_vs_height_felt": olsB,
                      "log10_top180_vs_height_felt": olsC}

    # ------------------- recommendation -----------------------------------
    # The TOP CFC-180 output (the BO objective surrogate) is far less sensitive
    # to the input than CH5 is: it only ranges ~300-460 G across a 7x change in
    # CH5, because it is set by the specimen's own response, not the raw base
    # hit. So a harsh (near-saturating) input buys almost no extra output while
    # eating the CH5 head-room that stiffer/larger designs in the BO search
    # space will need. The operating point is therefore chosen to
    #   (a) keep the CH5 bottleneck below FS by a safety factor (so a design
    #       up to SAFETY x stiffer than this near-saturation specimen still
    #       fits under 9,442.9 G), and
    #   (b) among those, maximise the repeatable TOP output (best BO SNR).
    SAFETY = 3.0  # allow a 3x stiffer design before CH5 clips
    ch5_ceiling = FULL_SCALE_G["CH5"] / SAFETY
    snr_floor_g = 5.0 * TRIGGER_LEVEL_G  # CH5 mean must stay well above trigger
    usable = []
    for cd in summary["conditions"]:
        if (cd["ch5_frac_fs"]["max"] * FULL_SCALE_G["CH5"] <= ch5_ceiling
                and cd["ch5_over_fs_count"] == 0
                and cd["ch5_raw_g"]["mean"] >= snr_floor_g):
            usable.append(cd)
    usable.sort(key=lambda cd: -cd["top_180_g"]["mean"])  # strongest output first

    # Inverse OLS: felt sheets needed to hold CH5 max at the ceiling per height.
    def felt_needed(height_in: float) -> float:
        target = np.log10(ch5_ceiling)
        return (target - olsA["coef"]["intercept"]["beta"]
                - b_h * height_in) / b_f

    print("\n=== recommendation ===")
    print(f"CH5 head-room target: keep max |peak| <= FS/{SAFETY:.0f} = "
          f"{ch5_ceiling:.0f} G (room for a {SAFETY:.0f}x stiffer BO design), "
          f"CH5 mean >= {snr_floor_g:.0f} G ({snr_floor_g/TRIGGER_LEVEL_G:.0f}x "
          f"trigger)")
    print("  felt sheets to hold CH5 max at the ceiling (inverse OLS):")
    for h in (20, 30, 40, 50, 60):
        print(f"    {h} in -> >= {felt_needed(h):.1f} felt sheets")
    if usable:
        best = usable[0]
        alt = usable[1] if len(usable) > 1 else best
        print(f"  PRIMARY: {best['height_in']} in + {best['n_felt']} felt sheets "
              f"-> CH5 {best['ch5_raw_g']['mean']:.0f} G "
              f"({100*best['ch5_frac_fs']['max']:.0f}% FS max, "
              f"{FULL_SCALE_G['CH5']/(best['ch5_frac_fs']['max']*FULL_SCALE_G['CH5']):.1f}x head-room), "
              f"TOP180 {best['top_180_g']['mean']:.0f} G "
              f"(CV {best['top_180_g']['cv']:.1f}%), T {best['t_ch5']['mean']:.3f}")
        print(f"  LOWER-HEIGHT ALT: {alt['height_in']} in + {alt['n_felt']} felt "
              f"-> CH5 {100*alt['ch5_frac_fs']['max']:.0f}% FS, "
              f"TOP180 {alt['top_180_g']['mean']:.0f} G")
        summary["recommendation"] = {
            "safety_factor": SAFETY, "ch5_ceiling_g": ch5_ceiling,
            "snr_floor_g": snr_floor_g,
            "primary": {"height_in": best["height_in"], "n_felt": best["n_felt"],
                        "ch5_mean_g": best["ch5_raw_g"]["mean"],
                        "ch5_max_frac_fs": best["ch5_frac_fs"]["max"],
                        "top_180_g": best["top_180_g"]["mean"]},
            "felt_needed_per_height": {str(h): float(felt_needed(h))
                                       for h in (20, 30, 40, 50, 60)},
            "usable_ranked": [{"height_in": cd["height_in"],
                               "n_felt": cd["n_felt"],
                               "ch5_mean_g": cd["ch5_raw_g"]["mean"],
                               "ch5_max_frac_fs": cd["ch5_frac_fs"]["max"],
                               "top_180_g": cd["top_180_g"]["mean"]}
                              for cd in usable]}
    else:
        print("  no condition met the head-room + SNR target")
        summary["recommendation"] = {"safety_factor": SAFETY,
                                      "ch5_ceiling_g": ch5_ceiling,
                                      "usable_ranked": []}

    # ------------------- figures ------------------------------------------
    labels = [f"{cd['height_in']}in\n{cd['n_felt']}f" for cd in summary["conditions"]]
    x = np.arange(len(labels))

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 9))
    ch5_mean = [cd["ch5_raw_g"]["mean"] for cd in summary["conditions"]]
    ch5_err = [cd["ch5_raw_g"]["std"] for cd in summary["conditions"]]
    ch5_max = [cd["ch5_raw_g"]["max"] for cd in summary["conditions"]]
    bars = a1.bar(x, ch5_mean, yerr=ch5_err, capsize=3, color="tab:blue",
                  alpha=0.8, label="CH5 raw |peak| (mean +- SD)")
    a1.plot(x, ch5_max, "kv", ms=6, label="worst-case drop")
    a1.axhline(FULL_SCALE_G["CH5"], color="tab:red", lw=1.6,
               label=f"CH5 full scale ({FULL_SCALE_G['CH5']:.0f} G)")
    a1.axhline(FULL_SCALE_G["CH5"] / SAFETY, color="tab:orange", ls="--",
               lw=1.2, label=f"FS/{SAFETY:.0f} head-room target "
                             f"({FULL_SCALE_G['CH5']/SAFETY:.0f} G)")
    a1.axhline(TRIGGER_LEVEL_G, color="k", ls=":", lw=1, label="300 G trigger")
    for xi, cd in zip(x, summary["conditions"]):
        if cd["ch5_over_fs_count"] or cd["ch5_frac_fs"]["max"] >= 0.98:
            a1.text(xi, FULL_SCALE_G["CH5"] * 1.02, "CLIP", ha="center",
                    color="tab:red", fontsize=8, fontweight="bold")
    a1.set(xticks=x, xticklabels=labels, ylabel="acceleration (G)", yscale="log",
           title="CH5 base-plate single-axis (FS 9,442.9 G): the saturation bottleneck")
    a1.legend(fontsize=8, loc="lower right")
    a1.grid(alpha=0.3, axis="y")

    ch5_fs = [100 * cd["ch5_frac_fs"]["max"] for cd in summary["conditions"]]
    ch4_fs = [100 * cd["ch4_frac_fs"]["max"] for cd in summary["conditions"]]
    w = 0.4
    a2.bar(x - w / 2, ch5_fs, w, color="tab:blue", label="CH5 (single-axis, FS 9,442.9 G)")
    a2.bar(x + w / 2, ch4_fs, w, color="tab:green", label="CH4 (top tri-axis, FS 13,624 G)")
    a2.axhline(100, color="tab:red", lw=1.4, label="full scale")
    a2.axhline(100 / SAFETY, color="tab:orange", ls="--", lw=1.2,
               label=f"FS/{SAFETY:.0f} head-room")
    a2.set(xticks=x, xticklabels=labels, ylabel="worst-case raw |peak| (% FS)",
           xlabel="condition (drop height / felt sheets)",
           title="Saturation head-room per condition")
    a2.legend(fontsize=8)
    a2.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(FIG / "01_saturation_by_condition.png", dpi=130)
    plt.close(fig)

    # height vs felt effect (OLS surface on CH5)
    fig, (b1, b2) = plt.subplots(1, 2, figsize=(13, 5))
    cmap = plt.get_cmap("viridis")
    felts = sorted({cd["n_felt"] for cd in summary["conditions"]})
    for nf in felts:
        pts = [(cd["height_in"], cd["ch5_raw_g"]["mean"])
               for cd in summary["conditions"] if cd["n_felt"] == nf]
        pts.sort()
        hs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        b1.plot(hs, ys, "o-", color=cmap(nf / max(felts)), label=f"{nf} felt")
    b1.axhline(FULL_SCALE_G["CH5"], color="tab:red", lw=1.4, label="CH5 FS")
    b1.set(xlabel="drop height (in)", ylabel="CH5 raw |peak| (G)", yscale="log",
           title="Height raises the hit; each felt sheet cushions it")
    b1.legend(fontsize=8)
    b1.grid(alpha=0.3)

    # OLS fit quality: predicted vs observed (log model)
    A = np.column_stack([np.ones(len(H)), H, F])
    beta = np.array([olsA["coef"][t]["beta"]
                     for t in ["intercept", "height_in", "n_felt"]])
    pred = A @ beta
    b2.scatter(log_ch5, pred, c=F, cmap="autumn", s=30)
    lim = [min(log_ch5.min(), pred.min()), max(log_ch5.max(), pred.max())]
    b2.plot(lim, lim, "k--", lw=1)
    b2.set(xlabel="observed log10(CH5 peak)", ylabel="OLS prediction",
           title=f"OLS log10(CH5) ~ height + felt  (R^2 = {olsA['r2']:.2f})")
    b2.grid(alpha=0.3)
    fig.colorbar(b2.collections[0], ax=b2, label="n felt")
    fig.tight_layout()
    fig.savefig(FIG / "02_height_felt_ols.png", dpi=130)
    plt.close(fig)

    # representative CH5 impact-window trace per condition (shows flat-topping
    # at the saturating conditions vs a clean pulse where there is head-room)
    fig, ax = plt.subplots(figsize=(11, 6))
    cmap = plt.get_cmap("turbo")
    for k, c in enumerate(conds):
        real = [r for r in c["rows"] if r["real_impact"] and "ch5_trace_g" in r]
        if not real:
            continue
        # pick the worst-case (largest raw peak) drop in the condition
        r = max(real, key=lambda rr: rr["ch5_raw_g"])
        col = cmap(k / max(1, len(conds) - 1))
        clip = r["sat"]["CH5"]["over_fs"] or r["sat"]["CH5"]["clip_run_samples"] > 3
        ax.plot(r["ch5_trace_ms"], r["ch5_trace_g"], color=col, lw=1.3,
                label=f"{c['height_in']}in/{c['n_felt']}f"
                      f"{' CLIP' if clip else ''}")
    ax.axhline(FULL_SCALE_G["CH5"], color="tab:red", lw=1.5, ls="-",
               label=f"CH5 FS ({FULL_SCALE_G['CH5']:.0f} G)")
    ax.axhline(-FULL_SCALE_G["CH5"], color="tab:red", lw=1.5, ls="-")
    ax.set(xlabel="time relative to CH5 impact (ms)",
           ylabel="CH5 base-plate acceleration (G)",
           title="Worst-case CH5 impact window per condition "
                 "(flat top = analog saturation)")
    ax.legend(fontsize=7, ncol=3, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_ch5_impact_traces.png", dpi=130)
    plt.close(fig)

    # strip the (large) raw traces before serialising the metrics JSON
    for cd in summary["conditions"]:
        for r in cd["per_capture"]:
            r.pop("ch5_trace_ms", None)
            r.pop("ch5_trace_g", None)
    with open(FIG / "felt_sheet_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
