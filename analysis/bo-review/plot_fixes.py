"""Held-out parity plots and feature importances of the surrogate with the review's fixes applied.

PR #121 (sgbaird, 2026-11-25): "I want to see the updated LOGO-CV parity plots
where the fixes have been applied, perhaps rendered and hosted on GitHub html
preview or something like that with plotly. Same with feature importance.
Something that could potentially go into the paper to show that the model is
learning something."

Which of the review's fixes reach the surrogate:

* item 1, the noise model: noise learned (no ``train_Yvar``) or
  replicate-based SEMs (``SEM^2 + s_print^2``) instead of the SEMs as fixed
  noise;
* item 4, the filament settings: the four batch-level settings dropped
  ("eight" inputs).

Items 2 (objective thresholds, pinned qLogNEHVI) and 3 (filament point fixed
before the acquisition) change only the acquisition. The surrogate and its
held-out predictions do not depend on them.

Inputs (all committed; nothing is refitted here):

* ``manuscript/data/t3-prism-bo-round5-logocv.csv``: the campaign's SAASBO
  (Ax 0.5.0, NUTS 512/256, SEMs as fixed noise), the run of SI fig:si-logocv;
* ``analysis/logocv-baselines/data/ax-saasbo-inferred-noise-twelve/``: the same
  Ax SAASBO, folds, seeds and NUTS budget with the SEMs blanked (noise learned);
* ``analysis/bo-review/data/logocv/saas-{fixed,learned,replicate}-twelve/`` and
  ``saas-learned-eight/``: BoTorch 0.18.1 SAAS (NumPyro, NUTS 512/256) from
  ``logocv_noise_models.py``;
* ``analysis/logocv-baselines/data/baselines/{mean,rf}-twelve.csv``: the
  training-mean predictor and the tuned random forest, for reference;
* ``analysis/bo-review/data/importances/all-{twelve,eight}-{fixed,learned}-512w256-s{0..3}.json``:
  SAAS fits to all 44 articles, four NUTS seeds at the campaign budget
  (``importances_stability.py``).

Outputs (``analysis/bo-review/figures/``):

* ``index.html``: the interactive page: scorecard, parity plots,
  importances, length scales, flatness. It loads ``plotly-<version>.min.js``
  (MIT, vendored next to it) by relative path, so it works opened locally,
  through htmlpreview.github.io and through raw.githack.com;
* ``logocv-parity-noise.{png,pdf}``: the paper candidate, campaign surrogate
  (top) against the same SAASBO with the noise learned (bottom);
* ``logocv-parity-other-fixes.{png,pdf}``: replicate-based SEMs and the
  eight-input model;
* ``feature-importance-noise.{png,pdf}``: importances and raw length scales of
  the twelve-input fit to all 44 articles, SEMs as fixed noise against noise
  learned;
* ``scorecard.{csv,json}``: every number on the page.

Usage::

    python analysis/bo-review/plot_fixes.py
"""

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
ROOT = HERE.parents[1]
BASE = HERE.parent / "logocv-baselines"
IMP = HERE / "data" / "importances"
OUT = HERE / "figures"
METRICS = ("t180", "e_reb_mJ")
N_PERM = 20000

# Ink and objective colours of the campaign figures (scripts/figures/plot_logocv.py)
INK = "#0b0b0b"
GRAY = "#83827d"
COLOR = {"t180": "#2a78d6", "e_reb_mJ": "#eb6834"}
TITLE = {"t180": "t180 (transmissibility)",
         "e_reb_mJ": "E_reb, mass-weighted rebound (mJ per drop)"}
TITLE_TEX = {"t180": r"$t_{180}$ (transmissibility)",
             "e_reb_mJ": r"$E_{\mathrm{reb}}$, mass-weighted rebound (mJ per drop)"}
TITLE_HTML = {"t180": "t<sub>180</sub> (transmissibility)",
              "e_reb_mJ": "E<sub>reb</sub>, mass-weighted rebound (mJ per drop)"}
FMT = {"t180": ".4f", "e_reb_mJ": ".2f"}
OBJ_HTML = {"t180": "t<sub>180</sub>", "e_reb_mJ": "E<sub>reb</sub> (mJ)"}
SESSION = {"seed": "batch 1 (seed)", "r2d2c": "batch 2", "drran": "batch 3, first print",
           "2dran": "batch 3, reprint", "corny": "batch 4"}
PARAM = {
    "R_mm": ("Base radius R", "mm"), "H_mm": ("Cell height H", "mm"),
    "twist_deg": ("Twist angle θ", "deg"), "strut_d_mm": ("Strut diameter d_s", "mm"),
    "cable_d_mm": ("Cable diameter d_t", "mm"), "mass_printed_g": ("Printed mass m", "g"),
    "strut_infill_pct": ("Strut infill", "%"), "tpu_infill_pct": ("Tendon infill", "%"),
    "pla_nozzle_temp_C": ("PLA nozzle temp.", "°C"),
    "pla_flow_mm3_s": ("PLA vol. speed", "mm³/s"),
    "tpu_nozzle_temp_C": ("TPU nozzle temp.", "°C"),
    "tpu_flow_mm3_s": ("TPU vol. speed", "mm³/s"),
}
TWELVE = list(PARAM)
PARAM_HTML = {
    "R_mm": "Base radius <i>R</i> (mm)", "H_mm": "Cell height <i>H</i> (mm)",
    "twist_deg": "Twist angle <i>\u03b8</i> (deg)", "strut_d_mm": "Strut diameter <i>d</i><sub>s</sub> (mm)",
    "cable_d_mm": "Cable diameter <i>d</i><sub>t</sub> (mm)", "mass_printed_g": "Printed mass <i>m</i> (g)",
    "strut_infill_pct": "Strut infill (%)", "tpu_infill_pct": "Tendon infill (%)",
    "pla_nozzle_temp_C": "PLA nozzle temp. (\u00b0C)", "pla_flow_mm3_s": "PLA vol. speed (mm\u00b3/s)",
    "tpu_nozzle_temp_C": "TPU nozzle temp. (\u00b0C)", "tpu_flow_mm3_s": "TPU vol. speed (mm\u00b3/s)",
}
PARAM_TEX = {
    "R_mm": r"Base radius $R$ (mm)", "H_mm": r"Cell height $H$ (mm)",
    "twist_deg": r"Twist angle $\theta$ (deg)", "strut_d_mm": r"Strut diameter $d_s$ (mm)",
    "cable_d_mm": r"Cable diameter $d_t$ (mm)", "mass_printed_g": r"Printed mass $m$ (g)",
    "strut_infill_pct": r"Strut infill (%)", "tpu_infill_pct": r"Tendon infill (%)",
    "pla_nozzle_temp_C": "PLA nozzle temp. (\u00b0C)", "pla_flow_mm3_s": r"PLA vol. speed (mm$^3$/s)",
    "tpu_nozzle_temp_C": "TPU nozzle temp. (\u00b0C)", "tpu_flow_mm3_s": r"TPU vol. speed (mm$^3$/s)",
}
EIGHT = TWELVE[:8]
RC = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Lato", "Source Sans Pro", "Open Sans", "DejaVu Sans"],
    "mathtext.fontset": "custom", "mathtext.rm": "Lato", "mathtext.it": "Lato:italic",
    "font.size": 17, "xtick.labelsize": 15, "ytick.labelsize": 15,
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.edgecolor": "#4a4a47", "axes.linewidth": 1.4,
    "xtick.major.size": 5, "ytick.major.size": 5,
    "xtick.major.width": 1.4, "ytick.major.width": 1.4,
}

