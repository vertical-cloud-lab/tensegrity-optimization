# `2dran1`–`2dran9` check-in (09-05/09-08/09-09 sessions)

Nine 20-drop sessions posted by @ctrhjk on PR #86 (09-10) as subfolders
of the standing public Box share — the second randomized batch after
`drran1`–`drran9` (09-02/03). 60 in / arrangement B (1/2 in PU mat),
current SOP capture settings (4 ch, 1.25 MHz, 100 ms, 2 ms pre-trigger,
150 G trigger on CH5). The Box folder labels all say 9-09-2026 (the
upload date); per the TP4 timestamps the sessions ran across three days:
`2dran1`–`2dran2` on 09-05 (~14:29–15:00 local), `2dran3`–`2dran5` on
09-08 (~09:25–12:08), `2dran6`–`2dran9` on 09-09 (~09:48–11:02).
**Key resolved 09-15:** both batches' label → design keys are committed
(`params.json` here and in `../drran-checkin/`, joined into the
campaign summaries/metrics), imported from the BO branch's
`bo/t3-prism-bo-round3-print-key.csv` (PR #102, committed 09-06,
photo-confirmed per plate cell). The labels were never re-randomized —
both batches are labeled by build-plate cell under the same back-left →
front-right raster, so `drranN` and `2dranN` are **the same design
(trials 28–36) on two different printed articles**. See "What the print
record settles" below.

