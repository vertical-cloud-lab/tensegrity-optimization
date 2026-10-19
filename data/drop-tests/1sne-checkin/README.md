# `1sne21`–`1sne83` check-in: replicate study, plate 1 (10-17 sessions)

Nine 20-drop sessions posted by @ctrhjk on PR #86 (10-19) as subfolders
of the standing public Box share. The links were posted without the
share prefix (`byu.app.box.com/folder/<id>`), but every id resolves under
the share `kkhmvnj9ni19b57dryk3gdroqrp5uf0b`. Settings: 60 in /
arrangement B (1/2 in PU mat), current SOP capture (4 ch, 1.25 MHz,
100 ms, 2 ms pre-trigger, 150 G trigger on CH5), TP4 database
`TensegrityDataBase 3 (9-8-2026)`. All nine sessions ran on one evening,
10-17, in label order: 16:55 (`1sne21`) to 22:09 (`1sne83`), at a 41 s
cadence. `1sne83` paused for 1 h 44 min after its third drop.

**What the articles are.** This is **plate 1 of the pre-registered
replicate study** (PR #102, `bo/t3-prism-replicate-study-plan.md`,
picks accepted 09-28; print key `bo/replicate-study/t3-prism-replicate-print-key.csv`).
The plate holds three copies each of three round-4 designs, printed
from one gcode at the round-4 filament point:

| label | design | trial | role in the plan | first article (one print, one seat) |
|---|---|---|---|---|
| `1sne71`, `1sne72`, `1sne73` | corny7 | t37 | on the front: the 0.803 record | 0.8031 |
| `1sne81`, `1sne82`, `1sne83` | corny8 | t39 | corny7's near-twin (TPU infill 34 vs 21 %) | 0.9535 |
| `1sne21`, `1sne22`, `1sne23` | corny2 | t38 | far end (tall amplifier family) | 1.0846 |

The last digit is the copy (plate row: 1 = back, 2 = middle, 3 =
front). Key: `params.json` (geometry and infill from the round-4 key;
masses from @ctrhjk's 10-17 print log on issue #98, where no defects were
noted). Plate 1 printed heavy: every copy weighs 0.5–0.9 g (2–4 %)
more than its first article. corny7 copies are 20.23–20.27 g against
19.62 g, corny8 copies 20.11–20.30 g against 19.64 g, and corny2 copies
20.89–21.08 g against 20.21 g. Plates 2 and 3 (weighed 10-17, not yet
dropped) are up to 0.4 g lighter than plate 1; their corny8 copies
weigh about the same.

- Raw captures (~1.6 GB, 180 CSVs) stay on Box. The ids are in each
  `raw/1sne<nn>/box-ids.json`, next to the committed TP4 series table.
  The 27 slo-mo clips (~14.6 GB) are in Box folder `428979535052`
  (`video/box-ids.json`). Their 27 Sony XML sidecars are committed in
  `video/xml/`, and all read `captureFps="959.04p"`.
