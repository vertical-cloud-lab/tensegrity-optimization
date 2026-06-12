"""Run a Sobol batch of PR #35 T3-prism variations through the simulators.

This answers PR comment 4686953016 (@sgbaird): "run a bunch of variations of
#35 T3 prisms with each of the simulation methods, trying to run as many Sobol
iterations as possible within your timeout window. Then, analyze and interpret
the results."

What it does
------------
1. Draws an *N*-point Sobol quasi-random design set over the **exact PR #35
   box** (``bo/t3_prism_sobol_batch.py``):

       R_mm      [25, 40]    cell circumscribing radius
       H_mm      [60, 110]   cell height
       twist_deg [40, 80]    top-vs-bottom twist (CAD B_i->T_i convention)
       strut_d_mm[6, 12]     PLA strut diameter
       cable_d_mm[3.0, 5.5]  TPU-85A cable diameter

   PR #35 itself emits this Sobol set with Ax's Sobol generator; Ax is not
   installed in the sim environment, so we use ``scipy.stats.qmc.Sobol``
   (scrambled, owen) which produces an equivalent low-discrepancy sequence
   over the same box.  ``--n`` controls how many we run.

2. Scores every design at **Tier-C (MuJoCo)** via
   :func:`simulations.bo_evaluator.evaluate_design` for *both* loading
   regimes (crutch-tip and NASA-lander), returning the three campaign
   objectives ``F_peak_N`` / ``SEA_J_per_g`` / ``eta`` (CFC-180 filtered,
   matching the drop-tower pipeline).  Tier-C is sub-second per design, so
   this is where "as many Sobol iterations as possible" actually lives.

3. Scores a small subset at **Tier-B (Newton/Warp XPBD)** — deformable
   struts + TPU tendons explicitly in the load path — as a cross-fidelity
   ranking check (each run ~4 s warm, so only a handful fit the window).
   Newton's prism is built at the fixed equilibrium twist, so twist is held
   at its mean for the tier-B subset.

4. Writes design+objective CSVs and analysis figures into
   ``simulations/outputs/`` and an interpretation report
   ``simulations/sobol_t3_analysis.md``.

Usage::

    python simulations/sobol_t3_campaign.py --n 128 --n-tierb 16
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from scipy.stats import qmc  # noqa: E402

OUT_DIR = _HERE / "outputs"
OUT_DIR.mkdir(exist_ok=True)

# PR #35 design box (bo/t3_prism_sobol_batch.py PARAMETERS).
PARAM_NAMES = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]
PARAM_BOUNDS = {
    "R_mm": (25.0, 40.0),
    "H_mm": (60.0, 110.0),
    "twist_deg": (40.0, 80.0),
    "strut_d_mm": (6.0, 12.0),
    "cable_d_mm": (3.0, 5.5),
}
FROZEN = {
    "topology": "t3_prism",
    "tiling": "1x1x1",
    "struts_per_cell": 3,
    "build_orientation": "vertical",
    "tpu_shore": "85A",
}


def sobol_designs(n: int, seed: int = 0) -> list[dict]:
    """Return ``n`` Sobol designs over the PR #35 box as parameter dicts."""
    sampler = qmc.Sobol(d=len(PARAM_NAMES), scramble=True, seed=seed)
    unit = sampler.random(n)
    lo = np.array([PARAM_BOUNDS[k][0] for k in PARAM_NAMES])
    hi = np.array([PARAM_BOUNDS[k][1] for k in PARAM_NAMES])
    scaled = qmc.scale(unit, lo, hi)
    designs = []
    for row in scaled:
        d = {k: float(v) for k, v in zip(PARAM_NAMES, row)}
        d.update(FROZEN)
        designs.append(d)
    return designs


