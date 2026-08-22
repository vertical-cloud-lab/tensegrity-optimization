# Iteration 4: hostile statistics review

## Referee Q1: What, exactly, does the seed round establish when there is one mechanically tested article per mapped geometry?

**Answer:** It establishes descriptive separation among the tested articles and closes one physical Bayesian-optimization loop. It does not yet identify a population-level geometry effect or reproducibility for newly printed articles.

The manuscript reports eight tested articles, but only seven have both mapped geometry and both objectives: “eight articles (six mapped Sobol designs, the reference prism, and one article pending a design mapping)” (manuscript-body.tex, lines 1163–1166). The limitations correctly state “single prints of each design ($n=1$ article per geometry, with one triplicate)” (lines 1426–1428). The campaign CSV confirms eight tested rows, seven mapped rows, and only one tested article for each mapped geometry.

The observed $t_{180}$ range is correct:

- Minimum: 0.89308, article 6lhxfy.
- Maximum: 1.06162, article bag26v.
- Absolute range: 0.16854, reported as 0.169.
- Relative spread: 18.87% relative to the minimum, 15.88% relative to the maximum, or 16.79% relative to the sample mean.

Thus “19% relative to the minimum” (lines 1174–1175) is numerically correct. If the intended claim is the “17 percent spread” mentioned in the review prompt, that corresponds to normalization by the sample mean and must be labeled as such.

The problem is the phrase **“design-driven range”** (lines 1174 and 1338). With one tested article per geometry, geometry is inseparable from article-to-article fabrication variation, defects, plate, and the mid-batch nozzle change. The range is plainly much larger than the reported within-session drop scatter, but it cannot yet be partitioned into design and fabrication components.

**Verdict: WOUNDED.**

**Concrete edits:**

1. Replace lines 1174–1176:
   > “The design-driven range of 0.169 in $t_{180}$ (19% relative to the minimum) dwarfs the 0.17 to 0.48% within-specimen repeatability.”

   with:
   > “Across these eight tested articles, $t_{180}$ spans 0.169 (18.9% of the observed minimum). This between-article range exceeds the 0.17–0.48% within-session, per-drop CV, but one mechanically tested article per geometry does not permit separation of geometry effects from print-to-print variation or other fabrication covariates.”

2. Replace lines 1338–1339:
   > “The objectives discriminate: a 0.169 design-driven range in $t_{180}$ against sub-percent repeatability is a usable signal.”

   with:
   > “The measurement distinguishes the tested articles: their $t_{180}$ means span 0.169, well beyond within-session drop scatter. Whether this separation reproduces across newly printed articles remains to be tested.”

3. Replace the conclusion’s “spanned 0.89 to 1.06 against sub-percent repeatability” (lines 1455–1457) with:
   > “spanned 0.89–1.06 across the eight tested articles, while within-session per-drop CVs were below 0.5%; article-level reproducibility remains under study.”

---

## Referee Q2: Is the claim that one design “clearly attenuated” statistically licensed?

**Answer:** It is clear for the measured article and session, not yet for fresh prints of that geometry.

Article 6lhxfy has $t_{180}=0.89308$ with per-drop SD 0.00416 across 101 drops. Its mean lies far below unity even if the provisional 0.72% article-level CV is used as a noise scale. A rough interval using that scale is 0.880–0.906. This supports attenuation of the tested article under this protocol.

But the manuscript’s own limitation is decisive: one mechanically tested article represents this geometry. The abstract says “one clearly attenuated it” (lines 154–156), the Results call it “a single design” (lines 1172–1174), and the conclusion says “one design crossed into genuine attenuation” (lines 1455–1457). “Design” and “genuine” imply replication that has not occurred.

**Verdict: WOUNDED.**

**Concrete edit throughout:** Replace “one design clearly/genuinely attenuated” with:
> “one tested article had a mean $t_{180}$ of 0.893, indicating peak attenuation under the tested condition; replication is needed to establish the geometry-level response.”

The five articles with means above unity and two near/below unity are correct descriptive counts. Keep those counts, but identify them as **tested articles**, not stable design properties.

---

## Referee Q3: Does $r=0.83$, $p=0.02$, $n=7$ establish a strong mass relationship?

**Answer:** It establishes a large but fragile sample association. The reported calculation is correct.

From the seven mapped rows in `t3-prism-bo-batch-drop-results.csv`, Pearson $r=0.8291$, two-sided $p=0.0211$. A Fisher-transform 95% confidence interval is approximately 0.20–0.97. More damagingly, deleting 6lhxfy changes the correlation from 0.83 to 0.19; deleting any other article leaves it between 0.82 and 0.90. The apparent association is therefore dominated by the lightest, best-attenuating article.

