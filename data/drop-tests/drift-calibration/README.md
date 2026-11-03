# Drift-calibration auto-drop tests (specimen `prc1kn`, 30 drops)

Raw TP4 accelerometer exports for the **drift-calibration** run by @ctrhjk,
posted on [PR #67](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67).

Direct follow-up to the [burn-in wax run](../burn-in-wax/README.md). This is the
preliminary experiment designed for the OLS drift-rate analysis: **30 drops
conducted automatically** at 13 in (~15 s cadence from the per-file TP4
`EventTime` stamps: events 1→30 span 01:08:06→01:15:29), using the same dummy
specimen (`prc1kn`, a deliberately-failed print with bubbles in its TPU cable) to
exercise the mount/DAQ, **not** to compare geometry. Goals:

1. define the **burn-in drop count** from where the initial seating transient
   flattens into a gradual trend;
2. measure the system's **inherent post-burn-in drift rate** by OLS on the
   stabilized phase only;
3. qualify the **reliability** of that regression.

During the run the tri-axis **output sensor fell off the key-seat housing**
(~26th drop per @ctrhjk; the data confirm the output collapses to noise from
drop 26 onward, with a pre-fall-off anomaly at drop 25). A movie-mode RX100 IV
video of the whole run exists but shut off partway and is too large to upload;
it is not committed.

## Recording setup

One specimen, **thirty drops** (`Signal{1..30}` = drops 1…30, contiguous
captures), drop height **13 in**, drops released automatically. Channels and
DAQ identical to the input-output / key-seat / wax series.

| Channel | Sensor | Mount | Role | Full scale (G) | Sensitivity (mV/G) | Trigger |
|---|---|---|---|--:|--:|---|
| CH2 | tri-axis | vertex **key-seat + wax** | output | 14492.8 | 0.69  | No |
| CH3 | tri-axis | vertex **key-seat + wax** | output | 14992.5 | 0.667 | No |
| CH4 | tri-axis | vertex **key-seat + wax** | output | 13624.0 | 0.734 | No |
| CH5 | single-axis | base plate (wax) | **input** | 9442.9 | 1.059 | **Yes** (1000 G) |

All channels AC-coupled, ICP on, Half-Sine waveform analysis. DAQ: record time
200 ms, 125 kHz (8 µs), 25000 samples, 2 % (4 ms) pre-trigger. Trigger is on CH5
(the single-axis input on the base plate).

## Files

Each CSV is a TP4 Time-Domain export: a short header block, then columns
`Time (sec), CH2 Acc (G's), CH3 Acc (G's), CH4 Acc (G's), CH5 Acc (G's)`.

| Files | Drops | Output-sensor state |
|---|---|---|
| `raw/drift_calibration_Signal{1..24}.csv` | 1–24 | attached (valid) |
| `raw/drift_calibration_Signal25.csv` | 25 | attached but **anomalous** (letting go) |
| `raw/drift_calibration_Signal{26..30}.csv` | 26–30 | **fell off** — output is noise; input CH5 still valid |

**File-name note:** the original exports were named
`drift calibration_Signal{1..30}` (the TP4 *capture* number; contiguous this
run). They are renamed here to `drift_calibration_Signal{n}.csv` and map
directly to drops 1…30.

## Analysis

- `figures/` — plots + `drift_calibration_metrics.json` from
  [`scripts/analysis/drop_test_drift_calibration_analysis.py`](../../../scripts/analysis/drop_test_drift_calibration_analysis.py)
  (fall-off detection, burn-in changepoint scan, stabilized-phase OLS with
  reliability checks, per-axis migration).
- Findings and SOP implications:
  [`docs/drop-test-drift-calibration-analysis.md`](../../../docs/drop-test-drift-calibration-analysis.md).

Regenerate with:

```bash
pip install numpy scipy matplotlib
python scripts/analysis/drop_test_drift_calibration_analysis.py
```

## Notes from @ctrhjk

1. The 30 drops were **conducted automatically**; drop height 13 in; all other
   settings identical to the burn-in wax run.
2. The tri-axis accelerometer **fell off the key-seat housing** during the run
   (guessed at the 26th drop — confirmed by the data).
3. `prc1kn` is the dummy/failed-print specimen used for mount/DAQ validation,
   not geometry comparison.
