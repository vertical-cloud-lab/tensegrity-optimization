#!/usr/bin/env python3
"""Submit the revised manuscript to Edison ANALYSIS for a THIRD round of mock
JMD peer review.

Per PR comment 4693797511 (@sgbaird: "When done, upload to edison analysis for
another round of mock reviewer & editor feedback, fetch, then report back"),
this bundles the current manuscript (clean PDF + review PDF + SI PDF + sources +
references.bib) into a single zipped collection (required for ANALYSIS uploads)
and asks the same three-reviewer + Associate-Editor panel used in rounds 1 and 2
to re-review the revised draft.

The prompt summarizes what changed since round 2 so the panel can focus on the
current state rather than re-flagging already-addressed items.

Non-blocking: the task id is written to ``mock-jmd-review-3-SUBMITTED.json`` for
a later fetch via ``client.get_task(task_id)`` (see fetch_mock_jmd_review3.py).

Run::

    python scripts/edison/submit_mock_jmd_review3.py
"""
from __future__ import annotations

import json
import os
import shutil
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

from edison_client import EdisonClient, JobNames, TaskRequest  # noqa: E402

MANU = HERE / "manuscript"
TRAJ = HERE / "edison-trajectories" / "mock-jmd-review-3"
BUNDLE_DIR = TRAJ / "bundle"
BUNDLE = TRAJ / "mock-jmd-review-3-bundle.zip"
SUBMITTED = TRAJ / "mock-jmd-review-3-SUBMITTED.json"

# Files copied into the bundle (the manuscript draft and its sources + SI).
BUNDLE_SRC = [
    MANU / "manuscript.pdf",
    MANU / "manuscript-todos.pdf",
    MANU / "supplementary.pdf",
    MANU / "manuscript-body.tex",
    MANU / "manuscript.tex",
    MANU / "manuscript-todos.tex",
    MANU / "supplementary.tex",
    MANU / "references.bib",
    MANU / "README.md",
]

