#!/usr/bin/env python3
"""Merge multiple binary STL files into one, with an optional per-input
translation. Useful for combining the support-only STL emitted by
:mod:`gcode_to_stl` with the source object STL so the printed part and
the supports the slicer will print under it can be inspected together in
any STL viewer.

Usage
-----

    # Plain concatenation (assumes inputs already share a coordinate frame):
    merge_stls.py out.stl part.stl supports.stl

    # Translate ``part.stl`` by (dx, dy, dz) mm before merging:
    merge_stls.py out.stl part.stl@10,5,0 supports.stl

    # Auto-align the first input so its XY bbox-center matches the
    # second input's XY bbox-center, and its lowest Z sits at z=0
    # (this is what the slicer does when it lays the object on the
    # build plate, so it brings a source mesh into the print-coordinate
    # frame of the gcode-derived support STL):
    merge_stls.py out.stl part.stl supports.stl --align-first-to-second

Binary STL format: 80-byte header, uint32 triangle count, then
``triangle_count × 50`` bytes (normal vec3 + 3 × vertex vec3 +
uint16 attribute).
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

import numpy as np


STL_HEADER_BYTES = 80
STL_TRI_BYTES = 50  # 12 floats + 1 uint16 attribute byte count


def _read_stl(path: Path) -> tuple[np.ndarray, int]:
    """Return the raw triangle block (uint8, shape (n, 50)) and the
    triangle count parsed from a binary STL.
    """
    data = path.read_bytes()
    if len(data) < STL_HEADER_BYTES + 4:
        raise ValueError(f"{path}: file is too short to be a binary STL")
    (n,) = struct.unpack("<I", data[STL_HEADER_BYTES:STL_HEADER_BYTES + 4])
    expected = STL_HEADER_BYTES + 4 + n * STL_TRI_BYTES
    if len(data) != expected:
        raise ValueError(
            f"{path}: declared {n} triangles but file size is "
            f"{len(data)} bytes (expected {expected}); not a binary STL?"
        )
    block = np.frombuffer(
        data[STL_HEADER_BYTES + 4:],
        dtype=np.uint8,
    ).reshape(n, STL_TRI_BYTES).copy()
    return block, n


def _vertices_view(block: np.ndarray) -> np.ndarray:
    """Return an (n_tris*3, 3) float32 view of the triangle vertices."""
    # Offsets 12..48 of each 50-byte triangle record hold three 3-float
    # vertices (the first 12 bytes are the normal).
    return np.frombuffer(
        block[:, 12:48].tobytes(), dtype="<f4"
    ).reshape(-1, 3)


def _bbox(block: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    v = _vertices_view(block)
    return v.min(axis=0), v.max(axis=0)


def _translate_block(block: np.ndarray, dxyz: np.ndarray) -> np.ndarray:
    """Return a copy of ``block`` with every vertex translated by
    ``dxyz`` (length-3, mm). Normals are unchanged (translation
    preserves orientation)."""
    if np.allclose(dxyz, 0.0):
        return block
    # Decode the 12-float (normal + 3 vertices) prefix as float32,
    # translate the three vertex slots, re-encode.
    floats = np.frombuffer(
        block[:, 0:48].tobytes(), dtype="<f4"
    ).reshape(-1, 12).copy()
    floats[:, 3:6] += dxyz.astype(np.float32)
    floats[:, 6:9] += dxyz.astype(np.float32)
    floats[:, 9:12] += dxyz.astype(np.float32)
    out = block.copy()
    out[:, 0:48] = np.frombuffer(floats.tobytes(), dtype=np.uint8).reshape(
        -1, 48
    )
    return out


def _parse_input_spec(spec: str) -> tuple[Path, np.ndarray | None]:
    """Parse ``path[@dx,dy,dz]`` into ``(Path, translation_or_None)``."""
    if "@" in spec:
        path_str, off_str = spec.rsplit("@", 1)
        try:
            dx, dy, dz = (float(s) for s in off_str.split(","))
        except ValueError as e:
            raise SystemExit(
                f"Bad translation in '{spec}': expected dx,dy,dz (mm) "
                f"after '@' ({e})"
            )
        return Path(path_str), np.array([dx, dy, dz], dtype=np.float64)
    return Path(spec), None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("out", type=Path, help="Output STL path.")
    ap.add_argument(
        "inputs",
        nargs="+",
        help=(
            "Input STL files. Optionally suffix each with '@dx,dy,dz' "
            "(mm, comma-separated) to translate that input before merging."
        ),
    )
    ap.add_argument(
        "--align-first-to-second",
        action="store_true",
        help=(
            "Before merging, translate the first input so its XY bbox "
            "center matches the second input's XY bbox center and its "
            "minimum Z is 0 (matches what a slicer does when it auto-"
            "centers an object on the build plate)."
        ),
    )
    args = ap.parse_args(argv)

    if len(args.inputs) < 2:
        ap.error("need at least two input STLs to merge")

    parsed: list[tuple[Path, np.ndarray | None]] = [
        _parse_input_spec(s) for s in args.inputs
    ]

    blocks: list[np.ndarray] = []
    for path, translate in parsed:
        block, n = _read_stl(path)
        if translate is not None:
            block = _translate_block(block, translate)
        blocks.append(block)
        print(f"  loaded {path} ({n:,} tris)")

    if args.align_first_to_second:
        a_min, a_max = _bbox(blocks[0])
        b_min, b_max = _bbox(blocks[1])
        a_ctr_xy = 0.5 * (a_min[:2] + a_max[:2])
        b_ctr_xy = 0.5 * (b_min[:2] + b_max[:2])
        dxyz = np.array(
            [b_ctr_xy[0] - a_ctr_xy[0], b_ctr_xy[1] - a_ctr_xy[1], -a_min[2]],
            dtype=np.float64,
        )
        print(f"  align-first-to-second translation: {dxyz}")
        blocks[0] = _translate_block(blocks[0], dxyz)

    total = sum(b.shape[0] for b in blocks)
    out_bytes = bytearray(STL_HEADER_BYTES + 4 + total * STL_TRI_BYTES)
    header = b"merged by merge_stls.py"
    out_bytes[:len(header)] = header
    struct.pack_into("<I", out_bytes, STL_HEADER_BYTES, total)
    offset = STL_HEADER_BYTES + 4
    for block in blocks:
        n_bytes = block.shape[0] * STL_TRI_BYTES
        out_bytes[offset:offset + n_bytes] = block.tobytes()
        offset += n_bytes

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(bytes(out_bytes))
    print(f"  wrote {args.out} ({total:,} tris, {len(out_bytes) / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
