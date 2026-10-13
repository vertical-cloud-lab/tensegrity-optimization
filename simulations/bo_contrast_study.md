# Objective sets that resolve the BO vs uninformed-DOE contrast

**Script**: `bo_contrast_study.py`. **Outputs**: `outputs/bo_contrast/`.
**Physics**: the corrected drop-tower simulator (`drop_tower_sim`, dead-band
tendons, calibrated mat) on the constant-printed-mass shape-ratio manifold
(20.23 g target, four scale-free ratios), exactly the space and instrument the
strain-era campaign used.

## 1. Why this study exists

The 2026-08-24 full-effort study found constrained qNEHVI statistically
indistinguishable from random, Sobol and Latin-hypercube sampling on the
(t180, peak_tendon_strain) pair at a 45-design budget, while the earlier
concordant pair (t180, e_reb_mJ) had separated the BO from every baseline
completely (97 % of a dense-sweep ceiling against 66 % for Sobol at 36
designs). The difference is not the optimizer. It is the geometry the
objective pair induces over the search space: strain and t180 are
anti-correlated across the manifold (Spearman rho -0.82), so most of the
printable cloud already sits near that front and hypervolume is nearly free
for any space-filling design. A model can only show an advantage where the
front is hard to reach without one.

This study makes that dependence measurable, uses it to choose an objective
pair on which the modeling advantage is genuinely testable, and then runs the
established repeat protocol on the chosen pair. The result is a
multi-objective setting with a real trade-off in which Bayesian optimization
separates from uninformed design-of-experiments baselines, plus the
diagnostic that predicts when it will.

## 2. The cloud

One scrambled-Sobol sweep of 16,384 designs (seed 20260825, distinct from
every campaign seed) over the four ratio axes, each design evaluated once by
the corrected simulator (about 41 ms per design over 4 processes, 11 minutes
total). 9,738 designs (59.4 %) are geometry-printable (cable at or above the
3.0 mm bridging floor, envelope at or below 250 cm^3). One evaluation returns
every candidate observable at once (t180, t1000, peak tendon strain, tendon
energy, stroke, rebound, pulse, and the projected geometry), so the one cloud
prices every candidate objective pair. Saved whole as
`contrast_cloud_ratios.csv.gz`.

## 3. The screen

For each candidate pair, both objectives minimized, the screen fixes a
reference point at 1.05 times the componentwise worst over the feasible cloud
(the era's printed-article convention would put the reference point inside
the envelope range and silently delete the far end of that front from every
hypervolume, so the convention is cloud-derived here, fixed once, and shared
by every method and seed). It then draws 2,000 Monte-Carlo batches of 45
designs and asks what fraction of the pair's ceiling an *uninformed* batch
collects for free. Batches are drawn from the geometry-printable rows,
because the printability check is closed-form geometry any sampler gets
without a simulation; constraints that need the simulation (the strain cap
variant) still cost the draw and are masked out of the hypervolume.

| pair | objectives | rho | front spans (of feasible span) | near-front band share | free HV, 45-design DOE |
|---|---|---:|---|---:|---:|
| strain (control) | t180 + peak tendon strain | -0.82 | 85 % / 89 % | 4.5 % | 84.6 +/- 2.4 % |
| rebound (dead control) | t180 + e_rebound | +0.59 | 46 % / 60 % of a 0.9 % span | 0.9 % | 81.0 +/- 5.3 % |
| **envelope (chosen)** | **t180 + envelope volume** | **-0.60** | **77 % / 85 %** | **1.2 %** | **80.0 +/- 3.7 %** |
| stroke | t180 + stroke | +0.65 | 47 % / 14 % | 12.2 % | 86.5 +/- 5.0 % |
| strain_envelope | strain + envelope | +0.69 | 1 % / 2 % | 0.4 % | 91.5 +/- 4.3 % |
| envelope_straincap | envelope pair + strain <= 0.12 | -0.61 | 65 % / 64 % | 1.7 % | 85.9 +/- 2.9 % |

(Free-HV fractions in this table are against the cloud-only ceiling; the
campaign numbers below use the polished ceiling, which is about 2 % higher.)

