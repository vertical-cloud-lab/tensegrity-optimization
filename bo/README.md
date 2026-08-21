# T-3_01 Sobol batch: print key, slicer files, and BO campaign script

This directory holds the key linking each printed T3-prism specimen ID to its
Sobol design parameters, for use when parsing drop data during the testing
campaign (issue [#98](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98)),
plus the Bayesian-optimization script that ingests the campaign results and
suggests the next print batch.

## BO campaign files

- `t3_prism_bo_campaign.py`: Honegumi-templated Ax script (multi-objective,
  fully Bayesian SAASBO, batch, existing data, visualization). Ingests the
  measured drop results, attaches them as completed Ax trials, attaches
  printed-but-untested specs as pending trials, and records the next
  suggested batch. The rebound objective is the absolute energy returned to
  the payload per drop (`e_reb_mJ = e_rebound * m_printed * g * h`), computed
  from each article's own weighed mass, and its noise folds in the
  print-to-print mass scatter measured from the spec-08 triplicate. See the
  docstring for the objective rationale (why `t180` stays a ratio) and the
  five documented deviations from the rendered template. Run from the repo
  root: `python bo/t3_prism_bo_campaign.py`.
- `t3_prism_mass_model.py`: the as-printed mass model, and the
  constant-printed-mass projection built on it. **What round 1 actually held
  constant was solid mass, not volume and not printed grams**: PR #35's
  Route A uniformly re-scales each design until
  `rho_PLA * V_PLA + rho_TPU * V_TPU = 30.95 g` (the solid mass of the S0
  reference STLs), converged to 0.15 g on rendered STL volumes. All 9
  articles sit at that solid mass and still weigh 18.50 to 22.29 g, because
  PLA prints sparse while thin TPU cables print near solid and the PLA/TPU
  split swings from 20.0/10.9 g to 27.3/3.6 g across the batch. This module
  calibrates the gap in two stages (analytic volumes against the 9 rendered
  designs, then rendered solid grams against the 12 weighed articles using a
  wall-plus-infill term in the as-printed strut diameter) and inverts it, so
  a design can be projected onto a constant *printed* mass with a closed
  bisection and no slicer in the loop. Residual sd 0.378 g, at or below the
  0.457 g print-to-print scatter, versus 0.927 g for a flat pair of density
  factors. `python bo/t3_prism_mass_model.py` prints the calibration report
  and re-projects the 9 round-1 articles.

- `t3-prism-bo-batch-drop-results.csv`: snapshot of the BO-ready
  `campaign_summary.csv` produced on PR #86 (branch
  `copilot/add-drop-test-protocol-again`, commit `642b8c0`, path
  `data/drop-tests/sobol-campaign/figures/campaign_summary.csv`): one row
  per tested specimen with objectives (mean and sd) and joined as-printed
  geometry. 8 of 9 specimens as of 2026-08-21; `amdjwm` has no known spec
  mapping and is skipped by the script until identified.
- `t3-prism-bo-suggestions-round1.csv`: the recorded round-1 output of the
  script. Per suggested design: the base (shape) coordinates, the constant
  `mass_printed_g` target, posterior-mean predictions for both objectives,
  the implied rebound fraction at that mass (`pred_e_rebound_approx`, for
  comparison with the raw `e_rebound` column of the results CSV), and the
  as-printed geometry the constant-printed-mass projection produces
  (`scale`, `*_print_mm`, `solid_mass_g`) with PR #35's two printability
  checks evaluated on it (`envelope_ok` for the 250 cm^3 cylinder,
  `cable_bridge_ok` for the 3.0 mm TPU self-bridging floor). Violations are
  flagged, not dropped, exactly as in round 1.
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
- `figures/t3-prism-bo-round2-predicted-vs-actual-PROTOTYPE.gif` and
  `.mp4`: the same prototype played out in time, which is how it is meant to
  be shown. The batch holds as orange diamonds, each diamond then travels its
  straight path to the measurement and hands off to an open black circle on
  arrival, and the front is recomputed while the round-1 front drops back to
  a pale dashed line and the new print IDs fade in. About 7.5 s, and the last
  frame matches the still PNG. Written by the same
  `--prototype-next-round` run; add `--no-animation` to write only the still.
  The MP4 needs `ffmpeg` on PATH (`apt-get install ffmpeg`); without it the
  script falls back to a Pillow-written GIF and skips the MP4. The GIF is
  built from the MP4 with an ffmpeg palette pass (12 fps, 980 px wide), which
  is what keeps it under a megabyte.

### Constant printed mass, and the `fit_out_of_design` kwarg it needs

The search space is 6-dimensional. The first five are PR #35's base Sobol
coordinates with the joint diameter frozen at 7 mm; since the projection
re-scales every dimension including the joint, those five fix the article's
*shape*. The sixth, `mass_printed_g`, fixes its *size*: the projection solves
for the uniform scale that hits that printed mass. Shape and mass together
determine the article exactly, which is what makes "hold the mass constant"
expressible at all.

That splits the space in two. The **fit space** carries `mass_printed_g` over
18.0 to 23.0 g, covering every weighed round-1 article. The **generation
space** pins it to the target (default 20.23 g, the weighed mass of the S0
reference `bpx68c`; `--target-mass-g` overrides). Round-1 data therefore sits
outside the generation space along the mass axis, so:

- the experiment is created on the fit space and the trials attached there,
  because `attach_trial` validates search-space membership and would raise
  long before any model exists;
- the search space is then narrowed, which needs
  `immutable_search_space_and_opt_config=False`;
- the SAASBO step gets
  `model_kwargs={"fit_out_of_design": True, "expand_model_space": True}`, so
  those out-of-design observations are still used to fit while `gen` stays
  inside the narrowed space (facebook/Ax#768). `fit_out_of_design` is
  deprecated after Ax 1.1.2, where `expand_model_space` alone is the live
  mechanism, so this pairing is correct for the pinned 0.5.0 and needs
  revisiting if the pin moves.

The generation slab is +/- 0.01 g rather than a `FixedParameter` or the
+/- 0.457 g print tolerance, for two separate reasons. A `FixedParameter`
would be stripped by Ax's `RemoveFixed` transform, taking the mass dimension
out of the model entirely, and the model needs it: attributing part of the
round-1 objective spread to mass rather than to shape is the whole point. And
a slab as wide as the print tolerance has an exploitable gradient, since
rebound energy scales with mass; with +/- 0.457 g, qNEHVI put all 9
suggestions on the light edge, choosing shapes at 19.77 g and then reporting
them at 20.23 g. The printer's tolerance is not a design variable.

One limitation this does not fix. Round-1 articles were built under the old
projection, so the same coordinates map to slightly different physical
articles now (re-projected scales move by up to 3.5 percent). Carrying
measured mass as the sixth parameter lets the model account for that instead
of silently averaging over it, but it is not the same as re-fitting on
as-printed geometry (facebook/Ax#3577, planned-vs-executed parameters, still
unimplemented upstream).

Still to do before the suggested designs can be printed: PR #35's
`t3_prism_sobol_batch.py` Route A solve has to be re-pointed at printed grams
(target `t3_prism_mass_model`'s model instead of solid mass) so its STLs
match the geometry the suggestions CSV reports.

## Model interpretability (diagnostics)

- `t3_prism_bo_diagnostics.py`: refits the round-1 SAASBO model from the
  committed AxClient snapshot and writes three interpretability figures plus
  the tables behind them. Nothing here comes from the Honegumi template
  (its `visualize=True` block is the Pareto scatter and nothing else); the
  first two are Ax 0.5.0's own diagnostic API and the third is built on top
  of the model's posterior. Run from the repo root:
  `python bo/t3_prism_bo_diagnostics.py` (about 6 min: one full NUTS fit for
  the importances and effects, a second reduced fit plus 7 refits for the
  leave-one-out folds). `--skip-cv` drops the expensive part, and
  `--plot-only` redraws all three figures from the recorded CSVs in about a
  second with only pandas and matplotlib.
- `figures/t3-prism-bo-round1-feature-importance.png` (+
  `t3-prism-bo-round1-feature-importance.csv`): SAAS inverse lengthscales
  per metric, via `TorchModelBridge.feature_importances`, which takes the
  median lengthscale over the MCMC draws, inverts it, and normalizes the
  six parameters to sum to 1. Ax's `MBM_X_trans` maps the search space onto
  the unit cube before fitting, so those numbers are comparable across
  parameters and read as "share of the model's sensitivity". The whiskers
  are the interquartile range across the individual MCMC draws, which the
  single-number Ax API discards; they are what tells you how firmly the
  ranking is held.
- `figures/t3-prism-bo-round1-loocv.png` (+ `t3-prism-bo-round1-loocv.csv`,
  `t3-prism-bo-round1-loocv-diagnostics.json`): leave-one-out via
  `ax.modelbridge.cross_validation.cross_validate(model, folds=-1)`, scored
  by `compute_diagnostics`. One gotcha worth knowing: `BoTorchModel` takes
  `refit_on_cv=False` by default in Ax 0.5.0, so an out-of-the-box
  cross-validation reconditions on the held-out training set while keeping
  hyperparameters fitted on all of the data, which leaks the held-out point
  and flatters the result. The diagnostics fit passes `refit_on_cv=True` and
  pays for the NUTS rerun per fold; that is the whole of the runtime.
- `figures/t3-prism-bo-round1-parameter-effects.png` and
  `figures/t3-prism-bo-round1-parameter-net-effects.png` (+
  `t3-prism-bo-round1-partial-dependence.csv`,
  `t3-prism-bo-round1-parameter-net-effects.csv`): the signed
  "does raising this parameter raise or lower this metric" view. Ax 0.5.0
  has no plot for this on a continuous space (`ax.plot.marginal_effects` is
  for factorial designs, and `plot_slice` fixes the other five parameters at
  one arbitrary point), so the script computes model-based partial
  dependence: sweep one parameter across its range while averaging the
  posterior mean over quasi-random draws of the other five. The first figure
  is the swept curves with a +/- 1 posterior sd band, the second is the net
  change from the low bound to the high bound as a signed tornado. Read them
  together: the tornado compresses each curve to one number, so a parameter
  that turns mid-range is marked with an asterisk and only the curve shows
  what it does. Partial dependence assumes the swept parameter is roughly
  independent of the others (true here, the search space is a plain box) and
  it does not show interactions.

`mass_printed_g` appears on the parameter axis of all three figures rather
than as a metric: under a constant-printed-mass projection the mass is chosen,
not observed, so predicting it would be predicting an input. It is worth
looking at, since it carries 20 percent of the model's t180 sensitivity and
16 percent of its rebound sensitivity, more than either strut or cable
diameter.

Two cautions that apply to all three, since n = 7 tested articles in a 6-D
space is a small sample: the importances sit close to the 1/6 equal-share
line with overlapping MCMC bands, and most of the partial-dependence curves
move by less than their own posterior sd. Read the direction and the
ranking, not the decimals. The mass curves need one more caution of their
own: printed mass and geometry are confounded by construction in round 1
(the light articles *are* the PLA-heavy thick-strut corner), so the sign of
the mass effect is the least trustworthy number on either figure.

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
