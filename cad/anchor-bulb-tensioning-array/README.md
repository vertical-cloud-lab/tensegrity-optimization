# Anchor-bulb tensioning test print array

A 15-specimen DOE-style print plate that sweeps **radial air gap × joint
size** for the **A3 countersunk** anchor head from
[PR #39](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/39)
([`cad/joint-design/A_variants/A3_countersunk.scad`](../joint-design/A_variants/A3_countersunk.scad)),
oriented for **horizontal-cable printing** so the worst-case TPU-bridging
failure mode is exposed in the test.

Closes [#84](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/84).

## What changed from the first revision

Per [@sgbaird-yolo's review](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/85#discussion-on-comment-4462368734)
of the original 12-specimen plate:

| Old | New | Why |
|---|---|---|
| **A1 frustum** rivet-head upset | **A3 countersunk** 90° conical head mating a countersink in the +Y face | Flush, self-centring, ~2.6× the bearing-wall area at the same OD; matches the design called out in [PR #39 comment 4461680803](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/39#issuecomment-4461680803). |
| **Vertical cable** (cable along print +Z) | **Horizontal cable** (cable along build-plate +Y, strut along print +Z) | Vertical-cable printing leaves the air gap trivial — the TPU is laid down on top of itself. The realistic failure mode is **horizontal**, where the TPU has to bridge the bore against gravity → intentional spaghetti / stringing into the gap. This is the failure mode the array is now designed to expose. |
| 3 axes (air gap, pause+lube, PVA sleeve) | **1 axis (air gap) × 1 axis (joint size)** | The H2D has IDEX (two extruders) and the AMS Pro is just a filament store, so a sacrificial-PVA 3rd material is not realistic. Pause+lube is a manual workflow that doesn't survive a multi-specimen plate cleanly. Focus on what works. |
| 12 specimens (TA-G\*/L\*/R\*) | **15 specimens (H-S{0..2}G{0..4})** — 3 node sizes × 5 gaps | Lets us see whether bigger nodes (longer bores) tolerate a different gap than smaller ones. |

## Why we need it

Pre-tensioning the A3 anchor-bulb works by gripping the TPU cable past
the conical head and pulling, so the cable strains until the cone seats
into its countersink and locks. **This only works if the bond between the
PLA bore wall and the TPU cable inside the bore is weak enough to fail at
a tractable pull force.** Plus, since we now print horizontally, we have
a second constraint: the air gap must also be small enough that the TPU
cable still prints as a recognisable cylinder through the bore instead
of stringing/sagging into the gap during the horizontal bore-crossing
extrusion pass.

## Specimen DOE — 3 node sizes × 5 air gaps

All 15 specimens share the **A3 countersunk** head (90° conical TPU head
mating a 90° countersink cut into the +Y face of the PLA node) and a
**2.4 mm TPU 85A cable**, a **6 mm PLA strut**, and a **16 × 26 × 4 mm
anchor tab** (clamped in a vise during the pull test). The DOE varies
only the air gap and the node size.

| ID | Node Ø (mm) | Air gap (mm) | Bore Ø (mm) | Through-bore length (= node Ø, mm) |
|---|:---:|:---:|:---:|:---:|
| **H-S0G0** | 7.5  | 0.1 | 2.6 | 7.5 |
| **H-S0G1** | 7.5  | 0.2 | 2.8 | 7.5 |
| **H-S0G2** | 7.5  | 0.3 | 3.0 | 7.5 |
| **H-S0G3** | 7.5  | 0.4 | 3.2 | 7.5 |
| **H-S0G4** | 7.5  | 0.6 | 3.6 | 7.5 |
| **H-S1G0** | 9.5  | 0.1 | 2.6 | 9.5 |
| **H-S1G1** | 9.5  | 0.2 | 2.8 | 9.5 |
| **H-S1G2** | 9.5  | 0.3 | 3.0 | 9.5 |
| **H-S1G3** | 9.5  | 0.4 | 3.2 | 9.5 |
| **H-S1G4** | 9.5  | 0.6 | 3.6 | 9.5 |
| **H-S2G0** | 12.0 | 0.1 | 2.6 | 12.0 |
| **H-S2G1** | 12.0 | 0.2 | 2.8 | 12.0 |
| **H-S2G2** | 12.0 | 0.3 | 3.0 | 12.0 |
| **H-S2G3** | 12.0 | 0.4 | 3.2 | 12.0 |
| **H-S2G4** | 12.0 | 0.6 | 3.6 | 12.0 |

S1 (node Ø 9.5 mm) matches the PR #39 Phase-3-refined geometry; S2
(node Ø 12.0 mm) matches the dovetail node OD; S0 (node Ø 7.5 mm) is the
smallest sphere that still leaves ≥ 2 PLA wall perimeters around a 3.6 mm
bore at the equator.

## Renders

Iso view of the full plate (~110 × 130 mm footprint, fits any H2D plate):

![Full array iso](renders/tensioning_array_iso.png)

Iso contact-sheet (rows = node size, columns = air gap):

![All specimens montage](renders/all_specimens_montage.png)

X=0 cross-section through one specimen per node size (mid-gap = 0.3 mm),
showing the bore + countersink + conical head:

![Section montage](renders/section_montage.png)

Per-specimen iso PNG and **STL** (one per specimen + `tensioning_array.stl`
for the whole plate) also live in `renders/`.

## Print recipe (Bambu H2D + AMS Pro)

| Extruder | Material | Used in |
|---|---|---|
| **L (left, AMS-fed)** | **PLA** (any brand) | tab + strut + node + bore + countersink |
| **R (right, direct)** | **TPU 85A** (NinjaFlex-class) | cable + conical head + pull handle |

The H2D has **two extruders** (IDEX), not three; the AMS Pro is a filament
store that switches between PLA brands/colours on the L extruder. The TPU
sits on the R extruder full-time.

- **Layer height** 0.2 mm
- **Wall count** 3 perimeters everywhere
- **Orientation** as drawn — strut vertical (+Z), cable horizontal (+Y),
  tab on the bed
- **Brim** 5 mm on each tab footprint
- **Important** — at the bore-crossing layer the TPU extruder has to lay
  down a 2.4 mm cylinder horizontally across an unsupported gap of
  `bore_d - cable_d = 2 × gap_r` mm with a span equal to the node Ø (= 7.5 /
  9.5 / 12.0 mm). This is exactly the failure mode the DOE is testing,
  so **do not** add support material inside the bore.

## Pull-test protocol

1. Snip the brim and inspect each specimen visually: was the cable
   recognisably cylindrical through the bore, or did it sag/string?
   Photograph each specimen at the bore-crossing layer **before** pulling.
2. Clamp the PLA tab in a vise (long axis horizontal, cable axis pointing
   away from the vise).
3. Grip the TPU pull handle ~15 mm past the conical head with a hand-held
   force gauge (e.g. Mark-10 M5-2 or AOSITE 50 N).
4. Pull steadily horizontally at ~10 mm/s and record the **peak force**
   at the instant the cone seats against the countersink. This is the
   pre-tensioning load `F_pre`.
5. Inspect: did the cable tear (failure), did the cone deform plastically
   (suboptimal), or did it seat cleanly with the cable still able to
   carry tendon load (success)?

**Success criterion:** smallest `F_pre` that reliably seats the cone
without cable damage, ideally in the 5–25 N range so a human can
pre-tension by hand.

## Reproducing the renders

```sh
bash cad/anchor-bulb-tensioning-array/render.sh
```

Outputs land in `cad/anchor-bulb-tensioning-array/renders/`: 15 `*_iso.png`,
3 `*_section_X_iso.png`, 15 `*.stl`, the full-plate `tensioning_array_iso.png`
+ `tensioning_array.stl`, and two contact-sheet montages
(`all_specimens_montage.png`, `section_montage.png`).

Requires `openscad` and `imagemagick` (`montage`); on a headless runner it
auto-wraps in `xvfb-run`.

## File layout

```
cad/anchor-bulb-tensioning-array/
├── _common.scad              shared geometry + parameterised specimen module
├── tensioning_array.scad     all 15 specimens on a single build plate
├── H-S{0,1,2}G{0..4}.scad    15 specimens — size index × gap index
├── H-S{0,1,2}G2_section_X.scad   X=0 cutaway per node size, at mid gap (0.3 mm)
├── render.sh                 builds renders/ from the SCAD sources
├── renders/                  PNGs, STLs, and contact-sheet montages
└── README.md                 this file
```

## Notes / next steps

- **Alternative path raised by [@sgbaird-alt](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/85#discussion-on-comment-4462314872):**
  manually thread an elastic cable into single-material PLA prints
  (no co-print of TPU, no anchor-bulb necessary). This array does not
  obviate that path — it is complementary, and stays useful even if the
  manual-threading approach turns out to be the right call for early
  builds, because for any future co-printed tendon (#54) we still need
  to know the limiting air gap.
- The DOE assumes the air-gap response is monotonic in joint size. If the
  three rows disagree on which gap is the winner, the next plate should
  add an intermediate node size (e.g. 10.5 mm) rather than another gap
  value.
- **A3 countersunk** is the chosen geometry per the PR review. If the
  countersink walls themselves fuse to the conical head and prevent
  pull-through at every gap, the fallback is A4 (lobed) or A0 (sphere)
  with the same air-gap × size DOE.
