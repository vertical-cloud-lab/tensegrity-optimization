# Edison trajectory -- mock-jmd-review-2

Task ID: `3fde560e-1bb9-4c6b-8fcc-eaeef4570bf4`  
Status: success

## Query

SECOND-ROUND mock peer review for an ASME Journal of Mechanical Design (JMD)
Research Paper submission. You reviewed an earlier draft of this same manuscript
in a prior round; this is the revised draft. The attached files are the current
populated draft (manuscript.pdf is the clean reader PDF; manuscript-todos.pdf is
the review PDF that additionally shows margin \todo{} annotations and a
\listoftodos; sources are manuscript-body.tex / manuscript.tex /
manuscript-todos.tex and references.bib; manuscript/README.md documents venue
choice and build).

The paper is a multi-material 3D-printed tensegrity-inspired energy-absorbing
crutch-tip study using experiment-driven Bayesian optimization (BO). Rigid PLA
struts in compression + soft TPU cables in tension, printed on a Bambu Lab H2D
dual-nozzle printer, characterized under quasi-static compression and
drop-weight impact. Quantitative Results/Discussion are INTENTIONALLY still
\todo{} placeholders -- the project is at the planned-methods phase. Please
review structure, framing, scope, novelty claims, methods rigor, literature
coverage, internal consistency, and venue fit (ASME JMD vs. backup Smart
Materials and Structures / Additive Manufacturing), NOT raw numerical values.

What CHANGED since the first round (so you can focus on the current state rather
than re-flagging already-addressed items):
  * The (author?) citation rendering artifacts were fixed; the blank third
    Contributions bullet is filled.
  * PLA+TPU is the INTENTIONAL, correct material pair for this study (the earlier
    PETG mention was an inconsistency; a separate PLA->PETG question is tracked
    elsewhere and is out of scope here). Treat PLA/TPU as the design choice.
  * The TPU joint mechanism is now described correctly: TPU tension elements are
    anchored INSIDE the ends of each PLA strut (the strut acting as a rigid cage
    with discrete cable outlets), NOT wrapped around the strut exterior.
  * Methods were refreshed with concrete planned-methods detail: D3-symmetric
    parameterization (12 diameter axes collapse to 4 orbit axes), categorical
    cable diameter set, Ax/BoTorch SAASBO + qNEHVI with TuRBO escalation, ISO/
    ASTM test standards, the bungee-assisted drop tower with hold-down
    mitigations, and an n=9 Sobol initialization batch.
  * Figures: Fig 2 (CAD + as-printed T3 prism), Fig 3 (fabrication/test
    workflow with real photos), and illustrative example data figures (a
    mechanistic drop-curve figure and four Ax surrogate-diagnostic figures: LOO
    cross-validation, parameter sensitivity, convergence, Pareto front) are now
    populated. The example data figures are honestly captioned "Illustrative
    example (synthetic data)" and watermarked because real experimental data is
    not yet collected.
  * Pretensioning is now described ONLY as a future scale-up validation step on
    the final Pareto-optimal designs (Contributions item 3); the
    primary BO loop and Fig 2 prototype do NOT use pretensioned cables.

Produce FOUR artifacts, in the same style as a JMD decision-letter package:

1. Mock Reviewer #1 -- Design / Mechanical Engineering (typical ASME JMD
   reviewer). Strict on novelty vs. prior tensegrity/lattice/spring-loaded-tip
   work, on the BO formulation (kernel, acquisition, categorical handling,
   single- vs. multi-fidelity framing, budget/scaling), on parameterization
   completeness, and on JMD scope fit. Major / Minor / Editorial; recommend
   Accept / Minor / Major / Reject / Reject-and-Resubmit.

2. Mock Reviewer #2 -- Biomechanics / Rehabilitation engineering. Strict on the
   crutch-tip clinical motivation, biomechanical relevance of the axial
   drop-tower fixture vs. real off-axis/cyclic crutch loading, transferability,
   IRB considerations, and clinical-metric mapping (SEA -> peak transmitted
   force at the wrist/shoulder). Recommendation.

