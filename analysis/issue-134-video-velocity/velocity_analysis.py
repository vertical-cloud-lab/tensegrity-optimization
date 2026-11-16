"""Velocity of the wired top tip before and after impact, from the video tracks,
and the same final velocity from integrating the top accelerometer (issue #134).

Video (per clip):
  v = (pixel displacement * true height [m]) / (frame interval [s] * perceived height [px])
  * true height: the overall printed height of the design (bottom of the bottom
    joints to the top of the accelerometer housings), from the design's STL
    (heights.json). The design key's H_mm is the node-plane height and leaves
    out 20 to 22 mm of joints and housings, so it does not match what the
    camera sees.
  * perceived height: x_bottom - x_top in the clip's last frame (specimen at
    rest), hand-marked on one clip per specimen (annotations.json).
  * frame interval: 1 / 959.04 s.
  Impact time t50: the moment the tip's downward velocity has fallen to half of
  its free-fall value (linear interpolation between frames). Initial velocity:
  mean over t50-25 ms to t50-5 ms. Final velocity: mean over t50+5 ms to
  t50+25 ms. The 5 ms gaps keep the impact itself out of both averages.

Accelerometer (per drop, drops 1 to 20):
  v(t) = v0 + integral of the top accelerometer (CH2, CH3, CH4) from the start
  of the record, with gravity taken out of the vertical axis (an accelerometer
  reads 0 g in free fall). v0 is straight down, equal to the specimen's mean
  video initial velocity carried forward in free fall to the start of the
  record. The impact time and windows are defined exactly as for the video.

Usage: python velocity_analysis.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import integrate

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
TRACKS = RES / "tracks"
WAVES = HERE / "_cache" / "waveforms"
G = 9.81
DT_MS = 1000.0 / 959.04
GAP_MS = 5.0
WIN_MS = 20.0


def load_inputs():
    specs = json.loads((HERE / "inputs" / "specimens.json").read_text())
    return specs


# ---------------------------------------------------------------- video ----
def impact_t50(t_ms: np.ndarray, v_down: np.ndarray, x_px: np.ndarray, x_rest: float,
               m_per_px: float) -> tuple[float, float]:
    """t50: the first time the downward velocity falls below half of its
    free-fall value, searched only where the tip is within 120 px of its rest
    position (it cannot stop anywhere else, so a tracking glitch further up the
    frame is not taken for the impact). Free-fall value: median velocity while
    the tip is 120 to 520 px short of its rest position."""
    xm = 0.5 * (x_px[:-1] + x_px[1:])
    ok = np.isfinite(v_down) & np.isfinite(xm)
    ff = ok & (xm > x_rest - 520) & (xm < x_rest - 120)
    if ff.sum() < 8:
        return np.nan, np.nan
    lvl = float(np.median(v_down[ff]))
    cand = np.flatnonzero(ok & (xm >= x_rest - 120))
    for j, i in enumerate(cand):
        if v_down[i] < 0.5 * lvl:
            prev = [k for k in range(i - 1, -1, -1) if ok[k]]
            if not prev:
                return np.nan, lvl
            i0 = prev[0]
            a, b = v_down[i0], v_down[i]
            frac = (a - 0.5 * lvl) / (a - b) if a != b else 0.0
            return float(t_ms[i0] + frac * (t_ms[i] - t_ms[i0])), lvl
    return np.nan, lvl


def hampel(v: np.ndarray, half: int = 3, thresh: float = 1.0) -> np.ndarray:
    """Blank single-frame tracking glitches: samples more than `thresh` m/s
    from the median of their +-`half` neighbours."""
    out = v.copy()
    for i in range(len(v)):
        if not np.isfinite(v[i]):
            continue
        nb = v[max(0, i - half):i + half + 1]
        nb = nb[np.isfinite(nb)]
        if len(nb) >= 3 and abs(v[i] - np.median(nb)) > thresh:
            out[i] = np.nan
    return out


def window_mean(t, v, lo, hi, robust=False):
    """Mean over the window. robust=True drops samples more than 25 % away from
    the window median (tracking glitches; used before impact, where the tip is
    in free fall and its velocity barely changes)."""
    m = (t >= lo) & (t <= hi) & np.isfinite(v)
    if robust and m.sum() > 3:
        med = np.median(v[m])
        m &= np.abs(v - med) <= 0.25 * abs(med)
    if m.sum() < 0.6 * WIN_MS / DT_MS:
        return np.nan, np.nan, int(m.sum())
    return float(np.mean(v[m])), float(np.std(v[m], ddof=1)), int(m.sum())


def video_clip(track_csv: Path, meta: dict, spec: dict) -> dict:
    tr = pd.read_csv(track_csv)
    perceived_px = meta["x_bottom_px"] - meta["x_top_px"]
    m_per_px = spec["true_height_mm"] * 1e-3 / perceived_px
    x = tr.x_px.to_numpy(); y = tr.y_px.to_numpy()
    f = tr.frame.to_numpy()
    # per-frame velocity (m/s), at the midpoint between frames
    vx = np.diff(x) * m_per_px / (DT_MS * 1e-3)      # +x = down in the world
    vy = np.diff(y) * m_per_px / (DT_MS * 1e-3)      # in-plane horizontal
    t = (f[:-1] + 0.5) * DT_MS
    v_down = vx.copy()
    ncc = tr.ncc.to_numpy()
    bad = (ncc[:-1] < 0.45) | (ncc[1:] < 0.45)
    v_down[bad] = np.nan; vy[bad] = np.nan
    x_rest = float(np.nanmedian(x[-30:]))
    t50, v_ff = impact_t50(t, v_down, x, x_rest, m_per_px)
    out = dict(specimen=meta["specimen"], clip=meta["clip"], perceived_height_px=round(perceived_px, 1),
               true_height_mm=spec["true_height_mm"], mm_per_px=round(m_per_px * 1e3, 4),
               n_tracked=meta["n_tracked"])
    if not np.isfinite(t50):
        out["status"] = "no impact found in the tracked frames"
        return out
    pre = (t50 - GAP_MS - WIN_MS, t50 - GAP_MS)
    post = (t50 + GAP_MS, t50 + GAP_MS + WIN_MS)
    vz = -v_down                                     # + up
    # tracking glitches after impact (template switches) give single-frame
    # spikes; blank them in the final window only (the impact itself is a
    # real 5 m/s change within a few frames and stays out of both windows)
    post_m = (t >= t50 + GAP_MS - 3 * DT_MS) & (t <= t50 + GAP_MS + WIN_MS + 3 * DT_MS)
    vz_h, vy_h = hampel(np.where(post_m, vz, np.nan)), hampel(np.where(post_m, vy, np.nan))
    n_glitch = int(np.sum(np.isfinite(np.where(post_m, vz, np.nan)) & ~np.isfinite(vz_h)))
    vz = np.where(post_m & np.isfinite(vz), vz_h, vz)
    vy = np.where(post_m & np.isfinite(vy), vy_h, vy)
    vi_z, vi_z_sd, ni = window_mean(t, vz, *pre, robust=True)
    vf_z, vf_z_sd, nf = window_mean(t, vz, *post)
    keep = np.isfinite(vz)
    mpre = (t >= pre[0]) & (t <= pre[1]) & keep
    if mpre.sum() > 3:
        med = np.median(vz[mpre]); keep &= ~(mpre & (np.abs(vz - med) > 0.25 * abs(med)))
    vy = np.where(keep | ~((t >= pre[0]) & (t <= pre[1])), vy, np.nan)
    vi_y, _, _ = window_mean(t, vy, *pre)
    vf_y, _, _ = window_mean(t, vy, *post)
    sp = np.hypot(vz, vy)
    vi_s, vi_s_sd, _ = window_mean(t, sp, *pre, robust=True)
    vf_s, vf_s_sd, _ = window_mean(t, sp, *post)
    out.update(status="ok" if np.isfinite(vi_z) and np.isfinite(vf_z) else
               "track too short for a full window",
               t50_frame=round(t50 / DT_MS, 2), n_pre=ni, n_post=nf, n_post_glitches=n_glitch,
               v_initial_z=vi_z, v_initial_z_sd=vi_z_sd, v_final_z=vf_z, v_final_z_sd=vf_z_sd,
               v_initial_y=vi_y, v_final_y=vf_y,
               v_initial=np.hypot(vi_z, vi_y), v_final=np.hypot(vf_z, vf_y),
               speed_initial_mean=vi_s, speed_final_mean=vf_s,
               ratio=np.hypot(vf_z, vf_y) / np.hypot(vi_z, vi_y),
               ratio_z=-vf_z / vi_z)
    # keep the trace for plots
    out["_trace"] = dict(t_rel_ms=t - t50, vz=vz, vy=vy)
    return out


# --------------------------------------------------------- accelerometer ----
def accel_drop(t_ms, a_g, v0_down, t_pre_center_rel):
    """Integrate the 3-axis top accelerometer for one drop.

    a_g: (n, 3) array of CH2, CH3, CH4 in G (CH4 vertical, + up).
    v0_down: the video initial speed (m/s, positive), which applies at the
    centre of the pre-impact window, t50 + t_pre_center_rel (negative, ms).
    Returns the post-window means and the trace.
    """
    t = t_ms * 1e-3
    acc = a_g * G
    acc[:, 2] -= G                                   # kinematic = specific force - g (up)
    dv = integrate.cumulative_trapezoid(acc, t, axis=0, initial=0)
    t50 = np.nan
    v_start = -v0_down
    for _ in range(3):                               # carry v0 from the window centre to t=0
        vz = v_start + dv[:, 2]
        below = np.flatnonzero(vz > 0.5 * v_start)   # downward speed below half
        if len(below) == 0:
            return None
        k = below[0]
        if k == 0:
            t50 = float(t_ms[0])
        else:
            a, b = vz[k - 1], vz[k]
            frac = (0.5 * v_start - a) / (b - a)
            t50 = float(t_ms[k - 1] + frac * (t_ms[k] - t_ms[k - 1]))
        # free fall from the window centre (t50 + t_pre_center_rel) to t = 0
        dt_ff = (0.0 - (t50 + t_pre_center_rel)) * 1e-3
        v_start = -(v0_down + G * dt_ff)
    v = np.column_stack([dv[:, 0], dv[:, 1], v_start + dv[:, 2]])
    m = (t_ms >= t50 + GAP_MS) & (t_ms <= t50 + GAP_MS + WIN_MS)
    vm = v[m].mean(axis=0)
    return dict(t50_ms=t50, v_start_z=v_start, vf_x=vm[0], vf_y=vm[1], vf_z=vm[2],
                vf_speed=float(np.linalg.norm(vm)), vf_xz=float(np.hypot(vm[0], vm[2])),
                vf_yz=float(np.hypot(vm[1], vm[2])),
                mean_g_post=a_g[m].mean(axis=0).tolist(), trace=(t_ms - t50, v))


def load_waveforms(spec: str) -> pd.DataFrame:
    return pd.read_csv(WAVES / f"{spec}_waveforms_50kHz.csv")


def main():
    specs = load_inputs()
    RES.mkdir(exist_ok=True)
    rows, traces = [], {}
    for meta_path in sorted(TRACKS.glob("*_meta.json")):
        meta = json.loads(meta_path.read_text())
        spec = specs[meta["specimen"]]
        r = video_clip(TRACKS / meta_path.name.replace("_meta.json", "_track.csv"), meta, spec)
        tr = r.pop("_trace", None)
        if tr is not None:
            traces[meta["clip"]] = tr
        r["shift_ncc"] = meta["shift_ncc"]
        rows.append(r)
    clips = pd.DataFrame(rows)
    clips.to_csv(RES / "video_per_clip.csv", index=False, float_format="%.4f")

    ok = clips[clips.status == "ok"]
    agg = ok.groupby("specimen").agg(
        n_clips=("clip", "count"),
        v_initial_mean=("v_initial", "mean"), v_initial_sd=("v_initial", "std"),
        v_final_mean=("v_final", "mean"), v_final_sd=("v_final", "std"),
        v_initial_z_mean=("v_initial_z", "mean"), v_initial_z_sd=("v_initial_z", "std"),
        v_final_z_mean=("v_final_z", "mean"), v_final_z_sd=("v_final_z", "std"),
        ratio_mean=("ratio", "mean"), ratio_sd=("ratio", "std"),
        ratio_z_mean=("ratio_z", "mean"), ratio_z_sd=("ratio_z", "std"),
        within_window_sd_initial=("v_initial_z_sd", "mean"),
        within_window_sd_final=("v_final_z_sd", "mean"),
    ).reset_index()

    # accelerometer integration, every drop of every specimen with a video result
    acc_rows, acc_traces = [], {}
    for _, s in agg.iterrows():
        sp = s.specimen
        wf = load_waveforms(sp)
        v0 = -s.v_initial_z_mean                     # downward speed, m/s
        for drop, g in wf.groupby("drop_number"):
            r = accel_drop(g.time_ms.to_numpy(), g[["ch2_g", "ch3_g", "ch4_g"]].to_numpy(float),
                           v0, -(GAP_MS + WIN_MS / 2))
            if r is None:
                continue
            tr = r.pop("trace")
            mg = r.pop("mean_g_post")
            acc_rows.append(dict(specimen=sp, drop=int(drop), v0_video=v0, **r,
                                 ch2_mean_g_post=mg[0], ch3_mean_g_post=mg[1], ch4_mean_g_post=mg[2]))
            if drop in (10, 11):
                acc_traces[(sp, int(drop))] = tr
    acc = pd.DataFrame(acc_rows)
    acc.to_csv(RES / "accel_integration_per_drop.csv", index=False, float_format="%.4f")
    acc_agg = acc.groupby("specimen").agg(
        n_drops=("drop", "count"),
        acc_vf_z_mean=("vf_z", "mean"), acc_vf_z_sd=("vf_z", "std"),
        acc_vf_speed_mean=("vf_speed", "mean"), acc_vf_speed_sd=("vf_speed", "std"),
        acc_vf_x_mean=("vf_x", "mean"), acc_vf_y_mean=("vf_y", "mean"),
        ch4_mean_g_post=("ch4_mean_g_post", "mean"),
    ).reset_index()
    summ = agg.merge(acc_agg, on="specimen", how="left")
    summ["batch"] = summ.specimen.map(lambda k: specs[k]["batch"])
    summ["T180_mean"] = summ.specimen.map(lambda k: specs[k]["T180_mean"])
    summ["T180_sd"] = summ.specimen.map(lambda k: specs[k]["T180_sd"])
    summ.to_csv(RES / "specimen_summary.csv", index=False, float_format="%.4f")
    np.save(RES / "_traces.npy", dict(video=traces, accel=acc_traces), allow_pickle=True)
    print(summ.round(3).to_string())


if __name__ == "__main__":
    main()
