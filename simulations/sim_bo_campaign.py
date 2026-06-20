"""Closed-loop Bayesian-optimization campaign over the PR #35 T3-prism box,
**evaluated entirely by simulation** (no printer, no drop-tower).

This is the simulation-only analogue of PR #35's `bo/t3_prism_sobol_batch.py`.
Where PR #35 emits a *single* Sobol batch for a human-in-the-loop print +
bench-test round, this script closes the loop: Ax proposes designs, a
simulation scores them, and the results are fed straight back to the Ax model
so a multi-objective qNEHVI surrogate drives the search.  Per @sgbaird
(PR comment 4759514616):

    "run a Bayesian optimization campaign as you see fit using only
     simulations as the objective functions.  Mirror what's in #35, but
     using these kinds of simulations instead of real experiments."

Follow-up (PR comment 4759900555) — separate the regimes, plot each random
seed individually, add std-dev bands to the averaged-behaviour plots, repeat
across the simulation tiers, and add Ax leave-one-out cross-validation (LOO-CV)
plots per seed and model to check for predictive signal:

    "the plotting of both crutch and lander on the same graphs is confusing
     because of the scale differences.  Separate these out.  Generate
     individual plots for each seed.  Also, add stdDev bands where applicable
     for the average behavior plots.  Repeat this for each of the tier methods
     ...  Also, create LOO-CV plots for each seed and model.  Ax has a built
     in method for creating these plots.  I want to see if there is predictive
     signal it's learning from."

Design box (identical to PR #35 `bo/t3_prism_sobol_batch.PARAMETERS`):

    R_mm        radius            [25, 40]
    H_mm        height            [60, 110]
    twist_deg   top-vs-bottom     [40, 80]
    strut_d_mm  PLA strut Ø       [6.0, 12.0]
    cable_d_mm  TPU cable Ø       [3.0, 5.5]

Frozen (matching PR #35): topology=t3_prism, tiling=1x1x1, tpu_shore=85A,
build_orientation=vertical, PLA struts / TPU cables.

Simulation tiers (the "tier methods" repeated across):

    C   MuJoCo rigid-tendon regime sim (``bo_evaluator.evaluate_design``):
        3 objectives — minimize ``F_peak_N``, maximize ``SEA_J_per_g``,
        maximize ``eta`` — driven by a qNEHVI hyper-volume surrogate.
    B   Newton/Warp XPBD drop (``newton_drop``): a single objective —
        minimize ``F_peak_N`` (peak |payload accel| × payload mass).  Newton
        exposes only the payload-acceleration trace (no tendon strain energy),
        so the Tier-B campaign is single-objective; this also tells us whether
        the mid-fidelity engine carries learnable design signal at all.

A separate campaign is run **per loading regime** (crutch, lander) **per
random seed**, because (a) the loading scenario is fixed inside a campaign
while the design varies, and (b) repeating the campaign across seeds is what
lets us report average optimization behaviour with a spread band.  All plots
keep the two regimes on **separate figures** (their objective scales differ by
~6×, which made the previous shared axes unreadable).

Outputs (under ``simulations/outputs/``), one set per tier × regime:

    sim_bo_<tier>_<regime>.csv                 all trials, all seeds
    sim_bo_<tier>_<regime>_pareto.csv          feasible Pareto subset (union)
    sim_bo_<tier>_<regime>_seed<k>_convergence.png   per-seed running-best
    sim_bo_<tier>_<regime>_convergence.png     mean running-best ± std band
    sim_bo_<tier>_<regime>_seed<k>_pareto.png  per-seed Pareto (multi-obj tiers)
    sim_bo_<tier>_<regime>_seed<k>_cv.png      LOO-CV observed-vs-predicted

Run::

    python simulations/sim_bo_campaign.py                  # Tier-C, both regimes, 3 seeds
    python simulations/sim_bo_campaign.py --tiers C B      # add Tier-B Newton
    python simulations/sim_bo_campaign.py --seeds 0 1 2 3  # more seeds -> tighter bands
    python simulations/sim_bo_campaign.py --regime crutch --n-iter 60
"""
from __future__ import annotations

