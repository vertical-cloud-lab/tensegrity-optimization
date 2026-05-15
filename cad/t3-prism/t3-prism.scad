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
// Base (unscaled) geometry. The actual printed dimensions are
// (R, H, strut_d, cable_d, joint_d) * scale_factor.
R_base       = 25;   // radius of the circumscribing circle of each end triangle
H_base       = 70;   // distance between bottom and top triangle planes
twist        = 60;   // rotation of the top triangle relative to the bottom
strut_d_base = 6;    // strut (compression member) diameter
// Cable diameter bumped 2.4 -> 3.0 mm after the first H2D PETG print spaghetti'd
// on layer ~362 of the top-cable bridge (PR #16 review). Edison ANALYSIS
// `25c1c897` recommended 3.0–4.0 mm and Marcus's follow-up print empirically
// confirmed the threshold: at scale 1.3x (cable_d ≈ 3.12 mm), Bambu Studio's
// auto-support logic finally tagged the top cables as needing supports; at the
// original 2.4 mm it skipped them and they sagged/waved. 3.0 mm sits inside
// Edison's window while keeping the tensegrity-cable feel.
cable_d_base = 3.0;  // cable (tension member) diameter -- >= 2*nozzle for FDM
joint_d_base = 7;    // small sphere diameter at each vertex for clean joints
$fn          = 48;

// Uniform scale factor applied to ALL linear dimensions (R, H, strut/cable/joint
// diameters). Bumped 1.0 -> 1.5 per PR #35 comment 4461996817 from @sgbaird:
// "not seeing any supports... the design itself is just too small, if it were
// bigger then we don't necessarily need supports on the TPU." At scale 1.0 the
// 3.0 mm top cables sat just below Bambu Studio's auto-support detection
// threshold, so when the team imported the MM project .3mf and sliced it, the
// slicer skipped supports on the TPU cables and the bridges sagged. At scale
// 1.5 the cables become 4.5 mm Ø — well above Bambu's threshold (verified at
// scale 1.3 ↔ cable_d ≈ 3.9 mm by @achris0520) — and large enough that TPU
// can self-bridge the top-triangle spans without needing supports at all.
// Bounding box at scale 1.5: ~75 × 75 × 115 mm (still fits 4-up on the H2D's
// 350 × 320 mm plate for batch printing — see PR #35 comment 4461855403).
scale_factor = 1.5;

R       = R_base       * scale_factor;
H       = H_base       * scale_factor;
strut_d = strut_d_base * scale_factor;
cable_d = cable_d_base * scale_factor;
joint_d = joint_d_base * scale_factor;

// `part` selects which subset of members to emit. Used by render_print.sh
// to export the single-material STL ("all") and the two halves of the
// multi-material H2D variant ("struts" -> rigid filament e.g. PLA on
// extruder 1, "cables" -> tougher filament e.g. PETG / eventually TPU on
// extruder 2). The two halves are rendered in the SAME world coordinates
// so the slicer assembles them into the original geometry without any
// per-part transform. The joint vertex spheres travel with the struts so
// the rigid skeleton owns the load-bearing nodes; the cables tie into the
// joints via their own end-cap spheres (`member` adds spheres at both
// ends), giving a multi-material interlock at every vertex.
part       = "all";  // "all" | "struts" | "cables"

// Optional rigid translation applied AFTER part selection. Used by
// render_print.sh for the multi-material variant: both the struts STL
// and the cables STL are pre-translated to the H2D bed centre and lifted
// so the lowest joint sphere sits on the bed (z=0). With the same offset
// applied to both halves, BambuStudio CLI's `--orient 0 --arrange 0` keeps
// them co-located and the slicer treats them as a single assembly with
// per-object filament assignment via `--load-filament-ids`.
offset_x   = 0;
offset_y   = 0;
offset_z   = 0;

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
module t3_prism_struts() {
    union() {
        // Joint nodes (bottom + top) — bonded into the rigid strut body.
        for (i = [0:2]) {
            translate(bottom_pt(i)) sphere(d=joint_d);
            translate(top_pt(i))    sphere(d=joint_d);
        }
        // Struts: B_i -> T_i  (compression members)
        for (i = [0:2]) member(bottom_pt(i),   top_pt(i),         strut_d);
    }
}

module t3_prism_cables() {
    union() {
        // Bottom cables: B_i -> B_{i+1}
        for (i = [0:2]) member(bottom_pt(i),   bottom_pt((i+1)%3), cable_d);
        // Top cables:    T_i -> T_{i+1}
        for (i = [0:2]) member(top_pt(i),      top_pt((i+1)%3),    cable_d);
        // Saddle/vertical cables: B_{i+1} -> T_i  (so cable i and strut i
        // meet at T_i but emerge from different bottom vertices)
        for (i = [0:2]) member(bottom_pt((i+1)%3), top_pt(i),      cable_d);
    }
}

module t3_prism() {
    union() {
        t3_prism_struts();
        t3_prism_cables();
    }
}

if      (part == "struts") translate([offset_x, offset_y, offset_z]) t3_prism_struts();
else if (part == "cables") translate([offset_x, offset_y, offset_z]) t3_prism_cables();
else                       translate([offset_x, offset_y, offset_z]) t3_prism();
