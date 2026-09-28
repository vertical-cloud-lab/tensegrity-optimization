"""Objective sets that resolve the BO vs uninformed-DOE contrast.

On the corrected drop-tower physics, the (t180, peak_tendon_strain) pair is
anti-correlated across the constant-mass shape-ratio manifold, so most of the
printable design cloud already lies near its Pareto front.  At a 45-design
budget any space-filling design (random, Sobol, Latin hypercube) then collects
almost the whole hypervolume for free, and the earlier full-effort study found
constrained qNEHVI statistically indistinguishable from the samplers on that
pair.  That is a property of the objective geometry, not of the optimizer: the
same protocol on the earlier concordant pair separated the BO completely from
every baseline (97 % of a dense-sweep ceiling against 66 % for Sobol).

This study makes that dependence explicit and then exploits it.

1.  ``--cloud N``: one dense scrambled-Sobol sweep of the manifold.  A single
    corrected-physics simulation returns every candidate observable, so one
    cloud prices every candidate objective pair at once.
2.  ``--screen``: for each candidate pair, Monte-Carlo resample 45-design
    uninformed batches from the cloud and measure how much of that pair's
    hypervolume ceiling they collect for free, plus front-geometry
    diagnostics (objective correlation, near-front band share, front
    localization in design space).  The current strain pair and the dead
    rebound pair are kept as controls.  The pair for the campaign is chosen
    by this screen: a genuine trade-off (the front spans a meaningful range
    of both objectives) whose free hypervolume is lowest, i.e. whose front a
    model has to *find*.
3.  ``--reference PAIR``: Nelder-Mead polish of the cloud's best weighted
    points, so the reported ceiling is not limited by cloud spacing.
4.  ``--campaign PAIR`` / ``--baselines PAIR``: the established repeat
    protocol on the chosen pair.  Ten independent seeds, each drawing its
    own scrambled Sobol round 0, 45 designs (9 + 4 x 9), constrained qNEHVI
    against random / Sobol / Latin hypercube / compass search at the same
    budget and seeds.  Baselines run in two modes: ``plain`` (the era
    protocol: infeasible draws are evaluated and excluded from fronts) and
    ``printable`` (a stronger DOE: draws are rejection-sampled through the
    simulation-free geometric printability check, so no sampler wastes
    budget on unprintable designs).
5.  ``--compare PAIR``: comparison figures, the summary table with
    Mann-Whitney tests, and a cross-pair contrast table that re-scores the
    committed strain-era runs under this study's reference convention so
    the old no-separation result and the new pair sit in one table.

Reference-point convention, shared by every method and seed: 1.05 times the
componentwise worst value over the feasible cloud.  The era convention (worst
over the nine printed articles) is not usable here because objectives such as
the envelope extend well past the printed nine, and a reference point inside
the feasible range would silently delete the far end of the front from every
hypervolume.

Run::

    python bo_contrast_study.py --cloud 8192 --jobs 4
    python bo_contrast_study.py --screen
    python bo_contrast_study.py --reference envelope --jobs 4
    python bo_contrast_study.py --campaign envelope --seeds 0 1 2 3 4 5 6 7 8 9 --jobs 3
    python bo_contrast_study.py --baselines envelope --jobs 4
    python bo_contrast_study.py --compare envelope
"""
from __future__ import annotations

import argparse
import math
import os
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import pandas as pd
from scipy.stats import qmc, spearmanr

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import drop_tower_sim  # noqa: E402
import pr102_sim_campaign as campaign  # noqa: E402
from pr102_sim_campaign import (  # noqa: E402
    CABLE_PRINT_FLOOR_MM, ENVELOPE_MAX_CM3, MASS_TARGET_G, RATIO_PARAMS,
    RATIO_PARAMETERS, hypervolume_2d, ratios_to_base,
)
from pr102_baselines import STRATEGY_STYLE, pareto_mask  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "bo_contrast"

BOUNDS_LO = np.array([p["bounds"][0] for p in RATIO_PARAMETERS], dtype=float)
BOUNDS_HI = np.array([p["bounds"][1] for p in RATIO_PARAMETERS], dtype=float)

CLOUD_SEED = 20260825          # distinct from every campaign/baseline seed
BUDGET = 45                    # 9-design round 0 + 4 model rounds of 9
BATCH = 9
ROUNDS = 4
SEEDS = list(range(10))
MC_DRAWS = 2000
NEAR_FRONT_EPS = 0.02          # of the normalized objective range

# Candidate objective pairs.  Both objectives minimized in every pair, and
# every observable comes out of the same simulation, so the one cloud prices
# them all.  ``constraints`` lists outcome constraints beyond the two
# printability ones (cable print floor, envelope cap) that every pair keeps.
PAIRS: dict[str, dict] = {
    "strain": {
        "objectives": ("t180", "peak_tendon_strain"), "constraints": [],
        "why": "the current campaign pair; anti-correlated, so most of the "
               "cloud is near-front and DOE collects the hypervolume for "
               "free.  Kept as the no-contrast control."},
    "rebound": {
        "objectives": ("t180", "e_rebound"), "constraints": [],
        "why": "the earlier PR #102-faithful pair; the rebound axis is "
               "mat-owned and spans under 1 %.  Kept as the dead-axis "
               "control."},
    "envelope": {
        "objectives": ("t180", "envelope_cm3"), "constraints": [],
        "why": "transmissibility against stowed bulk at constant printed "
               "mass: the lander packaging question.  Best t180 wants the "
               "widest article the build volume allows, minimum envelope "
               "wants the smallest, and being non-dominated at a given size "
               "requires the best shape for that size."},
    "stroke": {
        "objectives": ("t180", "stroke_mm"), "constraints": [],
        "why": "transmissibility against crush clearance consumed: how much "
               "travel the article uses to deliver its isolation."},
    "strain_envelope": {
        "objectives": ("peak_tendon_strain", "envelope_cm3"), "constraints": [],
        "why": "tendon survival against stowed bulk; neither objective is "
               "t180, so this probes whether the contrast depends on the "
               "transmissibility axis."},
    "envelope_straincap": {
        "objectives": ("t180", "envelope_cm3"),
        "constraints": [("peak_tendon_strain", "<=", 0.12)],
        "why": "the envelope pair with a TPU fatigue allowable as an "
               "outcome constraint.  The cap bites exactly where t180 is "
               "best (strain and t180 anti-correlate), so the constrained "
               "optimum must be learned, not stumbled on."},
}

