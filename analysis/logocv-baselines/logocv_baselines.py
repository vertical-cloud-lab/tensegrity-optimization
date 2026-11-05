"""LOGO-CV baselines and feature-set comparison for the round-5 surrogate.

PR #121 follow-up (sgbaird, 2026-11-05): "Perform LOGO-CV with 256/512, with
only the 6 (?) original parameters, not the additional print parameters, and
both with and without the simulations as contextual features, and for both
objectives. Show the same figures for the dummy cases of: 'predict everything
as the mean', using a hyperparameter-tuned RFR or similar model, etc."

The Ax SAASBO runs come from ``data/ax-runs/`` (vendored from the audit
branch ``claude/cv-signal-audit-20260922`` at ``6964ac2``) and
``data/ax-six-sim/`` (this branch, ``rerun_logocv_six_param_sim.py``). All
of them use the same protocol: the campaign's round-5 snapshot, one NUTS
refit per design fold at 256 samples / 512 warmup, reprint pairs held out
together, 35 folds over 44 articles.

This script

1. builds ``data/article-features.csv``: one row per article with the twelve
   campaign parameters (from the full-NUTS checkpoint, so they are exactly
   what Ax fitted), the six simulation features (``data/sim-features.csv``),
   the print session, the design fold key and the observed objective means
   and SEMs;
2. fits scikit-learn baselines under the identical leave-one-design-out
   protocol (same 35 folds, same observed values, same held-out articles),
   for a chosen set of feature spaces, and writes each as a CSV in the
   campaign's ``t3-prism-bo-round5-logocv.csv`` layout
   (``data/baselines/<model>-<space>.csv``);
3. scores every run (Ax and baseline) with one scorecard
   (``scores.json``, ``scores.csv``, ``scores.md``);
4. draws the SI figure (``scripts/figures/plot_logocv.py`` style, two parity
   panels) for every run (``figures/logocv-<run>.png``) and one comparison
   grid per objective (``figures/logocv-grid-<objective>.png``).

Baselines (every one fitted on the fold's training articles only, with any
hyperparameter chosen by an inner 5-fold GroupKFold over the training
designs, so nothing about the held-out design leaks in):

- ``mean``: the training mean. Its "sem" is the training sd, i.e. the
  predictive sd of a model that knows nothing about the design.
- ``session-mean``: the training mean of the held-out article's own print
  session (seed, r2d2c, drran, 2dran, corny). This is an oracle for the
  between-session calibration offsets, not a model any fit had access to
  (the twelve-parameter space can separate only three process points).
  Its "sem" is the within-session training sd.
- ``ridge``: standardized linear ridge regression, alpha tuned over
  10^-3 to 10^3.
- ``knn``: standardized k-nearest neighbours, k in {1, 2, 3, 5, 7, 10},
  uniform or distance weights.
- ``rf``: random forest, 200 trees, tuned over max_features {0.33, 0.67,
  1.0}, min_samples_leaf {1, 3} and max_depth {None, 4} (12 configurations).
- ``gp``: a Gaussian process with an ARD Matern-5/2 kernel plus a white
  noise term, hyperparameters by marginal likelihood (type-II ML) with
  restarts. The non-sparse, non-Bayesian counterpart of SAASBO.

For ``ridge``, ``knn`` and ``rf`` the reported ``predicted_sem`` is the
inner-CV RMSE of the selected configuration (a constant per fold: the model's
typical out-of-sample error, which is what a parity error bar should show
for a point predictor). ``gp`` reports its own predictive sd with the fitted
noise level removed, which is what Ax's ``predicted_sem`` is for SAASBO.

Scorecard per (run, objective): n, MAPE, RMSE, R2_oos (1 - SSE / SSE of the
per-fold training mean, so the ``mean`` baseline scores exactly 0), Spearman
rho_s with a two-sided permutation p (20,000 shuffles, seed 0, the
``plot_logocv.py`` recipe), Pearson r, design-level rho_s over the 35 design
means, prediction spread / data sd, and 1.96-sd coverage.

Usage (repo root)::

    python analysis/logocv-baselines/logocv_baselines.py --build-table
    python analysis/logocv-baselines/logocv_baselines.py --fit --spaces six six-sim twelve
    python analysis/logocv-baselines/logocv_baselines.py --score --plot
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = HERE / "data"
FIGS = HERE / "figures"
BASE_DIR = DATA / "baselines"
TABLE_CSV = DATA / "article-features.csv"
SIM_CSV = DATA / "sim-features.csv"
FULLNUTS = DATA / "ax-runs" / "full-nuts-rerun"
MANUSCRIPT_LOGO = ROOT / "manuscript" / "data" / "t3-prism-bo-round5-logocv.csv"

sys.path.insert(0, str(ROOT / "scripts" / "figures"))
import plot_logocv as pl  # noqa: E402  (the SI figure code)

METRICS = ("t180", "e_reb_mJ")
SHAPE = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]
MASS = ["mass_printed_g"]
PROCESS = ["strut_infill_pct", "tpu_infill_pct", "pla_nozzle_temp_C",
           "pla_flow_mm3_s", "tpu_nozzle_temp_C", "tpu_flow_mm3_s"]
SIM = ["sim_tierC_t180", "sim_tierC_tendon_energy_mJ", "sim_tierC_stroke_mm",
       "sim_tierB_t180", "sim_tierB_fn_hz", "sim_tierB_zeta_pct"]
SPACES = {
    "shape": SHAPE,
    "six": SHAPE + MASS,
    "twelve": SHAPE + MASS + PROCESS,
    "shape-sim": SHAPE + SIM,
    "six-sim": SHAPE + MASS + SIM,
    "twelve-sim": SHAPE + MASS + PROCESS + SIM,
    "sim-only": SIM,
}
SPACE_LABEL = {
    "shape": "5 shape coordinates",
    "six": "6 original parameters (shape + mass)",
    "twelve": "12 campaign parameters",
    "shape-sim": "5 shape + 6 sim features",
    "six-sim": "6 original + 6 sim features",
    "twelve-sim": "12 campaign + 6 sim features",
    "sim-only": "6 sim features only",
}
# Ax SAASBO runs, by feature space
AX_RUNS = {
    "shape": DATA / "ax-runs" / "ablation-shape-only",
    "six": DATA / "ax-runs" / "ablation-six-param",
    "twelve": FULLNUTS,
    "shape-sim": DATA / "ax-runs" / "sim-features-shape-sim",
    "six-sim": DATA / "ax-six-sim",
    "twelve-sim": DATA / "ax-runs" / "sim-features-twelve-sim",
    "sim-only": DATA / "ax-runs" / "sim-features-sim-only",
}
MODELS = ("mean", "session-mean", "ridge", "knn", "rf", "gp")
MODEL_LABEL = {
    "saasbo": "SAASBO (Ax, 256/512)",
    "mean": "training mean",
    "session-mean": "print-session mean",
    "ridge": "ridge (linear)",
    "knn": "k-nearest neighbours",
    "rf": "random forest (tuned)",
    "gp": "GP, ARD Matern (ML-II)",
}
N_PERM = 20000
SEED = 0


# ---------------------------------------------------------------- table
def build_table() -> pd.DataFrame:
    """One row per article: fold key, session, 12 parameters, 6 sim features,
    observed means and SEMs for both objectives. Parameters and observations
    are read from the full-NUTS checkpoint so they are exactly what Ax saw."""
    rows = []
    for line in (FULLNUTS / "folds.jsonl").read_text().splitlines():
        rec = json.loads(line)
        for art in rec["articles"]:
            row = {"print_id": art["print_id"], "arm_name": art["arm_name"],
                   "design": rec["fold_key"], "fold_index": rec["fold_index"]}
            row.update({k: float(v) for k, v in art["parameters"].items()})
            names = art["observed"]["metric_names"]
            for i, m in enumerate(names):
                row[f"{m}_obs"] = float(art["observed"]["means"][i])
                row[f"{m}_sem"] = float(art["observed"]["covariance"][i][i]) ** 0.5
            rows.append(row)
    t = pd.DataFrame(rows)
    assert len(t) == 44 and t.design.nunique() == 35, (len(t), t.design.nunique())
    sim = pd.read_csv(SIM_CSV).set_index("print_id")
    missing = [p for p in t.print_id if p not in sim.index]
    assert not missing, f"articles without simulation features: {missing}"
    for c in SIM:
        t[c] = t.print_id.map(sim[c]).astype(float)
    t["session"] = t.print_id.map(sim["batch"])
    assert t.session.notna().all()
    # reprint twins must share every simulation feature (design-mean mass)
    for d, g in t.groupby("design"):
        if len(g) > 1:
            assert np.allclose(g[SIM].to_numpy()[0], g[SIM].to_numpy()), d
    # the observed values must be the manuscript's LOGO file
    ref = pd.read_csv(MANUSCRIPT_LOGO)
    for m in METRICS:
        r = ref[ref.metric == m].set_index("print_id")
        assert np.allclose(t.set_index("print_id")[f"{m}_obs"].reindex(r.index), r.observed, atol=1e-5), m
    cols = (["print_id", "arm_name", "design", "fold_index", "session"]
            + SHAPE + MASS + PROCESS + SIM
            + [f"{m}_{s}" for m in METRICS for s in ("obs", "sem")])
    t = t[cols].sort_values("fold_index", kind="stable").reset_index(drop=True)
    t.to_csv(TABLE_CSV, index=False, float_format="%.10g")
    print(f"wrote {TABLE_CSV.relative_to(ROOT)}: {len(t)} articles, "
          f"{t.design.nunique()} designs, {t.session.nunique()} sessions")
    return t


def load_table() -> pd.DataFrame:
    return pd.read_csv(TABLE_CSV) if TABLE_CSV.exists() else build_table()


# ---------------------------------------------------------------- models
def _inner_cv(X, y, groups, make, grid, n_splits=5):
    """Pick the grid point with the lowest inner GroupKFold RMSE; return it,
    its inner RMSE, and the inner-CV predictions."""
    from sklearn.model_selection import GroupKFold

    gkf = GroupKFold(n_splits=min(n_splits, len(set(groups))))
    best = None
    for params in grid:
        pred = np.full(len(y), np.nan)
        for tr, te in gkf.split(X, y, groups):
            est = make(**params)
            est.fit(X[tr], y[tr])
            pred[te] = est.predict(X[te])
        rmse = float(np.sqrt(np.mean((pred - y) ** 2)))
        if best is None or rmse < best[1]:
            best = (params, rmse, pred)
    return best


def _grid(**kw):
    import itertools

    keys = list(kw)
    return [dict(zip(keys, vals)) for vals in itertools.product(*kw.values())]


def fit_predict(model: str, Xtr, ytr, gtr, str_tr, Xte, str_te, seed=SEED):
    """Fit one baseline on the training articles, predict the held-out ones.
    Returns (pred, sem, info)."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import Ridge
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    n_te = len(Xte)
    if model == "mean":
        mu, sd = float(np.mean(ytr)), float(np.std(ytr, ddof=1))
        return np.full(n_te, mu), np.full(n_te, sd), {}
    if model == "session-mean":
        pred, sem = np.empty(n_te), np.empty(n_te)
        for i, s in enumerate(str_te):
            same = ytr[str_tr == s]
            assert len(same) >= 2, s
            pred[i], sem[i] = np.mean(same), np.std(same, ddof=1)
        return pred, sem, {}
    if model == "ridge":
        make = lambda alpha: make_pipeline(StandardScaler(), Ridge(alpha=alpha))  # noqa: E731
        grid = _grid(alpha=list(np.logspace(-3, 3, 13)))
    elif model == "knn":
        make = lambda n_neighbors, weights: make_pipeline(  # noqa: E731
            StandardScaler(), KNeighborsRegressor(n_neighbors=n_neighbors, weights=weights))
        grid = _grid(n_neighbors=[1, 2, 3, 5, 7, 10], weights=["uniform", "distance"])
    elif model == "rf":
        make = lambda max_features, min_samples_leaf, max_depth: RandomForestRegressor(  # noqa: E731
            n_estimators=200, max_features=max_features, min_samples_leaf=min_samples_leaf,
            max_depth=max_depth, random_state=seed, n_jobs=1)
        grid = _grid(max_features=[0.33, 0.67, 1.0], min_samples_leaf=[1, 3],
                     max_depth=[None, 4])
    elif model == "gp":
        return _fit_gp(Xtr, ytr, Xte, seed)
    else:
        raise ValueError(model)
    params, inner_rmse, _ = _inner_cv(Xtr, ytr, gtr, make, grid)
    est = make(**params)
    est.fit(Xtr, ytr)
    return est.predict(Xte), np.full(n_te, inner_rmse), {"params": params, "inner_rmse": inner_rmse}


