# Iteration 5: Full JMD referee panel

**Evidence base.** I reviewed the 14-page compiled manuscript, 5-page Supplementary Information (SI), LaTeX sources, `references.bib`, all three campaign CSVs, and the supplied Pareto figure. I recomputed every numerical claim that can be checked from the attached campaign tables. Page numbers refer to the compiled PDFs; `MS L…` and `SI L…` refer to the LaTeX sources.

## Design and optimization referee

### Probe D1: Is this actually a closed-loop optimization result, or only a seed fit followed by untested recommendations?

**Referee:** Your title and repeated use of “experiment-driven Bayesian optimization” invite readers to infer that Bayesian optimization improved the physical design. What physical evidence shows that the recommendations work?

**Author, from the materials:** The manuscript does not claim completed improvement. The abstract says the results “establish the first recommendation step of the physical optimization campaign” and that round 2 remains pending (MS L159–162). The Introduction is also explicit: “closure of a full recommend–fabricate–measure–update cycle awaits round-2 testing” (MS L252–255). The Conclusion repeats that “closure of the full recommend--fabricate--measure--update cycle awaits the round-2 tests” (MS L1482–1487).

**Verdict: WITHSTANDS.** The campaign status is unusually clear. The manuscript reports a functioning measurement-to-recommendation pipeline, not demonstrated optimization gain.

---

### Probe D2: Does the attached round-2 suggestion CSV describe the nine designs actually on the printer?

**Referee:** Your Results say the nine plotted recommendations “have been sliced and sent to the printer” (MS L1263–1267). Yet the SI says two recommendation sets exist and that the repository CSV at branch head is the later constant-printed-mass set proposed for round 3, not the batch actually printed (SI L248–255). Which set is shown in Fig. 7 and supplied as `t3-prism-bo-suggestions-round1.csv`?

**Author, from the materials:** The attached CSV is plainly the regenerated set: all nine rows have `target_mass_g = 20.23` and predicted printed masses of 20.22 g. SI L248–255 says the actually sliced batch used the earlier solid-mass projection, whereas “the repository's suggestion CSV at the branch head is the regenerated (constant-printed-mass) set.” The manuscript does not provide a machine-readable table identifying the actual printed batch, so the claim that Fig. 7 represents the on-printer batch cannot be audited from the supplied materials.

**Verdict: FAILS.** This is a provenance error, not a missing-round-2-data problem.

**Concrete edit:** Replace MS L1257–1267 with:

> “Figure 7 shows the seven measured seed articles and **[identify recommendation set and immutable file/version]** at their posterior-mean predictions. Two recommendation sets exist: the batch physically sent to the printer used the original constant-solid-mass projection, whereas a subsequently regenerated set uses the constant-printed-mass projection described in the SI. Figure 7 and the archived CSV correspond to **[one set only]**.”

Archive both tables under unambiguous names, for example `round2_as_printed_solid_mass.csv` and `round3_candidate_printed_mass.csv`, and make Fig. 7 from the former if it is described as the batch on the printer.

---

### Probe D3: Are the seed-round statistical claims numerically correct and appropriately limited?

**Referee:** With seven mapped articles and one mechanically tested article per geometry, are you reporting noise, effects, and Pareto membership honestly?

**Author, from the materials:** Yes, with one important exception addressed below. Direct recomputation from `t3-prism-bo-batch-drop-results.csv` gives:

- eight tested articles, seven with mapped geometry and mass;
- \(t_{180}=0.89308\) to \(1.06162\), range \(0.16854\);
- within-article per-drop CV range 0.169% to 0.482%;
- mass–\(t_{180}\) Pearson \(r=0.829\), two-sided \(p=0.0211\), approximate 95% Fisher CI 0.203 to 0.974;
- after omitting `6lhxfy`, \(r=0.190\), \(p=0.718\);
- \(t_{180}\)–rebound Spearman \(\rho=-0.393\), \(p=0.383\);
- nondominated articles `6lhxfy`, `6nheas`, and `bpx68c`.

These reproduce MS L1179–1203 and L1257–1263. The manuscript correctly states that this does not separate geometry effects from fabrication variation (MS L1187–1191), calls the mass association noncausal and confounded (MS L1197–1203), and says the trade-off is not statistically resolved (MS L1192–1197).

