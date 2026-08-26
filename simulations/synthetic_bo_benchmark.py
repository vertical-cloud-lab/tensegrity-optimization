"""The BO-vs-DOE benchmark harness, re-run on synthetic analytic problems.

The physics study (``bo_contrast_study.py``) reports that constrained qNEHVI
reaches 94.2 % of a dense-sweep hypervolume ceiling on one objective pair
while every uninformed baseline lands at 77.5 to 80.2 %, and that on a
different pair the same code is statistically indistinguishable from random
search.  Our claim is that the difference is objective geometry, not
optimizer quality.  That claim is only worth anything if the harness itself
is sound, so this module runs the *same* harness on analytic problems whose
answers are known in advance:

* ``branin``            one objective, 2 D.  Known global minimum 0.397887.
                        Any working BO must beat random search here by a
                        wide margin.  If it does not, the implementation is
                        broken and nothing downstream survives.
* ``branin_negated``    minimize (Branin, -Branin).  Every point in the
                        domain is Pareto optimal by construction, so the
                        front is free and a space-filling design should tie
                        the optimizer.  This is the deliberate negative
                        control: "multi-objective" alone does not create a
                        BO advantage.
* ``branin_currin``     the standard 2-objective Branin-Currin benchmark on
                        the unit square, a genuine curved trade-off.  BO is
                        expected to separate.
* ``branin_currin_c``   Branin-Currin with the standard disk constraint
                        (x1 - 0.5)^2 + (x2 - 0.5)^2 <= 0.2, given to Ax as an
                        outcome constraint.  This is the only synthetic that
                        exercises the constraint plumbing the physics study
                        depends on.
* ``branin_currin_4d``  Branin-Currin embedded in 4 dimensions with two
                        inactive nuisance axes, so the search-space
                        dimension matches the physics study's four shape
                        ratios.

Everything that could differ between the physics study and this one is held
fixed: the generation strategy (9-design Sobol round 0 seeded with the
repeat's own seed, then ``BOTORCH_MODULAR`` at 8 restarts x 128 raw samples),
the 45-evaluation budget, the ten seeds, the four baselines (uniform random,
scrambled Sobol, scrambled Latin hypercube, compass search), the two baseline
modes (``plain`` and constraint-filtered ``feasible``), the hypervolume
routine, the reference-point rule, the Nelder-Mead polish of the ceiling, and
the Mann-Whitney comparison.

One convention had to be generalized.  The physics study inflates the
reference point as ``1.05 * worst``, which is only monotone for positive
objectives (it holds there: t180 and envelope_cm3 are both positive).  The
negated-Branin objective is negative, where that rule moves the reference
point the wrong way, so this module uses the sign-safe
``worst + 0.05 * (worst - best)`` over the feasible cloud, which coincides
with the study's rule whenever the best value is zero and is never worse
behaved.

Run::

    python synthetic_bo_benchmark.py --cloud --screen
    python synthetic_bo_benchmark.py --campaign --baselines --jobs 4
    python synthetic_bo_benchmark.py --compare
"""
from __future__ import annotations

import argparse
import json
import math
import os
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import pandas as pd
from scipy.optimize import minimize as scipy_minimize
from scipy.stats import qmc, mannwhitneyu, wilcoxon

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "synthetic_bo"

# Held identical to bo_contrast_study.py.
BUDGET = 45
BATCH = 9
ROUNDS = 4
SEEDS = list(range(10))
ACQ_RESTARTS = 8
ACQ_RAW_SAMPLES = 128
CLOUD_N = 16384
CLOUD_SEED = 20260826
MC_DRAWS = 2000
REF_INFLATION = 0.05          # of the feasible cloud's range, sign-safe
POLISH_WEIGHTS = 21

# The two physics-study results this control exists to bracket, taken from
# the committed bo_contrast summaries so the overview scatter can show
# synthetic and real points on one axis.  (free hypervolume of an uninformed
# 45-design batch, BO fraction of ceiling, best-baseline fraction of ceiling)
PHYSICS_ANCHORS = {
    "physics: t180 + envelope": (0.800, 0.9423, 0.8020),
    "physics: t180 + strain": (0.846, 0.8271, 0.7990),
}

STRATEGY_STYLE = {
    "botorch": ("BO (qNEHVI)", "tab:blue"),
    "sobol": ("Sobol", "tab:orange"),
    "lhs": ("Latin hypercube", "tab:green"),
    "random": ("random search", "tab:red"),
    "heuristic": ("compass search", "tab:purple"),
}


# --- the analytic problems -------------------------------------------------

def _branin_raw(x1: float, x2: float) -> float:
    a, b, c = 1.0, 5.1 / (4.0 * math.pi ** 2), 5.0 / math.pi
    r, s, t = 6.0, 10.0, 1.0 / (8.0 * math.pi)
    return (a * (x2 - b * x1 * x1 + c * x1 - r) ** 2
            + s * (1.0 - t) * math.cos(x1) + s)


def _branin_unit(u1: float, u2: float) -> float:
    """Branin on the unit square, the standard [0,1]^2 rescaling."""
    return _branin_raw(15.0 * u1 - 5.0, 15.0 * u2)


def _currin(u1: float, u2: float) -> float:
    u2 = max(u2, 1e-12)
    fac = 1.0 - math.exp(-1.0 / (2.0 * u2))
    num = 2300.0 * u1 ** 3 + 1900.0 * u1 ** 2 + 2092.0 * u1 + 60.0
    den = 100.0 * u1 ** 3 + 500.0 * u1 ** 2 + 4.0 * u1 + 20.0
    return fac * num / den


def _f_branin(x: np.ndarray) -> dict:
    return {"branin": _branin_raw(float(x[0]), float(x[1]))}


def _f_branin_negated(x: np.ndarray) -> dict:
    v = _branin_raw(float(x[0]), float(x[1]))
    return {"branin": v, "neg_branin": -v}


def _f_branin_currin(x: np.ndarray) -> dict:
    return {"branin": _branin_unit(float(x[0]), float(x[1])),
            "currin": _currin(float(x[0]), float(x[1]))}


def _f_branin_currin_c(x: np.ndarray) -> dict:
    res = _f_branin_currin(x)
    # BoTorch's ConstrainedBraninCurrin disk feasibility, expressed as a
    # slack that Ax constrains to be non-negative.
    res["disk_slack"] = 0.2 - ((float(x[0]) - 0.5) ** 2
                               + (float(x[1]) - 0.5) ** 2)
    return res


