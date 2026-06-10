#!/usr/bin/env python3
"""Standalone *example* surrogate-diagnostic figures for the manuscript's empty
figure slots, generated from a real Ax Bayesian-optimization loop on DUMMY data.

Requested in PR review (comment 4673509625): "create actual placeholder figures
for any of the figures that are actually just empty slots (e.g., an example of
LOO-CV plots obtained from Ax using dummy data, etc.)". The manuscript currently
has four data-figure slots rendered as empty boxes via ``\\figplaceholder`` in
``manuscript/manuscript-body.tex``:

  * ``fig:loocv``       -- leave-one-out cross-validation of the GP surrogate
  * ``fig:sensitivity`` -- parameter-sensitivity ranking
  * ``fig:convergence`` -- best-so-far performance vs. number of experiments
  * ``fig:pareto``      -- Pareto front in (peak transmitted force, SEA) space

This script runs a small **real** Ax campaign (Sobol init + BoTorch model-based
trials, the same SAASBO/qNEHVI-style machinery the manuscript describes) over a
tensegrity-flavoured search space (strut diameter, twist, pretension, and a
categorical cable diameter), evaluated by a **synthetic** surrogate, then renders
each diagnostic the way the real campaign would. The four outputs are drop-in
example replacements for the empty slots.

IMPORTANT: the objective values are SYNTHETIC. The search space mirrors the
documented design parameterization (PR #24/#35: cable_d in {1.2,1.8,2.4,3.0,4.5}
mm, four D3-orbit axes) and the objectives mirror the manuscript's SEA (maximize)
and peak transmitted force (minimize), but no experimental data is read. Every
panel carries a visible "ILLUSTRATIVE EXAMPLE -- synthetic data" watermark.
Replace ``evaluate()`` with real measured outcomes before any figure like this is
used as a result.

Run:
    python scripts/figures/ax_placeholder_figures_example.py
Outputs (figures/examples/):
    ax-loocv-example.{png,pdf}
    ax-sensitivity-example.{png,pdf}
    ax-convergence-example.{png,pdf}
    ax-pareto-example.{png,pdf}
    ax-placeholder-figures-contact-sheet.png   (2x2 preview for review)
"""
from __future__ import annotations

import os
import warnings

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Ax is verbose; keep the example run readable.
warnings.filterwarnings("ignore")
for _name in ("ax", "ax.api.client", "ax.service", "botorch", "gpytorch"):
    import logging

    logging.getLogger(_name).setLevel(logging.ERROR)

from ax.api import Client, RangeParameterConfig, ChoiceParameterConfig  # noqa: E402
import ax.adapter.cross_validation as CV  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "figures", "examples")
SEED = 36
RNG = np.random.default_rng(SEED)

# Colour-blind-safe pair (Wong/Okabe-Ito): bluish-green vs. vermillion.
C_PRED = "#0072B2"
C_BO = "#009E73"
C_BASE = "#D55E00"
WATERMARK = "ILLUSTRATIVE EXAMPLE — synthetic data"

# Tensegrity-flavoured search space (PR #24/#35 design parameterization).
CABLE_D = [1.2, 1.8, 2.4, 3.0, 4.5]  # mm, FFF-resolvable categorical
PARAM_LABELS = {
    "strut_d": r"strut $d$",
    "twist": r"twist $\theta$",
    "pretension": "pretension",
    "cable_d": r"cable $d$",
}


def evaluate(p: dict) -> dict:
    """Synthetic tensegrity surrogate: SEA [J/g] (maximize), peak_force [N] (min)."""
    sd, tw, pt = p["strut_d"], p["twist"], float(p["pretension"])
    cd = float(p["cable_d"])
    sea = (
        8.0
        + 3.0 * np.sin(np.radians(tw))
        - 0.5 * (sd - 3.0) ** 2
        + 1.2 * np.log(cd)
        + 4.0 * pt
        - 3.0 * (pt - 0.65) ** 2
    )
    peak = (
        1750.0
        - 620.0 * pt
        + 130.0 * (sd - 3.0) ** 2
        - 210.0 * np.cos(np.radians(tw))
        - 90.0 * np.log(cd)
    )
    # heteroscedastic-ish measurement noise, like replicate scatter
    sea += RNG.normal(0, 0.25)
    peak += RNG.normal(0, 22)
    return {"SEA": float(sea), "peak_force": float(peak)}


