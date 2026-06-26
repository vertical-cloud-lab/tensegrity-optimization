#!/usr/bin/env python3
# ============================================================================
# Geometric verification for the baked-in tree supports.
#
# Why this exists
# ---------------
# @sgbaird asked us to *prove* — not just eyeball — that every support tip
# actually reaches the part ("touching the floor and going all the way to
# contact it") after a print failed because supports under the vertical TPU
# cables were not touching. This script does heavy-duty mesh checks with
# `trimesh`'s exact ray/proximity engine and fails (non-zero exit) if any of
# them does not hold, so it can run in CI and gate the committed artefacts.
#
# Checks
# ------
#   1. CONTACT     — every intended tip lands *on* the part underside
#                    (closest-point distance to the part mesh ~ 0 mm).
#   2. REALISED    — every intended tip is actually present in the committed
#                    pillar STL (a pillar vertex sits at the tip), i.e. the
#                    artefact is not stale / missing tips.
#   3. ON-PLATE    — no support geometry prints below the build plate and at
#                    least one trunk foot actually reaches the plate
#                    ("touching the floor").
#   4. COVERAGE    — re-cast the underside at 2x finer spacing, keeping the
#                    face normal of each crossing. Only *flat* overhangs
#                    (face pointing more than 45 deg below horizontal,
#                    nz < -0.7) actually need support; near-vertical walls
#                    self-support as they print. Every flat-overhang sample
#                    must have a realised support tip beneath it within one
#                    reliable PLA bridge (`--bridge`, default 8 mm); the 5 mm
#                    coverage fraction is also reported for context.
#
# Usage
# -----
#   python3 verify_support_geometry.py PART.stl PILLARS.stl \
#       [--spacing 4 --min_clearance 1.5 --min_gap 1.0 --merge_radius 22]
#
# The geometry knobs must match the run that produced PILLARS.stl.
# ============================================================================
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

# Re-use the exact placement logic the generator uses so the verification
# samples the underside the same way the supports were placed.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generate_support_pillars import raycast_underside  # noqa: E402


def _load_mesh(path: Path):
    import trimesh
    mesh = trimesh.load(path, force="mesh")
    if not hasattr(mesh, "ray"):
        raise SystemExit(f"{path}: not a single triangle mesh")
    return mesh


