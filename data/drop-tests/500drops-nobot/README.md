# 2nd 500-drop failure test — bottom tri-axis (CH6–8) removed, completed 500/500

Re-run of the 500-drop failure test posted by @ctrhjk in
[PR #82](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/82).
The first attempt (`../500drops/`) was halted at drop 256 by a TP4 overload
(CH6 walking over its 1,002 G full scale). For this run the **bottom-vertex
low-range tri-axis (CH6–8) was physically removed**, and the run **completed
all 500 drops**.

## Specimen

The **same specimen as the first 500-drop test** — the newest print with the
new TPU filament and three bubbled diagonal tendons (see
[PR #35](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4983604148)).
It therefore entered this run with ~256 prior drops of history and finished
with ~756 cumulative drops. No specimen ID was stated.

## Files

`raw/500_Signal{1..500}.csv` — TP4 exports (session `New 500drops`), posted
as `500_{1..17}.zip`. All drops on 2026-07-16, 18:24–20:41 (~18 s cadence,
~137 min), per the embedded `EventTime` stamps.

## Setup

Drop height 10 in, bungees removed, trigger on CH5 @ **300 G**,
200 ms / 125 kHz / 2 % pre-trigger. Only four channels this run:

| channel | station | full scale |
|---|---|--:|
| CH2–CH4 | top-vertex key-seat tri-axis ("TOP", output) | 14,492.8 / 14,992.5 / 13,624.0 G |
| CH5 | base-plate single-axis (**trigger @ 300 G**) | 9,442.9 G |
| CH6–CH8 | **removed for this run** | — |

## Analysis

Script: `scripts/analysis/drop_test_500drops_nobot_analysis.py` (emits
`figures/500drops_nobot_metrics.json`). Findings — OLS trend regressions,
the drop-354 severity event, the run-1 comparison, and the assessment of
whether the BOT station is needed:
`docs/drop-test-500drops-nobot-analysis.md`.
