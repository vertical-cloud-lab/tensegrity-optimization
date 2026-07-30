#!/usr/bin/env python3
"""Polyurethane sheet-configuration sweep — which stack to run transmissibility on.

@me-madsen posted a four-arrangement sweep on PR #86 (Box folder
``4n678tlpnlk7q50dfi1rh1lkt7p6lx0y``, session "bpx68c - Polyurethane
Rubber - Further Tests", 2026-07-30 13:08-15:10): the same specimen
(``bpx68c``) dropped 10 times on each of

  A. the thin 1/4 in sheet alone            (Signals  1-10, trigger 300 G)
  B. the thick 1/2 in sheet alone           (Signals 11-20, trigger 300 G)
  C. 1/4 in on top of 1/2 in                (Signals 22-31, trigger 150 G)
  D. 1/2 in on top of 1/4 in                (Signals 32-41, trigger 150 G)

Signal 21 is a stray capture between B and C (13:26, 2 min after B ends
and 75 min before C starts) and is excluded per @me-madsen's instruction.
The trigger level was lowered to 150 G for C and D.

This is the "stiffen the operating point" mini-sweep called for by
``docs/drop-test-pu-vs-felt-analysis.md`` §next-steps and the
qualification protocol in ``docs/drop-test-absorber-alternatives.md``
§4.1, so the acceptance criteria there are evaluated directly.

Format: full 4-channel export (CH2-4 = top-vertex key-seat tri-axis "TOP"
output, CH5 = single-axis base-plate input + trigger) at 1.25 MHz over a
20 ms window. Three format-forced conventions, shared with
``drop_test_pu_vs_felt_analysis.py``:

  * baseline is the full-record median (the record starts *on* the
    trigger, so there is no clean pre-trigger window — CH5 CFC-180 already
    reads 35-207 G at t = 0 depending on the configuration);
  * the impact is located at the argmax of the CFC-180-filtered CH5 within
    the first 12 ms, not at the raw trigger spike, because the soft PU
    pulses peak 0.8-2.5 ms into the record;
  * the peak walk is bounded at +-5 ms (the softest stack's half-max width
    alone is ~2.6 ms).

Because the pulse onset is truncated by the trigger, the reported Δv is a
*captured* Δv (lower bound), not the full free-fall Δv — the truncation
fraction is estimated per drop and reported.

Emits ``data/drop-tests/pu-configs/figures/pu_configs_metrics.json``
consumed by ``docs/drop-test-pu-configs-analysis.md``.
"""
from __future__ import annotations

import io
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, signal as sig, stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import (  # noqa: E402
    DATA,
    FULL_SCALE_G,
    GRAVITY,
    TP4_HEADER_LINES,
    arr,
    cfc_filter,
    cv,
    ols_full,
    resultant,
)

OUT = DATA / "pu-configs"
RAW = OUT / "raw"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

TOP_COLS = (0, 1, 2)  # CH2, CH3, CH4
CH5 = 3

SEARCH_S = 0.012  # impact must land in the first 12 ms of the 20 ms record
HALF_WIN_S = 0.005  # peak-walk bound; softest half-max width is ~2.6 ms
DV_TOTAL_S = 0.012  # cumulative-integral plateau (all stacks settle by ~8 ms)

CONFIGS = [
    {"key": "quarter", "label": '1/4 in alone', "short": "A: 1/4",
     "zip": RAW / "quarter-in.zip", "trigger_g": 300.0, "color": "tab:red"},
    {"key": "half", "label": '1/2 in alone', "short": "B: 1/2",
     "zip": RAW / "half-in.zip", "trigger_g": 300.0, "color": "tab:orange"},
    {"key": "quarter_top", "label": '1/4 in on top of 1/2 in', "short": "C: 1/4 over 1/2",
     "zip": RAW / "quarter-top-half-bottom.zip", "trigger_g": 150.0, "color": "tab:green"},
    {"key": "half_top", "label": '1/2 in on top of 1/4 in', "short": "D: 1/2 over 1/4",
     "zip": RAW / "half-top-quarter-bottom.zip", "trigger_g": 150.0, "color": "tab:blue"},
]

