"""Teaching figures for the drop-tower metrics primer (PR #97, issue #94).

Generates three ILLUSTRATIVE figures for the lesson posted on PR #97.
All signals are synthetic, parameterized with representative values from
docs/drop-test-abc123-blind-analysis.md (tau ~ 2.4 ms, f_n ~ 520 Hz,
zeta ~ 0.06-0.11, t_second ~ 25 ms, dv ~ 5.47 m/s). They are cartoons of
the physics, not measured data, and feed no analysis.

Usage: python scripts/teaching/make_drop_tower_primer_figures.py
Writes PNGs to docs/figures/.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[2] / "docs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# Reference palette (validated light-mode values)
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
        "axes.titlesize": 11,
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

# Representative parameters (see docstring)
TAU = 2.4e-3  # base-pulse FWHM, s
PEAK_G = 300.0  # base-pulse peak, G
FN = 520.0  # ringdown frequency, Hz
ZETA = 0.07  # ringdown damping ratio
T_SECOND = 25e-3  # vertex second impact, s
G = 9.81


def half_sine(t, peak, tau_fwhm):
    """Half-sine pulse whose FWHM equals tau_fwhm (duration = 1.5 * FWHM)."""
    dur = 1.5 * tau_fwhm
    p = np.where((t >= 0) & (t <= dur), peak * np.sin(np.pi * t / dur), 0.0)
    return p, dur


def fig1_anatomy():
    t = np.linspace(-2e-3, 40e-3, 8000)
    base, dur = half_sine(t, PEAK_G, TAU)

    wn = 2 * np.pi * FN
    wd = wn * np.sqrt(1 - ZETA**2)
    ring = np.where(
        t > dur,
        -90 * np.exp(-ZETA * wn * (t - dur)) * np.sin(wd * (t - dur)),
        0.0,
    )
    ride, _ = half_sine(t, PEAK_G * 1.01, TAU)
    land, _ = half_sine(t - T_SECOND, 60, 0.8e-3)
    ring2 = np.where(
        t > T_SECOND + 1.2e-3,
        -35 * np.exp(-ZETA * wn * (t - T_SECOND - 1.2e-3)) * np.sin(wd * (t - T_SECOND - 1.2e-3)),
        0.0,
    )
    out = ride + ring + land + ring2

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8.6, 5.6), layout="constrained")
    ms = t * 1e3

    ax1.plot(ms, base, color=BLUE)
    ax1.set_ylabel("accel (G)")
    ax1.set_title("Anatomy of one drop record (illustrative, not measured data)")
    ax1.text(0.7, 315, "base input, CH5", color=INK2)
    ax1.annotate(
        "", xy=(0.6, 150), xytext=(3.0, 150), arrowprops=dict(arrowstyle="<->", color=INK2, lw=1)
    )
    ax1.text(3.4, 140, f"pulse width τ (FWHM) ≈ {TAU*1e3:.1f} ms", color=INK2)
    ax1.fill_between(ms, base, 0, where=base > 0, color=BLUE, alpha=0.12)
    ax1.text(4.2, 60, "shaded area = Δv ≈ 5.5 m/s\n(the arrest velocity — rig-health gauge)", color=INK2)

    ax2.plot(ms, out, color=ORANGE)
    ax2.set_ylabel("accel (G)")
    ax2.set_xlabel("time after impact (ms)")
    ax2.text(0.4, 330, "top-vertex output, CH2–CH4", color=INK2)
    ax2.annotate(
        "1. rides the pulse\n    (peak ratio T ≈ 1)",
        xy=(2.4, 250), xytext=(8.5, 265), color=INK2,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1),
    )
    ax2.annotate(
        "2. free ringdown: f_n ≈ 520 Hz,\n    envelope decay → ζ",
        xy=(7.5, -60), xytext=(9.5, -260), color=INK2,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1),
    )
    ax2.annotate(
        "3. vertex lands back:\n    t_second → e_rebound",
        xy=(T_SECOND * 1e3 + 0.5, 55), xytext=(29, 200), color=INK2,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1),
    )
    for ax in (ax1, ax2):
        ax.axhline(0, color=BASELINE, lw=0.8)
        ax.set_xlim(-2, 40)

    fig.savefig(OUT / "primer_fig1_drop_anatomy.png", dpi=160)
    plt.close(fig)


def fig2_damping():
    fs = 200_000
    t = np.arange(0, 14e-3, 1 / fs)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.9), layout="constrained")

    cases = [(0.06, BLUE, "ζ = 0.06  (Q ≈ 8)"), (0.11, ORANGE, "ζ = 0.11  (Q ≈ 4.5)")]
    wn = 2 * np.pi * FN
    for zeta, color, label in cases:
        wd = wn * np.sqrt(1 - zeta**2)
        x = np.exp(-zeta * wn * t) * np.cos(wd * t)
        env = np.exp(-zeta * wn * t)  # analytic envelope (= Hilbert env., no edge artifacts)
        ax1.plot(t * 1e3, x, color=color, lw=1.2, alpha=0.8)
        ax1.plot(t * 1e3, env, color=color, lw=2.0)
        ax2.semilogy(t * 1e3, env, color=color, lw=2.0, label=label)

    ax1.set_title("Ringdown + decay envelope")
    ax1.set_xlabel("time (ms)")
    ax1.set_ylabel("normalized amplitude")
    ax1.text(4.6, 0.62, "envelope = e^(−ζωₙt)\n(pipeline extracts it via\nthe Hilbert transform)", color=INK2)

    ax2.set_title("Same envelopes, log scale → straight lines")
    ax2.set_xlabel("time (ms)")
    ax2.set_ylabel("envelope (log)")
    ax2.text(1.2, 0.022, "slope = −ζωₙ\n(the fit reads ζ off this line;\nr² < 0.85 ⇒ not one clean mode)", color=INK2)
    ax2.legend(frameon=False, loc="upper right", labelcolor=INK2)
    ax2.set_ylim(1e-3, 1.5)

    fig.suptitle("Why ζ is an energy metric: ΔE/E per cycle ≈ 4πζ  (ζ=0.07 → ~60% of vibrational energy gone each cycle)", fontsize=10.5)
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

    fig, ax = plt.subplots(figsize=(8.2, 4.4), layout="constrained")
    ax.plot(ftau, srs, color=BLUE)
    ax.set_xscale("log")
    ax.set_ylim(0, 1.95)
    ax.axhline(1.0, color=BASELINE, lw=0.9, ls="--")
    ax.axvspan(0.9, 1.7, color=AQUA, alpha=0.15)

    ax.text(0.035, 0.08, "isolation:\nstructure too soft\nto follow the pulse", color=INK2)
    ax.annotate(
        "dynamic amplification peak",
        xy=(0.55, 1.66), xytext=(0.06, 1.55), color=INK2,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1),
    )
    ax.text(2.2, 0.72, "quasi-static: rides the pulse,\nresponse ≈ input", color=INK2)
    ax.text(0.95, 0.25, "our specimens\n(f·τ ≈ 0.9–1.7)", color="#0e7a53")

    ax.set_xlabel("f_n × τ (pulse FWHM)  — dimensionless")
    ax.set_ylabel("peak response ÷ peak input")
    ax.set_title("Shock response spectrum of a half-sine pulse (Q = 10) — where our specimens sit")
    fig.savefig(OUT / "primer_fig3_srs.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    fig1_anatomy()
    fig2_damping()
    fig3_srs()
    print("wrote figures to", OUT)
