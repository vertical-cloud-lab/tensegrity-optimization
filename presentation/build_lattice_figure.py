"""Build a concept image of a TPU + PLA tensegrity-inspired lattice.

Requested in PR #84 (me-madsen, 2026-08-24): a single unlabeled figure of
what a TPU + PLA lattice might look like, in the same clean rendering
style as the T3 search-space figures. This is a concept visual (the
lattice is future work, per the review discussion on the presentation
template), so the geometry is a plausible extension of the printed T3
prism rather than a design that exists in the campaign:

- A single level of T3 prisms (revised per me-madsen's follow-up: the
  two-layer mast version read as a mess), each shorter than the printed
  mid-range specimen so the prism proportions look roughly equilateral
  (height close to the base triangle's side length).
- Modules tile a 2 x 2 grid (also down from 3 x 2 in that revision).
  Neighbors are joined by one short TPU cable at the bottom and top
  vertex planes (the single nearest vertex pair), which is what makes it
  read as a lattice of connected modules rather than an array.
- Member proportions, colors, camera, and the occlusion-safe depth
  sorting all come from build_search_space_figure.py, so this image
  cannot drift from the T3 assets in style.

Output: presentation/media/fig-lattice-concept.png (16:9, unlabeled).
"""

from __future__ import annotations

import itertools
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build_search_space_figure import C_CABLE, C_STRUT, JOINT_D

OUT = HERE / "media" / "fig-lattice-concept.png"

# One module. Shorter than the printed mid-range specimen so the prism
# reads roughly equilateral: base triangle side = R * sqrt(3) ~ 52 mm,
# so H ~ 55 mm keeps height and width visually comparable.
R = 30.0          # mm, triangle radius
H = 55.0          # mm, height per layer
TWIST = 60.0      # deg
STRUT_D = 8.0     # mm, rigid PLA
CABLE_D = 3.5     # mm, flexible TPU
GRID_X = 2        # columns across
GRID_Y = 2        # columns deep
LAYERS = 1
SPACING = 84.0    # mm, column center-to-center

# Same azimuth as the T3 assets, but a higher elevation: from the T3
# camera the six columns stack up visually and the lattice reads as a
# tangle, so the lattice view looks down a little more steeply.
AZ = math.radians(27.0)
EL = math.radians(32.0)


def project(p):
    """Orthographic projection of one xyz point (mm) to (u, v, depth)."""
    x, y, z = p
    u = -math.sin(AZ) * x + math.cos(AZ) * y
    v = (-math.cos(AZ) * math.sin(EL) * x - math.sin(AZ) * math.sin(EL) * y
         + math.cos(EL) * z)
    d = (math.cos(AZ) * math.cos(EL) * x + math.sin(AZ) * math.cos(EL) * y
         + math.sin(EL) * z)
    return u, v, d


def prism_members(cx, cy, z0, rot_deg, twist_deg):
    """Members of one prism whose bottom triangle sits at rot_deg."""
    bot, top = [], []
    for i in range(3):
        ab = math.radians(90 + 120 * i + rot_deg)
        at = math.radians(90 + 120 * i + rot_deg + twist_deg)
        bot.append((cx + R * math.cos(ab), cy + R * math.sin(ab), z0))
        top.append((cx + R * math.cos(at), cy + R * math.sin(at), z0 + H))
    out = []
    for i in range(3):
        out.append((bot[i], top[i], STRUT_D, C_STRUT))            # strut
        out.append((bot[i], bot[(i + 1) % 3], CABLE_D, C_CABLE))  # bottom
        out.append((top[i], top[(i + 1) % 3], CABLE_D, C_CABLE))  # top
        out.append((bot[(i + 1) % 3], top[i], CABLE_D, C_CABLE))  # saddle
    for p in bot + top:                                           # joints
        out.append((p, p, JOINT_D, C_STRUT))
    return out


