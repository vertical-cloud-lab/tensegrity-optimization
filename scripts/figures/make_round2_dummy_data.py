#!/usr/bin/env python3
"""Generate the clearly-marked SYNTHETIC (dummy) round-2 dataset and figures.

The round-2 batch (Ax trials 10-18) is physically printed but not yet
drop-tested. Per PR #76 direction (comment 2026-08-23), the manuscript is
written at its intended final scope, so this script fabricates stand-in
"measured" values for the round-2 articles and renders the three figures the
Results section needs. Everything produced here is dummy data:

  * every figure carries a diagonal "SYNTHETIC PLACEHOLDER DATA" watermark,
  * dummy points are drawn in violet, matching the manuscript's \\dummy color,
  * the CSV filename ends in -DUMMY.csv.

Replace by rerunning the real campaign pipeline once the batch is tested.
Seed-round values below are the real measured results (Table 5 of the
manuscript); only the round-2 measured columns are invented.
"""

import csv
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIGDIR = ROOT / "figures" / "bo"
DATADIR = ROOT / "manuscript" / "data"

VIOLET = "#8E44AD"
BLUE = "#2E75C9"
ORANGE = "#E8703A"
GRAY = "#888888"

plt.rcParams.update({
    "font.size": 15,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 200,
})

# Real seed-round measurements (article, t180 mean, E_reb mJ). amdjwm is
# excluded (no weighed mass -> no E_reb), matching the manuscript.
SEED = [
    ("6lhxfy", 0.8931, 13.9),
    ("6nheas", 0.9970, 13.1),
    ("bpx68c", 1.0111, 6.2),
    ("9hhbkp", 1.0183, 6.9),
    ("nvxsrv", 1.0275, 8.2),
    ("autv5r", 1.0404, 8.8),
    ("bag26v", 1.0616, 7.7),
]

# DUMMY round-2 "measurements" (invented; clearly marked in every output).
# Columns: trial, article, mass g, t180 mean, t180 sd, E_reb mJ, f_n Hz,
# predicted t180 mean, predicted t180 sd (predictions are the real archived
# posterior means from round2-as-printed-solid-mass-projection.csv).
ROUND2 = [
    (10, "kq3w7f", 18.41, 0.8580, 0.0038, 12.1, 355, 0.8728, 0.0526),
    (11, "x8pdz2", 19.52, 0.9020, 0.0041, 11.4, 402, 0.8849, 0.0749),
    (12, "w4jn8y", 19.88, 0.9510, 0.0029,  8.9, 296, 0.9256, 0.0945),
    (13, "e9tk2m", 19.37, 0.9420, 0.0033,  7.4, 344, 0.9477, 0.0464),
    (14, "u5rb6x", 20.68, 0.9760, 0.0040,  8.1, 331, 0.9530, 0.0944),
    (15, "r2vq9c", 20.31, 0.9180, 0.0036, 10.6, 318, 0.9051, 0.0912),
    (16, "m7hs4t", 19.05, 0.8970, 0.0044,  9.8, 388, 0.9102, 0.0728),
    (17, "h3fc9q", 19.94, 0.9880, 0.0027,  7.9, 419, 0.9548, 0.0711),
    (18, "p6dm3z", 20.41, 1.0040, 0.0031,  7.2, 307, 0.9868, 0.0663),
]

# DUMMY budget-matched Sobol baseline "measurements" (nine invented articles).
BASELINE = [
    (0.982, 9.4), (1.031, 8.0), (0.958, 12.2), (1.044, 7.6), (1.012, 10.9),
    (0.996, 13.5), (1.055, 8.8), (0.969, 11.1), (1.021, 6.8),
]

REF_POINT = (1.10, 15.0)  # hypervolume reference (worst-corner anchor)


def pareto_front(points):
    """Non-dominated set for joint minimization of both coordinates."""
    front = []
    for p in points:
        if not any(q[0] <= p[0] and q[1] <= p[1] and q != p for q in points):
            front.append(p)
    return sorted(front)


def hypervolume(points, ref):
    """2-D dominated hypervolume (minimization) against ref corner."""
    front = pareto_front(points)
    hv, prev_y = 0.0, ref[1]
    for x, y in front:
        if x >= ref[0] or y >= ref[1]:
            continue
        hv += (ref[0] - x) * (prev_y - y)
        prev_y = y
    return hv


def watermark(ax):
    ax.text(0.5, 0.5, "SYNTHETIC\nPLACEHOLDER DATA", transform=ax.transAxes,
            fontsize=34, color=VIOLET, alpha=0.18, ha="center", va="center",
            rotation=30, fontweight="bold", zorder=0)


def fig_pred_vs_meas():
    fig, ax = plt.subplots(figsize=(7.2, 6.4))
    watermark(ax)
    lo, hi = 0.82, 1.06
    ax.plot([lo, hi], [lo, hi], color=GRAY, lw=1.2, ls="--", zorder=1)
    for _, art, _, t, ts, _, _, pt, pts in ROUND2:
        ax.errorbar(pt, t, xerr=pts, yerr=ts, fmt="D", color=VIOLET,
                    ecolor=VIOLET, elinewidth=1.2, capsize=3, ms=8, zorder=3)
        ax.annotate(art, (pt, t), textcoords="offset points", xytext=(7, 5),
                    fontsize=11, color=GRAY)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("Predicted $t_{180}$ (posterior mean $\\pm$ sd)")
    ax.set_title("Measured $t_{180}$ (stabilized mean $\\pm$ per-drop sd)\n"
                 "round-2 articles, dummy values", loc="left", fontsize=15)
    fig.tight_layout()
    fig.savefig(FIGDIR / "t3-prism-bo-round2-pred-vs-meas-DUMMY.png")
    plt.close(fig)


