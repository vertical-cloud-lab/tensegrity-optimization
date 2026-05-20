"""Bridge from PR #30's BO campaign parameterization → MuJoCo Tier-C sim.

This module is a *drop-in replacement* for the analytical
``bo.tensegrity_campaign.simulate_specimen`` dummy evaluator.  It maps an
Ax parameterization (the design-space dict that ``AxClient.get_next_trial``
returns) to the three campaign objectives by running the existing Tier-C
MuJoCo regime simulation in ``simulations.run_regimes``:

    F_peak_N      — peak transmitted force = peak |a_z| (m/s²) × payload mass
    SEA_J_per_g   — specific energy absorbed = max tendon strain energy / cell mass
    eta           — compaction efficiency  = mean force / peak force over the
                    pulse window (so a square plateau ≈ 1.0; a triangle ≈ 0.5)

For each tier-C evaluation, we:
  1. Convert the BO parameters into a
     :class:`simulations.printable_design.PrintableDesign` and run
     ``check()``; if the design is infeasible (class-2 strut overlap, tendon
     unprintable, prestrain past TPU break, etc.) we return penalised
     objectives so Ax learns the feasibility boundary cheaply.
  2. Build an overridden :class:`simulations.regimes.Regime` whose tendon
     stiffness, strut radius, prestrain, and cell scale match the BO
     parameters; keep the regime's payload-mass + ΔV (so we are
     *evaluating* the design against a fixed loading scenario, not changing
     the loading along with the design).
  3. Call :func:`simulations.run_regimes.simulate` for one trial.
  4. Compute F_peak, SEA, eta from the returned time-series.

Only the T3-prism topology is implemented; other PR #24/PR #30 topologies
(truncated_octahedron, simplex_4_strut, stacked_prism) fall back to the
T3 mesher and emit a warning so the BO loop can still propose them but
their fitness reflects T3 physics.  This is exactly the scope @sgbaird
called out in PR comment 4500844340: "we'll probably run simulations for
each of samples from #30 beginning with a set of T3 structures (#35) that
we've already been able to print."

Multi-fidelity (Newton tier-B, PolyFEM tier-A) is stubbed by ``fidelity``
keyword — future work, but the function signature is forward-compatible
with Ax's ``MultiFidelityAcquisition`` (Frazier 2018).

Usage in ``bo/tensegrity_campaign.py``::

    from simulations.bo_evaluator import evaluate_design

    response = evaluate_design(parameterization, regime=CRUTCH, fidelity="C")
    # response = {"F_peak_N": float, "SEA_J_per_g": float, "eta": float}
"""
from __future__ import annotations

import math
import sys
import warnings
from dataclasses import replace
from pathlib import Path
from typing import Literal, Mapping

# Make this script importable both as ``simulations.bo_evaluator`` *and*
# directly (``python simulations/bo_evaluator.py``) regardless of CWD.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import numpy as np

from printable_design import (  # noqa: E402
    EQUILIBRIUM_TWIST,
    PLA,
    PrintableDesign,
    TPU85A,
)
from regimes import CRUTCH, NASA_LANDER, Regime  # noqa: E402

# Map PR #30 ``tpu_shore`` choices to Young's modulus (MPa).  TPU 95A is
# ~2× stiffer than 85A per unit cross-section.
_TPU_E_MPA: Mapping[str, float] = {"85A": TPU85A.young_MPa, "95A": 25.0}

# Penalty values returned for infeasible designs.  Chosen so they sit well
# *outside* the Ax objective thresholds in ``bo/tensegrity_campaign.py``
# (F_PEAK_THRESHOLD=2500 N, SEA_THRESHOLD=0.05 J/g, ETA_THRESHOLD=0.20),
# which makes them automatically pruned from the Pareto front while still
# being learnable as a boundary by the GP.
_INFEASIBLE_F_PEAK_N = 5.0e4   # ~5 t — definitely crushes the user
_INFEASIBLE_SEA_J_PER_G = 1.0e-6
_INFEASIBLE_ETA = 1.0e-3


