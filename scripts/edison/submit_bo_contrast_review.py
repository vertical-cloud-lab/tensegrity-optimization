"""Send the BO-vs-DOE contrast study to Edison ANALYSIS for an
implementation audit.

Triggered by PR #33 comment (@sgbaird, 2026-08-26): "send any related files
from [the bo_contrast comment] (including comparison script, raw PNGs, data,
etc.) to Edison analysis for review. In particular, I'm looking to see if
there's a bad implementation of BO or not."

The uploaded bundle is everything needed to re-derive the reported numbers:
the study driver (BO wiring, baselines, hypervolume, reference convention),
the campaign module it imports its search space and hypervolume routine from,
the baseline module, the write-up, every figure, and the raw per-seed CSVs
for all ten BO repeats and all eighty baseline runs, plus the dense design
cloud and the polished reference fronts.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import time
from datetime import datetime, timezone

os.environ.setdefault(
    "EDISON_PLATFORM_API_KEY",
    os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY", ""),
)

from edison_client import EdisonClient, JobNames  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SIM = REPO_ROOT / "simulations"
BC = SIM / "outputs" / "bo_contrast"
OUT_DIR = REPO_ROOT / "edison-trajectories" / "bo-contrast-review"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BUNDLE_DIR = pathlib.Path(
    os.environ.get("EDISON_BUNDLE_DIR", "/tmp/edison_bo_contrast_bundle")
)

STATIC_FILES = [
    SIM / "bo_contrast_study.py",
    SIM / "bo_contrast_study.md",
    SIM / "pr102_sim_campaign.py",
    SIM / "pr102_baselines.py",
    BC / "bo_contrast_envelope_summary.csv",
    BC / "bo_contrast_strain_era_rescored.csv",
    BC / "bo_contrast_strain_era_rescored_seeds.csv",
    BC / "contrast_screen.csv",
    BC / "contrast_refs.csv",
    BC / "contrast_front_envelope.csv",
    BC / "contrast_front_strain.csv",
    BC / "bo_contrast_headline.png",
    BC / "bo_contrast_envelope_comparison.png",
    BC / "bo_contrast_envelope_objective_space.png",
    BC / "bo_contrast_screen.png",
    BC / "contrast_cloud_ratios.csv.gz",
]

GLOB_FILES = [
    (BC, "contrast_bo_envelope_seed*.csv"),
    (BC, "contrast_baseline_*_printable_envelope_seed*.csv"),
    (BC, "contrast_baseline_*_plain_envelope_seed*.csv"),
]


QUERY = """
# Review request: is our Bayesian-optimization implementation sound, or is the reported BO-vs-DOE separation an artifact?

We benchmark constrained multi-objective Bayesian optimization (Ax 0.5.0 /
BoTorch, `BOTORCH_MODULAR` which resolves to qNEHVI for two minimized
objectives) against four uninformed baselines on a deterministic physics
simulator of a 3D-printed tensegrity impact absorber. We report that BO
reaches 94.2 % of a dense-sweep hypervolume ceiling while every baseline
lands at 77.5 to 80.2 %, with Mann-Whitney p = 9.1e-5 (the floor of a
10-vs-10 test) and zero overlap between the two sets of ten seeds.

**The specific question we want answered: is the BO implementation correct?**
We want an adversarial audit in BOTH directions, because either error would
be embarrassing in a manuscript:

(a) Is the BO *unfairly advantaged* by an implementation or accounting
    choice, so the separation is an artifact rather than a modeling
    advantage? Candidate mechanisms we want checked explicitly:
    hypervolume/reference-point accounting, feasibility masking, whether the
    baselines are handicapped relative to best uninformed practice, whether
    the BO sees information the baselines do not, off-by-one budget
    accounting, and whether the objective-pair selection procedure
    (described below) constitutes selecting a benchmark that flatters the
    optimizer.

(b) Is the BO *broken or badly configured* in a way that made it look bad on
    the earlier objective pair, where we reported it statistically
    indistinguishable from random search? If so, our narrative that the
    difference between the pairs is objective geometry rather than optimizer
    quality is wrong.