3. Mock Reviewer #3 -- Additive manufacturing / materials. Strict on the
   PLA+TPU multi-material FFF processing claims, the internal-anchor joint vs.
   alternatives, interface durability/fatigue, FFF repeatability and resolution
   limits for the categorical cable-diameter set, process-parameter disclosure,
   and FFF vs. SLA/DLP/SLS/MJF justification. Recommendation.

4. Mock Editor (JMD Associate Editor) decision letter synthesizing the three
   reviews: single-paragraph summary, decision, and an itemized,
   priority-ordered list of revisions required before resubmission. Explicitly
   assess venue fit (JMD Research Paper vs. Design Innovation vs. Tech Brief vs.
   redirect to SMS / J. Mech. Behav. Biomed. Mater. / Additive Manufacturing)
   and explicitly state whether the revisions since round 1 have moved the
   manuscript closer to acceptance.

End with a short "Reviewers' bibliographic gaps" section listing specific
peer-reviewed references the authors are likely still missing, by topic, given
references.bib.

Be honest, specific, and grounded in the attached files. It is acceptable (and
expected) to note that the placeholder \todo{}s and the absence of experimental
results gate the final decision. Where round-1 concerns have been resolved, say
so; where they persist or new ones appear, flag them.


---

## Answer

Mock Reviewer #1 — Design / Mechanical Engineering (ASME JMD)

Recommendation: Major Revision

Major comments

1. The manuscript is materially better structured than the prior-round draft, but it is still not a reviewable JMD research paper in its present state because the Results and Discussion sections remain placeholders. The current submission reads as a planned-methods paper with illustrative synthetic figures rather than a completed research article. That is the main gate on any final recommendation.

2. The round-1 fixes you note are real improvements. The PLA/TPU material pair is now internally consistent. The internal-anchor joint is now described clearly and no longer conflicts with the earlier “wrapped exterior cable” description. The BO section is much more concrete, especially the Ax/BoTorch framing, qNEHVI, SAASBO, TuRBO escalation, and the n=9 Sobol batch. Those changes move the paper closer to something JMD could evaluate on design-method grounds.

3. The biggest remaining framing problem is scope drift between “general architected energy absorber” and “crutch-tip application.” The title, abstract, Introduction, Contributions, and most of Methods position the work as a general tensegrity-inspired energy absorber. The crutch-tip use case appears mainly in the Discussion as a future translation path. If the actual paper is a crutch-tip study, that application must be present up front in the problem statement, design requirements, constraints, objective selection, and validation logic. If the actual paper is a general design-method paper, then the crutch-tip language should be reduced and treated explicitly as a downstream application. Right now it is in between.

4. Novelty relative to Pajunen et al. (2019) and Mo et al. (2023) is still asserted more than demonstrated. You already left yourself a TODO on this. That gap needs to be closed with a clean, explicit comparison table or paragraph. As written, the claimed novelty seems to be the combination of: multi-material PLA/TPU FFF, an internal TPU-anchor joint, physical experiment-in-the-loop BO, and multi-objective optimization. That package may be novel, but the manuscript does not yet prove it.

5. The design parameterization is still under-specified and partly inconsistent. One paragraph states that under D3 symmetry the 12 member-diameter axes collapse to four orbit axes: one strut orbit plus three cable orbits. But Table 1 then lists only a single cable diameter d_t and a single strut diameter d_s, alongside R, H, and theta. That is not four diameter orbits. Either the initial campaign ties the three cable orbits together into one variable, or the table is incomplete. This matters because the dimensionality of the BO problem, the appropriateness of SAASBO, and the claimed expressiveness of the parameterization all depend on the exact design vector.

6. There is another parameterization inconsistency around tendon diameter. The text gives an FFF-resolvable categorical set {1.2, 1.8, 2.4, 3.0, 4.5} mm for the working prototype, while Table 1 gives a continuous range of 3.0–5.5 mm. A TODO notes this conflict, but until it is resolved the BO search space is not well defined. The same issue applies to topology handling: the paper cites Garrido-Merchan and Hernandez-Lobato for categorical GP handling and BOCS as a baseline, but the actual encoding used in Ax is not stated.

