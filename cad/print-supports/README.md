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

## C. Fallback: explicit Support Enforcer STL

If the `tree(hybrid) + on_build_plate_only` recipe in §B fails on an
exotic topology (e.g. a structure with overhangs Bambu's analyzer doesn't
flag, or with vertices that are bed-contact-but-not-coplanar), use the
geometry-agnostic enforcer generator
[`generate_support_enforcers.py`](generate_support_enforcers.py) to emit
explicit Support Enforcer volumes from a JSON description of the member
graph:

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
Support Enforcer**. Use the same process settings from §B and the slicer
will restrict support generation to the enforcer volumes.

Built-in `--topology` presets cover the catalogue in PR #22 — see
`generate_support_enforcers.py --help` for the current list.
