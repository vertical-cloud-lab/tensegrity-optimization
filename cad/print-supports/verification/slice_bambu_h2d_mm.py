#!/usr/bin/env python3
"""Headless multi-material PLA+TPU slice for the Bambu Lab H2D via the
patched ``vertical-cloud-lab/BambuStudio`` CLI (PR #2).

This is the multi-material counterpart to ``slice_bambu_h2d.py``. The
upstream ``bambu-studio`` CLI shipped in the Bambu Studio AppImage hard-
crashes with an out-of-bounds read on filament-map indexing as soon as you
ask it to slice a 2-filament 3MF on a single-extruder system profile.
``vertical-cloud-lab/BambuStudio`` PR #2 ships a fixed binary plus a
``slice-inputs`` bundle (flattened machine / process / filament profiles
for the stock H2D 0.4-nozzle system + a 2-part PLA-struts + TPU-cables
template 3MF) we drive directly from here.

The script:

  1. Calls ``build_mm_pillars_3mf.py`` to inject the manually-baked
     narrowing pillars (output of ``generate_support_pillars.py --stl``)
     as a third PLA-assigned part on top of the template 3MF.
  2. Invokes the patched ``bambu-studio --slice 0`` CLI under ``xvfb-run``
     against the flattened H2D 0.4-nozzle profile bundle.
  3. Copies the resulting ``plate_1.gcode`` out of the slicer's working
     directory.

Usage:

    slice_bambu_h2d_mm.py \\
        --bambu-bin /path/to/bambu-studio \\
        --ld-library /path/to/destdir/usr/local/lib \\
        --slice-inputs /path/to/slice-inputs \\
        --pillars-stl t3-prism-pr35-pillars.stl \\
        --out plate_1.gcode

The patched CLI logs a number of harmless
``get_extruder_variant_string, unsupported NozzleVolumeType=2`` errors
during slicing and exits with a non-zero status from a downstream
print-validation step, but it still writes a complete, valid
``plate_1.gcode`` (verified header: ``; filament: 1,2``, both filament
lengths > 0). We pass ``--no-check`` to silence the validation step and
treat a present, non-empty ``plate_1.gcode`` as success regardless of
exit code.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD_MM_3MF = HERE / "build_mm_pillars_3mf.py"


def find_one(root: Path, pattern: str) -> Path:
    matches = sorted(root.rglob(pattern))
    if not matches:
        raise SystemExit(f"slice-inputs bundle is missing {pattern!r} under {root}")
    return matches[0]


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--bambu-bin", required=True, type=Path,
                    help="Path to the patched bambu-studio binary "
                         "(vertical-cloud-lab/BambuStudio PR #2 build, "
                         "typically BambuStudio/bin/bambu-studio inside the "
                         "extracted CLI artifact).")
    ap.add_argument("--ld-library", type=Path, default=None,
                    help="Optional LD_LIBRARY_PATH for the bundled runtime "
                         "deps (destdir/usr/local/lib in the deps artifact). "
                         "Required if those libs aren't installed system-wide.")
    ap.add_argument("--slice-inputs", required=True, type=Path,
                    help="Path to the slice-inputs bundle from "
                         "vertical-cloud-lab/BambuStudio PR #2 (contains the "
                         "flattened H2D 0.4-nozzle machine + process + Bambu "
                         "PLA Basic + Bambu TPU 85A profile JSONs and the "
                         "PLA-struts + TPU-cables template 3MF).")
    ap.add_argument("--pillars-stl", required=True, type=Path,
                    help="Narrowing-pillar STL produced by "
                         "generate_support_pillars.py --stl ... .")
    ap.add_argument("--template-3mf", default=None, type=Path,
                    help="Override the template 3MF (default: auto-discover "
                         "the *.single.3mf under --slice-inputs).")
    ap.add_argument("--machine-json", default=None, type=Path)
    ap.add_argument("--process-json", default=None, type=Path)
    ap.add_argument("--pla-filament-json", default=None, type=Path)
    ap.add_argument("--tpu-filament-json", default=None, type=Path)
    ap.add_argument("--out", required=True, type=Path,
                    help="Where to write the resulting plate_1.gcode.")
    ap.add_argument("--workdir", type=Path, default=None,
                    help="Persistent working directory (default: a temp dir).")
    ap.add_argument("--keep-3mf", type=Path, default=None,
                    help="If given, also copy the built 3-part 3MF to this path.")
    args = ap.parse_args()

    template = args.template_3mf or find_one(args.slice_inputs, "*.single.3mf")
    machine = args.machine_json or find_one(args.slice_inputs, "machine/*.json")
    process = args.process_json or find_one(args.slice_inputs, "process/*.json")
    pla_fil = args.pla_filament_json or find_one(args.slice_inputs, "filament/*PLA*.json")
    tpu_fil = args.tpu_filament_json or find_one(args.slice_inputs, "filament/*TPU*.json")

    cleanup = args.workdir is None
    work = args.workdir or Path(tempfile.mkdtemp(prefix="h2d-mm-"))
    work.mkdir(parents=True, exist_ok=True)
    try:
        mm_3mf = work / "input-with-pillars.3mf"
        subprocess.run([
            sys.executable, str(BUILD_MM_3MF),
            "--template", str(template),
            "--pillars-stl", str(args.pillars_stl),
            "--out", str(mm_3mf),
        ], check=True)

        if args.keep_3mf:
            args.keep_3mf.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(mm_3mf, args.keep_3mf)

        outdir = work / "slicer-out"
        outdir.mkdir(exist_ok=True)
        # Wipe any stale plate_1.gcode from a previous run.
        stale = outdir / "plate_1.gcode"
        if stale.exists():
            stale.unlink()

        cmd = [
            "xvfb-run", "-a", str(args.bambu_bin),
            "--slice", "0",
            "--no-check",
            "--load-settings", f"{machine};{process}",
            "--load-filaments", f"{pla_fil};{tpu_fil}",
            "--outputdir", str(outdir),
            str(mm_3mf),
        ]
        env = os.environ.copy()
        if args.ld_library:
            env["LD_LIBRARY_PATH"] = (
                f"{args.ld_library}:{env.get('LD_LIBRARY_PATH', '')}".rstrip(":")
            )
        print("+", " ".join(cmd), file=sys.stderr)
        proc = subprocess.run(cmd, env=env)
        # Non-zero exit is expected — the validator complains about
        # NozzleVolumeType=2 even though the gcode is valid. Treat the
        # presence of a non-empty plate_1.gcode as the success signal.
        gcode = outdir / "plate_1.gcode"
        if not gcode.exists() or gcode.stat().st_size == 0:
            print(f"slicer exit={proc.returncode} and no plate_1.gcode was produced",
                  file=sys.stderr)
            sys.exit(proc.returncode or 1)

        args.out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(gcode, args.out)
        print(f"wrote {args.out} ({args.out.stat().st_size} bytes; "
              f"slicer exit={proc.returncode})", file=sys.stderr)
    finally:
        if cleanup:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
