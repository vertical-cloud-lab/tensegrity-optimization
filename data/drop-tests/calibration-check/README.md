# `calibration-check/` — post-reset sensitivity verification (2026-08-17 / 08-19)

The TP4's channel settings were **cleared and re-entered by hand** on
08-18. [`tp4-settings-2026-08-18.jpg`](tp4-settings-2026-08-18.jpg) is
@me-madsen's photo of the re-entered Recording Setup / Analog Channels
screen — committed as the canonical settings record. To verify the
re-entered sensitivities, the same specimen was re-run at the same
operating point (**`bpx68c`**, low-defect small T3 prism from the
print-defect study; **60 in**, **arrangement B** = 1/2 in PU mat):

| session | TP4 session ID | recorded | drops | Box folder |
|---|---|---|--:|---|
| before (pre-reset settings) | `bpx68c - 60 in - 1/2" mat - 100 drops` | 08-17 21:57–23:28 UTC | 101 | [`it5499hkyw24twg7179smsn0fv0bodal`](https://byu.box.com/s/it5499hkyw24twg7179smsn0fv0bodal) |
| after (re-entered settings) | `bpx68c - calibration testing` | 08-19 19:14–19:36 UTC | 30 | [`4tttcvt6lx008tr05meruslkwasqqskh`](https://byu.box.com/s/4tttcvt6lx008tr05meruslkwasqqskh) |

(The after folder is named `8-18-2026 …` on Box but its captures are
time-stamped 08-19.)

## Settings as re-entered (from the screenshot)

100 ms record, 1.25 MHz, 125,000 samples, 2 % = 2 ms pre-trigger;
CH2/CH3/CH4 (top-vertex tri-axis X/Y/Z) at 0.690 / 0.667 / 0.734 mV/G
(full scale 14,492.8 / 14,992.5 / 13,624.0 G), CH5 (base-plate
single-axis, trigger at 150 G) at 1.059 mV/G (9,442.9 G) — identical to
the channel map recorded since June
([`vertex-acrylic/README.md`](../vertex-acrylic/README.md)). CH1/6/7/8
inactive at the 10 mV/G default.

## Files

Raw captures are **not committed** (~1.2 GB); fetch from Box into
`raw/before/` and `raw/after/` (`bpx68c_Signal*.csv`). Per-file Box IDs
for both folders are in [`raw/box-ids.json`](raw/box-ids.json); download via
`https://byu.box.com/index.php?rm=box_download_shared_file&shared_name=<shared_name>&file_id=<typedID>`.

Committed: the two TP4 series tables (`raw/before-series.csv`,
`raw/after-series.csv` = each folder's `bpx68c.csv`), the settings
screenshot, and `figures/` (plots + `calibration_check_metrics.json`
with every per-drop metric).

## Analysis

Script: [`scripts/analysis/drop_test_calibration_check_analysis.py`](../../../scripts/analysis/drop_test_calibration_check_analysis.py)
(abc123 per-capture pipeline + per-axis peaks, axis shares, and
pre-trigger noise floors).
Writeup: [`docs/drop-test-calibration-check-analysis.md`](../../../docs/drop-test-calibration-check-analysis.md).

Headline: **the re-entered settings check out.** Every scale-cancelling
observable is continuous across the reset (Δv +0.1 %, T −0.3 %,
`e_rebound` −1.0 %, trigger crossing at 2.05 ms both sessions), which
pins any per-channel gain error to ≲1 % on CH5 and the resultant — far
below the smallest plausible mis-entry (3.4 %). The visible +9–11 %
level shift is pulse *reshaping* (peak up, width down, peak×width
constant) from the rested/re-seated mat, not a gain change.
