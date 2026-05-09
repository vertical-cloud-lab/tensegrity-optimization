// =============================================================================
// Design A — Anchor-bulb spherical node
// =============================================================================
// PETG sphere at each tensegrity vertex with through-holes; TPU cable threads
// through and is terminated in a printed-in-place TPU bulb on the far side.
// Per Edison ANALYSIS c38a2046 / followup ce84ddf8 geometry recommendations:
//   - Node OD ≈ 8.5–9.0 mm (here: 9.0 mm)
//   - Through-bore Ø ≈ 2.8–3.0 mm (here: 2.9 mm; +0.5 mm clearance over 2.4 mm cable)
//   - Bulb OD ≈ 4.0 mm (printed-in-place TPU on the far side)
// One PETG strut enters the node from -Z; one TPU cable passes through it
// horizontally along +X, terminated in a bulb on the +X side.
// =============================================================================
include <_common.scad>

node_d  = 9.0;       // PETG node sphere outer diameter
bore_d  = 2.9;       // through-hole diameter (cable_d + 0.5 mm clearance)
bulb_d  = 4.0;       // TPU bulb outer diameter at far end of cable
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
