"""Re-run the round-5 LOGO-CV at the library-default NUTS settings (256/512).

The committed `data/t3-prism-bo-round5-logocv.csv` was produced on the
campaign branch (`claude/issue-98-20260821-0103` at `bbf7a62`) by
`bo/t3_prism_bo_diagnostics.py --round 5 --cv-only --group-cv` with reduced
per-fold NUTS settings (64 samples / 128 warmup, 4 retained draws after
thinning 16). This script repeats that run at the BoTorch library defaults
(256 samples / 512 warmup, 16 retained draws), which is what every campaign
candidate-generation fit used, so the CV and the generation fits share one
standard (requested in PR #76 and PR #111).

It is the same code path as the campaign script: the model setup below is a
line-for-line replica of that script's `--cv-only --group-cv` branch, and the
fold loop calls the same `fit_saasbo` / `model.cross_validate` machinery with
`refit_on_cv=True`. Three deliberate additions, none of which changes the
statistics:

- **Per-fold checkpointing.** Each completed fold appends one JSON line
  (observed and predicted means and covariances for its articles) to
  `data/full-nuts-rerun/folds.jsonl` and is committed and pushed
  immediately, so a killed runner loses at most the fold in flight. On the
  next invocation completed folds are skipped.
- **A wall-clock budget** (`--max-seconds`): the process exits cleanly with
  a `RESUME_NEEDED` marker before the harness Bash timeout can kill it
  mid-write.
- **Per-fold seeding** (`torch.manual_seed(fold_index)` before each fold, on
  top of the unseeded original) so the result does not depend on how the run
  was chunked. NUTS remains stochastic across code or library versions; the
  seed only makes this artifact reproducible as committed.

When the last fold lands, the final CSV / diagnostics JSON / parity PNG are
written to `data/full-nuts-rerun/` in exactly the campaign formats (same
`_cv_table` and `render_loocv` functions, same `float_format="%.5f"`), and the
reconstruction from the JSONL is asserted against the in-memory results.

Usage (repo root; needs the campaign `bo/` tree extracted somewhere local,
plus `ax-platform==0.5.0 pandas matplotlib`)::

    git fetch origin claude/issue-98-20260821-0103
    mkdir -p /tmp/campaign/bo
    for f in $(git ls-tree -r --name-only origin/claude/issue-98-20260821-0103 -- bo/ \
               | grep -Ev 'figures/|slices/|per-specimen-stls/|\\.png$|\\.scad$'); do
        git show origin/claude/issue-98-20260821-0103:$f > /tmp/campaign/$f
    done
    python analysis/cv-signal-audit/rerun_logocv_full_nuts.py \
        --campaign-bo /tmp/campaign/bo --max-seconds 3000 --commit-each-fold
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
OUT_DIR = AUDIT_DIR / "data" / "full-nuts-rerun"
STATE_PATH = OUT_DIR / "state.json"
FOLDS_PATH = OUT_DIR / "folds.jsonl"
PUSH_SCRIPT = Path(
    "/home/runner/work/_actions/anthropics/claude-code-action/v1/scripts/git-push.sh"
)
COMMIT_TRAILER = (
    "\n\nCo-authored-by: Sterling G. Baird "
    "<45469701+sgbaird@users.noreply.github.com>"
    "\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
)


def _git_commit_push(paths, message, push=True):
    """Commit checkpoint files; never let a git hiccup kill the run."""
    try:
        repo_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
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
    if args.smoke:
        OUT_DIR = AUDIT_DIR / "data" / "full-nuts-rerun-SMOKE"
        STATE_PATH = OUT_DIR / "state.json"
        FOLDS_PATH = OUT_DIR / "folds.jsonl"
        args.num_samples, args.warmup_steps = 16, 32
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    import torch

    sys.path.insert(0, str(args.campaign_bo.resolve()))
    import t3_prism_bo_diagnostics as diag  # noqa: E402
    from t3_prism_bo_campaign import (  # noqa: E402
        BO_DIR,
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
    experiment.search_space = fit_search_space(include_process=has_process)
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

    # ---- initial fit (same spec the folds refit with) --------------------
    torch.manual_seed(10_000)
    cv_model = diag.fit_saasbo(
        experiment, data, args.num_samples, args.warmup_steps, refit_on_cv=True
    )

    training_data = cv_model.get_training_data()
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
    else:
        state = {
            "num_samples": args.num_samples,
            "warmup_steps": args.warmup_steps,
            "seed_scheme": "torch.manual_seed(fold_index) per fold, "
                           "manual_seed(10000) before the shared initial fit",
            "snapshot": snapshot.name,
            "campaign_branch": "claude/issue-98-20260821-0103",
            "campaign_code_commit": "bbf7a62",
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
                f"LOGO-CV full-NUTS rerun: fold {len(done)}/{len(fold_keys)} "
                f"({gkey})",
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
                      n_articles=n_articles, note=diag.LOGOCV_NOTE)
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
            f"LOGO-CV full-NUTS rerun complete: {len(fold_keys)} folds at "
            f"{args.num_samples}/{args.warmup_steps}",
        )
    print("ALL_FOLDS_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