7. The BO formulation is more mature than before, but still needs enough detail for a JMD methods review: kernel family, ARD vs non-ARD, output transforms, normalization, treatment of observation noise, batching q, total experimental budget T, stopping criterion, random seed policy, and how categorical and hierarchical variables are represented in Ax. “SAASBO + qNEHVI with TuRBO escalation” is promising, but it is not yet a reproducible method section.

8. I am not yet convinced that SAASBO is the right default for the first campaign as described. If the actual working design vector is roughly 5–6 variables with n=9 Sobol initialization, then SAASBO may be heavier than needed, while ordinary single-task or model-list GP variants could be easier to justify and diagnose. If the intended near-term space really is up to 25 dimensions, explain exactly when that expansion occurs and why the initial low-dimensional campaign is still informative.

9. The paper should decide whether it is single-fidelity, multi-fidelity, or sequentially staged. Right now Contribution 2 presents a direct physical-experiment BO loop, while Contribution 3 adds later validation on pretensioned assemblies and an inline TODO discusses possible inclusion of physics-based simulations. That is fine as a future path, but for the current paper you need a hard boundary: this manuscript is either a single-stage experiment-driven BO study, or it is a multi-source optimization paper. At present it says the former, with speculative text from the latter still left in place.

10. JMD fit is plausible but not automatic. The manuscript fits JMD best if the contribution is framed as a design methodology paper: parameterized architected-material design, constrained search-space definition, and experiment-driven BO for expensive physical prototypes. It fits less well if it is mostly an additive-manufacturing process paper or mostly an application paper about assistive-device impact attenuation. Without real results, I would not recommend acceptance into JMD on methods merit alone.

Minor comments

1. The abstract is below the 150–200 word target noted in your own README. I counted about 147 words once the TODO is removed.

2. The abstract does not mention the crutch-tip motivation at all, which reinforces the scope ambiguity.

3. Table 2, the print-parameter table, still has multiple TBD cells. For JMD, those can remain unknown at draft stage, but not in a resubmission.

4. The Results placeholder figures are honestly labeled as synthetic. Good. Keep that honesty. But for peer review they cannot substitute for the actual convergence, sensitivity, and Pareto evidence.

5. The sentence claiming the internal anchor is used “to ensure cyclic interface durability” is too strong without data. Later TODO text correctly asks for pull-out validation. The current claim should be softened until verified.

6. The test standards list in quasi-static compression is long, but the adaptation logic is still loose. Clarify which portions of each standard are actually followed and which are only inspirational.

7. The manuscript would benefit from a table of design variables, objectives, constraints, and nuisance variables all in one place.

Editorial comments

1. Resolve all in-text TODOs before resubmission; there are many, and several are central rather than cosmetic.

2. Tighten the Contributions list so each item is a completed contribution, not a planned one.

3. If the paper stays with JMD, consider a front-end figure or table explicitly mapping prior work by fabrication route, optimization strategy, and validation modality.

4. Standardize FDM vs FFF usage. The manuscript uses both.

5. Define whether “tension element,” “tendon,” and “cable” are interchangeable in this paper.

Mock Reviewer #2 — Biomechanics / Rehabilitation Engineering

Recommendation: Major Revision

Major comments

1. The present manuscript does not yet support its implied rehabilitation-engineering relevance strongly enough. If this is truly a crutch-tip paper, the clinical motivation must move from Discussion into the Introduction, objectives, and test design. At present, the manuscript is an architected-material paper with a late-stage assistive-device application story.

2. The axial quasi-static compression test and axial drop-tower setup are not obviously representative of real crutch-tip loading. Crutch use involves off-axis loading, fore-aft shear, frictional interaction with the ground, repeated cycles, and user-dependent gait patterns. The manuscript briefly acknowledges that slip resistance is out of scope and cites ISO 11334-4, but that is not enough if the application claim remains central.

3. Relatedly, the manuscript needs a clinical mapping from material-level metrics to user-relevant outcomes. SEA and compaction efficiency are useful engineering descriptors, but the user-facing question is whether the design reduces peak transmitted force, loading rate, or cumulative impulse at the wrist, elbow, shoulder, or residual limb. The Discussion gestures at upper-extremity overuse injury and crutch biomechanics, but the methods do not yet define a pathway from bench metrics to those outcomes.

