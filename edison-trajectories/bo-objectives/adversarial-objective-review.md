# Adversarial review of the T3-prism Bayesian-optimization objectives

**Review date:** 2026-08-21  
**Decision:** **Do not print the nine round-2 suggestions as-is.** Refit the optimizer with one primary objective and article-level noise, then regenerate the batch. Before deciding whether rebound belongs in any future optimization, run a short synchronized-video restrained/unrestrained test. The present batch was generated from a mislabeled, physically unvalidated second objective and a materially understated noise model.

## What changes the next print

1. **Drop `e_rebound` from qNEHVI.** It is a velocity ratio only under a restrictive ballistic interpretation, not an energy ratio. The bundle does not establish what body is in flight, that the carriage is stationary during flight, or that the detected second event is consistently a landing. Its detector fails conspicuously for `amdjwm` and is weak for other sessions.
2. **Use one primary response: minimize CFC-180 filtered peak ratio `t180`, with input severity controlled and recorded.** This is defensible as a screening endpoint, not as “energy absorbed.” It distinguishes these articles strongly, but it remains vulnerable to geometry-dependent mount coupling.
3. **Do not pass per-drop SEM as design noise.** The optimizer predicts a new printed article. Drops are repeated measurements on one article. The attached five-print study estimates a between-article-plus-mount CV of **0.72%**, not 2%; **1.95% is the observed five-print range**, not a standard deviation. Use a `t180` observation SD of approximately `sqrt((0.0072*y)^2 + SEM_drop^2)`, about **0.0064-0.0076** here. This is still 14-44 times the per-drop SEM in SD, depending on specimen.
4. **The current boundary collapse is not evidence that the corner is optimal.** Eight of nine suggestions set strut diameter to 12 mm, seven set height to 60 mm, and most other coordinates also hit bounds. With seven completed points in five dimensions, a batch of nine, fixed near-zero observation noise, and an extreme `6lhxfy` observation, SAASBO can interpret article/mount variation and one-point leverage as a steep deterministic surface. qNEHVI then spends the batch exploiting/extending a fragile inferred front. The collapse is consistent with the bad noise specification, though not uniquely caused by it.
5. **Reallocate drops to prints.** For each selected geometry, use at least **3 independently printed articles × 10-12 stabilized drops/article**, randomized in blocks with a reference article before/after each block. Ninety-nine analyzed drops on one print estimate that article very precisely but add almost no information about the next print.

---

# A. Locked data-only commitment

> **Provenance:** This block was written before reading the campaign markdown, print-defect markdown, energy-review markdown, README, analysis scripts, BO script, or suggestion file. It was saved at `edison-trajectories/bo-objectives/SECTION_A_LOCKED.md` on 2026-08-21T05:55:22Z with SHA-256 `c1f43a8a1f913e0b8390d291b1a27ef780c49555131d8d3a915dde3b2d5aea64`. The wording below is condensed for this report; the locked file retains the full original text.

## A1. Data-only objective choice

**Committed choice:** one objective, minimize input-adjusted CFC-180 output peak. Use `t180 = out_180_g/in_180_g` now, with `in_180_g` and `in_dv_ms` as exposure controls. With future independent-article replication, prefer output peak predicted at a prespecified input peak and pulse severity over an unqualified ratio.

| Candidate | Data-only classification | Reason |
|---|---|---|
| `t180` | **Objective, minimize** | Directly represents CFC-180 peak attenuation and removes much input-level variation. It is a filtered peak ratio, not a frequency-response transmissibility. |
| `out_180_g` | Endpoint requiring input adjustment | This is payload-facing, but raw specimen means are confounded by input means of 202.6-231.8 G. Within specimens, input/output peak Pearson correlations are 0.793-0.993. |
| `in_180_g` | Constraint/covariate | Exposure severity, not performance. |
| `in_dv_ms` | Constraint/diagnostic | Exposure and rig-health descriptor. |
| `t1000` | Diagnostic or threshold constraint | Flags broadband amplification; values reach 1.230-1.242. It is too session-sensitive to be coequal. |
| `t_second_ms` | Diagnostic | Timing alone is not damage or energy. Event identity is unvalidated. |
| `e_rebound` | Diagnostic only | Under ballistic assumptions it is `v_up/delta_v`, a velocity ratio. It is not an energy ratio. |
| `fn_hz`, `zeta_pct` | Opportunistic diagnostics | Fits are unavailable or unusable for several articles. |
| measured mass | Constraint/covariate | Printed mass varies 18.50-22.04 g despite constant solid-CAD mass. |

