#!/usr/bin/env python3
"""Build a multi-material PLA(struts+pillars) + TPU(cables) 3MF for the Bambu
Studio CLI.

Takes an existing PLA-struts + TPU-cables template 3MF (such as the one in
``vertical-cloud-lab/BambuStudio`` PR #2's ``slice-inputs`` bundle) and appends
the ``generate_support_pillars.py --stl`` output as a third PLA-assigned part
so the manually-baked narrowing pillars print on extruder 1 alongside the
struts.

Also fixes two H2D-Pro authoring quirks of the upstream template that the
patched CLI (vertical-cloud-lab/BambuStudio PR #2) still needs in order to
slice on a stock H2D 0.4-nozzle machine profile:

* ``nozzle_volume_type`` is forced to ``["Standard", "Hybrid"]`` so the TPU
  filament resolves to a valid extruder/nozzle combo on the H2D machine
  profile. ``"Hybrid"`` is the BambuStudio internal enum name for the
  user-facing GUI label "Direct Drive TPU High Flow"; without it the H2D
  profile falls through to ``Unknown`` on extruder 2 and the slicer aborts
  with "No valid nozzle found. Please check nozzle count.".
* ``flush_volumes_matrix`` and ``flush_volumes_vector`` are resized down from
  the 4-filament (16 / 8 entries) defaults to the 2-filament case (n*n = 4
  entries each) the slicer validator now strictly checks.

Usage:
    python build_mm_pillars_3mf.py \
        --template t3-prism.H2D-MM-PLAstruts-TPUcables.single.3mf \
        --pillars-stl t3-prism-pr35-pillars.stl \
        --out t3-prism.H2D-MM-PLAstruts-TPUcables-PLApillars.3mf
"""
from __future__ import annotations

import argparse
import json
import shutil
import struct
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD_NS = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
BBS_NS = "http://schemas.bambulab.com/package/2021"
ET.register_namespace("", CORE_NS)
ET.register_namespace("p", PROD_NS)
ET.register_namespace("BambuStudio", BBS_NS)


def read_stl(path: Path):
    data = path.read_bytes()
    n = struct.unpack_from("<I", data, 80)[0]
    verts: list[tuple[float, float, float]] = []
    tris: list[tuple[int, int, int]] = []
    off = 84
    for _ in range(n):
        # skip 12-byte normal
        base = off + 12
        v0 = struct.unpack_from("<fff", data, base)
        v1 = struct.unpack_from("<fff", data, base + 12)
        v2 = struct.unpack_from("<fff", data, base + 24)
        i = len(verts)
        verts.extend([v0, v1, v2])
        tris.append((i, i + 1, i + 2))
        off += 50
    return verts, tris


