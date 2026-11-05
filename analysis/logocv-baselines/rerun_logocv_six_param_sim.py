"""Re-run the round-5 LOGO-CV in the rounds-1-and-2 six-parameter space
with the #33 simulation outputs appended as extra input features.

PR #121 follow-up (sgbaird, 2026-11-05): "Perform LOGO-CV with 256/512, with
only the 6 (?) original parameters, not the additional print parameters, and
both with and without the simulations as contextual features, and for both
objectives." The "without" half already exists: the audit branch's
``ablation-six-param`` run (vendored here under ``data/ax-runs/``). This
driver adds the "with" half, variant ``six-sim``: R_mm, H_mm, twist_deg,
strut_d_mm, cable_d_mm, mass_printed_g plus the six ``sim_*`` features of
``data/sim-features.csv`` (12 parameters in total, none of them a print
process setting).

The file is ``analysis/cv-signal-audit/rerun_logocv_sim_features.py`` from
branch ``claude/cv-signal-audit-20260922`` at ``6964ac2`` with one base
space added (``six``: ``fit_search_space(include_process=False)`` of the
campaign script, i.e. the five shape coordinates plus weighed printed mass)
and the paths pointed at this directory. Everything else is that driver's
protocol, which is the audit's standard one: the campaign's round-5 Ax
snapshot, ``fit_saasbo`` with ``refit_on_cv=True``, library-default NUTS
(256 samples / 512 warmup), reprint pairs held out together,
``torch.manual_seed(fold_index)`` per fold, ``manual_seed(10000)`` before
the shared initial fit, fold order asserted identical to
``data/ax-runs/full-nuts-rerun/state.json``, feature bounds = observed
range over the 46 design-mapped articles padded by ten percent of the span.

Variants (``--variant``):

- ``six-sim``: the six rounds-1-and-2 parameters plus the six features (12).
  Baseline: ``data/ax-runs/ablation-six-param/``.
- ``six-param``: the six parameters, no features; reproduction check against
  ``data/ax-runs/ablation-six-param/`` (use with ``--only-folds`` and
  ``--out-dir``).
- ``shape-sim``, ``twelve-sim``, ``sim-only``, ``shape-only``: the audit
  driver's own variants, unchanged.

- ``six``, ``twelve``: the six parameters, or the campaign's twelve, with no
  features. For SAASBO these repeat ``ablation-six-param`` and
  ``full-nuts-rerun`` (reproduction checks, need ``--out-dir``); they exist
  for the other surrogates below.

Surrogates (``--model``; PR #121 follow-up, sgbaird, 2026-11-05: "try also
with Ax default and separately also BoFire"). Everything except the model
is the protocol above: same snapshot, same data, same fit space, same folds,
same seeds, ``refit_on_cv=True``.

- ``saasbo`` (default): the campaign's surrogate, ``diag.fit_saasbo``.
- ``ax-default``: what Ax 0.5.0 fits when nobody chooses a model.
  ``AxClient`` without a generation strategy calls
  ``choose_generation_strategy``, which for this all-continuous space gives
  Sobol and then ``Models.BOTORCH_MODULAR`` with the default surrogate
  (``SingleTaskGP``, BoTorch 0.13's dimension-scaled lognormal lengthscale
  prior, MAP fit) and a ``Winsorize`` transform in front of the usual ones.
  The model kwargs are taken from that BoTorch step verbatim. With two
  minimized objectives and no objective thresholds, ``Winsorize`` clips each
  objective's upper tail at the Tukey fence (Q3 + 1.5 IQR) before the fit.
- ``ax-registry``: ``Models.BOTORCH_MODULAR`` with the registry's own
  transforms (no ``Winsorize``), i.e. exactly the SAASBO transform stack with
  only the BoTorch model class changed.

For the two MAP models ``warm_start_refit`` is set False, so each fold's
hyperparameters are optimized from the prior's starting point and not from
the full-data optimum (Ax's default warm start would carry information about
the held-out design into the fold). SAASBO's NUTS refit draws afresh, so it
is unaffected and keeps the archived setting.

Noise (``--noise``): ``known`` (default) passes the archived per-article SEMs
as Ax's known observation noise, as the campaign did; ``inferred`` blanks
them (``sem = NaN``) so the GP learns one noise level per objective.

Output directory: ``data/ax-<variant>/`` for SAASBO with known noise (the
existing runs), ``data/ax-saasbo-inferred-noise-<variant>/`` for SAASBO with
the noise inferred, otherwise ``data/<model>[-inferred-noise]-<variant>/``
(``data/ax-default-six/``, ``data/ax-registry-twelve/``, ...).

Usage (repo root; campaign ``bo/`` tree extracted at ``bbf7a62``)::

    git archive bbf7a62 bo | tar -x -C /tmp/campaign
    for i in 0 1 2 3; do
      python analysis/logocv-baselines/rerun_logocv_six_param_sim.py \
          --campaign-bo /tmp/campaign/bo --variant six-sim --queue \
          --threads 1 --commit-each-fold &
    done; wait
    python analysis/logocv-baselines/rerun_logocv_six_param_sim.py \
        --campaign-bo /tmp/campaign/bo --variant six-sim --assemble \
        --commit-each-fold

    # Ax default (MAP, seconds per fold): fold loop, then assembly
    for v in six six-sim twelve; do
      python analysis/logocv-baselines/rerun_logocv_six_param_sim.py \
          --campaign-bo /tmp/campaign/bo --model ax-default --variant $v
      python analysis/logocv-baselines/rerun_logocv_six_param_sim.py \
          --campaign-bo /tmp/campaign/bo --model ax-default --variant $v --assemble
    done
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
FEATURES_CSV = HERE / "data" / "sim-features.csv"
PAYLOAD_CSV = HERE / "data" / "payload-objectives.csv"  # not vendored; campaign pair only
FULLNUTS_STATE = HERE / "data" / "ax-runs" / "full-nuts-rerun" / "state.json"
PUSH_SCRIPT = Path(
    "/home/runner/work/_actions/anthropics/claude-code-action/v1/scripts/git-push.sh"
)
COMMIT_TRAILER = (
    "\n\nCo-authored-by: Sterling G. Baird "
    "<45469701+sgbaird@users.noreply.github.com>"
    "\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
)

FEATURES = (
    "sim_tierC_t180",
    "sim_tierC_tendon_energy_mJ",
    "sim_tierC_stroke_mm",
    "sim_tierB_t180",
    "sim_tierB_fn_hz",
    "sim_tierB_zeta_pct",
)
BOUNDS_PAD = 0.10
VARIANTS = {
    "six-sim": dict(base="six", features=True,
                    note="the rounds-1-and-2 six parameters (five shape "
                         "coordinates plus weighed printed mass) plus the "
                         "six simulation features"),
    "six-param": dict(base="six", features=False,
                      note="the rounds-1-and-2 six parameters (reproduction "
                           "check)"),
    "shape-sim": dict(base="shape", features=True,
                      note="the five shape coordinates plus the six "
                           "simulation features"),
    "twelve-sim": dict(base="twelve", features=True,
                       note="the campaign's twelve parameters plus the six "
                            "simulation features"),
    "sim-only": dict(base="none", features=True,
                     note="the six simulation features alone"),
    "shape-only": dict(base="shape", features=False,
                       note="the five shape coordinates (reproduction check)"),
    "six": dict(base="six", features=False,
                note="the rounds-1-and-2 six parameters (five shape "
                     "coordinates plus weighed printed mass)"),
    "twelve": dict(base="twelve", features=False,
                   note="the campaign's twelve parameters"),
}
MODELS = ("saasbo", "ax-default", "ax-registry")
MODEL_NOTE = {
    "saasbo": "SAASBO (Models.SAASBO, SaasFullyBayesianSingleTaskGP, NUTS)",
    "ax-default": "Ax default: the BoTorch step of choose_generation_strategy "
                  "(Models.BOTORCH_MODULAR, default surrogate SingleTaskGP, "
                  "MAP fit, Winsorize + MBM_X_trans + Y_trans)",
    "ax-registry": "Models.BOTORCH_MODULAR with the registry transforms "
                   "(MBM_X_trans + Y_trans, the SAASBO stack), default "
                   "surrogate SingleTaskGP, MAP fit",
}
PAYLOAD = ("tavg10ms", "late_avg3ms_g")

OUT_DIR = STATE_PATH = FOLDS_PATH = LOCK_PATH = None


@contextmanager
def _locked():
    """Serialize checkpoint writes and git operations across shard workers."""
    with open(LOCK_PATH, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _git_commit_push(paths, message, push=True):
    """Commit checkpoint files; never let a git hiccup kill the run."""
    try:
        repo_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        subprocess.run(["git", "add", *[str(p) for p in paths]],
                       cwd=repo_root, check=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_root)
        if diff.returncode == 0:
            return  # nothing staged
        subprocess.run(["git", "commit", "-q", "-m", message + COMMIT_TRAILER],
                       cwd=repo_root, check=True)
        if push and PUSH_SCRIPT.exists():
            r = subprocess.run([str(PUSH_SCRIPT), "origin", "HEAD"], cwd=repo_root,
                               capture_output=True, text=True)
            if r.returncode != 0:
                subprocess.run(["git", "pull", "-q", "--rebase", "--autostash",
                                "origin", branch],
                               cwd=repo_root, check=True)
                subprocess.run([str(PUSH_SCRIPT), "origin", "HEAD"],
                               cwd=repo_root, check=True, capture_output=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  WARNING: checkpoint commit/push failed ({exc}); "
              "data is on disk, continuing", flush=True)


def _obs_data_to_dict(od):
    return {
        "metric_names": list(od.metric_names),
        "means": [float(v) for v in od.means],
        "covariance": [[float(v) for v in row] for row in od.covariance],
    }


def _obs_data_from_dict(d):
    from ax.core.observation import ObservationData

    return ObservationData(
        metric_names=list(d["metric_names"]),
        means=np.asarray(d["means"], dtype=float),
        covariance=np.asarray(d["covariance"], dtype=float),
    )


def _read_folds():
    by_key = {}
    if FOLDS_PATH.exists():
        with FOLDS_PATH.open() as fh:
            for line in fh:
                rec = json.loads(line)
                by_key[rec["fold_key"]] = rec
    return by_key


def _cv_results_from_jsonl(fold_keys):
    """Rebuild the CVResult list in canonical fold order from the checkpoint."""
    from ax.core.observation import Observation, ObservationFeatures
    from ax.modelbridge.cross_validation import CVResult

    by_key = _read_folds()
    results = []
    for gkey in fold_keys:
        for art in by_key[gkey]["articles"]:
            obs = Observation(
                features=ObservationFeatures(parameters=dict(art["parameters"])),
                data=_obs_data_from_dict(art["observed"]),
                arm_name=art["arm_name"],
            )
            results.append(
                CVResult(observed=obs, predicted=_obs_data_from_dict(art["predicted"]))
            )
    return results


def feature_bounds(table: pd.DataFrame) -> dict:
    out = {}
    for f in FEATURES:
        lo, hi = float(table[f].min()), float(table[f].max())
        pad = BOUNDS_PAD * (hi - lo)
        out[f] = [lo - pad, hi + pad]
    return out


def assemble(args, names, diag, labels_by_arm, n_articles, n_params, keep,
             t_start, run_label):
    """Rebuild the run in canonical fold order and write the campaign-format
    CSV, diagnostics JSON and parity PNG. Reads only the checkpoint."""
    with _locked():
        done = set(_read_folds())
        fold_keys = json.loads(STATE_PATH.read_text())["fold_keys"]
        if done != set(fold_keys):
            print(f"RESUME_NEEDED: {len(done)}/{len(fold_keys)} folds done",
                  flush=True)
            return 0
        cv_results = _cv_results_from_jsonl(fold_keys)
        by_key = _read_folds()
        FOLDS_PATH.write_text("".join(json.dumps(by_key[g]) + "\n"
                                      for g in fold_keys))

    diag.METRIC_ORDER = list(names)
    label = {"t180": "t180", "e_reb_mJ": "Rebound",
             "tavg10ms": "tavg10ms", "late_avg3ms_g": "late_avg3ms"}
    title = {"t180": "t180", "e_reb_mJ": "Rebound energy",
             "tavg10ms": "10 ms dose ratio", "late_avg3ms_g": "Hop landing"}
    diag.METRIC_LABEL = {n: f"{label[n]}\n(raw)" for n in names}
    diag.METRIC_TITLE = {n: f"{title[n]}, raw" for n in names}
    diag.METRIC_COLOR = dict(zip(names, ("#1f77b4", "#e8590c")))

    diagnostics_path = OUT_DIR / "t3-prism-bo-round5-logocv-diagnostics.json"
    table_out, diagnostics = diag._cv_table(cv_results, labels_by_arm,
                                            diagnostics_path)
    table_out.to_csv(OUT_DIR / "t3-prism-bo-round5-logocv.csv", index=False,
                     float_format="%.9g")
    diag.render_loocv(table_out, diagnostics,
                      OUT_DIR / "t3-prism-bo-round5-logocv.png",
                      n_articles=n_articles,
                      note=diag.LOGOCV_NOTE + f"\nObjectives raw; fit space: "
                      f"{n_params} parameters, {VARIANTS[args.variant]['note']}."
                      + ("" if args.model == "saasbo" and args.noise == "known"
                         else f"\nSurrogate: {MODEL_NOTE[args.model]}; noise "
                              f"{args.noise}."))
    state = json.loads(STATE_PATH.read_text())
    state["status"] = "complete"
    state["total_fold_seconds"] = round(sum(state["fold_seconds"].values()), 1)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
    for name in ("MAPE", "Correlation coefficient", "Rank correlation"):
        if name in diagnostics:
            values = {m: round(float(v), 4) for m, v in diagnostics[name].items()}
            print(f"  {name}: {values}", flush=True)
    if args.commit_each_fold:
        with _locked():
            _git_commit_push(
                [OUT_DIR],
                f"LOGO-CV {run_label} complete: {len(fold_keys)} folds"
                + (f" at {args.num_samples}/{args.warmup_steps}"
                   if args.model == "saasbo" else ""),
            )
    print(f"ALL_FOLDS_DONE ({time.time() - t_start:.0f} s)", flush=True)
    return 0


def fit_model(args, diag, experiment, data):
    """The initial fit, with the model spec every fold refits with."""
    if args.model == "saasbo":
        model = diag.fit_saasbo(experiment, data, args.num_samples,
                                args.warmup_steps, refit_on_cv=True)
        return model, {"num_samples": args.num_samples,
                       "warmup_steps": args.warmup_steps}
    from ax.modelbridge.registry import Models

    t0 = time.time()
    if args.model == "ax-default":
        from ax.modelbridge.dispatch_utils import choose_generation_strategy

        gs = choose_generation_strategy(
            search_space=experiment.search_space,
            optimization_config=experiment.optimization_config,
            experiment=experiment,
        )
        steps = [st for st in gs._steps if st.model == Models.BOTORCH_MODULAR]
        assert len(steps) == 1, gs
        kwargs = dict(steps[0].model_kwargs or {})
        info = {
            "generation_strategy": str(gs),
            "transforms": [t.__name__ for t in kwargs.get("transforms", [])],
            "transform_configs": kwargs.get("transform_configs"),
            "fit_out_of_design": kwargs.get("fit_out_of_design"),
        }
    else:
        kwargs = {}
        info = {"transforms": "registry default for Models.BOTORCH_MODULAR"}
    model = Models.BOTORCH_MODULAR(
        experiment=experiment, data=data, refit_on_cv=True,
        warm_start_refit=bool(args.warm_start_refit), **kwargs)
    surrogate = model.model.surrogate
    info.update({
        "botorch_model": type(surrogate.model).__name__,
        "submodels": [type(m).__name__ for m in
                      getattr(surrogate.model, "models", [surrogate.model])],
        "likelihoods": [type(m.likelihood).__name__ for m in
                        getattr(surrogate.model, "models", [surrogate.model])],
        "transforms_applied": [type(t).__name__ for t in model.transforms.values()],
        "refit_on_cv": True,
        "warm_start_refit": bool(args.warm_start_refit),
        "full_data_hyperparameters": _hypers(surrogate.model, model),
    })
    if "Winsorize" in model.transforms:
        info["winsorize_cutoffs_full_data"] = {
            m: [float(c) for c in v]
            for m, v in model.transforms["Winsorize"].cutoffs.items()}
    print(f"  {args.model}: {info['submodels']} with {info['likelihoods']}, "
          f"transforms {info['transforms_applied']}, fit in "
          f"{time.time() - t0:.1f} s", flush=True)
    return model, info


def _hypers(botorch_model, bridge):
    """Lengthscales (in the model's normalized input units) and noise of a
    fitted MAP model, per outcome. Handles a ``ModelListGP`` and a batched
    multi-output ``SingleTaskGP`` (Ax's ``allow_batched_models``)."""
    subs = getattr(botorch_model, "models", None)
    if subs is not None:
        pairs = [(name, sub, None) for name, sub in zip(bridge.outcomes, subs)]
    else:
        batched = getattr(botorch_model, "num_outputs", 1) > 1
        pairs = [(name, botorch_model, i if batched else None)
                 for i, name in enumerate(bridge.outcomes)]
    out = {}
    for name, sub, idx in pairs:
        kern = sub.covar_module
        base = getattr(kern, "base_kernel", kern)
        ls = base.lengthscale.detach()
        ls = ls[idx] if idx is not None else ls
        rec = {"kernel": type(base).__name__,
               "lengthscale": [round(float(v), 5) for v in ls.reshape(-1)]}
        if hasattr(kern, "outputscale"):
            os_ = kern.outputscale.detach()
            os_ = os_[idx] if idx is not None and os_.dim() else os_
            rec["outputscale"] = round(float(os_.reshape(-1)[0]), 5)
        lik = sub.likelihood
        rec["likelihood"] = type(lik).__name__
        if type(lik).__name__ == "GaussianLikelihood":
            noise = lik.noise.detach()
            noise = noise[idx] if idx is not None and noise.dim() > 1 else noise
            rec["noise_standardized"] = float(noise.reshape(-1)[0])
        out[name] = rec
    return out


def _last_fold_hypers(bridge):
    """Ax's ``cross_validate`` refits a clone and discards it; the fold's
    hyperparameters are recovered from the clone's state, which the patched
    ``ModularBoTorchModel.cross_validate`` below stores on the model."""
    model = bridge.model
    saved = getattr(model, "_last_cv_surrogate_model", None)
    return None if saved is None else _hypers(saved, bridge)


def _patch_cv_capture():
    """Keep a handle on the surrogate model each CV refit produced (Ax 0.5.0
    restores the full-data surrogate in a ``finally`` and drops the clone)."""
    from ax.models.torch.botorch_modular.model import (
        BoTorchModel as ModularBoTorchModel,
    )

    if getattr(ModularBoTorchModel, "_cv_capture_patched", False):
        return
    original_predict = ModularBoTorchModel.predict

    def predict(self, X, use_posterior_predictive=False):
        self._last_cv_surrogate_model = self.surrogate.model
        return original_predict(self, X, use_posterior_predictive=use_posterior_predictive)

    ModularBoTorchModel.predict = predict
    ModularBoTorchModel._cv_capture_patched = True


def _patch_winsorize_writable():
    """Compatibility shim, no change in behaviour: Ax 0.5.0's ``Winsorize``
    clips ``ObservationData.means`` in place, and under pandas >= 3
    (copy-on-write) those arrays arrive read-only, which raises
    "assignment destination is read-only". Hand it a writable copy."""
    from ax.modelbridge.transforms.winsorize import Winsorize

    if getattr(Winsorize, "_writable_patched", False):
        return
    original = Winsorize._transform_observation_data

    def _transform_observation_data(self, observation_data):
        for obsd in observation_data:
            if not obsd.means.flags.writeable:
                obsd.means = np.array(obsd.means, dtype=float, copy=True)
        return original(self, observation_data)

    Winsorize._transform_observation_data = _transform_observation_data
    Winsorize._writable_patched = True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign-bo", type=Path, required=True,
                    help="path to the extracted campaign bo/ directory")
    ap.add_argument("--variant", choices=sorted(VARIANTS), required=True)
    ap.add_argument("--model", choices=MODELS, default="saasbo",
                    help="surrogate (see the module docstring)")
    ap.add_argument("--warm-start-refit", action="store_true",
                    help="MAP models: start each fold's refit from the full-data "
                         "optimum (Ax's own default; leaks, off unless asked)")
    ap.add_argument("--noise", choices=("known", "inferred"), default="known",
                    help="known: archived SEMs as fixed noise (the campaign); "
                         "inferred: SEMs blanked, noise learned")
    ap.add_argument("--objectives", choices=("campaign", "payload"),
                    default="campaign")
    ap.add_argument("--shard", default="0/1",
                    help="i/n: run fold indices i+1, i+1+n, ... (1-based)")
    ap.add_argument("--only-folds", default="",
                    help="comma-separated fold keys to run (reproduction check)")
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="override the output directory")
    ap.add_argument("--threads", type=int, default=0,
                    help="torch.set_num_threads (0 = library default)")
    ap.add_argument("--max-seconds", type=float, default=3000,
                    help="clean-exit budget for this invocation")
    ap.add_argument("--num-samples", type=int, default=256,
                    help="NUTS samples per fold (BoTorch library default)")
    ap.add_argument("--warmup-steps", type=int, default=512,
                    help="NUTS warmup per fold (BoTorch library default)")
    ap.add_argument("--commit-each-fold", action="store_true",
                    help="git commit+push the checkpoint after every fold")
    ap.add_argument("--commit-every", type=int, default=1,
                    help="with --commit-each-fold: commit only when the number "
                         "of finished folds is a multiple of this")
    ap.add_argument("--assemble", action="store_true",
                    help="all folds done: write the campaign-format outputs")
    ap.add_argument("--queue", action="store_true",
                    help="work-queue mode: take the next fold nobody has done or "
                         "claimed (claims live in /tmp), instead of a fixed shard")
    ap.add_argument("--reverse", action="store_true",
                    help="walk the fold list from the end")
    args = ap.parse_args(argv)
    t_start = time.time()
    variant = VARIANTS[args.variant]
    run_label = f"{args.variant}, {args.objectives} pair"
    if args.model != "saasbo" or args.noise != "known":
        run_label = (f"{args.model}"
                     f"{', noise inferred' if args.noise == 'inferred' else ''}, "
                     + run_label)

    global OUT_DIR, STATE_PATH, FOLDS_PATH, LOCK_PATH
    shard_i, shard_n = (int(v) for v in args.shard.split("/"))
    assert 0 <= shard_i < shard_n, args.shard
    if (args.model, args.noise) == ("saasbo", "known"):
        out_name = f"ax-{args.variant}"
    else:
        out_name = (("ax-saasbo" if args.model == "saasbo" else args.model)
                    + ("-inferred-noise" if args.noise == "inferred" else "")
                    + f"-{args.variant}")
    out_name += "-payload" if args.objectives == "payload" else ""
    OUT_DIR = args.out_dir or HERE / "data" / out_name
    if not variant["features"] and args.model == "saasbo" and args.noise == "known":
        assert args.out_dir is not None, "reproduction check needs --out-dir"
    STATE_PATH = OUT_DIR / "state.json"
    FOLDS_PATH = OUT_DIR / "folds.jsonl"
    # one lock for every worker of every run: they share the git index
    LOCK_PATH = Path("/tmp") / "rerun_logocv_six_param_sim.lock"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    import torch

    if args.threads:
        torch.set_num_threads(args.threads)

    sys.path.insert(0, str(args.campaign_bo.resolve()))
    import t3_prism_bo_diagnostics as diag  # noqa: E402
    from t3_prism_bo_campaign import (  # noqa: E402
        BO_DIR,
        PARAM_NAMES,
        fit_search_space,
        load_round2_training_data,
        load_round3_reprint_training_data,
        load_round3_training_data,
        load_round4_training_data,
        load_training_data,
        repeat_group,
    )

    # ---- model setup: replica of the campaign script's main() ------------
    from ax.service.ax_client import AxClient

    snapshot = args.campaign_bo / "t3-prism-bo-ax-client-round5.json"
    ax_client = AxClient.load_from_json_file(str(snapshot))
    experiment = ax_client.experiment
    has_process = "pla_nozzle_temp_C" in experiment.search_space.parameters
    data = experiment.fetch_data()

    X1, _, labels1, _, _ = load_training_data(
        BO_DIR / "t3-prism-bo-batch-drop-results.csv",
        BO_DIR / "t3-prism-bo-batch.csv", process=None)
    X2, _, labels2, _, _ = load_round2_training_data(process=None)
    X3, _, labels3, _, _ = load_round3_training_data(include_process=has_process)
    X3r, _, labels3r, _, _ = load_round3_reprint_training_data(include_process=has_process)
    X4, _, labels4, _, _ = load_round4_training_data(include_process=has_process)
    X_all = X1 + X2 + X3 + X3r + X4
    labels_all = labels1 + labels2 + labels3 + labels3r + labels4
    labels_by_arm = {}
    for trial in experiment.trials.values():
        arm = trial.arm
        for x, label in zip(X_all, labels_all):
            if all(abs(float(arm.parameters[k]) - float(v)) < 1e-6
                   for k, v in x.items()):
                labels_by_arm[arm.name] = label.split(" ")[0]
                break
    n_articles = int(data.df["arm_name"].nunique())
    print(f"Loaded {snapshot.name}: {len(data.df)} observations, "
          f"{n_articles} tested articles, {len(labels_by_arm)} labeled",
          flush=True)

    # ---- objectives -------------------------------------------------------
    if args.objectives == "campaign":
        names = tuple(sorted(data.df["metric_name"].unique()))
        assert set(names) == {"t180", "e_reb_mJ"}, names
        objective_note = "the campaign pair as fitted in the round-5 snapshot"
    else:
        from ax.core.data import Data
        from ax.core.metric import Metric

        names = PAYLOAD
        table = pd.read_csv(PAYLOAD_CSV).set_index("print_id")
        seen = data.df[["trial_index", "arm_name"]].drop_duplicates()
        rows, matched = [], []
        for r in seen.itertuples():
            pid = labels_by_arm.get(r.arm_name)
            if pid is None or pid not in table.index:
                raise RuntimeError(f"arm {r.arm_name} (print {pid}) has no "
                                   "objective values; refusing to run")
            matched.append(pid)
            for n in names:
                rows.append({"trial_index": int(r.trial_index),
                             "arm_name": r.arm_name, "metric_name": n,
                             "mean": float(table.loc[pid, f"{n}_mean"]),
                             "sem": float(table.loc[pid, f"{n}_sem"])})
        new_df = pd.DataFrame(rows)
        assert len(matched) == n_articles == 44, (len(matched), n_articles)
        assert new_df["mean"].notna().all() and new_df["sem"].notna().all()
        assert (new_df["sem"] > 0).all()
        known = set(experiment.metrics)
        experiment.add_tracking_metrics(
            [Metric(name=n, lower_is_better=True) for n in names if n not in known])
        data = Data(df=new_df)
        objective_note = ("untransformed payload pair, values from "
                          "payload-objectives.csv")
        print(f"Objectives swapped to {names} for {len(matched)} articles",
              flush=True)

    if args.noise == "inferred":
        from ax.core.data import Data

        # blank the archived SEMs: the GP then learns one noise level per
        # objective instead of taking the per-article SEMs as known
        data = Data(df=data.df.assign(sem=np.nan))
        objective_note += "; SEMs blanked (noise inferred)"
        print("Noise: inferred (archived SEMs blanked)", flush=True)

    # ---- the fit space: base coordinates plus the simulation features -----
    from ax.core.parameter import ParameterType, RangeParameter
    from ax.core.search_space import SearchSpace

    base_space = fit_search_space(include_process=True)
    if variant["base"] == "shape":
        keep = list(PARAM_NAMES)
    elif variant["base"] == "six":
        keep = list(fit_search_space(include_process=False).parameters)
        assert keep == list(PARAM_NAMES) + ["mass_printed_g"], keep
    elif variant["base"] == "twelve":
        keep = list(base_space.parameters)
    else:
        keep = []
    missing = [k for k in keep
               if any(k not in a.parameters
                      for a in experiment.arms_by_name.values())]
    assert not missing, f"arms lack {missing}"

    feats = list(FEATURES) if variant["features"] else []
    bounds, placeholder_arms = {}, []
    if feats:
        ftable = pd.read_csv(FEATURES_CSV).set_index("print_id")
        bounds = feature_bounds(ftable)
        tested = set(data.df["arm_name"])
        unmatched = [a for a in tested if labels_by_arm.get(a) not in ftable.index]
        assert not unmatched, f"tested arms without simulation features: {unmatched}"
        # the snapshot also carries the round-5 candidate arms (generated,
        # never printed, no data); they never enter a fit, but every arm
        # needs a complete parameterization, so they get the table mean
        placeholder_arms = [a for a in experiment.arms_by_name if a not in tested]
        placeholder = {f: float(ftable[f].mean()) for f in feats}
    params = [base_space.parameters[name] for name in keep] + [
        RangeParameter(name=f, parameter_type=ParameterType.FLOAT,
                       lower=bounds[f][0], upper=bounds[f][1]) for f in feats]
    experiment._search_space = SearchSpace(parameters=params)
    for name, arm in experiment.arms_by_name.items():
        pid = labels_by_arm.get(name)
        new = {k: arm._parameters[k] for k in keep}
        if feats:
            new.update(placeholder if name in placeholder_arms
                       else {f: float(ftable.loc[pid, f]) for f in feats})
        arm._parameters = new
    if placeholder_arms:
        print(f"  {len(placeholder_arms)} untested candidate arms carry "
              "placeholder features (no data, never fitted)", flush=True)
    if experiment.status_quo is not None:
        sq = experiment.status_quo
        twin = experiment.arms_by_name.get(sq.name)
        assert twin is not None, "status quo arm is not a tested arm"
        sq._parameters = dict(twin._parameters)
    n_params = len(keep) + len(feats)
    print(f"Fit space ({args.variant}): {n_params} parameters "
          f"({', '.join(keep + feats)})", flush=True)
    for f in feats:
        print(f"  {f}: bounds {bounds[f][0]:.6g} to {bounds[f][1]:.6g}",
              flush=True)

    # ---- assembly needs no model: go straight there -----------------------
    if args.assemble:
        return assemble(args, names, diag, labels_by_arm, n_articles,
                        n_params, keep + feats, t_start, run_label)

    # ---- initial fit (same spec the folds refit with) --------------------
    if args.model != "saasbo":
        _patch_cv_capture()
        _patch_winsorize_writable()
    torch.manual_seed(10_000)
    cv_model, model_info = fit_model(args, diag, experiment, data)
    assert set(cv_model.outcomes) == set(names), cv_model.outcomes
    assert len(cv_model.parameters) == n_params, cv_model.parameters

    training_data = cv_model.get_training_data()
    assert len(training_data) == n_articles, (
        f"{n_articles - len(training_data)} observations dropped; "
        "refusing to continue")
    group_of = {
        obs.arm_name: repeat_group(labels_by_arm.get(obs.arm_name, obs.arm_name))
        for obs in training_data
    }
    fold_keys = list(dict.fromkeys(group_of[obs.arm_name] for obs in training_data))
    reference = json.loads(FULLNUTS_STATE.read_text())["fold_keys"]
    assert fold_keys == reference, (
        "fold order differs from data/full-nuts-rerun/state.json; the "
        "per-fold seeds would no longer be comparable")

    # ---- checkpoint state ------------------------------------------------
    fresh_state = {
        "variant": args.variant,
        "variant_note": variant["note"],
        "objectives": list(names),
        "objective_note": objective_note,
        "n_params": n_params,
        "kept_parameters": keep,
        "sim_features": feats,
        "sim_feature_bounds": bounds,
        "sim_feature_source": str(FEATURES_CSV.relative_to(HERE)),
        "untested_arms_with_placeholder_features": placeholder_arms,
        "sim_feature_note": "Tier C / Tier B drop-tower simulators from the "
                            "sim branch at 94e53a8, run at the design's print "
                            "geometry with the simulator's own mass model, so "
                            "reprint twins share every feature",
        "model": args.model,
        "model_note": MODEL_NOTE[args.model],
        "model_info": model_info,
        "noise": args.noise,
        "num_samples": args.num_samples,
        "warmup_steps": args.warmup_steps,
        "seed_scheme": "torch.manual_seed(fold_index) per fold, "
                       "manual_seed(10000) before the shared initial fit "
                       "(identical to the full-nuts-rerun protocol; fold order "
                       "asserted equal to full-nuts-rerun); folds split across "
                       "worker processes, each repeating the seeded initial fit",
        "snapshot": snapshot.name,
        "campaign_branch": "claude/issue-98-20260821-0103",
        "campaign_code_commit": "bbf7a62",
        "driver": "analysis/logocv-baselines/rerun_logocv_six_param_sim.py "
                  "(analysis/cv-signal-audit/rerun_logocv_sim_features.py at "
                  "6964ac2 plus the six-parameter base space)",
        "torch_threads": int(torch.get_num_threads()),
        "fold_keys": fold_keys,
        "fold_seconds": {},
        "status": "running",
    }
    with _locked():
        if STATE_PATH.exists():
            state = json.loads(STATE_PATH.read_text())
            if state["fold_keys"] != fold_keys:
                raise RuntimeError("fold keys changed between invocations")
            if (state["num_samples"], state["warmup_steps"]) != (
                    args.num_samples, args.warmup_steps):
                raise RuntimeError("NUTS settings changed between invocations")
            if state["objectives"] != list(names):
                raise RuntimeError("objectives changed between invocations")
            if state["variant"] != args.variant:
                raise RuntimeError("variant changed between invocations")
            if (state.get("model", "saasbo"), state.get("noise", "known")) != (
                    args.model, args.noise):
                raise RuntimeError("model or noise changed between invocations")
        else:
            STATE_PATH.write_text(json.dumps(fresh_state, indent=2) + "\n")
        done = set(_read_folds())

    wanted = [(k, g) for k, g in enumerate(fold_keys, start=1)
              if (k - 1) % shard_n == shard_i]
    if args.only_folds:
        only = set(args.only_folds.split(","))
        assert only <= set(fold_keys), only - set(fold_keys)
        wanted = [(k, g) for k, g in wanted if g in only]
    todo = [(k, g) for k, g in wanted if g not in done]
    if args.reverse:
        todo = todo[::-1]
    print(f"{len(fold_keys)} design folds over {len(training_data)} articles; "
          f"{len(done)} already checkpointed; shard {shard_i}/{shard_n} has "
          f"{len(todo)} to run", flush=True)

    # ---- fold loop (run_group_cv, checkpointed) --------------------------
    slowest = 0.0
    claims_path = Path("/tmp") / f"{OUT_DIR.name}.claims.json"

    def _claim(gkey):
        """Queue mode: atomically take a fold nobody has done or claimed."""
        with _locked():
            if gkey in _read_folds():
                return False
            claims = (json.loads(claims_path.read_text())
                      if claims_path.exists() else {})
            owner = claims.get(gkey)
            if owner is not None and owner != os.getpid():
                try:
                    os.kill(owner, 0)
                    return False          # a live worker has it
                except OSError:
                    pass                  # stale claim from a dead worker
            claims[gkey] = os.getpid()
            claims_path.write_text(json.dumps(claims))
            return True

    for k, gkey in todo:
        if args.queue and not _claim(gkey):
            continue
        elapsed = time.time() - t_start
        if slowest and elapsed + slowest > args.max_seconds:
            print(f"RESUME_NEEDED: shard {shard_i}/{shard_n} stopping at "
                  f"{elapsed:.0f} s, next fold would overrun "
                  f"--max-seconds {args.max_seconds:.0f}", flush=True)
            return 0
        test = [obs for obs in training_data if group_of[obs.arm_name] == gkey]
        train = [obs for obs in training_data if group_of[obs.arm_name] != gkey]
        torch.manual_seed(k)
        t_fold = time.time()
        preds = cv_model.cross_validate(
            cv_training_data=train,
            cv_test_points=[deepcopy(obs.features) for obs in test],
        )
        dt = time.time() - t_fold
        slowest = max(slowest, dt)
        rec = {
            "fold_key": gkey,
            "fold_index": k,
            "seconds": round(dt, 1),
            **({"hyperparameters": _last_fold_hypers(cv_model)}
               if args.model != "saasbo" else {}),
            "articles": [
                {
                    "arm_name": obs.arm_name,
                    "print_id": labels_by_arm.get(obs.arm_name, obs.arm_name),
                    "parameters": {p: float(v)
                                   for p, v in obs.features.parameters.items()},
                    "observed": _obs_data_to_dict(obs.data),
                    "predicted": _obs_data_to_dict(pred),
                }
                for obs, pred in zip(test, preds)
            ],
        }
        with _locked():
            with FOLDS_PATH.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            state = json.loads(STATE_PATH.read_text())
            state["fold_seconds"][gkey] = round(dt, 1)
            STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
            n_done = len(_read_folds())
            print(f"    fold {k}/{len(fold_keys)} ({gkey}, {len(test)} article"
                  f"{'s' if len(test) > 1 else ''}) in {dt:.0f} s; "
                  f"{n_done}/{len(fold_keys)} done", flush=True)
            if args.commit_each_fold and (
                    n_done % max(args.commit_every, 1) == 0
                    or n_done == len(fold_keys)):
                _git_commit_push(
                    [FOLDS_PATH, STATE_PATH],
                    f"LOGO-CV {run_label}: "
                    f"fold {n_done}/{len(fold_keys)} ({gkey})",
                )

    print("SHARD_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
