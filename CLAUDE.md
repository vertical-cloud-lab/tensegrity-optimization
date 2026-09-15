# Repo instructions for Claude

## Drop-test analysis: standing conventions

### T-drift watch (standing instruction, PR #86 · 2026-08-24)

In **every** drop-test analysis — in this PR or any other — screen each
session's within-session transmissibility series (T = TOP/CH5, CFC-180,
stabilized drops) for drift, report the numbers, and **notify prominently**
if a session breaks the historical envelope. Requested by @me-madsen after
the `r2d2c2` event; the round-2 batch is analyzed in a separate PR, so this
must not be forgotten between threads.

- Historical 1/2 in PU mat envelope (17 sessions, ~1,300 stabilized drops,
  08-10 → 08-24): |OLS slope| ≤ 0.051 %/drop, |first-5 vs last-5| ≤ 2.2 %.
  Per-session table: `data/drop-tests/r2d2-checkin/figures/t_drift_history.json`;
  figure: `.../figures/04_t_drift_history.png`.
- Flag thresholds: |slope| > 0.06 %/drop (slope_p < 0.01) or |end-to-end| > 2.5 %.
- Reference event: `r2d2c2` (08-24) stepped +3.5 % (1.023 → ~1.059 plateau,
  from ~drop 7, plateaued ~drop 14). Output-side — top-vertex peak rose while
  the CH5 input fell — lead suspect wax/mount coupling re-seat. `r2d2c1`,
  minutes earlier on the same mat, was dead flat.
- When flagged: the session's T mean is drift-contaminated. Do not hand it to
  the BO — use a plateau-only average or ask for a mount re-seat + re-run.
  Attribute the drift (output-side = mount; common-mode = rig/mat, cancels in T).
- The campaign pipeline (`scripts/analysis/drop_test_campaign_analysis.py`,
  `t_drift_watch()`) automates this: `t_drift_watch` block in
  `campaign_metrics.json`, `t_drift_flag`/slope/e2e columns in
  `campaign_summary.csv`, console warnings. Reuse it (or its convention) in
  any new analysis script, and state the watch outcome — flagged or clean —
  in every findings writeup.

### Replication across seats and prints (standing instruction, PR #86 · 2026-09-12, corrected 09-15)

The drift watch only catches *within-session* instability — a stably
wrong measurement passes it: `drran7` held T180 = 1.251 at CV 0.77 %
for 20 drops with no drift, and the value was an artifact anyway.
**09-15 correction to this rule's evidence base:** drran → 2dran was a
*re-print*, not a re-seat — @ctrhjk printed the round-3 plate (trials
28–36) twice (print logs 09-02/09-05 on issue #98; PR #102
`bo/README.md`), and the labels carry the build-plate cell in both
prints (keys: `data/drop-tests/{drran,2dran}-checkin/params.json`), so
`drranN` ↔ `2dranN` is the same-design pairing. The measured per-design
shifts are same-design **print+seat** noise: median +2.2 % (batch
offset ~+1.5 %; print-2 articles +1.3 % heavier), both fully clean
pairs ≤ 0.9 %, tails +3–5 %, and −17.8 % on the pair whose print-1
article had logged TPU-tendon bubbles and seat gauge 2.35
(t32 = `drran7`→`2dran7`: 1.2513 → 1.0286; the model had predicted
1.0204). `drran8`'s 0.9804 (drift-flagged) also did not reproduce
(t35 → 1.0109): round 3 has no reproduced attenuator. Details:
`data/drop-tests/2dran-checkin/README.md` ("What the print record
settles").

- Any single-print, single-seating T that would drive a decision (batch
  extreme, claimed attenuator, BO hand-off) needs confirmation on an
  independent mount re-seat — and, for extremes, ideally a replicate
  print — before it is treated as a design property. Positive control:
  `6lhxfy` 0.893 reproduced to 0.13 % across a day + re-seat — real
  attenuation does reproduce.
- Advisory seat gauge: broadband ratio T1000/T180 ≳ 1.15 (healthy
  ≈ 1.00–1.07 on the 1/2 in mat). The three largest round-3 per-design
  shifts are exactly the three pairs with a gauge-tripping side
  (`drran7` 2.35, `2dran1` 1.37, `2dran2` 1.15). Standing prediction
  (09-12, sharpened 09-15): `2dran1` (= t36, gauge 1.37) reads ~4 %
  high at 1.079 — its healthy-gauge print-1 sibling read 1.033 — and
  should come down on re-seat.
- BO ingestion: PR #102's `bo/t3-prism-bo-round3-drop-results.csv` is a
  drran-only snapshot (holds t32 = 1.251 and t35 = 0.980, both
  unrepresentative). Round-5 regeneration must re-ingest round 3
  per-design from both key-joined campaign summaries.

### Other conventions (pointers, not duplicates)

- Per-capture pipeline + capture settings: `analyze_capture` in
  `scripts/analysis/drop_test_abc123_blind_analysis.py`; use the **tail
  baseline** for sessions from 08-17 on (mat contact precedes the 2 ms
  pre-trigger window).
- Δv rig-health bars, warm-up discard, and dataset index:
  `docs/drop-test-speed-decay-analysis.md`, `data/drop-tests/README.md`.
- T3 specimen IDs are case-insensitive; treat as lowercase.