For a stationary landing surface and a body launched vertically at speed `v_up`, flight time is

`T_flight = 2 v_up/g`, so `g T_flight/(2 delta_v) = v_up/delta_v`.

An energy ratio would require squaring the velocity ratio and specifying compatible masses and reference states. Squaring a nonnegative objective is monotone, so it preserves deterministic ordering and Pareto membership, but it changes units, thresholds, uncertainty propagation, and interpretation.

## A2. Data-only assessment of a Pareto formulation

**Committed answer: no.** Across all eight specimen means, Pearson `r = -0.827` (`p = 0.011`), but Spearman `rho = -0.571` (`p = 0.139`). Excluding unreliable `amdjwm`, Pearson `r = -0.844` (`p = 0.017`, `n = 7`) while Spearman `rho = -0.393` (`p = 0.383`).

The dependence on one point is decisive:

| Reliable observations used | Pearson r | p | Spearman rho | p |
|---|---:|---:|---:|---:|
| all 7 | -0.844 | 0.017 | -0.393 | 0.383 |
| excluding `6lhxfy` | -0.429 | 0.395 | -0.029 | 0.957 |
| excluding `bag26v` | -0.849 | 0.033 | -0.429 | 0.397 |

A specimen-bootstrap 95% interval for Pearson correlation over the seven reliable points is **-0.982 to +0.762**, showing how little the sample fixes the population association. The empirical nondominated set for minimizing both metrics is `6lhxfy`, `6nheas`, and `bpx68c`, but three mutually nondominated observed articles do not establish a stable physical frontier.

## A3. Data-only noise commitment

**Committed replication unit:** independently printed article. The proposed formula was

`Var(y_article | design) = sigma_print^2 + sigma_session^2 + sigma_drop^2/n_drop`.

Based only on the prompt’s statement that printing moved `T` by ~2%, I provisionally committed to a 2% relative SD floor for `t180`, with no invented floor for rebound. I explicitly rejected per-drop SEM alone.

## A4. Locked answer

1. Optimize `t180` as the current input-normalized CFC-180 peak endpoint; develop output-at-fixed-input when replicated data support it.
2. Do not run `t180` plus `e_rebound` qNEHVI from these observations.
3. Use article-level, not drop-level, uncertainty.

## Explicit diff after reading the team documents

- **Change:** replace the provisional **2% SD** for `t180` with **0.72% relative SD** as the best bundle-based starting value.  
  **Why:** the print-defect study reports five article means with between-article CV 0.72% and a worst-to-best spread of 1.95%. The campaign text repeatedly calls the latter a “~2% floor,” but spread is not SD. The estimate also includes mount/order/session confounding and is therefore an upper bound on pure print variation, not a clean print-only component.
- **No change:** reject `e_rebound` as an optimization objective and reject per-drop SEM as design noise. Reading the documents strengthens both objections. The energy review itself states that the restrained-versus-unrestrained experiment remains open.
- **Refinement:** raw `out_180_g` should not replace `t180` without conditioning. Across the eight articles, raw-output rank versus `t180` is only Spearman `rho = 0.595` (`p = 0.120`); a simple output-on-input residual gives exactly the `t180` ranking here (`rho = 1.0`), but this is an eight-point descriptive fit, not a validated calibration model.

---

# B. `e_rebound` fails as an objective

## B1. Dimensional and physical audit

`e_rebound = g t_second/(2 delta_v)` is dimensionless. Under ideal ballistic flight, it estimates a **launch-velocity ratio**. Calling it a “rebound energy ratio” is wrong. If the numerator and denominator refer to the same mass and compatible states, the corresponding kinetic-energy ratio is `e_rebound^2`, not `e_rebound`.

There are additional assumptions hidden in the equation:

1. the detected interval starts at separation and ends at re-contact;
2. the same rigid body is in free flight throughout;
3. its launch and landing elevations are equal;
4. aerodynamic effects are negligible;
5. the landing surface is stationary or its motion is modeled;
6. `delta_v` is the relevant incident relative velocity.

