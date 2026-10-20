#!/usr/bin/env bash
# Render iso PNG + STL for every specimen in the anchor-bulb tensioning test
# array (A3 countersunk, horizontal cable orientation), plus three X=0 section
# cuts (one per node-size row) and a contact-sheet montage of the full plate.
#
# Usage:  bash cad/anchor-bulb-tensioning-array/render.sh
# Requirements: openscad, imagemagick (`montage`); auto-uses xvfb-run if no DISPLAY.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p renders

ISO_CAM_SPECIMEN="--camera=70,-50,30,0,5,18 --imgsize=600,500 --colorscheme=Tomorrow"
ISO_CAM_ARRAY="--camera=240,-200,140,10,0,30 --imgsize=1600,1000 --colorscheme=Tomorrow"

RUN=""
if [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null 2>&1; then
    RUN="xvfb-run -a"
fi

SPECIMENS=(
    H-S0G0 H-S0G1 H-S0G2 H-S0G3 H-S0G4
    H-S1G0 H-S1G1 H-S1G2 H-S1G3 H-S1G4
    H-S2G0 H-S2G1 H-S2G2 H-S2G3 H-S2G4
)

for s in "${SPECIMENS[@]}"; do
    echo ">>> Rendering ${s}"
    $RUN openscad -o "renders/${s}_iso.png" $ISO_CAM_SPECIMEN "${s}.scad"
    $RUN openscad -o "renders/${s}.stl"     "${s}.scad"
done

for s in H-S0G2 H-S1G2 H-S2G2; do
    echo ">>> Rendering ${s}_section_X"
    $RUN openscad -o "renders/${s}_section_X_iso.png" $ISO_CAM_SPECIMEN "${s}_section_X.scad"
done

echo ">>> Rendering full array"
$RUN openscad -o "renders/tensioning_array_iso.png" $ISO_CAM_ARRAY tensioning_array.scad
$RUN openscad -o "renders/tensioning_array.stl"     tensioning_array.scad

if command -v montage >/dev/null 2>&1; then
    # 3x5 grid: rows = node size, cols = gap.
    montage \
        -label "node 7.5 mm | gap 0.1 mm"  renders/H-S0G0_iso.png \
        -label "node 7.5 mm | gap 0.2 mm"  renders/H-S0G1_iso.png \
        -label "node 7.5 mm | gap 0.3 mm"  renders/H-S0G2_iso.png \
        -label "node 7.5 mm | gap 0.4 mm"  renders/H-S0G3_iso.png \
        -label "node 7.5 mm | gap 0.6 mm"  renders/H-S0G4_iso.png \
        -label "node 9.5 mm | gap 0.1 mm"  renders/H-S1G0_iso.png \
        -label "node 9.5 mm | gap 0.2 mm"  renders/H-S1G1_iso.png \
        -label "node 9.5 mm | gap 0.3 mm"  renders/H-S1G2_iso.png \
        -label "node 9.5 mm | gap 0.4 mm"  renders/H-S1G3_iso.png \
        -label "node 9.5 mm | gap 0.6 mm"  renders/H-S1G4_iso.png \
        -label "node 12.0 mm | gap 0.1 mm" renders/H-S2G0_iso.png \
        -label "node 12.0 mm | gap 0.2 mm" renders/H-S2G1_iso.png \
        -label "node 12.0 mm | gap 0.3 mm" renders/H-S2G2_iso.png \
        -label "node 12.0 mm | gap 0.4 mm" renders/H-S2G3_iso.png \
        -label "node 12.0 mm | gap 0.6 mm" renders/H-S2G4_iso.png \
        -tile 5x3 -geometry 300x270+6+6 -background white \
        -title "Anchor-bulb (A3 countersunk) horizontal-cable tensioning test array — 15 specimens (PLA orange, TPU cyan)" \
        renders/all_specimens_montage.png

    montage \
        -label "node 7.5 mm | gap 0.3 mm"  renders/H-S0G2_section_X_iso.png \
        -label "node 9.5 mm | gap 0.3 mm"  renders/H-S1G2_section_X_iso.png \
        -label "node 12.0 mm | gap 0.3 mm" renders/H-S2G2_section_X_iso.png \
        -tile 3x1 -geometry 500x420+8+8 -background white \
        -title "X=0 cutaways — middle-gap (0.3 mm) specimen at each node size" \
        renders/section_montage.png
fi

echo "done."
