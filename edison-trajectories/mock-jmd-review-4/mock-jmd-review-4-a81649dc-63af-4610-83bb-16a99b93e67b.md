# Edison trajectory -- mock-jmd-review-4

Task ID: `a81649dc-63af-4610-83bb-16a99b93e67b`  
Status: success

## Query

FOURTH-ROUND mock peer review for an ASME Journal of Mechanical Design (JMD)
Research Paper submission. You reviewed earlier drafts of this same manuscript
in three prior rounds (round 1 = Reject-and-Resubmit, round 2 = Major Revision,
round 3 = Major Revision but improving); this is the further-revised draft. The
attached files are the current populated draft (manuscript.pdf is the clean
reader PDF; manuscript-todos.pdf is the review PDF that additionally shows margin
\todo{} annotations and a \listoftodos; supplementary.pdf is the Supplementary
Information; sources are manuscript-body.tex / manuscript.tex /
manuscript-todos.tex / supplementary.tex and references.bib;
manuscript/README.md documents venue choice and build).

The paper is a multi-material 3D-printed (FDM) tensegrity-inspired
energy-absorbing structure study using experiment-driven Bayesian optimization
(BO). Rigid PLA struts in compression + soft TPU cables in tension, printed on a
Bambu Lab H2D dual-nozzle FDM printer, characterized under quasi-static
compression and drop-weight impact. The motivating application is framed up
front as a planetary-lander / payload energy absorber; a crutch-tip is mentioned
only as future work in the Discussion. Quantitative Results/Discussion are
INTENTIONALLY still \todo{} placeholders -- the project is at the
planned-methods phase. Please review structure, framing, scope, novelty claims,
methods rigor, literature coverage, internal consistency, and venue fit (ASME
JMD vs. backup Smart Materials and Structures / Additive Manufacturing), NOT raw
numerical values.

What CHANGED since round 3 (so you can focus on the current state rather than
re-flagging already-addressed items). These edits respond directly to the
round-3 Associate-Editor letter and reviewer comments:
  * CITATIONS NOW REAL (no longer TODO promises): the manuscript now cites the
    primary SAASBO paper (Eriksson & Jankowiak, UAI 2021) and the primary TuRBO
    paper (Eriksson et al., NeurIPS 2019); the canonical energy-absorber-metric
    references for SEA / densification displacement / compaction (energy-
    absorption) efficiency (Gibson & Ashby 1997; Avalle, Belingardi & Montanini
    2001; Tan et al. 2005; Michailidis et al. 2011); and the SAE J211/1 impact-
    instrumentation standard for the CFC-180 channel filtering. The matching
    "cite once added to bib" TODO notes were removed.
  * BO FORMULATION PRE-COMMITTED: the primary reported campaign is now stated
    explicitly as a CONSTRAINED MULTI-OBJECTIVE problem -- maximize SEA and
    compaction efficiency subject to an upper bound on peak transmitted force
    F_max <= F*, with F* fixed from the rigid-control drop response. The
    acquisition function is qNEHVI; the hypervolume reference point is anchored
    at the rigid-control (SEA, eta_c) pair. A single-objective LogEI run on SEA
    (same force constraint) is retained ONLY as a baseline. The input-noise-
    robust and evolution-guided constrained variants are now explicitly demoted
    to a contingency (adopted only if between-print variability dominates), not
    part of the default loop -- addressing the "toolkit inventory" concern.
  * SAASBO JUSTIFICATION made empirical: the campaign now benchmarks SAASBO
    against a standard single-task GP baseline with the same Matern-5/2 ARD
    kernel (retrospective leave-one-out calibration / predictive accuracy),
    rather than only asserting better UQ.
  * BUDGET CONSISTENCY: the specimen budget reads unambiguously as n=9 Sobol
    initialization + T=10 sequential batches of q=5 = 59 specimens total.
  * SCOPE DISCIPLINE: the Introduction now states explicitly that the study is
    scoped to single-cell, fixed-topology T3-prism specimens under AXIAL
    loading, and that off-axis / combined loading, multi-hit and cyclic
    durability, and landing-attitude variability are OUT OF SCOPE (future work);
    the novelty/generality claims are correspondingly scoped to this restricted
    prototype design space.
  * JOINT DIAMETER: the manuscript now explains WHY the joint diameter d_j is
    fixed at 7.0 mm (it sets the printed strut-end cage housing the internal
    cable anchors; constrained by tendon-outlet count and dual-nozzle clearance;
    fixing it keeps anchor geometry constant so the five optimized variables are
    not confounded by joint-strength changes); relaxing d_j is deferred to a
    follow-on joint-design study.
  * AS-BUILT RESOLUTION: a new paragraph acknowledges that although d_s and d_t
    are nominally continuous, the as-built cross-sections are discretized by
    nozzle diameter, line width, and support interaction, so the effective
    search granularity is coarser than the nominal continuous box; measured
    as-built diameters are reported and the dimensional spread is folded into
    the inferred observation noise.
  * METAL-ANALOG VALIDATION: the rank-preservation criterion is now fixed in
    advance as the Spearman rank-correlation coefficient rho_s between the two
    material systems' SEA orderings (peak transmitted force as a secondary
    ranking), and the test is framed as a STRINGENT, EXPLORATORY transfer test
    (deformation modes, joint compliance, friction, pretension, and strain-rate
    sensitivity all differ between PLA/TPU and Al/SS), not a presumed
    one-to-one validation.

