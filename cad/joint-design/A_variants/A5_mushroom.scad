// =============================================================================
// Design A5 — Mushroom / tee-head with a radiused undercut
// =============================================================================
// Maximum mechanical interlock per gram of TPU. The head sits on a short
// neck that necks-down to slightly less than the bore Ø, then flares back
// out to a flat-bottomed mushroom cap. The radiused undercut hooks the
// rim of the bore exit so the cable cannot pull through without tearing
// the TPU at its strongest section (the cap base, well clear of any
// stress-riser at the bore lip — Frascio 2024 fillet rule).
//
// Shape parameters:
//   - Cap OD                    = upset_od (4.8 mm) → 1.71× pull-through
//   - Cap thickness             = 1.6 mm (4 layers at 0.4 mm)
//   - Neck Ø                    = bore_d − 0.6 = 2.2 mm (sits proud of the
//                                  bore exit, hooked under the bore rim)
//   - Neck length               = 1.0 mm (axial gap between cap and node)
//   - Undercut fillet radius    = 0.4 mm (Frascio 2024 TPU de-notch radius)
// The result is a printed-in-place mushroom that requires the TPU cap to
// neck-fail before pull-through, vs. the spherical bulb which only requires
// elastic distortion.
// =============================================================================
include <_common_variants.scad>

cap_d     = upset_od;     // 4.8 mm cap (1.71× bore)
cap_th    = 1.6;          // 4 layers
neck_d    = bore_d - 0.6; // 2.2 mm — slightly proud of bore Ø for the hook
neck_l    = 1.0;          // axial gap between cap base and +X node face
fillet_r  = 0.4;          // undercut fillet radius (Frascio 2024)

module designA5_petg() { nodeA_petg(); }

module designA5_tpu() {
    nodeA_tpu_cable();
    // Build the mushroom as a rotational profile around the cable axis.
    // Profile in the (r, x) plane:
    //   - cable shaft: r=cable_d/2 from x=upset_x to x=upset_x+neck_l
    //   - cap: r=cap_d/2 from x=upset_x+neck_l to x=upset_x+neck_l+cap_th
    //   - radiused undercut where neck meets cap base
    translate([upset_x, 0, 0]) rotate([0, 90, 0])
        rotate_extrude(convexity=8)
            polygon(points=[
                [0,            0           ],
                [neck_d/2,     0           ],
                [neck_d/2,     neck_l - fillet_r],
                // Approximate the fillet with two intermediate vertices.
                [neck_d/2 + fillet_r*0.3,  neck_l - fillet_r*0.3],
                [neck_d/2 + fillet_r,      neck_l                ],
                [cap_d/2,      neck_l                ],
                [cap_d/2,      neck_l + cap_th       ],
                [0,            neck_l + cap_th       ]
            ]);
}

module designA5() {
    petg() designA5_petg();
    tpu()  designA5_tpu();
}

designA5();