4. The drop-tower fixture seems especially weak as a surrogate for real use unless justified better. The bungee-assisted rig, top tethers, and hold-down mitigations may be reasonable for controlled comparative screening, but they also create a loading condition that is different from realistic crutch-tip strike. You need a clear statement that this is an accelerated bench-screening modality, not a direct biomechanical surrogate. Then specify what later validation is required before any assistive-device claims can be made.

5. Cyclic durability matters more than single-impact behavior for a crutch-tip application. The manuscript mentions cyclic interface durability and repeated-impact use cases, but there is no cyclic compression, wear, or fatigue protocol yet. From a rehabilitation standpoint, that omission is more serious than the absence of one more drop condition.

6. Human-subjects and IRB issues are correctly absent from the current methods because no human testing is described. Keep it that way unless you actually add user studies. But if you want to motivate future translation, state clearly that this paper is a benchtop preclinical design-screening study and does not involve human subjects or require IRB approval in its current form.

7. There is still a mismatch between device-level geometry and the intended application envelope. The Discussion notes future miniaturization to crutch-tip diameters, but the working prototype is a ~50 mm bounding-box T3 prism. That is a large gap. For a rehab audience, the manuscript should either show a geometry scaling argument or stop short of implying near-term use in conventional crutch tips.

Minor comments

1. The cited rehabilitation literature is directionally relevant but still incomplete for translating ground-reaction-force attenuation to upper-extremity benefit.

2. Please distinguish “impact attenuation” from “comfort” and from “overuse risk.” Those are related but not interchangeable.

3. If traction is out of scope, say explicitly that no claim is being made about slip safety.

4. Consider whether cyclic compression at physiologic loading rates would be more clinically relevant than one part of the current quasi-static test battery.

Editorial comments

1. Add a concise paragraph in the Introduction explaining why crutch-tip impact attenuation is a legitimate design problem and what exact bench metrics serve as proxies.

2. Add a limitations paragraph specific to biomechanical transferability.

3. Avoid implying clinical efficacy from bench tests.

Mock Reviewer #3 — Additive Manufacturing / Materials

Recommendation: Major Revision

Major comments

1. The manuscript is much improved on the materials/process side compared with the earlier version because the PLA/TPU pairing is now consistent and the internal-anchor joint is described clearly. That fixes two major internal-consistency problems from round 1.

2. The largest remaining weakness is that the process description is still incomplete at a level that matters for reproducibility and for interpretation of failure modes. Table 2 contains multiple TBD values for nozzle temperatures, bed temperature, layer height, speed, and infill. Those are not side details for a PLA/TPU multimaterial FFF paper. They affect interfacial bonding, filament buckling risk, dimensional accuracy, tendon continuity, and mechanical scatter.

3. The internal-anchor joint is interesting and may be a meaningful design contribution, but the manuscript overstates what is known about it. At present there are no presented pull-out, fatigue, or cyclic durability data. Without those, statements about ensuring durability or keeping the interface in favorable stress states are mechanistic hypotheses, not validated conclusions.

4. The manufacturing-resolution story around cable diameter needs cleanup. The text first presents a categorical printable set {1.2, 1.8, 2.4, 3.0, 4.5} mm, then Table 1 gives 3.0–5.5 mm as a continuous variable, and a TODO says the lower bound is set by Bambu auto-support detection. That does not yet read like a controlled AM design space; it reads like a search space that is still being negotiated with the slicer. The final paper needs to report what diameters were actually printable with acceptable fidelity and variance, and how that finding shaped the BO space.

5. The choice of FFF over alternatives is not yet defended sharply enough. For the claimed contribution, the best justification is probably rapid, inexpensive, dual-material iteration on a single platform with direct experiment-in-the-loop optimization. If that is the argument, make it explicitly. Otherwise readers will reasonably ask why not use SLA/DLP for finer feature control or SLS/MJF for better repeatability in small lattice members.

6. The manuscript should report how repeatability will be quantified across prints and across plate positions. The current n=9 Sobol batch printed in a single 3x3 layout is efficient, but it introduces potential spatial/process confounding unless plate-position effects are checked.

