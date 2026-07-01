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
STL_STRUTS="${HERE}/t3-prism-struts.stl"
STL_STRUTS_SCAFFOLD="${HERE}/t3-prism-struts-scaffold.stl"
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

# `offset_z` lifts the geometry so its lowest point sits at the build-plate
# z=0. With the captive-core joints (default since PR #35 comment 4511036510)
# the bottom-vertex PLA shell underside is at SCAD z=-captive_shell_od/2
# ≈ -8.15 mm, but the flat bottom accelerometer key-seats
# (`add_accel_mount_bottom`, default since PR #35 / PR #67 2026-07-01) hang a
# further `accel_drop()` below that, making the true lowest feature the flat
# key-seat cap at SCAD z ≈ -18.29 mm (scale 1.5). We lift by +18.29 mm so the
# three coplanar flat caps land on the bed (a stable 3-point flat base). The
# cables STL inherits the SAME world-Z bounding box via the `cables_z_anchor()`
# spike inside `t3_prism_cables()` (which now also extends downward by
# `accel_drop()`), so Bambu Studio's per-part auto-bed-placement applies the
# same z offset to both halves and the TPU cables stay aligned with the joints
# (fixes the "horizontal cables too low at top and bottom" misalignment
# reported above PR #35 comment 4511036510). With `add_accel_mount_bottom=false`
# drop this back to 8.15; with `use_captive_core=false` too, drop to 3.5.
OFFSET_Z="${OFFSET_Z:-18.29}"
echo "==> OpenSCAD render -> ${STL_STRUTS##*/} (multi-material: rigid half / PLA, bed-centered)"
xvfb-run -a openscad -o "${STL_STRUTS}" --export-format=binstl \
    -D 'part="struts"' -D 'offset_x=175' -D 'offset_y=160' -D "offset_z=${OFFSET_Z}" "${SCAD}"

echo "==> OpenSCAD render -> ${STL_CABLES##*/} (multi-material: tension half / PETG, bed-centered)"
xvfb-run -a openscad -o "${STL_CABLES}" --export-format=binstl \
    -D 'part="cables"' -D 'offset_x=175' -D 'offset_y=160' -D "offset_z=${OFFSET_Z}" "${SCAD}"

# Production MM variant (PLA struts + TPU cables) needs PLA scaffold pillars
# *modeled* into the strut/PLA half so the slicer can't omit them. Bambu's
# tree(auto) supports skip near-vertical features and even with the most
# permissive thresholds will not scaffold the long unsupported runs of TPU
# cable that wave around mid-print. The scaffold-augmented strut STL emits
# the strut bodies + 7 thin PLA pillars from z=0 up to evenly-spaced
# touch-points on each of the 6 non-bottom cables (the bottom triangle is
# already on the build plate). Per PR #35 comment 4464251671.
echo "==> OpenSCAD render -> ${STL_STRUTS_SCAFFOLD##*/} (struts + 7-point PLA scaffold under TPU cables)"
xvfb-run -a openscad -o "${STL_STRUTS_SCAFFOLD}" --export-format=binstl \
    -D 'part="struts_scaffold"' -D 'offset_x=175' -D 'offset_y=160' -D "offset_z=${OFFSET_Z}" "${SCAD}"

echo "==> admesh manifold check"
admesh -fundecvb "${SCRATCH}/t3-prism-clean.stl" "${STL}" \
    | grep -E '(Number of parts|disconnected|Degenerate|Volume)' | head -6
admesh -fundecvb "${SCRATCH}/t3-prism-struts-clean.stl" "${STL_STRUTS}" \
    | grep -E '(Number of parts|disconnected|Degenerate|Volume)' | head -6
admesh -fundecvb "${SCRATCH}/t3-prism-cables-clean.stl" "${STL_CABLES}" \
    | grep -E '(Number of parts|disconnected|Degenerate|Volume)' | head -6
admesh -fundecvb "${SCRATCH}/t3-prism-struts-scaffold-clean.stl" "${STL_STRUTS_SCAFFOLD}" \
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

