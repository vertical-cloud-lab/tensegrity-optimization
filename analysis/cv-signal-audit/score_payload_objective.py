"""Score the payload-objective LOGO run against the campaign objectives.

PR #111 follow-up (sgbaird, 2026-09-24): re-score the BO campaign under
``tavg10ms``. The run in ``data/objective-tavg10ms/`` re-fit the
campaign's own round-5 surrogate (12-parameter space, NUTS 256/512,
same 35 design folds and per-fold seeds as ``data/full-nuts-rerun/``)
with the fit metrics swapped to the payload pair (``tavg10ms``,
``late_avg3ms_g``). This script asks whether the surrogate has held-out
skill on the payload objectives, and how that compares with the same
protocol's skill on the campaign objectives (t180, e_reb_mJ).

Reuses the audit's scoring machinery (`cv_signal_audit.py`): the same
article-level scorecard (r, Spearman rho with permutation p, honest
out-of-sample R^2, MAPE, calibration, shrinkage), the same design-level
collapse, plus two views the payload question needs: within-batch rank
skill (a print-session-free read) and the t180 exploit-cluster subset.
The 12-parameter baseline is scored first with the same seed so its
Monte-Carlo p-values reproduce the audit's metrics.json exactly.

Outputs: metrics-payload-objective.json,
figures/payload-objective-logocv.png, and a headline table on stdout.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import cv_signal_audit as base

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGS = HERE / "figures"

RUN_DIRS = {
    "twelve-param": DATA / "objective-tavg10ms",
    "shape-only": DATA / "objective-tavg10ms-shape-only",
}
RUN_LABEL = {"twelve-param": "12 params (campaign space)",
             "shape-only": "5 params (shape only)"}
CSV_NAME = "t3-prism-bo-round5-logocv.csv"
DIAG_NAME = "t3-prism-bo-round5-logocv-diagnostics.json"

PAYLOAD_METRICS = ("tavg10ms", "late_avg3ms_g")
PAYLOAD_LABEL = {"tavg10ms": "tavg10ms (10 ms dose ratio)",
                 "late_avg3ms_g": "late_avg3ms (hop landing, G)"}
# which campaign metric each payload metric replaces, for the comparison
COUNTERPART = {"tavg10ms": "t180", "late_avg3ms_g": "e_reb_mJ"}
BATCHES = ("seed", "r2d2c", "drran", "2dran", "corny")
N_PERM_BATCH = 20_000


def within_batch(d: pd.DataFrame, rng: np.random.Generator) -> dict:
    """Mean within-batch Spearman rho with a within-batch permutation p."""
    per = {}
    groups = []
    for b in BATCHES:
        g = d[d.batch == b]
        per[b] = float(stats.spearmanr(g.observed, g.predicted).statistic)
        groups.append((g.observed.values, g.predicted.values))
    mean_obs = float(np.mean(list(per.values())))
    null = np.empty(N_PERM_BATCH)
    for i in range(N_PERM_BATCH):
        vals = [stats.spearmanr(o, rng.permutation(p)).statistic
                for o, p in groups]
        null[i] = np.mean(vals)
    p = float((np.sum(np.abs(null) >= abs(mean_obs) - 1e-12) + 1)
              / (N_PERM_BATCH + 1))
    return {"per_batch_rho": per, "mean_rho": mean_obs, "perm_p": p}


def score_payload_run(logo: pd.DataFrame, logo_t180: pd.DataFrame,
                      rng: np.random.Generator, diag_path: Path) -> dict:
    out = {}
    diag = json.loads(diag_path.read_text())
    cluster_ids = set(
        logo_t180[(logo_t180.metric == "t180")
                  & (logo_t180.observed >= 0.95)
                  & (logo_t180.observed <= 1.10)].print_id)
    for metric in PAYLOAD_METRICS:
        d = logo[logo.metric == metric]
        m = base.held_out_metrics(d.observed.values, d.predicted.values,
                                  d.predicted_sem.values, d.design.values, rng)
        m["matches_archived_diagnostics"] = bool(
            abs(m["pearson_r"] - diag["Correlation coefficient"][metric]) < 1e-4
            and abs(m["mape_pct"] / 100 - diag["MAPE"][metric]) < 1e-4
            and abs(m["spearman_rho"] - diag["Rank correlation"][metric]) < 1e-3
        )
        obs, pred = d.observed.values, d.predicted.values
        better = (obs < np.median(obs)).astype(int)  # lower is better for both
        auc, auc_p = base.auc_mannwhitney(better, -pred)
        m["auc_better_half"] = auc
        m["auc_better_half_p"] = auc_p
        m["within_batch"] = within_batch(d, rng)
        cl = d[d.print_id.isin(cluster_ids)]
        m["t180_exploit_cluster"] = base.held_out_metrics(
            cl.observed.values, cl.predicted.values,
            cl.predicted_sem.values, cl.design.values, rng)
        m["t180_exploit_cluster"]["n"] = int(len(cl))
        out[metric] = m

    # design-level collapse (reprints averaged), as in the main audit
    out["design_level"] = {}
    for metric in PAYLOAD_METRICS:
        d = logo[logo.metric == metric]
        g = d.groupby("design").agg(observed=("observed", "mean"),
                                    predicted=("predicted", "mean"),
                                    predicted_sem=("predicted_sem", "mean"))
        out["design_level"][metric] = base.held_out_metrics(
            g.observed.values, g.predicted.values,
            g.predicted_sem.values, g.index.values, rng)
        # mirrored under the metric too, so figure/table code can treat the
        # payload runs and the baseline dicts uniformly
        out[metric]["design_level"] = out["design_level"][metric]

    # the campaign-story check: where does the model place corny7?
    t = logo[logo.metric == "tavg10ms"]
    out["corny7"] = {
        "observed_rank_of_44": int(stats.rankdata(t.observed.values)[
            list(t.print_id).index("corny7")]),
        "predicted_rank_of_44": int(stats.rankdata(t.predicted.values)[
            list(t.print_id).index("corny7")]),
    }

    # do the reprint twins agree, observed and as predicted?
    tw = {}
    for metric in PAYLOAD_METRICS:
        d = logo[logo.metric == metric]
        p1 = d[d.batch == "drran"].set_index("design")
        p2 = d[d.batch == "2dran"].set_index("design")
        common = p1.index.intersection(p2.index)
        tw[metric] = {
            "observed_pair_rho": float(stats.spearmanr(
                p1.loc[common].observed, p2.loc[common].observed).statistic),
            "predicted_pair_rho": float(stats.spearmanr(
                p1.loc[common].predicted, p2.loc[common].predicted).statistic),
        }
    out["reprint_pairs"] = tw
    return out


def fig_payload(logo: pd.DataFrame, res: dict, baseline: dict,
                shape: dict | None = None) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 9.4))

    for col, metric in enumerate(PAYLOAD_METRICS):
        ax = axes[0, col]
        d = logo[logo.metric == metric].copy()
        lo = min(d.observed.min(), d.predicted.min())
        hi = max(d.observed.max(), d.predicted.max())
        pad = 0.06 * (hi - lo)
        lims = (lo - pad, hi + pad)
        ax.plot(lims, lims, ls="--", lw=1, color="0.6", zorder=1)
        base.scatter_by_batch(ax, d, "observed", "predicted")
        ax.set_xlim(lims), ax.set_ylim(lims)
        ax.set_aspect("equal")
        ax.set_xlabel("Measured (held-out article)")
        ax.set_ylabel("LOGO-CV prediction")
        m = res[metric]
        box = (f"rho_s = {m['spearman_rho']:+.2f} "
               f"(perm p = {m['spearman_p_perm']:.4f})\n"
               f"$R^2_{{\\rm oos}}$ = {m['R2_oos_vs_fold_train_mean']:+.2f}   "
               f"MAPE = {m['mape_pct']:.1f}%")
        ax.text(0.03, 0.97, box, transform=ax.transAxes, va="top", ha="left",
                fontsize=9,
                bbox=dict(facecolor="white", alpha=0.9, edgecolor="0.8", pad=3))
        if metric == "tavg10ms":
            row = d[d.print_id == "corny7"].iloc[0]
            ax.annotate("corny7", (row.observed, row.predicted),
                        textcoords="offset points", xytext=(8, -2),
                        fontsize=8, color="0.35")
        ax.set_title(PAYLOAD_LABEL[metric], fontsize=11)
        base.style_axis(ax)

    # bottom row: payload metric vs its campaign counterpart, same protocol
    stat_spec = [
        ("spearman_rho", "article rho_s\n(n = 44)"),
        ("design_spearman_rho", "design rho_s\n(n = 35)"),
        ("within_batch_mean", "within-batch\nmean rho_s"),
        ("R2_oos_vs_fold_train_mean", "$R^2_{\\rm oos}$"),
    ]
    for col, metric in enumerate(PAYLOAD_METRICS):
        ax = axes[1, col]
        cp = COUNTERPART[metric]
        hue = base.T180_COLOR if col == 0 else base.REB_COLOR
        pairs = [(baseline[cp], "0.45", f"{cp} (campaign objective, 12p)",
                  "s", True, -0.16),
                 (res[metric], hue, f"{PAYLOAD_LABEL[metric]}, 12p",
                  "o", True, 0.0)]
        if shape is not None:
            pairs.append((shape[metric], hue,
                          f"{PAYLOAD_LABEL[metric]}, shape-only",
                          "o", False, 0.16))
        ax.axhline(0.0, color="0.55", lw=1.1, zorder=1)
        for j, (stat, lbl) in enumerate(stat_spec):
            for src, color, name, marker, filled, off in pairs:
                if stat == "design_spearman_rho":
                    v = src["design_level"]["spearman_rho"]
                elif stat == "within_batch_mean":
                    v = src["within_batch"]["mean_rho"]
                else:
                    v = src[stat]
                ax.scatter(j + off, v, s=70, marker=marker,
                           facecolors=color if filled else "none",
                           edgecolors=color, lw=1.5,
                           label=name if j == 0 else None, zorder=3)
        ax.annotate(f"p = {res[metric]['spearman_p_perm']:.4f}",
                    (0.0, res[metric]["spearman_rho"]),
                    textcoords="offset points", xytext=(6, 5),
                    fontsize=7.5, color="0.35")
        ax.set_xticks(range(len(stat_spec)))
        ax.set_xticklabels([s[1] for s in stat_spec], fontsize=8.5)
        ax.set_ylabel("Held-out statistic" if col == 0 else "")
        ax.legend(fontsize=8, frameon=False, loc="lower left")
        ax.set_title(f"{PAYLOAD_LABEL[metric]} vs {cp}", fontsize=11)
        base.style_axis(ax)

    fig.suptitle("Payload objectives under the campaign's own surrogate "
                 "protocol (12 params, LOGO-CV, NUTS 256/512, same folds "
                 "and seeds)", fontsize=12, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(FIGS / "payload-objective-logocv.png", dpi=200,
                bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIGS.mkdir(exist_ok=True)
    rng = np.random.default_rng(base.SEED)

    # 12-param campaign-objective baseline first: identical rng consumption
    # order to the main audit, so these numbers reproduce metrics.json
    logo_t180 = base.load_logo(DATA / "full-nuts-rerun" / CSV_NAME)
    baseline_articles = base.section_logo(
        logo_t180, rng, DATA / "full-nuts-rerun" / DIAG_NAME)
    baseline_design = base.section_design_level(logo_t180, rng)
    baseline = {}
    for m in base.METRICS:
        baseline[m] = dict(baseline_articles[m])
        baseline[m]["design_level"] = baseline_design[m]
        d = logo_t180[logo_t180.metric == m]
        baseline[m]["within_batch"] = within_batch(d, rng)

    # each payload run gets its own generator, so its p-values do not move
    # when the other run appears or disappears
    logos, runs = {}, {}
    for i, (key, rd) in enumerate(RUN_DIRS.items(), start=1):
        if not (rd / CSV_NAME).exists():
            continue
        logos[key] = base.load_logo(rd / CSV_NAME)
        runs[key] = score_payload_run(
            logos[key], logo_t180,
            np.random.default_rng(base.SEED + i), rd / DIAG_NAME)

    out = {
        "protocol": "LOGO-CV, NUTS 256/512, fold order and per-fold seeds "
                    "identical to data/full-nuts-rerun; fit metrics swapped "
                    "to the payload pair from data/payload-objectives.csv "
                    "(full-101 seed pass); twelve-param = campaign round-5 "
                    "space, shape-only = the Section 6 five-coordinate space",
        "payload_runs": runs,
        "campaign_baseline_12param": baseline,
    }
    (HERE / "metrics-payload-objective.json").write_text(
        json.dumps(out, indent=2) + "\n")

    if "twelve-param" in runs:
        fig_payload(logos["twelve-param"], runs["twelve-param"], baseline,
                    runs.get("shape-only"))

    rows = []
    for metric in PAYLOAD_METRICS:
        cp = COUNTERPART[metric]
        sources = [(f"{cp} [campaign, 12p]", baseline[cp])]
        sources += [(f"{metric} [{key}]", runs[key][metric]) for key in runs]
        for name, src in sources:
            dl = src["design_level"]
            rows.append({
                "objective": name,
                "rho_s": round(src["spearman_rho"], 3),
                "p": round(src["spearman_p_perm"], 4),
                "design_rho_s": round(dl["spearman_rho"], 3),
                "design_p": round(dl["spearman_p_perm"], 4),
                "within_batch": round(src["within_batch"]["mean_rho"], 3),
                "wb_p": round(src["within_batch"]["perm_p"], 4),
                "R2_oos": round(src["R2_oos_vs_fold_train_mean"], 3),
                "MAPE_pct": round(src["mape_pct"], 1),
                "cov95_pct": round(src["coverage_95_pct"], 0),
                "diag_ok": src.get("matches_archived_diagnostics", "n/a"),
            })
    print(pd.DataFrame(rows).to_string(index=False))
    for key, res in runs.items():
        print(f"\n[{key}] corny7 (tavg10ms): observed rank "
              f"{res['corny7']['observed_rank_of_44']}/44, predicted rank "
              f"{res['corny7']['predicted_rank_of_44']}/44")
        print(f"[{key}] cluster rho_s (tavg10ms): "
              f"{res['tavg10ms']['t180_exploit_cluster']['spearman_rho']:+.3f} "
              f"(p {res['tavg10ms']['t180_exploit_cluster']['spearman_p_perm']:.4f})")
        print(f"[{key}] reprint twins:", json.dumps(res["reprint_pairs"]))


if __name__ == "__main__":
    main()
