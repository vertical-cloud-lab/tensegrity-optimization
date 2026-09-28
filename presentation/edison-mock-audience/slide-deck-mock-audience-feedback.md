# Mock audience report: IDETC-CIE 2026 slide deck, Draft 1

## Executive read

The visible deck has a clear visual spine: **motivation → slow iteration → Bayesian optimization → multi-material printing → impact testing → closed loop → future applications**. The strongest section is slides 8–10, where fabrication, testing, and adaptive selection finally appear as one workflow.

But Draft 1 does not yet deliver the technical case promised by the agreed outline. The visible deck omits four things a DAC-10 audience will need:

1. **Honest scope:** no visible slide says that the PLA–TPU T3 prism is a proxy system rather than flight hardware.
2. **A precise optimization problem:** the six variables, two objectives, force constraint, noise treatment, and fabrication failures are not intelligible on slide 7.
3. **Quantitative evidence:** the sole results slot is hidden and empty, yet slides 10 and 12 already claim acceleration and transfer.
4. **A measured conclusion:** the talk jumps from the workflow to speculative applications without showing a campaign ledger, comparison against a budget-matched baseline, or feasible Pareto front.

The slide titles generally follow Doumont’s full-sentence-message rule, but several messages outrun the evidence. The deck also departs substantially from the Draft 3 timing plan, which reserves **5 of 15 minutes for results**. As built, results receive zero visible slides.

---

# P0. The program manager in the audience

## (a) My reaction in the room

Slide 1 tells me the team wants to work faster, but it does not tell me what is being optimized or what has actually been built. The title sounds aspirational rather than traceable to a project deliverable. I immediately want the formal title from the abstract or a shorter version of it.

The Super Ball Bot footage on slide 2 is an effective hook. I understand why reusable impact attenuation matters. But the slide creates a scope risk: I am looking at planetary landing hardware while the actual work is a printed PLA–TPU T3 proxy. Because that distinction is not stated immediately, I may spend the rest of the talk evaluating the work against flight-readiness criteria the project never intended to meet.

Slide 4 gives me the business problem, but not a baseline. “Slow and resource intensive” needs a number: hours per print-test cycle, number of factors, or the candidate count under a declared design of experiments. Without that, I cannot assess whether the proposed loop attacks the dominant schedule driver.

Slide 7 is where I expect the project definition. Instead, “6 variables,” “2 types of input data,” and “2 objectives” read like inventory labels. I cannot reconstruct the statement of work from them. I need to see what is automated, what remains manual, what the force cap is, and what constitutes a successful campaign.

Slides 8 and 9 make the project tangible. A labeled specimen and an actual drop test would build confidence. Yet “single-build” and “no joining” need a process qualification caveat, and I need the measurement chain to be explicit. The abstract refers to an instrumented tup and force–time data; slide 9 says accelerometers. Those may be compatible, but the deck presently leaves the relationship unclear.

Slide 10 is the right management view of the system, but “significantly accelerate” is a result claim placed on a workflow diagram. At this point I ask, “Compared with what, by how much, and over how many specimens?” Then the deck skips the hidden results slide and goes directly to future applications. That is the point where my confidence drops sharply. The project is asking me to extrapolate before closing the evidence loop.

Slide 12 is too early and too broad. A crutch tip and lattice can be legitimate next phases, but only after the team shows what the present campaign established and what technical risks remain. The blank questions slide gives me no durable take-home message.

### PM stage-risk register

| Risk | Likelihood | Consequence | Mitigation |
|---|---:|---:|---|
| Results are incomplete by conference lock | Medium to high | Critical: central claim becomes unsupported | Set a dated campaign freeze; predeclare a fallback message and minimum publishable result package |
| Embedded Super Ball Bot or drop-test video fails | Medium | Moderate: weak opening or broken pacing | Use local, trimmed files; retain a still-frame fallback on every video slide |
| Talk overruns because several videos and explanations are improvised | High | High: results or conclusion gets cut | Script videos to 10–15 seconds total each; rehearse to 13:30; assign 5 minutes to results |
| Scope is mistaken for flight-hardware validation | High | High: credibility damage in Q&A | Put “PLA–TPU T3 proxy; not flight hardware” on slide 2 or the next slide |
| Acceleration claim lacks a budget-matched comparator | High | Critical for DAC review audience | Show Sobol/random or another predeclared baseline at the same physical-test budget |
| Measurement chain is challenged | Medium | High | Add a methods schematic and backup slide on calibration, sampling, filtering, and metric extraction |
| “No joining” or “near autonomous” is read as full automation | Medium | Moderate | List manual steps explicitly: slicing, handling, setup, and testing |
| Animations distract or fail to communicate without narration | Medium | Moderate | Prefer one short clip plus static annotated frames; follow Doumont’s signal-to-noise rule |

