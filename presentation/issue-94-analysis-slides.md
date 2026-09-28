# Slide content for issue #94 — opening up the drop-tower analysis

Issue [#94](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/94)
asks for the drop-tower analysis to stop being a black box: *"it was surprising
to me that you went from CFC-180 to suggesting something else … it would be best
for us to spot-check your work,"* plus tutorial-style notebooks and links to
source materials.

This file is the talk-facing answer. Six slides (**30–35** of
`Slide Decks/IDETC Supplement Slides (BO block + gap + video + accel).pptx`) turn
that request into content the IDETC audience can also use, and the last section
lists what is still owed to #94 that a slide cannot deliver.

Rebuild the slides with `python presentation/build_supplement_deck.py`.

---

## The six slides

### 30 — "One drop becomes one row of data: three numbers and the scatter around them."

A four-box pipeline: **raw** (1.25 MHz, 4 channels) → **baseline** (pre-trigger
median) → **J211 filter** (CFC-180 and CFC-1000) → **metrics** (peak transmitted
force, SEA, compaction efficiency). Sub-line: replicate drops give the noise
model the optimizer needs — a single drop is never one point.

The point of the slide is that only two steps involve judgement, steps 2 and 3 —
and both of them are what bit us. Slides 31–34 are those two steps.

### 31 — "SAE J211 sets the filter, not us — and the class you pick changes the peak by a factor of two."

Figure: [`media/fig-baseline-and-cfc.png`](media/fig-baseline-and-cfc.png),
generated from **specimen `bpx68c`, Signal 11** of the polyurethane sweep
(`data/drop-tests/pu-configs/raw/half-in.zip` on the
`copilot/add-drop-test-protocol-again` branch).

* Left panel — the first 1.2 ms of the raw CH5 record, unshifted. The trigger
  crossing is at **0.41 ms**, so the export *does* contain pre-trigger data. The
  two candidate baselines are drawn: pre-trigger median **20.0 G** versus
  full-record median **−0.5 G**.
* Right panel — the same impact at three filter settings:
  **raw 567 G · CFC-1000 344 G · CFC-180 245 G**.

Spoken: a Channel Frequency Class number times 1.65 is the −3 dB corner, so
CFC-180 is 300 Hz and CFC-1000 is 1650 Hz. Implementation is a two-pole
Butterworth applied forward and backward (zero phase), exactly as in
`cfc_filter()` in
`scripts/analysis/drop_test_60in_5felts_analysis.py`.

### 32 — "We report both bands because they answer two different questions."

| | CFC-180 · 300 Hz | CFC-1000 · 1650 Hz |
|---|---|---|
| question | what does the payload feel? | what is the structure doing? |
| use | smooth pulse, stable peak, the number in the force constraint | keeps the 500–550 Hz specimen mode — the part that differs between designs |

This is the direct answer to the "why did you move off CFC-180?" question in
#94: **we did not abandon it**, we stopped using it as the *only* band. At a
300 Hz corner the specimen's own first mode (measured at **519–549 Hz** across
the ringdown analyses in this repo) is filtered away, so every design looks
alike. The force constraint stays CFC-180; the discrimination diagnostics are
CFC-1000.

### 33 — "Our sensors lied to us first" (existing slide, kept here in the arc)

The PR #74 calibration story: a mis-entered sensitivity made CH5 read
0.953 × CH4, and CH1 was clipping at the highest drops without it being visible.
Fix: regress every channel against every other, every campaign.

### 34 — "We paid an adversary to break our own analysis, and it broke it."

Figure: [`media/fig-baseline-flip.png`](media/fig-baseline-flip.png) — published
versus corrected CFC-180 transmissibility for the four polyurethane arrangements.

| arrangement | as published | corrected (pre-trigger baseline) |
|---|--:|--:|
| A — 1/4 in | 1.022 | 1.037 |
| B — 1/2 in | 0.996 | 1.063 |
| C — 1/4 over 1/2 | 0.986 | 1.050 |
| D — 1/2 over 1/4 | 0.989 | 1.094 |

Consequences: **no arrangement attenuates** (every T > 1), B is no longer the
most repeatable CFC-180 arrangement, and the "T falls monotonically with pulse
duration" relation disappears (Spearman ρ = 0.40, p = 0.60). Verdict adopted:
**none of the four — that sweep could not decide**; rerun it as a randomized
two-geometry crossover with ≥ 2 ms pre-trigger capture.

