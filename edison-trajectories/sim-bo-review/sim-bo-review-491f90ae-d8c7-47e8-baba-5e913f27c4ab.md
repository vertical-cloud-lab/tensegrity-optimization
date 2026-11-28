# Edison ANALYSIS brief: mock review of the simulation-only closed-loop BO campaign

- **Task ID:** `491f90ae-d8c7-47e8-baba-5e913f27c4ab`
- **Job:** `ANALYSIS`
- **Submitted:** 2026-06-20T22:33:02Z
- **Fetched:** 2026-06-20T22:56:49Z
- **Status:** success
- **PR comment:** 4760173539

---

Question:

# Project context and why we are exploring this

We are designing and 3D-printing class-1 tensegrity cells (3 rigid PLA struts,
E=3.5 GPa, rho=1240 kg/m^3; 9 soft TPU 85A tendons, E~12 MPa secant) in a
T3-triangular-prism topology as compact, tunable impact-absorbers. The program
goal is to build a simulation + Bayesian-optimization (BO) framework that (1)
generalizes to more advanced tensegrity structures and (2) yields real,
experimentally-validated "best" T3-prism designs on the bench (3D printer +
drop-tower + Instron). We study two impact regimes: crutch_tip (75 kg @
~1.4 m/s, anti-vibration HAVS peak constraint <= 8 g) and nasa_lander (5 kg @
~9.8 m/s, GEVS peak constraint <= 1500 g). The three objectives are peak
transmitted force (F_peak_N, minimize), specific energy absorption
(SEA_J_per_g, maximize), and compaction/stroke efficiency (eta, maximize).

# What we actually ran (attached)

