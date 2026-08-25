#!/usr/bin/env python3
"""Submit the mechanism-oriented data-figure example to Edison ANALYSIS for feedback.

Per PR review comment 4664873230 (@sgbaird: "send this to edison analysis for
feedback"), this uploads the standalone mechanistic-data-figure example
(figures/examples/mechanistic-data-figure-example.{png,pdf}, its generator, and
README) as a single zipped collection (required for ANALYSIS) and asks for
structured, actionable feedback on the figure design before real processed data
and high-speed-camera frames are swapped in.

Non-blocking: the task id is written to a ``*-SUBMITTED.json`` placeholder for a
later fetch via ``client.get_task(task_id)`` (see fetch_mechfig_feedback.py).

Run::

    python scripts/edison/submit_mechfig_feedback.py
"""
from __future__ import annotations

import json
import os
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    env = HERE / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


_load_dotenv()
if os.environ.get("EDISON_API_KEY") and not os.environ.get("EDISON_PLATFORM_API_KEY"):
    os.environ["EDISON_PLATFORM_API_KEY"] = os.environ["EDISON_API_KEY"]

from edison_client import EdisonClient, JobNames  # noqa: E402
from edison_client.models import TaskRequest  # noqa: E402

TRAJ = HERE / "edison-trajectories" / "mechfig-feedback"
BUNDLE_DIR = TRAJ / "bundle"
BUNDLE = TRAJ / "mechfig-bundle.zip"
SUBMITTED = TRAJ / "mechfig-feedback-SUBMITTED.json"

QUERY = """\
Attached (mechanistic-data-figure-example.png/.pdf, plus its matplotlib
generator and README) is a STANDALONE, ILLUSTRATIVE example figure -- built with
SYNTHETIC but physically-plausible data -- for an ASME Journal of Mechanical
Design (JMD) manuscript on multi-material 3D-printed tensegrity-inspired energy
absorbers (rigid PLA struts in compression + soft TPU cables in tension, printed
on a Bambu Lab H2D dual-nozzle printer, tested under drop-weight impact).

The manuscript currently lacks figures that connect the measured DATA to the
underlying MECHANISM. This example is a template for that kind of figure. It has
four panels:
  (a) Processed drop-impact deceleration curves: rigid control vs. tensegrity,
      SAE J211 CFC-180 filtered, with the raw 125 kHz tensegrity trace faded in
      to motivate filtering; a peak-transmitted-acceleration reduction callout;
      and three shaded mechanistic phases A (contact / cable pre-tension),
      B (strut+cable load redistribution -- the energy-spreading plateau, i.e.
      the actual mechanism), C (recovery / rebound).
  (b) T3-prism specimen callout: red PLA struts (compression), blue TPU cables
      (tension), one strut end circled.
  (c) Joint callout: cables anchoring INSIDE the strut end (the strut acting as a
      rigid cage with discrete cable outlets) -- the load path that flattens the
      peak.
  (d) Deformation snapshot at the phase-B plateau.
In the real article, panels (b)-(d) would be high-speed-camera frames / specimen
photos registered to marked points on the curve. The curves are anchored to the
documented real campaign (impact ~4.2 ms, control CFC-180 peak ~1792 G,
tensegrity ~370-463 G => ~74-79% reduction).

Please give concrete, prioritized, actionable feedback on this figure as a
publication-quality MECHANISTIC data figure for JMD. Specifically:

1. Storytelling: does the figure successfully link the measured signal to the
   structural mechanism? What is missing to make the load-path / energy-
   redistribution argument convincing to a mechanics reviewer?
2. Which additional quantities or panels would strengthen the mechanistic
   narrative (e.g., transmitted force vs. time, energy/impulse integral,
   displacement or strain from DIC, specific energy absorption, force-
   displacement hysteresis, cable tension vs. strut compression, phase-resolved
   high-speed frames)? Recommend the highest-value 1-2 additions.
3. Registration: best practice for tying camera frames / specimen photos to
   specific points/phases on the curve (markers, insets, leader lines, time
   stamps) without clutter.
4. Rigor / honesty: how to clearly mark synthetic vs. real data; what
   uncertainty / replicate information (n, CV, error bands) a JMD reviewer would
   expect; filtering disclosure (CFC class, sampling rate).
5. Layout, axes, color, and accessibility (colorblind-safe palette, font sizes,
   panel proportions, legend placement) for a single- vs. double-column ASME
   figure.
6. Any physics red flags in the synthetic curves themselves (impact duration,
   peak ratios, plateau shape, rebound) that would look implausible to a
   reviewer and should be tuned before real data is substituted.

Return a prioritized, itemized revision list we can implement directly, plus a
short "what an ideal version of this figure looks like" summary.
"""


def _make_bundle() -> None:
    files = sorted(p for p in BUNDLE_DIR.iterdir() if p.is_file())
    with zipfile.ZipFile(BUNDLE, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            zf.write(p, arcname=p.name)
    print(f"built {BUNDLE} ({BUNDLE.stat().st_size} bytes, {len(files)} files)")


def main() -> None:
    _make_bundle()
    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY")
        or os.environ.get("EDISON_API_KEY")
    )
    resp = client.store_file_content(
        name="mechfig-bundle",
        file_path=str(BUNDLE),
        as_collection=True,
    )
    entry_id = resp.data_storage.id
    uri = f"data_entry:{entry_id}"
    print(f"uploaded collection -> {uri}")

    task = TaskRequest(name=JobNames.ANALYSIS, query=QUERY)
    submitted = client.create_task(task, files=[uri])
    task_id = getattr(submitted, "task_id", None) or (
        submitted if isinstance(submitted, str) else None
    )
    print(f"submitted ANALYSIS task_id={task_id}")

    SUBMITTED.write_text(json.dumps({
        "slug": "mechfig-feedback",
        "task_id": str(task_id),
        "job": str(JobNames.ANALYSIS),
        "uploaded_collection": uri,
        "note": "non-blocking; fetch via scripts/edison/fetch_mechfig_feedback.py",
    }, indent=2))
    print(f"wrote {SUBMITTED}")


if __name__ == "__main__":
    main()
