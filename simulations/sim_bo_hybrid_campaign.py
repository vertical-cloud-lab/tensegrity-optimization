"""Closed-loop **fair** Bayesian-optimization campaign — the *hybrid* of Route A
(constant-mass shape-ratio manifold) + Route B (size-aware intensive objectives
+ envelope/footprint outcome constraints), both inside **one** ``AxClient``
campaign per regime.

This is the implementation @sgbaird asked for in PR comment 4815305004 —
"update the BO script(s) based on completing the hybrid approach" — where the
hybrid is the recommendation worked out in
[`fair_evaluation_analysis.md`](fair_evaluation_analysis.md) §3-4 and endorsed by
the Edison mock review (task ``e43abed6``).  It is the fair-evaluation analogue
of the *unconstrained variable-size* baseline in
[`sim_bo_campaign.py`](sim_bo_campaign.py): same closed loop, same engine
(Tier-C MuJoCo via ``bo_evaluator``), same one-campaign-per-regime structure —
but the *coordinates, objectives, and constraints* are changed so the optimiser
can only trade **shape at a fixed mass**, never **size**, which is what removes
the ~6× size confound that let the baseline "just get bigger" to win SEA.

What the hybrid changes vs ``sim_bo_campaign.py``
-------------------------------------------------

**Route A — constant-mass shape-ratio manifold (the search box).**
Instead of the PR #35 mm box (``R_mm``/``H_mm``/``twist_deg``/``strut_d_mm``/
``cable_d_mm``) where cell mass floats 4–6×, the campaign searches four
*dimensionless* shape ratios at a **fixed cell mass** ``m*`` (``--mass-g``):

    h_over_r            aspect ratio        H / R           [1.5, 4.4]
    h_over_strut_d      strut slenderness   H / strut_d     [5,   18]
    cable_over_strut_d  tendon/strut Ø      cable_d/strut_d [0.25, 0.92]
    twist_deg           equilibrium twist   (CAD/PR #35)    [40,  80]

``bo_evaluator.design_from_shape_ratios`` solves the single overall scale (a
closed-form cube root) so every design the GP sees weighs exactly ``m*`` grams.
SEA's denominator is then constant by construction.

**Route B — intensive objectives + envelope/footprint outcome constraints.**
The campaign scores the **intensive, size-aware** objectives recommended in
§3 (and by Edison):

    impact_F_N    minimize   impact channel — the **base floor-reaction** peak
                             for the lander (``bo_evaluator.base_reaction_peak_N``,
                             the sensorized-platen observable), the payload-accel
                             ``F_peak`` for the crutch (whose large soft cell
                             barely loads the floor, making base-reaction
                             degenerate; see ``sobol_t3_diagnostics.md``)
    SEA_J_per_g   maximize   mass-specific energy absorbed (cell only)
    SEA_J_per_cm3 maximize   **volume-specific** energy absorbed — the volumetric
                             budget the variable-size baseline hid
    eta           maximize   compaction efficiency (square-pulse-ness)

and carries the *remaining* budgets as Ax **outcome constraints** (mass is
already structurally fixed by Route A, so it is *not* a constraint):

    envelope_cm3  <= V*        (stowage / fairing volume; ``--envelope-max-cm3``)
    footprint_mm2 in [A_min, A_max]  (ground-pressure / stability; ``--footprint-*``)

Ax runs **constrained qNEHVI** automatically once a multi-objective experiment is
given ``outcome_constraints`` (BOTORCH_MODULAR).

A separate campaign is run **per loading regime** (crutch, lander) **per random
seed** (the regime is fixed inside a campaign; repeating across seeds gives the
±1σ band).  Each campaign is **seeded with the three already-printed PR #35 T3
cells projected onto the constant-mass manifold** (their shape ratios, re-scaled
to ``m*``), so the loop warm-starts from real hardware shapes.

Outputs (under ``simulations/outputs/``), one set per regime:

    sim_bo_hybrid_<regime>.csv                 all trials, all seeds
    sim_bo_hybrid_<regime>_pareto.csv          feasible Pareto subset (union)
    sim_bo_hybrid_<regime>_seed<k>_convergence.png   per-seed running-best
    sim_bo_hybrid_<regime>_convergence.png     mean running-best ± std band
    sim_bo_hybrid_<regime>_seed<k>_pareto.png  per-seed Pareto scatter
    sim_bo_hybrid_<regime>_feasibility.png     constraint-feasible fraction
    sim_bo_hybrid_<regime>_seed<k>_cv.png      LOO-CV observed-vs-predicted
    sim_bo_hybrid_<regime>_cv_summary.csv      predictive-signal table

Run::

    python simulations/sim_bo_hybrid_campaign.py                 # both regimes, 3 seeds, m*=30 g
    python simulations/sim_bo_hybrid_campaign.py --regime lander --mass-g 25
    python simulations/sim_bo_hybrid_campaign.py --seeds 0 1 2 3 --n-iter 40
    python simulations/sim_bo_hybrid_campaign.py --envelope-max-cm3 200 \
        --footprint-min-mm2 110 --footprint-max-mm2 190
"""
from __future__ import annotations

