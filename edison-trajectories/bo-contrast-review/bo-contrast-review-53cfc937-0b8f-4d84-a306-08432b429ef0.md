# Edison ANALYSIS brief: BO implementation audit (BO-vs-DOE contrast study)

- **Task ID:** `53cfc937-0b8f-4d84-a306-08432b429ef0`
- **Job:** `ANALYSIS`
- **Submitted:** 2026-08-26T20:27:57Z
- **Fetched:** 2026-08-26T20:27:58Z
- **Status:** success

---

Question:


# Review request: is our Bayesian-optimization implementation sound, or is the reported BO-vs-DOE separation an artifact?

We benchmark constrained multi-objective Bayesian optimization (Ax 0.5.0 /
BoTorch, `BOTORCH_MODULAR` which resolves to qNEHVI for two minimized
objectives) against four uninformed baselines on a deterministic physics
simulator of a 3D-printed tensegrity impact absorber. We report that BO
reaches 94.2 % of a dense-sweep hypervolume ceiling while every baseline
lands at 77.5 to 80.2 %, with Mann-Whitney p = 9.1e-5 (the floor of a
10-vs-10 test) and zero overlap between the two sets of ten seeds.

**The specific question we want answered: is the BO implementation correct?**
We want an adversarial audit in BOTH directions, because either error would
be embarrassing in a manuscript:

(a) Is the BO *unfairly advantaged* by an implementation or accounting
    choice, so the separation is an artifact rather than a modeling
    advantage? Candidate mechanisms we want checked explicitly:
    hypervolume/reference-point accounting, feasibility masking, whether the
    baselines are handicapped relative to best uninformed practice, whether
    the BO sees information the baselines do not, off-by-one budget
    accounting, and whether the objective-pair selection procedure
    (described below) constitutes selecting a benchmark that flatters the
    optimizer.

(b) Is the BO *broken or badly configured* in a way that made it look bad on
    the earlier objective pair, where we reported it statistically
    indistinguishable from random search? If so, our narrative that the
    difference between the pairs is objective geometry rather than optimizer
    quality is wrong.

Everything needed to re-derive our numbers is attached, including all raw
per-seed CSVs. Please recompute whatever you need rather than trusting our
summary.

## The problem

Design space: four dimensionless shape ratios of a class-1 tensegrity T3
prism (3 PLA struts, 9 TPU-85A tendons), each a plain continuous
`RangeParameter`:

  H_over_R          in [1.5, 4.4]
  H_over_strut_d    in [5.0, 18.33]
  cable_over_strut_d in [0.25, 0.9167]
  twist_deg         in [40, 80]

The single overall scale is solved in closed form so every design has
exactly the same printed mass (20.23 g), i.e. the search is on a
constant-mass manifold and mass is not a free variable. (This was a
deliberate earlier fix: an earlier formulation left mass free and one
objective turned out to be printed mass in disguise, rho = 0.99993.)

Objectives, both minimized, from one MuJoCo drop-tower simulation
(deterministic, ~41 ms per evaluation, no observation noise):

  t180          CFC-180-filtered transmissibility, top-vertex peak
                acceleration over base-plate peak acceleration
  envelope_cm3  bounding-envelope volume of the article (stowed bulk)

Outcome constraints (both are closed-form geometry, not simulation
outputs, and both are passed to Ax as outcome constraints):

  cable_d_print_mm >= 3.0     TPU self-bridging print floor
  envelope_cap_cm3 <= 250.0   build-volume cap

## The BO wiring, verbatim from `bo_contrast_study.py::run_bo_seed`

```python
gs = GenerationStrategy(steps=[
    GenerationStep(model=Models.SOBOL, num_trials=9, min_trials_observed=9,
                   max_parallelism=9, model_kwargs={"seed": seed}),
    GenerationStep(model=Models.BOTORCH_MODULAR, num_trials=-1,
                   max_parallelism=9,
                   model_gen_kwargs={"model_gen_options": {
                       "optimizer_kwargs": {"num_restarts": 8,
                                            "raw_samples": 128}}}),
])
ax_client = AxClient(generation_strategy=gs, random_seed=seed,
                     verbose_logging=False)
ax_client.create_experiment(
    name=..., parameters=RATIO_PARAMETERS,
    objectives={o1: ObjectiveProperties(minimize=True),
                o2: ObjectiveProperties(minimize=True)},
    outcome_constraints=["cable_d_print_mm >= 3.0",
                         "envelope_cap_cm3 <= 250.0"])
for rnd in range(5):                     # round 0 = Sobol, rounds 1-4 = model
    parameterizations, _ = ax_client.get_next_trials(9)
    for idx, params in parameterizations.items():
        res = evaluate(dict(params))     # the simulator
        ax_client.complete_trial(trial_index=idx,
                                 raw_data={k: v for k, v in res.items()
                                           if k in ax_keys})
```