Pearson inference also assumes independent observations from an approximately bivariate-normal population. Here the points are a fixed Sobol design sample plus a reference geometry, with mass induced by geometry. The nominal $p$-value is descriptive rather than a clean population test, and no causal interpretation is available. The Results do acknowledge the latter: “an observational association confounded with the design coordinates, not a causal mass effect” (lines 1182–1184).

**Verdict: WOUNDED.** The numeric claim survives, but “strongly” and the unqualified $p$-value convey more stability than seven structured points support.

**Concrete edits:**

- Replace lines 1181–1184 with:
  > “Among the seven mapped articles, printed mass and $t_{180}$ showed a large sample correlation ($r=0.83$, nominal two-sided $p=0.021$; approximate 95% CI 0.20–0.97). The association is confounded with the design coordinates and is highly sensitive to the lightest article ($r=0.19$ when 6lhxfy is omitted); it is not evidence of a causal mass effect.”

- At line 1013, replace “($r=0.83$ against $t_{180}$ across the mapped articles)” with “($r=0.83$, $n=7$, dominated by the lightest article, against $t_{180}$).”

---

## Referee Q4: Is the mass-confound argument coherent, or is it an excuse not to adjust?

**Answer, steelman:** The manuscript has a defensible estimand argument. Printed mass is partly generated by the geometry: partial-infill PLA struts and near-solid TPU tendons cause geometry-dependent printed mass (Supplementary, lines 232–241). If the scientific question is the **total performance of a fabricated geometry under the stated solid-CAD-mass projection**, conditioning on printed mass could remove a mediated part of that total effect. The data also show severe collinearity: mass correlates with strut diameter at $r=-0.91$, twist at $r=-0.84$, and cable diameter at $r=0.78$. At $n=7$, a model with five geometry variables plus mass cannot identify separate effects. Refusing to present a “mass-adjusted geometry effect” is statistically responsible.

**Answer, attack:** The current prose overstates what follows. It says “regressing mass out at $n=8$ would delete the very signal the campaign seeks” (lines 1373–1376). First, the relevant dataset is $n=7$, not 8: amdjwm has neither mass nor mapped geometry. Second, adjustment would target a different estimand, not necessarily “delete” legitimate signal. Third, because printed mass may directly affect impact dynamics, omitting it does not resolve the confound. The seed round simply cannot distinguish geometry-mediated mass effects, direct mass effects, and geometry effects independent of mass. Calling the rebound score “mass-aware” also does not deconfound $t_{180}$.

The later constant-printed-mass projection is the right experimental remedy, but it changes the feasible design comparison and should be described as an identification strategy rather than as validation of the round-1 compromise.

**Verdict: FAILS as currently phrased; answerable by changing the claim, not by fitting another regression.**

**Concrete replacement for lines 1369–1379:**
> “Holding solid CAD mass constant did not hold printed mass constant: the seed batch spans 18.50–22.29 g, and among the seven mapped tested articles mass and $t_{180}$ are correlated ($r=0.83$). Printed mass is itself induced by the geometry and is strongly collinear with member dimensions, so these seven observations cannot identify separate geometry and mass effects; a post hoc mass-adjusted regression would be unstable and would estimate a different, direct-effect quantity. We therefore report mass as a confounded tracking variable rather than attributing the association to mass or geometry. Later rounds use the calibrated printed-mass projection to compare geometries at approximately fixed printed mass.”

Also change “at $n=8$” to “among the seven mapped tested articles” everywhere.

---

## Referee Q5: Can the paper call the two objectives a genuine trade-off when $ho=-0.39$, $p=0.38$?

**Answer:** No. It can call the observed Pareto set nondegenerate and describe an apparent sample pattern. It cannot say that the objectives “genuinely trade off.”

From the seven mapped articles, Spearman $\rho=-0.3929$; the asymptotic two-sided $p=0.383$, and the exact permutation $p=0.396$. If 6lhxfy, the strongest attenuator, is removed, $\rho$ becomes $-0.029$. This is exactly the fragility disclosed in the Discussion: “driven substantially by the single strongest attenuator” (lines 1356–1358).

The current attached source has already converged substantially. Methods says “apparent trade-off” and “not statistically resolved” (lines 956–960); Results repeats that qualification (lines 1176–1180); Discussion does likewise. The phrase supplied in the prompt, “the two genuinely trade off in the measured seed round,” does **not** occur in the attached `.tex` or compiled PDF. If it survives in another branch, it conflicts directly with the reported statistic and must be removed.

