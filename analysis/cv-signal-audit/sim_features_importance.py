"""Which inputs does the widened model actually use? Full-data SAASBO fits
in the simulation-feature spaces, with Ax's lengthscale importances.

Companion to ``rerun_logocv_sim_features.py`` (Section 12). One fit per
(variant, objective pair) on all 44 articles, nothing held out, 256/512
NUTS, ``torch.manual_seed(10000)``, the Section 8 convention: importance
is Ax's ``feature_importances`` (inverse median ARD lengthscale,
normalized over the parameters) and the whiskers are the interquartile
range of the per-draw normalized inverse lengthscales across the 256
retained MCMC draws. In-sample R2 and 95 percent coverage are recorded
alongside so the Section 8 memorization check can be repeated for these
spaces.

Usage (repo root; campaign ``bo/`` tree extracted at ``bbf7a62``)::

    python analysis/cv-signal-audit/sim_features_importance.py \
        --campaign-bo /tmp/campaign/bo --threads 1

Outputs: ``data/sim-features-importance.csv`` (tidy, one row per
variant, metric, parameter) with the in-sample statistics in
``data/sim-features-importance-insample.csv``, and
``figures/sim-features-importance.png``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

AUDIT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(AUDIT_DIR))
from rerun_logocv_sim_features import (  # noqa: E402
    FEATURES, FEATURES_CSV, PAYLOAD, PAYLOAD_CSV, VARIANTS, feature_bounds,
)

OUT_CSV = AUDIT_DIR / "data" / "sim-features-importance.csv"
OUT_INSAMPLE = AUDIT_DIR / "data" / "sim-features-importance-insample.csv"
OUT_FIG = AUDIT_DIR / "figures" / "sim-features-importance.png"
COMBOS = (("shape-sim", "campaign"), ("twelve-sim", "campaign"),
          ("sim-only", "campaign"), ("shape-sim", "payload"))
SHORT = {"R_mm": "R", "H_mm": "H", "twist_deg": "twist", "strut_d_mm": "strut d",
         "cable_d_mm": "cable d", "mass_printed_g": "mass",
         "strut_infill_pct": "strut infill", "tpu_infill_pct": "TPU infill",
         "pla_nozzle_temp_C": "PLA temp", "pla_flow_mm3_s": "PLA flow",
         "tpu_nozzle_temp_C": "TPU temp", "tpu_flow_mm3_s": "TPU flow",
         "sim_tierC_t180": "sim C t180", "sim_tierC_tendon_energy_mJ": "sim C tendon E",
         "sim_tierC_stroke_mm": "sim C stroke", "sim_tierB_t180": "sim B t180",
         "sim_tierB_fn_hz": "sim B fn", "sim_tierB_zeta_pct": "sim B zeta"}
METRIC_TITLE = {"t180": "t180", "e_reb_mJ": "rebound (mJ)",
                "tavg10ms": "tavg10ms", "late_avg3ms_g": "late_avg3ms"}


def build(args, variant_name, objectives):
    """The driver's experiment setup, for a full fit (no folds)."""
    import torch

    sys.path.insert(0, str(args.campaign_bo.resolve()))
    import t3_prism_bo_diagnostics as diag  # noqa: E402
    from ax.core.parameter import ParameterType, RangeParameter
    from ax.core.search_space import SearchSpace
    from ax.service.ax_client import AxClient
    from t3_prism_bo_campaign import (  # noqa: E402
        BO_DIR, PARAM_NAMES, fit_search_space, load_round2_training_data,
        load_round3_reprint_training_data, load_round3_training_data,
        load_round4_training_data, load_training_data,
    )

    variant = VARIANTS[variant_name]
    snapshot = args.campaign_bo / "t3-prism-bo-ax-client-round5.json"
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

    if objectives == "campaign":
        names = tuple(sorted(data.df["metric_name"].unique()))
    else:
        from ax.core.data import Data
        from ax.core.metric import Metric

        names = PAYLOAD
        table = pd.read_csv(PAYLOAD_CSV).set_index("print_id")
        seen = data.df[["trial_index", "arm_name"]].drop_duplicates()
        rows = []
        for r in seen.itertuples():
            pid = labels_by_arm[r.arm_name]
            for n in names:
                rows.append({"trial_index": int(r.trial_index),
                             "arm_name": r.arm_name, "metric_name": n,
                             "mean": float(table.loc[pid, f"{n}_mean"]),
                             "sem": float(table.loc[pid, f"{n}_sem"])})
        known = set(experiment.metrics)
        experiment.add_tracking_metrics(
            [Metric(name=n, lower_is_better=True) for n in names if n not in known])
        data = Data(df=pd.DataFrame(rows))

    base_space = fit_search_space(include_process=True)
    keep = (list(PARAM_NAMES) if variant["base"] == "shape"
            else list(base_space.parameters) if variant["base"] == "twelve"
            else [])
    feats = list(FEATURES) if variant["features"] else []
    ftable = pd.read_csv(FEATURES_CSV).set_index("print_id")
    bounds = feature_bounds(ftable)
    tested = set(data.df["arm_name"])
    placeholder = {f: float(ftable[f].mean()) for f in feats}
    params = [base_space.parameters[name] for name in keep] + [
        RangeParameter(name=f, parameter_type=ParameterType.FLOAT,
                       lower=bounds[f][0], upper=bounds[f][1]) for f in feats]
    experiment._search_space = SearchSpace(parameters=params)
    for name, arm in experiment.arms_by_name.items():
        new = {k: arm._parameters[k] for k in keep}
        if feats:
            new.update(placeholder if name not in tested
                       else {f: float(ftable.loc[labels_by_arm[name], f])
                             for f in feats})
        arm._parameters = new
    if experiment.status_quo is not None:
        sq = experiment.status_quo
        sq._parameters = dict(experiment.arms_by_name[sq.name]._parameters)

    torch.manual_seed(10_000)
    model = diag.fit_saasbo(experiment, data, args.num_samples,
                            args.warmup_steps, refit_on_cv=False)
    assert len(model.get_training_data()) == n_articles
    return model, diag, names, labels_by_arm, keep + feats


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign-bo", type=Path, required=True)
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--num-samples", type=int, default=256)
    ap.add_argument("--warmup-steps", type=int, default=512)
    ap.add_argument("--figure-only", action="store_true")
    args = ap.parse_args(argv)

    if not args.figure_only:
        import torch

        if args.threads:
            torch.set_num_threads(args.threads)
        rows, insample = [], []
        for variant_name, objectives in COMBOS:
            t0 = time.time()
            model, diag, names, labels_by_arm, params = build(
                args, variant_name, objectives)
            draws = diag.per_draw_importances(model)
            for metric in names:
                ax_imp = model.feature_importances(metric)
                q25, q50, q75 = np.percentile(draws[metric], [25, 50, 75], axis=0)
                for j, p in enumerate(params):
                    rows.append({"variant": variant_name, "objectives": objectives,
                                 "metric": metric, "parameter": p,
                                 "importance": float(ax_imp[p]),
                                 "draw_q25": float(q25[j]), "draw_q50": float(q50[j]),
                                 "draw_q75": float(q75[j])})
            # in-sample parity at the training points
            obs_feats = [o.features for o in model.get_training_data()]
            preds = model.predict(obs_feats)
            for metric in names:
                y = np.array([o.data.means[list(o.data.metric_names).index(metric)]
                              for o in model.get_training_data()])
                mu = np.asarray(preds[0][metric])
                sd = np.sqrt(np.asarray(preds[1][metric][metric]))
                resid = y - mu
                insample.append({
                    "variant": variant_name, "objectives": objectives,
                    "metric": metric, "n": len(y),
                    "R2_insample": float(1 - resid.var() / y.var()),
                    "coverage_95_pct": float(np.mean(np.abs(resid) <= 1.96 * sd) * 100),
                    "median_posterior_sd_over_sd_obs": float(np.median(sd) / y.std(ddof=1)),
                    "seconds": round(time.time() - t0, 1)})
            print(f"{variant_name} / {objectives}: {len(params)} params, "
                  f"{time.time() - t0:.0f} s", flush=True)
            for metric in names:
                top = sorted(((r["importance"], r["parameter"]) for r in rows
                              if r["variant"] == variant_name
                              and r["objectives"] == objectives
                              and r["metric"] == metric), reverse=True)[:4]
                print(f"  {metric}: " + ", ".join(f"{p} {v:.2f}" for v, p in top),
                      flush=True)
        pd.DataFrame(rows).to_csv(OUT_CSV, index=False, float_format="%.6g")
        pd.DataFrame(insample).to_csv(OUT_INSAMPLE, index=False, float_format="%.6g")

    imp = pd.read_csv(OUT_CSV)
    combos = [(v, o) for v, o in COMBOS
              if ((imp.variant == v) & (imp.objectives == o)).any()]
    fig, axes = plt.subplots(len(combos), 2, figsize=(11, 2.9 * len(combos)),
                             squeeze=False)
    for i, (v, o) in enumerate(combos):
        sub = imp[(imp.variant == v) & (imp.objectives == o)]
        for j, metric in enumerate(sorted(sub.metric.unique(),
                                          key=lambda m: list(METRIC_TITLE).index(m))):
            ax = axes[i, j]
            s = sub[sub.metric == metric].sort_values("importance", ascending=True)
            colors = ["#c1553b" if p.startswith("sim_") else "#3b6ea5"
                      for p in s.parameter]
            ax.barh(range(len(s)), s.importance, color=colors, alpha=0.85)
            ax.errorbar(s.draw_q50, range(len(s)),
                        xerr=[s.draw_q50 - s.draw_q25, s.draw_q75 - s.draw_q50],
                        fmt="none", ecolor="0.3", lw=1, capsize=2)
            ax.set_yticks(range(len(s)))
            ax.set_yticklabels([SHORT.get(p, p) for p in s.parameter], fontsize=8)
            ax.set_title(f"{v}, {METRIC_TITLE[metric]}", fontsize=9.5)
            ax.set_xlabel("normalized inverse lengthscale (Ax importance)",
                          fontsize=8)
            ax.grid(color="0.92", lw=0.7, zorder=0)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
    fig.suptitle("Full-data SAASBO fits: simulation features (red) next to the "
                 "fit coordinates (blue); whiskers = IQR across 256 NUTS draws",
                 fontsize=10.5, y=1.0)
    fig.tight_layout()
    OUT_FIG.parent.mkdir(exist_ok=True)
    fig.savefig(OUT_FIG, dpi=150, bbox_inches="tight")
    print(f"wrote {OUT_CSV}, {OUT_INSAMPLE}, {OUT_FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
