# `speed-decay/` — velocity-vs-drop-count campaigns (2026-08-11 / 08-12)

Posted by @me-madsen on
[PR #86](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86)
as two Box folders — the 100-drop follow-up to the guide-rod
cleaning/greasing A/B ([`pre-post-grease/`](../pre-post-grease)), asking
whether the detected end velocity trends with drop count. Same operating
point throughout: **60 in**, **arrangement B** (1/2 in PU sheet alone),
**specimen 2** (small T3 prism, printing defects) — the `B2` reference cell.

| session | TP4 session ID | date | drops | Box folder |
|---|---|---|--:|---|
| session 2 | `Drop Speed Decay 2` | 08-11 | 55 (interrupted by a **9.7 min pause after drop 39**) | [`i2hpksf19h9w84bk26ed2n91tf7i4cnm`](https://byu.box.com/s/i2hpksf19h9w84bk26ed2n91tf7i4cnm) |
| session 3 | `Drop Speed Decay 3` | 08-12 | 100 (uninterrupted, ~41 s cadence) | [`cy7ijzs8cx4gkhic133z1zoaecwsl350`](https://byu.box.com/s/cy7ijzs8cx4gkhic133z1zoaecwsl350) |

## Capture settings

Identical to `abc123-blind` / `pre-post-grease`: CH2–CH4 = top-vertex
key-seat tri-axis output, CH5 = single-axis base-plate input + trigger
(150 G), 1.25 MHz, 125,000 samples = 100 ms record, 2.000 ms pre-trigger.
All 155 captures triggered cleanly; worst channel usage 4.3 % of full
scale.

## Files

Raw captures are **not committed** (~1.4 GB); fetch them from Box into
`raw/session2/` (`data_Signal1..55.csv`) and `raw/session3/`
(`dropdata_Signal1..100.csv`). Per-file Box IDs for both folders are in
[`raw/box-ids.json`](raw/box-ids.json); download via
`https://byu.box.com/index.php?rm=box_download_shared_file&shared_name=<shared_name>&file_id=<typedID>`.

Committed: the two TP4 series tables
(`raw/session2-series.csv` = the uploaded `data.csv`,
`raw/session3-series.csv` = `dropdata.csv`), `figures/` (plots +
`speed_decay_metrics.json` with every per-drop metric).

## Analysis

Script: [`scripts/analysis/drop_test_speed_decay_analysis.py`](../../../scripts/analysis/drop_test_speed_decay_analysis.py)
(reuses the abc123 per-capture pipeline unchanged).
Writeup: [`docs/drop-test-speed-decay-analysis.md`](../../../docs/drop-test-speed-decay-analysis.md).

Headline: **no velocity decay with drop count in steady state** — the
100-drop session is statistically flat in Δv (slope p = 0.75, CV 0.54 %,
the tightest Δv session on record at 60 in). Session 2 declined −2.8 %,
but entirely within its first 39 drops (the day after greasing), read as
the fresh grease film settling plus mat bedding-in; flat after its pause.
The greasing gain held across both days (steady 4.55–4.66 m/s vs 4.44
pre-grease), still ~87 % of the healthy-tower reference (5.28–5.35 m/s).
