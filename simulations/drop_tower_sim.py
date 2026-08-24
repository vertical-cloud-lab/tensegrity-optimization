"""MuJoCo analogue of the T-3_01 drop-tower test, in the PR #102 objectives.

Everything else in this directory scores a design on ``F_peak`` / ``SEA`` /
``eta`` under one of the two application regimes (crutch, lander).  The
campaign actually running on the bench (PR #102, data from PR #86) scores it
on two *different* numbers, measured on a Lansmont M23 at 60 in with a 1/2 in
PU mat:

``t180``
    CFC-180 transmissibility ``TOP / CH5``: the ratio of the filtered peak
    acceleration at the article's free top vertex to the filtered peak at
    the base plate it is mounted on.  Channel roles are from PR #67's
    input-output series (CH5 = single-axis sensor on the bottom acrylic
    plate = input; tri-axis hot-glued to the top vertex = output).
    Minimized.
``e_reb_mJ``
    ``e_rebound * m_printed * g * h`` with h = 1.524 m.  ``e_rebound`` is
    reported by the campaign pipeline as a restitution *velocity* ratio: the
    committed summary satisfies ``t_second = 2 * e_rebound * v_in / g`` to
    three digits on every specimen, i.e. it is the coefficient of restitution
    read off the time to the second impact.  Minimized.

This module reproduces both from a simulation, so a simulated design and a
tested article land in the same two-number objective space.  The model:

* A **carriage** (the falling base-plate assembly) on a vertical slide
  joint, i.e. the tower's guide rails.  It carries the CH5 site.
* A **PU mat** modeled as an explicit one-sided Hunt-Crossley contact
  applied to the carriage, ``F = k d + lambda d (-d_dot)`` for ``d > 0``,
  clipped at zero so the mat never pulls.  The damping term is proportional
  to penetration, not just to velocity: a plain Kelvin-Voigt mat delivers a
  ``c * v_impact`` force step at first touch, which at this closing speed is
  a larger spike than the pulse it is supposed to damp, and it puts the
  input peak under the control of the damping rather than the stiffness.
  Both parameters are calibrated once (``--calibrate``) against the measured
  input peak and restitution of the S0 reference article, then held fixed
  for every design.  Modeling the mat explicitly rather than through a
  contact pair is deliberate: the mat sets the input pulse, so it has to be
  *the calibrated thing*, and MuJoCo's solref/solimp do not map onto
  (peak, restitution) as directly.
* The **article**: three rigid PLA strut capsules at the printed density
  (``print_infill``: about 57 % of solid, so a 6 mm strut weighs what the
  scale says, not what solid PLA would), nine TPU tendons as spatial
  tendons with the ``printable_design`` axial stiffness, and the three
  bottom vertices tied to the carriage by ball anchors, which is what
  gluing a vertex to the plate does.  A 5 g accelerometer mass rides the
  measured top vertex.

What it does not model, stated so the correlation study is read correctly:
strut flexure (Tier C treats struts as rigid, so the article's own bending
modes are absent, and those are exactly what the 294 to 468 Hz ringdown
fits see), the mount's own compliance, tendon hysteresis, and any
mat-state or session drift.

Usage::

    python drop_tower_sim.py                 # S0 reference article
    python drop_tower_sim.py --calibrate     # refit the mat to the bench
    python drop_tower_sim.py --spec 1        # a Sobol batch design
"""
from __future__ import annotations

import argparse
import math
import textwrap
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from bo_evaluator import _cfc_filter, parameterization_to_design
from print_infill import (PLA_SOLIDITY, TPU_SOLIDITY, effective_pla_density_kgm3,
                          printed_mass_cad, project_constant_mass, scale_design)
from pr102_mass_model import (DEFAULT_PRINTED_MASS_TARGET_G, PARAM_NAMES,
                              calibrate as calibrate_mass_model)
from printable_design import PrintableDesign
from tprism_geometry import CABLES, STRUTS, tprism_nodes

G = 9.80665
DROP_H_M = 1.524              # 60 in, the campaign SOP
IMPACT_V_MPS = 5.30           # measured campaign mean in_dv (5.03 to 5.45)

