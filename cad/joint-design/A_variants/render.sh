#!/usr/bin/env bash
# Render iso + section_Y views of each anchor-upset shape variant of Design A
# as PNGs, plus 5x and 6x contact-sheet montages.
# Usage:  bash cad/joint-design/A_variants/render.sh
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p renders

ISO_CAM="--camera=40,40,15,0,0,-2 --imgsize=900,700 --colorscheme=Tomorrow"

RUN=""
if [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null 2>&1; then
    RUN="xvfb-run -a"
fi

VARIANTS=(A0_sphere A1_frustum A2_torus A3_countersunk A4_lobed A5_mushroom)

for v in "${VARIANTS[@]}"; do
    echo ">>> Rendering ${v}"
    $RUN openscad -o "renders/${v}_iso.png"              $ISO_CAM "${v}.scad"
    $RUN openscad -o "renders/${v}_section_Y_iso.png"    $ISO_CAM "${v}_section_Y.scad"
    $RUN openscad -o "renders/${v}.stl"                  "${v}.scad"
done

if command -v montage >/dev/null 2>&1; then
    montage \
        -label "A0 sphere (ref)"        renders/A0_sphere_iso.png \
        -label "A1 frustum (rivet)"     renders/A1_frustum_iso.png \
        -label "A2 torus (donut)"       renders/A2_torus_iso.png \
        -label "A3 countersunk (flush)" renders/A3_countersunk_iso.png \
        -label "A4 lobed (keyed)"       renders/A4_lobed_iso.png \
        -label "A5 mushroom (undercut)" renders/A5_mushroom_iso.png \
        -tile 6x1 -geometry 360x300+8+8 -background white \
        -title "Design A anchor-upset shape variants — iso (PETG/PLA orange, TPU cyan)" \
        renders/all_variants_iso_montage.png

    montage \
        -label "A0 sphere (ref)"        renders/A0_sphere_section_Y_iso.png \
        -label "A1 frustum (rivet)"     renders/A1_frustum_section_Y_iso.png \
        -label "A2 torus (donut)"       renders/A2_torus_section_Y_iso.png \
        -label "A3 countersunk (flush)" renders/A3_countersunk_section_Y_iso.png \
        -label "A4 lobed (keyed)"       renders/A4_lobed_section_Y_iso.png \
        -label "A5 mushroom (undercut)" renders/A5_mushroom_section_Y_iso.png \
        -tile 6x1 -geometry 360x300+8+8 -background white \
        -title "Design A anchor-upset shape variants — section cut at Y=0" \
        renders/all_variants_section_montage.png

    # 2-row grid (iso + section) for at-a-glance comparison.
    montage \
        renders/A0_sphere_iso.png \
        renders/A1_frustum_iso.png \
        renders/A2_torus_iso.png \
        renders/A3_countersunk_iso.png \
        renders/A4_lobed_iso.png \
        renders/A5_mushroom_iso.png \
        renders/A0_sphere_section_Y_iso.png \
        renders/A1_frustum_section_Y_iso.png \
        renders/A2_torus_section_Y_iso.png \
        renders/A3_countersunk_section_Y_iso.png \
        renders/A4_lobed_section_Y_iso.png \
        renders/A5_mushroom_section_Y_iso.png \
        -tile 6x2 -geometry 320x260+6+6 -background white \
        -title "Design A anchor-upset variants: iso (top) + Y=0 cutaway (bottom). A0 sphere | A1 frustum | A2 torus | A3 countersunk | A4 lobed | A5 mushroom" \
        renders/all_variants_grid_montage.png
fi

echo "done."
