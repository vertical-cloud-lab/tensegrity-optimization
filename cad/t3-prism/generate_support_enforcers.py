#!/usr/bin/env python3
# ============================================================================
# Generate "Support Enforcer" STL volumes for the T3-prism, automating the
# manual support-painting protocol that @achris0520 documented in
# https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/40
# (Audrey's manual-slice .3mf attachment, sliced with
# `support_type = tree(manual)`).
#
# Audrey's painting recipe (reproduced verbatim from the issue):
#   "From the BOTTOM VIEW of the part, paint supports manually onto the
#    members along each member's center axis, only about a third the
#    thickness of the projected view of each member so that when generated,
#    the supports only lightly touch the bottom of the members. Do not paint
#    supports where members begin to overlap at each vertex, except for the
#    three vertices that directly touch the build plate. Only those three
#    vertices should be connected to each other in a triangular fashion by
#    painted supports."
#
# This script emits an STL containing a small set of vertical rectangular
# prisms (one per painted stripe), rising from the build plate (z = 0) up
# past the highest point of each painted member. When the user imports the
# STL into Bambu Studio as `Part Modifier -> Support Enforcer` on the
# t3-prism assembly, BambuStudio's tree(auto)/tree(manual) generator places
# support touch-points only inside those volumes -- functionally identical
# to the manual paint, but parametric and repeatable.
#
# Usage (defaults match cad/t3-prism/t3-prism.scad at scale_factor = 1.5):
#   python3 cad/t3-prism/generate_support_enforcers.py \
#       --out cad/t3-prism/t3-prism-support-enforcers.stl
#
# Then in Bambu Studio:
#   1) Load your t3-prism assembly (struts + cables) on plate 1.
#   2) Right-click the assembly -> Add Part -> Load... ->
#      t3-prism-support-enforcers.stl
#   3) Right-click the new sub-part -> Change Type -> Support Enforcer.
#   4) Verify enable_support = 1, support_type = tree(manual),
#      support_on_build_plate_only = 1 (matches Audrey's slice).
#   5) Slice. Supports will appear only inside the enforcer volumes.
# ============================================================================
from __future__ import annotations

import argparse
import math
import struct
from pathlib import Path

import numpy as np

# ---- Geometry parameters (mm / degrees) -----------------------------------
# Defaults match cad/t3-prism/t3-prism.scad at scale_factor = 1.5, which is
# the scale Audrey's manual-paint screenshot was taken at (assembly
# bounding box ~68.7 x 110.0 x 57.1 mm per plate_1.json in the gcode.3mf).
DEFAULTS = dict(
    R=25.0 * 1.5,         # circumscribing radius of each end triangle
    H=70.0 * 1.5,         # bottom-to-top triangle plane distance
    twist=60.0,           # top-triangle rotation about z (deg)
    strut_d=6.0 * 1.5,    # PLA strut diameter
    cable_d=3.0 * 1.5,    # TPU cable diameter
    joint_d=7.0 * 1.5,    # joint-sphere diameter at each vertex
    # Painted stripe width as a fraction of the member's projected diameter
    # ("about a third the thickness of the projected view of each member").
    stripe_frac=1.0 / 3.0,
    # How far to trim each stripe back from its endpoints to avoid the
    # vertex-overlap zone ("do not paint supports where members begin to
    # overlap at each vertex"). Expressed as a multiplier of joint radius;
    # at 1.0 the stripe ends exactly at the joint-sphere boundary.
    trim_joint_radii=1.0,
    # Z-headroom above the highest endpoint of each painted member: the
    # enforcer needs to extend above the member so the slicer can drop
    # support touch-points onto its underside.
    z_headroom=2.0,
    # Bottom-vertex triangle enforcer width (mm). Audrey paints a small
    # triangular connector between the three bed-contact vertices on top
    # of the bottom-cable stripes; we slightly widen the bottom-cable
    # stripe to capture both at once when this flag is on.
    bottom_triangle_extra_w=0.0,
)


# ---- Vertex positions ------------------------------------------------------
def bottom_pt(i: int, R: float) -> np.ndarray:
    return np.array(
        [R * math.cos(math.radians(90 + 120 * i)),
         R * math.sin(math.radians(90 + 120 * i)),
         0.0])


def top_pt(i: int, R: float, H: float, twist: float) -> np.ndarray:
    return np.array(
        [R * math.cos(math.radians(90 + 120 * i + twist)),
         R * math.sin(math.radians(90 + 120 * i + twist)),
         H])


