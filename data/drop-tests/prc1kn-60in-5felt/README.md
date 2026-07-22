# `prc1kn` 60 in campaign (posted as "prc1kn-60in-5felt")

101 captures of the rig-calibration standard **`prc1kn`** (the bubbled-TPU
"failed print" dummy from the mount-validation and drift-calibration runs)
at the campaign operating point, posted by @me-madsen on PR #86 on
2026-07-21. Session ran 20:56–22:06 (70 min, median cadence 41 s), the
evening after the `7xadt6`/`9GMQYQ` validation campaigns.

**Note the stack:** the TP4 session ID is
`prc1kn 60in - 4 felt 1 cardboard` — **4 felt sheets + 1 cardboard**.
@me-madsen later confirmed (PR #86) that this is the composition of
*every* session labeled "5 felt" (the lab has no fifth felt sheet), so
this session ID is just the first honest label, not a substitution. The
folder name keeps the "5felt" label it was posted under; the elevated
raw base-plate spike relative to 2026-07-20 is cumulative stack wear,
not a composition change (see the analysis writeup, §3).

## Files

| file | contents |
|---|---|
| `prc1kn - set 1 - 1.zip` | `prc1kn set 1_Signal{1..25}.csv` |
| `prc1kn - set 1 - 2.zip` | `prc1kn set 1_Signal{26..50}.csv` |
| `prc1kn - set 1 - 3.zip` | `prc1kn set 1_Signal{51..75}.csv` |
| `prc1kn - set 1 - 4.zip` | `prc1kn set 1_Signal{76..101}.csv` |

TP4 Time-Domain exports, 200 ms / 125 kHz per capture. The analysis script
reads the CSVs straight out of the zips — no need to extract.

## Channel map (unchanged from the felt-sheet sweep / 60 in validation)

| channel | sensor | full scale |
|---|---|--:|
| CH2/CH3/CH4 | top-vertex key-seat tri-axis (X/Y/Z), "TOP" output | 14,492.8 / 14,992.5 / 13,624.0 G |
| CH5 | single-axis on the base acrylic plate — input + trigger | 9,442.9 G |

## Analysis

- Script: [`scripts/analysis/drop_test_prc1kn_60in_5felts_analysis.py`](../../../scripts/analysis/drop_test_prc1kn_60in_5felts_analysis.py)
- Writeup: [`docs/drop-test-prc1kn-60in-5felts-analysis.md`](../../../docs/drop-test-prc1kn-60in-5felts-analysis.md)
- Figures + machine-readable metrics: [`figures/`](figures/)

## Slow-mo videos

Two 959.04 fps videos (Sony RX100M4, XML sidecars included) of rehearsal
drops shot ~5.5 h before the DAQ session, with the 20 mm checkerboard
calibration grid in frame — see [`video/`](video/) and
[`docs/drop-test-prc1kn-video-analysis.md`](../../../docs/drop-test-prc1kn-video-analysis.md)
(kinematics, three-structure cross-reference, grid-placement guidance).
