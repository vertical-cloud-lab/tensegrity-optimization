#!/usr/bin/env python3
"""Convert a sliced .gcode file back into STL mesh(es) so the print can be
previewed in any STL viewer / mesh editor.

This is the closest thing to "show me exactly what's getting printed" you
can do without a printer attached: every G1 extrusion move is reified as
a short rectangular prism centered on the toolpath, layer-height tall and
extrusion-width wide. Each segment is then welded into a single binary
STL.

Per-feature filtering is supported via ``--features``, so you can extract
**only the support material** as its own STL (and load it into any viewer
to see exactly which surfaces are being held up, and how dense the
support coverage is) — which is the workflow this tool was added for.

Usage
-----

    # Everything (object + supports + brim) → one STL:
    gcode_to_stl.py plate.gcode all.stl

    # Supports + support interface only:
    gcode_to_stl.py plate.gcode supports.stl --features Support "Support interface"

    # Just the object (no supports, no brim):
    gcode_to_stl.py plate.gcode object.stl --object-only

    # Emit one STL per kind in one go (no second invocation needed):
    gcode_to_stl.py plate.gcode out_prefix --split

The triangle count is roughly ``8 × N_segments`` (one rectangular box of 12
triangles per extrusion, minus the 2 hidden bottom faces) which for a
typical T3-prism slice is around 100k–200k triangles per part.
"""
from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

import numpy as np


# Default layer height and line width if the slicer's header doesn't tell
# us — these match Bambu Studio's "0.20mm Standard @BBL H2D 0.4 nozzle"
# defaults and act as a safe fallback only.
DEFAULT_LAYER_HEIGHT_MM = 0.20
DEFAULT_LINE_WIDTH_MM = 0.42
# Numerical tolerances. EXTRUSION_EPS: distinguishes a real travel/extrude
# move from numerical noise (mm in XY, mm of filament for E). NORMAL_EPS:
# guards against dividing by a degenerate-triangle normal length.
EXTRUSION_EPS = 1e-9
NORMAL_EPS = 1e-12


# Slicer feature → coarse "kind" buckets we let users select on the CLI.
# Names come from PrusaSlicer (";TYPE:") and Bambu Studio / OrcaSlicer
# (";FEATURE:") gcode comments — both are parsed by this script.
FEATURE_TO_KIND = {
    # PrusaSlicer feature names
    "Skirt/Brim":                 "brim",
    "External perimeter":         "object",
    "Perimeter":                  "object",
    "Internal infill":            "object",
    "Solid infill":               "object",
    "Top solid infill":           "object",
    "Bridge infill":              "object",
    "Overhang perimeter":         "object",
    "Support material":           "support",
    "Support material interface": "support_interface",
    # Bambu Studio / OrcaSlicer feature names
    "Brim":                       "brim",
    "Outer wall":                 "object",
    "Inner wall":                 "object",
    "Sparse infill":              "object",
    "Internal solid infill":      "object",
    "Top surface":                "object",
    "Bottom surface":             "object",
    "Bridge":                     "object",
    "Internal Bridge":            "object",
    "Overhang wall":              "object",
    "Floating vertical shell":    "object",
    "Gap infill":                 "object",
    "Support":                    "support",
    "Support interface":          "support_interface",
    # Anything else (Custom, Wipe, etc.) is ignored.
}

# Pre-built regex once.
_G1_RE = re.compile(
    r"^G[01]\b"
    r"(?:[^;]*?\bX(?P<x>-?\d*\.?\d+))?"
    r"(?:[^;]*?\bY(?P<y>-?\d*\.?\d+))?"
    r"(?:[^;]*?\bZ(?P<z>-?\d*\.?\d+))?"
    r"(?:[^;]*?\bE(?P<e>-?\d*\.?\d+))?")