## (b) What I would tell a colleague the next day

> “They are building a loop that prints PLA–TPU tensegrity-like absorbers, drop-tests them, and lets Bayesian optimization choose the next print.”

That retains the basic workflow but loses the intended **dozens rather than hundreds** claim because the deck never demonstrates it. I would also probably describe the work as “lander research,” which is a distortion caused by the missing proxy-system statement.

## (c) My top three Q&A questions

1. What is the dated plan to complete the campaign, baseline comparison, and repeat testing before the conference slide freeze?
2. Which exact operations are automated today, which remain manual, and what is the measured end-to-end cycle time per adaptive batch?
3. What evidence will justify “dozens rather than hundreds,” and what will you claim if the budget-matched baseline does not show an advantage?

## (d) My most pointed objection

**You are presenting a claimed acceleration without showing a completed campaign, a comparator, or even a visible results slide.**

Unanswered, this is **critical**. I would not fund a scale-up phase from this deck. I might fund completion of the present campaign if the team showed a disciplined schedule, predefined success criteria, and a credible fallback.

## (e) Slide-deck verdict

- **Slide most needing work:** **Slide 11.** It must become a real, scheduled results package, preferably three slides: campaign ledger, budget-matched baseline, and feasible Pareto front.
- **Hidden-slide decision:** **Unhide slide 11**, but not in its current empty form. The talk cannot make its principal claim without it.

### PM slide-level punch list, ordered by schedule criticality

**Must be fixed first**

1. **Slide 11/results sequence:** assign owners and dates for data freeze, quality control, baseline computation, replicate analysis, and final plots. Define fallback wording now.
2. **Slide 2:** add the explicit scope line, “This study uses a printed PLA–TPU T3 prism as a proxy for developing the workflow; it is not flight hardware.”
3. **Slide 7:** replace category counts with the actual optimization problem, test budget, batch size, objectives, constraint, and noise/failure treatment.
4. **Slide 10:** remove “significantly” until slide 11 demonstrates a quantitative improvement; show automation boundaries and the loop’s measured cycle time.
5. **Slides 2 and 9:** download and trim media, test on the conference laptop, and put a static fallback image on each slide.

**Then fix**

6. **Slide 4:** quantify the current cost or candidate count and identify the bottleneck.
7. **Slide 8:** label PLA, TPU, interface, and any post-processing; qualify “no joining.”
8. **Slide 9:** reconcile accelerometers with the instrumented-tup description and show how force, energy absorption, and compaction efficiency are obtained.
9. **Slide 12:** convert the application collage into a conditional next-phase roadmap with gates.
10. **Slide 13:** end on the measured result and deployment rule, not a blank Q&A screen.

**Nice to have**

11. Replace decorative or looping media on slide 4 with one static process image unless it communicates a measured delay.
12. Add backup slides on Bayesian optimization implementation, finite-element-analysis positioning, repeatability, force-cap rationale, and print failures.

---

# P1. The skeptical Bayesian-optimization insider

## (a) My reaction in the room

The opening is competent but generic for a design-automation conference. Slides 1–4 set up an expensive physical experiment, which is a valid application class for Bayesian optimization (BO). I become interested when the presenter reaches slide 7, because that is where methodological seriousness should appear.

Instead, slide 7 says only “6 variables,” “2 types of input data,” and “2 objectives.” I do not learn the variables, their types, how categorical choices are encoded, whether process parameters are optimized, how noisy observations enter the Gaussian processes, how replicates identify noise, how failures are modeled, or how the force cap enters the acquisition. The title says BO handles noisy data, but the visual does not substantiate that message.

There is also an unresolved specification conflict across the supplied materials. The agreed outline says the study jointly optimizes T3 geometry and FDM processing parameters. The abstract’s design vector lists four continuous geometric variables, one integer, and two categorical variables, apparently **seven variables**, while its fabrication section says print parameters are held fixed within a batch. The slide says **six variables**. A DAC audience will notice if the spoken details do not reconcile these versions.

Slides 8–10 explain why physical feedback is useful, but they do not establish why qNEHVI is the right algorithm or whether adaptive selection helped. The visible deck never names qNEHVI, the feasible Pareto front, the peak-force constraint, batch size, initialization, or test budget. Hiding slide 5 is reasonable if it is only a generic “what is BO?” slide copied from another talk. But slide 7 must then carry the application-specific methodological content.

