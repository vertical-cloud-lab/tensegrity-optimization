# Edison trajectory — fourth-round mock JMD peer review

Per PR comment 4699376594 (@sgbaird: *"implement the feedback that you can. Send
back to Edison analysis with all relevant files uploaded, fetch artifacts and
report back."*), the further-revised manuscript draft was submitted to Edison
**ANALYSIS** for a fourth round of mock peer review. This follows round 1 (task
`6c140449`, Reject-and-Resubmit), round 2
(`edison-trajectories/mock-jmd-review-2/…-3fde560e…`, Major Revision), and
round 3 (`edison-trajectories/mock-jmd-review-3/…-d17a2155…`, Major Revision but
improving).

## What was sent

`bundle/` (zipped into `mock-jmd-review-4-bundle.zip` and uploaded as a single
collection, which ANALYSIS requires; the bundle/zip are regenerable build
artifacts and are not committed):

- `manuscript.pdf` — clean reader PDF (todonotes hidden)
- `manuscript-todos.pdf` — review PDF with margin `\todo{}` notes + `\listoftodos`
- `supplementary.pdf` — Supplementary Information
- `manuscript-body.tex` / `manuscript.tex` / `manuscript-todos.tex` /
  `supplementary.tex` — sources
- `references.bib` — curated build bibliography
- `README.md` — manuscript venue / build documentation

The PDFs were rebuilt from source so they reflect the round-3 feedback fixes:
real SAASBO/TuRBO/energy-absorber-metric/SAE-J211 citations (no longer TODO
promises), a pre-committed constrained multi-objective BO formulation (qNEHVI,
rigid-control reference point, LogEI single-objective baseline, robust/evolution
variants demoted to a contingency), an empirical SAASBO-vs-baseline
justification, explicit axial-only scope discipline (off-axis/cyclic/landing
attitude marked future work), a rationale for the fixed 7.0 mm joint diameter, a
new as-built FDM resolution discussion for the continuous diameters, and a
pre-specified Spearman rank-correlation metric for the metal-analog transfer
test (framed as a stringent exploratory test).

The prompt asks the same three-reviewer + Associate-Editor panel as rounds 1–3
to re-review the revised draft, and summarizes what changed since round 3 so the
panel focuses on the current state.

## Task

Submitted via `scripts/edison/submit_mock_jmd_review4.py`; fetched via
`scripts/edison/fetch_mock_jmd_review4.py`. The task id is recorded in
`mock-jmd-review-4-SUBMITTED.json`; the fetched result is written to
`mock-jmd-review-4-<task_id>.{md,json}` (plus `.ipynb` when the ANALYSIS
notebook artifact is present).
