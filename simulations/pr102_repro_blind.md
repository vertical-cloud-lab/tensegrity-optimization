# Blind reproduction of the BO-vs-baselines separation

Requested in PR #33 on 2026-08-25: reproduce the 2026-08-21 result in which the
simulation-only BO campaign clearly outperformed random, Sobol, Latin
hypercube, and compass search (final hypervolume 17.50 of an 18.024 reference,
against 10.9 to 14.5 for the baselines, Mann-Whitney p = 9.1e-5), with the
constraint that the reproduction be written **without reading the original
scripts**, and only afterwards compare against them to audit the
implementation. The target study is the one committed at `72f1989`
([pr102_baselines.py](pr102_baselines.py), [pr102_sim_campaign.py](pr102_sim_campaign.py)
as of that commit), which ran on the five-parameter PR #35 box with the
(t180, e_reb_mJ) objective pair and the era physics (before the tendon
semantics fix in `adf48b4`).

## Protocol

The blind reimplementation is [pr102_repro_blind.py](pr102_repro_blind.py). Its
specification came from exactly two sources: the PR #33 comment record, and
committed era **data** artifacts (result CSVs). The original scripts were
deleted from the working copy of the era tree before any work started, and the
blind script plus its complete results were committed (`1f30424`, `a7f3fb1`)
before either original was opened. The physics instrument is the era
`drop_tower_sim.evaluate_pr102` at `72f1989`, imported as a black box: its
call signature was discovered with `inspect.signature`, its source never
opened during the blind phase, and it was bit-verified by re-simulating 24
randomly sampled rows of the committed reference cloud (max deviation 1e-5 on
t180, which is the CSV's own 6-significant-figure rounding).

Details the record did not specify were declared as blind choices in the
script rather than guessed silently: the SEM convention attached to completed
trials, the compass-search mechanics, and the normalization inside the compass
scalarization.

## What could be pinned down before running anything

- The hypervolume convention: my independent 2-D routine reproduces the
  committed 18.024 reference ceiling on the committed front and matches the
  committed running-hv columns to 1e-4 (CSV rounding).
- The reference point (0.868168, 217.292) was recovered from data alone: it is
  exactly 1.05 times the componentwise worst of the nine printed articles'
  simulated objectives. The unblind read confirmed this is the original's rule
  (`REF_INFLATION = 1.05`).
- The Ax wiring: with `GenerationStep(SOBOL, num_trials=9,
  model_kwargs={"seed": seed})` and `AxClient(random_seed=seed)` (both
  disclosed in the PR thread), the blind campaign reproduces the era round-0
  Sobol draw digit for digit.

## Result: the separation reproduces

Ten seeds, 36 designs each (9 Sobol + 3 qNEHVI batches of 9), same fixed
reference point, era instrument.

| method | era final HV (10 seeds) | blind final HV (10 seeds) | era frac | blind frac | p vs BO |
|---|---|---|---|---|---|
| BO (qNEHVI) | 17.503 +- 0.250 | 17.511 +- 0.271 | 97.1% | 97.2% | - |
| compass | 14.490 +- 1.778 | 11.937 +- 2.080 | 80.4% | 66.2% | 9.1e-5 |
| Sobol | 11.816 +- 1.106 | 11.816 +- 1.165 | 65.6% | 65.6% | 9.1e-5 |
| Latin hypercube | 11.659 +- 1.541 | 11.659 +- 1.624 | 64.7% | 64.7% | 9.1e-5 |
| random | 10.860 +- 1.094 | 10.860 +- 1.153 | 60.3% | 60.3% | 9.1e-5 |

(The era standard deviations are population (ddof 0), the blind ones sample
(ddof 1); multiplying the blind column by sqrt(9/10) reproduces the era values
exactly for the three samplers.)

- **The three samplers reproduce to four decimals** because my blind generator
  guesses were the original's generators: `np.random.default_rng(seed)` (whose
  `random()` and `uniform()` draw identical streams, verified),
  `scipy.stats.qmc.Sobol(scramble=True, seed=seed)`, and
  `scipy.stats.qmc.LatinHypercube(seed=seed)`.
- **The BO reproduces to 0.05%** despite being independently rewritten and
  stochastic in its acquisition optimization: era 17.503, blind 17.511.
  Trajectory milestones at designs 9/18/27/36: era 51.3 / 95.9 / 97.0 / 97.1%
  of the ceiling, blind 51.3 / 95.5 / 97.0 / 97.2%. Per-seed finals span
  17.16 to 17.95 (era 17.18 to 17.96).
- **The separation statistic reproduces**: every baseline is completely
  separated from the BO across the two sets of ten seeds, p = 9.1e-5, the
  smallest value the one-sided Mann-Whitney U can return at n = 10 vs 10.

Figure: [outputs/repro_blind/repro_comparison.png](outputs/repro_blind/repro_comparison.png)
(blind trajectories with bands; blind vs era overlay, where the sampler traces
coincide exactly; final-HV dot plot per method, blind vs era).

