#!/usr/bin/env python3
"""Submit the drop-tower accelerometer "tuning" analysis (issue #71) to Edison.

This bundles the TP4 accelerometer dataset, the analysis script, the derived
peak-summary table, and the written findings/figures, uploads them as a single
collection, and creates an Edison ``ANALYSIS`` task asking for feedback on the
methodology, findings, and recommendations.

The task is submitted **non-blocking**: the script prints the task id and writes
``accelerometer-tuning-SUBMITTED.json`` so a later session can fetch the result.

Usage::

    python scripts/edison/submit_accelerometer_tuning.py

Requires ``edison-client`` and an API key in ``EDISON_PLATFORM_API_KEY`` (falls
back to ``EDISON_API_KEY``).
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from edison_client import EdisonClient, JobNames
from edison_client.models.app import TaskRequest

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "edison-trajectories" / "accelerometer-tuning"
SUBMITTED_JSON = OUT_DIR / "accelerometer-tuning-SUBMITTED.json"

# Files to bundle for the analysis (relative to repo root).
BUNDLE_PATHS = [
    "data/drop-tests/accelerometer-tuning",
    "scripts/analysis/accelerometer_tuning_analysis.py",
    "docs/accelerometer-tuning-analysis.md",
    "docs/figures/accelerometer-tuning",
]

QUERY = """\
We run drop tests on a bungee-assisted drop tower (the base accelerates downward
faster than 1 g, so unconstrained specimens lift off the base). On 06/02/2026 we
recorded a "tuning" series (TP4 Time-Domain exports: 4 channels at 125 kHz,
0.2 s / 25,000-sample windows, in G) to understand why a single-axis
accelerometer and a tri-axis accelerometer do not report the same acceleration.

The attached collection contains:
- data/drop-tests/accelerometer-tuning/raw/ : the TP4 series table
  (06.02.2026.csv) plus 13 time-domain event exports (06.02.2026_SignalN.csv).
- data/drop-tests/accelerometer-tuning/peak_summary.csv : derived raw and
  SAE J211 CFC-1000 / CFC-180 filtered peaks per event/channel.
- data/drop-tests/accelerometer-tuning/README.md : data format + inferred
  channel->sensor mapping.
- scripts/analysis/accelerometer_tuning_analysis.py : the analysis pipeline.
- docs/accelerometer-tuning-analysis.md + docs/figures/accelerometer-tuning/ :
  our written findings, troubleshooting, and figures.

Our current findings (please scrutinize, confirm or refute against the raw data,
and extend):
1. The single-axis channel (CH1) saturates/clips at a recurring ~8806 G ceiling
   (events 2/3/5), so its peak there is invalid.
2. Raw peaks are mount-resonance ringing (PSD energy past 20 kHz); SAE J211 CFC
   filtering is required before any comparison.
3. CH4 carries a fixed ~4.2 ms trigger/magnet-release artifact, not impact.
4. Sensors were swapped between positions and per-event labels were not posted,
   so only events 1 & 4 have both reading a comparable impact (single-axis is
   ~1.5x the tri-axis impact axis on CFC-180); this dataset cannot
   cross-calibrate the two sensors.

Please provide feedback as an independent reviewer/analyst:
(a) Verify the saturation/clipping claim (level, which events, evidence) directly
    from the raw time-domain data.
(b) Check the channel->sensor mapping (CH1 = single-axis; CH2-CH4 = tri-axis
    X/Y/Z) against the data and flag any inconsistency.
(c) Validate the filtering approach (CFC-1000 for g_max, CFC-180 for the
    rigid-body pulse / delta-v); recommend the correct CFC class and any phaseless
    / anti-alias considerations for a 125 kHz shock record.
(d) Confirm or correct the ~4.2 ms trigger/magnet-release artifact interpretation
    on CH4 and how to gate it out.
(e) Assess whether the single-axis-vs-tri-axis discrepancy is plausibly a
    sensitivity (mV/G) / full-scale-range mismatch versus a real physical
    difference, and lay out a rigorous back-to-back co-location cross-calibration
    protocol (mounting, sub-saturation drop heights, number of repeats, the
    regression to extract the scale factor, uncertainty reporting).
(f) Critique our recommendations and surface anything we are missing (sensor
    selection / range, mount resonance mitigation, sample-rate/anti-alias,
    labeling and metadata per run), with citations where relevant.
"""


def main() -> None:
    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get(
        "EDISON_API_KEY"
    )
    if not api_key:
        raise SystemExit(
            "Set EDISON_PLATFORM_API_KEY (or EDISON_API_KEY) before running."
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Stage the files into a single directory so they upload as one collection
    # (ANALYSIS crow requires directory uploads via store_file_content as a
    # collection; uploading files individually fails silently).
    bundle_dir = OUT_DIR / "bundle"
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True)
    for rel in BUNDLE_PATHS:
        src = REPO_ROOT / rel
        dst = bundle_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    client = EdisonClient(api_key=api_key)

    resp = client.store_file_content(
        name="accelerometer-tuning-bundle",
        file_path=bundle_dir,
        description=(
            "Drop-tower single-axis vs tri-axis accelerometer tuning dataset, "
            "analysis script, peak summary, and findings (issue #71)."
        ),
        as_collection=True,
        tags=["accelerometer-tuning", "drop-test", "issue-71"],
    )
    data_entry_uri = f"data_entry:{resp.data_storage.id}"
    print("Uploaded bundle ->", data_entry_uri)

    task = TaskRequest(name=JobNames.ANALYSIS, query=QUERY)
    submitted = client.create_task(task, files=[data_entry_uri])
    task_id = str(submitted) if not hasattr(submitted, "task_id") else submitted.task_id
    print("Submitted ANALYSIS task:", task_id)

    SUBMITTED_JSON.write_text(
        json.dumps(
            {
                "job_name": str(JobNames.ANALYSIS),
                "task_id": task_id,
                "data_entry_uri": data_entry_uri,
                "data_storage_id": str(resp.data_storage.id),
                "bundle_paths": BUNDLE_PATHS,
                "status": "submitted",
            },
            indent=2,
        )
        + "\n"
    )
    print("Wrote", SUBMITTED_JSON.relative_to(REPO_ROOT))

    # The uploaded copy lives in Edison storage; no need to keep the local stage.
    shutil.rmtree(bundle_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
