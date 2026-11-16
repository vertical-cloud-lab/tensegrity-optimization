"""Track the wired top tip in every clip of the specimens listed in
annotations.json, and write one CSV of frame-by-frame positions per clip.

annotations.json holds, for one reference clip per specimen, the hand-marked
position of the wired tip (the top tip the black accelerometer cable leaves
from) in that clip's last frame (specimen at rest on the carriage), plus the
left-most extent of the top tips (x_top) and the right-most extent of the
bottom joints (x_bottom), all in full-size pixels. The other clips of the same
specimen are matched to the reference by NCC on the specimen region of their
own last frame, which gives the camera shift between clips.

Usage:
    python run_tracking.py --videos /tmp/vid [--jobs 4] [specimen ...]
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

import track_tip as T

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "tracks"
ANN = json.loads((HERE / "annotations.json").read_text())


def clips_for(spec: str, videos: Path) -> list[Path]:
    batch = next(b for b in ("corny", "drran", "2dran", "dran3", "1sne") if spec.startswith(b))
    return sorted(p for p in (videos / batch).glob(f"{spec}-*.MP4"))


def reference_clip(spec: str) -> str:
    return next(k for k in ANN if k.rsplit("-", 1)[0] == spec)


def camera_shift(ref_img: np.ndarray, img: np.ndarray, a: dict) -> tuple[float, float, float]:
    """Shift of the specimen region between two rest frames (NCC)."""
    x0 = max(0, a["x_top"] - 40); x1 = min(1920, a["x_bottom"] + 20)
    y0 = max(0, a["tip"][1] - 110); y1 = min(1080, a["tip"][1] + 230)
    tpl = ref_img[y0:y1, x0:x1]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    pos, s = T.match(img, tpl, (cx, cy), rx=200, ry=150)
    if pos is None:
        return 0.0, 0.0, -1.0
    return pos[0] - cx, pos[1] - cy, s


def process(job):
    spec, clip, videos = job
    ref_name = reference_clip(spec)
    a = ANN[ref_name]
    rest, n = T.last_frame(clip)
    rest_g = cv2.cvtColor(rest, cv2.COLOR_BGR2GRAY)
    if clip.stem == ref_name:
        dx = dy = 0.0; s_shift = 1.0
    else:
        ref_clip = next(p for p in clips_for(spec, videos) if p.stem == ref_name)
        ref_img = cv2.cvtColor(T.last_frame(ref_clip)[0], cv2.COLOR_BGR2GRAY)
        dx, dy, s_shift = camera_shift(ref_img, rest_g, a)
    tip = (a["tip"][0] + dx, a["tip"][1] + dy)
    kf, kidx = T.keyframe_scan(clip)
    k = T.find_impact_keyframe(kf, kidx, tip)
    frames, start = T.read_frames(clip, k - 170, 260)
    x, y, sc = T.track(frames, rest_g, tip)
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame({"frame": np.arange(start, start + len(frames)), "x_px": x, "y_px": y, "ncc": sc})
    df.to_csv(OUT / f"{clip.stem}_track.csv", index=False, float_format="%.3f")
    meta = dict(specimen=spec, clip=clip.name, reference_clip=ref_name, n_frames=n,
                shift_px=[round(dx, 2), round(dy, 2)], shift_ncc=round(s_shift, 3),
                tip_rest_px=[round(tip[0], 1), round(tip[1], 1)],
                x_top_px=round(a["x_top"] + dx, 1), x_bottom_px=round(a["x_bottom"] + dx, 1),
                impact_keyframe=int(k), window_start=int(start), n_tracked=int(np.isfinite(x).sum()))
    (OUT / f"{clip.stem}_meta.json").write_text(json.dumps(meta, indent=1))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", type=Path, required=True)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("specimens", nargs="*")
    args = ap.parse_args()
    specs = args.specimens or sorted({k.rsplit("-", 1)[0] for k in ANN})
    jobs = [(s, c, args.videos) for s in specs for c in clips_for(s, args.videos)]
    with ProcessPoolExecutor(args.jobs) as ex:
        for m in ex.map(process, jobs):
            print(m["clip"], "shift", m["shift_px"], m["shift_ncc"], "tracked", m["n_tracked"], flush=True)


if __name__ == "__main__":
    main()
