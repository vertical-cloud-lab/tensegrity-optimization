# Input snapshots for the CV signal audit

These files are verbatim copies, taken 2026-09-22, of the campaign data
snapshots on PR #76's manuscript branch
(`copilot/vertical-cloud-labtensegrity-optimization` at commit `adbb771`,
directory `manuscript/data/`). That branch in turn snapshotted them from
the campaign branch `claude/issue-98-20260821-0103` (commits `e25ebf5`,
`bbf7a62`, and `3ad4dd6`; provenance notes in that directory's README).
They are vendored here so this analysis is self-contained and reproducible
on `main` regardless of what happens to either branch.

File-name convention (from the campaign branch): `batch` = the Sobol seed
batch (physical batch 1); `round1` = the first model-recommended batch
(`r2d2c*`, physical batch 2); `round3` = the `drran*` batch (physical
batch 3, Ax trials 28 to 36, re-printed as `2dran*` at the same trials);
`round4` = the `corny*` batch (physical batch 4, trials 37 to 45).

Key files:

- `t3-prism-bo-round5-logocv.csv` and `...-diagnostics.json`: the round-5
  leave-one-design-out CV over all 44 articles (reprint pairs held out
  together, one refit per fold). Produced by
  [`bo/t3_prism_bo_diagnostics.py` at `bbf7a62`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/bbf7a62/bo/t3_prism_bo_diagnostics.py)
  with `--round 5 --cv-only --group-cv` at reduced NUTS settings
  (64 samples / 128 warmup per fold; see the audit README for what that
  does and does not affect). `arm_name` in this CSV is a sequential
  re-index (0 to 43 in article order), not the Ax source trial; joins in
  the audit go through the print keys' `source_trial` column instead.
- `t3-prism-bo-round3-repeatability.csv`: the nine confirmed drran/2dran
  print pairs (identical designs, printed and tested twice).
- `t3-prism-bo-round{1,3,4}-predictions.csv`: the committed at-selection
  posterior predictions for each recommended batch, archived with the
  recommendation artifacts before the batches were printed. The campaign
  candidate-generation fits ran at the full library NUTS defaults
  (256/512), so these numbers do not carry the LOGO run's reduced-budget
  caveat.
- `t3-prism-bo-round{1,3,4}-print-key.csv`: print_id to Ax trial maps,
  with per-article mass, chamber RH, and defect notes.
- `t3-prism-bo-*-drop-results.csv`: per-article stabilized session
  summaries (means and per-drop sd per metric).
- `t3-prism-bo-front-evolution.csv`: hypervolume and front membership
  after each batch.
