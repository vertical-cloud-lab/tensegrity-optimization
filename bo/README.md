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
  mapping and is skipped by the script until identified. The `ajhby6` row
  (spec 07, the specimen missing from the PR #86 snapshot) was appended on
  2026-08-24 from its Box upload, computed with the same PR #86 analysis
  script; see the round-2 section below for the fetch provenance.
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
- **Prototype, synthetic data.** Four stills and an animation showing the
  layout the campaign will want once round 2 comes back, written by one run of
  `python bo/t3_prism_bo_campaign.py --prototype-next-round`. No round-2
  article has been printed or dropped, so the outcomes are drawn from the
  model's own predictive distribution at 0.3 sd (a full draw scatters the
  batch off the panel) and recorded to
  `t3-prism-bo-round2-outcomes-PROTOTYPE-dummy.csv`. Replace
  `synthesize_round2_outcomes` with the measured campaign summary to turn this
  into the real figure.

  The four stills are the four points at which the figure is at rest, in
  slide order:

  1. `figures/t3-prism-bo-round2-start-PROTOTYPE.png`: the round-1 figure. Its
     front, its print IDs, and the orange suggested points.
  2. `figures/t3-prism-bo-round2-uncertainty-PROTOTYPE.png`: the predicted
     uncertainties at the suggested points, frozen before anything moves
     (PR #102 review): a horizontal and a vertical bar spanning plus or minus
     1 sd per objective, and a shaded oval through the same contour, both in
     faded shades of the suggestion orange. The sd is **1 posterior standard
     deviation of the model's noise-free objective prediction** (the square
     root of the diagonal of the covariance `TorchModelBridge.predict`
     returned when the batch was generated, averaged over the SAAS MCMC
     draws). It is epistemic model uncertainty, not a standard error of any
     sample of drops. Only the per-objective marginals were recorded to the
     suggestions CSV, so the oval is axis-aligned; the cross-objective
     covariance `predict` also returns was not saved. Several rebound-energy
     sds are taller than the panel and simply crop at the axes, which is the
     honest picture: the LOOCV diagnostic found no out-of-sample skill on
     that objective, and these ovals are the same fact drawn in objective
     space.
  3. `figures/t3-prism-bo-round2-predicted-vs-actual-PROTOTYPE.png`: each
     orange diamond (predicted) joined by a straight path to the open black
     circle where that article actually landed. No front and no print IDs. The
     round-1 front has been retired and the round-2 front has not been computed
     yet; the IDs are retired with it, because seventeen of them over the
     travel paths is the crowding the beat list exists to avoid (PR #102
     review). The uncertainty layer stays anchored at the predictions at ghost
     opacity, so predicted-band-versus-landing is readable. Identity comes
     back on still 4.
  4. `figures/t3-prism-bo-round2-front-final-PROTOTYPE.png`: the prediction
     layer gone, the print IDs back, and the front recomputed over both rounds.
     The frame to use when the point is the new front rather than how the model
     did.

  All four are **frames of one figure** rather than four separate drawings,
  exported at 300 dpi (3300 x 2100 px, with that dpi written into the PNG so
  PowerPoint places them at 11 x 7 in) and with no tight bounding box. That
  makes them the same pixel size and puts every element that survives a beat
  (the axes, the ticks, the axis labels, and each print ID) at the same pixel
  in all four, so
  they can go on four consecutive slides and be cross-faded or morphed without
  anything sliding. Drawing them independently could not guarantee that, since
  each panel would solve its own label placement; labels are laid out once,
  against the final frame, for the whole set.
- `figures/t3-prism-bo-round2-predicted-vs-actual-PROTOTYPE.gif` and
  `.mp4`: the same four stills played out in time, which is how it is meant to
  be shown. Choreographed one idea per beat, after the PR #102 review found
  the first cut had too much moving and too much text on screen at once:
  hold on the round-1 figure (1.3 s, still 1), retire the round-1 front, its
  callouts and every print ID with nothing else moving (0.9 s), grow the
  plus-or-minus-1-sd bars and ovals in and freeze so they can be read
  (0.7 s + 1.4 s, still 2), travel the
  diamonds to their measurements while the uncertainty layer fades to ghost
  opacity at the predictions (2.6 s), hold on
  predicted versus measured (1.7 s, still 3), clear the prediction layer and
  its uncertainties
  (0.9 s), redraw the new front as its own step, wiping in along the polyline
  and filling each article as it reaches it (1.3 s), bring every ID back at
  once now that nothing is moving, and rest (2.4 s, still 4). About 13 s. At
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

