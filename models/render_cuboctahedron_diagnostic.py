"""Render a 3-panel diagnostic of ``cuboctahedron_tessellation()``.

Produces ``figures/cuboctahedron_tessellation_diagnostic.png``, which
decomposes the bottom-right panel of
``figures/tensegrity_models_extended_preview_shaded.png`` into:

1. the model as generated (6 struts + 36 cables),
2. the 6 struts alone, showing that all six are body diagonals of the
   cuboctahedron and therefore all intersect at the origin,
3. the 24 rim cables alone (the cuboctahedron's own edges), which are
   the only part of the model that is geometrically clean.

The 12 remaining cables run from a hub node at the origin out to each
vertex, so each one lies exactly inside the inner half of a strut
(cable radius 1.2 mm inside strut radius 2.5 mm). That co-axial burial
plus the six-way strut intersection is what makes panel 1 read as a
tangle of strands rather than a structure.

Run from the repository root::

    python models/render_cuboctahedron_diagnostic.py
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "models"))
from generate_stl import (  # noqa: E402
    _cylinder_triangles, cuboctahedron_tessellation,
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
STRUT_RADIUS, CABLE_RADIUS = 2.5, 1.2
SEGMENTS = 20


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


def draw(ax, nodes, struts, cables):
    strut_tris = member_triangles(nodes, struts, STRUT_RADIUS)
    cable_tris = member_triangles(nodes, cables, CABLE_RADIUS)
    tris = np.concatenate([strut_tris, cable_tris])
    colors = np.concatenate([shade(strut_tris, STRUT_RGB),
                             shade(cable_tris, CABLE_RGB)])
    ax.add_collection3d(Poly3DCollection(tris, facecolors=colors,
                                         edgecolors="none", zsort="average"))
    xyz = np.array(nodes)
    half = max(xyz.max(0) - xyz.min(0)) / 2.0 + 3.0
    cx, cy, cz = (xyz.max(0) + xyz.min(0)) / 2.0
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)
    ax.set_zlim(cz - half, cz + half)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=22, azim=-50)
    ax.set_axis_off()


nodes, struts, cables = cuboctahedron_tessellation(scale=18.0)
hub = len(nodes) - 1
rim_cables = [c for c in cables if hub not in c]

fig = plt.figure(figsize=(18, 6), facecolor="white")
for k, (s, c) in enumerate([(struts, cables), (struts, []), ([], rim_cables)]):
    ax = fig.add_subplot(1, 3, k + 1, projection="3d", facecolor="white")
    draw(ax, nodes, s, c)
fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0, wspace=0.0)
out = os.path.join(REPO_ROOT, "figures",
                   "cuboctahedron_tessellation_diagnostic.png")
fig.savefig(out, dpi=130)
print("wrote", out)