- Analysis:
  - `scripts/analysis/drop_test_campaign_analysis.py --params params.json`
    (standing pipeline, tail baseline, 2-drop warm-up, T-drift watch)
    writes `figures/campaign_metrics.json`, `campaign_summary.csv`,
    `01_campaign_series.png` and `11_campaign_ranking.png`.
    **This batch is why that pipeline now has a plausibility screen**
    (`screen_reason`, see below).
  - `scripts/analysis/drop_test_1sne_checkin_analysis.py --raw … --ref …`
    writes the fifth-drop figures (`02`–`10`), the capture census
    (`capture_census.json`), figures `12`–`15` and
    `replicate_interim.json`. `--ref` takes the original corny sessions
    (Box ids in `../corny-checkin/raw/`).
  - `scripts/analysis/drop_test_1sne_video_frames.py --mp4 …` writes
    `16_video_identity_montage.jpg` and `video_pairing.json`.
  - `scripts/analysis/drop_test_corny_1sne_video_comparison.py --mp4 … --daq …`
    writes the side-by-side videos with the first articles
    (`video/compare/`) and `figures/video-compare/` (see "Side by side with
    the first articles").

## Headline

1. **The recording had two separate faults; the specimens are not the
   problem.**
   - **58 of 180 captures are unusable.** Of those, 56 are *mistimed*:
     the TP4 triggered, but the 100 ms record contains no impact. They
     cluster in one hour, 17:18 → 18:17, from `1sne22` drop 11 through
     the end of `1sne72`. That is 56 of the 70 captures in that window.
   - **All six corny7 and corny8 sessions have a knocking top
     sensor.** A ~0.1 ms spike at impact onset (up to 3,500 G) reads T180
     high, and every one of those sessions fails the 1.145 seat gauge.
   - Only the three corny2 copies are clean.
2. **corny7's 0.803 did not reproduce on any drop.**
   - All 24 valid corny7-copy drops read 0.884–0.998.
   - The one copy with a full session (`1sne73`) reads **0.910**, and
     **0.900** on its only drop with no knock (gauge 1.00).
   - Taking the knock out (low-gauge drops only, or the drop-level
     correction) moves corny7 to 0.895–0.904, not toward 0.803.
3. **The corny7 − corny8 gap shrinks from −0.150 to about −0.03 under
   every reading.** That is inside the plan's "collapses to 0.05 or
   less" branch, and close to what the two frozen models predicted
   (+0.006 held-out, −0.020 round-4). It is **interim**, though: every
   corny7/corny8 number here comes from a knocking seat.
4. **corny2 replicates.** Its three copies read 1.063 / 1.069 / 1.077
   on healthy seats, against 1.085 for the first article. The
   article-level sd is 0.0072, or 0.0085 pooled with round 3, under the
   plan's 0.015 line.

## Fault 1: mistimed captures (17:18 → 18:17)

Captures by kind (`capture_census.json`, `figures/12_capture_timeline.png`):

| session | design | captures | clean (gauge < 1.145) | knock (gauge ≥ 1.145) | mistimed | other unusable |
|---|---|--:|--:|--:|--:|--:|
| `1sne21` | corny2 | 20 | 19 | 1 (warm-up drop 2) | 0 | 0 |
| `1sne22` | corny2 | 20 | 11 | 1 (drop 10) | 8 (drops 11–20 except 14, 17) | 0 |
| `1sne23` | corny2 | 20 | 6 | 0 | 12 | 2 (S2: CH5 Δv 3.4 m/s; S18: 7.5–9.5 kG one-sample spike on all three top axes) |
| `1sne71` | corny7 | 20 | 0 | 2 (drops 13, 14) | 18 | 0 |
| `1sne72` | corny7 | 20 ¹ | 0 | 2 (drops 5, 6) | 18 | 0 |
| `1sne73` | corny7 | 20 | 6 | 14 | 0 | 0 |
| `1sne81` | corny8 | 20 | 1 | 19 | 0 | 0 |
| `1sne82` | corny8 | 20 | 4 | 16 | 0 | 0 |
| `1sne83` | corny8 | 20 | 3 | 17 | 0 | 0 |

¹ The export holds events 1–9 and 15–25. Events 10–14 (18:07–18:11)
are missing, and events 20–22 fired 7–9 s apart, off the drop cadence.
`1sne71` event 11 also fired off-cadence (26 s after event 10).

**How we know these captures contain no impact:**

- **No impact on the top sensor.** The top-vertex channels never exceed
  noise in the mistimed captures. Their largest TP4 CH4 peak is 15 G,
  against 230–3,560 G on every valid capture. The top Z velocity change
  over the impact window is ≤ 0.08 m/s, against ~5 m/s on a real impact.
- **The top sensor was connected and working.** Its white-noise floor
  in the mistimed captures (0.50 / 0.52 / 0.46 G on CH2/3/4) is the
  same as in valid ones. An unplugged or unpowered sensor would change
  it.
- **The drops themselves were normal.** Seven slo-mo clips land on
  mistimed captures within ±1 s. In each, the carriage falls through the
  frame and lands with the same motion profile as every other clip, and
  the sensor sits on the vertex before and after (`figures/16`).
- **CH5 was misbehaving.** Its trace in mistimed captures is steps and
  plateaus of ±100–450 G, not a half-sine. The pipeline's Δv reads
  0.2–116 m/s, and the TP4's own table reads Δv up to ~12,500 in/s.
  Even the valid captures inside the window carry CH5 baseline steps
  (`figures/12`, bottom panel). On those, CH5 peaks disagree with the
  TP4 table by up to 9 %, against a 0.12 % median over all valid
  captures.

**Reading:** the CH5 (input + trigger) chain was intermittent for that
hour. The likeliest cause is a loose connector or a damaged cable at
either end. It fired the trigger at moments other than the impact, so
the record missed the drop.

- It began one drop after the evening's first strong knock (`1sne22`
  drop 10, CH4 1,165 G, 17:17:51).
