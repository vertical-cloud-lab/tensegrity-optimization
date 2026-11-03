# Follow-up adversarial review of round-2 results

**Review date:** 2026-08-25  
**Decision for the 8/25 presentation:** Show that round 2 produced an empirical extension of the measured two-metric set, especially `r2d2c6` at 4.07 mJ, but do not call this a replicated or validated engineering Pareto improvement. The frozen model failed calibration in opposite directions on both outputs. The data establish model misspecification; they do not identify reprojection stiffness as its cause.  
**Decision for round 3:** Do not print the nine proposed articles as a Bayesian-optimization batch. Refit on as-printed geometry, use `t180` as the sole objective with article-level noise, and spend nine print slots on three independently printed articles at each of three geometries: `6lhxfy`, `r2d2c6`, and one newly regenerated design. Re-seat and re-test `r2d2c3` before it enters the fit.

## What changes what you present and print

1. **Correct “8 of 9 rebound values were at or below prediction” to “9 of 9.”** All nine `t180` residuals were positive and all nine rebound-energy residuals were negative. Both sign tests give exact two-sided $p=0.0039$. This is not calibrated uncertainty centered on reality.
2. **Do not present reprojection stiffness as the explanation.** It is a plausible hypothesis, not an identified mechanism. The premise that all articles were 20–30% smaller is not reproduced: seven of nine were shrunk, two were expanded, and only one had scale 0.70–0.80. Round-2 mean scale was 0.865 versus 0.897 in round 1, an unremarkable 3.1 percentage-point difference (exact permutation $p=0.557$). More shrink did not significantly predict larger `t180` error ($r=0.382$, $p=0.310$).
3. **Replace “the uncertainty bands did their job” with an objective-specific calibration statement.** Rebound had 9/9 coverage at nominal 95%, but all observations were on the same side and the bands were very wide. `t180` had only 5/9 coverage at 95% and 1/9 at 68%. Posterior standard deviations of a noise-free mean are not full predictive intervals for a newly printed article.
4. **Keep `e_rebound` as a diagnostic, not a BO objective.** Round 2 materially improves detector-stability evidence, but not event identity or payload relevance. The delayed-event metric may become a constraint after synchronized video and a response-amplitude criterion validate what is being constrained.
5. **Do not use the present round-3 suggestions as evidence for a low-twist optimum.** Eight of nine are at 40° twist and seven of nine at 5.5 mm cables; two also fail stated print constraints. This is another boundary-heavy batch from the same bad likelihood and an altered representation.

# A. Calibration audit

## A1. Recomputed prediction errors

I joined `round2-frozen-predictions.csv` to `round2-print-key.csv` by trial and then to `round2-measured-drop-results.csv` by print ID. I independently reconstructed energy as

$$E_{reb}=e_{rebound}mgh,$$

using $g=9.80665\ \mathrm{m/s^2}$ and $h=1.524\ \mathrm{m}$. The largest discrepancy from `objectives-mass-normalized.csv` was 0.0049 mJ, attributable to rounding. Standardized residuals below use the requested frozen posterior standard deviation of the latent, noise-free mean:

$$z_i=\frac{y_i-\hat\mu_i}{\hat\sigma_i}.$$

| Article | `t180` measured | predicted ± SD | residual | z | rebound measured (mJ) | predicted ± SD (mJ) | residual (mJ) | z |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `r2d2c1` | 0.994 | 0.948 ± 0.046 | +0.046 | +1.00 | 5.97 | 8.31 ± 3.18 | −2.34 | −0.74 |
| `r2d2c2` | 1.041 | 0.926 ± 0.095 | +0.115 | +1.22 | 5.62 | 9.90 ± 5.03 | −4.27 | −0.85 |
| `r2d2c3` | 1.334 | 0.910 ± 0.073 | +0.423 | +5.82 | 5.59 | 10.09 ± 5.20 | −4.50 | −0.87 |
| `r2d2c4` | 1.185 | 0.885 ± 0.075 | +0.300 | +4.00 | 6.44 | 12.25 ± 5.73 | −5.80 | −1.01 |
| `r2d2c5` | 1.152 | 0.987 ± 0.066 | +0.165 | +2.48 | 6.71 | 8.37 ± 4.34 | −1.67 | −0.38 |
| `r2d2c6` | 1.055 | 0.953 ± 0.094 | +0.102 | +1.08 | 4.07 | 8.98 ± 5.58 | −4.91 | −0.88 |
| `r2d2c7` | 0.948 | 0.905 ± 0.091 | +0.043 | +0.47 | 12.17 | 13.02 ± 5.11 | −0.86 | −0.17 |
| `r2d2c8` | 1.070 | 0.955 ± 0.071 | +0.116 | +1.63 | 7.89 | 9.97 ± 5.34 | −2.08 | −0.39 |
| `r2d2c9` | 1.053 | 0.873 ± 0.053 | +0.180 | +3.43 | 5.84 | 11.31 ± 4.29 | −5.47 | −1.27 |