import argparse
import csv
import logging
import sys
import warnings
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import bo_evaluator as bo  # noqa: E402
from regimes import CRUTCH, NASA_LANDER, Regime  # noqa: E402

# Identical design box to PR #35 ``bo/t3_prism_sobol_batch.PARAMETERS``.
PARAMETERS = [
    {"name": "R_mm",       "type": "range", "bounds": [25.0,  40.0], "value_type": "float"},
    {"name": "H_mm",       "type": "range", "bounds": [60.0, 110.0], "value_type": "float"},
    {"name": "twist_deg",  "type": "range", "bounds": [40.0,  80.0], "value_type": "float"},
    {"name": "strut_d_mm", "type": "range", "bounds": [ 6.0,  12.0], "value_type": "float"},
    {"name": "cable_d_mm", "type": "range", "bounds": [ 3.0,   5.5], "value_type": "float"},
]
PARAM_NAMES = [p["name"] for p in PARAMETERS]

REGIMES: dict[str, Regime] = {"crutch": CRUTCH, "lander": NASA_LANDER}

# Per-tier objective definitions: (metric name, direction) where +1 = maximize,
# -1 = minimize.  Tier-C is the full 3-objective qNEHVI front; Tier-B (Newton)
# exposes only the payload-accel trace, so it is a single-objective campaign.
TIER_OBJECTIVES: dict[str, list[tuple[str, int]]] = {
    "C": [("F_peak_N", -1), ("SEA_J_per_g", +1), ("eta", +1)],
    "B": [("F_peak_N", -1)],
}
TIER_LABELS = {"C": "Tier-C (MuJoCo)", "B": "Tier-B (Newton/Warp)"}

REGIME_COLORS = {"crutch": "#1f77b4", "lander": "#d62728"}

# Penalty values for infeasible designs (mirrors ``bo_evaluator``); these sit
# far outside the achievable cloud so the GP can learn the feasibility boundary
# while they stay off the Pareto front.
_INFEASIBLE = {"F_peak_N": 5.0e4, "SEA_J_per_g": 1.0e-6, "eta": 1.0e-3}


# qNEHVI reference thresholds (the hyper-volume reference point).  Deliberately
# *outside* the achievable cloud so every feasible design contributes
# hyper-volume.  Tier-C F_peak sits near the static support load
# (see sobol_t3_analysis.md), so the threshold tracks payload weight.
def _thresholds(regime: Regime) -> dict[str, float]:
    static_weight_N = regime.payload_mass_kg * 9.81
    return {
        "F_peak_N": 1.5 * static_weight_N,
        "SEA_J_per_g": 0.0,
        "eta": 0.0,
    }


# --------------------------------------------------------------------------
# Per-tier evaluators.  Each returns ``(objectives_dict, feasible_bool)``.
# --------------------------------------------------------------------------
def _eval_tier_c(params: dict, regime: Regime, cfc180: bool) -> tuple[dict, bool]:
    design = bo.parameterization_to_design(params)
    feasible = not design.check()
    obj = bo.evaluate_design(params, regime=regime, fidelity="C", cfc180=cfc180)
    return obj, feasible


