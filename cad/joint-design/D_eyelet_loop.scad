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

module designD() {
    // PETG strut + eyelet ring at the tip; the eyelet's plane is the X-Z
    // plane (i.e. the ring's hole faces +Y) so the TPU loop, which lives in
    // a perpendicular plane, threads through it cleanly.
    petg() {
        translate([0, 0, -strut_l]) cylinder(h=strut_l, d=strut_d);
        translate([0, 0, eyelet_od/2 - 0.5]) rotate([90, 0, 0]) difference() {
            cylinder(h=eyelet_t, d=eyelet_od, center=true);
            cylinder(h=eyelet_t + 1, d=eyelet_id, center=true);
        }
    }

    // TPU loop — toroidal closed loop in the Y-Z plane (perpendicular to the
    // eyelet's plane), threaded through the eyelet's hole, with the cable
    // continuing out of one side of the loop along +X.
    tpu() {
        translate([0, 0, eyelet_od/2 - 0.5])
            rotate([0, 90, 0])
                rotate_extrude($fn=72)
                    translate([loop_id/2 + loop_minor_d/2, 0])
                        circle(d=loop_minor_d);
        // Cable on the +X side of the loop
        translate([loop_id/2 + loop_minor_d, 0, eyelet_od/2 - 0.5])
            rotate([0, 90, 0])
                cylinder(h=cable_l, d=cable_d);
    }

    // Visualize the print-in-place clearance gap as a thin transparent shell
    // (only useful in OpenSCAD GUI; harmless in headless renders).
    %translate([0, 0, eyelet_od/2 - 0.5]) rotate([90, 0, 0])
        difference() {
            cylinder(h=eyelet_t + 2*clear, d=eyelet_id, center=true);
            cylinder(h=eyelet_t + 2*clear + 1, d=eyelet_id - 2*clear, center=true);
        }
}

designD();
