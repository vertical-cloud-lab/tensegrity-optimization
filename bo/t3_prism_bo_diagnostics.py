"""Interpretability diagnostics for the T-3_01 SAASBO model (PR #102).

The Honegumi template's ``visualize=True`` block is a single Pareto scatter and
nothing else, so everything here is built on Ax's own diagnostic API at the
pinned version (ax-platform 0.5.0) rather than on the template:

1. **Feature importance (inverse lengthscales).**
   ``TorchModelBridge.feature_importances(metric_name)`` reads the fitted
   kernel's ARD lengthscales, takes the **median over the SAAS MCMC draws**,
   inverts, and normalizes so the five parameters sum to 1
   (``ax/models/torch/botorch.py::get_feature_importances_from_botorch_model``
   at tag 0.5.0). Because Ax's ``MBM_X_trans`` maps the search space onto the
   unit cube before fitting, those lengthscales are already in comparable
   units, so the normalized values are directly readable as "share of the
   model's sensitivity". This script plots Ax's own numbers as the bars, and
   adds an interquartile band computed from the **per-draw** normalized
   inverse lengthscales, which the single-number Ax API throws away. With 7
   training points that spread is the honest part of the picture: SAAS's
   sparsity prior shrinks most dimensions, and the band shows how firmly.

2. **Leave-one-out cross-validation.**
   ``ax.modelbridge.cross_validation.cross_validate(model, folds=-1)`` refits
   the model once per held-out arm and predicts it;
   ``compute_diagnostics`` scores the result. Two caveats that matter at this
   sample size, both stated on the figure rather than buried here: LOO on
   n = 7 is noisy, and each fold refits the full NUTS chain, so the folds run
   at reduced MCMC settings (see ``--cv-mcmc-samples``).

3. **Signed parameter effects.**
   Neither Ax 0.5.0 nor Honegumi ships a "does raising this parameter raise or
   lower this metric" plot: ``ax.plot.marginal_effects`` is for factorial
   (categorical) designs, and ``plot_slice`` holds the other parameters at one
   fixed point, which for a 5-D space with 7 points reads very differently
   depending on where you fix them. This script instead computes a
   model-based **partial dependence**: sweep one parameter across its range
   while averaging the posterior mean over quasi-random draws of the other
   four, which is the continuous analogue of a main effect. The net effect
   (value at the top of the range minus value at the bottom) is then drawn as
   a signed tornado, so "increasing twist lowers t180" is legible at a glance.
   Partial dependence assumes the swept parameter is roughly independent of
   the others, which holds here because the search space is a plain box, and
   it does not show interactions; the swept curves are plotted alongside the
   tornado so a non-monotonic parameter is visible rather than averaged away.

Usage (from the repo root)::

    pip install ax-platform==0.5.0 pandas matplotlib
    python bo/t3_prism_bo_diagnostics.py                 # all three figures
    python bo/t3_prism_bo_diagnostics.py --skip-cv       # fast, no LOO refits
    python bo/t3_prism_bo_diagnostics.py --mcmc-samples 128 --warmup-steps 256
    python bo/t3_prism_bo_diagnostics.py --plot-only      # restyle, no refit

By default the model is refit from the committed AxClient snapshot
(``t3-prism-bo-ax-client-round1.json``), so the diagnostics describe the same
data and the same model class that produced the committed round-2 suggestions.
NUTS is stochastic, so importances move by a percentage point or two between
runs; that is smaller than the interquartile bands drawn.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t3_prism_bo_campaign import (  # noqa: E402  (same directory)
    BO_DIR,
    FIGURE_DPI,
    FIG_RC,
    INK,
    LABEL_GRAY,
    DESIGN_PARAMS,
    fit_parameters,
    fit_search_space,
    obj1_name,
    obj2_name,
    mass_param,
    load_training_data,
    _label_points,
)

# Both objectives. Printed mass used to be a third (tracking) metric; it is a
# search-space parameter now (PR #102 constant-printed-mass change), so it
# appears on the parameter axis of every figure here instead of the metric one.
METRIC_ORDER = [obj1_name, obj2_name]

METRIC_LABEL = {
    obj1_name: "t180\n(transmissibility)",
    obj2_name: "Rebound energy\n(mJ per drop)",
}
METRIC_SHORT = {obj1_name: "t180", obj2_name: "rebound (mJ)"}
# One-line variants, for panels whose horizontal axis label sits at the same
# height as the title (the LOOCV grid).
METRIC_TITLE = {
    obj1_name: "t180 (transmissibility)",
    obj2_name: "Rebound energy (mJ per drop)",
}
METRIC_COLOR = {
    obj1_name: "#2a78d6",
    obj2_name: "#eb6834",
}

# Every figure here sweeps the full design vector, mass included.
PARAM_NAMES = DESIGN_PARAMS

PARAM_LABEL = {
    "R_mm": "R (mm)",
    "H_mm": "H (mm)",
    "twist_deg": "twist (deg)",
    "strut_d_mm": "strut Ø (mm)",
    "cable_d_mm": "cable Ø (mm)",
    mass_param: "printed mass (g)",
}

# Fit-space bounds, not the constant-mass generation slab: the diagnostics
# describe the model that was fitted, and it was fitted on articles spanning
# 18.50 to 22.29 g.
BOUNDS = {p["name"]: tuple(p["bounds"]) for p in fit_parameters()}


# ---- model ---------------------------------------------------------------
def fit_saasbo(experiment, data, num_samples, warmup_steps, refit_on_cv=False):
    """Fit the same SAASBO surrogate the campaign script generates from.

    ``Models.SAASBO`` in 0.5.0 is ``ModularBoTorchModel`` wrapping
    ``SaasFullyBayesianSingleTaskGP``; MCMC settings live on the model config's
    ``mll_options``, not as top-level kwargs (passing them directly raises).

    ``refit_on_cv`` defaults to **False** in Ax 0.5.0
    (``ax/models/torch/botorch_modular/model.py:95``), which means a
    cross-validation fold reconditions on the held-out training set while
    keeping hyperparameters that were fitted on all the data. That leaks the
    held-out point into the kernel and makes LOO look better than it is, so
    the cross-validation fit here sets it True and pays for the NUTS rerun.
    """
    from ax.modelbridge.registry import Models
    from ax.models.torch.botorch_modular.surrogate import ModelConfig, SurrogateSpec
    from botorch.models.fully_bayesian import SaasFullyBayesianSingleTaskGP

    spec = SurrogateSpec(
        model_configs=[
            ModelConfig(
                botorch_model_class=SaasFullyBayesianSingleTaskGP,
                mll_options={"num_samples": num_samples, "warmup_steps": warmup_steps},
            )
        ]
    )
    t0 = time.time()
    model = Models.SAASBO(
        experiment=experiment, data=data, surrogate_spec=spec, refit_on_cv=refit_on_cv
    )
    print(f"  fit in {time.time() - t0:.0f} s ({num_samples} samples / {warmup_steps} warmup)")
    return model


def per_draw_importances(model):
    """Normalized inverse lengthscales for every retained MCMC draw.

    Returns ``{metric: array(n_draws, n_params)}``. Ax's public
    ``feature_importances`` collapses this to a median before normalizing; the
    per-draw view is what makes the SAAS shrinkage visible.
    """
    surrogate = model.model.surrogate.model
    submodels = getattr(surrogate, "models", [surrogate])
    out = {}
    for metric, submodel in zip(model.outcomes, submodels):
        kernel = submodel.covar_module
        ls = getattr(kernel, "base_kernel", kernel).lengthscale
        ls = ls.detach().cpu().numpy().reshape(-1, len(model.parameters))
        inv = 1.0 / ls
        out[metric] = inv / inv.sum(axis=1, keepdims=True)
    return out


# ---- 1. feature importance ----------------------------------------------
def compute_feature_importance(model):
    """Tidy table: Ax's importance per (metric, parameter) plus the MCMC IQR."""
    params = list(model.parameters)
    draws = per_draw_importances(model)

    rows = []
    for metric in METRIC_ORDER:
        ax_values = model.feature_importances(metric)  # Ax's median-based value
        q25, q50, q75 = np.percentile(draws[metric], [25, 50, 75], axis=0)
        for j, name in enumerate(params):
            rows.append(
                {
                    "metric": metric,
                    "parameter": name,
                    "importance": float(ax_values[name]),
                    "q25": float(q25[j]),
                    "q75": float(q75[j]),
                    "median_per_draw": float(q50[j]),
                }
            )
    return pd.DataFrame(rows)