def run_campaign(n_trials: int = 26):
    client = Client(random_seed=SEED)
    client.configure_experiment(
        name="tensegrity_demo",
        parameters=[
            RangeParameterConfig(name="strut_d", parameter_type="float",
                                 bounds=(2.0, 4.5)),
            RangeParameterConfig(name="twist", parameter_type="float",
                                 bounds=(0.0, 120.0)),
            RangeParameterConfig(name="pretension", parameter_type="float",
                                 bounds=(0.0, 1.0)),
            ChoiceParameterConfig(name="cable_d", parameter_type="float",
                                  values=CABLE_D, is_ordered=True),
        ],
    )
    client.configure_optimization(objective="SEA, -peak_force")

    history = []  # (trial_index, SEA, peak_force)
    for _ in range(n_trials):
        for idx, p in client.get_next_trials(max_trials=1).items():
            out = evaluate(p)
            client.complete_trial(trial_index=idx, raw_data=out)
            history.append((idx, out["SEA"], out["peak_force"]))
    return client, np.array(history)


def _watermark(ax):
    ax.text(0.5, 0.5, WATERMARK, transform=ax.transAxes, ha="center", va="center",
            fontsize=13, color="0.5", alpha=0.18, rotation=22, zorder=0,
            fontweight="bold")


def _adapter(client):
    """Fitted BoTorch model from the campaign.

    NOTE: ``Client._generation_strategy`` is a private accessor; the new Ax API
    does not yet expose a public one for the underlying adapter. Centralized here
    so the internal-API dependency lives in a single place.
    """
    return client._generation_strategy.adapter


# ---------------------------------------------------------------------------
# (1) Leave-one-out cross-validation of the GP surrogate.
# ---------------------------------------------------------------------------
def fig_loocv(client) -> str:
    adapter = _adapter(client)  # fitted BoTorch model
    cv = CV.cross_validate(adapter)
    metrics = [("SEA", "SEA  [J g$^{-1}$]"), ("peak_force", "peak force  [N]")]

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 4.1))
    for ax, (m, label) in zip(axes, metrics):
        obs = np.array([r.observed.data.means_dict[m] for r in cv])
        pred = np.array([r.predicted.means_dict[m] for r in cv])
        sem = np.array([np.sqrt(max(r.predicted.covariance_matrix[m][m], 0.0))
                        for r in cv])
        lo = min(obs.min(), pred.min())
        hi = max(obs.max(), pred.max())
        pad = 0.06 * (hi - lo)
        line = [lo - pad, hi + pad]
        ax.plot(line, line, "--", color="0.4", lw=1.0, zorder=1, label="ideal $y=x$")
        ax.errorbar(obs, pred, yerr=sem, fmt="o", ms=4.5, color=C_PRED,
                    ecolor="0.6", elinewidth=0.8, capsize=2, zorder=3,
                    label="LOO prediction")
        # leave-one-out R^2
        ss_res = np.sum((obs - pred) ** 2)
        ss_tot = np.sum((obs - obs.mean()) ** 2)
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        ax.set_xlim(line)
        ax.set_ylim(line)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel(f"observed {label}")
        ax.set_ylabel(f"predicted {label}")
        ax.set_title(f"{m}   ($R^2_{{\\rm LOO}}={r2:.2f}$)", fontsize=10)
        ax.grid(True, ls=":", alpha=0.5)
        _watermark(ax)
    axes[0].legend(loc="upper left", fontsize=8, framealpha=0.9)
    fig.suptitle("Leave-one-out cross-validation of the GP surrogate (Ax)",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return _save(fig, "ax-loocv-example")


# ---------------------------------------------------------------------------
# (2) Parameter-sensitivity ranking (model length-scale based importances).
# ---------------------------------------------------------------------------
def fig_sensitivity(client) -> str:
    adapter = _adapter(client)
    metrics = ["SEA", "peak_force"]
    params = list(PARAM_LABELS.keys())
    imp = {m: adapter.feature_importances(m) for m in metrics}

    y = np.arange(len(params))
    h = 0.38
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.barh(y - h / 2, [imp["SEA"][p] for p in params], height=h,
            color=C_BO, label="SEA")
    ax.barh(y + h / 2, [imp["peak_force"][p] for p in params], height=h,
            color=C_BASE, label="peak force")
    ax.set_yticks(y)
    ax.set_yticklabels([PARAM_LABELS[p] for p in params])
    ax.invert_yaxis()
    ax.set_xlabel("relative importance (normalized inverse length-scale)")
    ax.set_title("Parameter-sensitivity ranking (Ax surrogate)", fontsize=11)
    ax.grid(True, axis="x", ls=":", alpha=0.5)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.9)
    _watermark(ax)
    fig.tight_layout()
    return _save(fig, "ax-sensitivity-example")


