"""Sketch of the two terms in the Introduction sentence
"Strut geometry, tension-element cross-section, connectivity, and unit-cell
tiling span a large configuration space" (manuscript-body.tex, Introduction).

(a) the cell every specimen in this paper uses: one T3 prism, connectivity
    taken rule by rule from cad/t3-prism/t3-prism.scad (campaign branch);
(b) a cell with different connectivity (a four-strut prism);
(c) tiling: several copies of the cell joined into a larger block.

Panels (b) and (c) are illustrations of the terms only. Neither is a design
the lab has built or modeled. Run: python make_sketch.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

STRUT = "#111111"   # PLA struts are printed black in the campaign photos
CABLE = "#2e9d4f"   # TPU tendons are printed green
NODE = "#7a7a7a"


def prism(n, radius, height, twist_deg, z0=0.0, x0=0.0, y0=0.0, start_deg=90.0):
    """Nodes and members of an n-strut prism, using the CAD's connectivity.

    strut i  : B_i -> T_i
    bottom i : B_i -> B_{i+1}
    top i    : T_i -> T_{i+1}
    saddle i : B_{i+1} -> T_i
    """
    step = 360.0 / n
    ang_b = np.radians(start_deg + step * np.arange(n))
    ang_t = ang_b + np.radians(twist_deg)
    bottom = np.c_[x0 + radius * np.cos(ang_b), y0 + radius * np.sin(ang_b), np.full(n, z0)]
    top = np.c_[x0 + radius * np.cos(ang_t), y0 + radius * np.sin(ang_t), np.full(n, z0 + height)]
    struts = [(bottom[i], top[i]) for i in range(n)]
    cables = []
    for i in range(n):
        j = (i + 1) % n
        cables += [(bottom[i], bottom[j]), (top[i], top[j]), (bottom[j], top[i])]
    return bottom, top, struts, cables


def draw(ax, struts, cables, nodes):
    for a, b in cables:
        ax.plot(*zip(a, b), color=CABLE, lw=1.6, solid_capstyle="round", zorder=2)
    for a, b in struts:
        ax.plot(*zip(a, b), color=STRUT, lw=4.0, solid_capstyle="round", zorder=3)
    nodes = np.asarray(nodes)
    ax.scatter(nodes[:, 0], nodes[:, 1], nodes[:, 2], s=14, color=NODE, depthshade=False, zorder=4)


def finish(ax, pts, elev=14, azim=-80):
    pts = np.asarray(pts)
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    pad = 0.15 * (hi - lo).max()
    ax.set_xlim(lo[0] - pad, hi[0] + pad)
    ax.set_ylim(lo[1] - pad, hi[1] + pad)
    ax.set_zlim(lo[2] - pad, hi[2] + pad)
    ax.set_box_aspect(hi - lo + 2 * pad, zoom=1.35)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()


def impact_arrow(ax, x, y, z_top, length):
    ax.quiver(x, y, z_top + length, 0, 0, -length * 0.8, color="#c0392b", lw=2.2,
              arrow_length_ratio=0.35)
    ax.text(x + 0.25, y, z_top + 0.85 * length, "impact", color="#c0392b", fontsize=9)


R, H = 1.0, 2.4   # height-to-radius ratio in the campaign's range (R 25-40 mm, H 60-110 mm)

fig = plt.figure(figsize=(13.5, 5.6), dpi=200)
RECTS = [(0.00, 0.30, 0.33, 0.58), (0.335, 0.30, 0.33, 0.58), (0.67, 0.30, 0.33, 0.58)]

# (a) this paper's cell
ax = fig.add_axes(RECTS[0], projection="3d")
b, t, s, c = prism(3, R, H, 60)
draw(ax, s, c, np.r_[b, t])
for k in range(3):
    ax.text(*(b[k] * [1.35, 1.35, 1] + [0, 0, -0.42]), f"$B_{k}$", fontsize=11, ha="center")
    ax.text(*(t[k] * [1.35, 1.35, 1] + [0, 0, 0.22]), f"$T_{k}$", fontsize=11, ha="center")
impact_arrow(ax, 0, 0, H + 0.15, 1.0)
finish(ax, np.r_[b, t, [[0, 0, H + 1.2]], [[0, 0, -0.5]]])
ax.set_title("(a) This paper: one $T_3$ prism\n(a single cell, $1\\times1\\times1$)",
             fontsize=11, loc="center")
ax.text2D(0.06, -0.02,
          "3 struts (black) and 9 tendons (green).\n"
          "Connectivity, from the campaign CAD:\n"
          "  strut $i$: $B_i$ to $T_i$\n"
          "  bottom tendon $i$: $B_i$ to $B_{i+1}$\n"
          "  top tendon $i$: $T_i$ to $T_{i+1}$\n"
          "  side (saddle) tendon $i$: $B_{i+1}$ to $T_i$",
          transform=ax.transAxes, fontsize=9, va="top", family="DejaVu Sans")

# (b) different connectivity
ax = fig.add_axes(RECTS[1], projection="3d")
b, t, s, c = prism(4, R, H, 45)
draw(ax, s, c, np.r_[b, t])
finish(ax, np.r_[b, t, [[0, 0, H + 1.0]]])
ax.set_title("(b) A different connectivity:\na four-strut prism (illustration)", fontsize=11)
ax.text2D(0.06, -0.02,
          "4 struts and 12 tendons: the same kinds of\n"
          "members, joined in a different pattern,\n"
          "so it is a different cell type. Choosing\n"
          "among cell types is a categorical choice.\n"
          "Held fixed at the $T_3$ prism in this paper.",
          transform=ax.transAxes, fontsize=9, va="top")

# (c) tiling: 3 x 1 x 2 block of T3 cells, stacked in columns with alternating twist
ax = fig.add_axes(RECTS[2], projection="3d")
pts = []
for col in range(3):
    x0 = col * 3.1 * R
    b1, t1, s1, c1 = prism(3, R, H, 60, x0=x0)
    # upper cell starts on the lower cell's top triangle and twists back
    b2, t2, s2, c2 = prism(3, R, H, -60, z0=H, x0=x0, start_deg=150)
    draw(ax, s1 + s2, c1 + c2, np.r_[b1, t1, t2])
    pts += [*b1, *t1, *t2]
impact_arrow(ax, 3.1 * R, 0, 2 * H + 0.15, 1.2)
finish(ax, np.r_[np.asarray(pts), [[3.1 * R, 0, 2 * H + 1.4]]])
ax.set_title("(c) Tiling: copies of the cell joined into a block\n"
             "(here $N_x\\times N_y\\times N_z = 3\\times1\\times2$, illustration)", fontsize=11)
ax.text2D(0.06, -0.02,
          "Tiling = how many cells, how they are arranged,\n"
          "and how each is oriented to the impact.\n"
          "Here each column stacks two cells that share a\n"
          "triangle of nodes. Not varied in this paper:\n"
          "every specimen is one cell.",
          transform=ax.transAxes, fontsize=9, va="top")

out = Path(__file__).with_name("connectivity-tiling-sketch.png")
fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.15)
print("wrote", out)
