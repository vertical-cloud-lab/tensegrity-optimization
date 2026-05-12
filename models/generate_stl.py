"""Generate binary STL files for canonical tensegrity structures.

This script produces solid (3D-printable) representations of well-known
tensegrity geometries for use in CAD review, slicing, and finite-element
import. Struts are rendered as solid cylinders; cables are rendered as
thin cylinders so that the full tensegrity topology is captured in a
single STL.

Structures emitted (see ``models/README.md`` for references):

* ``3bar_prism.stl``   - Snelson/Skelton 3-bar (T3) tensegrity prism
* ``4bar_prism.stl``   - 4-bar tensegrity prism
* ``icosahedron.stl``  - 6-strut tensegrity icosahedron (expanded
                          octahedron); the canonical "spherical" tensegrity

All geometry is authored from first principles (no third-party model
data) using only the Python standard library, so this generator is
fully self-contained and free of upstream licensing constraints.

Usage
-----
    python models/generate_stl.py [--out-dir models/stl]

Run from the repository root.
"""

from __future__ import annotations

import argparse
import math
import os
import struct
from typing import Iterable, List, Sequence, Tuple

Vec3 = Tuple[float, float, float]
Tri = Tuple[Vec3, Vec3, Vec3]

# ---------------------------------------------------------------------------
# Vector helpers (kept tiny and dependency-free)
# ---------------------------------------------------------------------------


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scale(a: Vec3, s: float) -> Vec3:
    return (a[0] * s, a[1] * s, a[2] * s)


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm(a: Vec3) -> float:
    return math.sqrt(_dot(a, a))


def _unit(a: Vec3) -> Vec3:
    n = _norm(a)
    if n == 0.0:
        raise ValueError("cannot normalize zero vector")
    return _scale(a, 1.0 / n)


def _orthonormal_basis(axis: Vec3) -> Tuple[Vec3, Vec3]:
    """Return two unit vectors orthogonal to ``axis`` and to each other."""
    a = _unit(axis)
    helper: Vec3 = (1.0, 0.0, 0.0) if abs(a[0]) < 0.9 else (0.0, 1.0, 0.0)
    u = _unit(_cross(a, helper))
    v = _cross(a, u)
    return u, v


# ---------------------------------------------------------------------------
# Primitive: capped cylinder between two points (used for both struts
# and cables; cables just use a smaller radius).
# ---------------------------------------------------------------------------


def _cylinder_triangles(
    p0: Vec3, p1: Vec3, radius: float, segments: int = 20
) -> List[Tri]:
    """Triangulate a closed (capped) cylinder between p0 and p1."""
    axis = _sub(p1, p0)
    length = _norm(axis)
    if length == 0.0 or radius <= 0.0:
        return []
    u, v = _orthonormal_basis(axis)

    ring0: List[Vec3] = []
    ring1: List[Vec3] = []
    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        offset = _add(_scale(u, radius * math.cos(theta)),
                      _scale(v, radius * math.sin(theta)))
        ring0.append(_add(p0, offset))
        ring1.append(_add(p1, offset))

    tris: List[Tri] = []
    # side wall: two triangles per segment
    for i in range(segments):
        j = (i + 1) % segments
        tris.append((ring0[i], ring0[j], ring1[j]))
        tris.append((ring0[i], ring1[j], ring1[i]))
    # caps: triangle fan from each centre
    for i in range(segments):
        j = (i + 1) % segments
        tris.append((p0, ring0[j], ring0[i]))   # bottom (normal -axis)
        tris.append((p1, ring1[i], ring1[j]))   # top    (normal +axis)
    return tris


# ---------------------------------------------------------------------------
# Binary STL writer
# ---------------------------------------------------------------------------


def _write_binary_stl(path: str, triangles: Sequence[Tri], header: str = "") -> None:
    header_bytes = header.encode("ascii", errors="ignore")[:80]
    header_bytes = header_bytes.ljust(80, b" ")
    with open(path, "wb") as fh:
        fh.write(header_bytes)
        fh.write(struct.pack("<I", len(triangles)))
        for v0, v1, v2 in triangles:
            edge1 = _sub(v1, v0)
            edge2 = _sub(v2, v0)
            n = _cross(edge1, edge2)
            mag = _norm(n)
            n = _scale(n, 1.0 / mag) if mag else (0.0, 0.0, 0.0)
            fh.write(struct.pack("<3f", *n))
            fh.write(struct.pack("<3f", *v0))
            fh.write(struct.pack("<3f", *v1))
            fh.write(struct.pack("<3f", *v2))
            fh.write(struct.pack("<H", 0))


# ---------------------------------------------------------------------------
# Tensegrity model builder
# ---------------------------------------------------------------------------


def _build_triangles(
    nodes: Sequence[Vec3],
    struts: Iterable[Tuple[int, int]],
    cables: Iterable[Tuple[int, int]],
    strut_radius: float,
    cable_radius: float,
    segments: int = 20,
) -> List[Tri]:
    tris: List[Tri] = []
    for i, j in struts:
        tris.extend(_cylinder_triangles(nodes[i], nodes[j],
                                        strut_radius, segments))
    for i, j in cables:
        tris.extend(_cylinder_triangles(nodes[i], nodes[j],
                                        cable_radius, segments))
    return tris


# ---------------------------------------------------------------------------
# Specific tensegrity geometries
# ---------------------------------------------------------------------------


