#!/usr/bin/env python3
"""T-drift history + CH5 input history for the 1/2 in PU mat era.

Answers PR #86 (comment 5401181788): is transmissibility drifting within
sessions, has it drifted before, and how has the CH5 base-plate input moved
over the mat's life?  Reads only the per-drop metrics already committed by the
per-dataset analyses (no raw data needed):

  - r2d2-checkin, sobol-campaign (+ partial sessions)   [tail baseline]
  - speed-decay, calibration-check, pre-post-grease     [pre-trigger baseline]

Note: calibration-check "before" is the same physical 101-drop 08-17 bpx68c
session as sobol-campaign "bpx68c" (two pipelines, two baselines); the tail-
baseline copy is used for the history plot and the duplicate is kept only in
the stats table, flagged.

Outputs:
  data/drop-tests/r2d2-checkin/figures/04_t_drift_history.png
  data/drop-tests/r2d2-checkin/figures/t_drift_history.json
"""

import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DT = os.path.join(ROOT, "data", "drop-tests")
OUT = os.path.join(DT, "r2d2-checkin", "figures")

BLUE = "#2a78d6"
ORANGE = "#eb6834"
GRAY = "#9a9891"
TEXT = "#0b0b0b"
TEXT2 = "#52514e"
SURFACE = "#fcfcfb"


def load(path):
    with open(os.path.join(DT, path)) as fh:
        return json.load(fh)


def collect_sessions():
    """Return list of dicts: label, t0 (ISO), rows, baseline, duplicate_of."""
    out = []

    def add(label, rows, baseline, dup=None):
        rows = [r for r in rows if r.get("t180") is not None]
        if len(rows) >= 6:
            out.append(dict(label=label, t0=rows[0]["event_time"], rows=rows,
                            baseline=baseline, duplicate_of=dup))

    for name, path in [("r2d2-checkin", "r2d2-checkin/figures/campaign_metrics.json"),
                       ("sobol", "sobol-campaign/figures/campaign_metrics.json"),
                       ("sobol-partial", "sobol-campaign/figures/partial_sessions_metrics.json")]:
        d = load(path)
        for spec, v in d["specimens"].items():
            add(spec, v["rows"], "tail")

    sd = load("speed-decay/figures/speed_decay_metrics.json")
    for k, rows in sd["rows"].items():
        add("specimen2-" + k, rows, "pretrig")

    cc = load("calibration-check/figures/calibration_check_metrics.json")
    add("bpx68c-cal-before", cc["rows"]["before"], "pretrig", dup="bpx68c")
    add("bpx68c-cal-after", cc["rows"]["after"], "pretrig")

    gg = load("pre-post-grease/figures/pre_post_grease_metrics.json")
    add("specimen2-grease", gg["rows"], "pretrig")

    out.sort(key=lambda s: s["t0"])
    return out


def ols(y):
    y = np.asarray(y, float)
    x = np.arange(len(y), dtype=float)
    n = len(y)
    b, a = np.polyfit(x, y, 1)
    resid = y - (a + b * x)
    sxx = float(((x - x.mean()) ** 2).sum())
    s2 = float((resid ** 2).sum()) / max(n - 2, 1)
    se = math.sqrt(s2 / sxx) if sxx > 0 else float("nan")
    t = b / se if se > 0 else float("nan")
    p = math.erfc(abs(t) / math.sqrt(2)) if t == t else float("nan")
    return b, float(y.mean()), p


def session_stats(s):
    rows = s["rows"]
    res = dict(label=s["label"], date=s["t0"][:10], n=len(rows),
               baseline=s["baseline"], duplicate_of=s["duplicate_of"])
    for key, name in [("t180", "t180"), ("in_180_g", "in180"),
                      ("in_raw_g", "inraw"), ("out_180_g", "out180"),
                      ("in_width_ms", "width"), ("in_dv_ms", "dv")]:
        vals = [r[key] for r in rows if r.get(key) is not None]
        if len(vals) < 4:
            continue
        b, m, p = ols(vals)
        cv = 100.0 * float(np.std(vals, ddof=1)) / m
        f5 = float(np.mean(vals[:5]))
        l5 = float(np.mean(vals[-5:]))
        res[name] = dict(mean=round(m, 4), cv_pct=round(cv, 2),
                         slope_pct_per_drop=round(100 * b / m, 4),
                         p=float(f"{p:.2e}"), end_to_end_pct=round(100 * (l5 - f5) / f5, 2))
    return res


