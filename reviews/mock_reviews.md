# Mock MRG Review Committee Feedback

**Proposal:** Experiment-Driven Design of Multi-Material 3D-Printed Tensegrity Structures for Energy Absorption

**PIs:** Jeffrey R. Hill (PI), Sterling G. Baird (Co-PI)

**Budget:** $25,000 over 2 years

**Students:** 2 undergraduates, 1 graduate co-mentor

---

## Reviewer 1

### Necessary Criteria Assessment

| Criterion | Met? | Comments |
|---|---|---|
| Focus on mentoring undergraduate students | Yes | Mentoring is woven throughout the proposal, not confined to a single section. The layered mentoring structure (faculty, graduate co-mentor, peer mentoring) is clearly articulated. |
| Consistent with faculty scholarship responsibilities | Yes | Both PIs have relevant expertise—Hill in structural mechanics and smart materials, Baird in Bayesian optimization and materials informatics. |
| Full-time faculty PI | Yes | Both PI and Co-PI are faculty in Mechanical Engineering at BYU. |
| Scholarship outcomes | Yes | Conference presentations (UCUR, ASME IDETC) and a peer-reviewed journal manuscript are explicitly planned. |

### Distinguishing Criteria

**Quality of mentoring experience: Strong**

The mentoring plan is one of the strongest aspects of this proposal. The progressive scaffolding model—moving students from guided replication of existing designs to independent creation of novel geometries by mid-Year 1—is well thought out. The concrete milestones (first successful multi-material print, first compression test, first data set fed into the BO loop) give students tangible evidence of progress, which is important for sustaining motivation.

The layered mentoring structure is compelling: weekly one-on-one faculty meetings for strategic guidance, a graduate co-mentor for day-to-day troubleshooting, and peer mentoring in Year 2 where experienced students mentor newly recruited sophomores. This creates multiple touch points and ensures students are not left without support.

The division of students into complementary roles (Student 1: design and fabrication; Student 2: testing and optimization) is smart because it creates natural peer-learning opportunities and teaches interdisciplinary collaboration. Each student develops distinct expertise while remaining connected to the full research cycle.

**Potential impact of work: Moderate to Strong**

The experiment-driven Bayesian optimization framework applied to tensegrity-inspired structures is a timely topic at the intersection of advanced manufacturing, metamaterials, and machine learning. The open-source dissemination of data, code, and tested designs extends the impact. However, the impact argument could be strengthened by being more specific about what gap this work fills relative to existing tensegrity and metamaterial literature.

### Strengths

1. **Mentoring is demonstrated, not just stated.** The proposal shows mentoring in action across every section rather than isolating it in a "Mentoring Environment" section. Student roles, mentoring cadences, and development trajectories are specific and believable.
2. **Accessible entry point.** The experiment-driven approach is genuinely accessible to undergraduates without simulation or advanced modeling prerequisites. This broadens the pool of students who can participate meaningfully.
3. **Structured but flexible.** The timeline is detailed enough to be credible but allows for iteration (e.g., simulation is optional, BO batch sizes can adapt to printing throughput).
4. **Two PIs with complementary expertise.** Hill brings structural mechanics and experimental testing; Baird brings data-driven optimization. This is a natural pairing for this project.

### Weaknesses

1. **Student 2's learning curve for BO may be steep.** While the proposal claims the project is accessible, implementing a Bayesian optimization loop in BoTorch/Ax is non-trivial, even with graduate co-mentor support. The proposal would benefit from more detail on how this student will be ramped up—e.g., pre-built templates, simplified starter problems, or structured tutorials.
2. **Biosketches lack specific publications.** Both biosketches describe research areas generically but list no specific publications. This makes it harder to evaluate the PIs' track records in the relevant areas (tensegrity structures, multi-material printing, BO for materials).
3. **The "50–100+ specimens" claim needs grounding.** The proposal estimates 50–100+ unique specimens over two years but does not justify this with printing times, testing throughput, or failure rates. If multi-material prints have high failure rates early on, this number may be optimistic.

### Suggestions for Improvement

- Add 2–3 representative publications to each biosketch to establish credibility in the relevant research areas.
- Provide a brief estimate of per-specimen fabrication and testing time to ground the throughput claim.
- Clarify how Student 2 will be onboarded to BoTorch/Ax—mention specific learning resources, starter scripts, or simplified initial BO problems.

### Overall Assessment

**Recommend funding.** This is a well-structured proposal with a strong mentoring plan and a scientifically interesting research question. The experiment-driven approach is well-suited to undergraduate research, and the complementary PI expertise is a good fit. The weaknesses noted above are addressable and do not undermine the core proposal.

---

## Reviewer 2

### Necessary Criteria Assessment

| Criterion | Met? | Comments |
|---|---|---|
| Focus on mentoring undergraduate students | Yes | Mentoring is central and well-integrated. |
| Consistent with faculty scholarship responsibilities | Yes | Aligns with both PIs' areas. |
| Full-time faculty PI | Yes | Confirmed. |
| Scholarship outcomes | Yes | Journal submission and conference presentations planned. |

