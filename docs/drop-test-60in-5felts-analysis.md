# 60 in / 5 felt validation — two specimens × 100 drops, OLS drift, and whether the operating point holds

Analysis of the two campaigns posted by @ctrhjk on PR #86: the operating
point recommended by the [felt-sheet sweep](drop-test-felt-sheet-analysis.md)
(**60 in drop height + 5 felt sheets**) run at full campaign length on two
distinct-geometry specimens, **`7xadt6`** (100 captures, `Marcus_{1..4}.zip`)
and **`9GMQYQ`** (101 captures, `jin_{1..4}.zip`), both on 2026-07-20
(7xadt6 first, 19:51–20:59; 9GMQYQ second, 21:12–22:32).

Rig unchanged from the felt-sheet sweep / `500drops-nobot` runs: **CH2/CH3/CH4**
= top-vertex key-seat tri-axis (X/Y/Z, "TOP" output), **CH5** = single-axis on
the base acrylic plate (input + trigger @ 300 G), bottom tri-axis removed,
200 ms / 125 kHz. Data: `data/drop-tests/7xadt6 _60in_5felts folder/` and
`data/drop-tests/9GMQYQ_60in_5felts/` (committed as zips; the script reads
the CSVs straight out of them); script:
`scripts/analysis/drop_test_60in_5felts_analysis.py`; metrics:
`data/drop-tests/60in-5felts-validation/figures/60in_5felts_metrics.json`.

## 1. Capture health: 201/201 clean

Both campaigns are operationally flawless — the best capture record of any
run so far:

| | `7xadt6` | `9GMQYQ` |
|---|--:|--:|
| real drops / captures | **100/100** | **101/101** |
| spurious triggers | 0 | 0 |
| impact lands at | 4.06 ± 0.07 ms | 4.00 ± 0.04 ms |
| cadence (median) | 41 s | 41 s (one 12.9 min pause before Signal 101) |
| campaign span | 68 min | 80 min |

The 41 s cadence confirms the ~42 s/drop figure used in the
[sample-size analysis](drop-test-sample-size-analysis.md) for 60 in.

## 2. Stabilized-phase OLS (the requested regression)

Same methodology as the 100/500-drop campaigns: burn-in changepoint scan on
the TOP CFC-180 output, then OLS of each metric on drop number over the
stabilized drops. The scan finds **no k ≤ 20 with a non-significant trend**
for either specimen — the drift is campaign-scale (felt wear, §3), not a
seating transient — so the SOP burn-in of 5 drops is used.

**`7xadt6` (drops 6–100, n = 95):**

| metric | mean | CV | slope /drop | %/drop | 95 % CI | p | R² | DW |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| TOP output CFC-180 (G) | 461.4 | 1.74 % | +0.287 | +0.062 | [+0.275, +0.298] | 1.4e-68 | 0.963 | 1.10 |
| CH5 input CFC-180 (G) | 446.2 | 1.66 % | +0.263 | +0.059 | [+0.252, +0.274] | 3.2e-66 | 0.959 | 1.05 |
| T = TOP/CH5 | 1.034 | **0.12 %** | +3e-5 | +0.003 | — | 2.7e-17 | 0.538 | 1.76 |

Split-half (TOP): +0.066 %/drop (drops 6–53) vs +0.044 %/drop (54–100) —
the trend persists but decelerates slightly.

**`9GMQYQ` (drops 6–101, n = 96):**

| metric | mean | CV | slope /drop | %/drop | 95 % CI | p | R² | DW |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| TOP output CFC-180 (G) | 475.2 | 1.00 % | +0.132 | +0.028 | [+0.110, +0.155] | 4.2e-20 | 0.594 | 0.77 |
| CH5 input CFC-180 (G) | 462.7 | 0.81 % | +0.061 | +0.013 | [+0.036, +0.085] | 4.7e-06 | 0.201 | 0.59 |
| T = TOP/CH5 | 1.027 | 0.45 % | +1.5e-4 | +0.015 | — | 4.3e-37 | 0.823 | 0.48 |

Split-half (TOP): +0.024 %/drop then +0.070 %/drop. The low Durbin-Watson
values (0.5–1.1) say the residuals are positively autocorrelated — the drift
is a smooth physical process, not white noise around a line, so the tiny
p-values should be read as "the trend is unambiguous", not as a precise
probability. Shapiro p ≈ 0.01–0.02 on the peak channels for the same reason.

**Reading the regression:** the TOP output climbs ~0.03–0.06 %/drop on both
specimens, but it does so **in lockstep with the input** — for `7xadt6` the
per-drop correlation between TOP and CH5 (CFC-180) is **r = 0.999**
(`9GMQYQ`: 0.895) — and the transmissibility **T = TOP/CH5 absorbs almost
all of it** (CV 0.12 % / 0.45 %; total drift over ~95 drops only +0.3 % /
+1.4 %). The drift is an *input/rig* effect, not specimen degradation:
pulse width and ringdown frequency are essentially flat, and the felt (§3)
explains the input rise. See `figures/02_stabilized_ols.png`.

## 3. The felt is a consumable — CH5's raw spike triples over the evening

The saturation audit (`figures/03_saturation.png`) is the campaign-scale
story. The **raw** CH5 spike grows monotonically across the evening — the
two campaigns were run back-to-back, presumably on the same felt stack:

| | CH5 raw \|peak\| first 5 | last 5 | worst | worst %FS |
|---|--:|--:|--:|--:|
| `7xadt6` (first) | 2,056 G (~22 % FS) | 3,163 G | 3,316 G (Signal 87) | 35.1 % |
| `9GMQYQ` (second) | 3,932 G (~42 % FS) | 6,068 G | 6,474 G (Signal 97) | **68.6 %** |

