# Workflow / specimen photographs (extracted from repo issue & PR comments)

Real images harvested from the project's GitHub issue and PR comment history and
cropped/orientation-corrected for use in the manuscript figures
(`manuscript/manuscript-body.tex`). Phone photos were EXIF-transposed so they
render upright when embedded by `pdflatex` (which ignores EXIF orientation).

| file | used in | source |
|------|---------|--------|
| `cad-render.png`            | Fig.~2(a) (printed-prototypes) and Fig.~3 "CAD Generation" node | PR #35 comment 4513151049 (`cad/t3-prism/t3-prism-iso.png`, OpenSCAD render) |
| `multimaterial-slice.png`   | Fig.~3 "Multi-Material Slicing" node | PR #35 comment 4464541324 (Bambu Studio slice: PLA left nozzle / TPU right nozzle, prime tower) |
| `printing-in-progress.jpg`  | Fig.~3 "Dual-Extrusion FDM" node | PR #35 comment 4519769283 (Bambu Lab H2D mid-print of the T3-prism batch) |
| `printed-specimen.jpg`      | Fig.~2(b) (printed-prototypes, with callouts) and Fig.~3 "Post-Processing" node | PR #35 comment 4634008108 (single as-printed T3 prism on the workbench) |
| `printed-batch.jpg`         | (reserve; not currently placed) | PR #35 comment 4634008108 (printed batch) |
| `drop-tower.jpg`            | Fig.~3 "Dynamic \& Static Testing" node | PR #36 comment 4509083060 (bungee-assisted drop-tower base plate + accelerometer) |

(Figure numbers are for the current `manuscript.pdf`; Fig.~3 is the
fabrication/characterization workflow diagram, `figures/fab-workflow.tex`.)

Regenerate the cropped/oriented copies from the originals with
`scripts/figures/fetch_repo_photos.py` (re-downloads from the recorded comment
attachments and re-applies the same crops).

## Scripted figures (cropped and down-scaled only)

These figures are rebuilt by their scripts from the recorded sources. The
scripts only crop, rotate (EXIF transpose) and down-scale the photographs or
video frames, and draw labels in the margins. The full-size phone photos and
the video stay out of the repository (`.gitignore` excludes video files and
zip archives under `figures/` and `manuscript/`).

| file | used in | source | script |
|------|---------|--------|--------|
| `replicate-specimens-panel.jpg` | `fig:replicate-specimens` (main text, Section 3.5) | Issue #98 print-log comments 5637649574 (2026-09-11, corny1 to corny9), 6240858848, 6241852209 and 6241963239 (2026-10-17, replicate plates 1 to 3). Rows corny7, corny8, corny2; columns the batch-4 specimen and the front-row copy (copy 3) of plates 1 to 3. IDs follow `bo/replicate-study/t3-prism-replicate-print-key.csv` on `claude/issue-98-20260821-0103`; masses are parsed from the log | `scripts/figures/build_replicate_photo_panel.py` (run with `python -P`; photos cached in `/tmp/replicate-photos`) |
| `print-timelapse-plate1.jpg` | `fig:print-timelapse` (main text, Section 3.2) | YouTube [`EmCLms7-Bd8`](https://youtu.be/EmCLms7-Bd8), "TT3_01 1sne## plate" (uploaded 2026-10-12; printer file stamp 2026-10-03), the H2D chamber timelapse of replicate plate 1 and the only plate timelapse without the toolhead in view | `scripts/figures/build_print_timelapse_figure.py` |
| `timelapse/plate1-01-first-layers.jpg`, `timelapse/plate1-02-mid-height.jpg`, `timelapse/plate1-03-final-layers.jpg` | panels (a) to (c) of `fig:print-timelapse` | frames at 0.75 s, 7.0 s and 15.5 s of the same video | same script |

YouTube blocks most datacenter IP ranges, so the timelapse video was
downloaded on the lab Raspberry Pi (standalone `yt-dlp` in a scratch
directory, rate-capped, removed afterwards) and passed to the script with
`--video`. On a residential connection `--download` fetches it directly.
