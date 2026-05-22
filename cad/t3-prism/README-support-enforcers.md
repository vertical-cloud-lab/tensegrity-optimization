# Automating Audrey's manual support paint

Automates the manual support-painting protocol from
[issue #40](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/40)
(originally posted by [@achris0520](https://github.com/achris0520) in
[issue #35 comment 4520949470](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/35#issuecomment-4520949470)).

> From the BOTTOM VIEW of the part, paint supports manually onto the members
> along each member's center axis, only about a third the thickness of the
> projected view of each member so that when generated, the supports only
> lightly touch the bottom of the members. Do not paint supports where members
> begin to overlap at each vertex, except for the three vertices that directly
> touch the build plate. Only those three vertices should be connected to each
> other in a triangular fashion by painted supports. Remember to paint
> supports only from the BOTTOM VIEW.
>
> — @achris0520, manual support documentation

`generate_support_enforcers.py` emits an STL of small vertical rectangular
prisms — one per painted stripe — sized and positioned exactly the same way
Audrey paints by hand:

| Member family             | Stripe width             | Trimmed at vertex? |
| ------------------------- | ------------------------ | ------------------ |
| 3 struts                  | `strut_d × 1/3`          | yes (joint radius) |
| 3 top-triangle cables     | `cable_d × 1/3`          | yes                |
| 3 saddle cables           | `cable_d × 1/3`          | yes                |
| 3 bottom-triangle cables  | `cable_d × 1/3`          | **no** (Audrey's exception — connects the three bed-contact vertices) |

Each stripe is extruded vertically from `z = 0` (bed) up to
`max(p1.z, p2.z) + z_headroom`, so it spans the full column under the
painted region.

## Usage

```bash
# defaults match t3-prism.scad at scale_factor = 1.5 (the scale used in
# Audrey's manual-paint screenshot, assembly bbox ~68.7 x 110.0 x 57.1 mm)
python3 cad/t3-prism/generate_support_enforcers.py \
    --out cad/t3-prism/t3-prism-support-enforcers.stl \
    --preview cad/t3-prism/t3-prism-support-enforcers.png
```

All geometry parameters are exposed as CLI flags
(`--R`, `--H`, `--twist`, `--strut_d`, `--cable_d`, `--joint_d`,
`--stripe_frac`, `--trim_joint_radii`, `--z_headroom`,
`--bottom_triangle_extra_w`). Defaults track
[`t3-prism.scad`](t3-prism.scad).

## Loading the enforcer in Bambu Studio

1. Load your t3-prism assembly (`t3-prism-struts.stl` +
   `t3-prism-cables.stl`) on plate 1, oriented the same way you would for
   the manual workflow.
2. Right-click the assembly → **Add Part → Load…** → pick
   `t3-prism-support-enforcers.stl`. It will appear as a sub-part of the
   assembly at the same world coordinates.
3. Right-click the new sub-part → **Change Type → Support Enforcer**.
4. Verify the per-object support overrides match Audrey's manual slice
   (these are what `tree(manual)` reads from):
   - `enable_support = 1`
   - `support_type = tree(manual)`
   - `support_on_build_plate_only = 1`
   - `support_threshold_angle = 30`
5. Slice. Support trees will appear only inside the enforcer prisms,
   touching the underside of each member just like in
   [`manual_supports_tips.png`](https://github.com/user-attachments/files/28156629/t3-prism.H2D-MM-PLAstruts-TPUcables_ORIGINAL_MANUAL_SLICE.gcode.zip).

## Why an enforcer STL instead of saving the painted .3mf?

The painted supports in Bambu Studio's GUI are stored as per-triangle
seed-fill flags on the model mesh, which means:

- They are **rebaked whenever you regenerate the source mesh** (e.g. tweak
  `scale_factor` in `t3-prism.scad` and re-run `render_print.sh`).
- They are **mesh-tessellation-dependent** — re-exporting the STL with a
  different `$fn` shifts every painted triangle.

A standalone enforcer STL sidesteps both problems: the paint pattern is
defined purely by `R`, `H`, `twist`, and the member diameters, so it
regenerates from scratch in <0.1 s for any new design and is unaffected by
mesh re-tessellation.
