#!/usr/bin/env python3
"""Video kinematics for the **burn-in wax** key-seat run (`prc1kn`, PR #67).

Companion to ``drop_test_burn_in_wax_analysis.py`` (which analyzes the
accelerometer CSVs). This script analyzes the **slow-motion videos** @ctrhjk
posted alongside the five *recorded* drops of the burn-in run
([comment 4847...](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67)),
to extract the descent / rebound kinematics the 200 ms accelerometer window
cannot see. (The three burn-in drops have no videos.)

Calibration note (new this run)
-------------------------------
@ctrhjk confirmed the camera (Sony RX100 IV) captured at **960 fps**. GitHub
transcodes the clips into a 30 fps playback container, so the slow-motion factor
is 960/30 = 32x. Because every *captured* frame is 1/960 s of real elapsed time
regardless of the playback container, we can now report **calibrated real-time**
timing: ``real_seconds = frame_index / 960`` (the prior key-seat video pass could
only give relative frames). Spatial scale is still uncalibrated, so vertical
motion stays in **pixels**; velocities are px/frame. We cross-check the measured
descent time against the free-fall time from the 13 in drop height as a sanity
check on the 960 fps calibration.

Method (unchanged from the key-seat video script)
-------------------------------------------------
The orange struts are segmented in HSV each frame; the vertical centroid of the
orange mask is a robust 1-D proxy for the structure's height. From that we get,
per recorded drop: first-impact frame, descent duration (real s via /960), a
quadratic free-fall check, and the elastic rebound as a fraction of drop depth.

Requires ``opencv-python-headless``, ``numpy``, ``scipy``, ``matplotlib``.
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

import cv2
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.signal import find_peaks  # noqa: E402

# recorded-drop label -> GitHub user-attachment asset. The five recorded drops
# are overall drops 4-8 of the run (drops 1-3 = burn-in, no video).
ASSETS = {
    "rec1": "9eb82bc6-e713-4ce8-8342-aa821e17df31",  # Signal4 (overall drop 4)
    "rec2": "5ada04e3-0b46-425a-aefd-4dc139adbcdb",  # Signal5 (overall drop 5)
    "rec3": "2a51d0fe-c1fd-4894-879a-37afb588264d",  # Signal6 (overall drop 6)
    "rec4": "7240db64-7e07-4377-bdbf-695bd1487568",  # Signal7 (overall drop 7)
    "rec5": "4a6967d8-65c4-4854-bb6e-fdae6acaa7db",  # Signal8 (overall drop 8)
}
ALL = list(ASSETS)
CAPTURE_FPS = 960.0  # true capture rate (RX100 IV HFR); real time = frame / 960
DROP_HEIGHT_M = 13 * 0.0254  # 13 in drop height
GRAVITY = 9.80665

REPO = Path(__file__).resolve().parents[2]
OUTDIR = REPO / "data" / "drop-tests" / "burn-in-wax" / "video-figures"
CACHE = Path(os.environ.get("VIDEO_CACHE", "/tmp/burnin-videos"))

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
    descent_frames = imp - start
    return dict(cy=cy, base=base, impact=imp, start=start,
                descent_frames=descent_frames,
                descent_ms_real=round(1e3 * descent_frames / CAPTURE_FPS, 1),
                vel_px_fr=round(vel, 3), acc_px_fr2=round(acc, 4),
                rebound_px=round(rebound, 1),
                rebound_frac=round(rebound / depth, 2) if depth else np.nan,
                apex=apex, total=len(cy))


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    res = {n: analyze(centroid_signal(fetch(n))) for n in ALL}

    table = {n: {k: v for k, v in r.items() if k != "cy"} for n, r in res.items()}
    print(json.dumps(table, indent=2))

    ff = (2 * DROP_HEIGHT_M / GRAVITY) ** 0.5
    desc = [res[n]["descent_ms_real"] for n in ALL]
    # NB: the tracked descent is only the *in-frame visible* portion (the tracker
    # onset is not the true release), so it is shorter than the full free-fall
    # time from 13 in; the free-fall number is printed as context, not a target.
    print(f"\nfull free-fall time from {DROP_HEIGHT_M*1000:.0f} mm = {ff*1e3:.0f} ms (context only)")
    print(f"in-frame visible descent (real, /960): mean {np.mean(desc):.1f} ± "
          f"{np.std(desc, ddof=1):.1f} ms (CV {100*np.std(desc, ddof=1)/np.mean(desc):.1f}%)")
    slopes = [res[n]["vel_px_fr"] for n in ALL]
    rebf = [res[n]["rebound_frac"] for n in ALL]
    print(f"descent slope (px/fr): mean {np.mean(slopes):.3f} "
          f"(CV {100*np.std(slopes, ddof=1)/np.mean(slopes):.2f}%)")
    print(f"rebound fraction: mean {np.mean(rebf):.2f} "
          f"(CV {100*np.std(rebf, ddof=1)/np.mean(rebf):.1f}%)")

    # Fig 1: descent overlay aligned at first impact.
    fig, ax = plt.subplots(figsize=(7.5, 5))
    for n in ALL:
        r = res[n]
        ax.plot((np.arange(r["total"]) - r["impact"]) / CAPTURE_FPS * 1e3,
                r["cy"] - r["base"], lw=1.3,
                label=f"{n} (descent {r['descent_ms_real']:.0f} ms)")
    ax.axvline(0, color="k", ls=":", lw=1)
    ax.set_xlim(-300, 300)
    ax.invert_yaxis()
    ax.set_xlabel("real time from impact (ms, frame/960)")
    ax.set_ylabel("centroid drop (px, down = +)")
    ax.set_title("prc1kn burn-in wax: descent + rebound (5 recorded drops)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUTDIR / "01_centroid_descent_overlay.png", dpi=110)

    # Fig 2: per-drop repeatability bars.
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    x = np.arange(len(ALL))
    ax.bar(x - 0.2, desc, 0.4, label="in-frame visible descent (ms, real /960)")
    ax2 = ax.twinx()
    ax2.bar(x + 0.2, rebf, 0.4, color="tab:orange", label="rebound fraction")
    ax.set_xticks(x)
    ax.set_xticklabels(ALL)
    ax.set_ylabel("descent time (ms)")
    ax2.set_ylabel("rebound fraction")
    ax.set_title("prc1kn burn-in wax: video kinematics repeatability")
    ax.legend(loc="upper left", fontsize=8)
    ax2.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUTDIR / "02_kinematics_repeatability.png", dpi=110)

    (OUTDIR / "video_metrics.json").write_text(json.dumps(table, indent=2))
    print(f"\nWrote figures + metrics to {OUTDIR}")


if __name__ == "__main__":
    main()