STILL INTENTIONALLY OPEN (known gates, do not re-flag as new defects): the
quantitative Results and Discussion remain \todo{} placeholders and several
BO/impact figures are illustrative synthetic examples; some fabrication/test
process parameters (Table 3 print settings, exact fixtures/DAQ) remain TBD
pending the campaign; the Zenodo archival DOI is a placeholder.

Produce FOUR artifacts, in the same style as a JMD decision-letter package:

1. Mock Reviewer #1 -- Design / Mechanical Engineering (typical ASME JMD
   reviewer). Strict on novelty vs. prior tensegrity/lattice/spring-loaded work,
   on the BO formulation (kernel, acquisition, noise, batch/budget, SAASBO
   justification at ~5 variables, constrained multi-objective formulation and
   reference point), on parameterization completeness and Table-1 consistency,
   and on JMD scope fit. Major / Minor / Editorial; recommend
   Accept / Minor / Major / Reject / Reject-and-Resubmit.

2. Mock Reviewer #2 -- Biomechanics / impact-mechanics. Strict on the
   energy-absorber motivation, relevance of the axial drop-tower fixture vs.
   real off-axis/cyclic loading, transferability, and metric mapping (SEA ->
   peak transmitted force). Recommendation.

3. Mock Reviewer #3 -- Additive manufacturing / materials. Strict on the
   PLA+TPU multi-material FDM processing claims, the internal-anchor joint vs.
   alternatives, interface durability/fatigue (now appropriately softened?),
   FDM repeatability and resolution limits for continuous-diameter members
   (now discussed?), process-parameter disclosure, and the metal-analog (Al/SS)
   validation plan (now with a pre-specified rank metric?). Recommendation.

4. Mock Editor (JMD Associate Editor) decision letter synthesizing the three
   reviews: single-paragraph summary, decision, and an itemized,
   priority-ordered list of revisions required before resubmission. Explicitly
   assess venue fit and explicitly state whether the round-4 revisions have
   moved the manuscript closer to acceptance relative to the round-3 Major
   Revision decision.

End with a short "Reviewers' bibliographic gaps" section listing specific
peer-reviewed references the authors are likely still missing, by topic, given
references.bib (note which round-3 gaps -- SAASBO, TuRBO, SEA/densification
metrics, SAE J211 -- are now closed).

Be honest, specific, and grounded in the attached files. It is acceptable (and
expected) to note that the placeholder \todo{}s and the absence of experimental
results gate the final decision. Where round-3 concerns have been resolved, say
so; where they persist or new ones appear, flag them.


---

## Answer

Mock Reviewer #1 — Design / Mechanical Engineering
Recommendation: Major Revision

