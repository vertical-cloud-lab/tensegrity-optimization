"""Submit the IDETC presentation outline to Edison Scientific (analysis job)
for simulated mock-audience feedback, poll until done, and save all artifacts.

Run from the repo root. Requires EDISON_API_KEY in the environment.
"""

import json
import os
import sys
import time
from pathlib import Path

from edison_client import EdisonClient, JobNames
from edison_client.models import TaskRequest

REPO = Path(__file__).resolve().parents[1]
OUTDIR = REPO / "presentation" / "edison-mock-audience"
OUTDIR.mkdir(parents=True, exist_ok=True)

FILES = [
    str(REPO / "presentation" / "doumont-presentation-template.md"),
    str(REPO / "presentation" / "doumont-video-notes.md"),
    str(REPO / "idetc-abstract.tex"),
]

QUERY = """\
You are simulating a mock conference audience for a ~15-minute technical talk at
IDETC-CIE 2026 (ASME International Design Engineering Technical Conferences),
Design Automation Conference track (DAC-10: design optimization applications).

Attached files:
1. doumont-presentation-template.md — the presentation outline to evaluate,
   structured per Jean-luc Doumont's opening/body/closing template. This is the
   artifact under review. Evaluate the talk a competent presenter would deliver
   from this outline (slides not yet made; an "Evidence/results" slot is a
   placeholder while the experimental campaign is in progress).
2. idetc-abstract.tex — the submitted conference abstract, for technical
   grounding of the project's claims (closed-loop Bayesian optimization of
   multi-material 3D-printed tensegrity-inspired energy absorbers, optimized
   directly from physical impact tests; qNEHVI; objectives = specific energy
   absorption and compaction efficiency subject to a peak transmitted-force cap).
3. doumont-video-notes.md — the presenter's notes on Doumont's presentation
   principles (messages not words, adapt to audience, one message per slide,
   signal-to-noise). Use these as part of the evaluation rubric.

Simulate the following SIX audience personas, chosen to span familiarity with
the base techniques (Bayesian optimization, tensegrity structures, additive
manufacturing), professional background, and level of skepticism:

P1. "The skeptical BO insider" — design-automation professor, 15 years in
    surrogate-based and Bayesian optimization; reviews for DAC. Expert in BO,
    moderate on AM, low on tensegrity. HIGHLY SKEPTICAL of applied-BO talks:
    default assumption is "off-the-shelf qNEHVI applied to yet another
    application." Will probe methodological novelty, experiment budget,
    baselines, and noise handling.
P2. "The aerospace practitioner" — senior EDL (entry, descent, landing)
    engineer from industry. Deep expertise in impact attenuation and lander
    hardware; NO familiarity with BO or ML jargon; knows tensegrity from the
    Super Ball Bot era. MODERATELY SKEPTICAL, practicality-focused: velocity
    regimes, scaling from desktop specimens to flight hardware, TRL,
    qualification.
P3. "The AM/materials researcher" — mid-career researcher in multi-material
    FDM and elastomer printing. Expert in AM/TPU, novice in BO and tensegrity.
    NEUTRAL/CURIOUS but will probe PLA-TPU interfacial bonding, print
    repeatability, batch-to-batch variation, and whether "no assembly" holds.
P4. "The first-year grad student" — new to ALL three base techniques.
    ENTHUSIASTIC, low skepticism. Tests followability: where does the talk lose
    a novice, which jargon lands unexplained, does the story arc carry them?
P5. "The FEA veteran" — computational structural mechanics researcher, 25
    years of finite-element work, expert in simulation, low familiarity with
    BO. DEFENSIVE AND SKEPTICAL of the claim "simulation can't be trusted for
    these structures": will push back that models can be calibrated, and ask
    why the authors didn't try harder before abandoning simulation.
P6. "The friendly industry generalist" — design engineer attending to scout
    useful methods. Moderate familiarity with optimization and AM, none with
    tensegrity. SUPPORTIVE, low skepticism, limited attention: tests
    memorability and the practical so-what ("could my team use this Monday?").

For EACH persona produce:
(a) a first-person reaction to the talk as outlined: what landed, what confused
    or lost them, where their attention drifted;
(b) the main message as they would repeat it to a colleague the next day, in
    their own words — noting any distortion from the intended message ("By
    closing the loop between multi-material 3D printing and Bayesian
    optimization, we can optimize tensegrity energy absorbers directly from
    real impact data — in dozens of prints, not thousands");
(c) their top 3 Q&A questions, in character;
(d) their single most pointed objection or challenge, and how damaging it is if
    the presenter has no good answer.

Then produce a SYNTHESIS section:
- cross-persona themes (what multiple personas stumbled on or attacked);
- the 3 highest-priority revisions to the outline, concretely worded;
- claims in the outline that need evidence, hedging, or a prepared backup slide
  for Q&A;
- which persona the current outline serves best and worst, and whether that is
  the right trade-off for the DAC-10 audience;
- predicted overall reception on a 1-10 scale with one-sentence rationale.

Write the whole result as a well-structured markdown report.
"""


def main() -> None:
    client = EdisonClient(api_key=os.environ["EDISON_API_KEY"])

    task_data = TaskRequest(name=JobNames.ANALYSIS, query=QUERY)
    task_ids = client.create_task(task_data, files=FILES)
    task_id = task_ids[0] if isinstance(task_ids, (list, tuple)) else task_ids
    task_id = str(task_id)
    (OUTDIR / "task-id.txt").write_text(task_id + "\n")
    print(f"submitted task {task_id}", flush=True)

    time.sleep(600)  # initial wait per repo guidance
    deadline = time.time() + 45 * 60
    while True:
        try:
            status = str(client.get_task(task_id).status).lower()
        except Exception as exc:  # transient API hiccups shouldn't kill the poll
            print(f"poll error: {exc}", flush=True)
            status = "unknown"
        print(f"status: {status}", flush=True)
        if any(s in status for s in ("success", "fail", "cancel", "error")):
            break
        if time.time() > deadline:
            print("timed out waiting for task", flush=True)
            break
        time.sleep(300)

    verbose = client.get_task(task_id, verbose=True, history=True)
    payload = verbose.model_dump(mode="json")
    (OUTDIR / "task-response.json").write_text(json.dumps(payload, indent=2, default=str))

    # Pull out the human-readable answer wherever the frame put it.
    answer = None
    frame = payload.get("environment_frame") or {}

    def hunt(node):
        found = []
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("answer", "formatted_answer", "final_answer") and isinstance(v, str) and len(v) > 200:
                    found.append(v)
                found.extend(hunt(v))
        elif isinstance(node, list):
            for v in node:
                found.extend(hunt(v))
        return found

    candidates = hunt(frame) + hunt({k: v for k, v in payload.items() if k != "environment_frame"})
    if candidates:
        answer = max(candidates, key=len)
        (OUTDIR / "mock-audience-feedback.md").write_text(answer)
        print("answer saved", flush=True)
    else:
        print("no answer field found; inspect task-response.json", flush=True)

    # Fetch any trajectory artifacts.
    try:
        files = client.list_files(task_id)
        (OUTDIR / "trajectory-files.json").write_text(json.dumps(files, indent=2, default=str))
        print(f"trajectory files listed: {files}", flush=True)
    except Exception as exc:
        print(f"list_files failed: {exc}", flush=True)

    print("done", flush=True)


if __name__ == "__main__":
    main()