# Reference points for the acceptance criteria (docs/drop-test-absorber-alternatives.md
# section 4.1) and for continuity with the felt-era catalogue.
FELT_REF = {
    "label": "4 felt + 1 cardboard (bpx68c, 07-30 a.m.)",
    "ch5_180_g": 407.59, "ch5_180_cv": 2.8, "ch5_width_ms": 1.67,
    "top_180_g": 411.26, "top_180_cv": 3.22, "t": 1.009, "t_cv": 0.44,
    "ch5_raw_g": 1491.25,
}
# The loose-stacked PU run from the paired A/B (docs/drop-test-pu-vs-felt-analysis.md).
PU_AB_REF = {"ch5_180_g": 186.21, "ch5_180_cv": 25.7, "ch5_width_ms": 3.31,
             "top_180_g": 182.14, "top_180_cv": 26.76, "t": 0.976, "t_cv": 1.25,
             "ch5_raw_g": 428.77}

HEADROOM_TARGET_G = FULL_SCALE_G["CH5"] / 3.0  # 3.1 kG FS/3 target
INPUT_BAND_G = (0.8 * FELT_REF["ch5_180_g"], 1.2 * FELT_REF["ch5_180_g"])
WIDTH_BAND_MS = (1.0, 2.5)
TRIGGER_MARGIN_MIN = 2.0  # raw |peak| / trigger level


def load_captures(zpath: Path) -> list[tuple[int, str]]:
    caps = []
    with zipfile.ZipFile(zpath) as zf:
        for member in zf.namelist():
            stem = Path(member).name
            if "Signal" not in stem or not stem.lower().endswith(".csv"):
                continue
            caps.append((int(stem.split("Signal")[1].split(".")[0]),
                         zf.read(member).decode("latin-1")))
    caps.sort(key=lambda c: c[0])
    return caps


def half_max_pulse(t: np.ndarray, a_g: np.ndarray, idx: int, dt: float) -> dict:
    """Half-max width around ``idx``; flags a start truncated by the record."""
    half = int(HALF_WIN_S / dt)
    lo0, hi0 = max(0, idx - half), min(len(a_g), idx + half)
    peak = a_g[idx]
    thr = abs(peak) / 2.0
    over = (np.sign(peak) * a_g) >= thr
    lo = idx
    while lo > lo0 and over[lo - 1]:
        lo -= 1
    hi = idx
    while hi < hi0 - 1 and over[hi + 1]:
        hi += 1
    dv = integrate.trapezoid(a_g[lo : hi + 1] * GRAVITY, t[lo : hi + 1])
    return {"peak_abs_g": float(abs(peak)), "t_peak_ms": float(t[idx] * 1e3),
            "pulse_width_ms": float((t[hi] - t[lo]) * 1e3),
            "delta_v_ms": float(abs(dv)),
            "start_truncated": bool(lo == 0 and over[0])}