Everything needed to re-derive our numbers is attached, including all raw
per-seed CSVs. Please recompute whatever you need rather than trusting our
summary.

## The problem

Design space: four dimensionless shape ratios of a class-1 tensegrity T3
prism (3 PLA struts, 9 TPU-85A tendons), each a plain continuous
`RangeParameter`:

  H_over_R          in [1.5, 4.4]
  H_over_strut_d    in [5.0, 18.33]
  cable_over_strut_d in [0.25, 0.9167]
  twist_deg         in [40, 80]

The single overall scale is solved in closed form so every design has
exactly the same printed mass (20.23 g), i.e. the search is on a
constant-mass manifold and mass is not a free variable. (This was a
deliberate earlier fix: an earlier formulation left mass free and one
objective turned out to be printed mass in disguise, rho = 0.99993.)

Objectives, both minimized, from one MuJoCo drop-tower simulation
(deterministic, ~41 ms per evaluation, no observation noise):

  t180          CFC-180-filtered transmissibility, top-vertex peak
                acceleration over base-plate peak acceleration
  envelope_cm3  bounding-envelope volume of the article (stowed bulk)

Outcome constraints (both are closed-form geometry, not simulation
outputs, and both are passed to Ax as outcome constraints):

  cable_d_print_mm >= 3.0     TPU self-bridging print floor
  envelope_cap_cm3 <= 250.0   build-volume cap

## The BO wiring, verbatim from `bo_contrast_study.py::run_bo_seed`

```python
gs = GenerationStrategy(steps=[
    GenerationStep(model=Models.SOBOL, num_trials=9, min_trials_observed=9,
                   max_parallelism=9, model_kwargs={"seed": seed}),
    GenerationStep(model=Models.BOTORCH_MODULAR, num_trials=-1,
                   max_parallelism=9,
                   model_gen_kwargs={"model_gen_options": {
                       "optimizer_kwargs": {"num_restarts": 8,
                                            "raw_samples": 128}}}),
])
ax_client = AxClient(generation_strategy=gs, random_seed=seed,
                     verbose_logging=False)
ax_client.create_experiment(
    name=..., parameters=RATIO_PARAMETERS,
    objectives={o1: ObjectiveProperties(minimize=True),
                o2: ObjectiveProperties(minimize=True)},
    outcome_constraints=["cable_d_print_mm >= 3.0",
                         "envelope_cap_cm3 <= 250.0"])
for rnd in range(5):                     # round 0 = Sobol, rounds 1-4 = model
    parameterizations, _ = ax_client.get_next_trials(9)
    for idx, params in parameterizations.items():
        res = evaluate(dict(params))     # the simulator
        ax_client.complete_trial(trial_index=idx,
                                 raw_data={k: v for k, v in res.items()
                                           if k in ax_keys})
```

Notes on choices we are unsure about and want judged:

- `complete_trial` is passed **plain floats**, no SEM. In Ax that means
  *inferred* noise, not known-zero noise, even though the simulator is
  deterministic. We considered passing `(value, 0.0)`. A previous paired
  study on a different objective pair found the two gave the same result
  there, but we have not re-tested it here. Does inferring noise on a
  noiseless deterministic simulator materially change qNEHVI behaviour, and
  which is the defensible choice?
- No `ObjectiveThreshold`s are set, so Ax infers reference points for the
  acquisition function from the observed data. Our *reporting* hypervolume
  uses a different, fixed reference point (below). Is that mismatch between
  the acquisition's inferred reference point and the scoring reference point
  a problem for the comparison, or is it fine because the same scoring rule
  is applied to every method?
- Acquisition optimizer runs at 8 restarts x 128 raw samples rather than the
  Ax defaults (20 x 1024). A previous paired study on a related pair found
  no difference (Wilcoxon p = 0.92, ten paired seeds, 5/10 wins). We did not
  repeat that check on this pair. Is that a real risk to the conclusion?
- Objectives are on very different scales (t180 ~ 0.65 to 1.0, envelope_cm3
  ~ 11 to 215). We rely on Ax/BoTorch's internal outcome standardization. Is
  anything else needed?
