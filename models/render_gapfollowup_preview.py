"""Render a 4-panel preview of the gap-followup tensegrity families.

Used to produce ``figures/tensegrity_models_gapfollowup_preview.png``
for the 4 new design families added in response to the gap-followup
Edison literature survey (task ``6226a551``): Snelson planar
X-module, Pugh diamond column, Pugh zig-zag column, and the
Rhode-Barbarigos pentagonal tensegrity-ring.

Run from the repository root::

    python models/render_gapfollowup_preview.py
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "models"))
from generate_stl import (  # noqa: E402
    snelson_x_module, pugh_diamond_column, pugh_zigzag_column,
    pentagonal_tensegrity_ring,
)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401, E402
from mpl_toolkits.mplot3d.art3d import Line3DCollection  # noqa: E402
import numpy as np  # noqa: E402


def draw(ax, nodes, struts, cables, title):
    nodes = np.array(nodes)
    sxyz = [(nodes[a], nodes[b]) for a, b in struts]
    cxyz = [(nodes[a], nodes[b]) for a, b in cables]
    if sxyz:
        ax.add_collection3d(Line3DCollection(sxyz, colors="#c0392b", linewidths=3.5))
    if cxyz:
        ax.add_collection3d(Line3DCollection(cxyz, colors="#2980b9", linewidths=1.2, alpha=0.9))
    ax.scatter(nodes[:, 0], nodes[:, 1], nodes[:, 2], s=12, c="k", depthshade=False)
    xs, ys, zs = nodes[:, 0], nodes[:, 1], nodes[:, 2]
    mx = max(xs.max() - xs.min(), ys.max() - ys.min(), zs.max() - zs.min()) / 2.0
    cx, cy, cz = (xs.max() + xs.min()) / 2, (ys.max() + ys.min()) / 2, (zs.max() + zs.min()) / 2
    ax.set_xlim(cx - mx, cx + mx)
    ax.set_ylim(cy - mx, cy + mx)
    ax.set_zlim(cz - mx, cz + mx)
    ax.set_box_aspect((1, 1, 1))
    ax.set_title(title, fontsize=10)
    ax.set_axis_off()


panels = [
    ("Snelson planar X-module\n(4 nodes / 2 struts / 4 cables)", snelson_x_module(scale=60.0, separation=6.0)),
    ("Pugh diamond column (3-bay T3)\n(12 / 9 / 30)", pugh_diamond_column(n=3, bays=3, radius=20.0, bay_height=40.0)),
    ("Pugh zig-zag column (3-bay T3)\n(12 / 9 / 21)", pugh_zigzag_column(n=3, bays=3, radius=20.0, bay_height=40.0)),
    ("Pentagonal tensegrity-ring\n(Rhode-Barbarigos 2010, simplified; 10 / 5 / 15)",
     pentagonal_tensegrity_ring(n_sides=5, radius=30.0, height=20.0)),
]

fig = plt.figure(figsize=(13, 12))
for i, (title, (nodes, struts, cables)) in enumerate(panels, start=1):
    ax = fig.add_subplot(2, 2, i, projection="3d")
    draw(ax, nodes, struts, cables, title)
fig.suptitle("Tensegrity design-family gap follow-up (Edison task 6226a551)",
             fontsize=13, y=0.995)
fig.tight_layout()
out = os.path.join(REPO_ROOT, "figures", "tensegrity_models_gapfollowup_preview.png")
fig.savefig(out, dpi=130, bbox_inches="tight")
print("wrote", out)
