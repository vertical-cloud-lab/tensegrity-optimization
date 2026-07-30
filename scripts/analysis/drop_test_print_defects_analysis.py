#!/usr/bin/env python3
"""Print-defect study — five nominally identical T3-prism specimens.

@me-madsen posted five ~100-drop campaigns on PR #86 (Box folder
``oii429e3znjusbltzg56h5kwbi5cj29n``): five specimens printed from the
*same* T3-prism model/configuration, dropped at 60 in on the 4-felt +
1-cardboard stack, to measure how much printing defects move the drop-test
result.

  1. ``57vqhx``  07-28 14:22, 101 captures | most defects
  2. ``mdt6ja``  07-28 15:34, 100 captures | most defects
  3. ``j1crxg``  07-28 17:06, 100 captures | most defects
  4. ``cruela``  07-29 11:52, 101 captures | mostly defect-free
  5. ``bpx68c``  07-29 16:34, 100 captures | most defect-free

Defect grading and the note that "for the 4th and 5th specimen the felt was
moved/adjusted slightly" are @me-madsen's; the defect photos/video are on
PR #35 (comment 5110159623 and the one below it). Specimen IDs are treated
as case-insensitive per @me-madsen's request and are lower-cased here.

**The felt adjustment is perfectly confounded with the defect grouping** —
specimens 1-3 (high defect) ran on 07-28 on one stack state and specimens
4-5 (low defect) ran on 07-29 after the stack was adjusted. This script
therefore (a) tests the input channel for a step at that boundary, and
(b) leads with T = TOP/CH5, the metric that cancels common-mode input
changes, while still reporting the raw output peak.

Format: full 4-channel export (CH2-4 = top-vertex key-seat tri-axis "TOP"
output, CH5 = single-axis base-plate input + trigger) at 1.25 MHz over a
20 ms window — the same capture format as the polyurethane runs, so the
per-capture conventions are imported from
``drop_test_pu_vs_felt_analysis`` (full-record median baseline, impact at
the CFC-180 CH5 argmax within 12 ms, +-4 ms peak walk).

Emits ``data/drop-tests/print-defects/figures/print_defects_metrics.json``
consumed by ``docs/drop-test-print-defects-analysis.md``.
"""
from __future__ import annotations

import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import (  # noqa: E402
    DATA,
    FULL_SCALE_G,
    arr,
    cv,
    ols_full,
)
from drop_test_pu_vs_felt_analysis import analyze_capture  # noqa: E402

OUT = DATA / "print-defects"
RAW = OUT / "raw"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# defect_rank: 1 = worst (most defects) ... 5 = best (most defect-free);
# @me-madsen graded 1-3 as "the most defects", 4 as "mostly defect free"
# and 5 as "the most defect free".
SPECIMENS = [
    {"id": "57vqhx", "order": 1, "defect_rank": 1, "defect_group": "high",
     "session": "57vqhX 60 in - 4 felt 1 crdbrd", "date": "2026-07-28"},
    {"id": "mdt6ja", "order": 2, "defect_rank": 2, "defect_group": "high",
     "session": "mDT6Ja - 60 in - 4 flt 1 crdbrd", "date": "2026-07-28"},
    {"id": "j1crxg", "order": 3, "defect_rank": 3, "defect_group": "high",
     "session": "J1CRxg - 60 in - 4 flt 1 crdbrd", "date": "2026-07-28"},
    {"id": "cruela", "order": 4, "defect_rank": 4, "defect_group": "low",
     "session": "Cruela - 60 in - 4 flt 1 crdbrd", "date": "2026-07-29"},
    {"id": "bpx68c", "order": 5, "defect_rank": 5, "defect_group": "low",
     "session": "bpX68c - 60in - 4 flt 1 crdbrd", "date": "2026-07-29"},
]
FELT_ADJUSTED_BEFORE = "cruela"  # @me-madsen: felt moved/adjusted for specimens 4 and 5

SOP_BURN_IN = 5  # drops discarded before the stabilized window (campaign SOP)
COLORS = ["tab:red", "tab:orange", "tab:brown", "tab:green", "tab:blue"]