def members(p: dict) -> list[tuple[str, np.ndarray, np.ndarray, float, bool]]:
    """Return (label, p1, p2, member_d, is_bottom_triangle) for all 12
    members of the T3-prism. The `is_bottom_triangle` flag marks the three
    bottom-triangle cables, which are NOT trimmed at the vertex overlaps
    (per Audrey's exception for the three bed-contact vertices)."""
    R, H, t = p["R"], p["H"], p["twist"]
    sd, cd = p["strut_d"], p["cable_d"]
    B = [bottom_pt(i, R) for i in range(3)]
    T = [top_pt(i, R, H, t) for i in range(3)]
    out: list[tuple[str, np.ndarray, np.ndarray, float, bool]] = []
    # 3 struts B_i -> T_i
    for i in range(3):
        out.append((f"strut_{i}", B[i], T[i], sd, False))
    # 3 bottom-triangle cables B_i -> B_{(i+1) % 3}  (bed contact -> bed contact)
    for i in range(3):
        out.append((f"cable_bot_{i}", B[i], B[(i + 1) % 3], cd, True))
    # 3 top-triangle cables T_i -> T_{(i+1) % 3}
    for i in range(3):
        out.append((f"cable_top_{i}", T[i], T[(i + 1) % 3], cd, False))
    # 3 saddle cables B_i -> T_{(i + 2) % 3}  (matches t3-prism.scad)
    for i in range(3):
        out.append((f"cable_saddle_{i}", B[i], T[(i + 2) % 3], cd, False))
    return out


# ---- Painted-stripe -> rectangular prism ----------------------------------
def stripe_prism(p1: np.ndarray, p2: np.ndarray, width: float,
                 trim: float, z_headroom: float) -> np.ndarray | None:
    """Project a member onto the XY plane, shrink each end by `trim`, then
    sweep the resulting 1D segment into a 2D rectangle of given `width`
    (centred on the projected axis), and finally extrude it vertically from
    z = 0 up to z = max(p1.z, p2.z) + z_headroom. Returns the 8 corner
    vertices as a (8, 3) array, ordered as [bottom_quad..., top_quad...]
    with each quad in CCW order viewed from +z. Returns None if the
    projected segment is shorter than 2*trim (i.e. trimmed away)."""
    a2, b2 = p1[:2].copy(), p2[:2].copy()
    axis = b2 - a2
    L = float(np.linalg.norm(axis))
    if L < 1e-9 or L <= 2 * trim:
        return None
    u = axis / L
    n = np.array([-u[1], u[0]])  # XY-perpendicular, unit
    a2t = a2 + u * trim
    b2t = b2 - u * trim
    hw = width / 2.0
    c0 = a2t - n * hw
    c1 = b2t - n * hw
    c2 = b2t + n * hw
    c3 = a2t + n * hw
    z0 = 0.0
    z1 = float(max(p1[2], p2[2])) + z_headroom
    return np.array(
        [[c0[0], c0[1], z0],
         [c1[0], c1[1], z0],
         [c2[0], c2[1], z0],
         [c3[0], c3[1], z0],
         [c0[0], c0[1], z1],
         [c1[0], c1[1], z1],
         [c2[0], c2[1], z1],
         [c3[0], c3[1], z1]])


def box_triangles(v: np.ndarray) -> list[tuple[np.ndarray, ...]]:
    """Tessellate an 8-vertex rectangular prism (vertex order matches the
    output of `stripe_prism`) into 12 outward-facing triangles."""
    b0, b1, b2, b3, t0, t1, t2, t3 = (v[i] for i in range(8))
    return [
        # bottom (z = z0), facing -z
        (b0, b2, b1), (b0, b3, b2),
        # top (z = z1), facing +z
        (t0, t1, t2), (t0, t2, t3),
        # side 0-1 (between b0-b1 and t1-t0)
        (b0, b1, t1), (b0, t1, t0),
        # side 1-2
        (b1, b2, t2), (b1, t2, t1),
        # side 2-3
        (b2, b3, t3), (b2, t3, t2),
        # side 3-0
        (b3, b0, t0), (b3, t0, t3),
    ]


# ---- Binary STL writer ----------------------------------------------------
def write_binary_stl(triangles: list[tuple[np.ndarray, ...]],
                     out_path: Path) -> None:
    header = b"t3-prism support enforcer (generate_support_enforcers.py)"
    header = header.ljust(80, b" ")[:80]
    with out_path.open("wb") as f:
        f.write(header)
        f.write(struct.pack("<I", len(triangles)))
        for tri in triangles:
            v0, v1, v2 = tri
            normal = np.cross(v1 - v0, v2 - v0)
            nrm = float(np.linalg.norm(normal))
            n = (normal / nrm) if nrm > 0 else np.zeros(3)
            f.write(struct.pack("<3f", *n))
            f.write(struct.pack("<3f", *v0))
            f.write(struct.pack("<3f", *v1))
            f.write(struct.pack("<3f", *v2))
            f.write(struct.pack("<H", 0))


