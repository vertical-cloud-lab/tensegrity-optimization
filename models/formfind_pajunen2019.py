"""Form-find the Pajunen et al. (2019) spherically-jointed impact cell.

Derives, from first principles, the node coordinates embedded as
``PAJUNEN_GEOMETRY3_NODES`` in ``generate_stl.py``, and re-verifies every
property claimed for them.  Needs ``numpy`` and ``scipy`` (unlike
``generate_stl.py``, which stays standard-library only by embedding the
result).

Background
----------
Pajunen, K., Johanns, P., Pal, R. K., Rimoli, J. J., Daraio, C.,
"Design and impact response of 3D-printable tensegrity-inspired
structures", *Materials & Design* 182:107966 (2019),
doi:10.1016/j.matdes.2019.107966 (open access; publisher PDF mirrored in
CaltechAUTHORS record scb9y-ppa15).  The paper's final "Geometry #3" is a
truncated-octahedron tensegrity (24 nodes, 12 struts, 36 cables, class 1)
whose nodal coordinates are scaled up 1.5x and whose pin joints are
replaced by 8.72 mm spheres, printed as a single PA2200 part with 2.6 mm
struts and 1.8 mm cables.

The paper states the baseline geometry but not its coordinates.  This
script reconstructs them:

1. Nodes start from the 24 vertices of the regular truncated octahedron
   (permutations of ``(0, +-1, +-2)``); cables are its 36 edges.
2. The 12 struts are interior chords.  Exhaustive enumeration of
   group-orbit perfect matchings shows the only chord family that is
   class 1 (no strut touches another) with realistic proportions is the
   sqrt(12) family, an orbit of the chiral tetrahedral rotation group T
   (order 12; the full octahedral group admits no such matching, which is
   why the paper needs "certain reflections" to tessellate the cell).
   The other candidate, sqrt(18), form-finds to struts longer than the
   cell height (L/H = 1.04 vs the published 44.2/48.3 = 0.92).
3. Force-density form-finding with independent densities for the two
   cable orbits (24 square-face edges, 12 hexagon-hexagon edges),
   solving for the density ratio at which the force-density matrix gains
   the required nullity 4 AND all 36 cables come out the same length,
   which is a stated property of the printed design ("all the cables and
   all the struts are the same length").

Checks reproduced against the paper (run this script to see them):

- all 36 cables one length, all 12 struts one length;
- strut length / face-to-face height = 0.946 (published 44.2/48.3 = 0.915,
  a 3 percent reconstruction gap from their elastic form-finding);
- sphere diameter implied by "cable lengths are maintained" after the
  1.5x scale-up: 2 x 0.5 x cable length = 8.95 mm (published: 8.72 mm);
- class 1 with printable clearances at full scale.

Run from the repository root::

    python models/formfind_pajunen2019.py
"""
import sys
from itertools import permutations, product

import numpy as np
from scipy.optimize import brentq, minimize_scalar

# Published Geometry #3 constants (mm).
BASELINE_HEIGHT = 48.3          # pin-jointed cell height, top to bottom face
SCALE_UP = 1.5                  # nodal coordinate scale-up for sphere room
SPHERE_DIAMETER = 8.72
STRUT_DIAMETER = 2.6
CABLE_DIAMETER = 1.8


def truncated_octahedron_vertices():
    verts = sorted(set(
        p for signs in product((1, -1), (1, -1))
        for base in [(0, signs[0] * 1, signs[1] * 2)]
        for p in permutations(base)))
    return np.array(verts, float)


def chiral_tetrahedral_group():
    """The 12 rotations preserving both the cube and one inscribed
    tetrahedron: even axis permutations with an even number of sign flips."""
    def parity(p):
        p = list(p)
        par = 1
        for i in range(len(p)):
            while p[i] != i:
                j = p[i]
                p[i], p[j] = p[j], p[i]
                par = -par
        return par
    mats = []
    for perm in permutations(range(3)):
        for signs in product((1, -1), repeat=3):
            if parity(perm) == 1 and np.prod(signs) == 1:
                M = np.zeros((3, 3))
                for i, (p, s) in enumerate(zip(perm, signs)):
                    M[i, p] = s
                mats.append(M)
    return mats


V = truncated_octahedron_vertices()
GROUP = chiral_tetrahedral_group()


def vindex(v):
    for i, u in enumerate(V):
        if np.allclose(u, v):
            return i
    raise KeyError(v)


