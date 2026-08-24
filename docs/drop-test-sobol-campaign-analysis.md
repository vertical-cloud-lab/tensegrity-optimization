# SOBOL + S0 campaign — first batch analysis (8/9 specimens)

**Data:** 10 Box uploads posted by @me-madsen on PR #86 (08-21) — 8 specimens
plus 2 partial/interrupted sessions, 942 captures ≈ 8.4 GB, recorded
08-13 → 08-20 under the standing SOP (60 in drop, arrangement B = 1/2 in PU
mat, 150 G trigger on CH5, 100 ms / 1.25 MHz / 2 ms pre-trigger, 101
drops/specimen).
**Script:** [`scripts/analysis/drop_test_campaign_analysis.py`](../scripts/analysis/drop_test_campaign_analysis.py)
(fetch: [`scripts/fetch_box_shared_folder.py`](../scripts/fetch_box_shared_folder.py));
outputs in [`data/drop-tests/sobol-campaign/figures/`](../data/drop-tests/sobol-campaign/figures/)
including the BO ingest file `campaign_summary.csv`.
**Design parameters:** joined from the print key recovered from the issue-#98
`.3mf` (`bo/t3-prism-bo-batch-print-key.csv` on branch
`claude/issue-98-20260821-0103`), committed here as
[`params.json`](../data/drop-tests/sobol-campaign/params.json).

## 0. TL;DR

1. **The campaign discriminates.** T = TOP/CH5 (CFC-180) spans
   **0.893 → 1.062 (16.8 %)** across the 8 specimens with within-specimen CV
   0.17–0.48 % — every adjacent pair in the ranking separates at |d| ≥ 2.8.
   **`6lhxfy` (Sobol spec 01) is the first strong attenuator ever measured
   under this SOP (T = 0.893)**, reproduced across two sessions on different
   days to 0.13 %.
2. **A processing fix was required first** (§2): the carriage now arrives
   fast enough that mat contact starts > 2 ms before the 150 G trigger, so
   the 2 ms pre-trigger window rides a +10–20 G contact foot and is no longer
   a valid baseline. Without the fix, Δv reads catastrophically low and — more
   importantly — **T carries a specimen-dependent bias of up to ~5 %**, which
   would have scrambled the BO objective. The fixed pipeline re-baselines on
   the record tail and was validated against the TP4 series tables'
   independent per-event Δv and raw peaks (agreement 1–3 %).
3. **The tower is healthy.** On the corrected (and TP4-corroborated) scale,
   input Δv was 5.03–5.45 m/s all week — at or near the healthy-tower bar —
   and it *improved* through the week (§3). The standing "tower still at
   ~87 % of free-fall" narrative from the 08-10/08-12 sessions was largely
   the same baseline artifact and is corrected below.
4. **For the BO hand-off** (§5): `campaign_summary.csv` has one row per
   specimen with objectives ± sd and design parameters. Two blockers on the
   metadata side: **`amdjwm` (2nd-best specimen, T = 0.980) appears in no
   print key anywhere** — its design parameters are unknown — and the
   `ebdna8` session seen on the TP4 status bar on 08-18 has not been
   uploaded.

## 1. Sessions

| specimen | Sobol spec | session (start) | captures | notes |
|---|---|---|--:|---|
| `bag26v` | 08 | 08-13 13:56 | 101/101 | earliest; 5 days before the rest; pre-settings-reset |
| `amdjwm-s1` | **unknown** | 08-17 11:33 | 87/87 | interrupted first attempt |
| `amdjwm` | **unknown** | 08-17 13:57 | 101/101 | full re-run, same day |
| `bpx68c` | S0 (ref) | 08-17 15:19 | 101/101 | = the calibration-check "before" set |
| `autv5r` | 02 | 08-19 15:34 | 103/103 | 2 extra captures (S103/104) after end-of-session pauses — normal drops, kept |
| `6lhxfy-s1` | 01 | 08-19 17:09 | 35/35 | interrupted first attempt |
| `6lhxfy` | 01 | 08-20 13:15 | 101/101 | full re-run next day |
| `9hhbkp` | 00 | 08-20 14:34 | 101/101 | |
| `nvxsrv` | 04 | 08-20 16:13 | 101/101 | one 13 min pause after drop 44 |
| `6nheas` | 05 | 08-20 18:02 | 101/101 | ends 08-21 01:24 UTC |