OBJ_LABEL = {
    "t180": "t180 (CFC-180 transmissibility, minimize)",
    "peak_tendon_strain": "peak tendon strain (minimize)",
    "e_rebound": "e_rebound (minimize)",
    "envelope_cm3": "envelope volume (cm^3, minimize)",
    "stroke_mm": "stroke (mm, minimize)",
}


def _as_params(x: np.ndarray) -> dict:
    return {n: float(v) for n, v in zip(RATIO_PARAMS, x)}


def _scale_unit(unit: np.ndarray) -> np.ndarray:
    return BOUNDS_LO + unit * (BOUNDS_HI - BOUNDS_LO)


def evaluate(params: dict) -> dict:
    """One corrected-physics evaluation on the constant-mass manifold."""
    res = campaign.evaluate(params, space="ratios")
    res["ok"] = bool(np.isfinite(res["t180"]))
    return res


_MASS_MODEL = None


def geom_printable(params: dict) -> bool:
    """Printability from geometry alone: no simulation is spent.

    The constant-mass scale solve and both printability bounds (cable print
    floor, envelope cap) are closed-form geometry, so any sampler may check
    them before committing an evaluation, exactly as an engineer laying out
    a print plate would.
    """
    global _MASS_MODEL
    if _MASS_MODEL is None:
        _MASS_MODEL = drop_tower_sim.mass_model()
    proj = _MASS_MODEL.project(ratios_to_base(params), MASS_TARGET_G)
    if not math.isfinite(proj.get("scale", float("nan"))):
        return False
    return bool(proj["envelope_ok"] and proj["cable_bridge_ok"])


def pair_feasible(df: pd.DataFrame, pair: str) -> np.ndarray:
    """Printability plus the pair's extra outcome constraints."""
    feas = df["feasible"].to_numpy(dtype=bool).copy()
    for metric, op, bound in PAIRS[pair]["constraints"]:
        v = df[metric].to_numpy(dtype=float)
        feas &= (v <= bound) if op == "<=" else (v >= bound)
    return feas


# --- the cloud ------------------------------------------------------------

def _cloud_chunk(job: tuple) -> pd.DataFrame:
    lo, hi, pts = job
    rows = []
    for i in range(lo, hi):
        p = _as_params(pts[i])
        rows.append({"i": i, **p, **evaluate(p)})
    return pd.DataFrame(rows)


def build_cloud(n: int, jobs: int, outdir: Path) -> pd.DataFrame:
    pts = _scale_unit(qmc.Sobol(len(RATIO_PARAMS), scramble=True,
                                seed=CLOUD_SEED).random(n))
    print(f"cloud: {n} designs over {jobs} process(es)", flush=True)
    t0 = time.time()
    edges = np.linspace(0, n, jobs + 1).astype(int)
    chunks = [(int(a), int(b), pts) for a, b in zip(edges[:-1], edges[1:])]
    if jobs > 1:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(jobs) as pool:
            frames = pool.map(_cloud_chunk, chunks)
    else:
        frames = [_cloud_chunk(c) for c in chunks]
    cloud = pd.concat(frames).sort_values("i").reset_index(drop=True)
    dt = time.time() - t0
    print(f"  {len(cloud)} designs in {dt:.1f} s ({1e3 * dt / len(cloud):.1f} "
          f"ms each), feasible {int(cloud['feasible'].sum())}", flush=True)
    outdir.mkdir(parents=True, exist_ok=True)
    cloud.to_csv(outdir / "contrast_cloud_ratios.csv.gz", index=False,
                 float_format="%.6g", compression="gzip")
    return cloud


def load_cloud(outdir: Path) -> pd.DataFrame:
    return pd.read_csv(outdir / "contrast_cloud_ratios.csv.gz")


def load_refs(outdir: Path) -> pd.DataFrame:
    return pd.read_csv(outdir / "contrast_refs.csv").set_index("pair")


def ref_for(pair: str, outdir: Path) -> np.ndarray:
    r = load_refs(outdir).loc[pair]
    return np.array([r["ref_obj1"], r["ref_obj2"]], dtype=float)


# --- the screen -----------------------------------------------------------

def _domination_depth(z: np.ndarray, zf: np.ndarray) -> np.ndarray:
    """One-sided Chebyshev depth of each point behind the front.

    ``z`` and ``zf`` are range-normalized minimization objectives.  Depth 0
    means on the front; depth d means some front point beats the point by d
    in its worst objective.  The share of the cloud with small depth is the
    band-vs-needle diagnostic: on a band geometry most of the cloud has
    depth near zero and DOE cannot lose.
    """
    out = np.empty(len(z))
    for a in range(0, len(z), 2048):               # chunked: (n, front, 2)
        diff = z[a:a + 2048, None, :] - zf[None, :, :]
        out[a:a + 2048] = np.maximum(diff.max(axis=2), 0.0).min(axis=1)
    return out


