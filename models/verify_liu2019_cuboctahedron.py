"""Check the Liu et al. (2019) cuboctahedron block against the paper.

Verifies the data in ``models/data/liu2019_cuboctahedron_*.csv`` against
Table A1 of Liu, Zegard, Pratapa & Paulino, *J. Mech. Phys. Solids*
131:147-166 (2019), and reports the member clearances that decide how fat
the printed struts and cables can be.

Exits non-zero if any check fails. Run from the repository root::

    python models/verify_liu2019_cuboctahedron.py
"""
import itertools
import math
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "models"))
from generate_stl import (  # noqa: E402
    LIU2019_MIN_STRUT_CABLE_CLEARANCE, LIU2019_MIN_STRUT_STRUT_CLEARANCE,
    _load_liu2019_cuboctahedron_block,
)

# Table A1, "Cuboctahedron" row.
PAPER = dict(N_V=40, N_B=109, N_S=13, cls=1, R_rz=0.75, PS=12, KI=17)
PRIMITIVE = ((2.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 2.0))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def segment_distance(p1, p2, p3, p4):
    """Shortest distance between segments p1-p2 and p3-p4."""
    u, v, w = _sub(p2, p1), _sub(p4, p3), _sub(p1, p3)
    a, b, c = _dot(u, u), _dot(u, v), _dot(v, v)
    d, e = _dot(u, w), _dot(v, w)
    det = a * c - b * b
    if abs(det) < 1e-12:
        s, t = 0.0, (e / c if c > 1e-12 else 0.0)
    else:
        s, t = (b * e - c * d) / det, (a * e - b * d) / det
    s, t = min(max(s, 0.0), 1.0), min(max(t, 0.0), 1.0)
    gap = [w[k] + s * u[k] - t * v[k] for k in range(3)]
    return math.sqrt(_dot(gap, gap))


def closest_approach(nodes, group_a, group_b, within_group=False):
    pairs = (itertools.combinations(group_a, 2) if within_group
             else itertools.product(group_a, group_b))
    best, where = float("inf"), None
    for (a, b), (c, d) in pairs:
        if len({a, b, c, d}) < 4:  # members sharing a node always touch
            continue
        gap = segment_distance(nodes[a], nodes[b], nodes[c], nodes[d])
        if gap < best:
            best, where = gap, ((a, b), (c, d))
    return best, where


def periodic_group_of(point):
    """Index of the node's equivalence class under the primitive vectors."""
    # The primitive vectors are axis-aligned, so each axis folds on its own.
    periods = [PRIMITIVE[k][k] for k in range(3)]
    return tuple(round((coord + p / 2.0) % p - p / 2.0, 6)
                 for coord, p in zip(point, periods))


def main() -> int:
    nodes, struts, cables, prestress = _load_liu2019_cuboctahedron_block()
    members = struts + cables
    failures = []

    def check(name, got, want):
        ok = got == want
        print(f"{'ok  ' if ok else 'FAIL'} {name}: {got} (paper: {want})")
        if not ok:
            failures.append(name)

    check("nodes N_V", len(nodes), PAPER["N_V"])
    check("members N_B", len(members), PAPER["N_B"])
    check("struts N_S", len(struts), PAPER["N_S"])

    # Self-balanced prestress: sum of force * unit vector is zero at every
    # node. Periodicity is deliberately not imposed here, because the paper
    # does not impose it on the equilibrium constraint either.
    residual = [[0.0, 0.0, 0.0] for _ in nodes]
    for (i, j), force in zip(members, prestress):
        direction = _sub(nodes[j], nodes[i])
        length = math.sqrt(_dot(direction, direction))
        for k in range(3):
            residual[i][k] += force * direction[k] / length
            residual[j][k] -= force * direction[k] / length
    worst = max(max(abs(c) for c in r) for r in residual)
    ok = worst < 1e-9
    print(f"{'ok  ' if ok else 'FAIL'} self-balanced prestress: "
          f"max nodal residual {worst:.2e}")
    if not ok:
        failures.append("self-balanced prestress")

    # Class-1 globally: no periodic node group carries more than one strut.
    per_group: dict = {}
    for i, j in struts:
        for end in (i, j):
            key = periodic_group_of(nodes[end])
            per_group[key] = per_group.get(key, 0) + 1
    check("max struts per periodic node group", max(per_group.values()),
          PAPER["cls"])

    # Restriction zone: nothing may cross the sphere of radius R_rz.
    origin = (0.0, 0.0, 0.0)
    nearest = min(segment_distance(nodes[i], nodes[j], origin, origin)
                  for i, j in members)
    ok = nearest >= PAPER["R_rz"] - 1e-9
    print(f"{'ok  ' if ok else 'FAIL'} restriction zone kept clear: nearest "
          f"member passes {nearest:.4f} from the centroid "
          f"(paper R_rz: {PAPER['R_rz']})")
    if not ok:
        failures.append("restriction zone")

    # Fabrication clearances, in the paper's units.
    ss, ss_where = closest_approach(nodes, struts, None, within_group=True)
    sc, sc_where = closest_approach(nodes, struts, cables)
    cc, _ = closest_approach(nodes, cables, None, within_group=True)
    print(f"     closest strut-strut approach {ss:.4f} at {ss_where}")
    print(f"     closest strut-cable approach {sc:.4f} at {sc_where}")
    print(f"     closest cable-cable approach {cc:.4f}")
    for name, measured, constant in (
            ("strut-strut clearance constant", ss,
             LIU2019_MIN_STRUT_STRUT_CLEARANCE),
            ("strut-cable clearance constant", sc,
             LIU2019_MIN_STRUT_CABLE_CLEARANCE)):
        ok = abs(measured - constant) < 5e-5
        print(f"{'ok  ' if ok else 'FAIL'} {name}: {constant}")
        if not ok:
            failures.append(name)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed: {', '.join(failures)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
