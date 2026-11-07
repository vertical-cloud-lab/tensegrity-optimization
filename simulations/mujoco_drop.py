"""MuJoCo simulation of a 3-bar tensegrity prism dropped onto a floor.

Each strut is a free-body capsule; cables are MuJoCo spatial tendons with
linear stiffness/damping (Hookean cable model).  We drop the prism from
1 m and log the COM height plus kinetic / strain / gravitational energies
over time to characterise its energy-absorbing response.

Outputs
-------
- simulations/outputs/mujoco_drop_energy.png   (plot)
- simulations/outputs/mujoco_drop_data.npz     (raw arrays)
- prints peak ground-reaction-equivalent deceleration to stdout.
"""
from __future__ import annotations

import os
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco
import numpy as np

from tprism_geometry import (BOTTOM_CABLES, CABLES, STRUTS, TOP_CABLES,
                              VERT_CABLES, tprism_nodes)

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def build_mjcf(radius: float = 0.10, height: float = 0.20,
               drop_height: float = 1.0,
               strut_density: float = 1240.0,    # PLA ~ kg/m^3
               strut_radius: float = 0.006,
               cable_stiffness: float = 8.0e3,   # N/m, soft TPU range
               cable_damping: float = 5.0) -> str:
    """Return an MJCF XML string for the prism dropped from drop_height."""
    nodes = tprism_nodes(radius=radius, height=height, z0=drop_height)
    bodies = []
    site_decls: dict[int, tuple[int, str]] = {}  # node -> (strut_idx, site_name)

    for s_idx, (a, b) in enumerate(STRUTS):
        pa, pb = nodes[a], nodes[b]
        center = 0.5 * (pa + pb)
        # Local site positions relative to body frame (world-aligned bodies).
        site_a = pa - center
        site_b = pb - center
        site_decls[a] = (s_idx, f"n{a}")
        site_decls[b] = (s_idx, f"n{b}")
        bodies.append(textwrap.dedent(f"""
            <body name="strut{s_idx}" pos="{center[0]:.6f} {center[1]:.6f} {center[2]:.6f}">
              <freejoint/>
              <geom type="capsule"
                    fromto="{site_a[0]:.6f} {site_a[1]:.6f} {site_a[2]:.6f}
                            {site_b[0]:.6f} {site_b[1]:.6f} {site_b[2]:.6f}"
                    size="{strut_radius:.4f}" density="{strut_density:.1f}"
                    rgba="0.2 0.4 0.9 1"/>
              <site name="n{a}" pos="{site_a[0]:.6f} {site_a[1]:.6f} {site_a[2]:.6f}" size="0.005"/>
              <site name="n{b}" pos="{site_b[0]:.6f} {site_b[1]:.6f} {site_b[2]:.6f}" size="0.005"/>
            </body>
        """))

    # Tendons: linear cable model (range="0 L0", stiffness>0, damping>0).
    tendons = []
    for c_idx, (a, b) in enumerate(CABLES):
        L0 = float(np.linalg.norm(nodes[a] - nodes[b]))
        # No pre-tension: cables behave as unilateral (zero force when slack).
        rest = L0
        tendons.append(textwrap.dedent(f"""
            <spatial name="cable{c_idx}" range="0 {rest:.6f}"
                     stiffness="{cable_stiffness:.2f}"
                     damping="{cable_damping:.2f}"
                     rgba="0.9 0.2 0.2 1" width="0.0015">
              <site site="n{a}"/>
              <site site="n{b}"/>
            </spatial>
        """))

    xml = f"""
    <mujoco model="tprism">
      <option gravity="0 0 -9.81" timestep="0.0005" integrator="RK4"/>
      <visual><global offwidth="800" offheight="600"/></visual>
      <worldbody>
        <geom name="floor" type="plane" size="2 2 0.1" rgba="0.8 0.8 0.8 1"/>
        {''.join(bodies)}
      </worldbody>
      <tendon>
        {''.join(tendons)}
      </tendon>
    </mujoco>
    """
    return xml


def run(duration: float = 1.5):
    xml = build_mjcf()
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)

    nsteps = int(duration / model.opt.timestep)
    t = np.zeros(nsteps)
    com_z = np.zeros(nsteps)
    ke = np.zeros(nsteps)
    pe = np.zeros(nsteps)            # gravitational
    se = np.zeros(nsteps)            # tendon strain energy
    g = -model.opt.gravity[2]

    # Pre-compute strut masses for KE/PE.
    masses = np.array([model.body_mass[i] for i in range(1, model.nbody)])
    total_mass = masses.sum()

    for k in range(nsteps):
        mujoco.mj_step(model, data)
        t[k] = data.time
        # COM height (mass-weighted z over all struts).
        zs = np.array([data.xpos[i, 2] for i in range(1, model.nbody)])
        com_z[k] = float(np.dot(masses, zs) / total_mass)
        ke[k] = float(np.sum(0.5 * masses * np.linalg.norm(data.cvel[1:, 3:6], axis=1) ** 2))
        pe[k] = float(total_mass * g * com_z[k])
        # Strain energy: 0.5 * k * max(0, L - L0)^2 per tendon.
        L = data.ten_length
        L0 = model.tendon_lengthspring[:, 1]
        kspring = model.tendon_stiffness
        strain = np.maximum(L - L0, 0.0)
        se[k] = float(0.5 * np.sum(kspring * strain ** 2))

    # Approx peak vertical deceleration of COM (numerical d^2 z / dt^2).
    dt = model.opt.timestep
    az = np.gradient(np.gradient(com_z, dt), dt)
    peak_g = float(np.max(np.abs(az)) / 9.81)
    settle_z = float(np.mean(com_z[-200:]))

    # Save data + plot.
    np.savez(os.path.join(OUT_DIR, "mujoco_drop_data.npz"),
             t=t, com_z=com_z, ke=ke, pe=pe, se=se, az=az)

    fig, axes = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    axes[0].plot(t, com_z, label="COM z (m)")
    axes[0].axhline(settle_z, ls="--", color="grey",
                    label=f"settled z = {settle_z:.3f} m")
    axes[0].set_ylabel("COM height (m)")
    axes[0].legend(loc="upper right")
    axes[0].set_title("MuJoCo: 3-bar tensegrity prism dropped from 1 m")
    axes[1].plot(t, ke, label="kinetic")
    axes[1].plot(t, se, label="tendon strain")
    axes[1].plot(t, pe - pe[-1], label="gravitational (offset)")
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("energy (J)")
    axes[1].legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "mujoco_drop_energy.png"), dpi=120)
    plt.close(fig)

    print(f"MuJoCo simulation OK ({nsteps} steps, dt={dt}s, T={duration}s)")
    print(f"  total mass     : {total_mass:.4f} kg")
    print(f"  settled COM z  : {settle_z:.4f} m")
    print(f"  peak COM accel : {peak_g:.2f} g (approx)")
    print(f"  peak KE        : {ke.max():.4f} J")
    print(f"  peak strain E  : {se.max():.4f} J")


if __name__ == "__main__":
    run()
