# `prc1kn` slow-mo video analysis (60 in campaign) + three-structure cross-reference

Frame-by-frame kinematics of the two slow-motion videos @me-madsen attached
directly to PR #86 (2026-07-21), recorded during the
[`prc1kn` 60 in campaign](drop-test-prc1kn-60in-5felts-analysis.md), plus the
answers to the two workflow questions asked with them: **direct attachments
vs YouTube links**, and **how to use the checkerboard calibration grid**.

- Videos + Sony XML sidecars: `data/drop-tests/prc1kn-60in-5felt/video/`
- Script: `scripts/analysis/drop_test_prc1kn_video_analysis.py` (reuses the
  trackers of `drop_test_60in_5felts_video_analysis.py`)
- Figures + machine-readable metrics:
  `data/drop-tests/prc1kn-60in-5felt/video/figures/`

## 1. Time base — exact this time, thanks to the XML sidecars

The Sony non-real-time metadata XMLs posted with the videos state the
capture rate outright — no more inferring it from PR comments:

```xml
<VideoFrame videoCodec="AVC_1920_1080_HP@L41" captureFps="959.04p" formatFps="23.98p"/>
<Device manufacturer="Sony" modelName="DSC-RX100M4"/>
<RecordingMode type="slowAndQuickMotion"/>
```

So real time = capture frame / **959.04** (the 7xadt6/9GMQYQ pass assumed
960; the difference is 0.1 %). The attached mp4s are 1080×1920 / 30 fps
portrait re-encodes of the 23.98p camera clips (crop + trim), so the same
23.98→30 pulldown-duplicate removal applies: 23.5 % / 21.3 % duplicates
detected and removed (textbook ~1-in-5 plus trim edges), the surviving
frames being camera capture frames. Recording timestamps: 15:30 and 15:58
MDT — i.e. the videos were shot ~5.5 h *before* the 20:56–22:06 DAQ
campaign, so they document the setup/rehearsal drops, not two of the 101
logged captures. Nothing in the kinematics depends on that, but drop-level
video↔DAQ pairing is not possible.

## 2. Kinematics

Same method as the 7xadt6/9GMQYQ pass: orange-strut HSV segmentation +
correlation trackers, spatial scale anchored on free-fall arrival from
60 in (5.47 m/s; the DAQ plate Δv of 5.78 m/s corroborates). Video 2's tan
OSB backdrop leaks into the permissive orange band (567k px vs the
specimen's ~18k), so it runs with a tighter saturation floor — the leak's
flicker otherwise out-correlates the specimen.

| | prc1kn drop 1 | prc1kn drop 2 | 7xadt6 | 9GMQYQ |
|---|--:|--:|--:|--:|
| deceleration bracket | 1 frame ≈ **1.0 ms** | ≤2 frames ≈ **2.1 ms** | 1.0 ms | 1.0 ms |
| DAQ TOP pulse width | 1.57 ms | 1.57 ms | 1.59 ms | 1.6 ms |
| top-vertex snap-back / impact speed | 1.05 † | 0.69 | 0.70 | 0.68 |
| sustained rebound / impact speed (e*) | 0.45 | 0.47 | 0.35 | 0.43 |
| brake deceleration | 3.7 g | 3.4 g | 2.1 g | 2.4 g |
| brake catch after impact | +79 ms, 150 mm | +76 ms, 145 mm | +89 ms, 130 mm | +86 ms, 150 mm |
| specimen-plane scale (free-fall anchor) | 3608 px/m | 3576 px/m | — | — |

† drop 1's snap-back window contains contact-adjacent correlation spikes
(motion-blur mislocks up to ~40 px/frame are visible through its descent),
so 1.05 should be read as "≈0.7, possibly inflated" — drop 2's clean 0.69
matches the other two specimens.

Highlights:

- **The video corroborates the DAQ record again**: arrival at free-fall
  speed, a single 1–2-frame deceleration (bracketing the DAQ's 1.57 ms
  CFC-pulse), one clean shock per drop, anti-rebound brake catch ~130–150 mm
  above the stack, specimen visibly intact and elastic throughout.
- **Internal consistency check passed**: the two videos were anchored to
  the free-fall speed *independently*, and both land on the same
  specimen-plane scale (3608 vs 3576 px/m, 0.9 % apart) while their grid
  scales differ by 30 % — exactly what a fixed camera + moved grid should
  produce. The anchor (and the 959.04 fps time base) would have to be wrong
  in the same proportion in both videos for this to be coincidence.
- The **brake is set harder than on 2026-07-20** (3.4–3.7 g vs 2.1–2.4 g,
  catch ~10 ms earlier). Same single-shock behavior, just a firmer catch.
- `prc1kn`'s carriage rebound (e* 0.45–0.47) is higher than 7xadt6's
  (0.35) / 9GMQYQ's (0.43), but this is a whole-collision property
  dominated by the impact stack — and `prc1kn`'s stack, while the same
  4-felt + 1-cardboard composition used in every "5 felt" session
  (confirmed by @me-madsen on PR #86), carried ~200 more drops of
  compaction and was measurably stiffer — so it cannot be attributed to
  the structure.

## 3. Cross-reference: which structure is the better energy absorber?

The [accelerometer answer](drop-test-prc1kn-60in-5felts-analysis.md) (mock
three-way comparison, ~95 stabilized drops each) is:

| rank | specimen | T = TOP/CH5 |
|--:|---|--:|
| 1 | `prc1kn` | 1.011 |
| 2 | `9GMQYQ` | 1.027 |
| 3 | `7xadt6` | 1.034 |

i.e. `prc1kn` is the *least-bad* transmitter — none of the three actually
attenuates (all T > 1). **The video record is consistent with that reading
and adds no contradiction, but it cannot independently reproduce the
ranking**, for two structural reasons:

- The differences being ranked are 1.6–2.3 % in a *filtered peak-G ratio*.
  The video's specimen-response observables (snap-back ratio ≈ 0.7 for all
  three; no visible plastic deformation for any) are identical across
  specimens at single-drop resolution — which is itself corroboration:
  all three pass the shock essentially 1:1, exactly what T ≈ 1.01–1.03
  says.
- The one video metric that *does* differ (carriage e*) is stack-dominated,
  and the stack's wear state changed between campaigns (§2 — same
  composition, ~200 more drops of compaction), so it is confounded in
  precisely the way the accelerometer writeup's caveat predicted.