def build_object_xml(object_id: int, uuid: str, verts, tris) -> str:
    lines = [
        f'  <object id="{object_id}" p:UUID="{uuid}" type="model">',
        "   <mesh>",
        "    <vertices>",
    ]
    for x, y, z in verts:
        lines.append(f'     <vertex x="{x:.7g}" y="{y:.7g}" z="{z:.7g}"/>')
    lines.append("    </vertices>")
    lines.append("    <triangles>")
    for a, b, c in tris:
        lines.append(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>')
    lines.append("    </triangles>")
    lines.append("   </mesh>")
    lines.append("  </object>")
    return "\n".join(lines) + "\n"


def patch_object_1_model(text: str, object_xml: str) -> str:
    needle = " </resources>"
    idx = text.rindex(needle)
    return text[:idx] + object_xml + text[idx:]


def patch_3dmodel(text: str, object_id: int, component_uuid: str, tx: float, ty: float, tz: float) -> str:
    component = (
        f'    <component p:path="/3D/Objects/object_1.model" objectid="{object_id}"'
        f' p:UUID="{component_uuid}" transform="1 0 0 0 1 0 0 0 1 {tx:.7g} {ty:.7g} {tz:.7g}"/>\n'
    )
    needle = "   </components>"
    idx = text.index(needle)
    return text[:idx] + component + text[idx:]


def patch_model_settings(text: str, object_id: int, name: str, tx: float, ty: float, tz: float, extruder: int, face_count: int) -> str:
    matrix = f"1 0 0 {tx} 0 1 0 {ty} 0 0 1 {tz} 0 0 0 1"
    part = (
        f'    <part id="{object_id}" subtype="normal_part">\n'
        f'      <metadata key="name" value="{name}"/>\n'
        f'      <metadata key="matrix" value="{matrix}"/>\n'
        f'      <metadata key="source_file" value="{name}"/>\n'
        f'      <metadata key="source_object_id" value="0"/>\n'
        f'      <metadata key="source_volume_id" value="0"/>\n'
        f'      <metadata key="source_offset_x" value="{tx}"/>\n'
        f'      <metadata key="source_offset_y" value="{ty}"/>\n'
        f'      <metadata key="source_offset_z" value="{tz}"/>\n'
        f'      <metadata key="extruder" value="{extruder}"/>\n'
        f'      <mesh_stat face_count="{face_count}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n'
        f"    </part>\n"
    )
    needle = "  </object>"
    idx = text.index(needle)
    return text[:idx] + part + text[idx:]


def patch_project_settings(path: Path, n_filaments: int) -> None:
    cfg = json.loads(path.read_text())
    # Force TPU-capable variant on extruder 2 (the BambuStudio internal enum
    # name for "Direct Drive TPU High Flow" is "Hybrid"; the user-facing label
    # in the Studio GUI is "TPU High Flow"). Without this the H2D machine
    # profile falls through to "Unknown" for extruder 2 and the slicer aborts
    # with "No valid nozzle found. Please check nozzle count.".
    cfg["nozzle_volume_type"] = ["Standard", "Hybrid"]
    # Resize flush matrices to n*n for the actual filament count
    n = n_filaments
    matrix = []
    for i in range(n):
        for j in range(n):
            matrix.append("0" if i == j else "280")
    cfg["flush_volumes_matrix"] = matrix
    cfg["flush_volumes_vector"] = ["140"] * (n * n)
    path.write_text(json.dumps(cfg, indent=4))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--template", required=True, type=Path,
                    help="PLA-struts + TPU-cables template 3MF (e.g. the slice-inputs bundle from vertical-cloud-lab/BambuStudio PR #2).")
    ap.add_argument("--pillars-stl", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--pillar-extruder", type=int, default=1,
                    help="Extruder index for the pillars (1 = first loaded filament, normally PLA).")
    ap.add_argument("--pillar-tx", type=float, default=175.0)
    ap.add_argument("--pillar-ty", type=float, default=160.0)
    ap.add_argument("--pillar-tz", type=float, default=0.0,
                    help="Z translation in mm applied to the pillars component. Pillars produced by generate_support_pillars.py already have z=0 at the bed, so the default (0) is correct.")
    args = ap.parse_args()

    work = Path(tempfile.mkdtemp(prefix="mm3mf-"))
    try:
        with zipfile.ZipFile(args.template) as zf:
            zf.extractall(work)

        verts, tris = read_stl(args.pillars_stl)
        new_uuid_object = "00010002-81cb-4c03-9d28-80fed5dfa1dc"
        new_uuid_component = "00010002-b206-40ff-9872-83e8017abed1"
        new_object_id = 3

        obj_model = work / "3D" / "Objects" / "object_1.model"
        obj_model.write_text(patch_object_1_model(
            obj_model.read_text(),
            build_object_xml(new_object_id, new_uuid_object, verts, tris),
        ))

        root_model = work / "3D" / "3dmodel.model"
        root_model.write_text(patch_3dmodel(
            root_model.read_text(),
            object_id=new_object_id,
            component_uuid=new_uuid_component,
            tx=args.pillar_tx, ty=args.pillar_ty, tz=args.pillar_tz,
        ))

        ms = work / "Metadata" / "model_settings.config"
        ms.write_text(patch_model_settings(
            ms.read_text(),
            object_id=new_object_id,
            name=args.pillars_stl.name,
            tx=args.pillar_tx, ty=args.pillar_ty, tz=args.pillar_tz,
            extruder=args.pillar_extruder,
            face_count=len(tris),
        ))

        ps = work / "Metadata" / "project_settings.config"
        patch_project_settings(ps, n_filaments=2)

        args.out.parent.mkdir(parents=True, exist_ok=True)
        if args.out.exists():
            args.out.unlink()
        # Preserve [Content_Types].xml + _rels structure by re-zipping everything
        with zipfile.ZipFile(args.out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(work.rglob("*")):
                if f.is_file():
                    zf.write(f, f.relative_to(work).as_posix())
        print(f"wrote {args.out} ({args.out.stat().st_size} bytes, {len(tris)} pillar tris)")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
