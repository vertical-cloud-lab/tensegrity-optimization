"""Blind reproduction of the 2026-08-21 BO-vs-baselines study (commit 72f1989).

Written BEFORE reading simulations/pr102_sim_campaign.py or
simulations/pr102_baselines.py, per the reproduction protocol requested in
PR #33: the specification below comes only from (a) the PR comment record and
(b) committed era *data* artifacts (CSV outputs), never from the original
scripts. The physics instrument is the era drop_tower_sim.evaluate_pr102,
extracted at commit 72f1989 into a separate directory and imported as a black
box (call signature discovered by inspect.signature; source never opened).

Specification assembled from the record:
- Search space, the PR #35 box: R_mm [25,40], H_mm [60,110], twist_deg
  [40,80], strut_d_mm [6,12], cable_d_mm [3.0,5.5]. All continuous.
- Objectives: minimize t180 and minimize e_reb_mJ; mass_g tracked.
- Budget: 36 designs per repeat = round 0 (9 scrambled Sobol points drawn by
  Ax's own Sobol generator, seeded per repeat) + 3 model rounds of 9 from
  BOTORCH_MODULAR (default multi-objective acquisition, qNEHVI).
- Seeding: AxClient(random_seed=seed) and the Sobol GenerationStep gets
  model_kwargs={"seed": seed} (both disclosed in the PR thread's round-0
  distinctness audit comment).
- Hypervolume: plain 2-D hypervolume, both objectives minimized, against the
  fixed reference point (0.868168, 217.292) recorded in the committed
  pr102_reference_summary.csv; points outside the reference box contribute 0.
  Validated against the committed running-hv columns (max abs err 1e-4, CSV
  rounding) and the committed front (reproduces the 18.024 ceiling).
- Baselines at the same budget and seeds: random (uniform iid), sobol
  (scrambled scipy Sobol over the whole budget), lhs (scrambled Latin
  hypercube), heuristic (compass/pattern search with a halving step on a
  normalized weighted sum, budget split over weightings 0.15/0.5/0.85, seed
  sets the start point and axis order).

Blind degrees of freedom (details the record does not pin down), each marked
with "BLIND CHOICE" at the implementation site: the SEM attached to completed
trials, the exact compass-search mechanics, and the objective normalization
inside the compass scalarization.

Usage:
  python simulations/pr102_repro_blind.py --era-dir /tmp/era/simulations \
      --methods bo random sobol lhs heuristic --seeds 0 1 2 3 4 5 6 7 8 9 \
      --jobs 4
  python simulations/pr102_repro_blind.py --aggregate-only
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUTDIR = HERE / "outputs" / "repro_blind"

PARAM_NAMES = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]
PARAM_BOUNDS = {
    "R_mm": (25.0, 40.0),
    "H_mm": (60.0, 110.0),
    "twist_deg": (40.0, 80.0),
    "strut_d_mm": (6.0, 12.0),
    "cable_d_mm": (3.0, 5.5),
}
# Recorded in the era pr102_reference_summary.csv (data, not script).
HV_REF = (0.868168, 217.292)
REFERENCE_HV = 18.024
N_BATCH = 9
N_ROUNDS = 4  # round 0 (Sobol) + 3 model rounds
BUDGET = N_BATCH * N_ROUNDS


def load_instrument(era_dir: str):
    """Import the era evaluate_pr102 as a black box."""
    sys.path.insert(0, era_dir)
    import drop_tower_sim  # noqa: E402

    def evaluate(params: dict) -> dict:
        out = drop_tower_sim.evaluate_pr102({k: float(v) for k, v in params.items()})
        return {
            "t180": float(out["t180"]),
            "e_reb_mJ": float(out["e_reb_mJ"]),
            "mass_g": float(out["mass_printed_g"]),
            "print_scale": float(out["print_scale"]),
            "ok": bool(out["ok"]),
        }

    return evaluate


def hv2d(points, ref=HV_REF) -> float:
    """2-D hypervolume, both objectives minimized, w.r.t. the fixed ref."""
    pts = np.asarray(
        [p for p in points if p[0] < ref[0] and p[1] < ref[1]], dtype=float
    )
    if len(pts) == 0:
        return 0.0
    pts = pts[np.argsort(pts[:, 0])]
    hv, best2, prev2 = 0.0, np.inf, ref[1]
    for a, b in pts:
        if b < best2:
            hv += (ref[0] - a) * (prev2 - b)
            best2 = b
            prev2 = b
    return hv


def finish_rows(rows: list[dict]) -> pd.DataFrame:
    """Append running hv / best columns in the era CSV convention."""
    df = pd.DataFrame(rows)
    hvs, b1, b2 = [], [], []
    for k in range(1, len(df) + 1):
        sub = df.iloc[:k]
        hvs.append(hv2d(sub[["t180", "e_reb_mJ"]].values))
        b1.append(sub["t180"].min())
        b2.append(sub["e_reb_mJ"].min())
    df["hv"], df["best_t180"], df["best_e_reb_mJ"] = hvs, b1, b2
    return df


def scale_unit(u: np.ndarray) -> list[dict]:
    lo = np.array([PARAM_BOUNDS[p][0] for p in PARAM_NAMES])
    hi = np.array([PARAM_BOUNDS[p][1] for p in PARAM_NAMES])
    x = lo + u * (hi - lo)
    return [dict(zip(PARAM_NAMES, row)) for row in x]


# ---------------------------------------------------------------- baselines


def run_sampler(evaluate, strategy: str, seed: int) -> pd.DataFrame:
    from scipy.stats import qmc

    if strategy == "random":
        rng = np.random.default_rng(seed)
        u = rng.uniform(size=(BUDGET, len(PARAM_NAMES)))
    elif strategy == "sobol":
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            u = qmc.Sobol(d=len(PARAM_NAMES), scramble=True, seed=seed).random(BUDGET)
    elif strategy == "lhs":
        u = qmc.LatinHypercube(d=len(PARAM_NAMES), seed=seed).random(BUDGET)
    else:
        raise ValueError(strategy)
    rows = []
    for t, params in enumerate(scale_unit(u)):
        res = evaluate(params)
        rows.append(
            {"strategy": strategy, "seed": seed, "round": t // N_BATCH, "trial": t}
            | params
            | res
        )
    return finish_rows(rows)


def run_heuristic(evaluate, seed: int) -> pd.DataFrame:
    """Compass (pattern) search, halving step, on a normalized weighted sum.

    BLIND CHOICE: the record specifies only "compass search with a halving
    step on a normalized weighted sum, budget split over three weightings
    (0.15/0.5/0.85); the seed sets the start and the axis order". Mechanics
    chosen here: per weighting w the scalar score is
    w * t180 / ref_t180 + (1 - w) * e_reb / ref_e_reb (normalization by the
    fixed hypervolume reference point); start at a seed-random point; probe
    +/- step along each axis in a seed-shuffled order, greedily re-centering
    on the first improvement; halve the step after a full failed sweep;
    initial step 0.25 of each axis range; 12 evaluations per weighting.
    """
    rng = np.random.default_rng(seed)
    lo = np.array([PARAM_BOUNDS[p][0] for p in PARAM_NAMES])
    hi = np.array([PARAM_BOUNDS[p][1] for p in PARAM_NAMES])
    span = hi - lo
    weights = [0.15, 0.5, 0.85]
    per_w = BUDGET // len(weights)
    rows = []
    t = 0

    def score(res, w):
        return w * res["t180"] / HV_REF[0] + (1 - w) * res["e_reb_mJ"] / HV_REF[1]

    for w in weights:
        x = lo + rng.uniform(size=len(PARAM_NAMES)) * span
        axis_order = rng.permutation(len(PARAM_NAMES))
        step = 0.25 * span
        res = evaluate(dict(zip(PARAM_NAMES, x)))
        rows.append(
            {"strategy": "heuristic", "seed": seed, "round": t // N_BATCH, "trial": t}
            | dict(zip(PARAM_NAMES, x))
            | res
        )
        t += 1
        best = score(res, w)
        used = 1
        while used < per_w:
            improved = False
            for ax in axis_order:
                for sign in (+1, -1):
                    if used >= per_w:
                        break
                    cand = x.copy()
                    cand[ax] = np.clip(cand[ax] + sign * step[ax], lo[ax], hi[ax])
                    if np.allclose(cand, x):
                        continue
                    res = evaluate(dict(zip(PARAM_NAMES, cand)))
                    rows.append(
                        {
                            "strategy": "heuristic",
                            "seed": seed,
                            "round": t // N_BATCH,
                            "trial": t,
                        }
                        | dict(zip(PARAM_NAMES, cand))
                        | res
                    )
                    t += 1
                    used += 1
                    s = score(res, w)
                    if s < best:
                        best, x = s, cand
                        improved = True
                        break
                if improved:
                    break
            if not improved:
                step = step / 2.0
    return finish_rows(rows)


# ----------------------------------------------------------------------- BO


def run_bo(evaluate, seed: int, acq_restarts=None, acq_raw_samples=None) -> pd.DataFrame:
    from ax.service.ax_client import AxClient, ObjectiveProperties

    try:
        from ax.modelbridge.generation_strategy import (
            GenerationStep,
            GenerationStrategy,
        )
        from ax.modelbridge.registry import Models as Generators
    except ImportError:  # newer ax naming
        from ax.generation_strategy.generation_strategy import (
            GenerationStep,
            GenerationStrategy,
        )
        from ax.generation_strategy.registry import Generators

    model_gen_kwargs = None
    if acq_restarts is not None:
        model_gen_kwargs = {
            "model_gen_options": {
                "optimizer_kwargs": {
                    "num_restarts": acq_restarts,
                    "raw_samples": acq_raw_samples,
                }
            }
        }
    gs = GenerationStrategy(
        steps=[
            GenerationStep(
                model=Generators.SOBOL,
                num_trials=N_BATCH,
                model_kwargs={"seed": seed},
            ),
            GenerationStep(
                model=Generators.BOTORCH_MODULAR,
                num_trials=-1,
                model_gen_kwargs=model_gen_kwargs,
            ),
        ]
    )
    ax_client = AxClient(
        generation_strategy=gs, random_seed=seed, verbose_logging=False
    )
    ax_client.create_experiment(
        name=f"repro_blind_seed{seed}",
        parameters=[
            {
                "name": p,
                "type": "range",
                "bounds": list(PARAM_BOUNDS[p]),
                "value_type": "float",
            }
            for p in PARAM_NAMES
        ],
        objectives={
            "t180": ObjectiveProperties(minimize=True),
            "e_reb_mJ": ObjectiveProperties(minimize=True),
        },
        tracking_metric_names=["mass_g"],
    )
    rows = []
    t = 0
    for rnd in range(N_ROUNDS):
        trials, _ = ax_client.get_next_trials(max_trials=N_BATCH)
        for trial_index, params in trials.items():
            res = evaluate(params)
            # BLIND CHOICE: SEM 0.0 (deterministic simulator).
            ax_client.complete_trial(
                trial_index,
                raw_data={
                    "t180": (res["t180"], 0.0),
                    "e_reb_mJ": (res["e_reb_mJ"], 0.0),
                    "mass_g": (res["mass_g"], 0.0),
                },
            )
            rows.append(
                {"seed": seed, "round": rnd, "trial": t}
                | {p: params[p] for p in PARAM_NAMES}
                | {k: res[k] for k in ("t180", "e_reb_mJ", "mass_g")}
            )
            t += 1
    return finish_rows(rows)


# ------------------------------------------------------------------ driver


def _worker(task):
    method, seed, era_dir, acq = task
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    evaluate = load_instrument(era_dir)
    t0 = time.time()
    if method == "bo":
        try:
            import torch

            torch.set_num_threads(int(os.environ.get("REPRO_TORCH_THREADS", "1")))
        except ImportError:
            pass
        df = run_bo(evaluate, seed, *acq)
        out = OUTDIR / f"repro_bo_seed{seed}.csv"
    elif method == "heuristic":
        df = run_heuristic(evaluate, seed)
        out = OUTDIR / f"repro_baseline_heuristic_seed{seed}.csv"
    else:
        df = run_sampler(evaluate, method, seed)
        out = OUTDIR / f"repro_baseline_{method}_seed{seed}.csv"
    df.to_csv(out, index=False)
    return method, seed, float(df["hv"].iloc[-1]), time.time() - t0


def aggregate(methods, seeds):
    from scipy.stats import mannwhitneyu

    era_summary = {}
    rows = []
    finals = {}
    for method in methods:
        fin, bt, be = [], [], []
        for seed in seeds:
            name = (
                f"repro_bo_seed{seed}.csv"
                if method == "bo"
                else f"repro_baseline_{method}_seed{seed}.csv"
            )
            df = pd.read_csv(OUTDIR / name)
            fin.append(df["hv"].iloc[-1])
            bt.append(df["best_t180"].iloc[-1])
            be.append(df["best_e_reb_mJ"].iloc[-1])
        finals[method] = np.array(fin)
        rows.append(
            {
                "strategy": "botorch" if method == "bo" else method,
                "n_seeds": len(seeds),
                "budget": BUDGET,
                "final_hv_mean": np.mean(fin),
                "final_hv_sd": np.std(fin, ddof=1),
                "best_t180_mean": np.mean(bt),
                "best_t180_sd": np.std(bt, ddof=1),
                "best_e_reb_mJ_mean": np.mean(be),
                "best_e_reb_mJ_sd": np.std(be, ddof=1),
                "hv_frac_of_reference": np.mean(fin) / REFERENCE_HV,
            }
        )
    if "bo" in finals:
        for r in rows:
            if r["strategy"] == "botorch":
                r["mannwhitney_p_vs_bo"] = np.nan
            else:
                m = {"botorch": "bo"}.get(r["strategy"], r["strategy"])
                r["mannwhitney_p_vs_bo"] = mannwhitneyu(
                    finals["bo"], finals[m], alternative="greater"
                ).pvalue
    summary = pd.DataFrame(rows)
    summary.to_csv(OUTDIR / "repro_summary.csv", index=False)
    print(summary.to_string(index=False))
    return summary, finals


def make_figures(methods, seeds, era_outputs: Path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    palette = {
        "bo": "#0072B2",
        "sobol": "#E69F00",
        "lhs": "#009E73",
        "random": "#CC79A7",
        "heuristic": "#D55E00",
    }
    label = {
        "bo": "BO (qNEHVI)",
        "sobol": "Sobol",
        "lhs": "Latin hypercube",
        "random": "random",
        "heuristic": "compass",
    }

    def load_all(method, blind=True):
        trajs = []
        for seed in seeds:
            if blind:
                name = (
                    f"repro_bo_seed{seed}.csv"
                    if method == "bo"
                    else f"repro_baseline_{method}_seed{seed}.csv"
                )
                df = pd.read_csv(OUTDIR / name)
            else:
                name = (
                    f"pr102_sim_bo_botorch_sobol_seed{seed}.csv"
                    if method == "bo"
                    else f"pr102_baseline_{method}_seed{seed}.csv"
                )
                df = pd.read_csv(era_outputs / name)
            trajs.append(df["hv"].values[:BUDGET])
        return np.vstack(trajs)

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    x = np.arange(1, BUDGET + 1)

    ax = axes[0]
    for method in methods:
        tr = load_all(method)
        mean, sd = tr.mean(axis=0), tr.std(axis=0, ddof=1)
        ls = "-" if method == "bo" else "--"
        ax.plot(x, mean, color=palette[method], ls=ls, lw=2, label=label[method])
        ax.fill_between(x, mean - sd, mean + sd, color=palette[method], alpha=0.15, lw=0)
        ax.annotate(
            label[method],
            (x[-1], mean[-1]),
            xytext=(4, 0),
            textcoords="offset points",
            color=palette[method],
            fontsize=8,
            va="center",
        )
    ax.axhline(REFERENCE_HV, color="0.4", lw=1, ls=":")
    ax.annotate(
        "reference 18.024", (1, REFERENCE_HV), xytext=(0, -10),
        textcoords="offset points", color="0.4", fontsize=8,
    )
    ax.set_xlim(1, BUDGET + 6)
    ax.set_xlabel("evaluation")
    ax.set_ylabel("hypervolume (fixed ref)")
    ax.set_title("Blind rerun: mean +- 1 sd across 10 seeds")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=8, loc="lower right")

    ax = axes[1]
    for method in methods:
        tr_b = load_all(method, blind=True)
        tr_e = load_all(method, blind=False)
        ax.plot(x, tr_b.mean(axis=0), color=palette[method], lw=2)
        ax.plot(x, tr_e.mean(axis=0), color=palette[method], lw=1.2, ls=":", alpha=0.8)
    ax.axhline(REFERENCE_HV, color="0.4", lw=1, ls=":")
    ax.set_xlim(1, BUDGET)
    ax.set_xlabel("evaluation")
    ax.set_ylabel("hypervolume (fixed ref)")
    ax.set_title("Blind (solid) vs era committed (dotted), per-method means")
    ax.grid(alpha=0.25)

    ax = axes[2]
    era_sum = pd.read_csv(era_outputs / "pr102_baselines_summary.csv")
    blind_sum = pd.read_csv(OUTDIR / "repro_summary.csv")
    order = ["botorch", "heuristic", "sobol", "lhs", "random"]
    key = {"botorch": "bo"}
    ypos = np.arange(len(order))
    for i, strat in enumerate(order):
        m = key.get(strat, strat)
        e = era_sum[era_sum.strategy == strat].iloc[0]
        b = blind_sum[blind_sum.strategy == strat].iloc[0]
        ax.errorbar(
            e.final_hv_mean, i + 0.17, xerr=e.final_hv_sd, fmt="o",
            color="0.45", ms=6, capsize=3,
        )
        ax.errorbar(
            b.final_hv_mean, i - 0.17, xerr=b.final_hv_sd, fmt="s",
            color=palette[m], ms=6, capsize=3,
        )
    ax.axvline(REFERENCE_HV, color="0.4", lw=1, ls=":")
    ax.set_yticks(ypos)
    ax.set_yticklabels([label[key.get(s, s)] for s in order])
    ax.invert_yaxis()
    ax.set_xlabel("final hypervolume at 36 designs (mean +- 1 sd)")
    ax.set_title("Blind rerun (color) vs era committed (gray)")
    ax.grid(alpha=0.25, axis="x")

    fig.tight_layout()
    fig.savefig(OUTDIR / "repro_comparison.png", dpi=160)
    print("wrote", OUTDIR / "repro_comparison.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--era-dir", default="/tmp/era/simulations")
    ap.add_argument(
        "--methods",
        nargs="+",
        default=["bo", "random", "sobol", "lhs", "heuristic"],
    )
    ap.add_argument("--seeds", nargs="+", type=int, default=list(range(10)))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--acq-restarts", type=int, default=None)
    ap.add_argument("--acq-raw-samples", type=int, default=None)
    ap.add_argument("--aggregate-only", action="store_true")
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    era_outputs = Path(args.era_dir) / "outputs"
    if not args.aggregate_only:
        tasks = [
            (m, s, args.era_dir, (args.acq_restarts, args.acq_raw_samples))
            for m in args.methods
            for s in args.seeds
        ]
        # cheap sampler tasks first so BO owns the cores at the end
        tasks.sort(key=lambda t: (t[0] == "bo", t[1]))
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            for method, seed, hv, dt in ex.map(_worker, tasks):
                print(f"{method} seed {seed}: final hv {hv:.4f}  ({dt:.0f} s)", flush=True)
    aggregate(args.methods, args.seeds)
    make_figures(args.methods, args.seeds, era_outputs)


if __name__ == "__main__":
    main()
