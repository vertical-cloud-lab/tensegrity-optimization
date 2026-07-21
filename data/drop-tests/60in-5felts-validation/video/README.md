# Slow-mo video record — 60 in / 5 felts campaign (7xadt6, 9GMQYQ)

Slow-motion videos of the two 60 in / 5 felt drop-test campaigns, recorded
by @ctrhjk on 2026-07-20 (the same evening as the 201-capture accelerometer
campaign analyzed in
[`docs/drop-test-60in-5felts-analysis.md`](../../../docs/drop-test-60in-5felts-analysis.md))
and posted as YouTube Shorts on PR #86:

| specimen | committed file | YouTube |
|---|---|---|
| `7xadt6` | [`7xadt6_slomo.mp4`](7xadt6_slomo.mp4) (5.8 MB, 677 frames) | https://youtube.com/shorts/Nab3hfuF4Dw |
| `9GMQYQ` | [`9GMQYQ_slomo.mp4`](9GMQYQ_slomo.mp4) (7.2 MB, 830 frames) | https://youtube.com/shorts/zkum2JlHpYk |

The .mp4 files were downloaded and pushed to the branch by @sgbaird
(2026-07-21, originally at repo root; renamed/moved here). CI cannot pull
from YouTube directly (sign-in/bot gate for datacenter IPs), which is why an
earlier pass could only analyze the eight public preview frames
(`*_maxres*.jpg`, `*_poster.jpg` — kept below for the record).

## Camera / time base

- **Sony RX100 IV, HFR mode, 960 fps** — camera spec posted by @ctrhjk in
  PR #67; same workflow as the burn-in-wax videos
  (`data/drop-tests/burn-in-wax/README.md`).
- The committed files are YouTube re-encodes: 720×1280, 30 fps container,
  encoder tag "Google". A camera-native HFR clip is a 24p conform, and the
  duration-preserving 24→30 conversion duplicates ~1 in 5 frames.
- The analysis script **detects and removes duplicated frames** (pixel-diff
  pass + a velocity-based pass for re-encoded duplicates), so real time is
  exactly `unique frame / 960` with no container ambiguity. Measured
  duplicate fractions: 19.8 % (7xadt6 — textbook 24p pulldown) and 14.1 %
  (9GMQYQ). One drop per video; 543 / 713 unique frames = 0.566 s / 0.743 s
  real.

## Analysis

Script: [`scripts/analysis/drop_test_60in_5felts_video_analysis.py`](../../../../scripts/analysis/drop_test_60in_5felts_video_analysis.py)
(requires `opencv-python-headless`). Tracking is correlation-based on the
orange-strut HSV row profile (blob positions fragment under motion blur;
profile correlation does not): consecutive-frame shifts give per-frame
velocity, 5-frame-baseline shifts give the low-noise descent trend. Static
orange content (the brown felt leaks into the HSV band) is subtracted via
the pre-entry median profile.

Findings (one drop per specimen; details + table in the writeup §7):

- **Impact pulse ≤ 2 capture frames ≈ 1–2 ms** — optical corroboration of
  the DAQ's ~1.6 ms CFC pulse width.
- **Anti-rebound catch**: the carriage rebounds at ~0.4× impact speed, is
  decelerated at ~2.1–2.4 g, and is held dead-still ~130–150 mm above the
  felt from ~86–89 ms after impact — no secondary impact.
- **Top-vertex snap-back at ~0.7× impact speed** on both specimens (elastic
  tensegrity re-extension); specimens visibly intact throughout.
- **Scale**: anchored on free-fall arrival speed from 60 in (5.47 m/s;
  DAQ Δv 5.53/5.69 m/s corroborates) → 3407 / 2241 px/m. Cross-check: both
  framings imply the same physical specimen size (82 vs 78 mm orange
  extent). Curvature self-calibration is not available — the pixel descent
  velocity is flat to ±2 % (perspective gradient cancels the free-fall
  gain).
- **Limit**: peak specimen compression falls between capture frames
  (inside the 1–2 ms pulse) — needs ≥5000 fps DIC per the Edison synthesis.

| output | content |
|---|---|
| `figures/05_video_kinematics.png` | velocity (m/s) full-drop + descent-velocity fit, both specimens |
| `figures/06_video_impact_zoom.png` | ±40/60 ms velocity zoom: the 1–2-frame reversal |
| `figures/07_video_montage_{7xadt6,9GMQYQ}.png` | entry → contact → turnaround → rebound → brake catch → hold frames |
| `figures/video_metrics.json` | all per-video metrics + DAQ cross-references |

## Legacy preview frames (pre-download pass)

`<specimen>_maxres1/2/3.jpg` (~25/50/75 % of runtime, 1280×720 letterboxed)
and `<specimen>_poster.jpg` — the only frames available before the videos
were committed. Their frame-level observations (rig/mount/tie-down
verification, specimen intact, felt impact-zone mottling, carriage "parked
above the felt" — now explained by the brake catch) are folded into the
writeup §7.