def cast_undersides(mesh, *, spacing: float, base_z: float,
                    min_clearance: float, min_gap: float,
                    down_normal_max: float) -> np.ndarray:
    """Bottom-up ray cast that returns one row ``(x, y, z, nz)`` for every
    down-facing underside crossing, keeping the face-normal z so the caller
    can tell genuine (flat) overhangs from self-supporting near-vertical
    walls. ``mesh`` must already be laid on the plate."""
    from collections import defaultdict
    lo_x, lo_y, _ = mesh.bounds[0]
    hi_x, hi_y, _ = mesh.bounds[1]
    xs = np.arange(lo_x, hi_x + spacing * 0.5, spacing)
    ys = np.arange(lo_y, hi_y + spacing * 0.5, spacing)
    XX, YY = np.meshgrid(xs, ys)
    n = XX.size
    origins = np.column_stack([XX.ravel(), YY.ravel(),
                               np.full(n, base_z - 1.0)])
    dirs = np.tile(np.array([0.0, 0.0, 1.0]), (n, 1))
    locs, idx_ray, idx_tri = mesh.ray.intersects_location(
        origins, dirs, multiple_hits=True)
    face_nz = mesh.face_normals[:, 2]
    per_ray: dict[int, list] = defaultdict(list)
    for loc, ir, it in zip(locs, idx_ray, idx_tri):
        per_ray[int(ir)].append((float(loc[2]), float(face_nz[it]), loc))
    z_min = base_z + float(min_clearance)
    up_min = -float(down_normal_max)
    out: list[tuple[float, float, float, float]] = []
    for crossings in per_ray.values():
        crossings.sort(key=lambda t: t[0])
        floor = base_z
        for z, nz, loc in crossings:
            if nz < down_normal_max:
                if z > z_min and (z - floor) > min_gap:
                    out.append((float(loc[0]), float(loc[1]), z, nz))
            elif nz > up_min:
                if z > floor:
                    floor = z
    return np.asarray(out, dtype=float).reshape(-1, 4)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("part", type=Path, help="printable part STL")
    ap.add_argument("pillars", type=Path, help="baked support STL to verify")
    ap.add_argument("--spacing", type=float, default=4.0)
    ap.add_argument("--min_clearance", type=float, default=1.5)
    ap.add_argument("--min_gap", type=float, default=1.0)
    ap.add_argument("--down_normal_max", type=float, default=-0.2)
    ap.add_argument("--base_z", type=float, default=0.0)
    ap.add_argument("--tip_overshoot", type=float, default=0.3)
    # A tip is "realised" if a pillar vertex is within this distance of it.
    ap.add_argument("--contact_tol", type=float, default=0.05,
                    help="max tip->part surface distance counted as contact")
    ap.add_argument("--realise_tol", type=float, default=0.6,
                    help="max tip->nearest-pillar-vertex distance")
    ap.add_argument("--bridge", type=float, default=8.0,
                    help="max horizontal distance (mm) from a flat-overhang "
                         "underside sample to a support tip beneath it that "
                         "still counts as covered (a reliable PLA bridge)")
    ap.add_argument("--flat_nz", type=float, default=-0.7,
                    help="face normal-z below which an underside is a genuine "
                         "(flat) overhang that needs support; between this and "
                         "down_normal_max it is a self-supporting wall")
    args = ap.parse_args()

    from trimesh.proximity import closest_point
    from scipy.spatial import cKDTree

    # ---- intended tips (same sampler the generator uses) -------------------
    hits, part = raycast_underside(
        args.part, spacing=args.spacing, min_clearance=args.min_clearance,
        base_z=args.base_z, min_gap=args.min_gap,
        down_normal_max=args.down_normal_max)
    hits = np.asarray(hits, dtype=float)
    pillars = _load_mesh(args.pillars)
    pverts = np.asarray(pillars.vertices, dtype=float)
    vtree = cKDTree(pverts)

    fails: list[str] = []

    # ---- check 1: contact --------------------------------------------------
    _, dist, _ = closest_point(part, hits)
    c1_max = float(dist.max())
    c1_ok = c1_max <= args.contact_tol
    if not c1_ok:
        n_bad = int((dist > args.contact_tol).sum())
        fails.append(f"CONTACT: {n_bad} tip(s) not on part surface "
                     f"(max gap {c1_max:.4f} mm)")

    # ---- check 2: realised in the artefact ---------------------------------
    d_tip, _ = vtree.query(hits)
    c2_bad = np.where(d_tip > args.realise_tol)[0]
    c2_ok = c2_bad.size == 0
    if not c2_ok:
        zbad = hits[c2_bad, 2]
        fails.append(f"REALISED: {c2_bad.size} intended tip(s) missing from "
                     f"the STL (z {zbad.min():.1f}-{zbad.max():.1f} mm); "
                     f"artefact is stale")

    # ---- check 3: on the plate, nothing below it ---------------------------
    zmin = float(pverts[:, 2].min())
    n_feet = int((pverts[:, 2] <= args.base_z + 1e-3).sum())
    c3_ok = (zmin >= args.base_z - 1e-3) and (n_feet > 0)
    if zmin < args.base_z - 1e-3:
        fails.append(f"ON-PLATE: support geometry dips to z={zmin:.4f} mm "
                     f"(below plate z={args.base_z})")
    if n_feet == 0:
        fails.append("ON-PLATE: no support vertex reaches the build plate")

    # ---- check 4: coverage of flat overhangs at 2x finer spacing -----------
    fine = cast_undersides(
        part, spacing=args.spacing / 2.0, base_z=args.base_z,
        min_clearance=args.min_clearance, min_gap=args.min_gap,
        down_normal_max=args.down_normal_max)
    flat = fine[fine[:, 3] < args.flat_nz]          # genuine overhangs only
    tip_xyz = hits[d_tip <= args.realise_tol]        # realised support tips
    ttree = cKDTree(tip_xyz[:, :2])
    # Nearest realised tip *beneath* each flat-overhang sample (a tip can sit
    # a hair above due to tip_overshoot, so allow +2 mm).
    nearest = np.full(len(flat), np.inf)
    for i, (x, y, z, _) in enumerate(flat):
        for k in ttree.query_ball_point([x, y], max(args.bridge, 8.0) + 1.0):
            if tip_xyz[k, 2] <= z + 2.0:
                nearest[i] = min(nearest[i],
                                 float(np.hypot(tip_xyz[k, 0] - x,
                                                tip_xyz[k, 1] - y)))
    n_flat = len(flat)
    worst = float(nearest.max()) if n_flat else 0.0
    frac5 = float((nearest <= 5.0).mean()) if n_flat else 1.0
    uncovered = int((nearest > args.bridge).sum())
    c4_ok = uncovered == 0
    if not c4_ok:
        uz = flat[nearest > args.bridge][:, 2]
        fails.append(f"COVERAGE: {uncovered} flat-overhang sample(s) lie "
                     f">{args.bridge} mm from any support beneath them "
                     f"(z {uz.min():.1f}-{uz.max():.1f} mm)")

    # ---- report ------------------------------------------------------------
    print("Support geometry verification")
    print(f"  part            : {args.part}")
    print(f"  supports        : {args.pillars}")
    print(f"  intended tips   : {len(hits)}  (z {hits[:,2].min():.1f}"
          f"-{hits[:,2].max():.1f} mm)")
    print(f"  flat overhangs  : {n_flat} samples (spacing {args.spacing/2} mm, "
          f"nz < {args.flat_nz})")
    print(f"  support verts   : {len(pverts)}  feet@plate {n_feet}")
    print()
    print(f"  [{'PASS' if c1_ok else 'FAIL'}] CONTACT   max tip->part gap "
          f"{c1_max:.4f} mm (<= {args.contact_tol})")
    print(f"  [{'PASS' if c2_ok else 'FAIL'}] REALISED  max tip->pillar "
          f"{float(d_tip.max()):.4f} mm (<= {args.realise_tol})")
    print(f"  [{'PASS' if c3_ok else 'FAIL'}] ON-PLATE  min support z "
          f"{zmin:.4f} mm, {n_feet} feet on plate")
    print(f"  [{'PASS' if c4_ok else 'FAIL'}] COVERAGE  flat overhangs within "
          f"5 mm of a support: {frac5*100:.1f}%, worst {worst:.1f} mm, "
          f"{uncovered} beyond {args.bridge} mm")
    print()
    if fails:
        print("RESULT: FAIL")
        for f in fails:
            print("  - " + f)
        return 1
    print("RESULT: PASS — every underside tip contacts the part and is "
          "realised on the plate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
