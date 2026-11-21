# 500-drop failure test, stopped by a TP4 overload at drop 256

Failure test posted by @ctrhjk in
[PR #82](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/82):
drop count set to **500**, but at the **256th drop** the Lansmont Test
Partner 4 showed an **overload condition and all signals were disconnected**,
so the run stopped with 256 recorded captures.

## Specimen

The newest print with the **new TPU filament**, in which **three diagonal
TPU tendons have serious bubbles** (humidity over 10 % during printing) —
see the photos in
[PR #35](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4983604148).
No specimen ID was stated.

## Files

`raw/500drops_Signal{1..256}.csv` — TP4 exports (session `500drops`), posted
as `500drops_{1..9}.zip`. All drops on 2026-07-15, 16:03–17:02 (~13 s
cadence, ~59 min), per the embedded `EventTime` stamps.

## Setup

Drop height 10 in, bungees removed, **trigger on CH5 lowered to 300 G** (per
the recommendation in PR #82), 200 ms / 125 kHz / 2 % pre-trigger.

| channel | station | full scale |
|---|---|--:|
| CH2–CH4 | top-vertex key-seat tri-axis ("TOP", output) | 14,492.8 / 14,992.5 / 13,624.0 G |
| CH5 | base-plate single-axis (**trigger @ 300 G**) | 9,442.9 G |
| CH6–CH8 | bottom-vertex low-range tri-axis ("BOT") | 1,002.0 / 991.1 / 989.1 G |

## Analysis

Script: `scripts/analysis/drop_test_500drops_analysis.py` (emits
`figures/500drops_metrics.json`). Findings — including the overload
diagnosis (CH6 walking over its 1,002 G full scale from ~drop 100 onward):
`docs/drop-test-500drops-analysis.md`.
