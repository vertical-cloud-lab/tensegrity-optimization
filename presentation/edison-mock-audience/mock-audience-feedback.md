# Mock audience report: IDETC-CIE 2026 DAC-10 talk

## Scope of this review

This evaluates the talk implied by the outline, not finished slides or delivery technique. The experimental campaign is still in progress, so I do **not** infer any favorable results. The empty “Evidence / results” section is treated as a major unresolved part of the talk: the outline currently explains why the workflow should be useful, but does not yet demonstrate that it is useful.

The central communication test is whether each listener leaves with the intended message:

> By closing the loop between multi-material 3D printing and Bayesian optimization, we can optimize tensegrity energy absorbers directly from real impact data, in dozens of prints rather than thousands.

---

# P1. The skeptical Bayesian-optimization insider

## (a) First-person reaction

The application is potentially interesting, and the design–print–test loop is easy to understand. The mixed continuous, integer, and categorical design space, physical failures, parallel fabrication, and multiple constrained objectives could make this a worthwhile design-automation case study.

But the outline keeps telling me that Bayesian optimization is sample-efficient without showing that **this implementation** is sample-efficient. “Dozens, not thousands” sounds like a slogan unless I see the actual experiment count, initialization size, batch size, replication policy, convergence behavior, and a comparison against credible alternatives. q-noisy expected hypervolume improvement, or qNEHVI, is established machinery. Merely deploying it does not establish methodological novelty.

I become skeptical at the statement that qNEHVI was selected because of heteroscedastic TPU and print noise. qNEHVI accounts for noisy observations, but the outline does not explain how the surrogate models heteroscedasticity, whether repeated specimens identify noise, or whether noise is being conflated with unmodeled process drift. Independent Gaussian processes with an unspecified observation model do not automatically resolve batch-dependent heteroscedasticity.

My attention drifts during the broad argument against simulation because it delays the information I came to DAC-10 to hear: the design variables, model formulation, constraint handling, acquisition implementation, budget, and benchmark. The Super Ball Bot hook is visually effective, but planetary landing may feel like application theater if the actual specimens and impact regime are far removed from that use case.

The strongest possible section is the results slot. In its current empty state, the talk has a method narrative but no validation.

## (b) What I would repeat the next day

> “They used standard batch noisy multi-objective Bayesian optimization to choose which multi-material printed impact specimens to test, instead of running a full physical sweep.”

**Distortion from the intended message:** I would omit the claim that the structures were optimized in dozens of prints because I have not seen evidence for it. I would also describe qNEHVI as standard rather than as the contribution.

## (c) Top three Q&A questions

1. **What is the actual experimental budget?** How many initial designs, adaptive iterations, specimens per batch, and physical replicates were used, and what stopping rule defined success?
2. **What baselines did you beat?** Did you compare qNEHVI with Sobol or Latin-hypercube sampling, random search, scalarized Bayesian optimization, or a domain-informed sequential design under the same number of physical tests?
3. **How exactly is noise modeled?** Are replicate-dependent variances supplied to the Gaussian processes, is a heteroscedastic likelihood fitted, and how are TPU lot, print batch, machine drift, and specimen-level defects distinguished?

## (d) Most pointed challenge

> “What did you contribute beyond applying off-the-shelf qNEHVI to a new specimen family?”

**Damage if unanswered: severe.** For a DAC review audience, this can reduce the work from a design-automation contribution to an application demonstration. A strong answer could rest on the experimental formulation, mixed-variable and failure-aware implementation, quantitative sample-efficiency evidence, and transferable operating lessons. Those contributions must be stated explicitly and tested.

---

# P2. The aerospace entry, descent, and landing practitioner

## (a) First-person reaction

The opening lands immediately. I recognize the Super Ball Bot concept, and “the lander is the energy absorber” is a useful framing. The three performance quantities also sound relevant: energy absorbed per mass, usable stroke, and force transmitted to the payload.