def mc_free_hv(obj: np.ndarray, geom_feas: np.ndarray, feas: np.ndarray,
               ref: np.ndarray, ceiling: float, budget: int, draws: int,
               seed: int, printable_only: bool) -> np.ndarray:
    """Fraction of the ceiling a random uninformed budget collects.

    ``printable_only`` draws from the geometry-printable rows (the check a
    sampler gets for free); constraints that need the simulation (the
    strain cap) still cost the draw and are masked out of the hypervolume,
    exactly as they would be in a real DOE batch.
    """
    rng = np.random.default_rng(seed)
    n = len(obj)
    out = np.empty(draws)
    pool = np.flatnonzero(geom_feas)
    replace = len(pool) < budget or n < budget   # only tiny smoke clouds
    for b in range(draws):
        idx = (rng.choice(pool, size=budget, replace=replace)
               if printable_only else
               rng.choice(n, size=budget, replace=replace))
        pts = np.where(feas[idx, None], obj[idx], np.inf)
        out[b] = hypervolume_2d(pts, ref) / ceiling
    return out


def screen(outdir: Path) -> None:
    cloud = load_cloud(outdir)
    ok = cloud[cloud["ok"].astype(bool)].reset_index(drop=True)
    rows, refs, mc_frames = [], [], {}
    for pair, spec in PAIRS.items():
        o1, o2 = spec["objectives"]
        feas = pair_feasible(ok, pair)
        obj = ok[[o1, o2]].to_numpy(dtype=float)
        fobj = obj[feas]
        ref = 1.05 * fobj.max(axis=0)
        front_mask = pareto_mask(fobj)
        front = fobj[front_mask]
        ceiling = hypervolume_2d(fobj, ref)

        lo = fobj.min(axis=0)
        rng_o = ref - lo
        z = (fobj - lo) / rng_o
        depth = _domination_depth(z, z[front_mask])
        band_share = float((depth < NEAR_FRONT_EPS).mean())

        geom = ok["feasible"].to_numpy(dtype=bool)
        mc_plain = mc_free_hv(obj, geom, feas, ref, ceiling, BUDGET,
                              MC_DRAWS, 1000, printable_only=False)
        mc_print = mc_free_hv(obj, geom, feas, ref, ceiling, BUDGET,
                              MC_DRAWS, 2000, printable_only=True)
        mc_frames[pair] = mc_print

        fidx = np.flatnonzero(feas)[front_mask]
        fp = ok.iloc[fidx][RATIO_PARAMS].to_numpy(dtype=float)
        loc = float(np.mean((np.percentile(fp, 75, axis=0)
                             - np.percentile(fp, 25, axis=0))
                            / (BOUNDS_HI - BOUNDS_LO)))

        rho = spearmanr(fobj[:, 0], fobj[:, 1]).statistic
        rows.append({
            "pair": pair, "obj1": o1, "obj2": o2,
            "n_feasible": int(feas.sum()), "n_front": int(front_mask.sum()),
            "rho_obj1_obj2": rho,
            "span_obj1": float(fobj[:, 0].max() - fobj[:, 0].min()),
            "span_obj2": float(fobj[:, 1].max() - fobj[:, 1].min()),
            "front_span_obj1": float(front[:, 0].max() - front[:, 0].min()),
            "front_span_obj2": float(front[:, 1].max() - front[:, 1].min()),
            "band_share_2pct": band_share,
            "front_param_iqr": loc,
            "ceiling_hv_cloud": ceiling,
            "free_hv_plain_mean": float(mc_plain.mean()),
            "free_hv_plain_sd": float(mc_plain.std()),
            "free_hv_printable_mean": float(mc_print.mean()),
            "free_hv_printable_sd": float(mc_print.std()),
            "free_hv_printable_p95": float(np.percentile(mc_print, 95)),
        })
        refs.append({"pair": pair, "obj1": o1, "obj2": o2,
                     "ref_obj1": ref[0], "ref_obj2": ref[1],
                     "ceiling_hv_cloud": ceiling})
        print(f"{pair:>20}: rho {rho:+.2f}, band {100 * band_share:5.1f} %, "
              f"free HV (printable 45) {100 * mc_print.mean():5.1f} % "
              f"+/- {100 * mc_print.std():.1f}", flush=True)

    pd.DataFrame(rows).to_csv(outdir / "contrast_screen.csv", index=False,
                              float_format="%.6g")
    pd.DataFrame(refs).to_csv(outdir / "contrast_refs.csv", index=False,
                              float_format="%.6g")
    plot_screen(ok, mc_frames, outdir)
    print(f"wrote {outdir}/contrast_screen.csv, contrast_refs.csv")


def plot_screen(ok: pd.DataFrame, mc_frames: dict, outdir: Path) -> None:
    pairs = list(PAIRS)
    fig, axes = plt.subplots(2, len(pairs), figsize=(4.1 * len(pairs), 7.6),
                             dpi=200)
    for j, pair in enumerate(pairs):
        o1, o2 = PAIRS[pair]["objectives"]
        feas = pair_feasible(ok, pair)
        obj = ok[[o1, o2]].to_numpy(dtype=float)
        ax = axes[0, j]
        ax.scatter(obj[~feas, 0], obj[~feas, 1], s=2, alpha=0.10,
                   color="#e5b8b3", rasterized=True)
        ax.scatter(obj[feas, 0], obj[feas, 1], s=2, alpha=0.18,
                   color="#9aa0a6", rasterized=True)
        fobj = obj[feas]
        fm = pareto_mask(fobj)
        fr = fobj[fm][np.argsort(fobj[fm][:, 0])]
        ax.plot(fr[:, 0], fr[:, 1], color="#c0392b", lw=1.8, zorder=5)
        ax.set_xlabel(o1, fontsize=8)
        ax.set_ylabel(o2, fontsize=8)
        ax.set_title(pair, fontsize=10)
        ax.grid(alpha=0.25, lw=0.5)

        ax = axes[1, j]
        mc = mc_frames[pair]
        ax.hist(100 * mc, bins=40, color="#2a78d6", alpha=0.85)
        ax.axvline(100 * mc.mean(), color="#111111", lw=1.2)
        ax.set_xlabel("free HV, printable 45-design DOE\n(% of cloud ceiling)",
                      fontsize=8)
        ax.set_ylabel("MC draws", fontsize=8)
        ax.set_title(f"mean {100 * mc.mean():.1f} %", fontsize=9)
        ax.grid(alpha=0.25, lw=0.5)
    fig.suptitle("Candidate objective pairs on the constant-mass manifold: "
                 "cloud, front, and what an uninformed 45-design batch "
                 "collects for free", fontsize=11)
    fig.tight_layout()
    fig.savefig(outdir / "bo_contrast_screen.png", bbox_inches="tight")
    plt.close(fig)


