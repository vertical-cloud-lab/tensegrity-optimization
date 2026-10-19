#!/usr/bin/env python3
"""First articles vs plate-1 copies: side-by-side slo-mo with synced acceleration (PR #86, 10-19).

@me-madsen (PR #86, 10-19): compare the slo-mo of the original corny drops
with the same designs' recent drops (corny7 with 1sne71-73, and so on),
side by side, each drop matched up as well as possible, with the
acceleration traces shown aligned to the video.

Three designs are on both sides: corny2 (t38), corny7 (t37) and corny8
(t39).  Each has four articles: the first article (``corny<N>``, recorded
09-12/09-14) and its three plate-1 copies (``1sne<N>1``-``3``, 10-17).
Every session filmed drops 1, 10 and 20 (the film-1/10/20 SOP), so each
design gives three four-way comparisons, one per filmed drop.

Clips.  Sony RX100 IV HFR, ``captureFps="959.04p"`` in every XML sidecar:
each stored frame is one capture frame, 1.0427 ms apart (the corny clips
are stored at 59.94p, the 1sne clips at 23.98p; only the playback rate
differs).  Both batches are portrait recordings stored unrotated; a 90 deg
clockwise rotation puts the tower upright.

Clip <-> drop pairing: the MP4 header creation time (camera clock) plus a
constant camera-to-DAQ offset, fitted per batch as in
``drop_test_1sne_video_frames.py``, against the TP4 series tables.  The
1sne pairing reproduces ``figures/video_pairing.json``.  A clip whose drop
has no usable capture (the 10-17 CH5 fault hour, a missing export, or a
clip filmed after the session's last capture) gets a *stand-in* trace: the
nearest usable capture of the same session, drawn dashed and labeled.

Sync.  The carriage is tracked in every frame (normalized cross-correlation
of its rest-frame appearance, sub-pixel vertical position).  CH5 sits on
the carriage, so integrating it twice (tail baseline, gravity included)
gives the carriage's own motion through the impact.  Fitting that to the
tracked trajectory (free time shift, pixel scale, arrival speed, offset)
places the CH5 CFC-180 peak on the video timeline to a small fraction of a
frame, and measures each clip's pixel scale at the carriage plane.  Clips
without a usable capture are placed by their lowest carriage point,
shifted by the lowest-point-to-CH5-peak lag measured on the fitted clips.
t = 0 everywhere is the CH5 CFC-180 peak.

What the clips show on the wide, high-twist family (corny7, corny8): the
top triangle sags and twists at impact, the side cables go slack, and the
structure snaps back upright 40-55 ms later, with the feet on the plate.
The snap-back is the top vertex's largest CFC-180 burst 25-70 ms after
impact (``snap_burst_ms`` in the json): the kind of secondary event the
hop metric (t_second, e_rebound) has been read as a landing.

Outputs (``data/drop-tests/1sne-checkin``):
  video/compare/<design>_vs_1sne<d>x.mp4      one video per design, three
                                              filmed drops in sequence
  video/compare/corny7_vs_1sne7x_drop10_preview.gif   inline preview
  figures/video-compare/24-26_video_compare_<design>.jpg
                                              frame strips + traces (drop 10)
  figures/video-compare/27_video_sync_check.png   video vs DAQ carriage motion
  figures/video-compare/video_comparison.json     pairing, sync, scale, labels

Usage:
    python scripts/analysis/drop_test_corny_1sne_video_comparison.py \\
        --mp4 DIR --daq DIR [--work DIR] [--ffmpeg PATH] [--procs N]
where --mp4 holds the 36 clips (``corny{2,7,8}-{1st,10th,20th}.MP4``,
Box ids in ``data/drop-tests/corny-checkin/video/box-ids.json``, and the
27 ``1sne*-{1,10,20}.MP4``, ids in ``video/box-ids.json``) and --daq holds
the captures named ``<session>_Signal<k>.csv`` (Box ids in each session's
``raw/<session>/box-ids.json``).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from multiprocessing import Pool
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import DATA, GRAVITY  # noqa: E402
from drop_test_abc123_blind_analysis import cfc_filter, parse_capture  # noqa: E402
from drop_test_1sne_checkin_analysis import census_capture, classify  # noqa: E402
from drop_test_1sne_video_frames import mvhd_creation  # noqa: E402

OUT = DATA / "1sne-checkin"
FIG = OUT / "figures"
FIGV = FIG / "video-compare"          # 24-27 (figures/ch5-replicates holds 17-23)
VID = OUT / "video" / "compare"
CORNY = DATA / "corny-checkin"

FPS = 959.04                          # captureFps in every sidecar
FRAME_W = 1080                        # upright frame width, px
DESIGNS = {"corny2": "t38", "corny7": "t37", "corny8": "t39"}
SLOTS = ("1", "10", "20")             # filmed drops (SOP)
CORNY_SUFFIX = {"1": "1st", "10": "10th", "20": "20th"}
USABLE = ("valid", "knock")           # capture classes that hold an impact
PAIR_MAX_S = 2.0                      # clip further than this from any event: no capture

# tracking (half-resolution upright frames)
SCALE = 0.5
NCC_MIN = 0.6
FIT_FRAMES = (-20, 12)                # sync-fit window around the lowest point

# composite layout
T0_MS, T1_MS = -35.0, 95.0            # video window around the CH5 peak
PANEL_W, PANEL_H = 360, 540           # px; the panel spans PANEL_MM below
PANEL_MM = (140.0, 210.0)             # (width, height) of the panel, mm at the plate
ABOVE_MM = 160.0                      # panel top this far above the plate at t = 0
PLOT_H, LABEL_H, HEAD_H, FOOT_H, GAP = 165, 70, 64, 34, 8
OUT_FPS = 15                          # 959 capture fps -> 64x slower than real time
HOLD_S = 0.8                          # freeze on first/last frame of each drop
YLIM_G = (-60.0, 460.0)
ZOOM_MS = (-3.0, 8.0)

# colors (dataviz reference palette; CH5 in ink, the top vertex in slots 1-2)
INK, INK2, MUTED, GRID, AXIS, SURFACE = ("#0b0b0b", "#52514e", "#898781", "#e1e0d9",
                                         "#c3c2b7", "#fcfcfb")
C_IN, C_TOP, C_TOPB = INK, "#2a78d6", "#eb6834"


def hex_bgr(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)


# --------------------------------------------------------------------------
# pairing
# --------------------------------------------------------------------------
def series_events(root: Path) -> list[dict]:
    ev = []
    for tab in sorted(root.glob("*/*.csv")):
        if "Signal" in tab.name:
            continue
        for line in tab.read_text(encoding="latin-1").splitlines()[6:]:
            c = [v.strip() for v in line.split(",")]
            if len(c) > 15 and c[1].isdigit():
                ev.append({"session": tab.parent.name, "event": int(c[1]),
                           "time": datetime.strptime(c[2], "%m/%d/%Y %I:%M:%S %p")})
    return sorted(ev, key=lambda e: e["time"])


def pair_clips(clips: dict[str, Path], ev: list[dict]) -> dict[str, dict]:
    """Constant camera->DAQ offset (the candidate that lands the most clips
    within PAIR_MAX_S of an event, refined by their median residual), then
    the nearest event per clip."""
    names = sorted(clips)
    cam = {n: mvhd_creation(clips[n]) for n in names}
    et = np.array([e["time"].timestamp() for e in ev])
    ct = np.array([cam[n].timestamp() for n in names])
    cands = (et[:, None] - ct[None, :]).ravel()
    hits = [(np.abs(et[None, :] - (ct[:, None] + d)).min(1) <= PAIR_MAX_S).sum() for d in cands]
    d0 = cands[int(np.argmax(hits))]
    near = np.abs(et[None, :] - (ct[:, None] + d0)).argmin(1)
    res = et[near] - (ct + d0)
    d0 += float(np.median(res[np.abs(res) <= PAIR_MAX_S]))
    off = timedelta(seconds=round(float(d0)))
    out = {}
    for n in names:
        daq = cam[n] + off
        e = min(ev, key=lambda e: abs((e["time"] - daq).total_seconds()))
        r = (daq - e["time"]).total_seconds()
        out[n] = {"camera_time": cam[n].isoformat(), "daq_time": daq.isoformat(),
                  "offset": str(off), "session": e["session"] if abs(r) <= PAIR_MAX_S else None,
                  "event": e["event"] if abs(r) <= PAIR_MAX_S else None,
                  "residual_s": round(r, 1)}
        if out[n]["event"] is None:          # say where the clip sits in its own session
            own = [x["time"] for x in ev if x["session"] == n.split("-")[0]]
            if daq > max(own):
                gap = (daq - max(own)).total_seconds() / 60
                note = f"{gap:.1f} min after the session's last capture"
            elif daq < min(own):
                gap = (min(own) - daq).total_seconds() / 60
                note = f"{gap:.1f} min before the session's first capture"
            else:
                note = "missing from the export"
            out[n]["note"] = note
    return out


# --------------------------------------------------------------------------
# carriage tracking
# --------------------------------------------------------------------------
def upright(frame: np.ndarray) -> np.ndarray:
    return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)


def decode_gray(path: Path) -> np.ndarray:
    cap = cv2.VideoCapture(str(path))
    out = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        g = cv2.resize(g, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_AREA)
        out.append(upright(g))
    return np.stack(out)


def moving_mask(E: np.ndarray, R: np.ndarray) -> np.ndarray:
    m = (cv2.absdiff(R, E) > 25).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))


def carriage_box(mask: np.ndarray) -> tuple[int, int, int, int]:
    """Rows/cols of the carriage block in the rest frame: the run of mask
    rows at least 60 % as wide as the widest, around the widest."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask)
    comp = lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    w = comp.sum(1)
    big = np.where(w > 0.6 * w.max())[0]
    r_max = int(np.argmax(w))
    run = next(r for r in np.split(big, np.where(np.diff(big) > 3)[0] + 1)
               if r[0] <= r_max <= r[-1])
    r0, r1 = int(run[0]), int(run[-1])
    cols = np.where(comp[r0:r1 + 1].mean(0) > 0.5)[0]
    return r0, r1, int(cols[0]), int(cols[-1])


