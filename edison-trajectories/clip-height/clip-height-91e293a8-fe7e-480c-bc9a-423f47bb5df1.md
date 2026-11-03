**Headline**

Your base-plate numbers reproduce from the attached CSV, and the diagnostic separates cleanly into "instrumentation works" vs "acrylic-plate load path is broken." The acrylic-plate measurement failure is almost certainly a load-path problem, not the sensor, DAQ, or trigger level alone.

**Self-contained report:** data_entry:clip-height-report-md-ps9g  
**Diagnostic figure:** data_entry:base-plate-diagnostic-png-xjrm  
**Files saved locally:** `clip_height_report.md`, `base_plate_diagnostic.png`

---

**A. Independent verification of base-plate numbers (Accelerometer_check_Signal1.csv)**

Baseline-corrected using mean over t < 3 ms. Impact search restricted to the first 10 ms. SAE J211 CFC filters implemented as 2-pole Butterworth, cutoff = 1.65 × CFC, applied phaseless via filtfilt.

- CH4 impact time: 3.912 ms (matches 4 ms pre-trigger).
- First-10-ms peaks:

| Channel | Raw | CFC-1000 | CFC-180 |
|---|---:|---:|---:|
| CH2 | 599.4 G | 44.6 G | 11.8 G |
| CH3 | 710.5 G | 55.4 G | 5.0 G |
| **CH4** | **3071.7 G** | **1154.4 G** | **276.9 G** |

- CH4 half-amplitude pulse width: 0.38 ms (CFC-1000), 1.52 ms (CFC-180). Your reported ~1.5 ms matches CFC-180.
- CH4 partial-pulse Δv: 3.364 m/s on the narrow CFC-1000 half-amplitude window (3.82–4.19 ms), which reproduces your ~3.3 m/s. The broader first-pulse zero-crossing window gives ~3.95 m/s — so report the window definition explicitly.
- Free-fall from 13 in (0.3302 m) is sqrt(2gh) = 2.545 m/s. Measured Δv is 1.32× (narrow window) to 1.55× (broad window) the free-fall value. Plausible for a bungee-assisted tower with some rebound captured in the integration window.
- CH4 dominates the off-axis channels at CFC-180 by 23.5× over CH2 and 55.5× over CH3, fully consistent with a mostly axis-aligned base-plate hit. Raw off-axis peaks of ~600–700 G are accelerometer-ringing / cross-axis contamination, exactly the reason CFC-180 is the right structural metric here.

**B. Most likely physical cause and how to confirm**

Most likely cause: the acrylic top plate is partly seated on or damped by the bungee-restrained specimen, so the strike is not a sharp, stiff, discrete shock at the plate — it is a slow, distributed loading the plate-mounted sensor sees at sub-trigger amplitude. Evidence chain:

1. 0/8 triggers across a wide 0.5–2.0 in clip-height sweep — a clip-only fix would have produced at least some recoveries.
2. The same DAQ/CH4 trigger produced 3.07× the trigger level on the base plate.
3. The same instrumentation chain produced clean 230–285 G CFC-180 peaks vertex-mounted in the prior series.
4. Only the acrylic transmitted-plate configuration fails.

Candidate sources, ranked:
- Plate not transmitting shock efficiently because the load path is mechanically ambiguous (preload, seating, distributed contact): strongest explanation. Confirm with simultaneous base + transmitted channels, hard top-stop or captive guided plate, high-speed video.
- Trigger level 1000 G too high for the transmitted path: contributes to the symptom but is downstream of the load-path problem. Confirm by lowering trigger to 100–200 G or running free-run capture.
- Edge-of-plate accelerometer position: possible secondary contributor but cannot explain 0/8. Confirm with a second sensor at plate centerline.
- Orientation error: unlikely to be primary because base-plate and vertex configurations work. Confirm by recording all three axes and computing vector magnitude.

**C. Prioritized recommendations**

1. Drop the 1000 G transmitted-plate trigger. Either trigger from the base/input channel, or free-run with sufficient pre/post buffer.
2. Record simultaneous input (base or carriage) and transmitted (plate or vertex) channels on every drop. This is what gives you a real transmissibility, Δv-in vs Δv-out, and a transfer-function-style metric for Bayesian optimization.
3. Redesign the load path: guided/captive top plate on linear bushings, a defined hard top-stop, clip geometry that retains the plate but does not preload it onto the specimen, bungees arranged to go slack at impact.
4. Improve plate-side mounting if you keep it: centerline placement above the contact, stiff stud mount where feasible, careful axis alignment.
5. Treat plate acoustic impedance/thickness as second-order — the dominant defect at the moment is mechanics, not material.
6. If a clean load path cannot be achieved quickly: abandon acrylic transmitted-g as the BO objective and use vertex-mounted CFC-180 peak g (already proven clean at 230–285 G) as the primary acceleration response metric, with SEA derived from energy bookkeeping. The acrylic-plate metric can return after a fixture redesign.

**D. Standards tie-back and additional captures**

- SAE J211: your CFC-180 = structural number rule is appropriate for this lightly damped lattice with ringing-dominated raw peaks. Use phaseless Butterworth (you do) and restrict peak search to the first ~10 ms (you do); the record here also contains a clear secondary rebound near 181.49 ms (~417 G raw) that would contaminate a global max.
- ASTM D7136: not a direct match for tensegrity unit cells, but the practice of a well-defined striker/specimen geometry with simultaneous input + response instrumentation directly applies — your current acrylic-plate setup is missing the controlled contact definition.
- ASTM D3332: cushion-style performance curves require repeatable input pulses and replication; any transmitted-g optimization target needs both before it can be trusted.
- ISO 5347: sensor mounting and surface preparation dominate high-frequency results; relevant if you keep the plate-mounted approach.

Additional captures to add before trusting transmitted-g:
- Simultaneous input + transmitted accelerometer on every drop.
- n ≥ 5 repeats per condition.
- Longer record if you want true ringdown — 200 ms already captures a rebound event at 181 ms; for ~10 s you will need a different acquisition mode.
- Synchronized high-speed video of the plate–specimen contact.
- No-specimen and rigid-dummy-specimen baselines to isolate fixture from tensegrity dynamics.
- Trigger-on-input, analyze-response. Report axis vector magnitude as a diagnostic alongside the on-axis channel.

---

**Discretionary decisions**
- Baseline-correction window: mean over t < 3 ms (well before the ~3.9 ms trigger arrival).
- CFC filter implementation: 2-pole Butterworth with cutoff = 1.65 × CFC frequency, applied forward-backward (`scipy.signal.filtfilt`). Approximates SAE J211 phaseless behavior; small numerical differences from TP4's native implementation are possible.
- Peak search window: first 10 ms only, as you requested.
- Pulse width definition: half-amplitude full-width of the main pulse.
- Partial-pulse Δv window: CH4 CFC-1000 half-amplitude width (3.82–4.19 ms) for the headline number to match your ~3.3 m/s; full first-pulse zero-crossing window reported alongside (~3.95 m/s) because the result is window-sensitive.
- Trapezoidal integration for Δv (np.trapezoid on the CFC-1000 signal scaled by 9.80665 m/s²/G).
- "First 10 ms" max chosen over global 200 ms max specifically because the record contains a secondary rebound event near 181.49 ms (~417 G raw) that would contaminate a global statistic.
- n = 1 drop for the base-plate check; uncertainty intervals not computed (one event).