“Observed front is nondegenerate” is a deterministic Pareto statement, not evidence of a population trade-off. Three points are nondominated because neither observed objective uniformly orders all seven points. That wording is valid if kept separate from inferential language.

**Verdict: WITHSTANDS in the attached version; FAILS in any version retaining “genuinely trade off.”**

**Concrete replacement wherever needed:**
> “The seven mapped articles form a nondegenerate observed Pareto set, but they do not establish a reproducible objective trade-off ($\rho=-0.39$, exact two-sided $p=0.396$); the apparent pattern is largely attributable to the strongest attenuator.”

I would also replace “at what rebound cost” in Discussion line 1345 with “whether attenuation reproducibly incurs a rebound-score cost.”

---

## Referee Q6: Are the within-specimen CVs being passed off as design or article-level certainty?

**Answer:** In several prominent sentences, yes.

The reported within-session values are correctly computed from the CSV: $t_{180}$ per-drop CVs range from 0.169% to 0.482%, rounded to 0.17–0.48%. These quantify scatter among repeated drops of the **same article in one session**. They do not quantify print-to-print variability, geometry-level uncertainty, or independent replication. Drops may also be serially dependent because the same article and rig are repeatedly impacted, so $s/\sqrt{101}$ is not automatically a valid independent-sampling standard error.

The text later acknowledges the estimand mismatch clearly: the current noise model concerns “the response of the tested article, not of a freshly printed article at the same design” (lines 997–1003). The Discussion also reports a 0.72% between-article CV from a five-print study (lines 1359–1361). This is faithful to the prior review. Numerically, 0.72% is 15.0–42.7 times the seed sessions’ per-drop SEM CVs, consistent with the manuscript’s rounded “14 to 44 times.”

However, “the design-driven range ... dwarfs ... within-specimen repeatability,” “usable signal,” and the conclusion’s “against sub-percent repeatability” invite the wrong comparison. They use conditional, repeated-drop precision to imply geometry-level certainty.

**Verdict: WOUNDED.**

**Concrete edits:** Use “within-session per-drop CV” every time, never bare “repeatability.” Add after lines 880–882:
> “These values describe repeated drops of the same physical article and do not estimate print-to-print or geometry-level repeatability; serial dependence among drops may also make $s/\sqrt{n_{\mathrm{drops}}}$ optimistic.”

In Table 5’s caption, “means $\pm$ one standard deviation over stabilized drops” is already correct and should remain.

---

## Referee Q7: Does the 0.13% cross-session reproduction establish reproducibility?

**Answer:** No. It is one paired anecdote, not an estimate of a reproducibility distribution.

The manuscript says “the one article re-tested in a separate session reproduced its mean to 0.13%” (lines 880–882). That is transparent about the sample count, but “reproduced” can still be read as a general property. Neither the provided campaign summary CSV nor print-key CSV contains the two session-level records needed to verify the 0.13% calculation.

**Verdict: WOUNDED.**

**Concrete edit:**
> “For the single article measured in two sessions, the two session means differed by 0.13%; this isolated re-test does not estimate cross-session reproducibility.”

Add the two session means or a linked session-level table to the Supplementary Information. Until then, the number is traceable only to manuscript assertion, not the attached campaign CSVs.

---

## Referee Q8: Is the 0.72% article-level CV itself precise enough to be called a noise floor?

**Answer:** No. It is the best available scale estimate, but it is uncertain because it comes from five prints.

The manuscript faithfully discloses the prior review’s result: “0.72% between-article CV measured in a five-print repeatability study” (lines 1359–1361), and the Supplementary repeats the planned correction (lines 220–226). Under an idealized normal model, a five-article estimate of 0.72% would have a very wide approximate 95% interval for the underlying CV/SD scale, about 0.43–2.07%. This interval is only illustrative because the raw five-print responses were not included among the attached CSVs and the normal/constant-mean assumptions cannot be checked.

Calling 0.72% a fixed “noise floor” at lines 1001–1003 overstates its precision. It is also unclear whether those five prints match the seed fabrication process, nozzle regime, and geometry distribution.

**Verdict: WOUNDED.**

**Concrete edits:**

- Replace “an article-level noise floor near 0.7% CV” with “a provisional article-level noise scale of 0.72% CV, estimated from five prints.”
- Replace “understate article-level uncertainty by roughly an order of magnitude” with “are substantially smaller than the provisional 0.72% between-article CV estimate.”
- Add the five article responses, design identity, fabrication conditions, and CV definition to the Supplementary data. Without those data, the disclosure is faithful but not independently auditable from the attachments.

