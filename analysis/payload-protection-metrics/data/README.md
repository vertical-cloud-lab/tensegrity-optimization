# Data provenance

## Raw waveforms (not committed; fetched from Box)

The per-drop TP4 time-domain captures (100 ms at 1.25 MHz; CH2 to CH4 =
top-vertex tri-axis, CH5 = base-plate input; 2 ms pre-trigger; 150 G
trigger on CH5) live on the lab's public Box share
(`byu.box.com/s/kkhmvnj9...`, the same share every `box-ids.json`
manifest on `copilot/add-drop-test-protocol-again` records), under
`Drop Test Data`. They are about 20 GB in total and are deliberately not
committed; [`../fetch_campaign_waveforms.py`](../fetch_campaign_waveforms.py)
re-downloads the exact selection in about 3 minutes at runner bandwidth.

[`box-session-manifest.json`](box-session-manifest.json) freezes what
this audit used: for each of the 45 sessions, the Box folder id and the
file name to file id map of the selected captures (8.6 GB, 963 usable
captures + series tables). Selection rule: all captures of the four
check-in batches (r2d2c1 to r2d2c9, drran1 to drran9, 2dran1 to 2dran9,
corny1 to corny9; 20 to 22 drops each), the first 26 signal numbers of
each 101-drop seed session (matching the check-in sample size; the
campaign's `t3_prism_drop_count_sensitivity.py` supports the subset),
skipping the interrupted partial sessions (`6lhxfy-s1` 35 drops,
`amdjwm-s1` 87 drops) and the 8-18 calibration session.

Two sessions have no committed manifest anywhere else in the repo and
are recorded here for the first time: `8-21-2026 - ajhby6` and the seven
`8-24-2026 - r2d2c{3..9}` sessions.

Known quirk: the `r2d2c8` upload nests its captures as
`..._Signal9_SignalN.csv` and its series table is named like a capture
(`..._Signal9.csv`). Parse the *last* `SignalN` token, and skip files
whose first line says `TP4 Series Table Export File`.

## Derived files (committed)

- [`per-drop-payload-metrics.csv`](per-drop-payload-metrics.csv): one row
  per capture (963), written by
  [`../compute_drop_metrics.py`](../compute_drop_metrics.py). Columns:
  the reproduced campaign pipeline metrics (t180, t1000, in/out peaks,
  delta-v, ringdown fn/zeta, t_second, e_rebound; same algorithms as
  `analyze_capture` in `drop_test_abc123_blind_analysis.py`, tail
  baseline) plus the payload-dose metrics defined in the
  [audit README](../README.md#0-definitions). Validity and warm-up
  filtering are applied downstream, not here: every parsed capture is a
  row.
- [`example-traces.npz`](example-traces.npz): 50 kHz decimated
  CFC-1000 in/out traces for the two specimens in the waveform-anatomy
  figure (corny7 and drran7, drop 10 each), so the figure re-renders
  without the raw tree.

## Sibling inputs (committed elsewhere on this branch)

- Committed campaign aggregates for the bit-exactness cross-check:
  [`../../cv-signal-audit/data/`](../../cv-signal-audit/data/README.md)
  (five drop-results tables).
- Design mapping, weighed masses, nominal coordinates, and Tier-B/C
  simulator values per article:
  [`../../sim-measured-correlations/data/sim-articles/sim_articles.csv`](../../sim-measured-correlations/data/sim-articles/sim_articles.csv).

## Cross-check result (from `metrics.json`)

Recomputed t180 / t1000 / e_rebound / delta-v specimen means match the
committed drop-results tables to max relative differences of about 1e-16
for all 36 check-in sessions. The seed batch (first ~24 of 101 drops
here vs all 101 there) agrees to 0.7 % on t180, 4 % on t1000, and 21 %
on one specimen's e_rebound (that channel drifts across the long
session, consistent with its negative reprint reliability).