### Batch diagnostics

| Diagnostic | `t180` | rebound energy |
|---|---:|---:|
| Mean residual | +0.166 | −3.54 mJ |
| Mean standardized residual | +2.35 | −0.729 |
| SD of standardized residuals | 1.76 | 0.351 |
| Nominal 68% coverage | 1/9 (11%) | 7/9 (78%) |
| Nominal 95% coverage | 5/9 (56%) | 9/9 (100%) |
| Residual signs | 9 positive, 0 negative | 0 positive, 9 negative |
| Exact two-sided sign-test $p$ | 0.0039 | 0.0039 |
| Frozen prediction versus outcome, Pearson $r$ | −0.078 ($p=0.842$) | +0.617 ($p=0.077$) |
| Frozen prediction versus outcome, Spearman $\rho$ | +0.117 ($p=0.765$) | +0.300 ($p=0.433$) |

For context, exact binomial 95% confidence intervals around the empirical 95% coverage rates are 0.212–0.863 for `t180` and 0.664–1.000 for rebound. Nine points cannot estimate a smooth calibration curve. They can expose gross directional bias, which is what happened here.

## A2. Attribution: established misspecification, unresolved mechanism

**Ruling: both noise misspecification and representation shift remain plausible, but the data identify neither as the unique cause. The only firm attribution is model misspecification under deployment covariates.**

What the results establish:

- The frozen model was systematically optimistic for `t180` and systematically high for rebound. Mean residual 95% t intervals across the nine designs were +0.070 to +0.261 for `t180` and −4.94 to −2.15 mJ for rebound.
- It had no ranking skill for `t180` in this batch. That is stronger evidence than simple undercoverage.
- Per-drop SEM was the wrong variance for predicting a new article. It can cause short length scales, excessive confidence, and aggressive acquisition, but **an understated zero-mean noise variance does not by itself predict that every residual will have the same sign**. It explains overconfidence better than directional bias.
- A deployment shift can create directional bias, but the supplied geometry does not isolate it. Round 1 was also projected before printing, no base design was printed at two controlled scales, and scale is confounded with all five design coordinates.

Evidence against presenting shrink as the identified cause:

- Round-2 scales ranged from 0.673 to 1.092. Seven articles shrank and two expanded. The claimed universal 20–30% shrink is false for these files.
- Scale distributions overlap strongly between rounds. Mean scale changed from 0.897 in round 1 to 0.865 in round 2.
- Within round 2, shrink percentage versus `t180` residual gave Pearson $r=0.382$ ($p=0.310$) and Spearman $\rho=0.400$ ($p=0.286$). The corresponding correlations with rebound residual were −0.326 ($p=0.391$) and −0.300 ($p=0.433$).
- The two residuals were negatively associated, as the stiffness story predicts, but weakly: Pearson $r=-0.555$ ($p=0.121$). This is suggestive, not discriminating.

Other plausible contributors are the unmodeled projection mapping itself, extrapolation from only eight mapped round-1 articles, print/mount realization, detector definition, defects in three round-2 articles, and using base coordinates when the tested objects occupy different absolute dimensions. The data do not apportion these causes.

**Round-3 implication:** fix both failures. Use article-level noise and train/generate in the same as-printed representation. Do not choose one remedy based on this batch.

## A3. Scorecard against the 8/21 review

