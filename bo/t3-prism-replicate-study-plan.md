# Replicate study plan: 3 designs x 9 articles (27 prints)

Status: **proposed picks, awaiting lab confirmation**. Plan and
pre-registration for the study described by @sgbaird on PR #102 on
2026-09-23, to be run by @achris0520, @me-madsen and @ctrhjk: three
characteristic designs (one on the Pareto front, one further away, one
furthest away), three copies of each per plate, three plates, 27 articles
total. Goals, in the lab's words: know whether there is signal, know
whether repeats will help the campaign, and check whether measured ranks
follow the predictions.

Everything quantitative here is frozen before any replicate article is
printed, so the rank check has a fixed target. Supporting analysis:
[`t3_prism_replicate_study_power.py`](t3_prism_replicate_study_power.py)
(reads only committed data), outputs
[`t3-prism-replicate-study-picks.csv`](t3-prism-replicate-study-picks.csv),
[`t3-prism-replicate-study-power.csv`](t3-prism-replicate-study-power.csv)
and [`figures/t3-prism-replicate-study-power.png`](figures/t3-prism-replicate-study-power.png).

## What the existing repeat data already says

The nine drran/2dran pairs (see the round-3 reprint section of
[`README.md`](README.md)) are the study's baseline, at n = 2 articles per
design:

- **t180**: between-print article sd 0.013 after removing a common +0.028
  batch shift, against design gaps of 0.01 to 0.03 within that batch. The
  within-batch rank did not survive the reprint (rank correlation +0.08
  over the nine pairs), not because t180 is noisy but because that batch's
  designs were too close together. One pair in nine was a gross artifact
  (drran7, 1.251 vs 1.029).
- **Rebound energy**: article sd 4.5 mJ against a design range of about
  4 to 18 mJ; pair rank correlation -0.18. At n = 1, rebound ranking is
  mostly noise.
- The current model's held-out design-level skill (round-5 LOGO-CV, 35
  design folds): rank correlation +0.08 on t180, -0.38 on rebound.

So the expected verdict is already visible in outline: t180 carries real
design signal when gaps are large, rebound needs repeats to be usable at
all. This study puts degrees of freedom behind those numbers and adds the
plate/session decomposition the pairs cannot give (drran and 2dran differ
by print batch and test day at once).

## Proposed designs

All three from round 4, which is what makes the study printable as three
identical plates: nozzle temperatures and volumetric speeds are filament
settings, one value per print job, so only same-round picks can all be
reproduced at their original process point (PLA 226 C at 29.5 mm3/s, TPU
236 C at 2.6 mm3/s). Per-part infills are per-article and pose no
constraint. STLs for all three already exist under
[`per-specimen-stls/`](per-specimen-stls/) (trials 37, 38, 39).

| role | article | trial | base R/H/twist/strut/cable | infill struts/cables | measured t180 | measured rebound (mJ) |
|---|---|---|---|---|--:|--:|
| on the front | corny7 | 37 | 40 / 78.2 / 79.0 / 10.46 / 3.0 | 22 / 21 % | 0.803 | 9.37 |
| further away | corny8 | 39 | 40 / 78.7 / 80.0 / 10.22 / 3.0 | 21 / 34 % | 0.954 | 17.54 |
| furthest away | corny2 | 38 | 25 / 110 / 40.0 / 10.92 / 5.5 | 18 / 34 % | 1.085 | 9.22 |

Why these three:

- **corny7** is the record attenuator and the anchor of the current
  design-mean front, and its 0.803 rests on one article and one
  accelerometer seating. Nine independent articles and seatings settle the
  standing question about the record, which is also the corner the round-5
  batch keeps a foot in.
- **corny8** is corny7's near twin in design space (same wide,
  high-twist, thin-cable family; the main coordinate difference is TPU
  infill, 21 vs 34 percent) yet measured 0.150 higher t180 and the largest
  rebound ever recorded (17.5 mJ). Twin coordinates with a large measured
  gap is exactly the pairing that separates design signal from article
  luck, and the held-out model says the gap should be near zero (see the
  reference table below). It is also the biggest rebound outlier, so its
  repeats are the single most informative rebound measurement available.
- **corny2** anchors the far end (worst clean t180 in round 4, tall
  low-twist family, no drift flag, complete channels). On the t180 axis
  the three sit at 0.80 / 0.95 / 1.09; note that by 2D distance from the
  front, corny8's rebound excess arguably puts it further out than corny2,
  so read "further/furthest" along the t180 axis.