import argparse
import csv
import logging
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import bo_evaluator as bo  # noqa: E402
from regimes import CRUTCH, NASA_LANDER, Regime  # noqa: E402

# --------------------------------------------------------------------------
# Route A: the scale-free shape-ratio search box (mass is *not* a search axis —
# it is fixed at m* and consumed by design_from_shape_ratios).  Ranges chosen so
# the manifold spans the same shapes the PR #35 mm box reaches (H/R, H/strut_d,
# cable_d/strut_d, twist), per fair_evaluation_analysis.md §3.
# --------------------------------------------------------------------------
RATIO_PARAMETERS = [
    {"name": "h_over_r",           "type": "range", "bounds": [1.5,  4.4],  "value_type": "float"},
    {"name": "h_over_strut_d",     "type": "range", "bounds": [5.0,  18.0], "value_type": "float"},
    {"name": "cable_over_strut_d", "type": "range", "bounds": [0.25, 0.92], "value_type": "float"},
    {"name": "twist_deg",          "type": "range", "bounds": [40.0, 80.0], "value_type": "float"},
]
RATIO_NAMES = [p["name"] for p in RATIO_PARAMETERS]

# The four intensive objectives (metric, +1 maximize / -1 minimize).
OBJECTIVES: list[tuple[str, int]] = [
    ("impact_F_N",    -1),
    ("SEA_J_per_g",   +1),
    ("SEA_J_per_cm3", +1),
    ("eta",           +1),
]
OBJ_NAMES = [m for m, _ in OBJECTIVES]

# The Route-B outcome constraints (geometry metrics returned by the evaluator).
CONSTRAINT_NAMES = ["envelope_cm3", "footprint_mm2"]

REGIME_COLORS = {"crutch": "#1f77b4", "lander": "#d62728"}


@dataclass(frozen=True)
class HybridConfig:
    """Per-regime hybrid settings (Route A mass + Route B constraints/channel)."""
    key: str
    regime: Regime
    mass_g: float
    envelope_max_cm3: float
    footprint_min_mm2: float
    footprint_max_mm2: float
    impact_metric: str          # which evaluator key feeds the impact objective
    base_reaction: bool         # run the extra floor-reaction drop?


# Default budgets.  m* sits mid-range of the three printed PR #35 cells
# (14–82 g); the envelope/footprint bounds are set so they bind on a meaningful
# fraction of the m*=30 g shape manifold (percentiles measured over a 256-point
# Sobol set: envelope median ~208 cm³, footprint median ~130 mm²).  All are
# overridable on the CLI; real lander budgets are a systems-engineering input
# (fair_evaluation_analysis.md §4 step 3).
DEFAULT_MASS_G = 30.0
DEFAULT_ENVELOPE_MAX_CM3 = 250.0
DEFAULT_FOOTPRINT_MIN_MM2 = 100.0
DEFAULT_FOOTPRINT_MAX_MM2 = 200.0


