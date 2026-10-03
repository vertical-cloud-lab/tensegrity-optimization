# `dran31`–`dran39` check-in: third print of the round-3 plate (09-28 / 09-29 / 10-02 sessions)

Nine 20-drop sessions posted by @ctrhjk on PR #86 (10-03) as subfolders
of the standing public Box share. 60 in / arrangement B (1/2 in PU
mat), current SOP capture settings (4 ch, 1.25 MHz, 100 ms, 2 ms
pre-trigger, 150 G trigger on CH5), TP4 database
`TensegrityDataBase 3 (9-8-2026)`. The Box folder labels say 10-02-2026
(the upload date). Per the TP4 series tables, the sessions ran on three
days, local time: `dran31`–`dran32` on 09-28 (18:53–19:38),
`dran33`–`dran36` on 09-29 (18:42–19:55), and `dran37`–`dran39` on
10-02 (16:29–17:14). Cadence was 41 s, with no pauses.

**What the articles are.** This is the **third print of the round-3
plate (trials 28–36)**, requested by @me-madsen on PR #102 (09-28) to
compare against `drran` (print 1) and `2dran` (print 2). The files
first named the articles `3dranN`. The lab labeled them `dran3N`, and
PR #102's relabel (`e9f5e2d`, 10-01) made `dran3N` canonical. Labels
follow the same build-plate raster as the first two prints, so
**`dran3N`, `drranN` and `2dranN` are the same design.** Key:
`params.json` here (geometry and infill from the round-3 print key,
masses from @ctrhjk's 09-28 print log on issue #98, where no defects
were noted). It is joined into `figures/campaign_summary.csv` and the
`design_params` of `figures/campaign_metrics.json`. This print averages
20.07 g, against 19.86 g for 2dran and 19.59 g for drran.

- Box share `kkhmvnj9ni19b57dryk3gdroqrp5uf0b`, one subfolder per
  session. The ids are in each `raw/dran3<n>/box-ids.json` manifest.
  Raw captures (~1.7 GB, 180 CSVs) stay on Box; the manifests re-fetch
  them with `scripts/fetch_box_shared_folder.py`. The TP4 series tables
  are committed next to the manifests. The pipeline's raw CH5 peaks
  agree with them to ≤ 0.43 % (median 0.05 %). Δv reads 3–6 % below the
  TP4's, because the integration windows differ, as in earlier batches.
- The 27 slo-mo clips (~14.7 GB) are in Box subfolder `423840097728`,
  with the manifest at `video/box-ids.json`. The 27 Sony XML sidecars
  are committed under `video/xml/`; all read `captureFps="959.04p"`.
  The film-drops-1/10/20 SOP was followed: the MP4s are named
  `dran3N-{1st,10th,20th}.MP4`.
  - **The camera clock was reset.** The sidecars read 2018-01-01,
    2018-01-02 and 2018-01-05. The camera still runs a constant
    3,192 d 9 h 56 m (±4 s) behind the DAQ on all three days, so
    pairing works.
    The sidecars run C0019–C0045 in recording order. The one short
    sidecar (C0020, 1824 frames) matches the one short MP4
    (`dran31-10th`, 487 MB vs ~548 MB), which pins the XML ↔ MP4 order.
  - **Pairing:** 22 of 27 clips land within ±1 s of their target
    drop's TP4 `EventTime`. Three `-10th` clips (`dran32`, `dran33`,
    `dran37`) filmed **drop 11**, one cadence late, as five corny clips
    did. Two `-20th` clips filmed **a drop after the session's last
    capture**, so no DAQ record exists for them: `dran31-20th`
    (+254 s after drop 20) and `dran35-20th` (+46 s).
  - **On-camera identity check:** the operator tapes the session label
    to the carriage. A rest frame from each drop-10 clip
    (`figures/14_video_identity_montage.jpg`, from
    `scripts/analysis/drop_test_dran3_video_frames.py`) shows the
    expected label in 9 of 9 clips. The clips are portrait recordings
    stored unrotated; rotate 90° clockwise to view them upright.
