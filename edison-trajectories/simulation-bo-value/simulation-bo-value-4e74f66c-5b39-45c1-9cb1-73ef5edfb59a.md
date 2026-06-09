# Edison ANALYSIS brief: value of multi-fidelity simulations for the PR #35 T3-prism BO campaign and high-fidelity validation

- **Task ID:** `4e74f66c-5b39-45c1-9cb1-73ef5edfb59a`
- **Job:** `ANALYSIS`
- **Submitted:** 2026-06-09T19:56:25Z
- **Fetched:** 2026-06-09T20:06:02Z
- **Status:** success

---

Question:

We have a multi-fidelity simulation stack for drop-impact response of class-1
tensegrity cells (3 PLA struts E=3.5 GPa rho=1240; 9 TPU 85A tendons, E~12 MPa
secant, sigma_break~26 MPa; T3-prism topology) for two regimes: crutch_tip
(75 kg @ 1.4 m/s, ~Ø24x25 mm cell, HAVS peak <= 8 g) and nasa_lander
(5 kg @ 9.8 m/s, ~Ø200x200 mm cell, GEVS peak <= 1500 g). Tiers: (C) MuJoCo
rigid-strut + tendon screening (~0.1 s/design on 1 CPU core); (B) NVIDIA Newton
(Warp XPBD, differentiable) + DiffPD; (A) PolyFEM+IPC NeoHookean on a welded
strut+tendon volumetric mesh.

