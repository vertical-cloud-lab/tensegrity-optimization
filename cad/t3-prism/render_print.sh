#!/usr/bin/env bash
# ============================================================================
# Tensegrity Optimization — T3-prism Bambu print-prep pipeline.
#
# Issue: "Get a bambu sliced print for a T3-prism" — pure PETG, single
# part, prepared for the Bambu Lab H2D (the lab's only printer; see
# `.github/copilot-instructions.md`). Renders the parametric OpenSCAD
# model to a printable STL, sanity-checks the mesh, generates an iso
# preview PNG, and produces TWO H2D artifacts:
#
#   * `slices/t3-prism.H2D.3mf`            — Bambu Studio PROJECT file
#       (re-importable in Bambu Studio for editing / re-slicing,
#       drag-and-drop or File > Open Project). No g-code inside.
#   * `slices/t3-prism.H2D-PETG.gcode.3mf` — sliced PRINT JOB
#       (uploaded to the printer over LAN/cloud; contains
#       `Metadata/plate_1.gcode` for direct firmware consumption).
#       Bambu Studio refuses to re-import this format with
#       "The file does not contain any geometry data" — that is by
#       design (it's a printer-side artifact, not a model).
#
# Implementation follows the empirically-verified BambuStudio CLI recipe
# from `vertical-cloud-lab/powder-doser` PR #23:
#   1. Download the official BambuStudio Linux AppImage (pinned version).
#   2. Extract its bundled `resources/profiles/BBL/{machine,process,filament}`.
#   3. Flatten the `inherits:` chain on each profile JSON into a single
#      "full config" — the CLI does NOT resolve inheritance.
#   4. Patch `from=system`, `inherits=""`, and `printer_settings_id` on
#      the machine profile so the CLI's compatibility check accepts it.
#      Set `curr_bed_type=Textured PEI Plate` so PETG passes the
#      filament-vs-bed compatibility check.
#   5. Run the CLI twice: once WITHOUT `--slice` to produce the project
#      `.3mf`, once WITH `--slice 1` (and IDEX manual filament-map for
#      the dual-extruder H2D) to produce the sliced `.gcode.3mf`.
#
# Outputs (next to this script):
#   t3-prism.stl                            Watertight, single-part PETG body
#   t3-prism-iso.png                        OpenSCAD iso preview
#   slices/t3-prism.H2D.3mf                 Bambu Studio project (re-importable)
#   slices/t3-prism.H2D-PETG.gcode.3mf      Sliced print job (printer upload)
#
# Pre-reqs: openscad, admesh, xvfb, plus the BambuStudio AppImage runtime
# deps (Ubuntu 24.04):
#   sudo apt-get install -y openscad admesh xvfb \
#       gstreamer1.0-plugins-base libsoup-3.0-0 libwebkit2gtk-4.1-0
# ============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAD="${HERE}/t3-prism.scad"
STL="${HERE}/t3-prism.stl"
STL_THICK="${HERE}/t3-prism-thick.stl"
STL_STRUTS="${HERE}/t3-prism-struts.stl"
STL_CABLES="${HERE}/t3-prism-cables.stl"
PNG="${HERE}/t3-prism-iso.png"
SLICES_DIR="${HERE}/slices"
SCRATCH="${SCRATCH:-/tmp/t3-prism}"
mkdir -p "${SLICES_DIR}" "${SCRATCH}"

# Pinned BambuStudio version (matches powder-doser PR #23 verification).
BAMBU_VERSION="${BAMBU_VERSION:-v02.06.00.51}"
BAMBU_APPIMAGE="${BAMBU_APPIMAGE:-${SCRATCH}/bambu.AppImage}"
BAMBU_URL="${BAMBU_URL:-https://github.com/bambulab/BambuStudio/releases/download/${BAMBU_VERSION}/BambuStudio_ubuntu-24.04-${BAMBU_VERSION}-20260417160415.AppImage}"

# ----------------------------------------------------------------------------
# 1. SCAD -> STL (single-material full body + per-part halves for MM)
# ----------------------------------------------------------------------------
echo "==> OpenSCAD render -> ${STL##*/} (single-material, both materials fused)"
xvfb-run -a openscad -o "${STL}" --export-format=binstl "${SCAD}"

