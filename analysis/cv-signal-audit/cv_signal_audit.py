"""Is there any predictive signal in the T3-prism campaign data?

Recomputes every cross-validation claim from the committed campaign
snapshots vendored in analysis/cv-signal-audit/data/ (provenance in
data/README.md), then answers three questions the LOGO-CV figure raised:

1. Article level: does the round-5 leave-one-design-out CV show skill
   beyond a trivial mean predictor? Reports r, r^2, Spearman rho with
   Monte-Carlo permutation p, and out-of-sample R^2 against both the
   global mean and the honest per-fold training mean, plus calibration
   coverage, shrinkage, jackknife influence, and a cluster-only view.
2. Design and selection level: the tests the optimizer actually needs.
   Collapses reprint pairs to design means, then scores the archived
   at-selection predictions for batches 2 to 4 within-batch (exact
   permutation p at n=9), including best-predicted-vs-best-measured.
3. Noise ladder: puts per-drop scatter, the standard errors the model
   ingested, between-print/seat scatter from the nine reprint pairs, and
   the design-to-design spread on one axis per metric, which is the
   context for the restraint-cord (bungee) interference question.

Deterministic: fixed RNG seed, exact enumeration where n makes it cheap.
Outputs: metrics.json plus three PNG figures under figures/.
"""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGS = HERE / "figures"
SEED = 20260922
N_PERM = 100_000

# Batch identity colors (Okabe-Ito subset, CVD-validated); 2dran shares the
# drran hue with open markers because it is the same nine designs re-printed.
BATCH_STYLE = {
    "seed": dict(color="#0072B2", marker="o", filled=True, label="seed (Sobol)"),
    "r2d2c": dict(color="#E69F00", marker="s", filled=True, label="batch 2 (r2d2c)"),
    "drran": dict(color="#009E73", marker="^", filled=True, label="batch 3 (drran)"),
    "2dran": dict(color="#009E73", marker="v", filled=False, label="batch 3 reprint (2dran)"),
    "corny": dict(color="#D55E00", marker="D", filled=True, label="batch 4 (corny)"),
}
T180_COLOR = "#1f77b4"   # metric hues, matching the campaign figures
REB_COLOR = "#e8590c"
GRID = dict(color="0.92", lw=0.7, zorder=0)

METRICS = ("t180", "e_reb_mJ")
METRIC_LABEL = {"t180": "t180 (transmissibility)", "e_reb_mJ": "rebound score (mJ)"}


# --------------------------------------------------------------------------
# loading and joins
# --------------------------------------------------------------------------

def batch_of(print_id: str) -> str:
    for prefix in ("r2d2c", "2dran", "drran", "corny"):
        if print_id.startswith(prefix):
            return prefix
    return "seed"


def load_logo() -> pd.DataFrame:
    """One row per (article, metric): observed, ingested SE, held-out pred."""
    logo = pd.read_csv(DATA / "t3-prism-bo-round5-logocv.csv")
    logo["batch"] = logo.print_id.map(batch_of)

    # design id: batch articles share a design iff they share an Ax source
    # trial (the drranN/2dranN reprint pairs); seed articles are unique.
    keys = pd.concat(
        pd.read_csv(DATA / f"t3-prism-bo-{r}-print-key.csv")[["print_id", "source_trial"]]
        for r in ("round1", "round3", "round4")
    )
    trial_of = dict(zip(keys.print_id, keys.source_trial))
    logo["design"] = [
        f"trial{trial_of[p]}" if p in trial_of else p for p in logo.print_id
    ]
    return logo


def load_prospective() -> pd.DataFrame:
    """At-selection posterior predictions joined to measured outcomes."""
    frames = []
    for rnd, batch in (("round1", "r2d2c"), ("round3", "drran"), ("round4", "corny")):
        pred = pd.read_csv(DATA / f"t3-prism-bo-{rnd}-predictions.csv")
        key = pd.read_csv(DATA / f"t3-prism-bo-{rnd}-print-key.csv")
        m = key.merge(pred, left_on="source_trial", right_on="trial_index",
                      how="inner", validate="many_to_one")
        m["batch"] = m.print_id.map(batch_of)
        frames.append(m)
    pro = pd.concat(frames, ignore_index=True)

    logo = load_logo()
    for metric, col in (("t180", "meas_t180"), ("e_reb_mJ", "meas_e_reb_mJ")):
        obs = logo[logo.metric == metric].set_index("print_id").observed
        pro[col] = pro.print_id.map(obs)
    if pro[["meas_t180", "meas_e_reb_mJ"]].isna().any().any():
        raise RuntimeError("prospective join failed for some articles")
    return pro