When slide 10 says the workflow “significantly accelerate[s]” optimization, I wait for a performance-versus-budget curve. It never arrives. Slide 12 then generalizes to other applications. My default conclusion is exactly the skeptical one posed in the prompt: this appears to be off-the-shelf qNEHVI attached to an interesting physical apparatus, with no demonstrated algorithmic or empirical advantage yet.

## (b) What I would tell a colleague the next day

> “It was an experimental self-driving-lab-style application of batch multi-objective BO to printed impact absorbers, but the talk did not show whether BO beat space-filling sampling.”

That differs from the intended message because I would not repeat “dozens, not hundreds” without a budget-matched baseline.

## (c) My top three Q&A questions

1. What are the exact decision variables and encodings, and why do the deck, scope statement, and abstract appear to disagree on whether there are six or seven variables and whether FDM parameters are optimized?
2. How is observation noise estimated: fixed noise, learned heteroscedastic noise, technical replicates, or repeated control specimens? What is the replicate allocation?
3. Against what budget-matched baseline do you evaluate qNEHVI, and what metric do you report: feasible hypervolume, best feasible objective values, or attainment probability versus physical tests?

## (d) My most pointed objection

**Nothing visible distinguishes a validated BO contribution from an untested application of standard qNEHVI.**

Unanswered, this is **critical for DAC-10 reception**. Application novelty can be enough, but only if the physical campaign is rigorous and the adaptive method is compared fairly under the same test budget.

## (e) Slide-deck verdict

- **Slide most needing work:** **Slide 7.** Replace the black-box inventory with a visual of posterior mean plus uncertainty → constrained batch acquisition → next physical tests, accompanied by the exact objectives and force constraint.
- **Hidden-slide decision:** **Keep slide 5 hidden** as a standalone generic BO tutorial. Merge one plain-language BO sentence into slide 7 and put qNEHVI details in backup.

---

# P2. The aerospace practitioner

## (a) My reaction in the room

The Super Ball Bot hook works because I know the lineage. Reusable landing structures are interesting. But the title’s claim that tensegrity provides “robust, reusable solutions” is broader than what this deck demonstrates. A lab drop of a polymer proxy is not evidence of robustness in thermal extremes, vacuum, dust, radiation, repeated impacts, or off-axis terrain contact.

The deck never immediately tells me that the actual specimen is **tensegrity-inspired**, lacks ideal compression-only and tension-only membership, and is not intended to fly. That makes slide 2 vulnerable to looking like borrowed aerospace relevance.

Slide 4 is plausible but too broad. Tensegrity design can be difficult, but aerospace development is not made slow only by design-space search. Verification, environmental qualification, uncertainty, packaging, guidance, and system integration matter. A faster specimen loop is useful, but it is one subsystem tool.

I am not helped much by slide 7. I need BO translated into engineering behavior: it chooses the next small batch based on predicted performance and uncertainty while rejecting designs expected to violate a payload-force limit. The slide should name that limit and show the actual trade-off.

Slides 8 and 9 are the first ones that answer “what did you build and how did you hit it?” A labeled specimen, deformation sequence, drop mass, speed or energy, orientation, and force measurement would hold my attention. Two simultaneous looping videos may not. I also want to know whether the structure rebounds, survives repeated drops, and retains its response, because the opening emphasizes reuse.

Slide 10 is understandable. Slide 12 loses me because it jumps from a T3 polymer coupon to lattices and crutch tips without stating transfer conditions or technology gates.

## (b) What I would tell a colleague the next day

> “They use an optimizer to choose which 3D-printed soft–rigid impact absorber to drop-test next, with the eventual motivation of reusable landing structures.”

That is fairly close, but I would deliberately downgrade “tensegrity” to “tensegrity-inspired absorber” and treat planetary landing as motivation only.

## (c) My top three Q&A questions

1. What makes the printed T3 specimen mechanically tensegrity-inspired rather than an ordinary compliant crush structure, and is it actually prestressed?
2. What impact energy, mass, orientation, and transmitted-force cap are used, and how do they relate to a payload-protection requirement?
3. How does performance change over repeated impacts, and what failure modes or permanent set limit the claimed reusability?

## (d) My most pointed objection

**The opening borrows flight relevance and reusability, but the visible deck never establishes the proxy boundary or shows repeated-impact evidence.**

Unanswered, this is **highly damaging** to credibility with aerospace practitioners, though it does not invalidate the optimization workflow itself.

## (e) Slide-deck verdict

- **Slide most needing work:** **Slide 2.** Keep the hook, but place a photograph of the actual T3 specimen beside the Super Ball Bot and state “motivation, not demonstrated flight readiness.”
- **Hidden-slide decision:** **Keep slide 3 hidden.** A generic elbow-friction GIF would distract and oversimplify. Merge a precise tensegrity-mechanism annotation into slide 8 instead.

