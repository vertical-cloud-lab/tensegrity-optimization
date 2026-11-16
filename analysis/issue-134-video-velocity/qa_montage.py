"""Check sheet for the tracker: for each specimen's reference clip, three crops
around the tracked tip (middle of the initial window, the impact, middle of the
final window), with the tracked point marked. Usage: python qa_montage.py --videos /tmp/vid"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
TR = HERE / "results" / "tracks"
DT_MS = 1000.0 / 959.04


def frame(path: Path, i: int) -> np.ndarray:
    cap = cv2.VideoCapture(str(path))
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    return cap.read()[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", type=Path, required=True)
    args = ap.parse_args()
    clips = pd.read_csv(HERE / "results" / "video_per_clip.csv")
    ann = json.loads((HERE / "annotations.json").read_text())
    rows = []
    for ref in ann:
        c = clips[clips["clip"] == ref + ".MP4"]
        if c.empty or c.iloc[0].status != "ok":
            continue
        t50 = float(c.iloc[0].t50_frame)
        tr = pd.read_csv(TR / f"{ref}_track.csv").set_index("frame")
        batch = next(b for b in ("corny", "drran", "2dran") if ref.startswith(b))
        path = args.videos / batch / f"{ref}.MP4"
        crops = []
        for lab, off in (("-15 ms", -15), ("impact", 0), ("+15 ms", 15)):
            i = int(round(t50 + off / DT_MS))
            if i not in tr.index or not np.isfinite(tr.loc[i, "x_px"]):
                crops.append(np.zeros((200, 200, 3), np.uint8)); continue
            x, y = tr.loc[i, "x_px"], tr.loc[i, "y_px"]
            im = frame(path, i)
            x0 = int(np.clip(x - 100, 0, 1920 - 200)); y0 = int(np.clip(y - 100, 0, 1080 - 200))
            cr = im[y0:y0 + 200, x0:x0 + 200].copy()
            cx, cy = int(round(x - x0)), int(round(y - y0))
            cv2.drawMarker(cr, (cx, cy), (0, 0, 255), cv2.MARKER_CROSS, 28, 2)
            cv2.putText(cr, lab, (4, 194), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            crops.append(cr)
        row = np.hstack(crops)
        cv2.putText(row, ref, (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
        rows.append(row)
    # three specimens per line
    while len(rows) % 3:
        rows.append(np.zeros_like(rows[0]))
    lines = [np.hstack(rows[i:i + 3]) for i in range(0, len(rows), 3)]
    for k in range(0, len(lines), 5):
        out = HERE / "figures" / f"05_tracking_check_{k // 5 + 1}.jpg"
        cv2.imwrite(str(out), np.vstack(lines[k:k + 5]), [cv2.IMWRITE_JPEG_QUALITY, 82])
        print(out.name)


if __name__ == "__main__":
    main()
