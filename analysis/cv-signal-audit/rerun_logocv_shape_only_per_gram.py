"""Re-run the round-5 LOGO-CV with mass out of the fit space AND the
objectives divided by mass.

PR #111 follow-up (sgbaird, 2026-09-25): "So then, just take the mass out
of the input space and divide the objectives by the mass. Right?" The two
halves had been tested separately: Section 6 removed mass from the fit
space with the objectives untouched (``data/ablation-shape-only/``,
``data/objective-tavg10ms-shape-only/``), and
``rerun_logocv_mass_normalized.py`` divided the objectives by mass with
mass kept as an input. This driver runs the combination.

* ``--pair campaign``: ``t180_per_g`` and ``e_reb_mJ_per_g`` (the latter
  equals ``e_rebound * g * h`` exactly, because the absolute form was built
  by multiplying by the same mass).
* ``--pair payload``: ``tavg10ms_per_g`` and ``late_avg3ms_g_per_g``.

Article values come from ``data/mass-normalized-objectives.csv`` (written
by ``mass_normalization_checks.py``; SEM(Y/m) = SEM(Y)/m, the scale
reading treated as exact), the same table the mass-retained per-gram runs
used. The fit space is the five shape coordinates, cut with the same
subspace swap as ``rerun_logocv_param_ablation.py``.

``--transform raw`` fits the untransformed pair instead, through the same
code path. It exists for one purpose, the reproduction check: running a
committed fold of ``data/ablation-shape-only/`` (campaign pair, the
snapshot's own values) or ``data/objective-tavg10ms-shape-only/``
(payload pair, ``data/payload-objectives.csv``) in a fresh process must
return the committed predictions, which establishes both that this
environment reproduces the earlier runs and that a fold does not depend
on which folds ran before it in the same process. That second property
is what makes ``--shard`` safe. Result on 2026-09-25: fold ``r2d2c3`` of
the payload run, re-run alone in a fresh process at the library-default
thread count (4 on the runner), matched the committed predictions and
covariances exactly (max difference 0). At ``--threads 1`` it did not:
the thread count is part of the floating-point path, so NUTS follows a
different (equally valid) trajectory. ``state.json`` records
``torch_threads``, and an exact reproduction needs the same setting.

Everything else is the audit's standard protocol: the campaign's round-5
Ax snapshot, ``fit_saasbo`` with ``refit_on_cv=True``, library-default
NUTS (256 samples / 512 warmup), reprint pairs held out together,
``torch.manual_seed(fold_index)`` per fold, ``manual_seed(10000)`` before
the shared initial fit, fold order asserted identical to
``data/full-nuts-rerun/state.json``.

``--shard i/n`` runs every n-th fold (fold indices i+1, i+1+n, ...), so
n processes can split one run. Workers append to the same ``folds.jsonl``
and ``state.json`` under an exclusive file lock, and commit under the same
lock; ``--assemble`` then rebuilds the run in canonical fold order and
writes the campaign-format CSV, diagnostics JSON and parity PNG.

Usage (repo root; campaign ``bo/`` tree extracted at ``bbf7a62``)::

    python analysis/cv-signal-audit/rerun_logocv_shape_only_per_gram.py \
        --campaign-bo /tmp/campaign/bo --pair payload --transform raw \
        --only-folds r2d2c3 --out-dir /tmp/repro-payload
    for i in 0 1; do
      python analysis/cv-signal-audit/rerun_logocv_shape_only_per_gram.py \
          --campaign-bo /tmp/campaign/bo --pair campaign --shard $i/2 \
          --threads 1 --commit-each-fold &
    done; wait
    python analysis/cv-signal-audit/rerun_logocv_shape_only_per_gram.py \
        --campaign-bo /tmp/campaign/bo --pair campaign --assemble \
        --commit-each-fold
"""

from __future__ import annotations

import argparse
import fcntl
import json
import subprocess
import sys
import time
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd

AUDIT_DIR = Path(__file__).resolve().parent
NORMALIZED_CSV = AUDIT_DIR / "data" / "mass-normalized-objectives.csv"
PAYLOAD_CSV = AUDIT_DIR / "data" / "payload-objectives.csv"
FULLNUTS_STATE = AUDIT_DIR / "data" / "full-nuts-rerun" / "state.json"
PUSH_SCRIPT = Path(
    "/home/runner/work/_actions/anthropics/claude-code-action/v1/scripts/git-push.sh"
)
COMMIT_TRAILER = (
    "\n\nCo-authored-by: Sterling G. Baird "
    "<45469701+sgbaird@users.noreply.github.com>"
    "\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
)

