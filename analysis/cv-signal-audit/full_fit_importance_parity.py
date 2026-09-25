"""Full-data SAASBO fits: feature importances and in-sample parity.

PR #111 follow-up (sgbaird, 2026-09-25): show feature importance for a
model trained on ALL of the data, for each combination of fit space and
objective, plus a parity plot of the fully trained model's predictions
with uncertainty to spot-check overfitting.

Six fits, each on all 44 measured articles (no held-out folds):

    fit space  x  objective pair
    -----------------------------
    twelve-param (campaign round-5 space)   x  (t180, e_reb_mJ)
    six-param (shape + weighed mass)        x  (t180, e_reb_mJ)
    shape-only (five shape coordinates)     x  (t180, e_reb_mJ)
    twelve-param                            x  (tavg10ms, late_avg3ms_g)
    six-param                               x  (tavg10ms, late_avg3ms_g)
    shape-only                              x  (tavg10ms, late_avg3ms_g)

Protocol identical to the audit's LOGO reruns except that nothing is held
out: the campaign's round-5 Ax snapshot, ``fit_saasbo`` at library-default
NUTS (256 samples / 512 warmup), ``torch.manual_seed(10000)`` before the
fit, the objective swap of ``rerun_logocv_payload_objective.py`` for the
payload pair, and the subspace cut of ``rerun_logocv_param_ablation.py``
for the reduced spaces. With that seed, each fit IS the corresponding
LOGO rerun's shared initial model state.

Because every committed LOGO run is a single NUTS realization, this
script also refits two of the combinations (the campaign's own
12-parameter fit and the Section 7 recommended shape-only payload fit)
at two extra seeds, so the realization-to-realization movement of the
importances and in-sample stats is measured rather than assumed.

Per fit, three things are extracted with the campaign's own code
(``t3_prism_bo_diagnostics.per_draw_importances`` and Ax's
``feature_importances``):

1. Normalized inverse-lengthscale importance per parameter (Ax's
   median-over-MCMC value) plus the interquartile range across the
   retained NUTS draws, which is the uncertainty of the importance.
2. In-sample posterior predictions (mean, sd) at every training article.
3. Timing and seeds, checkpointed to ``data/full-fit/fits.jsonl`` so the
   run is resumable and each fit can be committed as it lands.

``--plot-only`` re-renders figures/CSVs/metrics from the checkpoint.

Usage (repo root; campaign ``bo/`` tree extracted at ``bbf7a62``)::

    python analysis/cv-signal-audit/full_fit_importance_parity.py \
        --campaign-bo /tmp/campaign/bo --smoke
    python analysis/cv-signal-audit/full_fit_importance_parity.py \
        --campaign-bo /tmp/campaign/bo --max-seconds 520 --commit-each-fit
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

AUDIT_DIR = Path(__file__).resolve().parent
OUT_DIR = AUDIT_DIR / "data" / "full-fit"
FIGS = AUDIT_DIR / "figures"
OBJECTIVES_CSV = AUDIT_DIR / "data" / "payload-objectives.csv"
METRICS_OUT = AUDIT_DIR / "metrics-full-fit.json"
PUSH_SCRIPT = Path(
    "/home/runner/work/_actions/anthropics/claude-code-action/v1/scripts/git-push.sh"
)
COMMIT_TRAILER = (
    "\n\nCo-authored-by: Sterling G. Baird "
    "<45469701+sgbaird@users.noreply.github.com>"
    "\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
)

SPACES = ("twelve-param", "six-param", "shape-only")
PAIRS = {
    "campaign": ("t180", "e_reb_mJ"),
    "payload": ("tavg10ms", "late_avg3ms_g"),
}
CANONICAL_SEED = 10_000
# realization-noise probes: (space, pair) -> extra torch seeds
SEED_REPEATS = {
    ("twelve-param", "campaign"): [11, 12],
    ("shape-only", "payload"): [11, 12],
}

OBJ_LABEL = {
    "t180": "t180 (transmissibility)",
    "e_reb_mJ": "rebound score (mJ)",
    "tavg10ms": "tavg10ms (10 ms dose ratio)",
    "late_avg3ms_g": "late_avg3ms (hop landing, G)",
}
OBJ_COLOR = {
    "t180": "#1f77b4",
    "e_reb_mJ": "#e8590c",
    "tavg10ms": "#009E73",
    "late_avg3ms_g": "#CC79A7",
}
SPACE_LABEL = {
    "twelve-param": "12 params (campaign round-5 space)",
    "six-param": "6 params (shape + mass)",
    "shape-only": "5 params (shape only)",
}
# fixed parameter order and grouping, constant across every panel
PARAM_ORDER = [
    "R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm",
    "mass_printed_g", "strut_infill_pct", "tpu_infill_pct",
    "pla_nozzle_temp_C", "pla_flow_mm3_s", "tpu_nozzle_temp_C",
    "tpu_flow_mm3_s",
]
PARAM_LABEL = {
    "R_mm": "R (mm)",
    "H_mm": "H (mm)",
    "twist_deg": "twist (deg)",
    "strut_d_mm": "strut dia (mm)",
    "cable_d_mm": "cable dia (mm)",
    "mass_printed_g": "printed mass (g)",
    "strut_infill_pct": "strut infill (%)",
    "tpu_infill_pct": "TPU infill (%)",
    "pla_nozzle_temp_C": "PLA nozzle (C)",
    "pla_flow_mm3_s": "PLA flow (mm3/s)",
    "tpu_nozzle_temp_C": "TPU nozzle (C)",
    "tpu_flow_mm3_s": "TPU flow (mm3/s)",
}
GROUP_OF = {
    "R_mm": "shape", "H_mm": "shape", "twist_deg": "shape",
    "strut_d_mm": "shape", "cable_d_mm": "shape",
    "mass_printed_g": "mass",
    "strut_infill_pct": "process-article", "tpu_infill_pct": "process-article",
    "pla_nozzle_temp_C": "process-filament", "pla_flow_mm3_s": "process-filament",
    "tpu_nozzle_temp_C": "process-filament", "tpu_flow_mm3_s": "process-filament",
}
# Okabe-Ito hues (CVD-safe with gray); entity colors, fixed across panels
GROUP_COLOR = {
    "shape": "#0072B2",
    "mass": "#E69F00",
    "process-article": "#009E73",
    "process-filament": "#8c8c8c",
}
GROUP_LEGEND = {
    "shape": "shape coordinate",
    "mass": "weighed printed mass",
    "process-article": "process, per-article (infill)",
    "process-filament": "process, per-batch (temps/flows)",
}

STATE_PATH = OUT_DIR / "state.json"
FITS_PATH = OUT_DIR / "fits.jsonl"


def _git_commit_push(paths, message, push=True):
    """Commit checkpoint files; never let a git hiccup kill the run."""
    try:
        repo_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        subprocess.run(["git", "add", *[str(p) for p in paths]],
                       cwd=repo_root, check=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_root)
        if diff.returncode == 0:
            return
        subprocess.run(["git", "commit", "-m", message + COMMIT_TRAILER],
                       cwd=repo_root, check=True)
        if push and PUSH_SCRIPT.exists():
            r = subprocess.run([str(PUSH_SCRIPT), "origin", "HEAD"], cwd=repo_root)
            if r.returncode != 0:
                subprocess.run(["git", "pull", "--rebase", "origin", branch],
                               cwd=repo_root, check=True)
                subprocess.run([str(PUSH_SCRIPT), "origin", "HEAD"],
                               cwd=repo_root, check=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  WARNING: checkpoint commit/push failed ({exc}); "
              "data is on disk, continuing", flush=True)


def build_experiment(campaign_bo, space, pair):
    """Fresh snapshot load + label join + objective swap + subspace cut.

    Same mechanics as rerun_logocv_payload_objective.py and
    rerun_logocv_param_ablation.py, on a freshly loaded experiment so
    fits cannot contaminate one another.
    """
    from ax.service.ax_client import AxClient
    from t3_prism_bo_campaign import (
        BO_DIR,
        PARAM_NAMES,
        fit_search_space,
        load_round2_training_data,
        load_round3_reprint_training_data,
        load_round3_training_data,
        load_round4_training_data,
        load_training_data,
        mass_param,
    )

    snapshot = campaign_bo / "t3-prism-bo-ax-client-round5.json"
    ax_client = AxClient.load_from_json_file(str(snapshot))
    experiment = ax_client.experiment
    has_process = "pla_nozzle_temp_C" in experiment.search_space.parameters
    data = experiment.fetch_data()

    X1, _, labels1, _, _ = load_training_data(
        BO_DIR / "t3-prism-bo-batch-drop-results.csv",
        BO_DIR / "t3-prism-bo-batch.csv", process=None)
    X2, _, labels2, _, _ = load_round2_training_data(process=None)
    X3, _, labels3, _, _ = load_round3_training_data(include_process=has_process)
    X3r, _, labels3r, _, _ = load_round3_reprint_training_data(include_process=has_process)
    X4, _, labels4, _, _ = load_round4_training_data(include_process=has_process)
    X_all = X1 + X2 + X3 + X3r + X4
    labels_all = labels1 + labels2 + labels3 + labels3r + labels4
    labels_by_arm = {}
    for trial in experiment.trials.values():
        arm = trial.arm
        for x, label in zip(X_all, labels_all):
            if all(abs(float(arm.parameters[k]) - float(v)) < 1e-6
                   for k, v in x.items()):
                labels_by_arm[arm.name] = label.split(" ")[0]
                break
    n_articles = int(data.df["arm_name"].nunique())

    if pair == "payload":
        from ax.core.data import Data
        from ax.core.metric import Metric

        obj = pd.read_csv(OBJECTIVES_CSV).set_index("print_id")
        seen = data.df[["trial_index", "arm_name"]].drop_duplicates()
        rows, matched = [], []
        for r in seen.itertuples():
            pid = labels_by_arm.get(r.arm_name)
            if pid is None or pid not in obj.index:
                raise RuntimeError(f"arm {r.arm_name} (print {pid}) has no "
                                   "payload objective values; refusing to run")
            matched.append(pid)
            for m in PAIRS["payload"]:
                rows.append({"trial_index": int(r.trial_index),
                             "arm_name": r.arm_name, "metric_name": m,
                             "mean": float(obj.loc[pid, f"{m}_mean"]),
                             "sem": float(obj.loc[pid, f"{m}_sem"])})
        new_df = pd.DataFrame(rows)
        assert len(matched) == n_articles == 44, (len(matched), n_articles)
        assert new_df["mean"].notna().all() and (new_df["sem"] > 0).all()
        experiment.add_tracking_metrics(
            [Metric(name=m, lower_is_better=True) for m in PAIRS["payload"]])
        data = Data(df=new_df)

    keep = {
        "twelve-param": None,
        "six-param": PARAM_NAMES + [mass_param],
        "shape-only": list(PARAM_NAMES),
    }[space]
    if keep is not None:
        from ax.core.search_space import SearchSpace

        base_space = fit_search_space(include_process=False)
        experiment._search_space = SearchSpace(
            parameters=[base_space.parameters[name] for name in keep])
        for arm in experiment.arms_by_name.values():
            arm._parameters = {k: arm._parameters[k] for k in keep}
        if experiment.status_quo is not None:
            sq = experiment.status_quo
            sq._parameters = {k: v for k, v in sq._parameters.items() if k in keep}
    return experiment, data, labels_by_arm, keep, n_articles


def run_fit(campaign_bo, space, pair, seed, num_samples, warmup_steps):
    """One full-data fit; returns the checkpoint record."""
    import torch
    import t3_prism_bo_diagnostics as diag

    experiment, data, labels_by_arm, keep, n_articles = build_experiment(
        campaign_bo, space, pair)
    metrics = list(PAIRS[pair])
    torch.manual_seed(seed)
    t0 = time.time()
    model = diag.fit_saasbo(
        experiment, data, num_samples, warmup_steps, refit_on_cv=True)
    fit_s = time.time() - t0
    assert set(model.outcomes) == set(metrics), model.outcomes
    if keep is not None:
        assert set(model.parameters) == set(keep), model.parameters

    training = model.get_training_data()
    assert len(training) == n_articles == 44, (
        f"expected 44 training observations, got {len(training)}")

    # 1. importances: Ax's median value + quantiles across the NUTS draws
    draws = diag.per_draw_importances(model)
    params = list(model.parameters)
    importance = {}
    for metric in metrics:
        ax_values = model.feature_importances(metric)
        qs = np.percentile(draws[metric], [5, 25, 50, 75, 95], axis=0)
        importance[metric] = {
            "ax": {p: float(ax_values[p]) for p in params},
            "q05": {p: float(qs[0][j]) for j, p in enumerate(params)},
            "q25": {p: float(qs[1][j]) for j, p in enumerate(params)},
            "q50": {p: float(qs[2][j]) for j, p in enumerate(params)},
            "q75": {p: float(qs[3][j]) for j, p in enumerate(params)},
            "q95": {p: float(qs[4][j]) for j, p in enumerate(params)},
        }

    # 2. in-sample posterior predictions at every training article
    # (fresh ObservationFeatures: Ax transforms mutate features in place)
    from ax.core.observation import ObservationFeatures

    feats = [ObservationFeatures(parameters=dict(obs.features.parameters))
             for obs in training]
    f_mean, f_cov = model.predict(feats)
    insample = []
    for i, obs in enumerate(training):
        names = list(obs.data.metric_names)
        for metric in metrics:
            j = names.index(metric)
            insample.append({
                "arm_name": obs.arm_name,
                "print_id": labels_by_arm.get(obs.arm_name, obs.arm_name),
                "metric": metric,
                "observed": float(obs.data.means[j]),
                "observed_sem": float(np.sqrt(obs.data.covariance[j, j])),
                "predicted": float(f_mean[metric][i]),
                "predicted_sd": float(np.sqrt(f_cov[metric][metric][i])),
            })

    return {
        "key": f"{space}|{pair}|{seed}",
        "space": space,
        "pair": pair,
        "metrics": metrics,
        "seed": seed,
        "n_params": len(params),
        "parameters": params,
        "n_articles": n_articles,
        "num_samples": num_samples,
        "warmup_steps": warmup_steps,
        "fit_seconds": round(fit_s, 1),
        "importance": importance,
        "insample": insample,
    }


# ---- scoring + rendering --------------------------------------------------

def _logo_reference():
    """Held-out LOGO article-level stats for every (space, pair, metric)."""
    abl = json.loads((AUDIT_DIR / "metrics-param-ablation.json").read_text())
    pay = json.loads((AUDIT_DIR / "metrics-payload-objective.json").read_text())
    ref = {}
    for space in SPACES:
        for metric in PAIRS["campaign"]:
            ref[(space, "campaign", metric)] = abl["runs"][space]["article_level"][metric]
    for space in ("twelve-param", "shape-only"):
        for metric in PAIRS["payload"]:
            ref[(space, "payload", metric)] = pay["payload_runs"][space][metric]
    return ref


def _insample_stats(rows):
    from scipy import stats

    obs = np.array([r["observed"] for r in rows])
    pred = np.array([r["predicted"] for r in rows])
    sd = np.array([r["predicted_sd"] for r in rows])
    resid = pred - obs
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((obs - obs.mean()) ** 2))
    rho, _ = stats.spearmanr(obs, pred)
    return {
        "n": len(rows),
        "r2_insample": 1.0 - ss_res / ss_tot,
        "spearman_insample": float(rho),
        "rmse_insample": float(np.sqrt(np.mean(resid ** 2))),
        "shrinkage_sd_pred_over_sd_obs": float(np.std(pred, ddof=1)
                                               / np.std(obs, ddof=1)),
        "coverage_95_insample_pct": float(
            100.0 * np.mean(np.abs(resid) <= 1.96 * sd)),
        "median_posterior_sd": float(np.median(sd)),
        "sd_observed": float(np.std(obs, ddof=1)),
    }


def load_records():
    recs = {}
    with FITS_PATH.open() as fh:
        for line in fh:
            r = json.loads(line)
            recs[r["key"]] = r
    return recs


def write_tables(recs):
    imp_rows, ins_rows = [], []
    for r in recs.values():
        for metric in r["metrics"]:
            imp = r["importance"][metric]
            for p in r["parameters"]:
                imp_rows.append({
                    "space": r["space"], "pair": r["pair"], "seed": r["seed"],
                    "metric": metric, "parameter": p,
                    "importance": imp["ax"][p],
                    "q05": imp["q05"][p], "q25": imp["q25"][p],
                    "median_per_draw": imp["q50"][p],
                    "q75": imp["q75"][p], "q95": imp["q95"][p],
                })
        for row in r["insample"]:
            ins_rows.append({"space": r["space"], "pair": r["pair"],
                             "seed": r["seed"], **row})
    pd.DataFrame(imp_rows).to_csv(OUT_DIR / "feature-importance.csv",
                                  index=False, float_format="%.5f")
    pd.DataFrame(ins_rows).to_csv(OUT_DIR / "insample-predictions.csv",
                                  index=False, float_format="%.5f")


ROW_ORDER = [("campaign", "t180"), ("campaign", "e_reb_mJ"),
             ("payload", "tavg10ms"), ("payload", "late_avg3ms_g")]


def render_importance(recs, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    fig, axes = plt.subplots(4, 3, figsize=(13.2, 16.2), sharex=True)
    xmax = 0.0
    for (pair, metric), axrow in zip(ROW_ORDER, axes):
        for space, ax in zip(SPACES, axrow):
            rec = recs.get(f"{space}|{pair}|{CANONICAL_SEED}")
            if rec is None:
                ax.axis("off")
                continue
            imp = rec["importance"][metric]
            params = [p for p in PARAM_ORDER if p in rec["parameters"]]
            y = [PARAM_ORDER.index(p) for p in params]
            vals = [imp["ax"][p] for p in params]
            med = [imp["q50"][p] for p in params]
            lo = [max(imp["q50"][p] - imp["q25"][p], 0) for p in params]
            hi = [max(imp["q75"][p] - imp["q50"][p], 0) for p in params]
            xmax = max(xmax, max(imp["q75"][p] for p in params))
            ax.barh(y, vals, height=0.62, zorder=3,
                    color=[GROUP_COLOR[GROUP_OF[p]] for p in params])
            ax.errorbar(med, y, xerr=[lo, hi], fmt="none", ecolor="0.15",
                        elinewidth=1.2, capsize=3, zorder=4)
            # realization-noise probes: repeat-seed values as open circles
            for seed in SEED_REPEATS.get((space, pair), []):
                rep = recs.get(f"{space}|{pair}|{seed}")
                if rep is not None:
                    rimp = rep["importance"][metric]
                    ax.scatter([rimp["ax"][p] for p in params], y, s=22,
                               facecolors="none", edgecolors="0.15",
                               linewidths=1.0, zorder=5)
            ax.axvline(1.0 / len(params), color="0.45", lw=1.1,
                       ls=(0, (4, 4)), zorder=2)
            ax.set_ylim(len(PARAM_ORDER) - 0.4, -0.6)
            ax.set_yticks(range(len(PARAM_ORDER)))
            ax.set_yticklabels(
                [PARAM_LABEL[p] for p in PARAM_ORDER]
                if ax is axrow[0] else [""] * len(PARAM_ORDER), fontsize=9)
            ax.grid(axis="x", color="0.92", lw=0.7, zorder=0)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            if (pair, metric) == ROW_ORDER[0]:
                ax.set_title(SPACE_LABEL[space], fontsize=11.5, pad=10)
        axrow[0].set_ylabel(OBJ_LABEL[metric], fontsize=11,
                            color=OBJ_COLOR[metric], labelpad=8)
    for ax in axes[-1]:
        ax.set_xlabel("share of model sensitivity", fontsize=10)
        ax.set_xlim(0, min(1.0, xmax * 1.06))
    handles = [Patch(facecolor=GROUP_COLOR[g], label=GROUP_LEGEND[g])
               for g in ("shape", "mass", "process-article", "process-filament")]
    handles += [
        Line2D([], [], color="0.15", lw=1.2, label="IQR across NUTS draws"),
        Line2D([], [], ls="", marker="o", markerfacecolor="none",
               markeredgecolor="0.15", label="repeat fit, other NUTS seed"),
        Line2D([], [], color="0.45", lw=1.1, ls=(0, (4, 4)),
               label="equal sensitivity (1/n params)"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=4, fontsize=9.5,
               frameon=False, bbox_to_anchor=(0.5, 0.995))
    fig.suptitle(
        "SAAS feature importance, one full-data fit (44 articles) per fit "
        "space and objective\nAx feature_importances: normalized inverse "
        "median lengthscale, NUTS 256/512, seed 10000",
        fontsize=12.5, y=1.028)
    fig.text(0.5, -0.008,
             "A blank row means the parameter is not in that fit space "
             "(it is absence, not zero importance).",
             ha="center", fontsize=9.5, color="0.35")
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render_parity(recs, out_path, logo_ref):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(4, 3, figsize=(13.2, 16.6))
    for (pair, metric), axrow in zip(ROW_ORDER, axes):
        for space, ax in zip(SPACES, axrow):
            rec = recs.get(f"{space}|{pair}|{CANONICAL_SEED}")
            if rec is None:
                ax.axis("off")
                continue
            rows = [r for r in rec["insample"] if r["metric"] == metric]
            obs = np.array([r["observed"] for r in rows])
            osem = np.array([r["observed_sem"] for r in rows])
            pred = np.array([r["predicted"] for r in rows])
            sd = np.array([r["predicted_sd"] for r in rows])
            color = OBJ_COLOR[metric]
            ax.errorbar(obs, pred, yerr=2 * sd, xerr=2 * osem, fmt="none",
                        ecolor="0.82", elinewidth=0.9, zorder=2)
            ax.scatter(obs, pred, s=26, color=color, alpha=0.85, zorder=3,
                       edgecolors="white", linewidths=0.4)
            lims = [min(np.min(obs - 2 * osem), np.min(pred - 2 * sd)),
                    max(np.max(obs + 2 * osem), np.max(pred + 2 * sd))]
            pad = 0.04 * (lims[1] - lims[0])
            lims = [lims[0] - pad, lims[1] + pad]
            ax.plot(lims, lims, ls="--", lw=1, color="0.6", zorder=1)
            ax.set_xlim(lims), ax.set_ylim(lims)
            ax.set_aspect("equal")
            ax.grid(color="0.92", lw=0.7, zorder=0)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            s = _insample_stats(rows)
            ref = logo_ref.get((space, pair, metric))
            if ref is not None:
                logo_txt = (f"held-out LOGO: $\\rho_s$ {ref['spearman_rho']:+.2f}"
                            f" (p {ref['spearman_p_perm']:.3g}), "
                            f"$R^2_{{oos}}$ {ref['R2_oos_vs_fold_train_mean']:+.2f}")
            else:
                logo_txt = "held-out LOGO: not run for this combination"
            ax.annotate(
                f"in-sample: $R^2$ {s['r2_insample']:+.2f}, "
                f"$\\rho_s$ {s['spearman_insample']:+.2f}\n"
                f"sd(pred)/sd(obs) {s['shrinkage_sd_pred_over_sd_obs']:.2f}, "
                f"95% cov {s['coverage_95_insample_pct']:.0f}%\n" + logo_txt,
                xy=(0.03, 0.97), xycoords="axes fraction", va="top",
                fontsize=8.2,
                bbox=dict(facecolor="white", alpha=0.9, edgecolor="0.8", pad=3))
            if (pair, metric) == ROW_ORDER[0]:
                ax.set_title(SPACE_LABEL[space], fontsize=11.5, pad=10)
            if ax is axrow[0]:
                ax.set_ylabel(f"{OBJ_LABEL[metric]}\npredicted (2 sd bars)",
                              fontsize=10, color=OBJ_COLOR[metric])
            if (pair, metric) == ROW_ORDER[-1]:
                ax.set_xlabel("observed (2 SEM bars)", fontsize=10)
    fig.suptitle(
        "In-sample parity, one full-data fit (44 articles) per fit space and "
        "objective\nposterior mean and sd at the training points, NUTS "
        "256/512, seed 10000; held-out LOGO stats quoted for contrast",
        fontsize=12.5, y=0.998)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def write_metrics(recs, logo_ref):
    out = {
        "protocol": {
            "data": "round-5 snapshot, all 44 articles, nothing held out",
            "nuts": "256 samples / 512 warmup (library default)",
            "seed": ("torch.manual_seed(10000) before each fit, the same "
                     "state as the LOGO reruns' shared initial fit; repeat "
                     "seeds 11 and 12 on two combinations quantify NUTS "
                     "realization noise"),
            "campaign_code_commit": "bbf7a62",
            "importance": ("Ax feature_importances (normalized inverse median "
                           "SAAS lengthscale over MCMC draws) + per-draw "
                           "quantiles via per_draw_importances"),
        },
        "fits": {},
        "seed_repeats": {},
    }
    for key, rec in sorted(recs.items()):
        if rec["seed"] != CANONICAL_SEED:
            continue
        entry = {"n_params": rec["n_params"], "fit_seconds": rec["fit_seconds"],
                 "metrics": {}}
        for metric in rec["metrics"]:
            rows = [r for r in rec["insample"] if r["metric"] == metric]
            stats_ = _insample_stats(rows)
            imp = rec["importance"][metric]
            top = sorted(imp["ax"].items(), key=lambda kv: -kv[1])[:3]
            ref = logo_ref.get((rec["space"], rec["pair"], metric))
            entry["metrics"][metric] = {
                "insample": stats_,
                "top_importances": [
                    {"parameter": p, "importance": round(v, 4),
                     "iqr": [round(imp["q25"][p], 4), round(imp["q75"][p], 4)]}
                    for p, v in top],
                "logo_heldout_article_level": (
                    {k: ref[k] for k in ("spearman_rho", "spearman_p_perm",
                                         "R2_oos_vs_fold_train_mean",
                                         "shrinkage_sd_pred_over_sd_obs")}
                    if ref else None),
            }
        out["fits"][key] = entry
    # realization noise: canonical vs repeat seeds
    for (space, pair), seeds in SEED_REPEATS.items():
        base = recs.get(f"{space}|{pair}|{CANONICAL_SEED}")
        if base is None:
            continue
        deltas = {}
        for metric in base["metrics"]:
            base_imp = base["importance"][metric]["ax"]
            base_rows = [r for r in base["insample"] if r["metric"] == metric]
            base_stats = _insample_stats(base_rows)
            d_imp, d_rho, d_r2 = [], [], []
            for seed in seeds:
                rep = recs.get(f"{space}|{pair}|{seed}")
                if rep is None:
                    continue
                rep_imp = rep["importance"][metric]["ax"]
                d_imp.append(max(abs(rep_imp[p] - base_imp[p])
                                 for p in base["parameters"]))
                rep_rows = [r for r in rep["insample"] if r["metric"] == metric]
                rep_stats = _insample_stats(rep_rows)
                d_rho.append(rep_stats["spearman_insample"]
                             - base_stats["spearman_insample"])
                d_r2.append(rep_stats["r2_insample"] - base_stats["r2_insample"])
            if d_imp:
                deltas[metric] = {
                    "max_abs_importance_shift": round(max(d_imp), 4),
                    "insample_spearman_shift": [round(v, 4) for v in d_rho],
                    "insample_r2_shift": [round(v, 4) for v in d_r2],
                }
        out["seed_repeats"][f"{space}|{pair}"] = {
            "seeds": seeds, "deltas_vs_seed_10000": deltas}
    METRICS_OUT.write_text(json.dumps(out, indent=2) + "\n")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign-bo", type=Path, required=True)
    ap.add_argument("--num-samples", type=int, default=256)
    ap.add_argument("--warmup-steps", type=int, default=512)
    ap.add_argument("--max-seconds", type=float, default=3000)
    ap.add_argument("--commit-each-fit", action="store_true")
    ap.add_argument("--plot-only", action="store_true")
    ap.add_argument("--smoke", action="store_true",
                    help="plumbing check: tiny NUTS, two combos, /tmp output")
    args = ap.parse_args(argv)
    t_start = time.time()

    global OUT_DIR, STATE_PATH, FITS_PATH, METRICS_OUT, FIGS
    combos = [(s, p, CANONICAL_SEED) for p in PAIRS for s in SPACES]
    combos += [(s, p, seed) for (s, p), seeds in SEED_REPEATS.items()
               for seed in seeds]
    if args.smoke:
        OUT_DIR = Path("/tmp/full-fit-SMOKE")
        FIGS = OUT_DIR
        METRICS_OUT = OUT_DIR / "metrics-full-fit.json"
        STATE_PATH, FITS_PATH = OUT_DIR / "state.json", OUT_DIR / "fits.jsonl"
        args.num_samples, args.warmup_steps = 16, 32
        combos = [("twelve-param", "campaign", CANONICAL_SEED),
                  ("shape-only", "payload", CANONICAL_SEED),
                  ("twelve-param", "campaign", 11)]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(args.campaign_bo.resolve()))

    if not args.plot_only:
        if STATE_PATH.exists():
            state = json.loads(STATE_PATH.read_text())
            if (state["num_samples"], state["warmup_steps"]) != (
                    args.num_samples, args.warmup_steps):
                raise RuntimeError("NUTS settings changed between invocations")
        else:
            state = {
                "num_samples": args.num_samples,
                "warmup_steps": args.warmup_steps,
                "canonical_seed": CANONICAL_SEED,
                "seed_repeats": {f"{s}|{p}": seeds
                                 for (s, p), seeds in SEED_REPEATS.items()},
                "snapshot": "t3-prism-bo-ax-client-round5.json",
                "campaign_branch": "claude/issue-98-20260821-0103",
                "campaign_code_commit": "bbf7a62",
                "objectives_csv": OBJECTIVES_CSV.name,
                "fit_seconds": {},
                "status": "running",
            }
        done = set()
        if FITS_PATH.exists():
            with FITS_PATH.open() as fh:
                done = {json.loads(line)["key"] for line in fh}
        print(f"{len(combos)} fits planned; {len(done)} already checkpointed",
              flush=True)

        slowest = 0.0
        for space, pair, seed in combos:
            key = f"{space}|{pair}|{seed}"
            if key in done:
                continue
            elapsed = time.time() - t_start
            if done and elapsed + max(slowest, 120.0) > args.max_seconds:
                state["status"] = "resume_needed"
                STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
                print(f"RESUME_NEEDED: {len(done)}/{len(combos)} fits done, "
                      f"{elapsed:.0f} s elapsed", flush=True)
                return 0
            print(f"fit {key} ...", flush=True)
            rec = run_fit(args.campaign_bo, space, pair, seed,
                          args.num_samples, args.warmup_steps)
            slowest = max(slowest, rec["fit_seconds"])
            with FITS_PATH.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            state["fit_seconds"][key] = rec["fit_seconds"]
            STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
            done.add(key)
            print(f"    {key}: {rec['fit_seconds']:.0f} s", flush=True)
            if args.commit_each_fit:
                _git_commit_push(
                    [FITS_PATH, STATE_PATH],
                    f"Full-data fit {len(done)}/{len(combos)}: {key} "
                    f"at {args.num_samples}/{args.warmup_steps}")
        if len(done) < len(combos):
            return 0
        state["status"] = "complete"
        STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")

    # ---- assembly: tables, metrics, figures ------------------------------
    recs = load_records()
    if args.smoke:
        rec = next(iter(recs.values()))
        assert len(rec["insample"]) == 44 * 2
        for metric in rec["metrics"]:
            tot = sum(rec["importance"][metric]["ax"].values())
            assert abs(tot - 1.0) < 1e-6, tot
        logo_ref = _logo_reference()
        write_tables(recs)
        render_importance(recs, FIGS / "full-fit-feature-importance.png")
        render_parity(recs, FIGS / "full-fit-parity.png", logo_ref)
        write_metrics(recs, logo_ref)
        print("SMOKE_OK: fits ran, importances normalized, figures rendered",
              flush=True)
        return 0
    logo_ref = _logo_reference()
    write_tables(recs)
    render_importance(recs, FIGS / "full-fit-feature-importance.png")
    render_parity(recs, FIGS / "full-fit-parity.png", logo_ref)
    out = write_metrics(recs, logo_ref)
    for key, entry in out["fits"].items():
        for metric, m in entry["metrics"].items():
            print(f"  {key} {metric}: in-sample R2 "
                  f"{m['insample']['r2_insample']:+.3f}, rho_s "
                  f"{m['insample']['spearman_insample']:+.3f}, top "
                  f"{m['top_importances'][0]['parameter']}", flush=True)
    print("ALL_FITS_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
