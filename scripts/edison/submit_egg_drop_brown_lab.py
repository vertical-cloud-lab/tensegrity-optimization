"""Follow-up Edison Scientific LITERATURE_HIGH query for the egg-drop demo
(GitHub PR comment 4427200746 by @sgbaird-alt).

Question: Keith A. Brown's lab (Boston University) has reported "superlative"
mechanical energy absorption structures discovered via autonomous /
Bayesian-optimization closed-loop experimentation (BEAR / "self-driving lab"
work — Gongora 2020 Sci. Adv., Snapp 2024, etc.). Could that family of
geometries serve as a *baseline* or *reference upper-bound* in the drag-free
egg-drop benchmark proposed in the previous follow-up (Edison task
f41b7034)? Does it even make sense given the very different test conditions
(quasi-static / sub-impact vs free-fall drop, BO search space vs literature
designs, single-shot crushing vs reusable)?

This script writes a verbatim ``formatted_answer`` Markdown and a structured
``model_dump_json`` payload to ``edison-trajectories/`` per the lab convention
(both md and json, see prior tasks).

Usage:

    export EDISON_PLATFORM_API_KEY=...   # or EDISON_API_KEY (auto-mapped)
    pip install edison-client
    python scripts/edison/submit_egg_drop_brown_lab.py
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

# edison-client >= 0.12 reads EDISON_PLATFORM_API_KEY; tolerate the older
# EDISON_API_KEY name still documented in copilot-instructions.md.
if "EDISON_PLATFORM_API_KEY" not in os.environ and "EDISON_API_KEY" in os.environ:
    os.environ["EDISON_PLATFORM_API_KEY"] = os.environ["EDISON_API_KEY"]

from edison_client import EdisonClient, JobNames  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "edison-trajectories"
OUT_DIR.mkdir(parents=True, exist_ok=True)

QUERY = """
This is a SECOND FOLLOW-UP literature query for an undergraduate-mentored
research demonstration. The first Edison LITERATURE_HIGH task on this topic
(1b90208d-3555-4479-9db0-512d67e69f5f) covered egg fracture mechanics,
tensegrity topology selection, and instrumentation for a drop test of a raw
chicken egg on a multi-material 3D-printed (PETG strut + TPU 85A tendon)
tensegrity. The first follow-up (f41b7034-439e-45de-b97f-4bf1d85b9811)
proposed an apples-to-apples drag-free egg-drop benchmark with shared
constraints (Ø 200 mm bounding sphere, m_sys ≤ 500 g, m_egg ≈ 55 g, ASTM
D5276 rigid floor, primary FoM h_crit via Bruceton staircase, secondary SEA
/ η_V / N_reuse). Please do NOT re-derive that material — focus only on the
new question below.

NEW QUESTION (from the project lead):

Keith A. Brown's lab at Boston University (PI: Prof. Keith A. Brown,
Mechanical Engineering / Materials Science, BU) has published a series of
papers on "superlative" or "record-setting" mechanical energy absorbing
structures discovered using autonomous / Bayesian-optimization closed-loop
experimentation — the BEAR ("Bayesian Experimental Autonomous Researcher")
self-driving lab and successor systems. Representative references include:

  - Gongora, Snapp, Whiting, et al., "A Bayesian experimental autonomous
    researcher for mechanical design," Science Advances 6, eaaz1708 (2020).
  - Snapp et al. and follow-on BEAR / autonomous-design papers from the
    Brown group on FFF-printed energy-absorbing structures.
  - Any subsequent "superlative" / "record-setting" energy-absorption
    structure papers from this group (please surface the most recent and
    most-cited follow-ups, including any review articles).

Please answer all of the following, with peer-reviewed citations:

1. **What exactly did Brown's group report?**
   Summarize the 2–4 most relevant Brown-lab publications on
   energy-absorbing structures: what was the design space (parametric
   FFF-printed lattice / hollow-strut / unit-cell family?), what was the
   loading mode (quasi-static uniaxial compression? drop-tower impact?
   strain rate?), what was the reported figure of merit (toughness J/cm³,
   SEA J/g, plateau stress, energy ratio η = E_abs / (σ_max · ε)?), and
   what numerical record(s) did they claim relative to prior art?
   List the geometry families they explored (e.g. concave hexagonal
   honeycombs, beam-tied unit cells, BO-discovered topologies, etc.).

2. **Loading-regime applicability to a drag-free egg drop.**
   Were Brown's "superlative" results obtained under (a) quasi-static
   compression (mm/min), (b) low-velocity impact (drop-tower at <5 m/s),
   or (c) high-velocity impact (>10 m/s, free-fall ≥ ~5 m)? Quote the
   reported strain rates / impact velocities. Critically assess whether
   the FoM they report (typically toughness or SEA in quasi-static
   compression) extrapolates to peak-deceleration / survival in a free-
   fall egg drop. Specifically, does the BEAR ranking of geometries
   change between quasi-static crush and impact (any published evidence,
   or any general result from the cellular-solids / metamaterials
   literature relating quasi-static SEA to impact peak-g or h_crit)?

