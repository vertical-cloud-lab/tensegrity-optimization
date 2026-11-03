# Felt-sheet cushioning / accelerometer-saturation sweep (CH5 trigger @ 300 G)

Forty-five auto-drops posted by @ctrhjk in
[PR #82](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/82#issuecomment-5007713855)
to map where the accelerometers **saturate** and to find a drop height /
cushioning combination that keeps the whole rig inside its measurement range.
Felt sheets are stacked **beneath the drop block** to soften the impact; the
drop height is stepped up while the felt count is stepped with it so the base
hit stays bounded. This directly answers @sgbaird's concern that a specimen
which is *already near saturation* leaves no head-room for the stiffer designs
the BO search space will visit.

Same downscaled specimen as the 500-drop runs
([#82 comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/82#issuecomment-4996703024),
the print from
[#35](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4983604148)),
CH5 trigger @ **300 G**, `CH6–CH8` removed (bottom tri-axis not used, matching
the `500drops-nobot` run).

## Files

`raw/height_level_Signal{1..45}.csv` — TP4 exports (session "height level"),
200 ms / 125 kHz, recorded 2026-07-17 per the embedded `EventTime` stamps.
Five drops per `(height, felt)` condition, chronological:

| Signals | Height (in) | Felt sheets |
|---|--:|--:|
| 1–5   | 20 | 1 |
| 6–10  | 20 | 2 |
| 11–15 | 30 | 2 |
| 16–20 | 30 | 3 |
| 21–25 | 40 | 3 |
| 26–30 | 40 | 4 |
| 31–35 | 50 | 4 |
| 36–40 | 50 | 5 |
| 41–45 | 60 | 5 |

(The posting comment lists `Signal11–15` slightly out of order in the table,
but the `EventTime` stamps confirm they are the chronological 30 in / 2 felt
block.)

## Setup

Same rig and top-vertex key-seat as the 500-drop and `5vs10` runs, with the
bottom tri-axis removed and felt sheets added under the drop block. Only
CH2–CH5 are recorded.

| channel | station | full scale |
|---|---|--:|
| CH2–CH4 | top-vertex key-seat tri-axis ("TOP", output) | 14,492.8 / 14,992.5 / 13,624.0 G |
| CH5 | base-plate single-axis (taped; **trigger @ 300 G**) | 9,442.9 G |

CH5 (9,442.9 G) is the **lowest-ceiling channel** and therefore the saturation
bottleneck of the rig.

## Analysis

Script: `scripts/analysis/drop_test_felt_sheet_analysis.py` (emits
`figures/felt_sheet_metrics.json` and three figures). It locates each impact on
the triggered CH5 channel, audits raw |peak| vs full scale (with a flat-top
clip-run count), fits an OLS model of peak vs height + felt count, and picks a
head-room-limited operating point. Findings + BO height/cushioning
recommendation: `docs/drop-test-felt-sheet-analysis.md`.