# LOGO-CV runs. All share the 35 design folds (reprint twins held out
# together), the 44 articles and observed values, and the campaign's input
# bounds; see analysis/logocv-baselines/README.md.
RUNS = [
    dict(key="campaign", noise="SEMs as fixed noise", fix="none (campaign)",
         label="Campaign surrogate: SEMs as fixed noise",
         model="SAASBO, Ax 0.5.0, NUTS 512/256", space="twelve",
         path=ROOT / "manuscript/data/t3-prism-bo-round5-logocv.csv",
         note="The run of SI fig:si-logocv."),
    dict(key="learned", noise="noise learned", fix="1 (noise learned)",
         label="Fix 1: noise learned",
         model="SAASBO, Ax 0.5.0, NUTS 512/256", space="twelve",
         path=BASE / "data/ax-saasbo-inferred-noise-twelve/t3-prism-bo-round5-logocv.csv",
         note="The campaign's Ax code path, folds, seeds and NUTS budget; only the SEMs are blanked."),
    dict(key="replicate", noise="replicate-based SEMs", fix="1 (replicate-based SEMs)",
         label="Fix 1, alternative: replicate-based SEMs",
         model="SAAS, BoTorch 0.18.1 (NumPyro), NUTS 512/256", space="twelve",
         path=HERE / "data/logocv/saas-replicate-twelve/logocv.csv",
         note="train_Yvar = SEM² + s_print², s_print pooled over the reprint twins of the training fold."),
    dict(key="learned-eight", noise="noise learned", fix="1 + 4 (noise learned, filament settings dropped)",
         label="Fixes 1 and 4: noise learned, filament settings dropped",
         model="SAAS, BoTorch 0.18.1 (NumPyro), NUTS 512/256", space="eight",
         path=HERE / "data/logocv/saas-learned-eight/logocv.csv",
         note="Eight inputs: the five shape coordinates, printed mass and the two infill densities."),
    dict(key="learned-botorch", noise="noise learned", fix="1 (noise learned)",
         label="Fix 1 in the BoTorch 0.18 driver (check)",
         model="SAAS, BoTorch 0.18.1 (NumPyro), NUTS 512/256", space="twelve",
         path=HERE / "data/logocv/saas-learned-twelve/logocv.csv",
         note="Same driver as the replicate and eight-input runs: shows the driver does not matter."),
    dict(key="fixed-botorch", noise="SEMs as fixed noise", fix="none (campaign)",
         label="Campaign noise model in the BoTorch 0.18 driver (check)",
         model="SAAS, BoTorch 0.18.1 (NumPyro), NUTS 512/256", space="twelve",
         path=HERE / "data/logocv/saas-fixed-twelve/logocv.csv",
         note="Reproduces the campaign run in the faster driver."),
    dict(key="rf", noise="n/a", fix="reference",
         label="Reference: tuned random forest",
         model="scikit-learn, inner GroupKFold tuning", space="twelve",
         path=BASE / "data/baselines/rf-twelve.csv",
         note="Point predictions; bars are the inner-CV RMSE."),
    dict(key="mean", noise="n/a", fix="reference",
         label="Reference: training mean",
         model="mean of the training fold", space="none",
         path=BASE / "data/baselines/mean-twelve.csv",
         note="R2_oos = 0 by construction; its rank correlation is a leave-out artefact."),
]
RUN = {r["key"]: r for r in RUNS}


# ----------------------------------------------------------------------------- data
def load_table():
    t = pd.read_csv(BASE / "data" / "article-features.csv")
    assert len(t) == 44 and t.print_id.is_unique
    twins = t.groupby("design").print_id.apply(list).to_dict()
    t["twin"] = [", ".join(p for p in twins[d] if p != pid) for d, pid in zip(t.design, t.print_id)]
    t["session_label"] = t.session.map(SESSION)
    return t


def load_run(run, t):
    df = pd.read_csv(run["path"])
    out = {}
    for metric in METRICS:
        d = df[df.metric == metric].set_index("print_id").loc[t.print_id]
        obs = t[f"{metric}_obs"].to_numpy()
        assert np.allclose(d.observed.to_numpy(), obs, rtol=1e-4, atol=1e-6), run["key"]
        out[metric] = pd.DataFrame({
            "print_id": t.print_id.to_numpy(), "observed": obs,
            "observed_sem": t[f"{metric}_sem"].to_numpy(),
            "predicted": d.predicted.to_numpy(), "predicted_sd": d.predicted_sem.to_numpy(),
        })
    return out


