"""Baselines and a reference optimum for the PR #102 simulation-only campaign.

``pr102_sim_campaign.py`` runs the campaign's own loop (Sobol round 0, then
qNEHVI or SAASBO) against ``drop_tower_sim``.  On its own that says nothing
about whether the loop is *worth running*: a hypervolume trace that climbs
is only interesting relative to what climbs without a model, and a final
number is only interesting relative to what the box actually contains.

This module supplies both halves of that comparison.

**Baselines**, each run at the campaign's own budget (4 batches of 9 = 36
designs) and repeated over the same ten seeds, so their spread is directly
comparable to the campaign's:

``random``
    Uniform i.i.d. draws.  The floor: any method that cannot beat this is
    not doing anything.
``sobol``
    Scrambled Sobol over the whole budget.  This is the campaign's round 0
    extended to fill the budget, so the difference between it and the
    campaign is exactly what the surrogate contributes and nothing else.
``lhs``
    Scrambled Latin hypercube, the other standard space-filling design.
``heuristic``
    What an engineer does by hand: pick a weighting of the two objectives
    and hill-climb.  Implemented as compass (pattern) search with a
    halving step, on a normalized weighted sum, and the budget split over
    three weights (0.15 / 0.5 / 0.85) so that it produces a spread of
    trade-offs rather than one point.  Local, deterministic given its
    start; the seed sets the start and the axis order.

**Reference optimum** (``--reference``): a much less restricted budget --
65 536 scrambled Sobol designs, about 1800x the campaign's -- followed by a
Nelder-Mead polish of the best point under each of 21 weightings.  Its
non-dominated set is the best estimate of the true front available at this
fidelity, and its hypervolume is the ceiling every trace in the comparison
figure is drawn against.  It is not proof of a global optimum; it is a
dense enough sample that a method finishing well short of it is leaving
something on the table.

Every evaluation any of these performs is written to CSV, including the
full 65 536-row reference cloud, so plots and analyses can be redone later
without re-running anything.

Run::

    python pr102_baselines.py --reference --jobs 4      # the ceiling, ~11 min
    python pr102_baselines.py --strategies random sobol lhs heuristic --jobs 4
    python pr102_baselines.py --compare                 # figures only
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import pandas as pd
from scipy.stats import qmc

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import drop_tower_sim  # noqa: E402
from pr102_sim_campaign import (  # noqa: E402
    MASS, OBJ1, OBJ2, OUT, PARAMETERS, PARAM_NAMES,
    hypervolume_2d, reference_point,
)


def evaluate(params: dict) -> dict:
    """Score one design, keeping the feasibility flag.

    ``pr102_sim_campaign.evaluate`` drops everything but the two objectives
    and the mass because Ax wants exactly those; here the ``ok`` flag and
    the constant-mass print scale are worth keeping in the saved CSV.
    """
    res = drop_tower_sim.evaluate_pr102(params)
    return {OBJ1: float(res["t180"]), OBJ2: float(res["e_reb_mJ"]),
            MASS: float(res["mass_printed_g"]),
            "print_scale": float(res.get("print_scale", float("nan"))),
            "ok": bool(res.get("ok", True))}

BOUNDS_LO = np.array([p["bounds"][0] for p in PARAMETERS], dtype=float)
BOUNDS_HI = np.array([p["bounds"][1] for p in PARAMETERS], dtype=float)

BUDGET = 36          # 4 batches of 9, the campaign's own budget
BATCH = 9
SEEDS = list(range(10))

REFERENCE_N = 65536          # 2**16
REFERENCE_SEED = 12345
N_POLISH_WEIGHTS = 21

STRATEGY_STYLE = {
    "botorch": ("#2a78d6", "BO (qNEHVI)"),
    "sobol": ("#0f9d58", "Sobol"),
    "lhs": ("#f4a11d", "Latin hypercube"),
    "random": ("#9aa0a6", "random search"),
    "heuristic": ("#c0392b", "compass search"),
}


def _as_params(x: np.ndarray) -> dict:
    return {n: float(v) for n, v in zip(PARAM_NAMES, x)}


def _clip(x: np.ndarray) -> np.ndarray:
    return np.clip(x, BOUNDS_LO, BOUNDS_HI)


def _scale(unit: np.ndarray) -> np.ndarray:
    return BOUNDS_LO + unit * (BOUNDS_HI - BOUNDS_LO)


# --- the sampling baselines ----------------------------------------------

def _points_random(seed: int, n: int) -> np.ndarray:
    return _scale(np.random.default_rng(seed).random((n, len(PARAM_NAMES))))


def _points_sobol(seed: int, n: int) -> np.ndarray:
    return _scale(qmc.Sobol(len(PARAM_NAMES), scramble=True,
                            seed=seed).random(n))


def _points_lhs(seed: int, n: int) -> np.ndarray:
    return _scale(qmc.LatinHypercube(len(PARAM_NAMES), seed=seed).random(n))


# --- the heuristic --------------------------------------------------------

HEURISTIC_WEIGHTS = (0.15, 0.5, 0.85)


def _scalarize(res: dict, w: float, ref: np.ndarray) -> float:
    """Weighted sum of the two objectives, each normalized by the reference.

    Normalizing matters: ``t180`` is order 0.5 and ``e_reb_mJ`` is order
    200, so an un-normalized sum is a single-objective search on
    ``e_reb_mJ``.
    """
    return w * res[OBJ1] / ref[0] + (1.0 - w) * res[OBJ2] / ref[1]


def _run_heuristic(seed: int, budget: int, ref: np.ndarray) -> list[dict]:
    """Compass search with a halving step, on each of three weightings.

    Each weighting gets an equal slice of the budget.  From the current
    point the search probes one axis at a time, plus and minus the current
    step, accepts the first improvement it finds and otherwise halves the
    step -- the textbook pattern search, and a fair stand-in for turning
    one knob at a time on the bench.
    """
    rng = np.random.default_rng(seed)
    rows, spent = [], 0
    per_weight = budget // len(HEURISTIC_WEIGHTS)

    for wi, w in enumerate(HEURISTIC_WEIGHTS):
        left = per_weight if wi < len(HEURISTIC_WEIGHTS) - 1 else budget - spent
        if left <= 0:
            break
        x = _scale(rng.random(len(PARAM_NAMES)))
        res = evaluate(_as_params(x))
        rows.append({**_as_params(x), **res})
        spent += 1
        left -= 1
        best = _scalarize(res, w, ref)
        step = 0.35 * np.ones(len(PARAM_NAMES))     # fraction of each range
        span = BOUNDS_HI - BOUNDS_LO

        while left > 0:
            improved = False
            for ax in rng.permutation(len(PARAM_NAMES)):
                for sign in (+1.0, -1.0):
                    if left <= 0:
                        break
                    cand = x.copy()
                    cand[ax] = float(np.clip(
                        x[ax] + sign * step[ax] * span[ax],
                        BOUNDS_LO[ax], BOUNDS_HI[ax]))
                    if np.isclose(cand[ax], x[ax]):
                        continue
                    res = evaluate(_as_params(cand))
                    rows.append({**_as_params(cand), **res})
                    spent += 1
                    left -= 1
                    val = _scalarize(res, w, ref)
                    if val < best:
                        best, x, improved = val, cand, True
                        break
                if left <= 0:
                    break
            if not improved:
                step *= 0.5
                if step.max() < 1e-3:
                    step = 0.35 * np.ones(len(PARAM_NAMES))
    return rows


# --- one baseline run -----------------------------------------------------

def run_strategy(strategy: str, seed: int, budget: int = BUDGET,
                 batch: int = BATCH, outdir: Path = OUT) -> pd.DataFrame:
    ref = reference_point()
    if strategy == "heuristic":
        rows = _run_heuristic(seed, budget, ref)
    else:
        pts = {"random": _points_random, "sobol": _points_sobol,
               "lhs": _points_lhs}[strategy](seed, budget)
        rows = [{**_as_params(x), **evaluate(_as_params(x))} for x in pts]

    df = pd.DataFrame(rows)
    df.insert(0, "trial", np.arange(len(df)))
    df.insert(0, "round", df["trial"] // batch)
    df.insert(0, "seed", seed)
    df.insert(0, "strategy", strategy)
    obj = df[[OBJ1, OBJ2]].to_numpy(dtype=float)
    df["hv"] = [hypervolume_2d(obj[: i + 1], ref) for i in range(len(obj))]
    df["best_t180"] = df[OBJ1].cummin()
    df["best_e_reb_mJ"] = df[OBJ2].cummin()

    outdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(outdir / f"pr102_baseline_{strategy}_seed{seed}.csv",
              index=False, float_format="%.6g")
    return df


def _strategy_worker(job: tuple) -> str:
    strategy, seed, budget, batch, outdir = job
    t0 = time.time()
    run_strategy(strategy, seed, budget, batch, Path(outdir))
    print(f"  {strategy} seed {seed}: {budget} designs, "
          f"{time.time() - t0:.1f} s", flush=True)
    return f"{strategy}_seed{seed}"


# --- the reference optimum ------------------------------------------------

def _reference_chunk(job: tuple) -> pd.DataFrame:
    lo, hi, pts = job
    rows = []
    for i in range(lo, hi):
        p = _as_params(pts[i])
        rows.append({"i": i, **p, **evaluate(p)})
    return pd.DataFrame(rows)


def pareto_mask(obj: np.ndarray) -> np.ndarray:
    """Non-dominated mask for a *minimization* objective matrix."""
    n = len(obj)
    keep = np.ones(n, dtype=bool)
    order = np.argsort(obj[:, 0], kind="stable")
    best_y = np.inf
    for i in order:
        if obj[i, 1] < best_y - 1e-15:
            best_y = obj[i, 1]
        else:
            keep[i] = False
    return keep


def run_reference(n: int = REFERENCE_N, jobs: int = 4,
                  outdir: Path = OUT) -> pd.DataFrame:
    """Dense Sobol sweep plus a Nelder-Mead polish, as the front's ceiling."""
    ref = reference_point()
    pts = _points_sobol(REFERENCE_SEED, n)
    print(f"reference sweep: {n} designs over {jobs} process(es)", flush=True)

    t0 = time.time()
    edges = np.linspace(0, n, jobs + 1).astype(int)
    chunks = [(int(a), int(b), pts) for a, b in zip(edges[:-1], edges[1:])]
    if jobs > 1:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(jobs) as pool:
            frames = pool.map(_reference_chunk, chunks)
    else:
        frames = [_reference_chunk(c) for c in chunks]
    sweep = pd.concat(frames).sort_values("i").reset_index(drop=True)
    sweep["source"] = "sobol"
    print(f"  swept {len(sweep)} designs in {time.time() - t0:.1f} s "
          f"({1e3 * (time.time() - t0) / len(sweep):.1f} ms each)", flush=True)

    # Polish: from the best sweep point under each weighting, run Nelder-Mead
    # on that same weighted sum.  The sweep resolves the front's shape; the
    # polish stops the reported ceiling from being limited by sample spacing.
    from scipy.optimize import minimize
    ok = sweep[sweep["ok"].astype(bool)]
    polish_rows = []
    t0 = time.time()
    for w in np.linspace(0.0, 1.0, N_POLISH_WEIGHTS):
        s = (w * ok[OBJ1].to_numpy() / ref[0]
             + (1.0 - w) * ok[OBJ2].to_numpy() / ref[1])
        x0 = ok.iloc[int(np.argmin(s))][PARAM_NAMES].to_numpy(dtype=float)
        trace = []

        def f(x, _w=w, _trace=trace):
            p = _as_params(_clip(x))
            r = evaluate(p)
            _trace.append({**p, **r})
            if not r.get("ok", True) or not np.isfinite(r[OBJ1]):
                return 1e6
            return _scalarize(r, _w, ref)

        minimize(f, x0, method="Nelder-Mead",
                 options={"maxfev": 300, "xatol": 1e-3, "fatol": 1e-9})
        for row in trace:
            polish_rows.append({**row, "weight": w})
    polish = pd.DataFrame(polish_rows)
    polish["source"] = "polish"
    print(f"  polished {N_POLISH_WEIGHTS} weightings with {len(polish)} "
          f"evaluations in {time.time() - t0:.1f} s", flush=True)

    allr = pd.concat([sweep, polish], ignore_index=True)
    allr = allr[allr["ok"].astype(bool)].reset_index(drop=True)
    obj = allr[[OBJ1, OBJ2]].to_numpy(dtype=float)
    allr["pareto"] = pareto_mask(obj)
    hv = hypervolume_2d(obj, ref)

    outdir.mkdir(parents=True, exist_ok=True)
    # gzipped because it is 65 k rows; pandas reads it with no extra step.
    allr.to_csv(outdir / "pr102_reference_cloud.csv.gz", index=False,
                float_format="%.6g", compression="gzip")
    front = allr[allr["pareto"]].sort_values(OBJ1)
    front.to_csv(outdir / "pr102_reference_front.csv", index=False,
                 float_format="%.6g")
    pd.DataFrame([{"n_sweep": len(sweep), "n_polish": len(polish),
                   "n_feasible": len(allr), "n_pareto": int(allr["pareto"].sum()),
                   "hv": hv, "ref_t180": ref[0], "ref_e_reb_mJ": ref[1],
                   "best_t180": float(allr[OBJ1].min()),
                   "best_e_reb_mJ": float(allr[OBJ2].min())}]).to_csv(
        outdir / "pr102_reference_summary.csv", index=False, float_format="%.6g")
    print(f"reference hypervolume {hv:.4f}, front {int(allr['pareto'].sum())} "
          f"points, best t180 {allr[OBJ1].min():.4f}, "
          f"best e_reb_mJ {allr[OBJ2].min():.3f}")
    plot_reference(allr, front, outdir)
    return allr


