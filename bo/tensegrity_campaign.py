"""Tensegrity-inspired energy-absorber Bayesian-optimization campaign.

This module is the *customized* companion to ``bo/tensegrity_bo.py``. The
latter is the unmodified, regenerable honegumi scaffold; this file replaces
honegumi's Branin placeholder with the design variables and objectives that
are consistent across the project's existing artifacts:

* ``proposal.tex`` (BYU MRG)
    "strut diameter and length (PLA), tension-element cross-section (TPU),
    connectivity topology, and unit-cell tiling"; "peak transmitted force,
    specific energy absorption (SEA), and compaction efficiency".
* ``idetc-abstract.tex`` (ASME IDETC-CIE 2026, accepted)
    Continuous strut diameter / length and TPU skin width / thickness, an
    integer strut count per unit cell, and two categorical variables
    (connectivity topology, unit-cell tiling). Three measured outcomes:
    F_peak, SEA, eta. Multi-objective BO via qNEHVI.
* ``nasa-space-grant/proposal.tex`` (BYU NASA Space Grant)
    "strut diameter and length, TPU skin thickness, tiling and topology",
    minimize peak transmitted force at a target SEA.
* PR #24 (TPU + PETG variable scoping)
    Reinforces the same continuous + categorical split with reasonable bounds
    sized for the H2D printer.

Per the abstract, the source of truth at run time is the *physical
experiment*. Until that data starts arriving, this module ships an
**analytical dummy objective** (``simulate_specimen``) that returns
physically plausible F_peak / SEA / eta from the design vector. The dummy is
documented inline so it can be replaced wholesale by a call into the
experimental data layer (or an FE surrogate) without touching the BO loop.

Run it with::

    pip install -r bo/requirements.txt
    MPLBACKEND=Agg python bo/tensegrity_campaign.py            # quick run
    MPLBACKEND=Agg python bo/tensegrity_campaign.py --full     # 21-iter run
"""

from __future__ import annotations

import argparse
import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd
from ax.service.ax_client import AxClient, ObjectiveProperties

logging.getLogger("ax").setLevel(logging.WARNING)

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

#: Connectivity topologies and their nominal strut counts; consistent with
#: the unit cells discussed in the abstract and PR #24 (3-bar prism through
#: icosahedron).
TOPOLOGIES: tuple[str, ...] = (
    "3_bar_prism",
    "4_bar_prism",
    "octahedron",
    "icosahedron",
)

#: Unit-cell tiling patterns; the tiling axes are kept modest to stay within
#: the H2D build envelope and undergrad-friendly print times.
TILINGS: tuple[str, ...] = ("1x1x1", "2x2x1", "2x2x2")

