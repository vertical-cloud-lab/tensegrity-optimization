# Edison ANALYSIS brief: interpretation of the PR #35 T3-prism Sobol simulation campaign

- **Task ID:** `ff8faab3-9ea4-427d-b545-9d0255c38e9d`
- **Job:** `ANALYSIS`
- **Fetched:** 2026-06-15T22:59:45Z
- **Status:** success
- **PR comment:** 4713093337

---

The main take: your broad direction is right, but several of the strongest claims in `sobol_t3_analysis.md` need to be narrowed because the current Tier-C outputs are dominated by setup choices more than absorber physics.

1) The conclusions that are supported by the attached data

- Tier-C MuJoCo `F_peak` is nearly invariant across the sampled box. Recomputed on all 512 feasible rows:
  - crutch `F_peak`: 712.2–739.2 N, median 737.5 N, relative span 3.65%, CV 0.18%
  - lander `F_peak`: 4633.1–4785.7 N, median 4736.0 N, relative span 3.23%, CV 0.78%
- Tier-C discrimination is mostly in `SEA` and, for crutch, somewhat in `eta`:
  - crutch `SEA`: 4.10e-05 to 2.15e-03 J/g, CV 0.589
  - lander `SEA`: 2.41e-04 to 9.31e-03 J/g, CV 0.814
  - crutch `eta`: 0.923–0.988
  - lander `eta`: 0.7322–0.7340, effectively flat
- The feasible set is trivial in this box: 512/512 feasible.
- The cross-engine ranking numbers you quoted are reproducible from the CSVs:
  - PyBullet vs Tier-C MuJoCo lander `F_peak`: ρ = -0.021, n = 32, p = 0.91
  - PyChrono: ρ = 0.701, n = 14 usable non-NaN rows, p = 0.0052
  - Newton Tier-B: ρ = 0.601, n = 24, p = 0.0019
  - PolyFEM Tier-A peak-g: ρ = 0.429, n = 8, p = 0.289

2) Where the current interpretation is too strong or likely artifact-driven

A. Tier-C `F_peak` is not just “design-invariant”; in crutch it is almost exactly the payload weight

- Median crutch `F_peak` / (75 kg × 9.81 m/s²) = 1.002.
- Range is only 0.968–1.005 times payload weight.

That means the crutch metric is basically reading static support load after filtering, not a resolved impact peak. So I would not describe crutch Tier-C `F_peak` as “payload·ΔV-dominated.” The data support a stronger and more specific statement:

- In crutch, Tier-C `F_peak` is almost a static-weight observable under the current signal-processing and model setup.
- In lander, Tier-C `F_peak` corresponds to about 94.5–97.6 g on the 5 kg payload, still far below the 1500 g constraint and only weakly design-varying.

Why this likely happens, based on the code:

- `F_peak` is derived from payload z-acceleration, then CFC-180 filtered in `bo_evaluator.py`.
- The simulation initializes both payload and struts with the same downward velocity, so there is no free-fall separation phase; the whole assembly starts already moving together.
- The impact observable is the payload body acceleration, not floor reaction force through a sensorized base.
- In crutch especially, the low-pass filter plus a soft, conservative spring network can wash out short transients and leave a quasi-supported load plateau.

B. Tier-C `SEA` is not “energy absorbed” in the dissipative sense relevant to bench testing

From the code summary, Tier-C `SEA` is based on maximum tendon strain energy in conservative springs, rescaled by cell mass. It is not hysteretic energy loss, not force-displacement work, and not net kinetic energy dissipated.

That matters because:

- median reported Tier-C `SEA` is 5.11e-04 J/g (crutch) and 1.43e-03 J/g (lander)
- rough incoming kinetic energy per estimated cell mass is on the order of 2.2 J/g (crutch) and 7.3 J/g (lander)

So the reported `SEA` is about 10^3–10^4 times smaller than the incoming energy scale. That is consistent with a conservative elastic snapshot, not with true absorbed energy. I would relabel Tier-C `SEA` internally as something like “peak elastic strain energy density proxy” unless/until you compute a dissipative work metric that matches experiment.

