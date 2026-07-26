"""Submit the IDETC slide deck Draft 1 (extracted content + notes) to Edison
Scientific for simulated mock-audience feedback — a mock Program/Project
Manager persona plus six audience personas — then save the task id.

Run from the repo root. Requires EDISON_PLATFORM_API_KEY in the environment.
Waiting/fetching is done by wait_fetch_slide_review.py (single blocking call).
"""

import os
from pathlib import Path

from edison_client import EdisonClient, JobNames
from edison_client.models import RuntimeConfig, TaskRequest

REPO = Path(__file__).resolve().parents[2]
OUTDIR = REPO / "presentation" / "edison-mock-audience"
OUTDIR.mkdir(parents=True, exist_ok=True)

FILES = [
    str(OUTDIR / "slide-deck-draft1-extracted.md"),
    str(REPO / "presentation" / "doumont-presentation-template.md"),
    str(REPO / "presentation" / "doumont-video-notes.md"),
    str(REPO / "idetc-abstract.tex"),
]

QUERY = """\
You are simulating a mock conference audience for a ~15-minute technical talk at
IDETC-CIE 2026 (ASME International Design Engineering Technical Conferences),
Design Automation Conference track (DAC-10: design optimization applications).

This time the artifact under review is an ACTUAL SLIDE DECK (Draft 1), not just
an outline. Attached files:
1. slide-deck-draft1-extracted.md — a faithful slide-by-slide extraction of the
   PowerPoint: layout used, whether the slide is currently HIDDEN, all on-slide
   text (slide titles are full-sentence messages per Doumont), an inventory of
   non-text shapes/media/placeholders, and the presenter's own notes (which
   include the presenter's candid comments about intended changes and open
   questions — treat those as the presenter's current thinking). Many visuals
   are placeholders the presenter plans to fill; judge the plan, not the
   missing pixels, but DO flag placeholder choices you think are wrong.
2. doumont-presentation-template.md — the Draft 3 outline the deck is built
   from (the agreed story arc, scope/proxy framing, results plan, timing plan).
   Use it to spot where the deck diverges from the plan.
3. doumont-video-notes.md — the presenter's notes on Jean-luc Doumont's
   presentation principles (messages not words, adapt to audience, one message
   per slide, signal-to-noise). Part of the evaluation rubric.
4. idetc-abstract.tex — the submitted conference abstract, for technical
   grounding (closed-loop Bayesian optimization of multi-material 3D-printed
   tensegrity-inspired energy absorbers, optimized directly from physical
   impact tests; qNEHVI; objectives = specific energy absorption and
   compaction efficiency subject to a peak transmitted-force cap).

Context: the presenter is an undergraduate researcher; the PI is the project
lead. Four slides are currently HIDDEN (3, 5, 6, 11); hiding slide 6 removes
the "specimen information value / experiment as source of truth" argument and
slide 11 is the reserved results slot.

Simulate SEVEN personas. NEW this round, and to be treated as first among
equals:

P0. "The program manager in the audience" — a mock PM/project manager (think:
    research program manager at a national lab or aerospace prime who funds
    projects like this one; also plays the internal-stakeholder role of the
    project's own PM sitting in the audience). Moderate technical literacy in
    all three base techniques, expert in schedule/scope/risk. Watches for:
    Does the talk state scope honestly (proxy system vs. flight hardware)?
    Is there a credible plan for the empty results slot given the conference
    date? Are claims traceable to evidence? What is the risk register for this
    talk (what could go wrong on stage: missing results, video failures,
    overtime)? Would they fund the next phase after seeing it? Their feedback
    should include a concrete slide-level punch list ordered by
    schedule-criticality (what MUST be fixed before the talk vs. nice-to-have).

P1. "The skeptical BO insider" — design-automation professor, 15 years in
    surrogate-based and Bayesian optimization; reviews for DAC. HIGHLY
    SKEPTICAL: default assumption is "off-the-shelf qNEHVI applied to yet
    another application." Probes methodological novelty, budget, baselines,
    noise handling — and now also whether the deck's BO slides (5 hidden, 7
    visible) say anything an expert respects.
P2. "The aerospace practitioner" — senior EDL engineer; deep in impact
    attenuation and lander hardware; no BO/ML background; knows tensegrity
    from the Super Ball Bot era. MODERATELY SKEPTICAL, practicality-focused.
P3. "The AM/materials researcher" — multi-material FDM and elastomer printing
    expert; novice in BO and tensegrity. NEUTRAL/CURIOUS; probes PLA-TPU
    bonding, repeatability, and whether "single-build co-fabrication" holds.
P4. "The first-year grad student" — new to all three techniques. ENTHUSIASTIC.
    Tests followability slide by slide: where does the deck lose a novice,
    which jargon lands unexplained, do the hidden slides' absence break the
    story?
P5. "The FEA veteran" — 25 years of finite-element work. DEFENSIVE AND
    SKEPTICAL of any simulation-dismissal; checks whether the deck (with slide
    6 hidden) still makes a defensible case for experiment-first.
P6. "The friendly industry generalist" — design engineer scouting methods.
    SUPPORTIVE, limited attention; tests memorability and the practical
    so-what.

For EACH persona produce:
(a) a first-person reaction to sitting through the deck as it stands (visible
    slides in order, placeholders imagined as the presenter's notes describe
    them): what landed, what confused, where attention drifted;
(b) the main message as they would repeat it to a colleague the next day, in
    their own words — noting distortion from the intended message ("By closing
    the loop between multi-material 3D printing and Bayesian optimization, we
    can optimize tensegrity energy absorbers directly from real impact data —
    in dozens of prints, not hundreds");
(c) their top 3 Q&A questions, in character;
(d) their single most pointed objection, and how damaging it is unanswered;
(e) NEW: their verdict on the slide deck specifically (vs. the outline):
    which single slide most needs work, and which hidden slide (3, 5, 6, 11)
    they would unhide or keep hidden, and why.

Then produce a SYNTHESIS section:
- cross-persona themes;
- the 5 highest-priority slide-level revisions, concretely worded (slide
  number + exact change);
- a hidden-slide adjudication: for each of slides 3, 5, 6, 11, the panel's
  recommendation (unhide / merge into another slide / keep as backup) with
  one-line rationale;
- claims on visible slides needing evidence, hedging, or a prepared backup
  slide for Q&A;
- the PM's punch list reconciled with the technical personas' asks: one merged,
  ordered TODO list for the presenter (must-fix before talk / should-fix /
  polish);
- which persona the deck currently serves best and worst, and whether that is
  the right trade-off for DAC-10;
- predicted overall reception on a 1-10 scale, as-is vs. after must-fixes,
  with one-sentence rationale each.

Write the whole result as a well-structured markdown report.
"""


def main() -> None:
    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ["EDISON_API_KEY"]
    client = EdisonClient(api_key=api_key)

    # Official upload flow per
    # https://docs.edisonscientific.com/edison-client/file-management#upload
    storage_uris = []
    for path in FILES:
        resp = client.store_file_content(
            name=Path(path).name,
            file_path=path,
            description="Input document for IDETC slide-deck mock-audience review",
        )
        storage_uris.append(f"data_entry:{resp.data_storage.id}")
        print(f"uploaded {Path(path).name} -> {resp.data_storage.id}", flush=True)

    task_data = TaskRequest(
        name=JobNames.ANALYSIS,
        query=QUERY,
        runtime_config=RuntimeConfig(
            environment_config={"data_storage_uris": storage_uris},
        ),
    )
    task_ids = client.create_task(task_data)
    task_id = task_ids[0] if isinstance(task_ids, (list, tuple)) else task_ids
    (OUTDIR / "slide-review-task-id.txt").write_text(str(task_id) + "\n")
    print(f"submitted task {task_id}", flush=True)


if __name__ == "__main__":
    main()