942/942 captures are clean real drops — **zero invalid/spurious triggers in
the entire batch**, no channel above 4.7 % of full scale, median cadence
~41–45 s. The 08-13/08-17 sessions predate the 08-18 TP4 settings reset; the
calibration check already verified continuity across it.

## 2. The pre-trigger contact foot, and why the pipeline needed a fix

The abc123-era convention baselines every channel on the median of the 2 ms
pre-trigger window. That was valid when it was written. In this batch the
pre-trigger is **not quiet**: CH5 sits +10 to +20 G above the record tail for
the full 2 ms before the trigger (bag26v, the slowest session: +2 G;
08-19/20 sessions: +16 to +20 G). At 5.4 m/s the carriage crosses the mat's
12.7 mm thickness in ~2.3 ms, so early mat compression is already underway
more than 2 ms before the 150 G crossing — the entire pre-trigger window
rides the contact foot.

Consequences of baselining on the foot:

- **Δv collapses.** The 15 ms Δv integral picks up the (−foot) offset over
  its whole window: sessions read 2.0–3.5 m/s instead of ~5.3 m/s, and the
  bias *grows within a session* as the mat warms and the foot lengthens —
  manufacturing an apparent "velocity decay" that is not real.
- **T is biased per-specimen.** Peaks are measured relative to the wrong
  zero, and the foot differs between CH5 and the top-vertex channels (they
  see it through different paths), so T shifted by up to ~5 % in a
  specimen-dependent way (e.g. `nvxsrv` 1.074 → 1.024 after the fix,
  `autv5r` 1.077 → 1.041, while `bpx68c` barely moved 1.011 → 1.011).

**The fix** (committed): `analyze_capture` gains a `baseline="tail"` mode —
each channel is re-zeroed on its median over the final 30 ms of the 100 ms
record — and the campaign pipeline uses it for all sessions. The
default `"pretrigger"` mode is untouched, so every previously committed
analysis reproduces unchanged. Validation against the TP4's own series
tables (computed independently by the DAQ from raw data): per-event CH5 raw
peaks agree to 1–2 %, per-event Δv to 2–3 %, across all 10 sessions. On
clean-pretrigger sessions the two baselines coincide, so the corrected scale
remains comparable to the healthy-tower references.

**Correction to the standing record.** The same artifact was already
present, smaller, in the 08-10/08-12 rail-maintenance sessions (their TP4
series tables read 0.3–0.4 m/s higher than the committed pipeline values,
with the gap growing across the week). Two standing conclusions soften:
the "settled at 4.55–4.66 m/s ≈ 87 % of free-fall" plateau was an
underestimate (TP4 scale: 4.9–5.0 m/s and still rising), and the within-
session "mat-rebound decay" in Δv was partly the foot growing rather than
physics. Correction notes have been added to the speed-decay and
pre/post-grease docs. The qualitative conclusions (greasing produced a real
step; no cumulative decay over 100 drops) survive.

## 3. Rig health: the tower quietly finished recovering

Input Δv (corrected pipeline, corroborated by TP4) by session:

| date | session(s) | Δv (m/s) | % of 5.47 free-fall |
|---|---|--:|--:|
| 08-10 | pre/post-grease | 4.6 (TP4) | 84 % |
| 08-11 / 08-12 | speed-decay | 4.9 / 5.0 (TP4) | 90–91 % |
| 08-13 | `bag26v` | 5.03 (rising within session) | 92 % |
| 08-17 | `amdjwm-s1` / `amdjwm` / `bpx68c` | 5.01 / 5.26 / 5.30 | 92–97 % |
| 08-19 | `autv5r` / `6lhxfy-s1` | 5.34 / 5.51 | 98–101 %* |
| 08-20 | `6lhxfy` / `9hhbkp` / `nvxsrv` / `6nheas` | 5.37 / 5.45 / 5.33 / 5.26 | 96–100 %* |

