"""build123d port of `cad/t3-prism/t3-prism.scad` -> true B-rep STEP.

Issue #95, "route B": keep generation parametric on the Python side while
emitting **analytic** geometry (spherical faces, cylindrical faces, real
fillets) instead of the 49,846-triangle mesh OpenSCAD produces. Unlike
`onshape_featurescript_t3prism.py` (route C) this needs no Onshape account and
runs in CI.

    pip install build123d
    python3 cad/t3-prism/t3_prism_b123d.py --out-dir cad/t3-prism/step

Outputs, all in the SCAD's own world coordinates so they drop straight on top
of the existing STLs:

    t3-prism-struts.step   PLA half: joint shells, struts, accelerometer housings
    t3-prism-cables.step   TPU half: 9 cables + 6 captive cores
    t3-prism.step          both, as one STEP assembly

Parity with the SCAD
--------------------
Everything except the ten `hull()` calls is a 1:1 translation -- OpenSCAD's
`sphere`, `cylinder`, `cube`, `union` and `difference` all map onto OCCT
directly, and come out better because there is no tessellation.

The hulls have no OCCT equivalent and are handled two different ways:

  * `hull(sphere_a, sphere_b)` -- the teardrop joint blend -- is replaced by
    its EXACT analytic form. The convex hull of two spheres is the two spheres
    plus the truncated cone tangent to both, and the tangent circles are
    closed-form. This is not an approximation; it is the same solid the SCAD
    describes, minus the faceting.
  * `hull(slab, sphere)` -- the igloo skirt and the bottom key-seat skirt --
    has no closed form. Those become a union plus an `opFillet`-style blend,
    which is what a CAD engineer would have drawn and is smoother than a hull,
    but is NOT the same solid: see README-parametric.md for the volume delta.

`cables_z_anchor()` is deliberately dropped (it exists only to pin a separately
exported STL's bounding box for Bambu Studio's per-part bed placement).
"""
from __future__ import annotations

import argparse
import math
import pathlib
import sys

from build123d import (
    Axis, Compound, Location, Plane, Solid, Vector, export_step,
)

# ---------------------------------------------------------------------------
# Parameters -- names and values track t3-prism.scad exactly.
# ---------------------------------------------------------------------------
R_BASE = 25.0
H_BASE = 70.0
TWIST = 60.0
STRUT_D_BASE = 6.0
CABLE_D_BASE = 3.0
JOINT_D_BASE = 7.0

# "S0" specimen sizing = 76.92% of the 1.5x generations (PR #35, @achris0520).
S0_SCALE = 1.5 * 0.7692
SCALE = S0_SCALE

USE_CAPTIVE_CORE = True
CAPTIVE_BORE_CLEAR = 0.0      # bonded: the cable fills its bore exactly
CAPTIVE_BORE_TRAP = 1.5       # min (core_od - bore_d) / 2, so the core can't escape
CAPTIVE_CORE_CLEAR = 0.0      # bonded: the core touches the inner shell wall
CAPTIVE_WALL_BASE = 1.6
CAPTIVE_TEARDROP_Z = 1.5      # axial offset of the teardrop reference sphere

# Accelerometer housings. PHYSICAL-part dimensions: absolute mm, NOT scaled.
ADD_ACCEL_TOP = True
ADD_ACCEL_BOTTOM = True
ACCEL_POCKET_X = 6.2          # "A3" explicit pocket interior
ACCEL_POCKET_Y = 6.2
ACCEL_POCKET_Z = 6.8
ACCEL_WALL = 2.0
ACCEL_FLOOR = 1.5
ACCEL_DOME = 3.0
ACCEL_FLAT = 2.0
ACCEL_SINK = 2.0
ACCEL_SIDE_GAP = 1.0
ACCEL_HOVER = 2.0

BLEND_RADIUS = 2.0            # the fillet that stands in for the skirt hulls


