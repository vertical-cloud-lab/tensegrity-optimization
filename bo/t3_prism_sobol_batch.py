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
supports failing mid-print.

Output files (next to this script):

* ``t3-prism-bo-batch.csv``                                       -- one row per specimen + frozen vars
* ``t3-prism-bo-batch.json``                                      -- same data + Ax client snapshot
* ``t3-prism-bo-batch.scad``                                      -- generated OpenSCAD wrapper
* ``t3-prism-bo-batch.stl``                                       -- packed-on-plate combined STL (all parts fused)
* ``t3-prism-bo-batch-struts.stl``                                -- struts + joint spheres only (extruder 1 / PLA)
* ``t3-prism-bo-batch-cables.stl``                                -- cables only (extruder 2 / TPU)
* ``t3-prism-bo-batch-plate.png``                                 -- top-down build-plate preview PNG
* ``t3-prism-bo-batch-iso.png``                                   -- iso preview PNG
* ``slices/t3-prism-bo-batch.H2D-MM-PLAstruts-TPUcables.3mf``     -- Bambu H2D MM project (struts/PLA + cables/TPU,
                                                                     re-importable into Bambu Studio with
                                                                     per-part extruder assignment; *no* supports —
                                                                     paint them on manually per @achris0520's tip
                                                                     in PR #35 comment 4502140147)

Run::

    pip install ax-platform numpy
    sudo apt-get install -y openscad admesh xvfb \\
        gstreamer1.0-plugins-base libsoup-3.0-0 libwebkit2gtk-4.1-0
    python3 bo/t3_prism_sobol_batch.py
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import shutil
import subprocess
import sys
from pathlib import Path

from ax.service.ax_client import AxClient, ObjectiveProperties

logging.getLogger("ax").setLevel(logging.WARNING)

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


def specimen_footprint(r_mm: float, strut_d_mm: float, joint_d_mm: float = JOINT_D_BASE,
                       cable_d_mm: float = 0.0) -> float:
    """Bounding box edge length (mm) for one specimen.

    A T3-prism's triangular caps inscribe in a circle of radius R; the
    outermost geometry is the captive-core joint shell at each corner, so
    the bounding diameter is ``2R + shell_od`` (with ``shell_od`` derived
    the same way the SCAD template does it — see ``SPECIMEN_TEMPLATE``).
    Strut/cable cylinders fall *inside* this circle (they connect corners)
    so they do not extend the footprint.
    """
    del strut_d_mm  # kept for backwards-compatible signature
    if cable_d_mm > 0:
        # Mirror the captive-core SCAD: bore = cable_d (zero clearance —
        # TPU fills bore exactly, bonded), core_od = max(bore+3, joint_d),
        # shell_id = core_od (TPU core touches PLA — bonded), shell_od =
        # max(shell_id+3.2, joint_d). PR #35 comment 4513722886.
        bore_d = cable_d_mm
        core_od = max(bore_d + 2 * 1.5, joint_d_mm)
        shell_id = core_od
        shell_od = max(shell_id + 2 * 1.6, joint_d_mm)
    else:
        shell_od = joint_d_mm
    return 2.0 * r_mm + shell_od


def grid_layout(n: int, footprints: list[float]) -> tuple[int, int, float, float]:
    """Choose a rows x cols grid that fits on the plate.

    Returns (n_rows, n_cols, cell_x, cell_y). Cell dimensions are sized to
    the worst-case specimen footprint plus a small air gap; specimens that
    are smaller than the worst case still benefit from the tight pack since
    we keep the grid square.

    Honours ``PRIME_TOWER_RESERVE_X`` — the +X strip is unavailable, so we
    prefer layouts that are taller than they are wide.
    """
    # 6 mm air gap restores breathing room between specimen bounding
    # circles (the previous 2 mm gap from PR #35 comment 4503427854 was
    # "too tight last time" per PR #35 comment 4513164299) while still
    # allowing 3x3 packing to fit inside the prime-tower-reduced usable
    # area (PR #35 comment 4513445377).
    air_gap = 6.0
    cell = max(footprints) + air_gap
    usable_x = PLATE_X - 2 * PLATE_MARGIN - PRIME_TOWER_RESERVE_X
    usable_y = PLATE_Y - 2 * PLATE_MARGIN
    # Prefer the most square-ish layout that *fits*. Sweep candidate column
    # counts from 1..n; for each, derive rows = ceil(n/cols), check both
    # dimensions, score by "squareness" (smaller |rows-cols|).
    best: tuple[int, int] | None = None
    best_score = math.inf
    for cols in range(1, n + 1):
        rows = math.ceil(n / cols)
        if cols * cell > usable_x or rows * cell > usable_y:
            continue
        score = abs(rows - cols) + 0.01 * (rows * cols - n)  # tie-break: fewer empty cells
        if score < best_score:
            best_score = score
            best = (rows, cols)
    if best is None:
        # Fall back to original square-ish grid; caller will print a warning.
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        best = (rows, cols)
    rows, cols = best
    return rows, cols, cell, cell


SPECIMEN_TEMPLATE = """\
// specimen {idx:02d}  R={R:.2f} H={H:.2f} twist={tw:.2f} strut_d={sd:.2f} cable_d={cd:.2f}
// Captive-core joint params (mirror cad/t3-prism/t3-prism.scad,
// PR #35 comment 4513722886 + 4514072758): bore = cable_d (zero
// clearance — TPU fills the bore exactly); core_od >= bore + 2*1.5
// mm so the captive TPU mass cannot back out the bore; shell_id =
// core_od (TPU core touches PLA inner wall — bonded joint); shell_od =
// shell_id + 2*1.6 mm PLA wall (lifted to >= joint_d so the joint is
// never smaller than the legacy design). The shell uses a teardrop
// hull blend toward the strut axis (PR #35 comment 4514072758 — "the
// teardrop shape was fine"), and cable bores are OUTWARD-ONLY so they
// don't punch holes through the opposite side of the shell.
S{idx:02d}_BORE_D    = {cd:.4f};
S{idx:02d}_CORE_OD   = max(S{idx:02d}_BORE_D + 2*1.5, {jd:.4f});
S{idx:02d}_SHELL_ID  = S{idx:02d}_CORE_OD;
S{idx:02d}_SHELL_OD  = max(S{idx:02d}_SHELL_ID + 2*1.6, {jd:.4f});
S{idx:02d}_TEARDROP_Z = 1.5;
S{idx:02d}_TEARDROP_D = {sd:.4f} * 1.10;
module specimen_{idx:02d}_member(p1, p2, d) {{
    v=p2-p1; L=norm(v);
    yaw=atan2(v[1],v[0]);
    pitch=atan2(sqrt(v[0]*v[0]+v[1]*v[1]),v[2]);
    translate(p1) rotate([0,0,yaw]) rotate([0,pitch,0]) {{
        cylinder(h=L,d=d); sphere(d=d); translate([0,0,L]) sphere(d=d);
    }}
}}
module specimen_{idx:02d}_bore(dir, d, len) {{
    // Outward-only bore (see cad/t3-prism/t3-prism.scad bore_along() —
    // the previous centred bore punched holes through both sides of
    // the shell, PR #35 comment 4514072758).
    yaw=atan2(dir[1],dir[0]);
    pitch=atan2(sqrt(dir[0]*dir[0]+dir[1]*dir[1]),dir[2]);
    rotate([0,0,yaw]) rotate([0,pitch,0]) translate([0,0,-0.5])
        cylinder(h=len + 0.5, d=d);
}}
function specimen_{idx:02d}_bp(i) = [{R:.4f}*cos(90+120*i), {R:.4f}*sin(90+120*i), 0];
function specimen_{idx:02d}_tp(i) = [{R:.4f}*cos(90+120*i+{tw:.4f}),
                                     {R:.4f}*sin(90+120*i+{tw:.4f}), {H:.4f}];
function specimen_{idx:02d}_unit(v) = v / norm(v);
function specimen_{idx:02d}_sdir_b(i) =
    specimen_{idx:02d}_unit(specimen_{idx:02d}_tp(i) - specimen_{idx:02d}_bp(i));
function specimen_{idx:02d}_sdir_t(i) =
    specimen_{idx:02d}_unit(specimen_{idx:02d}_bp(i) - specimen_{idx:02d}_tp(i));
function specimen_{idx:02d}_cdirs_b(i) = [
    specimen_{idx:02d}_unit(specimen_{idx:02d}_bp((i+1)%3) - specimen_{idx:02d}_bp(i)),
    specimen_{idx:02d}_unit(specimen_{idx:02d}_bp((i+2)%3) - specimen_{idx:02d}_bp(i)),
    specimen_{idx:02d}_unit(specimen_{idx:02d}_tp((i+2)%3) - specimen_{idx:02d}_bp(i)),
];
function specimen_{idx:02d}_cdirs_t(i) = [
    specimen_{idx:02d}_unit(specimen_{idx:02d}_tp((i+1)%3) - specimen_{idx:02d}_tp(i)),
    specimen_{idx:02d}_unit(specimen_{idx:02d}_tp((i+2)%3) - specimen_{idx:02d}_tp(i)),
    specimen_{idx:02d}_unit(specimen_{idx:02d}_bp((i+1)%3) - specimen_{idx:02d}_tp(i)),
];
module specimen_{idx:02d}_shell(V, sdir, cdirs) {{
    translate(V) difference() {{
        // Teardrop hull blend toward the strut axis (PR #35 comment
        // 4514072758 — "the teardrop shape was fine"). The strut
        // emerges from the bump, not through a punched hole.
        hull() {{
            sphere(d=S{idx:02d}_SHELL_OD);
            translate(sdir * (S{idx:02d}_SHELL_OD/2 + S{idx:02d}_TEARDROP_Z))
                sphere(d=S{idx:02d}_TEARDROP_D);
        }}
        sphere(d=S{idx:02d}_SHELL_ID);
        for (cd = cdirs)
            specimen_{idx:02d}_bore(cd, S{idx:02d}_BORE_D, S{idx:02d}_SHELL_OD);
    }}
}}
module specimen_{idx:02d}_struts() {{
    union() {{
        for (i=[0:2]) {{
            specimen_{idx:02d}_shell(specimen_{idx:02d}_bp(i),
                                     specimen_{idx:02d}_sdir_b(i),
                                     specimen_{idx:02d}_cdirs_b(i));
            specimen_{idx:02d}_shell(specimen_{idx:02d}_tp(i),
                                     specimen_{idx:02d}_sdir_t(i),
                                     specimen_{idx:02d}_cdirs_t(i));
            specimen_{idx:02d}_member(specimen_{idx:02d}_bp(i),
                                     specimen_{idx:02d}_tp(i), {sd:.4f});
        }}
    }}
}}
module specimen_{idx:02d}_cables() {{
    union() {{
        for (i=[0:2]) {{
            specimen_{idx:02d}_member(specimen_{idx:02d}_bp(i),
                                     specimen_{idx:02d}_bp((i+1)%3), {cd:.4f});
            specimen_{idx:02d}_member(specimen_{idx:02d}_tp(i),
                                     specimen_{idx:02d}_tp((i+1)%3), {cd:.4f});
            specimen_{idx:02d}_member(specimen_{idx:02d}_bp((i+1)%3),
                                     specimen_{idx:02d}_tp(i),       {cd:.4f});
            // Captive TPU cores inside each PLA shell cavity.
            translate(specimen_{idx:02d}_bp(i)) sphere(d=S{idx:02d}_CORE_OD);
            translate(specimen_{idx:02d}_tp(i)) sphere(d=S{idx:02d}_CORE_OD);
        }}
        // Bounding-box z-anchor so cables.stl inherits the struts.stl
        // world-Z extents (fixes the "cables too low" misalignment;
        // see cad/t3-prism/t3-prism.scad cables_z_anchor()).
        translate([0, 0, -S{idx:02d}_SHELL_OD/2])
            cube([0.005, 0.005, {H:.4f} + S{idx:02d}_SHELL_OD], center=false);
    }}
}}
module specimen_{idx:02d}() {{
    if      (part == "struts") specimen_{idx:02d}_struts();
    else if (part == "cables") specimen_{idx:02d}_cables();
    else union() {{ specimen_{idx:02d}_struts(); specimen_{idx:02d}_cables(); }}
}}
if (spec == -1 || spec == {idx})
    translate([{cx:.3f}, {cy:.3f}, {cz:.3f}]) specimen_{idx:02d}();
"""


def emit_specimen_scad(idx: int, params: dict, cx: float, cy: float, cz: float) -> str:
    """SCAD snippet that instantiates one specimen at the given plate coords.

    Each specimen is wrapped in its own module so $fn / variable shadowing
    cannot leak across specimens in the unioned plate file.
    """
    return SPECIMEN_TEMPLATE.format(
        idx=idx,
        R=params["R_mm"], H=params["H_mm"], tw=params["twist_deg"],
        sd=params["strut_d_mm"], cd=params["cable_d_mm"], jd=JOINT_D_BASE,
        cx=cx, cy=cy, cz=cz,
    )


def write_batch_scad(path: Path, specimens: list[dict], rows: int, cols: int,
                     cell_x: float, cell_y: float) -> None:
    """Write the OpenSCAD wrapper that unions all specimens onto one plate."""
    # Centre the grid on the *usable* portion of the plate (i.e. the plate
    # minus the +X strip reserved for the IDEX prime/flush tower, per
    # PR #35 comment 4513164299).
    grid_w = cols * cell_x
    grid_h = rows * cell_y
    usable_x = PLATE_X - PRIME_TOWER_RESERVE_X
    x0 = (usable_x - grid_w) / 2.0 + cell_x / 2.0
    y0 = (PLATE_Y - grid_h) / 2.0 + cell_y / 2.0
    # Lift each specimen so the bottom of every captive-core PLA shell sits
    # at the build plate (matches Bambu's auto-bed-placement). The captive
    # shell OD is the larger of (cable_d + 5.4 mm) and JOINT_D_BASE, so the
    # bottom-vertex shell underside is at SCAD z = -shell_od/2 ≤ -joint_d/2.
    # Use the worst-case (largest shell_od across the batch) so EVERY
    # specimen's shell underside lands on or below the bed.
    max_cable_d = max(s["cable_d_mm"] for s in specimens)
    max_shell_od = max(max_cable_d + 2*1.5 + 2*1.6, JOINT_D_BASE)
    z_lift = max_shell_od / 2.0
    parts: list[str] = []
    parts.append(
        "// AUTO-GENERATED by bo/t3_prism_sobol_batch.py — do not hand-edit.\n"
        "// Single-batch Sobol design set for the T3-prism BO campaign\n"
        "// (PR #35 comment 4503109338). All specimens vertically oriented\n"
        "// (load axis = z). Supports will be manually painted in Bambu\n"
        "// Studio per @achris0520's tip in PR #35 comment 4502140147.\n"
        f"// Plate: {PLATE_X:.0f} x {PLATE_Y:.0f} mm (Bambu Lab H2D).\n"
        f"// Grid : {rows} x {cols} (cell {cell_x:.1f} x {cell_y:.1f} mm).\n"
        "//\n"
        "// `part` selects which half of each specimen to emit, mirroring\n"
        "// `cad/t3-prism/t3-prism.scad`:\n"
        "//   \"all\"    -> struts + cables fused (preview / single-material)\n"
        "//   \"struts\" -> rigid skeleton + joint spheres (PLA / extruder 1)\n"
        "//   \"cables\" -> tension members only (TPU / extruder 2)\n"
        "// Override at the CLI with `-D 'part=\"struts\"'`.\n"
        "part = \"all\";  // \"all\" | \"struts\" | \"cables\"\n"
        "// `spec` filters which specimen to emit; -1 (default) emits all\n"
        "// of them on the plate. Per-specimen STLs are rendered by the\n"
        "// driver with `-D spec=N` (PR #35 comment 4513722886): the\n"
        "// resulting per-specimen pair of struts/cables STLs is what\n"
        "// lets BambuStudio --assemble produce one composite object per\n"
        "// specimen instead of one giant fused object.\n"
        "spec = -1;\n"
        "\n"
    )
    for idx, params in enumerate(specimens):
        col = idx % cols
        row = idx // cols
        cx = x0 + col * cell_x
        cy = y0 + row * cell_y
        parts.append(emit_specimen_scad(idx, params, cx, cy, z_lift))
    # Render a thin visual marker for the reserved prime/flush-tower zone
    # (rendered only when ``part == "all"`` so it never leaks into the
    # struts/cables STLs the slicer assembles into the H2D MM .3mf).
    pt_x = PRIME_TOWER_RESERVE_X - 2 * PLATE_MARGIN
    parts.append(
        f"\n// Visual marker for the IDEX prime/flush-tower reserve zone.\n"
        f"// {PRIME_TOWER_RESERVE_X:.0f} mm wide strip on the +X side of the\n"
        f"// plate is held back from the specimen grid so the slicer can\n"
        f"// drop a wipe tower there without colliding (PR #35 comment\n"
        f"// 4513164299).\n"
        f"if (spec == -1 && part == \"all\") {{\n"
        f"  translate([{PLATE_X - PRIME_TOWER_RESERVE_X + PLATE_MARGIN:.2f}, "
        f"{PLATE_MARGIN:.2f}, 0])\n"
        f"    cube([{pt_x:.2f}, {PLATE_Y - 2 * PLATE_MARGIN:.2f}, 0.2]);\n"
        f"}}\n"
    )
    path.write_text("".join(parts))


def run_openscad(scad: Path, out: Path, *, camera: str | None = None,
                 image_size: str | None = None, defines: dict | None = None) -> None:
    """Invoke OpenSCAD headlessly via xvfb-run, writing STL or PNG."""
    cmd = ["xvfb-run", "-a", "openscad", "-o", str(out)]
    if out.suffix == ".stl":
        cmd += ["--export-format=binstl"]
    if camera:
        cmd += [f"--camera={camera}"]
    if image_size:
        cmd += [f"--imgsize={image_size}"]
    for k, v in (defines or {}).items():
        if isinstance(v, str):
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
REPO_ROOT = Path(__file__).resolve().parent.parent
T3_PRISM_DIR = REPO_ROOT / "cad" / "t3-prism"
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n", type=int, default=N_SPECIMENS,
                        help=f"number of specimens (default {N_SPECIMENS})")
    parser.add_argument("--seed", type=int, default=SEED,
                        help=f"Sobol seed (default {SEED})")
    parser.add_argument("--skip-render", action="store_true",
                        help="emit SCAD + CSV/JSON but skip OpenSCAD STL/PNG renders")
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

    # ---- Sobol-only Ax client (no model / no eval) -------------------------
    # Ax's default GenerationStrategy starts with a Sobol init step, so a
    # single call to ``get_next_trials(N)`` returns N quasi-random specimens
    # without ever touching a surrogate model. We mark each trial abandoned
    # so it does not pollute future runs of the closed-loop campaign.
    ax_client = AxClient(random_seed=args.seed)
    ax_client.create_experiment(
        name="t3_prism_sobol_batch",
        parameters=PARAMETERS,
        # Single-objective placeholder; we never report data back this round.
        # We just need *an* objective so AxClient creates a valid experiment.
        objectives={"placeholder": ObjectiveProperties(minimize=True)},
        overwrite_existing_experiment=True,
    )
    parameterizations, _ = ax_client.get_next_trials(args.n)
    specimens = [parameterizations[i] for i in sorted(parameterizations)]
    for idx in parameterizations:
        ax_client.abandon_trial(idx, reason="human-in-the-loop single-batch")

    # ---- Pack onto the H2D build plate -------------------------------------
    footprints = [specimen_footprint(s["R_mm"], s["strut_d_mm"],
                                     cable_d_mm=s["cable_d_mm"])
                  for s in specimens]
    rows, cols, cell_x, cell_y = grid_layout(args.n, footprints)
    grid_w = cols * cell_x
    grid_h = rows * cell_y
    if grid_w > PLATE_X - 2 * PLATE_MARGIN - PRIME_TOWER_RESERVE_X or grid_h > PLATE_Y - 2 * PLATE_MARGIN:
        print(
            f"WARNING: grid {grid_w:.1f}x{grid_h:.1f} mm exceeds usable plate "
            f"{PLATE_X - 2 * PLATE_MARGIN - PRIME_TOWER_RESERVE_X:.1f}x{PLATE_Y - 2 * PLATE_MARGIN:.1f} mm "
            f"(plate {PLATE_X:.0f}x{PLATE_Y:.0f} - prime-tower reserve {PRIME_TOWER_RESERVE_X:.0f} mm in +X)",
            file=sys.stderr,
        )

    # ---- Persist the design table -----------------------------------------
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
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["specimen", *(p["name"] for p in PARAMETERS), *sorted(frozen)]
        )
        for idx, params in enumerate(specimens):
            writer.writerow(
                [idx, *(f"{params[p['name']]:.4f}" for p in PARAMETERS),
                 *(frozen[k] for k in sorted(frozen))]
            )
    json_path.write_text(json.dumps(
        {
            "seed": args.seed,
            "n": args.n,
            "grid": {"rows": rows, "cols": cols, "cell_x": cell_x, "cell_y": cell_y},
            "plate": {"x_mm": PLATE_X, "y_mm": PLATE_Y, "margin_mm": PLATE_MARGIN,
                       "prime_tower_reserve_x_mm": PRIME_TOWER_RESERVE_X},
            "parameters": PARAMETERS,
            "frozen": frozen,
            "specimens": [{"idx": i, **s} for i, s in enumerate(specimens)],
        },
        indent=2,
    ))

    # ---- Render combined SCAD -> STL + PNG previews ------------------------
    write_batch_scad(scad_path, specimens, rows, cols, cell_x, cell_y)
    if args.skip_render:
        print(f"Wrote {csv_path.name}, {json_path.name}, {scad_path.name} (skipped renders).")
        return 0
    if not shutil.which("openscad"):
        print("openscad not found; install with `sudo apt-get install -y openscad`.",
              file=sys.stderr)
        return 2

    print(f"==> OpenSCAD render -> {stl_path.name} (n={args.n} specimens on plate)")
    run_openscad(scad_path, stl_path)
    print(f"==> OpenSCAD render -> {stl_struts_path.name} (struts + joints only, extruder 1 / PLA)")
    run_openscad(scad_path, stl_struts_path, defines={"part": "struts"})
    print(f"==> OpenSCAD render -> {stl_cables_path.name} (cables only, extruder 2 / TPU)")
    run_openscad(scad_path, stl_cables_path, defines={"part": "cables"})

    # Per-specimen STLs (one struts + one cables STL per specimen) — the
    # BambuStudio --assemble step uses these to build one composite object
    # per specimen with two parts each (PR #35 comment 4513722886).
    per_spec_dir = out_dir / "per-specimen-stls"
    per_spec_dir.mkdir(exist_ok=True)
    pairs: list[tuple[Path, Path]] = []
    for spec_idx in range(args.n):
        spec_struts = per_spec_dir / f"t3-prism-bo-spec{spec_idx:02d}-struts.stl"
        spec_cables = per_spec_dir / f"t3-prism-bo-spec{spec_idx:02d}-cables.stl"
        print(f"==> OpenSCAD render -> {spec_struts.relative_to(out_dir)}")
        run_openscad(scad_path, spec_struts,
                     defines={"part": "struts", "spec": spec_idx})
        print(f"==> OpenSCAD render -> {spec_cables.relative_to(out_dir)}")
        run_openscad(scad_path, spec_cables,
                     defines={"part": "cables", "spec": spec_idx})
        pairs.append((spec_struts, spec_cables))
    # Top-down build-plate camera: distance, fov, then translate above plate centre.
    cam_top = f"{PLATE_X/2:.1f},{PLATE_Y/2:.1f},0,0,0,0,{max(PLATE_X, PLATE_Y) * 1.4:.1f}"
    cam_iso = f"{PLATE_X/2:.1f},{PLATE_Y/2:.1f},0,55,0,25,{max(PLATE_X, PLATE_Y) * 1.6:.1f}"
    print(f"==> OpenSCAD render -> {plate_png.name} (top-down plate view)")
    run_openscad(scad_path, plate_png, camera=cam_top, image_size="1200,1100")
    print(f"==> OpenSCAD render -> {iso_png.name} (iso preview)")
    run_openscad(scad_path, iso_png, camera=cam_iso, image_size="1200,900")

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
