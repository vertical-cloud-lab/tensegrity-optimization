#!/usr/bin/env python3
"""Front evolution across the four measured batches (fig:front-evolution).

Recomputes the cumulative non-dominated front and the dominated
hypervolume at the (1.35, 15 mJ) reference after each batch from the
committed drop-results snapshots, checks the resulting table against
manuscript/data/t3-prism-bo-front-evolution.csv (exits non-zero on any
mismatch), and draws figures/bo/t3-prism-bo-front-evolution.{pdf,png}.

Usage:  python3 scripts/figures/build_front_evolution_figure.py
"""
from __future__ import annotations

import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from campaign_data import (  # noqa: E402
    FRONT_BLUES, GRAY, INK, REPO, STYLE, hypervolume, load_articles,
    pareto_mask, read_csv)

BATCH_NAMES = {1: "1 (Sobol)", 2: "2 (r2d2c)", 3: "3 (drran)", 4: "4 (corny)"}


def front_table(articles):
    rows, fronts, prev_members, prev_hv = [], [], set(), None
    for batch in (1, 2, 3, 4):
        cum = [a for a in articles if a["batch"] <= batch]
        t = [a["t180"] for a in cum]
        e = [a["e_reb_mJ"] for a in cum]
        keep = pareto_mask(t, e)
        members = sorted((a for a, k in zip(cum, keep) if k), key=lambda a: a["t180"])
        hv = hypervolume(t, e)
        ids = [a["print_id"] for a in members]
        rows.append({
            "after_batch": BATCH_NAMES[batch],
            "articles_cumulative": str(len(cum)),
            "hv_ref_1.35_15mJ": f"{hv:.3f}",
            "hv_gain_pct": "" if prev_hv is None else f"{100 * (hv - prev_hv) / prev_hv:.1f}",
            "best_t180": f"{min(t):.3f}",
            "min_e_reb_mJ": f"{round(min(e), 2):g}",
            "front": " ".join(ids),
            "entered": " ".join(sorted(set(ids) - prev_members)),
            "left": " ".join(sorted(prev_members - set(ids))),
        })
        fronts.append((batch, members, hv))
        prev_members, prev_hv = set(ids), hv
    return rows, fronts


def check_against_committed(rows) -> int:
    committed = read_csv("t3-prism-bo-front-evolution.csv")
    bad = 0
    for mine, ref in zip(rows, committed, strict=True):
        for col, val in ref.items():
            ok = (float(val) == float(mine[col])) if col in (
                "hv_ref_1.35_15mJ", "hv_gain_pct", "best_t180", "min_e_reb_mJ") and val else val == mine[col]
            if not ok:
                bad += 1
                print(f"MISMATCH {ref['after_batch']} {col}: committed {val!r}, recomputed {mine[col]!r}")
    print(f"front table vs t3-prism-bo-front-evolution.csv: {bad} mismatches")
    return bad


def main() -> int:
    articles = load_articles()
    rows, fronts = front_table(articles)
    bad = check_against_committed(rows)

    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(5.6, 3.3))
        ax.scatter([a["t180"] for a in articles], [a["e_reb_mJ"] for a in articles],
                   s=22, facecolor="white", edgecolor=GRAY, linewidth=0.8, zorder=2)
        handles = [Line2D([], [], ls="none", marker="o", ms=4.6, mfc="white",
                          mec=GRAY, mew=0.8, label="Measured specimen (35)")]
        for (batch, members, hv), color in zip(fronts, FRONT_BLUES):
            xs = [a["t180"] for a in members]
            ys = [a["e_reb_mJ"] for a in members]
            ax.plot(xs, ys, "-", color=color, lw=1.8, zorder=3, solid_capstyle="round")
            ax.scatter(xs, ys, s=22, facecolor=color, edgecolor=INK, linewidth=0.6, zorder=4)
            handles.append(Line2D([], [], color=color, lw=1.8, marker="o", ms=4.6,
                                  mfc=color, mec=INK, mew=0.6,
                                  label=f"Front after batch {batch} (HV {hv:.2f})"))
        ax.set_xlabel(r"$t_{180}$")
        ax.set_ylabel(r"$E_{\mathrm{reb}}$ (mJ per drop)")
        ax.set_xlim(0.78, 1.36)
        ax.set_ylim(3.0, 19.5)
        ax.legend(handles=handles, loc="upper right", frameon=False,
                  handlelength=2.2, borderaxespad=0.2)
        out = REPO / "figures" / "bo" / "t3-prism-bo-front-evolution"
        for ext in ("pdf", "png"):
            fig.savefig(f"{out}.{ext}", bbox_inches="tight", pad_inches=0.02,
                        facecolor="white")
        plt.close(fig)
    print(f"wrote {out}.pdf and .png")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