def make_config(regime_key: str, *, mass_g: float, envelope_max_cm3: float,
                footprint_min_mm2: float, footprint_max_mm2: float) -> HybridConfig:
    """Build the per-regime hybrid config.

    The **lander** uses the base floor-reaction peak as its impact channel (the
    sensorized-platen observable, not the support-load proxy); the **crutch**
    keeps payload-accel ``F_peak`` because its large soft cell barely loads the
    floor in the contact window, which makes the base-reaction channel
    degenerate (``sobol_t3_diagnostics.md``).
    """
    regime = {"crutch": CRUTCH, "lander": NASA_LANDER}[regime_key]
    use_base = regime_key == "lander"
    return HybridConfig(
        key=regime_key, regime=regime, mass_g=float(mass_g),
        envelope_max_cm3=float(envelope_max_cm3),
        footprint_min_mm2=float(footprint_min_mm2),
        footprint_max_mm2=float(footprint_max_mm2),
        impact_metric="F_base_peak_N" if use_base else "F_peak_N",
        base_reaction=use_base,
    )


# --------------------------------------------------------------------------
# Evaluator: shape ratios + fixed mass -> the four intensive objectives plus
# the geometry-constraint metrics.
# --------------------------------------------------------------------------
def evaluate_ratios(ratios: dict, cfg: HybridConfig, *, cfc180: bool) -> dict:
    """Score one shape-ratio point on the constant-mass manifold.

    Returns a dict with every objective (``impact_F_N``, ``SEA_J_per_g``,
    ``SEA_J_per_cm3``, ``eta``) and constraint metric (``envelope_cm3``,
    ``footprint_mm2``), plus ``cell_mass_g`` (should equal ``cfg.mass_g`` to
    machine precision) and the booleans ``printable`` / ``within_budget`` /
    ``feasible``.
    """
    design = bo.design_from_shape_ratios(
        mass_g=cfg.mass_g,
        h_over_r=float(ratios["h_over_r"]),
        h_over_strut_d=float(ratios["h_over_strut_d"]),
        cable_over_strut_d=float(ratios["cable_over_strut_d"]),
        twist_deg=float(ratios["twist_deg"]),
    )
    printable = not design.check()
    res = bo.evaluate_printable_design(
        design, regime=cfg.regime, fidelity="C", cfc180=cfc180,
        base_reaction=cfg.base_reaction)

    impact = float(res.get(cfg.impact_metric, res["F_peak_N"]))
    envelope = float(res["envelope_cm3"])
    footprint = float(res["footprint_mm2"])
    within_budget = (envelope <= cfg.envelope_max_cm3
                     and cfg.footprint_min_mm2 <= footprint <= cfg.footprint_max_mm2)
    return {
        "impact_F_N":    impact,
        "SEA_J_per_g":   float(res["SEA_J_per_g"]),
        "SEA_J_per_cm3": float(res["SEA_J_per_cm3"]),
        "eta":           float(res["eta"]),
        "envelope_cm3":  envelope,
        "footprint_mm2": footprint,
        "cell_mass_g":   float(res["cell_mass_g"]),
        "printable":     bool(printable),
        "within_budget": bool(within_budget),
        "feasible":      bool(printable and within_budget),
    }


def _make_objectives():
    """Ax ObjectiveProperties for the four intensive objectives.

    Thresholds (the qNEHVI reference point) are left to Ax to infer from the
    observed nadir — robust across the four heterogeneous objective scales
    (base-reaction force ~kN vs SEA ~1e-4 J/g vs eta ~1) without brittle
    hand-tuned reference points.
    """
    from ax.service.ax_client import ObjectiveProperties

    return {m: ObjectiveProperties(minimize=(d < 0)) for m, d in OBJECTIVES}


def _outcome_constraints(cfg: HybridConfig) -> list[str]:
    """Route-B outcome constraints as absolute Ax constraint strings.

    Mass is *not* here — Route A fixes it structurally on the manifold.
    """
    return [
        f"envelope_cm3 <= {cfg.envelope_max_cm3}",
        f"footprint_mm2 <= {cfg.footprint_max_mm2}",
        f"footprint_mm2 >= {cfg.footprint_min_mm2}",
    ]