def permutation_p(f, y, n=N_PERM, seed=0):
    """Spearman's rho and its two-sided permutation p, computed as in
    scripts/figures/plot_logocv.py (20,000 shuffles of the predictions, seed 0,
    p = (count + 1) / (n + 1)), so the campaign row matches the manuscript."""
    rho = stats.spearmanr(y, f).statistic
    rng = np.random.default_rng(seed)
    yr, fr = stats.rankdata(y), stats.rankdata(f)
    yc = yr - yr.mean()
    null = np.empty(n)
    for i in range(n):
        fpm = rng.permutation(fr)
        fc = fpm - fpm.mean()
        null[i] = yc @ fc / np.sqrt((yc ** 2).sum() * (fc ** 2).sum())
    return float(rho), float((np.sum(np.abs(null) >= abs(rho)) + 1) / (n + 1))


def score(d, t, metric):
    y, f, s = d.observed.to_numpy(), d.predicted.to_numpy(), d.predicted_sd.to_numpy()
    base = np.array([t.loc[t.design != g, f"{metric}_obs"].mean() for g in t.design])
    rho, p = permutation_p(f, y)
    return {
        "spearman_rho": rho, "perm_p": p,
        "R2_oos": float(1 - ((y - f) ** 2).sum() / ((y - base) ** 2).sum()),
        "MAPE_pct": float(100 * np.mean(np.abs(f - y) / np.abs(y))),
        "RMSE": float(np.sqrt(np.mean((f - y) ** 2))),
        "pearson_r": float(stats.pearsonr(f, y).statistic),
        "coverage_1.96sd_pct": float(100 * np.mean(np.abs(y - f) <= 1.96 * s)),
        "pred_sd_over_obs_sd": float(np.std(f, ddof=1) / np.std(y, ddof=1)),
    }


def load_importances(dataset, noise, budget="512w256"):
    paths = sorted(IMP.glob(f"{dataset}-{noise}-{budget}-s*.json"))
    assert len(paths) == 4, (dataset, noise, [p.name for p in paths])
    recs = [json.loads(p.read_text()) for p in paths]
    cols = recs[0]["columns"]
    out = {"columns": cols, "seeds": [r["seed"] for r in recs], "n": recs[0]["n"]}
    for metric in METRICS:
        per_seed = [np.array(r["metrics"][metric]["lengthscale_draws"]) for r in recs]
        ls = np.concatenate(per_seed)
        inv = 1 / ls
        share = inv / inv.sum(axis=1, keepdims=True)
        seed_med = np.array([np.median(x, axis=0) for x in per_seed])
        seed_ax = (1 / seed_med) / (1 / seed_med).sum(axis=1, keepdims=True)
        pooled_ax = 1 / np.median(ls, axis=0)
        f = [r["metrics"][metric] for r in recs]
        out[metric] = {
            "n_draws": int(ls.shape[0]),
            "share_median": np.median(share, axis=0), "share_q25": np.percentile(share, 25, axis=0),
            "share_q75": np.percentile(share, 75, axis=0),
            "ax_importance_pooled": pooled_ax / pooled_ax.sum(), "ax_importance_by_seed": seed_ax,
            "ls_median": np.median(ls, axis=0), "ls_q25": np.percentile(ls, 25, axis=0),
            "ls_q75": np.percentile(ls, 75, axis=0), "ls_median_by_seed": seed_med,
            "flat_sd": np.array([x["posterior_mean_sd_over_space"] for x in f]),
            "y_std": f[0]["y_std"],
            "noise_sd": (np.array([np.sqrt(np.median(x["noise_draws"])) * x["y_std"] for x in f])
                         if "noise_draws" in f[0] else None),
            "top_by_seed": [cols[int(np.argmax(v))] for v in seed_ax],
        }
    return out


# ----------------------------------------------------------------------------- text helpers
def fnum(v, nd=2, plus=True):
    s = f"{v:+.{nd}f}" if plus else f"{v:.{nd}f}"
    return s.replace("-", "−")


def fp(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def stat_lines(s):
    return (f"ρ_s = {fnum(s['spearman_rho'])} ({fp(s['perm_p'])})",
            f"R²_oos = {fnum(s['R2_oos'])}, MAPE {s['MAPE_pct']:.1f}%")


def pct(r):
    return "< 0.1%" if r < 0.001 else (f"{100 * r:.1f}%" if r < 0.1 else f"{100 * r:.0f}%")


def lims(frames):
    lo = min(min(d.observed.min(), d.predicted.min()) for d in frames)
    hi = max(max(d.observed.max(), d.predicted.max()) for d in frames)
    pad = 0.08 * (hi - lo)
    return lo - pad, hi + pad


# ----------------------------------------------------------------------------- static figures
def parity_png(rows, data, sc, out_stem, row_titles):
    with plt.rc_context(RC):
        fig, axes = plt.subplots(len(rows), 2, figsize=(13, 6.3 * len(rows)), dpi=300)
        axes = np.atleast_2d(axes)
        for j, metric in enumerate(METRICS):
            lim = lims([data[k][metric] for k in rows])
            for i, key in enumerate(rows):
                ax, d = axes[i, j], data[key][metric]
                ax.plot(lim, lim, color=GRAY, lw=1.4, ls=(0, (5, 5)), zorder=1)
                ax.errorbar(d.observed, d.predicted, xerr=d.observed_sem, yerr=d.predicted_sd,
                            fmt="o", ms=8.5, mfc="none", mec=COLOR[metric], mew=1.8,
                            ecolor=COLOR[metric], elinewidth=1.1, capsize=3, alpha=0.9, zorder=3)
                ax.set_xlim(*lim)
                ax.set_ylim(*lim)
                ax.set_aspect("equal", adjustable="box")
                for side in ("top", "right"):
                    ax.spines[side].set_visible(False)
                a, b = stat_lines(sc[key][metric])
                ax.text(0.97, 0.04, a.replace("ρ_s", r"$\rho_s$") + "\n"
                        + b.replace("R²_oos", r"$R^2_{\mathrm{oos}}$"),
                        transform=ax.transAxes, ha="right", va="bottom", fontsize=14.5, color=INK,
                        linespacing=1.5, zorder=5,
                        bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=2.5))
                ax.text(-0.02, 1.03, "abcdefgh"[2 * i + j], transform=ax.transAxes,
                        fontsize=18, fontweight="bold", ha="right", va="bottom")
                if i == 0:
                    ax.set_title(TITLE_TEX[metric], fontsize=17, pad=26)
                ax.set_xlabel("Measured", fontsize=16, labelpad=6)
                if j == 0:
                    ax.set_ylabel(f"{row_titles[i]}\n\nPredicted (held out)", fontsize=16)
        fig.tight_layout(h_pad=2.2)
        for ext in ("png", "pdf"):
            fig.savefig(OUT / f"{out_stem}.{ext}", dpi=300, bbox_inches="tight", facecolor="white",
                        metadata={"CreationDate": None} if ext == "pdf" else None)
        plt.close(fig)


