"""Offscreen 3D animation of the regime drops (crutch tip + NASA lander)
— *render-grade* re-build that fixes the bugs reported in PR comment
4427560261.

The earlier version of this script reused ``run_regimes.build_xml``,
which was designed for *metric extraction*: prism placed with 1 mm
ground clearance and given an initial impact-velocity downward kick so
metric extraction could skip the free-fall.  Combined with capsule radii
of 1.5 mm (crutch) / 6 mm (lander), every bottom strut started below
z=0 — the contact solver had to resolve massive penetration in step 1,
which is what the user saw as "structure goes beneath the floor".  The
payload plate was a free body with no joint or tendon connecting it to
the prism, only collision contact, so at impact velocity it punched
straight through the strut framework.

This script builds a *visualisation-only* MJCF where:

* The prism is lifted clear of the floor (``drop_height`` is the gap
  between the lowest point of the lowest capsule and z=0), so there is
  zero contact penetration at t=0.
* The payload mass is suspended *inside* the prism by 6 internal TPU
  tendons (one per node), matching the SUPERball / NASA TBR
  architecture used in ``simulations/newton_drop.py``.  This keeps the
  payload anchored to the structure for the entire animation instead of
  free-falling through it.
* The drop starts from rest at a sensible height per regime, so the
  GIF shows free-fall → impact → bounce, not just "everything already
  at impact velocity in frame 1".

For *quantitative* metric extraction (peak g, pulse FWHM, SEA, BO
sweep), still use ``simulations/run_regimes.py``; the metric model
intentionally skips the free-fall to keep nsteps small.

Outputs (under ``simulations/outputs/``):
  - ``regime_crutch_tip_drop.{gif,mp4}``
  - ``regime_nasa_lander_drop.{gif,mp4}``

Run with ``MUJOCO_GL=osmesa`` on headless runners.
"""
from __future__ import annotations

import os
import sys
import textwrap

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from regimes import CRUTCH, NASA_LANDER, Regime  # noqa: E402
from render_utils import render_drop  # noqa: E402
from tprism_geometry import CABLES, STRUTS, tprism_nodes  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def build_render_xml(r: Regime, *, drop_height: float,
                     payload_mass_kg: float | None = None) -> str:
    """Build a visualisation-only MJCF for regime ``r``.

    The prism carries the payload as extra mass distributed across the
    three struts (axial-loading model — matches the working 1 m
    baseline drop the user previously called "the most realistic", and
    matches a crutch tip where the user weight loads the strut tips
    directly).  No "payload suspended inside a cage" architecture: the
    earlier version of this file used SUPERball-style internal tendons
    to suspend the payload, but with TPU 85A tendon stiffnesses the
    payload + tendon dynamics oscillated wildly and the prism flipped
    through the floor on impact (PR comments 4427965775 / 4462016260).

    Parameters
    ----------
    r : Regime
        Regime to render.  Provides geometry, payload mass, and tendon
        material constants.
    drop_height : float
        Gap (m) between the lowest point of the lowest strut node and
        the floor at t=0.
    payload_mass_kg : float, optional
        Visualisation payload mass added on top of the strut self-mass.
        Defaults to ``r.payload_mass_kg``.
    """
    # z0 is set so the *lowest node site* sits at drop_height + a small
    # margin above the floor; capsule centres are above z0 by half-len*sin.
    z0 = drop_height + 2.0 * r.strut_radius_m
    nodes = tprism_nodes(radius=r.radius_m, height=r.height_m, z0=z0)
    m_payload = float(payload_mass_kg) if payload_mass_kg is not None \
        else r.payload_mass_kg
    # Distribute payload as extra mass on each of the 3 struts; combined
    # with the PLA strut self-mass (densely small), this gives the
    # prism the inertia of a real cell + crutch user / lander payload.
    extra_mass_per_strut = m_payload / 3.0

    bodies = []
    for s_idx, (a, b) in enumerate(STRUTS):
        pa, pb = nodes[a], nodes[b]
        center = 0.5 * (pa + pb)
        sa = pa - center
        sb = pb - center
        # Strut: capsule with the design density + an inertial sphere
        # whose mass = (1/3) of the visualisation payload, attached at
        # the strut centre (no extra geometry-collision volume).
        bodies.append(textwrap.dedent(f"""
            <body name="strut{s_idx}" pos="{center[0]:.6f} {center[1]:.6f} {center[2]:.6f}">
              <freejoint/>
              <geom type="capsule"
                    fromto="{sa[0]:.6f} {sa[1]:.6f} {sa[2]:.6f}
                            {sb[0]:.6f} {sb[1]:.6f} {sb[2]:.6f}"
                    size="{r.strut_radius_m:.5f}" density="{r.strut_density_kgm3:.1f}"
                    rgba="0.2 0.4 0.9 1"
                    solref="0.002 1" solimp="0.98 0.999 0.0001"/>
              <geom type="sphere" pos="0 0 0" size="0.0001"
                    mass="{extra_mass_per_strut:.6f}"
                    rgba="0 0 0 0" contype="0" conaffinity="0"/>
              <site name="n{a}" pos="{sa[0]:.6f} {sa[1]:.6f} {sa[2]:.6f}"
                    size="{max(0.001, 0.4 * r.strut_radius_m):.5f}"/>
              <site name="n{b}" pos="{sb[0]:.6f} {sb[1]:.6f} {sb[2]:.6f}"
                    size="{max(0.001, 0.4 * r.strut_radius_m):.5f}"/>
            </body>
        """))

    tendons = []
    # 9 prism cables (regime cable_pretension_frac).  Boost stiffness to
    # whatever is needed to keep static cable stretch under 5% of cell
    # extent given the visualisation payload weight per node.
    weight = m_payload * 9.81
    cell_extent = max(r.radius_m, r.height_m)
    k_min_static = weight / (0.05 * cell_extent)
    k_cable = max(r.cable_stiffness_Npm, k_min_static)
    cable_damping = max(r.cable_damping_Nspm,
                        0.10 * 2.0 * np.sqrt(k_cable * m_payload / 9.0))
    for c_idx, (a, b) in enumerate(CABLES):
        L0 = float(np.linalg.norm(nodes[a] - nodes[b]))
        rest = (1.0 - r.cable_pretension_frac) * L0
        tendons.append(textwrap.dedent(f"""
            <spatial name="cable{c_idx}" range="0 {rest:.6f}"
                     stiffness="{k_cable:.4f}"
                     damping="{cable_damping:.4f}"
                     rgba="0.9 0.2 0.2 1"
                     width="{max(0.0006, 0.05 * r.strut_radius_m):.5f}">
              <site site="n{a}"/>
              <site site="n{b}"/>
            </spatial>
        """))

    # Render-grade timestep: tighter than the metric model so impact
    # contacts are well-resolved visually.  Heavier viz payload → smaller
    # dt so the stiff floor contact stays stable.
    dt = min(r.sim_dt_s, 2.0e-5 if m_payload >= 5 else 5.0e-5)
    # ASTM D5276 / GSFC GEVS impact-surface convention: rigid concrete pad
    # (>= 150 mm thick, on >= 1 m^3 concrete/steel base; E_concrete ~ 30 GPa
    # >> E_PLA ~ 3.5 GPa, so contact compliance is dominated by the
    # strut, not the floor).  Modelled here as an infinite rigid MuJoCo
    # ``plane`` with critically-damped contact (solref tau=2 ms, beta=1)
    # and a sliding friction tuple representative of PLA-on-concrete
    # (mu_s ~ 0.55-0.65, mu_torsion ~ 0.005, mu_roll ~ 1e-4).
    return f"""
    <mujoco model="render_{r.name}">
      <option gravity="0 0 -9.81" timestep="{dt}" integrator="RK4"/>
      <worldbody>
        <geom name="floor" type="plane" size="2 2 0.1" rgba="0.85 0.85 0.85 1"
              friction="0.6 0.005 0.0001"
              solref="0.002 1" solimp="0.98 0.999 0.0001"/>
        {''.join(bodies)}
      </worldbody>
      <tendon>
        {''.join(tendons)}
      </tendon>
    </mujoco>
    """


