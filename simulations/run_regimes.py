"""Drive the MuJoCo prism through both application regimes (issue #18 +
issues #14/#16), embedded inside the Lansmont M23 envelope (issue #28).

For each regime we:
  1. Build a MuJoCo MJCF where the T-prism sits between the floor and a
     plate carrying the regime-specific payload mass; the plate starts at
     a height that gives the regime impact velocity.
  2. Step the dynamics, record the time-history of payload acceleration,
     plate force on the prism, and tendon strain energy.
  3. Sweep cable stiffness over two decades and recompute peak |a| (g),
     pulse width FWHM, and specific energy absorbed (SEA).
  4. Plot one time-history figure plus one stiffness-sweep figure per
     regime.

Outputs are written to ``simulations/outputs/`` next to the existing
single-engine demo plots.
"""
from __future__ import annotations

import os
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco
import numpy as np

from regimes import CRUTCH, NASA_LANDER, M23, Regime
from tprism_geometry import CABLES, STRUTS, tprism_nodes

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

G = 9.81  # m/s^2


def build_xml(r: Regime, *, cable_stiffness: float | None = None) -> str:
    """Build MJCF for regime ``r``.

    The prism sits with a 1 mm ground clearance and is given an initial
    downward velocity equal to the regime impact velocity (i.e. we start
    "at the moment of release after free-fall"); the plate above carries
    the regime payload mass with the same initial velocity so the unit
    cell is loaded in compression as soon as the bottom struts contact
    the floor.  This keeps the simulation window short and avoids
    spending compute on the free-fall phase.
    """
    if cable_stiffness is None:
        cable_stiffness = r.cable_stiffness_Npm

    z0 = 0.001  # 1 mm ground clearance
    nodes = tprism_nodes(radius=r.radius_m, height=r.height_m, z0=z0)

    plate_size = max(r.radius_m * 1.2, 0.02)
    plate_thickness = 0.01
    plate_z = z0 + r.height_m + plate_thickness * 0.5

    bodies, sites = [], []
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
              <site name="n{a}" pos="{sa[0]:.6f} {sa[1]:.6f} {sa[2]:.6f}" size="0.003"/>
              <site name="n{b}" pos="{sb[0]:.6f} {sb[1]:.6f} {sb[2]:.6f}" size="0.003"/>
            </body>
        """))
    # Plate body: total mass = payload mass.
    bodies.append(textwrap.dedent(f"""
        <body name="payload" pos="0 0 {plate_z:.6f}">
          <freejoint/>
          <geom type="box" size="{plate_size:.4f} {plate_size:.4f} {plate_thickness*0.5:.4f}"
                mass="{r.payload_mass_kg:.4f}" rgba="0.6 0.6 0.6 1"/>
        </body>
    """))

    tendons = []
    for c_idx, (a, b) in enumerate(CABLES):
        L0 = float(np.linalg.norm(nodes[a] - nodes[b]))
        rest = (1.0 - r.cable_pretension_frac) * L0
        tendons.append(textwrap.dedent(f"""
            <spatial name="cable{c_idx}" range="0 {rest:.6f}"
                     stiffness="{cable_stiffness:.2f}"
                     damping="{r.cable_damping_Nspm:.2f}"
                     rgba="0.9 0.2 0.2 1" width="0.0008">
              <site site="n{a}"/>
              <site site="n{b}"/>
            </spatial>
        """))

    return f"""
    <mujoco model="{r.name}">
      <option gravity="0 0 -9.81" timestep="{r.sim_dt_s}" integrator="RK4"/>
      <worldbody>
        <geom name="floor" type="plane" size="2 2 0.1" rgba="0.85 0.85 0.85 1"/>
        {''.join(bodies)}
      </worldbody>
      <tendon>
        {''.join(tendons)}
      </tendon>
    </mujoco>
    """


def simulate(r: Regime, *, cable_stiffness: float | None = None) -> dict:
    """Run one drop and return time-histories and scalar metrics."""
    xml = build_xml(r, cable_stiffness=cable_stiffness)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)

    # Identify payload body (last in the list).
    payload_id = model.nbody - 1
    nsteps = int(r.sim_duration_s / model.opt.timestep)
    t = np.zeros(nsteps)
    payload_z = np.zeros(nsteps)
    payload_vz = np.zeros(nsteps)
    se = np.zeros(nsteps)

    # Set the payload's initial *downward* velocity equal to the regime's
    # drop velocity, so we don't have to wait for it to fall.  This puts
    # the prism into compression at t=0 with the correct kinetic energy.
    # The prism struts likewise need v_z = -drop_velocity to ride along
    # with the payload (they are free bodies stacked between floor + plate
    # and otherwise would lag).
    for i in range(model.nbody):
        if i == 0:                       # world
            continue
        # qvel layout: 6 dof per free joint (3 lin + 3 ang).  Index 2 = z.
        addr = model.body_dofadr[i]
        data.qvel[addr + 2] = -r.drop_velocity_mps

    L0 = model.tendon_lengthspring[:, 1].copy()
    kspring = model.tendon_stiffness.copy()

    last_finite = nsteps
    for k in range(nsteps):
        mujoco.mj_step(model, data)
        t[k] = data.time
        payload_z[k] = data.xpos[payload_id, 2]
        payload_vz[k] = data.cvel[payload_id, 5]   # linear z velocity
        strain = np.maximum(data.ten_length - L0, 0.0)
        se[k] = float(0.5 * np.sum(kspring * strain ** 2))
        if (not np.isfinite(payload_z[k]) or not np.isfinite(payload_vz[k])
                or se[k] > 1e6 or se[k] < 0):
            last_finite = k
            break

    # Truncate to the finite/sane window for downstream metrics.
    t = t[:last_finite]
    payload_z = payload_z[:last_finite]
    payload_vz = payload_vz[:last_finite]
    se = se[:last_finite]
    if len(t) < 5:
        return {"regime": r.name, "t": t, "az_g": np.zeros_like(t),
                "vz": payload_vz, "z": payload_z, "se": se,
                "peak_g": float("nan"), "pulse_ms": float("nan"),
                "sea_Jpkg": float("nan"),
                "cable_stiffness_Npm": float(model.tendon_stiffness[0])}

    dt = model.opt.timestep
    az = np.gradient(payload_vz, dt)
    peak_g = float(np.max(np.abs(az)) / G)
    abs_a = np.abs(az) / G
    half = peak_g / 2.0
    above = abs_a >= half
    pulse_ms = (above.sum() * dt) * 1e3 if above.any() else 0.0
    sea = float(se.max() / r.payload_mass_kg)   # J/kg specific energy abs.

    return {
        "regime": r.name,
        "t": t, "az_g": az / G, "vz": payload_vz, "z": payload_z, "se": se,
        "peak_g": peak_g, "pulse_ms": pulse_ms, "sea_Jpkg": sea,
        "cable_stiffness_Npm": float(model.tendon_stiffness[0]),
    }


def plot_timeseries(res_list: list[dict], regime: Regime, fname: str) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(7.5, 8), sharex=True)
    for res in res_list:
        lbl = f"k = {res['cable_stiffness_Npm']:.0f} N/m"
        axes[0].plot(res["t"] * 1e3, res["az_g"], label=lbl)
        axes[1].plot(res["t"] * 1e3, res["vz"], label=lbl)
        axes[2].plot(res["t"] * 1e3, res["se"], label=lbl)
    axes[0].axhline(regime.target_peak_g, ls="--", color="grey",
                    label=f"target ≤ {regime.target_peak_g:.0f} g")
    axes[0].axhline(-regime.target_peak_g, ls="--", color="grey")
    axes[0].set_ylabel("payload accel (g)")
    axes[0].set_title(f"{regime.name}: {regime.description}")
    axes[0].legend(fontsize=8, loc="upper right")
    axes[1].set_ylabel("payload v_z (m/s)")
    axes[2].set_ylabel("tendon strain E (J)")
    axes[2].set_xlabel("time (ms)")
    for ax in axes:
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, fname), dpi=120)
    plt.close(fig)


def plot_sweep(rows: list[dict], regime: Regime, fname: str) -> None:
    ks = np.array([r["cable_stiffness_Npm"] for r in rows])
    pg = np.array([r["peak_g"] for r in rows])
    sea = np.array([r["sea_Jpkg"] for r in rows])

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    color1 = "tab:red"
    ax1.set_xscale("log")
    ax1.plot(ks, pg, "o-", color=color1, label="peak |a| (g)")
    ax1.axhline(regime.target_peak_g, ls="--", color=color1, alpha=0.5,
                label=f"target ≤ {regime.target_peak_g:.0f} g")
    ax1.set_xlabel("cable (TPU tendon) stiffness (N/m)")
    ax1.set_ylabel("peak |payload accel| (g)", color=color1)
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.grid(True, which="both", alpha=0.3)

    ax2 = ax1.twinx()
    color2 = "tab:blue"
    ax2.plot(ks, sea, "s--", color=color2, label="SEA (J/kg)")
    ax2.set_ylabel("specific energy absorbed (J/kg)", color=color2)
    ax2.tick_params(axis="y", labelcolor=color2)

    ax1.set_title(f"{regime.name}: BO objective surface (1-D slice)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, fname), dpi=120)
    plt.close(fig)


def main():
    print(f"Lansmont M23 envelope: {M23}\n")
    summary_rows = []
    for regime in (CRUTCH, NASA_LANDER):
        print(f"=== Regime: {regime.name} ===")
        print(f"   {regime.description}")

        # 1. Three illustrative single runs (soft / nominal / stiff cable).
        ks_show = np.array([0.25, 1.0, 4.0]) * regime.cable_stiffness_Npm
        ts_runs = [simulate(regime, cable_stiffness=float(k)) for k in ks_show]
        plot_timeseries(ts_runs, regime,
                        f"regime_{regime.name}_timeseries.png")
        for res in ts_runs:
            print(f"   k={res['cable_stiffness_Npm']:8.0f} N/m  "
                  f"peak={res['peak_g']:7.1f} g  "
                  f"pulse={res['pulse_ms']:5.2f} ms  "
                  f"SEA={res['sea_Jpkg']:7.3f} J/kg")

        # 2. Stiffness sweep for the BO-objective figure.
        ks_sweep = np.geomspace(0.05, 8.0, 11) * regime.cable_stiffness_Npm
        sweep_rows = [simulate(regime, cable_stiffness=float(k))
                      for k in ks_sweep]
        plot_sweep(sweep_rows, regime, f"regime_{regime.name}_sweep.png")

        # 3. Save numeric summary CSV.
        arr = np.array([(s["cable_stiffness_Npm"], s["peak_g"],
                         s["pulse_ms"], s["sea_Jpkg"]) for s in sweep_rows])
        np.savetxt(os.path.join(OUT_DIR, f"regime_{regime.name}_sweep.csv"),
                   arr, delimiter=",",
                   header="cable_stiffness_Npm,peak_g,pulse_ms,sea_Jpkg",
                   comments="")

        # 4. Pick the best-by-target row for the final summary.
        best = min(sweep_rows, key=lambda s: abs(s["peak_g"]
                                                 - regime.target_peak_g))
        summary_rows.append((regime.name, best))
        print(f"   best-fit-to-target: k={best['cable_stiffness_Npm']:.0f} N/m, "
              f"peak={best['peak_g']:.1f} g (target ≤ {regime.target_peak_g} g), "
              f"pulse={best['pulse_ms']:.2f} ms, SEA={best['sea_Jpkg']:.3f} J/kg\n")

    print("== Summary ==")
    print(f"{'regime':<14} {'k* (N/m)':>10} {'peak (g)':>10} "
          f"{'pulse (ms)':>11} {'SEA (J/kg)':>11}")
    for name, b in summary_rows:
        print(f"{name:<14} {b['cable_stiffness_Npm']:>10.0f} "
              f"{b['peak_g']:>10.1f} {b['pulse_ms']:>11.2f} "
              f"{b['sea_Jpkg']:>11.3f}")


if __name__ == "__main__":
    main()