# --- the reference polish -------------------------------------------------

def _scalarize_row(res: dict, pair: str, w: float, ref: np.ndarray) -> float:
    o1, o2 = PAIRS[pair]["objectives"]
    feas = bool(res.get("feasible", True))
    for metric, op, bound in PAIRS[pair]["constraints"]:
        v = float(res[metric])
        feas &= (v <= bound) if op == "<=" else (v >= bound)
    if not feas or not np.isfinite(res[o1]):
        return 10.0
    return w * res[o1] / ref[0] + (1.0 - w) * res[o2] / ref[1]


def _polish_chunk(job: tuple) -> pd.DataFrame:
    pair, weights, x0s, ref, maxfev = job
    from scipy.optimize import minimize
    rows = []
    for w, x0 in zip(weights, x0s):
        trace = []

        def f(x, _w=w, _trace=trace):
            p = _as_params(np.clip(x, BOUNDS_LO, BOUNDS_HI))
            r = evaluate(p)
            _trace.append({**p, **r, "weight": _w})
            return _scalarize_row(r, pair, _w, ref)

        minimize(f, x0, method="Nelder-Mead",
                 options={"maxfev": maxfev, "xatol": 1e-3, "fatol": 1e-9})
        rows.extend(trace)
    return pd.DataFrame(rows)


def run_reference(pair: str, jobs: int, outdir: Path,
                  n_weights: int = 15, maxfev: int = 150) -> None:
    cloud = load_cloud(outdir)
    ok = cloud[cloud["ok"].astype(bool)].reset_index(drop=True)
    o1, o2 = PAIRS[pair]["objectives"]
    ref = ref_for(pair, outdir)
    feas = pair_feasible(ok, pair)
    fe = ok[feas]
    weights = np.linspace(0.0, 1.0, n_weights)
    x0s = []
    for w in weights:
        s = w * fe[o1].to_numpy() / ref[0] + (1 - w) * fe[o2].to_numpy() / ref[1]
        x0s.append(fe.iloc[int(np.argmin(s))][RATIO_PARAMS]
                   .to_numpy(dtype=float))
    print(f"reference polish for {pair}: {n_weights} weightings x "
          f"maxfev {maxfev}", flush=True)
    t0 = time.time()
    edges = np.linspace(0, n_weights, jobs + 1).astype(int)
    chunks = [(pair, weights[a:b], x0s[a:b], ref, maxfev)
              for a, b in zip(edges[:-1], edges[1:]) if b > a]
    if jobs > 1:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(len(chunks)) as pool:
            frames = pool.map(_polish_chunk, chunks)
    else:
        frames = [_polish_chunk(c) for c in chunks]
    polish = pd.concat(frames, ignore_index=True)
    print(f"  {len(polish)} polish evaluations in {time.time() - t0:.1f} s",
          flush=True)
    polish.to_csv(outdir / f"contrast_polish_{pair}.csv.gz", index=False,
                  float_format="%.6g", compression="gzip")

    pfeas = pair_feasible(polish, pair) & polish["ok"].astype(bool).to_numpy()
    allobj = np.vstack([ok[[o1, o2]].to_numpy(dtype=float)[feas],
                        polish[[o1, o2]].to_numpy(dtype=float)[pfeas]])
    ceiling = hypervolume_2d(allobj, ref)
    fm = pareto_mask(allobj)
    front = pd.DataFrame(allobj[fm], columns=[o1, o2]).sort_values(o1)
    front.to_csv(outdir / f"contrast_front_{pair}.csv", index=False,
                 float_format="%.6g")
    refs = load_refs(outdir).reset_index()
    refs.loc[refs["pair"] == pair, "ceiling_hv_polished"] = ceiling
    refs.to_csv(outdir / "contrast_refs.csv", index=False, float_format="%.6g")
    cloud_ceiling = float(refs.loc[refs["pair"] == pair,
                                   "ceiling_hv_cloud"].iloc[0])
    print(f"polished ceiling {ceiling:.6g} (cloud alone {cloud_ceiling:.6g}, "
          f"+{100 * (ceiling / cloud_ceiling - 1):.2f} %), front {fm.sum()} pts")


def ceiling_for(pair: str, outdir: Path) -> float:
    r = load_refs(outdir).loc[pair]
    if "ceiling_hv_polished" in r and np.isfinite(r.get("ceiling_hv_polished",
                                                        float("nan"))):
        return float(r["ceiling_hv_polished"])
    return float(r["ceiling_hv_cloud"])


# --- the campaign ---------------------------------------------------------

def _finalize_run(df: pd.DataFrame, pair: str, ref: np.ndarray) -> pd.DataFrame:
    o1, o2 = PAIRS[pair]["objectives"]
    feas = pair_feasible(df, pair) & df["ok"].astype(bool).to_numpy()
    df["pair_feasible"] = feas
    obj = df[[o1, o2]].to_numpy(dtype=float)
    masked = np.where(feas[:, None], obj, np.inf)
    df["hv"] = [hypervolume_2d(masked[: i + 1], ref) for i in range(len(df))]
    df["best_obj1"] = pd.Series(np.where(feas, obj[:, 0], np.inf)).cummin()
    df["best_obj2"] = pd.Series(np.where(feas, obj[:, 1], np.inf)).cummin()
    return df


