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

import re
import sys
import zipfile


CFG_PATH = "Metadata/model_settings.config"
PART_SPLIT = re.compile(r"(<part [^>]*>.*?</part>)", re.DOTALL)
NAME_RE = re.compile(r'<metadata key="name" value="([^"]+)"\s*/>')
EXTRUDER_RE = re.compile(r'(<metadata key="extruder" value=")\d+(")')


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

    # Rewrite the archive in place, preserving member order/compression.
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in infos:
            zout.writestr(info, contents[info.filename])

    print(f"patched {target}: " + ", ".join(f"{k}->ext{v}" for k, v in mapping.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
