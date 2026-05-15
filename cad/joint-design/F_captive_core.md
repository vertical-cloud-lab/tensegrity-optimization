# Design F — Captive TPU core inside PETG/PLA outer shell

In response to PR #38 comment 4461700096:

> let's go with a design that has a ball on the outside with tpu on the
> inside (rather than a full feedthrough), sort of like an inner ball/mass
> surrounded by the outer ball, though of course it doesn't have to be an
> exact ball and stick model if we want to reduce stresses (e.g., filet
> the interface between the ball and stick slightly so it's a bit more
> like a tear drop)

and the cross-referenced material-interlock note from @achris0520
(<https://github.com/vertical-cloud-lab/byu-vcl/issues/82#issuecomment-4456499040>):

> Materials that do not bond together when printing can be set to
> interlock beams on certain layers, which keeps them from sliding apart

## Concept

A *non-feed-through* anchor: the TPU 85A "knot" lives entirely inside an
outer PETG/PLA shell. The cable enters/exits the shell through one small
bore on +X; the load-bearing TPU mass (the inner ball) is too big to fit
back out through that bore, so the cable is mechanically captive even
though PETG/PLA-TPU has no chemical bond.

| Feature | Value | Purpose |
|---|---:|---|
| Outer shell OD | 12.0 mm | Hosts the captive cavity + teardrop fillet |
| Cavity ID | 8.0 mm | Print-in-place gap around the core |
| TPU core OD | 7.0 mm | Inner mass (cannot exit the 2.8 mm bore) |
| Radial clearance (gap) | 0.5 mm | Per-side print-in-place clearance |
| Exit bore Ø | 2.8 mm | Single-sided cable exit (+X only) |
| Cable Ø | 2.4 mm | TPU 85A tendon |
| Pull-out ratio (core/bore) | 7.0 / 2.8 = **2.5×** | vs. 1.71× for Phase-3 A |
| Teardrop fillet seed | strut\_d × 1.10 | Smooth strut→shell blend |
| Interlock teeth/ring | 8 | Eight per ring, ±0.6 mm Z stagger |
| Tooth (h × w × t) | 1.2 × 1.6 × 0.8 mm | Radial × tangential × axial |

## Why a teardrop, not a sphere-on-stick?

The hull of the spherical shell with a small reference sphere placed
1.5 mm below it gives a smooth blend between the cylindrical strut and
the shell — no sharp re-entrant corner where a stress riser would form
under bending or impact. Conceptually identical to filleting a
machinist's eye-bolt, but generated implicitly by the convex hull rather
than a Boolean fillet.

## Why interlock teeth (per @achris0520)?

PETG/PLA does not chemically bond to TPU. Designs A0–A5 rely on a
mechanical pull-through ratio between the upset OD and the bore OD, but
nothing prevents the upset from rotating, ratcheting, or wearing through
the bore lip across n≥20 reuse drops. Two staggered rings of teeth fix
that:

- **PETG/PLA inward ring** at z = +0.6 mm — eight 1.2 × 1.6 × 0.8 mm
  bricks protruding from the shell ID into the print-in-place gap.
- **TPU outward ring** at z = -0.6 mm — eight matching bricks rotated by
  half a sector (22.5°) from the shell ring.

The two rings are radially long enough to overlap inside the gap but
axially separated, so they print past each other (no fused contact).
Once the print is finished, the two rings' radial overlap means the core
cannot translate ±Z with respect to the shell unless the teeth shear
through each other — a much stiffer failure mode than simple
shell-to-core friction.

This is exactly the mechanism @achris0520 described: the materials still
do not bond chemically, but they cannot slide apart.

## Print orientation (Bambu H2D IDEX)

Strut along +Z (down), shell at the top of the build. The captive core
prints layer-by-layer as a TPU print-in-place inside the PETG/PLA shell;
the +X bore is horizontal and bridges over a 2.8 mm gap (well within the
H2D's bridging capability). The teardrop fillet is naturally
self-supporting.

## Reproduce

```bash
bash cad/joint-design/render_F.sh
```

Outputs `renders/F_captive_core_iso.png`, `_section_X_iso.png`,
`_section_Y_iso.png`, `_section_Z_iso.png`, the
`F_captive_core_grid_montage.png` 4-up tile, and the `F_captive_core.stl`.

## Open design questions

- **Tooth count and stagger** — 8 teeth × 22.5° stagger is a starting
  point; 4 / 6 / 12 ring densities and tighter Z stagger (0.4 mm = 2
  layers) are worth a sweep.
- **Shell-cavity geometry** — a sphere is the simplest cavity but a
  prolate spheroid aligned with the cable axis would distribute pull-out
  load over more cavity wall.
- **Core shape** — making the core itself a torus around the cable axis
  could let the cable shear stress couple into hoop tension on the core,
  similar to the Khatri 2024 / Ye 2023 sleeve concept (Design C) but
  enclosed.

These are all in scope for the Phase-4 results pending from
`LITERATURE_HIGH f9804247` and `ANALYSIS e9a1f4cc`.