# --------------------------------------------------------------------------
# statistics helpers
# --------------------------------------------------------------------------

def perm_p_spearman(x: np.ndarray, y: np.ndarray, rng: np.random.Generator,
                    exact_max: int = 9) -> tuple[float, float]:
    """Two-sided permutation p for Spearman rho; exact enumeration if n small."""
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    rho_obs = np.corrcoef(rx, ry)[0, 1]
    n = len(x)
    if n <= exact_max:
        perms = np.array(list(itertools.permutations(range(n))))
        ry_perm = ry[perms]                       # (n!, n)
    else:
        ry_perm = np.stack([rng.permutation(ry) for _ in range(N_PERM)])
    rx_c = rx - rx.mean()
    ry_c = ry_perm - ry_perm.mean(axis=1, keepdims=True)
    rho = (ry_c @ rx_c) / np.sqrt((ry_c ** 2).sum(axis=1) * (rx_c ** 2).sum())
    p = float(np.mean(np.abs(rho) >= np.abs(rho_obs) - 1e-12))
    return float(rho_obs), p


def perm_p_pearson(x: np.ndarray, y: np.ndarray, rng: np.random.Generator) -> float:
    r_obs = np.corrcoef(x, y)[0, 1]
    y_perm = np.stack([rng.permutation(y) for _ in range(N_PERM)])
    xc = x - x.mean()
    yc = y_perm - y_perm.mean(axis=1, keepdims=True)
    r = (yc @ xc) / np.sqrt((yc ** 2).sum(axis=1) * (xc ** 2).sum())
    return float(np.mean(np.abs(r) >= np.abs(r_obs) - 1e-12))


