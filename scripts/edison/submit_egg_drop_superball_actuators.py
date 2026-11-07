"""Follow-up Edison Scientific LITERATURE_HIGH query for the egg-drop demo.

PR comment (new requirement) by @sgbaird-alt:

  > clarify the following via edison search: SUPERball v2 (Vespignani et al.
  > 2018): "A 2-meter diameter, 36 kg, fully actuated six-bar tensegrity
  > robot with 24 actuators and compliant nylon cables (up to 15% stretch).
  > Designed to survive impact velocities upward of 8 m/s, with simulations
  > analyzing up to 15 m/s impacts. Cable stiffness ~4000 N/m produced
  > lowest peak cable forces (~950 N) (vespignani2018designofsuperball pages
  > 1-2, vespignani2018designofsuperball pages 2-4)."
  >
  > What are the actuators? Explain it to me simply. How does this relate
  > to the current study which has largely untensioned connections and no
  > actuators? How does that limit the usefulness of this study? How
  > could/should the design be adjusted to be more amenable to future work?
  > Are there one-off validations we could use to help alleviate this tech
  > transfer concern?

This script writes a verbatim ``formatted_answer`` Markdown and a structured
``model_dump_json`` payload to ``edison-trajectories/`` per the lab convention
(both md and json, see prior tasks).

Usage:

    export EDISON_PLATFORM_API_KEY=...   # or EDISON_API_KEY (auto-mapped)
    pip install edison-client
    python scripts/edison/submit_egg_drop_superball_actuators.py
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
This is a THIRD follow-up literature query for the egg-drop tensegrity
demonstration project. Prior Edison tasks on this thread have already
covered topology, fracture mechanics, instrumentation, and a drag-free
V/m-constrained benchmark — please do NOT re-derive that material. Focus
exclusively on the SUPERball v2 actuator question and its tech-transfer
implications below.

CONTEXT FROM PRIOR EDISON FINDING (Vespignani et al. 2018):
   "A 2-meter diameter, 36 kg, fully actuated six-bar tensegrity robot
    with 24 actuators and compliant nylon cables (up to 15% stretch).
    Designed to survive impact velocities upward of 8 m/s, with
    simulations analyzing up to 15 m/s impacts. Cable stiffness
    ~4000 N/m produced lowest peak cable forces (~950 N)."

OUR CURRENT STUDY (the work we are positioning against this prior art):
   - Six-bar tensegrity unit cell, ~10–20× smaller than SUPERball v2
     (bounding sphere O(0.2 m) rather than 2 m).
   - Multi-material FFF print on a Bambu H2D: PETG struts +
     TPU 85A tendons (NinjaFlex-class, E ~12 MPa secant).
   - **Passive** structure: no motors, no on-board electronics, no
     active cable retraction. Tendons are pre-tensioned only by the
     printed geometry / assembly preload, not by actuators.
   - Many tendon-to-strut connections are presently treated as
     "largely untensioned" in modeling and as printed
     mechanical-interlock joints in hardware (see prior joint-design
     work in this repo: dovetail B + anchor-bulb A primary).
   - Intended demo is a drag-free egg drop onto a rigid floor (per
     the previous Edison follow-up benchmark, task f41b7034).

QUESTIONS TO ANSWER (cite peer-reviewed sources, give numbers with units):

1. **What are SUPERball v2's actuators? Explain simply.**
   Plain-English description of the 24 actuators in SUPERball v2:
     - Type (DC brushless motor + spool? linear screw? series-elastic?
       cable-driven reel?), make/model if Vespignani 2018 names one,
       and where on the robot they are mounted (inside the rigid
       struts? at the nodes? off-board?).
     - What each actuator physically does at a stroke level: does it
       reel cable in/out, change resting length, apply a torque, or
       something else? What is the stroke range / max force / max
       speed reported?
     - Why 24 (= 4 × 6 struts, or = number of actuated cables, or
       = 24 of the 30 cables, etc.) — i.e., the cable-actuation
       topology choice.
     - Role during landing vs role during locomotion: are the
       actuators *passive compliant* (acting like springs / dampers)
       at impact, or are they *active* (commanded to back-drive,
       reel out, or shed energy) during the touchdown event itself?
       Cite the Vespignani 2018 / Agogino 2018 / SunSpiral / Caluwaerts
       publications that document this.

2. **How does this relate to our passive PETG+TPU tensegrity?**
   Concrete contrast table or paragraph covering:
     - Cable / tendon material and stiffness: SUPERball v2 nylon
       (15% stretch, k ≈ 4000 N/m, peak force ~950 N at landing) vs
       our printed TPU 85A tendons (E ≈ 12 MPa, derive an order-of-
       magnitude k for a representative L = 100 mm × Ø 3 mm tendon
       and compare).
     - Pre-tension: SUPERball v2 actively servoed pretension from the
       motors vs our passive print-set / preload-only pretension.
     - Length adaptivity: SUPERball v2 can change cable resting length
       in flight / on impact vs ours which cannot.
     - Energy-dissipation pathway: where does kinetic energy go in
       each system at touchdown (motor back-EMF / friction / cable
       hysteresis / strut-floor contact / TPU hysteresis)?

3. **How does the lack of actuators limit the usefulness of our study?**
   Honest list of tech-transfer concerns to a SUPERball-v2-style
   actuated lander:
     - Cable preload uncertainty (passive print-set vs servoed setpoint)
       and how that propagates into peak-g and h_crit predictions.
     - Inability to reproduce Vespignani's "cable stiffness ~4000 N/m
       gives lowest peak cable force" finding without actuators (since
       our k is fixed by geometry and TPU choice, we cannot sweep k
       on the same hardware).
     - Inability to test active-landing strategies (variable-impedance
       control, motor back-driving as damper, payload-mass-aware
       pre-tension scheduling).
     - Scaling: Does anything go wrong physically when scaling a
       passive 6-bar tensegrity from 2 m / 36 kg down to 0.2 m /
       O(0.5 kg)? (Strain rate at impact is ~10× higher for the same
       drop height; TPU dynamic modulus increases with strain rate;
       tendon mass fraction shifts; strut Euler buckling load changes
       with L^-2.)
     - Reusability: SUPERball v2 explicitly tests N>1 landings — how
       many landings did our prior-art tensegrity references survive,
       and what failure modes appeared first (cable yield, cable creep,
       strut buckling, joint pull-out)?

4. **How could/should the passive design be adjusted to be more
   amenable to future actuated tensegrity work?**
   Specific, actionable design changes the project should make
   *now* so that the passive PETG+TPU drop demo cleanly extrapolates
   to an actuated SUPERball-v2-class lander later. Examples to evaluate:
     - Replace one or more printed TPU tendons with a removable
       bowden / nylon cable routed through a printed eyelet, so that
       a future revision can add a motorized spool at the strut end.
     - Print struts as **hollow** with an internal cavity and an
       end-cap interface sized for an off-the-shelf brushless motor +
       gearhead (e.g., a typical SUPERball-class motor envelope).
     - Standardize anchor geometry so a single anchor accepts either
       a printed TPU tendon (passive) OR a swaged steel/nylon cable
       termination (active), so the hardware can be retrofitted
       without re-printing the whole cell.
     - Add one or two "instrumented" tendons that include an inline
       load cell (or a printed strain-gauge channel) so that one-off
       cable-force traces can be captured without redesigning the
       cell.
     - Choose a strut diameter and node geometry that *already*
       satisfy the class-1 condition (strut Ø < closest-approach
       distance) at the larger SUPERball v2 scale, so the same
       topology survives a scale-up without rework.
     - Pre-instrument the payload cradle so an ADXL375 + ESP32 +
       DAQ can move from passive demo to actuated future revision
       unchanged.
   For each suggestion, state what concrete tech-transfer concern it
   alleviates and whether it imposes any cost (mass, printability,
   complexity) on the immediate passive demo.

5. **One-off validations to alleviate the tech-transfer concern.**
   Recommend a small set (3–6) of single-shot or low-replicate
   experiments that can be performed *on the passive PETG+TPU article*
   to directly de-risk the eventual jump to an actuated SUPERball-v2-
   class system. Each validation should:
     - Be doable with the already-recommended instrumentation
       (ADXL375 + ESP32 @ 3.2 kHz, ≥5000 fps high-speed video,
       photogate-TTL sync, optional inline tendon load cell).
     - Produce a number that can be directly compared against a
       Vespignani / Caluwaerts / Agogino / Zhang published number
       (peak cable force, peak payload g, energy ratio, recovery
       time, residual strain after N drops).
     - Be feasible at ~0.2 m scale with O(0.5 kg) mass.
   Concrete candidates to evaluate (and add others as appropriate):
     (a) **Single-tendon force trace** — instrument one tendon with
         an inline miniature load cell and measure peak cable force
         at h = 1, 2, 3 m drops. Compare per-tendon force normalized
         by (m·g·sqrt(2h/g)) to the Vespignani ~950 N at 8 m/s.
     (b) **Cable-stiffness sensitivity sweep** — print 3 specimens
         with TPU tendon Ø ∈ {1.5, 2.5, 4.0} mm (so k spans a
         decade) and check whether peak g vs k follows the
         Vespignani-style optimum, at the smaller scale.
     (c) **Pre-tension sensitivity** — assemble the same cell at
         3 different print-set pretensions (slack, nominal, taut)
         and measure peak g, residual strain, and cable hysteresis.
     (d) **N-drop reusability test** — drop the same specimen N=20
         times at h = 3 m and report cumulative residual strain and
         the drop number at first failure (mirrors Pajunen 2019
         protocol, cited in prior follow-up).
     (e) **Worst-case orientation** — test vertex-down, face-down,
         and edge-down landings to compare orientation-sensitivity
         envelope against the Zhang 2022 22″ tensegrity numbers.
     (f) **Quasi-static vs impact stiffness gap** — measure
         quasi-static k of one tendon on an Instron-class machine
         and compare to the apparent dynamic k inferred from the
         drop, to bound the rate-dependence of TPU 85A.
   Indicate which one or two of these are the *highest-leverage*
   single experiments for tech-transfer credibility.

6. **Bottom-line recommendation.**
   In one short paragraph, recommend whether the passive PETG+TPU
   tensegrity drop demo should explicitly position itself as
   "passive scale-model precursor to SUPERball-v2-class actuated
   landers" (with the design changes above) or as a standalone
   passive impact-absorber benchmark (and citing SUPERball v2 only
   as the canonical actuated reference). State the recommended
   *minimum viable* design changes (from question 4) and the
   *minimum viable* one-off validations (from question 5) needed
   to support that positioning in a future ASME JMD or RA-L
   submission.

Please cite specific peer-reviewed papers, conference proceedings,
NASA technical reports, and product datasheets where applicable.
""".strip()


def main() -> None:
    client = EdisonClient()
    task = {"name": JobNames.LITERATURE_HIGH, "query": QUERY}

    submission_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    print(f"[{submission_ts}] Submitting Edison LITERATURE_HIGH egg-drop "
          "SUPERball v2 actuator query (passive vs actuated tech transfer)...")

    responses = client.run_tasks_until_done(task)
    response = responses[0]

    task_id = getattr(response, "task_id", None) or getattr(response, "id", "unknown")
    short_id = str(task_id).split("-")[0]

    md_path = OUT_DIR / f"egg-drop-superball-actuators-{short_id}.md"
    json_path = OUT_DIR / f"egg-drop-superball-actuators-{short_id}.json"

    md_path.write_text(response.formatted_answer, encoding="utf-8")
    json_path.write_text(response.model_dump_json(indent=2), encoding="utf-8")

    print(f"  task_id        = {task_id}")
    print(f"  formatted_answer -> {md_path.relative_to(REPO_ROOT)}")
    print(f"  full payload     -> {json_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