The rig violates or has not demonstrated several of these. `in_dv_ms` is a full-pulse base integral and includes arrest plus rebound contributions; it is not automatically the incident specimen/plate relative velocity. The top sensor is attached to one vertex of a deformable tensegrity, not its center of mass or a known payload mass.

**Effect on BO:** replacing positive `e` with `e^2` would preserve a noiseless Pareto set, but not posterior inference. By the delta method, `Var(e^2) ≈ 4 e^2 Var(e)`, distributions become skewed near zero, and any fixed absolute SEM changes scale. Physical thresholds also change. The mislabeled quantity therefore affects more than prose once uncertainty or engineering limits enter.

## B2. What is hopping?

The bundle cannot establish it.

- The campaign records show a repeatable second-event time for most articles, but no synchronized video is included.
- The energy-review document asserts that the top vertex separates and lands, then says the restrained/unrestrained check is still scheduled. That is an inference followed by an admission that the discriminating test has not been run.
- No channel-resolved analysis demonstrates a top-only landing impulse absent from CH5, nor rules out carriage/mat restitution, plate motion, a rocking/recontact event, or a ringdown lobe.
- The carriage does rebound: the campaign analysis notes that full-pulse delta-v contains arrival plus rebound speed. A ballistic calculation relative to a moving plate is not the stated formula.

The TP4 series tables independently report event-level peaks, durations, and delta-v but do not report the late second event. They therefore validate the main pulse only, not the hop interpretation.

Even if the whole specimen leaves the plate, `0.5 m v_up^2` is energy of the specimen or some effective moving mass, not “energy returned to the payload.” The top accelerometer has negligible payload mass, and vertex deformation means its kinematics need not equal center-of-mass motion.

## B3. Direction of goodness

Both stories are plausible:

- **Minimize rebound:** a second impact can damage a payload, and retained elastic energy can create repeated shocks.
- **Do not penalize rebound automatically:** elastic storage and delayed return may lower the first transmitted peak. `6lhxfy` has the lowest `t180` (0.8931) and longest detected delay (55.18 ms). Penalizing its timing-derived velocity ratio can oppose the mechanism that reduces the primary peak.

For this rig, neither story makes `e_rebound` a valid objective because the metric omits the quantity needed to decide: the **amplitude, duration, direction, and payload response of the second impact**. A long soft hop and a short hard recontact can order differently by damage risk. If repeated impact is unacceptable, constrain the second-event CFC-180 peak or a payload-relevant shock-response-spectrum (SRS) ordinate after validating event identity. Do not minimize flight time as a surrogate.

## B4. Detector fragility

`amdjwm` is not a small anomaly. Its full session has `t_second` mean 31.77 ms, SD 15.70 ms, and range 22.06-69.96 ms; its `e_rebound` CV is 49.5%. The analysis document says the picker alternates between a landing candidate and a ringdown lobe.

Other warning signs:

- `nvxsrv`: `t_second` SD 1.25 ms and range 27.58-32.00 ms, wider than the 0.27-0.89 ms SD of most articles.
- `6lhxfy`: the detected second feature averages about **-9.36 dB** relative to the algorithm’s reference; `amdjwm` averages **-12.18 dB**. Soft events approach ringdown structure and are inherently harder to pick.
- Cross-session `e_rebound` shifts are **+6.59%** for `6lhxfy` and **+1.03%** for `amdjwm`, despite `t180` shifts of only -0.14% and -0.57%. With only two pairs, a rough independent-session relative SD estimate for rebound is 3.34%, with enormous uncertainty.

A fixed picker that always returns a value does not make the estimand observable. Soft, split, rocking, or multimodal recontacts require an explicit confidence/quality output and censoring model. Until synchronized video validates the detector across geometries, `e_rebound` is diagnostic.

---

# C. The claimed Pareto trade-off is not established

## C1. Association and leverage

The exact correlations are in Section A2. The headline linear anti-correlation is real for these observed means, but “genuinely trade off” is too strong because:

- rank correlation is nonsignificant;
- removing `6lhxfy` nearly eliminates rank association (`rho = -0.029`);
- one rebound value is unreliable;
- there are only seven training articles;
- uncertainty is at the article level, not the ~99-drop level.

The statement “best attenuator hops hardest” is one observation, not evidence of a general frontier.

## C2. Frontier versus one compliance axis

Two hypotheses remain:

1. **Decision-relevant conflict:** design variables independently control primary peak and validated rebound damage. Round 2 should populate distinct regions of a stable front, and replicated articles should preserve nondominance.
2. **One physical axis:** a compliant path shifts energy in time, reducing the first peak while increasing delayed motion. Then `t180` and hop timing are two projections of the same mechanism, and whether there is a conflict depends on a separate damage requirement for the delayed event.

Existing data do not discriminate these. Exploratory Spearman associations among the seven mapped articles are `rho(t180,H) = 0.929` and `rho(t180,strut diameter) = -0.750`, whereas rebound associations are weaker (`rho = -0.393` and `+0.321`, respectively). That could indicate partially different controls, detector noise, or small-sample confounding. Five variables with seven points cannot separate them.

A useful discriminating round would replicate designs that vary one suspected compliance control at a time, then measure main and second-event payload response directly. The proposed boundary-heavy batch is not such a test.

## C3. qNEHVI behavior and the collapsed batch

Noisy expected hypervolume improvement is designed for noisy multi-objective observations, but it can only honor the uncertainty supplied to it. Passing SD ~0.0004 for `t180` tells the model that differences of a few thousandths are highly reliable design effects. They are not reliable for a newly printed article.

In a sparse axis-aligned subspace Gaussian process (SAASBO), shrinkage encourages a few active dimensions. With seven completed points in five dimensions, an extreme low-`t180` point at relatively thick struts, short height, thin cables, and high twist can induce a simple steep story. qNEHVI then searches for hypervolume gains along that inferred surface while simultaneously filling a batch of nine. Boundaries are natural targets when a fitted trend has no observed turnover.

This is consistent with the output: 8/9 at maximum strut diameter, 7/9 at minimum height, 5/9 at each radius extreme, 8/9 at a twist extreme, and all 9 at a cable-diameter extreme. It does **not** prove that noise misspecification alone caused collapse. Search-space projection, sparse data, large batch size, model priors, and legitimate boundary optima can all contribute. The correct test is to refit with article-level noise and one objective and compare posterior diagnostics and suggestions across seeds.

---

# D. The noise model is the clearest failure

## D1. Consequences of per-drop SEM

The GP observation is one article mean. Per-drop SEM describes uncertainty in that article’s session mean, not variability of a future article made from the same geometry.

For campaign `t180`, drop SEM ranges about 0.00017-0.00052. The five-print study gives between-article-plus-mount SD `0.00744` at mean `1.03376`, CV **0.719%**. At campaign responses this implies SD **0.00643-0.00764**. The current likelihood is therefore too narrow by roughly **14-44 times in SD** and **~200-1,900 times in variance**, not a universal 50×. The “50×” comparison is only obtained by incorrectly treating the observed ~2% range as an SD.

Likely consequences are interpolation of print/mount lottery as geometry, exaggerated confidence in Pareto membership, spuriously short length scales or active-dimension selection, and aggressive exploitation. With `n = 7`, none of those diagnostics is stable.

## D2. What the print study actually supports

The five nominally identical article means are 1.0432, 1.0374, 1.0315, 1.0336, and 1.0231:

- mean: 1.03376;
- sample SD: 0.00744;
- CV: **0.719%**;
- range/mean: **1.944%**.

The 0.72% is not a clean print-only SD. Defect grade is confounded with test order, day, and a felt adjustment; accelerometer seating changes between specimens. The document correctly calls it an upper bound on pure print scatter. The study also used a different absorber arrangement and 20 ms records, which weakens transfer.

There is **no five-print estimate for `e_rebound`** because those 20 ms captures do not contain the later landing. The two matched session reruns bound only combined session/remount/detector effects for the same articles. They show far larger proportional movement in rebound than in `t180`, but two pairs cannot estimate a trustworthy variance component.

## D3. Concrete round-2 noise treatment

For `t180`, use a relative/log-scale model if available. A defensible fixed-noise approximation is

`sigma_i = sqrt((0.0072*y_i)^2 + SEM_drop,i^2)`.

This treats 0.72% as total article-level measurement/realization noise and avoids double-counting session effects already embedded in the five-print study. Run sensitivity fits at 0.5%, 0.72%, 1%, and 2% because the estimate is based on five confounded articles and a different test arrangement.