- It cleared between `1sne72` (last capture 18:17) and `1sne73` (first
  capture 18:23). From then on, all 80 captures hold an impact.

The standing pipeline's validity check (raw input ≥ 150 G) passed 51 of
the 56 mistimed captures, so before the fix they went straight into the
means.
`1sne71`'s first pass read T180 = 0.12 with Δv 19 m/s. It now screens
every capture with `screen_reason`:

- no top-vertex impact (T180 < 0.5);
- non-physical input Δv (outside 3.5–7 m/s);
- a top channel above 50 % of full scale.

Across the 1,480 scored drops of every earlier campaign-pipeline batch
(08-13 → 10-02), per-drop T180 ran 0.80–1.27, Δv 4.76–5.56 m/s, and the
top channels peaked at 16 % of full scale. The limits sit far outside
that range, so no earlier result changes.

## Fault 2: the top sensor knocks (all six corny7/corny8 sessions)

`figures/13_fault_waveforms.png` shows one capture of each kind.
Healthy drops (`1sne21`) show CH4 riding CH5's half-sine. In the
corny7/corny8 sessions, CH4 instead fires a ~0.1 ms spike early in the
impact (600–3,560 G), with opposite-sign spikes on the lateral axes and
no matching event on CH5. That is the signature of the sensor tapping
its seat. The ringdown fit locks onto a **lateral (Y-axis) ring at
820–880 Hz** (session means) in those sessions. The healthy corny2
copies ring at 380–490 Hz, and the corny7 first article at 418 Hz.

**What the knock does to T180** (`figures/14_t180_vs_gauge.png`):

- Within each knocking session, T180 rises drop by drop with the per-drop
  gauge T1000/T180, at **+0.092 ± 0.008 per unit gauge** (session-demeaned,
  t = 11.9, 72 drops in `1sne73`, `1sne81`, `1sne82`, `1sne83`).
- This is the first drop-level calibration of the advisory seat gauge.
  It confirms the round-3 pattern (gauge-tripping sessions read high,
  +4.5 to +19.8 %) inside single sessions.

**The top sensor's gain is intact.** A knock cannot fake a velocity
change, because momentum is conserved through it. So the check below
compares the top Z axis's velocity change over the impact (−3 to +15 ms)
with CH5's:

| design | first article | plate-1 copies |
|---|--:|---|
| corny2 | 0.997 | 0.961 / 1.007 / 1.016 |
| corny7 | 0.959 | 0.962 / 0.964 / 0.994 |
| corny8 | 0.978 | 1.018 / 0.918 / 0.936 |

A gain error large enough to explain corny7's +12 % would show up here.
It doesn't.

**Was it the seat or the design family?** These data can't separate the
two.

- The batch ran all corny2 copies first, then all corny7, then all
  corny8. The plan asked for designs interleaved within each block, so
  design is confounded with time of evening, including the fault hour.
- The wide, thin-cable family has knocked before. In the round-4 TP4
  tables, the TP4 timed CH4's peak as a sub-millisecond spike on 18 of
  20 drops for corny8's first article and 20 of 20 for corny6's, though
  both kept healthy gauges (1.03, 1.06). corny7's first article never
  did.

## Results (stabilized valid drops; T = TOP/CH5, CFC-180)

