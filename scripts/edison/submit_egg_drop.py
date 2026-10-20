"""Submit a LITERATURE_HIGH Edison Scientific query about an egg-drop demonstration
built on a 3D-printed (PETG strut + TPU 85A tendon) tensegrity, and persist both the
verbatim ``formatted_answer`` (Markdown) and the structured ``model_dump_json``
payload under ``edison-trajectories/``.

Context: GitHub issue "Explore the idea of using an egg drop" — the project
fabricates Snelson-class tensegrity unit cells on a Bambu H2D as PETG struts +
TPU 85A tendons. The issue asks whether dropping a raw chicken egg from height
into / onto such a tensegrity (or a tessellation of unit cells) is a viable
educational / promotional demo, how to secure the egg (mid-print pause to
embed it, or post-print harness on a real strut+cable structure), and what
instrumentation (high-speed video at the landing, embedded accelerometer,
force-sensitive landing pad) would best characterize the cushioning.

Usage:

    export EDISON_API_KEY=...
    python scripts/edison/submit_egg_drop.py
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

# edison-client >= 0.12 reads ``EDISON_PLATFORM_API_KEY``; tolerate the older
# ``EDISON_API_KEY`` variable name documented in copilot-instructions.md.
if "EDISON_PLATFORM_API_KEY" not in os.environ and "EDISON_API_KEY" in os.environ:
    os.environ["EDISON_PLATFORM_API_KEY"] = os.environ["EDISON_API_KEY"]

from edison_client import EdisonClient, JobNames  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "edison-trajectories"
OUT_DIR.mkdir(parents=True, exist_ok=True)

QUERY = """
We are designing an undergraduate-mentored research demonstration around a
multi-material 3D-printed tensegrity structure and would like a literature- and
practice-grounded answer to the following compound question.

PROJECT CONTEXT
- Hardware: Bambu Lab H2D (IDEX FFF, 0.4 mm nozzle), single printer.
- Materials: PETG struts (E ~ 2 GPa, density ~ 1270 kg/m^3, sigma_break ~ 50 MPa)
  and TPU 85A tendons (NinjaFlex-class, secant E ~ 12 MPa, density ~ 1200 kg/m^3,
  sigma_break ~ 26 MPa, strain to break ~ 5.5-6.6).
- Topology: Snelson-style class-1 unit cells (3-strut T-prism and related
  prisms/icosahedra), printable tendon diameter 1.2-6.0 mm, strut diameter
  >= 2.0 mm. We can also tessellate unit cells into a panel/mat or build a
  tensegrity-icosahedron ("ball").
- Goal of the demo: drop a raw chicken egg (mass ~ 50-60 g, shell fracture
  threshold roughly 25-35 N quasi-static, peak deceleration tolerance commonly
  cited around 50-150 g for short-duration impacts) from a known height and
  have the tensegrity absorb enough energy to keep the shell intact, while
  instrumenting the event well enough to publish.

QUESTIONS WE WANT THE EDISON ANSWER TO ADDRESS

1. Is an egg drop on a tensegrity a defensible educational/promotional
   demonstration? Summarize prior egg-drop pedagogy literature (mechanical
   engineering / physics education), and any prior published or popular work
   that has specifically used tensegrity, lattice, or auxetic structures as
   the cushion. Note if anyone has already done this so we do not over-claim
   novelty.

2. Egg fracture mechanics and impact tolerance. What is the published shell
   fracture force, fracture energy, and tolerable peak deceleration / impulse
   profile for a raw chicken egg (Gallus gallus domesticus) under drop or
   compression loading? Cite quantitative values with primary sources.

3. How should we secure the egg to the tensegrity? Compare and recommend:
   (a) Mid-print pause on the H2D to embed the egg inside an interior cavity
       of the structure (analogous to embedded-electronics tutorials). What
       are the documented thermal, adhesion, contamination, and humidity
       risks of pausing a PETG print at ~230 C extruder / ~70 C bed and
       inserting biological material? Will the egg shell survive the resumed
       layer being deposited on top of (or near) it?
   (b) Post-print harness using a TPU sleeve, net, or basket integrated with
       the tendons of a real strut+cable assembly.
   (c) External rigid cradle suspended in the tensegrity by additional TPU
       tendons.
   Discuss food-safety / cleanup implications for a public demo.

4. Single unit cell vs tessellation vs tensegrity icosahedron ("ball"). For an
   ~1-2 m drop of a 50-60 g egg, which topology gives the best deceleration
   profile and the best visual/educational story? Cite published energy-
   absorption or impact data for tensegrity panels, prisms, and icosahedra.
   How does this compare to conventional honeycomb / TPU lattice cushions
   from the AM literature?

5. Instrumentation plan. What is the best published practice for capturing
   such an impact in an undergraduate lab?
   - High-speed video at the landing point: recommended frame rate, field of
     view, lighting, and fiducials for digital image correlation or simple
     marker tracking on a 2 m drop of an egg-on-tensegrity.
   - Embedded accelerometer in or on the egg/payload: which low-mass MEMS
     IMUs (e.g., ADXL375, KX134, H3LIS331DL) have the range (>= 200 g) and
     bandwidth (>= 1 kHz) to resolve the impact, and what wiring / wireless
     options minimize tether artifacts?
   - Force-sensitive landing pad: thin-film FSR vs piezoelectric sheet vs
     instrumented load cell plate; sampling rate and dynamic range needed
     to resolve the rebound.
   - Recommended synchronization scheme between camera, IMU, and pad.

6. Summarize, in <= 10 numbered recommendations, a concrete experimental
   protocol for a first egg-drop demo on a PETG+TPU 85A tensegrity printed
   on a Bambu H2D, including drop heights, number of replicates, expected
   peak g, and the most informative figure to publish.

Please cite specific papers, standards (e.g., ASTM D5276 free-fall drop,
ASTM F1292 attenuation), and product datasheets where applicable. Where
quantitative values are given, please include units and source.
""".strip()


def main() -> None:
    client = EdisonClient()
    task = {"name": JobNames.LITERATURE_HIGH, "query": QUERY}

    submission_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    print(f"[{submission_ts}] Submitting Edison LITERATURE_HIGH egg-drop query...")

    # Blocking until done; the lab convention is to fetch in the same session
    # when feasible so the trajectory + references are committed together.
    responses = client.run_tasks_until_done(task)
    response = responses[0]

    task_id = getattr(response, "task_id", None) or getattr(response, "id", "unknown")
    short_id = str(task_id).split("-")[0]

    md_path = OUT_DIR / f"egg-drop-tensegrity-{short_id}.md"
    json_path = OUT_DIR / f"egg-drop-tensegrity-{short_id}.json"

    md_path.write_text(response.formatted_answer, encoding="utf-8")
    json_path.write_text(response.model_dump_json(indent=2), encoding="utf-8")

    print(f"  task_id        = {task_id}")
    print(f"  formatted_answer -> {md_path.relative_to(REPO_ROOT)}")
    print(f"  full payload     -> {json_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
