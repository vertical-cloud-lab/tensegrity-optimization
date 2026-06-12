#!/usr/bin/env python3
"""Submit the current manuscript draft to Edison ANALYSIS for a SECOND round of
mock JMD peer review.

Per PR comment 4686431615 (@sgbaird: "send to Edison analysis for another round
of mock reviewer feedback and report back the results in your comment reply.
Commit all Edison artifacts"), this bundles the current populated manuscript
(PDF + all three .tex wrappers + manuscript-body.tex + references.bib +
manuscript/README.md) into a single zipped collection (required for ANALYSIS
uploads) and asks the same three-reviewer + Associate-Editor panel used in the
first round (task 6c140449) to re-review the revised draft.

The prompt summarizes what changed since round 1 so the panel can focus on the
current state rather than re-flagging already-fixed blockers.

Non-blocking: the task id is written to ``mock-jmd-review-2-SUBMITTED.json`` for
a later fetch via ``client.get_task(task_id)`` (see fetch_mock_jmd_review2.py).

Run::

    python scripts/edison/submit_mock_jmd_review2.py
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

from edison_client import EdisonClient, JobNames  # noqa: E402
from edison_client.models import TaskRequest  # noqa: E402

MANU = HERE / "manuscript"
TRAJ = HERE / "edison-trajectories" / "mock-jmd-review-2"
BUNDLE_DIR = TRAJ / "bundle"
BUNDLE = TRAJ / "mock-jmd-review-2-bundle.zip"
SUBMITTED = TRAJ / "mock-jmd-review-2-SUBMITTED.json"

# Files copied into the bundle (the manuscript draft and its sources).
BUNDLE_SRC = [
    MANU / "manuscript.pdf",
    MANU / "manuscript-todos.pdf",
    MANU / "manuscript-body.tex",
    MANU / "manuscript.tex",
    MANU / "manuscript-todos.tex",
    MANU / "references.bib",
    MANU / "README.md",
]

QUERY = """\
SECOND-ROUND mock peer review for an ASME Journal of Mechanical Design (JMD)
Research Paper submission. You reviewed an earlier draft of this same manuscript
in a prior round; this is the revised draft. The attached files are the current
populated draft (manuscript.pdf is the clean reader PDF; manuscript-todos.pdf is
the review PDF that additionally shows margin \\todo{} annotations and a
\\listoftodos; sources are manuscript-body.tex / manuscript.tex /
manuscript-todos.tex and references.bib; manuscript/README.md documents venue
choice and build).

The paper is a multi-material 3D-printed tensegrity-inspired energy-absorbing
crutch-tip study using experiment-driven Bayesian optimization (BO). Rigid PLA
struts in compression + soft TPU cables in tension, printed on a Bambu Lab H2D
dual-nozzle printer, characterized under quasi-static compression and
drop-weight impact. Quantitative Results/Discussion are INTENTIONALLY still
\\todo{} placeholders -- the project is at the planned-methods phase. Please
review structure, framing, scope, novelty claims, methods rigor, literature
coverage, internal consistency, and venue fit (ASME JMD vs. backup Smart
Materials and Structures / Additive Manufacturing), NOT raw numerical values.

What CHANGED since the first round (so you can focus on the current state rather
than re-flagging already-addressed items):
  * The (author?) citation rendering artifacts were fixed; the blank third
    Contributions bullet is filled.
  * PLA+TPU is the INTENTIONAL, correct material pair for this study (the earlier
    PETG mention was an inconsistency; a separate PLA->PETG question is tracked
    elsewhere and is out of scope here). Treat PLA/TPU as the design choice.
  * The TPU joint mechanism is now described correctly: TPU tension elements are
    anchored INSIDE the ends of each PLA strut (the strut acting as a rigid cage
    with discrete cable outlets), NOT wrapped around the strut exterior.
  * Methods were refreshed with concrete planned-methods detail: D3-symmetric
    parameterization (12 diameter axes collapse to 4 orbit axes), categorical
    cable diameter set, Ax/BoTorch SAASBO + qNEHVI with TuRBO escalation, ISO/
    ASTM test standards, the bungee-assisted drop tower with hold-down
    mitigations, and an n=9 Sobol initialization batch.
  * Figures: Fig 2 (CAD + as-printed T3 prism), Fig 3 (fabrication/test
    workflow with real photos), and illustrative example data figures (a
    mechanistic drop-curve figure and four Ax surrogate-diagnostic figures: LOO
    cross-validation, parameter sensitivity, convergence, Pareto front) are now
    populated. The example data figures are honestly captioned "Illustrative
    example (synthetic data)" and watermarked because real experimental data is
    not yet collected.
  * Pretensioning is now described ONLY as a future scale-up validation step on
    the final Pareto-optimal designs (Contributions item 3); the
    primary BO loop and Fig 2 prototype do NOT use pretensioned cables.

Produce FOUR artifacts, in the same style as a JMD decision-letter package:

1. Mock Reviewer #1 -- Design / Mechanical Engineering (typical ASME JMD
   reviewer). Strict on novelty vs. prior tensegrity/lattice/spring-loaded-tip
   work, on the BO formulation (kernel, acquisition, categorical handling,
   single- vs. multi-fidelity framing, budget/scaling), on parameterization
   completeness, and on JMD scope fit. Major / Minor / Editorial; recommend
   Accept / Minor / Major / Reject / Reject-and-Resubmit.

2. Mock Reviewer #2 -- Biomechanics / Rehabilitation engineering. Strict on the
   crutch-tip clinical motivation, biomechanical relevance of the axial
   drop-tower fixture vs. real off-axis/cyclic crutch loading, transferability,
   IRB considerations, and clinical-metric mapping (SEA -> peak transmitted
   force at the wrist/shoulder). Recommendation.

3. Mock Reviewer #3 -- Additive manufacturing / materials. Strict on the
   PLA+TPU multi-material FFF processing claims, the internal-anchor joint vs.
   alternatives, interface durability/fatigue, FFF repeatability and resolution
   limits for the categorical cable-diameter set, process-parameter disclosure,
   and FFF vs. SLA/DLP/SLS/MJF justification. Recommendation.

4. Mock Editor (JMD Associate Editor) decision letter synthesizing the three
   reviews: single-paragraph summary, decision, and an itemized,
   priority-ordered list of revisions required before resubmission. Explicitly
   assess venue fit (JMD Research Paper vs. Design Innovation vs. Tech Brief vs.
   redirect to SMS / J. Mech. Behav. Biomed. Mater. / Additive Manufacturing)
   and explicitly state whether the revisions since round 1 have moved the
   manuscript closer to acceptance.

End with a short "Reviewers' bibliographic gaps" section listing specific
peer-reviewed references the authors are likely still missing, by topic, given
references.bib.

Be honest, specific, and grounded in the attached files. It is acceptable (and
expected) to note that the placeholder \\todo{}s and the absence of experimental
results gate the final decision. Where round-1 concerns have been resolved, say
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
        name="mock-jmd-review-2-bundle",
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
        "slug": "mock-jmd-review-2",
        "task_id": str(task_id),
        "job": str(JobNames.ANALYSIS),
        "uploaded_collection": uri,
        "query": QUERY,
        "note": "non-blocking; fetch via scripts/edison/fetch_mock_jmd_review2.py",
    }, indent=2))
    print(f"wrote {SUBMITTED}")


if __name__ == "__main__":
    main()