| session | design | valid/captures (scored) | T180 (CV) | drift %/drop, e2e % | T1000 | gauge | in CFC-180 | Δv m/s |
|---|---|---|--:|--:|--:|--:|--:|--:|
| `1sne21` | corny2 | 20/20 (18) | **1.0629** (0.50 %) | +0.015, +0.22 | 1.106 | 1.04 | 218.4 G | 5.28 [healthy] |
| `1sne22` | corny2 | 12/20 (10) | 1.0715 (1.63 %) | −0.209 (n.s.), −0.48 | 1.259 | 1.17 ² | 209.8 G | 5.11 [settled] |
| `1sne23` | corny2 | 6/20 (6) | **1.0772** (1.41 %) | +0.140 (n.s.), −0.18 | 1.099 | 1.02 | 208.1 G | 4.96 [settled] |
| `1sne71` | corny7 | 2/20 (2) | 0.9380 | — | 1.291 | **1.38** | 208.3 G | 5.01 [settled] |
| `1sne72` | corny7 | 2/20 (2) | 0.9723 | — | 1.957 | **2.01** | 208.4 G | 4.95 [settled] |
| `1sne73` | corny7 | 20/20 (18) | 0.9095 (1.14 %) | −0.112 (p = 0.025), −1.44 | 1.052 | **1.16** | 214.2 G | 5.05 [settled] |
| `1sne81` | corny8 | 20/20 (18) | 0.9101 (1.93 %) | −0.132 (n.s.), −1.05 | 1.319 | **1.45** | 216.4 G | 5.04 [settled] |
| `1sne82` | corny8 | 20/20 (18) | 1.0161 (3.11 %) | +0.040 (n.s.), −0.56 | 1.425 | **1.40** | 215.9 G | 5.10 [settled] |
| `1sne83` | corny8 | 20/20 (18) | 0.9951 (4.53 %) | −0.228 (n.s.), −2.07 | 1.764 | **1.77** | 221.1 G | 5.23 [settled] |

² The single drop-10 knock (gauge 2.44) is the whole story here. The
other nine scored drops average 1.0693 at gauge 1.03. Drops 3–9
(before the fault) read 1.077; the two valid drops after it read 1.056
and 1.031.

- **T-drift watch (standing instruction): clean by the rule.** No
  session breaks |slope| > 0.06 %/drop at p < 0.01 or |e2e| > 2.5 %.
  But the corny7/corny8 sessions scatter at CV 1.1–4.5 %, 4–16× the
  campaign's typical 0.28 %, which leaves the slope test with little
  power. `1sne73`'s −0.112 %/drop (p = 0.025) is the nearest miss. The
  seat gauge is the operative flag in this batch.
- **Rig health is fine.** Δv is 4.96–5.28 m/s, inputs 208–221 G, and
  pulse width 2.45–2.52 ms. The TP4 tables agree with the pipeline's
  CH5 raw peaks to 0.12 % median on valid captures (the fault-window
  outliers are described above).
- **Rebound (`e_rebound`) is not usable on corny7/corny8.** The hop
  detector sits at its 15 ms floor, or is multimodal, on all six
  sessions, because the knock ring outlasts the 15 ms search start.
  corny2's copies give 9.81 / 7.02 / 9.06 mJ per drop, against 9.22 mJ
  for its first article.

## Replicate study: interim scoring of plate 1 (`figures/15_replicate_interim.png`, `replicate_interim.json`)

The plan's endpoints are design means over nine articles across three
plates. Plate 1 gives three articles per design on one plate, so
everything below is interim. Three readings bracket the knock:

- **all valid drops:** the standing pipeline's numbers;
- **low-gauge:** only drops with gauge < 1.145;
- **adjusted:** every drop corrected to gauge 1.03 with the pooled
  slope. This is a model-based sensitivity check, not a measurement.