**Verdict: WITHSTANDS.** The seed data are described with suitable restraint.

---

### Probe D4: Is the stated simulation cross-metric result, \(\rho=-0.93\), exact \(p\approx0.0067\), statistically coherent?

**Referee:** For \(n=7\), Spearman coefficients occupy a discrete permutation distribution. Can \(\rho=-0.93\) have an exact two-sided permutation \(p\approx0.0067\)?

**Author, from the materials:** The manuscript and SI both state \(\rho=-0.93\), exact two-sided permutation \(p\approx0.0067\) (MS L1072–1079; SI L281–286). For seven untied ranks, the nearest attainable value is \(\rho=-0.928571\). Exhaustive enumeration of all \(7!=5040\) permutations gives a two-sided tail probability \(14/5040=0.00278\) when values at least as extreme in absolute magnitude are counted. Thus the quoted “exact” \(p\) is inconsistent with the standard exact permutation calculation. The underlying paired simulation scores were not supplied, so ties or a nonstandard test cannot be checked.

**Verdict: WOUNDED.** The association is properly called exploratory and in-sample, but its inferential number is wrong or undocumented.

**Concrete edit:** Either provide the seven paired values and the exact test implementation, or change MS L1075–1079 and SI L283–286 to:

> “Spearman \(\rho_s=-0.929\) across seven mapped articles; for seven untied ranks, the exact two-sided permutation \(p=0.0028\). Because this candidate metric was evaluated in-sample and selected without multiplicity adjustment, the association is hypothesis-generating and is not evidence of predictive validity.”

If ties explain the discrepancy, report the unrounded coefficient, tie structure, and permutation procedure instead.

---

### Probe D5: Is SAASBO justified, or is the model sophistication masking an unidentified seven-point fit?

**Referee:** Why use a fully Bayesian sparse-axis-aligned-subspace model with only seven observations in five design dimensions, then add mass as a sixth diagnostic input?

**Author, from the materials:** The paper says SAASBO was prespecified, chosen to marginalize hyperparameter uncertainty, and is not claimed to outperform a standard Gaussian process (MS L981–1013). It also states that seven observations for six correlated inputs cannot identify variable relevance and that the inverse-length-scale plots are prior-sensitive diagnostics only (MS L1290–1305). The leave-one-out results are weak, especially rebound: \(t_{180}\) MAPE 2.6%, \(r=0.70\); rebound MAPE 37.8%, \(r=-0.12\), with no independent test set (MS L1300–1308).

**Verdict: WITHSTANDS.** The model is defensible as a prespecified generator of candidates because its diagnostic limitations are disclosed. It is not yet evidence that SAASBO is the right model.

---

## Impact-mechanics referee

### Probe I1: Is \(t_{180}\) physically described without calling it transmissibility or proving cushioning?

**Referee:** You divide nonsimultaneous peak magnitudes from two different accelerometers. Why should this be interpreted mechanically?

**Author, from the materials:** The paper explicitly refuses the term transmissibility: “the two peaks need not be simultaneous” and a transient drop does not yield a frequency-response function (MS L844–851). It defines \(t_{180}\) only as a CFC-180 filtered peak-acceleration ratio and interprets values above/below one as peak amplification/attenuation under the tested condition (MS L844–854). The conclusion says only one tested article attenuated peak shock “under the tested condition” (MS L1494–1499).

**Verdict: WITHSTANDS.** This is careful and technically appropriate.

---

### Probe I2: Is the prior objective-stack disclosure faithful?

**Referee:** Did the Discussion fully disclose the three previously identified defects: unvalidated rebound physics, fragile trade-off, and understated article-level noise?

**Author, from the materials:** Yes. MS L1375–1392 states that the rebound fraction relies on an unvalidated ballistic interpretation, gives \(\rho=-0.39\), \(p=0.38\) for the fragile trade-off, and says per-drop standard errors understate the provisional 0.72% between-article CV. It then commits to article-level noise, candidate-constraint treatment of rebound, and replicate articles. This agrees with SI L214–227.