`sim_bo_campaign.py` is a CLOSED-LOOP, simulation-ONLY analogue of our PR #35
hardware Sobol batch: Ax (AxClient, Sobol -> BOTORCH_MODULAR) proposes a design
over the exact PR #35 design box (R_mm in [25,40], H_mm in [60,110],
twist_deg in [40,80], strut_d_mm in [6,12], cable_d_mm in [3.0,5.5]); a
simulation scores it; the result feeds straight back to the surrogate. We ran it
across a simulation FIDELITY ladder, per loading regime, with multiple random
seeds (seeded by the three already-printed PR #35 T3 cells):

  - Tier C (MuJoCo rigid-tendon regime sim, CFC-180-filtered axial accel,
    ~0.2 s/eval): 3-objective qNEHVI on {F_peak_N (min), SEA_J_per_g (max),
    eta (max)}; 3 seeds x ~33 evals per regime.
  - Tier B (NVIDIA Newton / Warp XPBD drop, TPU tendons in the dynamic load
    path, ~4 s/eval): SINGLE-objective min F_peak_N (Newton only exposes the
    payload-accel trace); 2 seeds x ~18 evals per regime.

The objectives map onto exactly what our drop-tower (PR #74 accelerometer +
SAE J211 CFC-180) and Instron experiments measure, so simulated and measured
trials can attach to the same Ax/BoTorch model.

Attached: the campaign driver (sim_bo_campaign.py), the sim->BO bridge
(bo_evaluator.py), one trial CSV per (tier, regime) plus the feasible Pareto
subset CSVs, and the figures: per-seed and mean+-1sigma convergence, per-seed
Pareto fronts, and the Ax leave-one-out cross-validation (LOO-CV) scatter for
each seed/model. Our own write-up is sim_bo_campaign.md (+ bo_integration.md).

# Key empirical observations we want you to check and interpret

1. Tier-C F_peak is near-invariant across the whole box (crutch span ~4.4%,
   lander ~3.5%) and sits at the static support load (crutch median
   F_peak/(75 kg*g) ~ 1.0); SEA is the live discriminator (crutch span ~27x,
   lander ~7.5x). So the Tier-C Pareto fronts are nearly vertical.
2. Tier-B (Newton) F_peak IS strongly design-dependent (~2.5x span), so its
   single-objective loop genuinely descends -- the elastic tendons resolve a
   design-dependent impact peak the rigid-contact tier cannot.
3. LOO-CV (R^2 / Spearman of CV-predicted vs observed, mean over seeds):
   Tier-C crutch SEA 0.97/0.96 (strong); Tier-C lander F_peak 0.91/0.95;
   Tier-B F_peak 0.99/0.91-0.92; but Tier-C lander eta 0.80/0.61 and Tier-C
   crutch F_peak 0.89/0.79 look weaker -- we believe the weak ones are because
   the OUTCOME ITSELF is nearly constant across the box (e.g. lander eta pinned
   at 0.732-0.734), not because the model failed to fit. Please confirm or
   refute from the CV figures/CSVs.
4. twist_deg carries ~0 signal at both tiers because neither the Tier-C regime
   override nor the Newton build consumes the twist axis (geometry is built at
   the fixed equilibrium twist) -- a plumbing limitation, not physics.

# What we need from you (act as a rigorous mock reviewer; cite where possible)

A. Mock-reviewer critique of this simulation-only BO campaign and the claims in
   sim_bo_campaign.md: are the conclusions sound given the attached CSVs and the
   LOO-CV figures? Flag over-claims and setup artifacts.
B. WHERE IS THERE PREDICTIVE SIGNAL AND WHERE IS THERE NOT? Use the LOO-CV data
   per (tier, regime, outcome, seed) to separate "the GP cannot learn this" from
   "this outcome is intrinsically near-constant so there is nothing to learn."
   Recommend better signal diagnostics if ours are insufficient.
C. RECOMMENDATIONS FOR INCORPORATING CONTEXTUAL INFORMATION INTO THE BO. This is
   the core ask. Given a cheap biased simulator (Tier-C), a costlier higher-
   fidelity simulator (Tier-B/A), two loading regimes, and eventual real bench
   data, how should we encode the available CONTEXT/SIDE-INFORMATION into the
   surrogate and acquisition? Specifically address: multi-fidelity / multi-task
   GPs (regime as a task, fidelity as a task/context); contextual / composite-
   objective BO; informative priors and physics-derived features (e.g. strut
   L*d^2 mass, equilibrium-twist plumbing) as inputs or mean functions;
   discrepancy/bias models (Kennedy-O'Hagan, autoregressive co-kriging) to fuse
   sim + bench; and cost-aware acquisition. Cite the relevant BO literature.
D. Objective/constraint formulation: one campaign per regime vs. a single
   multi-task / multi-objective (qNEHVI) campaign, and how to encode the HAVS
   (<= 8 g) / GEVS (<= 1500 g) constraints as outcome constraints.
E. A prioritized, actionable next-steps list: the 3-5 highest-information
   changes to the framework, and which designs to physically print/drop-test
   first to validate the simulated Pareto front.

Use the attached scripts, data, and figures as ground truth for what we have.

---

The main conclusions mostly hold, but the current write-up overstates what this simulation-only BO campaign proves. The data support three strong claims: (i) Tier-C `F_peak_N` is almost invariant across the box and, for the crutch regime, sits at the static support load; (ii) Tier-C discrimination is coming mainly from `SEA_J_per_g`, so the Tier-C Pareto sets are close to vertical/degenerate in `F_peak`; and (iii) Tier-B `F_peak_N` is strongly design-dependent, with a ~2.54× max/min span, so there is real optimization signal there. The data do **not** support stronger claims that the present closed-loop BO setup is already a good stand-in for the final constrained multi-regime problem, because there are clear setup artifacts: Tier-B crutch and lander runs use the same designs and produce almost identical `F_peak_N` values (mean crutch/lander ratio 0.998, SD 0.0023), which is much more consistent with a regime-plumbing issue than with physically distinct loading cases; Tier-C lander BO collapses onto a narrow ridge and repeats many identical or near-identical boundary designs; and the “feasible Pareto” outputs are not informative about the real bench constraints because Tier-C satisfies the HAVS/GEVS force thresholds for 100% of sampled designs while Tier-B violates them for 100% of sampled designs. That mismatch is too large to treat the tiers as interchangeable surrogates for constraint handling.

A. Mock-reviewer critique of the campaign and claims

What is well supported by the attached data:
- **Tier-C crutch `F_peak_N` is near-invariant and static-load-like.** Across all 99 trials, `F_peak_N` spans 708.09 to 739.20 N; `(max-min)/median = 4.23%`. The median is 736.42 N, and `75*9.81 = 735.75 N`, so the median ratio is 1.001. That supports your claim that Tier-C crutch `F_peak` is effectively the static support load, not a resolved impact peak.
- **Tier-C lander `F_peak_N` is also near-invariant.** It spans 4621.47 to 4783.77 N; `(max-min)/median = 3.50%`. So Tier-C is weakly sensitive to geometry on `F_peak` in both regimes.
- **Tier-C `SEA_J_per_g` is the main live discriminator.** Crutch `SEA` spans 27.4× (9.79e-5 to 2.68e-3 J/g), lander `SEA` spans 7.55× (6.21e-4 to 4.69e-3 J/g). That supports the “near-vertical Pareto” description.
- **Tier-B `F_peak_N` is strongly design-dependent.** Crutch spans 2.17 to 5.51 MN and lander 2.17 to 5.53 MN; both have max/min ≈ 2.54. That supports the claim that elastic tendons in the dynamic path unlock a geometry-dependent peak missed by Tier-C.

Where the current write-up over-claims or needs tightening:
- **The Tier-C Pareto results are methodologically weak as BO evidence.** In `sim_bo_C_crutch_pareto.csv`, the Pareto subset has `F_peak_N` spanning only 708.0861 to 708.4839 N, which is just **0.06%** of the median on the Pareto set. That is not a robust 3-objective trade-off surface; it is a nearly collapsed 1–2 objective slice. Saying “the loop works” is fair. Saying it meaningfully optimized all three outcomes is too strong.
- **Tier-C lander shows severe proposal collapse and duplication.** Of 99 rows, 45 are duplicate designs on the 5 design variables. Several low-`SEA` points are exact repeats of the upper corner `(R,H,twist,strut_d,cable_d)=(25,110,80,12,5.5)`. This is a known failure mode when EHVI-like methods operate with near-flat objectives and boundary uncertainty. That should be reported as optimizer degeneracy, not just as a property of the physics.
- **Tier-B appears almost regime-blind.** The same best design appears in both `sim_bo_B_crutch_pareto.csv` and `sim_bo_B_lander_pareto.csv`: `R=27.886`, `H=62.162`, `twist=58.083`, `strut_d=11.374`, `cable_d=5.048`. Across all 36 matched trial pairs, `F_peak_crutch/F_peak_lander` has mean 0.998 and SD 0.0023. Given the nominally different masses/velocities, this is much more consistent with a missing or improperly consumed regime parameter than with a physically believable invariance. Your point 4 about twist plumbing is plausible; a similar audit is needed for regime plumbing in Tier-B.
- **Constraint interpretation is not yet credible across fidelities.** If I convert your regime constraints into force thresholds using payload mass, the crutch HAVS limit is `8*9.81*75 = 5886 N` and the lander GEVS limit is `1500*9.81*5 = 73575 N`. Tier-C is 100% feasible under these thresholds; Tier-B is 0% feasible under them. That means the current “feasible Pareto” files are not an informative approximation to the real constrained optimization problem. They mostly reveal that the two simulators disagree catastrophically on the peak metric scale.
- **Twist should not be described as “0 signal” from observational correlations alone.** In the raw Tier-C lander batch, `twist_deg` has Spearman ρ = -0.739 with `F_peak_N`. But this is confounded: the BO stage has severe collinearity among `H_mm`, `twist_deg`, `strut_d_mm`, and `cable_d_mm` (pairwise Spearman ρ ≈ 0.956–0.982). So the data are consistent with your plumbing explanation, but the evidence is indirect. The honest version is: “twist is not independently identifiable in these data, and code inspection suggests it is not actually consumed.”

B. Where there is predictive signal and where there is not

Your interpretation is partly right, but it needs a sharper distinction between “learnable mapping” and “tiny outcome variance.”

Strong signal, supported by both your CV figures and the raw span structure:
- **Tier-C crutch `SEA_J_per_g`**: large dynamic range (27.4×), reported mean LOO-CV `R^2=0.97`, Spearman `ρ=0.96`. This is the cleanest example of real predictive signal.
- **Tier-C lander `F_peak_N`**: despite only a 3.5% span, the CV figure you showed for seed 1 gives `R^2=0.99`, `ρ=0.98`, and the points track the diagonal tightly. This is a good example that low relative span alone does **not** imply “nothing to learn.” The function can still be smooth and learnable.
- **Tier-B `F_peak_N`**: reported mean LOO-CV `R^2≈0.99`, `ρ≈0.91–0.92`, with a 2.54× range. Strong signal.

Weak or ambiguous signal:
- **Tier-C crutch `F_peak_N`**: your reported mean `R^2=0.89`, `ρ=0.79` is decent, but the outcome itself varies by only 4.23% overall and is physically dominated by the static-load artifact. So yes, the GP can interpolate it, but that does not make it decision-useful for impact design. This is a “learnable but low-value target.”
- **Tier-C crutch `eta`**: range 0.9192 to 0.9926, span 0.0734 absolute. There is some signal, but it is weaker and less clean than `SEA`.

Near-constant outcome, so “weak CV” should not be over-interpreted as model failure:
- **Tier-C lander `eta`**: range 0.7324 to 0.7339, absolute span 0.00145, SD 0.0004. In the CV figure, the predictive error bars are comparable to the full data range. That supports your interpretation that the issue is mainly intrinsic near-constancy, not lack of fit. But I would phrase it carefully: “The mapping may be learnable in a narrow absolute sense, but the outcome has negligible decision-scale variance over the design box, so it is not a useful optimization target at this fidelity.”

A cleaner diagnostic than the current CV tables:
1. **Report CV error relative to the outcome range**, not only `R^2` and rank correlation. Use something like `NRMSE = RMSE / (max-min)` or `MAE / IQR`. When the range is tiny, `R^2` can be unstable and misleading.
2. **Report standardized uncertainty**: median LOO posterior SD divided by observed SD, or by `(max-min)`. For Tier-C lander `eta`, this ratio is effectively large; that shows “no actionable signal.”
3. **Use a constant-mean null comparator.** Compare GP LOO log predictive density or RMSE against a null model that predicts the campaign mean. If the GP barely beats the null on an outcome with tiny spread, that outcome should be deprioritized.
4. **For variable importance, use ablation or Sobol/posterior sensitivity from the fitted surrogate**, not marginal correlations from BO samples. Correlations are badly confounded by adaptive sampling.
5. **Check calibration**, not just point accuracy: empirical coverage of 68%/95% LOO intervals and negative log predictive density. This matters if acquisition relies on posterior uncertainty.

C. Recommendations for incorporating contextual information into BO

This is the core fix. You have a textbook multi-source, multi-task, multi-fidelity problem with biased simulators and future physical data. I would not keep running fully separate per-regime, per-tier loops except as debugging baselines.

1. Use a **multi-task / multi-fidelity surrogate** with explicit context variables
- Treat **design** `x = (R,H,twist,strut_d,cable_d,...)` separately from **context** `c = (regime, fidelity, maybe payload mass, impact velocity, and contact model flags)`.
- At minimum, model regime and fidelity as discrete tasks in an intrinsic coregionalization model (ICM) or linear model of coregionalization (LMC). The classic references are Bonilla et al. 2008 for multi-task GPs and Swersky et al. 2013 for multi-task BO. For multi-fidelity BO with GPs, see Kennedy and O'Hagan 2000; Forrester et al. 2007; Kandasamy et al. 2017; Poloczek et al. 2017; Wu et al. 2019.
- In BoTorch/Ax terms, this usually means a **multi-output GP with task features** or a **fidelity feature** plus cost-aware acquisition. The key is to let the model learn cross-task covariance, not to hard-pool everything.

2. Encode **regime physically**, not only as a label
- If possible, do not represent crutch vs lander only as a binary task. Include the actual regime-defining variables as inputs: payload mass, impact velocity, perhaps impact energy `0.5 m v^2`, static preload, and any pulse-filter settings if they affect the measured target. This gives you a path to generalize beyond exactly two regimes.
- A sensible hybrid is: continuous regime descriptors as inputs plus a task index for unmodeled residual differences.

3. Use **autoregressive discrepancy models** to fuse Tier-C, Tier-B, Tier-A, and bench
- The basic Kennedy–O’Hagan calibration/discrepancy view is `y_real(x)=ρ y_sim(x)+δ(x)+ε`, where `δ(x)` is a GP discrepancy term. Kennedy and O’Hagan 2001 is the standard reference.
- For multiple simulator levels, use **autoregressive co-kriging**: `f_t(x)=ρ_{t-1}(x) f_{t-1}(x)+δ_t(x)`. This is the Le Gratiet/Forrester-style extension of the Kennedy–O’Hagan idea. It is a good fit for Tier-C → Tier-B → Tier-A → bench when lower tiers are cheaper but biased.
- Practically: start with Tier-C and Tier-B sharing a latent base function plus a fidelity-specific bias term. Once bench data arrive, add a bench discrepancy term instead of pretending the bench is just another exchangeable task.

4. Add **informative priors / engineered physics features**
The raw variables are okay for first passes, but your own observations suggest some structured features should help.
- Add rough **mass and slenderness proxies** as input features: strut mass proxy `~ H*d^2`, cable mass proxy `~ H*d_cable^2`, total printed mass if available, radius-to-height ratio `R/H`, and maybe a simple axial stiffness proxy combining strut and tendon contributions. The goal is not to replace the raw variables but to give the GP axes aligned with known mechanics.
- If twist is not actually consumed at a given fidelity, either remove it from that fidelity’s active input set or gate it via an **input mask by fidelity**. Otherwise the surrogate wastes lengthscale capacity on a dead axis and acquisition can get confused.
- If you have equilibrium-twist or prestrain quantities that are physically used by higher-fidelity models but not by Tier-C, include those as explicit context features when they become available.
- A mean function based on simple mechanics can help if you have enough prior structure. For example, model `F_peak` around a baseline trend in impact energy and effective stiffness, with the GP learning residuals. The BO literature on Bayesian optimization with priors and structured kernels supports this, though implementation details vary.

5. Use **cost-aware acquisition**
- With large cost gaps between Tier-C and Tier-B/A, you want expected improvement or hypervolume gain **per unit cost**, not just raw gain. BoTorch has cost-aware utilities for this style of policy; the general idea is in multi-fidelity BO work such as Kandasamy et al. 2017 and Wu et al. 2019.
- A practical policy is: let Tier-C scout broadly, but only if its learned correlation with Tier-B/bench on the decision-relevant outcomes is nontrivial. If Tier-C `F_peak` remains uncorrelated with Tier-B or bench `F_peak`, stop spending budget on Tier-C for that outcome and use Tier-C only for outcomes where it carries transfer value, such as maybe `SEA` or geometry screening.

6. Use **contextual or composite-objective BO** only if the composite reflects real decisions
- If the real program objective is regime-dependent, don’t collapse everything into one arbitrary scalar too early. A multi-output constrained BO setup is safer.
- If you do need a scalarized acquisition for manufacturing decisions, make the scalarization explicit and contextual, e.g. different utility weights by regime or mission profile, then optimize expected utility under the task context.

Good BO references to cite
- Jones, Schonlau, Welch (1998), EGO.
- Frazier (2018), “A Tutorial on Bayesian Optimization.”
- Daulton, Balandat, Bakshy (2020), differentiable expected hypervolume improvement / qEHVI.
- Daulton, Balandat, Bakshy (2021), qNEHVI for noisy parallel multi-objective BO.
- Swersky, Snoek, Adams (2013), multi-task BO.
- Kennedy and O’Hagan (2000, 2001), Bayesian calibration and discrepancy for computer models.
- Forrester, Sóbester, Keane (2007), multi-fidelity optimization via co-kriging.
- Kandasamy et al. (2017), multi-fidelity BO with continuous approximations.
- Wu et al. (2019), practical multi-fidelity BO for hyperparameter tuning; useful for cost-aware fidelity allocation patterns even outside ML.

D. Objective/constraint formulation

One campaign per regime vs one multi-task campaign:
- **Short term**: keep separate regime campaigns only as a debugging baseline while plumbing is still suspect. Right now Tier-B’s near-identical crutch/lander outputs imply that a pooled campaign would hide a bug.
- **Once regime plumbing is verified**: move to a **single multi-task campaign** with regime as task/context and outcomes `F_peak_N`, `SEA_J_per_g`, `eta` modeled jointly. This lets you share information where appropriate while preserving regime-specific optima and constraints.
- Use **constrained qNEHVI** if you still want a Pareto set over the three outcomes. That is the natural BoTorch-family tool for noisy multi-objective optimization with outcome constraints.

How to encode the HAVS / GEVS constraints:
- If the actual experimental constraint is on **peak acceleration**, model that quantity directly as an outcome if possible. Right now you are inferring force thresholds from mass. That is okay only if the mapping is exact and consistently defined across simulator and bench.
- If you keep `F_peak_N`, encode regime-specific constraints as outcome constraints conditioned on regime:
  - crutch feasible if `F_peak_N <= 75*9.81*8 = 5886 N`
  - lander feasible if `F_peak_N <= 5*9.81*1500 = 73575 N`
- In a multi-task model, this is a **context-dependent threshold**. Implementation-wise, either transform to a common constraint variable like `g = F_peak_N / (m g) - a_limit_in_g <= 0`, or model peak acceleration directly in g’s. I strongly prefer the latter because it removes regime-scale differences from the constraint and makes the task relation cleaner.
- The current data show that these constraints do not align across fidelities at all: Tier-C is always feasible, Tier-B never feasible. Until that is reconciled, constrained BO on the fused dataset will be numerically possible but scientifically misleading.

E. Prioritized next steps

1. **Audit and fix regime plumbing before any more BO claims.**
   Highest priority. Tier-B crutch and lander are nearly identical across matched trials. Verify which parameters actually affect the Newton drop: payload mass, impact speed, gravity, contact timing, and any scaling from acceleration trace to `F_peak_N`. Do the same audit for twist at every fidelity.

2. **Stop treating all Tier-C objectives as equally useful. Re-scope Tier-C’s role.**
   Based on these data, Tier-C `F_peak` is not a useful impact objective and Tier-C lander `eta` is nearly constant. Tier-C is currently most informative for `SEA`, maybe `eta` in crutch, and perhaps for broad geometry screening. Use it as a biased low-cost source, not as a direct optimizer for constraint satisfaction.

3. **Replace separate loops with a hierarchical multi-fidelity model once plumbing is fixed.**
   Start with a two-level model Tier-C ↔ Tier-B on `F_peak`, then extend to bench with a discrepancy term. Use regime as context and include physical regime descriptors (`m`, `v`, maybe energy) as inputs. Make acquisition cost-aware.

4. **Improve diagnostics before trusting surrogate learning.**
   Add LOO RMSE/MAE normalized by range or IQR, null-model comparisons, interval coverage, and posterior-SD-to-range ratios. Also report duplicate proposal counts and boundary-hit rates; for Tier-C lander, 45/99 duplicate designs is an optimizer pathology worth surfacing.

5. **Choose the first print/drop tests to maximize information about simulator bias, not just predicted optimum.**
   I would print and test 4 designs first:
   - **One Tier-B `F_peak` minimizer**: the shared Newton optimum around `R=27.886, H=62.162, twist=58.083, strut_d=11.374, cable_d=5.048` to test whether Tier-B’s claimed descent is real on bench.
   - **One high-SEA Tier-C lander design**: e.g. `R=27.886, H=62.162, twist=58.083, strut_d=11.374, cable_d=5.048`, which is also the top `SEA` point in `sim_bo_C_lander.csv`. Conveniently this overlaps the Tier-B optimum, so it is especially informative for cross-tier agreement.
   - **One low-SEA / heavy upper-corner design**: e.g. `(25,110,80,12,5.5)`, because Tier-C kept revisiting it. If bench data show it is not actually competitive, that exposes the BO/surrogate pathology quickly.
   - **One contrast design from the Tier-C crutch Pareto sliver** with similar `F_peak` but materially different `SEA`/`eta`, ideally a low-mass high-SEA point versus a heavier point. Since `F_peak` is flat there, this pair tests whether Tier-C’s `SEA` ranking transfers at all.

If budget allows a fifth, choose a design deliberately separated in `H` and cable diameter from the shared optimum to estimate a local gradient on the bench. The goal of the first physical round should be **simulator calibration and ranking transfer**, not just chasing the current predicted best point.

Bottom line
- Your headline claim that Tier-C and Tier-B expose very different signal structure is supported.
- Your claim that weak CV on some outcomes reflects near-constant outcomes is supported for Tier-C lander `eta`, but should be stated more carefully and backed by range-normalized error diagnostics.
- The current campaign also reveals important artifacts: Tier-B is probably regime-blind, Tier-C lander BO collapses and duplicates proposals, and the constraints are inconsistent across fidelities by orders of magnitude.
- The next framework step should be a **contextual, cost-aware, discrepancy-aware multi-fidelity BO model**, but only after plumbing audits on regime and twist.

References
- Jones DR, Schonlau M, Welch WJ. Efficient Global Optimization of Expensive Black-Box Functions. Journal of Global Optimization. 1998;13:455-492.
- Frazier PI. A Tutorial on Bayesian Optimization. arXiv:1807.02811, 2018.
- Daulton S, Balandat M, Bakshy E. Differentiable Expected Hypervolume Improvement for Parallel Multi-Objective Bayesian Optimization. NeurIPS 2020.
- Daulton S, Balandat M, Bakshy E. Parallel Bayesian Optimization of Multiple Noisy Objectives with Expected Hypervolume Improvement. NeurIPS 2021.
- Swersky K, Snoek J, Adams RP. Multi-Task Bayesian Optimization. NeurIPS 2013.
- Kennedy MC, O’Hagan A. Predicting the Output from a Complex Computer Code When Fast Approximations Are Available. Biometrika. 2000;87(1):1-13.
- Kennedy MC, O’Hagan A. Bayesian Calibration of Computer Models. Journal of the Royal Statistical Society B. 2001;63(3):425-464.
- Forrester AIJ, Sóbester A, Keane AJ. Multi-fidelity Optimization via Surrogate Modelling. Proceedings of the Royal Society A. 2007;463:3251-3269.
- Kandasamy K, Dasarathy G, Oliva J, Schneider J, Póczos B. Multi-fidelity Bayesian Optimisation with Continuous Approximations. ICML 2017.
- Wu J, Toscano-Palmerin S, Frazier PI, Wilson AG. Practical Multi-fidelity Bayesian Optimization for Hyperparameter Tuning. UAI 2019.

- Discretionary analytical decisions made during the analysis:
  - Used the attached CSVs and figures as primary evidence and treated the markdown write-up as a claim set to audit, not as evidence.
  - Interpreted regime constraints by converting acceleration limits to force thresholds via `F = m a`, because the attached campaign tables report `F_peak_N` rather than peak acceleration directly.
  - Evaluated “signal vs near-constant outcome” mainly from observed outcome span, CV figures, and duplicate/boundary behavior, rather than refitting the exact Ax/BoTorch GP, because the attached raw CV summary tables were not separately provided.
  - Used Spearman correlations only as descriptive diagnostics and did not interpret them causally or as variable-importance measures, because adaptive BO sampling induces strong confounding.
  - Flagged Tier-B regime insensitivity as a likely plumbing artifact based on near-identical matched-trial outputs, while noting that definitive confirmation would require code-path inspection or reruns with controlled perturbations.
  - Recommended a multi-task/multi-fidelity discrepancy model rather than a single pooled GP because the attached tiers disagree sharply in scale and constraint feasibility, making naive pooling scientifically unsafe.
  - Prioritized first physical tests for cross-tier disagreement and transfer validation, not purely predicted optimum performance, because calibration value is higher than exploitation at this stage.
