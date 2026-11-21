# Campaign summaries used by `scripts/analysis/pareto_rebound_index_variants.py`

Verbatim copies, taken 2026-10-23, so the comparison of m·e and m·e² on
PR #97 can be re-run without fetching other branches. Each file has one row
per tested article (stabilized session means: `t180_mean`, `e_rebound_mean`,
weighed `mass_g`, and the rest of the campaign pipeline's columns).

| file | source branch | commit | path there |
|---|---|---|---|
| `t3-prism-bo-batch-drop-results.csv` | `claude/issue-98-20260821-0103` (PR #102) | `65ff978` | `bo/` |
| `t3-prism-bo-round1-drop-results.csv` | same | `65ff978` | `bo/` |
| `t3-prism-bo-round3-drop-results.csv` | same | `65ff978` | `bo/` |
| `t3-prism-bo-round3-reprint-drop-results.csv` | same | `65ff978` | `bo/` |
| `t3-prism-bo-round4-drop-results.csv` | same | `65ff978` | `bo/` |
| `t3-prism-bo-round3-third-print-drop-results.csv` | `copilot/add-drop-test-protocol-again` (PR #86) | `64e468e` | `data/drop-tests/dran3-checkin/figures/campaign_summary.csv` |

File names follow the PR #102 convention: `batch` is the Sobol seed batch
(physical batch 1), `round1` is `r2d2c*` (batch 2), `round3` is `drran*`
(batch 3), `round3-reprint` is `2dran*` (second print of the batch-3
designs), `round3-third-print` is `dran31` to `dran39` (third print), and
`round4` is `corny*` (batch 4). The five PR #102 files are byte-identical
to the manuscript's snapshots in `manuscript/data/` on PR #76, and the
third-print file is byte-identical to the manuscript's
`t3-prism-bo-round3-third-print-drop-results.csv`.

Not included: the replicate-study plate 1 (`1sne21` to `1sne83`, PR #86
check-in of 2026-10-19), which is interim (two recording faults, seat-gauge
trips on six of nine sessions) and is not in the BO fit or the manuscript.