## Drop-count sensitivity (shorter round-2 sessions)

Round 1 ran ~101 drops per specimen. When session time is short, fewer drops
per specimen is an option, and this analysis quantifies the cost by replaying
round 1 as if each session had stopped after the first N drops.

- `t3-prism-per-drop-metrics.csv`: per-drop t180 and e_rebound for all 893
  valid round-1 drops (9 specimens). The first 8 specimens are extracted from
  `campaign_metrics.json` on the PR #86 branch
  `copilot/add-drop-test-protocol-again` (commit-level provenance in that
  branch's `data/drop-tests/sobol-campaign/`); the `ajhby6` rows (99 drops,
  tested 2026-08-21, uploaded to Box 2026-08-24) were computed on 2026-08-24
  by running that branch's `drop_test_campaign_analysis.py` unchanged on the
  Box upload. The 2 warmup drops per specimen are discarded in both cases.
- `t3_prism_drop_count_sensitivity.py`: builds the table and figure below,
  and `--emit-truncated N` writes
  `t3-prism-bo-batch-drop-results-firstN.csv`, a campaign summary with
  round-1 statistics recomputed over the first N drops in the exact schema
  `t3_prism_bo_campaign.py --results` expects.
- `t3-prism-drop-count-sensitivity.csv` and
  `figures/t3-prism-drop-count-sensitivity.png`: the replay results.

Where the "2 warmup drops" come from, since the phrase has caused confusion:
it is an analysis-time convention, not a step performed at the drop tower.
`scripts/analysis/drop_test_campaign_analysis.py` on the PR #86 branch sets
`WARMUP_DROPS = 2` and computes every stabilized statistic over
`valid[2:]`, so the first two trigger-valid captures of each session are
recorded but excluded from the means (which is why `n_valid` reads 101
while this per-drop file holds 99 rows per specimen). The number 2 comes
from the burn-in section of `docs/drop-test-sample-size-analysis.md` on
that branch: hot-glue mounts drift for 5 to 10 drops, the wax key-seat
mount settles within about 2. The lab-floor practice (one test drop at the
start of a specimen, kept unless anomalous, per Marcus Madsen on PR #102,
2026-08-24) is a separate check and is unaffected: if that test drop is
captured and healthy it simply becomes the first of the two
analysis-discarded drops. For a short round-2 session, record 2 extra
drops (22 for a 20-drop target) so the stabilized window matches round 1,
or pass a matching `--warmup` to the analysis.

What the replay shows. The t180 ranking of all 8 tested specimens is
identical at N = 20, N = 50 and the full session; the worst first-20 t180
deviation is +0.008 (bag26v, which softens over its session) against
design-to-design gaps of 0.007 to 0.087, and the per-drop SEM at N = 20 is
still an order of magnitude below those gaps. The e_rebound fraction is the
fragile one: 7 of 8 specimens sit within 2.5 percent of their full-session
value at N = 20, but amdjwm lands 21 percent low because a burst of harder
rebounds arrives around drops 26 to 40, and the mid-pack e_rebound ordering
(four specimens within 0.003 of each other) shuffles under truncation.

How a short round 2 is accounted for in the pipeline. The BO ingestion
already computes noise as sd/sqrt(n_valid) from the results CSV, so a
20-drop session simply enters the model with about 2.2x the standard error
and the GP downweights it accordingly; nothing needs changing there. The one
thing that should change: because most specimens drift slightly over a
session, ingest round 1 through the matching `-firstN` truncated summary so
both rounds average the same early-session window and estimate the same
quantity:

```bash
python bo/t3_prism_drop_count_sensitivity.py --emit-truncated 20
python bo/t3_prism_bo_campaign.py --results bo/t3-prism-bo-batch-drop-results-first20.csv ...
```

## Round-2 drop data (the r2d2c prints, first sessions 2026-08-24)