---

## Referee Q9: Are the feature importances scientifically interpretable at $n=7$ with six inputs?

**Answer:** Only as model diagnostics conditional on a strong prior, not as evidence that height or radius matters physically.

The manuscript mostly gets this right. It says the sparsity prior “has not identified a dominant subspace,” that no input separates decisively from the equal-share line, and that the diagnostics are not “evidence for or against variable relevance” (lines 1271–1294). Figure 8 reports posterior medians and interquartile ranges over Markov-chain Monte Carlo draws. Those intervals reflect uncertainty under the fitted model and prior; they are not frequentist confidence intervals and do not overcome the fact that six inputs are being diagnosed from seven observations. Printed mass is additionally collinear with several geometry variables.

The residual overclaim is “with cell height leading for $t_{180}$ and base radius for rebound energy” (lines 1277–1279). Readers will retain the ranking and forget the disclaimer.

**Verdict: WOUNDED, narrowly.**

**Concrete edit:** Delete the clause naming the leaders. Replace the paragraph’s first sentence with:
> “At seven observations for six correlated inputs, the normalized inverse length scales are prior-sensitive model diagnostics only; none supports a claim of variable relevance or ranking.”

Change Figure 8’s axis annotation from “Share of model sensitivity” to “Normalized inverse-length-scale diagnostic.” “Sensitivity” implies a more stable physical interpretation than the calculation supplies.

---

## Referee Q10: Do the LOOCV numbers demonstrate predictive skill?

**Answer:** No. They are descriptive diagnostics from seven dependent folds.

The reported values are MAPE 2.6% and $r=0.70$ for $t_{180}$, and MAPE 37.8% and $r=-0.12$ for rebound (lines 1280–1285). For orientation only, treating the seven pairs as independent gives an approximate 95% CI of $-0.11$ to 0.95 for $r=0.70$ and $-0.80$ to 0.70 for $r=-0.12$; nominal two-sided $p$-values are 0.080 and 0.798. In leave-one-out cross-validation, however, predictions arise from highly overlapping training sets, so ordinary correlation inference is not formally valid.

MAPE is also unstable as a generalization estimate at $n=7$. One held-out article changes the average by one seventh, and no uncertainty interval is reported. The manuscript correctly says $t_{180}$ correlation is imprecise and rebound gives no evidence of skill. But “Cross-validation tells the same two-sided story” and the figure’s prominent decimals still invite performance interpretation.

One consistency issue must be fixed: the compiled figure shown in the PDF labels rebound as $r=0.12$, while manuscript text and the supplied figure image report $r=-0.12$. The text/source claim is negative. Regenerate the compiled figure so the sign agrees.

**Verdict: WOUNDED.**

**Concrete edit:**
> “Seven-fold leave-one-out diagnostics yielded MAPE 2.6% and $r=0.70$ for $t_{180}$ and MAPE 37.8% and $r=-0.12$ for rebound. Because the seven folds share nearly all training observations and no independent test set exists, these values are descriptive and do not establish out-of-sample skill.”

Round MAPE to 3% and 38%, or retain decimals only in a table. The current figure’s “read the direction, not the decimals” is good, but the text should carry the same warning.

---

## Referee Q11: Does $\rho=-0.93$ at $n=7$ justify calling the Tier-C score a strong predictor?

**Answer:** It supports a strong in-sample rank association, not demonstrated prediction.

The manuscript and Supplementary both report Spearman $\rho=-0.93$ across seven mapped articles (main text lines 1065–1071; Supplementary lines 279–282). For $n=7$, the exact two-sided permutation $p$ for $|\rho|\ge0.93$ is approximately 0.0067. Thus the observed rank alignment is unusually strong under a no-association permutation null.

But the score is described as the “strongest cross-metric predictor,” which suggests metric selection among multiple candidates and predictive validation. The attachments do not enumerate all candidate metrics or provide a multiplicity correction, and the same seven articles appear to have been used to identify and evaluate the score. Small $n$ also makes the effect sensitive to individual ranks.

**Verdict: WOUNDED.**

**Concrete edit:** Replace “a strong cross-metric predictor” and “the strongest cross-metric predictor” with:
> “showed a strong exploratory in-sample rank association with measured $t_{180}$ ($\rho=-0.93$, $n=7$, exact two-sided permutation $p\approx0.0067$). Because the metric was evaluated on the seed set and candidate-metric selection was not multiplicity-adjusted, this is hypothesis-generating rather than validated predictive performance.”

