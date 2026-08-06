# `abc123-blind/` — blind ABC × 123 crossover (2026-08-04 / 08-05)

Posted by @me-madsen on
[PR #86](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86),
Box folder `tum0zm49ndrua62snpzh803pg9cdrz56`
([link](https://byu.box.com/s/tum0zm49ndrua62snpzh803pg9cdrz56)). This is the
executed version of the design pre-registered in
[`docs/drop-test-ab-blind-protocol.md`](../../../docs/drop-test-ab-blind-protocol.md).

## Design

Three absorber arrangements crossed with three specimens, 5 drops per cell:

| | A — 1/4 in PU alone | B — 1/2 in PU alone | C — 1/4 in over 1/2 in |
|---|:--:|:--:|:--:|
| **1** smaller T3 prism | 5 | 5 | 5 |
| **2** same model as 1, printing defects | 5 | 5 | 5 |
| **3** larger T3 prism | 5 | 5 | 5 |

Two folders of 45 captures each:

- **`ABC - 123 - Order Known`** — key disclosed by the operator:
  `A1` = Signals 1–5, `B1` = 6–10, `C1` = 11–15, `A2` = 16–20, `B2` = 21–25,
  `C2` = 26–30, `A3` = 31–35, `B3` = **41–45**, `C3` = 46–50 (Signals 36–40
  do not exist).
- **`ABC - 123 - Random Arrangement`** — the same nine cells shuffled in
  blocks of 5, key withheld. Signal 6 does not exist, so the blocks are
  Signals 1–5, 7–11, 12–16, 17–21, 22–26, 27–31, 32–36, 37–41, 42–46.

## Capture settings

| | |
|---|---|
| channels | CH2/CH3/CH4 = top-vertex key-seat tri-axis (X/Y/Z) output; CH5 = single-axis base-plate input + trigger |
| sample rate | 1.25 MHz (0.8 µs interval) |
| record | 125,000 samples = **100 ms** |
| pre-trigger | **2.000 ms** (2 %), verified on every capture |
| trigger | **150 G** throughout, both sets |
| full scale | CH2 14,492.8 G · CH3 14,992.5 G · CH4 13,624.0 G · CH5 9,442.9 G |

No channel exceeded 7 % of full scale in either set — the PU stacks removed
the head-room problem that the felt/cardboard campaigns had.

## Sessions (not what the folder names imply)

Clustering the capture timestamps by elapsed-time gaps gives **two**
sessions, not two sets:

| | signals | when | input Δv |
|---|---|---|--:|
| session 1 — set 1, all 45 | 1–50 | 08-04 00:15 → 03:02 | 5.47 ± 0.26 m/s |
| session 1 — set 2 block 1 | 1–5 | 08-04 03:12 → 03:16 | 5.35 ± 0.03 m/s |
| session 2 — set 2 blocks 2–9 | 7–46 | 08-05 23:42 → 08-06 00:40 | **4.22 ± 0.64 m/s** |

The session-2 impact velocity is ~22 % lower, which absolute level features
do not survive. **Confirmed cause (operator, 2026-08-06): all drops were
released from 60 in; the deficit is tower damage — the second drop pin broke
during set-2 drop 6 (the missing capture), see
[issue #92](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/92).**

## Data hygiene

- **Signal 12** (set 2) is not a clean drop: base-plate raw peak 108.6 G,
  *below* the 150 G trigger, "impact" at 9.9 ms with a 10 ms pulse. Excluded
  by the stated rule (raw peak ≥ trigger level). All other 89 captures are
  clean. Explanation: on the damaged tower, arrangement C's raw base peaks
  fell to 156–207 G — 1.04–1.38× the trigger — and Signal 12 is a real drop
  that never crossed it cleanly.
- **Blind-key outcome:** the operator confirmed the reconstructed key correct
  on all nine blocks (`B2 A1 C1 B1 C3 A3 A2 B3 C2`) — see
  [findings doc §0](../../../docs/drop-test-abc123-blind-analysis.md).

## Raw data is not committed

The 90 CSVs total ~823 MB, so only derived metrics and figures live here.
Re-fetch from the Box link above into `raw/known/` and `raw/random/` (keep
the original filenames) and run:

```bash
pip install numpy scipy matplotlib
python scripts/analysis/drop_test_abc123_blind_analysis.py --raw data/drop-tests/abc123-blind/raw
```

## Contents

| path | what |
|---|---|
| `figures/abc123_metrics.json` | every per-drop metric, the fitted classifiers, the reconstructed key, repeatability and discrimination tables |
| `figures/01_arrangement_discriminant.png` | input pulse FWHM, set 1 labelled vs set 2 blind |
| `figures/02_specimen_discriminant.png` | secondary-event timing, set 1 vs set 2 per arrangement |
| `figures/03_discrimination.png` | between-specimen SNR and the 1-vs-2 effect size, by arrangement |
| `figures/04_ringdown.png` | ringdown f_n / ζ / fit quality, and the secondary event by cell |

Findings: [`docs/drop-test-abc123-blind-analysis.md`](../../../docs/drop-test-abc123-blind-analysis.md).