**The selection rule, stated before the campaign ran**: exclude the two
controls; require the front to span a meaningful part of both objectives (a
genuine trade-off rather than a corner sliver); among the rest take the
lowest free hypervolume. `strain_envelope` fails the trade-off test (its
front collapses to 4 points spanning 1 to 2 % of either objective), `stroke`
has the highest free HV and the widest near-front band, and the strain-cap
variant gives away part of its ceiling to constraint-infeasible draws but
still frees more HV than the plain envelope pair. That leaves:

**minimize t180, minimize envelope volume, at constant 20.23 g printed
mass**, with the two printability bounds as outcome constraints.

Physically this is the lander packaging question from
`fair_evaluation_analysis.md`: the transmissibility a protective cell buys
against the stowed volume it costs, compared at equal printed mass. The best
t180 wants the widest, flattest article the build volume allows; the smallest
envelope wants a compact article that is necessarily stiff. Being
non-dominated at any given size requires the best *shape* for that size, so
the efficient set is a one-dimensional ridge through the four-dimensional
space (front parameter IQR 0.35 of range, against 0.18 for the strain pair:
the front *moves* through design space). A sampler has to land on the ridge
by luck; a model can trace it. The band share says the same thing from the
objective side: 1.2 % of the printable cloud is within 2 % of this front,
against 4.5 % for the strain pair.

## 4. Ceilings

`--reference PAIR` polishes the cloud front with Nelder-Mead from the best
cloud point under each of 15 weightings (about 2,000 extra evaluations per
pair). Polished ceilings: envelope 85.93 (cloud alone 84.02, +2.3 %), strain
0.06356 (+1.8 %). Fronts saved as `contrast_front_<pair>.csv`, polish
evaluations as `contrast_polish_<pair>.csv.gz`.

## 5. The strain-era runs, rescored against a ceiling

The era study had no reference sweep, so its no-separation finding was stated
in absolute hypervolume only. Rescoring the committed 45-design full-effort
runs (10 seeds each) against this study's strain reference point and polished
ceiling:

| method | final HV, % of strain ceiling |
|---|---:|
| BO (constrained qNEHVI, full effort) | 82.7 +/- 4.1 |
| Sobol | 79.9 +/- 2.1 |
| random | 79.6 +/- 4.0 |
| LHS | 78.9 +/- 2.6 |
| compass | 77.5 +/- 7.5 |

Everything sits in one overlapping 77 to 83 % band: the numeric form of "the
front is a band most draws already touch". (`bo_contrast_strain_era_rescored.csv`,
per-seed values in `_seeds.csv`.)

## 6. The campaign on the chosen pair

Protocol identical to the era studies: 10 independent seeds, each drawing its
own scrambled Sobol round 0 (the Sobol generator is seeded with the repeat's
own seed, and the round-0 batches are pairwise distinct across seeds), 45
designs (9 + 4 model batches of 9), constrained qNEHVI
(`Models.BOTORCH_MODULAR`) with the printability bounds as outcome
constraints. Acquisition at 8 restarts x 128 raw samples, the setting the
2026-08-24 paired study measured as statistically indistinguishable from the
Ax defaults on this simulator (Wilcoxon p = 0.92 over ten paired seeds).

Baselines at the same budget and seeds, in two modes: `plain` (the era
protocol: infeasible draws are evaluated and excluded from fronts and
hypervolumes) and `printable` (a stronger DOE than the era protocol:
candidates are rejection-sampled through the free geometric printability
check before any simulation is spent, so no sampler wastes budget on
unprintable designs; the compass search likewise skips unprintable probes
without charge). The headline comparison uses the stronger `printable` mode,
so the BO's margin is measured against the best uninformed practice, not
against baselines handicapped by the constraint.

### Results

