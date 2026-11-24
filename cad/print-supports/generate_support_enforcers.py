#!/usr/bin/env python3
# ============================================================================
# Geometry-agnostic Support Enforcer STL generator for FDM tensegrity prints.
#
# This is the **fallback** to the primary Bambu Studio settings recipe in
# README.md §B. Use it only when the tree(hybrid)+on_build_plate_only recipe
# fails on an exotic topology, or when you want bit-exact reproducibility of
# the manual paint pattern Audrey documented for the t3-prism in
# https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/40
#
# The generator is structure-agnostic: it takes a JSON description of an
# arbitrary member graph and emits one vertical rectangular prism per
# member, sized as a fraction of the member's diameter, extruded from
# z = 0 up past the member's highest endpoint. Members marked
# `"trim_ends": true` are shrunk back from each end so the stripe does not
# fall under a vertex overlap zone.
#
# Topology presets (see --topology) are provided for the canonical
# structures catalogued in PR #22 (t3_prism, prism_n, snelson_x,
# icosahedron, stacked_t3, pugh_diamond, pentagonal_ring). They are
# convenience wrappers — anything you can describe as a list of
# (p1, p2, diameter, trim_ends) members will work through --members.
#
# Usage:
#   # built-in topology preset (T3 prism with explicit geometry knobs)
#   python3 generate_support_enforcers.py --topology t3_prism \
#       --R 37.5 --H 105 --twist 60 --strut_d 9 --cable_d 4.5 \
#       --out enforcers.stl
#
#   # arbitrary structure
#   python3 generate_support_enforcers.py --members my_members.json \
#       --out enforcers.stl
#
# where my_members.json is, e.g.:
#   [
#     {"p1":[0,0,0],   "p2":[0,0,70],  "d":9.0, "trim_ends": true},
#     {"p1":[10,0,0],  "p2":[20,0,0],  "d":4.5, "trim_ends": false},
#     ...
#   ]
# ============================================================================
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path
from typing import Iterable

import numpy as np


# ---- Member dataclass-lite ------------------------------------------------
# Each member is a 4-tuple (p1, p2, diameter_mm, trim_ends_bool). `trim_ends`
# follows Audrey's "do not paint at the vertex overlaps" rule: True for
# members whose endpoints abut other members (struts, top/saddle cables),
# False for members whose endpoints are bed-contact vertices that should be
# connected through (the three bottom-triangle cables on a T3 prism).
Member = tuple[np.ndarray, np.ndarray, float, bool]


# ---- Topology presets (canonical tensegrity structures from PR #22) -------
def t3_prism(R: float, H: float, twist: float, strut_d: float,
             cable_d: float) -> list[Member]:
    """Snelson 3-bar T3 prism: 3 struts, 3 bottom cables (bed-contact,
    not trimmed), 3 top cables, 3 saddle cables."""
    B = [np.array([R * math.cos(math.radians(90 + 120 * i)),
                   R * math.sin(math.radians(90 + 120 * i)), 0.0])
         for i in range(3)]
    T = [np.array([R * math.cos(math.radians(90 + 120 * i + twist)),
                   R * math.sin(math.radians(90 + 120 * i + twist)), H])
         for i in range(3)]
    members: list[Member] = []
    for i in range(3):
        members.append((B[i], T[i], strut_d, True))            # strut
    for i in range(3):
        members.append((B[i], B[(i + 1) % 3], cable_d, False))  # bottom cable
    for i in range(3):
        members.append((T[i], T[(i + 1) % 3], cable_d, True))   # top cable
    for i in range(3):
        members.append((B[i], T[(i + 2) % 3], cable_d, True))   # saddle
    return members