# --- carriage + mat -------------------------------------------------------
# The carriage mass and the mat stiffness only enter the pulse through their
# ratio, so the mass is fixed at a nominal value for the falling base-plate
# assembly and the mat is calibrated against it.  Changing one without the
# other rescales the input peak.
CARRIAGE_MASS_KG = 2.0
MAT_THICKNESS_M = 0.0127      # 1/2 in PU mat
ACCEL_MASS_KG = 0.005         # tri-axis accelerometer + hot glue at the vertex

# Calibrated on the S0 reference article (bpx68c) by ``--calibrate``, on the
# constant-printed-mass manifold at its weighed 20.23 g; see the module
# docstring.  Units: stiffness N/m, damping N s/m^2 (the
# Hunt-Crossley coefficient multiplies penetration times velocity).
MAT_STIFFNESS_NPM = 3.184e5
MAT_DAMPING_NSPM = 5.392e4

# Tendon prestrain.  The printed article's tendons are taut at the
# equilibrium twist; a small prestrain is what stops the three ball-anchored
# rigid struts from being a mechanism at t = 0.
DEFAULT_PRESTRAIN = 0.02

# Tendon damping ratio used to size the viscous term on each cable.  This is
# an *input dial*, not a material property: zeta_analysis.py measures how the
# article's emergent modal damping responds to it and to the design.
DEFAULT_CABLE_ZETA = 0.02

SIM_DT_S = 2.0e-5             # 50 kHz, well above the CFC-1000 corner
SIM_DURATION_S = 0.040


@dataclass(frozen=True)
class MatModel:
    stiffness_Npm: float = MAT_STIFFNESS_NPM
    damping_Nspm: float = MAT_DAMPING_NSPM
    thickness_m: float = MAT_THICKNESS_M


