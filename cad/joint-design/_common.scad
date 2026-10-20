// Shared parameters for the five candidate PETG-strut + TPU-cable joint
// designs explored in `edison-trajectories/joint-design/`.
//
// Coordinate convention (per design): the PETG strut runs along +Z and the
// TPU cable runs along the global +X direction (so the joint plane is the
// X-Z plane). All units in mm. PETG is rendered orange, TPU dark cyan.
strut_d = 6.0;     // PETG strut diameter (matches t3-prism.scad)
cable_d = 2.4;     // TPU cable diameter (matches t3-prism.scad)
strut_l = 18.0;    // visible strut length to render
cable_l = 30.0;    // visible cable length on each side
$fn = 64;

PETG_RGB = [0.95, 0.55, 0.20];
TPU_RGB  = [0.10, 0.55, 0.55];

module petg() { color(PETG_RGB) children(); }
module tpu()  { color(TPU_RGB)  children(); }

// Strut as a vertical capsule along +Z, tip at z = 0, body extending to -strut_l.
module strut_body(length = strut_l, d = strut_d) {
    translate([0, 0, -length]) cylinder(h=length, d=d);
    sphere(d=d);
}

// Straight TPU cable along +X.
module cable_segment(length = cable_l, d = cable_d, x0 = 0) {
    translate([x0, 0, 0])
        rotate([0, 90, 0])
            cylinder(h=length, d=d);
}