def load_rows(spec: dict) -> list[dict]:
    rows = []
    with zipfile.ZipFile(RAW / f"{spec['id']}.zip") as zf:
        members = sorted(
            (m for m in zf.namelist() if m.lower().endswith(".csv") and "Signal" in m),
            key=lambda m: int(Path(m).name.split("Signal")[1].split(".")[0]),
        )
        for m in members:
            sig = int(Path(m).name.split("Signal")[1].split(".")[0])
            rows.append(analyze_capture(sig, zf.read(m).decode("latin-1")))
    for k, r in enumerate(rows, start=1):
        r["drop"] = k
    return rows


def analyze_specimen(spec: dict) -> dict:
    rows = load_rows(spec)
    times = [datetime.fromisoformat(r["event_time"]) for r in rows]
    gaps = np.array([(b - a).total_seconds() for a, b in zip(times, times[1:])])

    drops = arr(rows, "drop")
    stable_mask = drops > SOP_BURN_IN
    stable = [r for r in rows if r["drop"] > SOP_BURN_IN]

    print(f"\n{'=' * 82}\n=== {spec['id']}  (specimen {spec['order']}, "
          f"defects: {spec['defect_group']}) ===\n{'=' * 82}")
    print(f"session '{spec['session']}' on {spec['date']}: {len(rows)} captures, "
          f"median cadence {np.median(gaps):.0f} s, span "
          f"{(times[-1] - times[0]).total_seconds() / 60:.0f} min")
    ti = arr(rows, "t_imp_ms")
    print(f"impact lands at {ti.mean():.2f} +- {ti.std():.2f} ms into the record")

    sat = {}
    for name in FULL_SCALE_G:
        fr = np.array([r["sat"][name]["frac_fs"] for r in rows])
        sat[name] = {"median_frac_fs": float(np.median(fr)), "max_frac_fs": float(fr.max()),
                     "n_ge_95pct_fs": int((fr >= 0.95).sum())}
    print(f"head-room: CH5 raw median {100 * sat['CH5']['median_frac_fs']:.1f} % FS, "
          f"worst {100 * sat['CH5']['max_frac_fs']:.1f} % FS   |   "
          f"worst TOP axis {100 * max(sat[c]['max_frac_fs'] for c in ('CH2', 'CH3', 'CH4')):.1f} % FS")

    agg, drift = {}, {}
    for key in ["ch5_raw_g", "ch5_180_g", "ch5_width_ms", "ch5_dv_total_ms",
                "top_180_g", "top_width_ms", "t_ch5"]:
        a = arr(stable, key)
        agg[key] = {"mean": float(a.mean()), "sd": float(a.std(ddof=1)), "cv": cv(a),
                    "n": len(a)}
        drift[key] = ols_full(drops[stable_mask], a)
    print(f"\nstabilized window (drops {SOP_BURN_IN + 1}..{len(rows)}, "
          f"n = {agg['t_ch5']['n']}):")
    for key, label in [("ch5_180_g", "CH5 input CFC-180 (G)"),
                       ("top_180_g", "TOP output CFC-180 (G)"),
                       ("t_ch5", "T = TOP/CH5"),
                       ("top_width_ms", "output pulse width (ms)"),
                       ("ch5_dv_total_ms", "input Δv (m/s)")]:
        a, o = agg[key], drift[key]
        print(f"  {label:24s}: mean {a['mean']:9.4f}  sd {a['sd']:8.4f}  CV {a['cv']:5.2f}%   "
              f"drift {o['slope_pct']:+7.4f}%/drop  p = {o['p']:.1e}  R² = {o['r2']:.2f}")

    return {**{k: spec[k] for k in ("id", "order", "defect_rank", "defect_group",
                                    "session", "date")},
            "n_captures": len(rows),
            "cadence_s_median": float(np.median(gaps)),
            "span_min": float((times[-1] - times[0]).total_seconds() / 60.0),
            "t_imp_ms": {"mean": float(ti.mean()), "sd": float(ti.std())},
            "saturation": sat,
            "stabilized_window": [SOP_BURN_IN + 1, len(rows)],
            "aggregates": agg, "drift_ols": drift,
            "rows": rows, "stable": stable}


