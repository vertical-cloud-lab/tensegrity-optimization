#!/usr/bin/env python3
"""Design-space figure (fig:design-space, a figure* in Methods).

(a) A mid-range prism of the five-variable box (R = 32.5 mm, H = 85 mm,
    theta = 60 deg, d_s = 9 mm, d_t = 4.25 mm, before the constant-mass
    scaling) as an orthographic side elevation, with H dimensioned
    vertically between the planes through the joint centres, callouts for
    d_s and d_t, and a plan view for R and theta. Every label carries the
    variable's bounds.
(b) Six tested specimens drawn at their printed (post-projection) geometry
    on one millimetre scale, labelled with ID, batch, trial (or Sobol spec),
    and the measured t180 and E_reb from manuscript/data.
(c) The as-printed corny7 photograph (figures/photos/corny7-asprinted.jpg).

Writes figures/design-space.{pdf,png}, and panel (a) alone as
figures/photos/overview/initialize-design-space.pdf for fig:overview.
Run build_overview_photos.py first (it crops the corny7 photo).

Usage:  python3 scripts/figures/build_design_space_figure.py
"""
from __future__ import annotations

import math
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Arc, Circle  # noqa: E402
from PIL import Image  # noqa: E402

from campaign_data import (  # noqa: E402
    INK, PLA_BLACK, REPO, STYLE, TPU_GREEN, load_articles)
from t3_prism_render import draw_prism, nodes, project  # noqa: E402

MID = dict(R=32.5, H=85.0, twist=60.0, d_s=9.0, d_t=4.25)
SIDE_AZIM = -25.0
SPECIMENS = ["bpx68c", "6lhxfy", "r2d2c6", "corny7", "corny9", "corny4"]
PHOTO = REPO / "figures" / "photos" / "corny7-asprinted.jpg"


def panel_a(ax):
    R, H, tw, ds, dt = (MID[k] for k in ("R", "H", "twist", "d_s", "d_t"))
    umin, umax, vmin, vmax = draw_prism(ax, R, H, tw, ds, dt, azim=SIDE_AZIM, elev=0.0)
    # H: vertical dimension between the joint-centre planes (v = 0 and v = H)
    xd = umin - 9.0
    for v in (0.0, H):
        ax.plot([xd - 2.0, umin - 1.0], [v, v], color=INK, lw=0.4, ls=(0, (2, 1.5)))
    ax.annotate("", xy=(xd, H), xytext=(xd, 0.0),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.6, mutation_scale=6,
                                shrinkA=0, shrinkB=0))
    ax.text(xd - 2.5, H / 2, "$H$\n60 to\n110 mm", ha="right", va="center", fontsize=7)
    # d_s callout on the nearest strut, d_t on a saddle cable
    bot, top = nodes(R, H, tw)
    strut = max(range(3), key=lambda i: project(bot[i], SIDE_AZIM, 0)[2]
                + project(top[i], SIDE_AZIM, 0)[2])
    pa, pb = project(bot[strut], SIDE_AZIM, 0), project(top[strut], SIDE_AZIM, 0)
    sx, sy = pa[0] + 0.62 * (pb[0] - pa[0]), pa[1] + 0.62 * (pb[1] - pa[1])
    ax.annotate("$d_s$, 6 to 12 mm", xy=(sx, sy), xytext=(umax + 4.0, H * 0.80),
                fontsize=7, ha="left", va="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.5, mutation_scale=5,
                                shrinkA=1, shrinkB=1))
    j = (strut + 1) % 3
    pc, pd = project(bot[(j + 1) % 3], SIDE_AZIM, 0), project(top[j], SIDE_AZIM, 0)
    cx, cy = pc[0] + 0.30 * (pd[0] - pc[0]), pc[1] + 0.30 * (pd[1] - pc[1])
    ax.annotate("$d_t$, 3.0 to 5.5 mm", xy=(cx, cy), xytext=(umax + 4.0, H * 0.22),
                fontsize=7, ha="left", va="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.5, mutation_scale=5,
                                shrinkA=1, shrinkB=1))
    ax.text((umin + umax) / 2, vmax + 4.0, "Side elevation (projection)", ha="center",
            va="bottom", fontsize=7, style="italic")

    # plan view below: R and theta
    oy = -R - 26.0
    ox = (umin + umax) / 2
    ax.add_patch(Circle((ox, oy), R, fill=False, ec=INK, lw=0.4, ls=(0, (1, 1.5))))
    bxy = [(ox + p[0], oy + p[1]) for p in bot]
    txy = [(ox + p[0], oy + p[1]) for p in top]
    for i in range(3):
        k = (i + 1) % 3
        ax.plot([bxy[i][0], bxy[k][0]], [bxy[i][1], bxy[k][1]], color=TPU_GREEN, lw=1.4,
                solid_capstyle="round")
        ax.plot([txy[i][0], txy[k][0]], [txy[i][1], txy[k][1]], color=TPU_GREEN, lw=1.0,
                ls=(0, (3, 1.5)))
        ax.plot([bxy[i][0], txy[i][0]], [bxy[i][1], txy[i][1]], color=PLA_BLACK, lw=1.8,
                solid_capstyle="round")
    ax.annotate("", xy=bxy[0], xytext=(ox, oy),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.6, mutation_scale=6,
                                shrinkA=0, shrinkB=0))
    ax.annotate("$R$, 25 to 40 mm", xy=(ox, oy + R * 0.55), xytext=(ox + R + 3.0, oy + R * 0.85),
                fontsize=7, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.4, shrinkA=1, shrinkB=0))
    ax.add_patch(Arc((ox, oy), 0.9 * R, 0.9 * R, theta1=90, theta2=90 + MID["twist"],
                     color=INK, lw=0.6))
    ax.plot([ox, txy[0][0]], [oy, txy[0][1]], color=INK, lw=0.4, ls=(0, (2, 1.5)))
    mid_ang = math.radians(90 + MID["twist"] / 2)
    ax.annotate(r"$\theta$, 40$^\circ$ to 80$^\circ$",
                xy=(ox + 0.45 * R * math.cos(mid_ang), oy + 0.45 * R * math.sin(mid_ang)),
                xytext=(ox - R - 3.0, oy + R * 0.85), fontsize=7, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.4, shrinkA=1, shrinkB=0))
    ax.text(ox, oy - R - 4.0, "Plan view: base (solid), top (dashed)", ha="center",
            va="top", fontsize=7, style="italic")
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(umin - 52.0, umax + 50.0)
    ax.set_ylim(oy - R - 14.0, vmax + 12.0)


