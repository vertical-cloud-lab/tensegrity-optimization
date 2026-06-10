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
#     (default Ø 5 mm) narrowing to a small tip (default Ø 0.4 mm) that
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
#   # **recommended for arbitrary STL meshes** — ray-cast the actual
#   # underside of the part from the build-plate's point of view and
#   # grow Bambu-style tree supports (slim breakaway tips merging into a
#   # few thin-branch trunks) up to it. Requires ``trimesh`` (and
#   # optionally ``rtree`` for the spatial index).
#   python3 generate_support_pillars.py --stl part.stl --tree \
#       --out pillars.stl --out_part part_lifted.stl
#
#   # drop --tree for the original one-cone-per-cell pillars (each with
#   # its own wide base on the plate):
#   python3 generate_support_pillars.py --stl part.stl \
#       --out pillars.stl --out_part part_lifted.stl
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


# ---- STL ray-cast mode ----------------------------------------------------
# When the caller has an actual printable STL mesh (rather than a
# parametric topology preset or a hand-authored members.json), the most
# reliable way to figure out where pillars should land is to do exactly
# what the build plate "sees" looking up: cast a vertical ray from below
# the part at each (x, y) sample point, and record the height of the
# **first** triangle the ray hits. That hit point is, by construction,
# the lowest visible point of the mesh directly above (x, y) — i.e. the
# underside surface of whatever member is overhanging that spot.
#
# This is the geometric operation the previous parametric-only pillar
# pass was missing: it sampled along the *centerline* of each declared
# member, which (a) doesn't see joint spheres / end caps / bonded-core
# inserts that bulge below the nominal centerline, and (b) places the
# pillar tip at ``c.z - d/2`` (member underside, idealised as a perfect
# cylinder) even though the actual STL surface at that XY may be at a
# noticeably different z. The result was the visible gaps the PR
# reviewer flagged.
def raycast_underside(stl_path: Path, *, spacing: float,
                      min_clearance: float, base_z: float = 0.0
                      ) -> tuple[list[tuple[float, float, float]],
                                 "object"]:
    """Rasterise the mesh's bottom-view XY footprint at ``spacing`` mm,
    cast a +Z ray from below the part at each grid point, and return
    the list of ``(x, y, hit_z)`` tuples whose nearest hit lies above
    ``base_z + min_clearance``.

    The mesh is also translated in-place so its lowest point sits at
    ``base_z`` (this matches what the slicer does when it lays the
    object on the plate). The translated :class:`trimesh.Trimesh` is
    returned alongside the hit list so the caller can write a lifted
    copy of the part to merge with the pillar STL — that way the part
    and the pillars share a coordinate frame.

    Importing :mod:`trimesh` lazily keeps the topology-preset path
    (which only needs numpy) from carrying a hard dependency.
    """
    try:
        import trimesh
    except ImportError as e:  # pragma: no cover - install hint
        raise SystemExit(
            "--stl mode requires the `trimesh` package "
            "(pip install trimesh). " + str(e))
    mesh = trimesh.load(stl_path, force="mesh")
    if not hasattr(mesh, "ray"):
        raise SystemExit(
            f"{stl_path}: trimesh loaded a non-mesh object "
            f"(type={type(mesh).__name__}); expected a single Trimesh.")
    # Lay the part flat on the (virtual) plate so the pillar Z values we
    # emit match the slicer's print-coordinate frame.
    mesh.apply_translation([0.0, 0.0, base_z - float(mesh.bounds[0, 2])])
    lo_x, lo_y, _ = mesh.bounds[0]
    hi_x, hi_y, _ = mesh.bounds[1]
    xs = np.arange(lo_x, hi_x + spacing * 0.5, spacing)
    ys = np.arange(lo_y, hi_y + spacing * 0.5, spacing)
    XX, YY = np.meshgrid(xs, ys)
    n = XX.size
    # Start each ray a hair below the plate so a face that sits exactly
    # on z=base_z (a bed-contact triangle) still registers a hit and is
    # then filtered out by ``min_clearance``.
    origins = np.column_stack([
        XX.ravel(), YY.ravel(),
        np.full(n, base_z - 1.0),
    ])
    dirs = np.tile(np.array([0.0, 0.0, 1.0]), (n, 1))
    # ``multiple_hits=False`` returns the nearest hit per ray — exactly
    # the build-plate's-eye view of the underside.
    locs, idx_ray, _ = mesh.ray.intersects_location(
        origins, dirs, multiple_hits=False)
    hits: list[tuple[float, float, float]] = []
    z_min = base_z + float(min_clearance)
    for loc, ir in zip(locs, idx_ray):
        z = float(loc[2])
        if z <= z_min:
            continue
        ox = float(origins[ir, 0])
        oy = float(origins[ir, 1])
        hits.append((ox, oy, z))
    return hits, mesh


