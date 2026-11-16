"""Track the wired top tip (the one that houses the top accelerometer) through a
slow-motion drop clip.

Each clip is a Sony RX100 IV high-frame-rate recording at 959.04 frames/s,
stored as a 59.94 frame/s MP4 (16 times slower than real time). The camera is
turned a quarter turn, so world "down" points to the right of the frame
(+x in image coordinates) and the top of the specimen points left.

Steps for one clip:
1. Read the key frames only (every ~30th frame, about 2 s per clip) at quarter
   size and find the first key frame where the tip sits at its rest position.
   The impact happens in the 30 frames before it.
2. Read about 260 full-size frames around that key frame.
3. Track the tip backward in time from the end of that window, frame by
   frame, with normalized cross-correlation (NCC) template matching and a
   sub-pixel parabolic peak fit. The template is cut from the clip's last
   frame (specimen at rest) around the hand-marked tip position; a template
   cut from the previous tracked frame is used when the rest template matches
   poorly (motion blur or a twisted tip).

Positions are returned in full-size pixels, frame by frame.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np

FPS_CAM = 959.04                 # captureFps in every Sony XML sidecar
DT_MS = 1000.0 / FPS_CAM         # 1.0427 ms between frames
PLAYBACK_FPS = 60000 / 1001      # 59.94 frames/s in the MP4 container
Q = 4                            # key-frame scan is done at 1/Q size


def keyframe_scan(path: Path):
    """Key frames only, grey, at 1/Q size, with their frame indices."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    w, h = 1920 // Q, 1080 // Q
    r = subprocess.run([ff, "-v", "info", "-skip_frame", "nokey", "-i", str(path),
                        "-vf", f"showinfo,scale={w}:{h}:flags=area", "-fps_mode", "passthrough",
                        "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)
    frames = np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w)
    pts = np.array([float(x) for x in re.findall(r"pts_time:([0-9.]+)", r.stderr.decode())])
    idx = np.round((pts - pts[0]) * PLAYBACK_FPS).astype(int)
    return frames, idx[:len(frames)]


def read_frames(path: Path, start: int, count: int) -> tuple[np.ndarray, int]:
    """Full-size grey frames start .. start+count-1 (frame-accurate seek)."""
    cap = cv2.VideoCapture(str(path))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    start = max(0, start)
    count = min(count, n - start)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    out = np.empty((count, 1080, 1920), np.uint8)
    k = 0
    for k in range(count):
        ok, im = cap.read()
        if not ok:
            break
        out[k] = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    else:
        k = count
    return out[:k], start


def last_frame(path: Path, back: int = 3) -> tuple[np.ndarray, int]:
    cap = cv2.VideoCapture(str(path))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, n - back)
    ok, im = cap.read()
    return im, n


def _subpix(res: np.ndarray, loc: tuple[int, int]) -> tuple[float, float]:
    x, y = loc
    dx = dy = 0.0
    if 0 < x < res.shape[1] - 1:
        a, b, c = res[y, x - 1], res[y, x], res[y, x + 1]
        den = a - 2 * b + c
        dx = 0.5 * (a - c) / den if den < 0 else 0.0
    if 0 < y < res.shape[0] - 1:
        a, b, c = res[y - 1, x], res[y, x], res[y + 1, x]
        den = a - 2 * b + c
        dy = 0.5 * (a - c) / den if den < 0 else 0.0
    return x + float(np.clip(dx, -1, 1)), y + float(np.clip(dy, -1, 1))