# Thick-cable variant (cable_d 2.4 -> 3.5 mm) -- the print-failure-mode
# section of README.md (and the Edison ANALYSIS) recommends 3.0-4.0 mm
# to widen the top-cable bridges so PETG can span them and so Bambu
# Studio's auto-support actually catches the overhangs (in the first
# H2D test print with auto-support the 2.4 mm cables were thin enough
# that auto-support skipped them; @achris0520 found scaling the model
# to 1.3x re-enabled support generation on the strings, which is
# equivalent to bumping cable_d by ~1.5x). 3.5 mm is the midpoint of
# the recommended range.
echo "==> OpenSCAD render -> ${STL_THICK##*/} (thick-cable variant, cable_d=3.5)"
xvfb-run -a openscad -o "${STL_THICK}" --export-format=binstl \
    -D 'cable_d=3.5' "${SCAD}"

echo "==> OpenSCAD render -> ${STL_STRUTS##*/} (multi-material: rigid half / PLA, bed-centered)"
xvfb-run -a openscad -o "${STL_STRUTS}" --export-format=binstl \
    -D 'part="struts"' -D 'offset_x=175' -D 'offset_y=160' -D 'offset_z=3.5' "${SCAD}"

echo "==> OpenSCAD render -> ${STL_CABLES##*/} (multi-material: tension half / PETG, bed-centered)"
xvfb-run -a openscad -o "${STL_CABLES}" --export-format=binstl \
    -D 'part="cables"' -D 'offset_x=175' -D 'offset_y=160' -D 'offset_z=3.5' "${SCAD}"

echo "==> admesh manifold check"
admesh -fundecvb "${SCRATCH}/t3-prism-clean.stl" "${STL}" \
    | grep -E '(Number of parts|disconnected|Degenerate|Volume)' | head -6
admesh -fundecvb "${SCRATCH}/t3-prism-thick-clean.stl" "${STL_THICK}" \
    | grep -E '(Number of parts|disconnected|Degenerate|Volume)' | head -6
admesh -fundecvb "${SCRATCH}/t3-prism-struts-clean.stl" "${STL_STRUTS}" \
    | grep -E '(Number of parts|disconnected|Degenerate|Volume)' | head -6
admesh -fundecvb "${SCRATCH}/t3-prism-cables-clean.stl" "${STL_CABLES}" \
    | grep -E '(Number of parts|disconnected|Degenerate|Volume)' | head -6

# ----------------------------------------------------------------------------
# 2. Iso preview PNG (for the README + PR thumbnail)
# ----------------------------------------------------------------------------
echo "==> Iso preview PNG -> ${PNG##*/}"
xvfb-run -a openscad -o "${PNG}" --imgsize=600,800 \
    --autocenter --viewall --colorscheme=Tomorrow \
    --projection=perspective "${SCAD}"

# ----------------------------------------------------------------------------
# 3. BambuStudio AppImage + bundled BBL profiles
# ----------------------------------------------------------------------------
if [[ ! -x "${BAMBU_APPIMAGE}" ]]; then
    echo "==> Fetching BambuStudio ${BAMBU_VERSION} AppImage"
    curl -sLo "${BAMBU_APPIMAGE}" "${BAMBU_URL}"
    chmod +x "${BAMBU_APPIMAGE}"
fi

BBL_ROOT="${SCRATCH}/squashfs-root/resources/profiles/BBL"
if [[ ! -d "${BBL_ROOT}" ]]; then
    echo "==> Extracting bundled BBL profiles from AppImage"
    (cd "${SCRATCH}" && "${BAMBU_APPIMAGE}" --appimage-extract resources/profiles/BBL > /dev/null)
fi

# ----------------------------------------------------------------------------
# 4. Flatten inherits chain + slice for each printer
# ----------------------------------------------------------------------------
flatten () {
    local kind="$1" leaf="$2" out="$3"
    python3 "${HERE}/flatten_bambu_profile.py" "${kind}" "${leaf}" "${BBL_ROOT}" "${out}"
}