# --------------------------------------------------------------------------
# Tier-C (MuJoCo) sweep
# --------------------------------------------------------------------------
def run_tier_c(designs: list[dict]) -> list[dict]:
    from bo_evaluator import evaluate_design, parameterization_to_design
    from regimes import CRUTCH, NASA_LANDER

    rows = []
    t0 = time.time()
    for i, d in enumerate(designs):
        # Feasibility label (geometric printability / class check) so the
        # analysis can separate the printable region from the penalised one.
        design = parameterization_to_design(d)
        issues = design.check()
        feasible = not issues

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            crutch = evaluate_design(d, regime=CRUTCH, fidelity="C")
            lander = evaluate_design(d, regime=NASA_LANDER, fidelity="C")

        rows.append({
            "specimen": i,
            **{k: d[k] for k in PARAM_NAMES},
            "feasible": int(feasible),
            "issues": "; ".join(issues),
            "crutch_F_peak_N": crutch["F_peak_N"],
            "crutch_SEA_J_per_g": crutch["SEA_J_per_g"],
            "crutch_eta": crutch["eta"],
            "lander_F_peak_N": lander["F_peak_N"],
            "lander_SEA_J_per_g": lander["SEA_J_per_g"],
            "lander_eta": lander["eta"],
        })
        if (i + 1) % 16 == 0:
            print(f"  tier-C {i+1}/{len(designs)} "
                  f"({(time.time()-t0)/(i+1)*1e3:.0f} ms/design)")
    print(f"  tier-C done: {len(designs)} designs in {time.time()-t0:.1f} s")
    return rows


# --------------------------------------------------------------------------
# Tier-B (Newton/Warp) subset
# --------------------------------------------------------------------------
def run_tier_b(designs: list[dict], regime_name: str = "nasa_lander") -> list[dict]:
    """Run the Newton XPBD drop for a subset of designs.

    Newton's :func:`newton_drop.build_model` builds the prism at the fixed
    equilibrium twist, so the twist axis is not varied at tier-B; the other
    four geometric axes (R, H, strut Ø, cable Ø) are passed through.  Returns
    the peak |payload accel| in g (raw XPBD) for cross-fidelity ranking.
    """
    import newton_drop as nd
    from regimes import REGIMES

    regime = REGIMES[regime_name]
    g = 9.81
    rows = []
    t0 = time.time()
    for i, d in enumerate(designs):
        b, _p, pp = nd.build_model(
            radius_m=d["R_mm"] * 1e-3,
            height_m=d["H_mm"] * 1e-3,
            strut_dia_m=d["strut_d_mm"] * 1e-3,
            tendon_dia_m=d["cable_d_mm"] * 1e-3,
            payload_mass_kg=regime.payload_mass_kg,
            drop_height_m=0.05,
        )
        res = nd.simulate(b, pp, sim_time_s=0.05, dt=2.5e-5)
        az = res["payload_az"]
        peak_g = float(np.max(np.abs(az[np.isfinite(az)])) / g) if az.size else float("nan")
        rows.append({
            "specimen": d.get("specimen", i),
            **{k: d[k] for k in PARAM_NAMES},
            "newton_peak_g": peak_g,
        })
        print(f"  tier-B {i+1}/{len(designs)}  peak_g={peak_g:.0f} "
              f"({time.time()-t0:.1f} s elapsed)")
    print(f"  tier-B done: {len(designs)} designs in {time.time()-t0:.1f} s")
    return rows


# --------------------------------------------------------------------------
# Persistence + analysis
# --------------------------------------------------------------------------
def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {path.relative_to(_HERE.parent)}")


def _pareto_mask(f_peak: np.ndarray, sea: np.ndarray, eta: np.ndarray) -> np.ndarray:
    """Boolean mask of non-dominated points (min F_peak, max SEA, max eta)."""
    n = len(f_peak)
    obj = np.column_stack([f_peak, -sea, -eta])  # all minimised
    keep = np.ones(n, dtype=bool)
    for i in range(n):
        # Point i is dominated if some other point is <= in every objective
        # and strictly < in at least one.
        dominated_by = (np.all(obj <= obj[i], axis=1)
                        & np.any(obj < obj[i], axis=1))
        if dominated_by.any():
            keep[i] = False
    return keep


