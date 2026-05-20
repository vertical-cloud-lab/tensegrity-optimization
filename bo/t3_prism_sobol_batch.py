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

* ``t3-prism-bo-batch.csv``               -- one row per specimen + frozen vars
* ``t3-prism-bo-batch.json``              -- same data + Ax client snapshot
* ``t3-prism-bo-batch.scad``              -- generated OpenSCAD wrapper
* ``t3-prism-bo-batch.stl``               -- packed-on-plate combined STL
* ``t3-prism-bo-batch-plate.png``         -- top-down build-plate preview PNG
* ``t3-prism-bo-batch-iso.png``           -- iso preview PNG

Run::

    pip install ax-platform numpy
    sudo apt-get install -y openscad xvfb
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

# ---- Sobol batch knobs -----------------------------------------------------
N_SPECIMENS = 9      # 3x3 grid; manageable for the first human-in-the-loop pass
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


def specimen_footprint(r_mm: float, strut_d_mm: float, joint_d_mm: float = JOINT_D_BASE) -> float:
    """Conservative bounding box edge length (mm) for one specimen.

    A T3-prism's triangular caps inscribe in a circle of radius R; the worst-
    case footprint of the assembly is the diameter (2R) plus the joint sphere
    radius (so the corner nodes are wholly inside) plus a thin strut-shaft
    margin so adjacent specimens cannot graze each other.
    """
    return 2.0 * r_mm + joint_d_mm + strut_d_mm


def grid_layout(n: int, footprints: list[float]) -> tuple[int, int, float, float]:
    """Choose a rows x cols grid that fits on the plate.

    Returns (n_rows, n_cols, cell_x, cell_y). Cell dimensions are sized to
    the worst-case specimen footprint plus a 5 mm air gap, then padded to
    the plate margins.
    """
    # Square-ish grid.
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    air_gap = 5.0
    cell = max(footprints) + air_gap
    return rows, cols, cell, cell