enable_supports () {
    # Enable supports in a flattened process profile. Iteration history:
    #
    #   * 9f28b57: turned supports ON with `support_threshold_angle=30`.
    #     Caught the horizontal top cables (90° overhang) but skipped every
    #     near-vertical member.
    #   * THIS REVISION (PR #35 comment 4464152505): the user's photo of the
    #     scaled-up print shows supports only under the lower triangle and
    #     under the horizontal top cables — nothing scaffolding the three
    #     struts (B_i -> T_i) or the three saddle cables (B_{i+1} -> T_i),
    #     which then wave during printing because TPU 85A can't hold itself.
    #
    # Geometry at scale_factor=1.5 (`R=30`, `H=75`): the strut chord between
    # B_i and T_i has horizontal run = 2*R*sin(30°) = 30 mm and vertical run
    # = 75 mm, so the strut tilts only ~21.8° from vertical (~68.2° from
    # horizontal). Bambu's `support_threshold_angle` is the *overhang angle
    # from vertical*; a feature gets supports when its tilt EXCEEDS the
    # threshold. With the default 30° threshold the strut at 21.8° falls
    # BELOW the trigger, so the slicer skips it entirely. Saddle cables sit
    # in the same regime.
    #
    # Fix: drop the threshold to 10° so anything tilted more than 10° from
    # vertical is scaffolded (catches all struts + saddles + top cables),
    # densify the tree branches (`tree_support_branch_distance` 5.0 -> 2.0
    # so multiple branches encircle each thin pillar instead of one lonely
    # branch per region), beef up the trunks (`tree_support_branch_diameter`
    # 2.0 -> 3.0, `tree_support_wall_count` 0 -> 2 for stiffer scaffolding
    # against the TPU pulling sideways), and disable
    # `support_critical_regions_only` so the slicer doesn't restrict
    # supports to the most-extreme overhangs and skip everything in
    # between. Adds two interface layers (`support_interface_top_layers`)
    # so removing the supports leaves a cleaner cable surface.
    python3 -c "
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d['enable_support']                    = '1'
d['support_type']                      = 'tree(auto)'
d['support_threshold_angle']           = '10'
d['support_on_build_plate_only']       = '0'
d['support_critical_regions_only']     = '0'
d['tree_support_branch_angle']         = '40'
d['tree_support_branch_distance']      = '2'
d['tree_support_branch_diameter']      = '3'
d['tree_support_wall_count']           = '2'
d['support_interface_top_layers']      = '2'
d['support_interface_bottom_layers']   = '2'
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
    local tag="$1" machine_leaf="$2" process_leaf="$3" filament_leaf="$4"
    local m="${SCRATCH}/${tag}_machine_flat.json"
    local p="${SCRATCH}/${tag}_process_flat.json"
    local f="${SCRATCH}/${tag}_filament_flat.json"
    local proj_3mf="t3-prism.${tag}.3mf"
    local sliced_3mf="t3-prism.${tag}-PETG.gcode.3mf"
    local proj_outdir="${SCRATCH}/proj_${tag}"
    local sliced_outdir="${SCRATCH}/sliced_${tag}"

    echo "==> [${tag}] Flatten profiles"
    flatten machine  "${machine_leaf}"  "${m}"
    flatten process  "${process_leaf}"  "${p}"
    flatten filament "${filament_leaf}" "${f}"
    patch_bed "${m}"
    enable_supports "${p}"

    echo "==> [${tag}] BambuStudio CLI -> ${proj_3mf} (project, re-importable)"
    rm -rf "${proj_outdir}" && mkdir -p "${proj_outdir}"
    LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe \
    xvfb-run -a -s "-screen 0 1280x1024x24" "${BAMBU_APPIMAGE}" \
        --orient 1 --arrange 1 \
        --load-settings  "${m};${p}" \
        --load-filaments "${f}" \
        --export-3mf "${proj_3mf}" \
        --outputdir "${proj_outdir}" \
        "${STL}" 2>&1 | tail -2
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
        "${STL}" 2>&1 | tail -2

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
    local struts_stl="${6:-${STL_STRUTS}}"
    local struts_stl_basename
    struts_stl_basename="$(basename "${struts_stl}")"
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
    # Force tree(auto) supports for the MM project too — the top-cable
    # bridges still need scaffolding regardless of which filament fills
    # them (PETG/PLA struts/cables, or the production PLA + TPU pairing).
    # Without this the project opens in Bambu Studio with supports OFF
    # and the user has to remember to flip the toggle before slicing.
    enable_supports "${p}"

    echo "==> [${tag}] BambuStudio CLI --assemble -> ${proj_3mf} (one object, two parts)"
    rm -rf "${proj_outdir}" && mkdir -p "${proj_outdir}"
    LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe \
    xvfb-run -a -s "-screen 0 1280x1024x24" "${BAMBU_APPIMAGE}" \
        --assemble \
        --load-settings  "${m};${p}" \
        --load-filaments "${f1};${f2}" \
        --export-3mf "${proj_3mf}" \
        --outputdir "${proj_outdir}" \
        "${struts_stl}" "${STL_CABLES}" 2>&1 | tail -2

    echo "==> [${tag}] Patch model_settings.config: cables part -> extruder 2 (PETG)"
    python3 "${HERE}/patch_mm_extruder.py" "${proj_outdir}/${proj_3mf}" \
        "t3-prism-cables.stl=2" "${struts_stl_basename}=1"
    cp "${proj_outdir}/${proj_3mf}" "${SLICES_DIR}/${proj_3mf}"
}

