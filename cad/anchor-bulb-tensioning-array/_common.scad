// =============================================================================
// Shared parameters for the anchor-bulb (A1 frustum) tensioning test array.
//
// Background: PR #39 explored five anchor-upset shape variants for joint
// design A (anchor-bulb).  A1 (truncated cone / frustum / "rivet head") is
// the leading candidate for *pre-tensioning* because the flat bearing face
// loads up cleanly when the cable is pulled through the bore and seats the
// upset against the +X face of the PLA node (issue #84).
//
// Pre-tensioning by pull-through requires the PLA-to-TPU bond inside the bore
// to fail at a *finite* load — too tight and the TPU tears, too loose and the
// upset can't seat at all.  This file parameterises a single A1 specimen so
// the array script can vary the *interface treatment* between the PLA bore
// wall and the TPU cable along three independent axes:
//
//   Axis A — radial air gap        (`gap_r`,  mm)
//   Axis B — pause-and-lubricate   (`pause_z`, mm above strut top; 0 = none)
//   Axis C — sacrificial sleeve    (`sleeve_t`, mm wall in 3rd material;
//                                    0 = none, e.g. PVA / BVOH on AMS Pro)
//
// Coordinate convention for THIS array (differs from cad/joint-design/_common.scad
// which keeps the cable along +X for visual comparison):
//   +Z  = print-up direction = cable axis = pull direction
//   X-Y = build plate
// This orientation matches the recommended print orientation for the actual
// pull-test (cable axis vertical, frustum on top, anchor tab on bed) so the
// rendered geometry is exactly what comes off the printer.
//
// All dimensions are in millimetres.
// =============================================================================

$fn = 64;

// ----- Materials ------------------------------------------------------------
PLA_RGB   = [0.95, 0.55, 0.20];   // rigid strut/node (PLA per issue #45)
TPU_RGB   = [0.10, 0.55, 0.55];   // flexible cable + frustum upset (TPU 85A)
PVA_RGB   = [0.75, 0.78, 0.85];   // sacrificial release sleeve (AMS Pro 3rd nozzle)

module pla() { color(PLA_RGB) children(); }
module tpu() { color(TPU_RGB) children(); }
module pva() { color(PVA_RGB) children(); }

// ----- A1-frustum joint geometry (Phase-3 refined per PR #39) ---------------
node_d        = 9.5;     // PLA spherical node OD
bore_d_ref    = 2.8;     // reference bore Ø (0.4 mm clearance over 2.4 mm cable)
cable_d       = 2.4;     // TPU 85A cable Ø
frustum_base  = 4.8;     // upset OD at the +Z face of the node (1.71x bore)
frustum_top   = 3.6;     // 75% of base — 30deg half-angle, self-supporting in TPU85A
frustum_h     = 2.4;     // 6 layers at 0.4 mm

strut_d       = 6.0;     // PLA strut OD
strut_l       = 12.0;    // strut length below the node (anchored in pull tab)

// ----- Pull-test tab (PLA, on the build plate) ------------------------------
// Each specimen sits on a small rectangular tab whose +Z face captures the
// strut.  The tab gives the operator/clamp something to grab while the TPU
// cable above is pulled with a force gauge; the tab is large enough to bond
// to the bed via brim and small enough to fit 12 specimens on a 250x250 plate.
tab_l         = 26.0;    // X (long axis — points outward in the array layout)
tab_w         = 16.0;    // Y
tab_h         = 4.0;     // Z (~10 layers)
tab_label_h   = 0.6;     // emboss depth of the specimen ID label

// ----- Cable lengths --------------------------------------------------------
// Visible cable above the upset frustum = pull-handle (gripped by force gauge).
// Cable below the upset = bore section + slack inside the strut/tab.
cable_above   = 28.0;    // pull handle above frustum top
strut_top_z   = tab_h + strut_l;                    // top of strut (= bottom of node)
node_centre_z = strut_top_z + node_d/2;             // centre of node sphere
upset_z       = node_centre_z + node_d/2;           // base of frustum on +Z face
cable_top_z   = upset_z + frustum_h + cable_above;
cable_bot_z   = 0;                                  // anchored at bed (cable slack)