\* Δv is the full-pulse integral = arrival + rebound speed, so it can
slightly exceed the free-fall *arrival* figure; values at ~100 % imply
arrival within a few percent of free fall with a small mat rebound.

The greasing recovery did not stall at the 08-12 "settled" level — it kept
improving with traffic, and by campaign week the tower was effectively at
the healthy-tower bar (abc123 healthy reference 5.28–5.35 m/s). Every
campaign session lands in a ±4 % Δv band, so impact severity is matched
across specimens to about the same tolerance as the input peak (in180
203–232 G, partly specimen-mass-dependent).

## 4. Campaign results

### 4.1 Ranking (stabilized drops, warm-up 2 discarded)

| rank | specimen | spec | T180 (CV) | T1000 | e_rebound | t_second | fn / ζ (usable frac) |
|--:|---|---|--:|--:|--:|--:|---|
| 1 | `6lhxfy` | 01 | **0.8931 (0.47 %)** | 0.913 | 0.0504 | 55.2 ms | 368 Hz / 10.2 % (0.64) |
| 2 | `amdjwm` | ? | **0.9805 (0.26 %)** | 1.007 | 0.030† | 31.8 ms† | 455 Hz / 9.6 % (0.05) |
| 3 | `6nheas` | 05 | **0.9970 (0.32 %)** | 0.996 | 0.0402 | 43.2 ms | 322 Hz / 19.3 % (1.00) |
| 4 | `bpx68c` | S0 | 1.0111 (0.23 %) | 1.067 | 0.0204 | 22.1 ms | 468 Hz / 16.7 % (0.01) |
| 5 | `9hhbkp` | 00 | 1.0183 (0.17 %) | 1.028 | 0.0215 | 23.9 ms | 364 Hz / 11.2 % (0.58) |
| 6 | `nvxsrv` | 04 | 1.0275 (0.43 %) | 1.230 | 0.0266 | 28.9 ms | 294 Hz / 31.0 % (0.88) |
| 7 | `autv5r` | 02 | 1.0404 (0.34 %) | 1.136 | 0.0268 | 29.2 ms | 386 Hz / 6.4 % (0.39) |
| 8 | `bag26v` | 08 | 1.0616 (0.48 %) | 1.242 | 0.0241 | 24.7 ms | — (0.00) |

† `amdjwm`'s secondary-event detector is bimodal (CV ~49 %) — its hop lands
near a ringdown lobe and the picker alternates between two candidates; its
t_second/e_rebound are not reliable this session. All other specimens have
e_rebound CV ≤ 4.3 %.

ANOVA on T180: F ≈ 2.4 × 10³, p ≈ 0 across 8 specimens; spread 16.8 % with
median within-specimen CV 0.33 %. Adjacent-pair gaps and effect sizes
(Welch): 6lhxfy→amdjwm 9.8 % (|d| = 25), amdjwm→6nheas 1.7 % (5.7),
6nheas→bpx68c 1.4 % (5.0), bpx68c→9hhbkp 0.7 % (3.5), 9hhbkp→nvxsrv 0.9 %
(2.8), nvxsrv→autv5r 1.2 % (3.3), autv5r→bag26v 2.0 % (4.8). Figures:
[series](../data/drop-tests/sobol-campaign/figures/01_campaign_series.png) ·
[ranking](../data/drop-tests/sobol-campaign/figures/02_campaign_ranking.png).

**Honest tiering against the known noise floors** (print-to-print ≈ 2 %
spread in T; cross-session mount re-seat ≤ ~2 %): the ranking resolves into
four design-level tiers — **`6lhxfy` alone** (9.8 % clear of everything),
**`amdjwm`/`6nheas`** (attenuating-to-neutral), **the near-unity middle**
(`bpx68c`/`9hhbkp`/`nvxsrv`, spanning 1.6 % — *not* mutually resolved at the
print level), and **the amplifiers** (`autv5r`, `bag26v`). Within-tier order
is statistically real for *these articles* but should not be read as a
design difference.

### 4.2 The headline: `6lhxfy` (spec 01)

