// =============================================================================
// Design F — Captive TPU core inside a PETG/PLA outer shell
// =============================================================================
//
// Per-comment-4461700096 (PR #38, @sgbaird): instead of a feed-through anchor
// (Designs A0–A5 all push a TPU upset out the far side of the bore), put the
// TPU "anchor" entirely *inside* an outer PETG/PLA shell — an inner ball /
// mass surrounded by an outer ball. The cable still exits the shell on the
// +X side through a small bore, but the holding feature (the "knot") never
// leaves the shell, so there is no exposed TPU upset to wear, snag, or
// abrade across n>=20 Bruceton drops.
//
// Two extra refinements requested in the same comment:
//
// 1. "Filet the interface between the ball and stick slightly so it's a bit
//    more like a tear drop". Implemented with a hull() of the outer shell and
//    a small reference sphere set further down the strut, giving a smooth
//    teardrop blend between the cylindrical strut and the spherical shell —
//    no stress riser at the strut/shell intersection.
//
// 2. @achris0520 (byu-vcl#82, 4456499040): "Materials that do not bond
//    together when printing can be set to interlock beams on certain layers,
//    which keeps them from sliding apart". Implemented as two staggered rings
//    of radial teeth at the equator of the cavity:
//      - an inner ring of PETG/PLA teeth on the shell ID, offset to z = +tooth_dz
//      - an outer ring of TPU teeth on the core OD, offset to z = -tooth_dz
//    The teeth are radially long enough to overlap inside the print gap but
//    axially separated so they print past each other (no fused contact); on
//    pull-out the teeth catch and the captive core cannot translate along the
//    strut axis even though PETG/PLA-TPU has no chemical bond.
//
// Coordinate convention (matches `_common.scad`): PETG/PLA strut runs along
// -Z out the bottom of the shell; TPU cable exits along +X. Shell centred at
// origin. All units in mm.
//
// Print orientation (Bambu H2D IDEX, recommended): strut along build Z with
// the shell at the top — the captive core then prints in-place layer by
// layer with TPU and PETG/PLA simultaneously, the bridges over the cavity
// stay short (<= shell_id), and the +X bore is horizontal.
// =============================================================================
include <_common.scad>

// ---- Outer PETG/PLA shell ----
shell_od   = 12.0;   // outer diameter of the PETG/PLA shell (sphere)
shell_id   = 8.0;    // inner cavity diameter (= core_od + 2 * cavity_clear)

// ---- Captive TPU core (the "inner ball / mass") ----
core_od    = 7.0;    // TPU 85A captive core diameter
cavity_clear = (shell_id - core_od) / 2;  // 0.5 mm radial print-in-place gap

// ---- Cable exit bore (only the cable feeds out, not the core) ----
bore_d     = 2.8;    // exit-bore diameter (cable_d + 0.4 mm clearance)
bore_axis  = [1, 0, 0];  // cable exits +X

// ---- Teardrop strut/shell fillet ----
// hull() the shell with a small reference sphere shifted further down the
// strut to smoothly blend the cylinder into the sphere.
fillet_d   = strut_d * 1.10;     // slightly larger than strut to seed the hull
fillet_z   = -shell_od/2 - 1.5;  // start of the teardrop (below the shell)

// ---- Inter-material layer-interlock teeth (per achris0520) ----
n_teeth     = 8;       // number of teeth per ring (8 spacing = 45 deg)
tooth_h     = 1.2;     // radial protrusion (each ring extends 1.2 mm into the gap)
tooth_w     = 1.6;     // tangential width
tooth_t     = 0.8;     // axial thickness (~ 4 layers @ 0.2 mm)
tooth_dz    = 0.6;     // axial offset between PETG ring (+dz) and TPU ring (-dz)

// =============================================================================
// PETG/PLA outer shell + teardrop strut fillet + cable exit bore
// =============================================================================
module shell_solid() {
    // Teardrop = hull of the shell and a small sphere centred down the strut
    // axis. Strut is then unioned on; the hull provides the smooth blend.
    union() {
        hull() {
            sphere(d = shell_od);
            translate([0, 0, fillet_z]) sphere(d = fillet_d);
        }
        translate([0, 0, -strut_l]) cylinder(h = strut_l, d = strut_d);
    }
}

// PETG inward-pointing teeth (on the shell ID) at z = +tooth_dz.
module shell_interlock_teeth() {
    for (i = [0 : n_teeth - 1]) {
        rotate([0, 0, i * 360 / n_teeth])
            translate([core_od/2 + cavity_clear/2, 0, tooth_dz])
                // axis-aligned brick that protrudes radially inward
                translate([-tooth_h/2, -tooth_w/2, -tooth_t/2])
                    cube([tooth_h, tooth_w, tooth_t]);
    }
}

module designF_petg() {
    difference() {
        shell_solid();
        // hollow out the cavity for the captive core
        sphere(d = shell_id);
        // cable exit bore (single-sided, +X only — the core stays trapped)
        translate([0, 0, 0]) rotate([0, 90, 0])
            cylinder(h = shell_od, d = bore_d);
    }
    // Add the PETG interlock teeth back into the cavity at z = +tooth_dz
    shell_interlock_teeth();
}

// =============================================================================
// TPU captive core + outward interlock teeth + exiting cable
// =============================================================================
module core_with_teeth() {
    union() {
        sphere(d = core_od);
        for (i = [0 : n_teeth - 1]) {
            // TPU teeth offset by half a sector so they sit *between* the
            // PETG teeth in plan view, and at z = -tooth_dz so they clear
            // axially during print but interlock on pull-out.
            rotate([0, 0, (i + 0.5) * 360 / n_teeth])
                translate([core_od/2, 0, -tooth_dz])
                    translate([-tooth_h/2, -tooth_w/2, -tooth_t/2])
                        cube([tooth_h, tooth_w, tooth_t]);
        }
    }
}

module designF_tpu() {
    union() {
        core_with_teeth();
        // Cable enters/exits on +X only and terminates at the captive core
        // (the core IS the "knot" — single-ended termination, the cable
        // never feeds through the far side of the shell). The cable is
        // mechanically continuous with the core so it co-extrudes during
        // the print. A short visible stub (8 mm) is rendered for clarity;
        // in the real print the cable continues to the next node.
        cable_stub = 8.0;
        rotate([0, 90, 0])
            cylinder(h = shell_od/2 + cable_stub, d = cable_d);
    }
}

module designF() {
    petg() designF_petg();
    tpu()  designF_tpu();
}

designF();