def plot_reference(allr: pd.DataFrame, front: pd.DataFrame,
                   outdir: Path) -> None:
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 4.6), dpi=200)
    ax.scatter(allr[OBJ1], allr[OBJ2], s=2, alpha=0.15, color="#9aa0a6",
               rasterized=True, label=f"{len(allr)} designs")
    ax.plot(front[OBJ1], front[OBJ2], color="#c0392b", lw=2, marker="o", ms=3,
            label=f"reference front ({len(front)})")
    ax.set_xlabel("t180 (simulated, minimize)")
    ax.set_ylabel("e_reb_mJ (simulated, minimize)")
    ax.set_title("Reference sweep over the PR #102 box", fontsize=10)
    ax.grid(alpha=0.25, lw=0.5)
    ax.legend(fontsize=8)

    # Where on the box the front lives, per parameter, as a normalized
    # position: this is the actionable read of the front.
    lo, hi = BOUNDS_LO, BOUNDS_HI
    unit = (front[PARAM_NAMES].to_numpy(dtype=float) - lo) / (hi - lo)
    for j, name in enumerate(PARAM_NAMES):
        ax2.plot(front[OBJ1], unit[:, j], lw=1.5, label=name)
    ax2.set_xlabel("t180 along the reference front")
    ax2.set_ylabel("position in the box (0 = low bound, 1 = high)")
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_title("Front geometry", fontsize=10)
    ax2.grid(alpha=0.25, lw=0.5)
    ax2.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(outdir / "pr102_reference_front.png", bbox_inches="tight")
    plt.close(fig)


