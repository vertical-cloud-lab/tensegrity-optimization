// =============================================================================
// Design A2 — Toroidal / donut upset
// =============================================================================
// Replaces the spherical bulb with a torus printed coaxially with the cable
// so the PETG/PLA face bears on the inner curve of the torus. The torus
// distributes the bearing load over a wider annulus than the spherical cap
// of the reference design, giving a lower peak contact stress under the
// repeated drops of the lander demo (#16).
//
// Shape parameters:
//   - Major OD   = upset_od (4.8 mm) → preserves the 1.71× pull-through ratio
//   - Tube Ø     = 1.8 mm → 3-perimeter wall in TPU at 0.4 mm nozzle
//   - Major R    = (major_od - tube_d) / 2 = 1.5 mm
// The cable shaft passes through the hole in the centre of the torus; the
// inner radius of the torus (= 0.6 mm) is < cable radius (1.2 mm) so the
// torus wraps around and grips the cable shaft — this is what closes the
// load path against the PETG/PLA face.
// =============================================================================
include <_common_variants.scad>

major_od = upset_od;            // 4.8 mm overall OD
tube_d   = 1.8;                 // 3-perimeter wall at 0.4 mm nozzle
major_r  = (major_od - tube_d)/2;
torus_x  = upset_x + tube_d/2;  // bearing face flush against +X of node

module torus(major_r, tube_d) {
    rotate_extrude(convexity=4)
        translate([major_r, 0, 0])
            circle(d=tube_d);
}

module designA2_petg() { nodeA_petg(); }

module designA2_tpu() {
    nodeA_tpu_cable();
    // Torus axis coincides with the cable axis (+X) — rotate the XY-plane
    // torus 90° about Y so it sits with its hole facing -X.
    translate([torus_x, 0, 0]) rotate([0, 90, 0])
        torus(major_r, tube_d);
}

module designA2() {
    petg() designA2_petg();
    tpu()  designA2_tpu();
}

designA2();