- Analysis uses the standing campaign pipeline
  (`scripts/analysis/drop_test_campaign_analysis.py --params params.json`,
  tail baseline, 2-drop warm-up discard, standing T-drift watch) on the
  nine-session root. It writes `figures/campaign_metrics.json`,
  `campaign_summary.csv`, `01_campaign_series.png` and
  `11_campaign_ranking.png`. The fifth-drop figures (`02_dran31_drop5.png`
  … `10_dran39_drop5.png`) come from
  `scripts/analysis/drop_test_drran_checkin_analysis.py --raw … --out …`,
  reused as for 2dran. The three-print comparison comes from
  `scripts/analysis/drop_test_round3_three_print_comparison.py`
  (`12_three_print_comparison.png` + `three_print_comparison.json`).

## Results (stabilized drops 3–20; T = TOP/CH5, CFC-180)

| session | design | T180 (CV) | drift slope %/drop | e2e % | T1000 | gauge T1000/T180 | in CFC-180 | Δv m/s | first-landing hop |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| `dran31` | t36 | 1.0209 (0.25 %) | +0.003 | +0.00 | 1.048 | 1.03 | 218.7 G | 5.191 [settled] | 34.2 ms |
| `dran32` | t33 | 1.0386 (0.12 %) | −0.013 | −0.14 | 1.061 | 1.02 | 216.4 G | 5.164 [settled] | 16.2 ms (near the 15 ms floor) |
| `dran33` | t31 | 1.0366 (0.47 %) | +0.017 | +0.23 | 1.075 | 1.04 | 216.1 G | 5.200 [settled] | 24.3 ms (bimodal, CV 45 %) |
| `dran34` | t29 | 1.0201 (0.25 %) | −0.037 | −0.47 | 1.069 | 1.05 | 216.1 G | 5.149 [settled] | 53.2 ms |
| `dran35` | t28 | **1.1679 (1.46 %)** | +0.079 (n.s.) | +0.86 | **2.840** | **2.43, suspect** | 214.8 G | 5.062 [settled] | 24.8 ms (23 / 34 ms, bimodal) |
| `dran36` | t34 | 1.0353 (0.08 %) | +0.002 | +0.02 | 1.046 | 1.01 | 217.5 G | 5.114 [settled] | 24.1 ms |
| `dran37` | t32 | 1.0448 (0.29 %) | −0.036 | −0.55 | 1.091 | 1.04 | 217.3 G | 5.288 [healthy] | 38.0 ms |
| `dran38` | t35 | **0.9958 (0.57 %)** | −0.049 (p = 0.055) | −0.59 | 1.057 | 1.06 | 213.6 G | 5.193 [settled] | 29.4 ms |
| `dran39` | t30 | 1.0438 (0.12 %) | +0.004 | +0.03 | 1.067 | 1.02 | 214.3 G | 5.211 [settled] | 24.0 ms |

ANOVA on T180 gives p = 6.7e-129. The spread is 16.5 %, but 4.8 % without
`dran35`. All 180 of 180 captures triggered and parsed cleanly. There were
no invalid captures and no in-session pauses. The worst channel is
≤ 3.5 % of full scale everywhere except `dran35`'s CH4 (13.8 %) and
`dran38`'s CH4 (5.6 %). Batch level: median T180 is 1.0366 (drran
1.0373, 2dran 1.0533). Inputs are 213.6–218.7 G and Δv is
5.06–5.29 m/s, both on the campaign plateau. Median within-session CV
is 0.25 %.

## Anomaly screen

1. **T-drift watch (standing instruction): clean.** No session breaks
   the envelope (worst |e2e| 0.86 %, worst significant |slope|
   0.037 %/drop); r2d2c2-style drift did not recur. One sub-threshold
   feature: **`dran38` steps down once after drop 4.** Drops 3–4 read
   1.010/1.012; drops 5–20 sit on a 0.9939 plateau (CV 0.15 %). The
   step is output-side (output 216.6 → 212.2 G, input flat at
   214.2 → 213.5 G), and the hop lengthens at the same drop
   (28.1 → 29.3 ms). It looks like a seat that settled once, not drift.
   The plateau value (0.994) is the better number for this article.
