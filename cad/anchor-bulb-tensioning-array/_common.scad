// =============================================================================
// Shared parameters for the anchor-bulb (A3 countersunk) tensioning test array.
//
// Background: per PR #84 review (comment 4462368734), the joint geometry under
// study is the **A3 countersunk** anchor head from PR #39 — a 90° conical TPU
// head that mates a matching countersink cut into the +Y exit of the PLA bore.
// Compared to the A1 frustum it gives a flush far face (no protruding snag
// feature on impact), self-centres the cable as the joint loads, and roughly
// 2.6x the bearing-wall area at the same OD (~8.8 mm^2 conical wall).
//
// The single interface-treatment knob is the **radial air gap** between the
// PLA bore wall and the TPU cable, swept against **joint size** (node OD;
// bore is sized to clear a 2.4 mm cable plus the gap). The second axis tests
// whether bigger nodes (and thus longer bores) tolerate a different gap than
// smaller ones — a longer cable run inside the PLA gives more contact length
// for layer-to-layer fusion to form, so the same gap may behave very
// differently on a short vs. long bore.
//
// Pause-and-lubricate and PVA-sleeve treatments from the first revision of
// this array were dropped because: (1) the H2D has IDEX (two extruders),
// not three nozzles, and the AMS Pro is just a filament store, so a
// sacrificial 3rd material is not realistic; (2) Bambu does have an
// Edinburgh-style cable on each side, but pause-and-lubricate is a manual
// workflow that doesn't survive a multi-specimen plate cleanly. Focus on
// air gap for this DOE.
//
// **Print / pull-test orientation: HORIZONTAL CABLE.**
// In the previous (vertical-cable) revision the TPU was deposited *along*
// the print Z axis and gravity pulled it straight onto the underlying TPU
// — an air gap could be left and the cable would still print fine. In the
// real horizontal-cable use case (e.g. T3 prism tendons, lander tendons)
// the TPU has to bridge the bore *horizontally*, with gravity pulling it
// down into the air gap as it extrudes — i.e. intentional spaghetti /
// stringing across the bore length. The failure mode this array is
// designed to expose is exactly that: at what gap does the TPU cable
// no longer print as a clean cylinder through the bore?
//
// Coordinate convention:
//   +Z = print-up direction.  Strut is vertical (+Z); tab lies on the bed.
//   +Y = horizontal cable axis (in the build plate).  Cable enters at -Y,
//        bore runs through the node along +Y, conical head mates a
//        countersink at the +Y face, pull handle continues along +Y.
//   X  = lateral spacing between specimens on the plate.
//
// All dimensions are in mm.
// =============================================================================

$fn = 64;

// ----- Materials ------------------------------------------------------------
PLA_RGB   = [0.95, 0.55, 0.20];   // rigid strut/node (PLA per issue #45)
TPU_RGB   = [0.10, 0.55, 0.55];   // flexible cable + conical head (TPU 85A)

module pla() { color(PLA_RGB) children(); }
module tpu() { color(TPU_RGB) children(); }

// ----- Fixed geometry (constant across the DOE) -----------------------------
cable_d       = 2.4;     // TPU 85A cable Ø
strut_d       = 6.0;     // PLA strut OD
strut_l       = 14.0;    // strut length above the tab (anchors the node)

// Countersink head: 90deg included angle (45deg half-angle), so the cone
// axial depth equals (mouth_d - root_d)/2.
head_top_h    = 0.6;     // small flat above +Y face purely for render visibility
                         // (0 = perfectly flush — recommended for real print)

// ----- Pull-test tab (PLA, on the build plate) ------------------------------
// The tab gives the operator something to clamp in a vise while the TPU
// pull-handle is gripped by a force gauge.  The tab is shifted along -Y so
// the strut sits at the +Y edge of the tab — this puts the cable entry side
// (-Y) clear of the tab footprint so a pull-side cable still lies on the bed.
tab_l_y       = 26.0;    // Y depth (along cable axis)
tab_w_x       = 16.0;    // X width
tab_h         = 4.0;     // Z height (~10 layers)
tab_label_h   = 0.6;     // emboss depth of the specimen ID label
strut_y       = tab_l_y / 2 - strut_d;   // strut origin Y (offset toward +Y side)

// ----- Cable layout along Y -------------------------------------------------
// Cable enters at -Y (entry tail), passes through the bore (length = node_d),
// emerges on the +Y face into the countersink, and continues as the pull handle.
cable_entry_l = 18.0;    // cable tail on -Y side (extends past the tab)
cable_pull_l  = 26.0;    // pull handle past the +Y face of the node

