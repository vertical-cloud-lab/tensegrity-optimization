#!/usr/bin/env python3
"""Submit the revised manuscript to Edison ANALYSIS for a FOURTH round of mock
JMD peer review.

Per PR comment 4699376594 (@sgbaird: "implement the feedback that you can. Send
back to Edison analysis with all relevant files uploaded, fetch artifacts and
report back."), this bundles the current manuscript (clean PDF + review PDF +
SI PDF + sources + references.bib) into a single zipped collection (required for
ANALYSIS uploads) and asks the same three-reviewer + Associate-Editor panel used
in rounds 1-3 to re-review the further-revised draft.

The prompt summarizes what changed since round 3 so the panel can focus on the
current state rather than re-flagging already-addressed items.

Non-blocking: the task id is written to ``mock-jmd-review-4-SUBMITTED.json`` for
a later fetch via ``client.get_task(task_id)`` (see fetch_mock_jmd_review4.py).

Run::

    python scripts/edison/submit_mock_jmd_review4.py
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
TRAJ = HERE / "edison-trajectories" / "mock-jmd-review-4"
BUNDLE_DIR = TRAJ / "bundle"
BUNDLE = TRAJ / "mock-jmd-review-4-bundle.zip"
SUBMITTED = TRAJ / "mock-jmd-review-4-SUBMITTED.json"

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
FOURTH-ROUND mock peer review for an ASME Journal of Mechanical Design (JMD)
Research Paper submission. You reviewed earlier drafts of this same manuscript
in three prior rounds (round 1 = Reject-and-Resubmit, round 2 = Major Revision,
round 3 = Major Revision but improving); this is the further-revised draft. The
attached files are the current populated draft (manuscript.pdf is the clean
reader PDF; manuscript-todos.pdf is the review PDF that additionally shows margin
\\todo{} annotations and a \\listoftodos; supplementary.pdf is the Supplementary
Information; sources are manuscript-body.tex / manuscript.tex /
manuscript-todos.tex / supplementary.tex and references.bib;
manuscript/README.md documents venue choice and build).

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

What CHANGED since round 3 (so you can focus on the current state rather than
re-flagging already-addressed items). These edits respond directly to the
round-3 Associate-Editor letter and reviewer comments:
  * CITATIONS NOW REAL (no longer TODO promises): the manuscript now cites the
    primary SAASBO paper (Eriksson & Jankowiak, UAI 2021) and the primary TuRBO
    paper (Eriksson et al., NeurIPS 2019); the canonical energy-absorber-metric
    references for SEA / densification displacement / compaction (energy-
    absorption) efficiency (Gibson & Ashby 1997; Avalle, Belingardi & Montanini
    2001; Tan et al. 2005; Michailidis et al. 2011); and the SAE J211/1 impact-
    instrumentation standard for the CFC-180 channel filtering. The matching
    "cite once added to bib" TODO notes were removed.
  * BO FORMULATION PRE-COMMITTED: the primary reported campaign is now stated
    explicitly as a CONSTRAINED MULTI-OBJECTIVE problem -- maximize SEA and
    compaction efficiency subject to an upper bound on peak transmitted force
    F_max <= F*, with F* fixed from the rigid-control drop response. The
    acquisition function is qNEHVI; the hypervolume reference point is anchored
    at the rigid-control (SEA, eta_c) pair. A single-objective LogEI run on SEA
    (same force constraint) is retained ONLY as a baseline. The input-noise-
    robust and evolution-guided constrained variants are now explicitly demoted
    to a contingency (adopted only if between-print variability dominates), not
    part of the default loop -- addressing the "toolkit inventory" concern.
  * SAASBO JUSTIFICATION made empirical: the campaign now benchmarks SAASBO
    against a standard single-task GP baseline with the same Matern-5/2 ARD
    kernel (retrospective leave-one-out calibration / predictive accuracy),
    rather than only asserting better UQ.
  * BUDGET CONSISTENCY: the specimen budget reads unambiguously as n=9 Sobol
    initialization + T=10 sequential batches of q=5 = 59 specimens total.
  * SCOPE DISCIPLINE: the Introduction now states explicitly that the study is
    scoped to single-cell, fixed-topology T3-prism specimens under AXIAL
    loading, and that off-axis / combined loading, multi-hit and cyclic
    durability, and landing-attitude variability are OUT OF SCOPE (future work);
    the novelty/generality claims are correspondingly scoped to this restricted
    prototype design space.
  * JOINT DIAMETER: the manuscript now explains WHY the joint diameter d_j is
    fixed at 7.0 mm (it sets the printed strut-end cage housing the internal
    cable anchors; constrained by tendon-outlet count and dual-nozzle clearance;
    fixing it keeps anchor geometry constant so the five optimized variables are
    not confounded by joint-strength changes); relaxing d_j is deferred to a
    follow-on joint-design study.
  * AS-BUILT RESOLUTION: a new paragraph acknowledges that although d_s and d_t
    are nominally continuous, the as-built cross-sections are discretized by
    nozzle diameter, line width, and support interaction, so the effective
    search granularity is coarser than the nominal continuous box; measured
    as-built diameters are reported and the dimensional spread is folded into
    the inferred observation noise.
  * METAL-ANALOG VALIDATION: the rank-preservation criterion is now fixed in
    advance as the Spearman rank-correlation coefficient rho_s between the two
    material systems' SEA orderings (peak transmitted force as a secondary
    ranking), and the test is framed as a STRINGENT, EXPLORATORY transfer test
    (deformation modes, joint compliance, friction, pretension, and strain-rate
    sensitivity all differ between PLA/TPU and Al/SS), not a presumed
    one-to-one validation.

STILL INTENTIONALLY OPEN (known gates, do not re-flag as new defects): the
quantitative Results and Discussion remain \\todo{} placeholders and several
BO/impact figures are illustrative synthetic examples; some fabrication/test
process parameters (Table 3 print settings, exact fixtures/DAQ) remain TBD
pending the campaign; the Zenodo archival DOI is a placeholder.

Produce FOUR artifacts, in the same style as a JMD decision-letter package:

1. Mock Reviewer #1 -- Design / Mechanical Engineering (typical ASME JMD
   reviewer). Strict on novelty vs. prior tensegrity/lattice/spring-loaded work,
   on the BO formulation (kernel, acquisition, noise, batch/budget, SAASBO
   justification at ~5 variables, constrained multi-objective formulation and
   reference point), on parameterization completeness and Table-1 consistency,
   and on JMD scope fit. Major / Minor / Editorial; recommend
   Accept / Minor / Major / Reject / Reject-and-Resubmit.

2. Mock Reviewer #2 -- Biomechanics / impact-mechanics. Strict on the
   energy-absorber motivation, relevance of the axial drop-tower fixture vs.
   real off-axis/cyclic loading, transferability, and metric mapping (SEA ->
   peak transmitted force). Recommendation.

3. Mock Reviewer #3 -- Additive manufacturing / materials. Strict on the
   PLA+TPU multi-material FDM processing claims, the internal-anchor joint vs.
   alternatives, interface durability/fatigue (now appropriately softened?),
   FDM repeatability and resolution limits for continuous-diameter members
   (now discussed?), process-parameter disclosure, and the metal-analog (Al/SS)
   validation plan (now with a pre-specified rank metric?). Recommendation.

4. Mock Editor (JMD Associate Editor) decision letter synthesizing the three
   reviews: single-paragraph summary, decision, and an itemized,
   priority-ordered list of revisions required before resubmission. Explicitly
   assess venue fit and explicitly state whether the round-4 revisions have
   moved the manuscript closer to acceptance relative to the round-3 Major
   Revision decision.

End with a short "Reviewers' bibliographic gaps" section listing specific
peer-reviewed references the authors are likely still missing, by topic, given
references.bib (note which round-3 gaps -- SAASBO, TuRBO, SEA/densification
metrics, SAE J211 -- are now closed).

Be honest, specific, and grounded in the attached files. It is acceptable (and
expected) to note that the placeholder \\todo{}s and the absence of experimental
results gate the final decision. Where round-3 concerns have been resolved, say
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
        name="mock-jmd-review-4-bundle",
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
        "slug": "mock-jmd-review-4",
        "task_id": str(task_id),
        "job": str(JobNames.ANALYSIS),
        "uploaded_collection": uri,
        "query": QUERY,
        "note": "non-blocking; fetch via scripts/edison/fetch_mock_jmd_review4.py",
    }, indent=2))
    print(f"wrote {SUBMITTED}")


if __name__ == "__main__":
    main()
