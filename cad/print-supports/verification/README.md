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
# 1. Extract the T3-prism mesh from PR #35:
git show origin/copilot/get-bambu-sliced-print-t3-prism:cad/t3-prism/t3-prism.stl \
    > /tmp/t3-prism.stl

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
| Extrusion segments      | 425,230 total (96,176 support / 327,553 object / 1,198 brim) |
| Filament used           | 38.39 cm³ (PLA)                      |
| Estimated print time    | 6 h 52 m 30 s (normal mode)          |
| Support style           | organic tree (= Bambu `tree(hybrid)`)|
| Supports on plate only? | yes (`support_material_buildplate_only = 1`) |
| Brim                    | 5 mm outer-only                      |
| Bridges supported?      | no (`dont_support_bridges = 1`)      |

The support-only bottom view reproduces Audrey's centerline-stripe pattern
without any manual painting — supports live only under the 9 non-bed-contact
members, the three bottom-triangle cables bridge unsupported between the
bed-contact vertices, and tree branches all root on the plate.
