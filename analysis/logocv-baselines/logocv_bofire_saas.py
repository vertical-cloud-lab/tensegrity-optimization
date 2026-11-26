"""Leave-one-design-out CV of BoFire's fully Bayesian SAAS surrogate.

PR #121 follow-up (sgbaird, 2026-11-10), on the "not done" item "BoFire's own
fully Bayesian SAAS surrogate": "Do this also". ``logocv_bofire.py`` covers
BoFire's default (MAP) surrogate; this script covers its fully Bayesian one.

The surrogate is BoFire 0.5.0's ``FullyBayesianSingleTaskGPSurrogate`` with
``model_type="saas"`` (its default), one per output, as a BoFire strategy
builds it when given that data model:

- model: BoTorch's ``SaasFullyBayesianSingleTaskGP`` (Matern-5/2, SAAS
  half-Cauchy shrinkage on the inverse lengthscales), built with no
  ``train_Yvar``, so the noise is **learned** (BoTorch's Gamma(0.9, 10) prior
  on the standardized noise variance). BoFire's surrogate takes no per-point
  noise, so the archived SEMs are not used;
- input scaling: ``Normalize`` to the unit cube over the declared input
  bounds (``data/fit-space-bounds.json``, Ax's search space); output
  scaling: ``Standardize``; both learned inside the fold;
- fit: ``botorch.fit.fit_fully_bayesian_model_nuts``, which in BoTorch 0.18
  runs NumPyro's NUTS on JAX (dense mass matrix, maximum tree depth 6).
  BoFire passes ``warmup_steps``, ``num_samples`` and ``thinning`` and no
  seed, so the JAX PRNG key is 0 in every fold (BoFire's behaviour, kept).

NUTS budget: 512 warmup steps and 256 samples, thinned by 16 to 16 retained
draws (``--budget campaign``, the default), i.e. the budget of every Ax
SAASBO run in this directory and of the campaign. ``--budget bofire`` gives
BoFire's own data-model defaults (256 warmup, 128 samples, thinning 16, so 8
draws). The outputs of the two budgets go to separate directories.

Protocol: the 35 design folds of every other run here, in the same order,
over the 44 articles of ``data/article-features.csv``; each fold fits fresh
surrogates on the 43 or 42 training articles and predicts the held-out
ones; ``torch.manual_seed(fold_index)`` before each fit (as in the other
drivers; NUTS itself draws from the JAX key above).

Reported uncertainty: ``predicted`` is the mean of the Gaussian mixture over
the retained draws and ``predicted_sem`` its sd for the latent function
(``observation_noise=False``), which is what Ax's ``predicted_sem`` is for
the SAASBO runs. BoFire's own ``predict()`` sd (``observation_noise=True``,
the learned noise of each draw added) is kept as ``predicted_sd_bofire``.

Work is split into one task per (space, fold), so several processes can run
at once (``--worker``); each finished fold is written to
``<out>/folds/<space>/<fold_index>.json`` and ``--assemble`` writes the
campaign-format CSV, the per-fold hyperparameter summary and ``state.json``.

Output (``--budget campaign``): ``data/bofire-saas/bofire-saas-<space>.csv``
(campaign LOGO layout plus ``predicted_sd_bofire``),
``data/bofire-saas/bofire-saas-<space>-fits.json`` (per fold and objective:
median lengthscales over the draws on the unit cube, median learned noise
and outputscale, train size, seconds), ``data/bofire-saas/state.json``.

Environment: the BoFire one of ``logocv_bofire.py``.

Usage (repo root)::

    for i in 1 2 3 4; do
      /tmp/venv-bofire/bin/python analysis/logocv-baselines/logocv_bofire_saas.py \\
          --worker --spaces twelve six six-sim &
    done; wait
    /tmp/venv-bofire/bin/python analysis/logocv-baselines/logocv_bofire_saas.py \\
        --assemble --spaces twelve six six-sim
"""
from __future__ import annotations

import os