### Distinguishing Criteria

**Quality of mentoring experience: Moderate to Strong**

The mentoring structure is well-articulated, but I have some concerns about execution. The proposal relies heavily on the graduate co-mentor for day-to-day support, yet the budget allocates only $2,500 for graduate wages over two years. This is a very modest investment for what appears to be a critical role. If the graduate student is funded primarily through other means, this should be stated explicitly. If the graduate student leaves or becomes unavailable, the mentoring model loses a key layer.

The peer mentoring component in Year 2 is a nice addition, but the logistics are vague. How will experienced students be prepared to mentor? Will there be any training or structure, or is this assumed to happen organically?

**Potential impact of work: Moderate**

The research is technically sound but incremental. Bayesian optimization of 3D-printed structures has been demonstrated in several prior studies (the proposal cites Wang et al. 2022 and Mo et al. 2023). The contribution here is applying BO to tensegrity-inspired multi-material structures specifically, and doing so with a purely experimental (no simulation) loop. This is a reasonable contribution but not a paradigm shift.

The broader impact claims (protective equipment, packaging, aerospace) are generic and not well substantiated. At the scale of this project—unit-cell-level testing on a desktop FDM printer—the connection to real-world applications is aspirational rather than demonstrated.

### Strengths

1. **Clear, well-defined student projects.** Each student has a distinct scope with concrete deliverables. This avoids the common pitfall of vague or overlapping responsibilities.
2. **Hands-on, tangible research.** Students will design, print, and physically test structures. This is motivating and pedagogically effective for undergraduates.
3. **Reasonable budget.** The $25,000 allocation is appropriate for the proposed work. No expensive equipment purchases are required.

### Weaknesses

1. **Graduate co-mentor is underfunded.** $1,250/year ($2,500 total) for a graduate student who is described as providing "day-to-day guidance" is unrealistic unless the student is funded through other means. This creates a fragility in the mentoring plan.
2. **Limited novelty.** BO for metamaterial design has been done. Multi-material 3D printing of tensegrity-like structures has been done (Pajunen et al. 2019, Ye et al. 2023). The combination is reasonable but the proposal does not clearly articulate what is genuinely new here beyond the specific material/geometry pairing.
3. **Risk mitigation is thin.** What happens if multi-material PLA–TPU printing proves unreliable on the available printer? The proposal acknowledges potential interface issues (void formation, mixed-mode fracture) but does not describe a fallback plan. Early print failures could consume significant time and budget.
4. **Impact claims are overstated.** Protective equipment, aerospace, and packaging are mentioned as applications, but the proposal does not describe how unit-cell-level testing results would translate to any of these domains.

### Suggestions for Improvement

- Clarify the graduate co-mentor's funding source and time commitment. If funded through another mechanism, state this explicitly to alleviate concern about the sustainability of this role.
- Sharpen the novelty statement. What specific scientific question does this work answer that prior BO-for-metamaterials work has not? Is it the experiment-only (no simulation) approach? The PLA–TPU material combination? The tensegrity topology specifically? Make this explicit.
- Add a brief risk mitigation paragraph. If multi-material printing proves unreliable, what is the backup plan? (e.g., single-material geometries, alternative material combinations)
- Temper the broader impact claims or connect them to specific next steps that would bridge the gap between unit-cell testing and real applications.

### Overall Assessment

**Recommend funding with revisions.** The mentoring plan is solid and the research is feasible, but the proposal would benefit from sharpening the novelty argument, addressing the graduate co-mentor funding concern, and adding a risk mitigation plan. These are fixable issues; the core idea is sound.

---

## Reviewer 3

### Necessary Criteria Assessment

| Criterion | Met? | Comments |
|---|---|---|
| Focus on mentoring undergraduate students | Yes | The proposal clearly prioritizes mentoring. |
| Consistent with faculty scholarship responsibilities | Yes | Both PIs are working in relevant domains. |
| Full-time faculty PI | Yes | Confirmed. |
| Scholarship outcomes | Yes | Conference presentations and journal manuscript are planned outcomes. |

### Distinguishing Criteria

**Quality of mentoring experience: Strong**

This is a well-designed mentoring program. Several features stand out:

- The **progressive scaffolding model** is specific and credible: students start by replicating known geometries, progress to modifying parameters, and ultimately design novel topologies. This mirrors best practices in undergraduate research mentoring.
- The **complementary student roles** create a natural peer-learning dynamic. Student 1 develops manufacturing expertise; Student 2 develops data analysis and optimization skills. Their interdependence forces communication and collaboration.
- The **summer intensive period** with increased meeting frequency (twice-weekly faculty meetings, daily graduate co-mentor interaction) is well-structured. Summer full-time research is often where the most growth happens, and the proposal recognizes this.
- The **Year 2 peer mentoring** creates a sustainability mechanism and develops leadership skills in experienced students.

**Potential impact of work: Moderate to Strong**

