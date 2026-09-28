# Edison ANALYSIS brief: making the objective evaluations fair (mass / volume / contact area)

- **Task ID:** `e43abed6-2fac-4d93-a169-bc6cf9cc8116`
- **Job:** `ANALYSIS`
- **Submitted:** 2026-06-21T04:53:49Z
- **Fetched:** 2026-06-21T05:02:58Z
- **Status:** success
- **PR comment:** 4760939061

---

Question:

# Project context

We design and 3D-print class-1 tensegrity cells (3 rigid PLA struts, E=3.5 GPa,
rho=1240 kg/m^3; 9 soft TPU 85A tendons, E~12 MPa) in a T3 triangular-prism
topology as compact, tunable impact absorbers, and run a simulation +
Bayesian-optimization framework to find good designs that we then validate on a
3D printer + drop-tower + Instron. We study two loading regimes that reuse the
same unit cell: crutch_tip (75 kg @ ~1.4 m/s; HAVS peak constraint <= 8 g) and
nasa_lander (5 kg @ ~9.8 m/s; GSFC GEVS peak constraint <= 1500 g). Three
objectives: peak transmitted force F_peak_N (minimize), specific energy
absorption SEA_J_per_g (maximize), and compaction/stroke efficiency eta
(maximize). The drop-tower is a Lansmont M23 (<= 5000 g, >= 0.25 ms, <= 9.8 m/s,
<= 36 kg payload).

# The concern we want feedback on

Our Sobol / Pareto / BO campaigns draw designs from a 5-D box
(R_mm in [25,40], H_mm in [60,110], twist_deg in [40,80], strut_d_mm in [6,12],
cable_d_mm in [3.0,5.5]) and score them with a fixed loading scenario per regime.
But every corner of that box is a physically DIFFERENT-SIZED object: across the
box the cell mass varies 6.2x (9.5 -> 59 g), the circumscribing envelope volume
4.7x (118 -> 553 cm^3), and the strut-tip footprint area 4.0x (85 -> 339 mm^2).
So when the campaign reports "fat, short, large-radius cells win on SEA," that is
partly a tautology -- those cells simply have more material, volume, and contact
area. Of our three objectives only SEA is mass-normalized (SEA = strain_energy *
payload_mass / cell_mass); none control for volume or footprint; and F_peak at
our cheap Tier-C fidelity is a support-load / contact-area proxy (it tracks the
static support load), so it is contact-area- and stiffness-dominated rather than
mechanics-dominated. The crutch tolerates this (loose envelope) but for the
LANDER, mass and volume are the BINDING constraints, so letting the optimizer
"win by getting bigger" breaks the problem.

# What we are proposing (the thinking under review -- see fair_evaluation_analysis.md)

Real scaled-up lander-module constraints: (1) a hard MASS budget (absorber mass
is a fraction of landed mass -- single-digit %); (2) stowed/deployed ENVELOPE
VOLUME (fairing / CubeSat-U allocation); (3) FOOTPRINT / contact area setting
ground pressure on regolith and the tip-over stability cone (both a cap and a
floor); (4) crush STROKE long enough to hold peak g under GEVS at 9.8 m/s but
short enough to fit the deployed envelope; (5) SEA specified per unit mass AND
per unit volume.

Two routes to fairness (plus a hybrid we lean toward):
  Route A -- RE-PARAMETERIZE the search space so the budget is met by
  construction: a constant-mass manifold (fix total cell mass m*, solve one axis
  like cable_d or strut_d to hit it), a constant-envelope manifold (fix pi*R^2*H),
  a constant-footprint manifold, or scale-free SHAPE RATIOS (H/R, H/strut_d,
  cable_d/strut_d, twist) plus ONE explicit scale variable (mass or size) that is
  either fixed by the budget or carried as a separately-costed axis.
  Route B -- keep the box but make the OBJECTIVES/CONSTRAINTS size-aware: report
  intensive objectives (SEA_J_per_g AND SEA_J_per_cm^3, base-reaction peak g
  instead of the payload-accel proxy, ground pressure = reaction/footprint), and
  add cell_mass <= m*, envelope_vol <= V*, footprint in [A_min, A_max] as Ax
  OUTCOME CONSTRAINTS solved with constrained qNEHVI; or carry mass/volume as a
  cost (cost-aware acquisition) or an explicit 4th objective.
  Hybrid (recommended for the lander): Route A on the binding mass budget +
  scale-free shape ratios, with envelope volume and footprint as outcome
  constraints, scoring intensive objectives.