T = 0.893 — an 11 % peak reduction relative to the base input, where every
previously measured specimen sat within a few % of 1.0 (best ever before:
`yqpmx1` ≈ 0.96 at 13 in on the retired hot-glue mount). Its design corner:
**thickest struts (9.24 mm), thinnest cables (2.55 mm), highest twist
(77.4°), lightest mass (18.50 g)** — the compliant-cable/stiff-strut corner
of the Sobol box. It is also the biggest hopper (e_rebound 0.050, hop
landing at ~55 ms) and holds T1000 = 0.913, i.e. it attenuates broadband,
not just in the CFC-180 band. The BO prior should treat this corner as the
live region.

### 4.3 Session-to-session repeatability — the free crossover checks

The two interrupted sessions are independent re-runs (fresh mount seating,
different day for `6lhxfy`):

| specimen | session 1 | session 2 | ΔT180 |
|---|--:|--:|--:|
| `6lhxfy` | 0.8943 (35 drops, 08-19) | 0.8931 (101 drops, 08-20) | **0.13 %** |
| `amdjwm` | 0.9862 (87 drops, 08-17 am) | 0.9805 (101 drops, 08-17 pm) | 0.58 % |

Both land well inside the ~2 % re-seat envelope — T180 is transferring
across sessions far better than the historical worst cases. **T1000 does
not transfer** (`amdjwm` 1.159 → 1.007; `6lhxfy` 1.029 → 0.913): the
broadband ratio is dominated by mount-coupling HF content, confirming the
long-standing choice of CFC-180 T as the primary objective and T1000 as a
secondary/diagnostic only. (`autv5r` also drifts +15 % in T1000 *within*
its session while T180 stays flat — same lesson.)

### 4.4 Drift, ringdown, secondary metrics

- **T180 drift within sessions is negligible**: |slope| ≤ 0.016 %/drop
  (most ≤ 0.008 %), the two largest with the usual first-drops mat
  transient. 101 drops per specimen buys a ±0.05 % standard error on T —
  100× tighter than the print-to-print floor; 5–10 recorded drops would
  give the same design information (the standing sample-size result).
- **e_rebound** spans 0.020–0.050 (2.5×) and correlates with attenuation
  (the two best T specimens hop hardest — consistent with energy leaving
  through the compliant-cable path rather than transmitting). It remains
  the sharpest per-drop discriminator (CV ≤ 2 % for most specimens).
- **Ringdown fits** are usable for 5 of 8 specimens (fn 294–468 Hz,
  ζ 6–31 %). `bag26v` (0 % usable, the tallest article at H = 105 mm) and
  `bpx68c`/`amdjwm` (≤ 5 %) fail the r² gate — their post-impact envelope
  is not a single decaying mode. Treat fn/ζ as opportunistic secondary
  outputs, not campaign objectives.
- **Mat state**: CH5 raw stayed ≤ 4.7 % of full scale everywhere; the PU
  mat needed no attention across 942 drops.

## 5. BO hand-off

[`figures/campaign_summary.csv`](../data/drop-tests/sobol-campaign/figures/campaign_summary.csv)
carries one row per specimen: `t180`, `t1000`, `out_180_g`, `in_180_g`,
`in_dv_ms`, `t_second_ms`, `e_rebound`, `fn_hz`, `zeta_pct` (mean ± sd
each), Δv health verdict, and the design parameters (R, H, twist, strut Ø,
cable Ø, mass, spec index) joined from `params.json`. Recommended objective
column: `t180_mean` (with `t180_sd`); `e_rebound_mean` as a secondary
objective if the BO goes multi-output.

**Open items blocking a complete design table:**

1. **`amdjwm` maps to no known print.** It is absent from the `.3mf` print
   key, the Sobol design table, and every issue/PR in the repo. Its
   parameters are blank in the CSV. @me-madsen — which spec is it (a
   re-print of 03/06/07? a re-label?), and can its mass be added?
2. **`ebdna8` (spec 03)**: the 08-18 TP4 settings screenshot showed the
   database sitting on a completed session `ebdna8 - 60 in - 1/2" mat -
   101 drops`, but no `ebdna8` upload exists. If that session is real,
   uploading it may complete a 9th specimen for free.
3. The 9th specimen (tested "tomorrow morning" per the posting comment) and
   the slow-motion videos are pending; the pipeline is one command to
   re-run when they land.
