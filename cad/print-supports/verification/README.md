# Verification: T3-prism from PR #35, sliced for the **Bambu Lab H2D**

This folder is a one-shot end-to-end check that the §B PLA support recipe
in [`../README.md`](../README.md) actually places supports correctly on a
real tensegrity STL, with no per-geometry painting, and a way to inspect
the resulting toolpaths closely in any STL viewer.

## Slicer: the official Bambu Studio CLI

The lab's production printer is a **Bambu Lab H2D** (0.4 mm nozzle,
single-material PLA mode for the path-(a) recipe; PLA + TPU 85A for
path-(c)). The slicing toolchain is the official **`bambu-studio` CLI**
shipped inside the BambuStudio AppImage
([wiki](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage)),
which is

- the same binary that drives the Bambu Studio GUI on Linux — same
  slicing engine, same `resources/profiles/BBL/` system-profile bundle
  (machine: `Bambu Lab H2D 0.4 nozzle`; process: `0.20mm Standard @BBL
  H2D`; filament: `Bambu PLA Basic @BBL H2D`), same Bambu G-code dialect
  the printer consumes natively;
- usable headlessly under `xvfb` on Ubuntu 24.04 — the 24.04 AppImage
  build links `libsoup-3.0` / `WebKit2GTK-4.1` (both available on
  current Ubuntu) so it runs on a sandboxed CI runner with no desktop
  session. (An earlier revision of this PR used OrcaSlicer as a
  workaround for a `libsoup-2.4` / `WebKit2GTK-4.0` dependency in an
  older Bambu Studio build; that workaround is no longer needed.)

The keys in [`../bambu-pla-tensegrity-process.json`](../bambu-pla-tensegrity-process.json)
are Bambu Studio key names and can be `Process → Add → Import process`'d
straight into the Bambu Studio GUI as well.

> Note: the PyPI package `bambu-cli` is **unrelated** — it's a printer
> control client (MQTT/HTTPS/FTPS for uploading already-sliced files,
> starting jobs, monitoring status). Bambu Lab does not publish a Python
> slicing API; the supported automation path is the AppImage CLI used
> here.

## Inputs

- **Mesh** — `cad/t3-prism/t3-prism.stl` from PR #35 head
  `copilot/get-bambu-sliced-print-t3-prism` (the combined PLA + TPU mesh
  of the bonded-captive-core T3-prism at scale 1.5×, R = 37.5, H = 105,
  twist = 60, strut_d = 9, cable_d = 4.5, joint_d = 7).
- **Machine / process / filament profiles** — pulled straight from the
  BambuStudio AppImage's bundled `resources/profiles/BBL/` directory by
  [`slice_bambu_h2d.py`](slice_bambu_h2d.py); the wiki notes that the
  CLI requires a *flat* config rather than the inherits-chain one used
  by the GUI, so the script walks the inheritance chain itself before
  invoking the slicer.
- **Tensegrity overrides** — [`../bambu-pla-tensegrity-process.json`](../bambu-pla-tensegrity-process.json),
  applied on top of the `0.20mm Standard @BBL H2D` process profile.

## How to reproduce