# --------------------------------------------------------------------------
# Pareto helpers (4-objective non-dominated set over budget-feasible designs).
# --------------------------------------------------------------------------
def _pareto_mask(objs: np.ndarray, directions: np.ndarray) -> np.ndarray:
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


def _pareto_rows(rows: list[dict]) -> list[dict]:
    directions = np.array([d for _, d in OBJECTIVES], dtype=float)
    feasible = [r for r in rows if r["feasible"]]
    if not feasible:
        return []
    objs = np.array([[r[m] for m in OBJ_NAMES] for r in feasible])
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
# Seed projection: the three printed PR #35 T3 cells, mapped onto the manifold.
# --------------------------------------------------------------------------
def _seed_ratio_points() -> list[dict]:
    """Shape ratios of the three already-printed PR #35 T3 cells.

    Each printed cell is projected onto the constant-mass manifold by taking its
    four shape ratios (its own mass is dropped — the campaign re-scales it to
    ``m*``), so the loop warm-starts from real hardware *shapes*.
    """
    pts = []
    for s in bo._t3_seed_designs():
        params = {k: float(s[k]) for k in
                  ("R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm")}
        design = bo.parameterization_to_design(params)
        r = bo.design_to_shape_ratios(design)
        pts.append({k: float(r[k]) for k in RATIO_NAMES})
    return pts


# --------------------------------------------------------------------------
# Single campaign (one regime × one seed).
# --------------------------------------------------------------------------
def run_campaign(cfg: HybridConfig, *, seed: int, n_iter: int, cfc180: bool):
    """Run one closed-loop hybrid campaign; return ``(rows, ax_client)``."""
    from ax.service.ax_client import AxClient

    ax_client = AxClient(random_seed=seed, verbose_logging=False)
    ax_client.create_experiment(
        name=f"sim_bo_hybrid_{cfg.key}_seed{seed}",
        parameters=RATIO_PARAMETERS,
        objectives=_make_objectives(),
        outcome_constraints=_outcome_constraints(cfg),
        overwrite_existing_experiment=True,
    )

    rows: list[dict] = []

    def _record(idx, ratios, obj, stage):
        row = {"regime": cfg.key, "seed": seed, "trial": idx, "stage": stage}
        row.update({k: float(ratios[k]) for k in RATIO_NAMES})
        row.update({k: obj[k] for k in (
            "impact_F_N", "SEA_J_per_g", "SEA_J_per_cm3", "eta",
            "envelope_cm3", "footprint_mm2", "cell_mass_g",
            "printable", "within_budget", "feasible")})
        rows.append(row)

    def _raw(obj):
        # Ax needs every objective + constraint metric in raw_data.
        return {m: obj[m] for m in (*OBJ_NAMES, *CONSTRAINT_NAMES)}

    # ---- 1. Seed with the printed PR #35 cells (projected to the manifold) --
    for ratios in _seed_ratio_points():
        obj = evaluate_ratios(ratios, cfg, cfc180=cfc180)
        idx = ax_client.attach_trial(ratios)[1]
        ax_client.complete_trial(idx, raw_data=_raw(obj))
        _record(idx, ratios, obj, "seed")

    # ---- 2. Closed loop: Ax proposes, sim scores, feed back -----------------
    for _ in range(n_iter):
        ratios, idx = ax_client.get_next_trial()
        ratios = {k: float(ratios[k]) for k in RATIO_NAMES}
        obj = evaluate_ratios(ratios, cfg, cfc180=cfc180)
        ax_client.complete_trial(idx, raw_data=_raw(obj))
        _record(idx, ratios, obj, _trial_stage(ax_client, idx))

    fp = np.array([r["impact_F_N"] for r in rows])
    nfeas = sum(r["feasible"] for r in rows)
    print(f"  [hybrid/{cfg.key}/seed{seed}] {len(rows)} trials, "
          f"{nfeas} budget-feasible, impact_F {np.nanmin(fp):.1f}–"
          f"{np.nanmax(fp):.1f} N (m*={cfg.mass_g:g} g)")
    return rows, ax_client


