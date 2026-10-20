"""Minimal sanity-check renders to validate the offscreen MuJoCo render
pipeline before trusting more complex regime renders.

Per @sgbaird-alt's PR comment 4427560261, the existing
``regime_{crutch_tip,nasa_lander}_drop.gif`` animations had two visible
bugs:

* the prism appeared to dip below the floor on impact (struts placed
  with only 1 mm clearance + capsules of radius 1.5 / 6 mm → the bottom
  of every capsule starts BELOW z=0 at t=0; coupled with a 9.8 m/s
  downward initial velocity, the contact solver had to resolve massive
  penetration in step 1);
* the payload plate was a free body sitting on top of the prism with
  *no* joint or tendon holding it in place — only collision contact —
  and at 9.8 m/s × 5 kg it punched right through the strut framework.

Before re-running the regime renders we exercise three progressively
more complex scenes here so any future regression is easy to localise:

  1. ``spotcheck_capsule.gif`` — single capsule dropped from 0.30 m onto
     the ground plane.  Validates floor / lighting / camera / OSMesa.
  2. ``spotcheck_bare_prism.gif`` — bare 3-bar T-prism (no payload)
     dropped from 0.10 m.  Validates struts + tendons render, no
     penetration, cables stretch on impact.
  3. ``spotcheck_suspended_plate.gif`` — T-prism with payload plate
     suspended *inside* the prism by 6 internal TPU tendons (the
     SUPERball / NASA TBR architecture used in ``newton_drop.py``),
     dropped from 0.10 m.  Validates that a properly anchored payload
     stays inside the structure on impact.

Run with ``MUJOCO_GL=osmesa`` on headless runners.
"""
from __future__ import annotations

import os
import sys
import textwrap

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from render_utils import render_drop  # noqa: E402
from tprism_geometry import CABLES, STRUTS, tprism_nodes  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def _capsule_xml(*, drop_height: float = 0.30,
                 capsule_radius: float = 0.04,
                 capsule_half_length: float = 0.08) -> str:
    """One free capsule dropped from drop_height — a floor sanity check."""
    return f"""
    <mujoco model="spotcheck_capsule">
      <option gravity="0 0 -9.81" timestep="0.001" integrator="RK4"/>
      <worldbody>
        <geom name="floor" type="plane" size="2 2 0.1" rgba="0.85 0.85 0.85 1"/>
        <body name="capsule" pos="0 0 {drop_height:.4f}">
          <freejoint/>
          <geom type="capsule"
                fromto="0 0 -{capsule_half_length:.4f}
                        0 0  {capsule_half_length:.4f}"
                size="{capsule_radius:.4f}" density="1240"
                rgba="0.2 0.4 0.9 1"/>
        </body>
      </worldbody>
    </mujoco>
    """


