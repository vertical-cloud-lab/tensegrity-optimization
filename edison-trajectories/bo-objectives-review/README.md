# Edison adversarial review of the T3-prism BO objectives (task 3e398131)

Fetched 2026-08-22 on PR #76 (the task was submitted from PR #102 on 2026-08-21
by `scripts/edison/submit_bo_objectives_review.py` at commit 467a4f9 on branch
`claude/issue-98-20260821-0103`, and its results had not been fetched until now).

Contents:

- `adversarial-objective-review.md`: the commit-ready report. Headline: do not
  print the round-2 suggestions as-is; drop `e_rebound` from the acquisition
  (it is a velocity ratio under an unvalidated ballistic interpretation, not an
  energy ratio); optimize CFC-180 `t180` alone with input severity controlled;
  replace per-drop SEM with article-level noise (about 0.72 percent CV, so an
  observation SD near 0.0064 to 0.0076, which is 14 to 44 times the per-drop
  SEM); spend print capacity on replicate articles. The claimed t180 vs rebound
  trade-off is not robust (Spearman rho -0.393, p 0.383; removing `6lhxfy`
  collapses it).
- `SECTION_A_LOCKED.md` + `.sha256.txt`: the data-only Section A the reviewer
  committed to before reading the team's choices, with its integrity hash.
- `3e398131-notebook.ipynb`: the analysis notebook artifact.
- `bo-objectives-review-3e398131-*.json` / `.md`: full task state and the
  short-form answer.

Note: the round-2 batch (Ax trials 10 to 18, from commit 7a048ee's mass-aware
objectives) had already been sliced and sent to the printer before this review
was fetched. The manuscript treats the review's recommendations as revision
inputs for round 3 and reports them in the Discussion.
