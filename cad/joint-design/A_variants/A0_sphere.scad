// =============================================================================
// Design A0 — Reference: spherical bulb (the original Phase-3 geometry)
// =============================================================================
// Included here purely as the visual baseline so the four alternative upset
// shapes (frustum, torus, countersunk, lobed, mushroom) have something to
// be montaged against. Geometry is identical to `A_anchor_bulb.scad`.
// =============================================================================
include <_common_variants.scad>

bulb_d   = upset_od;                // 4.8 mm sphere upset
bulb_off = upset_x + bulb_d/2 - 0.5; // a little embedded into the +X face

module designA0_petg() { nodeA_petg(); }

module designA0_tpu() {
    nodeA_tpu_cable();
    translate([bulb_off, 0, 0]) sphere(d=bulb_d);
}

module designA0() {
    petg() designA0_petg();
    tpu()  designA0_tpu();
}

designA0();
