# Polyurethane sheet-configuration sweep (`bpx68c`, 60 in, 2026-07-30)

Four arrangements of the two polyurethane rubber sheets, 10 drops each, posted
by @me-madsen on PR #86
([comment 5136470475](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5136470475),
Box folder `4n678tlpnlk7q50dfi1rh1lkt7p6lx0y`) to determine which stack to run
transmissibility tests on.

Analysis: [`docs/drop-test-pu-configs-analysis.md`](../../../docs/drop-test-pu-configs-analysis.md) ·
Script: [`scripts/analysis/drop_test_pu_configs_analysis.py`](../../../scripts/analysis/drop_test_pu_configs_analysis.py)

## Setup

TP4 session `bpx68c - Polyurethane Rubber - Further Tests`, 2026-07-30
13:08–15:10. Same rig as the paired PU-vs-felt A/B run
([`pu-vs-felt/`](../pu-vs-felt/)): specimen `bpx68c` on the acrylic carriage
plate, bungees removed, top-vertex key-seat tri-axis, base-plate single-axis
input, 60 in drop height, ~40 s cadence.

| channel | sensor | role | full scale |
|---|---|---|--:|
| CH2 / CH3 / CH4 | high-range tri-axis, top-vertex key seat (X/Y/Z) | output ("TOP") | 14,492.8 / 14,992.5 / 13,624.0 G |
| CH5 | single-axis, base acrylic plate | input + trigger | 9,442.9 G |

Capture format: 4-channel, **1.25 MHz over a 20 ms window** (25,000 samples),
9 header lines. The record starts on the trigger, so there is no clean
pre-trigger baseline — see the analysis script's module docstring for the
conventions this forces.

## Files

| zip | arrangement | signals | trigger level |
|---|---|---|--:|
| `raw/quarter-in.zip` | **A** — the thin 1/4 in sheet alone | 1–10 | 300 G |
| `raw/half-in.zip` | **B** — the thicker 1/2 in sheet alone | 11–20 | 300 G |
| `raw/quarter-top-half-bottom.zip` | **C** — 1/4 in on top, 1/2 in underneath | 22–31 | 150 G |
| `raw/half-top-quarter-bottom.zip` | **D** — 1/2 in on top, 1/4 in underneath | 32–41 | 150 G |
| `raw/bpx68c_series_table.csv` | TP4 Series Table export for the whole session (all 41 events) | | |

**Signal 21 is absent from the upload** and is excluded per @me-madsen's
instruction. The series table shows it as an event at 13:26 — two minutes after
arrangement B ends and 75 minutes before C starts — i.e. a stray capture, not
part of any 10-drop block. The block boundaries above are confirmed by the
series-table timestamps (A 13:08–13:15, B 13:18–13:24, C 14:42–15:01,
D 15:03–15:10).

The trigger level was lowered from 300 G to 150 G for arrangements C and D
(@me-madsen), because those stacks do not produce a 300 G raw peak.

## Notes from @me-madsen

- Only two polyurethane sheets exist; the same two are used in every
  arrangement here, and they are also the sheets used in the earlier PU-vs-felt
  A/B run ([`pu-vs-felt/`](../pu-vs-felt/)) and linked from
  [issue #88](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/88#issuecomment-5079461202).
- The sheets are adhesive, so lateral movement is not considered a problem and
  fastening them down would be awkward. The analysis agrees fastening is
  unnecessary: the earlier bimodal input traces to *interface seating* between
  two stacked sheets, not sliding, and arrangement A uses a single sheet.

## Headline result

Arrangement **A (1/4 in sheet alone)** is the recommended operating point — the
only one passing all seven qualification criteria, reproducing the felt+cardboard
shock (371 G / 1.66 ms vs 408 G / 1.67 ms) with a 5.4× trigger margin and no
compaction problem. Full reasoning and the caveats in the analysis doc.

## Figures

| file | what |
|---|---|
| `figures/01_pulse_overlays.png` | input + output CFC-180 pulses, 10 drops per arrangement |
| `figures/02_config_comparison.png` | severity, head-room, pulse width and T vs the qualification criteria |
| `figures/03_stability.png` | within-arrangement drift over the 10 drops |
| `figures/04_severity_duration_map.png` | where each arrangement (and the felt stack, and the earlier bimodal A/B run) sits in (input peak, pulse width) |
| `figures/pu_configs_metrics.json` | all per-capture and per-arrangement metrics |
