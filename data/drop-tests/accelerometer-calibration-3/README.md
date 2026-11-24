# Five-channel accelerometer calibration data (issue #71 follow-up 3)

Fourth drop-tower series posted by @ctrhjk
([PR #74 comment 4673864934](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/74#issuecomment-4673864934)),
recorded 06/10/2026 under the TP4 session name *"AC3"*.

This run acts on the single open blocker from the
[06/09 corrected-sensitivity series](../accelerometer-calibration-2/): CH1 (the
high-sensitivity 11.61 mV/G single-axis) clipped on every drop because even on the
10 V range its full scale is only ~861 G, while the raw impact transient is several
thousand G.

The fix is to add a **second, much lower-sensitivity single-axis accelerometer on
CH5** (1.059 mV/G → 9442.9 G full scale on 10 V), placed on the very left next to
the others. **CH1 and the tri-axis (CH2–CH4) were not moved** since the previous
run. This gives two single-axis units to compare against the tri-axis Z (CH4),
which is the reference and the only trigger source:

- **CH5 vs CH4** — the real cross-calibration (both unclipped, co-located).
- **CH1 vs CH5 / CH1 vs CH4** — diagnoses *why* CH1 clips, since CH1 and CH5 are
  both single-axis and co-located, differing only in sensitivity/range.

## Acquisition settings (from @ctrhjk, all on a 10 V range)

| Channel | Sensor                   | Full scale | Sensitivity | Trigger |
| ------- | ------------------------ | ---------- | ----------- | ------- |
| CH1     | single-axis (Z)          | 861.3 G    | 11.61 mV/G  | none    |
| CH2     | tri-axis X               | 14492.8 G  | 0.690 mV/G  | none    |
| CH3     | tri-axis Y               | 14992.5 G  | 0.667 mV/G  | none    |
| CH4     | tri-axis Z (impact axis) | 13624.0 G  | 0.734 mV/G  | 1000 G  |
| CH5     | single-axis (Z)          | 9442.9 G   | 1.059 mV/G  | none    |

All channels were moved to the **10 V** range (up from 5 V on the 06/09 run). CH4
is the only trigger source because the goal is the CH4–CH5 calibration.

## Contents

The amplitude was swept by **drop height** (5 reps each); 5 in was too low to
trigger, so only 10/15/20 in are present:

- `raw/Test_10in_{1..5}.csv`
- `raw/Test_15in_{1..5}.csv`
- `raw/Test_20in_{1..5}.csv`
- `calibration_summary.csv` — derived per-drop raw and SAE J211 CFC-180 /
  CFC-1000 **impact-windowed** peaks for all five channels, the tri-axis
  resultant, the CH4↔CH5 peak-time lag, the CH5/CH4 and CH1/CH4 scale factors, and
  per-channel full-scale-clip flags.

Each time-domain CSV is the same TP4 format as the earlier series, now with an
extra `CH5 Acc (G's)` column: **5 channels** at **125 kHz** (8 µs/sample) over
**0.2 s / 25 000 samples**, in G, with a 2 %/4 ms pre-trigger.

## Reproduce

```bash
python3 scripts/analysis/accelerometer_calibration3_analysis.py
```

Writes figures to `docs/figures/accelerometer-calibration-3/` and
`calibration_summary.csv` here. See
[`docs/accelerometer-calibration3-analysis.md`](../../../docs/accelerometer-calibration3-analysis.md)
for the full analysis.