def _eval_tier_b(params: dict, regime: Regime, _cfc180: bool) -> tuple[dict, bool]:
    """Newton/Warp XPBD drop → minimize peak transmitted force.

    Newton builds the prism at the fixed equilibrium twist (the twist axis is
    not consumed at Tier-B, same limitation as the Sobol campaign), and only
    the payload-acceleration trace is available, so this is single-objective.
    """
    design = bo.parameterization_to_design(params)
    if design.check():
        return {"F_peak_N": _INFEASIBLE["F_peak_N"]}, False
    import newton_drop as nd

    builder, _pids, payload_pid = nd.build_model(
        radius_m=design.radius_m,
        height_m=design.height_m,
        strut_dia_m=design.strut_diameter_m,
        tendon_dia_m=design.tendon_diameter_m,
        payload_mass_kg=regime.payload_mass_kg,
        drop_height_m=0.05,
    )
    res = nd.simulate(builder, payload_pid, sim_time_s=0.05, dt=2.5e-5)
    az = np.asarray(res["payload_az"], dtype=float)
    finite = az[np.isfinite(az)]
    peak_g = float(np.max(np.abs(finite)) / 9.81) if finite.size else float("nan")
    if not np.isfinite(peak_g):
        return {"F_peak_N": _INFEASIBLE["F_peak_N"]}, False
    return {"F_peak_N": peak_g * 9.81 * regime.payload_mass_kg}, True


_EVALUATORS = {"C": _eval_tier_c, "B": _eval_tier_b}


def _make_objectives(tier: str, regime: Regime):
    from ax.service.ax_client import ObjectiveProperties

    if tier == "C":
        th = _thresholds(regime)
        return {
            "F_peak_N":    ObjectiveProperties(minimize=True,  threshold=th["F_peak_N"]),
            "SEA_J_per_g": ObjectiveProperties(minimize=False, threshold=th["SEA_J_per_g"]),
            "eta":         ObjectiveProperties(minimize=False, threshold=th["eta"]),
        }
    # Tier-B: single objective.
    return {"F_peak_N": ObjectiveProperties(minimize=True)}


# --------------------------------------------------------------------------
# Pareto helpers (used for the multi-objective Tier-C fronts).
# --------------------------------------------------------------------------
def _pareto_mask(objs: np.ndarray, directions: np.ndarray) -> np.ndarray:
    """Boolean mask of non-dominated rows (directions: +1 max, -1 min)."""
    z = objs * directions  # orient everything to "bigger is better"
    n = z.shape[0]
    keep = np.ones(n, dtype=bool)
    for i in range(n):
        if not keep[i]:
            continue
        for j in range(n):
            if i == j:
                continue
            if np.all(z[j] >= z[i]) and np.any(z[j] > z[i]):
                keep[i] = False
                break
    return keep


def _pareto_rows(rows: list[dict], tier: str) -> list[dict]:
    obj_names = [m for m, _ in TIER_OBJECTIVES[tier]]
    directions = np.array([d for _, d in TIER_OBJECTIVES[tier]], dtype=float)
    feasible = [r for r in rows if r["feasible"]]
    if not feasible:
        return []
    objs = np.array([[r[m] for m in obj_names] for r in feasible])
    mask = _pareto_mask(objs, directions)
    return [r for r, m in zip(feasible, mask) if m]


def _trial_stage(ax_client, idx: int) -> str:
    try:
        trial = ax_client.experiment.trials[idx]
        key = (trial.generator_runs[0]._model_key or "").lower()
    except Exception:
        return "bo"
    if "sobol" in key:
        return "sobol"
    if "manual" in key or not key:
        return "seed"
    return "bo"