- **Why not r2d2c3 (1.334) or drran7 (1.251) as the far pick**: both are
  suspected seat artifacts (drran7's own reprint measured 1.029), and both
  are from other rounds, so their original filament settings cannot
  coexist with corny reproductions on one plate. Testing whether those
  extremes replicate is a separate, cheaper re-seat exercise.

Alternates if the lab prefers: corny6 (0.911, on the front at the knee)
for the front pick; corny5 (1.088) instead of corny2, but it carries a
T-drift flag from its first session. Swapping picks only requires
re-running the power script and re-freezing the tables below.

## Pre-registered reference values

Three frozen references, because "does rank follow the predictions"
depends on which predictions. All values are on this branch as of
2026-09-23; per-article numbers in
[`t3-prism-replicate-study-picks.csv`](t3-prism-replicate-study-picks.csv).

t180, mean and 1 sd:

| reference | corny7 | corny8 | corny2 | ordering claimed |
|---|--:|--:|--:|---|
| measured first articles | 0.803 | 0.954 | 1.085 | corny7 < corny8 < corny2, gaps 0.150 / 0.131 |
| held-out model (round-5 LOGO-CV) | 0.978 +/- 0.085 | 0.972 +/- 0.134 | 1.050 +/- 0.071 | corny8 <= corny7 < corny2, first gap ~0.006 (a tie) |
| frozen round-4 acquisition | 0.934 +/- 0.131 | 0.954 +/- 0.153 | 1.008 +/- 0.147 | corny7 < corny8 < corny2, gaps 0.020 / 0.054 |

Rebound energy (mJ per drop), mean and 1 sd:

| reference | corny7 | corny8 | corny2 | ordering claimed |
|---|--:|--:|--:|---|
| measured first articles | 9.37 | 17.54 | 9.22 | corny8 highest; corny7 vs corny2 a tie (0.15 mJ) |
| held-out model (round-5 LOGO-CV) | 9.08 +/- 3.66 | 8.45 +/- 3.98 | 8.20 +/- 4.20 | no ordering claimed (flat within 1 sd) |
| frozen round-4 acquisition | 8.48 +/- 5.95 | 8.45 +/- 6.02 | 6.54 +/- 5.61 | no ordering claimed |

The three references agree that corny2 ranks last on t180 and disagree
about everything else, which is what makes the study informative:

- **If the first articles are design truth** (repeatability high), the
  reprint design means land near the measured row and the full t180
  ordering is recovered with probability ~1 at any n from 1 to 9.
- **If the held-out model is right** (the extremes were partly article
  luck), corny7 and corny8 come back statistically indistinguishable and
  the "measured" ordering reproduces only ~16 to 37 percent of the time.
- The discriminator is therefore **the corny7 minus corny8 design-mean gap**
  (its standard error at 9 articles per design is about 0.006), not the
  rank itself. In between, the study estimates the regression-to-the-mean
  coefficient directly.

## What a 3-design rank correlation can and cannot show

With three designs, Spearman's coefficient can only take the values 1,
0.5, -0.5 and -1, and a perfect rank occurs with probability 1/6 = 0.17
under random ordering, so even a perfect result cannot clear p = 0.05 on
its own. Report the rank agreement, but score the study on the
pre-registered endpoints below, which use the replicate means and their
standard errors instead of ranks. A secondary check with more resolution:
Spearman over all 27 articles against the pre-registered design values,
with a permutation p from shuffling design labels over articles.

## Power (from the measured pair noise)

Full table in
[`t3-prism-replicate-study-power.csv`](t3-prism-replicate-study-power.csv);
curves in the figure. Standard errors of a design mean, using the pair
noise and the fact that balanced plates cancel session/plate block shifts
out of design contrasts:

| n per design | t180 SE | rebound SE (mJ) | P(t180 ordering, measured truth) | P(t180 ordering, model truth) | P(corny8 rebound highest, measured truth) |
|--:|--:|--:|--:|--:|--:|
| 1 | 0.013 | 4.5 | ~1.00 | 0.37 | 0.84 |
| 3 | 0.008 | 2.6 | ~1.00 | 0.28 | 0.98 |
| 9 | 0.004 | 1.5 | ~1.00 | 0.16 | ~1.00 |

Notes. The corny7 vs corny2 rebound comparison (0.15 mJ apart as
measured) is an expected tie at any feasible n and must not be scored as
a rank success or failure. The t180 ordering resolves at n = 1 only
because the picks are spaced 10 sd apart by construction; the round-3
batch scrambled because its gaps were 1 sd. The variance-component
estimates themselves get within-cell df = 18, so the article sd comes
back with a 95 percent CI of roughly -25 to +48 percent, enough to set
the surrogate's observation noise honestly.

## Pre-registered endpoints

1. Variance components per objective from the nested fit
   (design, plate-within-design, article-within-plate): the fractions of
   article-level variance attributable to design vs print vs session.
2. The corny7 minus corny8 t180 design-mean gap, with 95 percent CI.
3. The corny8 rebound excess over the mean of corny7 and corny2, with CI.
4. Ordering agreement against each of the three frozen references, with
   the exact 1/6 null stated alongside.
5. The regression-to-the-mean slope: reprint design means against first
   article values, pooled with the nine drran/2dran pairs.

## Pre-registered decision rules for the campaign

- If the article sd on t180 confirms at or below about 0.015: keep one
  article per design in BO rounds, set the surrogate's observation noise
  to the article-level sd (not the per-drop SEM), and keep sessions
  balanced and reference-bracketed. Repeats then buy artifact protection
  (about 1 article in 20 has been a gross outlier so far), not precision.
- If the corny7 vs corny8 gap reproduces at 0.10 or more: the record
  corner is real design signal, TPU infill is a live t180 lever, and the
  round-5 corner allocation stands. If it collapses to 0.05 or less:
  single-article extremes stop being quoted as design truth, the front is
  re-ranked on design means only, and round 5 is regenerated with
  replicate-aware acquisition before printing.
- Rebound: if the article sd confirms near 4.5 mJ (expected), rebound is
  interpreted only at design-mean level with n of 3 or more, and
  single-article rebound values stop being quoted on fronts. This is the
  Edison ruling and the LOGO-CV result restated as a rule.
- Artifact rule: any article whose session mean sits more than 3 article
  sd from its design median gets an accelerometer re-seat and a 10 to 12
  drop re-run before it may be excluded; both sessions stay in the record.

## Protocol

Printing (required):

- One plate layout: three copies each of trials 37, 39, 38, printed three
  times. Identical print jobs: same file, the round-4 filament point (PLA
  226 C at 29.5 mm3/s, TPU 236 C at 2.6 mm3/s, no TPU preset swap
  needed), same spools if possible, RH noted per print.
- Per-part sparse infill per article: trial 37 struts 22 / cables 21,
  trial 39 struts 21 / cables 34, trial 38 struts 18 / cables 34 percent.
- Two routes to the file. GUI route: open
  [`slices/t3-prism-bo-round4.H2D-MM-PLAstruts-TPUcables.3mf`](slices/),
  delete trials 40 to 45, clone each remaining object twice, verify every
  clone kept its per-part infill overrides (select the part, the settings
  list must show "Sparse infill density"), auto-arrange, paint supports,
  slice. Or ask on PR #102 for a dedicated 9-object project; the plate
  generator needs a small change to accept duplicate designs. The mix
  (six articles at 77 to 78 mm footprint, three at 45 mm) is comparable
  to the round-4 plate, so one plate fits.
- Weigh and photograph every article. 27 masses at one filament point
  across three infill pairs is also the strongest mass-model validation
  set the campaign has had.

Labeling (required): corny7 and corny8 copies are visually near
identical. Photograph each plate with labels assigned before or at
removal, and record design, plate number (print job 1 to 3) and plate
position for every article ID in the print log. Three identical copies
per design per plate makes after-the-fact raster inference impossible,
so the photo-plus-log key is the only mapping that will exist.

Drop testing (required):

- 22 valid captures per article, so 20 score after the standard 2-drop
  discard. About three lab afternoons at the round-2 cadence.
- Interleave designs within each session block; do not test all copies
  of one design consecutively.
- Bracket each block with the same reference article (bpx68c, or one
  designated corny7 copy) so session drift is identifiable; log the
  accelerometer re-seat (wax bed plus tape) per article.

Optional but cheap: one 10 to 12 drop re-seat re-run of r2d2c3 in the
same campaign, which settles the other suspected seat artifact without
using any of the 27 slots.

## Sequencing against round 5

The round-5 print files (trials 55 to 63) are committed and
slice-checked, but this study is the better next print. Round 5's own
acquisition went humble after the reprint data (predicted t180 1.018 to
1.030 everywhere, no promised front improvement), the corny7 answer
decides whether the corner round 5 keeps a foot in is real, and the
noise numbers set the observation noise for the round-6 refit. If both
can print, print the replicate plates first and test their articles
first.