# Bambu Lab H2D — the lab's only printer (see `.github/copilot-instructions.md`).
# Settings match Marcus's `cad/t3-prism/t3-prism.3mf` Bambu Studio project
# (PETG Basic on left extruder, no supports).
slice_bambu "H2D" \
    "Bambu Lab H2D 0.4 nozzle" \
    "0.20mm Standard @BBL H2D" \
    "Bambu PETG Basic @BBL H2D 0.4 nozzle"

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

# Multi-material H2D variant with the materials swapped: PETG struts +
# **PLA cables**. Requested in PR #35 comment 4445480059 ("create a
# version of the T3-prism with the cables made of PLA"). PLA on the
# tension members gives a much stiffer "string" (PLA E ≈ 3.3 GPa vs
# PETG E ≈ 2 GPa) and lets the team A/B-test which polymer pair best
# previews the eventual TPU 85A swap. Filament order is swapped relative
# to `H2D-MM`: f1 = PETG (struts/extruder 1), f2 = PLA (cables/extruder
# 2). The mechanical-interlock-at-the-joint discussion (TPU "glove"
# wrapping the strut ends) is being tracked separately in PR #39 — this
# slice keeps the same parametric SCAD geometry and just swaps the
# per-part filament assignment.
slice_bambu_mm "H2D-MM-PLAcables" \
    "Bambu Lab H2D 0.4 nozzle" \
    "0.20mm Standard @BBL H2D" \
    "Bambu PETG Basic @BBL H2D 0.4 nozzle" \
    "Bambu PLA Basic @BBL H2D"

# Multi-material H2D variant — the **production-target** pairing: PLA struts
# + **TPU 85A cables**. Requested in PR #35 comment 4455977731 ("a design
# that uses PLA for the struts and TPU for the cables so [the team] can
# slice and print this file directly"). PLA gives the rigid compression
# skeleton; TPU 85A (NinjaFlex-class, E ≈ 12 MPa secant) gives the
# compliant tension cables that mimic real tensegrity strings. Filament
# slot 1 = PLA (struts/extruder 1), slot 2 = TPU 85A (cables/extruder 2).
# The PLA↔TPU interface has the best peer-reviewed bond data (PLA–TPU butt
# 6.5 MPa, alt-deposition 7.4 MPa, mech-interlock shear ~24 MPa; see
# `edison-trajectories/strut-material-selection-5bb5e5d3-*.md`), making
# this the lowest-risk MM combination for a single-print tensegrity. Per
# PR #39 comment 4427586306, the TPU "glove" / mechanical-interlock joint
# is being tracked separately under joint-design (issue #38) and is not
# baked into the geometry here.
slice_bambu_mm "H2D-MM-PLAstruts-TPUcables" \
    "Bambu Lab H2D 0.4 nozzle" \
    "0.20mm Standard @BBL H2D" \
    "Bambu PLA Basic @BBL H2D" \
    "Bambu TPU 85A @BBL H2D 0.4 nozzle" \
    "${STL_STRUTS_SCAFFOLD}"

echo
echo "==> Render support-extrusion verification PNG (supports baked into g-code)"
python3 "${HERE}/render_supports.py" \
    "${SLICES_DIR}/t3-prism.H2D-PETG.gcode.3mf" \
    "${HERE}/t3-prism.H2D-PETG-supports.png" \
    "t3-prism.H2D-PETG.gcode.3mf (scale 1.5x, cable_d 4.5mm, supports=tree/auto, baked natively by BambuStudio CLI --slice 1)"

echo
echo "==> Done."
echo "    STL:        ${STL}"
echo "    STL struts: ${STL_STRUTS}"
echo "    STL cables: ${STL_CABLES}"
echo "    Iso:        ${PNG}"
echo "    Single-material (PETG, full pipeline incl. sliced print job):"
echo "      Project:  ${SLICES_DIR}/t3-prism.H2D.3mf            (Bambu Studio re-importable)"
echo "      Sliced:   ${SLICES_DIR}/t3-prism.H2D-PETG.gcode.3mf (printer upload)"
echo "    Multi-material (PLA struts + PETG cables, IDEX, project only):"
echo "      Project:  ${SLICES_DIR}/t3-prism.H2D-MM.3mf         (open in Bambu Studio,"
echo "                                                           Slice + Send to printer)"
echo "    Multi-material swap (PETG struts + PLA cables, IDEX, project only):"
echo "      Project:  ${SLICES_DIR}/t3-prism.H2D-MM-PLAcables.3mf"
echo "                                                          (open in Bambu Studio,"
echo "                                                           Slice + Send to printer)"
echo "    Multi-material production target (PLA struts + TPU 85A cables, IDEX, project only):"
echo "      Project:  ${SLICES_DIR}/t3-prism.H2D-MM-PLAstruts-TPUcables.3mf"
echo "                                                          (open in Bambu Studio,"
echo "                                                           Slice + Send to printer)"
