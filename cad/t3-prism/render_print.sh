#!/usr/bin/env bash
# ============================================================================
# Tensegrity Optimization — T3-prism Bambu print-prep pipeline.
#
# Issue: "Get a bambu sliced print for a T3-prism" — pure PETG, single
# part, sliced into a real Bambu Lab `.gcode.3mf` (the format Bambu
# firmware natively expects). Renders the parametric OpenSCAD model to a
# printable STL, sanity-checks the mesh, generates an iso preview PNG,
# and produces Bambu `.gcode.3mf` jobs for two common Bambu beds:
#
#   * Bambu Lab X1 Carbon (256x256 plate) with `Bambu PETG Basic @BBL X1C`
#   * Bambu Lab A1 mini   (180x180 plate) with `Generic PETG @BBL A1M`
#     (A1 mini does not ship a "Bambu PETG Basic" preset)
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
#   5. Slice headlessly under `xvfb-run` + software GL.
#
# Outputs (next to this script):
#   t3-prism.stl                                  Watertight, single-part PETG body
#   t3-prism-iso.png                              OpenSCAD iso preview
#   slices/t3-prism.X1C-PETG.gcode.3mf            Bambu X1C, native .gcode.3mf
#   slices/t3-prism.A1mini-PETG.gcode.3mf         Bambu A1 mini, native .gcode.3mf
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
PNG="${HERE}/t3-prism-iso.png"
SLICES_DIR="${HERE}/slices"
SCRATCH="${SCRATCH:-/tmp/t3-prism}"
mkdir -p "${SLICES_DIR}" "${SCRATCH}"

# Pinned BambuStudio version (matches powder-doser PR #23 verification).
BAMBU_VERSION="${BAMBU_VERSION:-v02.06.00.51}"
BAMBU_APPIMAGE="${BAMBU_APPIMAGE:-${SCRATCH}/bambu.AppImage}"
BAMBU_URL="${BAMBU_URL:-https://github.com/bambulab/BambuStudio/releases/download/${BAMBU_VERSION}/BambuStudio_ubuntu-24.04-${BAMBU_VERSION}-20260417160415.AppImage}"

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

slice_bambu () {
    local tag="$1" machine_leaf="$2" process_leaf="$3" filament_leaf="$4"
    # Optional 5th arg: "idex" → pass --filament-map-mode Manual --filament-map 1
    # (required on multi-extruder Bambu printers like the H2D, even with a
    # single filament; see powder-doser PR #23 for the empirical caveat).
    local mode="${5:-single}"
    local m="${SCRATCH}/${tag}_machine_flat.json"
    local p="${SCRATCH}/${tag}_process_flat.json"
    local f="${SCRATCH}/${tag}_filament_flat.json"
    local outdir="${SCRATCH}/out_${tag}"
    local out3mf="t3-prism.${tag}-PETG.gcode.3mf"

    echo "==> [${tag}] Flatten profiles"
    flatten machine  "${machine_leaf}"  "${m}"
    flatten process  "${process_leaf}"  "${p}"
    flatten filament "${filament_leaf}" "${f}"
    patch_bed "${m}"

    echo "==> [${tag}] BambuStudio CLI -> ${out3mf}"
    rm -rf "${outdir}" && mkdir -p "${outdir}"
    local idex_args=()
    local slice_idx=0
    if [[ "${mode}" == "idex" ]]; then
        # Manual filament map is gated by `plate_to_slice != 0`; pass --slice 1.
        idex_args=(--filament-map-mode "Manual" --filament-map "1")
        slice_idx=1
    fi
    LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe \
    xvfb-run -a -s "-screen 0 1280x1024x24" "${BAMBU_APPIMAGE}" \
        --orient 1 --arrange 1 \
        --load-settings  "${m};${p}" \
        --load-filaments "${f}" \
        "${idex_args[@]}" \
        --slice "${slice_idx}" \
        --export-3mf "${out3mf}" \
        --outputdir "${outdir}" \
        "${STL}" 2>&1 | tail -3

    # Surface the slice stats (return_code, time, weight) and copy the 3MF in.
    python3 -c "
import json, sys
r = json.load(open(sys.argv[1] + '/result.json'))
print(f'    return_code = {r[\"return_code\"]}, error_string = {r[\"error_string\"]!r}')
for plate in r.get('sliced_plates', []):
    pred = float(plate.get('total_predication', plate.get('main_predication', 0)))
    grams = sum(float(f.get('total_used_g', 0)) for f in plate.get('filaments', []))
    print(f'    plate {plate.get(\"id\")}: time = {pred/3600:.2f} h ({pred/60:.1f} min), weight = {grams:.2f} g')
" "${outdir}"
    cp "${outdir}/${out3mf}" "${SLICES_DIR}/${out3mf}"
}

# Bambu X1 Carbon (256x256), Bambu PETG Basic
slice_bambu "X1C" \
    "Bambu Lab X1 Carbon 0.4 nozzle" \
    "0.20mm Standard @BBL X1C" \
    "Bambu PETG Basic @BBL X1C"

# Bambu A1 mini (180x180), Generic PETG (A1 mini does not ship a
# "Bambu PETG Basic" preset).
slice_bambu "A1mini" \
    "Bambu Lab A1 mini 0.4 nozzle" \
    "0.20mm Standard @BBL A1M" \
    "Generic PETG @BBL A1M"

# Bambu Lab H2D — the lab's actual printer. IDEX, so requires manual
# filament-map setup even with one filament. Settings match the
# `cad/t3-prism/t3-prism.3mf` Bambu Studio project that Marcus uploaded
# (PETG Basic on left extruder, no supports).
slice_bambu "H2D" \
    "Bambu Lab H2D 0.4 nozzle" \
    "0.20mm Standard @BBL H2D" \
    "Bambu PETG Basic @BBL H2D 0.4 nozzle" \
    "idex"

echo
echo "==> Done."
echo "    STL:     ${STL}"
echo "    Iso:     ${PNG}"
echo "    3MF:     ${SLICES_DIR}/t3-prism.{X1C,A1mini}-PETG.gcode.3mf"