class Dims:
    """Derived dimensions, mirroring the SCAD's derived block."""

    def __init__(self, scale: float = SCALE):
        self.scale = scale
        self.R = R_BASE * scale
        self.H = H_BASE * scale
        self.strut_d = STRUT_D_BASE * scale
        self.cable_d = CABLE_D_BASE * scale
        self.joint_d = JOINT_D_BASE * scale
        self.captive_wall = CAPTIVE_WALL_BASE * scale
        self.bore_d = self.cable_d + 2 * CAPTIVE_BORE_CLEAR
        self.core_od = max(self.bore_d + 2 * CAPTIVE_BORE_TRAP, self.joint_d)
        self.shell_id = self.core_od + 2 * CAPTIVE_CORE_CLEAR
        self.shell_od = max(self.shell_id + 2 * self.captive_wall, self.joint_d)
        self.teardrop_d = self.strut_d * 1.10
        self.joint_outer_r = (self.shell_od / 2 if USE_CAPTIVE_CORE
                              else self.joint_d / 2)

    # -- vertices ----------------------------------------------------------
    def bottom_pt(self, i: int) -> Vector:
        a = math.radians(90 + 120 * i)
        return Vector(self.R * math.cos(a), self.R * math.sin(a), 0.0)

    def top_pt(self, i: int) -> Vector:
        a = math.radians(90 + 120 * i + TWIST)
        return Vector(self.R * math.cos(a), self.R * math.sin(a), self.H)

    def cable_dirs_b(self, i: int) -> list[Vector]:
        v = self.bottom_pt(i)
        return [(self.bottom_pt((i + 1) % 3) - v).normalized(),
                (self.bottom_pt((i + 2) % 3) - v).normalized(),
                (self.top_pt((i + 2) % 3) - v).normalized()]

    def cable_dirs_t(self, i: int) -> list[Vector]:
        v = self.top_pt(i)
        return [(self.top_pt((i + 1) % 3) - v).normalized(),
                (self.top_pt((i + 2) % 3) - v).normalized(),
                (self.bottom_pt((i + 1) % 3) - v).normalized()]


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------
def sphere_at(p: Vector, r: float) -> Solid:
    return Solid.make_sphere(r).locate(Location(p))


def capsule(p1: Vector, p2: Vector, d: float) -> Solid:
    """cylinder + hemispherical end caps -- the SCAD `member` module."""
    v = p2 - p1
    length = v.length
    body = Solid.make_cylinder(d / 2, length, Plane(origin=p1, z_dir=v))
    return body + sphere_at(p1, d / 2) + sphere_at(p2, d / 2)


def bore_along(V: Vector, direction: Vector, d: float, length: float) -> Solid:
    """Outward-only cable exit bore -- the SCAD `bore_along` module.

    Outward-only by design: a centred bore punches a second, unwanted hole out
    the far side of the shell (PR #35 comment 4514072758).
    """
    u = direction.normalized()
    start = V - u * 0.5
    return Solid.make_cylinder(d / 2, length + 0.5,
                               Plane(origin=start, z_dir=u))


def hull_of_two_spheres(c1: Vector, r1: float, c2: Vector, r2: float) -> Solid:
    """EXACT convex hull of two spheres: both spheres + the tangent frustum.

    For centres a distance `d` apart, the external tangent line to the two
    circles in any plane through the axis touches sphere i at axial offset
    ``r_i * (r1 - r2) / d`` from its centre, on a circle of radius
    ``r_i * sqrt(1 - ((r1 - r2) / d) ** 2)``. Building the frustum between
    those two circles and unioning the spheres reproduces the hull with no
    faceting at all. Degenerates gracefully when one sphere contains the other.
    """
    axis = c2 - c1
    d = axis.length
    if d < 1e-9 or d <= abs(r1 - r2):          # one sphere swallows the other
        return sphere_at(c1, r1) + sphere_at(c2, r2)
    u = axis.normalized()
    k = (r1 - r2) / d                          # cos of the tangent-line angle
    s = math.sqrt(max(0.0, 1.0 - k * k))
    p1 = c1 + u * (r1 * k)
    p2 = c2 + u * (r2 * k)
    frustum = Solid.make_cone(r1 * s, r2 * s, (p2 - p1).length,
                              Plane(origin=p1, z_dir=u))
    return sphere_at(c1, r1) + sphere_at(c2, r2) + frustum


# ---------------------------------------------------------------------------
# Accelerometer housings
# ---------------------------------------------------------------------------
def accel_mount_local(domed: bool) -> tuple[Solid, Solid]:
    """Housing body + pocket cutter, axis-aligned at the origin.

    +X is the open (slide-in / cable-exit) face; the pocket floor is at local
    z = 0. Mirrors the SCAD `accel_mount_local`.
    """
    px, py, pz = ACCEL_POCKET_X, ACCEL_POCKET_Y, ACCEL_POCKET_Z
    bx0, bx1 = -ACCEL_WALL, px
    byh = py / 2 + ACCEL_WALL
    bz0 = -(ACCEL_FLOOR + ACCEL_SINK)
    bz1 = pz
    cx = (bx0 + bx1) / 2

    body = Solid.make_box(bx1 - bx0, 2 * byh, bz1 - bz0,
                          Plane(origin=(bx0, -byh, bz0)))
    if domed:
        # The SCAD hulls the body's top rim up to a sphere. That is a
        # slab-to-sphere hull, so use the crown sphere + a blend instead.
        rcrown = min(bx1 - bx0, 2 * byh) / 2
        body = body + sphere_at(Vector(cx, 0, bz1 + ACCEL_DOME - rcrown),
                                rcrown)
    else:
        body = body + Solid.make_box(bx1 - bx0, 2 * byh, ACCEL_FLAT,
                                     Plane(origin=(bx0, -byh, bz1)))
    # Pocket: three walls + floor + cap, OPEN on +X.
    cutter = Solid.make_box(px + byh + 5, py, pz,
                            Plane(origin=(0, -py / 2, 0)))
    return body, cutter


