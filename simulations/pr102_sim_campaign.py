"""The PR #102 campaign, run closed-loop against simulations instead of prints.

PR #102's ``bo/t3_prism_bo_campaign.py`` is a *one-shot* script by necessity:
its objective function is a print plus a 101-drop session, so it ingests the
measured batch, suggests the next nine articles and exits.  This script is
the same campaign with ``drop_tower_sim`` in place of the drop tower, which
makes it a closed loop and therefore lets it be repeated from different
initial seeds to see how much of the outcome is the optimizer and how much
is the draw.

Matched to PR #102, deliberately:

* the same five-parameter search space (the PR #35 base Sobol box),
* the same two minimized objectives, ``t180`` and ``e_reb_mJ``, computed by
  ``drop_tower_sim`` to the same definitions,
* the same ``mass_g`` tracking metric, here the infill-corrected printed
  mass from ``print_infill`` rather than a weighed article,
* the same batch size (9, one print plate) and the same SAASBO generation
  strategy by default.

Two initializations are available, and they answer different questions.
``--init sobol`` (the default) starts each repeat **from scratch**: round 0
is the campaign's own nine-point Sobol draw, scrambled with that repeat's
seed, so the whole campaign -- initial design and every subsequent
suggestion -- is an independent draw.  That is what makes a repeat a
repeat, and it is the only way the spread across seeds means anything.
``--init printed`` reproduces PR #102 exactly instead, attaching the nine
articles that were physically printed as completed trials; every repeat
then shares an identical round 0, so the seeds differ only in the
surrogate's own randomness and agree far more closely than the problem
warrants.

The hypervolume reference point is fixed across seeds and across
initializations (it is derived once from the nine printed articles, scored
in simulation, inflated by 5 %), so traces from different seeds are
directly comparable even though their round 0 differs.

Differences from PR #102, all forced by running in simulation: the loop
continues past one round, and noise is zero (the sim is deterministic, so
no SEM is attached).

SAASBO fits a fully Bayesian NUTS model per round, which dominates the
wall-clock here (the simulation itself is about 0.3 s per design).  Use
``--model botorch`` for the cheap qNEHVI surrogate when the question is
about the loop rather than about the model.

Two search spaces (``--space``).  ``slab6`` is the PR #102-faithful one:
the five base millimetre axes plus ``mass_printed_g`` in a narrow slab.
``ratios`` (the default, per the 2026-08-22 review of the slab runs) drops
the mass parameter entirely: the campaign searches the four scale-free
shape ratios, the overall scale is solved so printed mass equals the
20.23 g target exactly, the second objective is the dimensionless
``e_rebound`` (``e_reb_mJ`` is a constant multiple of it on this
manifold), and the projected article's printability (cable diameter,
envelope) enters as Ax outcome constraints.  See ``space_config``.

Run::

    python pr102_sim_campaign.py --seed 0 --rounds 4
    python pr102_sim_campaign.py --seeds 0 1 2 3 --jobs 4   # repeats in parallel
    python pr102_sim_campaign.py --aggregate                # figures across seeds
"""
from __future__ import annotations

import argparse
import math
import os
import time
from pathlib import Path

# One thread per process: the parallelism here is one campaign per seed, and
# oversubscribing BLAS inside each of them makes every repeat slower.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import drop_tower_sim  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "pr102"
OUT = HERE / "outputs"

SHAPE_PARAMS = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]
MASS_PARAM = "mass_printed_g"
PARAM_NAMES = SHAPE_PARAMS + [MASS_PARAM]
OBJ1, OBJ2, MASS = "t180", "e_reb_mJ", "mass_g"
OBJ2_RATIOS = "e_rebound"

