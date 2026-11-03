"""Teaching figures for the drop-tower metrics primer (PR #97, issue #94).

Generates three ILLUSTRATIVE figures for the lesson posted on PR #97, in a
deliberately barebones style (requested in PR #97 review): one plain-sentence
headline, one simple plot, at most two trace colors, and the key number or
equation set large beside the plot.

All signals are synthetic, parameterized with representative values from
docs/drop-test-abc123-blind-analysis.md (tau ~ 2 ms, f_n ~ 520 Hz,
zeta ~ 0.07, t_second ~ 25 ms, dv ~ 5.5 m/s). They are cartoons of the
physics, not measured data, and feed no analysis.

Usage: python scripts/teaching/make_drop_tower_primer_figures.py
Writes PNGs to docs/figures/.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[2] / "docs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# Two trace colors only (blue = base sensor, orange = top-vertex sensor),
# CVD-validated against a white surface.
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

# Representative parameters (see docstring)
TAU = 2.4e-3  # base-pulse FWHM, s
PEAK_G = 300.0  # base-pulse peak, G
FN = 520.0  # ringdown frequency, Hz
ZETA = 0.07  # ringdown damping ratio
T_SECOND = 25e-3  # vertex second impact, s


def headline(fig, text):
    """Plain-sentence title, top left, like a slide message title."""
    fig.text(0.045, 0.97, text, fontsize=17, color=INK, ha="left", va="top",
             linespacing=1.4)


def half_sine(t, peak, tau_fwhm):
    """Half-sine pulse whose FWHM equals tau_fwhm (duration = 1.5 * FWHM)."""
    dur = 1.5 * tau_fwhm
    p = np.where((t >= 0) & (t <= dur), peak * np.sin(np.pi * t / dur), 0.0)
    return p, dur


def top_vertex_trace(t, ride_peak=PEAK_G * 1.01, ride_delay=0.0):
    """Cartoon top-vertex record: ride, ringdown, quiet flight, hop landing."""
    ride, dur = half_sine(t - ride_delay, ride_peak, TAU)
    dur += ride_delay
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


def fig1_anatomy():
    t = np.linspace(-2e-3, 40e-3, 8000)
    base, _ = half_sine(t, PEAK_G, TAU)
    # slight lag and overshoot on the ride so both traces stay visible;
    # the peak ratio is still ~1
    top = top_vertex_trace(t, ride_peak=PEAK_G * 1.12, ride_delay=0.45e-3)
    ms = t * 1e3

    fig = plt.figure(figsize=(11.2, 5.6))
    headline(fig, "One drop record is three events: ride the pulse, ring down,\n"
                  "then the top vertex hops and lands back  (illustrative)")
    ax = fig.add_axes([0.07, 0.13, 0.89, 0.62])

    ax.plot(ms, base, color=BLUE, label="bottom sensor (plate)")
    ax.plot(ms, top, color=ORANGE, label="top-vertex sensor")
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.legend(frameon=False, loc="upper right")

    ax.annotate(
        "impact pulse: its area is the\narrival speed, $\\Delta v \\approx 5.5$ m/s",
        xy=(1.0, 170), xytext=(4.5, 260), color=BLUE,
        arrowprops=dict(arrowstyle="-", color=BLUE, lw=1),
    )
    ax.annotate(
        "ringdown: gives $f_n$ and $\\zeta$",
        xy=(5.6, -85), xytext=(8.5, -230), color=ORANGE,
        arrowprops=dict(arrowstyle="-", color=ORANGE, lw=1),
    )
    ax.annotate(
        "the vertex lands back:\ngives $t_{second}$",
        xy=(25.6, 58), xytext=(28.5, 170), color=ORANGE,
        arrowprops=dict(arrowstyle="-", color=ORANGE, lw=1),
    )

    ax.set_xlim(-2, 40)
    ax.set_ylim(-300, 390)
    ax.set_xlabel("time after impact (ms)")
    ax.set_ylabel("acceleration (G)")
    fig.savefig(OUT / "primer_fig1_drop_anatomy.png", dpi=160)
    plt.close(fig)


def fig2_damping():
    fs = 200_000
    t = np.arange(0, 12e-3, 1 / fs)
    wn = 2 * np.pi * FN
    wd = wn * np.sqrt(1 - ZETA**2)
    x = np.exp(-ZETA * wn * t) * np.cos(wd * t)
    env = np.exp(-ZETA * wn * t)
    ms = t * 1e3

    fig = plt.figure(figsize=(11.2, 5.4))
    headline(fig, "How fast the ringdown fades is the damping ratio $\\zeta$")
    ax = fig.add_axes([0.09, 0.14, 0.50, 0.68])

    ax.plot(ms, x, color=ORANGE, lw=1.4)
    ax.plot(ms, env, color=BLUE, lw=2.2)
    ax.axhline(0, color=MUTED, lw=0.8)

    ax.annotate(
        "ringdown at $f_n \\approx$ 520 Hz",
        xy=(1.55, -0.48), xytext=(3.4, -0.75), color=ORANGE,
        arrowprops=dict(arrowstyle="-", color=ORANGE, lw=1),
    )
    ax.annotate(
        "envelope $e^{-\\zeta\\omega_n t}$",
        xy=(2.7, env[int(2.7e-3 * fs)]), xytext=(4.6, 0.55), color=BLUE,
        arrowprops=dict(arrowstyle="-", color=BLUE, lw=1),
    )

    ax.set_xlim(0, 12)
    ax.set_ylim(-1.05, 1.1)
    ax.set_xlabel("time after impact (ms)")
    ax.set_ylabel("normalized amplitude")

    fig.text(0.79, 0.62, "$\\zeta \\approx 0.07$", fontsize=26, color=BLUE,
             ha="center")
    fig.text(0.79, 0.44,
             "energy lost per cycle\n$\\approx 4\\pi\\zeta \\approx$ 58%",
             fontsize=16, color=INK, ha="center", linespacing=1.6)
    fig.text(0.79, 0.24,
             "which is why our usable\nringdowns last only 5 to 13 ms",
             fontsize=11, color=MUTED, ha="center", linespacing=1.5)
    fig.savefig(OUT / "primer_fig2_damping.png", dpi=160)
    plt.close(fig)


def srs_half_sine(f_over_tau, Q=10.0):
    """Maximax SRS of a unit half-sine (duration D), x-axis f_n * D.

    Direct time integration of an SDOF base-excitation oscillator.
    """
    zeta = 1 / (2 * Q)
    D = 1.0  # normalize: pulse duration 1 s, sweep fn = ratio / D
    out = []
    for r in f_over_tau:
        fn = r / D
        wn = 2 * np.pi * fn
        dt = min(D, 1 / fn) / 400
        # residual-phase peak occurs within the first free cycle after the pulse
        t_end = D + 1.5 / fn
        n = int(t_end / dt)
        tt = np.arange(n) * dt
        base = np.where(tt <= D, np.sin(np.pi * tt / D), 0.0)
        # state = [rel disp, rel vel]; semi-implicit Euler is fine at dt<<T
        z = zv = 0.0
        amax = 0.0
        for a_b in base:
            zacc = -2 * zeta * wn * zv - wn**2 * z - a_b
            zv += zacc * dt
            z += zv * dt
            aa = abs(-2 * zeta * wn * zv - wn**2 * z)  # absolute accel
            if aa > amax:
                amax = aa
        out.append(amax)
    return np.array(out)


def fig3_srs():
    # x-axis in f_n * tau(FWHM); for a half-sine, duration D = 1.5 * FWHM
    ftau = np.geomspace(0.03, 7, 90)
    srs = srs_half_sine(1.5 * ftau)

    fig = plt.figure(figsize=(11.2, 5.6))
    headline(fig, "How hard a structure is shaken depends on its frequency\n"
                  "compared to the pulse: soft is isolated, stiff just rides along")
    ax = fig.add_axes([0.07, 0.13, 0.89, 0.60])

    ax.plot(ftau, srs, color=BLUE)
    ax.set_xscale("log")
    ax.set_ylim(0, 1.95)
    ax.axhline(1.0, color=MUTED, lw=0.9, ls="--")
    ax.text(0.032, 1.04, "response = input", color=MUTED, fontsize=10)

    ax.axvspan(0.9, 1.7, color=ORANGE, alpha=0.14, lw=0)
    ax.text(1.23, 1.62, "our specimens\n$f_n\\tau \\approx$ 0.9 to 1.7",
            color=ORANGE, ha="center", linespacing=1.5)

    ax.text(0.045, 0.32, "isolated:\ntoo soft to\nfollow the pulse",
            color=INK, linespacing=1.5)
    ax.text(0.30, 1.78, "amplified", color=INK)
    ax.text(3.1, 0.72, "rides the pulse", color=INK)

    ax.set_xlabel("structure frequency $\\times$ pulse width  ($f_n\\tau$, dimensionless)")
    ax.set_ylabel("peak response $\\div$ peak input")
    fig.savefig(OUT / "primer_fig3_srs.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    fig1_anatomy()
    fig2_damping()
    fig3_srs()
    print("wrote figures to", OUT)
