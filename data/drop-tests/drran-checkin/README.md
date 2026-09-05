# `drran1`–`drran9` check-in (09-02/09-03 sessions)

Nine 20-drop sessions posted by @ctrhjk on PR #86 (09-05) as subfolders
of the standing public Box share, requesting the r2d2-style check-in:
one fifth-drop waveform plot per specimen, transmissibility averages,
and a first-look anomaly screen. 60 in / arrangement B (1/2 in PU mat),
current SOP capture settings (4 ch, 1.25 MHz, 100 ms, 2 ms pre-trigger,
150 G trigger on CH5). Per the TP4 timestamps the sessions ran in order:
`drran1`–`drran7` on 09-02 (~14:20–19:00 local), `drran8`–`drran9` on
09-03 morning (~09:05–09:37) — the Box folder labels all say 9-3-2026.
The `drran` labels appear to be a blind/randomized numbering of the
round-2 batch (cf. the r2d2 naming and the 1–9 model numbers in
@timothy-commins's video note); **the drran → design-parameter key is
not in the repo yet** and is needed before any BO hand-off.

- Box share `kkhmvnj9ni19b57dryk3gdroqrp5uf0b`, one subfolder per
  session (ids in each `raw/drran<n>/box-ids.json` manifest). Raw
  captures (~1.7 GB, 180 CSVs) stay on Box; the manifests re-fetch them
  via `scripts/fetch_box_shared_folder.py`. Unlike prior uploads, **no
  TP4 series tables were included** in this export.
- 27 slo-mo clips (3 per specimen, ~11.5 GB, no XML sidecars) in Box
  subfolder `415062614150` — manifest at `video/box-ids.json`; not
  analyzed this pass.
- Analysis: the standing campaign pipeline
  (`scripts/analysis/drop_test_campaign_analysis.py`, tail baseline,
  2-drop warm-up discard, standing T-drift watch) on the nine-session
  root → `figures/campaign_metrics.json` + `campaign_summary.csv` +
  `01_campaign_series.png` + `11_campaign_ranking.png`; the requested
  fifth-drop figures (Signal 5 of each session) come from
  `scripts/analysis/drop_test_drran_checkin_analysis.py` →
  `02_drran1_drop5.png` … `10_drran9_drop5.png`.

## Results (stabilized drops 3–20; T = TOP/CH5, CFC-180)

| session | T180 (CV) | drift slope %/drop | in CFC-180 | Δv m/s | e_rebound | t_second |
|---|--:|--:|--:|--:|--:|--:|
| `drran1` | 1.0326 (0.16 %) | +0.024 | 226.2 G | 5.408 [healthy] | 0.063 | 69.1 ms |
| `drran2` | 1.0345 (0.06 %) | −0.002 | 224.2 G | 5.354 [healthy] | 0.041 | 44.4 ms |
| `drran3` | 1.0389 (0.11 %) | −0.016 | 224.9 G | 5.298 [healthy] | 0.014 | 15.4 ms |
| `drran4` | 1.0344 (0.16 %) | −0.018 | 217.4 G | 5.224 [settled] | 0.031 | 32.6 ms |
| `drran5` | 1.0373 (0.23 %) | −0.040 | 214.8 G | 5.205 [settled] | 0.017 | 17.8 ms |
| `drran6` | 1.0471 (0.38 %) | −0.059 | 222.2 G | 5.409 [healthy] | 0.017 | 18.3 ms |
| `drran7` | **1.2513** (0.77 %) | +0.012 (n.s.) | 223.6 G | 5.411 [healthy] | 0.027 † | 30.1 ms † |
| `drran8` | **0.9804** (0.52 %) | **+0.092 — T-DRIFT FLAG** | 223.0 G | 5.330 [healthy] | 0.039 † | 42.2 ms † |
| `drran9` | 1.0425 (0.09 %) | +0.010 | 217.8 G | 5.258 [settled] | 0.018 | 19.3 ms |

† hop-detector caveats below. ANOVA on T180: p = 8.9e-189, spread
25.7 %. All 180/180 captures triggered and parsed clean; no pauses;
~41–43 s cadence; worst channel ≤ 3.8 % of full scale everywhere except
`drran7`'s CH4 (16 % FS raw ≈ 2.2 kG on the top vertex).

## Anomaly screen

1. **T-drift watch (standing instruction): `drran8` is flagged** —
   slope +0.092 %/drop (p = 2.4e-09), a steady climb 0.969 → 0.989
   (+1.23 % end-to-end, still rising at drop 20, no plateau). Signature
   differs from the r2d2c2 reference event: both channels *fell*
   (input −4.7 %, output −3.5 % — the batch's strongest mat warm-up,
   first session of the 09-03 morning on a rested mat) and T rose
   because the cancellation was imperfect. Its mean is provisional;
   last-10 mean = 0.9838. It is the batch's only attenuator either way
   (next best 1.033). The other eight sessions are clean —
   r2d2c2-style drift did not recur.
2. **`drran7` transmits at T180 = 1.251** — the strongest amplifier on
   program record (prior worst ~1.19–1.22), with broadband T (CFC-1000)
   ≈ 2.94 and top-vertex raw peaks ~2.2 kG (16 % FS). Stable across all
   20 drops (CV 0.77 %, no drift), so it is characteristic of the
   article, not a loose-mount rattle — but worth a physical check
   (mount seat, strut/tendon integrity) and a look at its 3 slo-mo
   clips before treating it as a design result.
3. **`drran1` has the largest specimen hop ever recorded**: landing at
   +69.1 ms (verified as a real quiet-then-burst event, tight across
   drops at 68.5–69.6 ms), e_rebound 0.063 vs the prior record 0.050
   (`6lhxfy`). Note it sits just inside the detector's 70 ms search
   cap.
4. **Hop-detector caveats**: `drran8` double-bounces (repeatable
   landings at +39 ms and +70 ms), so its per-drop t_second mixes the
   two (CV 23 %) — first-landing e_rebound ≈ 0.036. `drran7` shows no
   clear ballistic landing; its only strong late burst (+78–81 ms,
   200–280 G) sits in the anti-rebound brake-catch window, so its
   t_second/e_rebound are envelope-rise readings, not a hop.
5. Δv is healthy across the batch (5.21–5.41 m/s; the 09-02 evening
   drifts down `drran1`→`drran5` as the mat warms and recovers after
   the 10-min pause before `drran6`) — the post-#92 tower recovery is
   holding; no rig action needed.
6. Bookkeeping: folder labels say 9-3-2026 but `drran1`–`drran7` ran on
   09-02 per the TP4 event times; `drran4`–`drran9` session IDs say
   "0.5 mat" (vs "0.5 in mat"); no series tables in the export.
