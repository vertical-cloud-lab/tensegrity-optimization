# Panels of the overview loop (`fig:overview`, `figures/overview-loop.tex`)

Built by `scripts/figures/build_overview_photos.py` (crops) and
`scripts/figures/build_design_space_figure.py` (the Initialize drawing),
from the downscaled sources in `../overview-src/` (longest side at most
1800 px, EXIF orientation applied). Rebuild with `make figure-overview`.

| panel file | source copy in `overview-src/` | original |
|---|---|---|
| `initialize-design-space.pdf` | (drawn) | `build_design_space_figure.py`, mid-range prism of the five-variable box |
| `design-bo-panel.png` | `../../overview-updated.png` | the Bayesian-optimization panel of the proposal overview, cropped unchanged |
| `make-plate-render.jpg` | `batch4-plate-render.png` | `bo/t3-prism-bo-round4-plate.png` at 9fba359 on `claude/issue-98-20260821-0103`, posted in PR #102 comment 5591924787 (2026-09-08); an OpenSCAD render of the batch-4 plate (no Bambu Studio render of round 4 exists) |
| `make-painted-supports.jpg` | `painted-supports-slice.png` | PR #35 comment 5110159623 (me-madsen, 2026-07-28), "The applied supports": the slicer shows the TPU tendon in orange and the hand-painted PLA support wall in black |
| `make-h2d-midprint.jpg` | `h2d-midprint-replicate-plate1.jpg` | frame at 7.0 s of YouTube `EmCLms7-Bd8`, the H2D timelapse of replicate plate 1 (frame extracted on `claude/request-d-replicate-figures-20261027` at 532461f) |
| `test-taped-batch.jpg` | `taped-batch2.jpg` | PR #102 comment 5401263050 (sgbaird, 2026-08-24), IMG_0431: batch 2 (r2d2c1 to r2d2c9) on a taped 3 x 3 grid |
| `test-carriage.jpg` | `carriage-specimen-mdt6ja.jpg` | slide 23 of the group IDETC 2026 deck (`ppt/media/image34.jpeg`, photo dated 2026-08-06); the strut label reads mDT6Ja, i.e. specimen mdt6ja of the July print-defects study, not a campaign specimen (to be confirmed, see the `\todo` under `fig:overview`) |

`../corny7-asprinted.jpg` (panel (c) of `fig:design-space`) is cropped by the
same script from `overview-src/corny7-asprinted.jpg`, the corny7 photo in
issue #98 comment 5637649574 (ctrhjk, 2026-09-11).
