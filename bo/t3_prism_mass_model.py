"""As-printed mass model for the T-3_01 prism family, and the constant-printed-mass projection.

Why this exists
---------------
PR #35's batch generator (``bo/t3_prism_sobol_batch.py``, branch
``copilot/get-bambu-sliced-print-t3-prism``) projects every Sobol design onto a
constant **solid** mass manifold: it uniformly re-scales the design until
``rho_PLA * V_PLA_solid + rho_TPU * V_TPU_solid`` equals
``m* = 30.95 g`` (the solid-volume mass of the S0 reference STLs), converged to
0.15 g on rendered STL volumes. That is constant solid mass, *not* constant
volume (the two materials have different densities) and *not* constant printed
mass. The 9 printed articles therefore all sit at 30.95 g solid and yet weigh
18.50 to 22.29 g on the scale, because PLA prints sparse (walls + ~24 percent
infill) while thin TPU cables print near solid, and the PLA/TPU split swings
from 20.0/10.9 g (spec 05) to 27.3/3.6 g (spec 01).

This module closes that gap: it calibrates printed grams against the 12 weighed
articles, then inverts the model so a design can be projected onto a constant
**printed** mass instead.

Two calibrations, both fit here rather than hard-coded, so they update when
articles are added to the print key:

1. *Analytic volume model vs rendered STL volumes.* The analytic estimate in
   PR #35's generator is documented as +/-10 percent because boolean overlaps
   are ignored. Regressing it against the rendered ``pla_g``/``tpu_g`` in
   ``t3-prism-bo-batch.csv`` (9 designs, all at the converged scale) gives one
   correction factor per material, after which it reproduces rendered solid
   grams to within ~0.5 g PLA and ~0.11 g TPU. That removes OpenSCAD from the
   BO loop entirely.
2. *Rendered solid grams vs the scale.* A wall-plus-infill model,

       m_printed = m_PLA_solid * [i + (1 - i) * (1 - (1 - 2w/d_strut)^2)]
                 + m_TPU_solid * f_TPU

   where ``i`` is the effective infill fraction, ``w`` the PLA wall thickness
   and ``d_strut`` the as-printed strut diameter. The strut-diameter term is
   what makes this beat a flat pair of density factors: a 6.4 mm strut is
   proportionally more wall than a 9.2 mm one, so it prints denser. ``f_TPU``
   is a lumped factor, not a literal density: it also absorbs TPU flow bias and
   any systematic error in the analytic cable volume.

Fitted on the 12 weighed articles the residual sd is ~0.38 g, at or below the
0.457 g print-to-print scatter measured from the spec-08 triplicate
(dea4ls/bag26v/ghmj4y, one design printed three times). In other words the
model is as accurate as the process is repeatable, which is the point to stop
refining it. A flat two-density fit (56.5 percent PLA, 99.6 percent TPU)
leaves 0.93 g, twice the print scatter, and is reported alongside for contrast.

Infill as an input rather than a fitted constant
-----------------------------------------------
The two infill percentages are BO design variables from round 3 on (PR #102,
2026-08-26), so the model has to answer "how big does this design have to be to
still weigh 20.23 g if I print the struts at 40 percent instead of 15?". Both
tested plates were sliced at the same 15 percent grid sparse infill, so there is
no data with which to fit an infill response; the model carries a stated
first-order assumption instead.

* *Struts (PLA).* The fitted ``infill`` is 23.6 percent while the slicer was set
  to 15, because it also absorbs the three solid top and bottom shells at each
  strut end, the joint shells and any flow bias. Moving the slicer's density is
  modeled as moving the effective value point for point, which holds that
  non-infill remainder fixed.
* *Cables and captive cores (TPU).* ``f_TPU`` is one lumped factor over both TPU
  bodies, so the analytic TPU volume is split into tendons and the six captive
  cores and only the cores respond: at 3 to 5 mm printed a tendon is a few line
  widths across and prints solid at any density, while a 7 to 10 mm captive core
  is mostly infill, which is why the lock ball photographed on issue #85 came
  out hollow. The core term is carried as the ratio of wall-plus-infill solid
  fractions against the nominal setting.

Both terms are exactly 1.0 (no change) at ``NOMINAL_INFILL_PCT``, so every
number this module produced before infill became a variable is reproduced
byte for byte. Over the round-3 bounds the strut density moves the solved scale
by about -9 to +1 percent and the TPU density by about -1 percent; run this
module for the sweep. The round-3 weighings are the first data that can check
either assumption, and they should be fed back here before round 4.

Not modeled: purge/flush and the prime tower (multi-material plate waste is not
part of an article's weighed mass, so it should not be), and per-print defects
(``dea4ls`` carries residual PLA on a tendon and is the largest positive
residual at +0.7 g).

Run ``python bo/t3_prism_mass_model.py`` for the calibration report.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

BO_DIR = Path(__file__).resolve().parent

# Solid densities and fixed geometry, identical to PR #35's generator.
RHO_PLA = 1.24e-3  # g/mm^3, Bambu PLA Basic
RHO_TPU = 1.21e-3  # g/mm^3, Bambu TPU 85A
JOINT_D_BASE = 7.0  # mm, frozen; scales with the projection like every dimension
# PLA mass of the six absolute-size sensor housings (3 igloo mounts + 3 bottom
# key-seats). These do NOT scale, so they are a constant offset in every mass
# balance. Value from t3-prism-bo-batch.json (PR #35), constraints.housing_mass_g.
HOUSING_MASS_G = 6.76107521259489
# Solid-mass target the printed batch was actually built to (PR #35 Route A).
SOLID_MASS_TARGET_G = 30.94789906161643
# Default constant-printed-mass target: the weighed mass of the S0 reference
# article bpx68c. Round 1 anchored its solid target to the S0 reference design,
# so anchoring the printed target to the same article keeps the reference
# comparable across rounds. Override with --target-mass-g.
DEFAULT_PRINTED_MASS_TARGET_G = 20.23
# Slicer sparse infill density every calibration article was printed at: 15
# percent grid, inherited from Bambu's stock "0.30mm Standard @BBL H2D 0.6
# nozzle" process profile and identical in both tested plates (verified in
# Metadata/project_settings.config of the round-1 and round-2 .3mf projects).
# The infill-aware terms below are differentials around this point, so the
# calibrated model is reproduced exactly when a design sits at it.
NOMINAL_INFILL_PCT = 15.0

PARAM_NAMES = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]


def captive_core_od(params: dict) -> float:
    """Captive-core (TPU lock ball) outer diameter in mm at scale 1."""
    return max(params["cable_d_mm"] + 3.0, JOINT_D_BASE)


def joint_shell_od(params: dict) -> float:
    """Outer diameter in mm at scale 1 of the six PLA joint shells.

    This, not the strut, is what sets an article's footprint on the plate:
    the circumscribing cylinder is ``2 * R + shell_od`` wide.
    """
    return max(captive_core_od(params) + 3.2, JOINT_D_BASE)


def analytic_body_volumes_split(params: dict) -> tuple[float, float, float]:
    """(V_PLA, V_TPU_cable, V_TPU_core) in mm^3 at scale 1, housings EXCLUDED.

    Ported verbatim from ``estimate_body_mass_g`` in PR #35's
    ``bo/t3_prism_sobol_batch.py`` (split by material instead of summed), with
    the TPU term further split into the tendons and the six captive cores.
    The split matters because those two TPU bodies respond to sparse infill in
    opposite ways: a 3 to 5 mm tendon is a few line widths across and prints
    solid whatever the infill is, while a 7 to 10 mm captive core is mostly
    infill (the hollow lock ball photographed on issue #85).
    """
    R, H, tw = params["R_mm"], params["H_mm"], params["twist_deg"]
    sd, cd, jd = params["strut_d_mm"], params["cable_d_mm"], JOINT_D_BASE
    l_strut = math.hypot(2 * R * math.sin(math.radians(tw / 2)), H)
    l_side = R * math.sqrt(3)
    b1 = (R * math.cos(math.radians(210)), R * math.sin(math.radians(210)), 0.0)
    t0 = (R * math.cos(math.radians(90 + tw)), R * math.sin(math.radians(90 + tw)), H)
    l_saddle = math.dist(b1, t0)
    core_od = max(cd + 3.0, jd)
    shell_od = max(core_od + 3.2, jd)
    v_pla = 3 * (math.pi * sd * sd / 4 * l_strut + 0.7 * (4 / 3) * math.pi * (sd / 2) ** 3)
    v_pla += 6 * (4 / 3) * math.pi * ((shell_od / 2) ** 3 - (core_od / 2) ** 3)
    v_cable = 0.97 * math.pi * cd * cd / 4 * (6 * l_side + 3 * l_saddle)
    v_core = 0.85 * 6 * (4 / 3) * math.pi * (core_od / 2) ** 3
    return v_pla, v_cable, v_core


def analytic_body_volumes(params: dict) -> tuple[float, float]:
    """(V_PLA, V_TPU) in mm^3 at scale 1, EXCLUDING the absolute-size housings."""
    v_pla, v_cable, v_core = analytic_body_volumes_split(params)
    return v_pla, v_cable + v_core


@dataclass(frozen=True)
class MassModel:
    """Calibrated map from (base coordinates, uniform scale) to printed grams."""

    k_pla: float       # analytic -> rendered solid-volume correction, PLA
    k_tpu: float       # analytic -> rendered solid-volume correction, TPU
    infill: float      # effective PLA infill fraction
    wall_mm: float     # effective PLA wall thickness
    f_tpu: float       # lumped TPU solid fraction (also absorbs flow bias)
    resid_sd_g: float  # printed-mass residual sd on the calibration articles
    n_articles: int
    flat_resid_sd_g: float  # same, for the flat two-density fit (for contrast)
    flat_f_pla: float
    flat_f_tpu: float

    # -- solid side -------------------------------------------------------
    def solid_grams_split(self, params: dict,
                          scale: float) -> tuple[float, float, float]:
        """(PLA g, TPU tendon g, TPU captive-core g) of the solid geometry.

        Every dimension including the joint diameter scales, so the body terms
        are exactly cubic in ``scale``; only the housings stay put.
        """
        v_pla, v_cable, v_core = analytic_body_volumes_split(params)
        pla = RHO_PLA * self.k_pla * v_pla * scale ** 3 + HOUSING_MASS_G
        cable = RHO_TPU * self.k_tpu * v_cable * scale ** 3
        core = RHO_TPU * self.k_tpu * v_core * scale ** 3
        return pla, cable, core

    def solid_grams(self, params: dict, scale: float) -> tuple[float, float]:
        """(PLA g, TPU g) of the solid geometry at ``scale``, housings included."""
        pla, cable, core = self.solid_grams_split(params, scale)
        return pla, cable + core

    # -- printed side -----------------------------------------------------
    def _wall_fraction(self, infill: float, d_print_mm: float) -> float:
        """Wall-plus-infill solid fraction of a round member of diameter ``d``."""
        core = max(1.0 - 2.0 * self.wall_mm / d_print_mm, 0.0)
        return infill + (1.0 - infill) * (1.0 - core ** 2)

    def pla_solid_fraction(self, strut_d_print_mm: float,
                           strut_infill_pct: float | None = None) -> float:
        """Effective printed/solid density ratio for PLA at a given strut Ø.

        ``self.infill`` is the *effective* infill fitted at the one nominal
        slicer setting every calibration article was printed at
        (``NOMINAL_INFILL_PCT``); it sits above that nominal value because it
        also absorbs the solid top and bottom shells, the joint shells and any
        flow bias. Changing the slicer's sparse infill density is modeled as a
        point-for-point shift of the effective value, which holds that
        non-infill remainder fixed. At ``strut_infill_pct = NOMINAL_INFILL_PCT``
        this reproduces the calibrated model exactly.
        """
        infill = self.infill
        if strut_infill_pct is not None:
            infill = min(max(
                self.infill + (strut_infill_pct - NOMINAL_INFILL_PCT) / 100.0,
                0.0), 1.0)
        return self._wall_fraction(infill, strut_d_print_mm)

    def tpu_core_factor(self, core_d_print_mm: float,
                        tpu_infill_pct: float | None = None) -> float:
        """Multiplier on the captive cores' share of ``f_tpu`` at a given infill.

        ``f_tpu`` is a single lumped factor fitted over both TPU bodies at the
        nominal infill, so a change in TPU infill is carried as the *ratio* of
        wall-plus-infill solid fractions for a member the size of a captive
        core. Equals 1.0 at the nominal setting, which leaves the calibration
        untouched. The tendons are left alone: at 3 to 5 mm printed they are a
        few line widths across and print solid at any infill.
        """
        if tpu_infill_pct is None:
            return 1.0
        base = self._wall_fraction(NOMINAL_INFILL_PCT / 100.0, core_d_print_mm)
        if base <= 0.0:
            return 1.0
        return self._wall_fraction(tpu_infill_pct / 100.0, core_d_print_mm) / base

    def printed_mass_g(self, params: dict, scale: float,
                       strut_infill_pct: float | None = None,
                       tpu_infill_pct: float | None = None) -> float:
        pla, cable, core = self.solid_grams_split(params, scale)
        frac = self.pla_solid_fraction(params["strut_d_mm"] * scale,
                                       strut_infill_pct)
        g_core = self.tpu_core_factor(captive_core_od(params) * scale,
                                      tpu_infill_pct)
        return pla * frac + self.f_tpu * (cable + core * g_core)

    def printed_mass_from_solid(self, pla_g: float, tpu_g: float,
                                strut_d_print_mm: float) -> float:
        """Printed grams from *rendered* solid grams (used in calibration)."""
        return pla_g * self.pla_solid_fraction(strut_d_print_mm) + tpu_g * self.f_tpu

    # -- the projection ---------------------------------------------------
    def solve_scale_for_printed_mass(self, params: dict, target_g: float,
                                     tol_g: float = 1e-4,
                                     strut_infill_pct: float | None = None,
                                     tpu_infill_pct: float | None = None) -> float:
        """Uniform scale ``s`` such that ``printed_mass_g(params, s) == target``.

        Monotone increasing in ``s`` (the body terms are cubic, the housing
        offset is positive and its density factor rises with strut Ø), so a
        plain bisection on a bracketed interval is enough. Returns nan if the
        target is unreachable inside a generous scale range, which happens when
        the housings alone already outweigh the target.
        """
        def m(s):
            return self.printed_mass_g(params, s, strut_infill_pct, tpu_infill_pct)

        lo, hi = 1e-3, 20.0
        if m(lo) > target_g:
            return float("nan")
        if m(hi) < target_g:
            return float("nan")
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if m(mid) < target_g:
                lo = mid
            else:
                hi = mid
            if hi - lo < 1e-9:
                break
        s = 0.5 * (lo + hi)
        if abs(m(s) - target_g) > tol_g:
            return float("nan")
        return s

    def project(self, params: dict, target_g: float,
                strut_infill_pct: float | None = None,
                tpu_infill_pct: float | None = None) -> dict:
        """Project base coordinates onto the constant-printed-mass manifold.

        Returns the as-printed geometry plus the constraint columns PR #35's
        generator reports, so a suggestion can be checked for printability
        before anything is rendered. The two infill arguments are the slicer's
        sparse infill density for the strut (PLA) and cable (TPU) parts; they
        move the solved scale, because a sparser article has to be larger to
        weigh the same.
        """
        s = self.solve_scale_for_printed_mass(
            params, target_g, strut_infill_pct=strut_infill_pct,
            tpu_infill_pct=tpu_infill_pct)
        if not math.isfinite(s):
            return {"scale": float("nan")}
        pla, tpu = self.solid_grams(params, s)
        out = {
            "scale": s,
            "R_print_mm": params["R_mm"] * s,
            "H_print_mm": params["H_mm"] * s,
            "strut_d_print_mm": params["strut_d_mm"] * s,
            "cable_d_print_mm": params["cable_d_mm"] * s,
            "joint_d_print_mm": JOINT_D_BASE * s,
            "core_d_print_mm": captive_core_od(params) * s,
            "shell_d_print_mm": joint_shell_od(params) * s,
            "solid_mass_g": pla + tpu,
            "printed_mass_g": self.printed_mass_g(
                params, s, strut_infill_pct, tpu_infill_pct),
        }
        # Same definitions as PR #35: envelope is the circumscribing cylinder,
        # the cable floor is the TPU self-bridging threshold from Edison 25c1c897.
        out["footprint_d_mm"] = 2 * out["R_print_mm"] + out["shell_d_print_mm"]
        out["envelope_cm3"] = math.pi * out["R_print_mm"] ** 2 * out["H_print_mm"] / 1000.0
        out["envelope_ok"] = out["envelope_cm3"] <= 250.0
        out["cable_bridge_ok"] = out["cable_d_print_mm"] >= 3.0
        return out


def _load_calibration_frames(bo_dir: Path = BO_DIR):
    design = pd.read_csv(bo_dir / "t3-prism-bo-batch.csv").set_index("specimen")
    key = pd.read_csv(bo_dir / "t3-prism-bo-batch-print-key.csv",
                      dtype={"specimen": "string"})
    return design, key


def calibrate(bo_dir: Path = BO_DIR) -> MassModel:
    """Fit both stages from the committed batch table and print key."""
    design, key = _load_calibration_frames(bo_dir)

    # Stage 1: analytic body volumes -> rendered solid grams (9 designs).
    a_pla, a_tpu, r_pla, r_tpu = [], [], [], []
    for spec, row in design.iterrows():
        params = {n: float(row[n]) for n in PARAM_NAMES}
        v_pla, v_tpu = analytic_body_volumes(params)
        s3 = float(row["scale"]) ** 3
        a_pla.append(RHO_PLA * v_pla * s3)
        a_tpu.append(RHO_TPU * v_tpu * s3)
        r_pla.append(float(row["pla_g"]) - HOUSING_MASS_G)
        r_tpu.append(float(row["tpu_g"]))
    k_pla = float(np.dot(a_pla, r_pla) / np.dot(a_pla, a_pla))
    k_tpu = float(np.dot(a_tpu, r_tpu) / np.dot(a_tpu, a_tpu))

    # Stage 2: rendered solid grams -> weighed printed grams (all weighed
    # articles, including all three spec-08 prints so the print scatter carries
    # its real weight, and the S0 reference whose solid split comes from stage 1).
    s0_params = {"R_mm": 25.0, "H_mm": 70.0, "twist_deg": 60.0,
                 "strut_d_mm": 6.0, "cable_d_mm": 3.0}
    s0_scale = 1.1538  # issue #98, 2026-08-17: S0 printed at uniform 1.1538
    stage1 = MassModel(k_pla, k_tpu, 0.0, 0.0, 1.0, float("nan"), 0,
                       float("nan"), float("nan"), float("nan"))
    s0_pla, s0_tpu = stage1.solid_grams(s0_params, s0_scale)

    pla_g, tpu_g, d_print, weighed = [], [], [], []
    for _, row in key.iterrows():
        spec = str(row["specimen"])
        if spec == "S0":
            p, t, d = s0_pla, s0_tpu, s0_params["strut_d_mm"] * s0_scale
        else:
            q = design.loc[int(spec)]
            p, t, d = float(q["pla_g"]), float(q["tpu_g"]), float(q["strut_d_print_mm"])
        pla_g.append(p)
        tpu_g.append(t)
        d_print.append(d)
        weighed.append(float(row["mass_g"]))
    pla_g = np.asarray(pla_g)
    tpu_g = np.asarray(tpu_g)
    d_print = np.asarray(d_print)
    weighed = np.asarray(weighed)

    def residuals(theta):
        i, w, ft = theta
        core = np.clip(1.0 - 2.0 * w / d_print, 0.0, None)
        frac = i + (1.0 - i) * (1.0 - core ** 2)
        return weighed - (pla_g * frac + tpu_g * ft)

    from scipy.optimize import least_squares

    sol = least_squares(residuals, [0.30, 0.90, 0.90],
                        bounds=([0.0, 0.2, 0.6], [0.9, 3.0, 1.05]))
    infill, wall, f_tpu = (float(v) for v in sol.x)
    dof = max(len(weighed) - 3, 1)
    resid_sd = float(np.sqrt(np.sum(residuals(sol.x) ** 2) / dof))

    # Flat two-density fit, kept only so the report can show what the strut
    # diameter term buys.
    flat = np.linalg.lstsq(np.column_stack([pla_g, tpu_g]), weighed, rcond=None)[0]
    flat_resid = weighed - np.column_stack([pla_g, tpu_g]) @ flat
    flat_sd = float(np.sqrt(np.sum(flat_resid ** 2) / max(len(weighed) - 2, 1)))

    return MassModel(k_pla=k_pla, k_tpu=k_tpu, infill=infill, wall_mm=wall,
                     f_tpu=f_tpu, resid_sd_g=resid_sd, n_articles=len(weighed),
                     flat_resid_sd_g=flat_sd, flat_f_pla=float(flat[0]),
                     flat_f_tpu=float(flat[1]))


def calibration_report(model: MassModel, target_g: float = DEFAULT_PRINTED_MASS_TARGET_G,
                       bo_dir: Path = BO_DIR) -> str:
    design, key = _load_calibration_frames(bo_dir)
    lines = [
        "T-3_01 printed-mass model",
        "=" * 78,
        f"  analytic -> rendered solid: k_PLA = {model.k_pla:.4f}, k_TPU = {model.k_tpu:.4f}",
        f"  wall + infill:  infill = {model.infill * 100:.1f} %, "
        f"wall = {model.wall_mm:.2f} mm, f_TPU = {model.f_tpu:.3f}",
        f"  effective PLA printed/solid density: "
        f"{model.pla_solid_fraction(9.3):.3f} at a 9.3 mm strut to "
        f"{model.pla_solid_fraction(6.4):.3f} at a 6.4 mm strut",
        f"  residual sd = {model.resid_sd_g:.3f} g over {model.n_articles} weighed "
        f"articles (print-to-print scatter 0.457 g)",
        f"  flat two-density fit for contrast: {model.flat_f_pla:.3f} PLA / "
        f"{model.flat_f_tpu:.3f} TPU, residual sd {model.flat_resid_sd_g:.3f} g",
        "",
        f"Round-1 articles re-projected onto constant printed mass {target_g:.2f} g",
        "-" * 78,
        f"{'spec':>4} {'weighed':>8} {'scale old':>10} {'scale new':>10} "
        f"{'R_pr':>7} {'H_pr':>7} {'strut':>6} {'cable':>6} {'env cm3':>8}  flags",
    ]
    weighed_by_spec = (key[key["specimen"] != "S0"]
                       .assign(spec=lambda d: d["specimen"].astype(int))
                       .groupby("spec")["mass_g"].mean())
    for spec, row in design.iterrows():
        params = {n: float(row[n]) for n in PARAM_NAMES}
        pr = model.project(params, target_g)
        flags = []
        if not pr.get("envelope_ok", True):
            flags.append("envelope>250")
        if not pr.get("cable_bridge_ok", True):
            flags.append("cable<3.0")
        w = weighed_by_spec.get(spec, float("nan"))
        lines.append(
            f"{spec:>4} {w:>8.2f} {row['scale']:>10.4f} {pr['scale']:>10.4f} "
            f"{pr['R_print_mm']:>7.2f} {pr['H_print_mm']:>7.2f} "
            f"{pr['strut_d_print_mm']:>6.2f} {pr['cable_d_print_mm']:>6.2f} "
            f"{pr['envelope_cm3']:>8.1f}  {', '.join(flags) or 'ok'}"
        )

    # What the two infill knobs do to the projection, on the S0 reference.
    s0 = {"R_mm": 25.0, "H_mm": 70.0, "twist_deg": 60.0,
          "strut_d_mm": 6.0, "cable_d_mm": 3.0}
    lines += [
        "",
        f"Infill sweep on the S0 reference design at {target_g:.2f} g printed",
        "-" * 78,
        f"  {'strut %':>7} {'TPU %':>6} {'scale':>7} {'strut Ø':>8} "
        f"{'core Ø':>7} {'env cm3':>8} {'vs 15/15':>9}",
    ]
    ref = model.project(s0, target_g, NOMINAL_INFILL_PCT, NOMINAL_INFILL_PCT)
    # corners of the round-3 process bounds (12 to 35 percent since the
    # 2026-08-31 tightening; the old 10 to 60 corners are extrapolations no
    # batch will print)
    for si, ti in ((12, 15), (NOMINAL_INFILL_PCT, NOMINAL_INFILL_PCT),
                   (25, 15), (35, 15), (15, 35), (35, 35)):
        pr = model.project(s0, target_g, si, ti)
        lines.append(
            f"  {si:>7.0f} {ti:>6.0f} {pr['scale']:>7.4f} "
            f"{pr['strut_d_print_mm']:>8.2f} {pr['core_d_print_mm']:>7.2f} "
            f"{pr['envelope_cm3']:>8.1f} "
            f"{100 * (pr['scale'] / ref['scale'] - 1):>8.1f} %"
        )
    lines += [
        "  Read the last column as: at a fixed printed mass, a sparser article "
        "has to be bigger",
        "  and a denser one smaller. The strut infill moves the scale by a few "
        "percent over its",
        "  whole range; the TPU infill barely moves it, because the captive "
        "cores are a small",
        "  share of the mass. Both are extrapolations away from the single "
        "nominal setting",
        f"  ({NOMINAL_INFILL_PCT:.0f} percent) the model was calibrated at, and "
        "the round-3 weighings are what test them.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--target-mass-g", type=float,
                    default=DEFAULT_PRINTED_MASS_TARGET_G)
    args = ap.parse_args()
    print(calibration_report(calibrate(), args.target_mass_g))
