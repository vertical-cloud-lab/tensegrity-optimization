# Blind A/B arrangement test — pre-registered analysis plan

**Status:** pre-registration, written **before** any set-2 data exists.
Proposed by @me-madsen on
[PR #86](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5172705873).

The point of committing this before the data arrives is that the decision rule
cannot be tuned after the fact. If the rule below misclassifies, that is a
recorded miss, not something to be re-derived.

Related: [`drop-test-pu-configs-analysis.md`](drop-test-pu-configs-analysis.md)
(superseded recommendation) ·
[`edison-trajectories/pu-configs/report/adversarial-review.md`](../edison-trajectories/pu-configs/report/adversarial-review.md)
(the adversarial review that called for a randomized crossover).

---

## 1. Design as proposed

**Capture:** 100 ms record, 10 % pre-trigger, one trigger level for all drops.

**Set 1 — labeled.** 10 drops arrangement A (1/4 in PU sheet alone), then
10 drops arrangement B (1/2 in PU sheet alone). Order disclosed. Used to fit
the classifier thresholds *in-session*.

**Set 2 — blind.** 20 drops as four contiguous blocks of 5: two A blocks and
two B blocks in randomized order, known to the operator, withheld from the
analysis. The analysis emits a predicted order; the operator scores it.

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
5. Only after per-drop labels are fixed, read off the block order. If the
   per-drop labels are not consistent with four contiguous blocks of 5, report
   the raw per-drop labeling as-is rather than snapping it to the expected
   design.

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
2. **One trigger level throughout** (~150 G). The July sweep changed the
   trigger between blocks, confounding arrangement with trigger. At 150 G,
   B has ~3.3× margin on its minimum observed raw peak and A ~8.6×.
3. **Reconcile the pre-trigger numbers.** 10 % of a 100 ms record is 10 ms, not
   2 ms. 10 ms is the better setting and comfortably exceeds the ≥ 2 ms ask —
   just confirm which the instrument is actually applying.
4. **Randomize with an RNG and record the key before the first drop.**
5. **Do not disturb the accelerometer mount between sets.** Mount re-seating
   has produced ~2.3 % shifts in `T`, larger than anything being measured; log
   it if it happens.
6. **Log warm-ups rather than discarding them.** A bedded in at +4.6 %/drop
   over its July block; keeping those captures labeled lets the transient be
   used or excluded at analysis time.

---

## 5. Expected export properties (to be checked on arrival)

The TP4 appears to hold a fixed 25,000-sample buffer — 200 ms at 125 kHz and
20 ms at 1.25 MHz both export 25,000 samples. A 100 ms record should therefore
arrive at **~250 kHz, 25,000 samples**, which is ~31× the SAE J211 minimum for
CFC-1000. If it differs, the analysis notes it rather than assuming.

Two consequences of the longer record, both anticipated:

- **The brake catch will be in-record.** Video work put the anti-rebound brake
  catch at +76 to +89 ms after impact, so a 90 ms post-trigger window may
  capture it as a second transient near the end of the record. Peak-finding is
  windowed near the trigger, so this is informative rather than a problem.
- **Damping becomes measurable.** 90 ms of post-impact record is ~50 cycles at
  the ~550 Hz output band, enough to fit a ringdown decay. This is the largest
  scientific gain in the proposal: ringdown damping is a defensible
  energy-dissipation metric, unlike the peak ratio `T`.