- The two outcome constraints are deterministic geometry with no noise, and
  are also checkable in closed form before evaluating. We give them to Ax as
  probabilistic outcome constraints anyway. Would `ParameterConstraint`-style
  handling, a feasibility-weighted acquisition, or rejection at generation
  time be more appropriate, and would it change the comparison?

## The baselines

Four, all at the identical budget of 45 evaluations and the identical ten
seeds: uniform random, scrambled Sobol, scrambled Latin hypercube, and a
compass/pattern search (initial step 0.35 of range, halved on a failed
sweep, three weightings 0.15/0.5/0.85 of a normalized weighted sum so it
produces a spread of trade-offs rather than one point, fresh axis
permutation per sweep).

Both the samplers and the compass search run in two modes:

- `plain`: infeasible draws are evaluated and then excluded from fronts.
- `printable`: candidate points are rejection-sampled through the
  *simulation-free* closed-form printability check, so no sampler wastes
  budget on an unprintable design, and the compass search skips unprintable
  probes without being charged for them. This is the mode we report, on the
  argument that it is the strongest honest DOE.

The BO's own Sobol round 0 is **not** rejection-filtered: it draws from the
full box like any Ax Sobol step. So in the reported comparison the
baselines get a free constraint oracle that the BO's initialization does
not. We believe this makes the comparison conservative in the BO's favour,
but please check that reasoning, and check whether the reverse could be
true through the constraint plumbing.

## Scoring

Hypervolume of the dominated region for two minimized objectives, computed
with our own 2-D sweep routine (`hypervolume_2d` in `pr102_sim_campaign.py`,
attached), with infeasible points masked to +inf before accumulation, so a
run's hypervolume is a monotone non-decreasing function of its evaluation
index. Reference point, shared by every method and every seed: 1.05 times
the componentwise worst value over the feasible dense cloud. The ceiling
(the denominator of the "94.2 % of ceiling" figure) is the hypervolume of
the non-dominated set of a 16,384-design scrambled-Sobol sweep plus a
Nelder-Mead polish of the best weighted points (+2.3 % over the raw sweep).

Please verify the hypervolume routine against a standard implementation
(e.g. BoTorch's `Hypervolume` / `DominatedPartitioning`) on our raw CSVs,
and check the reference-point convention for any way it could favour a
method that concentrates points near one end of the front.

## The objective-pair selection procedure, which we consider the biggest
## threat to validity and want judged explicitly

We did not pick the reported objective pair first. We ran one dense
16,384-design cloud (attached, `contrast_cloud_ratios.csv.gz`), which prices
every candidate observable at once because one simulation returns all of
them. For each of six candidate pairs we Monte-Carlo resampled 2,000
uninformed 45-design batches from that cloud and measured the fraction of
that pair's hypervolume ceiling an uninformed batch collects "for free",
plus front-geometry diagnostics. The screen's results (attached,
`contrast_screen.csv`):

  pair                       obj-corr   free HV (uninformed 45)
  t180 + peak_tendon_strain   -0.82      84.6 +- 2.4 %   (previous pair; control)
  t180 + e_rebound            +0.59      81.0 +- 5.3 %   (dead-axis control)
  t180 + envelope_cm3         -0.60      80.0 +- 3.7 %   (CHOSEN)
  t180 + stroke_mm            +0.65      86.5 +- 5.0 %
  strain + envelope_cm3       +0.69      91.5 +- 4.3 %
  envelope + strain <= 0.12   -0.61      85.9 +- 2.9 %

Selection rule, stated before the campaign ran: exclude the two controls,
require a genuine trade-off (the front must span a meaningful fraction of
both objective ranges, which eliminates pairs whose front is a sliver), then
take the lowest free hypervolume. The physical justification we give for the
chosen pair is that it is the lander packaging question: isolation bought
against stowed bulk, at equal printed mass.

Questions on this specifically:
1. Is "choose the objective pair whose front an uninformed sampler is least
   likely to hit by chance, then report that BO beats uninformed sampling on
   it" a legitimate benchmark design, a circular one, or legitimate only if
   framed and reported in a particular way? What framing would a referee
   accept?