| Prior prediction or conclusion | Result |
|---|---|
| Per-drop SEM would make the optimizer overconfident for new articles. | **Supported for `t180`.** Only 5/9 fell inside nominal 95% latent-mean bands, and three exceeded 3 SD. Rebound bands were wide rather than overconfident. |
| Boundary collapse was not evidence of an optimum. | **Supported.** No round-2 article beat `6lhxfy` on `t180`; the frozen `t180` means had no within-batch ranking skill. |
| qNEHVI was extending a fragile inferred front. | **Partly supported.** The observed empirical front did extend, especially on the low-rebound channel, but not with a validated second objective or article replication. The prior review was too dismissive about the possibility of useful rebound discrimination. |
| `e_rebound` detector was fragile across new geometry. | **Refuted for this batch.** All nine yielded stable values, with within-session rebound CV 0.43–3.82% (median 1.26%) and second-event-time CV 0.36–3.39%. This is meaningful detector evidence. It does not validate event identity. |
| `e_rebound` should not be an objective without physical validation. | **Still supported.** Stable detection answers repeatability within these sessions, not what moved, whether the event is harmful, or whether minimizing flight-time-derived velocity is the correct direction. |
| A batch of one article per design cannot estimate design repeatability. | **Supported and now directly limiting.** No print-to-print variance is available for any new front point. |
| Article-level noise alone explained the collapse. | **The prior review did not claim uniqueness and was right not to.** The new data elevate representation shift as a competing explanation that the prior review did not analyze. |

# B. The rebound channel after round 2

## B1. Status of the metric

Round 2 supplies two real advances:

1. The detector returned stable delayed-event values across nine new geometries, including a 3-fold range in article means from 0.0142 to 0.0440.
2. `r2d2c6` produced a channel value of 4.07 mJ versus the previous absolute-energy floor of 6.10–6.18 mJ, a 33–34% decrease.

That moves `e_rebound` from “fragile diagnostic” to **stable diagnostic in this batch**. It does not make it a valid engineering objective. The formula still estimates a velocity ratio under ballistic assumptions and is then multiplied by $mgh$ without squaring the velocity ratio. It is not measured rebound energy. No synchronized video, relative-motion record, or second-impact amplitude establishes event identity or damage relevance.

Promotion path:

- **To a constraint:** synchronized high-speed video must show that the same detected interval consistently brackets separation and re-contact across at least a high-hop and low-hop geometry, restrained/unrestrained intervention must alter the event as predicted, and the constraint must be stated on a payload-relevant second-impact peak or shock-response-spectrum ordinate. Independently printed articles must reproduce it.
- **To an objective:** all constraint requirements plus an engineering utility showing why lower is monotonically better. The present data do not supply that utility.

## B2. Correlation and whether a front is established

There are 17 mapped articles in `objectives-mass-normalized.csv`, not 18. The eighteenth tested article is unmapped `amdjwm` and correctly cannot enter a design-space or Pareto analysis.

Across the 17 mapped articles:

- `t180` versus absolute rebound energy: Pearson $r=-0.537$, $p=0.026$; Spearman $\rho=-0.456$, $p=0.066$; Kendall $\tau=-0.338$, $p=0.063$.
- Excluding `6lhxfy`: Pearson $r=-0.401$, $p=0.124$; Spearman $\rho=-0.347$, $p=0.188$.
- Round 2 alone: Pearson $r=-0.399$, $p=0.287$; Spearman $\rho=-0.217$, $p=0.576$.
- A 200,000-resample article bootstrap gave a descriptive Pearson 95% interval of −0.785 to −0.166. This interval does not correct measurement error or establish a mechanism.

The anti-association is less dependent on one point than at $n=7$, but rank evidence remains marginal and round 2 by itself does not show a monotonic trade-off. An **empirical nondominated set exists by definition**. A stable physical Pareto front does not yet exist as an evidence-backed claim. A one-dimensional compliance mechanism remains compatible with the data.

## B3. Absolute versus per-gram framing

The recomputed fronts exactly match the flags:

- Absolute mJ: `{6lhxfy, r2d2c7, r2d2c1, r2d2c2, r2d2c6}`.
- Per gram: `{6lhxfy, r2d2c7, r2d2c1, ajhby6, bpx68c, r2d2c6}`.
- Common set: `{6lhxfy, r2d2c7, r2d2c1, r2d2c6}`.

The team’s common-membership claim survives. `r2d2c2` is not robust to framing and is drift-contaminated. Present the **per-gram form as a rescaled diagnostic velocity ratio**, not as specific energy absorption. It removes specimen mass from a quantity whose physical “energy” interpretation is already unsupported. If stakeholders require the historical BO plot, show absolute mJ beside it and state that the front changes.

# C. Rulings on proposed presentation claims

## C1. “The batch genuinely improved the Pareto front…”

**Verdict: survives with a required caveat.** The arithmetic is correct for measured means: four of five absolute-front points are round 2; `r2d2c1` is lower than `bpx68c` on both means; and `r2d2c6` lowers the measured absolute floor from 6.10–6.18 to 4.07 mJ.

Use this caveat verbatim:

> **“This is an empirical front of single printed articles on a physically unvalidated rebound proxy. It is not yet a replicated design-level Pareto front; `r2d2c2` is drift-contaminated, and front membership changes under mass normalization.”**

Do not say `r2d2c1` “strictly dominates” `bpx68c` without “on observed means.” With the 0.72% `t180` floor and a provisional 5% rebound floor, the approximate probability that `r2d2c1` is lower on both is only 0.65. By contrast, `r2d2c6`’s low-rebound separation is large: 4.07 versus 6.10–6.18 mJ.

## C2. “The model was systematically optimistic… plausible physics…”

**Verdict: survives with a required caveat for the first clause; does not survive as a causal explanation.**

Use this caveat verbatim:

> **“All nine `t180` outcomes exceeded their frozen predictions, but these data do not identify why. Reprojection-induced stiffness is one hypothesis; noise misspecification, sparse extrapolation, mounting, defects, and the mismatch between base and as-printed coordinates remain confounded.”**

The sentence “the same stiffness that raises `t180` lowers restitution” is consistent with the signs but is a just-so story at present. Scale did not significantly explain residual magnitude, and there is no controlled same-design/different-scale comparison.

## C3. “The uncertainty bands did their job…”

**Verdict: does not survive.** It is selective. A fair slide statement is:

> **“The wide rebound bands covered all nine measurements but were directionally biased: all nine outcomes were below their predicted means. `t180` was miscalibrated, with only 5/9 inside nominal 95% latent-mean bands.”**

## C4. Additional result worth presenting

Say this:

> **“Round 2 proved that the rebound detector can be stable and design-discriminating within short sessions across nine new geometries, but one article per geometry cannot separate design effects from print and mounting realization.”**

Also say that the frozen model did not improve the primary endpoint: best round-2 `t180` was 0.948 (`r2d2c7`), 0.055 above round-1 best `6lhxfy` at 0.893. Only two of nine round-2 articles had `t180<1`.

# D. Data-quality rulings

## D1. `r2d2c3`

The recorded result is internally stable but physically ambiguous:

- Every scored drop was separated from every other article: `r2d2c3` minimum `t180` was 1.303; the maximum among the other eight was 1.200.
- Its linear drift was −0.0145% per drop ($p=0.703$), so the high mean is not a session ramp.
- `t1000/t180=1.860`, versus 0.999–1.450 elsewhere, is a real signal-processing signature, not random scatter.
- `r2d2c3` and `r2d2c6` have the same base $R,H,$ strut, and cable settings and nearly identical as-printed dimensions; twist differs by 40°. Their large outcome difference could therefore be a real twist-controlled broadband mode. It could also be seating/mount coupling because both `t180` and especially `t1000` are mount-sensitive.

The committed metrics cannot discriminate those explanations. **Hold `r2d2c3` out of training pending re-test.** Do not merely deweight a possible structural outlier into a possible mount outlier.

Minimal re-test: remove and reinstall the accelerometer/mount, document seating, then collect two blinded randomized blocks of 10–12 stabilized drops on the same article, interleaved with `r2d2c6` or `bpx68c`. If the 1.33/2.48 signature survives independent reseating, ingest both sessions with a session effect. If it collapses, mark the first session as a mount failure.

## D2. `r2d2c2`

The drift is not subtle: slope +0.2529% per drop, $p=6.0\times10^{-11}$, with first-five versus last-five means 1.023 and 1.059. **Re-test and exclude the current mean from front and GP claims until a clean session exists.** An illustrative uncertainty that adds half the 3.5% excursion in quadrature is 0.020, versus 0.0083 from the 0.72% floor plus drop SEM, but that inflation assumes an arbitrary drift distribution and does not repair a window-dependent estimand.

## D3. Mixed session lengths

Per-drop SEM is not adequate. It addresses uncertainty in an article’s session mean, not print-to-print prediction. In round 1, first-19 versus full-session differences reached 0.00793 in `t180` (0.747%), essentially the entire 0.72% article floor. For rebound they reached 21.1% for `amdjwm`; even excluding that detector failure, `ajhby6` shifted 3.91%.

For the immediate refit, re-window round 1 to the first 19 stabilized drops so both rounds estimate the same early-session mean. Retain full data for diagnostics. The better later model is a hierarchical drop-index/session model rather than discarding data. Use randomized blocks and a reference article so time drift is estimable rather than silently folded into geometry.

# E. Round-3 ruling

## E1. Diagnosis of the proposed pivot