C. The twist≈0 result is real for Tier-C, but currently says more about parameter plumbing than about physics

This part of your write-up is sound for Tier-C. The code path does not use `twist_deg` in the rigid-regime override, so the near-zero Spearman values are expected and should not be interpreted as physical irrelevance.

My recomputation for Tier-C Spearman ρ confirms:
- `twist_deg` with all six Tier-C objectives: about -0.04 to +0.003

But there is a second issue: in the attached Tier-B subset, `twist_deg` is also near zero for Newton peak-g:
- Tier-B Newton `newton_peak_g` vs `twist_deg`: ρ = -0.015, p = 0.945

That does not prove twist is unimportant physically. It means one of three things is happening:
- twist is still not materially affecting the Tier-B geometry actually exercised,
- the chosen Tier-B observable is also dominated by other effects,
- or this T3 box simply has weak twist leverage for that impact observable.

You should test plumbing first, not physics first.

D. Cross-fidelity rank agreement is suggestive, not yet strong enough to claim a validated ladder for `F_peak`

The Newton correlation is the only one here with both moderate n and clear statistical support. PyChrono is promising but based on 14 usable rows. PolyFEM peak-g is not informative: its values are essentially all ~1 g.

Specifically:
- PolyFEM `polyfem_peak_g` mean is ~1.00 g with SD 0.0065 g.
- The discriminating Tier-A observable in your CSV is settled COM height, not peak-g.
- In this 8-design subset, settled COM height is perfectly rank-correlated with `H_mm` (ρ = 1.0), which suggests the current Tier-A subset is mostly expressing geometry/posture, not yet a rich impact-response signal.

So I would not write that PolyFEM supports Tier-C `F_peak` ranking. At present it does not.

3) What parts of Tier-C are trustworthy enough to use

Useful at Tier-C now:
- geometric feasibility screening in the sampled box
- very cheap broad coverage of the design space
- coarse ranking for “softer vs stiffer axial response” proxies, mainly through `H_mm` and `strut_d_mm`
- identifying regions where the current payload-acceleration observable is completely non-discriminating
- pretraining a surrogate on smooth low-fidelity trends, with explicit acknowledgement that the target is biased

Not trustworthy enough at Tier-C to act on directly:
- absolute `F_peak` for either regime
- compliance with the HAVS ≤8 g or GEVS ≤1500 g constraints, because the simulated constraints are nowhere near active
- twist sensitivity
- true energy absorption in the experimental sense
- final ranking among top candidates when rankings depend on deformation, hysteresis, buckling, contact, or rate effects

Require Tier-B/A or bench validation:
- any design call driven by `F_peak`
- any decision hinging on tendon material nonlinearity / damping / hysteresis
- any conclusion about twist
- constraint satisfaction near the actual accept/reject threshold

4) What is likely causing the apparent parameter effects at Tier-C

The strongest clue is the relation between Tier-C lander `F_peak` and a simple strut-mass proxy:
- Spearman ρ between lander `F_peak` and a crude strut mass proxy (`L * d^2`) = -0.976

That is almost a smoking gun that much of the Tier-C `F_peak` ranking is an inertia/contact-geometry effect from changing rigid-body mass and capsule size, not absorber mechanics.

You can see the regime dependence too:
- crutch `F_peak` vs `strut_d_mm`: ρ = +0.713
- lander `F_peak` vs `strut_d_mm`: ρ = -0.955

When the sign flips by regime, the safest reading is not “strut diameter is the dominant design lever for impact attenuation.” The safer reading is:
- Tier-C `F_peak` is highly sensitive to how mass, contact geometry, and filtered payload acceleration interact with each regime.

5) How to test whether these are setup artifacts or real physics

High priority tests:

- Freeze rigid-body mass while varying `strut_d_mm`.
  - If Tier-C `F_peak` sensitivity collapses, the current signal is mostly inertia-driven.
