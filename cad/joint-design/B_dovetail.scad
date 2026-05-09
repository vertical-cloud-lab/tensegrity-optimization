// =============================================================================
// Design B — Co-printed dovetail / T-slot mechanical interlock (PRIMARY)
// =============================================================================
// PETG strut tip ends in a captive dovetail / T-slot socket; the TPU cable is
// terminated in a matching dovetail / T-head co-printed inside the socket.
// Per Edison ANALYSIS followup ce84ddf8 §4 geometry:
//   - Slot mouth width:        6.4 mm (in a ~7 mm node envelope)
//   - TPU head width (undercut): 7.4 mm (0.5 mm capture per side)
//   - Slot internal height:    3.6 mm
//   - Slot depth (along strut axis): 5.0 mm
//   - Dovetail flank angle:    25° (lower stress concentration than 90° T)
//   - Running clearance:       0.25 mm per side on non-load-bearing faces
// Strut runs along +Z; cable exits along +X. The PETG cap above the head
// (the "roof") is the print-in-place bridge that captures the TPU dovetail.
// =============================================================================
include <_common.scad>

slot_mouth   = 6.4;
slot_inner   = 7.4;
slot_height  = 3.6;
slot_depth   = 5.0;       // along strut axis (Z)
flank_deg    = 25;        // half-flank, measured from vertical wall
clear        = 0.25;      // running clearance on non-load-bearing faces
node_d       = 9.0;       // PETG socket outer diameter near tip

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
        // Dovetail pocket — wide at the bottom (captive). Add `clear` per side
        // on the non-load-bearing faces.
        translate([-(node_d/2 + 0.1), 0, -slot_depth/2 - 0.5])
            rotate([90, 0, 90])
                linear_extrude(height = node_d + 0.2 + clear)
                    dovetail_xs(slot_mouth + 2*clear,
                                slot_inner + 2*clear,
                                slot_height + 2*clear);
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
