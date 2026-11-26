"""The reference point Ax inferred for every archived campaign batch.

PR #121, item 2 of Juan Florez-Coronel's review: "No objective thresholds or
acquisition classes are set, Ax therefore infers a reference point that has
been tight in every snapshot". With no ``threshold=`` on either objective,
Ax 0.5.0 infers one per generation call (``infer_objective_thresholds``:
nadir of the model-predicted Pareto front minus 10 percent of its range) and
stores it in each generator run's ``gen_metadata["objective_thresholds"]``.
This script reads those values straight out of the archived ``AxClient``
JSON snapshots (no refit) and writes ``data/inferred-thresholds.json``.

Usage::

    git archive origin/claude/issue-98-20260821-0103 bo | tar -x -C /tmp/campaign-head
    git archive origin/claude/me2-objective-bo-20261029 bo | tar -x -C /tmp/campaign-me2
    python analysis/bo-review/inferred_thresholds.py /tmp/campaign-head/bo/t3-prism-bo-ax-client-round{1,2,3,4,5}.json \
        /tmp/campaign-me2/bo/t3-prism-bo-ax-client-round6.json
"""

import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "data" / "inferred-thresholds.json"
records = []
for f in sys.argv[1:]:
    exp = json.loads(Path(f).read_text())["experiment"]
    oc = exp.get("optimization_config") or {}
    user = [(x["metric"]["name"], x["bound"]) for x in (oc.get("objective_thresholds") or [])]
    seen = {}
    for ti, trial in exp["trials"].items():
        runs = trial.get("generator_runs") or ([trial["generator_run"]] if trial.get("generator_run") else [])
        for gr in runs:
            ot = (gr.get("gen_metadata") or {}).get("objective_thresholds")
            if ot:
                key = tuple(sorted((x["metric"]["name"], round(x["bound"], 4)) for x in ot))
                seen.setdefault(key, []).append(int(ti))
    for key, trials in seen.items():
        records.append({"snapshot": Path(f).name, "user_thresholds": user,
                        "inferred": dict(key), "generated_trials": sorted(trials)})
        print(Path(f).name, dict(key), f"trials {min(trials)}-{max(trials)}")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, indent=1) + "\n")