| T180 | corny7 | corny8 | corny2 | corny7 − corny8 |
|---|---|---|---|--:|
| first article | 0.803 | 0.954 | 1.085 | −0.150 |
| plate 1, all valid drops | 0.940 (0.938 / 0.972 / 0.910) | 0.974 (0.910 / 1.016 / 0.995) | 1.071 (1.063 / 1.072 / 1.077) | −0.034 |
| plate 1, low-gauge drops | 0.904 (`1sne73` only, 5 drops) | 0.933 (0.890 / 0.967 / 0.944) | 1.070 | −0.029 |
| plate 1, gauge-adjusted | 0.895 (0.906 / 0.882 / 0.898) | 0.927 (0.872 / 0.982 / 0.928) | 1.065 | −0.032 |
| held-out model (round-5 LOGO-CV) | 0.978 ± 0.085 | 0.972 ± 0.134 | 1.050 ± 0.071 | +0.006 |
| frozen round-4 model | 0.934 ± 0.131 | 0.954 ± 0.153 | 1.008 ± 0.147 | −0.020 |

Pre-registered endpoints, as far as plate 1 can take them:

1. **Article sd (E1).** Only corny2 has healthy seats: 0.0072 (df 2),
   or 0.0085 pooled with round 3's 0.0087 (df 10). That is under the
   0.015 line, which points to "one article per design is enough
   precision". But this evening's artifact rate was 6 of 9 sessions,
   against about 1 in 14 in round 3, so the plan's "repeats buy artifact
   protection" clause got a live demonstration.
2. **corny7 − corny8 gap (E2).** −0.029 to −0.034 under every reading,
   against −0.150 on the first articles. The plan scores ≥ 0.10 as
   "reproduces" and ≤ 0.05 as "collapses", so plate 1 points squarely
   at "collapses". **Do not act on the rule yet:**
   - all six corny7/corny8 sessions knock;
   - corny8's copies spread 0.11, which is seat noise.

   If plates 2 and 3, on healthy seats, look like this, the plan's
   collapse consequences apply:
   - 0.803 stops being quoted as corny7's design value;
   - the front is re-ranked on design means;
   - round 5 is regenerated with replicate-aware acquisition.
3. **corny8 rebound excess (E3).** Not scoreable (see above).
4. **Ordering (E4).** corny7 < corny8 < corny2 under all three
   readings. That matches the first-article and frozen round-4 orderings
   and puts corny2 last, as all three references do. corny7 vs corny8
   is not resolved: the 0.03 gap is smaller than corny8's
   copy-to-copy spread. Remember that a 3-design ordering has a 1/6
   chance baseline.
5. **Regression to the mean (E5).** Deferred until corny7/corny8 have
   healthy seats.

**What this means for corny7's record:**

- The plan's artifact rule says any article more than 3 article sd from
  its design median gets a re-seat and a 10–12 drop re-run before it may
  be excluded.
- On plate 1, the article that sits far from its design median is
  **corny7's first article itself**: 0.803 against copies at 0.90–0.94,
  about 11–16 article sd.
- The cleanest test is to re-drop that original article on a healthy
  seat, in the same session as its copies.

## Video (`figures/16_video_identity_montage.jpg`, `video_pairing.json`)

- **The camera clock is still reset** (sidecars read 2018-01-20). It
  runs a constant 3,192 d 9 h 56 m 08 s behind the DAQ, the same offset
  as the dran3 batch.
  - The MP4 headers' creation times match the sidecars one-to-one. The
    file counter jumps from C0068 to C0015/C0017/C0018 and back to
    C0069.
  - The one short clip (`1sne82-10`, 1,200 frames) is C0068.
- **Pairing:**
  - **20 of 27 clips land on their named drop** within ±1 s.
  - `1sne73-10` filmed drop 11.
  - `1sne83-1` filmed event 4, the first drop after the 1 h 44 min
    pause.
  - Five clips have no capture:
    - `1sne72-10` falls in the missing events 10–14;
    - `1sne72-20`, `1sne73-20` and `1sne82-20` were filmed 3, 25 and
      35 min after their session's last capture, with that session's
      label on the carriage;
    - `1sne83-20` was filmed 48 s after the last capture.
