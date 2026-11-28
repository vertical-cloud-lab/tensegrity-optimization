#!/usr/bin/env python3
"""Patch per-part extruder assignment in a Bambu Studio project ``.3mf``.

BambuStudio CLI's ``--assemble`` merges several STLs into one object with
one ``<part>`` per STL, but it puts every part on extruder 1 by default
and does not honour ``--load-filament-ids`` or any per-part flag. For the
T3-prism multi-material variant (PLA struts + PETG cables) we patch the
resulting ``Metadata/model_settings.config`` after the fact so each
part gets the correct ``extruder`` metadata.

Usage::

    patch_mm_extruder.py PROJECT.3MF NAME=EXTRUDER_ID [NAME=EXTRUDER_ID ...]

Where ``NAME`` is the part's source STL filename (matched against the
``<metadata key="name" value="..."/>`` immediately after ``<part``) and
``EXTRUDER_ID`` is the 1-based extruder index.

This is a write-back-in-place edit: the ``.3mf`` is rewritten with the
patched ``Metadata/model_settings.config`` and every other entry copied
through unchanged.
"""
from __future__ import annotations

import json
import re
import sys
import zipfile


CFG_PATH = "Metadata/model_settings.config"
PROJ_PATH = "Metadata/project_settings.config"
PART_SPLIT = re.compile(r"(<part [^>]*>.*?</part>)", re.DOTALL)
NAME_RE = re.compile(r'<metadata key="name" value="([^"]+)"\s*/>')
EXTRUDER_RE = re.compile(r'(<metadata key="extruder" value=")\d+(")')

# Default per-extruder colours used when expanding a single-entry
# `filament_colour` array to match the actual filament count. Bambu Studio's
# default extruder palette in v02.06: green, cyan, yellow, magenta.
DEFAULT_COLOURS = ["#00AE42", "#76D9F4", "#F4EE2A", "#E94BAA"]


def patch(cfg: str, mapping: dict[str, str]) -> str:
    out = []
    for chunk in PART_SPLIT.split(cfg):
        if chunk.startswith("<part"):
            m = NAME_RE.search(chunk)
            if m and m.group(1) in mapping:
                ext = mapping[m.group(1)]
                if EXTRUDER_RE.search(chunk):
                    chunk = EXTRUDER_RE.sub(rf"\g<1>{ext}\g<2>", chunk)
                else:
                    # No existing extruder metadata — inject one before </part>.
                    chunk = chunk.replace(
                        "</part>",
                        f'      <metadata key="extruder" value="{ext}"/>\n    </part>',
                    )
        out.append(chunk)
    return "".join(out)


def patch_project_filaments(proj_json: bytes) -> bytes:
    """Expand the per-filament arrays in ``project_settings.config`` so they
    match the length of ``filament_settings_id``.

    BambuStudio CLI's ``--load-filaments a;b`` populates ``filament_settings_id``,
    ``filament_type``, and ``filament_ids`` with one entry per filament, but it
    leaves ``filament_colour`` and ``filament_map`` at their single-entry
    defaults (``['#00AE42']`` / ``['1']``). When Bambu Studio re-imports the
    project it uses the SHORTER of those arrays to determine how many filament
    slots the project occupies — the user sees a single PLA filament even
    though both filaments are configured (PR #35 comment 4464399849).

    Fix: pad ``filament_colour`` from ``DEFAULT_COLOURS`` and pad
    ``filament_map`` with ascending extruder indices (``['1', '2', ...]``).
    """
    d = json.loads(proj_json.decode())
    n = len(d.get("filament_settings_id", []))
    if n <= 1:
        return proj_json
    cols = list(d.get("filament_colour", []))
    while len(cols) < n:
        cols.append(DEFAULT_COLOURS[len(cols) % len(DEFAULT_COLOURS)])
    d["filament_colour"] = cols[:n]
    fmap = list(d.get("filament_map", []))
    while len(fmap) < n:
        fmap.append(str(len(fmap) + 1))
    d["filament_map"] = fmap[:n]
    # `filament_nozzle_map` tells Bambu Studio which *physical nozzle* each
    # filament is loaded into (1-based). BambuStudio CLI leaves this at the
    # single-entry default ``['1']`` after ``--load-filaments a;b``, which
    # causes the headless slice path to fail with "could not found
    # extruder_type Direct Drive, nozzle_volume_type Standard, filament_index
    # 2, extruder index 2" because filament 2 has no nozzle assignment.
    # Mirror ``filament_map`` (1, 2, 3, ...) so each filament is pinned to
    # the IDEX nozzle that the H2D loads it into.
    nmap = list(d.get("filament_nozzle_map", []))
    while len(nmap) < n:
        nmap.append(str(len(nmap) + 1))
    d["filament_nozzle_map"] = nmap[:n]
    # Switch from "Auto For Flush" to "Manual" so Bambu Studio honours the
    # explicit per-extruder map instead of trying to re-pack onto one nozzle
    # — IDEX H2D prints with one extruder per material, no flush tower needed.
    d["filament_map_mode"] = "Manual"
    return (json.dumps(d, indent=2) + "\n").encode()


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    target, *pairs = argv[1:]
    mapping: dict[str, str] = {}
    for p in pairs:
        if "=" not in p:
            print(f"bad NAME=EXT pair: {p!r}", file=sys.stderr)
            return 2
        name, ext = p.split("=", 1)
        mapping[name] = ext

    with zipfile.ZipFile(target, "r") as zin:
        infos = zin.infolist()
        contents = {info.filename: zin.read(info.filename) for info in infos}

    if CFG_PATH not in contents:
        print(f"{target}: missing {CFG_PATH}", file=sys.stderr)
        return 1

    cfg = contents[CFG_PATH].decode()
    new_cfg = patch(cfg, mapping)
    contents[CFG_PATH] = new_cfg.encode()

    if PROJ_PATH in contents:
        contents[PROJ_PATH] = patch_project_filaments(contents[PROJ_PATH])

    # Rewrite the archive in place, preserving member order/compression.
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in infos:
            zout.writestr(info, contents[info.filename])

    print(f"patched {target}: " + ", ".join(f"{k}->ext{v}" for k, v in mapping.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