This fourth-round draft is materially improved relative to the round-3 version. The biggest round-3 problems that blocked serious technical review are now addressed: the key Bayesian-optimization citations are real and appropriate; the primary BO campaign is now pre-committed as a constrained multi-objective formulation rather than a menu of possible algorithms; the SAASBO choice is framed as something to be benchmarked rather than asserted; the specimen budget is internally consistent at 59; the scope is now explicitly limited to a single-cell fixed-topology T3 prism under axial loading; the fixed joint diameter is justified; the as-built discretization of nominally continuous diameters is acknowledged; and the metal-analog comparison is now framed as an exploratory rank-preservation test with a pre-specified Spearman metric. Those are real improvements.

What still prevents a favorable recommendation is that the manuscript remains, by the authors’ own explicit statement, at a planned-methods stage, with Results and Discussion still placeholders and several figures synthetic or illustrative. For JMD, a research paper can tolerate some final polishing still in progress, but not the absence of the core evidence that the claimed design method actually works. So my recommendation remains Major Revision rather than acceptance-level support.

Major comments

1. The paper still lacks the evidence needed to support its central contribution.
The manuscript now states clearly that the “closed-loop experimental campaign has not yet produced reportable results” and that Sections 4 and 5 remain placeholders. That honesty is good. But it also means the main claim — that experiment-driven BO is an effective design method for this architecture class — is not yet demonstrated. The manuscript currently offers a framework, not a completed JMD research study. Until the authors report actual closed-loop outcomes, the paper cannot be judged on novelty in practice, BO effectiveness, sensitivity structure, or design insight.

2. The novelty positioning is much better, but still not quite sharp enough for JMD.
Table 1 is useful and the comparison against Pajunen et al. 2019, Intrigila et al. 2022, and Mo et al. 2023 is the right move. Still, the Introduction contains a TODO explicitly noting that “1–2 sentences clearly stating the gap this paper closes” still need to be written. That gap statement is not cosmetic. It is the sentence JMD readers will use to decide whether this is a design-method paper or a materials/process paper with BO attached. Right now the implied claim is: multi-material PLA/TPU tensegrity-inspired architecture + experiment-driven BO + physical testing. That is plausible as a contribution, but the manuscript should state more crisply what design knowledge becomes possible only because of the closed-loop method.

3. The BO section is substantially improved, but some design-method details still need tightening.
The constrained multi-objective statement is now coherent: maximize SEA and compaction efficiency subject to F_max <= F*, with qNEHVI and a rigid-control-anchored reference point, plus a LogEI SEA-only baseline. Good. This directly resolves the round-3 “toolkit inventory” problem.

That said, a few details still need to be made fully operational rather than aspirational:
- The definition of the rigid control used to set F* should be stated unambiguously in the Methods. Is it a no-absorber impact, a rigid PLA-only specimen, or another baseline configuration?
- If hypervolume is anchored at the rigid-control (SEA, eta_c) pair, say explicitly whether designs worse than the control in one objective but better in the other remain admissible so long as they satisfy the force constraint.
- The manuscript says observation noise is modeled as learned homoscedastic noise, while dimensional spread is “folded into the inferred observation noise.” That is acceptable as a first pass, but the paper should justify homoscedastic noise if replicate data later show clear geometry-dependent variance.
- The SAASBO benchmark plan is sensible, but the exact retrospective comparison criterion should be pre-specified more explicitly than “leave-one-out calibration and predictive accuracy.” Which metrics: RMSE, negative log predictive density, empirical coverage, rank correlation of candidate ordering, or some combination?

4. The parameterization is more disciplined, but manufacturing-feasibility constraints remain under-specified.
The working prototype is now clearly five-dimensional: R, H, theta, d_s, d_t, with d_j fixed at 7.0 mm. Good. The as-built resolution paragraph is also a needed improvement. But the manuscript still contains a TODO to “specify exact manufacturing-feasibility constraints once finalized.” At this stage, that is not a side issue. If the BO box includes geometries that are technically printable in CAD but not reliably fabricable or testable, the effective search space differs from the stated one. JMD readers need the actual admissibility rules.

