"""Mid-fidelity tensegrity drop simulation using NVIDIA Newton + Warp.

This is the **Edison "Recommendation B"** escalation from the rigid-strut
MuJoCo / PyBullet / PyChrono sims under ``simulations/{mujoco,pybullet,
pychrono}_drop.py``.  The original Recommendation B target was DiffPD
(MIT GFX, SIGGRAPH 2021), but it is not on PyPI and its CMake/Pangolin
build fails on the lab's Linux runners.  Newton (NVIDIA's open-source
GPU-accelerated, *differentiable* physics engine, ``pip install
newton``) provides the same capability we needed from DiffPD:

* a single physical model that mixes **rigid bodies, particles, and
  springs with full bidirectional coupling**, so the TPU tendons are
  actually in the load path;
* a soft-contact pipeline (``CollisionPipeline``, ``soft_contact_ke``)
  rather than the hard floor-pin in MuJoCo's rigid-strut model;
* differentiable autodiff via Warp tapes (the reason DiffPD was
  recommended in the first place — for BO gradient access later).

Geometry
--------
The 3-bar Snelson T-prism from ``tprism_geometry.py`` is built as
**all-particle**: 6 prism nodes + 1 payload node.  Each strut is a
high-stiffness spring (PLA, E ≈ 3.5 GPa, A from strut Ø) and each cable
is a TPU-85A spring (E ≈ 12 MPa secant).  The payload is rigidly
coupled to the three top nodes by additional stiff springs.  The whole
thing is dropped from height ``drop_height`` onto the Newton ground
plane.

This is *not* yet IPC-grade barrier-method contact (Recommendation A);
that requires PolyFEM, whose PyPI sdist is broken (no CMakeLists.txt
in the upload).  We document the install attempt next to this script in
``newton_drop.md`` so a future agent can rerun it cleanly.
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import newton
import warp as wp

from printable_design import PLA, TPU85A
from tprism_geometry import (
    BOTTOM_CABLES, EQUILIBRIUM_TWIST, STRUTS, TOP_CABLES, VERT_CABLES,
    tprism_nodes,
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def axial_spring_ke(young_MPa: float, area_m2: float, length_m: float) -> float:
    """k = E * A / L."""
    return young_MPa * 1e6 * area_m2 / length_m


def build_model(*, radius_m=0.10, height_m=0.20,
                strut_dia_m=8.0e-3, tendon_dia_m=3.0e-3,
                payload_mass_kg=1.0, drop_height_m=0.10,
                impact_velocity_mps=0.0,
                node_mass_kg=0.005):
    """Build a Newton model of the prism + payload + ground.

    ``impact_velocity_mps`` seeds an initial downward velocity on every
    particle so the cell already carries the regime-defined impact speed
    at the start of the (short) free-fall over ``drop_height_m``.  This is
    what makes the drop *regime-aware*: a crutch (1.4 m/s) and a lander
    (9.8 m/s) hit the floor at very different speeds even though their
    geometry and clearance are identical.  The default of ``0.0`` keeps the
    historical pure-free-fall behaviour.
    """
    builder = newton.ModelBuilder(up_axis="Z", gravity=-9.81)

    nodes = tprism_nodes(radius=radius_m, height=height_m,
                         twist=EQUILIBRIUM_TWIST)
    # Lift so the lowest node starts at drop_height + small clearance.
    nodes[:, 2] += drop_height_m

    init_vel = (0.0, 0.0, -float(impact_velocity_mps))

    # Add particles for the 6 prism nodes.
    pids = []
    for p in nodes:
        pid = builder.add_particle(pos=tuple(map(float, p)),
                                   vel=init_vel,
                                   mass=node_mass_kg)
        pids.append(pid)

    # Payload particle at the centroid of the top triangle.
    top_centroid = nodes[3:6].mean(axis=0)
    payload_pid = builder.add_particle(pos=tuple(map(float, top_centroid)),
                                       vel=init_vel,
                                       mass=payload_mass_kg)

    A_strut = np.pi * (0.5 * strut_dia_m) ** 2
    A_tendon = np.pi * (0.5 * tendon_dia_m) ** 2

    # Strut springs: PLA, very stiff -> behave as rigid at our regime.
    strut_len = float(np.linalg.norm(nodes[STRUTS[0][0]] - nodes[STRUTS[0][1]]))
    ke_strut = axial_spring_ke(PLA.young_MPa, A_strut, strut_len)
    for (a, b) in STRUTS:
        builder.add_spring(pids[a], pids[b], ke=ke_strut, kd=0.0, control=0.0)

    # Tendon springs: TPU 85A, moderate stiffness; small damping to keep
    # the explicit XPBD integrator stable through the impact.
    for (a, b) in BOTTOM_CABLES + TOP_CABLES + VERT_CABLES:
        L = float(np.linalg.norm(nodes[a] - nodes[b]))
        ke = axial_spring_ke(TPU85A.young_MPa, A_tendon, L)
        builder.add_spring(pids[a], pids[b], ke=ke, kd=0.05, control=0.0)

    # Couple payload to *all 6* prism nodes via TPU-85A tendons — this is
    # the SUPERball / NASA TBR architecture and it puts the cable network
    # in series with the impact load path (which was the whole point of
    # escalating from rigid-strut MuJoCo).  The vertical span of these
    # internal tendons is approximately ``height_m``.
    A_payload_tendon = np.pi * (0.5 * tendon_dia_m) ** 2
    for node_idx in range(6):
        L = float(np.linalg.norm(nodes[node_idx] - top_centroid))
        ke = axial_spring_ke(TPU85A.young_MPa, A_payload_tendon, max(L, 1e-3))
        builder.add_spring(pids[node_idx], payload_pid, ke=ke, kd=0.05,
                           control=0.0)

    builder.add_ground_plane()
    return builder, pids, payload_pid


def simulate(builder, payload_pid, *, sim_time_s=0.10, dt=2.5e-5):
    model = builder.finalize()
    model.soft_contact_ke = 5.0e4
    model.soft_contact_kd = 1.0e1
    model.soft_contact_mu = 0.5

    solver = newton.solvers.SolverXPBD(model=model, iterations=8)
    pipeline = newton.CollisionPipeline(model, broad_phase="nxn",
                                        soft_contact_margin=2.0e-3)
    state0 = model.state()
    state1 = model.state()
    contacts = pipeline.contacts()
    control = model.control()

    n_steps = int(sim_time_s / dt)
    times = np.zeros(n_steps + 1)
    pz = np.zeros(n_steps + 1)
    pvz = np.zeros(n_steps + 1)
    paz = np.zeros(n_steps + 1)

    pz[0] = state0.particle_q.numpy()[payload_pid][2]
    pvz[0] = state0.particle_qd.numpy()[payload_pid][2]
    last_vz = pvz[0]

    for i in range(n_steps):
        state0.clear_forces()
        pipeline.collide(state0, contacts)
        solver.step(state0, state1, control, contacts, dt)
        state0, state1 = state1, state0

        q = state0.particle_q.numpy()[payload_pid]
        qd = state0.particle_qd.numpy()[payload_pid]
        times[i + 1] = (i + 1) * dt
        pz[i + 1] = q[2]
        pvz[i + 1] = qd[2]
        paz[i + 1] = (qd[2] - last_vz) / dt
        last_vz = qd[2]

    return dict(t=times, payload_z=pz, payload_vz=pvz,
                payload_az=paz, dt=dt)


def peak_decel_g(res, *, skip_ms: float = 2.0, smooth_ms: float = 0.3) -> float:
    """Robust peak payload deceleration (in g) during the genuine impact.

    The raw single-step finite-difference acceleration is dominated by a
    numerical start-up spike at the first XPBD step (the seeded impact
    velocity produces a huge ``(v[1]-v[0])/dt`` artifact), which is regime-
    and velocity-*insensitive*.  This helper (a) discards the first
    ``skip_ms`` of start-up transient and (b) lightly low-pass smooths the
    acceleration over ``smooth_ms`` before taking the magnitude peak, so the
    returned value reflects the real ground-contact deceleration and scales
    with impact velocity (Edison review 491f90ae: the previous raw peak made
    Tier-B regime-blind).
    """
    az = np.asarray(res["payload_az"], dtype=float)
    dt = float(res["dt"])
    az = np.nan_to_num(az, nan=0.0, posinf=0.0, neginf=0.0)
    skip = min(len(az) - 1, max(1, int(skip_ms * 1e-3 / dt)))
    az = az.copy()
    az[:skip] = 0.0
    w = max(1, int(smooth_ms * 1e-3 / dt))
    if w > 1:
        az = np.convolve(az, np.ones(w) / w, mode="same")
    return float(np.max(np.abs(az)) / 9.81) if az.size else float("nan")


def main():
    print("Newton (Warp) mid-fidelity tensegrity drop sim")
    print(f"  PLA E = {PLA.young_MPa:.0f} MPa   "
          f"TPU 85A E = {TPU85A.young_MPa:.0f} MPa\n")

    builder, _pids, payload_pid = build_model(
        radius_m=0.10, height_m=0.20,
        strut_dia_m=8.0e-3, tendon_dia_m=3.0e-3,
        payload_mass_kg=1.0, drop_height_m=0.10)
    res = simulate(builder, payload_pid, sim_time_s=0.20, dt=5.0e-5)

    g = 9.81
    peak_g = float(np.max(np.abs(res["payload_az"])) / g)
    print(f"  drop height        : 0.10 m  (mgh = {1.0*g*0.10:.3f} J)")
    print(f"  peak |payload accel|: {peak_g:.1f} g")
    print(f"  settled payload z  : {res['payload_z'][-50:].mean()*1e3:.1f} mm")

    # --- figure: payload accel + z vs time ---
    fig, axes = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
    axes[0].plot(res["t"] * 1e3, res["payload_az"] / g, lw=1.0, color="C0")
    axes[0].set_ylabel("payload accel (g)")
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title(
        "Newton (Warp XPBD) prism drop, all-particle TPU-85A tendons "
        "in load path"
    )
    axes[1].plot(res["t"] * 1e3, res["payload_z"] * 1e3, lw=1.0, color="C2")
    axes[1].set_xlabel("time (ms)")
    axes[1].set_ylabel("payload z (mm)")
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "newton_drop.png"), dpi=120)
    plt.close(fig)
    np.savez(os.path.join(OUT_DIR, "newton_drop.npz"), **res)
    print("  wrote outputs/newton_drop.{png,npz}")

    # --- mini sweep: tendon Ø in {1.5, 3.0, 5.0} mm ---
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    rows = []
    for d_t in (1.5e-3, 3.0e-3, 5.0e-3):
        b, _p, pp = build_model(tendon_dia_m=d_t)
        r = simulate(b, pp, sim_time_s=0.20, dt=5.0e-5)
        ax2.plot(r["t"] * 1e3, r["payload_az"] / g,
                 label=f"d_t = {d_t*1e3:.1f} mm", lw=1.0)
        peak = float(np.max(np.abs(r["payload_az"])) / g)
        rows.append((d_t * 1e3, peak))
        print(f"  d_t = {d_t*1e3:4.1f} mm  -> peak {peak:5.1f} g")
    ax2.set_xlabel("time (ms)")
    ax2.set_ylabel("payload accel (g)")
    ax2.set_title("Newton tendon-Ø sweep (TPU 85A in load path)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(os.path.join(OUT_DIR, "newton_tendon_sweep.png"), dpi=120)
    plt.close(fig2)
    np.savetxt(os.path.join(OUT_DIR, "newton_tendon_sweep.csv"),
               np.array(rows), delimiter=",",
               header="tendon_dia_mm,peak_g", comments="")
    print("  wrote outputs/newton_tendon_sweep.{png,csv}")


if __name__ == "__main__":
    main()