- Freeze contact radius while varying only density, then the reverse.
  - Separates mass effect from contact-geometry effect.
- Run the same 32–64-design subset with and without CFC-180 filtering.
  - If near-invariance disappears unfiltered, the filter is suppressing the only design-dependent transient.
- Replace payload-acceleration `F_peak` with floor reaction force peak and impulse.
  - Bench comparison wants transmitted load through the base; measure that directly in sim.
- Add a free-fall phase rather than starting payload and prism with the same initial velocity.
  - Starting the assembly already co-moving can mute the actual impact transient.
- Verify twist injection with 3–5 hand-picked extreme pairs at fixed {R,H,strut_d,cable_d} and only twist changed.
  - Plot node coordinates or exported geometry, not just response metrics.
- For Tier-B, repeat the same twist-isolation check before concluding twist is weak physically.

6) How to use the Sobol data inside BO

Best use: treat Tier-C as a biased, cheap auxiliary information source, not as a pseudo-experiment.

Recommended model structures

A. Autoregressive multi-fidelity GP / co-kriging

Use the classical autoregressive relation
- y_H(x) = ρ y_L(x) + δ(x)
where `y_L` is Tier-C and `y_H` is experiment or Tier-B/A, with `δ(x)` a discrepancy GP.

This is the Kennedy-O’Hagan calibration/discrepancy idea and the Le Gratiet recursive co-kriging line, both standard for multi-fidelity modeling.

Key citations:
- Kennedy, M. C., and O’Hagan, A. (2000). Predicting the output from a complex computer code when fast approximations are available. Biometrika 87(1): 1–13.
- Kennedy, M. C., and O’Hagan, A. (2001). Bayesian calibration of computer models. JRSS B 63(3): 425–464.
- Forrester, A. I. J., Sóbester, A., and Keane, A. J. (2007). Multi-fidelity optimization via surrogate modelling. Proc. R. Soc. A 463: 3251–3269.
- Le Gratiet, L. (2013). Multi-fidelity Gaussian process regression for computer experiments. PhD thesis / recursive co-kriging formulation.
- Perdikaris, P. et al. (2017). Nonlinear information fusion algorithms for data-efficient multi-fidelity modelling. Proc. R. Soc. A 473: 20160751.

B. Multi-task, multi-output BO with fidelity and regime as tasks

Represent regime (`crutch`, `lander`) and source (`Tier-C`, `Tier-B`, `bench`) as task labels or fidelity features. Use shared kernels with outcome-specific heads for `{F_peak, SEA, eta}`.

For acquisition, cost-aware noisy EHVI is the right family if you truly want a Pareto campaign under constraints.

Key citations:
- Swersky, K., Snoek, J., and Adams, R. P. (2013). Multi-task Bayesian optimization. NeurIPS 26.
- Kandasamy, K. et al. (2017). Multi-fidelity Bayesian optimisation with continuous approximations. ICML.
- Wu, J., Toscano-Palmerin, S., Frazier, P. I., and Wilson, A. G. (2019). Practical multi-fidelity Bayesian optimization for hyperparameter tuning. UAI.
- Daulton, S., Balandat, M., and Bakshy, E. (2020). Differentiable Expected Hypervolume Improvement for parallel multi-objective BO. NeurIPS.
- Daulton, S., Balandat, M., and Bakshy, E. (2021). Parallel Bayesian optimization of multiple noisy objectives with expected hypervolume improvement. NeurIPS.
- Frazier, P. I. (2018). A tutorial on Bayesian optimization. arXiv:1807.02811. Good overview of cost-aware and multi-fidelity BO.

C. Warm-starting and screening

What I would do with your current Tier-C Sobol rows:
- Use them to initialize the low-fidelity model only.
- Do not attach them as if they were bench-equivalent observations in the same noise model.
- Use them to define a screening prior and to seed candidate regions for higher-fidelity evaluation.
- Promote only a subset into Tier-B and bench based on uncertainty-aware rules.