def build_xml(design: PrintableDesign, *, prestrain: float = DEFAULT_PRESTRAIN,
              carriage_mass_kg: float = CARRIAGE_MASS_KG,
              pla_solidity: float = PLA_SOLIDITY,
              article_mass_g: float | None = None,
              cable_zeta: float = DEFAULT_CABLE_ZETA) -> str:
    """MJCF for one article mounted on the sliding carriage.

    ``article_mass_g`` pins the total mass of the three strut capsules to a
    weighed (or model-predicted as-printed) value.  The capsules are the only
    massive part of the article here -- the tendons are massless spatial
    tendons and the PLA joints and sensor housings are not separate bodies --
    so putting the whole as-printed mass on them is what makes the simulated
    inertia agree with the scale, and inertia is what sets transmissibility on
    a base-excited structure.  Left ``None``, the capsules carry only
    ``print_infill``'s effective sparse-PLA density and the article comes out
    light by the joint/housing share.
    """
    nodes = tprism_nodes(radius=design.radius_m, height=design.height_m,
                         twist=design.twist_rad, z0=0.0)
    plate_half = max(design.radius_m * 1.6, 0.03)
    plate_t = 0.006
    # carriage top face at z = 0; the article sits on it
    strut_density = effective_pla_density_kgm3(pla_solidity)
    if article_mass_g is not None:
        # capsule volume = pi r^2 L + 4/3 pi r^3, summed over the three struts
        r = design.strut_diameter_m * 0.5
        v_caps = 0.0
        for a, b in STRUTS:
            L = float(np.linalg.norm(nodes[a] - nodes[b]))
            v_caps += math.pi * r * r * L + (4.0 / 3.0) * math.pi * r ** 3
        if v_caps > 0.0:
            strut_density = float(article_mass_g) * 1e-3 / v_caps

    # the measured top vertex: the top end of strut 0
    a0, b0 = STRUTS[0]
    top_node = a0 if nodes[a0][2] > nodes[b0][2] else b0

    bodies = []
    for s_idx, (a, b) in enumerate(STRUTS):
        pa, pb = nodes[a], nodes[b]
        center = 0.5 * (pa + pb)
        sa, sb = pa - center, pb - center
        extra = ""
        if s_idx == 0:
            tip = sa if a == top_node else sb
            extra = (f'<geom name="accel" type="sphere" size="0.004" '
                     f'pos="{tip[0]:.6f} {tip[1]:.6f} {tip[2]:.6f}" '
                     f'mass="{ACCEL_MASS_KG}" contype="0" conaffinity="0" '
                     f'rgba="0.95 0.85 0.1 1"/>')
        bodies.append(textwrap.dedent(f"""
            <body name="strut{s_idx}" pos="{center[0]:.6f} {center[1]:.6f} {center[2]:.6f}">
              <freejoint/>
              <geom name="strut{s_idx}g" type="capsule"
                    fromto="{sa[0]:.6f} {sa[1]:.6f} {sa[2]:.6f}
                            {sb[0]:.6f} {sb[1]:.6f} {sb[2]:.6f}"
                    size="{design.strut_diameter_m * 0.5:.6f}"
                    density="{strut_density:.1f}" contype="0" conaffinity="0"
                    rgba="0.2 0.4 0.9 1"/>
              <site name="n{a}" pos="{sa[0]:.6f} {sa[1]:.6f} {sa[2]:.6f}" size="0.002"/>
              <site name="n{b}" pos="{sb[0]:.6f} {sb[1]:.6f} {sb[2]:.6f}" size="0.002"/>
              {extra}
            </body>
        """))

    tendons = []
    k_cable = design.cable_stiffness_Npm
    # light viscous damping on the tendons; TPU 85A is strongly lossy, and
    # without it the tendon network rings at its own numerical frequency
    c_cable = cable_zeta * 2.0 * math.sqrt(k_cable * max(ACCEL_MASS_KG, 1e-3))
    for c_idx, (a, b) in enumerate(CABLES):
        L0 = float(np.linalg.norm(nodes[a] - nodes[b]))
        rest = (1.0 - prestrain) * L0
        tendons.append(textwrap.dedent(f"""
            <spatial name="cable{c_idx}" range="0 {rest:.6f}"
                     stiffness="{k_cable:.3f}" damping="{c_cable:.4f}"
                     rgba="0.9 0.2 0.2 1" width="0.0006">
              <site site="n{a}"/>
              <site site="n{b}"/>
            </spatial>
        """))

    # ball anchors: each bottom vertex glued to the carriage plate
    bottoms = []
    for (a, b) in STRUTS:
        bottoms.append(a if nodes[a][2] < nodes[b][2] else b)
    equalities = []
    for s_idx, node in enumerate(bottoms):
        p = nodes[node]
        equalities.append(
            f'<connect body1="strut{s_idx}" body2="carriage" '
            f'anchor="{p[0]:.6f} {p[1]:.6f} {p[2]:.6f}"/>'
        )

    return f"""
    <mujoco model="drop_tower">
      <option gravity="0 0 -{G}" timestep="{SIM_DT_S}" integrator="implicitfast"/>
      <worldbody>
        <body name="carriage" pos="0 0 0">
          <joint name="slide" type="slide" axis="0 0 1"/>
          <geom name="plate" type="box"
                size="{plate_half:.4f} {plate_half:.4f} {plate_t * 0.5:.4f}"
                pos="0 0 {-plate_t * 0.5:.4f}" mass="{carriage_mass_kg:.4f}"
                contype="0" conaffinity="0" rgba="0.7 0.7 0.75 1"/>
          <site name="ch5" pos="0 0 {-plate_t * 0.5:.4f}" size="0.003"/>
        </body>
        {''.join(bodies)}
      </worldbody>
      <tendon>
        {''.join(tendons)}
      </tendon>
      <equality>
        {''.join(equalities)}
      </equality>
      <sensor>
        <framelinacc name="a_ch5" objtype="site" objname="ch5"/>
        <framelinacc name="a_top" objtype="site" objname="n{top_node}"/>
      </sensor>
    </mujoco>
    """