**Verdict: WITHSTANDS.** The disclosure is faithful and quantitatively consistent with the supplied campaign data.

---

### Probe I3: Why does the SI still call the second objective “rebound energy” after the main text proves it is not measured energy?

**Referee:** Your main text says \(E_{\mathrm{reb}}\) is “not a measured rebound energy” (MS L861–870), but SI L214–220 calls the objectives “the filtered peak-acceleration ratio and the rebound energy,” and the metal protocol repeatedly calls it rebound energy.

**Author, from the materials:** No satisfactory reconciliation is present. The equations give the quantity energy units, but the manuscript itself explains that a true restitution-energy relation would involve a squared velocity ratio and that \(\Delta v\) is not demonstrated incident relative velocity (MS L861–870).

**Verdict: WOUNDED.** The main analysis is honest, but terminology drifts back into a physical claim it has disavowed.

**Concrete edit:** Globally replace unqualified “rebound energy” with “provisional mass-weighted rebound score” until validation. In particular, change SI L218–220 to:

> “…the campaign responses are the filtered peak-acceleration ratio and a provisional mass-weighted rebound-timing score; quasi-static crush metrics are deferred…”

Change the Fig. 7 y-axis from “Rebound energy to payload” to “Provisional mass-weighted rebound score (mJ per drop).”

---

### Probe I4: Does the simulation ladder support any predictive claim?

**Referee:** Tier C omits twist, cannot reproduce \(t_{180}>1\), is insensitive to cable stiffness, and produces design-invariant restitution. Why present it as a ladder that “prioritizes candidates”?

**Author, from the materials:** The blind spots are explicitly listed in SI L272–287 and summarized in MS L1060–1091. The manuscript says simulation is “never” ground truth, calls the \(\rho=-0.93\) association exploratory and in-sample, reports only \(\rho\approx0.5\) for simulated \(t_{180}\), and keeps every surrogate observation physical.

**Verdict: WOUNDED.** The limitations are strong, but “prioritize candidates” at MS L1084 is broader than the evidence. A metric selected and evaluated on the same seven designs has no established prioritization value.

**Concrete edit:** Replace MS L1084–1087 with:

> “We therefore use the ladder for computational screening and post hoc mechanism hypotheses. Until the cross-metric association is tested prospectively, simulation does not determine acquisition values or candidate priority, and every surrogate observation remains physical.”

Also replace Contribution 4 (MS L293–297), “with its predictive reach … quantified,” with “with preliminary agreement and documented blind spots assessed against the seed round.”

---

### Probe I5: Can a synthetic impact trace appear in a Results-facing JMD manuscript?

**Referee:** Fig. 4 shows a 78% peak reduction, mechanism phases, and matched impulse using synthetic data. Even with a watermark, does it not visually teach an unobserved mechanism?

**Author, from the materials:** The caption labels it an “Illustrative example (synthetic data)” and says it is “to be regenerated from the campaign captures” (MS L918–935; manuscript p. 7). No campaign trace or synchronized structural event evidence supports the shown phase labels.

**Verdict: FAILS.** The disclaimer prevents data fabrication, but the figure still depicts an unobserved favorable mechanism and a rigid-control comparison absent from the reported campaign.

**Concrete edit:** Remove Fig. 4 now. If a conceptual processing schematic is necessary, use a signal-processing flowchart with no numerical traces, no “−78%,” and no inferred deformation phases. A later real-data version must use archived captures and label only events supported by synchronized measurements.

---

## Additive-manufacturing and materials referee

### Probe A1: Can another laboratory reproduce the prints from Table 3?

**Referee:** Where are nozzle temperatures, bed temperature, layer height, speeds, retraction, material manufacturers/grades, conditioning time, and slicer version/profile?

**Author, from the materials:** Table 3 contains `TBD` for both nozzle temperatures, bed temperature, and layer height (MS L744–771; manuscript p. 5). A TODO also asks for print speed, retraction, and interface-validation settings (MS L698–703). The paper provides printer, nozzle diameters, 15% grid/two walls for PLA, near-solid TPU, textured PEI, vertical orientation, manual supports, and ~8% relative humidity, but not enough to reproduce the build.