def _topology_warning(topology: str) -> None:
    if topology not in {"t3_prism", None}:
        warnings.warn(
            f"bo_evaluator: topology={topology!r} not yet implemented; "
            "running T3-prism physics and flagging.  Per PR #35 the lab is "
            "starting BO with T3-prism prints, so this is fine for the "
            "first batch; revisit when topology mesher lands.",
            stacklevel=2,
        )


def parameterization_to_design(params: Mapping) -> PrintableDesign:
    """Map an Ax ``parameterization`` dict → :class:`PrintableDesign`.

    Only the geometric / printable axes from ``bo/tensegrity_campaign.py``
    PARAMETERS are consumed here; the rest (tiling, infill pattern, build
    orientation) are honoured by the surrounding evaluator wrapper, not by
    the printable-design model.
    """
    twist_rad = math.radians(float(params.get("twist_angle_deg",
                                              math.degrees(EQUILIBRIUM_TWIST))))
    height_m = float(params.get("strut_length_mm", 25.0)) * 1e-3
    # Circumscribing radius from the T-prism node coordinates: with the
    # default twist the strut-to-strut chord length is ~radius·√3, so for
    # a given strut length L the cell radius ≈ L / (√3 · (1 + cos(twist))).
    # In practice ``run_regimes`` carries its own radius_m; we anchor on
    # the regime's cell scale and only scale tendon stiffness.
    radius_m = float(params.get("cell_radius_mm",
                                params.get("strut_length_mm", 25.0) * 0.5)) * 1e-3
    return PrintableDesign(
        radius_m=radius_m,
        height_m=height_m,
        twist_rad=twist_rad,
        strut_diameter_m=float(params["strut_diameter_mm"]) * 1e-3,
        tendon_diameter_m=float(params["cable_diameter_mm"]) * 1e-3,
        prestrain=float(params.get("prestress_pct", 0.0)) / 100.0,
    )


def _t3_seed_designs() -> list[dict]:
    """Pre-printed T3 designs (PR #35) ready as the first BO batch.

    These are the parameterizations the lab can drop in as ``existing_data``
    when the BO campaign turns on, so Ax has real observations from the
    designs we already have hardware for.
    """
    base = {
        "topology": "t3_prism",
        "tiling": "1x1x1",
        "tpu_shore": "85A",
        "petg_infill_pattern": "gyroid",
        "build_orientation": "vertical",
        "struts_per_cell": 3,
    }
    return [
        # PR #35 default (scale 1.5×, cable_d 4.5 mm) — Bambu H2D print
        {**base, "strut_diameter_mm": 3.0, "strut_length_mm": 37.5,
         "cable_diameter_mm": 4.5, "twist_angle_deg": 30.0,
         "prestress_pct": 0.0, "petg_infill_pct": 100.0,
         "interface_wrap_thickness_mm": 0.8},
        # PR #35 baseline (scale 1.0×) for comparison
        {**base, "strut_diameter_mm": 3.0, "strut_length_mm": 25.0,
         "cable_diameter_mm": 3.0, "twist_angle_deg": 30.0,
         "prestress_pct": 0.0, "petg_infill_pct": 100.0,
         "interface_wrap_thickness_mm": 0.8},
        # Soft-tendon variant
        {**base, "strut_diameter_mm": 3.0, "strut_length_mm": 37.5,
         "cable_diameter_mm": 1.5, "twist_angle_deg": 30.0,
         "prestress_pct": 2.0, "petg_infill_pct": 100.0,
         "interface_wrap_thickness_mm": 0.8},
    ]


