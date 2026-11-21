#!/usr/bin/env python3
"""Second 500-drop failure test (same bubbled-TPU print, 10 in, CH5 @ 300 G),
this time with the bottom tri-axis (CH6-8) physically removed: OLS trend
analysis + do we actually need the BOT station?

@ctrhjk re-ran the failure test on the same specimen as the first 500-drop
attempt (which a TP4 overload -- CH6 walking over its 1,002 G full scale --
halted at drop 256). For this run the bottom low-range tri-axis was
disconnected, leaving CH2-4 (TOP output) + CH5 (base-plate input, trigger).
This script answers:

  1. **Run health** -- did removing the only channel that could overload let
     the run complete all 500 drops, with clean triggers and no channel near
     full scale?
  2. **OLS regressions** -- trends of every metric vs drop number (the
     explicit ask), including the severity drift seen in every long campaign.
  3. **BOT necessity** -- compared against the first run's metrics
     (``data/drop-tests/500drops/figures/500drops_metrics.json``): what
     information did CH6-8 uniquely provide, and was any of it required for
     the BO objective stack (T = TOP/CH5, output peak, ringdown mode)?
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
RAW = REPO / "data" / "drop-tests" / "500drops-nobot" / "raw"
FIG = REPO / "data" / "drop-tests" / "500drops-nobot" / "figures"
PREV_METRICS = REPO / "data" / "drop-tests" / "500drops" / "figures" / "500drops_metrics.json"
FIG.mkdir(parents=True, exist_ok=True)

GRAVITY = 9.80665  # m/s^2 per G

TOP_COLS = (0, 1, 2)  # CH2, CH3, CH4 -- tri-axis output, top-vertex key-seat
CH5 = 3  # single-axis on the base plate -- the trigger channel (300 G)

CH_NAMES = ("CH2", "CH3", "CH4", "CH5")
FULL_SCALE_G = {"CH2": 14492.8, "CH3": 14992.5, "CH4": 13624.0, "CH5": 9442.9}

TRIGGER_LEVEL_G = 300.0
IMPACT_HALF_WIN_S = 0.0015
BASELINE_S = 0.0028
TP4_HEADER_LINES = 9

RING_BAND_HZ = (100.0, 2000.0)
RING_START_AFTER_IMPACT_S = 0.002
RING_LEN_S = 0.080

SIGNALS = range(1, 501)  # 500_Signal1..500 -- the run completed this time
REAL_IMPACT_FLOOR_G = 300.0


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

    top_res_raw = resultant(top)

    i_imp = int(np.argmax(top_res_raw))
    top_raw_pk = float(top_res_raw[i_imp])
    is_real = top_raw_pk >= REAL_IMPACT_FLOOR_G

    over = np.abs(ch5) >= TRIGGER_LEVEL_G
    i_x = int(np.argmax(over)) if over.any() else -1
    t_x_ms = float(t[i_x] * 1e3) if i_x >= 0 else float("nan")
    pre = np.abs(ch5[t < 0.0035])
    pre_max_g = float(pre.max()) if len(pre) else 0.0

    sat = {}
    for j, name in enumerate(CH_NAMES):
        x = np.abs(ch[:, j] - np.median(ch[:nb, j]))
        pk = float(x.max())
        sat[name] = {"peak_g": pk, "frac_fs": pk / FULL_SCALE_G[name]}

    row = {
        "signal": None,
        "event_time": event_time(path).isoformat(),
        "real_impact": bool(is_real),
        "t_imp_ms": float(t[i_imp] * 1e3),
        "trig_cross_ms": t_x_ms,
        "pre_trigger_max_g": pre_max_g,
        "top_raw_g": top_raw_pk,
        "ch5_raw_g": float(np.max(np.abs(ch5))),
        "sat": sat,
        "noise_top_g": [float(np.std(top[:nb, j])) for j in range(3)],
    }
    if not is_real:
        return row

    top180 = np.stack([cfc_filter(top[:, j], fs, 180) for j in range(3)], axis=1)
    m_top = windowed_peak(t, resultant(top180), i_imp, dt)
    m_ch5 = windowed_peak(t, cfc_filter(ch5, fs, 180), i_imp, dt)

    row.update({
        "top_180_g": m_top["peak_abs_g"],
        "ch5_180_g": m_ch5["peak_abs_g"],
        "t_ch5": m_top["peak_abs_g"] / m_ch5["peak_abs_g"],
        "top_width_ms": m_top["pulse_width_ms"],
        "ch5_dv_ms": m_ch5["delta_v_ms"],
        "dom_freq_hz": ringdown_dom_freq(t, top, i_imp, fs),
    })
    return row


def ols_full(x, y) -> dict:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    res = stats.linregress(x, y)
    mean = float(np.mean(y))
    return {"n": len(x), "slope": float(res.slope),
            "slope_pct": float(100.0 * res.slope / mean),
            "stderr": float(res.stderr),
            "p": float(res.pvalue), "r2": float(res.rvalue**2),
            "mean": mean, "cv": cv(y)}


def main() -> int:
    rows: list[dict] = []
    for sig in SIGNALS:
        row = analyze_capture(RAW / f"500_Signal{sig}.csv")
        row["signal"] = sig
        rows.append(row)

    real = [r for r in rows if r["real_impact"]]
    for k, r in enumerate(real, start=1):
        r["drop"] = k
    spurious = [r["signal"] for r in rows if not r["real_impact"]]
    times = [datetime.fromisoformat(r["event_time"]) for r in rows]
    gaps = np.array([(b - a).total_seconds() for a, b in zip(times, times[1:])])
    t_cross = np.array([r["trig_cross_ms"] for r in real])
    drops = np.array([r["drop"] for r in real], float)
    sigs = np.array([r["signal"] for r in rows], float)

    print("=== 2nd 500-drop failure test (BOT removed, 10 in): run health ===\n")
    print(f"captures: {len(rows)} = {len(real)} real + {len(spurious)} spurious {spurious}")
    print(f"cadence: median {np.median(gaps):.0f} s; max gap {gaps.max():.0f} s; span "
          f"{(times[-1] - times[0]).total_seconds() / 60:.0f} min "
          f"({times[0].time()} - {times[-1].time()})")
    print(f"CH5 first crossing of {TRIGGER_LEVEL_G:.0f} G: "
          f"{t_cross.mean():.3f} +- {t_cross.std():.3f} ms")
    pre_worst = max(r["pre_trigger_max_g"] for r in rows)
    print(f"worst pre-impact CH5 activity: {pre_worst:.1f} G "
          f"({TRIGGER_LEVEL_G / pre_worst:.0f}x below the 300 G level)")

    # ---------------- saturation audit (the overload question) --------
    print("\n=== Saturation audit: raw |peak| vs full scale, per channel ===\n")
    sat_summary = {}
    for name in CH_NAMES:
        fr = np.array([r["sat"][name]["frac_fs"] for r in rows])
        n95 = int((fr >= 0.95).sum())
        n_over = int((fr > 1.0).sum())
        sat_summary[name] = {"full_scale_g": FULL_SCALE_G[name],
                             "median_frac_fs": float(np.median(fr)),
                             "max_frac_fs": float(fr.max()),
                             "n_ge_95pct_fs": n95, "n_over_fs": n_over}
        print(f"  {name}: FS {FULL_SCALE_G[name]:8.1f} G   median {100 * np.median(fr):5.1f}% FS   "
              f"max {100 * fr.max():5.1f}% FS   >=95% FS on {n95:3d}/500   >FS on {n_over:3d}/500")

    # ---------------- OLS regressions ---------------------------------
    top = np.array([r["top_180_g"] for r in real])
    ch5v = np.array([r["ch5_180_g"] for r in real])
    tch5 = np.array([r["t_ch5"] for r in real])
    ch5_raw = np.array([r["ch5_raw_g"] for r in real])
    top_raw = np.array([r["top_raw_g"] for r in real])
    width = np.array([r["top_width_ms"] for r in real])
    dv = np.array([r["ch5_dv_ms"] for r in real])
    dom = np.array([r["dom_freq_hz"] for r in real])

    print("\n=== OLS regressions vs drop # (full run, n = %d) ===\n" % len(real))
    trends = {}
    for name, y in [("CH5 raw", ch5_raw), ("TOP raw resultant", top_raw),
                    ("CH5 CFC-180", ch5v), ("TOP CFC-180", top),
                    ("T = TOP/CH5", tch5), ("pulse width (ms)", width),
                    ("input dv (m/s)", dv), ("dom freq (Hz)", dom)]:
        o = ols_full(drops, y)
        trends[name] = o
        total = o["slope"] * (len(drops) - 1)
        print(f"  {name:18s}: mean {o['mean']:8.2f}  CV {o['cv']:5.2f}%   "
              f"slope {o['slope_pct']:+.4f}%/drop (p = {o['p']:.2e}, R^2 = {o['r2']:.3f})   "
              f"net over run {total / o['mean'] * 100:+.0f}%")

    # first vs second half OLS -- does the drift saturate?
    print("\nOLS by half (does the severity drift saturate?):")
    trends_halves = {}
    for name, y in [("CH5 CFC-180", ch5v), ("TOP CFC-180", top),
                    ("T = TOP/CH5", tch5), ("input dv (m/s)", dv)]:
        h1 = ols_full(drops[:250], y[:250])
        h2 = ols_full(drops[250:], y[250:])
        trends_halves[name] = {"first_half": h1, "second_half": h2}
        print(f"  {name:18s}: 1-250 {h1['slope_pct']:+.4f}%/drop (p={h1['p']:.1e})   "
              f"251-500 {h2['slope_pct']:+.4f}%/drop (p={h2['p']:.1e})")

    n_low = int((dom < 200).sum())
    print(f"\nringdown dominant mode: median {np.median(dom):.0f} Hz "
          f"(range {dom.min():.0f}-{dom.max():.0f}); < 200 Hz on {n_low}/{len(real)} drops")
    low_sigs = [int(d) for d, f in zip(drops, dom) if f < 200]
    if low_sigs:
        print(f"  low-mode drops: {low_sigs}")

    # ---------------- comparison vs run 1 (BOT present) ---------------
    prev = json.loads(PREV_METRICS.read_text())
    p_t = np.array(prev["per_capture"]["t_ch5"], float)
    p_ch5 = np.array(prev["per_capture"]["ch5_180_g"], float)
    p_top = np.array(prev["per_capture"]["top_180_g"], float)
    p_dv = np.array(prev["per_capture"]["ch5_dv_ms"], float)
    p_dom = np.array(prev["per_capture"]["dom_freq_hz"], float)
    p_drops = np.arange(1, len(p_t) + 1, dtype=float)

    print("\n=== vs run 1 (same specimen, BOT present, stopped at 256) ===\n")
    comparison = {}
    for name, y2, y1 in [("CH5 CFC-180", ch5v, p_ch5), ("TOP CFC-180", top, p_top),
                         ("T = TOP/CH5", tch5, p_t), ("input dv (m/s)", dv, p_dv)]:
        w = stats.ttest_ind(y1, y2[: len(y1)], equal_var=False)
        comparison[name] = {
            "run1_mean": float(y1.mean()), "run1_cv": cv(y1),
            "run2_mean": float(y2.mean()), "run2_cv": cv(y2),
            "run2_first256_mean": float(y2[: len(y1)].mean()),
            "welch_p_first256": float(w.pvalue),
        }
        print(f"  {name:18s}: run1 {y1.mean():8.3f} (CV {cv(y1):.2f}%)   "
              f"run2 {y2.mean():8.3f} (CV {cv(y2):.2f}%)   "
              f"run2[1..256] {y2[:len(y1)].mean():8.3f} (Welch p = {w.pvalue:.1e})")

    # Did the TOP/CH5 metrics see run 1's CH6 transition (drops ~97-134)?
    # Same-window comparison on run 1's own data: before (60-96) vs after (134-170).
    pre_w = slice(59, 96)
    post_w = slice(133, 170)
    print("\nrun 1's CH6 transition window, as seen by surviving channels (run 1 data):")
    transition_visibility = {}
    for name, y1 in [("T = TOP/CH5", p_t), ("CH5 CFC-180", p_ch5),
                     ("TOP CFC-180", p_top), ("dom freq (Hz)", p_dom)]:
        a, b = y1[pre_w], y1[post_w]
        w = stats.ttest_ind(a, b, equal_var=False)
        transition_visibility[name] = {
            "pre_mean": float(a.mean()), "post_mean": float(b.mean()),
            "shift_pct": float(100 * (b.mean() / a.mean() - 1)), "welch_p": float(w.pvalue)}
        print(f"  {name:18s}: drops 60-96 {a.mean():8.3f} -> drops 134-170 {b.mean():8.3f} "
              f"({100 * (b.mean() / a.mean() - 1):+.2f}%, Welch p = {w.pvalue:.1e})")

    # ---------------- figures ----------------------------------------
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 8.5), sharex=True)
    for name, col in [("CH2", "tab:cyan"), ("CH3", "tab:olive"), ("CH4", "tab:red"),
                      ("CH5", "tab:blue")]:
        fr = [100 * r["sat"][name]["frac_fs"] for r in rows]
        a1.plot(sigs, fr, "o-", ms=2, lw=0.8, color=col,
                label=f"{name} raw |peak| (FS = {FULL_SCALE_G[name]:.0f} G)")
    a1.axhline(100, color="k", ls="-", lw=1.2, label="full scale (TP4 overload)")
    a1.axhline(95, color="k", ls=":", lw=1)
    a1.set(ylabel="raw |peak| (% of full scale)", ylim=(0, 110),
           title="2nd 500-drop failure test (BOT removed) — no channel near full scale, 500/500 complete")
    a1.legend(fontsize=8, ncol=2)
    a1.grid(alpha=0.3)
    a2.plot(sigs, [r["ch5_raw_g"] for r in rows], "o-", ms=2, lw=0.8,
            color="tab:blue", label="CH5 raw |peak| (plate, trigger)")
    a2.plot(sigs, [r["top_raw_g"] for r in rows], "s-", ms=2, lw=0.8,
            color="tab:red", label="TOP raw resultant peak (CH2-4)")
    a2.axhline(TRIGGER_LEVEL_G, color="k", ls=":", lw=1.2, label="300 G trigger level")
    a2.set(xlabel="capture (Signal # = drop #)", ylabel="raw |peak| (G)", yscale="log")
    a2.legend(fontsize=8)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_run_health.png", dpi=130)
    plt.close(fig)

    fig, (b1, b2, b3) = plt.subplots(3, 1, figsize=(12, 11), sharex=True)
    for y, colr, lab in [(ch5v, "tab:blue", "CH5 CFC-180 peak"),
                         (top, "tab:red", "TOP CFC-180 peak")]:
        b1.plot(drops, y, "o-", ms=2, lw=0.8, color=colr, label=lab)
        o = ols_full(drops, y)
        b1.plot(drops, o["mean"] + o["slope"] * (drops - drops.mean()), "--",
                color=colr, lw=1.5,
                label=f"OLS {o['slope_pct']:+.4f}%/drop (p={o['p']:.0e})")
    b1.set(ylabel="CFC-180 peak (G)",
           title="OLS trends over 500 drops: levels, transmissibility, ringdown mode")
    b1.legend(fontsize=8)
    b1.grid(alpha=0.3)
    o = ols_full(drops, tch5)
    b2.plot(drops, tch5, "o-", ms=2, lw=0.8, color="tab:purple", label="T = TOP/CH5")
    b2.plot(drops, o["mean"] + o["slope"] * (drops - drops.mean()), "--",
            color="k", lw=1.5, label=f"OLS {o['slope_pct']:+.4f}%/drop (p={o['p']:.0e})")
    b2.set(ylabel="transmissibility")
    b2.legend(fontsize=8)
    b2.grid(alpha=0.3)
    b3.plot(drops, dom, "o", ms=3, color="tab:red", label="dominant ringdown mode (TOP)")
    b3.set(xlabel="drop #", ylabel="frequency (Hz)")
    b3.legend(fontsize=8)
    b3.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "02_ols_trends.png", dpi=130)
    plt.close(fig)

    fig, (c1, c2) = plt.subplots(2, 1, figsize=(12, 8.5), sharex=True)
    c1.plot(p_drops, p_t, "o-", ms=2, lw=0.7, color="tab:gray",
            label="run 1 (BOT present, stopped at 256)")
    c1.plot(drops, tch5, "o-", ms=2, lw=0.7, color="tab:purple",
            label="run 2 (BOT removed, 500/500)")
    c1.axvspan(97, 134, color="tab:green", alpha=0.15,
               label="run 1 CH6 transition window (drops 97-134)")
    c1.set(ylabel="T = TOP/CH5",
           title="Same specimen, back-to-back failure tests: run 1 (with BOT) vs run 2 (BOT removed)")
    c1.legend(fontsize=8)
    c1.grid(alpha=0.3)
    c2.plot(p_drops, p_ch5, "o-", ms=2, lw=0.7, color="tab:gray", label="run 1 CH5 CFC-180")
    c2.plot(drops, ch5v, "o-", ms=2, lw=0.7, color="tab:blue", label="run 2 CH5 CFC-180")
    c2.set(xlabel="drop #", ylabel="CH5 CFC-180 peak (G)")
    c2.legend(fontsize=8)
    c2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_run1_vs_run2.png", dpi=130)
    plt.close(fig)

    # ---------------- metrics JSON ------------------------------------
    def col(key, pool=rows, default=float("nan")):
        return [r.get(key, default) for r in pool]

    summary = {
        "specimen": "same bubbled-TPU print as the first 500-drop test (PR #35, 2026-07-15); "
                    "~256 prior drops of history",
        "setup": {"height_in": 10, "trigger": "CH5 @ 300 G", "planned_drops": 500,
                  "recorded_drops": len(rows),
                  "bot_station": "CH6-8 removed for this run",
                  "stop_reason": "completed"},
        "n_captures": len(rows),
        "spurious_captures": spurious,
        "cadence_s_median": float(np.median(gaps)),
        "cadence_s_max": float(gaps.max()),
        "trigger_cross_ms": {"mean": float(t_cross.mean()), "std": float(t_cross.std())},
        "worst_pre_trigger_g": pre_worst,
        "saturation": sat_summary,
        "trends_ols": trends,
        "trends_ols_halves": trends_halves,
        "vs_run1": comparison,
        "run1_transition_visibility_in_surviving_channels": transition_visibility,
        "ringdown": {"median_hz": float(np.median(dom)),
                     "min_hz": float(dom.min()), "max_hz": float(dom.max()),
                     "n_below_200hz": n_low, "low_mode_drops": low_sigs},
        "per_capture": {
            "signal": col("signal"),
            "event_time": col("event_time"),
            "ch5_raw_g": col("ch5_raw_g"),
            "top_raw_g": col("top_raw_g"),
            "ch5_180_g": col("ch5_180_g"),
            "top_180_g": col("top_180_g"),
            "t_ch5": col("t_ch5"),
            "top_width_ms": col("top_width_ms"),
            "ch5_dv_ms": col("ch5_dv_ms"),
            "dom_freq_hz": col("dom_freq_hz"),
            "frac_fs": {n: [r["sat"][n]["frac_fs"] for r in rows] for n in CH_NAMES},
        },
    }
    with open(FIG / "500drops_nobot_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
