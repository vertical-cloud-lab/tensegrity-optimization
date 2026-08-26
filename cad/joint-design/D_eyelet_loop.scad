// =============================================================================
// Design D — Captive TPU loop through PETG eyelet (chain-link)
// =============================================================================
// PETG strut ends in a printed eyelet ring; TPU cable is printed in-place as
// a closed loop threaded through it (chain-link, topological constraint
// only). 0.25-0.35 mm clearance per side between the two parts is required
// to avoid fusing during print. The loop introduces 2-3 mm of slack/deadband
// before tension transmits — that is the dominant simulator-assumption
// violation flagged by Edison ANALYSIS c38a2046 / followup ce84ddf8.
// =============================================================================
include <_common.scad>

eyelet_od    = 8.0;        // PETG ring outer diameter
eyelet_id    = 4.5;        // PETG ring inner diameter (the hole)
eyelet_t     = 2.0;        // PETG ring thickness (along strut axis)
loop_minor_d = cable_d;    // TPU loop wire diameter (matches cable)
loop_id      = 3.5;        // TPU loop inside diameter (must fit through eyelet hole)
clear        = 0.30;       // print-in-place clearance between PETG and TPU

// Eyelet ring hole center, just above strut tip (module-scope constant so
// designD_petg() / designD_tpu() can both reference it from sections).
eyelet_center_z = eyelet_od/2 + 0.5;

module designD_petg() {
    // PETG strut + eyelet ring at the tip. The eyelet ring axis is along +Y
    // (the ring lies in the X-Z plane, i.e. its hole faces +Y/-Y), with the
    // ring's hole center at (0, 0, eyelet_center_z).
    translate([0, 0, -strut_l]) cylinder(h=strut_l, d=strut_d);
    translate([0, 0, eyelet_center_z]) rotate([90, 0, 0]) difference() {
        cylinder(h=eyelet_t, d=eyelet_od, center=true);
        cylinder(h=eyelet_t + 1, d=eyelet_id, center=true);
    }
}

module designD_tpu() {
    // TPU loop — closed loop with axis along the +X direction (loop lies in
    // the Y-Z plane), centered on the ring-hole axis through the eyelet
    // center, so its centerline threads through the eyelet hole exactly once
    // (chain-link topology, linking number ±1). The cable exits along +X
    // tangent to the loop on the +X side.
    translate([0, 0, eyelet_center_z]) rotate([0, 90, 0])
        rotate_extrude($fn=72)
            translate([loop_id/2 + loop_minor_d/2, 0])
                circle(d=loop_minor_d);
    // Cable on the +X side of the loop, attached to the loop's +X surface
    // at the eyelet-center height.
    translate([loop_id/2 + loop_minor_d, 0, eyelet_center_z])
        rotate([0, 90, 0])
            cylinder(h=cable_l, d=cable_d);
}

module designD() {
    petg() designD_petg();
    tpu()  designD_tpu();
    // Visualize the print-in-place clearance gap as a thin transparent shell
    // (only useful in OpenSCAD GUI; harmless in headless renders).
    %translate([0, 0, eyelet_center_z]) rotate([90, 0, 0])
        difference() {
            cylinder(h=eyelet_t + 2*clear, d=eyelet_id, center=true);
            cylinder(h=eyelet_t + 2*clear + 1, d=eyelet_id - 2*clear, center=true);
        }
}

designD();