def initialize_drawing(ax):
    """Mid-range prism, side elevation and plan view side by side, symbols only."""
    R, H, tw, ds, dt = (MID[k] for k in ("R", "H", "twist", "d_s", "d_t"))
    umin, umax, vmin, vmax = draw_prism(ax, R, H, tw, ds, dt, azim=SIDE_AZIM, elev=0.0)
    xd = umin - 7.0
    ax.annotate("", xy=(xd, H), xytext=(xd, 0.0),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.6, mutation_scale=6,
                                shrinkA=0, shrinkB=0))
    ax.text(xd - 2.0, H / 2, "$H$", ha="right", va="center", fontsize=9)
    ax.text(umax + 3.0, H * 0.78, "$d_s$", ha="left", va="center", fontsize=9)
    ax.text(umax + 3.0, H * 0.30, "$d_t$", ha="left", va="center", fontsize=9,
            color=TPU_GREEN)
    bot, top = nodes(R, H, tw)
    ox, oy = umax + 22.0 + R, H / 2
    ax.add_patch(Circle((ox, oy), R, fill=False, ec=INK, lw=0.4, ls=(0, (1, 1.5))))
    bxy = [(ox + p[0], oy + p[1]) for p in bot]
    txy = [(ox + p[0], oy + p[1]) for p in top]
    for i in range(3):
        k = (i + 1) % 3
        ax.plot([bxy[i][0], bxy[k][0]], [bxy[i][1], bxy[k][1]], color=TPU_GREEN, lw=1.2)
        ax.plot([txy[i][0], txy[k][0]], [txy[i][1], txy[k][1]], color=TPU_GREEN, lw=0.9,
                ls=(0, (3, 1.5)))
        ax.plot([bxy[i][0], txy[i][0]], [bxy[i][1], txy[i][1]], color=PLA_BLACK, lw=1.6)
    ax.annotate("", xy=bxy[0], xytext=(ox, oy),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.6, mutation_scale=6,
                                shrinkA=0, shrinkB=0))
    ax.text(ox + 2.0, oy + R * 0.3, "$R$", fontsize=9, ha="left", va="center")
    ax.add_patch(Arc((ox, oy), 0.9 * R, 0.9 * R, theta1=90, theta2=90 + MID["twist"],
                     color=INK, lw=0.6))
    mid_ang = math.radians(90 + MID["twist"] / 2)
    ax.annotate(r"$\theta$", xy=(ox + 0.45 * R * math.cos(mid_ang),
                                 oy + 0.45 * R * math.sin(mid_ang)),
                xytext=(ox - 0.8 * R, oy + 1.22 * R), fontsize=9, ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.4, shrinkA=1, shrinkB=0))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(umin - 16.0, ox + R + 3.0)
    ax.set_ylim(vmin - 2.0, max(vmax, oy + 1.4 * R) + 2.0)