5. The manuscript is closer to JMD scope than before, but the fit is still conditional on the final paper emphasizing design methodology rather than process documentation.
In its present form, the strongest JMD-relevant content is the design parameterization, objective formulation, and closed-loop physical design strategy. The weakest JMD-fit elements are the still-large amount of process scaffolding, internal development placeholders, and application discussion that extends beyond demonstrated evidence. If the final revision reports completed BO campaigns and extracts design-method insight — for example, tradeoff structure, variable importance, and how the force-constrained Pareto set differs from intuition or one-factor-at-a-time design — then JMD is defensible. If the paper remains mainly a multi-material print/process and test-development paper, Additive Manufacturing or Smart Materials and Structures may be the more natural home.

Minor comments

1. The statement that SAASBO is retained for a ~5–6 variable problem is now much more defensible because the manuscript promises an empirical benchmark against a standard single-task GP with the same Matern-5/2 ARD kernel. That resolves a major round-3 concern in principle.

2. The explanation for fixing d_j at 7.0 mm is good and should stay. It directly addresses confounding between anchor geometry and the five optimized variables.

3. The as-built discretization paragraph is one of the better additions in this revision. Keep it.

4. The metal-analog validation framing is now appropriately softened. Treating it as an exploratory transfer test rather than “validation” in a strong sense is much more credible.

5. The manuscript still has too many visible internal-planning TODOs for a peer-review draft, even acknowledging this is a mock review exercise. Several are harmless, but some mark genuine conceptual incompleteness.

Editorial comments

1. Remove internal repository/PR/Edison references from the main text before any real submission. They belong, if anywhere, in author notes or SI, not in the paper narrative.
2. The abstract still reads like a proposal abstract, not a research-paper abstract.
3. Table 3 print parameters cannot remain mostly TBD in a real revision.
4. The Conclusions section currently overstates completion relative to the actual manuscript state.
5. The Discussion section is still only a topic list.

Bottom line

This draft is clearly stronger than round 3. The authors have done real work tightening scope, methodology, and citation discipline. But the paper is still gated by missing results, missing finalized process details, and a not-yet-completed design-method story. I would support another major revision if this were an internal mock cycle; I would not support acceptance or minor revision at this stage.

Mock Reviewer #2 — Biomechanics / Impact Mechanics
Recommendation: Major Revision

This revision is improved in two important ways from an impact-mechanics standpoint. First, the manuscript now explicitly limits scope to axial quasi-static and axial drop-weight loading, with off-axis, combined loading, cyclic/multi-hit durability, and landing-attitude variability declared out of scope. That is the right move. Second, the energy-absorption metrics are now grounded in standard references for SEA, densification displacement, and compaction efficiency, and the SAE J211/1 CFC-180 citation closes an obvious instrumentation gap.

Even with those improvements, the paper remains methodologically incomplete as an impact study because the impact evidence is still absent and some motivation-to-test mapping remains thin.

Major comments

1. The claimed application framing is still broader than the demonstrated loading scenario.
The abstract and introduction point to “aerospace landing structures” and planetary-landing-inspired tensegrity systems. The current fixture, however, is an axial drop configuration with constrained top motion and guided base registration. That is acceptable for a first prototype study, but the manuscript should be very careful not to imply that the present tests represent realistic lander touchdown conditions. The new scope paragraph helps, but the paper should say even more directly that the current setup is a screening test for axial load attenuation, not a lander analog.

2. The mapping from SEA to impact protection remains underdeveloped.
The manuscript does better now in making peak transmitted force a constrained quantity rather than just another objective. That is the right direction, because impact protection is not equivalent to maximizing SEA. Still, the paper should explain more explicitly why the chosen optimization structure — maximize SEA and compaction efficiency subject to F_max <= F* — best reflects the application logic. For cushioning systems, the force-time history, stroke availability, rebound, and timing of densification can matter as much as total absorbed energy. I am not asking the authors to add new metrics now, but I do want a stronger rationale for why these three metrics are sufficient for the present screening study.

3. The fixture description raises transferability questions that should be acknowledged more plainly.
The manuscript notes that the rig causes unconstrained specimens to lift off the base during descent and therefore uses light top tethers and base registration features. That is useful honesty. But those details also mean the measured response will depend on boundary-condition management in ways that may not transfer to free-contact applications. This does not invalidate the study. It does mean the authors should explicitly discuss how the fixture may alter early contact transients, specimen alignment, and peak-force measurement.