def parse_segments(gcode_path: Path, want_kinds: set[str] | None,
                   layer_height: float, line_width: float
                   ) -> dict[str, list[tuple[np.ndarray, np.ndarray, float]]]:
    """Return ``{kind: [(p0, p1, layer_z), …]}``.

    p0, p1 are XY (np.array, len 2). ``layer_z`` is the absolute Z (top of
    the layer); the box for the segment extends from ``layer_z -
    layer_height`` to ``layer_z``."""
    out: dict[str, list[tuple[np.ndarray, np.ndarray, float]]] = {}
    cur_x = cur_y = cur_z = 0.0
    cur_e = 0.0
    absolute_e = True   # M82 / M83 control this; default absolute for safety
    cur_kind: str | None = None
    cur_layer_z = 0.0   # Bambu emits "; Z_HEIGHT: …" before each layer

    with gcode_path.open() as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line:
                continue
            if line[0] == ";":
                # Comment / metadata.
                stripped = line[1:].strip()
                if stripped.startswith("FEATURE:") or \
                        stripped.startswith("TYPE:"):
                    feat = stripped.split(":", 1)[1].strip()
                    cur_kind = FEATURE_TO_KIND.get(feat)
                elif stripped.startswith("Z_HEIGHT:") or \
                        stripped.startswith("LAYER_Z:"):
                    try:
                        cur_layer_z = float(stripped.split(":", 1)[1].strip())
                    except ValueError:
                        pass
                continue
            if line.startswith("M82"):
                absolute_e = True
                continue
            if line.startswith("M83"):
                absolute_e = False
                continue
            if line.startswith("G92"):
                # G92 E0 resets the extruder origin.
                m = re.search(r"\bE(-?\d*\.?\d+)", line)
                if m:
                    cur_e = float(m.group(1))
                m = re.search(r"\bZ(-?\d*\.?\d+)", line)
                if m:
                    cur_z = float(m.group(1))
                continue
            m = _G1_RE.match(line)
            if not m:
                continue
            new_x = float(m.group("x")) if m.group("x") else cur_x
            new_y = float(m.group("y")) if m.group("y") else cur_y
            new_z = float(m.group("z")) if m.group("z") else cur_z
            e_raw = m.group("e")
            extruded = False
            if e_raw is not None:
                e_val = float(e_raw)
                if absolute_e:
                    if e_val > cur_e + EXTRUSION_EPS:
                        extruded = True
                    cur_e = e_val
                else:
                    if e_val > EXTRUSION_EPS:
                        extruded = True
            # If the move travels in XY and we have positive extrusion,
            # treat it as a printed segment.
            if extruded and cur_kind is not None and \
                    want_kinds is not None and cur_kind in want_kinds and \
                    (abs(new_x - cur_x) > EXTRUSION_EPS or abs(new_y - cur_y) > EXTRUSION_EPS):
                z_top = cur_layer_z if cur_layer_z > 0 else new_z
                out.setdefault(cur_kind, []).append((
                    np.array([cur_x, cur_y], dtype=np.float64),
                    np.array([new_x, new_y], dtype=np.float64),
                    z_top,
                ))
            cur_x, cur_y, cur_z = new_x, new_y, new_z
    return out


