"""Plot the round-5 leave-one-design-out CV (SI fig:si-logocv) and its metrics.

Reads the committed snapshots in manuscript/data/:
  t3-prism-bo-round5-logocv.csv               held-out predictions, one row per
                                              specimen and objective
  t3-prism-bo-round5-logocv-diagnostics.json  Ax compute_diagnostics output

Both come from the full-budget rerun (256 NUTS samples, 512 warmup steps per
fold, 35/35 folds) on branch claude/cv-signal-audit-20260922, commit 1e17c3e,
directory analysis/cv-signal-audit/data/full-nuts-rerun/. The earlier
64/128 run is kept as t3-prism-bo-round5-logocv-nuts64*.

Writes:
  figures/bo/t3-prism-bo-round5-logocv.png       two parity panels, no point
                                                 labels, no footer
  manuscript/data/t3-prism-bo-round5-logocv-stats.json
                                                 every number the manuscript
                                                 quotes about this CV

Spearman p-values are two-sided permutation p-values (20,000 shuffles of the
predictions, seed 0), with the asymptotic value alongside.

Usage:
    python scripts/figures/plot_logocv.py [--tag -nuts64]
"""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "manuscript" / "data"
FIG = ROOT / "figures" / "bo"

# Colours and ink match the campaign figures (bo/t3_prism_bo_campaign.py and
# bo/t3_prism_bo_diagnostics.py at bbf7a62), which were rendered in Lato.
INK = "#0b0b0b"
GRAY = "#83827d"
COLOR = {"t180": "#2a78d6", "e_reb_mJ": "#eb6834"}
TITLE = {
    "t180": r"$t_{180}$ (transmissibility)",
    "e_reb_mJ": r"$E_{\mathrm{reb}}$, mass-weighted rebound (mJ per drop)",
}
RC = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Lato", "Source Sans Pro", "Open Sans", "DejaVu Sans"],
    "mathtext.fontset": "custom",
    "mathtext.rm": "Lato",
    "mathtext.it": "Lato:italic",
    "font.size": 20,
    "xtick.labelsize": 19,
    "ytick.labelsize": 19,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.edgecolor": "#4a4a47",
    "axes.linewidth": 1.6,
    "xtick.major.size": 6,
    "ytick.major.size": 6,
    "xtick.major.width": 1.6,
    "ytick.major.width": 1.6,
}
N_PERM = 20000


def metrics(sub, diag, metric):
    o, p = sub.observed.to_numpy(), sub.predicted.to_numpy()
    rho, p_asym = stats.spearmanr(o, p)
    r, _ = stats.pearsonr(o, p)
    rng = np.random.default_rng(0)
    null = np.array([stats.spearmanr(o, rng.permutation(p))[0] for _ in range(N_PERM)])
    p_perm = (np.sum(np.abs(null) >= abs(rho)) + 1) / (N_PERM + 1)
    return {
        "n_specimens": int(len(o)),
        "MAPE": float(np.mean(np.abs((o - p) / o))),
        "MAPE_ax": float(diag["MAPE"][metric]),
        "spearman_rho": float(rho),
        "spearman_rho_ax": float(diag["Rank correlation"][metric]),
        "spearman_p_perm_two_sided": float(p_perm),
        "spearman_p_asymptotic": float(p_asym),
        "pearson_r": float(r),
        "pearson_r2": float(r * r),
        "coverage_1p96sd": float(np.mean(np.abs(o - p) <= 1.96 * sub.predicted_sem.to_numpy())),
        "sd_pred_over_sd_obs": float(np.std(p) / np.std(o)),
        "observed_range": [float(o.min()), float(o.max())],
    }


def plot(df, stats_by_metric, out):
    with plt.rc_context(RC):
        fig, axes = plt.subplots(1, 2, figsize=(13, 6.6), dpi=300)
        for ax, metric in zip(axes, ["t180", "e_reb_mJ"]):
            sub = df[df.metric == metric]
            lo = float(min(sub.observed.min(), sub.predicted.min()))
            hi = float(max(sub.observed.max(), sub.predicted.max()))
            pad = 0.18 * (hi - lo)
            lim = (lo - pad, hi + pad)
            ax.plot(lim, lim, color=GRAY, lw=1.6, ls=(0, (5, 5)), zorder=1)
            ax.errorbar(
                sub.observed, sub.predicted, xerr=sub.observed_sem, yerr=sub.predicted_sem,
                fmt="o", ms=10, mfc="none", mec=COLOR[metric], mew=2.0,
                ecolor=COLOR[metric], elinewidth=1.3, capsize=3.5, alpha=0.9, zorder=3,
            )
            ax.set_xlim(*lim)
            ax.set_ylim(*lim)
            ax.set_aspect("equal", adjustable="box")
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            ax.set_title(TITLE[metric], fontsize=19, pad=16)
            ax.set_xlabel("Measured", labelpad=10, fontsize=19)
            s = stats_by_metric[metric]
            ax.annotate(
                f"MAPE {100 * s['MAPE']:.1f}%   " + r"$\rho_s$" + f" = {s['spearman_rho']:+.2f}".replace("-", "\u2212"),
                xy=(0.97, 0.04), xycoords="axes fraction", fontsize=17,
                color=INK, va="bottom", ha="right",
            )
        axes[0].set_ylabel("Predicted", rotation=0, ha="left", va="bottom", fontsize=19)
        axes[0].yaxis.set_label_coords(-0.02, 1.02)
        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tag", default="", help='file-name tag, e.g. "-nuts64" for the 64/128 run')
    args = ap.parse_args(argv)
    df = pd.read_csv(DATA / f"t3-prism-bo-round5-logocv{args.tag}.csv")
    diag = json.loads((DATA / f"t3-prism-bo-round5-logocv{args.tag}-diagnostics.json").read_text())
    by_metric = {m: metrics(df[df.metric == m], diag, m) for m in ["t180", "e_reb_mJ"]}
    out_png = FIG / f"t3-prism-bo-round5-logocv{args.tag}.png"
    plot(df, by_metric, out_png)
    out_json = DATA / f"t3-prism-bo-round5-logocv{args.tag}-stats.json"
    out_json.write_text(json.dumps(by_metric, indent=2) + "\n")
    print(json.dumps(by_metric, indent=2))
    print(f"wrote {out_png.relative_to(ROOT)} and {out_json.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
