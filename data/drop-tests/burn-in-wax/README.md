# Burn-in wax key-seat input-output drop tests (specimen `prc1kn`)

Raw TP4 accelerometer exports for the **burn-in wax** run by @ctrhjk, posted on
[PR #67](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67).

Direct follow-up to the [key-seat + wax-retainer run](../key-mounted-wax/README.md),
which showed a small-but-significant output creep (+0.90 G/drop, p = 0.005) read
as the **wax seating** over the first few impacts. This run tests the proposed
fix: pre-seat the wax with a few unrecorded **burn-in** drops, then record.
@ctrhjk removed the old wax residue, applied **fresh wax** inside the key-seat
housing, and dropped the specimen **8 times**:

- **drops 1–3** (`Signal1..3`) — **burn-in** phase (no videos), meant to seat the
  fresh wax;
- **drops 4–8** (`Signal4..8`) — **recorded** phase (with videos), the drops that
  would count in a real campaign.

Same input-output pair as the whole series — single-axis **input** wax-mounted on
the base plate (CH5, triggered), tri-axis **output** in the top-vertex key-seat
(CH2/CH3/CH4, wax-retained), bungees removed. The specimen `prc1kn` is the same
**deliberately-failed print** (bubbles in its TPU cable); it is used only to
exercise the mount + DAQ + burn-in protocol, **not** to compare geometry.

## Recording setup

One specimen, **eight drops** (`Signal{1..8}` = drops 1…8), drop height **13 in**.
Channels and DAQ are identical to the key-seat / wax series.

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

| File | Drop # | Phase | Video |
|---|---|---|---|
| `raw/burn_in_wax_Signal1.csv` | 1 | burn-in | — |
| `raw/burn_in_wax_Signal2.csv` | 2 | burn-in | — |
| `raw/burn_in_wax_Signal3.csv` | 3 | burn-in | — |
| `raw/burn_in_wax_Signal4.csv` | 4 | recorded | yes |
| `raw/burn_in_wax_Signal5.csv` | 5 | recorded | yes |
| `raw/burn_in_wax_Signal6.csv` | 6 | recorded | yes |
| `raw/burn_in_wax_Signal7.csv` | 7 | recorded | yes |
| `raw/burn_in_wax_Signal8.csv` | 8 | recorded | yes |

**File-name note:** the original exports were named `Burn_in_wax_Signal{1..8}`
(the `Signal{n}` index is the TP4 *capture* number; contiguous this run). They are
renamed here to `burn_in_wax_Signal{n}.csv` and map directly to drops 1…8.

The videos are Sony RX100 IV captures at **960 fps** (GitHub serves a 30 fps
playback container → 32× slow-motion). They are not committed (~250 MB); the video
script re-downloads and caches them from the comment's asset URLs.

## Analysis

- `figures/` — accelerometer plots from
  [`scripts/analysis/drop_test_burn_in_wax_analysis.py`](../../../scripts/analysis/drop_test_burn_in_wax_analysis.py)
  (also loads the no-burn-in wax run for a side-by-side comparison).
- `video-figures/` — descent/rebound kinematics from
  [`scripts/analysis/drop_test_burn_in_wax_video_analysis.py`](../../../scripts/analysis/drop_test_burn_in_wax_video_analysis.py).
- Findings and SOP implications:
  [`docs/drop-test-burn-in-wax-analysis.md`](../../../docs/drop-test-burn-in-wax-analysis.md).

Regenerate with:

```bash
pip install numpy scipy matplotlib opencv-python-headless
python scripts/analysis/drop_test_burn_in_wax_analysis.py
python scripts/analysis/drop_test_burn_in_wax_video_analysis.py
```

## Notes from @ctrhjk

1. Old wax residue was removed from the key-seat housing and **fresh wax** applied
   before this run (so the wax-seating clock is reset).
2. First **three** drops are burn-in (discarded in a real campaign); the following
   five are the recorded drops with videos.
3. All other settings identical to the previous wax-retainer run; the specimen is
   the failed print `prc1kn` (TPU bubbles), used to validate the mount/DAQ —
   not a geometry comparison.