4. The impact figures are still illustrative synthetic examples.
This is an acceptable drafting device, and the manuscript labels them as synthetic. But until real traces are shown, the reader cannot judge whether the force filtering, event identification, plateau interpretation, and impulse-consistency narrative are actually supported by measured data.

5. The metal-analog transfer test is now framed appropriately, but it should not be oversold as validation of impact relevance.
The new pre-specified Spearman rho_s criterion is much better than the earlier loose wording. Still, ranking agreement between PLA/TPU and Al/SS structures would show only partial transfer of design ordering under the tested conditions. It would not validate human-surrogate, aerospace, or broader impact applicability. The authors mostly understand this now; they should keep that restraint in the final paper.

Minor comments

1. The use of canonical densification and compaction-efficiency references is a clear improvement.
2. Constraining peak transmitted force against a rigid control is conceptually much better than treating all objectives symmetrically.
3. The quasi-static section would benefit from a sentence linking quasi-static observables to the later impact objectives, beyond just using the same specimen family.
4. The slip/traction discussion tied to ISO 11334-4 is now clearly segregated as out of scope. Good.
5. The future crutch-tip discussion is now in the Discussion rather than front-loaded. That is better.

Editorial comments

1. Avoid language that suggests “validation” of planetary-landing use unless real application-relevant boundary conditions are tested.
2. Keep the lander motivation, but scale it back to “inspiration” or “screening relevance” unless later results justify more.
3. Once results exist, report whether F_max is measured before or after filtering, and be precise about which signal is optimized.

Bottom line

This is a better-scoped and more honest impact-mechanics manuscript than the previous round. But the paper still has no actual impact results, and the connection between the motivating application and the axial screening test remains only partial. I would recommend Major Revision.

Mock Reviewer #3 — Additive Manufacturing / Materials
Recommendation: Major Revision

This revision addresses several of my earlier process/materials concerns in a constructive way. In particular, the manuscript now softens the durability claim around the internal-anchor joint, explicitly notes that cyclic interface durability is to be verified rather than assumed, explains why the joint diameter is fixed, adds a thoughtful paragraph on the discretized as-built realization of nominally continuous diameters, and reframes the metal-analog exercise with a pre-specified rank metric. Those are all improvements.

The remaining problem is not that the process concept is unsound; it is that the paper still describes an unfinished fabrication-and-test protocol rather than a completed, reproducible manufacturing study.

Major comments

1. Process disclosure is still insufficient for a real archival paper.
Table 3 remains mostly TBD: nozzle temperatures, bed temperature, layer height, print speed, and infill are not finalized. There is also a TODO to document retraction settings and validation prints used to characterize PLA–TPU interface strength. For a multi-material FDM paper, especially one arguing that fabrication noise is part of the BO loop, these settings are not optional. They shape dimensional accuracy, bonding, TPU stringing, support removal, and joint integrity.

2. The internal-anchor joint is much better justified conceptually, but not yet validated materially.
The manuscript now does the right thing by saying Ye et al.’s wrapped interface is precedent, not validation, and by placing the current TPU-inside-PLA pocket as a different construction. Good. However, the manuscript still contains a TODO to verify junction strength against pull-out studies before making any cyclic-durability claim. That means the joint architecture remains a hypothesis. The paper can still proceed without full fatigue life data if it stops short of durability claims, but it does need at least enough mechanical evidence to show the joint survives the intended test envelope reproducibly.

3. The continuous-variable BO framing is now more realistic because the manuscript acknowledges fabrication quantization.
This is one of the strongest improvements. The authors now state plainly that d_s and d_t are continuous in the optimizer but discretized in the printed artifact by nozzle diameter, line width, and support interaction. Good. The next step is to make the measurement protocol concrete: how many diameter measurements per member, what instrument, at which locations, and whether the optimizer is updated with commanded geometry only or commanded plus measured realized geometry. The current statement suggests the surrogate is fitted on realized geometry, which is a strong and sensible choice, but the workflow should be explicit.