# --------------------------------------------------------------------------
# CSV I/O.
# --------------------------------------------------------------------------
_CSV_FIELDS = ["regime", "seed", "trial", "stage", *RATIO_NAMES,
               "impact_F_N", "SEA_J_per_g", "SEA_J_per_cm3", "eta",
               "envelope_cm3", "footprint_mm2", "cell_mass_g",
               "printable", "within_budget", "feasible"]


def _write_csv(path: Path, rows: list[dict],
               fieldnames: list[str] | None = None) -> None:
    if not rows:
        return
    fieldnames = fieldnames or _CSV_FIELDS
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})


# --------------------------------------------------------------------------
# Running-best (convergence) helper — only feasible designs update the best.
# --------------------------------------------------------------------------
def _running_best(values: np.ndarray, feasible: np.ndarray,
                  direction: int) -> np.ndarray:
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
    feas = np.array([bool(r["feasible"]) for r in ordered], dtype=bool)
    return _running_best(vals, feas, direction)


# --------------------------------------------------------------------------
# Plotting.  Every figure is for a single regime (the two regimes never share an
# axis — their objective scales differ by ~6×).
# --------------------------------------------------------------------------
def _import_plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


_PRETTY = {"impact_F_N": "impact F (N)", "SEA_J_per_g": "SEA (J/g)",
           "SEA_J_per_cm3": "SEA (J/cm³)", "eta": "eta"}


def _objective_label(metric: str, direction: int) -> str:
    arrow = "lower better" if direction < 0 else "higher better"
    return f"best {_PRETTY[metric]} — {arrow}"


def plot_seed_convergence(cfg: HybridConfig, seed: int, seed_rows: list[dict],
                          outdir: Path) -> None:
    plt = _import_plt()
    fig, axes = plt.subplots(1, len(OBJECTIVES),
                             figsize=(4.4 * len(OBJECTIVES), 4.0), squeeze=False)
    color = REGIME_COLORS[cfg.key]
    for ax, (metric, direction) in zip(axes[0], OBJECTIVES):
        rb = _seed_running_best(seed_rows, metric, direction)
        ax.plot(np.arange(1, len(rb) + 1), rb, "-o", color=color, ms=3, lw=1.6)
        ax.set_xlabel("evaluation #")
        ax.set_ylabel(_objective_label(metric, direction))
        ax.grid(alpha=0.3)
    fig.suptitle(f"hybrid (constant-mass {cfg.mass_g:g} g) · {cfg.key} · "
                 f"seed {seed} — running-best convergence")
    fig.tight_layout()
    fig.savefig(outdir / f"sim_bo_hybrid_{cfg.key}_seed{seed}_convergence.png",
                dpi=130)
    plt.close(fig)


def plot_mean_convergence(cfg: HybridConfig, by_seed: dict[int, list[dict]],
                          outdir: Path) -> None:
    plt = _import_plt()
    color = REGIME_COLORS[cfg.key]
    fig, axes = plt.subplots(1, len(OBJECTIVES),
                             figsize=(4.4 * len(OBJECTIVES), 4.0), squeeze=False)
    for ax, (metric, direction) in zip(axes[0], OBJECTIVES):
        curves = [_seed_running_best(rows, metric, direction)
                  for rows in by_seed.values()]
        n = min(len(c) for c in curves)
        stack = np.array([c[:n] for c in curves])
        x = np.arange(1, n + 1)
        mean = np.nanmean(stack, axis=0)
        std = np.nanstd(stack, axis=0)
        for c in stack:
            ax.plot(x, c, "-", color=color, lw=0.7, alpha=0.25)
        ax.plot(x, mean, "-", color=color, lw=2.2, label="mean")
        ax.fill_between(x, mean - std, mean + std, color=color, alpha=0.20,
                        label="±1σ across seeds")
        ax.set_xlabel("evaluation #")
        ax.set_ylabel(_objective_label(metric, direction))
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle(f"hybrid (constant-mass {cfg.mass_g:g} g) · {cfg.key} — "
                 f"mean running-best (± std band, {len(by_seed)} seeds)")
    fig.tight_layout()
    fig.savefig(outdir / f"sim_bo_hybrid_{cfg.key}_convergence.png", dpi=130)
    plt.close(fig)