def panel_b(ax, articles):
    by_id = {a["print_id"]: a for a in articles}
    cell_w, cell_h = 92.0, 168.0
    for k, pid in enumerate(SPECIMENS):
        a = by_id[pid]
        row, col = divmod(k, 3)
        cx = (col + 0.5) * cell_w
        base = (1 - row) * cell_h + 50.0
        _, _, vmin, _ = draw_prism(ax, a["R"], a["H"], a["twist"], a["d_s"], a["d_t"],
                                   x0=cx, y0=base, azim=-20.0, elev=10.0)
        if a["batch"] == 1:
            ident = "batch 1, reference" if a["spec"] == "S0" else f"batch 1, spec {a['spec']}"
        else:
            ident = f"batch {a['batch']}, trial {a['trial']}"
        values = (rf"$t_{{180}}$ {a['t180']:.3f}" "\n"
                  rf"$E_{{\mathrm{{reb}}}}$ {a['e_reb_mJ']:.1f} mJ")
        ax.text(cx, base + vmin - 2.5, f"{pid}\n{ident}\n{values}", ha="center",
                va="top", fontsize=6.6, linespacing=1.25)
    x1 = 3 * cell_w - 4.0
    ys = 2 * cell_h - 2.0  # above the short r2d2c6, top right
    ax.plot([x1 - 20.0, x1], [ys, ys], color=INK, lw=1.2, solid_capstyle="butt")
    ax.text(x1 - 22.5, ys, "20 mm", ha="right", va="center", fontsize=6.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(0, 3 * cell_w)
    ax.set_ylim(-9.0, 2 * cell_h + 2.0)


def panel_c(ax):
    if PHOTO.exists():
        ax.imshow(Image.open(PHOTO))
    else:
        ax.text(0.5, 0.5, "corny7 photo\n(missing)", ha="center", va="center",
                transform=ax.transAxes)
    ax.axis("off")


def main() -> int:
    articles = load_articles()
    with plt.rc_context(STYLE):
        fig = plt.figure(figsize=(7.0, 3.15))
        gs = fig.add_gridspec(1, 3, width_ratios=[2.35, 3.25, 1.4], wspace=0.04,
                              left=0.0, right=1.0, top=0.93, bottom=0.0)
        axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
        panel_a(axes[0])
        panel_b(axes[1], articles)
        panel_c(axes[2])
        for ax in axes:
            ax.set_anchor("N")  # top-align the equal-aspect panels
        fig.canvas.draw()  # settle the equal-aspect boxes before reading them
        for ax, letter in zip(axes, "abc"):
            pos = ax.get_position()
            fig.text(pos.x0, 0.985, f"({letter})", ha="left", va="top", fontsize=9,
                     fontweight="bold")
        out = REPO / "figures" / "design-space"
        for ext in ("pdf", "png"):
            fig.savefig(f"{out}.{ext}", bbox_inches="tight", pad_inches=0.02,
                        facecolor="white",
                        metadata={"CreationDate": None} if ext == "pdf" else None)
        plt.close(fig)
        # compact symbol-only version for the Initialize panel of fig:overview
        fig, ax = plt.subplots(figsize=(2.6, 1.3))
        initialize_drawing(ax)
        fig.savefig(REPO / "figures" / "photos" / "overview" / "initialize-design-space.pdf",
                    bbox_inches="tight", pad_inches=0.01, facecolor="white",
                    metadata={"CreationDate": None})
        plt.close(fig)
    by_id = {a["print_id"]: a for a in articles}
    for pid in SPECIMENS:
        a = by_id[pid]
        print(pid, a["batch"], a["spec"], a["trial"], f"{a['t180']:.4f}", f"{a['e_reb_mJ']:.2f}",
              a["R"], a["H"], a["twist"], a["d_s"], a["d_t"])
    print(f"wrote {out}.pdf and .png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
