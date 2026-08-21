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
  no gridlines, gray print IDs, horizontal y-axis label above the axis. Both
  axis labels mark the good direction with a down-arrow glyph rather than the
  words "lower is better" (PR #102 review); it is set as `ARROW_DOWN` in the
  script, and matplotlib falls through the sans-serif list per character if a
  machine's chosen face lacks U+2193. **Every figure written by either script
  is 300 dpi** (`FIGURE_DPI` in `t3_prism_bo_campaign.py`, imported by the
  diagnostics), so they hold up on a projector and in a printed deck. Print
  IDs are placed by a search that dodges the markers, the other IDs, the
  callout text, the callout leaders and the front line, weighted so that a
  label would rather cross a hairline than sit on top of words; nothing here
  is hand-positioned, because the point cloud moves every round.
- **Prototype, synthetic data.** Three stills and an animation showing the
  layout the campaign will want once round 2 comes back, written by one run of
  `python bo/t3_prism_bo_campaign.py --prototype-next-round`. No round-2
  article has been printed or dropped, so the outcomes are drawn from the
  model's own predictive distribution at 0.3 sd (a full draw scatters the
  batch off the panel) and recorded to
  `t3-prism-bo-round2-outcomes-PROTOTYPE-dummy.csv`. Replace
  `synthesize_round2_outcomes` with the measured campaign summary to turn this
  into the real figure.

  The three stills are the three points at which the figure is at rest, in
  slide order:

  1. `figures/t3-prism-bo-round2-start-PROTOTYPE.png`: the round-1 figure. Its
     front, its print IDs, and the orange suggested points.
  2. `figures/t3-prism-bo-round2-predicted-vs-actual-PROTOTYPE.png`: each
     orange diamond (predicted) joined by a straight path to the open black
     circle where that article actually landed. No front and no print IDs. The
     round-1 front has been retired and the round-2 front has not been computed
     yet; the IDs are retired with it, because seventeen of them over the
     travel paths is the crowding the beat list exists to avoid (PR #102
     review). Identity comes back on still 3.
  3. `figures/t3-prism-bo-round2-front-final-PROTOTYPE.png`: the prediction
     layer gone, the print IDs back, and the front recomputed over both rounds.
     The frame to use when the point is the new front rather than how the model
     did.

  All three are **frames of one figure** rather than three separate drawings,
  exported at 300 dpi (3300 x 2100 px, with that dpi written into the PNG so
  PowerPoint places them at 11 x 7 in) and with no tight bounding box. That
  makes them the same pixel size and puts every element that survives a beat
  (the axes, the ticks, the axis labels, and each print ID) at the same pixel
  in all three, so
  they can go on three consecutive slides and be cross-faded or morphed without
  anything sliding. Drawing them independently could not guarantee that, since
  each panel would solve its own label placement; labels are laid out once,
  against the final frame, for the whole set.
- `figures/t3-prism-bo-round2-predicted-vs-actual-PROTOTYPE.gif` and
  `.mp4`: the same three stills played out in time, which is how it is meant to
  be shown. Choreographed one idea per beat, after the PR #102 review found
  the first cut had too much moving and too much text on screen at once:
  hold on the round-1 figure (1.3 s, still 1), retire the round-1 front, its
  callouts and every print ID with nothing else moving (0.9 s), travel the
  diamonds to their measurements on an otherwise clean panel (2.6 s), hold on
  predicted versus measured (1.7 s, still 2), clear the prediction layer
  (0.9 s), redraw the new front as its own step, wiping in along the polyline
  and filling each article as it reaches it (1.3 s), bring every ID back at
  once now that nothing is moving, and rest (2.4 s, still 3). About 11 s. At
  most one callout is ever lit while anything is in motion, and nothing is
  labeled while anything is moving (eight IDs is fine on the round-1 slide,
  but carrying them through the travel while nine more arrive is not). The
  MP4 is 3300 x 2100 at 25 fps (h.264, yuv420p, so it plays in PowerPoint and
  Keynote as well as a browser), pixel-for-pixel the same canvas as the
  stills. Add `--no-animation` to write only the stills. The MP4 needs
  `ffmpeg` on PATH (`apt-get install ffmpeg`); without it the script falls
  back to a Pillow-written GIF and skips the MP4. The GIF is built from the
  MP4 with an ffmpeg palette pass (12 fps, 1280 px wide) and is for threads
  and this README, not for slides; use the MP4 there.

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
