"""Redraw the diagrams from the handwritten "Rebound energy" notes (issue #94).

Source: the handwritten PDF attached to
https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/94
(https://github.com/user-attachments/files/32534339/Rebound.energy.pdf),
dated September 21, 2026. Three figures, matching the three diagram groups
in the notes:

  1. the classical bounce (snaps 1 to 3),
  2. the apparatus snapshots (structure + plate + accelerometers),
  3. the five-phase time key behind v_s = g (t5 - t1) / 2.

Colors are the repo's validated dataviz defaults (light mode): ink #0b0b0b,
secondary #52514e, muted #898781, blue #2a78d6 (velocities), orange #eb6834
(accelerometers and their timestamps), aqua #1baf7a (struts). Validated with
the dataviz palette checker; the aqua contrast warn is relieved by direct
labels on every element.

Usage: python scripts/figures/rebound_energy_notes_figures.py
Writes PNGs into docs/figures/.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

INK = "#0b0b0b"
SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
BLUE = "#2a78d6"    # velocities
ORANGE = "#eb6834"  # accelerometers, timestamps
AQUA = "#1baf7a"    # struts

OUT = Path(__file__).resolve().parents[2] / "docs" / "figures"


def ground(ax, x0, x1, y=0.0, spacing=0.28, tick=0.16):
    """Hatched ground symbol: a baseline with short diagonal strokes below."""
    ax.plot([x0, x1], [y, y], color=INK, lw=1.6, solid_capstyle="butt", zorder=3)
    for x in np.arange(x0 + 0.06, x1, spacing):
        ax.plot([x, x - tick * 0.7], [y, y - tick], color=MUTED, lw=1.0, zorder=2)


def varrow(ax, x, y0, y1, label=None, dx_label=0.16, color=BLUE, lw=2.4):
    """Vertical velocity arrow from (x, y0) to (x, y1) with an ink label."""
    ax.annotate(
        "",
        xy=(x, y1),
        xytext=(x, y0),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=20),
        zorder=6,
    )
    if label:
        ax.text(
            x + dx_label,
            (y0 + y1) / 2,
            label,
            color=INK,
            fontsize=13,
            va="center",
            ha="left",
            zorder=6,
        )


def dim(ax, x, y0, y1, label):
    """Dimension line with arrowheads at both ends (for the drop height h)."""
    ax.annotate(
        "",
        xy=(x, y1),
        xytext=(x, y0),
        arrowprops=dict(arrowstyle="<|-|>", color=MUTED, lw=1.4, mutation_scale=14),
        zorder=4,
    )
    for y in (y0, y1):
        ax.plot([x - 0.09, x + 0.09], [y, y], color=MUTED, lw=1.2, zorder=4)
    ax.text(x + 0.14, (y0 + y1) / 2, label, color=SECONDARY, fontsize=13, va="center")


def ball(ax, x, y, r=0.20):
    ax.add_patch(Circle((x, y), r, facecolor=INK, edgecolor="none", zorder=5))


def scene_title(ax, x, y, text):
    ax.text(x, y, text, color=INK, fontsize=12.5, fontweight="bold", ha="center")


def note(ax, x, y, text, ha="center", fontsize=10.5, color=SECONDARY):
    ax.text(x, y, text, color=color, fontsize=fontsize, ha=ha, va="top")


def sensor(ax, x, y, label, label_dx=0.16, label_dy=0.0, s=0.17):
    """Accelerometer marker: an orange square with an ink label beside it."""
    ax.add_patch(
        Rectangle(
            (x - s / 2, y - s / 2),
            s,
            s,
            facecolor=ORANGE,
            edgecolor=INK,
            lw=0.9,
            zorder=7,
        )
    )
    ax.text(
        x + label_dx,
        y + label_dy,
        label,
        color=INK,
        fontsize=12,
        va="center",
        ha="left",
        zorder=7,
    )


def prism(ax, cx, base_y, height=1.35, width=1.55, squash=1.0):
    """Simplified 2D projection of a T3 tensegrity prism.

    Three struts (thick aqua) cross between the bottom and top triangles;
    tendons (thin secondary ink) trace both triangles and the three side
    tendons. Returns the apex node position (where the top accelerometer
    sits in the notes' drawings).
    """
    h = height * squash
    w = width / 2
    bot = [(-0.95 * w, 0.02), (0.12 * w, 0.12), (0.98 * w, 0.06)]
    top = [(-0.86 * w, 0.92 * h), (0.06 * w, h), (0.94 * w, 0.88 * h)]
    bot = [(cx + x, base_y + y) for x, y in bot]
    top = [(cx + x, base_y + y) for x, y in top]

    tendons = (
        [(bot[i], bot[(i + 1) % 3]) for i in range(3)]
        + [(top[i], top[(i + 1) % 3]) for i in range(3)]
        + [(bot[i], top[i]) for i in range(3)]
    )
    for (xa, ya), (xb, yb) in tendons:
        ax.plot([xa, xb], [ya, yb], color=SECONDARY, lw=1.0, zorder=4)
    struts = [(bot[0], top[1]), (bot[1], top[2]), (bot[2], top[0])]
    for (xa, ya), (xb, yb) in struts:
        ax.plot(
            [xa, xb], [ya, yb], color=AQUA, lw=4.0, solid_capstyle="round", zorder=5
        )
    apex = top[1]
    return apex


def block(ax, cx, bottom, bw=2.3, bh=0.66):
    ax.add_patch(
        Rectangle(
            (cx - bw / 2, bottom),
            bw,
            bh,
            facecolor=GRID,
            edgecolor=INK,
            lw=1.4,
            zorder=4,
        )
    )
    ax.text(
        cx,
        bottom + bh / 2,
        "$m_b$",
        color=INK,
        fontsize=14,
        ha="center",
        va="center",
        zorder=5,
    )
    return bottom + bh  # top surface y


def new_axes(figsize):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {path}")


def fig1_classical_bounce():
    fig, ax = new_axes((11, 4.0))
    ax.set_xlim(-0.4, 12.4)
    ax.set_ylim(-1.75, 4.1)

    centers = (1.7, 6.0, 10.3)
    for cx in centers:
        ground(ax, cx - 1.55, cx + 1.55)
    for x in (3.85, 8.15):
        ax.text(x, 1.1, r"$\Rightarrow$", color=MUTED, fontsize=22, ha="center")

    # Snap 1: falling from height h with velocity v_i just before impact.
    scene_title(ax, centers[0], 3.75, "Snap 1")
    ball(ax, centers[0] - 0.35, 2.55)
    varrow(ax, centers[0] - 0.35, 2.25, 0.55, label="$v_i$")
    dim(ax, centers[0] + 0.55, 0.0, 2.55, "$h$")
    note(ax, centers[0], -0.55, "velocity immediately\nprior to impact")
    note(
        ax,
        centers[0],
        -1.25,
        r"$E_i = \frac{1}{2} m v_i^2$",
        fontsize=12.5,
        color=INK,
    )

    # Snap 2: at rest on the ground at the instant of impact.
    scene_title(ax, centers[1], 3.75, "Snap 2")
    ball(ax, centers[1], 0.20)
    note(ax, centers[1], -0.55, "$v = 0$ at impact", fontsize=12.5, color=INK)
    note(ax, centers[1], -1.25, "energy lost")

    # Snap 3: leaving the ground with the return velocity v_s.
    scene_title(ax, centers[2], 3.75, "Snap 3")
    ball(ax, centers[2] - 0.15, 0.75)
    varrow(ax, centers[2] - 0.15, 1.05, 2.45, label="$v_s$")
    note(ax, centers[2], -0.55, "return velocity immediately\nfollows the impact")
    note(
        ax,
        centers[2],
        -1.25,
        r"$E_r = \frac{1}{2} m v_s^2$",
        fontsize=12.5,
        color=INK,
    )

    save(fig, "rebound_notes_fig1_classical_bounce.png")


def fig2_apparatus_snapshots():
    fig, ax = new_axes((11.5, 5.2))
    ax.set_xlim(-0.6, 13.0)
    ax.set_ylim(-1.55, 4.85)

    centers = (1.9, 6.2, 10.5)
    subtitles = (
        "immediately prior to impact",
        "during impact",
        "immediately following impact",
    )
    for i, (cx, sub) in enumerate(zip(centers, subtitles)):
        ground(ax, cx - 1.85, cx + 1.85)
        ax.text(
            cx,
            4.55,
            f"Snap {i + 1}",
            color=INK,
            fontsize=12.5,
            fontweight="bold",
            ha="center",
        )
        ax.text(cx, 4.18, sub, color=SECONDARY, fontsize=10.5, ha="center")

    # Snap 1: the whole assembly falls with uniform velocity v_i.
    cx = centers[0]
    top_y = block(ax, cx, 0.75)
    apex = prism(ax, cx, top_y)
    sensor(ax, apex[0], apex[1] + 0.10, "$A_T$")
    sensor(ax, cx + 0.95, top_y + 0.09, "$A_b$")
    ax.text(cx - 1.0, top_y + 0.55, "$m_T$", color=INK, fontsize=13, ha="center")
    varrow(ax, cx - 1.75, 1.15, 0.25)
    ax.text(cx - 1.75, 1.66, "$v_i$", color=INK, fontsize=13, ha="center")
    ax.text(cx - 1.75, 1.32, "uniform", color=SECONDARY, fontsize=10.5, ha="center")
    ax.annotate(
        "",
        xy=(cx + 1.65, 0.55),
        xytext=(cx + 1.65, 0.02),
        arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.3, mutation_scale=12),
    )
    ax.text(cx + 1.78, 0.32, "$x_0$", color=SECONDARY, fontsize=12, va="center")
    note(ax, cx, -0.55, "$v_i$ is measured from $A_b$")

    # Snap 2: the plate arrests; the structure compresses.
    cx = centers[1]
    top_y = block(ax, cx, 0.0)
    apex = prism(ax, cx, top_y, squash=0.68)
    sensor(ax, apex[0], apex[1] + 0.10, "$A_T$")
    sensor(ax, cx + 0.95, top_y + 0.09, "$A_b$")
    note(ax, cx, -0.55, "$v = 0$ uniformly", fontsize=12.5, color=INK)
    note(ax, cx, -1.05, "plate arrests; structure compresses\nand is about to rebound")

    # Snap 3: the top vertex separates with velocity v_s.
    cx = centers[2]
    top_y = block(ax, cx, 0.0)
    apex = prism(ax, cx, top_y)
    sensor(ax, cx + 0.95, top_y + 0.09, "$A_b$")
    lift = 0.62
    ax.plot(
        [apex[0], apex[0]],
        [apex[1] + 0.06, apex[1] + lift - 0.12],
        color=MUTED,
        lw=1.1,
        ls=(0, (2, 2)),
        zorder=4,
    )
    sensor(ax, apex[0], apex[1] + lift, "$A_T$")
    varrow(ax, apex[0], apex[1] + lift + 0.18, apex[1] + lift + 1.05, label="$v_s$")
    note(ax, cx, -0.55, "$v_s$ is calculated from timestamps\ntaken at $A_T$")

    save(fig, "rebound_notes_fig2_apparatus_snapshots.png")


def fig3_time_key():
    fig, ax = new_axes((11.5, 4.4))
    ax.set_xlim(-0.4, 13.4)
    ax.set_ylim(-2.45, 2.6)

    xs = (1.3, 3.9, 6.5, 9.1, 11.7)
    r = 0.18
    ys = (r, 1.11, 1.42, 1.11, r)  # phases 2 and 4 ride the ballistic arc
    ground(ax, 0.0, 13.0)

    # Dashed ballistic arc through the five phases.
    t = np.linspace(-1.0, 1.0, 120)
    ax.plot(
        xs[0] + (t + 1.0) / 2.0 * (xs[4] - xs[0]),
        r + (1.42 - r) * (1.0 - t**2),
        color=MUTED,
        lw=1.1,
        ls=(0, (3, 3)),
        zorder=2,
    )

    for x, y in zip(xs, ys):
        ball(ax, x, y, r=r)
    varrow(ax, xs[1] + 0.42, ys[1] - 0.30, ys[1] + 0.42, label="$v_2$", lw=2.0)
    varrow(ax, xs[3] + 0.42, ys[3] + 0.42, ys[3] - 0.30, label="$v_4$", lw=2.0)

    labels = (
        "impact\n$t_1 = 0$, $v_0 = 0$",
        "after impact\n$t_2$, $v_2$",
        "stopped\n$t_3$, $v_3 = 0$",
        "falling\n$t_4$, $v_4$",
        "final arrest\n$t_5$, $v_5 = 0$",
    )
    for i, (x, lab) in enumerate(zip(xs, labels)):
        ax.text(
            x,
            2.35,
            str(i + 1),
            color=MUTED,
            fontsize=15,
            fontweight="bold",
            ha="center",
        )
        note(ax, x, -0.45, lab, fontsize=11)

    # The interval the top accelerometer actually measures.
    ax.annotate(
        "",
        xy=(xs[4], -1.55),
        xytext=(xs[0], -1.55),
        arrowprops=dict(arrowstyle="<|-|>", color=ORANGE, lw=1.8, mutation_scale=16),
    )
    ax.text(
        (xs[0] + xs[4]) / 2,
        -1.85,
        "$t_5 - t_1$ measured at $A_T$"
        "$\\quad\\Rightarrow\\quad v_s = g\\,(t_5 - t_1)\\,/\\,2$",
        color=INK,
        fontsize=12.5,
        ha="center",
        va="top",
    )

    save(fig, "rebound_notes_fig3_time_key.png")


if __name__ == "__main__":
    fig1_classical_bounce()
    fig2_apparatus_snapshots()
    fig3_time_key()
