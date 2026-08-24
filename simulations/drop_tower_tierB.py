"""Tier-B drop-tower analogue: bending-capable struts + Kelvin-Voigt tendons.

This is the tier promotion that the zeta study (``zeta_analysis.md``) and the
Edison objective audit (9c0ab4c7) both point at.  ``drop_tower_sim`` (Tier C)
treats the three PLA struts as rigid capsules, so the article has no flexural
modes: its simulated ringdown lives at 22 to 96 Hz (rigid bodies swinging on
the tendon network) while the bench fits 294 to 468 Hz (strut flexure), its
``t180`` cannot exceed ~1 (no resonance, no amplification), and its
restitution answers to the mat rather than the article.  Three dead
observables, one missing mechanism.

What this module changes, and only this:

* **Struts bend.**  Each PLA strut is a chain of ``n_seg`` capsule segments
  joined by ball joints carrying a rotational spring ``k_theta = E_eff I /
  L_seg`` (the discrete-elastic-rod bending stiffness) and a rotational
  damper sized from the PLA structural loss factor,
  ``c_theta = eta_pla k_theta / omega_ref``.  ``E_eff`` is the Gibson-Ashby
  effective modulus of the sparse-infill strut (``print_infill``, ~1.5 GPa
  at the fitted 56.5 % solidity), not solid PLA's 3.5 GPa.
* **Tendons are Kelvin-Voigt.**  The dead-band spring is unchanged (zero
  force below slack, ``k x`` above), and the dashpot in parallel is sized
  from a TPU loss factor instead of an arbitrary modal dial:
  ``c = tan_delta_tpu * k_cable / omega_ref``.  ``omega_ref`` is the center
  of the measured ringdown band (2 pi * 380 Hz), i.e. the loss factor is
  matched at the frequency where the bench actually measures damping.

Everything else is inherited from Tier C so the two tiers are comparable:
the same carriage + calibrated Hunt-Crossley mat (the mat parameters are
*not* refit -- the input pulse is carriage-dominated, and the S0 check below
confirms the Tier-B article leaves it within a few G), the same CFC-180 /
CFC-1000 objective extraction, the same ball anchors at the bottom vertices,
the same 5 g accelerometer mass on the measured top vertex.

Loss-factor defaults (module constants, both exposed on the CLI): printed
PLA ``eta = 0.05`` and TPU 85A ``tan delta = 0.25`` are mid-range literature
values for FFF PLA structural damping and shore-85A polyester TPU DMA loss
tangent; neither is fit to the bench articles here.  That is deliberate:
this run asks whether bench-band physics *emerges* from material-level
inputs, not whether it can be tuned in.

Run::

    python drop_tower_tierB.py --check       # S0 sanity vs Tier C + bench
    python drop_tower_tierB.py               # all articles, CSV + PNG
    python drop_tower_tierB.py --n-seg 8
"""
from __future__ import annotations

import argparse
import math
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd

import drop_tower_sim as dts
from print_infill import PLA_SOLIDITY, effective_pla_modulus_MPa
from printable_design import PrintableDesign
from tprism_geometry import CABLES, STRUTS, tprism_nodes
from zeta_analysis import RELEASE_MARGIN_S, ringdown_fit

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "pr102"
OUT = HERE / "outputs"

G = 9.80665

N_SEG = 6                     # segments per strut; --n-seg for the study
ETA_PLA = 0.05                # structural loss factor of printed PLA
TAN_DELTA_TPU = 0.25          # TPU 85A DMA loss tangent
F_REF_HZ = 380.0              # center of the measured 294-468 Hz ringdown band
WALL_MM = 1.26                # 3 perimeters x 0.42 mm line width (slicer default)
TIERB_DT_S = 1.0e-5           # ball-spring modes reach a few kHz
RINGDOWN_DURATION_S = 0.20


def bending_modulus_MPa(strut_d_m: float, *, wall_m: float = WALL_MM * 1e-3,
                        ga_exponent: float = 1.5) -> float:
    """Effective *bending* modulus of a printed strut.

    The Gibson-Ashby power law is an axial/bulk homogenization; in bending
    the solid perimeter walls sit at the outer fiber and carry most of the
    second moment, so the flexural stiffness of a 3-perimeter sparse-infill
    strut is much closer to solid PLA than the bulk law says.  Composite
    section: solid annulus of the wall thickness at full modulus plus the
    infill core at the Gibson-Ashby modulus, combined through their shares
    of the area moment ``I``.
    """
    from printable_design import PLA
    r = strut_d_m * 0.5
    r_in = max(r - wall_m, 0.0)
    core_frac = (r_in / r) ** 4 if r > 0 else 0.0
    e_core = PLA.young_MPa * PLA_SOLIDITY ** ga_exponent
    return PLA.young_MPa * (1.0 - core_frac) + e_core * core_frac


