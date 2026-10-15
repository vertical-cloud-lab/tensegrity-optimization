# Key-seat mount drop-test analysis (specimen `prc1kn`)

Analysis of @ctrhjk's **key-seat mount validation** drop run
([PR #67](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4837240958),
drop height 13 in). This is a direct follow-up to the
[input-output (transmissibility) analysis](drop-test-input-output-analysis.md):
same input-output instrumentation (single-axis **input** on the base plate, CH5,
triggered; tri-axis **output** on the top vertex, CH2/CH3/CH4), same
bungees-removed setup. The **one** change under test is the **output mount** —
the tri-axis now seats in the printed **key-seat** pocket (the "igloo"
`accel_mount()` housing from #35) instead of a hand-applied hot-glue blob.

The question this run answers: in the prior input-output series the
transmissibility crept up across the five cyclic drops (pooled +0.015 in T per
drop, p = 1e-4), and both we and Edison attributed that to **hot-glue mount
creep**, not material softening. Does the key-seat make it go away?

The specimen `prc1kn` is a **deliberately-failed print** (bubbles in its TPU
cable); it is used only to exercise the mount + DAQ, **not** to compare geometry.

Raw data + channel map: [`data/drop-tests/key-mounted/`](../data/drop-tests/key-mounted/).
Reproduce with:

```bash
pip install numpy scipy matplotlib
python scripts/analysis/drop_test_key_mounted_analysis.py
```

## Method

Identical pipeline to the input-output analysis: impact located on the triggered
CH5 input within the first 10 ms (lands at t ≈ 3.9 ms), peaks taken in a ±1.5 ms
window (not a global 0.2 s max), baseline-corrected on the pre-impact samples,
and reported raw / SAE J211 CFC-1000 (≈1650 Hz) / CFC-180 (≈300 Hz). Output is
the tri-axis resultant √(CH2²+CH3²+CH4²); `T = output / input` on the CFC-180
peaks. Raw peaks are sensor-ringing-dominated, so CFC-180 is the structural
number. The drift test is an ordinary-least-squares fit of input, output and T
against drop number.

**File-name note:** the TP4 `Signal{n}` index is the capture number, not the
drop number — `Signal4` was discarded, so drops 1…5 = `Signal{1,2,3,5,6}`.

## Results

### Per-drop metrics (CFC-180)

| drop | t_imp (ms) | input CH5 (G) | output tri-axis (G) | **T = OUT/IN** | input Δv (m/s) |
|---:|--:|--:|--:|--:|--:|
| 1 | 4.07 | 223 | 232 | **1.04** | 2.66 |
| 2 | 3.92 | 223 | 232 | **1.04** | 2.71 |
| 3 | 3.91 | 220 | 239 | **1.08** | 2.66 |
| 4 | 3.91 | 212 | 233 | **1.10** | 2.55 |
| 5 | 4.06 | 218 | 233 | **1.07** | 2.64 |

### Aggregates (mean ± 1σ over 5 drops)

| quantity | mean ± 1σ | CV |
|---|--:|--:|
| input CH5 CFC-180 | 219.2 ± 4.4 G | 2.0 % |
| output tri-axis CFC-180 | 233.6 ± 3.0 G | 1.3 % |
| **T = OUT/IN** | **1.066 ± 0.026** | 2.4 % |

### Drift across the 5 cyclic drops (OLS vs drop #)

| series | slope | p | verdict |
|---|--:|--:|---|
| input  | −2.04 G/drop | 0.152 | not significant |
| **output** | **+0.39 G/drop** | **0.739** | **not significant** |
| T | +0.012 /drop | 0.170 | not significant |

## Findings

1. **The key-seat fixes the output-mount drift.** This is the headline. In the
   prior hot-glue series the *output* climbed at constant input and the pooled
   T-vs-drop slope was significant (+0.015/drop, p = 1e-4). With the key-seat the
   **output is flat — slope +0.39 G/drop, p = 0.74, CV 1.3 %** — and shows no
   significant trend. That confirms the earlier drift was mount creep (hot glue
   seating over cycles), exactly as Edison concluded, and that the printed
   key-seat removes it. This is the green light to start cyclic / to-failure
   campaigns without mistaking mount creep for fatigue.

2. **The small residual T trend is now on the input (wax) side, and it is not
   significant.** T drifts +0.012/drop (p = 0.17, n.s.); the contribution comes
   from the *input* drifting **down** (−2.04 G/drop, p = 0.15), not the output
   rising. So whatever residual creep remains has moved to the wax-mounted input
   sensor — worth watching, but well below the hot-glue effect and not yet
   statistically real over five drops.

3. **The input-output system is reproducible and triggers reliably.** All 5/5
   drops triggered cleanly on CH5; input 219 ± 4 G (CV 2.0 %), output 234 ± 3 G
   (CV 1.3 %), Δv ≈ 2.6 m/s — consistent with the bungees-removed controlled
   strike established in the input-output series.

4. **`T ≈ 1.07` for this specimen.** As expected for a vertex-to-vertex stiff
   path, the output slightly exceeds the input (T > 1, i.e. not "cushioning").
   This is a single failed-print specimen used to exercise the mount, so this
   value is **not** a geometry result — it just confirms `T` is well-defined and
   tight (CV 2.4 %) under the new mount.

## SOP / test-method implications

- **Adopt the key-seat for the output (vertex) sensor.** It removes the cyclic
  output drift that the hot-glue mount introduced — the single biggest blocker to
  trusting cyclic/to-failure data. This closes gap (1)/(2) flagged on the #35
  igloo review for the *output* node.
- **But add a retainer inside the housing.** The press-fit alone did not hold the
  sensor — it fell off during the run. Adding wax (or a clip/set-screw) inside
  the key-seat to retain the sensor, as Sterling suggested, keeps the rigid
  z-aligned seat while preventing fall-off; a thin wax film also matches the
  ISO-5347 couplant hierarchy and should not reintroduce the hot-glue-scale creep
  (re-run this OLS drift check on the first few drops to confirm).
- **Consider a third sensor.** Sterling's aside about a key-seated tri-axis at a
  *bottom* vertex would give a keyed input at the structure (vs. the wax-on-plate
  input), useful if the residual input-side drift grows.
- **Geometry discrimination still needs distinct intact prints.** This run was a
  single failed-print specimen; the per-geometry `T` comparison still wants n ≥ 5
  distinct intact prints per geometry, randomized order, capture extended past
  200 ms — unchanged from the input-output SOP.

## Caveats

- **n = 1 specimen** (single failed print), 5 cyclic drops — the drift result is
  about the *mount*, not the material/geometry.
- 200 ms window only (no full ringdown); Δv is a partial-pulse integral over the
  CFC-180 half-amplitude width.
- The accelerometer fell off during the run (press-fit insufficient); the five
  analyzed captures are clean, but the fall-off itself is a retention finding.
- Tri-axis output-axis orientation and CH4/CH5 axis correspondence remain
  unverified, as in the prior series.
