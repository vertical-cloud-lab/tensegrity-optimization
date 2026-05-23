# Verification: T3-prism from PR #35, sliced with the §B recipe

This folder is a one-shot end-to-end check that the §B PLA support recipe
in [`../README.md`](../README.md) actually places supports correctly on a
real tensegrity STL, with no per-geometry painting.

## Inputs

- Mesh: `cad/t3-prism/t3-prism.stl` from PR #35 head
  `copilot/get-bambu-sliced-print-t3-prism` (the combined PLA+TPU mesh of
  the bonded-captive-core T3-prism at scale 1.5×, R=37.5, H=105, twist=60,
  strut_d=9, cable_d=4.5, joint_d=7).
- Process: `prusaslicer-pla-tensegrity.ini` — a 1-to-1 PrusaSlicer 2.7
  translation of [`../bambu-pla-tensegrity-process.json`](../bambu-pla-tensegrity-process.json)
  so the recipe can be verified off-line without the Bambu Studio binary.
  Bambu→Prusa key mapping documented in-line at the top of the .ini.

## How to reproduce

```bash
# 1. Extract the T3-prism mesh from PR #35 (or, after it merges, from
#    main at the same path):
git show origin/copilot/get-bambu-sliced-print-t3-prism:cad/t3-prism/t3-prism.stl \
    > /tmp/t3-prism.stl
# (post-merge equivalent: `git show main:cad/t3-prism/t3-prism.stl > /tmp/t3-prism.stl`)

# 2. Slice with the recipe:
prusa-slicer --slice \
    --load cad/print-supports/verification/prusaslicer-pla-tensegrity.ini \
    --center 128,128 \
    --output /tmp/t3-prism.gcode /tmp/t3-prism.stl

# 3. Render the toolpath PNG (numpy + matplotlib):
python3 cad/print-supports/verification/render_gcode.py \
    /tmp/t3-prism.gcode \
    cad/print-supports/verification/t3-prism-pr35-gcode-preview.png
```

For reference, the snapshot committed here was generated from PR #35 head
commit `65d0d3f` (`copilot/get-bambu-sliced-print-t3-prism`).

## Result

- `t3-prism-pr35-gcode-preview.png` — 3-panel render of every extrusion
  move in the resulting G-code:
  - **Bottom view, supports only** (the slicer's automatic equivalent of
    Audrey's manual paint pattern).
  - **Iso, object grey + supports orange** — visually confirms every tree
    branch roots at the plate (`z≈0`), none on a member.
  - **First layer (z ≤ 0.25 mm)** — brim, object first layer, support
    touch-points actually on the bed.

### Slice summary

| Metric                  | Value                                |
| ----------------------- | ------------------------------------ |
| Layers                  | 601                                  |
| Layer height            | 0.20 mm                              |
| Extrusion segments      | 438,955 total (104,354 support / 333,092 object / 1,207 brim) |
| Filament used           | 38.93 cm³ (PLA)                      |
| Estimated print time    | 6 h 54 m 58 s (normal mode)          |
| Support style           | organic tree (= Bambu `tree(hybrid)`)|
| Supports on plate only? | yes (`support_material_buildplate_only = 1`) |
| Overhang threshold      | **10°** (TPU-safe — see below)       |
| Brim                    | 5 mm outer-only                      |
| Bridges supported?      | no (`dont_support_bridges = 1`)      |

The support-only bottom view reproduces Audrey's centerline-stripe pattern
without any manual painting, and after dropping `support_threshold_angle`
from 40° to 10° the entire down-facing side of every near-vertical strut
also gets supported all the way to the plate, so the same recipe survives
a TPU print of the same mesh (TPU sags on any shallow overhang PLA would
self-support).

## Why θ=10°? — TPU-safe strut-bottom coverage

The first draft of the recipe used `support_threshold_angle = 40` (~40°
from vertical). For PLA on the T3-prism that was fine, but it left the
shallow-overhang under-side of every near-vertical strut completely
unsupported because tilts of ~25–35° from vertical sit below the
threshold. TPU 85A (NinjaFlex-class, E ≈ 12 MPa) can't self-support those
overhangs and would sag.

Dropping the threshold to **10°** flags the entire down-facing surface of
every tilted member as an overhang, so the tree generator builds branches
from the plate all the way along each strut's bottom. The added coverage
shows up clearly in `t3-prism-pr35-threshold-comparison.png`:

| Metric                       | θ = 40° (old) | θ = 10° (new) | Δ        |
| ---------------------------- | ------------: | ------------: | -------: |
| Support extrusion segments   | 96,176        | 104,354       | +8.5 %   |
| Filament                     | 38.39 cm³     | 38.93 cm³     | +1.4 %   |
| Print time                   | 6 h 52 m 30 s | 6 h 54 m 58 s | +0.6 %   |

Only truly vertical surfaces (< 10° from vertical: the joint-sphere
overlaps at each vertex and the three bed-contact cones) are still
skipped, preserving the "do not paint at vertex overlaps" rule there.

To regenerate the comparison panel:

```bash
# slice once with the (old) θ=40 setting:
sed 's/^support_material_threshold = 10/support_material_threshold = 40/' \
    cad/print-supports/verification/prusaslicer-pla-tensegrity.ini \
    > /tmp/old.ini
prusa-slicer --slice --load /tmp/old.ini --center 128,128 \
    --output /tmp/t3-prism-old.gcode /tmp/t3-prism.stl

# slice again with the (new) θ=10 setting:
prusa-slicer --slice \
    --load cad/print-supports/verification/prusaslicer-pla-tensegrity.ini \
    --center 128,128 \
    --output /tmp/t3-prism.gcode /tmp/t3-prism.stl

# render the side-by-side diff:
python3 cad/print-supports/verification/diff_supports.py \
    /tmp/t3-prism-old.gcode /tmp/t3-prism.gcode \
    cad/print-supports/verification/t3-prism-pr35-threshold-comparison.png
```
