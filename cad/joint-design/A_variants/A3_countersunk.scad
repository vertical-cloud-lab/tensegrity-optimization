// =============================================================================
// Design A3 — Conical (countersunk) head — flush, self-centring
// =============================================================================
// Replaces the protruding bulb with a conical TPU head that mates a matching
// countersink cut into the +X exit of the PETG/PLA bore. The result is a
// flush far face (no protruding feature to snag on impact) and the cone
// self-centres the cable in the bore as the joint loads up.
//
// Shape parameters (90° included angle, standard ANSI flat-head):
//   - Countersink mouth Ø = upset_od (4.8 mm) at the +X face
//   - Cone bottom Ø       = bore_d   (2.8 mm) where it meets the cable
//   - Half-angle          = 45° → cone axial depth = (4.8-2.8)/2 = 1.0 mm
//   - Total head height   = 1.6 mm (1.0 mm cone + 0.6 mm flat top, just so
//                                   the head is clearly visible in the iso
//                                   render — set to 0.0 for true flush)
// Functional bearing area is the full conical wall = π·(R+r)·s ≈ 8.8 mm²
// (vs. ≈3.4 mm² projected on the reference sphere) → ~2.6× more bearing
// area at the same OD.
// =============================================================================
include <_common_variants.scad>

cs_mouth_d = upset_od;          // 4.8 mm at the +X face
cs_root_d  = bore_d;            // 2.8 mm where the cable shaft enters
cs_depth   = (cs_mouth_d - cs_root_d) / 2;   // 45° → 1.0 mm
head_top_h = 0.6;               // 0 = perfectly flush; nonzero for visibility

module designA3_petg() {
    difference() {
        nodeA_petg();
        // Cut a 45° countersink into the +X face: narrow (root) end deeper
        // inside the node, wide (mouth) end at the +X face.
        translate([upset_x - cs_depth, 0, 0]) rotate([0, 90, 0])
            cylinder(h=cs_depth + 0.01, d1=cs_root_d, d2=cs_mouth_d);
    }
}

module designA3_tpu() {
    nodeA_tpu_cable();
    // Conical head filling the countersink (root at -X, mouth at +X face),
    // plus a thin flat top extending past the +X face for visibility.
    translate([upset_x - cs_depth, 0, 0]) rotate([0, 90, 0])
        cylinder(h=cs_depth, d1=cs_root_d, d2=cs_mouth_d);
    translate([upset_x, 0, 0]) rotate([0, 90, 0])
        cylinder(h=head_top_h, d=cs_mouth_d);
}

module designA3() {
    petg() designA3_petg();
    tpu()  designA3_tpu();
}

designA3();
