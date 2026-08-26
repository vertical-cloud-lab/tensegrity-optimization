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

Both BO parameter schemas are accepted: the PR #30 scaffold
(``strut_diameter_mm``/``strut_length_mm``/``cable_diameter_mm``/
``twist_angle_deg``/``prestress_pct``) and the PR #35 T3-prism batch
(``R_mm``/``H_mm``/``twist_deg``/``strut_d_mm``/``cable_d_mm`` from
``bo/t3_prism_sobol_batch.py``).  See :func:`normalize_parameterization`.

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


# PR #35 (``bo/t3_prism_sobol_batch.py``) uses real-mm, post-scale T3-prism
# parameter names that differ from the PR #30 scaffold.  Map them onto the
# canonical PR #30 names so a single evaluator serves both campaigns.
_PR35_TO_PR30: Mapping[str, str] = {
    "R_mm": "cell_radius_mm",
    "H_mm": "strut_length_mm",
    "twist_deg": "twist_angle_deg",
    "strut_d_mm": "strut_diameter_mm",
    "cable_d_mm": "cable_diameter_mm",
}


def normalize_parameterization(params: Mapping) -> dict:
    """Return a copy of ``params`` keyed by the canonical PR #30 names.

    Accepts either the PR #30 ``bo/tensegrity_campaign.py`` schema
    (``strut_diameter_mm``/``strut_length_mm``/``cable_diameter_mm``/
    ``twist_angle_deg``) *or* the PR #35 ``bo/t3_prism_sobol_batch.py``
    schema (``R_mm``/``H_mm``/``twist_deg``/``strut_d_mm``/``cable_d_mm``).
    PR #35 names take precedence when both are present.  For the PR #35
    schema ``H_mm`` is the full cell height and ``R_mm`` the circumscribing
    radius, so we map them straight onto the PrintableDesign geometry rather
    than the radius≈L/2 heuristic the PR #30 path falls back to.

    Twist convention: the CAD/PR #35 strut connectivity is ``B_i → T_i`` with
    an equilibrium twist of 60° (``cad/t3-prism/t3-prism.scad``), whereas the
    simulator's :func:`tprism_geometry.tprism_nodes` uses ``B_i → T_{i+1}``
    with an equilibrium twist of 150°.  The two describe the *same* prism when
    ``sim_twist = scad_twist + 120°`` (the +120° accounts for the
    next-vertex strut connectivity), so a PR #35 ``twist_deg`` is offset by
    +120° as it is mapped onto the simulator's ``twist_angle_deg``.  Without
    this offset every printed T3-prism (PR #35 twist ∈ [40°, 80°]) would be
    mis-flagged class-2 because the struts appear to cross the central axis.
    """
    out = dict(params)
    for pr35, pr30 in _PR35_TO_PR30.items():
        if pr35 in params:
            value = float(params[pr35])
            if pr35 == "twist_deg":
                value += 120.0  # CAD (B_i→T_i) → sim (B_i→T_{i+1}) convention
            out[pr30] = value
    return out


def parameterization_to_design(params: Mapping) -> PrintableDesign:
    """Map an Ax ``parameterization`` dict → :class:`PrintableDesign`.

    Only the geometric / printable axes from ``bo/tensegrity_campaign.py``
    (PR #30) or ``bo/t3_prism_sobol_batch.py`` (PR #35) are consumed here;
    the rest (tiling, infill pattern, build orientation) are honoured by the
    surrounding evaluator wrapper, not by the printable-design model.
    """
    params = normalize_parameterization(params)
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


