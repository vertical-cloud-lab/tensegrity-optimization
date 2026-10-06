"""Side-by-side videos for issue #114, corny1 to corny6 (and corny7 as the reference):
Justin's work-vs-time graph on the left with a red time cursor, the slow-motion drop
video on the right, in sync. Under the work graph, the specimen's change in height
measured from the video is plotted against the change in height his work integral
uses (CH4 minus CH5, integrated twice).

Each session filmed drops 1, 10 and 20. The clip named "10th" is used for every
specimen; by the camera clock it caught drop 10 for corny1 to corny5 and drop 11
for corny6 and corny7 (see README.md).

How the two clocks are matched (same method as ../drop11-video for corny7): the
carriage is tracked frame by frame in the video (template match on its green
label). Its path is a straight line before impact and a slow rebound after, and
the two lines cross at the centroid of the impact pulse. The same centroid is
computed from the base-plate accelerometer (CH5). Pinning one to the other gives
the time of every video frame on the accelerometer clock.

How the height change is measured: in every frame, the specimen's highest point
(the left-most white pixels in the camera frame: the top nodes, where the CH4
sensor sits) is found by thresholding. Its distance to the tracked label, relative
to the median while the carriage is in the air on its bounce (50 to 95 ms, when
the specimen is unloaded), is the change in specimen height. The pixel scale comes
from the carriage's speed change at impact matched to CH5's, as in the corny7
video. A template track of the top nodes is kept as a cross-check; it agrees on
corny1 to corny5 but loses the twisting tops of corny6 and corny7.

Usage (from any directory):
    python make_work_videos.py                    # all seven, downloads on first use
    python make_work_videos.py corny1 corny4      # just these

Needs numpy, scipy, matplotlib, opencv-python-headless, imageio-ffmpeg.
"""
import argparse
import json
import subprocess
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

import cv2
import imageio_ffmpeg
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as mpl  # noqa: E402
import numpy as np  # noqa: E402
import scipy as sp  # noqa: E402

HERE = Path(__file__).resolve().parent
CACHE = HERE / "_cache"
# 50 kHz waveform CSVs for corny1 to corny9, committed on the issue #114 all-specimens
# branch (corny7's is byte-identical to the issue #110 export at commit 5cc4b1e)
CSV_URL = ("https://raw.githubusercontent.com/vertical-cloud-lab/tensegrity-optimization/"
           "1aff9ff/analysis/issue-114-work/all-specimens/waveforms/{spec}_waveforms_50kHz.csv")
# clips on the lab's public Box share (folder "9-14-2026 - corny_", manifest in
# data/drop-tests/corny-checkin/video/box-ids.json on PR #86)
BOX_URL = ("https://byu.app.box.com/index.php?rm=box_download_shared_file"
           "&shared_name=kkhmvnj9ni19b57dryk3gdroqrp5uf0b&file_id={fid}")

# drop: which drop the clip caught (camera clock, README.md). impact_guess: the
# frame where the frame-to-frame motion of the falling carriage stops, read off
# a scan of every frame; the exact sub-frame impact is fitted below.
SPECS = {
    "corny1": dict(clip="corny1-10th.MP4", sidecar="C0247M01", fid="f_2466877314391", drop=10, impact_guess=1078),
    "corny2": dict(clip="corny2-10th.MP4", sidecar="C0250M01", fid="f_2466876251923", drop=10, impact_guess=1098),
    "corny3": dict(clip="corny3-10th.MP4", sidecar="C0253M01", fid="f_2466878140477", drop=10, impact_guess=781),
    "corny4": dict(clip="corny4-10th.MP4", sidecar="C0256M01", fid="f_2466888848866", drop=10, impact_guess=1017),
    "corny5": dict(clip="corny5-10th.MP4", sidecar="C0259M01", fid="f_2466888068697", drop=10, impact_guess=1007),
    "corny6": dict(clip="corny6-10th.MP4", sidecar="C0262M01", fid="f_2466869751950", drop=11, impact_guess=864),
    "corny7": dict(clip="corny7-10th.MP4", sidecar="C0265M01", fid="f_2466875538664", drop=11, impact_guess=1017),
}