patch_bed () {
    # PETG is rejected on the default Cool Plate; switch to Textured PEI.
    python3 -c "
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d['curr_bed_type']    = 'Textured PEI Plate'
d['default_bed_type'] = 'Textured PEI Plate'
json.dump(d, open(p, 'w'), indent=2)
" "$1"
}

patch_supports () {
    # Enable tree (auto) supports on the flattened process profile.
    #
    # In the first H2D PETG print the BBL-default `enable_support=0` left
    # the top-cable bridges (43 mm horizontal sub-mm strands) unsupported
    # and the print spaghetti-failed at layer 362. The second print
    # @me-madsen ran with supports on (Bambu Studio GUI default tree-auto)
    # succeeded everywhere except the top "strings" -- BambuStudio's
    # auto-support filtered those out because the 2.4 mm cables present
    # too small an overhang area to trip the threshold. @achris0520
    # confirmed scaling the model to 1.3x re-enabled support generation on
    # the strings, which is geometrically equivalent to bumping cable_d
    # from 2.4 mm to ~3.1 mm. We use the thick-cable STL (cable_d=3.5)
    # together with these support settings to make sure auto-support
    # actually catches the top-cable bridges.
    python3 -c "
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d['enable_support']                 = '1'
d['support_type']                   = 'tree(auto)'
d['support_threshold_angle']        = '30'
d['support_on_build_plate_only']    = '0'
d['support_critical_regions_only']  = '0'
d['bridge_no_support']              = '0'
json.dump(d, open(p, 'w'), indent=2)
" "$1"
}

slice_bambu () {
    # Produce TWO H2D artifacts in one call:
    #   1. <tag>.3mf            — project file (no `--slice`), re-importable
    #                              in Bambu Studio for editing/re-slicing.
    #   2. <tag>-PETG.gcode.3mf — sliced print job (with `--slice 1` and IDEX
    #                              manual filament-map for the H2D), uploaded
    #                              to the printer over LAN/cloud.
    # Optional 5th arg: STL path override (defaults to ${STL}).
    # Optional 6th arg: "supports" to enable tree-auto supports.
    local tag="$1" machine_leaf="$2" process_leaf="$3" filament_leaf="$4"
    local stl_in="${5:-${STL}}"
    local supports="${6:-}"
    local m="${SCRATCH}/${tag}_machine_flat.json"
    local p="${SCRATCH}/${tag}_process_flat.json"
    local f="${SCRATCH}/${tag}_filament_flat.json"
    local proj_3mf="t3-prism.${tag}.3mf"
    local sliced_3mf
    if [[ "${supports}" == "supports" ]]; then
        sliced_3mf="t3-prism.${tag}-PETG-supports.gcode.3mf"
    else
        sliced_3mf="t3-prism.${tag}-PETG.gcode.3mf"
    fi
    local proj_outdir="${SCRATCH}/proj_${tag}"
    local sliced_outdir="${SCRATCH}/sliced_${tag}"

    echo "==> [${tag}] Flatten profiles"
    flatten machine  "${machine_leaf}"  "${m}"
    flatten process  "${process_leaf}"  "${p}"
    flatten filament "${filament_leaf}" "${f}"
    patch_bed "${m}"
    if [[ "${supports}" == "supports" ]]; then
        echo "==> [${tag}] Patch process profile: enable tree(auto) supports"
        patch_supports "${p}"
    fi

    echo "==> [${tag}] BambuStudio CLI -> ${proj_3mf} (project, re-importable)"
    rm -rf "${proj_outdir}" && mkdir -p "${proj_outdir}"
    LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe \
    xvfb-run -a -s "-screen 0 1280x1024x24" "${BAMBU_APPIMAGE}" \
        --orient 1 --arrange 1 \
        --load-settings  "${m};${p}" \
        --load-filaments "${f}" \
        --export-3mf "${proj_3mf}" \
        --outputdir "${proj_outdir}" \
        "${stl_in}" 2>&1 | tail -2
    cp "${proj_outdir}/${proj_3mf}" "${SLICES_DIR}/${proj_3mf}"

    echo "==> [${tag}] BambuStudio CLI -> ${sliced_3mf} (sliced print job)"
    rm -rf "${sliced_outdir}" && mkdir -p "${sliced_outdir}"
    # Manual filament map is gated by `plate_to_slice != 0`; pass --slice 1.
    # IDEX (H2D) needs Manual mode + an explicit map even with one filament.
    LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe \
    xvfb-run -a -s "-screen 0 1280x1024x24" "${BAMBU_APPIMAGE}" \
        --orient 1 --arrange 1 \
        --load-settings  "${m};${p}" \
        --load-filaments "${f}" \
        --filament-map-mode "Manual" --filament-map "1" \
        --slice 1 \
        --export-3mf "${sliced_3mf}" \
        --outputdir "${sliced_outdir}" \
        "${stl_in}" 2>&1 | tail -2

    # Surface the slice stats (return_code, time, weight) and copy the 3MF in.
    python3 -c "
import json, sys
r = json.load(open(sys.argv[1] + '/result.json'))
print(f'    return_code = {r[\"return_code\"]}, error_string = {r[\"error_string\"]!r}')
for plate in r.get('sliced_plates', []):
    pred = float(plate.get('total_predication', plate.get('main_predication', 0)))
    grams = sum(float(f.get('total_used_g', 0)) for f in plate.get('filaments', []))
    print(f'    plate {plate.get(\"id\")}: time = {pred/3600:.2f} h ({pred/60:.1f} min), weight = {grams:.2f} g')
" "${sliced_outdir}"
    cp "${sliced_outdir}/${sliced_3mf}" "${SLICES_DIR}/${sliced_3mf}"
}

