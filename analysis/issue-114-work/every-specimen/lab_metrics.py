#!/usr/bin/env python3
"""Per-drop T180 and velocity loss index for every session, from the lab's own
pipeline (issue #114).

Runs ``analyze_capture(path, baseline="tail")`` from the drop-test pipeline of
PR #86 (``scripts/analysis/drop_test_abc123_blind_analysis.py`` on branch
``copilot/add-drop-test-protocol-again``, head ``0a34991``) on each raw
1.25 MHz capture of drops 1 to 20. That is the call the campaign check-ins and
the corny7 export make, so the numbers are the campaign's own:

* ``t180``: CFC-180 peak of the top-vertex resultant (CH2 to CH4) over the
  CFC-180 peak of the base plate (CH5).
* ``e_rebound = g * t_second / (2 * dv)``: ``t_second`` is the time from the
  impact to the largest 300 to 900 Hz burst on the top vertex 15 to 70 ms
  later (the second contact), ``dv`` the base plate's velocity change.
* ``VLI = 1 - e_rebound``, the manuscript's velocity loss index (higher means
  less of the impact velocity comes back).

Drop k is the session's k-th capture (see ``fetch_waveforms.py``).

Usage:
    python lab_metrics.py --raw /tmp/drop-raw --pipeline-dir <PR #86 checkout>/scripts/analysis
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from fetch_waveforms import BATCHES, pick_files

HERE = Path(__file__).resolve().parent
KEYS = ("t180", "t1000", "in_180_g", "out_180_g", "in_dv_ms", "t_second_ms", "e_rebound")


def _init(pipeline_dir: str) -> None:
    sys.path.insert(0, pipeline_dir)


def _one(job: tuple[str, int, int, str]) -> dict:
    from drop_test_abc123_blind_analysis import analyze_capture
    spec, drop, signal, path = job
    m = analyze_capture(Path(path), baseline="tail")
    row = {"specimen_id": spec, "drop": drop, "signal": signal}
    row.update({k: m.get(k, np.nan) for k in KEYS})
    row["VLI"] = 1.0 - row["e_rebound"]
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True, help="where fetch_waveforms.py put the captures")
    ap.add_argument("--pipeline-dir", type=Path, required=True,
                    help="scripts/analysis of a PR #86 checkout")
    ap.add_argument("--out", type=Path, default=HERE / "results" / "per_drop_lab_metrics.csv")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()

    jobs = []
    for spec in [s for b in BATCHES.values() for s in b]:
        picks = pick_files(json.loads((HERE / "box-ids" / f"{spec}.json").read_text())["files"])
        jobs += [(spec, i, k, str(args.raw / spec / f"Signal{k}.csv"))
                 for i, (k, _, _) in picks.items()]
    with ProcessPoolExecutor(args.jobs, initializer=_init,
                             initargs=(str(args.pipeline_dir),)) as ex:
        rows = list(ex.map(_one, jobs, chunksize=8))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    print(f"wrote {len(rows)} drops to {args.out}")


if __name__ == "__main__":
    main()
