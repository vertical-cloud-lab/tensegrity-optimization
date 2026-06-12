# Workflow / specimen photographs (extracted from repo issue & PR comments)

Real images harvested from the project's GitHub issue and PR comment history and
cropped/orientation-corrected for use in the manuscript figures
(`manuscript/manuscript-body.tex`). Phone photos were EXIF-transposed so they
render upright when embedded by `pdflatex` (which ignores EXIF orientation).

| file | used in | source |
|------|---------|--------|
| `cad-render.png`            | Fig.~2(a) (printed-prototypes) and Fig.~3 "CAD Generation" node | PR #35 comment 4513151049 (`cad/t3-prism/t3-prism-iso.png`, OpenSCAD render) |
| `multimaterial-slice.png`   | Fig.~3 "Multi-Material Slicing" node | PR #35 comment 4464541324 (Bambu Studio slice: PLA left nozzle / TPU right nozzle, prime tower) |
| `printing-in-progress.jpg`  | Fig.~3 "Dual-Extrusion FFF" node | PR #35 comment 4519769283 (Bambu Lab H2D mid-print of the T3-prism batch) |
| `printed-specimen.jpg`      | Fig.~2(b) (printed-prototypes, with callouts) and Fig.~3 "Post-Processing" node | PR #35 comment 4634008108 (single as-printed T3 prism on the workbench) |
| `printed-batch.jpg`         | (reserve; not currently placed) | PR #35 comment 4634008108 (printed batch) |
| `drop-tower.jpg`            | Fig.~3 "Dynamic \& Static Testing" node | PR #36 comment 4509083060 (bungee-assisted drop-tower base plate + accelerometer) |

(Figure numbers are for the current `manuscript.pdf`; Fig.~3 is the
fabrication/characterization workflow diagram, `figures/fab-workflow.tex`.)

Regenerate the cropped/oriented copies from the originals with
`scripts/figures/fetch_repo_photos.py` (re-downloads from the recorded comment
attachments and re-applies the same crops).