# --------------------------------------------------------------------------
# Single campaign (one tier × one regime × one seed).
# --------------------------------------------------------------------------
def run_campaign(tier: str, regime_key: str, *, seed: int, n_iter: int,
                 cfc180: bool):
    """Run one closed-loop sim-only BO campaign.

    Returns ``(rows, ax_client)`` — the per-trial dict rows (params,
    objectives, stage, feasibility, seed) and the fitted AxClient (kept so the
    LOO-CV plot can refit its surrogate on the trial data).
    """
    from ax.service.ax_client import AxClient

    regime = REGIMES[regime_key]
    evaluate = _EVALUATORS[tier]
    obj_names = [m for m, _ in TIER_OBJECTIVES[tier]]

    ax_client = AxClient(random_seed=seed, verbose_logging=False)
    ax_client.create_experiment(
        name=f"sim_bo_{tier}_{regime_key}_seed{seed}",
        parameters=PARAMETERS,
        objectives=_make_objectives(tier, regime),
        overwrite_existing_experiment=True,
    )

    rows: list[dict] = []

    def _record(idx: int, params: dict, obj: dict, feasible: bool, stage: str):
        row = {"tier": tier, "regime": regime_key, "seed": seed,
               "trial": idx, "stage": stage, "feasible": bool(feasible)}
        row.update({k: float(params[k]) for k in PARAM_NAMES})
        # Fill every tier's objective slot (NaN where this tier doesn't score).
        for m in ("F_peak_N", "SEA_J_per_g", "eta"):
            row[m] = float(obj[m]) if m in obj else float("nan")
        rows.append(row)

    def _raw_data(obj: dict) -> dict:
        return {m: obj[m] for m in obj_names}

    # ---- 1. Seed with the already-printed PR #35 T3 cells -----------------
    for s in bo._t3_seed_designs():
        params = {k: float(s[k]) for k in PARAM_NAMES}
        obj, feasible = evaluate(params, regime, cfc180)
        idx = ax_client.attach_trial(params)[1]
        ax_client.complete_trial(idx, raw_data=_raw_data(obj))
        _record(idx, params, obj, feasible, stage="seed")

    # ---- 2. Closed-loop: Ax proposes, sim scores, feed back ---------------
    for _ in range(n_iter):
        params, idx = ax_client.get_next_trial()
        params = {k: float(params[k]) for k in PARAM_NAMES}
        obj, feasible = evaluate(params, regime, cfc180)
        ax_client.complete_trial(idx, raw_data=_raw_data(obj))
        _record(idx, params, obj, feasible, _trial_stage(ax_client, idx))

    fp = np.array([r["F_peak_N"] for r in rows])
    print(f"  [{tier}/{regime_key}/seed{seed}] {len(rows)} trials, "
          f"{sum(r['feasible'] for r in rows)} feasible, "
          f"F_peak {np.nanmin(fp):.1f}–{np.nanmax(fp):.1f} N")
    return rows, ax_client


# --------------------------------------------------------------------------
# CSV I/O.
# --------------------------------------------------------------------------
def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fieldnames = ["tier", "regime", "seed", "trial", "stage", "feasible",
                  *PARAM_NAMES, "F_peak_N", "SEA_J_per_g", "eta"]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})


# --------------------------------------------------------------------------
# Running-best (convergence) helper.
# --------------------------------------------------------------------------
def _running_best(values: np.ndarray, feasible: np.ndarray,
                  direction: int) -> np.ndarray:
    """Running best objective value at each evaluation (NaN until 1st feasible).

    Infeasible / non-finite evaluations do not update the running best, so the
    curve reflects only the best *feasible* design seen so far.
    """
    out = np.full(len(values), np.nan)
    best = None
    for i, (v, f) in enumerate(zip(values, feasible)):
        if f and np.isfinite(v):
            best = v if best is None else (min(best, v) if direction < 0
                                           else max(best, v))
        out[i] = best if best is not None else np.nan
    return out


def _seed_running_best(seed_rows: list[dict], metric: str,
                       direction: int) -> np.ndarray:
    ordered = sorted(seed_rows, key=lambda r: r["trial"])
    vals = np.array([r[metric] for r in ordered], dtype=float)
    feas = np.array([r["feasible"] for r in ordered], dtype=bool)
    return _running_best(vals, feas, direction)


# --------------------------------------------------------------------------
# Plotting.  Every figure is for a single (tier, regime) so the two regimes
# never share an axis (their scales differ by ~6×).
# --------------------------------------------------------------------------
def _import_plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def _objective_label(metric: str, direction: int) -> str:
    arrow = "lower better" if direction < 0 else "higher better"
    pretty = {"F_peak_N": "F_peak (N)", "SEA_J_per_g": "SEA (J/g)",
              "eta": "eta"}[metric]
    return f"best {pretty} — {arrow}"