---

# P3. The additive-manufacturing/materials researcher

## (a) My reaction in the room

Slides 1–4 give me a recognizable motivation for rapid experimental iteration. My interest rises on slide 8 because multi-material fused deposition modeling is where the claimed loop can succeed or fail.

The message “single-build co-fabrication, with no joining of parts” is attractive, but it needs exact boundaries. Is there support removal, trimming, conditioning, manual tensioning, or fixture insertion? Does “single build” mean one tool-change sequence on one machine, or truly co-deposited interfaces throughout the architecture? Are PLA and thermoplastic polyurethane (TPU) mechanically interlocked, chemically bonded, or merely in contact?

The abstract provides more useful information than the slide: a core-wrapping architecture is intended to resist delamination, specimens are weighed and dimensionally inspected, and a control is retested to monitor drift. Those are exactly the details the talk should surface. Slide 8’s planned printing video will not replace a labeled cross-section or interface image.

Slide 9 raises repeatability questions. TPU is rate-, temperature-, moisture-, and history-dependent. “Limited, noisy data” on slide 7 acknowledges noise but does not show the control plan. I need batch identity, drying/conditioning, build position, print orientation, machine state, interface failures, and replicates.

The deck also appears inconsistent about process parameters. The agreed scope says FDM processing parameters are optimized with structure, but the abstract says temperature, line width, infill, and retraction are held fixed within a batch. This could mean they vary between batches or are controlled rather than optimized, but the deck must say which.

I like the physical loop on slide 10. I do not yet accept that multi-material printing “supplies data fast” until cycle time and failure rate are shown.

## (b) What I would tell a colleague the next day

> “They co-print PLA and TPU impact specimens and use each mechanical test to guide the next design batch.”

I would probably omit “no joining” and “dozens rather than hundreds” until I saw interface qualification, failure accounting, and campaign data.

## (c) My top three Q&A questions

1. How is the PLA–TPU interface designed and qualified, and what fraction of specimens fail by delamination or print defects?
2. Which material, machine, conditioning, and build-position variables are controlled, measured as covariates, or optimized?
3. How many true replicates and repeated control specimens are used to separate BO improvement from printer drift and TPU batch variation?

## (d) My most pointed objection

**The deck treats co-fabrication as an enabling fact without showing interface integrity, repeatability, or the remaining manual processing steps.**

Unanswered, this is **highly damaging** because print variation is part of both the physical mechanism and the statistical noise model.

## (e) Slide-deck verdict

- **Slide most needing work:** **Slide 8.** Replace or supplement the printing clip with an annotated specimen and interface detail: PLA struts, continuous TPU network, deposition/wrapping strategy, prestress status, post-processing, and observed failure modes.
- **Hidden-slide decision:** **Keep slide 3 hidden.** Its proposed generic GIFs do not answer the materials questions. Put the relevant deformation mechanism on slide 8.

---

# P4. The first-year graduate student

## (a) My reaction in the room

Slide 1 sounds positive, and slide 2 gives me a memorable reason to care. I understand that the lander survives an impact because the structure itself deforms. But I do not yet know what “tensegrity” means, and the hidden slide 3 would not necessarily fix that: an elbow GIF and a squishing GIF could leave me with an inaccurate friction-versus-elasticity story.

Slide 4 is easy to follow. The three words “Iteration, Building, Testing” form a simple problem statement, although the images need to make their relationship obvious.

I get lost on slide 7. Six variables of what? What are the two input-data types? Are the two objectives “absorb energy” and “reduce force,” or something else? I do not know what a black box means in this setting. The title says Bayesian optimization works with noisy data, but I have not been shown how it decides anything.

Slide 8 helps because I can see printing. Still, I need labels that distinguish the rigid and flexible parts and one sentence explaining why the object is “tensegrity-inspired.” Slide 9 is intuitive if the clips are synchronized and annotated. I would understand even better if the slide drew the metric extraction directly on a force–time or force–displacement trace.

Slide 10 is the clearest slide in the deck. Printing → testing → optimizer → next print is the idea I will remember. But it arrives after the technical terms rather than before them. I would benefit from seeing a version of this loop before slide 7 and then revisiting it after the methods.

Slide 12 feels like a new presentation. I have not seen whether the current system worked, so the crutch tip and lattice do not feel earned. Then the talk ends on a blank question slide rather than telling me the answer.

## (b) What I would tell a colleague the next day

> “They repeatedly print and drop-test flexible 3D structures, and a machine-learning model decides what to print next.”

My retelling loses the two objectives, the force constraint, and the “dozens rather than hundreds” quantitative point. I might incorrectly call the method generic machine learning rather than Bayesian optimization.

