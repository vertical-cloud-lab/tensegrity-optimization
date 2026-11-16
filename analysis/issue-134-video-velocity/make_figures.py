"""Figures and tables for issue #134 (run after velocity_analysis.py)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)

INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8c8b86", "#e4e3df"
BATCH_COLOR = {"corny": "#2a78d6", "drran": "#eb6834", "2dran": "#1baf7a"}
BATCH_LABEL = {"corny": "corny (round 4)", "drran": "drran (round 3, print 1)",
               "2dran": "2dran (round 3, print 2)"}
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.titlesize": 11,
                     "axes.spines.top": False, "axes.spines.right": False})

ORDER = {
    "seed": ["6lhxfy", "6nheas", "9hhbkp", "ajhby6", "amdjwm", "autv5r", "bag26v", "bpx68c", "nvxsrv"],
    "r2d2c": [f"r2d2c{i}" for i in range(1, 10)],
    "drran": [f"drran{i}" for i in range(1, 10)],
    "2dran": [f"2dran{i}" for i in range(1, 10)],
    "dran3": [f"dran3{i}" for i in range(1, 10)],
    "corny": [f"corny{i}" for i in range(1, 10)],
    "1sne": [f"1sne{i}" for i in (21, 22, 23, 71, 72, 73, 81, 82, 83)],
}
NOTE = {"seed": "no video", "r2d2c": "no video",
        "dran3": "video exists; wired tip not identified (black struts)", "1sne": "video exists; wired tip not identified (black struts)"}


def fig_ratio(summ: pd.DataFrame, clips: pd.DataFrame):
    rows = [(b, s) for b in ["corny", "drran", "2dran", "dran3", "1sne", "seed", "r2d2c"] for s in ORDER[b]]
    fig, ax = plt.subplots(figsize=(7.2, 13.5))
    y = np.arange(len(rows))[::-1]
    s_idx = summ.set_index("specimen")
    for yi, (b, s) in zip(y, rows):
        if s in s_idx.index:
            r = s_idx.loc[s]
            c = BATCH_COLOR[b]
            pts = clips[(clips.specimen == s) & (clips.status == "ok")].ratio
            ax.scatter(pts, np.full(len(pts), yi), s=14, color=c, alpha=0.45, lw=0, zorder=2)
            ax.errorbar(r.ratio_mean, yi, xerr=r.ratio_sd if np.isfinite(r.ratio_sd) else None,
                        fmt="o", ms=7, color=c, mec="white", mew=1.2, capsize=3, elinewidth=1.4, zorder=3)
            ax.text(0.205, yi, f"{r.ratio_mean:.3f}" + (f" ± {r.ratio_sd:.3f}" if np.isfinite(r.ratio_sd) else ""),
                    va="center", fontsize=8, color=INK2)
        else:
            ax.text(0.003, yi, NOTE[b], va="center", fontsize=8, color=MUTED, style="italic")
    ax.set_yticks(y)
    ax.set_yticklabels([s for _, s in rows], fontsize=8)
    # batch separators and labels
    pos = 0
    for b in ["corny", "drran", "2dran", "dran3", "1sne", "seed", "r2d2c"]:
        n = len(ORDER[b])
        top = y[pos] + 0.5
        ax.axhline(top, color=GRID, lw=1, zorder=0)
        ax.text(0.245, y[pos] - (n - 1) / 2, b, rotation=270, va="center", ha="left", fontsize=9, color=INK2)
        pos += n
    ax.set_xlim(0, 0.25)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xlabel("final / initial speed of the wired top tip (video)")
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_title("Rebound ratio of the accelerometer tip, by specimen\n"
                 "large dot: mean of the filmed drops (bar: ±1 SD); small dots: each drop",
                 loc="left", color=INK)
    fig.tight_layout()
    fig.savefig(FIG / "01_ratio_by_specimen.png", dpi=160)
    plt.close(fig)


def fig_ratio_vs_t180(summ: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    for b, c in BATCH_COLOR.items():
        d = summ[summ.batch == b]
        ax.errorbar(d.T180_mean, d.ratio_mean, xerr=d.T180_sd, yerr=d.ratio_sd, fmt="o", ms=7,
                    color=c, mec="white", mew=1.2, capsize=2.5, elinewidth=1.1, label=BATCH_LABEL[b])
    for _, r in summ.iterrows():
        if r.T180_mean < 0.96 or r.T180_mean > 1.15 or r.ratio_mean > 0.15:
            ax.annotate(r.specimen, (r.T180_mean, r.ratio_mean), xytext=(5, 4), textcoords="offset points",
                        fontsize=8, color=INK2)
    d = summ.dropna(subset=["T180_mean", "ratio_mean"])
    rho, p = stats.spearmanr(d.T180_mean, d.ratio_mean)
    r_p, p_p = stats.pearsonr(d.T180_mean, d.ratio_mean)
    ax.set_xlabel("T180 (top peak / base peak, CFC 180), mean over drops 3 to 20")
    ax.set_ylabel("final / initial speed of the wired top tip (video)")
    ax.grid(color=GRID, lw=0.8)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.set_title(f"Video rebound ratio against T180 ({len(d)} specimens)\n"
                 f"Spearman ρ = {rho:.2f} (p = {p:.2g}), Pearson r = {r_p:.2f} (p = {p_p:.2g})",
                 loc="left", color=INK)
    fig.tight_layout()
    fig.savefig(FIG / "02_ratio_vs_T180.png", dpi=160)
    plt.close(fig)
    return dict(spearman=rho, spearman_p=p, pearson=r_p, pearson_p=p_p, n=len(d))


def fig_parity(summ: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.0))
    panels = [
        ("v_final_z_mean", "v_final_z_sd", "acc_vf_z_mean", "acc_vf_z_sd",
         "vertical velocity after impact (m/s, + up)", "a. Vertical component"),
        ("v_final_mean", "v_final_sd", "acc_vf_speed_mean", "acc_vf_speed_sd",
         "speed after impact (m/s)", "b. Speed (video: 2 in-plane axes; accelerometer: 3 axes)"),
    ]
    for ax, (vx, vxs, ay, ays, lab, title) in zip(axes, panels):
        for b, c in BATCH_COLOR.items():
            d = summ[summ.batch == b]
            ax.errorbar(d[vx], d[ay], xerr=d[vxs], yerr=d[ays], fmt="o", ms=7, color=c, mec="white",
                        mew=1.2, capsize=2.5, elinewidth=1.1, label=BATCH_LABEL[b])
        lim = (0, float(np.nanmax(summ[ay] + summ[ays].fillna(0))) * 1.08)
        ax.plot(lim, lim, color=MUTED, lw=1.2, ls="--", zorder=0)
        ax.text(lim[1] * 0.97, lim[1] * 0.92, "equal", color=MUTED, ha="right", fontsize=8)
        ax.set_xlim(lim); ax.set_ylim(lim)
        ax.set_aspect("equal")
        ax.set_xlabel(f"video: {lab}")
        ax.set_ylabel(f"accelerometer integral: {lab}")
        ax.grid(color=GRID, lw=0.8)
        ax.set_title(title, loc="left", color=INK, fontsize=10)
        err = summ[ay] - summ[vx]
        ax.text(0.03, 0.97, f"integral − video: mean {err.mean():+.2f} m/s, "
                            f"range {err.min():+.2f} to {err.max():+.2f}",
                transform=ax.transAxes, va="top", fontsize=8.5, color=INK2)
    axes[0].legend(frameon=False, fontsize=8.5, loc="lower right")
    fig.suptitle("Final velocity of the wired top tip: integrated accelerometer vs video "
                 "(each point: one specimen; bars: ±1 SD over drops)", x=0.01, ha="left",
                 color=INK, fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "03_final_velocity_integral_vs_video.png", dpi=160)
    plt.close(fig)


def fig_traces(summ: pd.DataFrame, traces: dict, examples):
    fig, axes = plt.subplots(1, len(examples), figsize=(5.0 * len(examples), 4.4), sharey=True)
    for ax, (spec, clip, drop) in zip(np.atleast_1d(axes), examples):
        v = traces["video"].get(clip)
        a = traces["accel"].get((spec, drop))
        ax.axvspan(-25, -5, color="#f0efec", zorder=0)
        ax.axvspan(5, 25, color="#f0efec", zorder=0)
        ax.text(-15, 0.92, "initial\nwindow", ha="center", va="top", fontsize=8, color=INK2,
                transform=ax.get_xaxis_transform())
        ax.text(15, 0.92, "final\nwindow", ha="center", va="top", fontsize=8, color=INK2,
                transform=ax.get_xaxis_transform())
        if a is not None:
            t, vv = a
            ax.plot(t, vv[:, 2], color="#eb6834", lw=2, label=f"accelerometer integral (drop {drop}), vertical")
            m = t > 3
            ax.plot(t[m], np.linalg.norm(vv[m], axis=1), color="#eb6834", lw=1.2, ls=":",
                    label="accelerometer integral, 3-axis speed")
        if v is not None:
            ax.plot(v["t_rel_ms"], v["vz"], "o", ms=3.5, color="#2a78d6", label=f"video ({clip}), vertical")
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.set_xlim(-30, 45)
        ax.set_ylim(-5.6, 2.2)
        ax.set_xlabel("time from impact t50 (ms)")
        ax.grid(color=GRID, lw=0.8)
        r = summ.set_index("specimen").loc[spec]
        ax.set_title(f"{spec}: T180 {r.T180_mean:.3f}, video ratio {r.ratio_mean:.3f}", loc="left",
                     color=INK, fontsize=10)
    np.atleast_1d(axes)[0].set_ylabel("velocity of the wired tip (m/s, + up)")
    np.atleast_1d(axes)[0].legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "04_example_velocity_traces.png", dpi=160)
    plt.close(fig)


def table_md(summ: pd.DataFrame) -> str:
    def pm(m, s, f="{:.3f}"):
        if not np.isfinite(m):
            return ""
        return f.format(m) + ("" if not np.isfinite(s) else " ± " + f.format(s))
    lines = ["| specimen | clips | initial speed (m/s) | final speed (m/s) | final vertical (m/s, + up) "
             "| ratio final/initial | T180 | integral, final vertical (m/s) | integral, final 3-axis speed (m/s) |",
             "|---|---|---|---|---|---|---|---|---|"]
    order = [s for b in ["corny", "drran", "2dran"] for s in ORDER[b]]
    s_idx = summ.set_index("specimen")
    for s in order:
        if s not in s_idx.index:
            continue
        r = s_idx.loc[s]
        lines.append(f"| {s} | {int(r.n_clips)} | {pm(r.v_initial_mean, r.v_initial_sd, '{:.2f}')} | "
                     f"{pm(r.v_final_mean, r.v_final_sd)} | {pm(r.v_final_z_mean, r.v_final_z_sd)} | "
                     f"{pm(r.ratio_mean, r.ratio_sd)} | {pm(r.T180_mean, r.T180_sd)} | "
                     f"{pm(r.acc_vf_z_mean, r.acc_vf_z_sd)} | {pm(r.acc_vf_speed_mean, r.acc_vf_speed_sd)} |")
    return "\n".join(lines)


def main():
    summ = pd.read_csv(RES / "specimen_summary.csv")
    clips = pd.read_csv(RES / "video_per_clip.csv")
    traces = np.load(RES / "_traces.npy", allow_pickle=True).item()
    fig_ratio(summ, clips)
    corr = fig_ratio_vs_t180(summ)
    fig_parity(summ)
    fig_traces(summ, traces, [("corny2", "corny2-10th.MP4", 10), ("corny7", "corny7-10th.MP4", 11)])
    (RES / "specimen_table.md").write_text(table_md(summ) + "\n")
    (RES / "ratio_vs_T180_correlation.json").write_text(json.dumps(corr, indent=1))
    print(json.dumps(corr, indent=1))


if __name__ == "__main__":
    main()