# The sixth parameter, and why the campaign needs it.  ``e_reb_mJ`` is an
# absolute energy, ``e_rebound * m * g * h``, so it is proportional to the
# article's printed mass.  Round 1 was projected onto constant *solid* mass
# (PR #35 Route A), which leaves printed mass free: over the 68,944-design
# reference sweep that ran with the old projection, printed mass spanned 32 %
# while simulated ``e_rebound`` spanned 0.34 %, and rho(e_reb_mJ, mass_g) came
# out at 0.9999.  The objective *was* the mass.  PR #102 commit 2f1ca2e fixed
# this by projecting onto constant *printed* mass and carrying mass as a
# parameter confined to a narrow slab, so competing shapes are compared at the
# same mass and the slab covers only the print-to-print scatter.
MASS_TARGET_G = 20.23     # weighed mass of the S0 reference article bpx68c
MASS_SCATTER_G = 0.457    # sd of the spec-08 triplicate (dea4ls/bag26v/ghmj4y)

# identical to PARAMETERS in bo/t3_prism_bo_campaign.py (PR #102)
PARAMETERS = [
    {"name": "R_mm", "type": "range", "bounds": [25.0, 40.0], "value_type": "float"},
    {"name": "H_mm", "type": "range", "bounds": [60.0, 110.0], "value_type": "float"},
    {"name": "twist_deg", "type": "range", "bounds": [40.0, 80.0], "value_type": "float"},
    {"name": "strut_d_mm", "type": "range", "bounds": [6.0, 12.0], "value_type": "float"},
    {"name": "cable_d_mm", "type": "range", "bounds": [3.0, 5.5], "value_type": "float"},
    {"name": MASS_PARAM, "type": "range", "value_type": "float",
     "bounds": [MASS_TARGET_G - MASS_SCATTER_G, MASS_TARGET_G + MASS_SCATTER_G]},
]

# --- ``--space ratios``: the Route 1 scale-free re-parameterization -------
# The slab space above carries mass as a sixth parameter, which is right for
# PR #102 (mass there is a genuinely free print-scale axis with measured
# scatter) and wrong here: the sim is deterministic and the constant-mass
# projection makes mass a function of shape, so the six coordinates are
# degenerate (every point shares its projected article with a one-parameter
# family of others) and the slab is exploitable as a gradient.  The fix
# recommended in the 2026-08-22 review comment is to search *shape* directly:
# the four dimensionless ratios below, with the single overall scale solved
# in closed form by ``pr102_mass_model`` so the printed mass equals
# ``MASS_TARGET_G`` exactly on every evaluation.  Mass never enters the
# search space, ``e_reb_mJ`` and ``e_rebound`` then differ by the constant
# ``m* g h``, and the second objective is the dimensionless ``e_rebound``.
#
# Ratio bounds are the extremes the PR #35 box can express (60/40 to 110/25
# for H/R, and so on).  The image of that box in ratio space is not a box,
# so this search space contains shape combinations the base box could only
# reach at a different overall size; on the constant-mass manifold overall
# size is not a design choice, so those are legitimate candidates rather
# than extrapolations.  What the base box cannot police any more is
# printability, so the projected article's cable diameter (TPU
# self-bridging floor, 3.0 mm) and envelope (250 cm^3) become explicit Ax
# outcome constraints instead of silent box implications.
RATIO_PARAMS = ["H_over_R", "H_over_strut_d", "cable_over_strut_d", "twist_deg"]
RATIO_NOMINAL_H_MM = 85.0     # arbitrary pre-projection size; the scale solve removes it
RATIO_PARAMETERS = [
    {"name": "H_over_R", "type": "range", "bounds": [1.5, 4.4],
     "value_type": "float"},
    {"name": "H_over_strut_d", "type": "range", "bounds": [5.0, 110.0 / 6.0],
     "value_type": "float"},
    {"name": "cable_over_strut_d", "type": "range", "bounds": [0.25, 5.5 / 6.0],
     "value_type": "float"},
    {"name": "twist_deg", "type": "range", "bounds": [40.0, 80.0],
     "value_type": "float"},
]
CABLE_PRINT_FLOOR_MM = 3.0    # Edison 25c1c897 TPU self-bridging threshold
ENVELOPE_MAX_CM3 = 250.0      # PR #35 build-volume cap


