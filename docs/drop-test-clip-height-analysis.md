# Clip-height sweep & base-plate accelerometer check — analysis

Analysis of @ctrhjk's two follow-up diagnostics (PR comments 4794351098 and
4794438322) on the recurring "the accelerometer on the acrylic plate never
registers an impact above its 1000 G trigger" problem first seen in the
[vertex-acrylic series](../data/drop-tests/vertex-acrylic/).

- Data + setup: [`data/drop-tests/clip-height/`](../data/drop-tests/clip-height/)
- Script: [`scripts/analysis/drop_test_clip_height_analysis.py`](../scripts/analysis/drop_test_clip_height_analysis.py)
- Figures: [`data/drop-tests/clip-height/figures/`](../data/drop-tests/clip-height/figures/)
- Edison ANALYSIS cross-check: [`edison-trajectories/clip-height/`](../edison-trajectories/clip-height/) (task `91e293a8`)

## What was run

1. **Clip-height sweep** (no usable CSV). Three extra bungee cords cured the
   earlier specimen fly-off; the tri-axis accelerometer was placed on the
   acrylic plate (vertex below) and the retaining clips swept across
   **0.5 / 1.0 / 1.5 / 2.0 in** above the plate, two drops each, on a "Practice"
   specimen. **None of the eight drops triggered** (no acceleration above the
   1000 G CH4 trigger), so there is only video — no waveform to analyze. Raising
   the clips alone did **not** restore a triggered measurement.

2. **Base-plate accelerometer check** (one CSV). The tri-axis accelerometer was
   moved onto the **bottom (base) plate** — no acrylic plate in the load path —
   and dropped from **13 in**. This produced
   [`Accelerometer_check_Signal1.csv`](../data/drop-tests/clip-height/raw/Accelerometer_check_Signal1.csv).

## Base-plate result

Impact located on the triggered CH4 channel at t = 3.91 ms (windowed within the
first 10 ms, not a global 0.2 s max — the 200 ms record also holds a ~417 G
secondary rebound near 181 ms that would contaminate a global statistic).
Baseline-corrected on the pre-impact samples; SAE J211 phaseless Butterworth
filtering (CFC-1000 ≈ 1650 Hz, CFC-180 ≈ 300 Hz).

| channel | raw \|g\| | CFC-1000 | CFC-180 | half-width | Δv |
|---|--:|--:|--:|--:|--:|
| CH2 (off-axis) | 599 | 45 | 10 | 0.41 ms | 0.03 m/s |
| CH3 (off-axis) | 710 | 55 | 5 | 1.30 ms | 0.05 m/s |
| **CH4 (triggered, drop axis)** | **3072** | **1154** | **280** | **1.49 ms** | **3.28 m/s** |

- **CH4 raw peak (3072 G) is 3.1× the 1000 G trigger** — the sensor and DAQ
  register a clean impact when the load reaches them directly.
- CH4 dominates the off-axis CH2/CH3 by ~23–55× at CFC-180, consistent with an
  axis-aligned base-plate hit; the ~600–700 G raw off-axis peaks are
  accelerometer ringing / cross-axis contamination (the reason CFC-180 is the
  structural number).
- Windowed Δv ≈ 3.3 m/s is 1.3–1.6× the 13 in free-fall value (2.5 m/s),
  plausible for the **bungee-assisted** tower with some rebound in the
  integration window.

These numbers were independently reproduced by Edison's data-analysis crow from
the same CSV (CH4 raw 3071.7 G, CFC-1000 1154.4 G, CFC-180 276.9 G, Δv 3.36 m/s).

## Interpretation

The failure is in the **load path, not the sensor, DAQ, or trigger level**.
Evidence chain:

1. 0/8 triggers across a wide 0.5–2.0 in clip-height sweep — a clip-only fix
   would have recovered at least some drops.
2. The same DAQ + CH4 trigger gives 3.1× over-trigger on the base plate.
3. The same instrumentation chain gave clean 230–285 G CFC-180 peaks
   vertex-mounted in the prior series.
4. Only the acrylic transmitted-plate configuration fails.

The most likely physical cause is that the acrylic top plate is **seated on / is
damped by the bungee-restrained specimen**, so the strike is a slow, distributed,
sub-trigger load rather than a sharp shock at the plate. The 1000 G trigger
being too high is a real but downstream contributor; edge-of-plate position and
orientation are at most secondary (they cannot explain 0/8, and the base-plate
and vertex configurations both work).

## Recommendations (prioritized)

1. **Drop or relocate the transmitted-plate trigger.** Trigger off the
   base/input channel, or free-run with enough pre/post buffer; if a CH4 trigger
   is kept on the plate, lower it to ~100–200 G.
2. **Record simultaneous input + transmitted channels on every drop** (base or
   carriage vs plate or vertex). This yields a real transmissibility / Δv-in vs
   Δv-out and a transfer-function metric for the BO objective.
3. **Redesign the load path** so the plate actually strikes the specimen:
   captive top plate on **linear bushings**, a defined **hard top-stop**, clip
   geometry that retains the plate without preloading it onto the specimen, and
   bungees arranged to go slack at impact.
4. **Improve plate-side mounting** if kept: centerline placement above the
   contact, a stiff stud mount where feasible, careful on-axis alignment (ISO
   5347). Treat acrylic thickness/impedance as second-order — the dominant
   defect is mechanics, not material.
5. **Fallback:** if a clean load path can't be achieved quickly, use the
   already-proven **vertex-mounted CFC-180 peak g** (230–285 G) as the primary
   acceleration response for BO, with SEA from energy bookkeeping; revisit the
   acrylic transmitted-g metric after a fixture redesign.

Standards tie-back (per Edison): SAE J211 (CFC-180 structural number, phaseless
Butterworth — already followed), ASTM D7136 instrumented drop-weight (controlled
striker/specimen contact + simultaneous input/response — currently missing),
ASTM D3332 cushion curves (need repeatable input pulses + replication), ISO 5347
(mounting/surface prep dominate high-frequency results). Add a full ringdown
capture mode, n ≥ 5 repeats, no-specimen / rigid-dummy baselines, and
synchronized high-speed video before trusting any transmitted-g objective.

## Caveats

- n = 1 base-plate drop; no uncertainty interval.
- The clip-height sweep has no waveform data (no trigger), so its conclusion
  rests on the 0/8 trigger count plus the base-plate / vertex contrast.
- Partial-pulse Δv is window-sensitive (3.3 m/s narrow half-amplitude window vs
  ~3.95 m/s broad zero-crossing window).
- CH5 (single-axis) was not used in either experiment; the going-forward sensor
  comparison still rests on the vertex-acrylic series.
