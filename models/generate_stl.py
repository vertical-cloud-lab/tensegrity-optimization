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
    parser.add_argument("--cable-radius", type=float, default=0.5,
                        help="cable cylinder radius in mm (default: 0.5)")
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
        "icosahedron.stl": (
            "6-strut tensegrity icosahedron (Jessen's orthogonal icosahedron)",
            six_strut_icosahedron(scale=15.0),
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