Bottom line: for ranking energy absorbers, trust the DAQ transmissibility
(with its stack/mount caveats); use the video for what it is good at —
verifying rig physics, pulse duration, specimen integrity, and setup SOP
compliance. A video-side *deformation* metric (peak compression during the
pulse) would need ≥5000 fps DIC, as the Edison synthesis recommended: at
959 fps the entire pulse spans 1–2 frames.

## 4. The calibration grid: does it help, and how to place it

**It helps — but as deployed it must not be used directly.** Both videos
have the 20 mm checkerboard taped *behind* the drop axis, at a different
depth in each. Measured (autocorrelation over 60–80 column strips, period
IQR 0.3–0.4 px, i.e. sub-0.5 % measurement noise):

| | grid scale | specimen-plane scale | speed error if grid used directly |
|---|--:|--:|--:|
| video 1 (grid near tower) | 2093 px/m | 3608 px/m | **+72 %** |
| video 2 (grid on far backdrop) | 1612 px/m | 3576 px/m | **+122 %** |

Because the grid sits 1.7× / 2.2× the camera→specimen distance, its px/mm
under-reads specimen motion by the depth ratio — a specimen speed computed
against the grid would come out 72 % / 122 % too high. Parallax is the
*entire* error budget; the grid itself is measured to <0.5 %.

Recommendations, in order of preference:

1. **Put the scale in the specimen's plane, riding with the carriage**: a
   20 mm-pitch high-contrast strip on the *edge of the acrylic plate* (or
   carriage side rail) facing the camera. It then shares the specimen's
   depth at every height, calibrates every frame, and makes the analysis
   independent of the free-fall assumption — that would turn the current
   "assumed 5.47 m/s arrival" into a measured quantity, including any rail
   friction loss.
2. **Static scale in the drop plane**: a vertical ruler/strip taped to a
   guide rail (the rails are within ~1 cm of the specimen plane). Nearly as
   good; doesn't move with the specimen but kills the depth mismatch.
3. **If the board must stay in the background** (it is useful as a
   uniform backdrop): keep it, but measure and log two distances per
   session — camera→drop-axis and camera→grid — so scale can be corrected
   by their ratio. Also avoid tan/orange backdrops behind it (video 2's OSB
   fights the orange-strut tracker; video 1's white/grey wall is ideal).
4. Keep the camera's optical axis horizontal and square to the tower, at
   impact height; the checkerboard (vs a plain ruler) then also supports a
   one-off lens-distortion calibration if we ever want sub-percent
   photogrammetry.

## 5. Attachments vs YouTube links

**Direct attachments are strictly better on every axis, please keep doing
that:**

- *Reliability*: YouTube blocks downloads from CI datacenter IPs (the
  7xadt6/9GMQYQ pass got only 8 preview frames after trying 8 player
  clients + mirrors); the GitHub attachments downloaded first try.
- *Accuracy*: no YouTube re-compression pass, and the **XML sidecars are
  the single most valuable upload** — they replaced last time's fps
  detective work with a stated 959.04 fps.
- *Effort*: minutes less per analysis, no frame-recovery heuristics.

One step better still: attach the **camera-original files** (the 1920×1080
23.98p clips the XMLs describe, plus the XMLs). The portrait uploads were
crop + 30 fps re-encodes, which (a) discard horizontal field of view and
(b) re-introduce pulldown duplicates that must be detected and stripped.
The originals are one-capture-frame-per-file-frame — zero time-base
ambiguity. If a file exceeds the upload limit, trim to ±1 s around impact.

## 6. Caveats

- Two drops, both from the rehearsal window (§1) — not paired to specific
  DAQ captures; stack state at recording time is between "fresh" and the
  logged session's.
- Spatial scale still rests on the free-fall-arrival anchor (§2's two-video
  consistency check supports it; a plate-mounted scale per rec. 1 would
  retire the assumption).
- Drop 1's snap-back ratio is contaminated by contact-adjacent mislocks
  (†); drop 2's tighter HSV band fragments the mask, so its
  connected-component "static height" (19 mm) is a fragment, not the
  specimen — neither number feeds any conclusion.
- Grid parallax percentages are per-session geometry; they change whenever
  the camera or grid moves.
