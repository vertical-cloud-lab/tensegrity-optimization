# SECTION A — LOCKED DATA-ONLY COMMITMENT

**Scope lock:** Derived only from the numeric CSV/JSON files and the rig description supplied in the request. I had not read the campaign markdown, print-defect markdown, energy-review markdown, README, analysis scripts, BO script, or suggestion file before writing this block. This text is not to be revised; later changes must be stated as diffs.

## A1. What I would optimize

**Primary formulation:** one objective, **minimize input-adjusted CFC-180 output peak**. With these data I would operationalize that as `t180 = out_180_g / in_180_g`, while retaining `in_180_g` as a nuisance/context variable and imposing an input-severity acceptance window. A preferable future analysis, once enough independent articles exist, is a regression/analysis-of-covariance estimate of output peak at a prespecified input peak (and possibly input pulse shape/delta-v), rather than relying solely on a ratio. The ratio is currently better than raw `out_180_g` for ranking because specimen mean input spans 202.6–231.8 G and output strongly tracks input within specimens (Pearson r = 0.793–0.993). Raw output confounds design with delivered input: for example, amdjwm's low 198.6 G output occurs at the lowest 202.6 G input.

**Candidate classification:**

- **`t180`: valid primary objective, minimize**, conditional on a controlled severity window and mount checks. It directly measures peak attenuation at the specified SAE J211 channel-frequency class. It is dimensionless and normalizes much of the delivered-input variation. A peak ratio can still be biased when numerator and denominator peaks occur at different times or when pulse shape varies, so input peak and delta-v remain diagnostics.
- **`out_180_g`: valid physical endpoint but not a stand-alone objective in this campaign.** It is arguably the payload-facing quantity of greatest engineering interest. Use it as the response in an input-adjusted model or evaluate it at a fixed input severity. With uncontrolled specimen-level input variation, its raw mean is confounded.
- **`in_180_g`: constraint/context, not an objective.** It defines exposure severity. Set an acceptance window or model it as a covariate; optimizing it would optimize the rig/contact rather than protection.
- **`in_dv_ms`: constraint/context and data-quality diagnostic.** It checks impact severity and supports restitution calculations. It is not a specimen performance objective unless the specimen can physically affect the measured base pulse, in which case that feedback itself is a rig-coupling diagnostic.
- **`t1000`: diagnostic and possible safety constraint, not a second coequal objective yet.** It detects high-frequency amplification missed by CFC-180. The cross-specimen rank association with `t180` is high (Spearman rho = 0.929), but broadband values reach 1.230–1.242 for nvxsrv/bag26v. I would cap unacceptable amplification if a payload-relevant threshold is defined rather than optimize it jointly without such a threshold.
- **`t_second_ms`: diagnostic, unusable as a direct protection objective.** It is a timing observation whose event identity must be validated. It does not by itself measure energy.
- **`e_rebound = g t_second/(2 delta_v)`: diagnostic only at present, not an objective.** For ballistic flight, flight time satisfies `t = 2 v_up/g`, hence `g t/(2 delta_v) = v_up/delta_v`: a **velocity ratio**, analogous to a coefficient of restitution only if `delta_v` is the correct incident relative-speed denominator and the detected second event is landing of the same moving body. It is not an energy ratio. A corresponding specific kinetic-energy ratio would be `(g t/(2 delta_v))^2` under restrictive equal-mass/reference assumptions. The label matters physically and for thresholds/noise under squaring, though a strictly monotone square would not change deterministic ordering or the Pareto set for nonnegative values. Event identity is not established by the tabulated metrics, and amdjwm's `t_second_ms` SD is 15.70 ms versus 0.27–1.25 ms for the others, demonstrating detector failure in at least one session.
- **`fn_hz`, `zeta_pct`: opportunistic diagnostics, unusable as campaign-wide objectives.** Missing for three or more specimens/fields and likely conditional on successful mode fitting. They may explain mechanisms but cannot support a common BO response from five specimens.
- **Printed mass:** constraint/covariate, not an objective under the stated constant-solid-CAD-mass goal. Actual mass ranges 18.50–22.04 g, so the intended equality did not hold in printed articles; include measured mass in interpretation and enforce/tighten a tolerance if mass is a design requirement.
- **Derived recommendation:** report an input-adjusted CFC-180 output peak at a fixed reference severity, plus `t180` as a transparent secondary summary. Do not create an energy-absorption objective from peak ratios or hop timing without force/displacement or validated body-velocity measurements.

