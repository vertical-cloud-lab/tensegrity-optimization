"""Leave-one-design-out CV of BoFire's default surrogate on the round-5 record.

PR #121 follow-up (sgbaird, 2026-11-05): "try also with Ax default and
separately also BoFire". The Ax half is ``rerun_logocv_six_param_sim.py
--model ax-default``; this script is the BoFire half.

"BoFire default" is the surrogate BoFire's strategies (``SoboStrategy``,
``MoboStrategy``) build when none is specified: one
``SingleTaskGPSurrogate`` per output, with its data-model defaults. In
BoFire 0.5.0 that is

- kernel: RBF with one lengthscale per input (ARD), no output scale, and the
  dimension-scaled lognormal lengthscale prior of Hvarfner et al. (BoFire's
  ``HVARFNER_LENGTHSCALE_PRIOR``, the same prior as BoTorch's default
  ``SingleTaskGP``);
- likelihood: Gaussian with a **learned** homoscedastic noise level,
  LogNormal(-4, 1) prior, lower bound 1e-4 (BoFire's surrogate takes no
  per-point noise, so the archived SEMs are not used);
- input scaling: ``Normalize`` to the unit cube over the declared input
  bounds; output scaling: ``Standardize``;
- fit: ``botorch.fit.fit_gpytorch_mll`` (MAP).

The domain declares each input with the bounds Ax fitted in
(``data/fit-space-bounds.json``: the campaign's ``fit_search_space`` for the
twelve parameters, the observed range padded by 10% for the six simulation
features), so BoFire's ``Normalize`` and Ax's agree.

Protocol: the 35 design folds of every other run here, in the same order,
over the 44 articles of ``data/article-features.csv`` (the parameters and
observed means exactly as Ax fitted them); each fold fits a fresh surrogate
on the 43 or 42 training articles and predicts the held-out ones;
``torch.manual_seed(fold_index)`` before each fit. Everything that is
learned (scalers included) is learned inside the fold.

Reported uncertainty: ``predicted_sem`` is the posterior sd of the latent
function (``observation_noise=False``), which is what Ax's ``predicted_sem``
is for the SAASBO runs and what the scorecard's coverage uses for every GP.
BoFire's own ``predict()`` reports the sd with the learned noise added
(``observation_noise=True``); that column is kept as
``predicted_sd_bofire`` and its coverage is reported separately.

Output: ``data/bofire/bofire-<space>.csv`` (campaign LOGO layout plus
``predicted_sd_bofire``), ``data/bofire/bofire-<space>-fits.json`` (per fold
and objective: fitted lengthscales in normalized units, noise, train size,
seconds), ``data/bofire/state.json`` (versions, settings).

Environment (separate from the Ax one; BoFire 0.5.0 needs BoTorch 0.18)::

    python -m venv /tmp/venv-bofire
    /tmp/venv-bofire/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
    /tmp/venv-bofire/bin/pip install "bofire[optimization]==0.5.0" matplotlib

Usage (repo root)::

    /tmp/venv-bofire/bin/python analysis/logocv-baselines/logocv_bofire.py \\
        --spaces six six-sim twelve
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from importlib import metadata
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = DATA / "bofire"
TABLE_CSV = DATA / "article-features.csv"
BOUNDS_JSON = DATA / "fit-space-bounds.json"
METRICS = ("t180", "e_reb_mJ")
SHAPE = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]
MASS = ["mass_printed_g"]
PROCESS = ["strut_infill_pct", "tpu_infill_pct", "pla_nozzle_temp_C",
           "pla_flow_mm3_s", "tpu_nozzle_temp_C", "tpu_flow_mm3_s"]
SIM = ["sim_tierC_t180", "sim_tierC_tendon_energy_mJ", "sim_tierC_stroke_mm",
       "sim_tierB_t180", "sim_tierB_fn_hz", "sim_tierB_zeta_pct"]
SPACES = {
    "six": SHAPE + MASS,
    "six-sim": SHAPE + MASS + SIM,
    "twelve": SHAPE + MASS + PROCESS,
    "shape": SHAPE,
    "shape-sim": SHAPE + SIM,
    "twelve-sim": SHAPE + MASS + PROCESS + SIM,
    "sim-only": SIM,
}


def bounds_for(cols):
    spec = json.loads(BOUNDS_JSON.read_text())
    allb = {**spec["bounds"], **spec["sim_feature_bounds"]}
    return {c: tuple(float(v) for v in allb[c]) for c in cols}


def make_surrogate(cols, bounds, metric):
    from bofire.data_models.domain.api import Inputs, Outputs
    from bofire.data_models.features.api import ContinuousInput, ContinuousOutput
    from bofire.data_models.surrogates.api import SingleTaskGPSurrogate
    import bofire.surrogates.api as surrogates

    inputs = Inputs(features=[ContinuousInput(key=c, bounds=bounds[c]) for c in cols])
    outputs = Outputs(features=[ContinuousOutput(key=metric)])
    data_model = SingleTaskGPSurrogate(inputs=inputs, outputs=outputs)
    return data_model, surrogates.map(data_model)


def describe_default(cols, bounds):
    """What the default data model resolves to (for state.json)."""
    dm, _ = make_surrogate(cols, bounds, METRICS[0])
    d = json.loads(dm.model_dump_json())
    keep = ("type", "kernel", "noise_prior", "noise_constraint", "scaler",
            "output_scaler", "aggregations", "categorical_encodings")
    return {k: d.get(k) for k in keep}


def hypers(sur, n_train, seconds):
    m = sur.model
    kern = m.covar_module
    base = getattr(kern, "base_kernel", kern)
    rec = {
        "kernel": type(base).__name__,
        "lengthscale": [round(float(v), 5) for v in base.lengthscale.detach().reshape(-1)],
        "noise_standardized": float(m.likelihood.noise.detach().reshape(-1)[0]),
        "n_train": int(n_train),
        "seconds": round(seconds, 2),
    }
    if hasattr(kern, "outputscale"):
        rec["outputscale"] = float(kern.outputscale.detach().reshape(-1)[0])
    return rec


def run_space(space, table, out_dir=OUT):
    import torch

    cols = SPACES[space]
    bounds = bounds_for(cols)
    for c in cols:   # every article must sit inside the declared domain
        lo, hi = bounds[c]
        assert table[c].between(lo - 1e-9, hi + 1e-9).all(), c
    designs = list(dict.fromkeys(table.design))      # canonical fold order
    assert designs == list(dict.fromkeys(
        table.sort_values("fold_index", kind="stable").design)), "fold order"
    rows, fits = [], {}
    t0 = time.time()
    for design in designs:
        te = (table.design == design).to_numpy()
        tr = ~te
        k = int(table.fold_index[te].iloc[0])
        for metric in METRICS:
            _, sur = make_surrogate(cols, bounds, metric)
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
            # latent-function sd (noise excluded), the convention of every
            # other GP row in the scorecard
            X = torch.from_numpy(
                sur.inputs.transform(test, sur.input_preprocessing_specs).values
            ).to(torch.float64)
            with torch.no_grad():
                post = sur.model.posterior(X=X, observation_noise=False)
                mu = post.mean.reshape(-1).numpy()
                sd_f = post.variance.clamp_min(0).sqrt().reshape(-1).numpy()
            assert np.allclose(mu, pred[f"{metric}_pred"].to_numpy(), rtol=1e-9, atol=1e-12)
            fits[f"{design}/{metric}"] = hypers(sur, tr.sum(), dt)
            for i, idx in enumerate(np.flatnonzero(te)):
                rows.append({
                    "arm_name": table.arm_name[idx], "print_id": table.print_id[idx],
                    "metric": metric, "observed": float(table[f"{metric}_obs"][idx]),
                    "observed_sem": float(table[f"{metric}_sem"][idx]),
                    "predicted": float(mu[i]), "predicted_sem": float(sd_f[i]),
                    "predicted_sd_bofire": float(pred[f"{metric}_sd"].iloc[i]),
                })
    out = pd.DataFrame(rows)
    assert len(out) == 88, len(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_dir / f"bofire-{space}.csv", index=False, float_format="%.9g")
    (out_dir / f"bofire-{space}-fits.json").write_text(json.dumps(fits, indent=1) + "\n")
    secs = time.time() - t0
    print(f"  bofire {space:8s} {secs:5.0f} s", flush=True)
    return out, secs, describe_default(cols, bounds)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--spaces", nargs="*", default=["six", "six-sim", "twelve"],
                    choices=list(SPACES))
    ap.add_argument("--threads", type=int, default=1)
    args = ap.parse_args(argv)

    import torch

    torch.set_num_threads(args.threads)
    table = pd.read_csv(TABLE_CSV)
    assert len(table) == 44 and table.design.nunique() == 35
    state_path = OUT / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    state.update({
        "what": "BoFire default surrogate (SingleTaskGPSurrogate, data-model "
                "defaults), one per objective, leave-one-design-out over the "
                "35 design folds of the round-5 record",
        "driver": "analysis/logocv-baselines/logocv_bofire.py",
        "versions": {p: metadata.version(p) for p in
                     ("bofire", "botorch", "gpytorch", "torch", "pandas", "numpy")},
        "python": sys.version.split()[0],
        "torch_threads": int(torch.get_num_threads()),
        "seed_scheme": "torch.manual_seed(fold_index) before each fit",
        "input_bounds_source": str(BOUNDS_JSON.relative_to(HERE)),
        "observed_values_source": str(TABLE_CSV.relative_to(HERE)),
        "predicted_sem": "posterior sd of the latent function "
                         "(observation_noise=False)",
        "predicted_sd_bofire": "BoFire predict() sd (observation_noise=True, "
                               "the learned noise added)",
    })
    state.setdefault("spaces", {})
    for space in args.spaces:
        _, secs, default = run_space(space, table)
        state["spaces"][space] = {"inputs": SPACES[space], "seconds": round(secs, 1),
                                  "data_model": default}
    OUT.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n")


if __name__ == "__main__":
    main()
