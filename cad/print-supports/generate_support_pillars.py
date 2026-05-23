#!/usr/bin/env python3
# ============================================================================
# Manual narrowing-pillar support generator for FDM tensegrity prints.
#
# Why this exists
# ---------------
# Bambu Studio's automatic tree generator cannot place supports under
# perfectly vertical surfaces (a vertical cable has no down-facing geometry
# for the overhang analyser to flag), and "Support Enforcer" volumes only
# help if the slicer's tree generator is willing to root branches under them
# — which is unreliable on tensegrity geometries where the enforcer column
# is taller than the tree generator's branch-stretch budget. After several
# round-trips trying to coax the slicer into doing this automatically, the
# project chose to **bake the supports directly into the printable mesh**:
#
#   * From a bottom view, drop a narrowing pillar from the build plate up
#     to the underside of each non-bed-contact member at evenly-spaced
#     sample points.
#   * The pillar is a tapered cone: a wide breakaway base on the plate
#     (default Ø 5 mm) narrowing to a small tip (default Ø 0.6 mm) that
#     fuses into the member's underside.
#   * The slicer then prints the pillars as part of the object (no
#     `enable_support` flag needed) and the operator snaps them off after
#     printing using the narrow tip as the breakaway notch.
#
# This is the geometric equivalent of the manual paint protocol Audrey
# documented in https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/40
# but expressed as real geometry rather than as a paint flag, so it works
# on TPU vertical members where the slicer's overhang analyser is
# physically incapable of placing supports.
#
# Usage
# -----
#   # built-in topology preset (T3 prism with explicit geometry knobs)
#   python3 generate_support_pillars.py --topology t3_prism \
#       --R 37.5 --H 105 --twist 60 --strut_d 9 --cable_d 4.5 \
#       --out pillars.stl
#
#   # arbitrary structure described by a members.json file
#   python3 generate_support_pillars.py --members my_members.json \
#       --out pillars.stl
#
# where ``my_members.json`` is, e.g.::
#
#   [
#     {"p1":[0,0,0],   "p2":[0,0,70],  "d":9.0, "trim_ends": true},
#     {"p1":[10,0,0],  "p2":[20,0,0],  "d":4.5, "trim_ends": false},
#     ...
#   ]
#
# ``trim_ends: false`` flags a bed-contact member (e.g. the three bottom
# cables of a T3 prism); those are skipped entirely because they already
# touch the plate and don't need a pillar.
#
# Then merge the pillar STL with your printable part STL into one mesh
# (e.g. via :mod:`verification/merge_stls`) and slice the combined STL in
# Bambu Studio with **supports turned OFF** — the pillars print as part of
# the part.
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
# Same shape as in :mod:`generate_support_enforcers` so the same
# members.json files / topology presets feed both generators.
Member = tuple[np.ndarray, np.ndarray, float, bool]


# ---- Topology presets (canonical tensegrity structures from PR #22) -------
def t3_prism(R: float, H: float, twist: float, strut_d: float,
             cable_d: float) -> list[Member]:
    """Snelson 3-bar T3 prism: 3 struts, 3 bottom (bed-contact) cables, 3
    top cables, 3 saddle cables. Bed-contact cables carry
    ``trim_ends=False`` and are skipped by the pillar generator."""
    B = [np.array([R * math.cos(math.radians(90 + 120 * i)),
                   R * math.sin(math.radians(90 + 120 * i)), 0.0])
         for i in range(3)]
    T = [np.array([R * math.cos(math.radians(90 + 120 * i + twist)),
                   R * math.sin(math.radians(90 + 120 * i + twist)), H])
         for i in range(3)]
    members: list[Member] = []
    for i in range(3):
        members.append((B[i], T[i], strut_d, True))             # strut
    for i in range(3):
        members.append((B[i], B[(i + 1) % 3], cable_d, False))  # bottom cable
    for i in range(3):
        members.append((T[i], T[(i + 1) % 3], cable_d, True))   # top cable
    for i in range(3):
        members.append((B[i], T[(i + 2) % 3], cable_d, True))   # saddle
    return members


def prism_n(n: int, R: float, H: float, twist: float, strut_d: float,
            cable_d: float) -> list[Member]:
    """n-bar generalised prism (4-bar, 6-bar, ...)."""
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
    """Load a list of members from JSON. Same schema as
    :mod:`generate_support_enforcers.load_members_json`."""
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