4. Spec 08's official article: the print key flags `dea4ls` (per the .3mf)
   vs `bag26v` (per the issue comment) — `bag26v` is what was tested here.

## 6. Caveats

- **n = 1 article per design** (except the two double-session specimens,
  which replicate *sessions*, not prints). The print-defect study put
  print-to-print scatter at ~2 % in T — that is the design-resolution
  floor for this table, and why the middle tier is unresolved.
- `bag26v` ran 5 days before the rest on a slightly slower tower
  (Δv 5.03 vs 5.26–5.45); T is severity-robust, but its last-place margin
  (2.0 % below `autv5r`) is larger than any plausible session effect.
- The Δv health bands in the script were derived on the pre-trigger
  baseline; they remain valid on the corrected scale because the two
  estimators coincide on clean-pretrigger (healthy-era) data, but
  sub-0.1 m/s comparisons across the estimator change should not be made.
- `amdjwm`'s t_second/e_rebound are unreliable this session (§4.1 †).
- The 2 ms pre-trigger is now structurally too short for a quiet baseline
  at healthy-tower speeds. The tail baseline handles it in analysis, but if
  the TP4 allows a longer pre-trigger (e.g. 5 ms = 5 %), the foot would be
  fully in-record and the estimator debate disappears at the capture level.

## 7. Addendum (2026-08-21): why the printed masses vary despite the constant-mass constraint

@sgbaird flagged that the measured masses (18.50–22.04 g, CV 5.9 %) vary
more than expected given the batch generator's constant-mass constraint
(PR #35, `bo/t3_prism_sobol_batch.py`).

**The constraint was implemented and converged.** Route A projects every
Sobol design onto the constant-mass manifold by uniform re-scaling, with
m\* = 30.95 g defined as the *solid-volume* mass of the S0 reference STLs
(ρ_PLA = 1.24, ρ_TPU = 1.21 g/cm³). The committed
`bo/t3-prism-bo-batch.csv` shows all 9 designs at 30.90–30.97 g predicted
(`mass_ok=True`, tolerance ±0.15 g).

**The gap is solid volume vs printed mass.** The slicer prints the PLA
struts/joints/housings with walls + sparse infill but the thin TPU cables
essentially solid. Regressing the 7 measured masses on the CSV's predicted
per-material solid masses (S0's split, 23.42 g PLA + 7.53 g TPU, computed
from the committed reference STLs):

```
measured ≈ 0.565 · m_PLA,solid + 0.986 · m_TPU,solid   (R² = 0.78, resid sd 0.64 g)
```

PLA prints at ~57 % of solid, TPU at ~99 %. Because the constant-mass
projection preserves shape ratios, the PLA/TPU split varies strongly by
design (TPU fraction 12–36 %), so each gram of solid mass the design moves
from PLA to TPU adds ~0.42 g of printed mass. That deterministically maps
the constant-solid-mass batch onto an ~±9 % printed-mass spread — e.g.
`6lhxfy` (spec 01, TPU fraction 0.118) is the lightest at 18.50 g while the
TPU-rich `9hhbkp`/`6nheas` (0.35–0.36) sit at 21.6–21.7 g. The ±0.3–0.8 g
residuals are true print-to-print variance (~3 %), consistent with the
print-defect study.

**Fix for future batches** (in `bo/t3_prism_sobol_batch.py` on PR #35):
either weight the scale solve's per-material volumes by effective print
densities (0.565 / 0.986 as fitted — one-line change, but profile-dependent),
or iterate the solve on the BambuStudio CLI's sliced per-filament grams,
which is exact for the active print profile. Which is "right" depends on
what the constraint is for: if the BO comparison is per-gram-of-printed-
structure, printed mass is the physical quantity to hold constant.

**Side effect worth using:** the fit predicts printed masses for the
untested specs — 03 (`ebdna8`) ≈ 20.4 g, 06 ≈ 19.2 g, 07 ≈ 21.5 g. Weighing
`amdjwm` (§5 open item 1) against these would help disambiguate which spec
it is (a ~19 g reading points at 06, ~21.5 g at 07).