- **Identity:** the carriage label matches the clip name in all 27 rest
  frames. The specimen is upright and the sensor seated in every frame,
  including the seven clips paired to mistimed captures.

## Side by side with the first articles (`video/compare/`, `figures/video-compare/`)

Requested by @me-madsen on PR #86 (10-19): the slo-mo of the original corny
drops next to the same designs' plate-1 copies (corny7 with `1sne71`–`73`,
and so on), each drop matched as well as possible, with the acceleration
traces aligned to the video.

- **Outputs:**
  - `video/compare/corny2_vs_1sne2x.mp4`, `corny7_vs_1sne7x.mp4` and
    `corny8_vs_1sne8x.mp4` (5.6–5.9 MB each): one video per design.
    - Four columns: the first article, then copies 1–3. Filmed drops 1, 10
      and 20 play in sequence, 64× slower than real time.
    - Under each clip is its acceleration record: the CH5 base input, plus
      the top-vertex resultant at CFC-180 and CFC-1000. There is a full −35
      to +95 ms panel and a −3 to +8 ms zoom, each with a cursor that moves
      with the video.
  - `video/compare/corny7_vs_1sne7x_drop10_preview.gif`: a looping preview
    of corny7's drop-10 comparison.
  - `figures/video-compare/24_video_compare_corny2.jpg`, `25_…_corny7.jpg`
    and `26_…_corny8.jpg`: drop 10 as six synced frames per article, next
    to that article's trace.
  - `figures/video-compare/27_video_sync_check.png` and
    `video_comparison.json`: pairing, sync, scale and labels for every clip.
- **Script:** `scripts/analysis/drop_test_corny_1sne_video_comparison.py
  --mp4 DIR --daq DIR --ffmpeg PATH --procs 4` (18 min on a 4-core runner).
  - `--mp4` holds the nine `corny{2,7,8}-{1st,10th,20th}.MP4` clips (ids in
    `../corny-checkin/video/box-ids.json`) and the 27 `1sne*` clips
    (`video/box-ids.json`), about 17 GB.
  - `--daq` holds the captures of the 12 sessions, saved as
    `<session>_Signal<k>.csv` (ids in each `raw/<session>/box-ids.json`).
  - The series tables, `capture_census.json` and `video_pairing.json` are
    read from the branch.
- **How each drop is matched:**
  - *Same drop:* both batches filmed drops 1, 10 and 20. Clips pair to
    captures by MP4 header time at a constant camera offset per batch; the
    1sne pairing reproduces `video_pairing.json`.
  - *Same instant:* t = 0 is the CH5 CFC-180 peak in every panel.
    - CH5 rides on the carriage, so CH5 integrated twice is the carriage's
      own path through the impact. Fitting that path to the carriage tracked
      frame by frame syncs **23 of 36 clips** to a residual rms of
      **0.10–0.28 mm** over the 33 frames around impact (one frame =
      1.04 ms).
    - The other 13 clips have no usable capture. They are placed by their
      lowest carriage point, which trails the CH5 peak by 1.07 ms (sd
      0.13 ms across the 23 fits).
  - *Same picture:* every panel shows the same 140 × 210 mm window at the
    plate, with the plate at the same height at t = 0. The scale comes from
    the same fit: 4.10 / 3.59 / 2.94 px/mm on the three filming days (09-12,
    09-14, 10-17), which used three different camera set-ups.
  - *Same impact:* the fitted arrival speed is 4.62–4.82 m/s on the first
    articles and 4.60–4.88 m/s on the copies.
- **Which drops have their own record** (*italic* = stand-in, drawn dashed:
  the nearest usable drop of the same session):

  | design | first article (1 / 10 / 20) | copy 1 | copy 2 | copy 3 |
  |---|---|---|---|---|
  | corny2 | S1 / S10 / S20 | S1 / S10 / S20 | S1 / S10 (knock) / *S17* | *S5* / *S14* / S20 |
  | corny7 | S1 / S11 / *S20* | *S13* / *S13* / *S14* | *S5* / *S6* / *S6* | S1 / S11 (knock) / *S20* |
  | corny8 | S1 / S10 / S20 | S1 (knock) / S10 (knock) / S20 | S1 / S10 / *S20* | S4 (knock) / S10 / *S20* |

  - Seven filmed drops landed on captures with no impact (the 17:18–18:17
    CH5-fault hour). Six weren't captured at all: the missing `1sne72`
    events, and clips filmed after a session's last capture.
  - **corny7 is the thin spot:** none of the six clips from `1sne71` and
    `1sne72` has its own record. Three clips filmed a neighbouring drop:
    `corny7-10th` and `1sne73-10` filmed drop 11, and `1sne83-1` filmed
    drop 4.