def importance_png(imp_f, imp_l, out_stem):
    cols = imp_l["columns"]
    names = [PARAM_TEX[c] for c in cols]
    yy = np.arange(len(cols))[::-1]
    h = 0.38
    with plt.rc_context(RC):
        fig, axes = plt.subplots(2, 2, figsize=(14.5, 13.5), dpi=300, sharey=True)
        for j, metric in enumerate(METRICS):
            ax = axes[0, j]
            for k, (imp, col, lab, off) in enumerate(
                    [(imp_l, COLOR[metric], "noise learned", h / 2),
                     (imp_f, GRAY, "SEMs as fixed noise (campaign)", -h / 2)]):
                m = imp[metric]
                med, q25, q75 = m["share_median"], m["share_q25"], m["share_q75"]
                ax.barh(yy + off, med, height=h * 0.92, color=col if k == 0 else "white",
                        edgecolor=col, linewidth=1.4, label=lab, zorder=2)
                ax.errorbar(med, yy + off, xerr=[med - q25, q75 - med], fmt="none",
                            ecolor=INK, elinewidth=1.0, capsize=2.5, zorder=3)
            ax.axvline(1 / len(cols), color=GRAY, ls=(0, (4, 4)), lw=1.2, zorder=1)
            ax.set_xlim(0, 0.62)
            ax.set_xlabel("Share of model sensitivity\n(normalized inverse length scale)", fontsize=15)
            ax.set_title(TITLE_TEX[metric], fontsize=17, pad=12)
            ax.text(-0.02, 1.02, "ab"[j], transform=ax.transAxes, fontsize=18,
                    fontweight="bold", ha="right", va="bottom")
            ax.legend(loc="lower right", fontsize=13, frameon=False)
            ax2 = axes[1, j]
            for k, (imp, col, lab, off) in enumerate(
                    [(imp_l, COLOR[metric], "noise learned", h / 2),
                     (imp_f, GRAY, "SEMs as fixed noise (campaign)", -h / 2)]):
                m = imp[metric]
                med, q25, q75 = m["ls_median"], m["ls_q25"], m["ls_q75"]
                ax2.errorbar(med, yy + off, xerr=[med - q25, q75 - med], fmt="o", ms=7,
                             mfc=col if k == 0 else "white", mec=col, mew=1.6, ecolor=col,
                             elinewidth=1.2, capsize=2.5, label=lab, zorder=3)
                for s in m["ls_median_by_seed"]:
                    ax2.plot(s, yy + off, "|", color=col, ms=9, mew=1.2, alpha=0.8, zorder=2)
            ax2.axvline(1.0, color=GRAY, ls=(0, (4, 4)), lw=1.2, zorder=1)
            ax2.set_xscale("log")
            ax2.set_xlim(0.005, 40)
            ax2.set_xlabel("Length scale on the unit cube (log)", fontsize=15)
            ax2.text(-0.02, 1.02, "cd"[j], transform=ax2.transAxes, fontsize=18,
                     fontweight="bold", ha="right", va="bottom")
            fl, ff = imp_l[metric], imp_f[metric]
            ax2.set_title("posterior-mean sd over the fit space, share of the data sd:\n"
                          f"{pct(np.median(fl['flat_sd']) / fl['y_std'])} noise learned, "
                          f"{pct(np.median(ff['flat_sd']) / ff['y_std'])} SEMs as fixed noise",
                          fontsize=13.5, pad=10, color=INK)
            for a in (ax, ax2):
                for side in ("top", "right"):
                    a.spines[side].set_visible(False)
        axes[0, 0].set_yticks(yy)
        axes[0, 0].set_yticklabels(names, fontsize=14)
        axes[1, 0].set_yticks(yy)
        axes[1, 0].set_yticklabels(names, fontsize=14)
        fig.tight_layout(h_pad=2.5, w_pad=2.0)
        for ext in ("png", "pdf"):
            fig.savefig(OUT / f"{out_stem}.{ext}", dpi=300, bbox_inches="tight", facecolor="white",
                        metadata={"CreationDate": None} if ext == "pdf" else None)
        plt.close(fig)


# ----------------------------------------------------------------------------- plotly
PLOTLY_FONT = dict(family="Lato, 'Source Sans Pro', 'Open Sans', Arial, sans-serif", size=14, color=INK)


def axis_suffix(n):
    return "" if n == 1 else str(n)


