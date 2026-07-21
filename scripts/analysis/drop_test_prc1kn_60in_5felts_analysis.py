#!/usr/bin/env python3
"""prc1kn 60 in campaign + three-way transmissibility comparison.

@me-madsen ran the rig-calibration standard ``prc1kn`` through the same
full-length campaign as the 60 in / 5 felt validation (PR #86): 101 captures
(``prc1kn - set 1 - {1..4}.zip``, session "prc1kn 60in - 4 felt 1 cardboard",
2026-07-21 20:56-22:06). Note the TP4 session ID: the stack was **4 felt
sheets + 1 cardboard**, not the 5 felt sheets used for ``7xadt6``/``9GMQYQ``
— the input channel tells us how comparable that makes the base hit.

Rig otherwise unchanged: CH2/CH3/CH4 = top-vertex key-seat tri-axis ("TOP"
output), CH5 = single-axis on the base acrylic plate (input + trigger),
200 ms / 125 kHz per capture, raw data stays in the committed zips.

This script:

  1. runs the identical per-capture pipeline + burn-in scan + stabilized OLS
     as ``drop_test_60in_5felts_analysis.py`` (imported, not copied) on
     ``prc1kn``;
  2. reloads the committed per-capture metrics for ``7xadt6``/``9GMQYQ``
     from ``60in_5felts_metrics.json`` and runs the mock three-structure
     transmissibility comparison @me-madsen asked for: stabilized
     T = TOP/CH5 per specimen, one-way ANOVA + pairwise Welch/Cohen's d,
     and an energy-absorber ranking (lower T = more attenuation).

Emits ``data/drop-tests/prc1kn-60in-5felt/figures/prc1kn_60in_metrics.json``
consumed by ``docs/drop-test-prc1kn-60in-5felts-analysis.md``.
"""
from __future__ import annotations

import json
import sys
from itertools import combinations
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
    analyze_specimen,
    arr,
    cv,
    ols_full,
)

OUT = DATA / "prc1kn-60in-5felt"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

PRIOR_METRICS = DATA / "60in-5felts-validation" / "figures" / "60in_5felts_metrics.json"

SPEC = {
    "id": "prc1kn",
    "dir": OUT,
    "zips": [f"prc1kn - set 1 - {k}.zip" for k in (1, 2, 3, 4)],
    "prefix": "prc1kn",
}

COLORS = {"7xadt6": "tab:red", "9GMQYQ": "tab:blue", "prc1kn": "tab:green"}


def stabilized_values(real: list[dict], burn_in: int, key: str) -> np.ndarray:
    drops = arr(real, "drop")
    return arr(real, key)[drops > burn_in]


