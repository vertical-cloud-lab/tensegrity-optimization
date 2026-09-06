"""Render the print files (per-specimen STLs + Bambu H2D MM project) for a
constant-printed-mass suggestions batch.

Why this exists
---------------
PR #35's generator (``bo/t3_prism_sobol_batch.py``, branch
``copilot/get-bambu-sliced-print-t3-prism``) owns the specimen geometry, but its
Route A projection re-solves every design onto constant SOLID mass (30.95 g) by
iterating the uniform scale on rendered STL volumes. Feeding it a BO suggestion
table therefore silently discards the constant-printed-mass projection the
campaign solved, which is exactly how the round-2 plate ended up spanning
17.3 to 22.5 g predicted printed while the model thought it was controlling
mass. This script closes that gap, the standing "re-point Route A at printed
grams" blocker: it renders each design at the scale ALREADY SOLVED by
``bo/t3_prism_bo_campaign.py`` via ``bo/t3_prism_mass_model.py`` (constant
printed grams, per-article infill fed back into the scale), so the STLs match
the as-printed geometry recorded in the suggestions CSV exactly and no mass
re-solve happens here.

The geometry itself is unchanged: every specimen renders straight from the
canonical ``cad/t3-prism/t3-prism.scad`` (copied byte-identical onto this
branch from ``copilot/get-bambu-sliced-print-t3-prism`` commit ``dbb5011``)
via ``-D`` overrides, so it carries the latest captive-core joints, the three
top-vertex igloo accelerometer mounts and the three bottom key-seats, which
stay at their absolute physical size while everything else scales. The STL
helpers, plate layout and the Bambu multi-material ``.3mf`` assembly are
adapted from the same PR #35 generator (see it for the full history of those
choices); differences here beyond the projection:

* Per-specimen STLs are named by Ax trial (``...-t28-struts.stl``) rather than
  plate position, so no raster-order inference is ever needed to map an
  article back to its design (the round-2 print key needed a photo shoot to
  settle exactly that).
* The ``.3mf`` uses the profiles the lab actually prints with (H2D 0.6 nozzle
  machine, ``0.30mm Standard @BBL H2D 0.6 nozzle`` process, verified against
  ``Metadata/project_settings.config`` of the printed round-2 plate) and the
  round-3 recipe's TPU preset ``Bambu TPU 85A @BBL H2D`` (the non-0.4-nozzle
  variant whose temperature window reaches 250 C).
* The batch's filament settings (nozzle temperatures and max volumetric
  speeds) are read from the suggestions CSV and written into the project's
  filament configs, and each part carries its article's sparse infill density
  as a per-part override. Verify both on import (select a part and check its
  settings list shows "Sparse infill density"); if the override did not
  survive the import, set the 18 values by hand per the plate recipe.
* Rendered volumes are pushed back through the calibrated printed-mass model
  as a verification column (``printed_g_est``): agreement with the 20.23 g
  target is limited by the model's analytic-to-rendered residual (~0.2 g),
  not by this script.

Run (from the repo root)::

    sudo apt-get install -y openscad xvfb libfuse2
    python3 bo/t3_prism_printed_mass_plate.py            # round 3 by default

Outputs land in ``bo/``: ``per-specimen-stls/<prefix>-tNN-{struts,cables}.stl``
(plate-positioned pairs), ``<prefix>-designs.csv`` (the manifest with the
rendered-mass verification), ``<prefix>-plate.json``, ``<prefix>.scad`` +
plate/iso preview PNGs, and ``slices/<prefix>.H2D-MM-PLAstruts-TPUcables.3mf``.
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

BO_DIR = Path(__file__).resolve().parent
REPO_ROOT = BO_DIR.parent
T3_PRISM_DIR = REPO_ROOT / "cad" / "t3-prism"
CANONICAL_SCAD = T3_PRISM_DIR / "t3-prism.scad"

sys.path.insert(0, str(BO_DIR))
from t3_prism_mass_model import (  # noqa: E402
    DEFAULT_PRINTED_MASS_TARGET_G,
    JOINT_D_BASE,
    PARAM_NAMES,
    RHO_PLA,
    RHO_TPU,
    analytic_body_volumes_split,
    calibrate,
    captive_core_od,
)

# ---- Build-plate geometry (Bambu Lab H2D), identical to PR #35 --------------
PLATE_X = 350.0  # mm
PLATE_Y = 320.0  # mm
PLATE_MARGIN = 5.0
PRIME_TOWER_RESERVE_X = 50.0  # +X strip kept clear for the IDEX prime tower

DEFAULT_DESIGNS = BO_DIR / "t3-prism-bo-suggestions-round3.csv"
DEFAULT_PREFIX = "t3-prism-bo-round3"

# Values the print columns of the source CSV must reproduce at the derived
# scale; anything larger means the CSV and this script disagree about the
# projection and nothing should be rendered.
PRINT_COLUMN_TOL_MM = 2e-3


# ---- Binary-STL helpers (adapted from bo/t3_prism_sobol_batch.py) -----------
def _stl_records(data: bytes):
    n = struct.unpack_from("<I", data, 80)[0]
    off = 84
    for _ in range(n):
        yield struct.unpack_from("<9f", data, off + 12)
        off += 50


def stl_volume_bbox(path: Path) -> tuple[float, list[float], list[float]]:
    """Signed volume (mm^3) + axis-aligned bbox of a binary STL.

    The signed-tetrahedron sum handles the hollow captive-core shells
    correctly (inner cavity surfaces subtract).
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


