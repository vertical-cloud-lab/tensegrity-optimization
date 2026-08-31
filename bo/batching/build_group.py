"""Build a single-plate project holding a chosen group of the official Sobol
specimens at explicit positions (used to slice the real heterogeneous batch
as two plates: 5 smaller-footprint articles cannot share one plate with the
4 largest once organic supports and the wipe tower are accounted for).

Usage: build_group.py out.3mf "objid:x:y,objid:x:y,..."
"""
import re, sys, uuid, zipfile, os, json

OUT = sys.argv[1]
SPEC = [tuple(p.split(':')) for p in sys.argv[2].split(',')]
SRC = 'batch_x'

model = open(f'{SRC}/3D/3dmodel.model').read()
ms = open(f'{SRC}/Metadata/model_settings.config').read()
header = model[:model.index('<resources>') + len('<resources>')]
build_uuid = re.search(r'<build p:UUID="([^"]+)">', model).group(1)

obj_defs, comp_files, items, ms_objs, insts, asm = [], set(), [], [], [], []
for i, (oid, x, y) in enumerate(SPEC):
    x, y = float(x), float(y)
    blk = re.search(rf'\s*<object id="{oid}" .*?</object>', model, re.S).group(0)
    obj_defs.append(blk)
    comp_files.update(re.findall(r'p:path="(/3D/Objects/[^"]+)"', blk))
    # object-local center: mean of component transform translations
    trs = [tuple(map(float, t.split()[-3:]))
           for t in re.findall(r'transform="([^"]+)"', blk)]
    cx = sum(t[0] for t in trs) / len(trs)
    cy = sum(t[1] for t in trs) / len(trs)
    items.append(f' <item objectid="{oid}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 {x-cx:.6f} {y-cy:.6f} 0" printable="1"/>')
    ms_objs.append(re.search(rf'\s*<object id="{oid}">.*?</object>', ms, re.S).group(0))
    insts.append(f'''    <model_instance>
      <metadata key="object_id" value="{oid}"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="{1000+i}"/>
    </model_instance>''')
    asm.append(f'   <assemble_item object_id="{oid}" instance_id="0" transform="1 0 0 0 1 0 0 0 1 {x:.2f} {y:.2f} 0" offset="0 0 0" />')

new_model = (header + ''.join(obj_defs) + '\n </resources>\n'
             + f' <build p:UUID="{build_uuid}">\n' + '\n'.join(items) + '\n </build>\n</model>\n')
plate = f'''  <plate>
    <metadata key="plater_id" value="1"/>
    <metadata key="plater_name" value="{os.path.basename(OUT)}"/>
    <metadata key="locked" value="false"/>
    <metadata key="filament_map_mode" value="Auto For Flush"/>
{chr(10).join(insts)}
  </plate>'''
new_ms = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>' + ''.join(ms_objs) + '\n' + plate
          + '\n  <assemble>\n' + '\n'.join(asm) + '\n  </assemble>\n</config>\n')

proj_cfg = json.load(open(f'{SRC}/Metadata/project_settings.config'))
proj_cfg['wipe_tower_x'] = ['165']
proj_cfg['wipe_tower_y'] = ['250']
proj = json.dumps(proj_cfg, indent=4)

rels3d = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
          + '\n'.join(f' <Relationship Target="{p}" Id="rel-{j+1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' for j, p in enumerate(sorted(comp_files)))
          + '\n</Relationships>')
rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>'''

if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', open(f'{SRC}/[Content_Types].xml').read())
    z.writestr('_rels/.rels', rels)
    z.writestr('3D/3dmodel.model', new_model)
    z.writestr('3D/_rels/3dmodel.model.rels', rels3d)
    for p in sorted(comp_files):
        z.write(f'{SRC}{p}', p.lstrip('/'))
    z.writestr('Metadata/model_settings.config', new_ms)
    z.writestr('Metadata/project_settings.config', proj)
print("wrote", OUT, "with", len(SPEC), "articles")