def parity_plotly(rows, data, sc, t, row_titles, height_per_row=520):
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    titles = []
    for i, key in enumerate(rows):
        for metric in METRICS:
            titles.append(f"{TITLE_HTML[metric]}<br><span style='font-size:13px;color:{GRAY}'>"
                          f"{row_titles[i]}</span>")
    fig = make_subplots(rows=len(rows), cols=2, subplot_titles=titles,
                        horizontal_spacing=0.12, vertical_spacing=0.14 / max(1, len(rows) - 1) + 0.04)
    inputs = TWELVE
    for j, metric in enumerate(METRICS):
        lim = lims([data[k][metric] for k in rows])
        for i, key in enumerate(rows):
            r, c = i + 1, j + 1
            n = i * 2 + j + 1
            d = data[key][metric]
            z = (d.observed - d.predicted) / d.predicted_sd
            fmt = FMT[metric]
            inp = ["<br>".join(f"{PARAM_HTML[cname].rsplit(' (', 1)[0]}: {t[cname].iloc[k]:.4g} {PARAM[cname][1]}"
                               for cname in inputs) for k in range(len(t))]
            custom = np.stack([
                t.print_id, t.session_label, t.design,
                [f" (reprint twin: {w})" if w else "" for w in t.twin],
                d.observed_sem, d.predicted_sd, z, inp, t.fold_index,
            ], axis=-1)
            fig.add_trace(go.Scatter(
                x=[lim[0], lim[1]], y=[lim[0], lim[1]], mode="lines",
                line=dict(color=GRAY, dash="dash", width=1.5), hoverinfo="skip", showlegend=False,
            ), row=r, col=c)
            fig.add_trace(go.Scatter(
                x=d.observed, y=d.predicted, mode="markers", customdata=custom,
                marker=dict(symbol="circle-open", size=10, color=COLOR[metric], line=dict(width=2)),
                error_x=dict(type="data", array=d.observed_sem, thickness=1, width=0,
                             color=COLOR[metric]),
                error_y=dict(type="data", array=d.predicted_sd, thickness=1.1, width=3,
                             color=COLOR[metric]),
                hovertemplate=(
                    "<b>%{customdata[0]}</b>, %{customdata[1]}<br>"
                    "design %{customdata[2]}%{customdata[3]}, fold %{customdata[8]}<br>"
                    f"measured %{{x:{fmt}}} ± %{{customdata[4]:{fmt}}} (SEM)<br>"
                    f"predicted %{{y:{fmt}}} ± %{{customdata[5]:{fmt}}} (posterior sd)<br>"
                    "(measured − predicted) / sd = %{customdata[6]:+.2f}<br>"
                    "<span style='font-size:11px'>%{customdata[7]}</span><extra></extra>"),
                showlegend=False, name=RUN[key]["label"],
            ), row=r, col=c)
            sfx = axis_suffix(n)
            fig.update_xaxes(range=list(lim), title_text="Measured", row=r, col=c,
                             showgrid=True, gridcolor="#ecebe7", zeroline=False)
            fig.update_yaxes(range=list(lim), title_text="Predicted (held out)", row=r, col=c,
                             scaleanchor=f"x{sfx}", scaleratio=1, showgrid=True,
                             gridcolor="#ecebe7", zeroline=False)
            a, b = stat_lines(sc[key][metric])
            a = a.replace("\u03c1_s", "\u03c1<sub>s</sub>")
            b = b.replace("R\u00b2_oos", "R<sup>2</sup><sub>oos</sub>")
            fig.add_annotation(
                text=f"{a}<br>{b}<br>coverage at 1.96 sd: {sc[key][metric]['coverage_1.96sd_pct']:.0f}%",
                xref=f"x{sfx} domain", yref=f"y{sfx} domain", x=0.98, y=0.03,
                xanchor="right", yanchor="bottom", showarrow=False, align="right",
                font=dict(size=13, color=INK), bgcolor="rgba(255,255,255,0.85)")
    fig.update_layout(template="simple_white", font=PLOTLY_FONT, height=height_per_row * len(rows),
                      margin=dict(l=70, r=30, t=90, b=60), hoverlabel=dict(font_size=12))
    fig.update_annotations(selector=dict(xref="paper"), font_size=15)
    return fig


def importance_plotly(imps, cols, title_suffix):
    """imps: list of (label, colour-or-None, imp dict, filled) in display order."""
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    names = [PARAM_HTML[c] for c in cols]
    height = 52 * len(cols) * 2 + 230
    fig = make_subplots(rows=2, cols=2, horizontal_spacing=0.2, vertical_spacing=150 / height,
                        subplot_titles=[f"{TITLE_HTML[m]}: share of model sensitivity" for m in METRICS]
                        + [f"{TITLE_HTML[m]}: raw length scales (log)" for m in METRICS])
    for j, metric in enumerate(METRICS):
        for lab, col, imp, filled in imps:
            colour = col or COLOR[metric]
            m = imp[metric]
            med, q25, q75 = m["share_median"], m["share_q25"], m["share_q75"]
            seeds = m["ax_importance_by_seed"]
            hover = [
                f"<b>{names[k]}</b><br>{lab}<br>share (posterior median over {m['n_draws']} draws): "
                f"{med[k]:.3f}<br>interquartile range: {q25[k]:.3f} to {q75[k]:.3f}<br>"
                f"Ax feature_importances, pooled draws: {m['ax_importance_pooled'][k]:.3f}<br>"
                f"Ax value per NUTS seed: " + ", ".join(f"{v:.3f}" for v in seeds[:, k])
                for k in range(len(cols))]
            fig.add_trace(go.Bar(
                y=names, x=med, orientation="h", name=lab, legendgroup=lab, showlegend=(j == 0),
                marker=dict(color=colour if filled else "white", line=dict(color=colour, width=1.8)),
                error_x=dict(type="data", symmetric=False, array=q75 - med, arrayminus=med - q25,
                             color=INK, thickness=1.1, width=3),
                hovertext=hover, hoverinfo="text",
            ), row=1, col=j + 1)
            lmed, l25, l75 = m["ls_median"], m["ls_q25"], m["ls_q75"]
            hover2 = [
                f"<b>{names[k]}</b><br>{lab}<br>length scale (unit cube), posterior median: {lmed[k]:.3g}<br>"
                f"interquartile range: {l25[k]:.3g} to {l75[k]:.3g}<br>median per NUTS seed: "
                + ", ".join(f"{v:.3g}" for v in m["ls_median_by_seed"][:, k])
                for k in range(len(cols))]
            fig.add_trace(go.Scatter(
                y=names, x=lmed, mode="markers", name=lab, legendgroup=lab, showlegend=False,
                marker=dict(symbol="circle" if filled else "circle-open", size=11, color=colour,
                            line=dict(color=colour, width=2)),
                error_x=dict(type="data", symmetric=False, array=l75 - lmed, arrayminus=lmed - l25,
                             color=colour, thickness=1.3, width=3),
                hovertext=hover2, hoverinfo="text",
            ), row=2, col=j + 1)
        n_top, n_bot = j + 1, j + 3
        fig.add_shape(type="line", x0=1 / len(cols), x1=1 / len(cols), y0=0, y1=1,
                      xref=f"x{axis_suffix(n_top)}", yref=f"y{axis_suffix(n_top)} domain",
                      line=dict(color=GRAY, dash="dash", width=1.3))
        fig.add_shape(type="line", x0=1, x1=1, y0=0, y1=1,
                      xref=f"x{axis_suffix(n_bot)}", yref=f"y{axis_suffix(n_bot)} domain",
                      line=dict(color=GRAY, dash="dash", width=1.3))
        fig.update_xaxes(title_text="share (normalized inverse length scale); dashed: equal share",
                         range=[0, 0.62], row=1, col=j + 1)
        fig.update_xaxes(title_text="length scale on the unit cube; dashed: width of the cube",
                         type="log", range=[np.log10(0.005), np.log10(40)],
                         tickvals=[0.01, 0.1, 1, 10], ticktext=["0.01", "0.1", "1", "10"],
                         row=2, col=j + 1)
        for r in (1, 2):
            fig.update_yaxes(autorange="reversed", row=r, col=j + 1)
    fig.update_layout(template="simple_white", font=PLOTLY_FONT, barmode="group",
                      bargap=0.25, bargroupgap=0.05, height=height,
                      legend=dict(orientation="h", y=1.07, x=0.5, xanchor="center"),
                      margin=dict(l=40, r=30, t=110, b=60), title=dict(text=title_suffix, x=0.01))
    fig.update_annotations(selector=dict(xref="paper"), font_size=15)
    return fig


