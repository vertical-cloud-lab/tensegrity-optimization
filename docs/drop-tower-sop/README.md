# Drop tower SOP template

Word template for the drop tower standard operating procedure, requested in
[issue #115](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/115#issuecomment-6511037439).

| File | What it is |
| --- | --- |
| [`drop-tower-sop-template.docx`](drop-tower-sop-template.docx) | The template to edit. Checklists come first, then a table of contents, then one section per required item (procedure, how it is verified, stop conditions), an incident register, log forms and sign-off. |
| [`drop-tower-sop-template-preview.pdf`](drop-tower-sop-template-preview.pdf) | A LibreOffice rendering of the same file, for a quick look without Word. It is not updated when the `.docx` is edited by hand. |
| [`figures/`](figures/) | The photos and figures placed in the template (sources below). |
| [`../../scripts/build_drop_tower_sop.py`](../../scripts/build_drop_tower_sop.py) | The script that generated the template. |

## Editing

- Text in gray brackets is a placeholder. Everything else is a draft taken from the repository
  records and general drop-test practice, and needs checking against the machine, the Lansmont
  manuals and the supervisor before approval.
- To edit together, upload the `.docx` to OneDrive or Teams and share it, or pass it back and
  forth here. Once hand edits start, the `.docx` is the master copy: re-running the script
  overwrites it.
- Appendix A of the template maps every item in the request to the section that covers it.
- After editing, update the table of contents (right-click it, Update Field).

To regenerate from scratch (`pip install python-docx pypdf`, LibreOffice for `--render`):

```bash
python scripts/build_drop_tower_sop.py --render   # .docx, TOC page numbers, PDF preview
```

## Figure sources

| Figure | File | Source |
| --- | --- | --- |
| 1 | `workspace-and-storage-cb152a-2026-10-13.jpg` | Four photos by Marcus Madsen, [issue #115 comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/115#issuecomment-6150496994), 2026-10-13, combined into one panel |
| 2 | `lansmont-m23-vendor-photo.jpg` | Lansmont Corp., [M23 data sheet](https://www.lansmont.com/sites/default/files/2025-10/M23%20Data%20Sheet.pdf) (October 2025), via [`equipment/lansmont-m23/images/`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/05b6344/equipment/lansmont-m23/images/SOURCES.md) |
| 3 | `prepared-setup-example-mdt6ja.jpg` | Slide 23 of the group IDETC 2026 deck, photo dated 2026-08-06, via [`figures/photos/overview-src/`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/47db4b1/figures/photos/overview/README.md) |
| 4 | `console-key-switch-do-not-operate-2026-08-04.jpg` | Marcus Madsen, [issue #92 comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/92#issuecomment-5183508899), 2026-08-04, cropped |
| 5 | `guide-rod-locking-pins-issue92.jpg` | Marcus Madsen, [issue #92](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/92): (a) and (c) from the issue body, 2026-07-30; (b) from the [closing comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/92#issuecomment-5272416211), 2026-08-12; cropped and combined |
| 6 | `carriage-table-base-accelerometer.jpg` | [Issue #36 comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4509083060), via [`figures/photos/drop-tower.jpg`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/38f7171/figures/photos/README.md) |
| 7 | `cable-routing-and-failure.jpg` | (a) Jinkwan Han, [PR #67 comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4870839517), 2026-07-02; (b) Marcus Madsen, [issue #115 comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/115#issuecomment-6277017048), 2026-10-19 (also on its own as `broken-accelerometer-cable-2026-10-19.jpg`) |
| 8 | `tp4-recording-setup-2026-08-18.jpg` | [`data/drop-tests/calibration-check/tp4-settings-2026-08-18.jpg`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/f6471ad/data/drop-tests/calibration-check/tp4-settings-2026-08-18.jpg) (PR #86) |
| 9 | `impact-sequence-60in-9GMQYQ.jpg` | [`07_video_montage_9GMQYQ.png`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/f6471ad/data/drop-tests/60in-5felts-validation/video/figures/07_video_montage_9GMQYQ.png) (PR #86), title line cropped |

The composite panels (figures 1, 5 and 7) were cropped and combined with Pillow from the original
attachments; the build script places the finished images and does not rebuild them.