FPS_CAM = 959.04              # captureFps in every sidecar of this session
DT_FRAME_MS = 1000.0 / FPS_CAM
SLOWDOWN = 120                # 100 ms of drop plays over 12 s
OUT_FPS = 30
HOLD_S = 1.0                  # still frames at the start and end
T_END_MS = 99.98
OUT_W, OUT_H = 1920, 1080
VID_W = 820                   # width of the video panel after rotating
TEMPLATE_AFTER = 40           # template frames: this many frames after impact_guess
KEY_T = [0.0, 2.5, 4.0, 6.0, 10.0, 20.0, 41.0, 70.0]


# --- Justin's function, copied unchanged from implimatation_or_work.py as
# --- uploaded to issue #114 on 2026-10-06 (justin/implimatation_or_work_2026-10-06.py)
def numaric_work(t_vec, a_top_vec, a_bottom_vec, m=1, g=9.81, v0=-5.46):
    v_top_vec = sp.integrate.cumulative_trapezoid((a_top_vec), t_vec, initial = 0)
    v_bottom_vec = sp.integrate.cumulative_trapezoid((a_bottom_vec), t_vec, initial = 0)
    work_vec = [0]
    work_top_vec = [0]
    work_bottom_vec = [0]
    for i in range(len(t_vec)-1):
        dx_top = (t_vec[i+1] - t_vec[i])*( (1/2)*(v_top_vec[i+1]+v_top_vec[i]) + v0)
        dx_bottom = (t_vec[i+1] - t_vec[i])*( (1/2)*(v_bottom_vec[i+1]+v_bottom_vec[i]) + v0)

        work = work_vec[i] + m*(g + a_top_vec[i+1])*(dx_top - dx_bottom)
        work_vec.append(work)

        work_top = work_top_vec[i] + m*(g + a_top_vec[i+1])*(dx_top)
        work_top_vec.append(work_top)

        work_bottom = work_bottom_vec[i] + m*(g + a_top_vec[i+1])*(-dx_bottom)
        work_bottom_vec.append(work_bottom)

    return np.array(work_vec), np.array(work_top_vec), np.array(work_bottom_vec)
# --- end of Justin's function


