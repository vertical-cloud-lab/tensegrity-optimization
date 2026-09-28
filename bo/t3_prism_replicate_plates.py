"""Print package for the replicate study (sne plates) and the 3dran reprint.

Requested on PR #102 on 2026-09-28 (comment 5873581840, @me-madsen): the
three designs proposed in ``t3-prism-replicate-study-plan.md`` and accepted
by the lab (corny7 = trial 37, corny8 = trial 39, corny2 = trial 38, under
the lab-confirmed corny key of commit 0a31417), three copies of each design
per plate, three plates, 27 articles named ``[plate]sne[spec][copy]`` (for
example ``2sne73`` = plate 2, corny7, copy 3); plus a third print of the
round-3 plate, whose first two prints are drran1-9 and 2dran1-9, named
``3dran1`` to ``3dran9``.

Nothing is re-rendered and no mass is re-solved. Every article is built from
the mesh data of the committed slicer project it was first printed from
(round 4 for the corny designs, round 3 for 3dran), so the geometry is the
printed geometry bit for bit, and the per-part sparse infill overrides and
the filament settings are carried over verbatim. Before writing anything the
script checks the project meshes against the committed per-trial STLs and
the round manifests, and it refuses to write if they disagree.

Replicate plate layout
----------------------
Each plate is a 3 x 3 Latin square: every row (back, middle, front) and
every left/center/right slot holds one article of each design, and the
square is cycled from plate to plate so that each design occupies each of
the nine plate positions exactly once over the three plates. Plate position
therefore cannot masquerade as a design effect, within a plate or across
the study. Because every row holds one copy of each design, the copy digit
is the row: copy 1 is the back row, copy 2 the middle row, copy 3 the front
row (the back-left to front-right raster every earlier plate used).

Rows are packed from measured mesh extents, so the wide corny7/corny8
articles do not force a wide cell on the narrow corny2. The whole layout
stays inside the H2D reach limits the round-4 generator enforces (TPU at
x >= 30 mm, PLA well left of the wipe tower the round-4 project places at
x = 287 mm), and the round-4 project settings are reused verbatim, so the
three plates print at exactly the round-4 filament point.

Outputs, all under ``bo/replicate-study/``:

* ``t3-prism-replicate-sne-plate{1,2,3}.H2D-MM-PLAstruts-TPUcables.3mf``:
  one Bambu Studio project per plate, objects named by article ID.
* ``t3-prism-3dran.H2D-MM-PLAstruts-TPUcables.3mf``: the committed round-3
  project with only its object names changed (``Trial 36`` -> ``3dran1``
  and so on); every other byte of the project is the drran/2dran file.
* ``t3-prism-replicate-print-key.csv``: every article ID with its design,
  plate, position, infill and filament settings.
* ``t3-prism-replicate-sne-plate-maps.png`` and
  ``t3-prism-3dran-plate-map.png``: top-down labeled plate maps.
* ``t3-prism-replicate-picks-performance.png``: measured rebound energy vs
  shock transmissibility for the three picks only.
* ``stls/``: byte copies of the committed per-trial STLs for the three
  picks and for the nine round-3 designs, renamed by article.

Run from the repo root (no OpenSCAD or slicer needed, about 30 s)::

    python3 bo/t3_prism_replicate_plates.py
"""

from __future__ import annotations

import csv
import hashlib
import re
import shutil
import sys
import uuid
import zipfile
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle  # noqa: E402
from scipy.spatial import ConvexHull  # noqa: E402

BO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BO_DIR))
from t3_prism_printed_mass_plate import (  # noqa: E402
    EXTRUDER1_MAX_X,
    EXTRUDER2_MIN_X,
    PLATE_MARGIN,
    PLATE_X,
    PLATE_Y,
    REACH_CLEARANCE,
    stl_volume_bbox,
)
from t3_prism_bo_campaign import (  # noqa: E402
    FIG_RC,
    FIGURE_DPI,
    FRONT_BLUE,
    INK,
    LABEL_GRAY,
    _callout,
    _style_axes,
)

OUT_DIR = BO_DIR / "replicate-study"
STL_DIR = BO_DIR / "per-specimen-stls"

ROUND4_3MF = BO_DIR / "slices" / "t3-prism-bo-round4.H2D-MM-PLAstruts-TPUcables.3mf"
ROUND3_3MF = BO_DIR / "slices" / "t3-prism-bo-round3.H2D-MM-PLAstruts-TPUcables.3mf"
ROUND4_MANIFEST = BO_DIR / "t3-prism-bo-round4-designs.csv"
ROUND3_MANIFEST = BO_DIR / "t3-prism-bo-round3-designs.csv"
ROUND3_KEY = BO_DIR / "t3-prism-bo-round3-print-key.csv"
PICKS_CSV = BO_DIR / "t3-prism-replicate-study-picks.csv"

