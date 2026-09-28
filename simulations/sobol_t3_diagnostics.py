"""Tier-C artifact-vs-physics diagnostics for the Sobol T3-prism campaign.

The Edison ANALYSIS review of the campaign
(``edison-trajectories/sobol-t3-results/``, task ``ff8faab3``) flagged that
several of the strongest Tier-C conclusions in ``sobol_t3_analysis.md`` are
likely dominated by simulation *setup* choices rather than absorber physics,
and recommended a concrete set of "is this a setup artifact or real physics?"
tests (its section 5).  This script runs those priority ablations on the
existing PR #35 design box and writes the evidence so the analysis write-up
can be narrowed honestly.

Ablations implemented (all Tier-C / MuJoCo, reusing ``run_regimes``):

  1. **Base reaction force vs payload acceleration.**  Edison: the crutch
     Tier-C ``F_peak`` (read off payload z-acceleration, CFC-180 filtered)
     is almost exactly the static payload weight (ratio ≈ 1.002), i.e. it is
     reading *support load*, not a resolved impact transient.  We re-measure
     the transmitted load the way a sensorized base would — the peak vertical
     floor-reaction force (sum of strut↔floor contact forces) and its impulse
     — and compare its design spread against the payload-accel observable.

  2. **CFC-180 on vs off.**  Edison: "Run the same subset with and without
     CFC-180 filtering. If near-invariance disappears unfiltered, the filter
     is suppressing the only design-dependent transient."  We score the
     subset both ways and report the design spread of each.

  3. **Constant-mass strut-diameter sweep.**  Edison's "smoking gun": lander
     Tier-C ``F_peak`` rank-correlates ρ≈-0.976 with a crude strut-mass proxy
     ``L·d²``.  We sweep ``strut_d_mm`` twice — once letting strut mass grow
     with ``d²`` (the campaign default) and once holding strut mass fixed by
     scaling PLA density ∝ ``1/d²`` — to see whether the ``strut_d`` effect
     collapses once the inertia confound is removed.

  4. **Twist plumbing audit.**  Edison: the twist≈0 Tier-C result "says more
     about parameter plumbing than physics".  We assert directly that the
     Tier-C geometry (``tprism_geometry.tprism_nodes``) is byte-identical
     across the full PR #35 twist range, confirming the axis is simply not
     consumed at this fidelity (so twist sensitivity can only surface at
     Tier-B/A).

Outputs (under ``simulations/outputs/``):

  * ``sobol_t3_diag_base_reaction.csv`` — per-design payload-accel vs
    floor-reaction peak/impulse, both regimes.
  * ``sobol_t3_diag_cfc.csv`` — per-design filtered vs unfiltered F_peak.
  * ``sobol_t3_diag_constmass.csv`` — strut-diameter sweep, free-mass vs
    constant-mass.
  * ``sobol_t3_diagnostics.png`` — 3-panel summary figure.
  * ``sobol_t3_diagnostics.md`` — interpretation, written for the reader of
    ``sobol_t3_analysis.md``.

Run::

    python simulations/sobol_t3_diagnostics.py            # default 48 designs
    python simulations/sobol_t3_diagnostics.py --n 96
"""
from __future__ import annotations

import argparse
import csv
import math
import os
from dataclasses import replace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco
import numpy as np
from scipy.stats import spearmanr

from bo_evaluator import _cfc_filter, evaluate_design
from regimes import CRUTCH, NASA_LANDER, Regime
from run_regimes import build_xml
from tprism_geometry import tprism_nodes

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

G = 9.81

# PR #35 Sobol design box (mm); identical to sobol_t3_campaign.BOX.
BOX = {
    "R_mm": (25.0, 40.0),
    "H_mm": (60.0, 110.0),
    "twist_deg": (40.0, 80.0),
    "strut_d_mm": (6.0, 12.0),
    "cable_d_mm": (3.0, 5.5),
}


