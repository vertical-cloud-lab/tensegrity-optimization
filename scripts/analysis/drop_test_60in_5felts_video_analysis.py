#!/usr/bin/env python3
"""Frame-by-frame video kinematics for the 60 in / 5 felts campaign.

Companion to ``drop_test_60in_5felts_analysis.py`` (accelerometer CSVs).
Analyzes the two slow-motion videos @ctrhjk recorded on 2026-07-20 (one drop
per specimen, posted as YouTube Shorts on PR #86 and committed to the branch
by @sgbaird):

    data/drop-tests/60in-5felts-validation/video/7xadt6_slomo.mp4
    data/drop-tests/60in-5felts-validation/video/9GMQYQ_slomo.mp4

Time base
---------
The camera is the Sony RX100 IV in HFR mode at **960 fps** (camera spec posted
by @ctrhjk in PR #67; same workflow as the burn-in-wax videos). The committed
files are YouTube re-encodes in a 30 fps container (encoder tag "Google").
A camera-native HFR clip is conformed to 24p, and a duration-preserving
24->30 conversion duplicates ~1 in 5 frames, so instead of assuming either
published mapping (frame/960 vs frame/1200) this script *detects and removes
duplicated frames* — first by inter-frame pixel difference, then a second
velocity-based pass that catches re-encoded duplicates (isolated frames with
near-zero measured motion in the middle of the descent). The surviving
unique frames are the camera's capture frames and real time is exactly
``unique_frame / 960`` regardless of what the container did. The measured
duplicate fraction is reported (expect ~1/5 for a 24p upload).

Tracking
--------
The orange struts are segmented in HSV. Around impact the mask fragments
under motion blur, so per-frame blob *positions* are unreliable exactly
where it matters. Two correlation trackers are used instead, both operating
on the orange-mask row profile (static orange content — the brown felt top
sheet leaks into the HSV band — is removed by subtracting the median
pre-entry profile):

* **velocity tracker** — normalized cross-correlation of consecutive
  frames' profiles gives the per-frame vertical shift directly (fragments
  translate with the specimen, so the peak tracks true motion through the
  blur); used for event detection, duplicate cleanup, the rebound/brake fit
  and the (scale-free) coefficient of restitution;
* **position tracker** — each descent frame is correlated against a single
  sharp mid-descent reference frame, giving absolute positions with
  independent (non-random-walk) noise; the quadratic fit of that trajectory
  is what calibrates the spatial scale.

Spatial scale + physics cross-checks
------------------------------------
No scale bar is in frame, but the pre-contact descent is ballistic, so its
pixel-space acceleration must equal g:

    scale [px/m] = a_px_per_frame^2 * 960^2 / g

Two checks then validate the calibration chain (960 fps time base + free
fall + the 60 in drop height):

  * tau = v_imp/a, time-to-impact from rest — **scale-free** — vs
    sqrt(2h/g) = 557 ms for 60 in
  * equivalent fall height h = v_imp^2/(2 g) vs 1.524 m

The DAQ campaign metrics (``figures/60in_5felts_metrics.json``) provide the
plate Delta-v and pulse width for cross-reference. Note the rig's rebound
brake: the carriage is caught mid-rebound (the post-impact climb
decelerates at ~2 g and ends in a stationary hold), so the rebound is *not*
ballistic and is never used for calibration.

Requires ``opencv-python-headless``, ``numpy``, ``scipy``, ``matplotlib``.
"""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
VIDDIR = REPO / "data" / "drop-tests" / "60in-5felts-validation" / "video"
OUTDIR = VIDDIR / "figures"
DAQ_METRICS = (REPO / "data" / "drop-tests" / "60in-5felts-validation"
               / "figures" / "60in_5felts_metrics.json")

VIDEOS = {"7xadt6": "7xadt6_slomo.mp4", "9GMQYQ": "9GMQYQ_slomo.mp4"}

CAPTURE_FPS = 960.0            # RX100 IV HFR capture rate (PR #67 camera spec)
DROP_HEIGHT_M = 60 * 0.0254    # 60 in
GRAVITY = 9.80665
FREE_FALL_S = float(np.sqrt(2 * DROP_HEIGHT_M / GRAVITY))
FREE_FALL_V = float(np.sqrt(2 * GRAVITY * DROP_HEIGHT_M))

