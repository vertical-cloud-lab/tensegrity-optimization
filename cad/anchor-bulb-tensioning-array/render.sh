#!/usr/bin/env bash
# Render iso PNG + STL for every specimen in the anchor-bulb tensioning test
# array, plus three section cuts (representative of each axis) and a contact-
# sheet montage of the full plate.
#
# Usage:  bash cad/anchor-bulb-tensioning-array/render.sh
# Requirements: openscad, imagemagick (`montage`); auto-uses xvfb-run if no DISPLAY.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p renders

ISO_CAM_SPECIMEN="--camera=80,80,28,0,0,28 --imgsize=600,800 --colorscheme=Tomorrow"
ISO_CAM_ARRAY="--camera=180,180,40,0,0,28 --imgsize=1600,1000 --colorscheme=Tomorrow"

RUN=""
if [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null 2>&1; then
    RUN="xvfb-run -a"
fi

SPECIMENS=(TA-G0 TA-G1 TA-G2 TA-G3 TA-G4 TA-G5 TA-L0 TA-L1 TA-L2 TA-R0 TA-R1 TA-R2)

for s in "${SPECIMENS[@]}"; do
    echo ">>> Rendering ${s}"
    $RUN openscad -o "renders/${s}_iso.png" $ISO_CAM_SPECIMEN "${s}.scad"
    $RUN openscad -o "renders/${s}.stl"     "${s}.scad"
done

for s in TA-G2 TA-L1 TA-R1; do
    echo ">>> Rendering ${s}_section_Y"
    $RUN openscad -o "renders/${s}_section_Y_iso.png" $ISO_CAM_SPECIMEN "${s}_section_Y.scad"
done

echo ">>> Rendering full array"
$RUN openscad -o "renders/tensioning_array_iso.png" $ISO_CAM_ARRAY tensioning_array.scad
$RUN openscad -o "renders/tensioning_array.stl"     tensioning_array.scad

if command -v montage >/dev/null 2>&1; then
    montage \
        -label "TA-G0 (gap=0.0 mm)" renders/TA-G0_iso.png \
        -label "TA-G1 (gap=0.1 mm)" renders/TA-G1_iso.png \
        -label "TA-G2 (gap=0.2 mm)" renders/TA-G2_iso.png \
        -label "TA-G3 (gap=0.3 mm)" renders/TA-G3_iso.png \
        -label "TA-G4 (gap=0.4 mm)" renders/TA-G4_iso.png \
        -label "TA-G5 (gap=0.6 mm)" renders/TA-G5_iso.png \
        -label "TA-L0 (pause Z=18.5)" renders/TA-L0_iso.png \
        -label "TA-L1 (pause Z=20.75)" renders/TA-L1_iso.png \
        -label "TA-L2 (pause Z=25.0)" renders/TA-L2_iso.png \
        -label "TA-R0 (PVA wall=0.2 mm)" renders/TA-R0_iso.png \
        -label "TA-R1 (PVA wall=0.4 mm)" renders/TA-R1_iso.png \
        -label "TA-R2 (PVA wall=0.6 mm)" renders/TA-R2_iso.png \
        -tile 4x3 -geometry 320x420+6+6 -background white \
        -title "Anchor-bulb tensioning test array — 12 specimens (PLA orange, TPU cyan, PVA grey)" \
        renders/all_specimens_montage.png

    montage \
        -label "TA-G2 (axis A: air gap)"     renders/TA-G2_section_Y_iso.png \
        -label "TA-L1 (axis B: pause+lube)"  renders/TA-L1_section_Y_iso.png \
        -label "TA-R1 (axis C: PVA sleeve)"  renders/TA-R1_section_Y_iso.png \
        -tile 3x1 -geometry 480x640+8+8 -background white \
        -title "Y=0 cutaways — one representative per axis" \
        renders/section_montage.png
fi

echo "done."
