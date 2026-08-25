#!/usr/bin/env python3
"""Submit one iteration of the Edison rubber-duck review of the JMD manuscript.

Per the PR #76 request (@sgbaird, 2026-08-22): after the extensive overhaul
aligning the manuscript with #84/#102/#99/#33 and the rest of the recent repo
history, run five iterations of "send one query to Edison, manually correct".
Each iteration has a distinct focus and uses an adversarial / Socratic framing:
Edison is asked to pose the hardest questions an expert referee would ask,
answer them from the attached materials where they are answerable, and flag
what the manuscript cannot answer, with severity and a concrete fix.

Usage::

    python scripts/edison/submit_rubberduck.py <iteration 1-5>

Writes the task id to
``edison-trajectories/rubberduck-<n>/rubberduck-<n>-SUBMITTED.json``;
fetch with ``python scripts/edison/fetch_rubberduck.py <n>``.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
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

BUNDLE_SRC = [
    MANU / "manuscript.pdf",
    MANU / "supplementary.pdf",
    MANU / "manuscript-body.tex",
    MANU / "supplementary.tex",
    MANU / "references.bib",
]

# Campaign data files so the reviewer can recompute rather than trust.
DATA_SRC_REMOTE = [
    # (path in repo working tree, bundled name)
    (HERE / "figures" / "bo" / "t3-prism-bo-round1-pareto.png",
     "t3-prism-bo-round1-pareto.png"),
]

PREAMBLE = """\
You are the rubber duck for an ASME Journal of Mechanical Design manuscript.
This is iteration {n} of 5, each with a different focus. Work by ADVERSARIAL
DIALOGUE and the SOCRATIC METHOD: write the session as an explicit
question-and-answer dialogue. For each probe, (a) pose the hardest question a
hostile expert referee would ask, (b) attempt to answer it yourself STRICTLY
from the attached materials (manuscript.pdf, supplementary.pdf, LaTeX sources,
references.bib, and the campaign data CSVs), quoting or citing the exact
passage or data you used, and (c) render a verdict: WITHSTANDS (the manuscript
answers it), WOUNDED (answerable but the text needs a specific change), or
FAILS (the manuscript cannot answer it and must change or soften). For every
WOUNDED or FAILS verdict, give the concrete edit you would make, at the level
of the sentence or number to change.

Context you should take as given rather than re-litigate: the campaign is
mid-flight. The nine-design Sobol seed round plus a reference prism are
printed; eight articles have completed 101-drop drop-tower sessions; a fully
Bayesian SAASBO surrogate was fit; nine round-2 designs are on the printer.
Round-2 results, the budget-matched baseline, the quasi-static Instron
campaign, and the metal-analog build are honestly declared placeholders; do
not flag their absence as a defect, but DO flag any place where the text
overclaims beyond the seed round. A prior adversarial review of the BO
objective stack (task 3e398131) already established: the rebound-energy
objective rests on an unvalidated ballistic interpretation, the
t180-versus-rebound trade-off is fragile at n=8, and per-drop SEM understates
article-level noise (about 0.72 percent CV); the manuscript now discloses all
three in its Discussion, so check the disclosure is faithful rather than
re-derive it.

The campaign data files attached are: t3-prism-bo-batch-drop-results.csv (one
row per tested article: stabilized objective means/sds over the 101-drop
session, ringdown descriptors, joined as-printed geometry and weighed mass),
t3-prism-bo-batch-print-key.csv (print IDs, masses, defects),
t3-prism-bo-suggestions-round1.csv (the model-recommended round-2 designs
with posterior predictions), and the round-1 Pareto figure PNG.
"""

FOCI = {
    1: """\
