# Drift-calibration #2 — 50 auto-drops (`prc1kn`): OLS drift + damage check

Analysis of the second drift-calibration series posted by @ctrhjk on
[PR #67](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67):
**50 automatically-released drops** at 13 in (~17 s cadence, ~14 min total),
same input-output instrumentation as the whole key-seat series — single-axis
**input** wax-mounted on the base plate (CH5, the triggered channel), tri-axis
**output** in the vertex key-seat + wax (CH2/CH3/CH4), bungees removed, dummy
specimen `prc1kn`. **New this run:** the output sensor's cable is tied off to
the iron rod, and the sensor **did not fall off** (vs the drop-26 fall-off in
run #1).

- Data + setup: [`data/drop-tests/drift-calibration2/`](../data/drop-tests/drift-calibration2/README.md)
- Script: [`scripts/analysis/drop_test_drift_calibration2_analysis.py`](../scripts/analysis/drop_test_drift_calibration2_analysis.py)
  (also emits `figures/drift_calibration2_metrics.json`)
- Companion: [run #1 (30 drops)](drop-test-drift-calibration-analysis.md) ·
  [`prc1kn` health check](drop-test-prc1kn-health-check.md)

All peaks are windowed at the CH5-located impact (±1.5 ms, first 10 ms),
baseline-corrected; **SAE J211 CFC-180** is the structural number; the output
is the tri-axis resultant; `T = output / input` on CFC-180 peaks.

## Headline results

1. **The 50-drop auto campaign is feasible.** 50/50 drops triggered and the
   output sensor stayed seated for all 50 — the cable tie-off cures the
   fall-off failure mode of run #1. Total wall time ~14 min.
2. **Transmissibility `T` is drift-free from drop 1** — mean 1.078, CV 1.95 %,
   slope −0.010 %/drop, p = 0.67. This is the run's most useful finding: the
   input and output peaks drift *together* (both ≈ +0.03…+0.04 %/drop), so
   the ratio cancels the common-mode rig-level drift entirely.
3. **The output-only peak keeps a small positive seating trend much longer
   than run #1** — the exponential-approach fit gives τ ≈ 12 drops (vs ≈ 5 in
   run #1), total seating amplitude ~6.9 G (≈ 2.9 %), and the split-half check
   shows the trend is gone (slightly negative) only in the second half
   (drops 29–50). A 5-drop burn-in is **not** enough for output-only metrics
   on this re-mount.
4. **No specimen damage** after ~98 cumulative recorded drops on `prc1kn`:
   ringdown mode locked at 549 Hz, pulse width flat at 1.49 ms, noise floors
   unchanged.
5. **The sensor is still slowly rotating in the seat** (CH3 +0.65 %/drop,
   p ≈ 1e-17; CH4 +0.32 %/drop, p ≈ 1e-22 at near-constant resultant) — the
   same early-warning signature that preceded run #1's fall-off. The cable tie
   prevents detachment but does not stop the rotation; the rotation-invariant
   resultant and `T` remain valid.

## 1) Burn-in / stabilization phase

Changepoint scan — OLS the output over drops k+1…50 for each candidate
burn-in count k:

| burn-in k | n | slope (%/drop) | p |
|--:|--:|--:|--:|
| 0 | 50 | +0.041 | <0.001 |
| 3 | 47 | +0.036 | <0.001 |
| 5 | 45 | +0.032 | <0.001 |
| 8 | 42 | +0.025 | <0.001 |
| 10 | 40 | +0.017 | 0.004 |
| 12 | 38 | +0.012 | 0.038 |

No k ≤ 12 reaches non-significance — with n ≈ 40–50 the test resolves slopes
far smaller than run #1 could, and the seating transient is genuinely slower
this time. Two independent estimates of the transition:

- **Exponential-approach fit** `out(d) = a − b·exp(−d/τ)`: plateau
  a = 242.1 G, amplitude b = 6.9 G (≈ 2.9 % of the plateau), **τ = 12.1
  drops** (95 % seated after ~3τ ≈ 36 drops). Run #1's τ was 4.9 drops.
- **Split-half check**: drops 6–28 drift +0.096 %/drop (p < 0.001); drops
  29–50 drift **−0.021 %/drop (p = 0.01)** — the seating trend has died out
  (and slightly reversed) by the second half.

So the stabilization point @ctrhjk asked to locate sits around **drop
~12–15** for the output-only metric on this re-mount (fresh wax + cable
tie-off seat differently than run #1's application), and full flatness only
arrives ~drop 28. For `T`, there is **no detectable burn-in at all** (flat
from drop 1).

## 2) Stabilized-phase OLS drift rate

Using the run-#1 SOP window (drops 6–50, n = 45) for comparability:

| series | mean | CV | slope (%/drop) | 95 % CI (G/drop) | p | R² |
|---|--:|--:|--:|--:|--:|--:|
| input CH5 | 223.6 G | 1.74 % | +0.043 | [+0.010, +0.183] | 0.029 | 0.11 |
| output | 241.0 G | 0.64 % | +0.032 | [+0.050, +0.105] | <0.001 | 0.43 |
| **T = OUT/IN** | **1.078** | **1.95 %** | **−0.010** | **[−0.0006, +0.0004] /drop** | **0.669** | **0.00** |

Reading:

- The output's +0.032 %/drop is dominated by the seating tail (see §1);
  restricted to drops 29–50 it is −0.021 %/drop. Accumulated over a 20-drop
  campaign the post-drop-28 bound is well under ~0.5 %.
- The **input itself drifts up** (+0.043 %/drop, p = 0.029), and input Δv
  rises too (+0.072 %/drop, p = 0.009, mean 2.61 m/s). The strike delivered by
  the auto-dropper got slightly harder over the 50 drops — a *rig-level*
  drift, not a mount or specimen effect. Because it is common-mode, it
  cancels in `T`.
- **`T` is the drift-immune observable**: slope indistinguishable from zero
  with a 95 % CI of ±0.0005/drop (±0.05 %/drop) — over a 20-drop campaign,
  |ΔT| ≤ ~1 % worst-case, centered on zero.

## 3) Regression reliability

- **Start-drop sensitivity:** sweeping the fit start over drops 3–13 moves the
  output slope monotonically +0.038 → +0.012 %/drop (all significant) — the
  scan is smooth, consistent with a decaying seating tail rather than a
  changepoint artifact. `T` stays n.s. at every start.
- **Autocorrelation:** Durbin-Watson on the drops-6–50 residuals is 0.43
  (output), 0.73 (input), 0.55 (T) — strong positive autocorrelation, i.e.
  the residuals carry the smooth seating curvature. That makes OLS
  *anti-conservative* (too eager to call trends), which cuts in opposite
  directions for the two conclusions: the flat-`T` verdict survives a
  fortiori; the output's tiny p-values should be read as "trend present"
  qualitatively, with the exponential fit (§1) as the better description of
  its shape.
- **Normality:** Shapiro-Wilk p = 0.23 / 0.07 / 0.18 (input / output / T) — no
  material violation.
- **Sample size:** n = 45 in the stabilized window (vs 19 in run #1) — the
  slope CIs are ~2× tighter; that, not new physics, is why sub-0.05 %/drop
  trends now reach significance.

## 4) Specimen damage / limitation check

Mount-robust indicators (see the [`prc1kn` health check](drop-test-prc1kn-health-check.md)
for why these can't be faked by seat/wax changes):

| indicator | mean | CV | slope (%/drop) | p | verdict |
|---|--:|--:|--:|--:|---|
| output pulse width | 1.49 ms | 0.40 % | −0.015 | <0.001 | flat† |
| ringdown dominant freq | 549 Hz | 1.10 % | −0.010 | 0.38 | **locked** |
| ringdown spectral centroid | 519 Hz | 15.7 % | +0.19 | 0.21 | flat w/ excursion‡ |
| pre-impact noise RMS (CH2/3/4) | 0.15–0.20 G | — | — | — | unchanged |

† The pulse width is quantized at the 8 µs sample step (all values are
1.480–1.504 ms, a 1–3-sample spread); the "significant" −0.015 %/drop slope
totals −0.75 % over 50 drops and points *shorter/stiffer* — the opposite of
damage (a cracked strut or cut tendon lengthens the pulse and lowers the
mode, f ∝ √k).

‡ Drops 16–19 show a transient high-frequency excursion (centroid 660–837 Hz,
dominant-freq blip to 580 Hz) that fully returns to baseline by drop 20. It
coincides with the inflection in the CH2/CH3 per-axis migration, so it reads
as a **seat micro-event** (the sensor shifting to a new orientation in the
wax), not a structural change — a structural shift would persist.

**Verdict: no damage.** Adding this run, `prc1kn` has taken ~98 recorded
drops (~48 across the four prior sessions + 50 here) at ~215–260 G CFC-180
with the ringdown mode still pinned at 549 Hz and the pulse width unchanged.
For BO-campaign timescales at 13 in, specimen wear-out remains undetectable —
on this (failed-print, PLA/TPU) dummy at least.

**Limitations observed in the data** (rig/mount, not the structure):

1. **Sensor rotation in the seat persists** — CH3 grows 1,023 → 1,285 G and
   CH4 2,945 → 3,376 G while CH2 wanders non-monotonically, all at
   near-constant resultant. Same loosening signature as run #1; the cable tie
   removes the *consequence* (fall-off) but not the *cause* (the sensor sits
   only halfway into the pocket — @ctrhjk's deeper-housing suggestion in the
   PR thread is the right fix).
2. **Rig-level input drift** (+0.04 %/drop peak, +0.07 %/drop Δv) — worth a
   look at the auto-dropper release mechanism / plate wax if
   output-at-fixed-input is ever preferred over `T`; `T` sidesteps it.
3. **T level is re-mount-dependent** — 1.215 (run #1) → 1.078 (this run) at
   the same nominal setup. Compare `T` only within a mount; never across
   re-waxings.

## 5) SOP recommendations

1. **Adopt the cable tie-off** — it converted a 30-drop-max campaign into a
   clean 50/50 and is free.
2. **Use `T` (per-drop output/input ratio) as the primary objective** — it
   needs no burn-in and is immune to the rig-level drift that both single
   channels carry. If output-only peak-g must be used, burn in **≥ 12–15
   drops** after every fresh wax application (τ was 12 here, 5 in run #1 —
   it varies per application, so re-run the changepoint scan each re-mount)
   or detrend against the input.
3. **Add a live seat-health check**: track the per-axis ratio (e.g. CH2/CH4)
   during long campaigns — it flagged the loosening ~14 drops before run #1's
   fall-off and shows the same slow rotation here.
4. **Deepen the key-seat pocket** (per @ctrhjk: the sensor only fits halfway)
   so the walls, not the wax film, register the sensor.

<sub>Caveats: n = 1 specimen and it is a deliberately-failed print — this
calibrates the mount/DAQ/rig, not geometry (T ≈ 1.08 is not a geometry
result); intact pre-tensioned prints may fatigue differently. 200 ms window
only; Δv is a partial-pulse integral; tri-axis orientation unverified (and
demonstrably drifting, per the migration); ringdown frequency resolution is
30.5 Hz (Welch), so mode shifts under ~6 % are not resolvable; raw input
peaks reach 50–79 % of the CH5 full scale (headroom OK this run).</sub>
