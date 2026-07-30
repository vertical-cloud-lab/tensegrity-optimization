# Print-defect study — five nominally identical T3-prism prints (60 in, 2026-07-28/29)

Five specimens printed from the same T3-prism model/configuration, ~100 drops
each at 60 in on the 4-felt + 1-cardboard stack, posted by @me-madsen on PR #86
([comment 5136111762](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5136111762),
Box folder `oii429e3znjusbltzg56h5kwbi5cj29n`). Purpose: measure how much
printing defects affect the drop-test result.

Analysis: [`docs/drop-test-print-defects-analysis.md`](../../../docs/drop-test-print-defects-analysis.md) ·
Script: [`scripts/analysis/drop_test_print_defects_analysis.py`](../../../scripts/analysis/drop_test_print_defects_analysis.py)

## Specimens

Specimen IDs are lower-cased here; per @me-madsen, treat T3 unique IDs as
case-insensitive (the TP4 exports use mixed case, e.g. `57vqhX`, `mDT6Ja`).

| # | id | zip | captures | session ID | date | defects (@me-madsen) |
|--:|---|---|--:|---|---|---|
| 1 | `57vqhx` | `raw/57vqhx.zip` | 101 | `57vqhX 60 in - 4 felt 1 crdbrd` | 07-28 14:22 | most defects |
| 2 | `mdt6ja` | `raw/mdt6ja.zip` | 100 | `mDT6Ja - 60 in - 4 flt 1 crdbrd` | 07-28 15:34 | most defects |
| 3 | `j1crxg` | `raw/j1crxg.zip` | 100 | `J1CRxg - 60 in - 4 flt 1 crdbrd` | 07-28 17:06 | most defects |
| 4 | `cruela` | `raw/cruela.zip` | 101 | `Cruela - 60 in - 4 flt 1 crdbrd` | 07-29 11:52 | mostly defect-free |
| 5 | `bpx68c` | `raw/bpx68c.zip` | 100 | `bpX68c - 60in - 4 flt 1 crdbrd` | 07-29 16:34 | most defect-free |

Defect photos/video: [PR #35 comment 5110159623](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-5110159623)
(video, specimens 1–4) and the comment below it (photo, specimen 5).

`raw/{id}_series_table.csv` is the TP4 Series Table export for each session.

## Setup

Standard 60 in campaign SOP: bungees removed, top-vertex key-seat tri-axis
output, base-plate single-axis input + trigger, 4 felt + 1 cardboard absorber
stack, ~40 s auto cadence.

| channel | sensor | role | full scale |
|---|---|---|--:|
| CH2 / CH3 / CH4 | high-range tri-axis, top-vertex key seat (X/Y/Z) | output ("TOP") | 14,492.8 / 14,992.5 / 13,624.0 G |
| CH5 | single-axis, base acrylic plate | input + trigger | 9,442.9 G |

Capture format: 4-channel, **1.25 MHz over a 20 ms window** (25,000 samples) —
the same short-window/high-rate format as the polyurethane sessions, not the
older 125 kHz / 200 ms format.

## ⚠️ Confounds — read before using these numbers

1. **The absorber stack was moved/adjusted before specimens 4 and 5**
   (@me-madsen). Those are also the low-defect specimens *and* a different day,
   so defect grade, session day and stack state all change at the same
   boundary. The base-plate raw peak drops 60 % across it (6,193 → 2,471 G).
2. **Defect grade is identical to test order** (graded 1–5 in the sequence
   tested), so any progressive rig effect reproduces the defect correlation.
3. **The accelerometer mount is re-seated between specimens.** Within a single
   session, with the mount untouched, T already wanders by up to 2.34 % — more
   than the 1.95 % spread across all five specimens.

The analysis doc leads with `T = TOP/CH5` because it cancels (1); it cannot
separate (2) or (3) from a real print effect. See §6 there for the cheap
follow-up experiment that would.

## Headline result

Print-to-print scatter in transmissibility is **CV ≈ 0.72 %** (1.95 % spread
across five copies) — the first direct measurement of the quantity the
sample-size analysis flagged as uncharacterized, and the same magnitude as the
2.3 % between-*design* spread reported in the three-structure 60 in comparison.
Practical consequence: **≥3 replicate prints per geometry** before treating a
sub-5 % T difference as a design result.

## Figures

| file | what |
|---|---|
| `figures/01_full_series.png` | per-drop input, output and T across all five campaigns |
| `figures/02_specimen_distributions.png` | per-specimen T and output distributions, ordered by defect grade |
| `figures/03_variance_and_confound.png` | within- vs between-specimen variance, T vs defect grade, and the input step at the felt adjustment |
| `figures/print_defects_metrics.json` | all per-capture and per-specimen metrics |

## Video

`video/*.XML` are the camera sidecars for the 14 slow-motion clips in the Box
upload (~548 MB each, ~7.4 GB total — not committed). Every sidecar states
`captureFps="959.04p"`, so the time base is exact.

Two notes on the set: `57cqhx 3.MP4` is a typo for `57vqhx 3`, and
`57vqhx 1.XML` has no matching MP4, so specimen 1 has 2 clips rather than 3.
Frame-by-frame kinematics have not been run on these — see the analysis doc §7.

## Relationship to other folders on this branch

`7-30-2026 - 100 drops - 60 in - 4 flt 1 crdbrd/` contains a partial duplicate
of the same two sessions uploaded directly to the branch: `57vqhx/` (101 loose
CSVs, identical session) and `mdt6ja/` (2 zips = 50 of the 100 captures). The
`raw/` zips here are complete for all five specimens and are what the analysis
script reads; that folder can be deleted to reclaim ~213 MB if desired. Note its
`7-30-2026` name refers to the upload date, not the test dates (07-28/07-29).