With fewer than ten points, estimating separate heteroskedastic print, session, and drop components inside the Ax Service model is not identifiable. Letting a homoskedastic GP infer all noise from seven points is also fragile. For this round, fixed empirically grounded noise plus sensitivity analysis is more defensible. Once replicated articles exist, fit a hierarchical model:

`y_design,article,session,drop = f(design) + article(design) + session(article) + drop error`,

and pass the posterior uncertainty for a new article or use a replicate-aware stochastic-kriging/heteroskedastic GP workflow.

If rebound is retained only for sensitivity, a provisional floor cannot be called print noise. The two session pairs suggest ~3.3% relative session SD, and detector failures argue for at least **5% relative SD plus explicit invalid/censored observations**. This is a conservative engineering sensitivity choice, not an estimate of print-to-print rebound variance. The preferred action is not to optimize it.

## D4. Better allocation

The 101-drop allocation is inefficient for design learning. Recommended for the same campaign stage:

- **3 independently printed articles per geometry**;
- **10-12 analyzed drops per article** after two warm-ups;
- randomized article order in blocks;
- the same reference article at block start/end;
- no mat adjustment within a block;
- fresh seating documented for each article.

Three articles × 12 analyzed drops gives 36 observations per geometry while changing the true design replication from one to three. If nine total print slots are fixed, do not spend all nine on nine new geometries. A practical compromise is **five new geometries plus four replicate prints**, including two additional `6lhxfy` articles and replication at a near-neutral/reference geometry. Exact allocation should be chosen after the corrected one-objective acquisition is generated.

---

# E. `t180` survives, but only as a screening metric

## E1. What the new campaign settles

The new evidence defeats the narrow claim that CFC-180 peak ratio cannot discriminate these tested articles. It spans 0.8931-1.0616, a 16.8% campaign spread, with within-article CV 0.17-0.48%. `6lhxfy` repeats across sessions to 0.14%; `amdjwm` to 0.57%. CFC-1000 does not transfer, changing -11.3% and -13.2% in the two reruns.

It does **not** establish that the difference is intrinsic structural attenuation. A mount or key-seat artifact can be stable for one geometry and reproducible after remounting if geometry controls contact area, wax thickness, orientation, local stiffness, or sensor alignment. Actual printed mass also covaries with design because constant solid mass did not yield constant printed mass.

Discriminating tests are:

1. independently printed replicate articles with randomized order;
2. repeated blind remounts per article;
3. an alternate top-sensor mounting or a small rigid payload plate with known mass;
4. synchronized video/relative-displacement measurement;
5. bench modal/transfer tests independent of the drop fixture.

The tail re-baseline and TP4 agreement support processing validity for the main pulse, not structural attribution.

## E2. Alternative metrics and ranking

What can be tested from the bundle:

- Raw `out_180_g` does **not** preserve ranking (`rho = 0.595` versus `t180`); it is input-confounded.
- A simple eight-article regression residual of output on input preserves the `t180` ranking exactly, but is underpowered and partly algebraic because `t180` is already the ratio.
- `t1000` is strongly rank-associated with `t180` (`rho = 0.929`) but changes the middle ordering and fails session transfer.

What cannot be tested from the attached derived files:

- SRS ratios at payload frequencies;
- band-limited frequency-domain transmission;
- output/input impulse ratios;
- simultaneous-peak or time-domain transfer measures.

Those require raw channel time histories, which are not in this bundle. The TP4 series tables contain independent per-axis event extrema, but axis peaks are not simultaneous and cannot reconstruct top-resultant CFC-180 peaks or SRS. Therefore no honest claim of ranking invariance across SRS, impulse, and band-limited alternatives is possible here.

SAE J211 channel-frequency-class filtering supports consistent impact-channel processing; it does not make a ratio of nonsimultaneous maxima a transfer function. SRS is standard for transient shock severity and should be computed from the 100 ms histories at payload-relevant oscillator frequencies and damping.

---

# F. Missing variables and recoverable information

## F1. What should enter