FOCUS OF THIS ITERATION: the Methods (Sections 3.1 to 3.4) and the objective
stack. Socratic sequence to run, at minimum: (1) From the drop-tower protocol
description ALONE (Section 3.3 and SI S4), derive what per-specimen
objectives YOU would define; then compare with Eq. (1) and interrogate every
symbol: is t180 well-defined (window, filter class, vector magnitude over
scalar peak), is E_reb dimensionally and physically coherent, is
e_reb = g t_second / (2 dv) actually a restitution-like fraction, and does
the text's refusal to call t180 a transmissibility hold up against SAE
J211 / ISO usage? (2) Could a reader reproduce the campaign from the Methods:
what is missing, what is TBD, and is every TBD honestly marked? (3) Is the
constant-solid-mass projection (m* = 30.95 g, envelope and cable-bridge
screens) described consistently between Section 3.1, the table captions, and
SI S5, and is its known limitation (printed grams not constant) disclosed
where a referee will look? (4) Does the noise-model paragraph (per-drop SEM
plus mass scatter, with the article-level correction flagged for round 3)
describe something a GP can actually consume, and is the SAASBO choice
justified or merely asserted? (5) Any internal contradiction between Methods
and the Results/Discussion numbers.""",
    2: """\
FOCUS OF THIS ITERATION: the Results (Section 4), the figures, and numerical
cross-checks. You have the raw campaign CSVs: RECOMPUTE rather than trust.
At minimum: (1) Recompute E_reb = e_rebound x mass x g x h (h = 60 in) for
every article in t3-prism-bo-batch-drop-results.csv and check Table 5's mJ
values and t180 means/sds against the CSV; flag any mismatch beyond rounding.
(2) Verify the claimed t180 span (0.893 to 1.062), the claim that seven of
eight articles amplify, the 17 percent design-driven spread, and the
correlation r = 0.83 between printed mass and t180 (compute it from the CSV;
state which articles you used and why). (3) Verify the observed Pareto set
(6lhxfy, 6nheas, bpx68c) is exactly the non-dominated set of the tested
articles under joint minimization, and that the figure matches. (4) Check
Table 5's row ordering, units, and the fn column against the CSV, including
the missing-value handling for amdjwm and bag26v. (5) Check every number
quoted in Section 4.2's surrogate-audit paragraph (MAPE 2.6 percent, r = 0.70,
r = -0.12) is consistent with the figures and plausibly derived from
leave-one-out at n = 7. (6) Inspect the attached Pareto PNG: do axis labels,
IDs, and front membership agree with the text and the CSV?""",
    3: """\
FOCUS OF THIS ITERATION: framing, novelty, and scope (title, abstract,
Sections 1, 2, and the novelty table). At minimum: (1) Attack the novelty
claim "no prior study closes a BO loop over co-printed multi-material
tensegrity-inspired hardware using physical impact measurements as the sole
ground truth" against the cited literature in references.bib (Pajunen 2019 and
2021, Bauer 2021, Intrigila 2022, Mo 2023, Santos 2023, Sabouni-Zawadzka
2024, Almeida 2025, Davami 2025, Wang 2026): is the claim stated with exactly
the right qualifiers, and does the novelty table's row for this work match
what was actually executed (SAASBO/qNEHVI on t180 and rebound energy, not SEA)?
(2) Is the planetary-lander motivation honest given the measured result that
most seed articles AMPLIFY peak shock, and does the testbed-not-flight-hardware
framing paragraph inoculate the paper adequately? (3) Does the abstract match
the body (objectives, budget, what is done versus planned), and is it within
JMD's length norms? (4) Is the tensegrity-inspired versus true-tensegrity
caveat (no pretension, extensible TPU) made early and consistently, and does
any sentence slip into claiming true tensegrity behavior? (5) Scope
discipline: does the out-of-scope list survive contact with what the
Discussion later claims?""",
    4: """\
FOCUS OF THIS ITERATION: statistical integrity at small n. The seed round has
eight tested articles, seven mapped to designs, one article per design (one
triplicate on a single design). At minimum: (1) Enumerate every quantitative
claim in the manuscript that rests on these n (correlations r = 0.83 and
rho = -0.93, the trade-off claim, the 17 percent spread, feature importances,
LOOCV metrics, the 0.72 percent article-level CV, the repeatability CVs) and
for each, judge whether the stated confidence matches what n supports,
proposing softened wording where it does not. (2) Is the mass-confound
treatment statistically coherent: the text argues regressing mass out at
n = 8 would delete signal because light articles ARE the thick-strut corner
by construction; steelman and attack that argument. (3) The trade-off
fragility disclosure quotes Spearman rho = -0.39, p = 0.38 from the prior
adversarial review; is the manuscript's use of "the two genuinely trade off
in the measured seed round" (Methods 3.4) consistent with that disclosure, or
does wording need to converge? (4) Are the within-specimen CVs (0.2 to 0.5
percent) and the cross-session 0.13 percent reproduction being used to imply
more article-level certainty than they license? (5) Propose the minimal set
of statistical-language edits that would survive a hostile statistics
reviewer, ranked by importance.""",
    5: """\
