#!/usr/bin/env python3
"""SOBOL + S0 BO-campaign batch analysis — one folder per specimen.

The optimization campaign (announced on PR #86, 08-19) runs every specimen
of the SOBOL + S0 batch through the standing SOP:

* 60 in drop, arrangement B (1/2 in PU mat, issue #88), 101 drops/specimen;
* capture: 4 channels (CH2-4 top-vertex tri-axis, CH5 base-plate input),
  1.25 MHz, 125,000 samples = 100 ms, 2 ms pre-trigger, 150 G trigger on
  CH5 — the settings verified after the 08-18 TP4 reset
  (``docs/drop-test-calibration-check-analysis.md``).

This script generalizes the per-session pipeline to N specimens so each
Box upload is one command to analyze.  Layout: ``--raw ROOT`` with one
subfolder per specimen session; the specimen ID is the first
whitespace-delimited token of the folder name, lowercased (per the SOP
note that T3 IDs are case-insensitive).  Captures may be loose
``*_Signal<k>.csv`` files or inside ``.zip`` archives (extracted to a temp
dir); TP4 series tables (no ``Signal`` in the name) are ignored.

Per drop it reuses ``analyze_capture`` from the abc123 blind-test pipeline
unchanged (SAE J211 CFC-180/1000 peaks, transmissibility T, pulse FWHM,
Δv, specimen-hop delay t_second, e_rebound, ringdown f_n/ζ).  Per
specimen it discards the SOP warm-up drops, drops invalid captures (raw
input below the trigger level — cf. abc123 Signal 12), and reports
stabilized mean/CV/OLS-drift for every campaign metric plus the Δv rig
health check (settled post-grease band vs the healthy-tower bar,
``docs/drop-test-speed-decay-analysis.md``).  Campaign level: one-way
ANOVA + pairwise Welch on T, a discrimination summary against the
print-to-print noise floor, figures, and two machine-readable outputs —
``figures/campaign_metrics.json`` (full) and
``figures/campaign_summary.csv`` (one row per specimen, for the BO loop).

Optionally ``--params params.json`` maps specimen ID -> design parameters;
entries are passed through into both outputs so the BO ingests
(parameters, objectives) pairs directly.

Standing T-drift watch (PR #86, comment 5401409218, 08-24): every run
screens each specimen's within-session T (CFC-180) series against the
historical 1/2 in mat envelope (16 sessions, ~1,300 stabilized drops:
|OLS slope| <= 0.051 %/drop, |first5-vs-last5| <= 2.2 % —
``data/drop-tests/r2d2-checkin/figures/t_drift_history.json``) and prints
a prominent warning + writes a ``t_drift_watch`` block and CSV columns
when a session breaks it.  Reference event: ``r2d2c2`` 08-24 stepped
+3.5 % (1.023 -> ~1.059 plateau), output-side (top-vertex peak rose while
the CH5 input fell), lead suspect wax/mount coupling re-seat.  A flagged
specimen's T mean is drift-contaminated — do not hand it to the BO
without resolving (plateau-only average, or re-seat + re-run).
"""
from __future__ import annotations

import argparse
import csv
import functools
import itertools
import json
import multiprocessing
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_abc123_blind_analysis import TRIGGER_LEVEL_G, analyze_capture  # noqa: E402
from drop_test_60in_5felts_analysis import DATA, GRAVITY  # noqa: E402

OUT_DEFAULT = DATA / "sobol-campaign"

WARMUP_DROPS = 2          # SOP: discard, settled-rig value (speed-decay §SOP)
PAUSE_S = 120.0           # inter-drop gap that marks an interruption
RING_R2_MIN = 0.85        # abc123 convention: below this, ζ is not a damping ratio

# Standing T-drift watch thresholds — just outside the historical 1/2 in mat
# envelope (t_drift_history.json: worst prior |slope| 0.051 %/drop, worst
# |end-to-end| 2.18 %; the r2d2c2 event sat at +0.253 %/drop, +3.50 %).
T_DRIFT_SLOPE_MAX = 0.06   # |%/drop| on stabilized T180, with slope_p < 0.01
T_DRIFT_E2E_MAX = 2.5      # |first-5 vs last-5 mean| in %

