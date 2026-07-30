"""Single-batch Sobol design generator for the T3-prism BO campaign.

Per PR #35 comment 4503109338 from @sgbaird (carried over from PR #30 / PR #24):
this is a **single-iteration**, human-in-the-loop, T3-prism-only first batch.
No measured objectives are reported back; this only emits the initial Sobol
quasi-random design set, renders each specimen, packs them onto a single
Bambu H2D build plate, and writes a preview PNG so the team can spot-check
before opening the result in Bambu Studio.

This is a *restricted* adaptation of ``bo/tensegrity_campaign.py`` from
``copilot/scaffold-bayesian-optimization-script`` (the PR #30 / #24 scaffold).
The full search space there spans every topology, tiling, material pairing,
and build orientation in the project's Edison-curated literature table. Here
we deliberately freeze every variable that is *not* specific to the T3-prism
geometry, since the team has only confirmed printability for T3-prisms so
far (PRs #30 / #24 / #16 / #35).

Frozen (defaults match the production target on this branch):

* ``topology`` = ``"t3_prism"``  -- canonical 3-strut tensegrity.
* ``tiling`` = ``"1x1x1"``       -- single unit cell.
* ``struts_per_cell`` = 3        -- T3 by definition.
* ``build_orientation`` = ``"vertical"`` -- per the comment, "Vertically
  orient it so you can maximize the number on the build plate".
* Materials: PLA struts + TPU 85A cables on the Bambu H2D IDEX nozzles
  (same as ``slices/t3-prism.H2D-MM-PLAstruts-TPUcables.3mf``).
* Supports: OFF in the slicer. Per the comment, "@achris0520 will manually
  paint on supports, so you can leave those off"; the modeled-in PLA
  scaffold pillars from PR #35 commit 5437366 are likewise disabled here
  (``part="all"`` in the SCAD, no ``scaffold`` block).

Sweep (T3-prism-specific geometric variables, taken from
``cad/t3-prism/t3-prism.scad``):

================================  ==================  =====================
Variable                          Range (mm/deg)      Maps to SCAD parameter
================================  ==================  =====================
``R_mm``       (radius)             [25, 40]          ``R_base``
``H_mm``       (height)             [60, 110]         ``H_base``
``twist_deg``  (top-vs-bottom)      [40, 80]          ``twist``
``strut_d_mm`` (PLA strut Ø)        [6.0, 12.0]       ``strut_d_base``
``cable_d_mm`` (TPU cable Ø)        [3.0, 5.5]        ``cable_d_base``
================================  ==================  =====================

The cable_d lower bound (3.0 mm) sits above the Bambu auto-support detector
threshold @achris0520 hit empirically at scale 1.3x (cable_d ≈ 3.9 mm) and
matches Edison ANALYSIS ``25c1c897``'s recommended floor (3.0–4.0 mm) so even
the smallest cable in the batch will TPU-self-bridge without painted
supports failing mid-print.  (NOTE: after the constant-mass projection below
the *as-printed* cable diameter can fall below that floor — flagged per
specimen in the CSV — which is acceptable under the manual-painted-supports
workflow.)

Rendering (PR #35 comment 5132975378 rework)
--------------------------------------------
Specimens are no longer generated from an embedded SCAD template.  Each
specimen is rendered **directly from the canonical**
``cad/t3-prism/t3-prism.scad`` via ``-D`` parameter overrides, so every
specimen automatically carries the latest joint + sensor-housing design:
captive-core joints, the three top-vertex "igloo" accelerometer mounts
(A3 pocket), and the three beside-mounted flat bottom key-seats.  The
housings are PHYSICAL-part fixtures in absolute mm and do not scale.

Constraints (PR #35 comment 5132975378, per the PR #33 hybrid campaign
``simulations/sim_bo_hybrid_campaign.py``)
--------------------------------------------------------------------------
* **Route A — constant cell mass.**  Every specimen is projected onto the
  constant-mass manifold: its (R, H, strut_d, cable_d, joint_d) are
  uniformly re-scaled (twist and all shape ratios preserved) until the
  estimated as-printed mass equals the fixed target ``m*``.  ``m*``
  defaults to the solid-volume mass of the current S0 reference design in
  ``cad/t3-prism/`` (the geometry of the team's most recent instrumented
  prints), computed from the committed ``t3-prism-{struts,cables}.stl``.
  Because the sensor housings don't scale, the solve iterates on rendered
  STL volumes (``m(s) = m_housings + m_body(1)·s³``) to |m − m*| ≤ 0.15 g.
* **Route B — max envelope volume.**  ``envelope_cm3 = π·R_print²·H_print``
  (circumscribing cylinder, same definition as
  ``simulations/bo_evaluator.py::cell_geometry_metrics``) must be
  ≤ 250 cm³.  The uniform scale is consumed by the mass constraint, so a
  shape whose envelope still exceeds V* at m* is CONSTRAINT-INFEASIBLE and
  is flagged (``envelope_ok=False``), not silently dropped or re-scaled.

Output files (next to this script):

* ``t3-prism-bo-batch.csv``                                       -- one row per specimen: original Sobol
                                                                     coordinates + as-printed (mass-projected)
                                                                     dimensions + mass/envelope constraint columns
* ``t3-prism-bo-batch.json``                                      -- same data + constraint + plate-layout metadata
* ``t3-prism-bo-batch.scad``                                      -- preview wrapper (imports the per-specimen STLs)
* ``t3-prism-bo-batch.stl``                                       -- packed-on-plate combined STL (all parts fused)
* ``t3-prism-bo-batch-struts.stl``                                -- struts + joints + housings (extruder 1 / PLA)
* ``t3-prism-bo-batch-cables.stl``                                -- cables + captive cores (extruder 2 / TPU)
* ``per-specimen-stls/t3-prism-bo-specNN-{struts,cables}.stl``    -- per-specimen plate-positioned STL pairs
* ``t3-prism-bo-batch-plate.png``                                 -- top-down build-plate preview PNG
* ``t3-prism-bo-batch-iso.png``                                   -- iso preview PNG
* ``slices/t3-prism-bo-batch.H2D-MM-PLAstruts-TPUcables.3mf``     -- Bambu H2D MM project (struts/PLA + cables/TPU,
                                                                     re-importable into Bambu Studio with
                                                                     per-part extruder assignment; *no* supports —
                                                                     paint them on manually per @achris0520's tip
                                                                     in PR #35 comment 4502140147)

Run::

    sudo apt-get install -y openscad admesh xvfb \\
        gstreamer1.0-plugins-base libsoup-3.0-0 libwebkit2gtk-4.1-0
    python3 bo/t3_prism_sobol_batch.py

By default the 9 designs are read back from the committed
``t3-prism-bo-batch.csv`` (the first Sobol batch, seed 0) so the physical
design coordinates stay pinned; pass ``--resample`` to draw a fresh Sobol
batch instead (requires ``pip install ax-platform``).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# ---- Frozen experimental context -------------------------------------------
TOPOLOGY = "t3_prism"
TILING = "1x1x1"
STRUTS_PER_CELL = 3
BUILD_ORIENTATION = "vertical"
TPU_SHORE = "85A"          # NinjaFlex-class; lab default
STRUT_MATERIAL = "PLA"     # Bambu PLA Basic on extruder 1
CABLE_MATERIAL = "TPU"     # Bambu TPU 85A on extruder 2
SUPPORTS = "manual_painted"  # Audrey paints them on in Bambu Studio
JOINT_D_BASE = 7.0         # mm, kept fixed (t3-prism.scad default)

# ---- Build-plate geometry (Bambu Lab H2D) ----------------------------------
PLATE_X = 350.0  # mm
PLATE_Y = 320.0  # mm
PLATE_MARGIN = 5.0  # keep specimens off the edge
# Reserve a strip on the +X side of the plate for the IDEX prime / flush
# tower that the slicer drops in for PLA<->TPU material changes.
# Bambu Studio's default prime tower is ~50 mm square; reserving a 50 mm
# wide × full-Y strip on +X gives the slicer ample room to drop the tower
# without colliding with any specimen corner (PR #35 comment 4513445377).
PRIME_TOWER_RESERVE_X = 50.0

# ---- Sobol batch knobs -----------------------------------------------------
# 9 specimens packed 3x3 on the H2D plate. PR #35 comment 4513164299
# briefly dropped this to 6 (3x2) to make room for an extra-fat 70 mm
# prime-tower reserve, but PR #35 comment 4513445377 reverted to 3x3 with
# a smaller 50 mm tower reserve and a 6 mm inter-cell air gap (up from
# the original 2 mm that was "too tight last time" per comment
# 4513164299, but tighter than the temporary 12 mm used at n=6 so 3x3
# still fits inside the prime-tower-reduced 290x310 mm usable area).
N_SPECIMENS = 9      # 3 rows x 3 cols
SEED = 0

# ---- Search space (T3-prism-specific geometric variables only) -------------
# Bounds reconciled against:
#   * cad/t3-prism/t3-prism.scad's existing defaults at scale_factor=1.5
#     (R=37.5, H=105, strut_d=9, cable_d=4.5).
#   * PR #24 Edison literature table 5ae24eaf (strut_d 1.5-5 mm pre-scale,
#     L/D in [8,25], cable_d 1.0-3.0 mm pre-scale, twist 10-45 deg).
#   * PR #35 print history: cable_d >= 3.0 mm is required for the top-cable
#     bridge to survive without auto-supports failing.
PARAMETERS: list[dict] = [
    {"name": "R_mm",        "type": "range", "bounds": [25.0,  40.0], "value_type": "float"},
    {"name": "H_mm",        "type": "range", "bounds": [60.0, 110.0], "value_type": "float"},
    {"name": "twist_deg",   "type": "range", "bounds": [40.0,  80.0], "value_type": "float"},
    {"name": "strut_d_mm",  "type": "range", "bounds": [ 6.0,  12.0], "value_type": "float"},
    {"name": "cable_d_mm",  "type": "range", "bounds": [ 3.0,   5.5], "value_type": "float"},
]


# ---- Constraints (PR #33 hybrid campaign: Route A + Route B) ----------------
# See the module docstring.  m* defaults to the solid-volume mass of the
# committed S0 reference STLs (the most recent instrumented prints); V* is
# sim_bo_hybrid_campaign.DEFAULT_ENVELOPE_MAX_CM3.
RHO_PLA = 1.24e-3            # g/mm^3, solid — Bambu PLA Basic
RHO_TPU = 1.21e-3            # g/mm^3, solid — Bambu TPU 85A
DEFAULT_ENVELOPE_MAX_CM3 = 250.0
MASS_TOL_G = 0.15            # |m - m*| convergence tolerance for the scale solve
MAX_MASS_ITERS = 4
CABLE_BRIDGE_FLOOR_MM = 3.0  # empirical TPU self-bridging floor (Edison 25c1c897)

REPO_ROOT = Path(__file__).resolve().parent.parent
T3_PRISM_DIR = REPO_ROOT / "cad" / "t3-prism"
CANONICAL_SCAD = T3_PRISM_DIR / "t3-prism.scad"
REF_STRUTS_STL = T3_PRISM_DIR / "t3-prism-struts.stl"
REF_CABLES_STL = T3_PRISM_DIR / "t3-prism-cables.stl"


# ---- Binary-STL helpers (volume / bbox / translate / merge) -----------------
def _stl_records(data: bytes):
    n = struct.unpack_from("<I", data, 80)[0]
    off = 84
    for _ in range(n):
        yield struct.unpack_from("<9f", data, off + 12)
        off += 50


def stl_volume_bbox(path: Path) -> tuple[float, list[float], list[float]]:
    """Signed volume (mm^3) + axis-aligned bbox of a binary STL.

    The signed-tetrahedron sum handles the hollow captive-core shells
    correctly (inner cavity surfaces subtract), unlike ``admesh`` which
    mis-reports these multi-part meshes.
    """
    data = path.read_bytes()
    vol = 0.0
    mins = [math.inf] * 3
    maxs = [-math.inf] * 3
    for v in _stl_records(data):
        ax, ay, az, bx, by, bz, cx, cy, cz = v
        vol += (ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx)
                + az * (bx * cy - by * cx)) / 6.0
        for x, y, z in ((ax, ay, az), (bx, by, bz), (cx, cy, cz)):
            mins[0] = min(mins[0], x); maxs[0] = max(maxs[0], x)
            mins[1] = min(mins[1], y); maxs[1] = max(maxs[1], y)
            mins[2] = min(mins[2], z); maxs[2] = max(maxs[2], z)
    return abs(vol), mins, maxs


def stl_translate(src: Path, dst: Path, dx: float, dy: float, dz: float) -> None:
    """Copy a binary STL with a rigid XYZ translation applied to every vertex."""
    data = bytearray(src.read_bytes())
    n = struct.unpack_from("<I", data, 80)[0]
    off = 84
    for _ in range(n):
        for k in range(3):
            base = off + 12 + 12 * k
            x, y, z = struct.unpack_from("<3f", data, base)
            struct.pack_into("<3f", data, base, x + dx, y + dy, z + dz)
        off += 50
    dst.write_bytes(bytes(data))


def stl_merge(srcs: list[Path], dst: Path) -> None:
    """Concatenate binary STLs into one (disjoint solids; no boolean union)."""
    bodies: list[bytes] = []
    total = 0
    for src in srcs:
        data = src.read_bytes()
        n = struct.unpack_from("<I", data, 80)[0]
        total += n
        bodies.append(data[84:84 + 50 * n])
    header = b"t3-prism-bo-batch merged".ljust(80, b"\0")
    dst.write_bytes(header + struct.pack("<I", total) + b"".join(bodies))


# ---- Mass model -------------------------------------------------------------
def estimate_body_mass_g(p: dict) -> float:
    """Analytic solid-mass estimate of one specimen at scale 1, EXCLUDING the
    absolute-size sensor housings.  Only used as the initial guess for the
    rendered-volume scale solve (boolean overlaps make it ~±10 %); the solve
    itself iterates on measured STL volumes so the fixed point is exact.
    """
    R, H, tw = p["R_mm"], p["H_mm"], p["twist_deg"]
    sd, cd, jd = p["strut_d_mm"], p["cable_d_mm"], JOINT_D_BASE
    l_strut = math.hypot(2 * R * math.sin(math.radians(tw / 2)), H)
    l_side = R * math.sqrt(3)
    b1 = (R * math.cos(math.radians(210)), R * math.sin(math.radians(210)), 0.0)
    t0 = (R * math.cos(math.radians(90 + tw)), R * math.sin(math.radians(90 + tw)), H)
    l_saddle = math.dist(b1, t0)
    # Captive-core joint sizing (mirrors t3-prism.scad at scale 1).
    core_od = max(cd + 3.0, jd)
    shell_od = max(core_od + 3.2, jd)
    v_pla = 3 * (math.pi * sd * sd / 4 * l_strut + 0.7 * (4 / 3) * math.pi * (sd / 2) ** 3)
    v_pla += 6 * (4 / 3) * math.pi * ((shell_od / 2) ** 3 - (core_od / 2) ** 3)
    v_tpu = 0.97 * math.pi * cd * cd / 4 * (6 * l_side + 3 * l_saddle)
    v_tpu += 0.85 * 6 * (4 / 3) * math.pi * (core_od / 2) ** 3
    return RHO_PLA * v_pla + RHO_TPU * v_tpu


def reference_mass_g() -> float:
    """m* anchor: solid-volume mass of the committed S0 reference design
    (``cad/t3-prism/t3-prism-{struts,cables}.stl`` — the geometry of the
    team's most recent instrumented prints, sensor housings included)."""
    vs, _, _ = stl_volume_bbox(REF_STRUTS_STL)
    vc, _, _ = stl_volume_bbox(REF_CABLES_STL)
    return RHO_PLA * vs + RHO_TPU * vc


def housing_mass_g(scratch: Path) -> float:
    """PLA mass of the six absolute-size sensor housings (3 igloo mounts +
    3 bottom key-seats, skirts included): committed reference struts STL
    minus a housings-off render of the same default design."""
    out = scratch / "s0-struts-nohousing.stl"
    if not out.exists():
        print("==> OpenSCAD render (once): S0 reference struts w/o housings "
              "(for the housing-mass estimate)")
        run_openscad(CANONICAL_SCAD, out, defines={
            "part": "struts",
            "add_accel_mount": False,
            "add_accel_mount_bottom": False,
        })
    v_ref, _, _ = stl_volume_bbox(REF_STRUTS_STL)
    v_no, _, _ = stl_volume_bbox(out)
    return RHO_PLA * (v_ref - v_no)


def plan_plate_layout(footprints: list[float]) -> dict:
    """Variable-cell rows x cols layout for the (mass-projected) specimens.

    The constant-mass projection leaves the specimens with quite different
    footprints (the large-R shapes shrink less in R than the stocky ones),
    so a uniform grid sized to the worst case no longer fits 3x3 inside the
    prime-tower-reduced usable area.  Instead, sort the footprints in
    descending order and fill the grid column-major so the largest
    specimens share a column and a row; each column takes the width of its
    largest occupant and each row the height of its largest occupant, with
    a 6 mm inter-cell air gap (PR #35 comment 4513445377) between cells
    only (the pack is centred inside the usable area).

    Honours ``PRIME_TOWER_RESERVE_X`` — the +X strip stays clear for the
    IDEX prime/flush tower.  Returns per-specimen cell centres (in the
    original specimen order) plus the grid metadata.
    """
    air_gap = 6.0
    n = len(footprints)
    rows = math.ceil(math.sqrt(n))
    cols = math.ceil(n / rows)
    order = sorted(range(n), key=lambda i: -footprints[i])
    cell_of: dict[int, tuple[int, int]] = {}
    for rank, i in enumerate(order):
        cell_of[i] = (rank % rows, rank // rows)   # column-major fill
    col_w = [0.0] * cols
    row_h = [0.0] * rows
    for i, (r, c) in cell_of.items():
        col_w[c] = max(col_w[c], footprints[i])
        row_h[r] = max(row_h[r], footprints[i])
    total_w = sum(col_w) + air_gap * (cols - 1)
    total_h = sum(row_h) + air_gap * (rows - 1)
    usable_x = PLATE_X - 2 * PLATE_MARGIN - PRIME_TOWER_RESERVE_X
    usable_y = PLATE_Y - 2 * PLATE_MARGIN
    if total_w > usable_x or total_h > usable_y:
        print(
            f"WARNING: packed grid {total_w:.1f}x{total_h:.1f} mm exceeds "
            f"usable plate {usable_x:.1f}x{usable_y:.1f} mm "
            f"(plate {PLATE_X:.0f}x{PLATE_Y:.0f} - prime-tower reserve "
            f"{PRIME_TOWER_RESERVE_X:.0f} mm in +X - {PLATE_MARGIN:.0f} mm "
            f"margins)", file=sys.stderr)
    # Centre the pack inside the usable (non-prime-tower) area.
    x_cursor = PLATE_MARGIN + (usable_x - total_w) / 2.0
    col_cx = []
    for c in range(cols):
        col_cx.append(x_cursor + col_w[c] / 2.0)
        x_cursor += col_w[c] + air_gap
    y_cursor = PLATE_MARGIN + (usable_y - total_h) / 2.0
    row_cy = []
    for r in range(rows):
        row_cy.append(y_cursor + row_h[r] / 2.0)
        y_cursor += row_h[r] + air_gap
    centres = [(col_cx[cell_of[i][1]], row_cy[cell_of[i][0]]) for i in range(n)]
    return {
        "rows": rows, "cols": cols, "air_gap": air_gap,
        "col_widths": col_w, "row_heights": row_h,
        "total_w": total_w, "total_h": total_h,
        "centres": centres,
    }

SPEC_STL_FMT = "t3-prism-bo-spec{idx:02d}-{part}.stl"


def render_specimen(part: str, out: Path, params: dict, scale: float) -> None:
    """Render one specimen part straight from the canonical t3-prism.scad.

    Passing the Sobol coordinates as the *_base dimensions with
    ``scale_factor = scale`` applies the Route-A constant-mass projection
    uniformly to R, H, strut_d, cable_d, and joint_d while keeping the
    sensor housings at their absolute physical size (the SCAD never scales
    them).  Scaffold pillars stay off (supports are manual-painted).
    """
    run_openscad(CANONICAL_SCAD, out, defines={
        "R_base": params["R_mm"],
        "H_base": params["H_mm"],
        "twist": params["twist_deg"],
        "strut_d_base": params["strut_d_mm"],
        "cable_d_base": params["cable_d_mm"],
        "joint_d_base": JOINT_D_BASE,
        "scale_factor": scale,
        "part": part,
    })


def solve_specimen(idx: int, params: dict, m_star: float, m_h: float,
                   work: Path) -> dict:
    """Project one Sobol design onto the constant-mass manifold.

    Iterates the uniform scale ``s`` with the cube-root update
    ``s <- s * ((m* - m_h) / (m(s) - m_h))^(1/3)`` on *rendered* STL
    volumes, so the converged mass includes every real geometry feature
    (captive cores, teardrops, skirts, housings, boolean overlaps).
    """
    s = ((m_star - m_h) / estimate_body_mass_g(params)) ** (1.0 / 3.0)
    struts = work / SPEC_STL_FMT.format(idx=idx, part="struts")
    cables = work / SPEC_STL_FMT.format(idx=idx, part="cables")
    m = float("nan")
    vs = vc = 0.0
    bb = None
    for it in range(1, MAX_MASS_ITERS + 1):
        print(f"==> spec{idx:02d} iter {it}: render at scale {s:.4f}")
        render_specimen("struts", struts, params, s)
        render_specimen("cables", cables, params, s)
        vs, smin, smax = stl_volume_bbox(struts)
        vc, cmin, cmax = stl_volume_bbox(cables)
        bb = ([min(a, b) for a, b in zip(smin, cmin)],
              [max(a, b) for a, b in zip(smax, cmax)])
        m = RHO_PLA * vs + RHO_TPU * vc
        print(f"    spec{idx:02d} iter {it}: m={m:.2f} g (target {m_star:.2f} g)")
        if abs(m - m_star) <= MASS_TOL_G:
            break
        s *= ((m_star - m_h) / max(m - m_h, 1e-9)) ** (1.0 / 3.0)
    else:
        print(f"WARNING: spec{idx:02d} scale solve stopped at |m - m*| = "
              f"{abs(m - m_star):.2f} g after {MAX_MASS_ITERS} iterations",
              file=sys.stderr)
    return {
        "idx": idx,
        "scale": s,
        "mass_g": m,
        "pla_g": RHO_PLA * vs,
        "tpu_g": RHO_TPU * vc,
        "struts_stl": struts,
        "cables_stl": cables,
        "bbox_min": bb[0],
        "bbox_max": bb[1],
    }


def write_preview_scad(path: Path, n: int, rows: int, cols: int,
                       cell: float) -> None:
    """Preview wrapper that imports the plate-positioned per-specimen STLs.

    The real geometry lives in the per-specimen STLs (rendered from the
    canonical ``cad/t3-prism/t3-prism.scad``); this wrapper only exists so
    the plate/iso PNGs and ad-hoc OpenSCAD inspection have a single entry
    point.  ``part`` mirrors the canonical SCAD ("all" | "struts" |
    "cables").
    """
    chunks: list[str] = [
        "// AUTO-GENERATED by bo/t3_prism_sobol_batch.py — do not hand-edit.\n"
        "// Preview wrapper for the T3-prism Sobol batch: imports the\n"
        "// per-specimen STLs rendered from cad/t3-prism/t3-prism.scad\n"
        "// (latest captive-core joints + A3 igloo top mounts + beside-\n"
        "// mounted flat bottom key-seats), each projected onto the\n"
        "// constant-mass manifold (PR #35 comment 5132975378).\n"
        f"// Plate: {PLATE_X:.0f} x {PLATE_Y:.0f} mm (Bambu Lab H2D).\n"
        f"// Grid : {rows} x {cols} (cell {cell:.1f} mm).\n"
        'part = "all";  // "all" | "struts" | "cables"\n\n'
    ]
    for idx in range(n):
        for part in ("struts", "cables"):
            fname = SPEC_STL_FMT.format(idx=idx, part=part)
            chunks.append(
                f'if (part == "all" || part == "{part}")\n'
                f'    import("per-specimen-stls/{fname}");\n'
            )
    pt_x = PRIME_TOWER_RESERVE_X - 2 * PLATE_MARGIN
    chunks.append(
        f"\n// Visual marker for the IDEX prime/flush-tower reserve zone.\n"
        f'if (part == "all") {{\n'
        f"  translate([{PLATE_X - PRIME_TOWER_RESERVE_X + PLATE_MARGIN:.2f}, "
        f"{PLATE_MARGIN:.2f}, 0])\n"
        f"    cube([{pt_x:.2f}, {PLATE_Y - 2 * PLATE_MARGIN:.2f}, 0.2]);\n"
        f"}}\n"
    )
    path.write_text("".join(chunks))



def run_openscad(scad: Path, out: Path, *, camera: str | None = None,
                 image_size: str | None = None, defines: dict | None = None,
                 viewall: bool = False) -> None:
    """Invoke OpenSCAD headlessly via xvfb-run, writing STL or PNG."""
    cmd = ["xvfb-run", "-a", "openscad", "-o", str(out)]
    if out.suffix == ".stl":
        cmd += ["--export-format=binstl"]
    if camera:
        cmd += [f"--camera={camera}"]
    if viewall:
        cmd += ["--viewall"]
    if image_size:
        cmd += [f"--imgsize={image_size}"]
    for k, v in (defines or {}).items():
        if isinstance(v, bool):
            cmd += ["-D", f"{k}={'true' if v else 'false'}"]
        elif isinstance(v, str):
            cmd += ["-D", f'{k}="{v}"']
        else:
            cmd += ["-D", f"{k}={v}"]
    cmd += [str(scad)]
    subprocess.run(cmd, check=True)


# ---- Bambu H2D multi-material 3mf assembly ---------------------------------
# Reuses the BambuStudio AppImage cache + flatten/patch helpers from
# `cad/t3-prism/render_print.sh`. Per PR #35 comment 4503267471 the BO batch
# project file must open in Bambu Studio with two parts that can be assigned
# different filaments (struts -> PLA / extruder 1, cables -> TPU / extruder 2)
# — the single combined STL we used previously imported as a single fused
# object so Bambu Studio could not split-to-parts.
BAMBU_VERSION = "v02.06.00.51"
BAMBU_URL = (
    "https://github.com/bambulab/BambuStudio/releases/download/"
    f"{BAMBU_VERSION}/BambuStudio_ubuntu-24.04-{BAMBU_VERSION}"
    "-20260417160415.AppImage"
)
SCRATCH = Path("/tmp/t3-prism")
BAMBU_APPIMAGE = SCRATCH / "bambu.AppImage"
BBL_ROOT = SCRATCH / "squashfs-root" / "resources" / "profiles" / "BBL"


def _ensure_bambu() -> None:
    """Download the BambuStudio AppImage and extract the bundled BBL profiles."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    if not BAMBU_APPIMAGE.exists():
        print(f"==> Fetching BambuStudio {BAMBU_VERSION} AppImage")
        subprocess.run(["curl", "-sLo", str(BAMBU_APPIMAGE), BAMBU_URL], check=True)
        BAMBU_APPIMAGE.chmod(0o755)
    if not BBL_ROOT.exists():
        print("==> Extracting bundled BBL profiles from AppImage")
        subprocess.run(
            [str(BAMBU_APPIMAGE), "--appimage-extract", "resources/profiles/BBL"],
            cwd=SCRATCH, check=True, stdout=subprocess.DEVNULL,
        )


def _flatten(kind: str, leaf: str, out: Path) -> None:
    subprocess.run(
        ["python3", str(T3_PRISM_DIR / "flatten_bambu_profile.py"),
         kind, leaf, str(BBL_ROOT), str(out)],
        check=True,
    )


def _patch_bed(profile: Path) -> None:
    d = json.loads(profile.read_text())
    d["curr_bed_type"] = "Textured PEI Plate"
    d["default_bed_type"] = "Textured PEI Plate"
    profile.write_text(json.dumps(d, indent=2))


def _split_assembled_into_objects(
    proj_3mf: Path, pairs: list[tuple[str, str]]
) -> None:
    """Split the single composite object emitted by ``--assemble`` into one
    composite object per (struts_stl, cables_stl) pair.

    Per PR #35 comment 4513722886 (@sgbaird), each tensegrity iteration on
    the plate must be its own Bambu Studio object made up of two part
    groups (PLA struts + TPU cables) so it can be moved as a unit. The
    BambuStudio CLI's ``--assemble`` flag instead merges *all* passed STLs
    into a single composite object, so the team can't move one specimen
    independently of the others without lassoing both of its parts.

    Fix: after ``--assemble``, edit ``3D/3dmodel.model`` and
    ``Metadata/model_settings.config`` in-place to split the single
    composite object into ``len(pairs)`` composite objects, each
    referencing two of the per-specimen STL meshes (struts → extruder 1,
    cables → extruder 2). The underlying ``3D/Objects/object_1.model``
    mesh data is untouched; only the grouping changes.
    """
    import re
    import uuid
    import zipfile

    MODEL_PATH = "3D/3dmodel.model"
    CFG_PATH = "Metadata/model_settings.config"

    # Mapping from STL filename -> (specimen_index, extruder_id). Struts
    # always go to extruder 1, cables to extruder 2.
    name_to_spec: dict[str, tuple[int, int]] = {}
    for spec_idx, (struts_name, cables_name) in enumerate(pairs):
        name_to_spec[struts_name] = (spec_idx, 1)
        name_to_spec[cables_name] = (spec_idx, 2)

    with zipfile.ZipFile(proj_3mf, "r") as zin:
        infos = zin.infolist()
        contents = {info.filename: zin.read(info.filename) for info in infos}

    if MODEL_PATH not in contents:
        raise RuntimeError(f"{proj_3mf}: missing {MODEL_PATH}")
    if CFG_PATH not in contents:
        raise RuntimeError(f"{proj_3mf}: missing {CFG_PATH}")

    # ---- Patch model_settings.config first (we need part-name -> id mapping). ----
    cfg = contents[CFG_PATH].decode()
    cfg_part_re = re.compile(
        r'<part id="(\d+)"[^>]*>(.*?)</part>', re.DOTALL
    )
    cfg_name_re = re.compile(r'<metadata key="name" value="([^"]+)"\s*/>')
    cfg_object_re = re.compile(
        r'(<object id="(\d+)"[^>]*>)(.*?)(</object>)', re.DOTALL
    )
    cfg_plate_re = re.compile(
        r'(<plate>)(.*?)(</plate>)', re.DOTALL
    )

    # The CLI emits exactly one <object> in the assembled file; find it and
    # capture its part blocks.
    obj_match = cfg_object_re.search(cfg)
    if obj_match is None:
        raise RuntimeError(f"{proj_3mf}: no <object> in {CFG_PATH}")
    obj_open, obj_id_str, obj_body, obj_close = obj_match.groups()
    composite_obj_id = int(obj_id_str)

    # Parse parts: each part has an id and a name; the name is the STL filename.
    parts: list[tuple[int, str, str]] = []  # (part_id, name, full_part_xml)
    for m in cfg_part_re.finditer(obj_body):
        part_id = int(m.group(1))
        part_xml = m.group(0)
        name_match = cfg_name_re.search(m.group(2))
        if name_match is None:
            raise RuntimeError(f"{proj_3mf}: <part id={part_id}> missing name")
        name = name_match.group(1)
        parts.append((part_id, name, part_xml))

    # Group parts by specimen index. Order within each specimen: struts first
    # (extruder 1), cables second (extruder 2).
    spec_to_parts: dict[int, dict[int, tuple[int, str, str]]] = {}
    for part_id, name, part_xml in parts:
        if name not in name_to_spec:
            raise RuntimeError(
                f"{proj_3mf}: <part name={name!r}> not in pairs mapping"
            )
        spec_idx, ext_id = name_to_spec[name]
        spec_to_parts.setdefault(spec_idx, {})[ext_id] = (part_id, name, part_xml)

    # Build the new <object> entries (one per specimen). Composite object IDs
    # start one past the original (to avoid collision with the part IDs which
    # are 1..len(parts)).
    new_composite_ids: list[int] = []
    cfg_new_objects: list[str] = []
    extruder_re = re.compile(r'(<metadata key="extruder" value=")\d+(")')
    for spec_idx in sorted(spec_to_parts):
        new_obj_id = composite_obj_id + spec_idx
        new_composite_ids.append(new_obj_id)
        chunks = [f'  <object id="{new_obj_id}">\n']
        chunks.append(f'    <metadata key="name" value="Specimen {spec_idx:02d}"/>\n')
        for ext_id in sorted(spec_to_parts[spec_idx]):
            _, _, part_xml = spec_to_parts[spec_idx][ext_id]
            # Force the correct extruder per part.
            if extruder_re.search(part_xml):
                part_xml = extruder_re.sub(rf"\g<1>{ext_id}\g<2>", part_xml)
            else:
                part_xml = part_xml.replace(
                    "</part>",
                    f'      <metadata key="extruder" value="{ext_id}"/>\n    </part>',
                )
            chunks.append("    " + part_xml + "\n")
        chunks.append("  </object>")
        cfg_new_objects.append("".join(chunks))

    cfg_new_object_block = "\n".join(cfg_new_objects)

    # Replace the single <object>...</object> block with the new ones.
    new_cfg = cfg[:obj_match.start()] + cfg_new_object_block + cfg[obj_match.end():]

    # Patch <plate>: one <model_instance> per new composite.
    plate_match = cfg_plate_re.search(new_cfg)
    if plate_match is None:
        raise RuntimeError(f"{proj_3mf}: no <plate> in {CFG_PATH}")
    plate_open, plate_body, plate_close = plate_match.groups()
    plate_header_match = re.search(
        r'^(.*?)(<model_instance>.*?</model_instance>\s*)', plate_body, re.DOTALL
    )
    if plate_header_match is None:
        # No existing model_instance — just inject after a trailing <gcode_file>.
        plate_header = plate_body.rstrip() + "\n"
    else:
        plate_header = plate_header_match.group(1)
    new_instances: list[str] = []
    for i, new_obj_id in enumerate(new_composite_ids):
        new_instances.append(
            f'    <model_instance>\n'
            f'      <metadata key="object_id" value="{new_obj_id}"/>\n'
            f'      <metadata key="instance_id" value="0"/>\n'
            f'      <metadata key="identify_id" value="{100 + i}"/>\n'
            f'    </model_instance>\n'
        )
    new_plate = plate_open + plate_header + "".join(new_instances) + "  " + plate_close
    new_cfg = new_cfg[:plate_match.start()] + new_plate + new_cfg[plate_match.end():]
    contents[CFG_PATH] = new_cfg.encode()

    # ---- Patch 3D/3dmodel.model next. -----------------------------------------
    model_xml = contents[MODEL_PATH].decode()
    model_obj_re = re.compile(
        r'(<object id="(\d+)"[^>]*type="model"[^>]*>)(.*?)(</object>)',
        re.DOTALL,
    )
    model_component_re = re.compile(
        r'<component\b[^>]*?objectid="(\d+)"[^>]*?/>'
    )
    model_build_re = re.compile(
        r'(<build[^>]*>)(.*?)(</build>)', re.DOTALL
    )
    model_item_re = re.compile(
        r'<item\b[^>]*?objectid="\d+"[^>]*?/>'
    )

    obj_match2 = model_obj_re.search(model_xml)
    if obj_match2 is None:
        raise RuntimeError(f"{proj_3mf}: no <object type=model> in {MODEL_PATH}")
    obj_open2, _obj_id2, obj_body2, obj_close2 = obj_match2.groups()
    components = model_component_re.findall(obj_body2)
    # Capture the *full* component tags too (we want to preserve transforms).
    component_tags = re.findall(r'<component\b[^>]*?/>', obj_body2)
    if len(component_tags) != len(parts):
        raise RuntimeError(
            f"{proj_3mf}: {MODEL_PATH} has {len(component_tags)} components "
            f"but {CFG_PATH} has {len(parts)} parts"
        )
    # Build a mapping component objectid -> tag.
    obj_id_to_tag: dict[str, str] = {}
    for tag in component_tags:
        m = re.search(r'objectid="(\d+)"', tag)
        if m:
            obj_id_to_tag[m.group(1)] = tag

    # Build new <object> entries. Each one wraps the two component tags for
    # that specimen (struts first, cables second, matching the order they
    # were passed to --assemble).
    new_model_objects: list[str] = []
    # Determine the (composite_id, [part_id, part_id]) layout to know
    # which underlying mesh objects belong to which specimen.
    for spec_idx in sorted(spec_to_parts):
        new_obj_id = composite_obj_id + spec_idx
        comp_tags: list[str] = []
        for ext_id in sorted(spec_to_parts[spec_idx]):
            part_id, _, _ = spec_to_parts[spec_idx][ext_id]
            tag = obj_id_to_tag.get(str(part_id))
            if tag is None:
                raise RuntimeError(
                    f"{proj_3mf}: no <component objectid={part_id}> in {MODEL_PATH}"
                )
            comp_tags.append("    " + tag)
        new_model_objects.append(
            f'  <object id="{new_obj_id}" p:UUID="{uuid.uuid4()}" type="model">\n'
            f'   <components>\n'
            + "\n".join(comp_tags) + "\n"
            f'   </components>\n'
            f'  </object>'
        )
    new_model_object_block = "\n".join(new_model_objects)
    new_model_xml = (
        model_xml[: obj_match2.start()]
        + new_model_object_block
        + model_xml[obj_match2.end() :]
    )

    # Replace the single <item> in <build> with one <item> per new composite.
    build_match = model_build_re.search(new_model_xml)
    if build_match is None:
        raise RuntimeError(f"{proj_3mf}: no <build> in {MODEL_PATH}")
    build_open, build_body, build_close = build_match.groups()
    existing_item_match = model_item_re.search(build_body)
    if existing_item_match is None:
        raise RuntimeError(f"{proj_3mf}: no <item> in <build>")
    # Reuse the existing transform attribute so the plate placement stays.
    existing_item = existing_item_match.group(0)
    transform_match = re.search(r'transform="([^"]*)"', existing_item)
    printable_match = re.search(r'printable="([^"]*)"', existing_item)
    transform_attr = (
        f' transform="{transform_match.group(1)}"' if transform_match else ""
    )
    printable_attr = (
        f' printable="{printable_match.group(1)}"' if printable_match else ' printable="1"'
    )
    new_items: list[str] = []
    for new_obj_id in new_composite_ids:
        new_items.append(
            f'  <item objectid="{new_obj_id}" p:UUID="{uuid.uuid4()}"'
            f"{transform_attr}{printable_attr}/>"
        )
    new_build = build_open + "\n" + "\n".join(new_items) + "\n " + build_close
    new_model_xml = (
        new_model_xml[: build_match.start()] + new_build + new_model_xml[build_match.end() :]
    )
    contents[MODEL_PATH] = new_model_xml.encode()

    # ---- Rewrite the archive ---------------------------------------------------
    with zipfile.ZipFile(proj_3mf, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in infos:
            zout.writestr(info, contents[info.filename])


def build_mm_3mf(
    pairs: list[tuple[Path, Path]], out_3mf: Path
) -> None:
    """Assemble per-specimen (struts, cables) STL pairs into a Bambu H2D MM ``.3mf``.

    Each pair becomes its own composite object on the build plate with two
    parts (struts → extruder 1 / PLA, cables → extruder 2 / TPU), so each
    specimen can be moved as a unit in Bambu Studio while keeping the PLA
    and TPU members locked together (PR #35 comment 4513722886).

    Mirrors ``slice_bambu_mm`` from ``cad/t3-prism/render_print.sh`` but
    without ``enable_supports`` (the BO batch leaves supports off;
    @achris0520 paints them on per PR #35 comment 4502140147). Filament
    slot 1 = PLA, slot 2 = TPU 85A.
    """
    _ensure_bambu()
    tag = "H2D-MM-PLAstruts-TPUcables"
    work = SCRATCH / f"bo_{tag}"
    work.mkdir(parents=True, exist_ok=True)
    m = work / "machine_flat.json"
    p = work / "process_flat.json"
    f1 = work / "filament1_flat.json"
    f2 = work / "filament2_flat.json"
    _flatten("machine",  "Bambu Lab H2D 0.4 nozzle",              m)
    _flatten("process",  "0.20mm Standard @BBL H2D",              p)
    _flatten("filament", "Bambu PLA Basic @BBL H2D",              f1)
    _flatten("filament", "Bambu TPU 85A @BBL H2D 0.4 nozzle",     f2)
    _patch_bed(m)

    proj_3mf = out_3mf.name
    proj_outdir = work / "proj"
    if proj_outdir.exists():
        shutil.rmtree(proj_outdir)
    proj_outdir.mkdir(parents=True)

    # Flatten the pairs into a single interleaved STL list (struts0, cables0,
    # struts1, cables1, ...) — the order is what the post-processor relies on
    # to re-group parts back into per-specimen composites.
    stl_args: list[str] = []
    pairs_names: list[tuple[str, str]] = []
    name_to_ext: dict[str, str] = {}
    for struts_stl, cables_stl in pairs:
        stl_args.extend([str(struts_stl), str(cables_stl)])
        pairs_names.append((struts_stl.name, cables_stl.name))
        name_to_ext[struts_stl.name] = "1"
        name_to_ext[cables_stl.name] = "2"

    print(
        f"==> BambuStudio CLI --assemble -> {proj_3mf} "
        f"({len(pairs)} specimens x 2 parts each)"
    )
    env = {**__import__("os").environ,
           "LIBGL_ALWAYS_SOFTWARE": "1", "GALLIUM_DRIVER": "llvmpipe"}
    subprocess.run(
        ["xvfb-run", "-a", "-s", "-screen 0 1280x1024x24", str(BAMBU_APPIMAGE),
         "--assemble",
         "--load-settings",  f"{m};{p}",
         "--load-filaments", f"{f1};{f2}",
         "--export-3mf",     proj_3mf,
         "--outputdir",      str(proj_outdir),
         *stl_args],
        check=True, env=env,
    )

    # patch_mm_extruder.py: (a) pad filament_colour / filament_map to length 2
    # and set filament_map_mode=Manual, (b) per-part extruder routing.
    print(
        f"==> Patch model_settings.config: struts -> extruder 1 (PLA), "
        f"cables -> extruder 2 (TPU)"
    )
    pair_args = [f"{name}={ext}" for name, ext in name_to_ext.items()]
    subprocess.run(
        ["python3", str(T3_PRISM_DIR / "patch_mm_extruder.py"),
         str(proj_outdir / proj_3mf), *pair_args],
        check=True,
    )

    # Split the single composite object emitted by --assemble into one
    # composite per specimen so each iteration on the plate is its own
    # movable Bambu Studio object with two part groups.
    print(
        f"==> Split assembled composite -> {len(pairs)} per-specimen objects "
        f"(PLA struts + TPU cables grouped per object)"
    )
    _split_assembled_into_objects(proj_outdir / proj_3mf, pairs_names)

    out_3mf.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(proj_outdir / proj_3mf, out_3mf)


def load_designs_from_csv(csv_path: Path, n: int) -> list[dict]:
    """Read the pinned first-batch Sobol coordinates back from the committed
    design table (only the five swept parameter columns are consumed, so the
    file may carry any number of extra as-printed / constraint columns)."""
    with csv_path.open() as f:
        rows = list(csv.DictReader(f))
    if len(rows) < n:
        raise SystemExit(
            f"{csv_path} has only {len(rows)} rows but --n={n}; "
            f"pass --resample to draw a fresh Sobol batch instead")
    keys = [p["name"] for p in PARAMETERS]
    return [{k: float(row[k]) for k in keys} for row in rows[:n]]


def sample_designs_sobol(n: int, seed: int) -> list[dict]:
    """Draw a fresh Sobol batch via Ax (only used with --resample)."""
    import logging

    from ax.service.ax_client import AxClient, ObjectiveProperties

    logging.getLogger("ax").setLevel(logging.WARNING)
    # Ax's default GenerationStrategy starts with a Sobol init step, so a
    # single call to ``get_next_trials(N)`` returns N quasi-random specimens
    # without ever touching a surrogate model. We mark each trial abandoned
    # so it does not pollute future runs of the closed-loop campaign.
    ax_client = AxClient(random_seed=seed)
    ax_client.create_experiment(
        name="t3_prism_sobol_batch",
        parameters=PARAMETERS,
        # Single-objective placeholder; we never report data back this round.
        objectives={"placeholder": ObjectiveProperties(minimize=True)},
        overwrite_existing_experiment=True,
    )
    parameterizations, _ = ax_client.get_next_trials(n)
    for idx in parameterizations:
        ax_client.abandon_trial(idx, reason="human-in-the-loop single-batch")
    return [parameterizations[i] for i in sorted(parameterizations)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n", type=int, default=N_SPECIMENS,
                        help=f"number of specimens (default {N_SPECIMENS})")
    parser.add_argument("--seed", type=int, default=SEED,
                        help=f"Sobol seed (default {SEED}; only used with --resample)")
    parser.add_argument("--resample", action="store_true",
                        help="draw a fresh Sobol batch via Ax instead of reading "
                             "the pinned designs back from the committed CSV")
    parser.add_argument("--mass-g", type=float, default=None,
                        help="Route-A constant cell mass m* in grams (default: "
                             "solid-volume mass of the committed S0 reference "
                             "STLs in cad/t3-prism/, i.e. the most recent "
                             "instrumented prints)")
    parser.add_argument("--envelope-max-cm3", type=float,
                        default=DEFAULT_ENVELOPE_MAX_CM3,
                        help="Route-B max envelope volume V* = pi*R^2*H in cm^3 "
                             f"(default {DEFAULT_ENVELOPE_MAX_CM3:g}, from "
                             "simulations/sim_bo_hybrid_campaign.py)")
    parser.add_argument("--jobs", type=int, default=4,
                        help="parallel OpenSCAD render workers (default 4)")
    parser.add_argument("--skip-render", action="store_true",
                        help="emit CSV/JSON with analytic scale estimates only; "
                             "skip all OpenSCAD renders (CI smoke test)")
    parser.add_argument("--skip-mm-3mf", action="store_true",
                        help="skip the BambuStudio CLI MM project .3mf assembly step")
    args = parser.parse_args(argv)

    out_dir = Path(__file__).resolve().parent
    csv_path = out_dir / "t3-prism-bo-batch.csv"
    json_path = out_dir / "t3-prism-bo-batch.json"
    scad_path = out_dir / "t3-prism-bo-batch.scad"
    stl_path = out_dir / "t3-prism-bo-batch.stl"
    stl_struts_path = out_dir / "t3-prism-bo-batch-struts.stl"
    stl_cables_path = out_dir / "t3-prism-bo-batch-cables.stl"
    plate_png = out_dir / "t3-prism-bo-batch-plate.png"
    iso_png = out_dir / "t3-prism-bo-batch-iso.png"
    slices_dir = out_dir / "slices"
    mm_3mf_path = slices_dir / "t3-prism-bo-batch.H2D-MM-PLAstruts-TPUcables.3mf"
    per_spec_dir = out_dir / "per-specimen-stls"

    # ---- The first-batch Sobol designs -------------------------------------
    if args.resample or not csv_path.exists():
        print(f"==> Drawing a fresh Sobol batch (n={args.n}, seed={args.seed})")
        specimens = sample_designs_sobol(args.n, args.seed)
    else:
        print(f"==> Reusing the pinned first-batch designs from {csv_path.name}")
        specimens = load_designs_from_csv(csv_path, args.n)

    # ---- Constraint targets -------------------------------------------------
    m_star = args.mass_g if args.mass_g is not None else reference_mass_g()
    v_star = args.envelope_max_cm3
    print(f"==> Route-A constant mass m* = {m_star:.2f} g "
          f"({'CLI override' if args.mass_g is not None else 'S0 reference STLs'}), "
          f"Route-B envelope max V* = {v_star:.0f} cm^3")

    if not shutil.which("openscad") and not args.skip_render:
        print("openscad not found; install with `sudo apt-get install -y openscad`.",
              file=sys.stderr)
        return 2

    if args.skip_render:
        # Analytic-only pass: report the estimated projection without STLs.
        m_h = 6.8  # nominal housing mass (g); rendered runs measure it exactly
        results = []
        for idx, params in enumerate(specimens):
            s = ((m_star - m_h) / estimate_body_mass_g(params)) ** (1.0 / 3.0)
            results.append({"idx": idx, "scale": s, "mass_g": float("nan"),
                            "pla_g": float("nan"), "tpu_g": float("nan")})
    else:
        SCRATCH.mkdir(parents=True, exist_ok=True)
        m_h = housing_mass_g(SCRATCH)
        print(f"==> Absolute-size sensor-housing mass (6 housings + skirts): "
              f"{m_h:.2f} g PLA")
        solve_dir = SCRATCH / "bo-mass-solve"
        solve_dir.mkdir(parents=True, exist_ok=True)
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            results = list(pool.map(
                lambda t: solve_specimen(t[0], t[1], m_star, m_h, solve_dir),
                enumerate(specimens)))

    # ---- Constraint bookkeeping ---------------------------------------------
    for params, res in zip(specimens, results):
        s = res["scale"]
        res["envelope_cm3"] = (math.pi * (params["R_mm"] * s) ** 2
                               * params["H_mm"] * s / 1000.0)
        res["envelope_ok"] = res["envelope_cm3"] <= v_star + 1e-9
        res["mass_ok"] = (not math.isnan(res["mass_g"])
                          and abs(res["mass_g"] - m_star) <= 2 * MASS_TOL_G)
        res["cable_d_print_mm"] = params["cable_d_mm"] * s
        res["cable_bridge_ok"] = res["cable_d_print_mm"] >= CABLE_BRIDGE_FLOOR_MM
    n_env_bad = sum(not r["envelope_ok"] for r in results)
    if n_env_bad:
        bad = ", ".join(f"spec{r['idx']:02d} ({r['envelope_cm3']:.0f} cm^3)"
                        for r in results if not r["envelope_ok"])
        print(f"WARNING: {n_env_bad}/{len(results)} specimens exceed the "
              f"envelope constraint V* = {v_star:.0f} cm^3 at constant mass "
              f"m* = {m_star:.1f} g: {bad}. Their shape is infeasible under "
              f"both constraints simultaneously (the uniform scale is consumed "
              f"by the mass constraint); they are flagged envelope_ok=False.",
              file=sys.stderr)

    # ---- Plate layout from measured footprints ------------------------------
    if args.skip_render:
        footprints = [2.0 * params["R_mm"] * res["scale"] + 25.0
                      for params, res in zip(specimens, results)]
    else:
        footprints = [
            2.0 * max(abs(v) for v in (res["bbox_min"][0], res["bbox_max"][0],
                                       res["bbox_min"][1], res["bbox_max"][1]))
            for res in results]
    layout = plan_plate_layout(footprints)
    rows, cols = layout["rows"], layout["cols"]

    # ---- Persist the design table -------------------------------------------
    frozen = {
        "topology": TOPOLOGY,
        "tiling": TILING,
        "struts_per_cell": STRUTS_PER_CELL,
        "build_orientation": BUILD_ORIENTATION,
        "tpu_shore": TPU_SHORE,
        "strut_material": STRUT_MATERIAL,
        "cable_material": CABLE_MATERIAL,
        "supports": SUPPORTS,
        "joint_d_mm": JOINT_D_BASE,
    }
    derived_cols = [
        "scale", "R_print_mm", "H_print_mm", "strut_d_print_mm",
        "cable_d_print_mm", "joint_d_print_mm", "mass_g", "pla_g", "tpu_g",
        "mass_target_g", "mass_ok", "envelope_cm3", "envelope_max_cm3",
        "envelope_ok", "cable_bridge_ok",
    ]
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["specimen", *(p["name"] for p in PARAMETERS),
                         *derived_cols, *sorted(frozen)])
        for idx, (params, res) in enumerate(zip(specimens, results)):
            s = res["scale"]
            writer.writerow([
                idx,
                *(f"{params[p['name']]:.4f}" for p in PARAMETERS),
                f"{s:.4f}",
                f"{params['R_mm'] * s:.3f}",
                f"{params['H_mm'] * s:.3f}",
                f"{params['strut_d_mm'] * s:.3f}",
                f"{params['cable_d_mm'] * s:.3f}",
                f"{JOINT_D_BASE * s:.3f}",
                f"{res['mass_g']:.2f}",
                f"{res['pla_g']:.2f}",
                f"{res['tpu_g']:.2f}",
                f"{m_star:.2f}",
                res["mass_ok"],
                f"{res['envelope_cm3']:.1f}",
                f"{v_star:.1f}",
                res["envelope_ok"],
                res["cable_bridge_ok"],
                *(frozen[k] for k in sorted(frozen)),
            ])
    json_path.write_text(json.dumps(
        {
            "seed": args.seed,
            "n": args.n,
            "designs_source": ("resampled" if args.resample else "pinned-csv"),
            "constraints": {
                "mass_target_g": m_star,
                "mass_tol_g": MASS_TOL_G,
                "housing_mass_g": m_h,
                "envelope_max_cm3": v_star,
                "rho_pla_g_per_cm3": RHO_PLA * 1000,
                "rho_tpu_g_per_cm3": RHO_TPU * 1000,
                "mass_anchor": "solid-volume mass of cad/t3-prism/"
                               "t3-prism-{struts,cables}.stl (S0 reference)",
                "envelope_definition": "pi * R_print^2 * H_print "
                                       "(bo_evaluator.cell_geometry_metrics)",
            },
            "grid": {"rows": rows, "cols": cols,
                     "air_gap_mm": layout["air_gap"],
                     "col_widths_mm": layout["col_widths"],
                     "row_heights_mm": layout["row_heights"],
                     "total_w_mm": layout["total_w"],
                     "total_h_mm": layout["total_h"]},
            "plate": {"x_mm": PLATE_X, "y_mm": PLATE_Y, "margin_mm": PLATE_MARGIN,
                      "prime_tower_reserve_x_mm": PRIME_TOWER_RESERVE_X},
            "parameters": PARAMETERS,
            "frozen": frozen,
            "specimens": [
                {"idx": i, **params,
                 **{k: res[k] for k in ("scale", "mass_g", "pla_g", "tpu_g",
                                        "envelope_cm3", "envelope_ok", "mass_ok",
                                        "cable_d_print_mm", "cable_bridge_ok")}}
                for i, (params, res) in enumerate(zip(specimens, results))
            ],
        },
        indent=2,
    ))
    if args.skip_render:
        print(f"Wrote {csv_path.name}, {json_path.name} "
              f"(analytic estimates only; renders skipped).")
        return 0

    # ---- Place specimens on the plate (pure STL translation) ----------------
    per_spec_dir.mkdir(exist_ok=True)
    pairs: list[tuple[Path, Path]] = []
    for idx, res in enumerate(results):
        cx, cy = layout["centres"][idx]
        cz = -res["bbox_min"][2]  # lowest feature (joint-shell underside) -> bed
        spec_struts = per_spec_dir / SPEC_STL_FMT.format(idx=idx, part="struts")
        spec_cables = per_spec_dir / SPEC_STL_FMT.format(idx=idx, part="cables")
        stl_translate(res["struts_stl"], spec_struts, cx, cy, cz)
        stl_translate(res["cables_stl"], spec_cables, cx, cy, cz)
        pairs.append((spec_struts, spec_cables))
        print(f"==> spec{idx:02d}: scale {res['scale']:.4f}, "
              f"mass {res['mass_g']:.2f} g (PLA {res['pla_g']:.2f} + "
              f"TPU {res['tpu_g']:.2f}), envelope {res['envelope_cm3']:.1f} cm^3 "
              f"[{'ok' if res['envelope_ok'] else 'VIOLATION'}] -> "
              f"plate ({cx:.1f}, {cy:.1f})")

    # ---- Combined STLs + preview wrapper + PNGs ------------------------------
    print(f"==> Merge -> {stl_struts_path.name} / {stl_cables_path.name} / {stl_path.name}")
    stl_merge([p for p, _ in pairs], stl_struts_path)
    stl_merge([c for _, c in pairs], stl_cables_path)
    stl_merge([f for pair in pairs for f in pair], stl_path)
    write_preview_scad(scad_path, args.n, rows, cols,
                       max(layout["col_widths"] + layout["row_heights"]))
    cam_top = f"{PLATE_X/2:.1f},{PLATE_Y/2:.1f},0,0,0,0,{max(PLATE_X, PLATE_Y) * 1.4:.1f}"
    cam_iso = f"{PLATE_X/2:.1f},{PLATE_Y/2:.1f},0,55,0,25,{max(PLATE_X, PLATE_Y) * 1.6:.1f}"
    print(f"==> OpenSCAD render -> {plate_png.name} (top-down plate view)")
    run_openscad(scad_path, plate_png, camera=cam_top, image_size="1200,1100",
                 viewall=True)
    print(f"==> OpenSCAD render -> {iso_png.name} (iso preview)")
    run_openscad(scad_path, iso_png, camera=cam_iso, image_size="1200,900",
                 viewall=True)

    if not args.skip_mm_3mf:
        build_mm_3mf(pairs, mm_3mf_path)

    print("Done.")
    print(f"  Design table : {csv_path}")
    print(f"  JSON         : {json_path}")
    print(f"  Combined STL : {stl_path}")
    print(f"  Struts STL   : {stl_struts_path}")
    print(f"  Cables STL   : {stl_cables_path}")
    print(f"  Plate PNG    : {plate_png}")
    print(f"  Iso PNG      : {iso_png}")
    if not args.skip_mm_3mf:
        print(f"  MM project   : {mm_3mf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
