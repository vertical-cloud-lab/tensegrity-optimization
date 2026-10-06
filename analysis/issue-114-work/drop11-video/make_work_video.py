"""Side-by-side video for issue #114: Justin's work-vs-time graph on the left with
a red time cursor, and the slow-motion drop video on the right, in sync.

corny7 drop 6 was not filmed (only drops 1, 10 and 20 were, and the clip labeled
"10th" caught drop 11), so this uses drop 11. See README.md.

How the two clocks are matched: the carriage carrying the specimen is tracked
frame by frame in the video (template match on its green label). Its path is a
straight line before impact and a slow rebound after, and the two lines cross at
the centroid of the impact pulse. The same centroid is computed from the
base-plate accelerometer (CH5). Pinning one to the other gives the time of every
video frame on the accelerometer clock.

Usage (from any directory):
    python make_work_video.py              # downloads the clip and CSV on first use
    python make_work_video.py --video corny7-10th.MP4 --csv corny7_waveforms_50kHz.csv

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
CSV_URL = ("https://raw.githubusercontent.com/vertical-cloud-lab/tensegrity-optimization/"
           "5cc4b1e/data/drop-tests/corny7-export/corny7_waveforms_50kHz.csv")
# corny7-10th.MP4 on the lab's public Box share (folder "9-14-2026 - corny_",
# manifest in data/drop-tests/corny-checkin/video/box-ids.json on PR #86)
BOX_URL = ("https://byu.app.box.com/index.php?rm=box_download_shared_file"
           "&shared_name=kkhmvnj9ni19b57dryk3gdroqrp5uf0b&file_id=f_2466875538664")

DROP = 11
FPS_CAM = 959.04              # captureFps in the clip's sidecar (C0265M01.XML)
DT_FRAME_MS = 1000.0 / FPS_CAM
SLOWDOWN = 120                # 100 ms of drop plays over 12 s
OUT_FPS = 30
HOLD_S = 1.0                  # still frames at the start and end
T_END_MS = 99.98

# Pixel boxes in the full 1920 x 1080 camera frame, chosen for this clip.
LABEL_BOX = (1440, 1580, 270, 540)   # x0, x1, y0, y1: green label on the carriage
TEMPLATE_FRAME = 1060                # carriage at rest near the top of its bounce
CROP = (880, 1600, 70, 633)          # part of the camera frame shown (specimen and carriage top)
TRACK_FRAMES = (990, 1140)
OUT_W, OUT_H = 1920, 1080


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
        with opener.open(url, timeout=600) as r, open(dest, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
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


def track_carriage(video: Path, f0: int, f1: int):
    """Horizontal image position of the carriage label in frames f0..f1 (px,
    relative to TEMPLATE_FRAME). The camera is on its side: right in the image
    is down in the lab."""
    x0, x1, y0, y1 = LABEL_BOX
    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_FRAMES, TEMPLATE_FRAME)
    ok, still = cap.read()
    tmpl = cv2.cvtColor(still, cv2.COLOR_BGR2GRAY)[y0:y1, x0:x1]
    cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
    pad = 30
    frames, xs, scores = [], [], []
    for f in range(f0, f1 + 1):
        ok, fr = cap.read()
        if not ok:
            break
        strip = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)[y0 - pad:y1 + pad, :]
        res = cv2.matchTemplate(strip, tmpl, cv2.TM_CCOEFF_NORMED)
        _, score, _, (xi, yi) = cv2.minMaxLoc(res)
        r = res[yi]
        dx = 0.0
        if 0 < xi < len(r) - 1:                  # parabolic sub-pixel peak
            den = r[xi - 1] - 2 * r[xi] + r[xi + 1]
            dx = 0.5 * (r[xi - 1] - r[xi + 1]) / den if den else 0.0
        frames.append(f)
        xs.append(xi + dx - x0)
        scores.append(score)
    return np.array(frames), np.array(xs), np.array(scores)


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


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--video", type=Path, default=CACHE / "corny7-10th.MP4")
    ap.add_argument("--csv", type=Path, default=CACHE / "corny7_waveforms_50kHz.csv")
    ap.add_argument("--out-dir", type=Path, default=HERE)
    args = ap.parse_args()
    if args.csv == CACHE / "corny7_waveforms_50kHz.csv":
        fetch(CSV_URL, args.csv)
    if args.video == CACHE / "corny7-10th.MP4":
        fetch(BOX_URL, args.video)
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    # 1. Justin's work curves for this drop, exactly as his script makes them
    t_ms, ch4, ch5 = load_drop(args.csv, DROP)
    time = t_ms * 1E-3
    work_z, work_z_top, work_z_bottom = numaric_work(time, ch4 * 9.81, ch5 * 9.81)
    i_pk = 1250 + int(np.argmax(work_z[1250:2250]))   # his "peak" window, 25-45 ms

    # 2. match the clocks
    tc_ms, dv, tpk_ms = pulse_centroid_ms(t_ms, ch5)
    frames, xs, scores = track_carriage(args.video, *TRACK_FRAMES)
    fc, p, q = impact_frame(frames, xs)
    t_of_frame = lambda f: tc_ms + (np.asarray(f) - fc) * DT_FRAME_MS   # noqa: E731
    # px per mm from the speed change: (fall slope - rebound slope) = scale * dv
    slope_post = np.polyval(np.polyder(q), fc)
    px_per_mm = (p[0] - slope_post) / (dv * DT_FRAME_MS)
    v_impact = p[0] / px_per_mm / DT_FRAME_MS
    sync = {
        "drop": DROP, "clip": "corny7-10th.MP4 (C0265M01)", "camera_fps": FPS_CAM,
        "impact_frame_subframe": round(fc, 3),
        "ch5_pulse_centroid_ms": round(tc_ms, 3), "ch5_peak_ms": round(tpk_ms, 3),
        "ch5_delta_v_pulse_m_s": round(dv, 3),
        "frame_at_record_start_t0": round(fc - tc_ms / DT_FRAME_MS, 2),
        "frame_at_record_end_t100ms": round(fc + (100 - tc_ms) / DT_FRAME_MS, 2),
        "carriage_px_per_mm": round(float(px_per_mm), 3),
        "carriage_impact_speed_from_video_m_s": round(float(v_impact), 3),
        "rebound_speed_from_video_m_s": round(float(-slope_post / px_per_mm / DT_FRAME_MS), 3),
        "label_match_score_min": round(float(scores.min()), 3),
        "justin_peak_25_45ms": {"t_ms": round(float(t_ms[i_pk]), 2),
                                "work_J_per_kg": round(float(work_z[i_pk]), 4)},
    }
    (out / "sync.json").write_text(json.dumps(sync, indent=1) + "\n")
    print(json.dumps(sync, indent=1))

    # 3. check figure: the carriage in the video against CH5 integrated twice
    # zeroed on the 70-100 ms tail, when the carriage is in the air, so CH5 reads
    # specific force; the carriage's own acceleration is that minus g
    a5 = (ch5 - np.median(ch5[t_ms >= 70])) * 9.81 - 9.81
    v5 = sp.integrate.cumulative_trapezoid(a5, time, initial=0) - v_impact
    y5 = sp.integrate.cumulative_trapezoid(v5, time, initial=0) * 1e3        # mm, up positive
    tv = t_of_frame(frames)
    y_vid = -(xs - np.polyval(p, fc)) / px_per_mm                            # mm, up positive
    fig, axs = mpl.subplots(1, 2, figsize=(11, 4.2), dpi=150, gridspec_kw={"width_ratios": [1, 1.6]})
    for ax, (lo, hi), (ylo, yhi) in zip(axs, [(-5, 15), (-5, 100)], [(-12, 12), (-30, 30)]):
        ax.plot(tv, y_vid - np.interp(tc_ms, tv, y_vid), "o", ms=3.5, label="carriage in the video (label tracking)")
        ax.plot(t_ms, y5 - np.interp(tc_ms, t_ms, y5), lw=1.5, label="base plate from CH5, integrated twice")
        ax.axvline(tc_ms, color="0.5", lw=0.8, ls=":")
        ax.set_xlim(lo, hi)
        ax.set_ylim(ylo, yhi)
        ax.set_xlabel("time on the accelerometer clock [ms]")
        ax.grid(alpha=0.4)
    axs[0].set_ylabel("height relative to impact [mm]")
    axs[0].set_title("impact (sets the sync)", fontsize=10)
    axs[1].set_title("whole record (bounce height is approximate)", fontsize=10)
    axs[1].legend(loc="lower right", fontsize=8)
    fig.suptitle(f"corny7 drop {DROP}: video frame {fc:.2f} = {tc_ms:.2f} ms on the accelerometer clock")
    fig.tight_layout()
    fig.savefig(out / "sync_check.png")
    mpl.close(fig)

    # 4. the work graph by itself, in Justin's format
    fig, ax = mpl.subplots(figsize=(6, 4.2), dpi=150)
    ax.plot(time, work_z, label="total")
    ax.plot(time, work_z_top, "--", label="top work")
    ax.plot(time, work_z_bottom, "--", label="bottom work")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("work [J/kg]")
    ax.set_title(f"corny7 trial {DROP}")
    ax.grid()
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / f"corny7_drop{DROP}_work.png")
    mpl.close(fig)

    # 5. the video
    x0, x1, y0, y1 = CROP
    vid_h = OUT_H
    vid_w = int(round((y1 - y0) * OUT_H / (x1 - x0)))     # after rotating 90 degrees
    left_w = OUT_W - vid_w
    f_first = int(np.floor(fc - tc_ms / DT_FRAME_MS)) - 1
    f_last = int(np.ceil(fc + (T_END_MS - tc_ms) / DT_FRAME_MS)) + 1
    cap = cv2.VideoCapture(str(args.video))
    cap.set(cv2.CAP_PROP_POS_FRAMES, f_first)
    cam = {}
    for f in range(f_first, f_last + 1):
        ok, fr = cap.read()
        img = cv2.rotate(fr[y0:y1, x0:x1], cv2.ROTATE_90_CLOCKWISE)   # lab "down" is down
        cam[f] = cv2.cvtColor(cv2.resize(img, (vid_w, vid_h), interpolation=cv2.INTER_AREA),
                              cv2.COLOR_BGR2RGB)

    key_t = [0.0, 4.0, 10.0, 20.0, 30.0, 41.1, 45.0, 60.0]
    fig = mpl.figure(figsize=(15, 6.2), dpi=120)
    axw = fig.add_axes([0.05, 0.12, 0.33, 0.78])
    axw.plot(time, work_z, label="total")
    axw.plot(time, work_z_top, "--", label="top work")
    axw.plot(time, work_z_bottom, "--", label="bottom work")
    for n, tk in enumerate(key_t, 1):
        axw.axvline(tk * 1e-3, color="red", lw=0.8, ls=":")
        axw.text(tk * 1e-3, 13.5, str(n), color="red", ha="center", fontsize=10)
    axw.set_ylim(-16.5, 15)
    axw.set_xlabel("time [s]")
    axw.set_ylabel("work [J/kg]")
    axw.set_title(f"corny7 trial {DROP}")
    axw.grid(alpha=0.5)
    axw.legend(loc="center", bbox_to_anchor=(0.62, 0.6), fontsize=8)
    for n, tk in enumerate(key_t, 1):
        f = int(round(fc + (tk - tc_ms) / DT_FRAME_MS))
        axi = fig.add_axes([0.40 + ((n - 1) % 4) * 0.15, 0.53 - ((n - 1) // 4) * 0.47, 0.145, 0.42])
        axi.imshow(cam[f])
        axi.set_axis_off()
        wz = float(np.interp(tk, t_ms, work_z))
        axi.set_title(f"{n}: t = {t_of_frame(f):.1f} ms, total {wz:.1f} J/kg", fontsize=9)
    fig.savefig(out / "key_frames.png")
    mpl.close(fig)

    fig = mpl.figure(figsize=(left_w / 100, OUT_H / 100), dpi=100)
    ax = fig.add_axes([0.12, 0.40, 0.84, 0.53])
    ax.plot(time, work_z, label="total")
    ax.plot(time, work_z_top, "--", label="top work")
    ax.plot(time, work_z_bottom, "--", label="bottom work")
    ax.plot(time[i_pk], work_z[i_pk], "o", ms=7, mfc="none", mec="k",
            label="max of total, 25 to 45 ms")
    ax.set_xlim(-0.003, 0.103)
    ax.set_xlabel("time [s]", fontsize=14)
    ax.set_ylabel("work [J/kg]", fontsize=14)
    ax.tick_params(labelsize=12)
    ax.set_title(f"corny7 trial {DROP}", fontsize=16)
    ax.grid()
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=2, fontsize=12, frameon=False)
    cursor = ax.axvline(0.0, color="red", lw=2.2)
    dot, = ax.plot([0.0], [0.0], "o", color="red", ms=7, zorder=5)
    readout = fig.text(0.12, 0.215, "", fontsize=18, family="monospace", va="top")
    fig.text(0.12, 0.06,
             f"Video: Sony RX100 IV at {FPS_CAM:.0f} frames/s, camera on its side, rotated here so down is down.\n"
             f"Played {SLOWDOWN}x slower than real time. Video synced to the base-plate accelerometer\n"
             f"(impact pulse centroid) to about half a frame (0.5 ms). Work from Justin's numaric_work, m = 1 kg.",
             fontsize=10.5, color="0.35", va="center")
    fig.canvas.draw()

    def left_panel(t_ms_now):
        ts = t_ms_now * 1e-3
        cursor.set_xdata([ts, ts])
        wz = float(np.interp(t_ms_now, t_ms, work_z))
        dot.set_data([ts], [wz])
        readout.set_text(f"t = {t_ms_now:6.2f} ms\ntotal work = {wz:6.2f} J/kg")
        fig.canvas.draw()
        return np.asarray(fig.canvas.buffer_rgba())[:, :, :3]

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    mp4 = out / f"corny7_drop{DROP}_work_video.mp4"
    proc = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{OUT_W}x{OUT_H}", "-r", str(OUT_FPS), "-i", "-",
                             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                             "-preset", "medium", "-movflags", "+faststart", str(mp4)],
                            stdin=subprocess.PIPE)
    n_hold = int(HOLD_S * OUT_FPS)
    n_run = int(round(T_END_MS * 1e-3 * SLOWDOWN * OUT_FPS))
    times = np.concatenate([np.zeros(n_hold), np.linspace(0, T_END_MS, n_run), np.full(n_hold, T_END_MS)])
    for t_now in times:
        f = int(round(fc + (t_now - tc_ms) / DT_FRAME_MS))
        right = cam[f].copy()
        cv2.putText(right, f"drop {DROP}, camera frame {f}", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                    (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(right, f"frame taken at t = {t_of_frame(f):5.1f} ms", (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
        proc.stdin.write(np.ascontiguousarray(np.hstack([left_panel(t_now), right])).tobytes())
    proc.stdin.close()
    proc.wait()
    print(f"wrote {mp4} ({len(times) / OUT_FPS:.1f} s, {mp4.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