# ----------------------------------------------------------------------------- page
CSS = """
body{font-family:Lato,'Source Sans Pro','Open Sans',Arial,sans-serif;color:#0b0b0b;
     max-width:1180px;margin:24px auto;padding:0 18px;line-height:1.5}
h1{font-size:26px;margin-bottom:4px} h2{font-size:21px;margin-top:38px;border-bottom:1px solid #ddd}
p,li{font-size:15.5px} .muted{color:#5f5e5a;font-size:14px}
table{border-collapse:collapse;font-size:13.5px;margin:10px 0}
th,td{border-bottom:1px solid #e4e3df;padding:4px 9px;text-align:right}
th{background:#f6f5f2} td.l,th.l{text-align:left} td:not(.l){white-space:nowrap}
tr.hl td{background:#eef4fc}
code{font-size:13px;background:#f3f2ef;padding:1px 4px;border-radius:3px}
"""


def scorecard_html(sc, keys):
    head = ("<tr><th class='l'>run</th><th class='l'>fix</th><th class='l'>model</th><th>inputs</th>"
            + "".join(f"<th>{m} ρ<sub>s</sub> (p)</th><th>{m} R²<sub>oos</sub></th>"
                      f"<th>{m} MAPE</th><th>{m} cov.</th>"
                      for m in ("t180", "E_reb")) + "</tr>")
    rows = []
    for k in keys:
        r = RUN[k]
        cells = [f"<td class='l'>{r['label']}</td><td class='l'>{r['fix']}</td>"
                 f"<td class='l'>{r['model']}</td><td>{ {'twelve': 12, 'eight': 8}.get(r['space'], '-') }</td>"]
        for metric in METRICS:
            s = sc[k][metric]
            rho = "mechanical" if k == "mean" else f"{fnum(s['spearman_rho'])} ({fp(s['perm_p']).replace('p = ', '').replace('p ', '')})"
            cells.append(f"<td>{rho}</td><td>{fnum(s['R2_oos'])}</td><td>{s['MAPE_pct']:.1f}%</td>"
                         f"<td>{s['coverage_1.96sd_pct']:.0f}%</td>")
        cls = " class='hl'" if k in ("learned", "learned-eight") else ""
        rows.append(f"<tr{cls}>" + "".join(cells) + "</tr>")
    return "<table>" + head + "".join(rows) + "</table>"


def flat_table_html(imps):
    rows = []
    for (dataset, noise), imp in imps.items():
        for metric in METRICS:
            m = imp[metric]
            top = pd.Series(m["top_by_seed"]).value_counts()
            top_s = ", ".join(f"{PARAM_HTML[c].rsplit(' (', 1)[0]} ({n}/4)" for c, n in top.items())
            nz = ("-" if m["noise_sd"] is None else
                  f"{np.median(m['noise_sd']):.3g}")
            rows.append(
                f"<tr><td class='l'>{dataset}</td><td class='l'>{noise}</td>"
                f"<td class='l'>{OBJ_HTML[metric]}</td>"
                f"<td>{np.median(m['flat_sd']):.3g}</td><td>{m['y_std']:.3g}</td>"
                f"<td>{pct(np.median(m['flat_sd']) / m['y_std'])}</td><td>{nz}</td>"
                f"<td class='l'>{top_s}</td></tr>")
    head = ("<tr><th class='l'>fit</th><th class='l'>noise</th><th class='l'>objective</th>"
            "<th>sd of the posterior mean over the space</th><th>data sd</th><th>ratio</th>"
            "<th>learned noise sd</th><th class='l'>top input per NUTS seed (Ax importance)</th></tr>")
    return "<table>" + head + "".join(rows) + "</table>"


def vendored_plotlyjs():
    """Write the plotly.js bundled with plotly.py next to the page, once, and
    return its file name. The page loads it by relative path: the GitHub HTML
    preview (htmlpreview.github.io) runs only scripts served from
    raw.githubusercontent.com, so a CDN copy would leave the plots blank there."""
    import plotly.offline as po

    name = f"plotly-{po.get_plotlyjs_version()}.min.js"
    if not (OUT / name).exists():
        (OUT / name).write_text(po.get_plotlyjs())
    return name


