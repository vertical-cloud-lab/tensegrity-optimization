# Adversarial review of the polyurethane absorber arrangement sweep

**Dataset:** `bpx68c`, 40 drops, 2026-07-30  
**Decision reviewed:** adopt arrangement B, 1/2 inch polyurethane alone  
**Verdict:** **Do not select B from this sweep. None of A–D is supported as the Bayesian-optimization operating point.** B remains a reasonable candidate for a randomized discrimination test, but the present data measure one specimen under four sequential input conditions. They do not measure the quantity needed for selection: separation among geometries relative to print and repeat noise.

## Conclusions that change the decision

1. **The exported records do contain usable pre-trigger data.** In every record, raw CH5 first crosses the stated trigger about 0.39 ms after `t = 0` (arrangement means 0.377–0.390 ms). At `t = 0`, raw CH5 is only 0.09–2.6% of its peak, not 22–53%. The reported 22–53% is created mainly by acausal pre-ringing from forward-backward CFC-180 filtering. The premise that the export begins at the trigger is contradicted by the CSV samples.
2. **The full-record median is not a defensible baseline for the tri-axis resultant.** Replacing it with the median of the quiet first 0.10 ms changes mean CFC-180 T from A/B/C/D = 1.022/0.996/0.986/0.989 to **1.037/1.063/1.050/1.094**. The claimed monotonic decline with pulse duration disappears (Spearman $\rho=0.40$, $p=0.60$ across four block means). B is no longer closest to unity and is no longer the most repeatable CFC-180 arrangement.
3. **The structural-band criterion is an estimator artifact.** The published Welch calculation has 305 Hz bin spacing and only one bin, 610 Hz, inside 450–800 Hz. It also takes the spectrum of the nonlinear vector magnitude. Its B > A ordering reverses under every tested linear-axis energy calculation: with a Tukey window, output fractions are **A 30.7%, B 7.0%, C 1.4%, D 1.5%**; absolute A-band output energy is about **20 times B**. Input-normalized band energy instead ranks D > A ≈ C > B. Criterion 3 does not survive.
4. **The $f\tau \le 1.5$ pass/fail rule is incorrect for the stated purpose.** For a 5%-damped single-degree-of-freedom oscillator under an ideal half-sine base pulse, calculated absolute-acceleration shock response peaks near $f_n\tau=0.82$ at 1.65 times input. At A/B/C-D values near 0.91/1.23/1.84, the maximax responses remain about 1.64/1.54/1.28. C and D are not quasi-static. A hard cutoff at 1.5 has no basis for maximizing discrimination.
5. **A's broad-band instability is real, but it is a deterministic within-block drift, not an independent variance estimate.** With the pre-trigger baseline, A's CFC-1000 T rises monotonically from 1.012 to 1.251; Spearman $\rho=1.00$. Its raw input rises 4.62% per drop. B's CFC-1000 CV is much smaller, 1.11% versus A's 6.41%, but that only shows B is less sensitive to whatever changed during A's one block. It does not show B is sensitive to geometry.
6. **All arrangement tests are pseudoreplicated for the arrangement effect.** There is one sequential block per arrangement. Ten drops estimate repeat behavior within a block; they do not provide 10 independent arrangement replicates. The reported Welch p-values cannot establish stack effects, monotonicity, or stacking-order equivalence.

## Decision table: which original grounds survive?

| Ground for B | Verdict | What remains defensible |
|---|---|---|
| 1. Minimum T variance in both bands | **Does not survive as stated** | B is clearly less variable than A in CFC-1000 under all reasonable baselines. B is not robustly best in both bands, the 2% cutoff was post hoc, and variance alone is not discrimination. |
| 2. A/B pass a 2.7 ms shock-regime cutoff | **Does not survive** | Pulse durations differ. The proposed SRS interpretation and pass/fail boundary are wrong; the mode itself is unverified. |
| 3. B has most 450–800 Hz output energy fraction | **Does not survive** | The exact published percentages reproduce, but the ordering is caused by a one-bin, nonlinear-resultant spectral estimator. Defensible alternatives give incompatible rankings. |
| 4. A has physical bedding/contact-spike instability | **Partly survives** | A has a strong raw and CFC-1000 trend. “Bedding-in” and the exact contact mechanism are not identified; temperature, alignment, seating, and sensor/mount evolution remain alternatives. |