def fisher_ci(r: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    z = np.arctanh(r)
    se = 1.0 / math.sqrt(n - 3)
    zc = stats.norm.ppf(1 - alpha / 2)
    return float(np.tanh(z - zc * se)), float(np.tanh(z + zc * se))


def auc_mannwhitney(labels: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    """AUC for labels (1=positive) ranked by scores, with two-sided MW p."""
    pos, neg = scores[labels == 1], scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan"), float("nan")
    res = stats.mannwhitneyu(pos, neg, alternative="two-sided")
    return float(res.statistic / (len(pos) * len(neg))), float(res.pvalue)


def held_out_metrics(obs: np.ndarray, pred: np.ndarray, psem: np.ndarray,
                     designs: np.ndarray, rng: np.random.Generator) -> dict:
    """The full article-level scorecard for one metric."""
    n = len(obs)
    resid = obs - pred
    sse = float((resid ** 2).sum())
    sst_global = float(((obs - obs.mean()) ** 2).sum())

    # honest LOGO baseline: predict each held-out design with the mean of
    # every *other* design's articles (what "no model" would have delivered)
    base = np.empty(n)
    for d in np.unique(designs):
        mask = designs == d
        base[mask] = obs[~mask].mean()
    sst_fold = float(((obs - base) ** 2).sum())

    r = float(np.corrcoef(obs, pred)[0, 1])
    rho, rho_p = perm_p_spearman(obs, pred, rng)
    lo, hi = fisher_ci(r, n)
    return {
        "n": n,
        "mape_pct": float(np.mean(np.abs(resid) / np.abs(obs)) * 100),
        "rmse": math.sqrt(sse / n),
        "pearson_r": r,
        "pearson_r_ci95": [lo, hi],
        "pearson_p_perm": perm_p_pearson(obs, pred, rng),
        "r_squared_of_r": r * r,
        "spearman_rho": rho,
        "spearman_p_perm": rho_p,
        "R2_oos_vs_global_mean": 1 - sse / sst_global,
        "R2_oos_vs_fold_train_mean": 1 - sse / sst_fold,
        "rmse_mean_predictor": math.sqrt(sst_fold / n),
        "shrinkage_sd_pred_over_sd_obs": float(pred.std(ddof=1) / obs.std(ddof=1)),
        "coverage_68_pct": float(np.mean(np.abs(resid) <= psem) * 100),
        "coverage_95_pct": float(np.mean(np.abs(resid) <= 1.96 * psem) * 100),
        "median_posterior_sd": float(np.median(psem)),
        "sd_observed": float(obs.std(ddof=1)),
    }


# --------------------------------------------------------------------------
# analysis sections
# --------------------------------------------------------------------------

def section_logo(logo: pd.DataFrame, rng: np.random.Generator) -> dict:
    out = {}
    diag = json.loads((DATA / "t3-prism-bo-round5-logocv-diagnostics.json").read_text())
    for metric in METRICS:
        d = logo[logo.metric == metric]
        m = held_out_metrics(d.observed.values, d.predicted.values,
                             d.predicted_sem.values, d.design.values, rng)
        # cross-check against the archived Ax diagnostics; the CSV rounds to
        # five decimals, which moves r and MAPE by <1e-5 but can flip
        # near-tied ranks, so the rank statistic gets a looser tolerance
        m["matches_archived_diagnostics"] = bool(
            abs(m["pearson_r"] - diag["Correlation coefficient"][metric]) < 1e-4
            and abs(m["mape_pct"] / 100 - diag["MAPE"][metric]) < 1e-4
            and abs(m["spearman_rho"] - diag["Rank correlation"][metric]) < 1e-3
        )
        # discrimination framed as classification: better-than-median, and
        # (for t180) genuine attenuator (< 1)
        obs, pred = d.observed.values, d.predicted.values
        better = (obs < np.median(obs)).astype(int)  # lower is better for both
        auc, auc_p = auc_mannwhitney(better, -pred)
        m["auc_better_half"] = auc
        m["auc_better_half_p"] = auc_p
        if metric == "t180":
            atten = (obs < 1.0).astype(int)
            m["n_attenuators"] = int(atten.sum())
            auc_a, auc_ap = auc_mannwhitney(atten, -pred)
            m["auc_attenuator"] = auc_a
            m["auc_attenuator_p"] = auc_ap
        out[metric] = m

    # influence and cluster-only view for t180
    t = logo[logo.metric == "t180"]
    obs, pred = t.observed.values, t.predicted.values
    r_full = np.corrcoef(obs, pred)[0, 1]
    drops = []
    for i in range(len(obs)):
        keep = np.arange(len(obs)) != i
        drops.append(np.corrcoef(obs[keep], pred[keep])[0, 1] - r_full)
    drops = np.array(drops)
    order = np.argsort(-np.abs(drops))[:3]
    out["t180_influence"] = {
        "r_full": float(r_full),
        "top_influencers": [
            {"print_id": t.print_id.values[i], "delta_r_when_removed": float(drops[i])}
            for i in order
        ],
    }
    cluster = t[(t.observed >= 0.95) & (t.observed <= 1.10)]
    out["t180_cluster_only"] = held_out_metrics(
        cluster.observed.values, cluster.predicted.values,
        cluster.predicted_sem.values, cluster.design.values, rng)
    outside = t[(t.observed < 0.95) | (t.observed > 1.10)]
    med = float(np.median(t.observed))
    hits = int((((outside.observed < med) & (outside.predicted < med))
                | ((outside.observed > med) & (outside.predicted > med))).sum())
    out["t180_extremes_direction"] = {
        "n_outside_cluster": int(len(outside)),
        "predicted_on_correct_side_of_median": hits,
        "binomial_p_vs_coinflip": float(stats.binomtest(hits, len(outside), 0.5).pvalue),
        "articles": {r.print_id: {"observed": float(r.observed),
                                  "predicted": float(r.predicted)}
                     for r in outside.itertuples()},
    }
    return out


def section_design_level(logo: pd.DataFrame, rng: np.random.Generator) -> dict:
    out = {}
    for metric in METRICS:
        d = logo[logo.metric == metric]
        g = d.groupby("design").agg(observed=("observed", "mean"),
                                    predicted=("predicted", "mean"),
                                    predicted_sem=("predicted_sem", "mean"))
        out[metric] = held_out_metrics(g.observed.values, g.predicted.values,
                                       g.predicted_sem.values,
                                       g.index.values, rng)
    return out


def section_reliability(logo: pd.DataFrame) -> dict:
    """Test-retest ceiling from the nine reprint pairs (recap of the prior
    reprint_reliability_ceiling.py analysis, recomputed here so this PR is
    self-contained)."""
    pairs = pd.read_csv(DATA / "t3-prism-bo-round3-repeatability.csv")
    out = {}
    for metric, col in (("t180", "t180"), ("e_reb_mJ", "e_reb_mJ")):
        x, y = pairs[f"{col}_1"].values, pairs[f"{col}_2"].values
        stacked = np.stack([x, y], axis=1)
        grand = stacked.mean()
        n, k = stacked.shape
        msb = k * ((stacked.mean(axis=1) - grand) ** 2).sum() / (n - 1)
        msw = ((stacked - stacked.mean(axis=1, keepdims=True)) ** 2).sum() / (n * (k - 1))
        icc = (msb - msw) / (msb + (k - 1) * msw)
        delta = y - x
        no7 = pairs.print_1 != "drran7"
        out[metric] = {
            "pair_pearson_r": float(np.corrcoef(x, y)[0, 1]),
            "pair_spearman_rho": float(stats.spearmanr(x, y).statistic),
            "icc_1_1": float(icc),
            "ceiling_r_sqrt_icc": float(math.sqrt(max(icc, 0.0))),
            "sigma_print_raw": float(np.std(delta, ddof=1) / math.sqrt(2)),
            "sigma_print_excl_drran7": float(
                np.std(delta[no7.values], ddof=1) / math.sqrt(2)),
            "median_shift": float(np.median(delta)),
            "reprint_as_predictor_mape_pct": float(np.mean(np.concatenate(
                [np.abs(delta) / np.abs(x), np.abs(-delta) / np.abs(y)])) * 100),
        }
    return out


def section_prospective(pro: pd.DataFrame, logo: pd.DataFrame,
                        rng: np.random.Generator) -> dict:
    """Score the archived at-selection predictions batch by batch."""
    out = {"batches": {}}
    rhos = {}
    for batch in ("r2d2c", "drran", "2dran", "corny"):
        d = pro[pro.batch == batch].copy()
        obs, pred = d.meas_t180.values, d.pred_t180_mean.values
        psd = d.pred_t180_sd.values
        rho, p_exact = perm_p_spearman(obs, pred, rng)  # exact at n=9
        best_idx = int(np.argmin(pred))
        best_meas_rank = int(stats.rankdata(obs)[best_idx])  # 1 = best measured
        obs_e, pred_e = d.meas_e_reb_mJ.values, d.pred_e_reb_mJ_mean.values
        rho_e, p_e = perm_p_spearman(obs_e, pred_e, rng)
        out["batches"][batch] = {
            "n": int(len(d)),
            "t180_mape_pct": float(np.mean(np.abs(pred - obs) / obs) * 100),
            "t180_spearman_rho": rho,
            "t180_p_exact_perm": p_exact,
            "t180_coverage_95_pct": float(np.mean(np.abs(obs - pred) <= 1.96 * psd) * 100),
            "t180_mean_bias": float(np.mean(obs - pred)),
            "best_predicted_print": d.print_id.values[best_idx],
            "best_predicted_measured_rank_of_9": best_meas_rank,
            "p_rank_by_chance": best_meas_rank / len(d),
            "e_reb_spearman_rho": rho_e,
            "e_reb_p_exact_perm": p_e,
        }
        if batch != "2dran":
            rhos[batch] = (obs, pred)

    # pooled within-batch rank test over the three prospective batches
    # (2dran excluded: same designs as drran, so not independent)
    obs_all = [rhos[b][0] for b in ("r2d2c", "drran", "corny")]
    pred_all = [rhos[b][1] for b in ("r2d2c", "drran", "corny")]

    def mean_rho(perm: bool) -> float:
        vals = []
        for o, p in zip(obs_all, pred_all):
            oo = rng.permutation(o) if perm else o
            vals.append(np.corrcoef(stats.rankdata(oo), stats.rankdata(p))[0, 1])
        return float(np.mean(vals))

    obs_stat = mean_rho(False)
    null = np.array([mean_rho(True) for _ in range(20_000)])
    out["pooled_within_batch"] = {
        "mean_spearman_rho": obs_stat,
        "p_perm_two_sided": float(np.mean(np.abs(null) >= abs(obs_stat) - 1e-12)),
    }

    # batch-3 design means (average the drran/2dran twins), scored against
    # the same at-selection predictions
    d3 = pro[pro.batch.isin(["drran", "2dran"])]
    g = d3.groupby("source_trial").agg(obs=("meas_t180", "mean"),
                                       pred=("pred_t180_mean", "first"))
    rho3, p3 = perm_p_spearman(g.obs.values, g.pred.values, rng)
    out["batch3_design_means"] = {"t180_spearman_rho": rho3, "p_exact_perm": p3}

    fe = pd.read_csv(DATA / "t3-prism-bo-front-evolution.csv")
    out["front_evolution"] = {
        "hv_first": float(fe.iloc[0]["hv_ref_1.35_15mJ"]),
        "hv_last": float(fe.iloc[-1]["hv_ref_1.35_15mJ"]),
        "best_t180_first": float(fe.iloc[0]["best_t180"]),
        "best_t180_last": float(fe.iloc[-1]["best_t180"]),
    }
    return out


def section_noise_ladder(logo: pd.DataFrame, reliability: dict) -> dict:
    """Within-session, ingested-SE, between-print, and between-design scatter
    on one axis per metric."""
    drops = pd.concat([
        pd.read_csv(DATA / f)
        for f in ("t3-prism-bo-batch-drop-results.csv",
                  "t3-prism-bo-round1-drop-results.csv",
                  "t3-prism-bo-round3-drop-results.csv",
                  "t3-prism-bo-round3-reprint-drop-results.csv",
                  "t3-prism-bo-round4-drop-results.csv")
    ], ignore_index=True).set_index("specimen")

    obs_mj = logo[logo.metric == "e_reb_mJ"].set_index("print_id").observed
    scale = obs_mj / drops.e_rebound_mean  # implied m*g*h per article, in mJ
    ladder = {}
    for metric in METRICS:
        d = logo[logo.metric == metric]
        if metric == "t180":
            per_drop_sd = drops.t180_sd
        else:
            per_drop_sd = drops.e_rebound_sd * scale
        design_means = d.groupby("design")["observed"].mean()
        ladder[metric] = {
            "median_within_session_per_drop_sd": float(per_drop_sd.median()),
            "median_ingested_se": float(d.observed_sem.median()),
            "between_print_sd_raw": reliability[metric]["sigma_print_raw"],
            "between_print_sd_excl_drran7": reliability[metric]["sigma_print_excl_drran7"],
            "between_design_sd": float(design_means.std(ddof=1)),
        }

    # exploratory geometry associations across all 44 articles (confounded
    # with design intent; reported only as context for the height-dependent
    # restraint-preload hypothesis)
    keys = pd.concat(
        pd.read_csv(DATA / f"t3-prism-bo-{r}-print-key.csv")[["print_id", "source_trial"]]
        for r in ("round1", "round3", "round4"))
    hm = {}
    for rnd in ("round1", "round3", "round4"):
        pr = pd.read_csv(DATA / f"t3-prism-bo-{rnd}-predictions.csv")
        hm.update(dict(zip(pr.trial_index, pr.H_mm)))
    seed_h = pd.read_csv(DATA / "t3-prism-bo-batch-drop-results.csv").set_index("specimen").H_mm
    trial_of = dict(zip(keys.print_id, keys.source_trial))
    t = logo[logo.metric == "t180"].set_index("print_id")
    e = logo[logo.metric == "e_reb_mJ"].set_index("print_id")
    H = pd.Series({p: hm[trial_of[p]] if p in trial_of else seed_h[p]
                   for p in t.index})
    seed = t[t.batch == "seed"]
    ladder["geometry_associations"] = {
        "spearman_t180_vs_H_all_44": float(stats.spearmanr(t.observed, H[t.index]).statistic),
        "spearman_t180_vs_H_seed_only": float(
            stats.spearmanr(seed.observed, H[seed.index]).statistic),
        "spearman_e_reb_mJ_vs_H_all_44": float(stats.spearmanr(e.observed, H[e.index]).statistic),
    }
    return ladder


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------

def style_axis(ax):
    ax.grid(**GRID)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def scatter_by_batch(ax, d: pd.DataFrame, xcol: str, ycol: str):
    for batch, st in BATCH_STYLE.items():
        sub = d[d.batch == batch]
        if sub.empty:
            continue
        ax.scatter(sub[xcol], sub[ycol], s=46, marker=st["marker"],
                   facecolors=st["color"] if st["filled"] else "none",
                   edgecolors=st["color"], lw=1.4, label=st["label"], zorder=3)


def fig_logo_parity(logo: pd.DataFrame, res: dict):
    fig, axes = plt.subplots(2, 2, figsize=(9.8, 8.8))
    rng = np.random.default_rng(SEED)
    for col, metric in enumerate(METRICS):
        d = logo[logo.metric == metric]
        m = res["logo_article_level"][metric]
        ax = axes[0, col]
        lo = min(d.observed.min(), d.predicted.min())
        hi = max(d.observed.max(), d.predicted.max())
        pad = 0.06 * (hi - lo)
        lims = (lo - pad, hi + pad)
        ax.plot(lims, lims, ls="--", lw=1, color="0.6", zorder=1)
        scatter_by_batch(ax, d, "predicted", "observed")
        ax.set_xlim(lims), ax.set_ylim(lims)
        ax.set_aspect("equal")
        ax.set_xlabel("Held-out prediction")
        ax.set_ylabel("Measured")
        ax.set_title(f"LOGO-CV, {METRIC_LABEL[metric]}", fontsize=11)
        box = (f"$R^2_{{\\rm oos}}$ = {m['R2_oos_vs_fold_train_mean']:+.2f}\n"
               f"$r$ = {m['pearson_r']:+.2f}  ($r^2$ = {m['r_squared_of_r']:.2f})\n"
               f"$\\rho_s$ = {m['spearman_rho']:+.2f}  (p = {m['spearman_p_perm']:.2f})")
        ax.text(0.97, 0.03, box, transform=ax.transAxes, va="bottom", ha="right",
                fontsize=9,
                bbox=dict(facecolor="white", alpha=0.9, edgecolor="0.8", pad=3))
        style_axis(ax)
        if metric == "t180":
            for pid, dx, dy in (("corny7", 8, -4), ("r2d2c3", -40, -3),
                                ("drran7", 8, -2), ("6lhxfy", 8, 0)):
                row = d[d.print_id == pid].iloc[0]
                ax.annotate(pid, (row.predicted, row.observed),
                            textcoords="offset points", xytext=(dx, dy),
                            fontsize=8, color="0.35")

        # permutation null of Spearman rho
        ax = axes[1, col]
        ry = stats.rankdata(d.predicted.values)
        rx = stats.rankdata(d.observed.values)
        null = np.array([
            np.corrcoef(rng.permutation(rx), ry)[0, 1] for _ in range(20_000)])
        color = T180_COLOR if metric == "t180" else REB_COLOR
        ax.hist(null, bins=60, color="0.82", zorder=2)
        ax.axvline(m["spearman_rho"], color=color, lw=2, zorder=3)
        ax.text(m["spearman_rho"], ax.get_ylim()[1] * 0.97,
                f"  observed {m['spearman_rho']:+.2f}\n  p = {m['spearman_p_perm']:.3f}",
                color=color, fontsize=9, va="top",
                ha="left" if m["spearman_rho"] < 0.1 else "right")
        ax.set_xlabel("Spearman rho under shuffled article labels")
        ax.set_ylabel("Permutations")
        ax.set_title("Where the observed rank correlation falls in the null",
                     fontsize=10.5)
        style_axis(ax)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=5, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, 0.975))
    fig.suptitle("Held-out article-level skill: at or below the shuffled-label null",
                 fontsize=12, y=0.998)
    fig.tight_layout(rect=(0, 0, 1, 0.945))
    fig.savefig(FIGS / "logo-parity-and-permutation.png", dpi=200)
    plt.close(fig)