Then the talk moves into language I do not naturally use: Gaussian-process surrogate, qNEHVI, acquisition function, hypervolume, exploration versus exploitation, and Pareto front. I can accept that the algorithm chooses the next tests, but I need a plain explanation of what information it uses and why I should trust the recommendations. If the presenter spends several minutes naming algorithms without connecting them to engineering decisions, I will lose the thread.

My main concern is application fidelity. A desktop drop-weight test at one fixed impact energy is not automatically evidence for entry, descent, and landing hardware. I need specimen dimensions, impact mass, velocity, energy, strain rate, boundary conditions, number of impacts, rebound behavior, temperature, vacuum sensitivity, and failure containment. PLA and TPU raise immediate environmental and qualification questions. I also want to know whether the absorber is reusable or sacrificial.

My attention returns when I see force–time traces, high-speed footage, and damaged specimens. It drifts if the talk stays on the optimizer rather than connecting each output to payload protection.

## (b) What I would repeat the next day

> “They have an algorithm that learns from successive drop tests and tells them which 3D-printed crush structure to make next, so they can find a lightweight low-force design with fewer prototypes.”

**Distortion from the intended message:** I would probably call the structures “crush structures,” losing the tensegrity distinction. I might also overgeneralize the method to planetary landers even though the current tests appear to be laboratory-scale.

## (c) Top three Q&A questions

1. What impact mass, velocity, energy, and strain-rate regime do the tests cover, and how do those values compare with a credible lander load case?
2. How do the selected designs scale with size and impact energy? Are the controlling mechanisms material-rate effects, geometric buckling, contact, or all three?
3. What happens under off-axis impact, repeated impacts, temperature extremes, aging, vacuum, and manufacturing defects?

## (d) Most pointed challenge

> “Why should I believe that a PLA–TPU specimen optimized at one laboratory impact condition tells me anything about flight-scale landing protection?”

**Damage if unanswered: severe for the planetary-landing framing, moderate for the underlying optimization study.** The presenter should clearly label planetary landing as motivation, not demonstrated readiness, and state the present technology scope. Otherwise the opening and closing overpromise relative to the reported experiment.

---

# P3. The additive-manufacturing and materials researcher

## (a) First-person reaction

The monolithic PLA–TPU architecture is the part I care about. The core-wrapping strategy sounds more credible than simply depositing TPU against exposed PLA and assuming durable adhesion. Holding print settings fixed within a batch, weighing specimens, checking dimensions, and periodically testing a control are all sensible.

I still need much more fabrication detail before I accept that design geometry is the main source of performance variation. PLA–TPU interfaces are sensitive to temperature, surface contact, moisture, residence time, toolpath order, contamination, and local geometry. “Print defects” is too broad. I want failure-mode evidence showing whether energy is absorbed through intended tension-network deformation, TPU hysteresis, strut buckling, interface peeling, or accidental damage.

The phrase “no assembly” catches my attention, but “eliminates assembly entirely” may be too strong. Does the build require support removal, trimming, conditioning, fixture insertion, post-tensioning, or manual alignment? If so, the accurate claim is “single-build co-fabrication” or “no joining of PLA and TPU members,” not zero assembly.

I am a Bayesian-optimization novice. I can follow the loop if the presenter says, “The model proposes the next small batch where improvement is plausible or uncertainty is high.” I will disengage if the slide foregrounds qNEHVI notation rather than the physical decisions it enables.

## (b) What I would repeat the next day

> “They co-print rigid PLA and flexible TPU energy absorbers, test them, and use the results to choose the next geometries instead of printing a large design-of-experiments grid.”

**Distortion from the intended message:** I would remember the fabrication loop more strongly than tensegrity or Bayesian optimization. I might interpret the improvement as mostly a material-interface result unless the structural mechanisms are shown.

## (c) Top three Q&A questions