def ratios_to_base(params: dict) -> dict:
    """Shape ratios -> base coordinates at the nominal pre-projection size."""
    H = RATIO_NOMINAL_H_MM
    sd = H / float(params["H_over_strut_d"])
    return {"R_mm": H / float(params["H_over_R"]), "H_mm": H,
            "twist_deg": float(params["twist_deg"]), "strut_d_mm": sd,
            "cable_d_mm": float(params["cable_over_strut_d"]) * sd}


def base_to_ratios(params: dict) -> dict:
    return {"H_over_R": float(params["H_mm"]) / float(params["R_mm"]),
            "H_over_strut_d": float(params["H_mm"]) / float(params["strut_d_mm"]),
            "cable_over_strut_d": (float(params["cable_d_mm"])
                                   / float(params["strut_d_mm"])),
            "twist_deg": float(params["twist_deg"])}


def space_config(space: str) -> dict:
    """Everything that differs between the two search spaces, in one place."""
    if space == "slab6":
        return {"parameters": PARAMETERS, "param_names": PARAM_NAMES,
                "obj2": OBJ2, "outcome_constraints": None}
    if space == "ratios":
        return {"parameters": RATIO_PARAMETERS, "param_names": RATIO_PARAMS,
                "obj2": OBJ2_RATIOS,
                "outcome_constraints": [
                    f"cable_d_print_mm >= {CABLE_PRINT_FLOOR_MM}",
                    f"envelope_cm3 <= {ENVELOPE_MAX_CM3}"]}
    raise ValueError(f"unknown space {space!r}")

# Hypervolume reference point.  Derived rather than typed in: the worst
# value each objective takes over the nine printed articles, scored in
# simulation and inflated 5 %, so every subsequent design contributes.  It
# must not depend on the seed's own round 0, or a repeat that happened to
# draw a bad initial batch would be handed a generous reference point and
# score a larger hypervolume for it, which is exactly the comparison the
# repeats exist to make.
REF_INFLATION = 1.05
_REF_CACHE: dict[tuple, np.ndarray] = {}


def evaluate(params: dict, *, solid: bool = False,
             space: str = "slab6") -> dict:
    if space == "ratios":
        base = ratios_to_base(params)
        res = drop_tower_sim.evaluate_pr102(base, target_mass_g=MASS_TARGET_G,
                                            solid_mass=solid)
        scale = float(res.get("print_scale", float("nan")))
        r_print = base["R_mm"] * scale
        h_print = base["H_mm"] * scale
        cable_print = base["cable_d_mm"] * scale
        envelope = math.pi * r_print ** 2 * h_print / 1000.0
        out = {OBJ1: float(res["t180"]), OBJ2_RATIOS: float(res["e_rebound"]),
               OBJ2: float(res["e_reb_mJ"]), MASS: float(res["mass_printed_g"]),
               "print_scale": scale,
               "R_print_mm": r_print, "H_print_mm": h_print,
               "strut_d_print_mm": base["strut_d_mm"] * scale,
               "cable_d_print_mm": cable_print, "envelope_cm3": envelope}
        out["feasible"] = bool(np.isfinite(out[OBJ1])
                               and cable_print >= CABLE_PRINT_FLOOR_MM
                               and envelope <= ENVELOPE_MAX_CM3)
        return out
    res = drop_tower_sim.evaluate_pr102(params, solid_mass=solid)
    return {OBJ1: float(res["t180"]), OBJ2: float(res["e_reb_mJ"]),
            MASS: float(res["mass_printed_g"])}