def specimen_center(mask: np.ndarray, box) -> float:
    """Column centre of the specimen in the rest frame: the moving mask in
    the ~100 mm above the carriage top, opened to drop the thin cables; the
    midpoint of the densest run of columns (struts and feet)."""
    r0, _, c0, c1 = (int(v) for v in box)
    m = mask[max(0, r0 - 170):r0 - 4, c0:c1 + 1]
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    col = np.convolve(m.sum(0).astype(float), np.ones(5) / 5, mode="same")
    on = np.where(col > 0.3 * col.max())[0]
    runs = np.split(on, np.where(np.diff(on) > 12)[0] + 1)
    best = max(runs, key=lambda r: col[r].sum())
    return float(c0 + 0.5 * (best[0] + best[-1]))


def match_y(frames, idx, T, sx0, sx1, pad):
    ys, xs, cc = {}, {}, {}
    for k in idx:
        res = cv2.matchTemplate(frames[k][:, sx0:sx1], T, cv2.TM_CCOEFF_NORMED)
        y, x = np.unravel_index(int(np.argmax(res)), res.shape)
        dy = 0.0
        if 0 < y < res.shape[0] - 1:
            a, b, c = res[y - 1, x], res[y, x], res[y + 1, x]
            den = a - 2 * b + c
            dy = 0.5 * (a - c) / den if den else 0.0
        ys[k], xs[k], cc[k] = y + dy, x - pad, float(res[y, x])
    return ys, xs, cc


def track_clip(path: Path) -> dict:
    """Carriage trajectory (half-res px below its rest position) around the
    impact, plus the rest-frame geometry needed to crop the panel."""
    fr = decode_gray(path)
    n = len(fr)
    E = np.median(fr[:20], axis=0).astype(np.uint8)
    R = np.median(fr[-20:], axis=0).astype(np.uint8)
    mask = moving_mask(E, R)
    box = carriage_box(mask)
    r0, r1, c0, c1 = box
    W = fr.shape[2]
    pad = 8
    ty0, ty1 = r0 + 4, r1 - 4
    tx0, tx1 = max(c0 + 6, pad), min(c1 - 6, W - 1 - pad)
    T = R[ty0:ty1, tx0:tx1]
    sx0, sx1 = tx0 - pad, tx1 + pad
    # coarse pass every 3rd frame, then every frame around the lowest point
    ys, xs, cc = match_y(fr, range(0, n, 3), T, sx0, sx1, pad)
    ok = [k for k in ys if cc[k] > NCC_MIN]
    k_c = max(ok, key=lambda k: ys[k])
    lo, hi = max(0, k_c - 160), min(n, k_c + 200)
    ys, xs, cc = match_y(fr, range(lo, hi), T, sx0, sx1, pad)
    k = np.arange(lo, hi)
    y = np.array([ys[i] for i in k]) - ty0
    x = np.array([xs[i] for i in k], float)
    c = np.array([cc[i] for i in k])
    good = c > NCC_MIN
    j = int(np.argmax(np.where(good, y, -np.inf)))
    a, b, d = y[j - 1], y[j], y[j + 1]
    k_low = float(k[j] + 0.5 * (a - d) / (a - 2 * b + d))
    return {"n_frames": n, "k": k, "y": y, "x": x, "cc": c, "box": box,
            "spec_x": specimen_center(mask, box), "k_low_int": int(k[j]), "k_low": k_low,
            "E": E, "R": R}


