"""Ballistic-model derivation figure for the e_rebound hop clock (issue #94).

Answers me-madsen's 09-21 question: in the five-phase sketch (1 impact
arrest, 2 rising, 3 stopped at the top, 4 falling, 5 final arrest), is the
time in the ballistic model measured from t1 to t5? Yes. The figure maps
the sketch onto the model and onto what the top sensor actually records:

* panel 1: height of the vertex above its seat, the sketch formalized,
  with the five phases placed on the flight parabola; t_second spans
  phase 1 to phase 5, and the apex (phase 3) is assumed at the midpoint
* panel 2: the vertical velocity, a straight line at slope -g, which is
  the whole model; the fall-leg kinematics v_return = g (t5 - t3) plus
  the up/down symmetry t5 - t3 = t_second / 2 give
  v_sep = g t_second / 2 and e_rebound = v_sep / Delta v
* panel 3: the top-vertex envelope through the same interval. Only the
  two bursts are observable; between them the vertex is in free flight
  and the sensor reads its noise floor, which is why the measurement is
  a clock reading and not an integrated velocity.

Numbers are measured values for round-2 article bag26v, drop Signal 33
(Delta v 5.029 m/s, t_second 24.66 ms, e_rebound 0.0240, decay sigma
185.9 1/s, ring amplitude intercept 56.6 G, landing burst +0.99 dB
relative to the impact envelope peak), copied from the per-drop row in
data/drop-tests/sobol-campaign/figures/campaign_metrics.json at commit
80d42b1 on the campaign branch. The raw waveforms live in Box and are
not committed, so panel 3 is drawn from those fitted parameters and is
labeled reconstructed; panels 1 and 2 are the model itself.

Usage (repo root): python scripts/figures/ballistic_model_figure.py
Writes docs/figures/ballistic_model_derivation.png. Needs matplotlib.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# palette (dataviz reference, validated 2-slot light mode; matches the
# earlier issue-94 figures: blue = bottom sensor, orange = top sensor)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
ORANGE = "#eb6834"
GRAY = "#b9b7b0"
GRID = "#e6e4de"

G = 9.80665

# measured per-drop values, bag26v Signal 33 (provenance in the docstring)
DV = 5.029                  # arrest Delta v from the bottom sensor (m/s)
T_SECOND_MS = 24.66         # impact burst to landing burst (ms)
SECOND_REL_DB = 0.99        # landing burst vs impact envelope peak (dB)
SIGMA = 185.9               # fitted ringdown decay rate (1/s)
AMP0_G = 56.6               # fitted envelope intercept (G)

V_SEP = G * T_SECOND_MS * 1e-3 / 2          # 0.121 m/s
E_REB = V_SEP / DV                          # 0.0240
APEX_MM = V_SEP ** 2 / (2 * G) * 1e3        # 0.75 mm
T_APEX_MS = T_SECOND_MS / 2                 # 12.33 ms

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "font.size": 11.5,
})

fig, axes = plt.subplots(
    1, 3, figsize=(14.8, 5.3), gridspec_kw={"width_ratios": [1.12, 1.0, 1.30]}
)
fig.subplots_adjust(left=0.05, right=0.985, top=0.75, bottom=0.115, wspace=0.27)

fig.suptitle(
    "The hop clock runs from your $t_1$ to your $t_5$: "
    "ballistics converts that one interval into a launch speed",
    fontsize=15.5, x=0.05, ha="left", y=0.97, fontweight="bold",
)
fig.text(
    0.05, 0.855,
    "phases 1 to 5 from the 09-21 sketch; annotated numbers are measured values from "
    "round-2 article bag26v, drop Signal 33 ($\\Delta v$ 5.029 m/s, $t_{second}$ 24.66 ms);\n"
    "curves are the model and that drop's fitted parameters, not raw waveforms "
    "(those live in Box, not the repo)",
    fontsize=10.5, color=INK2, va="top",
)


def phase_dot(ax, x, y, num, dx, dy, label, arrow=None):
    ax.plot([x], [y], "o", ms=7, color=ORANGE, zorder=5)
    ax.annotate(
        num, (x, y), xytext=(x + dx, y + dy), fontsize=10, color=INK,
        fontweight="bold", ha="center", va="center",
        bbox=dict(boxstyle="circle,pad=0.28", fc=SURFACE, ec=INK2, lw=1.0),
    )
    ax.annotate(label, (x + dx, y + dy), xytext=(0, -14),
                textcoords="offset points", fontsize=9.3, color=INK2,
                ha="center", va="top")
    if arrow:
        ax.annotate("", xytext=(x + 1.1, y), xy=(x + 1.1, y + arrow),
                    arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.3))


# panel 1: the sketch, formalized (vertex height above its seat)
ax = axes[0]
t = np.linspace(0, T_SECOND_MS, 300)
y = (V_SEP * t * 1e-3 - G * (t * 1e-3) ** 2 / 2) * 1e3
ax.plot(t, y, color=ORANGE, lw=2.6, zorder=4)
ax.axhline(0, color=INK2, lw=1.2)
ax.fill_between([-3.5, 29.5], -0.14, 0, color=GRID, zorder=1)
ax.text(28.7, -0.075, "seat", color=INK2, fontsize=9.5, ha="right", va="center")

yy = lambda tt: (V_SEP * tt * 1e-3 - G * (tt * 1e-3) ** 2 / 2) * 1e3
phase_dot(ax, 0.0, 0.0, "1", -1.7, 0.22, "impact,\narrest")
phase_dot(ax, 4.9, yy(4.9), "2", -2.3, 0.14, "rising,\n$v_2$", arrow=0.13)
phase_dot(ax, T_APEX_MS, APEX_MM, "3", 0.0, 0.13, "stopped, $v_3 = 0$")
phase_dot(ax, 19.8, yy(19.8), "4", 2.3, 0.14, "falling,\n$v_4$", arrow=-0.13)
phase_dot(ax, T_SECOND_MS, 0.0, "5", 1.8, 0.22, "final\narrest")

ax.plot([T_APEX_MS, T_APEX_MS], [0.40, APEX_MM], color=INK2, lw=0.9,
        dashes=(3, 2.5), zorder=2)
ax.text(T_APEX_MS, 0.345, f"apex {APEX_MM:.2f} mm at\n$t_1 + t_{{second}}/2$\n"
        "(assumed, never observed)", color=INK2, fontsize=9.3, va="top",
        ha="center")

ax.annotate("", xytext=(0, 0.97), xy=(T_SECOND_MS, 0.97),
            arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.5))
ax.text(T_APEX_MS, 1.005,
        "$t_{second} = t_5 - t_1$ = 24.66 ms  (measured)",
        color=INK, fontsize=10.6, ha="center", fontweight="bold")
for xx in (0.0, T_SECOND_MS):
    ax.plot([xx, xx], [0.0, 0.97], color=GRAY, lw=0.9, dashes=(1.5, 2.5), zorder=2)

ax.set_title("1. your sketch, formalized", color=INK, fontsize=12.5, pad=6)
ax.set_xlabel("time from impact (ms)")
ax.set_ylabel("vertex height above its seat (mm)")
ax.set_xlim(-3.5, 29.5)
ax.set_ylim(-0.14, 1.10)

# panel 2: the derivation (velocity at slope -g)
ax = axes[1]
ax.axhline(0, color=INK2, lw=0.8)
ax.plot([0, T_SECOND_MS], [V_SEP, -V_SEP], color=ORANGE, lw=2.6, zorder=4)
ax.plot([0, T_APEX_MS, T_SECOND_MS], [V_SEP, 0, -V_SEP], "o", ms=7,
        color=ORANGE, zorder=5)
ax.text(0.8, V_SEP + 0.010, "launch $v_2$ = +0.121 m/s", color=INK,
        fontsize=10, fontweight="bold")
ax.text(11.5, -0.048, "$v_3 = 0$ at $t_3$", color=INK2, fontsize=9.6, ha="right")
ax.text(T_SECOND_MS - 0.6, -V_SEP - 0.024, "return $v_4$ = $-$0.121 m/s",
        color=INK, fontsize=10, ha="right", fontweight="bold")
ax.text(26.8, 0.142, "slope $= -g$\n(the only in-flight force\nthe model allows)",
        color=INK2, fontsize=9.6, ha="right", va="top")

ax.text(
    0.03, 0.035,
    "fall leg, your equation:  $v_{return} = 0 + g\\,(t_5 - t_3)$\n"
    "free-flight symmetry:  $t_5 - t_3 = t_{second}\\,/\\,2$\n"
    "$\\Rightarrow\\; v_{sep} = v_{return} = g\\,t_{second}/2$ = 0.121 m/s\n"
    "$\\Rightarrow\\; e_{rebound} = v_{sep}/\\Delta v$ = 0.121 / 5.029 = 0.0240",
    transform=ax.transAxes, fontsize=10.6, color=INK, va="bottom",
    bbox=dict(boxstyle="round,pad=0.55", fc=SURFACE, ec=GRAY, lw=1.0),
)

ax.set_title("2. the derivation: one straight line", color=INK, fontsize=12.5, pad=6)
ax.set_xlabel("time from impact (ms)")
ax.set_ylabel("vertex vertical velocity (m/s)")
ax.set_xlim(-1.5, 27.5)
ax.set_ylim(-0.335, 0.175)

# panel 3: what the top sensor records (reconstructed from fitted numbers)
ax = axes[2]
t = np.linspace(-3, 30, 4000)
floor = 2.5                                        # illustrative noise floor (G)
pk = 90.0                                          # impact envelope peak (drawn)
burst1 = pk * np.exp(-((t - 0.35) ** 2) / (2 * 0.45 ** 2))
decay = np.where(t > 0.6, AMP0_G * np.exp(-SIGMA * np.clip(t, 0, None) * 1e-3), 0)
pk2 = pk * 10 ** (SECOND_REL_DB / 20)
burst2 = np.where(
    t < T_SECOND_MS,
    pk2 * np.exp(-((t - T_SECOND_MS) ** 2) / (2 * 0.45 ** 2)),
    pk2 * np.exp(-SIGMA * (t - T_SECOND_MS) * 1e-3),
)
env = np.maximum.reduce([np.full_like(t, floor), burst1, decay, burst2])
ax.plot(t, env, color=ORANGE, lw=2.2, zorder=4)

ax.axvspan(15, 30, color=GRID, zorder=1)
ax.text(29.4, 249, "landing-burst search window +15 to +70 ms\n"
        "(shown to +30; the brake catch at +76 to +89 ms is outside it)",
        color=INK2, fontsize=9.0, ha="right", va="top")

ax.plot([0.35, 0.35], [97, 126], color=INK, lw=1.2)
ax.text(1.6, 101, "$t_1$: impact burst\n(assumed launch)", color=INK,
        fontsize=9.6, ha="left", va="bottom", fontweight="bold")
ax.plot([T_SECOND_MS, T_SECOND_MS], [110, 139], color=INK, lw=1.2)
ax.text(23.5, 144, "$t_5$: landing burst, +1.0 dB\nvs the impact envelope\n"
        "peak (measured)", color=INK, fontsize=9.6, ha="right", va="bottom",
        fontweight="bold")

ax.text(1.6, 98, "decaying slope: ringdown while\n"
        "still in contact, $1/\\sigma$ = 5.4 ms",
        color=INK2, fontsize=9.0, va="top")
ax.text(8.6, 62, "phases 2 to 4: free flight.\nThe sensor reads only noise:\n"
        "no velocity is readable, so\nthe clock is the measurement.",
        color=INK, fontsize=9.2, va="top")

ax.set_title("3. what the top sensor records (reconstructed)",
             color=INK, fontsize=12.5, pad=6)
ax.set_xlabel("time from impact (ms)")
ax.set_ylabel("top-vertex envelope (G)")
ax.set_xlim(-3, 30)
ax.set_ylim(-7, 252)

for ax in axes:
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

out = Path(__file__).resolve().parents[2] / "docs" / "figures"
out.mkdir(parents=True, exist_ok=True)
fig.savefig(out / "ballistic_model_derivation.png", dpi=150)
print("wrote", out / "ballistic_model_derivation.png")
