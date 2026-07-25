#!/usr/bin/env python3
"""Verify the anti-wobble tendon guide cages against the part mesh.

Companion to ``verify_support_geometry.py`` for the ``--cage`` output of
``generate_support_pillars.py`` (see the tendon-cage section of README.md).
The cages are the opposite contract to the tree supports: they must reach
the plate and surround each tendon, but must **never touch the part**.
Exits non-zero on any failure so it can gate CI.

Checks
------
NO-CONTACT   every cage vertex is outside the part, at least --min_standoff
             from its surface (cages bound wobble, they never fuse on).
ON-PLATE     no cage geometry below base_z; feet actually land on the plate.
ENCIRCLE     at sampled heights along each tendon the cage vertices surround
             the tendon axis: the largest empty azimuth gap stays within the
             designed C-ring opening (+ slack), i.e. no missing pillar.
REMOVABLE    each ring's opening chord is at least --min_squeeze x the
             tendon diameter, so the finished cage squeezes off the soft
             TPU tendon sideways (a chord *above* the diameter would be an
             escape corridor during the print — see sweep_cage_design.py).

Usage
-----
    python3 verify_cage_geometry.py \
        --part /tmp/t3-prism.stl \
        --cages t3-prism-pr35-cages.stl \
        --report t3-prism-pr35-cage-report.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh


def _fail(msg: str) -> None:
    print(f"FAIL  {msg}")
    sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--part", type=Path, required=True,
                    help="Printable part STL the cages were generated from.")
    ap.add_argument("--cages", type=Path, required=True,
                    help="Cage-only STL (generate_support_pillars.py --cage_only).")
    ap.add_argument("--report", type=Path, required=True,
                    help="JSON report written via --cage_report.")
    ap.add_argument("--min_standoff", type=float, default=0.3,
                    help="Minimum allowed cage-to-part surface distance (mm). "
                         "Default 0.3 (design clearance is >= 0.8).")
    ap.add_argument("--min_squeeze", type=float, default=0.75,
                    help="Minimum ring-opening chord / tendon diameter for "
                         "REMOVABLE (soft-TPU squeeze-out). Overridden by "
                         "the report's own 'squeeze' value when present. "
                         "Default 0.75.")
    ap.add_argument("--gap_slack_deg", type=float, default=45.0,
                    help="Allowed azimuth-gap slack beyond the ring opening "
                         "before ENCIRCLE fails. Default 45.")
    args = ap.parse_args()

    part = trimesh.load(args.part, force="mesh")
    cages = trimesh.load(args.cages, force="mesh")
    rep = json.loads(args.report.read_text())
    base_z = float(rep["base_z"])
    # generate_support_pillars.py lifts the part so it sits on the plate
    # (raycast_underside translates min-z to base_z) and builds the cages in
    # that lifted frame — replicate the lift or every distance is offset.
    lift = base_z - float(part.bounds[0, 2])
    if abs(lift) > 1e-9:
        part.apply_translation([0.0, 0.0, lift])
        print(f"note  lifted part by {lift:+.3f} mm to the cage frame")
    verts = np.asarray(cages.vertices)

    # ---- NO-CONTACT ---------------------------------------------------
    sd = trimesh.proximity.ProximityQuery(part).signed_distance(verts)
    inside = int((sd > 0).sum())
    standoff = float(-sd.max())
    if inside:
        _fail(f"NO-CONTACT: {inside} cage vertices are inside the part")
    if standoff < args.min_standoff:
        _fail(f"NO-CONTACT: closest cage vertex is {standoff:.3f} mm from "
              f"the part (< {args.min_standoff} mm)")
    print(f"PASS  NO-CONTACT: closest cage-to-part distance "
          f"{standoff:.3f} mm (>= {args.min_standoff} mm), 0 inside")

    # ---- ON-PLATE -----------------------------------------------------
    z_min = float(verts[:, 2].min())
    feet = int((verts[:, 2] < base_z + 0.01).sum())
    if z_min < base_z - 1e-6:
        _fail(f"ON-PLATE: cage geometry extends {base_z - z_min:.3f} mm "
              f"below the plate")
    if feet == 0:
        _fail("ON-PLATE: no cage vertices land on the build plate")
    print(f"PASS  ON-PLATE: min z {z_min:.3f}, {feet} foot vertices on plate")

    # ---- ENCIRCLE -----------------------------------------------------
    for i, t in enumerate(rep["tendons"]):
        fx, fy = t["fx"], t["fy"]
        worst = 0.0
        for zs in np.linspace(t["z_lo"] + 5.0, t["z_hi"] - 5.0, 5):
            # slice the cage solid (pillar frusta only have vertices at
            # their end rims, so a vertex-band test would miss them)
            sec = cages.section(plane_origin=[0.0, 0.0, float(zs)],
                                plane_normal=[0.0, 0.0, 1.0])
            axis = np.array([fx[0] * zs + fx[1], fy[0] * zs + fy[1]])
            near = np.empty((0, 3))
            if sec is not None and len(sec.vertices):
                sv = np.asarray(sec.vertices)
                d = sv[:, :2] - axis
                near = sv[np.linalg.norm(d, axis=1) < 2.5 * t["r_pillar"]]
            if len(near) < 3:
                _fail(f"ENCIRCLE: tendon[{i}] has no cage geometry at "
                      f"z={zs:.1f}")
            ang = np.sort(np.degrees(np.arctan2(near[:, 1] - axis[1],
                                                near[:, 0] - axis[0])))
            gaps = np.diff(np.concatenate([ang, [ang[0] + 360.0]]))
            worst = max(worst, float(gaps.max()))
        limit = t["opening_deg"] + args.gap_slack_deg
        if worst > limit:
            _fail(f"ENCIRCLE: tendon[{i}] max empty azimuth gap "
                  f"{worst:.0f} deg > {limit:.0f} deg (missing pillar?)")
        print(f"PASS  ENCIRCLE: tendon[{i}] max azimuth gap {worst:.0f} deg "
              f"(<= {limit:.0f} deg), {t['n_pillars']} pillars / "
              f"{t['n_rings']} rings")

    # ---- REMOVABLE ----------------------------------------------------
    # A soft TPU tendon squeezes out of an opening chord >= ~0.75x its
    # diameter (the generator's --cage_squeeze). A chord *above* the
    # diameter would let the tendon escape the ring during the print
    # (see sweep_cage_design.py), so bigger is not better here.
    min_squeeze = float(rep.get("squeeze", args.min_squeeze))
    for i, t in enumerate(rep["tendons"]):
        chord, dia = t["opening_chord"], 2.0 * t["r"]
        if chord < min_squeeze * dia - 1e-6:
            _fail(f"REMOVABLE: tendon[{i}] ring opening chord {chord:.2f} mm "
                  f"< {min_squeeze:.2f} x tendon dia {dia:.2f} mm — cage "
                  f"cannot be squeezed off the finished tendon")
        print(f"PASS  REMOVABLE: tendon[{i}] opening chord {chord:.2f} mm "
              f">= {min_squeeze:.2f} x tendon dia {dia:.2f} mm "
              f"(soft-TPU squeeze-out)")

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
