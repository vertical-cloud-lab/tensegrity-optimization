# 7-22 → 7-27 second-batch 60 in campaigns

Four ~100-drop campaigns at 60 in on the 4 felt + 1 cardboard stack,
posted by @me-madsen on PR #86 — re-runs of the three batch-1 specimens
plus `RW5F61`'s first 60 in session.

| folder | specimen | date | captures | export format |
|---|---|---|--:|---|
| `7-22-2026 prc1kn - 4 felt 1 crdbrd/` | `prc1kn` | 2026-07-22 | 100 | CH2–CH5, 200 ms @ 125 kHz |
| `7-23-2026 RW5F61 - 60in - 4 felt- 1 cardboard/` | `RW5F61` | 2026-07-23 | 101 | **CH5 only**, 20 ms @ 1.25 MHz |
| `7-27-2026 7xadt6 60 in - 4 felt 1 cardbrd/` | `7xadt6` | 2026-07-27 | 100 | **CH5 only**, 20 ms @ 1.25 MHz |
| `7-27-2026 9GMQYQ 60 in - 4 felt 1 cardbrd/` | `9GMQYQ` | 2026-07-27 | 101 | **CH5 only**, 20 ms @ 1.25 MHz |

Raw TP4 exports stay inside the committed zips (`*_{1..4}.zip` per
session); the analysis reads the CSVs straight out of them.

Channel map (4-channel format, unchanged from the batch-1 campaigns):
CH2/CH3/CH4 = top-vertex key-seat tri-axis (X/Y/Z, "TOP" output),
CH5 = single-axis on the base acrylic plate (input + trigger). The three
CH5-only sessions recorded just the base-plate input — no output channel,
so no transmissibility (see §2 of the analysis writeup).

Notes:

* The `prc1kn` zips here are byte-identical to
  [`../7-22-2026 prc1kn 100drops/`](../7-22-2026%20prc1kn%20100drops/)
  (same upload committed twice).
* The `9GMQYQ` files' internal session ID reads `9GMGYQ` (typo).
* `figures/` holds the derived figures + `batch_722_727_metrics.json`.

Analysis: [`docs/drop-test-7-22-7-27-batch-analysis.md`](../../../docs/drop-test-7-22-7-27-batch-analysis.md)
Script: [`scripts/analysis/drop_test_722_727_batch_analysis.py`](../../../scripts/analysis/drop_test_722_727_batch_analysis.py)