def main() -> int:
    s = analyze_specimen(SPEC)
    real = s["real"]

    # ---------------- prior campaign (committed metrics) ----------------
    prior = json.loads(PRIOR_METRICS.read_text())
    campaigns = {}
    for sid in ("7xadt6", "9GMQYQ"):
        rows = prior["per_capture"][sid]
        campaigns[sid] = {
            "real": [r for r in rows if r["real_impact"]],
            "burn_in": prior["specimens"][sid]["burn_in_drops"],
        }
    campaigns["prc1kn"] = {"real": real, "burn_in": s["burn_in_drops"]}
    order = ["7xadt6", "9GMQYQ", "prc1kn"]

    # ---------------- input comparability check --------------------------
    print(f"\n{'=' * 70}\n=== input comparability (4 felt + 1 cardboard vs 5 felt) ===\n{'=' * 70}")
    input_ctx = {}
    for sid in order:
        c = campaigns[sid]
        ch5 = stabilized_values(c["real"], c["burn_in"], "ch5_180_g")
        ch5_raw = stabilized_values(c["real"], c["burn_in"], "ch5_raw_g")
        dv = stabilized_values(c["real"], c["burn_in"], "ch5_dv_ms")
        input_ctx[sid] = {
            "ch5_180_mean": float(ch5.mean()), "ch5_180_cv": cv(ch5),
            "ch5_raw_first5": float(np.mean(ch5_raw[:5])),
            "ch5_raw_last5": float(np.mean(ch5_raw[-5:])),
            "ch5_raw_max_frac_fs": float(ch5_raw.max() / FULL_SCALE_G["CH5"]),
            "dv_mean": float(dv.mean()),
        }
        i = input_ctx[sid]
        print(f"  {sid:8s}: CH5 CFC-180 {i['ch5_180_mean']:6.1f} G (CV {i['ch5_180_cv']:.2f}%)  "
              f"raw first5 {i['ch5_raw_first5']:6.0f} G -> last5 {i['ch5_raw_last5']:6.0f} G "
              f"(max {100 * i['ch5_raw_max_frac_fs']:.1f}% FS)   dv {i['dv_mean']:.2f} m/s")

    # ---------------- three-way transmissibility comparison --------------
    print(f"\n{'=' * 70}\n=== mock three-structure comparison (stabilized drops) ===\n{'=' * 70}")
    comparison = {}
    for key, label in [("top_180_g", "TOP CFC-180 (G)"), ("t_ch5", "T = TOP/CH5")]:
        vals = {sid: stabilized_values(campaigns[sid]["real"], campaigns[sid]["burn_in"], key)
                for sid in order}
        f_stat, f_p = stats.f_oneway(*(vals[sid] for sid in order))
        pairs = {}
        for a_id, b_id in combinations(order, 2):
            a, b = vals[a_id], vals[b_id]
            tt = stats.ttest_ind(a, b, equal_var=False)
            sp = np.sqrt((a.std(ddof=1) ** 2 + b.std(ddof=1) ** 2) / 2.0)
            pairs[f"{a_id} vs {b_id}"] = {
                "diff_pct": float(100.0 * (a.mean() - b.mean()) / b.mean()),
                "welch_p": float(tt.pvalue),
                "cohens_d": float((a.mean() - b.mean()) / sp) if sp else float("nan"),
            }
        comparison[key] = {
            "per_specimen": {sid: {"n": int(len(vals[sid])), "mean": float(vals[sid].mean()),
                                   "sd": float(vals[sid].std(ddof=1)), "cv": cv(vals[sid])}
                             for sid in order},
            "anova_f": float(f_stat), "anova_p": float(f_p),
            "pairwise": pairs,
        }
        print(f"\n  {label} (ANOVA F = {f_stat:.0f}, p = {f_p:.1e}):")
        for sid in order:
            v = vals[sid]
            print(f"    {sid:8s}: {v.mean():8.3f} +- {v.std(ddof=1):.3f} (CV {cv(v):.2f}%, n = {len(v)})")
        for pair, p in pairs.items():
            print(f"    {pair:20s}: diff {p['diff_pct']:+6.1f}%   Welch p = {p['welch_p']:.1e}   "
                  f"d = {p['cohens_d']:+.1f}")

    # energy-absorber ranking: lower T = more of the base shock kept away
    # from the payload (T < 1 attenuates, T > 1 amplifies)
    t_means = {sid: comparison["t_ch5"]["per_specimen"][sid]["mean"] for sid in order}
    ranking = sorted(order, key=lambda sid: t_means[sid])
    print("\n  energy-absorber ranking (lower T = better attenuator):")
    for k, sid in enumerate(ranking, start=1):
        t = t_means[sid]
        print(f"    {k}. {sid:8s} T = {t:.3f}  ({'attenuates' if t < 1 else 'amplifies'} "
              f"the CFC-180 peak by {abs(1 - t) * 100:.1f}%)")

    # ---------------- figures -------------------------------------------
    rows = s["rows"]
    sigs = arr(rows, "signal")
    drops = arr(real, "drop")
    stable = drops > s["burn_in_drops"]
    xs = drops[stable]

    # Fig 1: full series
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(sigs, arr(rows, "ch5_raw_g"), "o-", ms=3, color="tab:blue",
            label="CH5 raw |peak| (base plate, trigger)")
    ax.plot(sigs, arr(rows, "top_raw_g"), "s-", ms=3, color="tab:red",
            label="TOP |tri-axis| raw peak (CH2-4)")
    ax.axhline(FULL_SCALE_G["CH5"] / 3.0, color="k", ls=":", lw=1.2,
               label="CH5 FS/3 head-room target")
    for sp_sig in s["spurious_captures"]:
        ax.axvline(sp_sig, color="gray", ls="--", lw=1)
    ax.set(xlabel="capture (Signal #)", ylabel="raw |peak| (G)",
           title=f"prc1kn 60 in / 4 felt + 1 cardboard: {len(real)} real drops / "
                 f"{s['n_captures']} captures (median cadence {s['cadence_s']['median']:.0f} s)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_full_series.png", dpi=130)
    plt.close(fig)

    # Fig 2: stabilized-phase OLS, TOP and T
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    for ax, (key, name) in zip(axes, [("top_180_g", "TOP output CFC-180 (G)"),
                                      ("t_ch5", "T = TOP/CH5 (CFC-180)")]):
        y = arr(real, key)[stable]
        o = ols_full(xs, y)
        ax.plot(xs, y, "o", ms=3.5, color=COLORS["prc1kn"])
        fit = o["mean"] - o["slope"] * xs.mean() + o["slope"] * xs
        ax.plot(xs, fit, "k-", lw=1.5,
                label=f"OLS {o['slope']:+.4f}/drop ({o['slope_pct']:+.3f}%/drop)\n"
                      f"p = {o['p']:.1e}, R² = {o['r2']:.2f}")
        lo_f = o["mean"] - o["ci_lo"] * xs.mean() + o["ci_lo"] * xs
        hi_f = o["mean"] - o["ci_hi"] * xs.mean() + o["ci_hi"] * xs
        ax.fill_between(xs, np.minimum(lo_f, hi_f), np.maximum(lo_f, hi_f),
                        color=COLORS["prc1kn"], alpha=0.15, label="95% CI on slope")
        ax.set(xlabel="drop #", ylabel=name,
               title=f"prc1kn (drops {s['stabilized_window'][0]}-{s['stabilized_window'][1]})")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    fig.suptitle("stabilized-phase OLS drift — prc1kn, 60 in / 4 felt + 1 cardboard")
    fig.tight_layout()
    fig.savefig(FIG / "02_stabilized_ols.png", dpi=130)
    plt.close(fig)

    # Fig 3: saturation audit vs the prior campaign's felt-wear trajectory
    fig, ax = plt.subplots(figsize=(12, 5.5))
    fr5 = np.array([r["sat"]["CH5"]["frac_fs"] for r in rows]) * 100
    fr4 = np.array([r["sat"]["CH4"]["frac_fs"] for r in rows]) * 100
    ax.plot(sigs, fr5, "o-", ms=3, color=COLORS["prc1kn"],
            label=f"prc1kn CH5 (FS {FULL_SCALE_G['CH5']:.0f} G)")
    ax.plot(sigs, fr4, "s--", ms=2.5, color=COLORS["prc1kn"], alpha=0.5,
            label=f"prc1kn CH4 (FS {FULL_SCALE_G['CH4']:.0f} G)")
    for sid in ("7xadt6", "9GMQYQ"):
        fr = np.array([r["sat"]["CH5"]["frac_fs"] for r in prior["per_capture"][sid]]) * 100
        ax.plot(np.arange(1, len(fr) + 1), fr, "-", lw=1, alpha=0.45, color=COLORS[sid],
                label=f"{sid} CH5 (5 felt, 2026-07-20)")
    ax.axhline(100 / 3, color="k", ls=":", lw=1.2, label="FS/3 head-room target")
    ax.set(xlabel="capture (Signal #)", ylabel="raw |peak| (% of full scale)",
           title="saturation audit: prc1kn (4 felt + 1 cardboard) vs the 5-felt campaigns")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "03_saturation.png", dpi=130)
    plt.close(fig)

    # Fig 4: three-structure comparison (stabilized TOP and T)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (key, name) in zip(axes, [("top_180_g", "TOP output CFC-180 (G)"),
                                      ("t_ch5", "T = TOP/CH5")]):
        data = [stabilized_values(campaigns[sid]["real"], campaigns[sid]["burn_in"], key)
                for sid in order]
        bp = ax.boxplot(data, tick_labels=order, patch_artist=True, widths=0.5)
        for patch, sid in zip(bp["boxes"], order):
            patch.set_facecolor(COLORS[sid])
            patch.set_alpha(0.4)
        if key == "t_ch5":
            ax.axhline(1.0, color="k", ls=":", lw=1.2, label="T = 1 (no attenuation)")
            ax.legend(fontsize=8)
        c = comparison[key]
        ax.set(ylabel=name, title=f"ANOVA F = {c['anova_f']:.0f}, p = {c['anova_p']:.1e}")
        ax.grid(alpha=0.3, axis="y")
    fig.suptitle("mock three-structure comparison on the stabilized drops\n"
                 "(caveat: prc1kn ran on 4 felt + 1 cardboard and a separate re-waxed mount)")
    fig.tight_layout()
    fig.savefig(FIG / "04_three_structure_comparison.png", dpi=130)
    plt.close(fig)

    # ---------------- machine-readable summary ---------------------------
    summary = {
        "condition": {"height_in": 60, "stack": "4 felt + 1 cardboard",
                      "session_id": "prc1kn 60in - 4 felt 1 cardboard"},
        "specimen": {k: v for k, v in s.items() if k not in ("rows", "real")},
        "per_capture": rows,
        "input_context": input_ctx,
        "comparison": comparison,
        "energy_absorber_ranking": ranking,
        "t_means": t_means,
    }
    with open(FIG / "prc1kn_60in_metrics.json", "w") as fh:
        json.dump(summary, fh, indent=1)

    print(f"\nwrote figures + metrics to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