// =============================================================================
// One A3-countersunk specimen, parameterised on (node_d, gap_r).
//
// Parameters:
//   id        text label embossed onto the top face of the tab
//   node_d    PLA node OD (sphere diameter).  Bore depth = node_d.
//   gap_r     additional radial air gap (mm) added to cable_d/2.
//             bore_d = cable_d + 2*gap_r.  Sweep gap_r in 0.1..0.6 mm.
// =============================================================================
module specimen_A3_pla(id = "TS-?", node_d = 9.5, gap_r = 0.2) {
    bore_d        = cable_d + 2*max(gap_r, 0);
    cs_mouth_d    = bore_d + 2.0;                  // 1.0 mm wider than bore on each side
    cs_root_d     = bore_d;                        // cone root = bore Ø
    cs_depth      = (cs_mouth_d - cs_root_d) / 2;  // 45deg half-angle => 1.0 mm
    node_centre_z = tab_h + strut_l + node_d/2;

    difference() {
        union() {
            // tab: shifted in -Y so strut sits near +Y edge (cable entry tail
            // is free of the tab footprint).
            translate([-tab_w_x/2, strut_y - tab_l_y, 0])
                cube([tab_w_x, tab_l_y, tab_h]);
            // strut along +Z
            translate([0, strut_y, tab_h])
                cylinder(h = strut_l, d = strut_d);
            // node sphere
            translate([0, strut_y, node_centre_z])
                sphere(d = node_d);
        }
        // horizontal through-bore along +Y (length spans the whole node)
        translate([0, strut_y - node_d, node_centre_z])
            rotate([-90, 0, 0])
                cylinder(h = 2*node_d, d = bore_d);
        // 90deg countersink cut into the +Y face of the node
        translate([0, strut_y + node_d/2 - cs_depth, node_centre_z])
            rotate([-90, 0, 0])
                cylinder(h = cs_depth + 0.02, d1 = cs_root_d, d2 = cs_mouth_d);
        // embossed specimen ID on top of the tab
        translate([0, strut_y - tab_l_y + 3.5, tab_h - tab_label_h + 0.01])
            linear_extrude(height = tab_label_h + 0.02)
                text(id, size = 3.0, halign = "center", valign = "baseline",
                     font = "Liberation Sans:style=Bold");
    }
}

module specimen_A3_tpu(node_d = 9.5, gap_r = 0.2) {
    bore_d        = cable_d + 2*max(gap_r, 0);
    cs_mouth_d    = bore_d + 2.0;
    cs_root_d     = bore_d;
    cs_depth      = (cs_mouth_d - cs_root_d) / 2;
    node_centre_z = tab_h + strut_l + node_d/2;

    // entry tail at -Y, through the bore, plus a stub past the +Y face
    translate([0, strut_y - node_d/2 - cable_entry_l, node_centre_z])
        rotate([-90, 0, 0])
            cylinder(h = cable_entry_l + node_d - cs_depth, d = cable_d);
    // conical head filling the countersink
    translate([0, strut_y + node_d/2 - cs_depth, node_centre_z])
        rotate([-90, 0, 0])
            cylinder(h = cs_depth, d1 = cs_root_d, d2 = cs_mouth_d);
    // small flat top above the +Y face for visibility (set head_top_h=0 for flush)
    translate([0, strut_y + node_d/2, node_centre_z])
        rotate([-90, 0, 0])
            cylinder(h = head_top_h, d = cs_mouth_d);
    // pull handle continuing on +Y
    translate([0, strut_y + node_d/2 + head_top_h, node_centre_z])
        rotate([-90, 0, 0])
            cylinder(h = cable_pull_l, d = cable_d);
}

// Coloured single specimen (use this in the array layout and individual
// per-specimen files).
module specimen_A3(id = "TS-?", node_d = 9.5, gap_r = 0.2) {
    pla() specimen_A3_pla(id = id, node_d = node_d, gap_r = gap_r);
    tpu() specimen_A3_tpu(node_d = node_d, gap_r = gap_r);
}

// X=0 cutaway (cable axis stays in view, front X half removed) so the bore /
// countersink / cable interface is visible. Per-material intersection keeps
// colours intact in the cut view.
module specimen_A3_section_X(id = "TS-?", node_d = 9.5, gap_r = 0.2) {
    pla() intersection() {
        specimen_A3_pla(id = id, node_d = node_d, gap_r = gap_r);
        translate([-50, -50, -1]) cube([50, 100, 80]);
    }
    tpu() intersection() {
        specimen_A3_tpu(node_d = node_d, gap_r = gap_r);
        translate([-50, -50, -1]) cube([50, 100, 80]);
    }
}