# ---------------------------------------------------------------------------
# (3) Best-so-far convergence vs. number of experiments (BO vs. random).
# ---------------------------------------------------------------------------
def fig_convergence(client, history) -> str:
    sea = history[:, 1]
    n = len(sea)
    x = np.arange(1, n + 1)
    bo_best = np.maximum.accumulate(sea)

    # Independent random-search baseline: draw uniformly from the SAME search
    # space and evaluate with the SAME synthetic surrogate (not a reshuffle of
    # the BO-concentrated pool, which would unfairly inflate the baseline).
    rng = np.random.default_rng(7)
    runs = []
    for _ in range(200):
        vals = []
        for _ in range(n):
            p = {
                "strut_d": rng.uniform(2.0, 4.5),
                "twist": rng.uniform(0.0, 120.0),
                "pretension": rng.uniform(0.0, 1.0),
                "cable_d": rng.choice(CABLE_D),
            }
            vals.append(evaluate(p)["SEA"])
        runs.append(np.maximum.accumulate(vals))
    draws = np.array(runs)
    base_mean = draws.mean(axis=0)
    base_lo, base_hi = np.percentile(draws, [10, 90], axis=0)

    n_sobol = 9  # documented n=9 Sobol initialization batch (PR #35)
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.fill_between(x, base_lo, base_hi, color=C_BASE, alpha=0.15,
                    label="random search (10–90%)")
    ax.plot(x, base_mean, color=C_BASE, lw=1.6, ls="--", label="random search (mean)")
    ax.plot(x, bo_best, color=C_BO, lw=2.0, marker="o", ms=4,
            label="Bayesian optimization")
    ax.axvspan(0.5, n_sobol + 0.5, color="0.85", alpha=0.5, zorder=0)
    ax.text(n_sobol / 2 + 0.5, ax.get_ylim()[0], "Sobol\ninit", ha="center",
            va="bottom", fontsize=8, color="0.4")
    ax.set_xlabel("number of physical experiments")
    ax.set_ylabel("best-so-far SEA  [J g$^{-1}$]")
    ax.set_title("Convergence of the BO loop", fontsize=11)
    ax.set_xlim(1, n)
    ax.grid(True, ls=":", alpha=0.5)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.9)
    _watermark(ax)
    fig.tight_layout()
    return _save(fig, "ax-convergence-example")


# ---------------------------------------------------------------------------
# (4) Pareto front in (peak transmitted force, SEA) space.
# ---------------------------------------------------------------------------
def fig_pareto(client, history) -> str:
    peak_all = history[:, 2]
    sea_all = history[:, 1]
    pf = client.get_pareto_frontier()
    pf_pts = np.array([(o["peak_force"][0], o["SEA"][0]) for _, o, _, _ in pf])
    order = np.argsort(pf_pts[:, 0])
    pf_pts = pf_pts[order]

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.scatter(peak_all, sea_all, s=26, color="0.6", alpha=0.7,
               label="evaluated designs", zorder=2)
    ax.plot(pf_pts[:, 0], pf_pts[:, 1], "-o", color=C_BO, lw=1.8, ms=6,
            label="Pareto front", zorder=3)
    # annotate the two extremes (offset away from the front cluster)
    ax.annotate("max SEA", xy=pf_pts[-1], xytext=(18, -2),
                textcoords="offset points", fontsize=8, color=C_BO,
                arrowprops=dict(arrowstyle="-", color=C_BO, lw=0.6))
    ax.annotate("min peak force", xy=pf_pts[0], xytext=(20, 18),
                textcoords="offset points", fontsize=8, color=C_BO,
                arrowprops=dict(arrowstyle="-", color=C_BO, lw=0.6))
    ax.set_xlabel("peak transmitted force  [N]   (minimize)")
    ax.set_ylabel("SEA  [J g$^{-1}$]   (maximize)")
    ax.set_title("Pareto-optimal designs", fontsize=11)
    ax.grid(True, ls=":", alpha=0.5)
    ax.legend(loc="lower left", fontsize=9, framealpha=0.9)
    _watermark(ax)
    fig.tight_layout()
    return _save(fig, "ax-pareto-example")


def _save(fig, base: str) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    png = os.path.join(OUT_DIR, base + ".png")
    pdf = os.path.join(OUT_DIR, base + ".pdf")
    fig.savefig(png, dpi=200)
    fig.savefig(pdf)
    plt.close(fig)
    return png


def contact_sheet(paths) -> None:
    import matplotlib.image as mpimg

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    for ax, p in zip(axes.ravel(), paths):
        ax.imshow(mpimg.imread(p))
        ax.axis("off")
    fig.suptitle("Ax surrogate-diagnostic placeholder examples (synthetic data)",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = os.path.join(OUT_DIR, "ax-placeholder-figures-contact-sheet.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print("wrote", out)


def main() -> None:
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11})
    client, history = run_campaign()
    paths = [
        fig_loocv(client),
        fig_sensitivity(client),
        fig_convergence(client, history),
        fig_pareto(client, history),
    ]
    for p in paths:
        print("wrote", p, "(and .pdf)")
    contact_sheet(paths)


if __name__ == "__main__":
    main()
