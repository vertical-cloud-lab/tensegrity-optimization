# 30-drop check run after the 200-drop campaign (`7xadt6`, 10 in)

Thirty additional auto-drops posted by @ctrhjk in
[PR #67](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67)
immediately after the 200-drop campaign (see `../200drops/`), run specifically
to diagnose the three problems flagged in that campaign's report:

1. **BOT electrical dropout** — CH6–8 silent for Signals 61–173, then
   self-recovered (intermittent cable/connector suspected);
2. **BOT over full scale at 10 in** — CH8 > FS on 50/87 alive captures;
3. **CH5 excursion** — CH5 sagged to a 210–230 G shelf at drops ~140–175 with
   T spiking to 1.09–1.16 (tape-coupling suspect);

plus the end-of-campaign **~122 Hz ringdown-mode watch item** (dominant on 8
of the last 9 campaign drops).

## Files

`raw/check_Signal{203..232}.csv` — TP4 exports, Signal numbering continuing
the 200-drop campaign's sequence (203–232 = check drops 1–30). All drops on
2026-07-13, 19:26–19:33 UTC per the embedded `EventTime` stamps (~14 s
cadence, ~7 min).

## Setup

Same as the 200-drop campaign: specimen `7xadt6` (fresh intact print), drop
height 10 in, bungees removed, trigger on CH5 at 1000 G, 200 ms / 125 kHz /
2 % pre-trigger.

| channel | station | full scale |
|---|---|--:|
| CH2–CH4 | top-vertex key-seat tri-axis ("TOP", output) | 14,492.8 / 14,992.5 / 13,624.0 G |
| CH5 | base-plate single-axis (taped; **trigger @ 1000 G**) | 9,442.9 G |
| CH6–CH8 | bottom-vertex low-range tri-axis ("BOT") | 1,002.0 / 991.1 / 989.1 G |

## Analysis

Script: `scripts/analysis/drop_test_200drops_check_analysis.py` (emits
`figures/200drops_check_metrics.json`). Findings:
`docs/drop-test-200drops-check-analysis.md`.
