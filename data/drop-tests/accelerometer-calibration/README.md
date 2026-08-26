# Co-located accelerometer cross-calibration data (issue #71 follow-up)

Second drop-tower series posted by @ctrhjk
([PR #74 comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/74#issuecomment-4663450421)),
recorded 06/08/2026 under the TP4 session name *"Accelerometer callibaration"*.

Unlike the 06/02/2026 [`accelerometer-tuning`](../accelerometer-tuning/) series
(sensors swapped between positions), here **both accelerometers are mounted
directly on the bottom acrylic plate** — the co-located, back-to-back arrangement
recommended in the tuning analysis
([per issue #71](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/71#issuecomment-4634258100)) —
so the two sensors see the same rigid-body input and can be cross-calibrated.

## Acquisition settings (from @ctrhjk)

| Channel | Sensor                    | Full scale | Sensitivity |
| ------- | ------------------------- | ---------- | ----------- |
| CH1     | single-axis accelerometer | 20,000 G   | 0.25 mV/G   |
| CH2     | tri-axis X                | 10,000 G   | 1.0 mV/G    |
| CH3     | tri-axis Y                | 10,000 G   | 1.0 mV/G    |
| CH4     | tri-axis Z (impact axis)  | 10,000 G   | 1.0 mV/G    |

CH1 was stepped up to a **20,000 G** full scale (the tuning-analysis
recommendation, after the 10,000 G part saturated at ~8.8 kG in the 06/02 series).

## Contents

- `raw/500G_Signal5.csv` — trigger level **500 G**. @ctrhjk raised the trigger
  after an early-measurement issue, so this is a low-amplitude / aborted capture
  and is **excluded from the cross-calibration regression**.
- `raw/1000G_Signal{6,7,9,12,14,15,17}.csv` — trigger level **1000 G**; seven
  repeated clean drops used for the cross-calibration. (Intermediate event
  numbers correspond to non-drop captures, e.g. the hoist raising, and were not
  posted.)
- `calibration_summary.csv` — derived per-event raw and SAE J211 CFC-180 /
  CFC-1000 **impact-windowed** peaks, the tri-axis resultant, the CH1/CH4 scale
  factor, and a CH1 full-scale-clip flag.

Each time-domain CSV is the same TP4 format as the 06/02 series: 4 channels at
**125 kHz** (8 µs/sample) over **0.2 s / 25 000 samples**, in G.

## Reproduce

```bash
python3 scripts/analysis/accelerometer_calibration_analysis.py
```

Writes figures to `docs/figures/accelerometer-calibration/` and
`calibration_summary.csv` here. See
[`docs/accelerometer-calibration-analysis.md`](../../../docs/accelerometer-calibration-analysis.md)
for the full analysis.