## (c) My top three Q&A questions

1. What exactly is tensegrity, and which parts of your printed specimen are in tension and compression?
2. What are the six things the optimizer can change, and what are the two scores it is trying to improve?
3. How does the optimizer know whether to try something uncertain rather than the design it currently thinks is best?

## (d) My most pointed objection

**The deck names the ingredients before giving me a plain-language map of how they work together.**

Unanswered, this is **moderately damaging**. I retain the loop but lose the actual research question and technical contribution.

## (e) Slide-deck verdict

- **Slide most needing work:** **Slide 7.** It needs one concrete candidate, predicted performance plus uncertainty, and the next selected batch, not abstract counts around a black box.
- **Hidden-slide decision:** **Unhide neither slide 3 nor slide 5 as written.** If forced to choose one, **keep slide 5 hidden** and integrate its one-sentence concept into a redesigned slide 7. Generic explanation would add time without restoring the missing optimization details.

---

# P5. The finite-element-analysis veteran

## (a) My reaction in the room

The opening is fine until slide 4 implies that physical iteration is the central route around slow design. I start waiting for the argument about simulation. Because slide 6 is hidden, the deck never states the agreed, defensible position: a sufficiently calibrated model may cost more than it saves for this campaign, particularly when interfaces, defects, rate dependence, contact, and millisecond shock transients dominate.

That omission avoids an overt attack on finite-element analysis (FEA), which is good, but it also creates a logical hole. Why is physical BO the chosen source of objective values? Why not a hybrid strategy, reduced-order model, analytical screening, or multi-fidelity optimization? The deck merely proceeds from “design is slow” to “BO makes experimentation affordable.”

I object to any suggestion that experimental data are automatically “real” and simulations are not. Measurements also involve sensor bandwidth, filtering, fixture dynamics, uncertainty, and model-based transformations. Slide 9’s “accelerometers gather real data” wording is particularly vulnerable. A force estimate derived from acceleration still rests on calibration and assumptions.

Slide 10 is a useful experimental workflow. It should be presented as a scoped engineering choice, not a universal replacement for simulation. Slide 12’s transfer claim needs the condition from the outline: use this pattern where tests are authoritative, costly, the design space is mixed, and goals conflict.

## (b) What I would tell a colleague the next day

> “They bypass a calibrated finite-element model and optimize directly against impact tests because the printed interfaces and transient response are difficult to model economically.”

That is close to the intended experiment-first rationale, but I had to infer it; the visible slides do not say it clearly.

## (c) My top three Q&A questions

1. What evidence shows that calibrating a useful simulation would cost more than it saves for this campaign, rather than merely being inconvenient?
2. How do you verify the measured peak transmitted force, including sensor bandwidth, fixture dynamics, filtering, and uncertainty?
3. Why exclude analytical or low-fidelity screening from a multi-fidelity BO strategy, especially for infeasible geometries and gross structural trends?

## (d) My most pointed objection

**The deck uses experiment-first optimization without stating a scoped cost-and-validity argument or acknowledging where simulation could still add value.**

Unanswered, this is **highly damaging in Q&A**. It makes the methodology look ideologically anti-simulation rather than economically reasoned.

## (e) Slide-deck verdict

- **Slide most needing work:** **Slide 4.** It should become the two-sided decision: exhaustive physical search is too costly, while campaign-grade calibration for the hardest responses is also costly; therefore choose physical tests adaptively.
- **Hidden-slide decision:** **Merge slide 6 into slide 4**, rather than unhide it as written. Keep a fuller evidence-backed simulation/experiment comparison as backup.

---

# P6. The friendly industry generalist

## (a) My reaction in the room

The opening video is memorable, and I like the practical goal of shortening build–test iteration. Slide 4 is easy to understand. My attention slips on slide 7 because the counts and black-box symbol do not tell a story. I do not need the name qNEHVI, but I need to know that the software balances trying promising designs with learning from uncertain ones and respects a force limit.

Slides 8–10 are the strongest run. If the presenter shows one labeled specimen, one clean drop clip, and one loop diagram, I can see how I might use the pattern in another product-development problem. I want a cycle-time number and an indication of what software or human work is required.

Slide 12 dilutes the message by offering several destinations before proving the present result. The ending is weak. A blank Q&A slide discards the chance to leave the audience with the workflow, the best specimen, and a measured improvement.

## (b) What I would tell a colleague the next day

> “Print it, break or drop it, feed the measurements back, and let the optimizer pick the next batch instead of running a huge test matrix.”

That captures the intended practical pattern, but I would probably overgeneralize it beyond the specific conditions under which it is useful.

