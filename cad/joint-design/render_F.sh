#!/usr/bin/env bash
# Render iso + 3 orthogonal section views of Design F (captive TPU core inside
# PETG/PLA outer shell with teardrop strut fillet + layer-interlock teeth).
# Usage:  bash cad/joint-design/render_F.sh
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p renders

ISO_CAM="--camera=40,40,15,0,0,0 --imgsize=1100,900 --colorscheme=Tomorrow"

RUN=""
if [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null 2>&1; then
    RUN="xvfb-run -a"
fi

VIEWS=(F_captive_core F_captive_core_section_X F_captive_core_section_Y F_captive_core_section_Z)

for v in "${VIEWS[@]}"; do
    echo ">>> Rendering ${v}"
    # Iso uses preview (better colours); section files need --render so the
    # difference()-cube CSG actually evaluates (preview was reusing the iso
    # image for orthogonal cuts).
    if [[ "$v" == *section* ]]; then
        $RUN openscad --render -o "renders/${v}_iso.png" $ISO_CAM "${v}.scad"
    else
        $RUN openscad -o "renders/${v}_iso.png" $ISO_CAM "${v}.scad"
    fi
done
$RUN openscad -o "renders/F_captive_core.stl" "F_captive_core.scad"

if command -v montage >/dev/null 2>&1; then
    montage \
        -label "iso"             renders/F_captive_core_iso.png \
        -label "section X=0"     renders/F_captive_core_section_X_iso.png \
        -label "section Y=0"     renders/F_captive_core_section_Y_iso.png \
        -label "section Z=0"     renders/F_captive_core_section_Z_iso.png \
        -tile 4x1 -geometry 480x400+8+8 -background white \
        -title "Design F — captive TPU core inside PETG/PLA outer shell, teardrop strut fillet, layer-interlock teeth (PETG/PLA orange, TPU cyan)" \
        renders/F_captive_core_grid_montage.png
fi

echo "done."