2. **Advisory seat gauge: `dran35` trips it hard (2.43)**, the
   batch's only suspect seat. It is the `drran7` pathology on a
   different design: T180 1.168 at CV 1.46 % (±3 % drop-to-drop swings,
   1.141–1.207), T1000 2.84, and an output CFC-1000 peak of 718 G
   against ~270–280 G on every other session. Its two highest-T drops
   (S12 1.207, S17 1.194) are the only ones whose hop lands at ~34 ms
   instead of ~23–24 ms, so the vertex is rattling on its seat. The
   print log notes no defects, so a bad seat is the lead suspect, with
   an unlogged article defect as the alternative. A side-by-side of its
   drop-10 impact against its infill-only clone sibling `dran39`
   (`figures/15_video_impact_dran35_vs_dran39.jpg`) shows no visible
   difference at 960 fps in this framing. Both specimens stay seated
   and upright, and the sensor stays on. **Do not use 1.168 as t28's
   value.** The replicate-study artifact rule (PR #102,
   `bo/t3-prism-replicate-study-plan.md`) applies: it sits +10.1 % from
   t28's three-print median, ~12 article sd away, so it needs a mount
   re-seat and a 10–12 drop re-run before it can be excluded. The other
   eight sessions gauge healthy (1.01–1.06).
3. **Hop-detector boundary effects** (search window 15–70 ms):
   `dran32` sits near the 15 ms floor, as `2dran2` did on the same
   design (t33). `dran33` and `dran35` are bimodal, so their
   `t_second`/`e_rebound` means are mixtures. `dran34` (53.2 ms) and
   `dran37` (38.0 ms) are clean. As before, hop timing is an article
   property and not a design one: t29's hop reads 32.5 / 40.1 / 53.2 ms
   across the three prints.
4. **Rig health is fine.** Δv is 5.06–5.29 m/s (8 settled, 1 healthy).
   The batch mean of 5.18 m/s is the lowest of the four check-in
   batches (drran / 2dran / corny 5.32 / 5.19 / 5.23 m/s), still inside
   the settled band. Inputs are 214–219 G, pulse width
   2.45–2.54 ms, and there were no missed triggers.

## Three-print comparison (`figures/12_three_print_comparison.png`, `three_print_comparison.json`)

Same label index means the same design. Health screen: gauge < 1.145
and no T-drift flag. Six of the 27 sessions fail it (`*`). The
deviation in brackets is from the design's three-print median.

| # | design | pred | print 1 `drran` | print 2 `2dran` | print 3 `dran3` | screened mean |
|--:|---|--:|---|---|---|--:|
| 1 | t36 | 1.051 | 1.0326 (g 1.07) | 1.0791* (g 1.37, +4.5 %) | 1.0209 (g 1.03) | 1.027 |
| 2 | t33 | 1.057 | 1.0345 (g 1.09) | 1.0900* (g 1.15, +4.9 %) | 1.0386 (g 1.02) | 1.037 |
| 3 | t31 | 1.043 | 1.0389 (g 1.11) | 1.0533 (g 1.13) | 1.0366 (g 1.04) | 1.043 |
| 4 | t29 | 1.032 | 1.0344 | 1.0433 | 1.0201 | 1.033 |
| 5 | t28 | 1.059 | 1.0373 | 1.0604 | 1.1679* (g 2.43, +10.1 %) | 1.049 |
| 6 | t34 | 1.065 | 1.0471 | 1.0859* (drift, +3.7 %) | 1.0353 | 1.041 |
| 7 | t32 | 1.020 | 1.2513* (g 2.35, +19.8 %) | 1.0286 | 1.0448 | 1.037 |
| 8 | t35 | 1.039 | 0.9804* (drift) | 1.0109 | 0.9958 | 1.003 |
| 9 | t30 | 1.058 | 1.0425 | 1.0451 | 1.0438 | 1.044 |

What three prints settle:

- **Print-to-print noise is smaller than the two-print estimate.** On
  the 21 screened sessions, a design + print-offset fit leaves a
  residual article+seat sd of **0.0087** (dof 10, worst residual
  0.013). The replicate-study plan pre-registered ~0.013 from the
  drran/2dran pairs. Print offsets against print 1 are +0.008 for
  print 2 and −0.003 for print 3.
