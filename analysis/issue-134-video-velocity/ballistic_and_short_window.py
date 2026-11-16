"""Issue #134 follow-up (Justin, 2026-11-16): two more checks on the 27 filmed
specimens.

1. The video rebound ratio against the ballistic one of issue #94.
   Ballistic method (``analyze_capture`` in
   ``scripts/analysis/drop_test_abc123_blind_analysis.py`` at a10d890, used by
   every BO round):
     t_second  time from the main impact burst on the top sensor to the largest
               burst 15 to 70 ms later (read as the vertex landing back)
     v_sep     = g * t_second / 2 (free flight under gravity, launched at impact)
     dv        = integral of the base sensor (CH5) over the impact pulse
     e_rebound = v_sep / dv
   Per-specimen values are the campaign tables on branch
   ``claude/issue-98-20260821-0103`` (commit 65ff978), copied to
   ``inputs/ballistic/``.

2. The final velocity from integrating only the vertical axis (CH4) over the
   impact pulse, against the video final velocity. Integration runs from the
   first sample of the record to the end of the pulse: the first time after
   the peak at which CH4 (0.5 ms moving average) falls below 10 % of its peak.
   The velocity there is taken as the final velocity; nothing after it is
   integrated. The initial value is the one of ``velocity_analysis.py`` (the
   video initial velocity carried to the start of the record in free fall).
   A sweep over the integration end time shows how the answer depends on where
   the integration stops.

Run after ``velocity_analysis.py`` (it needs ``results/specimen_summary.csv``,
``results/video_per_clip.csv``, ``results/_traces.npy`` and the waveforms in
``_cache/waveforms``).

Usage: python ballistic_and_short_window.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402
from scipy.ndimage import uniform_filter1d  # noqa: E402

from make_figures import BATCH_COLOR, BATCH_LABEL, GRID, INK, INK2, MUTED, ORDER  # noqa: E402
from velocity_analysis import GAP_MS, WIN_MS, accel_drop, load_waveforms  # noqa: E402

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
FIG = HERE / "figures"
BAL = HERE / "inputs" / "ballistic"
G = 9.81
DT_MS = 1000.0 / 959.04
FS_KHZ = 50.0
SMOOTH_MS = 0.5            # moving average before finding the end of the pulse
END_FRAC = 0.10            # the pulse ends when CH4 falls below this fraction of its peak
SWEEP = np.round(np.arange(1.0, 30.01, 0.25), 2)   # integration end times, ms after t50
VIDEO_HALF_MS = 1.0        # video velocity at time x: mean over x +- 1 ms
MARK = {"corny": "o", "drran": "s", "2dran": "^"}
ROUNDS = {"corny": "round4", "drran": "round3", "2dran": "round3-reprint"}


# ------------------------------------------------------------- ballistic ----
def load_ballistic() -> pd.DataFrame:
    d = pd.concat([pd.read_csv(BAL / f"t3-prism-bo-{r}-drop-results.csv") for r in ROUNDS.values()])
    d = d[["specimen", "n_valid", "in_dv_ms_mean", "in_dv_ms_sd", "t_second_ms_mean",
           "t_second_ms_sd", "e_rebound_mean", "e_rebound_sd"]].copy()
    d["v_sep_mean"] = G * d.t_second_ms_mean * 1e-3 / 2
    d["v_sep_sd"] = G * d.t_second_ms_sd * 1e-3 / 2
    # drops behind the means: the per-drop tables list the drops used
    per = pd.concat([pd.read_csv(BAL / f"t3-prism-bo-{r}-per-drop-metrics.csv") for r in ROUNDS.values()])
    chk = per.groupby("specimen").e_rebound.agg(["mean", "std", "count"]).rename(
        columns={"mean": "e_perdrop_mean", "std": "e_perdrop_sd", "count": "n_perdrop"})
    return d.merge(chk, left_on="specimen", right_index=True, how="left")


# ---------------------------------------------------- short-window integral ----
def pulse_end(t_ms: np.ndarray, a: np.ndarray) -> int:
    """Index of the first sample after the peak at which the 0.5 ms moving
    average of ``a`` falls below END_FRAC of its peak."""
    s = uniform_filter1d(a, int(round(SMOOTH_MS * FS_KHZ)))
    ip = int(np.argmax(s))
    below = np.flatnonzero(s[ip:] < END_FRAC * s[ip])
    return ip + int(below[0]) if len(below) else len(a) - 1


def short_window(summ: pd.DataFrame):
    rows, sweep_rows = [], []
    for _, s in summ.iterrows():
        sp = s.specimen
        wf = load_waveforms(sp)
        v0 = -s.v_initial_z_mean
        for drop, g in wf.groupby("drop_number"):
            t = g.time_ms.to_numpy()
            a3 = g[["ch2_g", "ch3_g", "ch4_g"]].to_numpy(float)
            r = accel_drop(t, a3.copy(), v0, -(GAP_MS + WIN_MS / 2))
            if r is None:
                continue
            t_rel, v = r["trace"]
            vz = v[:, 2]
            k4 = pulse_end(t, a3[:, 2])
            k5 = pulse_end(t, g.ch5_g.to_numpy(float))
            fin = (t_rel >= GAP_MS) & (t_rel <= GAP_MS + WIN_MS)
            rows.append(dict(specimen=sp, drop=int(drop), t50_ms=r["t50_ms"], v_start_z=r["v_start_z"],
                             ch4_peak_g=float(uniform_filter1d(a3[:, 2], 25).max()),
                             pulse_end_ms=float(t_rel[k4]), v_pulse_z=float(vz[k4]),
                             pulse_end_ch5_ms=float(t_rel[k5]), v_pulse_ch5_z=float(vz[k5]),
                             vf_z_full=float(vz[fin].mean())))
            sweep_rows.append(dict(specimen=sp, drop=int(drop),
                                   **{f"{x:g}": float(np.interp(x, t_rel, vz)) for x in SWEEP}))
    return pd.DataFrame(rows), pd.DataFrame(sweep_rows)


def video_at(traces: dict, clips: pd.DataFrame, xs: np.ndarray) -> pd.DataFrame:
    """Mean vertical video velocity over x +- 1 ms, per clip, then averaged
    over the clips of each specimen."""
    out = {}
    for _, c in clips.iterrows():
        tr = traces["video"].get(c["clip"])
        if tr is None:
            continue
        t, z = tr["t_rel_ms"], tr["vz"]
        vals = []
        for x in xs:
            m = (t >= x - VIDEO_HALF_MS) & (t <= x + VIDEO_HALF_MS) & np.isfinite(z)
            vals.append(float(np.mean(z[m])) if m.sum() else np.nan)
        out.setdefault(c.specimen, []).append(vals)
    return pd.DataFrame({sp: np.nanmean(np.array(v), axis=0) for sp, v in out.items()}, index=xs).T


# ------------------------------------------------------------------ plots ----
def _scatter(ax, d, x, xs, y, ys, label=True):
    for b in ["corny", "drran", "2dran"]:
        e = d[d.batch == b]
        ax.errorbar(e[x], e[y], xerr=e[xs] if xs else None, yerr=e[ys] if ys else None,
                    fmt=MARK[b], ms=7, color=BATCH_COLOR[b], mec="white", mew=1.2, capsize=2.5,
                    elinewidth=1.1, label=BATCH_LABEL[b] if label else None)


def _equal(ax, lim):
    ax.plot(lim, lim, color=MUTED, lw=1.2, ls="--", zorder=0)
    span = lim[1] - lim[0]
    ax.text(lim[1] - 0.02 * span, lim[1] - 0.07 * span, "equal", color=MUTED, ha="right", fontsize=8)
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_aspect("equal")
    ax.grid(color=GRID, lw=0.8)


def fig_ballistic(d: pd.DataFrame, st: dict):
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.6))
    ax = axes[0]
    _scatter(ax, d, "ratio_z_mean", "ratio_z_sd", "e_rebound_mean", "e_rebound_sd")
    _equal(ax, (0, 0.18))
    ax.set_xlabel("video: final / initial vertical velocity of the wired tip")
    ax.set_ylabel("ballistic (issue #94): e_rebound = g t_second / (2 Δv)")
    ax.set_title("a. Ratio of final to initial velocity", loc="left", color=INK, fontsize=10)
    ax.text(0.03, 0.97, f"ballistic / video: median {st['ratio_of_ratios_median']:.2f} "
                        f"(range {st['ratio_of_ratios_min']:.2f} to {st['ratio_of_ratios_max']:.2f})\n"
                        f"Spearman ρ = {st['spearman_ratio']:.2f} (p = {st['spearman_ratio_p']:.2g}), n = {st['n']}",
            transform=ax.transAxes, va="top", fontsize=8.5, color=INK2)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(0.0, 0.88))

    ax = axes[1]
    _scatter(ax, d, "v_final_z_mean", "v_final_z_sd", "v_sep_mean", "v_sep_sd", label=False)
    _equal(ax, (0, 0.8))
    ax.set_xlabel("video: vertical velocity after impact (m/s, + up)")
    ax.set_ylabel("ballistic: v_sep = g t_second / 2 (m/s)")
    ax.set_title("b. Numerator: final velocity", loc="left", color=INK, fontsize=10)
    ax.text(0.03, 0.97, f"ballistic − video: mean {st['vsep_minus_video_mean']:+.2f} m/s, "
                        f"range {st['vsep_minus_video_min']:+.2f} to {st['vsep_minus_video_max']:+.2f}",
            transform=ax.transAxes, va="top", fontsize=8.5, color=INK2)

    ax = axes[2]
    d = d.assign(v_initial_down=-d.v_initial_z_mean)
    _scatter(ax, d, "v_initial_down", "v_initial_z_sd", "in_dv_ms_mean", "in_dv_ms_sd", label=False)
    _equal(ax, (4.3, 5.7))
    ax.axhline(5.47, color=MUTED, lw=0.8, ls=":")
    ax.text(5.68, 5.485, "free fall from 60 in: 5.47 m/s", color=MUTED, fontsize=8, va="bottom", ha="right")
    ax.set_xlabel("video: vertical velocity before impact (m/s, down)")
    ax.set_ylabel("ballistic: Δv of the base sensor, CH5 (m/s)")
    ax.set_title("c. Denominator: initial velocity", loc="left", color=INK, fontsize=10)
    ax.text(0.97, 0.03, f"ballistic − video: mean {st['dv_minus_video_mean']:+.2f} m/s, "
                        f"range {st['dv_minus_video_min']:+.2f} to {st['dv_minus_video_max']:+.2f}\n"
                        f"base Δv − video change (initial + final): mean "
                        f"{st['dv_minus_video_change_mean']:+.2f} m/s, SD {st['dv_minus_video_change_sd']:.2f}",
            transform=ax.transAxes, va="bottom", ha="right", fontsize=8.5, color=INK2)
    fig.suptitle("Rebound ratio of the wired top tip: ballistic method (issue #94) vs video "
                 "(each point: one specimen; bars: ±1 SD over drops)", x=0.01, ha="left", color=INK, fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "06_ratio_ballistic_vs_video.png", dpi=160, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def fig_short(sw: pd.DataFrame, sweep_err: pd.DataFrame, pulse_iqr, st: dict):
    fig = plt.figure(figsize=(16.5, 5.8))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.25])
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    lim = (-0.9, 1.7)
    panels = [("acc_vf_z_full_mean", "acc_vf_z_full_sd", "a. Whole record: integrated through the final window",
               "full"),
              ("acc_v_pulse_mean", "acc_v_pulse_sd", "b. Pulse only: integration stops when CH4 < 10 % of peak",
               "pulse")]
    for ax, (y, ys, title, key) in zip(axes[:2], panels):
        _scatter(ax, sw, "v_final_z_mean", "v_final_z_sd", y, ys, label=key == "full")
        ax.axhline(0, color=MUTED, lw=0.8); ax.axvline(0, color=MUTED, lw=0.8)
        _equal(ax, lim)
        ax.set_xlabel("video: vertical velocity after impact (m/s, + up)")
        ax.set_ylabel("accelerometer integral, vertical axis only (m/s, + up)")
        ax.set_title(title, loc="left", color=INK, fontsize=10)
        ax.text(0.03, 0.97, f"integral − video: mean {st[key + '_mean']:+.2f} m/s, SD {st[key + '_sd']:.2f}\n"
                            f"range {st[key + '_min']:+.2f} to {st[key + '_max']:+.2f}, "
                            f"RMS {st[key + '_rms']:.2f} m/s\n"
                            f"Pearson r with video = {st[key + '_r']:.2f}",
                transform=ax.transAxes, va="top", fontsize=8.5, color=INK2)
        for _, rr in sw.iterrows():
            if key == "pulse" and rr[y] - rr.v_final_z_mean < -0.25:
                ax.annotate(rr.specimen, (rr.v_final_z_mean, rr[y]), xytext=(6, -3), textcoords="offset points",
                            fontsize=7.5, color=INK2)
    axes[0].legend(frameon=False, fontsize=8.5, loc="lower right")

    ax = axes[2]
    ax.axvspan(GAP_MS, GAP_MS + WIN_MS, color="#f0efec", zorder=0)
    ax.text(GAP_MS + WIN_MS / 2, 0.97, "video final window", ha="center", va="top", fontsize=8, color=INK2,
            transform=ax.get_xaxis_transform())
    ax.axvspan(*pulse_iqr, color="#dcdad5", zorder=0)
    ax.text(np.mean(pulse_iqr), 0.03, "pulse ends\n(middle half\nof drops)", ha="center", va="bottom",
            fontsize=7.5, color=INK2, transform=ax.get_xaxis_transform())
    ax.axhline(0, color=MUTED, lw=0.9)
    x = sweep_err.index.to_numpy(float)
    for col, c, lab in [("held", "#eb6834", "integral at the stop time − video final velocity\n"
                                            "(what you get if you stop there)"),
                        ("matched", "#2a78d6", "integral − video, both at the same time\n"
                                               "(error of the integral itself)")]:
        ok = np.isfinite(sweep_err[f"{col}_median"].to_numpy(float))
        ax.fill_between(x[ok], sweep_err[f"{col}_q25"].to_numpy(float)[ok],
                        sweep_err[f"{col}_q75"].to_numpy(float)[ok], color=c, alpha=0.18, lw=0)
        ax.plot(x[ok], sweep_err[f"{col}_median"].to_numpy(float)[ok], color=c, lw=2, label=lab)
    ax.set_xlim(0, 30)
    ax.set_ylim(-1.0, 1.4)
    ax.set_xlabel("time after impact t50 where the integration stops (ms)")
    ax.set_ylabel("integral − video, vertical (m/s)")
    ax.grid(color=GRID, lw=0.8)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_title("c. Error against where the integration stops\n"
                 "(line: median of the 27 specimens; band: middle half of them)",
                 loc="left", color=INK, fontsize=10)
    fig.suptitle("Final vertical velocity of the wired top tip: accelerometer integrated over the whole record "
                 "or over the impact pulse only, vs video", x=0.01, ha="left", color=INK, fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "07_final_velocity_pulse_only_vs_video.png", dpi=160, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def tip_height(clip: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Time after t50 (ms) and height of the tracked tip above its position at
    t50 (mm, + up), from the video track of one clip."""
    stem = clip["clip"].replace(".MP4", "")
    tr = pd.read_csv(RES / "tracks" / f"{stem}_track.csv")
    t = (tr.frame.to_numpy() - clip.t50_frame) * DT_MS
    x = tr.x_px.to_numpy()                              # + down in the world
    ok = np.isfinite(x)
    x0 = np.interp(0.0, t[ok], x[ok])
    return t, -(x - x0) * clip.mm_per_px