def sobol_batch_params() -> list[dict]:
    """The nine printed T-3_01 articles, at their base Sobol coordinates.

    Their mass coordinate is the weighed mass of the print, where there is
    one, and the batch target otherwise: these articles were built to a
    constant *solid* mass and so are scattered along the mass axis rather
    than sitting on the campaign's constant-printed-mass slab, which is the
    same thing PR #102 notes about its own round-1 data.
    """
    batch = pd.read_csv(DATA / "t3-prism-bo-batch.csv").set_index("specimen")
    key = pd.read_csv(DATA / "t3-prism-bo-batch-print-key.csv",
                      dtype={"specimen": "string"})
    weighed = (key[key["specimen"] != "S0"]
               .assign(spec=lambda d: d["specimen"].astype(int))
               .groupby("spec")["mass_g"].mean().to_dict())
    out = []
    for spec, row in batch.iterrows():
        p = {n: float(row[n]) for n in SHAPE_PARAMS}
        p[MASS_PARAM] = float(weighed.get(int(spec), MASS_TARGET_G))
        out.append(p)
    return out


def reference_point(solid: bool = False, space: str = "slab6") -> np.ndarray:
    """Seed-independent hypervolume reference, from the printed articles.

    In the ratio space the nine articles enter as their (scale-invariant)
    shape ratios and are all projected onto the single ``MASS_TARGET_G``
    manifold, and the second axis is the dimensionless ``e_rebound``.
    """
    key = (solid, space)
    if key not in _REF_CACHE:
        obj2 = space_config(space)["obj2"]
        if space == "ratios":
            seeds = [base_to_ratios(p) for p in sobol_batch_params()]
        else:
            seeds = sobol_batch_params()
        scored = [evaluate(p, solid=solid, space=space) for p in seeds]
        worst = np.array([max(r[OBJ1] for r in scored),
                          max(r[obj2] for r in scored)], dtype=float)
        _REF_CACHE[key] = REF_INFLATION * worst
    return _REF_CACHE[key]


def hypervolume_2d(points: np.ndarray, ref: np.ndarray) -> float:
    """Dominated hypervolume of a minimization front against ``ref``."""
    pts = points[(points < ref).all(axis=1)]
    if pts.size == 0:
        return 0.0
    pts = pts[np.argsort(pts[:, 0])]
    hv, best_y = 0.0, ref[1]
    for x, y in pts:
        if y < best_y:
            hv += (ref[0] - x) * (best_y - y)
            best_y = y
    return float(hv)


def seed_tag(model: str, init: str, seed: int, solid: bool = False,
             space: str = "slab6") -> str:
    prefix = f"{model}_{init}" if space == "slab6" else f"{model}_{space}_{init}"
    return f"{prefix}_seed{seed}" + ("_solid" if solid else "")


