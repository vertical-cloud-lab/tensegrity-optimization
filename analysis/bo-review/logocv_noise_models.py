"""Leave-one-design-out CV of the campaign surrogate under three noise models.

PR #121 (sgbaird, 2026-11-10), item 1 of Juan Florez-Coronel's review:
"Could you compare fixed noise against inferred noise and against
replicate-based SEMs using grouped cross-validation?"

Noise models (``--noise``), all on the same 35 design folds, articles,
observed values and input bounds as every run in ``analysis/logocv-baselines``:

* ``fixed``: the archived per-article SEMs as known noise (``train_Yvar =
  sem**2``), what the campaign fed Ax.
* ``learned``: no ``train_Yvar``; one homoscedastic noise level per
  objective is learned with the other hyperparameters.
* ``replicate``: ``train_Yvar = sem**2 + s_print**2``, where ``s_print`` is
  the pooled within-design sd of the reprint pairs **in the training fold**
  (the held-out pair never informs its own noise). Each article is one print,
  so the noise of its mean is the drop-level SEM plus the print-to-print
  scatter the pairs measure.

Surrogates (``--model``):

* ``saas``: BoTorch's ``SaasFullyBayesianSingleTaskGP`` (the class Ax's
  SAASBO and BoFire's SAAS surrogate build), NUTS at the campaign budget
  (512 warmup, 256 samples, thinning 16) through
  ``botorch.fit.fit_fully_bayesian_model_nuts``, which in BoTorch 0.18 runs
  NumPyro on JAX. ``--seed`` is the JAX PRNG seed (default: the fold index).
* ``map``: BoTorch's default ``SingleTaskGP`` (RBF-ARD, dimension-scaled
  lognormal lengthscale prior, MAP fit), the model Ax's and BoFire's
  defaults build.

Inputs are normalized to ``analysis/logocv-baselines/data/fit-space-bounds.json``
and outputs standardized inside each fold (BoTorch's ``Standardize`` rescales
``train_Yvar`` with them).

Usage (BoFire venv, BoTorch 0.18.1)::

    for i in 1 2 3; do
      python analysis/bo-review/logocv_noise_models.py --model saas \
          --noise replicate --space twelve --worker &
    done; wait
    python analysis/bo-review/logocv_noise_models.py --model saas \
        --noise replicate --space twelve --assemble
"""

from __future__ import annotations

import os