def run_bo_seed(pair: str, seed: int, outdir: Path, rounds: int = ROUNDS,
                batch: int = BATCH, acq_restarts: int = 8,
                acq_raw_samples: int = 128) -> pd.DataFrame:
    """Constrained qNEHVI on the chosen pair, era wiring, per-seed round 0.

    Every repeat draws its own scrambled Sobol round 0 (the Sobol generator
    is seeded with the repeat's own seed, as well as through
    ``AxClient(random_seed=...)``), so no two repeats share an initial
    batch.  The acquisition runs at 8 restarts x 128 raw samples, the
    setting the 2026-08-24 paired study measured as statistically
    indistinguishable from the Ax defaults on this simulator (Wilcoxon
    p = 0.92 over ten paired seeds).
    """
    from ax.modelbridge.factory import Models
    from ax.modelbridge.generation_strategy import (GenerationStep,
                                                    GenerationStrategy)
    from ax.service.ax_client import AxClient, ObjectiveProperties

    o1, o2 = PAIRS[pair]["objectives"]
    ref = ref_for(pair, outdir)
    constraints = [f"cable_d_print_mm >= {CABLE_PRINT_FLOOR_MM}",
                   f"envelope_cap_cm3 <= {ENVELOPE_MAX_CM3}"]
    for metric, op, bound in PAIRS[pair]["constraints"]:
        constraints.append(f"{metric} {op} {bound}")
    gs = GenerationStrategy(steps=[
        GenerationStep(model=Models.SOBOL, num_trials=batch,
                       min_trials_observed=batch, max_parallelism=batch,
                       model_kwargs={"seed": seed}),
        GenerationStep(model=Models.BOTORCH_MODULAR, num_trials=-1,
                       max_parallelism=batch,
                       model_gen_kwargs={"model_gen_options": {
                           "optimizer_kwargs": {
                               "num_restarts": int(acq_restarts),
                               "raw_samples": int(acq_raw_samples)}}}),
    ])
    ax_client = AxClient(generation_strategy=gs, random_seed=seed,
                         verbose_logging=False)
    ax_client.create_experiment(
        name=f"bo_contrast_{pair}_seed{seed}",
        parameters=RATIO_PARAMETERS,
        objectives={o1: ObjectiveProperties(minimize=True),
                    o2: ObjectiveProperties(minimize=True)},
        outcome_constraints=constraints,
    )
    ax_keys = {o1, o2, "cable_d_print_mm", "envelope_cap_cm3"}
    ax_keys |= {m for m, _, _ in PAIRS[pair]["constraints"]}

    rows = []
    for rnd in range(rounds + 1):
        t0 = time.time()
        parameterizations, _ = ax_client.get_next_trials(batch)
        for idx, params in parameterizations.items():
            res = evaluate(dict(params))
            res["envelope_cap_cm3"] = res["envelope_cm3"]
            rows.append({"seed": seed, "round": rnd, "trial": idx,
                         **{k: float(v) for k, v in params.items()},
                         **dict(res)})
            ax_client.complete_trial(
                trial_index=idx,
                raw_data={k: v for k, v in res.items() if k in ax_keys})
        print(f"  {pair} seed {seed} round {rnd}: {batch} designs, "
              f"{time.time() - t0:.1f} s", flush=True)

    df = _finalize_run(pd.DataFrame(rows), pair, ref)
    outdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(outdir / f"contrast_bo_{pair}_seed{seed}.csv", index=False,
              float_format="%.6g")
    return df


def _bo_worker(job: tuple) -> str:
    pair, seed, outdir, rounds, batch, acq_restarts, acq_raw = job
    t0 = time.time()
    run_bo_seed(pair, seed, Path(outdir), rounds, batch, acq_restarts, acq_raw)
    print(f"BO {pair} seed {seed} done in {time.time() - t0:.1f} s", flush=True)
    return f"{pair}_seed{seed}"


# --- the baselines --------------------------------------------------------

def _gen_stream(strategy: str, seed: int):
    """An endless stream of candidate points for rejection sampling.

    Space-filling generators are extended in whole blocks so the accepted
    subsequence keeps their stratification as far as rejection allows.
    """
    if strategy == "random":
        rng = np.random.default_rng(seed)
        while True:
            yield from _scale_unit(rng.random((256, len(RATIO_PARAMS))))
    elif strategy == "sobol":
        eng = qmc.Sobol(len(RATIO_PARAMS), scramble=True, seed=seed)
        while True:
            yield from _scale_unit(eng.random(256))
    elif strategy == "lhs":
        n_block = 0
        while True:
            n_block += 1
            eng = qmc.LatinHypercube(len(RATIO_PARAMS),
                                     seed=seed + 7919 * n_block)
            yield from _scale_unit(eng.random(BUDGET))
    else:
        raise ValueError(strategy)


def _run_sampler(strategy: str, seed: int, budget: int,
                 printable_only: bool) -> list[dict]:
    rows, rejected = [], 0
    for x in _gen_stream(strategy, seed):
        if len(rows) >= budget:
            break
        p = _as_params(x)
        if printable_only and not geom_printable(p):
            rejected += 1
            continue
        rows.append({**p, **evaluate(p), "rejected_before": rejected})
    return rows