4. Repeatability is recognized but not yet characterized.
The manuscript says dimensional spread will be folded into inferred observation noise. Fine as a model statement. But manufacturing repeatability itself still needs empirical characterization. Even a small planned repeatability subsection would help: replicate builds at one or two geometries, reporting mass, diameter, and perhaps simple stiffness spread. Without that, “noise” risks becoming a catch-all for process variation that is not actually understood.

5. The support-generation workflow is interesting but still reads like development notes.
The narrowing-pillar/manual support strategy may well be important to making the TPU tendons printable. But the paper should condense this into a reproducible manufacturing description rather than a narrative of workaround discovery. Right now the SI still leans heavily on repository-history language.

6. The metal-analog plan is now much more credible methodologically.
Pre-specifying Spearman rho_s as the primary transfer criterion is good practice. But I would still avoid calling the metal system a “validation” unless the geometric similarity, pretensioning protocol, and boundary conditions are actually shown to be comparable enough for that label. “Transfer test” is the better term and the manuscript already uses it.

Minor comments

1. The explanation for fixed d_j = 7.0 mm is convincing and should remain.
2. The manuscript is right to separate the internal-anchor design from exposed overmolded interfaces.
3. The statement that the lower TPU-diameter bound is tied to the Bambu auto-support detection floor is useful and concrete.
4. The selected Bambu Lab H2D platform is fine for a prototype paper, but the single-platform limitation should be acknowledged explicitly in the limitations section.
5. The SI should ultimately include either CAD snapshots or section views that make the internal anchor geometry unambiguous.

Editorial comments

1. Remove claims of improved cyclic durability unless backed by data.
2. Replace repository-task references in the main text with archival descriptions.
3. If real submission is intended, move more manufacturing detail from TODO state into either the main Methods or SI.

Bottom line

The authors have clearly listened to prior criticism. The multi-material FDM story is now more careful and less hand-wavy. But the process is still under-specified and the joint concept still under-validated. I recommend Major Revision.

Mock Editor (JMD Associate Editor) Decision Letter
Decision: Major Revision

This fourth-round revision is closer to publishable form than the prior round-3 Major Revision. The manuscript now shows better methodological discipline, more accurate citation practice, clearer scope control, and a more coherent Bayesian-optimization formulation. In particular, the reviewers agree that several important earlier concerns have been substantively addressed: the previously missing primary citations for SAASBO, TuRBO, the standard energy-absorption metrics, and SAE J211/1 are now present; the optimization campaign is now pre-committed as a constrained multi-objective problem rather than an open-ended algorithm inventory; the SAASBO choice is framed as an empirical benchmark question rather than an assertion; the specimen budget is internally consistent; the fixed joint diameter is justified; the effective discretization of nominally continuous printed diameters is acknowledged; and the metal-system comparison is reframed more appropriately as an exploratory transfer test with a pre-specified rank-based criterion. These changes move the paper in the right direction and represent real progress relative to round 3.

At the same time, the manuscript remains fundamentally incomplete as a JMD Research Paper because its central evidence is still absent. The authors state explicitly that the work remains at a planned-methods phase, that the closed-loop campaign has not yet produced reportable results, and that the Results and Discussion sections remain placeholders. Several methods details remain TBD, including core print settings and some finalized test-protocol disclosures. As a result, the paper cannot yet be assessed on whether the proposed design method actually yields new design knowledge, useful Pareto tradeoffs, or experimentally supported insight beyond prior tensegrity-inspired absorber studies. The manuscript is therefore not ready for acceptance, but it has moved meaningfully closer to acceptance than in round 3.

Required revisions before resubmission, in priority order

1. Complete the paper as a research paper, not a planned-methods scaffold.
Provide the full closed-loop experimental results, including the realized BO campaign outcomes, actual Pareto fronts or constrained tradeoffs, the single-objective baseline comparison, and the completed Discussion section. Without this, the paper remains non-archival.

2. Convert the BO methodology from a proposal to a reproducible implemented method.
State unambiguously how F* is defined from the rigid control, what exact predictive/calibration metrics are used to compare SAASBO against the standard single-task GP baseline, how noise is modeled if replicate data reveal heteroscedasticity, and how realized geometry measurements enter the surrogate-training pipeline.