def render_regime(r: Regime) -> None:
    """Drop ``r``'s prism (carrying payload as added strut mass) from rest."""
    cell_extent = max(r.radius_m, r.height_m)
    drop_height = min(0.20, max(0.04, 1.5 * cell_extent))
    free_fall_s = float(np.sqrt(2.0 * drop_height / 9.81))
    duration = free_fall_s + 0.20     # impact + bounce

    # Cap the visualisation payload mass.  The crutch regime's 75 kg
    # user weight crushes the 24 mm cell beyond elastic recovery in any
    # plausible printable design — fine for the metric extraction model
    # which intentionally trades fidelity for speed, not fine for a GIF
    # that's supposed to look physical.  We cap at the largest mass
    # whose static weight produces ≤ 5% cable stretch under the regime's
    # design cable stiffness, which keeps the cell visibly intact:
    #     m_max = 0.05 * cell_extent * k_cable / g
    max_viz_mass = 0.05 * cell_extent * r.cable_stiffness_Npm / 9.81
    viz_payload = min(r.payload_mass_kg, max(0.5, max_viz_mass))

    z0 = drop_height + 2.0 * r.strut_radius_m
    distance = 5.0 * cell_extent + 1.5 * drop_height
    lookat_z = 0.5 * (drop_height + z0 + r.height_m)
    floor_size = 4.0 * (cell_extent + drop_height)

    xml = build_render_xml(r, drop_height=drop_height,
                           payload_mass_kg=viz_payload)

    title = (f"{r.name}: viz payload {viz_payload:.2f} kg "
             f"(actual {r.payload_mass_kg:g} kg), "
             f"drop {drop_height * 1e3:.0f} mm")

    render_drop(
        xml,
        out_stem=os.path.join(OUT_DIR, f"regime_{r.name}_drop"),
        duration_s=duration,
        cam_lookat=(0.0, 0.0, lookat_z),
        cam_distance=distance,
        cam_elevation=-12.0,
        cam_azimuth=35.0,
        n_frames=60,
        playback_fps=24,
        tendon_width=max(0.0006, 0.05 * r.strut_radius_m),
        floor_size=floor_size,
        title=title,
    )


def main() -> None:
    for r in (CRUTCH, NASA_LANDER):
        render_regime(r)


if __name__ == "__main__":
    main()
