#!/usr/share/miniconda/bin/python
"""PyChrono (Project Chrono 10.x) simulation of a 3-bar tensegrity prism.

Project Chrono is installed via conda from the `projectchrono` channel:

    conda install -c projectchrono -c conda-forge pychrono

Note: the homonymous PyPI package `pychrono` is unrelated and must NOT be
installed.  This script uses the conda Python interpreter explicitly via
its shebang line.

Each cable is modelled with a ChLinkTSDA (translational spring-damper-
actuator) link using the native ``SetSpringCoefficient`` /
``SetDampingCoefficient`` API.  TSDA produces equal-and-opposite forces
along the link axis proportional to (length - rest), which is the
classical Hookean cable; we set ``rest = L0`` so cables behave as
unilateral cables (zero force when slack, since contact is the only
external compressive load).  Struts are ChBodyEasyCylinder rigid bodies.

Outputs
-------
- simulations/outputs/pychrono_drop_data.npz
- simulations/outputs/pychrono_drop_energy.png
"""
from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pychrono as chrono

sys.path.insert(0, os.path.dirname(__file__))
from tprism_geometry import CABLES, STRUTS, tprism_nodes  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def _make_strut(sys_, p0, p1, *, radius, density, mat=None):
    vec = p1 - p0
    length = float(np.linalg.norm(vec))
    center = 0.5 * (p0 + p1)
    if mat is None:
        body = chrono.ChBodyEasyCylinder(chrono.ChAxis_Y, radius, length,
                                         density, True, False)
    else:
        body = chrono.ChBodyEasyCylinder(chrono.ChAxis_Y, radius, length,
                                         density, True, True, mat)
    body.SetPos(chrono.ChVector3d(*center))
    z_world = chrono.ChVector3d(*(vec / length))
    q = chrono.QuatFromVec2Vec(chrono.ChVector3d(0, 1, 0), z_world)
    body.SetRot(q)
    sys_.Add(body)
    return body


def run(duration: float = 1.5, dt: float = 2.0e-4):
    sys_ = chrono.ChSystemSMC()
    sys_.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))
    sys_.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

    mat = chrono.ChContactMaterialSMC()
    mat.SetYoungModulus(2.0e7)
    mat.SetFriction(0.6)
    mat.SetRestitution(0.1)

    ground = chrono.ChBodyEasyBox(4.0, 4.0, 0.05, 1000.0, True, True, mat)
    ground.SetPos(chrono.ChVector3d(0, 0, -0.025))
    ground.SetFixed(True)
    sys_.Add(ground)

    nodes = tprism_nodes(z0=1.0)
    radius = 0.006
    density = 1240.0

    strut_bodies = []
    for a, b in STRUTS:
        strut_bodies.append(_make_strut(sys_, nodes[a], nodes[b],
                                        radius=radius, density=density,
                                        mat=mat))

    node_anchor = {}
    for s_idx, (a, b) in enumerate(STRUTS):
        node_anchor[a] = (strut_bodies[s_idx], nodes[a])
        node_anchor[b] = (strut_bodies[s_idx], nodes[b])

    cable_k = 8.0e3
    cable_c = 5.0
    links = []
    for a, b in CABLES:
        ba, wa = node_anchor[a]
        bb, wb = node_anchor[b]
        L0 = float(np.linalg.norm(wb - wa))
        rest = L0  # no pre-tension; cables start just-taut
        link = chrono.ChLinkTSDA()
        link.Initialize(ba, bb, False,
                        chrono.ChVector3d(*wa), chrono.ChVector3d(*wb))
        link.SetRestLength(rest)
        link.SetSpringCoefficient(cable_k)
        link.SetDampingCoefficient(cable_c)
        sys_.Add(link)
        links.append(link)

    sys_.SetSolverType(chrono.ChSolver.Type_BARZILAIBORWEIN)
    sys_.GetSolver().AsIterative().SetMaxIterations(150)

    nsteps = int(duration / dt)
    t = np.zeros(nsteps)
    com_z = np.zeros(nsteps)
    ke = np.zeros(nsteps)
    se = np.zeros(nsteps)
    masses = np.array([b.GetMass() for b in strut_bodies])
    total = float(masses.sum())

    for k in range(nsteps):
        sys_.DoStepDynamics(dt)
        t[k] = sys_.GetChTime()
        zs = np.array([b.GetPos().z for b in strut_bodies])
        com_z[k] = float(np.dot(masses, zs) / total)
        v = np.array([[b.GetPosDt().x, b.GetPosDt().y, b.GetPosDt().z]
                      for b in strut_bodies])
        ke[k] = float(np.sum(0.5 * masses * np.sum(v ** 2, axis=1)))
        s_e = 0.0
        for link in links:
            stretch = max(0.0, link.GetLength() - link.GetRestLength())
            s_e += 0.5 * cable_k * stretch ** 2
        se[k] = s_e

    np.savez(os.path.join(OUT_DIR, "pychrono_drop_data.npz"),
             t=t, com_z=com_z, ke=ke, se=se)

    fig, axes = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    axes[0].plot(t, com_z)
    axes[0].set_ylabel("COM height (m)")
    axes[0].set_title("PyChrono: 3-bar tensegrity prism dropped from 1 m")
    axes[1].plot(t, ke, label="kinetic")
    axes[1].plot(t, se, label="cable strain")
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("energy (J)")
    axes[1].legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "pychrono_drop_energy.png"), dpi=120)
    plt.close(fig)

    print(f"PyChrono simulation OK ({nsteps} steps, dt={dt}s)")
    print(f"  total mass     : {total:.4f} kg")
    print(f"  settled COM z  : {float(np.mean(com_z[-100:])):.4f} m")
    print(f"  peak KE        : {ke.max():.4f} J")
    print(f"  peak strain E  : {se.max():.4f} J")


if __name__ == "__main__":
    run()