# What we need from you (act as a rigorous mock reviewer; cite where possible)

A. Is our diagnosis correct that the current campaign is size-confounded and that
   this specifically breaks the LANDER objective comparison? Anything we have
   mischaracterized about which objective normalizes what?
B. For a scaled-up tensegrity lander crush-core / shock-isolator module, what ARE
   the real design constraints and typical budget VALUES we should target (mass
   fraction of landed mass, J/g and J/cm^3 specific-absorption figures of merit,
   ground-pressure / footprint limits on regolith, stroke/standoff)? Cite
   heritage crush-core / airbag / honeycomb / SUPERball / MER / GEVS numbers
   where you can.
C. NORMALIZE THE OBJECTIVES (ad hoc) vs RE-PARAMETERIZE THE SEARCH SPACE (so
   constraints always hold): which is methodologically sounder for fair
   multi-objective BO, and when? Is a constant-mass / constant-volume MANIFOLD
   (lower-dimensional feasible set) preferable to a rectangular box with outcome
   constraints, given GP modeling and qNEHVI behavior on constrained vs
   manifold-restricted domains? Cite the relevant BO / design-of-experiments /
   dimensional-analysis (Buckingham-pi / similitude) literature.
D. If we DO use outcome constraints, how should mass/volume/footprint and the
   HAVS (<= 8 g) / GEVS (<= 1500 g) peak-g limits be encoded -- hard constraints,
   soft penalties, or a feasibility-weighted (constrained qNEHVI) acquisition --
   and how does that interact with our biased cheap Tier-C simulator?
E. A prioritized, actionable list: the 3-5 highest-value changes to make the
   evaluations fair (especially for the lander), and which to implement first.

Use fair_evaluation_analysis.md as the primary artifact under review; regimes.py
and bo_evaluator.py are ground truth for the loading definitions and the
F_peak/SEA/eta math; pareto_render_campaign.md and sobol_t3_diagnostics.md show
the size-confounded result and the support-load/elastic-proxy caveats.

---

Your core diagnosis is right. The current lander campaign is size-confounded, and the confound is big enough that cross-design comparisons are not fair for the lander use case. The cleanest fix is your hybrid: reparameterize onto a fixed mass budget first, then keep volume and footprint as explicit outcome constraints, and score only intensive / physically relevant observables.

A. Is the diagnosis correct?

Yes, with two nuances.

1. The size confound is real and large.
   In `fair_evaluation_analysis.md`, the same 5-D box spans about 6.2× cell mass, 4.7× envelope volume, and 4.0× footprint area. I sanity-checked the geometry independently and got essentially the same order of magnitude: about 6.6× mass, 4.69× volume, and 4.0× footprint spread across corners. That is not a small nuisance. It means the optimizer is comparing different-sized artifacts, not just different shapes.

2. Your objective-normalization read is mostly correct.
   - `SEA_J_per_g` is already mass-normalized by construction. In `bo_evaluator.py`, `sea_J_per_g = (res["sea_Jpkg"] * regime.payload_mass_kg) / cell_mass_g` (lines 362–365 from the quoted code path). So you should not describe SEA as unnormalized on mass. Your markdown already gets this right.
   - `SEA_J_per_g` is not normalized on volume, footprint, or stroke. So for lander work it is still incomplete as a fairness metric.
   - `eta` is dimensionless, so it is intrinsically normalized. But for the lander Tier-C campaign it is nearly constant (`0.732–0.734` in `pareto_render_campaign.md`), so it currently contributes almost no discrimination.
   - `F_peak_N` is not size-normalized. In code it is `peak_g * 9.81 * regime.payload_mass_kg` (line 353), with fixed payload mass per regime. That part is fine. The problem is the observable used for `peak_g`.

