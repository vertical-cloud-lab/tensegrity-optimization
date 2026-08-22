"""Render the Pajunen et al. (2019) spherically-jointed impact cell.

Produces ``figures/pajunen2019_sphere_jointed_shaded.png``: a single
shaded, text-free panel of ``pajunen_sphere_jointed_cell()`` in the same
Lambert-shaded style as ``render_extended_preview_shaded.py`` (red =
struts, blue = cables); the printed ball joints render as gray spheres.

Run from the repository root::

    python models/render_pajunen_cell.py
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "models"))
from generate_stl import (  # noqa: E402
    NODE_SPHERES, RADIUS_OVERRIDES, _cylinder_triangles, _sphere_triangles,
    pajunen_sphere_jointed_cell,
)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import to_rgb  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402
import numpy as np  # noqa: E402

STRUT_RGB = np.array(to_rgb("#c0392b"))
CABLE_RGB = np.array(to_rgb("#2980b9"))
SPHERE_RGB = np.array(to_rgb("#95a5a6"))
LIGHT = np.array([-0.45, 0.35, 0.82])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
AMBIENT, DIFFUSE = 0.32, 0.68
SEGMENTS = 16


def shade(tris, base_rgb):
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    norms = np.linalg.norm(n, axis=1, keepdims=True)
    n = n / np.where(norms == 0.0, 1.0, norms)
    lam = np.abs(n @ LIGHT)
    brightness = AMBIENT + DIFFUSE * lam
    return np.clip(brightness[:, None] * base_rgb[None, :], 0.0, 1.0)


nodes, struts, cables = pajunen_sphere_jointed_cell()
strut_r, cable_r = RADIUS_OVERRIDES["pajunen_spherically_jointed.stl"]
sphere_r = NODE_SPHERES["pajunen_spherically_jointed.stl"]

strut_tris = np.array([t for i, j in struts for t in
                       _cylinder_triangles(nodes[i], nodes[j], strut_r,
                                           segments=SEGMENTS)])
cable_tris = np.array([t for i, j in cables for t in
                       _cylinder_triangles(nodes[i], nodes[j], cable_r,
                                           segments=SEGMENTS)])
sphere_tris = np.array([t for n in nodes for t in
                        _sphere_triangles(n, sphere_r, segments=SEGMENTS)])

tris = np.concatenate([strut_tris, cable_tris, sphere_tris])
colors = np.concatenate([shade(strut_tris, STRUT_RGB),
                         shade(cable_tris, CABLE_RGB),
                         shade(sphere_tris, SPHERE_RGB)])

fig = plt.figure(figsize=(8, 8), facecolor="white")
ax = fig.add_subplot(111, projection="3d", facecolor="white")
coll = Poly3DCollection(tris, facecolors=colors, edgecolors="none",
                        zsort="average")
ax.add_collection3d(coll)
xyz = np.array(nodes)
half = max(xyz.max(0) - xyz.min(0)) / 2.0 + sphere_r + 2.0
cx, cy, cz = (xyz.max(0) + xyz.min(0)) / 2.0
ax.set_xlim(cx - half, cx + half)
ax.set_ylim(cy - half, cy + half)
ax.set_zlim(cz - half, cz + half)
ax.set_box_aspect((1, 1, 1))
ax.view_init(elev=18, azim=-55)
ax.set_axis_off()
fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
out = os.path.join(REPO_ROOT, "figures",
                   "pajunen2019_sphere_jointed_shaded.png")
fig.savefig(out, dpi=160)
print("wrote", out)