def plot_seed_pareto(cfg: HybridConfig, seed: int, seed_rows: list[dict],
                     outdir: Path) -> None:
    """impact_F↔SEA_J_per_g and SEA_J_per_cm3↔eta scatter + Pareto front."""
    plt = _import_plt()
    color = REGIME_COLORS[cfg.key]
    feasible = [r for r in seed_rows if r["feasible"]]
    if not feasible:
        return
    pareto = _pareto_rows(seed_rows)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    panels = [
        (axes[0], "impact_F_N", "SEA_J_per_g",
         "impact F (N)  [minimize]", "SEA (J/g)  [maximize]"),
        (axes[1], "SEA_J_per_cm3", "eta",
         "SEA (J/cm³)  [maximize]", "eta  [maximize]"),
    ]
    for ax, xkey, ykey, xlabel, ylabel in panels:
        ax.scatter([r[xkey] for r in feasible], [r[ykey] for r in feasible],
                   s=22, alpha=0.4, color=color, label="budget-feasible")
        if pareto:
            px = np.array([r[xkey] for r in pareto])
            py = np.array([r[ykey] for r in pareto])
            order = np.argsort(px)
            ax.plot(px[order], py[order], "-o", color=color, ms=6, lw=1.5,
                    label="Pareto (4-obj)")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle(f"hybrid (constant-mass {cfg.mass_g:g} g) · {cfg.key} · "
                 f"seed {seed} — intensive-objective trades")
    fig.tight_layout()
    fig.savefig(outdir / f"sim_bo_hybrid_{cfg.key}_seed{seed}_pareto.png",
                dpi=130)
    plt.close(fig)


def plot_feasibility(cfg: HybridConfig, all_rows: list[dict],
                     outdir: Path) -> None:
    """Constraint-feasible fraction over evaluation order (qNEHVI learning the
    Route-B budget boundary)."""
    plt = _import_plt()
    color = REGIME_COLORS[cfg.key]
    ordered = sorted(all_rows, key=lambda r: r["trial"])
    by_trial: dict[int, list[bool]] = {}
    for r in ordered:
        by_trial.setdefault(int(r["trial"]), []).append(bool(r["feasible"]))
    trials = sorted(by_trial)
    frac = [float(np.mean(by_trial[t])) for t in trials]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(trials, frac, "-o", color=color, ms=3)
    ax.axhline(np.mean([bool(r["feasible"]) for r in all_rows]), ls="--",
               color="0.5", label="campaign mean")
    ax.set_xlabel("evaluation #")
    ax.set_ylabel("fraction within envelope/footprint budget")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_title(f"hybrid · {cfg.key} — Route-B constraint feasibility "
                 f"(V≤{cfg.envelope_max_cm3:g} cm³, footprint "
                 f"∈[{cfg.footprint_min_mm2:g},{cfg.footprint_max_mm2:g}] mm²)")
    fig.tight_layout()
    fig.savefig(outdir / f"sim_bo_hybrid_{cfg.key}_feasibility.png", dpi=130)
    plt.close(fig)


