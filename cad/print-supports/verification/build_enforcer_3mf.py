#!/usr/bin/env python3
# Build a 3MF that bundles a printable model and a Support Enforcer
# modifier mesh inside one object. The output is the Slic3r/PrusaSlicer
# 3MF flavour, which OrcaSlicer (and therefore Bambu Studio, which
# OrcaSlicer is a fork of) also loads — verified end-to-end with the
# OrcaSlicer 2.4.0-dev nightly CLI and a Bambu Lab H2D 0.4 nozzle system
# profile (see verification/README.md). Neither OrcaSlicer's nor
# PrusaSlicer's `--merge` CLI flag produces an enforcer volume on its
# own (both emit ModelPart), so this small helper writes the
# `volume_type=SupportEnforcer` metadata ourselves.
import struct
import sys
import zipfile
from pathlib import Path


def read_binary_stl(path: Path):
    data = path.read_bytes()
    # Skip the 80-byte header
    n = struct.unpack_from("<I", data, 80)[0]
    off = 84
    tris = []
    for _ in range(n):
        # normal (skip) + 3 vertices + attribute (skip)
        vs = struct.unpack_from("<3f3f3f3f", data, off)
        tris.append([vs[3:6], vs[6:9], vs[9:12]])
        off += 50
    return tris


def stl_bbox(tris):
    xs = [v[0] for t in tris for v in t]
    ys = [v[1] for t in tris for v in t]
    zs = [v[2] for t in tris for v in t]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def write_3mf(out_path: Path, part_tris, enforcer_tris,
              translate=(0.0, 0.0, 0.0)):
    """Emit a 3MF with one object containing two volumes:
        volume 0 = ModelPart       (the printable mesh)
        volume 1 = SupportEnforcer (the enforcer modifier mesh)
    Both are placed in the same object coordinate system. `translate`
    shifts the whole object on the bed for centering."""
    all_tris = []
    parts = [("part", part_tris), ("enforcer", enforcer_tris)]
    vol_ranges = {}
    vid = 0
    for name, tris in parts:
        first = vid
        for tri in tris:
            for vertex in tri:
                all_tris.append(vertex)
                vid += 1
        # vid now counts vertices. We need facet-ID ranges. Each triangle
        # uses 3 vertices, so the facets are: first_facet = first/3.
        first_facet = first // 3
        last_facet = (vid // 3) - 1
        vol_ranges[name] = (first_facet, last_facet)

    # Build the 3D/3dmodel.model XML (single object, two volumes)
    vertices_xml = "\n".join(
        f'      <vertex x="{v[0]}" y="{v[1]}" z="{v[2]}"/>'
        for v in all_tris)
    triangles_xml = []
    for i in range(0, len(all_tris), 3):
        triangles_xml.append(
            f'      <triangle v1="{i}" v2="{i+1}" v3="{i+2}"/>')
    triangles_xml = "\n".join(triangles_xml)
    tx, ty, tz = translate
    model_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:slic3rpe="http://schemas.slic3r.org/3mf/2017/06">
 <metadata name="Application">PrusaSlicer-tensegrity-enforcer</metadata>
 <resources>
  <object id="1" type="model">
   <mesh>
    <vertices>
{vertices_xml}
    </vertices>
    <triangles>
{triangles_xml}
    </triangles>
   </mesh>
  </object>
 </resources>
 <build>
  <item objectid="1" transform="1 0 0 0 1 0 0 0 1 {tx} {ty} {tz}"/>
 </build>
</model>
'''

    (pf_first, pf_last) = vol_ranges["part"]
    (ef_first, ef_last) = vol_ranges["enforcer"]
    config_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<config>
 <object id="1" instances_count="1">
  <metadata type="object" key="name" value="t3-prism + enforcers"/>
  <volume firstid="{pf_first}" lastid="{pf_last}">
   <metadata type="volume" key="name" value="t3-prism"/>
   <metadata type="volume" key="volume_type" value="ModelPart"/>
   <metadata type="volume" key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
  </volume>
  <volume firstid="{ef_first}" lastid="{ef_last}">
   <metadata type="volume" key="name" value="enforcers"/>
   <metadata type="volume" key="volume_type" value="SupportEnforcer"/>
   <metadata type="volume" key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
  </volume>
 </object>
</config>
'''

    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>
'''
    rels_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rel-1" Target="/3D/3dmodel.model" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
'''

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels_xml)
        z.writestr("3D/3dmodel.model", model_xml)
        z.writestr("Metadata/Slic3r_PE_model.config", config_xml)


def main():
    if len(sys.argv) < 4:
        print("usage: build_enforcer_3mf.py part.stl enforcer.stl out.3mf "
              "[bed_cx] [bed_cy]", file=sys.stderr)
        raise SystemExit(2)
    part = read_binary_stl(Path(sys.argv[1]))
    enforcer = read_binary_stl(Path(sys.argv[2]))
    out_path = Path(sys.argv[3])
    bed_cx = float(sys.argv[4]) if len(sys.argv) > 4 else 128.0
    bed_cy = float(sys.argv[5]) if len(sys.argv) > 5 else 128.0
    # Compute the translation to put the printable part's XY centre on the
    # bed centre and its lowest point at z = 0. Then bake the SAME
    # translation into BOTH the part and the enforcer mesh vertices so
    # PrusaSlicer's per-volume auto-arrange doesn't pull them apart.
    (xmin, ymin, zmin), (xmax, ymax, _) = stl_bbox(part)
    cx = (xmin + xmax) / 2.0
    cy = (ymin + ymax) / 2.0
    tx, ty, tz = (bed_cx - cx, bed_cy - cy, -zmin)

    def shift(tris):
        return [[(v[0] + tx, v[1] + ty, v[2] + tz) for v in t] for t in tris]

    part = shift(part)
    enforcer = shift(enforcer)
    write_3mf(out_path, part, enforcer, translate=(0.0, 0.0, 0.0))
    print(f"Wrote {out_path}")
    print(f"  part triangles    : {len(part)}")
    print(f"  enforcer triangles: {len(enforcer)}")
    print(f"  baked translate   : ({tx:.2f}, {ty:.2f}, {tz:.2f})")


if __name__ == "__main__":
    main()