3. The observable critique is definitely right for the crutch and directionally right for the lander.
   `sobol_t3_diagnostics.md` shows the crutch payload-acceleration `F_peak` is basically static support load: median ratio to static weight `1.002`. With 75 kg payload, static weight is `75*9.81 = 735.75 N`, which matches the reported crutch `F_peak` span `712–739 N`. So for the crutch, the objective is mostly reading support load, not impact attenuation.

   For the lander, there is one nuance: the Pareto campaign reports `F_peak = 4628–4790 N`. With a 5 kg payload, that corresponds to roughly `94–98 g`, not `~1 g`. So the lander payload-accel channel is not as degenerate as the crutch one. Still, your diagnostics show the floor-reaction channel is the physically better transmitted-load observable, with lander floor-reaction median about `103.5×` static weight. So I would tighten the claim to:
   - crutch Tier-C `F_peak`: essentially a support-load proxy,
   - lander Tier-C `F_peak`: a real transient, but still not the best transmitted-load metric; base reaction is the right bench-matched observable.

4. Why this breaks the lander problem specifically.
   Your own framing is right: for a lander, mass and stowed/deployed volume are binding system budgets, not free variables. If the optimizer is allowed to gain SEA or reduce pressure by just making the absorber larger/heavier, the comparison stops answering the real engineering question. In the crutch regime, the fairness issue matters less because the envelope is looser and the use case is less dominated by strict mass fraction. For the lander, it is a problem-definition error, not just a presentation issue.

B. What are the real lander-module constraints and plausible target values?

I can support the structure of your constraint list strongly. I cannot give a single universal “correct” numeric budget for all landers because that depends on mission class, gravity, soil, terminal velocity, deployment architecture, and whether the absorber is primary EDL hardware or only terminal shock isolation. So the honest answer is: use ranges, not one magic number.

The constraint set you list is the right one:
1. absorber mass budget,
2. stowed and deployed envelope volume,
3. footprint / ground pressure / static stability,
4. available crush stroke / standoff,
5. intensive energy-absorption metrics per mass and per volume,
6. testability within M23.

Suggested working values for a small deployable lander shock-isolator module:

1. Mass budget
   Use a hard absorber mass cap as a fraction of landed mass. For early trade studies I would start with `1–10%` of landed mass as the broad envelope, and `2–5%` as the serious target band for a crush-core-like subsystem. Single-digit percent is the right scale for your study. I would not bake in a narrower number until you tie it to a specific mission architecture.

   For your current 5 kg regime, that implies a first-pass module mass budget of roughly:
   - aggressive: `50–100 g` total absorber allowance,
   - practical starting band: `100–250 g`,
   - upper exploratory cap: `500 g` if this is only a placeholder architecture model.

   Since your current unit cell already spans roughly `9.5–59 g`, the search box is wandering over a huge chunk of that plausible budget range with no accounting. That supports your complaint.

2. Volume / stowage budget
   You should impose a hard deployed envelope cap and probably a stowed-volume cap if the concept is deployable. If you do not yet have mission packaging numbers, I would treat `V*` as a design-study variable and report fronts at 2–3 fixed values rather than one unconstrained sweep.

3. Footprint and ground pressure
   Ground pressure should be encoded through transmitted base reaction over footprint, not footprint alone. Regolith bearing capacity varies wildly with soil state, slope, and dynamic effects, so I would not defend a single kPa number without mission-specific soil assumptions. For a mock-review standard, the safe move is to carry a footprint band `[A_min, A_max]` plus a ground-pressure outcome constraint derived from peak or quasi-static base reaction.

   If you need an early placeholder, define it from allowable sinkage or stability requirements rather than from an unsupported literature cherry-pick. In other words: do not optimize footprint in isolation; optimize `pressure = reaction/area` and stability margin together.