def plot_seed_convergence(tier: str, regime_key: str, seed: int,
                          seed_rows: list[dict], outdir: Path) -> None:
    plt = _import_plt()
    objs = TIER_OBJECTIVES[tier]
    fig, axes = plt.subplots(1, len(objs), figsize=(4.8 * len(objs), 4.0),
                             squeeze=False)
    color = REGIME_COLORS[regime_key]
    for ax, (metric, direction) in zip(axes[0], objs):
        rb = _seed_running_best(seed_rows, metric, direction)
        ax.plot(np.arange(1, len(rb) + 1), rb, "-o", color=color, ms=3, lw=1.6)
        ax.set_xlabel("evaluation #")
        ax.set_ylabel(_objective_label(metric, direction))
        ax.grid(alpha=0.3)
    fig.suptitle(f"{TIER_LABELS[tier]} · {regime_key} · seed {seed} — "
                 f"running-best convergence")
    fig.tight_layout()
    fig.savefig(outdir / f"sim_bo_{tier}_{regime_key}_seed{seed}_convergence.png",
                dpi=130)
    plt.close(fig)


def plot_mean_convergence(tier: str, regime_key: str,
                          by_seed: dict[int, list[dict]], outdir: Path) -> None:
    """Mean running-best across seeds with a ±1σ std-dev band."""
    plt = _import_plt()
    objs = TIER_OBJECTIVES[tier]
    color = REGIME_COLORS[regime_key]
    fig, axes = plt.subplots(1, len(objs), figsize=(4.8 * len(objs), 4.0),
                             squeeze=False)
    for ax, (metric, direction) in zip(axes[0], objs):
        curves = [_seed_running_best(rows, metric, direction)
                  for rows in by_seed.values()]
        n = min(len(c) for c in curves)
        stack = np.array([c[:n] for c in curves])  # (seeds, evals)
        x = np.arange(1, n + 1)
        mean = np.nanmean(stack, axis=0)
        std = np.nanstd(stack, axis=0)
        # Faint individual-seed traces behind the mean.
        for c in stack:
            ax.plot(x, c, "-", color=color, lw=0.7, alpha=0.25)
        ax.plot(x, mean, "-", color=color, lw=2.2, label="mean")
        ax.fill_between(x, mean - std, mean + std, color=color, alpha=0.20,
                        label="±1σ across seeds")
        ax.set_xlabel("evaluation #")
        ax.set_ylabel(_objective_label(metric, direction))
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle(f"{TIER_LABELS[tier]} · {regime_key} — mean running-best "
                 f"(± std band, {len(by_seed)} seeds)")
    fig.tight_layout()
    fig.savefig(outdir / f"sim_bo_{tier}_{regime_key}_convergence.png", dpi=130)
    plt.close(fig)


def plot_seed_pareto(tier: str, regime_key: str, seed: int,
                     seed_rows: list[dict], outdir: Path) -> None:
    """F_peak↔SEA and F_peak↔eta scatter + Pareto front for a single seed."""
    if len(TIER_OBJECTIVES[tier]) < 2:
        return  # single-objective tier has no Pareto front
    plt = _import_plt()
    color = REGIME_COLORS[regime_key]
    feasible = [r for r in seed_rows if r["feasible"]]
    if not feasible:
        return
    pareto = _pareto_rows(seed_rows, tier)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    for ax, ykey, ylabel in (
        (axes[0], "SEA_J_per_g", "SEA (J/g)  [maximize]"),
        (axes[1], "eta", "eta  [maximize]"),
    ):
        x = [r["F_peak_N"] for r in feasible]
        y = [r[ykey] for r in feasible]
        ax.scatter(x, y, s=22, alpha=0.4, color=color, label="all feasible")
        if pareto:
            px = np.array([r["F_peak_N"] for r in pareto])
            py = np.array([r[ykey] for r in pareto])
            order = np.argsort(px)
            ax.plot(px[order], py[order], "-o", color=color, ms=6, lw=1.5,
                    label="Pareto")
        ax.set_xlabel("F_peak (N)  [minimize]")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle(f"{TIER_LABELS[tier]} · {regime_key} · seed {seed} — "
                 f"Pareto fronts")
    fig.tight_layout()
    fig.savefig(outdir / f"sim_bo_{tier}_{regime_key}_seed{seed}_pareto.png",
                dpi=130)
    plt.close(fig)


