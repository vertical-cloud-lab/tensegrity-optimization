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
  seven documented deviations from the rendered template. From round 3 the
  search space also carries six print-process parameters, with the four
  filament-level ones taking one Sobol-drawn value for the whole batch; see
  the print-process section below. Run from the repo
  root: `python bo/t3_prism_bo_campaign.py --round 3`.
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
  bisection and no slicer in the loop. Since 2026-08-26 the two infill
  percentages are inputs to that solve rather than fitted constants, because
  a sparser article has to be larger to weigh the same. Residual sd 0.378 g, at or below the
  0.457 g print-to-print scatter, versus 0.927 g for a flat pair of density
  factors. `python bo/t3_prism_mass_model.py` prints the calibration report
  and re-projects the 9 round-1 articles.

- `t3_prism_slicer_settings.py`: reads the print-process settings back out of
  a Bambu Studio `.3mf` project (process profile, layer height, line width,
  sparse infill, wall loops, and per-filament nozzle temperature and max
  volumetric speed, plus any per-object or per-part overrides). It is what
  makes `AS_PRINTED_PROCESS` in the campaign script auditable rather than a
  hard-coded constant, and it is what round 4 should run on the round-3 plates
  to record what they were actually sliced at rather than what they were asked
  for. `python bo/t3_prism_slicer_settings.py bo/slices/*.3mf [--csv out.csv]
  [--raw]`.

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
match the geometry the suggestions CSV reports. The suggestions CSV already
carries the solved uniform `scale` per article, so the shorter path is to
render each design's SCAD at its own base coordinates and that scale and skip
the solve entirely; from round 3 the scale also depends on the article's strut
infill, so it cannot be recomputed from the shape alone.

### Print-process parameters, and why the filament settings are one value per batch