1. How was PLA–TPU bonding quantified, and where did failed specimens actually fail: within TPU, within PLA, or at the interface?
2. How many nominally identical replicates were printed and tested, and how large were within-batch, between-batch, and printer-drift effects relative to design effects?
3. What manual operations occur after printing, and what exactly does “no assembly” exclude?

## (d) Most pointed challenge

> “How do you know the optimizer is learning architecture rather than uncontrolled interface quality and process drift?”

**Damage if unanswered: severe.** If fabrication variation is not measured and separated from design effects, both the surrogate and the claimed Pareto front may be unstable. Replicates, blocking or covariates, control specimens, dimensional measurements, and failure-mode documentation are needed.

---

# P4. The first-year graduate student

## (a) First-person reaction

The opening video and the phrase “the lander is the energy absorber” give me a concrete picture. I understand the basic problem: too many designs to print, and computer models may miss messy material behavior. I also understand the loop when it is described as “design, print, drop, learn, repeat.” That story carries me.

I start getting lost when several unfamiliar terms arrive together: tensegrity-inspired, compaction efficiency, Gaussian process, surrogate, acquisition function, qNEHVI, heteroscedastic noise, Pareto front, probabilistic feasibility constraint, and exploration versus exploitation. The preview says the audience already believes optimization works, but I still need one intuitive sentence explaining what Bayesian optimization does. Skipping “Bayesian optimization 101” should not mean skipping the conceptual bridge.

I am also unsure how the structure works. Are the TPU parts stretched before impact? Are the PLA struts touching? What makes this “tensegrity-inspired” rather than a multi-material lattice? A labeled specimen image and a short deformation sequence would help much more than a verbal definition.

My attention drifts during the repeated case against simulation because I accepted that point the first time. It returns for printing footage, the drop test, and a clear plot with a marked “better” direction.

## (b) What I would repeat the next day

> “They let an artificial-intelligence program learn from 3D-printed drop tests and keep suggesting better shock absorbers, so they do not have to test every design.”

**Distortion from the intended message:** I would probably call Bayesian optimization “AI,” omit the two-objective trade-off and force constraint, and assume each new design is simply better than the last. I might also miss what tensegrity contributes.

## (c) Top three Q&A questions

1. What makes one of these specimens a tensegrity structure rather than an ordinary 3D-printed lattice?
2. How does the computer decide which design to print next, in plain language?
3. Can one design maximize both energy absorption and compaction efficiency while also lowering peak force, or must those goals trade off?

## (d) Most pointed challenge

> “I followed the loop, but I still do not understand what is physically special about the structure or what the optimizer actually learned.”

**Damage if unanswered: moderate.** Experts can fill in some gaps, but a talk that leaves novices with only “AI plus 3D printing” has failed to communicate its engineering mechanism. One specimen-mechanics visual and one plain-language optimization visual would largely solve this.

---

# P5. The finite-element-analysis veteran

## (a) First-person reaction

The statement “simulation can’t be trusted for these structures” puts me on the defensive before I have seen any evidence. Interfacial slip, viscoelasticity, large deformation, buckling, contact, strain-rate dependence, and manufacturing variability are difficult, but they are not intrinsically beyond finite-element analysis. Models can be calibrated, uncertainty can be propagated, and simulation can still screen designs even if it is imperfect.

The abstract is more defensible than the talk outline. It says the workflow avoids **direct dependence on calibrated finite-element simulation for objective evaluation** and acknowledges future analytical or multifidelity shortcuts. The presentation should use that language. The current outline turns a project-scope choice into a universal technical claim.

I accept the economic argument that calibrating a high-fidelity model may not be worthwhile for an early design campaign. That is a stronger position: measured tests provide authoritative objective values, while the study asks whether sequential design can use a small physical budget efficiently. I would also welcome evidence that simulation errors change design rankings or miss observed failure modes. Without such evidence, the repeated attack on simulation sounds like a straw man.

My attention drifts when the talk says simulation is unreliable several times without showing a simulation–experiment discrepancy. It returns when the presenter discusses physical failure modes and admits where lower-fidelity physics could later improve the loop.