def _fit_gp(Xtr, ytr, Xte, seed):
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
    from sklearn.preprocessing import StandardScaler

    sc = StandardScaler().fit(Xtr)
    Xs, Xt = sc.transform(Xtr), sc.transform(Xte)
    d = Xs.shape[1]
    kernel = (ConstantKernel(1.0, (1e-2, 1e2))
              * Matern(length_scale=np.ones(d), length_scale_bounds=(1e-1, 1e2), nu=2.5)
              + WhiteKernel(noise_level=0.1, noise_level_bounds=(1e-4, 1e1)))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True,
                                      n_restarts_optimizer=4, random_state=seed)
        gp.fit(Xs, ytr)
        mu, sd_y = gp.predict(Xt, return_std=True)
    # sklearn's predictive variance includes the white-noise term; Ax's
    # predicted_sem for SAASBO excludes observation noise. Remove it (in y
    # units: the kernel is fitted on standardized y).
    noise = float(gp.kernel_.k2.noise_level) * float(gp._y_train_std ** 2)
    sd_f = np.sqrt(np.maximum(sd_y ** 2 - noise, 1e-12))
    return mu, sd_f, {"kernel": str(gp.kernel_), "lml": float(gp.log_marginal_likelihood_value_)}


def run_baseline(model: str, space: str, table: pd.DataFrame) -> pd.DataFrame:
    """Leave-one-design-out predictions for one model in one feature space,
    in the campaign's LOGO CSV layout."""
    cols = SPACES[space]
    X = table[cols].to_numpy(float)
    groups = table.design.to_numpy()
    sessions = table.session.to_numpy()
    rows, info = [], {}
    t0 = time.time()
    for design in dict.fromkeys(groups):          # canonical fold order
        te = groups == design
        tr = ~te
        for m in METRICS:
            y = table[f"{m}_obs"].to_numpy(float)
            pred, sem, inf = fit_predict(model, X[tr], y[tr], groups[tr],
                                         sessions[tr], X[te], sessions[te])
            info[f"{design}/{m}"] = inf
            for i, idx in enumerate(np.flatnonzero(te)):
                rows.append({
                    "arm_name": table.arm_name[idx], "print_id": table.print_id[idx],
                    "metric": m, "observed": y[idx],
                    "observed_sem": table[f"{m}_sem"][idx],
                    "predicted": float(pred[i]), "predicted_sem": float(sem[i]),
                })
    out = pd.DataFrame(rows)
    assert len(out) == 88
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(BASE_DIR / f"{model}-{space}.csv", index=False, float_format="%.9g")
    (BASE_DIR / f"{model}-{space}-fits.json").write_text(json.dumps(info, indent=1, default=str) + "\n")
    print(f"  {model:13s} {space:11s} {time.time() - t0:6.0f} s", flush=True)
    return out


