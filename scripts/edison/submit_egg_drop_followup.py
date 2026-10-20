"""Follow-up Edison Scientific LITERATURE_HIGH query for the egg-drop demo
(GitHub PR comment 4413896231 by @sgbaird).

Context refinement from the original task (1b90208d):
- The desired demo geometry is a **rooftop-style hard drop** (no drag/parachute,
  no streamers, no air-brakes) onto a fixed landing surface, mimicking a
  planetary-lander touchdown as closely as possible.
- The egg payload is held in a rigid printable cradle (PETG) suspended inside
  a tensegrity (per @sgbaird: "the PETG holder sounds good"), analogous to
  the NASA SUPERball lander concept.
- @sgbaird wants the literature's *best* drag-free egg-protection setup as
  an apples-to-apples baseline / benchmark, and asks whether — under shared
  constraints such as bounding volume and total system mass — a tensegrity
  protector can demonstrably win on a common metric (peak deceleration,
  specific energy absorbed, critical drop height for survival, reusability).

This script writes a verbatim ``formatted_answer`` Markdown and a structured
``model_dump_json`` payload to ``edison-trajectories/`` per the lab convention
(both md and json, see prior tasks).

Usage:

    export EDISON_PLATFORM_API_KEY=...   # or EDISON_API_KEY (auto-mapped)
    pip install edison-client
    python scripts/edison/submit_egg_drop_followup.py
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
This is a FOLLOW-UP literature query for an undergraduate-mentored research
demonstration (PR comment from project lead). The original Edison
LITERATURE_HIGH task (1b90208d-3555-4479-9db0-512d67e69f5f) covered egg
fracture mechanics, tensegrity topology selection, and instrumentation for a
drop test of a raw chicken egg on a multi-material 3D-printed
(PETG strut + TPU 85A tendon) tensegrity. Please do NOT re-derive that
material — focus only on the new questions below.

NEW SCOPE (from the project lead):
We want to mimic a planetary-lander touchdown as closely as possible
(NASA SUPERball-style: rigid payload pod suspended inside a tensegrity shell)
and we want a "rooftop drop" — i.e. NO drag-based slowing (no parachute,
no streamers, no flutter wings, no balloons, no inflated bags that work
primarily by drag/aerodynamic deceleration). The egg sits in a printable
PETG cradle inside the tensegrity. The structure must absorb the impact
purely by elastic / plastic / hyperelastic deformation of the protector
itself on contact with a rigid floor.

QUESTIONS TO ANSWER

1. **Drag-free baseline survey.** What is the published "state of the
   practice" for protecting a fragile payload (egg or egg-equivalent ~30–80 g
   shell-fragile object) in a free-fall drop where drag is intentionally
   excluded as the deceleration mechanism? Survey the engineering-education
   and applied-mechanics literature for drop-tower / building-drop / rooftop
   egg-protector designs whose mechanism of deceleration is one of:
   (a) Crushable foam / honeycomb / lattice / metamaterial cushion (single-
       use plastic deformation),
   (b) Elastic / hyperelastic recoverable cushion (TPU lattice, silicone,
       rubber spring, elastomeric foam),
   (c) Spring / mechanical isolator stack (coil, leaf, bellows, MR damper),
   (d) Granular / particle damper (sand, beads, gels),
   (e) Tensegrity / cable-strut shell (NASA SUPERball lineage,
       icosahedron drone shells),
   (f) Bio-inspired analogues (woodpecker beak, pomelo peel, owl-feather
       sandwich), if any have been demonstrated as drop protectors,
   (g) Anything else with published quantitative survival data.
   For each category, name the canonical reference(s) and report the
   reported survival drop-height, peak deceleration, payload mass, and
   bounding volume / footprint where available.

2. **What is the current "best in class"?** Of the drag-free egg-protection
   designs above, which has the best published combination of
   (i) maximum survivable drop height for an egg-mass payload,
   (ii) lowest specific volume V/m_payload, and
   (iii) lowest specific mass m_protector / m_payload?
   Please give a short ranked shortlist (3–5 designs) with the headline
   numbers and citations, distinguishing single-use vs reusable and
   Earth-gravity vs Mars/Moon-relevant data. Identify any standardized
   "egg-drop benchmark" / "fragile-payload benchmark" used in the
   pedagogy or planetary-lander literature that we could adopt as
   our baseline.

3. **Apples-to-apples benchmark protocol.** Recommend a fair benchmarking
   protocol so that a PETG+TPU tensegrity (with internal PETG egg cradle)
   can be quantitatively compared against the drag-free baselines under
   shared constraints. Please specify:
   - Constraint set: e.g. fixed bounding volume V_max (cite a sensible
     default, e.g. inscribed in a 200 mm sphere or a 200×200×200 mm cube),
     fixed total system mass m_sys, fixed payload mass m_egg ≈ 55 g,
     fixed landing surface (rigid concrete floor per ASTM D5276),
     fixed drop orientation policy (worst-case or random).
   - Primary scalar figure of merit (e.g. critical drop height h_crit at
     which P_survive = 0.5; peak g_max at h = 1 m; specific energy
     absorbed SEA = E_abs / m_protector; volumetric efficiency
     E_abs / V; reusability count N_impact_to_failure).
   - Secondary figures of merit and how to plot them.
   - Statistical replicate count and recommended dose-response design
     (drop-height ladder, n per height, fresh egg per drop).
   - Any existing standards (ASTM D5276 free-fall drop, ASTM F1292
     impact attenuation, ISTA series, MIL-STD-810, etc.) we should
     cite as the methodological backbone.

4. **Where does a tensegrity actually win?** Under each of the proposed
   benchmark constraint sets (bounded V, bounded m, bounded both),
   identify the regime(s) — drop height, payload mass, reusability
   requirement, omnidirectionality requirement — in which a
   PETG+TPU tensegrity is *expected* (per the published mechanics)
   to dominate the baselines. Cite quantitative comparisons where they
   exist (e.g. Bauer 2021 tensegrity vs octet/Kelvin lattices,
   Pajunen 2019 reusability, Zhang 2018 six-bar SUPERball drop,
   Zha 2020/2024 icosahedron drone collision data, Skelton/Sultan
   class-1 tensegrity lander concepts, NASA Tensegrity Robotics
   Toolkit / SUPERball publications). Identify regimes where a
   conventional crushable foam or TPU lattice is expected to beat
   the tensegrity, so the recommended demonstration is honestly
   framed.

5. **Recommended single-figure demo plot.** Propose ONE publication-
   quality figure that would make the strongest case for the tensegrity
   protector under the benchmark of question 3. The figure should
   compare the PETG+TPU tensegrity against 2–4 named baseline designs
   (one per category from question 1) on a common axis pair (e.g.
   peak g vs drop height with a survivability band; or specific energy
   absorbed vs bounding volume with iso-mass contours). Include:
   - Axis specification with units and recommended range.
   - Which baselines to plot and where the published data points sit.
   - The hypothesized location of the tensegrity data and the qualitative
     argument for why it should fall in the winning region.
   - Any caveats / failure modes the figure should disclose.

6. **Quick-look references / suppliers / reproducibility.** Provide a
   short bibliography of the most useful primary sources, plus, where
   relevant, named commercial parts (foams, lattices, MR dampers,
   accelerometer breakouts) so an undergraduate team can reproduce
   the baseline measurements.

Please cite specific peer-reviewed papers, conference proceedings,
NASA technical reports, ASTM/ISTA/MIL standards, and product datasheets
where applicable. Quantitative claims should include units and a primary
source.
""".strip()


def main() -> None:
    client = EdisonClient()
    task = {"name": JobNames.LITERATURE_HIGH, "query": QUERY}

    submission_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    print(f"[{submission_ts}] Submitting Edison LITERATURE_HIGH egg-drop FOLLOW-UP "
          "query (drag-free baseline + volume/mass-constrained tensegrity benchmark)...")

    responses = client.run_tasks_until_done(task)
    response = responses[0]

    task_id = getattr(response, "task_id", None) or getattr(response, "id", "unknown")
    short_id = str(task_id).split("-")[0]

    md_path = OUT_DIR / f"egg-drop-followup-{short_id}.md"
    json_path = OUT_DIR / f"egg-drop-followup-{short_id}.json"

    md_path.write_text(response.formatted_answer, encoding="utf-8")
    json_path.write_text(response.model_dump_json(indent=2), encoding="utf-8")

    print(f"  task_id        = {task_id}")
    print(f"  formatted_answer -> {md_path.relative_to(REPO_ROOT)}")
    print(f"  full payload     -> {json_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
