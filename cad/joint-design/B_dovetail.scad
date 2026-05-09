// =============================================================================
// Design B — Co-printed dovetail / T-slot mechanical interlock (PRIMARY)
// =============================================================================
// PETG strut tip ends in a captive dovetail / T-slot socket; the TPU cable is
// terminated in a matching dovetail / T-head co-printed inside the socket.
// Per Edison Phase-3 ANALYSIS 19e0c868 §2 (CAD review) geometry, which
// supersedes the earlier ce84ddf8 §4 numbers:
//   - Node OD:                 12.0 mm (was 9.0; needed for >=2 perimeters
//                                       on the lateral PETG cheeks)
//   - Slot mouth width:         5.4 mm (allows solid bridging over the gap)
//   - TPU head width (undercut):7.06 mm (≈0.83 mm undercut per side)
//   - Slot internal height:     4.0 mm
//   - Slot depth (along strut): 6.0 mm (>=4-6 mm engagement plateau, Wang 2026)
//   - Dovetail flank angle:    22.5° (Wang 2026 shear-strength optimum for
//                                     bi-material FDM rigid-flexible interlock)
//   - Lateral (Y) clearance:    0.20 mm per face (load-bearing fit, Ermolai 2024)
//   - Roof (Z) clearance:       0.30 mm (bridge sag tolerance, Ermolai 2024)
//   - +X exit fillet:           0.5 mm (de-notches TPU cable redirection,
//                                       Frascio 2024)
// Strut runs along +Z; cable exits along +X. The PETG cap above the head
// (the "roof") is the print-in-place bridge that captures the TPU dovetail.
// =============================================================================
include <_common.scad>

slot_mouth   = 5.4;
slot_inner   = 7.06;
slot_height  = 4.0;
slot_depth   = 6.0;       // along strut axis (Z)
flank_deg    = 22.5;      // half-flank, measured from vertical wall
clear_lat    = 0.20;      // lateral (Y, load-bearing) running clearance per face
clear_roof   = 0.30;      // roof (Z) clearance per face — bridge-sag tolerance
mouth_fillet = 0.5;       // PETG slot-mouth +X exit fillet (TPU de-notch)
node_d       = 12.0;      // PETG socket outer diameter near tip

// Dovetail / T-head extruded along +X (X = depth into slot).
// The cross-section in (Y,Z) is wider at the bottom (slot_inner) than the
// top (slot_mouth) — that is the "captive" undercut.
module dovetail_xs(width_top, width_bot, height) {
    polygon(points = [
        [-width_top/2,  height/2],
        [ width_top/2,  height/2],
        [ width_bot/2, -height/2],
        [-width_bot/2, -height/2],
    ]);
}

module designB_petg() {
    difference() {
        union() {
            translate([0, 0, -slot_depth - 0.5])
                cylinder(h=slot_depth + 0.5, d=node_d);
            translate([0, 0, -strut_l])
                cylinder(h=strut_l - slot_depth, d=strut_d);
        }
        // Dovetail pocket — wide at the bottom (captive). Differential clearance:
        // tight on the lateral (Y) load-bearing flanks (`clear_lat`), looser on
        // the roof (Z) for bridge-sag tolerance (`clear_roof`).
        translate([-(node_d/2 + 0.1), 0, -slot_depth/2 - 0.5])
            rotate([90, 0, 90])
                linear_extrude(height = node_d + 0.2 + clear_lat)
                    dovetail_xs(slot_mouth + 2*clear_lat,
                                slot_inner + 2*clear_lat,
                                slot_height + 2*clear_roof);
    }
}

module designB_tpu() {
    // Head: dovetail cross-section extruded along the slot depth.
    translate([-node_d/2, 0, -slot_depth/2 - 0.5])
        rotate([90, 0, 90])
            linear_extrude(height = slot_depth)
                dovetail_xs(slot_mouth, slot_inner, slot_height);
    // Cable exits the slot mouth on the +X side
    translate([node_d/2 - 0.5, 0, 0]) rotate([0, 90, 0])
        cylinder(h=cable_l, d=cable_d);
}

module designB() {
    petg() designB_petg();
    tpu()  designB_tpu();
}

designB();
