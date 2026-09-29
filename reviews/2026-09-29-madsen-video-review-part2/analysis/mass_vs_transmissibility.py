"""Transmissibility and velocity loss index against weighed printed mass, one point per article.

Answers the 2026-09-29 video request (item 7 of the part-2 review): "a graph charting
the performance and transmissibility for each structure over its printed mass ... the
lowest starting printing mass ... at the very left ... track transmissibility as the
y value".

Inputs are the committed snapshots in manuscript/data/ (44 drop-tested articles):
the per-article covariate table (weighed mass, t180) and the five drop-result files
(rebound fraction e_reb). The velocity loss index is VLI = 1 - e_reb, where the
pipeline's e_reb = g * t_second / (2 * dv) is the ratio of the top vertex's ballistic
hop speed to the base-plate velocity change (checked against the drop files to 5e-5).

Run from the repository root:
    python reviews/2026-09-29-madsen-video-review-part2/analysis/mass_vs_transmissibility.py
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "manuscript" / "data"
OUT = Path(__file__).resolve().parent
TARGET_G = 20.23  # constant printed-mass target from batch 3 on
G = 9.80665

DROP_FILES = {
    "seed": "t3-prism-bo-batch-drop-results.csv",
    "batch 2": "t3-prism-bo-round1-drop-results.csv",
    "batch 3": "t3-prism-bo-round3-drop-results.csv",
    "batch 3 reprint": "t3-prism-bo-round3-reprint-drop-results.csv",
    "batch 4": "t3-prism-bo-round4-drop-results.csv",
}


def load() -> pd.DataFrame:
    drops = []
    for batch, name in DROP_FILES.items():
        d = pd.read_csv(DATA / name)
        d["batch"] = batch
        drops.append(d)
    drops = pd.concat(drops, ignore_index=True)
    check = G * drops.t_second_ms_mean / 1000 / (2 * drops.in_dv_ms_mean)
    assert (drops.e_rebound_mean - check).abs().max() < 1e-3, "e_reb formula changed"
    cov = pd.read_csv(DATA / "t3-prism-article-print-covariates.csv")
    art = cov.merge(drops[["specimen", "batch", "e_rebound_mean", "t180_sd", "n_valid"]],
                    left_on="print_id", right_on="specimen", how="inner")
    art["mass_g"] = art["mass_g_with_label"]
    art["vli"] = 1.0 - art["e_rebound_mean"]
    art["regime"] = np.where(art.batch.isin(["seed", "batch 2"]),
                             "Batches 1 and 2: constant solid CAD mass",
                             "Batches 3 and 4: constant printed mass (20.23 g target)")
    return art


def corr(x, y):
    r, p = stats.pearsonr(x, y)
    rho, prho = stats.spearmanr(x, y)
    return dict(n=int(len(x)), pearson_r=round(float(r), 3), r2=round(float(r * r), 3),
                pearson_p=round(float(p), 4), spearman_rho=round(float(rho), 3),
                spearman_p=round(float(prho), 4))


def main():
    art = load()
    summary = {"n_articles": int(len(art)),
               "lightest_article": {"id": art.loc[art.mass_g.idxmin(), "print_id"],
                                    "mass_g": float(art.mass_g.min())},
               "heaviest_article": {"id": art.loc[art.mass_g.idxmax(), "print_id"],
                                    "mass_g": float(art.mass_g.max())},
               "vli_range": [round(float(art.vli.min()), 4), round(float(art.vli.max()), 4)],
               "all": {"t180": corr(art.mass_g, art.t180_obs), "vli": corr(art.mass_g, art.vli)},
               "by_regime": {}, "by_batch": {}}
    for reg, sub in art.groupby("regime"):
        summary["by_regime"][reg] = {"t180": corr(sub.mass_g, sub.t180_obs),
                                     "vli": corr(sub.mass_g, sub.vli)}
    for b, sub in art.groupby("batch"):
        summary["by_batch"][b] = {
            "n": int(len(sub)),
            "mass_mean_g": round(float(sub.mass_g.mean()), 3),
            "mass_sd_g": round(float(sub.mass_g.std(ddof=1)), 3),
            "mass_cv_pct": round(float(100 * sub.mass_g.std(ddof=1) / sub.mass_g.mean()), 2),
            "mass_min_g": float(sub.mass_g.min()), "mass_max_g": float(sub.mass_g.max()),
            "mean_offset_from_20.23_g": round(float(sub.mass_g.mean() - TARGET_G), 3),
            "mean_offset_from_20.23_pct": round(float(100 * (sub.mass_g.mean() - TARGET_G) / TARGET_G), 2),
            "n_below_target": int((sub.mass_g < TARGET_G).sum()),
            "t180": corr(sub.mass_g, sub.t180_obs) if len(sub) > 2 else None,
        }
        if sub.pred_printed_mass_g.notna().all():
            off = sub.mass_g - sub.pred_printed_mass_g
            summary["by_batch"][b]["mean_offset_from_model_prediction_g"] = round(float(off.mean()), 3)
    (OUT / "mass-vs-transmissibility-summary.json").write_text(json.dumps(summary, indent=1))
    art[["print_id", "batch", "mass_g", "pred_printed_mass_g", "t180_obs", "t180_sd", "e_rebound_mean",
         "vli", "ereb_obs", "n_valid"]].sort_values("mass_g").to_csv(
        OUT / "mass-vs-transmissibility-articles.csv", index=False, float_format="%.5g")

    # ---- figure: two panels, one y-scale each, shared x (weighed printed mass) ----
    colors = {"Batches 1 and 2: constant solid CAD mass": "#2a78d6",
              "Batches 3 and 4: constant printed mass (20.23 g target)": "#eb6834"}
    markers = {"seed": "o", "batch 2": "s", "batch 3": "^", "batch 3 reprint": "v", "batch 4": "D"}
    ink, muted, grid = "#0b0b0b", "#52514e", "#e4e3df"
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": muted, "axes.labelcolor": ink,
                         "xtick.color": muted, "ytick.color": muted})
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.4), sharex=True)
    xmin = art.mass_g.min()
    for ax, col, ylab in [(axes[0], "t180_obs", "Transmissibility $t_{180}$ (lower is better)"),
                          (axes[1], "vli", "Velocity loss index, $1 - e_{\\mathrm{reb}}$ (higher is better)")]:
        ax.axvline(TARGET_G, color=muted, lw=1, ls=(0, (4, 3)), zorder=1)
        if col == "t180_obs":
            ax.axhline(1.0, color=muted, lw=1, zorder=1)
            ax.text(23.55, 1.0, "no attenuation", va="bottom", ha="right", color=muted, fontsize=8.5)
        for b in markers:
            s2 = art[art.batch == b]
            reg = s2.regime.iloc[0]
            if True:
                ax.scatter(s2.mass_g, s2[col], s=46, marker=markers[b], color=colors[reg],
                           edgecolor="#fcfcfb", linewidth=1.2, zorder=3,
                           label=(f"{b} (" + ("constant solid mass" if reg.startswith("Batches 1") else "constant printed mass") + ")") if ax is axes[0] else None)
        ax.set_ylabel(ylab)
        ax.grid(True, color=grid, lw=0.8, zorder=0)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.set_xlim(xmin - 0.1, art.mass_g.max() + 0.15)
        ax.set_xlabel(f"Weighed printed mass (g); left edge = lightest article ({xmin:.2f} g)")
        key = "t180" if col == "t180_obs" else "vli"
        s = summary["all"][key]
        lines = [f"All 44: r = {s['pearson_r']:+.2f} (r$^2$ = {s['r2']:.2f}), Spearman $\\rho$ = {s['spearman_rho']:+.2f}"]
        for reg in colors:
            s = summary["by_regime"][reg][key]
            short = "Batches 1, 2" if reg.startswith("Batches 1") else "Batches 3, 4"
            lines.append(f"{short} (n = {s['n']}): r = {s['pearson_r']:+.2f}, $\\rho$ = {s['spearman_rho']:+.2f}")
        b4 = summary["by_batch"]["batch 4"]["t180"] if key == "t180" else None
        if b4:
            lines.append(f"Batch 4 alone: r = {b4['pearson_r']:+.2f} (two design families)")
        pos = (0.98, 0.03, "bottom")
        ax.text(pos[0], pos[1], "\n".join(lines), transform=ax.transAxes, ha="right", va=pos[2],
                fontsize=8.3, color=ink, linespacing=1.5,
                bbox=dict(boxstyle="round,pad=0.4", fc="#fcfcfb", ec=grid, lw=0.8))
    for ax in axes:
        ax.text(TARGET_G + 0.05, ax.get_ylim()[1], "20.23 g target (batches 3, 4)",
                color=muted, fontsize=8, va="top")
    for pid, dx, dy in [("corny7", 0.08, -0.012), ("6lhxfy", 0.08, -0.004), ("drran7", 0.08, 0.0),
                        ("r2d2c3", 0.08, -0.004)]:
        row = art[art.print_id == pid]
        if len(row):
            axes[0].annotate(pid, (row.mass_g.iloc[0], row.t180_obs.iloc[0]),
                             xytext=(row.mass_g.iloc[0] + dx, row.t180_obs.iloc[0] + dy),
                             fontsize=8, color=muted, va="center")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=9,
               bbox_to_anchor=(0.5, -0.01), title="Marker = physical batch; color = mass-control regime (blue: batches 1, 2 held solid CAD mass; orange: batches 3, 4 held printed mass at 20.23 g)",
               title_fontsize=9)
    fig.suptitle("Per-article transmissibility and velocity loss index against weighed printed mass "
                 "(44 drop-tested articles)", fontsize=11.5, color=ink, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.14, 1, 0.95))
    fig.savefig(OUT / "mass-vs-transmissibility.png", dpi=170, facecolor="#fcfcfb")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