**Unblinding status (09-12, @ctrhjk on PR #86):** (1) the `drran` and
`2dran` sets are "identical structures" — read on 09-12 as the same
nine physical articles re-tested; **corrected 09-15: it means identical
*designs*** (the print record shows two separate prints — see "What the
print record settles" below, which supersedes the same-article reading
this check-in previously carried); (2) nothing unusual was observed
while `2dran6` was dropped (anomaly item 1); (3) this batch's clips
were filmed at random drops, so no clip ↔ recorded-drop pairing is
possible here — future sessions will film drops 1, 10 and 20, which
pairs clips to captures deterministically via sidecar `CreationDate` ↔
TP4 `EventTime`. The two asks this check-in closed with — the per-label
key, and prints-vs-re-prints confirmation — are both now answered: the
key by PR #102's round-3 print key, the composition by PR #102's
`bo/README.md` print logs (09-02 / 09-05, issue #98) and @me-madsen's
09-15 statement on this PR that 2dran is a reprint.

- Box share `kkhmvnj9ni19b57dryk3gdroqrp5uf0b`, one subfolder per
  session (ids in each `raw/2dran<n>/box-ids.json` manifest). Raw
  captures (~1.7 GB, 180 CSVs) stay on Box; the manifests re-fetch them
  via `scripts/fetch_box_shared_folder.py`. Unlike the drran export,
  **TP4 series tables are included** — committed per session next to
  the manifests; the pipeline's raw CH5 peaks agree with them to
  ≤ 0.1 % (Δv to 2–4 %, different integration windows).
- 27 slo-mo clips (3 per session, ~7.9 GB) in Box subfolder
  `416623983635` — manifest at `video/box-ids.json` — **with the 27
  Sony XML sidecars** (committed under `video/xml/`, all
  `captureFps="959.04p"`). Clips-per-day match sessions-per-day exactly
  (09-05: 6, 09-08: 9, 09-09: 12 = 3 × sessions), but several sidecar
  timestamps fall between/after the DAQ windows (e.g. C0222–C0224 at
  15:19–15:27 on 09-05, after `2dran2` ended), so clips include
  video-only drops and/or the camera clock is offset; the MP4s were
  renamed `2dranN-M.MP4` by the operator while the XMLs keep camera
  names C0219–C0245, and the XML ↔ MP4 pairing can't be confirmed
  without the MP4s' embedded metadata. C0233 is only 600 frames
  (~0.63 s) — likely an aborted clip. MP4s not analyzed this pass.
  *09-12: @ctrhjk confirms the clips were recorded at random drops —
  consistent with the timestamp finding; treat this batch's clips as
  qualitative documentation only. Future SOP: film drops 1, 10 and 20
  per session (endorsed — drop 1 is the only record of the discarded
  warm-up transient, and drops 1/20 bracket the drift-watch window).*
- Analysis: the standing campaign pipeline
  (`scripts/analysis/drop_test_campaign_analysis.py`, tail baseline,
  2-drop warm-up discard, standing T-drift watch) on the nine-session
  root → `figures/campaign_metrics.json` + `campaign_summary.csv` +
  `01_campaign_series.png` + `11_campaign_ranking.png`; fifth-drop
  waveform figures (Signal 5 of each session) via
  `scripts/analysis/drop_test_drran_checkin_analysis.py --raw … --out …`
  → `02_2dran1_drop5.png` … `10_2dran9_drop5.png`; cross-batch
  comparison via `scripts/analysis/drop_test_2dran_batch_comparison.py`
  → `12_batch_comparison.png` + `batch_comparison.json` (fingerprint
  best-fit — superseded as a correspondence 09-15); keyed per-design
  comparison via
  `scripts/analysis/drop_test_round3_per_design_comparison.py` →
  `13_per_design_comparison.png` + `per_design_comparison.json`;
  `params.json` (label → design key) joined into
  `campaign_summary.csv` / `campaign_metrics.json` design_params.

## Results (stabilized drops 3–20; T = TOP/CH5, CFC-180)

| session | T180 (CV) | drift slope %/drop | e2e % | T1000 | in CFC-180 | Δv m/s | first-landing hop |
|---|--:|--:|--:|--:|--:|--:|--:|
| `2dran1` | 1.0791 (0.34 %) | +0.020 | +0.24 | **1.473** | 222.6 G | 5.284 [healthy] | 27.2 ms (drifts 26.1 → 28.0) |
| `2dran2` | 1.0900 (0.54 %) | −0.029 | −0.46 | 1.250 | 219.1 G | 5.155 [settled] | **≤ 15 ms (censored)** |
| `2dran3` | 1.0533 (0.33 %) | −0.057 | −0.76 | 1.195 | 214.5 G | 5.111 [settled] | 15.5 ms (+ 2nd landing ~61 ms) |
| `2dran4` | 1.0433 (0.25 %) | +0.023 | +0.29 | 1.108 | 223.9 G | 5.303 [healthy] | 40.1 ms |
| `2dran5` | 1.0604 (0.13 %) | −0.014 | −0.20 | 1.101 | 222.0 G | 5.316 [healthy] | 17.9 ms (floor-mixed) |
| `2dran6` | 1.0859 (**1.80 %**) | **−0.187 — T-DRIFT FLAG** | **−2.79** | 1.133 | 216.2 G | 5.137 [settled] | ~23 ms (erratic, CV 41 %) |
| `2dran7` | 1.0286 (0.16 %) | +0.012 | +0.20 | 1.060 | 215.5 G | 5.128 [settled] | 40.1 ms |
| `2dran8` | **1.0109** (0.11 %) | −0.000 | 0.00 | 1.042 | 217.2 G | 5.111 [settled] | 35.4 ms |
| `2dran9` | 1.0451 (0.23 %) | +0.025 | +0.39 | 1.055 | 218.0 G | 5.186 [settled] | 54.5 ms |

ANOVA on T180: p = 9.4e-84, spread 7.50 %. All 180/180 captures
triggered and parsed clean; no in-session pauses; ~41–43 s cadence;
worst channel ≤ 3.5 % of full scale everywhere except `2dran1`'s CH4
(6.2 % FS — the batch's broadband outlier, cf. `drran7`'s 16 %).
`e_rebound` = g·t_hop/(2·Δv) where the hop is clean: `2dran9` 0.0515,
`2dran7` 0.0383, `2dran4` 0.0371, `2dran8` 0.0340, `2dran1` 0.0252,
`2dran5` 0.0165, `2dran3` ≈ 0.015 (first landing), `2dran2` ≤ 0.0145.

## Anomaly screen

1. **T-drift watch (standing instruction): `2dran6` is flagged** —
   end-to-end −2.79 % (envelope ±2.5 %; slope −0.187 %/drop at
   p = 0.017). Not the clean r2d2c2 staircase: the series is *erratic*
   (T 1.055–1.134, step-like output-side level changes at drops ~8 and
   ~15 on top of a normal mat-warm-up input decline; hop timing equally
   unsteady). Both channels fell (input −2.9 %, output −5.6 %), so the
   pipeline attributes it common-mode/input-side, but the excess is
   output-side — an unsteady mount/wax seat is the lead suspect. Its
   mean (1.086) is drift-contaminated; late-session level ≈ 1.06. If
   `2dran6`'s number matters downstream, re-seat the mount and re-run;
   it is top-3-amplifier either way. The other eight sessions are clean
   (|e2e| ≤ 0.76 %) — r2d2c2-style drift did not recur in them.
   *Update 09-12: @ctrhjk confirms nothing unusual was observed during
   the session — the instability is latent (wax-seat), not a handling
   incident; the provisional status stands unchanged.*
2. **Neither drran extreme recurs.** No 2dran session comes near
   `drran7`'s T180 = 1.251 (batch max here: 1.090), and none attenuates
   (batch min 1.011 vs `drran8`'s 0.980). See the comparison below.
3. **Hop-detector boundary effects** (secondary-burst search window is
   15–70 ms): `2dran2` sits pinned at the 15 ms floor (real landing
   ≤ 15 ms — the smallest hop measured on this rig); `2dran3`
   double-bounces (repeatable landings at ~15.5 and ~61 ms, argmax
   flips → its t_second mean/CV are mixtures); `2dran5` mixes 15.0-floor
   readings with ~19.3 ms. `2dran4`/`2dran7`/`2dran8`/`2dran9` are
   clean (CV ≤ 3 %). `2dran1`'s hop *grows monotonically* 26.1 → 28.0 ms
   through the session — unique in the program so far.
4. **Rig health is fine**: Δv 5.11–5.32 m/s (healthy/settled band) on
   all nine; inputs 215–224 G on the campaign plateau; the 09-05
   sessions start at 5.28–5.32 and the later days sit slightly lower —
   the familiar within-evening mat warm-up, no cumulative decline.
5. Bookkeeping: folder labels say 9-09-2026 but the sessions ran
   09-05/09-08/09-09 per TP4 event times; session IDs say "0.5 mat";
   `2dran3`'s Box folder name has a missing space ("2dran3- 60in").

## Cross-batch comparison (vs `drran1`–`drran9`, `figures/12_batch_comparison.png`)

- **The labels do not carry over** — *so the fingerprints said.* Under
  the identity map the standardized fingerprint distance is ~2× the
  best-fit assignment's (19.2 vs 10.3), and identity pairs contradict
  the hop constants (e.g. `drran1` 69.1 ms vs `2dran1` 27.2 ms).
  *Corrected 09-15: the labels DO carry over (same raster, same design
  per label). What this statistic actually measured is that the hop and
  broadband features are print-dependent article properties, so
  same-design articles from two prints don't fingerprint-match — cf.
  the abc123 blind test, where print defects alone moved `t_second` at
  \|d\| ≈ 10–19.*
- **The best-fit correspondence is suggestive, not decisive** (runner-up
  margins ≲ 0.2 z for most pairs — the low-hop articles are mutually
  degenerate): `drran1↔2dran9` (each batch's big-hop article, though
  69 → 54 ms is a larger change than any article has shown before),
  `drran8↔2dran8` (each batch's lowest-T article, 0.980 → 1.011),
  `drran7↔2dran1` (each batch's broadband/CH4-hot article — but hugely
  milder now: T1000 2.94 → 1.47, T180 1.251 → 1.079, CH4 16 → 6.2 %
  FS). *Superseded 09-15: except for the accidental `drran8↔2dran8`,
  these candidate pairs crossed designs (`drran7↔2dran1` is t32↔t36) —
  the true pairing is per-label. Retained (with
  `figures/batch_comparison.json`) as a record of what DAQ fingerprints
  alone can and cannot certify.*
- **Batch level**: median T180 1.053 vs 1.037 (+1.6 %, inside the known
  session-to-session re-seat envelope), inputs within 1.3 %, Δv within
  2.4 %. Within-session precision matches (median CV ≈ 0.25 %).
- Full numbers: `figures/batch_comparison.json`.

### What the print record settles (09-15) — supersedes the 09-12 same-articles reading

The check-in's question 1 asked whether @ctrhjk's *"drran sets and
2dran sets are identical structures"* meant the same physical prints
re-tested or a re-print of the same nine designs. The print record
answers: **re-print.** PR #102's `bo/README.md` records that the
round-3 plate was printed twice by @ctrhjk — print 1 =
`drran1`–`drran9` (print log with masses, RH and photos on issue #98,
2026-09-02), print 2 = `2dran1`–`2dran9` (same log format, 2026-09-05)
— and its `bo/t3-prism-bo-round3-print-key.csv` (committed 09-06,
before either interpretation existed on this branch) keys **both**
batches' labels to trials 28–36 by build-plate cell, photo-confirmed
per cell. @me-madsen restated it on this PR on 09-15: *"2dran is a
reprint of drran and should be a better representation of the digital
model"* — and indeed the key logs print 2 defect-free while four
print-1 articles (`drran3/5/6/7` = t31/t28/t34/t32) carry "some tiny
bubbles on the diagonal tendons". The 09-12 same-articles reading was
therefore wrong; these two batches are a **same-design print-to-print
replication test** (print + session + seat noise combined), and the
per-label pairing below replaces the fingerprint best-fit.

Per-design T180, print 1 → print 2 (`figures/13_per_design_comparison.png`
+ `figures/per_design_comparison.json`, from
`scripts/analysis/drop_test_round3_per_design_comparison.py`;
pathologies = advisory seat gauge T1000/T180, T-drift-watch flags, and
the print key's defect log):

| # | design | T180 print 1 → print 2 | Δ | pathologies |
|--:|---|---|--:|---|
| 7 | t32 | 1.2513 → 1.0286 | **−17.8 %** | p1: bubbled TPU tendons + gauge 2.35 |
| 2 | t33 | 1.0345 → 1.0900 | +5.4 % | p2 gauge 1.15 (p1 1.09) |
| 1 | t36 | 1.0326 → 1.0791 | +4.5 % | p2 gauge 1.37 |
| 6 | t34 | 1.0471 → 1.0859 † | +3.7 % † | p1 bubbles; p2 drift-flagged |
| 8 | t35 | 0.9804 ‡ → 1.0109 | +3.1 % | p1 drift-flagged |
| 5 | t28 | 1.0373 → 1.0604 | +2.2 % | p1 bubbles |
| 3 | t31 | 1.0389 → 1.0533 | +1.4 % | p1 bubbles; gauges 1.11 / 1.13 |
| 4 | t29 | 1.0344 → 1.0433 | **+0.9 %** | clean |
| 9 | t30 | 1.0425 → 1.0451 | **+0.2 %** | clean |

† vs `2dran6`'s late-session level (~1.06) the change is ~+1.2 %.
‡ `drran8`'s drift-flagged mean; vs its last-10 mean (0.9838) +2.8 %.

Reading it for repeatability: median +2.2 % with 8/9 positive — a
systematic batch offset (the print-2 articles are +0.26 g ≈ +1.3 %
heavier at byte-identical print settings per PR #102's session-offset
analysis, and the sessions are different days/mount seatings) — and
**both fully clean pairs reproduce to ≤ 0.9 %**, i.e. at within-print
session repeatability. Every pair off by more than ~2 % carries an
identified measurement pathology on at least one side. Cross-print rank
order is poor overall (Spearman 0.08) for a structural reason: on
print 1 the seven mid-field designs span only 1.4 % (including the
t28/t30/t33 parameter-clone trio, spread 0.8 % there), so their
ordering was never resolvable at this noise level; at the extremes the
prints agree qualitatively — t35 (the round's only twisted design,
61.5°) is the lowest-T design on both prints, and t34 ranks #2
amplifier on both. The 09-12 "same-article" bounds survive re-badged as
design-level facts: neither print-1 extreme reproduced on the clean
print — **round 3 still has no reproduced attenuator.**

**"Better representation of the digital model" — measured, yes.**
Against the frozen round-3 predictions
(`bo/t3-prism-bo-round3-predictions.csv`): print 1 Spearman ρ = 0.20
(p = 0.61), RMS 0.081; print 2 **ρ = 0.72 (p = 0.03), RMS 0.020 — 4×
closer**. The improvement is concentrated exactly at the defect: t32
was round 3's *best-predicted* design (pred 1.0204), measured
worst-on-record on the bubbled print-1 article (1.2513), and lands
within 0.8 % of prediction on the clean print 2 (1.0286). Excluding
t32, the two prints agree with the model comparably (ρ 0.71 vs 0.64,
RMS 0.026 vs 0.021) — print 2's advantage is having no defective
article, not a globally different response.

**Cross-thread flag for PR #102 / round 5:**
`bo/t3-prism-bo-round3-drop-results.csv` there is a **drran-only**
snapshot — the BO currently holds t32 = 1.2513 and t35 = 0.9804, both
now known unrepresentative. The round-5 regeneration already pending on
the corny-key correction should also re-ingest round 3 per-design from
both key-joined campaign summaries (this folder's + `../drran-checkin/`'s),
preferring gauge-healthy, drift-clean seatings.

The two corollaries promoted to `CLAUDE.md` on 09-12 survive with their
evidence base corrected (see the updated section there):

1. **Within-session stability certifies nothing** — `drran7` held 1.251
   at CV 0.77 %, passed the drift watch, and the value was an
   article/seat artifact all the same. Decision-driving values need
   replication — across a re-seat, and (for extremes) across a
   replicate print. Positive control: `6lhxfy` 0.893 reproduced to
   0.13 % across a day + re-seat.
2. **The advisory seat gauge (T1000/T180 ≳ 1.15) gains evidence:** the
   three largest per-design shifts are exactly the three pairs whose
   one side trips it (`drran7` 2.35, `2dran1` 1.37, `2dran2` 1.15).
   The standing 09-12 prediction sharpens: `2dran1` (= t36, gauge 1.37)
   reads ~4 % high at 1.079 — its healthy-gauge print-1 sibling
   (`drran1`) read 1.033 — and should come down on re-seat.

Residual asks: a quick physical confirm from @ctrhjk that both printed
sets (18 articles) exist — and, if the print-1 articles are still on
hand, a 20-drop **re-seat of ex-`drran7`** (the bubbled t32 article)
would split defect vs seat in the −17.8 % pair: if it repeats ~1.25 the
artifact is the article (defect), if it lands ~1.03–1.09 it was the
seat.