def segments_to_triangles(segments: list[tuple[np.ndarray, np.ndarray, float]],
                          layer_height: float, line_width: float
                          ) -> np.ndarray:
    """Reify each extrusion segment as an oriented box and return an
    ``(N, 3, 3)`` triangle array. Each box is 12 triangles."""
    if not segments:
        return np.zeros((0, 3, 3), dtype=np.float32)
    n = len(segments)
    p0 = np.array([s[0] for s in segments], dtype=np.float64)   # (n, 2)
    p1 = np.array([s[1] for s in segments], dtype=np.float64)   # (n, 2)
    z_top = np.array([s[2] for s in segments], dtype=np.float64)
    z_bot = np.maximum(z_top - layer_height, 0.0)
    d = p1 - p0
    L = np.maximum(np.linalg.norm(d, axis=1, keepdims=True), EXTRUSION_EPS)
    t = d / L                                                   # along-axis
    nrm = np.stack([-t[:, 1], t[:, 0]], axis=1)                 # perp xy
    half = line_width * 0.5
    # 8 corners per box (CCW bottom, CCW top).
    cA = p0 + nrm * half
    cB = p0 - nrm * half
    cC = p1 - nrm * half
    cD = p1 + nrm * half
    A_b = np.concatenate([cA, z_bot[:, None]], axis=1)
    B_b = np.concatenate([cB, z_bot[:, None]], axis=1)
    C_b = np.concatenate([cC, z_bot[:, None]], axis=1)
    D_b = np.concatenate([cD, z_bot[:, None]], axis=1)
    A_t = np.concatenate([cA, z_top[:, None]], axis=1)
    B_t = np.concatenate([cB, z_top[:, None]], axis=1)
    C_t = np.concatenate([cC, z_top[:, None]], axis=1)
    D_t = np.concatenate([cD, z_top[:, None]], axis=1)
    # 12 triangles per box, CCW outward.
    tris = np.empty((n, 12, 3, 3), dtype=np.float64)
    # Top (+Z): A_t B_t C_t, A_t C_t D_t
    tris[:, 0] = np.stack([A_t, B_t, C_t], axis=1)
    tris[:, 1] = np.stack([A_t, C_t, D_t], axis=1)
    # Bottom (-Z): reversed winding A_b D_b C_b, A_b C_b B_b
    tris[:, 2] = np.stack([A_b, D_b, C_b], axis=1)
    tris[:, 3] = np.stack([A_b, C_b, B_b], axis=1)
    # +nrm side (A): A_b A_t B_t, A_b B_t B_b   (between A and B)
    # actually we want the 4 side faces between consecutive corner pairs
    # going CCW around the loop A → B → C → D → A.
    def side(P_b, P_t, Q_b, Q_t):
        return np.stack([P_b, P_t, Q_t], axis=1), \
               np.stack([P_b, Q_t, Q_b], axis=1)
    tris[:, 4], tris[:, 5] = side(A_b, A_t, B_b, B_t)
    tris[:, 6], tris[:, 7] = side(B_b, B_t, C_b, C_t)
    tris[:, 8], tris[:, 9] = side(C_b, C_t, D_b, D_t)
    tris[:, 10], tris[:, 11] = side(D_b, D_t, A_b, A_t)
    return tris.reshape(-1, 3, 3).astype(np.float32)


def write_binary_stl(tris: np.ndarray, out_path: Path) -> None:
    """Write an ``(N, 3, 3)`` triangle array as binary STL."""
    n = tris.shape[0]
    with out_path.open("wb") as f:
        f.write(b"\0" * 80)
        f.write(struct.pack("<I", n))
        if n == 0:
            return
        # Per-triangle normal.
        v0 = tris[:, 0]
        v1 = tris[:, 1]
        v2 = tris[:, 2]
        nrm = np.cross(v1 - v0, v2 - v0)
        norms = np.linalg.norm(nrm, axis=1, keepdims=True)
        nrm = np.where(norms > NORMAL_EPS, nrm / np.maximum(norms, NORMAL_EPS), 0.0)
        # Pack each triangle: 12 floats + uint16 attribute byte count.
        buf = bytearray(50 * n)
        for i in range(n):
            struct.pack_into("<12fH", buf, i * 50,
                             nrm[i, 0], nrm[i, 1], nrm[i, 2],
                             v0[i, 0], v0[i, 1], v0[i, 2],
                             v1[i, 0], v1[i, 1], v1[i, 2],
                             v2[i, 0], v2[i, 1], v2[i, 2],
                             0)
        f.write(buf)


