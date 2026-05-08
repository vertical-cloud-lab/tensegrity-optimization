"""PyBullet simulation of a 3-bar tensegrity prism (rigid struts + spring cables).

PyBullet has no native tendon primitive, so we model each cable as a Hookean
unilateral spring (compression = zero force) and apply equal/opposite forces
to the two strut anchor points each timestep.  This is the classical mass-
spring approach used by NTRTsim's predecessor Bullet-based engine.

Outputs
-------
- simulations/outputs/pybullet_drop_data.npz
- simulations/outputs/pybullet_drop_energy.png
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pybullet as p
import pybullet_data

from tprism_geometry import CABLES, STRUTS, tprism_nodes

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def _make_strut(p0: np.ndarray, p1: np.ndarray, *,
                radius: float, density: float):
    """Create a single capsule strut between world points p0 and p1."""
    vec = p1 - p0
    length = float(np.linalg.norm(vec))
    center = 0.5 * (p0 + p1)
    # Orient capsule along its long axis (pybullet capsule local Z is long).
    z = vec / length
    # Build a rotation matrix mapping +Z to z, then convert to quaternion.
    if abs(z[2]) < 0.999:
        x = np.cross(np.array([0.0, 0.0, 1.0]), z)
    else:
        x = np.cross(np.array([1.0, 0.0, 0.0]), z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    R = np.column_stack([x, y, z])
    # quaternion from rotation matrix.
    qw = 0.5 * np.sqrt(max(1e-12, 1 + R[0, 0] + R[1, 1] + R[2, 2]))
    qx = (R[2, 1] - R[1, 2]) / (4 * qw)
    qy = (R[0, 2] - R[2, 0]) / (4 * qw)
    qz = (R[1, 0] - R[0, 1]) / (4 * qw)
    quat = [qx, qy, qz, qw]

    vol = np.pi * radius ** 2 * length
    mass = density * vol
    col = p.createCollisionShape(p.GEOM_CAPSULE, radius=radius, height=length)
    vis = p.createVisualShape(p.GEOM_CAPSULE, radius=radius, length=length,
                              rgbaColor=[0.2, 0.4, 0.9, 1.0])
    bid = p.createMultiBody(baseMass=mass,
                            baseCollisionShapeIndex=col,
                            baseVisualShapeIndex=vis,
                            basePosition=center.tolist(),
                            baseOrientation=quat)
    return bid, length


def _world_anchor(body_id: int, local_offset: np.ndarray) -> np.ndarray:
    pos, orn = p.getBasePositionAndOrientation(body_id)
    R = np.array(p.getMatrixFromQuaternion(orn)).reshape(3, 3)
    return np.asarray(pos) + R @ local_offset


def run(duration: float = 1.5, dt: float = 1.0e-3):
    p.connect(p.DIRECT)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.81)
    p.setTimeStep(dt)
    p.loadURDF("plane.urdf")

    nodes = tprism_nodes(z0=1.0)  # drop from 1 m
    strut_radius = 0.006
    density = 1240.0

    strut_bodies: list[int] = []
    local_anchors: list[tuple[np.ndarray, np.ndarray]] = []
    for a, b in STRUTS:
        bid, _ = _make_strut(nodes[a], nodes[b],
                             radius=strut_radius, density=density)
        strut_bodies.append(bid)
        # Local anchors in body frame at construction.
        center = 0.5 * (nodes[a] + nodes[b])
        # Body initially world-aligned offset = world point - center, then
        # rotated into body frame; we rebuilt R above so reuse it via inverse.
        _, orn = p.getBasePositionAndOrientation(bid)
        R = np.array(p.getMatrixFromQuaternion(orn)).reshape(3, 3)
        loc_a = R.T @ (nodes[a] - center)
        loc_b = R.T @ (nodes[b] - center)
        local_anchors.append((loc_a, loc_b))

    # Map node index -> (strut body id, local anchor offset).
    node_anchor: dict[int, tuple[int, np.ndarray]] = {}
    for s_idx, (a, b) in enumerate(STRUTS):
        node_anchor[a] = (strut_bodies[s_idx], local_anchors[s_idx][0])
        node_anchor[b] = (strut_bodies[s_idx], local_anchors[s_idx][1])

    cable_rest = []
    for a, b in CABLES:
        L0 = float(np.linalg.norm(nodes[a] - nodes[b]))
        cable_rest.append(L0)  # no pre-tension; unilateral cables only

    cable_k = 8.0e3
    cable_c = 5.0

    nsteps = int(duration / dt)
    t = np.zeros(nsteps)
    com_z = np.zeros(nsteps)
    ke = np.zeros(nsteps)
    se = np.zeros(nsteps)

    masses = []
    for bid in strut_bodies:
        info = p.getDynamicsInfo(bid, -1)
        masses.append(info[0])
    masses = np.asarray(masses)
    total_mass = masses.sum()

    for k in range(nsteps):
        # Apply cable forces.
        strain_energy = 0.0
        for (a, b), L0 in zip(CABLES, cable_rest):
            ba, oa = node_anchor[a]
            bb, ob = node_anchor[b]
            wa = _world_anchor(ba, oa)
            wb = _world_anchor(bb, ob)
            d = wb - wa
            L = float(np.linalg.norm(d))
            if L < 1e-9:
                continue
            n = d / L
            stretch = max(0.0, L - L0)
            # Damping along cable axis.
            va = np.asarray(p.getBaseVelocity(ba)[0])
            vb = np.asarray(p.getBaseVelocity(bb)[0])
            vrel = float(np.dot(vb - va, n))
            f_mag = cable_k * stretch + cable_c * vrel
            if f_mag < 0.0:                       # cables can't push
                f_mag = 0.0
            f_vec = f_mag * n
            p.applyExternalForce(ba, -1, f_vec.tolist(), wa.tolist(),
                                 p.WORLD_FRAME)
            p.applyExternalForce(bb, -1, (-f_vec).tolist(), wb.tolist(),
                                 p.WORLD_FRAME)
            strain_energy += 0.5 * cable_k * stretch ** 2

        p.stepSimulation()
        t[k] = (k + 1) * dt
        zs = np.array([p.getBasePositionAndOrientation(b)[0][2]
                       for b in strut_bodies])
        com_z[k] = float(np.dot(masses, zs) / total_mass)
        vels = np.array([p.getBaseVelocity(b)[0] for b in strut_bodies])
        ke[k] = float(np.sum(0.5 * masses * np.linalg.norm(vels, axis=1) ** 2))
        se[k] = float(strain_energy)

    p.disconnect()

    np.savez(os.path.join(OUT_DIR, "pybullet_drop_data.npz"),
             t=t, com_z=com_z, ke=ke, se=se)

    fig, axes = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    axes[0].plot(t, com_z)
    axes[0].set_ylabel("COM height (m)")
    axes[0].set_title("PyBullet: 3-bar tensegrity prism dropped from 1 m")
    axes[1].plot(t, ke, label="kinetic")
    axes[1].plot(t, se, label="cable strain")
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("energy (J)")
    axes[1].legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "pybullet_drop_energy.png"), dpi=120)
    plt.close(fig)

    print(f"PyBullet simulation OK ({nsteps} steps, dt={dt}s)")
    print(f"  total mass     : {total_mass:.4f} kg")
    print(f"  settled COM z  : {float(np.mean(com_z[-100:])):.4f} m")
    print(f"  peak KE        : {ke.max():.4f} J")
    print(f"  peak strain E  : {se.max():.4f} J")


if __name__ == "__main__":
    run()