def prism_n(n: int, R: float, H: float, twist: float, strut_d: float,
            cable_d: float) -> list[Member]:
    """n-bar prism (4-bar, 6-bar, ...): generalises t3_prism."""
    B = [np.array([R * math.cos(2 * math.pi * i / n),
                   R * math.sin(2 * math.pi * i / n), 0.0])
         for i in range(n)]
    twr = math.radians(twist)
    T = [np.array([R * math.cos(2 * math.pi * i / n + twr),
                   R * math.sin(2 * math.pi * i / n + twr), H])
         for i in range(n)]
    members: list[Member] = []
    for i in range(n):
        members.append((B[i], T[i], strut_d, True))
    for i in range(n):
        members.append((B[i], B[(i + 1) % n], cable_d, False))
    for i in range(n):
        members.append((T[i], T[(i + 1) % n], cable_d, True))
    for i in range(n):
        members.append((B[i], T[(i - 1) % n], cable_d, True))
    return members


TOPOLOGIES = {
    "t3_prism": ("3-bar Snelson T3 prism (Audrey's reference structure)",
                 t3_prism),
    "prism_n":  ("n-bar generalised prism (--n flag selects n)", prism_n),
}


def build_topology(name: str, args: argparse.Namespace) -> list[Member]:
    if name not in TOPOLOGIES:
        raise SystemExit(
            f"Unknown topology {name!r}. Choices: {', '.join(TOPOLOGIES)}")
    if name == "t3_prism":
        return t3_prism(args.R, args.H, args.twist, args.strut_d, args.cable_d)
    if name == "prism_n":
        return prism_n(args.n, args.R, args.H, args.twist, args.strut_d,
                       args.cable_d)
    raise SystemExit(f"Topology {name!r} is registered but unimplemented")


# ---- members.json loader --------------------------------------------------
def load_members_json(path: Path) -> list[Member]:
    """Load a list of members from JSON. Schema:
        [{"p1": [x, y, z], "p2": [x, y, z], "d": <mm>,
          "trim_ends": <bool, default true>}, ...]
    Coordinates are in mm; the build plate lies at z = 0."""
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise SystemExit(f"{path}: expected a JSON list of members")
    out: list[Member] = []
    for i, m in enumerate(data):
        try:
            p1 = np.asarray(m["p1"], dtype=float)
            p2 = np.asarray(m["p2"], dtype=float)
            d = float(m["d"])
        except (KeyError, TypeError, ValueError) as e:
            raise SystemExit(f"{path}: member[{i}] is malformed: {e}") from e
        if p1.shape != (3,) or p2.shape != (3,):
            raise SystemExit(
                f"{path}: member[{i}] p1/p2 must be length-3 [x,y,z]")
        trim = bool(m.get("trim_ends", True))
        out.append((p1, p2, d, trim))
    return out