def _run_compass(pair: str, seed: int, budget: int, ref: np.ndarray,
                 printable_only: bool) -> list[dict]:
    """The era compass search, generalized to any pair and to free
    printability: in printable mode, geometry-infeasible probes are skipped
    without spending budget, the way a person would skip an unprintable
    layout without building it."""
    rng = np.random.default_rng(seed)
    rows, spent = [], 0
    heuristic_weights = (0.15, 0.5, 0.85)
    per_weight = budget // len(heuristic_weights)
    span = BOUNDS_HI - BOUNDS_LO

    def _try(x: np.ndarray) -> dict | None:
        nonlocal spent
        p = _as_params(x)
        if printable_only and not geom_printable(p):
            return None
        res = evaluate(p)
        rows.append({**p, **res})
        spent += 1
        return res

    for wi, w in enumerate(heuristic_weights):
        left = (per_weight if wi < len(heuristic_weights) - 1
                else budget - spent)
        if left <= 0:
            break
        while True:
            x = _scale_unit(rng.random(len(RATIO_PARAMS)))
            res = _try(x)
            if res is not None:
                break
        left -= 1
        best = _scalarize_row(res, pair, w, ref)
        step = 0.35 * np.ones(len(RATIO_PARAMS))

        while left > 0:
            improved = False
            for axi in rng.permutation(len(RATIO_PARAMS)):
                for sign in (+1.0, -1.0):
                    if left <= 0:
                        break
                    cand = x.copy()
                    cand[axi] = float(np.clip(x[axi] + sign * step[axi]
                                              * span[axi],
                                              BOUNDS_LO[axi], BOUNDS_HI[axi]))
                    if np.isclose(cand[axi], x[axi]):
                        continue
                    res = _try(cand)
                    if res is None:
                        continue
                    left -= 1
                    val = _scalarize_row(res, pair, w, ref)
                    if val < best:
                        best, x, improved = val, cand, True
                        break
                if left <= 0:
                    break
            if not improved:
                step *= 0.5
                if step.max() < 1e-3:
                    step = 0.35 * np.ones(len(RATIO_PARAMS))
    return rows


def run_baseline(pair: str, strategy: str, seed: int, outdir: Path,
                 budget: int = BUDGET, printable_only: bool = True
                 ) -> pd.DataFrame:
    ref = ref_for(pair, outdir)
    if strategy == "heuristic":
        rows = _run_compass(pair, seed, budget, ref, printable_only)
    else:
        rows = _run_sampler(strategy, seed, budget, printable_only)
    df = pd.DataFrame(rows)
    df.insert(0, "trial", np.arange(len(df)))
    df.insert(0, "round", df["trial"] // BATCH)
    df.insert(0, "seed", seed)
    df.insert(0, "strategy", strategy)
    df = _finalize_run(df, pair, ref)
    mode = "printable" if printable_only else "plain"
    outdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(outdir / f"contrast_baseline_{strategy}_{mode}_{pair}"
                       f"_seed{seed}.csv", index=False, float_format="%.6g")
    return df


def _baseline_worker(job: tuple) -> str:
    pair, strategy, seed, outdir, budget, printable_only = job
    run_baseline(pair, strategy, seed, Path(outdir), budget, printable_only)
    return f"{strategy}_{seed}"


# --- comparison -----------------------------------------------------------

def _load_bo(pair: str, outdir: Path) -> list[pd.DataFrame]:
    files = sorted(outdir.glob(f"contrast_bo_{pair}_seed*.csv"),
                   key=lambda f: int(f.stem.split("seed")[-1]))
    return [pd.read_csv(f) for f in files]


def _load_base(pair: str, strategy: str, mode: str,
               outdir: Path) -> list[pd.DataFrame]:
    files = sorted(
        outdir.glob(f"contrast_baseline_{strategy}_{mode}_{pair}_seed*.csv"),
        key=lambda f: int(f.stem.split("seed")[-1]))
    return [pd.read_csv(f) for f in files]


def compare(pair: str, outdir: Path, mode: str = "printable") -> None:
    from scipy.stats import mannwhitneyu

    o1, o2 = PAIRS[pair]["objectives"]
    ceiling = ceiling_for(pair, outdir)
    traces = {"botorch": _load_bo(pair, outdir)}
    for s in ("sobol", "lhs", "random", "heuristic"):
        traces[s] = _load_base(pair, s, mode, outdir)
    traces = {k: v for k, v in traces.items() if v}

    fig, axes = plt.subplots(1, 3, figsize=(16.6, 4.5), dpi=200)
    rows = []
    bo_final = None
    for strategy, frames in traces.items():
        n = min(len(f) for f in frames)
        colour, label = STRATEGY_STYLE[strategy]
        x = np.arange(1, n + 1)
        for ax, col, ylabel in ((axes[0], "hv", "dominated hypervolume"),
                                (axes[1], "best_obj1",
                                 f"running-best {o1}"),
                                (axes[2], "best_obj2",
                                 f"running-best {o2}")):
            arr = np.vstack([f[col].to_numpy()[:n] for f in frames])
            mean, sd = arr.mean(axis=0), arr.std(axis=0)
            ax.plot(x, mean, color=colour, lw=2,
                    label=f"{label} (n={len(frames)})")
            ax.fill_between(x, mean - sd, mean + sd, color=colour, alpha=0.15)
            ax.set_xlabel("simulated design")
            ax.set_ylabel(ylabel)
            ax.grid(alpha=0.25, lw=0.5)
        final = np.array([f["hv"].to_numpy()[n - 1] for f in frames])
        b1 = np.array([f["best_obj1"].to_numpy()[n - 1] for f in frames])
        b2 = np.array([f["best_obj2"].to_numpy()[n - 1] for f in frames])
        if strategy == "botorch":
            bo_final = final
        rows.append({"strategy": strategy, "n_seeds": len(frames),
                     "budget": n,
                     "final_hv_mean": final.mean(), "final_hv_sd": final.std(),
                     "hv_frac_of_ceiling": final.mean() / ceiling,
                     f"best_{o1}_mean": b1.mean(), f"best_{o1}_sd": b1.std(),
                     f"best_{o2}_mean": b2.mean(), f"best_{o2}_sd": b2.std()})
    axes[0].axhline(ceiling, color="#111111", ls="--", lw=1.2,
                    label="ceiling (cloud + polish)")
    for ax in axes:
        ax.legend(fontsize=7.5)
    axes[0].set_title("Hypervolume against the fixed reference point",
                      fontsize=10)
    axes[1].set_title(f"Best {o1} so far", fontsize=10)
    axes[2].set_title(f"Best {o2} so far", fontsize=10)
    mode_label = ("printability-filtered DOE" if mode == "printable"
                  else "plain DOE")
    n_bo = len(traces.get("botorch", []))
    fig.suptitle(f"Objective pair '{pair}' ({o1} + {o2}): constrained qNEHVI "
                 f"against {mode_label}, mean +/- 1 sd over "
                 f"{n_bo} independent-seed repeats", fontsize=11)
    fig.tight_layout()
    fig.savefig(outdir / f"bo_contrast_{pair}_comparison.png",
                bbox_inches="tight")
    plt.close(fig)

    summary = pd.DataFrame(rows)
    if bo_final is not None:
        pvals = []
        for strategy in summary["strategy"]:
            if strategy == "botorch":
                pvals.append(np.nan)
                continue
            frames = traces[strategy]
            other = np.array([f["hv"].to_numpy()[-1] for f in frames])
            pvals.append(mannwhitneyu(bo_final, other,
                                      alternative="greater").pvalue)
        summary["mannwhitney_p_vs_bo"] = pvals
    summary.to_csv(outdir / f"bo_contrast_{pair}_summary.csv", index=False,
                   float_format="%.6g")
    print(summary.to_string(index=False))

    # objective-space panel: where every method spent its budget
    front_path = outdir / f"contrast_front_{pair}.csv"
    fig, ax = plt.subplots(figsize=(7.0, 5.4), dpi=200)
    cloud = load_cloud(outdir)
    okc = cloud[cloud["ok"].astype(bool)]
    cfeas = pair_feasible(okc, pair)
    ax.scatter(okc.loc[cfeas, o1], okc.loc[cfeas, o2], s=2, alpha=0.10,
               color="#d5d8dc", rasterized=True, label="feasible cloud")
    if front_path.exists():
        front = pd.read_csv(front_path)
        ax.plot(front[o1], front[o2], color="#111111", lw=1.8, zorder=6,
                label="reference front")
    for strategy, frames in traces.items():
        colour, label = STRATEGY_STYLE[strategy]
        allpts = pd.concat(frames)
        allpts = allpts[allpts["pair_feasible"].astype(bool)]
        ax.scatter(allpts[o1], allpts[o2], s=8, alpha=0.4, color=colour,
                   label=label, zorder=4)
    ax.set_xlabel(OBJ_LABEL.get(o1, o1))
    ax.set_ylabel(OBJ_LABEL.get(o2, o2))
    ax.set_title(f"Pair '{pair}': where each method spent its budget "
                 "(feasible designs, all seeds pooled)", fontsize=10)
    ax.grid(alpha=0.25, lw=0.5)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / f"bo_contrast_{pair}_objective_space.png",
                bbox_inches="tight")
    plt.close(fig)
    print(f"wrote bo_contrast_{pair}_comparison.png, _objective_space.png, "
          f"_summary.csv")