def _bare_prism_xml(*, radius: float = 0.10, height: float = 0.20,
                    drop_height: float = 0.10,
                    strut_radius: float = 0.006,
                    strut_density: float = 1240.0,    # PLA per #45
                    cable_stiffness: float = 8.0e3,
                    cable_damping: float = 5.0,
                    cable_pretension_frac: float = 0.0) -> str:
    """Bare T-prism dropped from low height — validates struts + tendons.

    The prism is lifted clear of the floor (``drop_height`` is the gap
    between the *lowest point of the lowest capsule* and z=0, NOT the
    body-centre height) so there is no contact penetration at t=0.
    """
    z0 = drop_height + strut_radius
    nodes = tprism_nodes(radius=radius, height=height, z0=z0)

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
                    size="{strut_radius:.5f}" density="{strut_density:.1f}"
                    rgba="0.2 0.4 0.9 1"/>
              <site name="n{a}" pos="{sa[0]:.6f} {sa[1]:.6f} {sa[2]:.6f}" size="0.004"/>
              <site name="n{b}" pos="{sb[0]:.6f} {sb[1]:.6f} {sb[2]:.6f}" size="0.004"/>
            </body>
        """))

    tendons = []
    for c_idx, (a, b) in enumerate(CABLES):
        L0 = float(np.linalg.norm(nodes[a] - nodes[b]))
        rest = (1.0 - cable_pretension_frac) * L0
        tendons.append(textwrap.dedent(f"""
            <spatial name="cable{c_idx}" range="0 {rest:.6f}"
                     stiffness="{cable_stiffness:.2f}"
                     damping="{cable_damping:.2f}"
                     rgba="0.9 0.2 0.2 1" width="0.0015">
              <site site="n{a}"/>
              <site site="n{b}"/>
            </spatial>
        """))

    return f"""
    <mujoco model="spotcheck_bare_prism">
      <option gravity="0 0 -9.81" timestep="0.0005" integrator="RK4"/>
      <worldbody>
        <geom name="floor" type="plane" size="2 2 0.1" rgba="0.85 0.85 0.85 1"/>
        {''.join(bodies)}
      </worldbody>
      <tendon>
        {''.join(tendons)}
      </tendon>
    </mujoco>
    """


def _suspended_plate_xml(*, radius: float = 0.10, height: float = 0.20,
                         drop_height: float = 0.10,
                         strut_radius: float = 0.006,
                         strut_density: float = 1240.0,   # PLA per #45
                         payload_mass: float = 0.5,
                         cable_stiffness: float = 8.0e3,
                         cable_damping: float = 5.0,
                         cable_pretension_frac: float = 0.05,
                         suspension_stiffness: float = 4.0e3,
                         suspension_damping: float = 3.0) -> str:
    """T-prism with payload **suspended inside** by 6 internal TPU tendons.

    This matches the SUPERball / NASA TBR architecture (also used in
    ``simulations/newton_drop.py``): the payload hangs from every prism
    node so it remains inside the structure during impact instead of
    being a free plate that punches through the strut frame.

    The 6 internal tendons are pre-tensioned (``cable_pretension_frac``)
    so the payload sits centred at rest; on impact, the tendons stretch
    and the strain-colour map (red = high) visualises load transfer.
    """
    z0 = drop_height + strut_radius
    nodes = tprism_nodes(radius=radius, height=height, z0=z0)
    payload_pos = np.array([0.0, 0.0, z0 + 0.5 * height])

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
                    size="{strut_radius:.5f}" density="{strut_density:.1f}"
                    rgba="0.2 0.4 0.9 1"/>
              <site name="n{a}" pos="{sa[0]:.6f} {sa[1]:.6f} {sa[2]:.6f}" size="0.004"/>
              <site name="n{b}" pos="{sb[0]:.6f} {sb[1]:.6f} {sb[2]:.6f}" size="0.004"/>
            </body>
        """))
    payload_radius = 0.20 * radius
    bodies.append(textwrap.dedent(f"""
        <body name="payload" pos="{payload_pos[0]:.6f} {payload_pos[1]:.6f} {payload_pos[2]:.6f}">
          <freejoint/>
          <geom type="sphere" size="{payload_radius:.4f}" mass="{payload_mass:.4f}"
                rgba="0.6 0.6 0.6 1" contype="0" conaffinity="0"/>
          <site name="payload_center" pos="0 0 0" size="0.003"/>
        </body>
    """))

    tendons = []
    # Outer 9 prism cables.
    for c_idx, (a, b) in enumerate(CABLES):
        L0 = float(np.linalg.norm(nodes[a] - nodes[b]))
        rest = (1.0 - cable_pretension_frac) * L0
        tendons.append(textwrap.dedent(f"""
            <spatial name="cable{c_idx}" range="0 {rest:.6f}"
                     stiffness="{cable_stiffness:.2f}"
                     damping="{cable_damping:.2f}"
                     rgba="0.9 0.2 0.2 1" width="0.0015">
              <site site="n{a}"/>
              <site site="n{b}"/>
            </spatial>
        """))
    # 6 internal payload-suspension tendons (one per prism node).
    for n_idx in range(6):
        L0 = float(np.linalg.norm(nodes[n_idx] - payload_pos))
        rest = (1.0 - cable_pretension_frac) * L0
        tendons.append(textwrap.dedent(f"""
            <spatial name="susp{n_idx}" range="0 {rest:.6f}"
                     stiffness="{suspension_stiffness:.2f}"
                     damping="{suspension_damping:.2f}"
                     rgba="0.9 0.6 0.2 1" width="0.0012">
              <site site="n{n_idx}"/>
              <site site="payload_center"/>
            </spatial>
        """))

    return f"""
    <mujoco model="spotcheck_suspended_plate">
      <option gravity="0 0 -9.81" timestep="0.0005" integrator="RK4"/>
      <worldbody>
        <geom name="floor" type="plane" size="2 2 0.1" rgba="0.85 0.85 0.85 1"/>
        {''.join(bodies)}
      </worldbody>
      <tendon>
        {''.join(tendons)}
      </tendon>
    </mujoco>
    """


def main() -> None:
    print("== Spot-check 1/3: single capsule drop ==")
    render_drop(
        _capsule_xml(),
        out_stem=os.path.join(OUT_DIR, "spotcheck_capsule"),
        duration_s=0.8,
        cam_lookat=(0.0, 0.0, 0.15),
        cam_distance=0.9,
        cam_elevation=-12.0,
        cam_azimuth=35.0,
        target_fps=30,
        tendon_width=0.001,
        floor_size=0.6,
        title="Spot-check 1: capsule drop (validates floor + camera)",
    )

    print("== Spot-check 2/3: bare T-prism drop (no payload) ==")
    render_drop(
        _bare_prism_xml(),
        out_stem=os.path.join(OUT_DIR, "spotcheck_bare_prism"),
        duration_s=1.0,
        cam_lookat=(0.0, 0.0, 0.15),
        cam_distance=0.7,
        cam_elevation=-12.0,
        cam_azimuth=35.0,
        target_fps=30,
        tendon_width=0.0025,
        floor_size=0.8,
        title="Spot-check 2: bare T-prism drop (no penetration)",
    )

    print("== Spot-check 3/3: T-prism with internally-suspended payload ==")
    render_drop(
        _suspended_plate_xml(),
        out_stem=os.path.join(OUT_DIR, "spotcheck_suspended_plate"),
        duration_s=1.0,
        cam_lookat=(0.0, 0.0, 0.15),
        cam_distance=0.7,
        cam_elevation=-12.0,
        cam_azimuth=35.0,
        target_fps=30,
        tendon_width=0.0025,
        floor_size=0.8,
        title="Spot-check 3: T-prism w/ suspended payload (SUPERball-style)",
    )


if __name__ == "__main__":
    main()