# --------------------------------------------------------------------------
# DAQ
# --------------------------------------------------------------------------
def daq_trace(path: Path) -> dict:
    """Tail-baselined channels, CFC-180/1000, t relative to the CH5 CFC-180
    peak, and CH5's twice-integrated carriage motion for the sync fit."""
    t, ch, _ = parse_capture(path)
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    x = ch - np.median(ch[int(0.070 / dt):], axis=0)
    ch5 = x[:, 3]
    top = x[:, :3]
    ch5_180 = cfc_filter(ch5, fs, 180)
    ip = int(np.argmax(np.abs(ch5_180[:int(0.015 / dt)])))
    top180 = np.sqrt(sum(cfc_filter(top[:, c], fs, 180) ** 2 for c in range(3)))
    top1000 = np.sqrt(sum(cfc_filter(top[:, c], fs, 1000) ** 2 for c in range(3)))
    topraw = np.sqrt((top ** 2).sum(1))
    a_down = GRAVITY * (1.0 - ch5)             # CH5 > 0 pushes the carriage up
    v = integrate.cumulative_trapezoid(a_down, t, initial=0.0)
    yk = integrate.cumulative_trapezoid(v, t, initial=0.0)
    step = 25                                  # 50 kHz is plenty for drawing
    tr = (t - t[ip]) * 1e3
    return {"t_rec": t, "y_rec": yk, "t_peak_s": float(t[ip]),
            "t_ms": tr[::step], "ch5_180": ch5_180[::step], "top180": top180[::step],
            "top1000": top1000[::step],
            "topraw_peak_g": float(topraw[:int(0.015 / dt)].max()),
            "rec_ms": (float(tr[0]), float(tr[-1]))}


def kin_at(tq: np.ndarray, tr: dict) -> np.ndarray:
    """CH5-integrated carriage position at record times tq (free fall before
    the record starts)."""
    out = np.interp(tq, tr["t_rec"], tr["y_rec"])
    pre = tq < tr["t_rec"][0]
    out[pre] = 0.5 * GRAVITY * (tq[pre] - tr["t_rec"][0]) ** 2
    return out


def sync_fit(trk: dict, tr: dict) -> dict:
    """Shift/scale/speed fit of the CH5 kinematics to the tracked carriage."""
    k0 = trk["k_low_int"]
    sel = (trk["k"] >= k0 + FIT_FRAMES[0]) & (trk["k"] <= k0 + FIT_FRAMES[1]) & (trk["cc"] > NCC_MIN)
    ks, yy = trk["k"][sel].astype(float), trk["y"][sel]

    def solve(sh):
        tq = (ks - k0) / FPS + sh
        A = np.stack([tq, kin_at(tq, tr), np.ones_like(tq)], 1)
        coef, *_ = np.linalg.lstsq(A, yy, rcond=None)
        r = yy - A @ coef
        return float(r @ r), coef, r

    tp = tr["t_peak_s"]
    grid = np.arange(tp - 0.004, tp + 0.006, 2e-5)
    sse = [solve(s)[0] for s in grid]
    sh = float(grid[int(np.argmin(sse))])
    fine = np.arange(sh - 4e-5, sh + 4e-5, 1e-6)
    sh = float(fine[int(np.argmin([solve(s)[0] for s in fine]))])
    sse, coef, r = solve(sh)
    s_half = coef[1]                           # half-res px per metre
    k_peak = k0 + (tp - sh) * FPS
    return {"k_peak": float(k_peak), "px_per_mm": float(s_half / SCALE / 1000.0),
            "v0_ms": float(coef[0] / s_half), "rms_px_half": float(np.sqrt(sse / len(r))),
            "n_fit": int(len(r)), "lag_low_minus_peak_ms": float((trk["k_low"] - k_peak) / FPS * 1e3),
            "coef": [float(c) for c in coef]}


def sync_model_mm(sync: dict, tr: dict, t_ms) -> np.ndarray:
    """Fitted carriage position (mm below its rest position) at t_ms from the
    CH5 peak."""
    tq = tr["t_peak_s"] + np.asarray(t_ms, float) * 1e-3
    c0, c1, c2 = sync["coef"]
    return (c0 * tq + c1 * kin_at(tq, tr) + c2) / (sync["px_per_mm"] * SCALE)


# --------------------------------------------------------------------------
# panels
# --------------------------------------------------------------------------
def panel_rect(trk: dict, k_peak: float, px_mm: float) -> tuple[int, int, int, int]:
    """Full-res upright crop (x0, y0, x1, y1): plate (carriage top) at t = 0
    sits ABOVE_MM below the panel top, specimen centred."""
    r0 = trk["box"][0]
    y_peak = float(np.interp(k_peak, trk["k"], trk["y"]))
    plate_y = (r0 + y_peak) / SCALE
    cx = trk["spec_x"] / SCALE
    w, h = PANEL_MM[0] * px_mm, PANEL_MM[1] * px_mm
    cx = min(max(cx, w / 2), FRAME_W - w / 2)   # stay inside the frame (09-12 framing)
    y0 = plate_y - ABOVE_MM * px_mm
    return int(round(cx - w / 2)), int(round(y0)), int(round(cx + w / 2)), int(round(y0 + h))


