"""Submit an Edison Scientific ANALYSIS task on @ctrhjk's clip-height /
accelerometer-check drop diagnostics, and fetch the result.

Driven by sgbaird PR comment 4794736130:
> have a look at the previous two comments. Send an Edison analysis query with
> the data, fetch this session, summarize interpretation, provide
> recommendations directly in your comment reply.

The "previous two comments" are @ctrhjk's clip-height sweep (PR comment
4794351098 — eight drops at clip heights 0.5/1/1.5/2 in, tri-axis on the
acrylic plate, NONE triggered, so no CSV) and the accelerometer check (PR
comment 4794438322 — tri-axis moved to the base plate, 13 in drop, one CSV that
DID trigger cleanly).

We bundle the one available CSV plus the context/analysis markdown into a
single zipped collection (Edison ANALYSIS requires directory uploads as a
collection) and ask the data-analysis crow to interpret the diagnostic and
recommend how to get a reliable triggered measurement out of the acrylic-plate
configuration.

Idempotent: records the task id in clip-height-SUBMITTED.json and reuses it.
"""
from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "clip-height"
OUT.mkdir(parents=True, exist_ok=True)
SUBMITTED = OUT / "clip-height-SUBMITTED.json"

# The repo's Copilot env injects the key as EDISON_API_KEY (older sessions saw
# EDISON_PLATFORM_API_KEY); read both, and strip a possible trailing newline.
api_key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
if not api_key:
    raise SystemExit("EDISON_API_KEY (or EDISON_PLATFORM_API_KEY) not set")
client = EdisonClient(api_key=api_key.strip())

