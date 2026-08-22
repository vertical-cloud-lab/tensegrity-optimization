"""Teaching figure for the rebound-energy objective of PR #102.

One three-panel figure showing the full chain from raw record to BO
objective:

  panel A: the top-vertex record and the hop delay t_second (illustrative
           cartoon in the style of primer_fig1);
  panel B: the ballistic conversion, v_sep = g*t_second/2 and
           e_rebound = v_sep/dv (Bernstein 1977 bounce-timing method);
  panel C: the PR #102 objective e_reb_mJ = e_rebound * m * g * h for the
           real T-3_01 Sobol batch (measured values, see PANEL_C_DATA).

Panels A and B are cartoons of the physics, parameterized with
representative campaign values; they are not measured data. Panel C uses
the measured campaign snapshot: bo/t3-prism-bo-batch-drop-results.csv on
branch claude/issue-98-20260821-0103 (PR #102), itself a copy of
campaign_summary.csv from PR #86 commit 642b8c0. amdjwm is omitted, as in
the BO script, because it has no spec mapping and no recorded mass.

Usage: python scripts/teaching/make_rebound_energy_figure.py
Writes docs/figures/primer_fig4_rebound_energy.png.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[2] / "docs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# Reference palette (validated light-mode values, same as the primer figures)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "sans-serif",
        "font.size": 10,
        "text.color": INK,
        "axes.edgecolor": BASELINE,
        "axes.labelcolor": INK2,
        "axes.titlecolor": INK,
        "axes.titlesize": 10.5,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "lines.linewidth": 1.8,
    }
)

G = 9.80665  # m/s^2, the value the BO script uses
DROP_H_M = 60 * 0.0254  # 1.524 m
DV = 5.33  # m/s, typical measured arrest velocity for the batch
T_SECOND = 29e-3  # s, representative hop delay (batch range 22 to 55 ms)
FN = 520.0  # Hz, ringdown mode for the cartoon
ZETA = 0.07
TAU = 1.6e-3  # s, base-pulse FWHM for the cartoon

# Measured campaign snapshot for panel C (see module docstring for the
# provenance): specimen, Sobol spec, e_rebound mean, printed mass in grams.
PANEL_C_DATA = [
    ("6lhxfy", "01", 0.0504, 18.50),
    ("6nheas", "05", 0.0402, 21.73),
    ("9hhbkp", "00", 0.0215, 21.62),
    ("autv5r", "02", 0.0268, 22.04),
    ("bag26v", "08", 0.0241, 21.42),
    ("bpx68c", "S0", 0.0204, 20.23),
    ("nvxsrv", "04", 0.0266, 20.66),
]


def half_sine(t, peak, tau_fwhm):
    """Half-sine pulse whose FWHM equals tau_fwhm (duration = 1.5 * FWHM)."""
    dur = 1.5 * tau_fwhm
    p = np.where((t >= 0) & (t <= dur), peak * np.sin(np.pi * t / dur), 0.0)
    return p, dur


def panel_a(ax):
    """Top-vertex record cartoon: impact, ringdown, quiet flight, hop landing."""
    t = np.linspace(-2e-3, 40e-3, 8000)
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
    ms = t * 1e3
    ax.plot(ms, ride + ring + land + ring2, color=ORANGE, lw=1.4)
    ax.axhline(0, color=BASELINE, lw=0.8)

    ax.annotate(
        "impact:\nride + ringdown",
        xy=(1.8, 240), xytext=(6.5, 280), color=INK2,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1),
    )
    ax.annotate(
        "vertex lands back\n(largest envelope burst\nin the 15 to 70 ms tail)",
        xy=(T_SECOND * 1e3 + 0.6, 58), xytext=(24.5, 190), color=INK2,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1),
    )
    ax.annotate(
        "", xy=(0.0, -180), xytext=(T_SECOND * 1e3, -180),
        arrowprops=dict(arrowstyle="<->", color=INK2, lw=1.1),
    )
    ax.text(T_SECOND * 1e3 / 2, -255, "t_second (the hop flight time)",
            color=INK2, ha="center")
    ax.set_xlim(-2, 40)
    ax.set_ylim(-310, 360)
    ax.set_xlabel("time after impact (ms)")
    ax.set_ylabel("top-vertex accel (G)")
    ax.set_title("A. Measure one time: t_second")


def panel_b(ax):
    """Ballistic flight of the hop: t_second gives v_sep, then e_rebound."""
    v_sep = G * T_SECOND / 2.0
    t = np.linspace(0, T_SECOND, 300)
    h_mm = (v_sep * t - 0.5 * G * t**2) * 1e3
    ms = t * 1e3
    ax.plot(ms, h_mm, color=AQUA, lw=2.2)
    ax.fill_between(ms, h_mm, 0, color=AQUA, alpha=0.12)
    ax.axhline(0, color=BASELINE, lw=0.8)

    apex = v_sep**2 / (2 * G) * 1e3
    ax.annotate(
        f"apex = v_sep²/2g ≈ {apex:.1f} mm\n(the hop is tiny; only its\ntiming is measured)",
        xy=(T_SECOND * 5e2, apex), xytext=(2.2, 0.62), color=INK2,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1),
    )
    ax.text(
        0.97, 0.97,
        "flight time under gravity alone:\n"
        f"v_sep = g·t_second/2 ≈ {v_sep:.2f} m/s\n\n"
        f"e_rebound = v_sep/Δv ≈ {v_sep / DV:.3f}\n"
        "(a velocity ratio: the restitution\ncoefficient of the vertex hop)",
        color=INK, transform=ax.transAxes, ha="right", va="top",
        bbox=dict(boxstyle="round,pad=0.45", fc=SURFACE, ec=GRID),
    )
    ax.set_xlim(0, T_SECOND * 1e3 * 1.05)
    ax.set_ylim(0, apex * 1.55)
    ax.set_xlabel("time after impact (ms)")
    ax.set_ylabel("vertex height above seat (mm)")
    ax.set_title("B. Ballistics turns it into a speed")


def panel_c(ax):
    """The PR #102 objective on the real batch, sorted, direct-labeled."""
    rows = sorted(
        PANEL_C_DATA,
        key=lambda r: r[2] * r[3] * G * DROP_H_M,
    )
    names = [
        f"{spec_id}  (spec {spec})\ne = {e:.3f} · {m:.1f} g"
        for spec_id, spec, e, m in rows
    ]
    mj = [e * m * G * DROP_H_M for _, _, e, m in rows]
    y = np.arange(len(rows))
    ax.barh(y, mj, height=0.62, color=BLUE, edgecolor=SURFACE, linewidth=2)
    for yi, v in enumerate(mj):
        ax.text(v + 0.25, yi, f"{v:.1f} mJ", color=INK2, va="center",
                fontsize=9)
    ax.set_yticks(y, names, fontsize=8.5)
    ax.set_xlim(0, 16.5)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("e_reb_mJ = e_rebound · m · g · h  (mJ per drop)")
    ax.set_title("C. Weight by impact energy: the BO objective")
    ax.text(
        0.62, 0.01,
        "grams are re-penalized:\n6nheas nearly matches\n6lhxfy in mJ despite a\n20% lower e_rebound,\nbecause it is 3.2 g heavier",
        color=INK2, transform=ax.transAxes, fontsize=8.5, va="bottom",
    )


def main():
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.3), layout="constrained")
    panel_a(axes[0])
    panel_b(axes[1])
    panel_c(axes[2])
    fig.suptitle(
        "Rebound energy, PR #102 objective 2 (minimized): one measured time, "
        "two conversions. Panels A and B illustrative; panel C measured.",
        fontsize=11,
    )
    fig.savefig(OUT / "primer_fig4_rebound_energy.png", dpi=160)
    plt.close(fig)
    print("wrote", OUT / "primer_fig4_rebound_energy.png")


if __name__ == "__main__":
    main()
