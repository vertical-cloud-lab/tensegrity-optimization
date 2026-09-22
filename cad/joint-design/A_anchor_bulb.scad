// =============================================================================
// Design A — Anchor-bulb spherical node
// =============================================================================
// PETG sphere at each tensegrity vertex with through-holes; TPU cable threads
// through and is terminated in a printed-in-place TPU bulb on the far side.
// Per Edison Phase-3 ANALYSIS 19e0c868 §3 (CAD review) geometry, which
// supersedes the earlier c38a2046 / ce84ddf8 numbers (raises bulb-to-bore
// pull-through ratio from 1.38× to 1.71×):
//   - Node OD ≈ 9.5 mm (was 9.0; cleanly encases the 2.8 mm bore while
//     preserving perimeter thickness)
//   - Through-bore Ø ≈ 2.8 mm (0.4 mm clearance over 2.4 mm cable)
//   - Bulb OD ≈ 4.8 mm (printed-in-place TPU on the far side; 1.71× bore,
//     full 1.0 mm radial TPU bearing against the PETG face)
// One PETG strut enters the node from -Z; one TPU cable passes through it
// horizontally along +X, terminated in a bulb on the +X side.
// =============================================================================
include <_common.scad>

node_d  = 9.5;       // PETG node sphere outer diameter
bore_d  = 2.8;       // through-hole diameter (cable_d + 0.4 mm clearance)
bulb_d  = 4.8;       // TPU bulb outer diameter at far end of cable (1.71× bore)
bulb_off = node_d/2 + 1.5;  // bulb center distance from node center along +X

module designA_petg() {
    difference() {
        union() {
            sphere(d=node_d);
            translate([0, 0, -strut_l]) cylinder(h=strut_l, d=strut_d);
        }
        // Horizontal cable bore along +X (clear right through the node)
        translate([-node_d, 0, 0]) rotate([0, 90, 0])
            cylinder(h=2*node_d, d=bore_d);
    }
}

module designA_tpu() {
    // Cable on the entry (-X) side
    translate([-cable_l, 0, 0]) rotate([0, 90, 0])
        cylinder(h=cable_l, d=cable_d);
    // Cable through the bore + a short stub past the bulb's near face
    translate([-node_d/2 - 0.1, 0, 0]) rotate([0, 90, 0])
        cylinder(h=node_d + 1.5, d=cable_d);
    // Anchor bulb on the +X side
    translate([bulb_off, 0, 0]) sphere(d=bulb_d);
}

module designA() {
    petg() designA_petg();
    tpu()  designA_tpu();
}

designA();