def cell_geometry_metrics(design: PrintableDesign) -> dict[str, float]:
    """Mass / envelope / footprint of a printable cell (no simulation).

    These are the size descriptors the fairness analysis
    (``fair_evaluation_analysis.md``) showed float 4–6× across the PR #35 box,
    so the hybrid campaign needs them to (a) hold cell mass constant by
    construction — Route A — and (b) constrain envelope volume / footprint —
    Route B.  All are derivable from the :class:`PrintableDesign` geometry, so
    they add no simulation cost.

      ``cell_mass_g``   3 PLA struts + 9 TPU tendons (cell only; payload excluded,
                        the 9-tendon family approximated at the vertical-cable
                        length, the longest, matching the SEA denominator).
      ``envelope_cm3``  circumscribing cylinder ``π R² H``.
      ``footprint_mm2`` strut-tip ground-contact area ``3 · π (strut_d/2)²``.
    """
    L_strut = design.strut_length_m
    v_strut = 3.0 * math.pi * (design.strut_diameter_m / 2.0) ** 2 * L_strut
    n = design.nodes
    L_tendon = float(np.linalg.norm(n[0] - n[3]))     # vertical cable (longest)
    v_tendon = 9.0 * math.pi * (design.tendon_diameter_m / 2.0) ** 2 * L_tendon
    cell_mass_g = (v_strut * PLA.density_kgm3
                   + v_tendon * TPU85A.density_kgm3) * 1000.0
    envelope_cm3 = math.pi * design.radius_m ** 2 * design.height_m * 1e6
    footprint_mm2 = 3.0 * math.pi * (design.strut_diameter_m / 2.0) ** 2 * 1e6
    return {"cell_mass_g": float(cell_mass_g),
            "envelope_cm3": float(envelope_cm3),
            "footprint_mm2": float(footprint_mm2)}


# Arbitrary anchor radius for the shape-ratio prototype; it cancels in the
# cube-root scale solve below, so its value does not affect the result.
_SHAPE_RATIO_ANCHOR_R_M = 0.03


def design_from_shape_ratios(
    *,
    mass_g: float,
    h_over_r: float,
    h_over_strut_d: float,
    cable_over_strut_d: float,
    twist_deg: float,
    prestrain: float = 0.0,
) -> PrintableDesign:
    """Route-A constant-mass manifold: a scale-free shape at a fixed cell mass.

    The fairness analysis (``fair_evaluation_analysis.md`` §3, Route A) calls for
    re-parameterising the search onto dimensionless shape ratios with the binding
    budget (cell mass) held constant by construction, so the optimiser can only
    trade *shape*, never *size* — which is what removes the 6.2× size confound.

    Build the prism shape from the dimensionless ratios

        ``h_over_r``           aspect ratio ``H / R``
        ``h_over_strut_d``     strut slenderness ``H / strut_d``
        ``cable_over_strut_d`` tendon-to-strut diameter ratio ``cable_d / strut_d``
        ``twist_deg``          CAD/PR #35 equilibrium twist (offset +120° to the
                               simulator convention, as in
                               :func:`normalize_parameterization`)

    then solve the *single* overall scale so the cell mass equals ``mass_g``
    exactly.  Because every length — node radii/heights *and* the strut/tendon
    diameters — scales together, the cell mass is homogeneous of degree three in
    the scale, so the solve is the closed-form cube root
    ``s = (mass_g / m_proto)**(1/3)``.
    """
    twist_rad = math.radians(float(twist_deg) + 120.0)  # CAD→sim convention
    r0 = _SHAPE_RATIO_ANCHOR_R_M
    h0 = float(h_over_r) * r0
    strut_d0 = h0 / float(h_over_strut_d)
    cable_d0 = float(cable_over_strut_d) * strut_d0
    proto = PrintableDesign(
        radius_m=r0, height_m=h0, twist_rad=twist_rad,
        strut_diameter_m=strut_d0, tendon_diameter_m=cable_d0,
        prestrain=float(prestrain))
    m_proto = cell_geometry_metrics(proto)["cell_mass_g"]
    scale = (float(mass_g) / m_proto) ** (1.0 / 3.0) if m_proto > 0 else 1.0
    return PrintableDesign(
        radius_m=r0 * scale, height_m=h0 * scale, twist_rad=twist_rad,
        strut_diameter_m=strut_d0 * scale, tendon_diameter_m=cable_d0 * scale,
        prestrain=float(prestrain))