- **Primary objective:** `t180`, minimize, with accepted windows for `in_180_g`, `in_dv_ms`, pulse width, saturation, and baseline quality.
- **Raw output:** report and model as `out_180_g` at standardized input severity. Do not optimize unadjusted means.
- **CFC-1000:** diagnostic or an engineering constraint only after defining a threshold. Given poor remount transfer, do not use a tight threshold based on one session. The 1.23-1.24 values warrant investigation.
- **Mass:** enforce printed mass, not solid-CAD mass, if equal-mass comparison is intended. Otherwise include measured mass as a covariate and consider a separate mass constraint. Do not invent a mass-normalized peak-G metric; acceleration is already force per payload mass, while specimen-mass normalization needs a stated design utility.
- **`fn_hz`, `zeta_pct`:** mechanism diagnostics. Missingness and failed single-mode fits make them unsuitable as BO objectives.
- **Second-event response:** after event validation, use second-impact peak/SRS or a no-separation constraint, not flight time mislabeled as energy.
- **True absorption:** if the engineering goal is energy absorption rather than shock screening, add force-displacement hysteresis, specific energy absorption, crush-force efficiency, or an instrumented impactor test. Current accelerometer data cannot identify specimen absorbed energy.

## F2. `amdjwm`

A supervised GP cannot use an outcome-only point without design coordinates. Attaching guessed coordinates would corrupt the model. It remains useful as:

- evidence that the rig achieved `t180 = 0.9805`;
- a check on response and detector variability;
- a target for forensic identification.

Measure its mass and geometry, photograph/scan it, inspect plate labels and print logs, and compare distinctive defects. The print key suggests untested candidates with differing masses/geometries, but mass alone will not prove identity. Recovering its coordinates would add one of only eight outcomes and the second-best measured `t180`; with seven training points in five dimensions, that is a material information loss.

---

# G. Verdict

## 1. Locked answer and change after reading

The locked answer chose one input-adjusted CFC-180 peak objective, rejected rebound as an objective, rejected Pareto BO, and required article-level noise. Those conclusions stand. The numerical noise floor changes from a prompt-induced provisional 2% SD to the document-supported **0.72% CV**, because the reported ~2% is a five-print range.

## 2. Which legs of the quoted claim survive?

| Claim leg | Verdict |
|---|---|
| “Minimize `t180` and minimize `e_rebound`” | **Half survives.** Minimize `t180` as a screening endpoint. Remove `e_rebound`; it is not validated energy or payload damage. |
| “They genuinely trade off, so the Pareto front is informative” | **Does not survive.** Pearson association is leverage-sensitive, rank association is weak, event identity is unknown, and `6lhxfy` drives the apparent relation. |
| “Per-drop SEM is the BO noise; print floor noted but not modeled” | **Does not survive.** This is pseudoreplication for predicting a new article and materially overstates certainty. |

## 3. Corrected round-2 formulation

- **Objective:** minimize `t180` only.
- **Exposure/quality constraints:** prespecified acceptable ranges for input CFC-180 peak, input delta-v, pulse width, saturation, and baseline quality; block/reference correction if session drift is detected.
- **Diagnostics:** `out_180_g`, `t1000`, second-event waveform, mass, `fn_hz`, and `zeta_pct` where valid.
- **Noise:** `sigma_t180,i = sqrt((0.0072*y_i)^2 + SEM_drop,i^2)`, with sensitivity runs at 0.5%, 1%, and 2%. Do not use drop SEM alone.
- **Replication:** at least 3 prints × 10-12 analyzed drops for designs used to establish a design effect. Randomize and block with a reference.
- **Model check:** compare one-objective SAASBO against a simpler Gaussian process with regularized length scales and against a space-filling/Thompson-style batch. With seven points, suggestions that are not robust across plausible models/noise floors should not consume the entire print batch.

## 4. Print decision

**Do not print the committed round-2 suggestions as-is.** The cheapest defensible sequence is:

1. **Run a short event-identity experiment now:** synchronized high-speed video plus CH2-CH5 waveforms on one strong hopper (`6lhxfy`) and one low-hop reference (`bpx68c`), both unrestrained and lightly restrained against lift-off without changing the main load path. Use at least 5 stabilized drops per condition. Track carriage/plate and specimen center/top markers. This determines whether the delayed feature is specimen flight, carriage bounce, rocking, or ringdown-picker error.
2. **Refit immediately in parallel:** one `t180` objective, article-level 0.72% noise, pending points retained, and multiple noise sensitivities/seeds.
3. **Regenerate the nine-print allocation:** combine corrected-model proposals with independent replicas, especially additional `6lhxfy` articles. Do not let all nine slots chase the same unreplicated boundary trend.

