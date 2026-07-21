# Slow-mo video record — 60 in / 5 felts campaign (7xadt6, 9GMQYQ)

Slow-motion videos of the two 60 in / 5 felt drop-test campaigns, posted by
@ctrhjk on PR #86 (2026-07-21):

| specimen | video | title (YouTube) |
|---|---|---|
| `7xadt6` | https://youtube.com/shorts/Nab3hfuF4Dw | "Drop test - 7xadt6 - 7-20-2026" |
| `9GMQYQ` | https://youtube.com/shorts/zkum2JlHpYk | "Drop test - 9GMQYQ - 7-20-2026" |

Channel: BYU Vertical Cloud Lab. Recorded 2026-07-20, the same evening as
the 201-capture accelerometer campaign analyzed in
[`docs/drop-test-60in-5felts-analysis.md`](../../../docs/drop-test-60in-5felts-analysis.md).

## What is committed here

**Full video download was not possible from the CI runner** (YouTube gates
both the player API and the watch page behind a sign-in/bot check for
datacenter IPs; yt-dlp with every player client, Invidious mirrors, and the
embedded player were all tried). What YouTube does serve publicly are the
auto-generated preview frames, which are real video frames:

- `<specimen>_maxres1/2/3.jpg` — frames at ~25 % / 50 % / 75 % of the video
  runtime (1280×720 letterboxed, active area x≈437–843)
- `<specimen>_poster.jpg` — the 1080×1920 poster frame

Eight frames total. Frame-by-frame analysis (impact deformation, rebound
kinematics, contact time vs the DAQ pulse width) needs the original files —
see "Enabling full video analysis" below.

## Frame-level observations

Setup, visible in both videos and consistent with the campaign READMEs:

- T3-prism specimen (orange struts, black tendons) upright on the acrylic
  plate on top of the grey drop carriage; carriage rides two vertical guide
  rails; brown-topped felt stack on the fixed base below (lighter sheets
  visible beneath the top brown sheet, consistent with the 5-sheet stack).
- Tri-axial accelerometer seated at the top vertex in the key-seat mount
  (light-grey wax visible), thin white cable routed off the top with generous slack
  (no visible cable load on the specimen). A coiled strain-relief cable
  hangs from above the carriage.
- **No bungees attached to the carriage** — confirms the bungee-removed SOP
  carried over from the input-output redesign.
- 7xadt6 close-up: a dark tether runs from a bottom node down to an anchor
  point on the plate (the specimen tie-down), and a silver puck on the
  plate to the specimen's right is consistent with the stud-mounted
  single-axis input accelerometer (CH5).

Quantitative frame comparison (9GMQYQ, 50 % vs 75 % frames, orange-strut
pixel mask + edge detection):

- Carriage bottom edge identical at y = 444 px in both frames; felt top
  edge 544 vs 540 px — the carriage is **parked at the same hold position
  (~a carriage-half-height above the felt) in both frames**, i.e. these
  frames bracket a post-drop/re-hoist hold, not free fall.
- The specimen's strut bounding box matches to ≤1 px between the two
  frames (bbox 78×125 px) — the specimen sits still on the plate with no
  whole-pixel residual motion; the only inter-frame change localizes to
  the top-vertex accelerometer/cable region (sub-strut-scale wobble).
- Specimen intact in every frame of both videos: struts straight, tendons
  taut, geometry upright — consistent with both specimens surviving their
  ~100-drop campaigns with CV ≤ 1.7 %.
- The top felt sheet shows a mottled darker zone near the impact center in
  the 9GMQYQ frames — consistent with the cumulative felt-compaction
  finding (CH5 raw spike 2.1 → 6.5 kG over the evening), though lighting
  can't be excluded from a still.

## Enabling full video analysis

To make frame-by-frame quantitative analysis possible (deformation
tracking, rebound kinematics, contact-time vs DAQ pulse width,
drop-height verification):

1. Attach the original video files directly to a PR/issue comment (GitHub
   accepts .mp4 attachments up to 10 MB), commit them to the repo, or add
   them to a release — anything fetchable without YouTube's bot gate.
2. Note the **recording frame rate** (e.g. 240 fps) and playback rate, so
   video time maps to real time.
3. Optional but valuable: a ruler or object of known size in the focal
   plane for pixel-to-mm calibration.
