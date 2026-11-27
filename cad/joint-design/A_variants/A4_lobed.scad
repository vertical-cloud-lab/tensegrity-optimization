// =============================================================================
// Design A4 — Star / lobed / knurled head (rotational keying)
// =============================================================================
// Replaces the spherical bulb with a 6-lobed star head so the upset can't
// rotate relative to the bore under repeated drops. This is what the lander
// demo (#16) Bruceton n≥20 reuse case actually wants — every drop
// reseats the joint at a slightly different angle, and a smooth bulb just
// spins; a lobed head torsionally keys against the bore exit.
//
// Shape parameters:
//   - Bounding OD            = upset_od (4.8 mm) → preserves 1.71× ratio
//   - Lobe count             = 6
//   - Lobe Ø (each)          = 1.6 mm → 4-perimeter feature in TPU at 0.4 mm
//   - Lobe centre radius     = 1.4 mm from cable axis
//   - Head thickness         = 1.6 mm along +X
// The PETG/PLA bore is left round (Ø 2.8 mm); the lobes engage the +X face
// of the node when the cable pulls in -X. Optionally one could match the
// bore mouth with a 6-lobe profile to fully constrain rotation; here we
// leave the bore round so the joint stays drop-in compatible with the
// reference geometry and only change the head.
// =============================================================================
include <_common_variants.scad>

bound_d   = upset_od;           // 4.8 mm bounding circle
lobes     = 6;
lobe_d    = 1.6;
lobe_r    = (bound_d - lobe_d) / 2;   // 1.6 mm centre offset → 4.8 mm bound
head_th   = 1.6;                // 4 layers at 0.4 mm
head_x    = upset_x - 0.3;      // a touch embedded in the +X face

module star_head(thickness, lobes, lobe_d, lobe_r, hub_d) {
    // 2D star + central hub, then linear-extruded along +Z.
    linear_extrude(height=thickness, convexity=8) {
        union() {
            circle(d=hub_d);
            for (i = [0:lobes-1]) {
                rotate([0, 0, i * 360 / lobes])
                    translate([lobe_r, 0, 0])
                        circle(d=lobe_d);
            }
        }
    }
}

module designA4_petg() { nodeA_petg(); }

module designA4_tpu() {
    nodeA_tpu_cable();
    // Lobed disc on the cable axis (+X). Hub Ø ≥ bore so the head fully
    // covers the bore exit; lobes radiate outward in the Y-Z plane.
    translate([head_x, 0, 0]) rotate([0, 90, 0])
        star_head(thickness=head_th, lobes=lobes, lobe_d=lobe_d,
                  lobe_r=lobe_r, hub_d=bore_d + 0.6);
}

module designA4() {
    petg() designA4_petg();
    tpu()  designA4_tpu();
}

designA4();