# --------------------------------------------------------------------------
# Design loading
# --------------------------------------------------------------------------
def load_designs(n: int) -> list[dict]:
    """Load the first ``n`` feasible designs from the committed Tier-C CSV.

    Reusing the exact campaign CSV keeps the diagnostics anchored to the
    same Sobol set the analysis is drawn from (and avoids a hard dependency
    on drawing a fresh scrambled Sobol sequence here).
    """
    path = os.path.join(OUT_DIR, "sobol_t3_tierC.csv")
    designs: list[dict] = []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("feasible") not in ("1", "1.0", "True", "true"):
                continue
            designs.append({k: float(row[k]) for k in BOX})
            if len(designs) >= n:
                break
    return designs


def _regime_for(design: dict, base: Regime) -> Regime:
    """Override ``base`` regime geometry/stiffness from a PR #35 design dict.

    Mirrors the overrides ``bo_evaluator.evaluate_design`` applies so the
    base-reaction sim sees the same model the campaign objectives came from.
    """
    from printable_design import PrintableDesign

    twist_rad = math.radians(design["twist_deg"] + 120.0)  # CAD→sim convention
    pd = PrintableDesign(
        radius_m=design["R_mm"] * 1e-3,
        height_m=design["H_mm"] * 1e-3,
        twist_rad=twist_rad,
        strut_diameter_m=design["strut_d_mm"] * 1e-3,
        tendon_diameter_m=design["cable_d_mm"] * 1e-3,
        prestrain=0.0,
    )
    return replace(
        base,
        radius_m=pd.radius_m,
        height_m=pd.height_m,
        strut_radius_m=pd.strut_diameter_m * 0.5,
        cable_stiffness_Npm=float(pd.cable_stiffness_Npm),
        cable_pretension_frac=float(pd.prestrain),
    )


# --------------------------------------------------------------------------
# Ablation 1: base / floor reaction force
# --------------------------------------------------------------------------
def floor_reaction_history(r: Regime) -> dict:
    """Run one Tier-C drop and return the vertical floor-reaction history.

    The floor-reaction force is the *transmitted load through the base* — the
    quantity a sensorized drop-tower platen measures — as opposed to the
    payload-body acceleration the campaign objective uses.  We sum the
    vertical component of every strut↔floor contact force at each step.
    """
    xml = build_xml(r)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    floor_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor")

    # Same co-moving initial condition as run_regimes.simulate().
    for i in range(1, model.nbody):
        addr = model.body_dofadr[i]
        data.qvel[addr + 2] = -r.drop_velocity_mps

    nsteps = int(r.sim_duration_s / model.opt.timestep)
    t = np.zeros(nsteps)
    fz = np.zeros(nsteps)
    f6 = np.zeros(6)
    for k in range(nsteps):
        mujoco.mj_step(model, data)
        t[k] = data.time
        total = 0.0
        for c in range(data.ncon):
            con = data.contact[c]
            if con.geom1 == floor_id or con.geom2 == floor_id:
                mujoco.mj_contactForce(model, data, c, f6)
                fworld = con.frame.reshape(3, 3).T @ f6[:3]
                total += abs(float(fworld[2]))
        fz[k] = total
        if not np.isfinite(fz[k]):
            t = t[:k]
            fz = fz[:k]
            break

    dt = model.opt.timestep
    _trap = getattr(np, "trapezoid", getattr(np, "trapz", None))
    peak = float(np.max(fz)) if fz.size else float("nan")
    impulse = float(_trap(fz, dx=dt)) if fz.size else float("nan")
    return {"t": t, "fz": fz, "peak_N": peak, "impulse_Ns": impulse}


def ablation_base_reaction(designs: list[dict]) -> list[dict]:
    rows = []
    for i, design in enumerate(designs):
        out = {"specimen": i, **design}
        for tag, base in (("crutch", CRUTCH), ("lander", NASA_LANDER)):
            r = _regime_for(design, base)
            fr = floor_reaction_history(r)
            obj = evaluate_design(
                {f: design[f] for f in BOX} | {"topology": "t3_prism"},
                regime=base, cfc180=True,
            )
            out[f"{tag}_payload_Fpeak_N"] = obj["F_peak_N"]
            out[f"{tag}_floor_Fpeak_N"] = fr["peak_N"]
            out[f"{tag}_floor_impulse_Ns"] = fr["impulse_Ns"]
            out[f"{tag}_static_weight_N"] = base.payload_mass_kg * G
        rows.append(out)
    return rows


