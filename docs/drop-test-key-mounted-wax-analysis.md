# Key-seat **+ wax retainer** drop-test analysis (specimen `prc1kn`)

Analysis of @ctrhjk's **wax-retainer follow-up** drop run
([PR #67](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4838901017),
drop height 13 in). Direct follow-up to the bare
[key-seat analysis](drop-test-key-mounted-analysis.md): same input-output
instrumentation (single-axis **input** on the base plate, CH5, triggered;
tri-axis **output** in the top-vertex key-seat, CH2/CH3/CH4), same
bungees-removed setup. The **one** change under test is the **output-sensor
retention** — in the bare key-seat run the tri-axis sat by press-fit alone and
**fell off** mid-run, so @ctrhjk added **wax inside the key-seat housing** to
retain it.

The question this run answers: with the wax retainer in, does the output stay
drift-free (as the bare key-seat appeared to: output slope +0.39 G/drop, p = 0.74,
n.s.), or does the added wax reintroduce the kind of mount creep the original
hot-glue mount showed (T +0.015/drop, p = 1e-4)?

The specimen `prc1kn` is a **deliberately-failed print** (bubbles in its TPU
cable); it is used only to exercise the mount + DAQ, **not** to compare geometry.

Raw data + channel map: [`data/drop-tests/key-mounted-wax/`](../data/drop-tests/key-mounted-wax/).
Reproduce with:

```bash
pip install numpy scipy matplotlib
python scripts/analysis/drop_test_key_mounted_wax_analysis.py
```

## Method

Identical pipeline to the key-seat analysis: impact located on the triggered CH5
input within the first 10 ms (lands at t ≈ 4.1 ms), peaks taken in a ±1.5 ms
window (not a global 0.2 s max), baseline-corrected on the pre-impact samples,
reported raw / SAE J211 CFC-1000 (≈1650 Hz) / CFC-180 (≈300 Hz). Output is the
tri-axis resultant √(CH2²+CH3²+CH4²); `T = output / input` on the CFC-180 peaks.
Raw peaks are sensor-ringing-dominated, so CFC-180 is the structural number. The
drift test is an ordinary-least-squares fit of input, output and T against drop
number. The script also re-analyzes the bare key-seat run for a side-by-side
wax-vs-no-wax comparison. Captures are contiguous this run: `Signal{7..11}` =
drops 1…5.

## Per-drop results (CFC-180)

| drop | input CH5 (G) | output tri-axis (G) | **T = OUT/IN** |
|---:|--:|--:|--:|
| 1 | 230 | 226 | **0.98** |
| 2 | 229 | 228 | **0.99** |
| 3 | 228 | 228 | **1.00** |
| 4 | 227 | 229 | **1.01** |
| 5 | 228 | 230 | **1.01** |
| **mean ± 1σ** | **228.5 ± 1.2** (CV 0.5 %) | **228.2 ± 1.5** (CV 0.6 %) | **0.999 ± 0.011** (CV 1.1 %) |

Input Δv ≈ 2.7 m/s, input pulse width ≈ 1.5 ms, impact at t ≈ 4.1 ms — all
consistent with the bungees-removed controlled strike.

### Wax vs no-wax (same specimen, same key-seat)

| metric | bare press-fit (prior) | **+ wax retainer (this run)** |
|---|--:|--:|
| input CH5 mean / CV | 219.2 G / 2.0 % | **228.5 G / 0.5 %** |
| output mean / CV | 233.6 G / 1.3 % | **228.2 G / 0.6 %** |
| T mean / CV | 1.066 / 2.4 % | **0.999 / 1.1 %** |
| input OLS slope (p) | −2.04 G/drop (0.15, n.s.) | **−0.58 G/drop (0.13, n.s.)** |
| output OLS slope (p) | +0.39 G/drop (0.74, n.s.) | **+0.90 G/drop (0.005, sig.)** |
| T OLS slope (p) | +0.012/drop (0.17, n.s.) | **+0.0064/drop (0.011, sig.)** |
| sensor retained? | **no** (fell off) | **yes** |

## Headlines

1. **The wax retainer fixes the fall-off and makes the system the most
   repeatable yet.** 5/5 drops captured, the sensor stayed put, and the
   coefficients of variation roughly **halved** across the board — input CV
   2.0 → 0.5 %, output 1.3 → 0.6 %, T 2.4 → 1.1 %. Both input (228.5 ± 1.2 G) and
   output (228.2 ± 1.5 G) are now flat and tight, and T ≈ 1.00 ± 0.01. This is
   the cleanest input-output run in the series.

2. **A small but now statistically-significant output creep appears — and the
   significance is a side-effect of how tight the data became, not a large
   effect.** The output rises monotonically +0.90 G/drop (p = 0.005) and T rises
   +0.0064/drop (p = 0.011). But the *magnitude* is tiny: output goes 226 → 230 G
   over five drops (~1.8 % total), T goes 0.98 → 1.01 (~3 %). Because the residual
   scatter collapsed to CV ≈ 0.6 %, even this whisper of a trend clears p < 0.05 —
   whereas the larger-magnitude wobble of the bare run (output slope +0.39, but
   noisy) did not. **Statistical significance here ≠ practically important
   drift.** Note the slope direction is the classic mount signature: output rising
   at near-constant input is consistent with the **wax progressively seating /
   coupling** over the first few impacts, the same mechanism as (but ~half the
   T-slope of) the original hot-glue creep (+0.015/drop).

3. **The input (wax-on-plate) side is now essentially rock-stable.** The
   downward input drift I'd flagged in the bare run (−2.04 G/drop) shrank to
   −0.58 G/drop (p = 0.13, n.s.) and the input CV is the best in the whole series
   (0.5 %). The wax-on-flat-plate input mount is in good shape.

## SOP / test-method implications

- **Adopt the wax-retained key-seat as the output mount.** It solves the
  retention problem the bare press-fit had and delivers the tightest input-output
  repeatability so far — exactly what a BO objective needs as a low noise floor.
- **Burn in the wax before recording a long campaign.** The residual output creep
  is most plausibly wax seating over the first few impacts. For 20-drop /
  to-failure runs, take a few unrecorded **settling drops** first (or discard the
  first 1–2), then start the recorded series — otherwise this ~0.9 G/drop wax
  seating could be misread as early material fatigue. Re-running this same OLS
  drift check on the first few recorded drops is the cheap confirmation.
- **Report effect sizes, not just p-values, for drift.** With CV now ≈ 0.5–0.6 %,
  the drift test is sensitive enough that trivially small trends will read as
  "significant." Quote the per-drop slope as a % of the mean (here ~0.4 %/drop on
  output) so a real fatigue signal in future to-failure data is distinguishable
  from sub-percent mount settling.
- **Sterling's 3rd-accelerometer idea remains the clean fix** if even this
  residual matters: a second keyed seat at a bottom vertex (or a stud/cement input
  mount) would remove the last bit of mount dependence.

## Caveats

- n = 1 specimen (the failed print `prc1kn`), 5 cyclic drops — this validates the
  **mount/DAQ**, not material or geometry. T ≈ 1.00 is not a geometry result;
  geometry discrimination still needs n ≥ 5 distinct intact prints per geometry,
  randomized order.
- 200 ms capture window only (no full ringdown); Δv is a partial-pulse integral
  over the half-amplitude pulse.
- Tri-axis output-axis orientation is unverified (resultant is orientation-robust,
  but per-axis attribution is not claimed).
- The wax-seating interpretation of the residual output creep is inferred from the
  slope direction (output up at constant input) and is consistent with — but not
  independently confirmed against — a longer burn-in series.