7. Please be careful about the interface language. Co-printed PLA/TPU systems often fail by local geometric discontinuity, poor fusion, or stress concentration near material transitions, not simply by “delamination.” The present manuscript would benefit from a more neutral description unless interfacial fracture surfaces are actually characterized.

8. The comparison to Ye et al. is handled more honestly now than before. Good. The manuscript correctly says Ye et al. is a co-printing precedent, not validation of this joint. Keep that distinction.

9. If the paper remains in JMD, the additive-manufacturing detail can sit in support of the design-method contribution. If the results eventually center on process windows, joint mechanics, and printability constraints more than on BO-enabled design discovery, Additive Manufacturing may become the stronger venue.

Minor comments

1. Clarify nozzle diameters, filament brands/grades, and whether drying protocols were used for TPU.

2. State whether the PLA struts are solid or what infill/wall strategy is used.

3. Explain how support removal affects the TPU members and whether damage during post-processing was tracked.

4. Report nominal vs measured dimensions for printed tendon diameters.

5. If the Supplementary Information contains the five-joint comparison, the main text should still summarize the selection criteria briefly.

Editorial comments

1. Standardize terminology around printer technology: the text mixes FDM and FFF.

2. The methods section would benefit from a short subsection titled “Manufacturing constraints used to define the BO search space.”

3. Replace “ensure cyclic interface durability” with a more cautious phrase unless test data are shown.

Mock Editor (JMD Associate Editor) Decision Letter

Thank you for submitting the revised manuscript. The revision is stronger than the prior-round draft in several important ways: the PLA/TPU material system is now internally consistent; the internal TPU anchor mechanism is described clearly; the methods have been expanded with a more concrete parameterization, standards-aware testing plan, and a substantially more credible Ax/BoTorch optimization framework; and the synthetic placeholder figures are honestly labeled rather than being presented as if they were data. These are meaningful improvements and they do move the manuscript closer to something that could be publishable. That said, the paper is still not ready for acceptance, or for a minor revision path, because the core Results and Discussion remain placeholders and several central methodological points remain internally inconsistent or under-specified.

Decision: Major Revision

Priority-ordered revisions required before resubmission

1. Convert the manuscript from a planned-methods draft into a completed research paper. Real experimental results are required. Synthetic illustrative figures cannot stand in for Results in a JMD Research Paper.

2. Resolve the scope and venue framing. Decide whether this paper is primarily:
   a. a JMD design-method paper on experiment-driven BO of tensegrity-inspired energy absorbers, with crutch tips as a future application, or
   b. an application paper centered on crutch-tip biomechanics and assistive-device impact attenuation.
   The current manuscript mixes these two frames. If the crutch-tip application remains central, it must appear in the title/abstract/introduction, drive the requirements and metrics, and be validated against application-relevant loading conditions.

3. Make the design parameterization internally consistent. Specifically reconcile:
   a. the claim that D3 symmetry reduces 12 member-diameter axes to four orbit axes,
   b. Table 1, which currently shows only one strut diameter and one cable diameter,
   c. the categorical cable-diameter set versus the continuous d_t range, and
   d. the actual connectivity-topology variables used in the BO search space.

4. Fully specify the BO methodology. The resubmission should state the surrogate model class, kernel choice, transforms/normalization, noise treatment, acquisition settings, batch size, initialization protocol, total budget, stopping rule, seed policy, and the exact categorical/hierarchical encoding used in Ax. Also justify why SAASBO is the appropriate default for the dimensionality actually used in the first campaign.

5. Sharpen the novelty claim against the closest prior art, especially Pajunen et al. (2019), Intrigila et al. (2022), and Mo et al. (2023). A comparison table would help. The paper must show exactly what is new in design representation, fabrication route, optimization loop, and validation.

6. Complete the additive-manufacturing methods. All process-critical parameters must be reported, and claims regarding the internal-anchor joint should be supported by at least basic strength/repeatability evidence or softened accordingly.

7. Strengthen the application-transfer discussion if crutch tips remain part of the central story. The present axial bench tests are not sufficient proxies for real crutch use without a much clearer rationale and explicit limitations. If that rationale cannot be made convincingly in this paper, reposition the assistive-device aspect as future work.