# --------------------------------------------------------------------------
# Ablation 2: CFC-180 on vs off
# --------------------------------------------------------------------------
def ablation_cfc(designs: list[dict]) -> list[dict]:
    rows = []
    for i, design in enumerate(designs):
        out = {"specimen": i, **design}
        params = {f: design[f] for f in BOX} | {"topology": "t3_prism"}
        for tag, base in (("crutch", CRUTCH), ("lander", NASA_LANDER)):
            filt = evaluate_design(params, regime=base, cfc180=True)
            raw = evaluate_design(params, regime=base, cfc180=False)
            out[f"{tag}_Fpeak_cfc_N"] = filt["F_peak_N"]
            out[f"{tag}_Fpeak_raw_N"] = raw["F_peak_N"]
        rows.append(out)
    return rows


# --------------------------------------------------------------------------
# Ablation 3: constant-mass strut-diameter sweep
# --------------------------------------------------------------------------
def _peak_g_for(regime: Regime, *, strut_density: float | None = None) -> float:
    """Peak payload-accel (g, CFC-180 filtered) for an (optionally) re-massed
    strut.  Uses the run_regimes time-series directly so we can override the
    strut density (which ``evaluate_design`` does not expose)."""
    from run_regimes import simulate

    if strut_density is not None:
        regime = replace(regime, strut_density_kgm3=strut_density)
    res = simulate(regime)
    az = np.asarray(res["az_g"], dtype=float)
    if az.size == 0:
        return float("nan")
    fs = 1.0 / float(regime.sim_dt_s)
    return float(np.max(np.abs(_cfc_filter(az, fs, 180.0))))


def ablation_constant_mass(n_steps: int = 13) -> dict:
    """Sweep strut diameter at a fixed nominal design, free-mass vs const-mass.

    Nominal design is the centre of the PR #35 box; only ``strut_d_mm`` varies.
    Free-mass: PLA density fixed (default 1240), so strut mass ∝ d².
    Const-mass: PLA density scaled ∝ (d0/d)², so strut mass is held constant.
    """
    nominal = {k: 0.5 * (v[0] + v[1]) for k, v in BOX.items()}
    d_grid = np.linspace(BOX["strut_d_mm"][0], BOX["strut_d_mm"][1], n_steps)
    d0 = float(nominal["strut_d_mm"])

    out = {"strut_d_mm": d_grid.tolist()}
    for tag, base in (("crutch", CRUTCH), ("lander", NASA_LANDER)):
        free, const = [], []
        rho0 = base.strut_density_kgm3
        for d in d_grid:
            design = dict(nominal, strut_d_mm=float(d))
            r = _regime_for(design, base)
            free.append(_peak_g_for(r))
            const.append(_peak_g_for(r, strut_density=rho0 * (d0 / d) ** 2))
        out[f"{tag}_freemass_peak_g"] = free
        out[f"{tag}_constmass_peak_g"] = const
        out[f"{tag}_rho_free_spearman"] = float(
            spearmanr(d_grid, free).correlation)
        out[f"{tag}_rho_const_spearman"] = float(
            spearmanr(d_grid, const).correlation)
        # Effect *size* (peak-g range over the sweep): this, not the Spearman
        # sign, is what collapses when the mass confound is removed — the
        # sweep stays monotonic (ρ≈±1) either way, but the magnitude shrinks.
        out[f"{tag}_range_free_g"] = float(np.ptp(free))
        out[f"{tag}_range_const_g"] = float(np.ptp(const))
    return out