def crop_pad(img: np.ndarray, rect) -> np.ndarray:
    x0, y0, x1, y1 = rect
    H, W = img.shape[:2]
    out = np.zeros((y1 - y0, x1 - x0, 3), np.uint8)
    sx0, sy0, sx1, sy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if sx1 > sx0 and sy1 > sy0:
        out[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = img[sy0:sy1, sx0:sx1]
    return out


def panel_frames(path: Path, k_peak: float, rect, t_ms: np.ndarray) -> list[np.ndarray]:
    """Panels at the requested times (nearest capture frame), auto-levelled
    with one stretch per clip (from the t = +60 ms frame) and lightly
    smoothed (edge-preserving; the 1sne session was filmed in a dark room)."""
    want = np.clip(np.round(k_peak + t_ms * 1e-3 * FPS).astype(int), 0, None)
    need = sorted(set(want.tolist()))
    cap = cv2.VideoCapture(str(path))
    got, k = {}, 0
    while k <= need[-1]:
        if not cap.grab():
            break
        if k in need:
            img = crop_pad(upright(cap.retrieve()[1]), rect)
            got[k] = cv2.resize(img, (PANEL_W, PANEL_H), interpolation=cv2.INTER_AREA)
        k += 1
    ref = got[want[int(np.argmin(np.abs(t_ms - 60.0)))]]
    lum = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
    lo, hi = np.percentile(lum[lum > 0], [1.0, 99.5]) if (lum > 0).any() else (0, 255)
    lut = np.clip((np.arange(256) - lo) * 235.0 / max(hi - lo, 1.0) + 8, 0, 255).astype(np.uint8)
    out = {}
    for kk, img in got.items():
        img = cv2.LUT(img, lut)
        out[kk] = cv2.bilateralFilter(img, 7, 30, 5)
    blank = np.zeros((PANEL_H, PANEL_W, 3), np.uint8)
    return [out.get(int(w), blank) for w in want]


# --------------------------------------------------------------------------
# plots (rendered once; the cursor is drawn per frame)
# --------------------------------------------------------------------------
def style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(AXIS)
    ax.tick_params(colors=INK2, labelsize=7.5, length=2.5)


def plot_image(tr: dict | None, xlim, standin: bool, zoom: bool, note: str):
    """RGB image of one trace panel + the time->pixel map of its x axis."""
    fig = plt.figure(figsize=(PANEL_W / 100, PLOT_H / 100), dpi=100, facecolor=SURFACE)
    ax = fig.add_axes([0.13, 0.22, 0.83, 0.68])
    style(ax)
    ls = (0, (4, 2.2)) if standin else "-"
    if tr is not None:
        m = (tr["t_ms"] >= xlim[0] - 1) & (tr["t_ms"] <= xlim[1] + 1)
        t = tr["t_ms"][m]
        ax.plot(t, tr["top1000"][m], color=C_TOPB, lw=0.9, ls=ls, alpha=0.9)
        ax.plot(t, tr["ch5_180"][m], color=C_IN, lw=1.4, ls=ls)
        ax.plot(t, tr["top180"][m], color=C_TOP, lw=1.4, ls=ls)
        if xlim[0] < tr["rec_ms"][0]:
            ax.axvspan(xlim[0], tr["rec_ms"][0], color="#f0efec", lw=0)
            if not zoom:
                ax.text(0.5 * (xlim[0] + tr["rec_ms"][0]), YLIM_G[1] * 0.55, "before\nrecord",
                        ha="center", va="center", fontsize=7, color=MUTED)
        over = tr["top1000"][m] > YLIM_G[1]
        if over.any():
            j = int(np.argmax(tr["top1000"][m]))
            ax.annotate(f"{tr['top1000'][m][j]:.0f} G", (t[j], YLIM_G[1]), xytext=(4, -9),
                        textcoords="offset points", fontsize=7, color=INK2)
    else:
        ax.text(0.5, 0.5, "no capture", transform=ax.transAxes, ha="center", va="center",
                fontsize=9, color=MUTED)
    ax.set_xlim(*xlim)
    ax.set_ylim(*YLIM_G)
    ax.set_ylabel("G", fontsize=7.5, color=INK2, labelpad=1)
    ax.set_xlabel("ms from CH5 peak" + (" (zoom)" if zoom else ""), fontsize=7.5,
                  color=INK2, labelpad=1)
    if note:
        ax.text(0.99, 0.97, note, transform=ax.transAxes, ha="right", va="top", fontsize=7,
                color=INK2)
    fig.canvas.draw()
    img = cv2.cvtColor(np.asarray(fig.canvas.buffer_rgba())[:, :, :3], cv2.COLOR_RGB2BGR)
    bb = ax.get_window_extent()
    H = img.shape[0]
    xa, xb = bb.x0, bb.x1
    ytop, ybot = H - bb.y1, H - bb.y0
    plt.close(fig)

    def x_of(tms):
        return xa + (tms - xlim[0]) / (xlim[1] - xlim[0]) * (xb - xa)
    return img.copy(), x_of, (int(ytop), int(ybot))


# --------------------------------------------------------------------------
# text (PIL, DejaVu Sans from matplotlib)
# --------------------------------------------------------------------------
_FONT_DIR = Path(matplotlib.get_data_path()) / "fonts" / "ttf"


def font(size: int, bold: bool = False):
    from PIL import ImageFont
    return ImageFont.truetype(str(_FONT_DIR / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")),
                              size)


def wrap(text: str, size: int, width: int) -> list[str]:
    """Greedy word wrap to a pixel width (explicit newlines kept)."""
    f, out = font(size), []
    for para in text.split("\n"):
        line = ""
        for w in para.split(" "):
            trial = f"{line} {w}".strip()
            if line and f.getlength(trial) > width:
                out.append(line)
                line = w
            else:
                line = trial
        out.append(line)
    return out


def draw_text(img: np.ndarray, items) -> np.ndarray:
    """items: (x, y, text, size, bold, hex color[, anchor])."""
    from PIL import Image, ImageDraw
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil)
    for it in items:
        x, y, text, size, bold, col = it[:6]
        d.text((x, y), text, font=font(size, bold), fill=col, anchor=it[6] if len(it) > 6 else "la")
    return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)


# --------------------------------------------------------------------------
# comparison table
# --------------------------------------------------------------------------
def articles(design: str) -> list[str]:
    return [design] + [f"1sne{design[-1]}{c}" for c in "123"]


def clip_name(art: str, slot: str) -> str:
    return (f"{art}-{CORNY_SUFFIX[slot]}.MP4" if art.startswith("corny")
            else f"{art}-{slot}.MP4")


def role(art: str) -> str:
    if art.startswith("corny"):
        return "first article"
    return f"copy {art[-1]} ({ {'1': 'back', '2': 'middle', '3': 'front'}[art[-1]] } row)"


def session_classes() -> dict[tuple[str, int], str]:
    """Capture class per (session, signal): the committed 1sne census; every
    corny capture holds an impact (180/180 clean, corny-checkin README)."""
    cls = {(r["session"], int(r["signal"])): r["class"]
           for r in json.loads((FIG / "capture_census.json").read_text())}
    for d in DESIGNS:
        for e in series_events(CORNY / "raw"):
            if e["session"] == d:
                cls[(d, e["event"])] = "usable"
    return cls


def choose_trace(art: str, slot: str, pair: dict, cls: dict) -> dict:
    """The filmed drop's own capture if it holds an impact; otherwise the
    nearest usable capture of the same session (stand-in)."""
    own = pair.get("event") if pair.get("session") == art else None
    c = cls.get((art, own)) if own else None
    if own and (c in USABLE or c == "usable"):
        return {"filmed_drop": own, "signal": own, "standin": False, "own_class": c, "why": ""}
    nominal = own or int(slot)
    pool = [s for (a, s), k in cls.items() if a == art and (k in USABLE or k == "usable")]
    s = min(pool, key=lambda s: (abs(s - nominal), s))
    why = (f"drop {own}: no impact in the capture ({c})" if own
           else f"not captured (filmed {pair.get('note', '')})" if "min" in pair.get("note", "")
           else f"not captured ({pair.get('note', '')})")
    return {"filmed_drop": own, "signal": s, "standin": True, "own_class": c, "why": why}