# ---- OpenSCAD ---------------------------------------------------------------
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
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


def render_specimen(part: str, out: Path, params: dict, scale: float) -> None:
    """Render one specimen part from the canonical t3-prism.scad at a FIXED
    uniform scale (no mass solve): R, H, strut, cable and joint diameters all
    scale; the sensor housings stay at absolute size (the SCAD never scales
    them). Scaffold pillars stay off, supports are manual-painted."""
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


# ---- Designs ---------------------------------------------------------------
def load_solved_designs(csv_path: Path) -> list[dict]:
    """Read a constant-printed-mass suggestions CSV (one row per article).

    The uniform scale is derived from the print columns (H_print_mm / H_mm,
    the largest dimension, carries the most relative precision; the CSV's own
    ``scale`` column is rounded to 4 decimals) and then cross-checked against
    every print column, so a CSV whose projection disagrees with this script
    refuses to render instead of quietly printing the wrong geometry.
    """
    with csv_path.open() as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f"{csv_path}: no rows")
    needed = [*PARAM_NAMES, "trial_index", "scale", "H_print_mm",
              "strut_infill_pct", "tpu_infill_pct", "printed_mass_g"]
    missing = [k for k in needed if k not in rows[0]]
    if missing:
        raise SystemExit(f"{csv_path} is missing column(s) {missing}; this "
                         f"script needs a solved constant-printed-mass table "
                         f"(t3-prism-bo-suggestions-round3.csv or later)")
    designs = []
    for row in rows:
        params = {k: float(row[k]) for k in PARAM_NAMES}
        s = float(row["H_print_mm"]) / params["H_mm"]
        checks = {
            "R_print_mm": params["R_mm"] * s,
            "H_print_mm": params["H_mm"] * s,
            "strut_d_print_mm": params["strut_d_mm"] * s,
            "cable_d_print_mm": params["cable_d_mm"] * s,
            "joint_d_print_mm": JOINT_D_BASE * s,
        }
        for col, want in checks.items():
            got = float(row[col])
            if abs(got - want) > PRINT_COLUMN_TOL_MM:
                raise SystemExit(
                    f"{csv_path} trial {row['trial_index']}: {col} = {got} "
                    f"but the derived scale {s:.6f} gives {want:.4f}; the "
                    f"CSV's projection and this script disagree, refusing to "
                    f"render")
        if abs(s - float(row["scale"])) > 5e-4:
            raise SystemExit(
                f"{csv_path} trial {row['trial_index']}: derived scale "
                f"{s:.6f} is not the CSV's scale column {row['scale']}")
        designs.append({
            "label": str(int(float(row["trial_index"]))),
            "params": params,
            "scale": s,
            "strut_infill_pct": float(row["strut_infill_pct"]),
            "tpu_infill_pct": float(row["tpu_infill_pct"]),
            "target_g": float(row["printed_mass_g"]),
            "row": row,
        })
    return designs


# ---- Rendered-volume mass verification --------------------------------------
def printed_grams_from_rendered(model, params: dict, scale: float,
                                pla_g: float, tpu_g: float,
                                strut_infill_pct: float,
                                tpu_infill_pct: float) -> float:
    """Push rendered solid grams through the calibrated wall+infill model.

    Mirrors ``MassModel.printed_mass_g`` but with rendered solid masses in
    place of the analytic ones. The rendered cables STL fuses tendons and
    captive cores into one body, so the cores' share (the only TPU body that
    responds to infill) is taken from the analytic split, where the material
    correction factor cancels in the ratio.
    """
    _, v_cable, v_core = analytic_body_volumes_split(params)
    core_share = v_core / (v_cable + v_core)
    g_core = model.tpu_core_factor(captive_core_od(params) * scale,
                                   tpu_infill_pct)
    frac = model.pla_solid_fraction(params["strut_d_mm"] * scale,
                                    strut_infill_pct)
    return (pla_g * frac
            + model.f_tpu * tpu_g * ((1.0 - core_share) + core_share * g_core))


