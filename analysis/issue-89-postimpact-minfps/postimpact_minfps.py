#!/usr/bin/env python3
"""Minimum-fps analysis for the POST-IMPACT deformation window (issue #89).

@sgbaird's reframing: the camera fps requirement is set not by the ~1.6 ms
deceleration pulse but by the specimen deformation over the 100s of ms
AFTER impact. This script quantifies that regime from two sources:

1. The two prc1kn 959.04 fps slow-mo videos (PR #86 branch,
   ``data/drop-tests/prc1kn-60in-5felt/video/prc1kn_video{1,2}_slomo.mp4``)
   — specimen height (deformation proxy), width, and centroid (bounce /
   brake-catch kinematics) tracked from impact turnaround to end of clip
   (~459 / 573 ms of real time at the XML-sidecar 959.04 fps time base).
2. The prc1kn set-1 DAQ captures committed on this branch
   (``prc1kn - set 1 - 1.zip``: 25 x 200 ms @ 125 kHz; CH2-4 top-vertex
   tri-axis, CH5 base plate) — post-pulse spectral content converted to
   per-band RMS *displacement*, i.e. what a camera could actually see.

Method notes
------------
* Pulldown duplicates (23.98p->30 fps re-encode) removed with the same
  inter-frame-difference detector as the committed video analyses; the
  surviving frames are camera capture frames at 959.04 fps.
* Specimen segmented with the committed HSV bands (video 2 uses the
  S>=130 floor because of the tan OSB backdrop leak); per frame the
  specimen is the tall-narrow connected blob (h 250-480 px, w 90-200 px,
  area-gated) nearest the drop axis; blur/neighbor-merged masks (w 210+)
  are rejected and bridged by interpolation, then >4-MAD spikes off a
  7-frame rolling median are rejected.
* Spatial scale: committed specimen-plane scales (3608 / 3576 px/m,
  free-fall anchored). Static specimen height 103.65 mm (committed).
* Decimation study: the 959 fps trace is subsampled to candidate frame
  rates and linearly interpolated back; errors are reported over the
  active first 150 ms after impact.

Usage::

    python postimpact_minfps.py --videos-dir /path/with/the/two/mp4s \
        --daq-dir /path/with/extracted/prc1kn-set1-csvs --out figures/

Requires numpy, scipy, matplotlib, opencv-python-headless.
"""
from __future__ import annotations

import argparse, glob, json, os, pickle
import numpy as np
from scipy import signal
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FPS = 959.04
SCALE = {"v1": 3608.16, "v2": 3576.0}     # px/m (committed video_metrics.json)
CATCH_MS = {"v1": 79.2, "v2": 76.0}       # brake catch after impact (committed)
STATIC_MM = 103.65                        # static specimen height (committed)
VIDEOS = {"v1": "prc1kn_video1_slomo.mp4", "v2": "prc1kn_video2_slomo.mp4"}
HSV_HI = np.array([26, 255, 255])
G = 9.80665
FS_DAQ = 125000.0


