"""Render the old and new ``cuboctahedron_tessellation()`` side by side.

Produces ``figures/cuboctahedron_tessellation_diagnostic.png`` with four
panels:

1. the model this repository used to generate (6 struts + 36 cables),
2. its 6 struts alone, all of them body diagonals of the cuboctahedron and
   therefore all intersecting at the origin,
3. its 24 rim cables alone (the cuboctahedron's own edges), the only part
   of that model that was geometrically clean,
4. the replacement: the published Liu et al. (2019) tessellation block,
   40 nodes / 13 struts / 96 cables, read from ``models/data``.

The 12 cables missing from panel 3 ran from a hub node at the origin out
to each vertex, so each one lay inside the inner half of a strut (cable
radius 1.2 mm inside strut radius 2.5 mm). That co-axial burial plus the
six-way strut intersection is what made panel 1 read as a tangle of
strands rather than a structure. Panel 4 has neither problem: no strut
touches another, and a restriction zone of radius 0.75 keeps the centre
of the block empty.

Run from the repository root::

    python models/render_cuboctahedron_diagnostic.py
"""
import math
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "models"))
from generate_stl import (  # noqa: E402
    RADIUS_OVERRIDES, _cylinder_triangles, _scale,
    cuboctahedron_tessellation,
)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import to_rgb  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402
import numpy as np  # noqa: E402

# Same shading model as render_extended_preview_shaded.py.
STRUT_RGB = np.array(to_rgb("#c0392b"))
CABLE_RGB = np.array(to_rgb("#2980b9"))
LIGHT = np.array([-0.45, 0.35, 0.82])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
AMBIENT, DIFFUSE = 0.32, 0.68
SEGMENTS = 20


def legacy_cuboctahedron(scale=18.0):
    """The superseded model, kept here only so the figure can show it.

    Classified vertex pairs of a cuboctahedron by distance: the 24 pairs
    at sqrt(2)*scale became cables, and the 6 pairs at 2*sqrt(2)*scale
    became struts. At that distance the only pairs are the antipodal
    ones, so every strut was a diameter. A hub node was then added at the
    origin, on all six of them.
    """
    raw = []
    for sx in (1.0, -1.0):
        for sy in (1.0, -1.0):
            raw.append((sx, sy, 0.0))
            raw.append((sx, 0.0, sy))
            raw.append((0.0, sx, sy))
    nodes = [_scale(v, scale) for v in raw]
    edge_len = math.sqrt(2.0) * scale
    diag_len = 2.0 * edge_len
    tol = 1e-3 * scale
    struts, cables = [], []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            d = math.dist(nodes[i], nodes[j])
            if abs(d - edge_len) < tol:
                cables.append((i, j))
            elif abs(d - diag_len) < tol:
                struts.append((i, j))
    hub = len(nodes)
    nodes.append((0.0, 0.0, 0.0))
    cables.extend((i, hub) for i in range(hub))
    return nodes, struts, cables


def member_triangles(nodes, members, radius):
    tris = []
    for i, j in members:
        tris.extend(_cylinder_triangles(nodes[i], nodes[j], radius,
                                        segments=SEGMENTS))
    return np.array(tris) if tris else np.zeros((0, 3, 3))


def shade(tris, base_rgb):
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    norms = np.linalg.norm(n, axis=1, keepdims=True)
    n = n / np.where(norms == 0.0, 1.0, norms)
    brightness = AMBIENT + DIFFUSE * np.abs(n @ LIGHT)
    return np.clip(brightness[:, None] * base_rgb[None, :], 0.0, 1.0)


def draw(ax, nodes, struts, cables, strut_radius, cable_radius):
    strut_tris = member_triangles(nodes, struts, strut_radius)
    cable_tris = member_triangles(nodes, cables, cable_radius)
    tris = np.concatenate([strut_tris, cable_tris])
    colors = np.concatenate([shade(strut_tris, STRUT_RGB),
                             shade(cable_tris, CABLE_RGB)])
    ax.add_collection3d(Poly3DCollection(tris, facecolors=colors,
                                         edgecolors="none", zsort="average"))
    xyz = np.array(nodes)
    half = max(xyz.max(0) - xyz.min(0)) / 2.0
    cx, cy, cz = (xyz.max(0) + xyz.min(0)) / 2.0
    half *= 1.06
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)
    ax.set_zlim(cz - half, cz + half)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=22, azim=-50)
    ax.set_axis_off()


old_nodes, old_struts, old_cables = legacy_cuboctahedron(scale=18.0)
old_hub = len(old_nodes) - 1
rim_cables = [c for c in old_cables if old_hub not in c]
new_nodes, new_struts, new_cables = cuboctahedron_tessellation(scale=60.0)
new_strut_r, new_cable_r = RADIUS_OVERRIDES["cuboctahedron_tessellation.stl"]

panels = [
    (old_nodes, old_struts, old_cables, 2.5, 1.2),
    (old_nodes, old_struts, [], 2.5, 1.2),
    (old_nodes, [], rim_cables, 2.5, 1.2),
    (new_nodes, new_struts, new_cables, new_strut_r, new_cable_r),
]

fig = plt.figure(figsize=(24, 6), facecolor="white")
for k, (nodes, struts, cables, strut_r, cable_r) in enumerate(panels):
    ax = fig.add_subplot(1, 4, k + 1, projection="3d", facecolor="white")
    draw(ax, nodes, struts, cables, strut_r, cable_r)
fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0, wspace=0.0)
out = os.path.join(REPO_ROOT, "figures",
                   "cuboctahedron_tessellation_diagnostic.png")
fig.savefig(out, dpi=130)
print("wrote", out)