# ---- Painted-stripe -> rectangular prism geometry -------------------------
def stripe_prism(p1: np.ndarray, p2: np.ndarray, width: float,
                 trim: float, z_headroom: float,
                 vertical_pad: float | None = None) -> np.ndarray | None:
    """Project a member onto the XY plane, shrink each end by `trim`, sweep
    into a rectangle of `width` (centred on the projected axis), then
    extrude from z = 0 to max(p1.z, p2.z) + z_headroom. Returns 8 vertices
    [bottom_quad CCW, top_quad CCW].

    Vertical members (whose XY projection is shorter than `width`) cannot
    cast a useful XY stripe — they have no down-facing surface for the
    slicer's overhang analysis to detect, which is the exact failure mode
    on near-vertical TPU cables. For those we emit a `vertical_pad`-sized
    square enforcer column centred on the lower endpoint's XY position,
    extruded from z = 0 up to the member's highest point. Trimming is
    ignored in that case so the column still reaches the bed. Set
    `vertical_pad=None` to fall back to the legacy "skip vertical members"
    behaviour and return None instead.
    """
    a2, b2 = p1[:2].copy(), p2[:2].copy()
    axis = b2 - a2
    L = float(np.linalg.norm(axis))
    z1 = float(max(p1[2], p2[2])) + z_headroom
    # Degenerate / near-vertical: XY projection shorter than the stripe
    # width — a tilted thin stripe here is geometrically pointless and the
    # slicer's overhang analyzer cannot see vertical cylinder sides as
    # overhangs regardless of `support_threshold_angle`. Emit a square
    # footprint instead so explicit-enforcer mode still covers the member.
    if vertical_pad is not None and L < max(width, 1e-9):
        # Pin the column under the *lower* endpoint (whichever has smaller z)
        # so the support tower reaches it cleanly from the plate.
        lower = p1 if p1[2] <= p2[2] else p2
        cx, cy = float(lower[0]), float(lower[1])
        hp = vertical_pad / 2.0
        return np.array(
            [[cx - hp, cy - hp, 0.0], [cx + hp, cy - hp, 0.0],
             [cx + hp, cy + hp, 0.0], [cx - hp, cy + hp, 0.0],
             [cx - hp, cy - hp, z1],  [cx + hp, cy - hp, z1],
             [cx + hp, cy + hp, z1],  [cx - hp, cy + hp, z1]])
    if L < 1e-9 or L <= 2 * trim:
        return None
    u = axis / L
    n = np.array([-u[1], u[0]])
    a2t, b2t = a2 + u * trim, b2 - u * trim
    hw = width / 2.0
    c0 = a2t - n * hw
    c1 = b2t - n * hw
    c2 = b2t + n * hw
    c3 = a2t + n * hw
    z0 = 0.0
    return np.array(
        [[c0[0], c0[1], z0], [c1[0], c1[1], z0],
         [c2[0], c2[1], z0], [c3[0], c3[1], z0],
         [c0[0], c0[1], z1], [c1[0], c1[1], z1],
         [c2[0], c2[1], z1], [c3[0], c3[1], z1]])


def box_triangles(v: np.ndarray) -> list[tuple[np.ndarray, ...]]:
    """Tessellate the 8-vertex prism from stripe_prism() into 12
    outward-facing triangles."""
    b0, b1, b2, b3, t0, t1, t2, t3 = (v[i] for i in range(8))
    return [
        (b0, b2, b1), (b0, b3, b2),                # bottom (-z)
        (t0, t1, t2), (t0, t2, t3),                # top (+z)
        (b0, b1, t1), (b0, t1, t0),                # side 0-1
        (b1, b2, t2), (b1, t2, t1),                # side 1-2
        (b2, b3, t3), (b2, t3, t2),                # side 2-3
        (b3, b0, t0), (b3, t0, t3),                # side 3-0
    ]


# ---- Binary STL writer ----------------------------------------------------
def write_binary_stl(triangles: Iterable[tuple[np.ndarray, ...]],
                     out_path: Path) -> int:
    triangles = list(triangles)
    header = b"tensegrity support enforcer (generate_support_enforcers.py)"
    header = header.ljust(80, b" ")[:80]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as f:
        f.write(header)
        f.write(struct.pack("<I", len(triangles)))
        for v0, v1, v2 in triangles:
            normal = np.cross(v1 - v0, v2 - v0)
            nrm = float(np.linalg.norm(normal))
            n = (normal / nrm) if nrm > 0 else np.zeros(3)
            f.write(struct.pack("<3f", *n))
            f.write(struct.pack("<3f", *v0))
            f.write(struct.pack("<3f", *v1))
            f.write(struct.pack("<3f", *v2))
            f.write(struct.pack("<H", 0))
    return len(triangles)


