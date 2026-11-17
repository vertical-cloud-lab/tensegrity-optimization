# Synthetic control for the BO-vs-DOE benchmark harness

The physics study (`bo_contrast_study.md`) reports that constrained qNEHVI
reaches 94.2 % of a dense-sweep hypervolume ceiling on the
`t180` + `envelope_cm3` pair while every uninformed baseline lands at 77.5 to
80.2 %, and that the identical code on the `t180` + `peak_tendon_strain` pair
is statistically indistinguishable from random search. That contrast is only
worth reporting if the harness itself is sound, so this module
(`synthetic_bo_benchmark.py`) re-runs the *same* harness on analytic problems
whose answers are known in advance.

Everything that could differ between the two studies is held fixed: the
generation strategy (9-design Sobol round 0 seeded with the repeat's own seed,
then `BOTORCH_MODULAR` at 8 restarts x 128 raw samples), the 45-evaluation
budget, the ten seeds, the four baselines (uniform random, scrambled Sobol,
scrambled Latin hypercube, compass search), the hypervolume routine, the
reference-point rule, the Nelder-Mead polish of the reference set, and the
statistical comparison.

## The problems

| problem | objectives | dim | why it is here |
|---|---|---|---|
| `branin` | minimize Branin | 2 | known global minimum 0.397887. A working BO must beat random search by a wide margin, or nothing downstream survives |
| `branin_negated` | minimize (Branin, -Branin) | 2 | every point in the domain is Pareto optimal by construction. The intended negative control |
| `branin_currin` | minimize (Branin, Currin) | 2 | the standard 2-objective benchmark, a genuine curved trade-off |
| `branin_currin_c` | same, plus disk constraint | 2 | BoTorch's `ConstrainedBraninCurrin` feasibility disk, given to Ax as an outcome constraint. The only synthetic that exercises the constraint plumbing the physics study depends on |
| `branin_currin_4d` | same, 2 nuisance axes | 4 | search dimension matched to the physics study's four shape ratios |

One convention had to be generalized. The physics study inflates the
reference point as `1.05 * worst`, which is only monotone for positive
objectives (it holds there: `t180` and `envelope_cm3` are both positive). The
negated-Branin objective is negative, where that rule moves the reference
point the wrong way, so this module uses the sign-safe
`worst + 0.05 * (worst - best)` over the feasible cloud, which coincides with
the study's rule whenever the best value is zero.

## Result 1: the harness is sound

`branin`, 10 seeds, 45 evaluations, simple regret against the analytic
optimum:

| method | median regret | geometric-mean regret | exact one-sided p vs BO |
|---|--:|--:|--:|
| BO (qNEHVI) | **0.0014** | 0.0019 | |
| compass search | 0.0016 | 0.0031 | 0.37 |
| Latin hypercube | 0.62 | 0.68 | 5.4e-6 |
| Sobol | 1.00 | 0.68 | 5.4e-6 |
| random search | 1.31 | 1.04 | 5.4e-6 |

BO is roughly 450 to 900 times closer to the optimum than any space-filling
design, with 10 of 10 paired wins. Compass search ties it, which is the
correct behaviour: pattern search on a smooth two-dimensional function at 45
evaluations is genuinely competitive, and a harness that showed BO crushing
compass search here would be the suspicious result, not the reassuring one.

On the four multi-objective problems the same harness gives BO the expected
advantage every time:

| problem | BO | Sobol | LHS | random | compass | exact MW p | paired wins |
|---|--:|--:|--:|--:|--:|--:|--:|
| `branin_negated` | 96.9 % | 84.7 % | 82.3 % | 83.2 % | 88.4 % | 5.4e-6 | 10/10 |
| `branin_currin` | 99.9 % | 88.2 % | 83.7 % | 86.4 % | 84.0 % | 5.4e-6 | 10/10 |
| `branin_currin_c` | 96.6 % | 92.2 % | 91.3 % | 90.8 % | 91.5 % | 7.5e-4 | 9/10 |
| `branin_currin_4d` | 99.8 % | 84.6 % | 84.8 % | 89.9 % | 80.2 % | 5.4e-6 | 10/10 |

(fraction of the reference-set hypervolume, mean over 10 seeds.)

Two readings worth keeping. The constrained problem is where BO's margin
narrows most (4.4 points against 11.7 unconstrained), which matters because
the physics study is constrained. And the nuisance-axis problem costs the
samplers more than it costs BO, which is the expected direction: quasi-random
stratification degrades with dimension and a GP with per-axis lengthscales
largely ignores an inactive axis.

## Result 2: the metric can hide the effect

On `branin` the hypervolume fraction reads 0.99998 for BO and 0.9959 for
random search. That is a 0.4-point difference standing in for a 700-fold
difference in simple regret. For a single objective, hypervolume against a
distant reference point is mostly a constant offset, and the interesting part
is the last fraction of a percent.

This is a caution about the reported statistic rather than a defect: whenever
a reference point sits far outside the region of interest, most of the
hypervolume is baseline offset shared by every method, and differences
compress. The physics study's reference point is 1.05 times the worst feasible
value, so it is close to the data rather than far outside it, but "fraction of
ceiling" should always be read next to the raw objective values.

## Result 3: the degenerate control did not behave as predicted

The `(f, -f)` pair was included as a negative control on the expectation that
if every point is Pareto optimal then the front is free and BO has nothing to
find. That expectation was wrong, and it was wrong for a reason worth
recording.

Every one of the 16,384 cloud points is non-dominated (`n_front` = 16405
including the polish), and the near-front share is 100 %. Yet BO reaches
96.9 % of the reference set while the samplers reach 82.3 to 84.7 %, with
complete separation. The reason is that hypervolume on an anti-diagonal front
is dominated by the *extremes*: the set that maximizes it contains the global
minimum and the global maximum of Branin, and finding those is exactly a
single-objective search problem, which is exactly what BO is good at. Being
on the front is free; being at the end of it is not.

