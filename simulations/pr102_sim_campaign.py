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
* the same initialization: round 0 is the nine-point Sobol batch that was
  physically printed (``data/pr102/t3-prism-bo-batch.csv``), attached as
  completed trials,
* the same batch size (9, one print plate) and the same SAASBO generation
  strategy by default.

Differences, all forced by running in simulation: the loop continues past
one round; noise is zero (the sim is deterministic, so no SEM is attached);
and the seed varies, which is the entire point.

SAASBO fits a fully Bayesian NUTS model per round, which dominates the
wall-clock here (the simulation itself is about 0.3 s per design).  Use
``--model botorch`` for the cheap qNEHVI surrogate when the question is
about the loop rather than about the model.

Run::

    python pr102_sim_campaign.py --seed 0 --rounds 4
    python pr102_sim_campaign.py --aggregate          # figures across seeds
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import drop_tower_sim  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "pr102"
OUT = HERE / "outputs"

PARAM_NAMES = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]
OBJ1, OBJ2, MASS = "t180", "e_reb_mJ", "mass_g"

# identical to PARAMETERS in bo/t3_prism_bo_campaign.py (PR #102)
PARAMETERS = [
    {"name": "R_mm", "type": "range", "bounds": [25.0, 40.0], "value_type": "float"},
    {"name": "H_mm", "type": "range", "bounds": [60.0, 110.0], "value_type": "float"},
    {"name": "twist_deg", "type": "range", "bounds": [40.0, 80.0], "value_type": "float"},
    {"name": "strut_d_mm", "type": "range", "bounds": [6.0, 12.0], "value_type": "float"},
    {"name": "cable_d_mm", "type": "range", "bounds": [3.0, 5.5], "value_type": "float"},
]

# Hypervolume reference point.  Fixed across seeds so the traces are
# comparable, and derived from the initial Sobol batch rather than typed in:
# the worst value each objective takes on the nine printed articles, inflated
# 5 %, so every subsequent design contributes.
REF_INFLATION = 1.05


def evaluate(params: dict, *, solid: bool = False) -> dict:
    kwargs = {"pla_solidity": 1.0, "tpu_solidity": 1.0} if solid else {}
    res = drop_tower_sim.evaluate_pr102(params, **kwargs)
    return {OBJ1: float(res["t180"]), OBJ2: float(res["e_reb_mJ"]),
            MASS: float(res["mass_printed_g"])}


def sobol_batch_params() -> list[dict]:
    """The nine printed T-3_01 articles, at their base Sobol coordinates."""
    batch = pd.read_csv(DATA / "t3-prism-bo-batch.csv").set_index("specimen")
    return [{n: float(row[n]) for n in PARAM_NAMES} for _, row in batch.iterrows()]


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


def run_seed(seed: int, rounds: int, batch_size: int, model: str,
             outdir: Path, solid: bool = False) -> pd.DataFrame:
    from ax.modelbridge.factory import Models
    from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
    from ax.service.ax_client import AxClient, ObjectiveProperties

    step_model = Models.SAASBO if model == "saasbo" else Models.BOTORCH_MODULAR
    gs = GenerationStrategy(steps=[GenerationStep(
        model=step_model, num_trials=-1,
        max_parallelism=batch_size)])
    ax_client = AxClient(generation_strategy=gs, random_seed=seed,
                         verbose_logging=False)
    ax_client.create_experiment(
        name=f"t3_prism_sim_campaign_seed{seed}",
        parameters=PARAMETERS,
        objectives={OBJ1: ObjectiveProperties(minimize=True),
                    OBJ2: ObjectiveProperties(minimize=True)},
        tracking_metric_names=[MASS],
    )

    rows = []
    # round 0: the printed Sobol batch, scored in simulation
    for params in sobol_batch_params():
        _, idx = ax_client.attach_trial(params)
        res = evaluate(params, solid=solid)
        # snapshot before completing: complete_trial rewrites the dict in
        # place into (mean, sem) tuples
        rows.append({"seed": seed, "round": 0, "trial": idx, **params,
                     **dict(res)})
        ax_client.complete_trial(trial_index=idx, raw_data=res)

    for rnd in range(1, rounds + 1):
        t0 = time.time()
        parameterizations, _ = ax_client.get_next_trials(batch_size)
        for idx, params in parameterizations.items():
            res = evaluate(dict(params), solid=solid)
            rows.append({"seed": seed, "round": rnd, "trial": idx,
                         **{k: float(v) for k, v in params.items()},
                         **dict(res)})
            ax_client.complete_trial(trial_index=idx, raw_data=res)
        print(f"  seed {seed} round {rnd}: {batch_size} designs, "
              f"{time.time() - t0:.1f} s")

    df = pd.DataFrame(rows)
    init = df[df["round"] == 0]
    ref = REF_INFLATION * init[[OBJ1, OBJ2]].to_numpy(dtype=float).max(axis=0)
    obj = df[[OBJ1, OBJ2]].to_numpy(dtype=float)
    df["hv"] = [hypervolume_2d(obj[: i + 1], ref) for i in range(len(obj))]
    df["best_t180"] = df[OBJ1].cummin()
    df["best_e_reb_mJ"] = df[OBJ2].cummin()

    outdir.mkdir(parents=True, exist_ok=True)
    tag = f"{model}_seed{seed}" + ("_solid" if solid else "")
    df.to_csv(outdir / f"pr102_sim_bo_{tag}.csv", index=False, float_format="%.6g")
    plot_seed(df, outdir / f"pr102_sim_bo_{tag}.png", seed, model)
    return df


