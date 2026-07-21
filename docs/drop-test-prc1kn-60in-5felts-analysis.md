# `prc1kn` at 60 in + mock three-structure transmissibility comparison

Analysis of the campaign posted by @me-madsen on PR #86: the
rig-calibration standard **`prc1kn`** run through the same full-length
campaign as the [60 in / 5 felt validation](drop-test-60in-5felts-analysis.md)
— 101 captures (`prc1kn - set 1 - {1..4}.zip`), 2026-07-21 20:56–22:06,
the evening after the `7xadt6`/`9GMQYQ` campaigns — plus the requested
**mock comparison of transmissibility across the three structures**.

**⚠️ The stack was not 5 felt sheets.** The TP4 session ID reads
`prc1kn 60in - 4 felt 1 cardboard`. That substitution matters (§3): the
cardboard-for-felt swap roughly **doubles the raw base-plate spike**, and
CH5 spent the entire session above the FS/3 head-room target, peaking at
**79 % of full scale**.

Rig otherwise unchanged: CH2–CH4 = top-vertex key-seat tri-axis ("TOP"
output), CH5 = single-axis on the base plate (input + trigger), 200 ms /
125 kHz. Data: `data/drop-tests/prc1kn-60in-5felt/` (committed zips);
script: `scripts/analysis/drop_test_prc1kn_60in_5felts_analysis.py`;
metrics: `data/drop-tests/prc1kn-60in-5felt/figures/prc1kn_60in_metrics.json`.

## 1. Capture health: 101/101 clean

| | `prc1kn` |
|---|--:|
| real drops / captures | **101/101** |
| spurious triggers | 0 |
| impact lands at | 3.99 ± 0.02 ms |
| cadence (median) | 41 s |
| campaign span | 70 min |

Third consecutive flawless campaign at the 41 s / 60 in cadence
(`figures/01_full_series.png`).

## 2. Stabilized-phase OLS (drops 6–101, n = 96)

Same convention as the validation campaigns: the burn-in scan finds no
k ≤ 20 with a non-significant trend (campaign-scale felt wear again, not a
seating transient), so the SOP burn-in of 5 is used.

| metric | mean | CV | slope /drop | %/drop | p | R² | DW |
|---|--:|--:|--:|--:|--:|--:|--:|
| TOP output CFC-180 (G) | 477.4 | 1.09 % | +0.179 | +0.038 | 5.3e-52 | 0.915 | 2.13 |
| CH5 input CFC-180 (G) | 472.2 | 0.65 % | +0.107 | +0.023 | 3.4e-65 | 0.955 | 1.45 |
| T = TOP/CH5 | 1.011 | 0.51 % | +1.5e-4 | +0.015 | 1.4e-24 | 0.674 | 2.50 |

Split-half (TOP): +0.047 %/drop (drops 6–54) → +0.030 %/drop (55–101) —
same decelerating input-driven climb as the 5-felt campaigns, and T again
absorbs most of it (total drift ≈ +1.4 % over 96 drops). Health
indicators are clean: output pulse width 1.57 ms (CV 0.58 %, slope
−0.017 %/drop — a slight *shortening* as the stack stiffens, the opposite
of damage), plate Δv 5.78 m/s (free-fall from 60 in plus rebound), and the
ringdown's structural lobe stays put (the 51 % CV on "dominant frequency"
is the familiar bin-hop between the ~120 Hz and ~500 Hz lobes, cf. the
[health check](drop-test-prc1kn-health-check.md)). **`prc1kn` survives 100
drops at 60 in as calmly as it survived 48 at 13 in** — the dummy remains
a valid calibration standard at campaign energy.

## 3. The cardboard substitution: CH5 near saturation all session

`figures/03_saturation.png` overlays this session on the 5-felt campaigns:

| session (chronological) | stack | CH5 raw first 5 | last 5 | worst %FS |
|---|---|--:|--:|--:|
| `7xadt6` (07-20) | 5 felt, fresh | 2,448 G | 3,163 G | 35.1 % |
| `9GMQYQ` (07-20) | 5 felt, worn | 4,210 G | 6,068 G | 68.6 % |
| **`prc1kn` (07-21)** | **4 felt + 1 cardboard** | **5,775 G** | **7,276 G** | **79.2 %** |

- Every one of the 101 captures is above the FS/3 target (drop 1 already
  hits 45 % FS); the session ends ~20 % below the sensor's full scale. A
  stiffer intact specimen (or one more evening of compaction) would risk
  clipping the input channel.
