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

    params = normalize_parameterization(parameterization)
    design = parameterization_to_design(params)
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
    # divided by the peak (1.0 = perfect rectangular plateau).  Uses the
    # same (filtered) signal the peak was read from.
    az_g = np.abs(az_signed)
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