8. Add a limitations section that squarely addresses experimental budget, single-printer dependence, axial-only loading, unresolved cyclic durability, and the gap between the current prototype scale and any eventual crutch-tip envelope.

Venue fit assessment

At this stage, the manuscript is closest to an ASME JMD Research Paper only if the final version delivers on the design-method contribution: a well-defined parameterized design space, a rigorous experiment-driven BO workflow, and genuine design insight from the optimization campaign. If those pieces remain the center of gravity, JMD is defensible. If the final paper ends up emphasizing multimaterial printability windows, interface/joint mechanics, and process reproducibility more than design methodology, Additive Manufacturing would likely be the better fit. If the assistive-device biomechanics and user-relevance become central, a biomechanics-oriented outlet such as Journal of the Mechanical Behavior of Biomedical Materials may be stronger. Smart Materials and Structures could also be a reasonable backup if the paper leans more toward architected metamaterial behavior than design methodology. This draft does not read like a Technical Brief. It is also not naturally a Design Innovation paper unless the manuscript is restructured around the design artifact and design process rather than hypothesis-driven experimental evaluation.

Assessment of progress since round 1

Yes, the manuscript has moved closer to acceptance. The revision resolves several earlier internal inconsistencies and substantially improves the methodological scaffolding. The remaining obstacles are not cosmetic; they are the absence of actual results, unresolved search-space inconsistencies, incomplete AM process disclosure, and an unsettled scope between general architected-material design and crutch-tip application.

Reviewers’ bibliographic gaps

Likely missing or still underused references by topic, based on the current references.bib and the manuscript text:

- Tensegrity-inspired AM and impact/metamaterial context: Bauer et al. 2021, Advanced Materials, on additively manufactured tensegrity-inspired metamaterials; Pajunen et al. 2021, Extreme Mechanics Letters; any directly relevant follow-on papers from the Daraio/Rimoli line beyond the 2019 Materials & Design paper.
- Cellular energy-absorber metric definitions: Gibson and Ashby on cellular solids; Avalle, Belingardi, and Montanini (2001); Tan et al. (2005); Michailidis et al. (2011) for SEA, densification strain, and compaction efficiency conventions.
- Categorical/mixed-variable BO in engineering design: papers beyond Garrido-Merchan and BOCS that are closer to constrained mixed-variable physical experimentation may help justify the chosen encoding.
- Crutch-tip / assistive-device biomechanics: additional papers that directly connect crutch-tip compliance or damping to upper-extremity peak loads and loading rate would strengthen the translation argument.
- Impact/shock test standards relevant to cushioning or polymeric energy absorbers: if the manuscript keeps a crutch-tip framing, standards or canonical methods closer to footwear/assistive-device impact attenuation may be more persuasive than the current broad ASTM/ISO list.
- Multimaterial PLA/TPU interface durability and fatigue: references specifically on cyclic loading, interfacial strength, and dimensional fidelity for co-printed rigid/soft polymer transitions would strengthen the joint-mechanics claims.

- Discretionary analytical decisions made during the analysis
- Treated the LaTeX source, not the PDF, as the primary review object because it exposed unresolved TODOs, internal inconsistencies, and manuscript structure more directly than the rendered clean PDF.
- Focused the mock review on structure, framing, method rigor, novelty, literature, internal consistency, and venue fit, while deliberately not evaluating absent quantitative results beyond noting that their absence blocks acceptance.
- Used the clean and TODO-aware manuscript structure described in README to infer intended submission state and JMD formatting expectations.
- Interpreted JMD fit primarily through the manuscript’s apparent center of gravity: design methodology versus additive-manufacturing process study versus rehabilitation application study.
- Flagged the D3-orbit parameterization as inconsistent with Table 1 based on the textual description of four orbit axes versus the tabulated variables, rather than assuming an unstated implementation detail.
- Flagged the tendon-diameter search space as inconsistent because both a categorical printable set and a continuous range are explicitly present in the source.
- Treated synthetic Ax/BoTorch figures as ethically acceptable placeholders because they are explicitly labeled as synthetic, while still judging them insufficient for a research-paper decision.
- Chose not to recommend rejection because the revision appears substantially improved and methodologically promising, but recommended major revision because the absence of real results and unresolved method details are still decisive.