- The CFC-180 input barely notices (472.2 G vs 446–463 G on 5 felt —
  within ~6 %): the cardboard adds short high-frequency spike content, the
  signature already established for compacted felt. So the *filtered*
  physics stayed comparable, which is what rescues the three-way
  comparison below — but the raw head-room is nearly gone.
- **Recommendation: don't substitute cardboard for felt.** Restore the
  5-felt stack (or 6 felt if swaps are impractical) and keep the refresh
  rule from the validation writeup: refresh when CH5 raw exceeds
  FS/3 ≈ 3.1 kG. On this stack that threshold was exceeded before the
  first drop.

## 4. Mock three-structure transmissibility comparison

Stabilized drops, all three campaigns (`figures/04_three_structure_comparison.png`):

| specimen | TOP CFC-180 (G) | T = TOP/CH5 | n |
|---|--:|--:|--:|
| `7xadt6` | 461.4 ± 8.1 (CV 1.74 %) | 1.034 ± 0.001 (CV 0.12 %) | 95 |
| `9GMQYQ` | 475.2 ± 4.8 (CV 1.00 %) | 1.027 ± 0.005 (CV 0.45 %) | 96 |
| `prc1kn` | 477.4 ± 5.2 (CV 1.09 %) | 1.011 ± 0.005 (CV 0.51 %) | 96 |

One-way ANOVA on T: F = 816, p = 1.9e-118. Pairwise (Welch):

| pair | ΔT | p | \|d\| |
|---|--:|--:|--:|
| `7xadt6` vs `9GMQYQ` | +0.7 % | 6.4e-27 | 2.1 |
| `9GMQYQ` vs `prc1kn` | +1.6 % | 4.2e-56 | 3.3 |
| `7xadt6` vs `prc1kn` | +2.3 % | 5.3e-69 | 6.2 |

**Energy-absorber ranking (lower T = better):**

1. **`prc1kn` — T = 1.011** (amplifies the base peak by 1.1 %)
2. `9GMQYQ` — T = 1.027 (+2.7 %)
3. `7xadt6` — T = 1.034 (+3.4 %)

Two honest readings of that ranking:

- **None of the three attenuates.** All sit above T = 1: at this stiff
  ~1.6 ms base pulse, each structure passes the CFC-180 peak through
  essentially 1:1, slightly amplified. "Best absorber" here means "least
  bad" — the only structure measured below 1 so far is `yqpmx1`
  (T ≈ 0.96, [input-output run](drop-test-input-output-analysis.md), 13 in).
  If the BO campaign's goal is genuine shock *absorption*, there is real
  head-room to search for.
- **The nominal winner is the failed print.** `prc1kn` is the bubbled-TPU
  dummy — softer tendons plausibly do transmit a touch less peak — but its
  campaign differs from the other two in stack (§3) and in mount
  re-waxing, so treat the 1.6–2.3 % gaps as indicative, not settled
  (see caveats). What the comparison *does* establish cleanly is
  methodological: with ~95 stabilized drops each, three structures whose T
  values span only 2.3 % separate with |d| = 2.1–6.2. **T resolves
  between-structure differences far smaller than anything the BO campaign
  needs** (≥10 % between-design differences at n ≈ 5 drops).

## 5. Caveats

- **Stack mismatch:** `prc1kn` ran on 4 felt + 1 cardboard, the others on
  a shared 5-felt stack a day earlier. T normalizes the input level
  (CFC-180 inputs agree within ~6 %), but a stiffer stack shifts the input
  spectrum, and T is frequency-dependent — part of the 1.6–2.3 % gap could
  be stack, not structure.
- **Mount confound:** the tri-axis was re-waxed between campaigns, and the
  [health check](drop-test-prc1kn-health-check.md) showed re-mounts can
  shift T's *level* (0.99 → 1.20 across the 13 in sessions; the recent
  wax-SOP campaigns cluster much tighter, 1.01–1.03, but the confound
  isn't zero). Compare T across specimens only within a shared SOP, and
  prefer same-session A/B when a ranking actually matters.
- n = 1 physical article per structure (95–96 repeat drops each);
  print-to-print reproducibility is still uncharacterized.
- Durbin–Watson ~0.6–2.1 on the drifting channels: slopes and R² are the
  meaningful quantities, the tiny p-values overstate certainty.
- 200 ms window; Δv is partial-pulse; CFC-180 peak transmissibility only —
  an SRS- or band-wise T (as the Edison synthesis recommends) may rank
  differently.