# The study's designs in the plan's order (on the front, further, furthest).
# `spec` is the digit that goes into the article ID.
DESIGNS = [
    {"print_id": "corny7", "spec": 7, "trial": 37, "role": "on the front"},
    {"print_id": "corny8", "spec": 8, "trial": 39, "role": "further away"},
    {"print_id": "corny2", "spec": 2, "trial": 38, "role": "furthest away"},
]
N_PLATES = 3
ROWS = ("back", "middle", "front")    # copy digit = row index + 1
SLOTS = ("left", "center", "right")
ROW_GAP_MM = 8.0     # bbox-to-bbox, between rows
SLOT_GAP_MM = 7.0    # bbox-to-bbox, within a row (round 4 used 6)
TOWER_CLEARANCE_MM = 10.0  # PLA kept this far left of the wipe tower body

MESH_FILE = "3D/Objects/object_1.model"
MODEL_FILE = "3D/3dmodel.model"
SETTINGS_FILE = "Metadata/model_settings.config"
PROJECT_FILE = "Metadata/project_settings.config"

# Fixed namespace so every UUID written into the projects is reproducible:
# rerunning the script rewrites byte-identical 3mf files.
UUID_NS = uuid.UUID("5d0c6f3e-2f7a-4c1e-9a55-3b1f0c7e9a21")

DESIGN_COLORS = {"corny7": "#2a78d6", "corny8": "#eb6834", "corny2": "#3f9b5a"}


# ---- 3mf parsing ------------------------------------------------------------
def read_zip(path: Path) -> tuple[list[zipfile.ZipInfo], dict[str, bytes]]:
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        return infos, {i.filename: z.read(i.filename) for i in infos}