# ---- Pillar geometry ------------------------------------------------------
def _faceted_cone(base_xy: np.ndarray, base_r: float, top_xy: np.ndarray,
                  top_r: float, base_z: float, top_z: float,
                  facets: int) -> list[tuple[np.ndarray, ...]]:
    """Faceted truncated cone (frustum) with a flat circular cap at each
    end. The base is centred on ``(base_xy, base_z)`` with radius
    ``base_r``; the top is centred on ``(top_xy, top_z)`` with radius
    ``top_r``. Returns a list of outward-facing CCW triangles.

    For a typical narrowing pillar the base sits on the build plate
    (``base_z = 0``) with ``base_r`` wide enough to print stably, and the
    top sits at the member's underside (``top_z = z_centerline - d/2``)
    with ``top_r`` small enough to snap off cleanly.
    """
    angles = np.linspace(0.0, 2.0 * math.pi, facets, endpoint=False)
    cos_a = np.cos(angles)
    sin_a = np.sin(angles)
    bx, by = float(base_xy[0]), float(base_xy[1])
    tx, ty = float(top_xy[0]), float(top_xy[1])

    base_ring = [
        np.array([bx + base_r * cos_a[i], by + base_r * sin_a[i], base_z])
        for i in range(facets)
    ]
    top_ring = [
        np.array([tx + top_r * cos_a[i], ty + top_r * sin_a[i], top_z])
        for i in range(facets)
    ]
    base_centre = np.array([bx, by, base_z])
    top_centre = np.array([tx, ty, top_z])

    tris: list[tuple[np.ndarray, ...]] = []
    for i in range(facets):
        j = (i + 1) % facets
        # Side quad (base[i] -> base[j] -> top[j] -> top[i]) → 2 tris,
        # outward CCW when viewed from outside the cone.
        tris.append((base_ring[i], base_ring[j], top_ring[j]))
        tris.append((base_ring[i], top_ring[j], top_ring[i]))
        # Bottom cap (faces -z, so winding seen from below is CCW).
        tris.append((base_centre, base_ring[j], base_ring[i]))
        # Top cap (faces +z, CCW seen from above).
        tris.append((top_centre, top_ring[i], top_ring[j]))
    return tris


def member_pillars(p1: np.ndarray, p2: np.ndarray, d: float,
                   trim_ends: bool, *, spacing: float, end_trim: float,
                   base_d: float, tip_d: float, base_z: float,
                   tip_overshoot: float,
                   facets: int) -> list[tuple[np.ndarray, ...]]:
    """Emit narrowing pillars along one member.

    Sample points are uniformly spaced along the 3D centerline at
    ``spacing`` mm, starting / ending ``end_trim`` mm in from each
    endpoint when ``trim_ends`` is True (to avoid colliding with the
    joint sphere at each node). For each sample point the centerline
    coordinate is ``c = p1 + t * (p2 - p1)``; the pillar drops straight
    down from ``(c.x, c.y, c.z - d/2 + tip_overshoot)`` (i.e. just inside
    the member's underside so the fused boolean is watertight after
    slicing) to ``(c.x, c.y, base_z)`` (the build plate).
    """
    axis = p2 - p1
    L = float(np.linalg.norm(axis))
    if L < 1e-9:
        return []
    # Effective span after trimming back from each endpoint.
    t_lo_dist = end_trim if trim_ends else 0.0
    t_hi_dist = L - (end_trim if trim_ends else 0.0)
    if t_hi_dist - t_lo_dist <= 0.0:
        return []
    # Number of pillars so that they are roughly uniformly spaced at
    # ``spacing`` mm and there is always at least one (under the centre
    # of the member) for very short spans.
    span = t_hi_dist - t_lo_dist
    n_pillars = max(1, int(round(span / spacing)))
    if n_pillars == 1:
        ts = np.array([0.5 * (t_lo_dist + t_hi_dist)])
    else:
        ts = np.linspace(t_lo_dist, t_hi_dist, n_pillars)

    tris: list[tuple[np.ndarray, ...]] = []
    base_r = base_d / 2.0
    tip_r = tip_d / 2.0
    member_r = d / 2.0
    for t_along in ts:
        frac = t_along / L
        c = p1 + frac * axis  # centerline point at this sample
        # Pillar top sits just inside the underside of the member so the
        # boolean union after slicing is watertight. ``tip_overshoot``
        # buries the tip ``tip_overshoot`` mm inside the cylinder.
        top_z = float(c[2] - member_r + tip_overshoot)
        if top_z <= base_z + 1e-6:
            # Member's underside is at or below the plate (a strut that
            # contacts the bed): a pillar would have zero / negative
            # height. Skip.
            continue
        top_xy = c[:2]
        base_xy = c[:2]
        tris.extend(_faceted_cone(base_xy, base_r, top_xy, tip_r,
                                  base_z, top_z, facets))
    return tris


