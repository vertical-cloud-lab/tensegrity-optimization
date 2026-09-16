"""Read the print-process settings out of a Bambu Studio .3mf project.

Why this exists
---------------
Six slicer settings became BO design variables on 2026-08-26 (PR #102):
the sparse infill density of the strut (PLA) and cable (TPU) parts, and the
nozzle temperature and max volumetric speed of each filament. Their values for
the two tested batches are hard-coded as ``AS_PRINTED_PROCESS`` in
``t3_prism_bo_campaign.py``, and a hard-coded constant that nobody can check is
how a campaign ends up arguing about what it printed. This module reads the
same numbers back out of the project files, so the constant is auditable:

    python bo/t3_prism_slicer_settings.py bo/slices/*.3mf

It is also what round 4 should use on the round-3 plates. The suggestions CSV
records what the batch was *asked* to print at; the .3mf records what it was
*sliced* at, and only the second one is a measurement (facebook/Ax#3577,
planned versus executed parameters).

What it reads
-------------
``Metadata/project_settings.config`` is JSON. Process-level fields
(``layer_height``, ``sparse_infill_density``, ``wall_loops``, ...) are plain
scalars. Filament-level fields are arrays, and their length is not the slot
count: Bambu stores one entry per (filament, nozzle) combination that exists,
which on the H2D was 12 entries for 6 slots in one project and 3 entries for 2
slots in another. ``nozzle_temperature_range_low`` / ``_high`` *are* per slot,
so the mapping used here is to take each slot's temperature as the value in
that slot's own vendor window, preferring one that no other slot's window
admits. On both committed projects that is unambiguous (PLA 220 C, TPU 240 C),
and ``--raw`` prints the arrays so a future project can be checked by eye if it
is not.

``Metadata/model_settings.config`` is XML, one ``<object>`` per specimen with
one ``<part>`` per material. Per-object and per-part overrides live there as
``<metadata key="sparse_infill_density" .../>`` entries; neither tested plate
has any, which is exactly why the two infill percentages had never been chosen.
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pandas as pd

PROCESS_FIELDS = [
    "print_settings_id", "printer_settings_id", "layer_height", "line_width",
    "sparse_infill_density", "sparse_infill_pattern", "wall_loops",
    "top_shell_layers", "bottom_shell_layers",
]
OVERRIDE_KEYS = ("sparse_infill_density", "sparse_infill_pattern", "wall_loops",
                 "layer_height")


def _floats(values):
    out = []
    for v in values:
        try:
            out.append(float(v))
        except (TypeError, ValueError):
            pass
    return out


def _slot_block(values, n_slots, i):
    """The entries belonging to slot ``i``, when the array divides evenly.

    Bambu stores one entry per (filament, nozzle) pair that exists, so a
    project with 6 slots on a 2-nozzle machine carries 12 entries in slot
    order. When the array does not divide evenly (one project here has 3
    entries for 2 slots) there is nothing to key on and this returns the whole
    array for the caller to filter on value instead.
    """
    if not values or n_slots <= 0 or len(values) % n_slots:
        return list(values)
    per = len(values) // n_slots
    return list(values[i * per:(i + 1) * per])


def used_extruders(model_xml: str) -> set[int]:
    """Extruder numbers any object or part on the plate actually prints with."""
    root = ET.fromstring(model_xml)
    used = set()
    for node in root.iter():
        for md in node.findall("metadata"):
            if md.get("key") == "extruder":
                try:
                    used.add(int(md.get("value", "")))
                except ValueError:
                    pass
    return used


def filament_slots(settings: dict, used: set[int] | None = None) -> list[dict]:
    """One row per filament slot: type, preset, temperature, volumetric cap."""
    types = settings.get("filament_type", [])
    n = len(types)
    presets = settings.get("filament_settings_id", [""] * n)
    lows = _floats(settings.get("nozzle_temperature_range_low", []))
    highs = _floats(settings.get("nozzle_temperature_range_high", []))
    temps = _floats(settings.get("nozzle_temperature", []))
    flows = _floats(settings.get("filament_max_volumetric_speed", []))
    windows = list(zip(lows, highs))

    rows = []
    for i, kind in enumerate(types):
        lo, hi = windows[i] if i < len(windows) else (float("-inf"), float("inf"))
        # temperatures this slot's vendor window admits, most specific first:
        # a value no other slot's window admits identifies the slot outright
        mine = [t for t in _slot_block(temps, n, i) if lo <= t <= hi]
        unique = [t for t in mine
                  if not any(l <= t <= h for j, (l, h) in enumerate(windows)
                             if j != i)]
        temp = (unique or mine or [float("nan")])[0]
        # TPU runs an order of magnitude slower than PLA, so the volumetric
        # caps separate on size even when the slot blocks do not divide
        soft = str(kind).upper().startswith("TPU")
        candidates = [f for f in _slot_block(flows, n, i) if (f < 10.0) == soft]
        rows.append({
            "slot": i + 1,
            "filament_type": kind,
            "preset": str(presets[i] if i < len(presets) else "").split("(")[0],
            "nozzle_temp_C": temp,
            "temp_window_C": f"{lo:g}-{hi:g}" if windows else "",
            "max_volumetric_mm3_s": min(candidates) if candidates else float("nan"),
            "used_on_plate": (i + 1) in used if used is not None else None,
        })
    return rows


def part_overrides(model_xml: str) -> list[dict]:
    """Per-object and per-part slicer overrides, if the project carries any."""
    root = ET.fromstring(model_xml)
    rows = []
    for obj in root.findall("object"):
        obj_name = ""
        for md in obj.findall("metadata"):
            if md.get("key") == "name":
                obj_name = md.get("value", "")
        scopes = [("object", obj_name, obj)]
        scopes += [("part", next((md.get("value", "")
                                  for md in part.findall("metadata")
                                  if md.get("key") == "name"), ""), part)
                   for part in obj.findall("part")]
        for scope, name, node in scopes:
            for md in node.findall("metadata"):
                if md.get("key") in OVERRIDE_KEYS:
                    rows.append({"object": obj_name, "scope": scope,
                                 "name": name, "setting": md.get("key"),
                                 "value": md.get("value")})
    return rows


def read_project(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        settings = json.loads(z.read("Metadata/project_settings.config"))
        model = z.read("Metadata/model_settings.config").decode("utf-8")
    return {
        "path": path,
        "process": {k: settings.get(k) for k in PROCESS_FIELDS},
        "filaments": filament_slots(settings, used_extruders(model)),
        "overrides": part_overrides(model),
        "raw": settings,
    }


def report(project: dict, raw: bool = False) -> str:
    lines = [str(project["path"]), "=" * 78]
    lines += [f"  {k}: {v}" for k, v in project["process"].items()]
    lines.append("  filaments (a slot no object prints with is marked unused, "
                 "and its values mean nothing):")
    for row in project["filaments"]:
        mark = "" if row["used_on_plate"] in (True, None) else "  [unused]"
        lines.append(
            f"    slot {row['slot']}  {row['filament_type']:<4} "
            f"{row['nozzle_temp_C']:.0f} C (window {row['temp_window_C']}), "
            f"{row['max_volumetric_mm3_s']:.1f} mm^3/s   {row['preset']}{mark}"
        )
    if project["overrides"]:
        lines.append("  per-object / per-part overrides:")
        for row in project["overrides"]:
            lines.append(f"    {row['object']} / {row['scope']} {row['name']}: "
                         f"{row['setting']} = {row['value']}")
    else:
        lines.append("  per-object / per-part overrides: none, so every part "
                     "inherits the one global sparse infill density")
    if raw:
        lines.append("  raw filament arrays:")
        for key in ("nozzle_temperature", "nozzle_temperature_range_low",
                    "nozzle_temperature_range_high",
                    "filament_max_volumetric_speed", "filament_type"):
            lines.append(f"    {key}: {project['raw'].get(key)}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("projects", nargs="+", type=Path, help=".3mf project files")
    ap.add_argument("--csv", type=Path, default=None,
                    help="also write one tidy row per (project, filament slot)")
    ap.add_argument("--raw", action="store_true",
                    help="print the raw filament arrays behind the mapping")
    args = ap.parse_args(argv)

    rows = []
    for path in args.projects:
        project = read_project(path)
        print(report(project, raw=args.raw))
        print()
        for row in project["filaments"]:
            rows.append({"project": path.name, **project["process"], **row,
                         "n_part_overrides": len(project["overrides"])})
    if args.csv:
        pd.DataFrame(rows).to_csv(args.csv, index=False)
        print(f"Wrote {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
