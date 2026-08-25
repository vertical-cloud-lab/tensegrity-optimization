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

4. **Parity evolution (before vs after the round-2 data).**
   ``--parity-evolution`` renders two parity panels (predicted vs measured,
   one per objective, +/- 1 sd bars) in which every tested article's
   prediction travels from the plate-generating model's value (commit
   7a048ee, the state that chose the printed batch) to the value from the
   refit trained on all collected data. See the section-4 comment below for
   the provenance of each prediction. Output is three registered stills plus
   a GIF/MP4, same grammar and pixel geometry as the campaign figure sets.

Usage (from the repo root)::

    pip install ax-platform==0.5.0 pandas matplotlib
    python bo/t3_prism_bo_diagnostics.py                 # figures 1-3
    python bo/t3_prism_bo_diagnostics.py --skip-cv       # fast, no LOO refits
    python bo/t3_prism_bo_diagnostics.py --mcmc-samples 128 --warmup-steps 256
    python bo/t3_prism_bo_diagnostics.py --plot-only      # restyle, no refit
    python bo/t3_prism_bo_diagnostics.py --parity-evolution            # figure 4
    python bo/t3_prism_bo_diagnostics.py --parity-evolution --plot-only

By default the model is refit from the committed AxClient snapshot
(``t3-prism-bo-ax-client-round1.json``), so the diagnostics describe the same
data and the same model class that produced the committed round-2 suggestions.
NUTS is stochastic, so importances move by a percentage point or two between
runs; that is smaller than the interquartile bands drawn.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))