def simulate(design: PrintableDesign, *, mat: MatModel | None = None,
             impact_v_mps: float = IMPACT_V_MPS,
             prestrain: float = DEFAULT_PRESTRAIN,
             carriage_mass_kg: float = CARRIAGE_MASS_KG,
             pla_solidity: float = PLA_SOLIDITY,
             tpu_solidity: float = TPU_SOLIDITY,
             article_mass_g: float | None = None,
             cfc: float = 180.0,
             cable_zeta: float = DEFAULT_CABLE_ZETA,
             duration_s: float = SIM_DURATION_S) -> dict:
    """One drop.  Returns the PR #102 objectives plus the raw channels."""
    import mujoco

    mat = mat or MatModel()
    model = mujoco.MjModel.from_xml_string(
        build_xml(design, prestrain=prestrain, carriage_mass_kg=carriage_mass_kg,
                  pla_solidity=pla_solidity, article_mass_g=article_mass_g,
                  cable_zeta=cable_zeta))
    data = mujoco.MjData(model)

    carriage_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "carriage")
    slide_adr = model.jnt_dofadr[mujoco.mj_name2id(
        model, mujoco.mjtObj.mjOBJ_JOINT, "slide")]

    # Geometry the article-deformation observables need, recomputed exactly as
    # build_xml computed it.  Tendon rest lengths are the slack lengths the
    # prestrain leaves, so "strain" below means tension strain above slack, and
    # the tendon force/energy figures are the k_cable * extension proxies (the
    # tendon also carries a limit constraint at the same rest length, so these
    # are nominal-stiffness proxies, not the constraint-solver force).
    nodes = tprism_nodes(radius=design.radius_m, height=design.height_m,
                         twist=design.twist_rad, z0=0.0)
    rest_len = np.array([(1.0 - prestrain) * np.linalg.norm(nodes[a] - nodes[b])
                         for a, b in CABLES])
    k_cable = design.cable_stiffness_Npm
    a0, b0 = STRUTS[0]
    top_node = a0 if nodes[a0][2] > nodes[b0][2] else b0
    top_site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, f"n{top_node}")
    ch5_site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "ch5")

    # start with the whole assembly moving down at the impact velocity, with
    # the carriage exactly at the top of the (uncompressed) mat
    data.qpos[model.jnt_qposadr[mujoco.mj_name2id(
        model, mujoco.mjtObj.mjOBJ_JOINT, "slide")]] = 0.0
    for i in range(1, model.nbody):
        adr = model.body_dofadr[i]
        if i == carriage_id:
            data.qvel[slide_adr] = -impact_v_mps
        else:
            data.qvel[adr + 2] = -impact_v_mps

    nsteps = int(duration_s / SIM_DT_S)
    t = np.zeros(nsteps)
    a_in = np.zeros(nsteps)
    a_out = np.zeros(nsteps)
    v_car = np.zeros(nsteps)
    f_mat = np.zeros(nsteps)
    peak_strain = 0.0
    peak_energy_J = 0.0
    rel_z0 = None
    stroke_m = 0.0

    for k in range(nsteps):
        # one-sided Kelvin-Voigt mat under the carriage
        z = float(data.qpos[model.jnt_qposadr[0]])
        vz = float(data.qvel[slide_adr])
        pen = -z                      # carriage travel into the mat
        if pen > 0.0:
            f = pen * (mat.stiffness_Npm - mat.damping_Nspm * vz)
            f = max(f, 0.0)           # the mat pushes, never pulls
        else:
            f = 0.0
        data.xfrc_applied[carriage_id, 2] = f

        mujoco.mj_step(model, data)

        t[k] = data.time
        a_in[k] = data.sensordata[2]      # framelinacc ch5, z
        a_out[k] = data.sensordata[5]     # framelinacc top vertex, z
        v_car[k] = float(data.qvel[slide_adr])
        f_mat[k] = f
        # article-deformation observables (candidate objectives)
        ext = np.maximum(data.ten_length - rest_len, 0.0)
        s = float(np.max(ext / rest_len))
        if s > peak_strain:
            peak_strain = s
        e = 0.5 * k_cable * float(np.sum(ext * ext))
        if e > peak_energy_J:
            peak_energy_J = e
        rel_z = float(data.site_xpos[top_site][2] - data.site_xpos[ch5_site][2])
        if rel_z0 is None:
            rel_z0 = rel_z
        elif rel_z0 - rel_z > stroke_m:
            stroke_m = rel_z0 - rel_z
        if not np.isfinite(a_in[k]) or not np.isfinite(a_out[k]):
            t, a_in, a_out, v_car, f_mat = (arr[:k] for arr in
                                            (t, a_in, a_out, v_car, f_mat))
            break

    if t.size < 50:
        return {"t180": float("nan"), "e_rebound": float("nan"),
                "e_reb_mJ": float("nan"), "ok": False}

    fs = 1.0 / SIM_DT_S
    in_f = _cfc_filter(a_in, fs, cfc=cfc)
    out_f = _cfc_filter(a_out, fs, cfc=cfc)
    in_peak_g = float(np.max(np.abs(in_f))) / G
    out_peak_g = float(np.max(np.abs(out_f))) / G
    t180 = out_peak_g / in_peak_g if in_peak_g > 0 else float("nan")

    # restitution: carriage velocity once the mat force has released
    contact = f_mat > 0.0
    if contact.any():
        last = int(np.max(np.nonzero(contact)[0]))
        after = v_car[last + 1:]
        v_reb = float(np.max(after)) if after.size else 0.0
    else:
        v_reb = 0.0
    e_rebound = max(v_reb, 0.0) / impact_v_mps

    pm = printed_mass_cad(design, pla_solidity=pla_solidity,
                          tpu_solidity=tpu_solidity)
    # ``e_reb_mJ`` is deliberately an *absolute* energy (PR #102): a lighter
    # article returning the same velocity fraction returns less energy to the
    # payload.  That makes the mass it is multiplied by load-bearing, so it is
    # the calibrated as-printed mass when the caller supplies one (which is
    # what the constant-printed-mass projection does) and only falls back to
    # the flat-solidity estimate otherwise.
    mass_g = float(article_mass_g) if article_mass_g is not None else pm.printed_g
    e_reb_mJ = e_rebound * mass_g * G * DROP_H_M

    # pulse width of the input at half peak, for the sanity table
    above = np.abs(in_f) >= 0.5 * np.max(np.abs(in_f))
    pulse_ms = float(above.sum()) * SIM_DT_S * 1e3

    # CFC-1000 transmissibility, the campaign's other measured ratio
    in_1k = _cfc_filter(a_in, fs, cfc=1000.0)
    out_1k = _cfc_filter(a_out, fs, cfc=1000.0)
    in_1k_pk = float(np.max(np.abs(in_1k)))
    t1000 = (float(np.max(np.abs(out_1k))) / in_1k_pk
             if in_1k_pk > 0 else float("nan"))

    return {
        "t180": float(t180),
        "e_rebound": float(e_rebound),
        "e_reb_mJ": float(e_reb_mJ),
        "in_180_g": in_peak_g,
        "out_180_g": out_peak_g,
        "pulse_ms": pulse_ms,
        "t1000": float(t1000),
        "peak_tendon_strain": float(peak_strain),
        "peak_tendon_energy_mJ": float(peak_energy_J * 1e3),
        "stroke_mm": float(stroke_m * 1e3),
        "mass_printed_g": mass_g,
        "mass_flat_model_g": pm.printed_g,
        "mass_solid_g": pm.solid_g,
        "tpu_fraction": pm.tpu_fraction,
        "v_rebound_mps": float(v_reb),
        "ok": True,
        "t": t, "a_in_g": in_f / G, "a_out_g": out_f / G, "v_car": v_car,
        # unfiltered channels for ringdown work: the CFC-180 corner sits at
        # ~300 Hz, right on top of the measured 294-468 Hz ringdown band, so
        # any modal fit has to run on the raw traces
        "a_in_raw_g": a_in / G, "a_out_raw_g": a_out / G, "f_mat": f_mat,
    }


