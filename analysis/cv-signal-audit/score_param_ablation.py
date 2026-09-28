"""Score the parameter-space ablation LOGO runs against the 12-parameter run.

PR #111 follow-up (sgbaird, 2026-09-23): what happens to held-out skill if
the model ignores the six print-process parameters added in round 3 and is
built on the original six (five shape coordinates + weighed printed mass,
the rounds-1-and-2 fit space)? A shape-only run (mass removed too) isolates
what the mass input contributes.

Reuses the audit's scoring machinery (`cv_signal_audit.py`) unchanged: the
same article-level scorecard (r, Spearman rho with permutation p, honest
out-of-sample R^2, MAPE, calibration, shrinkage, exploit-cluster view,
attenuator AUC) and the same design-level collapse, each run cross-checked
against the Ax diagnostics its driver archived. All three runs share the
folds, the NUTS budget (256/512), the seeding scheme, and the measured
values; only the fit space differs.

Inputs (produced by rerun_logocv_full_nuts.py / rerun_logocv_param_ablation.py):

- data/full-nuts-rerun/          12 params: shape + mass + 6 process
- data/ablation-six-param/        6 params: shape + mass (rounds-1/2 space)
- data/ablation-shape-only/       5 params: shape alone

Outputs: metrics-param-ablation.json, figures/param-ablation-comparison.png,
and a headline table on stdout. Runs whose files are missing are skipped, so
the script can score partial progress. Deterministic (fixed seed, fixed run
order).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import cv_signal_audit as base

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGS = HERE / "figures"

RUNS = {
    "shape-only": {
        "dir": DATA / "ablation-shape-only",
        "label": "5 params: shape only",
        "short": "5 (shape)",
        "n_params": 5,
    },
    "six-param": {
        "dir": DATA / "ablation-six-param",
        "label": "6 params: shape + mass (rounds-1/2 space)",
        "short": "6 (shape+mass)",
        "n_params": 6,
    },
    "twelve-param": {
        "dir": DATA / "full-nuts-rerun",
        "label": "12 params: shape + mass + 6 process (round-5 space)",
        "short": "12 (+process)",
        "n_params": 12,
    },
}
CSV_NAME = "t3-prism-bo-round5-logocv.csv"
DIAG_NAME = "t3-prism-bo-round5-logocv-diagnostics.json"
ORDER = ["shape-only", "six-param", "twelve-param"]


def headline(res: dict, present: list[str]) -> dict:
    out = {}
    for metric in base.METRICS:
        rows = {}
        for key in present:
            a = res["runs"][key]["article_level"][metric]
            d = res["runs"][key]["design_level"][metric]
            row = {
                "pearson_r": a["pearson_r"],
                "spearman_rho": a["spearman_rho"],
                "spearman_p_perm": a["spearman_p_perm"],
                "R2_oos_vs_fold_train_mean": a["R2_oos_vs_fold_train_mean"],
                "mape_pct": a["mape_pct"],
                "shrinkage_sd_pred_over_sd_obs": a["shrinkage_sd_pred_over_sd_obs"],
                "design_spearman_rho": d["spearman_rho"],
                "design_spearman_p_perm": d["spearman_p_perm"],
            }
            if metric == "t180":
                row["auc_attenuator"] = a["auc_attenuator"]
                row["auc_attenuator_p"] = a["auc_attenuator_p"]
                cl = res["runs"][key]["article_level"]["t180_cluster_only"]
                row["cluster_pearson_r"] = cl["pearson_r"]
                row["cluster_spearman_rho"] = cl["spearman_rho"]
                row["cluster_spearman_p"] = cl["spearman_p_perm"]
            rows[key] = row
        out[metric] = rows
    return out


def cross_run_shifts(logos: dict, present: list[str]) -> dict:
    """How far each ablation moved the held-out predictions from 12-param."""
    out = {}
    if "twelve-param" not in present:
        return out
    for key in present:
        if key == "twelve-param":
            continue
        per_metric = {}
        for metric in base.METRICS:
            t = logos["twelve-param"]
            s = logos[key]
            tp = t[t.metric == metric].set_index("print_id").predicted
            sp = s[s.metric == metric].set_index("print_id").predicted.reindex(tp.index)
            obs = t[t.metric == metric].set_index("print_id").observed
            per_metric[metric] = {
                "pearson_r_between_runs": float(np.corrcoef(tp, sp)[0, 1]),
                "median_abs_shift": float(np.median(np.abs(sp - tp))),
                "median_abs_shift_over_sd_obs": float(
                    np.median(np.abs(sp - tp)) / obs.std(ddof=1)),
            }
        out[key] = per_metric
    return out


def fig_comparison(logos: dict, res: dict, present: list[str]) -> None:
    """Top: where the 6-param model moved each article's held-out prediction.
    Bottom: the headline statistics across the three fit spaces."""
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 9.2))

    for col, metric in enumerate(base.METRICS):
        ax = axes[0, col]
        t = logos["twelve-param"]
        s = logos["six-param"]
        f = t[t.metric == metric].set_index("print_id")
        g = s[s.metric == metric].set_index("print_id")
        d = pd.DataFrame({"twelve": f.predicted,
                          "six": g.predicted.reindex(f.index),
                          "batch": f.batch}).reset_index()
        lo = min(d.twelve.min(), d.six.min())
        hi = max(d.twelve.max(), d.six.max())
        pad = 0.06 * (hi - lo)
        lims = (lo - pad, hi + pad)
        ax.plot(lims, lims, ls="--", lw=1, color="0.6", zorder=1)
        base.scatter_by_batch(ax, d, "twelve", "six")
        ax.set_xlim(lims), ax.set_ylim(lims)
        ax.set_aspect("equal")
        ax.set_xlabel("Held-out prediction, 12 params")
        ax.set_ylabel("Held-out prediction, 6 params (shape + mass)")
        cr = res["cross_run_prediction_shifts"]["six-param"][metric]
        box = (f"between-run r = {cr['pearson_r_between_runs']:.3f}\n"
               f"median |shift| = {cr['median_abs_shift']:.3g} "
               f"({100 * cr['median_abs_shift_over_sd_obs']:.0f}% of data sd)")
        # lower-right for rebound: an outlying 2dran marker lives top-center
        bx, by, bva, bha = ((0.03, 0.97, "top", "left") if metric == "t180"
                            else (0.97, 0.03, "bottom", "right"))
        ax.text(bx, by, box, transform=ax.transAxes, va=bva, ha=bha,
                fontsize=9,
                bbox=dict(facecolor="white", alpha=0.9, edgecolor="0.8", pad=3))
        if metric == "t180":
            row = d[d.print_id == "corny7"].iloc[0]
            ax.annotate("corny7", (row.twelve, row.six),
                        textcoords="offset points", xytext=(8, 2),
                        fontsize=8, color="0.35")
        ax.set_title(base.METRIC_LABEL[metric], fontsize=11)
        base.style_axis(ax)

    stats_spec = [
        ("spearman_rho", "spearman_p_perm", "article_level", "o", True,
         "Spearman rho, articles (n = 44)"),
        ("spearman_rho", "spearman_p_perm", "design_level", "o", False,
         "Spearman rho, design means (n = 35)"),
        ("R2_oos_vs_fold_train_mean", None, "article_level", "s", True,
         "$R^2_{\\rm oos}$ vs fold-train mean"),
    ]
    # neutral proxy handles: in the panels the rho markers wear the metric
    # hue, so the legend stays colorless to avoid naming either metric
    from matplotlib.lines import Line2D
    proxies = [
        Line2D([], [], ls="", marker=m, markersize=8, color="0.3",
               markerfacecolor="0.3" if filled else "none",
               markeredgewidth=1.5, label=lbl)
        for _, _, _, m, filled, lbl in stats_spec
    ]
    xs = {k: i for i, k in enumerate(ORDER)}
    for col, metric in enumerate(base.METRICS):
        ax = axes[1, col]
        hue = base.T180_COLOR if metric == "t180" else base.REB_COLOR
        ax.axhline(0.0, color="0.55", lw=1.1, zorder=1)
        for stat, pkey, level, marker, filled, label in stats_spec:
            color = hue if stat == "spearman_rho" else "0.25"
            for key in present:
                m = res["runs"][key][level][metric]
                x = xs[key] + (-0.12 if level == "design_level" else
                               (0.12 if stat.startswith("R2") else 0.0))
                ax.scatter(x, m[stat], s=64, marker=marker,
                           facecolors=color if filled else "none",
                           edgecolors=color, lw=1.5, zorder=3)
                if pkey and level == "article_level":
                    ax.annotate(f"p = {m[pkey]:.3f}", (x, m[stat]),
                                textcoords="offset points", xytext=(7, 4),
                                fontsize=7.5, color="0.35")
        ax.set_xticks(range(len(ORDER)))
        ax.set_xticklabels([RUNS[k]["short"] for k in ORDER], fontsize=9)
        ax.set_xlim(-0.5, len(ORDER) - 0.5)
        ax.set_xlabel("Fit space (number of parameters)")
        if col == 0:
            ax.set_ylabel("Held-out statistic")
        ax.set_title(base.METRIC_LABEL[metric], fontsize=11)
        base.style_axis(ax)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=5, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, 0.995))
    fig.legend(handles=proxies, loc="lower center", ncol=3, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.suptitle("Fit-space ablation at the same folds, budget, and seeds "
                 "(LOGO-CV, NUTS 256/512)", fontsize=12, y=1.03)
    fig.tight_layout(rect=(0, 0.035, 1, 0.975))
    fig.savefig(FIGS / "param-ablation-comparison.png", dpi=200,
                bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIGS.mkdir(exist_ok=True)
    rng = np.random.default_rng(base.SEED)
    present = [k for k in ORDER[::-1] if (RUNS[k]["dir"] / CSV_NAME).exists()]
    # score twelve-param first so its Monte-Carlo draws (and therefore its
    # permutation p-values) are identical to the main audit's metrics.json
    logos, res = {}, {"nuts_budget": "256 samples / 512 warmup per fold "
                                     "(library default) for every run",
                      "runs": {}}
    for key in present:
        logo = base.load_logo(RUNS[key]["dir"] / CSV_NAME)
        logos[key] = logo
        res["runs"][key] = {
            "label": RUNS[key]["label"],
            "n_params": RUNS[key]["n_params"],
            "article_level": base.section_logo(
                logo, rng, RUNS[key]["dir"] / DIAG_NAME),
            "design_level": base.section_design_level(logo, rng),
        }

    # same articles, same measurements in every run; only predictions differ
    ref = present[0]
    for key in present[1:]:
        for metric in base.METRICS:
            a = logos[ref][logos[ref].metric == metric].set_index("print_id")
            b = logos[key][logos[key].metric == metric].set_index("print_id")
            assert np.allclose(a.observed, b.observed.reindex(a.index))

    res["cross_run_prediction_shifts"] = cross_run_shifts(logos, present)
    res["headline"] = headline(res, present)

    (HERE / "metrics-param-ablation.json").write_text(
        json.dumps(res, indent=2) + "\n")

    if {"twelve-param", "six-param"} <= set(present):
        fig_comparison(logos, res, present)

    for metric in base.METRICS:
        print(f"\n=== {metric} ===")
        cols = ["pearson_r", "spearman_rho", "spearman_p_perm",
                "R2_oos_vs_fold_train_mean", "mape_pct",
                "design_spearman_rho", "design_spearman_p_perm"]
        table = pd.DataFrame(res["headline"][metric]).T[cols]
        print(table.round(4).to_string())
        for key in present:
            ok = res["runs"][key]["article_level"][metric][
                "matches_archived_diagnostics"]
            print(f"  {key}: matches its archived Ax diagnostics: {ok}")


if __name__ == "__main__":
    main()
