# Blind A/B arrangement test — pre-registered analysis plan

**Status:** pre-registration, written **before** any set-2 data exists.
Proposed by @me-madsen on
[PR #86](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5172705873).

**Amendment 1 (still before any data exists)** — @me-madsen revised the design in
[a follow-up comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5172815953):
set 2 becomes **20 fully randomized drops** rather than four contiguous blocks
of 5, two specimens of different geometry are in play, and the capture settings
are fixed (100 ms, 1.25 MHz, 125,000 samples, 2 % = 2 ms pre-trigger, 150 G
trigger throughout). §1 and §6 record the revision; the §2 decision rule is
unchanged except that the block-order readout in step 5 no longer applies.
Note the amendment strictly *removes* information available to the analysis
(no block structure to lean on), so it cannot flatter the result.

**Amendment 2 (still before any data exists)** — @me-madsen proposed an 80-drop
variant in
[a further comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5172937746):
back to blocks of 5, four arrangements (A, B, C, D) × two specimens, one
labeled set of 8 blocks in fixed order and one blind set of the same 8 blocks
shuffled. §7 records the decidability analysis for that variant — in
particular the prediction, made here before any data exists, that **C and D
cannot be told apart from the input channel** and would be reported as
*uncertain* under the §2 step-4 abstention rule.

The point of committing this before the data arrives is that the decision rule
cannot be tuned after the fact. If the rule below misclassifies, that is a
recorded miss, not something to be re-derived.

Related: [`drop-test-pu-configs-analysis.md`](drop-test-pu-configs-analysis.md)
(superseded recommendation) ·
[`edison-trajectories/pu-configs/report/adversarial-review.md`](../edison-trajectories/pu-configs/report/adversarial-review.md)
(the adversarial review that called for a randomized crossover).

---

## 1. Design as proposed

### 1.1 Terminology (the two factors are independent)

- **Arrangement** — the polyurethane absorber stack under the carriage.
  **A = 1/4 in sheet alone**, **B = 1/2 in sheet alone**. A property of the
  *rig*; it sets the severity and duration of the input pulse.
- **Geometry / specimen** — the printed T3 article being dropped. A property of
  the *article under test*; it sets how the top vertex responds to that pulse.

They are crossed, not alternatives: any specimen can be dropped on any
arrangement. "2 arrangements × 2 geometries × 5 drops" means the four cells

| | arrangement A (1/4 in) | arrangement B (1/2 in) |
|---|---|---|
| **specimen 1** | 5 drops | 5 drops |
| **specimen 2** | 5 drops | 5 drops |

for 20 drops total. This is what makes the run a *crossover*: it measures
whether the specimen difference shows up on both arrangements, and whether one
arrangement shows it more clearly — the discrimination question the adversarial
review said the single-specimen sweep could not answer.

### 1.2 Capture (as fixed by the operator)

100 ms record · 1.25 MHz · 125,000 samples · 2 % (= 2 ms) pre-trigger ·
**150 G trigger for every drop**. The arithmetic is self-consistent
(1.25 MHz × 100 ms = 125,000 samples; 2 % × 100 ms = 2 ms), and 2 ms of
pre-trigger meets the ≥ 2 ms requirement while leaving 98 ms of post-impact
record for the ringdown fit. Expected export size ≈ 9 MB/drop across 4 channels
(5× the 20 ms exports).

### 1.3 Sets

**Set 1 — labeled.** 10 drops arrangement A, then 10 drops arrangement B.
Order disclosed. Used to fit the classifier thresholds *in-session*. If the
specimen axis is also to be called blind, set 1 must cover all four cells of
§1.1 (5 labeled drops per cell), otherwise there is no labeled data from which
to fit a specimen threshold.

**Set 2 — blind.** 20 drops in **fully randomized per-drop order** (amendment
1; e.g. `ABBBBAABA…`), the key known to the operator and withheld from the
analysis. The analysis emits a per-drop label sequence; the operator scores it.
Per-drop randomization is a strict improvement over the original blocks of 5:
it breaks the confound between arrangement and elapsed time / sheet history,
gives each drop an independent re-seating of the stack, and lowers the
guess-alone pass probability from 1-in-6 to ~1-in-10⁶.

---

## 2. Pre-registered decision rule

All features are computed from the **input** channel (CH5, base plate) only.
Baseline is the channel-wise median of the pre-trigger window (per the
adversarial review's finding that a full-record median is contaminated by the
ringdown). Peaks are located in a window around the trigger, not by global max.

**Primary discriminant — CH5 input pulse width** (half-amplitude duration of
the CFC-180 input pulse). Chosen because it is a *shape* metric: it is
invariant to overall level, so session-to-session drift, sheet bedding-in and
trigger-level changes cannot move it. In the 40-drop July sweep it gave the
cleanest split of any feature, with **no overlap**:

| feature | A (1/4 in) | B (1/2 in) | separation | overlap |
|---|--:|--:|--:|:--:|
| **input pulse width (ms)** | **1.656 ± 0.026** (range 1.599–1.687) | **2.247 ± 0.029** (range 2.205–2.300) | **21.5 σ** | none |
| hardness ratio CFC-1000/CFC-180 | 2.191 ± 0.074 | 1.316 ± 0.033 | 15.4 σ | none |
| input CFC-180 peak (G) | 370.6 ± 5.4 | 261.4 ± 3.9 | 23.3 σ | none |
| input raw peak (G) | 2050 ± 298 | 543 ± 29 | 7.1 σ | none |

**Confirmatory features (must agree with the primary):** the dimensionless
hardness ratio and the CFC-180 input peak. Both are also level- or
shape-robust; the raw peak is used only as a tie-breaker because A's raw peak
drifts +4.6 %/drop.

**Procedure.**

1. Fit each feature's threshold as the **midpoint of the two set-1 class
   means**, from set 1 only. (Validated on the July sweep: 0/20 errors on all
   three features, worst-case margin 6.2–10.3 σ.)
2. Classify **each set-2 drop independently**. No use of block structure, no
   use of adjacency, no use of the July absolute levels.
3. Report a per-drop label plus its margin in pooled σ on the primary feature.
4. **Prespecified abstention:** any drop landing within 3 σ of the threshold on
   the primary feature is reported as *uncertain*, not guessed.
5. ~~Only after per-drop labels are fixed, read off the block order.~~
   **Superseded by amendment 1:** set 2 is fully randomized per drop, so there
   is no block structure to read off. The reported answer is the raw 20-label
   sequence in capture order. No smoothing, no majority vote over neighbours,
   and no adjustment toward an assumed 10/10 split — if the labels come out
   13 A / 7 B, that is what is reported.
6. If a specimen classifier was fitted (set 1 covering all four cells), the
   specimen call is made from the **output** channel and reported as a second,
   independent 20-label sequence. Arrangement labels are not used to inform
   specimen labels or vice versa.

**Prediction of record:** 20/20 correct, with margins > 5 σ.

---

## 3. What this test does and does not establish

**Does:** confirms the input-side pipeline reads the absorber configuration
correctly, and — more usefully — establishes that an arrangement is a
*reproducible* variable across independent re-seatings of the stack. Every
absorber dataset in this repo so far ran one contiguous block per arrangement,
which is exactly why the review found zero arrangement-level degrees of
freedom. Two separated blocks per arrangement is the first design here that
replicates the absorber factor at the block level.

**Does not:** probe the failure mode that actually bit the last analysis. The
error Edison found was an *output-side processing* error (a full-record-median
baseline biasing `T`); a blind arrangement classification driven by the input
channel would have passed cleanly with that bug fully present.

**Discrimination** — whether an arrangement lets geometry differences exceed
noise — is testable **only if** the two specimens of amendment 1 are randomized
independently of arrangement, i.e. all four cells of §1.1 are populated. If
specimen and arrangement change together, the two factors are perfectly
confounded and the run reverts to a confirmation test. Either way the run
cannot estimate print-to-print variance (that needs replicate prints, measured
at ~0.72 % CV in the print-defect study), so it bounds discrimination from
above, not from below.

---

## 4. Recommended amendments

1. **Two specimens, not one.** Make set 2 `2 geometries × 2 arrangements × 5
   drops`. Same 20 drops, but it becomes the crossover the review asked for and
   yields the geometry × arrangement interaction. The blind test survives
   intact and gets richer: the **input** channel carries arrangement, the
   **output** channel carries specimen, so both can be called blind from
   independent evidence.
2. ✅ **Adopted.** One trigger level throughout (150 G). The July sweep changed
   the trigger between blocks, confounding arrangement with trigger. At 150 G,
   the July minimum raw peaks give **10.8× margin on A and 3.3× on B**.
3. ✅ **Resolved.** The revised setting is 2 % of 100 ms = 2 ms, which is
   arithmetically consistent and satisfies the ≥ 2 ms requirement. The earlier
   suggestion of 10 % is withdrawn: with the record length fixed at 100 ms, a
   smaller pre-trigger fraction buys more post-impact record for the ringdown
   fit, and 2 ms (2,500 samples at 1.25 MHz) is an ample baseline window.
4. **Randomize with an RNG and record the key before the first drop.**
5. **Do not disturb the accelerometer mount between sets.** Mount re-seating
   has produced ~2.3 % shifts in `T`, larger than anything being measured; log
   it if it happens.
6. **Log warm-ups rather than discarding them.** A bedded in at +4.6 %/drop
   over its July block; keeping those captures labeled lets the transient be
   used or excluded at analysis time.

---

## 5. Export properties

**Corrected:** an earlier version of this document inferred that the TP4 holds a
fixed 25,000-sample buffer (200 ms at 125 kHz and 20 ms at 1.25 MHz both export
25,000 samples). The operator's settings — 100 ms at 1.25 MHz = **125,000
samples** — show that record length and rate are set independently. The
sample interval is 0.8 µs, ~156× the SAE J211 minimum sample rate for CFC-1000,
so filtering is unconstrained.

Practical consequence: at ~1.83 MB per 25,000-sample 4-channel CSV, a
125,000-sample capture is **≈ 9 MB**, so 40 drops ≈ 365 MB uncompressed. Zip
per session and upload to Box rather than committing loose CSVs.

Two consequences of the longer record, both anticipated:

- **The brake catch will be in-record.** Video work put the anti-rebound brake
  catch at +76 to +89 ms after impact, so a 90 ms post-trigger window may
  capture it as a second transient near the end of the record. Peak-finding is
  windowed near the trigger, so this is informative rather than a problem.
- **Damping becomes measurable.** 90 ms of post-impact record is ~50 cycles at
  the ~550 Hz output band, enough to fit a ringdown decay. This is the largest
  scientific gain in the proposal: ringdown damping is a defensible
  energy-dissipation metric, unlike the peak ratio `T`.

---

## 6. Revision log

**Amendment 1 — 2026-08-03, before any set-2 data exists.**

| item | original proposal | revised | effect on the test |
|---|---|---|---|
| set-2 order | four contiguous blocks of 5 | 20 fully randomized drops | **harder** — no block structure to lean on; chance pass 1-in-6 → ~1-in-10⁶ |
| specimens | one | two, different geometry | enables the crossover; adds an independent output-side blind call |
| pre-trigger | "10 % (2 ms)" — inconsistent | 2 % = 2 ms at 100 ms | resolved; 98 ms post-impact retained |
| sample rate | assumed ~250 kHz / 25,000 | 1.25 MHz / 125,000 | none analytically; 5× file size |
| trigger | "one level, ~150 G" | exactly 150 G throughout | adopted as recommended |

Open item at the time of writing: whether the two specimens are randomized
**independently of** arrangement (giving the four crossed cells of §1.1) or
swapped together with it. Only the crossed version answers the discrimination
question; if specimen and arrangement are changed together they are perfectly
confounded and neither factor can be attributed.

**Amendment 2 — 2026-08-03, before any set-2 data exists.** The 80-drop
four-arrangement variant, and the C/D decidability analysis of §7. The §2
decision rule is unchanged; §7 only records, in advance, which cells it is
expected to abstain on.

---

## 7. Decidability of a four-arrangement blind set (amendment 2)

Computed from the adversarial review's independently recomputed per-drop
metrics for the July sweep
([`independent_per_drop_metrics.csv`](../edison-trajectories/pu-configs/report/independent_per_drop_metrics.csv),
pre-trigger baseline, 10 drops per arrangement). Pairwise separation of the
arrangements on the primary discriminant, **CH5 input pulse FWHM**:

| pair | Δ (ms) | pooled sd | separation | ranges overlap? |
|---|--:|--:|--:|:--:|
| A vs B | 0.498 | 0.022 | 22.8 σ | no |
| A vs C | 1.634 | 0.047 | 35.1 σ | no |
| A vs D | 1.501 | 0.041 | 36.9 σ | no |
| B vs C | 1.136 | 0.045 | 25.0 σ | no |
| B vs D | 1.004 | 0.039 | 25.5 σ | no |
| **C vs D** | **0.132** | **0.057** | **2.3 σ** | **yes** |

The same pattern holds on every other input feature, and C/D is worse on all
of them: input CFC-180 peak 167.29 vs 167.33 G (**0.01 σ**), input CFC-1000
peak 0.45 σ, hardness ratio CFC-1000/CFC-180 1.21 σ, raw peak 2.40 σ. Every
one overlaps. There is no input-side feature that separates the two stacking
orders.

**Consequence under the committed rule.** A midpoint threshold on pulse FWHM
misclassifies 2 of the 20 July C/D drops, and **no C or D drop exceeds 2.9 σ of
margin** — so §2 step 4 (abstain within 3 σ) would report *every* C and D drop
as *uncertain*. Any C/D drops in a blind set are therefore prepaid abstentions,
not scored calls.

**The 2.3 σ that does exist is not attributable to stacking order.** The two
blocks were sequential (C = signals 22–31, D = 32–41) and drift within them in
*opposite* directions: C +0.0124 ms/drop, D −0.0120 ms/drop. Over ten drops
each that is ±0.12 ms, essentially the entire 0.132 ms block-mean difference.
The implied effect also depends on which drops are compared — first-3 means
differ by 0.053 ms, last-3 means by 0.207 ms, a 4× swing. With one block per
arrangement there are zero arrangement-level degrees of freedom, so this
contrast cannot be assigned to the stacking order rather than to elapsed time
or bedding-in.

**Recorded prediction for the four-arrangement variant:** A and B called
correctly with > 5 σ margins; the two-sheet blocks separated from A and B with
> 20 σ margins but **not** resolved into C vs D, and reported as uncertain.

**Recommendation (made before data exists):** collapse C and D into a single
two-sheet arrangement and prefer the **1/4 in on top** order (July CVs: input
CFC-180 1.6 % vs 3.8 %, `T` CFC-180 1.2 % vs 2.5 % — the harder sheet as the
contact surface is the more repeatable of the two). Retaining one two-sheet
configuration is worthwhile: it gives a third point on the severity–duration
axis (≈ 1.64 / 2.14 / 3.2 ms input pulse), which turns "which arrangement
discriminates best" into a dose–response question rather than a two-way
comparison. Retaining *both* orders spends drops on a contrast the input
channel demonstrably cannot resolve.

### 7.1 The freed drops: a same-geometry replicate print

The binding limit on any discrimination claim is that print-to-print scatter
among nominally identical articles is the same order as the between-geometry
differences being measured (print-defect study: five copies of one geometry
spanned 1.95 % in `T`; the three-structure 60 in "different geometries"
ranking spanned 2.3 %). A run with one article per geometry cannot separate
those two variances, whatever the arrangement.

Adding a **second print of the same geometry** as a third specimen level fixes
this within the same budget, because discrimination becomes a directly measured
ratio: between-geometry response difference ÷ between-print response
difference, per arrangement. Two of the print-defect articles (`cruela`,
`bpx68c` — the two lowest-defect copies) already exist and serve.

An 80-drop layout on that basis, 5 drops per cell, 8 cells, two sets:

| | arrangement A (1/4) | arrangement B (1/2) | arrangement E (1/4 over 1/2) |
|---|:--:|:--:|:--:|
| specimen 1 | 5 | 5 | 5 |
| specimen 1b *(replicate print of 1)* | 5 | 5 | — |
| specimen 2 *(different geometry)* | 5 | 5 | 5 |

Same 80 drops, same 8 blind labels per set. The blind test then becomes
informative rather than confirmatory: **failing to separate 1 from 1b while
separating 1 from 2 is the success case**, since it demonstrates the
measurement responds to geometry and not to print noise. Separating 1 from 1b
as easily as 1 from 2 would show the opposite, and is the outcome that would
invalidate single-print design ranking in the BO campaign.

### 7.2 Mount re-seating is the dominant threat to the specimen call

Changing specimen re-seats the top-vertex accelerometer, and mount re-seating
has produced ~2.3 % shifts in `T` — larger than the specimen differences under
test. This is why **blocks of 5 are the right unit here** and per-drop
randomization of the specimen factor is not recommended (it would inject a
mount re-seat into every drop); amendment 1's per-drop randomization argument
applies to the arrangement factor, where a swap is only a sheet change.

Two consequences to accept in advance:

- Randomize the **block order** with an RNG and record the key before drop 1.
  Each cell then occupies one labeled block and one blind block, separated in
  time, which gives the mount and the stack an independent re-seating per cell
  — the block-level replication every previous absorber dataset lacked.
- If the specimen call fails while the arrangement call succeeds, the leading
  explanation is mount re-seating, not the pipeline. That result would itself
  be first-order: it would mean specimens can only be compared within a single
  mount seating, which constrains how the BO campaign must be sequenced. Log
  every re-seat so the two explanations stay separable.
