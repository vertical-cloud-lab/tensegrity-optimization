# `corny1`–`corny9` check-in (09-12 / 09-14 sessions)

Nine 20-drop sessions posted by @ctrhjk on PR #86 (09-15) as subfolders
of the standing public Box share — the third randomized round-2 batch
after `drran1`–`drran9` (09-02/03) and `2dran1`–`2dran9`
(09-05/08/09). 60 in / arrangement B (1/2 in PU mat), current SOP
capture settings (4 ch, 1.25 MHz, 100 ms, 2 ms pre-trigger, 150 G
trigger on CH5). The Box folder labels say 9-14-2026 (the upload date);
per the TP4 timestamps `corny1`–`corny3` ran 09-12 (~14:09–14:56
local) and `corny4`–`corny9` ran 09-14 (~10:11–11:52), cadence
41–45 s, from the new TP4 database `TensegrityDataBase 3 (9-8-2026)`.
**The corny → design key is not in the repo, and — unlike drran/2dran —
the batch does not even fingerprint as the same nine articles** (see
the comparison below), so the composition question is open: same nine
structures again, or a new set (e.g. the round-2 BO-proposed designs)?
The per-label key remains the BO blocker.

- Box share `kkhmvnj9ni19b57dryk3gdroqrp5uf0b`, one subfolder per
  session (ids in each `raw/corny<n>/box-ids.json` manifest). Raw
  captures (~1.7 GB, 180 CSVs) stay on Box; the manifests re-fetch them
  via `scripts/fetch_box_shared_folder.py`. TP4 series tables are
  committed per session next to the manifests; the pipeline's raw CH5
  peaks agree with them to ≤ 0.78 % (median 0.22 %; Δv to ~2 %,
  different integration windows).
- 27 slo-mo clips (3 per session, ~7.5 GB) in Box subfolder
  `418098656735` — manifest at `video/box-ids.json` — with the 27 Sony
  XML sidecars committed under `video/xml/` (all
  `captureFps="959.04p"`). **First batch under the new film-drops-
  1/10/20 SOP, and it works**: the MP4s are named
  `cornyN-{1st,10th,20th}.MP4` and the sidecar `CreationDate`s pair to
  the TP4 `EventTime`s of drops 1/10/20 in recording order at a
  *constant* camera − DAQ clock offset of +31.45 to +31.50 min
  (camera clock fast) — deterministic pairing, exactly as intended.
  Exception: five clips sit one cadence later (+45–55 s) —
  `corny6-10th`, `corny6-20th`, `corny7-10th`, `corny7-20th`,
  `corny9-20th` — so the two `-10th` clips most likely filmed drop 11
  and the three `-20th` clips started after the session's final drop;
  verify against the MP4 content if those specific clips matter, and
  start the clip a beat *before* the target drop in future sessions.
  MP4s not analyzed this pass.
- Analysis: the standing campaign pipeline
  (`scripts/analysis/drop_test_campaign_analysis.py`, tail baseline,
  2-drop warm-up discard, standing T-drift watch) on the nine-session
  root → `figures/campaign_metrics.json` + `campaign_summary.csv` +
  `01_campaign_series.png` + `11_campaign_ranking.png`; fifth-drop
  waveform figures (Signal 5 of each session) via
  `scripts/analysis/drop_test_corny_checkin_analysis.py`
  → `02_corny1_drop5.png` … `10_corny9_drop5.png`; three-batch
  comparison via `scripts/analysis/drop_test_corny_batch_comparison.py`
  → `12_batch_comparison.png` + `batch_comparison.json`.

## Results (stabilized drops 3–20; T = TOP/CH5, CFC-180)