def n_bar_prism(
    n: int = 3,
    radius: float = 30.0,
    height: float = 60.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for a stable n-bar tensegrity prism.

    For a regular n-prism the relative twist between top and bottom
    polygons that yields a self-equilibrated (stable) tensegrity is
    ``theta = pi/2 - pi/n`` (Connelly & Whiteley, 1996; Skelton & de
    Oliveira, 2009, ch. 2).  Cables are the bottom polygon (n), top
    polygon (n) and n diagonal "saddle" cables joining bottom node *i*
    to top node ``(i+1) mod n``.
    """
    if n < 3:
        raise ValueError("n-prism requires n >= 3")
    twist = math.pi / 2.0 - math.pi / n
    bottom = [
        (radius * math.cos(2.0 * math.pi * i / n),
         radius * math.sin(2.0 * math.pi * i / n),
         0.0)
        for i in range(n)
    ]
    top = [
        (radius * math.cos(2.0 * math.pi * i / n + twist),
         radius * math.sin(2.0 * math.pi * i / n + twist),
         height)
        for i in range(n)
    ]
    nodes = bottom + top                            # indices 0..n-1, n..2n-1
    struts = [(i, n + i) for i in range(n)]         # bottom_i -> top_i
    cables: List[Tuple[int, int]] = []
    for i in range(n):
        cables.append((i, (i + 1) % n))                         # bottom ring
        cables.append((n + i, n + (i + 1) % n))                 # top ring
        cables.append((i, n + (i + 1) % n))                     # saddle
    return nodes, struts, cables


def six_strut_icosahedron(
    scale: float = 15.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for the 6-strut tensegrity icosahedron.

    Also known as the "expanded octahedron" or simply the spherical
    tensegrity.  Its self-equilibrated geometry is *Jessen's orthogonal
    icosahedron* (Jessen, 1967): the 12 vertices are the cyclic
    permutations of ``(0, +/-1, +/-2)``, the 6 struts (length 4) are
    the long edges of the three mutually orthogonal 2x4 rectangles,
    and the 24 cables (length sqrt(6)) span the remaining vertex pairs.
    The strut-to-cable length ratio is exactly ``sqrt(8/3) ~= 1.633``.

    References: Pugh, *An Introduction to Tensegrity* (1976), ch. 3;
    Skelton & de Oliveira, *Tensegrity Systems* (2009), sec. 2.4;
    Jessen, "Orthogonal icosahedra", *Nordisk Mat. Tidskr.* 15 (1967).
    """
    # Vertices grouped by the three mutually orthogonal rectangles:
    #   indices 0..3   : x = 0  rectangle (0, +/-1, +/-2)
    #   indices 4..7   : z = 0  rectangle (+/-1, +/-2, 0)
    #   indices 8..11  : y = 0  rectangle (+/-2, 0, +/-1)
    raw: List[Vec3] = [
        (0.0,  1.0,  2.0), (0.0,  1.0, -2.0),     # 0, 1
        (0.0, -1.0,  2.0), (0.0, -1.0, -2.0),     # 2, 3
        ( 1.0,  2.0, 0.0), ( 1.0, -2.0, 0.0),     # 4, 5
        (-1.0,  2.0, 0.0), (-1.0, -2.0, 0.0),     # 6, 7
        ( 2.0, 0.0,  1.0), ( 2.0, 0.0, -1.0),     # 8, 9
        (-2.0, 0.0,  1.0), (-2.0, 0.0, -1.0),     # 10, 11
    ]
    nodes = [_scale(v, scale) for v in raw]

    # The 6 struts are the long edges (length 4*scale) of the three
    # 2x4 rectangles -- two per rectangle.
    struts: List[Tuple[int, int]] = [
        (0, 1), (2, 3),       # x = 0  rectangle, long edges (share y)
        (4, 5), (6, 7),       # z = 0  rectangle, long edges (share x)
        (8, 10), (9, 11),     # y = 0  rectangle, long edges (share z)
    ]
    # The 24 cables are the inter-rectangle vertex pairs at distance
    # sqrt(6) * scale (every short edge of Jessen's orthogonal
    # icosahedron). The 6 short rectangle edges (length 2*scale) are
    # interior and carry no element.
    cables: List[Tuple[int, int]] = []
    cable_len = math.sqrt(6.0) * scale
    tol = 1e-3 * scale
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if abs(_norm(_sub(nodes[i], nodes[j])) - cable_len) < tol:
                cables.append((i, j))
    assert len(struts) == 6, f"expected 6 struts, got {len(struts)}"
    assert len(cables) == 24, f"expected 24 cables, got {len(cables)}"
    return nodes, struts, cables


def stacked_prism(
    n: int = 3,
    bays: int = 3,
    radius: float = 30.0,
    bay_height: float = 60.0,
    alternate_chirality: bool = True,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for a stacked n-bar tensegrity column.

    Multiple ``n``-bar prisms are stacked vertically (Snelson "Needle
    Tower" / mast topology) by sharing the top polygon of bay ``k`` with
    the bottom polygon of bay ``k+1``.  When ``alternate_chirality`` is
    True the twist sign flips between successive bays (the chirality
    pattern of Snelson's Needle Tower I/II, 1968-69), which is the
    classical configuration for self-equilibrated stacked tensegrity
    masts.  Each bay contributes ``n`` struts and ``3n`` cables; the top
    polygon of bay ``k`` doubles as the bottom polygon of bay ``k+1`` so
    only one polygon ring per junction is added.

    Reference: Snelson, K., *Needle Tower I/II*; Skelton & de Oliveira,
    *Tensegrity Systems* (2009), sec. 2.6 (stacked prisms).
    """
    if n < 3:
        raise ValueError("stacked prism requires n >= 3")
    if bays < 1:
        raise ValueError("stacked prism requires bays >= 1")
    twist0 = math.pi / 2.0 - math.pi / n  # stable single-bay twist
    nodes: List[Vec3] = []
    # Generate bays + 1 polygon rings, applying cumulative twist.
    cum_twist = 0.0
    for k in range(bays + 1):
        z = k * bay_height
        for i in range(n):
            ang = 2.0 * math.pi * i / n + cum_twist
            nodes.append((radius * math.cos(ang), radius * math.sin(ang), z))
        if k < bays:
            cum_twist += -twist0 if (alternate_chirality and k % 2 == 1) else twist0
    struts: List[Tuple[int, int]] = []
    cables: List[Tuple[int, int]] = []
    for k in range(bays):
        b = k * n          # bottom-ring index offset
        t = (k + 1) * n    # top-ring index offset
        for i in range(n):
            struts.append((b + i, t + i))                       # strut
            cables.append((b + i, b + (i + 1) % n))             # bottom ring
            cables.append((b + i, t + (i + 1) % n))             # saddle
        # Add the top ring of the very last bay (otherwise shared with next bay)
        if k == bays - 1:
            for i in range(n):
                cables.append((t + i, t + (i + 1) % n))
    return nodes, struts, cables


def truncated_octahedron_tensegrity(
    scale: float = 12.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for the 12-strut truncated-octahedron tensegrity.

    The Rimoli/Pajunen tensegrity-inspired metamaterial unit cell.  The
    24 nodes are the vertices of the regular truncated octahedron --
    all permutations of ``(0, +/-1, +/-2)``.  The 12 struts are the
    diagonals of the 6 square faces (2 per square; in the
    self-equilibrated configuration the two diagonals of a square do
    not physically intersect because of slight prestress-induced node
    offsets, but the topology is treated as class-1 in the original
    references).  The 36 cables are the polyhedron edges (24 hexagonal
    + 12 square).  Strut/cable length ratio is ``2 / sqrt(2) = sqrt(2)``.

    References: Rimoli, J. J., "On the impact tolerance of tensegrity-based
    planetary landers", AIAA SciTech 2016; Pajunen, K. et al., "Design
    and impact response of 3D-printable tensegrity-inspired structures",
    *Materials & Design* 182:107966, 2019.
    """
    raw: List[Vec3] = []
    base = (0.0, 1.0, 2.0)
    seen = set()
    # Generate the 24 unique permutations of (0, +/-1, +/-2).
    from itertools import permutations
    for sx in (1, -1):
        for sy in (1, -1):
            for sz in (1, -1):
                triple = (sx * base[0], sy * base[1], sz * base[2])
                for p in permutations(triple):
                    if p not in seen:
                        seen.add(p)
                        raw.append(p)
    raw.sort()
    nodes = [_scale(v, scale) for v in raw]
    # Edges of the truncated octahedron have length sqrt(2) (in raw coords).
    edge_len = math.sqrt(2.0) * scale
    # Square-face diagonals have length 2 (in raw coords).
    diag_len = 2.0 * scale
    tol = 1e-3 * scale
    cables: List[Tuple[int, int]] = []
    struts: List[Tuple[int, int]] = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            d = _norm(_sub(nodes[i], nodes[j]))
            if abs(d - edge_len) < tol:
                cables.append((i, j))
            elif abs(d - diag_len) < tol:
                # Only square-face diagonals have this length; in the
                # truncated octahedron there are exactly 12 such pairs
                # (one pair per square face of which there are 6,
                # contributing 2 diagonals each).
                struts.append((i, j))
    assert len(struts) == 12, f"expected 12 struts, got {len(struts)}"
    assert len(cables) == 36, f"expected 36 cables, got {len(cables)}"
    return nodes, struts, cables


# ---------------------------------------------------------------------------
# Additional design families from the Edison literature survey
# (cable-domes, biotensegrity, robots, deployable masts, patents,
#  bistable, cuboctahedron metamaterials).  See ``models/README.md``
# and ``edison-trajectories/2026-05-09-tensegrity-designs-fad054b3.md``.
# ---------------------------------------------------------------------------


def geiger_cable_dome(
    n_radial: int = 12,
    rings: Sequence[float] = (60.0, 40.0, 20.0),
    strut_lengths: Sequence[float] = (20.0, 30.0, 40.0),
    apex_height: float = 50.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for a Geiger-type radial cable-dome.

    Reproduces the canonical Geiger Aspension Dome topology used in the
    Seoul Olympic Gymnastics and Fencing Arenas (1986/88) and described
    by Fu (2005).  ``n_radial`` radial ribs each carry vertical struts
    of decreasing height as they progress inward across the
    concentrically nested cable rings (``rings`` = outer-to-inner radii,
    ``strut_lengths`` = corresponding strut lengths).  Each rib is
    completed by ridge cables (top of strut to top of next inner
    strut), diagonal cables (top of strut to bottom of next inner
    strut), and hoop cables (between adjacent ribs at each ring).  The
    central oculus is closed by a single tension hub at ``apex_height``.

    NB: a Geiger dome is technically a *cable-dome* rather than a
    pure class-1 tensegrity (the outer compression ring is not
    embedded in the cable network); we emit the inner radial+hoop
    cable + vertical strut pattern that *is* tensegrity-like.

    Reference: Fu, F. "Structural behavior and design methods of
    tensegrity domes."  J. Constructional Steel Research 61(1):23-35,
    2005.  Geiger, D., US Patent 4,736,553 (1988).
    """
    n = int(n_radial)
    if n < 6:
        raise ValueError("Geiger dome requires n_radial >= 6")
    if len(rings) != len(strut_lengths) or len(rings) < 2:
        raise ValueError("rings and strut_lengths must match (length >= 2)")
    nodes: List[Vec3] = []
    # For each ring we have n bottom (= node on prior outer-ring's top
    # for inner ribs) and n top (= apex of the strut at that ring).
    # Build all rings' top/bottom nodes.
    bottom_idx = [[0] * n for _ in rings]
    top_idx = [[0] * n for _ in rings]
    for r, (radius, h) in enumerate(zip(rings, strut_lengths)):
        # Accumulate height inward to model the dome curvature; the
        # 0.25 factor is a visual aspect-ratio scalar (it sets the
        # dome's rise per unit nested-ring strut accumulation -- not
        # a physical prestress quantity).
        z_base = sum(strut_lengths[:r]) * 0.25
        z_top = z_base + h
        for i in range(n):
            ang = 2.0 * math.pi * i / n
            bx, by = radius * math.cos(ang), radius * math.sin(ang)
            bottom_idx[r][i] = len(nodes)
            nodes.append((bx, by, z_base))
            top_idx[r][i] = len(nodes)
            nodes.append((bx, by, z_top))
    # Apex hub
    apex = len(nodes)
    nodes.append((0.0, 0.0, apex_height))

    struts: List[Tuple[int, int]] = []
    cables: List[Tuple[int, int]] = []
    for r in range(len(rings)):
        for i in range(n):
            # Vertical strut at every (ring, rib) station
            struts.append((bottom_idx[r][i], top_idx[r][i]))
            # Hoop cable connecting bottom rings (outer compression ring
            # for r==0 is treated as a hoop here; physically it is a
            # rigid ring, but topologically treating it as a hoop
            # cable keeps the STL simple and printable).
            cables.append((bottom_idx[r][i], bottom_idx[r][(i + 1) % n]))
            # Hoop cable connecting top of struts at this ring
            cables.append((top_idx[r][i], top_idx[r][(i + 1) % n]))
            # Ridge cable: top of this strut -> top of next inner strut
            if r + 1 < len(rings):
                cables.append((top_idx[r][i], top_idx[r + 1][i]))
                # Diagonal cable: top of this strut -> bottom of next
                # inner strut, providing the dome's prestress
                cables.append((top_idx[r][i], bottom_idx[r + 1][i]))
        # Innermost ring: cables to apex hub
        if r == len(rings) - 1:
            for i in range(n):
                cables.append((top_idx[r][i], apex))
    return nodes, struts, cables


def biotensegrity_spine(
    vertebrae: int = 4,
    scale: float = 12.0,
    spacing: float = 36.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for a stacked-icosahedron spine.

    A simplified Levin / Flemons biotensegrity spinal column: each
    "vertebra" is a 6-strut tensegrity icosahedron (Jessen's orthogonal
    icosahedron) and the vertebrae are stacked along ``+z`` with
    inter-vertebral cables connecting the top-most 4 nodes of one
    icosahedron to the bottom-most 4 nodes of the next.  This produces
    the classic tensegrity-spine topology pursued by Tom Flemons,
    Stephen Levin (Biotensegrity Archive), and the Berkeley ULTRA-Spine
    project.

    Reference: Levin, S. M., "Biotensegrity: the mechanics of fascia",
    in *Fascia: The Tensional Network of the Human Body*, 2nd ed.,
    Elsevier (2021).  Sabelhaus et al., "Inverse statics optimization
    for compound tensegrity robots", IEEE RA-L 5(3):3982-3989, 2020.
    """
    if vertebrae < 2:
        raise ValueError("spine requires >= 2 vertebrae")
    nodes: List[Vec3] = []
    struts: List[Tuple[int, int]] = []
    cables: List[Tuple[int, int]] = []
    per_vert = 12  # nodes per icosahedron
    for v in range(vertebrae):
        v_nodes, v_struts, v_cables = six_strut_icosahedron(scale=scale)
        offset = len(nodes)
        z_off = v * spacing
        for x, y, z in v_nodes:
            nodes.append((x, y, z + z_off))
        for a, b in v_struts:
            struts.append((offset + a, offset + b))
        for a, b in v_cables:
            cables.append((offset + a, offset + b))
        if v > 0:
            # Connect 4 highest nodes of previous vertebra to 4 lowest
            # nodes of this vertebra (inter-vertebral disc cables).
            prev_offset = offset - per_vert
            zs_prev = sorted(range(per_vert),
                             key=lambda i: nodes[prev_offset + i][2],
                             reverse=True)[:4]
            zs_cur = sorted(range(per_vert),
                            key=lambda i: nodes[offset + i][2])[:4]
            for a, b in zip(zs_prev, zs_cur):
                cables.append((prev_offset + a, offset + b))
    return nodes, struts, cables


def superball_with_payload(
    scale: float = 18.0,
    payload_scale: float = 6.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for the SUPERball-with-payload variant.

    The 6-strut Jessen icosahedron (the SUPERball outer structure)
    with an inner 6-strut "mini-icosahedron" suspended at the centre
    by 12 payload cables (one per outer cable's midpoint) -- the
    payload-suspension variant described by SunSpiral et al. (2015),
    used to protect the avionics box during planetary-lander rolling
    impact.

    Reference: SunSpiral, V. et al., "SUPERball: Modular Robotics for
    Planetary Exploration", NASA Ames Tech Report, 2015; Sabelhaus,
    A. P. et al., IEEE ICRA, 2015.
    """
    outer_nodes, outer_struts, outer_cables = six_strut_icosahedron(scale)
    pay_nodes, pay_struts, pay_cables = six_strut_icosahedron(payload_scale)
    nodes = list(outer_nodes)
    pay_offset = len(nodes)
    nodes.extend(pay_nodes)
    struts = list(outer_struts) + [(pay_offset + a, pay_offset + b)
                                    for a, b in pay_struts]
    cables = list(outer_cables) + [(pay_offset + a, pay_offset + b)
                                    for a, b in pay_cables]
    # Payload suspension: connect each payload node to the nearest
    # outer node (12 inner spring-cable assemblies).
    for i, p in enumerate(pay_nodes):
        # find nearest outer node
        best, best_d = 0, float("inf")
        for j, o in enumerate(outer_nodes):
            d = _norm(_sub(p, o))
            if d < best_d:
                best, best_d = j, d
        cables.append((pay_offset + i, best))
    return nodes, struts, cables


def tibert_pellegrino_mast(
    n: int = 3,
    bays: int = 6,
    radius: float = 18.0,
    bay_height: float = 30.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for a Tibert/Pellegrino deployable mast.

    A taller (default 6-bay) stacked n-prism mast with alternating
    chirality, matching the topology used in Tibert and Pellegrino's
    deployable tensegrity mast study (2003).  This is the same topology
    as ``stacked_prism`` but with parameters tuned to a slender mast
    aspect ratio (height ~10x diameter) appropriate for deployable
    space-mast applications.

    Reference: Tibert, A. G. and Pellegrino, S. "Review of Form-Finding
    Methods for Tensegrity Structures."  Int. J. Space Structures
    18(4):209-223, 2003.  Skelton & de Oliveira, ch. 2.6.
    """
    return stacked_prism(n=n, bays=bays, radius=radius,
                         bay_height=bay_height, alternate_chirality=True)


def patent_us6441801_antenna(
    n_sides: int = 6,
    bottom_radius: float = 50.0,
    top_radius: float = 30.0,
    height: float = 60.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for the Knight et al. tensegrity antenna.

    Reproduces the parallel-platform topology of US 6,441,801 B1
    (Knight, Duffy, Crane, "Deployable Antenna Reflector with
    Tensegrity Support Architecture", 2002): an upper hexagonal
    platform of radius ``top_radius`` connected to a lower hexagonal
    base of radius ``bottom_radius`` by 6 compression strut + 6
    tension tie pairs in a screw-motion-driven configuration.  Each
    upper node ``i`` is connected to lower node ``i`` by a strut and
    to lower node ``(i+1) mod n`` by a tension tie; in addition the
    upper and lower polygon edges form 12 boundary cables.

    Reference: Knight, B., Duffy, J., Crane, C. D., U.S. Patent
    6,441,801 B1, "Deployable Antenna Reflector", 27 Aug 2002.
    """
    n = int(n_sides)
    if n < 3:
        raise ValueError("antenna requires n_sides >= 3")
    nodes: List[Vec3] = []
    bottom = [(bottom_radius * math.cos(2 * math.pi * i / n),
               bottom_radius * math.sin(2 * math.pi * i / n),
               0.0) for i in range(n)]
    top = [(top_radius * math.cos(2 * math.pi * i / n + math.pi / n),
            top_radius * math.sin(2 * math.pi * i / n + math.pi / n),
            height) for i in range(n)]
    nodes.extend(bottom)
    nodes.extend(top)
    struts: List[Tuple[int, int]] = [(i, n + i) for i in range(n)]
    cables: List[Tuple[int, int]] = []
    for i in range(n):
        cables.append((i, (i + 1) % n))                 # bottom polygon
        cables.append((n + i, n + (i + 1) % n))         # top polygon
        cables.append((i, n + (i - 1) % n))             # tension tie
    return nodes, struts, cables


def bistable_double_prism(
    radius: float = 25.0,
    bay_height: float = 45.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for the Intrigila bistable double-prism.

    Two T3 prisms stacked back-to-back so their apex (twisted) polygons
    coincide, producing the bistable snap-through unit cell of
    Intrigila et al. (2022). The shared middle polygon plays the role
    of a compliant "hinge ring"; in the stereolithographically-printed
    monolithic version the snapping mechanism is realized by locally
    reduced cross-sections at the shared nodes.

    Reference: Intrigila, C. et al. "Fabrication and experimental
    characterisation of a bistable tensegrity-like unit for lattice
    metamaterials."  Additive Manufacturing 57:102946, Sep 2022.
    """
    # Both half-prisms use the standard self-equilibrated T3 twist
    # angle (pi/2 - pi/n with n = 3 -> pi/6 rad = 30 deg). The top
    # half mirrors the bottom so the shared middle ring is the
    # twisted apex of both prisms (the snap-through "hinge ring").
    twist = math.pi / 2.0 - math.pi / 3.0
    bottom = [(radius * math.cos(2 * math.pi * i / 3),
               radius * math.sin(2 * math.pi * i / 3),
               0.0) for i in range(3)]
    middle = [(radius * math.cos(2 * math.pi * i / 3 + twist),
               radius * math.sin(2 * math.pi * i / 3 + twist),
               bay_height) for i in range(3)]
    # Top polygon untwisted relative to middle (mirror of bottom prism)
    top = [(radius * math.cos(2 * math.pi * i / 3),
            radius * math.sin(2 * math.pi * i / 3),
            2.0 * bay_height) for i in range(3)]
    nodes = bottom + middle + top
    struts: List[Tuple[int, int]] = []
    cables: List[Tuple[int, int]] = []
    # Bottom T3 prism
    for i in range(3):
        struts.append((i, 3 + i))                               # strut
        cables.append((i, (i + 1) % 3))                         # bottom ring
        cables.append((3 + i, 3 + (i + 1) % 3))                 # middle ring
        cables.append((i, 3 + (i + 1) % 3))                     # saddle
    # Top T3 prism (mirror)
    for i in range(3):
        struts.append((3 + i, 6 + i))                           # strut (mirror)
        cables.append((6 + i, 6 + (i + 1) % 3))                 # top ring
        cables.append((3 + i, 6 + (i - 1) % 3))                 # mirror saddle
    return nodes, struts, cables


def snelson_x_module(
    scale: float = 30.0,
    separation: float = 4.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for Snelson's planar X-module.

    The "X-piece" is the smallest planar tensegrity module: two struts
    crossed in an "X" pattern, held by four perimeter cables along the
    quadrilateral that connects the four strut endpoints.  Because the
    struts are non-touching, they are offset in ``z`` by ``separation``
    so that the two diagonals of the unit square lie in different
    parallel planes (this is the physical Snelson realization of the
    module; in the topology graph they are class-1 disjoint).

    The X-module is the seed of Snelson's planar weave compositions
    (his X-piece sculpture lineage) and of the X-column / X-tower
    family.  It is the most buildable next addition for layered
    PETG+TPU pads: it lies flat, prints in a single planar pass, and
    tessellates trivially in 2D.

    Reference: Motro, R., *Tensegrity: Structural Systems for the
    Future* (2003), ch. 1-2.  Snelson, K., US Patent 3,169,611 (1965).
    Cowcher, S., "Design and analysis of single-layer tensegrity
    structures" (PhD thesis, 2015), pp. 11-15, 120-124.
    """
    s = scale
    h = 0.5 * separation
    nodes: List[Vec3] = [
        (0.0, 0.0, -h),     # 0: lower-left  (strut A start)
        (s,   0.0,  h),     # 1: lower-right (strut B start)
        (s,   s,   -h),     # 2: upper-right (strut A end)
        (0.0, s,    h),     # 3: upper-left  (strut B end)
    ]
    struts: List[Tuple[int, int]] = [(0, 2), (1, 3)]  # the two diagonals (do not touch)
    cables: List[Tuple[int, int]] = [(0, 1), (1, 2), (2, 3), (3, 0)]
    return nodes, struts, cables


def pugh_diamond_column(
    n: int = 3,
    bays: int = 3,
    radius: float = 20.0,
    bay_height: float = 40.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for the Pugh "diamond" stacked column.

    The diamond pattern is one of two canonical cable-routing schemes
    catalogued by Anthony Pugh (*An Introduction to Tensegrity*, 1976,
    ch. 3): each strut's bottom end is joined to **both adjacent**
    struts' bottom ends, and similarly for its top end, so the cable
    network on the side surface of a stacked prism is made up of
    diamond-shaped rhombi.  This is achieved by adding *two* saddles
    per strut between successive polygon rings (the "+1" and "-1"
    neighbours), in contrast to the single saddle of a plain stacked
    Snelson prism.

    Reference: Pugh, A., *An Introduction to Tensegrity*, UC Press
    (1976), ch. 3 ("Diamond Pattern").
    """
    if n < 3:
        raise ValueError("pugh_diamond_column requires n >= 3")
    if bays < 1:
        raise ValueError("pugh_diamond_column requires bays >= 1")
    twist0 = math.pi / 2.0 - math.pi / n
    nodes: List[Vec3] = []
    cum_twist = 0.0
    for k in range(bays + 1):
        z = k * bay_height
        for i in range(n):
            ang = 2.0 * math.pi * i / n + cum_twist
            nodes.append((radius * math.cos(ang), radius * math.sin(ang), z))
        if k < bays:
            cum_twist += -twist0 if (k % 2 == 1) else twist0
    struts: List[Tuple[int, int]] = []
    cables: List[Tuple[int, int]] = []
    for k in range(bays):
        b = k * n
        t = (k + 1) * n
        for i in range(n):
            struts.append((b + i, t + i))
            cables.append((b + i, b + (i + 1) % n))     # bottom polygon
            # Diamond saddles: each strut bottom -> both adjacent strut tops
            cables.append((b + i, t + (i + 1) % n))
            cables.append((b + i, t + (i - 1) % n))
        if k == bays - 1:
            for i in range(n):
                cables.append((t + i, t + (i + 1) % n))
    return nodes, struts, cables


def pugh_zigzag_column(
    n: int = 3,
    bays: int = 3,
    radius: float = 20.0,
    bay_height: float = 40.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for the Pugh "zig-zag" stacked column.

    The zig-zag (or "circuit") pattern of Pugh 1976 routes a single
    continuous cable in alternating up/down passes that connect each
    strut's bottom end to the *opposite* end of the next strut.  This
    produces a Z-shaped side panel between adjacent struts instead of
    the diamond / rhombus of the diamond pattern.  In the assembled
    column this is realized as ``n`` zig-zag cables per bay (each
    bottom-end ``i`` -> top-end ``(i+1) mod n`` of the same bay,
    followed by top-end ``(i+1) mod n`` -> bottom-end ``(i+2) mod n``
    of the next bay above).

    Reference: Pugh, A., *An Introduction to Tensegrity*, UC Press
    (1976), ch. 3 ("Zig-Zag Pattern").
    """
    if n < 3:
        raise ValueError("pugh_zigzag_column requires n >= 3")
    if bays < 1:
        raise ValueError("pugh_zigzag_column requires bays >= 1")
    twist0 = math.pi / 2.0 - math.pi / n
    nodes: List[Vec3] = []
    cum_twist = 0.0
    for k in range(bays + 1):
        z = k * bay_height
        for i in range(n):
            ang = 2.0 * math.pi * i / n + cum_twist
            nodes.append((radius * math.cos(ang), radius * math.sin(ang), z))
        if k < bays:
            cum_twist += -twist0 if (k % 2 == 1) else twist0
    struts: List[Tuple[int, int]] = []
    cables: List[Tuple[int, int]] = []
    for k in range(bays):
        b = k * n
        t = (k + 1) * n
        for i in range(n):
            struts.append((b + i, t + i))
            cables.append((b + i, b + (i + 1) % n))     # bottom polygon
            # Zig-zag: saddle skips one strut (jump of 2) instead of the
            # plain-prism jump of 1, producing the continuous Z-fold
            # cable pattern on each side panel.
            cables.append((b + i, t + (i + 2) % n))
        if k == bays - 1:
            for i in range(n):
                cables.append((t + i, t + (i + 1) % n))
    return nodes, struts, cables


def pentagonal_tensegrity_ring(
    n_sides: int = 5,
    radius: float = 30.0,
    height: float = 20.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for the Rhode-Barbarigos pentagonal ring.

    Approximate first-principles reconstruction of the "pentagonal
    hollow rope" / tensegrity-ring module of Rhode-Barbarigos et al.
    (Eng. Struct. 2010 / J. Struct. Eng. 2012): a closed-ring module
    with a single strut circuit and a hollow central void, used as
    the basis for the EPFL tensegrity footbridge.  Topology used here:
    ``n_sides=5`` (pentagonal) yields 10 nodes (5 top + 5 bottom),
    5 struts arranged as a zig-zag circuit between alternating top
    and bottom nodes, and 15 cables = 5 top-polygon + 5 bottom-polygon
    + 5 vertical cables.

    NB: This is the **simplified single-module topology** (consistent
    with Cowcher 2015 ch. 3 description); the full ``15 / 30 / 15``
    count quoted in Rhode-Barbarigos 2010 refers to the *deployable*
    variant with two-layer hollow-rope strands -- see the "Caveats and
    clarifications needed" section in ``models/README.md`` for the
    figures from the paper that would be needed to refine this.

    Reference: Rhode-Barbarigos, L. et al., "Designing tensegrity
    modules for pedestrian bridges", *Eng. Struct.* 32(4):1158-1167,
    2010, doi:10.1016/j.engstruct.2009.12.042.
    """
    n = int(n_sides)
    if n < 3:
        raise ValueError("pentagonal_tensegrity_ring requires n_sides >= 3")
    nodes: List[Vec3] = []
    # Bottom ring (n nodes at z=0)
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        nodes.append((radius * math.cos(ang), radius * math.sin(ang), 0.0))
    # Top ring (n nodes at z=height, twisted by pi/n for zig-zag connection)
    twist = math.pi / n
    for i in range(n):
        ang = 2.0 * math.pi * i / n + twist
        nodes.append((radius * math.cos(ang), radius * math.sin(ang), height))
    struts: List[Tuple[int, int]] = []
    cables: List[Tuple[int, int]] = []
    # Single zig-zag strut circuit visiting alternating bottom/top nodes
    for i in range(n):
        struts.append((i, n + i))  # bottom-i -> top-i (the circuit "rungs")
    # Bottom + top polygon cables
    for i in range(n):
        cables.append((i, (i + 1) % n))
        cables.append((n + i, n + (i + 1) % n))
    # Vertical / connecting cables (top-i -> bottom-(i+1) mod n)
    for i in range(n):
        cables.append((n + i, (i + 1) % n))
    return nodes, struts, cables


def cuboctahedron_tessellation(
    scale: float = 18.0,
) -> Tuple[List[Vec3], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return (nodes, struts, cables) for the Liu et al. cuboctahedron cell.

    The 12 vertices of a regular cuboctahedron are the cyclic
    permutations of ``(+/-1, +/-1, 0)`` (and their permutations); the
    cell has 24 edges (length sqrt(2)) which we emit as cables, and
    we add a central node connected to the 12 vertices by 12
    additional cables (modelling the central tension hub of Liu et
    al.'s 96-cable / 13-strut tessellation block in a simplified
    1-block representation).  6 long struts span between opposite
    vertex pairs (length 2*sqrt(2)) acting as the discontinuous
    compression skeleton.

    NB: This is a *simplified single-block representation* of Liu et
    al.'s 13-strut/96-cable tessellation (which in the original paper
    is built up by tessellating multiple cuboctahedral cells with
    shared tendon-network connectivity and 12 prestress states); we
    emit one cell so it is printable and comparable in scale to the
    other unit-cell STLs in this directory.

    Reference: Liu, K., Zegard, T., Pratapa, P. P., Paulino, G. H.
    "Unraveling tensegrity tessellations for metamaterials with
    tunable stiffness and bandgaps."  J. Mech. Phys. Solids 131:147-166,
    2019.
    """
    raw: List[Vec3] = []
    for sx in (1.0, -1.0):
        for sy in (1.0, -1.0):
            raw.append((sx * 1.0, sy * 1.0, 0.0))
            raw.append((sx * 1.0, 0.0, sy * 1.0))
            raw.append((0.0, sx * 1.0, sy * 1.0))
    nodes: List[Vec3] = [_scale(v, scale) for v in raw]
    edge_len = math.sqrt(2.0) * scale
    diag_len = 2.0 * math.sqrt(2.0) * scale
    tol = 1e-3 * scale
    cables: List[Tuple[int, int]] = []
    struts: List[Tuple[int, int]] = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            d = _norm(_sub(nodes[i], nodes[j]))
            if abs(d - edge_len) < tol:
                cables.append((i, j))
            elif abs(d - diag_len) < tol:
                struts.append((i, j))
    # Central tension hub
    hub = len(nodes)
    nodes.append((0.0, 0.0, 0.0))
    for i in range(hub):
        cables.append((i, hub))
    return nodes, struts, cables


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out-dir", default=os.path.join(os.path.dirname(__file__), "stl"),
        help="directory to write STL files into (default: models/stl)",
    )
    parser.add_argument("--strut-radius", type=float, default=2.5,
                        help="strut cylinder radius in mm (default: 2.5)")
    parser.add_argument("--cable-radius", type=float, default=1.2,
                        help="cable cylinder radius in mm (default: 1.2; "
                             "matches the 2.4 mm-Ø TPU cables in cad/t3-prism). "
                             "Cables are not literal strings -- they will be "
                             "printed in TPU -- so a non-trivial diameter is "
                             "needed to be physically realistic")
    parser.add_argument("--segments", type=int, default=24,
                        help="cylinder facet count (default: 24)")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    structures = {
        "3bar_prism.stl": (
            "3-bar tensegrity prism (T3, Snelson simplex)",
            n_bar_prism(n=3, radius=30.0, height=60.0),
        ),
        "4bar_prism.stl": (
            "4-bar tensegrity prism (T4)",
            n_bar_prism(n=4, radius=30.0, height=60.0),
        ),
        "6bar_prism.stl": (
            "6-bar tensegrity prism (T6)",
            n_bar_prism(n=6, radius=30.0, height=60.0),
        ),
        "icosahedron.stl": (
            "6-strut tensegrity icosahedron (Jessen's orthogonal icosahedron)",
            six_strut_icosahedron(scale=15.0),
        ),
        "stacked_t3_column.stl": (
            "Stacked 3-bay T3 column (Snelson 'Needle Tower' mast topology)",
            stacked_prism(n=3, bays=3, radius=20.0, bay_height=40.0),
        ),
        "truncated_octahedron.stl": (
            "Truncated-octahedron tensegrity (Rimoli/Pajunen unit cell)",
            truncated_octahedron_tensegrity(scale=12.0),
        ),
        "geiger_cable_dome.stl": (
            "Geiger cable-dome (Seoul Olympic Hall topology)",
            geiger_cable_dome(n_radial=12,
                              rings=(60.0, 40.0, 20.0),
                              strut_lengths=(20.0, 25.0, 30.0),
                              apex_height=55.0),
        ),
        "biotensegrity_spine.stl": (
            "Biotensegrity spine (4 stacked Jessen-icosahedron vertebrae)",
            biotensegrity_spine(vertebrae=4, scale=12.0, spacing=36.0),
        ),
        "superball_with_payload.stl": (
            "NASA SUPERball with inner payload (6-strut + payload icosahedron)",
            superball_with_payload(scale=18.0, payload_scale=6.0),
        ),
        "tibert_pellegrino_mast.stl": (
            "Tibert/Pellegrino deployable mast (6-bay alternating-chirality)",
            tibert_pellegrino_mast(n=3, bays=6, radius=18.0, bay_height=30.0),
        ),
        "patent_us6441801_antenna.stl": (
            "Knight et al. tensegrity antenna (US 6,441,801 B1)",
            patent_us6441801_antenna(n_sides=6, bottom_radius=50.0,
                                     top_radius=30.0, height=60.0),
        ),
        "bistable_double_prism.stl": (
            "Bistable double-prism (Intrigila 2022)",
            bistable_double_prism(radius=25.0, bay_height=45.0),
        ),
        "cuboctahedron_tessellation.stl": (
            "Cuboctahedron tensegrity tessellation cell (Liu et al. 2019)",
            cuboctahedron_tessellation(scale=18.0),
        ),
        "snelson_x_module.stl": (
            "Snelson planar X-module (2 struts, 4 cables)",
            snelson_x_module(scale=60.0, separation=6.0),
        ),
        "pugh_diamond_column.stl": (
            "Pugh diamond-pattern stacked column (3-bay T3)",
            pugh_diamond_column(n=3, bays=3, radius=20.0, bay_height=40.0),
        ),
        "pugh_zigzag_column.stl": (
            "Pugh zig-zag-pattern stacked column (3-bay T3)",
            pugh_zigzag_column(n=3, bays=3, radius=20.0, bay_height=40.0),
        ),
        "pentagonal_tensegrity_ring.stl": (
            "Pentagonal tensegrity-ring module (Rhode-Barbarigos 2010, simplified)",
            pentagonal_tensegrity_ring(n_sides=5, radius=30.0, height=20.0),
        ),
    }

    for filename, (label, (nodes, struts, cables)) in structures.items():
        tris = _build_triangles(
            nodes, struts, cables,
            strut_radius=args.strut_radius,
            cable_radius=args.cable_radius,
            segments=args.segments,
        )
        out_path = os.path.join(args.out_dir, filename)
        _write_binary_stl(out_path, tris, header=label)
        print(f"wrote {out_path}: {len(nodes)} nodes, {len(struts)} struts, "
              f"{len(cables)} cables, {len(tris)} triangles")


if __name__ == "__main__":
    main()