Practical policy:
- Fit low-fidelity surrogates on all 512 Tier-C rows per regime.
- Select 8–12 diverse candidates spanning low predicted `F_peak`, high predicted `SEA`, and high uncertainty.
- Evaluate those at Tier-B or bench.
- Fit an autoregressive discrepancy model from Tier-C to Tier-B/bench.
- Use cost-aware constrained qNEHVI on the high-fidelity posterior, where cheap queries are allowed only when their value of information per cost exceeds direct bench/Tier-B sampling.

7) Objective and constraint formulation

Keep the scientific objectives separate from the trust assigned to each fidelity.

Objectives
- minimize transmitted peak load or peak-g
- maximize true specific energy absorption
- maximize stroke efficiency / compaction efficiency

But I would change the exact Tier-C observables used for BO if possible:
- For `F_peak`, prefer base reaction force or transmitted force, not payload acceleration alone.
- For `SEA`, prefer force-displacement work normalized by cell mass, and if possible partition recoverable vs dissipated energy.
- For `eta`, keep a plateau/rectangularity metric, but define it from the same force-time or force-displacement curve used experimentally.

Constraints
- crutch: `peak_g <= 8`
- lander: `peak_g <= 1500`

At BO level, encode each as a probabilistic feasibility constraint in its own regime. Because the thresholds differ so much, I would not average them or collapse them into a single scalar penalty.

One campaign or two?

My recommendation:
- one shared campaign architecture
- two regime-specific constrained objectives
- regime entered as a task/context variable

Reason:
- same design space
- different loading conditions and constraint scales
- some shared structure likely exists, but the Pareto fronts are regime-specific

So operationally this is a multi-task, multi-objective, constrained BO problem. If implementation complexity is too high right now, the fallback is:
- run two regime-specific campaigns with a shared low-fidelity prior or shared kernel hyperparameters

What I would not do:
- pool crutch and lander into a single scalarized objective too early
- use Tier-C predicted constraint satisfaction as ground truth, since constraints are inactive across the current sample

8) Which designs to print first

Because Tier-C `F_peak` is not trustworthy, the first print/drop batch should maximize information, not just exploit the nominal Tier-C Pareto front.

Priority batch: 6–8 prints

Include:
- 2 designs near the Tier-C “best SEA” corner
- 2 near the opposite geometry corner with low strut diameter / high height
- 2 twist-extreme matched pairs at fixed {R,H,strut_d,cable_d} to directly test whether twist matters on the bench
- 1 or 2 center-point / replicate designs to estimate experimental noise and print-to-print variability

Based on your Tier-C sensitivities, the most informative contrasts are along:
- `strut_d_mm`: low vs high
- `H_mm`: low vs high
- `twist_deg`: matched extreme pair specifically for falsifying the current twist-null result

I would not select first prints based only on tiny Tier-C `F_peak` differences. Those are below the model bias floor.

9) What to instrument

Minimum:
- base reaction force or load cell if possible
- payload accelerometer, same CFC-180 post-processing as planned
- high-speed video or displacement sensor for stroke / compaction
- specimen mass measured individually
- post-impact recovery height / rebound if you want energy partition clues

Strongly recommended:
- synchronized force and displacement so you can compute actual work loops
- at least a few quasi-static or moderate-rate Instron compression tests on the same printed cells to estimate effective stiffness, hysteresis, and repeatability

10) Immediate next analyses / experiments, in priority order

1. Recompute Tier-C outputs with transmitted base reaction force and unfiltered + filtered peaks.
   - This is the fastest way to see whether the current near-invariant `F_peak` is a signal-processing artifact.

2. Run a controlled ablation on `strut_d_mm`.
   - constant mass, varying contact radius
   - constant contact radius, varying mass
   - constant both, varying only tendon stiffness via `cable_d_mm`
   This will tell you what Tier-C is actually measuring.

3. Do a twist plumbing audit at Tier-C and Tier-B.
   - confirm geometry changes visually and numerically for matched extreme-twist pairs.

