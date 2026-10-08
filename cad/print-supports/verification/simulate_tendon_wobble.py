#!/usr/bin/env python3
# ============================================================================
# Analytic nozzle-force wobble model for the thin TPU tendons.
#
# Why this exists
# ---------------
# The recurring PR #35 failure mode (video in PR #35 comment 5040197700) is the
# near-vertical TPU 85A tendon being pushed around by the nozzle while it
# prints: it rests on one bonded end and behaves as a clamped-free cantilever,
# so every nozzle touch / bead-drag force deflects the already-printed column
# sideways and the next layer lands offset. `fea_support_stability.py` covers
# the *PLA support* columns; this script covers the *TPU tendon itself* and
# quantifies which intervention actually fixes the wobble:
#
#   bare TPU tendon  vs  tendon-cage rings (--cage artefacts in this PR)
#   vs  uniform upscaling  vs  a PLA tendon of the same size (reference).
#
# Model: Euler-Bernoulli cantilever of the currently-printed length L with a
# lateral point force F at the print front, tip deflection F*L^3/(3*E*I).
# A cage ring at height h_r (printed in lockstep with the tendon) lets the
# tendon deflect freely by the ring clearance c, then acts as a lateral stop:
# tip deflection ~ c + F*(L-h_r)^3/(3*E*I). First-order, deliberately simple —
# the point is the *orders of magnitude* between scenarios, not mm precision
# (large-deflection and contact effects are ignored; forces scale linearly).
#
# Defaults mirror the committed cage artefacts (t3-prism-pr35-cage-report.json):
# tendon d=4.8 mm, printed span 80 mm, ring spacing 12 mm, clearance 0.8 mm
# (sim-tuned defaults; see sweep_cage_design.py / fea_tendon_wobble.py).
# Printed-material moduli: TPU 85A E~15 MPa, PLA E~2.3 GPa (same as the FEA).
#
# Requires: numpy, matplotlib.
# ============================================================================
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Categorical palette (validated: dataviz reference palette, slots 1-4)
C_BLUE, C_ORANGE, C_AQUA, C_YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"


def bending_stiffness(e_mpa: float, d_mm: float) -> float:
    """3*E*I for a solid circular section, N*mm^2."""
    i_mm4 = np.pi * d_mm**4 / 64.0
    return 3.0 * e_mpa * i_mm4


