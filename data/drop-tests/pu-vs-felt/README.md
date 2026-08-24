# Polyurethane rubber vs felt+cardboard paired A/B test (`bpx68c`)

Posted by @me-madsen on PR #86 (Box folder
`https://byu.box.com/s/qfryxzjej47yil7ztvqxmhf5qcq0qa4p`): the same
specimen dropped 5 times on the incumbent 4-felt + 1-cardboard stack and
then 5 times on the new polyurethane rubber sheets (issue #88) — the
first data on the durable-absorber replacement proposed in
[`docs/drop-test-absorber-alternatives.md`](../../../docs/drop-test-absorber-alternatives.md).

## Sessions (both 2026-07-30, same mount, back-to-back)

| zip | TP4 session ID | drops | time |
|---|---|--:|---|
| `raw/felt-cardboard.zip` | `bpx68c - 60 in - 4 flt 1 crdbrd` | 5 | 11:19–11:23 |
| `raw/polyurethane.zip` | `bpx68c - Polyurethane Rubber` | 5 | 11:41–11:45 |

Each zip holds `bpx68c_Signal{1..5}.csv` (`Signal` index = drop number)
plus the TP4 series-table export `bpx68c.csv`. Format: full 4-channel
export at **1.25 MHz over a 20 ms window** (the short-window format of
the 7-23/7-27 sessions, but with all channels enabled).

The PU session ID does not state a drop height or the rubber sheet
count/thickness/durometer; the measured full-pulse Δv matches free fall
from 60 in, so the analysis treats both sessions as 60 in.

## Channel map (unchanged from the 60 in campaigns)

| channel | sensor | full scale |
|---|---|--:|
| CH2 / CH3 / CH4 | top-vertex key-seat tri-axis X/Y/Z ("TOP" output) | 14,492.8 / 14,992.5 / 13,624.0 G |
| CH5 | single-axis on the base acrylic plate (input + trigger) | 9,442.9 G |

## Analysis

Script: [`scripts/analysis/drop_test_pu_vs_felt_analysis.py`](../../../scripts/analysis/drop_test_pu_vs_felt_analysis.py)
(reads the CSVs straight out of the zips) → `figures/` +
`figures/pu_vs_felt_metrics.json`. Writeup:
[`docs/drop-test-pu-vs-felt-analysis.md`](../../../docs/drop-test-pu-vs-felt-analysis.md).

Headline: PU cuts the raw CH5 spike −71 % (head-room problem solved) and
delivers a ~2× longer, −54 % lower input pulse; T = 0.976 (CV 1.3 %) vs
1.009 (CV 0.4 %) on felt — but the PU input is bimodal at n = 5
(soft/stiff stack states), so the stack needs seating/restraint and a
stiffer operating point before campaign use.