DROP_HEIGHT_M = 60 * 0.0254
V_FREEFALL = float(np.sqrt(2.0 * GRAVITY * DROP_HEIGHT_M))  # 5.468 m/s

# Δv references at this exact configuration (60 in, arrangement B).
HEALTHY_B_DV = (5.276, 5.347)   # abc123 healthy tower, 08-04
SETTLED_DV = (4.55, 4.66)       # post-grease settled state, 08-11/12
DV_LOW_FLAG = 4.40              # below the 08-10 pre-grease level: rig alarm

# stabilized aggregate + drift for each of these per-drop keys
METRIC_KEYS = ("t180", "t1000", "out_180_g", "out_1000_g", "in_180_g",
               "in_raw_g", "in_width_ms", "in_dv_ms", "t_second_ms",
               "e_rebound", "foot_ch5_g")
RING_KEYS = ("fn_hz", "zeta_pct")   # gated on ring_r2 >= RING_R2_MIN
CSV_FIELDS = ("t180", "t1000", "out_180_g", "in_180_g", "in_dv_ms",
              "t_second_ms", "e_rebound", "fn_hz", "zeta_pct")


def agg(vals) -> dict:
    y = np.asarray(vals, float)
    y = y[np.isfinite(y)]
    if len(y) < 2:
        return {"n": int(len(y)), "mean": float(y.mean()) if len(y) else None}
    x = np.arange(len(y), dtype=float)
    sl, _, r, p, _ = stats.linregress(x, y)
    return {"n": int(len(y)), "mean": float(y.mean()), "sd": float(y.std(ddof=1)),
            "cv_pct": float(100 * y.std(ddof=1) / y.mean()) if y.mean() else None,
            "slope_pct_per_drop": float(100 * sl / y.mean()) if y.mean() else None,
            "slope_p": float(p), "r2": float(r * r)}


def t_drift_watch(stab: list[dict], metrics: dict) -> dict:
    """Screen the stabilized T180 series against the historical drift envelope.

    Returns slope/end-to-end numbers, a ``flagged`` bool, and — when flagged —
    an input/output attribution (an output-side drift with a flat-or-falling
    input is the r2d2c2 mount-coupling signature; a common-mode drift would
    cancel in T and is rig/mat, not mount).
    """
    t = [r["t180"] for r in stab if np.isfinite(r.get("t180", np.nan))]
    if len(t) < 6:
        return {"flagged": False, "note": "too few drops to screen"}
    e2e = float(100 * (np.mean(t[-5:]) - np.mean(t[:5])) / np.mean(t[:5]))
    m = metrics["t180"]
    slope, p = m.get("slope_pct_per_drop"), m.get("slope_p")
    slope_hit = slope is not None and abs(slope) > T_DRIFT_SLOPE_MAX and p < 0.01
    flagged = bool(slope_hit or abs(e2e) > T_DRIFT_E2E_MAX)
    watch = {"flagged": flagged,
             "slope_pct_per_drop": slope, "slope_p": p,
             "end_to_end_pct": round(e2e, 2),
             "envelope": {"slope_max": T_DRIFT_SLOPE_MAX, "e2e_max": T_DRIFT_E2E_MAX}}
    if flagged:
        out_e2e = 100 * (np.mean([r["out_180_g"] for r in stab[-5:]])
                         / np.mean([r["out_180_g"] for r in stab[:5]]) - 1)
        in_e2e = 100 * (np.mean([r["in_180_g"] for r in stab[-5:]])
                        / np.mean([r["in_180_g"] for r in stab[:5]]) - 1)
        side = ("output-side (mount/coupling suspect — r2d2c2 signature)"
                if out_e2e - in_e2e > 0.5 * abs(e2e) and in_e2e < 1.0
                else "common-mode / input-side (rig or mat)")
        watch.update({"out_e2e_pct": round(float(out_e2e), 2),
                      "in_e2e_pct": round(float(in_e2e), 2), "attribution": side,
                      "note": "T mean is drift-contaminated; resolve before BO "
                              "hand-off (plateau-only average or re-seat + re-run)"})
    return watch


