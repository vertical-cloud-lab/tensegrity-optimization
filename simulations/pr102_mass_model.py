"""Constant-*printed*-mass projection, ported from PR #102's ``t3_prism_mass_model``.

Why this file exists, and why it replaces ``print_infill.project_constant_mass``
in the PR #102 objective path
-----------------------------------------------------------------------------
``drop_tower_sim.evaluate_pr102`` originally projected a base Sobol design onto
PR #35's Route-A manifold: uniformly rescale until the *solid* CAD mass equals
30.95 g.  That is what the round-1 batch was built to, and it is not constant
printed mass -- the nine articles all sit at 30.95 g solid and weigh 18.50 to
22.29 g on the scale, because PLA prints sparse and TPU prints near solid and
the PLA/TPU split moves with the shape.

That leak is fatal for the second objective.  ``e_reb_mJ = e_rebound * m * g * h``
is an *absolute* energy by design (PR #102 keeps it absolute deliberately: a
lighter article returning the same velocity fraction returns less energy to the
payload).  With mass free to swing, the objective becomes the mass.  Measured on
the 68,944-design reference sweep with the old projection: rho(e_reb_mJ, mass_g)
= 0.99993, simulated ``e_rebound`` spanning 0.34 % against mass spanning 32 %.
Minimizing ``e_reb_mJ`` was minimizing printed mass and nothing else.

PR #102 closed this in commit 2f1ca2e by projecting onto constant *printed* mass
and carrying ``mass_printed_g`` as a sixth BO parameter inside a narrow slab
(target +/- 0.457 g, the spec-08 triplicate scatter), so competing designs are
compared at the same mass and ``e_reb_mJ`` is back to measuring restitution.
This module is that projection, calibrated here from the same committed CSVs
(``simulations/data/pr102/``) so the numbers are traceable rather than copied.

The model itself is PR #102's, unchanged: a two-stage fit (analytic body volumes
to rendered solid grams, then rendered solid grams to weighed printed grams
through a wall-plus-infill law whose PLA solid fraction depends on the printed
strut diameter), with the six absolute-size sensor housings carried as a
non-scaling mass offset.  It is worth porting rather than reusing
``print_infill``'s two flat solidity factors: PR #102 reports that flat fit as
its own contrast case at 0.93 g residual sd, twice the print-to-print scatter,
against 0.38 g for this one.  ``print_infill`` stays in place for the effective
strut *density and modulus* the simulator needs, which is a different question
from as-printed grams.

Run ``python pr102_mass_model.py`` for the calibration report.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

BO_DIR = Path(__file__).resolve().parent / "data" / "pr102"

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

PARAM_NAMES = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]


def analytic_body_volumes(params: dict) -> tuple[float, float]:
    """(V_PLA, V_TPU) in mm^3 at scale 1, EXCLUDING the absolute-size housings.

    Ported verbatim from ``estimate_body_mass_g`` in PR #35's
    ``bo/t3_prism_sobol_batch.py`` (split by material instead of summed).
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
    v_tpu = 0.97 * math.pi * cd * cd / 4 * (6 * l_side + 3 * l_saddle)
    v_tpu += 0.85 * 6 * (4 / 3) * math.pi * (core_od / 2) ** 3
    return v_pla, v_tpu


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
    def solid_grams(self, params: dict, scale: float) -> tuple[float, float]:
        """(PLA g, TPU g) of the solid geometry at ``scale``, housings included.

        Every dimension including the joint diameter scales, so the body terms
        are exactly cubic in ``scale``; only the housings stay put.
        """
        v_pla, v_tpu = analytic_body_volumes(params)
        pla = RHO_PLA * self.k_pla * v_pla * scale ** 3 + HOUSING_MASS_G
        tpu = RHO_TPU * self.k_tpu * v_tpu * scale ** 3
        return pla, tpu

    # -- printed side -----------------------------------------------------
    def pla_solid_fraction(self, strut_d_print_mm: float) -> float:
        """Effective printed/solid density ratio for PLA at a given strut Ø."""
        core = max(1.0 - 2.0 * self.wall_mm / strut_d_print_mm, 0.0)
        return self.infill + (1.0 - self.infill) * (1.0 - core ** 2)

    def printed_mass_g(self, params: dict, scale: float) -> float:
        pla, tpu = self.solid_grams(params, scale)
        frac = self.pla_solid_fraction(params["strut_d_mm"] * scale)
        return pla * frac + tpu * self.f_tpu

    def printed_mass_from_solid(self, pla_g: float, tpu_g: float,
                                strut_d_print_mm: float) -> float:
        """Printed grams from *rendered* solid grams (used in calibration)."""
        return pla_g * self.pla_solid_fraction(strut_d_print_mm) + tpu_g * self.f_tpu

    # -- the projection ---------------------------------------------------
    def solve_scale_for_printed_mass(self, params: dict, target_g: float,
                                     tol_g: float = 1e-4) -> float:
        """Uniform scale ``s`` such that ``printed_mass_g(params, s) == target``.

        Monotone increasing in ``s`` (the body terms are cubic, the housing
        offset is positive and its density factor rises with strut Ø), so a
        plain bisection on a bracketed interval is enough. Returns nan if the
        target is unreachable inside a generous scale range, which happens when
        the housings alone already outweigh the target.
        """
        lo, hi = 1e-3, 20.0
        if self.printed_mass_g(params, lo) > target_g:
            return float("nan")
        if self.printed_mass_g(params, hi) < target_g:
            return float("nan")
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if self.printed_mass_g(params, mid) < target_g:
                lo = mid
            else:
                hi = mid
            if hi - lo < 1e-9:
                break
        s = 0.5 * (lo + hi)
        if abs(self.printed_mass_g(params, s) - target_g) > tol_g:
            return float("nan")
        return s

    def project(self, params: dict, target_g: float) -> dict:
        """Project base coordinates onto the constant-printed-mass manifold.

        Returns the as-printed geometry plus the constraint columns PR #35's
        generator reports, so a suggestion can be checked for printability
        before anything is rendered.
        """
        s = self.solve_scale_for_printed_mass(params, target_g)
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
            "solid_mass_g": pla + tpu,
            "printed_mass_g": self.printed_mass_g(params, s),
        }
        # Same definitions as PR #35: envelope is the circumscribing cylinder,
        # the cable floor is the TPU self-bridging threshold from Edison 25c1c897.
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
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--target-mass-g", type=float,
                    default=DEFAULT_PRINTED_MASS_TARGET_G)
    args = ap.parse_args()
    print(calibration_report(calibrate(), args.target_mass_g))