Raw campaign data is uploaded manually to the shared Box folder
[`tensegrity-optimization`](https://byu.box.com/s/kkhmvnj9ni19b57dryk3gdroqrp5uf0b)
(public view/download link created by @sgbaird on PR #86, 2026-07-21),
subfolder `Drop Test Data`, one folder per session. Fetch a session with the
script copied from the PR #86 branch:

```bash
python scripts/fetch_box_shared_folder.py kkhmvnj9ni19b57dryk3gdroqrp5uf0b DEST
```

That downloads the entire share (videos included). To pull one session
folder, resolve its folder id from the share listing first; the ids used on
2026-08-24 were 411619211572 (`r2d2c1`), 411623696481 (`r2d2c2`),
411630638267 (`r2d2c3`), 411633263159 (`r2d2c4`), 411638730821 (`r2d2c5`),
411638799623 (`r2d2c6`), 411634427962 (`r2d2c7`), 411654362191 (`r2d2c8`),
411659610187 (`r2d2c9`), and 410920465434 (`ajhby6`).

Upload quirk worth knowing before re-analyzing: the `r2d2c8` session was
exported under a name ending in `_Signal9`, so on Box its TP4 series table
is `..._Signal9.csv` (which parses as a capture and crashes the pipeline)
and its 22 real captures are `..._Signal9_SignalN.csv` (which the pipeline
skips). Rename the table to something without `Signal` and strip the first
`_Signal9` from the capture names before running the analysis.

The BO round-1 plate (the second tested batch, designs `t3-prism-bo-round1.csv`
on the PR #35 branch) was removed and labeled `r2d2c1` through `r2d2c9` on
2026-08-24; masses with label were posted in issue #98 the same day. Files:

- `t3-prism-bo-round1-print-key.csv`: print ID to specimen/trial mapping for
  all nine articles, plus RH% and defect notes from the issue #98 print log
  as they are posted. The mapping is CONFIRMED as of 2026-08-24: @sgbaird
  posted photos of the removed prints on a numbered tabletop grid
  (positions 1 to 9 = `r2d2c1` to `r2d2c9`, laid out in the plate
  arrangement) together with a Bambu Studio screenshot anchoring the
  back-left plate object as Specimen 03, which pins the raster direction.
  That is the same back-left to front-right mapping the mass fit had
  inferred (residual sd about 0.5 g, uniform +0.3 g label offset, center
  cell `r2d2c5` = Specimen 08 unambiguous), so the photographic and
  mass-model evidence agree independently.
- `t3-prism-bo-round1-drop-results.csv`: campaign summary for all nine
  sessions (r2d2c1 to r2d2c9, uploaded 2026-08-24; 21 valid captures each,
  22 for r2d2c8; 19 to 20 scored after the 2-drop warmup discard), produced
  by the PR #86 branch `drop_test_campaign_analysis.py` unchanged. Same
  schema as `t3-prism-bo-batch-drop-results.csv` plus the three T-drift
  watch columns that script now emits (`t_drift_flag`,
  `t180_slope_pct_per_drop`, `t180_e2e_pct`). The `mass_g` column is the
  posted mass with label. The geometry columns (`R_mm`, `H_mm`,
  `twist_deg`, `strut_d_mm`, `cable_d_mm`) are **as-printed** dimensions,
  matching the `*_print_*` columns of `t3-prism-bo-round1-designs.csv` for
  the specimen's spec, not the Ax base coordinates. Reading them as base
  coordinates makes the spec mapping look wrong (one downstream analysis
  did exactly that); the print key is the authoritative specimen-to-spec
  map.
- `t3-prism-bo-round1-per-drop-metrics.csv`: the stabilized per-drop rows
  for those sessions (172 rows), same schema as
  `t3-prism-per-drop-metrics.csv`.
- `t3-prism-bo-round1-designs.csv`: the plate that was actually printed
  (`bo/t3-prism-bo-round1.csv` on the PR #35 branch, commit 8809b25).
  `R_mm`..`cable_d_mm` are the base coordinates of Ax trials 10 to 18; the
  `*_print_*` columns are the constant-solid-mass projection that went to
  the printer.
- `t3-prism-bo-round1-predictions.csv`: the suggestions CSV as it stood
  when that plate was generated (commit `7a048ee`), kept frozen so
  predicted-vs-measured is drawn against what the model actually claimed.

Session notes from the 2026-08-24 uploads: all captures in all nine
sessions are trigger-valid, no pauses, input Δv 5.29 to 5.41 m/s (healthy
band). One session, `r2d2c2`, breaks the historical within-session T-drift
envelope (+0.25 %/drop, +3.5 % end to end, output-side signature: mount or
coupling suspect); its t180 mean is drift-contaminated and its inflated sd
is what the BO ingestion sees. The `r2d2c1` folder name originally said
"23 drops" against 21 events in the TP4 series table and export; the folder
has since been renamed to "21 drops" on Box, so the name and contents now
agree. The session ID string inside every export still reads "101 drops"
(template reuse), which is cosmetic.

Print-log entries for all nine r2d2c articles were posted to issue #98 on
2026-08-24 (ronnie-guymon) and are folded into
`t3-prism-bo-round1-print-key.csv`: every article printed at ~11 % RH;
defects were limited to detached or "spaghetti" TPU tendon strings on
`r2d2c1` (two top tendons, plus an odd foot support), `r2d2c4` (one top
tendon, one piece about 1/4 detached), and `r2d2c8` (two bottom tendons,
full span); the other six printed clean.

### Round-2 outcomes and the round-3 batch

With all nine round-2 sessions in, the ingestion in
`t3_prism_bo_campaign.py` attaches both batches (18 tested articles: 9
round-1 including `bpx68c`, minus the unmapped `amdjwm`, plus 9 r2d2c) and
the two still-untested round-1 prints (specs 03 and 06) as pending. Run:

```bash
python bo/t3_prism_bo_campaign.py --round 2       # refit + round-3 batch
python bo/t3_prism_bo_campaign.py --measured-round2  # predicted-vs-measured
                                                     # figure set + animation
```

The first command writes `t3-prism-bo-suggestions-round2.csv` (the round-3
candidate batch at constant printed mass), the AxClient snapshot
`t3-prism-bo-ax-client-round2.json`, and
`figures/t3-prism-bo-round2-pareto.png`. The second renders the measured
predicted-vs-actual figure set (`figures/t3-prism-bo-round2-start.png`,
`-uncertainty.png`, `-predicted-vs-actual.png`, `-front-final.png`, plus
the MP4/GIF), the real-data version of the `-PROTOTYPE` set, which is kept
for provenance.

### Rebound energy divided by mass (the intensive objective)

`t3-prism-bo-objectives-mass-normalized.csv` tabulates both forms of the
rebound objective for every tested article (18 as of the full round-2
upload on 2026-08-24), with per-form Pareto flags against `t180`. Definitions: `e_reb_mJ = e_rebound * m * g * h`
(absolute energy returned to the payload per drop, the current BO
objective), and `e_reb_mJ_per_g = e_reb_mJ / m` (specific rebound energy,
the SEA-style intensive framing from PR #33). Because the absolute form is
built by multiplying the measured restitution fraction by the article's own
measured mass, dividing by that same mass recovers `e_rebound * g * h`
exactly: the per-gram objective is the raw restitution fraction rescaled by
the constant `g * h` = 14.95 mJ/g.

Findings from the measured data (unlike the simulated campaign on PR #33,
where the absolute form was 99.99% mass): the measured restitution fraction
spans 2.5x (CV 37%) while mass spans only CV 7%, so design signal dominates
either form; Pearson r between `e_reb_mJ` and mass is +0.18, dropping to
-0.03 after normalization; the two rankings agree at Spearman 0.89 with the
extremes identical. The Pareto front is where the choice matters. Over all
18 tested articles the absolute-form front is `6lhxfy`, `r2d2c7`, `r2d2c1`,
`r2d2c2`, `r2d2c6` and the per-gram front is `6lhxfy`, `r2d2c7`, `r2d2c1`,
`ajhby6`/`bpx68c`, `r2d2c6`; `6lhxfy`, `r2d2c7`, `r2d2c1` and `r2d2c6`
survive both framings (`r2d2c2` earns its absolute-form spot partly by
printing light, at 17.96 g).

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