PROMPT = r"""
We are de-risking a benchtop drop-tower workflow for small (~50 mm edge)
multi-material 3D-printed tensegrity unit cells (PLA/PETG struts, TPU 85A
tendons) on a bungee-assisted drop tower. Accelerometer data is captured on a
Vishay/PCB TP4 system: 200 ms record, 125 kHz (8 us) sample, 25000 samples,
2% (4 ms) pre-trigger, so a real impact lands at t ~= 3.9-4.1 ms.

Channel setup for this batch:
  CH2 tri-axis  full scale 14492.8 G, trigger No,  sensitivity 0.69  mV/G
  CH3 tri-axis  full scale 14992.5 G, trigger No,  sensitivity 0.667 mV/G
  CH4 tri-axis  full scale 13624.0 G, trigger YES (level 1000 G), sens 0.734 mV/G
  CH5 single    full scale  9442.9 G, trigger No,  sensitivity 1.059 mV/G
SAE J211 phaseless Butterworth filtering is applied (CFC 1000 ~= 1650 Hz,
CFC 180 ~= 300 Hz); raw peaks on these lightly damped lattices are
accelerometer-ringing dominated, so CFC-180 is our structural number.

BACKGROUND PROBLEM. In an earlier vertex- vs. acrylic-plate series, the
accelerometer placed on the acrylic "top plate" repeatedly registered NO impact
above the 1000 G trigger (3 of 4 acrylic runs), while the same sensor on a
tensegrity vertex gave clean, repeatable ~230-285 G CFC-180 peaks. Hypothesis:
the retaining clips sit too low, so the acrylic plate seats on / is held by the
specimen and the shock never reaches the plate sensor.

TWO NEW DIAGNOSTIC EXPERIMENTS (the data + my write-up are attached):

(1) Clip-height sweep. Three extra bungee cords were added (two vertices each
pinned by two cords, the third by the remaining two), which cured the earlier
specimen fly-off. The tri-axis accelerometer was placed on the acrylic plate
with a vertex directly below; the retaining clips were set at 0.5, 1.0, 1.5 and
2.0 in above the plate, two drops at each height, on a "Practice" specimen.
RESULT: NONE of the 8 drops triggered (no acceleration above 1000 G), so there
is no CSV for this sweep -- only video. So raising the clips alone did not
restore a triggered measurement.

(2) Accelerometer check. To test whether the sensor/DAQ itself was at fault, the
tri-axis accelerometer was moved onto the BOTTOM (base) plate (no acrylic plate
in the load path) and dropped from 13 in. This is the ONE attached CSV
(Accelerometer_check_Signal1.csv, TP4 session "Practice with dummy"). Our
analysis of it: CH4 (the triggered, drop-axis channel) raw peak ~3072 G
(~3.1x the 1000 G trigger), CFC-1000 ~1154 G, CFC-180 ~280 G, half-amplitude
pulse width ~1.5 ms, windowed delta-v ~3.3 m/s; CH2/CH3 (the off-axis channels)
are small (<=710 G raw). So the sensor + DAQ register a clean base-plate impact.

We read this as: the load path, not the sensor or trigger level, is the failure
-- the acrylic plate seats on / is damped by the bungee-restrained specimen so
the transmitted shock never reaches the plate-mounted sensor, regardless of clip
height in the 0.5-2.0 in range tested.

Please do a DATA ANALYSIS of the attached base-plate CSV and a quantitative
interpretation of the whole diagnostic, then give concrete recommendations.
Specifically:

A. Verify our base-plate numbers independently from the attached CSV: locate the
   impact on CH4 (windowed within the first 10 ms, not a global 0.2 s max),
   baseline-correct, and report raw / CFC-1000 / CFC-180 peak |g|, pulse width,
   and partial-pulse delta-v for CH2/CH3/CH4. Comment on whether CH4 alone being
   large (vs CH2/CH3) is consistent with a single-axis-aligned base-plate hit,
   and whether ~3.3 m/s delta-v is physically consistent with a 13 in
   (0.33 m) drop on a bungee-assisted tower (free-fall would give ~2.5 m/s).

B. Given (1) zero triggers on the acrylic plate across a 0.5-2.0 in clip-height
   sweep but (2) a clean 3x-over-trigger hit on the base plate, what is the most
   likely physical cause, and how would you confirm it? Address each of
   @ctrhjk's candidate error sources: accelerometer position (edge of plate),
   accelerometer orientation, trigger level too high (1000 G), and the acrylic
   plate not transmitting shock efficiently. Use the attached base-plate result
   and the prior vertex result (clean) to discriminate among these.

C. Concrete, prioritized recommendations to get a reliable triggered
   transmitted-acceleration measurement -- or a justification to ABANDON the
   acrylic-plate transmitted-g approach in favor of vertex-mounted sensing for
   our Bayesian-optimization objective (peak transmitted g_max, SEA). Cover:
   lowering / removing the CH4 trigger level (or using a free-run + post-trigger
   capture); a clean load path that forces the plate to strike the specimen
   (clip geometry, a hard top-stop, a captive top plate on linear bushings,
   removing the bungee preload at the moment of impact); accelerometer mounting
   and on-axis alignment on a thin acrylic plate (stud/wax vs adhesive,
   resonance/mass-loading); and whether the acrylic plate's thickness/impedance
   meaningfully attenuates a ~kHz shock to a small lattice.

D. Tie back to standards / published drop-tower practice (SAE J211, ASTM D7136
   instrumented drop-weight, ASTM D3332 cushion curves, ISO 5347 mounting) where
   relevant, and note what additional captures (full ~10 s ringdown, a
   base-plate input channel recorded simultaneously with a transmitted channel,
   n>=5 repeats) we should add so the transmitted-g objective is trustworthy.

Output a single self-contained markdown report we can commit under
edison-trajectories/clip-height/.
"""


def main() -> int:
    # ---- assemble the upload bundle -------------------------------------
    bundle = OUT / "bundle"
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)
    shutil.copy2(
        REPO / "data" / "drop-tests" / "clip-height" / "raw" / "Accelerometer_check_Signal1.csv",
        bundle / "Accelerometer_check_Signal1.csv",
    )
    shutil.copy2(REPO / "data" / "drop-tests" / "clip-height" / "README.md", bundle / "README.md")
    analysis_md = REPO / "docs" / "drop-test-clip-height-analysis.md"
    if analysis_md.exists():
        shutil.copy2(analysis_md, bundle / "drop-test-clip-height-analysis.md")

    if SUBMITTED.exists():
        task_id = json.loads(SUBMITTED.read_text())["task_id"]
        print("reusing task_id:", task_id)
        return 0

    # Edison ANALYSIS requires directory uploads as a single zipped collection.
    resp = client.store_file_content(
        name="clip-height-drop-diagnostic",
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