The event test gates only whether rebound returns as a future constraint. It should not delay correcting the GP noise or regenerating the batch.

---

# Evidence and references

## Bundle evidence

- `campaign_metrics.json`: 794 post-warm-up per-drop rows across eight full sessions.
- `partial_sessions_metrics.json`: matched reruns for `6lhxfy` and `amdjwm`.
- `t3-prism-bo-batch-drop-results.csv`: article-level means/SDs and mapped design data.
- `series-table_*.csv`: TP4 independent event peak/duration/delta-v exports; these do not contain the late-event waveform needed to validate hopping.
- `drop-test-sobol-campaign-analysis.md`: baseline correction, rankings, session comparisons, and stated detector failure.
- `drop-test-print-defects-analysis.md`: five-print CV/range and confounding audit.
- `drop-tower-energy-absorption-review.md`: stated ballistic interpretation and explicitly pending restrained/unrestrained test.
- `t3_prism_bo_campaign.py`: fixed per-drop SEM, SAASBO, qNEHVI-style multi-objective service workflow, and omitted article-level floor.
- `t3-prism-bo-suggestions-round1.csv`: boundary-heavy proposed batch.

## External anchors

1. Eriksson D, Jankowiak M. “High-Dimensional Bayesian Optimization with Sparse Axis-Aligned Subspaces.” *Proceedings of UAI 2021*. DOI: [10.48550/arXiv.2103.00349](https://doi.org/10.48550/arXiv.2103.00349).
2. Daulton S, Balandat M, Bakshy E. “Parallel Bayesian Optimization of Multiple Noisy Objectives with Expected Hypervolume Improvement.” *NeurIPS 2021*. DOI: [10.48550/arXiv.2105.08195](https://doi.org/10.48550/arXiv.2105.08195).
3. Binois M, Gramacy RB, Ludkovski M. “Practical heteroskedastic Gaussian process modeling for large simulation experiments.” *Journal of Computational and Graphical Statistics* 27(4), 2018. DOI: [10.1080/10618600.2018.1458625](https://doi.org/10.1080/10618600.2018.1458625).
4. Binois M, Huang J, Gramacy RB, Ludkovski M. “Replication or Exploration? Sequential Design for Stochastic Simulation Experiments.” *Technometrics* 61(1), 2019. DOI: [10.1080/00401706.2018.1469433](https://doi.org/10.1080/00401706.2018.1469433).
5. SAE International. *SAE J211/1_202208: Instrumentation for Impact Test, Part 1, Electronic Instrumentation*. DOI: [10.4271/J211/1_202208](https://doi.org/10.4271/J211/1_202208).
6. ISO 18431-4:2007. *Mechanical vibration and shock: Signal processing, Part 4: Shock-response spectrum analysis*.
7. Bernstein AD. “Listening to the coefficient of restitution.” *American Journal of Physics* 45, 41-44 (1977). DOI: [10.1119/1.10904](https://doi.org/10.1119/1.10904).

## Limitations

- Only eight full-session articles and seven mapped training articles are available.
- The five-print variance study is confounded and used a different mat arrangement and shorter records.
- Raw 100 ms waveforms and campaign slow-motion video are absent, so SRS, band-limited transfer, impulse ranking, and physical second-event identity cannot be independently recomputed.
- Correlation analyses treat article means as independent; with `n = 7-8`, p-values and bootstrap intervals are unstable and do not establish mechanism or causation.
- Proposed rebound noise is not estimable from independent-print data. This is why rebound is excluded rather than assigned false precision.

## Discretionary analytical decisions

- Treated the independently printed article as the replication unit for design-level BO.
- Used Pearson and Spearman correlations together and leave-one-out sensitivity because linear correlation was visibly leverage-sensitive.
- Used a specimen-level nonparametric bootstrap for a descriptive correlation interval; no population-normality claim is made.
- Used the five-print 0.72% CV as the central fixed-noise floor and specified 0.5-2% sensitivity analyses because the study is confounded.
- Chose one-objective `t180` optimization rather than a two-objective model because rebound lacks a validated estimand and engineering threshold.
- Classified CFC-1000 and rebound as diagnostics/possible constraints rather than objectives pending repeatability and payload-relevance evidence.
- Recommended 3 articles × 10-12 analyzed drops as a pragmatic allocation balancing print replication and within-session precision; exact power depends on the design effect targeted.