def find_captures(folder: Path, scratch: Path) -> list[Path]:
    """Loose Signal CSVs plus any inside zip archives, deduped by signal no."""
    files = {p.name: p for p in folder.rglob("*Signal*.csv")}
    for z in sorted(folder.rglob("*.zip")):
        with zipfile.ZipFile(z) as zf:
            for m in zf.namelist():
                base = Path(m).name
                if "Signal" in base and base.endswith(".csv") and base not in files:
                    dest = scratch / folder.name / base
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(zf.read(m))
                    files[base] = dest
    bysig = {}
    for p in files.values():
        try:
            sig_no = int(p.stem.split("Signal")[1])
        except (IndexError, ValueError):
            continue
        bysig.setdefault(sig_no, p)
    return [bysig[k] for k in sorted(bysig)]


def pauses(rows):
    et = [datetime.fromisoformat(r["event_time"]) for r in rows if r["event_time"]]
    return [{"after_drop": i + 1, "gap_min": float((b - a).total_seconds() / 60)}
            for i, (a, b) in enumerate(zip(et[:-1], et[1:]))
            if (b - a).total_seconds() > PAUSE_S]


def analyze_specimen(spec_id: str, folder: Path, scratch: Path, warmup: int,
                     procs: int = 1) -> dict:
    paths = find_captures(folder, scratch)
    if not paths:
        print(f"  !! no Signal CSVs under {folder} — skipped")
        return {}
    # Tail baseline: from 08-17 on, mat contact starts >2 ms before the 150 G
    # trigger, so the pre-trigger window is not a valid zero (see the
    # analyze_capture docstring).  Validated against the TP4 series tables.
    cap = functools.partial(analyze_capture, baseline="tail")
    if procs > 1:
        with multiprocessing.Pool(procs) as pool:
            rows = pool.map(cap, paths)
    else:
        rows = [cap(p) for p in paths]
    for r in rows:
        print(f"  S{r['signal']:3d}  in180 {r['in_180_g']:6.1f} G  "
              f"T {r['t180']:.3f}  dv {r['in_dv_ms']:.3f} m/s  "
              f"t_sec {r.get('t_second_ms', float('nan')):6.2f} ms", flush=True)

    valid = [r for r in rows if r["in_raw_g"] >= TRIGGER_LEVEL_G]
    invalid = [r["signal"] for r in rows if r["in_raw_g"] < TRIGGER_LEVEL_G]
    stab = valid[warmup:] if len(valid) > warmup + 2 else valid

    metrics = {k: agg([r[k] for r in stab]) for k in METRIC_KEYS}
    ring_ok = [r for r in stab if r.get("ring_r2", 0) >= RING_R2_MIN]
    for k in RING_KEYS:
        metrics[k] = agg([r[k] for r in ring_ok if k in r])
    metrics["ring_usable_frac"] = float(len(ring_ok) / len(stab)) if stab else None

    dv = metrics["in_dv_ms"]["mean"]
    first5 = float(np.mean([r["in_dv_ms"] for r in valid[:5]])) if valid else None
    health = ("healthy" if dv >= HEALTHY_B_DV[0] else
              "settled" if dv >= SETTLED_DV[0] - 0.05 else
              "low" if dv >= DV_LOW_FLAG else "alarm")
    worst_fs = {c: float(max(r["frac_fs"][c] for r in valid))
                for c in ("CH2", "CH3", "CH4", "CH5")} if valid else {}

    drift = t_drift_watch(stab, metrics)
    if drift["flagged"]:
        print(f"  ** T-DRIFT WATCH: {spec_id} breaks the historical envelope — "
              f"slope {drift['slope_pct_per_drop']:+.3f} %/drop, "
              f"end-to-end {drift['end_to_end_pct']:+.2f} % "
              f"[{drift.get('attribution', '')}]", flush=True)

    return {"folder": folder.name, "n_captures": len(rows),
            "n_valid": len(valid), "invalid_signals": invalid,
            "warmup_discarded": min(warmup, max(0, len(valid) - 3)),
            "pauses": pauses(valid),
            "event_first": valid[0]["event_time"] if valid else None,
            "event_last": valid[-1]["event_time"] if valid else None,
            "metrics": metrics,
            "dv_health": {"session_mean": dv, "first5_mean": first5,
                          "verdict": health,
                          "frac_freefall": float(dv / V_FREEFALL / 0.9761)
                          if dv else None},   # cal: healthy B2 = 97.6 % of ff
            "worst_frac_fs": worst_fs, "t_drift_watch": drift,
            "rows": stab, "all_rows": rows}


