# Clip-height sweep & accelerometer-check drop tests

Two follow-up experiments by @ctrhjk (PR #67 thread) aimed at the recurring
problem that **the accelerometer placed on the acrylic plate never registers an
impact above its 1000 G trigger** — first seen in the
[`vertex-acrylic`](../vertex-acrylic/) series (3/4 acrylic runs gave no clean
impact).

## 1. Clip-height sweep — PR comment [4794351098](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36)

**Goal:** test whether the retaining-clip height is what kills the
acrylic-plate measurement (clips set too low were hypothesized to let the
acrylic plate seat on / be held by the specimen, so the shock never reaches the
plate-mounted sensor).

**Setup:**
- Added **three more bungee cords** so two vertices are each pinned by two cords
  and the third vertex by the remaining two. This cured the earlier specimen
  fly-off.
- **Tri-axis** accelerometer placed **above the acrylic plate**, vertex directly
  below. The single-axis (CH5) sensor was intentionally omitted for this test.
- Retaining clips set at **0.5, 1.0, 1.5, 2.0 in** above the acrylic-plate
  surface; **two drops at each height** on a "Practice" tensegrity specimen.
- Channel / recording setup identical to the vertex-acrylic series
  (CH2/CH3/CH4 tri-axis, CH4 triggered at 1000 G; 200 ms / 125 kHz / 2 % =
  4 ms pre-trigger).

**Result:** **none of the eight drops triggered** — no acceleration above the
1000 G trigger was recorded at any clip height, so there is **no waveform CSV**
for this sweep (video only). Adding cords fixed fly-off but did not make the
load reach the plate sensor. @ctrhjk's candidate error sources: accelerometer
position (edge of plate), accelerometer orientation, a trigger level (1000 G)
that is too high, or the acrylic plate not transmitting the shock efficiently.

## 2. Accelerometer check (base plate) — PR comment [4794438322](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36)

**Goal:** rule the sensor / DAQ in or out by removing the acrylic plate from the
load path entirely.

**Setup:** same channel / recording setup, but the **tri-axis accelerometer was
placed directly on the bottom (base) plate**. Drop height **13 in**.

**Result:** a clean, triggered impact — see [`raw/Accelerometer_check_Signal1.csv`](raw/Accelerometer_check_Signal1.csv)
(TP4 session ID "Practice with dummy", 06/24/2026). Analyzed by
[`scripts/analysis/drop_test_clip_height_analysis.py`](../../../scripts/analysis/drop_test_clip_height_analysis.py);
findings in [`docs/drop-test-clip-height-analysis.md`](../../../docs/drop-test-clip-height-analysis.md).

| channel | raw \|g\| | CFC-1000 | CFC-180 | Δv |
|---|--:|--:|--:|--:|
| CH2 | 599 | 45 | 10 | 0.03 |
| CH3 | 710 | 55 | 5 | 0.05 |
| **CH4 (triggered, drop axis)** | **3072** | **1154** | **280** | **3.28** |

CH4 raw peak (3072 G) is **3.1× the 1000 G trigger**, so the sensor and DAQ
register a clean impact when the load reaches them directly. This isolates the
clip-height "no trigger" failure to the **load path** — the acrylic plate is
seating on / being damped by the bungee-restrained specimen so the shock never
reaches the plate-mounted sensor — not to the sensor, trigger level, or DAQ.

## Channel setup (both experiments)

| ch | sensor | full scale | trigger | sensitivity |
|---|---|--:|---|--:|
| CH2 | tri-axis | 14492.8 G | No | 0.69 mV/G |
| CH3 | tri-axis | 14992.5 G | No | 0.667 mV/G |
| CH4 | tri-axis | 13624.0 G | **Yes, 1000 G** | 0.734 mV/G |
| CH5 | single-axis | 9442.9 G | No | 1.059 mV/G (unused here) |

Recording: 200 ms record, 125 kHz (8 µs), 25 000 samples, 2 % (4 ms) pre-trigger.