The practical consequence for the physics study is the next result.

## Result 4: free hypervolume bounds the DOE level but does not fix the gap

The Monte-Carlo screen that chose the physics study's objective pair
estimates the fraction of the reference hypervolume an uninformed 45-design
batch collects. Run on these five problems it is a good predictor of where
the *baselines* land, as it was on the physics simulator. It is not a
predictor of the BO-minus-baseline gap:

| problem | free HV | BO | best baseline | gap (points) |
|---|--:|--:|--:|--:|
| `branin` | 99.6 % | 100.0 % | 100.0 % | 0.0 |
| physics `t180` + envelope | 80.0 % | 94.2 % | 80.2 % | 14.0 |
| `branin_negated` | 83.3 % | 96.9 % | 88.4 % | 8.5 |
| `branin_currin_4d` | 84.4 % | 99.8 % | 89.9 % | 9.9 |
| `branin_currin` | 84.6 % | 99.9 % | 88.2 % | 11.7 |
| physics `t180` + strain | 84.6 % | 82.7 % | 79.9 % | 2.8 |
| `branin_currin_c` | 89.7 % | 96.6 % | 92.2 % | 4.4 |

Two rows sit at a free hypervolume of 84.6 % with gaps of 2.8 and 11.7
percentage points. So free hypervolume answers "how well will an uninformed
batch do", which is what it was built for, and does not answer "how much
better can a model do", which depends on how learnable the response is. The
physics write-up should claim the first and not the second.

## Result 5: independent audit of the scoring

`--audit` re-derives the three things the reported contrast depends on and
that a reader should not have to take on trust. Run against both this control
and the physics study's committed CSVs:

| check | synthetic (200 runs) | physics envelope pair (50 runs) |
|---|---|---|
| hypervolume vs BoTorch's exact `Hypervolume` | max relative disagreement 3.6e-8 | 1.6e-6 (CSV rounding at `%.6g`) |
| evaluations per run | 45 for every method and seed | 45 for every method and seed |
| identical round-0 batches across seeds | none | none |

The hypervolume routine, the budget accounting, and the per-seed
initialization are all clean.

## Result 6: two corrections to the physics write-up, both confirmed here

**The reported "ceiling" is not a ceiling.** It is the dense cloud plus a
Nelder-Mead polish, and the campaign found feasible points beyond it.
Rebuilding the denominator from the union of the cloud, the polished front,
and every feasible evaluation of every method gives 87.086 against the
reported 85.929, a 1.35 % increase. On that denominator BO is at 93.0 % and
the best printable baseline at 79.1 %. The separation is unchanged, but the
number should be called a best-known reference hypervolume, not a ceiling.
Notably the BO's own evaluations contribute 1.137 of the 1.157 increase while
all 40 baseline runs together contribute 0.121, which is what makes the
original denominator flattering rather than neutral.

**`9.13e-5` is not the floor of a 10-vs-10 Mann-Whitney test.** It is SciPy's
asymptotic approximation, which `method="auto"` selects above n = 8. The exact
one-sided value under complete separation is `1 / C(20,10)` = **5.41e-6**.
Every p-value in this module is now computed with `method="exact"`, and the
paired exact Wilcoxon (the more appropriate test, since seeds are matched
across methods) is reported alongside: 9.77e-4 with 10 of 10 paired wins,
which is that test's own floor at n = 10.

## What this control cannot do

It validates the harness, not the physics. It cannot say whether the
tensegrity simulator is right, whether the six-pair selection generalizes, or
whether the envelope ridge has the engineering meaning claimed for it. It
also does not settle the cross-pair comparison: the strain-era baselines were
run under the older unfiltered protocol and at full acquisition effort, so
"only the objectives changed" is not yet an isolated claim. The controlled
test for that is a 2 x 2 paired ablation (objective pair x model-driven
versus continued Sobol, shared initial designs, known-zero noise, fixed
objective thresholds, one acquisition setting, the same feasibility oracle
for both sides), which is listed as follow-on work rather than done here.

## Files

- `synthetic_bo_benchmark.py`: the driver. `--cloud --screen --campaign
  --baselines --compare --audit`
- `outputs/synthetic_bo/synthetic_cloud_<problem>.csv.gz`: the 16,384-design
  reference cloud per problem
- `outputs/synthetic_bo/synthetic_reference_<problem>.json`,
  `synthetic_front_<problem>.csv`: reference point, reference-set
  hypervolume, non-dominated set
- `outputs/synthetic_bo/synthetic_screen.csv`: free-hypervolume screen and
  front-geometry diagnostics
- `outputs/synthetic_bo/synthetic_bo_<problem>_seed<k>.csv` (50 runs),
  `synthetic_baseline_<strategy>_<mode>_<problem>_seed<k>.csv` (240 runs):
  every evaluation, with parameters, objectives, feasibility, running
  hypervolume and running bests
- `outputs/synthetic_bo/synthetic_summary_<problem>.csv`,
  `synthetic_summary_all.csv`: the tables above
- `outputs/synthetic_bo/synthetic_audit.csv`,
  `synthetic_audit_physics.csv`: the audit of result 5 and result 6
- `outputs/synthetic_bo/synthetic_<problem>.png`,
  `synthetic_overview.png`: the figures

Reproduce (about 30 minutes on 4 cores, dominated by the 50 BO runs):

```bash
python simulations/synthetic_bo_benchmark.py --cloud --screen
python simulations/synthetic_bo_benchmark.py --campaign --baselines --jobs 4
python simulations/synthetic_bo_benchmark.py --compare --audit
```
