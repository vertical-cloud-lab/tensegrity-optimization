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

Run::

    python pr102_sim_campaign.py --seed 0 --rounds 4
    python pr102_sim_campaign.py --seeds 0 1 2 3 --jobs 4   # repeats in parallel
    python pr102_sim_campaign.py --aggregate                # figures across seeds
"""
from __future__ import annotations

import argparse
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

# Hypervolume reference point.  Derived rather than typed in: the worst
# value each objective takes over the nine printed articles, scored in
# simulation and inflated 5 %, so every subsequent design contributes.  It
# must not depend on the seed's own round 0, or a repeat that happened to
# draw a bad initial batch would be handed a generous reference point and
# score a larger hypervolume for it, which is exactly the comparison the
# repeats exist to make.
REF_INFLATION = 1.05
_REF_CACHE: dict[bool, np.ndarray] = {}


def evaluate(params: dict, *, solid: bool = False) -> dict:
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


def reference_point(solid: bool = False) -> np.ndarray:
    """Seed-independent hypervolume reference, from the printed articles."""
    if solid not in _REF_CACHE:
        scored = [evaluate(p, solid=solid) for p in sobol_batch_params()]
        worst = np.array([max(r[OBJ1] for r in scored),
                          max(r[OBJ2] for r in scored)], dtype=float)
        _REF_CACHE[solid] = REF_INFLATION * worst
    return _REF_CACHE[solid]


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


def seed_tag(model: str, init: str, seed: int, solid: bool = False) -> str:
    return f"{model}_{init}_seed{seed}" + ("_solid" if solid else "")


def run_seed(seed: int, rounds: int, batch_size: int, model: str,
             outdir: Path, solid: bool = False,
             init: str = "sobol") -> pd.DataFrame:
    from ax.modelbridge.factory import Models
    from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
    from ax.service.ax_client import AxClient, ObjectiveProperties

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
    steps.append(GenerationStep(model=step_model, num_trials=-1,
                                max_parallelism=batch_size))
    gs = GenerationStrategy(steps=steps)
    ax_client = AxClient(generation_strategy=gs, random_seed=seed,
                         verbose_logging=False)
    ax_client.create_experiment(
        name=f"t3_prism_sim_campaign_{init}_seed{seed}",
        parameters=PARAMETERS,
        objectives={OBJ1: ObjectiveProperties(minimize=True),
                    OBJ2: ObjectiveProperties(minimize=True)},
        tracking_metric_names=[MASS],
    )

    rows = []
    if init == "printed":
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
            res = evaluate(dict(params), solid=solid)
            rows.append({"seed": seed, "round": rnd, "trial": idx,
                         **{k: float(v) for k, v in params.items()},
                         **dict(res)})
            ax_client.complete_trial(trial_index=idx, raw_data=res)
        print(f"  seed {seed} round {rnd}: {batch_size} designs, "
              f"{time.time() - t0:.1f} s", flush=True)

    df = pd.DataFrame(rows)
    ref = reference_point(solid)
    obj = df[[OBJ1, OBJ2]].to_numpy(dtype=float)
    df["hv"] = [hypervolume_2d(obj[: i + 1], ref) for i in range(len(obj))]
    df["best_t180"] = df[OBJ1].cummin()
    df["best_e_reb_mJ"] = df[OBJ2].cummin()

    outdir.mkdir(parents=True, exist_ok=True)
    tag = seed_tag(model, init, seed, solid)
    df.to_csv(outdir / f"pr102_sim_bo_{tag}.csv", index=False, float_format="%.6g")
    plot_seed(df, outdir / f"pr102_sim_bo_{tag}.png", seed, model, init=init)
    return df


def _run_seed_worker(job: tuple) -> str:
    """multiprocessing entry point; returns the tag it wrote."""
    seed, rounds, batch_size, model, outdir, solid, init = job
    t0 = time.time()
    run_seed(seed, rounds, batch_size, model, Path(outdir), solid=solid,
             init=init)
    tag = seed_tag(model, init, seed, solid)
    print(f"seed {seed} done in {time.time() - t0:.1f} s", flush=True)
    return tag


def plot_seed(df: pd.DataFrame, path: Path, seed: int, model: str,
              init: str = "sobol") -> None:
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
    ax_e.plot(x, df["best_e_reb_mJ"], color="#c0392b", lw=1.8, ls="--",
              label="best e_reb_mJ")
    ax_e.set_ylabel("running-best e_reb_mJ (mJ)", color="#c0392b")
    ax_e.tick_params(axis="y", labelcolor="#c0392b")
    ax_b.set_title("running best, per objective", fontsize=10)

    sc = ax_p.scatter(df[OBJ1], df[OBJ2], c=df["round"], cmap="viridis", s=32)
    ax_p.set_xlabel("t180 (simulated, minimize)")
    ax_p.set_ylabel("e_reb_mJ (simulated, minimize)")
    ax_p.set_title("objective space, coloured by round", fontsize=10)
    ax_p.grid(alpha=0.25, lw=0.5)
    fig.colorbar(sc, ax=ax_p, label="round")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def aggregate(outdir: Path, model: str, init: str = "sobol") -> None:
    files = sorted(outdir.glob(f"pr102_sim_bo_{model}_{init}_seed*.csv"),
                   key=lambda f: int(f.stem.split("seed")[-1].split("_")[0]))
    files = [f for f in files if "_solid" not in f.name]
    if not files:
        print(f"no per-seed CSVs for {model}/{init} in {outdir}")
        return
    frames = [pd.read_csv(f) for f in files]
    n = min(len(f) for f in frames)
    hv = np.vstack([f["hv"].to_numpy()[:n] for f in frames])
    t180 = np.vstack([f["best_t180"].to_numpy()[:n] for f in frames])
    ereb = np.vstack([f["best_e_reb_mJ"].to_numpy()[:n] for f in frames])

    fig, (ax_h, ax_t, ax_e, ax_0) = plt.subplots(1, 4, figsize=(20.5, 4.2),
                                                 dpi=200)
    x = np.arange(1, n + 1)
    for ax, arr, label in ((ax_h, hv, "dominated hypervolume"),
                           (ax_t, t180, "running-best t180"),
                           (ax_e, ereb, "running-best e_reb_mJ (mJ)")):
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
        ax_0.scatter(r0[OBJ1], r0[OBJ2], s=26, alpha=0.8,
                     color=cmap(i % 10), label=f"seed {int(f['seed'].iloc[0])}")
    ax_0.set_xlabel("t180 (simulated)")
    ax_0.set_ylabel("e_reb_mJ (simulated)")
    ax_0.set_title("round 0, per seed", fontsize=10)
    ax_0.grid(alpha=0.25, lw=0.5)
    ax_0.legend(fontsize=6, ncol=2)

    init_label = ("printed Sobol batch, shared" if init == "printed"
                  else "from scratch, per-seed Sobol")
    fig.suptitle(f"Simulation-only T-3_01 campaign, {len(frames)} seeds "
                 f"({model}, {init_label})", fontsize=11)
    fig.tight_layout()
    fig.savefig(outdir / f"pr102_sim_bo_{model}_{init}_aggregate.png",
                bbox_inches="tight")
    plt.close(fig)

    summary = pd.concat(frames).groupby("seed").agg(
        final_hv=("hv", "max"), best_t180=(OBJ1, "min"),
        best_e_reb_mJ=(OBJ2, "min"), n=("trial", "count"))
    summary.to_csv(outdir / f"pr102_sim_bo_{model}_{init}_summary.csv",
                   float_format="%.6g")
    print(summary.to_string())
    cv = summary["final_hv"].std() / summary["final_hv"].mean()
    print(f"final hypervolume across seeds: mean {summary['final_hv'].mean():.4g}, "
          f"sd {summary['final_hv'].std():.4g} ({100 * cv:.2f} % of the mean)")
    print(f"Wrote {outdir}/pr102_sim_bo_{model}_{init}_aggregate.png and _summary.csv")


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
    ap.add_argument("--jobs", type=int, default=1,
                    help="repeats to run concurrently (one process per seed)")
    ap.add_argument("--solid", action="store_true",
                    help="ablation: ignore infill, run at solid PLA density")
    ap.add_argument("--aggregate", action="store_true",
                    help="only rebuild the cross-seed figures from existing CSVs")
    ap.add_argument("--outdir", type=Path, default=OUT)
    args = ap.parse_args(argv)

    if args.aggregate:
        aggregate(args.outdir, args.model, args.init)
        return 0

    seeds = args.seeds if args.seeds else [args.seed]
    jobs = [(seed, args.rounds, args.batch_size, args.model, str(args.outdir),
             args.solid, args.init) for seed in seeds]
    print(f"{len(seeds)} repeat(s): {args.rounds} rounds x {args.batch_size} "
          f"designs, {args.model}, init={args.init}, jobs={args.jobs}")

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
        aggregate(args.outdir, args.model, args.init)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