def run_seed(seed: int, rounds: int, batch_size: int, model: str,
             outdir: Path, solid: bool = False,
             init: str = "sobol", space: str = "slab6") -> pd.DataFrame:
    from ax.modelbridge.factory import Models
    from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
    from ax.service.ax_client import AxClient, ObjectiveProperties

    cfg = space_config(space)
    obj2 = cfg["obj2"]
    step_model = Models.SAASBO if model == "saasbo" else Models.BOTORCH_MODULAR
    steps = []
    if init == "sobol":
        # From scratch: this repeat draws its own initial batch, scrambled
        # with its own seed.  Ax's Sobol generator is seeded explicitly as
        # well as through AxClient(random_seed=...) so the draw is pinned to
        # the seed rather than to whatever global state the process is in.
        steps.append(GenerationStep(
            model=Models.SOBOL, num_trials=batch_size,
            min_trials_observed=batch_size, max_parallelism=batch_size,
            model_kwargs={"seed": seed}))
    # The acquisition optimization dominates the wall-clock (AxClient
    # generates the batch one q=1 gen call at a time, each a full multi-start
    # optimization; with the ratio space's two outcome constraints a round of
    # 9 costs about 300 s at the Ax defaults of 20 restarts x 1024 raw
    # samples).  The surface is 4-6 dimensional and smooth, so a lighter
    # multi-start loses little; this cuts a model round to tens of seconds.
    gen_options = {"model_gen_options": {"optimizer_kwargs": {
        "num_restarts": 8, "raw_samples": 128}}}
    steps.append(GenerationStep(model=step_model, num_trials=-1,
                                max_parallelism=batch_size,
                                model_gen_kwargs=gen_options))
    gs = GenerationStrategy(steps=steps)
    ax_client = AxClient(generation_strategy=gs, random_seed=seed,
                         verbose_logging=False)
    # keep the Ax metric list lean: every metric named here gets its own GP
    # fit per round, and the CSV keeps all of evaluate()'s columns regardless
    tracking = [MASS] if space == "slab6" else []
    ax_client.create_experiment(
        name=f"t3_prism_sim_campaign_{space}_{init}_seed{seed}",
        parameters=cfg["parameters"],
        objectives={OBJ1: ObjectiveProperties(minimize=True),
                    obj2: ObjectiveProperties(minimize=True)},
        tracking_metric_names=tracking,
        outcome_constraints=cfg["outcome_constraints"],
    )

    # keys Ax gets back on complete_trial: objectives, constraint metrics,
    # tracking metrics; the rest of evaluate()'s columns are CSV-only
    ax_keys = {OBJ1, obj2, *tracking}
    if cfg["outcome_constraints"]:
        ax_keys |= {"cable_d_print_mm", "envelope_cm3"}

    rows = []
    if init == "printed":
        if space == "ratios":
            raise ValueError("--init printed reproduces PR #102's slab-space "
                             "round 0 and is not defined on the ratio manifold")
        # PR #102's own round 0: the nine articles that were printed,
        # attached as completed trials.  Identical for every seed.
        for params in sobol_batch_params():
            # PR #102 keeps two search spaces, a wide one to fit on and the
            # narrow slab to generate in, so round-1 articles can sit off the
            # slab along the mass axis.  ``AxClient`` carries one space, so
            # here the attached mass coordinate is clipped into the slab
            # instead.  That costs the model some of the round-1 mass spread
            # and only affects ``--init printed``; the default ``--init
            # sobol`` repeats draw their own batch on the slab and are
            # unaffected.
            params = dict(params)
            params[MASS_PARAM] = float(np.clip(
                params[MASS_PARAM], MASS_TARGET_G - MASS_SCATTER_G,
                MASS_TARGET_G + MASS_SCATTER_G))
            _, idx = ax_client.attach_trial(params)
            res = evaluate(params, solid=solid)
            # snapshot before completing: complete_trial rewrites the dict in
            # place into (mean, sem) tuples
            rows.append({"seed": seed, "round": 0, "trial": idx, **params,
                         **dict(res)})
            ax_client.complete_trial(trial_index=idx, raw_data=res)
        first_round = 1
    else:
        first_round = 0

    for rnd in range(first_round, rounds + 1):
        t0 = time.time()
        parameterizations, _ = ax_client.get_next_trials(batch_size)
        for idx, params in parameterizations.items():
            res = evaluate(dict(params), solid=solid, space=space)
            rows.append({"seed": seed, "round": rnd, "trial": idx,
                         **{k: float(v) for k, v in params.items()},
                         **dict(res)})
            ax_client.complete_trial(
                trial_index=idx,
                raw_data={k: v for k, v in res.items() if k in ax_keys})
        print(f"  seed {seed} round {rnd}: {batch_size} designs, "
              f"{time.time() - t0:.1f} s", flush=True)

    df = pd.DataFrame(rows)
    ref = reference_point(solid, space)
    obj = df[[OBJ1, obj2]].to_numpy(dtype=float)
    # only printable designs count toward the front and the running bests;
    # in the slab space every design is feasible and the mask is all-true
    feas = (df["feasible"].to_numpy(dtype=bool) if "feasible" in df
            else np.ones(len(df), dtype=bool))
    masked = np.where(feas[:, None], obj, np.inf)
    df["hv"] = [hypervolume_2d(masked[: i + 1], ref) for i in range(len(obj))]
    df["best_t180"] = pd.Series(np.where(feas, df[OBJ1], np.inf)).cummin()
    df["best_e_reb_mJ"] = pd.Series(np.where(feas, df[OBJ2], np.inf)).cummin()
    if space == "ratios":
        df["best_e_rebound"] = pd.Series(
            np.where(feas, df[OBJ2_RATIOS], np.inf)).cummin()

    outdir.mkdir(parents=True, exist_ok=True)
    tag = seed_tag(model, init, seed, solid, space)
    df.to_csv(outdir / f"pr102_sim_bo_{tag}.csv", index=False, float_format="%.6g")
    plot_seed(df, outdir / f"pr102_sim_bo_{tag}.png", seed, model, init=init,
              space=space)
    return df


