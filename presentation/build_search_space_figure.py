"""Build the T3-prism search-space figure for the IDETC slide deck.

One annotated mid-range design calls out the five geometry parameters the
optimizer changes, and four designs from the actual Sobol seed batch are
drawn to a common scale to show how different the same five numbers can
look. Requested in PR #84 (sgbaird, 2026-08-19): "a figure that shows a
few different structures and calls out the parameters that we're changing
in terms of geometry, in other words, a representation of the full search
space".

Sources of truth:
- Geometry + connectivity: cad/t3-prism/t3-prism.scad (branch
  claude/issue-95-20260806-0306). B_i at angle 90 + 120*i on a circle of
  radius R at z=0; T_i at 90 + 120*i + twist at z=H. Strut i: B_i -> T_i;
  bottom cable i: B_i -> B_{i+1}; top cable i: T_i -> T_{i+1};
  saddle cable i: B_{i+1} -> T_i. Joint spheres (d = 7 mm) at all six
  vertices.
- Bounds: bo/t3_prism_sobol_batch.py PARAMETERS (commit 65d0d3f, the
  script that generated the printed campaign batch): R 25-40 mm,
  H 60-110 mm, twist 40-80 deg, strut_d 6-12 mm, cable_d 3-5.5 mm.
- Seed designs: bo/t3-prism-bo-batch.csv (commit 18c41a6, PR #35 branch),
  specimens 1, 2, 3, 5 chosen for spread across the bounds.

Output: presentation/media/fig-search-space.png (16:9, for a full slide).
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "media" / "fig-search-space.png"

# Printed-campaign bounds (bo/t3_prism_sobol_batch.py PARAMETERS).
BOUNDS = {
    "R_mm": (25.0, 40.0),
    "H_mm": (60.0, 110.0),
    "twist_deg": (40.0, 80.0),
    "strut_d_mm": (6.0, 12.0),
    "cable_d_mm": (3.0, 5.5),
}
JOINT_D = 7.0  # mm, fixed across the campaign

# Annotated design: the middle of every bound.
MID = {k: (lo + hi) / 2.0 for k, (lo, hi) in BOUNDS.items()}

# Four of the nine Sobol seed designs (bo/t3-prism-bo-batch.csv rows 1,2,3,5).
SEEDS = [
    ("seed 2", dict(R_mm=38.9665, H_mm=99.9950, twist_deg=47.6915,
                    strut_d_mm=7.0737, cable_d_mm=3.9241)),
    ("seed 1", dict(R_mm=33.7842, H_mm=80.0836, twist_deg=77.4080,
                    strut_d_mm=10.8717, cable_d_mm=3.0003)),
    ("seed 3", dict(R_mm=25.1224, H_mm=72.0587, twist_deg=65.1213,
                    strut_d_mm=10.1789, cable_d_mm=4.6640)),
    ("seed 5", dict(R_mm=36.3001, H_mm=63.2297, twist_deg=52.9940,
                    strut_d_mm=6.4571, cable_d_mm=4.0550)),
]

# Entity colors: printed black PLA struts, orange TPU cables (EMC accent).
C_STRUT = "#2b2b2b"
C_CABLE = "#e97132"
INK = "#333333"
INK2 = "#595959"
GUIDE = "#8c8c8c"

AZ = math.radians(27.0)   # view azimuth
EL = math.radians(16.0)   # view elevation


def project(p):
    """Orthographic projection of one xyz point (mm) to (u, v, depth)."""
    x, y, z = p
    u = -math.sin(AZ) * x + math.cos(AZ) * y
    v = (-math.cos(AZ) * math.sin(EL) * x - math.sin(AZ) * math.sin(EL) * y
         + math.cos(EL) * z)
    d = (math.cos(AZ) * math.cos(EL) * x + math.sin(AZ) * math.cos(EL) * y
         + math.sin(EL) * z)
    return u, v, d


def nodes(params):
    """Bottom and top vertices per the t3-prism.scad equations."""
    R, H, tw = params["R_mm"], params["H_mm"], params["twist_deg"]
    bot, top = [], []
    for i in range(3):
        ab = math.radians(90 + 120 * i)
        at = math.radians(90 + 120 * i + tw)
        bot.append((R * math.cos(ab), R * math.sin(ab), 0.0))
        top.append((R * math.cos(at), R * math.sin(at), H))
    return bot, top


def members(params):
    """(p0, p1, diameter_mm, color) for every member and joint."""
    bot, top = nodes(params)
    sd, cd = params["strut_d_mm"], params["cable_d_mm"]
    out = []
    for i in range(3):
        out.append((bot[i], top[i], sd, C_STRUT))                    # strut
        out.append((bot[i], bot[(i + 1) % 3], cd, C_CABLE))          # bottom
        out.append((top[i], top[(i + 1) % 3], cd, C_CABLE))          # top
        out.append((bot[(i + 1) % 3], top[i], cd, C_CABLE))          # saddle
    for p in bot + top:                                              # joints
        out.append((p, p, JOINT_D, C_STRUT))
    return out


def draw_structure(ax, params, ppmm):
    """Depth-sorted round-capped segments; ppmm = display points per mm."""
    segs = []
    for p0, p1, d_mm, color in members(params):
        if p0 == p1:  # joint sphere: zero-length round-capped line
            u, v, dep = project(p0)
            segs.append((dep, [u, u], [v, v], d_mm, color))
            continue
        n = 24
        pts = [tuple(a + (b - a) * t / n for a, b in zip(p0, p1))
               for t in range(n + 1)]
        proj = [project(p) for p in pts]
        for a, b in zip(proj[:-1], proj[1:]):
            segs.append(((a[2] + b[2]) / 2, [a[0], b[0]], [a[1], b[1]],
                         d_mm, color))
    segs.sort(key=lambda s: s[0])  # far first
    for _, us, vs, d_mm, color in segs:
        ax.plot(us, vs, color=color, linewidth=d_mm * ppmm,
                solid_capstyle="round", zorder=3)


def setup_axes(ax, fig, center_uv, span_mm_w, span_mm_h):
    """Fix limits so both axes share one mm scale; return points-per-mm."""
    pos = ax.get_position()
    box_w_in = pos.width * fig.get_figwidth()
    box_h_in = pos.height * fig.get_figheight()
    s = max(span_mm_w / box_w_in, span_mm_h / box_h_in)  # mm per inch
    cu, cv = center_uv
    ax.set_xlim(cu - s * box_w_in / 2, cu + s * box_w_in / 2)
    ax.set_ylim(cv - s * box_h_in / 2, cv + s * box_h_in / 2)
    ax.set_axis_off()
    return 72.0 / s


def struct_center(params):
    us, vs = [], []
    bot, top = nodes(params)
    for p in bot + top:
        u, v, _ = project(p)
        us.append(u)
        vs.append(v)
    return (min(us) + max(us)) / 2, (min(vs) + max(vs)) / 2


def annotate_left(ax, params, cu, cv):
    """Callouts anchored in the margins around the structure at (cu, cv)."""
    R, H, tw = params["R_mm"], params["H_mm"], params["twist_deg"]
    bot, top = nodes(params)

    def uv(p):
        u, v, _ = project(p)
        return u, v

    leader = dict(arrowstyle="-", color=GUIDE, lw=1.0, shrinkA=2, shrinkB=4)

    # Circumscribed circle of the bottom triangle, dashed.
    ang = np.linspace(0, 2 * math.pi, 120)
    circ = [uv((R * math.cos(a), R * math.sin(a), 0.0)) for a in ang]
    ax.plot([c[0] for c in circ], [c[1] for c in circ], ls=(0, (4, 3)),
            lw=1.1, color=GUIDE, zorder=2)

    # Radius line from center to bottom vertex 2 (front right).
    c0 = uv((0, 0, 0))
    b2 = uv(bot[2])
    ax.plot([c0[0], b2[0]], [c0[1], b2[1]], ls=(0, (4, 3)), lw=1.1,
            color=GUIDE, zorder=2)
    mid_r = ((c0[0] + b2[0]) / 2, (c0[1] + b2[1]) / 2)
    ax.annotate("triangle radius R\n25 to 40 mm", xy=mid_r,
                xytext=(cu + 52, cv - 72), fontsize=11.5,
                color=INK, ha="left", va="top", arrowprops=leader)

    # Height dimension line, in clear space left of the structure.
    u_dim = cu - 60
    v_lo, v_hi = uv((0, 0, 0))[1], uv((0, 0, H))[1]
    ax.annotate("", xy=(u_dim, v_hi), xytext=(u_dim, v_lo),
                arrowprops=dict(arrowstyle="<->", color=GUIDE, lw=1.1))
    for v in (v_lo, v_hi):  # extension ticks
        ax.plot([u_dim - 4, u_dim + 4], [v, v], lw=1.0, color=GUIDE)
    ax.annotate("height H\n60 to 110 mm",
                xy=(u_dim - 6, (v_lo + v_hi) / 2), fontsize=11.5,
                color=INK, ha="right", va="center")

    # Twist arc above the top plane, outside the structure so it stays
    # visible: from the untwisted vertex-0 angle to the T_0 angle.
    a0, a1 = math.radians(90), math.radians(90 + tw)
    Ra = R + 12
    for a in (a0, a1):  # dotted radius spokes from the top-plane center
        sp = uv((Ra * math.cos(a), Ra * math.sin(a), H))
        ct = uv((0, 0, H))
        ax.plot([ct[0], sp[0]], [ct[1], sp[1]], ls=(0, (1.5, 2.5)),
                lw=1.0, color=GUIDE, zorder=4)
    arc = [uv((Ra * math.cos(a), Ra * math.sin(a), H))
           for a in np.linspace(a0, a1, 40)]
    ax.plot([c[0] for c in arc[:-2]], [c[1] for c in arc[:-2]],
            ls=(0, (4, 3)), lw=1.1, color=GUIDE, zorder=4)
    ax.annotate("", xy=arc[-1], xytext=arc[-4],
                arrowprops=dict(arrowstyle="->", color=GUIDE, lw=1.1),
                zorder=4)
    ax.annotate("twist angle\n40 to 80\N{DEGREE SIGN}",
                xy=arc[-6],
                xytext=(cu + 52, cv + 76), fontsize=11.5,
                color=INK, ha="center", va="top", arrowprops=leader)

    # Strut diameter: leader from the right margin to strut 2, mid-height.
    sp = uv(tuple(a + (b - a) * 0.55 for a, b in zip(bot[2], top[2])))
    ax.annotate("strut diameter\n6 to 12 mm\nrigid PLA", xy=sp,
                xytext=(cu + 58, cv + 8), fontsize=11.5, color=INK,
                ha="left", va="center", arrowprops=leader)

    # Cable diameter: leader from the lower-left margin to bottom cable 0->1.
    cm = uv(tuple((a + b) / 2 for a, b in zip(bot[0], bot[1])))
    ax.annotate("cable diameter\n3 to 5.5 mm\nflexible TPU", xy=cm,
                xytext=(cu - 56, cv - 62), fontsize=11.5, color=INK,
                ha="right", va="top", arrowprops=leader)


def main():
    fig = plt.figure(figsize=(13.333, 7.5), dpi=200)
    fig.patch.set_facecolor("white")

    # Left: annotated mid-range design (extra margin for callouts).
    ax_l = fig.add_axes([0.015, 0.09, 0.40, 0.84])
    cu, cv = struct_center(MID)
    ppmm = setup_axes(ax_l, fig, (cu, cv), 235, 178)
    draw_structure(ax_l, MID, ppmm)
    annotate_left(ax_l, MID, cu, cv)
    fig.text(0.215, 0.955, "Five geometry numbers define a design",
             ha="center", fontsize=14.5, color=INK, fontweight="bold")

    # Right: four Sobol seed designs on one common mm scale.
    fig.text(0.71, 0.955, "Four of the nine starting designs, to scale",
             ha="center", fontsize=14.5, color=INK, fontweight="bold")
    grid = [(0.435, 0.575), (0.715, 0.575), (0.435, 0.155), (0.715, 0.155)]
    for (x0, y0), (name, p) in zip(grid, SEEDS):
        ax = fig.add_axes([x0, y0, 0.27, 0.355])
        cu, cv = struct_center(p)
        ppmm_i = setup_axes(ax, fig, (cu, cv), 150, 126)
        draw_structure(ax, p, ppmm_i)
        ax.text(0.5, -0.03,
                f"R {p['R_mm']:.0f} mm   H {p['H_mm']:.0f} mm   "
                f"twist {p['twist_deg']:.0f}\N{DEGREE SIGN}\n"
                f"strut \N{DIAMETER SIGN} {p['strut_d_mm']:.1f} mm   "
                f"cable \N{DIAMETER SIGN} {p['cable_d_mm']:.1f} mm",
                transform=ax.transAxes, ha="center", va="top",
                fontsize=10.5, color=INK2, linespacing=1.4)

    fig.text(0.5, 0.018,
             "Bounds from the campaign batch generator "
             "(bo/t3_prism_sobol_batch.py). Material pairing, joint size, "
             "and vertical build orientation stay fixed.",
             ha="center", fontsize=9.5, color=INK2, style="italic")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor="white")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
