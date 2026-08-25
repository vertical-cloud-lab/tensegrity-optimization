#!/usr/bin/env python3
"""Submit the revised manuscript to Edison ANALYSIS for a FIFTH round of mock
JMD peer review.

Per PR comment 4700329518 (@sgbaird-yolo: "yes" -- approving the round-4 ask to
integrate the already-flagged tensegrity-AM references), this bundles the current
manuscript (clean PDF + review PDF + SI PDF + sources + references.bib) into a
single zipped collection (required for ANALYSIS uploads) and asks the same
three-reviewer + Associate-Editor panel used in rounds 1-4 to re-review the
further-revised draft.

The prompt summarizes what changed since round 4 (the integrated
tensegrity-additive-manufacturing literature) so the panel can focus on the
current state rather than re-flagging already-addressed items.

Non-blocking: the task id is written to ``mock-jmd-review-5-SUBMITTED.json`` for
a later fetch via ``client.get_task(task_id)`` (see fetch_mock_jmd_review5.py).

Run::

    python scripts/edison/submit_mock_jmd_review5.py
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
TRAJ = HERE / "edison-trajectories" / "mock-jmd-review-5"
BUNDLE_DIR = TRAJ / "bundle"
BUNDLE = TRAJ / "mock-jmd-review-5-bundle.zip"
SUBMITTED = TRAJ / "mock-jmd-review-5-SUBMITTED.json"

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
FIFTH-ROUND mock peer review for an ASME Journal of Mechanical Design (JMD)
Research Paper submission. You reviewed earlier drafts of this same manuscript in
four prior rounds (round 1 = Reject-and-Resubmit, round 2 = Major Revision,
round 3 = Major Revision but improving, round 4 = Major Revision and closer to
publishable form); this is the further-revised draft. The attached files are the
current populated draft (manuscript.pdf is the clean reader PDF;
manuscript-todos.pdf is the review PDF that additionally shows margin \\todo{}
annotations and a \\listoftodos; supplementary.pdf is the Supplementary
Information; sources are manuscript-body.tex / manuscript.tex /
manuscript-todos.tex / supplementary.tex and references.bib;
manuscript/README.md documents venue choice and build).

The paper is a multi-material 3D-printed (FDM) tensegrity-inspired
energy-absorbing structure study using experiment-driven Bayesian optimization
(BO). Rigid PLA struts in compression + soft TPU cables in tension, printed on a
Bambu Lab H2D dual-nozzle FDM printer, characterized under quasi-static
compression and drop-weight impact. The motivating application is framed up front
as a planetary-lander / payload energy absorber; a crutch-tip is mentioned only
as future work in the Discussion. Quantitative Results/Discussion are
INTENTIONALLY still \\todo{} placeholders -- the project is at the
planned-methods phase. Please review structure, framing, scope, novelty claims,
methods rigor, literature coverage, internal consistency, and venue fit (ASME JMD
vs. backup Smart Materials and Structures / Additive Manufacturing), NOT raw
numerical values.

What CHANGED since round 4 (so you can focus on the current state rather than
re-flagging already-addressed items). This edit responds directly to the only new
reference ask in the round-4 Associate-Editor letter:
  * TENSEGRITY-ADDITIVE-MANUFACTURING LITERATURE NOW INTEGRATED. The round-4
    editor confirmed all four round-3 citation gaps (SAASBO, TuRBO,
    SEA/densification metrics, SAE J211) were CLOSED and asked only that the
    already-flagged tensegrity-AM works be integrated once verified. Each DOI was
    verified against Crossref and the following are now cited in the
    "Multi-Material 3D Printing" / tensegrity-architecture background (replacing
    the prior \\todo{} placeholder note):
      - Bauer et al. 2021, Advanced Materials 33(10):2005647
        (doi:10.1002/adma.202005647) -- 3D-printed tensegrity metamaterials that
        delocalize deformation to resist catastrophic failure.
      - Pajunen et al. 2021, Extreme Mechanics Letters 44:101236
        (doi:10.1016/j.eml.2021.101236) -- prestrain-induced bandgap tuning in
        3D-printed tensegrity-inspired lattices.
      - Sabouni-Zawadzka et al. 2024, Archives of Civil Engineering 70(2):343-357
        (doi:10.24425/ace.2024.150987) -- experimental mechanical properties of
        3D-printed tensegrity-inspired metamaterials (4-strut simplex module).
      - Almeida et al. 2025, Int. J. Solids and Structures 322:113590
        (doi:10.1016/j.ijsolstr.2025.113590) -- high-strain-rate response of
        3D-printable tensegrity-inspired structures.
      - Davami et al. 2025, Int. J. Impact Engineering 198:105208
        (doi:10.1016/j.ijimpeng.2024.105208) -- dynamic analysis of additively
        manufactured tensegrity structures.
      - Wang et al. 2026, Additive Manufacturing 118:105107
        (doi:10.1016/j.addma.2026.105107) -- integrated fabrication and
        validation of tensegrity-inspired rigid-flexible metamaterials.
    (Santos 2023, Adv. Mater., doi:10.1002/adma.202300639, flagged in the same
    round-4 list, was already cited in earlier rounds.) The TODO note that
    enumerated these as "to verify-then-cite" has been removed.

All round-2/3/4 method and framing fixes remain in place: real SAASBO/TuRBO and
SEA/densification/SAE-J211 citations; the primary campaign pre-committed as a
CONSTRAINED MULTI-OBJECTIVE problem (maximize SEA and compaction efficiency
subject to peak transmitted force F_max <= F*, F* fixed from the rigid control;
acquisition qNEHVI; hypervolume reference point at the rigid-control point;
single-objective LogEI kept only as a baseline; robust/evolution-guided variants
demoted to contingency); empirical SAASBO-vs-single-task-GP benchmarking;
internally consistent budget (n=9 Sobol + T=10 x q=5 = 59 specimens); explicit
out-of-scope statement (off-axis/combined loading, multi-hit/cyclic durability,
landing-attitude variability are future work); justified fixed joint diameter
d_j = 7.0 mm; an as-built-resolution paragraph; and a pre-specified Spearman
rank-correlation (rho_s) criterion for the exploratory metal-analog (Al/SS)
transfer test.

STILL INTENTIONALLY OPEN (known gates, do not re-flag as new defects): the
quantitative Results and Discussion remain \\todo{} placeholders and several
BO/impact figures are illustrative synthetic examples; some fabrication/test
process parameters (Table 3 print settings, exact fixtures/DAQ) remain TBD
pending the campaign; the Zenodo archival DOI is a placeholder.

Produce FOUR artifacts, in the same style as a JMD decision-letter package:

1. Mock Reviewer #1 -- Design / Mechanical Engineering (typical ASME JMD
   reviewer). Strict on novelty vs. prior tensegrity/lattice/spring-loaded work
   (now that the tensegrity-AM literature is integrated, is the novelty claim
   still defensible and correctly positioned?), on the BO formulation (kernel,
   acquisition, noise, batch/budget, SAASBO justification at ~5 variables,
   constrained multi-objective formulation and reference point), on
   parameterization completeness and Table-1 consistency, and on JMD scope fit.
   Major / Minor / Editorial; recommend
   Accept / Minor / Major / Reject / Reject-and-Resubmit.

2. Mock Reviewer #2 -- Biomechanics / impact-mechanics. Strict on the
   energy-absorber motivation, relevance of the axial drop-tower fixture vs. real
   off-axis/cyclic loading, transferability, and metric mapping (SEA -> peak
   transmitted force). Recommendation.

3. Mock Reviewer #3 -- Additive manufacturing / materials. Strict on the PLA+TPU
   multi-material FDM processing claims, the internal-anchor joint vs.
   alternatives, interface durability/fatigue, FDM repeatability and resolution
   limits for continuous-diameter members, process-parameter disclosure, the
   metal-analog (Al/SS) validation plan, and whether the newly integrated
   tensegrity-AM references are used appropriately (not over-claimed). Recommend.

4. Mock Editor (JMD Associate Editor) decision letter synthesizing the three
   reviews: single-paragraph summary, decision, and an itemized, priority-ordered
   list of revisions required before resubmission. Explicitly assess venue fit
   and explicitly state whether the round-5 revisions (tensegrity-AM literature
   integration) have moved the manuscript closer to acceptance relative to the
   round-4 Major Revision decision, and whether the round-4 reference ask is now
   resolved.

End with a short "Reviewers' bibliographic gaps" section listing any specific
peer-reviewed references the authors are still missing, by topic, given
references.bib (note explicitly that the round-3 gaps -- SAASBO, TuRBO,
SEA/densification metrics, SAE J211 -- and the round-4 tensegrity-AM ask are now
closed).

Be honest, specific, and grounded in the attached files. It is acceptable (and
expected) to note that the placeholder \\todo{}s and the absence of experimental
results gate the final decision. Where prior concerns have been resolved, say so;
where they persist or new ones appear, flag them.
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
        name="mock-jmd-review-5-bundle",
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
        "slug": "mock-jmd-review-5",
        "task_id": str(task_id),
        "job": str(JobNames.ANALYSIS),
        "uploaded_collection": uri,
        "query": QUERY,
        "note": "non-blocking; fetch via scripts/edison/fetch_mock_jmd_review5.py",
    }, indent=2))
    print(f"wrote {SUBMITTED}")


if __name__ == "__main__":
    main()