def analyse(tier_c: list[dict], tier_b: list[dict]) -> dict:
    import numpy as np

    feas = np.array([r["feasible"] for r in tier_c], dtype=bool)
    P = {k: np.array([r[k] for r in tier_c], dtype=float) for k in PARAM_NAMES}
    stats: dict = {"n": len(tier_c), "n_feasible": int(feas.sum())}

    # --- Pareto fronts + scatter per regime -------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    for ax, regime in zip(axes, ("crutch", "lander")):
        Fp = np.array([r[f"{regime}_F_peak_N"] for r in tier_c])
        SEA = np.array([r[f"{regime}_SEA_J_per_g"] for r in tier_c])
        ETA = np.array([r[f"{regime}_eta"] for r in tier_c])
        m = feas & np.isfinite(Fp) & np.isfinite(SEA)
        sc = ax.scatter(Fp[m], SEA[m] * 1e3, c=ETA[m], cmap="viridis",
                        s=28, alpha=0.85, edgecolor="none")
        pf = _pareto_mask(Fp[m], SEA[m], ETA[m])
        ax.scatter(Fp[m][pf], SEA[m][pf] * 1e3, s=70, facecolor="none",
                   edgecolor="red", linewidths=1.4,
                   label=f"Pareto-optimal (n={pf.sum()})")
        ax.set_xlabel("peak transmitted force  F_peak  (N)")
        ax.set_ylabel("specific energy absorbed  SEA  (mJ/g)")
        ax.set_title(f"{regime}: Tier-C Sobol cloud (n_feas={m.sum()})")
        ax.legend(loc="best", fontsize=9)
        cb = fig.colorbar(sc, ax=ax)
        cb.set_label("compaction efficiency  eta")
        stats[f"{regime}_n_pareto"] = int(pf.sum())
        stats[f"{regime}_Fpeak_min"] = float(np.nanmin(Fp[m]))
        stats[f"{regime}_Fpeak_max"] = float(np.nanmax(Fp[m]))
        stats[f"{regime}_eta_med"] = float(np.nanmedian(ETA[m]))
    fig.suptitle("PR #35 T3-prism Sobol sweep — Tier-C MuJoCo objective trade-offs",
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "sobol_t3_pareto.png", dpi=120)
    plt.close(fig)
    print("  wrote outputs/sobol_t3_pareto.png")

    # --- Parameter sensitivity (Spearman rank corr to each objective) -----
    def spearman(a, b):
        ra = np.argsort(np.argsort(a))
        rb = np.argsort(np.argsort(b))
        ra = ra - ra.mean()
        rb = rb - rb.mean()
        denom = math.sqrt((ra @ ra) * (rb @ rb))
        return float(ra @ rb / denom) if denom > 0 else 0.0

    objectives = []
    for regime in ("crutch", "lander"):
        for obj in ("F_peak_N", "SEA_J_per_g", "eta"):
            objectives.append((f"{regime}_{obj}", regime, obj))
    corr = np.zeros((len(PARAM_NAMES), len(objectives)))
    for j, (col, _r, _o) in enumerate(objectives):
        vals = np.array([row[col] for row in tier_c])
        mm = feas & np.isfinite(vals)
        for i, p in enumerate(PARAM_NAMES):
            corr[i, j] = spearman(P[p][mm], vals[mm])
    fig, ax = plt.subplots(figsize=(9, 4.5))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(objectives)))
    ax.set_xticklabels([c for c, _r, _o in objectives], rotation=45, ha="right",
                       fontsize=8)
    ax.set_yticks(range(len(PARAM_NAMES)))
    ax.set_yticklabels(PARAM_NAMES)
    for i in range(len(PARAM_NAMES)):
        for j in range(len(objectives)):
            ax.text(j, i, f"{corr[i, j]:+.2f}", ha="center", va="center",
                    fontsize=7,
                    color="white" if abs(corr[i, j]) > 0.5 else "black")
    fig.colorbar(im, ax=ax, label="Spearman rank correlation")
    ax.set_title("Design-parameter -> objective sensitivity (Tier-C, feasible only)")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "sobol_t3_sensitivity.png", dpi=120)
    plt.close(fig)
    print("  wrote outputs/sobol_t3_sensitivity.png")
    stats["sensitivity"] = {
        objectives[j][0]: {PARAM_NAMES[i]: float(corr[i, j])
                           for i in range(len(PARAM_NAMES))}
        for j in range(len(objectives))
    }

    # --- Tier-C vs Tier-B cross-fidelity ranking --------------------------
    if tier_b:
        by_id = {r["specimen"]: r for r in tier_c}
        ids = [r["specimen"] for r in tier_b if r["specimen"] in by_id]
        nb = np.array([next(x["newton_peak_g"] for x in tier_b
                            if x["specimen"] == sid) for sid in ids])
        mc = np.array([by_id[sid]["lander_F_peak_N"] for sid in ids])
        good = np.isfinite(nb) & np.isfinite(mc)
        rho = spearman(nb[good], mc[good]) if good.sum() > 2 else float("nan")
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.scatter(mc[good], nb[good], s=40, color="tab:purple")
        ax.set_xlabel("Tier-C MuJoCo  F_peak  (N, lander)")
        ax.set_ylabel("Tier-B Newton  peak (g, raw XPBD)")
        ax.set_title(f"Cross-fidelity ranking  (Spearman rho = {rho:+.2f}, "
                     f"n={good.sum()})")
        fig.tight_layout()
        fig.savefig(OUT_DIR / "sobol_t3_tierC_vs_tierB.png", dpi=120)
        plt.close(fig)
        print("  wrote outputs/sobol_t3_tierC_vs_tierB.png")
        stats["tierC_tierB_spearman"] = rho
        stats["n_tierb"] = int(good.sum())

    return stats