## (c) My top three Q&A questions

1. How many prints and calendar days did it take to reach a useful design compared with your previous workflow?
2. What parts of this system could another engineering team reuse without building the same drop tower or writing a custom optimizer?
3. What happens when a print fails or a test produces an outlier?

## (d) My most pointed objection

**I understand the loop, but the deck never gives me the one number or result that proves it was worth building.**

Unanswered, this is **moderately to highly damaging**. I would remember the concept but not have a reason to adopt or sponsor it.

## (e) Slide-deck verdict

- **Slide most needing work:** **Slide 13.** Replace the blank Q&A screen with the best measured result, the closed-loop diagram, and one deployment rule; retain a small “Questions?” label.
- **Hidden-slide decision:** **Unhide slide 11** once populated. Results are more valuable than another explanatory slide.

---

# Synthesis

## Cross-persona themes

1. **The scope boundary is missing.** The Super Ball Bot is a good hook, but every persona risks interpreting a PLA–TPU proxy as a claim about flight hardware.
2. **Slide 7 is the weakest visible technical slide.** It serves neither experts nor novices. Counts such as “6 variables” and “2 objectives” are information, not a message.
3. **The main claim currently lacks evidence.** “Significantly accelerate,” “supplies data fast,” and “dozens, not hundreds” require a campaign ledger and a budget-matched comparison.
4. **The results omission breaks the story.** The deck follows the outline through the workflow, then skips the outline’s largest time block and moves directly to future work.
5. **The physical system needs more definition.** The audience needs a labeled specimen, a clear explanation of “tensegrity-inspired,” interface design, remaining manual steps, and the measurement chain.
6. **Noise must be operational rather than rhetorical.** Saying the data are noisy is insufficient. Replicates, periodic controls, drift, failures, and uncertainty should be shown.
7. **Experiment-first needs a scoped rationale.** The deck should not dismiss FEA, but it should explain why adaptive physical testing is the economical source of objective values for this campaign.
8. **The close is not a conclusion.** Future applications and a blank Q&A slide do not substitute for the measured finding and its conditions of transfer.
9. **Media are a communication and schedule risk.** Short clips can work, but multiple looping videos violate the signal-to-noise principle and create failure modes.
10. **The project specification needs reconciliation.** The supplied materials differ on six versus seven variables, whether FDM process parameters are optimized, and whether peak force is a constraint or part of the Pareto trade-off.

## Five highest-priority slide-level revisions

### 1. Slide 11: replace one empty slot with a three-slide quantitative results sequence

Use full-sentence titles tied to observed data:

- **11A:** “The campaign used **N** specimens in **B** adaptive batches, including **R** replicates and **F** failed prints.”
- **11B:** “At the same physical-test budget, adaptive selection reached **[measured feasible-performance result]** faster than **[predeclared Sobol/random baseline]**.”
- **11C:** “The measured feasible Pareto front trades specific energy absorption against compaction efficiency while respecting a **[value and unit]** peak-force cap.”

Show uncertainty, replicate spread, infeasible points, and representative specimen photographs or traces. If the campaign cannot support the baseline claim, change the talk’s main message to: **“We evaluate whether noise-aware multi-objective Bayesian optimization can reduce the physical-test budget.”**

### 2. Slide 7: state the actual constrained optimization problem

Replace the current black-box/count design with:

- the named decision variables and their types;
- a small batch entering the printer/test loop;
- objectives: maximize specific energy absorption and compaction efficiency;
- constraint: peak transmitted force below a stated cap;
- qNEHVI’s role in one plain sentence: it chooses a small next batch likely to expand the feasible trade-off frontier while accounting for uncertainty and noisy tests;
- the declared test budget, initialization size, and batch size.

Resolve six versus seven variables and whether processing parameters are decision variables before finalizing this slide.

### 3. Slide 2: put the proxy boundary beside the hook

Keep the Super Ball Bot clip, but add an image of the actual specimen and the visible sentence:

> **“Here, a printed PLA–TPU T3 prism is a proxy for developing the workflow, not flight hardware.”**

Change or qualify “robust, reusable solutions” unless the present campaign includes repeat-impact evidence.

### 4. Slide 4: turn the vague need into the two-sided engineering decision

Retitle it:

> **“Because exhaustive testing and campaign-grade model calibration are both costly, each physical specimen must be chosen for its information value.”**

Add one quantified physical-search estimate and one scoped calibration challenge. Do not say simulation is untrustworthy. State that FEA and lower-fidelity models remain possible screening or future multi-fidelity tools.

### 5. Slides 10 and 13: separate the demonstrated loop from the conclusion

