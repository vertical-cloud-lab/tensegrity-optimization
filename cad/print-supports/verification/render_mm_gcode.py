#!/usr/bin/env python3
"""Render a Bambu Studio multi-material gcode coloured by extruder.

Tracks the active extruder via BambuStudio's ``M1020 S{0,1}`` toolchange
markers (also identified by ``; toolchange #N`` comments). Filament 1
(extruder T0) is drawn in PLA green, filament 2 (T1) in TPU light blue.
Prime-tower / wipe-tower extrusions are filtered out of the iso view so they
don't obscure the actual print.

Usage:
    render_mm_gcode.py <input.gcode> <output.png> [--title "..."]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

EXTRUDER_COLOR = {
    0: "#00AE42",   # PLA – BambuStudio green
    1: "#76D9F4",   # TPU – light blue
}
EXTRUDER_NAME = {0: "PLA (T0)", 1: "TPU (T1)"}

# Features we never want to draw in the iso / bottom views (they make a thick
# block in the middle of the plate and hide the actual part).
SKIP_FEATURES = {"Prime tower", "Wipe tower", "Custom"}

re_g = re.compile(r"^G[01]\b")
re_xy = re.compile(r"\b([XYZEF])(-?(?:\d+\.?\d*|\.\d+))")
re_feature = re.compile(r"^;\s*(?:TYPE|FEATURE)\s*:\s*(.*)$")
re_layer_height = re.compile(r"^;\s*layer_height\s*=\s*([\d.]+)")
re_toolchange = re.compile(r"^M1020\s+S(\d+)")
re_filament_decl = re.compile(r"^;\s*filament:\s*([0-9,]+)")


def parse(path: Path):
    x = y = z = 0.0
    e_prev = 0.0
    feature = "Custom"
    extruder = 0
    layer_height: float | None = None
    filaments: list[int] = []
    segs_xyz: list[tuple[float, float, float, float, float, float]] = []
    segs_ext: list[int] = []
    segs_feat: list[str] = []
    with path.open() as f:
        for line in f:
            if line.startswith(";"):
                m = re_feature.match(line)
                if m:
                    feature = m.group(1).strip()
                    continue
                m = re_layer_height.match(line)
                if m and layer_height is None:
                    layer_height = float(m.group(1))
                    continue
                m = re_filament_decl.match(line)
                if m and not filaments:
                    filaments = [int(s) for s in m.group(1).split(",") if s.strip()]
                    continue
                continue
            m = re_toolchange.match(line)
            if m:
                extruder = int(m.group(1))
                continue
            if not re_g.match(line):
                continue
            kv = dict(re_xy.findall(line))
            nx = float(kv.get("X", x))
            ny = float(kv.get("Y", y))
            nz = float(kv.get("Z", z))
            e = float(kv.get("E", e_prev))
            if "E" in kv and e > e_prev and (nx != x or ny != y):
                segs_xyz.append((x, y, z, nx, ny, nz))
                segs_ext.append(extruder)
                segs_feat.append(feature)
            x, y, z = nx, ny, nz
            e_prev = e if "E" in kv else e_prev
    return (
        np.array(segs_xyz, dtype=float),
        np.array(segs_ext, dtype=int),
        np.array(segs_feat, dtype=object),
        layer_height,
        filaments,
    )


def subsample(mask: np.ndarray, max_n: int) -> np.ndarray:
    idx = np.where(mask)[0]
    if len(idx) > max_n:
        idx = idx[np.linspace(0, len(idx) - 1, max_n).astype(int)]
    return idx


def draw(ax, arr, mask, color, lw, alpha):
    for i in mask:
        x0, y0, z0, x1, y1, z1 = arr[i]
        if ax.name == "3d":
            ax.plot([x0, x1], [y0, y1], [z0, z1], color=color, lw=lw, alpha=alpha)
        else:
            ax.plot([x0, x1], [y0, y1], color=color, lw=lw, alpha=alpha)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("gcode", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--title", default=None)
    ap.add_argument("--max-segments-per-channel", type=int, default=12000,
                    help="Subsample limit per (extruder, panel) to keep render time bounded.")
    args = ap.parse_args()

    arr, ext, feat, layer_height, filaments = parse(args.gcode)
    print(f"parsed {len(arr)} extrusion segments from {args.gcode}", file=sys.stderr)
    print(f"  filaments declared in header: {filaments}", file=sys.stderr)
    for k in (0, 1):
        n = int((ext == k).sum())
        print(f"  extruder {k} ({EXTRUDER_NAME[k]}): {n}", file=sys.stderr)

    keep = ~np.isin(feat, list(SKIP_FEATURES))
    pla = (ext == 0) & keep
    tpu = (ext == 1) & keep

    fig = plt.figure(figsize=(16, 6.5))

    # Panel 1: bottom view (XY) – everything except prime tower
    ax1 = fig.add_subplot(1, 3, 1)
    ax1.set_aspect("equal")
    ax1.set_title("Bottom view — coloured by extruder\n"
                  "green = PLA (struts + pillars on T0), blue = TPU (cables on T1)",
                  fontsize=10)
    for mask, color, lw in [
        (pla, EXTRUDER_COLOR[0], 0.35),
        (tpu, EXTRUDER_COLOR[1], 0.55),
    ]:
        for i in subsample(mask, args.max_segments_per_channel):
            x0, y0, _, x1, y1, _ = arr[i]
            ax1.plot([x0, x1], [y0, y1], color=color, lw=lw, alpha=0.75)
    ax1.set_xlabel("X (mm)")
    ax1.set_ylabel("Y (mm)")
    ax1.grid(True, alpha=0.3)

    # Panel 2: iso view of object + pillars + cables
    ax2 = fig.add_subplot(1, 3, 2, projection="3d")
    ax2.set_title("Iso — PLA (green) struts + pillars, TPU (blue) cables\n"
                  "pillars taper up to each member's underside",
                  fontsize=10)
    for mask, color, lw, alpha in [
        (pla, EXTRUDER_COLOR[0], 0.4, 0.8),
        (tpu, EXTRUDER_COLOR[1], 0.55, 0.95),
    ]:
        draw(ax2, arr, subsample(mask, args.max_segments_per_channel), color, lw, alpha)
    ax2.set_xlabel("X (mm)")
    ax2.set_ylabel("Y (mm)")
    ax2.set_zlabel("Z (mm)")
    ax2.view_init(elev=18, azim=-60)

    # Panel 3: first-layer (z below 1.25 * layer_height) – shows pillar bases
    ax3 = fig.add_subplot(1, 3, 3)
    ax3.set_aspect("equal")
    lh = layer_height if layer_height else 0.20
    first_thresh = 1.25 * lh
    ax3.set_title(f"First layer (z ≤ {first_thresh:.2f} mm)\n"
                  "PLA pillar bases land directly on the bed",
                  fontsize=10)
    first = arr[:, 2] <= first_thresh
    for mask, color, lw in [
        (pla & first, EXTRUDER_COLOR[0], 0.55),
        (tpu & first, EXTRUDER_COLOR[1], 0.55),
    ]:
        for i in subsample(mask, args.max_segments_per_channel):
            x0, y0, _, x1, y1, _ = arr[i]
            ax3.plot([x0, x1], [y0, y1], color=color, lw=lw, alpha=0.85)
    ax3.set_xlabel("X (mm)")
    ax3.set_ylabel("Y (mm)")
    ax3.grid(True, alpha=0.3)

    zmax = float(arr[:, [2, 5]].max()) if len(arr) else 0.0
    n_layers = int(round(zmax / lh)) + 1
    n_tool = int(((np.diff(ext)) != 0).sum())
    title = args.title or (
        f"{args.gcode.name} — multi-material PLA + TPU via the patched "
        f"vertical-cloud-lab/BambuStudio CLI\n"
        f"{len(arr):,} extrusion segments • {n_layers} layers @ {lh:.2f} mm • "
        f"{n_tool} toolchanges • PLA={int(pla.sum()):,} segs, "
        f"TPU={int(tpu.sum()):,} segs")
    fig.suptitle(title, fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(args.out, dpi=160, bbox_inches="tight")
    print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