QUERY = """\
THIRD-ROUND mock peer review for an ASME Journal of Mechanical Design (JMD)
Research Paper submission. You reviewed earlier drafts of this same manuscript
in two prior rounds (round 1 = Reject-and-Resubmit, round 2 = Major Revision);
this is the further-revised draft. The attached files are the current populated
draft (manuscript.pdf is the clean reader PDF; manuscript-todos.pdf is the
review PDF that additionally shows margin \\todo{} annotations and a
\\listoftodos; supplementary.pdf is the Supplementary Information; sources are
manuscript-body.tex / manuscript.tex / manuscript-todos.tex / supplementary.tex
and references.bib; manuscript/README.md documents venue choice and build).

The paper is a multi-material 3D-printed (FDM) tensegrity-inspired
energy-absorbing structure study using experiment-driven Bayesian optimization
(BO). Rigid PLA struts in compression + soft TPU cables in tension, printed on a
Bambu Lab H2D dual-nozzle FDM printer, characterized under quasi-static
compression and drop-weight impact. The motivating application is framed up
front as a planetary-lander / payload energy absorber; a crutch-tip is mentioned
only as future work in the Discussion. Quantitative Results/Discussion are
INTENTIONALLY still \\todo{} placeholders -- the project is at the
planned-methods phase. Please review structure, framing, scope, novelty claims,
methods rigor, literature coverage, internal consistency, and venue fit (ASME
JMD vs. backup Smart Materials and Structures / Additive Manufacturing), NOT raw
numerical values.

What CHANGED since round 2 (so you can focus on the current state rather than
re-flagging already-addressed items). These edits respond directly to the
round-2 Associate-Editor letter:
  * SCOPE: the title/abstract/intro now consistently frame a planetary-lander /
    payload energy absorber as the motivating use case; the crutch-tip appears
    ONLY as a future-work item in the Discussion (no longer mixed into the
    front matter). The abstract omits the crutch-tip motivation.
  * PARAMETERIZATION CONSISTENCY: the earlier "12 diameter axes collapse to 4
    orbit axes (1 strut + 3 cable)" claim was REMOVED. The authoritative BO
    search space (from the T3-prism BO implementation) is FIVE continuous
    variables -- circumradius R [25,40] mm, height H [60,110] mm, twist [40,80]
    deg, a SINGLE strut diameter [6.0,12.0] mm, and a SINGLE cable/tendon
    diameter -- and Table 1 now matches this exactly (one d_s, one d_t).
  * TENDON DIAMETER: now CONTINUOUS over [3.0, 5.5] mm (the earlier categorical
    set {1.2,1.8,2.4,3.0,4.5} mm was an inconsistency and has been removed).
    There are therefore NO categorical variables in the T3-prism search space.
  * BO METHOD now specified for reproducibility: SAASBO (fully-Bayesian sparse
    axis-aligned GP) with a Matern-5/2 ARD kernel and model-inferred
    (homoskedastic) observation noise; standardized objective, normalized
    inputs; an n=9 Sobol initialization batch followed by T=10 sequential
    batches of q=5 prints (50 specimens total); fixed-seed policy; Zenodo DOI
    placeholder for the archived code/data. SAASBO is justified as giving better
    uncertainty quantification / predictive accuracy even at this modest
    (~5-variable) dimensionality.
  * NOVELTY: a dedicated comparison table now contrasts this work against
    Pajunen 2019, Intrigila 2022, and Mo 2023 across architecture, fabrication,
    optimization approach, and ground-truth/validation -- so the novelty claim
    is demonstrated, not merely asserted.
  * LANGUAGE: "ensure cyclic interface durability" has been softened to an
    intention to be verified by pull-out and fatigue testing; FFF has been
    standardized to FDM throughout.
  * METAL-ANALOG VALIDATION: a new Methods subsection plus SI section describe a
    planned validation campaign using hollow aluminum rods + stainless-steel
    threaded cables. Rather than only the top performers, a few predicted
    worst-, mediocre-, and best-performing designs will be built and compared
    against their PLA/TPU equivalents to test whether the rank ordering is
    preserved. Placeholder table + figure (with image callouts for the
    assembled/printed structures) represent this; these are honestly marked as
    placeholders because the structures do not yet exist.

Produce FOUR artifacts, in the same style as a JMD decision-letter package:

1. Mock Reviewer #1 -- Design / Mechanical Engineering (typical ASME JMD
   reviewer). Strict on novelty vs. prior tensegrity/lattice/spring-loaded work,
   on the BO formulation (kernel, acquisition, noise, batch/budget, SAASBO
   justification at ~5 variables), on parameterization completeness and Table-1
   consistency, and on JMD scope fit. Major / Minor / Editorial; recommend
   Accept / Minor / Major / Reject / Reject-and-Resubmit.

2. Mock Reviewer #2 -- Biomechanics / impact-mechanics. Strict on the
   energy-absorber motivation, relevance of the axial drop-tower fixture vs.
   real off-axis/cyclic loading, transferability, and metric mapping (SEA ->
   peak transmitted force). Recommendation.

3. Mock Reviewer #3 -- Additive manufacturing / materials. Strict on the
   PLA+TPU multi-material FDM processing claims, the internal-anchor joint vs.
   alternatives, interface durability/fatigue (now appropriately softened?),
   FDM repeatability and resolution limits for continuous-diameter members,
   process-parameter disclosure, and the metal-analog (Al/SS) validation plan.
   Recommendation.

4. Mock Editor (JMD Associate Editor) decision letter synthesizing the three
   reviews: single-paragraph summary, decision, and an itemized,
   priority-ordered list of revisions required before resubmission. Explicitly
   assess venue fit and explicitly state whether the round-3 revisions have
   moved the manuscript closer to acceptance relative to the round-2 Major
   Revision decision.

End with a short "Reviewers' bibliographic gaps" section listing specific
peer-reviewed references the authors are likely still missing, by topic, given
references.bib.

Be honest, specific, and grounded in the attached files. It is acceptable (and
expected) to note that the placeholder \\todo{}s and the absence of experimental
results gate the final decision. Where round-2 concerns have been resolved, say
so; where they persist or new ones appear, flag them.
"""


def _make_bundle() -> None:
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    BUNDLE_DIR.mkdir(parents=True)
    for src in BUNDLE_SRC:
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, BUNDLE_DIR / src.name)
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
        name="mock-jmd-review-3-bundle",
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
        "slug": "mock-jmd-review-3",
        "task_id": str(task_id),
        "job": str(JobNames.ANALYSIS),
        "uploaded_collection": uri,
        "query": QUERY,
        "note": "non-blocking; fetch via scripts/edison/fetch_mock_jmd_review3.py",
    }, indent=2))
    print(f"wrote {SUBMITTED}")


if __name__ == "__main__":
    main()