- **Slide 10:** retitle to **“The closed loop turns each measured test into the next small batch of specimens.”** Remove “significantly accelerate” until the results demonstrate it. Mark automated and manual stages.
- **Slide 13:** retain the closed-loop thumbnail, add the best quantitative result, and state the deployment rule: **use the loop when tests are authoritative, each test is costly, the design space is mixed, and performance goals conflict.** Add “Questions?” without clearing the conclusion from the screen.

## Hidden-slide adjudication

| Hidden slide | Recommendation | Rationale |
|---|---|---|
| **3: tensegrity usefulness/mechanism** | **Merge into slide 8** | The generic elbow and squishing GIFs add noise and risk an inaccurate mechanism; an annotated actual specimen and deformation sequence are stronger. |
| **5: generic BO explanation** | **Merge into slide 7; keep original as backup or delete** | DAC experts do not need a generic advocacy slide, but novices need one plain-language sentence and a concrete acquisition visual. |
| **6: specimen information value/experiment-first** | **Merge into slide 4; keep evidence-rich version as backup** | The argument is structurally necessary, but the current title is vague and the visual does not support the scoped calibration-versus-campaign-cost decision. |
| **11: results** | **Unhide and expand to three slides** | Results are the evidentiary center of the talk and were allocated five minutes in the agreed outline. An empty or hidden results slot makes the main claim untenable. |

## Visible-slide claims needing evidence, hedging, or backup

| Slide | Claim | Required treatment |
|---|---|---|
| **1** | “Build better tensegrity structures faster” | Define “better” with the two objectives and force constraint; support “faster” with the results comparison. |
| **2** | Tensegrity is robust and reusable for planetary landings | Cite the Super Ball Bot source; distinguish concept evidence from this study; provide repeat-impact evidence or hedge reusability. |
| **2** | Parachutes and retrorockets struggle in the stated conditions | Cite an authoritative aerospace source if retained in narration; avoid implying universal inadequacy. |
| **4** | Current tensegrity design is slow and resource intensive | Quantify candidate count, print/test time, hand-assembly burden, or calibration effort. |
| **7** | BO makes experiments affordable with limited, noisy data | Show campaign budget, noise characterization, replicates, baseline, and performance versus tests. Prepare qNEHVI and Gaussian-process details in backup. |
| **7** | Six variables, two input-data types, two objectives | Reconcile with the apparent seven-variable abstract specification and identify every quantity. Clarify “input-data types.” |
| **8** | Multi-material AM supplies data fast | Report print-to-result cycle time and failure rate. |
| **8** | Single-build co-fabrication with no joining | Show interface and post-processing; use “no joining of PLA and TPU members” if other manual operations remain. |
| **9** | Accelerometers gather the relevant impact data | Show sensor locations and the derivation of transmitted force, specific energy absorption, and compaction efficiency. Reconcile this wording with the abstract’s instrumented-tup description. |
| **10** | The loop significantly accelerates optimization | Remove “significantly” unless a defined baseline and uncertainty support it. Statistical significance should not be implied casually. |
| **12** | Workflow will transfer to lattices and other applications | Present as conditional future work with transfer criteria, not an achieved result. Attribute any external crutch-tip image and claim. |

### Prepared backup slides

1. Full design-variable table, bounds, encoding, and fixed versus optimized process parameters.
2. qNEHVI implementation, Gaussian-process assumptions, constraint treatment, batch size, and acquisition settings.
3. Noise plan: replicates, periodic control, heteroscedasticity, drift, outlier policy, and uncertainty propagation.
4. Budget-matched baseline definition and evaluation metric.
5. Force-cap rationale and full objective definitions.
6. Sensor chain, calibration, sample rate, filtering, fixture dynamics, and metric extraction.
7. PLA–TPU interface, conditioning, build layout, dimensional/mass deviations, and print-failure modes.
8. Scoped FEA rationale with citations or internal validation; possible analytical or multi-fidelity extensions.
9. Automation map and cycle-time breakdown.
10. Repeated-impact behavior if reusability remains in the opening.

## Merged, ordered presenter TODO list

### Must fix before the talk