**Verdict: FAILS.** Unlike pending performance results, these are existing campaign metadata and must be recovered now.

**Concrete edit:** Replace every `TBD` with the exact archived slicer values and add filament manufacturer/product/color/lot where available, drying temperature and duration, line widths, wall count, infill pattern/density, print speeds, support-interface settings, and slicer/profile version. If a value was not logged, say “not recorded” and identify it as a limitation rather than guessing.

---

### Probe A2: Did the manuscript verify the as-built geometry being optimized?

**Referee:** You optimize continuous member diameters but attach commanded CAD geometry to the surrogate. Did you measure the printed diameters, ovality, tendon cross-section, twist, or height?

**Author, from the materials:** No. MS L620–637 says dimensional metrology “has not yet been performed,” that slicer line-width quantization coarsens the space, and that the surrogate uses commanded post-projection geometry. Only mass was measured for every mapped article.

**Verdict: WOUNDED.** The limitation is stated, but the phrase “five geometry variables” can still be read as five measured physical variables.

**Concrete edit:** Add after MS L633–637:

> “Accordingly, the present surrogate maps commanded CAD settings, not verified as-built dimensions, to article responses. Apparent geometric trends may therefore include slicer quantization and fabrication error.”

This remains **DATA-GATED** for correction: dimensional metrology is needed before interpreting geometric sensitivity.

---

### Probe A3: Is the claimed internal-anchor durability contribution supported?

**Referee:** Contribution 1 says the joint is “intended to improve cyclic interface durability” but pull-out and fatigue verification is pending (MS L265–276). The SI’s joint figure is itself a placeholder. What evidence supports the design claim?

**Author, from the materials:** The manuscript later says no joint failed during repeated-drop sessions but correctly notes these were not controlled fatigue tests and do not establish interface durability (MS L1430–1434). No pull-out or fatigue data are attached.

**Verdict: WOUNDED.** The caveat is present, but the contribution list foregrounds an unverified engineering advantage.

**Concrete edit:** Change MS L268–276 to:

> “…TPU tension elements anchored inside the PLA strut ends. This study reports the resulting printable joint geometry; pull-out strength, fatigue life, and any durability advantage over exposed interfaces remain untested.”

Replace SI Fig. S1’s placeholder with the existing five CAD renders before submission. This is fixable without new experimental data.

---

### Probe A4: Is the workflow figure faithful to what was done?

**Referee:** Fig. 3 says “Post-Processing & Pretensioning” and “Dynamic & Static Testing.” Yet the Introduction says “no pretension is activated or measured” (MS L209–212), and quasi-static testing is pending (MS L891–912). Which is true?

**Author, from the materials:** The text is clear that no pretension was activated or measured and that static testing is planned. The figure is inconsistent with the completed campaign.

**Verdict: FAILS.** This is a visual overclaim beyond the seed round.

**Concrete edit:** In Fig. 3 replace “Post-Processing & Pretensioning” with “Support Removal & Inspection.” Replace “Dynamic & Static Testing” with “Drop-Tower Testing,” or visually separate “completed in seed round” from “planned quasi-static testing” using dashed borders and an explicit legend. Remove “tension tuning.”

---

### Probe A5: Is the metal-analog protocol sufficiently specified to test transfer rather than mass and joint changes?

**Referee:** “Same \(R,H,\theta\), and member-diameter parameterization” is not a reproducible analog definition. What are aluminum alloy and temper, tube wall thickness, cable construction and diameter, joint hardware, pretension, anchor torque, total mass, payload mass, and replicate count? How will a much heavier metal article be compared under the “identical” drop protocol?

**Author, from the materials:** The protocol supplies hollow aluminum rods, stainless threaded cables, worst/mid/best predicted tiers, the same nominal geometric parameterization, and Spearman rank correlation on \(t_{180}\) (MS L1093–1125; SI L301–315). It acknowledges different deformation modes, joint compliance, friction, pretension behavior, and rate sensitivity (MS L1111–1116). It supplies none of the construction, mass-matching, replicate, or uncertainty details above.

**Verdict: FAILS.** The concept is good, but this is not yet a preregistered protocol capable of distinguishing geometric rank transfer from material-system and mass confounding.

