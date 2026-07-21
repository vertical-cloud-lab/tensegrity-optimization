# 60 in / 5 felt validation — derived analysis outputs

Derived dataset (no raw data of its own) for the validation campaigns of the
felt-sheet sweep's recommended operating point (**60 in drop height + 5 felt
sheets**), posted by @ctrhjk on PR #86:

| specimen | raw data | captures | session |
|---|---|--:|---|
| `7xadt6` | [`../7xadt6 _60in_5felts folder/`](../7xadt6%20_60in_5felts%20folder/) — `Marcus_{1..4}.zip` | 100 | "7xadt6 60in+5felts", 2026-07-20 19:51–20:59 |
| `9GMQYQ` | [`../9GMQYQ_60in_5felts/`](../9GMQYQ_60in_5felts/) — `jin_{1..4}.zip` | 101 | "9GMQYQ 60in+5felts", 2026-07-20 21:12–22:32 |

The raw TP4 exports (200 ms / 125 kHz) stay inside the committed zips; the
analysis script reads them directly.

## Setup / channel map

Rig unchanged from the felt-sheet sweep and `500drops-nobot` runs; bottom
tri-axis removed. Per @ctrhjk's channel note on PR #86:

| channel | station | full scale |
|---|---|--:|
| CH2 | top-vertex key-seat tri-axis, **X** ("TOP" output) | 14,492.8 G |
| CH3 | top-vertex key-seat tri-axis, **Y** | 14,992.5 G |
| CH4 | top-vertex key-seat tri-axis, **Z** | 13,624.0 G |
| CH5 | base-plate single-axis (input, **trigger @ 300 G**) | 9,442.9 G |

## Analysis

Script: `scripts/analysis/drop_test_60in_5felts_analysis.py` (emits
`figures/60in_5felts_metrics.json`). Writeup:
[`docs/drop-test-60in-5felts-analysis.md`](../../../docs/drop-test-60in-5felts-analysis.md)
— capture health (201/201 clean), the burn-in scan + stabilized-phase OLS
drift regressions, the felt-wear saturation story (CH5 raw spike 2.1 →
6.5 kG over the evening), specimen discrimination, and the keep-60-in/5-felt
+ manage-felt-as-consumable recommendation.

| figure | content |
|---|---|
| `figures/01_full_series.png` | per-capture raw CH5 / TOP peaks + FS/3 line, both specimens |
| `figures/02_stabilized_ols.png` | stabilized-phase OLS fits: TOP and T = TOP/CH5 per specimen |
| `figures/03_saturation.png` | CH5 / CH4 raw peak as % of full scale across the evening |
| `figures/04_specimen_comparison.png` | stabilized TOP and T boxplots, Welch p, Cohen's d |

## Slow-mo video

[`video/`](video/) — links to @ctrhjk's slow-motion videos of both campaigns
(YouTube shorts, 2026-07-20), the eight publicly-served real preview frames
(full downloads are bot-gated from CI), frame-level observations
(rig/mount/tie-down verification, specimen intact throughout, felt
impact-zone mottling), and what to post to enable full frame-by-frame
kinematics.