def _f_branin_currin_4d(x: np.ndarray) -> dict:
    # Axes 2 and 3 are nuisance dimensions the objectives ignore, matching
    # the physics study's four-dimensional search space.
    return _f_branin_currin(x)


PROBLEMS: dict[str, dict] = {
    "branin": {
        "fn": _f_branin,
        "params": [("x1", -5.0, 10.0), ("x2", 0.0, 15.0)],
        "objectives": ("branin",),
        "constraints": [],
        "known_optimum": 0.39788735772973816,
        "why": "single-objective sanity check with a known global minimum; "
               "a working BO must beat random search by a wide margin",
    },
    "branin_negated": {
        "fn": _f_branin_negated,
        "params": [("x1", -5.0, 10.0), ("x2", 0.0, 15.0)],
        "objectives": ("branin", "neg_branin"),
        "constraints": [],
        "known_optimum": None,
        "why": "degenerate control: every point is Pareto optimal, so the "
               "front is free and BO should tie the samplers",
    },
    "branin_currin": {
        "fn": _f_branin_currin,
        "params": [("x1", 0.0, 1.0), ("x2", 0.0, 1.0)],
        "objectives": ("branin", "currin"),
        "constraints": [],
        "known_optimum": None,
        "why": "standard 2-objective benchmark with a genuine curved "
               "trade-off; BO expected to separate",
    },
    "branin_currin_c": {
        "fn": _f_branin_currin_c,
        "params": [("x1", 0.0, 1.0), ("x2", 0.0, 1.0)],
        "objectives": ("branin", "currin"),
        "constraints": [("disk_slack", ">=", 0.0)],
        "known_optimum": None,
        "why": "the same problem with the standard disk constraint, the "
               "only synthetic that exercises the outcome-constraint "
               "plumbing the physics study relies on",
    },
    "branin_currin_4d": {
        "fn": _f_branin_currin_4d,
        "params": [("x1", 0.0, 1.0), ("x2", 0.0, 1.0),
                   ("x3", 0.0, 1.0), ("x4", 0.0, 1.0)],
        "objectives": ("branin", "currin"),
        "constraints": [],
        "known_optimum": None,
        "why": "Branin-Currin with two inactive nuisance axes so the search "
               "dimension matches the physics study's four shape ratios",
    },
}


def bounds_of(problem: str) -> tuple[np.ndarray, np.ndarray]:
    p = PROBLEMS[problem]["params"]
    return (np.array([b[1] for b in p], dtype=float),
            np.array([b[2] for b in p], dtype=float))


def param_names(problem: str) -> list[str]:
    return [b[0] for b in PROBLEMS[problem]["params"]]


def ax_parameters(problem: str) -> list[dict]:
    return [{"name": n, "type": "range", "bounds": [lo, hi],
             "value_type": "float"}
            for n, lo, hi in PROBLEMS[problem]["params"]]


def evaluate(problem: str, x: np.ndarray) -> dict:
    res = PROBLEMS[problem]["fn"](np.asarray(x, dtype=float))
    return {k: float(v) for k, v in res.items()}


def feasible_row(problem: str, res: dict) -> bool:
    for metric, op, bound in PROBLEMS[problem]["constraints"]:
        v = res[metric]
        if op == ">=" and not v >= bound:
            return False
        if op == "<=" and not v <= bound:
            return False
    return True


def feasible_mask(problem: str, df: pd.DataFrame) -> np.ndarray:
    ok = np.ones(len(df), dtype=bool)
    for metric, op, bound in PROBLEMS[problem]["constraints"]:
        v = df[metric].to_numpy(dtype=float)
        ok &= (v >= bound) if op == ">=" else (v <= bound)
    return ok


# --- hypervolume, generalized to one or two objectives ---------------------

def hypervolume(points: np.ndarray, ref: np.ndarray) -> float:
    """Dominated hypervolume of a minimization set against ``ref``.

    For two objectives this is the same sweep as
    ``pr102_sim_campaign.hypervolume_2d``, kept identical on purpose.  For
    one objective it degenerates to the simple-regret gap ``ref - min f``,
    so single- and multi-objective problems share one scoring code path.
    """
    pts = np.atleast_2d(points)
    if pts.shape[1] == 1:
        good = pts[pts[:, 0] < ref[0]]
        return 0.0 if good.size == 0 else float(ref[0] - good[:, 0].min())
    pts = pts[(pts < ref).all(axis=1)]
    if pts.size == 0:
        return 0.0
    pts = pts[np.argsort(pts[:, 0])]
    hv, best_y = 0.0, ref[1]
    for x, y in pts:
        if y < best_y:
            hv += (ref[0] - x) * (best_y - y)
            best_y = y
    return float(hv)


def domination_depth(z: np.ndarray, zf: np.ndarray) -> np.ndarray:
    """One-sided Chebyshev depth behind the front, identical to the
    ``_domination_depth`` the physics study's screen uses.  Depth 0 means on
    the front; depth d means some front point beats the point by d in its
    worst normalized objective."""
    out = np.empty(len(z))
    for a in range(0, len(z), 2048):
        diff = z[a:a + 2048, None, :] - zf[None, :, :]
        out[a:a + 2048] = np.maximum(diff.max(axis=2), 0.0).min(axis=1)
    return out


def pareto_mask(obj: np.ndarray) -> np.ndarray:
    n = len(obj)
    keep = np.ones(n, dtype=bool)
    for i in range(n):
        if not keep[i]:
            continue
        dominated = ((obj <= obj[i]).all(axis=1) & (obj < obj[i]).any(axis=1))
        if dominated.any():
            keep[i] = False
    return keep


# --- the dense cloud, reference point and ceiling --------------------------

def cloud_path(problem: str) -> Path:
    return OUT / f"synthetic_cloud_{problem}.csv.gz"


def build_cloud(problem: str, n: int = CLOUD_N) -> pd.DataFrame:
    lo, hi = bounds_of(problem)
    eng = qmc.Sobol(len(lo), scramble=True, seed=CLOUD_SEED)
    pts = lo + eng.random(n) * (hi - lo)
    names = param_names(problem)
    rows = []
    for x in pts:
        res = evaluate(problem, x)
        rows.append({**dict(zip(names, x)), **res})
    df = pd.DataFrame(rows)
    df["feasible"] = feasible_mask(problem, df)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(cloud_path(problem), index=False, float_format="%.8g")
    return df


