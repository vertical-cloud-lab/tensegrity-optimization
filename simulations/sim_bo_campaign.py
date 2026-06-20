"""Closed-loop Bayesian-optimization campaign over the PR #35 T3-prism box,
**evaluated entirely by simulation** (no printer, no drop-tower).

This is the simulation-only analogue of PR #35's `bo/t3_prism_sobol_batch.py`.
Where PR #35 emits a *single* Sobol batch for a human-in-the-loop print +
bench-test round, this script closes the loop: Ax proposes designs, the
Tier-C MuJoCo regime simulation (`bo_evaluator.evaluate_design`) scores them,
and the results are fed straight back to the Ax model so a multi-objective
qNEHVI surrogate drives the search.  Per @sgbaird (PR comment 4759514616):

    "run a Bayesian optimization campaign as you see fit using only
     simulations as the objective functions.  Mirror what's in #35, but
     using these kinds of simulations instead of real experiments."

Design box (identical to PR #35 `bo/t3_prism_sobol_batch.PARAMETERS`):

    R_mm        radius            [25, 40]
    H_mm        height            [60, 110]
    twist_deg   top-vs-bottom     [40, 80]
    strut_d_mm  PLA strut Ø       [6.0, 12.0]
    cable_d_mm  TPU cable Ø       [3.0, 5.5]

Frozen (matching PR #35): topology=t3_prism, tiling=1x1x1, tpu_shore=85A,
build_orientation=vertical, PLA struts / TPU cables.

Objectives (the same three PR #30 / `bo_evaluator` outcomes):

    F_peak_N      minimize   peak transmitted force (support-load proxy at
                             Tier-C — see sobol_t3_diagnostics.md)
    SEA_J_per_g   maximize   specific energy absorbed (elastic-energy proxy
                             at Tier-C)
    eta           maximize   compaction efficiency (mean/peak over pulse)

A separate campaign is run **per loading regime** (crutch, lander), because
the loading scenario is fixed inside a campaign while the design varies
(see bo_integration.md "Multi-task treatment of the regimes" for why a
single multi-task GP would eventually share information across the two;
here we keep them independent so the per-regime Pareto fronts stay legible).

The first trials are seeded with the three already-printed PR #35 T3 cells
(`bo_evaluator._t3_seed_designs()`), exactly the anchor-the-GP-on-hardware
sequence sketched in bo_integration.md, except the seed objectives are also
simulated here (this is a sim-only campaign).

Outputs (under ``simulations/outputs/``):

    sim_bo_<regime>.csv         full trial table (params + objectives + stage)
    sim_bo_<regime>_pareto.csv  Pareto-optimal subset
    sim_bo_pareto.png           F_peak↔SEA↔eta Pareto scatter, both regimes
    sim_bo_convergence.png      running-best objective vs trial, both regimes

Run::

    python simulations/sim_bo_campaign.py                 # both regimes, defaults
    python simulations/sim_bo_campaign.py --n-iter 40     # more BO trials
    python simulations/sim_bo_campaign.py --regime crutch # one regime only
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

OBJECTIVE_NAMES = ["F_peak_N", "SEA_J_per_g", "eta"]

# Designs that fail ``PrintableDesign.check()`` are scored with the penalised
# ``bo_evaluator._INFEASIBLE_F_PEAK_N`` (5e4 N); anything below this cutoff is
# a genuine (feasible) evaluation kept on the Pareto front / in the figures.
F_PEAK_FEASIBLE_MAX_N = 4.0e4

REGIMES: dict[str, Regime] = {"crutch": CRUTCH, "lander": NASA_LANDER}

# qNEHVI reference thresholds (the hypervolume reference point).  These are
# deliberately *outside* the achievable cloud so every feasible design
# contributes hypervolume.  F_peak is set above the regime's static payload
# weight band; SEA / eta floors are below anything a printable cell reaches.
# (Tier-C F_peak is near the static support load — see sobol_t3_analysis.md —
# so the threshold tracks payload weight.)
def _thresholds(regime: Regime) -> dict[str, float]:
    static_weight_N = regime.payload_mass_kg * 9.81
    return {
        "F_peak_N": 1.5 * static_weight_N,   # reference worse than any design
        "SEA_J_per_g": 0.0,
        "eta": 0.0,
    }


def _pareto_mask(objs: np.ndarray, directions: np.ndarray) -> np.ndarray:
    """Return a boolean mask of non-dominated rows.

    ``objs`` is (n, m); ``directions`` is (m,) with +1 = maximize, -1 =
    minimize.  Row i is dominated if some row j is >= on every objective
    and strictly > on at least one (after orienting all to maximization).
    """
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


def _trial_stage(ax_client, idx: int) -> str:
    """Best-effort label of which generator proposed trial ``idx``.

    Seeds are attached manually (``Manual``); Ax's default strategy then
    runs a Sobol init step before switching to the BoTorch/qNEHVI model.
    """
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


def run_campaign(regime_key: str, *, n_iter: int, seed: int,
                 cfc180: bool) -> list[dict]:
    """Run one closed-loop sim-only BO campaign for ``regime_key``.

    Returns a list of per-trial dict rows (params, objectives, stage).
    """
    from ax.service.ax_client import AxClient, ObjectiveProperties

    regime = REGIMES[regime_key]
    thresholds = _thresholds(regime)
    objectives = {
        "F_peak_N":    ObjectiveProperties(minimize=True,  threshold=thresholds["F_peak_N"]),
        "SEA_J_per_g": ObjectiveProperties(minimize=False, threshold=thresholds["SEA_J_per_g"]),
        "eta":         ObjectiveProperties(minimize=False, threshold=thresholds["eta"]),
    }

    ax_client = AxClient(random_seed=seed, verbose_logging=False)
    ax_client.create_experiment(
        name=f"sim_bo_{regime_key}",
        parameters=PARAMETERS,
        objectives=objectives,
        overwrite_existing_experiment=True,
    )

    rows: list[dict] = []

    def _evaluate(params: dict) -> dict[str, float]:
        return bo.evaluate_design(params, regime=regime, fidelity="C",
                                  cfc180=cfc180)

    def _record(idx: int, params: dict, obj: dict, stage: str) -> None:
        row = {"trial": idx, "regime": regime_key, "stage": stage}
        row.update({k: float(params[k]) for k in PARAM_NAMES})
        row.update({k: float(obj[k]) for k in OBJECTIVE_NAMES})
        rows.append(row)

    # ---- 1. Seed with the already-printed PR #35 T3 cells -----------------
    seeds = bo._t3_seed_designs()
    for s in seeds:
        params = {k: float(s[k]) for k in PARAM_NAMES}
        obj = _evaluate(params)
        idx = ax_client.attach_trial(params)[1]
        ax_client.complete_trial(idx, raw_data=obj)
        _record(idx, params, obj, stage="seed")
        print(f"  [{regime_key}] seed   trial {idx:>3}  "
              f"F_peak={obj['F_peak_N']:8.1f}  SEA={obj['SEA_J_per_g']:.2e}  "
              f"eta={obj['eta']:.3f}")

    # ---- 2. Closed-loop: Ax proposes, sim scores, feed back ---------------
    for _ in range(n_iter):
        params, idx = ax_client.get_next_trial()
        params = {k: float(params[k]) for k in PARAM_NAMES}
        obj = _evaluate(params)
        ax_client.complete_trial(idx, raw_data=obj)
        stage = _trial_stage(ax_client, idx)
        _record(idx, params, obj, stage=stage)
        print(f"  [{regime_key}] {stage:<6} trial {idx:>3}  "
              f"F_peak={obj['F_peak_N']:8.1f}  SEA={obj['SEA_J_per_g']:.2e}  "
              f"eta={obj['eta']:.3f}")

    return rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fieldnames = ["trial", "regime", "stage", *PARAM_NAMES, *OBJECTIVE_NAMES]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _pareto_rows(rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    directions = np.array([-1.0, +1.0, +1.0])  # min F_peak, max SEA, max eta
    objs = np.array([[r[k] for k in OBJECTIVE_NAMES] for r in rows])
    # Drop penalised (infeasible) rows from the front.
    finite = objs[:, 0] < F_PEAK_FEASIBLE_MAX_N
    mask = np.zeros(len(rows), dtype=bool)
    if finite.any():
        sub_mask = _pareto_mask(objs[finite], directions)
        mask[np.where(finite)[0][sub_mask]] = True
    return [r for r, m in zip(rows, mask) if m]


def make_figures(all_rows: dict[str, list[dict]], outdir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {"crutch": "#1f77b4", "lander": "#d62728"}

    # ---- Pareto scatter: F_peak vs SEA, point size ~ eta ------------------
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, ykey, ylabel in (
        (axes[0], "SEA_J_per_g", "SEA (J/g)  [maximize]"),
        (axes[1], "eta", "eta  [maximize]"),
    ):
        for rk, rows in all_rows.items():
            feasible = [r for r in rows if r["F_peak_N"] < F_PEAK_FEASIBLE_MAX_N]
            if not feasible:
                continue
            x = [r["F_peak_N"] for r in feasible]
            y = [r[ykey] for r in feasible]
            ax.scatter(x, y, s=18, alpha=0.35, color=colors[rk],
                       label=f"{rk} (all)")
            pr = _pareto_rows(rows)
            if pr:
                px = [r["F_peak_N"] for r in pr]
                py = [r[ykey] for r in pr]
                order = np.argsort(px)
                ax.plot(np.array(px)[order], np.array(py)[order],
                        "-o", color=colors[rk], ms=6, lw=1.5,
                        label=f"{rk} Pareto")
        ax.set_xlabel("F_peak (N)  [minimize]")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Sim-only BO (Tier-C MuJoCo): Pareto fronts over the PR #35 T3 box")
    fig.tight_layout()
    fig.savefig(outdir / "sim_bo_pareto.png", dpi=130)
    plt.close(fig)

    # ---- Convergence: running-best per objective vs trial -----------------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    for ax, key, best, label in (
        (axes[0], "F_peak_N", "min", "best F_peak (N) — lower better"),
        (axes[1], "SEA_J_per_g", "max", "best SEA (J/g) — higher better"),
        (axes[2], "eta", "max", "best eta — higher better"),
    ):
        for rk, rows in all_rows.items():
            feasible = [r for r in rows if r["F_peak_N"] < F_PEAK_FEASIBLE_MAX_N]
            if not feasible:
                continue
            vals = np.array([r[key] for r in feasible])
            running = np.minimum.accumulate(vals) if best == "min" \
                else np.maximum.accumulate(vals)
            ax.plot(np.arange(1, len(running) + 1), running,
                    "-", color=colors[rk], lw=1.8, label=rk)
        ax.set_xlabel("evaluation #")
        ax.set_ylabel(label)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Sim-only BO running-best objective vs evaluation")
    fig.tight_layout()
    fig.savefig(outdir / "sim_bo_convergence.png", dpi=130)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--regime", choices=["crutch", "lander", "both"],
                        default="both", help="which loading regime(s) to run")
    parser.add_argument("--n-iter", type=int, default=40,
                        help="closed-loop BO trials per regime (after the "
                             "3 seed + Sobol init) (default 40)")
    parser.add_argument("--seed", type=int, default=0, help="Ax random seed")
    parser.add_argument("--raw-peak", action="store_true",
                        help="read raw (unfiltered) peak instead of CFC-180")
    parser.add_argument("--outdir", type=Path,
                        default=_HERE / "outputs", help="output directory")
    args = parser.parse_args(argv)

    # Quiet Ax's very chatty INFO logging (keep warnings).
    logging.getLogger("ax").setLevel(logging.WARNING)
    warnings.filterwarnings("ignore", category=UserWarning, module="bo_evaluator")

    args.outdir.mkdir(parents=True, exist_ok=True)
    regime_keys = ["crutch", "lander"] if args.regime == "both" else [args.regime]

    all_rows: dict[str, list[dict]] = {}
    for rk in regime_keys:
        print(f"\n=== sim-only BO campaign: {rk} "
              f"(seed designs + {args.n_iter} closed-loop trials) ===")
        rows = run_campaign(rk, n_iter=args.n_iter, seed=args.seed,
                            cfc180=not args.raw_peak)
        all_rows[rk] = rows
        _write_csv(args.outdir / f"sim_bo_{rk}.csv", rows)
        pr = _pareto_rows(rows)
        _write_csv(args.outdir / f"sim_bo_{rk}_pareto.csv", pr)
        print(f"  -> {len(rows)} trials, {len(pr)} Pareto-optimal "
              f"(wrote sim_bo_{rk}.csv / sim_bo_{rk}_pareto.csv)")

    make_figures(all_rows, args.outdir)
    print(f"\nWrote figures: sim_bo_pareto.png, sim_bo_convergence.png "
          f"-> {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