def write_trimesh_binary_stl(mesh: "object", out_path: Path) -> None:
    """Export a trimesh.Trimesh to a binary STL via the same writer the
    pillar generator uses (no additional dependencies required)."""
    tris = [(mesh.vertices[a], mesh.vertices[b], mesh.vertices[c])
            for a, b, c in mesh.faces]
    write_binary_stl(tris, out_path)


def pillars_from_hits(hits: list[tuple[float, float, float]], *,
                      base_d: float, tip_d: float, base_z: float,
                      tip_overshoot: float, facets: int
                      ) -> list[tuple[np.ndarray, ...]]:
    """Build a faceted cone for each ``(x, y, hit_z)`` hit, taking the
    pillar tip ``tip_overshoot`` mm above the hit surface so the union
    with the part mesh is watertight after slicing."""
    triangles: list[tuple[np.ndarray, ...]] = []
    base_r = base_d / 2.0
    tip_r = tip_d / 2.0
    for x, y, hit_z in hits:
        top_z = hit_z + tip_overshoot
        if top_z <= base_z + 1e-6:
            continue
        xy = np.array([x, y])
        triangles.extend(_faceted_cone(xy, base_r, xy, tip_r,
                                       base_z, top_z, facets))
    return triangles


# ---- Tree-support geometry -------------------------------------------------
# @achris0520 reported that the dense one-pillar-per-grid-cell layout printed
# as solid, fully-fused columns that broke the part when peeled off: every
# tip had its own wide base on the plate, so there was a huge amount of
# build-plate contact and material. The ``--tree`` mode reproduces the
# Bambu Studio "tree support" behaviour instead — many slim breakaway tips
# touch the underside with a tiny contact patch, those tips merge pairwise
# into thin self-supporting branches, and the branches converge onto just a
# few circular trunk feet on the plate. Far less plate contact, far less
# material (thin branches slice to walls-only / near-hollow), and the small
# tip contact snaps off without tearing the part.
def _perp_basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return two orthonormal vectors spanning the plane perpendicular to
    ``axis`` (which need not be unit length)."""
    n = float(np.linalg.norm(axis))
    a = axis / n if n > 1e-12 else np.array([0.0, 0.0, 1.0])
    ref = np.array([1.0, 0.0, 0.0]) if abs(a[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(a, ref)
    u /= np.linalg.norm(u)
    v = np.cross(a, u)
    return u, v


def _frustum_general(p_lo: np.ndarray, r_lo: float, p_hi: np.ndarray,
                     r_hi: float, facets: int
                     ) -> list[tuple[np.ndarray, ...]]:
    """Closed (capped) frustum between two arbitrary 3D points.

    Unlike :func:`_faceted_cone` (which is axis-aligned to +Z) this builds
    a cone segment along the arbitrary ``p_lo -> p_hi`` axis, so it can be
    used for the slanted branches of a support tree. Both ends are capped,
    making each segment an individually watertight closed solid; segments
    that share an endpoint overlap there, and the slicer unions the
    overlapping solids exactly as it did with the original independent
    pillars."""
    axis = p_hi - p_lo
    u, v = _perp_basis(axis)
    angles = np.linspace(0.0, 2.0 * math.pi, facets, endpoint=False)
    lo_ring = [p_lo + r_lo * (math.cos(t) * u + math.sin(t) * v)
               for t in angles]
    hi_ring = [p_hi + r_hi * (math.cos(t) * u + math.sin(t) * v)
               for t in angles]
    tris: list[tuple[np.ndarray, ...]] = []
    for i in range(facets):
        j = (i + 1) % facets
        tris.append((lo_ring[i], lo_ring[j], hi_ring[j]))
        tris.append((lo_ring[i], hi_ring[j], hi_ring[i]))
        # caps (winding chosen so normals point outward along the axis)
        tris.append((p_lo, lo_ring[j], lo_ring[i]))
        tris.append((p_hi, hi_ring[i], hi_ring[j]))
    return tris


class _TreeNode:
    __slots__ = ("xy", "z", "r", "grounded")

    def __init__(self, xy: np.ndarray, z: float, r: float,
                 grounded: bool = False):
        self.xy = np.asarray(xy, dtype=float)
        self.z = float(z)
        self.r = float(r)
        self.grounded = grounded

    @property
    def pos(self) -> np.ndarray:
        return np.array([self.xy[0], self.xy[1], self.z])


def build_support_tree(tips: list[tuple[float, float, float]], *,
                       base_z: float, branch_d: float, trunk_d: float,
                       max_branch_angle: float, merge_radius: float,
                       facets: int) -> tuple[list[tuple[np.ndarray, ...]], int]:
    """Agglomeratively merge tip nodes into a small number of trunks and
    emit the branch geometry.

    Each iteration merges the closest pair of still-active nodes (in XY)
    whose separation is within ``merge_radius`` into a parent placed at
    their XY midpoint, low enough that both branches stay within
    ``max_branch_angle`` degrees of vertical (so they print without their
    own supports). The parent radius grows by area so trunks thicken
    toward the plate, capped at ``trunk_d``. When a parent would drop below
    the plate it is clamped to ``base_z`` and grounded (a trunk foot);
    nodes that cannot merge any further are extended straight down to the
    plate. The result is many slim tips fanning into a few feet — Bambu
    "tree support" style.

    Returns ``(triangles, n_feet)``.
    """
    branch_r = branch_d / 2.0
    trunk_r = trunk_d / 2.0
    tan_a = math.tan(math.radians(max_branch_angle))
    tris: list[tuple[np.ndarray, ...]] = []

    # Active interior nodes (just below each breakaway tip). The slim
    # breakaway contact cone itself is emitted by the caller.
    active = [_TreeNode(np.array([x, y]), z, branch_r) for x, y, z in tips]
    feet = 0

    def emit_edge(parent: _TreeNode, child: _TreeNode) -> None:
        _emit_branch(parent, child, tris, facets)

    def ground(node: _TreeNode) -> None:
        nonlocal feet
        # Straight vertical trunk down to the plate, widening to a foot.
        if node.z > base_z + 1e-6:
            foot = _TreeNode(node.xy.copy(), base_z, max(node.r, trunk_r))
            emit_edge(foot, node)
        feet += 1

    while len(active) > 1:
        # closest pair in XY
        best = None
        best_d = None
        for i in range(len(active)):
            if active[i].grounded:
                continue
            for j in range(i + 1, len(active)):
                if active[j].grounded:
                    continue
                d = float(np.linalg.norm(active[i].xy - active[j].xy))
                if best_d is None or d < best_d:
                    best_d = d
                    best = (i, j)
        if best is None or best_d > merge_radius:
            break
        i, j = best
        a, b = active[i], active[j]
        pxy = 0.5 * (a.xy + b.xy)
        # parent low enough that each branch stays within the angle budget

        def join_z(node: _TreeNode) -> float:
            if tan_a <= 0:
                return base_z
            return node.z - float(np.linalg.norm(node.xy - pxy)) / tan_a

        pz = min(join_z(a), join_z(b), a.z, b.z) - 1e-6
        grounded = False
        if pz <= base_z:
            pz = base_z
            grounded = True
        pr = min(trunk_r, math.sqrt(a.r ** 2 + b.r ** 2))
        parent = _TreeNode(pxy, pz, pr, grounded=grounded)
        emit_edge(parent, a)
        emit_edge(parent, b)
        if grounded:
            feet += 1
        # remove children (higher index first), append parent
        for k in sorted((i, j), reverse=True):
            active.pop(k)
        if grounded:
            # the grounded parent is a finished foot; do not keep merging it
            continue
        active.append(parent)

    # extend any remaining ungrounded nodes straight down to the plate
    for node in active:
        if not node.grounded:
            ground(node)
    return tris, feet


def _emit_branch(parent: _TreeNode, child: _TreeNode,
                 tris: list[tuple[np.ndarray, ...]], facets: int) -> None:
    tris.extend(_frustum_general(parent.pos, parent.r, child.pos, child.r,
                                 facets))


def tree_from_tips(tips: list[tuple[float, float, float]], *,
                   base_z: float, tip_d: float, branch_d: float,
                   trunk_d: float, tip_contact_h: float,
                   tip_overshoot: float, max_branch_angle: float,
                   merge_radius: float, facets: int
                   ) -> tuple[list[tuple[np.ndarray, ...]], int, int]:
    """Build the full tree mesh for a set of underside tip points.

    For each tip a slim breakaway contact cone (Ø ``tip_d`` at the part
    surface widening to Ø ``branch_d`` over ``tip_contact_h`` mm) is
    emitted, then the branch network underneath converges onto a few feet.
    Returns ``(triangles, n_tips, n_feet)``.
    """
    tip_r = tip_d / 2.0
    branch_r = branch_d / 2.0
    tris: list[tuple[np.ndarray, ...]] = []
    interior_tips: list[tuple[float, float, float]] = []
    for x, y, z in tips:
        z_contact = z + tip_overshoot          # buried in the part underside
        z_node = z - tip_contact_h             # where the branch network starts
        if z_node <= base_z + 1e-6:
            # underside is right at the plate: just a tiny stub, no tree
            xy = np.array([x, y])
            tris.extend(_faceted_cone(xy, branch_r, xy, tip_r,
                                      base_z, z_contact, facets))
            continue
        xy = np.array([x, y])
        # breakaway contact cone: small tip -> branch radius
        tris.extend(_frustum_general(np.array([x, y, z_node]), branch_r,
                                     np.array([x, y, z_contact]), tip_r,
                                     facets))
        interior_tips.append((x, y, z_node))
    branch_tris, feet = build_support_tree(
        interior_tips, base_z=base_z, branch_d=branch_d, trunk_d=trunk_d,
        max_branch_angle=max_branch_angle, merge_radius=merge_radius,
        facets=facets)
    tris.extend(branch_tris)
    # The tilted end-cap ring of a slanted branch that meets a grounded
    # foot can dip a fraction of the trunk radius below the plate; clamp
    # every vertex to ``base_z`` so no support geometry prints below the
    # build plate (the resulting flat-on-plate foot is exactly what we
    # want anyway).
    def clamp_tri(tri: tuple[np.ndarray, ...]) -> tuple[np.ndarray, ...]:
        return tuple(np.array([v[0], v[1], max(float(v[2]), base_z)])
                     for v in tri)

    clamped = [clamp_tri(tri) for tri in tris]
    return clamped, len(tips), feet


def member_tips(p1: np.ndarray, p2: np.ndarray, d: float, trim_ends: bool, *,
                spacing: float, end_trim: float, base_z: float
                ) -> list[tuple[float, float, float]]:
    """Sample underside tip points along one member's centerline (the tree
    counterpart to :func:`member_pillars`)."""
    axis = p2 - p1
    L = float(np.linalg.norm(axis))
    if L < 1e-9:
        return []
    t_lo = end_trim if trim_ends else 0.0
    t_hi = L - (end_trim if trim_ends else 0.0)
    span = t_hi - t_lo
    if span <= 0.0:
        return []
    n = max(1, int(round(span / spacing)))
    ts = (np.array([0.5 * (t_lo + t_hi)]) if n == 1
          else np.linspace(t_lo, t_hi, n))
    member_r = d / 2.0
    out: list[tuple[float, float, float]] = []
    for t_along in ts:
        c = p1 + (t_along / L) * axis
        z = float(c[2] - member_r)
        if z <= base_z + 1e-6:
            continue
        out.append((float(c[0]), float(c[1]), z))
    return out


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
    src.add_argument("--stl", type=Path,
                     help="Ray-cast mode: load an STL mesh, project it "
                          "onto XY, cast +Z rays from below, and place a "
                          "pillar at every grid cell whose nearest hit is "
                          "above --min_clearance. Requires `trimesh`.")
    ap.add_argument("--out", type=Path, required=True,
                    help="Output STL path (binary STL).")
    ap.add_argument("--out_part", type=Path, default=None,
                    help="[--stl only] Also write the input mesh, lifted "
                         "so min(z) sits at --base_z, to this path. Use "
                         "it as the merge partner for --out so the part "
                         "and the pillars share a coordinate frame.")
    ap.add_argument("--min_clearance", type=float, default=1.5,
                    help="[--stl only] Skip pillars where the nearest "
                         "underside hit is within this many mm of the "
                         "build plate (default 1.5 mm; filters out the "
                         "bed-contact triangle so we don't drop a pillar "
                         "under something that's already on the plate).")
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
    ap.add_argument("--tip_d", type=float, default=0.4,
                    help="Pillar tip diameter where it fuses to the "
                         "member's underside (mm). Smaller = easier to "
                         "snap off and a smaller surface scar. The tip is "
                         "buried --tip_overshoot mm into the member so it "
                         "prints reliably even at one nozzle width. Default "
                         "0.4 (1x a 0.4 mm nozzle; matches Bambu Studio's "
                         "guidance for fine/delicate contact points).")
    ap.add_argument("--base_z", type=float, default=0.0,
                    help="Z height of the build plate (mm). Default 0.0.")
    ap.add_argument("--tip_overshoot", type=float, default=0.3,
                    help="Bury the pillar tip this many mm inside the "
                         "member so the boolean union is watertight after "
                         "slicing. Default 0.3.")
    ap.add_argument("--facets", type=int, default=12,
                    help="Number of sides on the faceted cone (default "
                         "12; higher = rounder + more triangles).")
    # Tree-support mode knobs
    ap.add_argument("--tree", action="store_true",
                    help="Emit Bambu-style tree supports instead of one "
                         "straight pillar per sample point: slim breakaway "
                         "tips merge into thin branches that converge onto "
                         "a few circular feet, so there is far less "
                         "build-plate contact and material, and the tips "
                         "snap off without tearing the part.")
    ap.add_argument("--branch_d", type=float, default=1.8,
                    help="[--tree] Branch diameter (mm). Kept thin so the "
                         "slicer prints walls-only (near-hollow). Default "
                         "1.8.")
    ap.add_argument("--trunk_d", type=float, default=5.0,
                    help="[--tree] Maximum trunk diameter near the plate "
                         "(mm); branches thicken by area as they merge, "
                         "capped here. Default 5.0.")
    ap.add_argument("--tip_contact_h", type=float, default=2.5,
                    help="[--tree] Height (mm) of the slim breakaway "
                         "contact cone between the part underside (Ø "
                         "--tip_d) and the branch network (Ø --branch_d). "
                         "A taller cone keeps the neck thin for longer so "
                         "the visible connection point stays narrow (like a "
                         "Bambu tree-support tip) and breaks away cleanly. "
                         "Default 2.5.")
    ap.add_argument("--max_branch_angle", type=float, default=40.0,
                    help="[--tree] Maximum branch deviation from vertical "
                         "(deg) so branches print without their own "
                         "supports. Default 40.")
    ap.add_argument("--merge_radius", type=float, default=22.0,
                    help="[--tree] Maximum XY separation (mm) of two nodes "
                         "that may merge into one branch; larger = fewer "
                         "feet. Default 22.")
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
    if args.stl is not None:
        hits, lifted_mesh = raycast_underside(
            args.stl, spacing=args.spacing,
            min_clearance=args.min_clearance, base_z=args.base_z,
        )
        if args.tree:
            triangles, n_tips, n_feet = tree_from_tips(
                hits, base_z=args.base_z, tip_d=args.tip_d,
                branch_d=args.branch_d, trunk_d=args.trunk_d,
                tip_contact_h=args.tip_contact_h,
                tip_overshoot=args.tip_overshoot,
                max_branch_angle=args.max_branch_angle,
                merge_radius=args.merge_radius, facets=args.facets,
            )
            n_tris = write_binary_stl(triangles, args.out)
            print(f"Wrote {args.out} (tree mode)", file=sys.stderr)
            print(f"  triangles         : {n_tris:,}", file=sys.stderr)
            print(f"  tip contacts      : {n_tips}", file=sys.stderr)
            print(f"  trunk feet        : {n_feet}", file=sys.stderr)
            print(f"  spacing (mm)      : {args.spacing}", file=sys.stderr)
            print(f"  merge_radius (mm) : {args.merge_radius}", file=sys.stderr)
        else:
            triangles = pillars_from_hits(
                hits, base_d=args.base_d, tip_d=args.tip_d,
                base_z=args.base_z, tip_overshoot=args.tip_overshoot,
                facets=args.facets,
            )
            n_tris = write_binary_stl(triangles, args.out)
            print(f"Wrote {args.out}", file=sys.stderr)
            print(f"  triangles         : {n_tris:,}", file=sys.stderr)
            print(f"  pillars emitted   : {len(hits)}", file=sys.stderr)
            print(f"  spacing (mm)      : {args.spacing}", file=sys.stderr)
            print(f"  min_clearance (mm): {args.min_clearance}",
                  file=sys.stderr)
        if args.out_part is not None:
            write_trimesh_binary_stl(lifted_mesh, args.out_part)
            print(f"  lifted part STL   : {args.out_part}", file=sys.stderr)
        return
    if args.members is not None:
        members = load_members_json(args.members)
    else:
        members = build_topology(args.topology, args)
    if args.tree:
        skip_bed_contact = not args.include_bed_contact
        tips: list[tuple[float, float, float]] = []
        for p1, p2, d, trim_ends in members:
            if skip_bed_contact and not trim_ends:
                continue
            tips.extend(member_tips(
                p1, p2, d, trim_ends, spacing=args.spacing,
                end_trim=args.end_trim, base_z=args.base_z))
        triangles, n_tips, n_feet = tree_from_tips(
            tips, base_z=args.base_z, tip_d=args.tip_d,
            branch_d=args.branch_d, trunk_d=args.trunk_d,
            tip_contact_h=args.tip_contact_h,
            tip_overshoot=args.tip_overshoot,
            max_branch_angle=args.max_branch_angle,
            merge_radius=args.merge_radius, facets=args.facets,
        )
        n_tris = write_binary_stl(triangles, args.out)
        print(f"Wrote {args.out} (tree mode)", file=sys.stderr)
        print(f"  triangles         : {n_tris:,}", file=sys.stderr)
        print(f"  tip contacts      : {n_tips}", file=sys.stderr)
        print(f"  trunk feet        : {n_feet}", file=sys.stderr)
        return
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