# --- comparison -----------------------------------------------------------

def _load_traces(outdir: Path, strategy: str) -> list[pd.DataFrame]:
    if strategy == "botorch":
        files = sorted(outdir.glob("pr102_sim_bo_botorch_sobol_seed*.csv"),
                       key=lambda f: int(f.stem.split("seed")[-1]))
        files = [f for f in files if "_solid" not in f.name]
    else:
        files = sorted(outdir.glob(f"pr102_baseline_{strategy}_seed*.csv"),
                       key=lambda f: int(f.stem.split("seed")[-1]))
    return [pd.read_csv(f) for f in files]


def compare(outdir: Path = OUT, strategies=("botorch", "sobol", "lhs",
                                            "random", "heuristic")) -> None:
    ref_hv = ref_t180 = ref_ereb = None
    summary_path = outdir / "pr102_reference_summary.csv"
    if summary_path.exists():
        s = pd.read_csv(summary_path).iloc[0]
        ref_hv, ref_t180, ref_ereb = s["hv"], s["best_t180"], s["best_e_reb_mJ"]

    panels = [("hv", "dominated hypervolume", ref_hv),
              ("best_t180", "running-best t180", ref_t180),
              ("best_e_reb_mJ", "running-best e_reb_mJ (mJ)", ref_ereb)]
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4), dpi=200)

    rows = []
    for strategy in strategies:
        frames = _load_traces(outdir, strategy)
        if not frames:
            print(f"no traces for {strategy}, skipping")
            continue
        n = min(len(f) for f in frames)
        colour, label = STRATEGY_STYLE[strategy]
        x = np.arange(1, n + 1)
        for ax, (col, ylabel, ref_val) in zip(axes, panels):
            arr = np.vstack([f[col].to_numpy()[:n] for f in frames])
            mean, sd = arr.mean(axis=0), arr.std(axis=0)
            ax.plot(x, mean, color=colour, lw=2, label=f"{label} (n={len(frames)})")
            ax.fill_between(x, mean - sd, mean + sd, color=colour, alpha=0.15)
            ax.set_xlabel("simulated design")
            ax.set_ylabel(ylabel)
            ax.grid(alpha=0.25, lw=0.5)
        final = np.array([f[panels[0][0]].to_numpy()[n - 1] for f in frames])
        bt = np.array([f["best_t180"].to_numpy()[n - 1] for f in frames])
        be = np.array([f["best_e_reb_mJ"].to_numpy()[n - 1] for f in frames])
        rows.append({"strategy": strategy, "n_seeds": len(frames), "budget": n,
                     "final_hv_mean": final.mean(), "final_hv_sd": final.std(),
                     "best_t180_mean": bt.mean(), "best_t180_sd": bt.std(),
                     "best_e_reb_mJ_mean": be.mean(),
                     "best_e_reb_mJ_sd": be.std(),
                     "hv_frac_of_reference": (final.mean() / ref_hv
                                              if ref_hv else np.nan)})

    for ax, (_, _, ref_val) in zip(axes, panels):
        if ref_val is not None and np.isfinite(ref_val):
            ax.axhline(ref_val, color="#111111", ls="--", lw=1.2,
                       label="reference (65 k + polish)")
        ax.legend(fontsize=7.5)
    axes[0].set_title("Hypervolume against a fixed reference point", fontsize=10)
    axes[1].set_title("Best t180 so far", fontsize=10)
    axes[2].set_title("Best e_reb_mJ so far", fontsize=10)
    fig.suptitle("Simulation-only T-3_01 campaign against baselines, "
                 "mean +/- 1 sd over 10 seeds", fontsize=11)
    fig.tight_layout()
    fig.savefig(outdir / "pr102_baselines_comparison.png", bbox_inches="tight")
    plt.close(fig)

    summary = pd.DataFrame(rows)

    # Ten seeds per method is few enough that the +/- 1 sd bands overlap in
    # places, so test the final hypervolumes rather than eyeballing them.
    # Mann-Whitney rather than a t-test: n = 10 and hypervolume is bounded
    # above by the reference, so normality is not on offer.
    from scipy.stats import mannwhitneyu
    ref_frames = _load_traces(outdir, "botorch")
    if ref_frames:
        base = np.array([f["hv"].to_numpy()[-1] for f in ref_frames])
        pvals = []
        for strategy in strategies:
            if strategy == "botorch":
                pvals.append(np.nan)
                continue
            frames = _load_traces(outdir, strategy)
            if not frames:
                continue
            other = np.array([f["hv"].to_numpy()[-1] for f in frames])
            pvals.append(mannwhitneyu(base, other, alternative="greater").pvalue)
        if len(pvals) == len(summary):
            summary["mannwhitney_p_vs_bo"] = pvals

    summary.to_csv(outdir / "pr102_baselines_summary.csv", index=False,
                   float_format="%.6g")
    print(summary.to_string(index=False))

    # Objective-space panel: every method's evaluations against the front.
    front_path = outdir / "pr102_reference_front.csv"
    if front_path.exists():
        front = pd.read_csv(front_path)
        fig, ax = plt.subplots(figsize=(6.8, 5.2), dpi=200)
        ax.plot(front[OBJ1], front[OBJ2], color="#111111", lw=1.8, zorder=5,
                label="reference front")
        for strategy in strategies:
            frames = _load_traces(outdir, strategy)
            if not frames:
                continue
            colour, label = STRATEGY_STYLE[strategy]
            allpts = pd.concat(frames)
            ax.scatter(allpts[OBJ1], allpts[OBJ2], s=7, alpha=0.35,
                       color=colour, label=label)
        ax.set_xlabel("t180 (simulated, minimize)")
        ax.set_ylabel("e_reb_mJ (simulated, minimize)")
        ax.set_title("Where each method spent its 36 designs "
                     "(10 seeds pooled)", fontsize=10)
        ax.grid(alpha=0.25, lw=0.5)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(outdir / "pr102_baselines_objective_space.png",
                    bbox_inches="tight")
        plt.close(fig)
    print(f"Wrote {outdir}/pr102_baselines_comparison.png and _summary.csv")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strategies", nargs="*",
                    default=["random", "sobol", "lhs", "heuristic"])
    ap.add_argument("--seeds", type=int, nargs="*", default=SEEDS)
    ap.add_argument("--budget", type=int, default=BUDGET)
    ap.add_argument("--batch-size", type=int, default=BATCH)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--reference", action="store_true",
                    help="run the dense reference sweep instead of baselines")
    ap.add_argument("--reference-n", type=int, default=REFERENCE_N)
    ap.add_argument("--compare", action="store_true",
                    help="only rebuild the comparison figures from CSVs")
    ap.add_argument("--outdir", type=Path, default=OUT)
    args = ap.parse_args(argv)

    if args.reference:
        run_reference(args.reference_n, args.jobs, args.outdir)
        return 0
    if args.compare:
        compare(args.outdir)
        return 0

    jobs = [(s, seed, args.budget, args.batch_size, str(args.outdir))
            for s in args.strategies for seed in args.seeds]
    print(f"{len(jobs)} baseline run(s): {args.budget} designs each")
    t0 = time.time()
    if args.jobs > 1 and len(jobs) > 1:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(min(args.jobs, len(jobs))) as pool:
            for _ in pool.imap_unordered(_strategy_worker, jobs):
                pass
    else:
        for job in jobs:
            _strategy_worker(job)
    print(f"{len(jobs)} run(s) in {time.time() - t0:.1f} s")
    compare(args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
