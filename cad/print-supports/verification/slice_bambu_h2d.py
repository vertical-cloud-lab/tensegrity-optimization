#!/usr/bin/env python3
"""Headless Bambu Studio CLI slice for the Bambu Lab H2D.

This is the verification driver behind the path-(a) and path-(c) previews in
this directory. It targets the actual production printer for this lab — a
Bambu Lab H2D with a 0.4 mm nozzle in single-material PLA mode — by pulling
the bundled `Bambu Lab H2D 0.4 nozzle` system machine profile, the
`0.20mm Standard @BBL H2D` process profile, and the `Bambu PLA Basic @BBL
H2D` filament profile straight out of the Bambu Studio AppImage's
``resources/profiles/BBL/`` directory, then overlaying the tensegrity
tweaks listed in ``cad/print-supports/bambu-pla-tensegrity-process.json``.

This is the **official** ``bambu-studio`` CLI shipped inside the Bambu
Studio AppImage (see https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage),
not a fork. The Ubuntu 24.04 build of the AppImage links
``libsoup-3.0`` / ``WebKit2GTK-4.1`` and runs cleanly under ``xvfb`` on
this lab's CI runner, so we can drive the genuine slicer headlessly.

(Note: the PyPI package ``bambu-cli`` is unrelated — it controls printers
over MQTT/HTTPS/FTPS using already-sliced files; it does not perform
slicing. Bambu Lab does not publish a Python slicing API; the supported
automation path is the AppImage CLI invoked as below.)

The script:

  1. Resolves the H2D profile inheritance chain by hand (the Bambu Studio
     CLI requires "a full config instead of the one used in
     resources/profiles/BBL/…", per the wiki) and writes the flattened
     machine / process / filament JSON to ``--workdir``.
  2. Applies the overrides from ``bambu-pla-tensegrity-process.json``
     (plus any extra ``--override KEY=VALUE`` flags) on top of the
     flattened process profile.
  3. Translates the input STL so its lowest vertex sits on z=0 (the slicer
     refuses parts whose bounding box dips below the bed).
  4. Invokes ``bambu-studio --arrange 1 --slice 0 --export-3mf …`` and
     copies the resulting ``plate_1.gcode`` out of the work directory.

Usage:

    slice_bambu_h2d.py path/to/BambuStudio.AppImage input.stl out.gcode \\
        [--override support_threshold_angle=40] \\
        [--workdir /tmp/h2d_workdir]

The ``BambuStudio.AppImage`` argument can be either the AppImage file
itself or an already-extracted ``squashfs-root`` directory (we look for
``bin/bambu-studio`` and ``resources/profiles/BBL/`` underneath it).
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


def write_flat_profiles(bambu_root: Path, workdir: Path,
                        overrides: dict[str, str]) -> tuple[Path, Path, Path]:
    """Flatten the Bambu H2D 0.4 nozzle profile chain into ``workdir`` and
    apply the tensegrity overrides on top of the process profile. Returns
    (process_path, machine_path, filament_path)."""
    bbl = bambu_root / "resources" / "profiles" / "BBL"
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


def extract_gcode(workdir: Path, project_3mf: Path, out_gcode: Path) -> None:
    """Locate the sliced plate gcode. Bambu Studio's CLI writes
    ``plate_1.gcode`` directly into ``--outputdir`` AND also embeds it
    inside the project 3MF at ``Metadata/plate_1.gcode``. Prefer the
    on-disk copy (saves a zip extract); fall back to the 3MF."""
    direct = workdir / "plate_1.gcode"
    if direct.is_file() and direct.stat().st_size > 0:
        shutil.copyfile(direct, out_gcode)
        return
    with zipfile.ZipFile(project_3mf) as z:
        gcode_names = [n for n in z.namelist()
                       if n.endswith(".gcode") and "/Metadata/" in "/" + n]
        if not gcode_names:
            raise RuntimeError(f"no gcode inside {project_3mf}")
        with z.open(gcode_names[0]) as src, out_gcode.open("wb") as dst:
            shutil.copyfileobj(src, dst)


def resolve_bambu_studio(arg: Path, workdir: Path) -> tuple[list[str], Path]:
    """Resolve --bambu-studio into (argv-prefix, resource-root).

    * If ``arg`` points at a directory containing ``bin/bambu-studio`` and
      ``resources/profiles/BBL/`` (an already-extracted ``squashfs-root``),
      use it directly.
    * Otherwise treat ``arg`` as the AppImage file itself and run it with
      ``--appimage-extract-and-run`` (the AppImage launcher handles the
      extraction once and caches it).

    Returns a tuple ``([prog, *flags], resource_root)`` ready to be
    prepended to the bambu-studio CLI arguments.
    """
    p = arg.resolve()
    if p.is_dir():
        bin_path = p / "bin" / "bambu-studio"
        if not bin_path.exists():
            sys.exit(f"{bin_path} not found — expected an extracted "
                     f"Bambu Studio squashfs-root directory")
        if not (p / "resources" / "profiles" / "BBL").is_dir():
            sys.exit(f"{p}/resources/profiles/BBL not found")
        return [str(bin_path)], p
    # AppImage file: extract once into workdir for the BBL profiles, and
    # invoke via the AppImage launcher.
    extract_dir = workdir / "bambu-studio-extracted"
    if not (extract_dir / "squashfs-root" / "resources" / "profiles"
            / "BBL").is_dir():
        extract_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(p), "--appimage-extract"],
                       check=True, cwd=extract_dir,
                       stdout=subprocess.DEVNULL)
    return [str(p), "--appimage-extract-and-run"], \
        extract_dir / "squashfs-root"


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bambu_studio", type=Path,
                    help="Path to the BambuStudio AppImage (e.g. "
                         "BambuStudio_ubuntu-24.04-*.AppImage) OR a "
                         "directory with an already-extracted "
                         "squashfs-root (contains bin/bambu-studio and "
                         "resources/profiles/BBL/).")
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

    workdir = args.workdir or args.out.with_suffix(".workdir")
    workdir.mkdir(parents=True, exist_ok=True)

    bs_prefix, bambu_root = resolve_bambu_studio(args.bambu_studio, workdir)

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

    proc_p, mach_p, fila_p = write_flat_profiles(bambu_root, workdir,
                                                  overrides)

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
    # Bambu Studio CLI also drops ``plate_1.gcode`` directly into outputdir
    # alongside the 3MF; clear any stale copy.
    plate_gcode = workdir / "plate_1.gcode"
    if plate_gcode.exists():
        plate_gcode.unlink()

    cmd = [
        "xvfb-run", "-a", *bs_prefix,
        # Tensegrity enforcer meshes are very thin (sub-nozzle-width in
        # places, by design); Bambu Studio's empty-layer check aborts on
        # them unless we explicitly allow it through.
        "--no-check=1",
        "--load-settings", f"{mach_p};{proc_p}",
        "--load-filaments", str(fila_p),
        "--arrange", "1",
        "--slice", "0",
        "--debug", "2",
        "--export-3mf", project_3mf.name,
        "--outputdir", str(workdir),
        str(onbed),
    ]
    print("running:", " ".join(cmd), file=sys.stderr)
    # Some Bambu Studio CLI subcommands resolve --export-3mf relative to
    # cwd, so run from the workdir.
    res = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True)
    # Bambu Studio sometimes returns non-zero (e.g. from a post-slice
    # thumbnail step that tries to open Wayland) even when the gcode was
    # produced; trust the existence of plate_1.gcode/3MF as success.
    have_gcode = (workdir / "plate_1.gcode").exists() or project_3mf.exists()
    if not have_gcode:
        sys.stderr.write(res.stdout[-4000:])
        sys.stderr.write(res.stderr[-4000:])
        sys.exit(f"bambu-studio failed with code {res.returncode}")

    extract_gcode(workdir, project_3mf, args.out)
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