SPECIMEN_TEMPLATE = """\
// specimen {idx:02d}  R={R:.2f} H={H:.2f} twist={tw:.2f} strut_d={sd:.2f} cable_d={cd:.2f}
module specimen_{idx:02d}() {{
    R={R:.4f}; H={H:.4f}; twist_={tw:.4f};
    strut_d={sd:.4f}; cable_d={cd:.4f}; joint_d={jd:.4f};
    module member_(p1,p2,d) {{
        v=p2-p1; L=norm(v);
        yaw=atan2(v[1],v[0]);
        pitch=atan2(sqrt(v[0]*v[0]+v[1]*v[1]),v[2]);
        translate(p1) rotate([0,0,yaw]) rotate([0,pitch,0]) {{
            cylinder(h=L,d=d); sphere(d=d); translate([0,0,L]) sphere(d=d);
        }}
    }}
    function bp(i)=[R*cos(90+120*i), R*sin(90+120*i), 0];
    function tp(i)=[R*cos(90+120*i+twist_), R*sin(90+120*i+twist_), H];
    union() {{
        for (i=[0:2]) {{
            translate(bp(i)) sphere(d=joint_d);
            translate(tp(i)) sphere(d=joint_d);
            member_(bp(i), tp(i), strut_d);
            member_(bp(i), bp((i+1)%3), cable_d);
            member_(tp(i), tp((i+1)%3), cable_d);
            member_(bp((i+1)%3), tp(i), cable_d);
        }}
    }}
}}
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
    # Centre the grid on the plate.
    grid_w = cols * cell_x
    grid_h = rows * cell_y
    x0 = (PLATE_X - grid_w) / 2.0 + cell_x / 2.0
    y0 = (PLATE_Y - grid_h) / 2.0 + cell_y / 2.0
    # Lift each specimen so the bottom-triangle joint sphere underside sits
    # on the plate (matches the Bambu Studio auto-bed-placement behaviour).
    z_lift = JOINT_D_BASE / 2.0
    parts: list[str] = []
    parts.append(
        "// AUTO-GENERATED by bo/t3_prism_sobol_batch.py — do not hand-edit.\n"
        "// Single-batch Sobol design set for the T3-prism BO campaign\n"
        "// (PR #35 comment 4503109338). All specimens vertically oriented\n"
        "// (load axis = z). Supports will be manually painted in Bambu\n"
        "// Studio per @achris0520's tip in PR #35 comment 4502140147.\n"
        f"// Plate: {PLATE_X:.0f} x {PLATE_Y:.0f} mm (Bambu Lab H2D).\n"
        f"// Grid : {rows} x {cols} (cell {cell_x:.1f} x {cell_y:.1f} mm).\n"
        "\n"
    )
    for idx, params in enumerate(specimens):
        col = idx % cols
        row = idx // cols
        cx = x0 + col * cell_x
        cy = y0 + row * cell_y
        parts.append(emit_specimen_scad(idx, params, cx, cy, z_lift))
    path.write_text("".join(parts))


def run_openscad(scad: Path, out: Path, *, camera: str | None = None,
                 image_size: str | None = None) -> None:
    """Invoke OpenSCAD headlessly via xvfb-run, writing STL or PNG."""
    cmd = ["xvfb-run", "-a", "openscad", "-o", str(out)]
    if out.suffix == ".stl":
        cmd += ["--export-format=binstl"]
    if camera:
        cmd += [f"--camera={camera}"]
    if image_size:
        cmd += [f"--imgsize={image_size}"]
    cmd += [str(scad)]
    subprocess.run(cmd, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n", type=int, default=N_SPECIMENS,
                        help=f"number of specimens (default {N_SPECIMENS})")
    parser.add_argument("--seed", type=int, default=SEED,
                        help=f"Sobol seed (default {SEED})")
    parser.add_argument("--skip-render", action="store_true",
                        help="emit SCAD + CSV/JSON but skip OpenSCAD STL/PNG renders")
    args = parser.parse_args(argv)

    out_dir = Path(__file__).resolve().parent
    csv_path = out_dir / "t3-prism-bo-batch.csv"
    json_path = out_dir / "t3-prism-bo-batch.json"
    scad_path = out_dir / "t3-prism-bo-batch.scad"
    stl_path = out_dir / "t3-prism-bo-batch.stl"
    plate_png = out_dir / "t3-prism-bo-batch-plate.png"
    iso_png = out_dir / "t3-prism-bo-batch-iso.png"

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
    footprints = [specimen_footprint(s["R_mm"], s["strut_d_mm"]) for s in specimens]
    rows, cols, cell_x, cell_y = grid_layout(args.n, footprints)
    grid_w = cols * cell_x
    grid_h = rows * cell_y
    if grid_w > PLATE_X - 2 * PLATE_MARGIN or grid_h > PLATE_Y - 2 * PLATE_MARGIN:
        print(
            f"WARNING: grid {grid_w:.1f}x{grid_h:.1f} mm exceeds plate "
            f"{PLATE_X - 2 * PLATE_MARGIN:.1f}x{PLATE_Y - 2 * PLATE_MARGIN:.1f} mm",
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
            "plate": {"x_mm": PLATE_X, "y_mm": PLATE_Y, "margin_mm": PLATE_MARGIN},
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
    # Top-down build-plate camera: distance, fov, then translate above plate centre.
    cam_top = f"{PLATE_X/2:.1f},{PLATE_Y/2:.1f},0,0,0,0,{max(PLATE_X, PLATE_Y) * 1.4:.1f}"
    cam_iso = f"{PLATE_X/2:.1f},{PLATE_Y/2:.1f},0,55,0,25,{max(PLATE_X, PLATE_Y) * 1.6:.1f}"
    print(f"==> OpenSCAD render -> {plate_png.name} (top-down plate view)")
    run_openscad(scad_path, plate_png, camera=cam_top, image_size="1200,1100")
    print(f"==> OpenSCAD render -> {iso_png.name} (iso preview)")
    run_openscad(scad_path, iso_png, camera=cam_iso, image_size="1200,900")
    print("Done.")
    print(f"  Design table : {csv_path}")
    print(f"  JSON         : {json_path}")
    print(f"  Combined STL : {stl_path}")
    print(f"  Plate PNG    : {plate_png}")
    print(f"  Iso PNG      : {iso_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
