"""Tensegrity-inspired energy-absorber Bayesian-optimization campaign.

This module is the *customized* companion to ``bo/tensegrity_bo.py``. The
latter is the unmodified, regenerable honegumi scaffold; this file replaces
honegumi's Branin placeholder with the design variables and objectives that
are consistent across the project's existing artifacts:

* ``proposal.tex`` (BYU MRG)
    "strut diameter and length, tension-element cross-section (TPU),
    connectivity topology, and unit-cell tiling"; "peak transmitted force,
    specific energy absorption (SEA), and compaction efficiency".
* ``idetc-abstract.tex`` (ASME IDETC-CIE 2026, accepted)
    Continuous strut diameter / length and TPU cross-section, an integer
    strut count per unit cell, and categorical topology + tiling. Three
    measured outcomes: F_peak, SEA, eta. Multi-objective BO via qNEHVI.
* ``nasa-space-grant/proposal.tex`` (BYU NASA Space Grant)
    "strut diameter and length, TPU cross-section, tiling and topology",
    minimize peak transmitted force at a target SEA.
* PR #24 — TPU + PETG variable scoping (Edison LITERATURE_HIGH task
    ``5ae24eaf-…``). Drives the design space here:
    - **PETG** struts (not PLA) + **TPU 85A/95A** tendons on a Bambu H2D.
    - Bounds from the Pajunen / Khatri / León-Calero / Bustihan literature
      table in ``edison-trajectories/tpu-petg-bo-variables-5ae24eaf-….md``.
    - Topologies are the four "defensible seed families" called out there:
      truncated octahedron (Pajunen), 4-strut simplex, T3 prism, stacked
      prism. Tilings extended to include 1×1×2 and 3×3×2 per the same table.
    - Adds twist angle, prestress, PETG infill %, PETG infill pattern,
      TPU shore, interface wrap thickness, and build orientation as
      first-class BO variables (geometric + material/print).

Per the abstract, the source of truth at run time is the *physical
experiment*. Until that data starts arriving, this module ships an
**analytical dummy objective** (``simulate_specimen``) that returns
physically plausible F_peak / SEA / eta from the design vector. The dummy is
documented inline so it can be replaced wholesale by a call into the
experimental data layer (or an FE surrogate) without touching the BO loop.

Run it with::

    pip install -r bo/requirements.txt
    MPLBACKEND=Agg python bo/tensegrity_campaign.py
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd
from ax.service.ax_client import AxClient, ObjectiveProperties

logging.getLogger("ax").setLevel(logging.WARNING)

# Campaign-loop knobs. Tweak in-place; this script is intentionally a flat,
# top-to-bottom recipe rather than a CLI.
N_ITERATIONS = 5  # bump to ~21 once the dummy evaluator is replaced
BATCH_SIZE = 2  # parallel trials per BO step (matches IDETC abstract)
SEED = 0

# ----------------------------------------------------------------------------
# Objective and parameter specification
# ----------------------------------------------------------------------------

#: Objective metric names (used both in the search space and the plotting code).
F_PEAK = "F_peak_N"  # peak transmitted force during impact, Newtons (minimize)
SEA = "SEA_J_per_g"  # specific energy absorption, J/g (maximize)
ETA = "eta"  # compaction efficiency, dimensionless (maximize)

#: Reference thresholds for the multi-objective hypervolume calculation. These
#: act as the "worst tolerable" outcomes that define the reference point. Real
#: numbers should be chosen from pilot data; these defaults span the feasible
#: range of the dummy objective so the optimizer has a non-degenerate
#: hypervolume to chase from trial 1.
F_PEAK_THRESHOLD = 2500.0  # N — anything beyond this would crush the user
SEA_THRESHOLD = 0.05  # J/g — minimal acceptable energy absorption per mass
ETA_THRESHOLD = 0.20  # — minimal acceptable load-limiting plateau quality

#: Connectivity topologies — the four "defensible seed families" called out
#: in PR #24's Edison literature table (5ae24eaf): Pajunen-style truncated
#: octahedron (strongest EA evidence), 4-strut simplex, T3 prism, and the
#: practical stacked-prism columnar absorber.
TOPOLOGIES: tuple[str, ...] = (
    "truncated_octahedron",
    "simplex_4_strut",
    "t3_prism",
    "stacked_prism",
)

#: Unit-cell tiling patterns. Extended over the IDETC abstract set with
#: 1×1×2 and 3×3×2 per the PR #24 recommended categorical list while staying
#: within H2D build envelope / undergrad print-time budget.
TILINGS: tuple[str, ...] = ("1x1x1", "1x1x2", "2x2x1", "2x2x2", "3x3x2")

#: TPU shore-hardness grades supported by the León-Calero / Bustihan studies
#: cited in PR #24. The lab default is 85A (NinjaFlex-class).
TPU_SHORES: tuple[str, ...] = ("85A", "95A")

#: PETG infill pattern — common slicer choices with distinct anisotropy and
#: crush behaviour (PR #24 Edison table).
PETG_INFILL_PATTERNS: tuple[str, ...] = ("rectilinear", "grid", "gyroid")

#: Build orientation relative to the load axis (PR #24 Edison table).
BUILD_ORIENTATIONS: tuple[str, ...] = ("vertical", "horizontal", "45deg")

#: Continuous + integer + categorical search space.
#:
#: Bounds taken directly from PR #24's Edison literature table
#: (``tpu-petg-bo-variables-5ae24eaf-….md``, section D — "Recommended Numeric
#: Bounds for BoTorch/Ax Search Space"). The set is deliberately a *subset*
#: of the full ~20-variable Edison table: the most influential geometric +
#: print knobs are exposed here so the BO loop stays tractable inside the
#: 50–100-specimen undergrad campaign size that PR #24 calls out.
PARAMETERS: list[dict] = [
    # --- Geometric / topological ---------------------------------------
    {
        # PETG strut diameter; Pajunen used ~3 mm. PR #24: [1.5, 5.0] mm.
        "name": "strut_diameter_mm",
        "type": "range",
        "bounds": [1.5, 5.0],
        "value_type": "float",
    },
    {
        # Strut length. Combined with strut_diameter it yields the
        # slenderness L/D that PR #24 lists as the central buckling-vs-
        # crushing knob; we expose L directly (Edison bound: L/D ∈ [8, 25]
        # → ~ 12–125 mm at the extremes; we restrict to the H2D-friendly
        # 15–50 mm window the IDETC abstract uses).
        "name": "strut_length_mm",
        "type": "range",
        "bounds": [15.0, 50.0],
        "value_type": "float",
    },
    {
        # TPU tendon/cable diameter (replaces the IDETC abstract's skin
        # width + thickness pair). PR #24: [1.0, 3.0] mm — Pajunen-style
        # cable cross-section, manufacturable on a 0.4 mm nozzle.
        "name": "cable_diameter_mm",
        "type": "range",
        "bounds": [1.0, 3.0],
        "value_type": "float",
    },
    {
        # Twist angle for prism / stacked-prism families. PR #24: [10°, 45°].
        "name": "twist_angle_deg",
        "type": "range",
        "bounds": [10.0, 45.0],
        "value_type": "float",
    },
    {
        # Tendon prestrain (Pajunen sweet spot ≈ 2 %). PR #24: [0 %, 5 %].
        "name": "prestress_pct",
        "type": "range",
        "bounds": [0.0, 5.0],
        "value_type": "float",
    },
    {
        # Integer strut count per unit cell. Encoded as an ordered choice so
        # the GP can reason about ordering while still respecting integrality.
        "name": "struts_per_cell",
        "type": "choice",
        "values": [3, 4, 6, 8, 12],
        "is_ordered": True,
        "sort_values": True,
    },
    {
        "name": "topology",
        "type": "choice",
        "values": list(TOPOLOGIES),
        "is_ordered": False,
    },
    {
        "name": "tiling",
        "type": "choice",
        "values": list(TILINGS),
        "is_ordered": False,
    },
    # --- Material / print ----------------------------------------------
    {
        # TPU shore hardness. Lab uses 85A by default; 95A trades cushion
        # for plateau-stress stability (PR #24 / León-Calero).
        "name": "tpu_shore",
        "type": "choice",
        "values": list(TPU_SHORES),
        "is_ordered": True,
        "sort_values": False,
    },
    {
        # PETG infill % (PR #24: [40, 100]). One of the strongest FDM knobs.
        "name": "petg_infill_pct",
        "type": "range",
        "bounds": [40.0, 100.0],
        "value_type": "float",
    },
    {
        "name": "petg_infill_pattern",
        "type": "choice",
        "values": list(PETG_INFILL_PATTERNS),
        "is_ordered": False,
    },
    {
        # PETG–TPU interface wrap thickness (Khatri 2024). Replaces the
        # IDETC abstract's tpu_skin_thickness with the more general
        # multimaterial-joint reinforcement variable from PR #24.
        "name": "interface_wrap_thickness_mm",
        "type": "range",
        "bounds": [0.4, 2.0],
        "value_type": "float",
    },
    {
        "name": "build_orientation",
        "type": "choice",
        "values": list(BUILD_ORIENTATIONS),
        "is_ordered": False,
    },
]

OBJECTIVES: dict[str, ObjectiveProperties] = {
    F_PEAK: ObjectiveProperties(minimize=True, threshold=F_PEAK_THRESHOLD),
    SEA: ObjectiveProperties(minimize=False, threshold=SEA_THRESHOLD),
    ETA: ObjectiveProperties(minimize=False, threshold=ETA_THRESHOLD),
}

# ----------------------------------------------------------------------------
# Analytical dummy objective
# ----------------------------------------------------------------------------

# Densities (g / cm^3). PETG ≈ 1.27, TPU 85A/95A ≈ 1.21. Only used for the
# relative mass term in the dummy SEA calculation.
RHO_PETG = 1.27
RHO_TPU = 1.21

# Per-topology stiffness multiplier; larger ⇒ stiffer cell ⇒ higher peak force.
# Ordering follows PR #24's Pajunen-recommended ranking (truncated octahedron
# is the strongest seed family but also the stiffest).
_TOPOLOGY_STIFFNESS = {
    "t3_prism": 1.0,
    "simplex_4_strut": 1.15,
    "stacked_prism": 1.35,
    "truncated_octahedron": 1.7,
}

# Per-tiling multiplier on transmitted force (more cells in the load path
# share the load and slightly raise the plateau).
_TILING_FORCE = {
    "1x1x1": 1.0,
    "1x1x2": 1.4,
    "2x2x1": 1.6,
    "2x2x2": 2.4,
    "3x3x2": 3.6,
}

# Per-topology hysteretic energy absorption efficiency (idealized cells with
# more redundant tension members dissipate more under post-buckling load).
_TOPOLOGY_HYSTERESIS = {
    "t3_prism": 0.55,
    "simplex_4_strut": 0.62,
    "stacked_prism": 0.72,
    "truncated_octahedron": 0.85,
}

# TPU shore softness factor for the cushion term: 85A is ~2× softer per unit
# cross-section than 95A (memory: NinjaFlex secant E ≈ 12 MPa).
_TPU_SOFTNESS = {"85A": 1.0, "95A": 0.55}

# PETG infill pattern stiffness factors (anisotropy / crush behaviour).
_INFILL_PATTERN_K = {"rectilinear": 1.0, "grid": 1.05, "gyroid": 0.9}

# Build-orientation multipliers on transmitted force. Vertical (load-aligned)
# struts carry load axially and so see the highest peak; 45° splits load
# between axial and shear; horizontal struts crush rather than buckle.
_ORIENTATION_FORCE = {"vertical": 1.0, "horizontal": 0.75, "45deg": 0.88}


@dataclass(frozen=True)
class SpecimenResponse:
    """Container for one specimen's measured outcomes."""

    f_peak_N: float
    sea_J_per_g: float
    eta: float

    def as_raw_data(self) -> dict[str, float]:
        return {F_PEAK: self.f_peak_N, SEA: self.sea_J_per_g, ETA: self.eta}


