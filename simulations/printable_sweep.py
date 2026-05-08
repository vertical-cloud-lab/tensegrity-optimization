"""Sweep over *printable* PETG-strut + TPU-tendon design variables.

Where ``run_regimes.py`` swept an abstract cable stiffness ``k`` (N/m),
this driver instead sweeps over the variables the operator actually
chooses at design / print time:

* **Tendon diameter** d_t (mm).  The H2D's 0.4 mm nozzle bounds the
  practical range ~ 1.2 - 6.0 mm; outside this we either cannot print
  the tendon at all (lower bound) or should switch to a multi-strand
  bundle (upper bound).
* **Tendon prestrain** epsilon_0 (%).  Set physically by the assembly
  fixture or by sewing the tendon at length (1 - eps_0) * L0.

The peak deceleration / specific-energy-absorbed metrics are then
re-computed by re-using the same MuJoCo backend as ``run_regimes.py``,
but with cable stiffness derived as ``k = E_TPU * pi (d_t/2)^2 / L``
using the TPU 95A modulus (~25 MPa).

Two figures per regime are written to ``outputs/``:

* ``regime_<name>_printable_heatmap.png`` -- 2D heatmap of peak |a| (g)
  over (tendon dia, prestrain), with the class-1 region (struts not in
  contact) highlighted.
* ``regime_<name>_printable_pareto.png`` -- Pareto cloud of peak (g)
  vs SEA (J/kg) over the same grid, colour-coded by tendon diameter.
"""
from __future__ import annotations

import os
from itertools import product

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import run_regimes
from printable_design import (
    MAX_PRINTABLE_TENDON_DIA_M, MIN_PRINTABLE_TENDON_DIA_M,
    PrintableDesign, TPU95A, tpu_cable_stiffness_Npm,
)
from regimes import CRUTCH, NASA_LANDER, Regime
from tprism_geometry import EQUILIBRIUM_TWIST

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def regime_to_design(r: Regime, *, tendon_dia_m: float, strut_dia_m: float,
                     prestrain: float) -> PrintableDesign:
    return PrintableDesign(
        radius_m=r.radius_m, height_m=r.height_m,
        twist_rad=EQUILIBRIUM_TWIST,
        strut_diameter_m=strut_dia_m,
        tendon_diameter_m=tendon_dia_m,
        prestrain=prestrain,
    )


def simulate_design(r: Regime, design: PrintableDesign) -> dict:
    """Run the same MuJoCo drop as run_regimes.simulate(), but with the
    cable stiffness *derived* from the printable design and the cable
    pretension overridden from the design."""
    # We mutate a copy of the regime to inject the design's prestrain.
    from dataclasses import replace
    r2 = replace(r, cable_pretension_frac=design.prestrain)
    res = run_regimes.simulate(r2, cable_stiffness=design.cable_stiffness_Npm)
    res["tendon_dia_m"] = design.tendon_diameter_m
    res["prestrain"] = design.prestrain
    res["class_1"] = design.is_class_1
    res["class_1_margin_m"] = design.class_1_margin_m
    return res


def sweep_regime(r: Regime, *, strut_dia_m: float,
                 tendon_dias_m: np.ndarray,
                 prestrains: np.ndarray) -> list[dict]:
    rows = []
    for d_t, eps in product(tendon_dias_m, prestrains):
        design = regime_to_design(r, tendon_dia_m=d_t,
                                  strut_dia_m=strut_dia_m,
                                  prestrain=eps)
        res = simulate_design(r, design)
        rows.append(res)
    return rows


