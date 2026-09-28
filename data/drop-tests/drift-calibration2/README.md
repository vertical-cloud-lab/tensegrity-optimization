# Drift-calibration #2 auto-drop tests (specimen `prc1kn`, 50 drops)

Raw TP4 accelerometer exports for the **second drift-calibration** run by
@ctrhjk, posted on
[PR #67](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67).

Direct follow-up to the [30-drop drift-calibration run](../drift-calibration/README.md).
This run repeats the OLS drift-rate experiment at larger n — **50 drops
conducted automatically** at 13 in (~17 s cadence from the per-file TP4
`EventTime` stamps: events 1→50 span 21:16:27→21:30:27, ~14 min) — and also
qualifies whether a 50+-drop auto campaign is feasible. Same dummy specimen
(`prc1kn`, a deliberately-failed print with bubbles in its TPU cable), used to
exercise the mount/DAQ/rig, **not** to compare geometry.

**New this run:** the tri-axis output sensor's **cable is tied off to the iron
rod**, so cable pull can't drag the sensor out of the key-seat. Unlike run #1
(fell off at drop 26), the sensor **stayed attached for all 50 drops**.

## Recording setup

One specimen, **fifty drops** (`Signal{1..50}` = drops 1…50, contiguous
captures), drop height **13 in**, drops released automatically. Channels and
DAQ identical to the input-output / key-seat / wax / drift-calibration series.

| Channel | Sensor | Mount | Role | Full scale (G) | Sensitivity (mV/G) | Trigger |
|---|---|---|---|--:|--:|---|
| CH2 | tri-axis | vertex **key-seat + wax**, cable tied | output | 14492.8 | 0.69  | No |
| CH3 | tri-axis | vertex **key-seat + wax**, cable tied | output | 14992.5 | 0.667 | No |
| CH4 | tri-axis | vertex **key-seat + wax**, cable tied | output | 13624.0 | 0.734 | No |
| CH5 | single-axis | base plate (wax) | **input** | 9442.9 | 1.059 | **Yes** (1000 G) |

All channels AC-coupled, ICP on, Half-Sine waveform analysis. DAQ: record time
200 ms, 125 kHz (8 µs), 25000 samples, 2 % (4 ms) pre-trigger. Trigger is on CH5
(the single-axis input on the base plate).

## Files

Each CSV is a TP4 Time-Domain export: a short header block, then columns
`Time (sec), CH2 Acc (G's), CH3 Acc (G's), CH4 Acc (G's), CH5 Acc (G's)`.

| Files | Drops | Output-sensor state |
|---|---|---|
| `raw/drift_calibration2_Signal{1..50}.csv` | 1–50 | attached (all valid) |

**File-name note:** the original exports were named
`drift calibration2_Signal{1..50}`. They are renamed here to
`drift_calibration2_Signal{n}.csv` and map directly to drops 1…50.

## Analysis

- `figures/` — plots + `drift_calibration2_metrics.json` from
  [`scripts/analysis/drop_test_drift_calibration2_analysis.py`](../../../scripts/analysis/drop_test_drift_calibration2_analysis.py)
  (burn-in changepoint scan + exponential seating fit, stabilized-phase OLS
  with reliability checks, per-axis migration, and the mount-robust specimen
  damage indicators from the `prc1kn` health check).
- Findings and SOP implications:
  [`docs/drop-test-drift-calibration2-analysis.md`](../../../docs/drop-test-drift-calibration2-analysis.md).

Regenerate with:

```bash
pip install numpy scipy matplotlib
python scripts/analysis/drop_test_drift_calibration2_analysis.py
```

## Notes from @ctrhjk

1. The 50 drops were **conducted automatically**; drop height 13 in; all other
   settings identical to the first drift-calibration run.
2. The accelerometer **did not fall off** — the cable coming out of the
   accelerometer was fixed to the iron rod so the sensor can't be pulled out
   of the seat by its cable.
3. `prc1kn` is the dummy/failed-print specimen used for mount/DAQ validation,
   not geometry comparison.
4. Goals repeated from run #1: identify the burn-in/stabilization phase, OLS
   the stabilized-phase drift rate, verify regression reliability — plus check
   the specimen for damage/limitations after the accumulated campaigns.