```bash
# 0. Once: grab the Bambu Studio Ubuntu 24.04 AppImage. The script can
#    either drive the AppImage directly (it will run --appimage-extract
#    on first invocation and cache the result) or use an
#    already-extracted squashfs-root directory.
curl -L -o /tmp/BambuStudio.AppImage \
    https://github.com/bambulab/BambuStudio/releases/download/v02.06.00.51/BambuStudio_ubuntu-24.04-v02.06.00.51-20260417160415.AppImage
chmod +x /tmp/BambuStudio.AppImage
BAMBU=/tmp/BambuStudio.AppImage

# 1. Extract the T3-prism mesh from PR #35 (or, after it merges, from
#    main at the same path):
git show origin/copilot/get-bambu-sliced-print-t3-prism:cad/t3-prism/t3-prism.stl \
    > /tmp/t3-prism.stl
# (post-merge equivalent: `git show main:cad/t3-prism/t3-prism.stl > /tmp/t3-prism.stl`)

# 2. Slice with the Bambu Lab H2D recipe (path (a) — PLA, no enforcer):
python3 cad/print-supports/verification/slice_bambu_h2d.py \
    $BAMBU /tmp/t3-prism.stl /tmp/t3-prism.gcode

# 3. Render the toolpath PNG (numpy + matplotlib):
python3 cad/print-supports/verification/render_gcode.py \
    /tmp/t3-prism.gcode \
    cad/print-supports/verification/t3-prism-pr35-gcode-preview.png

# 4. (Optional but recommended for close visual inspection) convert
#    the sliced gcode back into a per-feature STL — see "Previewing
#    supports as an STL" below.
python3 cad/print-supports/verification/gcode_to_stl.py \
    /tmp/t3-prism.gcode /tmp/t3-prism-supports.stl --support-only
```

For reference, the snapshot committed here was generated from PR #35 head
commit `65d0d3f` (`copilot/get-bambu-sliced-print-t3-prism`) using
BambuStudio 02.06.00.51 (Ubuntu 24.04 AppImage; build string visible in
the gcode header under `; BambuStudio 02.06.00.51`).

## Result (path a — PLA, no enforcer, single-material H2D extruder)