| session | T180 (CV) | drift slope %/drop | e2e % | T1000 | gauge T1000/T180 | in CFC-180 | Δv m/s | first-landing hop |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| `corny1` | 1.0459 (0.28 %) | −0.001 | −0.03 | 1.299 | **1.24 — suspect** | 219.8 G | 5.259 [settled] | 31.3 ms |
| `corny2` | 1.0846 (0.27 %) | −0.022 | −0.21 | 1.110 | 1.02 | 216.0 G | 5.104 [settled] | 31.8 ms |
| `corny3` | 1.0705 (0.12 %) | −0.019 | −0.25 | 1.248 | **1.17 — suspect** | 218.9 G | 5.197 [settled] | 30.8 ms |
| `corny4` | 1.0475 (0.24 %) | −0.032 | −0.38 | 1.076 | 1.03 | 225.2 G | 5.361 [healthy] | **≤ 15 ms (censored)** |
| `corny5` | 1.0876 (0.91 %) | **−0.144 — T-DRIFT FLAG** | **−1.90** | 1.197 | 1.10 | 222.3 G | 5.282 [healthy] | 29.2 ms (drifts 37 → 26) |
| `corny6` | 0.9106 (**1.99 %**) | −0.067 (n.s.) | −0.96 | 0.966 | 1.06 | 219.9 G | 5.190 [settled] | ~15/36 ms (bimodal, erratic) |
| `corny7` | **0.8031** (0.31 %) | +0.020 | +0.16 | **0.787** | 0.98 | 219.9 G | 5.215 [settled] | ~15.7 ms + main landing 41.7 ms |
| `corny8` | 0.9535 (0.26 %) | +0.023 | +0.35 | 0.986 | 1.03 | 220.2 G | 5.241 [settled] | **≥ 70 ms (at search cap)** |
| `corny9` | 0.8766 (0.42 %) | −0.005 | −0.03 | 0.885 | 1.01 | 218.1 G | 5.230 [settled] | 69.4 ms (near cap) |

ANOVA on T180: p = 9.0e-171, spread **28.8 %** — the widest
well-behaved batch of the program (drran's 25.7 % was one outlier —
excluding `drran7` it was 6.5 %; 2dran was 7.5 %; here the spread is
carried by four separate attenuating sessions). All 180/180 captures
triggered and parsed clean; no in-session pauses; no invalid captures;
worst channel ≤ 3.7 % of full scale everywhere except `corny6`'s CH4
(6.0 %). `e_rebound` where the hop is clean: `corny9` 0.0622, `corny8`
0.0598 (cap-censored, so a lower bound), `corny7` 0.0319 (main
landing), `corny2` 0.0305, `corny3` 0.0291, `corny1` 0.0287, `corny5`
0.0276, `corny6` 0.0197 (erratic), `corny4` ≤ 0.0140 (censored).

**The headline: four sessions attenuate — `corny7` 0.803, `corny9`
0.877, `corny6` 0.911, `corny8` 0.954 — where the previous two
round-2 batches (18 sessions, same nine articles twice) never measured
below 0.980.** `corny7` is the strongest attenuation on program record,
10 % below the previous best (`6lhxfy` 0.893 in the SOBOL campaign),
with a clean session (CV 0.31 %), a healthy broadband gauge (0.98 —
it attenuates CFC-1000 too, 0.787), and a textbook waveform
(`figures/08_corny7_drop5.png`: output visibly under input through the
whole pulse). Per the standing between-seat replication rule
(`CLAUDE.md`), all four attenuation numbers — and especially the
record — are **single-seating values pending an independent re-seat
confirmation** before they count as article properties (positive
control: real attenuation reproduces — `6lhxfy` 0.893 held to 0.13 %
across a day + re-seat).

## Anomaly screen

1. **T-drift watch (standing instruction): `corny5` is flagged** —
   slope −0.144 %/drop (p = 1.0e-5; envelope ±0.06), end-to-end
   −1.90 %. The pipeline's binary attribution labels it "common-mode /
   input-side", but that rule only pattern-matches a *rising* output:
   the per-channel numbers (output −2.61 % vs input −0.72 % end-to-end)
   show the excess is an **output-side decline** — an inverted r2d2c2
   signature (mount/wax coupling settling *in* rather than loosening),
   T sliding 1.100 → 1.068 with no plateau established. Its mean
   (1.0876) is drift-contaminated; late-session level ≈ 1.07. If
   `corny5`'s number matters downstream, re-seat and re-run. The other
   eight sessions pass the watch (|e2e| ≤ 0.96 %).
2. **`corny6` is erratic without tripping the watch** — CV 1.99 %
   (4–8× batch-typical), T swinging 0.888–0.964 in non-monotone steps
   (slope n.s., so no flag), hop timing bimodal (15/36 ms), and the
   batch's hottest channel (CH4 6.0 % FS). This is the `2dran6` family
   of latent seat instability. Its mean (0.911) is low-confidence —
   though it attenuates under any reading (session max 0.964).
3. **Advisory seat gauge (T1000/T180 ≳ 1.15 = suspect): `corny1`
   (1.24) and `corny3` (1.17) trip it; `corny5` (1.10) is borderline.**
   Every large same-article shift on record carried a gauge ≥ 1.15 in
   at least one seating, so `corny1`/`corny3`'s T180 (1.046 / 1.071)
   should be treated as possibly-high pending re-seat. All four
   attenuators gauge healthy (0.98–1.06) — the attenuation does not
   carry the bad-seat signature.