_MASS_MODEL = None


def mass_model():
    """The calibrated printed-mass model, fit once per process."""
    global _MASS_MODEL
    if _MASS_MODEL is None:
        _MASS_MODEL = calibrate_mass_model()
    return _MASS_MODEL


def evaluate_pr102(parameterization, *, manifold: str = "printed",
                   target_mass_g: float | None = None,
                   solid_mass: bool = False, **kwargs) -> dict:
    """Score a PR #35/#102 base parameterization on the campaign objectives.

    ``parameterization`` uses the PR #102 search-space keys (``R_mm``,
    ``H_mm``, ``twist_deg``, ``strut_d_mm``, ``cable_d_mm``), which are the
    *base* Sobol coordinates: what actually gets printed is the uniform
    rescale of them that hits a mass target, so the base parameterization is
    projected first and the simulation runs on the article that would come
    off the plate.

    ``solid_mass`` is the infill ablation: keep the projected geometry but
    give the article the mass it would have printed solid.

    ``manifold`` selects which mass is held constant.

    ``"printed"`` (default)
        Constant **as-printed** mass, PR #102 commit 2f1ca2e: solve the
        uniform scale so the calibrated mass model
        (:mod:`pr102_mass_model`) predicts ``target_mass_g`` grams on the
        scale.  The target comes from the sixth search-space parameter
        ``mass_printed_g`` when the caller supplies it, else from
        ``target_mass_g``, else from the S0 reference article's weighed
        20.23 g.  This is the manifold the objectives need: ``e_reb_mJ`` is
        an absolute energy proportional to mass, so leaving mass free makes
        it *be* the mass.
    ``"solid"``
        Constant **solid-CAD** mass, PR #35 Route A (30.95 g), which is what
        the round-1 batch was built to.  Kept so the round-1 articles can be
        scored on the manifold they were actually printed on, and so the
        earlier results in this directory stay reproducible.  Do not use it
        for a campaign: across the box it leaves printed mass spanning 32 %
        and ``e_reb_mJ`` rank-correlates with mass at 0.9999.
    """
    design = parameterization_to_design(parameterization)
    if manifold == "solid":
        printed, scale = project_constant_mass(design)
        res = simulate(printed, **kwargs)
        res["print_scale"] = scale
        res["mass_target_g"] = float("nan")
        return {k: v for k, v in res.items() if not isinstance(v, np.ndarray)}
    if manifold != "printed":
        raise ValueError(f"unknown manifold {manifold!r}")

    target = parameterization.get("mass_printed_g", target_mass_g)
    target = float(target) if target is not None else DEFAULT_PRINTED_MASS_TARGET_G
    base = {n: float(parameterization[n]) for n in PARAM_NAMES}
    model = mass_model()
    scale = model.solve_scale_for_printed_mass(base, target)
    if not np.isfinite(scale):
        # The housings alone outweigh the target: no rescale reaches it.
        return {"t180": float("nan"), "e_rebound": float("nan"),
                "e_reb_mJ": float("nan"), "mass_printed_g": float("nan"),
                "print_scale": float("nan"), "mass_target_g": target,
                "ok": False}
    article_g = target
    if solid_mass:
        # Infill ablation on this manifold: the projection still puts the
        # article at the target *printed* mass, but the simulated inertia is
        # what the same geometry would weigh printed solid.  (Setting
        # ``pla_solidity=1`` cannot express it here, because the mass is
        # pinned rather than derived from a density.)
        article_g = float(sum(model.solid_grams(base, scale)))
    res = simulate(scale_design(design, scale), article_mass_g=article_g, **kwargs)
    res["print_scale"] = scale
    res["mass_target_g"] = target
    return {k: v for k, v in res.items() if not isinstance(v, np.ndarray)}