- **The 2dran batch offset was not about mass.** Print 3 is the
  heaviest print (+0.21 g over 2dran), yet its median T sits back at
  print 1's level (1.0366 vs 1.0373). Print 2's raw +1.6 % median
  offset comes mostly from its three unhealthy sessions (`2dran1`,
  `2dran2`, `2dran6`); screened, print 2 sits only +0.8 % above.
  This corrects the 09-15 reading, which offered the +1.3 % mass
  difference as a candidate driver.
- **The seat gauge marked every gross outlier.** All four sessions in
  round 3 that tripped the gauge are their design's high outlier, at
  +4.5 / +4.9 / +10.1 / +19.8 % above the three-print median. The 20
  sessions with a healthy gauge (≤ 1.07) sit at a median 0.17 % from
  their design median, max 3.7 % (`2dran6`, which is drift-flagged).
  Gauge vs deviation gives Spearman ρ = +0.52 (p = 0.006). Two of the
  27 sessions are gross artifacts (`drran7`, `dran35`, both ≥ 10 % off).
  That is about 1 in 14, a little above the replicate-study plan's
  "about 1 article in 20". The gauge plus drift watch catches them
  without needing a sibling.
- **Standing checks:**
  - **t32 resolved.** `drran7`'s 1.251 was an article or seat
    artifact. The two clean prints read 1.029 and 1.045, close to the
    1.020 prediction.
  - **t36: the CLAUDE.md prediction is supported at design level.** The
    prediction was that `2dran1` (gauge 1.37) reads ~4 % high. The
    healthy-gauge prints of t36 read 1.033 (`drran1`) and 1.021
    (`dran31`), so `2dran1` reads +5.1 % above their mean. A re-seat of
    the `2dran1` article itself would still be needed for the
    article-level test.
  - **t35 is the lowest-T design in every print** (0.980* / 1.011 /
    0.996, screened mean 1.003). It is round 3's only twisted design
    (61.5°). It sits at T ≈ 1.00, not a meaningful attenuator next to
    corny7's 0.803. **Round 3 still has no attenuating design.**
- **Design signal in round 3 is mostly t35.** The additive-fit design
  means span 1.001–1.045, with between-design sd 0.0136. Without t35
  the other eight span 1.028–1.045 (sd 0.006), which is below the
  0.0087 article sd. Single articles cannot rank those eight, so pairwise rank
  agreement between prints is poor (ρ = 0.08 drran–2dran, 0.67
  drran–dran3, 0.20 2dran–dran3). Pooled over prints, the screened
  design means track the frozen round-3 predictions at **ρ = 0.75
  (p = 0.02), RMS 0.020**. Print 3 alone gives ρ 0.30, and print 2
  alone 0.72.

## What this batch needs from the lab

1. **Re-seat `dran35` and re-run it for 10–12 drops** (replicate-study
   artifact rule). If it comes back near 1.04–1.06, the 1.168 was the
   seat. If it repeats around 1.17, the article is suspect; then weigh
   it and inspect its tendons. Either way both sessions stay in the
   record.
2. **BO ingestion (PR #102):** the round-3 loader now maps
   `dran3N → drranN` (`REPRINT_PREFIX`, `e9f5e2d`). `dran35`'s 1.168
   should go in only with its gauge flag, or be held back until the
   re-seat. The same applies to the other unhealthy round-3 sessions
   (`drran7`, `drran8`, `2dran1`, `2dran2`, `2dran6`). The screened
   design means above are the round-3 values to quote.
3. Optional: a 20-drop re-seat of `2dran1` would close the article-level
   test of the t36 prediction. The ex-`drran7` re-seat that the 2dran
   check-in asked for is lower priority now that t32 is settled at
   design level. It would still separate defect from seat for that one
   article.
4. Camera: reset the RX100's date/time. Pairing survived because the
   offset stayed constant, but a correct clock makes the sidecars
   self-describing. Also start the `-10th`/`-20th` clips a beat before
   the target drop (3 of 9 `-10th` clips filmed drop 11).
