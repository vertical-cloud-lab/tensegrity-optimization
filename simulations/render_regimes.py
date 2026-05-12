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
                     suspension_stiffness_frac: float = 0.5) -> str:
    """Build a visualisation-only MJCF for regime ``r``.

    Parameters
    ----------
    r : Regime
        Regime to render.  Provides geometry, payload mass, and tendon
        material constants.
    drop_height : float
        Gap (m) between the lowest point of the lowest strut capsule
        and the floor at t=0.  Choose ~5× the cell extent so free-fall
        + impact comfortably fit in the GIF.
    suspension_stiffness_frac : float
        Stiffness of the 6 internal payload-suspension tendons, as a
        fraction of the prism cable stiffness.  0.5 keeps the suspension
        soft enough to engage during impact.
    """
    z0 = drop_height + r.strut_radius_m
    nodes = tprism_nodes(radius=r.radius_m, height=r.height_m, z0=z0)
    payload_pos = np.array([0.0, 0.0, z0 + 0.5 * r.height_m])
    payload_radius = max(0.005, 0.20 * r.radius_m)

    bodies = []
    for s_idx, (a, b) in enumerate(STRUTS):
        pa, pb = nodes[a], nodes[b]
        center = 0.5 * (pa + pb)
        sa = pa - center
        sb = pb - center
        bodies.append(textwrap.dedent(f"""
            <body name="strut{s_idx}" pos="{center[0]:.6f} {center[1]:.6f} {center[2]:.6f}">
              <freejoint/>
              <geom type="capsule"
                    fromto="{sa[0]:.6f} {sa[1]:.6f} {sa[2]:.6f}
                            {sb[0]:.6f} {sb[1]:.6f} {sb[2]:.6f}"
                    size="{r.strut_radius_m:.5f}" density="{r.strut_density_kgm3:.1f}"
                    rgba="0.2 0.4 0.9 1"/>
              <site name="n{a}" pos="{sa[0]:.6f} {sa[1]:.6f} {sa[2]:.6f}"
                    size="{max(0.001, 0.4 * r.strut_radius_m):.5f}"/>
              <site name="n{b}" pos="{sb[0]:.6f} {sb[1]:.6f} {sb[2]:.6f}"
                    size="{max(0.001, 0.4 * r.strut_radius_m):.5f}"/>
            </body>
        """))
    # Payload as a sphere suspended inside the prism.  ``contype=0
    # conaffinity=0`` disables collision (the tendons hold it in place)
    # so we never get the "plate punches through strut" failure mode.
    bodies.append(textwrap.dedent(f"""
        <body name="payload" pos="{payload_pos[0]:.6f} {payload_pos[1]:.6f} {payload_pos[2]:.6f}">
          <freejoint/>
          <geom type="sphere" size="{payload_radius:.5f}"
                mass="{r.payload_mass_kg:.5f}"
                rgba="0.55 0.55 0.6 1" contype="0" conaffinity="0"/>
          <site name="payload_center" pos="0 0 0" size="{payload_radius * 0.4:.5f}"/>
        </body>
    """))

    tendons = []
    # Outer 9 prism cables (regime cable_pretension_frac).
    for c_idx, (a, b) in enumerate(CABLES):
        L0 = float(np.linalg.norm(nodes[a] - nodes[b]))
        rest = (1.0 - r.cable_pretension_frac) * L0
        tendons.append(textwrap.dedent(f"""
            <spatial name="cable{c_idx}" range="0 {rest:.6f}"
                     stiffness="{r.cable_stiffness_Npm:.4f}"
                     damping="{r.cable_damping_Nspm:.4f}"
                     rgba="0.9 0.2 0.2 1"
                     width="{max(0.0006, 0.05 * r.strut_radius_m):.5f}">
              <site site="n{a}"/>
              <site site="n{b}"/>
            </spatial>
        """))
    # 6 internal payload-suspension tendons (one per prism node) — the
    # SUPERball architecture; keeps the payload anchored to the structure
    # during impact so it cannot punch through.
    susp_k = suspension_stiffness_frac * r.cable_stiffness_Npm
    for n_idx in range(6):
        L0 = float(np.linalg.norm(nodes[n_idx] - payload_pos))
        rest = (1.0 - r.cable_pretension_frac) * L0
        tendons.append(textwrap.dedent(f"""
            <spatial name="susp{n_idx}" range="0 {rest:.6f}"
                     stiffness="{susp_k:.4f}"
                     damping="{r.cable_damping_Nspm:.4f}"
                     rgba="0.9 0.6 0.2 1"
                     width="{max(0.0005, 0.04 * r.strut_radius_m):.5f}">
              <site site="n{n_idx}"/>
              <site site="payload_center"/>
            </spatial>
        """))

    # Render-grade timestep: stricter than the metric model's 2e-5 / 5e-5
    # so impact contacts are well-resolved visually (the metric model
    # intentionally trades fidelity for speed).
    dt = min(r.sim_dt_s, 5.0e-5 if r.payload_mass_kg <= 10 else 1.0e-4)
    return f"""
    <mujoco model="render_{r.name}">
      <option gravity="0 0 -9.81" timestep="{dt}" integrator="RK4"/>
      <worldbody>
        <geom name="floor" type="plane" size="2 2 0.1" rgba="0.85 0.85 0.85 1"/>
        {''.join(bodies)}
      </worldbody>
      <tendon>
        {''.join(tendons)}
      </tendon>
    </mujoco>
    """


def render_regime(r: Regime) -> None:
    """Drop ``r``'s prism + suspended payload from rest, render to GIF/MP4."""
    cell_extent = max(r.radius_m, r.height_m)
    # Drop heights chosen so the free-fall takes ~50–120 ms — long enough
    # to show the descent without bloating the GIF or stretching the
    # suspension tendons past their elastic envelope (the lander payload
    # is 5 kg with soft 8 kN/m TPU tendons, so we cap drop_height to keep
    # the post-impact suspension extension under ~10% of the prism scale).
    drop_height = min(0.20, max(0.04, 1.5 * cell_extent))
    free_fall_s = float(np.sqrt(2.0 * drop_height / 9.81))
    duration = free_fall_s + 0.20     # impact + bounce

    # Camera: frame the whole free-fall envelope.  ``cell_extent``-scaled
    # without the floor-of-0.4m we previously used (too zoomed-out for
    # the 24 mm crutch cell — it just showed an empty floor).
    distance = 5.0 * cell_extent + 1.5 * drop_height
    # lookat the *centre of the prism's free-fall envelope* (not just
    # 0.5*drop_height — that would point below the prism's resting z).
    z0 = drop_height + r.strut_radius_m
    lookat_z = 0.5 * drop_height + 0.5 * (z0 + r.height_m)
    floor_size = 4.0 * (cell_extent + drop_height)

    xml = build_render_xml(r, drop_height=drop_height)

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
        title=(f"{r.name}: payload {r.payload_mass_kg:g} kg, "
               f"drop {drop_height * 1e3:.0f} mm "
               f"(suspended-payload tensegrity)"),
    )


def main() -> None:
    for r in (CRUTCH, NASA_LANDER):
        render_regime(r)


if __name__ == "__main__":
    main()