def build_xml_tierB(design: PrintableDesign, *,
                    prestrain: float = dts.DEFAULT_PRESTRAIN,
                    carriage_mass_kg: float = dts.CARRIAGE_MASS_KG,
                    article_mass_g: float | None = None,
                    n_seg: int = N_SEG,
                    eta_pla: float = ETA_PLA,
                    tan_delta_tpu: float = TAN_DELTA_TPU,
                    f_ref_hz: float = F_REF_HZ,
                    weld_base: bool = False) -> str:
    """MJCF with segmented flexural struts and Kelvin-Voigt tendons."""
    nodes = tprism_nodes(radius=design.radius_m, height=design.height_m,
                         twist=design.twist_rad, z0=0.0)
    plate_half = max(design.radius_m * 1.6, 0.03)
    plate_t = 0.006
    omega_ref = 2.0 * math.pi * f_ref_hz

    # Mass split: the strut capsules carry the printed-PLA density (walls +
    # sparse infill, ``print_infill``), and the *rest* of the weighed article
    # mass -- vertex joint housings, tendon material, glue -- is lumped as six
    # equal point masses at the vertices, which is where the printed joints
    # actually are.  Tier C smeared the whole article mass into the strut
    # density; for rigid struts only the totals matter, but here the mass
    # *distribution* sets the flexural frequencies, so it has to be right.
    r = design.strut_diameter_m * 0.5
    strut_density = 1240.0 * PLA_SOLIDITY
    vertex_mass = 0.0
    if article_mass_g is not None:
        v_caps = 0.0
        for a, b in STRUTS:
            L = float(np.linalg.norm(nodes[a] - nodes[b]))
            v_caps += math.pi * r * r * L + (4.0 / 3.0) * math.pi * r ** 3
        m_caps = strut_density * v_caps
        residual = float(article_mass_g) * 1e-3 - m_caps
        if residual >= 0.0:
            vertex_mass = residual / 6.0
        elif v_caps > 0.0:
            # article lighter than the printed-density struts: scale down
            strut_density = float(article_mass_g) * 1e-3 / v_caps

    # discrete-elastic-rod bending stiffness between segments, wall-aware
    E_eff = bending_modulus_MPa(design.strut_diameter_m) * 1e6
    I_area = math.pi * design.strut_diameter_m ** 4 / 64.0

    a0, b0 = STRUTS[0]
    top_node = a0 if nodes[a0][2] > nodes[b0][2] else b0

    bodies = []
    site_owner = {}               # node index -> owning segment body name
    for s_idx, (a, b) in enumerate(STRUTS):
        # every strut in tprism_nodes runs bottom node -> top node, so the
        # chain root sits at the anchored bottom vertex and the free tip is
        # the last segment's far end; asserted rather than assumed
        assert nodes[b][2] > nodes[a][2]
        pa, pb = nodes[a], nodes[b]
        seg = (pb - pa) / n_seg
        L_seg = float(np.linalg.norm(seg))
        k_theta = E_eff * I_area / L_seg
        c_theta = eta_pla * k_theta / omega_ref
        root_extra = ""
        tip_extra = (f'<site name="n{b}" pos="{seg[0]:.6f} {seg[1]:.6f} '
                     f'{seg[2]:.6f}" size="0.002"/>')
        if vertex_mass > 0.0:
            root_extra = (f'<geom name="j{a}" type="sphere" size="0.003" '
                          f'pos="0 0 0" mass="{vertex_mass:.6f}" '
                          f'contype="0" conaffinity="0" rgba="0.4 0.4 0.4 1"/>')
            tip_extra += (f'<geom name="j{b}" type="sphere" size="0.003" '
                          f'pos="{seg[0]:.6f} {seg[1]:.6f} {seg[2]:.6f}" '
                          f'mass="{vertex_mass:.6f}" contype="0" '
                          f'conaffinity="0" rgba="0.4 0.4 0.4 1"/>')
        if s_idx == 0 and top_node == b:
            tip_extra += (
                f'<geom name="accel" type="sphere" size="0.004" '
                f'pos="{seg[0]:.6f} {seg[1]:.6f} {seg[2]:.6f}" '
                f'mass="{dts.ACCEL_MASS_KG}" contype="0" conaffinity="0" '
                f'rgba="0.95 0.85 0.1 1"/>')
        chain = [textwrap.dedent(f"""
            <body name="s{s_idx}seg0" pos="{pa[0]:.6f} {pa[1]:.6f} {pa[2]:.6f}">
              <freejoint/>
              <geom name="s{s_idx}g0" type="capsule"
                    fromto="0 0 0 {seg[0]:.6f} {seg[1]:.6f} {seg[2]:.6f}"
                    size="{r:.6f}" density="{strut_density:.1f}"
                    contype="0" conaffinity="0" rgba="0.2 0.4 0.9 1"/>
              <site name="n{a}" pos="0 0 0" size="0.002"/>
              {root_extra}
              {tip_extra if n_seg == 1 else ''}
        """)]
        for j in range(1, n_seg):
            chain.append(textwrap.dedent(f"""
                <body name="s{s_idx}seg{j}" pos="{seg[0]:.6f} {seg[1]:.6f} {seg[2]:.6f}">
                  <joint name="s{s_idx}b{j}" type="ball"
                         stiffness="{k_theta:.5f}" damping="{c_theta:.7f}"/>
                  <geom name="s{s_idx}g{j}" type="capsule"
                        fromto="0 0 0 {seg[0]:.6f} {seg[1]:.6f} {seg[2]:.6f}"
                        size="{r:.6f}" density="{strut_density:.1f}"
                        contype="0" conaffinity="0" rgba="0.2 0.4 0.9 1"/>
                  {tip_extra if j == n_seg - 1 else ''}
            """))
        chain.append("</body>" * n_seg)
        bodies.append("".join(chain))
        site_owner[a] = f"s{s_idx}seg0"
        site_owner[b] = f"s{s_idx}seg{n_seg - 1}"

    tendons = []
    k_cable = design.cable_stiffness_Npm
    # Kelvin-Voigt dashpot: loss tangent matched at the ringdown band
    c_cable = tan_delta_tpu * k_cable / omega_ref
    for c_idx, (a, b) in enumerate(CABLES):
        L0 = float(np.linalg.norm(nodes[a] - nodes[b]))
        rest = (1.0 - prestrain) * L0
        tendons.append(textwrap.dedent(f"""
            <spatial name="cable{c_idx}" springlength="0 {rest:.6f}"
                     stiffness="{k_cable:.3f}" damping="{c_cable:.5f}"
                     rgba="0.9 0.2 0.2 1" width="0.0006">
              <site site="n{a}"/>
              <site site="n{b}"/>
            </spatial>
        """))

    bottoms = []
    for (a, b) in STRUTS:
        bottoms.append(a if nodes[a][2] < nodes[b][2] else b)
    equalities = []
    for node in bottoms:
        p = nodes[node]
        if weld_base:
            # the glue patch transmits moment: clamped limit
            equalities.append(
                f'<weld body1="{site_owner[node]}" body2="carriage" '
                f'anchor="{p[0]:.6f} {p[1]:.6f} {p[2]:.6f}"/>'
            )
        else:
            # point hinge at the glued vertex: pinned limit
            equalities.append(
                f'<connect body1="{site_owner[node]}" body2="carriage" '
                f'anchor="{p[0]:.6f} {p[1]:.6f} {p[2]:.6f}"/>'
            )

    return f"""
    <mujoco model="drop_tower_tierB">
      <option gravity="0 0 -{G}" timestep="{TIERB_DT_S}" integrator="implicitfast"/>
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


def simulate_tierB(design: PrintableDesign, *,
                   mat: dts.MatModel | None = None,
                   impact_v_mps: float = dts.IMPACT_V_MPS,
                   prestrain: float = dts.DEFAULT_PRESTRAIN,
                   article_mass_g: float | None = None,
                   n_seg: int = N_SEG,
                   eta_pla: float = ETA_PLA,
                   tan_delta_tpu: float = TAN_DELTA_TPU,
                   weld_base: bool = False,
                   duration_s: float = RINGDOWN_DURATION_S) -> dict:
    """One Tier-B drop.  PR #102 objectives + ringdown fit on the raw traces."""
    import mujoco

    mat = mat or dts.MatModel()
    model = mujoco.MjModel.from_xml_string(
        build_xml_tierB(design, prestrain=prestrain,
                        article_mass_g=article_mass_g, n_seg=n_seg,
                        eta_pla=eta_pla, tan_delta_tpu=tan_delta_tpu,
                        weld_base=weld_base))
    data = mujoco.MjData(model)

    carriage_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "carriage")
    slide_jnt = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "slide")
    slide_adr = model.jnt_dofadr[slide_jnt]

    nodes = tprism_nodes(radius=design.radius_m, height=design.height_m,
                         twist=design.twist_rad, z0=0.0)
    rest_len = np.array([(1.0 - prestrain) * np.linalg.norm(nodes[a] - nodes[b])
                         for a, b in CABLES])
    k_cable = design.cable_stiffness_Npm
    a0, b0 = STRUTS[0]
    top_node = a0 if nodes[a0][2] > nodes[b0][2] else b0
    top_site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, f"n{top_node}")
    ch5_site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "ch5")

    # whole assembly co-moving down at the impact velocity
    for i in range(model.njnt):
        if model.jnt_type[i] == mujoco.mjtJoint.mjJNT_SLIDE:
            data.qvel[model.jnt_dofadr[i]] = -impact_v_mps
        elif model.jnt_type[i] == mujoco.mjtJoint.mjJNT_FREE:
            data.qvel[model.jnt_dofadr[i] + 2] = -impact_v_mps

    nsteps = int(duration_s / TIERB_DT_S)
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
        z = float(data.qpos[model.jnt_qposadr[slide_jnt]])
        vz = float(data.qvel[slide_adr])
        pen = -z
        if pen > 0.0:
            f = pen * (mat.stiffness_Npm - mat.damping_Nspm * vz)
            f = max(f, 0.0)
        else:
            f = 0.0
        data.xfrc_applied[carriage_id, 2] = f

        mujoco.mj_step(model, data)

        t[k] = data.time
        a_in[k] = data.sensordata[2]
        a_out[k] = data.sensordata[5]
        v_car[k] = float(data.qvel[slide_adr])
        f_mat[k] = f
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

    if t.size < 1000:
        return {"ok": False}

    fs = 1.0 / TIERB_DT_S
    in_f = dts._cfc_filter(a_in, fs, cfc=180.0)
    out_f = dts._cfc_filter(a_out, fs, cfc=180.0)
    in_peak_g = float(np.max(np.abs(in_f))) / G
    out_peak_g = float(np.max(np.abs(out_f))) / G
    in_1k = dts._cfc_filter(a_in, fs, cfc=1000.0)
    out_1k = dts._cfc_filter(a_out, fs, cfc=1000.0)
    in_1k_pk = float(np.max(np.abs(in_1k)))

    contact = f_mat > 0.0
    v_reb = 0.0
    fit = {}
    if contact.any():
        last = int(np.max(np.nonzero(contact)[0]))
        after = v_car[last + 1:]
        v_reb = float(np.max(after)) if after.size else 0.0
        start = last + int(RELEASE_MARGIN_S / TIERB_DT_S)
        if t.size - start > 2000:
            rel = (a_out[start:] - a_in[start:]) / G
            fit = ringdown_fit(t[start:], rel)
            # the bench fits all land in the flexural band (>=286 Hz), so a
            # like-for-like comparison also needs the fit restricted to that
            # family even when a low swing mode dominates the sim spectrum
            flex = ringdown_fit(t[start:], rel, fmin=150.0)
            fit.update({f"flex_{k}": v for k, v in flex.items()})
    e_rebound = max(v_reb, 0.0) / impact_v_mps

    return {
        "ok": True,
        "t180": out_peak_g / in_peak_g if in_peak_g > 0 else float("nan"),
        "t1000": (float(np.max(np.abs(out_1k))) / in_1k_pk
                  if in_1k_pk > 0 else float("nan")),
        "in_180_g": in_peak_g, "out_180_g": out_peak_g,
        "e_rebound": float(e_rebound),
        "e_reb_mJ": float(e_rebound * (article_mass_g or 0.0) * G * dts.DROP_H_M),
        "peak_tendon_strain": float(peak_strain),
        "peak_tendon_energy_mJ": float(peak_energy_J * 1e3),
        "stroke_mm": float(stroke_m * 1e3),
        "fn_hz": fit.get("fn_hz", float("nan")),
        "zeta_pct": fit.get("zeta_pct", float("nan")),
        "ringdown_r2": fit.get("r2", float("nan")),
        "ringdown_dominant_frac": fit.get("dominant_frac", float("nan")),
        "fn_flex_hz": fit.get("flex_fn_hz", float("nan")),
        "zeta_flex_pct": fit.get("flex_zeta_pct", float("nan")),
        "ringdown_flex_r2": fit.get("flex_r2", float("nan")),
        "flex_dominant_frac": fit.get("flex_dominant_frac", float("nan")),
        "t": t, "a_in_g": a_in / G, "a_out_g": a_out / G,
        "f_mat": f_mat, "v_car": v_car,
    }