def main():
    sessions = collect_sessions()
    stats = [session_stats(s) for s in sessions]

    plot_sessions = [s for s in sessions if s["duplicate_of"] is None]

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12.5, 10.5), facecolor=SURFACE,
        gridspec_kw=dict(height_ratios=[1, 1.05], hspace=0.55))

    # ---- panel 1: CH5 input CFC-180 across the mat era -------------------
    ax1.set_facecolor(SURFACE)
    x0 = 0
    ticks, tick_labels = [], []
    for s in plot_sessions:
        rows = s["rows"]
        y = [r["in_180_g"] for r in rows]
        x = np.arange(x0, x0 + len(y))
        hot = s["label"].startswith("r2d2")
        ax1.plot(x, y, color=ORANGE if hot else BLUE, lw=1.4 if hot else 1.0,
                 solid_capstyle="round", zorder=3 if hot else 2)
        short = s["label"].replace("specimen2-", "s2-")
        ticks.append(x0 + len(y) / 2)
        tick_labels.append(f"{s['t0'][5:10]} {short}")
        x0 += len(y) + 6
    ax1.set_xlim(-10, x0 + 4)
    ax1.set_ylim(185, 246)
    ax1.set_ylabel("CH5 input, CFC-180 peak (G)", fontsize=9, color=TEXT)
    ax1.set_title("CH5 base-plate input over the 1/2 in mat's life "
                  "(every session, ~1,150 stabilized drops, 08-10 → 08-24)",
                  fontsize=10.5, color=TEXT, loc="left", pad=10)
    ax1.annotate("tower recovering\n(Δv 4.6 → 5.3 m/s)", xy=(190, 236),
                 fontsize=7.5, color=TEXT2, ha="center")
    ax1.annotate("campaign plateau ≈ 220–232 G", xy=(760, 242),
                 fontsize=7.5, color=TEXT2, ha="center")
    ax1.set_xticks(ticks)
    ax1.set_xticklabels(tick_labels, rotation=90, fontsize=6.6, color=TEXT2)
    ax1.tick_params(labelsize=8, colors=TEXT2)
    ax1.tick_params(axis="x", length=0)
    ax1.grid(axis="y", color="#e8e7e3", lw=0.6, zorder=0)
    for sp in ("top", "right", "bottom"):
        ax1.spines[sp].set_visible(False)
    ax1.spines["left"].set_color("#d8d7d2")

    # ---- panel 2: within-session T drift, normalized ---------------------
    ax2.set_facecolor(SURFACE)
    for s in plot_sessions:
        rows = s["rows"]
        t = np.array([r["t180"] for r in rows])
        ref = t[:5].mean()
        y = 100.0 * (t / ref - 1.0)
        x = np.arange(1, len(t) + 1)
        if s["label"] == "r2d2c2":
            ax2.plot(x, y, color=ORANGE, lw=2.2, zorder=5)
            ax2.annotate("r2d2c2 (08-24): +3.5 % step,\noutput-side, plateaus ≈ drop 14",
                         xy=(x[-1], y[-1]), xytext=(x[-1] + 2, y[-1]),
                         fontsize=8, color=ORANGE, va="center")
        elif s["label"] == "r2d2c1":
            ax2.plot(x, y, color=BLUE, lw=2.0, zorder=4)
            ax2.annotate("r2d2c1 (08-24): flat", xy=(x[-1], y[-1]),
                         xytext=(x[-1] + 2, y[-1] - 0.25), fontsize=8,
                         color=BLUE, va="center")
        else:
            ax2.plot(x, y, color=GRAY, lw=0.8, alpha=0.55, zorder=2)
    ax2.annotate("all 14 prior 1/2 in mat sessions\n(each ≤ ±2 % end-to-end)",
                 xy=(78, -2.6), fontsize=8, color=TEXT2, ha="center")
    ax2.axhline(0, color="#d8d7d2", lw=0.8, zorder=1)
    ax2.set_xlabel("recorded drop number within session (after 2-drop warm-up discard)",
                   fontsize=9, color=TEXT)
    ax2.set_ylabel("T (CFC-180) vs first 5 drops (%)", fontsize=9, color=TEXT)
    ax2.set_title("Within-session transmissibility drift, every 1/2 in mat session — "
                  "r2d2c2 is the outlier", fontsize=10.5, color=TEXT, loc="left", pad=10)
    ax2.tick_params(labelsize=8, colors=TEXT2)
    ax2.grid(axis="y", color="#e8e7e3", lw=0.6, zorder=0)
    ax2.set_xlim(0, 125)
    for sp in ("top", "right"):
        ax2.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax2.spines[sp].set_color("#d8d7d2")

    fig.savefig(os.path.join(OUT, "04_t_drift_history.png"), dpi=150,
                bbox_inches="tight", facecolor=SURFACE)

    with open(os.path.join(OUT, "t_drift_history.json"), "w") as fh:
        json.dump(dict(note="Within-session drift stats for every 1/2 in mat "
                            "session with committed per-drop metrics; slopes "
                            "are OLS on stabilized drops, %/drop of the "
                            "session mean; p from normal approx (residuals "
                            "autocorrelated - treat as descriptive).",
                       sessions=stats), fh, indent=1)

    for st in stats:
        print(f"{st['label']:20s} {st['date']} n={st['n']:3d} "
              f"T {st['t180']['mean']:.4f} slope {st['t180']['slope_pct_per_drop']:+.3f}%/dr "
              f"end2end {st['t180']['end_to_end_pct']:+.2f}% | "
              f"in180 {st['in180']['mean']:6.1f} G {st['in180']['end_to_end_pct']:+.2f}%")


if __name__ == "__main__":
    main()