# ---------------------------------------------------------------- scores
def load_run(space: str, model: str) -> pd.DataFrame | None:
    if model == "saasbo":
        path = AX_RUNS[space] / "t3-prism-bo-round5-logocv.csv"
    else:
        path = BASE_DIR / f"{model}-{space}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    assert len(df) == 88, path
    return df


def perm_p_spearman(o, p, rng, n_perm=N_PERM) -> float:
    """Two-sided permutation p for Spearman's rho: shuffle the predictions,
    Pearson on average ranks (identical to scipy.stats.spearmanr, ties
    included), vectorized over the shuffles."""
    rx, ry = stats.rankdata(o), stats.rankdata(p)
    rho = np.corrcoef(rx, ry)[0, 1]
    idx = np.argsort(rng.random((n_perm, len(ry))), axis=1)
    yp = ry[idx]
    xc = rx - rx.mean()
    yc = yp - yp.mean(axis=1, keepdims=True)
    null = (yc @ xc) / np.sqrt((yc ** 2).sum(axis=1) * (xc ** 2).sum())
    return float((np.sum(np.abs(null) >= abs(rho) - 1e-12) + 1) / (n_perm + 1))


def score(df: pd.DataFrame, table: pd.DataFrame, metric: str, rng) -> dict:
    sub = df[df.metric == metric].set_index("print_id").reindex(table.print_id)
    o, p, s = sub.observed.to_numpy(), sub.predicted.to_numpy(), sub.predicted_sem.to_numpy()
    design = table.design.to_numpy()
    # the per-fold training mean (what the `mean` baseline predicts)
    mean_pred = np.array([o[design != d].mean() for d in design])
    rho, p_asym = stats.spearmanr(o, p)
    p_perm = perm_p_spearman(o, p, rng)
    g = pd.DataFrame({"o": o, "p": p, "d": design}).groupby("d").mean()
    rho_d, p_d = stats.spearmanr(g.o, g.p)
    return {
        "n": int(len(o)),
        "MAPE": float(np.mean(np.abs((o - p) / o))),
        "RMSE": float(np.sqrt(np.mean((o - p) ** 2))),
        "R2_oos_vs_fold_mean": float(1 - np.sum((o - p) ** 2) / np.sum((o - mean_pred) ** 2)),
        "spearman_rho": float(rho),
        "spearman_p_perm_two_sided": float(p_perm),
        "spearman_p_asymptotic": float(p_asym),
        "pearson_r": float(stats.pearsonr(o, p)[0]),
        "design_mean_spearman_rho": float(rho_d),
        "design_mean_spearman_p_asymptotic": float(p_d),
        "sd_pred_over_sd_obs": float(np.std(p) / np.std(o)),
        "coverage_1p96sd": float(np.mean(np.abs(o - p) <= 1.96 * s)),
        "median_predicted_sem": float(np.median(s)),
    }


