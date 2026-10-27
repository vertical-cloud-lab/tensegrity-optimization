# Simulation-only campaign figures

Figures for the simulated Bayesian-optimization campaign of PR #33, cited in
the manuscript as Section 3.6 (Methods, `sec:methods:sim`), Section 4.4
(Results, `sec:results:sim`, Table `tab:sim-campaign`) and the Supplementary
Information section `si:sim-campaign`.

| File | Used as | Built by |
|---|---|---|
| `sim-campaign.png` | SI Fig. `fig:si-sim-campaign` | `scripts/figures/sim_campaign_tables.py` |

Regenerate with `make sim` (or `python3 scripts/figures/sim_campaign_tables.py`).
The same script writes `manuscript/tables/sim-campaign.tex` (main-text table),
`manuscript/tables/si-sim-campaign.tex` (SI table) and
`manuscript/data/sim/sim-campaign-stats.json` (every number the text quotes).
It needs numpy, scipy, pandas and matplotlib, reads only the snapshot under
`manuscript/data/sim/`, and stops with an error if the recomputation
disagrees with the committed PR #33 summaries or audit.

## Provenance of the snapshot

Every file under `manuscript/data/sim/` except `sim-campaign-stats.json` is a
verbatim copy from branch `copilot/explore-simulations-for-tensegrity`
(PR #33) at commit `94e53a8`:

| Snapshot path | Source path at `94e53a8` |
|---|---|
| `envelope/contrast_bo_envelope_seed{0..9}.csv` | `simulations/outputs/bo_contrast/` (10 BO repeats, t180 + envelope pair) |
| `envelope/contrast_baseline_{random,sobol,lhs,heuristic}_{printable,plain}_envelope_seed{0..9}.csv` | `simulations/outputs/bo_contrast/` (80 baseline runs; `heuristic` is compass search; `printable` is the filtered mode) |
| `strain-era/pr102_sim_bo_botorch_ratios-strain_sobol_seed{0..9}.csv`, `strain-era/pr102_baseline_{random,sobol,lhs,heuristic}_ratios-strain_seed{0..9}.csv` | `simulations/outputs/` (the t180 + peak-tendon-strain control pair, full acquisition effort) |
| `contrast_refs.csv`, `contrast_front_{envelope,strain}.csv`, `contrast_screen.csv`, `contrast_cloud_ratios.csv.gz` | `simulations/outputs/bo_contrast/` (reference points, refined fronts, pair screen, 16,384-design sweep) |
| `bo_contrast_envelope_summary.csv`, `bo_contrast_strain_era_rescored{,_seeds}.csv` | `simulations/outputs/bo_contrast/` (committed summaries, used only as cross-checks) |
| `audits/synthetic_audit_physics.csv` | `simulations/outputs/synthetic_bo/` (hypervolume audit against BoTorch, best-known reference) |
| `audits/edison-bo-contrast-review-53cfc937.md` | `edison-trajectories/bo-contrast-review/bo-contrast-review-53cfc937-0b8f-4d84-a306-08432b429ef0.md` (independent implementation review; the full JSON trajectory stays on the PR #33 branch) |

The simulator (`simulations/drop_tower_sim.py`) and the campaign driver
(`simulations/bo_contrast_study.py`) are not copied; they live on the PR #33
branch, which must be merged or tagged before submission (a `\todo` in the
Methods says so).

## What the script checks

- Every run holds exactly 45 evaluations.
- Each run's final hypervolume, recomputed from its feasible evaluations,
  matches the running value stored in its CSV (relative difference below
  1e-5; the largest is 2e-6, from `%.6g` rounding).
- The method means match `bo_contrast_envelope_summary.csv`, and the strain
  rescoring matches `bo_contrast_strain_era_rescored_seeds.csv`.
- The envelope pair's best-known reference hypervolume (87.086) matches the
  value in `audits/synthetic_audit_physics.csv`.
- The refined-front and sweep hypervolumes match `contrast_refs.csv`.
- No two BO seeds drew the same first (Sobol) batch.