3. **Single-use vs reusable.**
   Are the Brown-lab structures single-use (densified and destroyed during
   the energy-absorption event) or reusable (elastic / hyperelastic
   recovery, like a tensegrity)? What polymer / material did the BEAR work
   use (PLA? TPU? other)? How does this map to the categories defined in
   the prior follow-up task (a) crushable foam / lattice cushion,
   (b) elastic recoverable cushion, (e) tensegrity?

4. **Could the Brown-lab "superlative" geometry serve as the upper-bound
   baseline in our benchmark?**
   Under the shared constraints from Edison task f41b7034 (Ø 200 mm
   bounding sphere, m_sys ≤ 500 g, m_egg ≈ 55 g, rigid concrete floor
   per ASTM D5276, h up to 15 m), would it be defensible to:
   (i) FFF-print the BEAR-discovered "best" unit cell as a solid cushion
       block (or cell tessellation) of the same bounding volume,
   (ii) use it as a *baseline* curve on the recommended demo plot
       (peak g vs drop height with the egg-fracture survivability band),
   (iii) interpret it as the **closed-loop-optimized baseline** representing
       what an automated BO search converges to within a parametric
       design space, against which the tensegrity (which is a
       *topologically distinct* class-1 cable-strut shell, not in the
       BEAR search space) is compared?
   Please give an explicit yes / no / yes-with-caveats recommendation,
   and identify any technical issues:
       - Can the BEAR optimal cell be re-printed faithfully on a
         consumer FFF printer (Bambu H2D class) given that BEAR papers
         report the optimal geometry parameters?
       - Is the BEAR FoM (quasi-static toughness J/cm³) at all
         comparable to peak-g in a free-fall drop, or is the comparison
         apples-to-oranges?
       - Are there licensing / reproducibility constraints (proprietary
         BO model, unreleased optimal-geometry STL)?
       - Does the "superlative" claim hold under impact loading, or
         only under quasi-static loading?

5. **Better alternative baselines if BEAR is not appropriate.**
   If the BEAR / Brown-lab geometry is *not* a fair baseline for a
   drag-free egg drop (because of loading-regime mismatch or
   non-reproducibility), what would be the closest defensible "BO-optimized
   FFF-printed energy absorber" baseline from the autonomous-design or
   metamaterials literature that *is* reported under impact loading?
   Examples to consider: Gu et al. (MIT, BO-optimized composites under
   drop-tower impact); the autonomous-design literature on auxetic /
   hierarchical lattices under impact; any recent follow-on work
   (2023–2026) extending BEAR-style autonomous design to impact regimes.

6. **Concrete recommendation.**
   In one paragraph, recommend either (a) include a Brown-lab BEAR-derived
   FFF lattice as the **"BO-optimized lattice baseline"** alongside the
   foam, honeycomb, and tensegrity entries on the demo plot, OR
   (b) decline to use BEAR as a baseline and instead cite it as
   conceptually-related prior art for *how to discover* the optimal
   tensegrity (i.e., apply the BEAR methodology to our class-1 tensegrity
   design space), explaining the reasoning either way. Note that the
   project itself is a Bayesian-optimization-of-tensegrities effort, so
   the framing "BEAR for tensegrities" is the natural narrative if the
   geometry is not directly comparable.

Please cite specific peer-reviewed papers, conference proceedings, and
technical reports where applicable. Quantitative claims should include
units and a primary source.
""".strip()


def main() -> None:
    client = EdisonClient()
    task = {"name": JobNames.LITERATURE_HIGH, "query": QUERY}

    submission_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    print(f"[{submission_ts}] Submitting Edison LITERATURE_HIGH egg-drop "
          "Brown-lab baseline query (BEAR / superlative energy absorber as a "
          "drag-free benchmark)...")

    responses = client.run_tasks_until_done(task)
    response = responses[0]

    task_id = getattr(response, "task_id", None) or getattr(response, "id", "unknown")
    short_id = str(task_id).split("-")[0]

    md_path = OUT_DIR / f"egg-drop-brown-lab-{short_id}.md"
    json_path = OUT_DIR / f"egg-drop-brown-lab-{short_id}.json"

    md_path.write_text(response.formatted_answer, encoding="utf-8")
    json_path.write_text(response.model_dump_json(indent=2), encoding="utf-8")

    print(f"  task_id        = {task_id}")
    print(f"  formatted_answer -> {md_path.relative_to(REPO_ROOT)}")
    print(f"  full payload     -> {json_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