2. Our Monte-Carlo screen predicted 78.2 % free hypervolume for uninformed
   45-design batches and the measured baselines came in at 77.5 to 80.2 %.
   Does that agreement validate the screen, or is it tautological given both
   come from the same cloud?
3. Is there a standard name and a standard diagnostic for what we are
   measuring (how much of a Pareto front a space-filling design collects for
   free)? We would like to cite prior art rather than invent a diagnostic.

## The two results we are contrasting

Same protocol, same budget, same seeds, same code path, two objective pairs:

  pair                        BO            best baseline   separation
  t180 + peak_tendon_strain   82.7 % ceil   79.9 % ceil     none (overlapping)
  t180 + envelope_cm3         94.2 % ceil   80.2 % ceil     p = 9.1e-5, no overlap

Our claim is that the difference is a property of the objective geometry
(the strain pair's front is a wide band that a space-filling design lands
near by accident; the envelope pair's front is a 1-D ridge through a 4-D
space, with only 1.2 % of the printable cloud within 2 % of it), not a
property of the optimizer or its implementation.

Please state plainly whether you believe that claim is supported by the
attached artifacts, and list any implementation defect you find, ranked by
how much it could move the reported numbers. If you find none, say so
plainly, and say what additional control would most cheaply falsify the
result. We are separately running the identical harness on synthetic
analytic benchmarks (Branin-family, including a deliberately degenerate
`(f, -f)` pair) as a control; suggestions for what a synthetic control
should and should not be able to show are welcome.

## Attached files

- `bo_contrast_study.py` (the study driver: BO wiring, baselines, screen,
  reference polish, comparison)
- `pr102_sim_campaign.py` (search space, `hypervolume_2d`, the constant-mass
  projection and evaluator entry point)
- `pr102_baselines.py` (earlier baseline implementations this study builds on)
- `bo_contrast_study.md` (the write-up as it currently reads)
- `contrast_bo_envelope_seed*.csv` (all 10 BO repeats, every evaluation with
  parameters, both objectives, feasibility flag, running hypervolume)
- `contrast_baseline_*_{printable,plain}_envelope_seed*.csv` (all 80
  baseline runs, same columns)