No surviving ground establishes that B discriminates geometry. The correct choice from this sweep is **“none of these; the sweep cannot decide.”** If the intended objective is impact-energy absorption, the question is also partly malformed because peak acceleration transmissibility does not measure absorbed energy.

## 1. Independent recomputation

### 1.1 Analysis plan and choices

1. Parse all 40 CSVs; exclude Signal 21 as instructed.
2. Inspect raw pre-trigger samples before choosing a baseline. The first 0.10 ms is quiet and precedes the rapid pulse rise; subtract its channel-wise median. Sensitivity checks used 0.05–0.30 ms, the last 5 ms, and the original full-record median.
3. Use a two-pole Butterworth low-pass at 300 Hz for CFC-180 and 1667 Hz for CFC-1000, applied forward and backward. This reproduces the supplied implementation when its full-record median is also used.
4. Search the first 12 ms independently for the absolute CH5 peak and tri-axis vector-magnitude output peak. Peaks need not be simultaneous. Define T as their ratio only to reproduce the proposed metric.
5. Define pulse width as linearly interpolated CH5 CFC-180 full width at half maximum. Integrate signed CH5 CFC-180 acceleration over 0–12 ms and report the maximum absolute cumulative velocity as **captured Δv**, not impact speed.
6. Treat CVs and Student-t confidence intervals as descriptive within-block summaries. They are not arrangement-level inferential uncertainty because the design has one block per arrangement and clear trends.

### 1.2 Arrangement summaries

Values are mean (CV). T 95% intervals are ordinary t intervals across ten drops and are descriptive only.

|Cfg.|Raw input/output G|CFC-1000 input/output G|T1000, CV, 95% CI|CFC-180 input/output G|T180, CV, 95% CI|FWHM ms|Captured Δv m/s|
|:--:|---:|---:|---:|---:|---:|---:|---:|
|A|2043 (14.54%)/2097 (7.40%)|806.4 (4.98%)/944.4 (1.90%)|1.174, 6.41%, [1.121, 1.228]|363.5 (1.73%)/377.0 (1.23%)|1.037, 0.54%, [1.033, 1.041]|1.644 (1.48%)|5.429 (0.63%)|
|B|526 (5.43%)/409 (7.60%)|326.7 (4.58%)/340.5 (5.29%)|1.042, 1.11%, [1.033, 1.050]|244.0 (2.38%)/259.4 (2.30%)|1.063, 1.18%, [1.054, 1.072]|2.142 (0.89%)|5.050 (1.98%)|
|C|272 (10.28%)/297 (2.60%)|175.6 (1.68%)/199.3 (2.33%)|1.135, 1.54%, [1.123, 1.148]|167.3 (1.61%)/175.6 (1.07%)|1.050, 1.22%, [1.041, 1.059]|3.278 (1.87%)|5.300 (1.76%)|
|D|220 (6.04%)/287 (2.55%)|178.6 (5.01%)/210.3 (2.80%)|1.179, 3.02%, [1.154, 1.205]|167.3 (3.80%)/182.9 (1.63%)|1.094, 2.48%, [1.074, 1.113]|3.146 (1.66%)|5.064 (3.93%)|

The original raw input means reproduce to rounding. The original filtered input peaks also reproduce when the original full-record median is used. The large T differences come from output baseline handling before taking a nonlinear resultant, not from impact-location selection.

### 1.3 Numbers that do not reproduce under a defensible baseline

|Quantity|Published A/B/C/D|Independent A/B/C/D|Cause|
|---|---|---|---|
|CFC-180 T|1.022/0.996/0.986/0.989|1.037/1.063/1.050/1.094|Full-record median shifts each output axis before vector magnitude; no true pre-impact baseline was used despite one being present.|
|CFC-180 T CV|0.43/0.34/0.95/0.49%|0.54/1.18/1.22/2.48%|Same baseline issue; D is especially sensitive.|
|CFC-1000 T|1.163/0.990/1.074/1.074|1.174/1.042/1.135/1.179|Same baseline issue.|
|CFC-1000 T CV|6.12/1.36/0.93/1.19%|6.41/1.11/1.54/3.02%|Same baseline issue and drift. A remains much worse than B.|
|FWHM|1.66/2.25/3.37/3.35 ms|1.64/2.14/3.28/3.15 ms|Pre-trigger instead of full-record baseline; A widths remain left-censored at half maximum.|
|450–800 Hz fraction|16.6/22.5/10.8/13.0%|Exact values reproduce only for the original estimator|Welch spacing 305 Hz leaves one in-band bin; spectrum of resultant magnitude is nonlinear and window-dependent.|

