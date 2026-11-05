# LOGO-CV in the original six-parameter space, with and without simulation features, against dummy and off-the-shelf baselines

**The ask ([PR #121, 2026-11-05](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/121)):**
"Perform LOGO-CV with 256/512, with only the 6 (?) original parameters, not
the additional print parameters, and both with and without the simulations as
contextual features, and for both objectives. Show the same figures for the
dummy cases of: 'predict everything as the mean', using a hyperparameter-tuned
RFR or similar model, etc. I.e., some baselines for comparison."

Everything here is recomputed from the committed campaign record under the
one held-out protocol the manuscript's SI figure uses (leave-one-design-out,
35 design folds over 44 articles, reprint pairs held out together), by the
two scripts in this directory. Inputs and their provenance are in
[`data/README.md`](data/README.md); every number below is in
[`scores.json`](scores.json) / [`scores.csv`](scores.csv), and the full
scorecard tables are in [`scores.md`](scores.md).

## What "the original six parameters" are, and what was already on record

The fit space of rounds 1 and 2 was six parameters: the five shape
coordinates (`R_mm`, `H_mm`, `twist_deg`, `strut_d_mm`, `cable_d_mm`) plus
the article's weighed printed mass (`mass_printed_g`). Round 3 added six
print-process settings (two infill densities that vary per article, four
filament settings that take one value per batch), giving the twelve-parameter
space of the manuscript's figure. The audit branch
(`claude/cv-signal-audit-20260922`, PR #111) had already re-run the
leave-one-design-out CV at 256 NUTS samples / 512 warmup steps in the
six-parameter space (and in several other spaces, including the five shape
coordinates with and without the six #33 simulation features). Those runs
are vendored verbatim under `data/ax-runs/`. The one combination the request
needed that did not exist, **the six original parameters plus the six
simulation features**, was run here
([`rerun_logocv_six_param_sim.py`](rerun_logocv_six_param_sim.py), the
audit's featurization driver with a six-parameter base space; output in
`data/ax-six-sim/`, 35/35 folds, median 146 s per fold on one torch
thread, four workers). Before it ran, the same driver re-ran one archived
fold with no features and matched the committed predictions and covariances
exactly (maximum difference 0.0), so the stack installed here (Ax 0.5.0,
BoTorch 0.13.0, torch 2.15 CPU) reproduces the archived runs.

The simulation features are the six `sim_*` columns the audit chose before
looking at any held-out number: the Tier C and Tier B transmissibility
analogues, Tier C peak tendon energy and stroke, Tier B ringdown frequency
and damping, computed by the #33 simulators at the design's print geometry
with the design-mean weighed mass, so reprint twins share identical
features. They enter Ax as range parameters with bounds equal to the
observed range padded by ten percent, exactly as in the audit.

## The baselines

[`logocv_baselines.py`](logocv_baselines.py) fits scikit-learn models under
the identical protocol: the same 35 folds, the same 44 articles, the same
observed objective values (asserted equal to
`manuscript/data/t3-prism-bo-round5-logocv.csv`), the same feature values
Ax fitted (read from the full-NUTS checkpoint). Every hyperparameter is
chosen inside the fold by a 5-fold GroupKFold over the training designs, so
the held-out design never touches the choice.

| model | what it is | reported uncertainty |
|---|---|---|
| training mean | the mean of the training articles ("predict everything as the mean") | the training sd |
| print-session mean | the training mean of the held-out article's own print session (seed, r2d2c, drran, 2dran, corny). An oracle for the between-session offsets, not something a fitted model had access to | the within-session training sd |
| ridge (linear) | standardized inputs, ridge regression, alpha tuned over 10^-3 to 10^3 | inner-CV RMSE of the chosen alpha |
| k-nearest neighbours | standardized inputs, k in {1, 2, 3, 5, 7, 10}, uniform or distance weights | inner-CV RMSE |
| random forest (tuned) | 200 trees; max_features {0.33, 0.67, 1.0}, min_samples_leaf {1, 3}, max_depth {None, 4} | inner-CV RMSE |
| GP, ARD Matern (ML-II) | Matern-5/2 with one lengthscale per input plus a white-noise term, hyperparameters by marginal likelihood with restarts: the plain, non-sparse, non-Bayesian cousin of SAASBO | its own predictive sd, noise removed (what Ax reports for SAASBO) |

Two reading notes. The training-mean baseline's rank correlation is
mechanically negative under a leave-one-out protocol (removing a high
article lowers the training mean), so its rho_s carries no information;
what it provides is the MAPE floor and the R2_oos zero. R2_oos is
1 - SSE(model) / SSE(per-fold training mean), so a negative value means the
model is worse than predicting the mean.

## Results

Held out over 35 design folds (44 articles). rho_s is Spearman's rank
correlation between held-out prediction and measurement, with a two-sided
permutation p (20,000 shuffles); "design" is the same statistic over the 35
design means; R2_oos is against the per-fold training mean; "spread" is the
sd of the predictions over the sd of the measurements; "95% cov" is the share
of articles within 1.96 reported sd of the measurement. SAASBO rows are the
Ax runs at 256/512; the twelve-parameter SAASBO row is the manuscript's SI
figure.

**t180 (transmissibility)**

| feature space | model | MAPE | R2_oos | rho_s (p) | design rho_s | spread | 95% cov |
|---|---|--:|--:|--:|--:|--:|--:|
| 6 original (shape + mass) | SAASBO | 5.2% | +0.12 | +0.05 (0.73) | +0.06 | 0.47 | 84% |
| 6 original | training mean | 5.2% | 0 | mechanical | | 0.03 | 91% |
| 6 original | print-session mean | 6.0% | +0.02 | +0.03 (0.86) | +0.06 | 0.45 | 89% |
| 6 original | ridge | 5.2% | +0.17 | +0.51 (<0.001) | +0.53 | 0.55 | 93% |
| 6 original | k-nearest neighbours | 4.4% | +0.22 | +0.44 (0.003) | +0.49 | 0.69 | 93% |
| 6 original | random forest (tuned) | 4.5% | +0.40 | **+0.59 (<0.001)** | +0.63 | 0.60 | 93% |
| 6 original | GP, ARD Matern (ML-II) | 4.6% | +0.31 | +0.51 (<0.001) | +0.56 | 0.77 | 75% |
| 6 original + 6 sim | **SAASBO (new run)** | 5.4% | +0.02 | **-0.14 (0.37)** | -0.14 | 0.13 | 86% |
| 6 original + 6 sim | ridge | 5.2% | +0.19 | +0.54 (<0.001) | +0.58 | 0.65 | 89% |
| 6 original + 6 sim | k-nearest neighbours | 4.4% | +0.36 | +0.53 (<0.001) | +0.54 | 0.67 | 93% |
| 6 original + 6 sim | random forest (tuned) | 4.1% | +0.49 | **+0.65 (<0.001)** | +0.71 | 0.66 | 91% |
| 6 original + 6 sim | GP, ARD Matern (ML-II) | 5.2% | +0.16 | +0.41 (0.006) | +0.44 | 0.81 | 70% |
| 12 campaign | SAASBO (manuscript) | 4.8% | +0.12 | +0.32 (0.036) | +0.37 | 0.32 | 89% |
| 12 campaign | ridge | 5.4% | +0.09 | +0.41 (0.005) | +0.43 | 0.53 | 93% |
| 12 campaign | k-nearest neighbours | 4.7% | +0.25 | +0.52 (<0.001) | +0.58 | 0.71 | 95% |
| 12 campaign | random forest (tuned) | 5.0% | +0.33 | +0.52 (<0.001) | +0.58 | 0.67 | 93% |
| 12 campaign | GP, ARD Matern (ML-II) | 4.4% | +0.34 | +0.55 (<0.001) | +0.61 | 0.77 | 77% |

**E_reb (mass-weighted rebound, mJ per drop)**

| feature space | model | MAPE | R2_oos | rho_s (p) | design rho_s | spread | 95% cov |
|---|---|--:|--:|--:|--:|--:|--:|
| 6 original (shape + mass) | SAASBO | 43.6% | -0.37 | -0.42 (0.005) | -0.31 | 0.37 | 84% |
| 6 original | training mean | 37.9% | 0 | mechanical | | 0.03 | 93% |
| 6 original | print-session mean | 38.9% | -0.11 | -0.20 (0.18) | -0.07 | 0.32 | 86% |
| 6 original | ridge | 36.2% | +0.10 | +0.28 (0.064) | +0.25 | 0.41 | 91% |
| 6 original | k-nearest neighbours | 37.2% | 0.00 | +0.23 (0.14) | +0.14 | 0.41 | 89% |
| 6 original | random forest (tuned) | 40.5% | -0.08 | +0.13 (0.39) | +0.10 | 0.34 | 89% |
| 6 original | GP, ARD Matern (ML-II) | 36.2% | +0.05 | +0.24 (0.12) | +0.17 | 0.32 | 36% |
| 6 original + 6 sim | **SAASBO (new run)** | 43.5% | -0.30 | **-0.71 (<0.001)** | -0.67 | 0.30 | 89% |
| 6 original + 6 sim | ridge | 35.1% | +0.13 | +0.35 (0.021) | +0.33 | 0.38 | 91% |
| 6 original + 6 sim | k-nearest neighbours | 38.7% | -0.06 | +0.06 (0.72) | -0.07 | 0.38 | 91% |
| 6 original + 6 sim | random forest (tuned) | 35.8% | +0.04 | +0.20 (0.19) | +0.18 | 0.39 | 91% |
| 6 original + 6 sim | GP, ARD Matern (ML-II) | 35.9% | -0.02 | +0.21 (0.17) | +0.12 | 0.39 | 34% |
| 12 campaign | SAASBO (manuscript) | 38.8% | -0.05 | -0.40 (0.008) | -0.30 | 0.11 | 93% |
| 12 campaign | ridge | 34.9% | +0.10 | +0.37 (0.014) | +0.41 | 0.47 | 91% |
| 12 campaign | k-nearest neighbours | 39.6% | -0.05 | +0.14 (0.36) | +0.09 | 0.49 | 89% |
| 12 campaign | random forest (tuned) | 35.9% | +0.08 | +0.27 (0.082) | +0.41 | 0.39 | 91% |
| 12 campaign | GP, ARD Matern (ML-II) | 33.9% | +0.18 | +0.41 (0.006) | +0.46 | 0.47 | 57% |

![t180 comparison grid](figures/logocv-grid-t180.png)

![E_reb comparison grid](figures/logocv-grid-e_reb_mJ.png)

The SI-style figure for each run is `figures/logocv-<model>-<space>.png`
(for example [`logocv-saasbo-six-sim.png`](figures/logocv-saasbo-six-sim.png),
[`logocv-rf-six.png`](figures/logocv-rf-six.png),
[`logocv-mean-six.png`](figures/logocv-mean-six.png)).

### Reading

- **In the six-parameter space the inputs carry a usable t180 signal, and
  SAASBO is the one model that does not use it.** On identical folds,
  inputs and targets, SAASBO ranks held-out t180 at +0.05 while ridge,
  k-nearest neighbours, the tuned random forest and a plain ARD GP rank it
  at +0.44 to +0.59 (random forest: R2_oos +0.40, MAPE 4.5%, design-level
  rho_s +0.63). The audit's explanation stands: the weighed-mass input is a
  print-session label in physical units, and the SAAS sparsity prior leans
  on it. The marginal-likelihood GP in the same space switches mass nearly
  off (median ARD lengthscale 6.3 on standardized inputs, against 0.1 for
  cable diameter) and rides the cable-diameter gradient instead
  (`data/baselines/gp-lengthscales.json`).
- **Appending the six simulation features hurts SAASBO and helps the
  forest.** SAASBO goes from +0.05 to -0.14 on t180 and from -0.42 to
  -0.71 on E_reb, the inversion the audit saw in the shape-only space
  (relevance diluted across six proxies of the same coordinates). The
  random forest goes from +0.59 to +0.65 (R2_oos +0.49, MAPE 4.1%), ridge
  from +0.51 to +0.54, the ARD GP falls to +0.41. For a tree ensemble the
  features act as pre-computed nonlinear transforms of the geometry; for a
  sparse GP they are collinear competitors.
- **The manuscript's twelve-parameter SAASBO (+0.32) is not the ceiling of
  the record.** In that same space the GP (ML-II) reaches +0.55, the forest
  and k-nearest neighbours +0.52, ridge +0.41. The gain over the twelve
  parameters is between-session calibration (the four filament settings
  are batch labels), which the shape-only baselines reach without it.
- **E_reb has no real held-out skill in any model.** The best R2_oos is
  +0.18 (GP, twelve parameters) and the best ranking +0.41 (same run,
  p 0.006) with ridge at +0.35 to +0.37; the random forest and k-nearest
  neighbours are at or below the mean in R2_oos. SAASBO is anti-correlated
  in every space and worse than predicting the mean (R2_oos -0.05 to
  -0.37), with the six-plus-sim run the most inverted of the set (-0.71).
  The MAPE floor of the mean predictor is 37.9%; the best model reaches
  33.9%. This is the metric the reprint pairs already showed to be
  noise-floored.
- **Dummies.** Predicting the mean gives t180 MAPE 5.2% and E_reb MAPE
  37.9%, which the SAASBO runs beat by at most 0.4 points and the forest by
  1.1 points. The print-session mean adds nothing (R2_oos +0.02 and -0.11),
  so the session offsets alone are not what the baselines are exploiting.
- **Uncertainty.** SAASBO's posterior sd covers 84 to 93% of articles at
  1.96 sd, honest but with a prediction spread of only a tenth to a half
  of the data sd. The ML-II GP's noise-free predictive sd is overconfident
  (70 to 77% on t180, 34 to 57% on E_reb). The inner-CV RMSE bars of the
  point models cover 89 to 95%, as a correctly sized constant error should.

### Caveats

- 44 articles and 35 designs. Every row is one realization: the audit's
  NUTS-budget experiment moved SAASBO's t180 rho_s by 0.24 with nothing but
  the sampler budget changed, and the forest and GP would move with their
  seeds and inner folds too. Differences under about 0.2 in rho_s between
  rows should not be ranked; the gap between SAASBO (+0.05, -0.14) and the
  baselines (+0.44 to +0.65) in the six-parameter spaces is larger than
  that, the differences among the baselines are not.
- This table holds 36 held-out model-by-space-by-objective numbers; quoting
  its best cell is optimistic in the usual way.
- The baselines fit the per-article objective means unweighted; SAASBO
  uses the per-article SEMs as known noise. For t180 the SEMs (0.0004 to
  0.003) are far below the between-print scatter, so this changes little;
  for E_reb they are also small relative to the design spread.
- The simulation features of a held-out design are computed from its
  geometry and design-mean weighed mass, which is what a candidate could
  provide before printing (the audit found the four non-ringdown channels
  insensitive to the within-design mass choice).
- The print-session mean uses session labels no fitted model had; it is a
  reference line, not a candidate model.

What this suggests for the manuscript: the held-out t180 skill reported for
the surrogate (rho_s +0.32 in the twelve-parameter space) is a fact about
the SAASBO surrogate with weighed mass as an input, not the ceiling of the
data, since simpler models on the same folds reach +0.5 to +0.65. Whether
that belongs in the SI next to the LOGO figure is the authors' call; the
grid figures above are drawn to drop in.

## Files

- [`rerun_logocv_six_param_sim.py`](rerun_logocv_six_param_sim.py): the Ax
  driver (variant `six-sim`; `six-param` and the audit's variants are
  available for reproduction checks).
- [`logocv_baselines.py`](logocv_baselines.py): the article table, the
  baselines, the scorecard and the figures.
- [`scores.json`](scores.json), [`scores.csv`](scores.csv),
  [`scores.md`](scores.md): the scorecard for every run.
- [`data/`](data/README.md): vendored Ax runs, the new run, the article
  feature table, the baseline predictions (campaign CSV layout) and the
  hyperparameters each fold chose.
- [`figures/`](figures/): `logocv-<model>-<space>.png`, the SI figure for
  each run, and `logocv-grid-t180.png` / `logocv-grid-e_reb_mJ.png`, the
  comparison grids.

## Reproduce

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install "ax-platform==0.5.0" scikit-learn matplotlib pandas scipy
git archive bbf7a62 bo | tar -x -C /tmp/campaign        # campaign code and snapshot
for i in 0 1 2 3; do
  python analysis/logocv-baselines/rerun_logocv_six_param_sim.py \
      --campaign-bo /tmp/campaign/bo --variant six-sim --queue --threads 1 &
done; wait
python analysis/logocv-baselines/rerun_logocv_six_param_sim.py \
    --campaign-bo /tmp/campaign/bo --variant six-sim --assemble
python analysis/logocv-baselines/logocv_baselines.py --build-table --fit --score --plot
```
