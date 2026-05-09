// =============================================================================
// Design C — TPU overmolded sleeve over knurled / grooved PETG strut tip
// =============================================================================
// TPU cable continues *over* a knurled PETG strut tip as a hoop-tensioned
// sleeve (Ye 2023 / Khatri 2024 PETG–TPU wrap style). Sleeve overlap ~8 mm,
// sleeve wall ~0.8–1.2 mm thick, knurl pitch ~1.5 mm, knurl depth ~0.4 mm.
// =============================================================================
include <_common.scad>

overlap     = 8.0;        // axial overlap of TPU sleeve onto PETG tip
sleeve_t    = 1.0;        // sleeve wall thickness (radial)
knurl_pitch = 1.5;        // axial pitch of grooves
knurl_depth = 0.4;        // groove depth (subtracted from strut OD)
n_knurls    = floor(overlap / knurl_pitch);

module knurled_strut() {
    difference() {
        // Bare PETG strut + slightly enlarged tip block (the "knurled zone")
        union() {
            translate([0, 0, -strut_l]) cylinder(h=strut_l, d=strut_d);
            sphere(d=strut_d);
        }
        // Stack of annular grooves around the +Z tip
        for (i = [0:n_knurls-1]) {
            z = -i * knurl_pitch;
            translate([0, 0, z])
                rotate_extrude($fn=64)
                    translate([strut_d/2 - knurl_depth/2, 0])
                        circle(d = knurl_depth, $fn=24);
        }
    }
}

module sleeve() {
    // Hollow TPU tube hugging the PETG tip with `sleeve_t` wall thickness.
    sleeve_id = strut_d + 0.05;          // slip fit (assume hoop-tension)
    sleeve_od = sleeve_id + 2*sleeve_t;
    translate([0, 0, -overlap])
        difference() {
            cylinder(h=overlap + strut_d/2, d=sleeve_od);
            translate([0, 0, -0.1]) cylinder(h=overlap + strut_d/2 + 0.2, d=sleeve_id);
        }
    // Hemispherical cap closing the sleeve over the strut tip
    translate([0, 0, strut_d/2]) difference() {
        sphere(d = sleeve_od);
        sphere(d = sleeve_id);
        translate([-sleeve_od, -sleeve_od, -2*sleeve_od]) cube([2*sleeve_od, 2*sleeve_od, 2*sleeve_od]);
    }
}

module designC_petg() { knurled_strut(); }

module designC_tpu() {
    sleeve();
    // TPU cable continues out the +X side from the sleeve tip
    translate([0, 0, strut_d/2 + sleeve_t/2]) rotate([0, 90, 0])
        cylinder(h=cable_l, d=cable_d);
}

module designC() {
    petg() designC_petg();
    tpu()  designC_tpu();
}

designC();