def campaign_stats(specs: dict, key: str = "t180") -> dict:
    groups = {s: [r[key] for r in d["rows"]] for s, d in specs.items() if d}
    if len(groups) < 2:
        return {}
    f, p = stats.f_oneway(*groups.values())
    pair = {}
    for a, b in itertools.combinations(sorted(groups), 2):
        t, pp = stats.ttest_ind(groups[a], groups[b], equal_var=False)
        ga, gb = np.asarray(groups[a]), np.asarray(groups[b])
        sp = np.sqrt((ga.var(ddof=1) + gb.var(ddof=1)) / 2)
        pair[f"{a} vs {b}"] = {
            "diff_pct": float(100 * (gb.mean() - ga.mean()) / ga.mean()),
            "p": float(pp), "d": float((gb.mean() - ga.mean()) / sp) if sp else None}
    means = {s: float(np.mean(v)) for s, v in groups.items()}
    spread = 100 * (max(means.values()) - min(means.values())) / np.mean(list(means.values()))
    within = float(np.median([100 * np.std(v, ddof=1) / np.mean(v)
                              for v in groups.values()]))
    return {"anova_F": float(f), "anova_p": float(p),
            "means": means, "spread_pct": float(spread),
            "median_within_cv_pct": within,
            "ranking": sorted(means, key=means.get), "pairwise": pair}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=OUT_DEFAULT / "raw",
                    help="root folder; one subfolder per specimen session")
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--warmup", type=int, default=WARMUP_DROPS)
    ap.add_argument("--params", type=Path, default=None,
                    help="optional JSON: specimen id -> design parameters")
    ap.add_argument("--procs", type=int, default=1,
                    help="worker processes per specimen (capture-level)")
    args = ap.parse_args()

    params = json.loads(args.params.read_text()) if args.params else {}
    params = {k.lower(): v for k, v in params.items()}

    folders = sorted(p for p in args.raw.iterdir() if p.is_dir())
    if not folders:
        sys.exit(f"no specimen subfolders under {args.raw} (fetch from Box first)")

    specs = {}
    with tempfile.TemporaryDirectory() as td:
        for folder in folders:
            spec_id = folder.name.split()[0].lower()
            print(f"== {spec_id}  ({folder.name})")
            specs[spec_id] = analyze_specimen(spec_id, folder, Path(td),
                                              args.warmup, args.procs)

    specs = {s: d for s, d in specs.items() if d}
    camp = {k: campaign_stats(specs, k) for k in ("t180", "t1000", "e_rebound")}

    fig_dir = args.out / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "config": "60 in, arrangement B (1/2 in PU mat), 150 G trigger, "
                  "100 ms / 1.25 MHz capture",
        "warmup_discarded_per_specimen": args.warmup,
        "v_freefall_ms": V_FREEFALL,
        "dv_references": {"healthy_B": HEALTHY_B_DV, "settled_post_grease": SETTLED_DV,
                          "alarm_below": DV_LOW_FLAG},
        "specimens": {s: {**{k: v for k, v in d.items() if k != "all_rows"},
                          "design_params": params.get(s)}
                      for s, d in specs.items()},
        "campaign": camp,
    }
    with open(fig_dir / "campaign_metrics.json", "w") as fh:
        json.dump(out, fh, indent=1)

    with open(fig_dir / "campaign_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        pkeys = sorted({k for v in params.values() for k in v}) if params else []
        w.writerow(["specimen", "n_valid", "dv_health"]
                   + [f"{k}_{s}" for k in CSV_FIELDS for s in ("mean", "sd")]
                   + ["t_drift_flag", "t180_slope_pct_per_drop", "t180_e2e_pct"]
                   + pkeys)
        for s, d in specs.items():
            row = [s, d["n_valid"], d["dv_health"]["verdict"]]
            for k in CSV_FIELDS:
                m = d["metrics"][k]
                row += [m.get("mean"), m.get("sd")]
            dw = d["t_drift_watch"]
            row += [dw["flagged"], dw.get("slope_pct_per_drop"),
                    dw.get("end_to_end_pct")]
            row += [(params.get(s) or {}).get(k) for k in pkeys]
            w.writerow(row)

    for s, d in specs.items():
        m, dv = d["metrics"], d["dv_health"]
        print(f"{s}: n {d['n_valid']}/{d['n_captures']}  "
              f"T180 {m['t180']['mean']:.4f} (CV {m['t180']['cv_pct']:.2f} %)  "
              f"e_reb {m['e_rebound']['mean']:.4f}  "
              f"dv {dv['session_mean']:.3f} m/s [{dv['verdict']}]")
    if camp["t180"]:
        c = camp["t180"]
        print(f"campaign T180: spread {c['spread_pct']:.2f} % across "
              f"{len(c['means'])} specimens, ANOVA p = {c['anova_p']:.2e}, "
              f"ranking (best first) {c['ranking']}")
    flagged = [s for s, d in specs.items() if d["t_drift_watch"]["flagged"]]
    if flagged:
        print(f"** T-DRIFT WATCH: {flagged} exceeded the historical "
              f"within-session envelope (|slope| > {T_DRIFT_SLOPE_MAX} %/drop or "
              f"|end-to-end| > {T_DRIFT_E2E_MAX} %) — report these prominently; "
              f"their T means need resolution before BO hand-off")
    else:
        print("T-drift watch: no session outside the historical envelope "
              "(r2d2c2-style drift did not recur)")

    make_figures(specs, camp, fig_dir)
    print(f"figures + metrics under {fig_dir}")


def make_figures(specs, camp, fig_dir):
    ids = sorted(specs)
    cmap = plt.get_cmap("tab10")
    colors = {s: cmap(i % 10) for i, s in enumerate(ids)}

    # -- 01: per-drop T series per specimen --------------------------------
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True)
    for s in ids:
        rows = specs[s]["rows"]
        x = np.arange(1, len(rows) + 1)
        axes[0].plot(x, [r["t180"] for r in rows], "o-", ms=2.5, lw=0.7,
                     color=colors[s], label=s)
        axes[1].plot(x, [r["in_dv_ms"] for r in rows], "o-", ms=2.5, lw=0.7,
                     color=colors[s])
    axes[0].set_ylabel("T = TOP/CH5 (CFC-180)")
    axes[0].set_title("Stabilized drops per specimen (warm-up discarded)")
    axes[0].legend(fontsize=8, ncol=min(5, len(ids)))
    axes[1].axhspan(*HEALTHY_B_DV, color="tab:green", alpha=0.15, lw=0)
    axes[1].axhspan(*SETTLED_DV, color="tab:olive", alpha=0.15, lw=0)
    axes[1].set_ylabel("input Δv (m/s)")
    axes[1].set_xlabel("stabilized drop number")
    for ax in axes:
        ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(fig_dir / "01_campaign_series.png", dpi=150)
    plt.close(fig)

    # -- 02: ranking with distributions ------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8))
    panels = [("t180", "T = TOP/CH5 (CFC-180)"),
              ("t1000", "T (CFC-1000)"),
              ("e_rebound", "e_rebound = g·t_second/(2·Δv)")]
    for ax, (key, ylab) in zip(axes, panels):
        data = [[r[key] for r in specs[s]["rows"] if np.isfinite(r.get(key, np.nan))]
                for s in ids]
        bp = ax.boxplot(data, tick_labels=ids, patch_artist=True, widths=0.6,
                        medianprops={"color": "k"})
        for patch, s in zip(bp["boxes"], ids):
            patch.set_facecolor(colors[s])
            patch.set_alpha(0.5)
        ax.set_ylabel(ylab, fontsize=9)
        ax.grid(alpha=0.25, axis="y")
        ax.tick_params(axis="x", rotation=45, labelsize=8)
    if camp.get("t180"):
        axes[0].set_title(f"ANOVA p = {camp['t180']['anova_p']:.1e}, "
                          f"spread {camp['t180']['spread_pct']:.1f} %", fontsize=9)
    fig.suptitle("SOBOL + S0 campaign — specimen comparison (stabilized drops)")
    fig.tight_layout()
    fig.savefig(fig_dir / "02_campaign_ranking.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