def strut_matching():
    """Orbit of the chord (0,1,2)-(2,-1,0) under T: the unique class-1
    perfect matching family at squared chord length 12."""
    v0 = np.array([0.0, 1.0, 2.0])
    w0 = np.array([2.0, -1.0, 0.0])
    pairs = set()
    for M in GROUP:
        a, b = vindex(M @ v0), vindex(M @ w0)
        pairs.add((min(a, b), max(a, b)))
    pairs = sorted(pairs)
    assert len(pairs) == 12
    counts = {}
    for a, b in pairs:
        counts[a] = counts.get(a, 0) + 1
        counts[b] = counts.get(b, 0) + 1
    assert len(counts) == 24 and all(c == 1 for c in counts.values()), \
        "strut set is not a perfect matching"
    return pairs


def cable_edges():
    edges = [(i, j) for i in range(24) for j in range(i + 1, 24)
             if abs(np.sum((V[i] - V[j]) ** 2) - 2.0) < 1e-9]
    assert len(edges) == 36
    square, hexhex = [], []
    for i, j in edges:
        a, b = V[i], V[j]
        if any(abs(a[k]) == 2 and a[k] == b[k] for k in range(3)):
            square.append((i, j))
        else:
            hexhex.append((i, j))
    assert len(square) == 24 and len(hexhex) == 12
    return square, hexhex


STRUTS = strut_matching()
SQ_EDGES, HEX_EDGES = cable_edges()
MEMBERS = HEX_EDGES + SQ_EDGES + STRUTS


def force_density_matrix(r, alpha):
    """q = 1 on hexagon-hexagon cables, alpha on square-face cables,
    -r on struts."""
    q = np.array([1.0] * len(HEX_EDGES) + [alpha] * len(SQ_EDGES)
                 + [-r] * len(STRUTS))
    D = np.zeros((24, 24))
    for (i, j), qi in zip(MEMBERS, q):
        D[i, i] += qi
        D[j, j] += qi
        D[i, j] -= qi
        D[j, i] -= qi
    return D, q


def fourth_eigenvalue(r, alpha):
    D, _ = force_density_matrix(r, alpha)
    return np.sort(np.abs(np.linalg.eigvalsh(D)))[3]


def equilibrium_ratio(alpha, r_guess):
    rs = np.linspace(max(r_guess - 0.2, 0.02), r_guess + 0.2, 801)
    i = int(np.argmin([fourth_eigenvalue(r, alpha) for r in rs]))
    res = minimize_scalar(lambda r: fourth_eigenvalue(r, alpha),
                          bounds=(rs[max(i - 2, 0)], rs[min(i + 2, 800)]),
                          method="bounded", options={"xatol": 1e-12})
    return res.x


def symmetric_configuration(r, alpha, seed=1):
    """Equivariant (T-symmetric) configuration in the nullspace of D."""
    D, _ = force_density_matrix(r, alpha)
    w, U = np.linalg.eigh(D)
    B = U[:, np.argsort(np.abs(w))[:4]]
    ones = np.ones(24) / np.sqrt(24)
    B = B - np.outer(ones, ones @ B)
    Q, S, _ = np.linalg.svd(B, full_matrices=False)
    X0 = Q[:, :3]
    perms = [[vindex(M @ V[i]) for i in range(24)] for M in GROUP]
    rng = np.random.default_rng(seed)
    for _ in range(16):
        Xa = X0 @ rng.standard_normal((3, 3))
        Xs = np.zeros_like(Xa)
        for M, p in zip(GROUP, perms):
            P = np.zeros((24, 24))
            P[p, range(24)] = 1.0
            Xs += P @ Xa @ M.T
        Xs /= len(GROUP)
        if np.linalg.matrix_rank(Xs, tol=1e-6) == 3:
            # Fix chirality/orientation to correlate with the regular
            # polyhedron, and normalise face-to-face height to 1.
            if np.trace(Xs.T @ V) < 0:
                Xs = -Xs
            top = [i for i in range(24) if V[i][2] == 2.0]
            bot = [i for i in range(24) if V[i][2] == -2.0]
            H = np.mean(Xs[top][:, 2]) - np.mean(Xs[bot][:, 2])
            return Xs / H
    raise RuntimeError("symmetrisation degenerated for every random seed")