def strain_era_contrast(outdir: Path) -> None:
    """Re-score the committed strain-era runs under this study's convention.

    The era study ran the same protocol (10 seeds, 45 designs, full-effort
    qNEHVI) on the (t180, peak_tendon_strain) pair and found no separation,
    but it had no reference sweep, so its summary carries absolute
    hypervolumes only.  The cloud built here prices that pair's ceiling, so
    the era trials can be re-scored against it: same reference point, same
    ceiling estimator, directly comparable to the new pair's numbers.
    """
    era_dir = HERE / "outputs"
    ref = ref_for("strain", outdir)
    ceiling = ceiling_for("strain", outdir)
    rows = []
    specs = [("botorch", "pr102_sim_bo_botorch_ratios-strain_sobol_seed*.csv"),
             ("sobol", "pr102_baseline_sobol_ratios-strain_seed*.csv"),
             ("lhs", "pr102_baseline_lhs_ratios-strain_seed*.csv"),
             ("random", "pr102_baseline_random_ratios-strain_seed*.csv"),
             ("heuristic", "pr102_baseline_heuristic_ratios-strain_seed*.csv")]
    seed_rows = []
    for strategy, pat in specs:
        finals = []
        for f in sorted(era_dir.glob(pat)):
            df = pd.read_csv(f)
            feas = df["feasible"].to_numpy(dtype=bool)
            obj = df[["t180", "peak_tendon_strain"]].to_numpy(dtype=float)
            masked = np.where(feas[:, None], obj, np.inf)
            hv = hypervolume_2d(masked, ref)
            finals.append(hv)
            seed_rows.append({"strategy": strategy, "file": f.name,
                              "final_hv": hv,
                              "hv_frac_of_ceiling": hv / ceiling})
        if finals:
            finals = np.array(finals)
            rows.append({"strategy": strategy, "n_seeds": len(finals),
                         "final_hv_mean": finals.mean(),
                         "final_hv_sd": finals.std(),
                         "hv_frac_of_ceiling": finals.mean() / ceiling})
    out = pd.DataFrame(rows)
    out.to_csv(outdir / "bo_contrast_strain_era_rescored.csv", index=False,
               float_format="%.6g")
    pd.DataFrame(seed_rows).to_csv(
        outdir / "bo_contrast_strain_era_rescored_seeds.csv", index=False,
        float_format="%.6g")
    print("strain-era runs, re-scored under the study convention:")
    print(out.to_string(index=False))


