# Drop-tower accelerometer "tuning" analysis (issue #71)

Analysis of the 06/02/2026 drop-tower test series that @me-madsen and @ctrhjk ran
to standardize the setup and to understand why the **single-axis** and
**tri-axis** accelerometers do not report the same acceleration.

- **Raw data:** [`data/drop-tests/accelerometer-tuning/raw/`](../data/drop-tests/accelerometer-tuning/raw)
  (TP4 exports: one series table `06.02.2026.csv` + 13 time-domain
  `06.02.2026_SignalN.csv` files).
- **Script:** [`scripts/analysis/accelerometer_tuning_analysis.py`](../scripts/analysis/accelerometer_tuning_analysis.py)
  (`python3 scripts/analysis/accelerometer_tuning_analysis.py`).
- **Derived table:** [`data/drop-tests/accelerometer-tuning/peak_summary.csv`](../data/drop-tests/accelerometer-tuning/peak_summary.csv).
- **Figures:** [`docs/figures/accelerometer-tuning/`](figures/accelerometer-tuning).

## Data format

Each time-domain file is a 4-channel record sampled at **125 kHz** (8 µs/sample)
over a **0.2 s / 25 000-sample** window, in **G**. `SignalN` is event `N` from the
table export. Channel mapping **inferred from the data** (the per-test position
labels promised in the issue had not been posted at analysis time, so please
confirm):

| Channel | Sensor (inferred)                |
| ------- | -------------------------------- |
| CH1     | single-axis accelerometer        |
| CH2     | tri-axis X                       |
| CH3     | tri-axis Y                       |
| CH4     | tri-axis Z (impact axis)         |

CH2/CH3/CH4 move together as a group (clearest in events 11–12), which is the
signature of one tri-axis sensor, while CH1 behaves independently — hence the
single-axis = CH1 assignment.

## Method

Drop-tower shock records are dominated by **mount/sensor ringing**, so the *raw*
peak G is not a physically meaningful number. The script applies the
**SAE J211** Channel Frequency Class (CFC) phaseless 4-pole Butterworth filter
(forward + backward) at two classes:

- **CFC 1000** (-3 dB ≈ 1.65 kHz) — peak acceleration / `g_max`.
- **CFC 180** (-3 dB ≈ 300 Hz) — rigid-body pulse, Δv, structural response.

The same filter is applied identically to every channel so they can be compared.

## Key findings

### 1. The single-axis channel (CH1) is **saturating** (clipping) on hard hits

In events **2, 3 and 5** CH1 rails at an essentially identical ceiling
(**8803 / 8806 / 8806 G**) and sits on a flat plateau for ~0.2 ms — the textbook
signature of a sensor/DAQ that has hit full scale. The recorded "peak" is a clip
level, not the true acceleration (the real peak is higher and unknown).

![CH1 saturation](figures/accelerometer-tuning/ch1_saturation.png)

**This alone makes the two sensors impossible to match in those events**: you are
comparing a clipped channel against an unclipped one. Any sensitivity adjustment
that pushes CH1 higher just clips harder.

### 2. Raw peaks are ringing-dominated — compare filtered values, not raw

Across all impact events the raw traces carry large broadband ringing (PSD energy
out past 20 kHz, with mount-resonance peaks around ~18–20 kHz on CH1), riding on a
much smaller rigid-body pulse below ~2 kHz. Filtering changes the peaks
dramatically (e.g. event 1 CH1: 2576 G raw → 483 G CFC-180; CH4: 1280 G raw → 312 G).

![PSD of impact events](figures/accelerometer-tuning/psd_impact_events.png)

### 3. CH4 carries a fixed ~4.2 ms artifact (trigger / magnet-release)

CH4 peaks at **~4.0–4.4 ms in nearly every event** (1, 3, 4, 5, 9, 13), independent
of the actual impact. This matches the fixed trigger/magnet-release transient seen
in the earlier campaign (issue #36) and is **not** an impact measurement. In events
11–12 *all four* channels peak at exactly 3.90 ms, i.e. a common synchronized
transient rather than a mechanical impact. Analysis windows should be gated to the
real impact and this trigger artifact fixed at the source.

### 4. The sensors were in **different positions** per test, so this data cannot
cross-calibrate them

Because the accelerometers were swapped/relocated between runs (and the per-event
position labels were not posted), most events show one sensor seeing a large hit
while the other sees almost nothing — they were not experiencing the same input:

| Pattern                                   | Events        |
| ----------------------------------------- | ------------- |
| Both sensors see a comparable big impact  | 1, 4          |
| CH1 huge & saturated, tri-axis quiet      | 2, 3, 5       |
| CH1 moderate (~270 G), tri-axis quiet     | 9, 10, 13     |
| CH1 ~0, tri-axis sees the hit (~34–44 G)  | 11, 12        |
| No / aborted drop (noise only)            | 6, 7, 8       |

Only **events 1 and 4** have both sensors reading a comparable large impact. There
the single-axis (CH1) reads about **1.5×** the tri-axis impact axis (CH4) on the
CFC-180 pulse (483/312 and 473/316). That is a useful number but it is *not* a
clean co-located calibration — even events 1/4 may be different mounting locations.

Per-event CFC-1000 peaks, CH1 vs CH4:

![Peak comparison](figures/accelerometer-tuning/peak_comparison_ch1_ch4.png)

## Recommendations ("tuning" the sensors)

1. **Stop the clipping first.** The single-axis channel is railing at ~8.8 kG.
   Either lower its gain / increase its range, or use a sensor whose full scale
   comfortably exceeds the expected peak. Confirm the **sensitivity (mV/G) entered
   in TP4 matches each sensor's calibration sheet** — a wrong sensitivity value is
   the most common cause of two sensors disagreeing by a fixed factor.
2. **Do a real co-location cross-calibration.** Mount both sensors **rigidly,
   back-to-back on the same plate**, with their sensitive axes aligned to the drop
   direction, and run several **repeatable, sub-saturation** drops. Apply the same
   CFC filter to both and regress CH1 against CH4 — a single slope is the scale
   factor to reconcile them. Do this before trusting any swapped-position numbers.
3. **Always compare filtered peaks, not raw.** Use CFC 1000 for `g_max` and
   CFC 180 for Δv / structural response, applied identically to both channels.
   Raw peaks are ringing/artifact dominated and will never agree.
4. **Fix the mounting resonance.** The broadband ringing out to ~20 kHz points to a
   compliant mount/adapter. Use a stud or thin stiff-adhesive mount, minimize
   adapter mass between sensor and plate, and strain-relieve the cables.
5. **Separate the trigger/magnet artifact.** CH4's fixed ~4.2 ms spike is the
   magnet-release transient, not impact — gate the analysis window to the real
   impact and address the trigger coupling at the source.
6. **Label every run.** Record which sensor, which position, and which orientation
   for each event so swapped-position tests can be interpreted.
7. Sample rate (125 kHz) is adequate; keep both channels on the same rate and
   anti-alias settings.