def load_cloud(problem: str) -> pd.DataFrame:
    return pd.read_csv(cloud_path(problem))


def reference_point(problem: str, cloud: pd.DataFrame) -> np.ndarray:
    """Sign-safe generalization of the study's 1.05 x worst rule."""
    objs = PROBLEMS[problem]["objectives"]
    feas = cloud[cloud["feasible"].astype(bool)]
    worst = feas[list(objs)].to_numpy(dtype=float).max(axis=0)
    best = feas[list(objs)].to_numpy(dtype=float).min(axis=0)
    return worst + REF_INFLATION * (worst - best)


def _polish(problem: str, cloud: pd.DataFrame, ref: np.ndarray
            ) -> pd.DataFrame:
    """Nelder-Mead polish of the cloud's best weighted points, the same
    ceiling-sharpening step the physics study uses."""
    objs = list(PROBLEMS[problem]["objectives"])
    lo, hi = bounds_of(problem)
    feas = cloud[cloud["feasible"].astype(bool)]
    obj = feas[objs].to_numpy(dtype=float)
    span = np.where(ref - obj.min(axis=0) > 0, ref - obj.min(axis=0), 1.0)
    names = param_names(problem)
    X = feas[names].to_numpy(dtype=float)
    rows = []
    weights = ([0.0] if len(objs) == 1
               else np.linspace(0.0, 1.0, POLISH_WEIGHTS))
    for w in np.atleast_1d(weights):
        wv = (np.array([1.0]) if len(objs) == 1
              else np.array([w, 1.0 - w]))

        def scal(x):
            x = np.clip(x, lo, hi)
            res = evaluate(problem, x)
            if not feasible_row(problem, res):
                return 1e9
            z = np.array([res[o] for o in objs])
            return float(((z - obj.min(axis=0)) / span * wv).sum())

        start = X[np.argmin(((obj - obj.min(axis=0)) / span * wv).sum(axis=1))]
        out = scipy_minimize(scal, start, method="Nelder-Mead",
                             options={"maxiter": 400, "xatol": 1e-8,
                                      "fatol": 1e-10})
        x = np.clip(out.x, lo, hi)
        res = evaluate(problem, x)
        if feasible_row(problem, res):
            rows.append({**dict(zip(names, x)), **res})
    return pd.DataFrame(rows)


def build_reference(problem: str) -> dict:
    cloud = load_cloud(problem)
    ref = reference_point(problem, cloud)
    objs = list(PROBLEMS[problem]["objectives"])
    polish = _polish(problem, cloud, ref)
    feas = cloud[cloud["feasible"].astype(bool)]
    all_obj = feas[objs].to_numpy(dtype=float)
    if len(polish):
        all_obj = np.vstack([all_obj, polish[objs].to_numpy(dtype=float)])
    ceiling = hypervolume(all_obj, ref)
    front = all_obj[pareto_mask(all_obj)] if len(objs) > 1 else None
    info = {"problem": problem, "ref": ref.tolist(), "ceiling": ceiling,
            "cloud_hv": hypervolume(feas[objs].to_numpy(dtype=float), ref),
            "n_cloud": int(len(cloud)),
            "n_feasible": int(feas.shape[0]),
            "best": feas[objs].to_numpy(dtype=float).min(axis=0).tolist(),
            "n_front": int(len(front)) if front is not None else 1}
    if PROBLEMS[problem]["known_optimum"] is not None:
        info["known_optimum"] = PROBLEMS[problem]["known_optimum"]
        info["ceiling"] = float(ref[0] - PROBLEMS[problem]["known_optimum"])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"synthetic_reference_{problem}.json").write_text(
        json.dumps(info, indent=2))
    if front is not None:
        pd.DataFrame(front, columns=objs).to_csv(
            OUT / f"synthetic_front_{problem}.csv", index=False,
            float_format="%.8g")
    return info


def load_reference(problem: str) -> dict:
    return json.loads((OUT / f"synthetic_reference_{problem}.json").read_text())


# --- the free-hypervolume screen ------------------------------------------

def screen(problem: str, rng_seed: int = 12345) -> dict:
    """How much of the ceiling an uninformed 45-design batch collects.

    This is the diagnostic the physics study used to choose its objective
    pair.  Running it on problems whose geometry is known independently is
    the point: it should call the degenerate pair free and the genuine
    trade-off expensive, before any optimizer is run.
    """
    cloud = load_cloud(problem)
    info = load_reference(problem)
    ref = np.array(info["ref"], dtype=float)
    objs = list(PROBLEMS[problem]["objectives"])
    feas = cloud["feasible"].to_numpy(dtype=bool)
    obj = cloud[objs].to_numpy(dtype=float)
    masked = np.where(feas[:, None], obj, np.inf)
    rng = np.random.default_rng(rng_seed)
    hvs = np.empty(MC_DRAWS)
    for i in range(MC_DRAWS):
        idx = rng.choice(len(cloud), size=BUDGET, replace=False)
        hvs[i] = hypervolume(masked[idx], ref)
    frac = hvs / info["ceiling"]
    if len(objs) > 1:
        fo = obj[feas]
        front = fo[pareto_mask(fo)]
        corr = float(np.corrcoef(fo[:, 0], fo[:, 1])[0, 1])
        rng_o = fo.max(axis=0) - fo.min(axis=0)
        rng_o = np.where(rng_o > 0, rng_o, 1.0)
        fspan = ((front.max(axis=0) - front.min(axis=0)) / rng_o).tolist()
        # near-front share: fraction of the feasible cloud within 2 % of the
        # normalized front, the study's "is the front easy to land near" test
        zf = (front - fo.min(axis=0)) / rng_o
        z = (fo - fo.min(axis=0)) / rng_o
        sub = z[rng.choice(len(z), size=min(4000, len(z)), replace=False)]
        near_share = float((domination_depth(sub, zf) <= 0.02).mean())
    else:
        corr, fspan, near_share = float("nan"), [float("nan")], float("nan")
    out = {"problem": problem, "free_hv_mean": float(frac.mean()),
           "free_hv_sd": float(frac.std(ddof=1)),
           "obj_corr": corr, "front_span": fspan,
           "near_front_share": near_share,
           "n_front": info["n_front"]}
    return out