## (b) What I would repeat the next day

> “They skipped finite-element modeling and used Bayesian optimization directly on physical tests because they judged model calibration too expensive for these multi-material specimens.”

**Distortion from the intended message:** I would frame the work as bypassing simulation rather than as enabling rapid experimental optimization. If the presenter is combative about simulation, that dispute may become the only thing I remember.

## (c) Top three Q&A questions

1. What evidence shows that a calibrated finite-element model is insufficient for design ranking, rather than merely costly to construct?
2. Did you compare the physical-test-only workflow with a simple mechanics model or multifidelity surrogate that could reduce the experimental budget further?
3. Which observed behaviors dominate the model discrepancy: interface failure, TPU viscoelasticity, contact, buckling imperfections, or geometry errors from printing?

## (d) Most pointed challenge

> “You have shown that simulation is inconvenient, not that it cannot be trusted. Why is abandoning it scientifically preferable to calibrating and validating it?”

**Damage if unanswered: severe and avoidable.** The current absolute wording invites a technical fight that is unnecessary to the contribution. Reframing the claim as a cost-and-dependence decision would preserve the motivation without asserting that finite-element modeling is incapable.

---

# P6. The friendly industry generalist

## (a) First-person reaction

The loop is memorable: print a candidate, test it, update the model, and print the next informative candidate. I can imagine using that pattern for brackets, seals, lattice pads, or process settings when simulation is weak and tests are expensive. “Dozens rather than thousands” is exactly the kind of value proposition I remember.

I do not need the mathematical details of qNEHVI, but I need an operational recipe. What software is used? How many initial samples are required? How automated is the handoff from optimizer to computer-aided design and slicing? How long does one cycle take? What expertise does a team need? The abstract says candidate selection is automated but slicing, specimen handling, and testing remain manual. That qualification should appear in the talk before I infer a robotic self-driving laboratory.

The tensegrity and planetary material is interesting, but my attention will drift if it occupies too much of a 15-minute slot. The method becomes useful to me only when the presenter explicitly generalizes it and defines when it is worth using.

The ending about moving humankind forward is less memorable than a concrete deployment rule. I would prefer a final slide saying: “Use this loop when tests are authoritative, each test is costly, the design space is mixed, and several performance goals conflict.”

## (b) What I would repeat the next day

> “They showed a practical test-driven optimization loop that can find good 3D-printed designs with a few dozen prototypes instead of a giant test matrix.”

**Distortion from the intended message:** I may overstate automation and assume the “few dozen” claim is established across applications. I will probably forget the names qNEHVI and tensegrity, but retain the workflow.

## (c) Top three Q&A questions

1. What parts of the workflow are automated today, and what does an engineer still do manually between recommendation and test result?
2. What minimum experiment budget and software stack would my team need to try this on a different component?
3. When is this approach better than a conventional design of experiments, response-surface method, or a calibrated simulation?

## (d) Most pointed challenge

> “What concrete evidence tells me this saved enough prototypes and engineering time to justify the added optimization infrastructure?”

**Damage if unanswered: moderate to severe.** I will still like the idea, but I will not take it back to my team. A budget-matched baseline and a simple timeline or cost comparison would convert interest into action.

---

# Synthesis

## Cross-persona themes

### 1. The causal chain is understandable, but the claimed payoff is not yet demonstrated

All six personas can understand the basic design–print–test–learn loop. The empty results section prevents them from deciding whether the loop actually found better designs, found them faster, or handled noise reliably. The phrase “dozens, not thousands” is currently an unsupported quantitative claim.

At minimum, the results need to show:

- total number of unique designs and physical specimens;
- initial versus adaptively selected designs;
- batch size and number of iterations;
- replicate policy and failure count;
- measured uncertainty or repeatability;
- progress under the actual experimental budget;
- the final feasible Pareto set for **specific energy absorption and compaction efficiency subject to the force cap**;
- a budget-matched nonadaptive or simpler optimization baseline.