def page(figs, sc, imps, t, data):
    import plotly.io as pio

    def emb(key, first=False):
        # fixed div ids keep the page byte-identical between reruns
        return pio.to_html(figs[key], full_html=False, include_plotlyjs=False, div_id=key,
                           config={"displaylogo": False, "responsive": True,
                                   "toImageButtonOptions": {"format": "svg", "scale": 1}})

    c, l = sc["campaign"], sc["learned"]
    imp_l = imps[("all-twelve", "learned")]
    imp_f = imps[("all-twelve", "fixed")]
    top_t = pd.Series(imp_l["t180"]["top_by_seed"]).value_counts()
    plotly_js = vendored_plotlyjs()
    miss = []
    for metric, k in (("t180", 2), ("e_reb_mJ", 3)):
        d = data["learned"][metric].assign(err=lambda x: (x.observed - x.predicted).abs())
        for _, r in d.sort_values("err", ascending=False).head(k).iterrows():
            miss.append(f"{OBJ_HTML[metric]} {r.print_id} ({r.observed:.2f}, {r.predicted:.2f})")
    misses = "; ".join(miss)
    body = f"""
<h1>The campaign surrogate with the review's fixes applied</h1>
<p class="muted">PR #121, branch <code>claude/request-c-tables-logocv-ai-20261027</code>. Generated by
<code>analysis/bo-review/plot_fixes.py</code> from committed run records; nothing is refitted on this page.
Hover over any point or bar for its record. Every number here is in <code>scorecard.json</code>.</p>

<p><b>Which fixes reach the surrogate.</b> Of the review's points, the noise model (item 1: noise learned, or
replicate-based SEMs, instead of the per-article SEMs as fixed noise) and the filament settings (item 4: the four
batch-level settings dropped) change the model. The objective thresholds and the filament point fixed before the
acquisition (items 2 and 3) change only how candidates are chosen, so they do not enter the held-out predictions.</p>

<h2>1. Held-out predictions: campaign surrogate against the same SAASBO with the noise learned</h2>
<p>Leave-one-design-out cross-validation over the 44 articles: 35 design folds, each batch-3 reprint pair held out
together, one NUTS refit per fold at the campaign budget (512 warmup steps, 256 samples). Both rows are the campaign's
Ax 0.5.0 SAASBO with the same folds, seeds and budget; the bottom row blanks the SEMs so the noise is learned.
Vertical bars are one posterior sd of the held-out prediction (latent, without the learned noise), horizontal bars the
ingested SEM, dashed line parity. R²<sub>oos</sub> is against predicting each fold's training mean.</p>
{emb('parity_main', first=True)}
<p><b>Reading.</b> With the SEMs as fixed noise every held-out prediction sits near the pooled mean (spread of the
predictions {c['t180']['pred_sd_over_obs_sd']:.2f} of the data sd for t<sub>180</sub>,
{c['e_reb_mJ']['pred_sd_over_obs_sd']:.2f} for E<sub>reb</sub>), and the E<sub>reb</sub> ordering runs against the
measurements (ρ<sub>s</sub> {fnum(c['e_reb_mJ']['spearman_rho'])}). With the noise learned the predictions follow
the measurements: t<sub>180</sub> ρ<sub>s</sub> {fnum(l['t180']['spearman_rho'])} ({fp(l['t180']['perm_p'])}),
R²<sub>oos</sub> {fnum(l['t180']['R2_oos'])}; E<sub>reb</sub> ρ<sub>s</sub>
{fnum(l['e_reb_mJ']['spearman_rho'])} ({fp(l['e_reb_mJ']['perm_p'])}), R²<sub>oos</sub>
{fnum(l['e_reb_mJ']['R2_oos'])}. Its largest misses (measured, predicted): {misses}.</p>

<h2>2. Scorecard</h2>
<p>Same 35 folds and 44 articles in every row. ρ<sub>s</sub>: Spearman rank correlation of held-out prediction and
measurement, two-sided permutation p (20,000 shuffles). Coverage: share of articles within 1.96 latent posterior sd.
Highlighted: the two models with the fixes applied.</p>
{scorecard_html(sc, [r['key'] for r in RUNS])}
<p class="muted">The two "check" rows refit the campaign and learned-noise models in the BoTorch 0.18 / NumPyro driver of
<code>logocv_noise_models.py</code>, which the replicate-SEM and eight-input runs use: the driver does not change the
conclusion. Latent coverage of the learned-noise models falls short for E<sub>reb</sub> because the learned noise is left
out of the bars; BoFire's predictive sd, which adds it, covers 89 to 93% (see
<code>analysis/logocv-baselines/README.md</code>).</p>

<h2>3. The other fixes: replicate-based SEMs, and the filament settings dropped</h2>
<p>Top: train_Yvar = SEM² + s_print², with s_print pooled over the reprint twins of each training fold (twelve
inputs). Bottom: noise learned and the four filament settings dropped (eight inputs: R, H, θ, d<sub>s</sub>,
d<sub>t</sub>, printed mass, strut and tendon infill), the model the review recommends until a plate varies the
filament settings on purpose. Both: BoTorch 0.18.1 SAAS, NUTS 512/256.</p>
{emb('parity_other')}

<h2>4. Feature importance of the surrogate fitted to all 44 articles</h2>
<p>SAAS fits to all 44 articles at the campaign budget, four NUTS seeds each (64 posterior draws pooled). Top: the share
of model sensitivity, i.e. Ax's <code>feature_importances</code> (inverse length scale, normalized to sum to 1); bars are
the posterior median over draws, whiskers the interquartile range; hover for Ax's pooled value and the value per seed.
Bottom: the raw length scales on the unit cube, which say how smooth the model is (the normalization above hides that).
Filled: noise learned. Open: SEMs as fixed noise (campaign).</p>
{emb('imp_twelve')}
<p><b>Reading.</b> With the SEMs as fixed noise the printed mass gets the largest share for both objectives, at length
scales of a few hundredths of the cube: the model uses mass to tell the reprint twins apart and is flat between
articles. With the noise learned every length scale is of the order of the cube or longer (a smooth, close to linear
model), the t<sub>180</sub> model ranks cable diameter <i>d</i><sub>t</sub> first
({', '.join(f"{PARAM_HTML[k].rsplit(' (', 1)[0]} in {v} of 4 seeds" for k, v in top_t.items())}), and printed mass drops to an ordinary
share. E<sub>reb</sub> has no stable ranking: its top input changes with the seed.</p>
{emb('imp_eight')}

<h2>5. Is the model flat?</h2>
<p>The sd of the posterior mean over 1024 scrambled-Sobol points of the fit space, against the sd of the 44
measurements (median over the four NUTS seeds). A flat model has a ratio near zero.</p>
{flat_table_html(imps)}

<h2>Data and provenance</h2>
<ul>
<li>Campaign surrogate: <code>manuscript/data/t3-prism-bo-round5-logocv.csv</code> (SI fig:si-logocv).</li>
<li>Noise learned (Ax): <code>analysis/logocv-baselines/data/ax-saasbo-inferred-noise-twelve/</code>.</li>
<li>BoTorch 0.18 runs: <code>analysis/bo-review/data/logocv/saas-&lt;noise&gt;-&lt;space&gt;/</code>
(<code>logocv_noise_models.py</code>).</li>
<li>Importances: <code>analysis/bo-review/data/importances/all-&lt;space&gt;-&lt;noise&gt;-512w256-s&lt;seed&gt;.json</code>
(<code>importances_stability.py</code>).</li>
<li>Static versions for the manuscript: <code>logocv-parity-noise.pdf</code>, <code>logocv-parity-other-fixes.pdf</code>,
<code>feature-importance-noise.pdf</code> (and PNGs) next to this page.</li>
</ul>
"""
    return (f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<title>Surrogate with the review fixes: LOGO-CV and feature importance</title>"
            f"<script src='{plotly_js}' charset='utf-8'></script><style>{CSS}</style></head>"
            f"<body>{body}</body></html>\n")