def render_feature_importance(table, out_path):
    params = [p for p in PARAM_NAMES if p in set(table["parameter"])]

    with plt.rc_context(FIG_RC):
        fig, axes = plt.subplots(1, len(METRIC_ORDER), figsize=(6.5 * len(METRIC_ORDER), 6.4),
                                 dpi=FIGURE_DPI, sharex=True, squeeze=False)
        axes = axes[0]
        y = np.arange(len(params))[::-1]
        for ax, metric in zip(axes, METRIC_ORDER):
            sub = table[table.metric == metric].set_index("parameter").loc[params]
            ax.barh(
                y, sub["importance"], height=0.62,
                color=METRIC_COLOR[metric], alpha=0.88, zorder=2,
            )
            ax.errorbar(
                sub["median_per_draw"], y,
                xerr=[
                    (sub["median_per_draw"] - sub["q25"]).clip(lower=0),
                    (sub["q75"] - sub["median_per_draw"]).clip(lower=0),
                ],
                fmt="none", ecolor=INK, elinewidth=1.8, capsize=6, zorder=3,
            )
            ax.set_yticks(y)
            ax.set_yticklabels([PARAM_LABEL[p] for p in params])
            ax.set_title(METRIC_LABEL[metric], fontsize=20, pad=14)
            ax.set_xlim(0, max(0.5, float(table["q75"].max()) * 1.08))
            ax.grid(False)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            ax.axvline(1.0 / len(params), color=LABEL_GRAY, lw=1.4, ls=(0, (4, 4)), zorder=1)

        axes[0].annotate(
            f"equal sensitivity (1/{len(params)})",
            xy=(1.0 / len(params), len(params) - 0.55),
            xytext=(6, 0), textcoords="offset points",
            fontsize=15, color=LABEL_GRAY, va="center",
        )
        for ax in axes:
            ax.set_xlabel("Share of model sensitivity", labelpad=10, fontsize=19)
        fig.text(
            0.5, -0.03,
            "Bars: Ax feature_importances (median SAAS lengthscale, inverted, normalized).\n"
            "Whiskers: interquartile range across MCMC draws. n = 7 tested articles.",
            ha="center", fontsize=15, color=LABEL_GRAY,
        )
        fig.tight_layout()
        fig.savefig(out_path, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
        plt.close(fig)


# ---- 2. leave-one-out cross-validation ----------------------------------
def run_loocv(model, labels_by_arm, diagnostics_path):
    from ax.modelbridge.cross_validation import compute_diagnostics, cross_validate

    t0 = time.time()
    cv_results = cross_validate(model=model, folds=-1)  # -1 == leave-one-out
    print(f"  LOOCV: {len(cv_results)} folds in {time.time() - t0:.0f} s")
    diagnostics = compute_diagnostics(cv_results)

    rows = []
    for result in cv_results:
        arm = result.observed.arm_name
        obs, pred = result.observed.data, result.predicted
        for metric in obs.metric_names:
            i = list(obs.metric_names).index(metric)
            j = list(pred.metric_names).index(metric)
            rows.append(
                {
                    "arm_name": arm,
                    "print_id": labels_by_arm.get(arm, arm),
                    "metric": metric,
                    "observed": float(obs.means[i]),
                    "observed_sem": float(np.sqrt(obs.covariance[i, i])),
                    "predicted": float(pred.means[j]),
                    "predicted_sem": float(np.sqrt(pred.covariance[j, j])),
                }
            )
    table = pd.DataFrame(rows)

    diag_out = {
        name: {k: float(v) for k, v in per_metric.items()}
        for name, per_metric in diagnostics.items()
    }
    diagnostics_path.write_text(json.dumps(diag_out, indent=2, sort_keys=True) + "\n")
    return table, diagnostics


def render_loocv(table, diagnostics, out_path):
    with plt.rc_context(FIG_RC):
        fig, axes = plt.subplots(1, len(METRIC_ORDER), figsize=(6.5 * len(METRIC_ORDER), 6.6),
                                 dpi=FIGURE_DPI, squeeze=False)
        axes = axes[0]
        for ax, metric in zip(axes, METRIC_ORDER):
            sub = table[table.metric == metric]
            lo = float(min(sub.observed.min(), sub.predicted.min()))
            hi = float(max(sub.observed.max(), sub.predicted.max()))
            pad = 0.18 * (hi - lo) if hi > lo else 1.0
            lim = (lo - pad, hi + pad)
            ax.plot(lim, lim, color=LABEL_GRAY, lw=1.6, ls=(0, (5, 5)), zorder=1)
            ax.errorbar(
                sub.observed, sub.predicted,
                xerr=sub.observed_sem, yerr=sub.predicted_sem,
                fmt="o", ms=11, mfc="none", mec=METRIC_COLOR[metric], mew=2.2,
                ecolor=METRIC_COLOR[metric], elinewidth=1.5, capsize=4, zorder=3,
            )
            ax.set_xlim(*lim)
            ax.set_ylim(*lim)
            ax.set_aspect("equal", adjustable="box")
            ax.grid(False)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            ax.set_title(METRIC_TITLE[metric], fontsize=19, pad=16)
            ax.set_xlabel("Measured", labelpad=10, fontsize=19)
            # greedy placement, so the mass panel's near-coincident articles
            # stay legible instead of stacking on one another
            _label_points(ax, sub, "print_id", "observed", "predicted", fontsize=14)

            mape = diagnostics.get("MAPE", {}).get(metric)
            corr = _safe_corr(sub.observed.to_numpy(), sub.predicted.to_numpy())
            note = []
            if mape is not None:
                note.append(f"MAPE {100 * mape:.1f}%")
            if corr is not None:
                note.append(f"r = {corr:.2f}")
            if note:
                # bottom right: the half of the panel the diagonal leaves
                # empty, and the half the point labels do not compete for
                ax.annotate(
                    "   ".join(note),
                    xy=(0.97, 0.04), xycoords="axes fraction",
                    fontsize=16, color=INK, va="bottom", ha="right",
                )
        axes[0].set_ylabel(
            "Predicted", rotation=0, ha="left", va="bottom", fontsize=19,
        )
        axes[0].yaxis.set_label_coords(-0.02, 1.02)
        fig.text(
            0.5, -0.04,
            "Leave-one-out: each article predicted by a model that refit NUTS without it.\n"
            "Dashed line is perfect prediction. n = 7, so read the direction, not the decimals.",
            ha="center", fontsize=15, color=LABEL_GRAY,
        )
        fig.tight_layout()
        fig.savefig(out_path, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
        plt.close(fig)


def _safe_corr(a, b):
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


# ---- 3. signed parameter effects ----------------------------------------
def partial_dependence(model, n_grid=9, n_background=64, seed=0):
    """Model-based partial dependence for each (parameter, metric) pair.

    For each grid value of the swept parameter, the posterior mean is averaged
    over `n_background` quasi-random draws of the other four parameters, so the
    curve is a main effect rather than one arbitrary slice.
    """
    from ax.core.observation import ObservationFeatures

    rng = np.random.default_rng(seed)
    background = np.column_stack(
        [rng.uniform(*BOUNDS[name], size=n_background) for name in PARAM_NAMES]
    )

    features, index = [], []
    grids = {}
    for name in PARAM_NAMES:
        lo, hi = BOUNDS[name]
        grid = np.linspace(lo, hi, n_grid)
        grids[name] = grid
        col = PARAM_NAMES.index(name)
        for value in grid:
            block = background.copy()
            block[:, col] = value
            for row in block:
                features.append(
                    ObservationFeatures(parameters=dict(zip(PARAM_NAMES, map(float, row))))
                )
                index.append((name, float(value)))

    means = {metric: [] for metric in METRIC_ORDER}
    sds = {metric: [] for metric in METRIC_ORDER}
    chunk = 1024
    for start in range(0, len(features), chunk):
        f_mean, f_cov = model.predict(features[start : start + chunk])
        for metric in METRIC_ORDER:
            means[metric].extend(f_mean[metric])
            sds[metric].extend(np.sqrt(np.asarray(f_cov[metric][metric], float)))

    frame = pd.DataFrame(index, columns=["parameter", "value"])
    for metric in METRIC_ORDER:
        frame[metric] = means[metric]
        frame[f"{metric}__sd"] = sds[metric]
    pdp = frame.groupby(["parameter", "value"], as_index=False).mean()
    return pdp, grids


def net_effects(pdp):
    """Signed low-bound-to-high-bound change per (metric, parameter)."""
    rows = []
    for metric in METRIC_ORDER:
        for name in PARAM_NAMES:
            sub = pdp[pdp.parameter == name].sort_values("value")
            values = sub[metric].to_numpy()
            rows.append(
                {
                    "metric": metric,
                    "parameter": name,
                    "net_effect": float(values[-1] - values[0]),
                    "swing": float(values.max() - values.min()),
                    "monotonic": bool(
                        np.all(np.diff(values) >= 0) or np.all(np.diff(values) <= 0)
                    ),
                }
            )
    return pd.DataFrame(rows)


def render_parameter_effects(pdp, net, out_curves, out_tornado):
    """Two figures: the swept curves, and the signed net effect per parameter."""
    with plt.rc_context(FIG_RC):
        fig, axes = plt.subplots(
            len(METRIC_ORDER), len(PARAM_NAMES),
            figsize=(3.5 * len(PARAM_NAMES), 5.5 * len(METRIC_ORDER)), dpi=FIGURE_DPI,
        )
        for i, metric in enumerate(METRIC_ORDER):
            row = pdp[["parameter", "value", metric, f"{metric}__sd"]]
            span = row[metric].max() - row[metric].min()
            band = float(row[f"{metric}__sd"].mean())
            for j, name in enumerate(PARAM_NAMES):
                ax = axes[i, j]
                sub = row[row.parameter == name].sort_values("value")
                # +/- 1 posterior sd, averaged over the background draws: the
                # effect is only worth reading where the curve moves by more
                # than this
                ax.fill_between(
                    sub.value,
                    sub[metric] - sub[f"{metric}__sd"],
                    sub[metric] + sub[f"{metric}__sd"],
                    color=METRIC_COLOR[metric], alpha=0.15, lw=0,
                )
                ax.plot(sub.value, sub[metric], color=METRIC_COLOR[metric], lw=3.2)
                centre = 0.5 * (row[metric].max() + row[metric].min())
                half = max(0.62 * span, 1.15 * band)
                ax.set_ylim(centre - half, centre + half)
                ax.grid(False)
                for side in ("top", "right"):
                    ax.spines[side].set_visible(False)
                ax.tick_params(labelsize=15)
                if i == len(METRIC_ORDER) - 1:
                    ax.set_xlabel(PARAM_LABEL[name], fontsize=18, labelpad=8)
                if j == 0:
                    ax.set_ylabel(METRIC_LABEL[metric], fontsize=17, labelpad=10)
                else:
                    ax.set_yticklabels([])
        fig.text(
            0.5, 0.005,
            "Partial dependence: one parameter swept across its range, the other four averaged "
            "out.\nShared y-scale within a row, so panel slope is comparable. Shaded band is "
            "+/- 1 posterior sd.",
            ha="center", fontsize=15, color=LABEL_GRAY,
        )
        fig.tight_layout(rect=(0, 0.03, 1, 1))
        fig.savefig(out_curves, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    with plt.rc_context(FIG_RC):
        fig, axes = plt.subplots(1, len(METRIC_ORDER), figsize=(6.5 * len(METRIC_ORDER), 6.4),
                                 dpi=FIGURE_DPI, squeeze=False)
        axes = axes[0]
        y = np.arange(len(PARAM_NAMES))[::-1]
        for ax, metric in zip(axes, METRIC_ORDER):
            sub = net[net.metric == metric].set_index("parameter").loc[PARAM_NAMES]
            colors = [
                "#b3352b" if v > 0 else "#2a78d6" for v in sub["net_effect"]
            ]
            ax.barh(y, sub["net_effect"], height=0.62, color=colors, alpha=0.9, zorder=2)
            ax.axvline(0, color=INK, lw=1.6, zorder=3)
            reach = float(np.abs(net[net.metric == metric]["net_effect"]).max())
            ax.set_xlim(-1.9 * reach, 1.9 * reach)
            digits = 3 if metric == obj1_name else 1
            for k, (name, value) in enumerate(zip(PARAM_NAMES, sub["net_effect"])):
                # asterisk rather than the word, so a label on a short bar
                # cannot run back over the parameter names
                text = f"{value:+.{digits}f}"
                if not sub.loc[name, "monotonic"]:
                    text += "*"
                ax.annotate(
                    text,
                    xy=(value, y[k]),
                    xytext=(9 if value > 0 else -9, 0),
                    textcoords="offset points",
                    ha="left" if value > 0 else "right",
                    va="center", fontsize=14, color=INK,
                )
            ax.set_yticks(y)
            ax.set_yticklabels([PARAM_LABEL[p] for p in PARAM_NAMES])
            ax.grid(False)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            ax.set_title(METRIC_LABEL[metric], fontsize=20, pad=14)
            ax.set_xlabel(f"Change in {METRIC_SHORT[metric]}\nlow bound to high bound",
                          fontsize=17, labelpad=10)
        fig.text(
            0.5, -0.06,
            "Bar right (red) = raising the parameter raises the metric; left (blue) = lowers it.\n"
            "Both objectives are minimized, so for t180 and rebound energy, \u2190 is better. "
            "* marks a parameter whose swept curve turns, so the net effect hides it.",
            ha="center", fontsize=15, color=LABEL_GRAY,
        )
        fig.tight_layout()
        fig.savefig(out_tornado, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
        plt.close(fig)


# ---- driver --------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--snapshot",
        type=Path,
        default=BO_DIR / "t3-prism-bo-ax-client-round1.json",
        help="AxClient JSON written by t3_prism_bo_campaign.py",
    )
    ap.add_argument("--results", type=Path, default=BO_DIR / "t3-prism-bo-batch-drop-results.csv")
    ap.add_argument("--design", type=Path, default=BO_DIR / "t3-prism-bo-batch.csv")
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--mcmc-samples", type=int, default=256, help="NUTS samples for the main fit")
    ap.add_argument("--warmup-steps", type=int, default=512)
    ap.add_argument(
        "--cv-mcmc-samples", type=int, default=128,
        help="NUTS samples for the LOO refits (one per held-out article)",
    )
    ap.add_argument("--cv-warmup-steps", type=int, default=256)
    ap.add_argument("--skip-cv", action="store_true", help="skip the leave-one-out refits")
    ap.add_argument(
        "--plot-only",
        action="store_true",
        help=(
            "redraw all three figures from the recorded diagnostic CSVs without "
            "refitting (needs only pandas + matplotlib, ~1 s)"
        ),
    )
    ap.add_argument("--n-grid", type=int, default=9)
    ap.add_argument("--n-background", type=int, default=64)
    args = ap.parse_args(argv)

    fig_dir = BO_DIR / "figures"
    fig_dir.mkdir(exist_ok=True)
    stem = f"t3-prism-bo-round{args.round}"

    if args.plot_only:
        importance = pd.read_csv(BO_DIR / f"{stem}-feature-importance.csv")
        render_feature_importance(importance, fig_dir / f"{stem}-feature-importance.png")
        pdp = pd.read_csv(BO_DIR / f"{stem}-partial-dependence.csv")
        net = pd.read_csv(BO_DIR / f"{stem}-parameter-net-effects.csv")
        render_parameter_effects(
            pdp, net,
            fig_dir / f"{stem}-parameter-effects.png",
            fig_dir / f"{stem}-parameter-net-effects.png",
        )
        cv_path = BO_DIR / f"{stem}-loocv.csv"
        if cv_path.exists():
            cv_table = pd.read_csv(cv_path)
            diagnostics = json.loads((BO_DIR / f"{stem}-loocv-diagnostics.json").read_text())
            render_loocv(cv_table, diagnostics, fig_dir / f"{stem}-loocv.png")
        print(f"Redrew diagnostics figures in {fig_dir}")
        return 0

    from ax.service.ax_client import AxClient

    ax_client = AxClient.load_from_json_file(str(args.snapshot))
    experiment = ax_client.experiment
    # The snapshot was saved with the search space narrowed to the constant-mass
    # generation slab, which would make 9 of 10 articles out of design and drop
    # them from the fit. Diagnostics describe the fitted model, not the next
    # batch, so widen back to the fit space before refitting.
    experiment.search_space = fit_search_space()
    data = experiment.fetch_data()

    # Trial 0..n-1 were attached in the order load_training_data returns, so
    # the arm names map back onto print IDs; verify against the parameters
    # rather than trusting the order.
    _, _, labels, _, _ = load_training_data(args.results, args.design)
    labels_by_arm = {}
    for trial_index, trial in experiment.trials.items():
        if trial_index >= len(labels):
            continue
        arm = trial.arm
        labels_by_arm[arm.name] = labels[trial_index].split(" ")[0]
    print(f"Loaded {args.snapshot.name}: {len(data.df)} observations, "
          f"{len(labels_by_arm)} labeled articles")

    print("Fitting SAASBO for diagnostics...")
    model = fit_saasbo(experiment, data, args.mcmc_samples, args.warmup_steps)

    imp_png = fig_dir / f"{stem}-feature-importance.png"
    importance = compute_feature_importance(model)
    render_feature_importance(importance, imp_png)
    importance.to_csv(BO_DIR / f"{stem}-feature-importance.csv", index=False,
                      float_format="%.4f")
    print(f"\nFeature importance (share of model sensitivity) -> {imp_png}")
    print(
        importance.pivot(index="parameter", columns="metric", values="importance")
        .loc[PARAM_NAMES, METRIC_ORDER].round(3).to_string()
    )

    print("\nPartial dependence sweep...")
    pdp, _ = partial_dependence(model, n_grid=args.n_grid, n_background=args.n_background)
    curves_png = fig_dir / f"{stem}-parameter-effects.png"
    tornado_png = fig_dir / f"{stem}-parameter-net-effects.png"
    net = net_effects(pdp)
    render_parameter_effects(pdp, net, curves_png, tornado_png)
    pdp.to_csv(BO_DIR / f"{stem}-partial-dependence.csv", index=False, float_format="%.5f")
    net.to_csv(BO_DIR / f"{stem}-parameter-net-effects.csv", index=False, float_format="%.5f")
    print(f"  curves -> {curves_png}\n  tornado -> {tornado_png}")
    for metric in METRIC_ORDER:
        sub = net[net.metric == metric].set_index("parameter").loc[PARAM_NAMES]
        for name, row in sub.iterrows():
            arrow = "raises" if row.net_effect > 0 else "lowers"
            flag = "" if row.monotonic else "  (non-monotonic)"
            print(
                f"  increasing {PARAM_LABEL[name]:<14} {arrow} {METRIC_SHORT[metric]:<14}"
                f" by {abs(row.net_effect):.3f}{flag}"
            )

    if args.skip_cv:
        print("\nLOOCV skipped (--skip-cv).")
        return 0

    print("\nLeave-one-out cross-validation (one refit per article)...")
    # a separate fit, because the folds must genuinely re-run NUTS
    cv_model = fit_saasbo(
        experiment, data, args.cv_mcmc_samples, args.cv_warmup_steps, refit_on_cv=True
    )
    cv_png = fig_dir / f"{stem}-loocv.png"
    cv_table, diagnostics = run_loocv(
        cv_model, labels_by_arm, BO_DIR / f"{stem}-loocv-diagnostics.json"
    )
    render_loocv(cv_table, diagnostics, cv_png)
    cv_table.to_csv(BO_DIR / f"{stem}-loocv.csv", index=False, float_format="%.5f")
    print(f"  figure -> {cv_png}")
    for name in ("MAPE", "Total raw effect", "Fisher exact test p"):
        if name in diagnostics:
            values = {m: round(float(v), 4) for m, v in diagnostics[name].items()}
            print(f"  {name}: {values}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
