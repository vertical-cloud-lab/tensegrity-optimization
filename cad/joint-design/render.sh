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

# Section / cutaway views (model intersected with the +Y half-space) so the
# captive interior geometry is visible (bore for A; slot+head for B; sleeve
# wall + knurl for C; embedded barbs for E). Use isometric camera so the
# colored outer surfaces and the cut faces are both visible.
for design in A_anchor_bulb B_dovetail C_tpu_sleeve_overmold E_tpu_rebar; do
    echo ">>> Rendering ${design}_section"
    $RUN openscad -o "renders/${design}_section_iso.png"  $ISO_CAM  "${design}_section.scad"
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
        renders/A_anchor_bulb_section_iso.png \
        renders/B_dovetail_section_iso.png \
        renders/C_tpu_sleeve_overmold_section_iso.png \
        renders/D_eyelet_loop_iso.png \
        renders/E_tpu_rebar_section_iso.png \
        -tile 5x1 -geometry 400x320+8+8 -background white \
        -title "Section / cutaway views (cut at Y=0): A bore, B captive head, C sleeve+knurl, D loop+eyelet, E barbed rebar" \
        renders/all_section_montage.png
fi

echo "done."