def fig_height(d: pd.DataFrame, clips: pd.DataFrame, examples):
    """Height of the wired tip after impact (video), with the ballistic flight
    time and the path the ballistic model assumes."""
    fig, axes = plt.subplots(2, 3, figsize=(16.5, 8.8), sharex=True, sharey=True)
    b = d.set_index("specimen")
    shades = ["#2a78d6", "#5f9be3", "#93bdee"]
    for ax, sp in zip(axes.ravel(), examples):
        c_all = clips[(clips.specimen == sp) & (clips.status == "ok")]
        ax.axvspan(15, 70, color="#f0efec", zorder=0)
        ax.axhline(0, color=MUTED, lw=0.9)
        for k, (_, c) in enumerate(c_all.iterrows()):
            t, up = tip_height(c)
            ax.plot(t, up, "-", lw=1.5, color=shades[k % 3],
                    label="video, each filmed drop (one shade per drop)" if k == 0 else None)
        ts = b.loc[sp, "t_second_ms_mean"]
        vs = b.loc[sp, "v_sep_mean"]
        tt = np.linspace(0, ts, 200)
        ax.plot(tt, vs * tt - 0.5 * G * (tt * 1e-3) ** 2 * 1e3, color="#eb6834", lw=2.2,
                label="ballistic model: leaves at impact, free flight under gravity, lands at t_second")
        ax.axvline(ts, color="#eb6834", lw=1.0, ls="--")
        ax.text(ts + 1.5, 0.95, f"t_second {ts:.0f} ms", color=INK2, fontsize=8,
                transform=ax.get_xaxis_transform(), va="top")
        ax.set_xlim(-5, 120)
        ax.set_ylim(-6, 36)
        ax.grid(color=GRID, lw=0.8)
        ax.set_title(f"{sp}: video final {b.loc[sp, 'v_final_z_mean']:.2f} m/s, "
                     f"ballistic v_sep {vs:.2f} m/s", loc="left", color=INK, fontsize=10)
    for ax in axes[-1]:
        ax.set_xlabel("time after impact t50 (ms)")
    for ax in axes[:, 0]:
        ax.set_ylabel("height of the wired tip above\nits position at impact (mm)")
    h, lab = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower left", ncol=2, frameon=False, fontsize=9, bbox_to_anchor=(0.01, 0.0))
    fig.suptitle("Where the wired tip goes after impact (video) and the hop the ballistic model assumes "
                 "(gray band: the 15 to 70 ms window in which t_second is searched)",
                 x=0.01, ha="left", color=INK, fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIG / "08_tip_height_after_impact.png", dpi=160, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def height_stats(clips: pd.DataFrame) -> pd.DataFrame:
    """Per clip: how far the tip rises above its position at impact, by when,
    and the largest upward velocity in the rise, from the video track."""
    rows = []
    for _, c in clips.iterrows():
        t, up = tip_height(c)
        ok = np.isfinite(up) & (t >= 0) & (t <= 75)
        tt, uu = t[ok], up[ok]
        i = int(np.argmax(uu))
        rows.append(dict(specimen=c.specimen, clip=c["clip"], rise_mm_by_75ms=float(uu[i]),
                         t_max_rise_ms=float(tt[i]), track_end_ms=float(np.nanmax(t[np.isfinite(up)]))))
    return pd.DataFrame(rows)


def _err_stats(err: pd.Series, a: pd.Series, b: pd.Series, key: str) -> dict:
    return {f"{key}_mean": float(err.mean()), f"{key}_sd": float(err.std()), f"{key}_min": float(err.min()),
            f"{key}_max": float(err.max()), f"{key}_rms": float(np.sqrt((err ** 2).mean())),
            f"{key}_r": float(stats.pearsonr(a, b)[0])}


def table_md(d: pd.DataFrame) -> str:
    def pm(m, s, f="{:.3f}"):
        if not np.isfinite(m):
            return ""
        return f.format(m) + ("" if not np.isfinite(s) else " ± " + f.format(s))
    lines = ["| specimen | video ratio, vertical | ballistic e_rebound | t_second (ms) | ballistic v_sep (m/s) "
             "| video final vertical (m/s) | base Δv, CH5 (m/s) | video initial vertical (m/s, down) "
             "| integral, whole record (m/s) | integral, pulse only (m/s) | pulse end (ms after t50) |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    idx = d.set_index("specimen")
    for s in [s for b in ["corny", "drran", "2dran"] for s in ORDER[b]]:
        if s not in idx.index:
            continue
        r = idx.loc[s]
        lines.append(f"| {s} | {pm(r.ratio_z_mean, r.ratio_z_sd)} | {pm(r.e_rebound_mean, r.e_rebound_sd)} | "
                     f"{pm(r.t_second_ms_mean, r.t_second_ms_sd, '{:.1f}')} | {pm(r.v_sep_mean, r.v_sep_sd)} | "
                     f"{pm(r.v_final_z_mean, r.v_final_z_sd)} | {pm(r.in_dv_ms_mean, r.in_dv_ms_sd, '{:.2f}')} | "
                     f"{pm(-r.v_initial_z_mean, r.v_initial_z_sd, '{:.2f}')} | "
                     f"{pm(r.acc_vf_z_full_mean, r.acc_vf_z_full_sd)} | {pm(r.acc_v_pulse_mean, r.acc_v_pulse_sd)} | "
                     f"{pm(r.pulse_end_ms_mean, r.pulse_end_ms_sd, '{:.2f}')} |")
    return "\n".join(lines)


def main():
    summ = pd.read_csv(RES / "specimen_summary.csv")
    clips = pd.read_csv(RES / "video_per_clip.csv")
    clips = clips[clips.status == "ok"]
    traces = np.load(RES / "_traces.npy", allow_pickle=True).item()

    # 1. ballistic vs video
    bal = load_ballistic()
    d = summ.merge(bal, on="specimen", how="left")
    st = dict(n=int(d.e_rebound_mean.notna().sum()))
    rr = d.e_rebound_mean / d.ratio_z_mean
    st.update(ratio_of_ratios_median=float(rr.median()), ratio_of_ratios_min=float(rr.min()),
              ratio_of_ratios_max=float(rr.max()))
    st["spearman_ratio"], st["spearman_ratio_p"] = map(float, stats.spearmanr(d.ratio_z_mean, d.e_rebound_mean))
    st["pearson_ratio"], st["pearson_ratio_p"] = map(float, stats.pearsonr(d.ratio_z_mean, d.e_rebound_mean))
    e = d.v_sep_mean - d.v_final_z_mean
    st.update(vsep_minus_video_mean=float(e.mean()), vsep_minus_video_min=float(e.min()),
              vsep_minus_video_max=float(e.max()),
              vsep_over_video_median=float((d.v_sep_mean / d.v_final_z_mean).median()))
    e = d.in_dv_ms_mean + d.v_initial_z_mean
    st.update(dv_minus_video_mean=float(e.mean()), dv_minus_video_min=float(e.min()),
              dv_minus_video_max=float(e.max()))
    # the base pulse integral is the carriage's whole velocity change (arrival plus
    # any rebound); the video's whole change of the tip is initial + final
    e = d.in_dv_ms_mean - (d.v_final_z_mean - d.v_initial_z_mean)
    st.update(dv_minus_video_change_mean=float(e.mean()), dv_minus_video_change_sd=float(e.std()),
              dv_minus_video_change_min=float(e.min()), dv_minus_video_change_max=float(e.max()),
              dv_minus_video_change_pct=float((e / (d.v_final_z_mean - d.v_initial_z_mean)).mean() * 100))
    st["spearman_vsep_vfinal"], st["spearman_vsep_vfinal_p"] = map(
        float, stats.spearmanr(d.v_final_z_mean, d.v_sep_mean))
    # free flight at the video final velocity: flight time and hop height
    d["free_flight_ms_at_video_vf"] = 2 * d.v_final_z_mean / G * 1e3
    d["free_flight_height_mm_at_video_vf"] = d.v_final_z_mean ** 2 / (2 * G) * 1e3
    st["perdrop_mean_matches_table"] = bool(np.allclose(d.e_perdrop_mean, d.e_rebound_mean, atol=5e-4))

    # 2. pulse-only integration
    per, sweep = short_window(summ)
    per.to_csv(RES / "accel_pulse_only_per_drop.csv", index=False, float_format="%.4f")
    agg = per.groupby("specimen").agg(
        acc_v_pulse_mean=("v_pulse_z", "mean"), acc_v_pulse_sd=("v_pulse_z", "std"),
        acc_v_pulse_ch5_mean=("v_pulse_ch5_z", "mean"),
        acc_vf_z_full_mean=("vf_z_full", "mean"), acc_vf_z_full_sd=("vf_z_full", "std"),
        pulse_end_ms_mean=("pulse_end_ms", "mean"), pulse_end_ms_sd=("pulse_end_ms", "std"),
        pulse_end_ch5_ms_mean=("pulse_end_ch5_ms", "mean")).reset_index()
    d = d.merge(agg, on="specimen", how="left")
    for key, col in [("full", "acc_vf_z_full_mean"), ("pulse", "acc_v_pulse_mean"),
                     ("pulse_ch5", "acc_v_pulse_ch5_mean")]:
        st.update(_err_stats(d[col] - d.v_final_z_mean, d[col], d.v_final_z_mean, key))
    st["pulse_end_ms_median"] = float(per.pulse_end_ms.median())
    st["pulse_end_ms_q25"], st["pulse_end_ms_q75"] = map(float, per.pulse_end_ms.quantile([0.25, 0.75]))
    soft = d.specimen.isin(["corny6", "corny7", "corny8", "corny9"])
    for key, col in [("full", "acc_vf_z_full_mean"), ("pulse", "acc_v_pulse_mean")]:
        st[f"{key}_mean_soft"] = float((d[col] - d.v_final_z_mean)[soft].mean())
        st[f"{key}_mean_rest"] = float((d[col] - d.v_final_z_mean)[~soft].mean())

    # sweep over the stop time
    acc_x = sweep.drop(columns="drop").groupby("specimen").mean()
    acc_x.columns = acc_x.columns.astype(float)
    vid_x = video_at(traces, clips, SWEEP)
    vf = d.set_index("specimen").v_final_z_mean
    held = acc_x.sub(vf, axis=0)
    matched = acc_x - vid_x.loc[acc_x.index, acc_x.columns]
    rows = []
    for x in SWEEP:
        h, m = held[x], matched[x]
        rows.append(dict(t_stop_ms=x, held_median=h.median(), held_q25=h.quantile(0.25), held_q75=h.quantile(0.75),
                         held_mean=h.mean(), held_rms=np.sqrt((h ** 2).mean()),
                         matched_median=m.median() if x >= 2.5 else np.nan,
                         matched_q25=m.quantile(0.25) if x >= 2.5 else np.nan,
                         matched_q75=m.quantile(0.75) if x >= 2.5 else np.nan,
                         matched_mean=m.mean(), matched_rms=np.sqrt((m ** 2).mean())))
    sweep_err = pd.DataFrame(rows).set_index("t_stop_ms")
    sweep_err.to_csv(RES / "pulse_only_stop_time_sweep.csv", float_format="%.4f")
    for x in (3.0, 5.0, 10.0, 15.0, 20.0, 25.0):
        st[f"matched_median_at_{x:g}ms"] = float(sweep_err.loc[x, "matched_median"])
        st[f"held_median_at_{x:g}ms"] = float(sweep_err.loc[x, "held_median"])
    best = sweep_err.held_rms.idxmin()
    st["held_rms_min"] = float(sweep_err.held_rms.min())
    st["held_rms_min_at_ms"] = float(best)

    d.to_csv(RES / "ballistic_and_pulse_only_summary.csv", index=False, float_format="%.4f")
    (RES / "ballistic_and_pulse_only_table.md").write_text(table_md(d) + "\n")
    (RES / "ballistic_and_pulse_only_stats.json").write_text(json.dumps(st, indent=1))

    fig_ballistic(d, st)
    fig_short(d, sweep_err, (st["pulse_end_ms_q25"], st["pulse_end_ms_q75"]), st)
    fig_height(d, clips, ["corny2", "corny7", "corny9", "drran2", "2dran5", "2dran9"])
    hs = height_stats(clips)
    hs.to_csv(RES / "tip_rise_after_impact_per_clip.csv", index=False, float_format="%.3f")
    st["rise_mm_median"] = float(hs.rise_mm_by_75ms.median())
    st["rise_mm_min"], st["rise_mm_max"] = float(hs.rise_mm_by_75ms.min()), float(hs.rise_mm_by_75ms.max())
    st["ballistic_hop_mm_min"] = float((d.v_sep_mean ** 2 / (2 * G) * 1e3).min())
    st["ballistic_hop_mm_max"] = float((d.v_sep_mean ** 2 / (2 * G) * 1e3).max())
    (RES / "ballistic_and_pulse_only_stats.json").write_text(json.dumps(st, indent=1))
    print(json.dumps(st, indent=1))


if __name__ == "__main__":
    main()