# --- the campaign ---------------------------------------------------------

def _finalize(problem: str, df: pd.DataFrame, ref: np.ndarray) -> pd.DataFrame:
    objs = list(PROBLEMS[problem]["objectives"])
    feas = feasible_mask(problem, df)
    df["feasible"] = feas
    obj = df[objs].to_numpy(dtype=float)
    masked = np.where(feas[:, None], obj, np.inf)
    df["hv"] = [hypervolume(masked[: i + 1], ref) for i in range(len(df))]
    for j, o in enumerate(objs):
        df[f"best_{o}"] = pd.Series(np.where(feas, obj[:, j],
                                             np.inf)).cummin()
    return df


def run_bo_seed(problem: str, seed: int, rounds: int = ROUNDS,
                batch: int = BATCH) -> pd.DataFrame:
    """The physics study's BO wiring, verbatim apart from the objectives."""
    from ax.modelbridge.factory import Models
    from ax.modelbridge.generation_strategy import (GenerationStep,
                                                    GenerationStrategy)
    from ax.service.ax_client import AxClient, ObjectiveProperties

    spec = PROBLEMS[problem]
    objs = list(spec["objectives"])
    info = load_reference(problem)
    ref = np.array(info["ref"], dtype=float)
    constraints = [f"{m} {op} {b}" for m, op, b in spec["constraints"]]

    gs = GenerationStrategy(steps=[
        GenerationStep(model=Models.SOBOL, num_trials=batch,
                       min_trials_observed=batch, max_parallelism=batch,
                       model_kwargs={"seed": seed}),
        GenerationStep(model=Models.BOTORCH_MODULAR, num_trials=-1,
                       max_parallelism=batch,
                       model_gen_kwargs={"model_gen_options": {
                           "optimizer_kwargs": {
                               "num_restarts": ACQ_RESTARTS,
                               "raw_samples": ACQ_RAW_SAMPLES}}}),
    ])
    ax_client = AxClient(generation_strategy=gs, random_seed=seed,
                         verbose_logging=False)
    ax_client.create_experiment(
        name=f"synthetic_{problem}_seed{seed}",
        parameters=ax_parameters(problem),
        objectives={o: ObjectiveProperties(minimize=True) for o in objs},
        outcome_constraints=constraints or None,
    )
    ax_keys = set(objs) | {m for m, _, _ in spec["constraints"]}
    names = param_names(problem)

    rows = []
    for rnd in range(rounds + 1):
        t0 = time.time()
        parameterizations, _ = ax_client.get_next_trials(batch)
        for idx, params in parameterizations.items():
            x = np.array([params[n] for n in names], dtype=float)
            res = evaluate(problem, x)
            rows.append({"strategy": "botorch", "seed": seed, "round": rnd,
                         "trial": idx,
                         **{n: float(params[n]) for n in names}, **res})
            ax_client.complete_trial(
                trial_index=idx,
                raw_data={k: v for k, v in res.items() if k in ax_keys})
        print(f"  {problem} seed {seed} round {rnd}: {batch} designs, "
              f"{time.time() - t0:.1f} s", flush=True)

    df = _finalize(problem, pd.DataFrame(rows), ref)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / f"synthetic_bo_{problem}_seed{seed}.csv", index=False,
              float_format="%.8g")
    return df


# --- the baselines --------------------------------------------------------

def _gen_stream(problem: str, strategy: str, seed: int):
    lo, hi = bounds_of(problem)
    d = len(lo)
    if strategy == "random":
        rng = np.random.default_rng(seed)
        while True:
            yield from lo + rng.random((256, d)) * (hi - lo)
    elif strategy == "sobol":
        eng = qmc.Sobol(d, scramble=True, seed=seed)
        while True:
            yield from lo + eng.random(256) * (hi - lo)
    elif strategy == "lhs":
        blk = 0
        while True:
            blk += 1
            eng = qmc.LatinHypercube(d, seed=seed + 7919 * blk)
            yield from lo + eng.random(BUDGET) * (hi - lo)
    else:
        raise ValueError(strategy)


def _scalarize(problem: str, res: dict, w: float, ref: np.ndarray,
               lo_obj: np.ndarray) -> float:
    objs = list(PROBLEMS[problem]["objectives"])
    if not feasible_row(problem, res):
        return 1e9
    z = np.array([res[o] for o in objs], dtype=float)
    span = np.where(ref - lo_obj > 0, ref - lo_obj, 1.0)
    wv = np.array([1.0]) if len(objs) == 1 else np.array([w, 1.0 - w])
    return float((((z - lo_obj) / span) * wv).sum())


def _run_sampler(problem: str, strategy: str, seed: int,
                 feasible_only: bool) -> list[dict]:
    names = param_names(problem)
    rows, rejected = [], 0
    for x in _gen_stream(problem, strategy, seed):
        if len(rows) >= BUDGET:
            break
        res = evaluate(problem, x)
        if feasible_only and not feasible_row(problem, res):
            rejected += 1
            continue
        rows.append({**dict(zip(names, x)), **res,
                     "rejected_before": rejected})
    return rows


def _run_compass(problem: str, seed: int, ref: np.ndarray,
                 lo_obj: np.ndarray, feasible_only: bool) -> list[dict]:
    """The era compass search: initial step 0.35 of range, halved on a
    failed sweep, three weightings, fresh axis permutation per sweep."""
    lo, hi = bounds_of(problem)
    d = len(lo)
    span = hi - lo
    names = param_names(problem)
    rng = np.random.default_rng(seed)
    rows, spent = [], 0
    objs = PROBLEMS[problem]["objectives"]
    weights = (0.5,) if len(objs) == 1 else (0.15, 0.5, 0.85)
    per_weight = BUDGET // len(weights)

    def _try(x):
        nonlocal spent
        res = evaluate(problem, x)
        if feasible_only and not feasible_row(problem, res):
            return None
        rows.append({**dict(zip(names, x)), **res})
        spent += 1
        return res

    for wi, w in enumerate(weights):
        left = per_weight if wi < len(weights) - 1 else BUDGET - spent
        if left <= 0:
            break
        while True:
            x = lo + rng.random(d) * span
            res = _try(x)
            if res is not None:
                break
        left -= 1
        best = _scalarize(problem, res, w, ref, lo_obj)
        step = 0.35 * np.ones(d)
        while left > 0:
            improved = False
            for axi in rng.permutation(d):
                for sign in (+1.0, -1.0):
                    if left <= 0:
                        break
                    cand = x.copy()
                    cand[axi] = float(np.clip(x[axi] + sign * step[axi]
                                              * span[axi], lo[axi], hi[axi]))
                    if np.isclose(cand[axi], x[axi]):
                        continue
                    res = _try(cand)
                    if res is None:
                        continue
                    left -= 1
                    val = _scalarize(problem, res, w, ref, lo_obj)
                    if val < best:
                        best, x, improved = val, cand, True
                        break
                if left <= 0:
                    break
            if not improved:
                step *= 0.5
                if step.max() < 1e-3:
                    step = 0.35 * np.ones(d)
    return rows