1. **Freeze the scientific specification.** Reconcile the number and type of decision variables, whether FDM parameters are optimized or controlled, the two objectives, the force constraint, treatment of print failures, and the measurement chain. Use one formulation across slides, abstract, paper, and Q&A.
2. **Set a results completion plan.** Establish dates and owners for campaign completion, repeat tests, data quality review, baseline analysis, and slide freeze. Predeclare the fallback claim if the baseline does not support “dozens rather than hundreds.”
3. **Build the three-slide results sequence.** Campaign ledger → budget-matched baseline → measured feasible Pareto front. Allocate approximately five minutes, as the agreed outline requires.
4. **Add the proxy statement to slide 2.** State plainly that the PLA–TPU T3 specimen is a workflow proxy and not flight hardware.
5. **Redesign slide 7.** Show the exact constrained multi-objective problem, test budget, small batches, uncertainty, noisy observations, and the role of qNEHVI.
6. **Remove unsupported result language.** Until supported, delete “significantly” from slide 10 and avoid “dozens rather than hundreds” in the title, narration, or close.
7. **Clarify experiment-first positioning.** Merge the information-value argument into slide 4 and prepare an evidence-backed FEA backup slide.
8. **Make the experiment auditable.** On slide 9 or backup, reconcile accelerometers and the instrumented tup; show how all three performance metrics are calculated and how uncertainty is handled.
9. **De-risk every video.** Store local trimmed files, disable distracting loops, test them on presentation hardware, and include static fallback frames.
10. **Rehearse to 13:30–14:00.** Protect the results and conclusion from being cut. Practice once without slides, consistent with Doumont’s preparation advice.

### Should fix

11. **Replace slide 8’s generic print emphasis with mechanism and materials evidence.** Label PLA, TPU, interface strategy, prestress status, deformation, post-processing, and failure modes.
12. **Quantify slide 4.** Give at least one campaign-relevant cost, duration, or candidate-count estimate.
13. **Show automation boundaries on slide 10.** Candidate selection and surrogate updating may be automated; slicing, handling, test setup, and testing remain manual according to the abstract.
14. **Convert slide 12 to a gated roadmap.** Separate demonstrated T3-proxy results from future lattices, flight materials, and terrestrial applications.
15. **Turn slide 13 into the conclusion.** Leave the audience with the best result and transfer rule while taking questions.
16. **Prepare technical backup slides.** Prioritize baseline fairness, noise, force-cap rationale, print failures, materials repeatability, and FEA positioning.

### Polish

17. Replace the slide 1 title with a specific message, such as **“Physical Bayesian optimization searches multi-material tensegrity absorbers one small test batch at a time.”**
18. Left-align titles and use intentional line breaks; check every slide at six-per-page scale.
19. Use one purposeful visual per slide. Avoid decorative loading or elbow animations.
20. Standardize terminology: “Bayesian optimization,” not “Bays Opt”; “tensegrity-inspired” where appropriate; define specific energy absorption once.
21. Add citations directly beside borrowed footage, images, and quantitative claims.

## Who the deck serves best and worst

- **Best served:** **P6, the friendly industry generalist.** The visible sequence is visually intuitive, practical, and easy to reduce to “print → test → learn → repeat.”
- **Worst served:** **P1, the skeptical BO insider.** The current deck omits nearly every item needed to judge a DAC-10 contribution: exact problem formulation, budget, baseline, noise model, constraint handling, and empirical adaptive advantage.

That is **not the right trade-off for DAC-10**. The deck should remain accessible to P4 and P6, but its technical center must satisfy P1 without turning into a BO lecture. One rigorous optimization slide, three quantitative results slides, and targeted backup material would achieve that balance.

## Predicted reception

- **As is: 4/10.** The physical workflow and application are memorable, but the absent scope statement, empty results section, vague BO slide, and unsupported acceleration claim leave the DAC contribution unproven.
- **After the must-fixes: 8/10.** A scoped proxy claim, reconciled methods, fair budget-matched comparison, feasible Pareto front, and measured conclusion would turn the same visual story into a credible design-optimization application talk.

## Discretionary analytical decisions

- Evaluated only the visible slide order for the simulated in-room reactions, while using hidden slides and presenter notes to judge revision options.
- Treated planned placeholder visuals as if implemented according to the presenter’s notes, but judged the selected visual concept and associated stage risk rather than absent graphic quality.
- Prioritized the Draft 3 outline over conflicting Draft 1 wording because the prompt identifies it as the agreed story arc, scope framing, results plan, and timing plan.
- Rated objections qualitatively as moderate, high, or critical rather than assigning unsupported numerical probabilities.
- Recommended three results slides rather than preserving one reserved slot because the agreed outline specifies three distinct evidentiary products and allocates five minutes to results.
- Recommended merging hidden slides 3, 5, and 6 rather than simply unhiding them because their necessary ideas can be conveyed with higher signal-to-noise on existing slides.
- Treated the six-versus-seven-variable and optimized-versus-fixed-process-parameter differences as unresolved specification conflicts requiring reconciliation, rather than inferring which document is correct.
- Assessed claims against the supplied deck extraction, Draft 3 outline, Doumont notes, and submitted abstract only; no independent validation of cited literature or unseen experimental data was attempted.