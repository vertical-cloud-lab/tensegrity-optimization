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
**The corny → design key is resolved (2026-09-15; § Design key below):
the nine articles are the round-4 BO-proposed designs — trials 37–45
of the BO branch's `bo/t3-prism-bo-suggestions-round4.csv`, printed as
one plate from `bo/slices/t3-prism-bo-round4.H2D-MM-PLAstruts-
TPUcables.3mf` @ `9fba359` (PR #102) — labeled by build-plate
position.** None of them is a drran/2dran article (those are the
round-3 print, trials 28–36, per the BO branch's
`bo/t3-prism-bo-round3-print-key.csv`), which is exactly what the
fingerprint comparison below concluded from the T data alone.

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

## Design key (resolved 2026-09-15)

@me-madsen identified the batch (PR #86, 09-15): the articles are the
round-4 print job, and the `corny1`–`corny9` labels were assigned by
**build-plate position**, with an annotated copy of the committed
plate render (`bo/t3-prism-bo-round4-plate.png` on the BO branch)
fixing the orientation. On that render (+x right, +y — the plate back
in the Bambu frame — up, wipe tower at right) the labels run
**column-major from the top-right**: right column top→bottom =
corny1/2/3, middle = corny4/5/6, left = corny7/8/9 — i.e. the plate
viewed rotated 90° CCW gives me-madsen's "1–9 row-major from
top-left".

| label | trial | plate cell | R×H print (mm) | strut/cable Ø (mm) | twist | infill s/c % | mass g meas (est) | pred T180 | meas T180 |
|---|---|---|---|---|---|---|---|---|---|
| `corny1` | t42 | back-right | 17.7 × 77.7 | 8.47 / 3.88 | 40° | 19/34 | 20.20 (20.41) | 1.010 ± 0.148 | 1.046 |
| `corny2` | t38 | middle-right | 18.3 × 80.3 | 7.98 / 4.02 | 40° | 18/34 | 20.21 (20.52) | 1.008 ± 0.147 | 1.085 |
| `corny3` | t45 | front-right | 19.7 × 86.5 | 6.89 / 4.32 | 40° | 12/35 | 20.15 (20.64) | 1.004 ± 0.149 | 1.071 |
| `corny4` | t44 | back-center | 20.8 × 91.5 | 4.99 / 4.58 | 40° | 19/21 | 20.56 (20.46) | 1.013 ± 0.140 | 1.048 |
| `corny5` | t40 | middle-center | 20.8 × 91.6 | 5.00 / 4.58 | 40° | 18/21 | 20.58 (20.45) | 1.012 ± 0.140 | 1.088* |
| `corny6` | t41 | front-center | 33.4 × 67.3 | 8.65 / 2.51 | 80° | 29/18 | 19.45 (19.93) | 0.943 ± 0.134 | 0.911 |
| `corny7` | t37 | back-left | 34.3 × 67.1 | 8.98 / 2.58 | 79° | 22/21 | 19.62 (19.92) | **0.934 ± 0.131 (best predicted)** | **0.803** |
| `corny8` | t39 | middle-left | 34.7 × 68.3 | 8.86 / 2.60 | 80° | 21/34 | 19.64 (19.95) | 0.954 ± 0.153 | 0.954 |
| `corny9` | t43 | front-left | 37.1 × 65.5 | 9.25 / 2.78 | 80° | 12/29 | 19.46 (19.97) | 0.941 ± 0.146 | 0.877 |

\* drift-contaminated mean; late-session ≈ 1.07 (anomaly 1 below).

Machine-readable: `params.json` in this folder, joined into
`figures/campaign_summary.csv` and the `design_params` slots of
`figures/campaign_metrics.json` (the same join
`drop_test_campaign_analysis.py --params` performs on a re-run).
Masses + defects from @ctrhjk's round-4 print log (issue #98, 09-11).

**Provenance + validation** — four legs, three independent of the
annotation:

1. **The annotated render** (primary): me-madsen drew the 1–9 labels
   directly onto the round-4 plate render, so each label points at a
   specific trial's rendered geometry — no grid-orientation guessing
   left.
2. **Orientation is forced by the T data alone.** The four
   attenuator-corner designs (t37/t39/t41/t43: R = 40 class, twist
   79–80°, thick struts, 3.0 mm cables — the `6lhxfy` corner) occupy
   the render's left column + bottom-middle. Of the 8 possible grid
   orientations (4 rotations × mirror), only the annotated one puts
   the four measured attenuating labels {6,7,8,9} on those four
   cells.
3. **Print-log photos give a calibrated within-family test.** The
   sticker labels are the same tape on every article (equal axial
   extent across the corny3/4/5 photos ⇒ equal pixel scale):
   `corny3`'s strut measures ≈ 1.35× `corny4`/`corny5`'s — matching
   t45 (6.89 mm) against the t44/t40 clones (5.0 mm; predicted ratio
   1.38) — and `corny4` ≈ `corny5` as the clone pair. `corny1`/
   `corny2` are visibly the fat-strut tall pair (t42/t38). This is
   the check that discriminates the two candidate keys that were in
   circulation (warning below).
4. **Masses split the families with no crossings**: the four
   attenuator-corner articles weigh 19.45–19.64 g (est 19.92–19.97),
   the five tall articles 20.15–20.58 g (est 20.41–20.64) — one
   consistent session offset, −0.31 ± 0.13 g. (Within a family the
   predicted spread ≤ 0.23 g sits below the mass model's 0.38 g
   residual, so masses cannot discriminate there.)

Bonus consistency: under this key the frozen round-4 predictions rank
the attenuator family **perfectly** — predicted t37 < t43 < t41 < t39
↔ measured `corny7` (0.803) < `corny9` (0.877) < `corny6` (0.911) <
`corny8` (0.954), Spearman ρ = +1.0 (ρ = 0.82 across all nine; the
five amplifier predictions span only 0.9 %, ~sd/15, so their order
carries no information). And the `corny8` 764 Hz ringdown outlier
lands on t39, the attenuator printed at the batch-max 34 % TPU-cable
infill — the stiffest thin cables of the four.

**Caveats.** (a) The `corny4` ↔ `corny5` split rests on the
annotation alone: t44/t40 are deliberate near-clones (geometry
identical to 0.1 %, strut infill 19 vs 18 %) — untestable by photo,
mass or T, and immaterial at that level, but recorded for the BO's
infill axis. (b) Within the attenuator family the photos add no
independent leg (strut Øs within 7 %, camera elevations differ); that
half rests on legs 1–2 and the prediction ranking. (c) Assumes the
plate printed as committed (identity build-item transforms @
`9fba359`) and that labels were applied before articles left the
plate — @ctrhjk printed, labeled and photographed, so a one-line
confirm closes this; a 30-second caliper check would too (width
across feet: `corny9` ≈ 84 mm vs `corny6` ≈ 75 mm predicted).

**⚠️ Cross-thread key mismatch (PR #102).** The concurrent round-4 BO
ingestion (branch `claude/issue-98-20260821-0103` @ `c3aa44f`, run
34916710422) had to guess the numbering before this key existed and
guessed family-grouped: its `bo/t3-prism-bo-round4-print-key.csv`
agrees on the family split and on `corny1`/`corny2` but **differs on
the other 7 rows** (corny3=t44, corny4=t40, corny5=t45, corny6=t37,
corny7=t39, corny8=t43, corny9=t41). The photo measurement (leg 3)
directly contradicts it — it needs `corny5`, not `corny3`, to be the
6.9 mm-strut t45 — and under it the within-attenuator
predicted↔measured ranking inverts (ρ = −0.8). Consequence there: the
0.803 record is credited to t39 instead of the best-predicted t37,
and the round-5 refit/suggestions generated in that run inherit the
scrambled parameter→outcome pairing within both families. The 7 rows
need correcting and round 5 regenerating before anything prints.

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
   *(Key: `corny8` = t39, the attenuator printed at the batch-max
   34 % TPU-cable infill — the stiffest thin-cable article of the
   four — so a plausibly real modal difference, not seat state.)*
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
  *(Post-key: confirmed and strengthened — all nine are new articles,
  the round-4 designs t37–t45; the fingerprint read was exactly
  right.)*
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
  *(Key verdict: `corny1` = t42, a new round-4 article — the
  ex-`drran7` lineage is closed, and the gauge-1.24 reading is t42's
  own seating. The 2dran1 prediction still awaits a 2dran re-seat.)*
- Full numbers: `figures/batch_comparison.json`.

## What this batch needs from the lab

1. ~~The key, more urgent than ever~~ **Resolved 09-15** (§ Design
   key): trials 37–45, none of them drran/2dran articles — and the
   campaign has indeed found its first genuine attenuator family, led
   by the best-predicted design. Remaining actions: correct the 7
   mismatched rows in the BO branch's
   `bo/t3-prism-bo-round4-print-key.csv` and regenerate round 5
   before printing; optional close-outs per the § Design key caveats
   (@ctrhjk one-line labeling confirm; calipers on `corny9` vs
   `corny6`).
2. **Re-seat confirmations** per the standing rule, in priority order:
   `corny7` (the record — 20 drops after an independent mount re-seat
   settles it), `corny9`, then re-seat + re-run for the two unstable
   sessions (`corny5` flagged, `corny6` erratic) and the two gauge
   suspects (`corny1`, `corny3`).
3. Camera SOP tweak: start each clip *before* the target drop — five
   of this batch's 27 clips ran one drop late (item in the video note
   above).