We are wiring tier-C into the PR #35 T3-prism Bayesian-optimization campaign
(t3_prism_sobol_batch.py). That script currently only emits a Sobol design set
with a *placeholder* objective and reports no data back. Our bridge
(bo_evaluator.py) maps the PR #35 parameter schema (R_mm[25,40], H_mm[60,110],
twist_deg[40,80], strut_d_mm[6,12], cable_d_mm[3.0,5.5]) -> a PrintableDesign ->
run_regimes.simulate(regime) -> objectives {F_peak_N, SEA_J_per_g, eta}
(eta = compaction/stroke efficiency). The same objective space is what the
drop-tower experiments (PR #74 accelerometer + SAE J211 CFC-180 filtered peak g;
PR #67 drop protocol) and Instron tests measure, so simulated and measured rows
can attach to the same Ax/BoTorch model.

We need a rigorous, citation-backed analysis answering:

# 1. Value of cheap simulation inside the BO loop
Given tier-C costs ~0.1 s/design vs. days per printed+drop-tested specimen, how
should we best use the simulator inside a sequential / batch BO campaign? Cover
concretely: (a) multi-fidelity / multi-task BO formulations (e.g.,
MF-MES, trace-aware knowledge gradient, BoTorch SingleTaskMultiFidelityGP /
Ax multi-task) that fuse cheap-sim + expensive-experiment observations on the
shared {F_peak, SEA, eta} objective space; (b) using the simulator to seed /
warm-start the GP prior or as a cheap "screening" pre-filter before committing a
specimen to print; (c) cost-aware acquisition (cost per fidelity) and when the
expected value of a tier-C / tier-B eval exceeds its cost; (d) the risk of model
discrepancy / bias between sim and bench, and the standard ways to correct it
(discrepancy/bias GP a la Kennedy-O'Hagan, delta-modelling, autoregressive
co-kriging). Cite the BO + multi-fidelity literature.

# 2. What the simulations can tell us that the printer/bench cannot cheaply
Enumerate specific quantities the sims expose per design that are hard or
expensive to measure experimentally and would improve the campaign: e.g.,
full-field strut/tendon strain history, contact sequence / buckling onset, energy
partition (tendon vs. strut vs. contact), sensitivity gradients (Newton/DiffPD
differentiability) for gradient-informed BO, and the class-1 feasibility / strut
self-collision screen. Which of these are trustworthy at tier C vs. require
tier A/B?

# 3. Value for the high-fidelity manual validation measurements
How should simulation outputs shape the *experimental* program (drop-tower /
Instron)? e.g., which designs to physically test first (max-information / D-
optimal under the surrogate), what instrumentation to add (where peak strain
localizes), what loading rate / drop height brackets the regimes, and how to set
up the sim-vs-experiment comparison so the bench data can recalibrate the sim
(which scalar + which curves to compare; SAE J211 filtering parity).

# 4. Objective trade-offs and regime handling
We see peak-force vs. SEA vs. compaction-efficiency (eta) trade-offs that differ
sharply by regime (lander: F_peak ~kN, eta ~0.7; crutch: eta ~0.96, cushion-
limited). Should we run one BO campaign per regime or a single multi-objective /
multi-task campaign? Recommend the objective formulation (scalarization vs. EHVI
Pareto) and any constraints (HAVS <= 8 g, GEVS <= 1500 g) to encode.

# 5. Concrete recommendations
A prioritized, actionable list: the specific BoTorch/Ax components to use, the
order of operations to integrate bo_evaluator.py into t3_prism_sobol_batch.py,
and 3-5 immediate next experiments. Flag where advice is engineering judgement
vs. literature-grounded, with citations.

Use the attached files (the PR #35 BO script, our sim->BO bridge, the tier-C
simulator, and the manuscript draft) as ground truth for what we have built.

---

Here is a rigorous, citation-backed analysis of how to integrate the tier-C MuJoCo simulator into the tensegrity Bayesian Optimization (BO) campaign. 

### 1. Value of cheap simulation inside the BO loop

At ~0.1 seconds per evaluation, the tier-C MuJoCo simulator provides an extreme cost asymmetry compared to the physical print-and-drop cycle (days). You can exploit this asymmetry via two primary formulations:

**(a) Warm-starting the GP Prior via Single-Task BO:**
Instead of learning the objective landscape purely from expensive drop-tower experiments, use the simulator to evaluate an initial Sobol space-filling design (Sobol 1967). This populates the GP prior with the gross trends of the parameter space (e.g., that thicker tendons generally increase force and SEA). Currently, `t3_prism_sobol_batch.py` throws away the objectives; you should use `bo_evaluator.evaluate_batch_csv` to compute F_peak, SEA, and $\eta_c$ and `attach_trial` these to the Ax client. 
*Relevant citations: Snoek et al. 2012 (NeurIPS) on practical BO initialization; Balandat et al. 2020 (NeurIPS) for BoTorch integration.*

**(b) Multi-Fidelity / Multi-Task BO Formulations:**
The mathematically rigorous approach is to treat tier-C as a continuous or discrete low-fidelity information source. Since tier-C provides biased but correlated estimates of the true physics, you can use **Multi-Task GP models** (Swersky et al. 2013) where task 0 = sim and task 1 = bench. 
BoTorch provides `SingleTaskMultiFidelityGP`, which models the objective using an autoregressive co-kriging framework originating from **Kennedy & O'Hagan (2000, 2001)**. In this framework, the high-fidelity bench measurement $f_{bench}(x)$ is modeled as a scaled simulator output plus a discrepancy function $\delta(x)$: 
$f_{bench}(x) = \rho f_{sim}(x) + \delta(x)$.
*Relevant citations: Kennedy & O'Hagan 2000 (Biometrika); Forrester et al. 2007 (Proc. R. Soc. A); Poloczek et al. 2017 (NeurIPS) on misoKG; Wu et al. 2020 (UAI) on continuous-fidelity KG (cfKG).*

**(c) Cost-aware acquisition:**
The expected value of querying the simulator exceeds its cost whenever the uncertainty reduction in the shared GP (transferred to the bench task via covariance) is large relative to the ~0.1s compute time. Use **Cost-Weighted Expected Improvement (EI-per-second)** (Snoek et al. 2012) or Multi-Fidelity Knowledge Gradient (cfKG) / Multi-Fidelity Max-Value Entropy Search (MF-MES) (Takeno et al. 2020, ICML).

### 2. What simulations can tell us that the bench cannot cheaply

Tier-C MuJoCo exposes internal states per timestep that are expensive or impossible to measure with external video/accelerometry:
*   **Energy partition:** The time-series vector `se` tracks tendon strain energy vs kinetic vs strut strain energy. 
*   **Kinematic feasibility:** The `design.check()` collision screen flags class-1 feasibility (struts overlapping) before committing PLA to the build plate.
*   **Sensitivity gradients:** While MuJoCo (tier-C) is not natively differentiable in the way Warp XPBD (tier-B) or DiffPD are, you can trivially compute finite-difference gradients of peak force with respect to geometry at 0.1s per step. This informs active subspace reduction (Constantine 2015) before BO begins.
*Trustworthiness:* Tier-C is trustworthy for gross trend discovery (bulk energy partitions, clearance checks) but cannot predict local stress localizations or TPU weld-line failures. Tier-B/A is required for those localized failure modes.

### 3. Value for the high-fidelity manual validation measurements

Simulation outputs should dictate the physical testing matrix:
*   **Experiment selection:** Do not randomly sample the bench drops. Use the tier-C trained surrogate to identify the regions of highest uncertainty or maximum expected hypervolume improvement (**qNEHVI**; Daulton et al. 2021) and only print *those* designs.
*   **Instrumentation targeting:** The simulation's maximum strain locations indicate exactly where to place transfer tape/markers for the Polytec QTec laser vibrometry or high-speed camera tracking.
*   **Calibration parity:** For the bench data to accurately recalibrate the sim discrepancy $\delta(x)$, the signal processing must match. Apply an **SAE J211 CFC-180** filter (180 Hz cutoff) to both the raw physical accelerometer voltages and the simulated $a_z$ vectors before extracting $F_{peak}$.

### 4. Objective trade-offs and regime handling

You observed regime-specific clustering (Lander: F_peak ~kN, $\eta_c$ ~0.7 vs Crutch: $\eta_c$ ~0.96). 
*   **Do not run a single scalarized BO campaign.** Compaction efficiency ($\eta_c$) and Peak Force conflict fundamentally. 
*   **Recommendation:** Run **one multi-objective campaign per regime** using **qNEHVI** (Daulton et al. 2021). Treat SEA and $\eta_c$ as maximization objectives. Treat the regime targets (HAVS $\leq$ 8g, GEVS $\leq$ 1500g) as **black-box constraints** evaluated by the surrogate (Letham et al. 2019, Bayesian Analysis).

### 5. Concrete recommendations and order of operations

1.  **Filter Parity (Immediate):** Update `bo_evaluator.py` to apply an SAE J211 CFC-180 digital filter (using scipy.signal) to the simulated acceleration array before extracting `peak_g`. *[Engineering judgment grounded in standard crash-test methodology].*
2.  **Close the loop on PR #35 (Immediate):** Modify `t3_prism_sobol_batch.py` to pass the Sobol parameterizations through `evaluate_batch_csv()`. Attach these outcomes to the Ax client as initial simulator data rather than abandoning the trials.
3.  **Formulate Multi-Objective Constraints:** Configure Ax with `objectives={"SEA_J_per_g": minimize=False, "eta": minimize=False}` and `outcome_constraints=["F_peak_N <= 750"]` (for the crutch 75kg * 10g limit, roughly). 
4.  **Implement Multi-Fidelity (Next 2 weeks):** Switch from standard GPs to BoTorch's `SingleTaskMultiFidelityGP`. Add a `fidelity` parameter to the search space (`"sim"` vs `"bench"`). Configure Ax to use `MultiFidelityKnowledgeGradient` to automatically query the simulator 1000x for every 1 bench drop.
5.  **Drop-tower calibration:** Execute the 9 physical drops from the PR #35 plate. Report the F_peak and SEA back to Ax as `fidelity="bench"`. The surrogate will automatically learn the discrepancy $\delta(x)$ between MuJoCo and reality.

***

### Discretionary Analytical Decisions
*   Recommended qNEHVI over LogEI because the trade-off between compaction efficiency and peak force necessitates Pareto-front exploration rather than scalarization.
*   Recommended separate regime campaigns rather than a combined campaign because the physics bounds (8g vs 1500g) operate in distinct nonlinear regimes that will warp a single GP length scale.
*   Specified SAE J211 CFC-180 filtering as the standard for matching physical crash data to simulated high-frequency ringing.
*   Advised standard Co-Kriging (Kennedy-O'Hagan) via BoTorch `SingleTaskMultiFidelityGP` over more complex non-linear fusion (NARGP) for initial implementation due to software readiness.
