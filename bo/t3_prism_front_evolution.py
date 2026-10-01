#!/usr/bin/env python3
"""Pareto-front evolution across the four measured batches.

Recomputes, from the committed drop-results CSVs only, the cumulative
Pareto front after each physical batch (round 1 Sobol, round 2 r2d2c,
round 3 drran, round 4 corny) and the dominated hypervolume at the
standing reference point (t180 = 1.35, rebound = 15 mJ; the reference
every hypervolume number quoted on PR #102 uses). Writes

  bo/t3-prism-bo-front-evolution.csv        per-round table (HV, front
                                            membership, entrants, exits)
  bo/figures/t3-prism-bo-front-evolution.png one panel: all tested
                                            articles + the four fronts

Needs only pandas + matplotlib (reuses the campaign script's loaders,
which read the committed CSVs; no Ax, no refit).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

BO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BO_DIR))

from t3_prism_bo_campaign import (  # noqa: E402
    ARROW_DOWN, BO_DIR, FIG_RC, FIGURE_DPI, FRONT_BLUE, INK, LABEL_GRAY,
    load_round2_training_data, load_round3_training_data,
    load_round4_training_data, load_training_data, obj1_name, obj2_name,
    observed_frame,
)

# The reference point used for every HV number quoted on the PR thread.
HV_REF = (1.35, 15.0)

# One color per cumulative front, palest first (matplotlib Blues family
# around the repo's FRONT_BLUE so the newest front reads strongest).
FRONT_COLORS = ["#c3d7f0", "#8fb6e4", "#5b93da", FRONT_BLUE]


def pareto_mask(t: np.ndarray, e: np.ndarray) -> np.ndarray:
    """Non-dominated mask for joint minimization of (t, e)."""
    n = len(t)
    keep = np.ones(n, dtype=bool)
    for i in range(n):
        dominated = (t <= t[i]) & (e <= e[i]) & ((t < t[i]) | (e < e[i]))
        if dominated.any():
            keep[i] = False
    return keep


def hypervolume(t: np.ndarray, e: np.ndarray, ref=HV_REF) -> float:
    """Dominated hypervolume of the front of (t, e) under minimization."""
    keep = pareto_mask(t, e)
    pts = sorted(zip(t[keep], e[keep]))
    hv, prev_t = 0.0, None
    # staircase: walk the front left to right; each point owns the strip
    # from its t to the next point's t at its own rebound level
    for i, (ti, ei) in enumerate(pts):
        if ti >= ref[0] or ei >= ref[1]:
            continue
        nxt = min(ref[0], pts[i + 1][0]) if i + 1 < len(pts) else ref[0]
        hv += max(0.0, nxt - ti) * (ref[1] - ei)
        prev_t = ti
    return hv


def main() -> int:
    _, y1, l1, *_ = load_training_data(
        BO_DIR / "t3-prism-bo-batch-drop-results.csv",
        BO_DIR / "t3-prism-bo-batch.csv")
    _, y2, l2, *_ = load_round2_training_data()
    _, y3, l3, *_ = load_round3_training_data()
    _, y4, l4, *_ = load_round4_training_data()
    rounds = [("1 (Sobol)", y1, l1), ("2 (r2d2c)", y2, l2),
              ("3 (drran)", y3, l3), ("4 (corny)", y4, l4)]

    rows, fronts, prev_members, prev_hv = [], [], set(), None
    y_cum, l_cum = [], []
    for name, y, l in rounds:
        y_cum, l_cum = y_cum + y, l_cum + l
        frame = observed_frame(y_cum, l_cum)
        t = frame[obj1_name].to_numpy()
        e = frame[obj2_name].to_numpy()
        keep = pareto_mask(t, e)
        members = frame.loc[keep].sort_values(obj1_name)
        hv = hypervolume(t, e)
        member_ids = members["print_id"].tolist()
        rows.append({
            "after_batch": name,
            "articles_cumulative": len(frame),
            "hv_ref_1.35_15mJ": round(hv, 3),
            "hv_gain_pct": (None if prev_hv is None
                            else round(100 * (hv - prev_hv) / prev_hv, 1)),
            "best_t180": round(float(t.min()), 3),
            "min_e_reb_mJ": round(float(e.min()), 2),
            "front": " ".join(member_ids),
            "entered": " ".join(sorted(set(member_ids) - prev_members)),
            "left": " ".join(sorted(prev_members - set(member_ids))),
        })
        fronts.append((name, members, hv))
        prev_members, prev_hv = set(member_ids), hv

    table = pd.DataFrame(rows)
    out_csv = BO_DIR / "t3-prism-bo-front-evolution.csv"
    table.to_csv(out_csv, index=False)
    print(table.drop(columns=["front"]).to_string(index=False))
    print(f"\nTable written to {out_csv}")

    # ---- figure ---------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with plt.rc_context(FIG_RC):
        fig, ax = plt.subplots(figsize=(11, 7), dpi=FIGURE_DPI)
        frame_all = observed_frame(y_cum, l_cum)
        ax.scatter(frame_all[obj1_name], frame_all[obj2_name], s=110,
                   facecolor="white", edgecolor=LABEL_GRAY, linewidth=1.6,
                   zorder=2)
        for (name, members, hv), color in zip(fronts, FRONT_COLORS):
            ax.plot(members[obj1_name], members[obj2_name], "-", color=color,
                    linewidth=4.0, zorder=3, solid_capstyle="round")
            ax.scatter(members[obj1_name], members[obj2_name], s=110,
                       facecolor=color, edgecolor=INK, linewidth=1.4,
                       zorder=4)
        # swatch legend in the empty upper-right corner: a leader line per
        # front would cross the data (three fronts share their left end)
        for i, ((name, members, hv), color) in enumerate(
                zip(fronts, FRONT_COLORS)):
            y_pos = 0.97 - i * 0.075
            ax.plot([0.66, 0.72], [y_pos, y_pos], transform=ax.transAxes,
                    color=color, linewidth=6, solid_capstyle="round",
                    clip_on=False, zorder=5)
            ax.text(0.745, y_pos,
                    f"after batch {name.split(' ')[0]}   HV {hv:.2f}",
                    transform=ax.transAxes, fontsize=17, color=INK,
                    ha="left", va="center", zorder=5)
        ax.set_xlabel(f"Shock transmissibility t180 ({ARROW_DOWN} is better)")
        ax.set_ylabel("Rebound energy to payload /\n(mJ per drop, "
                      f"{ARROW_DOWN} is better)", rotation=0, ha="left",
                      va="bottom")
        ax.yaxis.set_label_coords(-0.035, 1.04)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines["left"].set_position(("outward", 14))
        ax.spines["bottom"].set_position(("outward", 14))
        fig.subplots_adjust(left=0.11, right=0.97, top=0.86, bottom=0.13)
        out_png = BO_DIR / "figures" / "t3-prism-bo-front-evolution.png"
        fig.savefig(out_png, dpi=FIGURE_DPI, facecolor="white")
        plt.close(fig)
    print(f"Figure saved to {out_png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