4. Stroke / standoff
   This one you can bound from first principles. To cap peak deceleration at `a_max`, a constant-force ideal absorber needs at least
   `s >= v^2 / (2 a_max)`.
   With `v = 9.8 m/s` and `a_max = 1500 g = 14715 m/s^2`,
   `s_min ≈ 9.8^2 / (2*14715) ≈ 3.3 mm`.

   That is the absolute physics floor for a perfectly rectangular deceleration pulse. Real absorbers need more stroke because pulses are not rectangular, efficiency is below 1, loads are not perfectly axial, and you need margin. With your current `eta ≈ 0.733`, a back-of-envelope adjusted floor is closer to `~4.5–6 mm` even before safety margin. So your stroke/standoff constraint is real, but the current geometry range `H = 60–110 mm` is much larger than the minimum needed purely from the 1500 g cap. That means height in your box is mostly a packaging / shape variable, not a necessity forced by the GEVS cap.

5. Energy-absorption figures of merit
   Your reviewer instinct is right: report both gravimetric and volumetric figures.
   - Gravimetric: `SEA_J_per_g`
   - Volumetric: `SEA_J_per_cm3`

   In crashworthiness and cellular-materials literature, both are standard because one rewards low mass and the other rewards packaging efficiency. Lu and Yu’s crash-energy-absorption framework and Jones’ structural-impact framework both treat mass efficiency and crush stress / volumetric efficiency as separate design concerns, not interchangeable ones. Your lander problem needs both.

6. GEVS / HAVS numbers
   - The `≤1500 g` small-spacecraft shock target is a reasonable engineering proxy, but be careful with wording: GEVS is normally expressed through shock response spectra and qualification environments, not as one universal half-sine scalar for every subsystem. Use your current `1500 g` value as a study target, but cite it as a chosen requirement proxy, not as “the” GEVS number for all cases.
   - For the crutch, a strict `≤8 g peak` criterion is not the same thing as ISO 5349 HAVS, because HAVS is frequency-weighted and exposure-duration based, not a single-peak threshold. So I would soften that language: say the crutch regime uses an internal peak-acceleration target chosen to be conservative relative to HAVS concerns, not that ISO 5349 directly implies `8 g peak`.

C. Normalize objectives vs reparameterize search space: which is sounder?

For the lander, reparameterization is methodologically sounder.

Why:
1. Your dominant constraints are true resource budgets, not preferences.
   Mass budget is not “nice to have.” It is a hard systems constraint. If a design violates it, it is not a candidate. Hard budgets are usually best handled structurally when possible.

2. Equality-type constraints are awkward as outcome constraints.
   A constant-mass manifold is basically an equality constraint. Standard constrained BO, including qNEHVI with feasibility weighting, is much happier with inequality constraints than with a thin equality-feasible set embedded in a box. If you keep the 5-D box and ask the optimizer to find a narrow constant-mass slice through it, you waste samples and make the GP learn a sharp feasible boundary that you already know analytically.

3. Reparameterization removes a known nuisance direction.
   Your present coordinates mix shape and scale. That is bad statistically and physically. Replacing `(R, H, strut_d, cable_d, twist)` with dimensionless shape groups plus one explicit scale variable is cleaner because it aligns the parameterization with the invariants of the problem. That is exactly the logic of Buckingham-π and similitude. A recent paper, Senadeera et al., “Bayesian Optimisation with Dimensionless Groups: A Synergy of Performance and Fundamental Understanding” (Applied Sciences, 2025), explicitly reports faster convergence and better interpretability when BO is done in dimensionless space. That is unusually on-point for your case.

4. It improves interpretability of the Pareto front.
   On a constant-mass manifold, a “better” design really means better shape allocation of the same resource. Right now, part of the front is just “more material.” Reparameterization makes the front honest.

When objective normalization / outcome constraints are still the right move:
- for secondary constraints that are not easy to satisfy analytically,
- when the feasible set is broad and inequality-defined,
- when you want the GP to learn near-boundary behavior because feasibility itself is uncertain,
- when the constraint depends on simulator outputs rather than geometry formulas.

That is why your hybrid is the right recommendation:
- Route A for fixed mass,
- Route B for envelope, footprint, ground pressure, and peak-g constraints,
- intensive objectives for reporting.

