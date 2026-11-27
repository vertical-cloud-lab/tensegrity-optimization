// =============================================================================
// Design A1 — Truncated cone / frustum (rivet-head) upset
// =============================================================================
// Replaces the spherical bulb of the reference design with a flat-topped
// frustum so the TPU bears against the PETG/PLA face on a flat annulus
// instead of a curved spherical cap. The flat top also lays down cleanly
// under the H2D top-layer pass (no curved free surface).
//
// Shape parameters:
//   - Base OD (against the PETG face) = upset_od (4.8 mm) → preserves the
//     1.71× pull-through ratio of the reference geometry.
//   - Top OD                          = 3.6 mm (75 % of base) → gentle 30°
//     half-angle, self-supporting in TPU 85A on a Bambu H2D without supports.
//   - Height                          = 2.4 mm → ~6 layers at 0.4 mm.
// Bearing area (flat annulus between bore Ø 2.8 and base Ø 4.8) = 6.0 mm²
// (vs. ≈3.4 mm² projected bearing on the reference sphere) → ~75 % more
// load-spreading area at the same OD.
// =============================================================================
include <_common_variants.scad>

base_d  = upset_od;        // 4.8 mm at the PETG face
top_d   = 3.6;             // 75 % of base — 30° half-angle
height  = 2.4;             // 6 layers at 0.4 mm
base_x  = upset_x - 0.3;   // a touch embedded in the +X face for fusion

module designA1_petg() { nodeA_petg(); }

module designA1_tpu() {
    nodeA_tpu_cable();
    // Frustum aligned with the cable axis (+X).
    translate([base_x, 0, 0]) rotate([0, 90, 0])
        cylinder(h=height, d1=base_d, d2=top_d);
}

module designA1() {
    petg() designA1_petg();
    tpu()  designA1_tpu();
}

designA1();