The manuscript already says simulation is for screening and not ground truth, which helps.

---

## Referee Q12: Are the print-to-print mass and mass-model precision claims adequately supported?

**Answer:** The descriptive SD is supported, but the general precision claim is too strong.

Three prints of design 08 weigh 22.29, 21.42, and 22.10 g in the print-key CSV. Their sample SD is 0.457 g, matching Supplementary lines 101–104. But this is one geometry, three prints, visibly different defects, and an unresolved official-article assignment. It is not a general process repeatability estimate.

The Supplementary says the mass model residual SD is 0.378 g, “at or below the measured 0.457 g print-to-print scatter, so it is as accurate as the process is repeatable” (lines 242–244). Comparing two uncertain SD estimates, one from only three prints, does not support that conclusion.

**Verdict: WOUNDED.**

**Concrete edit:**
> “The calibrated model has a residual SD of 0.378 g. For context, the three available prints of design 08 have a sample SD of 0.457 g; three prints of one geometry are insufficient to establish a general process repeatability limit.”

Also clarify in the main limitations that the design-08 triplicate provides mass replication, but only one of those articles appears in the reported mechanical-response table. Otherwise “with one triplicate” can be misread as three replicated drop sessions.

---

# Minimal edit set, ranked by importance

1. **Fix the mass-confound paragraph.** Change $n=8$ to seven mapped articles and replace “regressing mass out would delete signal” with the non-identifiability/alternative-estimand wording above.
2. **Stop comparing geometry-level evidence to within-session CV.** Replace every bare “repeatability” with “within-session per-drop CV” and state that one article per geometry prevents separation of design and print effects.
3. **Converge all trade-off language.** Use “nondegenerate observed Pareto set” plus “apparent, unresolved trade-off”; delete “genuinely trade off” from any other branch and soften “at what rebound cost.”
4. **Qualify the mass correlation.** Add $n=7$, approximate CI 0.20–0.97, and the leave-6lhxfy-out result $r=0.19$.
5. **Demote 0.72% from a fixed floor to a provisional five-print scale estimate.** Supply the raw five-print data and fabrication conditions.
6. **Make attenuation article-specific.** Say that 6lhxfy attenuated under the tested condition; do not yet call attenuation an established geometry property.
7. **Label feature importances as prior-sensitive model diagnostics.** Remove the named “leading” variables and avoid “share of sensitivity.”
8. **Describe LOOCV as descriptive only.** State that overlapping folds preclude ordinary independent-pair inference; fix the rebound-correlation sign inconsistency in the compiled figure.
9. **Rename the Tier-C result an exploratory in-sample rank association.** Add exact permutation $p\approx0.0067$ and disclose metric-selection/multiplicity limitations.
10. **Qualify the repeatability anecdotes.** State that 0.13% is one article measured in two sessions and that the 0.457 g SD is three prints of one design.

# Bottom-line referee judgment

The manuscript is unusually candid for a mid-flight campaign, and the trade-off, rebound-validity, and per-drop-versus-article-noise disclosures are substantively faithful to the prior adversarial review. The main remaining statistical defect is not a wrong calculation. It is **estimand slippage**: within-session precision is repeatedly placed next to between-design language, causing one tested article per geometry to read like replicated geometry evidence. The mass paragraph then claims more causal clarity than the seed design can provide.

With the ranked edits above, the seed-round claims can survive a hostile statistics review as descriptive, exploratory evidence. Without them, the manuscript overstates design-level certainty despite its correct small-$n$ caveats.

## Discretionary analytical decisions

- Used exact two-sided permutation inference for the $n=7$ Spearman correlations rather than relying only on the asymptotic approximation.
- Used Fisher-transform intervals for Pearson correlations as approximate small-sample uncertainty summaries; these rely on independence and approximate bivariate normality, which are doubtful for a structured Sobol sample.
- Assessed influence through leave-one-article-out correlations because formal robust-regression modeling is not identifiable or stable with seven observations and strongly collinear predictors.
- Treated the 0.72% article-level CV as a provisional external scale estimate because the underlying five-print raw data were not among the attached campaign CSVs.
- Used a normal-theory chi-square interval only to illustrate the uncertainty of a five-article SD/CV estimate, not as a validated interval for the unavailable repeatability dataset.
- Interpreted “spread” as requiring an explicit denominator; retained 18.9% relative to the minimum because that is the denominator currently stated in the manuscript.