def _cv_signal(observed: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    """Range-normalized predictive-signal diagnostics (r2/rho/nrmse/null_skill).

    Mirrors ``sim_bo_campaign._cv_signal`` so a tiny-variance outcome is not
    mistaken for model failure (Edison review 491f90ae)."""
    from scipy.stats import spearmanr

    obs = np.asarray(observed, dtype=float)
    pred = np.asarray(predicted, dtype=float)
    ok = np.isfinite(obs) & np.isfinite(pred)
    obs, pred = obs[ok], pred[ok]
    nan = {"r2": float("nan"), "rho": float("nan"), "nrmse": float("nan"),
           "null_skill": float("nan"), "n": int(obs.size)}
    if obs.size < 3 or np.allclose(obs, obs[0]):
        return nan
    ss_res = float(np.sum((obs - pred) ** 2))
    ss_tot = float(np.sum((obs - obs.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    rho = float(spearmanr(obs, pred).statistic)
    rmse_gp = float(np.sqrt(ss_res / obs.size))
    rmse_null = float(np.sqrt(ss_tot / obs.size))
    rng = float(obs.max() - obs.min())
    nrmse = rmse_gp / rng if rng > 0 else float("nan")
    null_skill = 1.0 - rmse_gp / rmse_null if rmse_null > 0 else float("nan")
    return {"r2": r2, "rho": rho, "nrmse": nrmse, "null_skill": null_skill,
            "n": int(obs.size)}


def plot_seed_cv(cfg: HybridConfig, seed: int, ax_client,
                 outdir: Path) -> dict[str, dict[str, float]]:
    """LOO-CV observed-vs-predicted per objective for one seed's fitted model."""
    from ax.adapter.cross_validation import cross_validate
    from ax.adapter.registry import Generators

    plt = _import_plt()
    try:
        adapter = Generators.BOTORCH_MODULAR(
            experiment=ax_client.experiment,
            data=ax_client.experiment.lookup_data(),
        )
        cv = cross_validate(adapter)
    except Exception as exc:  # pragma: no cover - model fit can fail on tiny data
        warnings.warn(f"cross_validate failed for hybrid/{cfg.key}/seed{seed}: "
                      f"{exc!r}")
        return {}

    obs = {m: [] for m in OBJ_NAMES}
    pred = {m: [] for m in OBJ_NAMES}
    sem = {m: [] for m in OBJ_NAMES}
    for res in cv:
        for m in OBJ_NAMES:
            if m in res.observed.data.means_dict and m in res.predicted.means_dict:
                obs[m].append(res.observed.data.means_dict[m])
                pred[m].append(res.predicted.means_dict[m])
                sem[m].append(float(np.sqrt(max(
                    res.predicted.covariance_matrix[m][m], 0.0))))

    signal: dict[str, dict[str, float]] = {}
    fig, axes = plt.subplots(1, len(OBJ_NAMES),
                             figsize=(4.4 * len(OBJ_NAMES), 4.4), squeeze=False)
    color = REGIME_COLORS[cfg.key]
    for ax, m in zip(axes[0], OBJ_NAMES):
        o = np.array(obs[m], dtype=float)
        p = np.array(pred[m], dtype=float)
        e = np.array(sem[m], dtype=float)
        sig = _cv_signal(o, p)
        signal[m] = sig
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
        ax.set_title(f"{m}\nR²={sig['r2']:.2f}  ρ={sig['rho']:.2f}\n"
                     f"NRMSE={sig['nrmse']:.3f}  null-skill={sig['null_skill']:.2f}",
                     fontsize=9)
        ax.grid(alpha=0.3)
    fig.suptitle(f"hybrid · {cfg.key} · seed {seed} — LOO cross-validation "
                 f"(predictive signal)")
    fig.tight_layout()
    fig.savefig(outdir / f"sim_bo_hybrid_{cfg.key}_seed{seed}_cv.png", dpi=130)
    plt.close(fig)
    return signal


# --------------------------------------------------------------------------
# Driver.
# --------------------------------------------------------------------------
def run_regime(cfg: HybridConfig, *, seeds: list[int], n_iter: int,
               cfc180: bool, outdir: Path) -> None:
    n_seed = len(_seed_ratio_points())
    print(f"\n=== hybrid fair BO · {cfg.key} "
          f"(constant mass {cfg.mass_g:g} g; {len(seeds)} seeds × "
          f"({n_seed}+{n_iter}) evals) ===")
    by_seed: dict[int, list[dict]] = {}
    clients: dict[int, object] = {}
    all_rows: list[dict] = []
    for seed in seeds:
        rows, ax_client = run_campaign(cfg, seed=seed, n_iter=n_iter,
                                       cfc180=cfc180)
        by_seed[seed] = rows
        clients[seed] = ax_client
        all_rows.extend(rows)

    _write_csv(outdir / f"sim_bo_hybrid_{cfg.key}.csv", all_rows)
    _write_csv(outdir / f"sim_bo_hybrid_{cfg.key}_pareto.csv",
               _pareto_rows(all_rows))

    cv_summary: list[dict] = []
    for seed in seeds:
        plot_seed_convergence(cfg, seed, by_seed[seed], outdir)
        plot_seed_pareto(cfg, seed, by_seed[seed], outdir)
        sig = plot_seed_cv(cfg, seed, clients[seed], outdir)
        if sig:
            txt = "  ".join(
                f"{m}:R²={s['r2']:.2f}/ρ={s['rho']:.2f}/"
                f"NRMSE={s['nrmse']:.3f}/null-skill={s['null_skill']:.2f}"
                for m, s in sig.items())
            print(f"  [hybrid/{cfg.key}/seed{seed}] LOO-CV  {txt}")
            for m, s in sig.items():
                cv_summary.append({"regime": cfg.key, "seed": seed,
                                   "metric": m, **s})
    if cv_summary:
        _write_csv(outdir / f"sim_bo_hybrid_{cfg.key}_cv_summary.csv", cv_summary,
                   fieldnames=["regime", "seed", "metric", "r2", "rho",
                               "nrmse", "null_skill", "n"])
    plot_mean_convergence(cfg, by_seed, outdir)
    plot_feasibility(cfg, all_rows, outdir)
    print(f"  -> wrote sim_bo_hybrid_{cfg.key}.csv + per-seed/mean/CV/feasibility "
          f"figures")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--regime", choices=["crutch", "lander", "both"],
                        default="both", help="which loading regime(s) to run")
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2],
                        help="Ax random seeds (one campaign each; >1 enables the "
                             "std-dev band)")
    parser.add_argument("--n-iter", type=int, default=30,
                        help="closed-loop BO trials per campaign (after the 3 "
                             "seed designs) (default 30)")
    parser.add_argument("--mass-g", type=float, default=DEFAULT_MASS_G,
                        help="Route-A constant cell mass m* in grams "
                             f"(default {DEFAULT_MASS_G:g})")
    parser.add_argument("--envelope-max-cm3", type=float,
                        default=DEFAULT_ENVELOPE_MAX_CM3,
                        help="Route-B envelope-volume constraint V* (cm³)")
    parser.add_argument("--footprint-min-mm2", type=float,
                        default=DEFAULT_FOOTPRINT_MIN_MM2,
                        help="Route-B minimum strut-tip footprint A_min (mm²)")
    parser.add_argument("--footprint-max-mm2", type=float,
                        default=DEFAULT_FOOTPRINT_MAX_MM2,
                        help="Route-B maximum strut-tip footprint A_max (mm²)")
    parser.add_argument("--raw-peak", action="store_true",
                        help="read raw (unfiltered) peak instead of CFC-180")
    parser.add_argument("--outdir", type=Path, default=_HERE / "outputs",
                        help="output directory")
    args = parser.parse_args(argv)

    logging.getLogger("ax").setLevel(logging.WARNING)
    warnings.filterwarnings("ignore", category=UserWarning, module="bo_evaluator")

    args.outdir.mkdir(parents=True, exist_ok=True)
    regime_keys = ["crutch", "lander"] if args.regime == "both" else [args.regime]

    for rk in regime_keys:
        cfg = make_config(
            rk, mass_g=args.mass_g, envelope_max_cm3=args.envelope_max_cm3,
            footprint_min_mm2=args.footprint_min_mm2,
            footprint_max_mm2=args.footprint_max_mm2)
        run_regime(cfg, seeds=args.seeds, n_iter=args.n_iter,
                   cfc180=not args.raw_peak, outdir=args.outdir)

    print(f"\nDone. Figures + CSVs under {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
