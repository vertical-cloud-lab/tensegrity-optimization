"""Submit Edison Scientific LITERATURE_HIGH query for drop-test troubleshooting.

Driven by sgbaird PR comment 4546311380:
> send to edison scientific (high effort literature). Fetch this session.
> Commit all artifacts. Summarize in your comment reply and provide direct
> link to md file.

Context attached: docs/drop-test-protocol.md (this PR's doc) describes the
first instrumented crush/drop attempts on Jeff Hill's drop tower, the
observed failure modes (specimen lift-off pre-impact, ~25 deg cage tilt
from loose rod/hole tolerance, late slow-mo framing), and the planned
three-test next iteration (bare specimen -> plate-only -> instrumented
cage drop).
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from edison_client import EdisonClient, TaskRequest

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "drop-test"
OUT.mkdir(parents=True, exist_ok=True)

# edison-client >= 0.12 reads EDISON_PLATFORM_API_KEY (not EDISON_API_KEY)
api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY")
if not api_key:
    raise SystemExit("EDISON_PLATFORM_API_KEY (or EDISON_API_KEY) not set")
client = EdisonClient(api_key=api_key)

PROMPT = r"""
We are running our first instrumented crush / drop tests on small (~50 mm
edge) multi-material 3D-printed tensegrity unit cells (PLA or PETG struts,
TPU 85A tendons; ~10-50 g per cell) on a benchtop drop tower with an
electromagnetic-hoist release.

Setup (also see attached `docs/drop-test-protocol.md`):
 - Drop tower with rigid steel base plate; magnet-release hoist.
 - Accelerometer #1 mounted on the steel base plate (input shock).
 - Accelerometer #2 mounted on a small acrylic "top plate" that sits on
   the specimen (transmitted shock). Manuals are the Vishay/PCB
   TP4 Quick Start (W20000-98-15) and TP4 User's Guide (W20000-98-14).
 - A "cage" of two 1/4"-thick acrylic plates separated by four ~18 in
   threaded steel rods (cut + threaded in-house) is meant to keep the
   top plate captive over the specimen.
 - Slow-motion video on a phone (high-speed camera from PSC available
   as an upgrade).

Observed failure modes from the first instrumented drop:
 1. Specimen / bottom acrylic plate separation during descent: the
    tensegrity cell lifts off the lower plate before impact, so it is
    no longer aligned under the top plate.
 2. Cage tilt: the rod-to-hole clearance lets the top plate tilt ~25 deg
    off horizontal, biasing the transmitted-acceleration measurement and
    risking off-axis loading of the accelerometer.
 3. Slow-mo framing starts after hoist release, so the initial descent
    is out of frame.
 4. Data is only being saved for the initial ~200 ms shock window; we
    actually want the full ~10 s ringdown.

Quantities of interest the drop tower must feed into our Bayesian
optimization stack (see companion `edison-trajectories/objective-functions/`
work):
 - Peak transmitted g_max on the top plate (minimize)
 - Specific energy absorption (SEA) inferred from drop height,
   specimen mass, and input-vs-transmitted impulse difference
 - Full ~10 s ringdown waveform (secondary modes, damping)
 - Reusability / number of drops to failure N_reuse
 - Slow-mo or high-speed displacement field of the deforming struts

Please produce a HIGH-EFFORT literature synthesis aimed specifically at
*troubleshooting and de-risking this benchtop drop-tower workflow for
small 3D-printed lattice / tensegrity specimens*. Cite peer-reviewed and
standards literature throughout. Use the section skeleton below; keep
each subsection self-contained so the lab team can read just the part
they need.

(a) **Best-practice benchtop drop-tower workflows** for sub-100 g 3D-printed
    cellular / lattice / tensegrity specimens:
    - ASTM / ISO standards that apply or have to be adapted (e.g.
      ASTM D5276 free-fall package drop, ASTM D7136 instrumented drop-weight,
      ISO 6603 puncture, ISO 1683 reference levels, ASTM D3332 cushioning
      cushion-curve, MIL-STD-810 method 516, ASTM E1820 if fracture).
      For each: what it covers, what has to be adapted for our small
      tensegrity samples, and the key reported metrics.
    - Recommended impact velocities, drop heights, repeat counts, and
      Bruceton-style sensitivity protocols seen in the literature for
      similar specimen mass / size.
    - Conditioning (humidity, temperature, anneal) for PLA + PETG + TPU
      85A specimens before mechanical test.

(b) **Specimen-retention fixtures**. Survey published fixturing that
    addresses our failure mode #1 (specimen lift-off before impact) and
    failure mode #2 (off-axis tilt) for cellular and tensegrity samples.
    Specifically discuss:
    - Linear bushings vs. plain holes on guide rods: what tolerance
      class / clearance is typical, what tilt angle that implies for a
      cage of our geometry, and recommended sleeve bearing classes
      (e.g. IGUS DryLin J / R; LM linear bushings).
    - Light retention clips, magnets, or elastic preload that hold the
      top plate seated on the specimen until impact without significantly
      pre-loading the specimen.
    - Methods of bonding / mechanically anchoring the specimen to the
      bottom plate without changing its compliance (double-sided
      transfer tape, register pins through tensegrity nodes, V-block
      cradles, vacuum chuck).
    - Vertex-mounted accelerometer schemes (sensor bonded to one
      tensegrity node) and how they manage cable strain relief and
      survivability under repeated drops.