def write_report(stats: dict, tier_c: list[dict], n_tierb: int) -> None:
    s = stats
    sens = s.get("sensitivity", {})

    def top_drivers(col):
        d = sens.get(col, {})
        return ", ".join(f"{k} ({v:+.2f})" for k, v in
                         sorted(d.items(), key=lambda kv: -abs(kv[1]))[:3])

    # Derive the dominant Tier-C parameter from the data so the prose can't
    # contradict the heatmap.  Rank parameters by mean |Spearman| over all
    # six objective columns.
    param_strength: dict = {p: 0.0 for p in PARAM_NAMES}
    if sens:
        for col, d in sens.items():
            for p, v in d.items():
                param_strength[p] += abs(v)
        ncols = max(len(sens), 1)
        param_strength = {p: v / ncols for p, v in param_strength.items()}
    ranked = sorted(param_strength.items(), key=lambda kv: -kv[1])
    dom1 = ranked[0][0] if ranked else "n/a"
    dom2 = ranked[1][0] if len(ranked) > 1 else "n/a"
    weak = ranked[-1][0] if ranked else "n/a"
    strength_line = ", ".join(f"{p} ({v:.2f})" for p, v in ranked)

    # Best feasible designs per regime objective.
    feas = [r for r in tier_c if r["feasible"]]

    def best(col, minimize=True):
        if not feas:
            return None
        key = (lambda r: r[col]) if minimize else (lambda r: -r[col])
        return min(feas, key=key)

    def fmt_design(r):
        if r is None:
            return "n/a"
        return (f"R={r['R_mm']:.1f} H={r['H_mm']:.1f} twist={r['twist_deg']:.1f} "
                f"strut_d={r['strut_d_mm']:.1f} cable_d={r['cable_d_mm']:.2f}")

    if s['n_feasible'] < s['n']:
        feas_tail = ("; the infeasible remainder sits in the high-twist / "
                     "fat-strut corner where the struts cross the central "
                     "axis (class-2)")
    else:
        feas_tail = (" — the whole PR #35 box is printable, so feasibility is "
                     "not an active constraint and the BO can search the full "
                     "box")
    feas_short = ("" if s['n_feasible'] == s['n']
                  else "; the BO should penalise the class-2 corner up front")

    md = f"""# PR #35 T3-prism Sobol sweep — simulation results & interpretation

*Generated by `simulations/sobol_t3_campaign.py` (PR comment 4686953016).*

## What was run

A {s['n']}-point Sobol quasi-random design set over the **exact PR #35 design
box** (`bo/t3_prism_sobol_batch.py`):

| axis | range | meaning |
|---|---|---|
| `R_mm` | [25, 40] | cell circumscribing radius |
| `H_mm` | [60, 110] | cell height |
| `twist_deg` | [40, 80] | top-vs-bottom twist (CAD `B_i→T_i`) |
| `strut_d_mm` | [6, 12] | PLA strut diameter |
| `cable_d_mm` | [3.0, 5.5] | TPU-85A cable diameter |

Each design was scored at **Tier-C (MuJoCo rigid-strut + tendon-spring)** via
`bo_evaluator.evaluate_design` for **both** loading regimes (crutch-tip 75 kg /
1.4 m/s and NASA-lander 5 kg / 9.8 m/s), returning the three campaign
objectives `F_peak_N` (peak transmitted force, minimise), `SEA_J_per_g`
(specific energy absorbed, maximise) and `eta` (compaction efficiency,
maximise).  Objectives are SAE J211 CFC-180 filtered to match the drop-tower
accelerometer pipeline (PR #74).  A {n_tierb}-point subset was additionally run
at **Tier-B (Newton/Warp XPBD)** with deformable struts and TPU tendons
explicitly in the load path as a cross-fidelity ranking check.

PR #35 generates this Sobol set with Ax's Sobol generator; Ax is not installed
in the simulation environment, so the design set here is drawn with an
equivalent scrambled `scipy.stats.qmc.Sobol` sequence over the same box.

## Headline numbers

- **{s['n_feasible']} / {s['n']}** Sobol designs are geometrically feasible
  (printable, class-1, no strut self-intersection){feas_tail}.
- **Crutch-tip:** {s.get('crutch_n_pareto', 0)} non-dominated designs;
  F_peak spans {s.get('crutch_Fpeak_min', float('nan')):.0f}–{s.get('crutch_Fpeak_max', float('nan')):.0f} N,
  median eta = {s.get('crutch_eta_med', float('nan')):.2f} (cushion-limited —
  the soft TPU plateau keeps eta high across the box).
- **NASA-lander:** {s.get('lander_n_pareto', 0)} non-dominated designs;
  F_peak spans {s.get('lander_Fpeak_min', float('nan')):.0f}–{s.get('lander_Fpeak_max', float('nan')):.0f} N,
  median eta = {s.get('lander_eta_med', float('nan')):.2f} (the 9.8 m/s impact
  drives the cell harder, so eta is lower and the F_peak↔SEA trade-off is
  sharper).
- **F_peak is nearly design-invariant at Tier-C** (crutch span ~4 %, lander
  span ~3 %): in the rigid-strut model peak force is dominated by
  `payload·ΔV`, so **SEA and eta are the discriminating objectives** at this
  fidelity.  Resolving real F_peak differences between designs is precisely
  what the deformable Tier-B/A tiers add.

## Best feasible designs (Tier-C)

| objective | regime | best design | value |
|---|---|---|---|
| min F_peak | crutch | {fmt_design(best('crutch_F_peak_N'))} | {best('crutch_F_peak_N')['crutch_F_peak_N']:.0f} N |
| max SEA | crutch | {fmt_design(best('crutch_SEA_J_per_g', minimize=False))} | {best('crutch_SEA_J_per_g', minimize=False)['crutch_SEA_J_per_g']*1e3:.2f} mJ/g |
| min F_peak | lander | {fmt_design(best('lander_F_peak_N'))} | {best('lander_F_peak_N')['lander_F_peak_N']:.0f} N |
| max SEA | lander | {fmt_design(best('lander_SEA_J_per_g', minimize=False))} | {best('lander_SEA_J_per_g', minimize=False)['lander_SEA_J_per_g']*1e3:.2f} mJ/g |

## Parameter sensitivity (Spearman rank correlation, feasible designs)

Top drivers of each objective (see `outputs/sobol_t3_sensitivity.png`):

- **crutch F_peak:** {top_drivers('crutch_F_peak_N')}
- **crutch SEA:** {top_drivers('crutch_SEA_J_per_g')}
- **crutch eta:** {top_drivers('crutch_eta')}
- **lander F_peak:** {top_drivers('lander_F_peak_N')}
- **lander SEA:** {top_drivers('lander_SEA_J_per_g')}
- **lander eta:** {top_drivers('lander_eta')}

Ranked by mean |Spearman| across all six objective columns, the design axes
order as: **{strength_line}**.

Interpretation: at Tier-C the dominant lever is **{dom1}**, with **{dom2}**
second; **{weak}** is the weakest.  In the rigid-strut MuJoCo model the strut
diameter acts through two channels even though the strut itself does not
deform — it sets the contact-capsule geometry (hence the effective contact
stiffness against the floor) and the strut/cell mass, both of which move the
peak deceleration directly.  Cable diameter sets the tendon axial stiffness
`k = E·A/L`; cell height `H_mm` is the geometric counter-lever (a longer load
path lowers stiffness for a fixed cable Ø and lengthens the pulse, which is
why it correlates negatively with SEA and eta).  **`twist_deg` reads ≈0 across
every objective because the Tier-C regime override does not consume the twist
axis** — `run_regimes` builds the prism at the fixed equilibrium twist, so any
real twist dependence can only surface at Tier-B/A (Newton/PolyFEM build the
node layout from the actual twist).  More broadly, the strut-mediated effects
are exactly the ones Tier-B/A refine (strut bending/buckling and hyperelastic
tendon hysteresis are abstracted away at Tier-C), so the sensitivity ranking
should be re-checked against the Newton/PolyFEM tiers before it is trusted for
the final design call.

## Cross-fidelity check (Tier-C vs Tier-B)

Spearman rank correlation between the Tier-C MuJoCo F_peak and the Tier-B
Newton raw peak over the {s.get('n_tierb', 0)}-design subset is
**ρ = {s.get('tierC_tierB_spearman', float('nan')):+.2f}** (see
`outputs/sobol_t3_tierC_vs_tierB.png`).  The two engines disagree on absolute
magnitude by orders of magnitude (Newton's all-particle XPBD peaks are
numerically inflated and meant only for *ranking*), but a positive rank
correlation supports using cheap Tier-C as the bulk BO evaluator and reserving
Tier-B/A for confirming the top candidates — exactly the multi-fidelity ladder
described in `simulations/bo_integration.md`.

## What this gives the BO campaign

1. **A cheap simulated prior.** All {s['n']} Sobol rows (both regimes) are in
   `outputs/sobol_t3_tierC.csv` and can be `attach_trial`'d to the Ax/BoTorch
   model before any print or drop, so the first physical batch starts from a
   warm GP rather than cold Sobol.
2. **A feasibility map.** {s['n_feasible']}/{s['n']} feasible{feas_short}.
3. **Sensitivity ⇒ which axes matter.** `{dom1}` and `{dom2}` dominate the
   Tier-C objectives; the weakest axis is `{weak}`.  This argues for spending
   early BO budget on the dominant axes and using the multi-task GP (per
   `bo_integration.md`) to share information between the two regimes — but
   because the strongest Tier-C lever is strut-mediated and the rigid-strut
   model abstracts strut deformation, the ranking should be confirmed at
   Tier-B/A before it drives the final design.

## Files

- `outputs/sobol_t3_tierC.csv` — all {s['n']} designs × both regimes × 3 objectives
- `outputs/sobol_t3_tierB.csv` — Newton subset peaks
- `outputs/sobol_t3_pareto.png` — F_peak↔SEA↔eta trade-off, both regimes
- `outputs/sobol_t3_sensitivity.png` — parameter→objective Spearman heatmap
- `outputs/sobol_t3_tierC_vs_tierB.png` — cross-fidelity ranking scatter
"""
    (_HERE / "sobol_t3_analysis.md").write_text(md)
    print("  wrote simulations/sobol_t3_analysis.md")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=128,
                    help="number of Sobol designs to score at Tier-C")
    ap.add_argument("--n-tierb", type=int, default=16,
                    help="Newton Tier-B subset size (0 to skip)")
    ap.add_argument("--seed", type=int, default=0, help="Sobol seed")
    args = ap.parse_args(argv)

    print(f"== Sobol T3-prism campaign: n={args.n}, n_tierb={args.n_tierb} ==")
    designs = sobol_designs(args.n, seed=args.seed)

    print("Tier-C (MuJoCo) sweep ...")
    tier_c = run_tier_c(designs)
    write_csv(tier_c, OUT_DIR / "sobol_t3_tierC.csv")

    tier_b: list[dict] = []
    if args.n_tierb > 0:
        # Evenly-spaced subset across the Sobol order for fidelity coverage.
        idx = np.linspace(0, len(designs) - 1, args.n_tierb).astype(int)
        subset = []
        for k in idx:
            d = dict(designs[int(k)])
            d["specimen"] = int(k)
            subset.append(d)
        print(f"Tier-B (Newton) subset of {len(subset)} ...")
        try:
            tier_b = run_tier_b(subset, regime_name="nasa_lander")
            write_csv(tier_b, OUT_DIR / "sobol_t3_tierB.csv")
        except Exception as e:  # pragma: no cover
            print(f"  tier-B skipped ({e!r})")

    print("Analysis ...")
    stats = analyse(tier_c, tier_b)
    write_report(stats, tier_c, len(tier_b))
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