Notes on choices we are unsure about and want judged:

- `complete_trial` is passed **plain floats**, no SEM. In Ax that means
  *inferred* noise, not known-zero noise, even though the simulator is
  deterministic. We considered passing `(value, 0.0)`. A previous paired
  study on a different objective pair found the two gave the same result
  there, but we have not re-tested it here. Does inferring noise on a
  noiseless deterministic simulator materially change qNEHVI behaviour, and
  which is the defensible choice?
- No `ObjectiveThreshold`s are set, so Ax infers reference points for the
  acquisition function from the observed data. Our *reporting* hypervolume
  uses a different, fixed reference point (below). Is that mismatch between
  the acquisition's inferred reference point and the scoring reference point
  a problem for the comparison, or is it fine because the same scoring rule
  is applied to every method?
- Acquisition optimizer runs at 8 restarts x 128 raw samples rather than the
  Ax defaults (20 x 1024). A previous paired study on a related pair found
  no difference (Wilcoxon p = 0.92, ten paired seeds, 5/10 wins). We did not
  repeat that check on this pair. Is that a real risk to the conclusion?
- Objectives are on very different scales (t180 ~ 0.65 to 1.0, envelope_cm3
  ~ 11 to 215). We rely on Ax/BoTorch's internal outcome standardization. Is
  anything else needed?
- The two outcome constraints are deterministic geometry with no noise, and
  are also checkable in closed form before evaluating. We give them to Ax as
  probabilistic outcome constraints anyway. Would `ParameterConstraint`-style
  handling, a feasibility-weighted acquisition, or rejection at generation
  time be more appropriate, and would it change the comparison?

## The baselines

Four, all at the identical budget of 45 evaluations and the identical ten
seeds: uniform random, scrambled Sobol, scrambled Latin hypercube, and a
compass/pattern search (initial step 0.35 of range, halved on a failed
sweep, three weightings 0.15/0.5/0.85 of a normalized weighted sum so it
produces a spread of trade-offs rather than one point, fresh axis
permutation per sweep).

Both the samplers and the compass search run in two modes:

- `plain`: infeasible draws are evaluated and then excluded from fronts.
- `printable`: candidate points are rejection-sampled through the
  *simulation-free* closed-form printability check, so no sampler wastes
  budget on an unprintable design, and the compass search skips unprintable
  probes without being charged for them. This is the mode we report, on the
  argument that it is the strongest honest DOE.

The BO's own Sobol round 0 is **not** rejection-filtered: it draws from the
full box like any Ax Sobol step. So in the reported comparison the
baselines get a free constraint oracle that the BO's initialization does
not. We believe this makes the comparison conservative in the BO's favour,
but please check that reasoning, and check whether the reverse could be
true through the constraint plumbing.

## Scoring

Hypervolume of the dominated region for two minimized objectives, computed
with our own 2-D sweep routine (`hypervolume_2d` in `pr102_sim_campaign.py`,
attached), with infeasible points masked to +inf before accumulation, so a
run's hypervolume is a monotone non-decreasing function of its evaluation
index. Reference point, shared by every method and every seed: 1.05 times
the componentwise worst value over the feasible dense cloud. The ceiling
(the denominator of the "94.2 % of ceiling" figure) is the hypervolume of
the non-dominated set of a 16,384-design scrambled-Sobol sweep plus a
Nelder-Mead polish of the best weighted points (+2.3 % over the raw sweep).

