# Corrected-sensitivity accelerometer calibration data (issue #71 follow-up 2)

Third drop-tower series posted by @ctrhjk
([PR #74 comment 4664234492](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/74#issuecomment-4664234492)),
recorded 06/09/2026 under the TP4 session name *"Accelerometer Callibartion 2"*.

This run acts on the two fixes recommended after the
[06/08 co-located series](../accelerometer-calibration/):

1. **The per-channel sensitivities were re-entered from the calibration
   certificates** (the 06/08 run used placeholder values). The certificate
   single-axis sensitivity is **11.61 mV/G**, not the 0.25 mV/G placeholder —
   a `11.61 / 0.25 ≈ 46×` change, which is what had produced the spurious ~30×
   single-vs-tri ratio.
2. **The acrylic plates were removed and both sensors were bolted to the bare
   metal load**, on the same level ~1/4 in apart, single-axis on the left — a
   stiffer, genuinely co-located mount (per @ctrhjk; this also corrects the
   "bottom acrylic plate" assumption used for the 06/08 series).

## Acquisition settings (from @ctrhjk, all on a 5 V range)

| Channel | Sensor                   | Full scale | Sensitivity | Trigger  |
| ------- | ------------------------ | ---------- | ----------- | -------- |
| CH1     | single-axis (Z)          | 430.7 G    | 11.61 mV/G  | 430.66 G |
| CH2     | tri-axis X               | 7246.4 G   | 0.690 mV/G  | 1000 G   |
| CH3     | tri-axis Y               | 7496.3 G   | 0.667 mV/G  | 1000 G   |
| CH4     | tri-axis Z (impact axis) | 6812.0 G   | 0.734 mV/G  | 1000 G   |

Re-entering the high 11.61 mV/G single-axis sensitivity drops CH1's full scale to
only **430.7 G** (5 V / 11.61 mV/G), so CH1 now rails on every usable drop.

## Contents

The amplitude was swept by **drop height** (5 reps each); 5 in was too low to
trigger, so only 10/15/20 in are present:

- `raw/Test_10in_{1..5}.csv`
- `raw/Test_15in_{1..5}.csv`
- `raw/Test_20in_{1..5}.csv`
- `calibration_summary.csv` — derived per-drop raw and SAE J211 CFC-180 /
  CFC-1000 **impact-windowed** peaks, the tri-axis resultant, the CH1/CH4 scale
  factor, and a CH1 full-scale-clip flag.

Each time-domain CSV is the same TP4 format as the earlier series: 4 channels at
**125 kHz** (8 µs/sample) over **0.2 s / 25 000 samples**, in G, with a 2 %/4 ms
pre-trigger.

## Reproduce

```bash
python3 scripts/analysis/accelerometer_calibration2_analysis.py
```

Writes figures to `docs/figures/accelerometer-calibration-2/` and
`calibration_summary.csv` here. See
[`docs/accelerometer-calibration2-analysis.md`](../../../docs/accelerometer-calibration2-analysis.md)
for the full analysis.
