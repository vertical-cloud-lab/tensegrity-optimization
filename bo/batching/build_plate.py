"""Build a single-plate Bambu Studio project with N instances of Specimen 04.

Reuses the exact object definition, mesh file (with any paint data), and full
project_settings.config from the as-printed Sobol batch 3MF. Instances are
placed on a fixed 3x3 grid (columns x=70/160/250, rows y=48/125/202, filled
row-major) chosen so that every instance box (77x75 mm measured from sliced
G-code, supports and brim included) clears the wipe tower zone at the back
(tower set to the H2D profile default x=165, y=250) and the extrusion
calibration strip at the front. No --arrange is needed; the slicer's arranger
otherwise overflows to a second plate beyond 6 articles because it reserves
conservative margins.
"""
import re, sys, uuid, zipfile, os, json

N = int(sys.argv[1])
OUT = sys.argv[2]
SRC = 'batch_x'
COLS = [70.0, 160.0, 250.0]
ROWS = [48.0, 125.0, 202.0]
# object-local center of Specimen 04 (component transform translation)
CX, CY = 250.665314, 172.376358

model = open(f'{SRC}/3D/3dmodel.model').read()
ms = open(f'{SRC}/Metadata/model_settings.config').read()

header = model[:model.index('<resources>') + len('<resources>')]
obj15 = re.search(r'\s*<object id="15".*?</object>', model, re.S).group(0)
build_uuid = re.search(r'<build p:UUID="([^"]+)">', model).group(1)

items = []
for i in range(N):
    x, y = COLS[i % 3], ROWS[i // 3]
    items.append(f' <item objectid="15" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 {x-CX:.6f} {y-CY:.6f} 0" printable="1"/>')

new_model = (header + obj15 + '\n </resources>\n'
             + f' <build p:UUID="{build_uuid}">\n' + '\n'.join(items) + '\n </build>\n</model>\n')

obj15_ms = re.search(r'\s*<object id="15">.*?</object>', ms, re.S).group(0)
instances = '\n'.join(
    f'''    <model_instance>
      <metadata key="object_id" value="15"/>
      <metadata key="instance_id" value="{i}"/>
      <metadata key="identify_id" value="{1000+i}"/>
    </model_instance>''' for i in range(N))
plate = f'''  <plate>
    <metadata key="plater_id" value="1"/>
    <metadata key="plater_name" value="batch_of_{N}"/>
    <metadata key="locked" value="false"/>
    <metadata key="filament_map_mode" value="Auto For Flush"/>
{instances}
  </plate>'''
assemble = '\n'.join(
    f'   <assemble_item object_id="15" instance_id="{i}" transform="1 0 0 0 1 0 0 0 1 {COLS[i%3]:.2f} {ROWS[i//3]:.2f} 0" offset="0 0 0" />'
    for i in range(N))
new_ms = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>' + obj15_ms + '\n' + plate
          + '\n  <assemble>\n' + assemble + '\n  </assemble>\n</config>\n')

proj_cfg = json.load(open(f'{SRC}/Metadata/project_settings.config'))
proj_cfg['wipe_tower_x'] = ['165']
proj_cfg['wipe_tower_y'] = ['250']
proj = json.dumps(proj_cfg, indent=4)

rels3d = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/Objects/object_5.model" Id="rel-5" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>'''
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
    z.write(f'{SRC}/3D/Objects/object_5.model', '3D/Objects/object_5.model')
    z.writestr('Metadata/model_settings.config', new_ms)
    z.writestr('Metadata/project_settings.config', proj)
print("wrote", OUT, "with", N, "instances")