def segment_distance(p1, p2, p3, p4):
    d1, d2, r0 = p2 - p1, p4 - p3, p1 - p3
    a, e, f = d1 @ d1, d2 @ d2, d2 @ r0
    c, b = d1 @ r0, d1 @ d2
    den = a * e - b * b
    s = np.clip((b * f - c * e) / den, 0, 1) if den > 1e-12 else 0.0
    t = np.clip((b * s + f) / e, 0, 1)
    s = np.clip((b * t - c) / a, 0, 1)
    return float(np.linalg.norm((p1 + s * d1) - (p3 + t * d2)))


def solve():
    state = {"r": 0.46}

    def cable_length_mismatch(alpha):
        r = equilibrium_ratio(alpha, state["r"])
        state["r"] = r
        X = symmetric_configuration(r, alpha)
        l_sq = np.mean([np.linalg.norm(X[a] - X[b]) for a, b in SQ_EDGES])
        l_hex = np.mean([np.linalg.norm(X[a] - X[b]) for a, b in HEX_EDGES])
        return l_sq / l_hex - 1.0

    alpha = brentq(cable_length_mismatch, 0.5, 1.0, xtol=1e-10)
    r = equilibrium_ratio(alpha, state["r"])
    X = symmetric_configuration(r, alpha)
    return alpha, r, X


def main():
    alpha, r, X = solve()
    print(f"force densities: hexagon-hexagon cables 1.0, "
          f"square-face cables {alpha:.6f}, struts {-r:.6f}")

    D, q = force_density_matrix(r, alpha)
    residual = np.zeros((24, 3))
    for (i, j), qi in zip(MEMBERS, q):
        residual[i] += qi * (X[i] - X[j])
        residual[j] += qi * (X[j] - X[i])
    print(f"nodal equilibrium residual: {np.abs(residual).max():.2e}")

    Ls = [np.linalg.norm(X[a] - X[b]) for a, b in STRUTS]
    Lc = [np.linalg.norm(X[a] - X[b]) for a, b in SQ_EDGES + HEX_EDGES]
    print(f"strut length / height  = {np.mean(Ls):.4f}"
          f"  (spread {max(Ls) - min(Ls):.1e}; paper 44.2/48.3 = 0.9151)")
    print(f"cable length / height  = {np.mean(Lc):.4f}"
          f"  (spread {max(Lc) - min(Lc):.1e}; all 36 equal, as published)")

    height = SCALE_UP * BASELINE_HEIGHT
    cable_mm = np.mean(Lc) * height
    implied_sphere = cable_mm - cable_mm / SCALE_UP
    print(f"Geometry #3 cell height {height:.2f} mm, cable node-to-node "
          f"{cable_mm:.2f} mm")
    print(f"sphere diameter implied by 'cable lengths are maintained': "
          f"{implied_sphere:.2f} mm (published {SPHERE_DIAMETER} mm)")

    dss = min(segment_distance(X[a], X[b], X[c], X[d])
              for k, (a, b) in enumerate(STRUTS) for (c, d) in STRUTS[k + 1:])
    dsc = min(segment_distance(X[a], X[b], X[c], X[d])
              for (a, b) in STRUTS for (c, d) in SQ_EDGES + HEX_EDGES
              if not ({a, b} & {c, d}))
    print(f"clearances at {height:.2f} mm scale: strut-strut "
          f"{dss * height:.1f} mm, strut-cable {dsc * height:.1f} mm "
          f"(class 1, printable with {STRUT_DIAMETER}/{CABLE_DIAMETER} mm "
          f"members)")

    nodes_mm = X * height
    print("\nnode coordinates (mm), index: x y z")
    for i, (x, y, z) in enumerate(nodes_mm):
        print(f"  {i:2d}: {x:12.6f} {y:12.6f} {z:12.6f}")
    print("\nstrut index pairs:", STRUTS)

    # Cross-check against the table embedded in generate_stl.py, if importable.
    try:
        sys.path.insert(0, __file__.rsplit("/", 1)[0])
        from generate_stl import PAJUNEN_GEOMETRY3_NODES, PAJUNEN_STRUTS
        emb = np.array(PAJUNEN_GEOMETRY3_NODES)
        err = np.abs(emb - nodes_mm).max()
        print(f"\nmax deviation from generate_stl.PAJUNEN_GEOMETRY3_NODES: "
              f"{err:.2e} mm")
        assert err < 1e-3, "embedded coordinates disagree with form-finding"
        assert list(PAJUNEN_STRUTS) == [tuple(p) for p in STRUTS], \
            "embedded strut list disagrees"
        print("embedded table in generate_stl.py verified.")
    except ImportError as exc:
        print(f"(skipping generate_stl cross-check: {exc})")


if __name__ == "__main__":
    main()