Please verify the hypervolume routine against a standard implementation
(e.g. BoTorch's `Hypervolume` / `DominatedPartitioning`) on our raw CSVs,
and check the reference-point convention for any way it could favour a
method that concentrates points near one end of the front.

## The objective-pair selection procedure, which we consider the biggest
## threat to validity and want judged explicitly

We did not pick the reported objective pair first. We ran one dense
16,384-design cloud (attached, `contrast_cloud_ratios.csv.gz`), which prices
every candidate observable at once because one simulation returns all of
them. For each of six candidate pairs we Monte-Carlo resampled 2,000
uninformed 45-design batches from that cloud and measured the fraction of
that pair's hypervolume ceiling an uninformed batch collects "for free",
plus front-geometry diagnostics. The screen's results (attached,
`contrast_screen.csv`):

  pair                       obj-corr   free HV (uninformed 45)
  t180 + peak_tendon_strain   -0.82      84.6 +- 2.4 %   (previous pair; control)
  t180 + e_rebound            +0.59      81.0 +- 5.3 %   (dead-axis control)
  t180 + envelope_cm3         -0.60      80.0 +- 3.7 %   (CHOSEN)
  t180 + stroke_mm            +0.65      86.5 +- 5.0 %
  strain + envelope_cm3       +0.69      91.5 +- 4.3 %
  envelope + strain <= 0.12   -0.61      85.9 +- 2.9 %

Selection rule, stated before the campaign ran: exclude the two controls,
require a genuine trade-off (the front must span a meaningful fraction of
both objective ranges, which eliminates pairs whose front is a sliver), then
take the lowest free hypervolume. The physical justification we give for the
chosen pair is that it is the lander packaging question: isolation bought
against stowed bulk, at equal printed mass.

Questions on this specifically:
1. Is "choose the objective pair whose front an uninformed sampler is least
   likely to hit by chance, then report that BO beats uninformed sampling on
   it" a legitimate benchmark design, a circular one, or legitimate only if
   framed and reported in a particular way? What framing would a referee
   accept?
2. Our Monte-Carlo screen predicted 78.2 % free hypervolume for uninformed
   45-design batches and the measured baselines came in at 77.5 to 80.2 %.
   Does that agreement validate the screen, or is it tautological given both
   come from the same cloud?
3. Is there a standard name and a standard diagnostic for what we are
   measuring (how much of a Pareto front a space-filling design collects for
   free)? We would like to cite prior art rather than invent a diagnostic.

## The two results we are contrasting

Same protocol, same budget, same seeds, same code path, two objective pairs:

  pair                        BO            best baseline   separation
  t180 + peak_tendon_strain   82.7 % ceil   79.9 % ceil     none (overlapping)
  t180 + envelope_cm3         94.2 % ceil   80.2 % ceil     p = 9.1e-5, no overlap

Our claim is that the difference is a property of the objective geometry
(the strain pair's front is a wide band that a space-filling design lands
near by accident; the envelope pair's front is a 1-D ridge through a 4-D
space, with only 1.2 % of the printable cloud within 2 % of it), not a
property of the optimizer or its implementation.

Please state plainly whether you believe that claim is supported by the
attached artifacts, and list any implementation defect you find, ranked by
how much it could move the reported numbers. If you find none, say so
plainly, and say what additional control would most cheaply falsify the
result. We are separately running the identical harness on synthetic
analytic benchmarks (Branin-family, including a deliberately degenerate
`(f, -f)` pair) as a control; suggestions for what a synthetic control
should and should not be able to show are welcome.

## Attached files

- `bo_contrast_study.py` (the study driver: BO wiring, baselines, screen,
  reference polish, comparison)
- `pr102_sim_campaign.py` (search space, `hypervolume_2d`, the constant-mass
  projection and evaluator entry point)
- `pr102_baselines.py` (earlier baseline implementations this study builds on)
- `bo_contrast_study.md` (the write-up as it currently reads)
- `contrast_bo_envelope_seed*.csv` (all 10 BO repeats, every evaluation with
  parameters, both objectives, feasibility flag, running hypervolume)
- `contrast_baseline_*_{printable,plain}_envelope_seed*.csv` (all 80
  baseline runs, same columns)
- `contrast_cloud_ratios.csv.gz` (the 16,384-design cloud, every observable)
- `contrast_front_*.csv`, `contrast_refs.csv`, `contrast_screen.csv`
- the four figures


---

# Audit verdict

**The envelope-pair BO loop is substantively correct, and the BO-vs-DOE separation is not explained by a hypervolume, feasibility, or budget-accounting bug.** I independently recomputed all 90 envelope runs from their raw objective and feasibility columns. Every run has 45 evaluations, saved and recomputed feasibility agree exactly, all hypervolume traces are monotone, and the recomputed endpoint ordering has complete separation.