### 2. “Simulation can’t be trusted” is too absolute

P1 questions the evidence, P2 cares about application validity, and P5 directly rejects the premise. Even P6 needs to know when the loop is preferable to simulation. The abstract already contains better wording: physical measurements are used for objective evaluation “without relying on calibrated finite-element simulation.”

The defensible claim is not that simulation fails universally. It is that a sufficiently calibrated multiphysics model may be expensive relative to the available design campaign, and the authors therefore test whether physical-data-driven sequential optimization is useful without depending on such a model.

### 3. The talk needs a two-level explanation of Bayesian optimization

P1 does not want introductory Bayesian-optimization material; P2, P3, P4, and P5 need a plain conceptual bridge. These needs are compatible. Give the intuition in one sentence and one visual, then put the implementation specifics in a compact technical panel or backup slide.

Suggested spoken explanation:

> “After each batch, the model estimates both expected performance and uncertainty across the design space. The acquisition rule selects a small next batch that is most likely to expand the feasible trade-off frontier, while accounting for noisy tests and print failures.”

This is not “Bayesian optimization 101.” It is the minimum explanation needed to interpret the workflow.

### 4. The physical mechanism and the word “tensegrity” need clarification

P2 may reduce the objects to crush structures, P3 may interpret the result as an interface study, and P4 may not distinguish the specimens from ordinary lattices. A labeled as-printed specimen plus a four-frame deformation sequence should show:

- rigid PLA struts;
- continuous flexible TPU network;
- whether and how pre-tension exists;
- load path before and during impact;
- intended energy-dissipation mechanisms;
- why “tensegrity-inspired” is the precise term.

### 5. Manufacturing variability is part of the model, not background noise

P1 and P3 will both press this point. Periodically retesting one control is useful but may not identify design-specific heteroscedasticity, lot effects, or confounding between iteration and material batch. The talk needs to state the replication, randomization, blocking, covariate, and drift-monitoring plan. If those steps were not used, the limitation must be explicit.

### 6. The application framing outruns the demonstrated scope

The planetary hook is strong, but P2 will not equate fixed-energy laboratory tests on PLA–TPU specimens with flight hardware. The closing escalates further by claiming that the next lander absorber can be “proven” in weeks. That wording should be narrowed unless the campaign includes relevant scaling and environmental evidence.

### 7. The objective statement is not fully consistent across the outline

The task and Point 2 correctly describe two objectives, specific energy absorption and compaction efficiency, with a peak-force constraint. The candidate evidence list instead proposes “SEA vs. peak transmitted force,” and the abstract’s expected-outcomes section similarly describes trade-offs between SEA and peak force. Those are different optimization formulations.

The talk must consistently distinguish:

- **objectives:** maximize specific energy absorption and compaction efficiency;
- **constraint:** peak transmitted force must not exceed a specified cap;
- **feasible Pareto front:** trade-offs between the two objectives among designs satisfying that cap.

If peak force is instead treated as a third objective, the task statement and optimization formulation must be revised accordingly.

### 8. The closing favors inspiration over technical precision

P6 is likely to remember “dozens, not thousands,” but P1, P2, and P5 may hear overreach in “proven,” “in weeks,” and “moves humankind forward.” A DAC-10 close should end on the measured engineering result and transfer condition. The Super Ball Bot bookend can remain, but it should not imply flight qualification.

---

# Three highest-priority revisions

## Priority 1: Build the talk around a quantitative result, not around the availability of a workflow

Replace the placeholder with a required three-slide evidence sequence:

1. **“The campaign used N specimens across B adaptive batches under a fixed physical-test budget.”**  
   Show initialization, adaptive batches, replicates, failures, elapsed cycle time, and the force threshold. Do not use `N` or `B` in the actual talk; insert the observed values.