def fig_round2_pareto():
    fig, ax = plt.subplots(figsize=(7.6, 6.6))
    watermark(ax)
    seed_pts = [(t, e) for _, t, e in SEED]
    r2_pts = [(t, e) for _, _, _, t, _, e, _, _, _ in ROUND2]
    front = pareto_front(seed_pts + r2_pts)
    fx, fy = zip(*front)
    ax.plot(fx, fy, color=BLUE, lw=2.4, zorder=2, label="Pareto front (rounds 1+2)")
    for (art, t, e) in SEED:
        ax.plot(t, e, "o", mfc="none", mec="black", ms=10, mew=1.6, zorder=3)
        ax.annotate(art, (t, e), textcoords="offset points", xytext=(7, 6),
                    fontsize=11, color=GRAY)
    for _, art, _, t, _, e, _, _, _ in ROUND2:
        ax.plot(t, e, "D", color=VIOLET, ms=9, zorder=4)
        ax.annotate(art, (t, e), textcoords="offset points", xytext=(7, -12),
                    fontsize=11, color=VIOLET)
    ax.plot([], [], "o", mfc="none", mec="black", ms=9, mew=1.6,
            label="Seed round (measured)")
    ax.plot([], [], "D", color=VIOLET, ms=9,
            label="Round 2 (synthetic dummy)")
    ax.legend(frameon=False, loc="upper right", fontsize=12)
    ax.set_xlabel("Filtered peak-acceleration ratio $t_{180}$ (lower is better)")
    ax.set_title("Rebound energy to payload (mJ per drop, lower is better)",
                 loc="left", fontsize=15)
    fig.tight_layout()
    fig.savefig(FIGDIR / "t3-prism-bo-round2-pareto-DUMMY.png")
    plt.close(fig)


def fig_hypervolume():
    seed_pts = [(t, e) for _, t, e in SEED]
    r2_pts = [(t, e) for _, _, _, t, _, e, _, _, _ in ROUND2]

    def cumulative(points0, added):
        xs, ys, pts = [], [], list(points0)
        for i, p in enumerate(added, start=len(points0) + 1):
            pts.append(p)
            xs.append(i)
            ys.append(hypervolume(pts, REF_POINT))
        return xs, ys

    hv_seed = hypervolume(seed_pts, REF_POINT)
    bo_x, bo_y = cumulative(seed_pts, r2_pts)
    bl_x, bl_y = cumulative(seed_pts, BASELINE)

    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    watermark(ax)
    ax.plot([len(seed_pts)] + bo_x, [hv_seed] + bo_y, "-D", color=VIOLET,
            ms=7, lw=2, label="BO (qNEHVI) round 2, dummy")
    ax.plot([len(seed_pts)] + bl_x, [hv_seed] + bl_y, "-s", color=GRAY,
            ms=6, lw=2, label="Budget-matched Sobol baseline, dummy")
    ax.axvline(len(seed_pts), color="black", lw=0.8, ls=":")
    ax.annotate("seed round\n(measured)", (len(seed_pts), hv_seed),
                textcoords="offset points", xytext=(10, -6), fontsize=11)
    ax.set_xlabel("Tested articles with both objectives")
    ax.set_title("Dominated hypervolume (ref. point 1.10, 15.0 mJ)",
                 loc="left", fontsize=15)
    ax.legend(frameon=False, fontsize=12, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGDIR / "t3-prism-bo-hypervolume-DUMMY.png")
    plt.close(fig)

    return hv_seed, bo_y[-1], bl_y[-1]


def write_csv():
    path = DATADIR / "round2-measured-DUMMY.csv"
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["# SYNTHETIC PLACEHOLDER DATA: round-2 measured values are"
                    " invented stand-ins pending the physical drop sessions"])
        w.writerow(["trial_index", "article", "mass_g", "t180_mean", "t180_sd",
                    "e_reb_mJ", "f_n_hz", "pred_t180_mean", "pred_t180_sd"])
        for row in ROUND2:
            w.writerow(row)
    return path


def main():
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig_pred_vs_meas()
    fig_round2_pareto()
    hv_seed, hv_bo, hv_bl = fig_hypervolume()
    path = write_csv()

    seed_pts = [(t, e) for _, t, e in SEED]
    r2_pts = [(t, e) for _, _, _, t, _, e, _, _, _ in ROUND2]
    ape = [abs(t - pt) / pt * 100 for _, _, _, t, _, _, _, pt, _ in ROUND2]
    print(f"wrote {path}")
    print(f"seed HV = {hv_seed:.4f}")
    print(f"BO HV (17 articles) = {hv_bo:.4f}  (+{(hv_bo/hv_seed-1)*100:.1f}%)")
    print(f"Sobol baseline HV   = {hv_bl:.4f}  (+{(hv_bl/hv_seed-1)*100:.1f}%)")
    print(f"pred-vs-meas t180 MAPE = {sum(ape)/len(ape):.2f}%  "
          f"(max {max(ape):.2f}%)")
    print("combined front:", pareto_front(seed_pts + r2_pts))


if __name__ == "__main__":
    main()