# ---- Plate layout (adapted from bo/t3_prism_sobol_batch.py) -----------------
def plan_plate_layout(footprints: list[float]) -> dict:
    """Variable-cell rows x cols layout: sort footprints descending, fill the
    grid column-major so the largest specimens share a column and a row, size
    each column/row to its largest occupant, 6 mm air gap, pack centred in
    the usable (non-prime-tower) area."""
    air_gap = 6.0
    n = len(footprints)
    rows = math.ceil(math.sqrt(n))
    cols = math.ceil(n / rows)
    order = sorted(range(n), key=lambda i: -footprints[i])
    cell_of: dict[int, tuple[int, int]] = {}
    for rank, i in enumerate(order):
        cell_of[i] = (rank % rows, rank // rows)
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
        print(f"WARNING: packed grid {total_w:.1f}x{total_h:.1f} mm exceeds "
              f"usable plate {usable_x:.1f}x{usable_y:.1f} mm", file=sys.stderr)
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
    return {"rows": rows, "cols": cols, "air_gap": air_gap,
            "col_widths": col_w, "row_heights": row_h,
            "total_w": total_w, "total_h": total_h, "centres": centres}


def write_preview_scad(path: Path, stl_names: list[str], rows: int,
                       cols: int) -> None:
    """Preview wrapper importing the plate-positioned per-specimen STLs."""
    chunks: list[str] = [
        "// AUTO-GENERATED by bo/t3_prism_printed_mass_plate.py. Do not hand-edit.\n"
        "// Preview wrapper for a constant-printed-mass batch: imports the\n"
        "// per-specimen STLs rendered from cad/t3-prism/t3-prism.scad at the\n"
        "// scale solved by bo/t3_prism_bo_campaign.py (constant printed grams).\n"
        f"// Plate: {PLATE_X:.0f} x {PLATE_Y:.0f} mm (Bambu Lab H2D). "
        f"Grid: {rows} x {cols}.\n"
        'part = "all";  // "all" | "struts" | "cables"\n\n'
    ]
    for name in stl_names:
        part = "struts" if name.endswith("-struts.stl") else "cables"
        chunks.append(
            f'if (part == "all" || part == "{part}")\n'
            f'    import("per-specimen-stls/{name}");\n'
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


# ---- Bambu H2D multi-material 3mf assembly ----------------------------------
# Same AppImage + flatten/patch pipeline as bo/t3_prism_sobol_batch.py; the
# profiles are the ones the lab actually prints with (verified against the
# printed round-2 plate's project_settings.config), with the round-3 recipe's
# TPU preset swap already applied.
BAMBU_VERSION = "v02.06.00.51"
BAMBU_URL = (
    "https://github.com/bambulab/BambuStudio/releases/download/"
    f"{BAMBU_VERSION}/BambuStudio_ubuntu-24.04-{BAMBU_VERSION}"
    "-20260417160415.AppImage"
)
SCRATCH = Path("/tmp/t3-prism")
BAMBU_APPIMAGE = SCRATCH / "bambu.AppImage"
BBL_ROOT = SCRATCH / "squashfs-root" / "resources" / "profiles" / "BBL"

MACHINE_LEAF = "Bambu Lab H2D 0.6 nozzle"
PROCESS_LEAF = "0.30mm Standard @BBL H2D 0.6 nozzle"
PLA_LEAF = "Bambu PLA Basic @BBL H2D 0.6 nozzle"
# The recipe's required preset swap: NOT the "0.4 nozzle" variant, whose
# temperature window caps at 240 C, below the batch's TPU setting.
TPU_LEAF = "Bambu TPU 85A @BBL H2D"


def _ensure_bambu() -> None:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    if not BAMBU_APPIMAGE.exists():
        print(f"==> Fetching BambuStudio {BAMBU_VERSION} AppImage")
        subprocess.run(["curl", "-sLo", str(BAMBU_APPIMAGE), BAMBU_URL],
                       check=True)
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


def _patch_filament(profile: Path, temp_c: float, flow_mm3_s: float) -> None:
    """Write the batch's nozzle temperature and max volumetric speed into a
    flattened filament config (the two per-filament settings the round-3
    recipe fixes batch-wide). Values are per-extruder string lists."""
    d = json.loads(profile.read_text())
    n = max(len(d.get("nozzle_temperature", ["0"])), 1)
    d["nozzle_temperature"] = [f"{temp_c:g}"] * n
    d["nozzle_temperature_initial_layer"] = [f"{temp_c:g}"] * n
    d["filament_max_volumetric_speed"] = [f"{flow_mm3_s:g}"] * n
    profile.write_text(json.dumps(d, indent=2))


def _split_assembled_into_objects(
    proj_3mf: Path, pairs: list[tuple[str, str]], object_names: list[str],
    part_settings: dict[str, dict[str, str]] | None = None,
) -> None:
    """Split the single composite object emitted by ``--assemble`` into one
    two-part object per specimen (struts on extruder 1, cables on extruder 2),
    named per Ax trial, each part carrying its per-part config overrides
    (sparse infill density). Adapted from bo/t3_prism_sobol_batch.py; the
    mesh data is untouched, only the grouping changes."""
    import re
    import uuid
    import zipfile

    MODEL_PATH = "3D/3dmodel.model"
    CFG_PATH = "Metadata/model_settings.config"
    part_settings = part_settings or {}

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

    # ---- Patch model_settings.config first (need part-name -> id mapping) ----
    cfg = contents[CFG_PATH].decode()
    cfg_part_re = re.compile(r'<part id="(\d+)"[^>]*>(.*?)</part>', re.DOTALL)
    cfg_name_re = re.compile(r'<metadata key="name" value="([^"]+)"\s*/>')
    cfg_object_re = re.compile(
        r'(<object id="(\d+)"[^>]*>)(.*?)(</object>)', re.DOTALL)
    cfg_plate_re = re.compile(r'(<plate>)(.*?)(</plate>)', re.DOTALL)

    obj_match = cfg_object_re.search(cfg)
    if obj_match is None:
        raise RuntimeError(f"{proj_3mf}: no <object> in {CFG_PATH}")
    obj_open, obj_id_str, obj_body, obj_close = obj_match.groups()
    composite_obj_id = int(obj_id_str)

    parts: list[tuple[int, str, str]] = []
    for m in cfg_part_re.finditer(obj_body):
        part_id = int(m.group(1))
        part_xml = m.group(0)
        name_match = cfg_name_re.search(m.group(2))
        if name_match is None:
            raise RuntimeError(f"{proj_3mf}: <part id={part_id}> missing name")
        parts.append((part_id, name_match.group(1), part_xml))

    spec_to_parts: dict[int, dict[int, tuple[int, str, str]]] = {}
    for part_id, name, part_xml in parts:
        if name not in name_to_spec:
            raise RuntimeError(
                f"{proj_3mf}: <part name={name!r}> not in pairs mapping")
        spec_idx, ext_id = name_to_spec[name]
        spec_to_parts.setdefault(spec_idx, {})[ext_id] = (part_id, name, part_xml)

    new_composite_ids: list[int] = []
    cfg_new_objects: list[str] = []
    extruder_re = re.compile(r'(<metadata key="extruder" value=")\d+(")')
    for spec_idx in sorted(spec_to_parts):
        new_obj_id = composite_obj_id + spec_idx
        new_composite_ids.append(new_obj_id)
        chunks = [f'  <object id="{new_obj_id}">\n']
        chunks.append(
            f'    <metadata key="name" value="{object_names[spec_idx]}"/>\n')
        for ext_id in sorted(spec_to_parts[spec_idx]):
            _, part_name, part_xml = spec_to_parts[spec_idx][ext_id]
            if extruder_re.search(part_xml):
                part_xml = extruder_re.sub(rf"\g<1>{ext_id}\g<2>", part_xml)
            else:
                part_xml = part_xml.replace(
                    "</part>",
                    f'      <metadata key="extruder" value="{ext_id}"/>\n'
                    f'    </part>',
                )
            extra = "".join(
                f'      <metadata key="{k}" value="{v}"/>\n'
                for k, v in part_settings.get(part_name, {}).items())
            if extra:
                part_xml = part_xml.replace("</part>", extra + "    </part>")
            chunks.append("    " + part_xml + "\n")
        chunks.append("  </object>")
        cfg_new_objects.append("".join(chunks))

    new_cfg = (cfg[:obj_match.start()] + "\n".join(cfg_new_objects)
               + cfg[obj_match.end():])

    plate_match = cfg_plate_re.search(new_cfg)
    if plate_match is None:
        raise RuntimeError(f"{proj_3mf}: no <plate> in {CFG_PATH}")
    plate_open, plate_body, plate_close = plate_match.groups()
    plate_header_match = re.search(
        r'^(.*?)(<model_instance>.*?</model_instance>\s*)', plate_body,
        re.DOTALL)
    if plate_header_match is None:
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
    new_plate = (plate_open + plate_header + "".join(new_instances)
                 + "  " + plate_close)
    new_cfg = (new_cfg[:plate_match.start()] + new_plate
               + new_cfg[plate_match.end():])
    contents[CFG_PATH] = new_cfg.encode()

    # ---- Patch 3D/3dmodel.model ---------------------------------------------
    model_xml = contents[MODEL_PATH].decode()
    model_obj_re = re.compile(
        r'(<object id="(\d+)"[^>]*type="model"[^>]*>)(.*?)(</object>)',
        re.DOTALL)
    model_build_re = re.compile(r'(<build[^>]*>)(.*?)(</build>)', re.DOTALL)
    model_item_re = re.compile(r'<item\b[^>]*?objectid="\d+"[^>]*?/>')

    obj_match2 = model_obj_re.search(model_xml)
    if obj_match2 is None:
        raise RuntimeError(f"{proj_3mf}: no <object type=model> in {MODEL_PATH}")
    _, _, obj_body2, _ = obj_match2.groups()
    component_tags = re.findall(r'<component\b[^>]*?/>', obj_body2)
    if len(component_tags) != len(parts):
        raise RuntimeError(
            f"{proj_3mf}: {MODEL_PATH} has {len(component_tags)} components "
            f"but {CFG_PATH} has {len(parts)} parts")
    obj_id_to_tag: dict[str, str] = {}
    for tag in component_tags:
        m = re.search(r'objectid="(\d+)"', tag)
        if m:
            obj_id_to_tag[m.group(1)] = tag

    new_model_objects: list[str] = []
    for spec_idx in sorted(spec_to_parts):
        new_obj_id = composite_obj_id + spec_idx
        comp_tags: list[str] = []
        for ext_id in sorted(spec_to_parts[spec_idx]):
            part_id, _, _ = spec_to_parts[spec_idx][ext_id]
            tag = obj_id_to_tag.get(str(part_id))
            if tag is None:
                raise RuntimeError(
                    f"{proj_3mf}: no <component objectid={part_id}> in "
                    f"{MODEL_PATH}")
            comp_tags.append("    " + tag)
        new_model_objects.append(
            f'  <object id="{new_obj_id}" p:UUID="{uuid.uuid4()}" type="model">\n'
            f'   <components>\n'
            + "\n".join(comp_tags) + "\n"
            f'   </components>\n'
            f'  </object>'
        )
    new_model_xml = (model_xml[:obj_match2.start()]
                     + "\n".join(new_model_objects)
                     + model_xml[obj_match2.end():])

    build_match = model_build_re.search(new_model_xml)
    if build_match is None:
        raise RuntimeError(f"{proj_3mf}: no <build> in {MODEL_PATH}")
    build_open, build_body, build_close = build_match.groups()
    existing_item_match = model_item_re.search(build_body)
    if existing_item_match is None:
        raise RuntimeError(f"{proj_3mf}: no <item> in <build>")
    existing_item = existing_item_match.group(0)
    transform_match = re.search(r'transform="([^"]*)"', existing_item)
    printable_match = re.search(r'printable="([^"]*)"', existing_item)
    transform_attr = (f' transform="{transform_match.group(1)}"'
                      if transform_match else "")
    printable_attr = (f' printable="{printable_match.group(1)}"'
                      if printable_match else ' printable="1"')
    new_items: list[str] = []
    for new_obj_id in new_composite_ids:
        new_items.append(
            f'  <item objectid="{new_obj_id}" p:UUID="{uuid.uuid4()}"'
            f"{transform_attr}{printable_attr}/>")
    new_build = build_open + "\n" + "\n".join(new_items) + "\n " + build_close
    new_model_xml = (new_model_xml[:build_match.start()] + new_build
                     + new_model_xml[build_match.end():])
    contents[MODEL_PATH] = new_model_xml.encode()

    with zipfile.ZipFile(proj_3mf, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in infos:
            zout.writestr(info, contents[info.filename])


def build_mm_3mf(pairs: list[tuple[Path, Path]], object_names: list[str],
                 out_3mf: Path, filament_settings: dict,
                 part_settings: dict[str, dict[str, str]]) -> None:
    """Assemble per-specimen (struts, cables) STL pairs into a Bambu H2D MM
    project with the batch's filament settings and per-part infill overrides.

    Each pair becomes its own composite object (struts -> extruder 1 / PLA,
    cables -> extruder 2 / TPU) so a specimen moves as a unit in Bambu
    Studio. Supports stay off; they are painted on manually.
    """
    _ensure_bambu()
    for leaf, kind in ((MACHINE_LEAF, "machine"), (PROCESS_LEAF, "process"),
                       (PLA_LEAF, "filament"), (TPU_LEAF, "filament")):
        if not (BBL_ROOT / kind / f"{leaf}.json").exists():
            raise SystemExit(
                f"Bundled BBL profiles have no {kind} preset {leaf!r}; "
                f"available: "
                + ", ".join(sorted(p.stem for p in (BBL_ROOT / kind).glob("*H2D*")))
            )
    work = SCRATCH / "bo_round3_mm"
    work.mkdir(parents=True, exist_ok=True)
    m = work / "machine_flat.json"
    p = work / "process_flat.json"
    f1 = work / "filament1_flat.json"
    f2 = work / "filament2_flat.json"
    _flatten("machine", MACHINE_LEAF, m)
    _flatten("process", PROCESS_LEAF, p)
    _flatten("filament", PLA_LEAF, f1)
    _flatten("filament", TPU_LEAF, f2)
    _patch_bed(m)
    _patch_filament(f1, filament_settings["pla_nozzle_temp_C"],
                    filament_settings["pla_flow_mm3_s"])
    _patch_filament(f2, filament_settings["tpu_nozzle_temp_C"],
                    filament_settings["tpu_flow_mm3_s"])

    proj_3mf = out_3mf.name
    proj_outdir = work / "proj"
    if proj_outdir.exists():
        shutil.rmtree(proj_outdir)
    proj_outdir.mkdir(parents=True)

    stl_args: list[str] = []
    pairs_names: list[tuple[str, str]] = []
    name_to_ext: dict[str, str] = {}
    for struts_stl, cables_stl in pairs:
        stl_args.extend([str(struts_stl), str(cables_stl)])
        pairs_names.append((struts_stl.name, cables_stl.name))
        name_to_ext[struts_stl.name] = "1"
        name_to_ext[cables_stl.name] = "2"

    print(f"==> BambuStudio CLI --assemble -> {proj_3mf} "
          f"({len(pairs)} specimens x 2 parts each)")
    env = {**__import__("os").environ,
           "LIBGL_ALWAYS_SOFTWARE": "1", "GALLIUM_DRIVER": "llvmpipe"}
    subprocess.run(
        ["xvfb-run", "-a", "-s", "-screen 0 1280x1024x24", str(BAMBU_APPIMAGE),
         "--assemble",
         "--load-settings", f"{m};{p}",
         "--load-filaments", f"{f1};{f2}",
         "--export-3mf", proj_3mf,
         "--outputdir", str(proj_outdir),
         *stl_args],
        check=True, env=env,
    )

    print("==> Patch model_settings.config: struts -> extruder 1 (PLA), "
          "cables -> extruder 2 (TPU)")
    pair_args = [f"{name}={ext}" for name, ext in name_to_ext.items()]
    subprocess.run(
        ["python3", str(T3_PRISM_DIR / "patch_mm_extruder.py"),
         str(proj_outdir / proj_3mf), *pair_args],
        check=True,
    )

    print(f"==> Split assembled composite -> {len(pairs)} per-trial objects "
          f"with per-part sparse infill overrides")
    _split_assembled_into_objects(proj_outdir / proj_3mf, pairs_names,
                                  object_names, part_settings)

    out_3mf.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(proj_outdir / proj_3mf, out_3mf)


# ---- Main -------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--designs-csv", type=Path, default=DEFAULT_DESIGNS,
                        help="solved constant-printed-mass suggestions CSV "
                             f"(default {DEFAULT_DESIGNS.name})")
    parser.add_argument("--out-prefix", default=DEFAULT_PREFIX,
                        help=f"basename for emitted artifacts (default "
                             f"{DEFAULT_PREFIX})")
    parser.add_argument("--jobs", type=int, default=4,
                        help="parallel OpenSCAD render workers (default 4)")
    parser.add_argument("--skip-mm-3mf", action="store_true",
                        help="skip the BambuStudio CLI MM project assembly")
    args = parser.parse_args(argv)

    prefix = args.out_prefix
    designs = load_solved_designs(args.designs_csv)
    print(f"==> {len(designs)} articles from {args.designs_csv.name}, "
          f"target printed mass "
          f"{designs[0]['target_g']:.2f} g "
          f"(scales {min(d['scale'] for d in designs):.4f} to "
          f"{max(d['scale'] for d in designs):.4f}; no mass re-solve here)")

    if not shutil.which("openscad"):
        print("openscad not found; install with "
              "`sudo apt-get install -y openscad xvfb`.", file=sys.stderr)
        return 2

    model = calibrate()
    print(f"==> Printed-mass model: infill {model.infill * 100:.1f} %, wall "
          f"{model.wall_mm:.2f} mm, f_TPU {model.f_tpu:.3f} "
          f"(residual sd {model.resid_sd_g:.3f} g over {model.n_articles} "
          f"articles)")

    solve_dir = SCRATCH / "printed-mass-plate"
    solve_dir.mkdir(parents=True, exist_ok=True)

    def render_one(i_design):
        i, d = i_design
        struts = solve_dir / f"{prefix}-t{d['label']}-struts.stl"
        cables = solve_dir / f"{prefix}-t{d['label']}-cables.stl"
        print(f"==> trial {d['label']}: render at scale {d['scale']:.6f}")
        render_specimen("struts", struts, d["params"], d["scale"])
        render_specimen("cables", cables, d["params"], d["scale"])
        vs, smin, smax = stl_volume_bbox(struts)
        vc, cmin, cmax = stl_volume_bbox(cables)
        bb = ([min(a, b) for a, b in zip(smin, cmin)],
              [max(a, b) for a, b in zip(smax, cmax)])
        return {"struts_stl": struts, "cables_stl": cables,
                "pla_g": RHO_PLA * vs, "tpu_g": RHO_TPU * vc,
                "bbox_min": bb[0], "bbox_max": bb[1]}

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(render_one, enumerate(designs)))

    # ---- Rendered-volume verification against the printed-mass target -------
    worst = 0.0
    for d, res in zip(designs, results):
        res["printed_g_est"] = printed_grams_from_rendered(
            model, d["params"], d["scale"], res["pla_g"], res["tpu_g"],
            d["strut_infill_pct"], d["tpu_infill_pct"])
        res["printed_g_delta"] = res["printed_g_est"] - d["target_g"]
        worst = max(worst, abs(res["printed_g_delta"]))
        print(f"    trial {d['label']}: rendered solid "
              f"{res['pla_g'] + res['tpu_g']:.2f} g "
              f"(PLA {res['pla_g']:.2f} + TPU {res['tpu_g']:.2f}), "
              f"printed est {res['printed_g_est']:.2f} g "
              f"({res['printed_g_delta']:+.2f} g vs target)")
    print(f"==> Worst |printed est - target| = {worst:.2f} g "
          f"(mass-model residual sd {model.resid_sd_g:.2f} g, print-to-print "
          f"scatter 0.457 g)")
    if worst > 1.0:
        print("ERROR: rendered geometry misses the printed-mass target by "
              "more than 1 g somewhere; not writing outputs.", file=sys.stderr)
        return 1

    # ---- Plate layout from measured footprints -------------------------------
    footprints = [
        2.0 * max(abs(v) for v in (res["bbox_min"][0], res["bbox_max"][0],
                                   res["bbox_min"][1], res["bbox_max"][1]))
        for res in results]
    layout = plan_plate_layout(footprints)

    per_spec_dir = BO_DIR / "per-specimen-stls"
    per_spec_dir.mkdir(exist_ok=True)
    pairs: list[tuple[Path, Path]] = []
    for d, res, (cx, cy) in zip(designs, results, layout["centres"]):
        cz = -res["bbox_min"][2]  # lowest feature (key-seat underside) -> bed
        spec_struts = per_spec_dir / res["struts_stl"].name
        spec_cables = per_spec_dir / res["cables_stl"].name
        stl_translate(res["struts_stl"], spec_struts, cx, cy, cz)
        stl_translate(res["cables_stl"], spec_cables, cx, cy, cz)
        pairs.append((spec_struts, spec_cables))
        res["plate_x_mm"], res["plate_y_mm"] = cx, cy
        res["footprint_meas_mm"] = 2.0 * max(
            abs(v) for v in (res["bbox_min"][0], res["bbox_max"][0],
                             res["bbox_min"][1], res["bbox_max"][1]))

    # ---- Manifest ------------------------------------------------------------
    manifest_path = BO_DIR / f"{prefix}-designs.csv"
    carried = ["R_print_mm", "H_print_mm", "strut_d_print_mm",
               "cable_d_print_mm", "joint_d_print_mm", "core_d_print_mm",
               "shell_d_print_mm", "footprint_d_mm", "envelope_cm3",
               "envelope_ok", "cable_bridge_ok", "pla_nozzle_temp_C",
               "pla_flow_mm3_s", "tpu_nozzle_temp_C", "tpu_flow_mm3_s"]
    with manifest_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["specimen", "trial_index", "best_predicted", *PARAM_NAMES,
                    "strut_infill_pct", "tpu_infill_pct", "scale",
                    *carried, "pla_solid_g", "tpu_solid_g", "solid_g",
                    "printed_g_est", "target_printed_g", "printed_g_delta",
                    "footprint_meas_mm", "plate_x_mm", "plate_y_mm",
                    "struts_stl", "cables_stl"])
        for i, (d, res) in enumerate(zip(designs, results)):
            w.writerow([
                i, d["label"], d["row"].get("best_predicted", ""),
                *(f"{d['params'][k]:.4f}" for k in PARAM_NAMES),
                f"{d['strut_infill_pct']:.0f}", f"{d['tpu_infill_pct']:.0f}",
                f"{d['scale']:.6f}",
                *(d["row"].get(c, "") for c in carried),
                f"{res['pla_g']:.2f}", f"{res['tpu_g']:.2f}",
                f"{res['pla_g'] + res['tpu_g']:.2f}",
                f"{res['printed_g_est']:.2f}", f"{d['target_g']:.2f}",
                f"{res['printed_g_delta']:+.2f}",
                f"{res['footprint_meas_mm']:.1f}",
                f"{res['plate_x_mm']:.1f}", f"{res['plate_y_mm']:.1f}",
                f"per-specimen-stls/{pairs[i][0].name}",
                f"per-specimen-stls/{pairs[i][1].name}",
            ])

    json_path = BO_DIR / f"{prefix}-plate.json"
    json_path.write_text(json.dumps({
        "designs_source": str(args.designs_csv.name),
        "projection": "constant printed mass, solved by "
                      "bo/t3_prism_bo_campaign.py via bo/t3_prism_mass_model.py"
                      " (rendered at the solved scale; no re-solve here)",
        "target_printed_mass_g": designs[0]["target_g"],
        "scad": "cad/t3-prism/t3-prism.scad (byte-identical copy of "
                "copilot/get-bambu-sliced-print-t3-prism @ dbb5011)",
        "mass_model": {"infill": model.infill, "wall_mm": model.wall_mm,
                       "f_tpu": model.f_tpu, "k_pla": model.k_pla,
                       "k_tpu": model.k_tpu,
                       "resid_sd_g": model.resid_sd_g},
        "grid": {"rows": layout["rows"], "cols": layout["cols"],
                 "air_gap_mm": layout["air_gap"],
                 "col_widths_mm": layout["col_widths"],
                 "row_heights_mm": layout["row_heights"],
                 "total_w_mm": layout["total_w"],
                 "total_h_mm": layout["total_h"]},
        "plate": {"x_mm": PLATE_X, "y_mm": PLATE_Y, "margin_mm": PLATE_MARGIN,
                  "prime_tower_reserve_x_mm": PRIME_TOWER_RESERVE_X},
        "profiles": {"machine": MACHINE_LEAF, "process": PROCESS_LEAF,
                     "filament_1_pla": PLA_LEAF, "filament_2_tpu": TPU_LEAF},
        "specimens": [
            {"idx": i, "trial_index": int(d["label"]), **d["params"],
             "strut_infill_pct": d["strut_infill_pct"],
             "tpu_infill_pct": d["tpu_infill_pct"],
             "scale": d["scale"],
             "pla_solid_g": res["pla_g"], "tpu_solid_g": res["tpu_g"],
             "printed_g_est": res["printed_g_est"],
             "plate_x_mm": res["plate_x_mm"], "plate_y_mm": res["plate_y_mm"]}
            for i, (d, res) in enumerate(zip(designs, results))
        ],
    }, indent=2))

    # ---- Preview wrapper + PNGs ----------------------------------------------
    scad_path = BO_DIR / f"{prefix}.scad"
    write_preview_scad(scad_path,
                       [name for pair in pairs for name in
                        (pair[0].name, pair[1].name)],
                       layout["rows"], layout["cols"])
    plate_png = BO_DIR / f"{prefix}-plate.png"
    iso_png = BO_DIR / f"{prefix}-iso.png"
    cam_top = (f"{PLATE_X/2:.1f},{PLATE_Y/2:.1f},0,0,0,0,"
               f"{max(PLATE_X, PLATE_Y) * 1.4:.1f}")
    cam_iso = (f"{PLATE_X/2:.1f},{PLATE_Y/2:.1f},0,55,0,25,"
               f"{max(PLATE_X, PLATE_Y) * 1.6:.1f}")
    print(f"==> OpenSCAD render -> {plate_png.name} (top-down plate view)")
    run_openscad(scad_path, plate_png, camera=cam_top, image_size="1200,1100",
                 viewall=True)
    print(f"==> OpenSCAD render -> {iso_png.name} (iso preview)")
    run_openscad(scad_path, iso_png, camera=cam_iso, image_size="1200,900",
                 viewall=True)

    # ---- MM project ----------------------------------------------------------
    mm_3mf_path = BO_DIR / "slices" / f"{prefix}.H2D-MM-PLAstruts-TPUcables.3mf"
    if not args.skip_mm_3mf:
        first = designs[0]["row"]
        filament_settings = {
            "pla_nozzle_temp_C": float(first["pla_nozzle_temp_C"]),
            "pla_flow_mm3_s": float(first["pla_flow_mm3_s"]),
            "tpu_nozzle_temp_C": float(first["tpu_nozzle_temp_C"]),
            "tpu_flow_mm3_s": float(first["tpu_flow_mm3_s"]),
        }
        part_settings = {}
        for d, (spec_struts, spec_cables) in zip(designs, pairs):
            part_settings[spec_struts.name] = {
                "sparse_infill_density": f"{d['strut_infill_pct']:.0f}%"}
            part_settings[spec_cables.name] = {
                "sparse_infill_density": f"{d['tpu_infill_pct']:.0f}%"}
        object_names = [f"Trial {d['label']}" for d in designs]
        build_mm_3mf(pairs, object_names, mm_3mf_path, filament_settings,
                     part_settings)

    print("Done.")
    print(f"  Manifest      : {manifest_path}")
    print(f"  Plate JSON    : {json_path}")
    print(f"  Per-spec STLs : {per_spec_dir}/{prefix}-tNN-*.stl")
    print(f"  Plate PNG     : {plate_png}")
    print(f"  Iso PNG       : {iso_png}")
    if not args.skip_mm_3mf:
        print(f"  MM project    : {mm_3mf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
