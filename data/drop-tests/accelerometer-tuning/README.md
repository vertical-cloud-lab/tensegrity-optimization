# Accelerometer "tuning" drop-tower data (issue #71)

Raw TP4 exports from the 06/02/2026 drop-tower series comparing the single-axis
and tri-axis accelerometers, plus derived products.

## Contents

- `raw/06.02.2026.csv` — TP4 series **table** export: one row per event with the
  per-channel peak `Accel` (G), pulse `Duration` (ms) and `Delta V` (in/sec).
- `raw/06.02.2026_SignalN.csv` — TP4 **time-domain** export for event `N`
  (N = 1..13): 4 channels (CH1–CH4) sampled at 125 kHz for 0.2 s (25 000 samples), in G.
- `peak_summary.csv` — derived per-event raw and SAE J211 CFC-180 / CFC-1000 peaks,
  tri-axis resultant, CH1/CH4 ratio, and a CH1 saturation flag.

## Channel mapping (inferred — confirm)

| Channel | Sensor                    |
| ------- | ------------------------- |
| CH1     | single-axis accelerometer |
| CH2     | tri-axis X                |
| CH3     | tri-axis Y                |
| CH4     | tri-axis Z (impact axis)  |

## Reproduce

```bash
python3 scripts/analysis/accelerometer_tuning_analysis.py
```

Writes figures to `docs/figures/accelerometer-tuning/` and `peak_summary.csv` here.

See [`docs/accelerometer-tuning-analysis.md`](../../../docs/accelerometer-tuning-analysis.md)
for the full analysis and troubleshooting.
