# 2nd 30-drop check run after the 200-drop campaign (`7xadt6`, 10 in)

Thirty further auto-drops posted by @ctrhjk in
[PR #67](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67)
immediately after the first 30-drop check run (see `../200drops-check/`), run
to answer a single question: **do the same three problems from the 200-drop
campaign still exist?**

1. **BOT electrical dropout** — CH6–8 silent for Signals 61–173 in the
   campaign, then self-recovered; alive 30/30 in check-run 1;
2. **BOT over full scale at 10 in** — CH7/CH8 (~989–991 G FS) ran over full
   scale on most check-run-1 drops;
3. **CH5 excursion / tape coupling** — CH5 sagged and T rose to ~1.088 in
   check-run 1 (vs the 1.025 campaign level);

plus the **~122 Hz ringdown-mode watch item** (back at ~550 Hz in check-run 1).

## Files

`raw/check2_Signal{233..262}.csv` — TP4 exports, Signal numbering continuing
the campaign / check-run-1 sequence (233–262 = check2 drops 1–30). All drops
on 2026-07-13 per the embedded `EventTime` stamps (~14 s cadence, ~7 min).

## Setup

Same as the 200-drop campaign and check-run 1: specimen `7xadt6` (same intact
print), drop height 10 in, bungees removed, trigger on CH5 at 1000 G,
200 ms / 125 kHz / 2 % pre-trigger.

| channel | station | full scale |
|---|---|--:|
| CH2–CH4 | top-vertex key-seat tri-axis ("TOP", output) | 14,492.8 / 14,992.5 / 13,624.0 G |
| CH5 | base-plate single-axis (taped; **trigger @ 1000 G**) | 9,442.9 G |
| CH6–CH8 | bottom-vertex low-range tri-axis ("BOT") | 1,002.0 / 991.1 / 989.1 G |

## Analysis

Script: `scripts/analysis/drop_test_200drops_check2_analysis.py` (emits
`figures/200drops_check2_metrics.json`). Findings:
`docs/drop-test-200drops-check2-analysis.md`.