def simulate_specimen(
    parameters: Mapping[str, float | int | str],
    *,
    rng: np.random.Generator | None = None,
) -> SpecimenResponse:
    """Return a physically plausible (but synthetic) response for a design.

    This is the **placeholder** evaluation function. Replace it with either a
    call into the experimental data layer (looking up a fabricated specimen's
    drop-weight test results) or a calibrated FE surrogate. The signature is
    intentionally minimal so the closed-loop BO at the bottom of this script
    does not need to change when the real evaluator lands.

    The model is hand-tuned to give the BO loop a non-trivial Pareto front:

    * ``F_peak`` rises with strut diameter, strut count, topology stiffness,
      and tiling, but is reduced by thicker, wider TPU skins (cushioning).
    * ``SEA`` rises with topology hysteresis and skin volume but falls when
      mass grows faster than absorbed energy (so very thick struts hurt SEA).
    * ``eta`` rises with skin thickness (better load-limiting plateau) and
      saturates around the topology's hysteresis ceiling.

    Small Gaussian noise is added to mimic the heteroscedastic batch-to-batch
    variability called out in the IDETC abstract.
    """
    rng = rng if rng is not None else np.random.default_rng()

    d = float(parameters["strut_diameter_mm"])  # mm, PETG strut
    L = float(parameters["strut_length_mm"])  # mm
    d_cable = float(parameters["cable_diameter_mm"])  # mm, TPU tendon
    twist = float(parameters["twist_angle_deg"])  # deg
    prestress = float(parameters["prestress_pct"])  # %
    n_struts = int(parameters["struts_per_cell"])
    topo = str(parameters["topology"])
    tile = str(parameters["tiling"])
    shore = str(parameters["tpu_shore"])
    infill = float(parameters["petg_infill_pct"])  # %
    infill_pat = str(parameters["petg_infill_pattern"])
    wrap_t = float(parameters["interface_wrap_thickness_mm"])  # mm
    orient = str(parameters["build_orientation"])

    # Volumes in cm^3 (mm^3 / 1000). PETG strut volume is scaled by infill
    # fraction so the very low-infill struts actually drop in mass.
    petg_volume_cm3 = (
        n_struts * math.pi * (d / 2) ** 2 * L * (infill / 100.0) / 1000.0
    )
    # TPU tendon: one cable per strut, similar length. Plus the interface
    # wrap (a thin TPU jacket around each PETG strut, length ≈ L).
    tpu_cable_cm3 = n_struts * math.pi * (d_cable / 2) ** 2 * L / 1000.0
    tpu_wrap_cm3 = n_struts * math.pi * d * wrap_t * L / 1000.0
    tpu_volume_cm3 = tpu_cable_cm3 + tpu_wrap_cm3
    mass_g = petg_volume_cm3 * RHO_PETG + tpu_volume_cm3 * RHO_TPU

    topo_k = _TOPOLOGY_STIFFNESS[topo]
    tile_k = _TILING_FORCE[tile]
    eta_ceiling = _TOPOLOGY_HYSTERESIS[topo]
    softness = _TPU_SOFTNESS[shore]
    infill_k = _INFILL_PATTERN_K[infill_pat]
    orient_k = _ORIENTATION_FORCE[orient]

    # Peak transmitted force (N). Scaled so that a small T3 prism reaches
    # ~500 N and an aggressive truncated octahedron 3x3x2 reaches several kN.
    # Cushion factor in (0, 1]: thicker cables / wraps and softer (85A) TPU
    # all lower the peak. The denominator's `4.0 mm^2` is a reference TPU
    # cross-section (cable + wrap) that gives cushion ≈ 0.625 at the
    # reference area (~38 % peak reduction) — re-fit against pilot data.
    cushion_area = math.pi * (d_cable / 2) ** 2 + d * wrap_t
    cushion = 1.0 / (1.0 + 0.6 * softness * cushion_area / 4.0)
    # Prestress mildly raises the first-yield load (snap-through caps later).
    prestress_factor = 1.0 + 0.04 * prestress
    # Infill % scales strut compression strength roughly linearly.
    infill_strength = 0.4 + 0.6 * (infill / 100.0)
    f_peak = (
        180.0
        * topo_k
        * tile_k
        * orient_k
        * infill_strength
        * infill_k
        * (d**2)
        / max(L, 1e-3)
        * (n_struts / 4.0)
        * cushion
        * prestress_factor
    )

    # Absorbed energy (J). 0.18 J/cm^3 reference energy density for TPU
    # (softer shore absorbs more per unit volume); 0.4 weights the
    # (smaller) PETG contribution. The 1 / (1 + 0.05*d) term softly
    # penalizes very thick struts that buckle catastrophically rather than
    # absorbing energy progressively. Twist angle adds a small bonus for
    # mid-range twists (peak near ~30°) where stiffness-collapse mode shifts
    # contribute extra hysteresis.
    twist_bonus = 1.0 + 0.15 * math.exp(-((twist - 30.0) ** 2) / (2 * 12.0**2))
    absorbed_J = (
        0.18
        * eta_ceiling
        * (tpu_volume_cm3 * (0.5 + 0.5 * softness) + 0.4 * petg_volume_cm3)
        * tile_k
        * twist_bonus
    ) / (1.0 + 0.05 * d)
    sea_val = absorbed_J / max(mass_g, 1e-3)

    # Compaction efficiency in [0, 1]. Saturating function of the combined
    # TPU cushion (cable + wrap); 0.85 + 0.05 adds a small bonus for cells
    # with >=6 redundant struts (more uniform plateau response). Softer 85A
    # TPU gives a flatter plateau, slightly raising eta. Replace with a
    # measured force-displacement integral.
    eta_val = (
        eta_ceiling
        * (1.0 - math.exp(-1.5 * (d_cable / 2.0 + wrap_t)))
        * (0.85 + 0.05 * (n_struts >= 6))
        * (0.9 + 0.1 * softness)
    )
    eta_val = float(min(max(eta_val, 0.05), 0.95))

    # Heteroscedastic noise: noise grows with peak force (consistent with
    # accelerometer scaling), and TPU-dominated metrics see more relative
    # noise than the geometric F_peak.
    f_peak += rng.normal(0.0, max(20.0, 0.03 * f_peak))
    sea_val += rng.normal(0.0, 0.05 * max(sea_val, 0.1))
    eta_val += rng.normal(0.0, 0.02)
    eta_val = float(min(max(eta_val, 0.0), 1.0))

    return SpecimenResponse(
        f_peak_N=float(max(f_peak, 1.0)),
        sea_J_per_g=float(max(sea_val, 0.01)),
        eta=eta_val,
    )