What about qNEHVI and GP behavior?
- Constrained qNEHVI is a good fit for inequality outcome constraints like `volume <= V*`, `A_min <= footprint <= A_max`, `peak_g <= g_max`, `pressure <= p_max`.
- It is a poor substitute for an analytically known equality manifold like constant mass.
- If you can solve one variable from the mass equation robustly, do it and search in the lower-dimensional domain. That gives better sample efficiency and cleaner surrogate modeling.

D. How should the constraints be encoded, and what about biased Tier-C?

Use hard feasibility constraints in the problem definition, enforced through constrained acquisition for simulator-derived quantities.

Concretely:

1. Mass, envelope volume, footprint
   - `cell_mass_g <= m*`: hard constraint. Better yet, enforce by construction for the lander.
   - `envelope_cm3 <= V*`: hard outcome constraint.
   - `A_min <= footprint_mm2 <= A_max`: hard outcome constraint if footprint itself matters for stability and packaging.

   If you switch to pressure-based reasoning, then footprint can be partly replaced by:
   - `peak_ground_pressure_kPa = peak_base_reaction / footprint <= p_max`
   plus perhaps a minimum radius or stability-margin constraint.

2. Peak-g limits
   - Crutch: `transmitted_accel_metric <= target`, but only after you define the right metric. If the bench standard is weighted acceleration or a filtered time-domain peak, optimize that exact observable.
   - Lander: `base_reaction_derived_peak_g <= 1500` as a hard outcome constraint.

   Do not use soft penalties here unless the requirement is genuinely negotiable. If exceeding 1500 g means mission failure, it is a hard constraint.

3. Hard penalties vs constrained qNEHVI
   Since you are already in Ax/BoTorch territory, constrained qNEHVI is the right default. Hard-coded `_INFEASIBLE_*` penalties are acceptable for geometry / printability filters, but less attractive for physics constraints because they collapse all infeasible designs onto the same fake response and can distort the surrogate. Feasibility-weighted acquisition is cleaner.

4. Interaction with biased Tier-C
   This part matters a lot. You should not impose hard constraints on a biased cheap observable as if it were truth.

   I would separate constraints into three classes:
   - Analytic geometry constraints: hard, trusted, enforce exactly.
   - Bench-matched Tier-C observables with decent validity: hard or feasibility-weighted.
   - Known-biased Tier-C proxies: do not use as mission-critical hard constraints.

   In your case:
   - mass, volume, footprint: trusted, hard.
   - base reaction at Tier-C: probably acceptable as the lander transmitted-load objective/constraint if it matches what the platen measures.
   - payload-accel `F_peak`: not acceptable as the main hard constraint.
   - `eta` in the lander Tier-C model: not useful enough to drive decisions.

   If you keep a multi-fidelity stack, the principled route is: enforce geometry budgets at all fidelities, use Tier-C for coarse feasibility screening, and reserve final peak-g acceptance for Tier-B/A or experiment.

E. Priority list: highest-value changes

I’d do these in this order.

1. Replace the lander evaluation observable.
   First fix `F_peak` so the lander campaign optimizes base reaction / transmitted-load peak or derived peak-g, not the current payload-accel proxy. Without this, the lander objective is pointed at the wrong physics channel.

2. Add explicit size metrics to the evaluator output.
   Return `cell_mass_g`, `envelope_cm3`, `footprint_mm2`, and `SEA_J_per_cm3` from `evaluate_design`. This is cheap and immediately makes every campaign auditable.

3. Reparameterize the lander search onto a constant-mass domain.
   This is the biggest fairness fix. Use shape ratios such as `H/R`, `H/strut_d`, `cable_d/strut_d`, and `twist`, then solve one geometric variable to satisfy `cell_mass = m*`. If the solve produces an out-of-bounds diameter, reject that ratio tuple. This directly answers the real question: best shape for a fixed mass budget.

4. Add constrained qNEHVI for the remaining lander budgets.
   Keep `envelope_cm3 <= V*`, footprint or pressure bounds, and `peak_g <= 1500` as explicit outcome constraints. This is where constrained BO helps.