`t180` and `e_rebound` appear negatively associated, but the evidence does not establish two independent pieces of payload-protection physics. `e_rebound` is nearly identical to `t_second_ms` across specimen means (Pearson r = 0.998) and may reflect one compliance/restitution axis or fixture motion. I therefore would not use a Pareto formulation from these data alone.

## A2. Is multi-objective optimization warranted?

No, not with `t180` and `e_rebound` as currently measured.

Across all eight specimen means, Pearson r(`t180`, `e_rebound`) = **−0.827** (two-sided p = **0.011**), but Spearman rho = **−0.571** (p = **0.139**). Excluding amdjwm because its rebound detection is flagged unreliable gives Pearson r = **−0.844** (p = **0.017**, n = 7) but Spearman rho = **−0.393** (p = **0.383**). This conflict indicates a small-sample, leverage-sensitive relationship rather than a securely ordered trade-off.

The dependence on 6lhxfy is decisive. Among the seven reliable specimens, removing 6lhxfy changes Pearson r to **−0.429** (p = **0.395**, n = 6) and Spearman rho to **−0.029** (p = **0.957**). Removing bag26v instead gives Pearson r = **−0.849** (p = **0.033**) but Spearman rho = **−0.429** (p = **0.397**). Thus the linear anti-correlation is largely anchored by one extreme attenuator/hopper and is not robust in ranks.

For minimizing both values, the measured nondominated set is 6lhxfy, 6nheas, and bpx68c after excluding unreliable amdjwm. That empirical set shows mutual nondominance but does not prove a stable decision-relevant Pareto frontier. With n = 7 reliable articles, one article per geometry, uncertain rebound event identity, and strong single-point leverage, a two-objective BO is unsupported. Optimize CFC-180 attenuation; retain rebound timing/velocity ratio as a diagnostic until independently validated and tied to a payload requirement.

## A3. Noise for each design observation

The experimental unit for design-level optimization is an **independently printed article**, not a drop. The 99 post-warm-up drops are repeated measurements of the same article and cannot reduce print-to-print variability by `sqrt(99)`.

For an article-mean response `y`, use

`Var(y_obs | design) = sigma_print^2 + sigma_session^2 + sigma_drop^2/n_drop`,

with terms defined on a relative/log scale where practical. Given the supplied prior replication scales, my initial fixed noise for `t180` would be a **2% relative standard deviation floor**, combined with the article's drop SEM and, only if the stated 2% print scale excludes remount/session variation, a session term up to 2%:

- if the ~2% print-to-print estimate already comes from independently mounted print tests and therefore includes ordinary session/remount variability: `sigma_t180 = sqrt((0.02*y)^2 + SEM_drop^2)`;
- if print and session components were estimated separately and are independent: `sigma_t180 = sqrt((0.02*y)^2 + sigma_session^2 + SEM_drop^2)`, with `sigma_session` estimated from matched re-mounts rather than automatically taking the maximum observed 2% shift.

At `t180 ~ 1`, the first formula gives SD ~**0.020**, versus the observed per-drop SEM ~0.00017–0.00052. The supplied ~0.0004 treatment is therefore ~50-fold too small in SD and ~2,500-fold too small in variance for predicting a new print.

No print-to-print replication scale is supplied for `e_rebound`, so I would **not invent one and would not hand it to the GP as near-zero fixed noise**. If it were retained after event validation, obtain independent-print replicates and estimate a log-scale article variance. Until then, a transparent provisional sensitivity analysis could use at least a 2% relative floor, `sqrt((0.02*e)^2 + SEM_drop^2)`, but that assumes transfer of the t180 print CV and is not evidentially justified. The correct data-only decision is to keep rebound diagnostic rather than pretend its design-level noise is known.

## A4. Committed answer

1. **Optimize one endpoint:** minimize input-adjusted CFC-180 output peak, using `t180` now and moving toward output-at-fixed-input when replication supports it. Treat input peak/delta-v as exposure controls; constrain gross CFC-1000 amplification; keep rebound and modal fits diagnostic.
2. **Do not run `t180` + `e_rebound` qNEHVI from these eight articles.** The rebound metric is a conditional velocity ratio, not energy; event identity is unvalidated; rank evidence is weak; and the association collapses without 6lhxfy.
3. **Use article-level noise.** For `t180`, start with `sigma = sqrt((0.02*y)^2 + SEM_drop^2)` if the print estimate includes mounting/session effects. Do not use per-drop SEM alone. Do not assign a precise design-level rebound noise without independent-print data.