## The one blind divergence: compass search, and why

My blind compass scored 11.94 +- 2.08 against the era 14.49 +- 1.78. The
record described it only as "compass (pattern) search with a halving step on a
normalized weighted sum, budget split over three weightings (0.15/0.5/0.85);
the seed sets the start and the axis order", which is not enough to pin the
mechanics. The unblind read found three differences, all in my
under-specified guesses (the scalarization and its normalization by the
reference point I had guessed correctly):

1. initial step 0.35 of each axis range (mine: 0.25);
2. a fresh random axis permutation every sweep, continuing through the
   remaining axes after an accepted move (mine: one fixed permutation, restart
   the sweep after every accepted move);
3. a step reset to 0.35 if the halving collapses it below 1e-3 (mine: none).

Re-running my variant with only the initial step corrected to 0.35 gives
12.79 +- 1.89, so the step size explains roughly a third of the gap and the
sweep mechanics the rest
([outputs/repro_blind/unblind_compass_ablation.csv](outputs/repro_blind/unblind_compass_ablation.csv)
has the per-seed values). As the definitive check, the **original**
`pr102_baselines.py` heuristic was re-run from the era tree in this fresh
environment: it reproduces its own ten committed per-seed CSVs
**bit-identically** (14.49003 +- 1.778).

## Unblind implementation audit, item by item

| aspect | blind choice | original (`72f1989`) | outcome |
|---|---|---|---|
| search space, param order | PR #35 box, 5 floats | identical literal | matched |
| round-0 Sobol wiring | `SOBOL` step + `model_kwargs={"seed"}` + `random_seed` | same, plus `min_trials_observed`/`max_parallelism` | draws match digit for digit; the extra kwargs do not affect the draw |
| model step | `BOTORCH_MODULAR`, default acquisition options | same, `max_parallelism=9` | matched (both Ax 0.5.0 defaults) |
| batching | `get_next_trials(9)`, complete each | same | matched |
| SEM on completion | `(value, 0.0)` per metric (noise known zero) | plain floats (SEM **unknown**, so the GP infers noise) | semantic difference, no measurable effect here (17.511 vs 17.503). Note the original docstring reads "noise is zero ... no SEM is attached", but in Ax an unattached SEM means *inferred*, not zero |
| budget | 36 fixed | `--rounds 3` at the run that produced the CSVs (script default is 4, i.e. 45) | matched as run |
| hypervolume + ref point | own routine + ref recovered from data | `hypervolume_2d` + 1.05 x printed-article worst | numerically identical |
| random baseline | `default_rng(seed).uniform` | `default_rng(seed).random` | identical streams, bit-equal results |
| sobol/lhs baselines | scipy qmc, seeded, scrambled | same calls | bit-equal results |
| compass | see above | see above | diverged; fully explained, original re-verified bit-identically |
| summary sd | ddof 1 | ddof 0 (numpy default) | cosmetic |
| Mann-Whitney | one-sided, greater | same | matched |
| CSV float format | full precision | `%.6g` | cosmetic |

## Verdict

The "BO clearly outperforms the baselines" result at `72f1989` is
**implementation-robust**: an independent reimplementation written from the
prose record alone, sharing only the physics instrument and the recorded
reference point, lands within 0.05% on the BO, to four decimals on the three
samplers, and reproduces the complete p = 9.1e-5 separation. The only
implementation-sensitive component is the compass baseline, whose exact
mechanics genuinely matter (2.5 hypervolume units between two reasonable
readings of the same one-line description); under either reading it stays far
below the BO, so the headline conclusion does not depend on it.

Two scope notes. First, this validates the *computation*, not the *objective*:
the era objective pair predates the tendon-semantics fix (`adf48b4`) and the
e_reb_mJ mass-proxy findings of 2026-08-22, so all of those caveats stand
unchanged; on the corrected, anti-correlated (t180, peak_tendon_strain) pair
the same BO legitimately does not separate from samplers, and both results can
be true at once because they describe different response surfaces. Second, the
baseline gap is exactly as the era write-up interpreted it: the front of the
concordant pair lives in a corner that space-filling designs cannot reach at
n = 36, and one model-driven batch does.

## Files

- [pr102_repro_blind.py](pr102_repro_blind.py): the blind script (frozen as
  committed in `1f30424`/`a7f3fb1`; the audit above lives here, not in edits
  to it)
- [outputs/repro_blind/](outputs/repro_blind/): `repro_bo_seed<k>.csv`,
  `repro_baseline_<strategy>_seed<k>.csv`, `repro_summary.csv`,
  `unblind_compass_ablation.csv`, `repro_comparison.png`
- Reproduce: extract the era tree (`git archive 72f1989 simulations | tar -x
  -C /tmp/era`), then
  `python simulations/pr102_repro_blind.py --era-dir /tmp/era/simulations`
  (about 25 minutes for the ten BO seeds on four cores), then
  `--aggregate-only` for figures.