### 1.4 Per-drop results

An asterisk marks A widths whose left half-maximum crossing occurs before the record starts. The raw and filtered output are tri-axis magnitudes.

|Sig.|Cfg.|Raw in/out (G)|T raw|CFC1000 in/out (G)|T1000|CFC180 in/out (G)|T180|FWHM (ms)|Captured Δv (m/s)|
|---:|:--:|---:|---:|---:|---:|---:|---:|---:|---:|
|1|A|1615/1726|1.069|893.0/904.0|1.012|377.0/386.6|1.026|1.593*|5.501|
|2|A|1659/1942|1.170|843.7/927.3|1.099|369.2/380.8|1.031|1.621*|5.453|
|3|A|1793/2076|1.158|824.6/931.6|1.130|365.9/380.1|1.039|1.631*|5.422|
|4|A|1940/2154|1.110|811.1/950.9|1.172|364.2/377.7|1.037|1.639*|5.422|
|5|A|1983/2179|1.099|807.6/953.4|1.181|364.6/377.9|1.036|1.647*|5.452|
|6|A|2068/2102|1.016|795.9/957.9|1.204|362.2/375.6|1.037|1.651*|5.432|
|7|A|2230/2167|0.972|788.2/959.0|1.217|359.1/374.2|1.042|1.653*|5.377|
|8|A|2463/2185|0.887|775.6/958.3|1.236|358.9/372.5|1.038|1.664*|5.418|
|9|A|2322/2222|0.957|764.7/951.1|1.244|357.3/372.4|1.042|1.669*|5.412|
|10|A|2353/2223|0.945|759.8/950.7|1.251|356.1/372.2|1.045|1.674*|5.397|
|11|B|567/423|0.746|344.3/362.8|1.054|245.0/263.5|1.076|2.110|4.983|
|12|B|515/459|0.891|345.8/362.6|1.049|252.9/265.8|1.051|2.143|5.236|
|13|B|516/432|0.837|343.0/357.6|1.043|251.6/264.7|1.052|2.122|5.164|
|14|B|567/425|0.750|337.5/350.2|1.038|249.4/264.1|1.059|2.139|5.153|
|15|B|543/424|0.781|328.8/345.1|1.049|245.1/262.5|1.071|2.139|5.063|
|16|B|538/425|0.789|319.8/337.7|1.056|241.0/260.4|1.080|2.143|4.985|
|17|B|520/389|0.747|317.0/331.8|1.047|241.2/258.0|1.070|2.139|4.994|
|18|B|523/383|0.733|313.2/324.4|1.036|239.4/249.9|1.044|2.163|5.005|
|19|B|481/361|0.751|308.6/315.7|1.023|236.4/249.7|1.056|2.179|4.971|
|20|B|491/373|0.759|309.3/316.6|1.024|237.7/255.5|1.075|2.145|4.943|
|22|C|297/304|1.023|176.7/198.5|1.124|168.8/174.9|1.037|3.243|5.254|
|23|C|306/307|1.003|176.9/199.5|1.127|169.4/175.6|1.037|3.241|5.270|
|24|C|305/307|1.008|178.4/201.9|1.132|170.6/176.1|1.032|3.252|5.332|
|25|C|290/298|1.028|177.1/207.1|1.169|167.5/178.8|1.067|3.178|5.141|
|26|C|287/295|1.028|174.8/203.8|1.166|166.3/176.9|1.063|3.224|5.184|
|27|C|267/296|1.110|172.0/194.3|1.130|163.2/173.4|1.062|3.321|5.265|
|28|C|250/293|1.175|169.9/192.6|1.133|163.0/172.7|1.060|3.375|5.341|
|29|C|235/290|1.234|173.6/194.2|1.119|165.9/174.2|1.050|3.346|5.388|
|30|C|244/290|1.189|177.0/199.4|1.126|167.9/175.7|1.047|3.320|5.409|
|31|C|242/285|1.177|179.3/202.3|1.128|170.3/177.5|1.042|3.280|5.414|
|32|D|203/280|1.379|160.9/199.9|1.243|154.9/176.4|1.139|3.186|4.720|
|33|D|213/292|1.373|179.0/210.5|1.176|167.8/183.0|1.091|3.177|5.118|
|34|D|245/302|1.233|174.2/203.5|1.168|168.3/182.6|1.085|3.214|5.200|
|35|D|209/285|1.365|169.6/203.1|1.198|162.2/179.0|1.103|3.209|4.992|
|36|D|216/285|1.320|181.3/214.6|1.184|168.1/184.8|1.099|3.131|5.068|
|37|D|215/282|1.308|179.9/216.8|1.205|166.4/184.4|1.108|3.106|4.982|
|38|D|216/280|1.296|179.9/212.7|1.182|166.5/183.1|1.100|3.110|4.995|
|39|D|224/290|1.295|183.5/214.3|1.168|170.2/185.1|1.088|3.123|5.118|
|40|D|215/280|1.301|183.0/213.1|1.165|168.4/184.7|1.096|3.048|4.952|
|41|D|240/293|1.220|194.4/214.4|1.103|180.4/185.8|1.030|3.153|5.493|

