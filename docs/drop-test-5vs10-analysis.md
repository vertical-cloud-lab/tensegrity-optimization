# 5 in vs 10 in drop-height comparison — 500 G trigger validation and a BO height recommendation

Analysis of the 60 drops posted by @ctrhjk on
[PR #82](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/82):
CH5 trigger lowered from 1000 G to **500 G**, then 30 auto-drops at **5 in**
(`5vs10_Signal1–30`) and 30 at **10 in** (`5vs10_Signal31–60`), same rig and
channel map as the 200-drop campaign. Data:
`data/drop-tests/5vs10/`; script:
`scripts/analysis/drop_test_5vs10_analysis.py`; machine-readable metrics:
`data/drop-tests/5vs10/figures/5vs10_metrics.json`.

## 1. The 500 G trigger fix works — 60/60 drops captured

| | 5 in | 10 in |
|---|--:|--:|
| triggered / real impacts | **30/30** | **30/30** |
| CH5 raw \|peak\| | 2,195 ± 118 G (1,936–2,454) | 5,807 ± 164 G (5,336–6,079) |
| worst margin over 500 G | **3.87×** | 10.67× |
| worst pre-impact CH5 activity | 18.6 G (27× below level) | 8.1 G (62× below level) |
| first 500 G crossing | 3.896 ± 0.000 ms | 3.895 ± 0.003 ms |

The earlier 5-in failure mode is gone: every 5-in drop clears the 500 G
level by ≥3.9×, while the level still sits 27× above the worst pre-impact
activity, so there is no false-trigger risk. Trigger timing is essentially
deterministic (sub-3 µs jitter at 5 in).

Notably, this session's 5-in raw peaks (min 1,936 G) would have cleared even
the **old 1000 G level** — unlike the `7xadt6` practice drops that started
this investigation. That confirms the no-trigger episode was a
setup/coupling-state effect, not a fixed property of 5-in drops, and is
exactly why the level should stay at 500 G: it buys the margin that absorbs
session-to-session coupling variability.

## 2. Saturation: 5 in helps the low-range BOT axes but does not save them

Raw |peak| as a fraction of full scale (FS ≈ 990–1,000 G for CH6–8):

| channel | 5 in median (max) %FS | 5 in >FS | 10 in median (max) %FS | 10 in >FS |
|---|--:|--:|--:|--:|
| CH6 | 40.7 (96.3) | 0/30 | 76.4 (107.4) | **9/30** |
| CH7 | 88.9 (104.9) | **2/30** | 105.0 (107.2) | **26/30** |
| CH8 | 94.3 (107.5) | **4/30** | 101.7 (107.0) | **16/30** |

At 10 in the BOT tri-axis is quantitatively unusable (CH7 over FS on 26/30
drops, medians at or above 100 % FS — consistent with both check runs). At
5 in the picture improves but stays marginal: CH8's median is 94 % FS and
CH7/CH8 still exceed FS on 2–4 of 30 drops. **No candidate drop height fixes
BOT** — that requires higher-range sensors at the bottom vertex (or accepting
BOT as a qualitative alive/dead diagnostic only). The high-range channels are
comfortable everywhere: at 10 in the hardest-working ones are CH5 at 62 % FS
and CH4 at 36 % FS, leaving clean headroom for stiffer specimens.

## 3. Metric quality: sub-1 % CV at both heights

CFC-180 (SAE J211) metrics over 30 drops, mean (CV):

| metric | 5 in | 10 in | 10/5 ratio |
|---|--:|--:|--:|
| CH5 input peak | 150.8 G (0.44 %) | 221.8 G (0.86 %) | 1.471 |
| TOP output peak | 171.6 G (0.69 %) | 249.5 G (0.31 %) | 1.454 |
| T = TOP/CH5 | 1.138 (0.39 %) | 1.125 (0.83 %) | 0.989 |
| pulse width | 1.499 ms (0.26 %) | 1.492 ms (0.27 %) | 1.00 |
| input Δv | 1.81 m/s (0.46 %) | 2.60 m/s (1.40 %) | 1.436 |

Observations:

- **Both heights are excellent measurement points.** Every primary metric
  holds CV < 1 % over 30 drops; the height separation is enormous (Welch
  p ≤ 1e-43, |d| ≥ 25 on the levels), so the two severities are cleanly
  distinguishable operating points, and neither is close to a noise floor.
- **CFC-180 levels scale almost ideally with √h** (1.45–1.47 vs √2 = 1.414),
  while the **raw** spike scales far more steeply (CH5 raw ratio 2.65×) —
  quantitative confirmation of the earlier finding that raw-spike trigger
  margin collapses much faster than √h at low heights.
- **T is nearly height-invariant** (1.138 vs 1.125, a 1 % shift) — good news
  for T as a BO objective: it measures the structure, not the severity
  setting. The small but real difference (d = −1.7) means BO results should
  still standardize on one height rather than mixing them.
- The familiar slow upward T drift is present at both heights (+0.032 %/drop
  at 5 in, +0.045 %/drop at 10 in, both p ≤ 0.007) — same
  mount/coupling-drift signature seen in every campaign since input-output.
- Session-level caveat: T ≈ 1.13 at 10 in here vs 1.083 in the check runs —
  the CH5 tape coupling state has moved again between sessions (tape re-laid
  and/or a different specimen; the posting comment doesn't name the specimen
  ID). Within-session stability is superb; between-session comparability
  still isn't, which is another argument for the rigid keyed CH5 seat in the
  SOP.
- BOT alive 30/30 at both heights; ringdown dominant mode is ~549 Hz on most
  drops with sporadic 122–214 Hz excursions on 6/30 (5 in) and 5/30 (10 in)
  — worth keeping on the watch list, not alarming.

## 4. Recommendation: standardize the BO campaign at **10 in** (trigger at 500 G)

With the 500 G level, trigger reliability no longer constrains the choice —
both heights captured 30/30 with margin. The decision then falls to metric
quality, discrimination potential, and specimen wear:

**Why 10 in:**

1. **Best repeatability of the primary objective.** The TOP output peak —
   the core of both candidate objectives (T, and output-at-fixed-input) —
   is at its tightest at 10 in (CV 0.31 %).
2. **More energy to interrogate the structure.** 44 % more input Δv and
   ~45 % higher CFC-180 levels exercise the lattice harder, which is where
   geometry differences express themselves (the input-output study that
   first showed geometry discrimination ran at comparable severity, 13 in).
   At 5 in a stiff specimen barely works its struts.
3. **Continuity with the durability baseline.** All wear/drift calibration
   (200-drop campaign + both check runs: >260 drops on one specimen with no
   functional failure) is at 10 in. A 10-in BO campaign inherits that
   evidence directly; a 5-in campaign would need its own burn-in/wear
   characterization.
4. **5 in doesn't buy what it was supposed to buy.** Its one hardware
   advantage — keeping the low-range BOT axes in range — doesn't fully
   materialize (CH8 median 94 % FS, still clipping on some drops), so the
   BOT range problem must be solved with sensors either way.

**What 5 in is for (keep it validated, don't discard it):** a gentler,
now-proven operating point — Δv 1.44× lower, levels ~31 % lower, and the
best T repeatability of the pair (CV 0.39 %) — appropriate if BO explores
fragile/soft candidate geometries that might be damaged by repeated 10-in
hits, and as the second point of a future two-severity objective (the
near-√h scaling of the CFC levels makes severity sweeps well-behaved).

**Standing items either way:** keep the trigger at 500 G (worst-case margin
3.9× at 5 in, 10.7× at 10 in; false-trigger clearance ≥27×); treat CH6–8 as
qualitative until re-ranged; and keep pushing the rigid keyed CH5 seat to
close the between-session T shifts.

## Figures

- `data/drop-tests/5vs10/figures/01_trigger_saturation.png` — CH5 raw peaks
  vs the 500 G level (both heights), and CH7/CH8 %FS per drop.
- `data/drop-tests/5vs10/figures/02_metrics_by_height.png` — per-drop
  CFC-180 input, output, T, and Δv at both heights.

## Caveats

- Specimen ID not stated for this session (levels suggest a `7xadt6`-class
  intact print; treat cross-session comparisons as approximate).
- One specimen, one session — the height comparison is within-specimen;
  geometry-discrimination vs height is untested (would need ≥2 geometries
  dropped at both heights).
- 200 ms window as always; Δv is the impact-pulse integral, not the full
  event.
- 5-in and 10-in blocks were run sequentially (not randomized), so height is
  confounded with drop count 1–30 vs 31–60 within the session; the tiny
  within-block drifts (<0.05 %/drop) make this negligible in practice.