def derive_layer_and_width(gcode_path: Path) -> tuple[float, float]:
    """Pull layer_height and line_width out of the gcode header."""
    lh = DEFAULT_LAYER_HEIGHT_MM
    lw = DEFAULT_LINE_WIDTH_MM
    with gcode_path.open() as f:
        for line in f:
            if not line.startswith(";"):
                # We only look at the header; G-code body is ignored here.
                break
            if "layer_height" in line and "=" in line:
                try:
                    lh = float(line.split("=", 1)[1].split(",")[0].strip())
                except ValueError:
                    pass
            for key in ("support_line_width", "line_width", "extrusion_width",
                        "default_extrusion_width"):
                if line.lstrip("; ").startswith(key + " ") and "=" in line:
                    try:
                        v = line.split("=", 1)[1].split(",")[0].strip()
                        # Bambu emits things like "0.42" or "100%"; ignore %.
                        if not v.endswith("%"):
                            lw = float(v)
                    except ValueError:
                        pass
    return lh, lw


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("gcode", type=Path)
    ap.add_argument("out", type=Path,
                    help="Output STL path, OR an output prefix (without "
                         "suffix) when --split is given.")
    ap.add_argument("--features", nargs="*", default=None,
                    help="Slicer feature names to include (PrusaSlicer "
                         "TYPE or Bambu/Orca FEATURE names). Defaults to "
                         "all kinds.")
    ap.add_argument("--support-only", action="store_true",
                    help="Shorthand: --features Support 'Support interface' "
                         "'Support material' 'Support material interface'.")
    ap.add_argument("--object-only", action="store_true",
                    help="Shorthand: every object-kind extrusion, no "
                         "supports, no brim.")
    ap.add_argument("--split", action="store_true",
                    help="Emit one STL per kind: <out>-supports.stl, "
                         "<out>-object.stl, <out>-brim.stl (only the kinds "
                         "actually present).")
    ap.add_argument("--layer-height", type=float, default=None,
                    help="Override layer height (mm) used for the box "
                         "extrusion (default: parsed from gcode header).")
    ap.add_argument("--line-width", type=float, default=None,
                    help="Override extrusion line width (mm) used for the "
                         "box extrusion (default: parsed from gcode "
                         "header, fallback 0.42).")
    args = ap.parse_args()

    if args.support_only and args.object_only:
        sys.exit("--support-only and --object-only are mutually exclusive")

    # Resolve which kinds to keep.
    all_kinds = {"object", "support", "support_interface", "brim"}
    if args.support_only:
        want_kinds = {"support", "support_interface"}
    elif args.object_only:
        want_kinds = {"object"}
    elif args.features:
        want_kinds = {FEATURE_TO_KIND[f]
                      for f in args.features if f in FEATURE_TO_KIND}
        if not want_kinds:
            sys.exit(f"none of {args.features!r} matched a known feature "
                     f"name; valid names: {sorted(FEATURE_TO_KIND)}")
    else:
        want_kinds = all_kinds

    lh, lw = derive_layer_and_width(args.gcode)
    if args.layer_height is not None:
        lh = args.layer_height
    if args.line_width is not None:
        lw = args.line_width
    print(f"  layer_height = {lh:.3f} mm, line_width = {lw:.3f} mm",
          file=sys.stderr)

    by_kind = parse_segments(args.gcode, want_kinds, lh, lw)
    counts = {k: len(v) for k, v in by_kind.items()}
    print(f"  parsed segments: {counts}", file=sys.stderr)

    if args.split:
        # out is treated as a prefix; emit one STL per non-empty kind.
        for kind, segs in by_kind.items():
            tris = segments_to_triangles(segs, lh, lw)
            out_path = args.out.with_name(args.out.name + f"-{kind}.stl")
            write_binary_stl(tris, out_path)
            print(f"wrote {out_path} ({tris.shape[0]} triangles)",
                  file=sys.stderr)
    else:
        all_segs = [s for segs in by_kind.values() for s in segs]
        tris = segments_to_triangles(all_segs, lh, lw)
        write_binary_stl(tris, args.out)
        print(f"wrote {args.out} ({tris.shape[0]} triangles, "
              f"{args.out.stat().st_size} bytes)", file=sys.stderr)


if __name__ == "__main__":
    main()
