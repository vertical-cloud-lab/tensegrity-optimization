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
from collections import defaultdict
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
# the part at each (x, y) sample point and look at **every** triangle the
# ray crosses, not just the first one.
#
# A closed solid is entered and exited in pairs along the ray: the ray
# crosses a *down-facing* face (triangle normal points down, ``nz < 0``)
# to enter solid — that face is the underside of a member — and later
# crosses an *up-facing* face (``nz > 0``) to exit. Every down-facing
# crossing is therefore an overhang surface that may need a support tip.
#
# The previous implementation used ``multiple_hits=False``, i.e. it only
# ever recorded the single **lowest** surface above each (x, y). That
# silently dropped every member stacked above another one along the same
# vertical column — most importantly the bottom end-caps of the vertical
# TPU cables, which hang in mid-air above the struts: the ray hit the
# strut first and the cable above it never received a tip, so it printed
# unsupported and sagged (the print failure the reviewer reported). It
# also produced far fewer contact points than the part actually needs.
#
# This version walks all crossings per ray (sorted bottom-up), keeps a
# running "floor" at the top of the most recent solid span (or the build
# plate), and emits a tip at each down-facing underside that (a) sits
# above ``base_z + min_clearance`` and (b) has at least ``min_gap`` mm of
# open air below it — i.e. it is a genuine overhang and not a face that is
# already resting on the plate or on a lower member. This captures joint
# spheres, end caps, members crossing over other members, and the vertical
# cable end-caps the centerline / lowest-hit passes all missed.
def raycast_underside(stl_path: Path, *, spacing: float,
                      min_clearance: float, base_z: float = 0.0,
                      min_gap: float = 1.0, down_normal_max: float = -0.2
                      ) -> tuple[list[tuple[float, float, float]],
                                 "object"]:
    """Rasterise the mesh's bottom-view XY footprint at ``spacing`` mm,
    cast a +Z ray from below the part at each grid point, and return the
    list of ``(x, y, hit_z)`` tuples for **every** down-facing underside
    surface the ray crosses that lies above ``base_z + min_clearance`` and
    has more than ``min_gap`` mm of open air directly below it.

    ``down_normal_max`` is the maximum (most positive) z-component of a
    face normal that still counts as "down-facing"; the default ``-0.2``
    treats anything tilted more than ~11° below horizontal as an
    overhang and ignores near-vertical side walls (which carry no
    overhang and self-support as they print).

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
    # on z=base_z (a bed-contact triangle) still registers a crossing.
    origins = np.column_stack([
        XX.ravel(), YY.ravel(),
        np.full(n, base_z - 1.0),
    ])
    dirs = np.tile(np.array([0.0, 0.0, 1.0]), (n, 1))
    # ``multiple_hits=True`` returns *every* triangle each ray crosses, so
    # we can see the undersides of members stacked above one another.
    locs, idx_ray, idx_tri = mesh.ray.intersects_location(
        origins, dirs, multiple_hits=True)
    face_nz = mesh.face_normals[:, 2]
    per_ray: dict[int, list[tuple[float, float, np.ndarray]]] = defaultdict(list)
    for loc, ir, it in zip(locs, idx_ray, idx_tri):
        per_ray[int(ir)].append((float(loc[2]), float(face_nz[it]), loc))
    hits: list[tuple[float, float, float]] = []
    z_min = base_z + float(min_clearance)
    up_normal_min = -float(down_normal_max)
    for crossings in per_ray.values():
        crossings.sort(key=lambda t: t[0])
        # ``floor`` tracks the top of the most-recent solid span (or the
        # build plate) so we can measure the open gap under each underside.
        floor = base_z
        for z, nz, loc in crossings:
            if nz < down_normal_max:           # down-facing -> an underside
                if z > z_min and (z - floor) > min_gap:
                    hits.append((float(loc[0]), float(loc[1]), z))
            elif nz > up_normal_min:           # up-facing -> top of a span
                if z > floor:
                    floor = z
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


# ---- Tendon-cage mode (anti-wobble guide cages, PR #35 proposal) -----------
# me-madsen observed (PR #35) that a near-vertical TPU tendon "tends to move
# around quite a bit while being printed as it's only resting on one point and
# the tip of the nozzle can push it around", producing the bubbling /
# imperfection defects photographed there, and proposed "a cage of 3 hollow
# pillars/supports around each tendon" to keep it from wandering.
#
# The ``--cage`` mode implements that proposal:
#
#   * **Tendon detection** — horizontal cross-sections of the part mesh are
#     taken every ``--cage_slice_dz`` mm; small, nearly-circular section
#     components (equivalent diameter between ``--cage_min_d`` and
#     ``--cage_max_d``) are linked slice-to-slice into chains; chains longer
#     than ``--cage_min_len`` whose fitted axis is within ``--cage_max_tilt``
#     degrees of vertical are tendons. (On the PR #35 T3-prism this finds
#     the three Ø4.6 mm TPU cables, which tilt ~20° from vertical.)
#   * **Guide pillars** — three Ø ``--cage_pillar_d`` pillars run parallel to
#     the tendon axis at 120° spacing, standing off the tendon surface by
#     ``--cage_pillar_gap`` so they never touch it. Their common azimuth
#     offset is optimised (in ``--cage_azimuth_step``° steps) so the pillars
#     stay at least ``--cage_clearance`` clear of the rest of the part;
#     where a strut/joint still blocks a pillar the pillar is trimmed to
#     just below the clash.
#   * **C-ring braces** — every ``--cage_ring_spacing`` mm an open annular
#     ring (inner face ``--cage_ring_gap`` from the tendon surface) ties the
#     pillars together, so the cage is a stiff triangulated column rather
#     than three floppy lone pillars, and constrains the tendon's lateral
#     wobble to ~the ring gap. Each ring leaves a ``--cage_opening``° opening
#     (auto-widened until the opening chord exceeds the tendon diameter) so
#     the finished cage can be pulled off the tendon sideways after the
#     pillar feet are snapped off the plate. Rings that would clash with a
#     crossing member are skipped automatically.
#
# The cage never touches the part: it bounds the tendon's motion during the
# print (the nozzle can only push it ~the ring gap) without fusing to it.
def _section_components(mesh: "object", z: float) -> list[dict]:
    """Cross-section the mesh at height ``z`` and return one entry per
    connected section loop: its XY centroid, mean/max radius about the
    centroid, and radial std-dev (circularity proxy). Uses raw
    ``mesh_plane`` segments + a union-find over shared endpoints so it
    needs no shapely/networkx."""
    from trimesh.intersections import mesh_plane
    segs = mesh_plane(mesh, plane_normal=[0.0, 0.0, 1.0],
                      plane_origin=[0.0, 0.0, z])
    if len(segs) == 0:
        return []
    n = len(segs)
    parent = list(range(n))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    endpoint_map: dict[tuple[float, float], list[int]] = defaultdict(list)
    for i, s in enumerate(segs):
        for e in s:
            endpoint_map[(round(float(e[0]), 3),
                          round(float(e[1]), 3))].append(i)
    for owners in endpoint_map.values():
        r0 = find(owners[0])
        for k in owners[1:]:
            rk = find(k)
            if rk != r0:
                parent[rk] = r0
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)
    out: list[dict] = []
    for idx in groups.values():
        pts = segs[idx][:, :, :2].reshape(-1, 2)
        c = pts.mean(axis=0)
        r = np.linalg.norm(pts - c, axis=1)
        out.append(dict(center=c, r_mean=float(r.mean()),
                        r_max=float(r.max()), r_std=float(r.std())))
    return out


def detect_tendons(mesh: "object", *, base_z: float, cage_min_d: float,
                   cage_max_d: float, cage_max_tilt: float,
                   cage_min_len: float, slice_dz: float,
                   link_tol: float = 3.0) -> list[dict]:
    """Find near-vertical thin members ("tendons") by linking small circular
    cross-section components across horizontal slices.

    Returns one dict per tendon with the slice z-range (``z_lo``/``z_hi``),
    the tendon radius ``r`` (median of the per-slice max radii), the tilt
    from vertical in degrees, and linear fits ``fx``/``fy`` giving the
    centerline as ``x = polyval(fx, z)``, ``y = polyval(fy, z)``.
    """
    z0 = float(mesh.bounds[0, 2])
    z1 = float(mesh.bounds[1, 2])
    tilt_slope = math.tan(math.radians(cage_max_tilt))
    chains: list[list[tuple[float, np.ndarray, float]]] = []
    active: list[list[tuple[float, np.ndarray, float]]] = []
    for z in np.arange(z0 + 1.0, z1 - 0.5, slice_dz):
        comps = [c for c in _section_components(mesh, float(z))
                 if cage_min_d <= 2.0 * c["r_mean"] <= cage_max_d
                 and c["r_std"] <= 0.2 * c["r_mean"] + 0.05]
        used: set[int] = set()
        still_active = []
        for ch in active:
            zp, cp, rp = ch[-1]
            best = None
            best_d = None
            allow = link_tol + (float(z) - zp) * tilt_slope
            for i, c in enumerate(comps):
                if i in used:
                    continue
                d = float(np.linalg.norm(c["center"] - cp))
                if d <= allow and abs(c["r_max"] - rp) <= 0.35 * rp:
                    if best_d is None or d < best_d:
                        best_d = d
                        best = i
            if best is not None:
                used.add(best)
                ch.append((float(z), comps[best]["center"],
                           comps[best]["r_max"]))
                still_active.append(ch)
            else:
                chains.append(ch)
        for i, c in enumerate(comps):
            if i not in used:
                still_active.append([(float(z), c["center"], c["r_max"])])
        active = still_active
    chains.extend(active)

    tendons: list[dict] = []
    for ch in chains:
        if len(ch) < 3:
            continue
        zs = np.array([e[0] for e in ch])
        if zs[-1] - zs[0] < cage_min_len:
            continue
        cxy = np.array([e[1] for e in ch])
        rr = np.array([e[2] for e in ch])
        fx = np.polyfit(zs, cxy[:, 0], 1)
        fy = np.polyfit(zs, cxy[:, 1], 1)
        tilt = math.degrees(math.atan(math.hypot(fx[0], fy[0])))
        if tilt > cage_max_tilt:
            continue
        tendons.append(dict(z_lo=float(zs[0]), z_hi=float(zs[-1]),
                            r=float(np.median(rr)), tilt=float(tilt),
                            fx=[float(v) for v in fx],
                            fy=[float(v) for v in fy]))
    return tendons


def _quad(p00: np.ndarray, p01: np.ndarray, p11: np.ndarray,
          p10: np.ndarray) -> list[tuple[np.ndarray, ...]]:
    return [(p00, p01, p11), (p00, p11, p10)]


def _annular_sector(center_xy: np.ndarray, z0: float, z1: float,
                    r_in: float, r_out: float, a0_deg: float,
                    sweep_deg: float, seg_deg: float = 8.0
                    ) -> list[tuple[np.ndarray, ...]]:
    """Closed solid: an annular sector (C-ring segment) extruded from
    ``z0`` to ``z1``, centred on ``center_xy``, spanning ``sweep_deg``
    degrees counter-clockwise from ``a0_deg``."""
    n = max(6, int(math.ceil(sweep_deg / seg_deg)))
    angs = np.radians(a0_deg + np.linspace(0.0, sweep_deg, n + 1))
    cx, cy = float(center_xy[0]), float(center_xy[1])

    def pt(r: float, t: float, z: float) -> np.ndarray:
        return np.array([cx + r * math.cos(t), cy + r * math.sin(t), z])

    tris: list[tuple[np.ndarray, ...]] = []
    for i in range(n):
        tA, tB = float(angs[i]), float(angs[i + 1])
        iA0, iB0 = pt(r_in, tA, z0), pt(r_in, tB, z0)
        iA1, iB1 = pt(r_in, tA, z1), pt(r_in, tB, z1)
        oA0, oB0 = pt(r_out, tA, z0), pt(r_out, tB, z0)
        oA1, oB1 = pt(r_out, tA, z1), pt(r_out, tB, z1)
        tris += _quad(oA0, oB0, oB1, oA1)   # outer wall (normal +r)
        tris += _quad(iB0, iA0, iA1, iB1)   # inner wall (normal -r)
        tris += _quad(iA1, oA1, oB1, iB1)   # top (normal +z)
        tris += _quad(iA0, iB0, oB0, oA0)   # bottom (normal -z)
    t_start, t_end = float(angs[0]), float(angs[-1])
    tris += _quad(pt(r_in, t_start, z0), pt(r_out, t_start, z0),
                  pt(r_out, t_start, z1), pt(r_in, t_start, z1))  # start cap
    tris += _quad(pt(r_in, t_end, z0), pt(r_in, t_end, z1),
                  pt(r_out, t_end, z1), pt(r_out, t_end, z0))     # end cap
    return tris


def build_tendon_cages(mesh: "object", tendons: list[dict], *,
                       base_z: float, pillar_d: float, pillar_gap: float,
                       ring_gap: float, ring_h: float, ring_spacing: float,
                       opening_deg: float, clearance: float, foot_d: float,
                       foot_h: float, top_margin: float, bottom_margin: float,
                       azimuth_step: float, facets: int
                       ) -> tuple[list[tuple[np.ndarray, ...]], list[dict]]:
    """Emit an anti-wobble guide cage (3 pillars + C-ring braces) around
    each detected tendon. Returns ``(triangles, per-tendon stats)``."""
    from trimesh.proximity import ProximityQuery
    pq = ProximityQuery(mesh)
    pillar_r = pillar_d / 2.0
    tris: list[tuple[np.ndarray, ...]] = []
    stats: list[dict] = []
    for tn in tendons:
        r_t = tn["r"]
        r_in = r_t + ring_gap
        r_p = r_t + pillar_gap + pillar_r
        r_out = r_p + pillar_r

        def cx(z):
            return np.polyval(tn["fx"], z)

        def cy(z):
            return np.polyval(tn["fy"], z)

        z_top = tn["z_hi"] - top_margin
        # The pillar's *guard* segment runs parallel to the tendon axis over
        # the tendon's free span. Below the tendon (where the extended axis
        # dives into the anchoring joint / strut cluster) each pillar gets a
        # separate *approach* segment leaning from a clash-free plate foot
        # up to the guard's lower end.
        z_guard_lo = tn["z_lo"] + 1.0
        zs = np.arange(z_guard_lo, z_top, 2.0)
        if len(zs) < 3:
            continue
        # -- pick the pillar-triad azimuth maximising clash-free guard span
        phis = np.arange(0.0, 120.0, azimuth_step)
        cand_pts = []
        for phi0 in phis:
            for k in range(3):
                a = math.radians(phi0 + 120.0 * k)
                cand_pts.append(np.column_stack([
                    cx(zs) + r_p * math.cos(a),
                    cy(zs) + r_p * math.sin(a),
                    zs]))
        sd = pq.signed_distance(np.vstack(cand_pts))
        clear = np.nan_to_num(-sd, nan=-1.0).reshape(
            len(phis), 3, len(zs))  # distance outside the part
        ok = clear >= pillar_r + clearance
        best = None
        for pi, phi0 in enumerate(phis):
            heights = []
            for k in range(3):
                bad = np.where(~ok[pi, k])[0]
                h = z_top if len(bad) == 0 else max(
                    z_guard_lo, float(zs[bad[0]]) - 2.0)
                heights.append(float(h))
            score = sum(heights)
            if best is None or score > best[0]:
                best = (score, float(phi0), heights)
        _, phi0, heights = best

        # -- clash-free approach from a plate foot up to each guard start
        centre_xy = np.array([float(cx(0.5 * (tn["z_lo"] + tn["z_hi"]))),
                              float(cy(0.5 * (tn["z_lo"] + tn["z_hi"])))])
        outward = centre_xy - np.asarray(mesh.centroid)[:2]
        outward = (outward / np.linalg.norm(outward)
                   if np.linalg.norm(outward) > 1e-9 else np.array([1.0, 0.0]))
        out_az = math.degrees(math.atan2(outward[1], outward[0]))
        approach_cands: list[tuple[float, float]] = [(0.0, 0.0)]
        for lean in (10.0, 20.0, 30.0):
            for daz in sorted(range(0, 360, 30),
                              key=lambda d: min(d, 360 - d)):
                approach_cands.append((lean, out_az + daz))
        pillar_info: list[dict | None] = []
        seg_pts = []
        seg_meta = []
        for k in range(3):
            guard_h = heights[k]
            if guard_h < z_guard_lo + 5.0:
                pillar_info.append(None)   # guard blocked almost immediately
                continue
            a = math.radians(phi0 + 120.0 * k)
            off = np.array([r_p * math.cos(a), r_p * math.sin(a)])
            p0 = np.array([cx(z_guard_lo) + off[0],
                           cy(z_guard_lo) + off[1], z_guard_lo])
            for lean, az in approach_cands:
                shift = math.tan(math.radians(lean)) * (z_guard_lo - base_z)
                foot = np.array([
                    p0[0] + shift * math.cos(math.radians(az)),
                    p0[1] + shift * math.sin(math.radians(az)), base_z])
                t_samples = np.linspace(0.02, 0.98,
                                        max(6, int(z_guard_lo / 2.0)))
                pts = foot[None, :] + t_samples[:, None] * (p0 - foot)[None, :]
                seg_pts.append(pts)
                seg_meta.append((k, lean, az, foot, p0, guard_h,
                                 len(pts)))
            pillar_info.append("pending")
        chosen: dict[int, tuple] = {}
        if seg_pts:
            sd = np.nan_to_num(-pq.signed_distance(np.vstack(seg_pts)),
                               nan=-1.0)
            ofs = 0
            for k, lean, az, foot, p0, guard_h, n_s in seg_meta:
                d = sd[ofs:ofs + n_s]
                ofs += n_s
                if k in chosen:
                    continue
                # near the plate the wide foot flare needs the clearance
                margin = pillar_r + clearance
                low = foot[2] + 2.0
                zvals = foot[2] + (p0[2] - foot[2]) * np.linspace(
                    0.02, 0.98, n_s)
                req = np.where(zvals < low, foot_d / 2.0 + clearance, margin)
                if bool((d >= req).all()):
                    chosen[k] = (foot, p0, guard_h)
        # -- emit pillar geometry
        n_pillars = 0
        guard_tops: list[float] = []
        for k in range(3):
            if pillar_info[k] is None or k not in chosen:
                guard_tops.append(0.0)
                continue
            foot, p0, guard_h = chosen[k]
            a = math.radians(phi0 + 120.0 * k)
            off = np.array([r_p * math.cos(a), r_p * math.sin(a)])
            top = np.array([cx(guard_h) + off[0],
                            cy(guard_h) + off[1], guard_h])
            u = (p0 - foot)
            u = u / np.linalg.norm(u)
            flare_top = foot + u * foot_h
            tris.extend(_frustum_general(   # foot flare on the plate
                foot, foot_d / 2.0, flare_top, pillar_r, facets))
            tris.extend(_frustum_general(   # approach segment
                flare_top, pillar_r, p0, pillar_r, facets))
            tris.extend(_frustum_general(   # guard segment (‖ tendon)
                p0, pillar_r, top, pillar_r, facets))
            guard_tops.append(guard_h)
            n_pillars += 1
        heights = guard_tops

        # -- C-ring braces
        opening = max(
            opening_deg,
            math.degrees(2.0 * math.asin(
                min(1.0, (2.0 * r_t + 0.6) / (2.0 * r_in)))))
        sweep = 360.0 - opening
        a0 = phi0 + 300.0 + opening / 2.0  # opening centred between
        #                                     pillar k=2 and pillar k=0
        z_ring_hi = (sorted(guard_tops)[1] if len(guard_tops) == 3
                     else max(guard_tops, default=0.0))  # 2nd-highest: a
        #                                    ring needs >= 2 pillar anchors
        ring_zs = np.arange(tn["z_lo"] + bottom_margin,
                            z_ring_hi - ring_h, ring_spacing)
        n_rings = 0
        for rz in ring_zs:
            anchored = sum(1 for h in guard_tops if h >= rz + ring_h)
            if anchored < 2:
                continue
            zc = float(rz) + ring_h / 2.0
            centre = np.array([cx(zc), cy(zc)])
            # clash check: sample the ring solid; the tendon itself sits
            # ring_gap away from the inner face, so a healthy ring clears
            # the part everywhere — any closer hit is a crossing member.
            samp_a = np.radians(a0 + np.linspace(0.0, sweep, 24))
            samp_r = np.array([r_in + 0.2, 0.5 * (r_in + r_out),
                               r_out - 0.2])
            pts = np.array([[centre[0] + r * math.cos(t),
                             centre[1] + r * math.sin(t), zc]
                            for t in samp_a for r in samp_r])
            if float((-pq.signed_distance(pts)).min()) < 0.25:
                continue
            tris.extend(_annular_sector(centre, float(rz),
                                        float(rz) + ring_h,
                                        r_in, r_out, a0, sweep))
            n_rings += 1
        stats.append(dict(
            r=r_t, tilt=tn["tilt"], z_lo=tn["z_lo"], z_hi=tn["z_hi"],
            phi0=phi0, pillar_heights=heights, n_pillars=n_pillars,
            n_rings=n_rings, r_ring_in=r_in, r_pillar=r_p,
            opening_deg=opening,
            opening_chord=2.0 * r_in * math.sin(math.radians(opening / 2.0)),
            fx=tn["fx"], fy=tn["fy"]))
    # A tilted foot-flare's bottom cap can dip below the plate; clamp every
    # vertex to base_z (flat-on-plate feet, same as the tree mode).
    tris = [tuple(np.array([v[0], v[1], max(float(v[2]), base_z)])
                  for v in tri) for tri in tris]
    return tris, stats


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
                          "pillar under every down-facing underside the "
                          "ray crosses that is above --min_clearance and "
                          "has more than --min_gap mm of air below it. "
                          "Requires `trimesh`.")
    ap.add_argument("--out", type=Path, required=True,
                    help="Output STL path (binary STL).")
    ap.add_argument("--out_part", type=Path, default=None,
                    help="[--stl only] Also write the input mesh, lifted "
                         "so min(z) sits at --base_z, to this path. Use "
                         "it as the merge partner for --out so the part "
                         "and the pillars share a coordinate frame.")
    ap.add_argument("--min_clearance", type=float, default=1.5,
                    help="[--stl only] Skip underside hits within this "
                         "many mm of the build plate (default 1.5 mm; "
                         "filters out members that already sit on the "
                         "plate, e.g. the bed-contact triangle).")
    ap.add_argument("--min_gap", type=float, default=1.0,
                    help="[--stl only] Only treat a down-facing surface as "
                         "an overhang needing support if it has more than "
                         "this many mm of open air directly below it "
                         "(default 1.0 mm). Stops tips being dropped under "
                         "a member that is already resting on the plate or "
                         "on a lower member.")
    ap.add_argument("--down_normal_max", type=float, default=-0.2,
                    help="[--stl only] Maximum face-normal z-component that "
                         "still counts as a down-facing underside (default "
                         "-0.2 ~= surfaces tilted >11 deg below horizontal). "
                         "Near-vertical side walls are ignored.")
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
    # Tendon-cage mode knobs (anti-wobble guide cages, PR #35 proposal)
    ap.add_argument("--cage", action="store_true",
                    help="[--stl only] Also emit an anti-wobble guide cage "
                         "(3 pillars + C-ring braces, never touching the "
                         "part) around each detected near-vertical tendon, "
                         "in addition to the normal supports. Implements "
                         "me-madsen's PR #35 proposal for TPU cables the "
                         "nozzle pushes around mid-print.")
    ap.add_argument("--cage_only", action="store_true",
                    help="[--stl only] Emit ONLY the tendon cages (no tree "
                         "supports / pillars) — useful for writing the cage "
                         "as its own STL to load as a separate object.")
    ap.add_argument("--cage_report", type=Path, default=None,
                    help="[--cage] Write per-tendon cage geometry stats to "
                         "this JSON path (consumed by "
                         "verification/verify_cage_geometry.py).")
    ap.add_argument("--cage_pillar_d", type=float, default=2.5,
                    help="[--cage] Guide-pillar diameter (mm). Default 2.5.")
    ap.add_argument("--cage_pillar_gap", type=float, default=1.5,
                    help="[--cage] Clearance between the tendon surface and "
                         "the nearest pillar surface (mm). Default 1.5.")
    ap.add_argument("--cage_ring_gap", type=float, default=1.2,
                    help="[--cage] Clearance between the tendon surface and "
                         "the C-ring inner face (mm) — the tendon's maximum "
                         "lateral wobble. Default 1.2.")
    ap.add_argument("--cage_ring_h", type=float, default=1.2,
                    help="[--cage] C-ring height (mm). Default 1.2 (6 "
                         "layers at 0.2 mm).")
    ap.add_argument("--cage_ring_spacing", type=float, default=18.0,
                    help="[--cage] Vertical spacing between C-rings (mm). "
                         "Default 18.")
    ap.add_argument("--cage_opening", type=float, default=120.0,
                    help="[--cage] C-ring opening angle (deg) for pulling "
                         "the cage off the tendon after printing; auto-"
                         "widened until the opening chord exceeds the "
                         "tendon diameter. Default 120.")
    ap.add_argument("--cage_clearance", type=float, default=0.8,
                    help="[--cage] Minimum clearance between cage pillars "
                         "and any non-tendon part geometry (mm); pillars "
                         "are trimmed below anything closer. Default 0.8.")
    ap.add_argument("--cage_foot_d", type=float, default=6.0,
                    help="[--cage] Pillar foot-flare diameter on the plate "
                         "(mm). Default 6.")
    ap.add_argument("--cage_min_d", type=float, default=1.5,
                    help="[--cage] Minimum cross-section diameter (mm) for "
                         "a component to count as a tendon. Default 1.5.")
    ap.add_argument("--cage_max_d", type=float, default=7.0,
                    help="[--cage] Maximum cross-section diameter (mm) for "
                         "a component to count as a tendon (excludes "
                         "struts). Default 7.")
    ap.add_argument("--cage_max_tilt", type=float, default=25.0,
                    help="[--cage] Maximum tendon tilt from vertical (deg) "
                         "to receive a cage. Default 25 (the PR #35 "
                         "T3-prism TPU cables tilt ~20 deg).")
    ap.add_argument("--cage_min_len", type=float, default=25.0,
                    help="[--cage] Minimum tendon length (mm of z-extent) "
                         "to receive a cage. Default 25.")
    ap.add_argument("--cage_slice_dz", type=float, default=3.0,
                    help="[--cage] Cross-section slice spacing (mm) for "
                         "tendon detection. Default 3.")
    ap.add_argument("--cage_azimuth_step", type=float, default=5.0,
                    help="[--cage] Step (deg) for the clash-avoiding "
                         "pillar-triad azimuth search. Default 5.")
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
    if (args.cage or args.cage_only) and args.stl is None:
        raise SystemExit("--cage/--cage_only require --stl mode (tendon "
                         "detection cross-sections the actual mesh).")
    if args.stl is not None:
        hits, lifted_mesh = raycast_underside(
            args.stl, spacing=args.spacing,
            min_clearance=args.min_clearance, base_z=args.base_z,
            min_gap=args.min_gap, down_normal_max=args.down_normal_max,
        )
        cage_tris: list = []
        if args.cage or args.cage_only:
            tendons = detect_tendons(
                lifted_mesh, base_z=args.base_z,
                cage_min_d=args.cage_min_d, cage_max_d=args.cage_max_d,
                cage_max_tilt=args.cage_max_tilt,
                cage_min_len=args.cage_min_len,
                slice_dz=args.cage_slice_dz)
            cage_tris, cage_stats = build_tendon_cages(
                lifted_mesh, tendons, base_z=args.base_z,
                pillar_d=args.cage_pillar_d,
                pillar_gap=args.cage_pillar_gap,
                ring_gap=args.cage_ring_gap, ring_h=args.cage_ring_h,
                ring_spacing=args.cage_ring_spacing,
                opening_deg=args.cage_opening,
                clearance=args.cage_clearance, foot_d=args.cage_foot_d,
                foot_h=1.5, top_margin=3.0, bottom_margin=3.0,
                azimuth_step=args.cage_azimuth_step, facets=args.facets)
            print(f"Tendon cages       : {len(cage_stats)} tendons",
                  file=sys.stderr)
            for i, st in enumerate(cage_stats):
                print(f"  tendon[{i}]: Ø{2*st['r']:.2f} mm, "
                      f"tilt {st['tilt']:.1f}°, "
                      f"z {st['z_lo']:.1f}–{st['z_hi']:.1f}, "
                      f"{st['n_pillars']} pillars "
                      f"(h {', '.join(f'{h:.0f}' for h in st['pillar_heights'])}), "
                      f"{st['n_rings']} rings, "
                      f"opening {st['opening_deg']:.0f}° "
                      f"(chord {st['opening_chord']:.2f} mm vs tendon "
                      f"Ø{2*st['r']:.2f} mm)", file=sys.stderr)
            if args.cage_report is not None:
                args.cage_report.parent.mkdir(parents=True, exist_ok=True)
                args.cage_report.write_text(json.dumps(dict(
                    base_z=args.base_z, pillar_d=args.cage_pillar_d,
                    pillar_gap=args.cage_pillar_gap,
                    ring_gap=args.cage_ring_gap, ring_h=args.cage_ring_h,
                    ring_spacing=args.cage_ring_spacing,
                    clearance=args.cage_clearance,
                    tendons=cage_stats), indent=2))
                print(f"  cage report       : {args.cage_report}",
                      file=sys.stderr)
        if args.cage_only:
            n_tris = write_binary_stl(cage_tris, args.out)
            print(f"Wrote {args.out} (cage only)", file=sys.stderr)
            print(f"  triangles         : {n_tris:,}", file=sys.stderr)
            if args.out_part is not None:
                write_trimesh_binary_stl(lifted_mesh, args.out_part)
                print(f"  lifted part STL   : {args.out_part}",
                      file=sys.stderr)
            return
        if args.tree:
            triangles, n_tips, n_feet = tree_from_tips(
                hits, base_z=args.base_z, tip_d=args.tip_d,
                branch_d=args.branch_d, trunk_d=args.trunk_d,
                tip_contact_h=args.tip_contact_h,
                tip_overshoot=args.tip_overshoot,
                max_branch_angle=args.max_branch_angle,
                merge_radius=args.merge_radius, facets=args.facets,
            )
            triangles = triangles + cage_tris
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
            ) + cage_tris
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