Machine-readable copies accompany this report as `independent_per_drop_metrics.csv` and `independent_arrangement_summary.csv`.

## 2. Record start, filtering, and Δv

### 2.1 The record is not starting at the trigger crossing

Across all 40 files, raw CH5 crosses the configured threshold at 0.348–0.390 ms. Mean crossings are A 0.390, B 0.389, C 0.377, D 0.389 ms. The first 0.10 ms is near zero relative to peak. This looks like a fixed pre-trigger buffer in the export even though the metadata say otherwise.

Forward-backward filtering is acausal. It spreads the future pulse backward, producing CFC-180 values at `t = 0` equal to 15.9–52.1% of peak even though raw `t = 0` values are only 0.09–2.6%. Therefore `filtered[0]/peak` is not a truncation estimator.

Prepending 1–10 ms of a flat measured baseline before filtering changes mean CFC-180 T by at most 0.063% and CFC-1000 T negligibly. With the actual pre-trigger baseline, start-edge transients do **not** materially corrupt the interior peaks. CFC-180 is more edge-sensitive because its impulse response is longer. The severe sensitivity in the submitted table comes from baseline choice, not SciPy's endpoint padding.

### 2.2 Trigger-level confounding

The trigger change is aliased with A/B versus C/D at the design level, so cross-pair causal comparisons remain confounded. Signal-level evidence indicates that the exports nevertheless begin about 0.39 ms before their own threshold crossing. A/B share both trigger level and time period; C/D share the lower level. Thus the A-versus-B CFC-1000 CV contrast is not explained by different nominal trigger settings.

That does not fully rescue A versus B. Their pulse shapes differ, A's CFC-1000 T has a deterministic trend, and there is one fixed-order block per condition. Artificially cropping A/B at their first 150 or 300 G crossing leaves CFC-1000 CVs essentially unchanged, A ~6.2% and B ~1.2%. It strongly perturbs CFC-180 T because that filter needs low-frequency history. This reinforces the need for a longer pre-trigger capture, not the original claim that there is none.

### 2.3 Δv is not an impact-velocity measurement

The 0–12 ms cumulative integrals are 5.05–5.43 m/s on average, near the ideal 5.47 m/s free-fall speed from 60 inches. Agreement is not validation. The integral mixes deceleration, rebound, gravity convention, baseline error, plate rotation, and any post-impact oscillation. The terminal 20 ms integrals differ substantially from the maximum cumulative values. A's half-maximum onset is left-censored in all ten records.

Use this Δv only as a captured, processing-dependent waveform descriptor. Do not label it full impact Δv, a lower bound, or absorbed energy. A photogate/encoder immediately before impact and after rebound would provide actual incident and rebound velocities. A load cell plus displacement or velocity is needed for force–displacement energy.

