"""Teaching figure for the rebound-energy objective of PR #102.

One barebones figure (style requested in PR #97 review): the top-vertex
record with the hop delay t_second marked, and the two-step conversion to
the BO objective set large beside the plot, worked with real numbers from
one article of the T-3_01 Sobol batch.

The trace is an illustrative cartoon parameterized with representative
campaign values; it is not measured data. The worked numbers are the
measured campaign snapshot for article bag26v (spec 08):
t_second = 24.72 ms, dv = 5.030 m/s, printed mass 21.42 g, from
bo/t3-prism-bo-batch-drop-results.csv on branch claude/issue-98-20260821-0103
(PR #102), itself a copy of campaign_summary.csv from PR #86 commit 642b8c0.

Usage: python scripts/teaching/make_rebound_energy_figure.py
Writes docs/figures/primer_fig4_rebound_energy.png.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

OUT = Path(__file__).resolve().parents[2] / "docs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# Two trace colors only, CVD-validated against a white surface.
BLUE = "#2678d3"
ORANGE = "#e8702a"
INK = "#111111"
MUTED = "#7a7a7a"
GRID = "#e6e6e6"
SPINE = "#bfbfbf"

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "font.family": "sans-serif",
        "font.size": 12,
        "text.color": INK,
        "axes.edgecolor": SPINE,
        "axes.labelcolor": INK,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "lines.linewidth": 2.0,
    }
)

G = 9.80665  # m/s^2, the value the BO script uses
DROP_H_M = 60 * 0.0254  # 1.524 m
# Measured values for article bag26v (see module docstring for provenance)
T_SECOND = 24.72e-3  # s
DV = 5.030  # m/s
MASS_G = 21.42  # g
# Cartoon-only parameters
FN = 520.0
ZETA = 0.07
TAU = 1.6e-3


def half_sine(t, peak, tau_fwhm):
    """Half-sine pulse whose FWHM equals tau_fwhm (duration = 1.5 * FWHM)."""
    dur = 1.5 * tau_fwhm
    p = np.where((t >= 0) & (t <= dur), peak * np.sin(np.pi * t / dur), 0.0)
    return p, dur


def top_vertex_trace(t):
    """Cartoon top-vertex record: ride, ringdown, quiet flight, hop landing."""
    ride, dur = half_sine(t, 300, TAU)
    wn = 2 * np.pi * FN
    wd = wn * np.sqrt(1 - ZETA**2)
    ring = np.where(
        t > dur,
        -90 * np.exp(-ZETA * wn * (t - dur)) * np.sin(wd * (t - dur)),
        0.0,
    )
    land, _ = half_sine(t - T_SECOND, 60, 0.8e-3)
    ring2 = np.where(
        t > T_SECOND + 1.2e-3,
        -35
        * np.exp(-ZETA * wn * (t - T_SECOND - 1.2e-3))
        * np.sin(wd * (t - T_SECOND - 1.2e-3)),
        0.0,
    )
    return ride + ring + land + ring2


def main():
    v_sep = G * T_SECOND / 2.0
    e_reb = v_sep / DV
    e_reb_mj = e_reb * (MASS_G / 1e3) * G * DROP_H_M * 1e3

    t = np.linspace(-2e-3, 40e-3, 8000)
    ms = t * 1e3

    fig = plt.figure(figsize=(11.2, 5.6))
    fig.text(0.045, 0.97,
             "We time the hop of the top vertex, turn it into a speed,\n"
             "then weight it by the print's mass  (trace illustrative)",
             fontsize=17, color=INK, ha="left", va="top", linespacing=1.4)
    ax = fig.add_axes([0.07, 0.13, 0.50, 0.62])

    ax.plot(ms, top_vertex_trace(t), color=ORANGE, lw=1.6)
    ax.axhline(0, color=MUTED, lw=0.8)

    ax.annotate(
        "the vertex\nlands back",
        xy=(25.4, 58), xytext=(29, 180), color=ORANGE,
        arrowprops=dict(arrowstyle="-", color=ORANGE, lw=1),
    )
    ax.annotate(
        "", xy=(0.0, -190), xytext=(T_SECOND * 1e3, -190),
        arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=1.4),
    )
    ax.text(T_SECOND * 1e3 / 2, -262,
            "$t_{second}$ = 24.7 ms  (the hop flight time)",
            color=ORANGE, ha="center")

    ax.set_xlim(-2, 40)
    ax.set_ylim(-310, 380)
    ax.set_xlabel("time after impact (ms)")
    ax.set_ylabel("top-vertex acceleration (G)")

    # Right side: the two-step conversion, fraction drawn by hand so the
    # measured terms can carry the trace colors.
    xc = 0.695
    fig.text(xc, 0.615, "$g \\cdot t_{second}\\,/\\,2$", fontsize=20,
             color=ORANGE, ha="center", va="bottom")
    fig.add_artist(Line2D([xc - 0.085, xc + 0.085], [0.595, 0.595],
                          transform=fig.transFigure, color=INK, lw=1.4))
    fig.text(xc, 0.575, "$\\Delta v$", fontsize=20, color=BLUE,
             ha="center", va="top")
    fig.text(xc + 0.10, 0.578, f"$=\\ e_{{rebound}} \\approx {e_reb:.3f}$",
             fontsize=17, color=INK, ha="left", va="center")

    fig.text(xc + 0.065, 0.40,
             "$e_{rebound} \\cdot m g h \\ \\approx$ "
             f"$\\mathbf{{{e_reb_mj:.1f}\\ mJ}}$",
             fontsize=19, color=INK, ha="center", va="center")
    fig.text(xc + 0.065, 0.30,
             "the BO objective, minimized",
             fontsize=12, color=INK, ha="center")

    fig.text(xc + 0.065, 0.175,
             f"worked for article bag26v: $\\Delta v$ = {DV:.2f} m/s\n"
             f"from the bottom sensor, m = {MASS_G:.1f} g weighed,\n"
             "h = 60 in drop height",
             fontsize=10.5, color=MUTED, ha="center", linespacing=1.6)

    fig.savefig(OUT / "primer_fig4_rebound_energy.png", dpi=160)
    plt.close(fig)
    print("wrote", OUT / "primer_fig4_rebound_energy.png")


if __name__ == "__main__":
    main()