def _cv_signal(observed: np.ndarray, predicted: np.ndarray) -> tuple[float, float]:
    """Return (R², Spearman ρ) of predicted vs observed for a CV fold set."""
    from scipy.stats import spearmanr

    obs = np.asarray(observed, dtype=float)
    pred = np.asarray(predicted, dtype=float)
    ok = np.isfinite(obs) & np.isfinite(pred)
    obs, pred = obs[ok], pred[ok]
    if obs.size < 3 or np.allclose(obs, obs[0]):
        return float("nan"), float("nan")
    ss_res = float(np.sum((obs - pred) ** 2))
    ss_tot = float(np.sum((obs - obs.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    rho = float(spearmanr(obs, pred).statistic)
    return r2, rho


def plot_seed_cv(tier: str, regime_key: str, seed: int, ax_client,
                 outdir: Path) -> dict[str, tuple[float, float]]:
    """LOO-CV observed-vs-predicted per metric for one seed's fitted model.

    Uses Ax's built-in :func:`ax.adapter.cross_validation.cross_validate` on a
    BoTorch surrogate refit over the campaign's trial data — the standard way
    to check whether the GP has learned predictive signal for each outcome.
    Returns ``{metric: (R², Spearman ρ)}``.
    """
    from ax.adapter.cross_validation import cross_validate
    from ax.adapter.registry import Generators

    plt = _import_plt()
    obj_names = [m for m, _ in TIER_OBJECTIVES[tier]]

    try:
        adapter = Generators.BOTORCH_MODULAR(
            experiment=ax_client.experiment,
            data=ax_client.experiment.lookup_data(),
        )
        cv = cross_validate(adapter)
    except Exception as exc:  # pragma: no cover - model fit can fail on tiny data
        warnings.warn(f"cross_validate failed for {tier}/{regime_key}/seed{seed}: "
                      f"{exc!r}")
        return {}

    obs = {m: [] for m in obj_names}
    pred = {m: [] for m in obj_names}
    sem = {m: [] for m in obj_names}
    for res in cv:
        for m in obj_names:
            if m in res.observed.data.means_dict and m in res.predicted.means_dict:
                obs[m].append(res.observed.data.means_dict[m])
                pred[m].append(res.predicted.means_dict[m])
                sem[m].append(float(np.sqrt(max(
                    res.predicted.covariance_matrix[m][m], 0.0))))

    signal: dict[str, tuple[float, float]] = {}
    fig, axes = plt.subplots(1, len(obj_names), figsize=(4.6 * len(obj_names), 4.4),
                             squeeze=False)
    color = REGIME_COLORS[regime_key]
    for ax, m in zip(axes[0], obj_names):
        o = np.array(obs[m], dtype=float)
        p = np.array(pred[m], dtype=float)
        e = np.array(sem[m], dtype=float)
        r2, rho = _cv_signal(o, p)
        signal[m] = (r2, rho)
        ax.errorbar(o, p, yerr=e, fmt="o", color=color, ms=4, alpha=0.7,
                    ecolor="0.6", elinewidth=0.8, capsize=2)
        if o.size:
            lo = float(np.nanmin([o.min(), p.min()]))
            hi = float(np.nanmax([o.max(), p.max()]))
            pad = 0.05 * (hi - lo + 1e-12)
            ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], "k--", lw=1,
                    alpha=0.7)
        ax.set_xlabel(f"observed {m}")
        ax.set_ylabel(f"CV-predicted {m}")
        ax.set_title(f"{m}\nR²={r2:.2f}  ρ={rho:.2f}", fontsize=10)
        ax.grid(alpha=0.3)
    fig.suptitle(f"{TIER_LABELS[tier]} · {regime_key} · seed {seed} — "
                 f"LOO cross-validation (predictive signal)")
    fig.tight_layout()
    fig.savefig(outdir / f"sim_bo_{tier}_{regime_key}_seed{seed}_cv.png", dpi=130)
    plt.close(fig)
    return signal


# --------------------------------------------------------------------------
# Driver.
# --------------------------------------------------------------------------
def run_tier_regime(tier: str, regime_key: str, *, seeds: list[int],
                    n_iter: int, cfc180: bool, outdir: Path) -> None:
    print(f"\n=== sim-only BO: {TIER_LABELS[tier]} · {regime_key} "
          f"({len(seeds)} seeds × ({3}+{n_iter}) evals) ===")
    by_seed: dict[int, list[dict]] = {}
    clients: dict[int, object] = {}
    all_rows: list[dict] = []
    for seed in seeds:
        rows, ax_client = run_campaign(tier, regime_key, seed=seed,
                                       n_iter=n_iter, cfc180=cfc180)
        by_seed[seed] = rows
        clients[seed] = ax_client
        all_rows.extend(rows)

    _write_csv(outdir / f"sim_bo_{tier}_{regime_key}.csv", all_rows)
    _write_csv(outdir / f"sim_bo_{tier}_{regime_key}_pareto.csv",
               _pareto_rows(all_rows, tier))

    for seed in seeds:
        plot_seed_convergence(tier, regime_key, seed, by_seed[seed], outdir)
        plot_seed_pareto(tier, regime_key, seed, by_seed[seed], outdir)
        sig = plot_seed_cv(tier, regime_key, seed, clients[seed], outdir)
        if sig:
            txt = "  ".join(f"{m}:R²={r2:.2f}/ρ={rho:.2f}"
                            for m, (r2, rho) in sig.items())
            print(f"  [{tier}/{regime_key}/seed{seed}] LOO-CV  {txt}")
    plot_mean_convergence(tier, regime_key, by_seed, outdir)
    print(f"  -> wrote sim_bo_{tier}_{regime_key}.csv + per-seed/mean/CV figures")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tiers", nargs="+", choices=["C", "B"], default=["C"],
                        help="simulation tier(s) to run the BO loop on "
                             "(C=MuJoCo 3-obj, B=Newton single-obj)")
    parser.add_argument("--regime", choices=["crutch", "lander", "both"],
                        default="both", help="which loading regime(s) to run")
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2],
                        help="Ax random seeds (one campaign each; >1 enables "
                             "the std-dev band)")
    parser.add_argument("--n-iter", type=int, default=30,
                        help="closed-loop BO trials per campaign (after the 3 "
                             "seed designs) (default 30)")
    parser.add_argument("--raw-peak", action="store_true",
                        help="read raw (unfiltered) peak instead of CFC-180 "
                             "(Tier-C only)")
    parser.add_argument("--outdir", type=Path, default=_HERE / "outputs",
                        help="output directory")
    args = parser.parse_args(argv)

    logging.getLogger("ax").setLevel(logging.WARNING)
    warnings.filterwarnings("ignore", category=UserWarning, module="bo_evaluator")

    args.outdir.mkdir(parents=True, exist_ok=True)
    regime_keys = ["crutch", "lander"] if args.regime == "both" else [args.regime]

    for tier in args.tiers:
        for rk in regime_keys:
            run_tier_regime(tier, rk, seeds=args.seeds, n_iter=args.n_iter,
                            cfc180=not args.raw_peak, outdir=args.outdir)

    print(f"\nDone. Figures + CSVs under {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
