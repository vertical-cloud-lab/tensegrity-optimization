"""PETG strut + TPU "string" tensegrity-like design module.

The lab will fabricate the unit cell on a Bambu H2D as **PETG struts +
TPU tendons** (an FFF-printed approximation of a Snelson tensegrity, not
a pure tensegrity built from machined rods + Spectra cord).  This module
bridges that hardware reality with the simulation parameters consumed by
``run_regimes.py``, so that:

1. **Cable stiffness is derived from a printable geometry** (tendon
   diameter d_t and length L) rather than supplied as an abstract
   ``k`` in N/m.  The relationship is the elementary axial-spring
   formula ``k = E * A / L`` with ``E`` the TPU secant modulus.
2. **The class of the tensegrity is checked geometrically** before the
   sim is run: a "true" Snelson tensegrity is class-1, meaning no two
   struts touch.  In an FDM build with finite strut radius r_s, this
   becomes the constraint ``2 r_s < d_min(r, h, twist)``, where
   ``d_min`` is the closest approach between any pair of struts.  If
   the constraint is violated the structure is *tensegrity-like* (some
   loads bypass the tendons through strut-strut contact) and the BO
   objective is degenerate; we surface that explicitly so the operator
   sees it before printing.
3. **Manual-build hardware constraints** (knot/loop overhead at strut
   ends, minimum printable tendon dia, slip-thread vs sewn anchor) are
   captured as named constants so future agents do not silently set a
   tendon dia smaller than the H2D 0.4 mm nozzle can resolve.

The two materials and their published-typical FFF-print properties:

================================  ===========  ============
Property                          PETG         TPU 95A
================================  ===========  ============
Density (kg / m^3)                ~1270        ~1200
Young's modulus E (MPa)           ~2000        ~25 (secant)
Yield / break stress (MPa)        ~50          ~30 (break)
Strain to break (%)               ~5–10        ~400–550
================================  ===========  ============

(TPU 95A E is the small-strain secant; the large-strain stiffness is
strongly nonlinear / Mullins-affected.  For printable axial-spring k it
is the relevant quantity for the BO sweep here, where prestrain stays
small.)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tprism_geometry import CABLES, EQUILIBRIUM_TWIST, STRUTS, tprism_nodes


# --- Material properties --------------------------------------------------

@dataclass(frozen=True)
class Material:
    name: str
    young_MPa: float
    density_kgm3: float
    yield_break_MPa: float


PETG = Material("PETG",   young_MPa=2000.0, density_kgm3=1270.0,
                yield_break_MPa=50.0)
TPU95A = Material("TPU95A", young_MPa=25.0, density_kgm3=1200.0,
                  yield_break_MPa=30.0)


# --- Hardware (Bambu H2D) constraints -------------------------------------

H2D_NOZZLE_M = 0.4e-3       # 0.4 mm nozzle (per stored repo memory)
MIN_PRINTABLE_TENDON_DIA_M = 1.2e-3   # ~3 perimeters wide; rule of thumb
MAX_PRINTABLE_TENDON_DIA_M = 6.0e-3   # bigger -> use multi-strand instead
MIN_PRINTABLE_STRUT_DIA_M  = 2.0e-3   # PETG strut needs wall + infill


# --- Derived helpers ------------------------------------------------------

def tpu_cable_stiffness_Npm(diameter_m: float, length_m: float,
                            material: Material = TPU95A) -> float:
    """Axial-spring stiffness ``k = E * A / L`` for an FFF tendon.

    Sanity for TPU 95A, 1 mm dia, 0.20 m strut length:
        E A / L = 25e6 * pi (0.5e-3)^2 / 0.20 = 98 N/m.
    For a 3 mm dia tendon it is ~880 N/m.  This sets the *physically
    achievable* range of the cable_stiffness sweep in ``run_regimes.py``
    (~ 50-2000 N/m for a crutch-tip cell, much less than the abstract
    sweep ranges we explored before).
    """
    A = np.pi * (0.5 * diameter_m) ** 2
    return float(material.young_MPa * 1e6 * A / length_m)


def strut_pair_min_distance(nodes: np.ndarray) -> float:
    """Minimum closest-approach distance between any two of the 3 struts.

    Each strut is a line segment in 3D.  We sample 200 points per
    segment and take the minimum cross-pair distance; for the 3 segments
    of a regular T-prism this is accurate enough (the analytical
    closest-approach is monotone in twist near 5pi/6 and the numerical
    minimum converges to the analytical value to <0.1 mm at N=200).
    """
    segs = [(nodes[a], nodes[b]) for (a, b) in STRUTS]
    samples = []
    ts = np.linspace(0.0, 1.0, 200)
    for (p, q) in segs:
        samples.append(p[None, :] + ts[:, None] * (q - p)[None, :])
    d_min = np.inf
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            d = np.linalg.norm(samples[i][:, None, :] - samples[j][None, :, :],
                               axis=-1)
            d_min = min(d_min, float(d.min()))
    return d_min


@dataclass(frozen=True)
class PrintableDesign:
    """A printable PETG-strut + TPU-tendon Snelson cell design."""
    radius_m: float
    height_m: float
    twist_rad: float
    strut_diameter_m: float
    tendon_diameter_m: float
    prestrain: float                # fraction; 0 = slack, 0.05 = 5% prestrain

    # ------- derived quantities -------
    @property
    def nodes(self) -> np.ndarray:
        return tprism_nodes(radius=self.radius_m, height=self.height_m,
                            twist=self.twist_rad)

    @property
    def strut_length_m(self) -> float:
        n = self.nodes
        a, b = STRUTS[0]
        return float(np.linalg.norm(n[a] - n[b]))

    @property
    def cable_stiffness_Npm(self) -> float:
        # Use the *vertical* cable length (the longest of the three
        # cable families, and the one that shortens fastest under
        # axial compression).
        n = self.nodes
        L = float(np.linalg.norm(n[0] - n[3]))
        return tpu_cable_stiffness_Npm(self.tendon_diameter_m, L)

    @property
    def strut_pair_min_distance_m(self) -> float:
        return strut_pair_min_distance(self.nodes)

    @property
    def is_class_1(self) -> bool:
        """True iff struts do not interpenetrate (true tensegrity)."""
        return self.strut_diameter_m < self.strut_pair_min_distance_m

    @property
    def class_1_margin_m(self) -> float:
        """Positive: struts clear by this much. Negative: they overlap."""
        return self.strut_pair_min_distance_m - self.strut_diameter_m

    def check(self) -> list[str]:
        """Return a list of human-readable warnings for this design."""
        issues = []
        if not self.is_class_1:
            issues.append(
                f"Struts overlap by {-self.class_1_margin_m*1e3:.2f} mm "
                "(class-2: not a true tensegrity; loads bypass tendons)."
            )
        if self.tendon_diameter_m < MIN_PRINTABLE_TENDON_DIA_M:
            issues.append(
                f"Tendon dia {self.tendon_diameter_m*1e3:.2f} mm < min "
                f"printable {MIN_PRINTABLE_TENDON_DIA_M*1e3:.2f} mm on H2D "
                "(0.4 mm nozzle, 3-perimeter rule)."
            )
        if self.tendon_diameter_m > MAX_PRINTABLE_TENDON_DIA_M:
            issues.append(
                f"Tendon dia {self.tendon_diameter_m*1e3:.2f} mm > "
                f"{MAX_PRINTABLE_TENDON_DIA_M*1e3:.1f} mm; consider "
                "multi-strand TPU tendons instead of a single fat one."
            )
        if self.strut_diameter_m < MIN_PRINTABLE_STRUT_DIA_M:
            issues.append(
                f"Strut dia {self.strut_diameter_m*1e3:.2f} mm < min "
                f"printable {MIN_PRINTABLE_STRUT_DIA_M*1e3:.2f} mm."
            )
        # Cable stress at prestrain must be within TPU break stress.
        sigma = self.prestrain * TPU95A.young_MPa
        if sigma > TPU95A.yield_break_MPa:
            issues.append(
                f"Prestrain {self.prestrain*100:.1f}% gives "
                f"sigma~{sigma:.1f} MPa > TPU break {TPU95A.yield_break_MPa} MPa."
            )
        return issues


if __name__ == "__main__":
    # Two illustrative printable designs spanning the crutch and lander cells.
    crutch = PrintableDesign(
        radius_m=0.012, height_m=0.025, twist_rad=EQUILIBRIUM_TWIST,
        strut_diameter_m=3.0e-3, tendon_diameter_m=1.5e-3, prestrain=0.05)
    lander = PrintableDesign(
        radius_m=0.10, height_m=0.20, twist_rad=EQUILIBRIUM_TWIST,
        strut_diameter_m=12.0e-3, tendon_diameter_m=3.0e-3, prestrain=0.05)
    for name, d in [("crutch_tip", crutch), ("nasa_lander", lander)]:
        print(f"== {name} ==")
        print(f"  strut length            = {d.strut_length_m*1e3:6.1f} mm")
        print(f"  closest strut approach  = {d.strut_pair_min_distance_m*1e3:6.2f} mm")
        print(f"  class-1 margin          = {d.class_1_margin_m*1e3:6.2f} mm "
              f"({'OK' if d.is_class_1 else 'CLASS-2: STRUTS COLLIDE'})")
        print(f"  derived cable stiffness = {d.cable_stiffness_Npm:7.1f} N/m")
        for w in d.check():
            print(f"  WARN: {w}")