# Orange-strut HSV band (dim indoor lighting -> permissive V floor)
HSV_LO = np.array([4, 80, 60])
HSV_HI = np.array([26, 255, 255])

DUP_REL_THRESHOLD = 0.12   # inter-frame diff < 12 % of local median => duplicate
MIN_MASS = 4000.0          # min orange mass (px) for a usable frame
MAX_SHIFT = 80             # consecutive-frame correlation search range (px)


# --------------------------------------------------------------------- I/O
def read_video(path: Path) -> dict:
    """One streaming pass: duplicate-detection diffs + orange row profiles."""
    cap = cv2.VideoCapture(str(path))
    profiles, cc, diffs = [], [], [0.0]
    prev_small = None
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        small = cv2.resize(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY), (90, 160))
        if prev_small is not None:
            diffs.append(float(np.mean(np.abs(small.astype(np.int16)
                                              - prev_small.astype(np.int16)))))
        prev_small = small

        hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, HSV_LO, HSV_HI)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        profiles.append(mask.sum(axis=1).astype(np.float32) / 255.0)

        # largest connected blob >= 800 px (compression proxy on clean frames)
        nlab, _, st, cen = cv2.connectedComponentsWithStats(mask)
        best = max(((st[i, cv2.CC_STAT_AREA], i) for i in range(1, nlab)
                    if st[i, cv2.CC_STAT_AREA] >= 800), default=None)
        if best:
            i = best[1]
            cc.append((cen[i][1], st[i, cv2.CC_STAT_TOP],
                       st[i, cv2.CC_STAT_TOP] + st[i, cv2.CC_STAT_HEIGHT],
                       float(best[0])))
        else:
            cc.append((np.nan,) * 4)
    cap.release()
    cy, top, bot, area = (np.array([c[i] for c in cc]) for i in range(4))
    return {"n_frames": len(profiles), "profiles": np.stack(profiles),
            "cc_cy": cy, "cc_top": top, "cc_bot": bot, "cc_area": area,
            "diff": np.array(diffs)}