def fig_prospective(pro: pd.DataFrame, res: dict):
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.7), sharey=False)
    for ax, batch in zip(axes, ("r2d2c", "drran", "corny")):
        b = res["prospective"]["batches"][batch]
        d = pro[pro.batch == batch]
        st = BATCH_STYLE[batch]
        ax.errorbar(d.pred_t180_mean, d.meas_t180, xerr=1.96 * d.pred_t180_sd,
                    fmt="none", ecolor="0.8", elinewidth=1.1, zorder=2)
        ax.scatter(d.pred_t180_mean, d.meas_t180, s=52, marker=st["marker"],
                   facecolors=st["color"], edgecolors=st["color"], zorder=4)
        if batch == "drran":
            d2 = pro[pro.batch == "2dran"]
            ax.scatter(d2.pred_t180_mean, d2.meas_t180, s=52, marker="v",
                       facecolors="none", edgecolors=st["color"], lw=1.4,
                       zorder=4, label="2dran re-print")
            for trial in d.source_trial:
                p1 = d[d.source_trial == trial]
                p2 = d2[d2.source_trial == trial]
                ax.plot([p1.pred_t180_mean.iloc[0]] * 2,
                        [p1.meas_t180.iloc[0], p2.meas_t180.iloc[0]],
                        color=st["color"], lw=0.7, alpha=0.5, zorder=3)
            ax.legend(fontsize=8, loc="upper left", framealpha=0.9)
        best = d.loc[d.pred_t180_mean.idxmin()]
        ax.scatter(best.pred_t180_mean, best.meas_t180, s=240, marker="*",
                   facecolors="none", edgecolors="0.2", lw=1.2, zorder=5)
        star_off = {"r2d2c": (-6, -30), "drran": (10, -4), "corny": (10, -16)}[batch]
        ax.annotate(f"best-predicted\nmeasured rank {b['best_predicted_measured_rank_of_9']}/9",
                    (best.pred_t180_mean, best.meas_t180),
                    textcoords="offset points", xytext=star_off, fontsize=8,
                    color="0.3")
        lims = (min(ax.get_xlim()[0], ax.get_ylim()[0]),
                max(ax.get_xlim()[1], ax.get_ylim()[1]))
        ax.plot(lims, lims, ls="--", lw=1, color="0.6", zorder=1)
        ax.set_title(f"{BATCH_STYLE[batch]['label']}\n"
                     f"rho = {b['t180_spearman_rho']:+.2f} (exact p = {b['t180_p_exact_perm']:.2f}), "
                     f"MAPE {b['t180_mape_pct']:.1f}%", fontsize=10)
        ax.set_xlabel("Predicted t180 at selection time")
        style_axis(ax)
    axes[0].set_ylabel("Measured t180")
    fig.suptitle("At-selection predictions vs what each batch then measured "
                 "(bars: 1.96 predicted sd)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(FIGS / "prospective-batch-skill.png", dpi=200)
    plt.close(fig)


def fig_noise_ladder(res: dict):
    ladder = res["noise_ladder"]
    rows = [
        ("Design-to-design spread (35 design means)", "between_design_sd", 1.0),
        ("Between print/seat, all 9 pairs", "between_print_sd_raw", 1.0),
        ("Between print/seat, excl. drran7", "between_print_sd_excl_drran7", 1.0),
        ("SE the surrogate ingested (median)", "median_ingested_se", 1.0),
        ("Per-drop scatter within a session (median)", "median_within_session_per_drop_sd", 1.0),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.2))
    for ax, metric in zip(axes, METRICS):
        vals = [ladder[metric][k] for _, k, _ in rows]
        color = T180_COLOR if metric == "t180" else REB_COLOR
        shades = ["0.55" if i else color for i in (0, 1, 1, 1, 1)]
        y = np.arange(len(rows))[::-1]
        ax.barh(y, vals, height=0.62, color=shades, zorder=3)
        for yi, v in zip(y, vals):
            ax.text(v * 1.12, yi, f"{v:.4g}", va="center", fontsize=8.5,
                    color="0.25")
        ax.set_xscale("log")
        ax.set_yticks(y)
        ax.set_yticklabels([lbl for lbl, _, _ in rows] if metric == "t180" else [])
        ax.set_title(METRIC_LABEL[metric], fontsize=11)
        ax.set_xlabel("Standard deviation (same units as the metric)")
        ax.grid(axis="x", **GRID)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_xlim(min(vals) * 0.5, max(vals) * 4)
    fig.suptitle("The noise ladder: design-to-design signal (colored bar) vs the "
                 "noise rungs (gray) a single-print prediction must climb",
                 fontsize=11.5)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(FIGS / "noise-ladder.png", dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------

def main() -> None:
    FIGS.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    logo = load_logo()
    pro = load_prospective()

    res = {"logo_article_level": section_logo(logo, rng)}
    res["design_level_35"] = section_design_level(logo, rng)
    res["reliability_ceiling"] = section_reliability(logo)
    res["prospective"] = section_prospective(pro, logo, rng)
    res["noise_ladder"] = section_noise_ladder(logo, res["reliability_ceiling"])

    (HERE / "metrics.json").write_text(json.dumps(res, indent=2) + "\n")

    fig_logo_parity(logo, res)
    fig_prospective(pro, res)
    fig_noise_ladder(res)

    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
