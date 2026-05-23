#!/usr/bin/env python3
"""Side-by-side comparison of two sliced .gcode files (old θ=40 vs new θ=10).

Shows where the lower threshold added supports along the bottom of every
near-vertical strut. Two panels (bottom-view, supports-only) and a
difference panel highlighting the *added* support touch-points only.
"""
import re, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OLD, NEW, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
SUPPORT_TYPES = {"Support material", "Support material interface"}

re_g  = re.compile(r"^G[01]\b")
re_xy = re.compile(r"\b([XYZEF])(-?\d+\.?\d*)")
re_ty = re.compile(r"^;TYPE:(.*)$")

def parse_supports(path):
    """Return Nx6 array of support-extrusion segments (x0,y0,z0,x1,y1,z1)."""
    x = y = z = 0.0
    e_prev = 0.0
    current_type = "Custom"
    segs = []
    with open(path) as f:
        for line in f:
            m = re_ty.match(line)
            if m:
                current_type = m.group(1).strip()
                continue
            if not re_g.match(line):
                continue
            kv = dict(re_xy.findall(line))
            nx = float(kv.get("X", x))
            ny = float(kv.get("Y", y))
            nz = float(kv.get("Z", z))
            e = float(kv.get("E", e_prev))
            if ("E" in kv and e > e_prev and (nx != x or ny != y)
                    and current_type in SUPPORT_TYPES):
                segs.append((x, y, z, nx, ny, nz))
            x, y, z = nx, ny, nz
            e_prev = e if "E" in kv else e_prev
    return np.array(segs)

old = parse_supports(OLD)
new = parse_supports(NEW)
print(f"old supports: {len(old):>6} segments", file=sys.stderr)
print(f"new supports: {len(new):>6} segments", file=sys.stderr)

# crude difference: bin old support midpoints onto a 1 mm grid and flag
# every new segment whose midpoint falls in an empty bin (i.e., the new
# threshold added support coverage there).
def midpoints(a):
    return np.column_stack([(a[:, 0] + a[:, 3]) / 2,
                            (a[:, 1] + a[:, 4]) / 2,
                            (a[:, 2] + a[:, 5]) / 2])

cell = 1.0  # mm
old_mid = midpoints(old)
new_mid = midpoints(new)
old_keys = {tuple(int(v) for v in p) for p in (old_mid / cell)}
added_mask = np.array([tuple(int(v) for v in p) not in old_keys
                       for p in (new_mid / cell)])
added = new[added_mask]
print(f"added (new∖old): {added_mask.sum():>6} segments", file=sys.stderr)

fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))

def plot_bottom(ax, segs, color, title):
    ax.set_aspect("equal")
    for x0, y0, _z0, x1, y1, _z1 in segs:
        ax.plot([x0, x1], [y0, y1], color=color, lw=0.4, alpha=0.65)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.grid(True, alpha=0.3)

plot_bottom(axes[0], old, "#ff9800",
            f"BEFORE — support_threshold_angle = 40°\n"
            f"{len(old):,} support extrusion segments (PLA-only safe)")
plot_bottom(axes[1], new, "#ff9800",
            f"AFTER — support_threshold_angle = 10°\n"
            f"{len(new):,} support extrusion segments (TPU-safe)")
# Difference: faint NEW background + bright ADDED overlay
axes[2].set_aspect("equal")
for x0, y0, _z0, x1, y1, _z1 in new:
    axes[2].plot([x0, x1], [y0, y1], color="#cfd8dc", lw=0.3, alpha=0.5)
for x0, y0, _z0, x1, y1, _z1 in added:
    axes[2].plot([x0, x1], [y0, y1], color="#d81b60", lw=0.4, alpha=0.8)
axes[2].set_title(f"DIFFERENCE — added by θ=10° (pink)\n"
                  f"{added_mask.sum():,} new segments along strut bottoms "
                  f"(+{100 * added_mask.sum() / max(1, len(old)):.0f}%)",
                  fontsize=10)
axes[2].set_xlabel("X (mm)")
axes[2].set_ylabel("Y (mm)")
axes[2].grid(True, alpha=0.3)

fig.suptitle("PR #35 T3-prism — effect of support_threshold_angle 40° → 10°\n"
             "on the §B PLA recipe (same mesh, same recipe, only θ changed)",
             fontsize=11, y=1.02)
fig.tight_layout()
fig.savefig(OUT, dpi=160, bbox_inches="tight")
print(f"wrote {OUT}", file=sys.stderr)