- **What the side by side shows:**
  1. **The struts are a different colour.** All three first articles have
     white PLA struts. All nine copies have black struts, with a white band
     on one strut that looks like the ID sticker. This is the print-batch
     confound named in the follow-up below; on its own it explains nothing
     (dran3 showed no colour offset).
  2. **corny7 and corny8 fold and snap back, and the motion is the same on
     the originals and the copies.**
     - Within about 5–10 ms of impact, the top triangle sags and twists and
       the side cables go visibly slack (S-shaped).
     - The structure stays folded, then snaps upright 40–55 ms after impact.
       The feet stay on the plate, as far as the ~0.4 mm/px video can tell.
     - The snap-back lands on the top sensor's largest CFC-180 burst 25–70 ms
       after impact (`snap_burst_ms` in the json):

       | snap-back | first article | copy 1 | copy 2 | copy 3 |
       |---|--:|--:|--:|--:|
       | corny7 | 41.5–42.8 ms | ~53 ms ¹ | 51–54 ms ¹ | 39.7–41.6 ms |
       | corny8 | 39.3–40.8 ms | 39.0–43.0 ms | 48.1–49.6 ms | 50.3–53.6 ms |

       ¹ From stand-in drops. The films of the filmed drops agree: still
       folded at +42 ms, upright by about +55 ms.
     - **For corny7, nothing in the gross motion separates the 0.803 article
       from its copies.** corny7 and `1sne73` fold and re-erect on the same
       schedule (~41 ms), but their T180s differ (0.80 vs 0.91–0.92). The
       difference is in the impact pulse itself, which 1 ms frames can't
       resolve. The traces show it: corny7's top-vertex peak sits clearly
       under CH5's, while `1sne73`'s matches it. What does vary between
       copies is how long they stay folded (about 40 vs about 50 ms), and
       that doesn't line up with first article vs copy.
  3. **On this family the secondary burst is the cables re-tensioning, not a
     hop landing.** Keep that in mind when reading `t_second` / `e_rebound`.
     The snap-back burst is also measurable on the knocking copies, where
     the hop detector sits at its 15 ms floor (`1sne71`, `72`, `81`, `83`),
     and on corny8's original, where it sits at its 70 ms cap.
  4. **corny2 doesn't fold.** The tall design stays upright with taut cables
     on all four articles.
  5. **The seat knock isn't visible.** It lasts ~0.1 ms, far shorter than
     one frame.
- **Standing checks:** the T-drift watch flags none of the 12 sessions
  (`1sne71`/`1sne72` have too few valid drops to fit a slope), and every
  trace drawn holds a screened impact (`valid` or `knock` class).

## What this batch needs from the lab

1. **Fix the CH5 chain before plates 2–3 are dropped.**
   - Reseat or replace the CH5 cable and both connectors (the sensor
     end and the TP4 end), and give it strain relief clear of the
     carriage.
   - **Live check, from the TP4 series table after the first drops of
     every session:** CH4's peak should be ≥ 150 G. All 56 mistimed
     captures read ≤ 15 G, and every valid one ≥ 230 G. CH5 should show
     a ~3–4 ms duration and Δv ≈ 205–225 in/s.
2. **Check the seat before each session.**
   - In the same table, a CH4 peak above 2× CH5's flags a knocking
     seat. On this batch that rule caught 63 of the 72 gauge-flagged
     drops, with 3 false alarms in 50.
   - Across the 29 earlier check-in sessions it fired mostly on the
     known gross seat artifacts (`2dran1`, `dran35`). It also fired on
     ≤ 25 % of drops in three sessions whose gauges stayed healthy.
   - So if most of the first three drops trip it, re-seat (fresh wax,
     sensor flush, cable not pulling) before continuing.