def design_to_shape_ratios(design: PrintableDesign) -> dict[str, float]:
    """Inverse of :func:`design_from_shape_ratios` (mass + the four ratios).

    Used to project the already-printed PR #35 seed cells onto the constant-mass
    manifold so the hybrid campaign can warm-start from real hardware shapes.
    ``twist_deg`` is returned in the CAD/PR #35 convention (the +120° simulator
    offset removed).
    """
    metrics = cell_geometry_metrics(design)
    return {
        "mass_g": metrics["cell_mass_g"],
        "h_over_r": design.height_m / design.radius_m,
        "h_over_strut_d": design.height_m / design.strut_diameter_m,
        "cable_over_strut_d": design.tendon_diameter_m / design.strut_diameter_m,
        "twist_deg": math.degrees(design.twist_rad) - 120.0,
    }


def base_reaction_peak_N(regime: Regime, *, cfc180: bool = True) -> float:
    """Peak vertical floor-reaction force for one Tier-C drop of ``regime``.

    Route B of the fairness fix replaces the payload-acceleration ``F_peak``
    (a support-load proxy at Tier-C; see ``sobol_t3_diagnostics.md``) with the
    *transmitted load through the base* — the quantity a sensorized drop-tower
    platen measures.  We sum the vertical component of every strut↔floor contact
    force at each step and return the (optionally CFC-180 filtered) peak.

    This mirrors ``sobol_t3_diagnostics.floor_reaction_history`` but is kept here
    so the evaluator stays self-contained (no matplotlib import).  It runs a
    second short MuJoCo drop, so it roughly doubles the per-design cost; callers
    opt in via ``base_reaction=True``.
    """
    import mujoco  # noqa: E402  (lazy: evaluator stays importable without GL)

    from run_regimes import build_xml  # noqa: E402

    model = mujoco.MjModel.from_xml_string(build_xml(regime))
    data = mujoco.MjData(model)
    floor_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor")
    # Same co-moving initial condition as run_regimes.simulate().
    for i in range(1, model.nbody):
        addr = model.body_dofadr[i]
        data.qvel[addr + 2] = -regime.drop_velocity_mps
    nsteps = int(regime.sim_duration_s / model.opt.timestep)
    fz = np.zeros(nsteps)
    f6 = np.zeros(6)
    for k in range(nsteps):
        mujoco.mj_step(model, data)
        total = 0.0
        for c in range(data.ncon):
            con = data.contact[c]
            if con.geom1 == floor_id or con.geom2 == floor_id:
                mujoco.mj_contactForce(model, data, c, f6)
                fworld = con.frame.reshape(3, 3).T @ f6[:3]
                total += abs(float(fworld[2]))
        fz[k] = total
        if not np.isfinite(fz[k]):
            fz = fz[:k]
            break
    if not fz.size:
        return float("nan")
    if cfc180:
        fz = _cfc_filter(fz, 1.0 / float(regime.sim_dt_s), cfc=180.0)
    return float(np.max(np.abs(fz)))


def _t3_seed_designs() -> list[dict]:
    """Pre-printed T3 designs (PR #35) ready as the first BO batch.

    These are the parameterizations the lab can drop in as ``existing_data``
    when the BO campaign turns on, so Ax has real observations from the
    designs we already have hardware for.  Expressed in the PR #35
    ``bo/t3_prism_sobol_batch.py`` schema (real mm, post-scale) so the cell
    geometry matches the printed parts exactly.
    """
    base = {
        "topology": "t3_prism",
        "tiling": "1x1x1",
        "tpu_shore": "85A",
        "build_orientation": "vertical",
        "struts_per_cell": 3,
    }
    return [
        # PR #35 production target (scale 1.5×): R=37.5, H=105, cable_d 4.5 mm
        {**base, "R_mm": 37.5, "H_mm": 105.0, "twist_deg": 60.0,
         "strut_d_mm": 9.0, "cable_d_mm": 4.5, "prestress_pct": 0.0},
        # PR #35 baseline (scale 1.0×): R=25, H=70, cable_d 3.0 mm
        {**base, "R_mm": 25.0, "H_mm": 70.0, "twist_deg": 60.0,
         "strut_d_mm": 6.0, "cable_d_mm": 3.0, "prestress_pct": 0.0},
        # High-twist / fat-cable corner of the PR #35 Sobol box
        {**base, "R_mm": 40.0, "H_mm": 110.0, "twist_deg": 80.0,
         "strut_d_mm": 12.0, "cable_d_mm": 5.5, "prestress_pct": 2.0},
    ]