# --- calibration ----------------------------------------------------------

S0_BASE_PARAMS = {"R_mm": 25.0, "H_mm": 70.0, "twist_deg": 60.0,
                  "strut_d_mm": 6.0, "cable_d_mm": 3.0}
# bpx68c, the S0 reference article: campaign summary means.
S0_MEASURED = {"in_180_g": 208.2, "e_rebound": 0.0204, "t180": 1.0111,
               "in_dv_ms": 5.3017}


def target_pulse_ms(peak_g: float = S0_MEASURED["in_180_g"],
                    dv_mps: float = S0_MEASURED["in_dv_ms"]) -> float:
    """Half-sine pulse width implied by the measured peak and delta-v.

    ``dv = (2/pi) * a_peak * T`` for a half sine, so the campaign's own
    numbers fix the width; nothing is assumed.
    """
    return 1e3 * math.pi * dv_mps / (2.0 * peak_g * G)


def calibrate(target_in_g: float = S0_MEASURED["in_180_g"],
              target_ms: float | None = None) -> MatModel:
    """Fit (mat stiffness, mat damping) to the measured *input pulse*.

    The two residuals are the input peak and the pulse width, both measured
    (the width via :func:`target_pulse_ms` from the campaign's peak and
    delta-v), against two log-parameters, by Nelder-Mead.

    Note what is deliberately *not* a calibration target: the measured
    restitution (0.020 to 0.050).  A mat that returned that little energy in
    this model would have to be so lossy that its peak lands near 300 G,
    well above what the tower measures -- the missing energy leaves through
    paths this model does not carry (guide rails, anvil and frame, the mount
    itself).  Calibrating on restitution would therefore corrupt the input
    pulse, which is the one thing the model can get right, so the simulated
    ``e_rebound`` is treated as a *rank* proxy for the measured one rather
    than a prediction of its value, and the correlation study reports it
    that way.
    """
    from scipy.optimize import minimize

    target_ms = target_ms if target_ms is not None else target_pulse_ms()
    base = dict(S0_BASE_PARAMS)
    s0_scale = mass_model().solve_scale_for_printed_mass(
        base, DEFAULT_PRINTED_MASS_TARGET_G)
    design = scale_design(parameterization_to_design(base), s0_scale)

    def residual(logp):
        k, c = float(np.exp(logp[0])), float(np.exp(logp[1]))
        res = simulate(design, mat=MatModel(k, c),
                       article_mass_g=DEFAULT_PRINTED_MASS_TARGET_G)
        if not res["ok"] or not np.isfinite(res["in_180_g"]):
            return 1e3
        return (math.log(max(res["in_180_g"], 1e-6) / target_in_g) ** 2
                + math.log(max(res["pulse_ms"], 1e-6) / target_ms) ** 2)

    x0 = np.log([MAT_STIFFNESS_NPM, MAT_DAMPING_NSPM])
    out = minimize(residual, x0, method="Nelder-Mead",
                   options={"xatol": 1e-3, "fatol": 1e-6, "maxiter": 200})
    return MatModel(float(np.exp(out.x[0])), float(np.exp(out.x[1])))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--calibrate", action="store_true",
                    help="refit the mat model to the S0 reference article")
    ap.add_argument("--spec", type=int, default=None,
                    help="Sobol spec index from the PR #102 batch table")
    ap.add_argument("--solid", action="store_true",
                    help="infill ablation: give the article its solid mass")
    ap.add_argument("--manifold", choices=("printed", "solid"), default="printed",
                    help="which mass the projection holds constant")
    args = ap.parse_args(argv)

    if args.calibrate:
        mat = calibrate()
        print(f"calibrated mat: stiffness = {mat.stiffness_Npm:.4g} N/m, "
              f"damping = {mat.damping_Nspm:.4g} N s/m")
        s0 = scale_design(parameterization_to_design(S0_BASE_PARAMS),
                          mass_model().solve_scale_for_printed_mass(
                              dict(S0_BASE_PARAMS),
                              DEFAULT_PRINTED_MASS_TARGET_G))
        res = simulate(s0, mat=mat,
                       article_mass_g=DEFAULT_PRINTED_MASS_TARGET_G)
        print(f"  S0 check: in_180 = {res['in_180_g']:.1f} G "
              f"(measured {S0_MEASURED['in_180_g']:.1f}), "
              f"pulse = {res['pulse_ms']:.2f} ms "
              f"(target {target_pulse_ms():.2f}), "
              f"e_rebound = {res['e_rebound']:.4f} "
              f"(measured {S0_MEASURED['e_rebound']:.4f}, rank proxy only), "
              f"t180 = {res['t180']:.4f} (measured {S0_MEASURED['t180']:.4f})")
        return 0

    if args.spec is None:
        params = dict(S0_BASE_PARAMS)
        label = "S0 reference"
    else:
        import pandas as pd
        batch = pd.read_csv(
            Path(__file__).resolve().parent / "data" / "pr102"
            / "t3-prism-bo-batch.csv").set_index("specimen")
        row = batch.loc[args.spec]
        params = {k: float(row[k]) for k in
                  ("R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm")}
        label = f"Sobol spec {args.spec:02d}"

    res = evaluate_pr102(params, manifold=args.manifold,
                         solid_mass=args.solid)
    print(f"{label}: {params}")
    for key in ("t180", "e_rebound", "e_reb_mJ", "in_180_g", "out_180_g",
                "pulse_ms", "print_scale", "mass_printed_g", "mass_target_g"):
        print(f"  {key:16s} = {res[key]:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