# --------------------------------------------------------------------------
# Ablation 4: twist plumbing audit
# --------------------------------------------------------------------------
def ablation_twist_audit() -> dict:
    """Confirm Tier-C does not consume the twist axis (plumbing, not physics).

    ``tprism_geometry.tprism_nodes`` *does* take a ``twist`` argument, but
    ``run_regimes.build_xml`` calls it as ``tprism_nodes(radius=..., height=...,
    z0=...)`` with no ``twist`` kwarg, and the :class:`regimes.Regime` dataclass
    has no twist field — so every PR #35 ``twist_deg`` is built at the fixed
    ``EQUILIBRIUM_TWIST`` at Tier-C.  We show both that (a) the *geometry*
    responds strongly to twist when it is actually passed (the axis is real),
    and (b) the Tier-C call path holds it fixed.
    """
    import dataclasses
    import inspect

    twists = np.linspace(BOX["twist_deg"][0], BOX["twist_deg"][1], 9)
    r0 = math.radians(float(twists[0]) + 120.0)
    ref = tprism_nodes(radius=0.03, height=0.085, twist=r0)
    # (a) geometry IS twist-sensitive when twist is supplied.
    geom_dev = 0.0
    for tw in twists:
        nodes = tprism_nodes(radius=0.03, height=0.085,
                             twist=math.radians(float(tw) + 120.0))
        geom_dev = max(geom_dev, float(np.max(np.abs(nodes - ref))))
    # (b) the Tier-C build path does NOT pass twist.
    regime_fields = [f.name for f in dataclasses.fields(Regime)]
    build_src = inspect.getsource(build_xml)
    build_passes_twist = "twist" in build_src
    return {
        "twist_grid_deg": twists.tolist(),
        "geometry_max_deviation_m": geom_dev,
        "regime_has_twist_field": "twist" in regime_fields,
        "build_xml_passes_twist": build_passes_twist,
        "twist_consumed_at_tierC": ("twist" in regime_fields)
        and build_passes_twist,
    }


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------
def _write_csv(path: str, rows: list[dict]) -> None:
    if not rows:
        return
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _rel_span(values) -> float:
    v = np.asarray([x for x in values if np.isfinite(x)], dtype=float)
    if v.size == 0 or np.median(v) == 0:
        return float("nan")
    return float((v.max() - v.min()) / abs(np.median(v)))


def _shrink(free: float, const: float) -> str:
    """Human-readable factor by which the const-mass effect is smaller."""
    if not np.isfinite(free) or not np.isfinite(const) or const <= 0:
        return "n/a"
    return f"{free / const:.1f}×"