Round-0 audit: all ten seeds drew pairwise-distinct Sobol batches, and their
round-0 hypervolumes span 40.2 to 54.9 (47 to 64 % of the BO's final), so
the repeats start far apart and converge rather than sharing a start.

Final hypervolume as a fraction of the polished ceiling (85.93), 45 designs,
10 seeds:

| method | final HV | % of ceiling | best t180 | best envelope (cm^3) | p vs BO |
|---|---:|---:|---:|---:|---:|
| BO (constrained qNEHVI) | 80.97 +/- 1.82 | **94.2 %** | 0.691 +/- 0.013 | 11.00 +/- 0.00 | - |
| random search | 68.91 +/- 2.21 | 80.2 % | 0.704 | 23.7 | 9.1e-5 |
| compass search | 67.98 +/- 4.34 | 79.1 % | 0.717 | 12.3 | 9.1e-5 |
| Sobol | 67.36 +/- 3.44 | 78.4 % | 0.703 | 20.8 | 9.1e-5 |
| Latin hypercube | 66.62 +/- 2.80 | 77.5 % | 0.699 | 25.2 | 9.1e-5 |

9.1e-5 is the smallest value a one-sided Mann-Whitney U can return at 10
against 10: the two sets of ten do not overlap for any baseline.  The worst
BO seed (91.2 %) beats the best seed of every baseline (85.4 %).  In the
weaker `plain` mode (the era baseline protocol, infeasible draws charged)
the samplers land at 72.5 to 75.1 %, so the free printability check buys
them 4 to 6 points and they still finish 14 points under the BO.

The Monte-Carlo screen predicted the uninformed result almost exactly
(78.2 % of the polished ceiling predicted, 77.5 to 80.2 % measured), which
is the point of the screen: the free-HV number is a property of the
objective geometry that can be measured for a few CPU-minutes before
anyone commits a campaign to it.

The mechanism is visible in the traces and the objective-space panel.
Through round 0 the BO sits at or below the samplers (its own round 0 is
an unfiltered Sobol draw).  The moment the model takes over the blue trace
breaks away and never re-crosses: the model walks the efficient ridge
(best shape at every size), while the samplers fill the box and touch the
ridge only where luck puts them.  The pooled scatter shows the BO's
evaluations lining the reference front along its whole length, including
resolving the 11.0 cm^3 minimum-envelope corner to three digits on every
seed, with every sampler's cloud sitting in the dominated interior.

Contrast with the strain pair under the identical protocol and convention
(section 5): there the BO's margin over the best sampler was 2.8 points of
ceiling with overlapping seed distributions; here it is 14.0 points with
none.  Same optimizer, same budget, same simulator, same manifold; the
only change is which two observables the campaign calls objectives.

## 7. Files

- `bo_contrast_study.py`: cloud, screen, reference polish, campaign,
  baselines, comparison, era rescore, headline figure
- `outputs/bo_contrast/contrast_cloud_ratios.csv.gz`: all 16,384 evaluations
- `outputs/bo_contrast/contrast_screen.csv`, `contrast_refs.csv`,
  `bo_contrast_screen.png`: the pair screen
- `outputs/bo_contrast/contrast_front_<pair>.csv`,
  `contrast_polish_<pair>.csv.gz`: ceilings
- `outputs/bo_contrast/contrast_bo_envelope_seed<k>.csv`: the 10 BO repeats
- `outputs/bo_contrast/contrast_baseline_<strategy>_<mode>_envelope_seed<k>.csv`:
  40 baseline runs per mode
- `outputs/bo_contrast/bo_contrast_envelope_comparison.png`,
  `_objective_space.png`, `_summary.csv`: the comparison
- `outputs/bo_contrast/bo_contrast_strain_era_rescored.csv` (+ `_seeds.csv`):
  the era rescore
- `outputs/bo_contrast/bo_contrast_headline.png`: both pairs side by side

Reproduce:

```bash
python bo_contrast_study.py --cloud 16384 --jobs 4
python bo_contrast_study.py --screen
python bo_contrast_study.py --reference envelope --jobs 4
python bo_contrast_study.py --reference strain --jobs 4
python bo_contrast_study.py --campaign envelope --seeds 0 1 2 3 4 5 6 7 8 9 --jobs 4
python bo_contrast_study.py --baselines envelope --jobs 4
python bo_contrast_study.py --compare envelope --era-contrast --headline envelope
```

## 8. Caveats

- The ceiling is a dense sample plus a local polish, not a proof of global
  optimality; methods are compared against the same fixed ceiling, so the
  relative statements do not depend on it being exact.
- The screen's free-HV number measures the search-space geometry, not any
  optimizer; the campaign is the test of whether the BO actually collects
  what DOE leaves.
- Objective values are simulated. Tier-C caveats from the earlier studies
  carry over unchanged (t180 cannot exceed about 1 because rigid struts
  cannot resonate); the envelope axis is exact geometry.
- The choice of pair optimizes the *benchmark's* ability to show a modeling
  advantage. That is the question this study was asked; whether envelope or
  strain is the right second objective for the bench campaign is a separate
  decision recorded in `pr102_sim_campaign.md` section 7.