def match(img: np.ndarray, tpl: np.ndarray, center: tuple[float, float], rx: int, ry: int):
    """Best NCC match of tpl in img near center (template centre coordinates)."""
    th, tw = tpl.shape
    cx, cy = center
    x0 = int(round(cx - tw / 2 - rx)); y0 = int(round(cy - th / 2 - ry))
    x1 = int(round(cx + tw / 2 + rx)); y1 = int(round(cy + th / 2 + ry))
    x0c, y0c = max(0, x0), max(0, y0)
    x1c, y1c = min(img.shape[1], x1), min(img.shape[0], y1)
    if x1c - x0c < tw + 2 or y1c - y0c < th + 2:
        return None, -1.0
    res = cv2.matchTemplate(img[y0c:y1c, x0c:x1c], tpl, cv2.TM_CCOEFF_NORMED)
    _, mx, _, loc = cv2.minMaxLoc(res)
    sx, sy = _subpix(res, loc)
    return (x0c + sx + tw / 2, y0c + sy + th / 2), float(mx)


def find_impact_keyframe(kf: np.ndarray, kidx: np.ndarray, tip_rest: tuple[float, float],
                         half: int = 12) -> int:
    """First key frame from which the tip stays at its rest position."""
    tx, ty = tip_rest[0] / Q, tip_rest[1] / Q
    rest = kf[-1]
    tpl = rest[int(ty) - half:int(ty) + half, int(tx) - half:int(tx) + half]
    ok = []
    for f in kf:
        pos, s = match(f, tpl, (tx, ty), rx=40 // Q * 4, ry=60 // Q)
        ok.append(pos is not None and s > 0.6 and abs(pos[0] - tx) < 120 / Q)
    ok = np.array(ok)
    # earliest k such that every key frame from k on (except possibly one) is at rest
    for k in range(len(ok)):
        if ok[k:].mean() > 0.9 and ok[k]:
            return int(kidx[k])
    return int(kidx[-1])


def track(frames: np.ndarray, rest_img: np.ndarray, tip_rest: tuple[float, float],
          half: int = 32, start_search: int = 120):
    """Track backward from the last frame of `frames` to the first.

    Returns arrays x, y, score (NaN where lost), in full-size pixels.
    """
    n = len(frames)
    tx, ty = tip_rest
    tpl0 = rest_img[int(ty) - half:int(ty) + half, int(tx) - half:int(tx) + half].copy()
    x = np.full(n, np.nan); y = np.full(n, np.nan); sc = np.full(n, np.nan)
    pos, s = match(frames[-1], tpl0, (tx, ty), rx=start_search, ry=40)
    if pos is None:
        return x, y, sc
    x[-1], y[-1], sc[-1] = pos[0], pos[1], s
    prev_tpl = None
    v = (0.0, 0.0)
    lost = 0
    for i in range(n - 2, -1, -1):
        px, py = x[i + 1] - v[0], y[i + 1] - v[1]
        rx = int(18 + 0.6 * abs(v[0])); ry = int(14 + 0.6 * abs(v[1]))
        p0, s0 = match(frames[i], tpl0, (px, py), rx, ry)
        p1, s1 = (None, -1.0)
        if prev_tpl is not None:
            p1, s1 = match(frames[i], prev_tpl, (px, py), rx, ry)
        if p0 is not None and (s0 >= 0.55 or s0 >= s1 - 0.05):
            pos, s = p0, s0
        else:
            pos, s = p1, s1
        if pos is None or s < 0.35 or pos[0] < half + 2:
            lost += 1
            if lost > 2:
                break
            x[i], y[i] = px, py
            sc[i] = s
            continue
        lost = 0
        x[i], y[i], sc[i] = pos[0], pos[1], s
        # velocity estimate in px/frame (backward), from the last 2 steps
        j = min(i + 3, n - 1)
        v = ((x[j] - x[i]) / (j - i), (y[j] - y[i]) / (j - i))
        xi, yi = int(round(x[i])), int(round(y[i]))
        if half <= xi < frames.shape[2] - half and half <= yi < frames.shape[1] - half:
            prev_tpl = frames[i][yi - half:yi + half, xi - half:xi + half].copy()
    # drop the trailing interpolated (lost) points
    bad = sc < 0.35
    x[bad] = np.nan; y[bad] = np.nan
    return x, y, sc
