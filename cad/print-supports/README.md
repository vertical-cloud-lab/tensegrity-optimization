# Single-material PLA tensegrity supports in Bambu Studio

This directory documents a **general-purpose** support recipe for FDM-printing
any tensegrity structure as a single-material PLA part in Bambu Studio
(Bambu Lab printers; Orca/PrusaSlicer use the same option names). It is the
sliceable replacement for the manual paint protocol Audrey documented in
[issue #40](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/40)
and is intended to cover the structure families catalogued in
[issue/PR #22](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/22)
(t3-prism, 4/6-bar prisms, Snelson X, icosahedron, Pugh diamond/zig-zag,
pentagonal ring, stacked-T3 column, Geiger dome, biotensegrity spine, …)
without per-geometry tweaking.

> **TL;DR — no painting required.** Print on the build plate with the
> overhang triangle vertex *down*, set `support_type = tree(hybrid)` with
> `support_on_build_plate_only = 1`, a 5 mm brim, and Bambu Studio's tree
> generator will autonomously place exactly the centerline stripes Audrey
> would have painted by hand. The settings below were chosen so the same
> profile slices any of the canonical topologies in
> [`models/stl/`](../../models) (PR #22) without re-tuning.

## A. Orientation (one rule, applies to all topologies)

Orient the part so that **exactly the three bed-contact vertices touch
`z = 0`**. For:

| Topology              | Bed-contact vertices                    |
| --------------------- | --------------------------------------- |
| T3 / 4-bar / 6-bar prism | bottom triangle / quad / hexagon       |
| Snelson X-module      | bottom strut endpoints                  |
| Icosahedron / 6-bar wheel | one face (3 vertices) flat to plate  |
| Pugh diamond / zig-zag column | bottom layer triangle               |
| Pentagonal ring       | bottom pentagon                         |
| Stacked-T3 column     | bottommost t3 triangle                  |
| Geiger cable dome     | tension-ring nodes                      |

Bambu Studio's **Auto orient** (`A` key) almost always picks this for
tensegrity geometries because their projected-area-minimum lies on a flat
node ring. If it doesn't, manually rotate so a flat node ring sits on the
plate.

## B. Process settings — single-material PLA

These are the per-process overrides relative to the stock
`0.20 mm Standard @BBL X1C` PLA profile. Names match the keys Bambu Studio
writes to `process.json` inside the `.3mf` (so they can be diffed against
Audrey's `tree(manual)` slice).

| Key                              | Value           | Why |
| -------------------------------- | --------------- | --- |
| `enable_support`                 | `1`             | turn on supports |
| `support_type`                   | `tree(hybrid)`  | tree branches under overhangs *and* a thin grid under flat overhangs; equivalent to Audrey's `tree(manual)` once `on_build_plate_only` is set, but driven by the slicer's overhang analysis instead of paint flags |
| `support_on_build_plate_only`    | `1`             | branches drop to the plate, never onto a member — matches the painted-from-the-bottom-view rule |
| `support_threshold_angle`        | `10`            | low enough that the entire down-facing side of every tilted strut is flagged as overhang and gets supported all the way to the plate — same recipe must survive TPU (which can't self-support shallow overhangs the way PLA can). At θ=10° only truly vertical surfaces (< 10° from vertical) are skipped, so the joint-sphere overlaps at each vertex are still ignored while the near-vertical strut sections gain full bottom-stripe coverage. |
| `support_object_xy_distance`     | `0.35`          | leaves a clean gap around each cable so supports peel cleanly |
| `support_top_z_distance`         | `0.2`           | one layer gap; peels with no scarring on PLA |
| `support_interface_top_layers`   | `2`             | enough for stable touch-points, still snaps off |
| `support_interface_bottom_layers`| `0`             | not needed when `on_build_plate_only = 1` |
| `support_interface_pattern`      | `rectilinear`   | breaks cleanly off PLA |
| `support_base_pattern`           | `default`       | tree(hybrid) ignores this; left at default |
| `tree_support_branch_distance`   | `2.5`           | dense enough that ~Ø3 mm cables get touch-points along their full length, matching Audrey's "stripe" coverage |
| `tree_support_tip_diameter`      | `0.8`           | minimum tip width — keeps the contact print to ~1/3 of the cable's projected width, the same fraction Audrey paints |
| `tree_support_branch_diameter`   | `2.0`           | sturdy enough to bridge from plate up to a 70 mm-tall T3 prism without toppling |
| `tree_support_branch_angle`      | `40`            | branches can splay outward to reach saddle cables without colliding with struts |
| `tree_support_wall_count`        | `0`             | thin-wall branches, easier to remove |
| `bridge_no_support`              | `1`             | the three bottom-triangle cables bridge between bed-contact vertices and don't need supports — PLA bridges 30+ mm at 100 mm/s cleanly |
| `thick_bridges`                  | `0`             | smoother bottom on the bridged cables |
| `brim_type`                      | `outer_only`    | tensegrity nodes have tiny plate-contact footprints; brim is the cheapest insurance against tip-over mid-print |
| `brim_width`                     | `5`             | 5 mm is enough for a Ø7 mm joint sphere; raise to 8 mm for taller stacks |

### Why `tree(hybrid)` instead of `tree(manual)` or paint?

Audrey's original `tree(manual)` slice puts the slicer in a mode where it
*only* respects painted seed-triangles. That works for one part but is
laborious and gets wiped whenever the source mesh is regenerated. The
combination above gives an automated equivalent:

- `tree(hybrid)` uses the slicer's overhang analysis, so the seed pattern
  is recomputed every time you re-slice — no painting state to lose.
- `support_on_build_plate_only = 1` forces every tree branch to root at the
  plate, so supports never touch a member from the side or top (Audrey's
  bottom-view-only constraint).
- `support_threshold_angle = 10` means the slicer flags the entire
  down-facing side of every tilted member (struts included) as an
  overhang, so trees climb from the plate all the way along each strut's
  bottom. The original draft used θ=40° which left near-vertical struts
  unsupported — fine for PLA but unsafe for TPU (which sags on any shallow
  overhang). At θ=10° only true vertical surfaces (joint-sphere overlaps
  at each vertex, true bed-contact cones) are still skipped, preserving
  Audrey's "do not paint at vertex overlaps" rule there.
- `tree_support_tip_diameter = 0.8` combined with
  `tree_support_branch_distance = 2.5` reproduces the ~1/3-of-member-width
  centerline stripe coverage.

### One-shot import

A ready-to-load `process.json` snippet (drop into Bambu Studio →
`Process → Add → Import process`) is included as
[`bambu-pla-tensegrity-process.json`](bambu-pla-tensegrity-process.json).

## C. TPU-safe / multi-material: §B settings **+ Support Enforcer STL**

Path §B alone is sufficient when the part is single-material PLA, because
the slicer's overhang analysis can detect the down-facing surfaces of
every tilted strut. **It is not sufficient when any member is printed in
TPU** (or when a member is vertical). The reason is fundamental, not a
the slicer's overhang analysis can detect the down-facing surfaces of
every tilted strut. **It is not sufficient when any member is printed in
TPU** (or when a member is vertical). The reason is fundamental, not a
threshold-tuning problem:

> The slicer's overhang analysis only ever flags surfaces that **face
> downward**. A vertical (or near-vertical) cable cylinder has **no
> down-facing surface at all** — its sides face sideways — so **no
> value of `support_threshold_angle`, not even 0°, will ever cause the
> slicer to place supports under it.** PLA self-supports a vertical
> cylinder fine (each layer is a disc resting on the disc below), but
> TPU 85A — molten, soft, ~2× softer than TPU 95A — sags
> layer-to-layer and the cable goes out of shape.

The fix is to bypass overhang analysis for those members entirely by
loading an **explicit Support Enforcer modifier mesh** alongside the
printable part. The slicer then forces supports in the enforcer volume
regardless of orientation:

```bash
# 1. Generate a per-member enforcer STL (geometry-agnostic — see §D):
python3 cad/print-supports/generate_support_enforcers.py \
    --topology t3_prism --R 37.5 --H 105 --twist 60 \
    --strut_d 9 --cable_d 4.5 \
    --out enforcers.stl

# 2. In Bambu Studio (single-material PLA *or* multi-material PLA+TPU):
#    a. Open the printable part normally.
#    b. Right-click the assembly → Add Part → Load… → pick `enforcers.stl`.
#    c. Right-click the new sub-part → Change Type → Support Enforcer.
#    d. Apply the §B process settings and slice.
```

The same `bambu-pla-tensegrity-process.json` settings from §B work
unchanged — `support_on_build_plate_only = 1` still applies inside the
enforcer region, so branches still root at the plate, never on a
member. The enforcer geometry simply tells the slicer *which XY columns
must be supported regardless of overhang shape*.

A full PrusaSlicer-CLI end-to-end verification on the PR #35 T3-prism
(every member gets continuous bottom coverage, including any that the
auto-tree analysis missed) is in
[`verification/`](verification/) — see
`t3-prism-pr35-tpu-enforced-preview.png` and the `build_enforcer_3mf.py`
helper used to bundle the printable + enforcer meshes into one 3MF.

## D. Geometry-agnostic enforcer generator

[`generate_support_enforcers.py`](generate_support_enforcers.py) takes
an arbitrary member graph and emits one vertical rectangular prism per
member:

```bash
# 1. describe your structure (or use one of the bundled topology presets)
python3 cad/print-supports/generate_support_enforcers.py \
    --topology t3_prism --R 37.5 --H 105 --twist 60 \
    --strut_d 9 --cable_d 4.5 \
    --out enforcers.stl

# 2. or feed an arbitrary member graph
python3 cad/print-supports/generate_support_enforcers.py \
    --members my_members.json --out enforcers.stl
#   where my_members.json is a list of
#   {"p1":[x,y,z], "p2":[x,y,z], "d":<diameter_mm>,
#    "trim_ends":true|false}
```

Then in Bambu Studio: right-click the assembly → **Add Part → Load…** →
pick `enforcers.stl` → right-click the new sub-part → **Change Type →
Support Enforcer**. Use the same process settings from §B.

**Vertical / near-vertical members are handled automatically.** Any
member whose XY projection is shorter than its enforcer stripe width
(i.e. a literally vertical cable, or one whose endpoints have nearly
identical X/Y) is emitted as a small square footprint column under the
member's lower endpoint instead of being silently skipped — this is the
case the slicer's overhang analysis cannot ever cover. Override the
default footprint size with `--vertical_pad <mm>` if you need a tighter
or wider column.

Built-in `--topology` presets cover the catalogue in PR #22 — see
`generate_support_enforcers.py --help` for the current list.
