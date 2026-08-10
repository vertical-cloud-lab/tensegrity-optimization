# `pre-post-grease/` — guide-rod cleaning/greasing A/B (2026-08-10)

Posted by @me-madsen on
[PR #86](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86),
Box folder `m3jsyavz2h2c7ck8pe496j6x8utm8bll`
([link](https://byu.box.com/s/m3jsyavz2h2c7ck8pe496j6x8utm8bll)), TP4 session
ID **"Drop Speed Decay"**. Ten drops, all at **60 in** on **arrangement B**
(1/2 in PU sheet alone) with **specimen 2** (small T3 prism, printing
defects) — the same `B2` cell measured in the abc123 blind crossover, which
supplies matched healthy-tower (08-04) and damaged-tower (08-05/06)
references:

- **Signals 1–5** — before cleaning and greasing the guide rods
  (15:16–15:19 local; ~42 s cadence)
- **Signals 6–10** — after cleaning + greasing (15:25–15:28; the
  maintenance itself is the 6.4 min gap)

This is the follow-up to the issue #92 tower damage (broken drop pin /
rail friction), after the blind-test analysis found the carriage arriving
at only 79–86 % of free-fall speed.

## Capture settings

Identical to the abc123 campaign: CH2–CH4 = top-vertex key-seat tri-axis
output, CH5 = single-axis base-plate input + trigger (150 G), 1.25 MHz,
125,000 samples = 100 ms record, 2.000 ms pre-trigger.

## Files

Raw captures are **not committed** (~95 MB); fetch them from the Box folder
into `raw/`. Per-file Box IDs (download via
`https://byu.box.com/index.php?rm=box_download_shared_file&shared_name=m3jsyavz2h2c7ck8pe496j6x8utm8bll&file_id=f_<ID>`):

| file | Box ID |
|---|---|
| `pre-post-grease_Signal1.csv` | 2401060278519 |
| `pre-post-grease_Signal2.csv` | 2401060722634 |
| `pre-post-grease_Signal3.csv` | 2401061305806 |
| `pre-post-grease_Signal4.csv` | 2401060413232 |
| `pre-post-grease_Signal5.csv` | 2401092160704 |
| `pre-post-grease_Signal6.csv` | 2401063331683 |
| `pre-post-grease_Signal7.csv` | 2401062832721 |
| `pre-post-grease_Signal8.csv` | 2401060773154 |
| `pre-post-grease_Signal9.csv` | 2401062167276 |
| `pre-post-grease_Signal10.csv` | 2401060686160 |

Committed: `raw/pre-post-grease.csv` (the TP4 series table, 1.6 KB),
`figures/` (plots + `pre_post_grease_metrics.json` with every per-drop
metric).

## Analysis

Script: [`scripts/analysis/drop_test_pre_post_grease_analysis.py`](../../../scripts/analysis/drop_test_pre_post_grease_analysis.py)
(reuses the abc123 per-capture pipeline unchanged).
Writeup: [`docs/drop-test-pre-post-grease-analysis.md`](../../../docs/drop-test-pre-post-grease-analysis.md).

Headline: cleaning/greasing produced a real **+5.4 % step in impact Δv**
(4.44 → 4.68 m/s, p = 1.3e-4), independently corroborated by a +5.1 % step
in the ballistic specimen-hop delay — but the tower still delivers only
~88 % of free-fall speed (≈ 47 in equivalent from a 60 in hoist), so the
greasing recovered roughly **28 % of the damage deficit**; the issue #92
pin repair is still needed.