Source: Edison Scientific adversarial review, task `d9092c5a`, committed at
`edison-trajectories/pu-configs/report/adversarial-review.md` on the
`copilot/add-drop-test-protocol-again` branch, with the recomputation
reproduced independently in-repo.

Delivery note: no drama. We asked for the analysis to be attacked, four of our
grounds fell, and the document was marked **superseded** rather than quietly
patched.

### 35 — "Every number on these slides can be re-derived from committed raw data."

Backup slide for Q&A. Raw CSVs and the analysis script live beside each campaign;
the filter is a published standard; the adversarial re-analysis, its recomputed
tables and its notebook are committed too. This is where the Colab link goes once
the tutorial notebook exists.

---

## Source materials (the second half of what #94 asked for)

### Standards

| Standard | What it fixes | Where it shows up here |
|---|---|---|
| **SAE J211-1**, *Instrumentation for Impact Test — Part 1: Electronic Instrumentation* | the CFC filter classes; −3 dB corner ≈ CFC × 1.65 Hz | slides 31–32; `cfc_filter()` |
| **ISO 6487** | the equivalent road-vehicle measurement-technique filter definition | slide 35 |
| **ISO 5348:2021**, *Mechanical mounting of accelerometers* | stud/wax/adhesive mounting and its usable bandwidth | slide 28 (key-seat + wax mount) |

⚠️ The adversarial review corrected a citation we had been repeating: the
mounting standard is **ISO 5348**, not ISO 5347. Fix that anywhere it survives
before the talk.

### In-repo primary sources (branch `copilot/add-drop-test-protocol-again`)

| Asset | Path |
|---|---|
| filter + metric implementation | `scripts/analysis/drop_test_60in_5felts_analysis.py` (`cfc_filter`, `windowed_peak`) |
| the analysis under review in #94 | `scripts/analysis/drop_test_pu_configs_analysis.py` |
| the superseded write-up, with its banner | `docs/drop-test-pu-configs-analysis.md` |
| the adversarial review | `edison-trajectories/pu-configs/report/adversarial-review.md` |
| independent recomputation | `edison-trajectories/pu-configs/report/independent_per_drop_metrics.csv`, `…/independent_arrangement_summary.csv` |
| raw data used on slide 31 | `data/drop-tests/pu-configs/raw/half-in.zip` → `bpx68c_Signal11.csv` |
| protocol and known failure modes | `docs/drop-test-protocol.md` |
| video-side corroboration of the ~1.6 ms pulse | `docs/drop-test-60in-5felts-analysis.md`, `data/drop-tests/60in-5felts-validation/video/README.md` |

### Video sources

| Video | Use |
|---|---|
| our print timelapse, <https://www.youtube.com/watch?v=nQNmi-NiL5I> | slide 20 (embedded; also opens the background addendum) |
| TP4 DAQ training walkthrough, <https://youtu.be/RNjpAmWWmkQ> | background for anyone re-running the analysis |
| drop-test SOP, <https://youtu.be/dL2djikfJFE> | background |
| drop shorts `Nab3hfuF4Dw` / `zkum2JlHpYk` | the YouTube copies of the `7xadt6` / `9GMQYQ` clips used on slide 25 |

---

## Still owed to #94 (a slide cannot do these)

1. **The tutorial Colab notebook.** Auto-download one campaign's raw CSVs from
   this repo, walk through baseline → CFC filter → peak/Δv with the equations
   and plots inline, and end by reproducing the slide-31 numbers
   (567 / 344 / 245 G). Slide 35 has the slot for its link.
2. **Re-run the two sibling analyses.** `drop_test_pu_vs_felt_analysis.py` and
   `drop_test_print_defects_analysis.py` share the full-record-median baseline.
   The print-defect study matters most: its between-specimen differences are
   ~2 %, the same order as the baseline shift.
3. **The randomized crossover** the review prescribes — two geometries ×
   arrangements A and B, 5 drops per cell, interleaved in randomized order, one
   common trigger level, ≥ 2 ms pre-trigger and 50–100 ms post-impact capture,
   outcomes prespecified.
4. **An Edison cross-check of the standards claims** on slides 31–32 before the
   deck freezes, since they are stated on stage as fact.
