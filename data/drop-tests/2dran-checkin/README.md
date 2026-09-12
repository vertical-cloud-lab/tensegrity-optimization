# `2dran1`–`2dran9` check-in (09-05/09-08/09-09 sessions)

Nine 20-drop sessions posted by @ctrhjk on PR #86 (09-10) as subfolders
of the standing public Box share — the second randomized batch after
`drran1`–`drran9` (09-02/03). 60 in / arrangement B (1/2 in PU mat),
current SOP capture settings (4 ch, 1.25 MHz, 100 ms, 2 ms pre-trigger,
150 G trigger on CH5). The Box folder labels all say 9-09-2026 (the
upload date); per the TP4 timestamps the sessions ran across three days:
`2dran1`–`2dran2` on 09-05 (~14:29–15:00 local), `2dran3`–`2dran5` on
09-08 (~09:25–12:08), `2dran6`–`2dran9` on 09-09 (~09:48–11:02).
**Neither the 2dran → design key nor the 2dran ↔ drran article
correspondence is in the repo**; the labels are evidently re-randomized
between batches (see the comparison below), so the key is needed before
any BO hand-off.

**Unblinding status (09-12, @ctrhjk on PR #86):** (1) the `drran` and
`2dran` sets are **the same nine structures** — the conditional
readings in the comparison below are thereby upgraded to measured
same-article facts (see "What the same-articles confirmation settles");
(2) nothing unusual was observed while `2dran6` was dropped (anomaly
item 1); (3) this batch's clips were filmed at random drops, so no
clip ↔ recorded-drop pairing is possible here — future sessions will
film drops 1, 10 and 20, which pairs clips to captures
deterministically via sidecar `CreationDate` ↔ TP4 `EventTime`. Still
pending: the per-label key (drranN / 2dranN → article/design ID), the
BO blocker; and an explicit confirmation that "identical structures"
means the same physical prints re-tested (not fresh re-prints of the
same nine designs), which the seat-artifact reading below assumes.

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
  → `12_batch_comparison.png` + `batch_comparison.json`.

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

- **The labels do not carry over.** Under the identity map the
  standardized fingerprint distance is ~2× the best-fit assignment's
  (19.2 vs 10.3), and identity pairs contradict the hop constants
  (e.g. `drran1` 69.1 ms vs `2dran1` 27.2 ms). As expected for a
  re-randomized batch.
- **The best-fit correspondence is suggestive, not decisive** (runner-up
  margins ≲ 0.2 z for most pairs — the low-hop articles are mutually
  degenerate): `drran1↔2dran9` (each batch's big-hop article, though
  69 → 54 ms is a larger change than any article has shown before),
  `drran8↔2dran8` (each batch's lowest-T article, 0.980 → 1.011),
  `drran7↔2dran1` (each batch's broadband/CH4-hot article — but hugely
  milder now: T1000 2.94 → 1.47, T180 1.251 → 1.079, CH4 16 → 6.2 %
  FS). @ctrhjk confirmed on 09-12 that these **are** the same nine
  structures — see the subsection below.
- **Batch level**: median T180 1.053 vs 1.037 (+1.6 %, inside the known
  session-to-session re-seat envelope), inputs within 1.3 %, Δv within
  2.4 %. Within-session precision matches (median CV ≈ 0.25 %).
- Full numbers: `figures/batch_comparison.json`.

### What the same-articles confirmation settles (09-12)

@ctrhjk: *"drran sets and 2dran sets are identical structures."* Taking
that as the same nine physical articles re-tested (it answers the
either/or in the check-in's question 1), a true bijection exists even
though the low-hop pairings stay degenerate, and two bounds hold under
**any** pairing:

- **The article that measured T180 = 1.2513 (`drran7`) re-measured
  ≤ 1.0900** (the 2dran max) — at least **−12.9 %**. The program-record
  amplifier was substantially a seat artifact; its broadband signature
  collapsed with it (best-fit partner `2dran1`: T1000 2.94 → 1.47, CH4
  raw 16 → 6.2 % FS).
- **The article that measured 0.9804 (`drran8`) re-measured ≥ 1.0109**
  (the 2dran min) — at least **+3.1 %**. Round 2's only attenuation
  measurement did not survive its re-seat: **as of now, round 2 has no
  reproducibly attenuating article** (all nine ≥ 1.011 in the latest
  seating).
- A third, near-assignment-free fact: `2dran2` (1.0900) is either the
  ex-`drran7` article (−12.9 %) or rose ≥ +4.1 % from ≤ 1.0471 — so at
  least one *mid-field* article also moved ≥ 4 %.

Best-fit paired T180 changes (pairings with runner-up margin ≲ 0.2 z
are indicative only):

| best-fit pair | T180 drran → 2dran | Δ |
|---|---|--:|
| `drran7 → 2dran1` (anchor) | 1.2513 → 1.0791 | **−13.8 %** |
| `drran3 → 2dran2` (degenerate) | 1.0389 → 1.0900 | **+4.9 %** |
| `drran9 → 2dran6` (degenerate) | 1.0425 → 1.0859 † | +4.2 % † |
| `drran8 → 2dran8` (anchor) | 0.9804 → 1.0109 | +3.1 % |
| `drran5 → 2dran5` | 1.0373 → 1.0604 | +2.2 % |
| `drran1 → 2dran9` (anchor) | 1.0326 → 1.0451 | +1.2 % |
| `drran2 → 2dran4` | 1.0345 → 1.0433 | +0.9 % |
| `drran6 → 2dran3` (degenerate) | 1.0471 → 1.0533 | +0.6 % |
| `drran4 → 2dran7` | 1.0344 → 1.0286 | −0.6 % |

† `2dran6` is the drift-flagged provisional mean; vs its late-session
level (~1.06) the change is ~+1.7 %.

Same-article seat-to-seat noise is therefore **heavy-tailed**: median
+1.2 %, five of nine within the known ±2.2 % re-seat envelope, tails at
+3–5 % and −13.8 %. Rank order is only partly preserved (Spearman
ρ ≈ 0.75 under best-fit — an upper bound, since the pairing was fitted
partly on T180). Two corollaries, promoted to standing conventions in
the repo `CLAUDE.md`:

1. **Within-session stability does not certify a seat.** `drran7` held
   1.251 at CV 0.77 % with no drift — it passed the T-drift watch —
   and was still wrong by ~14 %. Single-seating extremes (or any
   decision-driving T) need an independent re-seat confirmation before
   they count as article properties. Positive control: `6lhxfy`'s
   0.893 reproduced to 0.13 % across a day + re-seat — real
   attenuation does reproduce.
2. **Advisory seat gauge — broadband ratio T1000/T180** (healthy
   ≈ 1.00–1.07 on this mat): every large same-article shift on record
   carried ≥ 1.15 in at least one seating (`drran7` 2.35, `2dran2`
   1.15). Standing prediction, on record before any re-test:
   **`2dran1` (ratio 1.37, this batch's CH4-hot session) reads high at
   1.079 and should come down on its next re-seat.**

Once the per-label key lands, these two batches become a 9-article ×
2-seat reproducibility dataset — exactly the seat-noise model the BO
needs. The asks stand: the key for both batches (drranN → ID and
2dranN → ID yields the cross-batch mapping for free), and confirmation
that the articles are the same physical prints (not re-prints).