# --------------------------------------------------------------------------
# composite
# --------------------------------------------------------------------------
def layout():
    W = 4 * PANEL_W + 5 * GAP
    y_lab = HEAD_H
    y_vid = y_lab + LABEL_H
    y_p1 = y_vid + PANEL_H + GAP
    y_p2 = y_p1 + PLOT_H
    y_foot = y_p2 + PLOT_H + GAP
    H = y_foot + FOOT_H
    return W + (W % 2), H + (H % 2), y_lab, y_vid, y_p1, y_p2, y_foot


def col_x(i: int) -> int:
    return GAP + i * (PANEL_W + GAP)


def static_layer(design: str, slot: str, cols: list[dict]):
    W, H, y_lab, y_vid, y_p1, y_p2, y_foot = layout()
    img = np.full((H, W, 3), hex_bgr(SURFACE), np.uint8)
    items = [(GAP, 10, f"{design} ({DESIGNS[design]}): first article vs its three plate-1 copies"
              f"  ·  filmed drop {slot}", 22, True, INK),
             (GAP, 40, "60 in, 1/2 in PU mat · 959 fps capture shown 64x slower · "
              "t = 0 is the CH5 (base input) CFC-180 peak", 13, False, INK2)]
    cursors = []
    for i, c in enumerate(cols):
        x = col_x(i)
        items.append((x, y_lab + 2, f"{c['article']}  ·  {c['role']}", 14, True, INK))
        for j, line in enumerate(wrap(c["line2"], 11, PANEL_W - 4)[:3]):
            items.append((x, y_lab + 21 + 15 * j, line, 11, False, INK2))
        p1, f1, yy1 = plot_image(c["trace"], (T0_MS, T1_MS), c["standin"], False, c["plot_note"])
        p2, f2, yy2 = plot_image(c["trace"], ZOOM_MS, c["standin"], True, "")
        img[y_p1:y_p1 + PLOT_H, x:x + PANEL_W] = p1
        img[y_p2:y_p2 + PLOT_H, x:x + PANEL_W] = p2
        cursors.append(((f1, y_p1 + yy1[0], y_p1 + yy1[1], (T0_MS, T1_MS)),
                        (f2, y_p2 + yy2[0], y_p2 + yy2[1], ZOOM_MS)))
    lx = GAP
    ly = y_foot + 8
    legend = [("CH5 base input, CFC-180", C_IN, 1.4), ("top vertex resultant, CFC-180", C_TOP, 1.4),
              ("top vertex resultant, CFC-1000 (shows the seat knock)", C_TOPB, 0.9)]
    for text, col, _ in legend:
        cv2.line(img, (lx, ly + 8), (lx + 26, ly + 8), hex_bgr(col), 2, cv2.LINE_AA)
        items.append((lx + 32, ly, text, 12, False, INK))
        lx += 32 + int(font(12).getlength(text)) + 26
    items.append((lx, ly, "dashed = stand-in trace (filmed drop has no usable capture)", 12,
                  False, INK2))
    return draw_text(img, items), cursors


def frame_at(static: np.ndarray, cursors, panels: list[np.ndarray], t_ms: float) -> np.ndarray:
    W, H, y_lab, y_vid, y_p1, y_p2, y_foot = layout()
    img = static.copy()
    for i, p in enumerate(panels):
        img[y_vid:y_vid + PANEL_H, col_x(i):col_x(i) + PANEL_W] = p
    for i, cs in enumerate(cursors):
        for f, ya, yb, xl in cs:
            if xl[0] <= t_ms <= xl[1]:
                xx = col_x(i) + int(round(f(t_ms)))
                cv2.line(img, (xx, ya), (xx, yb), hex_bgr("#e34948"), 2, cv2.LINE_AA)
    return draw_text(img, [(W - GAP, 12, f"t = {t_ms:+.1f} ms", 24, True, INK, "ra")])