4. Print and bench-test a small D-optimal or maximin 6–8 design set rather than the nominal Tier-C winners.
   - include replicate(s) and twist pairs.

5. Build the first discrepancy model Tier-C → bench on the shared observables.
   - Even with 6–8 physical points, you can estimate whether Tier-C is useful as a prior for each outcome.

11) Bottom-line critique of `sobol_t3_analysis.md`

Sound:
- Tier-C covers the whole box cheaply.
- Feasibility is inactive in this box.
- Tier-C `F_peak` is nearly invariant.
- Twist-null at Tier-C is expected from the current implementation.
- Newton provides some support for a rank-preserving low→higher fidelity link.

Needs revision:
- Replace “`F_peak` is payload·ΔV-dominated” with a more precise statement that, under the current setup, crutch `F_peak` is essentially static-load-like and lander `F_peak` is weakly design-dependent.
- Do not present Tier-C `SEA` as true energy absorption; it is a conservative elastic-energy proxy under the current implementation.
- Do not count PolyFEM peak-g as supporting the Tier-C ladder; it is effectively constant in this subset.
- Be explicit that the strongest Tier-C lever, `strut_d_mm`, may be acting mainly through rigid-body mass/contact geometry rather than absorber mechanics.

That still leaves a solid path forward: use Tier-C for cheap screening and prior-shaping, but let Tier-B/A and the bench decide anything that matters for `F_peak`, true SEA, twist, and constraint satisfaction.

Sources cited
- Kennedy MC, O’Hagan A. Predicting the output from a complex computer code when fast approximations are available. Biometrika. 2000;87(1):1-13.
- Kennedy MC, O’Hagan A. Bayesian calibration of computer models. Journal of the Royal Statistical Society Series B. 2001;63(3):425-464.
- Forrester AIJ, Sóbester A, Keane AJ. Multi-fidelity optimization via surrogate modelling. Proceedings of the Royal Society A. 2007;463:3251-3269.
- Swersky K, Snoek J, Adams RP. Multi-task Bayesian optimization. NeurIPS. 2013.
- Kandasamy K, Dasarathy G, Schneider J, Póczos B. Multi-fidelity Bayesian optimisation with continuous approximations. ICML. 2017.
- Perdikaris P, Raissi M, Damianou A, Lawrence N, Karniadakis G. Nonlinear information fusion algorithms for data-efficient multi-fidelity modelling. Proceedings of the Royal Society A. 2017;473:20160751.
- Frazier PI. A tutorial on Bayesian optimization. arXiv:1807.02811. 2018.
- Wu J, Toscano-Palmerin S, Frazier PI, Wilson AG. Practical multi-fidelity Bayesian optimization for hyperparameter tuning. UAI. 2019.
- Daulton S, Balandat M, Bakshy E. Differentiable Expected Hypervolume Improvement for parallel multi-objective Bayesian optimization. NeurIPS. 2020.
- Daulton S, Balandat M, Bakshy E. Parallel Bayesian optimization of multiple noisy objectives with expected hypervolume improvement. NeurIPS. 2021.

- Discretionary analytical decisions made during the analysis
- Focused the quantitative re-check on the attached CSVs rather than re-running simulations from source, because the user asked to validate the reported conclusions against the provided outputs.
- Used all 512 Tier-C rows without further filtering because every row was marked feasible.
- Evaluated parameter influence with Spearman rank correlation, matching the project’s existing analysis choice.
- For PyChrono rank correlation, dropped the 2 rows with missing `pychrono_peak_g` before recomputing ρ.
- Reported approximate 95% confidence intervals for rank correlations using Fisher z as a quick uncertainty summary; these are approximate for Spearman and were used only to contextualize sample-size limitations.
- Interpreted Tier-C `SEA` using the code definition summarized from the attached scripts: maximum spring strain energy normalized by cell mass, not an experimentally dissipated-energy measure.
- Recommended a multi-task/multi-fidelity constrained BO framing rather than separate independent campaigns because the two regimes share the same design variables but have distinct response scales and constraints.