def write_zip(path: Path, infos: list[zipfile.ZipInfo],
              contents: dict[str, bytes]) -> None:
    """Rewrite a project with the source's entry order and timestamps, so a
    rerun produces a byte-identical file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in infos:
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = info.external_attr
            zout.writestr(zi, contents[info.filename])


def _floats(s: str) -> list[float]:
    return [float(v) for v in s.split()]


def parse_project(path: Path) -> dict:
    """Articles of a project written by bo/t3_prism_printed_mass_plate.py:
    one composite object per article, one struts part (extruder 1) and one
    cables part (extruder 2), meshes in a single object file."""
    infos, contents = read_zip(path)
    mesh_xml = contents[MESH_FILE].decode()
    model_xml = contents[MODEL_FILE].decode()
    cfg = contents[SETTINGS_FILE].decode()

    meshes = {}
    for m in re.finditer(r' *<object id="(\d+)"[^>]*>\s*<mesh>.*?</mesh>\s*'
                         r'</object>', mesh_xml, re.S):
        block = m.group(0)
        v = np.array(re.findall(
            r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"/>', block),
            dtype=float)
        meshes[int(m.group(1))] = {"xml": block.strip(), "verts": v,
                                   "lo": v.min(axis=0), "hi": v.max(axis=0)}

    comps = {}
    for m in re.finditer(r'<object id="(\d+)"[^>]*type="model">\s*'
                         r'<components>(.*?)</components>', model_xml, re.S):
        for c in re.finditer(r'<component p:path="([^"]+)" objectid="(\d+)"'
                             r'[^>]*transform="([^"]+)"/>', m.group(2)):
            comps[int(c.group(2))] = (int(m.group(1)),
                                      np.array(_floats(c.group(3))[9:12]))
    items = {int(m.group(1)): np.array(_floats(m.group(2))[9:12])
             for m in re.finditer(r'<item objectid="(\d+)"[^>]*transform='
                                  r'"([^"]+)"', model_xml)}

    articles = []
    for m in re.finditer(r'<object id="(\d+)">(.*?)</object>', cfg, re.S):
        body = m.group(2)
        name = re.search(r'<metadata key="name" value="([^"]+)"/>',
                         body).group(1)
        parts = {}
        for p in re.finditer(r'<part id="(\d+)"[^>]*>.*?</part>', body, re.S):
            pxml = p.group(0)
            ext = re.search(r'key="extruder" value="(\d+)"', pxml).group(1)
            kind = "struts" if ext == "1" else "cables"
            mesh_id = int(p.group(1))
            parent, trans = comps[mesh_id]
            if parent != int(m.group(1)):
                raise SystemExit(f"{path.name}: part {mesh_id} is not a "
                                 f"component of object {m.group(1)}")
            parts[kind] = {
                "mesh_id": mesh_id,
                "xml": pxml,
                "name": re.search(r'key="name" value="([^"]+)"', pxml).group(1),
                "infill": re.search(r'key="sparse_infill_density" '
                                    r'value="([^"]+)"', pxml).group(1),
                "trans": trans,
            }
        trial = int(re.search(r"-t(\d+)-", parts["struts"]["name"]).group(1))
        articles.append({"object_id": int(m.group(1)), "name": name,
                         "trial": trial, "parts": parts,
                         "item": items[int(m.group(1))]})
    return {"infos": infos, "contents": contents, "meshes": meshes,
            "articles": {a["trial"]: a for a in articles},
            "mesh_header": mesh_xml[:mesh_xml.index("<resources>")
                                    + len("<resources>")],
            "model_header": model_xml[:model_xml.index("<resources>")
                                      + len("<resources>")]}


def article_bbox(project: dict, article: dict) -> tuple[np.ndarray, np.ndarray]:
    """World-space bbox of an article (component + build-item translation)."""
    los, his = [], []
    for part in article["parts"].values():
        mesh = project["meshes"][part["mesh_id"]]
        off = part["trans"] + article["item"]
        los.append(mesh["lo"] + off)
        his.append(mesh["hi"] + off)
    return np.min(los, axis=0), np.max(his, axis=0)


def verify_against_stls(project: dict, rnd: str, trials) -> dict[int, dict]:
    """The committed per-trial STLs and the project meshes must be the same
    solids in the same component frame; returns per-trial local geometry."""
    out = {}
    for t in trials:
        art = project["articles"][t]
        geo = {}
        for kind, part in art["parts"].items():
            stl = STL_DIR / f"t3-prism-bo-{rnd}-t{t}-{kind}.stl"
            _, lo, hi = stl_volume_bbox(stl)
            mesh = project["meshes"][part["mesh_id"]]
            lo3, hi3 = mesh["lo"] + part["trans"], mesh["hi"] + part["trans"]
            err = max(np.max(np.abs(lo3 - lo)), np.max(np.abs(hi3 - hi)))
            if err > 0.01:
                raise SystemExit(f"trial {t} {kind}: project mesh and {stl.name}"
                                 f" disagree by {err:.3f} mm; refusing to write")
            geo[kind] = {"lo": lo3, "hi": hi3, "stl": stl,
                         "verts": mesh["verts"] + part["trans"]}
        lo = np.minimum(geo["struts"]["lo"], geo["cables"]["lo"])
        hi = np.maximum(geo["struts"]["hi"], geo["cables"]["hi"])
        geo["lo"], geo["hi"] = lo, hi
        geo["center"] = (lo + hi) / 2.0
        out[t] = geo
    return out


# ---- replicate plates ---------------------------------------------------------
def latin_design(plate: int, row: int, slot: int) -> dict:
    """Design at (row, slot) of plate `plate` (1-based). Each plate is a Latin
    square, and cycling it by one per plate puts every design in every plate
    position exactly once over the three plates."""
    return DESIGNS[(row + slot + plate - 1) % len(DESIGNS)]


def plan_replicate_layout(geo: dict[int, dict], wipe_tower_x: float) -> dict:
    """Row-packed Latin-square layout from measured extents."""
    ext = {d["trial"]: geo[d["trial"]]["hi"] - geo[d["trial"]]["lo"]
           for d in DESIGNS}
    # Left edge that keeps every design's TPU reachable if it is leftmost.
    tpu_min_x = EXTRUDER2_MIN_X + REACH_CLEARANCE
    left = max(PLATE_MARGIN, max(
        tpu_min_x - (geo[t]["cables"]["lo"][0] - geo[t]["lo"][0])
        for t in ext))
    row_w = sum(e[0] for e in ext.values()) + SLOT_GAP_MM * (len(SLOTS) - 1)
    row_h = max(e[1] for e in ext.values())
    total_h = len(ROWS) * row_h + ROW_GAP_MM * (len(ROWS) - 1)
    y_front = PLATE_MARGIN + (PLATE_Y - 2 * PLATE_MARGIN - total_h) / 2.0
    # row 0 is the back row (largest y)
    row_cy = [y_front + total_h - row_h / 2.0 - r * (row_h + ROW_GAP_MM)
              for r in range(len(ROWS))]

    plates = {}
    for p in range(1, N_PLATES + 1):
        cells = []
        for r in range(len(ROWS)):
            x = left
            for s in range(len(SLOTS)):
                d = latin_design(p, r, s)
                w = ext[d["trial"]][0]
                cells.append({"plate": p, "row": r, "slot": s, "design": d,
                              "cx": x + w / 2.0, "cy": row_cy[r],
                              "id": f"{p}sne{d['spec']}{r + 1}"})
                x += w + SLOT_GAP_MM
        plates[p] = cells

    # Reach and tower checks on the final geometry, not the plan.
    for cells in plates.values():
        for c in cells:
            g = geo[c["design"]["trial"]]
            shift = np.array([c["cx"], c["cy"]]) - g["center"][:2]
            c["shift"] = shift
            tpu_lo = g["cables"]["lo"][0] + shift[0]
            pla_hi = g["struts"]["hi"][0] + shift[0]
            y_lo, y_hi = g["lo"][1] + shift[1], g["hi"][1] + shift[1]
            if tpu_lo < tpu_min_x - 1e-6:
                raise SystemExit(f"{c['id']}: TPU at x = {tpu_lo:.1f} mm")
            if pla_hi > min(EXTRUDER1_MAX_X - REACH_CLEARANCE,
                            wipe_tower_x - TOWER_CLEARANCE_MM) + 1e-6:
                raise SystemExit(f"{c['id']}: PLA at x = {pla_hi:.1f} mm")
            if y_lo < PLATE_MARGIN or y_hi > PLATE_Y - PLATE_MARGIN:
                raise SystemExit(f"{c['id']}: y {y_lo:.1f} to {y_hi:.1f} mm")
    return {"plates": plates, "left_mm": left, "row_w_mm": row_w,
            "row_h_mm": row_h, "total_h_mm": total_h, "row_cy": row_cy}


def _uuid(*key) -> str:
    return str(uuid.uuid5(UUID_NS, "/".join(str(k) for k in key)))


def _matrix(t: np.ndarray) -> str:
    return (f"1 0 0 {t[0]!r} 0 1 0 {t[1]!r} 0 0 1 {t[2]!r} 0 0 0 1")


def _part_xml(src_xml: str, mesh_id: int, trans: np.ndarray) -> str:
    """Source part block with a new id and the new placement written into
    both the matrix and the source offsets (they carry the same numbers in
    every project the generator has written)."""
    x = re.sub(r'<part id="\d+"', f'<part id="{mesh_id}"', src_xml, count=1)
    x = re.sub(r'(key="matrix" value=")[^"]*(")',
               lambda m: m.group(1) + _matrix(trans) + m.group(2), x)
    for k, v in zip("xyz", trans):
        x = re.sub(rf'(key="source_offset_{k}" value=")[^"]*(")',
                   lambda m, v=v: m.group(1) + repr(float(v)) + m.group(2), x)
    return x


def build_replicate_project(src: dict, cells: list[dict], plate: int,
                            out: Path) -> None:
    meshes_out, objects_out, cfg_out, items_out, inst_out = [], [], [], [], []
    base_obj = 2 * len(cells) + 1  # composite ids follow the mesh ids
    for k, c in enumerate(cells):
        art = src["articles"][c["design"]["trial"]]
        obj_id = base_obj + k
        comp_tags, part_xml = [], []
        for j, kind in enumerate(("struts", "cables")):
            part = art["parts"][kind]
            mesh_id = 2 * k + j + 1
            mesh = src["meshes"][part["mesh_id"]]["xml"]
            mesh = re.sub(r'<object id="\d+" p:UUID="[^"]*"',
                          f'<object id="{mesh_id}" p:UUID="'
                          f'{_uuid("mesh", plate, c["id"], kind)}"', mesh,
                          count=1)
            meshes_out.append("  " + mesh)
            trans = part["trans"] + np.array([*c["shift"], 0.0])
            t = " ".join(repr(float(v)) for v in trans)
            comp_tags.append(
                f'    <component p:path="/{MESH_FILE}" objectid="{mesh_id}" '
                f'p:UUID="{_uuid("comp", plate, c["id"], kind)}" '
                f'transform="1 0 0 0 1 0 0 0 1 {t}"/>')
            part_xml.append("    " + _part_xml(part["xml"], mesh_id, trans))
            c.setdefault("infill", {})[kind] = part["infill"]
            c.setdefault("part_names", {})[kind] = part["name"]
        objects_out.append(
            f'  <object id="{obj_id}" p:UUID="{_uuid("obj", plate, c["id"])}"'
            f' type="model">\n   <components>\n' + "\n".join(comp_tags)
            + "\n   </components>\n  </object>")
        cfg_out.append(f'  <object id="{obj_id}">\n'
                       f'    <metadata key="name" value="{c["id"]}"/>\n'
                       + "\n".join(part_xml) + "\n  </object>")
        items_out.append(
            f'  <item objectid="{obj_id}" p:UUID="'
            f'{_uuid("item", plate, c["id"])}" transform="1 0 0 0 1 0 0 0 1 '
            f'0 0 0" printable="1"/>')
        inst_out.append(
            f'    <model_instance>\n'
            f'      <metadata key="object_id" value="{obj_id}"/>\n'
            f'      <metadata key="instance_id" value="0"/>\n'
            f'      <metadata key="identify_id" value="{100 + k}"/>\n'
            f'    </model_instance>')

    contents = dict(src["contents"])
    contents[MESH_FILE] = (src["mesh_header"] + "\n" + "\n".join(meshes_out)
                           + "\n </resources>\n <build/>\n</model>\n").encode()
    contents[MODEL_FILE] = (
        src["model_header"] + "\n" + "\n".join(objects_out)
        + f'\n </resources>\n <build p:UUID="{_uuid("build", plate)}">\n'
        + "\n".join(items_out) + "\n </build>\n</model>\n").encode()
    src_cfg = src["contents"][SETTINGS_FILE].decode()
    plate_head = re.search(r"<plate>(.*?)<model_instance>", src_cfg,
                           re.S).group(1).rstrip() + "\n"
    plate_head = re.sub(r'(key="plater_name" value=")[^"]*(")',
                        rf"\g<1>Replicate plate {plate} "
                        rf"({plate}sne##)\g<2>", plate_head)
    contents[SETTINGS_FILE] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'
        + "\n".join(cfg_out) + "\n  <plate>" + plate_head
        + "\n".join(inst_out) + "\n  </plate>\n  <assemble>\n  </assemble>\n"
        "</config>\n").encode()
    write_zip(out, src["infos"], contents)


def verify_replicate_project(path: Path, cells: list[dict],
                             src: dict) -> None:
    """Re-read the written project: names, infills, extruders, placement,
    no overlaps, and settings byte-identical to the round-4 project."""
    proj = parse_project(path)
    arts = {}
    contents = proj["contents"]
    cfg = contents[SETTINGS_FILE].decode()
    names = re.findall(r'<object id="\d+">\s*<metadata key="name" '
                       r'value="([^"]+)"/>', cfg)
    if sorted(names) != sorted(c["id"] for c in cells):
        raise SystemExit(f"{path.name}: object names {names}")
    for m in re.finditer(r'<object id="(\d+)">(.*?)</object>', cfg, re.S):
        name = re.search(r'key="name" value="([^"]+)"', m.group(2)).group(1)
        arts[name] = int(m.group(1))
    # parse_project keys by trial, which repeats here; re-key by object id
    by_object = {a["object_id"]: a for a in _articles_by_object(proj)}
    boxes = []
    for c in cells:
        art = by_object[arts[c["id"]]]
        for kind in ("struts", "cables"):
            if art["parts"][kind]["infill"] != c["infill"][kind]:
                raise SystemExit(f"{c['id']} {kind}: infill "
                                 f"{art['parts'][kind]['infill']}")
        lo, hi = article_bbox(proj, art)
        want = np.array([c["cx"], c["cy"]])
        if np.max(np.abs((lo[:2] + hi[:2]) / 2.0 - want)) > 0.01:
            raise SystemExit(f"{c['id']}: placed off its planned center")
        boxes.append((c["id"], lo, hi))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (a, alo, ahi), (b, blo, bhi) = boxes[i], boxes[j]
            gap = max(blo[0] - ahi[0], alo[0] - bhi[0],
                      blo[1] - ahi[1], alo[1] - bhi[1])
            if gap < min(ROW_GAP_MM, SLOT_GAP_MM) - 0.01:
                raise SystemExit(f"{path.name}: {a} and {b} only {gap:.1f} mm "
                                 f"apart")
    if contents[PROJECT_FILE] != src["contents"][PROJECT_FILE]:
        raise SystemExit(f"{path.name}: project settings drifted from round 4")


def _articles_by_object(proj: dict) -> list[dict]:
    """parse_project() keys articles by trial; on a replicate plate a trial
    repeats, so rebuild the full list from the settings file."""
    cfg = proj["contents"][SETTINGS_FILE].decode()
    model_xml = proj["contents"][MODEL_FILE].decode()
    comps = {}
    for m in re.finditer(r'<object id="(\d+)"[^>]*type="model">\s*'
                         r'<components>(.*?)</components>', model_xml, re.S):
        for c in re.finditer(r'objectid="(\d+)"[^>]*transform="([^"]+)"',
                             m.group(2)):
            comps[int(c.group(1))] = np.array(_floats(c.group(2))[9:12])
    items = {int(m.group(1)): np.array(_floats(m.group(2))[9:12])
             for m in re.finditer(r'<item objectid="(\d+)"[^>]*transform='
                                  r'"([^"]+)"', model_xml)}
    out = []
    for m in re.finditer(r'<object id="(\d+)">(.*?)</object>', cfg, re.S):
        parts = {}
        for p in re.finditer(r'<part id="(\d+)"[^>]*>.*?</part>', m.group(2),
                             re.S):
            pxml = p.group(0)
            ext = re.search(r'key="extruder" value="(\d+)"', pxml).group(1)
            parts["struts" if ext == "1" else "cables"] = {
                "mesh_id": int(p.group(1)),
                "infill": re.search(r'key="sparse_infill_density" '
                                    r'value="([^"]+)"', pxml).group(1),
                "trans": comps[int(p.group(1))]}
        out.append({"object_id": int(m.group(1)), "parts": parts,
                    "item": items[int(m.group(1))]})
    return out


# ---- 3dran ----------------------------------------------------------------------
def load_3dran_key() -> list[dict]:
    """3dranN is the same design as drranN and 2dranN (photo-confirmed key)."""
    rows = list(csv.DictReader(ROUND3_KEY.open()))
    first = {r["print_id"]: r for r in rows}
    key = []
    for n in range(1, 10):
        a, b = first[f"drran{n}"], first[f"2dran{n}"]
        if a["source_trial"] != b["source_trial"]:
            raise SystemExit(f"drran{n} and 2dran{n} map to different trials")
        key.append({"id": f"3dran{n}", "trial": int(a["source_trial"]),
                    "spec": int(a["spec"]), "row": a["plate_row"],
                    "slot": a["plate_col"], "drran": a, "2dran": b})
    return key


def build_3dran_project(key: list[dict], out: Path) -> dict:
    """The round-3 project with only the object names (and the plate label)
    changed. Returns the parsed source for the plate map."""
    src = parse_project(ROUND3_3MF)
    cfg = src["contents"][SETTINGS_FILE].decode()
    for k in key:
        old = f'<metadata key="name" value="Trial {k["trial"]}"/>'
        if cfg.count(old) != 1:
            raise SystemExit(f"round-3 project: {old!r} found "
                             f"{cfg.count(old)} times")
        cfg = cfg.replace(old, f'<metadata key="name" value="{k["id"]}"/>')
    cfg = re.sub(r'(key="plater_name" value=")[^"]*(")',
                 r"\g<1>3dran reprint of drran/2dran\g<2>", cfg, count=1)
    contents = dict(src["contents"])
    contents[SETTINGS_FILE] = cfg.encode()
    write_zip(out, src["infos"], contents)

    # Everything but the names must still be the drran/2dran file.
    _, new = read_zip(out)
    for name, data in src["contents"].items():
        if name != SETTINGS_FILE and new[name] != data:
            raise SystemExit(f"3dran project: {name} differs from round 3")
    old_lines = src["contents"][SETTINGS_FILE].decode().splitlines()
    new_lines = new[SETTINGS_FILE].decode().splitlines()
    changed = [(a, b) for a, b in zip(old_lines, new_lines) if a != b]
    if len(old_lines) != len(new_lines) or len(changed) != len(key) + 1:
        raise SystemExit("3dran project: unexpected settings changes")
    return src


# ---- key, STL copies ----------------------------------------------------------
def manifest(path: Path) -> dict[int, dict]:
    return {int(r["trial_index"]): r for r in csv.DictReader(path.open())}


def write_key(layout: dict, key3: list[dict], src3: dict) -> Path:
    m4, m3 = manifest(ROUND4_MANIFEST), manifest(ROUND3_MANIFEST)
    picks = {r["print_id"]: r for r in csv.DictReader(PICKS_CSV.open())}
    cols = ["article_id", "plate", "design", "trial", "spec_digit",
            "copy", "plate_row", "plate_slot", "plate_x_mm", "plate_y_mm",
            "strut_infill_pct", "tpu_infill_pct", "pla_nozzle_temp_C",
            "pla_flow_mm3_s", "tpu_nozzle_temp_C", "tpu_flow_mm3_s",
            "printed_g_est", "earlier_prints", "earlier_masses_g",
            "slicer_project", "struts_stl", "cables_stl"]
    rows = []
    for p, cells in layout["plates"].items():
        for c in sorted(cells, key=lambda c: (c["row"], c["slot"])):
            d, man = c["design"], m4[c["design"]["trial"]]
            rows.append([
                c["id"], f"sne{p}", d["print_id"], d["trial"], d["spec"],
                c["row"] + 1, ROWS[c["row"]], SLOTS[c["slot"]],
                f"{c['cx']:.1f}", f"{c['cy']:.1f}",
                man["strut_infill_pct"], man["tpu_infill_pct"],
                *(f"{float(man[k]):g}" for k in (
                    "pla_nozzle_temp_C", "pla_flow_mm3_s",
                    "tpu_nozzle_temp_C", "tpu_flow_mm3_s")),
                man["printed_g_est"], d["print_id"],
                picks[d["print_id"]]["mass_g"],
                f"t3-prism-replicate-sne-plate{p}."
                "H2D-MM-PLAstruts-TPUcables.3mf",
                f"stls/{d['print_id']}-t{d['trial']}-struts.stl",
                f"stls/{d['print_id']}-t{d['trial']}-cables.stl",
            ])
    for k in key3:
        art = src3["articles"][k["trial"]]
        lo, hi = article_bbox(src3, art)
        man = m3[k["trial"]]
        rows.append([
            k["id"], "3dran", f"round-3 trial {k['trial']}", k["trial"], "",
            "", k["row"], k["slot"], f"{(lo[0] + hi[0]) / 2:.1f}",
            f"{(lo[1] + hi[1]) / 2:.1f}",
            man["strut_infill_pct"], man["tpu_infill_pct"],
            *(f"{float(man[kk]):g}" for kk in (
                "pla_nozzle_temp_C", "pla_flow_mm3_s",
                "tpu_nozzle_temp_C", "tpu_flow_mm3_s")),
            man["printed_g_est"],
            f"{k['drran']['print_id']}; {k['2dran']['print_id']}",
            f"{k['drran']['mass_g_with_label']}; "
            f"{k['2dran']['mass_g_with_label']}",
            "t3-prism-3dran.H2D-MM-PLAstruts-TPUcables.3mf",
            f"stls/3dran/{k['id']}-t{k['trial']}-struts.stl",
            f"stls/3dran/{k['id']}-t{k['trial']}-cables.stl",
        ])
    path = OUT_DIR / "t3-prism-replicate-print-key.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    return path


def copy_stls(key3: list[dict]) -> None:
    """Byte copies of the committed per-trial STLs, renamed by article so the
    folder is self-contained (git stores identical content once)."""
    (OUT_DIR / "stls" / "3dran").mkdir(parents=True, exist_ok=True)
    for d in DESIGNS:
        for kind in ("struts", "cables"):
            shutil.copyfile(
                STL_DIR / f"t3-prism-bo-round4-t{d['trial']}-{kind}.stl",
                OUT_DIR / "stls" / f"{d['print_id']}-t{d['trial']}-{kind}.stl")
    for k in key3:
        for kind in ("struts", "cables"):
            shutil.copyfile(
                STL_DIR / f"t3-prism-bo-round3-t{k['trial']}-{kind}.stl",
                OUT_DIR / "stls" / "3dran" / f"{k['id']}-t{k['trial']}-{kind}.stl")


# ---- figures ---------------------------------------------------------------------
def _hull(verts: np.ndarray) -> np.ndarray:
    xy = verts[:, :2]
    return xy[ConvexHull(xy).vertices]


def _plate_axes(ax, title: str) -> None:
    ax.add_patch(Rectangle((0, 0), PLATE_X, PLATE_Y, fc="#f4f3ef",
                           ec="#4a4a47", lw=1.4, zorder=0))
    ax.set_xlim(-8, PLATE_X + 8)
    ax.set_ylim(-26, PLATE_Y + 44)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(PLATE_X / 2, PLATE_Y + 5, "BACK", ha="center", va="bottom",
            fontsize=12, color=LABEL_GRAY)
    ax.text(PLATE_X / 2, -8, "FRONT (door)", ha="center", va="top",
            fontsize=12, color=LABEL_GRAY)
    ax.text(0, PLATE_Y + 26, title, ha="left", va="bottom", fontsize=17,
            color=INK, fontweight="bold")


def _tower(ax, x: float, y: float) -> None:
    ax.add_patch(Rectangle((x, y), 10, 30, fc="#d9d8d3", ec="#8d8c88",
                           lw=1.0, ls="--", zorder=1))
    ax.text(x + 5, y + 34, "wipe\ntower", ha="center", va="bottom",
            fontsize=9, color=LABEL_GRAY)


def render_sne_plate_maps(layout: dict, geo4: dict, tower_xy) -> Path:
    hulls = {d["trial"]: _hull(np.vstack([geo4[d["trial"]]["struts"]["verts"],
                                          geo4[d["trial"]]["cables"]["verts"]]))
             - geo4[d["trial"]]["center"][:2] for d in DESIGNS}
    with plt.rc_context({**FIG_RC, "font.size": 12}):
        fig, axes = plt.subplots(1, N_PLATES, figsize=(19.5, 7.4),
                                 dpi=FIGURE_DPI)
        for ax, (p, cells) in zip(axes, layout["plates"].items()):
            _plate_axes(ax, f"Plate {p}  ({p}sne##)")
            _tower(ax, *tower_xy)
            for c in cells:
                d = c["design"]
                pts = hulls[d["trial"]] + np.array([c["cx"], c["cy"]])
                ax.add_patch(Polygon(pts, closed=True,
                                     fc=DESIGN_COLORS[d["print_id"]],
                                     ec=INK, lw=1.0, alpha=0.30, zorder=2))
                ax.text(c["cx"], c["cy"] + 5, c["id"], ha="center",
                        va="center", fontsize=17, fontweight="bold",
                        color=INK, zorder=3)
                ax.text(c["cx"], c["cy"] - 12,
                        f"{d['print_id']} (t{d['trial']})", ha="center",
                        va="center", fontsize=11, color="#3d3d3a", zorder=3)
        fig.text(0.5, 0.02,
                 "ID = [plate] sne [design digit: 7 = corny7, 8 = corny8, "
                 "2 = corny2] [copy: 1 = back row, 2 = middle, 3 = front]."
                 "  Each design sits in every position once over the three "
                 "plates.", ha="center", fontsize=12, color=LABEL_GRAY)
        fig.subplots_adjust(left=0.01, right=0.99, top=0.97, bottom=0.07,
                            wspace=0.04)
        path = OUT_DIR / "t3-prism-replicate-sne-plate-maps.png"
        fig.savefig(path, dpi=FIGURE_DPI, facecolor="white")
        plt.close(fig)
    return path


def render_3dran_plate_map(key3: list[dict], src3: dict) -> Path:
    """No wipe tower on this map: the round-3 project still carries the
    profile default (x = 15 mm), which the GUI dealt with when drran and
    2dran were printed, so the file does not say where it actually went."""
    with plt.rc_context({**FIG_RC, "font.size": 12}):
        fig, ax = plt.subplots(figsize=(8.2, 8.3), dpi=FIGURE_DPI)
        _plate_axes(ax, "3dran plate (third print of drran and 2dran)")
        for k in key3:
            art = src3["articles"][k["trial"]]
            verts = np.vstack([src3["meshes"][p["mesh_id"]]["verts"]
                               + p["trans"] + art["item"]
                               for p in art["parts"].values()])
            lo, hi = article_bbox(src3, art)
            cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
            ax.add_patch(Polygon(_hull(verts), closed=True, fc="#8d8c88",
                                 ec=INK, lw=1.0, alpha=0.25, zorder=2))
            ax.text(cx, cy + 6, k["id"], ha="center", va="center",
                    fontsize=17, fontweight="bold", color=INK, zorder=3)
            ax.text(cx, cy - 11, f"trial {k['trial']}\n= {k['drran']['print_id']}"
                    f", {k['2dran']['print_id']}", ha="center", va="center",
                    fontsize=10, color="#3d3d3a", zorder=3, linespacing=1.2)
        fig.text(0.5, 0.02, "Positions as laid out in the committed round-3 "
                 "project (3dranN is the same design as drranN and 2dranN).",
                 ha="center", fontsize=11, color=LABEL_GRAY)
        fig.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.07)
        path = OUT_DIR / "t3-prism-3dran-plate-map.png"
        fig.savefig(path, dpi=FIGURE_DPI, facecolor="white")
        plt.close(fig)
    return path


def render_picks_performance() -> Path:
    """The campaign's objective-space panel, cut down to the three picks.
    Measured first-article values (one article, one seating each); corny7 is
    filled because it sits on the campaign's current Pareto front."""
    picks = {r["print_id"]: r for r in csv.DictReader(PICKS_CSV.open())}
    xs = {k: float(v["meas_t180"]) for k, v in picks.items()}
    ys = {k: float(v["meas_e_reb_mJ"]) for k, v in picks.items()}
    with plt.rc_context(FIG_RC):
        fig, ax = plt.subplots(figsize=(11.0, 7.0), dpi=FIGURE_DPI)
        for d in DESIGNS:
            k = d["print_id"]
            on_front = d["role"] == "on the front"
            ax.scatter([xs[k]], [ys[k]], s=260, lw=2.4, ec=INK,
                       fc=FRONT_BLUE if on_front else "none", zorder=4)
        xticks = np.array([0.8, 0.9, 1.0, 1.1])
        yticks = np.arange(8.0, 18.1, 2.0)
        _style_axes(ax, xlim=(0.785, 1.12), ylim=(7.5, 18.6),
                    xticks=xticks, yticks=yticks)
        offsets = {"corny7": (16, 10), "corny8": (16, 8), "corny2": (-16, 16)}
        for d in DESIGNS:
            k = d["print_id"]
            dx, dy = offsets[k]
            ax.annotate(k, (xs[k], ys[k]), xytext=(dx, dy),
                        textcoords="offset points", fontsize=22,
                        color=LABEL_GRAY, ha="left" if dx > 0 else "right",
                        va="bottom", zorder=5)
        _callout(ax, "On the current Pareto front", (xs["corny7"], ys["corny7"]),
                 (0.10, 0.10), FRONT_BLUE)
        # below the x-axis label, as on the campaign Pareto figures
        fig.text(0.5, -0.1, "First article of each design (one print, one "
                 "accelerometer seating), round-4 drop sessions of "
                 "2026-09-12 and 2026-09-14.", ha="center", fontsize=14,
                 color=LABEL_GRAY)
        path = OUT_DIR / "t3-prism-replicate-picks-performance.png"
        fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight",
                    facecolor="white")
        plt.close(fig)
    return path