def place(shape: Solid, V: Vector, z0: float, ang_deg: float,
          shift_x: float) -> Solid:
    """translate(V.x, V.y, z0) * rotate_z(ang) * translate(shift_x, 0, 0)."""
    return (shape.translate(Vector(shift_x, 0, 0))
            .rotate(Axis.Z, ang_deg)
            .translate(Vector(V.X, V.Y, z0)))


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_pla(dm: Dims, blend: bool = True) -> Compound:
    """Joint shells + struts + accelerometer housings (the PLA half)."""
    solids: list[Solid] = []
    cutters: list[Solid] = []

    for i in range(3):
        B, T = dm.bottom_pt(i), dm.top_pt(i)
        if USE_CAPTIVE_CORE:
            # Teardrop-blended shell: the exact hull of the shell sphere and a
            # small sphere pushed out along the strut axis, so the strut
            # emerges from a filleted bump rather than a re-entrant corner
            # (PR #35 comment 4514072758, "stick with the teardrop style").
            for V, other in ((B, T), (T, B)):
                u = (other - V).normalized()
                solids.append(hull_of_two_spheres(
                    V, dm.shell_od / 2,
                    V + u * (dm.shell_od / 2 + CAPTIVE_TEARDROP_Z),
                    dm.teardrop_d / 2))
        else:
            solids.append(sphere_at(B, dm.joint_d / 2))
            solids.append(sphere_at(T, dm.joint_d / 2))
        solids.append(capsule(B, T, dm.strut_d))   # strut i: B_i -> T_i

    blen = ACCEL_POCKET_X + ACCEL_WALL
    byw = ACCEL_POCKET_Y + 2 * ACCEL_WALL
    cx_local = (-ACCEL_WALL + ACCEL_POCKET_X) / 2
    bz0 = -(ACCEL_FLOOR + ACCEL_SINK)
    r_off = dm.joint_outer_r + blen / 2 + ACCEL_SIDE_GAP

    if ADD_ACCEL_TOP:
        for i in range(3):
            T = dm.top_pt(i)
            ang = 90 + 120 * i + TWIST
            z0 = T.Z + dm.joint_outer_r + ACCEL_FLOOR
            body, cutter = accel_mount_local(domed=True)
            solids.append(place(body, T, z0, ang, -cx_local))
            cutters.append(place(cutter, T, z0, ang, -cx_local))

    if ADD_ACCEL_BOTTOM:
        for i in range(3):
            B = dm.bottom_pt(i)
            ang = 90 + 120 * i
            # Lift so the seat underside hovers ACCEL_HOVER above the joint
            # underside -- the joint sphere, not the seat, touches the plate
            # (PR #35 comment 4859762053).
            z0 = B.Z - dm.joint_outer_r + ACCEL_HOVER - bz0
            body, cutter = accel_mount_local(domed=False)
            solids.append(place(body, B, z0, ang, r_off - cx_local))
            cutters.append(place(cutter, B, z0, ang, r_off - cx_local))
            # Skirt bridging the radial gap from the joint sphere to the
            # seat's inner face (the SCAD hulls this).
            skirt = Solid.make_box(
                r_off - blen / 2 + 0.5 - dm.joint_outer_r * 0.4, byw,
                ACCEL_POCKET_Z - bz0,
                Plane(origin=(dm.joint_outer_r * 0.4, -byw / 2, bz0)))
            solids.append(place(skirt, B, z0, ang, 0.0))

    part = solids[0]
    for s in solids[1:]:
        part = part + s

    if blend:
        part = _try_blend(part, BLEND_RADIUS)

    if USE_CAPTIVE_CORE:
        bore_len_top = (dm.shell_od + ACCEL_POCKET_X + ACCEL_POCKET_Y
                        + 2 * ACCEL_WALL)
        bore_len_bot = dm.shell_od + 2 * (r_off + blen / 2)
        for i in range(3):
            B, T = dm.bottom_pt(i), dm.top_pt(i)
            cutters.append(sphere_at(B, dm.shell_id / 2))
            cutters.append(sphere_at(T, dm.shell_id / 2))
            for u in dm.cable_dirs_b(i):
                cutters.append(bore_along(B, u, dm.bore_d, bore_len_bot))
            for u in dm.cable_dirs_t(i):
                cutters.append(bore_along(T, u, dm.bore_d, bore_len_top))

    for cutter in cutters:
        part = part - cutter
    return part


