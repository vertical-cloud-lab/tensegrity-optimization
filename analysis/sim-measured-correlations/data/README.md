# Input snapshots for the simulation-to-measurement correlation audit

Three groups of files. Measured drop-tower data is not duplicated here: the
audit reads it from [`../../cv-signal-audit/data/`](../../cv-signal-audit/data/)
on this same branch (provenance in that directory's README).

## `campaign/` (vendored 2026-09-23)

Verbatim copies from the campaign branch `claude/issue-98-20260821-0103` at
commit `3ad4dd6`, directory `bo/`:

- `t3-prism-bo-batch-print-key.csv`: the batch-1 (Sobol seed) print key,
  photo-confirmed print_id to spec mapping with as-printed dimensions and
  weighed masses. `amdjwm` (measured, second-lowest t180 of the seed batch)
  appears in the drop results but has no row here and therefore no design
  mapping; it cannot be simulated and joins only measured-vs-measured
  statistics.
- `t3-prism-bo-batch.csv`: nominal Sobol coordinates per seed spec.
- `t3-prism-bo-round{1,3,4}-designs.csv`: per-trial design tables with both
  nominal box coordinates and as-printed (`*_print_mm`) dimensions, plus the
  process parameters (infill percentages, nozzle temperatures, flows) for
  rounds 3 and 4. **These are the canonical as-built geometries**: for every
  r2d2c article the round1 table reproduces the drop-results geometry
  columns exactly, whereas the older `t3-prism-bo-suggestions-round1.csv`
  (which the sim branch's 2026-08 article roster used) carries a superseded
  constant-printed-mass projection that was never printed; round 1 was
  actually built on the constant-solid-mass manifold (30.95 g solid target,
  weighed masses 17.9 to 23.5 g). See the main README, section 1.
- `t3-prism-bo-objectives-mass-normalized.csv`: the campaign's per-gram
  objective variant. Note `e_reb_mJ` per gram equals `e_rebound` times
  `g h`, so the per-gram objective is rank-identical to the restitution
  ratio `e_rebound`; the audit uses `e_rebound` for that channel.

## `sim-branch/` (vendored 2026-09-23)

Verbatim copies from `copilot/explore-simulations-for-tensegrity` at its tip
`94e53a8` (2026-08-26), directory `simulations/outputs/`. These are the
prior sim-vs-measured artifacts this audit replicates and extends:

- `pr102_sim_vs_measured.csv`, `pr102_correlations.csv`: the 2026-08
  correlation screen of ~30 simulated observables against the two measured
  objectives at n = 7 seed articles (write-up: `pr102_sim_campaign.md`
  section 3 on that branch).
- `tierB_articles.csv`, `tierA_articles.csv`, `tier_promotion_stats.csv`,
  `tier_promotion_comparison.csv`: the Tier-B (flexural-strut MuJoCo) and
  Tier-A (PolyFEM viscoelastic) runs over the 21 articles known then.
  Caveat inherited from the geometry note above: their nine r2d2c rows were
  simulated at the superseded suggestions dims (up to ~40 percent off in
  height), so only their batch-1 rows are geometry-correct.
- `zeta_measured_correlations.csv`, `zeta_articles_sim.csv`: the ringdown
  damping study (`zeta_analysis.md` on that branch).
- `pr102_objective_screen_summary.csv`: the simulated candidate-objective
  screen of the era.

## `sim-articles/` (produced on this branch)

Written by [`../run_sims_on_articles.py`](../run_sims_on_articles.py) on
2026-09-23, importing the simulator modules from the sim branch tree at
`94e53a8` unmodified:

- `sim_articles.csv`: one row per design-mapped article (46 = 44 measured
  LOGO articles plus the printed-but-unmeasured `ebdna8` and `1zm8rv`),
  as-printed geometry and weighed mass, with `tierC_*` channels from
  `drop_tower_sim.simulate` and `tierB_*` channels from
  `drop_tower_tierB.simulate_tierB`.
- `regime_designs.csv`: one row per distinct design (37), crutch and lander
  regime metrics from `bo_evaluator.evaluate_printable_design`
  (`F_peak_N`, `SEA_J_per_g`, `SEA_J_per_cm3`, `eta`, `F_base_peak_N`) plus
  the analytic geometry metrics (`geom_cell_mass_g`, `geom_envelope_cm3`,
  `geom_footprint_mm2`). The regime override does not consume the twist
  axis (known Tier-C plumbing gap documented in `sobol_t3_diagnostics.md`
  on the sim branch); the drop-tower tiers do consume twist.

Environment for the run: mujoco 3.14.0, numpy 2.5.3, scipy 1.18.1,
pandas 3.0.6, single-threaded, no RNG anywhere in the simulators. The
batch-1 articles, whose geometry inputs are identical to the 2026-08 run,
reproduce that run's Tier-B `t180` values to a maximum absolute difference
of 3e-14 despite the newer MuJoCo; the nine r2d2c articles move by a median
0.21 in Tier-B `t180` because their geometry is corrected (main README,
section 1).