def preview_gif(static, cursors, pans, t_ms: np.ndarray, path: Path, t_range=(-5.0, 60.0),
                step: int = 2, scale: float = 0.5, ms_per_frame: int = 120):
    """Looping GIF of one drop (header, video panels and the full-record
    plots) for inline display in a PR comment.  One shared palette: a
    median cut of the video content plus the chart's own ink/series colors,
    so thin trace lines keep their hue."""
    from PIL import Image
    _, _, _, _, y_p1, _, _ = layout()
    idx = [m for m in range(0, len(t_ms), step) if t_range[0] <= t_ms[m] <= t_range[1]]
    frames = []
    for m in idx:
        img = frame_at(static, cursors, [np.ascontiguousarray(p[m]) for p in pans], float(t_ms[m]))
        img = cv2.GaussianBlur(img[:y_p1 + PLOT_H], (3, 3), 0.7)
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        frames.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    sample = Image.fromarray(np.vstack(frames[::max(1, len(frames) // 4)]))
    pal = sample.quantize(colors=112, method=Image.Quantize.MEDIANCUT).getpalette()[:112 * 3]
    for h in (INK, INK2, MUTED, GRID, AXIS, SURFACE, C_TOP, C_TOPB, "#e34948", "#f0efec",
              "#d6dc6a", "#b9c24a", "#eef08a"):          # + the TPU cables' yellows
        pal += [int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)]
    pimg = Image.new("P", (1, 1))
    pimg.putpalette(pal + [0] * (768 - len(pal)))
    q = [Image.fromarray(f).quantize(palette=pimg, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms_per_frame, loop=0,
              optimize=True)


def encode(frames, path: Path, ffmpeg: str, fps: int = OUT_FPS):
    first = next(frames)
    H, W = first.shape[:2]
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
           "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "slow",
           "-crf", "30", "-g", "60", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    pr.stdin.write(first.tobytes())
    for f in frames:
        pr.stdin.write(f.tobytes())
    pr.stdin.close()
    if pr.wait():
        raise RuntimeError(f"ffmpeg failed on {path}")


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------
STRIP_SLOT = "10"                       # mid-session drop: scored, not warm-up
GIF_DESIGNS = ("corny7",)               # inline preview for the design asked about
FOLDING = ("corny7", "corny8")          # designs whose specimens fold and snap back
SNAP_MS = (25.0, 70.0)                  # window of the top vertex's snap-back burst
STRIP_MS = (-3.0, 5.0, 15.0, 30.0, 42.0, 55.0)   # seated, folding, folded, ..., upright


def fig_strip(design: str, cols: list[dict], t_ms: np.ndarray, path: Path):
    """Four rows (first article, three copies) x six synced frames, with each
    row's acceleration record on the right (grey lines = the frame times)."""
    tw, gap, lab, row_gap = 1.62, 0.04, 0.36, 0.20          # inches
    th = tw * PANEL_H / PANEL_W
    trw, left, top0 = 5.2, 0.2, 0.95
    W = left + 6 * (tw + gap) + 0.62 + trw + 0.18
    H = top0 + 0.25 + 4 * (lab + th + row_gap) + 0.4
    fig = plt.figure(figsize=(W, H), dpi=100, facecolor=SURFACE)
    fig.text(left / W, 1 - 0.32 / H, f"{design} ({DESIGNS[design]}): first article vs its three "
             f"plate-1 copies, filmed drop {STRIP_SLOT}, frames synced to the acceleration record",
             fontsize=14, color=INK, va="center")
    fig.text(left / W, 1 - 0.66 / H, "Every panel at the same physical scale, plate at the same "
             "height at t = 0 (CH5 CFC-180 peak). Dashed trace = stand-in from the nearest usable "
             "drop of the same session.", fontsize=9.5, color=INK2, va="center")
    for j, ts in enumerate(STRIP_MS):
        fig.text((left + j * (tw + gap) + tw / 2) / W, 1 - (top0 + 0.12) / H, f"{ts:+.0f} ms",
                 ha="center", va="center", fontsize=10.5, color=INK)
    for i, c in enumerate(cols):
        y_lab = top0 + 0.25 + i * (lab + th + row_gap)
        fig.text(left / W, 1 - (y_lab + 0.15) / H,
                 f"{c['article']}  ·  {c['role']}  ·  {c['line2']}", fontsize=9.5, color=INK,
                 va="center", fontweight="bold" if i == 0 else "normal")
        y_img = y_lab + lab
        pan = np.load(c["panels"], mmap_mode="r")
        for j, ts in enumerate(STRIP_MS):
            ax = fig.add_axes([(left + j * (tw + gap)) / W, 1 - (y_img + th) / H, tw / W, th / H])
            m = int(np.argmin(np.abs(t_ms - ts)))
            ax.imshow(cv2.cvtColor(np.ascontiguousarray(pan[m]), cv2.COLOR_BGR2RGB))
            ax.set_axis_off()
        ax = fig.add_axes([(left + 6 * (tw + gap) + 0.62) / W, 1 - (y_img + th - 0.3) / H,
                           trw / W, (th - 0.36) / H])
        style(ax)
        tr = c["trace"]
        ls = (0, (4, 2.2)) if c["standin"] else "-"
        m = (tr["t_ms"] >= -8) & (tr["t_ms"] <= 95)
        ax.plot(tr["t_ms"][m], tr["top1000"][m], color=C_TOPB, lw=0.9, ls=ls,
                label="top vertex, CFC-1000")
        ax.plot(tr["t_ms"][m], tr["ch5_180"][m], color=C_IN, lw=1.5, ls=ls,
                label="CH5 base input, CFC-180")
        ax.plot(tr["t_ms"][m], tr["top180"][m], color=C_TOP, lw=1.5, ls=ls,
                label="top vertex, CFC-180")
        for ts in STRIP_MS:
            ax.axvline(ts, color=MUTED, lw=0.7, zorder=0)
        if design in FOLDING:
            ts, g = c["snap"]
            ax.plot(ts, g, "o", ms=6, color=C_TOP, mec=SURFACE, mew=1.2, zorder=5)
            ax.annotate(f"snap-back {ts:.1f} ms", (ts, g), xytext=(6, 10),
                        textcoords="offset points", fontsize=8, color=INK)
        ax.set_xlim(-8, 95)
        ax.set_ylim(*YLIM_G)
        ax.set_ylabel("G", fontsize=9, color=INK2)
        if i == 0:
            ax.legend(fontsize=7.5, frameon=False, loc="upper right")
        if i == len(cols) - 1:
            ax.set_xlabel("ms from the CH5 CFC-180 peak", fontsize=9, color=INK2)
    fig.savefig(path, dpi=100, facecolor=SURFACE, pil_kwargs={"quality": 90})
    plt.close(fig)


DAY_COLOR = {"2026-09-12": "#2a78d6", "2026-09-14": "#eb6834", "2026-10-17": "#1baf7a"}


def fig_sync(rows: list[dict], path: Path):
    fitted = [r for r in rows if r["sync"]]
    fig = plt.figure(figsize=(15.5, 9.4), dpi=100, facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, hspace=0.62, wspace=0.18, left=0.06, right=0.985, top=0.9,
                          bottom=0.13)

    def video_vs_model(r):
        s = r["sync"]
        t = (r["track_k"] - s["k_peak"]) / FPS * 1e3
        m = (t >= -22) & (t <= 14) & (r["trk"]["cc"] > NCC_MIN)
        y = r["track_y"][m] / (s["px_per_mm"] * SCALE)
        return t[m], y, y - sync_model_mm(s, r["trace"], t[m])

    ex = next(r for r in fitted if r["clip"] == "corny7-1st.MP4")
    ax = fig.add_subplot(gs[0, 0])
    style(ax)
    t, y, _ = video_vs_model(ex)
    tq = np.linspace(-22, 14, 600)
    ax.plot(tq, sync_model_mm(ex["sync"], ex["trace"], tq), color=C_TOP, lw=1.6,
            label="CH5 integrated twice (fitted shift, scale, speed)")
    ax.plot(t, y, "o", ms=4.2, color=INK, mec=SURFACE, mew=0.7, label="carriage tracked in the video")
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_xlabel("ms from the CH5 CFC-180 peak", fontsize=9, color=INK2)
    ax.set_ylabel("carriage, mm below its rest position", fontsize=9, color=INK2)
    ax.set_title("Example: corny7-1st (drop 1). One frame = 1.04 ms; the kink is the impact",
                 fontsize=10, color=INK, loc="left")
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    ins = ax.inset_axes([0.07, 0.5, 0.36, 0.44])
    style(ins)
    zq = np.linspace(-4, 7, 300)
    ins.plot(zq, sync_model_mm(ex["sync"], ex["trace"], zq), color=C_TOP, lw=1.6)
    mz = (t >= -4) & (t <= 7)
    ins.plot(t[mz], y[mz], "o", ms=4.2, color=INK, mec=SURFACE, mew=0.7)
    ins.axvline(0, color=MUTED, lw=0.8)
    ins.set_title("zoom", fontsize=7.5, color=INK2, loc="left")

    ax = fig.add_subplot(gs[0, 1])
    style(ax)
    for r in fitted:
        t, _, res = video_vs_model(r)
        ax.plot(t, res, color=DAY_COLOR[r["date"]], lw=0.9, alpha=0.75)
    rms = [r["sync"]["rms_px_half"] / (r["sync"]["px_per_mm"] * SCALE) for r in fitted]
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_xlabel("ms from the CH5 CFC-180 peak", fontsize=9, color=INK2)
    ax.set_ylabel("video − fit, mm", fontsize=9, color=INK2)
    ax.set_title(f"Residuals, all {len(fitted)} clips with their own capture: rms "
                 f"{min(rms):.2f}–{max(rms):.2f} mm (median {np.median(rms):.2f})",
                 fontsize=10, color=INK, loc="left")
    for dday, col in DAY_COLOR.items():
        ax.plot([], [], color=col, lw=1.6, label=f"{dday[5:]} clips")
    ax.legend(fontsize=8, frameon=False, loc="lower right", ncol=3)

    labels = [r["clip"][:-4] for r in fitted]
    for k, (key, ylab, title) in enumerate([
            ("lag_low_minus_peak_ms", "lowest point − CH5 peak, ms",
             "Lowest carriage point vs CH5 peak (used to place the clips without a capture)"),
            ("px_per_mm", "px/mm at the carriage (full res)",
             "Scale from the same fit: three camera set-ups (one per filming day)")]):
        ax = fig.add_subplot(gs[1, k])
        style(ax)
        vals = [r["sync"][key] for r in fitted]
        for i, r in enumerate(fitted):
            ax.plot(i, vals[i], "o", ms=6, color=DAY_COLOR[r["date"]], mec=SURFACE, mew=0.8)
        if key == "lag_low_minus_peak_ms":
            ax.axhline(np.median(vals), color=INK2, lw=0.9)
            ax.text(len(vals) - 0.5, np.median(vals), f" median {np.median(vals):.2f} ms",
                    fontsize=8, color=INK2, va="bottom", ha="right")
        else:
            for dday in DAY_COLOR:
                v = [x for x, r in zip(vals, fitted) if r["date"] == dday]
                if v:
                    ax.axhline(np.median(v), color=DAY_COLOR[dday], lw=0.8)
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(labels, rotation=90, fontsize=7)
        ax.set_ylabel(ylab, fontsize=9, color=INK2)
        ax.set_title(title, fontsize=10, color=INK, loc="left")
    fig.suptitle("Video ↔ accelerometer sync check: the tracked carriage against CH5's own "
                 "kinematics", fontsize=13, color=INK, x=0.06, ha="left")
    fig.savefig(path, dpi=100, facecolor=SURFACE)
    plt.close(fig)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def save_panels(job) -> Path:
    mp4, k_peak, rect, t_ms, out = job
    np.save(out, np.stack(panel_frames(mp4, k_peak, rect, t_ms)))
    return out


def cached_track(mp4: Path, work: Path) -> dict:
    f = work / f"{mp4.stem}_track.npz"
    if f.exists():
        z = np.load(f, allow_pickle=False)
        return {k: (z[k].item() if z[k].ndim == 0 else z[k]) for k in z.files}
    trk = track_clip(mp4)
    np.savez_compressed(f, **{k: np.asarray(v) for k, v in trk.items()})
    return trk


def warm_track(job) -> str:
    """Pool worker: fill the tracking cache (decoding is most of the run)."""
    mp4, work = job
    cached_track(mp4, work)
    return mp4.name


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mp4", type=Path, required=True)
    ap.add_argument("--daq", type=Path, required=True)
    ap.add_argument("--work", type=Path, default=Path("/tmp/corny-1sne-video"))
    ap.add_argument("--ffmpeg", default=shutil.which("ffmpeg") or "ffmpeg")
    ap.add_argument("--no-video", action="store_true")
    ap.add_argument("--procs", type=int, default=3)
    args = ap.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    VID.mkdir(parents=True, exist_ok=True)
    FIGV.mkdir(parents=True, exist_ok=True)

    # -- pairing --------------------------------------------------------------
    corny = {clip_name(d, s): args.mp4 / clip_name(d, s) for d in DESIGNS for s in SLOTS}
    sne = {clip_name(a, s): args.mp4 / clip_name(a, s)
           for d in DESIGNS for a in articles(d)[1:] for s in SLOTS}
    pairs = pair_clips(corny, series_events(CORNY / "raw"))
    pairs.update(pair_clips(sne, series_events(OUT / "raw")))
    committed = {r["clip"]: r for r in json.loads((FIG / "video_pairing.json").read_text())["clips"]}
    for n in sne:
        assert committed[n]["paired_event"] == pairs[n]["event"], n
    cls = session_classes()

    # -- per clip: tracking, trace choice, DAQ, sync ------------------------------
    with Pool(args.procs) as pool:
        for name in pool.imap_unordered(warm_track, [(args.mp4 / c, args.work)
                                                     for c in sorted({**corny, **sne})]):
            print(f"tracked {name}", flush=True)
    rows = []
    for d in DESIGNS:
        for a in articles(d):
            for s in SLOTS:
                name = clip_name(a, s)
                trk = cached_track(args.mp4 / name, args.work)
                ch = choose_trace(a, s, pairs[name], cls)
                cap = args.daq / f"{a}_Signal{ch['signal']}.csv"
                tr = daq_trace(cap)
                met = census_capture(cap)
                met["class"] = classify(met)
                sync = None if ch["standin"] else sync_fit(trk, tr)
                rows.append({"design": d, "article": a, "slot": s, "clip": name,
                             "pair": pairs[name], **ch, "trace": tr, "metrics": met,
                             "sync": sync, "track_k": trk["k"], "track_y": trk["y"], "trk": trk,
                             "date": pairs[name]["daq_time"][:10]})
                print(f"{name:17s} drop {ch['filmed_drop']} -> trace S{ch['signal']}"
                      f"{' (stand-in)' if ch['standin'] else ''}  class {met['class']}"
                      + (f"  sync k_peak {sync['k_peak']:.2f} lag {sync['lag_low_minus_peak_ms']:.2f} ms"
                         f" scale {sync['px_per_mm']:.3f} px/mm v0 {sync['v0_ms']:.2f} m/s"
                         f" rms {sync['rms_px_half']:.2f} px" if sync else ""), flush=True)

    fitted = [r for r in rows if r["sync"]]
    lag = float(np.median([r["sync"]["lag_low_minus_peak_ms"] for r in fitted]))
    day_scale = {}
    for r in fitted:
        day_scale.setdefault(r["date"], []).append(r["sync"]["px_per_mm"])
    # the camera did not move within a day, so every panel takes its day's
    # median fitted scale (the per-clip fits scatter 1-2 %)
    for r in rows:
        r["px_mm"] = float(np.median(day_scale[r["date"]]))
        if r["sync"]:
            r["k_peak"], r["placed_by"] = r["sync"]["k_peak"], "CH5 kinematics fit"
        else:
            r["k_peak"] = r["trk"]["k_low"] - lag * 1e-3 * FPS
            r["placed_by"] = f"lowest carriage point - {lag:.2f} ms (median lag)"

    # the wide family (corny7/corny8) folds at impact and snaps back upright;
    # the snap lands as the largest top-vertex CFC-180 burst 25-70 ms after
    # the impact (corny2 does not fold, so its value there is just the
    # largest ripple)
    for r in rows:
        tr = r["trace"]
        w = (tr["t_ms"] >= SNAP_MS[0]) & (tr["t_ms"] <= SNAP_MS[1])
        j = int(np.argmax(tr["top180"][w]))
        r["snap"] = (float(tr["t_ms"][w][j]), float(tr["top180"][w][j]))

    # -- panels ---------------------------------------------------------------------
    t_ms = np.arange(T0_MS, T1_MS + 1e-9, 1e3 / FPS)
    jobs = []
    for r in rows:
        r["rect"] = panel_rect(r["trk"], r["k_peak"], r["px_mm"])
        r["panels"] = args.work / f"{r['clip'][:-4]}_panels.npy"
        if not r["panels"].exists():
            jobs.append((args.mp4 / r["clip"], r["k_peak"], r["rect"], t_ms, r["panels"]))
    with Pool(args.procs) as pool:
        for f in pool.imap_unordered(save_panels, jobs):
            print(f"panels -> {f.name}", flush=True)

    # -- labels ---------------------------------------------------------------------
    for r in rows:
        m = r["metrics"]
        tag = "knock" if m["class"] == "knock" else "healthy seat"
        if r["standin"]:
            r["line2"] = (f"{r['date'][5:]} · {r['why']}")
            r["line3"] = (f"trace: stand-in drop {r['signal']} (T180 {m['t180']:.3f}, "
                          f"gauge {m['gauge']:.2f})")
        else:
            r["line2"] = (f"{r['date'][5:]} · drop {r['signal']} · T180 {m['t180']:.3f} · "
                          f"gauge {m['gauge']:.2f} ({tag})")
            r["line3"] = ""
        r["role"] = role(r["article"])
        r["plot_note"] = f"stand-in: drop {r['signal']}" if r["standin"] else ""

    # -- composites + videos ------------------------------------------------------------
    for d in DESIGNS:
        segs = []
        for s in SLOTS:
            cols = [next(r for r in rows if r["article"] == a and r["slot"] == s) for a in articles(d)]
            for c in cols:
                c["line2_full"] = c["line2"] + (f"\n{c['line3']}" if c["line3"] else "")
            static, cursors = static_layer(d, s, [{**c, "line2": c["line2_full"]} for c in cols])
            pans = [np.load(c["panels"], mmap_mode="r") for c in cols]
            segs.append((static, cursors, pans))
        if args.no_video:
            continue

        def frames(segs=segs):
            for static, cursors, pans in segs:
                def at(m):
                    return frame_at(static, cursors, [np.ascontiguousarray(p[m]) for p in pans],
                                    float(t_ms[m]))
                first = at(0)
                for _ in range(int(HOLD_S * OUT_FPS)):
                    yield first
                for m in range(len(t_ms)):
                    last = at(m)
                    yield last
                for _ in range(int(HOLD_S * OUT_FPS)):
                    yield last
        out = VID / f"{d}_vs_1sne{d[-1]}x.mp4"
        encode(frames(), out, args.ffmpeg)
        print(f"video -> {out} ({out.stat().st_size / 1e6:.1f} MB)")
        if d in GIF_DESIGNS:
            static, cursors, pans = segs[SLOTS.index(STRIP_SLOT)]
            gif = VID / f"{d}_vs_1sne{d[-1]}x_drop{STRIP_SLOT}_preview.gif"
            preview_gif(static, cursors, pans, t_ms, gif)
            print(f"preview -> {gif} ({gif.stat().st_size / 1e6:.1f} MB)")

    # -- figures ------------------------------------------------------------------
    for i, d in enumerate(DESIGNS):
        cols = [next(r for r in rows if r["article"] == a and r["slot"] == STRIP_SLOT)
                for a in articles(d)]
        fig_strip(d, [{**c, "line2": c["line2"] + (" · " + c["line3"] if c["line3"] else "")}
                      for c in cols], t_ms, FIGV / f"{24 + i}_video_compare_{d}.jpg")
    fig_sync(rows, FIGV / "27_video_sync_check.png")

    # -- json -------------------------------------------------------------------------
    out = {"capture_fps": FPS, "t0": "CH5 CFC-180 peak", "window_ms": [T0_MS, T1_MS],
           "lag_low_minus_peak_ms": {"median": lag,
                                     "sd": float(np.std([r["sync"]["lag_low_minus_peak_ms"]
                                                         for r in fitted], ddof=1)),
                                     "n": len(fitted)},
           "px_per_mm_by_day": {k: {"median": float(np.median(v)), "n": len(v),
                                    "cv_pct": float(100 * np.std(v, ddof=1) / np.mean(v))
                                    if len(v) > 1 else None} for k, v in day_scale.items()},
           "clips": []}
    for r in rows:
        m = r["metrics"]
        out["clips"].append({
            "clip": r["clip"], "design": r["design"], "article": r["article"], "slot": r["slot"],
            "camera_time": r["pair"]["camera_time"], "daq_time": r["pair"]["daq_time"],
            "paired_session": r["pair"]["session"], "filmed_drop": r["filmed_drop"],
            "pair_residual_s": r["pair"]["residual_s"], "pair_note": r["pair"].get("note", ""),
            "own_capture_class": r["own_class"], "trace_signal": r["signal"],
            "trace_is_standin": r["standin"], "standin_reason": r["why"],
            "trace_class": m["class"], "t180": m["t180"], "t1000": m["t1000"],
            "gauge": m["gauge"], "in_180_g": m["in_180_g"], "out_180_g": m["out_180_g"],
            "in_dv_ms": m["in_dv_ms"], "top_raw_peak_g": r["trace"]["topraw_peak_g"],
            "snap_burst_ms": r["snap"][0], "snap_burst_g": r["snap"][1],
            "placed_by": r["placed_by"], "k_peak_frame": r["k_peak"],
            "k_lowest_frame": r["trk"]["k_low"], "px_per_mm": r["px_mm"],
            "sync": r["sync"], "panel_rect_fullres_xyxy": list(map(int, r["rect"]))})
    (FIGV / "video_comparison.json").write_text(json.dumps(out, indent=1))
    print(f"figures + json -> {FIGV}")


if __name__ == "__main__":
    main()