def column_vertices(cx, cy):
    """Vertex positions of one column, keyed by plane index 0..LAYERS."""
    planes = {}
    for k in range(LAYERS + 1):
        # Alternating chirality returns the triangle to rot 0 on even
        # planes and leaves it at rot TWIST on odd planes.
        rot = TWIST if k % 2 else 0.0
        planes[k] = [
            (cx + R * math.cos(math.radians(90 + 120 * i + rot)),
             cy + R * math.sin(math.radians(90 + 120 * i + rot)),
             k * H)
            for i in range(3)
        ]
    return planes


def lattice_members():
    centers = {(i, j): (i * SPACING, j * SPACING)
               for i, j in itertools.product(range(GRID_X), range(GRID_Y))}
    out = []
    for cx, cy in centers.values():
        for k in range(LAYERS):
            rot = TWIST if k % 2 else 0.0
            tw = -TWIST if k % 2 else TWIST
            out.extend(prism_members(cx, cy, k * H, rot, tw))
    # Short TPU links between grid neighbors at every vertex plane: only
    # the closest vertex pair(s), so the joints stay sparse and legible.
    verts = {ij: column_vertices(*c) for ij, c in centers.items()}
    for (i, j) in centers:
        for ni, nj in ((i + 1, j), (i, j + 1)):
            if (ni, nj) not in centers:
                continue
            for k in range(LAYERS + 1):
                pairs = [(math.dist(a, b), a, b)
                         for a in verts[(i, j)][k]
                         for b in verts[(ni, nj)][k]]
                d, a, b = min(pairs)  # single closest pair only
                out.append((a, b, CABLE_D, C_CABLE))
    return out


FADE = 0.35  # how much the farthest members blend toward white


def draw_members(ax, members, ppmm):
    """Depth-sorted round-capped segments (front-surface depth), as in
    build_search_space_figure.draw_structure but over an arbitrary
    member list so the whole lattice occludes correctly as one body.
    A single prism needs no depth cue, but with several columns behind
    one another flat colors read as a tangle, so far segments fade
    slightly toward the background."""
    segs = []
    for p0, p1, d_mm, color in members:
        if p0 == p1:
            u, v, dep = project(p0)
            segs.append((dep + d_mm / 2, [u, u], [v, v], d_mm, color))
            continue
        n = 32
        pts = [tuple(a + (b - a) * t / n for a, b in zip(p0, p1))
               for t in range(n + 1)]
        proj = [project(p) for p in pts]
        for a, b in zip(proj[:-1], proj[1:]):
            segs.append(((a[2] + b[2]) / 2 + d_mm / 2,
                         [a[0], b[0]], [a[1], b[1]], d_mm, color))
    segs.sort(key=lambda s: s[0])  # far first
    d_lo = min(s[0] for s in segs)
    d_hi = max(s[0] for s in segs)
    for dep, us, vs, d_mm, color in segs:
        t = FADE * (d_hi - dep) / (d_hi - d_lo)
        r, g, b = matplotlib.colors.to_rgb(color)
        faded = (r + (1 - r) * t, g + (1 - g) * t, b + (1 - b) * t)
        ax.plot(us, vs, color=faded, linewidth=d_mm * ppmm,
                solid_capstyle="round", zorder=3)


def main():
    members = lattice_members()
    us, vs = [], []
    for p0, p1, _, _ in members:
        for p in (p0, p1):
            u, v, _ = project(p)
            us.append(u)
            vs.append(v)
    pad = 14.0  # mm, keeps thick round caps inside the frame
    span_u = max(us) - min(us) + 2 * pad
    span_v = max(vs) - min(vs) + 2 * pad
    cu = (max(us) + min(us)) / 2
    cv = (max(vs) + min(vs)) / 2

    fig = plt.figure(figsize=(13.333, 7.5), dpi=200)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    box_w_in, box_h_in = fig.get_figwidth(), fig.get_figheight()
    s = max(span_u / box_w_in, span_v / box_h_in)  # mm per inch
    ax.set_xlim(cu - s * box_w_in / 2, cu + s * box_w_in / 2)
    ax.set_ylim(cv - s * box_h_in / 2, cv + s * box_h_in / 2)
    ax.set_axis_off()
    draw_members(ax, members, 72.0 / s)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor="white")
    print(f"wrote {OUT} ({len(members)} members)")


if __name__ == "__main__":
    main()