def extract_blobs(path: str, tag: str, cache: str) -> dict:
    """All orange blobs >=2000 px per frame + pulldown-duplicate mask."""
    if os.path.exists(cache):
        return pickle.load(open(cache, "rb"))
    hsv_lo = np.array([4, 80, 60]) if tag == "v1" else np.array([4, 130, 60])
    cap = cv2.VideoCapture(path)
    frames_gray, allblobs = [], []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        frames_gray.append(cv2.resize(g, (g.shape[1] // 4, g.shape[0] // 4)))
        mask = cv2.inRange(cv2.cvtColor(fr, cv2.COLOR_BGR2HSV), hsv_lo, HSV_HI)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        n, lab, stats, cent = cv2.connectedComponentsWithStats(mask)
        allblobs.append([[stats[i, cv2.CC_STAT_TOP], stats[i, cv2.CC_STAT_HEIGHT],
                          stats[i, cv2.CC_STAT_LEFT], stats[i, cv2.CC_STAT_WIDTH],
                          stats[i, cv2.CC_STAT_AREA], cent[i][0], cent[i][1]]
                         for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= 2000])
    cap.release()
    n = len(frames_gray)
    d = np.array([np.abs(frames_gray[i].astype(np.float32)
                         - frames_gray[i - 1].astype(np.float32)).mean()
                  for i in range(1, n)])
    med = np.array([np.median(d[max(0, i - 10):i + 11]) for i in range(len(d))])
    keep = np.r_[True, ~(d < 0.12 * med)]
    out = dict(allblobs=allblobs, keep=keep)
    pickle.dump(out, open(cache, "wb"))
    return out


def build_trace(tag: str, raw: dict) -> dict:
    ab = [raw["allblobs"][i] for i in np.where(raw["keep"])[0]]
    nu = len(ab)
    # shape gate: tall narrow blob = intact specimen silhouette
    # (w <= 200 rejects blur/neighbor-merged masks, which run 210-240 wide)
    area_lo, area_hi = (8000, 22000) if tag == "v1" else (4500, 16000)

    def cands(fb):
        return [b for b in fb if 250 <= b[1] <= 480 and 90 <= b[3] <= 200
                and area_lo <= b[4] <= area_hi]

    cx_ref = float(np.median([b[5] for fb in ab for b in cands(fb)]))
    sel = np.full((nu, 7), np.nan)
    for i, fb in enumerate(ab):
        c = cands(fb)
        if c:
            sel[i] = min(c, key=lambda b: abs(b[5] - cx_ref))
    cy = sel[:, 6]
    t0 = int(np.nanargmax(cy))                      # turnaround (bounce bottom)
    miss = float(np.mean(np.isnan(cy[t0:])))

    def interp(x):
        s = x[t0:]; idx = np.arange(len(s)); g = np.isfinite(s)
        s = np.interp(idx, idx[g], s[g])
        med = signal.medfilt(s, 7)
        mad = np.median(np.abs(s - med)) + 1e-9
        g2 = np.abs(s - med) <= 4 * mad
        return np.interp(idx, idx[g2], s[g2])

    mm = 1000.0 / SCALE[tag]
    tr = dict(t=np.arange(nu - t0) / FPS * 1e3,
              h=interp(sel[:, 1]) * mm, w=interp(sel[:, 3]) * mm,
              cy=interp(sel[:, 6]) * mm, t0=t0, miss=miss)
    print(f"{tag}: turnaround uframe {t0}, post {nu-t0} frames "
          f"({tr['t'][-1]:.0f} ms), missing/interp {miss:.0%}")
    return tr


def decimate(tr: dict, key: str, tmax: float = 150.0) -> dict:
    m_ = tr["t"] <= tmax
    x, t = tr[key][m_], tr["t"][m_]
    out = {}
    for fps in [30, 60, 120, 240, 480, 959]:
        idx = np.unique(np.arange(0, len(x), FPS / fps).astype(int))
        xr = np.interp(t, t[idx], x[idx])
        err = x - xr
        out[fps] = dict(rms_mm=float(np.sqrt(np.mean(err ** 2))),
                        max_mm=float(np.abs(err).max()),
                        dip_err_mm=(float(abs(xr.min() - x.min()))
                                    if key == "h" else None))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos-dir", required=True)
    ap.add_argument("--daq-dir", required=True,
                    help="directory with the extracted prc1kn set-1 CSVs")
    ap.add_argument("--out", default="figures")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    M: dict = {}

    V = {}
    for tag, fn in VIDEOS.items():
        raw = extract_blobs(os.path.join(args.videos_dir, fn), tag,
                            os.path.join(args.out, f"{tag}_allblobs.pkl"))
        V[tag] = build_trace(tag, raw)

    spec = {}
    for tag, tr in V.items():
        q = tr["t"] > 300
        noise = float(tr["h"][q].std())
        hdip = float(tr["h"][(tr["t"] > 20) & (tr["t"] < 100)].min())
        hset = float(np.median(tr["h"][q]))
        M[tag] = dict(post_window_ms=float(tr["t"][-1]), miss_frac=tr["miss"],
                      h_noise_mm=noise, h_dip_mm=hdip, h_settled_mm=hset,
                      dip_pct=100 * (hset - hdip) / hset)
        x = signal.detrend(tr["h"][tr["t"] <= 150])
        f, p = signal.welch(x, fs=FPS, nperseg=128)
        pn = noise ** 2 / (FPS / 2)               # white tracking-noise PSD
        above = f[p > 3 * pn]
        cum = np.cumsum(p) / p.sum()
        spec[tag] = (f, p, pn)
        M[tag]["h_f95_hz"] = float(f[np.searchsorted(cum, 0.95)])
        M[tag]["h_content_above_noise_hz"] = (float(above.max())
                                              if len(above) else 0.0)
        M[tag]["decim_h"] = decimate(tr, "h")
        M[tag]["decim_cy"] = decimate(tr, "cy")
        print(f"  {tag}: dip {hdip:.1f} -> settled {hset:.1f} mm "
              f"({M[tag]['dip_pct']:.1f}%), noise {noise:.2f} mm, "
              f"f95 {M[tag]['h_f95_hz']:.0f} Hz")

    # ------------------------------------------------------------- DAQ
    files = sorted(glob.glob(os.path.join(args.daq_dir, "*.csv")))
    psds = []
    for fn in files:
        a = np.genfromtxt(fn, delimiter=",", skip_header=10, usecols=(0, 1, 2, 3, 4))
        ch = a[:, 1:5] - np.median(a[:200, 1:5], axis=0)
        i0 = int(np.argmax(np.abs(ch[: int(0.03 * FS_DAQ), 3])))
        s = i0 + int(0.005 * FS_DAQ)
        f_daq, p = signal.welch(ch[s:, 0:3], fs=FS_DAQ, nperseg=16384, axis=0)
        psds.append(p.sum(axis=1))
    P_top = np.mean(psds, axis=0)
    bd = {}
    for lo, hi in [(10, 20), (20, 50), (50, 100), (100, 200), (200, 500),
                   (500, 1000), (1000, 3000)]:
        m_ = (f_daq >= lo) & (f_daq < hi)
        Sx = P_top[m_] * G ** 2 / (2 * np.pi * f_daq[m_]) ** 4
        bd[f"{lo}-{hi}"] = dict(
            x_rms_um=float(np.sqrt(np.trapezoid(Sx, f_daq[m_])) * 1e6),
            a_rms_g=float(np.sqrt(np.trapezoid(P_top[m_], f_daq[m_]))))
    M["daq_band_disp_top"] = bd
    M["daq_n"] = len(files)

    # --------------------------------------------------------- figures
    plt.rcParams.update({"figure.dpi": 110, "font.size": 9})

    fig, axes = plt.subplots(2, 2, figsize=(11, 6.6), sharex="col",
                             gridspec_kw={"width_ratios": [2.2, 1]})
    for i, tag in enumerate(["v1", "v2"]):
        tr = V[tag]
        for j, (tmax, ttl) in enumerate([(None, "full post-impact window"),
                                         (120, "first 120 ms")]):
            ax = axes[i, j]
            m_ = (np.ones(len(tr["t"]), bool) if tmax is None
                  else tr["t"] <= tmax)
            ax.plot(tr["t"][m_], tr["h"][m_], lw=0.8, color="#d95f02")
            ax2 = ax.twinx()
            ax2.plot(tr["t"][m_], tr["cy"][m_], lw=0.8, color="#1b9e77")
            ax.axhline(STATIC_MM, color="k", lw=0.6, ls=":")
            ax.axvline(CATCH_MS[tag], color="0.4", lw=0.8, ls="--")
            if j == 0:
                ax.annotate("brake catch", (CATCH_MS[tag], ax.get_ylim()[1]),
                            xytext=(4, -10), textcoords="offset points",
                            fontsize=8)
                ax.set_ylabel(f"prc1kn drop {i+1}\nheight (mm)",
                              color="#d95f02")
                ax2.set_ylabel("centroid y (mm, image)", color="#1b9e77")
            ax.set_title(f"drop {i+1} — {ttl}", fontsize=9)
            if i == 1:
                ax.set_xlabel("time after impact turnaround (ms)")
    fig.suptitle("prc1kn 60 in drops @ 959 fps — post-impact deformation & "
                 "bounce (orange: height = deformation proxy; green: centroid)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(f"{args.out}/01_postimpact_traces.png", bbox_inches="tight")
    plt.close(fig)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
    for tag, c in [("v1", "#d95f02"), ("v2", "#7570b3")]:
        f, p, pn = spec[tag]
        a1.loglog(f[1:], p[1:], color=c, lw=1.2, label=f"drop {tag[-1]} h(t) PSD")
        a1.axhline(pn, color=c, lw=0.7, ls=":",
                   label=f"drop {tag[-1]} tracking-noise floor")
    a1.set_xlabel("frequency (Hz)"); a1.set_ylabel("PSD (mm$^2$/Hz)")
    a1.set_title("Video deformation signal, first 150 ms after impact\n"
                 "(959 fps; content above the dotted noise floor is real)")
    a1.legend(fontsize=7); a1.grid(alpha=0.3, which="both")
    asd_x = (np.sqrt(P_top * G ** 2)
             / (2 * np.pi * np.maximum(f_daq, 1)) ** 2 * 1e6)
    a2.loglog(f_daq[2:], asd_x[2:], color="#1b9e77", lw=1.0)
    px_um = 1000 / 3.608
    a2.axhline(px_um, color="k", lw=0.8, ls="--")
    a2.text(1500, px_um * 1.25, "1 camera pixel (0.28 mm)", fontsize=8)
    a2.axhline(px_um / 10, color="0.5", lw=0.8, ls="--")
    a2.text(1500, px_um / 10 * 1.25, "0.1 px (subpixel DIC limit)",
            fontsize=8, color="0.4")
    a2.set_xlim(8, 20000); a2.set_xlabel("frequency (Hz)")
    a2.set_ylabel(r"displacement ASD ($\mu$m/$\sqrt{\rm Hz}$)")
    a2.set_title("DAQ top-vertex, post-pulse window (+5$\\to$195 ms), n=%d "
                 "drops\ndisplacement equivalent of the acceleration spectrum"
                 % len(files))
    a2.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(f"{args.out}/02_spectra.png", bbox_inches="tight")
    plt.close(fig)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
    tr = V["v1"]; m_ = tr["t"] <= 150
    x, t = tr["h"][m_], tr["t"][m_]
    for fps, c in [(959, "0.75"), (240, "#1b9e77"), (120, "#7570b3"),
                   (60, "#e7298a"), (30, "#d95f02")]:
        idx = np.unique(np.arange(0, len(x), FPS / fps).astype(int))
        a1.plot(t[idx], x[idx], marker="o" if fps < 900 else None, ms=2.5,
                lw=1.0, color=c, label=f"{fps} fps", alpha=0.9)
    a1.axhline(STATIC_MM, color="k", lw=0.6, ls=":")
    a1.set_xlabel("time after impact (ms)")
    a1.set_ylabel("specimen height (mm)")
    a1.set_title("drop 1 deformation trace resampled at candidate frame rates")
    a1.legend(fontsize=8); a1.grid(alpha=0.3)
    fpss = [30, 60, 120, 240, 480]
    for tag, c in [("v1", "#d95f02"), ("v2", "#7570b3")]:
        a2.plot(fpss, [M[tag]["decim_h"][f]["rms_mm"] for f in fpss], "o-",
                color=c, label=f"drop {tag[-1]} h(t) RMS err")
        a2.plot(fpss, [M[tag]["decim_h"][f]["max_mm"] for f in fpss], "s--",
                color=c, alpha=0.55, label=f"drop {tag[-1]} max err")
    a2.axhline(M["v1"]["h_noise_mm"], color="k", ls=":", lw=0.8)
    a2.text(300, M["v1"]["h_noise_mm"] * 1.08, "tracking noise (1$\\sigma$)",
            fontsize=8)
    a2.set_xscale("log"); a2.set_xticks(fpss); a2.set_xticklabels(fpss)
    a2.set_xlabel("simulated frame rate (fps)")
    a2.set_ylabel("reconstruction error (mm)")
    a2.set_title("error vs frame rate, first 150 ms after impact")
    a2.legend(fontsize=8); a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{args.out}/03_decimation.png", bbox_inches="tight")
    plt.close(fig)

    with open(f"{args.out}/minfps_metrics.json", "w") as fh:
        json.dump(M, fh, indent=2, default=float)
    print("figures + metrics written to", args.out)


if __name__ == "__main__":
    main()
