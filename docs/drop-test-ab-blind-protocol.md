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
channel would have passed cleanly with that bug fully present. Nor does it
test **discrimination** — whether an arrangement lets geometry differences
exceed noise — because that requires more than one specimen.

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
