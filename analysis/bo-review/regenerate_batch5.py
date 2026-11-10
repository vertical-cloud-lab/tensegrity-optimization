"""Regenerate batch 5 with the campaign script, changing only the acquisition setup.

PR #121 (sgbaird, 2026-11-10), on Juan Florez-Coronel's review of the BO
methods:

* "Set these thresholds and see how that affects the batch 5 suggested
  experiments." ``--thresholds`` gives both objectives an explicit
  ``ObjectiveProperties(threshold=...)`` at the campaign's own hypervolume
  reference (``REBOUND_FORMS[form]["hv_ref"]``: (1.35, 15 mJ) for ``me``,
  (1.35, 50 mg) for ``me2``) and pins ``botorch_acqf_class`` to
  ``qLogNoisyExpectedHypervolumeImprovement`` (already Ax 0.5.0's default
  for two objectives, so the pin documents rather than changes it).
* ``--learned-noise`` (item 1): every objective goes to Ax as ``(mean,
  None)``, so the GP learns one noise level per objective instead of taking
  the per-article SEMs as known.
* "Honegumi with fixed_features should be able to take care of this."
  ``--fixed-filament`` hands the batch's filament point (the same seeded
  Sobol point the script would substitute afterwards) to
  ``AxClient.get_next_trials(fixed_features=...)``, so the acquisition
  optimizes the other eight coordinates around it instead of having its
  filament choice overwritten after the fact.

Nothing else changes: same campaign code, data, seed, target mass and
batch size. Every variant refits the same model with the same seed (the
fit does not depend on thresholds or fixed features), so differences
between variants come from the acquisition, not from MCMC.

The campaign script writes its outputs next to itself, so each variant runs
on its own copy of the ``bo/`` tree::

    git archive origin/claude/me2-objective-bo-20261029 bo | tar -x -C /tmp/b5-control
    python analysis/bo-review/regenerate_batch5.py --campaign-bo /tmp/b5-control/bo \
        --rebound-form me2 --tag control
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--campaign-bo", type=Path, required=True)
ap.add_argument("--rebound-form", choices=("me", "me2"), default="me2")
ap.add_argument("--thresholds", action="store_true")
ap.add_argument("--fixed-filament", action="store_true")
ap.add_argument("--learned-noise", action="store_true",
                help="report each objective as (mean, None) so Ax learns the noise "
                     "instead of taking the SEMs as known (item 1 of the review)")
ap.add_argument("--seed", type=int, default=42)
ap.add_argument("--threads", type=int, default=1)
ap.add_argument("--tag", required=True)
ap.add_argument("--out", type=Path, required=True,
                help="JSON record of the run (thresholds used, inferred, filament point)")
args = ap.parse_args()

import torch  # noqa: E402

torch.set_num_threads(args.threads)
sys.path.insert(0, str(args.campaign_bo.resolve()))
import t3_prism_bo_campaign as camp  # noqa: E402
import ax.modelbridge.generation_strategy as gsmod  # noqa: E402
from ax.service.ax_client import AxClient, ObjectiveProperties  # noqa: E402
from ax.service.utils.instantiation import FixedFeatures  # noqa: E402
from botorch.acquisition.multi_objective.logei import (  # noqa: E402
    qLogNoisyExpectedHypervolumeImprovement,
)

ROUND, BATCH = 6, 5   # run 6 = batch 5 regenerated (the me2 branch's numbering)
record = {"tag": args.tag, "rebound_form": args.rebound_form,
          "thresholds_set": args.thresholds, "fixed_filament": args.fixed_filament,
          "learned_noise": args.learned_noise,
          "seed": args.seed, "threads": args.threads}

_orig_create = AxClient.create_experiment


def create_experiment(self, *a, **kw):
    if args.thresholds:
        names = list(kw["objectives"])
        ref = camp.REBOUND_FORMS[args.rebound_form]["hv_ref"]
        kw["objectives"] = {n: ObjectiveProperties(minimize=True, threshold=float(r))
                            for n, r in zip(names, ref)}
        record["thresholds"] = dict(zip(names, map(float, ref)))
    return _orig_create(self, *a, **kw)


AxClient.create_experiment = create_experiment

_orig_gs_init = gsmod.GenerationStrategy.__init__


def gs_init(self, steps, *a, **kw):
    if args.thresholds:
        for step in steps:
            # GenerationStep.model_kwargs is a read-only view of its model
            # spec's kwargs dict in Ax 0.5.0; update that dict in place
            step.model_specs[0].model_kwargs.update(
                botorch_acqf_class=qLogNoisyExpectedHypervolumeImprovement)
    _orig_gs_init(self, steps, *a, **kw)


gsmod.GenerationStrategy.__init__ = gs_init

_orig_complete = AxClient.complete_trial


def complete_trial(self, trial_index, raw_data, *a, **kw):
    if args.learned_noise:
        # (mean, None): Ax treats the SEM as unknown and the model learns the noise
        raw_data = {k: (v[0] if isinstance(v, tuple) else v, None)
                    for k, v in raw_data.items()}
    return _orig_complete(self, trial_index, raw_data, *a, **kw)


AxClient.complete_trial = complete_trial

_orig_gnt = AxClient.get_next_trials


def get_next_trials(self, max_trials, ttl_seconds=None, fixed_features=None):
    if args.fixed_filament:
        pt = camp.sobol_process_point(camp.FILAMENT_PROCESS_PARAMS, args.seed + 1,
                                      index=max(BATCH - 3, 0))
        fixed_features = FixedFeatures(parameters={k: float(v) for k, v in pt.items()})
        record["fixed_features"] = {k: float(v) for k, v in pt.items()}
    t0 = time.time()
    out = _orig_gnt(self, max_trials, ttl_seconds=ttl_seconds,
                    fixed_features=fixed_features)
    record["gen_seconds"] = round(time.time() - t0, 1)
    # what Ax used as the reference point for each generated trial
    inferred = []
    for idx in out[0]:
        gr = self.experiment.trials[idx].generator_runs[0]
        meta = gr.gen_metadata or {}
        ot = meta.get("objective_thresholds")
        inferred.append(None if ot is None else
                        [{"metric": t.metric.name, "bound": float(t.bound),
                          "relative": bool(t.relative)} for t in ot])
    record["objective_thresholds_per_trial"] = inferred
    model = self.generation_strategy.model
    record["acqf_class"] = getattr(getattr(model, "model", None), "botorch_acqf_class", None)
    record["acqf_class"] = (None if record["acqf_class"] is None
                            else record["acqf_class"].__name__)
    return out


AxClient.get_next_trials = get_next_trials

argv = ["--round", str(ROUND), "--batch-number", str(BATCH),
        "--rebound-form", args.rebound_form, "--seed", str(args.seed)]
t_start = time.time()
rc = camp.main(argv)
record["total_seconds"] = round(time.time() - t_start, 1)
record["suggestions_csv"] = str(args.campaign_bo / f"t3-prism-bo-suggestions-round{ROUND}.csv")
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps(record, indent=2, default=str) + "\n")
print("RECORD", json.dumps(record, default=str)[:2000], flush=True)
sys.exit(rc or 0)
