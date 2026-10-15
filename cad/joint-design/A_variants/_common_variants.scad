// =============================================================================
// Shared parameters for the five anchor-upset shape variants of Design A
// (PETG/PLA spherical node + TPU cable + TPU printed-in-place upset on the
// far side of the bore).
//
// All variants share the same node + bore geometry from the Phase-3-refined
// `A_anchor_bulb.scad` so the only thing that changes is the shape of the
// TPU upset on the +X side of the node:
//   - Node OD            = 9.5 mm  (PETG/PLA sphere)
//   - Through-bore Ø     = 2.8 mm  (0.4 mm clearance over 2.4 mm cable)
//   - Cable Ø            = 2.4 mm  (TPU 85A)
//   - Reference upset OD = 4.8 mm  (1.71× bore — pull-through ratio target)
//
// Coordinate convention (matches `_common.scad`): PETG strut runs along +Z
// from the node, TPU cable runs along the global +X direction. The upset is
// always centred on +X. All units in mm.
//
// Each variant exports two modules:
//   designA<x>_petg() — the PETG/PLA node + strut + bore
//   designA<x>_tpu()  — the TPU cable + upset shape under study
// and a top-level designA<x>() that colours and unions them.
//
// Background / motivation: PR #38 thread asked why the original Design A
// uses a literal sphere ("bulb"). Sphere is just the laziest defensible
// upset shape; with FFF design freedom there are several plausibly better
// alternatives. These five variants visualize the candidates so they can be
// compared head-to-head before the next print.
// =============================================================================
include <../_common.scad>

// Geometry shared by every variant
node_d   = 9.5;                     // PETG/PLA node sphere outer diameter
bore_d   = 2.8;                     // through-hole diameter (cable_d + 0.4 mm)
upset_od = 4.8;                     // reference upset OD (1.71× bore)
upset_x  = node_d/2;                // far face of the bore (start of the upset)

// PETG/PLA node + axial strut + horizontal bore (identical for all variants)
module nodeA_petg() {
    difference() {
        union() {
            sphere(d=node_d);
            translate([0, 0, -strut_l]) cylinder(h=strut_l, d=strut_d);
        }
        // Horizontal cable bore along ±X clear through the node.
        translate([-node_d, 0, 0]) rotate([0, 90, 0])
            cylinder(h=2*node_d, d=bore_d);
    }
}

// TPU cable (entry on -X side, through the bore, plus a short shaft inside
// the upset). Each variant adds its own upset shape on top of this.
module nodeA_tpu_cable() {
    // Cable on the entry (-X) side
    translate([-cable_l, 0, 0]) rotate([0, 90, 0])
        cylinder(h=cable_l, d=cable_d);
    // Cable through the bore + a short stub past the bulb's near face.
    translate([-node_d/2 - 0.1, 0, 0]) rotate([0, 90, 0])
        cylinder(h=node_d + 1.5, d=cable_d);
}