# ----------------------------------------------------------------------------
# Plotting
# ----------------------------------------------------------------------------


def plot_pareto(ax_client: AxClient, output: Path | None = None) -> Path | None:
    """Save a 2D scatter of observed F_peak vs SEA, highlighting the Pareto set.

    Returns the path written, or ``None`` if matplotlib is not installed (so
    the script remains usable on a headless machine without plotting deps).
    """
    try:
        import matplotlib

        matplotlib.use("Agg", force=False)
        import matplotlib.pyplot as plt
    except ImportError:  # pragma: no cover - matplotlib is in requirements.txt
        return None

    df = ax_client.get_trials_data_frame()
    pareto = ax_client.get_pareto_optimal_parameters(use_model_predictions=False)
    pareto_df = pd.DataFrame([p[1][0] for p in pareto.values()])

    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    ax.scatter(df[F_PEAK], df[SEA], fc="none", ec="k", label="Observed")
    if not pareto_df.empty:
        pareto_df = pareto_df.sort_values(F_PEAK)
        ax.plot(
            pareto_df[F_PEAK],
            pareto_df[SEA],
            color="#0033FF",
            lw=2,
            marker="o",
            label="Pareto front",
        )
    ax.set_xlabel("Peak transmitted force [N]  (minimize)")
    ax.set_ylabel("Specific energy absorption [J/g]  (maximize)")
    ax.set_title("Tensegrity-inspired energy absorber BO campaign")
    ax.legend(loc="best")
    fig.tight_layout()

    output = output or Path(__file__).resolve().parent / "campaign_pareto.png"
    fig.savefig(output)
    plt.close(fig)
    return output


