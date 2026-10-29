#!/usr/bin/env python3
"""Session-level QC comparison: round-1 campaign vs the 8/24 round-2 sessions.

Round 2 was run by a different crew (Ronnie, Sam, Andrew, Tim) than the
round-1 campaign. This script compares the two rounds on every channel the
committed data can support that is about the rig, the schedule, and the
session conduct rather than the specimen designs:

* rig input state per session (input peak G, input delta-v, dv-health flags)
  from the campaign summary CSVs;
* session schedule and cadence (start/end, inter-drop intervals, mid-session
  pauses, turnaround between specimens) from the per-drop event_time stamps;
* within-session stability of t180 over a matched window (the first 19
  stabilized drops of every session, so 101-drop round-1 sessions are
  compared with 21-capture round-2 sessions on equal footing).

Outputs
    bo/t3-prism-round-qc-comparison.csv          per-session QC table
    bo/figures/t3-prism-round-qc-comparison.png  4-panel evidence figure

Usage
    python bo/t3_prism_round_qc_comparison.py

Notes on provenance: per-drop files are the stabilized lists (the first two
valid captures of each session are discarded upstream by the PR #86
pipeline), so cadence and stability are computed over scored drops only.
Timestamps are recorded in UTC; the schedule panel converts to Mountain
time (UTC-6 in August) because that is the lab's clock.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
FIGDIR = ROOT / "figures"

# Same figure language as the campaign figures: humanist sans, detached
# spines, no grid, 300 dpi. Two-series categorical palette validated for
# CVD separation and surface contrast (blue/orange, marker shape as the
# secondary encoding so identity is never color-alone).
FIGURE_DPI = 300
R1_BLUE = "#3A70D6"
R2_ORANGE = "#D97706"
INK = "#0b0b0b"
MUTED = "#83827d"
FIG_RC = {
    "font.family": "sans-serif",
    "font.sans-serif": [
        "Source Sans Pro", "Source Sans 3", "Open Sans", "Lato",
        "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans",
    ],
    "font.size": 12.5,
    "axes.labelsize": 13.5,
    "axes.titlesize": 14.5,
    "xtick.labelsize": 11.5,
    "ytick.labelsize": 12,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.edgecolor": "#4a4a47",
    "axes.linewidth": 1.3,
}

MATCHED_WINDOW = 19  # scored drops per session in the shortest round-2 sessions
MT_OFFSET_H = -6     # Mountain daylight time relative to the UTC timestamps


def _load():
    r1 = pd.read_csv(ROOT / "t3-prism-per-drop-metrics.csv", parse_dates=["event_time"])
    r2 = pd.read_csv(ROOT / "t3-prism-bo-round1-per-drop-metrics.csv", parse_dates=["event_time"])
    s1 = pd.read_csv(ROOT / "t3-prism-bo-batch-drop-results.csv")
    s2 = pd.read_csv(ROOT / "t3-prism-bo-round1-drop-results.csv")
    return r1, r2, s1, s2


def _session_rows(per_drop: pd.DataFrame, summary: pd.DataFrame, label: str) -> pd.DataFrame:
    rows = []
    for spec, g in per_drop.groupby("specimen"):
        g = g.sort_values("event_time")
        dt = g["event_time"].diff().dt.total_seconds().dropna()
        w = g.head(MATCHED_WINDOW)
        t, e = w["t180"].to_numpy(), w["e_rebound"].to_numpy()
        idx = np.arange(len(t))
        srow = summary.loc[summary["specimen"] == spec].iloc[0]
        rows.append({
            "round": label,
            "specimen": spec,
            "start_utc": g["event_time"].iloc[0],
            "end_utc": g["event_time"].iloc[-1],
            "n_scored": len(g),
            "session_min": (g["event_time"].iloc[-1] - g["event_time"].iloc[0]).total_seconds() / 60,
            "dt_median_s": dt.median(),
            "gap_max_s": dt.max(),
            "n_pauses_gt120s": int((dt > 120).sum()),
            "dv_health": srow["dv_health"],
            "in_dv_ms_mean": srow["in_dv_ms_mean"],
            "in_dv_ms_sd": srow["in_dv_ms_sd"],
            "in_180_g_mean": srow["in_180_g_mean"],
            "in_180_g_sd": srow["in_180_g_sd"],
            "t180_w19_cv_pct": float(np.std(t) / np.mean(t) * 100),
            "t180_w19_slope_pct_per_drop": float(np.polyfit(idx, t, 1)[0] / np.mean(t) * 100),
            "ereb_w19_cv_pct": float(np.std(e) / np.mean(e) * 100),
        })
    return pd.DataFrame(rows)


def build_table() -> pd.DataFrame:
    r1, r2, s1, s2 = _load()
    tab = pd.concat([
        _session_rows(r1, s1, "round 1"),
        _session_rows(r2, s2, "round 2"),
    ]).sort_values("start_utc").reset_index(drop=True)
    return tab


def _style(ax):
    ax.grid(False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_position(("outward", 8))


def render(tab: pd.DataFrame, out_png: Path):
    plt.rcParams.update(FIG_RC)
    fig = plt.figure(figsize=(15.0, 10.2), dpi=FIGURE_DPI, facecolor="white")
    gs = fig.add_gridspec(2, 2, hspace=0.52, wspace=0.30,
                          left=0.065, right=0.985, top=0.90, bottom=0.075)
    ax_g = fig.add_subplot(gs[0, 0])
    ax_dv = fig.add_subplot(gs[1, 0])
    ax_cv = fig.add_subplot(gs[0, 1])
    ax_sched = fig.add_subplot(gs[1, 1])

    x = np.arange(len(tab))
    is_r2 = (tab["round"] == "round 2").to_numpy()
    colors = np.where(is_r2, R2_ORANGE, R1_BLUE)
    markers = np.where(is_r2, "s", "o")
    settled = (tab["dv_health"] == "settled").to_numpy()

    def scatter_by_round(ax, y, yerr, mark_settled=False):
        for i in range(len(tab)):
            face = "white" if (mark_settled and settled[i]) else colors[i]
            ax.errorbar(x[i], y[i], yerr=yerr[i], fmt="none",
                        ecolor=colors[i], elinewidth=1.6, capsize=3, zorder=2)
            ax.scatter(x[i], y[i], s=64, marker=markers[i], facecolor=face,
                       edgecolor=colors[i], linewidth=1.8, zorder=3)

    def session_axis(ax):
        ax.set_xticks(x)
        ax.set_xticklabels(tab["specimen"], rotation=90, fontsize=9.5)
        # light separator between the rounds
        split = np.argmax(is_r2) - 0.5
        ax.axvline(split, color="#d8d7d3", linewidth=1.2, zorder=1)

    # Panel A: input peak G per session
    scatter_by_round(ax_g, tab["in_180_g_mean"].to_numpy(), tab["in_180_g_sd"].to_numpy())
    _style(ax_g)  # before session_axis: moving a spine resets tick-label props
    session_axis(ax_g)
    ax_g.set_ylabel("Input peak (G, mean $\\pm$ sd)")
    ax_g.set_title("A. Rig input state: peak G per session", loc="left")
    ax_g.set_ylim(195, 240)
    ax_g.annotate("Aug 13-17 sessions ran ~20 G softer;\nevery session since Aug 19 sits at 222-232 G",
                  xy=(1.0, 206), xytext=(3.4, 199.5), fontsize=11, color=MUTED,
                  arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.0))

    # Panel B: input delta-v per session
    scatter_by_round(ax_dv, tab["in_dv_ms_mean"].to_numpy(), tab["in_dv_ms_sd"].to_numpy(),
                     mark_settled=True)
    _style(ax_dv)
    session_axis(ax_dv)
    ax_dv.set_ylabel("Input $\\Delta v$ (m/s, mean $\\pm$ sd)")
    ax_dv.set_title("B. Rig input state: carriage $\\Delta v$ per session", loc="left")
    ax_dv.set_ylim(4.95, 5.60)
    ax_dv.annotate('open markers: "settled" dv-health flag\n(4 of 9 round-1 sessions; none in round 2)',
                   xy=(0.0, 5.03), xytext=(1.8, 4.985), fontsize=11, color=MUTED,
                   arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.0))

    # Panel C: within-session t180 stability, matched 19-drop window
    scatter_by_round(ax_cv, tab["t180_w19_cv_pct"].to_numpy(),
                     np.zeros(len(tab)))
    _style(ax_cv)
    session_axis(ax_cv)
    ax_cv.set_ylabel("t180 CV within session (%)")
    ax_cv.set_title("C. t180 stability, first 19 scored drops of every session",
                    loc="left")
    r1max = tab.loc[~is_r2, "t180_w19_cv_pct"].max()
    ax_cv.axhline(r1max, color=R1_BLUE, linewidth=1.2, linestyle=(0, (4, 3)),
                  alpha=0.6)
    ax_cv.text(-0.4, r1max + 0.04, "round-1 max", fontsize=10.5, color=R1_BLUE)
    for spec, why in [("r2d2c2", "drift (T-drift flag)"),
                      ("r2d2c8", "drift + mid-session pause"),
                      ("r2d2c3", "scatter, no drift")]:
        i = tab.index[tab["specimen"] == spec][0]
        ax_cv.annotate(f"{spec}: {why}",
                       xy=(x[i], tab.loc[i, "t180_w19_cv_pct"]),
                       xytext=(x[i] - 9.6, tab.loc[i, "t180_w19_cv_pct"] + 0.02),
                       fontsize=10.5, color=INK,
                       arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9))
    ax_cv.set_ylim(0, 1.65)

    # Panel D: schedule swimlane in Mountain time
    mt = tab.copy()
    mt["start_mt"] = mt["start_utc"] + pd.Timedelta(hours=MT_OFFSET_H)
    mt["end_mt"] = mt["end_utc"] + pd.Timedelta(hours=MT_OFFSET_H)
    days = sorted(mt["start_mt"].dt.date.unique())
    ymap = {d: len(days) - 1 - k for k, d in enumerate(days)}
    for _, row in mt.iterrows():
        d = row["start_mt"].date()
        y = ymap[d]
        h0 = row["start_mt"].hour + row["start_mt"].minute / 60
        h1 = row["end_mt"].hour + row["end_mt"].minute / 60
        c = R2_ORANGE if row["round"] == "round 2" else R1_BLUE
        ax_sched.barh(y, h1 - h0, left=h0, height=0.56, color=c,
                      edgecolor="white", linewidth=0.8, zorder=3)
    ax_sched.set_yticks([ymap[d] for d in days])
    ax_sched.set_yticklabels([pd.Timestamp(d).strftime("Aug %d") for d in days])
    ax_sched.set_xlim(11.5, 20.2)
    ax_sched.set_xticks(range(12, 21))
    ax_sched.set_xticklabels([f"{h:d}:00" for h in range(12, 21)])
    _style(ax_sched)
    ax_sched.set_xlabel("Time of day, Mountain (UTC-6)")
    ax_sched.set_title("D. Session schedule: 5 test days vs one afternoon",
                       loc="left")
    y_r2 = ymap[mt.loc[is_r2, "start_mt"].iloc[0].date()]
    ax_sched.text(17.35, y_r2, "9 sessions in 4.1 h,\nturnarounds 9-35 min",
                  fontsize=11, color=MUTED, va="center")

    # shared legend
    from matplotlib.lines import Line2D
    handles = [
        Line2D([], [], marker="o", linestyle="", markersize=9,
               markerfacecolor=R1_BLUE, markeredgecolor=R1_BLUE,
               label="Round 1 (usual crew, Aug 13-21)"),
        Line2D([], [], marker="s", linestyle="", markersize=9,
               markerfacecolor=R2_ORANGE, markeredgecolor=R2_ORANGE,
               label="Round 2 (substitute crew, Aug 24)"),
    ]
    fig.legend(handles=handles, loc="upper right", ncol=2, frameon=False,
               bbox_to_anchor=(0.985, 0.995), fontsize=13)
    fig.suptitle("Drop-session QC: round 1 vs round 2", x=0.065, y=0.975,
                 ha="left", fontsize=17, fontweight="bold")

    fig.savefig(out_png, dpi=FIGURE_DPI, facecolor="white")
    plt.close(fig)


def main():
    tab = build_table()
    out_csv = ROOT / "t3-prism-round-qc-comparison.csv"
    tab.to_csv(out_csv, index=False)
    print(f"wrote {out_csv} ({len(tab)} sessions)")
    FIGDIR.mkdir(exist_ok=True)
    out_png = FIGDIR / "t3-prism-round-qc-comparison.png"
    render(tab, out_png)
    print(f"wrote {out_png}")


if __name__ == "__main__":
    main()
