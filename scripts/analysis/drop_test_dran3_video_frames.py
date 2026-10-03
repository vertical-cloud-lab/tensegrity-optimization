#!/usr/bin/env python3
"""dran31..dran39 slo-mo frame check — identity montage + impact strip (PR #86, 10-03).

The batch's 27 clips (Sony RX100 IV HFR, ``captureFps="959.04p"``, 2052
frames per clip) are portrait recordings stored unrotated: the drop runs
along image x, and a 90° clockwise rotation puts the tower upright.  The
operator tapes the session label onto the carriage, so a post-impact
frame shows which session a clip belongs to, independently of the file
name and of the camera clock (reset to 2018 for this batch).

Two figures from the drop-10 clips (``dran3N-10th.MP4``):

- ``14_video_identity_montage.jpg`` — one rest frame (frame 1500, after
  the carriage has settled) per session, cropped to carriage + specimen;
- ``15_video_impact_dran35_vs_dran39.jpg`` — the impact sequence of the
  gauge-tripping ``dran35`` (t28) next to its infill-only clone sibling
  ``dran39`` (t30), aligned on the frame of peak inter-frame motion.

Usage:
    python scripts/analysis/drop_test_dran3_video_frames.py --mp4 DIR
where DIR holds the ``dran3N-10th.MP4`` clips (Box ids in
``data/drop-tests/dran3-checkin/video/box-ids.json``).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import DATA  # noqa: E402

OUT = DATA / "dran3-checkin" / "figures"
REST_FRAME = 1500
STRIP_OFFSETS = (-30, -10, 0, 10, 20, 35, 60, 100)   # frames rel. to peak motion


def upright(frame: np.ndarray) -> np.ndarray:
    """Rotate to upright and lift the dark exposure for viewing."""
    return cv2.convertScaleAbs(cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE), alpha=1.8, beta=10)


def read_frames(path: Path, wanted: set[int]) -> dict[int, np.ndarray]:
    cap = cv2.VideoCapture(str(path))
    out, k = {}, 0
    while k <= max(wanted):
        if not cap.grab():
            break
        if k in wanted:
            out[k] = cap.retrieve()[1]
        k += 1
    return out


def peak_motion_frame(path: Path) -> int:
    """Frame with the largest mean inter-frame difference (carriage arrival)."""
    cap = cv2.VideoCapture(str(path))
    prev, best, best_k, k = None, -1.0, 0, 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(cv2.resize(fr, (240, 135)), cv2.COLOR_BGR2GRAY).astype(float)
        if prev is not None:
            e = np.abs(g - prev).mean()
            if e > best:
                best, best_k = e, k
        prev, k = g, k + 1
    return best_k


def label(img: np.ndarray, text: str, scale: float = 0.6) -> np.ndarray:
    cv2.putText(img, text, (6, int(28 * scale + 6)), cv2.FONT_HERSHEY_SIMPLEX,
                scale, (0, 255, 255), 2)
    return img


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mp4", type=Path, required=True, help="folder with dran3N-10th.MP4")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    tiles = []
    for n in range(1, 10):
        path = args.mp4 / f"dran3{n}-10th.MP4"
        nfr = int(cv2.VideoCapture(str(path)).get(cv2.CAP_PROP_FRAME_COUNT))
        k = min(REST_FRAME, nfr - 5)
        img = upright(read_frames(path, {k})[k])[1050:1700, 120:1020]
        tiles.append(label(cv2.resize(img, (450, 325)), f"dran3{n}-10th  frame {k}"))
    grid = np.vstack([np.hstack(tiles[j:j + 3]) for j in range(0, 9, 3)])
    cv2.imwrite(str(args.out / "14_video_identity_montage.jpg"), grid,
                [cv2.IMWRITE_JPEG_QUALITY, 88])

    rows = []
    for n in (5, 9):
        path = args.mp4 / f"dran3{n}-10th.MP4"
        k0 = peak_motion_frame(path)
        frames = read_frames(path, {k0 + d for d in STRIP_OFFSETS})
        strip = []
        for d in STRIP_OFFSETS:
            img = cv2.resize(upright(frames[k0 + d])[700:1750, 100:1050], (238, 263))
            strip.append(label(img, f"dran3{n} {d:+d} fr ({d / 0.95904:+.0f} ms)", 0.42))
        rows.append(np.hstack(strip))
        print(f"dran3{n}: peak inter-frame motion at frame {k0}")
    cv2.imwrite(str(args.out / "15_video_impact_dran35_vs_dran39.jpg"), np.vstack(rows),
                [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"figures -> {args.out}")


if __name__ == "__main__":
    main()
