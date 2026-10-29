# Photo and video index for the T-3 print and drop-test process

This document collects the photo and video documentation of the physical
workflow, from slicing and printing through support removal, labeling,
weighing, drop-tower setup, and data recording. Every item links to the GitHub
comment it was posted in (so the surrounding discussion is one click away) and
credits the person who captured it. Items are grouped by process stage and
listed chronologically within each stage.

How this index was assembled (2026-08-24): all issue and PR bodies and
comments in this repository were fetched through the GitHub API (paginated,
repo wide, including PR review comments) and scanned for `user-attachments`,
`user-images`, YouTube, BYU Box, and OneDrive links. That sweep found 913
media URLs posted by lab members across 30 threads. Media files committed to
git were located by listing every branch of a blobless mirror. Bulk uploads
(for example, 30 to 60 per-drop videos in one comment) are indexed here as a
single entry with a count rather than one line per file.

A note on link types: a GitHub link ending in a bare UUID under
`github.com/user-attachments/assets/` is a photo or a video depending on what
was uploaded; each entry below says which. BYU Box and YouTube links carry the
raw or long-form video that GitHub attachments would have re-encoded (see
[the upload convention](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5040076463)
Sterling set for PR #86: raw high-speed video goes to Box, viewable copies go
to YouTube).

## 1. Slicing and support design

