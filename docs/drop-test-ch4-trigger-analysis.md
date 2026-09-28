# CH4-trigger validation — 50 auto-drops on `RW5F61`

Analysis of the **CH4-trigger campaign** posted by @ctrhjk on
[PR #67](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67):
50 automatic drops at 13 in on specimen `RW5F61`, with the DAQ **trigger moved
from the base-plate single-axis (CH5) to the top-vertex key-seat drop-axis
channel CH4** at the same 1000 G level. Everything else matches the 100-drop
campaign (taped CH5, low-range bottom-vertex tri-axis CH6–8, cable tie-offs).

- Raw data + channel map: [`data/drop-tests/ch4-trigger/`](../data/drop-tests/ch4-trigger/)
- Script: [`scripts/analysis/drop_test_ch4_trigger_analysis.py`](../scripts/analysis/drop_test_ch4_trigger_analysis.py)
- Figures + machine-readable metrics:
  [`data/drop-tests/ch4-trigger/figures/`](../data/drop-tests/ch4-trigger/figures/)

All quoted peaks are SAE J211 CFC-180 (phaseless) unless labelled raw.

## 1. Trigger assessment — the CH4 trigger passes on every axis we can test

**50/50 captures are real drops. Zero spurious triggers, zero lost drops,
zero fall-offs.**

| trigger health metric | value | comment |
|---|---|---|
| real drops captured | **50/50** | vs 27/30 + 5 spurious in the (untaped) CH5-trigger 30-drop run |
| CH4 first crossing of 1000 G | **3.896 ± 0.002 ms** (range 3.896–3.904) | ±1 sample (8 µs) of jitter across the whole campaign |
| impact (TOP resultant argmax) | 3.96 ± 0.00 ms | perfectly consistent record alignment |
| CH4 raw \|peak\| | 3,472 ± 87 G (3,239–3,655) | **3.2–3.7× margin** over the 1000 G level |
| CH4 headroom vs full scale | max 26.8 % of 13,624 G FS | no saturation risk on the trigger channel |
| pre-crossing quiet | ≤ 4 G before 3.5 ms in every record | the only pre-crossing samples near the level are the impact rising edge itself |
| cadence | median 14 s (13–14 s), 50 drops in ~11 min | fastest campaign so far (100-drop ran at ~20 s) |

Details worth recording:

1. **Timing is deterministic.** The 1000 G crossing lands at sample 487
   (3.896 ms) in 49/50 records and sample 488 in the other — a single sample
   of jitter. The constant ~0.10 ms offset from the nominal 4.000 ms
   pre-trigger point is a fixed DAQ latency/definition offset, identical in
   every record, and harmless: it just means "t = 3.9 ms" is the trigger
   instant in these exports.
2. **No rattle-trigger exposure.** Before the impact rising edge the CH4
   channel sits at ≤ 4 G — three orders of magnitude below the level. The
   failure mode that produced 5 spurious captures in the 30-drop run (the
   detached CH5 firing on its own motion) has no analogue here: the trigger
   now lives on a sensor that is key-seated, waxed **and** cable-tied.
3. **Margin is comfortable and stable.** The worst-case crossing margin is
   3.2×, and the CH4 raw peak drifts by only ±2.5 % across 50 drops — no
   trend toward the level. (For comparison, CH5's raw peaks ran 5.5–8.1 kG =
   5.5–8× margin in the 100-drop run; CH4's 3.2–3.7× is smaller but far more
   than enough, with none of CH5's fall-off history.)

**Verdict: adopt the CH4 (1000 G) trigger as the SOP trigger.** It removes
the last single point of failure — the trigger no longer depends on the one
sensor (CH5) that has detached twice — at zero cost in capture quality,
timing stability, or cadence.

## 2. Consistency with the 100-drop campaign (same specimen, same rig)

Stabilized-phase values, this run vs the 100-drop (CH5-trigger) run:

| metric | 100-drop (CH5 trig) | this run (CH4 trig) |
|---|--:|--:|
| TOP output | 241.7 G (CV 1.01 %) | 226.7 G (CV 1.55 %) |
| CH5 plate | 252.6 G (CV 1.89 %) | 236.3 G (CV 1.15 %) |
| **T = TOP/CH5** | **0.957 (CV 2.12 %)** | **0.960 (CV 1.20 %)** |

**T = TOP/CH5 reproduces to 0.3 % across the trigger change** — strong
evidence the trigger relocation does not perturb the measurement, and further
confirmation that T is the robust cross-session quantity. (The ~6 % lower
absolute TOP/CH5 levels are the familiar re-setup/level shift between
sessions; absolute peaks remain mount-history-dependent.)

## 3. OLS drift — a common-mode rig softening that T cancels

The burn-in changepoint scan never reaches an n.s. TOP trend (the exponential
seating fit diverges — there is **no seating transient**); the trend is a
slow campaign-scale decline instead. Stabilized window taken as drops 11–50
(n = 40) per the ≥10-drop SOP:

| series | mean | CV | slope (%/drop) | p |
|---|--:|--:|--:|--:|
| TOP output (CH2–4) | 226.7 G | 1.55 % | −0.078 | 7.0e−05 |
| CH5 plate (taped) | 236.3 G | 1.15 % | −0.065 | 3.1e−06 |
| **T = TOP/CH5** | **0.960** | **1.20 %** | **−0.013** | **0.43 (n.s.)** |
| BOT input (CH6–8) | 163.8 G | 9.98 % | +0.264 | 0.052 (saturation-biased) |
| T\* = TOP/BOT | 1.401 | 12.71 % | −0.439 | 0.010 (saturation-biased) |

- **TOP and CH5 decline together** (−1.7 % and −2.5 % total over the
  campaign) and the plate input Δv falls in step (−0.075 %/drop,
  p = 1e−07) — the auto-dropper's strike got slightly softer over the 50
  drops, a *rig-level* drift. Because it is common-mode, **T is flat**
  (stabilized p = 0.43; full-series drops 1–50: 0.957, CV 1.25 %,
  +0.023 %/drop, p = 0.065 n.s.) — the mirror image of drift-calibration #2,
  where a strike that got *harder* also cancelled in T.
- Contrast with the 100-drop run's CH5 behaviour: there CH5 crept **up**
  while TOP stayed flat (tape seating), poisoning T with a −0.043 %/drop
  drift. This session the tape is past its seating phase and T carries no
  significant drift at all — consistent with the "burn the tape in" reading.
- Split-half check: drops 11–31 −0.034 %/drop (p = 0.39), drops 32–50
  −0.011 %/drop (p = 0.86) — the decline is too gentle to resolve in either
  half alone; reliability diagnostics (DW 1.7–2.6 on TOP/CH5/T, Shapiro
  n.s.) are the healthiest of any campaign yet.

## 4. Known issues carried over (not trigger-related)

1. **The bottom-vertex tri-axis is still under-ranged**: CH8 exceeds its
   989.1 G full scale on 40/50 drops (median 105 % FS), CH7 on 8/50, CH6 on
   6/50. BOT peaks, T\* and BOT Δv remain saturation-biased — the ≥3 kG
   swap (or a lower drop height) is still pending.
2. **The bottom seat is still rotating**: CH6 collapses 849 → 269 G raw
   (−2.57 %/drop, p = 3e−08) at near-constant resultant — the same in-seat
   rotation signature as before. Deeper key-seat pockets remain the fix;
   resultant-based metrics stay robust to it.
3. **Pre-impact noise RMS on the TOP axes roughly doubles** across the
   campaign (0.2 → 0.55 G on CH2). Still ≈ 0.004 % of full scale and far
   below anything that could touch the trigger, but worth a glance at the
   top seat/cable before the next campaign.

## 5. Specimen `RW5F61` — no damage signature at ~180 cumulative drops

Mount-robust indicators over the 50 drops:

| indicator | result | verdict |
|---|---|---|
| output pulse width | 1.51 ms, CV 0.83 %, −0.014 %/drop (p = 0.079) | flat — no softening; the 100-drop run's +2.7 % widening did **not** continue |
| ringdown dominant freq | alternates between two mode clusters, ~520–700 Hz and ~1,340–1,740 Hz (≈25 drops each); no trend (p = 0.97) | two structural modes of comparable ringdown energy trading dominance drop-to-drop — a spectral-estimate coin-flip, not a stiffness change |
| ringdown spectral centroid | −0.306 %/drop, p = 0.062 (n.s.) | no significant migration |
| plate input Δv | 2.79 m/s, CV 1.64 % | consistent with 13 in + rig |

`RW5F61` now has **180 conducted / 177 captured drops** with no accumulating
damage signature. Note the pulse-width watch item from the 100-drop campaign
(+2.7 % within-campaign widening) reversed here (flat/slightly narrower),
supporting the "per-campaign mount/seating effect" reading over early tendon
relaxation.

## 6. Recommendations

1. **Adopt the CH4 1000 G trigger as SOP** — validated at 50-drop scale:
   50/50 capture rate, ±1 sample timing jitter, 3.2–3.7× margin, no
   saturation exposure, and the trigger no longer rides the fall-off-prone
   plate sensor. Record `trigger = CH4 (top key-seat, drop axis)` in the
   protocol doc.
2. **Keep CH5 as a measurement channel only.** Its taped mount is fine for
   the input reference; nothing critical depends on it any more.
3. **Swap the bottom-vertex sensor to a ≥3 kG-range unit** before using
   BOT/T\* quantitatively (unchanged from the 100-drop findings).
4. **Keep the ≥10-drop burn-in.** No seating transient appeared this run,
   but the rig-level common-mode drift (and the 100-drop tape seating)
   both front-load; T needs no burn-in either way.
5. This closes the instrumentation-qualification arc: trigger, mounts,
   retention, burn-in and drift floor are all characterized. The next
   campaign can be the **geometry-discrimination** one — n ≥ 5 distinct
   intact prints, vertex key-seat output, T = TOP/CH5 objective.

## Caveats

n = 1 specimen and `RW5F61` is still a failed print (top-tendon bubbles) —
this qualifies the trigger/DAQ, not geometry (T ≈ 0.96 is not a geometry
result). 200 ms window; Δv partial-pulse; tri-axis orientations unverified
(bottom seat demonstrably rotating); BOT quantities saturation-biased
throughout; the "rig softening" reading of the common-mode TOP/CH5 decline is
inferred from Δv + the T cancellation, not an independent release-energy
measurement.