(c) **Instrumentation and signal acquisition** specific to small,
    lightly damped lattice samples:
    - Sensor selection: ADXL375 / Endevco / PCB 350-series ranges and
      bandwidths suitable for ~kHz shock; required full-scale (e.g.
      +-200 g vs +-500 g) given expected g_max for our specimen mass.
    - Mounting: adhesive vs stud vs wax, and the resonance shift /
      mass-loading bias each introduces on a thin acrylic top plate.
    - Sample rate (>= 10x the highest frequency of interest) and
      anti-alias filtering recommendations from ISO 5347 / SAE J211.
    - **Long-window capture** (the ~10 s ringdown): trigger / pre-trigger
      settings, ring-buffer length, and how groups have separated the
      initial shock from the slow decay in published drop-tower work.
    - Synchronizing slow-mo (or high-speed) video with the accelerometer
      stream (photogate / LED-flash / TTL / SMPTE).

(d) **High-speed and phone-slow-mo imaging** of cellular impact:
    - Minimum frame rate / shutter / lighting recommended for ~1-3 m/s
      impact on a 50 mm specimen.
    - DIC (digital image correlation) on tensegrity / lattice impact:
      speckle prep on PLA/PETG, software (Ncorr, GOM, DICe), reported
      strain-rate / displacement uncertainty.
    - When a modern phone's slow-mo (240-960 fps) is and isn't adequate
      relative to a checked-out high-speed camera (Photron / Phantom).

(e) **Data reduction and uncertainty** for the BO objective stack:
    - How to convert raw a(t) -> g_max, SEA, cushion-curve, and
      attenuation transfer function in published drop-tower studies.
    - Reproducibility / specimen-to-specimen scatter reported for FFF
      lattice impact -> sets the experimental noise floor BO has to see.
    - Typical confidence-interval reporting (n, std, IQR) for these
      metrics.

(f) **Common gotchas** specifically called out in the drop-tower
    literature for cellular / lattice / tensegrity specimens:
    - Plate-bounce contamination of g_max (our failure mode that the
      cage is meant to solve).
    - Strain-rate effects in TPU 85A tendons at impact rates vs the
      quasi-static rate where E ~ 12 MPa is measured.
    - Anisotropy from FFF layer orientation under impact.
    - Frame ringing / fixture resonance polluting the high-frequency
      tail of a(t).
    - Magnet-release jerk / residual hoist swing.

(g) **Closely related published drop-tower datasets** on 3D-printed
    lattices / tensegrity / cellular impact that we should benchmark
    against (Zhang 2018, Davami 2025, Intrigila 2022, Pajunen 2019,
    Khatri-Egan 2024, Anand 2022, and any others you find). For each:
    specimen geometry, material, instrumentation, drop heights, reported
    g_max / SEA / N_reuse, and how their fixture handled the
    specimen-retention problem.

For every recommendation in (a)-(g), please cite peer-reviewed papers,
standards, or manufacturer documentation -- no uncited claims. Where
quantitative values are given (g, fps, kHz, MPa, mm, deg), include the
source and the original measurement context.

Output: a single self-contained markdown report we can drop into
`edison-trajectories/drop-test/` alongside this PR's
`docs/drop-test-protocol.md`.
"""

# Attach the protocol doc that the user just merged
proto_uri = client.upload_file(
    file_path=str(REPO / "docs" / "drop-test-protocol.md"),
    name="drop-test-protocol.md",
    description="Current drop-test setup, failure modes, and 3-test plan",
    tags=["drop-test", "protocol", "tensegrity"],
)
print("uploaded:", proto_uri)

task = TaskRequest(
    name="job-futurehouse-paperqa3-high",
    query=PROMPT,
    tags=["drop-test", "tensegrity", "issue-troubleshooting"],
)
submitted = client.create_task(task, files=[proto_uri])
task_id = submitted if isinstance(submitted, str) else getattr(
    submitted, "task_id", None
) or getattr(submitted, "trajectory_id", None) or str(submitted)
print("submitted task_id:", task_id)

(OUT / "drop-test-SUBMITTED.json").write_text(
    json.dumps(
        {"task_id": task_id, "uploaded_files": [proto_uri], "task_type": "LITERATURE_HIGH"},
        indent=2,
    )
)

TERMINAL = {"success", "failed", "cancelled", "error", "crashed"}
POLL = 30
t0 = time.time()
while True:
    r = client.get_task(task_id=task_id)
    status = getattr(r, "status", None) or r.model_dump().get("status")
    elapsed = int(time.time() - t0)
    print(f"[{elapsed:5d}s] status={status}")
    if status in TERMINAL:
        break
    time.sleep(POLL)

dump = r.model_dump()
(OUT / f"drop-test-{task_id}.json").write_text(json.dumps(dump, indent=2, default=str))
md = dump.get("formatted_answer") or dump.get("answer") or ""
(OUT / f"drop-test-{task_id}.md").write_text(md if isinstance(md, str) else json.dumps(md, indent=2))
print(f"wrote {OUT}/drop-test-{task_id}.md  ({len(md)} chars)")