def plot_heatmap(rows: list[dict], regime: Regime,
                 tendon_dias_m: np.ndarray, prestrains: np.ndarray,
                 fname: str) -> None:
    nx, ny = len(tendon_dias_m), len(prestrains)
    Z = np.array([r["peak_g"] for r in rows]).reshape(nx, ny)
    sea = np.array([r["sea_Jpkg"] for r in rows]).reshape(nx, ny)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    extent = [prestrains[0] * 100, prestrains[-1] * 100,
              tendon_dias_m[0] * 1e3, tendon_dias_m[-1] * 1e3]
    for ax, data, label in [(axes[0], Z, "peak |a| (g)"),
                            (axes[1], sea, "SEA (J/kg)")]:
        im = ax.imshow(data, origin="lower", aspect="auto",
                       extent=extent, cmap="viridis")
        ax.set_xlabel("tendon prestrain (%)")
        ax.set_ylabel("tendon diameter (mm)")
        ax.set_title(f"{regime.name}: {label}")
        fig.colorbar(im, ax=ax, label=label)
    fig.suptitle(f"{regime.name}: printable design sweep "
                 f"(PETG strut Ø{regime.strut_radius_m*2*1e3:.1f} mm + "
                 f"TPU 95A tendons; E={TPU95A.young_MPa:.0f} MPa)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, fname), dpi=120)
    plt.close(fig)


def plot_pareto(rows: list[dict], regime: Regime, fname: str) -> None:
    pg = np.array([r["peak_g"] for r in rows])
    sea = np.array([r["sea_Jpkg"] for r in rows])
    dt = np.array([r["tendon_dia_m"] for r in rows]) * 1e3
    eps = np.array([r["prestrain"] for r in rows]) * 100

    fig, ax = plt.subplots(figsize=(6.5, 5))
    sc = ax.scatter(sea, pg, c=dt, cmap="plasma", s=40 + 6 * eps,
                    edgecolor="k", linewidth=0.4)
    ax.axhline(regime.target_peak_g, ls="--", color="red", alpha=0.6,
               label=f"target peak ≤ {regime.target_peak_g:.0f} g")
    ax.set_xlabel("specific energy absorbed (J/kg)")
    ax.set_ylabel("peak |payload accel| (g)")
    ax.set_title(f"{regime.name}: printable Pareto "
                 "(marker size ∝ prestrain)")
    fig.colorbar(sc, ax=ax, label="tendon diameter (mm)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, fname), dpi=120)
    plt.close(fig)


def main():
    print(f"TPU 95A E = {TPU95A.young_MPa} MPa, "
          f"PETG E = 2000 MPa.  Sweeping printable design vars.\n")

    tendon_dias_m = np.array([1.2, 1.6, 2.0, 2.5, 3.0, 4.0, 5.0]) * 1e-3
    prestrains    = np.array([0.0, 0.02, 0.04, 0.06, 0.08])

    summary = []
    for regime in (CRUTCH, NASA_LANDER):
        # PETG strut diameter from the regime's strut_radius_m.
        strut_dia_m = 2.0 * regime.strut_radius_m

        # Sanity print: scan a representative design and report class-1.
        ref = regime_to_design(regime, tendon_dia_m=2.0e-3,
                               strut_dia_m=strut_dia_m, prestrain=0.04)
        print(f"=== {regime.name} ===")
        print(f"   strut ØPETG    = {strut_dia_m*1e3:.2f} mm")
        print(f"   strut length   = {ref.strut_length_m*1e3:.1f} mm")
        print(f"   strut-strut Δ  = {ref.strut_pair_min_distance_m*1e3:.2f} mm "
              f"({'class-1 OK' if ref.is_class_1 else 'CLASS-2 COLLISION'})")
        # Verify the printable range maps to a sensible k range.
        k_lo = tpu_cable_stiffness_Npm(MIN_PRINTABLE_TENDON_DIA_M, regime.height_m)
        k_hi = tpu_cable_stiffness_Npm(MAX_PRINTABLE_TENDON_DIA_M, regime.height_m)
        print(f"   printable k    = {k_lo:.0f} … {k_hi:.0f} N/m "
              f"(Ø {MIN_PRINTABLE_TENDON_DIA_M*1e3:.1f}–"
              f"{MAX_PRINTABLE_TENDON_DIA_M*1e3:.1f} mm at this length)")
        # Print warnings for the reference design.
        for w in ref.check():
            print(f"   WARN: {w}")

        rows = sweep_regime(regime, strut_dia_m=strut_dia_m,
                            tendon_dias_m=tendon_dias_m,
                            prestrains=prestrains)
        plot_heatmap(rows, regime, tendon_dias_m, prestrains,
                     f"regime_{regime.name}_printable_heatmap.png")
        plot_pareto(rows, regime,
                    f"regime_{regime.name}_printable_pareto.png")

        # Save full csv for the BO loop to consume later.
        arr = np.array([(r["tendon_dia_m"]*1e3, r["prestrain"]*100,
                         r["peak_g"], r["pulse_ms"], r["sea_Jpkg"],
                         int(r["class_1"])) for r in rows])
        np.savetxt(os.path.join(OUT_DIR,
                                f"regime_{regime.name}_printable.csv"),
                   arr, delimiter=",",
                   header="tendon_dia_mm,prestrain_pct,peak_g,pulse_ms,"
                          "sea_Jpkg,class_1",
                   comments="")

        # Best-by-target row for the per-regime summary.
        feasible = [r for r in rows if np.isfinite(r["peak_g"])
                    and r["class_1"]
                    and r["peak_g"] <= regime.target_peak_g]
        if feasible:
            best = max(feasible, key=lambda r: r["sea_Jpkg"])
            print(f"   best (class-1, peak ≤ target, max SEA): "
                  f"d_t={best['tendon_dia_m']*1e3:.2f} mm, "
                  f"prestrain={best['prestrain']*100:.1f}%, "
                  f"peak={best['peak_g']:.1f} g, "
                  f"SEA={best['sea_Jpkg']:.3f} J/kg")
            summary.append((regime.name, best))
        else:
            print(f"   no class-1 design meets peak target {regime.target_peak_g} g; "
                  "needs DiffPD/IPC fidelity or geometry change.")
            summary.append((regime.name, None))
        print()

    print("== Printable-sweep summary ==")
    for name, b in summary:
        if b is None:
            print(f"{name:<12}  no feasible design in this rigid-strut model")
        else:
            print(f"{name:<12}  d_t={b['tendon_dia_m']*1e3:.2f} mm, "
                  f"eps0={b['prestrain']*100:.1f}%, "
                  f"peak={b['peak_g']:.1f} g, "
                  f"SEA={b['sea_Jpkg']:.3f} J/kg")


if __name__ == "__main__":
    main()
