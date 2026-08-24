# `r2d2c1` / `r2d2c2` first-upload check-in (08-24)

First two sessions of the `r2d2` pair, posted by @me-madsen on PR #86
(08-24) as an in-progress check ("the data so far"): fifth-drop plots,
transmissibility averages, and an anomaly screen. 21 drops per specimen,
back-to-back sessions on 08-24 (12:55–13:10 and 13:43–13:58 local),
60 in / arrangement B (1/2 in PU mat), current SOP capture settings
(4 ch, 1.25 MHz, 100 ms, 2 ms pre-trigger, 150 G trigger on CH5).

- Box shares: `r2d2c1` = `ual6v97k8wjgalsy3hqwhcrbr9fwz0xn`
  (folder `8-24-2026 -r2d2c1 - 60in - 0.5in mat - 23 drops`),
  `r2d2c2` = `c2455s0cybpzs3m6z2ptjq43n5ur4pno`
  (`8-24-2026 -r2d2c2 - 60in - 0.5in mat - 21 drops`).
  Raw captures (~400 MB) stay on Box; each `raw/<id>/box-ids.json`
  manifest re-fetches them via `scripts/fetch_box_shared_folder.py`.
  The TP4 series tables are committed alongside.
- Analysis: the standing campaign pipeline
  (`scripts/analysis/drop_test_campaign_analysis.py`, tail baseline,
  2-drop warm-up discard) on a two-specimen root →
  `figures/campaign_metrics.json` + `campaign_summary.csv` +
  `01_campaign_series.png`; the requested single-drop figures
  (Signal 5 of each session) come from
  `scripts/analysis/drop_test_r2d2_checkin_analysis.py` →
  `02_r2d2c1_drop5.png` / `03_r2d2c2_drop5.png`.

## Results (stabilized drops 3–21)

| | `r2d2c1` | `r2d2c2` |
|---|--:|--:|
| T = TOP/CH5, CFC-180 | **0.9942** (CV 0.21 %, drift p = 1.0) | **1.0411** (CV 1.48 %, **+0.25 %/drop**, p = 6e-11) |
| T, CFC-1000 | 1.002 (CV 0.57 %) | 1.114 (CV 5.6 %) |
| input CFC-180 (G) | 229.3 | 228.8 |
| Δv (m/s) | 5.31 [healthy] | 5.32 [healthy] |
| e_rebound | 0.0206 | 0.0210 |

All 42/42 captures triggered and parsed clean; no channel above 4.2 % of
full scale; ~43 s cadence, no pauses.

## Anomalies flagged at check-in

1. **`r2d2c2`'s T climbs monotonically 1.017 → 1.060 (+4 %) over 21
   drops** — output rises while the input falls, unlike `r2d2c1` where
   both channels drift down in lockstep (mat warming) and T stays flat.
   Output-side coupling change (mount seating / specimen settling) is the
   lead suspect; its mean above is drift-contaminated.
2. `r2d2c2`'s **raw** input carries strong drop-to-drop contact hash
   (raw-peak CV 9.7 % vs 2.2 % on c1; visible in the drop-5 zoom);
   CFC-180 input is unaffected (CV 1.1 %).
3. Label bookkeeping: the `r2d2c1` TP4 session ID says "101 drops", the
   Box folder "23 drops", the export holds 21 events.
4. `r2d2c2` drop 1 shows a first-drop transient (CH4 547 G / 0.65 ms in
   the series table, short hop) — covered by the warm-up discard.