Six slicer settings became design variables on 2026-08-26 (PR #102). They had
been stock defaults nobody chose: both tested plates were sliced from Bambu's
`0.30mm Standard @BBL H2D 0.6 nozzle` process at 15 percent grid sparse infill,
2 wall loops, 0.30 mm layers and 0.62 mm line width, with PLA Basic at 220 C
and 30 mm^3/s and TPU 85A at 240 C and 2.5 mm^3/s. Those numbers are read
straight out of `Metadata/project_settings.config` in the two committed slicer
projects, and they are identical in both, so **all 17 tested articles sit at
one point of this six-dimensional space** and the round-3 batch is its
initialization rather than an optimization of it.

The bounds were tightened on 2026-08-31 (PR #102 review): the first draw of
the batch-wide filament settings landed at 247 C TPU at the high-flow
hotend's full 4.8 mm^3/s rating, which risked the #96 carbonization failure
and the untested flow ceiling in the same print. Every range now brackets
the proven operating point instead of reaching for the preset or hardware
limits. The original ranges (infill 10 to 60 %, PLA 200 to 235 C and 15 to
30 mm^3/s, TPU 230 to 250 C and 2.0 to 4.8 mm^3/s) are recorded here and in
the `PROCESS_SPECS` block so a later round can widen deliberately once one
round of process data exists.

| Parameter | Bounds | Set at | Slicer field | Why these bounds |
|---|---|---|---|---|
| `strut_infill_pct` | 12 to 35 % | 15 | sparse infill density, `-struts` part | brackets the stock 15; 35 keeps the printed-mass model near its one calibration point (its infill term is unvalidated differential physics) and keeps the constant-mass projection from shrinking dense articles onto the fixed-size sensor housings |
| `tpu_infill_pct` | 12 to 35 % | 15 | sparse infill density, `-cables` part | same range; still spans a soft to a firm captive core (the hollow lock ball photographed on issue #85) without leaving the mass model's comfort zone |
| `pla_nozzle_temp_C` | 212 to 228 C | 220 | PLA filament nozzle temperature | plus or minus 8 around the proven 220 (Bambu PLA Basic's own preset window is 190 to 240); cold plus fast risks underextrusion through the 0.6 nozzle, hot strings across the tendons, and neither failure needs to be found in a batch of test articles |
| `pla_flow_mm3_s` | 20 to 30 mm^3/s | 30 | PLA filament max volumetric speed | 30 is the vendor value both plates ran at and stays the ceiling; the floor is two thirds of it rather than the old half, so the batch cannot pair its coldest nozzle with a flow far from anything ever printed here |
| `tpu_nozzle_temp_C` | 235 to 245 C | 240 | TPU filament nozzle temperature | plus or minus 5 around the 240 both plates ran at (the generic Bambu TPU 85A @BBL H2D preset allows 200 to 250); the old 250 top was backed off because of the #96 hotend-carbonization history |
| `tpu_flow_mm3_s` | 2.2 to 3.6 mm^3/s | 2.5 | TPU filament max volumetric speed | 2.2 sits just below the 2.5 both plates ran at; 3.6 is 75 percent of the high-flow hotend's 4.8 mm^3/s rating (issue #96), so the round probes the new hotend's headroom without spending all of it in one go at an untested temperature |

Where those "set at" numbers come from, so they can be checked rather than
believed: `python bo/t3_prism_slicer_settings.py bo/slices/*.3mf` reads them
back out of the two committed slicer projects and writes
`t3-prism-slicer-process-settings.csv`. Both projects report the same process
profile and the same values on the two slots any object prints with (PLA on
extruder 1 at 220 C and 30 mm^3/s, TPU on extruder 2 at 240 C and
2.5 mm^3/s), and neither carries a single per-object or per-part override.
`slices/t3-prism-bo-round1.H2D-MM-PLAstruts-TPUcables_manual-supports.3mf` is
the r2d2c plate, posted to issue #98 on 2026-08-24 and byte-identical
(sha256 `4a7bc1a0…`) to the copy committed at `8809b25` on the
`copilot/get-bambu-sliced-print-t3-prism` branch; it is copied here so this
branch can be checked without fetching that one.

Two things the extractor turns up that are worth acting on independently of
the BO. The TPU slot still uses the `Bambu TPU 85A @BBL H2D 0.4 nozzle`
preset, left over from before the high-flow hotend went in on 2026-08-17, and
that preset caps the temperature window at 240 C; the generic
`@BBL H2D` preset allows 200 to 250, so the round-3 batch, which asks for
244 C, needs the preset swapped, not just the number typed. And the TPU had
been running at 2.5 mm^3/s on a hotend rated for 4.8, the headroom
@me-madsen noted on 2026-08-18; the round-3 draw lands on 3.6, so this batch
spends most of that headroom (75 percent of the rating) while holding some
back for a round that has seen 3.6 work.

Watch the top of the TPU temperature range in particular. Issue #96 traced a
multi-week printer outage to processing lubricant carbonizing in the hotend on
long hot TPU prints; that history is why the range now tops out at 245 C
rather than the preset's 250, and a plate near that top is still the one to
check mid-print for a flow taper.

**Speed is parameterized as max volumetric speed, not mm/s, because that is
the setting that binds.** The process profile asks for 200 mm/s on the outer
wall and 350 mm/s on sparse infill, which at 0.62 x 0.30 mm of extrusion is 37
and 65 mm^3/s: both materials already run flow-capped everywhere, so the mm/s
fields do nothing. Bambu Studio also has no per-material mm/s at all (speeds
belong to the process and are shared by both filaments), while the volumetric
cap is per filament. Every table reports the equivalent mm/s next to it
(`pla_speed_mm_s`, `tpu_speed_mm_s`), which is `flow / (0.62 * 0.30)`.

#### One filament setting for the whole batch

Two of the six can vary between articles on one plate and four cannot.

- **Article-level.** Sparse infill density is a per-object and per-part
  setting. Each specimen is one Bambu object holding a `<spec>-struts.stl`
  part on extruder 1 and a `<spec>-cables.stl` part on extruder 2 (confirmed
  in `Metadata/model_settings.config` of the committed project), so a per-part
  override addresses PLA and TPU separately. Without the override both parts
  inherit one global value, which is why neither had ever been chosen.
- **Filament-level.** Nozzle temperature and max volumetric speed are filament
  settings, and every object on a plate is built layer by layer through the
  same two nozzles. One print job carries one value of each.

The first version of this batch (commit `265bfe5`) bought within-round
variation on the four filament axes by splitting the batch across three
plates sliced at three different settings. On review (PR #102, 2026-08-31)
that split plot was replaced with the simpler design the batch now uses:
**one value of each filament setting for the whole batch.** Formally they are
the optimal predicted print parameters of the batch's best-predicted
specimen, applied everywhere; because all 17 tested articles sit at a single
point of the process space, an "optimal predicted" setting does not exist yet
and the values are drawn by Sobol sampling within the bounds instead (next
section). The best-predicted specimen is the candidate whose predicted means
add the most dominated hypervolume to the measured front at the reference
point (1.35, 15 mJ) used for the round-2 front-expansion numbers; when no
candidate's predicted means improve the front, which is the humble-model
case, the tie-break is the lowest predicted `t180`, the campaign's primary
endpoint per the Edison round-2 review. The `best_predicted` column in the
suggestions CSV and the recipe name it.

What this trades away, knowingly: the round learns nothing about the four
filament axes (one level of each), where the split-plot version bought three
confounded-with-plate levels. What it buys: one print job instead of three,
no plate-level confound inside the round, and a batch whose nine articles are
strictly comparable on shape and infill. Variation on the filament axes now
accrues across rounds instead of within one, which is why the draw comes from
a sequence (below) rather than an independent random point each time.

Plates are now nothing but floor space. Articles go onto as few plates as
they pack onto, chunked largest-first (with identical settings everywhere
there is no confound left for the deal to protect); the nine round-3 articles
fit one plate at about 218 x 218 mm of the usable 290 x 310 mm, so the batch
is one print job. A plate that does not fit is called out to be split rather
than quietly repacked. `--freeze-process` still pins all six parameters at
the as-printed point and gives back the shape-plus-mass batch of rounds 1
and 2.

#### Why Sobol and a Latin hypercube instead of the acquisition function

qNEHVI also returns values for these six parameters, and they are worth
nothing. With every observation at one process point the posterior is flat
along those axes, so the acquisition surface is flat too and whatever the
optimizer returns there is an artifact of its starting points. The run prints
the spread it produced before replacing it.

The replacement differs by level. The four filament settings are one point
drawn from a seeded scrambled Sobol sequence over their bounds: for a single
point that is a uniform random draw with a reproducible seed, which is all
"chosen" can honestly mean with no data to prefer one setting over another,
and Sobol rather than a plain RNG so that a later batch still lacking process
data continues the same sequence (batch N takes point N minus 3), keeping the
accumulated batch-level points spread out instead of clumping the way
independent draws can. The two infill densities are a centered Latin
hypercube across the nine articles, stratifying each axis into nine bins.
Every coordinate is rounded onto the slicer field's own resolution (1 C, 1
percent, 0.1 mm^3/s) so the number in the table is the number typed into
Bambu Studio, with no planned-versus-executed gap.

The run then re-queries the model at the delivered points and prints how much
the substitution moved its predictions, against the model's own posterior sd,
so the cost is measured rather than assumed. A GP cannot learn a response
from an input that never varied, so what is left along those six axes is the
SAAS prior's residual sensitivity, not evidence, and the substitution trades
a fraction of one posterior sd of prior noise for process coordinates the lab
can actually type. If a later round prints this number and it has grown a
lot, that is the signal that the model has begun to learn the process axes
from data, and the substitution should be dropped in favor of letting the
acquisition choose.

#### Infill feeds back into the printed-mass projection

Strut infill is not only a material property, it is a size lever. At a fixed
printed mass a sparser article has to be larger, so the projection in
`t3_prism_mass_model.py` now solves the scale given the infill: over the
tightened round-3 bounds (12 to 35 percent) the strut density moves the
solved scale by about -5 to +1 percent and the TPU density by under
1 percent (run `python bo/t3_prism_mass_model.py` for the sweep). Both terms
are differentials around
the 15 percent nominal, so at that setting the calibrated model is reproduced
exactly and every number it produced before is unchanged. Neither term has
been validated: no article has ever been printed at any other infill. **The
round-3 weighings are the first data that can check them, and they should be
fed back into the calibration before round 4.**

### Round-3 batch (the first with print-process parameters)

This is run 3 of the script, and it supersedes run 2. Both ingest exactly the
same 17 tested articles; run 2 produced a candidate batch on the six-parameter
space that was never printed, and run 3 produces the batch that is, on the
twelve-parameter space. That is why the physical batch number and the run
number are the same here and `--batch-number` exists: it names the batch in
the figure callout and the recipe title, and defaults to `--round` plus one,
which is only right when every previous run's batch went to a printer.

```bash
python bo/t3_prism_bo_campaign.py --round 3 --batch-number 3
python bo/t3_prism_bo_campaign.py --round 3 --batch-number 3 --plot-only \
    # redraws the Pareto panel, the process-space panel and the recipe from
    # the recorded CSV, no Ax install and no refit
```

The one option worth knowing about: `--freeze-process` gives back the
shape-plus-mass batch of rounds 1 and 2. The earlier `--plates` and
`--control-plate` options went away with the split plot (they set how many
filament levels the round bought, and there is now exactly one). One thing
that leaves uncovered, worth saying out loud: with a single filament level, a
round-level batch effect and the filament-setting effect are fully confounded
in this round's data. The control that remains is the one the Edison round-2
review recommended anyway, bracketing the drop sessions with a re-tested
reference article, which is independent of how the batch is sliced.

- `t3-prism-bo-suggestions-round3.csv`: the batch to print. One row per
  article: plate (floor space only), a `best_predicted` flag naming the
  specimen the batch-wide filament settings formally belong to, base shape
  coordinates, the constant `mass_printed_g` target, the six process
  coordinates (four of them identical on every row by construction) plus the
  two derived mm/s speeds, posterior-mean predictions for both objectives,
  and the as-printed geometry the constant-printed-mass projection produces
  at that article's own infill (`scale`, `*_print_mm`, `footprint_d_mm`,
  `solid_mass_g`) with PR #35's two printability checks evaluated on it.
  Violations are flagged, not dropped, the same as in rounds 1 and 2.
- `t3-prism-bo-round3-plate-recipe.md`: the same batch written as a print
  recipe. The filament settings stated once for the whole batch, per-part
  infill overrides and as-printed geometry per article, and a packing check
  per plate. This is the file to work from at the slicer.
- `t3-prism-bo-ax-client-round3.json`: full AxClient state. The nine delivered
  articles are attached as pending trials, so round 4 warm-starts from the
  batch that is actually going to the printer rather than from the raw
  acquisition output.
- `figures/t3-prism-bo-round3-pareto.png`: the objective-space view in the
  usual grammar, 17 tested articles and the 9 suggestions at their predicted
  means.
- `figures/t3-prism-bo-round3-process-space.png`: one strip per process
  parameter, showing the single black circle where all 17 tested articles
  sit, nine orange diamonds on each infill axis, and a single orange diamond
  on each filament axis (one value for the batch).

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

### Round-2 diagnostics and the LOOCV animation set

The same diagnostics re-run on the 17-article two-round fit (the
`t3-prism-bo-ax-client-round2.json` snapshot; `amdjwm` is still unmapped and
stays out):

    python bo/t3_prism_bo_diagnostics.py \
        --snapshot bo/t3-prism-bo-ax-client-round2.json --round 2 --cv-animation

writes the `*-round2-*` versions of every figure and table above, plus a
LOOCV figure set and animation in the same registered-still grammar as the
measured round-2 predicted-vs-actual set (`--cv-animation`; add
`--no-animation` for the stills alone, or re-render from the committed CSV
with `--plot-only --cv-animation --round 2`):

- `figures/t3-prism-bo-round2-loocv-start.png`,
  `-uncertainty.png`, `-predicted-vs-actual.png`, `-front-final.png`: four
  3300 x 2100 stills at 300 dpi, frames of one figure, so they register
  pixel-for-pixel on consecutive slides. Each article's held-out prediction
  (a model refit without that article) opens as an orange diamond, grows its
  +/- 1 sd bars and axis-aligned oval, freezes, then travels to the measured
  outcome and lands as the standard open black circle; the measured Pareto
  front then wipes in and the print IDs return. There is no prior-round
  layer (the predictions are the tested articles themselves), so the
  round-2 set's retire beat drops out.
- `figures/t3-prism-bo-round2-loocv-predicted-vs-actual.mp4` (+ `.gif`): the
  animated version, same beats. The uncertainty here is the same quantity as
  in the measured set (1 posterior sd of the noise-free objective), but from
  the held-out refit, so it is an honest out-of-sample bar rather than a
  training-point one.

Headline movement against the round-1 diagnostics: with 17 articles the
LOOCV rank correlation on rebound energy went from -0.14 (no skill) to 0.70,
and t180 sits at 0.60 with MAPE 5.4 percent, so the model now has genuine
out-of-sample ordering skill on both objectives. The round-2 batch that
landed systematically right of its t180 predictions is in the fit now, and
it shows: r2d2c3, which the pre-round-2 model missed by 5.8 sd, is a 2.7-sd
held-out miss for a refit that has seen the other round-2 articles, still
the worst t180 residual but no longer in a class of its own (the two
largest, r2d2c3 high and r2d2c6 low, are the two stiffest short-prism
designs, so that corner of the space is where the surrogate remains
weakest).

### Parity evolution (predictions before vs after the round-2 data)

The corrected form of the cross-validation figure request on PR #102: two
parity panels, one per objective, predicted on the vertical axis against
measured on the horizontal, showing where every tested article's prediction
stood before the round-2 sessions and where the refit trained on all
collected data puts it. Measured values never move, so all motion in the
animation is the model changing its mind.

    python bo/t3_prism_bo_diagnostics.py --parity-evolution              # ~4 min, 2 refits
    python bo/t3_prism_bo_diagnostics.py --parity-evolution --plot-only  # redraw from the CSV

Provenance of the two prediction sets, per article:

- **Before** is the model state that actually chose the printed plate:
  commit `7a048ee`'s AxClient (5 shape parameters, 7 articles in the fit),
  restored from git history as `t3-prism-bo-ax-client-plate-7a048ee.json`
  (`git show 7a048ee:bo/t3-prism-bo-ax-client-round1.json`). For the nine
  r2d2c articles the before values are `t3-prism-bo-round1-predictions.csv`
  verbatim, the frozen numbers the plate was generated from and the numbers
  every table on the PR #102 thread quotes. For the round-1 articles they
  come from a seeded refit of that snapshot, in sample for the seven
  articles that model had seen and out of sample for `ajhby6` (spec 07 was
  still a pending trial then). A fidelity check predicts the nine plate
  designs with the refit and compares against the frozen CSV; the run that
  produced the committed table agreed to within 0.024 on t180 and 1.4 mJ on
  rebound energy, 0.3 of the frozen sd on both, so the reconstructed and
  frozen numbers describe the same model.
- **After** is the round-2 snapshot's refit (6 parameters, 17 articles)
  predicting in sample at each article's own coordinates and weighed mass.
  In-sample parity is the point of this figure (the request was the refit
  trained on all collected data); the honest out-of-sample companion is the
  LOOCV set above, which shares the grammar.

Uncertainties, stated on the figure: vertical bars are 1 posterior sd of
the noise-free objective from whichever model owns the frame (before or
after), horizontal gray bars are the measured value's 1 SEM as ingested
(for rebound energy that includes the 0.457 g print-to-print mass scatter
in quadrature, which is why those are visible while the t180 SEMs are not).

Files, same registered-still grammar as every other figure set here (all
3300 x 2100 at 300 dpi, frames of one figure, no tight bounding box):

- `figures/t3-prism-bo-round2-parity-start.png`: the before state. Round-1
  articles are open black circles hugging the diagonal (in sample); the
  nine forecasts are orange diamonds, all below the diagonal on t180
  (measured landed 0.04 to 0.42 above forecast, the systematic optimism)
  and all above it on rebound energy (measured landed 0.9 to 5.8 mJ below).
- `figures/t3-prism-bo-round2-parity-shift.png`: every prediction has
  traveled vertically to the refit's value, ghost diamonds and dashed
  risers marking where each forecast stood; one before/after pair is named.
- `figures/t3-prism-bo-round2-parity-final.png`: the ghosts cleaned up,
  print IDs in. The refit describes all 17 articles to within 0.0002 on
  t180 and 0.03 mJ on rebound (in sample, as expected for a GP with
  per-drop SEMs this small; r2d2c3's forecast 0.910 +/- 0.073 now sits at
  1.333 against its measured 1.334).
- `figures/t3-prism-bo-round2-parity.mp4` (+ `.gif`): the animated version.
  Beats: hold on the before state, staggered vertical travel with the
  diamonds handing off to open circles, a named before/after hold, clean,
  rest with IDs.
- `t3-prism-bo-round2-parity-evolution.csv`: the full table (measured,
  before, after, 1 sd each, provenance flags per article and objective).

### LOOCV evolution (held-out skill, initialization data vs all data)

The corrected form of the parity-evolution request (sgbaird, PR #102): both
states are leave-one-out predictions, so the pair of plots is an
out-of-sample report card before and after the round-2 data rather than an
in-sample refit. The start state runs LOOCV over the initialization dataset
alone: the eight tested round-1 articles (seven mapped Sobol specs plus the
S0 reference `bpx68c`; `amdjwm` stays out, unmapped), each predicted by a
model refit without it on the other seven. The end state is LOOCV over all
collected data: 17 articles, each predicted by a model refit on the other
16. The model class, 6-parameter space, per-fold NUTS refit
(`refit_on_cv=True`) and MCMC settings are identical in the two states, so
a change in held-out skill is attributable to the added data.

    python bo/t3_prism_bo_diagnostics.py --loocv-evolution              # 8 init folds, ~5 min
    python bo/t3_prism_bo_diagnostics.py --loocv-evolution --plot-only  # redraw from the CSV

Two provenance rules keep the comparison clean:

- The end state is reused verbatim from the committed 17-fold LOOCV
  (`t3-prism-bo-round2-loocv.csv`, commit `83e137a`), so this figure and
  the LOOCV animation set quote identical numbers. Re-run
  `t3_prism_bo_diagnostics.py --round 2` first if the ingested data ever
  changes; the compute step raises if the two states' observed values
  disagree.
- The start state is not the old committed round-1 LOOCV
  (`t3-prism-bo-round1-loocv.csv`): that run predates `ajhby6` and used
  the 5-D space with mass as a tracking metric. Holding the model class
  fixed matters more here than matching the historical artifact, so the
  start state refits the current 6-D formulation on the eight round-1
  articles.

What the committed run says, per objective (LOOCV rank correlation and
MAPE; the left side of each arrow is the initialization state, n = 8, the
right side is all data, n = 17):

- **Rebound energy: the model learned.** Rank corr +0.24 to +0.70, MAPE
  29.3% to 23.6%. The improvement is not just the wider round-2 spread
  being easier to rank: restricted to the same eight round-1 articles, the
  all-data folds cut the median held-out residual from 2.37 to 1.78 mJ and
  raise the within-round-1 rank corr from +0.24 to +0.55.
- **t180: the added batch did not transfer.** Rank corr +0.76 to +0.60
  over the growing pool, and on the same eight round-1 articles the
  held-out median residual worsens from 0.015 to 0.036 while their
  internal ranking collapses (+0.76 to -0.10; seven of the eight measured
  values sit within 0.07 of one another, so that ordering is fragile).
  This is the base-coordinate representation shift the Edison round-2
  review flagged: the r2d2c batch measured systematically stiffer at
  comparable coordinates, so folds that include it pull the round-1
  backfits upward. Rank correlations at n = 8 swing by several tenths
  between NUTS realizations, so read directions, not decimals.

Files (registered stills, 3300 x 2100 at 300 dpi, frames of one figure, no
tight bounding box):

- `figures/t3-prism-bo-loocv-evolution-start.png`: the initialization-only
  LOOCV parity, the eight articles as orange diamonds with +/- 1 sd bars.
- `figures/t3-prism-bo-loocv-evolution-shift.png`: the same eight articles
  re-predicted under the all-data folds, ghost diamonds and dashed risers
  marking the initialization values; the round-2 articles are not on the
  panel yet.
- `figures/t3-prism-bo-loocv-evolution-final.png`: the all-data LOOCV
  parity, all 17 articles as open circles, print IDs in.
- `figures/t3-prism-bo-loocv-evolution.mp4` (+ `.gif`): the animated
  version. Beats: hold on the initialization LOOCV, staggered vertical
  travel with diamond-to-circle handoff, the nine round-2 articles fading
  in as their own beat, hold, clean, rest with IDs.
- `t3-prism-bo-loocv-evolution.csv`: the merged table (measured +/- SEM,
  initialization prediction +/- 1 sd where that state exists, all-data
  prediction +/- 1 sd, per article and objective).
- `t3-prism-bo-loocv-evolution-init.csv` + `-diagnostics.json`: the raw
  initialization-only folds, and both states' Ax cross-validation
  diagnostics.

Per-gram companion (`--per-gram`, display only, use with `--plot-only`):
the same set with every rebound-energy quantity (measured value and SEM,
both states' held-out prediction means and sds) divided by the article's
weighed mass, written as `-per-gram` tagged files next to the absolute
ones. As with the campaign figures, the measured quotient is exactly
e_rebound * g * h, the intensive form from the PR #33 notes, so no article
scores well by printing light; predictions divide by the same weighed mass
they were conditioned on. MAPE is invariant under the per-article division
(each article's relative error is unchanged), but the ranking is not, so
the rebound skill numbers on the panels are recomputed from the
transformed values with the same definitions as the committed absolute
diagnostics (verified to reproduce them exactly before transforming):
rank corr +0.02 (initialization only) to +0.68 (all data), against +0.24
to +0.70 in absolute mJ. The learning verdict is the same in both forms;
the initialization state merely starts even closer to no skill once the
printed-mass dividend is stripped out. The committed CSVs stay in absolute
mJ; the transform lives in `loocv_evolution_per_gram` and runs at render
time.

    python bo/t3_prism_bo_diagnostics.py --loocv-evolution --plot-only --per-gram

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

### Window extrapolation (round 2 projected to a full session)

The replay above asks what round 1 would have looked like short; this
analysis asks the reverse as well: what the round-2 short sessions (19 to 20
scored drops) would likely read at round-1 length, and whether any headline
claim depends on the choice of window. `t3_prism_drop_window_extrapolation.py`
computes, from the committed per-drop files only:

- `t3-prism-drop-window-ratios.csv`: per round-1 specimen, the ratio of the
  full-session mean to the first-19 mean, per objective ingredient. Pooled:
  t180 ratio 0.9985 (sd 0.0033, range -0.7 to +0.4 percent), e_rebound
  ratio 1.041 (sd 0.086), where the rebound spread is dominated by amdjwm's
  late burst (+26.7 percent; without it, 1.013 with sd 0.015). The round-1
  t180 ranking at 19 drops is preserved (Spearman +0.98; the one swap is
  ajhby6 vs bpx68c, first-19 means 0.00003 apart).
- `t3-prism-drop-window-extrapolation.csv`: each round-2 article's measured
  window mean times the pooled ratio, with a 1 sd band (ratio spread
  combined with the article's own SEM) and a min/max envelope. This is an
  estimate that assumes round-2 articles drift like round-1 articles did;
  it is analysis, not measurement, so it is not an ingestion file.
- `t3-prism-drop-window-front-robustness.csv`: Pareto membership for the 17
  mapped articles under three conventions: mixed (as committed), matched
  first-19 in both rounds, and full-equivalent (round 2 extrapolated). The
  round-2 core of the front (6lhxfy, r2d2c7, r2d2c1, r2d2c2, r2d2c6) is
  identical under all three; the window choice only decides whether the
  low-rebound round-1 anchors also sit on it (ajhby6 joins under matched
  first-19; ajhby6 and bpx68c both join under full-equivalent).
- `t3-prism-bo-batch-drop-results-first19.csv`: the matched-window round-1
  summary in the ingestion schema (19 is the modal scored count of the
  round-2 sessions; the guidance above used 20 before the sessions ran).
  This, not the extrapolation, is the file to feed a refit.
- `figures/t3-prism-drop-window-extrapolation.png`: both halves on one
  canvas.

Two conclusions worth carrying. The round-2 calibration verdicts do not
depend on the window: extrapolated to a full session, all nine articles
stay above their frozen t180 predictions and below their frozen rebound
predictions (6 of 9 stay below even at the +27 percent worst-case burst
envelope). And one claim does need a qualifier: "r2d2c1 strictly dominates
bpx68c" holds as committed and under matched windows, but r2d2c1's
extrapolated full-session rebound (6.21 mJ, sd 0.51) edges 0.03 mJ above
bpx68c's measured 6.18, so state that dominance as a short-window result.

```bash
python bo/t3_prism_drop_window_extrapolation.py            # all outputs
python bo/t3_prism_drop_window_extrapolation.py --no-figure
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

Every figure has a per-gram rendering: pass `--per-gram` with `--plot-only`
or `--measured-round2` and the outputs gain a `-per-gram` suffix
(`figures/t3-prism-bo-round2-pareto-per-gram.png` and the four-still
`-per-gram` set with its MP4/GIF). Measured values divide by the article's
weighed mass; predicted means and sds divide by the mass the model
predicted for the design when the plate was generated (round-3 suggestions
divide by their constant 20.23 g target). It is a display mode only: the
recorded CSVs and the BO fit stay in absolute mJ. The round-2 Pareto
figures (both forms) also draw the round-1 front as a faded gray line with
no markers, so the hypervolume gained by the newest batch reads visually.

## Round-1 vs round-2 session QC (operator comparison)

Round 2 was run on 2026-08-24 by a substitute crew (Ronnie, Sam, Andrew,
Tim) while the usual operators were away. `t3_prism_round_qc_comparison.py`
compares the two rounds on every channel the committed data supports that
is about the rig, the schedule, and session conduct rather than the
specimen designs. Outputs: `t3-prism-round-qc-comparison.csv` (one row per
session: schedule, cadence, pauses, input state, matched-window t180
stability) and `figures/t3-prism-round-qc-comparison.png` (4 panels).
Timestamps come from the per-drop `event_time` columns (UTC; the schedule
panel converts to Mountain time). Regenerate with
`python bo/t3_prism_round_qc_comparison.py` (seconds; pandas + matplotlib
only).

Headline findings, all from committed CSVs:

- The substitute crew reproduced the protocol faithfully. Same TP4
  configuration and export format, same auto-drop cadence (median
  inter-drop interval 41 to 45 s in both rounds), and a rig input state
  (delta-v 5.29 to 5.41 m/s, input peak 226.7 to 229.3 G) inside the
  healthy band of round 1's post-Aug-19 sessions. The round-2 rig state
  does not explain the systematic round-2 prediction misses.
- Round 2 is the most internally uniform session block in the project.
  Across-session input-peak spread is 2.6 G (round 1: 29.2 G) and delta-v
  spread is 0.12 m/s (round 1: 0.42). No session today was dv-health
  "settled" (round 1 had 4 of 9), and there is no settling trend across
  the nine back-to-back sessions, likely because short sessions put only
  ~190 captures on the mat in one afternoon versus 404 on Aug 20 alone,
  after which the mat visibly settled (session-mean delta-v fell from 5.45
  to 5.26 over that day and both next sessions flagged settled).
- Round 1 was itself heterogeneous: it spans five test days and two rig
  input eras. The Aug 13 and Aug 17 sessions (`bag26v`, `amdjwm`,
  `bpx68c`) ran ~20 G softer input than every session since Aug 19; the
  cause is not recorded in the data. `bag26v`, the spec-08 official
  article in the BO fit, is therefore the one round-1 result measured
  under a materially different input state.
- Session conduct today was cleaner: only 1 of 9 sessions contains a
  mid-session pause over 2 minutes (round 1: 4 of 9, up to 13 minutes),
  and turnaround between specimens was 9 to 35 minutes (the 35 was the
  deliberate stop after `r2d2c1` to upload and check with the usual crew
  remotely before continuing).
- The three least stable 19-drop windows ever recorded are all in round 2:
  `r2d2c2` (t180 CV 1.44%, monotonic drift, T-drift flagged), `r2d2c8`
  (CV 1.06%, downward drift, also the session with the pause, the extra
  capture, and the `_Signal9` export quirk), and `r2d2c3` (CV 0.85%, pure
  scatter, no drift). Round 1's matched-window maximum is 0.50%. The other
  six round-2 sessions are as stable as round 1's best (`r2d2c7` at CV
  0.085% is the most stable window in the dataset), so the anomalies
  cluster on specific sessions rather than affecting the batch uniformly.
  The re-test recommendations for `r2d2c2` and `r2d2c3` stand.
- What the timestamps cannot rule out: no round-1 article was re-run on
  Aug 24, so an output-side shift common to all of today's sessions
  (sensor mounting habits, mat restitution state at fixed input) is not
  excluded by data alone. A short re-run of `bpx68c` under current
  conditions remains the direct control.

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