def _tower_xy(project_bytes: bytes) -> tuple[float, float]:
    cfg = project_bytes.decode()
    x = float(re.search(r'"wipe_tower_x": \[\s*"([^"]+)"', cfg).group(1))
    y = float(re.search(r'"wipe_tower_y": \[\s*"([^"]+)"', cfg).group(1))
    return x, y


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    src4 = parse_project(ROUND4_3MF)
    geo4 = verify_against_stls(src4, "round4", [d["trial"] for d in DESIGNS])
    m4 = manifest(ROUND4_MANIFEST)
    for d in DESIGNS:
        art, man = src4["articles"][d["trial"]], m4[d["trial"]]
        for kind, col in (("struts", "strut_infill_pct"),
                          ("cables", "tpu_infill_pct")):
            if art["parts"][kind]["infill"] != f"{int(man[col])}%":
                raise SystemExit(f"trial {d['trial']} {kind}: project infill "
                                 f"{art['parts'][kind]['infill']} vs manifest "
                                 f"{man[col]} %")
        print(f"==> {d['print_id']} = trial {d['trial']}: project mesh == "
              f"committed STLs; infill struts "
              f"{art['parts']['struts']['infill']} / cables "
              f"{art['parts']['cables']['infill']}")

    tower4 = _tower_xy(src4["contents"][PROJECT_FILE])
    layout = plan_replicate_layout(geo4, tower4[0])
    print(f"==> Layout: rows {layout['row_w_mm']:.1f} x "
          f"{layout['total_h_mm']:.1f} mm from x = {layout['left_mm']:.1f}; "
          f"wipe tower kept at {tower4}")
    for p, cells in layout["plates"].items():
        out = OUT_DIR / (f"t3-prism-replicate-sne-plate{p}."
                         "H2D-MM-PLAstruts-TPUcables.3mf")
        build_replicate_project(src4, cells, p, out)
        verify_replicate_project(out, cells, src4)
        rows = [" ".join(c["id"] for c in cells if c["row"] == r)
                for r in range(len(ROWS))]
        print(f"==> Plate {p}: {out.name} ({out.stat().st_size / 1e6:.1f} MB)"
              f"\n      back:   {rows[0]}\n      middle: {rows[1]}"
              f"\n      front:  {rows[2]}")

    key3 = load_3dran_key()
    out3 = OUT_DIR / "t3-prism-3dran.H2D-MM-PLAstruts-TPUcables.3mf"
    src3 = build_3dran_project(key3, out3)
    verify_against_stls(src3, "round3", [k["trial"] for k in key3])
    print(f"==> 3dran: {out3.name}; only object names differ from "
          f"{ROUND3_3MF.name}: "
          + ", ".join(f"{k['id']} = t{k['trial']}" for k in key3))

    copy_stls(key3)
    key_path = write_key(layout, key3, src3)
    maps = render_sne_plate_maps(layout, geo4, tower4)
    map3 = render_3dran_plate_map(key3, src3)
    perf = render_picks_performance()
    for path in (key_path, maps, map3, perf):
        print(f"==> wrote {path.relative_to(BO_DIR.parent)}")
    for path in sorted(OUT_DIR.glob("*.3mf")):
        print(f"    {path.name}: sha256 "
              f"{hashlib.sha256(path.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