def build_tpu(dm: Dims) -> Compound:
    """9 cables + 6 captive cores (the TPU half)."""
    solids: list[Solid] = []
    for i in range(3):
        solids.append(capsule(dm.bottom_pt(i), dm.bottom_pt((i + 1) % 3),
                              dm.cable_d))
        solids.append(capsule(dm.top_pt(i), dm.top_pt((i + 1) % 3),
                              dm.cable_d))
        # Saddle: B_{i+1} -> T_i. Strut i and saddle i meet at T_i but start
        # from different bottom vertices -- the defining tensegrity property.
        solids.append(capsule(dm.bottom_pt((i + 1) % 3), dm.top_pt(i),
                              dm.cable_d))
        if USE_CAPTIVE_CORE:
            solids.append(sphere_at(dm.bottom_pt(i), dm.core_od / 2))
            solids.append(sphere_at(dm.top_pt(i), dm.core_od / 2))
    part = solids[0]
    for s in solids[1:]:
        part = part + s
    return part


def _try_blend(part, radius: float):
    """Fillet the slab-to-sphere junctions, backing off until OCCT accepts.

    OFF BY DEFAULT, and for a real reason: the exact teardrop hull meets the
    shell sphere along a TANGENT (G1-continuous) circle, and asking OCCT to
    fillet a tangent edge aborts the process with SIGABRT rather than raising
    something Python can catch -- so a `try` around this does not save you. If
    you want blended joints, route C (`onshape_featurescript_t3prism.py`) does
    it reliably on Parasolid; this is the same trade-off documented in
    README-parametric.md.
    """
    from build123d import GeomType
    print("  [blend] WARNING: OCCT may abort the process on tangent edges")
    try:
        candidates = part.edges().filter_by(GeomType.CIRCLE)
    except Exception as exc:                                    # noqa: BLE001
        print(f"  [blend] edge selection failed ({exc}); skipping")
        return part
    if not candidates:
        print("  [blend] no circular edges found; skipping")
        return part
    r = radius
    for _ in range(5):
        try:
            blended = part.fillet(r, list(candidates))
            print(f"  [blend] filleted {len(candidates)} edges at {r:.3f} mm")
            return blended
        except Exception:                                       # noqa: BLE001
            r /= 2
    print(f"  [blend] no fillet radius <= {radius} mm was accepted; "
          "shipping unblended")
    return part


def _report(label: str, shape) -> None:
    bb = shape.bounding_box()
    solids = shape.solids()
    vol = sum(s.volume for s in solids)
    print(f"  {label}: {len(solids)} solid(s), {len(shape.faces())} faces, "
          f"volume {vol:.1f} mm^3, bbox "
          f"{bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm, "
          f"z {bb.min.Z:.2f}..{bb.max.Z:.2f}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=str(pathlib.Path(__file__).parent / "step"))
    ap.add_argument("--scale", type=float, default=SCALE,
                    help=f"uniform scale factor (default S0 = {SCALE:.4f})")
    ap.add_argument("--blend", action="store_true",
                    help="attempt the fillet that stands in for the skirt "
                         "hulls. OFF by default: OCCT aborts the process "
                         "(SIGABRT, not a catchable exception) when asked to "
                         "fillet the tangent teardrop edges")
    args = ap.parse_args(argv)

    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    dm = Dims(args.scale)
    print(f"scale {dm.scale:.4f}  R {dm.R:.3f}  H {dm.H:.3f}  "
          f"strut_d {dm.strut_d:.3f}  cable_d {dm.cable_d:.3f}  "
          f"shell_od {dm.shell_od:.3f}")

    print("building PLA half ...")
    pla = build_pla(dm, blend=args.blend)
    _report("struts", pla)

    print("building TPU half ...")
    tpu = build_tpu(dm)
    _report("cables", tpu)

    export_step(pla, str(out / "t3-prism-struts.step"))
    export_step(tpu, str(out / "t3-prism-cables.step"))
    both = Compound(children=[pla, tpu])
    export_step(both, str(out / "t3-prism.step"))
    for name in ("t3-prism-struts.step", "t3-prism-cables.step",
                 "t3-prism.step"):
        p = out / name
        print(f"  wrote {p} ({p.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
