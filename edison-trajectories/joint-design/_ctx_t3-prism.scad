// ============================================================================
// Tensegrity Optimization — T3-prism (3-strut tensegrity), single-piece.
// ============================================================================
//
// Geometry
// --------
// A T3-prism (https://en.wikipedia.org/wiki/Tensegrity) consists of:
//   * 3 isolated compression members ("struts"),
//   * 9 tension members ("cables"): 3 on the bottom triangle, 3 on the top
//     triangle, and 3 vertical/saddle cables connecting them.
//
// The two triangular end-caps are identical equilateral triangles inscribed
// in a circle of radius R. The top triangle is rotated by `twist` degrees
// relative to the bottom (per the issue: 60° -- matches the Wikipedia
// reference image cited on the issue).
//
//   B_i = (R*cos(90 + 120*i),               R*sin(90 + 120*i),               0)
//   T_i = (R*cos(90 + 120*i + twist),       R*sin(90 + 120*i + twist),       H)
//
// Connectivity (i in {0,1,2}, mod 3 implied):
//   strut i              :  B_i           --> T_i
//   bottom cable i       :  B_i           --> B_{i+1}
//   top cable i          :  T_i           --> T_{i+1}
//   vertical/saddle i    :  B_{i+1}       --> T_i
//
// Strut i and saddle i meet at T_i but originate at different bottom
// vertices, which is the defining "no two compression members touch each
// other" property of a tensegrity (the struts themselves are kept apart
// by the cables).
//
// Pure-PETG, single-piece print
// -----------------------------
// Per the issue: "Assume pure PETG for now, not multi-material." Both the
// struts and the (thinner) cables are unioned into one solid that prints in
// a single PETG extrusion. Cable diameter is intentionally well above any
// FDM minimum-feature limit so the model survives slicing without dropouts.
//
// Render:  paste into https://openscad.org/demo/  -> F6 (Render)
// Headless STL + PNG preview + Bambu slice (CI/local):
//   bash cad/t3-prism/render_print.sh
// ============================================================================

// ---- Parameters (mm / degrees) --------------------------------------------
R          = 25;   // radius of the circumscribing circle of each end triangle
H          = 70;   // distance between bottom and top triangle planes
twist      = 60;   // rotation of the top triangle relative to the bottom
strut_d    = 6;    // strut (compression member) diameter
cable_d    = 2.4;  // cable (tension member) diameter -- >= 2*nozzle for FDM
joint_d    = 7;    // small sphere diameter at each vertex for clean joints
$fn        = 48;

// ---- Vertex positions ------------------------------------------------------
function bottom_pt(i) = [R*cos(90 + 120*i),         R*sin(90 + 120*i),         0];
function top_pt(i)    = [R*cos(90 + 120*i + twist), R*sin(90 + 120*i + twist), H];

// ---- A capsule (cylinder + hemispherical end-caps) between two points -----
module member(p1, p2, d) {
    v   = p2 - p1;
    L   = norm(v);
    // Orient cylinder along v: rotate Z-axis to v's direction.
    yaw   = atan2(v[1], v[0]);
    pitch = atan2(sqrt(v[0]*v[0] + v[1]*v[1]), v[2]);
    translate(p1)
        rotate([0, 0, yaw])
            rotate([0, pitch, 0]) {
                cylinder(h=L, d=d);
                sphere(d=d);
                translate([0, 0, L]) sphere(d=d);
            }
}

// ---- T3-prism assembly -----------------------------------------------------
module t3_prism() {
    union() {
        // Joint nodes (bottom + top), keep all members fused into a single body
        for (i = [0:2]) {
            translate(bottom_pt(i)) sphere(d=joint_d);
            translate(top_pt(i))    sphere(d=joint_d);
        }
        // Struts: B_i -> T_i  (compression members)
        for (i = [0:2]) member(bottom_pt(i),   top_pt(i),         strut_d);
        // Bottom cables: B_i -> B_{i+1}
        for (i = [0:2]) member(bottom_pt(i),   bottom_pt((i+1)%3), cable_d);
        // Top cables:    T_i -> T_{i+1}
        for (i = [0:2]) member(top_pt(i),      top_pt((i+1)%3),    cable_d);
        // Saddle/vertical cables: B_{i+1} -> T_i  (so cable i and strut i
        // meet at T_i but emerge from different bottom vertices)
        for (i = [0:2]) member(bottom_pt((i+1)%3), top_pt(i),      cable_d);
    }
}

t3_prism();
