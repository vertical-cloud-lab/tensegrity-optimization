"""Submit an Edison Scientific ANALYSIS task on @ctrhjk's input-output
(transmissibility) drop series, and fetch the result.

Driven by sgbaird PR comment 4804945090:
> analyze the data that @ctrhjk provided in [PR #67 comment 4804858562] ...
> Then, send to edison for feedback when you're done analyzing. Fetch this
> session. Summarize and reply.

The series (PR comment 4804858562) pairs a single-axis accelerometer on the
bottom acrylic plate (the INPUT, now the triggered channel CH5) with a tri-axis
accelerometer hot-glued to the top vertex (the OUTPUT, CH2/CH3/CH4). The bungees
were removed for this run. Four distinct-geometry specimens (Practice, n0jdwk,
yqpmx1, h8Lbev) were each dropped five times from 13 in.

We bundle the 20 raw CSVs, the data README, our analysis markdown, and the
generated figures into a single zipped collection (Edison ANALYSIS requires
directory uploads as a collection) and ask the data-analysis crow to verify our
numbers and critique transmissibility as a Bayesian-optimization objective.

Idempotent: records the task id in input-output-SUBMITTED.json and reuses it.
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "input-output"
OUT.mkdir(parents=True, exist_ok=True)
SUBMITTED = OUT / "input-output-SUBMITTED.json"

# The repo's Copilot env injects the key as EDISON_API_KEY (older sessions saw
# EDISON_PLATFORM_API_KEY); read both, and strip a possible trailing newline.
api_key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
if not api_key:
    raise SystemExit("EDISON_API_KEY (or EDISON_PLATFORM_API_KEY) not set")
client = EdisonClient(api_key=api_key.strip())

PROMPT = r"""
We are de-risking a benchtop drop-tower workflow for small (~50 mm edge)
multi-material 3D-printed tensegrity unit cells (PLA/PETG struts, TPU 85A
tendons). Accelerometer data is captured on a Vishay/PCB TP4 system: 200 ms
record, 125 kHz (8 us) sample, 25000 samples, 2% (4 ms) pre-trigger, so a real
impact lands at t ~= 3.9 ms.

NEW INSTRUMENTATION DESIGN ("input-output" transmissibility). A single-axis
accelerometer is mounted on the BOTTOM acrylic plate, right next to one of the
specimen's vertices -- this is the INPUT sensor (it sees the plate strike). A
tri-axis accelerometer is hot-glued to the TOP vertex of the specimen -- this is
the OUTPUT sensor (it sees what the specimen transmits). Crucially, the BUNGEES
WERE REMOVED for this series (pretension off), unlike earlier runs where a
bungee-assisted tower drove specimen lift-off and contaminated the data.

Channel setup for this batch (trigger moved to the single-axis input):
  CH2 tri-axis (vertex, output)  full scale 14492.8 G, trigger No,  sens 0.69  mV/G
  CH3 tri-axis (vertex, output)  full scale 14992.5 G, trigger No,  sens 0.667 mV/G
  CH4 tri-axis (vertex, output)  full scale 13624.0 G, trigger No,  sens 0.734 mV/G
  CH5 single   (base,   INPUT)   full scale  9442.9 G, trigger YES (level 1000 G), sens 1.059 mV/G

Four distinct-geometry T3-prism specimens (Practice, n0jdwk, yqpmx1, h8Lbev)
were EACH dropped FIVE times from 13 in. The 20 raw CSVs are attached
({Practice,n0jdwk,yqpmx1,h8Lbev}_Signal{1..5}.csv; Signal index = drop number,
not channel). Also attached: the data README (channel map) and our analysis
markdown (docs/drop-test-input-output-analysis.md) and figures.

OUR ANALYSIS (please verify independently). SAE J211 phaseless Butterworth
filtering (CFC 1000 ~= 1650 Hz, CFC 180 ~= 300 Hz); raw peaks on these lightly
damped lattices are accelerometer-ringing dominated, so CFC-180 is our
structural number. We locate the impact on the triggered CH5 (input) within the
first 10 ms (windowed +-1.5 ms peak, not a global 0.2 s max), baseline-correct,
take the single-axis CH5 as the input and the tri-axis RESULTANT
sqrt(CH2^2+CH3^2+CH4^2) as the output, and define transmissibility
T = output / input on the CFC-180 peaks. Per-specimen mean +- 1 sigma over the 5
drops:
  Practice : input 244 +- 2 G, output 285 +- 4 G,  T = 1.17 +- 0.01 (T CV 0.8%)
  n0jdwk   : input 244 +- 3 G, output 290 +- 10 G, T = 1.19 +- 0.05 (T CV 4.6%)
  yqpmx1   : input 241 +- 4 G, output 230 +- 2 G,  T = 0.96 +- 0.02 (T CV 2.1%)
  h8Lbev   : input 235 +- 4 G, output 256 +- 1 G,  T = 1.09 +- 0.02 (T CV 2.0%)
