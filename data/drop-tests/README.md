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
| `7-22-2026 prc1kn 100drops/` | 100 (zips) | `prc1kn` second 100-drop campaign at 60 in (posted by @ctrhjk) — byte-identical zips also committed under `7-22 - 7-27 Drop Tests/` | [`drop-test-7-22-7-27-batch-analysis.md`](../../docs/drop-test-7-22-7-27-batch-analysis.md) |
| `7-22 - 7-27 Drop Tests/` | 402 (zips) | Second-batch 60 in campaigns: `prc1kn` 07-22 (4-channel re-run of the 07-21 campaign), `RW5F61` 07-23, `7xadt6` 07-27, `9GMQYQ` 07-27 (the latter three **CH5-only** exports, 20 ms @ 1.25 MHz — no transmissibility) + batch-1 consistency comparison (`figures/`) | [`drop-test-7-22-7-27-batch-analysis.md`](../../docs/drop-test-7-22-7-27-batch-analysis.md) |
| `prc1kn-health/` | — | Derived cross-dataset health check of `prc1kn` + sensor (no raw data of its own) | [`drop-test-prc1kn-health-check.md`](../../docs/drop-test-prc1kn-health-check.md) |
| `sample-size/` | — | Derived variance + sample-size + timing meta-analysis: how many drops per specimen, variance so far, and set duration at ~42 s/drop (no raw data of its own) | [`drop-test-sample-size-analysis.md`](../../docs/drop-test-sample-size-analysis.md) |
| `compaction/` | — | Derived CH5-only absorber-stack compaction analysis: wear per drop, recovery, the "unusable" point, and T-vs-compaction robustness over 704 drops (no raw data of its own) | [`drop-test-compaction-analysis.md`](../../docs/drop-test-compaction-analysis.md) |
| `pu-vs-felt/` | 10 + 2 (zips) | Polyurethane-rubber vs 4 felt + 1 cardboard paired A/B test, specimen `bpx68c`, 5 drops each, 07-30 (posted by @me-madsen via Box, PR #86) — first data on the durable-absorber replacement (issue #88), full 4-channel 1.25 MHz / 20 ms exports | [`drop-test-pu-vs-felt-analysis.md`](../../docs/drop-test-pu-vs-felt-analysis.md) |
| `print-defects/` | 502 (zips) | Print-defect study: five nominally identical T3-prism prints (`57vqhx`, `mdt6ja`, `j1crxg`, `cruela`, `bpx68c`), ~100 drops each at 60 in on 4 felt + 1 cardboard, 07-28/07-29 (posted by @me-madsen via Box, PR #86) — first direct measurement of print-to-print scatter in `T`; the stack was adjusted before specimens 4–5, which confounds the defect grouping | [`drop-test-print-defects-analysis.md`](../../docs/drop-test-print-defects-analysis.md) |
| `pu-configs/` | 40 (zips) | Polyurethane sheet-arrangement sweep, specimen `bpx68c`, 4 arrangements × 10 drops at 60 in, 07-30 (posted by @me-madsen via Box, PR #86) — picks the transmissibility operating point; the 1/2 in sheet alone at a 150 G trigger is the most repeatable under both CFC-180 and CFC-1000 and puts the most output energy in the structural band | [`drop-test-pu-configs-analysis.md`](../../docs/drop-test-pu-configs-analysis.md) |
| `7-30-2026 - 100 drops - 60 in - 4 flt 1 crdbrd/` | 151 | Direct-to-branch upload of two print-defect sessions (`57vqhx` loose CSVs, `mdt6ja` 2 zips = 50 of 100 captures) — partial duplicate of `print-defects/raw/`; folder name is the upload date, the tests were 07-28 | [`drop-test-print-defects-analysis.md`](../../docs/drop-test-print-defects-analysis.md) |
| `abc123-blind/` | 90 (Box) | **Blind ABC × 123 crossover**, 3 PU arrangements × 3 specimens × 5 drops × 2 sets, 08-04/08-05 (posted by @me-madsen via Box, PR #86) — the executed version of the pre-registered blind protocol; 100 ms / 1.25 MHz / 2 ms pre-trigger / 150 G. Raw not committed (823 MB); metrics + figures only | [`drop-test-abc123-blind-analysis.md`](../../docs/drop-test-abc123-blind-analysis.md) |
| `pre-post-grease/` | 10 (Box) | **Guide-rod cleaning/greasing A/B** ("Drop Speed Decay"), 5 drops before + 5 after rail maintenance, 60 in / arrangement B / specimen 2, 08-10 (posted by @me-madsen via Box, PR #86); same capture settings as `abc123-blind`. Raw not committed (95 MB); series table + metrics + figures only | [`drop-test-pre-post-grease-analysis.md`](../../docs/drop-test-pre-post-grease-analysis.md) |
| `speed-decay/` | 155 (Box) | **Velocity-vs-drop-count campaigns** ("Drop Speed Decay 2/3"), 55 drops (08-11, interrupted after 39) + 100 drops uninterrupted (08-12), 60 in / arrangement B / specimen 2 (posted by @me-madsen via Box, PR #86); same capture settings as `abc123-blind`. Raw not committed (~1.4 GB); series tables + Box-ID manifest + metrics + figures only | [`drop-test-speed-decay-analysis.md`](../../docs/drop-test-speed-decay-analysis.md) |
| `calibration-check/` | 131 (Box) | **Post-reset sensitivity verification**: `bpx68c` 101 drops 08-17 (pre-reset settings) vs 30 drops 08-19 (settings re-entered 08-18), 60 in / arrangement B (posted by @me-madsen via Box, PR #86); includes the committed TP4 settings screenshot (canonical record). Raw not committed (~1.2 GB); series tables + Box-ID manifest + metrics + figures only | [`drop-test-calibration-check-analysis.md`](../../docs/drop-test-calibration-check-analysis.md) |
| `sobol-campaign/` | 942 (Box) | **SOBOL + S0 BO-campaign batch, first 8/9 specimens** (posted by @me-madsen via Box, PR #86): 101 drops/specimen (+2 interrupted sessions) at 60 in / arrangement B, 08-13→08-20; T spans 0.893–1.062 with `6lhxfy` (spec 01) the first strong attenuator; introduces the tail-baseline fix for the pre-trigger contact foot. Raw not committed (~8.4 GB); series tables + Box-ID manifests + metrics + figures + BO summary CSV | [`drop-test-sobol-campaign-analysis.md`](../../docs/drop-test-sobol-campaign-analysis.md) |
| `r2d2-checkin/` | 42 (Box) | **`r2d2c1`/`r2d2c2` first-upload check-in** (posted by @me-madsen via Box, PR #86): 21 drops each, back-to-back 08-24 sessions at 60 in / arrangement B; fifth-drop plots + T averages (c1 0.994, CV 0.21 %; c2 1.041 with a +0.25 %/drop output-side drift). Raw not committed (~400 MB); series tables + Box-ID manifests + metrics + figures only | [`r2d2-checkin/README.md`](r2d2-checkin/README.md) |
| `figures/` | — | Plots for the first-drops analysis (`scripts/analysis/drop_test_analysis.py`) | — |

Total: **1,530 loose raw CSVs** + **704 unique CSVs inside the 60 in
campaign zips** (302 batch 1 + 402 batch 2; the `prc1kn` 07-22 zips are
additionally committed twice) + **12 CSVs in the `pu-vs-felt/` zips**
+ **40 CSVs in the `pu-configs/` zips** + **502 CSVs in the
`print-defects/` zips** (151 of which are additionally present as the
direct-to-branch upload under `7-30-2026 - 100 drops - 60 in - 4 flt 1
crdbrd/`) + the 5 original `.txt` exports.

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
