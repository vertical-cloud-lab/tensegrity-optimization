# Drop-test data

Raw instrumentation data and analysis outputs for the crush/drop tests on
Jeff Hill's tower (issue #36, thread in PR #67). Each dataset lives in its
own folder with `raw/` (TP4 Time-Domain exports, 125 kHz, 0.2 s window),
`figures/`, and a `README.md` documenting the setup and channel map; the
matching analysis writeup is in [`docs/`](../../docs/) and the reproducible
script in [`scripts/analysis/`](../../scripts/analysis/).

## Dataset index (chronological)

| Dataset | Raw files | What it is | Analysis |
|---|---|---|---|
| `raw/` | 5 (.txt) | First instrumented drops (`Signal 10–14`: PETG, audrey ×3, control), posted by @me-madsen on issue #36 (May 22) | [`drop-test-analysis.md`](../../docs/drop-test-analysis.md) |
| `vertex-acrylic/` | 8 | Vertex- vs acrylic-plate mounting, 4 specimens × 2 configs, 13 ft | [`drop-test-vertex-acrylic-analysis.md`](../../docs/drop-test-vertex-acrylic-analysis.md) |
| `clip-height/` | 1 | Clip-height sweep (0/8 triggered, video only) + base-plate accelerometer check | [`drop-test-clip-height-analysis.md`](../../docs/drop-test-clip-height-analysis.md) |
| `input-output/` | 20 | Input–output (transmissibility) design: 4 geometries × 5 drops, bungees removed, 13 in | [`drop-test-input-output-analysis.md`](../../docs/drop-test-input-output-analysis.md) |
| `key-mounted/` | 5 | Key-seat mount validation, `prc1kn`, 5 drops | [`drop-test-key-mounted-analysis.md`](../../docs/drop-test-key-mounted-analysis.md) |
| `key-mounted-wax/` | 5 | Key-seat + wax-retainer retest, `prc1kn`, 5 drops (original exports `Key mounted2_Signal{7..11}`) | [`drop-test-key-mounted-wax-analysis.md`](../../docs/drop-test-key-mounted-wax-analysis.md) |
| `burn-in-wax/` | 8 | Burn-in wax drift check, `prc1kn`, 3 burn-in + 5 recorded drops | [`drop-test-burn-in-wax-analysis.md`](../../docs/drop-test-burn-in-wax-analysis.md) |
| `drift-calibration/` | 30 | Drift calibration, 30 auto-drops, `prc1kn`, 13 in | [`drop-test-drift-calibration-analysis.md`](../../docs/drop-test-drift-calibration-analysis.md) |
| `drift-calibration2/` | 50 | Drift calibration #2, 50 auto-drops, cable secured | [`drop-test-drift-calibration2-analysis.md`](../../docs/drop-test-drift-calibration2-analysis.md) |
| `30drops-real/` | 32 | 30 auto-drops with a real specimen | [`drop-test-30drops-real-analysis.md`](../../docs/drop-test-30drops-real-analysis.md) |
| `100drops/` | 100 | 100-drop campaign (posted as `drop{1..4}.zip`) | [`drop-test-100drops-analysis.md`](../../docs/drop-test-100drops-analysis.md) |
| `ch4-trigger/` | 50 | CH4-trigger configuration check, 50 drops | [`drop-test-ch4-trigger-analysis.md`](../../docs/drop-test-ch4-trigger-analysis.md) |
| `5in-100drops/` | 100 | 100 drops at 5 in (posted as `drop{1..4}.zip`) | [`drop-test-5in-100drops-analysis.md`](../../docs/drop-test-5in-100drops-analysis.md) |
| `200drops/` | 200 | 200-drop campaign, `7xadt6`, 10 in, CH5 trigger (posted as `200drops_{1..8}.zip`) | [`drop-test-200drops-analysis.md`](../../docs/drop-test-200drops-analysis.md) |
| `200drops-check/` | 30 | 1st 30-drop check run (`check_Signal203–232`) after the 200-drop problems | [`drop-test-200drops-check-analysis.md`](../../docs/drop-test-200drops-check-analysis.md) |
| `200drops-check2/` | 30 | 2nd 30-drop check run (`check2_Signal233–262`) | [`drop-test-200drops-check2-analysis.md`](../../docs/drop-test-200drops-check2-analysis.md) |
| `5vs10/` | 60 | 5 in vs 10 in height comparison, 30 drops each, CH5 trigger lowered to 500 G (PR #82) | [`drop-test-5vs10-analysis.md`](../../docs/drop-test-5vs10-analysis.md) |
| `500drops/` | 256 | 500-drop failure test (bubbled-TPU print, 10 in, CH5 trigger @ 300 G), stopped by a TP4 overload at drop 256 — CH6 over full scale (PR #82, posted as `500drops_{1..9}.zip`) | [`drop-test-500drops-analysis.md`](../../docs/drop-test-500drops-analysis.md) |
| `500drops-nobot/` | 500 | 2nd 500-drop failure test, same specimen, bottom tri-axis (CH6–8) removed — completed 500/500 (PR #82, posted as `500_{1..17}.zip`) | [`drop-test-500drops-nobot-analysis.md`](../../docs/drop-test-500drops-nobot-analysis.md) |
| `felt-sheet/` | 45 | Felt-sheet cushioning / saturation sweep: 9 (height, felt) conditions × 5 drops, CH5 trigger @ 300 G (PR #82) | [`drop-test-felt-sheet-analysis.md`](../../docs/drop-test-felt-sheet-analysis.md) |
| `7xadt6 _60in_5felts folder/` | 100 (zips) | 60 in / 5 felt validation campaign, specimen `7xadt6` (`Marcus_{1..4}.zip`, PR #86) | [`drop-test-60in-5felts-analysis.md`](../../docs/drop-test-60in-5felts-analysis.md) |
| `9GMQYQ_60in_5felts/` | 101 (zips) | 60 in / 5 felt validation campaign, specimen `9GMQYQ` (`jin_{1..4}.zip`, PR #86) | [`drop-test-60in-5felts-analysis.md`](../../docs/drop-test-60in-5felts-analysis.md) |
| `60in-5felts-validation/` | — | Derived analysis of the two 60 in / 5 felt campaigns: stabilized OLS drift, felt-wear saturation, specimen discrimination (no raw data of its own) + 960 fps slo-mo videos and frame-by-frame kinematics (`video/`) | [`drop-test-60in-5felts-analysis.md`](../../docs/drop-test-60in-5felts-analysis.md) |
| `prc1kn-60in-5felt/` | 101 (zips) | `prc1kn` 60 in campaign (`prc1kn - set 1 - {1..4}.zip`, PR #86) — stack **4 felt + 1 cardboard**, per @me-madsen the actual composition of every "5 felt"-labeled session — + mock three-structure transmissibility comparison + 959.04 fps slo-mo videos with XML sidecars and calibration-grid parallax analysis (`video/`) | [`drop-test-prc1kn-60in-5felts-analysis.md`](../../docs/drop-test-prc1kn-60in-5felts-analysis.md), [`drop-test-prc1kn-video-analysis.md`](../../docs/drop-test-prc1kn-video-analysis.md) |
| `prc1kn-health/` | — | Derived cross-dataset health check of `prc1kn` + sensor (no raw data of its own) | [`drop-test-prc1kn-health-check.md`](../../docs/drop-test-prc1kn-health-check.md) |
| `sample-size/` | — | Derived variance + sample-size + timing meta-analysis: how many drops per specimen, variance so far, and set duration at ~42 s/drop (no raw data of its own) | [`drop-test-sample-size-analysis.md`](../../docs/drop-test-sample-size-analysis.md) |
| `figures/` | — | Plots for the first-drops analysis (`scripts/analysis/drop_test_analysis.py`) | — |

Total: **1,530 loose raw CSVs** + **302 CSVs inside the 60 in campaign
zips** + the 5 original `.txt` exports.

## Provenance / completeness

Every CSV/ZIP attachment posted across all PR #67 comments (fetched via the
GitHub API with pagination, so hidden/collapsed comments are included) has
been downloaded and byte-compared (SHA-256) against the committed files:
269 unique loose-CSV links and 16 ZIPs (containing 400 CSVs) — all
byte-identical, with no attachment missing from the repo and no committed
file unaccounted for. The `5vs10/` (60 CSV attachments), `500drops/`
(9 ZIPs containing 256 CSVs) and `500drops-nobot/` (17 ZIPs containing 500
CSVs) datasets were posted on PR #82, all committed. Photos/videos posted as `user-attachments/assets`
links are intentionally not committed (see
[`drop-test-video-analysis.md`](../../docs/drop-test-video-analysis.md) for
the video-derived kinematics).

## Regenerating figures

```bash
pip install numpy scipy matplotlib
python scripts/analysis/<script>.py   # one script per dataset, see table above
```