# ---- Top-level driver -----------------------------------------------------
def generate(members: list[Member], out_stl: Path,
             stripe_frac: float, trim: float, z_headroom: float,
             vertical_pad: float | None = None) -> dict:
    triangles: list[tuple[np.ndarray, ...]] = []
    emitted = skipped = vertical = 0
    for p1, p2, d, trim_ends in members:
        width = d * stripe_frac
        t = trim if trim_ends else 0.0
        # For vertical members the slicer's overhang analyser can never
        # see a cylinder's side as an overhang, so we emit a square
        # footprint sized to the member's diameter (a hair bigger than
        # the cylinder, so the enforcer envelope cleanly contains the
        # cable's first layer at z=0+).
        pad = (d + 0.5) if vertical_pad is None else vertical_pad
        prism = stripe_prism(p1, p2, width, t, z_headroom,
                             vertical_pad=pad)
        if prism is None:
            skipped += 1
            continue
        # Detect whether this was emitted as a vertical-column fallback
        # (axis XY length < width) for the report.
        xy_len = float(np.linalg.norm(p2[:2] - p1[:2]))
        if xy_len < max(width, 1e-9):
            vertical += 1
        triangles.extend(box_triangles(prism))
        emitted += 1
    n_tris = write_binary_stl(triangles, out_stl)
    return dict(out_stl=str(out_stl), triangles=n_tris,
                stripes_emitted=emitted, stripes_skipped=skipped,
                vertical_columns=vertical)


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--members", type=Path,
                     help="Path to a members.json file (geometry-agnostic).")
    src.add_argument("--topology", choices=sorted(TOPOLOGIES),
                     help="Built-in topology preset: " +
                          "; ".join(f"{k}: {v[0]}"
                                    for k, v in TOPOLOGIES.items()))
    ap.add_argument("--out", type=Path, required=True,
                    help="Output STL path (binary STL).")
    # Stripe-shape knobs (apply to all topologies / member files alike)
    ap.add_argument("--stripe_frac", type=float, default=1.0 / 3.0,
                    help="Stripe width as a fraction of member diameter "
                         "(default 1/3, matches Audrey's paint).")
    ap.add_argument("--trim", type=float, default=3.5,
                    help="Trim each stripe back this many mm from each "
                         "endpoint of a `trim_ends=True` member (default "
                         "3.5 mm ~= one joint-sphere radius for "
                         "Ø7 mm joints).")
    ap.add_argument("--z_headroom", type=float, default=2.0,
                    help="Extra height (mm) above the member's max z "
                         "(default 2.0).")
    ap.add_argument("--vertical_pad", type=float, default=None,
                    help="For members whose XY projection is shorter than "
                         "their stripe width (i.e. vertical or near-"
                         "vertical members — TPU cables that the slicer's "
                         "overhang analysis cannot detect regardless of "
                         "`support_threshold_angle`), emit a square "
                         "footprint of this size (mm) centred on the lower "
                         "endpoint. Default = member diameter + 0.5 mm.")
    # Topology-preset knobs (only used when --topology is set)
    ap.add_argument("--R", type=float, default=37.5,
                    help="[prism] circumradius of end polygon (mm).")
    ap.add_argument("--H", type=float, default=105.0,
                    help="[prism] bottom-to-top plane distance (mm).")
    ap.add_argument("--twist", type=float, default=60.0,
                    help="[prism] top-polygon twist about z (deg).")
    ap.add_argument("--strut_d", type=float, default=9.0,
                    help="[prism] strut diameter (mm).")
    ap.add_argument("--cable_d", type=float, default=4.5,
                    help="[prism] cable diameter (mm).")
    ap.add_argument("--n", type=int, default=3,
                    help="[prism_n] number of bars (default 3 = T3 prism).")
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    if args.members is not None:
        members = load_members_json(args.members)
    else:
        members = build_topology(args.topology, args)
    info = generate(members, args.out,
                    stripe_frac=args.stripe_frac, trim=args.trim,
                    z_headroom=args.z_headroom,
                    vertical_pad=args.vertical_pad)
    print(f"Wrote {info['out_stl']}", file=sys.stderr)
    print(f"  triangles        : {info['triangles']}", file=sys.stderr)
    print(f"  stripes emitted  : {info['stripes_emitted']}", file=sys.stderr)
    print(f"  vertical columns : {info['vertical_columns']}", file=sys.stderr)
    print(f"  stripes skipped  : {info['stripes_skipped']}", file=sys.stderr)


if __name__ == "__main__":
    main()