def plot_seed(df: pd.DataFrame, path: Path, seed: int, model: str) -> None:
    fig, (ax_c, ax_p) = plt.subplots(1, 2, figsize=(11, 4.2), dpi=200)
    ax_c.plot(df.index + 1, df["hv"], color="#2a78d6", lw=1.8)
    ax_c.set_xlabel("simulated design")
    ax_c.set_ylabel("dominated hypervolume")
    ax_c.set_title(f"convergence (seed {seed}, {model})", fontsize=10)
    ax_c.grid(alpha=0.25, lw=0.5)
    n_init = int((df["round"] == 0).sum())
    ax_c.axvline(n_init, color="#52514e", ls=":", lw=1)
    ax_c.annotate("printed Sobol batch", (n_init, ax_c.get_ylim()[0]),
                  textcoords="offset points", xytext=(4, 12), fontsize=7,
                  color="#52514e")

    sc = ax_p.scatter(df[OBJ1], df[OBJ2], c=df["round"], cmap="viridis", s=32)
    ax_p.set_xlabel("t180 (simulated, minimize)")
    ax_p.set_ylabel("e_reb_mJ (simulated, minimize)")
    ax_p.set_title("objective space, coloured by round", fontsize=10)
    ax_p.grid(alpha=0.25, lw=0.5)
    fig.colorbar(sc, ax=ax_p, label="round")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def aggregate(outdir: Path, model: str) -> None:
    files = sorted(outdir.glob(f"pr102_sim_bo_{model}_seed*.csv"))
    files = [f for f in files if "_solid" not in f.name]
    if not files:
        print(f"no per-seed CSVs for model {model} in {outdir}")
        return
    frames = [pd.read_csv(f) for f in files]
    n = min(len(f) for f in frames)
    hv = np.vstack([f["hv"].to_numpy()[:n] for f in frames])
    t180 = np.vstack([f["best_t180"].to_numpy()[:n] for f in frames])

    fig, (ax_h, ax_t) = plt.subplots(1, 2, figsize=(11, 4.2), dpi=200)
    x = np.arange(1, n + 1)
    for ax, arr, label in ((ax_h, hv, "dominated hypervolume"),
                           (ax_t, t180, "running-best t180")):
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
    fig.suptitle(f"Simulation-only T-3_01 campaign, {len(frames)} seeds ({model})",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(outdir / f"pr102_sim_bo_{model}_aggregate.png", bbox_inches="tight")
    plt.close(fig)

    summary = pd.concat(frames).groupby("seed").agg(
        final_hv=("hv", "max"), best_t180=(OBJ1, "min"),
        best_e_reb_mJ=(OBJ2, "min"), n=("trial", "count"))
    summary.to_csv(outdir / f"pr102_sim_bo_{model}_summary.csv",
                   float_format="%.6g")
    print(summary.to_string())
    print(f"Wrote {outdir}/pr102_sim_bo_{model}_aggregate.png and _summary.csv")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="*", default=None,
                    help="run several seeds in this process")
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--batch-size", type=int, default=9, help="prints per plate")
    ap.add_argument("--model", choices=("saasbo", "botorch"), default="saasbo",
                    help="saasbo mirrors PR #102; botorch is the cheap qNEHVI")
    ap.add_argument("--solid", action="store_true",
                    help="ablation: ignore infill, run at solid PLA density")
    ap.add_argument("--aggregate", action="store_true",
                    help="only rebuild the cross-seed figures from existing CSVs")
    ap.add_argument("--outdir", type=Path, default=OUT)
    args = ap.parse_args(argv)

    if args.aggregate:
        aggregate(args.outdir, args.model)
        return 0

    seeds = args.seeds if args.seeds else [args.seed]
    for seed in seeds:
        t0 = time.time()
        print(f"seed {seed}: {args.rounds} rounds x {args.batch_size} designs "
              f"({args.model})")
        run_seed(seed, args.rounds, args.batch_size, args.model, args.outdir,
                 solid=args.solid)
        print(f"seed {seed} done in {time.time() - t0:.1f} s")
    if len(seeds) > 1:
        aggregate(args.outdir, args.model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