**Concrete edit:** Replace “pre-registered metal-analog validation protocol” in Contribution 5 (MS L298–303) with “planned exploratory metal-analog comparison.” Add a protocol table specifying alloy/temper, tube outside and inside diameters, cable specification, joints, pretensioning procedure and measurement, article and payload masses, drop orientation, replication, exclusion rules, and analysis. Predefine what happens with ties and report \(\rho_s\) with an exact permutation interval/test. Change Table 4’s final clause from “agreement … indicates the optimization transfers” to “rank agreement would be preliminary evidence consistent with transfer; disagreement would not isolate which material or joint difference caused the change.”

---

## Cross-cutting referee probes

### Probe C1: Is the Background complete and accurately cited?

**Referee:** Does the literature review support its own claims, or has the working bibliography leaked into the paper?

**Author, from the materials:** The Background covers classical tensegrity, printed impact structures, rigid–soft additive manufacturing, Bayesian optimization, noisy multiobjective acquisition, and recent dynamic work. However:

1. MS L236–240 says Bayesian optimization drove “hyperparameter tuning of AlphaGo,” citing Silver et al. 2016. That paper is about deep neural networks and Monte Carlo tree search, not a BO application.
2. MS L462–467 claims FDM-specific “multimaterial interface adhesion (notably TPU bonded to rigid co-printed substrates)” is characterized by `caminero2019printingparameters`. The cited title is *Additive Manufacturing of PLA-Based Composites … Graphene Nanoplatelet Reinforcement* (`references.bib` L707–720), which does not support a PLA/TPU interface claim.
3. `ruwais2025mechanicalperformanceof`, cited at MS L455–458, has `journal = {Unknown journal, 2025}` and no DOI (`references.bib` L613–618).
4. The compiled bibliography contains visible corruption and typos, including “Johans” and “Daraoio” for Pajunen et al., “Rancy” for Raney, “ppj Computational Materials,” and malformed URLs on manuscript pp. 11–13.

**Verdict: FAILS.** The topical coverage is adequate; citation integrity and formatting are not.

**Concrete edits:**

- Delete the AlphaGo example or replace it with a verified BO application.
- Delete the Caminero interface-adhesion sentence unless a genuine TPU-to-rigid-substrate adhesion source is inserted.
- Verify and complete Ruwais or remove it.
- Normalize all cited BibTeX entries from primary metadata. At minimum fix `vespignani2018design` to `@inproceedings`; `garridomerchan2020…` to `@article`; `davami2019…` to `@article`; separate journal, volume, issue, pages, and date fields; remove literal `null` from `wang2025…`; and replace `and others` stubs for `wang2022…` and `lee2023…` with verified author lists.

---

### Probe C2: Are figures and captions publication-ready?

**Referee:** Do the figures communicate completed evidence without ambiguity?

**Author, from the materials:** Figs. 2, 6, and 7 are generally clear. Fig. 7 correctly shows all seven mapped points and the three-member Pareto set. However:

- Fig. 1 is a proposal-style overview with a small BO inset and a dark generic printer photograph; its source TODO says it is reproduced from a proposal (MS L317–329).
- Fig. 3 contains the pretension/static-testing overclaims above.
- Fig. 4 is synthetic.
- Fig. 5 and SI Fig. S2 are text-box placeholders.
- SI Fig. S1 is a text-box placeholder despite the text saying the five designs were already developed.
- Fig. 6 has no design IDs or visible scale bar, limiting its use as evidence.
- Fig. 8’s source caption says “share of model sensitivity,” which risks overstating normalized inverse length scales despite the caveat.
- The compiled PDF includes an unintended final “List of Figures/List of Tables” page, where placeholders are exposed again (manuscript p. 14).

**Verdict: FAILS.** The central quantitative figures are usable, but the figure set as a whole is not submission-ready.

**Concrete edits:** Remove Fig. 4; correct Fig. 3; replace available SI joint art; label Fig. 6 by spec ID and add dimensions/scale; rename Fig. 8’s x-axis “normalized inverse length scale”; remove all empty placeholder floats from the review PDF; and remove `\listoftodos`/the unintended lists from the clean build.

---

### Probe C3: Is the SI/main-text split sensible?

