# Felt-sheet cushioning sweep — where the accelerometers saturate, and a head-room-safe drop setting

Analysis of the 45 drops posted by @ctrhjk on
[PR #82](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/82#issuecomment-5007713855):
the same downscaled specimen as the 500-drop runs was dropped **five times**
at nine `(height, felt-sheets)` conditions — felt sheets stacked under the
drop block to cushion the hit — with CH5 the trigger @ **300 G** and the
bottom tri-axis (CH6–8) removed. The goal was to find where the sensors clip
and pick a height/cushioning combination that keeps the whole rig in range.
Data: `data/drop-tests/felt-sheet/`; script:
`scripts/analysis/drop_test_felt_sheet_analysis.py`; machine-readable metrics:
`data/drop-tests/felt-sheet/figures/felt_sheet_metrics.json`.

This closes the loop on @sgbaird's earlier concern: the current print already
runs the single-axis CH5 near full scale, so a *stiffer* design in the BO
search space could clip it — the campaign needs a drop setting with margin,
not the hardest hit the rig can produce.

## 1. Per-condition summary (5 drops each)

Impacts located on the triggered CH5 channel; raw |peak| audited against full
scale; TOP = top-vertex tri-axis CFC-180 resultant (the output/BO surrogate);
`T = TOP180 / CH5-180`.

| height / felt | CH5 raw \|peak\| (mean ± SD) | CH5 max %FS | over-FS | CH4 max %FS | TOP180 G (CV) | T |
|---|--:|--:|--:|--:|--:|--:|
| 20 in / 1 f | 9,591 ± 234 G | **105.3 %** | **4/5** | 55.9 % | 369 (0.6 %) | 2.28* |
| 20 in / 2 f | 4,383 ± 361 G | 49.8 % | 0/5 | 23.0 % | 306 (0.7 %) | 1.085 |
| 30 in / 2 f | 9,236 ± 112 G | **98.7 %** | 0/5 | 30.6 % | 375 (0.2 %) | 1.146 |
| 30 in / 3 f | 3,071 ± 383 G | 36.3 % | 0/5 | 21.1 % | 339 (1.0 %) | 1.050 |
| 40 in / 3 f | 7,050 ± 472 G | 79.3 % | 0/5 | 27.5 % | 416 (1.3 %) | 1.070 |
| 40 in / 4 f | 1,357 ± 47 G | 14.9 % | 0/5 | 13.9 % | 376 (2.1 %) | 1.046 |
| 50 in / 4 f | 2,060 ± 128 G | 23.9 % | 0/5 | 17.3 % | 416 (0.3 %) | 1.045 |
| 50 in / 5 f | 1,369 ± 29 G | 14.9 % | 0/5 | 13.3 % | 400 (1.3 %) | 1.046 |
| 60 in / 5 f | 2,614 ± 150 G | 29.7 % | 0/5 | 19.1 % | 462 (0.7 %) | 1.040 |

\* T = 2.28 at 20 in / 1 f is a **saturation artifact**, not a physical
transmissibility: when the raw CH5 spike clips at ~9.9 kG the CFC-180
low-pass sees a truncated pulse, deflating the CH5-180 denominator and
inflating T. It is a symptom of the clipping, not a measurement.

## 2. Saturation: CH5 (9,442.9 G single-axis) is the bottleneck, and it clips

- **20 in / 1 felt** drives CH5 **over full scale on 4 of 5 drops** (mean
  9,591 G, worst 9,947 G, 105 % FS) with visible analog flat-topping in the
  impact-window trace — this condition is quantitatively unusable.
- **30 in / 2 felt** sits at **98.7 % FS** (worst 9,322 G): not formally over,
  but with no usable margin and one flat-top sample — treat as saturated.
- **CH4 (top tri-axis, FS 13,624 G) never exceeds 56 % FS** and is ≤ 31 % FS
  at every non-clipping condition. The rig's ceiling is set entirely by the
  low-range single-axis CH5 on the base plate, exactly as flagged before:
  swapping CH5 for a higher-range single-axis part (or accepting the tri-axis
  CH4 as the base reference) is the real fix; felt is the interim fix.

See `figures/01_saturation_by_condition.png` (per-condition CH5/CH4 %FS with
the CLIP flags) and `figures/03_ch5_impact_traces.png` (the worst-case CH5
pulse per condition — the two saturating conditions flat-top against the FS
line while the cushioned ones are clean pulses).

## 3. OLS: height and felt count cleanly separate (n = 45, R² = 0.87)

Because height and felt were stepped together, a two-term regression is used
to de-confound them. On `log10(CH5 raw peak)`:

| term | β | interpretation | p |
|---|--:|---|--:|
| intercept | +3.982 | — | 2e-46 |
| height (per in) | +0.0266 | each **+10 in → ×1.85** on the CH5 peak | 2e-09 |
| felt (per sheet) | −0.447 | each **+1 felt sheet → ×0.36 (≈ 64 % attenuation)** | 6e-16 |

R² = 0.874 (adj 0.868); both effects are overwhelmingly significant. One felt
sheet cancels roughly **24 in** of drop height (0.447 / 0.0266). The
linear-scale model agrees: +268 G/in, −4,449 G/sheet.

Inverting the model gives the felt count needed to hold the CH5 worst case at
the ⅓-FS head-room target (3,148 G) at each height:

| height | felt sheets needed (≤ ⅓ FS) |
|--:|--:|
| 20 in | ≥ 2.3 |
| 30 in | ≥ 2.9 |
| 40 in | ≥ 3.5 |
| 50 in | ≥ 4.1 |
| 60 in | ≥ 4.7 |

## 4. The output barely depends on the input — so cushion aggressively

The key observation for the campaign: the **TOP CFC-180 output ranges only
306–462 G across a 7× swing in CH5 input**, because it is set by the
specimen's own response, not by how hard the base is hit. It grows mildly and
smoothly with drop height (energy in), and is *most repeatable at the higher,
well-cushioned conditions* (CV 0.3–0.7 % at 50–60 in vs 2.1 % at 40 in / 4 f).

So a harsh, near-saturating input buys almost no extra output signal while
spending all of the CH5 head-room the BO search space needs. The operating
point should therefore **maximize the repeatable output subject to a CH5
saturation-margin**, not maximize the input.

## 5. Recommendation

Using a **3× CH5 head-room** rule — keep the worst-case CH5 |peak| ≤ FS/3
(3,148 G), so a design up to ~3× stiffer than this already-near-saturation
specimen still fits under 9,442.9 G — and requiring CH5 to stay ≥ 5× the
300 G trigger for SNR, the usable conditions ranked by output signal are:

| rank | height / felt | CH5 max %FS | CH5 head-room | TOP180 (CV) |
|--:|---|--:|--:|--:|
| **1 (primary)** | **60 in / 5 f** | 29.7 % | **3.4×** | **462 G (0.7 %)** |
| 2 | 50 in / 4 f | 23.9 % | 4.2× | 416 G (0.3 %) |
| 3 | 40 in / 4 f | 14.9 % | 6.7× | 376 G (2.1 %) |
| 4 | 50 in / 5 f | 14.9 % | 6.7× | 400 G (1.3 %) |

**Recommended: 60 in drop + 5 felt sheets.** It gives the strongest, most
repeatable specimen output (462 G, CV 0.7 %) while holding CH5 at ~30 % FS —
3.4× head-room for stiffer BO designs — and CH4 at only 19 % FS. **50 in /
4 felt** is the best lower-height alternative (still ~4× head-room, 416 G,
CV 0.3 %) if 60 in is inconvenient to lift.

**Avoid 20 in / 1 felt and 30 in / 2 felt** — both saturate CH5. As a rule of
thumb from the model, add **one felt sheet per ~24 in** of height (≈ ⌈h/22⌉ +
buffer), which is why the reliable conditions all sit at height-to-felt ratios
around 10–12 in per sheet.

## 6. Caveats

- **The "5 felt" conditions were physically 4 felt + 1 cardboard** —
  @me-madsen later confirmed (PR #86) that the lab owns only four felt
  sheets, so every 5-sheet stack in this sweep (50 in / 5 f, 60 in / 5 f)
  included one cardboard sheet. The measurements stand as measured (the
  recommended 60 in operating point *is* the mixed stack, and the 201-drop
  validation reproduced its levels), but the per-sheet OLS coefficient in
  §3 blends the two materials at the top of the range, and extrapolations
  to "6 felt sheets" assume felt that would have to be purchased.
- **n = 1 specimen** (5 repeat drops per condition); the head-room factor of 3
  is an engineering choice — tighten it once the stiffest BO design's expected
  peak is known (from the #35 search-space bounds), since that, not this
  specimen, sets the true required margin.
- Single-axis CH5 vs tri-axis CH4 axis correspondence is unverified; T values
  assume they measure comparable axes.
- 200 ms capture window only (partial-pulse Δv); no felt-wear tracking across
  the five drops.
- The real long-term fix for head-room is a higher-range base sensor, not
  more felt — felt also changes the pulse shape (widens it), which matters if
  SEA / pulse-shape metrics are later added to the objective stack.
- Felt itself turned out to be a consumable (it compacts measurably over
  ~100 drops; see the 60 in validation §3). Durable non-consumable
  alternatives (elastomer programmer pads, Sorbothane, rubber mats) are
  surveyed in
  [drop-test-absorber-alternatives.md](drop-test-absorber-alternatives.md).