- `t3-prism-pr35-gcode-preview.png` — 3-panel render of every extrusion
  move in the resulting Bambu H2D G-code:
  - **Bottom view, supports only** (the slicer's automatic equivalent of
    Audrey's manual paint pattern).
  - **Iso, object grey + supports orange** — visually confirms every tree
    branch roots at the plate (`z≈0`), none on a member.
  - **First layer (z ≤ 0.25 mm)** — brim, object first layer, support
    touch-points actually on the bed.

### Slice summary (path a, θ = 10°)

| Metric                  | Value                                              |
| ----------------------- | -------------------------------------------------- |
| Slicer                  | BambuStudio 02.06.00.51 (official CLI)             |
| Printer profile         | Bambu Lab H2D 0.4 nozzle                           |
| Filament profile        | Bambu PLA Basic @BBL H2D                           |
| Layers                  | 601                                                |
| Layer height            | 0.20 mm                                            |
| Filament used           | 26.6 cm³ (33.5 g, PLA)                             |
| Estimated print time    | 1 h 41 m 40 s                                      |
| Support style           | `tree(auto)` (Bambu organic tree, single material) |
| Supports on plate only? | yes (`support_on_build_plate_only = 1`)            |
| Overhang threshold      | **10°** (TPU-safe; see below)                      |
| Brim                    | 5 mm outer-only                                    |
| Bridges supported?      | no (`bridge_no_support = 1`)                       |

The support-only bottom view reproduces Audrey's centerline-stripe pattern
without any manual painting, and after dropping `support_threshold_angle`
from 40° to 10° the entire down-facing side of every near-vertical strut
also gets supported all the way to the plate, so the same recipe survives
a TPU print of the same mesh (TPU sags on any shallow overhang PLA would
self-support).

## Previewing supports as an STL — `gcode_to_stl.py`

The 3-panel PNGs are useful for a quick at-a-glance check but they
flatten everything into 2D and you can't rotate / fly through the
geometry. [`gcode_to_stl.py`](gcode_to_stl.py) closes that gap: it
parses every `G1 E…` extrusion move out of the sliced gcode, reifies
each one as a small rectangular prism (layer-height tall, extrusion-line
wide, centered on the toolpath), and writes the result as a binary STL
that loads into any STL viewer (Bambu Studio, Meshlab, FreeCAD, blender,
3D-printable-thing-viewer, etc.).

Filter by slicer "feature" name (PrusaSlicer `;TYPE:` or Bambu/Orca
`;FEATURE:`), or use the shorthand flags:

```bash
# Just the support material (this is what you want for close-up
# inspection of "which surfaces are being held up and how densely"):
python3 cad/print-supports/verification/gcode_to_stl.py \
    /tmp/t3-prism.gcode /tmp/supports.stl --support-only

# Just the object (no supports, no brim):
python3 cad/print-supports/verification/gcode_to_stl.py \
    /tmp/t3-prism.gcode /tmp/object.stl --object-only

# Everything at once, one STL per kind:
python3 cad/print-supports/verification/gcode_to_stl.py \
    /tmp/t3-prism.gcode /tmp/parts --split
# → /tmp/parts-object.stl, /tmp/parts-support.stl, …
```

Two pre-generated support-only STLs are committed here so reviewers can
download and drop them straight into a viewer without re-running the
slicer:

| STL                                              | Source slice               | Triangles | Bytes  |
| ------------------------------------------------ | -------------------------- | --------: | -----: |
| `t3-prism-pr35-th10-supports.stl`                | path (a), θ = 10°          |   111,972 |  5.4 MB |
| `t3-prism-pr35-tpu-enforced-supports.stl`        | path (c), enforcer + θ=10° |   266,868 | 13.3 MB |

(Triangle count is ≈ 12 × number of extrusion segments. The enforcer
version is ~2.4× larger because the enforcer columns force continuous
coverage along the full bottom of every member.)

## Previewing supports **and the part together** — `merge_stls.py`

The supports-only STLs above are the closest-up view of what gets
printed *as support*, but they don't tell you which surface of the
object each branch is holding up. To see both in the same frame, run
[`merge_stls.py`](merge_stls.py) — it concatenates two or more binary
STLs into one, with an optional per-input translation, and a
`--align-first-to-second` flag that translates the first input so its
XY bbox-center matches the second's and its lowest Z sits at z = 0
(this brings a source mesh out of "centered at origin" into the
print-coordinate frame the gcode-derived support STL lives in):

```bash
# Combine source mesh + path-(a) supports into one inspectable STL.
python3 cad/print-supports/verification/merge_stls.py \
    /tmp/t3-prism-th10-object-and-supports.stl \
    /tmp/t3-prism.stl \
    cad/print-supports/verification/t3-prism-pr35-th10-supports.stl \
    --align-first-to-second
```

Two pre-generated combined STLs are committed alongside the
supports-only ones — open them in any STL viewer to see the part (in
its own object group) and the supports (in a second group, colorable
separately) sharing the same coordinate frame:

| STL                                                          | Source slice               | Triangles | Bytes  |
| ------------------------------------------------------------ | -------------------------- | --------: | -----: |
| `t3-prism-pr35-th10-object-and-supports.stl`                 | path (a), θ = 10°          |   136,838 |  6.8 MB |
| `t3-prism-pr35-tpu-enforced-object-and-supports.stl`         | path (c), enforcer + θ=10° |   291,734 | 14.6 MB |

Matplotlib render of the two combined STLs side-by-side (object in
grey, supports in orange; iso + bottom view):

![object + supports preview](t3-prism-pr35-object-and-supports-preview.png)

## Why θ = 10°? — TPU-safe strut-bottom coverage (partial fix)

The first draft of the recipe used `support_threshold_angle = 40` (~40°
from vertical). For PLA on the T3-prism that was fine, but it left the
shallow-overhang under-side of every near-vertical strut completely
unsupported because tilts of ~25–35° from vertical sit below the
threshold. TPU 85A (NinjaFlex-class, E ≈ 12 MPa) can't self-support those
overhangs and would sag.

Dropping the threshold to **10°** flags the entire down-facing surface of
every tilted member as an overhang, so the tree generator builds branches
from the plate all the way along each strut's bottom. The H2D tree-
support generator's response to the threshold change is visible in
`t3-prism-pr35-threshold-comparison.png` and in the numbers below — on
Bambu's `tree(auto)` the slope of "more flagged area = more material" is
not monotonic: at θ = 10° the slicer can merge nearby overhangs into
shared trunks, so it sometimes extrudes *less* support material than at
θ = 40° while still covering more of each strut's underside. On this
mesh, θ = 10° extrudes a touch less than θ = 40°:

| Metric                       | θ = 40° (old) | θ = 10° (new) |        Δ |
| ---------------------------- | ------------: | ------------: | -------: |
| `Support` feature blocks     |           764 |           622 |  −18.6 % |
| `Support interface` blocks   |           214 |            75 |  −65.0 % |
| Print time                   | 1 h 45 m 42 s | 1 h 41 m 21 s |   −4.1 % |

This handles **tilted** struts but is fundamentally **insufficient** for
truly vertical or near-vertical members — see the next section.

To regenerate the comparison panel:

```bash
# slice once at θ = 40° (the old default):
python3 cad/print-supports/verification/slice_bambu_h2d.py \
    $BAMBU /tmp/t3-prism.stl /tmp/t3-prism-th40.gcode \
    --override support_threshold_angle=40

# slice again at θ = 10° (the current recipe):
python3 cad/print-supports/verification/slice_bambu_h2d.py \
    $BAMBU /tmp/t3-prism.stl /tmp/t3-prism-th10.gcode

# render the side-by-side diff:
python3 cad/print-supports/verification/diff_supports.py \
    /tmp/t3-prism-th40.gcode /tmp/t3-prism-th10.gcode \
    cad/print-supports/verification/t3-prism-pr35-threshold-comparison.png
```

## The fundamental problem: overhang analysis can't see vertical cylinders

Lowering `support_threshold_angle` only ever helps for surfaces that
*face downward*. A vertical (or near-vertical) cable cylinder has **no
down-facing surface at all** — its sides face sideways — so **no value
of `support_threshold_angle`, not even 0°, will ever cause the slicer to
place supports under it.** PLA self-supports a vertical cylinder fine
(each layer is a disc resting on the disc below), but TPU 85A — molten,
soft, ~2× softer than TPU 95A — sags layer-to-layer and the cable goes
out of shape.

The only general-purpose fix is **explicit Support Enforcer geometry**:
a separate STL of small vertical prisms (one per member) loaded into the
slicer as Support Enforcer modifier volumes. The slicer then places
supports in the enforcer region *regardless of overhang analysis*. This
is path (c) in [`../README.md`](../README.md) — previously documented as
the "fallback", now mandatory for any TPU-bound print.

## TPU-safe verification: PR #35 T3-prism + path (c) enforcer STL

This re-slice combines path (a) settings with path (c) Support Enforcer
geometry generated by
[`../generate_support_enforcers.py`](../generate_support_enforcers.py).
Every member — strut, top cable, saddle, *and* any near-vertical cable —
gets continuous support coverage along its full XY footprint, all the
way down to the build plate.

- `t3-prism-pr35-enforcers.stl` — Support Enforcer STL emitted by
  `generate_support_enforcers.py --topology t3_prism …` for the PR #35
  T3-prism. 144 triangles, 12 prisms (one per non-bed-contact member;
  the saddle/top cables become rectangular stripes; any member whose
  XY projection is shorter than its stripe width — i.e. truly vertical
  TPU cables — becomes a square footprint column via the
  `--vertical_pad` path, default = `member_d + 0.5 mm`).
- `build_enforcer_3mf.py` — bundles a printable STL and an enforcer STL
  into a single 3MF, marking the second mesh as a `SupportEnforcer`
  volume in `Metadata/Slic3r_PE_model.config`. Bambu Studio inherits
  the PrusaSlicer-style 3MF reader, so the same enforcer 3MF loads
  cleanly into the GUI as well as the CLI.
- `t3-prism-pr35-tpu-enforced-preview.png` — the resulting 3-panel
  gcode preview from the H2D slice. The bottom-view panel now has a
  continuous orange stripe along the full XY projection of every
  member, not just the tilted ones, and the iso panel shows tree
  branches climbing the full length of each strut's underside.
- `t3-prism-pr35-tpu-enforced-supports.stl` — the support-only STL
  produced by `gcode_to_stl.py --support-only` from the enforced
  slice. **This is the artifact to load if you want to inspect
  exactly which surfaces are being held up under the TPU-safe
  recipe.** 266,868 triangles, 13.3 MB binary STL, opens in any
  viewer (verified in Bambu Studio's own "Add Part → Load" dialog
  and in MeshLab).

### How to reproduce the TPU-safe slice

```bash
# 1. T3-prism mesh as above (cad/t3-prism/t3-prism.stl from PR #35).

# 2. Generate the per-member Support Enforcer STL:
python3 cad/print-supports/generate_support_enforcers.py \
    --topology t3_prism --R 37.5 --H 105 --twist 60 \
    --strut_d 9 --cable_d 4.5 \
    --out /tmp/t3_enforcers.stl
# (For arbitrary topologies: --members my_members.json.)

# 3. Bundle the printable mesh and the enforcer STL into one 3MF, with
#    the enforcer marked SupportEnforcer (Bambu Studio's CLI has no
#    "merge with subtype" flag; the helper does the wiring):
python3 cad/print-supports/verification/build_enforcer_3mf.py \
    /tmp/t3-prism.stl /tmp/t3_enforcers.stl /tmp/t3-with-enforcers.3mf

# 4. Slice with the Bambu H2D recipe applied to the enforcer 3MF (the
#    enforcer adds coverage on top of the auto-tree — `enable_support = 1`
#    is already on in the recipe):
python3 cad/print-supports/verification/slice_bambu_h2d.py \
    $BAMBU /tmp/t3-with-enforcers.3mf /tmp/out.gcode

# 5. Render the 3-panel preview:
python3 cad/print-supports/verification/render_gcode.py \
    /tmp/out.gcode \
    cad/print-supports/verification/t3-prism-pr35-tpu-enforced-preview.png \
    --title "T3-prism + enforcer-STL — full bottom coverage on every member (TPU-safe, Bambu H2D)"

# 6. Extract the supports-only mesh for close visual inspection:
python3 cad/print-supports/verification/gcode_to_stl.py \
    /tmp/out.gcode \
    cad/print-supports/verification/t3-prism-pr35-tpu-enforced-supports.stl \
    --support-only
```

### TPU-safe slice metrics (Bambu H2D, BambuStudio CLI)

| Metric                  | Value                                              |
| ----------------------- | -------------------------------------------------- |
| Slicer                  | BambuStudio 02.06.00.51 (official CLI)             |
| Printer profile         | Bambu Lab H2D 0.4 nozzle                           |
| Filament profile        | Bambu PLA Basic @BBL H2D                           |
| Layers                  | 580                                                |
| Layer height            | 0.20 mm                                            |
| Estimated print time    | 3 h 36 m 22 s                                      |
| Support style           | `tree(auto)` + enforcer-restricted                 |
| Supports on plate only? | yes (`support_on_build_plate_only = 1`)            |
| Auto supports?          | yes — additive to enforcer (`enable_support = 1`)  |
| Enforcer volumes        | 12 prisms (one per non-bed-contact member)         |
| `Support` feature blocks    | 695                                            |
| `Support interface` blocks  | 174                                            |
| Brim                    | 5 mm outer-only                                    |
| Bridges supported?      | no (`bridge_no_support = 1`)                       |

The print-time jump from 1 h 41 m → 3 h 36 m is the cost of forcing
continuous bottom coverage along every member's full length — the
per-member enforcer columns are short and dense rather than tall and
sparse, but they multiply across all 12 non-bed-contact members.

### For Bambu Studio GUI users

Bambu Studio has the same enforcer concept exposed in the GUI:
right-click the assembly → **Add Part → Load…** → pick the enforcer STL
→ **Change Type → Support Enforcer**. Use the process settings from
`bambu-pla-tensegrity-process.json` and the slice is equivalent to step
4 above. No 3MF assembly needed (Bambu Studio's GUI does the part-with-
two-volumes wiring).