def evaluate_design(
    parameterization: Mapping,
    *,
    regime: Regime = CRUTCH,
    fidelity: Literal["C", "B", "A"] = "C",
) -> dict[str, float]:
    """Run one simulation and return PR #30's three BO objectives.

    Parameters
    ----------
    parameterization
        Ax parameter dict, schema = ``bo/tensegrity_campaign.PARAMETERS``.
    regime
        Loading scenario (CRUTCH or NASA_LANDER from
        ``simulations.regimes``).  Loading is *fixed* per BO campaign, not
        a design variable.
    fidelity
        "C" = MuJoCo (current default — cheap, ~1 s),
        "B" = Newton/Warp XPBD (planned, ~30 s),
        "A" = PolyFEM+IPC (planned, ~5 min).  Only "C" is implemented.

    Returns
    -------
    dict with keys ``"F_peak_N"``, ``"SEA_J_per_g"``, ``"eta"`` matching
    the ``F_PEAK``/``SEA``/``ETA`` outcome names in
    ``bo/tensegrity_campaign.py``.  Returns *penalised* values if the
    design is infeasible (class-2 strut overlap, unprintable tendon,
    prestrain past TPU yield, etc.).
    """
    if fidelity != "C":
        raise NotImplementedError(
            "Only Tier-C (MuJoCo) is wired in `bo_evaluator.evaluate_design`. "
            "Tier-B (Newton) and Tier-A (PolyFEM+IPC) are planned but require "
            "the per-cell tprism_mesh.py + newton_drop.py / polyfem_drop.py "
            "wrappers to accept an arbitrary PrintableDesign first; see "
            "simulations/bo_integration.md for the planned signature."
        )

    _topology_warning(parameterization.get("topology"))

    design = parameterization_to_design(parameterization)
    issues = design.check()
    if issues:
        warnings.warn(
            "bo_evaluator: infeasible design: " + "; ".join(issues),
            stacklevel=2,
        )
        return {
            "F_peak_N": _INFEASIBLE_F_PEAK_N,
            "SEA_J_per_g": _INFEASIBLE_SEA_J_PER_G,
            "eta": _INFEASIBLE_ETA,
        }

    # Import lazily so this module remains importable even when mujoco is
    # not installed (e.g., for ``edison_client``-only environments).
    from run_regimes import simulate  # noqa: E402

    overridden = replace(
        regime,
        radius_m=design.radius_m,
        height_m=design.height_m,
        strut_radius_m=design.strut_diameter_m * 0.5,
        cable_stiffness_Npm=float(design.cable_stiffness_Npm),
        cable_pretension_frac=float(design.prestrain),
    )
    res = simulate(overridden)

    peak_g = res["peak_g"]
    if not np.isfinite(peak_g):
        return {
            "F_peak_N": _INFEASIBLE_F_PEAK_N,
            "SEA_J_per_g": _INFEASIBLE_SEA_J_PER_G,
            "eta": _INFEASIBLE_ETA,
        }

    f_peak_N = peak_g * 9.81 * regime.payload_mass_kg

    # Cell mass for SEA: 3 PLA struts + 9 TPU tendons (cell-only; payload
    # is excluded so SEA reflects design intent).
    n = design.nodes
    L_strut = float(np.linalg.norm(n[0] - n[1]))      # any STRUTS[0]
    v_strut = 3 * math.pi * (design.strut_diameter_m / 2) ** 2 * L_strut
    L_tendon = float(np.linalg.norm(n[0] - n[3]))     # vertical tendon
    v_tendon = 9 * math.pi * (design.tendon_diameter_m / 2) ** 2 * L_tendon
    cell_mass_g = (v_strut * PLA.density_kgm3
                   + v_tendon * TPU85A.density_kgm3) * 1000.0
    sea_J_per_g = (res["sea_Jpkg"] * regime.payload_mass_kg) / max(cell_mass_g,
                                                                   1e-6)

    # Compaction efficiency: mean |a| over the half-peak pulse window
    # divided by the peak (1.0 = perfect rectangular plateau).
    az_g = np.abs(np.asarray(res["az_g"]))
    if az_g.size and peak_g > 0:
        above = az_g >= 0.5 * peak_g
        eta = float(az_g[above].mean() / peak_g) if above.any() else 0.0
    else:
        eta = 0.0

    return {
        "F_peak_N": float(f_peak_N),
        "SEA_J_per_g": float(sea_J_per_g),
        "eta": float(eta),
    }


if __name__ == "__main__":
    # Smoke-test against the three PR #35 T3 seed designs.
    for i, p in enumerate(_t3_seed_designs()):
        try:
            r = evaluate_design(p, regime=CRUTCH, fidelity="C")
            print(f"seed #{i}  F_peak={r['F_peak_N']:9.1f} N  "
                  f"SEA={r['SEA_J_per_g']:8.4f} J/g  eta={r['eta']:.3f}")
        except Exception as e:           # pragma: no cover - smoke test
            print(f"seed #{i}  FAILED: {e!r}")