def _cfc_filter(signal: np.ndarray, fs_hz: float, cfc: float = 180.0) -> np.ndarray:
    """SAE J211 CFC digital filter (zero-phase, forward + backward pass).

    Implements the Butterworth filter specified in SAE J211-1 appendix C —
    the same channel-frequency-class (CFC) filter the drop-tower
    accelerometer pipeline applies (PR #74).  A single 2nd-order section
    (biquad) is run forward and then backward, which both cancels phase
    distortion and yields an effective 4th-order zero-phase response
    (i.e. the "4-pole phaseless" filter the standard calls for).  Filtering
    the simulated acceleration before extracting peak force puts the cheap
    tier-C objective in the *same* processed space as the bench
    measurement, which is what lets simulated and measured rows share one
    GP/Ax model (Edison ANALYSIS task 4e74f66c, rec #1).

    Pure NumPy so the bridge keeps no SciPy dependency.

    Parameters
    ----------
    signal : 1-D acceleration time-history (any consistent unit).
    fs_hz  : sampling rate of ``signal`` in Hz.
    cfc    : channel frequency class (180 for CFC-180).
    """
    x = np.asarray(signal, dtype=float)
    # Need a few samples for the biquad warm-up / two-pass edge handling.
    if x.size < 7 or not np.isfinite(fs_hz) or fs_hz <= 0:
        return x
    T = 1.0 / fs_hz
    # 2.0775 = empirical SAE J211-1 appendix C constant converting the CFC
    # value (Hz) to the filter's -3 dB design frequency for the 4-pole
    # phaseless Butterworth.
    wd = 2.0 * math.pi * cfc * 2.0775
    wa = math.tan(wd * T / 2.0)
    denom = 1.0 + math.sqrt(2.0) * wa + wa * wa
    b0 = wa * wa / denom
    b1 = 2.0 * b0
    b2 = b0
    a1 = -2.0 * (wa * wa - 1.0) / denom
    a2 = (-1.0 + math.sqrt(2.0) * wa - wa * wa) / denom

    def _pass(seq: np.ndarray) -> np.ndarray:
        y = np.empty_like(seq)
        for i in range(seq.size):
            xi = seq[i]
            xi1 = seq[i - 1] if i >= 1 else seq[0]
            xi2 = seq[i - 2] if i >= 2 else seq[0]
            yi1 = y[i - 1] if i >= 1 else seq[0]
            yi2 = y[i - 2] if i >= 2 else seq[0]
            y[i] = b0 * xi + b1 * xi1 + b2 * xi2 + a1 * yi1 + a2 * yi2
        return y

    forward = _pass(x)
    backward = _pass(forward[::-1])[::-1]
    return backward