# --------------------------------------------------------------------------
# the article roster: everything printed in the two batches
# --------------------------------------------------------------------------

def article_roster() -> pd.DataFrame:
    """One row per printed article across both batches, as-printed geometry.

    Batch 1 comes from the PR #102 print key (12 prints of specs 0-8 + S0);
    batch 2 (round 2, currently on/headed to the tower) from the round-1
    suggestions table joined to the round-2 print key.  ``amdjwm`` (measured,
    second-best t180) has no design mapping and therefore cannot be
    simulated; it is the known hole in the measured side.
    """
    key1 = pd.read_csv(DATA / "t3-prism-bo-batch-print-key.csv")
    res = pd.read_csv(DATA / "t3-prism-bo-batch-drop-results.csv")
    measured = set(res["specimen"])
    rows = []
    for _, r in key1.iterrows():
        rows.append({
            "print_id": r["print_id"], "batch": 1,
            "spec": str(r["specimen"]),
            "measured": r["print_id"] in measured,
            "R_mm": float(r["R_print_mm"]), "H_mm": float(r["H_print_mm"]),
            "twist_deg": float(r["twist_deg"]),
            "strut_d_mm": float(r["strut_d_print_mm"]),
            "cable_d_mm": float(r["cable_d_print_mm"]),
            "mass_g": float(r["mass_g"]),
        })
    key2 = pd.read_csv(DATA / "t3-prism-bo-round1-print-key.csv")
    sug = pd.read_csv(DATA / "t3-prism-bo-suggestions-round1.csv")
    sug["spec"] = [f"{int(t) - 10:02d}" for t in sug["trial_index"]]
    sug = sug.set_index("spec")
    for _, r in key2.iterrows():
        s = sug.loc[f"{int(r['spec']):02d}"]
        rows.append({
            "print_id": r["print_id"], "batch": 2,
            "spec": str(r["spec"]),
            "measured": int(r["n_drops_recorded"] or 0) > 0,
            "R_mm": float(s["R_print_mm"]), "H_mm": float(s["H_print_mm"]),
            "twist_deg": float(s["twist_deg"]),
            "strut_d_mm": float(s["strut_d_print_mm"]),
            "cable_d_mm": float(s["cable_d_print_mm"]),
            "mass_g": float(r["mass_g_with_label"]),
        })
    return pd.DataFrame(rows)