All 20/20 drops triggered cleanly. The input (base) peak is nearly constant
across all specimens/drops (235-248 G, <=1.7% CV), so the between-specimen T
spread looks like a genuine structural-response difference. We also see a mild
within-run upward drift in T across the five drops (e.g. n0jdwk T climbs
1.11 -> 1.24 over drops 1->5; the output rises while the input holds).

Please do a DATA ANALYSIS of the attached CSVs and a quantitative critique.
Specifically:

A. Independently verify the per-drop and per-specimen numbers from the attached
   CSVs: locate the impact on CH5 (windowed in the first 10 ms, not a global
   max), baseline-correct, and report raw / CFC-1000 / CFC-180 peak |g| for the
   input (CH5) and the output (tri-axis resultant), the transmissibility
   T = OUT/IN, the input pulse width and partial-pulse delta-v. Confirm or
   correct our mean +- sigma table and CVs. Is the ~2.8-3.0 m/s partial-pulse
   delta-v physically consistent with a 13 in (0.33 m) free (bungee-removed)
   drop (free-fall would give ~2.5 m/s)?

B. Is transmissibility T = output_vertex / input_base a sound, well-posed
   objective for Bayesian optimization of these tensegrity cells? Critique it
   vs alternatives: output peak at fixed input, a frequency-domain
   transmissibility / FRF (since we now have a simultaneous input+output pair),
   shock-response-spectrum (SRS) reduction, transmitted impulse / delta-v ratio,
   or energy-based SEA. Address: (i) whether a single broadband peak ratio is
   meaningful when input and output may peak at different times/frequencies and
   the tri-axis is on a different point than the single-axis; (ii) whether
   T > 1 (output exceeds input, which we see for 3 of 4 specimens -- amplifies
   rather than isolates) is expected for a stiff vertex-to-vertex load path and
   what that implies for "cushioning" claims; (iii) sensitivity to the unknown
   tri-axis orientation (hot-glue mount -> resultant robust to rotation but
   per-axis split not); (iv) how to propagate the ~1-5% CV into a BO noise model.

C. Interpret the mild within-run drift in T across the 5 cyclic drops (output
   creeping up at constant input). Is this most likely progressive seating /
   loosening of the hot-glued vertex mount, cyclic softening / damage of the
   structure, or a real fatigue signal we should keep? How would you separate
   mount artifact from specimen physics (e.g. re-seat-and-repeat, swap mount
   method, interleave specimens)? What does it imply for the planned 20-drop (or
   to-failure) cyclic tests?

D. Concrete, prioritized recommendations to turn this input-output rig into a
   trustworthy producer of a BO objective for impact/energy absorption: mounting
   (replace hot glue with a z-axis-aligned seat; stud/wax vs adhesive; mass
   loading & mount resonance on a small vertex), capture (full ~10 s ringdown
   vs 200 ms; do we need the bungee removed permanently?), replication (n>=5
   distinct specimens per geometry, not just 5 drops of one), and which
   standards / published drop-tower practice (SAE J211, ASTM D7136 / D3332
   cushion curves, ISO 5347 mounting, SRS practice) to follow. Note what extra
   captures would let us regress T against the original tensegrity geometry
   parameters once the IDs are tied back to the design.

Output a single self-contained markdown report we can commit under
edison-trajectories/input-output/.
"""


def main() -> int:
    # ---- assemble the upload bundle -------------------------------------
    bundle = OUT / "bundle"
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)

    raw = REPO / "data" / "drop-tests" / "input-output" / "raw"
    for csv in sorted(raw.glob("*.csv")):
        shutil.copy2(csv, bundle / csv.name)
    shutil.copy2(
        REPO / "data" / "drop-tests" / "input-output" / "README.md",
        bundle / "data-README.md",
    )
    analysis_md = REPO / "docs" / "drop-test-input-output-analysis.md"
    if analysis_md.exists():
        shutil.copy2(analysis_md, bundle / "drop-test-input-output-analysis.md")
    figs = REPO / "data" / "drop-tests" / "input-output" / "figures"
    for png in sorted(figs.glob("*.png")):
        shutil.copy2(png, bundle / png.name)

    if SUBMITTED.exists():
        task_id = json.loads(SUBMITTED.read_text())["task_id"]
        print("reusing task_id:", task_id)
        return 0

    # Edison ANALYSIS requires directory uploads as a single zipped collection.
    resp = client.store_file_content(
        name="input-output-drop-series",
        file_path=str(bundle),
        as_collection=True,
    )
    uri = f"data_entry:{resp.data_storage.id}"
    print("uploaded collection:", uri)

    task = TaskRequest(name=JobNames.ANALYSIS, query=PROMPT)
    submitted = client.create_task(task, files=[uri])
    task_id = submitted if isinstance(submitted, str) else str(submitted)
    print("submitted task_id:", task_id)

    SUBMITTED.write_text(
        json.dumps(
            {"task_id": task_id, "uploaded_files": [uri], "task_type": "ANALYSIS"},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