from t3_prism_bo_campaign import (  # noqa: E402  (same directory)
    ANIM_DPI,
    ANIM_FIGSIZE,
    BO_DIR,
    FIGURE_DPI,
    FIG_RC,
    GIF_WIDTH_PX,
    INK,
    LABEL_GRAY,
    LEADER_GRAY,
    SUGGEST_ORANGE,
    DESIGN_PARAMS,
    STILL_STAGES,
    W_LEADER,
    W_LINE,
    W_TEXT,
    fit_parameters,
    fit_search_space,
    obj1_name,
    obj2_name,
    mass_param,
    load_training_data,
    load_round2_training_data,
    render_round2_prototype,
    _axes_frac,
    _callout,
    _callout_alpha,
    _label_points,
    _leader_ends,
    _nice_ticks,
    _rgba,
    _segment_boxes,
    _smoothstep,
    _text_boxes,
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


def render_feature_importance(table, out_path, n_articles=None):
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
        n_note = f" n = {n_articles} tested articles." if n_articles else ""
        fig.text(
            0.5, -0.03,
            "Bars: Ax feature_importances (median SAAS lengthscale, inverted, normalized).\n"
            f"Whiskers: interquartile range across MCMC draws.{n_note}",
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


def render_loocv(table, diagnostics, out_path, n_articles=None):
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
        if n_articles is None:
            n_articles = int(table["print_id"].nunique())
        fig.text(
            0.5, -0.04,
            "Leave-one-out: each article predicted by a model that refit NUTS without it.\n"
            f"Dashed line is perfect prediction. n = {n_articles}, so read the "
            "direction, not the decimals.",
            ha="center", fontsize=15, color=LABEL_GRAY,
        )
        fig.tight_layout()
        fig.savefig(out_path, dpi=FIGURE_DPI, bbox_inches="tight", facecolor="white")
        plt.close(fig)


def _safe_corr(a, b):
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def render_cv_travel_set(cv_table, round_number, animate=True):
    """The LOOCV story in the round-2 figure/animation grammar (PR #102).

    Same beat engine, stills and registration as the measured
    predicted-vs-actual set, driven by the held-out predictions instead of a
    suggestion batch: every tested article's LOOCV prediction opens as an
    orange diamond, grows its +/- 1 sd bars and oval and freezes, then
    travels to where that article actually measured, landing as the same
    open black circle it is on every other figure. The measured Pareto front
    then wipes in and the print IDs return. There is no prior-round layer
    here (the predictions ARE the tested articles), so the retire beat drops
    out and the clip opens directly on the predictions.

    Returns ``(stills, gif, mp4)`` exactly like the campaign renderer; the
    file stem is ``t3-prism-bo-round{N}-loocv-*`` so the two sets sit side
    by side in ``bo/figures/``.
    """
    order = cv_table["print_id"].drop_duplicates().tolist()
    piv = cv_table.set_index(["print_id", "metric"])
    sugg_rows, act_rows = [], []
    for pid in order:
        row_s, row_a = {"print_id": pid}, {"print_id": pid}
        for metric in METRIC_ORDER:
            row_s[f"pred_{metric}_mean"] = float(piv.loc[(pid, metric), "predicted"])
            row_s[f"pred_{metric}_sd"] = float(piv.loc[(pid, metric), "predicted_sem"])
            row_a[metric] = float(piv.loc[(pid, metric), "observed"])
        sugg_rows.append(row_s)
        act_rows.append(row_a)
    suggestions = pd.DataFrame(sugg_rows)
    actual = pd.DataFrame(act_rows)
    return render_round2_prototype(
        actual.iloc[0:0], suggestions, actual, round_number,
        animate=animate, synthetic=False,
        stem=f"t3-prism-bo-round{round_number}-loocv",
        series_label="Held-out predictions (LOOCV),\none model per article",
        pred_label="Predicted\n(article held out)",
        front_label="Measured Pareto front",
        unc_label="Held-out prediction ± 1 sd\n(model posterior)",
    )


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


# ---- 4. parity evolution: predictions before vs after the round-2 data ---
# The form sgbaird asked for on PR #102: two parity panels (predicted vs
# measured, one per objective, +/- 1 sd bars) where every tested article's
# prediction travels from where it stood BEFORE the round-2 sessions to where
# the refit trained on all collected data puts it.
#
# The "before" model is the model state that actually chose the printed
# plate: commit 7a048ee's AxClient (5 shape parameters, 7 articles in the
# fit), restored from git history as t3-prism-bo-ax-client-plate-7a048ee.json.
# For the nine r2d2c articles the before values are the frozen suggestions
# CSV verbatim (t3-prism-bo-round1-predictions.csv, the numbers the plate was
# generated from and the numbers every table on the thread quotes); for the
# round-1 articles they come from a seeded refit of that snapshot, in sample
# for the seven articles that model had seen and out of sample for ajhby6
# (spec 07 was still a pending trial then). A fidelity check predicts the
# nine plate designs with the refit and reports the gap to the frozen CSV, so
# the two provenances are known to describe the same model.
#
# The "after" values are the round-2 snapshot's refit (6 parameters, 17
# articles) predicting in sample at each article's own coordinates and
# weighed mass. In-sample parity is the point here (the request is "the refit
# model trained on all collected data"); the honest out-of-sample companion
# is the LOOCV set, which shares this grammar.
PLATE_SNAPSHOT = BO_DIR / "t3-prism-bo-ax-client-plate-7a048ee.json"
ROUND2_SNAPSHOT = BO_DIR / "t3-prism-bo-ax-client-round2.json"
FROZEN_PREDICTIONS = BO_DIR / "t3-prism-bo-round1-predictions.csv"
PARITY_CSV = BO_DIR / "t3-prism-bo-round2-parity-evolution.csv"
PARITY_STEM = "t3-prism-bo-round2-parity"
FROZEN_COL = {obj1_name: "pred_t180", obj2_name: "pred_e_reb_mJ"}


def _predict_objectives(model, feature_dicts):
    """Posterior mean and 1 sd of each objective at the given design points."""
    from ax.core.observation import ObservationFeatures

    feats = [ObservationFeatures(parameters=dict(d)) for d in feature_dicts]
    f_mean, f_cov = model.predict(feats)
    return {
        metric: (
            np.asarray(f_mean[metric], float),
            np.sqrt(np.asarray(f_cov[metric][metric], float)),
        )
        for metric in METRIC_ORDER
    }


def compute_parity_evolution(args):
    """One table per (article, objective): measured value, the prediction the
    plate-generating model made, and the all-data refit's prediction."""
    import torch
    from ax.service.ax_client import AxClient

    shape_names = [p for p in DESIGN_PARAMS if p != mass_param]
    X1, y1, labels1, _, _ = load_training_data(args.results, args.design)
    X2, y2, labels2, _, trial_of = load_round2_training_data()
    frozen = pd.read_csv(FROZEN_PREDICTIONS).set_index("trial_index")

    # -- before: the plate-generating model (7a048ee, 5-D, 7 articles)
    torch.manual_seed(0)
    np.random.seed(0)
    exp_b = AxClient.load_from_json_file(str(PLATE_SNAPSHOT)).experiment
    data_b = exp_b.fetch_data()
    print(f"Plate snapshot: {data_b.df['arm_name'].nunique()} articles in fit "
          f"({len(shape_names)}-D shape space)")
    print("Fitting the plate-generating model (before state)...")
    model_b = fit_saasbo(exp_b, data_b, args.mcmc_samples, args.warmup_steps)

    base1 = [{k: float(x[k]) for k in shape_names} for x in X1]
    pred_b = _predict_objectives(model_b, base1)
    done = [t.arm.parameters for t in exp_b.trials.values()
            if t.status.name == "COMPLETED"]

    def in_fit(base):
        return any(
            all(abs(float(d[k]) - base[k]) < 1e-6 for k in shape_names)
            for d in done
        )

    # Fidelity check: the same refit at the nine plate designs, against the
    # frozen CSV. NUTS is stochastic, so this bounds how far the round-1
    # articles' reconstructed before values can sit from the original run.
    fro_feats = [
        {k: float(frozen.loc[t, k]) for k in shape_names} for t in frozen.index
    ]
    check = _predict_objectives(model_b, fro_feats)
    for metric in METRIC_ORDER:
        col = FROZEN_COL[metric]
        gap = np.abs(check[metric][0] - frozen[f"{col}_mean"].to_numpy(float))
        rel = gap / frozen[f"{col}_sd"].to_numpy(float)
        print(f"  refit vs frozen CSV, {metric}: "
              f"max |d mean| = {gap.max():.3f} ({rel.max():.2f} frozen sd)")

    # -- after: the round-2 refit on everything (6-D, 17 articles)
    torch.manual_seed(0)
    np.random.seed(0)
    exp_a = AxClient.load_from_json_file(str(ROUND2_SNAPSHOT)).experiment
    # widen back from the constant-mass generation slab, same as the other
    # diagnostics, so the out-of-slab articles stay in the fit
    exp_a.search_space = fit_search_space()
    data_a = exp_a.fetch_data()
    print(f"Round-2 snapshot: {data_a.df['arm_name'].nunique()} articles in fit "
          f"({len(DESIGN_PARAMS)}-D space)")
    print("Fitting the all-data refit (after state)...")
    model_a = fit_saasbo(exp_a, data_a, args.mcmc_samples, args.warmup_steps)
    pred_a = _predict_objectives(
        model_a, [{k: float(x[k]) for k in DESIGN_PARAMS} for x in X1 + X2]
    )

    rows = []
    for i, (label, ydict) in enumerate(zip(labels1 + labels2, y1 + y2)):
        pid = label.split(" ")[0]
        round2 = i >= len(labels1)
        trial = trial_of.get(label) if round2 else None
        for metric in METRIC_ORDER:
            meas, sem = ydict[metric]
            if round2:
                col = FROZEN_COL[metric]
                pb = float(frozen.loc[trial, f"{col}_mean"])
                sb = float(frozen.loc[trial, f"{col}_sd"])
                fitted = False
                src = "frozen suggestions CSV (7a048ee)"
            else:
                pb = float(pred_b[metric][0][i])
                sb = float(pred_b[metric][1][i])
                fitted = in_fit(base1[i])
                src = ("plate-model refit (7a048ee)" if fitted
                       else "plate-model refit (7a048ee), out of sample")
            rows.append({
                "print_id": pid,
                "round": 2 if round2 else 1,
                "trial_index": trial if round2 else np.nan,
                "metric": metric,
                "measured": float(meas),
                "measured_sem": float(sem),
                "pred_before": pb,
                "pred_before_sd": sb,
                "before_in_fit": fitted,
                "before_source": src,
                "pred_after": float(pred_a[metric][0][i]),
                "pred_after_sd": float(pred_a[metric][1][i]),
            })
    table = pd.DataFrame(rows)
    table.to_csv(PARITY_CSV, index=False, float_format="%.5f")
    print(f"  parity table -> {PARITY_CSV}")
    for metric in METRIC_ORDER:
        sub = table[(table.metric == metric) & (table["round"] == 2)]
        before = float((sub.measured - sub.pred_before).abs().median())
        after = float((sub.measured - sub.pred_after).abs().median())
        print(f"  {metric}: round-2 median |residual| "
              f"{before:.3f} (before) -> {after:.3f} (after)")
    return table


def render_parity_evolution(table, animate=True, fps=25):
    """Two animated parity panels: predictions travel before -> after.

    Same grammar, registration and encoding as the campaign's figure sets.
    Beats, one idea each: (1) hold on the before state, forecasts as orange
    diamonds and round-1 articles as open black circles, +/- 1 sd bars on
    everything; (2) travel, each prediction eases vertically to the refit's
    value while its bar moves and resizes with it and the diamonds hand off
    to open circles, a ghost diamond and a dashed riser marking where the
    forecast stood; (3) hold, one before/after pair named; (4) clean, the
    ghost layer fades; (5) rest, the print IDs fade in. Measured values do
    not move: x is pinned to the drop sessions, so all motion is the model
    changing its mind. Stills are the three rest points (start, shift,
    final), the same pixel size as the video, no tight bounding box.
    """
    from matplotlib.collections import LineCollection

    order = table["print_id"].drop_duplicates().tolist()
    n_art = len(order)
    piv = table.set_index(["print_id", "metric"])
    P = {}
    for metric in METRIC_ORDER:
        sub = piv.xs(metric, level="metric").loc[order]
        P[metric] = {
            "x": sub["measured"].to_numpy(float),
            "xerr": sub["measured_sem"].to_numpy(float),
            "yb": sub["pred_before"].to_numpy(float),
            "sb": sub["pred_before_sd"].to_numpy(float),
            "ya": sub["pred_after"].to_numpy(float),
            "sa": sub["pred_after_sd"].to_numpy(float),
        }
    is2 = (
        piv.xs(METRIC_ORDER[0], level="metric").loc[order]["round"].to_numpy(int)
        == 2
    )
    n2 = int(is2.sum())
    r2_idx = np.where(is2)[0]

    TICK_STEP = {obj1_name: 0.1, obj2_name: 2.0}
    ticks, lims = {}, {}
    for metric in METRIC_ORDER:
        d = P[metric]
        vals = np.concatenate([d["x"], d["yb"], d["ya"]])
        t = _nice_ticks(float(vals.min()), float(vals.max()), TICK_STEP[metric])
        ticks[metric] = t
        pad = 0.22 * TICK_STEP[metric]
        lims[metric] = (float(t[0]) - pad, float(t[-1]) + pad)

    # beat boundaries in seconds
    T0, D_TR, D_H1, D_CL, D_RS = 1.6, 2.6, 1.7, 0.9, 2.4
    T1 = T0 + D_TR
    T2 = T1 + D_H1
    T3 = T2 + D_CL
    n_frames = int(round((T3 + D_RS) * fps))
    starts = 0.55 * np.arange(n2) / max(n2 - 1, 1)  # staggered travel

    ink_rgba = np.array(mcolors.to_rgba(INK))
    orange_rgba = np.array(mcolors.to_rgba(SUGGEST_ORANGE))

    with plt.rc_context(FIG_RC):
        fig, axes = plt.subplots(1, 2, figsize=ANIM_FIGSIZE, dpi=ANIM_DPI)
        # explicit margins, no tight bbox: the three stills and the video
        # must be the same pixel size, like every other registered set here
        fig.subplots_adjust(left=0.075, right=0.975, top=0.80, bottom=0.145,
                            wspace=0.30)
        fig.patch.set_facecolor("white")

        art = {}
        diag_name = {}
        for ax, metric in zip(axes, METRIC_ORDER):
            d, t, lim = P[metric], ticks[metric], lims[metric]
            ax.set_anchor("S")
            ax.set_xlim(*lim)
            ax.set_ylim(*lim)
            ax.set_xticks(t)
            ax.set_yticks(t)
            ax.set_aspect("equal", adjustable="box")
            ax.grid(False)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            for side in ("left", "bottom"):
                ax.spines[side].set_position(("outward", 14))
            ax.spines["bottom"].set_bounds(t[0], t[-1])
            ax.spines["left"].set_bounds(t[0], t[-1])
            ax.tick_params(labelsize=19)
            ax.set_title(METRIC_TITLE[metric], fontsize=21, pad=40)
            ax.set_xlabel("Measured", labelpad=10, fontsize=20)

            ax.plot(lim, lim, color=LABEL_GRAY, lw=1.6, ls=(0, (5, 5)), zorder=1)
            # park the diagonal's name at whichever point along it sits
            # farthest from every marker position, before or after states
            # both: the points hug the line at rest, so a fixed spot would
            # collide for one panel or the other
            pts = ax.transData.transform(
                np.column_stack([
                    np.concatenate([d["x"], d["x"]]),
                    np.concatenate([d["yb"], d["ya"]]),
                ])
            )
            best = None
            for f in np.linspace(0.12, 0.88, 25):
                v = lim[0] + f * (lim[1] - lim[0])
                px, py = ax.transData.transform((v, v))
                dmin = float(np.hypot(pts[:, 0] - px, pts[:, 1] - py).min())
                if best is None or dmin > best[0]:
                    best = (dmin, v)
            dpos = best[1]
            diag_name[ax] = ax.annotate(
                "measured = predicted", (dpos, dpos),
                textcoords="offset points", xytext=(-5, 5),
                rotation=45, rotation_mode="anchor", ha="center", va="bottom",
                fontsize=13.5, color=LABEL_GRAY, zorder=1,
            )

            vbars = LineCollection(
                [[(x, y - s), (x, y + s)]
                 for x, y, s in zip(d["x"], d["yb"], d["sb"])],
                linewidths=2.2, zorder=1.6,
            )
            ax.add_collection(vbars)
            hbars = LineCollection(
                [[(x - e, y), (x + e, y)]
                 for x, y, e in zip(d["x"], d["yb"], d["xerr"])],
                colors=mcolors.to_rgba(LABEL_GRAY, 0.65),
                linewidths=2.0, zorder=1.5,
            )
            ax.add_collection(hbars)
            conn = LineCollection(
                [[(x, y), (x, y)] for x, y in zip(d["x"][is2], d["yb"][is2])],
                linewidths=1.8, linestyles=(0, (4, 3)), zorder=1.4,
            )
            ax.add_collection(conn)
            ghost = ax.scatter(
                d["x"][is2], d["yb"][is2], marker="D", s=150,
                fc=_rgba(SUGGEST_ORANGE, np.zeros(n2)), ec="none", zorder=2,
            )
            r1pts = ax.scatter(
                d["x"][~is2], d["yb"][~is2], fc="none", ec=INK,
                s=190, lw=2.4, zorder=4,
            )
            landed = ax.scatter(
                d["x"][is2], d["ya"][is2], fc="none",
                ec=_rgba(INK, np.zeros(n2)), s=190, lw=2.4, zorder=4,
            )
            mover = ax.scatter(
                d["x"][is2], d["yb"][is2], marker="D", s=150,
                fc=_rgba(SUGGEST_ORANGE, np.ones(n2)), ec="none", zorder=6,
            )
            art[metric] = dict(vbars=vbars, hbars=hbars, conn=conn,
                               ghost=ghost, r1pts=r1pts, landed=landed,
                               mover=mover)

        axL, axR = axes
        dL, dR = P[obj1_name], P[obj2_name]
        axL.set_ylabel("Predicted", rotation=0, ha="left", va="bottom",
                       fontsize=20)
        axL.yaxis.set_label_coords(-0.12, 1.02)

        # Beat-1 callouts: name the two cohorts on the left panel and the
        # bars on the right one. At most one text is lit while anything moves.
        i_r1 = int(np.argmax(np.where(~is2, dL["yb"], -np.inf)))
        c_r1 = _callout(
            axL, "Articles in the round-1 fit",
            (dL["x"][i_r1], dL["yb"][i_r1]), (0.03, 0.93), INK,
            leader=LEADER_GRAY,
        )
        i_far = r2_idx[int(np.argmax(dL["x"][is2]))]
        c_r2 = _callout(
            axL, "Round-2 forecasts\n(before their sessions)",
            (dL["x"][i_far], dL["yb"][i_far]), (0.97, 0.07),
            SUGGEST_ORANGE, ha="right",
        )
        # What the bars are, as a static footnote rather than a callout: the
        # bars exist in every beat (before, during and after the travel), so
        # their explanation never fades. Bottom right of the rebound panel,
        # the region its forecasts cannot reach (they sat above the diagonal).
        txt_unc = axR.text(
            0.98, 0.015,
            "bars: predicted ± 1 sd (model posterior)\ngray: measured ± 1 SEM",
            transform=axR.transAxes, fontsize=15, color=LABEL_GRAY,
            ha="right", va="bottom", zorder=6,
        )

        # travel-and-after statement; stays through the rest state
        txt_refit = axL.text(
            0.03, 0.90,
            f"Refit on all collected data\n(rounds 1 + 2, {n_art} articles)",
            transform=axL.transAxes, fontsize=18, color=INK, va="center",
            alpha=0.0, zorder=6,
        )

        # Beat-3 pair: the biggest t180 mover, named before and after. Text
        # right-aligned and pulled toward the panel's interior, so neither
        # can overflow the frame or reach the refit statement at top left.
        i_mv = r2_idx[int(np.argmax(np.abs(dL["ya"] - dL["yb"])[is2]))]
        gxy = (dL["x"][i_mv], dL["yb"][i_mv])
        lxy = (dL["x"][i_mv], dL["ya"][i_mv])
        c_before = _callout(
            axL, "Forecast, before", gxy,
            _axes_frac(axL, gxy, -0.06, -0.12), SUGGEST_ORANGE, ha="right",
        )
        c_after = _callout(
            axL, "Refit, after", lxy,
            _axes_frac(axL, lxy, -0.08, -0.13), INK, leader=LEADER_GRAY,
            ha="right",
        )
        for ann in (c_before, c_after):
            _callout_alpha(ann, 0.0)

        # Print IDs, laid out once against the final frame; lit only at rest.
        def diag_boxes(ax, lim):
            p = ax.transData.transform([[lim[0], lim[0]], [lim[1], lim[1]]])
            return _segment_boxes([(tuple(p[0]), tuple(p[1]))], n=24, half=7,
                                  weight=W_LINE)

        def outside_boxes(ax):
            """Half-planes beyond the panel, so a label prefers any interior
            candidate over one that clips at the canvas or strays into the
            neighbouring panel (parity panels are narrower than the single
            objective-space panel the placer was tuned on)."""
            bb = ax.get_window_extent()
            big = 1e6
            return [
                (-big, -big, bb.x0, big, W_TEXT),
                (bb.x1, -big, big, big, W_TEXT),
                (-big, -big, big, bb.y0, W_TEXT),
                (-big, bb.y1, big, big, W_TEXT),
            ]

        fig.canvas.draw()
        ids = []
        for ax, metric in zip(axes, METRIC_ORDER):
            d = P[metric]
            frame_df = pd.DataFrame(
                {"print_id": order, "x": d["x"], "y": d["ya"]}
            )
            # pads are display pixels: at 300 dpi a 13.5 pt character is
            # ~55 px, so a legible clearance needs tens of pixels
            obstacles = (
                diag_boxes(ax, lims[metric])
                + outside_boxes(ax)
                + _text_boxes(fig, [diag_name[ax]], pad=26)
            )
            if ax is axL:
                obstacles = obstacles + _text_boxes(fig, [txt_refit], pad=26)
            else:
                obstacles = obstacles + _text_boxes(fig, [txt_unc], pad=44)
            anns = _label_points(ax, frame_df, "print_id", "x", "y",
                                 fontsize=13.5, obstacles=obstacles)
            for ann in anns:
                ann.set_alpha(0.0)
            ids.extend(anns)

        def update(frame):
            t = frame / fps
            u = float(np.clip((t - T0) / D_TR, 0.0, 1.0))
            p = np.full(n_art, _smoothstep(u))
            p[is2] = _smoothstep((u - starts) / 0.45)
            w = _smoothstep((p[is2] - 0.55) / 0.45)   # diamond -> circle
            g = _smoothstep(p[is2] / 0.25)            # ghost layer in
            m = _smoothstep((t - T1) / 0.4)           # shift callouts
            c = _smoothstep((t - T2) / D_CL)          # clean
            r = _smoothstep((t - T3) / 0.6)           # ids at rest

            for metric in METRIC_ORDER:
                d, a = P[metric], art[metric]
                y = d["yb"] + (d["ya"] - d["yb"]) * p
                s = d["sb"] + (d["sa"] - d["sb"]) * p
                a["vbars"].set_segments(
                    [[(x, yy - ss), (x, yy + ss)]
                     for x, yy, ss in zip(d["x"], y, s)]
                )
                colors = np.tile(ink_rgba, (n_art, 1))
                colors[:, 3] = 0.35
                mix = ((1.0 - w[:, None]) * orange_rgba
                       + w[:, None] * ink_rgba)
                colors[is2, :3] = mix[:, :3]
                colors[is2, 3] = 0.62 - 0.27 * w
                a["vbars"].set_color(colors)
                a["hbars"].set_segments(
                    [[(x - e, yy), (x + e, yy)]
                     for x, e, yy in zip(d["x"], d["xerr"], y)]
                )
                a["conn"].set_segments(
                    [[(x, y0), (x, yy)] for x, y0, yy
                     in zip(d["x"][is2], d["yb"][is2], y[is2])]
                )
                a["conn"].set_color(_rgba(SUGGEST_ORANGE, 0.45 * g * (1 - c)))
                a["ghost"].set_facecolor(
                    _rgba(SUGGEST_ORANGE, 0.38 * g * (1 - c))
                )
                a["r1pts"].set_offsets(
                    np.column_stack([d["x"][~is2], y[~is2]])
                )
                a["mover"].set_offsets(np.column_stack([d["x"][is2], y[is2]]))
                a["mover"].set_facecolor(_rgba(SUGGEST_ORANGE, 1.0 - w))
                a["landed"].set_edgecolor(_rgba(INK, w))

            fade0 = 1.0 - _smoothstep(u / 0.22)
            for ann in (c_r1, c_r2):
                _callout_alpha(ann, fade0)
            txt_refit.set_alpha(_smoothstep((u - 0.15) / 0.35))
            _callout_alpha(c_before, m * (1 - c))
            _callout_alpha(c_after, m * (1 - c))
            for ann in ids:
                ann.set_alpha(r)
            return ()

        fig_dir = BO_DIR / "figures"
        fig_dir.mkdir(exist_ok=True)
        still_frames = {
            "start": 0,
            "shift": int(round(T2 * fps)) - 1,
            "final": n_frames - 1,
        }
        stills = {}
        for stage, frame in still_frames.items():
            update(frame)
            out = fig_dir / f"{PARITY_STEM}-{stage}.png"
            fig.savefig(out, dpi=ANIM_DPI, facecolor="white")
            stills[stage] = out

        out_mp4 = out_gif = None
        have_ffmpeg = shutil.which("ffmpeg") is not None
        if animate:
            from matplotlib.animation import (
                FFMpegWriter, FuncAnimation, PillowWriter,
            )

            anim = FuncAnimation(fig, update, frames=n_frames,
                                 interval=1000 / fps)
            out_mp4 = fig_dir / f"{PARITY_STEM}.mp4"
            out_gif = fig_dir / f"{PARITY_STEM}.gif"
            if have_ffmpeg:
                anim.save(
                    out_mp4,
                    writer=FFMpegWriter(
                        fps=fps, codec="libx264", bitrate=-1,
                        extra_args=["-pix_fmt", "yuv420p", "-crf", "18"],
                    ),
                    savefig_kwargs={"facecolor": "white"},
                )
            else:
                out_mp4 = None
                print("ffmpeg not found: skipping the MP4, writing the GIF only")
                anim.save(out_gif, writer=PillowWriter(fps=12))
        plt.close(fig)

    if animate and have_ffmpeg:
        # palette-based GIF off the MP4, same pass as the campaign sets
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error", "-i", str(out_mp4),
                "-vf",
                f"fps=12,scale={GIF_WIDTH_PX}:-2:flags=lanczos,split[a][b];"
                "[a]palettegen=max_colors=128[p];"
                "[b][p]paletteuse=dither=bayer:bayer_scale=3",
                "-loop", "0", str(out_gif),
            ],
            check=True,
        )
    return stills, out_gif, out_mp4


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
    ap.add_argument(
        "--cv-animation",
        action="store_true",
        help=(
            "also render the LOOCV predicted-vs-measured figure set and "
            "animation (four registered stills + GIF + MP4, same grammar as "
            "the round-2 measured set); with --plot-only it redraws from the "
            "committed LOOCV CSV"
        ),
    )
    ap.add_argument(
        "--no-animation",
        action="store_true",
        help="with --cv-animation, write only the still PNGs (no GIF/MP4)",
    )
    ap.add_argument(
        "--parity-evolution",
        action="store_true",
        help=(
            "render the before/after parity set instead of the other "
            "diagnostics: two parity panels (one per objective, ± 1 sd "
            "bars) where every article's prediction travels from the "
            "plate-generating model's value (7a048ee) to the all-data "
            "refit's (PR #102 request). Refits both snapshots, ~5 min; "
            "with --plot-only it redraws from the committed parity CSV"
        ),
    )
    args = ap.parse_args(argv)

    fig_dir = BO_DIR / "figures"
    fig_dir.mkdir(exist_ok=True)
    stem = f"t3-prism-bo-round{args.round}"

    if args.parity_evolution:
        if args.plot_only:
            table = pd.read_csv(PARITY_CSV)
        else:
            table = compute_parity_evolution(args)
        stills, gif, mp4 = render_parity_evolution(
            table, animate=not args.no_animation
        )
        for i, stage in enumerate(("start", "shift", "final"), start=1):
            print(f"  slide {i} ({stage}): {stills[stage]}")
        if gif or mp4:
            print("  animation: " + ", ".join(str(x) for x in (mp4, gif) if x))
        return 0

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
            if args.cv_animation:
                render_cv_travel_set(
                    cv_table, args.round, animate=not args.no_animation
                )
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

    # Map arm names back onto print IDs by matching the attached parameters,
    # not the attachment order: the round-2 snapshot holds both rounds'
    # completed articles plus pending and generated trials, so order is not a
    # reliable key. Every completed trial's 6-vector is unique across the
    # tested articles, which is what makes this exact.
    X1, _, labels1, _, _ = load_training_data(args.results, args.design)
    X2, _, labels2, _, _ = load_round2_training_data()
    X_all, labels_all = X1 + X2, labels1 + labels2
    labels_by_arm = {}
    for trial in experiment.trials.values():
        arm = trial.arm
        for x, label in zip(X_all, labels_all):
            if all(
                abs(float(arm.parameters[k]) - float(v)) < 1e-6
                for k, v in x.items()
            ):
                labels_by_arm[arm.name] = label.split(" ")[0]
                break
    n_articles = int(data.df["arm_name"].nunique())
    print(f"Loaded {args.snapshot.name}: {len(data.df)} observations, "
          f"{n_articles} tested articles, {len(labels_by_arm)} labeled")

    print("Fitting SAASBO for diagnostics...")
    model = fit_saasbo(experiment, data, args.mcmc_samples, args.warmup_steps)

    imp_png = fig_dir / f"{stem}-feature-importance.png"
    importance = compute_feature_importance(model)
    render_feature_importance(importance, imp_png, n_articles=n_articles)
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
    render_loocv(cv_table, diagnostics, cv_png, n_articles=n_articles)
    cv_table.to_csv(BO_DIR / f"{stem}-loocv.csv", index=False, float_format="%.5f")
    print(f"  figure -> {cv_png}")
    for name in ("MAPE", "Total raw effect", "Fisher exact test p"):
        if name in diagnostics:
            values = {m: round(float(v), 4) for m, v in diagnostics[name].items()}
            print(f"  {name}: {values}")

    if args.cv_animation:
        print("\nLOOCV figure set + animation (round-2 grammar)...")
        stills, gif, mp4 = render_cv_travel_set(
            cv_table, args.round, animate=not args.no_animation
        )
        for i, stage in enumerate(STILL_STAGES, start=1):
            print(f"  slide {i} ({stage}): {stills[stage]}")
        if gif or mp4:
            print("  animation: " + ", ".join(str(x) for x in (mp4, gif) if x))
    return 0


if __name__ == "__main__":
    sys.exit(main())