The new batch is not evidence of genuine low-twist learning. Eight of nine points are at minimum twist and seven at maximum cable diameter. Trial 22 violates the envelope limit and trial 26 violates the cable-bridge rule. The proposed `t180` means, 0.998–1.052 with mean 1.021, sit near the mapped round-1 mean 1.008 and all-data mean 1.053. This is compatible with posterior regression toward the data center after the optimistic corner failed. It is not evidence that the model learned an improved attenuator: no proposed mean approaches observed `6lhxfy=0.893`, and no round-2 article beat it.

The low-rebound side is also tracking a single unreplicated observation: trials 20 and 25 are predicted near 4.85 mJ after `r2d2c6=4.07` mJ. Calling this a learned corner would be premature.

## E2. Concrete formulation and allocation

### Model

- **Objective:** minimize `t180` only, interpreted as a CFC-180 peak-ratio screening endpoint.
- **Exposure controls:** restrict test sessions to the demonstrated healthy input-$\Delta v$ band and include centered session-mean `in_dv_ms` as a nuisance covariate. Record `in_180_g`, pulse width, baseline quality, saturation, block, and reference response. Do not optimize exposure.
- **Diagnostics:** raw `out_180_g`, `t1000`, delayed-event timing and amplitude, measured mass, print defects, and modal-fit outputs where valid.
- **Constraints:** printed mass target 20.23 g with a prespecified manufacturing tolerance based on achieved process capability, envelope ≤250 cm³, cable bridge ≥3.0 mm, no invalid captures, and no unresolved drift flag. Do not use the artificial ±0.01 g optimizer slab as if it were physical process capability.
- **`t180` observation SD:**

$$\sigma_{T,i}=\sqrt{(0.0072y_i)^2+\frac{s_{drop,i}^2}{n_i}}.$$

  Across the supplied mapped articles this is about 0.0064–0.0100; for ordinary, unflagged round-2 articles it is about 0.0068–0.0087. Run sensitivity fits at 0.5%, 1%, and 2% relative floors. Handle `r2d2c2` and `r2d2c3` by data-quality rulings, not arbitrary variance inflation.
- **Rebound, if shown in a non-acquisition sensitivity fit only:**

$$\sigma_{E,i}=\sqrt{(0.05E_i)^2+SEM_{drop,E,i}^2}.$$

  This gives approximately 0.20–0.70 mJ over the mapped data. The 5% term is a conservative sensitivity choice from prior session evidence, not an estimated independent-print SD. Do not use rebound in acquisition until validation.
- **Acquisition:** compare corrected single-objective SAASBO with a regularized conventional GP and a space-filling or Thompson-sampling batch over several seeds. A new geometry should print only if its selection is robust to the 0.5–2% noise range and model choice. qNEHVI is not applicable with one objective; noisy expected improvement or Thompson sampling is.