def tip_deflection(lengths: np.ndarray, force_n: float, e_mpa: float, d_mm: float,
                   ring_spacing: float | None = None,
                   ring_clearance: float = 0.8) -> np.ndarray:
    """Tip deflection (mm) at each printed length; rings (if any) print in
    lockstep, so the highest ring sits one spacing below the print front."""
    k = bending_stiffness(e_mpa, d_mm)
    free = force_n * lengths**3 / k
    if ring_spacing is None:
        return free
    n_rings = np.floor(lengths / ring_spacing)
    h_ring = n_rings * ring_spacing
    braced = ring_clearance + force_n * (lengths - h_ring) ** 3 / k
    return np.where(n_rings > 0, np.minimum(free, braced), free)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tendon_d", type=float, default=4.8, help="tendon diameter, mm")
    ap.add_argument("--span", type=float, default=80.0, help="printed tendon length, mm")
    ap.add_argument("--force", type=float, default=0.01,
                    help="lateral nozzle/bead-drag force, N (deflections scale linearly)")
    ap.add_argument("--e_tpu", type=float, default=15.0, help="printed TPU 85A modulus, MPa")
    ap.add_argument("--e_pla", type=float, default=2300.0, help="printed PLA modulus, MPa")
    ap.add_argument("--ring_spacing", type=float, default=12.0, help="cage ring spacing, mm")
    ap.add_argument("--ring_clearance", type=float, default=0.8, help="cage ring clearance, mm")
    ap.add_argument("--upscale", type=float, default=1.5, help="uniform scale factor scenario")
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).parent / "t3-prism-pr35-tendon-wobble-model.png")
    a = ap.parse_args()

    lengths = np.linspace(1.0, a.span, 400)
    f_mn = a.force * 1e3

    scenarios = [  # (label, color, deflection array at full resolution)
        (f"bare TPU Ø4.8 (current)", C_ORANGE,
         tip_deflection(lengths, a.force, a.e_tpu, a.tendon_d)),
        (f"TPU upscaled ×{a.upscale:g} (Ø{a.tendon_d*a.upscale:.1f})", C_YELLOW,
         tip_deflection(np.linspace(1.0, a.span * a.upscale, 400), a.force,
                        a.e_tpu, a.tendon_d * a.upscale)),
        (f"TPU + cage rings @ {a.ring_spacing:g} mm", C_AQUA,
         tip_deflection(lengths, a.force, a.e_tpu, a.tendon_d,
                        ring_spacing=a.ring_spacing, ring_clearance=a.ring_clearance)),
        (f"PLA Ø4.8 (reference)", C_BLUE,
         tip_deflection(lengths, a.force, a.e_pla, a.tendon_d)),
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.2), facecolor=SURFACE)
    for ax in (ax1, ax2):
        ax.set_facecolor(SURFACE)
        ax.grid(True, color="#e6e5e1", linewidth=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(INK2)
        ax.tick_params(colors=INK2)

    # Panel A: deflection vs printed length ---------------------------------
    for label, color, defl in scenarios:
        x = np.linspace(1.0, a.span * (a.upscale if "upscaled" in label else 1.0), 400)
        frac = x / x[-1]  # compare at the same fraction of the print
        ax1.plot(frac * 100, defl, color=color, linewidth=2, label=label)
        ax1.annotate(label, (100, defl[-1]), xytext=(4, 0),
                     textcoords="offset points", color=INK, fontsize=9, va="center")
    ax1.set_yscale("log")
    ax1.set_xlim(0, 100)
    ax1.set_xlabel("printed fraction of tendon (%)", color=INK)
    ax1.set_ylabel(f"lateral tip deflection under {f_mn:g} mN (mm)", color=INK)
    ax1.set_title("Wobble compliance while the tendon prints", color=INK, fontsize=11)
    ax1.margins(x=0.28)
    ax1.legend(fontsize=8, framealpha=0, labelcolor=INK)

    # Panel B: worst-case deflection during the print vs ring spacing -------
    spacings = np.linspace(5.0, a.span, 200)
    d_worst = np.array([tip_deflection(lengths, a.force, a.e_tpu, a.tendon_d,
                                       ring_spacing=s,
                                       ring_clearance=a.ring_clearance).max()
                        for s in spacings])
    ax2.plot(spacings, d_worst, color=C_AQUA, linewidth=2)
    ax2.axhline(a.ring_clearance, color=INK2, linewidth=1, linestyle="--")
    ax2.annotate(f"ring clearance floor ({a.ring_clearance:g} mm)",
                 (spacings[0], a.ring_clearance), xytext=(4, 4),
                 textcoords="offset points", color=INK2, fontsize=9)
    d_committed = tip_deflection(lengths, a.force, a.e_tpu, a.tendon_d,
                                 ring_spacing=a.ring_spacing,
                                 ring_clearance=a.ring_clearance).max()
    ax2.plot([a.ring_spacing], [d_committed], "o", color=C_ORANGE, markersize=9)
    ax2.annotate(f"committed cage ({a.ring_spacing:g} mm → {d_committed:.2f} mm)",
                 (a.ring_spacing, d_committed), xytext=(8, 6),
                 textcoords="offset points", color=INK, fontsize=9)
    ax2.set_yscale("log")
    ax2.set_xlabel("cage ring spacing (mm)", color=INK)
    ax2.set_ylabel(f"worst tip deflection during print, {f_mn:g} mN (mm)", color=INK)
    ax2.set_title("Cage ring spacing trade-off", color=INK, fontsize=11)

    fig.suptitle(
        f"TPU tendon nozzle-wobble model — Ø{a.tendon_d:g} mm × "
        f"{a.span:g} mm, E_TPU={a.e_tpu:g} MPa, F={f_mn:g} mN (linear in F)",
        color=INK, fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(a.out, dpi=140, facecolor=SURFACE)
    print(f"wrote {a.out}")

    for label, _, defl in scenarios:
        print(f"  {label:38s} full-height deflection {defl[-1]:8.3f} mm "
              f"({defl[-1]/a.force:8.1f} mm/N compliance)")


if __name__ == "__main__":
    main()