**Referee:** Does the SI hold reproducibility detail while the main paper holds the scientific argument?

**Author, from the materials:** Broadly yes: the main paper defines objectives and campaign logic, while the SI carries print IDs, defects, calibration, filter correction, mass-model details, simulation blind spots, and development history. But the SI repeatedly defers exact exclusion rules, event windows, filter initialization, and “stabilized mean” to unreleased code (SI L185–200). It also relies on mutable GitHub pull requests and issues rather than an immutable archive.

**Verdict: WOUNDED.** The division is conceptually sound, but essential operational definitions cannot live only in future code.

**Concrete edit:** Add an SI table listing all analysis parameters: contact window, peak window, baseline interval, second-contact threshold/window, warm-up and exclusion rules, stabilization rule, filter implementation and boundary handling, and software entry point. Keep code as the executable record, not the sole definition.

---

### Probe C4: Are reproducibility and archival statements adequate?

**Referee:** Can a referee reproduce Tables 5 and Figs. 7–9 today?

**Author, from the materials:** No. The manuscript accurately calls archival release “a declared submission gate rather than a solved item” (MS L1041–1055), and the SI repeats that a version-tagged code release is required (SI L194–200). The supplied files do not include raw captures, processing code, exact model state, the leave-one-out CSV cited at MS L1308–1311, or the actual printed round-2 recommendation set.

**Verdict: WOUNDED.** The draft is honest, but not reproducible yet.

**Concrete edit:** Before submission, deposit an immutable release containing raw or losslessly processed capture records, article-to-design mapping, both recommendation sets, Ax experiment state, random seeds, model configuration and posterior diagnostics, figure scripts, environment lock file, and a single command/workflow reproducing every reported table and plot. Insert the DOI and release tag at MS L1052–1055.

---

### Probe C5: Are all placeholders honest?

**Referee:** Do any placeholder elements imply completed evidence?

**Author, from the materials:** The abstract, Results, Discussion, and Conclusion consistently declare round 2, baseline, quasi-static, replication, and metal-analog outcomes pending. Those absences should not be treated as defects in this mid-flight review. Two places nevertheless overstep:

- Fig. 3 visually presents pretensioning and static testing as workflow stages without marking them pending.
- The metal section says Table 4 “reports” and Fig. 5 “shows” the comparison/specimens (MS L1123–1125), although both are empty placeholders.

**Verdict: WOUNDED.** The prose-level campaign status is honest, but those present-tense visual references are not.

**Concrete edit:** Change MS L1123–1125 to:

> “The planned reporting format is specified in Table 4. The table and specimen photographs will be added after fabrication and testing.”

For a circulation draft, retain placeholders only under a front-page “WORKING DRAFT: PENDING DATA” banner. For journal submission, remove all empty placeholder floats and insert them only when data exist.

## Associate Editor synthesis

**Associate Editor:** The paper has a credible design-research core: a physical seed campaign, carefully defined peak-ratio metric, transparent small-sample caveats, fully Bayesian candidate generation, and unusually candid disclosure of an objective-stack failure. The campaign statistics in Table 5 and the observed Pareto set reproduce from the supplied CSV. The central weakness is not that round 2 is pending; that was stipulated and is honestly stated. The weakness is that the draft mixes three states of evidence: completed seed measurements, auditable but unreleased computational records, and visual/protocol placeholders. A JMD referee should not have to infer which round-2 CSV corresponds to the hardware, overlook a wrong exact permutation \(p\), or reconcile “no pretension” with a figure that says “pretensioning.” The bibliography also contains at least two substantive miscitations and extensive malformed metadata.

**Panel recommendation: MAJOR REVISION, not yet submission-ready.** The seed-round scientific claims largely withstand review. The manuscript package does not yet withstand a reproducibility, citation-integrity, or figure-honesty review.

# Priority-ordered revision list

## MUST-FIX-NOW

