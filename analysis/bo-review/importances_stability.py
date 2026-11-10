"""Raw lengthscales, importances and MCMC stability of the SAAS surrogate.

PR #121 (sgbaird, 2026-11-10), items 6 to 8 of Juan Florez-Coronel's review:

6. "The t180 feature importances are close to uniform, which may mean the
   model is close to flat. The raw lengthscales would tell." Ax's
   ``feature_importances`` is the inverse of the median lengthscale over the
   draws, normalized to sum to 1 (``get_feature_importances_from_botorch_model``
   in Ax 0.5.0), so it cannot say whether the model is flat. This script
   reports the raw lengthscales on the unit cube, the outputscale, the noise
   and a direct flatness measure: the sd of the posterior mean over 1024
   scrambled-Sobol points of the fit space, in the objective's own units,
   next to the sd of the data.
7. "No importances exist yet for the 12-parameter model." Same table for the
   twelve-parameter model on all 44 articles.
8. "MCMC settings are left at defaults and differ between runs, so a
   stability check across seeds and sample counts would help." Each fit is
   repeated over JAX seeds 0 to 3 at three NUTS budgets (256/128,
   512/256 = the campaign's, 1024/512; warmup/samples, thinning 16). Across
   seeds the script reports the spread of the importances and of the
   posterior mean at the training points, and a split-R-hat over the four
   seeds (one chain each) for the log lengthscales and the noise.

Datasets: ``round2-six`` (the 17 articles of rounds 1 and 2 in the six-
parameter space, the model behind the archived round-2 importances) and
``all-twelve`` (all 44 articles, the campaign's twelve parameters).
Noise: ``fixed`` (the archived SEMs, as the campaign) and ``learned``.

Usage (BoFire venv, BoTorch 0.18.1)::

    python analysis/bo-review/importances_stability.py --run --noise fixed
    python analysis/bo-review/importances_stability.py --run --noise learned
    python analysis/bo-review/importances_stability.py --summarize
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
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "logocv-baselines"))
from logocv_bofire import METRICS, SPACES, bounds_for  # noqa: E402
from logocv_noise_models import load_table  # noqa: E402

OUT = HERE / "data" / "importances"
BUDGETS = {"256/128": (256, 128), "512/256": (512, 256), "1024/512": (1024, 512)}
SEEDS = (0, 1, 2, 3)
DATASETS = {
    "round2-six": dict(sessions=("seed", "r2d2c"), space="six"),
    "all-twelve": dict(sessions=None, space="twelve"),
}


def fit_one(t, cols, metric, noise, warmup, samples, seed, grid):
    import torch
    from botorch.fit import fit_fully_bayesian_model_nuts
    from botorch.models.fully_bayesian import SaasFullyBayesianSingleTaskGP
    from botorch.models.transforms import Normalize, Standardize

    b = bounds_for(cols)
    bt = torch.tensor([[b[c][0] for c in cols], [b[c][1] for c in cols]],
                      dtype=torch.float64)
    X = torch.tensor(t[cols].to_numpy(), dtype=torch.float64)
    Y = torch.tensor(t[f"{metric}_obs"].to_numpy(), dtype=torch.float64)[:, None]
    Yvar = torch.tensor(t[f"{metric}_sem"].to_numpy(), dtype=torch.float64)[:, None] ** 2
    m = SaasFullyBayesianSingleTaskGP(
        X, Y, train_Yvar=Yvar if noise == "fixed" else None,
        input_transform=Normalize(d=len(cols), bounds=bt),
        outcome_transform=Standardize(m=1))
    torch.manual_seed(seed)
    t0 = time.time()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit_fully_bayesian_model_nuts(m, warmup_steps=warmup, num_samples=samples,
                                      thinning=16, disable_progbar=True, seed=seed)
    dt = time.time() - t0
    kern = m.covar_module
    ls = kern.base_kernel.lengthscale.detach().reshape(-1, len(cols)).numpy()
    ystd = float(t[f"{metric}_obs"].std(ddof=1))
    rec = {
        "lengthscale_draws": ls.round(6).tolist(),
        "outputscale_draws": (kern.outputscale.detach().reshape(-1).numpy()).round(6).tolist(),
        "y_std": ystd, "seconds": round(dt, 2),
    }
    if noise == "learned":
        rec["noise_draws"] = m.likelihood.noise.detach().reshape(-1).numpy().round(8).tolist()
    Xg = bt[0] + (bt[1] - bt[0]) * torch.tensor(grid, dtype=torch.float64)
    with torch.no_grad():
        mu_g = m.posterior(Xg).mixture_mean.reshape(-1).numpy()
        mu_tr = m.posterior(X).mixture_mean.reshape(-1).numpy()
    rec["posterior_mean_sd_over_space"] = float(np.std(mu_g, ddof=1))
    rec["posterior_mean_at_train"] = mu_tr.round(6).tolist()
    return rec


def run(noise, datasets, budgets, seeds):
    from scipy.stats import qmc

    t = load_table()
    OUT.mkdir(parents=True, exist_ok=True)
    for dname in datasets:
        spec = DATASETS[dname]
        sub = t if spec["sessions"] is None else t[t.session.isin(spec["sessions"])]
        sub = sub.reset_index(drop=True)
        cols = SPACES[spec["space"]]
        grid = qmc.Sobol(d=len(cols), scramble=True, seed=1234).random(1024)
        for bname in budgets:
            warmup, samples = BUDGETS[bname]
            for seed in seeds:
                path = OUT / f"{dname}-{noise}-{bname.replace('/', 'w')}-s{seed}.json"
                if path.exists():
                    continue
                rec = {"dataset": dname, "noise": noise, "budget": bname,
                       "seed": seed, "columns": cols, "n": len(sub),
                       "print_ids": sub.print_id.tolist(), "metrics": {}}
                for metric in METRICS:
                    rec["metrics"][metric] = fit_one(sub, cols, metric, noise, warmup,
                                                     samples, seed, grid)
                path.write_text(json.dumps(rec) + "\n")
                print(f"  {path.name}: "
                      + ", ".join(f"{m} {r['seconds']:.0f} s"
                                  for m, r in rec["metrics"].items()), flush=True)


def split_rhat(chains):
    """Split-R-hat (Gelman et al. 2013) for a list of 1-D chains."""
    halves = []
    for c in chains:
        c = np.asarray(c, dtype=float)
        h = len(c) // 2
        halves += [c[:h], c[h:2 * h]]
    x = np.array(halves)
    n = x.shape[1]
    w = x.var(axis=1, ddof=1).mean()
    b = n * x.mean(axis=1).var(ddof=1)
    var = (n - 1) / n * w + b / n
    return float(np.sqrt(var / w)) if w > 0 else float("nan")


def summarize():
    rows, stab = [], []
    recs = [json.loads(p.read_text()) for p in sorted(OUT.glob("*.json"))
            if p.name not in ("summary.json",)]
    for r in recs:
        for metric, f in r["metrics"].items():
            ls = np.array(f["lengthscale_draws"])
            med = np.median(ls, axis=0)
            inv = 1 / med
            imp = inv / inv.sum()
            for j, c in enumerate(r["columns"]):
                rows.append({
                    "dataset": r["dataset"], "noise": r["noise"], "budget": r["budget"],
                    "seed": r["seed"], "metric": metric, "parameter": c,
                    "lengthscale_median": med[j],
                    "lengthscale_q25": np.percentile(ls[:, j], 25),
                    "lengthscale_q75": np.percentile(ls[:, j], 75),
                    "ax_importance": imp[j],
                })
            stab.append({
                "dataset": r["dataset"], "noise": r["noise"], "budget": r["budget"],
                "seed": r["seed"], "metric": metric,
                "outputscale_median": float(np.median(f["outputscale_draws"])),
                "noise_sd_median": (float(np.sqrt(np.median(f["noise_draws"])) * f["y_std"])
                                    if "noise_draws" in f else None),
                "posterior_mean_sd_over_space": f["posterior_mean_sd_over_space"],
                "y_std": f["y_std"], "seconds": f["seconds"],
            })
    imp = pd.DataFrame(rows)
    st = pd.DataFrame(stab)
    imp.to_csv(OUT / "lengthscales-importances.csv", index=False, float_format="%.5g")
    st.to_csv(OUT / "fit-summary.csv", index=False, float_format="%.5g")
    # seed-to-seed stability at each budget
    out = []
    for (d, n, b, m), g in imp.groupby(["dataset", "noise", "budget", "metric"]):
        piv = g.pivot(index="seed", columns="parameter", values="ax_importance")
        pivls = g.pivot(index="seed", columns="parameter", values="lengthscale_median")
        recs_dbm = [r for r in recs if (r["dataset"], r["noise"], r["budget"]) == (d, n, b)]
        means = np.array([r["metrics"][m]["posterior_mean_at_train"] for r in recs_dbm])
        draws = [np.log(np.array(r["metrics"][m]["lengthscale_draws"])) for r in recs_dbm]
        rh = [split_rhat([dr[:, j] for dr in draws]) for j in range(draws[0].shape[1])]
        sdf = st[(st.dataset == d) & (st.noise == n) & (st.budget == b) & (st.metric == m)]
        top = piv.mean().sort_values(ascending=False)
        out.append({
            "dataset": d, "noise": n, "budget": b, "metric": m, "n_seeds": len(piv),
            "importance_mean": {k: round(float(v), 3) for k, v in top.items()},
            "importance_seed_sd_max": round(float(piv.std(ddof=1).max()), 3),
            "top_parameter_per_seed": [str(piv.loc[s].idxmax()) for s in piv.index],
            "lengthscale_median_by_seed": {str(s): {c: round(float(v), 3) for c, v in pivls.loc[s].items()}
                                           for s in pivls.index},
            "split_rhat_log_lengthscale_max": round(float(np.nanmax(rh)), 3),
            "split_rhat_log_lengthscale": {c: round(float(v), 3)
                                           for c, v in zip(recs_dbm[0]["columns"], rh)},
            "posterior_mean_at_train_seed_sd_median": float(np.median(means.std(axis=0, ddof=1))),
            "posterior_mean_at_train_seed_sd_max": float(means.std(axis=0, ddof=1).max()),
            "posterior_mean_sd_over_space_by_seed": [round(float(v), 4) for v in
                                                     sdf.sort_values("seed").posterior_mean_sd_over_space],
            "y_std": float(sdf.y_std.iloc[0]),
            "noise_sd_median_by_seed": (None if sdf.noise_sd_median.isna().all() else
                                        [round(float(v), 4) for v in sdf.sort_values("seed").noise_sd_median]),
        })
    (OUT / "summary.json").write_text(json.dumps(out, indent=1) + "\n")
    for o in out:
        print(o["dataset"], o["noise"], o["budget"], o["metric"],
              "top", o["top_parameter_per_seed"], "imp-sd", o["importance_seed_sd_max"],
              "Rhat", o["split_rhat_log_lengthscale_max"],
              "flat", o["posterior_mean_sd_over_space_by_seed"], "ystd", round(o["y_std"], 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--noise", choices=("fixed", "learned"))
    ap.add_argument("--datasets", nargs="+", default=list(DATASETS))
    ap.add_argument("--budgets", nargs="+", default=list(BUDGETS))
    ap.add_argument("--seeds", nargs="+", type=int, default=list(SEEDS))
    ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args()
    if a.run:
        run(a.noise, a.datasets, a.budgets, a.seeds)
    if a.summarize:
        summarize()


if __name__ == "__main__":
    main()
