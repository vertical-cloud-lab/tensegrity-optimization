# Equipment selection — first-round Instron stiffness tests (issue #49)

This note maps the abstract recommendations from the Edison
LITERATURE_HIGH brief
([`instron-stiffness-9f68e71e-…md`](./instron-stiffness-9f68e71e-c552-4333-aa5c-37de18c8eefd.md))
onto the **actually-available BYU CB 123 tensile-test equipment** that
@sgbaird flagged in
[PR comment 4462547993](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/50#issuecomment-4462547993).

(Drop-tower / impact equipment from issue #28 is out of scope for the
*first* stiffness-only campaign and is covered separately in the
`copilot/add-drop-tower-picture` materials.)

## TL;DR — recommended kit for the first test

| Role | Chosen equipment | Why |
|---|---|---|
| **Test frame** | **1 kip Mini Tensile Tester (CB 123)** | Only frame with both (a) a load cell sized to our specimens and (b) the 36" stroke needed to reach densification on a 25–50 mm specimen if we ever extend the test. |
| **Load cell** | **100 lb cell (≈ 445 N, ±0.25 lb ≈ ±1.1 N)** | Matches the brief's recommended **100–500 N** range for ~5–30 g tensegrity cells in the small-strain regime. Resolution dominates anything our specimens will produce. |
| **Strain measurement** | **MTS AOX optical extensometer** (<2.5 µm res., 2 mm min gauge) | Directly satisfies the brief's *"use a non-contact extensometer / DIC rather than crosshead displacement at sub-mm compliance"* recommendation. The 2 mm min gauge fits even the smallest single-cell specimens. AOX **requires training** — book first-test alongside a trained operator. |
| **Crosshead speed** | Use machine's slow regime (target nominal strain rate per ASTM D1621/E9 norms; e.g. 1 mm/min on a ~25 mm bounding-box height ≈ 6.7 × 10⁻⁴ s⁻¹). The 1 kip frame's 1000 mm/min ceiling is irrelevant for stiffness work. | Standard practice in 8/12 of the brief's published analogs. |
| **Compliance baseline** | Steel-on-steel platens-only run on the 1 kip frame, AOX *off* the specimen, before each session | Subtract from specimen displacement per ASTM E111 logic referenced in the brief. |

## Full machine triage

| Machine | Frame cap. | Best load cell | Stroke | Verdict for issue #49 first-stiffness tests |
|---|---|---|---|---|
| **1 kip Mini Tensile Tester** | 1 000 lb (≈ 4.45 kN) | **100 lb (±1.1 N)** ✅ | 36" (≈ 914 mm) | **PRIMARY.** Best load-cell match (within Edison-recommended 100–500 N window). Long stroke is overkill for stiffness only, but is exactly right when the same frame is later reused for monotonic loading toward densification. |
| 3 kip Acumen | 2 700 lbf (≈ 12 kN) | 675 lbf (≈ 3 kN) — smallest | 2.75" (≈ 70 mm) | **Skip for stiffness.** Smallest available cell is ~3 kN — ~7× larger than the Edison-recommended ceiling, so resolution at the small loads our cells produce will be poor. Stroke also too short for any later densification work. Keep in reserve only for torsional sub-tests on jointed specimens. |
| 20 kip 809 A/T | 20 000 lb (≈ 89 kN) | 20 000 lb (±2 lb ≈ ±9 N) | 6" (≈ 152 mm) | **Skip.** Even the ±2 lb resolution is ~8× the entire load range our small-strain stiffness tests will see. Reserve for any future strut-only failure tests on consolidated PETG coupons. |
| 100 kip Landmark | 110 000 lb (≈ 489 kN) | 110 000 lb (±10 lb) | 6" (≈ 152 mm) | **Do not use.** 4-orders-of-magnitude over-ranged for our specimens. |
| AOX (MTS Advantage Optical Extensometer) | — | — | <2.5 µm res., 2 mm min gauge, >1000 % strain range | **Pair with the 1 kip frame.** Directly addresses the brief's DIC/extensometer recommendation. Requires training — must coordinate with a trained operator before the first test. |

## What this changes vs. the Edison brief

The Edison brief was written generically ("the lab's 5 kN cell is
likely over-ranged… borrow / order a 100–500 N cell"). This note
replaces that generic advice with a concrete mapping:

* **Load-cell concern resolved in-house.** The 100 lb cell on the 1 kip
  Mini Tensile Tester (≈ 445 N, ±1.1 N) is already on-site and is the
  best match in the listed inventory. **No purchase / borrow request
  needed.**
* **Optical-extensometer concern resolved in-house.** AOX
  (<2.5 µm resolution) covers the brief's machine-compliance and
  sub-mm-displacement recommendations at higher fidelity than crosshead
  + DIC software would. Caveat: training requirement gates the first
  test.
* **Specimen-size implication.** The 1 kip frame is listed as
  accepting specimens of width 0–6.35 mm and notes "no standard
  cylindrical adapters". Our tensegrity-inspired single cells (25–50 mm
  bounding cube) will not fit standard tensile grips on this frame for
  *tension* on the assembled cell, but **compression** between flat
  platens is unaffected. For the bracket coupon work (PETG / TPU 85A
  per ASTM D638 / D412) the 6.35 mm width limit is comfortably above
  the standard ~3.18 mm Type V dog-bone width and at the upper end of
  Type I (12.7 mm — does **not** fit; use Type IV or Type V instead).
* **Densification deferred.** The first round per the brief is
  stiffness-only with loading capped well below densification (≤ 30 %
  nominal strain), so the 1 kip frame's load-cell range is *not* the
  binding constraint; the load-cell *resolution* is.

## Open items to confirm before the first test

1. Confirm 100 lb cell is **calibrated within ASTM E4 verification class
   1** (or get it re-verified before the first session).
2. Confirm AOX training slot for the operator who will run the
   campaign.
3. Decide on coupon dog-bone type for PETG / TPU 85A material cards
   given the 6.35 mm width ceiling — likely ASTM D638 Type V (PETG) and
   ASTM D412 Die C scaled (TPU 85A). Document in the per-specimen
   metadata schema (Artifact 2 of the brief).
4. Order/print **steel-on-steel calibration platens** sized for the
   1 kip frame for the machine-compliance baseline.