def run_baseline(problem: str, strategy: str, seed: int,
                 feasible_only: bool = True) -> pd.DataFrame:
    info = load_reference(problem)
    ref = np.array(info["ref"], dtype=float)
    lo_obj = np.array(info["best"], dtype=float)
    if strategy == "heuristic":
        rows = _run_compass(problem, seed, ref, lo_obj, feasible_only)
    else:
        rows = _run_sampler(problem, strategy, seed, feasible_only)
    df = pd.DataFrame(rows)
    df.insert(0, "trial", np.arange(len(df)))
    df.insert(0, "round", df["trial"] // BATCH)
    df.insert(0, "seed", seed)
    df.insert(0, "strategy", strategy)
    df = _finalize(problem, df, ref)
    mode = "feasible" if feasible_only else "plain"
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / f"synthetic_baseline_{strategy}_{mode}_{problem}"
                    f"_seed{seed}.csv", index=False, float_format="%.8g")
    return df


# --- workers --------------------------------------------------------------

def _bo_worker(job):
    problem, seed = job
    t0 = time.time()
    run_bo_seed(problem, seed)
    print(f"BO {problem} seed {seed} done in {time.time() - t0:.1f} s",
          flush=True)
    return f"{problem}_{seed}"


def _base_worker(job):
    problem, strategy, seed, feasible_only = job
    run_baseline(problem, strategy, seed, feasible_only)
    return f"{problem}_{strategy}_{seed}"


# --- comparison -----------------------------------------------------------

def _load(problem: str, pattern: str) -> list[pd.DataFrame]:
    return [pd.read_csv(p) for p in sorted(OUT.glob(pattern))]


def compare(problem: str, mode: str = "feasible") -> pd.DataFrame:
    info = load_reference(problem)
    ceiling = info["ceiling"]
    objs = list(PROBLEMS[problem]["objectives"])
    rows = []
    curves = {}
    bo = _load(problem, f"synthetic_bo_{problem}_seed*.csv")
    if not bo:
        raise SystemExit(f"no BO runs for {problem}")
    sets = {"botorch": bo}
    for strat in ("sobol", "lhs", "random", "heuristic"):
        runs = _load(problem,
                     f"synthetic_baseline_{strat}_{mode}_{problem}_seed*.csv")
        if runs:
            sets[strat] = runs
    bo_final = np.array([d["hv"].iloc[-1] for d in bo])
    for strat, runs in sets.items():
        final = np.array([d["hv"].iloc[-1] for d in runs])
        n = min(len(d) for d in runs)
        curves[strat] = np.vstack([d["hv"].to_numpy()[:n] for d in runs])
        row = {"problem": problem, "strategy": strat, "n_seeds": len(runs),
               "budget": int(n), "final_hv_mean": float(final.mean()),
               "final_hv_sd": float(final.std(ddof=1)),
               "hv_frac_of_ceiling": float(final.mean() / ceiling)}
        for j, o in enumerate(objs):
            b = np.array([d[f"best_{o}"].iloc[-1] for d in runs])
            row[f"best_{o}_mean"] = float(b.mean())
            row[f"best_{o}_sd"] = float(b.std(ddof=1))
        opt = PROBLEMS[problem]["known_optimum"]
        if opt is not None:
            reg = np.array([d[f"best_{objs[0]}"].iloc[-1] for d in runs]) - opt
            row["simple_regret_median"] = float(np.median(reg))
            row["simple_regret_gmean"] = float(
                np.exp(np.log(np.maximum(reg, 1e-12)).mean()))
            row["simple_regret_min"] = float(reg.min())
            row["simple_regret_max"] = float(reg.max())
            if strat != "botorch":
                bo_reg = np.array(
                    [d[f"best_{objs[0]}"].iloc[-1] for d in bo]) - opt
                row["mannwhitney_p_regret_vs_bo"] = float(
                    mannwhitneyu(bo_reg, reg, alternative="less",
                                 method="exact").pvalue)
        if strat != "botorch":
            # method="exact" on purpose.  SciPy's "auto" switches to the
            # asymptotic approximation above n = 8, which reports 9.13e-5
            # for complete separation at 10 vs 10 where the exact one-sided
            # value is 1 / C(20,10) = 5.41e-6.
            row["mannwhitney_p_vs_bo"] = float(
                mannwhitneyu(bo_final, final, alternative="greater",
                             method="exact").pvalue)
            # Seeds are matched across methods, so the paired test is the
            # more appropriate one; reported alongside rather than instead.
            d = bo_final - final
            row["wilcoxon_p_vs_bo"] = (
                float(wilcoxon(d, alternative="greater",
                               method="exact").pvalue)
                if np.any(d != 0) else float("nan"))
            row["paired_wins_vs_bo"] = int((d > 0).sum())
        rows.append(row)
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / f"synthetic_summary_{problem}.csv", index=False,
                   float_format="%.6g")
    _plot_problem(problem, curves, summary, ceiling, mode)
    return summary


