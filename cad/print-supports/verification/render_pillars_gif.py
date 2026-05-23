#!/usr/bin/env python3
"""Render a rotating GIF of the combined part+pillars STL for visual review.

Reads `t3-prism-pr35-with-pillars.stl` (or any merged STL where the first N
triangles are the printable part and the trailing M triangles are the
pillars produced by ``generate_support_pillars.py``) and writes an animated
GIF that spins the scene through 360° of azimuth, so a reviewer can
verify every pillar tip actually lands on the part underside without
having to open the STL in a 3-D viewer.

Default inputs/outputs match the PR #35 T3-prism artefacts committed in
this directory:

    python3 render_pillars_gif.py

Override with --combined / --pillars / --out to render any other pair.
"""
from __future__ import annotations
import argparse
import io
import struct
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402
from PIL import Image  # noqa: E402

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
                    default=HERE / "t3-prism-pr35-pillars-rotating.gif")
    ap.add_argument("--frames", type=int, default=36)
    ap.add_argument("--duration_ms", type=int, default=80)
    ap.add_argument("--elev", type=float, default=18.0)
    ap.add_argument("--stride", type=int, default=2,
                    help="downsample triangles by this stride for render speed")
    ap.add_argument("--title", type=str,
                    default="PR #35 T3-prism + ray-cast narrowing pillars")
    args = ap.parse_args()

    combined = read_binary_stl(args.combined)
    pillars = read_binary_stl(args.pillars)
    n_pillar = len(pillars)
    n_part = len(combined) - n_pillar
    if n_part <= 0:
        raise SystemExit(
            f"--combined ({len(combined)} tris) must contain at least one "
            f"more triangle than --pillars ({n_pillar} tris)")
    part_tris = combined[:n_part][::args.stride]
    pillar_tris = combined[n_part:][::args.stride]
    print(f"part tris: {n_part} (rendering {len(part_tris)})")
    print(f"pillar tris: {n_pillar} (rendering {len(pillar_tris)})")

    pts = combined.reshape(-1, 3)
    lo = pts.min(axis=0)
    hi = pts.max(axis=0)
    cx, cy, cz = (lo + hi) / 2
    r = float((hi - lo).max() / 2 * 1.05)

    frames = []
    for i in range(args.frames):
        az = i * 360.0 / args.frames
        fig = plt.figure(figsize=(5, 5), dpi=90)
        ax = fig.add_subplot(111, projection="3d")
        ax.add_collection3d(Poly3DCollection(
            part_tris, facecolor="lightgrey", edgecolor="none", alpha=0.55))
        ax.add_collection3d(Poly3DCollection(
            pillar_tris, facecolor="darkorange", edgecolor="none", alpha=0.95))
        ax.set_xlim(cx - r, cx + r)
        ax.set_ylim(cy - r, cy + r)
        ax.set_zlim(cz - r, cz + r)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=args.elev, azim=az)
        ax.set_axis_off()
        ax.set_title(args.title, fontsize=9)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)
        buf.seek(0)
        frames.append(Image.open(buf).convert("P", palette=Image.ADAPTIVE))
        print(f"  frame {i + 1}/{args.frames}", flush=True)

    frames[0].save(args.out, save_all=True, append_images=frames[1:],
                   duration=args.duration_ms, loop=0, optimize=True, disposal=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