SOURCE = {"campaign": ("t180", "e_reb_mJ"),
          "payload": ("tavg10ms", "late_avg3ms_g")}
OUT_NAME = {"campaign": "objective-per-gram-shape-only",
            "payload": "objective-payload-per-gram-shape-only"}

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


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign-bo", type=Path, required=True,
                    help="path to the extracted campaign bo/ directory")
    ap.add_argument("--pair", choices=("campaign", "payload"), required=True,
                    help="campaign = (t180, e_reb_mJ); "
                         "payload = (tavg10ms, late_avg3ms_g)")
    ap.add_argument("--transform", choices=("per-gram", "raw"),
                    default="per-gram",
                    help="per-gram divides each objective by the article's "
                         "weighed mass; raw is for the reproduction check")
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
    ap.add_argument("--assemble", action="store_true",
                    help="all folds done: write the campaign-format outputs")
    args = ap.parse_args(argv)
    t_start = time.time()

    global OUT_DIR, STATE_PATH, FOLDS_PATH, LOCK_PATH
    shard_i, shard_n = (int(v) for v in args.shard.split("/"))
    assert 0 <= shard_i < shard_n, args.shard
    OUT_DIR = args.out_dir or AUDIT_DIR / "data" / OUT_NAME[args.pair]
    if args.transform == "raw" and args.out_dir is None:
        raise SystemExit("--transform raw is a reproduction check; "
                         "give it a throwaway --out-dir")
    STATE_PATH = OUT_DIR / "state.json"
    FOLDS_PATH = OUT_DIR / "folds.jsonl"
    # one lock for every worker of every run: they share the git index
    LOCK_PATH = Path("/tmp") / "rerun_logocv_shape_only_per_gram.lock"
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

    # ---- the objective swap ---------------------------------------------
    src = SOURCE[args.pair]
    if args.transform == "per-gram":
        names = tuple(f"{s}_per_g" for s in src)
        table = pd.read_csv(NORMALIZED_CSV).set_index("print_id")
        cols = {n: (f"{s}__per_gram", f"{s}__per_gram_sem")
                for s, n in zip(src, names)}
    elif args.pair == "payload":
        names = src
        table = pd.read_csv(PAYLOAD_CSV).set_index("print_id")
        cols = {n: (f"{n}_mean", f"{n}_sem") for n in names}
    else:
        names, table, cols = src, None, None  # the snapshot's own values

    if table is not None:
        from ax.core.data import Data
        from ax.core.metric import Metric

        seen = data.df[["trial_index", "arm_name"]].drop_duplicates()
        rows, matched = [], []
        for r in seen.itertuples():
            pid = labels_by_arm.get(r.arm_name)
            if pid is None or pid not in table.index:
                raise RuntimeError(f"arm {r.arm_name} (print {pid}) has no "
                                   "objective values; refusing to run")
            matched.append(pid)
            for n in names:
                mcol, scol = cols[n]
                rows.append({"trial_index": int(r.trial_index),
                             "arm_name": r.arm_name, "metric_name": n,
                             "mean": float(table.loc[pid, mcol]),
                             "sem": float(table.loc[pid, scol])})
        new_df = pd.DataFrame(rows)
        assert len(matched) == n_articles == 44, (len(matched), n_articles)
        assert new_df["mean"].notna().all() and new_df["sem"].notna().all()
        assert (new_df["sem"] > 0).all()
        # observations_from_data silently drops metrics the experiment does
        # not know about, so register the swapped pair as tracking metrics
        known = set(experiment.metrics)
        experiment.add_tracking_metrics(
            [Metric(name=n, lower_is_better=True) for n in names if n not in known])
        data = Data(df=new_df)
        print(f"Objectives swapped to {names} for {len(matched)} articles "
              f"({args.transform})", flush=True)

    # ---- the fit space: five shape coordinates ---------------------------
    from ax.core.search_space import SearchSpace

    keep = list(PARAM_NAMES)
    assert "mass_printed_g" not in keep, keep
    base_space = fit_search_space(include_process=False)
    experiment._search_space = SearchSpace(
        parameters=[base_space.parameters[name] for name in keep])
    for arm in experiment.arms_by_name.values():
        arm._parameters = {k: arm._parameters[k] for k in keep}
    if experiment.status_quo is not None:
        sq = experiment.status_quo
        sq._parameters = {k: v for k, v in sq._parameters.items() if k in keep}
    n_params = len(keep)
    print(f"Shape-only fit space: {n_params} parameters ({', '.join(keep)})",
          flush=True)

    # ---- initial fit (same spec the folds refit with) --------------------
    torch.manual_seed(10_000)
    cv_model = diag.fit_saasbo(
        experiment, data, args.num_samples, args.warmup_steps, refit_on_cv=True
    )
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
        "objectives": list(names),
        "source_objectives": list(src),
        "transform": args.transform,
        "n_params": n_params,
        "kept_parameters": keep,
        "fit_space": "5-parameter shape-only (mass_printed_g and the six "
                     "process settings removed)",
        "objective_note": ("each objective divided per article by the weighed "
                           "printed mass (SEM scaled by 1/m, mass treated as "
                           "exact), values from mass-normalized-objectives.csv"
                           if args.transform == "per-gram" else
                           "untransformed pair (reproduction check)"),
        "num_samples": args.num_samples,
        "warmup_steps": args.warmup_steps,
        "seed_scheme": "torch.manual_seed(fold_index) per fold, "
                       "manual_seed(10000) before the shared initial fit "
                       "(identical to the full-nuts-rerun protocol; fold order "
                       "asserted equal to full-nuts-rerun); folds split across "
                       "shard processes, each repeating the seeded initial fit",
        "snapshot": snapshot.name,
        "campaign_branch": "claude/issue-98-20260821-0103",
        "campaign_code_commit": "bbf7a62",
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
    print(f"{len(fold_keys)} design folds over {len(training_data)} articles; "
          f"{len(done)} already checkpointed; shard {shard_i}/{shard_n} has "
          f"{len(todo)} to run", flush=True)

    # ---- fold loop (run_group_cv, checkpointed) --------------------------
    slowest = 0.0
    for k, gkey in todo if not args.assemble else []:
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
            if args.commit_each_fold:
                _git_commit_push(
                    [FOLDS_PATH, STATE_PATH],
                    f"LOGO-CV shape-only, {args.pair} objectives per gram: "
                    f"fold {n_done}/{len(fold_keys)} ({gkey})",
                )

    if not args.assemble:
        print("SHARD_DONE", flush=True)
        return 0

    # ---- assembly --------------------------------------------------------
    with _locked():
        done = set(_read_folds())
        if done != set(fold_keys):
            print(f"RESUME_NEEDED: {len(done)}/{len(fold_keys)} folds done",
                  flush=True)
            return 0
        cv_results = _cv_results_from_jsonl(fold_keys)
        # rewrite the checkpoint in canonical fold order (shards append in
        # completion order); the content of every record is unchanged
        by_key = _read_folds()
        FOLDS_PATH.write_text("".join(json.dumps(by_key[g]) + "\n"
                                      for g in fold_keys))

    diag.METRIC_ORDER = list(names)
    unit = "per g" if args.transform == "per-gram" else "raw"
    label = {"t180": "t180", "e_reb_mJ": "Rebound",
             "tavg10ms": "tavg10ms", "late_avg3ms_g": "late_avg3ms"}
    title = {"t180": "t180", "e_reb_mJ": "Rebound energy",
             "tavg10ms": "10 ms dose ratio", "late_avg3ms_g": "Hop landing"}
    diag.METRIC_LABEL = {n: f"{label[s]}\n({unit})" for s, n in zip(src, names)}
    diag.METRIC_TITLE = {n: f"{title[s]}, {unit}" for s, n in zip(src, names)}
    diag.METRIC_COLOR = dict(zip(names, ("#1f77b4", "#e8590c")))

    diagnostics_path = OUT_DIR / "t3-prism-bo-round5-logocv-diagnostics.json"
    table_out, diagnostics = diag._cv_table(cv_results, labels_by_arm,
                                            diagnostics_path)
    table_out.to_csv(OUT_DIR / "t3-prism-bo-round5-logocv.csv", index=False,
                     float_format="%.5f")
    diag.render_loocv(table_out, diagnostics,
                      OUT_DIR / "t3-prism-bo-round5-logocv.png",
                      n_articles=n_articles,
                      note=diag.LOGOCV_NOTE + "\nObjective transform: "
                      f"{args.transform}; fit space: {n_params} shape "
                      "parameters (mass removed as an input).")
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
                f"LOGO-CV shape-only, {args.pair} objectives per gram complete: "
                f"{len(fold_keys)} folds at {args.num_samples}/{args.warmup_steps}",
            )
    print(f"ALL_FOLDS_DONE ({time.time() - t_start:.0f} s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
