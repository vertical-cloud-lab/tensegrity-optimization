"""Sweep cable stiffness in the MuJoCo prism drop and record peak deceleration.

This is the kind of black-box objective evaluation a Bayesian-optimization
loop would call: vary one or more design parameters (here, only the cable
spring constant) and measure an energy-absorption metric (peak vertical
deceleration of the COM during a 1 m drop -- lower = better cushioning).

The script intentionally re-uses ``mujoco_drop.build_mjcf`` so a future BO
driver only needs to wrap ``evaluate(...)``.
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco
import numpy as np

from mujoco_drop import build_mjcf

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def evaluate(cable_stiffness: float, *, duration: float = 1.5) -> dict:
    """Run one drop and return a dict of scalar metrics."""
    xml = build_mjcf(cable_stiffness=cable_stiffness)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    nsteps = int(duration / model.opt.timestep)
    masses = np.array([model.body_mass[i] for i in range(1, model.nbody)])
    total = masses.sum()
    z = np.zeros(nsteps)
    se = np.zeros(nsteps)
    for k in range(nsteps):
        mujoco.mj_step(model, data)
        zs = np.array([data.xpos[i, 2] for i in range(1, model.nbody)])
        z[k] = float(np.dot(masses, zs) / total)
        L = data.ten_length
        L0 = model.tendon_lengthspring[:, 1]
        kspring = model.tendon_stiffness
        strain = np.maximum(L - L0, 0.0)
        se[k] = float(0.5 * np.sum(kspring * strain ** 2))
    az = np.gradient(np.gradient(z, model.opt.timestep), model.opt.timestep)
    return {
        "k": cable_stiffness,
        "peak_g": float(np.max(np.abs(az)) / 9.81),
        "peak_strain_J": float(se.max()),
        "settled_z": float(np.mean(z[-200:])),
    }


def main():
    ks = np.geomspace(5.0e2, 5.0e4, 9)
    rows = [evaluate(float(k)) for k in ks]
    print(f"{'k (N/m)':>10} {'peak_g':>9} {'peak_SE (J)':>13} {'settled z (m)':>15}")
    for r in rows:
        print(f"{r['k']:10.1f} {r['peak_g']:9.2f} {r['peak_strain_J']:13.4f} {r['settled_z']:15.4f}")

    # Save table + plot.
    arr = np.array([(r["k"], r["peak_g"], r["peak_strain_J"], r["settled_z"])
                    for r in rows])
    np.savetxt(os.path.join(OUT_DIR, "mujoco_sweep.csv"), arr,
               header="cable_stiffness_Npm,peak_g,peak_strain_J,settled_z_m",
               delimiter=",", comments="")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogx(arr[:, 0], arr[:, 1], "o-")
    ax.set_xlabel("cable stiffness (N/m)")
    ax.set_ylabel("peak |COM deceleration| (g)")
    ax.set_title("MuJoCo: BO objective candidate vs. cable stiffness")
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "mujoco_sweep.png"), dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    main()
