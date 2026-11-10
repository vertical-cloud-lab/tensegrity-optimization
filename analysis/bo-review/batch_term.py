"""Batch (print-session) terms in the surrogate: LOGO and leave-one-batch-out.

PR #121 (sgbaird, 2026-11-10), item 4 of Juan Florez-Coronel's review:
"Filament settings change only between batches, so the GP sees any batch
difference (spool, humidity, test sessions) as a filament effect. Would you
drop those four parameters from the model, or add a batch term, until an
experiment varies them on purpose?" and sgbaird: "I wonder if this would be
a case for using batch number as part of the search space. Attempt and
explore this."

The 44 articles come from five print sessions (``session`` in
``article-features.csv``): the seed batch, r2d2c (batch 2), drran (batch 3),
2dran (batch 3 reprinted) and corny (batch 4). The four filament settings
take four distinct values, one per session, with the seed and r2d2c
sessions sharing one, so they are session labels.

Models (all BoTorch ``SingleTaskGP``, MAP, noise learned, inputs normalized
to the campaign bounds, outputs standardized inside the fold):

* ``none``: the design inputs only (``six``, ``eight`` = six plus the two
  per-article infill densities, ``twelve`` = the campaign space).
* ``ri``: plus an additive random intercept per session, a ``LinearKernel``
  on one-hot session columns (k = v * [same session]). A held-out article
  from a known session borrows its session's offset; an article from a new
  session gets the design prediction with v added to its variance.
* ``ord``: plus the session's print order (1 to 5) as one more continuous
  input under the same ARD kernel, i.e. "batch number as part of the search
  space". A new batch is an extrapolation along that axis.

Two cross-validations:

* LOGO: the 35 design folds of every run in this PR (twins held out
  together). Every held-out article's session is in the training data.
* LOBO: leave one session out (5 folds), the situation of a new batch.
  When drran is held out its reprint 2dran is in training and vice versa,
  so those two folds test "same designs, new print session".

Usage (BoFire venv)::

    python analysis/bo-review/batch_term.py
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "logocv-baselines"))
from logocv_bofire import METRICS, bounds_for  # noqa: E402
from logocv_noise_models import ALL_SPACES, load_table, permutation_p  # noqa: E402

OUT = HERE / "data" / "batch-term"
SESSIONS = ["seed", "r2d2c", "drran", "2dran", "corny"]   # print order
SPACES = ["six", "eight", "twelve"]
TERMS = ["none", "ri", "ord"]


def design_matrix(t, space, term):
    cols = ALL_SPACES[space]
    b = bounds_for(cols)
    X = t[cols].to_numpy(dtype=float)
    lo = [b[c][0] for c in cols]
    hi = [b[c][1] for c in cols]
    if term == "ri":
        oh = np.column_stack([(t.session == s).to_numpy(float) for s in SESSIONS])
        X = np.column_stack([X, oh])
        lo += [0.0] * len(SESSIONS)
        hi += [1.0] * len(SESSIONS)
    elif term == "ord":
        order = t.session.map({s: i + 1 for i, s in enumerate(SESSIONS)}).to_numpy(float)
        X = np.column_stack([X, order])
        lo += [1.0]
        hi += [float(len(SESSIONS))]
    return X, np.array([lo, hi]), len(cols)


def fit_predict(Xtr, ytr, Xte, bounds, d_design, term):
    import torch
    from botorch.fit import fit_gpytorch_mll
    from botorch.models import SingleTaskGP
    from botorch.models.transforms import Normalize, Standardize
    from botorch.models.utils.gpytorch_modules import (
        get_covar_module_with_dim_scaled_prior,
    )
    from gpytorch.kernels import AdditiveKernel, LinearKernel
    from gpytorch.mlls import ExactMarginalLogLikelihood

    Xtr_t = torch.tensor(Xtr, dtype=torch.float64)
    Ytr = torch.tensor(ytr, dtype=torch.float64)[:, None]
    Xte_t = torch.tensor(Xte, dtype=torch.float64)
    bt = torch.tensor(bounds, dtype=torch.float64)
    d = Xtr.shape[1]
    if term == "ri":
        covar = AdditiveKernel(
            get_covar_module_with_dim_scaled_prior(
                ard_num_dims=d_design, active_dims=list(range(d_design))),
            LinearKernel(active_dims=list(range(d_design, d))))
    else:
        covar = None   # BoTorch default over every column (ord: d_design + 1)
    m = SingleTaskGP(Xtr_t, Ytr, covar_module=covar,
                     input_transform=Normalize(d=d, bounds=bt),
                     outcome_transform=Standardize(m=1))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit_gpytorch_mll(ExactMarginalLogLikelihood(m.likelihood, m))
    with torch.no_grad():
        post = m.posterior(Xte_t)
        mu = post.mean.reshape(-1).numpy()
        sd = post.variance.clamp_min(0).sqrt().reshape(-1).numpy()
    return mu, sd, m


def batch_effects(t, space, metric):
    """Posterior mean and sd of each session's random intercept, all 44
    articles, original units (additive-GP decomposition)."""
    import torch

    X, bounds, dd = design_matrix(t, space, "ri")
    y = t[f"{metric}_obs"].to_numpy(float)
    _, _, m = fit_predict(X, y, X[:1], bounds, dd, "ri")
    m.eval()
    with torch.no_grad():
        Xn = m.input_transform(torch.tensor(X, dtype=torch.float64))
        K = m.covar_module(Xn).to_dense()
        noise = m.likelihood.noise.reshape(-1)[0]
        Kn = K + noise * torch.eye(len(y), dtype=torch.float64)
        ystd = float(m.outcome_transform.stdvs.reshape(-1)[0])
        ymean = float(m.outcome_transform.means.reshape(-1)[0])
        ys = (torch.tensor(y, dtype=torch.float64) - ymean) / ystd
        lin = m.covar_module.kernels[1]
        v = float(lin.variance.reshape(-1)[0])
        Kinv = torch.linalg.inv(Kn)
        out = {}
        for j, s in enumerate(SESSIONS):
            ind = torch.tensor((t.session == s).to_numpy(float), dtype=torch.float64)
            kb = v * ind
            mean = float(kb @ Kinv @ ys) * ystd
            var = float(v - kb @ Kinv @ kb) * ystd ** 2
            out[s] = {"effect": mean, "sd": float(np.sqrt(max(var, 0.0))),
                      "n_articles": int(ind.sum())}
        out["_session_sd"] = float(np.sqrt(v)) * ystd
        out["_noise_sd"] = float(np.sqrt(float(noise))) * ystd
    return out


def cv(t, space, term, scheme):
    X, bounds, dd = design_matrix(t, space, term)
    groups = t.design.to_numpy() if scheme == "logo" else t.session.to_numpy()
    res = {}
    for metric in METRICS:
        y = t[f"{metric}_obs"].to_numpy(float)
        mu = np.empty(len(y))
        sd = np.empty(len(y))
        base = np.empty(len(y))
        for g in dict.fromkeys(groups):
            te = groups == g
            mu[te], sd[te], _ = fit_predict(X[~te], y[~te], X[te], bounds, dd, term)
            base[te] = y[~te].mean()
        rho, p = permutation_p(mu, y, n=5000)
        res[metric] = {
            "spearman": rho, "perm_p": p,
            "R2_oos": float(1 - ((y - mu) ** 2).sum() / ((y - base) ** 2).sum()),
            "MAPE_pct": float(100 * np.mean(np.abs(mu - y) / np.abs(y))),
            "coverage_1.96sd_pct": float(100 * np.mean(np.abs(y - mu) <= 1.96 * sd)),
        }
        if scheme == "lobo":
            res[metric]["per_session_mean_error"] = {
                s: float(np.mean(mu[groups == s] - y[groups == s])) for s in SESSIONS}
            res[metric]["per_session_R2"] = {
                s: float(1 - ((y[groups == s] - mu[groups == s]) ** 2).sum()
                         / ((y[groups == s] - base[groups == s]) ** 2).sum())
                for s in SESSIONS}
    return res


def confound_table(t):
    cols = ["pla_nozzle_temp_C", "pla_flow_mm3_s", "tpu_nozzle_temp_C", "tpu_flow_mm3_s"]
    g = t.groupby("session", sort=False)[cols].agg(lambda s: "/".join(f"{v:g}" for v in sorted(set(s))))
    return g.loc[SESSIONS].reset_index().to_dict(orient="records")


def main():
    t = load_table()
    OUT.mkdir(parents=True, exist_ok=True)
    out = {"sessions_in_print_order": SESSIONS,
           "filament_settings_by_session": confound_table(t), "cv": {}, "batch_effects": {}}
    for scheme in ("logo", "lobo"):
        for space in SPACES:
            for term in TERMS:
                key = f"{scheme}/{space}/{term}"
                out["cv"][key] = cv(t, space, term, scheme)
                s = out["cv"][key]
                print(key, " ".join(f"{m}: rho {v['spearman']:+.2f} R2 {v['R2_oos']:+.2f}"
                                    for m, v in s.items()), flush=True)
    for space in ("six", "eight"):
        for metric in METRICS:
            out["batch_effects"][f"{space}/{metric}"] = batch_effects(t, space, metric)
            print(space, metric, json.dumps(out["batch_effects"][f"{space}/{metric}"])[:400])
    (OUT / "batch-term.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
