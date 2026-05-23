#!/usr/bin/env python3
"""Headless OrcaSlicer (Bambu Studio fork) slice for the Bambu Lab H2D.

This is the verification driver behind the path-(a) and path-(c) previews in
this directory. It targets the actual production printer for this lab — a
Bambu Lab H2D with a 0.4 mm nozzle in single-material PLA mode — by pulling
OrcaSlicer's bundled `Bambu Lab H2D 0.4 nozzle` system machine profile, the
`0.20mm Standard @BBL H2D` process profile, and the `Bambu PLA Basic @BBL
H2D` filament profile, then overlaying the tensegrity tweaks listed in
``cad/print-supports/bambu-pla-tensegrity-process.json``.

We use OrcaSlicer rather than the official Bambu Studio AppImage because

* OrcaSlicer is a direct community fork of Bambu Studio (which is itself a
  fork of PrusaSlicer / Slic3r), sharing the same slicing engine, the same
  Bambu profile catalogue, and the same Bambu G-code dialect.
* OrcaSlicer ships a Linux AppImage that runs headlessly under xvfb without
  needing a desktop session, whereas the Bambu Studio Linux AppImage links
  libsoup-2.4 / WebKit2GTK-4.0 (deprecated on Ubuntu 24.04) and exits at
  startup. The OrcaSlicer profile catalogue ``resources/profiles/BBL/`` is
  imported verbatim from Bambu Studio so the H2D recipe transfers 1:1.

The script:

  1. Resolves the H2D profile inheritance chain by hand (OrcaSlicer's CLI
     does not walk ``inherits`` when a profile is loaded via
     ``--load-settings`` outside its system datadir) and writes the
     flattened machine / process / filament JSON to ``--workdir``.
  2. Applies the overrides from ``bambu-pla-tensegrity-process.json``
     (plus any extra ``--override KEY=VALUE`` flags) on top of the
     flattened process profile.
  3. Translates the input STL so its lowest vertex sits on z=0 (the slicer
     refuses parts whose bounding box dips below the bed).
  4. Invokes ``orca-slicer --arrange 1 --slice 0 --export-3mf …`` and
     extracts ``Metadata/plate_1.gcode`` from the sliced project.

Usage:

    slice_h2d.py path/to/orca-slicer-AppRun input.stl out.gcode \\
        [--override support_threshold_angle=40] \\
        [--workdir /tmp/h2d_workdir]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

REPO_OVERRIDES = (
    Path(__file__).resolve().parent.parent / "bambu-pla-tensegrity-process.json"
)


def flatten(start: Path, search_dir: Path) -> dict:
    """Walk the ``inherits`` chain of a Bambu/Orca profile JSON and return a
    flat dict with later (more-specific) keys overriding earlier ones."""
    chain = []
    cur: Path | None = start
    while cur is not None:
        with cur.open() as f:
            d = json.load(f)
        chain.append(d)
        parent = d.get("inherits")
        if not parent:
            break
        cand = search_dir / f"{parent}.json"
        if not cand.exists():
            break
        cur = cand
    merged: dict = {}
    skip = {"inherits", "instantiation", "from", "setting_id"}
    for src in reversed(chain):
        for k, v in src.items():
            if k in skip:
                continue
            merged[k] = v
    return merged


def lift_stl_to_bed(in_path: Path, out_path: Path) -> tuple[float, float, float]:
    """Translate a binary STL so its minimum Z vertex sits at z = 0."""
    data = in_path.read_bytes()
    n = struct.unpack_from("<I", data, 80)[0]
    # First pass: find min_z across all vertices.
    min_z = float("inf")
    off = 84
    for _ in range(n):
        floats = struct.unpack_from("<12f", data, off)
        for vi in (5, 8, 11):  # v1.z, v2.z, v3.z
            if floats[vi] < min_z:
                min_z = floats[vi]
        off += 50
    if min_z >= 0.0:
        # Already on or above the bed; nothing to do.
        shutil.copyfile(in_path, out_path)
        return (0.0, 0.0, 0.0)
    shift_z = -min_z
    out = bytearray(data[:84])
    off = 84
    for _ in range(n):
        rec = bytearray(data[off:off + 50])
        floats = list(struct.unpack("<12f", rec[0:48]))
        for vi in (5, 8, 11):
            floats[vi] += shift_z
        rec[0:48] = struct.pack("<12f", *floats)
        out.extend(rec)
        off += 50
    out_path.write_bytes(out)
    return (0.0, 0.0, shift_z)


def write_flat_profiles(orca_root: Path, workdir: Path,
                        overrides: dict[str, str]) -> tuple[Path, Path, Path]:
    """Flatten the Bambu H2D 0.4 nozzle profile chain into ``workdir`` and
    apply the tensegrity overrides on top of the process profile. Returns
    (process_path, machine_path, filament_path)."""
    bbl = orca_root / "resources" / "profiles" / "BBL"
    machine = flatten(bbl / "machine" / "Bambu Lab H2D 0.4 nozzle.json",
                      bbl / "machine")
    machine["type"] = "machine"
    machine["from"] = "system"
    machine["instantiation"] = "true"
    machine["name"] = "Bambu Lab H2D 0.4 nozzle"
    m_path = workdir / "h2d-machine.json"
    with m_path.open("w") as f:
        json.dump(machine, f, indent=2)

    process = flatten(bbl / "process" / "0.20mm Standard @BBL H2D.json",
                      bbl / "process")
    process["type"] = "process"
    process["from"] = "system"
    process["instantiation"] = "true"
    process["name"] = "0.20mm Standard @BBL H2D"
    for k, v in overrides.items():
        if k.startswith("_") or k in {"name", "from", "inherits", "type",
                                       "instantiation", "setting_id"}:
            continue
        process[k] = v
    p_path = workdir / "h2d-process.json"
    with p_path.open("w") as f:
        json.dump(process, f, indent=2)

    filament = flatten(bbl / "filament" / "Bambu PLA Basic @BBL H2D.json",
                       bbl / "filament")
    filament["type"] = "filament"
    filament["from"] = "system"
    filament["instantiation"] = "true"
    filament["name"] = "Bambu PLA Basic @BBL H2D"
    f_path = workdir / "h2d-filament.json"
    with f_path.open("w") as f:
        json.dump(filament, f, indent=2)
    return p_path, m_path, f_path


def extract_gcode(project_3mf: Path, out_gcode: Path) -> None:
    """Pull ``Metadata/plate_1.gcode`` out of an OrcaSlicer-sliced 3MF."""
    with zipfile.ZipFile(project_3mf) as z:
        gcode_names = [n for n in z.namelist()
                       if n.endswith(".gcode") and "/Metadata/" in "/" + n]
        if not gcode_names:
            raise RuntimeError(f"no gcode inside {project_3mf}")
        with z.open(gcode_names[0]) as src, out_gcode.open("wb") as dst:
            shutil.copyfileobj(src, dst)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("orca", type=Path,
                    help="Path to OrcaSlicer's AppRun (e.g. extracted "
                         "AppImage's ./AppRun) — see the README for how to "
                         "obtain the Ubuntu 24.04 nightly build.")
    ap.add_argument("input", type=Path,
                    help="Input STL (or 3MF) to slice.")
    ap.add_argument("out", type=Path,
                    help="Where to write the extracted plate_1.gcode.")
    ap.add_argument("--workdir", type=Path, default=None,
                    help="Scratch dir (default: <out>.workdir).")
    ap.add_argument("--override", action="append", default=[],
                    help="Extra process override KEY=VALUE (repeatable). "
                         "These stack on top of "
                         "bambu-pla-tensegrity-process.json.")
    ap.add_argument("--no-repo-overrides", action="store_true",
                    help="Slice with the unmodified Bambu H2D Standard "
                         "process profile (no tensegrity tweaks).")
    args = ap.parse_args()

    orca_root = args.orca.resolve().parent
    if not (orca_root / "resources" / "profiles" / "BBL").is_dir():
        sys.exit(f"could not find OrcaSlicer BBL profiles under {orca_root}")

    workdir = args.workdir or args.out.with_suffix(".workdir")
    workdir.mkdir(parents=True, exist_ok=True)

    if args.no_repo_overrides:
        overrides: dict[str, str] = {}
    else:
        with REPO_OVERRIDES.open() as f:
            overrides = {k: v for k, v in json.load(f).items()
                         if not k.startswith("_")}
    for kv in args.override:
        if "=" not in kv:
            sys.exit(f"--override expects KEY=VALUE, got {kv!r}")
        k, v = kv.split("=", 1)
        overrides[k] = v

    proc_p, mach_p, fila_p = write_flat_profiles(orca_root, workdir, overrides)

    onbed = args.input
    if args.input.suffix.lower() == ".stl":
        onbed = workdir / (args.input.stem + "-onbed.stl")
        shift = lift_stl_to_bed(args.input, onbed)
        if shift != (0.0, 0.0, 0.0):
            print(f"  lifted {args.input.name} by {shift[2]:.3f} mm to put "
                  f"min_z = 0", file=sys.stderr)

    project_3mf = workdir / "sliced.3mf"
    if project_3mf.exists():
        project_3mf.unlink()

    cmd = [
        "xvfb-run", "-a", str(args.orca),
        "--datadir", str(workdir / "orca-data"),
        "--load-settings", f"{proc_p};{mach_p}",
        "--load-filaments", str(fila_p),
        "--arrange", "1",
        "--no-check",
        "--slice", "0",
        "--export-3mf", project_3mf.name,
        "--outputdir", str(workdir),
        str(onbed),
    ]
    print("running:", " ".join(cmd), file=sys.stderr)
    # Some OrcaSlicer subcommands resolve --export-3mf relative to cwd, so
    # run from the workdir.
    res = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True)
    if res.returncode != 0 or not project_3mf.exists():
        sys.stderr.write(res.stdout[-4000:])
        sys.stderr.write(res.stderr[-4000:])
        sys.exit(f"orca-slicer failed with code {res.returncode}")

    extract_gcode(project_3mf, args.out)
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