There are, however, **three manuscript-level corrections**:

1. **The reported ceiling is not a ceiling.** BO found feasible points beyond the cloud-plus-polish reference front. Adding all supplied feasible evaluations to the reference set increases hypervolume from 85.9287 to **87.0916**, a **1.35%** increase. Thus BO is at most **92.97%**, not 94.23%, of the best hypervolume currently present in the artifacts. The best printable baseline becomes 79.13% on this denominator. The separation remains large.
2. **The stated Mann–Whitney “floor” is wrong.** With ten versus ten observations and complete separation, the exact one-sided value is **p = 5.41×10⁻⁶**. The reported **9.13×10⁻⁵** is SciPy’s asymptotic approximation, not the attainable floor. Because seeds are matched, a paired test is preferable: one-sided exact Wilcoxon gives **p = 9.77×10⁻⁴** for every baseline, with 10/10 paired wins. State the planned inferential test and correct four comparisons, for example Holm adjustment.
3. **The two objective-pair studies are not demonstrably an identical-protocol controlled contrast.** The attached strain-era filenames and source indicate full-default acquisition effort for BO and the older, unfiltered baseline protocol, whereas the envelope study uses 8×128 acquisition optimization and printable-filtered baselines. Rescoring endpoints under one reference convention does not remove those design differences. The geometry explanation is plausible and well supported descriptively, but the artifacts do not isolate objective pair as the only changed factor.

## Recomputed envelope results

Using the fixed reported reference point `(1.038710, 262.446)` and the polished denominator 85.9287:

| Method | Mean final HV | Mean fraction | Range across seeds | Mean feasible evaluations |
|---|---:|---:|---:|---:|
| BO | 80.9678 | **94.23%** | 91.21–97.40% | 40.1/45 |
| Random, printable | 68.9116 | 80.20% | 76.77–85.35% | 45/45 |
| Compass, printable | 67.9817 | 79.11% | 67.37–84.33% | 45/45 |
| Sobol, printable | 67.3608 | 78.39% | 70.89–83.34% | 45/45 |
| Latin hypercube, printable | 66.6173 | 77.53% | 70.79–82.44% | 45/45 |

The worst BO seed, 91.21%, exceeds the best printable baseline seed, 85.35%. Mann–Whitney probability-of-superiority estimates are **1.00** for all four comparisons. Mean absolute BO advantages are 12.06 to 14.35 hypervolume units. Paired bootstrap 95% intervals for mean differences were:

- versus random: **10.24 to 13.80**
- versus compass: **10.29 to 16.11**
- versus Sobol: **11.26 to 16.04**
- versus Latin hypercube: **12.35 to 16.49**

These bootstrap intervals are descriptive because ten seeds are a small sample and seed-level outcomes need not be normally distributed.

## Implementation audit, ranked by potential impact

### 1. Underestimated reference front and denominator: verified, moderate reporting impact

The supplied `contrast_front_envelope.csv` reproduces the reported polished hypervolume as 85.92873. Unioning that front, the dense cloud, and every feasible BO and baseline evaluation gives **87.09158**. BO evaluations alone add **1.1371** hypervolume units beyond the claimed reference; all printable baselines together add far less.

This does not create the BO-vs-baseline difference because every run was scored against the same fixed reference point. It does invalidate “ceiling” and inflates all percentages of ceiling, especially BO’s because BO is the method that exposed the missing front. Call it a **reference-set hypervolume** or **best-known hypervolume**, rebuild it from the union of all evaluated feasible points, and ideally run a stronger independent global reference search. Do not use a benchmarked method’s own points only in the denominator without including all methods and disclosing the construction.

### 2. Cross-pair protocol mismatch: high impact on the causal narrative

The evidence supports these separate observations:

- On the envelope pair, BO strongly beats printable-filtered baselines.
- On the strain-era data, endpoint distributions overlap. Recomputed mean fractions are BO 82.71%, Sobol 79.90%, random 79.63%, Latin hypercube 78.86%, and compass 77.53%.
- The dense cloud shows different geometry: Spearman correlation −0.600 and 1.16% near-front share for envelope, versus −0.822 and 4.46% for strain.