# ----------------------------------------------------------------------------
# Closed-loop BO campaign
# ----------------------------------------------------------------------------

rng = np.random.default_rng(SEED)

# AxClient is itself the high-level wrapper around the BO loop. Its default
# GenerationStrategy starts with a Sobol quasi-random init phase (covering
# the search space without pilot data) and then switches automatically to
# the model-based MOO acquisition once enough observations exist.
ax_client = AxClient(random_seed=SEED)
ax_client.create_experiment(
    name="tensegrity_energy_absorber",
    parameters=PARAMETERS,
    objectives=OBJECTIVES,
    overwrite_existing_experiment=True,
)

for _ in range(N_ITERATIONS):
    parameterizations, _complete = ax_client.get_next_trials(BATCH_SIZE)
    for trial_index, parameterization in parameterizations.items():
        response = simulate_specimen(parameterization, rng=rng)
        ax_client.complete_trial(
            trial_index=trial_index, raw_data=response.as_raw_data()
        )

pareto = ax_client.get_pareto_optimal_parameters(use_model_predictions=False)
df = ax_client.get_trials_data_frame()
print(f"Completed {len(df)} trials ({N_ITERATIONS * BATCH_SIZE} BO-selected).")
print(f"Pareto-optimal designs: {len(pareto)}")
print("Best per-objective values observed:")
print(f"  min {F_PEAK} = {df[F_PEAK].min():.1f} N")
print(f"  max {SEA}    = {df[SEA].max():.3f} J/g")
print(f"  max {ETA}    = {df[ETA].max():.3f}")

path = plot_pareto(ax_client)
if path is not None:
    print(f"Wrote Pareto plot to {path}")
