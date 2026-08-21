# T-3_01 Sobol batch: print key, slicer files, and BO campaign script

This directory holds the key linking each printed T3-prism specimen ID to its
Sobol design parameters, for use when parsing drop data during the testing
campaign (issue [#98](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98)),
plus the Bayesian-optimization script that ingests the campaign results and
suggests the next print batch.

## BO campaign files

- `t3_prism_bo_campaign.py`: Honegumi-templated Ax script (multi-objective,
  fully Bayesian SAASBO, batch, existing data, visualization). Ingests the
  measured drop results, attaches them as completed Ax trials in the base
  Sobol parameter space from PR #35, attaches printed-but-untested specs as
  pending trials, and records the next suggested batch. Accounts for the
  per-print mass differences (18.5 to 22.3 g despite the constant-mass
  constraint, which holds solid CAD volume rather than printed grams): the
  rebound objective is the absolute energy returned to the payload per drop
  (`e_reb_mJ = e_rebound * m_printed * g * h`), its noise folds in the
  print-to-print mass scatter measured from the spec-08 triplicate, and
  `mass_g` is a tracking metric so the model learns printed mass from the
  base coordinates. See the docstring for the objective rationale (why
  `t180` stays a ratio) and the four documented deviations from the
  rendered template. Run from the repo root:
  `python bo/t3_prism_bo_campaign.py`.
- `t3-prism-bo-batch-drop-results.csv`: snapshot of the BO-ready
  `campaign_summary.csv` produced on PR #86 (branch
  `copilot/add-drop-test-protocol-again`, commit `642b8c0`, path
  `data/drop-tests/sobol-campaign/figures/campaign_summary.csv`): one row
  per tested specimen with objectives (mean and sd) and joined as-printed
  geometry. 8 of 9 specimens as of 2026-08-21; `amdjwm` has no known spec
  mapping and is skipped by the script until identified.
- `t3-prism-bo-suggestions-round1.csv`: the recorded round-1 output of the
  script: suggested base-space designs for the next print batch with
  posterior-mean predictions for both objectives, the predicted as-printed
  mass of each design (`pred_mass_g_mean`), and the implied rebound
  fraction at that mass (`pred_e_rebound_approx`, for comparison with the
  raw `e_rebound` column of the results CSV). Feed these rows to
  `t3_prism_sobol_batch.py` (PR #35) for constant-mass projection and
  slicing.
- `t3-prism-bo-ax-client-round1.json`: full AxClient state (experiment,
  data, generation strategy) for reproducibility and warm-starting round 2.
- `figures/t3-prism-bo-round1-pareto.png`: objective-space view (tested
  articles labeled by print ID, the Pareto front through the non-dominated
  articles, and the suggested round-2 candidates at their predicted means),
  styled for slides. The parameter-space parallel-coordinates panel that the
  Honegumi template pairs with it was dropped on review (PR #102). The front
  drawn is the non-dominated set of the observed points, which for round 1 is
  the same three articles (`6lhxfy`, `6nheas`, `bpx68c`) that Ax's
  model-predicted Pareto set picks out. Redraw it without refitting the model
  (pandas + matplotlib only, no Ax install needed) with
  `python bo/t3_prism_bo_campaign.py --plot-only`. Styling follows the
  hand-made reference on PR #102: no legend box (series are named by
  leader-line callouts in the plot area), detached left and bottom spines,
  no gridlines, gray print IDs, horizontal y-axis label above the axis.
- `figures/t3-prism-bo-round2-predicted-vs-actual-PROTOTYPE.png` and
  `t3-prism-bo-round2-outcomes-PROTOTYPE-dummy.csv`: **prototype, synthetic
  data.** The layout the campaign will want once round 2 comes back: each
  orange diamond (predicted) is joined by a straight path to the open black
  circle where that article actually landed, the Pareto front is recomputed
  over both rounds, and the round-1 front stays dashed underneath so the
  improvement reads at a glance. No round-2 article has been printed or
  dropped, so the outcomes are drawn from the model's own predictive
  distribution at 0.3 sd (a full draw scatters the batch off the panel).
  Replace `synthesize_round2_outcomes` with the measured campaign summary to
  turn this into the real figure. Draw it with
  `python bo/t3_prism_bo_campaign.py --prototype-next-round`.

## Print key files

- `t3-prism-bo-batch-print-key.csv`: one row per physical print. Maps the
  6-character print ID to its Sobol specimen number (0 to 8, or S0 for the
  reference prism), the plate in the slicer project, its role
  (official test article or rejected duplicate), documented mass, RH% at time
  of print, noted defects, and as-printed geometry.
- `t3-prism-bo-batch.csv`: the full Sobol batch design table (base and
  as-printed parameter values, mass and envelope constraint checks), copied
  from PR #35 commit `32addaf` so it is available on `main`.
- `slices/t3-prism-bo-batch.H2D-MM-PLAstruts-TPUcables.as-printed.3mf`: the
  Bambu Studio project actually used for the batch prints, uploaded by
  @me-madsen in issue #98. Plates 1 to 9 each hold one specimen and are named
  with the print IDs; plate 10 is an unnamed staging plate with six specimens
  and was not a print source of record.

## Provenance of the key

The print-ID-to-specimen mapping comes from the `.3mf` itself: each plate's
name records the print IDs and each plate carries exactly one specimen object
("Specimen 00" through "Specimen 08"). Masses, RH%, and defects come from the
print documentation comments in issue #98. Geometry columns are the
as-printed values from `t3-prism-bo-batch.csv`.

Known discrepancy, not yet resolved: for Specimen 08, the plate 1 label in
the `.3mf` marks `dea4ls` as official and `bag26v` as good, while the issue
#98 comment of 2026-08-12 marks `bag26v` as official. The key records the
`.3mf` labels and flags both rows; confirm which print is the test article
before analysis.

The S0 reference prism (`bpx68c`) is not part of the Sobol batch and is not
in this `.3mf`; its row is included because it is being tested alongside the
batch. Its geometry is the base T3 prism at scale factor 1.1538 (see the
issue #98 discussion of 2026-08-17).