- `7xadt6` starts right at the fresh-felt level the sweep measured
  (2,614 ± 150 G) and crosses the **FS/3 head-room target (3,148 G) around
  drop 67**; `9GMQYQ` is above FS/3 from drop 1 and ends at ~2/3 of full
  scale. On this trajectory a third same-evening campaign would have pushed
  CH5 toward saturation.
- The **CFC-180** input barely moves by comparison (446 → 463 G between the
  campaigns): compacted felt mostly adds short high-frequency spike content,
  which is exactly what eats the raw-peak head-room (and would clip a stiffer
  specimen's input channel) while leaving the filtered physics almost intact.
- Consistent with viscoelastic felt recovery, `9GMQYQ` Signal 101 — recorded
  after the 12.9 min pause — drops back to 56 % FS from the ~65 % just
  before the pause.
- CH4, the largest top-vertex axis (Z), never exceeds **22.1 % FS** on either
  specimen; the tri-axis output has abundant head-room throughout. CH2 (X)
  ≤ 3.1 % FS and CH3 (Y) ≤ 6.7 % FS — the output is strongly Z-dominated,
  as expected for a vertical drop.

## 4. Does the setting discriminate geometry?

On the stabilized drops (Welch t-test, `figures/04_specimen_comparison.png`):

| metric | `7xadt6` | `9GMQYQ` | diff | Welch p | \|d\| |
|---|--:|--:|--:|--:|--:|
| TOP CFC-180 (G) | 461.4 (CV 1.74 %) | 475.2 (CV 1.00 %) | −2.9 % | 3.7e-30 | 2.1 |
| T = TOP/CH5 | 1.034 (CV 0.12 %) | 1.027 (CV 0.45 %) | +0.7 % | 6.4e-27 | 2.1 |

The two geometries separate decisively (d ≈ 2.1) even though they happen to
be close responders (−2.9 % on TOP) — the per-drop noise is small enough
that even sub-1 % differences in T are resolvable at n ≈ 5. This is the
repeatability the felt-sheet sweep predicted for 60 in / 5 felt (sweep
specimen: 462 G, CV 0.7 % — `7xadt6`'s 461.4 G is a near-exact match).

## 5. Verdict and recommendation

**The 60 in / 5 felt setting is validated — keep it — but manage the felt
as a consumable.** Specifically:

1. **Keep 60 in / 5 felt sheets** as the campaign operating point. It
   delivered 201/201 clean captures, the strongest and most repeatable
   output of any tested condition (461–475 G, CV ≤ 1.7 %), and clean
   geometry discrimination. No head-room problem originates from the
   condition itself: with fresh felt, CH5 sits at ~22 % FS (≈ 4.6×
   head-room).
2. **Replace (or top up) the felt stack when CH5's raw |peak| exceeds
   FS/3 ≈ 3.1 kG — in practice roughly every ~100 drops at 60 in.** The
   entire campaign-scale drift in this dataset is felt compaction: the raw
   CH5 spike tripled (2.1 → 6.5 kG) over the 201-drop evening. Refreshing
   felt per specimen (or per ~100 drops) keeps every specimen's input
   comparable and preserves the clip margin for stiffer BO designs. Log the
   felt state (drops-on-stack) with each session.
3. **If mid-campaign felt swaps are impractical, run 60 in / 6 felt
   sheets.** One extra sheet attenuates the base hit ×0.36 (felt-sheet
   model), which would have held even this evening's worst case at ~25 % FS
   — at nearly zero cost in output signal, since the output is set by the
   specimen, not the input (306–462 G across a 7× input swing in the sweep).
   The lower-height fallback remains 50 in / 4–5 felt (~42 % less input
   energy, 12–20 s faster per drop) if hoisting to 60 in becomes the
   bottleneck.
4. **Prefer T = TOP/CH5 (or output-at-logged-input) as the BO objective**,
   as already recommended by the input-output analysis: T cancels the
   felt-wear drift almost entirely (CV 0.12–0.45 % vs 1.0–1.7 % for the raw
   output; r = 0.999 input-output tracking on `7xadt6`). At the
   [recommended 2 + 5 drops per specimen](drop-test-sample-size-analysis.md),
   within-specimen felt wear contributes only ~0.1–0.3 % to T — negligible
   against the ≥10 % between-design differences.

## 6. Caveats

- n = 1 specimen per geometry; the two specimens' 100-drop campaigns are
  what make the per-drop statistics strong, but geometry conclusions still
  rest on one print each.
- The "same felt stack all evening" reading is inferred from the monotonic
  CH5 raw trend across the two back-to-back sessions (and its recovery after
  the 12.9 min pause); @ctrhjk should confirm whether the felt was changed
  between specimens — if it *was*, the `9GMQYQ` starting level (~42 % FS)
  suggests felt sheets also vary unit-to-unit, which strengthens, not
  weakens, the case for logging felt state and normalizing by the input.
- Full-scale values are carried over from the felt-sheet sweep channel
  table (CH2–CH4: 14,492.8 / 14,992.5 / 13,624.0 G; CH5: 9,442.9 G);
  sensor serial numbers weren't posted with this dataset.
- Durbin-Watson 0.5–1.1 on the drifting channels means the OLS p-values
  overstate certainty (autocorrelated residuals); slopes and R² are the
  meaningful quantities.
- 200 ms window only; Δv is partial-pulse; the felt-wear extrapolation
  beyond 201 drops is a straight-line eyeball, not a fitted wear model.
