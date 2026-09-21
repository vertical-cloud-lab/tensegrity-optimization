"""Velocity-timeline schematic for the e_rebound bookkeeping (issue #94).

Answers the question "does the code account for the top accelerometer's
fall, stop, and rebound back up?" by drawing the vertical velocity of the
top-vertex assembly through the three phases of one drop and color-coding
where each number comes from:

* the fall: recorded by neither sensor; the drop height sets the arrival
  speed, and the measured arrest Delta-v is the cross-check
* the arrest: bottom sensor (CH5), Delta-v = integral of a dt, the
  denominator of e_rebound
* the hop: top sensor supplies two timestamps only (impact burst, landing
  burst); the velocity between them is the ballistic model g*t_second/2

Numbers annotated from round-2 article bag26v (Delta-v 5.03 m/s,
t_second 24.7 ms, e_rebound 0.024), the same drop used by
docs/figures/primer_fig4_rebound_energy.png. The traces are illustrative;
the annotated numbers are the measured ones.

Usage (repo root): python scripts/figures/rebound_bookkeeping_figure.py
Writes docs/figures/rebound_bookkeeping_timeline.png. Needs matplotlib.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# palette (dataviz reference, validated 2-slot light mode; matches the
# idetc teaching figures: blue = bottom sensor, orange = top sensor)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
GRAY = "#b9b7b0"
GRID = "#e6e4de"

G = 9.80665
H_M = 60 * 0.0254            # 1.524 m drop height
V_FF = np.sqrt(2 * G * H_M)  # 5.468 m/s free-fall arrival speed
DV = 5.03                    # measured arrest Delta-v for bag26v (m/s)
T_SECOND_S = 0.0247          # measured hop flight time for bag26v
V_SEP = G * T_SECOND_S / 2   # 0.121 m/s ballistic separation speed
E_REB = V_SEP / DV           # 0.024
APEX_MM = V_SEP**2 / (2 * G) * 1e3   # 0.75 mm
ARREST_MS = 2.5              # illustrative arrest duration

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "font.size": 11.5,
})

fig, axes = plt.subplots(
    1, 3, figsize=(13.2, 4.9), gridspec_kw={"width_ratios": [1.05, 1.0, 1.55]}
)
fig.subplots_adjust(left=0.055, right=0.985, top=0.76, bottom=0.13, wspace=0.30)

fig.suptitle(
    "Where each number in $e_{rebound}$ comes from: "
    "the fall is inferred, the stop is integrated, the hop is timed",
    fontsize=15.5, x=0.055, ha="left", y=0.97, fontweight="bold",
)
fig.text(
    0.055, 0.865,
    "vertical velocity of the top-vertex assembly (up = positive); annotated numbers "
    "are measured values from round-2 article bag26v, traces illustrative",
    fontsize=11, color=INK2,
)

# phase 1: the fall (neither sensor is read; height sets the arrival speed)
ax = axes[0]
t = np.linspace(0, 0.557, 200)
ax.plot(t * 1e3, -G * t, color=GRAY, lw=2.6, dashes=(4, 2))
ax.set_title("1. the fall (557 ms)", color=INK, fontsize=12.5, pad=6)
ax.set_xlabel("time from release (ms)")
ax.set_ylabel("velocity (m/s)")
ax.set_ylim(-6.1, 0.55)
ax.text(
    20, -4.35,
    "recorded by neither sensor:\nboth ride the plate down.\n"
    "h = 60 in sets the arrival\nspeed $\\sqrt{2gh}$ = 5.47 m/s",
    color=INK2, fontsize=10.5, va="top",
)

# phase 2: the arrest (bottom sensor CH5, the Delta-v integral)
ax = axes[1]
t = np.linspace(0, ARREST_MS, 200)
v = -DV / 2 * (1 + np.cos(np.pi * t / ARREST_MS))
ax.plot(t, v, color=BLUE, lw=2.6)
ax.plot([-0.6, 0], [-DV, -DV], color=GRAY, lw=2.6, dashes=(4, 2))
ax.plot([ARREST_MS, 4.0], [0, 0], color=BLUE, lw=2.6)
ax.set_title("2. the arrest (2 to 3 ms)", color=INK, fontsize=12.5, pad=6)
ax.set_xlabel("time from impact (ms)")
ax.set_ylim(-6.1, 0.55)
ax.set_xlim(-0.6, 4.0)
ax.text(
    1.55, -2.15, "bottom sensor (CH5):\n$\\Delta v = \\int a\\,dt$ = 5.03 m/s\n"
    "the denominator; also\na rig check: 92% of\nfree fall",
    color=BLUE, fontsize=10.5, va="top", fontweight="bold",
)
ax.text(
    0.2, -5.35, "everything still moves together",
    color=INK2, fontsize=10, va="top",
)

# phase 3: the hop (top sensor timestamps; ballistics in between)
ax = axes[2]
ts_ms = T_SECOND_S * 1e3
ax.axvline(0, color=ORANGE, lw=2.6)
ax.text(0.55, 0.148, "impact burst,\nassumed takeoff", color=ORANGE,
        fontsize=10, va="top", fontweight="bold")
ax.axvline(ts_ms, color=ORANGE, lw=2.6)
ax.text(ts_ms - 0.55, 0.148, "second burst:\nvertex lands back",
        color=ORANGE, fontsize=10, va="top", ha="right", fontweight="bold")
t = np.linspace(0, ts_ms, 100)
ax.plot(t, V_SEP - G * t * 1e-3, color=ORANGE, lw=2.2, dashes=(4, 2))
ax.plot(ts_ms / 2, 0.0, "o", ms=8, color=ORANGE)
ax.axhline(0, color=INK2, lw=0.8)
ax.set_title("3. the hop (24.7 ms), y zoomed 40x", color=INK, fontsize=12.5, pad=6)
ax.set_xlabel("time from impact (ms)")
ax.set_ylim(-0.185, 0.16)
ax.set_xlim(-1.2, 33.5)
ax.text(12.9, 0.022, "apex, 0.75 mm\nabove the seat", color=INK2, fontsize=10.5)
ax.text(
    1.4, -0.085,
    "solid: measured, two timestamps\nonly; no velocity is read here\n"
    "dashed: modeled at slope $-g$, so\n$v_{sep} = g\\,t_{second}/2$ = 0.12 m/s",
    color=INK2, fontsize=10, va="top",
)
ax.text(
    1.4, -0.183,
    "$e_{rebound} = v_{sep}/\\Delta v$ = 0.024",
    color=INK, fontsize=12, va="bottom", fontweight="bold",
)

for ax in axes:
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

out = Path(__file__).resolve().parents[2] / "docs" / "figures"
out.mkdir(parents=True, exist_ok=True)
fig.savefig(out / "rebound_bookkeeping_timeline.png", dpi=150)
print("wrote", out / "rebound_bookkeeping_timeline.png")
