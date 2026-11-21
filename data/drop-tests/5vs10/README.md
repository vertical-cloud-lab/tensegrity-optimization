# 5 in vs 10 in height comparison (CH5 trigger lowered to 500 G)

Sixty auto-drops posted by @ctrhjk in
[PR #82](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/82)
to validate the 5-in drop after the earlier 5-in practice drops failed to
trigger at the 1000 G level: the CH5 trigger level was **lowered to 500 G**,
then 30 drops were run at **5 in** and 30 at **10 in**, back-to-back on the
same rig, to (a) confirm 5 in now triggers reliably and (b) decide which drop
height the BO campaign should standardize on.

## Files

`raw/5vs10_Signal{1..30}.csv` — 5-in drops 1–30.
`raw/5vs10_Signal{31..60}.csv` — 10-in drops 1–30.

TP4 exports (session "5in test"), 200 ms / 125 kHz / 2 % pre-trigger, all
recorded 2026-07-14 20:44–20:57 UTC per the embedded `EventTime` stamps
(~11–14 s cadence, ~6–7 min per height).

## Setup

Same rig and channel map as the 200-drop campaign and its check runs, with
two differences: **trigger level 500 G** (was 1000 G) and the two heights.
Specimen ID not stated in the posting comment (the 10-in levels sit ~5 %
above the `7xadt6` check-run values — treat specimen identity as
unconfirmed).

| channel | station | full scale |
|---|---|--:|
| CH2–CH4 | top-vertex key-seat tri-axis ("TOP", output) | 14,492.8 / 14,992.5 / 13,624.0 G |
| CH5 | base-plate single-axis (taped; **trigger @ 500 G**) | 9,442.9 G |
| CH6–CH8 | bottom-vertex low-range tri-axis ("BOT") | 1,002.0 / 991.1 / 989.1 G |

## Analysis

Script: `scripts/analysis/drop_test_5vs10_analysis.py` (emits
`figures/5vs10_metrics.json`). Findings + BO drop-height recommendation:
`docs/drop-test-5vs10-analysis.md`.
