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

RESULTS_PLACEHOLDER

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
