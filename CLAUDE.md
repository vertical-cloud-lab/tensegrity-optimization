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

### Other conventions (pointers, not duplicates)

- Per-capture pipeline + capture settings: `analyze_capture` in
  `scripts/analysis/drop_test_abc123_blind_analysis.py`; use the **tail
  baseline** for sessions from 08-17 on (mat contact precedes the 2 ms
  pre-trigger window).
- Δv rig-health bars, warm-up discard, and dataset index:
  `docs/drop-test-speed-decay-analysis.md`, `data/drop-tests/README.md`.
- T3 specimen IDs are case-insensitive; treat as lowercase.