But “only the objectives changed” is too strong. The strain BO is described as full effort, while envelope BO uses 8 restarts and 128 raw samples. More importantly, the strain baseline files come from the earlier unfiltered implementation, while envelope reporting uses the stronger printable-filtered implementation. The strain pair also shows one-sided unadjusted Mann–Whitney values of 0.038 versus Sobol, 0.019 versus Latin hypercube, 0.137 versus random, and 0.061 versus compass. Calling it simply “statistically indistinguishable” depends on the comparator, sidedness, and multiplicity rule.

**Required clean control:** rerun both objective pairs through the current harness, with the same initial designs, known-zero noise, identical acquisition settings, and printable-oracle treatment. Then fit a paired analysis of the within-seed BO-minus-baseline difference with objective pair as the contrast. Until then, phrase the geometry claim as the leading explanation, not an experimentally isolated cause.

### 3. Unknown-noise observations on a deterministic simulator: real configuration defect, uncertain numerical impact

Ax 0.5.0 explicitly documents that a plain mean means unknown observation noise and that noiseless evaluations should be supplied as `(mean, 0.0)` [Ax trial-evaluation documentation](https://ax.dev/docs/0.5.0/trial-evaluation/). Therefore the current input is not the defensible representation of this simulator.

This is not an obvious unfair advantage. Inferred noise can smooth deterministic structure, alter posterior variance, and make qNEHVI integrate over observational uncertainty unnecessarily. It could help or hurt depending on fit. The existing CSVs cannot identify the counterfactual effect because suggestions would change after the first model fit.

**Fix:** return `(float(value), 0.0)` for both objectives and both deterministic geometry metrics, then run paired seeds against the current implementation. Given the complete separation and 12–14 HV-unit margins, overturning the envelope result seems unlikely, but that is an empirical claim and should be checked.

### 4. Acquisition/reference-point mismatch: valid but avoidable, probably modest

The reporting reference is fixed and common, so the endpoint comparison itself is fair. However, qNEHVI optimizes hypervolume relative to Ax-inferred objective thresholds, while the score uses a different reference point. That means BO is not explicitly optimizing the reported metric. It is more likely to reduce BO performance than inflate it, but dynamic inferred thresholds can change which front regions are valued.

For a clean benchmark, provide fixed `ObjectiveThreshold`s corresponding to the prespecified reporting reference, with correct minimization direction. BoTorch notes that qNEHVI requires a reference point and recommends either a domain-defined acceptable bound or a documented dynamic strategy [BoTorch constrained qNEHVI tutorial](https://botorch.org/docs/tutorials/constrained_multi_objective_bo). Run inferred and fixed-threshold versions as a paired sensitivity analysis.

### 5. Deterministic feasibility represented by learned outcome constraints: conservative for BO here

The plumbing is internally consistent:

- `cable_d_print_mm` is passed with constraint `>= 3.0`.
- `envelope_cap_cm3` is exactly equal to `envelope_cm3` in every BO row and is constrained `<= 250`.
- Post-hoc feasibility matches the stored `pair_feasible` flag in every row.
- BO feasibility rises from **61.1% in round 0** to 90.0%, 97.8%, 96.7%, and 100% in model rounds 1–4.

Printable baselines receive a free rejection oracle and obtain 45 feasible simulations. BO receives only 40.1 feasible evaluations on average and has to learn the same deterministic boundary. This advantages the baselines, not BO. At nine evaluations, printable random/Sobol already average ~66% of the polished reference-set HV, while BO’s unfiltered Sobol initialization averages 57.2%. BO overtakes after model fitting.

Ax `ParameterConstraint`s are generally algebraic constraints on parameter values; these projected nonlinear geometric constraints are not naturally represented by a simple linear parameter constraint. Appropriate choices are:

- give **every method**, including BO, the same cheap feasibility oracle through constrained candidate generation/rejection; or
- charge every method for infeasible proposals and let BO model the constraints.

The current hybrid is conservative but asymmetric. Report that asymmetry and add oracle-filtered BO as the fairest engineering comparison. The duplicated `envelope_cm3`/`envelope_cap_cm3` GP is inefficient rather than numerically incorrect; if Ax permits one metric to be both objective and constrained, use the same metric name.

### 6. Reduced acquisition optimization: unverified risk, unlikely source of unfair advantage

Eight restarts and 128 raw samples can miss acquisition maxima relative to 20×1024. This would normally make BO worse, although stochastic optimizer behavior is not monotonic seed by seed. The prior paired result on another pair does not establish equivalence here.

The cheap control is not necessarily ten full repeats. Rerun at least the weakest BO seeds with identical initial Sobol points and 20×1024, then extend to all seeds if endpoint changes approach the observed between-method margin. For publication, a paired 10-seed sensitivity is preferable.

### 7. Objective scaling: no defect found

The raw scales differ substantially, but standard Ax/BoTorch modular models normalize inputs and standardize modeled outcomes in their standard setup. No manual objective rescaling is required. Scalarized compass objectives are explicitly normalized by the reference point, which avoids domination by envelope units.

### 8. Budget and information flow: no defect found

- Every envelope run contains exactly 45 rows.
- BO uses 9 initial Sobol trials plus 36 model-selected trials.
- No duplicate charging or off-by-one error appears in the raw traces.
- The ten BO initial batches are pairwise distinct.
- Printed mass is exactly 20.23 g in every attached run.
- All parameters lie within bounds; apparent cable-ratio excesses are only ~3.3×10⁻⁷ from six-significant-digit CSV rounding.
- Ax receives only objectives and constraint metrics, not the dense cloud, reference polish, or baseline outcomes.
- The screen and ceiling are not fed into the BO except indirectly through the authors’ choice of objectives; the acquisition does not see the cloud.

## Hypervolume audit

The 2-D minimization sweep is correct. It:

1. drops points not strictly better than the reference in both coordinates;
2. sorts by the first minimized objective;
3. accumulates non-overlapping rectangles only when the second objective improves.

Across all 90 raw envelope files, independently recomputed running values differ from saved values by at most **2.16×10⁻⁴**, consistent with CSV rounding. There were no monotonicity violations. I could not execute BoTorch’s `Hypervolume` in this audit environment because BoTorch is not installed, but the algorithm is the standard exact two-objective calculation and the supplied front reproduces the saved reference hypervolume.

Reference-point sensitivity does not remove the separation. For four reasonable fixed references that all dominate the feasible cloud, every BO seed remains above every printable-baseline seed. Relative to the cloud-only hypervolume, BO versus the best baseline was:

- 96.13% versus 79.47% at 1.001× componentwise worst;
- 96.36% versus 82.02% at the reported 1.05× reference;
- 96.90% versus 86.86% at 1.20× worst;
- 95.94% versus 80.57% using a 5%-of-range margin.

A more distant reference gives greater weight to extreme points and narrows the relative gap, as expected. It does not reverse it. The reference should nevertheless be justified by engineering acceptability rather than chosen only from observed worst values. Hypervolume’s dependence on the reference point is standard; see Guerreiro, Fonseca, and Paquete, *The Hypervolume Indicator* (2022), DOI: [10.1145/3453474](https://doi.org/10.1145/3453474).

## Baseline fairness

For **uninformed, one-shot, simulation-budgeted sampling**, printable random, scrambled Sobol, and Latin hypercube are reasonable strong baselines. Printable rejection is generous because it does not charge geometric failures. Compass search supplies a local sequential non-model comparator but is not a comprehensive representation of derivative-free multi-objective optimization.

Do not call the set “best uninformed practice” without qualification. Missing useful controls include:

- Sobol continued from the **exact BO initial design** for each seed, isolating the value of model-selected evaluations;
- random/Sobol restricted through the same feasible-domain oracle supplied to BO;
- a stronger sequential model-free multi-objective method, if the claim extends beyond DOE;
- common-random-number pairing based on shared initial designs, not merely equal integer seed labels across different generators.

The headline claim should be “qNEHVI beat the four specified DOE/compass baselines,” not “qNEHVI beat uninformed optimization in general.”

## Objective-pair selection

Choosing the pair with the lowest expected fixed-budget random-search hypervolume is **legitimate as construction of a challenge benchmark**, but circular if presented as unbiased evidence that BO generally beats DOE. The selection criterion explicitly chooses the case where DOE is predicted to look weakest. A referee could accept it if you:

1. label the screen as **benchmark construction**, not validation;
2. disclose all six candidate pairs and the exact prespecified eligibility/selection rule;
3. treat the chosen-pair result as conditional on selection;
4. report results across all eligible objective pairs, or validate the geometry-to-advantage hypothesis on new pairs not used in selection;
5. keep the physical envelope objective justification independent of the optimizer result.

“Meaningful fraction” must be converted into a numerical, prespecified cutoff. Otherwise the exclusion of alternatives remains researcher-discretionary even if written before the campaign.

The screen-to-baseline agreement is **calibration on the same simulator and design distribution**, not independent validation. It is not wholly tautological because the campaign baseline coordinates are newly generated rather than resampled cloud rows. But both estimate nearly the same functional: fixed-budget hypervolume under a printable-conditioned uninformed design distribution, using a ceiling/reference derived from that same cloud. Independent validation requires a new dense cloud seed, analytic ground truth, or new objective pairs.

There is no single standard name for “hypervolume collected for free.” Use a transparent description such as:

> **fixed-budget random-search hypervolume attainment**, reported as the distribution of normalized hypervolume after 45 feasible space-filling evaluations.

Related standard tools are the **hypervolume indicator**, **empirical attainment functions**, and fixed-budget benchmarking distributions. Do not present the 2%-near-front share as a standard metric; it is a useful custom diagnostic whose normalization and tolerance must be stated. Relevant reviews are Brockhoff and Tušar, *Benchmarking multiobjective optimizers 2.0* (2021), DOI: [10.1145/3449726.3461421](https://doi.org/10.1145/3449726.3461421), and Audet et al., *Performance indicators in multiobjective optimization* (2021), DOI: [10.1016/j.ejor.2020.11.016](https://doi.org/10.1016/j.ejor.2020.11.016).

## Plain answer to the scientific claim

**Supported in a qualified form:** the artifacts strongly support that envelope geometry is harder for space-filling designs and that qNEHVI learns useful structure on that pair. They do not support the stronger sentence that objective geometry is proven to be the sole cause of the cross-pair difference, because objective selection was optimized for low random-search attainment and the two pair studies differ in baseline constraint handling and acquisition settings.

A defensible manuscript statement is:

> On a prespecified envelope-volume challenge pair selected for low fixed-budget random-search hypervolume attainment, constrained qNEHVI achieved 10/10 seed-wise wins over each of four baselines. Dense-cloud diagnostics are consistent with the hypothesis that this advantage arises because the efficient envelope front occupies a narrower region of the design space than the strain front. A fully crossed rerun is needed to attribute the difference between objective pairs solely to geometry.

## Cheapest decisive falsification

Run a **2×2 paired ablation** using identical initial Sobol designs:

- objectives: strain versus envelope;
- continuation: qNEHVI versus continued printable Sobol;
- known-zero noise for all outputs;
- fixed objective thresholds equal to the scoring reference;
- the same cheap-feasibility oracle for both methods;
- identical 20×1024 acquisition effort for both objective pairs.

The key statistic is the paired interaction:

$$
(\mathrm{HV}_{BO}-\mathrm{HV}_{Sobol})_{envelope}
-
(\mathrm{HV}_{BO}-\mathrm{HV}_{Sobol})_{strain}.
$$

If that interaction is consistently positive across seeds, the geometry narrative survives a direct controlled test. If not, configuration or historical protocol differences explain part of the contrast.

Synthetic Branin-family controls can verify orientation, feasibility masking, thresholds, budget accounting, known-zero noise, reproducibility, and recovery of known Pareto fronts. A degenerate `(f,-f)` pair should show that broad anti-correlated objective geometry grants high hypervolume to space-filling designs and leaves little room for BO. Synthetic tests **cannot** validate the tensegrity simulator, prove that the six-pair selection generalizes, or establish that the physical envelope ridge has the asserted engineering meaning.

### Discretionary analytical decisions

- Used the fixed reported reference point for primary reproduction, then tested four alternative dominating reference points.
- Rebuilt the best-known reference hypervolume from the union of the dense cloud, supplied polished front, and all feasible campaign/baseline points.
- Reported both the authors’ unpaired Mann–Whitney test and an exact paired Wilcoxon test because integer seeds were matched across methods.
- Used one-sided tests to match the prespecified directional claim that BO has higher hypervolume.
- Used a 50,000-resample percentile bootstrap for descriptive 95% intervals on mean BO-minus-baseline differences.
- Treated the 2% near-front share as a custom geometry diagnostic, not a standardized performance indicator.
- Interpreted “ceiling” conservatively as best-known reference hypervolume because no global-optimality certificate is available.