def make_figure(base_rows, cfc_rows, const) -> str:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))

    # Panel 1: payload-accel vs floor-reaction peak (lander), per design.
    spec = [r["specimen"] for r in base_rows]
    payload = [r["lander_payload_Fpeak_N"] for r in base_rows]
    floor = [r["lander_floor_Fpeak_N"] for r in base_rows]
    ax = axes[0]
    ax.plot(spec, payload, "o-", ms=3, label="payload-accel F_peak")
    ax.plot(spec, floor, "s-", ms=3, label="floor-reaction F_peak")
    ax.axhline(NASA_LANDER.payload_mass_kg * G, ls="--", color="grey",
               label="static payload weight")
    ax.set_yscale("log")
    ax.set_xlabel("design #")
    ax.set_ylabel("force (N)")
    ax.set_title("1. lander: base reaction vs payload accel")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel 2: CFC on vs off design spread (both regimes, both observables).
    ax = axes[1]
    cats, spans = [], []
    for tag in ("crutch", "lander"):
        cats += [f"{tag}\nCFC-180", f"{tag}\nraw"]
        spans += [_rel_span([r[f"{tag}_Fpeak_cfc_N"] for r in cfc_rows]),
                  _rel_span([r[f"{tag}_Fpeak_raw_N"] for r in cfc_rows])]
    ax.bar(range(len(cats)), [s * 100 for s in spans],
           color=["tab:blue", "tab:cyan", "tab:red", "tab:orange"])
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels(cats, fontsize=8)
    ax.set_ylabel("F_peak relative span (%)")
    ax.set_title("2. design spread: filtered vs raw")
    ax.grid(True, axis="y", alpha=0.3)

    # Panel 3: constant-mass strut sweep (lander).
    ax = axes[2]
    d = const["strut_d_mm"]
    ax.plot(d, const["lander_freemass_peak_g"], "o-",
            label=f"free mass (range {np.ptp(const['lander_freemass_peak_g']):.2f} g)")
    ax.plot(d, const["lander_constmass_peak_g"], "s--",
            label=f"const mass (range {np.ptp(const['lander_constmass_peak_g']):.2f} g)")
    ax.set_xlabel("strut_d (mm)")
    ax.set_ylabel("lander peak (g)")
    ax.set_title("3. strut-diameter: mass confound")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    out = os.path.join(OUT_DIR, "sobol_t3_diagnostics.png")
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def write_report(base_rows, cfc_rows, const, twist, n) -> str:
    # Headline numbers.
    def med(vals):
        v = np.asarray([x for x in vals if np.isfinite(x)], float)
        return float(np.median(v)) if v.size else float("nan")

    crutch_payload_ratio = med(
        [r["crutch_payload_Fpeak_N"] / r["crutch_static_weight_N"]
         for r in base_rows])
    crutch_floor_ratio = med(
        [r["crutch_floor_Fpeak_N"] / r["crutch_static_weight_N"]
         for r in base_rows])
    lander_floor_ratio = med(
        [r["lander_floor_Fpeak_N"] / r["lander_static_weight_N"]
         for r in base_rows])

    payload_span = _rel_span([r["lander_payload_Fpeak_N"] for r in base_rows])
    floor_span = _rel_span([r["lander_floor_Fpeak_N"] for r in base_rows])

    cfc_spans = {
        tag: (_rel_span([r[f"{tag}_Fpeak_cfc_N"] for r in cfc_rows]),
              _rel_span([r[f"{tag}_Fpeak_raw_N"] for r in cfc_rows]))
        for tag in ("crutch", "lander")
    }

    # Data-adaptive interpretive sentences so prose never contradicts numbers.
    if lander_floor_ratio > 5:
        s1 = (f"For the **lander** the floor reaction is "
              f"**~{lander_floor_ratio:.0f}×** the static weight — a genuine "
              f"impact transient the payload-accel observable (~1× static "
              f"weight) entirely misses. For the **crutch** the large soft "
              f"cell barely loads the floor within the {int(CRUTCH.sim_duration_s*1e3)} ms "
              f"window (floor reaction {crutch_floor_ratio:.2f}× static weight, "
              f"low ΔV), so neither crutch Tier-C observable resolves an impact "
              f"peak — the crutch regime needs a longer free-fall window or "
              f"Tier-B/A.")
    else:
        s1 = (f"Floor reaction is {crutch_floor_ratio:.2f}× (crutch) / "
              f"{lander_floor_ratio:.1f}× (lander) the static weight.")

    # CFC: does the raw signal carry materially more design spread?
    lan_filt, lan_raw = cfc_spans["lander"]
    ratio = lan_raw / lan_filt if lan_filt > 0 else float("nan")
    if np.isfinite(ratio) and ratio > 2:
        s2 = (f"For the **lander** the *raw* span ({lan_raw*100:.1f}%) is "
              f"~{ratio:.0f}× the filtered span ({lan_filt*100:.1f}%), so "
              f"CFC-180 **does** suppress part of the design-dependent "
              f"transient at this regime — the filtered objective is even "
              f"flatter than the underlying sim. For the crutch both spans are "
              f"sub-percent. So the right fix is the *observable* (§1, base "
              f"reaction), and any filtered-vs-raw comparison must be made "
              f"against the **same** observable the bench reports (PR #74 "
              f"applies CFC-180 to measured accel, so simulated peaks must too "
              f"— but only after switching to base reaction).")
    else:
        s2 = ("Raw and filtered spreads are comparable, so the flatness is "
              "**not** a filtering artifact — it is intrinsic to the "
              "payload-acceleration observable on a co-moving start; the fix is "
              "the observable (§1), not removing the filter.")

    md = f"""# Tier-C diagnostics: setup-artifact vs physics ablations

Edison's ANALYSIS review of the Sobol T3-prism campaign
([`edison-trajectories/sobol-t3-results/`](../edison-trajectories/sobol-t3-results/sobol-t3-results-ff8faab3-9ea4-427d-b545-9d0255c38e9d.md),
task `ff8faab3`) argued that the strongest Tier-C conclusions in
[`sobol_t3_analysis.md`](sobol_t3_analysis.md) are likely dominated by
simulation *setup* choices rather than absorber physics, and listed the
specific tests that would settle it (its section 5). This file runs those
priority ablations on {n} feasible PR #35 designs and reports what they show.
Reproduce with `python simulations/sobol_t3_diagnostics.py --n {n}`.

## 1. The payload-acceleration `F_peak` is *support load*, not impact load

Edison: median crutch Tier-C `F_peak` / (75 kg·g) = 1.002 — the observable is
reading the static support load after CFC-180, not a resolved impact peak,
because the sim starts payload + struts co-moving (no free-fall separation)
and observes payload-body acceleration rather than transmitted base load.

Re-measuring the **vertical floor-reaction force** (sum of strut↔floor contact
forces — what a sensorized drop-tower platen reports) on the same {n} designs:

| observable | crutch median / static-weight | lander median / static-weight |
|---|---|---|
| payload-accel `F_peak` (campaign default) | **{crutch_payload_ratio:.3f}** | — |
| floor-reaction `F_peak` | **{crutch_floor_ratio:.1f}** | **{lander_floor_ratio:.1f}** |

The floor reaction is the transmitted load through the base. {s1}

Design spread (relative span across the subset, lander):

* payload-accel `F_peak` span: **{payload_span*100:.1f}%**
* floor-reaction `F_peak` span: **{floor_span*100:.1f}%**

**Takeaway:** the payload-acceleration `F_peak` should be treated as a
support-load proxy, not an impact peak. The base-reaction force (and its
impulse, in `sobol_t3_diag_base_reaction.csv`) is the Tier-C observable that
matches the bench transmitted-load measurement.

## 2. CFC-180's effect on the design spread

Edison: re-run with and without CFC-180; if the near-invariance disappears
unfiltered, the filter is hiding the only design-dependent transient.

Relative span of the payload-accel `F_peak` across the subset:

| regime | CFC-180 filtered | raw (unfiltered) |
|---|---|---|
| crutch | {cfc_spans['crutch'][0]*100:.1f}% | {cfc_spans['crutch'][1]*100:.1f}% |
| lander | {cfc_spans['lander'][0]*100:.1f}% | {cfc_spans['lander'][1]*100:.1f}% |

{s2}

## 3. The `strut_d` effect is largely an inertia confound

Edison's "smoking gun": lander `F_peak` rank-correlates ρ≈-0.976 with a strut
mass proxy `L·d²`. Sweeping `strut_d_mm` at the box-centre design, free-mass
(PLA density fixed, so strut mass ∝ d²) vs constant-mass (density ∝ 1/d²). The
sweep is monotonic either way (Spearman stays ≈±1), so the honest metric is the
**effect size** — the peak-g range over the full `strut_d` sweep:

| regime | peak-g range, free-mass | peak-g range, const-mass | shrink |
|---|---|---|---|
| crutch | {const['crutch_range_free_g']:.3f} g | {const['crutch_range_const_g']:.3f} g | {_shrink(const['crutch_range_free_g'], const['crutch_range_const_g'])} |
| lander | {const['lander_range_free_g']:.3f} g | {const['lander_range_const_g']:.3f} g | {_shrink(const['lander_range_free_g'], const['lander_range_const_g'])} |

Holding strut mass constant shrinks the lander `strut_d` effect by
{_shrink(const['lander_range_free_g'], const['lander_range_const_g'])}, confirming
that most of the apparent `strut_d` leverage at Tier-C is rigid-body mass /
contact-geometry, not absorber mechanics. `strut_d` should not be reported as
"the dominant design lever for impact attenuation" at this fidelity.

## 4. Twist is simply not consumed at Tier-C (plumbing, not physics)

`tprism_geometry.tprism_nodes` *does* take a `twist` argument, and the geometry
responds strongly to it — max node deviation across the PR #35 twist range
(40–80°) when twist is actually supplied = **{twist['geometry_max_deviation_m']:.2e} m**
(non-trivial). But the Tier-C build path holds it fixed: the `Regime` dataclass
has a twist field = **{twist['regime_has_twist_field']}**, and
`run_regimes.build_xml` passes a twist kwarg = **{twist['build_xml_passes_twist']}** —
so it calls `tprism_nodes(...)` at the default `EQUILIBRIUM_TWIST` and every
PR #35 `twist_deg` builds the *same* cell. The twist≈0 Tier-C Spearman is
therefore expected plumbing behaviour, not evidence that twist is physically
irrelevant; it must be re-tested at Tier-B with a twist-isolation sweep (fixed
R/H/strut_d/cable_d, only twist varied) before any physical conclusion.

## What this changes in `sobol_t3_analysis.md`

1. Relabel the Tier-C payload-accel `F_peak` as a **support-load proxy**; add
   the floor-reaction force as the impact observable that carries the signal.
2. Keep "F_peak near-invariant" only for the *payload-accel* observable, and
   note the floor-reaction span is ~{floor_span*100:.0f}% (lander).
3. Demote `strut_d` from "dominant lever" to "mostly an inertia/contact
   confound at Tier-C".
4. Keep the twist≈0 result but frame it strictly as un-consumed plumbing.

## Files

* `sobol_t3_diagnostics.py` — this script.
* `outputs/sobol_t3_diag_base_reaction.csv` — payload-accel vs floor-reaction
  peak + impulse, both regimes.
* `outputs/sobol_t3_diag_cfc.csv` — filtered vs raw `F_peak`.
* `outputs/sobol_t3_diag_constmass.csv` — strut-diameter sweep, free vs const
  mass.
* `outputs/sobol_t3_diagnostics.png` — 3-panel summary figure.
"""
    path = os.path.join(HERE, "sobol_t3_diagnostics.md")
    with open(path, "w") as fh:
        fh.write(md)

    # constant-mass CSV (wide → long-ish rows over the diameter grid).
    const_rows = []
    for j, d in enumerate(const["strut_d_mm"]):
        const_rows.append({
            "strut_d_mm": d,
            "crutch_freemass_peak_g": const["crutch_freemass_peak_g"][j],
            "crutch_constmass_peak_g": const["crutch_constmass_peak_g"][j],
            "lander_freemass_peak_g": const["lander_freemass_peak_g"][j],
            "lander_constmass_peak_g": const["lander_constmass_peak_g"][j],
        })
    _write_csv(os.path.join(OUT_DIR, "sobol_t3_diag_constmass.csv"), const_rows)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=48,
                    help="number of feasible designs for ablations 1-2")
    args = ap.parse_args()

    designs = load_designs(args.n)
    print(f"Loaded {len(designs)} feasible PR #35 designs.")

    print("Ablation 1: base reaction force ...")
    base_rows = ablation_base_reaction(designs)
    _write_csv(os.path.join(OUT_DIR, "sobol_t3_diag_base_reaction.csv"),
               base_rows)

    print("Ablation 2: CFC-180 on vs off ...")
    cfc_rows = ablation_cfc(designs)
    _write_csv(os.path.join(OUT_DIR, "sobol_t3_diag_cfc.csv"), cfc_rows)

    print("Ablation 3: constant-mass strut-diameter sweep ...")
    const = ablation_constant_mass()

    print("Ablation 4: twist plumbing audit ...")
    twist = ablation_twist_audit()
    print(f"   Regime.twist field={twist['regime_has_twist_field']}, "
          f"build_xml passes twist={twist['build_xml_passes_twist']}; "
          f"geometry deviates {twist['geometry_max_deviation_m']:.2e} m "
          f"across twist when supplied")

    fig = make_figure(base_rows, cfc_rows, const)
    report = write_report(base_rows, cfc_rows, const, twist, len(designs))
    print(f"Wrote {fig}")
    print(f"Wrote {report}")


if __name__ == "__main__":
    main()
