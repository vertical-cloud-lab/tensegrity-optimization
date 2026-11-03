#!/usr/bin/env python3
"""Render the static iso + bottom-view preview of the part+pillars STL.

Companion still image to ``render_pillars_gif.py`` (same scene/colours), used
to regenerate ``t3-prism-pr35-pillars-preview.png``. The left panel is an
isometric view; the right panel looks straight up from the build plate
(elev = -90) so every support tip is visible against the part underside —
the view that matters for confirming the supports actually reach the members.

    python3 render_pillars_preview.py

Override with --combined / --pillars / --out to render any other pair.
"""
from __future__ import annotations
import argparse
import struct
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

HERE = Path(__file__).resolve().parent


def read_binary_stl(path: Path) -> np.ndarray:
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        raw = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
    return np.frombuffer(raw[:, 12:48].tobytes(), dtype="<f4").reshape(n, 3, 3)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--combined", type=Path,
                    default=HERE / "t3-prism-pr35-with-pillars.stl")
    ap.add_argument("--pillars", type=Path,
                    default=HERE / "t3-prism-pr35-pillars.stl")
    ap.add_argument("--out", type=Path,
                    default=HERE / "t3-prism-pr35-pillars-preview.png")
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--title", type=str,
                    default="PR #35 T3-prism + ray-cast narrowing pillars "
                            "(grey = part, orange = supports)")
    args = ap.parse_args()

    combined = read_binary_stl(args.combined)
    pillars = read_binary_stl(args.pillars)
    n_pillar = len(pillars)
    n_part = len(combined) - n_pillar
    if n_part <= 0:
        raise SystemExit("--combined must contain more triangles than --pillars")
    part_tris = combined[:n_part][::args.stride]
    pillar_tris = combined[n_part:][::args.stride]

    pts = combined.reshape(-1, 3)
    lo = pts.min(axis=0)
    hi = pts.max(axis=0)
    cx, cy, cz = (lo + hi) / 2
    r = float((hi - lo).max() / 2 * 1.05)

    views = [("isometric", 22, -60), ("bottom (build-plate view)", -89, -90)]
    fig = plt.figure(figsize=(11, 5.5), dpi=110)
    for k, (name, elev, az) in enumerate(views):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d")
        ax.add_collection3d(Poly3DCollection(
            part_tris, facecolor="lightgrey", edgecolor="none", alpha=0.5))
        ax.add_collection3d(Poly3DCollection(
            pillar_tris, facecolor="darkorange", edgecolor="none", alpha=0.95))
        ax.set_xlim(cx - r, cx + r)
        ax.set_ylim(cy - r, cy + r)
        ax.set_zlim(cz - r, cz + r)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=elev, azim=az)
        ax.set_axis_off()
        ax.set_title(name, fontsize=10)
    fig.suptitle(args.title, fontsize=11)
    fig.tight_layout()
    fig.savefig(args.out, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(f"wrote {args.out}  (part {n_part} tris, pillars {n_pillar} tris)")


if __name__ == "__main__":
    main()
