#!/usr/bin/env python3
"""Video kinematics analysis for the key-seat (`prc1kn`) drop-test series.

Companion to ``drop_test_key_mounted_analysis.py`` (which analyzes the
accelerometer CSVs). This script analyzes the **slow-motion videos** @ctrhjk
posted alongside the same run on
PR #67 (comment 4837240958), to extract drop kinematics that the 200 ms
accelerometer window cannot see (the full descent, the elastic rebound, and the
output-sensor fall-off).

The videos are Sony RX100 IV high-frame-rate captures conformed to a 30 fps
container, so timings are reported in *playback frames / seconds* (a fixed but
unknown slow-motion factor); they are valid for **relative** drop-to-drop
comparison, not for absolute velocity. Spatial scale is uncalibrated, so
vertical motion is in **pixels**.

Method
------
The tensegrity's orange struts are segmented in HSV each frame; the vertical
centroid of the orange mask is a clean, robust proxy for the structure's height.
From that single 1-D signal we get, per drop:

* the **first-impact frame** (first prominent peak of the centroid-down signal),
* the **descent duration** and a quadratic fit (a downward curvature confirms
  free-fall acceleration -> bungees removed, as reported),
* the **elastic rebound** (how far the centroid springs back up after impact,
  as a fraction of the drop depth),

and an overlay of all valid drops aligned at impact (a visual repeatability
check that complements the accelerometer CV).

Videos are downloaded (and cached) from the GitHub asset URLs below. Requires
``opencv-python-headless``, ``numpy``, ``scipy``, ``matplotlib`` and an ffmpeg
(``imageio-ffmpeg`` is fine for the montage frames; not required for tracking).

Usage::

    python scripts/analysis/drop_test_video_analysis.py
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

import cv2
import numpy as np
from scipy.signal import find_peaks

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# drop number -> GitHub user-attachment asset (drop 3's video was deleted by the
# uploader; "falloff" is the separate clip showing the output sensor detaching).
ASSETS = {
    "drop1": "601b8b03-e60e-4745-b99f-a4211222f642",
    "drop2": "c93cbbad-19ac-4094-ae6b-d57e4d4d839d",
    "drop4": "dc4b87a1-5a3e-442e-a010-9fddc63a2bb8",
    "drop5": "f228e20b-8e3b-455e-bfd8-b9b7267f5308",
    "falloff": "9360cd0a-1863-43ba-b5eb-8c5d5f5ed458",
}
VALID_DROPS = ["drop1", "drop2", "drop4", "drop5"]
FPS = 30.0  # container playback fps (not the capture fps)

REPO = Path(__file__).resolve().parents[2]
OUTDIR = REPO / "data" / "drop-tests" / "key-mounted" / "video-figures"
CACHE = Path(os.environ.get("VIDEO_CACHE", "/tmp/prc1kn-videos"))

# Orange-strut HSV gate.
HSV_LO = np.array([5, 90, 90])
HSV_HI = np.array([25, 255, 255])


def fetch(name: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    dst = CACHE / f"{name}.mp4"
    if not dst.exists():
        url = f"https://github.com/user-attachments/assets/{ASSETS[name]}"
        print(f"  downloading {name} ...")
        urllib.request.urlretrieve(url, dst)
    return dst


def centroid_signal(path: Path, scale: float = 0.35) -> np.ndarray:
    """Vertical centroid (px, down=+) of the orange mask, per frame."""
    cap = cv2.VideoCapture(str(path))
    cy = []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        fr = cv2.resize(fr, None, fx=scale, fy=scale)
        hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
        m = cv2.inRange(hsv, HSV_LO, HSV_HI)
        rows = m.sum(axis=1)
        area = rows.sum() / 255
        cy.append(float((np.arange(len(rows)) * rows).sum() / rows.sum())
                  if area > 30 else np.nan)
    cap.release()
    return np.array(cy, float)


def smooth(x: np.ndarray, k: int = 7) -> np.ndarray:
    idx = np.arange(len(x))
    good = ~np.isnan(x)
    x = np.interp(idx, idx[good], x[good])
    return np.convolve(x, np.ones(k) / k, mode="same")


def analyze(cy: np.ndarray) -> dict:
    cy = smooth(cy)
    f = np.arange(len(cy))
    rng = cy.max() - cy.min()
    peaks, _ = find_peaks(cy, prominence=rng * 0.4, distance=40)
    imp = int(peaks[0]) if len(peaks) else int(np.argmax(cy))
    base = cy[:imp].min()
    thr = base + 0.1 * (cy[imp] - base)
    pre = np.where(cy[:imp] <= thr)[0]
    start = int(pre[-1]) if len(pre) else max(0, imp - 150)
    seg, segy = f[start:imp], cy[start:imp]
    vel = acc = np.nan
    if len(seg) > 8:
        vel = float(np.polyfit(seg, segy, 1)[0])
        acc = float(2 * np.polyfit(seg, segy, 2)[0])
    post = cy[imp:imp + 250]
    apex = imp + int(np.argmin(post)) if len(post) > 5 else imp
    rebound = float(cy[imp] - cy[apex])
    depth = float(cy[imp] - base)
    return dict(cy=cy, base=base, impact=imp, start=start,
                descent_frames=imp - start, descent_s=round((imp - start) / FPS, 2),
                vel_px_fr=round(vel, 3), acc_px_fr2=round(acc, 4),
                rebound_px=round(rebound, 1),
                rebound_frac=round(rebound / depth, 2) if depth else np.nan,
                apex=apex, total=len(cy))


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    res = {n: analyze(centroid_signal(fetch(n))) for n in ASSETS}

    table = {n: {k: v for k, v in r.items() if k != "cy"} for n, r in res.items()}
    print(json.dumps(table, indent=2))

    # Fig 1: descent overlay aligned at first impact.
    fig, ax = plt.subplots(figsize=(7, 5))
    for n in VALID_DROPS:
        r = res[n]
        ax.plot(np.arange(r["total"]) - r["impact"], r["cy"] - r["base"],
                lw=1.3, label=f"{n} (impact f{r['impact']})")
    ax.axvline(0, color="k", ls=":", lw=1)
    ax.set_xlim(-260, 260)
    ax.invert_yaxis()
    ax.set_xlabel("frames from impact (30 fps playback)")
    ax.set_ylabel("centroid drop (px, down = +)")
    ax.set_title("prc1kn key-seat: descent + rebound, aligned at 1st impact")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUTDIR / "01_centroid_descent_overlay.png", dpi=110)

    # Fig 2: per-drop repeatability bars.
    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = np.arange(len(VALID_DROPS))
    ax.bar(x - 0.2, [res[n]["descent_s"] for n in VALID_DROPS], 0.4,
           label="descent time (s, playback)")
    ax.bar(x + 0.2, [res[n]["rebound_frac"] for n in VALID_DROPS], 0.4,
           label="rebound fraction (springs back / drop depth)")
    ax.set_xticks(x)
    ax.set_xticklabels(VALID_DROPS)
    ax.set_title("prc1kn key-seat: video kinematics repeatability")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTDIR / "02_kinematics_repeatability.png", dpi=110)

    (OUTDIR / "video_metrics.json").write_text(json.dumps(table, indent=2))
    print(f"\nWrote figures + metrics to {OUTDIR}")


if __name__ == "__main__":
    main()