def _plot_problem(problem, curves, summary, ceiling, mode):
    objs = list(PROBLEMS[problem]["objectives"])
    ncol = 2 if len(objs) == 1 else 3
    fig, axes = plt.subplots(1, ncol, figsize=(5.0 * ncol, 4.2))
    ax = axes[0]
    for strat, arr in curves.items():
        label, color = STRATEGY_STYLE[strat]
        x = np.arange(1, arr.shape[1] + 1)
        m, s = arr.mean(axis=0), arr.std(axis=0, ddof=1)
        ax.plot(x, m / ceiling, color=color, lw=2, label=label)
        ax.fill_between(x, (m - s) / ceiling, (m + s) / ceiling,
                        color=color, alpha=0.15, lw=0)
    ax.axhline(1.0, color="k", ls="--", lw=1, label="dense-sweep ceiling")
    ax.set_xlabel("evaluations")
    ax.set_ylabel("hypervolume / ceiling")
    ax.set_title(f"{problem}: running hypervolume\n(mean $\\pm$ 1$\\sigma$, "
                 f"{len(next(iter(curves.values())))} seeds)")
    ax.legend(fontsize=7.5, loc="lower right")
    ax.grid(alpha=0.3)

    ax = axes[1]
    order = list(curves.keys())
    vals = [summary.loc[summary.strategy == s, "final_hv_mean"].iloc[0]
            / ceiling for s in order]
    errs = [summary.loc[summary.strategy == s, "final_hv_sd"].iloc[0]
            / ceiling for s in order]
    colors = [STRATEGY_STYLE[s][1] for s in order]
    ax.bar(range(len(order)), vals, yerr=errs, capsize=4, color=colors,
           alpha=0.85)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([STRATEGY_STYLE[s][0] for s in order], rotation=25,
                       ha="right", fontsize=8)
    ax.axhline(1.0, color="k", ls="--", lw=1)
    ax.set_ylabel("final hypervolume / ceiling")
    ax.set_title("final fraction of ceiling")
    ax.grid(alpha=0.3, axis="y")
    for i, s in enumerate(order):
        p = summary.loc[summary.strategy == s, "mannwhitney_p_vs_bo"]
        if len(p) and np.isfinite(p.iloc[0]):
            ax.text(i, vals[i] + errs[i] + 0.012, f"p={p.iloc[0]:.1e}",
                    ha="center", fontsize=6.5)

    if len(objs) == 1 and PROBLEMS[problem]["known_optimum"] is not None:
        opt = PROBLEMS[problem]["known_optimum"]
        ax = axes[1]
        ax.clear()
        for strat in curves:
            runs = (_load(problem, f"synthetic_bo_{problem}_seed*.csv")
                    if strat == "botorch" else
                    _load(problem, f"synthetic_baseline_{strat}_{mode}_"
                                   f"{problem}_seed*.csv"))
            if not runs:
                continue
            n = min(len(d) for d in runs)
            arr = np.vstack([d[f"best_{objs[0]}"].to_numpy()[:n]
                             for d in runs]) - opt
            label, color = STRATEGY_STYLE[strat]
            x = np.arange(1, n + 1)
            med = np.median(arr, axis=0)
            ax.plot(x, med, color=color, lw=2, label=label)
            ax.fill_between(x, np.percentile(arr, 25, axis=0),
                            np.percentile(arr, 75, axis=0), color=color,
                            alpha=0.15, lw=0)
        ax.set_yscale("log")
        ax.set_xlabel("evaluations")
        ax.set_ylabel("simple regret, best $-$ 0.397887")
        ax.set_title("simple regret (median, IQR band)\n"
                     "the statistic the hypervolume fraction hides")
        ax.legend(fontsize=7.5)
        ax.grid(alpha=0.3, which="both")

    if len(objs) > 1:
        ax = axes[2]
        fpath = OUT / f"synthetic_front_{problem}.csv"
        if fpath.exists():
            front = pd.read_csv(fpath).to_numpy()
            front = front[np.argsort(front[:, 0])]
            ax.plot(front[:, 0], front[:, 1], "k-", lw=1.2,
                    label="reference front", zorder=1)
        for strat in ("random", "botorch"):
            runs = (_load(problem, f"synthetic_bo_{problem}_seed*.csv")
                    if strat == "botorch" else
                    _load(problem, f"synthetic_baseline_random_{mode}_"
                                   f"{problem}_seed*.csv"))
            if not runs:
                continue
            d = pd.concat(runs)
            d = d[d["feasible"].astype(bool)]
            label, color = STRATEGY_STYLE[strat]
            ax.scatter(d[objs[0]], d[objs[1]], s=7, alpha=0.35, color=color,
                       label=f"{label} evaluations", zorder=2)
        ax.set_xlabel(objs[0] + " (minimize)")
        ax.set_ylabel(objs[1] + " (minimize)")
        if problem.startswith("branin_currin"):
            ax.set_xscale("log")
        ax.set_title("objective space, all seeds pooled")
        ax.legend(fontsize=7.5)
        ax.grid(alpha=0.3)
    fig.suptitle(f"synthetic control: {problem}", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT / f"synthetic_{problem}.png", dpi=150)
    plt.close(fig)


