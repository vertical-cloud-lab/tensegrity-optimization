"""Re-run the round-5 LOGO-CV in the rounds-1-and-2 parameter space.

PR #111 follow-up (sgbaird, 2026-09-23): what if we ignored the six
parameters added in round 3 and built the model on the original six,
making sure mass is in the parameter space? The campaign's fit space grew
from 6 parameters (rounds 1 and 2: the five shape coordinates plus the
article's weighed printed mass, exactly `fit_parameters(include_process=
False)` in the campaign script) to 12 in round 3, when six print-process
parameters were added. Mass has been a fit dimension since round 1, so
"the six" already includes it. Every LOGO run committed on this branch
fits the 12-parameter space; this script repeats the LOGO-CV with the
process dimensions removed.

Two variants, selected with ``--variant``:

- ``six-param``: R_mm, H_mm, twist_deg, strut_d_mm, cable_d_mm,
  mass_printed_g. The requested model, identical to the rounds-1-and-2
  fit space.
- ``shape-only``: the five shape coordinates alone. Control that
  isolates what the mass input contributes on top of shape.

Same code path, data, budget, folds, and seeding as
``rerun_logocv_full_nuts.py`` (library-default NUTS 256/512,
``fit_saasbo`` with ``refit_on_cv=True``, reprint pairs held out
together, ``torch.manual_seed(fold_index)`` per fold), so differences
against ``data/full-nuts-rerun/`` are attributable to the feature set
plus NUTS realization noise. The one mechanical addition: after the
print-id join, every arm's parameterization is cut down to the kept
parameters and the experiment's search space is swapped to the matching
subspace, which is what makes ``Models.SAASBO`` build its design matrix
on the reduced space. Guards assert that no observation was silently
dropped as out-of-design and that the fitted model saw exactly the kept
parameters.

Usage (repo root; campaign ``bo/`` tree extracted as for the full-NUTS
rerun, code identical to ``bbf7a62``)::

    python analysis/cv-signal-audit/rerun_logocv_param_ablation.py \
        --campaign-bo /tmp/campaign/bo --variant six-param \
        --max-seconds 660 --commit-each-fold
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path

import numpy as np

AUDIT_DIR = Path(__file__).resolve().parent
PUSH_SCRIPT = Path(
    "/home/runner/work/_actions/anthropics/claude-code-action/v1/scripts/git-push.sh"
)
COMMIT_TRAILER = (
    "\n\nCo-authored-by: Sterling G. Baird "
    "<45469701+sgbaird@users.noreply.github.com>"
    "\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
)

VARIANTS = {
    # populated in main() from the campaign module's own name lists, so the
    # kept sets cannot drift from the campaign definitions
    "six-param": "shape + weighed printed mass (the rounds-1-and-2 fit space)",
    "shape-only": "shape coordinates alone (control: what does mass add)",
}

# set per-variant in main()
OUT_DIR = STATE_PATH = FOLDS_PATH = None


def _git_commit_push(paths, message, push=True):
    """Commit checkpoint files; never let a git hiccup kill the run.

    A parallel session pushes to this branch too, so a rejected push gets
    one rebase-and-retry before giving up until the next checkpoint.
    """
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
        subprocess.run(["git", "commit", "-m", message + COMMIT_TRAILER],
                       cwd=repo_root, check=True)
        if push and PUSH_SCRIPT.exists():
            r = subprocess.run([str(PUSH_SCRIPT), "origin", "HEAD"], cwd=repo_root)
            if r.returncode != 0:
                subprocess.run(["git", "pull", "--rebase", "origin", branch],
                               cwd=repo_root, check=True)
                subprocess.run([str(PUSH_SCRIPT), "origin", "HEAD"],
                               cwd=repo_root, check=True)
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


def _cv_results_from_jsonl(fold_keys):
    """Rebuild the CVResult list in canonical fold order from the checkpoint."""
    from ax.core.observation import Observation, ObservationFeatures
    from ax.modelbridge.cross_validation import CVResult

    by_key = {}
    with FOLDS_PATH.open() as fh:
        for line in fh:
            rec = json.loads(line)
            by_key[rec["fold_key"]] = rec
    results = []
    for gkey in fold_keys:
        rec = by_key[gkey]
        for art in rec["articles"]:
            obs = Observation(
                features=ObservationFeatures(parameters=dict(art["parameters"])),
                data=_obs_data_from_dict(art["observed"]),
                arm_name=art["arm_name"],
            )
            results.append(
                CVResult(observed=obs, predicted=_obs_data_from_dict(art["predicted"]))
            )
    return results, by_key


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign-bo", type=Path, required=True,
                    help="path to the extracted campaign bo/ directory")
    ap.add_argument("--variant", choices=sorted(VARIANTS), required=True)
    ap.add_argument("--max-seconds", type=float, default=3000,
                    help="clean-exit budget for this invocation")
    ap.add_argument("--num-samples", type=int, default=256,
                    help="NUTS samples per fold (BoTorch library default)")
    ap.add_argument("--warmup-steps", type=int, default=512,
                    help="NUTS warmup per fold (BoTorch library default)")
    ap.add_argument("--commit-each-fold", action="store_true",
                    help="git commit+push the checkpoint after every fold")
    ap.add_argument("--smoke", action="store_true",
                    help="plumbing check: tiny NUTS settings, first fold only, "
                         "throwaway output dir")
    args = ap.parse_args(argv)
    t_start = time.time()

    global OUT_DIR, STATE_PATH, FOLDS_PATH
    OUT_DIR = AUDIT_DIR / "data" / f"ablation-{args.variant}"
    if args.smoke:
        OUT_DIR = AUDIT_DIR / "data" / f"ablation-{args.variant}-SMOKE"
        args.num_samples, args.warmup_steps = 16, 32
    STATE_PATH = OUT_DIR / "state.json"
    FOLDS_PATH = OUT_DIR / "folds.jsonl"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    import torch

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
        mass_param,
        repeat_group,
    )

    keep = {
        "six-param": PARAM_NAMES + [mass_param],
        "shape-only": list(PARAM_NAMES),
    }[args.variant]

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

    # ---- the ablation: cut arms and search space to the kept parameters --
    from ax.core.search_space import SearchSpace

    base_space = fit_search_space(include_process=False)
    # The public setter refuses to shrink a search space once trials exist
    # (a parameter-count guard); its body is otherwise a plain assignment
    # (ax/core/experiment.py:224-257), so assign directly.
    experiment._search_space = SearchSpace(
        parameters=[base_space.parameters[name] for name in keep])
    for arm in experiment.arms_by_name.values():
        arm._parameters = {k: arm._parameters[k] for k in keep}
    if experiment.status_quo is not None:
        sq = experiment.status_quo
        sq._parameters = {k: v for k, v in sq._parameters.items() if k in keep}
    print(f"Variant {args.variant}: fit space cut to {len(keep)} parameters "
          f"({', '.join(keep)})", flush=True)

    # ---- initial fit (same spec the folds refit with) --------------------
    torch.manual_seed(10_000)
    cv_model = diag.fit_saasbo(
        experiment, data, args.num_samples, args.warmup_steps, refit_on_cv=True
    )
    assert set(cv_model.parameters) == set(keep), (
        f"model saw {sorted(cv_model.parameters)}, expected {sorted(keep)}")

    training_data = cv_model.get_training_data()
    assert len(training_data) == n_articles, (
        f"{n_articles - len(training_data)} observations dropped as "
        "out-of-design by the subspace swap; refusing to continue")
    assert all(set(obs.features.parameters) == set(keep)
               for obs in training_data)
    group_of = {
        obs.arm_name: repeat_group(labels_by_arm.get(obs.arm_name, obs.arm_name))
        for obs in training_data
    }
    fold_keys = list(dict.fromkeys(group_of[obs.arm_name] for obs in training_data))

    # ---- checkpoint state ------------------------------------------------
    if STATE_PATH.exists():
        state = json.loads(STATE_PATH.read_text())
        if state["fold_keys"] != fold_keys:
            raise RuntimeError(
                "fold keys changed between invocations; refusing to resume "
                f"(state has {len(state['fold_keys'])}, now {len(fold_keys)})")
        if (state["num_samples"], state["warmup_steps"]) != (
                args.num_samples, args.warmup_steps):
            raise RuntimeError("NUTS settings changed between invocations")
        if state["kept_parameters"] != keep:
            raise RuntimeError("kept parameters changed between invocations")
    else:
        state = {
            "variant": args.variant,
            "variant_note": VARIANTS[args.variant],
            "kept_parameters": keep,
            "num_samples": args.num_samples,
            "warmup_steps": args.warmup_steps,
            "seed_scheme": "torch.manual_seed(fold_index) per fold, "
                           "manual_seed(10000) before the shared initial fit "
                           "(identical to the full-nuts-rerun protocol)",
            "snapshot": snapshot.name,
            "campaign_branch": "claude/issue-98-20260821-0103",
            "campaign_code_commit": "bbf7a62 (branch tip 233f4df; both bo "
                                    "scripts unchanged since bbf7a62)",
            "fold_keys": fold_keys,
            "fold_seconds": {},
            "status": "running",
        }
    done = set()
    if FOLDS_PATH.exists():
        with FOLDS_PATH.open() as fh:
            done = {json.loads(line)["fold_key"] for line in fh}
    print(f"{len(fold_keys)} design folds over {len(training_data)} articles; "
          f"{len(done)} already checkpointed", flush=True)

    # ---- fold loop (run_group_cv, checkpointed) --------------------------
    from ax.modelbridge.cross_validation import CVResult

    ran_this_invocation = []
    slowest = 0.0
    for k, gkey in enumerate(fold_keys, start=1):
        if gkey in done:
            continue
        elapsed = time.time() - t_start
        if ran_this_invocation and elapsed + slowest > args.max_seconds:
            state["status"] = "resume_needed"
            STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
            print(f"RESUME_NEEDED: {len(done)}/{len(fold_keys)} folds done, "
                  f"{elapsed:.0f} s elapsed, next fold would overrun "
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
        print(f"    fold {k}/{len(fold_keys)} ({gkey}, {len(test)} article"
              f"{'s' if len(test) > 1 else ''}) in {dt:.0f} s", flush=True)
        rec = {
            "fold_key": gkey,
            "fold_index": k,
            "seconds": round(dt, 1),
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
        with FOLDS_PATH.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        state["fold_seconds"][gkey] = round(dt, 1)
        STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
        done.add(gkey)
        ran_this_invocation.append(
            [CVResult(observed=obs, predicted=pred)
             for obs, pred in zip(test, preds)])
        if args.commit_each_fold:
            _git_commit_push(
                [FOLDS_PATH, STATE_PATH],
                f"LOGO-CV {args.variant} ablation: fold {len(done)}/"
                f"{len(fold_keys)} ({gkey})",
            )
        if args.smoke:
            break

    if args.smoke:
        cv_results, _ = _cv_results_from_jsonl(fold_keys[:1])
        flat = [r for fold in ran_this_invocation for r in fold]
        for rebuilt, direct in zip(cv_results, flat):
            assert rebuilt.observed.arm_name == direct.observed.arm_name
            assert np.allclose(rebuilt.predicted.means, direct.predicted.means)
            assert np.allclose(rebuilt.predicted.covariance,
                               direct.predicted.covariance)
            assert np.allclose(rebuilt.observed.data.means,
                               direct.observed.data.means)
        print("SMOKE_OK: one fold ran, JSONL round-trip exact", flush=True)
        return 0

    # ---- assembly --------------------------------------------------------
    if len(done) < len(fold_keys):
        state["status"] = "resume_needed"
        STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
        print(f"RESUME_NEEDED: {len(done)}/{len(fold_keys)} folds done",
              flush=True)
        return 0

    cv_results, _ = _cv_results_from_jsonl(fold_keys)
    # cross-check the JSONL against anything computed in this process
    flat_direct = {r.observed.arm_name: r
                   for fold in ran_this_invocation for r in fold}
    for rebuilt in cv_results:
        direct = flat_direct.get(rebuilt.observed.arm_name)
        if direct is not None:
            assert np.allclose(rebuilt.predicted.means, direct.predicted.means)
            assert np.allclose(rebuilt.predicted.covariance,
                               direct.predicted.covariance)

    diagnostics_path = OUT_DIR / "t3-prism-bo-round5-logocv-diagnostics.json"
    table, diagnostics = diag._cv_table(cv_results, labels_by_arm,
                                        diagnostics_path)
    table.to_csv(OUT_DIR / "t3-prism-bo-round5-logocv.csv", index=False,
                 float_format="%.5f")
    diag.render_loocv(table, diagnostics,
                      OUT_DIR / "t3-prism-bo-round5-logocv.png",
                      n_articles=n_articles,
                      note=diag.LOGOCV_NOTE + "\nFit-space ablation: "
                      + ", ".join(keep))
    state["status"] = "complete"
    state["total_fold_seconds"] = round(sum(state["fold_seconds"].values()), 1)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
    for name in ("MAPE", "Correlation coefficient", "Rank correlation",
                 "Fisher exact test p"):
        if name in diagnostics:
            values = {m: round(float(v), 4) for m, v in diagnostics[name].items()}
            print(f"  {name}: {values}", flush=True)
    if args.commit_each_fold:
        _git_commit_push(
            [OUT_DIR, STATE_PATH],
            f"LOGO-CV {args.variant} ablation complete: {len(fold_keys)} "
            f"folds at {args.num_samples}/{args.warmup_steps}",
        )
    print("ALL_FOLDS_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