def analyze_capture(sig_no: int, text: str) -> dict:
    ev = None
    for line in text.splitlines()[:TP4_HEADER_LINES]:
        if line.startswith("EventTime:"):
            ev = datetime.strptime(line.split(":", 1)[1].strip(), "%m/%d/%Y %I:%M:%S %p")
    d = np.genfromtxt(io.StringIO(text), skip_header=TP4_HEADER_LINES,
                      delimiter=",", usecols=(0, 1, 2, 3, 4))
    t, ch = d[:, 0], d[:, 1:5]
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt

    ch = ch - np.median(ch, axis=0)  # full-record median baseline (see module doc)
    top, ch5 = ch[:, TOP_COLS], ch[:, CH5]

    n_search = int(SEARCH_S / dt)
    ch5_180 = cfc_filter(ch5, fs, 180)
    ch5_1000 = cfc_filter(ch5, fs, 1000)
    i_imp = int(np.argmax(np.abs(ch5_180[:n_search])))
    m_ch5 = half_max_pulse(t, ch5_180, i_imp, dt)

    top180 = np.stack([cfc_filter(top[:, j], fs, 180) for j in range(3)], axis=1)
    res180 = resultant(top180)
    half = int(HALF_WIN_S / dt)
    lo, hi = max(0, i_imp - half), min(len(t), i_imp + half)
    i_top = lo + int(np.argmax(res180[lo:hi]))
    m_top = half_max_pulse(t, res180, i_top, dt)

    n_dv = int(DV_TOTAL_S / dt)
    v = integrate.cumulative_trapezoid(ch5_180[:n_dv] * GRAVITY, t[:n_dv], initial=0.0)
    dv_captured = float(np.max(np.abs(v)))
    # how much of the rise the trigger cut off: CFC-180 CH5 at t = 0 vs the peak
    onset_frac = float(abs(ch5_180[0]) / m_ch5["peak_abs_g"])

    sat = {}
    for name, col in [("CH2", 0), ("CH3", 1), ("CH4", 2), ("CH5", 3)]:
        pk = float(np.max(np.abs(ch[:, col])))
        sat[name] = {"peak_g": pk, "frac_fs": pk / FULL_SCALE_G[name]}

    # output spectrum: energy centroid of the tri-axis resultant over the impact
    seg = resultant(top)[max(0, i_imp - int(0.001 / dt)) : i_imp + int(0.008 / dt)]
    f, p = sig.welch(seg - seg.mean(), fs=fs, nperseg=min(4096, len(seg)))
    band = (f >= 100.0) & (f <= 20000.0)
    centroid = float(np.sum(f[band] * p[band]) / np.sum(p[band]))

    return {
        "signal": sig_no,
        "event_time": ev.isoformat(),
        "t_imp_ms": m_ch5["t_peak_ms"],
        "ch5_raw_g": float(np.max(np.abs(ch5))),
        "ch5_frac_fs": sat["CH5"]["frac_fs"],
        "ch5_1000_g": float(np.max(np.abs(ch5_1000[:n_search]))),
        "ch5_180_g": m_ch5["peak_abs_g"],
        "ch5_width_ms": m_ch5["pulse_width_ms"],
        "ch5_dv_pulse_ms": m_ch5["delta_v_ms"],
        "ch5_dv_captured_ms": dv_captured,
        "onset_frac": onset_frac,
        "start_truncated": m_ch5["start_truncated"],
        "top_180_g": m_top["peak_abs_g"],
        "top_width_ms": m_top["pulse_width_ms"],
        "top_centroid_hz": centroid,
        "t_ch5": m_top["peak_abs_g"] / m_ch5["peak_abs_g"],
        "sat": sat,
        "series": {
            "t_ms": (t[:n_dv:40] * 1e3).tolist(),
            "ch5_180_g": ch5_180[:n_dv:40].tolist(),
            "top_180_g": res180[:n_dv:40].tolist(),
            "v_ms": v[::40].tolist(),
        },
    }