def score_all(table: pd.DataFrame, spaces) -> dict:
    out = {}
    for space in spaces:
        for model in ("saasbo",) + MODELS:
            df = load_run(space, model)
            if df is None:
                continue
            rng = np.random.default_rng(SEED)
            out[f"{model}-{space}"] = {
                "model": model, "space": space, "n_features": len(SPACES[space]),
                **{m: score(df, table, m, rng) for m in METRICS},
            }
    (HERE / "scores.json").write_text(json.dumps(out, indent=2) + "\n")
    flat = []
    for run, r in out.items():
        for m in METRICS:
            flat.append({"run": run, "model": r["model"], "space": r["space"],
                         "n_features": r["n_features"], "metric": m, **r[m]})
    pd.DataFrame(flat).to_csv(HERE / "scores.csv", index=False, float_format="%.4g")
    write_markdown(out, spaces)
    summarize_gp(spaces)
    return out


def summarize_gp(spaces) -> dict:
    """Median fitted ARD lengthscale per input (standardized units) across
    the 35 folds of each GP baseline, and how often it sat at the 100 upper
    bound (= the input switched off). Written to data/baselines/gp-lengthscales.json."""
    import re

    out = {}
    for space in spaces:
        path = BASE_DIR / f"gp-{space}-fits.json"
        if not path.exists():
            continue
        fits = json.loads(path.read_text())
        cols = SPACES[space]
        for m in METRICS:
            ls, noise = [], []
            for key, v in fits.items():
                if key.endswith("/" + m):
                    k = v["kernel"]
                    ls.append([float(x) for x in re.search(r"length_scale=\[([^\]]+)\]", k).group(1).split(",")])
                    noise.append(float(re.search(r"noise_level=([0-9.e+-]+)", k).group(1)))
            ls = np.array(ls)
            out[f"gp-{space}/{m}"] = {
                "n_folds": int(len(ls)),
                "median_lengthscale": dict(zip(cols, np.round(np.median(ls, axis=0), 3).tolist())),
                "share_at_upper_bound": dict(zip(cols, np.round((ls >= 99).mean(axis=0), 2).tolist())),
                "median_noise_level_normalized": float(np.median(noise)),
            }
    (BASE_DIR / "gp-lengthscales.json").write_text(json.dumps(out, indent=2) + "\n")
    return out