slice_bambu_mm () {
    # Multi-material H2D variant (PLA struts + PETG cables, IDEX).
    #
    # The two STLs (`t3-prism-struts.stl`, `t3-prism-cables.stl`) are
    # rendered above in the SAME world coordinates (both pre-translated to
    # the H2D bed centre) so they form a true assembled tensegrity, not two
    # separate objects on the bed. To get BambuStudio to treat them as
    # parts of one object we:
    #
    #   1. Run with `--assemble` (no `--slice`) to merge both STLs into a
    #      single Bambu Studio project (`<object>` with two `<part>`s).
    #      `--assemble + --slice + manual filament map` is unstable in
    #      v02.06.00.51 (segfaults on `--load-filament-ids` with merged
    #      objects), so the slice happens in a follow-up pass.
    #   2. Patch the resulting `Metadata/model_settings.config` so the
    #      cables part is assigned to extruder 2 (PETG) while the struts
    #      part stays on extruder 1 (PLA). The defaults from `--assemble`
    #      put both parts on extruder 1.
    #   3. The resulting `slices/t3-prism.H2D-MM.3mf` opens in Bambu
    #      Studio with both parts already merged into one object and the
    #      correct PLA/PETG extruder assignment per part — the user just
    #      hits Slice / Send to printer.
    #
    # We do NOT emit a sliced `.gcode.3mf` for the multi-material variant
    # from the CLI, because BambuStudio v02.06.00.51's headless slice path
    # does not honour per-part extruder assignment when re-loading a
    # project 3mf as input. The Bambu Studio GUI handles this correctly.
    local tag="$1" machine_leaf="$2" process_leaf="$3"
    local f1_leaf="$4" f2_leaf="$5"
    local m="${SCRATCH}/${tag}_machine_flat.json"
    local p="${SCRATCH}/${tag}_process_flat.json"
    local f1="${SCRATCH}/${tag}_filament1_flat.json"
    local f2="${SCRATCH}/${tag}_filament2_flat.json"
    local proj_3mf="t3-prism.${tag}.3mf"
    local proj_outdir="${SCRATCH}/proj_${tag}"

    echo "==> [${tag}] Flatten profiles (PLA + PETG dual-filament)"
    flatten machine  "${machine_leaf}" "${m}"
    flatten process  "${process_leaf}" "${p}"
    flatten filament "${f1_leaf}"      "${f1}"
    flatten filament "${f2_leaf}"      "${f2}"
    patch_bed "${m}"

    echo "==> [${tag}] BambuStudio CLI --assemble -> ${proj_3mf} (one object, two parts)"
    rm -rf "${proj_outdir}" && mkdir -p "${proj_outdir}"
    LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe \
    xvfb-run -a -s "-screen 0 1280x1024x24" "${BAMBU_APPIMAGE}" \
        --assemble \
        --load-settings  "${m};${p}" \
        --load-filaments "${f1};${f2}" \
        --export-3mf "${proj_3mf}" \
        --outputdir "${proj_outdir}" \
        "${STL_STRUTS}" "${STL_CABLES}" 2>&1 | tail -2

    echo "==> [${tag}] Patch model_settings.config: cables part -> extruder 2 (PETG)"
    python3 "${HERE}/patch_mm_extruder.py" "${proj_outdir}/${proj_3mf}" \
        "t3-prism-cables.stl=2" "t3-prism-struts.stl=1"
    cp "${proj_outdir}/${proj_3mf}" "${SLICES_DIR}/${proj_3mf}"
}