The experiment-driven BO framework is a compelling model for how undergraduates can contribute to data-driven research. The open-source data/code commitment adds value. The direct applicability to protective equipment and lightweight structures is plausible, though the proposal would be stronger with a more specific motivating problem (e.g., a particular helmet standard, a specific energy absorption target).

### Strengths

1. **Mentoring plan is among the strongest I have reviewed.** The layered structure, progressive scaffolding, and peer mentoring in Year 2 are all well-articulated and specific. This is not a generic "students will be mentored" statement—it is a detailed plan.
2. **Experiment-driven approach is well-suited to MRG goals.** The choice to center the project on physical experimentation rather than simulation removes a major barrier to undergraduate participation while still producing publishable results.
3. **Budget is clean and well-justified.** No frivolous expenses. The front-loading of supplies in Year 1 and travel in Year 2 makes logical sense.
4. **Timeline is detailed and realistic.** The Gantt-style table clearly shows how tasks map to semesters, with appropriate ramping.

### Weaknesses

1. **Only 2 undergraduate students for $25,000.** At $18,000 in undergraduate wages over two years, each student receives $9,000. This is reasonable for part-time + summer work, but the MRG is spending $12,500/student. Some reviewers may feel that more students should benefit for this level of investment. Could a third student be added in Year 2, even in a limited role?
2. **Budget justification mentions "simulation" for undergrad work** (budget.tex line 34–35: "full-time during summer terms for simulation, 3D printing, and testing"), but the proposal body explicitly de-emphasizes simulation. This inconsistency, while minor, suggests the budget narrative was not fully updated after the proposal's strategic pivot to experiment-driven work.
3. **No explicit assessment or evaluation plan.** How will the PIs know if the mentoring is successful? Student satisfaction surveys? Tracking of post-graduation outcomes? Conference paper acceptance rates? An evaluation plan, even brief, would strengthen the proposal.
4. **Relationship to external funding section could be stronger.** The statement "If successful, the preliminary data may inform a future NSF proposal" is honest but may concern reviewers who worry the MRG is primarily serving as seed funding for external grants rather than as a standalone mentoring initiative.

### Suggestions for Improvement

- Consider whether a third undergraduate could be brought on in Year 2 in a limited capacity, mentored by the Year 1 students. This would increase the mentoring reach and demonstrate the peer mentoring model more concretely.
- Fix the simulation reference in the budget justification to match the proposal body's experiment-driven framing.
- Add a 2–3 sentence evaluation plan: How will the PIs assess whether the mentoring objectives were met? (e.g., student self-assessments, tracking of conference submissions, graduate school applications)
- Reframe the external funding relationship to emphasize that the MRG is self-contained and the mentoring outcomes are the primary goal, with any external proposal being a secondary benefit.

### Overall Assessment

**Recommend funding.** This is a strong proposal with an excellent mentoring plan, a feasible and well-scoped research project, and a clean budget. The weaknesses identified are minor and mostly relate to tightening the narrative rather than fundamental concerns. The budget inconsistency (simulation reference) should be corrected before final submission.

---

## Summary of Reviewer Consensus

### Areas of Agreement

- **All reviewers agree the necessary criteria are met.** The proposal clearly focuses on mentoring undergraduates, is consistent with faculty scholarship, has a full-time faculty PI, and plans for scholarship outcomes.
- **All reviewers rate the mentoring quality highly.** The layered mentoring structure, progressive scaffolding, and peer mentoring in Year 2 are consistently praised.
- **All reviewers find the budget reasonable** and the timeline realistic.
- **All reviewers recommend funding** (two unconditionally, one with revisions).

### Common Concerns

1. **Graduate co-mentor funding and sustainability** (Reviewers 1 and 2): The graduate student plays a critical role but receives modest funding ($2,500 total). Clarifying the funding source and contingency plan would strengthen the proposal.
2. **Specimen throughput claim** (Reviewer 1) and **risk mitigation** (Reviewer 2): The "50–100+ specimens" estimate and the reliance on multi-material printing both need more grounding. What if print reliability is lower than expected?
3. **Biosketches lack specificity** (Reviewer 1): Adding representative publications would strengthen credibility.
4. **Budget justification inconsistency** (Reviewer 3): The reference to "simulation" in the budget text should be corrected to match the experiment-driven framing.
5. **Novelty articulation** (Reviewer 2): The proposal should more clearly state what is new relative to prior BO-for-metamaterials work.

### Recommended Revisions (Priority Order)

1. **Fix budget justification** to remove the reference to "simulation" (simple text correction).
2. **Clarify graduate co-mentor funding source** and contingency if the student becomes unavailable.
3. **Add representative publications** to biosketches.
4. **Add a brief risk mitigation paragraph** addressing potential multi-material printing challenges.
5. **Sharpen the novelty statement** to distinguish this work from prior BO-for-metamaterials studies.
6. **Ground the throughput estimate** with per-specimen fabrication and testing times.
7. **Add a brief evaluation plan** for assessing mentoring success.
