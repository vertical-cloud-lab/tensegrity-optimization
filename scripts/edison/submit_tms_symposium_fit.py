#!/usr/bin/env python3
"""Submit an Edison ANALYSIS task asking for feedback on the fit of the
TMS 2027 tensegrity abstract within the "AI-Enabled Materials Processing"
symposium, and whether an additive-manufacturing-focused symposium would fit
better.

Attaches the abstract and the symposium call-for-abstracts (flyer PDF + text)
as a single zipped collection. Writes a SUBMITTED placeholder with the task id
so fetching is resumable.

Usage:
    EDISON_API_KEY=... python scripts/edison/submit_tms_symposium_fit.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

HERE = Path(__file__).resolve().parents[2]
TRAJ = HERE / "edison-trajectories" / "tms-symposium-fit"
BUNDLE = TRAJ / "bundle"
SUBMITTED = TRAJ / "tms-symposium-fit-SUBMITTED.json"

QUERY = """\
We are deciding where to submit a conference abstract for the TMS 2027 Annual
Meeting & Exhibition (abstracts due July 1, 2026). The attached bundle contains:

  - tms-2027-abstract.md: our draft abstract, titled "Closed-Loop Bayesian
    Optimization of Multi-Material 3D-Printed Tensegrity-Inspired Energy
    Absorbers." It describes a closed-loop, experiment-driven campaign that
    co-prints rigid PLA struts and flexible TPU tension elements by
    multi-material fused deposition modeling (FDM) and uses multi-objective
    Bayesian optimization (qNEHVI on a Gaussian-process surrogate) to drive a
    design-print-test loop directly on physical measurements (peak transmitted
    force, specific energy absorption, compaction efficiency), with print
    failures handled as a probabilistic feasibility constraint. The optimized
    variables are GEOMETRIC/TOPOLOGICAL design parameters (strut diameter and
    length, tension-element cross-section, strut count, connectivity topology,
    unit-cell tiling) -- NOT process/print parameters and NOT composition.

  - TMS2027-symposium-CFA-text.txt and TMS2027-CFA-Flyer.pdf: the call for
    abstracts for the symposium we currently target, "AI-Enabled Materials
    Processing: Integrating Accelerated Experimental Workflows and
    Processing-Aware Machine Learning" (Data-Driven and Computational Materials
    Design topic; Materials Processing and Manufacturing Division).

Please give candid, specific feedback:

1. FIT ASSESSMENT. How well does our abstract, AS WRITTEN, fit this symposium's
   stated scope? The CFA explicitly centers on "processing history as a primary
   design variable" and "process-aware microstructure and property control."
   Our current optimization targets geometry/topology, not processing
   parameters and not microstructure. Assess whether this is a mismatch and how
   serious it is.

2. STRENGTHENING THE PROCESSING ANGLE. The reviewers note we could incorporate
   optimization of FDM PROCESS PARAMETERS (e.g., nozzle/bed temperature, print
   speed, layer height, line width, flow/extrusion multiplier, cooling,
   retraction, interface/overlap settings at the rigid-flexible boundary) into
   the BO loop. This would make it a (weak) materials-processing problem
   (processing varies, composition fixed). Concretely: which print parameters
   most plausibly affect energy absorption, interfacial bond strength, and
   defect populations for PLA+TPU multi-material FDM, and which would be most
   defensible to add so the abstract genuinely matches a "processing as a design
   variable" symposium? Suggest how to frame the abstract (and what to measure)
   to make the processing-aware-ML framing credible rather than superficial.

3. BETTER-FIT SYMPOSIA. Identify which OTHER TMS 2027 symposia (especially
   additive-manufacturing-focused ones, and architected/cellular/energy-
   absorbing materials or mechanical-behavior symposia) would be a stronger home
   for this abstract as currently written. For each, briefly justify the fit and
   note any reframing needed. If you are not certain a given symposium exists at
   TMS 2027, say so and suggest the closest standing TMS symposium series.

4. RECOMMENDATION. Give a clear bottom-line recommendation: keep the current
   symposium (with which specific edits), or move to a named alternative, and
   what minimal abstract changes each path requires. Note any abstract text we
   should add/cut to stay within the 150-word TMS limit.
"""


def main() -> None:
    api_key = (os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY") or "").strip()
    if not api_key:
        raise SystemExit("No EDISON_API_KEY / EDISON_PLATFORM_API_KEY in environment")

    client = EdisonClient(api_key=api_key)

    # Upload the abstract + CFA as a single zipped collection.
    resp = client.store_file_content(name="tms-symposium-fit-bundle", file_path=str(BUNDLE), as_collection=True)
    uri = f"data_entry:{resp.data_storage.id}"
    print("uploaded bundle:", uri)

    task = TaskRequest(name=JobNames.ANALYSIS, query=QUERY)
    task_id = client.create_task(task, files=[uri])
    task_id = str(task_id)
    print("submitted ANALYSIS task:", task_id)

    SUBMITTED.write_text(json.dumps({"task_id": task_id, "bundle_uri": uri}, indent=2))
    print("wrote", SUBMITTED)


if __name__ == "__main__":
    main()