def _fmt_p(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def write_markdown(out: dict, spaces) -> None:
    lines = []
    for m, label in (("t180", "t180 (transmissibility)"), ("e_reb_mJ", "E_reb (mJ per drop)")):
        lines += [f"### {label}, held out over 35 design folds (44 articles)", "",
                  "| feature space | model | MAPE | RMSE | R2_oos | rho_s (perm p) | design-mean rho_s | r | spread / data sd | 95% cov |",
                  "|---|---|--:|--:|--:|--:|--:|--:|--:|--:|"]
        for space in spaces:
            for model in ("saasbo",) + MODELS:
                r = out.get(f"{model}-{space}")
                if r is None:
                    continue
                s = r[m]
                lines.append(
                    f"| {SPACE_LABEL[space]} | {MODEL_LABEL[model]} | {100 * s['MAPE']:.1f}% | "
                    f"{s['RMSE']:.3g} | {s['R2_oos_vs_fold_mean']:+.2f} | "
                    f"{s['spearman_rho']:+.2f} ({_fmt_p(s['spearman_p_perm_two_sided'])}) | "
                    f"{s['design_mean_spearman_rho']:+.2f} | {s['pearson_r']:+.2f} | "
                    f"{s['sd_pred_over_sd_obs']:.2f} | {100 * s['coverage_1p96sd']:.0f}% |")
        lines.append("")
    (HERE / "scores.md").write_text("\n".join(lines))


# ---------------------------------------------------------------- figures
def plot_run(space: str, model: str, table: pd.DataFrame, scores: dict) -> Path | None:
    df = load_run(space, model)
    if df is None:
        return None
    FIGS.mkdir(parents=True, exist_ok=True)
    out = FIGS / f"logocv-{model}-{space}.png"
    s = scores[f"{model}-{space}"]
    pl.plot(df, {m: s[m] for m in METRICS}, out)
    return out


def plot_grid(spaces, models, table: pd.DataFrame, scores: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIGS.mkdir(parents=True, exist_ok=True)
    for metric in METRICS:
        with plt.rc_context({**pl.RC, "font.size": 11, "xtick.labelsize": 9, "ytick.labelsize": 9}):
            nr, nc = len(spaces), len(models)
            fig, axes = plt.subplots(nr, nc, figsize=(2.6 * nc, 2.75 * nr), dpi=200, squeeze=False)
            runs = {(sp, mo): load_run(sp, mo) for sp in spaces for mo in models}
            vals = [v[v.metric == metric][["observed", "predicted"]].to_numpy().ravel()
                    for v in runs.values() if v is not None]
            lo, hi = float(np.min(np.concatenate(vals))), float(np.max(np.concatenate(vals)))
            pad = 0.08 * (hi - lo)
            lim = (lo - pad, hi + pad)
            for i, sp in enumerate(spaces):
                for j, mo in enumerate(models):
                    ax = axes[i, j]
                    df = runs[(sp, mo)]
                    for side in ("top", "right"):
                        ax.spines[side].set_visible(False)
                    ax.plot(lim, lim, color=pl.GRAY, lw=1.0, ls=(0, (5, 5)), zorder=1)
                    ax.set_xlim(*lim)
                    ax.set_ylim(*lim)
                    ax.set_aspect("equal", adjustable="box")
                    if i == 0:
                        ax.set_title(MODEL_LABEL[mo], fontsize=10.5, pad=8)
                    if j == 0:
                        ax.set_ylabel(SPACE_LABEL[sp].replace(" (", "\n("), fontsize=10)
                    if i == nr - 1:
                        ax.set_xlabel("Measured", fontsize=10)
                    ax.tick_params(labelbottom=(i == nr - 1), labelleft=(j == 0))
                    if df is None:
                        ax.text(0.5, 0.5, "not run", transform=ax.transAxes, ha="center",
                                va="center", color=pl.GRAY, fontsize=10)
                        continue
                    sub = df[df.metric == metric]
                    ax.errorbar(sub.observed, sub.predicted, yerr=sub.predicted_sem, fmt="o",
                                ms=4.5, mfc="none", mec=pl.COLOR[metric], mew=1.1,
                                ecolor=pl.COLOR[metric], elinewidth=0.6, capsize=0, alpha=0.85,
                                zorder=3)
                    s = scores[f"{mo}-{sp}"][metric]
                    ax.text(0.97, 0.03, (f"MAPE {100 * s['MAPE']:.1f}%\n"
                                         + r"$\rho_s$" + f" = {s['spearman_rho']:+.2f}").replace("-", "−"),
                            transform=ax.transAxes, ha="right", va="bottom", fontsize=9)
            fig.suptitle(pl.TITLE[metric] + ": held-out predictions, 35 design folds, 44 articles",
                         fontsize=12, y=1.0)
            fig.supylabel("Predicted", fontsize=11, x=0.004)
            fig.tight_layout()
            out = FIGS / f"logocv-grid-{metric}.png"
            fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
            plt.close(fig)
            print(f"wrote {out.relative_to(ROOT)}")


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--build-table", action="store_true")
    ap.add_argument("--fit", action="store_true", help="run the baselines")
    ap.add_argument("--models", nargs="*", default=list(MODELS), choices=MODELS)
    ap.add_argument("--spaces", nargs="*", default=["six", "six-sim", "twelve"],
                    choices=list(SPACES))
    ap.add_argument("--force", action="store_true", help="refit baselines that already have a CSV")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--plot", action="store_true")
    ap.add_argument("--grid-models", nargs="*", default=["saasbo", "mean", "session-mean", "ridge", "knn", "rf", "gp"])
    args = ap.parse_args(argv)

    table = build_table() if args.build_table or not TABLE_CSV.exists() else load_table()
    if args.fit:
        for space in args.spaces:
            for model in args.models:
                if (BASE_DIR / f"{model}-{space}.csv").exists() and not args.force:
                    print(f"  {model:13s} {space:11s} (cached)")
                    continue
                run_baseline(model, space, table)
    scores = None
    if args.score or args.plot:
        scores = score_all(table, args.spaces)
        print((HERE / "scores.md").read_text())
    if args.plot:
        for space in args.spaces:
            for model in ("saasbo",) + MODELS:
                p = plot_run(space, model, table, scores)
                if p is not None:
                    print(f"wrote {p.relative_to(ROOT)}")
        plot_grid(args.spaces, args.grid_models, table, scores)


if __name__ == "__main__":
    main()