1. **Resolve round-2 recommendation provenance.** Identify and archive the exact nine designs on the printer; distinguish them from the regenerated constant-printed-mass set; regenerate Fig. 7 from the correctly named set.
2. **Correct the \(n=7\), \(\rho=-0.93\) exact permutation result.** Supply paired values and code; absent ties, report \(\rho_s=-0.9286\), exact two-sided \(p=0.0028\).
3. **Remove the synthetic Fig. 4.** Do not show unobserved attenuation or deformation phases as a data-like plot.
4. **Correct Fig. 3.** Remove “Pretensioning,” “tension tuning,” and unqualified completed static testing.
5. **Recover all print parameters now.** Replace Table 3’s `TBD`s; add material, conditioning, slicer, speed, line-width, and support details. State “not recorded” where recovery fails.
6. **Use “provisional mass-weighted rebound score” consistently.** Change Fig. 7’s y-axis and all SI/metal passages that call it measured rebound energy.
7. **Repair citation integrity.** Remove the AlphaGo-as-BO claim; remove or replace the Caminero PLA/TPU-interface miscitation; verify/remove the unknown-journal Ruwais item; rebuild cited BibTeX metadata from primary records.
8. **Replace or remove non-data placeholders in the review build.** SI Fig. S1 can be replaced now from existing CAD work. Remove empty metal floats until data arrive or watermark the entire circulation draft.
9. **Specify the metal study as a planned exploratory comparison, not a preregistered validation.** Add materials, joints, pretension, mass, replication, exclusions, and exact rank-analysis rules.
10. **Make operational signal-processing definitions explicit in the SI.** Do not defer all thresholds and windows solely to future code.
11. **Fix front/back matter.** Correct author contribution footnotes, remove the date-bearing corresponding-author footnote if not required, eliminate line-number glitches and the unintended list-of-figures/tables page, and complete funding identifiers.
12. **Tighten simulation wording.** Replace “predictive reach quantified” and “prioritize candidates” with language limited to exploratory in-sample association and mechanism hypotheses.

## DATA-GATED

1. Round-2 predicted-versus-measured performance and closure of one physical BO cycle.
2. Budget-matched baseline and SAASBO-versus-standard-GP calibration comparison.
3. Replicate-article response data sufficient to estimate geometry-level and article-level variation.
4. Video validation of the rebound interpretation and decision on whether it becomes a constraint.
5. Quasi-static Instron metrics, including specific energy absorption and compaction efficiency.
6. Metal/polymer rank comparison after a reproducible metal protocol is fixed.
7. As-built dimensional metrology before interpreting commanded-variable sensitivities as physical geometry effects.
8. Pull-out/fatigue testing before claiming improved joint durability.

# Distance from a JMD major-revision-toward-accept

The draft is one full experimental round and one disciplined manuscript-cleanup pass away from being a credible **Major Revision** case, not close to acceptance in its current form. The completed seed evidence is stronger than the paper’s unfinished appearance suggests: its principal numerical claims reproduce, the limitations are mostly candid, and the objective-stack disclosure is faithful. But JMD cannot evaluate optimization effectiveness until round-2 measurements and a budget-matched comparison exist, and the current package has preventable blockers unrelated to new data: ambiguous recommendation provenance, a wrong “exact” \(p\)-value, synthetic and contradictory figures, unrecovered print settings, an underspecified metal protocol, unreleased analysis records, and damaged citation metadata. Fixing those now would turn this from a visibly mid-construction draft into a rigorous mid-campaign manuscript. The later data would then decide whether it advances toward acceptance.

## Discretionary analytical decisions

- Treated the stipulated absence of round-2, baseline, quasi-static, and metal outcomes as campaign status rather than defects; flagged only overclaims and protocol deficiencies around them.
- Used exhaustive permutation enumeration for the \(n=7\) Spearman check, with a two-sided absolute-correlation tail including equally extreme permutations.
- Recomputed rebound-score values from the CSV using \(g=9.80665\,\mathrm{m/s^2}\) and \(h=1.524\,\mathrm{m}\).
- Used Pearson correlation and a Fisher-transformation confidence interval to audit the manuscript’s stated mass association, matching the manuscript’s chosen analysis.
- Evaluated Pareto membership as strict nondominance under minimization of both reported objectives.
- Classified a point as FAILS when the supplied record could not establish provenance or support the stated claim; used WOUNDED when the evidence existed but wording, terminology, or documentation required correction.