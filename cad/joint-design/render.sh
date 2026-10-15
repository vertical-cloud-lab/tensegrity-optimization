#!/usr/bin/env bash
# Render iso + section views of each candidate joint design as PNGs.
# Usage:  bash cad/joint-design/render.sh
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p renders

# Camera args:  --camera = eye_x,eye_y,eye_z,center_x,center_y,center_z  (auto-zoom)
# We pick an eye position roughly southeast and slightly elevated so the
# joint plane (X-Z) and the TPU/PETG split are both visible.
ISO_CAM="--camera=40,40,15,0,0,-2 --imgsize=900,700 --colorscheme=Tomorrow"
TOP_CAM="--camera=0,0,40,0,0,-2 --imgsize=600,600 --colorscheme=Tomorrow"

# OpenSCAD's PNG renderer needs a GL context — wrap in xvfb-run if no DISPLAY.
RUN=""
if [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null 2>&1; then
    RUN="xvfb-run -a"
fi

for design in A_anchor_bulb B_dovetail C_tpu_sleeve_overmold D_eyelet_loop E_tpu_rebar; do
    echo ">>> Rendering ${design}"
    $RUN openscad -o "renders/${design}_iso.png"  $ISO_CAM  "${design}.scad"
    openscad -o "renders/${design}.stl"      "${design}.scad"
done

# Section / cutaway views on three orthogonal planes (Y=0, X=0, Z=-2) so the
# captive interior geometry is visible from multiple directions. This makes
# topology / connectivity issues (e.g., chain-link in D, head-cable continuity
# in B) unambiguous from a single viewing angle.
for design in A_anchor_bulb B_dovetail C_tpu_sleeve_overmold D_eyelet_loop E_tpu_rebar; do
    for axis in Y X Z; do
        echo ">>> Rendering ${design}_section_${axis}"
        $RUN openscad -o "renders/${design}_section_${axis}_iso.png" \
            $ISO_CAM  "${design}_section_${axis}.scad"
    done
done

# Backwards-compat aliases (the older single Y-cut filename is still embedded
# in some README image references).
for design in A_anchor_bulb B_dovetail C_tpu_sleeve_overmold D_eyelet_loop E_tpu_rebar; do
    cp -f "renders/${design}_section_Y_iso.png" "renders/${design}_section_iso.png"
done

# Build a contact-sheet montage if ImageMagick is available.
if command -v montage >/dev/null 2>&1; then
    montage \
        renders/A_anchor_bulb_iso.png \
        renders/B_dovetail_iso.png \
        renders/C_tpu_sleeve_overmold_iso.png \
        renders/D_eyelet_loop_iso.png \
        renders/E_tpu_rebar_iso.png \
        -tile 5x1 -geometry 400x320+8+8 -background white \
        -title "PETG (orange) + TPU (cyan) joint candidates A B C D E (iso)" \
        renders/all_iso_montage.png

    montage \
        renders/A_anchor_bulb_section_Y_iso.png \
        renders/B_dovetail_section_Y_iso.png \
        renders/C_tpu_sleeve_overmold_section_Y_iso.png \
        renders/D_eyelet_loop_section_Y_iso.png \
        renders/E_tpu_rebar_section_Y_iso.png \
        -tile 5x1 -geometry 400x320+8+8 -background white \
        -title "Section / cutaway views (cut at Y=0): A bore, B captive head, C sleeve+knurl, D loop+eyelet, E barbed rebar" \
        renders/all_section_montage.png

    # Multi-plane orthogonal cross-section grid (5 designs x 3 cut planes).
    # Each row: one design; each column: one orthogonal cut (Y=0, X=0, Z=-2).
    # This is the visualization requested by PR comment 4427543897 to disambiguate
    # B-dovetail head/cable continuity and D-eyelet loop chain-link topology.
    montage \
        -label "A iso"          renders/A_anchor_bulb_iso.png \
        -label "A cut Y=0"      renders/A_anchor_bulb_section_Y_iso.png \
        -label "A cut X=0"      renders/A_anchor_bulb_section_X_iso.png \
        -label "A cut Z=-2"     renders/A_anchor_bulb_section_Z_iso.png \
        -label "B iso"          renders/B_dovetail_iso.png \
        -label "B cut Y=0"      renders/B_dovetail_section_Y_iso.png \
        -label "B cut X=0"      renders/B_dovetail_section_X_iso.png \
        -label "B cut Z=-2"     renders/B_dovetail_section_Z_iso.png \
        -label "C iso"          renders/C_tpu_sleeve_overmold_iso.png \
        -label "C cut Y=0"      renders/C_tpu_sleeve_overmold_section_Y_iso.png \
        -label "C cut X=0"      renders/C_tpu_sleeve_overmold_section_X_iso.png \
        -label "C cut Z=-2"     renders/C_tpu_sleeve_overmold_section_Z_iso.png \
        -label "D iso"          renders/D_eyelet_loop_iso.png \
        -label "D cut Y=0"      renders/D_eyelet_loop_section_Y_iso.png \
        -label "D cut X=0"      renders/D_eyelet_loop_section_X_iso.png \
        -label "D cut Z=-2"     renders/D_eyelet_loop_section_Z_iso.png \
        -label "E iso"          renders/E_tpu_rebar_iso.png \
        -label "E cut Y=0"      renders/E_tpu_rebar_section_Y_iso.png \
        -label "E cut X=0"      renders/E_tpu_rebar_section_X_iso.png \
        -label "E cut Z=-2"     renders/E_tpu_rebar_section_Z_iso.png \
        -tile 4x5 -geometry 380x300+6+6 -background white \
        -title "PETG+TPU joint candidates: iso + 3 orthogonal cross-sections per design" \
        renders/all_multiplane_section_montage.png
fi

echo "done."