# ---- Top-level driver -----------------------------------------------------
def generate(params: dict, out_stl: Path,
             preview_png: Path | None = None) -> dict:
    p = dict(DEFAULTS)
    p.update(params)
    joint_r = p["joint_d"] / 2.0

    triangles: list[tuple[np.ndarray, ...]] = []
    stripes_emitted = 0
    stripes_skipped = 0
    stripe_records: list[dict] = []

    for label, p1, p2, member_d, is_bot in members(p):
        width = member_d * p["stripe_frac"]
        if is_bot:
            # Bottom-triangle cables are NOT trimmed at the vertex overlaps
            # (the three bed-contact vertices must be connected in a
            # triangular fashion per Audrey's exception).
            trim = 0.0
            width += p["bottom_triangle_extra_w"]
        else:
            # All other members trim back from each end by the joint
            # radius so the painted stripe ends just outside the vertex
            # sphere ("do not paint supports where members begin to
            # overlap at each vertex").
            trim = joint_r * p["trim_joint_radii"]

        prism = stripe_prism(p1, p2, width, trim, p["z_headroom"])
        if prism is None:
            stripes_skipped += 1
            continue
        triangles.extend(box_triangles(prism))
        stripes_emitted += 1
        stripe_records.append(dict(label=label, width=width, trim=trim,
                                   p1=p1.tolist(), p2=p2.tolist()))

    out_stl.parent.mkdir(parents=True, exist_ok=True)
    write_binary_stl(triangles, out_stl)

    info = dict(
        out_stl=str(out_stl),
        triangles=len(triangles),
        stripes_emitted=stripes_emitted,
        stripes_skipped=stripes_skipped,
        params=p,
        stripes=stripe_records,
    )

    if preview_png is not None:
        _render_preview(stripe_records, p, preview_png)
        info["preview_png"] = str(preview_png)
    return info


def _render_preview(stripes: list[dict], p: dict, out_png: Path) -> None:
    # Bottom-view (looking up the +z axis at the painted XY projection) so
    # the rendered figure visually matches Audrey's screenshot.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    from matplotlib.collections import PatchCollection

    fig, ax = plt.subplots(figsize=(6.5, 6.5))

    # Draw the projected member centerlines first (gray) for context.
    for label, p1, p2, d, _ in members(p):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                color=(0.55, 0.6, 0.65), lw=d * 2.0, alpha=0.35,
                solid_capstyle="round", zorder=1)

    # Overlay the emitted enforcer stripes (purple, mimicking the
    # BambuStudio paint-support highlight colour in the screenshot).
    patches = []
    for s in stripes:
        p1 = np.array(s["p1"][:2])
        p2 = np.array(s["p2"][:2])
        axis = p2 - p1
        L = float(np.linalg.norm(axis))
        if L < 1e-9:
            continue
        u = axis / L
        n = np.array([-u[1], u[0]])
        trim = s["trim"]
        a, b = p1 + u * trim, p2 - u * trim
        hw = s["width"] / 2.0
        poly = np.array([a - n * hw, b - n * hw, b + n * hw, a + n * hw])
        patches.append(Polygon(poly, closed=True))
    ax.add_collection(PatchCollection(
        patches, facecolor=(0.55, 0.45, 0.85, 0.92),
        edgecolor=(0.30, 0.20, 0.55, 1.0), linewidths=0.4, zorder=3))

    R = p["R"]
    lim = R * 1.4
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_title("T3-prism support enforcers (bottom view)\n"
                 f"{len(stripes)} stripes  ·  stripe width = "
                 f"member_d × {p['stripe_frac']:.2f}  ·  "
                 f"vertex trim = {p['trim_joint_radii']:.2f} × joint_r")
    ax.grid(True, alpha=0.25)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path,
                    default=Path("cad/t3-prism/t3-prism-support-enforcers.stl"),
                    help="Output STL path (binary STL).")
    ap.add_argument("--preview", type=Path,
                    default=Path("cad/t3-prism/t3-prism-support-enforcers.png"),
                    help="Bottom-view PNG preview path.")
    ap.add_argument("--no-preview", action="store_true",
                    help="Skip the PNG preview.")
    for k, v in DEFAULTS.items():
        ap.add_argument(f"--{k}", type=type(v), default=v,
                        help=f"(default {v})")
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    params = {k: getattr(args, k) for k in DEFAULTS}
    preview = None if args.no_preview else args.preview
    info = generate(params, args.out, preview)
    print(f"Wrote {info['out_stl']}")
    print(f"  triangles       : {info['triangles']}")
    print(f"  stripes emitted : {info['stripes_emitted']}")
    print(f"  stripes skipped : {info['stripes_skipped']}")
    if "preview_png" in info:
        print(f"  preview         : {info['preview_png']}")


if __name__ == "__main__":
    main()