2. **“Adaptive selection improved the feasible design set faster than [predeclared baseline].”**  
   Plot a budget-matched performance measure across physical tests, with uncertainty across repeated runs if available. If only one physical campaign exists, avoid inferential claims that require repeated campaigns and supplement with clearly labeled retrospective resampling or simulation-based algorithm checks.

3. **“These measured designs form the final feasible trade-off between specific energy absorption and compaction efficiency.”**  
   Show uncertainty or replicate spread, mark infeasible force-cap violations, and include specimen images or force–time traces for representative Pareto designs.

If the campaign cannot support those statements, revise the main message from “we can optimize … in dozens” to “we are evaluating whether noisy multi-objective Bayesian optimization can reduce the physical test budget.”

## Priority 2: Replace the anti-simulation premise with a scoped engineering decision

Replace:

> “Simulation can’t be trusted for these structures.”

with:

> “For these multi-material prints, obtaining objective values from a validated high-fidelity model would require substantial calibration of interface, rate, contact, and defect behavior. We therefore ask how far a limited budget of direct physical tests can take us without depending on that model.”

Then title Point 1 with a message rather than a topic:

> **“When model calibration and exhaustive testing are both costly, each physical specimen must be chosen for information value.”**

This keeps the pincer structure while avoiding an unnecessary universal claim.

## Priority 3: Reallocate the 15 minutes around audience decisions

A concrete timing plan:

- **1.5 min:** Super Ball Bot hook, specimen, and present study scope.
- **2 min:** Why exhaustive physical search and high-fidelity calibration are costly.
- **2.5 min:** One visual of the closed loop, including a one-sentence Bayesian-optimization explanation.
- **2 min:** Actual design variables, objectives, force constraint, fabrication failures, and noise controls.
- **5 min:** measured results, baseline, uncertainty, representative specimens, and failure modes.
- **1 min:** limitations and transfer conditions.
- **1 min:** measured conclusion and bookend.

Move kernel choices, log-space acquisitions, detailed encoding, and other implementation material to backup slides unless a result depends directly on them. This follows Doumont’s principle that each slide should communicate one interpreted message rather than expose the speaker’s notes.

---

# Claims needing evidence, hedging, or backup slides

| Claim or topic | What is needed in the main talk | Prepared backup material |
|---|---|---|
| “Dozens of prints, not thousands” | Actual specimen count, definition of success, and budget-matched comparator | Full campaign ledger; sensitivity to initialization and stopping rule |
| “Simulation can’t be trusted” | Replace with scoped calibration-cost language unless direct validation evidence exists | Simulation–experiment traces, ranking errors, or documented failure modes a tested model missed |
| “qNEHVI handles heteroscedastic noise” | Specify the actual observation-noise model and replication strategy | Likelihood formulation, fixed versus inferred noise, residual diagnostics, replicate variance by design or batch |
| qNEHVI “over standard expected improvement” | Use a technically appropriate comparison; ordinary expected improvement is not a like-for-like multi-objective batch baseline | Comparisons with random/Sobol, scalarization, qEHVI or another relevant noisy/constrained baseline |
| “The Pareto front is the design deliverable” | Show the two stated objectives and force-cap feasibility consistently | Hypervolume reference point, normalization, uncertainty, constraint treatment |
| Peak-force cap | State its numerical value and engineering rationale | Sensitivity of selected designs to alternative cap values |
| Probabilistic print-feasibility constraint | Report failures and demonstrate that the classifier or constraint model is identifiable at the available sample size | Failure labels, calibration, confusion or reliability metrics, acquisition formula |
| “No assembly” / “eliminates assembly entirely” | List any post-print operations; use “single-build co-fabrication” if manual steps remain | Fabrication workflow photographs and labor-time accounting |
| “Candidate goes to tested specimen in hours” | Median or representative print-to-result time and what remains manual | Time breakdown for design, slicing, printing, conditioning, inspection, and testing |
| “Dramatically faster” | Define faster relative to a measured or estimated comparator | Cost and wall-clock accounting with assumptions |
| Transfer to other architectures | Present as a conditional hypothesis, not a demonstrated result | Applicability checklist: test cost, dimensionality, noise, throughput, and constraint structure |
| Planetary-landing relevance | Clearly state that this is motivation unless scale and environment are tested | Impact similitude, energy and velocity regime, environmental gaps, technology-readiness discussion |
| PLA–TPU interface robustness | Failure-mode and repeatability evidence | Microscopy or fracture images, process parameters, conditioning and moisture controls |
| “Tensegrity-inspired” | Show the load path and identify which tensegrity features are retained | Geometric definition, pre-tension status, comparison with a conventional lattice/control |
| Independent Gaussian processes | State why cross-objective correlation is ignored and whether that choice matters | Residual correlations and sensitivity to multi-output alternatives |
| Mixed categorical variables | Briefly state how candidates are represented and optimized | Kernel or encoding details; treatment of invalid combinations |