def evaluate_design(
    parameterization: Mapping,
    *,
    regime: Regime = CRUTCH,
    fidelity: Literal["C", "B", "A"] = "C",
    cfc180: bool = True,
    base_reaction: bool = False,
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
    cfc180
        When True (default), the simulated axial acceleration is passed
        through an SAE J211 CFC-180 filter before peak force / eta are
        extracted, matching the drop-tower accelerometer pipeline (PR #74)
        so simulated and measured objectives live in the same processed
        space.  Set False to read raw (unfiltered) peaks.
    base_reaction
        When True, also run the floor-reaction drop and add
        ``"F_base_peak_N"`` (the transmitted-load observable Route B of the
        fairness fix prefers over the payload-accel ``F_peak``; see
        ``fair_evaluation_analysis.md`` and ``sobol_t3_diagnostics.md``).
        Roughly doubles the per-design cost.

    Returns
    -------
    dict with keys ``"F_peak_N"``, ``"SEA_J_per_g"``, ``"eta"`` matching
    the ``F_PEAK``/``SEA``/``ETA`` outcome names in
    ``bo/tensegrity_campaign.py``, plus the size descriptors
    ``"cell_mass_g"``, ``"envelope_cm3"``, ``"footprint_mm2"`` and the
    volumetric SEA ``"SEA_J_per_cm3"`` (used by the hybrid fair campaign for
    Route-B constraints / intensive objectives), and ``"F_base_peak_N"`` when
    ``base_reaction=True``.  Returns *penalised* objective values if the design
    is infeasible (class-2 strut overlap, unprintable tendon, prestrain past
    TPU yield, etc.); the size descriptors are still reported.
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
    params = normalize_parameterization(parameterization)
    design = parameterization_to_design(params)
    return evaluate_printable_design(
        design, regime=regime, fidelity=fidelity, cfc180=cfc180,
        base_reaction=base_reaction)


def _penalised(design: PrintableDesign, base_reaction: bool) -> dict[str, float]:
    """Penalised objectives for an infeasible design (size descriptors kept)."""
    out = {
        "F_peak_N": _INFEASIBLE_F_PEAK_N,
        "SEA_J_per_g": _INFEASIBLE_SEA_J_PER_G,
        "SEA_J_per_cm3": _INFEASIBLE_SEA_J_PER_G,
        "eta": _INFEASIBLE_ETA,
    }
    out.update(cell_geometry_metrics(design))
    if base_reaction:
        out["F_base_peak_N"] = _INFEASIBLE_F_PEAK_N
    return out


def evaluate_printable_design(
    design: PrintableDesign,
    *,
    regime: Regime = CRUTCH,
    fidelity: Literal["C", "B", "A"] = "C",
    cfc180: bool = True,
    base_reaction: bool = False,
) -> dict[str, float]:
    """Score an explicit :class:`PrintableDesign` (Tier-C MuJoCo).

    This is the core evaluator shared by :func:`evaluate_design` (which builds
    the design from an Ax box parameterization) and the hybrid constant-mass
    campaign (which builds the design from shape ratios via
    :func:`design_from_shape_ratios`).  See :func:`evaluate_design` for the
    return schema.
    """
    if fidelity != "C":
        raise NotImplementedError("Only Tier-C is implemented (see evaluate_design).")

    metrics = cell_geometry_metrics(design)

    issues = design.check()
    if issues:
        warnings.warn(
            "bo_evaluator: infeasible design: " + "; ".join(issues),
            stacklevel=2,
        )
        return _penalised(design, base_reaction)

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

    # SAE J211 CFC-180 filter the acceleration to match the drop-tower
    # accelerometer pipeline (PR #74); peak and eta are then read off the
    # same processed signal the bench reports.
    az_signed = np.asarray(res["az_g"], dtype=float)
    if cfc180 and az_signed.size:
        fs_hz = 1.0 / float(regime.sim_dt_s)
        az_signed = _cfc_filter(az_signed, fs_hz, cfc=180.0)
        peak_g = float(np.max(np.abs(az_signed)))
    else:
        peak_g = res["peak_g"]

    if not np.isfinite(peak_g):
        return _penalised(design, base_reaction)

    f_peak_N = peak_g * 9.81 * regime.payload_mass_kg

    # SEA: peak elastic strain energy / cell mass (cell-only; payload excluded
    # so SEA reflects design intent).  ``SEA_J_per_cm3`` is the same numerator
    # over the envelope volume — the volumetric budget the lander also has.
    cell_mass_g = metrics["cell_mass_g"]
    abs_energy_J = res["sea_Jpkg"] * regime.payload_mass_kg
    sea_J_per_g = abs_energy_J / max(cell_mass_g, 1e-6)
    sea_J_per_cm3 = abs_energy_J / max(metrics["envelope_cm3"], 1e-6)

    # Compaction efficiency: mean |a| over the half-peak pulse window
    # divided by the peak (1.0 = perfect rectangular plateau).  Uses the
    # same (filtered) signal the peak was read from.
    az_g = np.abs(az_signed)
    if az_g.size and peak_g > 0:
        above = az_g >= 0.5 * peak_g
        eta = float(az_g[above].mean() / peak_g) if above.any() else 0.0
    else:
        eta = 0.0

    out = {
        "F_peak_N": float(f_peak_N),
        "SEA_J_per_g": float(sea_J_per_g),
        "SEA_J_per_cm3": float(sea_J_per_cm3),
        "eta": float(eta),
        **metrics,
    }
    if base_reaction:
        out["F_base_peak_N"] = base_reaction_peak_N(overridden, cfc180=cfc180)
    return out


def evaluate_batch_csv(
    csv_path,
    *,
    regime: Regime = CRUTCH,
    fidelity: Literal["C", "B", "A"] = "C",
    cfc180: bool = True,
) -> list[dict]:
    """Evaluate every row of a PR #35 ``t3-prism-bo-batch.csv`` design batch.

    The batch generator in ``bo/t3_prism_sobol_batch.py`` emits the Sobol
    design set but reports *no* objectives back to Ax.  This reads that CSV,
    runs the Tier-C sim for each specimen, and returns the design row merged
    with its ``{F_peak_N, SEA_J_per_g, eta}`` so the values can be attached to
    the AxClient (``attach_trial`` + ``complete_trial``) as a cheap simulated
    prior before the physical drops are run.
    """
    import csv as _csv

    rows: list[dict] = []
    with open(csv_path, newline="") as fh:
        for raw in _csv.DictReader(fh):
            params = {k: v for k, v in raw.items() if v not in (None, "")}
            # Coerce the numeric design columns; leave categoricals as str.
            for key in ("R_mm", "H_mm", "twist_deg", "strut_d_mm",
                        "cable_d_mm", "strut_diameter_mm", "strut_length_mm",
                        "cable_diameter_mm", "twist_angle_deg", "prestress_pct"):
                if key in params:
                    try:
                        params[key] = float(params[key])
                    except (TypeError, ValueError):
                        pass
            obj = evaluate_design(params, regime=regime, fidelity=fidelity,
                                  cfc180=cfc180)
            rows.append({**raw, **obj})
    return rows


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Tier-C MuJoCo evaluator for the tensegrity BO campaign "
                    "(PR #30 / PR #35 schemas).")
    parser.add_argument(
        "--batch-csv", default=None,
        help="Path to a PR #35 t3-prism-bo-batch.csv; evaluate every row.")
    parser.add_argument(
        "--regime", choices=["crutch_tip", "nasa_lander"],
        default="crutch_tip", help="Fixed loading scenario.")
    parser.add_argument(
        "--raw-peak", action="store_true",
        help="Read raw (unfiltered) peak instead of SAE J211 CFC-180.")
    args = parser.parse_args()

    _regime = NASA_LANDER if args.regime == "nasa_lander" else CRUTCH
    _cfc180 = not args.raw_peak

    if args.batch_csv:
        results = evaluate_batch_csv(args.batch_csv, regime=_regime,
                                     cfc180=_cfc180)
        for i, r in enumerate(results):
            print(f"row #{i}  F_peak={float(r['F_peak_N']):9.1f} N  "
                  f"SEA={float(r['SEA_J_per_g']):8.4f} J/g  "
                  f"eta={float(r['eta']):.3f}")
    else:
        # Smoke-test against the three PR #35 T3 seed designs.
        for i, p in enumerate(_t3_seed_designs()):
            try:
                r = evaluate_design(p, regime=_regime, fidelity="C",
                                    cfc180=_cfc180)
                print(f"seed #{i}  F_peak={r['F_peak_N']:9.1f} N  "
                      f"SEA={r['SEA_J_per_g']:8.4f} J/g  eta={r['eta']:.3f}")
            except Exception as e:        # pragma: no cover - smoke test
                print(f"seed #{i}  FAILED: {e!r}")