FOCUS OF THIS ITERATION: the full-referee pass. Play a complete JMD referee
panel in dialogue form: a design/optimization referee, an impact-mechanics
referee, and an AM/materials referee each get a Socratic exchange (hardest
question, best answer from the materials, verdict), then an Associate Editor
synthesizes. Cover anything the first four iterations' foci would miss:
Background completeness, figure quality and captions, SI-to-main-text
division, reference formatting and any miscitations, the metal-analog
protocol, the simulation ladder's claims (including the Spearman rho = -0.93
cross-metric claim and its n = 7 basis), reproducibility/archival statements,
and the honesty of every placeholder. End with: (a) a priority-ordered
revision list distinguishing MUST-FIX-NOW (wording/consistency, fixable
without new data) from DATA-GATED, and (b) a frank one-paragraph assessment
of how far this draft is from a JMD Major-Revision-toward-accept, given that
Results are mid-campaign.""",
}


def main() -> None:
    n = int(sys.argv[1])
    assert n in FOCI, f"iteration must be 1-5, got {n}"
    traj = HERE / "edison-trajectories" / f"rubberduck-{n}"
    bundle_dir = traj / "bundle"
    bundle = traj / f"rubberduck-{n}-bundle.zip"
    submitted = traj / f"rubberduck-{n}-SUBMITTED.json"

    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True)
    for src in BUNDLE_SRC:
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, bundle_dir / src.name)
    for src, name in DATA_SRC_REMOTE:
        if src.exists():
            shutil.copy2(src, bundle_dir / name)
    # Campaign CSVs snapshotted from the PR #102 branch into /tmp/bo by the
    # session; fall back to fetching from git if absent.
    import subprocess
    for csv_name in (
        "t3-prism-bo-batch-drop-results.csv",
        "t3-prism-bo-batch-print-key.csv",
        "t3-prism-bo-suggestions-round1.csv",
    ):
        local = Path("/tmp/bo") / csv_name
        if local.exists():
            shutil.copy2(local, bundle_dir / csv_name)
        else:
            out = subprocess.run(
                ["git", "-C", str(HERE), "show",
                 f"origin/claude/issue-98-20260821-0103:bo/{csv_name}"],
                capture_output=True, text=True, check=True,
            ).stdout
            (bundle_dir / csv_name).write_text(out)

    files = sorted(p for p in bundle_dir.iterdir() if p.is_file())
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            zf.write(p, arcname=p.name)
    print(f"built {bundle} ({bundle.stat().st_size} bytes, {len(files)} files)")

    query = PREAMBLE.format(n=n) + "\n" + FOCI[n]

    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY")
        or os.environ.get("EDISON_API_KEY")
    )
    resp = client.store_file_content(
        name=f"rubberduck-{n}-bundle",
        file_path=str(bundle),
        as_collection=True,
    )
    entry_id = resp.data_storage.id
    uri = f"data_entry:{entry_id}"
    print(f"uploaded collection -> {uri}")

    task = TaskRequest(name=JobNames.ANALYSIS, query=query)
    sub = client.create_task(task, files=[uri])
    task_id = getattr(sub, "task_id", None) or (sub if isinstance(sub, str) else None)
    print(f"submitted ANALYSIS task_id={task_id}")

    submitted.write_text(json.dumps({
        "slug": f"rubberduck-{n}",
        "task_id": str(task_id),
        "job": str(JobNames.ANALYSIS),
        "uploaded_collection": uri,
        "query": query,
        "note": "fetch via scripts/edison/fetch_rubberduck.py",
    }, indent=2))
    print(f"wrote {submitted}")


if __name__ == "__main__":
    main()