def headline(pair: str, outdir: Path, mode: str = "printable") -> None:
    """The two-panel money plot: the same protocol on both objective pairs.

    Left: the committed strain-era runs (the no-separation geometry).
    Right: this study's chosen pair.  Both axes are the fraction of that
    pair's own polished ceiling, so the panels are directly comparable.
    """
    era = pd.read_csv(outdir / "bo_contrast_strain_era_rescored_seeds.csv")
    order = ["botorch", "sobol", "lhs", "random", "heuristic"]
    ceiling = ceiling_for(pair, outdir)
    new_rows = []
    for s in order:
        frames = (_load_bo(pair, outdir) if s == "botorch"
                  else _load_base(pair, s, mode, outdir))
        for f in frames:
            new_rows.append({"strategy": s,
                             "hv_frac_of_ceiling":
                                 f["hv"].to_numpy()[-1] / ceiling})
    new = pd.DataFrame(new_rows)

    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.9), dpi=200, sharey=True)
    rng = np.random.default_rng(7)
    for ax, df, title in (
            (axes[0], era, "(t180, peak tendon strain): the anti-correlated "
             "band\nno separation, committed era runs"),
            (axes[1], new, f"(t180, envelope volume): the efficient ridge\n"
             f"this study, mode = {mode}")):
        for i, s in enumerate(order):
            v = 100 * df.loc[df["strategy"] == s,
                             "hv_frac_of_ceiling"].to_numpy()
            if not len(v):
                continue
            colour, label = STRATEGY_STYLE[s]
            x = i + rng.uniform(-0.13, 0.13, len(v))
            ax.scatter(x, v, s=26, alpha=0.8, color=colour, zorder=4)
            ax.hlines(v.mean(), i - 0.28, i + 0.28, color=colour, lw=2.5,
                      zorder=5)
        ax.axhline(100, color="#111111", ls="--", lw=1.1)
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels([STRATEGY_STYLE[s][1] for s in order], fontsize=8,
                           rotation=12)
        ax.set_title(title, fontsize=10)
        ax.grid(alpha=0.25, lw=0.5, axis="y")
    axes[0].set_ylabel("final hypervolume, % of the pair's own ceiling\n"
                       "(45 designs, 10 independent seeds)")
    fig.suptitle("Same optimizer, same protocol, same simulator: the "
                 "BO-vs-DOE contrast is a property of the objective pair",
                 fontsize=11.5)
    fig.tight_layout()
    fig.savefig(outdir / "bo_contrast_headline.png", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {outdir}/bo_contrast_headline.png")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cloud", type=int, default=None, metavar="N",
                    help="build the N-design observable cloud")
    ap.add_argument("--screen", action="store_true")
    ap.add_argument("--reference", metavar="PAIR", default=None,
                    help="Nelder-Mead polish of the pair's ceiling")
    ap.add_argument("--campaign", metavar="PAIR", default=None)
    ap.add_argument("--baselines", metavar="PAIR", default=None)
    ap.add_argument("--compare", metavar="PAIR", default=None)
    ap.add_argument("--era-contrast", action="store_true",
                    help="re-score the committed strain-era runs under this "
                         "study's reference convention")
    ap.add_argument("--headline", metavar="PAIR", default=None,
                    help="the two-panel strain-era vs chosen-pair figure")
    ap.add_argument("--strategies", nargs="*",
                    default=["random", "sobol", "lhs", "heuristic"])
    ap.add_argument("--mode", choices=("printable", "plain", "both"),
                    default="both",
                    help="baseline sampling mode; printable rejection-samples "
                         "through the free geometric check")
    ap.add_argument("--seeds", type=int, nargs="*", default=SEEDS)
    ap.add_argument("--rounds", type=int, default=ROUNDS)
    ap.add_argument("--batch-size", type=int, default=BATCH)
    ap.add_argument("--acq-restarts", type=int, default=8)
    ap.add_argument("--acq-raw-samples", type=int, default=128)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--outdir", type=Path, default=OUT)
    args = ap.parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)

    if args.cloud:
        build_cloud(args.cloud, args.jobs, args.outdir)
    if args.screen:
        screen(args.outdir)
    if args.reference:
        run_reference(args.reference, args.jobs, args.outdir)
    if args.campaign:
        jobs = [(args.campaign, s, str(args.outdir), args.rounds,
                 args.batch_size, args.acq_restarts, args.acq_raw_samples)
                for s in args.seeds]
        t0 = time.time()
        if args.jobs > 1 and len(jobs) > 1:
            import multiprocessing as mp
            with mp.get_context("spawn").Pool(min(args.jobs,
                                                  len(jobs))) as pool:
                for tag in pool.imap_unordered(_bo_worker, jobs):
                    print(f"  wrote {tag}", flush=True)
        else:
            for job in jobs:
                _bo_worker(job)
        print(f"{len(jobs)} BO repeat(s) in {time.time() - t0:.1f} s")
    if args.baselines:
        modes = (["printable", "plain"] if args.mode == "both"
                 else [args.mode])
        jobs = [(args.baselines, s, seed, str(args.outdir), BUDGET,
                 m == "printable")
                for m in modes for s in args.strategies for seed in args.seeds]
        t0 = time.time()
        if args.jobs > 1 and len(jobs) > 1:
            import multiprocessing as mp
            with mp.get_context("spawn").Pool(min(args.jobs,
                                                  len(jobs))) as pool:
                for _ in pool.imap_unordered(_baseline_worker, jobs):
                    pass
        else:
            for job in jobs:
                _baseline_worker(job)
        print(f"{len(jobs)} baseline run(s) in {time.time() - t0:.1f} s")
    if args.compare:
        compare(args.compare, args.outdir)
    if args.era_contrast:
        strain_era_contrast(args.outdir)
    if args.headline:
        headline(args.headline, args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