- `contrast_cloud_ratios.csv.gz` (the 16,384-design cloud, every observable)
- `contrast_front_*.csv`, `contrast_refs.csv`, `contrast_screen.csv`
- the four figures
"""


def _assemble_bundle() -> list[pathlib.Path]:
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    BUNDLE_DIR.mkdir(parents=True)
    copied: list[pathlib.Path] = []
    paths = list(STATIC_FILES)
    for root, pattern in GLOB_FILES:
        paths.extend(sorted(root.glob(pattern)))
    for src in paths:
        if not src.exists():
            print(f"  MISSING {src}")
            continue
        dst = BUNDLE_DIR / src.name
        shutil.copy2(src, dst)
        copied.append(dst)
    return copied


def _extract_answer(result) -> str:
    formatted = getattr(result, "formatted_answer", None) or ""
    try:
        ef = result.environment_frame
        ef_d = ef.model_dump() if hasattr(ef, "model_dump") else ef
        state = ef_d["state"]["state"]
        if isinstance(state.get("answer"), str) and state["answer"].strip():
            return state["answer"]
        answer = state["response"]["answer"]
        return answer.get("formatted_answer") or formatted
    except Exception:  # noqa: BLE001
        try:
            dump = result.model_dump()
            if isinstance(dump.get("answer"), str) and dump["answer"].strip():
                return dump["answer"]
        except Exception:  # noqa: BLE001
            pass
        return formatted


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--poll-minutes", type=float, default=40.0)
    ap.add_argument("--poll-seconds", type=float, default=60.0)
    ap.add_argument("--task-id", default=None,
                    help="skip submission and fetch this task instead")
    ap.add_argument("--submit-only", action="store_true")
    args = ap.parse_args()

    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get(
        "EDISON_API_KEY"
    )
    if not api_key:
        raise SystemExit("EDISON_PLATFORM_API_KEY / EDISON_API_KEY env var not set")
    client = EdisonClient(api_key=api_key.strip())

    submitted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if args.task_id:
        task_id = args.task_id
    else:
        copied = _assemble_bundle()
        print(f"  bundled {len(copied)} files")
        resp = client.store_file_content(
            name="bo-contrast-review",
            file_path=str(BUNDLE_DIR),
            description=(
                "BO-vs-DOE contrast study: driver + campaign + baseline "
                "sources, write-up, all per-seed BO and baseline CSVs, the "
                "16,384-design cloud, reference fronts, and every figure"
            ),
            as_collection=True,
        )
        storage_id = getattr(getattr(resp, "data_storage", None), "id", None)
        if storage_id is None:
            storage_id = getattr(resp, "id", None)
        print(f"  data_storage id: {storage_id}")
        files = [f"data_entry:{storage_id}"] if storage_id else None

        print(f"[{submitted_at}] submitting ANALYSIS bo-contrast-review query")
        submitted = client.create_task(
            task_data={"name": JobNames.ANALYSIS, "query": QUERY},
            files=files,
        )
        task_id = getattr(submitted, "trajectory_id", None) or str(submitted)
        print(f"  task id: {task_id}")
        (OUT_DIR / f"bo-contrast-review-{task_id}-SUBMITTED.json").write_text(
            json.dumps({
                "task_id": task_id, "submitted_at": submitted_at,
                "job": "ANALYSIS",
                "topic": "audit of the BO implementation behind the "
                         "BO-vs-DOE contrast study (PR #33)",
                "uploaded_files": [p.name for p in copied],
            }, indent=2))
        if args.submit_only:
            print("  submit-only: not polling")
            return

    deadline = time.time() + args.poll_minutes * 60
    last_status = None
    status = None
    while time.time() < deadline:
        try:
            status_resp = client.get_task(task_id=task_id, lite=True)
        except Exception as exc:  # noqa: BLE001
            print(f"  status poll failed: {exc!r}", flush=True)
            time.sleep(args.poll_seconds)
            continue
        status = getattr(status_resp, "status", None) or str(status_resp)
        if status != last_status:
            print(f"  [{datetime.now(timezone.utc).strftime('%H:%M:%S')}] "
                  f"status: {status}", flush=True)
            last_status = status
        if str(status).lower() in {"success", "fail", "failed", "error",
                                   "cancelled"}:
            break
        time.sleep(args.poll_seconds)

    if str(status).lower() not in {"success", "fail", "failed", "error",
                                   "cancelled"}:
        print(f"  still {status} after {args.poll_minutes} min; "
              f"pointer kept for a follow-up fetch")
        return

    result = client.get_task(task_id=task_id, verbose=True)
    md_path = OUT_DIR / f"bo-contrast-review-{task_id}.md"
    json_path = OUT_DIR / f"bo-contrast-review-{task_id}.json"
    formatted = _extract_answer(result)
    md_path.write_text(
        f"# Edison ANALYSIS brief: BO implementation audit "
        f"(BO-vs-DOE contrast study)\n\n"
        f"- **Task ID:** `{task_id}`\n- **Job:** `ANALYSIS`\n"
        f"- **Submitted:** {submitted_at}\n"
        f"- **Fetched:** "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- **Status:** {getattr(result, 'status', 'unknown')}\n\n"
        f"---\n\nQuestion:\n\n{QUERY}\n\n---\n\n{formatted}\n"
    )
    try:
        json_path.write_text(result.model_dump_json(indent=2))
    except Exception:  # noqa: BLE001
        json_path.write_text(json.dumps(result, default=str, indent=2))
    print(f"  wrote {md_path.relative_to(REPO_ROOT)}")
    print(f"  wrote {json_path.relative_to(REPO_ROOT)}")
    stale = OUT_DIR / f"bo-contrast-review-{task_id}-SUBMITTED.json"
    if stale.exists() and str(getattr(result, "status", "")).lower() == "success":
        stale.unlink()


if __name__ == "__main__":
    main()