| What it shows | Who / when | Links |
|---|---|---|
| First automatic-support experiments: failed print next to first successful PETG print; scale 1.3x makes Bambu add supports to the top strings | @me-madsen, 2026-05-12 | [2 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4426810002), [2 support screenshots](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4432773923) |
| Manually painted supports, first attempt: too much mass, TPU tendon fully encased in PLA support | @achris0520 and @ctrhjk (ported by @sgbaird), 2026-05-20 | [1 photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4502096572), [7 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4502126554) |
| The thin-paint recipe that worked: brush sizes, bottom-view painting pattern, and the first good print that came off the plate | @achris0520 (ported by @sgbaird), 2026-05-20 | [3 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4502140147) |
| Written manual-support instructions plus the original manually sliced gcode | @achris0520, 2026-05-22 | [comment with zip](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4520949470), mirrored in [issue #65](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/65) |
| 12-minute screen recording (no audio) of the manual support painting walkthrough, with start and end files attached | @sgbaird walked through by @achris0520, 2026-05-20 | [video](https://youtu.be/esYGqPv2fb0), [comment with files](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4502171087) |
| Multi-material import fixed: parts split and assignable, spacing screenshots | @sgbaird, 2026-05-20 | [2 screenshots](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4503427854) |
| Automated pillar supports (PR #66): render check that pillars touch the TPU cables, video review of connection-point diameter, and the failure where supports were not touching | @sgbaird, 2026-05-26 to 2026-06-12 | [2 screenshots](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/66#issuecomment-4546383138), [video](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/66#issuecomment-4673401417), [failure photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/66#issuecomment-4693738004) |
| Bucket-fill trick for painting supports on the segmented STLs | @achris0520, 2026-07-09 | [screenshot](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4930026388) |
| Proposed 3-pillar cage around each tendon (hand sketches) and the edge supports actually applied | @me-madsen, 2026-07-21 and 2026-07-28 | [sketches](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-5040197700), [applied supports screenshot](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-5110159623) |
| BO round-1 plate with manual supports and print presets (the file behind the batch printed 2026-08-21 to 08-24) | @achris0520, 2026-08-21 | [comment with zip](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-5374553137) |

## 2. Printing in progress

| What it shows | Who / when | Links |
|---|---|---|
| First PETG print running on the H2D | @sgbaird-alt, 2026-05-08 | [photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4408792220) |
| Multi-material print starting | @sgbaird-alt, 2026-05-15 | [photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4464541324) |
| Sobol batch plate mid-print, about 15 hours total | @sgbaird (screenshot from @achris0520), 2026-05-22 | [2 screenshots](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4519769283) |
| TPU tendon moving under the nozzle during printing (the wobble problem) | @me-madsen, 2026-07-21 | [Box video](https://byu.box.com/s/r6zw5hffqbv9opx8apoqyi434hgz598r) |
| Supports themselves wobbling when half TPU (why the switch to all-PLA supports) | @achris0520, 2026-06-24 | [video](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4794280199) |
| Timelapse of a print with the surrounding edge supports | @me-madsen / @achris0520, 2026-07-28 | [YouTube](https://youtu.be/2wneIJc1WV8) |
| Stabilized tendons printing with almost no visible wobble | @me-madsen, 2026-07-28 | [video](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-5110159623) |
| Timelapse after tightening support/object xy distance to 0.2 mm (the bpx68c print) | @me-madsen / @achris0520, 2026-07-29 | [YouTube](https://youtu.be/xVBunPal9Kw) |
| Short print clips | @achris0520, 2026-06-24 and 2026-07-28 | [short](https://youtube.com/shorts/KGSePOjRa_I), [comparison short of the last 4 prints](https://youtube.com/shorts/n7wlCLvXLmI), [Box video of the same 4 prints](https://byu.box.com/s/d8kga3d5djcrvkiys7non9thdhvg413z) |
| Polished print timelapse used for the IDETC talk | posted by @sgbaird, 2026-07-31 | [YouTube](https://www.youtube.com/watch?v=nQNmi-NiL5I) |

## 3. Print failures and printer troubleshooting

| What it shows | Who / when | Links |
|---|---|---|
| Spaghetti failure on an early print | @sgbaird-alt, 2026-05-08 | [photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4409344661) |
| Bad stringing on one specimen of the first batch | @sgbaird, 2026-05-22 | [photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4521380707) |
| Tendon print-angle comparison: parallel, 45 degree, and perpendicular tendons (issue #61) | @me-madsen, 2026-05-22 | [3 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/61) |
| Failed open-ended print that still absorbs energy (issue #68) | @me-madsen, 2026-05-29 | [2 photos + 3 videos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/68) |
| All-PLA supports fused to the structure (auto spacing kicked in) | @ctrhjk with note from @achris0520, 2026-06-24 | [3 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4794006620) |
| Humidity bubbles in TPU; first success after drying below 8% RH; flush-tower spaghetti | @achris0520, 2026-06-29 | [4 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4835595840) |
| TPU clog mid-print, then success at 235 to 240 C | @achris0520, 2026-07-04 | [photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4884103569) |
| TPU assist module up and running | @achris0520 / @ctrhjk, 2026-07-08 | [photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4910591253) |
| Bubbles still on diagonal tendons after new TPU roll (over 10% RH) | @ctrhjk, 2026-07-13 to 07-15 | [7 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4960119866), [5 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4983604148) |
| Tendon imperfection close-up that motivated the support cage | @me-madsen, 2026-07-21 | [photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-5040197700) |
| Left-extruder jam saga (issue #96): error state, gap-print defects with direction marked, black vs white filament A/B prints | @me-madsen, 2026-08-06 | [7 photos in the issue body](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/96) |
| AMS slot A/B testing to isolate the jam | @me-madsen, 2026-08-06 to 08-10 | [2 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/96#issuecomment-5209802244), [resolution photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/96#issuecomment-5245877618) |
| TPU flow tapering off over a print (jam recurrence) | @me-madsen, 2026-08-17 | [4 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/96#issuecomment-5318367917), [4 photos of the PLA test prints](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/96#issuecomment-5319246036) |
| Extruder disassembly and the white PLA debris found inside; TPU high-flow 0.6 mm nozzle install; cold pull | @me-madsen, 2026-08-17 | [3 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/96#issuecomment-5321284844), [TPU assist module internals](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/96#issuecomment-5319638577), [consistent test strip](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/96#issuecomment-5319623743) |
| Jam declared resolved: an exquisite print, with the two minor removal defects photographed | @me-madsen, 2026-08-18 | [3 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/96#issuecomment-5332072667) |

## 4. Removing prints and supports

| What it shows | Who / when | Links |
|---|---|---|
| Support removal for one of the first three specimens | @sgbaird, 2026-05-22 | [YouTube](https://youtu.be/V86ctTIHKDY) |
| Curated support-removal clip (trimmed for slides) | committed on the PR #84 branch | [`presentation/media/clip-support-removal.mp4`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/claude/issue-83-20260715-2018/presentation/media/clip-support-removal.mp4) |
| Removal difficulty notes for the tight-support recipe (10 to 20 minutes per model, tendon-break risk) with photos of bpx68c on the plate | @me-madsen, 2026-07-29 | [2 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-5121885731) |
| Defects introduced during removal: strings peeled off bottom tendons (ebdna8, 6nheas) and the trimmed strings on the #96 test print | @me-madsen, 2026-08-13 to 08-19 | [ebdna8](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5285048840), [6nheas](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5348663481), [trimmed defects](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/96#issuecomment-5332072667) |

## 5. Labeling and identification

| What it shows | Who / when | Links |
|---|---|---|
| The ID scheme: label-maker wrap on a strut, 6-character lowercase IDs, how to generate them | @sgbaird, 2026-05-22 | [instructions](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4522905787) |
| A printed label placed on a specimen | @me-madsen, 2026-08-18 | [photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/96#issuecomment-5332026555) |
| The sliced plate names that map print IDs to Sobol specs (the zip behind this PR's key) | @me-madsen, 2026-08-21 | [comment with zip](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5363921562) |
| Visual key for the whole batch | this branch | [`bo/t3-prism-bo-batch-print-key.png`](../bo/t3-prism-bo-batch-print-key.png) |

## 6. Weighing and the T-3_01 print log (issue #98)

The scale (accurate to 0.01 g, borrowed from the Smash Lab):
[photo by @me-madsen, 2026-08-10](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/97#issuecomment-5245151502).
Infill and hollow TPU lock-ball documentation:
[2 cutaway photos by @me-madsen in issue #85, 2026-08-18](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/85#issuecomment-5335315349).

Per-specimen log entries, each with a photo, mass, RH%, and defect notes (all
photos by @me-madsen). Spec mapping follows
[`bo/t3-prism-bo-batch-print-key.csv`](../bo/t3-prism-bo-batch-print-key.csv):

| Print ID | Spec | Log entry with photo | Date |
|---|---|---|---|
| bag26v (official per comment) | 08 | [entry](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5270381244) | 2026-08-12 |
| dea4ls (official per .3mf) | 08 | [same entry](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5270381244) | 2026-08-12 |
| ghmj4y | 08 | [same entry](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5270381244) | 2026-08-12 |
| 1zm8rv | 06 | [entry](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5270410479) | 2026-08-12 |
| ebdna8 | 03 | [entry](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5285048840) | 2026-08-13 |
| bpx68c | S0 reference | [entry](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5334673614) | 2026-08-18 |
| autv5r | 02 | [entry](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5347041332) | 2026-08-19 |
| ajhby6 | 07 | [entry, 2 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5347204673) | 2026-08-19 |
| 9hhbkp | 00 | [entry](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5347324349) | 2026-08-19 |
| 6lhxfy | 01 | [entry](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5348529679) | 2026-08-19 |
| 6nheas | 05 | [entry](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5348663481) | 2026-08-19 |
| nvxsrv | 04 | [entry](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5348809661) | 2026-08-19 |

Group photo of the complete batch (all Sobol specs plus the S0 prism):
[photo by @me-madsen, 2026-08-19](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5348907091).
Note: `amdjwm` was drop-tested in the round-1 campaign but has no #98 log entry,
photo, or spec mapping.

## 7. Drop tower hardware and setup

| What it shows | Who / when | Links |
|---|---|---|
| Lansmont M23 shock tester brochure and the Polytec Qtec laser vibrometer identification | @Jeffrayhill1, 2026-05-08 | [PDF](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/27#issuecomment-4408498939) |
| Lab walkthrough video with Jeff covering the tower, accelerometer mounting, high-speed camera, shaker, and slug rig | recorded 2026-05, screenshots annotated by @sgbaird 2026-05-21 | [YouTube](https://youtu.be/RNjpAmWWmkQ), [4 screenshots](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4509083060), [5 screenshots](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4509305026) |
| TP4 data-acquisition manuals (quick start + user's guide) | @ctrhjk, 2026-05-21 | [PDFs](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4513715511) |
| Specimen cage design: acrylic plates and guide rods (drawing + parts), and the finished cut-and-threaded rods | @me-madsen and @ctrhjk, 2026-05-22 to 05-23 | [design, 2 images](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4521516377), [rods photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4523574847) |
| First drop tests: specimen separating from the plate, 25 degree tilt problem | video posted by @sgbaird, 2026-05-26 | [video](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4545983664) |
| Plate tolerance comparison videos (loose vs tight, with and without specimen) | @me-madsen and @ctrhjk, 2026-05-26 | [3 videos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4547152777), [4 videos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4547220915) |
| Bungee retention concept for cyclic testing | @me-madsen, 2026-05-28 | [image + video](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4568826378) |
| Felt stack compression over time (issue #88) | @me-madsen, 2026-07-29 | [photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/88#issuecomment-5121703763) |
| New polyurethane sheets sticking to the drop block, and the felt-debris fix | @me-madsen, 2026-07-30 | [video + photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/88#issuecomment-5134564783) |
| Guide-rod locking pin snapped during mat calibration (issue #92), the safety interlock box, and the machined screwdriver replacements | @me-madsen, 2026-07-30 to 08-12 | [3 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/92), [2 interlock photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/92#issuecomment-5183508899), [replacement](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/92#issuecomment-5198212336), [both pins done](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/92#issuecomment-5272416211) |
| Release hook sticking open, before and after WD-40 (PR #86) | @me-madsen, 2026-07-22 | [2 videos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5051515083) |
| High-speed camera and its safety-motivated remote trigger (issue #91); camera remote delivered | @sgbaird and @me-madsen, 2026-07-30 and 08-05 | [3 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/91), [remote photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/91#issuecomment-5198290266) |
| Wi-Fi adapter installed in the tower computer (issue #90) | @me-madsen, 2026-08-05 | [2 photos](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/90#issuecomment-5198260416) |

## 8. Accelerometer mounting and tuning

| What it shows | Who / when | Links |
|---|---|---|
| Tri-axis vs single-axis disagreement: 12 slow-motion drop videos with their CSVs (issue #71) | @me-madsen and @ctrhjk, 2026-06-04 | [issue body](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/71), [9 labeled graphs](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/71#issuecomment-4633820479) |
| Sensor placement photo (both accelerometers on the metal load) and height-sweep drop videos, 5 per height at 10/15/20 inches (PR #74) | @ctrhjk, 2026-06-09 to 06-10 | [placement photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/74#issuecomment-4663572321), [~20 videos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/74#issuecomment-4664234492), [repeat with ch5 added](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/74#issuecomment-4673864934) |
| Hot-glue mount on a vertex vs accelerometer above the acrylic plate | @ctrhjk, 2026-06-23 | [2 photos + 16 per-drop videos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4783408053) |
| Vertex key-seat housing: wax securing, accelerometer falling off mid-drop (video), cable tie-off fix, taping the housing entrance | @ctrhjk, 2026-06-29 to 07-08 | [wax photo + failure video](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4837240958), [wax added](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4838901017), [cable fixed to rod](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4870839517), [taped entrance](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4918818168) |
| Housing sizing iterations: too short, rotating in oversized pocket, finally a perfect fit | @sgbaird and @ctrhjk, 2026-07-01 to 07-13 | [too short](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4848946178), [halfway in](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4867769577), [rotating](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4895789291), [6 mm vs 6.1 mm](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4927872672), [fits](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4960119866) |
| Two tri-axis setup (top and bottom housings) on specimen RW5F61 | @ctrhjk, 2026-07-03 | [3 photos + 30 drops](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4872786485) |

## 9. Protocol development drop tests (PR #67 and PR #82)

These comments each carry a per-drop set of slow-motion videos and CSVs; the
counts below are the media totals in each comment.

| Test | Who / when | Links |
|---|---|---|
| Clip-height sweep (0.5 to 2 inches above the plate), 8 videos | @ctrhjk, 2026-06-24 | [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4794351098) |
| Accelerometer sanity check on the bottom plate | @ctrhjk, 2026-06-24 | [photo + video](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4794438322) |
| Input-output accelerometer design, 4 specimens, 5 drops each (47 media) | @ctrhjk, 2026-06-25 | [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4804858562) |
| Fixity validation of the four-cord method, 8 videos | @ctrhjk, 2026-06-26 | [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4813080485) |
| Burn-in wax drift test, 5 videos | @ctrhjk, 2026-07-01 | [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4849968630) |
| 30-drop and 50-drop automated drift calibrations (auto-drop rig photo) | @ctrhjk, 2026-07-02 | [30 drops](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4861564582), [50 drops](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4870839517) |
| 100 drops, 7-channel setup | @ctrhjk, 2026-07-06 | [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4897632381) |
| 200 drops on 7xadt6 (specimen photo) | @ctrhjk, 2026-07-13 | [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4961087426) |
| 5 in vs 10 in drop-height comparison, 30 drops each | @ctrhjk, 2026-07-14 | [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/82#issuecomment-4973983998) |
| 500-drop endurance attempts (overload at drop 256, then a full 500 with video) | @ctrhjk, 2026-07-15 to 07-16 | [attempt](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/82#issuecomment-4983665345), [full run + YouTube](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/82#issuecomment-4996703024), [video](https://youtu.be/uqn3qnJPfN8) |
| Saturation test: drop height vs felt-sheet count matrix | @ctrhjk, 2026-07-17 | [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/82#issuecomment-5007713855) |

## 10. Running a session and recording data

| What it shows | Who / when | Links |
|---|---|---|
| The drop-test procedure end to end, as set up at the time | @me-madsen, 2026-05-29 | [YouTube](https://youtu.be/dL2djikfJFE) |
| Setting up the tower for automated drops (cyclic testing) | @me-madsen, 2026-05-29 | [YouTube](https://youtu.be/TXerxMYEsDM) |
| TP4 channel settings reference photo taken after the settings were accidentally cleared, with before/after validation data | @me-madsen, 2026-08-19 | [photo + Box links](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5347154331) |
| Creating and switching TP4 databases when they fill up | @me-madsen, 2026-08-21 | [YouTube](https://youtu.be/BSK_UcERTVw) |
| Raw-video upload convention: raw to Box, viewable to YouTube, avoid comment attachments | @sgbaird, 2026-07-21 | [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5040076463), shared [Box folder](https://byu.box.com/s/kkhmvnj9ni19b57dryk3gdroqrp5uf0b) |
| Guide-rod cleaning and greasing effect on impact velocity (5 drops before, 5 after) | @me-madsen, 2026-08-10 | [Box data](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5246421075) |

## 11. Round-1 campaign measurements and videos (PR #86)

| What it shows | Who / when | Links |
|---|---|---|
| Slow-motion drops of 7xadt6 and 9GMQYQ | @ctrhjk, 2026-07-21 | [shorts, 2 links](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5036908261) |
| prc1kn drop videos with the 20 mm calibration grid in frame, plus camera XML metadata | @me-madsen, 2026-07-21 | [2 videos](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5039978703) |
| prc1kn 100-drop session video data | @ctrhjk, 2026-07-22 | [Box folder](https://byu.box.com/s/ncvfn5shhg1ignoibg1c3wd03p31p6c2) |
| Print-defect sensitivity study: 5 same-design specimens, data + 15 slow-motion clips | @me-madsen, 2026-07-30 and 08-03 | [data folder](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5136111762), [clips folder](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5172089094) |
| Felt vs polyurethane and PU-configuration comparisons | @me-madsen, 2026-07-30 | [felt vs PU](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5134418379), [PU configs](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5136470475) |
| Mat-arrangement blind study explainer video and the two data folders (known and randomized order) | @me-madsen, 2026-08-06 | [video + folders](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5199261361), [key verification photo](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5209909579) |
| The round-1 campaign data drop: per-specimen Box folders for 8 of 9 specimens (60 in, 101 drops each) | @me-madsen, 2026-08-21 | [comment with all links](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5364260352) |

## 12. Process media committed to git branches

Curated or snapshotted copies of the media above, already inside the
repository:

- PR #86 branch `copilot/add-drop-test-protocol-again`,
  [`data/drop-tests/`](https://github.com/vertical-cloud-lab/tensegrity-optimization/tree/copilot/add-drop-test-protocol-again/data/drop-tests):
  slow-motion mp4s and poster frames for 7xadt6, 9GMQYQ, and prc1kn
  (`60in-5felts-validation/video/`, `prc1kn-60in-5felt/video/`), a burn-in-wax
  example drop (`burn-in-wax/video-example/drop5.mp4`), and the TP4 settings
  photo (`calibration-check/tp4-settings-2026-08-18.jpg`).
- PR #84 branch `claude/issue-83-20260715-2018`,
  [`presentation/media/`](https://github.com/vertical-cloud-lab/tensegrity-optimization/tree/claude/issue-83-20260715-2018/presentation/media):
  trimmed clips ready for slides, including `clip-print-timelapse.mp4`,
  `clip-support-removal.mp4`, `clip-drop-afar.mp4`, `clip-drop-highspeed.mp4`,
  `clip-drop-phone-audio.mp4`, and `clip-our-slomo-drop.mp4`, each with a
  poster frame.
- Manuscript branch `copilot/vertical-cloud-labtensegrity-optimization`,
  [`figures/photos/`](https://github.com/vertical-cloud-lab/tensegrity-optimization/tree/copilot/vertical-cloud-labtensegrity-optimization/figures/photos):
  `drop-tower.jpg`, `printing-in-progress.jpg`, `printed-batch.jpg`,
  `printed-specimen.jpg`.
- This branch: [`bo/figures/`](../bo/figures) (analysis figures) and
  [`bo/t3-prism-bo-batch-print-key.png`](../bo/t3-prism-bo-batch-print-key.png).

## 13. Outreach and presentation captures of the process

- Group photo of printed structures and a trimmed drop-test video prepared for
  reviewer outreach, posted by @sgbaird on 2026-06-05:
  [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/41#issuecomment-4633995059).
- The photo and video @ctrhjk attached to the outreach email on 2026-07-14:
  [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/41#issuecomment-4972494682).
- Wide-angle video of a drop test, posted by @sgbaird on 2026-07-31 for the
  IDETC slides:
  [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/84#issuecomment-5146294908).
- Practice presentation recording (2026-08-07 exchange):
  [YouTube](https://youtu.be/M4u7qwBbTxM), and the slide walkthrough of
  2026-08-20: [YouTube](https://youtu.be/-0qPEmmgSBA).

## 14. Known gaps

- Slow-motion videos for the round-1 Sobol campaign sessions were still being
  uploaded as of @me-madsen's
  [2026-08-21 comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86#issuecomment-5364260352)
  ("Slo-mo video data will take me a little more time to upload"); no later
  comment posts them.
- `amdjwm` has drop data but no photo, mass log entry, or spec mapping in
  issue #98.
- The BO round-1 (second batch) prints finished on 2026-08-24 but have not
  been removed from the plate, ID'd, or photographed yet, per @me-madsen's
  note relayed in
  [PR #102](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/102#issuecomment-5398179948).
- No photo or video documents the label printing step itself (the label maker
  in use); the closest items are the ID-scheme instructions and the placed
  label photo in section 5.