def _run_seed_worker(job: tuple) -> str:
    """multiprocessing entry point; returns the tag it wrote."""
    seed, rounds, batch_size, model, outdir, solid, init, space = job
    t0 = time.time()
    run_seed(seed, rounds, batch_size, model, Path(outdir), solid=solid,
             init=init, space=space)
    tag = seed_tag(model, init, seed, solid, space)
    print(f"seed {seed} done in {time.time() - t0:.1f} s", flush=True)
    return tag


def plot_seed(df: pd.DataFrame, path: Path, seed: int, model: str,
              init: str = "sobol", space: str = "slab6") -> None:
    obj2 = space_config(space)["obj2"]
    obj2_best = "best_e_rebound" if space == "ratios" else "best_e_reb_mJ"
    obj2_label = ("e_rebound (simulated, minimize)" if space == "ratios"
                  else "e_reb_mJ (simulated, minimize)")
    fig, (ax_c, ax_b, ax_p) = plt.subplots(1, 3, figsize=(16, 4.2), dpi=200)
    ax_c.plot(df.index + 1, df["hv"], color="#2a78d6", lw=1.8)
    ax_c.set_xlabel("simulated design")
    ax_c.set_ylabel("dominated hypervolume")
    ax_c.set_title(f"convergence (seed {seed}, {model})", fontsize=10)
    ax_c.grid(alpha=0.25, lw=0.5)
    n_init = int((df["round"] == 0).sum())
    ax_c.axvline(n_init, color="#52514e", ls=":", lw=1)
    label = ("printed Sobol batch" if init == "printed"
             else f"Sobol batch (seed {seed})")
    ax_c.annotate(label, (n_init, ax_c.get_ylim()[0]),
                  textcoords="offset points", xytext=(4, 12), fontsize=7,
                  color="#52514e")

    # Running best on each objective separately.  Hypervolume alone hides
    # which of the two is actually improving, and they are on scales two
    # orders of magnitude apart, so they get one axis each.
    x = df.index + 1
    ax_b.plot(x, df["best_t180"], color="#2a78d6", lw=1.8, label="best t180")
    ax_b.set_xlabel("simulated design")
    ax_b.set_ylabel("running-best t180", color="#2a78d6")
    ax_b.tick_params(axis="y", labelcolor="#2a78d6")
    ax_b.grid(alpha=0.25, lw=0.5)
    ax_e = ax_b.twinx()
    ax_e.plot(x, df[obj2_best], color="#c0392b", lw=1.8, ls="--",
              label=f"best {obj2}")
    ax_e.set_ylabel(f"running-best {obj2}", color="#c0392b")
    ax_e.tick_params(axis="y", labelcolor="#c0392b")
    ax_b.set_title("running best, per objective", fontsize=10)

    sc = ax_p.scatter(df[OBJ1], df[obj2], c=df["round"], cmap="viridis", s=32)
    if "feasible" in df:
        bad = ~df["feasible"].astype(bool)
        if bad.any():
            ax_p.scatter(df.loc[bad, OBJ1], df.loc[bad, obj2], s=70,
                         facecolors="none", edgecolors="#c0392b", lw=1.0,
                         label="unprintable")
            ax_p.legend(fontsize=7)
    ax_p.set_xlabel("t180 (simulated, minimize)")
    ax_p.set_ylabel(obj2_label)
    ax_p.set_title("objective space, coloured by round", fontsize=10)
    ax_p.grid(alpha=0.25, lw=0.5)
    fig.colorbar(sc, ax=ax_p, label="round")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def aggregate(outdir: Path, model: str, init: str = "sobol",
              space: str = "slab6") -> None:
    obj2 = space_config(space)["obj2"]
    obj2_best = "best_e_rebound" if space == "ratios" else "best_e_reb_mJ"
    prefix = (f"pr102_sim_bo_{model}_{init}" if space == "slab6"
              else f"pr102_sim_bo_{model}_{space}_{init}")
    files = sorted(outdir.glob(f"{prefix}_seed*.csv"),
                   key=lambda f: int(f.stem.split("seed")[-1].split("_")[0]))
    files = [f for f in files if "_solid" not in f.name]
    if not files:
        print(f"no per-seed CSVs for {model}/{space}/{init} in {outdir}")
        return
    frames = [pd.read_csv(f) for f in files]
    n = min(len(f) for f in frames)
    hv = np.vstack([f["hv"].to_numpy()[:n] for f in frames])
    t180 = np.vstack([f["best_t180"].to_numpy()[:n] for f in frames])
    ereb = np.vstack([f[obj2_best].to_numpy()[:n] for f in frames])

    fig, (ax_h, ax_t, ax_e, ax_0) = plt.subplots(1, 4, figsize=(20.5, 4.2),
                                                 dpi=200)
    x = np.arange(1, n + 1)
    for ax, arr, label in ((ax_h, hv, "dominated hypervolume"),
                           (ax_t, t180, "running-best t180"),
                           (ax_e, ereb, f"running-best {obj2}")):
        for row in arr:
            ax.plot(x, row, color="#9aa0a6", lw=0.8, alpha=0.7)
        mean, sd = arr.mean(axis=0), arr.std(axis=0)
        ax.plot(x, mean, color="#2a78d6", lw=2, label=f"mean of {len(frames)} seeds")
        ax.fill_between(x, mean - sd, mean + sd, color="#2a78d6", alpha=0.2,
                        label="+/- 1 sd")
        ax.set_xlabel("simulated design")
        ax.set_ylabel(label)
        ax.grid(alpha=0.25, lw=0.5)
        ax.legend(fontsize=8)

    # Third panel: every repeat's own round 0.  With --init sobol these are
    # different draws, which is the point; with --init printed they collapse
    # onto one set of nine markers, which is the failure mode this panel
    # exists to make visible.
    cmap = plt.get_cmap("tab10")
    for i, f in enumerate(frames):
        r0 = f[f["round"] == 0]
        ax_0.scatter(r0[OBJ1], r0[obj2], s=26, alpha=0.8,
                     color=cmap(i % 10), label=f"seed {int(f['seed'].iloc[0])}")
    ax_0.set_xlabel("t180 (simulated)")
    ax_0.set_ylabel(f"{obj2} (simulated)")
    ax_0.set_title("round 0, per seed", fontsize=10)
    ax_0.grid(alpha=0.25, lw=0.5)
    ax_0.legend(fontsize=6, ncol=2)

    init_label = ("printed Sobol batch, shared" if init == "printed"
                  else "from scratch, per-seed Sobol")
    space_label = ("constant-mass shape ratios" if space == "ratios"
                   else "base box + mass slab")
    fig.suptitle(f"Simulation-only T-3_01 campaign, {len(frames)} seeds "
                 f"({model}, {init_label}, {space_label})", fontsize=11)
    fig.tight_layout()
    fig.savefig(outdir / f"{prefix}_aggregate.png", bbox_inches="tight")
    plt.close(fig)

    all_rows = pd.concat(frames)
    aggs = {"final_hv": ("hv", "max"), "best_t180": ("best_t180", "min"),
            "best_e_reb_mJ": ("best_e_reb_mJ", "min"),
            "n": ("trial", "count")}
    if space == "ratios":
        aggs["best_e_rebound"] = ("best_e_rebound", "min")
        aggs["n_feasible"] = ("feasible", "sum")
    summary = all_rows.groupby("seed").agg(**aggs)
    summary.to_csv(outdir / f"{prefix}_summary.csv", float_format="%.6g")
    print(summary.to_string())
    cv = summary["final_hv"].std() / summary["final_hv"].mean()
    print(f"final hypervolume across seeds: mean {summary['final_hv'].mean():.4g}, "
          f"sd {summary['final_hv'].std():.4g} ({100 * cv:.2f} % of the mean)")
    print(f"Wrote {outdir}/{prefix}_aggregate.png and _summary.csv")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="*", default=None,
                    help="run several repeats, each an independent campaign")
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--batch-size", type=int, default=9, help="prints per plate")
    ap.add_argument("--model", choices=("saasbo", "botorch"), default="saasbo",
                    help="saasbo mirrors PR #102; botorch is the cheap qNEHVI")
    ap.add_argument("--init", choices=("sobol", "printed"), default="sobol",
                    help="sobol: each repeat draws its own seeded round 0 "
                         "(from scratch).  printed: every repeat starts from "
                         "the nine physically printed articles, as PR #102 did")
    ap.add_argument("--space", choices=("slab6", "ratios"), default="ratios",
                    help="ratios (default): the Route 1 scale-free shape "
                         "ratios at exactly constant printed mass, objectives "
                         "t180 + e_rebound, printability as outcome "
                         "constraints.  slab6: the earlier PR #102-style six "
                         "parameters incl. the mass slab, kept for comparison")
    ap.add_argument("--jobs", type=int, default=1,
                    help="repeats to run concurrently (one process per seed)")
    ap.add_argument("--solid", action="store_true",
                    help="ablation: ignore infill, run at solid PLA density")
    ap.add_argument("--aggregate", action="store_true",
                    help="only rebuild the cross-seed figures from existing CSVs")
    ap.add_argument("--outdir", type=Path, default=OUT)
    args = ap.parse_args(argv)

    if args.aggregate:
        aggregate(args.outdir, args.model, args.init, args.space)
        return 0

    seeds = args.seeds if args.seeds else [args.seed]
    jobs = [(seed, args.rounds, args.batch_size, args.model, str(args.outdir),
             args.solid, args.init, args.space) for seed in seeds]
    print(f"{len(seeds)} repeat(s): {args.rounds} rounds x {args.batch_size} "
          f"designs, {args.model}, init={args.init}, space={args.space}, "
          f"jobs={args.jobs}")

    t0 = time.time()
    if args.jobs > 1 and len(jobs) > 1:
        import multiprocessing as mp
        # Each worker runs one campaign end to end.  MuJoCo and the BoTorch
        # fit are both effectively single-threaded here, and the fit is the
        # wall-clock, so keep every library to one thread per worker and let
        # the parallelism come from the seeds.
        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=min(args.jobs, len(jobs))) as pool:
            for tag in pool.imap_unordered(_run_seed_worker, jobs):
                print(f"  wrote {tag}", flush=True)
    else:
        for job in jobs:
            _run_seed_worker(job)
    print(f"{len(seeds)} repeat(s) in {time.time() - t0:.1f} s")

    if len(seeds) > 1:
        aggregate(args.outdir, args.model, args.init, args.space)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
