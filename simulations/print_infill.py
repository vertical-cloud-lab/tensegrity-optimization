"""Sub-100 % PLA infill: printed mass and effective strut properties.

Every simulation in this directory has so far treated a strut as **solid**
PLA (rho = 1240 kg/m^3, E = 3500 MPa).  The articles on the bench are not
solid: the Bambu profile prints the PLA struts/joints with walls plus a
sparse infill, while the thin TPU tendons come out essentially solid.  The
PR #86 campaign analysis (section 7, "why the printed masses vary despite
the constant-mass constraint") regressed the seven weighed articles of the
T-3_01 Sobol batch on their per-material solid masses and got

    measured ~= 0.565 * m_PLA,solid + 0.986 * m_TPU,solid   (R^2 = 0.78)

so the PLA prints at about 57 % of solid density and the TPU at about 99 %.
:func:`fit_solidity` re-derives those coefficients from the committed CSVs
(``simulations/data/pr102/``) so the number in the simulation is traceable
to the scale readings rather than copied from prose.

Why this matters for the simulator, concretely:

* **Mass.** A 6.2x lighter-than-solid strut set changes the article's
  inertia, which is exactly what sets the transmissibility of a
  base-excited structure.  The constant-mass projection in PR #35 holds
  *solid* volume constant, so the printed batch is not constant-mass: it
  spans 18.5 to 22.3 g because the PLA/TPU split moves with the design.
  Feeding solid density to the sim reproduces neither the absolute masses
  nor their spread.
* **Stiffness.** Sparse infill also softens the strut.  Tier-C treats
  struts as rigid capsules so only the mass channel bites there, but the
  effective modulus is needed by any tier that lets the strut deform
  (Newton, PolyFEM) and by the tendon-vs-strut compliance ratio.  The
  Gibson-Ashby scaling for a cellular solid,
  ``E_eff / E_solid = (rho_eff / rho_solid) ** n``, brackets the answer:
  ``n = 1`` for a stretch-dominated cell (the limit that fits an FFF part
  whose load-bearing perimeters are solid and axial) and ``n = 2`` for a
  bending-dominated open cell (the limit for a sparse gyroid loaded
  transversely).  We default to ``n = 1.5`` and expose it, rather than
  pretending one of the bounds is the answer: the printed strut is walls
  plus infill, i.e. genuinely between the two.  With phi = 0.565 the
  bracket is E_eff = 1980 MPa (n=1) to 1117 MPa (n=2), 1489 MPa at n=1.5.

Nothing here re-slices anything: the solidity is an *effective* number
that folds wall count, infill density and pattern into one scalar, which
is all a mass-and-stiffness model can identify from a scale reading.  A
per-profile exact answer would come from the BambuStudio CLI's sliced
per-filament grams, as PR #86 section 7 notes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from printable_design import PLA, TPU85A, PrintableDesign
from tprism_geometry import STRUTS

DATA_DIR = Path(__file__).resolve().parent / "data" / "pr102"

# Fitted on the seven weighed T-3_01 articles (PR #86 section 7); reproduced
# by ``fit_solidity()`` from the committed CSVs.
PLA_SOLIDITY = 0.565
TPU_SOLIDITY = 0.986

# Gibson-Ashby exponent for E_eff/E_solid = phi**n.  1 = stretch-dominated,
# 2 = bending-dominated; an FFF strut with solid perimeters plus sparse
# infill sits between them.
STIFFNESS_EXPONENT = 1.5


def effective_pla_density_kgm3(solidity: float = PLA_SOLIDITY) -> float:
    """Printed PLA density: solid density times the effective solid fraction."""
    return PLA.density_kgm3 * float(solidity)


def effective_pla_modulus_MPa(solidity: float = PLA_SOLIDITY,
                              exponent: float = STIFFNESS_EXPONENT) -> float:
    """Gibson-Ashby effective modulus of the sparse-infill strut."""
    return PLA.young_MPa * float(solidity) ** float(exponent)


def effective_tpu_density_kgm3(solidity: float = TPU_SOLIDITY) -> float:
    """Printed TPU density (the thin tendons come out essentially solid)."""
    return TPU85A.density_kgm3 * float(solidity)


# --- per-material solid volumes -------------------------------------------

def material_volumes_m3(design: PrintableDesign) -> dict[str, float]:
    """Solid PLA (3 struts) and TPU (9 tendons) volumes of one cell.

    Same geometric convention as ``bo_evaluator.cell_geometry_metrics``: the
    nine tendons are all charged at the vertical-cable length (the longest of
    the three families), and joints/housings are folded into the strut term.
    That over-counts tendon volume slightly and under-counts joints, which is
    why the solidity coefficients below are *effective* rather than physical
    infill percentages.
    """
    n = design.nodes
    L_strut = design.strut_length_m
    v_strut = 3.0 * math.pi * (design.strut_diameter_m / 2.0) ** 2 * L_strut
    L_tendon = float(np.linalg.norm(n[0] - n[3]))
    v_tendon = 9.0 * math.pi * (design.tendon_diameter_m / 2.0) ** 2 * L_tendon
    return {"pla_m3": float(v_strut), "tpu_m3": float(v_tendon)}


@dataclass(frozen=True)
class PrintedMass:
    """Solid-CAD and as-printed masses of one cell, in grams."""
    pla_solid_g: float
    tpu_solid_g: float
    pla_printed_g: float
    tpu_printed_g: float

    @property
    def solid_g(self) -> float:
        return self.pla_solid_g + self.tpu_solid_g

    @property
    def printed_g(self) -> float:
        return self.pla_printed_g + self.tpu_printed_g

    @property
    def tpu_fraction(self) -> float:
        """Solid-mass fraction carried by TPU (0.12 to 0.36 across the batch)."""
        return self.tpu_solid_g / max(self.solid_g, 1e-12)


def printed_mass(design: PrintableDesign,
                 *, pla_solidity: float = PLA_SOLIDITY,
                 tpu_solidity: float = TPU_SOLIDITY) -> PrintedMass:
    """As-printed mass of a cell, from its geometry and the fitted solidities."""
    v = material_volumes_m3(design)
    pla_solid_g = v["pla_m3"] * PLA.density_kgm3 * 1000.0
    tpu_solid_g = v["tpu_m3"] * TPU85A.density_kgm3 * 1000.0
    return PrintedMass(
        pla_solid_g=pla_solid_g,
        tpu_solid_g=tpu_solid_g,
        pla_printed_g=pla_solid_g * float(pla_solidity),
        tpu_printed_g=tpu_solid_g * float(tpu_solidity),
    )


# --- calibration ----------------------------------------------------------

def fit_solidity(batch_csv: Path | None = None,
                 key_csv: Path | None = None) -> dict[str, float]:
    """Least-squares fit of (PLA, TPU) solidity to the weighed articles.

    Regresses each official print's measured mass on the batch table's
    per-material *solid* masses (``pla_g``, ``tpu_g``), with no intercept:

        measured ~ phi_PLA * m_PLA,solid + phi_TPU * m_TPU,solid

    Returns the two coefficients, R^2, residual sd and n.  This is the same
    regression PR #86 section 7 reports; running it here keeps the constants
    at the top of this module honest if either CSV is updated.
    """
    import pandas as pd

    batch_csv = batch_csv or DATA_DIR / "t3-prism-bo-batch.csv"
    key_csv = key_csv or DATA_DIR / "t3-prism-bo-batch-print-key.csv"
    batch = pd.read_csv(batch_csv).set_index("specimen")
    key = pd.read_csv(key_csv, dtype={"specimen": "string"})

    # one weighed article per Sobol spec: the "official" print (spec 08 has
    # a triplicate; take its official row, matching what was drop-tested)
    rows = []
    for _, r in key.iterrows():
        spec = str(r["specimen"]).strip()
        if spec in ("", "S0", "<NA>") or not spec.isdigit():
            continue
        if not str(r["role"]).startswith("official"):
            continue
        b = batch.loc[int(spec)]
        rows.append((float(b["pla_g"]), float(b["tpu_g"]), float(r["mass_g"])))

    A = np.array([[p, t] for p, t, _ in rows])
    y = np.array([m for _, _, m in rows])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    return {
        "pla_solidity": float(coef[0]),
        "tpu_solidity": float(coef[1]),
        "r2": 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan"),
        "resid_sd_g": float(np.sqrt(ss_res / max(len(y) - 2, 1))),
        "n": len(y),
    }


if __name__ == "__main__":
    fit = fit_solidity()
    print("Refit from simulations/data/pr102/ (PR #102 batch + print key):")
    print(f"  measured ~= {fit['pla_solidity']:.3f} * m_PLA,solid "
          f"+ {fit['tpu_solidity']:.3f} * m_TPU,solid")
    print(f"  R^2 = {fit['r2']:.2f}, residual sd = {fit['resid_sd_g']:.2f} g, "
          f"n = {fit['n']} weighed articles")
    print(f"  module constants in use: PLA {PLA_SOLIDITY}, TPU {TPU_SOLIDITY}")
    print()
    print(f"effective PLA density  = {effective_pla_density_kgm3():7.1f} kg/m^3 "
          f"(solid {PLA.density_kgm3:.0f})")
    for n in (1.0, STIFFNESS_EXPONENT, 2.0):
        print(f"effective PLA modulus  = {effective_pla_modulus_MPa(exponent=n):7.0f} MPa "
              f"(Gibson-Ashby n = {n})")
    print(f"struts per cell        = {len(STRUTS)}")


# --- CAD-vs-model geometry correction and the constant-mass projection ----
#
# The volume model above is the same three-capsules-plus-nine-cylinders
# idealization the rest of this directory uses.  The printed CAD is not that:
# it also carries PLA joints, housings and the modeled-in scaffold (PR #35),
# and its nine tendons are not all as long as the vertical cable.  Regressing
# the batch table's per-material *reference-STL* masses (``pla_g``/``tpu_g``,
# at print scale) on the model volumes gives two shape-independent factors,
#
#     m_PLA,CAD ~= 1.68 * m_PLA,model      m_TPU,CAD ~= 0.68 * m_TPU,model
#
# with ~9 % and ~6 % scatter across the nine designs -- small enough that one
# factor per material carries the CAD geometry into the simulation, large
# enough that ignoring them puts the article's mass out by a factor 1.5.
PLA_GEOM_FACTOR = 1.68
TPU_GEOM_FACTOR = 0.68

# Target solid-CAD mass of the constant-mass projection (PR #35 batch
# generator): the solid-volume mass of the S0 reference STLs.
TARGET_SOLID_MASS_G = 30.95


def cad_solid_masses_g(design: PrintableDesign) -> tuple[float, float]:
    """(PLA, TPU) solid-CAD masses of a cell, geometry-corrected."""
    v = material_volumes_m3(design)
    pla_g = v["pla_m3"] * PLA.density_kgm3 * 1000.0 * PLA_GEOM_FACTOR
    tpu_g = v["tpu_m3"] * TPU85A.density_kgm3 * 1000.0 * TPU_GEOM_FACTOR
    return float(pla_g), float(tpu_g)


def scale_design(design: PrintableDesign, scale: float) -> PrintableDesign:
    """Uniformly rescale every length of a cell (the PR #35 projection)."""
    from dataclasses import replace
    s = float(scale)
    return replace(design,
                   radius_m=design.radius_m * s,
                   height_m=design.height_m * s,
                   strut_diameter_m=design.strut_diameter_m * s,
                   tendon_diameter_m=design.tendon_diameter_m * s)


def project_constant_mass(design: PrintableDesign,
                          target_solid_g: float = TARGET_SOLID_MASS_G
                          ) -> tuple[PrintableDesign, float]:
    """PR #35 Route-A projection: uniform scale to a fixed solid-CAD mass.

    Returns the as-printed design and the scale applied.  Cell mass is
    homogeneous of degree three in the scale, so the solve is a cube root --
    the same closed form ``bo_evaluator.design_from_shape_ratios`` uses.
    This is what turns a set of *base* Sobol coordinates into the article
    that actually gets printed, and the simulation has to run on the latter:
    across the T-3_01 batch the projection moves every length by 0.77 to
    1.04, so base and printed geometry differ by up to a quarter.
    """
    pla_g, tpu_g = cad_solid_masses_g(design)
    total = pla_g + tpu_g
    scale = (float(target_solid_g) / total) ** (1.0 / 3.0) if total > 0 else 1.0
    return scale_design(design, scale), float(scale)


def printed_mass_cad(design: PrintableDesign,
                     *, pla_solidity: float = PLA_SOLIDITY,
                     tpu_solidity: float = TPU_SOLIDITY) -> PrintedMass:
    """As-printed mass using the geometry-corrected CAD volumes.

    This is the number to compare against a scale reading; :func:`printed_mass`
    uses the uncorrected idealized volumes and is kept for continuity with the
    rest of the directory's mass bookkeeping.
    """
    pla_solid_g, tpu_solid_g = cad_solid_masses_g(design)
    return PrintedMass(
        pla_solid_g=pla_solid_g,
        tpu_solid_g=tpu_solid_g,
        pla_printed_g=pla_solid_g * float(pla_solidity),
        tpu_printed_g=tpu_solid_g * float(tpu_solidity),
    )


def fit_geometry_factors(batch_csv: Path | None = None) -> dict[str, float]:
    """Refit ``PLA_GEOM_FACTOR`` / ``TPU_GEOM_FACTOR`` from the batch table."""
    import pandas as pd

    from bo_evaluator import parameterization_to_design

    batch_csv = batch_csv or DATA_DIR / "t3-prism-bo-batch.csv"
    batch = pd.read_csv(batch_csv).set_index("specimen")
    pla_r, tpu_r = [], []
    for _, row in batch.iterrows():
        params = {k: float(row[k]) for k in
                  ("R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm")}
        design = parameterization_to_design(params)
        printed = scale_design(design, float(row["scale"]))
        v = material_volumes_m3(printed)
        pla_r.append(float(row["pla_g"])
                     / (v["pla_m3"] * PLA.density_kgm3 * 1000.0))
        tpu_r.append(float(row["tpu_g"])
                     / (v["tpu_m3"] * TPU85A.density_kgm3 * 1000.0))
    return {"pla_geom_factor": float(np.mean(pla_r)),
            "pla_geom_cv": float(np.std(pla_r) / np.mean(pla_r)),
            "tpu_geom_factor": float(np.mean(tpu_r)),
            "tpu_geom_cv": float(np.std(tpu_r) / np.mean(tpu_r)),
            "n": len(pla_r)}