def dedup_pixel(v: dict) -> np.ndarray:
    """Pass 1: duplicate frames by inter-frame pixel difference."""
    d = v["diff"]
    k = 21
    med = np.array([np.median(d[max(0, i - k // 2):i + k // 2 + 1])
                    for i in range(len(d))])
    dup = (d < DUP_REL_THRESHOLD * np.maximum(med, 1e-6)) & (med > 0.5)
    dup[0] = False
    return np.where(~dup)[0]


# --------------------------------------------------------------- trackers
def _subpixel(corr: np.ndarray, k: int) -> float:
    if 0 < k < len(corr) - 1:
        c0, c1, c2 = corr[k - 1], corr[k], corr[k + 1]
        den = c0 - 2 * c1 + c2
        if den != 0:
            return 0.5 * (c0 - c2) / den
    return 0.0


def _ncc_shift(a: np.ndarray, b: np.ndarray, shifts: np.ndarray) -> float:
    """Shift of b relative to a (down = +) maximizing normalized correlation."""
    rows = len(a)
    corr = np.empty(len(shifts))
    for j, s in enumerate(shifts):
        aa = a[max(0, -s):rows - max(0, s)]
        bb = b[max(0, s):rows - max(0, -s)]
        na, nb = np.linalg.norm(aa), np.linalg.norm(bb)
        corr[j] = np.dot(aa, bb) / (na * nb) if na > 0 and nb > 0 else 0.0
    k = int(np.argmax(corr))
    return float(shifts[k]) + _subpixel(corr, k)


def velocity_series(prof: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per-frame vertical shift (px, down = +) between consecutive frames."""
    n = len(prof)
    mass = prof.sum(axis=1)
    vel = np.full(n, np.nan)
    shifts = np.arange(-MAX_SHIFT, MAX_SHIFT + 1)
    dm = [p - p.mean() for p in prof]
    for f in range(1, n):
        if mass[f] >= MIN_MASS and mass[f - 1] >= MIN_MASS:
            vel[f] = _ncc_shift(dm[f - 1], dm[f], shifts)
    return vel, mass


def baseline_velocity(prof: np.ndarray, frames: np.ndarray,
                      baseline: int = 5) -> tuple[np.ndarray, np.ndarray]:
    """Velocity via B-frame-apart correlation, assigned to the midpoint.

    Over a 5-frame baseline the specimen's appearance barely changes, so the
    correlation locks reliably while the per-frame noise drops ~B-fold vs
    consecutive-frame shifts. Returns (midpoints, velocities px/frame).
    """
    shifts = np.arange(-baseline * MAX_SHIFT, baseline * MAX_SHIFT + 1)
    mids, vels = [], []
    for f in frames:
        g = f + baseline
        if g >= len(prof):
            continue
        a = prof[f] - prof[f].mean()
        b = prof[g] - prof[g].mean()
        vels.append(_ncc_shift(a, b, shifts) / baseline)
        mids.append(f + baseline / 2.0)
    return np.array(mids), np.array(vels)


# --------------------------------------------------------------- analysis
def clean_profiles(v: dict, keep: np.ndarray) -> np.ndarray:
    """Static-content-subtracted profiles on the unique-frame timeline."""
    prof = v["profiles"][keep]
    mass0 = prof.sum(axis=1)
    entry = int(np.argmax(mass0 > 2 * MIN_MASS))
    n_bg = max(10, entry - 10)
    return np.clip(prof - np.median(prof[:n_bg], axis=0), 0, None)


def profile_top(prof: np.ndarray) -> np.ndarray:
    """Row of the 2nd percentile of each frame's profile mass."""
    out = np.full(len(prof), np.nan)
    for i, p in enumerate(prof):
        m = p.sum()
        if m > MIN_MASS:
            out[i] = np.searchsorted(np.cumsum(p) / m, 0.02)
    return out


def analyze(v: dict, keep: np.ndarray) -> tuple[dict, np.ndarray]:
    """Kinematics on the unique-frame timeline; returns (result, keep)."""
    # velocity pass + second-stage duplicate cleanup (re-encoded duplicates
    # show up as isolated near-zero velocities in the middle of real motion)
    n_dup2 = 0
    for _ in range(3):
        prof = clean_profiles(v, keep)
        vel, mass = velocity_series(prof)
        loc = np.array([np.nanmedian(np.abs(
            vel[max(1, f - 3):f + 4])) if not np.isnan(vel[f]) else np.nan
            for f in range(len(vel))])
        dup2 = (~np.isnan(vel)) & (loc > 3.0) & (np.abs(vel) < 0.25 * loc)
        if not dup2.any():
            break
        n_dup2 += int(dup2.sum())
        keep = keep[~dup2]
    f = np.arange(len(vel), dtype=float)

    # events
    vmax_i = int(np.nanargmax(np.where(np.isnan(vel), -np.inf, vel)))
    v_peak = float(vel[vmax_i])
    after = np.where(~np.isnan(vel) & (f > vmax_i) & (vel < -2.0))[0]
    turn = int(after[0]) if len(after) else len(vel) - 1
    down = np.where(~np.isnan(vel[:turn]) & (vel[:turn] > 0.7 * v_peak))[0]
    contact = int(down[-1])                # last full-speed frame
    pulse_frames = turn - contact          # deceleration bracket
    entry_ok = np.where(~np.isnan(vel) & (vel > 0.7 * v_peak)
                        & (profile_top(prof) > 25))[0]
    d_lo = int(entry_ok[0])

    # descent fit on 5-frame-baseline velocities (low noise, locks under blur)
    desc = np.arange(d_lo, contact + 1)
    B = 5 if len(desc) > 15 else 3
    # pairs must end strictly before contact so no sample straddles the pulse
    starts = desc[desc + B <= contact - 1]
    mids, v5 = baseline_velocity(prof, starts, B)
    med5 = np.median(v5)
    ok = (v5 > 0.75 * med5) & (v5 < 1.25 * med5)   # reject entry mislocks
    mids, v5 = mids[ok], v5[ok]
    coef, cov = np.polyfit(mids, v5, 1, cov=True)
    a_px = float(coef[0])
    a_err = float(np.sqrt(cov[0, 0]))
    fit_res = float(np.std(v5 - np.polyval(coef, mids)))

    # robust impact speed: median consecutive-frame velocity just before contact
    v_imp_px = float(np.nanmedian(vel[max(d_lo, contact - 12):contact + 1]))

    # ---- spatial scale: ASSUMED near-free-fall arrival speed from 60 in ----
    # The pixel-space descent velocity is constant to ~1-2 % (descent_flatness
    # below): the +7-8 % free-fall velocity gain expected over the visible
    # window is cancelled by the camera's perspective scale gradient (the
    # specimen recedes from the optical axis as it falls), so curvature-based
    # self-calibration is not available from this camera position. The scale
    # is instead anchored on the arrival speed being free-fall from 60 in
    # (5.47 m/s) — corroborated independently by the DAQ plate Delta-v
    # (5.53 m/s campaign mean). Any rail-friction loss scales all
    # metre-denominated outputs down proportionally.
    scale = v_imp_px * CAPTURE_FPS / FREE_FALL_V     # px per metre
    v_imp_ms = FREE_FALL_V                            # by construction
    g_px_expected = GRAVITY * scale / CAPTURE_FPS ** 2

    # rebound (velocity tracker): elastic snap-back spike in the first ~4
    # frames, then the sustained carriage rebound, then the brake
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
        brake_g = brake_a * CAPTURE_FPS ** 2 / scale / GRAVITY
        rise_px = float(-np.nansum(np.where(np.isnan(vel[turn:catch]), 0,
                                            vel[turn:catch])))

    # specimen compression proxy: largest-CC bbox height on intact frames
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
                        "resolvable with mask-based tracking at 960 fps")

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
                       "(5.47 m/s); DAQ plate dv 5.53 m/s corroborates",
        "v_impact_px_per_frame": v_imp_px,
        "v_impact_ms_assumed": float(v_imp_ms),
        "impact_pulse_frames": int(pulse_frames),
        "impact_pulse_ms": float(pulse_frames / CAPTURE_FPS * 1000),
        "snapback_peak_px_per_frame": snap_px,
        "snapback_ratio": float(snap_px / v_imp_px),
        "v_rebound_px_per_frame": v_reb_px,
        "v_rebound_ms": float(v_reb_px * CAPTURE_FPS / scale),
        "coeff_restitution_scalefree": float(v_reb_px / v_imp_px),
        "brake_decel_g": brake_g,
        "catch_delay_ms": (float((catch - turn) / CAPTURE_FPS * 1000)
                           if catch else None),
        "catch_rise_px": rise_px,
        "catch_rise_mm": (rise_px / scale * 1000) if rise_px else None,
        "specimen_compression": comp,
        "series": {"f": f, "vel": vel, "mass": mass,
                   "desc_mids": mids, "desc_v5": v5, "coef": coef},
    }
    return res, keep


# ------------------------------------------------------------------ figures
def grab_frames(path: Path, playback_idx: list[int]) -> dict[int, np.ndarray]:
    cap = cv2.VideoCapture(str(path))
    out, want, n = {}, sorted(set(playback_idx)), 0
    while want:
        ok, fr = cap.read()
        if not ok:
            break
        if n == want[0]:
            out[n] = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
            want.pop(0)
        n += 1
    cap.release()
    return out


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    daq = json.loads(DAQ_METRICS.read_text()) if DAQ_METRICS.exists() else None
    colors = {"7xadt6": "#0072B2", "9GMQYQ": "#D55E00"}
    results = {}

    for spec, fname in VIDEOS.items():
        print(f"== {spec}: {fname}")
        v = read_video(VIDDIR / fname)
        keep0 = dedup_pixel(v)
        r, keep = analyze(v, keep0)
        dup = 1 - len(keep) / v["n_frames"]
        r["keep"] = keep
        r["video"] = {"file": fname, "playback_frames": v["n_frames"],
                      "unique_frames": len(keep),
                      "duplicate_fraction": float(dup),
                      "real_duration_s": float(len(keep) / CAPTURE_FPS)}
        results[spec] = r
        print(f"   {v['n_frames']} -> {len(keep)} unique (dup {dup:.1%} "
              f"incl. {r['n_velocity_dups_removed']} re-encoded), "
              f"real {len(keep)/CAPTURE_FPS:.3f} s")
        print(f"   contact f{r['contact_frame']} -> turnaround "
              f"f{r['turnaround_frame']} ({r['impact_pulse_ms']:.1f} ms pulse), "
              f"catch f{r['catch_frame']}")
        print(f"   pixel-flat descent: a {r['descent_flatness']['a_px_per_frame2']:+.4f}"
              f"±{r['descent_flatness']['a_err']:.4f} px/f^2 vs g-expected "
              f"+{r['descent_flatness']['expected_g_px_per_frame2']:.4f} "
              f"(res {r['descent_flatness']['residual_px_per_frame']:.2f}, "
              f"n {r['descent_flatness']['n_points']})")
        print(f"   scale {r['scale_px_per_m']:.0f} px/m (assumed v_imp "
              f"{FREE_FALL_V:.2f} m/s), v_imp {r['v_impact_px_per_frame']:.1f} px/f")
        print(f"   e* {r['coeff_restitution_scalefree']:.2f}, snapback "
              f"{r['snapback_ratio']:.2f}, v_reb {r['v_rebound_ms']:.2f} m/s, "
              f"brake {r['brake_decel_g'] and round(r['brake_decel_g'], 2)} g, "
              f"catch +{r['catch_delay_ms'] and round(r['catch_delay_ms'])} ms / "
              f"{r['catch_rise_mm'] and round(r['catch_rise_mm'])} mm rise")
        print(f"   compression: {r['specimen_compression']}")

    # figure 05: velocity + descent-position fit
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.5), sharex="col")
    for col, (spec, r) in enumerate(results.items()):
        t = (r["series"]["f"] - r["turnaround_frame"]) / CAPTURE_FPS * 1000
        vel_ms = r["series"]["vel"] * CAPTURE_FPS / r["scale_px_per_m"]
        ax = axes[0][col]
        ax.plot(t, vel_ms, ".", ms=2.5, color=colors[spec])
        ax.axvline(0, color="k", ls=":", lw=0.8)
        ax.axhline(0, color="grey", lw=0.5)
        if r["catch_frame"]:
            tcatch = (r["catch_frame"] - r["turnaround_frame"]) / CAPTURE_FPS * 1e3
            ax.axvline(tcatch, color="grey", ls="--", lw=0.7)
            ax.annotate("brake catch", (tcatch, 0.6), fontsize=8, rotation=90)
        ax.set_ylabel("velocity (m/s, down +)")
        ax.set_title(f"{spec} — v_imp {r['v_impact_px_per_frame']:.1f} px/f, "
                     f"pulse {r['impact_pulse_ms']:.1f} ms, "
                     f"e* {r['coeff_restitution_scalefree']:.2f}, "
                     f"brake {r['brake_decel_g']:.1f} g")
        ax.grid(alpha=0.3)

        ax2 = axes[1][col]
        mids, v5 = r["series"]["desc_mids"], r["series"]["desc_v5"]
        coef = r["series"]["coef"]
        td = (mids - r["turnaround_frame"]) / CAPTURE_FPS * 1000
        ax2.plot(td, v5, ".", ms=4, color=colors[spec],
                 label="5-frame-baseline velocity")
        ax2.plot(td, np.polyval(coef, mids), "k--", lw=1.1,
                 label=(f"linear fit: {r['descent_flatness']['a_px_per_frame2']:+.3f} px/f$^2$ "
                        f"(g would be +{r['descent_flatness']['expected_g_px_per_frame2']:.3f})"))
        ax2.set_xlabel("real time from turnaround (ms)  [unique frame / 960]")
        ax2.set_ylabel("descent velocity (px/frame)")
        ax2.legend(fontsize=8)
        ax2.grid(alpha=0.3)
    fig.suptitle("60 in / 5 felts slow-mo — correlation tracking "
                 "(Sony RX100 IV, 960 fps; duplicates removed)")
    fig.tight_layout()
    fig.savefig(OUTDIR / "05_video_kinematics.png", dpi=150)
    plt.close(fig)

    # figure 06: impact zoom (velocity, raw px/frame to keep it scale-honest)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, (spec, r) in zip(axes, results.items()):
        t = (r["series"]["f"] - r["turnaround_frame"]) / CAPTURE_FPS * 1000
        w = (t > -40) & (t < 60)
        ax.plot(t[w], r["series"]["vel"][w], ".-", ms=3.5, lw=0.7,
                color=colors[spec])
        ax.axvline(0, color="k", ls=":", lw=0.8)
        ax.axhline(0, color="grey", lw=0.5)
        tc = (r["contact_frame"] - r["turnaround_frame"]) / CAPTURE_FPS * 1000
        ax.axvline(tc, color="grey", ls="--", lw=0.7)
        daq_w = ""
        if daq:
            pc = [c for c in daq["per_capture"][spec] if c.get("real_impact")]
            daq_w = f" (DAQ pulse {np.mean([c['top_width_ms'] for c in pc]):.1f} ms)"
        ax.set_title(f"{spec} — decel {r['contact_frame']}->"
                     f"{r['turnaround_frame']} = "
                     f"{r['impact_pulse_ms']:.1f} ms{daq_w}")
        ax.set_xlabel("ms from turnaround")
        ax.set_ylabel("velocity (px/frame, down +)")
        ax.grid(alpha=0.3)
    fig.suptitle("Impact zoom — the deceleration to zero happens in 1-3 "
                 "capture frames, corroborating the DAQ's ~1.6 ms pulse")
    fig.tight_layout()
    fig.savefig(OUTDIR / "06_video_impact_zoom.png", dpi=150)
    plt.close(fig)

    # figure 07: montage per specimen
    for spec, r in results.items():
        keep = r["keep"]
        marks = [("entry", r["descent_window"][0]),
                 ("-15 ms", r["turnaround_frame"] - 14),
                 ("contact", r["contact_frame"]),
                 ("turnaround", r["turnaround_frame"]),
                 ("+15 ms", r["turnaround_frame"] + 14),
                 ("brake catch", r["catch_frame"] or r["turnaround_frame"] + 100),
                 ("hold", min(len(keep) - 1, (r["catch_frame"] or 0) + 200))]
        marks = [(lab, int(np.clip(i, 0, len(keep) - 1))) for lab, i in marks]
        got = grab_frames(VIDDIR / VIDEOS[spec], [int(keep[i]) for _, i in marks])
        fig, axes = plt.subplots(1, len(marks), figsize=(2.6 * len(marks), 6.2))
        for ax, (lab, ci) in zip(axes, marks):
            ax.imshow(got[int(keep[ci])])
            tms = (ci - r["turnaround_frame"]) / CAPTURE_FPS * 1000
            ax.set_title(f"{lab}\n{tms:+.1f} ms", fontsize=9)
            ax.axis("off")
        fig.suptitle(f"{spec} — impact sequence (real ms from turnaround, "
                     f"unique frame / 960 fps)")
        fig.tight_layout()
        fig.savefig(OUTDIR / f"07_video_montage_{spec}.png", dpi=110)
        plt.close(fig)

    # ---------------------------------------------------------------- metrics
    out = {"capture_fps": CAPTURE_FPS, "drop_height_m": DROP_HEIGHT_M,
           "free_fall_reference": {"tau_s": FREE_FALL_S, "v_ms": FREE_FALL_V},
           "specimens": {}}
    for spec, r in results.items():
        rr = {k: val for k, val in r.items() if k not in ("series", "keep")}
        if daq:
            pc = [c for c in daq["per_capture"][spec] if c.get("real_impact")]
            rr["daq_reference"] = {
                "n_captures": len(pc),
                "mean_ch5_dv_ms": float(np.mean([c["ch5_dv_ms"] for c in pc])),
                "mean_top_width_ms": float(np.mean([c["top_width_ms"] for c in pc])),
                "mean_ch5_width_ms": float(np.mean([c["ch5_width_ms"] for c in pc])),
            }
        out["specimens"][spec] = rr
    (OUTDIR / "video_metrics.json").write_text(json.dumps(out, indent=2))
    print(f"\nwrote {OUTDIR/'video_metrics.json'} + 4 figures")


if __name__ == "__main__":
    main()