#: Continuous + integer + categorical search space. Bounds are deliberately
#: conservative; revisit once the H2D pilot prints and PR #24's literature
#: synthesis land.
PARAMETERS: list[dict] = [
    {
        "name": "strut_diameter_mm",
        "type": "range",
        "bounds": [1.5, 6.0],
        "value_type": "float",
    },
    {
        "name": "strut_length_mm",
        "type": "range",
        "bounds": [15.0, 50.0],
        "value_type": "float",
    },
    {
        "name": "tpu_skin_thickness_mm",
        "type": "range",
        "bounds": [0.4, 2.0],
        "value_type": "float",
    },
    {
        "name": "tpu_skin_width_mm",
        "type": "range",
        "bounds": [1.0, 6.0],
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
]

OBJECTIVES: dict[str, ObjectiveProperties] = {
    F_PEAK: ObjectiveProperties(minimize=True, threshold=F_PEAK_THRESHOLD),
    SEA: ObjectiveProperties(minimize=False, threshold=SEA_THRESHOLD),
    ETA: ObjectiveProperties(minimize=False, threshold=ETA_THRESHOLD),
}

# ----------------------------------------------------------------------------
# Analytical dummy objective
# ----------------------------------------------------------------------------

# Densities (g / cm^3). Approximate, only used for the relative mass term in
# the dummy SEA calculation.
RHO_PLA = 1.24
RHO_TPU = 1.21

# Per-topology stiffness multiplier; larger ⇒ stiffer cell ⇒ higher peak force.
_TOPOLOGY_STIFFNESS = {
    "3_bar_prism": 1.0,
    "4_bar_prism": 1.15,
    "octahedron": 1.4,
    "icosahedron": 1.7,
}

# Per-tiling multiplier on transmitted force (more cells in the load path
# share the load and slightly raise the plateau).
_TILING_FORCE = {"1x1x1": 1.0, "2x2x1": 1.6, "2x2x2": 2.4}

# Per-topology hysteretic energy absorption efficiency (idealized cells with
# more redundant tension members dissipate more under post-buckling load).
_TOPOLOGY_HYSTERESIS = {
    "3_bar_prism": 0.55,
    "4_bar_prism": 0.62,
    "octahedron": 0.75,
    "icosahedron": 0.82,
}


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
    intentionally minimal so the BO loop in :func:`run_campaign` does not need
    to change when the real evaluator lands.

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

    d = float(parameters["strut_diameter_mm"])  # mm
    L = float(parameters["strut_length_mm"])  # mm
    t = float(parameters["tpu_skin_thickness_mm"])  # mm
    w = float(parameters["tpu_skin_width_mm"])  # mm
    n_struts = int(parameters["struts_per_cell"])
    topo = str(parameters["topology"])
    tile = str(parameters["tiling"])

    # Volumes in cm^3 (mm^3 / 1000).
    pla_volume_cm3 = n_struts * math.pi * (d / 2) ** 2 * L / 1000.0
    # Each strut wrapped by a TPU sheath of thickness t, width w, length ~L.
    tpu_volume_cm3 = n_struts * t * w * L / 1000.0
    mass_g = pla_volume_cm3 * RHO_PLA + tpu_volume_cm3 * RHO_TPU

    topo_k = _TOPOLOGY_STIFFNESS[topo]
    tile_k = _TILING_FORCE[tile]
    eta_ceiling = _TOPOLOGY_HYSTERESIS[topo]

    # Peak transmitted force (N). Scaled so that a small 3-bar-prism cell is
    # ~500 N and an aggressive icosahedron 2x2x2 reaches several kN.
    # Cushion factor in (0, 1]: thicker/wider TPU skins lower the peak. The
    # denominator's `4.0 mm^2` is a reference skin cross-section that gives a
    # ~50% cushion at t*w = 4 mm^2 — re-fit against pilot data when available.
    cushion = 1.0 / (1.0 + 0.6 * t * w / 4.0)
    f_peak = (
        180.0 * topo_k * tile_k * (d**2) / max(L, 1e-3) * (n_struts / 4.0) * cushion
    )

    # Absorbed energy (J). 0.18 J/cm^3 is a hand-tuned reference energy
    # density for the TPU skins; 0.4 weights the (smaller) PLA contribution.
    # The 1 / (1 + 0.05*d) term softly penalizes very thick struts that
    # buckle catastrophically rather than absorbing energy progressively.
    absorbed_J = (
        0.18 * eta_ceiling * (tpu_volume_cm3 + 0.4 * pla_volume_cm3) * tile_k
    ) / (1.0 + 0.05 * d)
    sea_val = absorbed_J / max(mass_g, 1e-3)

    # Compaction efficiency in [0, 1]. Saturating function of TPU thickness:
    # 1.5 mm^-1 gives ~78% of the topology ceiling at t = 1 mm; 0.85 + 0.05
    # adds a small bonus for cells with >=6 redundant struts (more uniform
    # plateau response). Replace with a measured force-displacement integral.
    eta_val = eta_ceiling * (1.0 - math.exp(-1.5 * t)) * (0.85 + 0.05 * (n_struts >= 6))
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
# Pilot ("existing data") seed
# ----------------------------------------------------------------------------

#: A handful of plausible pilot designs that span the search space. These
#: stand in for the geometric-fidelity baselines mentioned in
#: ``nasa-space-grant/proposal.tex`` ("verified geometric fidelity ... on at
#: least 5 baseline geometries").
PILOT_DESIGNS: list[dict] = [
    {
        "strut_diameter_mm": 2.0,
        "strut_length_mm": 25.0,
        "tpu_skin_thickness_mm": 0.6,
        "tpu_skin_width_mm": 2.0,
        "struts_per_cell": 3,
        "topology": "3_bar_prism",
        "tiling": "1x1x1",
    },
    {
        "strut_diameter_mm": 3.0,
        "strut_length_mm": 30.0,
        "tpu_skin_thickness_mm": 1.0,
        "tpu_skin_width_mm": 3.0,
        "struts_per_cell": 4,
        "topology": "4_bar_prism",
        "tiling": "2x2x1",
    },
    {
        "strut_diameter_mm": 4.0,
        "strut_length_mm": 35.0,
        "tpu_skin_thickness_mm": 1.4,
        "tpu_skin_width_mm": 4.0,
        "struts_per_cell": 6,
        "topology": "octahedron",
        "tiling": "2x2x1",
    },
    {
        "strut_diameter_mm": 5.0,
        "strut_length_mm": 40.0,
        "tpu_skin_thickness_mm": 1.8,
        "tpu_skin_width_mm": 5.0,
        "struts_per_cell": 8,
        "topology": "icosahedron",
        "tiling": "2x2x2",
    },
    {
        "strut_diameter_mm": 2.5,
        "strut_length_mm": 45.0,
        "tpu_skin_thickness_mm": 0.8,
        "tpu_skin_width_mm": 2.5,
        "struts_per_cell": 4,
        "topology": "octahedron",
        "tiling": "1x1x1",
    },
]


# ----------------------------------------------------------------------------
# BO campaign
# ----------------------------------------------------------------------------


def build_ax_client(*, random_seed: int | None = 0) -> AxClient:
    """Create the :class:`AxClient` configured for our MOO campaign."""
    ax_client = AxClient(random_seed=random_seed)
    ax_client.create_experiment(
        name="tensegrity_energy_absorber",
        parameters=PARAMETERS,
        objectives=OBJECTIVES,
        overwrite_existing_experiment=True,
    )
    return ax_client


def attach_pilot_data(
    ax_client: AxClient,
    *,
    rng: np.random.Generator | None = None,
) -> None:
    """Seed the surrogate with the simulated pilot specimen responses."""
    rng = rng if rng is not None else np.random.default_rng(0)
    for parameterization in PILOT_DESIGNS:
        _, trial_index = ax_client.attach_trial(parameterization)
        response = simulate_specimen(parameterization, rng=rng)
        ax_client.complete_trial(trial_index=trial_index, raw_data=response.as_raw_data())


def run_campaign(
    *,
    n_iterations: int = 21,
    batch_size: int = 2,
    random_seed: int = 0,
) -> AxClient:
    """Run the closed-loop BO campaign with the dummy specimen evaluator."""
    rng = np.random.default_rng(random_seed)
    ax_client = build_ax_client(random_seed=random_seed)
    attach_pilot_data(ax_client, rng=rng)

    for _ in range(n_iterations):
        parameterizations, _complete = ax_client.get_next_trials(batch_size)
        for trial_index, parameterization in parameterizations.items():
            response = simulate_specimen(parameterization, rng=rng)
            ax_client.complete_trial(
                trial_index=trial_index, raw_data=response.as_raw_data()
            )

    return ax_client


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
# CLI
# ----------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run the full 21-iteration campaign (default: 5 iterations for a smoke run).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
        help="Number of parallel trials per BO step (default: 2, matching the IDETC abstract's batch evaluation).",
    )
    parser.add_argument(
        "--seed", type=int, default=0, help="Random seed for the BO and dummy evaluator."
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip writing the Pareto-front PNG (useful in CI).",
    )
    args = parser.parse_args(argv)

    n_iterations = 21 if args.full else 5
    ax_client = run_campaign(
        n_iterations=n_iterations,
        batch_size=args.batch_size,
        random_seed=args.seed,
    )

    pareto = ax_client.get_pareto_optimal_parameters(use_model_predictions=False)
    df = ax_client.get_trials_data_frame()
    print(
        f"Completed {len(df)} trials ({len(PILOT_DESIGNS)} pilot + "
        f"{n_iterations * args.batch_size} BO-selected)."
    )
    print(f"Pareto-optimal designs: {len(pareto)}")
    print("Best per-objective values observed:")
    print(f"  min {F_PEAK} = {df[F_PEAK].min():.1f} N")
    print(f"  max {SEA}    = {df[SEA].max():.3f} J/g")
    print(f"  max {ETA}    = {df[ETA].max():.3f}")

    if not args.no_plot:
        path = plot_pareto(ax_client)
        if path is not None:
            print(f"Wrote Pareto plot to {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