# ---- Binary STL writer ----------------------------------------------------
def write_binary_stl(triangles: Iterable[tuple[np.ndarray, ...]],
                     out_path: Path) -> int:
    triangles = list(triangles)
    header = b"tensegrity narrowing pillars (generate_support_pillars.py)"
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
def generate(members: list[Member], out_stl: Path, *,
             spacing: float, end_trim: float,
             base_d: float, tip_d: float, base_z: float,
             tip_overshoot: float, facets: int,
             skip_bed_contact: bool) -> dict:
    triangles: list[tuple[np.ndarray, ...]] = []
    pillar_count = 0
    members_pillared = 0
    members_skipped = 0
    for p1, p2, d, trim_ends in members:
        # By convention (matching generate_support_enforcers.py),
        # `trim_ends=False` flags bed-contact members like the bottom-
        # triangle cables of a T3 prism. Those already sit at z=0 and
        # don't need a pillar.
        if skip_bed_contact and not trim_ends:
            members_skipped += 1
            continue
        tris = member_pillars(
            p1, p2, d, trim_ends, spacing=spacing, end_trim=end_trim,
            base_d=base_d, tip_d=tip_d, base_z=base_z,
            tip_overshoot=tip_overshoot, facets=facets,
        )
        if not tris:
            members_skipped += 1
            continue
        n_p = len(tris) // (4 * facets)
        pillar_count += n_p
        members_pillared += 1
        triangles.extend(tris)
    n_tris = write_binary_stl(triangles, out_stl)
    return dict(out_stl=str(out_stl), triangles=n_tris,
                pillars=pillar_count, members_pillared=members_pillared,
                members_skipped=members_skipped)


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
    # Pillar-shape knobs
    ap.add_argument("--spacing", type=float, default=8.0,
                    help="Spacing (mm) between adjacent pillars along a "
                         "member's centerline (default 8.0).")
    ap.add_argument("--end_trim", type=float, default=3.5,
                    help="Skip sample points within this many mm of each "
                         "endpoint of a `trim_ends=True` member (default "
                         "3.5 mm ~= one joint-sphere radius for Ø7 mm "
                         "joints).")
    ap.add_argument("--base_d", type=float, default=5.0,
                    help="Pillar base diameter on the build plate (mm). "
                         "Wider = sticks to the plate better. Default 5.")
    ap.add_argument("--tip_d", type=float, default=0.6,
                    help="Pillar tip diameter where it fuses to the "
                         "member's underside (mm). Smaller = easier to "
                         "snap off, but ~2x nozzle width or it will not "
                         "print. Default 0.6 (1.5x a 0.4 mm nozzle).")
    ap.add_argument("--base_z", type=float, default=0.0,
                    help="Z height of the build plate (mm). Default 0.0.")
    ap.add_argument("--tip_overshoot", type=float, default=0.3,
                    help="Bury the pillar tip this many mm inside the "
                         "member so the boolean union is watertight after "
                         "slicing. Default 0.3.")
    ap.add_argument("--facets", type=int, default=12,
                    help="Number of sides on the faceted cone (default "
                         "12; higher = rounder + more triangles).")
    ap.add_argument("--include_bed_contact", action="store_true",
                    help="Also emit pillars under members marked "
                         "`trim_ends=False` (bed-contact cables). Off by "
                         "default since those already touch the plate.")
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
    info = generate(
        members, args.out,
        spacing=args.spacing, end_trim=args.end_trim,
        base_d=args.base_d, tip_d=args.tip_d, base_z=args.base_z,
        tip_overshoot=args.tip_overshoot, facets=args.facets,
        skip_bed_contact=not args.include_bed_contact,
    )
    print(f"Wrote {info['out_stl']}", file=sys.stderr)
    print(f"  triangles         : {info['triangles']:,}", file=sys.stderr)
    print(f"  pillars emitted   : {info['pillars']}", file=sys.stderr)
    print(f"  members pillared  : {info['members_pillared']}", file=sys.stderr)
    print(f"  members skipped   : {info['members_skipped']}", file=sys.stderr)


if __name__ == "__main__":
    main()