3. **Re-run the six corny7/corny8 copies on a healthy seat**, 10–12
   drops each. Per the artifact rule, include the original **corny7**
   (and corny8) article in the same session, interleaved with the
   copies. That one session settles whether 0.803 was the article or
   the seat.
4. **Plates 2 and 3: follow the plan's drop protocol.**
   - Interleave designs within each block.
   - Bracket each block with one reference article (bpx68c or a
     designated corny7 copy).
   - Record 22 captures per article. This batch ran all copies of each
     design back to back with 20 captures, which is why the fault hour
     and the knock each landed on whole designs.
5. Two questions:
   - What changed between 18:17 and 18:23, when the fault cleared?
   - Were `1sne72` events 10–14 deleted or lost?

   Optionally, reset the camera clock.

## BO hand-off (PR #102)

`figures/campaign_summary.csv` holds one row per article with the
standing columns. **Only the corny2 rows are design-grade.** The six
corny7/corny8 rows carry knocking-seat values (gauge 1.16–2.01; the CSV
has t1000 and t180 to recompute it). They must not enter the surrogate
as replicates of t37/t39 until they are re-run, and nothing here
replaces the first-article values in the round-5 fit yet. When plates
2–3 land, score the study from the screened design means, per the plan.

## Follow-up (10-19): the CH5 cable timeline and the article spread

Written after @me-madsen reported that the CH5 cable has since broken. The
full write-up is [`ch5-fault-and-replicates.md`](ch5-fault-and-replicates.md),
with figures and `ch5_replicates.json` in
[`figures/ch5-replicates/`](figures/ch5-replicates/).

- **The fault was intermittent, not a disconnection.** CH5 was healthy for
  the first 30 captures and for all 80 after 18:23. In the hour between, 14
  of 70 captures still held their impact. The bad triggers fired during the
  fall, 0.33 ± 0.10 s before impact on average, and three fired between
  drops.
- **The print files are identical** for the first articles and the plate-1
  copies: 556/556 slicer keys, including PLA 226 °C and TPU 236 °C nozzle
  temperatures. The undocumented difference is the strut PLA: **white on
  the first articles, black on every plate-1 copy** (the switch came between
  the corny and dran3 prints).
- **Article spread:** corny2's copies agree to SD 0.0072. The corny7 and
  corny8 copies' scatter is mostly the knocking seat. corny7's first article
  (0.803) remains the outlier against its cleanest copy (0.904).

## Follow-up (10-19): why the copies weigh more

Written after @me-madsen asked why every copy is 0.5–0.8 g heavier than
its first article, and whether black and white PLA differ. The full
write-up is [`print-mass-and-pla-colour.md`](print-mass-and-pla-colour.md),
with inputs in [`print-mass/`](print-mass/) and the figure in
[`figures/print-mass/`](figures/print-mass/).

- **The print models are identical.** Meshes, transforms, infill and all
  556 settings match, and the lab's Bambu Studio slices both projects to
  the same PLA and TPU per article (within 0.03 %).
- **The extra mass is a print-batch effect in the strut PLA.** Per
  commanded cm³, the four black batches put 3.8 % more PLA on the scale
  than the four white ones (1.196–1.221 vs 1.151–1.167 g/cm³). On round 3,
  the same nine designs reprinted white → white changed only the TPU;
  white → black changed the PLA. Of each copy's gain, 70–80 % is PLA.
- **Not density.** Nothing per colour is measured anywhere, and pigment
  would make white the denser one. The likely carrier is the spool's grams
  per metre (diameter tolerance ±0.03 mm) or the printing-time preset:
  weigh 1 m of each spool.
- **Shock:** the black round-3 reprint sits −0.003 in T from the white
  first print. corny7 and corny8 gained the same mass from the same
  material split, so the colour switch does not explain corny7.