def design_from_print(row) -> PrintableDesign:
    """As-printed geometry -> PrintableDesign (with the +120 deg sim twist map)."""
    from bo_evaluator import parameterization_to_design
    return parameterization_to_design(
        {k: float(row[k]) for k in
         ("R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm")})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="S0 sanity row only (vs Tier C and the bench)")
    ap.add_argument("--n-seg", type=int, default=N_SEG)
    ap.add_argument("--eta-pla", type=float, default=ETA_PLA)
    ap.add_argument("--tan-delta-tpu", type=float, default=TAN_DELTA_TPU)
    ap.add_argument("--weld-base", action="store_true",
                    help="clamped-limit base anchors (glue transmits moment)")
    ap.add_argument("--out-tag", default="")
    args = ap.parse_args(argv)

    roster = article_roster()
    if args.check:
        roster = roster[roster["print_id"] == "bpx68c"]

    rows = []
    for _, r in roster.iterrows():
        design = design_from_print(r)
        res = simulate_tierB(design, article_mass_g=float(r["mass_g"]),
                             n_seg=args.n_seg, eta_pla=args.eta_pla,
                             tan_delta_tpu=args.tan_delta_tpu,
                             weld_base=args.weld_base)
        rec = {k: r[k] for k in ("print_id", "batch", "spec", "measured",
                                 "R_mm", "H_mm", "twist_deg", "strut_d_mm",
                                 "cable_d_mm", "mass_g")}
        rec.update({k: v for k, v in res.items()
                    if not isinstance(v, np.ndarray)})
        rows.append(rec)
        print(f"{r['print_id']}: t180={res.get('t180', float('nan')):.4f} "
              f"fn={res.get('fn_hz', float('nan')):.0f} Hz "
              f"zeta={res.get('zeta_pct', float('nan')):.1f}% "
              f"e_reb={res.get('e_rebound', float('nan')):.4f} "
              f"strain={res.get('peak_tendon_strain', float('nan')):.4f}",
              flush=True)

    df = pd.DataFrame(rows)
    tag = args.out_tag
    OUT.mkdir(exist_ok=True)
    df.to_csv(OUT / f"tierB_articles{tag}.csv", index=False)
    print(f"wrote {OUT / f'tierB_articles{tag}.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
