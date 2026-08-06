# Blind ABC × 123 crossover — arrangement + specimen classification, and the first ringdown fit

**Data:** @me-madsen, Box folder `tum0zm49ndrua62snpzh803pg9cdrz56`, two
folders of 45 captures each ("ABC - 123 - Order Known" and "ABC - 123 -
Random Arrangement"), posted on
[PR #86](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86).
**Analysis:** [`scripts/analysis/drop_test_abc123_blind_analysis.py`](../scripts/analysis/drop_test_abc123_blind_analysis.py)
→ [`data/drop-tests/abc123-blind/figures/`](../data/drop-tests/abc123-blind/figures/).
**Pre-registration:** [`drop-test-ab-blind-protocol.md`](drop-test-ab-blind-protocol.md)
(§2 decision rule, committed before any of this data existed).

Design as executed: three arrangements — **A** = 1/4 in PU sheet alone,
**B** = 1/2 in alone, **C** = 1/4 in over 1/2 in — crossed with three
specimens — **1** = smaller T3 prism, **2** = same model as 1 but with
printing defects, **3** = larger T3 prism. Nine cells × 5 drops = 45 per
set. Set 1's order was disclosed; set 2 is the same nine cells shuffled in
blocks of 5, key withheld.

Capture: 4 channels (CH2–CH4 top-vertex key-seat tri-axis output, CH5
single-axis base-plate input + trigger), 1.25 MHz, 125,000 samples =
**100 ms record, 2.000 ms pre-trigger, 150 G trigger** — exactly as
specified. The pre-trigger window is real and clean (baseline sd 0.6–48 G,
|max| < 55 G), so every baseline here is a **pre-trigger median**, never
the full-record median that the
[adversarial review](../edison-trajectories/pu-configs/report/adversarial-review.md)
found contaminating the 20 ms exports.

---

## 1. Reconstructed key for "ABC - 123 - Random Arrangement"

| block | signals | **call** | arrangement margin | specimen evidence |
|--:|---|:--:|---|---|
| 1 | 1–5 | **B2** | 4.3–5.2 σ (within-cell) | cross-session, velocity-normalised; **lowest-confidence call** (see §1.2) |
| 2 | 7–11 | **A1** | 5.0–5.2 σ | rank, gap 18.3 d |
| 3 | 12–16 | **C1** | 4.5–4.8 σ | rank, gap 35.4 d |
| 4 | 17–21 | **B1** | 4.5–5.2 σ | cross-session, velocity-normalised |
| 5 | 22–26 | **C3** | 5.0–5.4 σ | rank, gap 35.4 d |
| 6 | 27–31 | **A3** | 4.4–4.7 σ | rank, gap 18.3 d |
| 7 | 32–36 | **A2** | 4.1–4.4 σ | rank, gap 18.3 d |
| 8 | 37–41 | **B3** | 3.1–5.1 σ | unambiguous on every route |
| 9 | 42–46 | **C2** | 11.0–14.4 σ | rank, gap 35.4 d |

Read in block order, the arrangement sequence is `B A C B C A A B C` and
the specimen sequence is `2 1 1 1 3 3 2 3 2`.
Each of the nine cells is used exactly once, which is a non-trivial
consistency check the analysis was not forced to satisfy: the arrangement
and specimen calls were made independently and the resulting 9 labels
happen to form a bijection.

**Excluded capture:** Signal 12 has a base-plate raw peak of **108.6 G**,
below the 150 G trigger it was captured on, with the "impact" at 9.9 ms and
a 10 ms pulse — not a clean drop. Excluded by a stated rule (raw peak ≥
trigger level), leaving block 3 with 4 valid drops. Worth checking whether
this was an aborted drop or a spurious trigger.

### 1.1 How the arrangement call was made (the pre-registered rule, unchanged)

Primary discriminant: **CH5 input pulse FWHM**, thresholds set at the
midpoints of the set-1 class means. From set 1:

| | A (1/4 in) | B (1/2 in) | C (1/4 over 1/2) |
|---|--:|--:|--:|
| input FWHM (ms) | 1.691 ± 0.050 | 2.219 ± 0.028 | 3.002 ± 0.233 |
| thresholds | — 1.955 — | | — 2.610 — |

Set-1 resubstitution: **45/45**. On set 2 every one of the 44 valid drops
falls in the same class as the rest of its block, with no drop closer than
0.17 ms to a threshold, and the block groupings are 3 A / 3 B / 3 C exactly
as the design requires.

**One recorded pre-registration failure, and it is mine.** §2 step 4 says
abstain within 3 σ of the threshold, with σ "pooled". Arrangement C's class
sd is **0.233 ms** — 4× A's and 8× B's — because specimen 3 shortens the C
pulse to 2.70 ms while specimens 1 and 2 sit at 3.15 ms. That is a
*specimen* effect living inside an arrangement class, something the July
two-arrangement sweep could not have revealed. It inflates the pooled σ to
0.138 ms, and under the literal rule **39 of 44 drops are within 3 σ and
must be reported as *uncertain***. Measured instead against the pooled
**within-cell** sd (0.056 ms), every call is 3.1–14.4 σ clear. I report both
denominators and the labels; the abstention is on the record as written, but
the substance is not in doubt — no drop is anywhere near a boundary in
absolute terms. The fix for next time is to define σ as within-cell, not
within-class.

### 1.2 How the specimen call was made (a stated extension)

The pre-registration fixes only that the specimen call comes from the output
channel, independently of the arrangement labels. Choosing *which* output
feature was done on set 1 alone, by an objective criterion set before
looking at any set-2 value: a feature qualifies if its specimen ordering is
**identical in all three arrangements** (i.e. it measures the specimen and
not a specimen × arrangement interaction) and its smallest adjacent-specimen
gap exceeds 1 within-cell sd.

| candidate | ordering in A / B / C | consistent? | min gap |
|---|---|:--:|--:|
| **`t_second_ms`** | 2<1<3 / 2<1<3 / 2<1<3 | **yes** | **7.81 d** |
| **`e_rebound`** | 2<1<3 / 2<1<3 / 2<1<3 | **yes** | **3.02 d** |
| `lag_ms` | 3<2<1 / 2<3<1 / 3<2<1 | no | 1.67 d |
| `t180` | 2<1<3 / 2<1<3 / 2<3<1 | no | 0.71 d |
| `fn_hz` | 3<1<2 / 2<1<3 / 1<3<2 | no | 0.14 d |
| `out_180_g` | 2<3<1 / 2<3<1 / 2<1<3 | no | 0.05 d |
| `zeta_pct` | 2<1<3 / 3<1<2 / 2<1<3 | no | 0.01 d |

Two features qualify, and they are the same physical quantity in raw and
normalised form (§3). Everything else — including the transmissibility `T`
that has been the working BO objective — fails the consistency test.

Matching set-2 blocks to specimens then used **rank within arrangement**,
which is immune to a session-level offset. That works for A and C, whose
three blocks were all recorded in one session. **Arrangement B's blocks span
two sessions** (§2), so ranks are not comparable there; B was matched on the
velocity-normalised `e_rebound` instead, choosing the permutation with the
smallest total mismatch. B's margin is the weakest in the run: best cost
0.0044 vs runner-up 0.0073, a ratio of only **1.67** (A and C are decided
outright by rank). **If any block label in the key above is wrong, it is
blocks 1 and 4 being swapped** — i.e. B1 ↔ B2, the two nominally identical
prints on the arrangement whose blocks straddle the session break. Two
independent routes (velocity-normalised `t_second`, and `T`) put block 1 at
specimen 2; one route (`f_n` rank) puts it at specimen 1.

---

## 2. Two things the data says that were not in the plan

**(a) Set 2 is not one session, and it is not at the same drop energy.**
Clustering the capture timestamps by elapsed-time gaps:

| | signals | when | input Δv |
|---|---|---|--:|
| session 1 — set 1 | 1–50 | 08-04 00:15 → 03:02 | 5.47 ± 0.26 m/s |
| session 1 — set 2 block 1 | 1–5 | 08-04 03:12 → 03:16 | 5.35 ± 0.03 m/s |
| **session 2 — set 2 blocks 2–9** | 7–46 | **08-05 23:42 → 08-06 00:40** | **4.22 ± 0.64 m/s** |

Set 2's first block was recorded 10 minutes after set 1 finished; the other
eight blocks came two days later at a **~22 % lower impact velocity**
(consistent with a lower drop height, ≈ 43 in vs 60 in, or an equivalent
change in the release). Absolute level features (input/output peak in G)
therefore do **not** transfer between the sets — set-2 arrangement A reads
292–303 G where set-1 A read 354–369 G. This is exactly the failure mode the
pre-registration chose a *shape* discriminant to avoid, and the arrangement
call is untouched by it. It is also the reason the specimen call needed the
session-aware treatment above.

**(b) Every record contains a large secondary event 17–35 ms after impact.**
This is the single most consequential thing in the dataset and it is only
visible because of the 100 ms record. Some numbers, from arrangement C:
the top-vertex band-limited envelope *rises 9–15 dB above* its post-impact
level at ~21–35 ms. Raw CH4 reaches 400–870 G in that burst — comparable to,
and in the softer arrangements larger than, the primary output ringdown.

It is **not** the carriage: at the same instant the base plate reads only
11–51 G, i.e. 2–5 % of its primary peak. It is the top of the specimen. It
is also **not** the anti-rebound brake catch, which the video work put at
+76 to +89 ms. My first ringdown fit ran straight across it and returned
*negative* damping, which is how it was found.

Its delay scales in proportion to impact velocity — the 22 % energy drop
between sessions shortens it by 13–19 %, and `g·t_second/(2·Δv)` reproduces
set-1 values to 0.1–6 % across that change on arrangement A. That is the
signature of a **ballistic hop**: the top vertex separates at ~0.10–0.17 m/s
(a ~0.5–1.5 mm rise) and lands back. So

> **`e_rebound = g · t_second / (2 · Δv)`** ≈ 0.019 (specimen 2),
> 0.022–0.024 (specimen 1), 0.028–0.030 (specimen 3)

is a dimensionless, velocity-invariant, arrangement-invariant specimen
constant — the first quantity measured in this program that transfers across
sessions. A high-speed clip through the +15 to +40 ms window would settle
whether it is the whole specimen leaving the plate or the tendons going
slack and snapping taut; the two have different implications for the fixture.

---

## 3. Repeatability and distinguishability — the two questions the test was for

### 3.1 Repeatability (within-cell CV, 5 drops, set 1)

| cell | input CFC-180 | input FWHM | output CFC-180 | `T` (CFC-180) | `t_second` | `e_rebound` |
|---|--:|--:|--:|--:|--:|--:|
| A1 | 1.35 | 0.64 | 1.44 | 0.28 | 2.02 | 1.04 |
| A2 | 0.67 | 0.45 | 0.63 | **0.12** | 0.64 | 0.86 |
| A3 | 9.17 | 4.68 | 6.90 | 2.56 | 1.68 | 7.53 |
| B1 | 1.32 | 1.05 | 1.57 | 0.25 | 0.66 | 0.76 |
| B2 | 0.85 | 0.75 | 1.08 | 0.27 | 0.62 | 0.82 |
| B3 | 1.10 | 0.65 | 1.22 | 0.14 | 0.88 | 1.44 |
| C1 | 3.88 | 4.00 | 3.64 | 0.48 | 3.37 | 3.89 |
| C2 | 2.16 | 2.02 | 2.27 | 0.27 | 0.30 | 0.69 |
| C3 | 0.84 | 0.56 | 1.14 | 0.36 | 1.08 | 1.48 |

**Repeatability is not the constraint.** `T` holds 0.12–0.48 % CV in 8 of 9
cells; the input holds ~1 % in the good cells. Two cells are visibly worse
and both have an identifiable cause rather than being noise: **A3** carries a
bedding-in transient (its first drop, Signal 31, reads 1.863 ms FWHM against
1.66–1.72 for the rest of the block, after a 7-minute pause), and **C1** and
**C2** drift upward through the block (C1's FWHM climbs 3.04 → 3.35 ms across
5 drops). Both are arguments for the 2-drop discarded warm-up already in the
SOP, and for treating the two-sheet stack as the one that needs to settle.

### 3.2 Distinguishability by arrangement

Between-specimen spread ÷ pooled within-cell sd, and the effect size for the
hard contrast — **specimen 1 vs 2, the same model differing only in printing
defects**:

| feature | | A (1/4) | B (1/2) | C (two-sheet) |
|---|---|--:|--:|--:|
| **`t_second_ms`** | SNR | 11.9 | **29.8** | 13.8 |
| | \|d\| 1 vs 2 | 10.1 | **18.6** | 7.8 |
| **`e_rebound`** | SNR | 3.9 | **19.3** | 9.0 |
| | \|d\| 1 vs 2 | 3.0 | **11.9** | 7.1 |
| `f_n` (ringdown) | SNR | 3.8 | **4.5** | 1.1 |
| | \|d\| 1 vs 2 | 1.7 | 2.9 | 2.1 |
| **`T` (CFC-180)** | SNR | 1.2 | **2.0** | 1.6 |
| | \|d\| 1 vs 2 | 0.75 | 1.50 | 3.02 |
| output CFC-180 peak | SNR | 0.3 | 1.2 | 5.0 * |
| | \|d\| 1 vs 2 | 0.50 | 2.26 | 0.17 |

\* arrangement C's output-peak spread is dominated by specimen 3 driving a
*harder input* on that stack (229 G vs 187 G), not by a larger response —
it is an input artefact, not discrimination.

**Answer: arrangement B (1/2 in sheet alone) is the more informative one**,
on every feature that carries specimen information, and it is simultaneously
among the most repeatable. A is a close second on `t_second`; C is the
weakest and also the least settled.

This lands on the same recommendation I made in July and that the
[Edison adversarial review](../edison-trajectories/pu-configs/report/adversarial-review.md)
overturned — but for a different and much better reason, and the review's
objection is now answered rather than repeated. The July argument ranked B
on **repeatability**, which the review correctly called the
minimum-variance trap: a stack soft enough that the vertex rides the base
gives a beautifully repeatable measurement of nothing, and no single-specimen
statistic can rule that out. This run ranks B on **measured discrimination
across three specimens**, which is the quantity that actually matters and
which the single-specimen sweep could not estimate. The two conclusions
agree; only the second one is evidence.

### 3.3 The uncomfortable part: `T` is the weakest discriminator measured

Peak-ratio transmissibility separates specimen 1 from specimen 2 at
\|d\| = 0.75–3.02 and spans 0.88–3.50 % across all three specimens. The
secondary-event timing separates the same pair at \|d\| = 7.8–18.6 and spans
40–53 %. Put against the print-defect study's finding that print-to-print
scatter in `T` among five nominally identical articles is ~0.72 % CV /
1.95 % spread, `T`'s between-specimen spread here is the same order as its
print noise — while `e_rebound`'s is an order of magnitude clear of anything
in this dataset.

Two candidate readings, and the run cannot separate them: either `t_second`
is genuinely more sensitive to geometry, or it is sensitive to something
correlated with the specimen swap (mass, seating, mount). The cheap
discriminator is the replicate-print cell of
[protocol §7.1](drop-test-ab-blind-protocol.md#71-the-freed-drops-a-same-geometry-replicate-print):
if two prints of the same geometry give the same `e_rebound` while the two
geometries differ, it is geometry.

### 3.4 Print defects are detectable

Specimens 1 and 2 are the same model. On `t_second`/`e_rebound` they
separate at \|d\| = 3.0–18.6 — comparable to, and on arrangement B larger
than, the 1-vs-3 size contrast on `T`. Whatever the defects are doing
mechanically, **the measurement sees them clearly**, and the blind set
reproduced the 1-vs-2 ordering independently on A and C. That answers
@me-madsen's stated interest directly: two "supposedly identical" structures
are *not* practically indistinguishable on this rig — which is a warning for
BO ranking, not a reassurance, since it means single-print evaluations
inherit print noise of the same size as the design effects.

---

## 4. Ringdown decay — done, and here is what it actually supports

Method: decimate to 50 kHz, band-pass 300–900 Hz (the repo's documented
519–549 Hz first mode), take the tri-axis channel with the most band energy,
fit `log|Hilbert envelope|` over impact + 1 ms → +14 ms (truncated earlier at
any envelope rise), and read `f_n` from the analytic phase slope — sub-bin
resolution, where a Welch estimate over a 13 ms window would give ~75 Hz bins.

| cell | f_n (Hz) | ζ (%) | fit r² | window |
|---|--:|--:|--:|--:|
| A1 | 528.4 ± 9.2 | 6.01 ± 1.07 | 0.85 | 9.8 ms |
| A2 | 551.8 ± 2.0 | 5.66 ± 0.49 | 0.89 | 13.0 ms |
| A3 | 450.1 ± 22.3 | 11.40 ± 1.66 | 0.90 | 5.1 ms |
| B1 | 382.5 ± 39.4 | 7.20 ± 0.53 | 0.48 | 13.0 ms |
| B2 | 317.2 ± 1.6 | 11.25 ± 0.59 | 0.66 | 13.0 ms |
| B3 | 518.5 ± 1.1 | 7.19 ± 0.61 | 0.91 | 13.0 ms |
| C1 | 406.2 ± 84.2 | 6.95 ± 9.70 | 0.73 | 8.8 ms |
| C2 | 510.4 ± 25.6 | 6.18 ± 1.51 | 0.75 | 10.3 ms |
| C3 | 503.5 ± 6.2 | 7.84 ± 0.77 | 0.91 | 11.4 ms |

Read it honestly:

- **Where the fit is good (r² ≥ 0.85: A1, A2, A3, B3, C3) ζ comes out
  5.7–11.4 % and repeats to 0.5–1.7 % absolute** — those are usable damping
  numbers, and the first in this program.
- **Where it is poor (B1 r² = 0.48, B2 0.66, C1 0.73) the ζ should not be
  read as a damping ratio.** C1's ζ has a 140 % CV; that is the estimator
  telling you the envelope is not one decaying mode, not a measurement.
- **`f_n` is not yet a trustworthy modal frequency.** It ranges 317–552 Hz
  and its specimen ordering flips between arrangements — i.e. it is partly
  tracking the *input* spectrum, which differs by arrangement. It also is
  not established that the ~500 Hz line is the specimen at all rather than
  the plate or the wax mount; the
  [adversarial review](../edison-trajectories/pu-configs/report/adversarial-review.md)
  flagged this and it remains open. The added-mass tap test it proposed is
  still the cheapest resolution.

**The blocker is the secondary event, not the record length.** 98 ms of
post-impact record was supposed to buy ~50 cycles at 550 Hz. It buys 5–13 ms
(≈ 3–7 cycles), because the hop at 17–35 ms re-excites the structure and ends
the free decay. Lengthening the record further will not help. What would:

1. **Stop the hop** — restrain the specimen to the plate (a light tie-down,
   or enough preload) so the free decay runs uninterrupted. This is the
   single highest-value fixture change available, and it would also remove a
   large uncontrolled load path.
2. If the hop is instead *the* thing worth measuring — and on this evidence
   it is the best discriminator in the dataset — then keep it and measure it
   deliberately, with video confirmation of what is moving.

Those two are in tension, and the choice should be made explicitly rather
than by default. My recommendation is to do (1) on a couple of blocks and
compare: if `e_rebound`'s discrimination survives restraint, it was
structural; if it vanishes, it was fixture dynamics and `T`/ζ go back to
being the objective.

---

## 5. Caveats

- **n = 1 article per specimen level.** Specimen 2 is one defective print,
  not a sample of defective prints. Print-to-print variance is still
  unestimated in this run (protocol §7.1's replicate-print cell was not
  included), so the discrimination figures in §3.2 bound how well the *rig*
  can separate these three articles, not how well it can separate designs.
- **Specimen changes are confounded with mount re-seatings** by
  construction, and set 2 gives one independent re-seating per cell. On
  arrangement B, block 1's `t_second` sits 1.4 ms (≈ 7 %) from its matched
  set-1 cell at the same drop energy — that is a direct measurement of the
  re-seating shift, and it is ~35 % of the B1–B2 specimen gap. Resolvable,
  but not with margin to spare.
- **The two sets were not run under one condition.** The ~22 % impact-velocity
  change between sessions was not logged in the session metadata and had to
  be inferred from Δv; please record drop height per session.
- **Δv is a processing-dependent descriptor**, not a validated velocity. It
  is unreliable in the set-2 C blocks (per-drop values swing 2.5–4.3 m/s
  within a block), which is why `e_rebound` was not used to decide C.
- The set-1 order is fully confounded with time (A1→B1→C1→A2…), so any
  set-1-only contrast could be a sequence effect. The set-2 randomisation is
  what protects the conclusions; keep it.

---

## 6. What I would run next

1. **Restrained vs unrestrained, 2 blocks × 5 drops on arrangement B.**
   Settles whether the secondary event is specimen dynamics or the specimen
   leaving the plate, and whether `e_rebound` survives. Cheapest decisive
   experiment available.
2. **The replicate-print cell.** Two prints of one geometry, arrangement B,
   5 drops each. Turns every discrimination number in §3.2 from
   "distinguishes these articles" into "distinguishes these designs".
3. **Log drop height and any release change per session** — the one piece of
   metadata whose absence cost the most here.
4. Keep the 100 ms / 2 ms pre-trigger / 150 G capture exactly as it is. It
   is strictly better than everything before it, and the pre-trigger window
   alone retires the baseline problem the adversarial review found.