# Bambu Lab H2D — the lab's only printer (see `.github/copilot-instructions.md`).
# Settings match Marcus's `cad/t3-prism/t3-prism.3mf` Bambu Studio project
# (PETG Basic on left extruder, no supports).
slice_bambu "H2D" \
    "Bambu Lab H2D 0.4 nozzle" \
    "0.20mm Standard @BBL H2D" \
    "Bambu PETG Basic @BBL H2D 0.4 nozzle"

# Thick-cable variant + tree(auto) supports. Addresses the spaghetti
# failure on the original print and the "auto-support skipped the top
# strings" failure mode @me-madsen / @achris0520 reported on the
# follow-up GUI re-slice (PR #35 comment 4426810002): cable_d 2.4 -> 3.5
# widens the bridges, and the patched process profile turns on
# tree(auto) supports with `support_critical_regions_only=0` so even
# the relatively-thin top cables register as overhangs.
slice_bambu "H2D-thick" \
    "Bambu Lab H2D 0.4 nozzle" \
    "0.20mm Standard @BBL H2D" \
    "Bambu PETG Basic @BBL H2D 0.4 nozzle" \
    "${STL_THICK}" \
    supports

# Multi-material H2D variant (PLA struts + PETG cables). PLA gives the
# rigid compression skeleton (eventually keeps its role); PETG handles the
# tension cables and is the placeholder for the eventual TPU swap. The
# tensegrity analogy: stiff bars in compression, compliant strings in
# tension, no two compression members touching.
slice_bambu_mm "H2D-MM" \
    "Bambu Lab H2D 0.4 nozzle" \
    "0.20mm Standard @BBL H2D" \
    "Bambu PLA Basic @BBL H2D" \
    "Bambu PETG Basic @BBL H2D 0.4 nozzle"

echo
echo "==> Done."
echo "    STL:        ${STL}"
echo "    STL thick:  ${STL_THICK}"
echo "    STL struts: ${STL_STRUTS}"
echo "    STL cables: ${STL_CABLES}"
echo "    Iso:        ${PNG}"
echo "    Single-material (PETG, full pipeline incl. sliced print job):"
echo "      Project:  ${SLICES_DIR}/t3-prism.H2D.3mf            (Bambu Studio re-importable)"
echo "      Sliced:   ${SLICES_DIR}/t3-prism.H2D-PETG.gcode.3mf (printer upload)"
echo "    Thick-cable variant (cable_d=3.5 mm, tree(auto) supports on):"
echo "      Project:  ${SLICES_DIR}/t3-prism.H2D-thick.3mf                       (Bambu Studio re-importable)"
echo "      Sliced:   ${SLICES_DIR}/t3-prism.H2D-thick-PETG-supports.gcode.3mf   (printer upload)"
echo "    Multi-material (PLA struts + PETG cables, IDEX, project only):"
echo "      Project:  ${SLICES_DIR}/t3-prism.H2D-MM.3mf         (open in Bambu Studio,"
echo "                                                           Slice + Send to printer)"