// =============================================================================
// One A1-frustum specimen, fully parameterised for interface treatment.
//
// Parameters:
//   id        text label embossed into the tab
//   gap_r     additional radial air gap (mm) added to bore_d_ref/2.
//             0    => bore Ø = 2.8 mm (Phase-3 default, ~0.2 mm radial clearance)
//             0.1  => bore Ø = 3.0 mm
//             ...
//   pause_z   if > 0, embossed fingertip well at this absolute Z height
//             on the side of the strut/node that marks the operator's
//             pause-and-lubricate plane. 0 disables.
//   sleeve_t  if > 0, sacrificial PVA tubular sleeve of this wall thickness
//             between the bore wall and the cable, full bore length.  0 disables.
// =============================================================================
// PLA-only body for one specimen (tab + strut + node, with bore + optional
// pause-and-lubricate finger well + embossed ID).
module specimen_A1_pla(id = "TA-?", gap_r = 0.2, pause_z = 0, sleeve_t = 0) {
    bore_d = cable_d + 2*max(gap_r, 0) + (sleeve_t > 0 ? 2*sleeve_t : 0);
    difference() {
        union() {
            translate([-tab_l/2, -tab_w/2, 0])
                cube([tab_l, tab_w, tab_h]);
            translate([0, 0, tab_h])
                cylinder(h=strut_l, d=strut_d);
            translate([0, 0, node_centre_z])
                sphere(d=node_d);
        }
        translate([0, 0, -1])
            cylinder(h=cable_top_z + 2, d=bore_d);
        if (pause_z > 0) {
            translate([0, node_d/2, pause_z])
                rotate([90, 0, 0])
                    cylinder(h=1.6, d=3.0);
        }
        translate([0, -tab_w/2 + 3.5, tab_h - tab_label_h + 0.01])
            linear_extrude(height = tab_label_h + 0.02)
                text(id, size = 3.2, halign = "center", valign = "baseline",
                     font = "Liberation Sans:style=Bold");
    }
}

// TPU-only body for one specimen (cable column + frustum upset + pull handle).
module specimen_A1_tpu() {
    translate([0, 0, cable_bot_z])
        cylinder(h = cable_top_z - cable_bot_z, d = cable_d);
    translate([0, 0, upset_z])
        cylinder(h = frustum_h, d1 = frustum_base, d2 = frustum_top);
}

// Optional PVA-only sacrificial sleeve in the bore.  Returns no geometry
// when sleeve_t == 0 so callers can unconditionally invoke it.
module specimen_A1_pva(sleeve_t = 0) {
    if (sleeve_t > 0) {
        translate([0, 0, tab_h])
            difference() {
                cylinder(h = upset_z - tab_h, d = cable_d + 2*sleeve_t);
                translate([0, 0, -0.1])
                    cylinder(h = upset_z - tab_h + 0.2, d = cable_d);
            }
    }
}

// Coloured single specimen.  Use this in the array layout and in individual
// per-specimen scad files.  Section-cut files should call the per-material
// modules above so that intersection() preserves per-material colours.
module specimen_A1(id = "TA-?", gap_r = 0.2, pause_z = 0, sleeve_t = 0) {
    pla() specimen_A1_pla(id, gap_r, pause_z, sleeve_t);
    tpu() specimen_A1_tpu();
    pva() specimen_A1_pva(sleeve_t);
}

// Coloured Y=0 cutaway of a single specimen, with per-material intersection so
// PLA / TPU / PVA all retain their colours in the cut view.
module specimen_A1_section_Y(id = "TA-?", gap_r = 0.2, pause_z = 0, sleeve_t = 0) {
    pla() intersection() {
        specimen_A1_pla(id, gap_r, pause_z, sleeve_t);
        translate([-50, -50, -1]) cube([100, 50, 80]);
    }
    tpu() intersection() {
        specimen_A1_tpu();
        translate([-50, -50, -1]) cube([100, 50, 80]);
    }
    pva() intersection() {
        specimen_A1_pva(sleeve_t);
        translate([-50, -50, -1]) cube([100, 50, 80]);
    }
}
