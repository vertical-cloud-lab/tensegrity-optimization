"""Simulation outputs as extra model inputs, scored: are the features
correlated with what the bench measured, and does the widened model rank
or quantify its uncertainty any better held out?

PR #111 (sgbaird, 2026-10-13): "see what happens if you bring in
simulation results from PR #33 as additional contextual variables the
model is able to learn and if it improves uncertainty (see the Honegumi
featurization tutorial). Are these correlated?"

Part 1, correlations (no model). The six ``sim_*`` features of
``data/sim-features.csv`` against the four measured objectives (article
level n = 44 and design level n = 35, Spearman with a permutation p),
against the five shape coordinates (Spearman, plus the share of each
feature a linear function of the coordinates explains), against each
other, and against their per-print weighed-mass versions.

Part 2, held out. Every ``data/sim-features-*/`` run written by
``rerun_logocv_sim_features.py`` is graded next to the committed baseline
in the same base space with the same objectives: the audit's standard
scorecard (``cv_signal_audit.held_out_metrics``, within-batch and
design-level Spearman) plus the uncertainty scorecard the question asks
for: 68 and 95 percent coverage, the spread of the standardized errors
(1.0 when the posterior sd is honest), Gaussian negative log likelihood
and CRPS of the held-out observations under the posterior, sharpness
(median posterior sd over the data sd), and whether the posterior sd
orders the absolute errors (Spearman). A run still in flight is graded
on the articles it has reached, with its baseline restricted to the same
articles, and flagged.

Outputs: ``metrics-sim-features.json``,
``figures/sim-features-correlations.png``,
``figures/sim-features-logocv.png``, and a summary on stdout.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import cv_signal_audit as base

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGS = HERE / "figures"
OUT_JSON = HERE / "metrics-sim-features.json"
FEATURES_CSV = DATA / "sim-features.csv"
PAYLOAD_CSV = DATA / "payload-objectives.csv"
CSV_NAME = "t3-prism-bo-round5-logocv.csv"
DIAG_NAME = "t3-prism-bo-round5-logocv-diagnostics.json"

SEED = 20261013
N_PERM = int(os.environ.get("N_PERM", 20_000))
base.N_PERM = N_PERM

FEATURES = ("sim_tierC_t180", "sim_tierC_tendon_energy_mJ",
            "sim_tierC_stroke_mm", "sim_tierB_t180", "sim_tierB_fn_hz",
            "sim_tierB_zeta_pct")
FEAT_LABEL = {"sim_tierC_t180": "Tier C t180",
              "sim_tierC_tendon_energy_mJ": "Tier C tendon energy",
              "sim_tierC_stroke_mm": "Tier C stroke",
              "sim_tierB_t180": "Tier B t180",
              "sim_tierB_fn_hz": "Tier B ringdown fn",
              "sim_tierB_zeta_pct": "Tier B ringdown zeta"}
COORDS = ("R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm")
OBJECTIVES = ("t180", "e_reb_mJ", "tavg10ms", "late_avg3ms_g")
OBJ_LABEL = {"t180": "t180", "e_reb_mJ": "rebound (mJ)",
             "tavg10ms": "tavg10ms", "late_avg3ms_g": "late_avg3ms (G)"}
BATCHES = ("seed", "r2d2c", "drran", "2dran", "corny")

# run directory -> (baseline directory, objectives it carries, label)
RUNS = {
    "sim-features-shape-sim": ("ablation-shape-only", ("t180", "e_reb_mJ"),
                               "shape + sim (11)"),
    "sim-features-twelve-sim": ("full-nuts-rerun", ("t180", "e_reb_mJ"),
                                "12 params + sim (18)"),
    "sim-features-sim-only": ("ablation-shape-only", ("t180", "e_reb_mJ"),
                              "sim only (6)"),
    "sim-features-shape-sim-payload": ("objective-tavg10ms-shape-only",
                                       ("tavg10ms", "late_avg3ms_g"),
                                       "shape + sim (11)"),
    "sim-features-twelve-sim-payload": ("objective-tavg10ms",
                                        ("tavg10ms", "late_avg3ms_g"),
                                        "12 params + sim (18)"),
    "sim-features-sim-only-payload": ("objective-tavg10ms-shape-only",
                                      ("tavg10ms", "late_avg3ms_g"),
                                      "sim only (6)"),
}
BASE_LABEL = {"ablation-shape-only": "shape only (5)",
              "full-nuts-rerun": "12 params",
              "objective-tavg10ms-shape-only": "shape only (5)",
              "objective-tavg10ms": "12 params"}
BASE_COLOR, SIM_COLOR = "#3b6ea5", "#c1553b"


# ------------------------------------------------------------ helpers
def perm_spearman(x, y, rng) -> tuple[float, float]:
    rho, p = base.perm_p_spearman(np.asarray(x, float), np.asarray(y, float), rng)
    return float(rho), float(p)


def residualize(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta


def perm_r(x: np.ndarray, y: np.ndarray, rng) -> tuple[float, float]:
    r = float(np.corrcoef(x, y)[0, 1])
    yp = np.stack([rng.permutation(y) for _ in range(N_PERM)])
    xc = x - x.mean()
    yc = yp - yp.mean(axis=1, keepdims=True)
    null = (yc @ xc) / np.sqrt((yc ** 2).sum(axis=1) * (xc ** 2).sum())
    return r, float((np.sum(np.abs(null) >= abs(r) - 1e-12) + 1) / (N_PERM + 1))


def within_batch_spearman(d: pd.DataFrame, obs_col: str, pred_col: str,
                          rng) -> dict:
    """Mean of the per-batch Spearman rho, with a within-batch shuffle null."""
    per, null = {}, np.zeros(N_PERM)
    batches = [b for b in BATCHES if (d.batch == b).sum() >= 3]
    for b in batches:
        g = d[d.batch == b]
        rx = stats.rankdata(g[obs_col].to_numpy())
        ry = stats.rankdata(g[pred_col].to_numpy())
        per[b] = float(np.corrcoef(rx, ry)[0, 1])
        idx = np.argsort(rng.random((N_PERM, len(ry))), axis=1)
        yp = ry[idx]
        xc = rx - rx.mean()
        yc = yp - yp.mean(axis=1, keepdims=True)
        null += (yc @ xc) / np.sqrt((yc ** 2).sum(axis=1) * (xc ** 2).sum())
    null /= len(batches)
    mean_obs = float(np.mean(list(per.values())))
    p = float((np.sum(np.abs(null) >= abs(mean_obs) - 1e-12) + 1) / (N_PERM + 1))
    return {"per_batch_rho": per, "mean_rho": mean_obs, "perm_p": p}


def uncertainty_metrics(obs: np.ndarray, pred: np.ndarray,
                        psd: np.ndarray) -> dict:
    """How honest and how useful the posterior sd is on held-out articles."""
    resid = obs - pred
    z = resid / psd
    phi, Phi = stats.norm.pdf(z), stats.norm.cdf(z)
    crps = psd * (z * (2 * Phi - 1) + 2 * phi - 1 / np.sqrt(np.pi))
    nll = 0.5 * np.log(2 * np.pi * psd ** 2) + 0.5 * z ** 2
    rho_sd_err = stats.spearmanr(psd, np.abs(resid)).statistic
    # a fold whose NUTS posterior collapsed to a near-deterministic function
    # leaves its articles with a posterior sd far below anything the data
    # support; those articles dominate any mean of z, NLL or CRPS, so the
    # metrics are also reported with them set aside
    sd_obs = obs.std(ddof=1)
    degenerate = psd < 0.05 * sd_obs
    ok = ~degenerate
    return {
        "coverage_68_pct": float(np.mean(np.abs(z) <= 1.0) * 100),
        "coverage_95_pct": float(np.mean(np.abs(z) <= 1.96) * 100),
        "z_sd": float(z.std(ddof=1)),
        "z_rms": float(np.sqrt(np.mean(z ** 2))),
        "mean_nll": float(nll.mean()),
        "median_nll": float(np.median(nll)),
        "mean_crps": float(crps.mean()),
        "crps_over_sd_obs": float(crps.mean() / sd_obs),
        "median_posterior_sd": float(np.median(psd)),
        "sharpness_sd_over_sd_obs": float(np.median(psd) / sd_obs),
        "spearman_sd_vs_abs_error": float(rho_sd_err),
        "n_degenerate_sd": int(degenerate.sum()),
        "degenerate_print_ids_note": "posterior sd below 5 percent of the data sd",
        "excluding_degenerate": {
            "n": int(ok.sum()),
            "coverage_95_pct": float(np.mean(np.abs(z[ok]) <= 1.96) * 100),
            "z_sd": float(z[ok].std(ddof=1)) if ok.sum() > 2 else float("nan"),
            "mean_nll": float(nll[ok].mean()),
            "crps_over_sd_obs": float(crps[ok].mean() / sd_obs),
            "spearman_sd_vs_abs_error": float(
                stats.spearmanr(psd[ok], np.abs(resid[ok])).statistic)
            if ok.sum() > 2 else float("nan"),
        },
    }


def load_run(run_dir: Path, metric: str) -> pd.DataFrame | None:
    """A finished run from its CSV; one in flight from its checkpoint."""
    path = run_dir / CSV_NAME
    partial = False
    if not path.exists():
        folds = run_dir / "folds.jsonl"
        if not folds.exists():
            return None
        rows = []
        for line in folds.read_text().splitlines():
            for art in json.loads(line)["articles"]:
                i = art["observed"]["metric_names"].index(metric)
                j = art["predicted"]["metric_names"].index(metric)
                rows.append({
                    "arm_name": art["arm_name"], "print_id": art["print_id"],
                    "metric": metric,
                    "observed": art["observed"]["means"][i],
                    "observed_sem": art["observed"]["covariance"][i][i] ** 0.5,
                    "predicted": art["predicted"]["means"][j],
                    "predicted_sem": art["predicted"]["covariance"][j][j] ** 0.5})
        if not rows:
            return None
        path = Path("/tmp") / f"{run_dir.name}-{metric}-partial.csv"
        pd.DataFrame(rows).drop_duplicates("print_id").to_csv(path, index=False)
        partial = True
    logo = base.load_logo(path)
    d = logo[logo.metric == metric].copy().reset_index(drop=True)
    d.attrs["partial"] = partial
    assert partial or len(d) == 44, (run_dir, metric, len(d))
    return d


def check_archived(run_dir: Path, metric: str, d: pd.DataFrame) -> bool | None:
    if d.attrs.get("partial"):
        return None
    diag = json.loads((run_dir / DIAG_NAME).read_text())
    r = float(np.corrcoef(d.observed, d.predicted)[0, 1])
    mape = float(np.mean(np.abs(d.observed - d.predicted) / np.abs(d.observed)))
    return bool(abs(r - diag["Correlation coefficient"][metric]) < 1e-4
                and abs(mape - diag["MAPE"][metric]) < 1e-4)


def grade(d: pd.DataFrame, rng) -> dict:
    m = base.held_out_metrics(d.observed.to_numpy(), d.predicted.to_numpy(),
                              d.predicted_sem.to_numpy(), d.design.to_numpy(),
                              rng)
    m["uncertainty"] = uncertainty_metrics(
        d.observed.to_numpy(), d.predicted.to_numpy(), d.predicted_sem.to_numpy())
    m["within_batch"] = within_batch_spearman(d, "observed", "predicted", rng)
    g = d.groupby("design").agg(o=("observed", "mean"), p=("predicted", "mean"),
                                s=("predicted_sem", "mean"))
    dl = base.held_out_metrics(g.o.to_numpy(), g.p.to_numpy(), g.s.to_numpy(),
                               g.index.to_numpy(), rng)
    m["design_level"] = {k: dl[k] for k in ("n", "spearman_rho",
                                            "spearman_p_perm", "pearson_r")}
    # rank skill with the collapsed-fold articles set aside (their
    # predictions are the training mean, so they only add ties and noise)
    ok = d.predicted_sem.to_numpy() >= 0.05 * d.observed.std(ddof=1)
    if ok.sum() >= 8 and ok.sum() < len(d):
        sub = d[ok]
        rho, p = base.perm_p_spearman(sub.observed.to_numpy(),
                                      sub.predicted.to_numpy(), rng)
        wb = within_batch_spearman(sub, "observed", "predicted", rng)
        m["excluding_collapsed"] = {"n": int(ok.sum()), "spearman_rho": float(rho),
                                    "spearman_p_perm": float(p),
                                    "within_batch_mean_rho": wb["mean_rho"],
                                    "within_batch_p": wb["perm_p"],
                                    "collapsed_print_ids": sorted(d[~ok].print_id)}
    return m


# ------------------------------------------------------------ part 1
def article_table() -> pd.DataFrame:
    """One row per LOGO article: objectives, coordinates, features."""
    feats = pd.read_csv(FEATURES_CSV).set_index("print_id")
    camp = base.load_logo(DATA / "ablation-shape-only" / CSV_NAME)
    df = camp[camp.metric == "t180"][["print_id", "batch", "design",
                                      "observed"]].rename(
        columns={"observed": "t180"}).reset_index(drop=True)
    reb = camp[camp.metric == "e_reb_mJ"].set_index("print_id").observed
    df["e_reb_mJ"] = df.print_id.map(reb)
    pay = pd.read_csv(PAYLOAD_CSV).set_index("print_id")
    df["tavg10ms"] = df.print_id.map(pay.tavg10ms_mean)
    df["late_avg3ms_g"] = df.print_id.map(pay.late_avg3ms_g_mean)
    for c in COORDS:
        df[c] = df.print_id.map(feats[f"nom_{c}"])
    df["mass_g"] = df.print_id.map(feats.mass_g)
    for f in FEATURES:
        df[f] = df.print_id.map(feats[f])
        df[f"{f}_weighed"] = df.print_id.map(feats[f"{f}_weighed"])
    assert df.notna().all().all(), df.columns[df.isna().any()]
    assert len(df) == 44
    return df


def correlations(df: pd.DataFrame, rng) -> dict:
    out = {"n_articles": int(len(df)), "n_designs": int(df.design.nunique())}
    des = df.groupby("design").mean(numeric_only=True)
    des["batch"] = df.groupby("design").batch.first()

    vs_obj = {}
    for f in FEATURES:
        ent = {}
        for obj in OBJECTIVES:
            rho_a, p_a = perm_spearman(df[f], df[obj], rng)
            rho_d, p_d = perm_spearman(des[f], des[obj], rng)
            wb = within_batch_spearman(df, obj, f, rng)
            ent[obj] = {"article_rho": rho_a, "article_p": p_a,
                        "design_rho": rho_d, "design_p": p_d,
                        "within_batch_mean_rho": wb["mean_rho"],
                        "within_batch_p": wb["perm_p"]}
        vs_obj[f] = ent
    out["features_vs_objectives"] = vs_obj

    # features vs coordinates: Spearman, linear R2 on the five, and the
    # partial correlation with t180 given the five (does the feature carry
    # anything about the bench beyond the coordinates it was computed from)
    X = np.column_stack([np.ones(len(des))] + [des[c].to_numpy() for c in COORDS])
    vs_coord = {}
    for f in FEATURES:
        y = des[f].to_numpy(dtype=float)
        e = residualize(y, X)
        r2 = float(1 - e.var() / y.var())
        yl = np.log(y) if (y > 0).all() else y
        el = residualize(yl, X)
        r2_log = float(1 - el.var() / yl.var())
        partial = {}
        for obj in ("t180", "tavg10ms"):
            eo = residualize(des[obj].to_numpy(dtype=float), X)
            r, p = perm_r(e, eo, rng)
            partial[obj] = {"partial_r_given_5_coords": r, "perm_p": p}
        vs_coord[f] = {
            "spearman_vs_coord": {c: float(stats.spearmanr(des[f], des[c]).statistic)
                                  for c in COORDS},
            "linear_R2_on_5_coords": r2,
            "linear_R2_on_5_coords_log_feature": r2_log,
            "partial_vs_objective": partial,
            "spearman_vs_weighed_mass_version": float(
                stats.spearmanr(df[f], df[f"{f}_weighed"]).statistic),
            "max_abs_twin_gap_weighed_version_over_design_sd": float(
                max(abs(g[f"{f}_weighed"].iloc[0] - g[f"{f}_weighed"].iloc[1])
                    for _, g in df.groupby("design") if len(g) == 2)
                / des[f].std(ddof=1)),
        }
    out["features_vs_coordinates"] = vs_coord
    out["feature_feature_spearman_design"] = (
        des[list(FEATURES)].corr(method="spearman").round(4).to_dict())
    # the coordinate the bench answers to most, for reference
    out["coords_vs_objectives_design_rho"] = {
        c: {obj: float(stats.spearmanr(des[c], des[obj]).statistic)
            for obj in OBJECTIVES} for c in COORDS}
    return out


# ------------------------------------------------------------ part 2
def heldout(rng) -> dict:
    out = {}
    for run_name, (base_name, objectives, label) in RUNS.items():
        run_dir, base_dir = DATA / run_name, DATA / base_name
        if not (run_dir / "folds.jsonl").exists():
            continue
        ent = {"baseline": base_name, "label": label,
               "baseline_label": BASE_LABEL[base_name], "objectives": {}}
        state_path = run_dir / "state.json"
        if state_path.exists():
            st = json.loads(state_path.read_text())
            ent["status"] = st.get("status")
            ent["n_params"] = st.get("n_params")
            ent["torch_threads"] = st.get("torch_threads")
            ent["folds_done"] = len(st.get("fold_seconds", {}))
        for obj in objectives:
            d_sim = load_run(run_dir, obj)
            d_base = load_run(base_dir, obj)
            if d_sim is None or d_base is None:
                continue
            o = {"n_articles_graded": int(len(d_sim)),
                 "partial": bool(d_sim.attrs["partial"]),
                 "archived_diagnostics_match": check_archived(run_dir, obj, d_sim),
                 "archived_diagnostics_match_baseline":
                     check_archived(base_dir, obj, d_base)}
            if d_sim.attrs["partial"]:
                d_base = d_base[d_base.print_id.isin(d_sim.print_id)].copy()
                d_base = d_base.reset_index(drop=True)
            o["with_sim_features"] = grade(d_sim, rng)
            o["baseline"] = grade(d_base, rng)
            # how far the features moved the held-out predictions
            m = d_sim.merge(d_base, on="print_id", suffixes=("_sim", "_base"))
            o["prediction_shift"] = {
                "spearman_pred_sim_vs_base": float(stats.spearmanr(
                    m.predicted_sim, m.predicted_base).statistic),
                "median_abs_shift_over_sd_obs": float(
                    np.median(np.abs(m.predicted_sim - m.predicted_base))
                    / m.observed_base.std(ddof=1)),
                "median_sd_ratio_sim_over_base": float(np.median(
                    m.predicted_sem_sim / m.predicted_sem_base)),
            }
            ent["objectives"][obj] = o
        out[run_name] = ent
    return out


def baselines_alone(rng) -> dict:
    """The four committed baselines graded on their own, so the collapsed-
    fold count and the rank statistics without those articles are on the
    record for every space the earlier sections leaned on."""
    out = {}
    for base_name in ("ablation-shape-only", "full-nuts-rerun",
                      "objective-tavg10ms-shape-only", "objective-tavg10ms"):
        objectives = (("t180", "e_reb_mJ") if "tavg10ms" not in base_name
                      else ("tavg10ms", "late_avg3ms_g"))
        ent = {}
        for obj in objectives:
            d = load_run(DATA / base_name, obj)
            g = grade(d, rng)
            ent[obj] = {
                "spearman_rho": g["spearman_rho"],
                "spearman_p_perm": g["spearman_p_perm"],
                "within_batch_mean_rho": g["within_batch"]["mean_rho"],
                "within_batch_p": g["within_batch"]["perm_p"],
                "design_rho": g["design_level"]["spearman_rho"],
                "coverage_95_pct": g["uncertainty"]["coverage_95_pct"],
                "n_collapsed": g["uncertainty"]["n_degenerate_sd"],
                "uncertainty_excluding_collapsed":
                    g["uncertainty"]["excluding_degenerate"],
                "excluding_collapsed": g.get("excluding_collapsed"),
            }
        out[base_name] = ent
    return out


# ------------------------------------------------------------ figures
def fig_correlations(df: pd.DataFrame, corr: dict) -> None:
    des = df.groupby("design").mean(numeric_only=True)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6),
                             gridspec_kw={"width_ratios": [1.15, 1]})
    # left: features vs objectives (design level) and vs coordinates
    cols = [OBJ_LABEL[o] for o in OBJECTIVES] + list(COORDS)
    M = np.zeros((len(FEATURES), len(cols)))
    P = np.ones((len(FEATURES), len(cols)))
    for i, f in enumerate(FEATURES):
        for j, obj in enumerate(OBJECTIVES):
            M[i, j] = corr["features_vs_objectives"][f][obj]["design_rho"]
            P[i, j] = corr["features_vs_objectives"][f][obj]["design_p"]
        for j, c in enumerate(COORDS):
            M[i, len(OBJECTIVES) + j] = corr["features_vs_coordinates"][f][
                "spearman_vs_coord"][c]
    ax = axes[0]
    im = ax.imshow(M, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=35, ha="right", fontsize=8.5)
    ax.set_yticks(range(len(FEATURES)))
    ax.set_yticklabels([FEAT_LABEL[f] for f in FEATURES], fontsize=9)
    for i in range(len(FEATURES)):
        for j in range(len(cols)):
            txt = f"{M[i, j]:+.2f}"
            if j < len(OBJECTIVES) and P[i, j] < 0.05:
                txt += "*"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7.6,
                    color="white" if abs(M[i, j]) > 0.55 else "black")
    ax.axvline(len(OBJECTIVES) - 0.5, color="black", lw=1.2)
    ax.set_title("Spearman rho, 35 design means\n"
                 "left of the line: measured objectives (* perm p < 0.05); "
                 "right: the fit coordinates", fontsize=9.5)
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)

    # right: the two transmissibility analogues against measured t180
    ax = axes[1]
    for f, mk, col in (("sim_tierC_t180", "o", "#0072B2"),
                       ("sim_tierB_t180", "s", "#D55E00")):
        rho = corr["features_vs_objectives"][f]["t180"]["design_rho"]
        ax.scatter(des[f], des.t180, s=38, marker=mk, facecolors="none",
                   edgecolors=col, lw=1.3,
                   label=f"{FEAT_LABEL[f]} (rho {rho:+.2f})", zorder=3)
    ax.axhline(1.0, color="0.6", lw=0.8, ls="--", zorder=1)
    ax.set_xlabel("simulated transmissibility analogue (design-mean mass)")
    ax.set_ylabel("measured t180, design mean")
    ax.set_title("The purpose-built analogues vs the bench", fontsize=10)
    ax.legend(fontsize=8, frameon=False)
    base.style_axis(ax)
    fig.suptitle("Simulation features: are they correlated with the bench, "
                 "and with the coordinates they were computed from?",
                 fontsize=11, y=1.02)
    fig.tight_layout()
    FIGS.mkdir(exist_ok=True)
    fig.savefig(FIGS / "sim-features-correlations.png", dpi=160,
                bbox_inches="tight")
    plt.close(fig)


def fig_heldout(res: dict) -> None:
    """Parity with error bars, baseline vs with features, per run and
    objective, plus a scorecard strip."""
    panels = []
    for run_name, ent in res.items():
        for obj, o in ent["objectives"].items():
            panels.append((run_name, ent, obj, o))
    if not panels:
        return
    n = len(panels)
    fig, axes = plt.subplots(n, 2, figsize=(9.2, 3.6 * n), squeeze=False)
    for row, (run_name, ent, obj, o) in enumerate(panels):
        d_sim = load_run(DATA / run_name, obj)
        d_base = load_run(DATA / ent["baseline"], obj)
        d_base = d_base[d_base.print_id.isin(d_sim.print_id)]
        for col, (d, g, title, color) in enumerate((
                (d_base, o["baseline"], ent["baseline_label"], BASE_COLOR),
                (d_sim, o["with_sim_features"], ent["label"], SIM_COLOR))):
            ax = axes[row, col]
            ax.errorbar(d.observed, d.predicted, yerr=1.96 * d.predicted_sem,
                        fmt="none", ecolor=color, alpha=0.35, lw=1, zorder=2)
            base.scatter_by_batch(ax, d, "observed", "predicted")
            lo = min(d.observed.min(), d.predicted.min())
            hi = max(d.observed.max(), d.predicted.max())
            ax.plot([lo, hi], [lo, hi], color="0.5", lw=0.9, zorder=1)
            u = g["uncertainty"]
            ax.set_title(f"{OBJ_LABEL[obj]}: {title}"
                         + (" (partial)" if o["partial"] else ""), fontsize=10)
            ax.text(0.02, 0.98,
                    f"rho_s {g['spearman_rho']:+.2f} (p {g['spearman_p_perm']:.3f})\n"
                    f"within batch {g['within_batch']['mean_rho']:+.2f}\n"
                    f"95% cov {u['coverage_95_pct']:.0f}%, z sd {u['excluding_degenerate']['z_sd']:.2f}*\n"
                    f"NLL {u['excluding_degenerate']['mean_nll']:+.2f}*, CRPS/sd {u['crps_over_sd_obs']:.2f}\n"
                    f"post sd / data sd {u['sharpness_sd_over_sd_obs']:.2f}; "
                    f"{u['n_degenerate_sd']} collapsed",
                    transform=ax.transAxes, va="top", fontsize=7.8,
                    bbox=dict(boxstyle="round", fc="white", ec="0.8", alpha=0.9))
            ax.set_xlabel("measured (held out)")
            ax.set_ylabel("predicted, 95% band")
            base.style_axis(ax)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=8,
               frameon=False, bbox_to_anchor=(0.5, -0.012))
    fig.suptitle("LOGO-CV (256/512 NUTS, same 35 folds): base space vs base "
                 "space + six simulation features", fontsize=11, y=1.0)
    fig.tight_layout(rect=(0, 0.02, 1, 0.99))
    fig.savefig(FIGS / "sim-features-logocv.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------ main
def main() -> None:
    rng = np.random.default_rng(SEED)
    df = article_table()
    corr = correlations(df, rng)
    res = heldout(rng)
    out = {"seed": SEED, "n_perm": N_PERM, "features": list(FEATURES),
           "correlations": corr, "heldout": res,
           "baselines_alone": baselines_alone(rng)}
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n")
    fig_correlations(df, corr)
    fig_heldout(res)

    print("features vs measured objectives, design level (rho, p):")
    for f in FEATURES:
        row = "  ".join(f"{obj} {corr['features_vs_objectives'][f][obj]['design_rho']:+.2f}"
                        f" ({corr['features_vs_objectives'][f][obj]['design_p']:.3f})"
                        for obj in OBJECTIVES)
        r2 = corr["features_vs_coordinates"][f]["linear_R2_on_5_coords"]
        pr = corr["features_vs_coordinates"][f]["partial_vs_objective"]["t180"]
        print(f"  {f:28s} {row} | R2 on coords {r2:.2f} | partial vs t180 "
              f"{pr['partial_r_given_5_coords']:+.2f} (p {pr['perm_p']:.2f})")
    for run_name, ent in res.items():
        print(f"\n{run_name} vs {ent['baseline']} "
              f"[{ent.get('status')}, {ent.get('folds_done')} folds]")
        for obj, o in ent["objectives"].items():
            for tag in ("baseline", "with_sim_features"):
                g = o[tag]
                u = g["uncertainty"]
                print(f"  {obj:14s} {tag:18s} n {g['n']:2d} rho_s {g['spearman_rho']:+.2f} "
                      f"(p {g['spearman_p_perm']:.3f}) within {g['within_batch']['mean_rho']:+.2f} "
                      f"design {g['design_level']['spearman_rho']:+.2f} "
                      f"R2oos {g['R2_oos_vs_fold_train_mean']:+.2f} | cov95 "
                      f"{u['coverage_95_pct']:.0f}% z_sd {u['z_sd']:.2f} NLL {u['mean_nll']:+.2f} "
                      f"CRPS/sd {u['crps_over_sd_obs']:.2f} sharp {u['sharpness_sd_over_sd_obs']:.2f} "
                      f"sd~|err| {u['spearman_sd_vs_abs_error']:+.2f} | degenerate {u['n_degenerate_sd']}: "
                      f"cov95 {u['excluding_degenerate']['coverage_95_pct']:.0f}% "
                      f"z_sd {u['excluding_degenerate']['z_sd']:.2f} NLL {u['excluding_degenerate']['mean_nll']:+.2f}")
            s = o["prediction_shift"]
            print(f"  {'':14s} shift: rank agreement {s['spearman_pred_sim_vs_base']:+.2f}, "
                  f"median |shift|/sd {s['median_abs_shift_over_sd_obs']:.2f}, "
                  f"sd ratio {s['median_sd_ratio_sim_over_base']:.2f}; archived match "
                  f"{o['archived_diagnostics_match']} / {o['archived_diagnostics_match_baseline']}")
    print(f"\nwrote {OUT_JSON}")


if __name__ == "__main__":
    main()