---

# Fit to the six-person audience

## Best served: P6, the friendly industry generalist

The outline has a clear problem–method–application arc, a memorable loop, and an attractive efficiency promise. P6 can understand the proposed value without needing the mathematics. The danger is that this persona may accept unsupported claims and overestimate the system’s automation and maturity.

P4 also benefits from the story structure, but the unexplained terminology and absent physical-mechanism visual will cause substantial loss of detail.

## Worst served: P1, the skeptical Bayesian-optimization insider

P1 is the most likely to judge the current talk as an off-the-shelf acquisition function applied to a new artifact. The outline anticipates this concern by saying not to teach Bayesian optimization, but it does not yet supply the evidence P1 needs: novelty positioning, rigorous baseline, budget, noise identification, constraint diagnostics, and measured sample efficiency.

P5 is nearly as poorly served because the opening motivation directly challenges finite-element modeling more strongly than the abstract supports.

## Is that the right trade-off for DAC-10?

No. A DAC-10 presentation should remain accessible to P2–P6, but it cannot underserve P1. The design-automation expert is likely to shape the technical discussion and the perceived contribution. Accessibility should come from a plain-language loop and strong visuals, not from omitting methodological validation. The best target is a two-layer talk: every listener can follow the engineering decision, while experts can see the experimental budget, comparator, noise model, and constraint formulation.

---

# Predicted reception

**Current outline: 5/10.** The loop and application are memorable, but without measured results, a budget-matched baseline, and narrower simulation and planetary claims, the talk reads as a polished motivation for an experiment rather than a completed DAC-10 contribution.

If the results establish repeatability and budgeted improvement, and the three priority revisions are made, the same structure could plausibly move into the **7–8/10** range. That conditional estimate is a judgment about presentation readiness, not a prediction of unobserved experimental outcomes.

---

# Discretionary analytical decisions

- Treated the unfinished evidence/results section as missing evidence rather than assuming that the planned campaign succeeds.
- Evaluated the artifact as a competent 15-minute delivery from the outline, not as a line edit of the outline or an assessment of slides that do not yet exist.
- Weighted technical credibility and evidentiary support more heavily than visual polish because the target is the DAC-10 design-optimization audience.
- Used the submitted abstract to resolve technical intent when the outline was ambiguous, while flagging inconsistencies rather than silently harmonizing them.
- Interpreted the stated optimization problem as two objectives, specific energy absorption and compaction efficiency, subject to a peak-force constraint; flagged language that instead treats peak force as an objective.
- Assigned qualitative damage levels of moderate, moderate-to-severe, or severe based on how directly an unanswered challenge would undermine each persona’s acceptance of the central claim.
- Chose P6 as the best-served persona because the present outline emphasizes an intuitive workflow and practical efficiency promise; chose P1 as the worst-served because the DAC-specific validation and novelty case is not yet developed.
- Scored predicted reception on the current incomplete outline, not on a hypothetical final talk with successful results.