4. **Hop-detector boundary effects** (search window 15–70 ms):
   `corny4` sits pinned at the 15 ms floor (a `2dran2`-class
   small-hop article); `corny8` sits at the 70 ms cap (its e_rebound
   is a lower bound) and `corny9` just under it (69.4 ms) — the two
   biggest hops of the program; `corny7` double-bounces (first landing
   ~15.7 ms, main landing 41.7 ms — argmax flips, so its t_second
   mean/CV are mixtures); `corny6` is erratic. `corny1/2/3/5` are
   clean.
5. **`corny8`'s ringdown sits at 764 Hz** where every other session in
   this and the two prior batches fits 300–420 Hz — with the batch's
   best fit quality (r² usable on 89 % of drops, ζ 4.8 %). A
   structurally distinct article, whatever the batch composition is.
6. **Rig health is fine**: Δv 5.10–5.36 m/s (healthy/settled band) on
   all nine, inputs 216–225 G on the campaign plateau, pulse width
   2.41–2.48 ms, cadence normal, zero missed triggers. The 09-14
   sessions ran ~44–45 s cadence vs 41–42 s on 09-12 (slower hoist
   day, no data impact).

## Cross-batch comparison (vs drran and 2dran, `figures/12_batch_comparison.png`)

- **Identity labeling is rejected in both directions** (standardized
  fingerprint cost: drran → corny identity 23.8 vs best-fit 14.6;
  2dran → corny identity 22.3 vs best-fit 16.7) — as expected for
  re-randomized labels.
- **But unlike drran ↔ 2dran, the batches don't even match as *sets*.**
  The drran ↔ 2dran best-fit closed at total cost 10.3 with the same
  T range; here the best-fit costs are 40–60 % higher, the
  triangulation is incoherent (drran → 2dran → corny agrees with the
  direct drran → corny map on only **2 of 9** articles), and the T
  *distribution* itself is incompatible: four corny sessions sit below
  every one of the 18 prior round-2 measurements (drran min 0.980,
  2dran min 1.011). Reading `corny7` = 0.803 as a re-seat of any
  drran/2dran article requires a −18 to −21 % same-article shift —
  and the four attenuators together require simultaneous shifts of
  −8/−12/−15/−18 % — against a measured same-article seat-noise
  distribution with median +1.2 %, typical tails +3–5 %, and a single
  −13.8 % outlier that *corrected a pathologically high seat back to
  the field*, never below it. Add `corny8`'s unique 764 Hz mode and
  the conclusion is: **at least the four attenuating articles are new
  to round 2's measured population — this is (at least partly) a
  different set of structures, not a third seating of the same nine.**
- **Batch level**: median T180 1.046 (drran 1.037, 2dran 1.053 — the
  amplifier half of corny sits exactly in the familiar band), batch-mean
  inputs within 0.7 % (218.8–221.6 G), Δv within 1.7 % (5.19–5.32 m/s).
  Within-session precision matches (median CV ≈ 0.27 %).
- **The on-record 09-12 prediction** (`2dran1`, gauge 1.37, "reads
  high at 1.079 and should come down on re-seat") **is not resolved by
  this batch**: assignment-free it fails to bind (corny max 1.0876 >
  1.0791), and the best-fit partner — `corny1` at 1.0459, i.e. −3.1 %,
  *consistent* with the prediction — has a runner-up margin of 0.03 z,
  worth nothing on its own. Suggestive footnote: `corny1` is again its
  batch's broadband-hottest session (gauge 1.24), so if the ex-`drran7`
  article *is* in this batch, `corny1` is the natural candidate and the
  gauge lineage would read 2.35 → 1.37 → 1.24 with T180
  1.251 → 1.079 → 1.046. Candidate only; the key decides.
- Full numbers: `figures/batch_comparison.json`.

## What this batch needs from the lab

1. **The key, more urgent than ever**: what are `corny1`–`corny9`
   (label → article/design ID, and whether any of them are the
   drran/2dran nine)? If these are the round-2 BO-proposed designs,
   the campaign has just found its first genuine attenuators — led by
   a program record — and none of it can reach the BO without the
   mapping.
2. **Re-seat confirmations** per the standing rule, in priority order:
   `corny7` (the record — 20 drops after an independent mount re-seat
   settles it), `corny9`, then re-seat + re-run for the two unstable
   sessions (`corny5` flagged, `corny6` erratic) and the two gauge
   suspects (`corny1`, `corny3`).
3. Camera SOP tweak: start each clip *before* the target drop — five
   of this batch's 27 clips ran one drop late (item in the video note
   above).