## 3. The proposed 519–549 Hz mode is not identified

The current files cannot distinguish specimen deformation, sensor-plus-mount motion, specimen rocking, or base excitation. Sensor and specimen masses are missing, and the prior ringdown records cited for 519–549 Hz were not attached.

In a 4–18 ms axis-wise ringdown check, CH3 carries the largest 400–900 Hz output energy in all 40 drops. Its peak is approximately A 517 ± 6 Hz, B 533 ± 3 Hz, C 511 ± 37 Hz, and D 477 ± 54 Hz. CH5 also has arrangement-dependent content in this region: its dominant 400–900 Hz peaks average about 815, 497, 417, and 442 Hz. The 14 ms ringdown gives only ~71 Hz independent Fourier resolution before zero-padding, so small shifts should not be over-read. A shared 500 Hz feature on output and base may be forced response; an axis-specific output feature could be structural, rocking, or mount motion. Severity correlations are inconsistent across arrangements.

### Cheapest mode-identification check

1. Measure accelerometer, wax/key-seat, and specimen masses.
2. Suspend or softly support the specimen and perform an instrumented tap test in three axes with the present sensor.
3. Repeat after adding a known small mass at the vertex, ideally 5–10% of the sensor-plus-tip effective mass, and repeat with the accelerometer moved to a stiffer nearby point or replaced by a non-contact vibrometer/phone video if resolution permits.
4. A large frequency shift with added sensor mass implicates a mass-loaded tip/mount mode. A mode that persists sensor-off and changes predictably with specimen geometry supports a specimen mode. A feature that vanishes off the base or changes with contact restraint supports rocking/contact.
5. Analyze signed per-axis channels. Do not estimate modes from the tri-axis resultant, which mixes axes nonlinearly and can create sum/difference content.

