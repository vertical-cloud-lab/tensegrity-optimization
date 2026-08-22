#!/usr/bin/env python3
# ============================================================================
# Render a sliced Bambu `.gcode.3mf` (or raw `plate_1.gcode`) into a 3D PNG
# that visually proves whether supports were generated natively by the slicer.
#
# Supports/Support-interface extrusion moves are color-coded distinctly from
# model moves, so the reviewer can see the tree(auto) scaffolding next to the
# T3-prism geometry. Used to answer PR #35 comment 4462414588 (verify supports
# exist in the slicer's g-code, not just in the project settings).
#
# Usage:
#   python3 render_supports.py <slice.gcode.3mf|plate_1.gcode> <out.png> [title]
#
# Categories (from BambuStudio `; FEATURE: <name>` markers):
#   * Support           — tree/normal support bodies
#   * Support interface — top/bottom touchpoint layers
#   * (everything else) — model walls, infill, bridges, etc. (downsampled)
# ============================================================================
import os
import re
import sys
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Line3DCollection


def load_gcode(src: str) -> str:
    if src.endswith(".3mf"):
        with zipfile.ZipFile(src) as z:
            with z.open("Metadata/plate_1.gcode") as f:
                return f.read().decode("utf-8", errors="replace")
    with open(src, "r", errors="replace") as f:
        return f.read()


def parse_segments(gcode: str):
    """Return (model_segs, support_segs, iface_segs) lists of
    ((x0,y0,z0),(x1,y1,z1)) tuples for every extrusion move."""
    g_re = re.compile(r"^G[0123]\b")
    num_re = re.compile(r"([XYZEFIJ])(-?\d*\.?\d+)")
    feat_re = re.compile(r"^;\s*FEATURE:\s*(.+?)\s*$")

    x = y = z = 0.0
    abs_xyz = True
    feat = "Custom"
    model, support, iface = [], [], []

    for line in gcode.splitlines():
        if line.startswith(";"):
            m = feat_re.match(line)
            if m:
                feat = m.group(1)
            continue
        if line.startswith("G90"):
            abs_xyz = True
            continue
        if line.startswith("G91"):
            abs_xyz = False
            continue
        if not g_re.match(line):
            continue
        nx, ny, nz, e = x, y, z, None
        for tag, val in num_re.findall(line):
            v = float(val)
            if tag == "X":
                nx = v if abs_xyz else x + v
            elif tag == "Y":
                ny = v if abs_xyz else y + v
            elif tag == "Z":
                nz = v if abs_xyz else z + v
            elif tag == "E":
                e = v
        if e is not None and e > 0 and (nx != x or ny != y):
            seg = ((x, y, z), (nx, ny, nz))
            if feat == "Support":
                support.append(seg)
            elif feat == "Support interface":
                iface.append(seg)
            else:
                model.append(seg)
        x, y, z = nx, ny, nz
    return model, support, iface


def downsample(segs, max_n):
    if len(segs) <= max_n:
        return segs
    idx = np.linspace(0, len(segs) - 1, max_n).astype(int)
    return [segs[i] for i in idx]


def render(src: str, out: str, title: str | None = None) -> None:
    gcode = load_gcode(src)
    model, support, iface = parse_segments(gcode)
    print(
        f"Parsed {src}: model={len(model)}, support={len(support)}, "
        f"support-interface={len(iface)}"
    )

    model_color = (0.55, 0.65, 0.78, 0.35)
    support_color = (0.95, 0.20, 0.20, 0.95)
    iface_color = (1.0, 0.55, 0.0, 0.95)

    # Dense multi-specimen plates need more model segments before the
    # structures read as anything but haze; `RS_MODEL_MAX` raises the cap.
    model_ds = downsample(model, int(os.environ.get("RS_MODEL_MAX", "40000")))

    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_subplot(111, projection="3d")
    if model_ds:
        ax.add_collection3d(
            Line3DCollection(
                model_ds, colors=[model_color] * len(model_ds), linewidths=0.4
            )
        )
    if support:
        ax.add_collection3d(
            Line3DCollection(
                support, colors=[support_color] * len(support), linewidths=0.7
            )
        )
    if iface:
        ax.add_collection3d(
            Line3DCollection(
                iface, colors=[iface_color] * len(iface), linewidths=0.9
            )
        )

    allpts = np.array(
        [p for s in (model_ds + support + iface) for p in s]
    )
    if len(allpts):
        mn, mx = allpts.min(0), allpts.max(0)
        ctr = (mn + mx) / 2
        span = mx - mn
        half = span[:2].max() / 2 * 1.05
        ax.set_xlim(ctr[0] - half, ctr[0] + half)
        ax.set_ylim(ctr[1] - half, ctr[1] + half)
        # Scale Z to the part height instead of forcing a cube: on a full
        # 350 mm plate a square box aspect spends most of the frame on air.
        ax.set_zlim(max(0, mn[2]), mn[2] + max(span[2], 1e-6) * 1.05)
        ax.set_box_aspect((1, 1, max(span[2] / max(span[:2].max(), 1e-6), 0.15)))
    else:
        ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.set_title(
        f"{title or os.path.basename(src)}\n"
        f"model segs (gray) · support segs (red) · support-interface (orange)\n"
        f"support extrusion moves: {len(support) + len(iface)} of "
        f"{len(support) + len(iface) + len(model)}"
    )
    elev, azim = (
        float(v) for v in os.environ.get("RS_VIEW", "22,-58").split(",")
    )
    ax.view_init(elev=elev, azim=azim)
    ax.legend(
        handles=[
            Line2D([0], [0], color=model_color, lw=2,
                   label=f"Model ({len(model)} segs)"),
            Line2D([0], [0], color=support_color, lw=2,
                   label=f"Support ({len(support)})"),
            Line2D([0], [0], color=iface_color, lw=2,
                   label=f"Support interface ({len(iface)})"),
        ],
        loc="upper left",
    )
    plt.tight_layout()
    plt.savefig(out, dpi=140, bbox_inches="tight")
    print(f"Saved {out}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    title = sys.argv[3] if len(sys.argv) > 3 else None
    render(sys.argv[1], sys.argv[2], title)
