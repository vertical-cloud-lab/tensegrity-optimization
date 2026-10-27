#!/usr/bin/env python3
"""Batch-4 predictions against outcomes (fig:batch4-pred-vs-meas).

Draws the nine archived posterior-mean predictions for Ax trials 37 to 45
(manuscript/data/t3-prism-bo-round4-predictions.csv, saved when the batch
was recommended), an arrow from each to the measured value of the article
printed for that trial (round-4 print key, source_trial), and the 26
articles the batch-4 fit was trained on (seed, batch 2, batch-3 first
prints). No uncertainty bars or ellipses. Writes
figures/bo/t3-prism-bo-round4-predicted-vs-actual.{pdf,png}.

Usage:  python3 scripts/figures/build_batch4_pred_vs_meas_figure.py
"""
from __future__ import annotations

import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from campaign_data import (  # noqa: E402
    GRAY, INK, PRED_ORANGE, REPO, STYLE, load_articles, read_csv)


def main() -> int:
    articles = load_articles()
    training = [a for a in articles if a["batch"] <= 3]
    measured = {a["trial"]: a for a in articles if a["batch"] == 4}
    preds = {int(r["trial_index"]): r for r in read_csv("t3-prism-bo-round4-predictions.csv")}
    assert len(training) == 26, len(training)
    assert sorted(preds) == sorted(measured) == list(range(37, 46))

    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(5.6, 3.3))
        ax.scatter([a["t180"] for a in training], [a["e_reb_mJ"] for a in training],
                   s=22, facecolor="white", edgecolor=GRAY, linewidth=0.8, zorder=2)
        for trial in sorted(preds):
            p, m = preds[trial], measured[trial]
            px, py = float(p["pred_t180_mean"]), float(p["pred_e_reb_mJ_mean"])
            ax.annotate("", xy=(m["t180"], m["e_reb_mJ"]), xytext=(px, py),
                        arrowprops=dict(arrowstyle="-|>", color=PRED_ORANGE, lw=0.9,
                                        mutation_scale=7, shrinkA=2.5, shrinkB=3.5),
                        zorder=3)
            ax.scatter([px], [py], marker="D", s=20, facecolor=PRED_ORANGE,
                       edgecolor="none", zorder=4)
            ax.scatter([m["t180"]], [m["e_reb_mJ"]], s=24, facecolor=INK,
                       edgecolor=INK, linewidth=0.6, zorder=5)
        handles = [
            Line2D([], [], ls="none", marker="o", ms=4.6, mfc="white", mec=GRAY, mew=0.8,
                   label="Training set of the batch-4 fit (26 specimens)"),
            Line2D([], [], ls="none", marker="D", ms=4.2, mfc=PRED_ORANGE, mec="none",
                   label="Batch-4 prediction (posterior mean)"),
            Line2D([], [], color=PRED_ORANGE, lw=0.9, marker=">", ms=3.5,
                   markevery=[1], label="Prediction to measurement, same trial"),
            Line2D([], [], ls="none", marker="o", ms=4.8, mfc=INK, mec=INK,
                   label="Batch-4 measured (9 specimens)"),
        ]
        ax.set_xlabel(r"$t_{180}$, transmissibility")
        ax.set_ylabel(r"$E_{\mathrm{reb}}$, mass-weighted rebound (mJ per drop)")
        ax.set_xlim(0.78, 1.36)
        ax.set_ylim(3.0, 19.5)
        ax.legend(handles=handles, loc="upper right", frameon=False,
                  handlelength=2.2, borderaxespad=0.2)
        out = REPO / "figures" / "bo" / "t3-prism-bo-round4-predicted-vs-actual"
        for ext in ("pdf", "png"):
            fig.savefig(f"{out}.{ext}", bbox_inches="tight", pad_inches=0.02,
                        facecolor="white",
                        metadata={"CreationDate": None} if ext == "pdf" else None)
        plt.close(fig)
    for trial in sorted(preds):
        m = measured[trial]
        print(f"trial {trial}: {m['print_id']}  pred ({float(preds[trial]['pred_t180_mean']):.3f}, "
              f"{float(preds[trial]['pred_e_reb_mJ_mean']):.1f})  meas ({m['t180']:.3f}, {m['e_reb_mJ']:.1f})")
    print(f"wrote {out}.pdf and .png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