def summarize(rows: list[dict], cfg: dict) -> dict:
    """Per-configuration aggregates, drift OLS and acceptance-criteria scoring."""
    n = len(rows)
    idx = np.arange(1, n + 1, dtype=float)
    agg, drift = {}, {}
    for key in ["ch5_raw_g", "ch5_180_g", "ch5_width_ms", "ch5_dv_captured_ms",
                "top_180_g", "top_width_ms", "top_centroid_hz", "t_ch5"]:
        a = arr(rows, key)
        agg[key] = {"mean": float(a.mean()), "sd": float(a.std(ddof=1)), "cv": cv(a),
                    "min": float(a.min()), "max": float(a.max())}
        drift[key] = ols_full(idx, a)

    raw = arr(rows, "ch5_raw_g")
    trig_margin = raw / cfg["trigger_g"]
    max_fs = float(arr(rows, "ch5_frac_fs").max())

    checks = {
        "headroom": {
            "criterion": f"CH5 raw |peak| <= FS/3 = {HEADROOM_TARGET_G:.0f} G",
            "value_g": float(raw.max()),
            "pass": bool(raw.max() <= HEADROOM_TARGET_G),
        },
        "input_severity": {
            "criterion": f"CH5 CFC-180 within +-20 % of the felt era "
                         f"({INPUT_BAND_G[0]:.0f}-{INPUT_BAND_G[1]:.0f} G)",
            "value_g": agg["ch5_180_g"]["mean"],
            "pass": bool(INPUT_BAND_G[0] <= agg["ch5_180_g"]["mean"] <= INPUT_BAND_G[1]),
        },
        "pulse_width": {
            "criterion": f"input pulse width {WIDTH_BAND_MS[0]}-{WIDTH_BAND_MS[1]} ms",
            "value_ms": agg["ch5_width_ms"]["mean"],
            "pass": bool(WIDTH_BAND_MS[0] <= agg["ch5_width_ms"]["mean"] <= WIDTH_BAND_MS[1]),
        },
        "output_repeatability": {
            "criterion": "TOP CFC-180 CV <= 2 %",
            "value_pct": agg["top_180_g"]["cv"],
            "pass": bool(agg["top_180_g"]["cv"] <= 2.0),
        },
        "t_repeatability": {
            "criterion": "T CV <= 2 %",
            "value_pct": agg["t_ch5"]["cv"],
            "pass": bool(agg["t_ch5"]["cv"] <= 2.0),
        },
        "trigger_margin": {
            "criterion": f"raw |peak| >= {TRIGGER_MARGIN_MIN:.0f}x the trigger level "
                         f"({cfg['trigger_g']:.0f} G)",
            "value_x": float(trig_margin.min()),
            "pass": bool(trig_margin.min() >= TRIGGER_MARGIN_MIN),
        },
        "stability": {
            "criterion": "|input drift| <= 0.5 %/drop over the 10 drops",
            "value_pct_per_drop": drift["ch5_180_g"]["slope_pct"],
            "pass": bool(abs(drift["ch5_180_g"]["slope_pct"]) <= 0.5),
        },
    }
    return {
        "key": cfg["key"], "label": cfg["label"], "trigger_g": cfg["trigger_g"],
        "n": n,
        "first_event": rows[0]["event_time"], "last_event": rows[-1]["event_time"],
        "aggregates": agg, "drift_ols": drift,
        "max_frac_fs": max_fs,
        "trigger_margin_min": float(trig_margin.min()),
        "trigger_margin_mean": float(trig_margin.mean()),
        "onset_frac_mean": float(arr(rows, "onset_frac").mean()),
        "checks": checks,
        "n_pass": int(sum(c["pass"] for c in checks.values())),
    }