def overview(problems: list[str], mode: str = "feasible") -> None:
    frames = []
    for p in problems:
        f = OUT / f"synthetic_summary_{p}.csv"
        if f.exists():
            frames.append(pd.read_csv(f))
    if not frames:
        return
    allsum = pd.concat(frames, ignore_index=True)
    allsum.to_csv(OUT / "synthetic_summary_all.csv", index=False,
                  float_format="%.6g")

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.6))
    ax = axes[0]
    width = 0.16
    order = ["botorch", "sobol", "lhs", "random", "heuristic"]
    xs = np.arange(len(problems))
    for k, strat in enumerate(order):
        vals, errs = [], []
        for p in problems:
            r = allsum[(allsum.problem == p) & (allsum.strategy == strat)]
            vals.append(float(r["hv_frac_of_ceiling"].iloc[0]) if len(r)
                        else np.nan)
            errs.append(float(r["final_hv_sd"].iloc[0]
                              / max(r["final_hv_mean"].iloc[0], 1e-12)
                              * r["hv_frac_of_ceiling"].iloc[0]) if len(r)
                        else np.nan)
        label, color = STRATEGY_STYLE[strat]
        ax.bar(xs + (k - 2) * width, vals, width, yerr=errs, capsize=2.5,
               color=color, alpha=0.85, label=label)
    ax.set_xticks(xs)
    ax.set_xticklabels(problems, rotation=15, ha="right", fontsize=8.5)
    ax.axhline(1.0, color="k", ls="--", lw=1)
    ax.set_ylabel("final hypervolume / ceiling")
    ax.set_title("BO against uninformed baselines, identical harness\n"
                 "45 evaluations, 10 seeds each")
    ax.legend(fontsize=7.5, ncol=2)
    ax.grid(alpha=0.3, axis="y")

    ax = axes[1]
    scr = OUT / "synthetic_screen.csv"
    if scr.exists():
        s = pd.read_csv(scr).set_index("problem")
        gaps, frees, labels = [], [], []
        for p in problems:
            if p not in s.index:
                continue
            bo = allsum[(allsum.problem == p) & (allsum.strategy == "botorch")]
            base = allsum[(allsum.problem == p)
                          & (allsum.strategy != "botorch")]
            if not len(bo) or not len(base):
                continue
            gaps.append(float(bo["hv_frac_of_ceiling"].iloc[0]
                              - base["hv_frac_of_ceiling"].max()))
            frees.append(float(s.loc[p, "free_hv_mean"]))
            labels.append(p)
        ax.scatter(np.array(frees) * 100, np.array(gaps) * 100, s=60,
                   color="tab:blue", zorder=3, label="synthetic control")
        for f, g, lab in zip(frees, gaps, labels):
            ax.annotate(lab, (f * 100, g * 100), fontsize=7.5,
                        xytext=(4, 4), textcoords="offset points")
        pf = [v[0] for v in PHYSICS_ANCHORS.values()]
        pg = [v[1] - v[2] for v in PHYSICS_ANCHORS.values()]
        ax.scatter(np.array(pf) * 100, np.array(pg) * 100, s=90,
                   marker="s", color="tab:red", zorder=4,
                   label="physics study")
        for f, g, lab in zip(pf, pg, PHYSICS_ANCHORS):
            ax.annotate(lab, (f * 100, g * 100), fontsize=7.5, color="tab:red",
                        xytext=(4, -10), textcoords="offset points")
        ax.axhline(0.0, color="k", lw=1)
        ax.set_xlabel("free hypervolume of an uninformed 45-design batch (%)")
        ax.set_ylabel("BO advantage over the best baseline\n"
                      "(percentage points of ceiling)")
        ax.set_title("free hypervolume bounds the DOE level but does not\n"
                     "fix the gap: two points sit at 84.6 % with gaps of\n"
                     "2.8 and 11.7 percentage points")
        ax.legend(fontsize=7.5, loc="upper right")
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "synthetic_overview.png", dpi=150)
    plt.close(fig)


def audit(problems: list[str], mode: str = "feasible") -> pd.DataFrame:
    """Independent checks of the scoring, on both this control and the
    physics study's committed CSVs.

    Three things the reported contrast depends on and that a reader should
    not have to take on trust: that our hypervolume sweep agrees with a
    standard implementation, that every method really spent the same
    budget, and that no two repeats shared an initial batch.
    """
    import torch
    from botorch.utils.multi_objective.hypervolume import Hypervolume

    def bt_hv(points: np.ndarray, ref: np.ndarray) -> float:
        pts = np.asarray(points, dtype=float)
        pts = pts[np.isfinite(pts).all(axis=1)]
        if pts.size == 0:
            return 0.0
        Y = torch.tensor(-pts, dtype=torch.double)
        r = torch.tensor(-np.asarray(ref, dtype=float), dtype=torch.double)
        return float(Hypervolume(ref_point=r).compute(Y))

    rows = []
    for problem in problems:
        objs = list(PROBLEMS[problem]["objectives"])
        if len(objs) < 2:
            continue
        ref = np.array(load_reference(problem)["ref"], dtype=float)
        worst, n, budgets = 0.0, 0, set()
        for pat in (f"synthetic_bo_{problem}_seed*.csv",
                    f"synthetic_baseline_*_{mode}_{problem}_seed*.csv"):
            for f in sorted(OUT.glob(pat)):
                d = pd.read_csv(f)
                budgets.add(len(d))
                feas = d["feasible"].to_numpy(dtype=bool)
                masked = np.where(feas[:, None],
                                  d[objs].to_numpy(dtype=float), np.inf)
                ours, theirs = float(d["hv"].iloc[-1]), bt_hv(masked, ref)
                worst = max(worst, abs(ours - theirs) / max(theirs, 1e-12))
                n += 1
        r0, dup = {}, []
        names = param_names(problem)
        for f in sorted(OUT.glob(f"synthetic_bo_{problem}_seed*.csv")):
            d = pd.read_csv(f)
            r0[f.stem] = d[d["round"] == 0][names].to_numpy().round(9)
        keys = sorted(r0)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                if np.array_equal(r0[a], r0[b]):
                    dup.append((a, b))
        rows.append({"problem": problem, "runs_checked": n,
                     "worst_rel_hv_disagreement_vs_botorch": worst,
                     "budgets_seen": sorted(budgets),
                     "identical_round0_pairs": len(dup)})
    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "synthetic_audit.csv", index=False)
    return df


