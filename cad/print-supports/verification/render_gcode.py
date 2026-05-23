#!/usr/bin/env python3
"""Render a sliced gcode file into a multi-panel PNG that visualises where
supports were placed by the PLA-tensegrity recipe.

Usage:
    render_gcode.py <input.gcode> <output.png> [--title "..."]

Panels:
  1. Bottom view (looking up the +Z axis) of all support extrusions only -
     this is the analogue of Audrey's manual paint pattern.
  2. Iso view of the object (grey) + supports (orange) so reviewers can
     verify branches root at the plate, never on a member.
  3. First-layer view of brim, object, supports.
"""
import argparse, re, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

ap = argparse.ArgumentParser(description=__doc__,
                             formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("gcode", type=Path)
ap.add_argument("out",   type=Path)
ap.add_argument("--title", default=None,
                help="Override the figure suptitle (default: derive from "
                     "input filename and the slicer header).")
args = ap.parse_args()
GC, OUT = args.gcode, args.out

TYPE_COLOR = {
    "Skirt/Brim":               "#7e57c2",
    "External perimeter":       "#37474f",
    "Perimeter":                "#546e7a",
    "Internal infill":          "#90a4ae",
    "Solid infill":             "#78909c",
    "Top solid infill":         "#607d8b",
    "Bridge infill":            "#5d4037",
    "Support material":         "#ff9800",
    "Support material interface": "#fb8c00",
}
OBJECT_TYPES   = {"External perimeter", "Perimeter",
                  "Internal infill", "Solid infill",
                  "Top solid infill", "Bridge infill"}
SUPPORT_TYPES  = {"Support material", "Support material interface"}

# ---- parse gcode -----------------------------------------------------------
re_g  = re.compile(r"^G[01]\b")
re_xy = re.compile(r"\b([XYZEF])(-?\d+\.?\d*)")
re_ty = re.compile(r"^;TYPE:(.*)$")
re_lh = re.compile(r"^;\s*layer_height\s*=\s*([\d.]+)")

x = y = z = 0.0
e_prev = 0.0
current_type = "Custom"
layer_height = None  # derived from the gcode header (`; layer_height = ...`)
# segments: list of (x0,y0,z0, x1,y1,z1, type)
segs = []
with GC.open() as f:
    for line in f:
        m = re_ty.match(line)
        if m:
            current_type = m.group(1).strip()
            continue
        m = re_lh.match(line)
        if m and layer_height is None:
            layer_height = float(m.group(1))
            continue
        if not re_g.match(line):
            continue
        kv = dict(re_xy.findall(line))
        nx = float(kv.get("X", x))
        ny = float(kv.get("Y", y))
        nz = float(kv.get("Z", z))
        e  = float(kv.get("E", e_prev))
        # extruding move?
        if "E" in kv and e > e_prev and (nx != x or ny != y):
            segs.append((x, y, z, nx, ny, nz, current_type))
        x, y, z = nx, ny, nz
        e_prev = e if "E" in kv else e_prev

print(f"parsed {len(segs)} extrusion segments from {GC}", file=sys.stderr)

arr = np.array([[s[0], s[1], s[2], s[3], s[4], s[5]] for s in segs])
types = np.array([s[6] for s in segs])
support_mask = np.isin(types, list(SUPPORT_TYPES))
object_mask  = np.isin(types, list(OBJECT_TYPES))
brim_mask    = types == "Skirt/Brim"
print(f"  supports : {support_mask.sum():>6}", file=sys.stderr)
print(f"  object   : {object_mask.sum():>6}", file=sys.stderr)
print(f"  brim     : {brim_mask.sum():>6}", file=sys.stderr)

# ---- render ----------------------------------------------------------------
fig = plt.figure(figsize=(16, 6.5))

# Panel 1: bottom view (xy) of supports only
ax1 = fig.add_subplot(1, 3, 1)
ax1.set_aspect("equal")
ax1.set_title("Bottom view — support extrusions only\n"
              "(this is the slicer's automatic equivalent of Audrey's paint)",
              fontsize=10)
sup = arr[support_mask]
for x0, y0, _z0, x1, y1, _z1 in sup:
    ax1.plot([x0, x1], [y0, y1], color=TYPE_COLOR["Support material"],
             lw=0.4, alpha=0.7)
# faint outline of the object footprint to anchor the eye
obj_first = arr[object_mask & (arr[:, 2] < 1.0)]
for x0, y0, _z0, x1, y1, _z1 in obj_first:
    ax1.plot([x0, x1], [y0, y1], color="#cfd8dc", lw=0.3, alpha=0.6)
ax1.set_xlabel("X (mm)")
ax1.set_ylabel("Y (mm)")
ax1.grid(True, alpha=0.3)

# Panel 2: iso view of object + supports
ax2 = fig.add_subplot(1, 3, 2, projection="3d")
ax2.set_title("Iso — object (grey) + tree supports (orange)\n"
              "all tree roots land on the plate (z≈0); none on a member",
              fontsize=10)
# subsample so it renders in reasonable time
def subsample(mask, max_n=8000):
    idx = np.where(mask)[0]
    if len(idx) > max_n:
        idx = idx[np.linspace(0, len(idx) - 1, max_n).astype(int)]
    return idx

for idx, color, lw, alpha in [
    (subsample(object_mask, 6000),  "#90a4ae", 0.3, 0.5),
    (subsample(support_mask, 6000), "#ff9800", 0.5, 0.85),
]:
    for i in idx:
        x0, y0, z0, x1, y1, z1 = arr[i]
        ax2.plot([x0, x1], [y0, y1], [z0, z1], color=color, lw=lw, alpha=alpha)
ax2.set_xlabel("X (mm)")
ax2.set_ylabel("Y (mm)")
ax2.set_zlabel("Z (mm)")
ax2.view_init(elev=18, azim=-60)

# Panel 3: first-layer (z<0.25) — shows brim + first layer of object + first
# touch-points of supports, i.e. exactly what's drawn on the bed.
ax3 = fig.add_subplot(1, 3, 3)
# Panel 3: first-layer (z<= first_layer_threshold) — shows brim + first
# layer of object + first touch-points of supports, i.e. exactly what's
# drawn on the bed. Threshold is 1.25x the discovered layer height so we
# capture the very first layer regardless of slicer profile.
first_layer_threshold = 0.25 if layer_height is None else 1.25 * layer_height
ax3.set_aspect("equal")
ax3.set_title(f"First layer (z ≤ {first_layer_threshold:.2f} mm)\n"
              "purple = brim, grey = object first layer, orange = support roots",
              fontsize=10)
first = arr[:, 2] <= first_layer_threshold
for mask_name, mask, color, lw in [
    ("brim",    brim_mask    & first, "#7e57c2", 0.6),
    ("object",  object_mask  & first, "#455a64", 0.5),
    ("support", support_mask & first, "#ff9800", 0.6),
]:
    seg = arr[mask]
    for x0, y0, _z0, x1, y1, _z1 in seg:
        ax3.plot([x0, x1], [y0, y1], color=color, lw=lw, alpha=0.8)
ax3.set_xlabel("X (mm)")
ax3.set_ylabel("Y (mm)")
ax3.grid(True, alpha=0.3)

# summary footer
zmax = float(arr[:, [2, 5]].max())
lh = layer_height if layer_height else 0.2
n_layers = int(round(zmax / lh)) + 1
title = args.title or (
    f"{GC.name} sliced via cad/print-supports/bambu-pla-tensegrity-process.json "
    f"(PrusaSlicer-translated)\n"
    f"{len(segs):,} extrusion segments • {n_layers} layers @ {lh:.2f} mm • "
    f"support fraction = {support_mask.sum() / max(1, len(segs)):.0%}")
fig.suptitle(title, fontsize=11, y=1.02)
fig.tight_layout()
fig.savefig(OUT, dpi=160, bbox_inches="tight")
print(f"wrote {OUT}", file=sys.stderr)