os.environ.setdefault("XLA_FLAGS", "--xla_cpu_multi_thread_eigen=false "
                      "intra_op_parallelism_threads=1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import warnings  # noqa: E402
from importlib import metadata  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "logocv-baselines"
sys.path.insert(0, str(BASE))
from logocv_bofire import METRICS, SPACES, TABLE_CSV, bounds_for  # noqa: E402

DATA = HERE / "data"
BUDGET = dict(warmup_steps=512, num_samples=256, thinning=16)
EXTRA_SPACES = {
    # item 4: the four filament settings dropped (they only vary between batches)
    "eight": SPACES["six"] + ["strut_infill_pct", "tpu_infill_pct"],
}
ALL_SPACES = {**SPACES, **EXTRA_SPACES}


def load_table():
    t = pd.read_csv(BASE / "data" / "article-features.csv")
    assert len(t) == 44
    return t


def pooled_print_sd(t, mask, metric):
    """Pooled within-design sd over designs with >= 2 articles in ``mask``."""
    sub = t.loc[mask]
    ss, df = 0.0, 0
    for _, g in sub.groupby("design"):
        if len(g) < 2:
            continue
        y = g[f"{metric}_obs"].to_numpy()
        ss += float(((y - y.mean()) ** 2).sum())
        df += len(y) - 1
    return float(np.sqrt(ss / df)), df


def build_model(X, Y, Yvar, model, noise, bounds_t):
    from botorch.models import SingleTaskGP
    from botorch.models.fully_bayesian import SaasFullyBayesianSingleTaskGP
    from botorch.models.transforms import Normalize, Standardize

    kw = dict(input_transform=Normalize(d=X.shape[-1], bounds=bounds_t),
              outcome_transform=Standardize(m=1))
    yv = None if noise == "learned" else Yvar
    if model == "saas":
        return SaasFullyBayesianSingleTaskGP(X, Y, train_Yvar=yv, **kw)
    return SingleTaskGP(X, Y, train_Yvar=yv, **kw)


def fit_predict(t, cols, tr, te, metric, model, noise, seed):
    import torch
    from botorch.fit import fit_fully_bayesian_model_nuts, fit_gpytorch_mll
    from gpytorch.mlls import ExactMarginalLogLikelihood

    b = bounds_for(cols)
    bounds_t = torch.tensor([[b[c][0] for c in cols], [b[c][1] for c in cols]],
                            dtype=torch.float64)
    X = torch.tensor(t.loc[tr, cols].to_numpy(), dtype=torch.float64)
    Y = torch.tensor(t.loc[tr, f"{metric}_obs"].to_numpy(), dtype=torch.float64)[:, None]
    sem = torch.tensor(t.loc[tr, f"{metric}_sem"].to_numpy(), dtype=torch.float64)[:, None]
    s_print, df = pooled_print_sd(t, tr, metric)
    Yvar = sem ** 2 + (s_print ** 2 if noise == "replicate" else 0.0)
    m = build_model(X, Y, Yvar, model, noise, bounds_t)
    torch.manual_seed(seed)
    t0 = time.time()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if model == "saas":
            fit_fully_bayesian_model_nuts(m, disable_progbar=True, seed=seed, **BUDGET)
        else:
            fit_gpytorch_mll(ExactMarginalLogLikelihood(m.likelihood, m))
    dt = time.time() - t0
    Xte = torch.tensor(t.loc[te, cols].to_numpy(), dtype=torch.float64)
    with torch.no_grad():
        post = m.posterior(Xte, observation_noise=False)
        if model == "saas":
            mu = post.mixture_mean.reshape(-1).numpy()
            sd = post.mixture_variance.clamp_min(0).sqrt().reshape(-1).numpy()
        else:
            mu = post.mean.reshape(-1).numpy()
            sd = post.variance.clamp_min(0).sqrt().reshape(-1).numpy()
    # hyperparameters on the unit cube (medians over draws for SAAS)
    kern = m.covar_module
    base = getattr(kern, "base_kernel", kern)
    ls = base.lengthscale.detach().reshape(-1 if model == "map" else
                                           base.lengthscale.shape[0], len(cols))
    ls = ls.reshape(-1, len(cols)).numpy()
    rec = {"lengthscale_median": [round(float(v), 5) for v in np.median(ls, axis=0)],
           "s_print_fold": s_print, "s_print_df": df, "seconds": round(dt, 2),
           "n_train": int(tr.sum())}
    if noise != "fixed" and noise != "replicate":
        nz = m.likelihood.noise.detach().reshape(-1).numpy()
        ystd = float(t.loc[tr, f"{metric}_obs"].std(ddof=1))
        rec["noise_sd_original_units_median"] = float(np.sqrt(np.median(nz)) * ystd)
    return mu, sd, rec


def run_fold(t, space, design, model, noise, seed_offset):
    cols = ALL_SPACES[space]
    te = (t.design == design).to_numpy()
    tr = ~te
    k = int(t.fold_index[te].iloc[0])
    rows, fits = [], {}
    for metric in METRICS:
        mu, sd, rec = fit_predict(t, cols, tr, te, metric, model, noise,
                                  seed=k + seed_offset)
        fits[metric] = rec
        for i, idx in enumerate(np.flatnonzero(te)):
            rows.append({"arm_name": t.arm_name[idx], "print_id": t.print_id[idx],
                         "metric": metric, "observed": float(t[f"{metric}_obs"][idx]),
                         "observed_sem": float(t[f"{metric}_sem"][idx]),
                         "predicted": float(mu[i]), "predicted_sem": float(sd[i])})
    return {"space": space, "design": design, "fold_index": k, "rows": rows,
            "fits": fits}


def out_dir(model, noise, space, seed_offset):
    tag = f"{model}-{noise}-{space}" + (f"-seed{seed_offset}" if seed_offset else "")
    return DATA / "logocv" / tag


def worker(t, model, noise, space, seed_offset):
    od = out_dir(model, noise, space, seed_offset)
    fdir = od / "folds"
    fdir.mkdir(parents=True, exist_ok=True)
    for design in dict.fromkeys(t.design):
        k = int(t.fold_index[t.design == design].iloc[0])
        target, claim = fdir / f"{k:02d}.json", fdir / f"{k:02d}.claim"
        if target.exists():
            continue
        try:
            fd = os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            continue
        os.write(fd, f"{os.getpid()}\n".encode())
        os.close(fd)
        t0 = time.time()
        rec = run_fold(t, space, design, model, noise, seed_offset)
        rec["seconds"] = round(time.time() - t0, 1)
        tmp = target.with_suffix(".tmp")
        tmp.write_text(json.dumps(rec) + "\n")
        tmp.replace(target)
        claim.unlink(missing_ok=True)
        print(f"  {od.name} fold {k:2d} ({design}) {rec['seconds']:.1f} s", flush=True)


def permutation_p(x, y, n=20000, seed=0):
    from scipy.stats import spearmanr

    rho = spearmanr(x, y).statistic
    rng = np.random.default_rng(seed)
    yr = pd.Series(y).rank().to_numpy()
    xr = pd.Series(x).rank().to_numpy()
    xc = xr - xr.mean()
    null = np.empty(n)
    for i in range(n):
        yp = rng.permutation(yr)
        null[i] = np.dot(xc, yp - yp.mean()) / np.sqrt((xc ** 2).sum() * ((yp - yp.mean()) ** 2).sum())
    return float(rho), float((np.abs(null) >= abs(rho) - 1e-12).mean())


def score(df, t):
    """MAPE, Spearman (permutation p), R2_oos against the per-fold training
    mean, coverage at 1.96 latent sd."""
    out = {}
    for metric in METRICS:
        d = df[df.metric == metric].set_index("print_id").loc[t.print_id]
        y, f, s = d.observed.to_numpy(), d.predicted.to_numpy(), d.predicted_sem.to_numpy()
        base = np.array([t.loc[t.design != g, f"{metric}_obs"].mean() for g in t.design])
        rho, p = permutation_p(f, y)
        out[metric] = {
            "MAPE_pct": float(100 * np.mean(np.abs(f - y) / np.abs(y))),
            "spearman": rho, "perm_p": p,
            "R2_oos": float(1 - ((y - f) ** 2).sum() / ((y - base) ** 2).sum()),
            "coverage_1.96sd_pct": float(100 * np.mean(np.abs(y - f) <= 1.96 * s)),
            "pred_spread_sd": float(np.std(f, ddof=1)),
            "obs_sd": float(np.std(y, ddof=1)),
        }
    return out


def assemble(t, model, noise, space, seed_offset):
    od = out_dir(model, noise, space, seed_offset)
    recs = [json.loads((od / "folds" / f"{k:02d}.json").read_text())
            for k in sorted(set(t.fold_index))]
    df = pd.DataFrame([r for rec in recs for r in rec["rows"]])
    df.to_csv(od / "logocv.csv", index=False, float_format="%.9g")
    fits = {rec["design"]: rec["fits"] for rec in recs}
    (od / "fits.json").write_text(json.dumps(fits, indent=1) + "\n")
    stats = score(df, t)
    state = {
        "model": model, "noise": noise, "space": space, "columns": ALL_SPACES[space],
        "budget": BUDGET if model == "saas" else "MAP (fit_gpytorch_mll)",
        "seed_scheme": f"fold_index + {seed_offset} (torch and the JAX PRNG)",
        "versions": {p: metadata.version(p) for p in
                     ("botorch", "gpytorch", "torch", "jax", "numpyro", "numpy", "pandas")},
        "python": sys.version.split()[0],
        "total_fold_seconds": round(sum(r["seconds"] for r in recs), 1),
        "stats": stats,
    }
    (od / "state.json").write_text(json.dumps(state, indent=1) + "\n")
    print(od.name, json.dumps({m: {k: round(v, 3) for k, v in s.items()}
                               for m, s in stats.items()}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=("saas", "map"), required=True)
    ap.add_argument("--noise", choices=("fixed", "learned", "replicate"), required=True)
    ap.add_argument("--space", choices=sorted(ALL_SPACES), required=True)
    ap.add_argument("--seed-offset", type=int, default=0)
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--assemble", action="store_true")
    a = ap.parse_args()
    t = load_table()
    if a.worker:
        worker(t, a.model, a.noise, a.space, a.seed_offset)
    if a.assemble:
        assemble(t, a.model, a.noise, a.space, a.seed_offset)


if __name__ == "__main__":
    main()
