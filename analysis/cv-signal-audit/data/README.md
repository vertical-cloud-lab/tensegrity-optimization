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
  (64 samples / 128 warmup per fold). Kept as the budget-comparison
  variant; superseded as the audit's primary input by the full-budget
  re-run below. `arm_name` in this CSV is a sequential re-index (0 to 43
  in article order), not the Ax source trial; joins in the audit go
  through the print keys' `source_trial` column instead.
- `full-nuts-rerun/`: the same LOGO-CV re-run 2026-09-22 at the
  library-default NUTS settings (256 samples / 512 warmup per fold), the
  budget every campaign candidate-generation fit used. Produced on this
  branch by [`../rerun_logocv_full_nuts.py`](../rerun_logocv_full_nuts.py)
  against the campaign branch's code and data at `bbf7a62` (same
  `fit_saasbo`/`cross_validate` path, `refit_on_cv=True`), with per-fold
  seeding for reproducibility. `folds.jsonl` holds the raw per-fold
  checkpoints (observed and predicted means and covariances, one JSON
  line per design fold, committed as each fold finished), `state.json`
  the settings and per-fold timings, and the CSV / diagnostics JSON / PNG
  are in the campaign's formats. This is the audit's **primary** LOGO
  input.
- `ablation-six-param/` and `ablation-shape-only/`: the fit-space
  ablation re-runs (2026-09-23, PR #111 follow-up), produced on this
  branch by [`../rerun_logocv_param_ablation.py`](../rerun_logocv_param_ablation.py)
  at the same 256/512 budget, folds, and per-fold seeding as
  `full-nuts-rerun/`, against the same campaign code (`bbf7a62`; branch
  tip `233f4df` leaves both bo scripts untouched). `six-param` fits the
  rounds-1-and-2 space (five shape coordinates plus weighed printed
  mass); `shape-only` drops mass too. Same file layout as
  `full-nuts-rerun/` (per-fold `folds.jsonl` checkpoints committed as
  they landed, `state.json` with settings and timings, final CSV /
  diagnostics JSON / parity PNG in the campaign formats).
- `payload-objectives.csv`: per-article payload-dose objective values
  (2026-09-24, PR #111 follow-up): `tavg10ms` (10 ms moving-average dose
  ratio) and `late_avg3ms_g` (hop-landing severity), each as mean and
  SEM = sd/sqrt(n) over the same stabilized drops the campaign
  aggregated, mirroring how t180/e_reb_mJ were ingested. Vendored by
  [`../rerun_logocv_payload_objective.py`](../rerun_logocv_payload_objective.py)
  `--write-objectives` from
  [`../../payload-protection-metrics/tables/specimen_metrics.csv`](../../payload-protection-metrics/tables/specimen_metrics.csv)
  after the full-101 seed pass (all 45 sessions bit-exact against the
  committed drop-results).
- `objective-tavg10ms/`: the LOGO-CV re-run with the fit metrics swapped
  to that payload pair (2026-09-24), produced on this branch by
  [`../rerun_logocv_payload_objective.py`](../rerun_logocv_payload_objective.py)
  at the same 256/512 budget, 12-parameter space, folds, and per-fold
  seeding as `full-nuts-rerun/` (fold order asserted identical), against
  the same campaign code (`bbf7a62`). Same file layout as the other
  rerun directories.
- `full-fit/`: the Section 8 full-data fits (2026-09-25, PR #111
  follow-up), produced on this branch by
  [`../full_fit_importance_parity.py`](../full_fit_importance_parity.py)
  against the same campaign code (`bbf7a62`) at the same 256/512 NUTS
  budget: one SAASBO fit on all 44 articles (nothing held out) per fit
  space (12-param / 6-param shape+mass / 5-param shape-only) and
  objective pair (campaign t180 + e_reb_mJ, payload tavg10ms +
  late_avg3ms), `torch.manual_seed(10000)` per fit, plus repeat fits at
  seeds 11 and 12 for two combinations to measure NUTS realization
  noise. `fits.jsonl` holds one record per fit (per-parameter
  importances with per-draw quantiles, in-sample predictions with
  posterior sd, committed as each fit landed), `state.json` the settings
  and timings; `feature-importance.csv` and `insample-predictions.csv`
  are the assembled tidy tables.
- `mass-normalized-objectives.csv` and
  `objective-per-gram/`, `objective-per-gram-six-param/` (2026-09-25,
  PR #111 follow-up): the Section 9 mass-normalization experiment.
  The CSV is the per-article table written by
  [`../mass_normalization_checks.py`](../mass_normalization_checks.py):
  weighed mass, the five shape coordinates, and each of the four audited
  objectives in three framings (raw, divided by mass, and with an
  ordinary least squares fit on mass subtracted), each with a propagated
  standard error. Objective values are the ones the campaign fitted
  (`t180`, `e_reb_mJ` read from `full-nuts-rerun/`) and the payload pair
  from `payload-objectives.csv`; masses are the weighed values in the
  drop-results tables. The two run directories are LOGO-CV re-runs from
  [`../rerun_logocv_mass_normalized.py`](../rerun_logocv_mass_normalized.py)
  with the fit metrics divided by mass, in the campaign's 12-parameter
  space and the rounds-1-and-2 six-parameter space, both of which keep
  `mass_printed_g` as an input. Same 256/512 budget, same folds, and the
  same per-fold seeding as `full-nuts-rerun/`, with the fold order
  asserted equal to it, so differences are attributable to the objective
  transform plus NUTS realization noise. Same file layout as the other
  run directories.
- `objective-tavg10ms-shape-only/` (2026-09-24, Section 7): the payload
  pair in the five-coordinate shape-only space, from
  [`../rerun_logocv_payload_objective.py`](../rerun_logocv_payload_objective.py)
  `--shape-only`.
- `objective-per-gram-shape-only/` and
  `objective-payload-per-gram-shape-only/` (2026-09-25, Section 10): the
  shape-only space with each objective divided by the weighed mass
  (campaign pair and payload pair), from
  [`../rerun_logocv_shape_only_per_gram.py`](../rerun_logocv_shape_only_per_gram.py),
  values from `mass-normalized-objectives.csv`. Folds were split across
  worker processes at one torch thread each (`torch_threads` in
  `state.json`); the campaign-pair run finished at 06:53 UTC, after the
  job that started it had posted its comment.
- `objective-tavg10ms-shape-infill/` (2026-09-25, Section 11): the payload
  pair, raw, in the five shape coordinates plus the two slicer infill
  settings (`strut_infill_pct`, `tpu_infill_pct`), mass and the four
  filament settings out, from
  [`../rerun_logocv_shape_infill.py`](../rerun_logocv_shape_infill.py).
  Before it ran, fold `r2d2c3` of `objective-tavg10ms-shape-only/` was
  re-run alone on the same runner at the default thread count and
  matched the committed predictions and covariances exactly. Four
  workers at one torch thread each. Like the three directories above it,
  this run follows the `full-nuts-rerun/` protocol: campaign code at
  `bbf7a62`, 256/512 NUTS, the same 35 folds with the fold order
  asserted equal, the same per-fold seeds, and the same file layout.
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
