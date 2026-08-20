"""Render a shaded, text-free preview of the 7 extended tensegrity families.

Produces ``figures/tensegrity_models_extended_preview_shaded.png``: the same
seven design families as ``figures/tensegrity_models_extended_preview.png``
(Geiger cable-dome, biotensegrity spine, NASA SUPERball + payload,
Tibert/Pellegrino mast, Knight et al. patent antenna, bistable double-prism,
cuboctahedron tessellation), but rendered as Lambert-shaded solid tubes with
no titles or embedded text. Struts are red, cables are blue, matching the
convention in ``render_gapfollowup_preview.py``.

Run from the repository root::

    python models/render_extended_preview_shaded.py
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "models"))
from generate_stl import (  # noqa: E402
    _cylinder_triangles,
    geiger_cable_dome, biotensegrity_spine, superball_with_payload,
    tibert_pellegrino_mast, patent_us6441801_antenna, bistable_double_prism,
    cuboctahedron_tessellation,
)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import to_rgb  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402
import numpy as np  # noqa: E402

STRUT_RGB = np.array(to_rgb("#c0392b"))
CABLE_RGB = np.array(to_rgb("#2980b9"))
# Key light from upper front-left plus a soft ambient floor, so tube
# curvature reads as a highlight-to-shadow gradient instead of flat fill.
LIGHT = np.array([-0.45, 0.35, 0.82])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
AMBIENT, DIFFUSE = 0.32, 0.68
STRUT_RADIUS, CABLE_RADIUS = 2.5, 1.2  # mm, same as generate_stl.py defaults
SEGMENTS = 16


def member_triangles(nodes, members, radius):
    tris = []
    for i, j in members:
        tris.extend(_cylinder_triangles(nodes[i], nodes[j], radius,
                                        segments=SEGMENTS))
    return np.array(tris)


def shade(tris, base_rgb):
    """Per-face Lambertian brightness applied to a base colour."""
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    norms = np.linalg.norm(n, axis=1, keepdims=True)
    n = n / np.where(norms == 0.0, 1.0, norms)
    # abs() shades back-facing triangles as if front-facing; with painter's
    # depth sorting they can peek through at silhouettes and would otherwise
    # render black.
    lam = np.abs(n @ LIGHT)
    brightness = AMBIENT + DIFFUSE * lam
    return np.clip(brightness[:, None] * base_rgb[None, :], 0.0, 1.0)


def draw(ax, model, elev, azim, member_scale=1.0):
    nodes, struts, cables = model
    strut_tris = member_triangles(nodes, struts, STRUT_RADIUS * member_scale)
    cable_tris = member_triangles(nodes, cables, CABLE_RADIUS * member_scale)
    tris = np.concatenate([strut_tris, cable_tris])
    colors = np.concatenate([shade(strut_tris, STRUT_RGB),
                             shade(cable_tris, CABLE_RGB)])
    # One collection per panel so matplotlib depth-sorts struts and cables
    # against each other instead of drawing whole collections in z-fighting
    # layers.
    coll = Poly3DCollection(tris, facecolors=colors, edgecolors="none",
                            zsort="average")
    ax.add_collection3d(coll)

    xyz = np.array(nodes)
    half = max(xyz.max(0) - xyz.min(0)) / 2.0 + 3.0
    cx, cy, cz = (xyz.max(0) + xyz.min(0)) / 2.0
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)
    ax.set_zlim(cz - half, cz + half)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()


# Same models and parameters as the extended preview / generate_stl.py main().
# member_scale fattens the tubes of the small-strut-count models so line
# weights look comparable across panels of very different physical size.
panels = [
    (geiger_cable_dome(n_radial=12, rings=(60.0, 40.0, 20.0),
                       strut_lengths=(20.0, 25.0, 30.0), apex_height=55.0),
     24, -60, 1.0),
    (biotensegrity_spine(vertebrae=4, scale=12.0, spacing=36.0),
     12, -55, 1.0),
    (superball_with_payload(scale=18.0, payload_scale=6.0),
     18, -50, 1.0),
    (tibert_pellegrino_mast(n=3, bays=6, radius=18.0, bay_height=30.0),
     10, -55, 1.0),
    (patent_us6441801_antenna(n_sides=6, bottom_radius=50.0,
                              top_radius=30.0, height=60.0),
     20, -55, 1.2),
    (bistable_double_prism(radius=25.0, bay_height=45.0),
     16, -55, 1.2),
    (cuboctahedron_tessellation(scale=18.0),
     22, -50, 1.0),
]

fig = plt.figure(figsize=(20, 10), facecolor="white")
# 4 panels on top, 3 centred below (an 8-column grid, each panel 2 wide).
gs = fig.add_gridspec(2, 8)
slots = [gs[0, 0:2], gs[0, 2:4], gs[0, 4:6], gs[0, 6:8],
         gs[1, 1:3], gs[1, 3:5], gs[1, 5:7]]
for slot, (model, elev, azim, member_scale) in zip(slots, panels):
    ax = fig.add_subplot(slot, projection="3d", facecolor="white")
    draw(ax, model, elev, azim, member_scale)
fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0,
                    wspace=0.0, hspace=0.0)
out = os.path.join(REPO_ROOT, "figures",
                   "tensegrity_models_extended_preview_shaded.png")
fig.savefig(out, dpi=140)
print("wrote", out)
