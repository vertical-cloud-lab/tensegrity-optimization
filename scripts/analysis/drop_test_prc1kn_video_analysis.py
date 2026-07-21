#!/usr/bin/env python3
"""Frame-by-frame video kinematics for the two prc1kn drops (60 in campaign).

Companion to ``drop_test_prc1kn_60in_5felts_analysis.py`` (accelerometer) and
sibling of ``drop_test_60in_5felts_video_analysis.py`` (7xadt6/9GMQYQ videos),
whose trackers this script imports and reuses. Analyzes the two slow-motion
videos @me-madsen attached directly to PR #86 (2026-07-21):

    data/drop-tests/prc1kn-60in-5felt/video/prc1kn_video1_slomo.mp4
    data/drop-tests/prc1kn-60in-5felt/video/prc1kn_video2_slomo.mp4

Time base — exact, from the camera XML sidecars
-----------------------------------------------
Unlike the 7xadt6/9GMQYQ pass (which had to *infer* the capture rate from a
PR comment), the Sony non-real-time metadata XMLs posted with the videos
state it outright::

    <VideoFrame videoCodec="AVC_1920_1080_HP@L41"
                captureFps="959.04p" formatFps="23.98p"/>
    <Device manufacturer="Sony" modelName="DSC-RX100M4"/>
    <RecordingMode type="slowAndQuickMotion"/>

so real time = unique capture frame / **959.04**. The attached mp4s are
1080x1920 / 30 fps portrait re-encodes (crop + trim of the 23.98p camera
clips), so the 23.98->30 pulldown duplicates (~1 in 5) are removed with the
same two-pass detector used for the YouTube re-encodes; the surviving frames
are camera capture frames.

Calibration grid
----------------
Both videos have a black/white checkerboard (20 mm squares, per @me-madsen)
taped behind the drop axis — at a *different depth* in each video (video 1:
just behind the specimen; video 2: on the far backdrop). The grid's vertical
period (2 squares = 40 mm) is measured by autocorrelation of column-strip
intensity profiles in a pre-entry frame. Because the grid is not in the
specimen's plane, its scale differs from the specimen-plane scale by the
camera-depth ratio; both scales are reported and their ratio quantifies the
parallax error you would make by reading specimen motion directly off the
grid. The specimen-plane scale keeps the free-fall anchor of the sibling
script (arrival speed = free fall from 60 in, corroborated by the DAQ plate
delta-v) so the three specimens stay directly comparable.

Requires ``opencv-python-headless``, ``numpy``, ``scipy``, ``matplotlib``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import drop_test_60in_5felts_video_analysis as base  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
VIDDIR = REPO / "data" / "drop-tests" / "prc1kn-60in-5felt" / "video"
OUTDIR = VIDDIR / "figures"
DAQ_METRICS = (REPO / "data" / "drop-tests" / "prc1kn-60in-5felt"
               / "figures" / "prc1kn_60in_metrics.json")
PRIOR_VIDEO_METRICS = (REPO / "data" / "drop-tests" / "60in-5felts-validation"
                       / "video" / "figures" / "video_metrics.json")

VIDEOS = {"drop1": "prc1kn_video1_slomo.mp4",
          "drop2": "prc1kn_video2_slomo.mp4"}

CAPTURE_FPS = 959.04           # from the XML sidecars (captureFps="959.04p")
GRID_SQUARE_MM = 20.0          # @me-madsen: each b/w segment is 20 mm tall
base.CAPTURE_FPS = CAPTURE_FPS  # analyze()/figures read the module global

# Per-video segmentation. The attached clips are 1080x1920 (2.25x the pixel
# area of the YouTube re-encodes). Video 2's tan OSB backdrop leaks into the
# permissive orange band (567k px at S>=80 with no specimen in frame vs the
# specimen's ~18k) and the leak's frame-to-frame flicker then out-correlates
# the specimen, so that video runs with a high saturation floor (S>=130:
# leak 4.9k px, specimen 17.6k). Video 1's backdrop is clean (1.1k px leak)
# and keeps the sibling script's permissive band; its higher mass floor
# keeps prc1kn's blurred partial-entry frames (cable + strut tips, spurious
# correlation spikes to ~70 px/frame) out of the trackers.
TUNING = {
    "drop1": {"hsv_lo": np.array([4, 80, 60]), "min_mass": 12000.0},
    "drop2": {"hsv_lo": np.array([4, 130, 60]), "min_mass": 6000.0},
}


def analyze_robust(v: dict, keep: np.ndarray) -> tuple[dict, np.ndarray]:
    """base.analyze with spike-proof event detection.

    prc1kn's entry frames produce isolated correlation mislocks (spikes up
    to ~70 px/frame against a ~19 px/frame descent), so the peak-velocity
    event search runs on a 5-frame median-filtered series; contact,
    turnaround, snap-back, rebound and the descent fit then proceed on the
    raw series exactly as in the sibling script. The descent fit is also
    guarded against degenerate windows.
    """
    n_dup2 = 0
    for _ in range(3):
        prof = base.clean_profiles(v, keep)
        vel, mass = base.velocity_series(prof)
        loc = np.array([np.nanmedian(np.abs(
            vel[max(1, f - 3):f + 4])) if not np.isnan(vel[f]) else np.nan
            for f in range(len(vel))])
        dup2 = (~np.isnan(vel)) & (loc > 3.0) & (np.abs(vel) < 0.25 * loc)
        if not dup2.any():
            break
        n_dup2 += int(dup2.sum())
        keep = keep[~dup2]
    f = np.arange(len(vel), dtype=float)

    # events — vmax on a median-filtered copy so isolated mislocks can't win
    velm = np.array([np.nanmedian(vel[max(1, i - 2):i + 3])
                     if not np.isnan(vel[i]) else np.nan
                     for i in range(len(vel))])
    vmax_i = int(np.nanargmax(np.where(np.isnan(velm), -np.inf, velm)))
    v_peak = float(velm[vmax_i])
    after = np.where(~np.isnan(vel) & (f > vmax_i) & (vel < -2.0))[0]
    turn = int(after[0]) if len(after) else len(vel) - 1
    down = np.where(~np.isnan(vel[:turn]) & (vel[:turn] > 0.7 * v_peak))[0]
    contact = int(down[-1])
    pulse_frames = turn - contact
    entry_ok = np.where(~np.isnan(vel) & (vel > 0.7 * v_peak)
                        & (base.profile_top(prof) > 25))[0]
    d_lo = int(entry_ok[0])

    desc = np.arange(d_lo, contact + 1)
    B = 5 if len(desc) > 15 else 3
    starts = desc[desc + B <= contact - 1]
    mids, v5 = base.baseline_velocity(prof, starts, B)
    med5 = np.median(v5)
    ok = (v5 > 0.75 * med5) & (v5 < 1.25 * med5)
    mids, v5 = mids[ok], v5[ok]
    if len(v5) >= 3:
        coef, cov = np.polyfit(mids, v5, 1, cov=True)
        a_px, a_err = float(coef[0]), float(np.sqrt(cov[0, 0]))
        fit_res = float(np.std(v5 - np.polyval(coef, mids)))
    else:
        coef, a_px, a_err, fit_res = np.array([0.0, med5]), np.nan, np.nan, np.nan

    v_imp_px = float(np.nanmedian(vel[max(d_lo, contact - 12):contact + 1]))
    scale = v_imp_px * base.CAPTURE_FPS / base.FREE_FALL_V
    g_px_expected = base.GRAVITY * scale / base.CAPTURE_FPS ** 2

    snap_px = float(-np.nanmin(vel[turn:turn + 5]))
    sus = vel[turn + 4:turn + 28]
    v_reb_px = float(-np.nanmedian(sus)) if np.isfinite(sus).any() else np.nan
    still = np.where(~np.isnan(vel) & (f > turn + 6) & (np.abs(vel) < 0.5))[0]
    catch = int(still[0]) if len(still) else None
    brake_g = rise_px = None
    if catch and catch - turn > 20:
        seg = np.arange(turn + 6, catch)
        mm = ~np.isnan(vel[seg])
        brake_a = float(np.polyfit(seg[mm].astype(float), vel[seg][mm], 1)[0])
        brake_g = brake_a * base.CAPTURE_FPS ** 2 / scale / base.GRAVITY
        rise_px = float(-np.nansum(np.where(np.isnan(vel[turn:catch]), 0,
                                            vel[turn:catch])))

    cc_h = v["cc_bot"][keep] - v["cc_top"][keep]
    cc_a = v["cc_area"][keep]
    hold0 = (catch or turn + 100) + 20
    a_hold = np.nanmedian(cc_a[hold0:])
    h_hold = float(np.nanmedian(cc_h[hold0:]))
    w = np.arange(max(0, turn - 15), min(len(cc_h), turn + 15))
    wv = w[(cc_a[w] > 0.6 * a_hold) & ~np.isnan(cc_h[w])]
    comp = {"valid_frames_near_impact": int(len(wv)),
            "static_height_px": h_hold,
            "static_height_mm": h_hold / scale * 1000}
    if pulse_frames <= 3:
        comp["note"] = ("deceleration pulse spans <= 3 capture frames; "
                        "peak compression occurs between frames and is not "
                        "resolvable with mask-based tracking at ~960 fps")

    res = {
        "descent_window": [int(d_lo), int(contact)],
        "contact_frame": int(contact), "turnaround_frame": int(turn),
        "catch_frame": catch,
        "n_velocity_dups_removed": n_dup2,
        "descent_flatness": {
            "a_px_per_frame2": a_px, "a_err": a_err,
            "expected_g_px_per_frame2": float(g_px_expected),
            "residual_px_per_frame": fit_res, "n_points": int(len(v5)),
            "interpretation": "free-fall velocity gain cancelled by "
                              "perspective scale gradient",
        },
        "scale_px_per_m": float(scale),
        "scale_basis": "arrival speed assumed = free fall from 60 in "
                       "(5.47 m/s); DAQ plate dv corroborates",
        "v_impact_px_per_frame": v_imp_px,
        "v_impact_ms_assumed": float(base.FREE_FALL_V),
        "impact_pulse_frames": int(pulse_frames),
        "impact_pulse_ms": float(pulse_frames / base.CAPTURE_FPS * 1000),
        "snapback_peak_px_per_frame": snap_px,
        "snapback_ratio": float(snap_px / v_imp_px),
        "v_rebound_px_per_frame": v_reb_px,
        "v_rebound_ms": float(v_reb_px * base.CAPTURE_FPS / scale),
        "coeff_restitution_scalefree": float(v_reb_px / v_imp_px),
        "brake_decel_g": brake_g,
        "catch_delay_ms": (float((catch - turn) / base.CAPTURE_FPS * 1000)
                           if catch else None),
        "catch_rise_px": rise_px,
        "catch_rise_mm": (rise_px / scale * 1000) if rise_px else None,
        "specimen_compression": comp,
        "series": {"f": f, "vel": vel, "mass": mass,
                   "desc_mids": mids, "desc_v5": v5, "coef": coef},
    }
    return res, keep


# ------------------------------------------------------------------- grid
def grid_scale_px_per_mm(frame_bgr: np.ndarray) -> dict:
    """Vertical grid period via autocorrelation of column-strip profiles.

    Returns px/mm at the *grid plane* plus the detection details. Uses the
    checkerboard's vertical period = 2 squares = 40 mm.
    """
    g = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    m = cv2.blur(g, (31, 31))
    sd = np.sqrt(np.clip(cv2.blur(g * g, (31, 31)) - m * m, 0, None))
    mask = (sd > 28).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    nlab, _, st, _ = cv2.connectedComponentsWithStats(mask)
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, w, h = (int(st[i, k]) for k in (cv2.CC_STAT_LEFT, cv2.CC_STAT_TOP,
                                          cv2.CC_STAT_WIDTH,
                                          cv2.CC_STAT_HEIGHT))
    # shave the bbox border (paper margin / tape)
    pad_x, pad_y = w // 8, h // 8
    roi = g[y + pad_y:y + h - pad_y, x + pad_x:x + w - pad_x]
    periods = []
    for x0 in range(0, roi.shape[1] - 6, 6):
        col = roi[:, x0:x0 + 6].mean(axis=1)
        col -= col.mean()
        if np.std(col) < 8:            # strip missed the pattern
            continue
        ac = np.correlate(col, col, "full")[len(col) - 1:]
        if ac[0] <= 0:
            continue
        ac /= ac[0]
        # first local max beyond the central lobe with meaningful correlation
        lag0 = int(np.argmax(ac < 0))  # end of central lobe
        if lag0 == 0 or lag0 + 5 >= len(ac):
            continue
        seg = ac[lag0:min(len(ac), lag0 + 4 * lag0)]
        k = lag0 + int(np.argmax(seg))
        if ac[k] > 0.25 and 0 < k < len(ac) - 1:
            periods.append(k + base._subpixel(ac, k))
    period = float(np.median(periods))
    return {"bbox_xywh": [x, y, w, h],
            "n_strips": len(periods),
            "period_px": period,
            "period_iqr_px": float(np.subtract(
                *np.percentile(periods, [75, 25]))),
            "px_per_mm_at_grid": period / (2 * GRID_SQUARE_MM)}


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    daq = json.loads(DAQ_METRICS.read_text()) if DAQ_METRICS.exists() else None
    prior = (json.loads(PRIOR_VIDEO_METRICS.read_text())
             if PRIOR_VIDEO_METRICS.exists() else None)
    colors = {"drop1": "#009E73", "drop2": "#CC79A7"}
    results = {}

    for drop, fname in VIDEOS.items():
        print(f"== {drop}: {fname}")
        base.HSV_LO = TUNING[drop]["hsv_lo"]
        base.MIN_MASS = TUNING[drop]["min_mass"]
        v = base.read_video(VIDDIR / fname)
        keep0 = base.dedup_pixel(v)
        r, keep = analyze_robust(v, keep0)
        dup = 1 - len(keep) / v["n_frames"]
        r["keep"] = keep
        r["video"] = {"file": fname, "playback_frames": v["n_frames"],
                      "unique_frames": len(keep),
                      "duplicate_fraction": float(dup),
                      "real_duration_s": float(len(keep) / CAPTURE_FPS)}

        # grid scale from a pre-entry frame (specimen not yet in frame)
        cap = cv2.VideoCapture(str(VIDDIR / fname))
        ok, fr0 = cap.read()
        cap.release()
        grid = grid_scale_px_per_mm(fr0)
        spec_px_mm = r["scale_px_per_m"] / 1000.0
        grid["px_per_mm_at_specimen_freefall_anchor"] = spec_px_mm
        grid["specimen_over_grid_scale"] = spec_px_mm / grid["px_per_mm_at_grid"]
        grid["speed_error_if_grid_used_directly_pct"] = (
            (grid["specimen_over_grid_scale"] - 1) * 100)
        r["grid"] = grid
        results[drop] = r

        print(f"   {v['n_frames']} -> {len(keep)} unique (dup {dup:.1%} incl. "
              f"{r['n_velocity_dups_removed']} re-encoded), real "
              f"{len(keep)/CAPTURE_FPS:.3f} s")
        print(f"   contact f{r['contact_frame']} -> turnaround "
              f"f{r['turnaround_frame']} ({r['impact_pulse_ms']:.1f} ms pulse), "
              f"catch f{r['catch_frame']}")
        print(f"   scale {r['scale_px_per_m']:.0f} px/m (free-fall anchor) | "
              f"grid {grid['px_per_mm_at_grid']*1000:.0f} px/m over "
              f"{grid['n_strips']} strips (period {grid['period_px']:.1f} px, "
              f"IQR {grid['period_iqr_px']:.1f}) -> specimen/grid "
              f"{grid['specimen_over_grid_scale']:.3f}")
        print(f"   e* {r['coeff_restitution_scalefree']:.2f}, snapback "
              f"{r['snapback_ratio']:.2f}, brake "
              f"{r['brake_decel_g'] and round(r['brake_decel_g'], 2)} g, catch "
              f"+{r['catch_delay_ms'] and round(r['catch_delay_ms'])} ms / "
              f"{r['catch_rise_mm'] and round(r['catch_rise_mm'])} mm rise")
        print(f"   compression: {r['specimen_compression']}")

    # ---- figure 08: velocity traces + impact zoom for both drops
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.5))
    for col, (drop, r) in enumerate(results.items()):
        t = (r["series"]["f"] - r["turnaround_frame"]) / CAPTURE_FPS * 1000
        vel_ms = r["series"]["vel"] * CAPTURE_FPS / r["scale_px_per_m"]
        ax = axes[0][col]
        ax.plot(t, vel_ms, ".", ms=2.5, color=colors[drop])
        ax.axvline(0, color="k", ls=":", lw=0.8)
        ax.axhline(0, color="grey", lw=0.5)
        if r["catch_frame"]:
            tc = (r["catch_frame"] - r["turnaround_frame"]) / CAPTURE_FPS * 1e3
            ax.axvline(tc, color="grey", ls="--", lw=0.7)
            ax.annotate("brake catch", (tc, 0.6), fontsize=8, rotation=90)
        ax.set_title(f"prc1kn {drop} — pulse {r['impact_pulse_ms']:.1f} ms, "
                     f"e* {r['coeff_restitution_scalefree']:.2f}, "
                     f"brake {r['brake_decel_g']:.1f} g")
        ax.set_ylabel("velocity (m/s, down +)")
        ax.grid(alpha=0.3)

        ax2 = axes[1][col]
        w = (t > -40) & (t < 60)
        ax2.plot(t[w], r["series"]["vel"][w], ".-", ms=3.5, lw=0.7,
                 color=colors[drop])
        ax2.axvline(0, color="k", ls=":", lw=0.8)
        ax2.axhline(0, color="grey", lw=0.5)
        daq_w = ""
        if daq:
            pc = [c for c in daq["per_capture"] if c.get("real_impact")]
            daq_w = (f" (DAQ pulse "
                     f"{np.mean([c['top_width_ms'] for c in pc]):.1f} ms)")
        ax2.set_title(f"impact zoom — decel bracket "
                      f"{r['impact_pulse_ms']:.1f} ms{daq_w}")
        ax2.set_xlabel("real time from turnaround (ms)  [unique frame / 959.04]")
        ax2.set_ylabel("velocity (px/frame, down +)")
        ax2.grid(alpha=0.3)
    fig.suptitle("prc1kn 60 in slow-mo — correlation tracking "
                 "(Sony RX100M4, 959.04 fps from XML; duplicates removed)")
    fig.tight_layout()
    fig.savefig(OUTDIR / "08_video_kinematics.png", dpi=150)
    plt.close(fig)

    # ---- figure 09: grid scale vs free-fall-anchored specimen scale
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    drops = list(results)
    gs = [results[d]["grid"]["px_per_mm_at_grid"] * 1000 for d in drops]
    ss = [results[d]["scale_px_per_m"] for d in drops]
    xs = np.arange(len(drops))
    ax.bar(xs - 0.18, gs, 0.36, label="grid plane (checkerboard, 20 mm sq)",
           color="#999999")
    ax.bar(xs + 0.18, ss, 0.36, label="specimen plane (free-fall anchor)",
           color="#0072B2")
    for i, d in enumerate(drops):
        err = results[d]["grid"]["speed_error_if_grid_used_directly_pct"]
        ax.annotate(f"grid-only error: {err:+.1f} %",
                    (i, max(gs[i], ss[i]) * 1.02), ha="center", fontsize=9)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{d}\n({VIDEOS[d]})" for d in drops], fontsize=9)
    ax.set_ylabel("scale (px per metre)")
    ax.set_title("Calibration-grid parallax: the grid sits behind the drop "
                 "axis,\nso its scale under-reads specimen motion by the "
                 "depth ratio")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(OUTDIR / "09_grid_parallax.png", dpi=150)
    plt.close(fig)

    # ---- figure 10: montage per drop
    for drop, r in results.items():
        keep = r["keep"]
        marks = [("entry", r["descent_window"][0]),
                 ("-15 ms", r["turnaround_frame"] - 14),
                 ("contact", r["contact_frame"]),
                 ("turnaround", r["turnaround_frame"]),
                 ("+15 ms", r["turnaround_frame"] + 14),
                 ("brake catch", r["catch_frame"] or r["turnaround_frame"] + 100),
                 ("hold", min(len(keep) - 1, (r["catch_frame"] or 0) + 200))]
        marks = [(lab, int(np.clip(i, 0, len(keep) - 1))) for lab, i in marks]
        got = base.grab_frames(VIDDIR / VIDEOS[drop],
                               [int(keep[i]) for _, i in marks])
        fig, axes = plt.subplots(1, len(marks), figsize=(2.2 * len(marks), 7))
        for ax, (lab, ci) in zip(axes, marks):
            ax.imshow(got[int(keep[ci])])
            tms = (ci - r["turnaround_frame"]) / CAPTURE_FPS * 1000
            ax.set_title(f"{lab}\n{tms:+.1f} ms", fontsize=9)
            ax.axis("off")
        fig.suptitle(f"prc1kn {drop} — impact sequence "
                     f"(real ms from turnaround, unique frame / 959.04 fps)")
        fig.tight_layout()
        fig.savefig(OUTDIR / f"10_video_montage_{drop}.png", dpi=110)
        plt.close(fig)

    # ---- figure 11: three-specimen video comparison
    if prior:
        specs = ["7xadt6", "9GMQYQ"]
        rows = {s: prior["specimens"][s] for s in specs}
        rows["prc1kn (d1)"] = results["drop1"]
        rows["prc1kn (d2)"] = results["drop2"]
        keys = [("snapback_ratio", "top-vertex snap-back / impact speed"),
                ("coeff_restitution_scalefree",
                 "sustained rebound / impact speed (e*)"),
                ("impact_pulse_ms", "deceleration bracket (ms)")]
        fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2))
        cmap = {"7xadt6": "#0072B2", "9GMQYQ": "#D55E00",
                "prc1kn (d1)": "#009E73", "prc1kn (d2)": "#009E73"}
        for ax, (k, lab) in zip(axes, keys):
            names = list(rows)
            vals = [rows[n][k] for n in names]
            ax.bar(names, vals, color=[cmap[n] for n in names])
            ax.set_title(lab, fontsize=10)
            ax.tick_params(axis="x", labelsize=8, rotation=15)
            ax.grid(alpha=0.3, axis="y")
        fig.suptitle("Video kinematics across the three structures "
                     "(one drop each for 7xadt6/9GMQYQ, two for prc1kn)")
        fig.tight_layout()
        fig.savefig(OUTDIR / "11_three_specimen_video.png", dpi=150)
        plt.close(fig)

    # ---------------------------------------------------------------- metrics
    out = {"capture_fps": CAPTURE_FPS,
           "capture_fps_source": "Sony XML sidecar (captureFps=959.04p, "
                                 "formatFps=23.98p, DSC-RX100M4)",
           "drop_height_m": base.DROP_HEIGHT_M,
           "grid_square_mm": GRID_SQUARE_MM,
           "free_fall_reference": {"tau_s": base.FREE_FALL_S,
                                   "v_ms": base.FREE_FALL_V},
           "drops": {}}
    for drop, r in results.items():
        rr = {k: val for k, val in r.items() if k not in ("series", "keep")}
        if daq:
            pc = [c for c in daq["per_capture"] if c.get("real_impact")]
            rr["daq_reference"] = {
                "n_captures": len(pc),
                "mean_ch5_dv_ms": float(np.mean([c["ch5_dv_ms"] for c in pc])),
                "mean_top_width_ms": float(np.mean([c["top_width_ms"]
                                                    for c in pc])),
            }
        out["drops"][drop] = rr
    (OUTDIR / "video_metrics.json").write_text(json.dumps(out, indent=2))
    print(f"\nwrote {OUTDIR/'video_metrics.json'} + 4 figures")


if __name__ == "__main__":
    main()