5. Re-run the lander Pareto study on several fixed budgets, not one giant unconstrained box.
   I would generate separate fronts for 2–3 mass budgets and maybe 2 envelope budgets. That will show whether the preferred shape is stable across realistic resource levels. It is more informative than one smeared front.

A couple of things I would change in the writeup language

1. Don’t say all three current objectives are unfair.
   Say:
   - `SEA_J_per_g` is fair on mass but incomplete for lander because it ignores volume and footprint.
   - `eta` is intrinsically normalized but presently non-discriminating.
   - `F_peak` is the main observable problem.

2. Be careful with the GEVS and HAVS wording.
   Use them as requirement proxies, not literal one-number standards unless you quote the exact source and test condition.

3. Be explicit that the current Tier-C lander front is not wrong, just answering a different question.
   It is finding good designs in an unconstrained variable-size family. That is a valid exploratory study. It is not a fair fixed-budget lander design comparison.

Bottom line

As a mock reviewer, I’d support your main recommendation.

For the lander, the right scientific move is:
- reparameterize to fixed absorber mass,
- optimize in dimensionless shape variables,
- constrain volume and footprint/pressure explicitly,
- replace payload-accel `F_peak` with base reaction,
- report both `SEA_J_per_g` and `SEA_J_per_cm3`.

That turns the campaign from “which design wins when size is free?” into the question you actually care about: “for a fixed mass budget and allowed package, which shape gives the best protection?”

Sources cited

Project artifacts reviewed:
- `/workspace/e43abed6-2fac-4d93-a169-bc6cf9cc8116/fair_evaluation_analysis.md`
- `/workspace/e43abed6-2fac-4d93-a169-bc6cf9cc8116/bo_evaluator.py`
- `/workspace/e43abed6-2fac-4d93-a169-bc6cf9cc8116/regimes.py`
- `/workspace/e43abed6-2fac-4d93-a169-bc6cf9cc8116/pareto_render_campaign.md`
- `/workspace/e43abed6-2fac-4d93-a169-bc6cf9cc8116/sobol_t3_diagnostics.md`

Methodology / background references:
- Daulton S, Balandat M, Bakshy E. Differentiable Expected Hypervolume Improvement for Parallel Multi-Objective Bayesian Optimization. NeurIPS 2020.
- Daulton S, Balandat M, Bakshy E. Parallel Bayesian Optimization of Multiple Noisy Objectives with Expected Hypervolume Improvement. NeurIPS 2021.
- Jones N. Structural Impact. Cambridge University Press.
- Lu G, Yu T. Energy Absorption of Structures and Materials. Woodhead.
- Barenblatt GI. Scaling. Cambridge University Press.
- Senadeera M et al. Bayesian Optimisation with Dimensionless Groups: A Synergy of Performance and Fundamental Understanding. Applied Sciences. 2025. Search result/full-text snippet retrieved via `e14c.web.web_search`.

Limitations

I cannot defend a single literature-grounded numeric target for absorber mass fraction, regolith pressure, or volumetric SEA across all “scaled-up lander module” concepts because the workspace does not contain mission-specific systems requirements, and the web search results available here were not sufficient to extract a clean, audited heritage table without risking overclaiming. The ranges above are therefore engineering starting bands, not final cited requirements. If you want, the next clean step is a dedicated source-traceable benchmark table built from mission design docs and crashworthiness reviews.

- Discretionary analytical decisions made during the analysis:
  - Treated the project markdown/code artifacts as primary evidence and used web search only for background/methodology support because no curated literature corpus was provided.
  - Performed an independent geometric sanity check of mass/volume/footprint spread using a simplified T3-prism length model to verify the confound magnitude rather than attempting to reproduce the full simulator.
  - Chose not to report p-values or inferential tests because the request was methodological review of deterministic campaign setup, not statistical hypothesis testing on sampled experimental replicates.
  - Interpreted the lander `1500 g` and crutch `8 g` values as engineering requirement proxies rather than literal universal standards, due to limited source traceability in the provided materials.
  - Recommended reparameterization for the mass budget and constrained qNEHVI for remaining inequalities, rather than a pure constraint-only approach, because the mass constraint is analytically known and effectively equality-like.