# one thread per worker process (set before JAX / torch are imported)
os.environ.setdefault("XLA_FLAGS", "--xla_cpu_multi_thread_eigen=false "
                      "intra_op_parallelism_threads=1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse  # noqa: E402
import json  # noqa: E402
import socket  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import warnings  # noqa: E402
from importlib import metadata  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from logocv_bofire import (  # noqa: E402
    BOUNDS_JSON, DATA, METRICS, SPACES, TABLE_CSV, bounds_for)

BUDGETS = {
    # name: (warmup_steps, num_samples, thinning, output directory)
    "campaign": (512, 256, 16, DATA / "bofire-saas"),
    "bofire": (256, 128, 16, DATA / "bofire-saas-default-budget"),
}


def make_surrogate(cols, bounds, metric, budget):
    from bofire.data_models.domain.api import Inputs, Outputs
    from bofire.data_models.features.api import ContinuousInput, ContinuousOutput
    from bofire.data_models.surrogates.api import FullyBayesianSingleTaskGPSurrogate
    import bofire.surrogates.api as surrogates

    warmup, samples, thinning, _ = BUDGETS[budget]
    inputs = Inputs(features=[ContinuousInput(key=c, bounds=bounds[c]) for c in cols])
    outputs = Outputs(features=[ContinuousOutput(key=metric)])
    data_model = FullyBayesianSingleTaskGPSurrogate(
        inputs=inputs, outputs=outputs, model_type="saas",
        warmup_steps=warmup, num_samples=samples, thinning=thinning)
    return data_model, surrogates.map(data_model)


def describe(cols, bounds, budget):
    """What the data model resolves to (for state.json)."""
    dm, _ = make_surrogate(cols, bounds, METRICS[0], budget)
    d = json.loads(dm.model_dump_json())
    keep = ("type", "model_type", "warmup_steps", "num_samples", "thinning",
            "features_to_warp", "scaler", "output_scaler", "aggregations")
    return {k: d.get(k) for k in keep}


def _draws(t):
    return t.detach().reshape(t.shape[0], -1).numpy()


def hypers(sur, n_train, seconds):
    """Per-fold summary of the retained NUTS draws (medians over draws)."""
    m = sur.model
    kern = m.covar_module
    base = getattr(kern, "base_kernel", kern)
    ls = _draws(base.lengthscale)                     # draws x d, unit cube
    rec = {
        "kernel": type(base).__name__,
        "n_draws": int(ls.shape[0]),
        "lengthscale_median": [round(float(v), 5) for v in np.median(ls, axis=0)],
        "noise_standardized_median": float(np.median(_draws(m.likelihood.noise))),
        "n_train": int(n_train),
        "seconds": round(seconds, 2),
    }
    if hasattr(kern, "outputscale"):
        rec["outputscale_median"] = float(np.median(_draws(kern.outputscale)))
    return rec


def fit_fold(table, space, design, budget):
    import torch

    cols = SPACES[space]
    bounds = bounds_for(cols)
    te = (table.design == design).to_numpy()
    tr = ~te
    k = int(table.fold_index[te].iloc[0])
    rows, fits = [], {}
    for metric in METRICS:
        _, sur = make_surrogate(cols, bounds, metric, budget)
        train = table.loc[tr, cols + [f"{metric}_obs"]].rename(
            columns={f"{metric}_obs": metric}).reset_index(drop=True)
        train[f"valid_{metric}"] = 1
        test = table.loc[te, cols].reset_index(drop=True)
        torch.manual_seed(k)
        t_fit = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sur.fit(train)
            pred = sur.predict(test)
        dt = time.time() - t_fit
        X = torch.from_numpy(
            sur.inputs.transform(test, sur.input_preprocessing_specs).values
        ).to(torch.float64)
        with torch.no_grad():
            post = sur.model.posterior(X=X, observation_noise=False)
            mu = post.mixture_mean.reshape(-1).numpy()
            sd_f = post.mixture_variance.clamp_min(0).sqrt().reshape(-1).numpy()
        assert np.allclose(mu, pred[f"{metric}_pred"].to_numpy(), rtol=1e-9, atol=1e-12)
        fits[metric] = hypers(sur, tr.sum(), dt)
        for i, idx in enumerate(np.flatnonzero(te)):
            rows.append({
                "arm_name": table.arm_name[idx], "print_id": table.print_id[idx],
                "metric": metric, "observed": float(table[f"{metric}_obs"][idx]),
                "observed_sem": float(table[f"{metric}_sem"][idx]),
                "predicted": float(mu[i]), "predicted_sem": float(sd_f[i]),
                "predicted_sd_bofire": float(pred[f"{metric}_sd"].iloc[i]),
            })
    return {"space": space, "design": design, "fold_index": k, "rows": rows,
            "fits": fits}


def fold_order(table):
    designs = list(dict.fromkeys(table.design))      # canonical fold order
    assert designs == list(dict.fromkeys(
        table.sort_values("fold_index", kind="stable").design)), "fold order"
    return designs


def check_domain(table, space):
    cols = SPACES[space]
    bounds = bounds_for(cols)
    for c in cols:   # every article must sit inside the declared domain
        lo, hi = bounds[c]
        assert table[c].between(lo - 1e-9, hi + 1e-9).all(), c


def worker(table, spaces, budget, limit=None):
    """Claim (space, fold) tasks in order until none are left."""
    out = BUDGETS[budget][3]
    done = 0
    for space in spaces:
        check_domain(table, space)
        fdir = out / "folds" / space
        fdir.mkdir(parents=True, exist_ok=True)
        for design in fold_order(table):
            k = int(table.fold_index[table.design == design].iloc[0])
            target = fdir / f"{k:02d}.json"
            claim = fdir / f"{k:02d}.claim"
            if target.exists():
                continue
            try:
                fd = os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                continue
            os.write(fd, f"{socket.gethostname()} {os.getpid()} {time.time():.0f}\n".encode())
            os.close(fd)
            t0 = time.time()
            rec = fit_fold(table, space, design, budget)
            rec["seconds"] = round(time.time() - t0, 1)
            tmp = target.with_suffix(".tmp")
            tmp.write_text(json.dumps(rec, indent=1) + "\n")
            tmp.replace(target)
            claim.unlink(missing_ok=True)
            print(f"  {budget} {space:8s} fold {k:2d} ({design}) {rec['seconds']:6.1f} s",
                  flush=True)
            done += 1
            if limit is not None and done >= limit:
                return


def assemble(table, spaces, budget):
    import torch

    warmup, samples, thinning, out = BUDGETS[budget]
    state_path = out / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    try:
        import jax
        x64 = bool(jax.config.read("jax_enable_x64"))
    except Exception:  # pragma: no cover
        x64 = None
    state.update({
        "what": "BoFire fully Bayesian SAAS surrogate "
                "(FullyBayesianSingleTaskGPSurrogate, model_type 'saas'), one "
                "per objective, leave-one-design-out over the 35 design folds "
                "of the round-5 record",
        "driver": "analysis/logocv-baselines/logocv_bofire_saas.py",
        "budget": {"name": budget, "warmup_steps": warmup, "num_samples": samples,
                   "thinning": thinning, "retained_draws": samples // thinning,
                   "max_tree_depth": 6, "sampler": "NumPyro NUTS (dense mass "
                   "matrix), via botorch.fit.fit_fully_bayesian_model_nuts"},
        "versions": {p: metadata.version(p) for p in
                     ("bofire", "botorch", "gpytorch", "torch", "jax", "numpyro",
                      "pandas", "numpy")},
        "python": sys.version.split()[0],
        "jax_enable_x64": x64,
        "threads_per_worker": 1,
        "seed_scheme": "torch.manual_seed(fold_index) before each fit; NUTS "
                       "uses jax.random.PRNGKey(0) in every fold (BoFire passes "
                       "no seed to fit_fully_bayesian_model_nuts)",
        "noise": "learned (no train_Yvar): BoTorch's Gamma(0.9, 10) prior on "
                 "the standardized noise variance",
        "input_bounds_source": str(BOUNDS_JSON.relative_to(HERE)),
        "observed_values_source": str(TABLE_CSV.relative_to(HERE)),
        "predicted": "mixture mean over the retained draws",
        "predicted_sem": "mixture sd of the latent function "
                         "(observation_noise=False)",
        "predicted_sd_bofire": "BoFire predict() sd (mixture, "
                               "observation_noise=True, the learned noise added)",
    })
    state.setdefault("spaces", {})
    tag = "bofire-saas"
    for space in spaces:
        fdir = out / "folds" / space
        rows, fits, secs, missing = [], {}, [], []
        for design in fold_order(table):
            k = int(table.fold_index[table.design == design].iloc[0])
            p = fdir / f"{k:02d}.json"
            if not p.exists():
                missing.append(k)
                continue
            rec = json.loads(p.read_text())
            assert rec["design"] == design and rec["space"] == space, p
            rows += rec["rows"]
            secs.append(rec["seconds"])
            for metric, h in rec["fits"].items():
                fits[f"{design}/{metric}"] = h
        if missing:
            print(f"  {space}: {35 - len(missing)}/35 folds, missing {missing}")
            continue
        df = pd.DataFrame(rows)
        assert len(df) == 88, len(df)
        df.to_csv(out / f"{tag}-{space}.csv", index=False, float_format="%.9g")
        (out / f"{tag}-{space}-fits.json").write_text(json.dumps(fits, indent=1) + "\n")
        state["spaces"][space] = {
            "inputs": SPACES[space], "folds": 35,
            "seconds_per_fold_median": round(float(np.median(secs)), 1),
            "seconds_total": round(float(np.sum(secs)), 1),
            "data_model": describe(SPACES[space], bounds_for(SPACES[space]), budget),
        }
        print(f"  {space}: 35/35 folds, median {np.median(secs):.1f} s per fold")
    out.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n")
    del torch


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--spaces", nargs="*", default=["twelve", "six", "six-sim"],
                    choices=list(SPACES))
    ap.add_argument("--budget", default="campaign", choices=list(BUDGETS))
    ap.add_argument("--worker", action="store_true", help="fit folds")
    ap.add_argument("--limit", type=int, default=None,
                    help="stop a worker after this many folds")
    ap.add_argument("--assemble", action="store_true")
    args = ap.parse_args(argv)

    import torch

    torch.set_num_threads(1)
    table = pd.read_csv(TABLE_CSV)
    assert len(table) == 44 and table.design.nunique() == 35
    if args.worker:
        worker(table, args.spaces, args.budget, args.limit)
    if args.assemble:
        assemble(table, args.spaces, args.budget)


if __name__ == "__main__":
    main()
