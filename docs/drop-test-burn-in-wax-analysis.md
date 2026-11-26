# Burn-in wax drift check — drop-test analysis (specimen `prc1kn`)

Analysis of @ctrhjk's **burn-in wax** drop run
([PR #67](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67),
drop height 13 in). Direct follow-up to the
[key-seat + wax-retainer analysis](drop-test-key-mounted-wax-analysis.md), which
found a small-but-statistically-significant output creep (**+0.90 G/drop,
p = 0.005**; T +0.0064/drop, p = 0.011) across 5 recorded drops and read it as
the **wax progressively seating** over the first few impacts. The recommended fix
was to **burn in the wax** — take a few unrecorded settling drops before starting
the recorded series.

This run tests that fix. @ctrhjk removed the old wax residue, applied **fresh
wax** inside the key-seat housing, and dropped `prc1kn` **8 times**:

- **drops 1–3** (`Signal1..3`) — **burn-in** phase (no videos), meant to seat the
  fresh wax and absorb the seating creep;
- **drops 4–8** (`Signal4..8`) — **recorded** phase (with videos), the drops that
  would count in a real campaign.

The question: does the wax-seating creep **concentrate in the burn-in drops and
flatten out** in drops 4–8, leaving the recorded phase drift-free?

Same input-output instrumentation as the whole series — single-axis **input** on
the base plate (CH5, triggered, wax-mounted); tri-axis **output** in the
top-vertex key-seat (CH2/CH3/CH4, wax-retained); bungees removed. The specimen
`prc1kn` is a **deliberately-failed print** (bubbles in its TPU cable), used only
to exercise the mount/DAQ, **not** to compare geometry.

Raw data + channel map: [`data/drop-tests/burn-in-wax/`](../data/drop-tests/burn-in-wax/).
Reproduce with:

```bash
pip install numpy scipy matplotlib
python scripts/analysis/drop_test_burn_in_wax_analysis.py
# videos (opencv):
python scripts/analysis/drop_test_burn_in_wax_video_analysis.py
```

## Method

Identical pipeline to the wax analysis: impact located on the triggered CH5 input
within the first 10 ms (lands at t ≈ 4.06 ms), peaks taken in a ±1.5 ms window
(not a global 0.2 s max), baseline-corrected on pre-impact samples, reported raw /
SAE J211 CFC-1000 (≈1650 Hz) / CFC-180 (≈300 Hz). Output is the tri-axis
resultant √(CH2²+CH3²+CH4²); `T = output / input` on the CFC-180 peaks. The drift
test is an OLS fit of input, output and T against drop number, run three ways: on
**all 8** drops, on the **burn-in** subset (1–3), and on the **recorded** subset
(4–8). Captures are contiguous: `Signal{1..8}` = drops 1…8.

## Per-drop results (CFC-180)

| drop | phase | input CH5 (G) | output tri-axis (G) | **T = OUT/IN** |
|---:|:--|--:|--:|--:|
| 1 | burn-in | 226 | 222 | **0.98** |
| 2 | burn-in | 222 | 225 | **1.01** |
| 3 | burn-in | 226 | 225 | **1.00** |
| 4 | recorded | 228 | 225 | **0.99** |
| 5 | recorded | 229 | 224 | **0.98** |
| 6 | recorded | 228 | 223 | **0.98** |
| 7 | recorded | 229 | 224 | **0.98** |
| 8 | recorded | 227 | 223 | **0.98** |

| subset | input CV | output CV | T CV | output OLS slope (p) | T OLS slope (p) |
|---|--:|--:|--:|--:|--:|
| all 8 | 1.00 % | 0.48 % | 1.18 % | −0.04 G/drop (0.81, n.s.) | −0.0027/drop (0.14, n.s.) |
| **burn-in (1–3)** | 0.95 % | 0.79 % | 1.38 % | **+1.67 G/drop** (0.20, n.s.†) | +0.0068/drop (0.67, n.s.†) |
| **recorded (4–8)** | 0.47 % | **0.31 %** | **0.48 %** | **−0.37 G/drop (0.08, n.s.)** | **−0.0007/drop (0.70, n.s.)** |

† n = 3, so the burn-in slopes cannot reach significance regardless of magnitude —
they are reported for their *size/direction*, not their p-value.

For comparison, the **prior wax run with no burn-in** (5 recorded drops, fresh
wax): output **+0.90 G/drop, p = 0.005 (significant)**; T +0.0064/drop, p = 0.011
(significant); output CV 0.64 %, T CV 1.07 %.

## Headlines

1. **The burn-in worked — this is the result we were after.** The output creep
   that was *statistically significant* in the no-burn-in run (+0.90 G/drop,
   p = 0.005) is **gone from the recorded phase**: output slope −0.37 G/drop
   (p = 0.08, n.s.) and T slope −0.0007/drop (p = 0.70, n.s.) across drops 4–8.
   Not only is it non-significant, the sign has flipped from creeping *up* to a
   trivial flat/slightly-down — exactly what "the wax has finished seating" looks
   like. **Cyclic / to-failure campaigns can now record from drop 4 onward without
   mistaking mount seating for early fatigue.**

2. **The seating really is concentrated in the burn-in drops.** Output climbs
   **+1.67 G/drop across drops 1–3** (222 → 225 → 225 G) — a steeper per-drop rise
   than the *entire* no-burn-in run's +0.90 G/drop — then plateaus. The creep
   didn't disappear; the burn-in **moved it out of the recorded window**, which is
   the whole point of the protocol.

3. **The recorded phase is the tightest, most drift-free data in the series.**
   Recorded-phase CVs are the best yet: input 0.47 %, **output 0.31 %**, **T
   0.48 %** — roughly half the no-burn-in run's already-good numbers and ~4× better
   than the original hot-glue mount. `T = 0.981 ± 0.005` over five drops. That is a
   very low noise floor for a BO objective.

4. **Input side stays rock-stable.** Input CH5 is flat and tight (228.2 ± 1.1 G
   recorded, CV 0.47 %, slope −0.21 G/drop, p = 0.62 n.s.) — the wax-on-flat-plate
   input mount continues to be the most reliable link in the chain.

## Video kinematics (5 recorded drops)

The five recorded drops have slow-motion videos (the burn-in drops do not).

> **Time-base correction (2026-07-01).** The raw `drop5.mp4` committed to this PR
> lets us verify the playback container directly. It is **30 fps** (808 frames /
> 26.93 s) — but its encoder tag is `clipchamp.com` and it carries an audio track,
> so it is **not** the camera-native file: it is a Clipchamp re-encode of a
> **24p / 960 fps** HFR capture (native HFR clips are silent, 24 fps). The bytes are
> **identical (MD5)** to the version GitHub serves from the comment, so GitHub does
> **not** re-encode or drop the frame rate — the 30 fps comes from the Clipchamp
> export, not GitHub. Consequently the earlier `frame / 960` mapping (which assumes
> a 30 fps container that is a 32× slow-mo of 960 fps) is only exact for a
> camera-*native* **24 fps** file; for this **30 fps** duration-preserving re-encode
> the physical slow factor is 960 / 24 = **40×**, so the correct mapping is
> `frame / 1200`, and the absolute in-frame descent time below is ~25 % smaller than
> first reported (94.6 → **≈ 75.7 ms**). The video cannot self-calibrate this (the
> structure enters the top of frame already falling, so there is no clean in-frame
> free-fall segment, and there is no scale bar) — treat any absolute video time as
> ± 25 % and use the **accelerometer** (Δv, free-fall) as the calibrated time source.
> **All relative results below are unaffected** (CVs, rebound fraction, drift
> in %/drop, transmissibility are dimensionless / relative and never used the
> absolute time base).

Vertical motion is in pixels (uncalibrated spatial scale); absolute timing carries
the ± 25 % container caveat above.

| metric | mean ± 1σ | CV |
|---|--:|--:|
| in-frame visible descent (real ms, `frame/1200`) | 75.7 ± 0.6 | 0.9 % |
| descent slope (px/frame) | 2.162 | 0.32 % |
| rebound fraction (of drop depth) | 0.47 | 0.9 % |

- **Optical repeatability corroborates the accelerometer.** Aligned at impact the
  five descents overlay almost perfectly — descent slope CV 0.32 %, rebound
  CV 0.9 % — the same "the rig is controlled" signal as the CFC-180 CVs above, from
  an independent (optical, non-contact) channel.
- **Descent shows consistent downward curvature** (positive `acc_px_fr²`),
  i.e. the structure accelerating under gravity → confirms the bungees are removed
  (the opposite of the early bungee-assisted lift-off).
- **~47 % elastic rebound**, identical across all five drops — the tensegrity
  spring-back sits cleanly *after* the impact event and adds no scatter.
- **Timing caveat:** the tracked ~75.7 ms (`frame/1200`; ≈ 94.6 ms under the
  superseded `frame/960`) is only the **in-frame visible** descent — the tracker
  onset is not the true release, so it is *not* the full free-fall time from 13 in
  (≈ 260 ms) and should not be compared to it 1:1. It is valid for the drop-to-drop
  *relative* comparison, which is the repeatability claim here, and that relative
  claim is independent of the 960-vs-1200 container factor.

## SOP / test-method implications

- **Adopt the burn-in wax protocol.** Apply fresh wax, take **≥3 unrecorded
  burn-in drops**, then record. Drops 4–8 here show that 3 burn-in drops are enough
  to seat this wax/geometry: the recorded phase is drift-free at CV ≈ 0.3–0.5 %.
- **Confirm burn-in completion per fresh application**, don't assume it. The cheap
  check is exactly this OLS drift test on the first few recorded drops — if the
  output slope is n.s. (as here), the wax has seated; if it's still creeping up,
  add burn-in drops before trusting the data.
- **Report effect sizes, not just p-values.** With CV now ≈ 0.3–0.5 %, the drift
  test is sensitive to sub-percent trends; quote slope as %/drop of the mean so a
  real fatigue signal in future to-failure runs is distinguishable from residual
  mount settling (here the recorded output slope is −0.16 %/drop, i.e. noise).
- **Re-seat requires re-burn-in.** This run stripped and re-applied the wax, so the
  seating clock reset; any time the sensor is re-mounted, repeat the burn-in.
- Sterling's **3rd accelerometer in a bottom-vertex key-seat** (or a stud/cement
  input mount) remains the clean long-term fix if even the residual sub-percent
  mount dependence needs to be removed.

## Caveats

- n = 1 specimen (the failed print `prc1kn`), 8 cyclic drops — this validates the
  **mount/DAQ + burn-in protocol**, not material or geometry. `T ≈ 0.98` is not a
  geometry result; geometry discrimination still needs n ≥ 5 distinct intact prints
  per geometry, randomized order.
- The burn-in-subset OLS (n = 3) cannot be statistically significant regardless of
  slope; the burn-in evidence is the *magnitude/direction* of its slope plus the
  *absence* of the previously-significant creep in the recorded subset.
- 200 ms capture window only (no full ringdown); Δv is a partial-pulse integral.
- Tri-axis output-axis orientation is unverified (resultant is orientation-robust).
- Video spatial scale uncalibrated (pixels); tracked descent is the in-frame
  visible portion only.