def main() -> int:
    per_cfg, summaries = {}, {}
    for cfg in CONFIGS:
        rows = [analyze_capture(s, txt) for s, txt in load_captures(cfg["zip"])]
        per_cfg[cfg["key"]] = rows
        summaries[cfg["key"]] = summarize(rows, cfg)

        print(f"\n{'=' * 96}\n=== {cfg['short']} — {cfg['label']} "
              f"({len(rows)} drops, trigger {cfg['trigger_g']:.0f} G) ===\n{'=' * 96}")
        for r in rows:
            print(f"  S{r['signal']:<3d} t_imp {r['t_imp_ms']:5.2f} ms  "
                  f"CH5 raw {r['ch5_raw_g']:7.0f} G ({100 * r['ch5_frac_fs']:4.1f}% FS)  "
                  f"CFC-180 {r['ch5_180_g']:6.1f} G  w {r['ch5_width_ms']:5.2f} ms  "
                  f"dv_cap {r['ch5_dv_captured_ms']:5.2f} m/s  "
                  f"TOP {r['top_180_g']:6.1f} G  T {r['t_ch5']:.3f}")
        s = summaries[cfg["key"]]
        for key, label in [("ch5_raw_g", "CH5 raw (G)"), ("ch5_180_g", "CH5 CFC-180 (G)"),
                           ("ch5_width_ms", "input width (ms)"),
                           ("ch5_dv_captured_ms", "dv captured (m/s)"),
                           ("top_180_g", "TOP CFC-180 (G)"),
                           ("top_centroid_hz", "output centroid (Hz)"),
                           ("t_ch5", "T = TOP/CH5")]:
            a, o = s["aggregates"][key], s["drift_ols"][key]
            print(f"  {label:20s}: mean {a['mean']:9.3f}  sd {a['sd']:8.3f}  "
                  f"CV {a['cv']:5.2f}%   drift {o['slope_pct']:+7.3f}%/drop "
                  f"(p = {o['p']:.1e}, R² = {o['r2']:.2f})")
        print(f"  trigger margin: min {s['trigger_margin_min']:.1f}x  "
              f"mean {s['trigger_margin_mean']:.1f}x   |   "
              f"pulse onset cut by the trigger: {100 * s['onset_frac_mean']:.0f} % of peak "
              f"already present at t = 0")
        print(f"  acceptance checks: {s['n_pass']}/{len(s['checks'])} pass")
        for name, c in s["checks"].items():
            val = next(v for k, v in c.items() if k.startswith("value"))
            print(f"    [{'PASS' if c['pass'] else 'FAIL'}] {name:22s} {val:9.2f}   "
                  f"({c['criterion']})")

    # ---------------- cross-configuration comparison ---------------------
    print(f"\n{'=' * 96}\n=== cross-configuration comparison ===\n{'=' * 96}")
    hdr = (f"  {'config':22s} {'CH5 raw':>10s} {'%FS':>6s} {'input':>9s} {'CV':>6s} "
           f"{'width':>7s} {'TOP':>8s} {'CV':>6s} {'T':>7s} {'CV':>6s} {'trig':>6s} {'pass':>5s}")
    print(hdr)
    for cfg in CONFIGS:
        s = summaries[cfg["key"]]
        a = s["aggregates"]
        print(f"  {cfg['short']:22s} {a['ch5_raw_g']['mean']:10.0f} "
              f"{100 * s['max_frac_fs']:5.1f}% {a['ch5_180_g']['mean']:9.1f} "
              f"{a['ch5_180_g']['cv']:5.1f}% {a['ch5_width_ms']['mean']:6.2f}m "
              f"{a['top_180_g']['mean']:8.1f} {a['top_180_g']['cv']:5.1f}% "
              f"{a['t_ch5']['mean']:7.3f} {a['t_ch5']['cv']:5.2f}% "
              f"{s['trigger_margin_min']:5.1f}x {s['n_pass']:3d}/7")
    print(f"  {'felt + cardboard ref':22s} {FELT_REF['ch5_raw_g']:10.0f} "
          f"{100 * FELT_REF['ch5_raw_g'] / FULL_SCALE_G['CH5']:5.1f}% "
          f"{FELT_REF['ch5_180_g']:9.1f} {FELT_REF['ch5_180_cv']:5.1f}% "
          f"{FELT_REF['ch5_width_ms']:6.2f}m {FELT_REF['top_180_g']:8.1f} "
          f"{FELT_REF['top_180_cv']:5.1f}% {FELT_REF['t']:7.3f} {FELT_REF['t_cv']:5.2f}%")

    # pairwise Welch on T and on the input, all configurations
    pairwise = {}
    for i, ca in enumerate(CONFIGS):
        for cb in CONFIGS[i + 1:]:
            a, b = per_cfg[ca["key"]], per_cfg[cb["key"]]
            entry = {}
            for key in ["ch5_180_g", "top_180_g", "t_ch5"]:
                x, y = arr(a, key), arr(b, key)
                tt = stats.ttest_ind(x, y, equal_var=False)
                sp = np.sqrt((x.std(ddof=1) ** 2 + y.std(ddof=1) ** 2) / 2.0)
                entry[key] = {"a_mean": float(x.mean()), "b_mean": float(y.mean()),
                              "diff_pct": float(100 * (y.mean() - x.mean()) / x.mean()),
                              "p": float(tt.pvalue),
                              "d": float((y.mean() - x.mean()) / sp) if sp else float("nan")}
            pairwise[f"{ca['key']}_vs_{cb['key']}"] = entry
    print("\n  T = TOP/CH5, pairwise (Welch):")
    for name, e in pairwise.items():
        t = e["t_ch5"]
        print(f"    {name:38s} {t['a_mean']:.3f} -> {t['b_mean']:.3f}  "
              f"({t['diff_pct']:+5.1f}%)  p = {t['p']:.2e}  d = {t['d']:+6.2f}")

    # ---------------- reconcile the earlier bimodal PU A/B run -----------
    # docs/drop-test-pu-vs-felt-analysis.md reported a "stiff"/"soft" split in
    # the 5-drop PU run without knowing the sheet arrangement. Match each of
    # those drops to its nearest arrangement here, in (input, width) space.
    ab_path = DATA / "pu-vs-felt" / "figures" / "pu_vs_felt_metrics.json"
    reconciliation = None
    if ab_path.exists():
        ab = json.load(open(ab_path))["per_capture"]["pu"]
        centres = {c["key"]: (summaries[c["key"]]["aggregates"]["ch5_180_g"]["mean"],
                              summaries[c["key"]]["aggregates"]["ch5_width_ms"]["mean"])
                   for c in CONFIGS}
        print(f"\n{'=' * 96}\n=== reconciling the earlier 5-drop PU A/B run "
              f"(docs/drop-test-pu-vs-felt-analysis.md) ===\n{'=' * 96}")
        matches = []
        for r in ab:
            # normalised distance so the two axes weigh equally
            best = min(centres, key=lambda k: ((r["ch5_180_g"] - centres[k][0]) / centres[k][0]) ** 2
                       + ((r["ch5_width_ms"] - centres[k][1]) / centres[k][1]) ** 2)
            matches.append({"signal": r["signal"], "ch5_180_g": r["ch5_180_g"],
                            "ch5_width_ms": r["ch5_width_ms"], "t_ch5": r["t_ch5"],
                            "nearest_config": best})
            print(f"  A/B S{r['signal']}: {r['ch5_180_g']:6.1f} G / {r['ch5_width_ms']:.2f} ms "
                  f"(T = {r['t_ch5']:.3f})  ->  nearest arrangement: {best}")
        reconciliation = {"matches": matches,
                          "config_centres_g_ms": {k: list(v) for k, v in centres.items()}}

    # ---------------- figures ------------------------------------------
    # Fig 1: input + output pulse overlays, one panel per configuration
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 8.5), sharex=True)
    for ax, cfg in zip(axes.ravel(), CONFIGS):
        for r in per_cfg[cfg["key"]]:
            s = r["series"]
            ax.plot(s["t_ms"], s["ch5_180_g"], lw=1.0, color=cfg["color"], alpha=0.55)
            ax.plot(s["t_ms"], s["top_180_g"], lw=1.0, color="k", alpha=0.35)
        sm = summaries[cfg["key"]]
        ax.set(title=f"{cfg['short']} — {cfg['label']}\n"
                     f"input {sm['aggregates']['ch5_180_g']['mean']:.0f} G "
                     f"(CV {sm['aggregates']['ch5_180_g']['cv']:.1f} %), "
                     f"w = {sm['aggregates']['ch5_width_ms']['mean']:.2f} ms, "
                     f"T = {sm['aggregates']['t_ch5']['mean']:.3f}",
               xlabel="time from trigger (ms)", ylabel="CFC-180 (G)", xlim=(0, 8))
        ax.grid(alpha=0.3)
    axes[0, 0].plot([], [], color="tab:gray", lw=1.5, label="CH5 input")
    axes[0, 0].plot([], [], color="k", alpha=0.5, lw=1.5, label="TOP output (resultant)")
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("bpx68c: base-plate input and top-vertex output pulses, "
                 "four polyurethane arrangements (10 drops each)")
    fig.tight_layout()
    fig.savefig(FIG / "01_pulse_overlays.png", dpi=130)
    plt.close(fig)

    # Fig 2: input severity / head-room / width / T summary bars
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
    x = np.arange(len(CONFIGS))
    labels = [c["short"] for c in CONFIGS]
    colors = [c["color"] for c in CONFIGS]

    ax = axes[0, 0]
    vals = [summaries[c["key"]]["aggregates"]["ch5_180_g"]["mean"] for c in CONFIGS]
    errs = [summaries[c["key"]]["aggregates"]["ch5_180_g"]["sd"] for c in CONFIGS]
    ax.bar(x, vals, yerr=errs, capsize=4, color=colors, alpha=0.85)
    ax.axhspan(*INPUT_BAND_G, color="tab:green", alpha=0.12,
               label="felt-era severity ±20 %")
    ax.axhline(FELT_REF["ch5_180_g"], color="k", ls="--", lw=1.2, label="felt + cardboard")
    ax.axhline(PU_AB_REF["ch5_180_g"], color="tab:purple", ls=":", lw=1.4,
               label="earlier PU A/B run")
    ax.set(xticks=x, xticklabels=labels, ylabel="CH5 input CFC-180 (G)",
           title="input severity vs the felt-era operating point")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis="y")

    ax = axes[0, 1]
    vals = [100 * summaries[c["key"]]["max_frac_fs"] for c in CONFIGS]
    ax.bar(x, vals, color=colors, alpha=0.85)
    ax.axhline(100 / 3, color="k", ls=":", lw=1.4, label="FS/3 head-room target")
    ax.axhline(100 * FELT_REF["ch5_raw_g"] / FULL_SCALE_G["CH5"], color="tab:brown",
               ls="--", lw=1.2, label="felt + cardboard (fresh)")
    ax.set(xticks=x, xticklabels=labels,
           ylabel="worst CH5 raw |peak| (% of 9,443 G FS)",
           title="base-sensor head-room (worst drop)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis="y")

    ax = axes[1, 0]
    vals = [summaries[c["key"]]["aggregates"]["ch5_width_ms"]["mean"] for c in CONFIGS]
    errs = [summaries[c["key"]]["aggregates"]["ch5_width_ms"]["sd"] for c in CONFIGS]
    ax.bar(x, vals, yerr=errs, capsize=4, color=colors, alpha=0.85)
    ax.axhspan(*WIDTH_BAND_MS, color="tab:green", alpha=0.12, label="target 1–2.5 ms")
    ax.axhline(FELT_REF["ch5_width_ms"], color="k", ls="--", lw=1.2,
               label="felt + cardboard")
    ax.set(xticks=x, xticklabels=labels, ylabel="input half-max width (ms)",
           title="input pulse duration")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis="y")

    ax = axes[1, 1]
    for k, cfg in enumerate(CONFIGS):
        tv = arr(per_cfg[cfg["key"]], "t_ch5")
        ax.plot(np.full(len(tv), k) + np.linspace(-0.1, 0.1, len(tv)), tv, "o", ms=6,
                color=cfg["color"])
        ax.hlines(tv.mean(), k - 0.24, k + 0.24, color=cfg["color"], lw=2.5,
                  label=f"{cfg['short']}: {tv.mean():.3f} (CV {cv(tv):.2f} %)")
    ax.axhline(1.0, color="k", ls=":", lw=1.2)
    ax.axhline(FELT_REF["t"], color="tab:brown", ls="--", lw=1.2,
               label=f"felt + cardboard: {FELT_REF['t']:.3f}")
    ax.set(xticks=x, xticklabels=labels, ylabel="T = TOP/CH5 (CFC-180)",
           title="transmissibility per drop")
    ax.legend(fontsize=7.5)
    ax.grid(alpha=0.3, axis="y")

    fig.suptitle("bpx68c: polyurethane arrangement sweep vs the qualification criteria")
    fig.tight_layout()
    fig.savefig(FIG / "02_config_comparison.png", dpi=130)
    plt.close(fig)

    # Fig 3: within-configuration stability over the 10 drops
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    for cfg in CONFIGS:
        rows = per_cfg[cfg["key"]]
        n = np.arange(1, len(rows) + 1)
        axes[0].plot(n, 100 * arr(rows, "ch5_frac_fs"), "o-", ms=5, color=cfg["color"],
                     label=cfg["short"])
        axes[1].plot(n, arr(rows, "ch5_180_g"), "o-", ms=5, color=cfg["color"])
        axes[2].plot(n, arr(rows, "t_ch5"), "o-", ms=5, color=cfg["color"])
    axes[0].axhline(100 / 3, color="k", ls=":", lw=1.2)
    axes[0].set(xlabel="drop within configuration", ylabel="CH5 raw (% FS)",
                title="head-room drift")
    axes[1].set(xlabel="drop within configuration", ylabel="CH5 CFC-180 (G)",
                title="input severity drift")
    axes[2].axhline(1.0, color="k", ls=":", lw=1.2)
    axes[2].set(xlabel="drop within configuration", ylabel="T = TOP/CH5",
                title="transmissibility drift")
    axes[0].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.suptitle("bpx68c: within-configuration stability over 10 consecutive drops")
    fig.tight_layout()
    fig.savefig(FIG / "03_stability.png", dpi=130)
    plt.close(fig)

    # Fig 4: severity-duration map — where each arrangement (and the earlier
    # bimodal A/B run, and the felt stack) sits in (input peak, pulse width)
    fig, ax = plt.subplots(figsize=(9, 6))
    for cfg in CONFIGS:
        rows = per_cfg[cfg["key"]]
        ax.plot(arr(rows, "ch5_width_ms"), arr(rows, "ch5_180_g"), "o", ms=7,
                color=cfg["color"], label=f"{cfg['short']} ({cfg['label']})")
    ax.plot(FELT_REF["ch5_width_ms"], FELT_REF["ch5_180_g"], "k*", ms=18,
            label="4 felt + 1 cardboard (reference)")
    if reconciliation:
        m = reconciliation["matches"]
        ax.plot([r["ch5_width_ms"] for r in m], [r["ch5_180_g"] for r in m], "x",
                ms=11, mew=2.2, color="tab:purple",
                label="earlier PU A/B run (loose stack, 5 drops)")
    ax.axhspan(*INPUT_BAND_G, color="tab:green", alpha=0.10)
    ax.axvspan(*WIDTH_BAND_MS, color="tab:green", alpha=0.10)
    ax.set(xlabel="input half-max pulse width (ms)", ylabel="CH5 input CFC-180 (G)",
           title="severity–duration map: the 1/4 in sheet alone reproduces the felt shock\n"
                 "(green band = qualification target)")
    ax.legend(fontsize=8.5)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "04_severity_duration_map.png", dpi=130)
    plt.close(fig)

    # ---------------- machine-readable summary --------------------------
    strip = lambda rows: [{k: v for k, v in r.items() if k != "series"} for r in rows]
    payload = {
        "specimen": "bpx68c",
        "session_id": "bpx68c - Polyurethane Rubber - Further Tests",
        "date": "2026-07-30",
        "excluded": {"signal": 21, "reason": "stray capture between configs B and C "
                                             "(13:26), excluded per @me-madsen"},
        "criteria": {
            "headroom_g": HEADROOM_TARGET_G,
            "input_band_g": list(INPUT_BAND_G),
            "width_band_ms": list(WIDTH_BAND_MS),
            "trigger_margin_min": TRIGGER_MARGIN_MIN,
        },
        "references": {"felt": FELT_REF, "pu_ab_run": PU_AB_REF},
        "configs": summaries,
        "pairwise": pairwise,
        "ab_run_reconciliation": reconciliation,
        "per_capture": {k: strip(v) for k, v in per_cfg.items()},
    }
    with open(FIG / "pu_configs_metrics.json", "w") as fh:
        json.dump(payload, fh, indent=1)
    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