def audit_physics() -> pd.DataFrame:
    """The same three checks against the physics study's committed CSVs.

    The point of the synthetic control is only as strong as the claim that
    the two studies share a scoring path, so the physics artifacts get the
    identical independent hypervolume check rather than an argument by
    analogy.
    """
    import torch
    from botorch.utils.multi_objective.hypervolume import Hypervolume

    bc = HERE / "outputs" / "bo_contrast"
    refs_path = bc / "contrast_refs.csv"
    if not refs_path.exists():
        print("  no bo_contrast artifacts on disk; skipping physics audit")
        return pd.DataFrame()
    refs = pd.read_csv(refs_path).set_index("pair")
    rows = []
    # Only the envelope pair is audited here.  The strain-era per-seed CSVs
    # live under a different prefix and carry a running hypervolume computed
    # against the era's own reference point, so cross-checking them against
    # this study's rescore reference would disagree by construction rather
    # than by defect.
    for pair, objs in (("envelope", ["t180", "envelope_cm3"]),):
        if pair not in refs.index:
            continue
        ref = refs.loc[pair, ["ref_obj1", "ref_obj2"]].to_numpy(dtype=float)
        r = torch.tensor(-ref, dtype=torch.double)
        worst, n, budgets = 0.0, 0, set()
        files = (sorted(bc.glob(f"contrast_bo_{pair}_seed*.csv"))
                 + sorted(bc.glob(f"contrast_baseline_*_printable_{pair}"
                                  f"_seed*.csv")))
        for f in files:
            d = pd.read_csv(f)
            if not set(objs).issubset(d.columns) or "hv" not in d.columns:
                continue
            budgets.add(len(d))
            col = "pair_feasible" if "pair_feasible" in d else "feasible"
            feas = d[col].to_numpy(dtype=bool)
            masked = np.where(feas[:, None], d[objs].to_numpy(dtype=float),
                              np.inf)
            pts = masked[np.isfinite(masked).all(axis=1)]
            theirs = (0.0 if pts.size == 0 else
                      float(Hypervolume(ref_point=r).compute(
                          torch.tensor(-pts, dtype=torch.double))))
            worst = max(worst,
                        abs(float(d["hv"].iloc[-1]) - theirs)
                        / max(theirs, 1e-12))
            n += 1
        names = ["H_over_R", "H_over_strut_d", "cable_over_strut_d",
                 "twist_deg"]
        r0, dup = {}, 0
        for f in sorted(bc.glob(f"contrast_bo_{pair}_seed*.csv")):
            d = pd.read_csv(f)
            if not set(names).issubset(d.columns):
                continue
            r0[f.stem] = d[d["round"] == 0][names].to_numpy().round(9)
        keys = sorted(r0)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                dup += int(np.array_equal(r0[a], r0[b]))
        # Edison 53cfc937 finding 1: the reported "ceiling" is the dense
        # cloud plus a Nelder-Mead polish, and the campaign found feasible
        # points beyond it, so it is a best-known reference hypervolume
        # rather than a ceiling.  Recomputed here from the union of the
        # cloud, the polished front, and every feasible evaluation of every
        # method, which is the denominator a benchmark should report.
        polished = float(refs.loc[pair, "ceiling_hv_polished"])
        parts, contrib = [], {}
        fr = pd.read_csv(bc / f"contrast_front_{pair}.csv")
        fcols = [c for c in fr.columns if c in objs] or list(fr.columns[:2])
        parts.append(fr[fcols].to_numpy(dtype=float))
        cl = pd.read_csv(bc / "contrast_cloud_ratios.csv.gz")
        parts.append(cl[cl["feasible"].astype(bool)][objs].to_numpy(float))
        base = list(parts)
        for tag, pat in (("bo", f"contrast_bo_{pair}_seed*.csv"),
                         ("baselines",
                          f"contrast_baseline_*_printable_{pair}_seed*.csv")):
            got = []
            for f in sorted(bc.glob(pat)):
                d = pd.read_csv(f)
                col = "pair_feasible" if "pair_feasible" in d else "feasible"
                got.append(d.loc[d[col].astype(bool), objs].to_numpy(float))
            if got:
                contrib[tag] = (hypervolume(np.vstack(base + got), ref)
                                - hypervolume(np.vstack(base), ref))
                parts.extend(got)
        best_known = hypervolume(np.vstack(parts), ref)
        rows.append({"pair": pair, "runs_checked": n,
                     "worst_rel_hv_disagreement_vs_botorch": worst,
                     "budgets_seen": sorted(budgets),
                     "bo_seeds": len(keys), "identical_round0_pairs": dup,
                     "reported_polished_ceiling": polished,
                     "best_known_reference_hv": best_known,
                     "best_known_over_polished": best_known / polished,
                     "hv_added_by_bo_points": contrib.get("bo", float("nan")),
                     "hv_added_by_baseline_points":
                         contrib.get("baselines", float("nan"))})
    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "synthetic_audit_physics.csv", index=False)
    return df


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--problems", nargs="+", default=list(PROBLEMS))
    ap.add_argument("--seeds", type=int, nargs="+", default=SEEDS)
    ap.add_argument("--cloud", action="store_true")
    ap.add_argument("--cloud-n", type=int, default=CLOUD_N)
    ap.add_argument("--screen", action="store_true")
    ap.add_argument("--campaign", action="store_true")
    ap.add_argument("--baselines", action="store_true")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--audit", action="store_true",
                    help="cross-check the hypervolume, budget parity and "
                         "round-0 distinctness")
    ap.add_argument("--mode", default="feasible",
                    choices=["feasible", "plain"])
    ap.add_argument("--jobs", type=int, default=1)
    args = ap.parse_args(argv)

    OUT.mkdir(parents=True, exist_ok=True)

    if args.cloud:
        for p in args.problems:
            t0 = time.time()
            build_cloud(p, args.cloud_n)
            info = build_reference(p)
            print(f"{p}: cloud {info['n_cloud']} "
                  f"({info['n_feasible']} feasible), ref "
                  f"{np.round(info['ref'], 4).tolist()}, ceiling "
                  f"{info['ceiling']:.6g}, front {info['n_front']} pts, "
                  f"{time.time() - t0:.1f} s", flush=True)

    if args.screen:
        rows = [screen(p) for p in args.problems]
        df = pd.DataFrame(rows)
        df.to_csv(OUT / "synthetic_screen.csv", index=False,
                  float_format="%.6g")
        print(df.to_string(index=False))

    if args.campaign:
        jobs = [(p, s) for p in args.problems for s in args.seeds]
        if args.jobs > 1:
            import multiprocessing as mp
            with mp.get_context("spawn").Pool(args.jobs) as pool:
                for tag in pool.imap_unordered(_bo_worker, jobs):
                    print(f"  finished {tag}", flush=True)
        else:
            for j in jobs:
                _bo_worker(j)

    if args.baselines:
        feasible_only = args.mode == "feasible"
        jobs = [(p, st, s, feasible_only) for p in args.problems
                for st in ("random", "sobol", "lhs", "heuristic")
                for s in args.seeds]
        if args.jobs > 1:
            import multiprocessing as mp
            with mp.get_context("spawn").Pool(args.jobs) as pool:
                list(pool.imap_unordered(_base_worker, jobs))
        else:
            for j in jobs:
                _base_worker(j)
        print(f"  {len(jobs)} baseline runs done")

    if args.compare:
        done = []
        for p in args.problems:
            if not list(OUT.glob(f"synthetic_bo_{p}_seed*.csv")):
                continue
            s = compare(p, args.mode)
            done.append(p)
            print(f"\n=== {p} ===")
            cols = ["strategy", "n_seeds", "final_hv_mean", "final_hv_sd",
                    "hv_frac_of_ceiling", "mannwhitney_p_vs_bo"]
            cols = [c for c in cols if c in s.columns]
            print(s[cols].to_string(index=False))
        overview(done, args.mode)

    if args.audit:
        print(audit(args.problems, args.mode).to_string(index=False))
        ph = audit_physics()
        if len(ph):
            print()
            print(ph.to_string(index=False))


if __name__ == "__main__":
    main()
