"""Quantify how much of the LOGO-CV 'poor performance' is a data ceiling.

Reads the committed campaign snapshots only:
  manuscript/data/t3-prism-bo-round5-logocv.csv        (held-out predictions)
  manuscript/data/t3-prism-bo-round3-repeatability.csv (nine reprint pairs)

Prints (a) a recomputation of the LOGO-CV metrics, (b) calibration coverage
of the held-out posterior, (c) test-retest reliability of the reprint pairs,
including the reprint itself used as a "predictor" of its twin, and writes
figures/analysis/reprint-test-retest-ceiling.png.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
LOGO = ROOT / "manuscript/data/t3-prism-bo-round5-logocv.csv"
PAIRS = ROOT / "manuscript/data/t3-prism-bo-round3-repeatability.csv"
OUT = ROOT / "figures/analysis/reprint-test-retest-ceiling.png"

BLUE = "#1f77b4"   # t180, matching the campaign figures
ORANGE = "#e8590c"  # rebound, matching the campaign figures


def icc_oneway(x: np.ndarray, y: np.ndarray) -> float:
    """ICC(1,1) for k=2 repeats per group (one-way random effects)."""
    pairs = np.stack([x, y], axis=1)
    grand = pairs.mean()
    n, k = pairs.shape
    msb = k * ((pairs.mean(axis=1) - grand) ** 2).sum() / (n - 1)
    msw = ((pairs - pairs.mean(axis=1, keepdims=True)) ** 2).sum() / (n * (k - 1))
    return (msb - msw) / (msb + (k - 1) * msw)


def report_logo(df: pd.DataFrame, metric: str) -> None:
    d = df[df.metric == metric]
    obs, pred, psem = d.observed.values, d.predicted.values, d.predicted_sem.values
    mape = np.mean(np.abs(pred - obs) / np.abs(obs))
    pear = stats.pearsonr(obs, pred)
    spear = stats.spearmanr(obs, pred)
    cover68 = np.mean(np.abs(obs - pred) <= psem)
    cover95 = np.mean(np.abs(obs - pred) <= 1.96 * psem)
    print(f"\nLOGO-CV {metric} (n={len(d)})")
    print(f"  MAPE {100*mape:.1f}%  Pearson {pear.statistic:+.2f} (p={pear.pvalue:.2f})"
          f"  Spearman {spear.statistic:+.2f} (p={spear.pvalue:.2f})")
    print(f"  sd(predicted)/sd(observed) = {pred.std(ddof=1):.4f}/{obs.std(ddof=1):.4f}"
          f" = {pred.std(ddof=1)/obs.std(ddof=1):.2f}")
    print(f"  median held-out posterior sd {np.median(psem):.4f}"
          f"  vs marginal sd of data {obs.std(ddof=1):.4f}")
    print(f"  coverage: {100*cover68:.0f}% within 1 sd, {100*cover95:.0f}% within 1.96 sd")
    print(f"  median ingested within-session SEM {np.median(d.observed_sem):.5f}")


def report_pairs(p: pd.DataFrame, m: str, label: str) -> tuple[np.ndarray, np.ndarray]:
    x, y = p[f"{m}_1"].values, p[f"{m}_2"].values
    pear = stats.pearsonr(x, y)
    spear = stats.spearmanr(x, y)
    sig_print = np.std(y - x, ddof=1) / np.sqrt(2)
    icc = icc_oneway(x, y)
    # the reprint used as a point predictor of its twin, both directions
    rel_err = np.concatenate([np.abs(y - x) / np.abs(x), np.abs(x - y) / np.abs(y)])
    print(f"\nTest-retest {label} (9 reprint pairs)")
    print(f"  Pearson {pear.statistic:+.2f} (p={pear.pvalue:.2f})"
          f"  Spearman {spear.statistic:+.2f} (p={spear.pvalue:.2f})")
    print(f"  sigma_print {sig_print:.4f}   ICC(1,1) {icc:+.2f}"
          f"   ceiling sqrt(max(ICC,0)) = {np.sqrt(max(icc, 0)):.2f}")
    print(f"  reprint-as-predictor MAPE {100*rel_err.mean():.1f}%")
    return x, y


def main() -> None:
    logo = pd.read_csv(LOGO)
    pairs = pd.read_csv(PAIRS)

    for metric in ("t180", "e_reb_mJ"):
        report_logo(logo, metric)

    t = logo[logo.metric == "t180"]
    frac_cluster = np.mean((t.observed >= 0.95) & (t.observed <= 1.10))
    print(f"\nt180 concentration: {100*frac_cluster:.0f}% of the 44 articles lie in"
          f" [0.95, 1.10]; extremes: "
          + ", ".join(f"{r.print_id} {r.observed:.3f}"
                      for r in t[(t.observed < 0.95) | (t.observed > 1.10)].itertuples()))

    x_t, y_t = report_pairs(pairs, "t180", "t180")
    no7 = pairs[pairs.print_1 != "drran7"]
    sig_no7 = np.std(no7.t180_2 - no7.t180_1, ddof=1) / np.sqrt(2)
    print(f"  sigma_print excluding drran7 {sig_no7:.4f}")
    x_e, y_e = report_pairs(pairs, "e_reb_mJ", "rebound energy")

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.6))
    fig.suptitle("Print 1 vs print 2 of the same nine designs: the ceiling any surrogate faces",
                 fontsize=11.5, y=0.98)

    specs = [
        (axes[0], x_t, y_t, BLUE, "t180 (transmissibility)", "{:.2f}"),
        (axes[1], x_e, y_e, ORANGE, "Rebound energy (mJ per drop)", "{:.0f}"),
    ]
    for ax, x, y, color, title, _fmt in specs:
        lo = min(x.min(), y.min())
        hi = max(x.max(), y.max())
        pad = 0.08 * (hi - lo)
        lims = (lo - pad, hi + pad)
        ax.plot(lims, lims, ls="--", lw=1, color="0.6", zorder=1)
        ax.scatter(x, y, s=55, facecolors="none", edgecolors=color, lw=1.8, zorder=3)
        pear = stats.pearsonr(x, y).statistic
        spear = stats.spearmanr(x, y).statistic
        ax.text(0.97, 0.04, f"r = {pear:+.2f}   rank r = {spear:+.2f}",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=10,
                bbox=dict(facecolor="white", alpha=0.85, edgecolor="none", pad=1.5))
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Print 1 (drranN), measured")
        ax.grid(color="0.92", lw=0.7, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    axes[0].set_ylabel("Print 2 (2dranN), measured")

    i7 = list(pairs.print_1).index("drran7")
    axes[0].annotate("drran7: campaign max on print 1,\nmid-pack on print 2",
                     xy=(x_t[i7], y_t[i7]), xytext=(0.60, 0.30),
                     textcoords="axes fraction", fontsize=9, color="0.25",
                     arrowprops=dict(arrowstyle="-", color="0.55", lw=0.9))
    i1 = list(pairs.print_1).index("drran1")
    axes[1].annotate("drran1: 18.1 to 7.3 mJ\non reprint",
                     xy=(x_e[i1], y_e[i1]), xytext=(0.62, 0.72),
                     textcoords="axes fraction", fontsize=9, color="0.25",
                     arrowprops=dict(arrowstyle="-", color="0.55", lw=0.9))

    fig.text(0.5, 0.005,
             "Identical designs, re-printed and re-tested (dashed line: perfect reproducibility). "
             "A surrogate predicting a single print cannot beat this reliability.",
             ha="center", fontsize=9, color="0.35")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200)
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