# ----------------------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t = load_table()
    data = {r["key"]: load_run(r, t) for r in RUNS}
    sc = {k: {m: score(data[k][m], t, m) for m in METRICS} for k in data}
    imps = {(ds, nz): load_importances(ds, nz)
            for ds in ("all-twelve", "all-eight") for nz in ("fixed", "learned")}

    # static figures
    parity_png(["campaign", "learned"], data, sc, "logocv-parity-noise",
               ["SEMs as fixed noise\n(campaign)", "Noise learned"])
    parity_png(["replicate", "learned-eight"], data, sc, "logocv-parity-other-fixes",
               ["Replicate-based SEMs\n(twelve inputs)", "Noise learned,\nfilament settings dropped"])
    importance_png(imps[("all-twelve", "fixed")], imps[("all-twelve", "learned")],
                   "feature-importance-noise")

    # interactive page
    figs = {
        "parity_main": parity_plotly(["campaign", "learned"], data, sc, t,
                                     ["SAASBO, SEMs as fixed noise (campaign)",
                                      "same SAASBO, noise learned"]),
        "parity_other": parity_plotly(["replicate", "learned-eight"], data, sc, t,
                                      ["SAAS, replicate-based SEMs, twelve inputs",
                                       "SAAS, noise learned, filament settings dropped (eight inputs)"]),
        "imp_twelve": importance_plotly(
            [("noise learned", None, imps[("all-twelve", "learned")], True),
             ("SEMs as fixed noise (campaign)", GRAY, imps[("all-twelve", "fixed")], False)],
            TWELVE, "Twelve inputs (the campaign's fit space)"),
        "imp_eight": importance_plotly(
            [("noise learned", None, imps[("all-eight", "learned")], True),
             ("SEMs as fixed noise (campaign)", GRAY, imps[("all-eight", "fixed")], False)],
            EIGHT, "Eight inputs (filament settings dropped)"),
    }
    (OUT / "index.html").write_text(page(figs, sc, imps, t, data))

    # scorecard
    rows = []
    for r in RUNS:
        for m in METRICS:
            rows.append({"run": r["key"], "label": r["label"], "fix": r["fix"], "model": r["model"],
                         "space": r["space"], "source": str(r["path"].relative_to(ROOT)),
                         "metric": m, **sc[r["key"]][m]})
    pd.DataFrame(rows).to_csv(OUT / "scorecard.csv", index=False, float_format="%.5g")
    imp_out = {}
    for (ds, nz), imp in imps.items():
        imp_out[f"{ds}-{nz}"] = {
            m: {"columns": imp["columns"],
                "share_median": np.round(imp[m]["share_median"], 4).tolist(),
                "share_iqr": [np.round(imp[m]["share_q25"], 4).tolist(),
                              np.round(imp[m]["share_q75"], 4).tolist()],
                "ax_importance_pooled": np.round(imp[m]["ax_importance_pooled"], 4).tolist(),
                "lengthscale_median": np.round(imp[m]["ls_median"], 4).tolist(),
                "top_input_by_seed": imp[m]["top_by_seed"],
                "posterior_mean_sd_over_space_by_seed": np.round(imp[m]["flat_sd"], 5).tolist(),
                "y_std": imp[m]["y_std"],
                "noise_sd_by_seed": (None if imp[m]["noise_sd"] is None
                                     else np.round(imp[m]["noise_sd"], 5).tolist())}
            for m in METRICS}
    (OUT / "scorecard.json").write_text(json.dumps(
        {"logocv": {r["key"]: {"label": r["label"], "fix": r["fix"], "model": r["model"],
                               "space": r["space"], "source": str(r["path"].relative_to(ROOT)),
                               "note": r["note"], **sc[r["key"]]} for r in RUNS},
         "importances": imp_out}, indent=1) + "\n")
    for r in RUNS:
        s = sc[r["key"]]
        print(f"{r['key']:16s} t180 rho {s['t180']['spearman_rho']:+.3f} p {s['t180']['perm_p']:.4f} "
              f"R2 {s['t180']['R2_oos']:+.3f} MAPE {s['t180']['MAPE_pct']:.2f} cov {s['t180']['coverage_1.96sd_pct']:.0f} | "
              f"E_reb rho {s['e_reb_mJ']['spearman_rho']:+.3f} p {s['e_reb_mJ']['perm_p']:.4f} "
              f"R2 {s['e_reb_mJ']['R2_oos']:+.3f} MAPE {s['e_reb_mJ']['MAPE_pct']:.2f} cov {s['e_reb_mJ']['coverage_1.96sd_pct']:.0f}")


if __name__ == "__main__":
    main()