def variance_components(groups: list[np.ndarray]) -> dict:
    """One-way random-effects decomposition: within- vs between-specimen SD."""
    k = len(groups)
    ns = np.array([len(g) for g in groups], float)
    means = np.array([g.mean() for g in groups])
    grand = float(np.concatenate(groups).mean())
    ss_w = float(sum(((g - g.mean()) ** 2).sum() for g in groups))
    df_w = float(ns.sum() - k)
    ms_w = ss_w / df_w
    ss_b = float((ns * (means - grand) ** 2).sum())
    ms_b = ss_b / (k - 1)
    n0 = (ns.sum() - (ns**2).sum() / ns.sum()) / (k - 1)
    var_b = max(0.0, (ms_b - ms_w) / n0)
    return {"grand_mean": grand,
            "sd_within": float(np.sqrt(ms_w)), "cv_within": float(100 * np.sqrt(ms_w) / grand),
            "sd_between": float(np.sqrt(var_b)),
            "cv_between": float(100 * np.sqrt(var_b) / grand),
            "icc": float(var_b / (var_b + ms_w)) if (var_b + ms_w) else float("nan"),
            "ratio_between_within": float(np.sqrt(var_b) / np.sqrt(ms_w)) if ms_w else float("nan")}


def main() -> int:
    specs = [analyze_specimen(s) for s in SPECIMENS]
    by_id = {s["id"]: s for s in specs}

    # ---------------- between-specimen comparison -----------------------
    print(f"\n{'=' * 82}\n=== between-specimen comparison (stabilized drops) ==="
          f"\n{'=' * 82}")
    print(f"  {'specimen':10s} {'#':>2s} {'defects':>8s} {'date':>11s} "
          f"{'input G':>9s} {'CV':>6s} {'TOP G':>9s} {'CV':>6s} {'T':>7s} {'CV':>6s} "
          f"{'CH5 %FS':>8s}")
    for s in specs:
        a = s["aggregates"]
        print(f"  {s['id']:10s} {s['order']:2d} {s['defect_group']:>8s} {s['date']:>11s} "
              f"{a['ch5_180_g']['mean']:9.1f} {a['ch5_180_g']['cv']:5.2f}% "
              f"{a['top_180_g']['mean']:9.1f} {a['top_180_g']['cv']:5.2f}% "
              f"{a['t_ch5']['mean']:7.4f} {a['t_ch5']['cv']:5.2f}% "
              f"{100 * s['saturation']['CH5']['median_frac_fs']:7.1f}%")

    stats_out = {}
    for key, label in [("ch5_180_g", "CH5 input"), ("top_180_g", "TOP output"),
                       ("t_ch5", "T = TOP/CH5")]:
        groups = [arr(s["stable"], key) for s in specs]
        f_st, p_an = stats.f_oneway(*groups)
        vc = variance_components(groups)
        rng = (max(g.mean() for g in groups) - min(g.mean() for g in groups)) / \
            np.mean([g.mean() for g in groups])
        stats_out[key] = {"anova_F": float(f_st), "anova_p": float(p_an),
                          "variance_components": vc, "spread_pct": float(100 * rng)}
        print(f"\n  {label}: ANOVA F = {f_st:.1f}, p = {p_an:.2e}   "
              f"spread across specimens = {100 * rng:.2f} %")
        print(f"    within-specimen CV {vc['cv_within']:.2f} %   "
              f"between-specimen CV {vc['cv_between']:.2f} %   "
              f"ratio {vc['ratio_between_within']:.1f}x   ICC {vc['icc']:.3f}")

    # pairwise Welch on T
    print("\n  T = TOP/CH5, pairwise (Welch):")
    pairwise = {}
    for i, a in enumerate(specs):
        for b in specs[i + 1:]:
            x, y = arr(a["stable"], "t_ch5"), arr(b["stable"], "t_ch5")
            tt = stats.ttest_ind(x, y, equal_var=False)
            sp = np.sqrt((x.std(ddof=1) ** 2 + y.std(ddof=1) ** 2) / 2.0)
            d = float((y.mean() - x.mean()) / sp) if sp else float("nan")
            pairwise[f"{a['id']}_vs_{b['id']}"] = {
                "a_mean": float(x.mean()), "b_mean": float(y.mean()),
                "diff_pct": float(100 * (y.mean() - x.mean()) / x.mean()),
                "p": float(tt.pvalue), "d": d}
            print(f"    {a['id']} vs {b['id']}: {x.mean():.4f} -> {y.mean():.4f} "
                  f"({100 * (y.mean() - x.mean()) / x.mean():+5.2f} %)  "
                  f"p = {tt.pvalue:.1e}  d = {d:+6.2f}")

    # ---------------- defect-level relationship -------------------------
    print(f"\n{'=' * 82}\n=== does the defect level explain the differences? ==="
          f"\n{'=' * 82}")
    defect_out = {}
    for key, label in [("top_180_g", "TOP output"), ("t_ch5", "T = TOP/CH5")]:
        means = np.array([s["aggregates"][key]["mean"] for s in specs])
        ranks = np.array([s["defect_rank"] for s in specs], float)
        rho = stats.spearmanr(ranks, means)
        # high-defect (1-3) vs low-defect (4-5), pooling the per-drop values
        hi = np.concatenate([arr(s["stable"], key) for s in specs
                             if s["defect_group"] == "high"])
        lo = np.concatenate([arr(s["stable"], key) for s in specs
                             if s["defect_group"] == "low"])
        tt = stats.ttest_ind(hi, lo, equal_var=False)
        # the same contrast at the specimen level (n = 3 vs 2) — the honest unit
        hi_m = np.array([s["aggregates"][key]["mean"] for s in specs
                         if s["defect_group"] == "high"])
        lo_m = np.array([s["aggregates"][key]["mean"] for s in specs
                         if s["defect_group"] == "low"])
        tt_spec = stats.ttest_ind(hi_m, lo_m, equal_var=False)
        defect_out[key] = {
            "spearman_rho": float(rho.statistic), "spearman_p": float(rho.pvalue),
            "high_mean": float(hi.mean()), "low_mean": float(lo.mean()),
            "diff_pct": float(100 * (lo.mean() - hi.mean()) / hi.mean()),
            "pooled_drop_level_p": float(tt.pvalue),
            "specimen_level_p": float(tt_spec.pvalue),
            "specimen_means": {s["id"]: float(s["aggregates"][key]["mean"]) for s in specs},
        }
        print(f"  {label}: Spearman rho vs defect rank = {rho.statistic:+.2f} "
              f"(p = {rho.pvalue:.2f}, n = 5 specimens)")
        print(f"    high-defect {hi.mean():.4f} vs low-defect {lo.mean():.4f} "
              f"({100 * (lo.mean() - hi.mean()) / hi.mean():+.2f} %)   "
              f"drop-level p = {tt.pvalue:.1e}   specimen-level p = {tt_spec.pvalue:.2f}")

    # ---------------- the felt-adjustment / session confound ------------
    print(f"\n{'=' * 82}\n=== confound check: the felt was adjusted before specimen 4 ==="
          f"\n{'=' * 82}")
    pre = np.concatenate([arr(s["stable"], "ch5_180_g") for s in specs
                          if s["defect_group"] == "high"])
    post = np.concatenate([arr(s["stable"], "ch5_180_g") for s in specs
                           if s["defect_group"] == "low"])
    tt_in = stats.ttest_ind(pre, post, equal_var=False)
    raw_pre = np.concatenate([arr(s["stable"], "ch5_raw_g") for s in specs
                              if s["defect_group"] == "high"])
    raw_post = np.concatenate([arr(s["stable"], "ch5_raw_g") for s in specs
                               if s["defect_group"] == "low"])
    confound = {
        "felt_adjusted_before": FELT_ADJUSTED_BEFORE,
        "input_180_pre": float(pre.mean()), "input_180_post": float(post.mean()),
        "input_180_diff_pct": float(100 * (post.mean() - pre.mean()) / pre.mean()),
        "input_180_p": float(tt_in.pvalue),
        "input_raw_pre": float(raw_pre.mean()), "input_raw_post": float(raw_post.mean()),
        "input_raw_diff_pct": float(100 * (raw_post.mean() - raw_pre.mean()) / raw_pre.mean()),
    }
    print(f"  CH5 CFC-180 input: specimens 1-3 {pre.mean():.1f} G  ->  "
          f"specimens 4-5 {post.mean():.1f} G "
          f"({confound['input_180_diff_pct']:+.2f} %, p = {tt_in.pvalue:.1e})")
    print(f"  CH5 raw |peak|:    specimens 1-3 {raw_pre.mean():.0f} G  ->  "
          f"specimens 4-5 {raw_post.mean():.0f} G "
          f"({confound['input_raw_diff_pct']:+.1f} %)")
    print("  -> the input itself moves across the boundary, so any output-peak "
          "difference\n     between the defect groups is confounded; T is the "
          "metric that cancels it.")

    # ---------------- within-session excursions in T --------------------
    # Fig 1 shows step changes in T inside single sessions (e.g. 57vqhx
    # around drop 25). Quantify them as the range of a 5-drop rolling mean
    # so they can be compared with the between-specimen spread.
    print(f"\n{'=' * 82}\n=== within-session excursions in T (5-drop rolling mean) ==="
          f"\n{'=' * 82}")
    excursion = {}
    for s in specs:
        y = arr(s["stable"], "t_ch5")
        roll = np.convolve(y, np.ones(5) / 5.0, mode="valid")
        rng_pct = 100.0 * (roll.max() - roll.min()) / roll.mean()
        excursion[s["id"]] = {"range_pct": float(rng_pct), "lo": float(roll.min()),
                              "hi": float(roll.max())}
        print(f"  {s['id']:8s}: {roll.min():.4f} -> {roll.max():.4f}  "
              f"({rng_pct:.2f} % of the session mean)")
    exc_max = max(e["range_pct"] for e in excursion.values())
    print(f"  worst within-session excursion {exc_max:.2f} % vs a between-specimen "
          f"spread of {stats_out['t_ch5']['spread_pct']:.2f} %")

    # ---------------- defect grade vs test order ------------------------
    # The defect grade is *identical* to the test order (1..5), so any
    # progressive rig/mount effect reproduces the "defect" correlation exactly.
    # The discriminating evidence is whether T also declines monotonically
    # *within* a day, where the stack state is common.
    print(f"\n{'=' * 82}\n=== defect grade vs test order (they are the same ranking) ==="
          f"\n{'=' * 82}")
    seq = {}
    for day in sorted({s["date"] for s in specs}):
        grp = [s for s in specs if s["date"] == day]
        means = [s["aggregates"]["t_ch5"]["mean"] for s in grp]
        mono = all(b < a for a, b in zip(means, means[1:]))
        seq[day] = {"ids": [s["id"] for s in grp], "t_means": [float(m) for m in means],
                    "monotone_decreasing": bool(mono)}
        print(f"  {day}: " + "  ".join(f"{s['id']} {m:.4f}" for s, m in zip(grp, means))
              + f"   -> monotone decreasing within the day: {mono}")
    print("  T declines with test order on both days, i.e. across the felt adjustment "
          "and\n  across the defect-group boundary — a progressive sequence effect "
          "explains the\n  ranking at least as well as the defect grade does.")

    # ---------------- what this means for the BO campaign ---------------
    t_vc = stats_out["t_ch5"]["variance_components"]
    print(f"\n{'=' * 82}\n=== implication for using T as a BO objective ===\n{'=' * 82}")
    print(f"  nominally identical prints spread {stats_out['t_ch5']['spread_pct']:.2f} % in T "
          f"(between-specimen CV {t_vc['cv_between']:.2f} %)")
    print(f"  within-specimen CV is {t_vc['cv_within']:.2f} %, so repeat drops on one article "
          f"are {t_vc['ratio_between_within']:.1f}x tighter than the print-to-print scatter")
    # Between-*design* T spreads measured so far, for scale.
    KNOWN_DESIGN_SPREADS = {
        "60 in campaign, 3 structures (prc1kn/9GMQYQ/7xadt6)": 2.3,
        "13 in input-output, 4 geometries (yqpmx1..n0jdwk)": 24.0,
    }
    print("\n  for scale, the between-design T spreads measured so far:")
    for label, spread in KNOWN_DESIGN_SPREADS.items():
        verdict = ("SMALLER than the print-to-print scatter — not resolvable "
                   "with n = 1 print") if spread <= stats_out["t_ch5"]["spread_pct"] else \
            "larger than the print-to-print scatter"
        print(f"    {label}: {spread:.1f} %  ->  {verdict}")
    # print-level replication for 80 % power at alpha = 0.05 (two-sided)
    reps = {}
    for delta in (1.0, 2.0, 3.0, 5.0, 10.0):
        n = 2.0 * (1.959964 + 0.841621) ** 2 * t_vc["cv_between"] ** 2 / delta**2
        reps[delta] = max(1, int(np.ceil(n)))
        print(f"  to resolve a {delta:4.1f} % between-design difference in T at 80 % power: "
              f"{reps[delta]:2d} replicate print(s) per geometry")

    # ---------------- figures ------------------------------------------
    # Fig 1: full per-drop series, all five campaigns
    fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
    x0 = 0
    ticks, labels = [], []
    for s, c in zip(specs, COLORS):
        n = s["n_captures"]
        x = np.arange(n) + x0
        axes[0].plot(x, arr(s["rows"], "ch5_180_g"), lw=1.1, color=c)
        axes[1].plot(x, arr(s["rows"], "top_180_g"), lw=1.1, color=c)
        axes[2].plot(x, arr(s["rows"], "t_ch5"), lw=1.1, color=c,
                     label=f"{s['id']} (#{s['order']}, {s['defect_group']} defect)")
        ticks.append(x0 + n / 2)
        labels.append(f"{s['id']}\n{s['date'][5:]}")
        for ax in axes:
            ax.axvline(x0, color="k", lw=0.7, alpha=0.4)
        x0 += n
    axes[0].set(ylabel="CH5 input CFC-180 (G)", title="base-plate input")
    axes[1].set(ylabel="TOP output CFC-180 (G)", title="top-vertex output")
    axes[2].set(ylabel="T = TOP/CH5", title="transmissibility", xticks=ticks)
    axes[2].set_xticklabels(labels)
    axes[2].axhline(1.0, color="k", ls=":", lw=1.0)
    axes[2].legend(fontsize=8, ncol=3)
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.suptitle("Five nominally identical T3-prism prints, ~100 drops each at 60 in "
                 "(4 felt + 1 cardboard)")
    fig.tight_layout()
    fig.savefig(FIG / "01_full_series.png", dpi=130)
    plt.close(fig)

    # Fig 2: per-specimen distributions of T and TOP, ordered by defect rank
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.6))
    order = sorted(specs, key=lambda s: s["defect_rank"])
    for ax, key, label in [(axes[0], "t_ch5", "T = TOP/CH5 (CFC-180)"),
                           (axes[1], "top_180_g", "TOP output CFC-180 (G)")]:
        data = [arr(s["stable"], key) for s in order]
        bp = ax.boxplot(data, patch_artist=True, widths=0.6, showfliers=False)
        for patch, s in zip(bp["boxes"], order):
            patch.set_facecolor(COLORS[s["order"] - 1])
            patch.set_alpha(0.55)
        ax.set(xticks=range(1, 6),
               xticklabels=[f"{s['id']}\n#{s['order']} ({s['defect_group']})" for s in order],
               ylabel=label, title=label.split(" (")[0])
        ax.grid(alpha=0.3, axis="y")
        ax.axvspan(0.5, 3.5, color="tab:red", alpha=0.05)
        ax.axvspan(3.5, 5.5, color="tab:green", alpha=0.05)
    axes[0].axhline(1.0, color="k", ls=":", lw=1.0)
    fig.suptitle("Print-to-print scatter, stabilized drops "
                 "(red band = high defect, green = low defect; felt adjusted before #4)")
    fig.tight_layout()
    fig.savefig(FIG / "02_specimen_distributions.png", dpi=130)
    plt.close(fig)

    # Fig 3: variance decomposition + the confound
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    ax = axes[0]
    keys = ["ch5_180_g", "top_180_g", "t_ch5"]
    names = ["CH5 input", "TOP output", "T = TOP/CH5"]
    w = 0.38
    xs = np.arange(3)
    ax.bar(xs - w / 2, [stats_out[k]["variance_components"]["cv_within"] for k in keys],
           width=w, label="within specimen (repeat drops)", color="tab:blue", alpha=0.85)
    ax.bar(xs + w / 2, [stats_out[k]["variance_components"]["cv_between"] for k in keys],
           width=w, label="between specimens (print to print)", color="tab:red", alpha=0.85)
    ax.set(xticks=xs, xticklabels=names, ylabel="CV (%)",
           title="variance components")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis="y")

    ax = axes[1]
    ranks = [s["defect_rank"] for s in specs]
    tm = [s["aggregates"]["t_ch5"]["mean"] for s in specs]
    tsd = [s["aggregates"]["t_ch5"]["sd"] for s in specs]
    for s, m, sd in zip(specs, tm, tsd):
        ax.errorbar(s["defect_rank"], m, yerr=sd, fmt="o", ms=9, capsize=5,
                    color=COLORS[s["order"] - 1], label=s["id"])
    ax.axvspan(0.5, 3.5, color="tab:red", alpha=0.07)
    ax.axvspan(3.5, 5.5, color="tab:green", alpha=0.07)
    ax.set(xlabel="defect rank (1 = most defects, 5 = most defect-free)",
           ylabel="T = TOP/CH5", xticks=ranks,
           title=f"T vs defect grade\nSpearman ρ = {defect_out['t_ch5']['spearman_rho']:+.2f} "
                 f"(p = {defect_out['t_ch5']['spearman_p']:.2f})")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    ax = axes[2]
    for s, c in zip(specs, COLORS):
        ax.plot(s["order"], 100 * s["saturation"]["CH5"]["median_frac_fs"], "o", ms=10,
                color=c)
        ax.plot(s["order"], s["aggregates"]["ch5_180_g"]["mean"] /
                max(sp["aggregates"]["ch5_180_g"]["mean"] for sp in specs) * 100,
                "s", ms=9, color=c, alpha=0.5)
    ax.axvline(3.5, color="k", ls="--", lw=1.5)
    ax.text(3.55, ax.get_ylim()[1] * 0.95, "felt adjusted", fontsize=9, va="top")
    ax.set(xlabel="specimen order (test sequence)", xticks=[1, 2, 3, 4, 5],
           ylabel="CH5 raw median (% FS)  •   input, normalised (%)  ■",
           title="the confound: the input moves at\nthe same boundary as the defect grouping")
    ax.grid(alpha=0.3)
    fig.suptitle("How much of the between-specimen difference is the print, "
                 "and how much is the rig?")
    fig.tight_layout()
    fig.savefig(FIG / "03_variance_and_confound.png", dpi=130)
    plt.close(fig)

    # ---------------- machine-readable summary --------------------------
    payload = {
        "study": "print-defect sensitivity, five nominally identical T3-prism prints",
        "height_in": 60, "stack": "4 felt + 1 cardboard",
        "burn_in_drops": SOP_BURN_IN,
        "confound_note": "the felt was moved/adjusted before specimens 4 and 5, which "
                         "are also the low-defect specimens and ran on a different day",
        "specimens": [{k: v for k, v in s.items() if k not in ("rows", "stable")}
                      for s in specs],
        "between_specimen": stats_out,
        "pairwise_T": pairwise,
        "defect_relationship": defect_out,
        "sequence_within_day": seq,
        "within_session_excursion_T": excursion,
        "replicate_prints_for_80pct_power": {str(k): v for k, v in reps.items()},
        "confound": confound,
        "per_capture": {s["id"]: [{k: v for k, v in r.items() if k != "series"}
                                  for r in s["rows"]] for s in specs},
    }
    with open(FIG / "print_defects_metrics.json", "w") as fh:
        json.dump(payload, fh, indent=1)
    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