3. Finalize and disclose the fabrication/process parameters.
Complete Table 3 and any associated text with actual nozzle temperatures, bed temperature, layer height, print speeds, infill, retraction/support settings, and any other process details needed to reproduce the multi-material FDM workflow and interpret process-induced variation.

4. Tighten the paper’s JMD design-method framing.
State the design gap versus Pajunen et al., Intrigila et al., and Mo et al. explicitly in the Introduction. In the final Discussion, extract design-method insight from the completed campaign, not just performance outcomes: tradeoff structure, variable sensitivity, boundary-condition dependence, and what the constrained multi-objective loop reveals that simpler design approaches would not.

5. Keep the application claims aligned with the demonstrated test conditions.
Retain the current scope restrictions and avoid suggesting that axial drop-tower screening alone validates planetary-landing or broader impact applications. The present fixture should be framed as an axial screening test unless future experiments support stronger claims.

6. Remove internal-development scaffolding from the archival narrative.
Eliminate visible TODOs, internal Edison/PR references in the main text, and proposal-style placeholders. Synthetic illustrative figures may be acceptable in drafting, but the resubmission must foreground measured data.

7. Maintain the current restraint regarding the internal-anchor joint and the metal-system comparison.
Do not claim cyclic durability improvements without supporting evidence. Continue to present the Al/SS study as an exploratory transfer test unless much stronger cross-system correspondence is demonstrated.

Venue-fit assessment

At present, the manuscript sits on the boundary between a design-method paper and a fabrication/process-development paper. The route to JMD is still viable, but only if the final revision centers on the design methodology and the experimentally supported design insights enabled by the BO framework. If the finished paper remains dominated by multi-material FDM process development and architecture fabrication details, Additive Manufacturing or Smart Materials and Structures would likely be the more natural venue. Relative to round 3, however, the current revision is more compatible with JMD because it now frames the work more clearly around parameterization, objective definition, constrained tradeoff exploration, and design-space learning.

Reviewers’ bibliographic gaps

Round-3 citation gaps now closed
- SAASBO primary citation: closed.
- TuRBO primary citation: closed.
- Canonical SEA / densification / compaction-efficiency references: closed.
- SAE J211/1 impact-instrumentation standard: closed.

Likely remaining gaps by topic
- 3D-printed tensegrity-inspired or tensegrity-like architected absorbers beyond Pajunen and Intrigila. The manuscript itself flags likely additions such as Bauer et al. (2021, Advanced Materials), Pajunen et al. (2021, Extreme Mechanics Letters), Santos (2023, Advanced Materials), and Sabouni-Zawadzka et al. (2024). These appear to be recognized in TODO text but not yet integrated into references.bib.
- Multi-material additive-manufacturing studies more directly tied to interface design, jointing, or rigid-soft architected lattices, beyond Ye et al., Khatri et al., Caminero et al., and Yavas et al.
- Impact-testing / drop-tower protocol references more directly aligned with the specific axial fixture and signal-processing workflow, beyond Pajunen, ASTM D1596 mention, and SAE J211/1.
- If the paper keeps the design-method emphasis for JMD, additional design-optimization references connecting BO to physical mechanical design experiments may still help situate the contribution more tightly.

- Discretionary analytical decisions made during this review:
  - Weighted the clean manuscript-body.tex as the primary review source, using supplementary.tex and references.bib only to verify process-detail coverage and bibliographic gaps.
  - Treated the manuscript’s explicit planned-methods status and placeholder Results/Discussion as a gating issue for recommendation, consistent with a JMD research-paper standard rather than a methods note standard.
  - Focused comments on changes since round 3 that were directly visible in the files, while avoiding re-flagging intentionally open gates as if they were newly discovered defects.
  - Assessed venue fit conditionally: JMD if final revision emphasizes design-method insight from completed experiments; Additive Manufacturing or Smart Materials and Structures if the center of gravity remains fabrication/process development.
  - Interpreted the metal-system study as an exploratory transfer test rather than formal external validation, based on the manuscript’s revised wording and pre-specified Spearman-rank criterion.