def fetch(url: str, dest: Path) -> Path:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading {dest.name} ...")
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
        with opener.open(url, timeout=600) as r, open(dest.with_suffix(".part"), "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        dest.with_suffix(".part").rename(dest)
    return dest


def load_drop(csv: Path, drop: int):
    """Same columns and units as Justin's script: CH4 is the top, CH5 the base."""
    data = np.loadtxt(csv, delimiter=",", skiprows=1)
    d = data[data[:, 0] == drop]
    return d[:, 1], d[:, 4], d[:, 5]          # time (ms), ch4 (G), ch5 (G)


def pulse_centroid_ms(t_ms, ch5_g):
    """Centroid of the base-plate impact pulse (CH5, zeroed on its 70-100 ms median)."""
    a = ch5_g - np.median(ch5_g[t_ms >= 70])
    ipk = int(np.argmax(np.where(t_ms < 15, a, -np.inf)))
    end = ipk + int(np.argmax(a[ipk:] <= 0))   # first zero crossing after the peak
    w = slice(0, end)
    tc = float(np.sum(t_ms[w] * a[w]) / np.sum(a[w]))
    dv = float(np.trapezoid(a[w], t_ms[w]) * 9.81e-3)
    return tc, dv, float(t_ms[ipk])


def read_frame(cap, f):
    cap.set(cv2.CAP_PROP_POS_FRAMES, f)
    ok, fr = cap.read()
    if not ok:
        raise RuntimeError(f"could not read frame {f}")
    return fr


def find_boxes(still):
    """Template boxes (x0, x1, y0, y1) in a still taken after impact: a 140 x 270 px
    patch centred on the green label, and the specimen's top nodes (the left-most
    white parts between the left wall and the carriage). Camera on its side: right
    in the image is down in the lab."""
    hsv = cv2.cvtColor(still, cv2.COLOR_BGR2HSV)
    green = ((hsv[..., 0] >= 35) & (hsv[..., 0] < 65) & (hsv[..., 1] > 50) & (hsv[..., 2] > 90)).astype(np.uint8)
    green = cv2.morphologyEx(green, cv2.MORPH_OPEN, np.ones((11, 11), np.uint8))
    n, _, stats, cent = cv2.connectedComponentsWithStats(green)
    i = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    cx, cy = (int(round(c)) for c in cent[i])
    h_img, w_img = still.shape[:2]
    label = (max(0, cx - 70), min(w_img, cx + 70), max(0, cy - 135), min(h_img, cy + 135))
    white = ((hsv[..., 1] < 70) & (hsv[..., 2] > 150)).astype(np.uint8)
    white = cv2.morphologyEx(white, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    y0, y1 = max(0, cy - 400), min(h_img, cy + 250)
    x0 = 700
    cols = white[y0:y1, x0:cx - 220].sum(axis=0)
    xt = x0 + int(np.nonzero(cols >= 8)[0][0])
    rows = np.nonzero(white[y0:y1, xt:xt + 60].sum(axis=1) >= 2)[0]
    top = (xt - 20, xt + 70, y0 + int(rows[0]) - 15, y0 + int(rows[-1]) + 15)
    return label, top


def track(video: Path, box, f_tmpl: int, f0: int, f1: int, pad_y: int = 30):
    """Horizontal image position of the patch `box` (from frame f_tmpl) in frames
    f0..f1, in px relative to its position in f_tmpl, with a parabolic sub-pixel
    peak. Searches a horizontal strip pad_y px taller than the patch."""
    x0, x1, y0, y1 = box
    cap = cv2.VideoCapture(str(video))
    tmpl = cv2.cvtColor(read_frame(cap, f_tmpl), cv2.COLOR_BGR2GRAY)[y0:y1, x0:x1]
    cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
    frames, xs, scores = [], [], []
    for f in range(f0, f1 + 1):
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        ys0 = max(0, y0 - pad_y)
        strip = g[ys0:min(g.shape[0], y1 + pad_y), :]
        res = cv2.matchTemplate(strip, tmpl, cv2.TM_CCOEFF_NORMED)
        _, score, _, (xi, yi) = cv2.minMaxLoc(res)
        r = res[yi]
        dx = 0.0
        if 0 < xi < len(r) - 1:
            den = r[xi - 1] - 2 * r[xi] + r[xi + 1]
            dx = 0.5 * (r[xi - 1] - r[xi + 1]) / den if den else 0.0
        frames.append(f)
        xs.append(xi + dx - x0)
        scores.append(score)
    return np.array(frames), np.array(xs), np.array(scores)


def track_top_edge(video: Path, top_box, label_x_abs, frames, x_min: int = 700):
    """Image x of the specimen's highest point (in the lab) in each frame: the
    left-most column with 8 or more white pixels in a band around the top nodes,
    searching right of the left wall and short of the carriage. Unlike a template,
    this does not care that a twisting top changes how it looks."""
    _, _, y0, y1 = top_box
    y0, y1 = max(0, y0 - 45), y1 + 45
    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(frames[0]))
    xs = []
    for f, lx in zip(frames, label_x_abs):
        ok, fr = cap.read()
        hsv = cv2.cvtColor(fr[y0:y1, x_min:], cv2.COLOR_BGR2HSV)
        white = ((hsv[..., 1] < 70) & (hsv[..., 2] > 150)).astype(np.uint8)
        white = cv2.morphologyEx(white, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        cols = white.sum(axis=0)
        cols[max(0, int(lx) - x_min - 150):] = 0
        k = np.nonzero(cols >= 8)[0]
        xs.append(x_min + k[0] if len(k) else np.nan)
    return np.array(xs, float)


def impact_frame(frames, x):
    """Sub-frame time where the free-fall line and the rebound path cross."""
    step = np.diff(x)
    fall = np.median(step[:20])
    k = int(np.argmax(step < 0.3 * fall))       # first frame step well below free fall
    pre = (frames >= frames[k] - 11) & (frames <= frames[k] - 1)
    post = (frames >= frames[k] + 2) & (frames <= frames[k] + 14)
    p = np.polyfit(frames[pre], x[pre], 1)
    q = np.polyfit(frames[post], x[post], 2)
    roots = np.roots(np.polysub(q, p))
    roots = roots[np.isreal(roots)].real
    fc = float(roots[np.argmin(np.abs(roots - frames[k]))])
    return fc, p, q


def run(spec: str, out: Path):
    cfg = SPECS[spec]
    drop = cfg["drop"]
    csv = fetch(CSV_URL.format(spec=spec), CACHE / f"{spec}_waveforms_50kHz.csv")
    video = fetch(BOX_URL.format(fid=cfg["fid"]), CACHE / cfg["clip"])
    tag = f"{spec}_drop{drop}"

    # 1. Justin's work curves for this drop, exactly as his script makes them
    t_ms, ch4, ch5 = load_drop(csv, drop)
    time = t_ms * 1E-3
    work_z, work_z_top, work_z_bottom = numaric_work(time, ch4 * 9.81, ch5 * 9.81)
    i_pk = 1250 + int(np.argmax(work_z[1250:2250]))   # his "peak" window, 25-45 ms
    # the height change his work sum uses: sum of (dx_top - dx_bottom), v0 cancels
    v4 = sp.integrate.cumulative_trapezoid(ch4 * 9.81, time, initial=0)
    v5 = sp.integrate.cumulative_trapezoid(ch5 * 9.81, time, initial=0)
    dh_acc = sp.integrate.cumulative_trapezoid(v4 - v5, time, initial=0) * 1e3     # mm, + = taller

    # 2. track the carriage and the specimen top, match the clocks
    g0 = cfg["impact_guess"]
    cap = cv2.VideoCapture(str(video))
    f_tmpl = g0 + TEMPLATE_AFTER
    still = read_frame(cap, f_tmpl)
    label_box, top_box = find_boxes(still)
    f0, f1 = g0 - 30, g0 + 110
    frames, x_lab, s_lab = track(video, label_box, f_tmpl, f0, f1)
    _, x_top_tmpl, s_top = track(video, top_box, f_tmpl, f0, f1, pad_y=40)   # cross-check only
    x_top = track_top_edge(video, top_box, x_lab + label_box[0], frames)
    fc, p, q = impact_frame(frames, x_lab)
    tc_ms, dv, tpk_ms = pulse_centroid_ms(t_ms, ch5)
    t_of_frame = lambda f: tc_ms + (np.asarray(f) - fc) * DT_FRAME_MS   # noqa: E731
    slope_post = np.polyval(np.polyder(q), fc)
    px_per_mm = (p[0] - slope_post) / (dv * DT_FRAME_MS)
    v_impact = p[0] / px_per_mm / DT_FRAME_MS
    # specimen height change: label-to-top distance against its median while the
    # carriage is in the air on its bounce (50 to 95 ms), when the specimen is
    # unloaded and the frames are sharp. Frames before impact are motion-blurred
    # (about 20 px per ms of fall), which biases the match, so they are only shown.
    tv = t_of_frame(frames)
    gap = (x_lab + label_box[0]) - x_top
    ref = (tv >= 50) & (tv <= 95)
    dh_vid = (gap - np.nanmedian(gap[ref])) / px_per_mm                           # mm, + = taller
    gap_t = (x_lab + label_box[0]) - (x_top_tmpl + top_box[0])
    dh_tmpl = (gap_t - np.median(gap_t[ref])) / px_per_mm
    pre = (frames >= fc - 12) & (frames <= fc - 2)
    sharp = tv >= 2.0
    in_rec = (tv >= 0) & (tv <= 100)
    sync = {
        "specimen": spec, "drop": drop, "clip": f"{cfg['clip']} ({cfg['sidecar']})",
        "camera_fps": FPS_CAM,
        "impact_frame_subframe": round(fc, 3),
        "ch5_pulse_centroid_ms": round(tc_ms, 3), "ch5_peak_ms": round(tpk_ms, 3),
        "ch5_delta_v_pulse_m_s": round(dv, 3),
        "frame_at_record_start_t0": round(fc - tc_ms / DT_FRAME_MS, 2),
        "frame_at_record_end_t100ms": round(fc + (100 - tc_ms) / DT_FRAME_MS, 2),
        "carriage_px_per_mm": round(float(px_per_mm), 3),
        "carriage_impact_speed_from_video_m_s": round(float(v_impact), 3),
        "label_box_x0x1y0y1": [int(v) for v in label_box], "top_box_x0x1y0y1": [int(v) for v in top_box],
        "template_frame": f_tmpl,
        "label_match_score_min": round(float(s_lab[in_rec].min()), 3),
        "video_height_change_mm": {
            "min_after_2ms": round(float(np.nanmin(dh_vid[sharp & in_rec])), 2),
            "t_of_min_ms": round(float(tv[sharp & in_rec][np.nanargmin(dh_vid[sharp & in_rec])]), 1),
            "max_after_2ms": round(float(np.nanmax(dh_vid[sharp & in_rec])), 2),
            "frames_without_a_top_edge": int(np.isnan(dh_vid[in_rec]).sum()),
            "at_15ms": round(float(np.interp(15, tv, dh_vid)), 2),
            "at_41ms": round(float(np.interp(41, tv, dh_vid)), 2),
            "reference": "median over 50-95 ms (carriage in the air)",
            "sd_over_reference_window": round(float(np.std(dh_vid[ref])), 2),
            "median_in_free_fall_before_impact_blurred": round(float(np.nanmedian(dh_vid[pre])), 2),
            "template_track_at_15ms_cross_check": round(float(np.interp(15, tv, dh_tmpl)), 2),
            "template_track_at_41ms_cross_check": round(float(np.interp(41, tv, dh_tmpl)), 2),
            "template_track_min_match_score": round(float(s_top[in_rec].min()), 3)},
        "accel_height_change_mm": {
            "min": round(float(dh_acc.min()), 2), "t_of_min_ms": round(float(t_ms[np.argmin(dh_acc)]), 1),
            "at_15ms": round(float(np.interp(15, t_ms, dh_acc)), 2),
            "at_41ms": round(float(np.interp(41, t_ms, dh_acc)), 2),
            "at_100ms": round(float(dh_acc[-1]), 1)},
        "dv_15ms_m_s": {"ch4_top": round(float(np.interp(15, t_ms, v4)), 3),
                        "ch5_base": round(float(np.interp(15, t_ms, v5)), 3)},
        "peak_g": {"ch4_top": round(float(ch4.max()), 1), "ch5_base": round(float(ch5.max()), 1)},
        "work_J_per_kg": {"min": round(float(work_z.min()), 3),
                          "t_of_min_ms": round(float(t_ms[np.argmin(work_z)]), 2),
                          "at_15ms": round(float(np.interp(15, t_ms, work_z)), 3),
                          "justin_window_max_25_45ms": round(float(work_z[i_pk]), 3),
                          "t_of_window_max_ms": round(float(t_ms[i_pk]), 2)},
    }
    print(json.dumps(sync, indent=1))
    np.savetxt(out / f"{tag}_video_track.csv",
               np.column_stack([frames, tv, x_lab + label_box[0], x_top, s_lab, dh_vid, dh_tmpl, s_top]),
               delimiter=",", fmt=["%d", "%.3f", "%.3f", "%.1f", "%.4f", "%.3f", "%.3f", "%.4f"],
               header="frame,t_ms,label_x_px,top_edge_x_px,label_match,video_height_change_mm,"
                      "template_height_change_mm,template_match",
               comments="")

    # 3. check figure: the carriage in the video against CH5 integrated twice,
    # and the specimen's height change from the video against the accelerometers
    a5 = (ch5 - np.median(ch5[t_ms >= 70])) * 9.81 - 9.81
    v5c = sp.integrate.cumulative_trapezoid(a5, time, initial=0) - v_impact
    y5 = sp.integrate.cumulative_trapezoid(v5c, time, initial=0) * 1e3
    y_vid = -(x_lab - np.polyval(p, fc)) / px_per_mm
    fig, axs = mpl.subplots(1, 3, figsize=(15, 4.2), dpi=130, gridspec_kw={"width_ratios": [1, 1.4, 1.4]})
    ax = axs[0]
    ax.plot(tv, y_vid - np.interp(tc_ms, tv, y_vid), "o", ms=3.5, label="carriage in the video")
    ax.plot(t_ms, y5 - np.interp(tc_ms, t_ms, y5), lw=1.5, label="base plate from CH5, integrated twice")
    ax.axvline(tc_ms, color="0.5", lw=0.8, ls=":")
    ax.set_xlim(-5, 15)
    ax.set_ylim(-12, 12)
    ax.set_title("impact (sets the sync)", fontsize=10)
    ax.set_ylabel("carriage height relative to impact [mm]")
    ax.legend(loc="lower left", fontsize=7.5)
    for ax, (lo, hi) in zip(axs[1:], [(-5, 20), (-5, 100)]):
        ax.plot(tv[sharp], dh_vid[sharp], "o", ms=3.5, color="C2", label="specimen height change, video")
        ax.plot(tv[~sharp], dh_vid[~sharp], "o", ms=3.5, mfc="none", color="C2", label="video, blurred frames (falling)")
        ax.plot(t_ms, dh_acc, lw=1.5, color="C3", label="height change in the work sum (CH4 - CH5, integrated twice)")
        ax.axhline(0, color="0.3", lw=0.8)
        ax.set_xlim(lo, hi)
        ax.set_ylabel("change in specimen height [mm]")
    axs[1].set_ylim(-12, 12)
    axs[2].set_ylim(-15, max(40, float(dh_acc.max()) * 1.05))
    axs[1].set_title("first 20 ms", fontsize=10)
    axs[2].set_title("whole record", fontsize=10)
    axs[2].legend(loc="upper left", fontsize=7.5)
    for ax in axs:
        ax.set_xlabel("time on the accelerometer clock [ms]")
        ax.grid(alpha=0.4)
    fig.suptitle(f"{spec} drop {drop}: video frame {fc:.2f} = {tc_ms:.2f} ms on the accelerometer clock, "
                 f"{px_per_mm:.2f} px/mm")
    fig.tight_layout()
    fig.savefig(out / f"{tag}_sync_check.png")
    mpl.close(fig)

    # 4. the camera frames for the record, cropped and rotated so down is down
    crop_x0 = max(0, top_box[0] - 120)
    crop_x1 = min(still.shape[1], label_box[1] + 160)
    crop_h = int(round(VID_W * (crop_x1 - crop_x0) / OUT_H))
    cy = (top_box[2] + top_box[3]) // 2
    crop_y0 = int(np.clip(cy - crop_h // 2, 0, still.shape[0] - crop_h))
    crop = (crop_x0, crop_x1, crop_y0, crop_y0 + crop_h)
    sync["video_crop_x0x1y0y1"] = [int(v) for v in crop]
    (out / f"{tag}_sync.json").write_text(json.dumps(sync, indent=1) + "\n")
    f_first = int(np.floor(fc - tc_ms / DT_FRAME_MS)) - 1
    f_last = int(np.ceil(fc + (T_END_MS - tc_ms) / DT_FRAME_MS)) + 1
    cap.set(cv2.CAP_PROP_POS_FRAMES, f_first)
    cam = {}
    for f in range(f_first, f_last + 1):
        ok, fr = cap.read()
        img = cv2.rotate(fr[crop[2]:crop[3], crop[0]:crop[1]], cv2.ROTATE_90_CLOCKWISE)
        cam[f] = cv2.cvtColor(cv2.resize(img, (VID_W, OUT_H), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)

    def frame_at(t_now):
        return int(np.clip(round(fc + (t_now - tc_ms) / DT_FRAME_MS), f_first, f_last))

    # 5. key frames
    fig = mpl.figure(figsize=(15, 6.4), dpi=120)
    axw = fig.add_axes([0.05, 0.40, 0.31, 0.52])
    axh = fig.add_axes([0.05, 0.08, 0.31, 0.24], sharex=axw)
    axw.plot(t_ms, work_z, label="total")
    axw.plot(t_ms, work_z_top, "--", label="top work")
    axw.plot(t_ms, work_z_bottom, "--", label="bottom work")
    axh.plot(tv[sharp], dh_vid[sharp], "o", ms=2.5, color="C2", label="video")
    axh.plot(t_ms, dh_acc, color="C3", label="CH4 - CH5")
    axh.set_ylim(-12, 40)
    for n, tk in enumerate(KEY_T, 1):
        for a in (axw, axh):
            a.axvline(tk, color="red", lw=0.8, ls=":")
        axw.text(tk, 1.02, str(n), color="red", ha="center", fontsize=9, transform=axw.get_xaxis_transform())
    axw.set_ylabel("work [J/kg]")
    axw.set_title(f"{spec} trial {drop}", pad=14)
    axw.grid(alpha=0.5)
    axw.legend(loc="lower right", fontsize=7.5)
    axh.set_xlim(-3, 103)
    axh.set_xlabel("time [ms]")
    axh.set_ylabel("height change [mm]")
    axh.grid(alpha=0.5)
    axh.legend(loc="upper left", fontsize=7.5)
    for n, tk in enumerate(KEY_T, 1):
        f = frame_at(tk)
        axi = fig.add_axes([0.40 + ((n - 1) % 4) * 0.15, 0.51 - ((n - 1) // 4) * 0.48, 0.145, 0.43])
        axi.imshow(cam[f])
        axi.set_axis_off()
        wz = float(np.interp(tk, t_ms, work_z))
        dhv = float(np.interp(float(t_of_frame(f)), tv, dh_vid))
        hv = f"height {dhv:+.1f} mm" if t_of_frame(f) >= 2.0 else "frame blurred"
        axi.set_title(f"{n}: t = {t_of_frame(f):.1f} ms\nwork {wz:+.2f} J/kg, {hv}", fontsize=8.5)
    fig.savefig(out / f"{tag}_key_frames.png")
    mpl.close(fig)

    # 6. the video: left panel drawn once, cursor artists blitted on top
    left_w = OUT_W - VID_W
    fig = mpl.figure(figsize=(left_w / 100, OUT_H / 100), dpi=100)
    ax = fig.add_axes([0.11, 0.50, 0.85, 0.44])
    axh = fig.add_axes([0.11, 0.255, 0.85, 0.17], sharex=ax)
    ax.plot(time, work_z, label="total")
    ax.plot(time, work_z_top, "--", label="top work")
    ax.plot(time, work_z_bottom, "--", label="bottom work")
    ax.plot(time[i_pk], work_z[i_pk], "o", ms=7, mfc="none", mec="k", label="max of total, 25 to 45 ms")
    ax.set_xlim(-0.003, 0.103)
    ax.set_ylabel("work [J/kg]", fontsize=14)
    ax.tick_params(labelsize=12, labelbottom=False)
    ax.set_title(f"{spec} trial {drop}", fontsize=16)
    ax.grid()
    ax.legend(loc="best", ncol=2, fontsize=11)
    axh.plot(tv[sharp] * 1e-3, dh_vid[sharp], "o", ms=3, color="C2", label="video (top to carriage)")
    axh.plot(time, dh_acc, color="C3", lw=1.8, label="used by the work sum (CH4 - CH5)")
    axh.axhline(0, color="0.3", lw=0.8)
    axh.set_ylim(-12, 40)                     # the red line runs off the top; the readout gives its value
    axh.set_xlabel("time [s]", fontsize=14)
    axh.set_ylabel("height\nchange [mm]", fontsize=12)
    axh.tick_params(labelsize=11)
    axh.grid()
    axh.legend(loc="upper left", fontsize=10.5)
    cursors = [a.axvline(0.0, color="red", lw=2.2, animated=True) for a in (ax, axh)]
    dot, = ax.plot([0.0], [0.0], "o", color="red", ms=7, zorder=5, animated=True)
    readout = fig.text(0.11, 0.165, "", fontsize=16, family="monospace", va="top", animated=True)
    fig.text(0.11, 0.035,
             f"Video: Sony RX100 IV at {FPS_CAM:.0f} frames/s, camera on its side, rotated here so down is down.\n"
             f"Played {SLOWDOWN}x slower than real time. Synced to the base-plate accelerometer (impact pulse\n"
             f"centroid) to about half a frame (0.5 ms). Work from Justin's numaric_work, m = 1 kg.",
             fontsize=10.5, color="0.35", va="center")
    fig.canvas.draw()
    bg = fig.canvas.copy_from_bbox(fig.bbox)

    def left_panel(t_now):
        ts = t_now * 1e-3
        fig.canvas.restore_region(bg)
        wz = float(np.interp(t_now, t_ms, work_z))
        dhv = float(np.interp(t_now, tv, dh_vid))
        dha = float(np.interp(t_now, t_ms, dh_acc))
        for c in cursors:
            c.set_xdata([ts, ts])
        dot.set_data([ts], [wz])
        vid = f"{dhv:+5.1f} mm" if t_now >= 2.0 else "blurred"
        readout.set_text(f"t = {t_now:6.2f} ms    total work = {wz:+6.2f} J/kg\n"
                         f"height change: video {vid}, CH4 - CH5 {dha:+5.1f} mm")
        for a, art in ((ax, cursors[0]), (axh, cursors[1]), (ax, dot)):
            a.draw_artist(art)
        fig.draw_artist(readout)
        return np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    mp4 = out / f"{tag}_work_video.mp4"
    proc = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{OUT_W}x{OUT_H}", "-r", str(OUT_FPS), "-i", "-",
                             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                             "-preset", "medium", "-movflags", "+faststart", str(mp4)],
                            stdin=subprocess.PIPE)
    n_hold = int(HOLD_S * OUT_FPS)
    n_run = int(round(T_END_MS * 1e-3 * SLOWDOWN * OUT_FPS))
    times = np.concatenate([np.zeros(n_hold), np.linspace(0, T_END_MS, n_run), np.full(n_hold, T_END_MS)])
    for t_now in times:
        f = frame_at(t_now)
        right = cam[f].copy()
        cv2.putText(right, f"{spec} drop {drop}, camera frame {f}", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                    (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(right, f"frame taken at t = {t_of_frame(f):5.1f} ms", (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
        proc.stdin.write(np.ascontiguousarray(np.hstack([left_panel(t_now), right])).tobytes())
    proc.stdin.close()
    proc.wait()
    mpl.close(fig)
    print(f"wrote {mp4} ({len(times) / OUT_FPS:.1f} s, {mp4.stat().st_size / 1e6:.1f} MB)")
    return sync


def summary(out: Path):
    """One panel per specimen: height change from the video against the one in the
    work sum, over the first 60 ms."""
    tracks = sorted(out.glob("corny*_drop*_video_track.csv"))
    if not tracks:
        return
    n = len(tracks)
    fig, axs = mpl.subplots(1, n, figsize=(2.6 * n, 3.9), dpi=130, sharey=True)
    axs = np.atleast_1d(axs)
    for ax, path in zip(axs, tracks):
        spec, drop = path.name.split("_")[:2]
        drop = int(drop.removeprefix("drop"))
        tr = np.loadtxt(path, delimiter=",", skiprows=1)
        t_ms, ch4, ch5 = load_drop(CACHE / f"{spec}_waveforms_50kHz.csv", drop)
        time = t_ms * 1e-3
        v4 = sp.integrate.cumulative_trapezoid(ch4 * 9.81, time, initial=0)
        v5 = sp.integrate.cumulative_trapezoid(ch5 * 9.81, time, initial=0)
        dh_acc = sp.integrate.cumulative_trapezoid(v4 - v5, time, initial=0) * 1e3
        sharp = tr[:, 1] >= 2.0
        ax.plot(tr[sharp, 1], tr[sharp, 5], "o", ms=2.5, color="C2", label="video")
        ax.plot(t_ms, dh_acc, color="C3", lw=1.6, label="work sum (CH4 - CH5)")
        ax.axhline(0, color="0.3", lw=0.8)
        ax.axvspan(25, 45, color="0.85", zorder=0)
        ax.set_xlim(0, 60)
        ax.set_ylim(-12, 40)
        ax.set_title(f"{spec} drop {drop}", fontsize=10)
        ax.set_xlabel("time [ms]")
        ax.grid(alpha=0.4)
    axs[0].set_ylabel("change in specimen height [mm]")
    axs[0].legend(loc="upper left", fontsize=7.5)
    fig.suptitle("Specimen height change: measured in the video (green) and the one Justin's work sum "
                 "integrates (red). Gray: his 25 to 45 ms peak window.", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "height_change_video_vs_work_sum.png")
    mpl.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("specimens", nargs="*", default=list(SPECS))
    ap.add_argument("--out-dir", type=Path, default=HERE)
    ap.add_argument("--summary-only", action="store_true", help="only redraw the all-specimen figure")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if not args.summary_only:
        for spec in args.specimens:
            run(spec, args.out_dir)
    summary(args.out_dir)


if __name__ == "__main__":
    main()