This follows the distinction between replication noise and exploration used in stochastic Gaussian-process design [Binois et al., 2018](https://doi.org/10.1080/10618600.2018.1458625); [Binois et al., 2019](https://doi.org/10.1080/00401706.2018.1469433). qNEHVI accounts only for uncertainty supplied to its model and does not protect against a wrong objective, likelihood, or covariate representation [Daulton et al., 2021](https://doi.org/10.48550/arXiv.2105.08195). SAASBO’s sparse-axis prior does not remove the need for adequate replication or deployment-valid inputs [Eriksson and Jankowiak, 2021](https://doi.org/10.48550/arXiv.2103.00349).

### Search representation

Refit on **as-printed** `R`, `H`, strut diameter, cable diameter, twist, and measured mass. Generate candidates through the same print-projection function first, then evaluate acquisition at their projected coordinates. Treat measured mass as a post-print covariate/constraint, not a freely exploitable design coordinate.

Printed mass alone does not absorb the representation shift. Two objects can have the same mass and different absolute dimensions, strut slenderness, cable section, and material distribution. A model fitted to base coordinates plus mass still asks the GP to infer an unobserved nonlinear projection from 17 articles. A projection-regime indicator cannot be estimated before any outcomes exist under the new regime. The clean bridge is to reproduce known as-printed geometries under controlled manufacture and ingest realized geometry and mass.

### Nine print slots

Print **three independently manufactured articles at each of three geometries**:

1. Three at the as-printed `6lhxfy` geometry, the unreplicated primary-endpoint best.
2. Three at the as-printed `r2d2c6` geometry, the unreplicated low-rebound extreme.
3. Three at one newly regenerated, constraint-valid geometry selected by agreement among corrected fits.

Use 10–12 stabilized drops per article after two warm-ups, randomized in blocks, with the same durable reference article at block start and end. The existing originals should not be counted as exchangeable replicates if process/projection conditions differ.

**Print decision:** regenerate. Print none of trials 19–27 as a BO recommendation. If schedule makes partial use unavoidable before refitting, trials 19, 20, and 24 are the only defensible sentinel subset because they are constraint-valid and span distinct corners; label them “model-diagnostic sentinels,” not optimized round-3 designs. Do not print trials 22 or 26.

## E3. Does the mass parameter fix the shift?

No. It helps condition on one important realized property, but it cannot encode the change from constant-solid-mass scaling to constant-printed-mass manufacture. The corrective action is as-printed geometry for fitting and generation, measured mass as a covariate/constraint, and matched replication bridging the manufacturing regimes. Any prediction under the new projection policy remains an extrapolation until such bridge data exist.

# F. Final verdict

1. **Calibration attribution:** the frozen model is decisively directionally biased on both outputs. Noise misspecification explains false precision; a base-versus-as-printed representation mismatch can explain deployment bias. The present data do not separate them, and the claimed universal 20–30% shrink is not in the numeric files. Fix both.
2. **Presentation claims:** C1 survives only as an observed, unreplicated proxy-front claim with the verbatim caveat above. C2’s optimism survives, but the stiffness attribution does not. C3 does not survive. Add the detector-stability result and the failure to improve best `t180`.
3. **Round 3:** one objective (`t180`), article-level 0.72% CV floor plus drop SEM, as-printed geometry, mass as realized covariate/constraint, input severity as nuisance covariate, and three articles each at `6lhxfy`, `r2d2c6`, and one regenerated design. Do not print the nine proposed candidates as a batch.
4. **Cheapest measurement with the highest immediate decision value:** **re-seat and re-test `r2d2c3`.** It determines whether the largest calibration failure and strongest broadband anomaly belongs in the 17-point fit. One article, two short blocks, and no new print are required. A restrained/unrestrained video test remains the cheapest way to validate rebound physics, but it does not resolve the immediate training-set contamination that will determine round-3 geometry.

# Reproducibility notes and limitations

- All summary means and SDs reproduced exactly from the 172 stabilized round-2 rows. The CSV field `n_valid` counts 21–22 trigger-valid captures, whereas the reported means use 19–20 rows after two warm-ups. Noise calculations in this review use the actual scored counts.
- `objectives-mass-normalized.csv` contains 17 mapped articles. Text calling this an 18-article objective analysis includes unmapped `amdjwm`; it cannot be used in a geometry-conditioned fit.
- There are no raw acceleration time histories in this review bundle. I could not recompute filtering, event picking, second-impact amplitude, shock-response spectra, or mount coupling. SAE J211 supports impact-channel filtering but does not validate the physical interpretation of this ratio [SAE J211/1_202208](https://doi.org/10.4271/J211/1_202208). Shock-response-spectrum validation would require the time histories and a specified damping/frequency range (ISO 18431-4:2007).
- Pareto probabilities are sensitivity calculations, not inferential proof. They assume independent normal article errors, a 0.72% `t180` floor, and a provisional 5% rebound floor. No independent-print rebound variance has been measured.
- Correlations are observational across selected designs. They do not establish causation or a population Pareto surface.

# Discretionary analytical decisions

- Treated the independently printed article, not a drop, as the design-level replication unit.
- Used two-sided exact sign tests at $\alpha=0.05$ and reported nominal 68% and 95% coverage against frozen latent-mean posterior SDs.
- Used both Pearson and rank correlations, leave-one-out sensitivity, and a 200,000-resample article bootstrap because one-point leverage remained plausible.
- Used the 0.72% CV as the central `t180` article-noise floor, with 0.5%, 1%, and 2% sensitivity fits.
- Used a 5% relative rebound floor only for sensitivity calculations; it is not claimed as an estimated print variance.
- Recomputed short-session comparability at the first 19 stabilized drops, matching the modal round-2 scored count.
- Recommended holding `r2d2c3` and the current `r2d2c2` session out rather than assigning subjective large variances.
- Chose a three-geometry by three-print allocation to estimate article repeatability at both observed extremes while retaining one corrected-model exploration geometry.
- Preferred the per-gram rebound display because it removes measured specimen mass, while explicitly refusing to call it specific absorbed energy.
