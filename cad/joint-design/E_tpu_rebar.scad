// =============================================================================
// Design E — TPU "rebar" (barbed) embedded several mm into the PETG strut tip
// =============================================================================
// TPU cable extends several mm into the PETG strut tip; PETG is printed on
// top of and around the embedded TPU, mechanical pullout limited by barbs
// (rebar in concrete). Per Edison ANALYSIS c38a2046 §4 geometry:
//   - Embed length:        10–12 mm along the strut axis (here: 11 mm)
//   - Anchor stem Ø:       2.4 mm (matches cable_d)
//   - Barbs:               2–3 at 2.0 mm pitch
//   - Barb major Ø:        3.0–3.2 mm (here: 3.1 mm)
//   - Barb step height:    ≥ 0.4 mm
//   - Flank angles:        30–45° on pull-out face; 45–60° on insertion face
//   - PETG ligament:       ≥ 1.0–1.2 mm from barb crest to outer surface
// =============================================================================
include <_common.scad>

embed_l       = 11.0;     // axial embed depth along strut axis (-Z direction from tip)
n_barbs       = 3;
barb_pitch    = 2.0;
barb_major_d  = 3.1;
barb_step     = (barb_major_d - cable_d) / 2;     // 0.35 mm radial step (close to spec)
flank_pull    = 35;       // pull-out face flank from radial (deg). Smaller = sharper barb.
flank_push    = 55;       // insertion face flank (deg). Larger = easier to insert.

// One barb as a triangular cross-section ring around the stem, centered
// on axial position z_center. Sharp pull-out face on the +Z side (toward
// the strut tip — bears load when the cable is pulled), shallow insertion
// face on the -Z side.
module one_barb(z_center) {
    pull_run = barb_step / tan(flank_pull);   // axial run of the sharp face
    push_run = barb_step / tan(flank_push);   // axial run of the shallow face
    translate([0, 0, z_center])
        rotate_extrude($fn=64)
            polygon(points = [
                [cable_d/2,        pull_run],   // stem just above crest (sharp side)
                [barb_major_d/2,   0],          // crest at radius barb_major_d/2
                [cable_d/2,       -push_run],   // stem well below crest (shallow side)
            ]);
}

module rebar_anchor() {
    // The embedded TPU rebar lives in the strut tip below z = 0.
    union() {
        // Stem
        translate([0, 0, -embed_l]) cylinder(h=embed_l, d=cable_d);
        // Barbs at evenly-spaced axial positions (deepest first)
        for (i = [0:n_barbs-1])
            one_barb(z_center = -embed_l + barb_pitch + i*barb_pitch);
    }
}

module designE_petg() {
    difference() {
        union() {
            translate([0, 0, -strut_l]) cylinder(h=strut_l, d=strut_d);
            sphere(d=strut_d);
        }
        rebar_anchor();
    }
}

module designE_tpu() {
    rebar_anchor();
    // Cable continues out the strut tip toward +Z (the natural strut axis)
    cylinder(h=cable_l, d=cable_d);
}

module designE() {
    petg() designE_petg();
    tpu()  designE_tpu();
}

designE();
