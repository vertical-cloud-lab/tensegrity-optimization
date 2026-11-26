# 30 auto-drops on near-real specimen `RW5F61` (32 captures)

Raw TP4 accelerometer exports for the **30-auto-drop run on `RW5F61`** by
@ctrhjk, posted on
[PR #67](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67).

First campaign on a **near-real specimen**: `RW5F61` has key-seat housings
printed at **both the top and a bottom vertex** (per the #35 igloo design), but
still counts as a failed print (small TPU bubbles on the top tendon). Two new
things vs the `prc1kn` drift-calibration runs:

1. a **third accelerometer** — a low-sensitivity tri-axis unit (9–10.5 mV/G)
   in the **bottom-vertex housing** on CH6/CH7/CH8 (X/Y/Z);
2. the **single-axis base-plate sensor (CH5, the trigger) fell off** during the
   campaign, producing spurious triggers — which is why there are **32 captures
   for 30 conducted drops**.

## Recording setup

Drop height **13 in**, drops released automatically (~15 s cadence; the 32
events span 04:12:54→04:20:16, ~7.4 min). DAQ identical to the
drift-calibration series: 200 ms record, 125 kHz (8 µs), 25000 samples, 2 %
(4 ms) pre-trigger. All channels AC-coupled, ICP on, Half-Sine analysis.

| Channel | Sensor | Mount | Role | Trigger |
|---|---|---|---|---|
| CH2/CH3/CH4 | tri-axis | **top-vertex key-seat** + wax, cable tied | output ("TOP") | No |
| CH5 | single-axis | base plate (wax) — **fell off mid-run** | nominal input | **Yes** (1000 G) |
| CH6/CH7/CH8 | tri-axis (9–10.5 mV/G) | **bottom-vertex housing**, cable tied | input reference ("BOT") | No |

CH2–CH5 full scales / sensitivities as in the prior series (14492.8 / 14992.5 /
13624.0 / 9442.9 G; 0.69 / 0.667 / 0.734 / 1.059 mV/G). CH6/CH7/CH8 = sens
X/Y/Z, 9–10.5 mV/G.

## Files

Each CSV is a TP4 Time-Domain export: header block, then columns
`Time, CH2, CH3, CH4, CH5, CH6, CH7, CH8 (G's)`.

| Captures | Classification |
|---|---|
| `Signal{1..10, 13..16, 18..26, 29..32}` | **27 real drops** (genuine specimen impact) |
| `Signal{11, 12, 17, 27, 28}` | **spurious triggers** from the detached CH5 sensor — no specimen impact in the window |

3 of the 30 conducted drops were never captured cleanly (their impacts fell in
DAQ dead time / outside the windows consumed by the spurious triggers).
**File-name note:** original exports were named `30drops with real_Signal{n}`;
renamed here to `30drops_with_real_Signal{n}.csv`.

## Analysis

- `figures/` — plots + `30drops_real_metrics.json` from
  [`scripts/analysis/drop_test_30drops_real_analysis.py`](../../../scripts/analysis/drop_test_30drops_real_analysis.py)
  (capture classification + CH5 fall-off forensics, burn-in scan,
  stabilized-phase OLS with reliability checks, per-axis migration, damage
  indicators).
- Findings and mounting recommendations:
  [`docs/drop-test-30drops-real-analysis.md`](../../../docs/drop-test-30drops-real-analysis.md).

Regenerate with:

```bash
pip install numpy scipy matplotlib
python scripts/analysis/drop_test_30drops_real_analysis.py
```

## Notes from @ctrhjk

1. `RW5F61` is "close to an actual specimen but still considered a failure
   specimen" (bubbles on the top tendon).
2. Cable tie-off applied to the accelerometers to prevent fall-off (the
   measure introduced after drift-calibration #1).
3. Observed problem: the single-axis base-plate accelerometer **fell off the
   acrylic plate**, and since it was the trigger it "detected the wrong surplus
   acceleration" — the fall-off capture(s) were to be identified from the data.