The applicable mounting document is **ISO 5348:2021**, not ISO 5347. ISO 5348 specifically addresses mechanical mounting of accelerometers and mount-induced changes in frequency response. ISO 16063-21 concerns comparison calibration, not proof that a wax mount on a compliant printed tip is dynamically transparent ([ISO 5348](https://www.iso.org/standard/78160.html); [ISO 16063-21](https://www.iso.org/standard/27053.html)). Criteria 2 and 3 must remain suspended until this check is done.

## 4. Correct interpretation of the half-sine shock response

For a unit half-sine base-acceleration pulse and 5% damping, direct numerical integration gives:

|$f_n\tau$|0.91 (A-like)|1.23 (B-like)|1.84 (C/D-like)|
|---:|---:|---:|---:|
|Absolute-acceleration maximax / input peak|1.64|1.54|1.28|
|Local $d\log(SRS)/d\log(f_n\tau)$|−0.09|−0.34|−0.59|

The response tends below one for very short pulses because the oscillator cannot react, peaks near 0.8, and approaches the imposed base acceleration, ratio one, only for long pulses. C/D at ~1.84 are still above unity and on a steeper part of the curve. Calling them quasi-static is incorrect.

There is no universal SRS criterion for “maximum geometry sensitivity.” If geometry changes modal frequency, sensitivity to frequency is related to the local slope of the **actual-pulse** SRS, while sensitivity to damping depends on ringing and spectral width. The SRS peak itself has near-zero frequency slope, so targeting the peak maximizes response but can minimize frequency discrimination. A knee or steep flank may better separate nearby modal frequencies, but it also makes results more sensitive to pulse-duration drift. The design criterion should be empirical:

$$
D_s = \frac{\operatorname{SD}(\text{geometry effects under stack }s)}
{\sqrt{\sigma^2_{\text{print},s}+\sigma^2_{\text{drop},s}}},
$$

or an equivalent cross-validated ranking accuracy, evaluated under each candidate stack. Compute input and output SRS from each measured pulse over a prespecified damping grid, for example 2%, 5%, and 10%, and choose the frequency/damping region that maximizes held-out geometry separation while remaining repeatable. Actual pulses are not ideal half-sines, so using measured-waveform SRS is mandatory. MIL-STD-810H Method 516.8 practice is environment- and item-tailored; an arbitrary $f\tau$ cutoff is not a substitute for a test tailored to the response spectrum ([official MIL-STD-810 record](https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=35978)).

## 5. Selection logic and a defensible statistic

The proposed procedure is vulnerable to selecting the least informative stack. If output follows the base rigidly, T approaches a stable constant with low repeat variance even when geometry has no effect. B's published values near one do not prove this failure, but they are fully compatible with it. No single-specimen statistic can estimate between-geometry sensitivity. Coherence, modal-band energy, and response nonlinearity can reject very poor measurement conditions; none bounds an unobserved geometry effect.

The ensemble band calculations give A/B high input-output coherence (~0.94/~0.91 averaged over channels in 450–800 Hz) and lower C/D coherence (~0.74/~0.54). These values show deterministic repeatability of the measured block, not geometry discrimination, and common deterministic pulse shape can inflate them. A has much more absolute modal-band signal than B, while B has lower broad-band T drift. That is a trade-off, not a winner.

### Recommended selection statistic

Fit a hierarchical model to randomized data:

$$y_{gprks}=\mu_s+\alpha_{g,s}+b_{p(g),s}+\beta_s x_{rks}+u_{k,s}+\epsilon_{gprks},$$

where $g$ is geometry, $p$ is print nested within geometry, $r$ is repeat, $k$ is randomized time/block, $s$ is absorber arrangement, and $x$ contains measured input severity/SRS covariates. Rank stacks by one of:

- cross-validated standardized geometry separation $D_s$;
- probability of preserving known geometry rankings on held-out prints;
- expected information gain about geometry effects per drop.

Require acceptable sensor headroom, input repeatability, and no time trend as constraints, not as the objective. Prespecify the metric and threshold before data collection.

### Minimal decision experiment

The cheapest useful screen is a **20-drop randomized crossover** using two existing geometries expected to differ, with five drops per geometry on A and B, interleaved in randomized order. Use the same two physical articles for the screen, lower trigger consistently, record at least 2 ms pre-trigger and 50–100 ms post-impact, and compute signed-axis input-adjusted SRS/band-transfer metrics. This directly asks whether B's lower noise compensates for its lower absolute structural-band excitation. If the effect is near the reported 2.3% recent ranking span, proceed to a confirmatory design with at least three geometries, three independent prints per geometry, and randomized repeats. The 20-drop screen cannot estimate print variance; it is the cheapest risk-reduction experiment, not final qualification.

## 6. Statistical audit

### 6.1 Trends and serial dependence

Under a tail-baseline sensitivity analysis, lag-1 correlations are as high as 0.98 for A CFC-1000 T, 0.96–0.98 for A/B CFC-180 input, and 0.93 for A raw input. Simple AR(1) effective-sample-size formulas collapse several nominal n=10 sequences toward one effective observation. With only ten ordered points, these estimates are unstable, but they decisively contradict independence.

Trend-adjusting T gives residual CVs:

|Metric|A|B|C|D|
|---|---:|---:|---:|---:|
|CFC-180 T|0.45%|0.25%|0.70%|0.36%|
|CFC-1000 T|2.03%|0.89%|0.89%|0.84%|

A remains worse in CFC-1000 after linear detrending, but this is one trajectory per arrangement. The naive A/B CFC-1000 variance ratio is ~35 and median-centered Levene $p=0.0086$; those p-values are not design-valid because trends and serial dependence violate exchangeability. For CFC-180, the naive A/B variance ratio is 2.67, F-test $p=0.16$, Levene $p=0.39$. The claimed superiority in both bands is not statistically established.

The proper arrangement-level unit is the independently randomized block. Here $n=1$ block per arrangement, so there are zero residual arrangement-level degrees of freedom. Trend-adjusted models cannot separate arrangement from elapsed time, warm-up, sheet history, or the 80-minute break. Report block means and trajectories descriptively; do not report the supplied Welch p-values as evidence for stack effects.

### 6.2 C versus D is not evidence of equivalence

Under the optimistic false assumption of independent drops, n=10 per group provides 80% power only for a difference of roughly **1.1% in CFC-180 T** with the observed noise. Smaller stacking-order effects are poorly detectable. Under the real one-block-per-order design, order and time are confounded and equivalence is not testable. A nonsignificant $p=0.47$ cannot support “stacking order does not matter.” An equivalence claim requires a prespecified smallest effect of interest and a two-one-sided-test or interval analysis in randomized replicated blocks.

## 7. Band-energy criterion

The exact 22.5% > 16.6% > 13.0% > 10.8% ordering is not robust.

|Normalization/estimator|A|B|C|D|Ordering|
|---|---:|---:|---:|---:|---|
|Published resultant Welch share|16.6%|22.5%|10.8%|13.0%|B > A > D > C|
|Linear-axis, full-record Tukey share|30.7%|7.0%|1.4%|1.5%|A > B > D ≈ C|
|Absolute output band energy, relative to A|1.000|0.051|0.004|0.004|A >>> B > C/D|
|Output/input band-energy ratio, relative to A|1.000|0.189|0.919|2.026|D > A ≈ C > B|

A fraction penalizes broadband arrangements, absolute energy rewards harder impacts, and output/input ratios can explode where input band energy is tiny, as in C/D. None alone is a selection criterion. Use signed-axis cross-spectral transfer estimates with confidence intervals and coherence, or input-conditioned output SRS. Ensure adequate excitation at each frequency and use longer records. Criterion 3 collapses under defensible normalization.

## 8. Is peak-ratio T a suitable Bayesian-optimization objective?

No, not for impact-energy absorption. It divides nonsynchronous peaks of single-axis base acceleration and nonlinear tri-axis output magnitude. The numerator and denominator can arise at different times and frequencies. Sensor mass may alter the numerator's structure. The metric ignores force, displacement, incident kinetic energy, and rebound kinetic energy. CFC-180 strongly suppresses 550 Hz, so the observed 0.94–1.22 historical range is consistent with a mostly rigid-body pulse-transmission metric. It is suggestive, not proof, because no geometry-null or sensor-mass control exists.

### Ranked alternatives for this rig

1. **Input-conditioned output SRS or output peak at fixed input SRS.** Best immediate transient metric. Available from the same accelerometers after extending pre/post-trigger capture; use signed axes and several damping values. Match or regress on input SRS rather than divide unrelated maxima.
2. **Band-limited transfer function with coherence.** Best for identifying where geometry changes dynamics if the system is approximately linear. Requires longer records, adequate input energy, window checks, and replicated cross-spectral estimates. Existing 20 ms records permit a rough audit but not a qualified frequency response function.
3. **Output peak at fixed measured incident velocity and input pulse.** Simple and interpretable for protecting a payload. Requires a photogate/encoder and tight input control; available acceleration data alone cannot guarantee fixed input.
4. **Damping ratio from per-axis ringdown.** Useful secondary descriptor after modes are validated. Requires 50–100 ms capture and a mount/mass-loading check. It is not itself energy absorbed in the impact.
5. **Incident/rebound kinetic-energy loss or force–displacement work.** This is the direct objective for energy absorption. It requires hardware: velocity before/after impact, known moving mass, and preferably force plus displacement. It should outrank all acceleration proxies if energy absorption is the actual design goal.
6. **Transmitted impulse or Δv ratio from the present accelerometers.** Low confidence because the sensors are at different points/axes and baselines dominate integrals. Needs validated rigid-body velocity channels and longer records.
7. **Energy dissipated per structural cycle from current acceleration alone.** Not identifiable. It requires modal mass/stiffness or collocated force–velocity/displacement information.

SAE J211/1:2022 addresses performance of the whole measurement channel; selecting nominal Butterworth cutoffs does not by itself demonstrate channel compliance ([SAE J211/1](https://saemobilus.sae.org/standards/j2111_202208-instrumentation-impact-test-part-1-electronic-instrumentation)). ASTM D3332 is relevant as a shock-machine product-fragility framework, but its purpose is fragility characterization, not validation of this peak-ratio objective ([ASTM D3332-99(2023)](https://store.astm.org/d3332-99r23.html)). ASTM D7136/D7136M concerns drop-weight damage resistance of fiber-reinforced polymer matrix composite plates and is not directly applicable to a tensegrity cell ([ASTM D7136/D7136M-25](https://store.astm.org/d7136_d7136m-25.html)). IEST-RD-DTE012 is relevant general guidance for dynamic data acquisition and analysis ([IEST-RD-DTE012](https://www.iest.org/Standards-RPs/Recommended-Practices/IEST-RD-DTE012)).

## 9. Side inferences

### Earlier bimodal five-drop run

The raw five-drop records were not attached, so the stated mechanism cannot be independently tested. Proximity in the two-dimensional input-peak/pulse-width plane is not identifying. Sheet-interface seating, specimen seating, plate tilt, drop-height variation, temperature, partial contact, and alignment can all move a drop along a severity-duration curve. “Consistent with interface seating” is supportable; “explained by interface seating” is not.

### PU-era versus felt-era comparability

The claimed monotonic T-duration relation does not survive baseline correction. Still, peak-ratio T depends on input pulse spectrum and processing band by construction, so values from different absorber stacks should not be pooled without input conditioning. That methodological warning survives; the claimed empirical monotonic law and its Welch p-values do not.

## 10. Final verdict in the requested order

1. **Numbers not reproduced:** raw CH5 and the original table reproduce under the supplied full-record-median pipeline. Under a defensible pre-trigger baseline, CFC-180 and CFC-1000 output peaks, T means/CVs, widths, and Δv change materially, especially for B–D. The 450–800 Hz percentages reproduce exactly only under a one-bin nonlinear-resultant estimator and are not robust.
2. **Grounds for B that survive:** none survives as sufficient selection evidence. Ground 4 partly survives as a descriptive warning against A. Ground 1 retains only the narrow fact that B is much less drift-prone than A in CFC-1000. Grounds 2 and 3 fail.
3. **Choice:** **none of these; the sweep cannot decide.** If “energy absorption” is the objective, the current question is also malformed because T is not an energy metric.
4. **Single cheapest risk-reduction experiment:** the 20-drop randomized two-geometry × A/B crossover described in Section 5, with a common trigger, at least 2 ms pre-trigger, 50–100 ms post-trigger, and prespecified input-conditioned SRS/band-transfer outcomes. It directly tests discrimination before spending 20 Bayesian-optimization designs on an objective that may mostly report rigid-body transmission.

## Limitations

- One specimen, one block per arrangement, fixed order, trigger and elapsed-time confounding.
- No sensor, mount, key-seat, or specimen masses; no sensor-off or added-mass control.
- Prior 519–549 Hz ringdown files and the earlier five-drop raw records were not attached.
- The first ~0.39 ms is pre-trigger, but A's CFC-180 half-maximum onset still predates the record.
- Frequency estimates are limited by a 20 ms record and ~14 ms usable ringdown.
- Public standard pages establish scope and identity; paywalled clause-level compliance was not audited. This report does not claim formal compliance or noncompliance.
- Correlations and coherence do not establish causal mechanisms or geometry sensitivity.

## Discretionary analytical decisions

- Used the median of the first 0.10 ms as baseline because raw inspection showed it preceded the trigger crossing; tested 0.05–0.30 ms and tail/full-record alternatives.
- Used two-pole forward-backward Butterworth filters at 300 and 1667 Hz to match the supplied CFC implementation closely while separating baseline effects from filter-definition effects.
- Used independent input and output peak searches in the first 12 ms rather than forcing synchronous peaks.
- Used interpolated full width at half maximum for pulse duration and flagged left-censored widths.
- Reported maximum absolute cumulative CH5 velocity over 0–12 ms as captured Δv, while explicitly declining to interpret it as incident speed or absorbed energy.
- Used CV and ordinary t intervals descriptively; did not treat them as arrangement-level inferential intervals.
- Used a Tukey 20% taper and summed signed-axis spectral energies for the primary spectral sensitivity check; also tested rectangular and Hann windows.
- Used 2%, 5%, 10%, and 20% damping conceptually for SRS sensitivity and reported 5% as the central engineering example.
- Set $\alpha=0.05$ for quoted exploratory tests; no multiple-comparison-adjusted discovery claims were made because the design does not support treatment inference.
- Proposed A and B, rather than all four stacks, for the cheapest discrimination screen because C/D add an interface and did not show a unique repeatability advantage; this is a cost judgment, not a conclusion that C/D are inferior for geometry discrimination.
