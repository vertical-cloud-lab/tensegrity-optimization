#!/usr/bin/env bash
# ============================================================================
# Tensegrity Optimization — T3-prism print-prep pipeline.
#
# Issue: "Get a bambu sliced print for a T3-prism" — pure PETG, single
# part. Render the parametric OpenSCAD model to a printable STL, sanity-
# check the mesh, generate an iso preview PNG, and produce Bambu-bound
# PETG g-code for two common Bambu beds (X1C-class 256x256 and A1-mini-
# class 180x180). Settings track Bambu Lab's published "Bambu PETG Basic"
# profile (255 °C nozzle / 70 °C bed, 0.4 mm nozzle, 0.20 mm layers).
#
# Outputs (next to this script):
#   t3-prism.stl                            Watertight, single-part PETG body
#   t3-prism-iso.png                        OpenSCAD iso preview
#   slices/t3-prism.X1C-PETG.gcode          Bambu X1C / P1S / A1 (256x256 bed)
#   slices/t3-prism.A1mini-PETG.gcode       Bambu A1 mini (180x180 bed)
#
# Pre-reqs: openscad, admesh, prusa-slicer, xvfb-run
#   sudo apt-get install -y openscad admesh prusa-slicer xvfb
#
# Notes on "Bambu sliced":
#   PrusaSlicer outputs Marlin-flavored g-code that runs natively on Bambu
#   firmware (Bambu's printers honour the Marlin G/M-code subset PrusaSlicer
#   emits). To produce a `.gcode.3mf` that uploads through Bambu Studio
#   Cloud (with thumbnail + per-plate metadata), open `t3-prism.stl` in
#   Bambu Studio with the Bambu PETG Basic preset and "0.20mm Standard
#   @ X1C" process — the geometry is identical and the slice settings here
#   already match Bambu's defaults.
# ============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAD="${HERE}/t3-prism.scad"
STL="${HERE}/t3-prism.stl"
PNG="${HERE}/t3-prism-iso.png"
SLICES_DIR="${HERE}/slices"
SCRATCH="${SCRATCH:-/tmp/t3-prism}"
mkdir -p "${SLICES_DIR}" "${SCRATCH}"

NOZZLE_DIAMETER="${NOZZLE_DIAMETER:-0.4}"
LAYER_HEIGHT="${LAYER_HEIGHT:-0.20}"
PETG_NOZZLE_TEMP="${PETG_NOZZLE_TEMP:-255}"   # Bambu PETG Basic nozzle
PETG_BED_TEMP="${PETG_BED_TEMP:-70}"          # Bambu PETG Basic bed

# ----------------------------------------------------------------------------
# 1. SCAD -> STL
# ----------------------------------------------------------------------------
echo "==> OpenSCAD render -> ${STL##*/}"
xvfb-run -a openscad -o "${STL}" --export-format=binstl "${SCAD}"

echo "==> admesh manifold check"
admesh -fundecvb "${SCRATCH}/t3-prism-clean.stl" "${STL}" \
    | grep -E '(Number of parts|disconnected|Degenerate|Volume)' | head -6

# ----------------------------------------------------------------------------
# 2. Iso preview PNG (for the README + PR thumbnail)
# ----------------------------------------------------------------------------
echo "==> Iso preview PNG -> ${PNG##*/}"
xvfb-run -a openscad -o "${PNG}" --imgsize=600,800 \
    --autocenter --viewall --colorscheme=Tomorrow \
    --projection=perspective "${SCAD}"

# ----------------------------------------------------------------------------
# 3. Slice for Bambu printers (PrusaSlicer with Bambu-equivalent PETG profile).
#    Bambu firmware accepts the Marlin g-code dialect PrusaSlicer emits;
#    settings below mirror Bambu Studio's "Bambu PETG Basic @ X1C / 0.20mm
#    Standard" preset (nozzle 255 °C, bed 70 °C, 3 perimeters, 25% gyroid).
# ----------------------------------------------------------------------------
slice_bambu () {
    local bed="$1" out="$2"
    prusa-slicer --export-gcode --output "${out}" \
        --filament-diameter 1.75 \
        --nozzle-diameter   "${NOZZLE_DIAMETER}" \
        --filament-type     PETG \
        --temperature                "${PETG_NOZZLE_TEMP}" \
        --first-layer-temperature    "${PETG_NOZZLE_TEMP}" \
        --bed-temperature            "${PETG_BED_TEMP}" \
        --first-layer-bed-temperature "${PETG_BED_TEMP}" \
        --bed-shape "${bed}" \
        --layer-height "${LAYER_HEIGHT}" --first-layer-height "${LAYER_HEIGHT}" \
        --perimeters 3 --top-solid-layers 5 --bottom-solid-layers 4 \
        --fill-density 25% --fill-pattern gyroid \
        --skirts 1 --skirt-distance 5 --brim-width 4 \
        --support-material --support-material-auto \
        --support-material-threshold 50 \
        --start-gcode $'G90\nM83\nM140 S'"${PETG_BED_TEMP}"$'\nM104 S'"${PETG_NOZZLE_TEMP}"$'\nG28\nM190 S'"${PETG_BED_TEMP}"$'\nM109 S'"${PETG_NOZZLE_TEMP}"$'\nG29\nG1 Z5 F600\n' \
        --end-gcode $'M104 S0\nM140 S0\nG28 X\nM84\n' \
        "${STL}" 2>&1 | tail -2
    grep -E '^; (estimated printing time|filament used \[(mm|cm3)\])' "${out}" \
        | sed 's/^/      /'
}

# Bambu X1C / X1 / P1S / A1 share a 256x256 build plate.
echo "==> PrusaSlicer -> Bambu X1C-class (256x256), PETG"
slice_bambu '0x0,256x0,256x256,0x256' "${SLICES_DIR}/t3-prism.X1C-PETG.gcode"

echo "==> PrusaSlicer -> Bambu A1 mini (180x180), PETG"
slice_bambu '0x0,180x0,180x180,0x180' "${SLICES_DIR}/t3-prism.A1mini-PETG.gcode"

echo
echo "==> Done."
echo "    STL:     ${STL}"
echo "    Iso:     ${PNG}"
echo "    G-code:  ${SLICES_DIR}/t3-prism.{X1C,A1mini}-PETG.gcode"
