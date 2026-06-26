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
part       = "all";  // "all" | "struts" | "cables" | "scaffold" | "struts_scaffold" | "all_scaffold"

// ---- Modeled-in PLA scaffold for the TPU cables ---------------------------
// The Bambu CLI's tree(auto) supports reliably scaffold horizontal overhangs
// (lower-triangle and the three top-triangle bridges at the new scale 1.5x)
// but they leave the *near-vertical* members untouched: each strut tilts only
// ~22 deg from vertical, the saddle cables are similar, and Bambu's overhang
// detector measures angle from vertical, so anything below the threshold is
// skipped — even when the slicer is told `support_critical_regions_only=0`
// and `support_threshold_angle=10`. The result on the production
// PLA-struts/TPU-cables print is exactly what @sgbaird-alt's photos show:
// supports under the bottom triangle, but the TPU saddle and top cables
// (and even the strut shafts) wave around mid-print because nothing is
// holding them upright.
//
// Per PR #35 comment 4464251671 ("We want to put PLA support points at 7
// points along the length of the TPU to keep it upright"), we now MODEL the
// scaffolding directly into the geometry as PLA pillars rising from the
// build plate up to evenly-spaced touch-points on each TPU cable. Because
// they are part of the model the slicer cannot omit them, and because they
// are routed to the PLA extruder in the multi-material variant they peel
// off the TPU cleanly post-print (the PLA-TPU bond is weak in shear, ~6.5
// MPa butt; see edison-trajectories/strut-material-selection-5bb5e5d3-*).
//
// `n_scaffolds` interior touch-points per cable, evenly spaced at
// fractions k/(n_scaffolds+1) along the cable's length. Pillars are
// truncated cones (wider at the bed for stability, narrower at the
// touch-point so they snap off without scarring the TPU).
n_scaffolds          = 7;            // touch-points along each TPU cable
scaffold_d_top_base  = 1.4;          // pillar Ø at the cable contact
scaffold_d_bot_base  = 3.0;          // pillar Ø at the bed (taper for stability)
scaffold_min_h_base  = 4.0;          // skip pillars shorter than this (mm, post-scale)

scaffold_d_top = scaffold_d_top_base * scale_factor;
scaffold_d_bot = scaffold_d_bot_base * scale_factor;
scaffold_min_h = scaffold_min_h_base * scale_factor;

// ---- Captive TPU core inside a PLA outer shell (Design F) -----------------
// Per PR #35 comment 4511036510 / PR #39 comment 4461700096
// (https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/39#issuecomment-4461700096):
// instead of half-burying the TPU cable end in a solid PLA joint sphere
// (the previous design — @ctrhjk's photos in PR #35 showed the cable
// inserts into only kinda half of the joint ball, giving unstable
// fixation and a fully encased TPU that was nearly impossible to remove),
// put a captive TPU "knot" entirely INSIDE a hollow PLA outer shell at
// every joint vertex. The cable still emerges from the shell along its
// outward direction, but it does so through a small PLA bore that is
// strictly narrower than the captive core; the TPU mass therefore cannot
// back out under tension regardless of PLA-TPU bond chemistry. PLA-TPU
// butt-bond is only ~6.5 MPa in shear (Lopes 2018; see
// edison-trajectories/strut-material-selection-5bb5e5d3*), so the shell
// and core stay mechanically separate even in their print-in-place state.
//
// Geometry (each joint vertex carries one strut + three cables; both
// bottom-B_i and top-T_i vertices share the same fan-of-three cable
// pattern, just routed to different remote vertices — see
// `vertex_cable_dirs()` below):
//   * `captive_bore_d`  : per-cable exit-bore diameter through the shell
//                         wall (= cable_d + bore_clear). Cable passes
//                         through with print clearance.
//   * `captive_core_od` : TPU captive-core sphere diameter; chosen so
//                         core_od > bore_d by at least `bore_trap` mm
//                         (the "trap" — the core cannot fit back out
//                         any single bore).
//   * `captive_shell_id`: shell inner-cavity diameter (= core_od +
//                         2*core_clear; gives a print-in-place radial
//                         gap so the core remains free to wiggle).
//   * `captive_shell_od`: outer PLA shell diameter (= shell_id + 2*wall).
//   * `captive_teardrop`: hull-blend offset that smoothly fillets the
//                         shell sphere into the strut cylinder, removing
//                         the sharp re-entrant corner at the shell/strut
//                         intersection (avoids the stress-concentration
//                         and over-extrusion artefact reported in
//                         @ctrhjk's first PETG+TPU print).
// PR #35 comment 4513722886 (@sgbaird): "make sure each TPU vertex has a
// full spherical PLA shell around it (no gaps except to allow TPU to pass
// through) and is in contact with the internal TPU vertex so the two
// material types bond together." Print-in-place clearances dropped to
// zero so the TPU core is bonded to the PLA inner shell wall and the
// cable fills its exit bore exactly (no annular air ring).
// PR #35 comment 4514072758 (@sgbaird): "the teardrop shape was fine.
// Stick with the teardrop style to reduce stresses." Restored the
// teardrop hull blend toward the strut so the shell/strut intersection
// is filleted instead of a sharp re-entrant corner. Also fixed the
// cable bore to cut only the outward half of the shell wall (the bore
// previously punched through both sides of the sphere, which created
// the mystery "holes on a lot of the vertices" he reported in
// 4514072758 — every cable was making TWO holes, not one).
use_captive_core   = true;            // set false to revert to solid joint spheres
captive_bore_clear = 0.0;             // mm, single-sided clearance around the cable (bonded)
captive_bore_trap  = 1.5;             // mm, MIN (core_od - bore_d) / 2 so the core can't escape
captive_core_clear = 0.0;             // mm, radial gap shell-ID -> core-OD (0 = bonded)
captive_wall_base  = 1.6;             // mm, PLA shell wall thickness (un-scaled)
captive_teardrop_z = 1.5;             // mm, axial offset of the teardrop reference sphere
captive_wall       = captive_wall_base * scale_factor;
captive_bore_d     = cable_d + 2 * captive_bore_clear;
captive_core_od    = max(captive_bore_d + 2 * captive_bore_trap, joint_d);
captive_shell_id   = captive_core_od + 2 * captive_core_clear;
captive_shell_od   = max(captive_shell_id + 2 * captive_wall, joint_d);
captive_teardrop_d = strut_d * 1.10;  // seed sphere for the teardrop blend

// ---- Accelerometer mount (Dytran 3133A4 tri-axis, 6 x 6 x 5.94 mm) --------
// PR #35 comment 4794790065 (@sgbaird): "extrude some extra material in a
// block on top of the top vertices and cut out a place to secure the 3-axis
// accelerometer ... a cable needs to feed out horizontally (hence three
// 'walls' and one opening) and ... because there will be a bit of adhesive
// there should be a bit of clearance so it can fit inside. A rounded shape on
// top should be preserved so that it's a bit like an igloo with the
// accelerometer sliding in, such that there is less friction between the
// acrylic plate and the tensegrity structure."
//
// We add one rounded ("igloo") mount on top of each of the three top vertices
// (so the team can secure the accelerometer to whichever vertex is convenient
// and every top contact point against the acrylic drop-test plate is rounded
// to reduce friction). Each mount is a small PLA block fused onto the top
// joint shell, with a rectangular pocket sized to the accelerometer plus an
// adhesive/fit clearance. The pocket is closed on the back and both sides
// (three walls) and on the bottom (floor), open on the outward-facing front
// (so the cable feeds out horizontally and the accelerometer slides in from
// the side), and capped by a rounded crown (the "igloo" top).
//
// The accelerometer is a PHYSICAL part — its dimensions are absolute
// millimetres (Dytran 3133A4, measured 6 x 6 x 5.94 mm L x W x H, PR #74
// comment 4792400480) and are NOT multiplied by `scale_factor`.
add_accel_mount = true;          // set false to omit the accelerometer mounts
accel_l     = 6.0;               // accelerometer length (X: slide-in / cable-exit axis)
accel_w     = 6.0;               // accelerometer width  (Y)
accel_h     = 5.94;              // accelerometer height (Z)
accel_clear = 0.4;               // per-side LATERAL (XY) clearance for the slide-in fit
accel_clear_top = 0.2;           // Z clearance above the accelerometer (below the crown)
accel_clear_bot = 0.2;           // Z clearance below the accelerometer (adhesive-bead recess)
accel_wall  = 2.0;               // PLA wall thickness around the pocket
accel_floor = 1.5;               // PLA floor thickness between the joint apex and the pocket floor
accel_dome  = 3.0;               // rounded PLA crown thickness above the pocket
accel_sink  = 2.0;               // depth the mount walls sink past the joint apex (for bonding)

// Pocket inner dimensions (the open +X face is the cable exit / slide-in).
// The Z depth carries an independent top + bottom clearance so the
// accelerometer seats flat on the (solid, flat) pocket floor with a thin
// adhesive recess below it and a small gap above it (PR #35 comment
// 4805516634: "change the tolerances to 0.2 mm top and 0.2 mm bottom").
function accel_pocket_x() = accel_l + 2 * accel_clear;
function accel_pocket_y() = accel_w + 2 * accel_clear;
function accel_pocket_z() = accel_h + accel_clear_top + accel_clear_bot;
// Outward radius of the joint node the mount fuses onto (captive shell in the
// default mode, solid joint sphere in legacy mode).
function joint_outer_r() = use_captive_core ? captive_shell_od / 2 : joint_d / 2;
// How far the rounded crown rises above the top-joint node equator. Used to
// keep the cables STL bounding box matched to the (now taller) struts STL —
// see cables_z_anchor().
function accel_rise() = accel_floor + accel_pocket_z() + accel_dome;

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

// At each bottom vertex B_i, three TPU cables radiate out (the two bottom-
// triangle cables and the saddle to T_{i-1}). At each top vertex T_i, three
// TPU cables radiate out (the two top-triangle cables and the saddle from
// B_{i+1}). The strut runs along the strut axis from B_i to T_i (or T_i to
// B_i). These helper functions return the unit-direction-from-vertex of
// each connected member, which the captive-core joint uses to (a) hull-
// blend the shell into the strut (`vertex_strut_dir`) and (b) cut a cable
// exit bore through the shell wall along each cable axis
// (`vertex_cable_dirs`). All three "from-vertex" cable directions point
// outward (away from V) so the bore cylinders never accidentally collapse.
function _unit(v) = v / norm(v);
function vertex_strut_dir_b(i) = _unit(top_pt(i)    - bottom_pt(i));
function vertex_strut_dir_t(i) = _unit(bottom_pt(i) - top_pt(i));
function vertex_cable_dirs_b(i) = [
    _unit(bottom_pt((i+1)%3)   - bottom_pt(i)),      // bottom cable B_i -> B_{i+1}
    _unit(bottom_pt((i+2)%3)   - bottom_pt(i)),      // bottom cable B_i <- B_{i-1}
    _unit(top_pt((i+2)%3)      - bottom_pt(i)),      // saddle B_i -> T_{i-1}
];
function vertex_cable_dirs_t(i) = [
    _unit(top_pt((i+1)%3)      - top_pt(i)),         // top cable T_i -> T_{i+1}
    _unit(top_pt((i+2)%3)      - top_pt(i)),         // top cable T_i <- T_{i-1}
    _unit(bottom_pt((i+1)%3)   - top_pt(i)),         // saddle T_i <- B_{i+1}
];

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

// Cylindrical bore along an arbitrary direction `dir` (does NOT need to be
// unit-length). The bore extends from a small inset on the -dir side
// (just past the vertex centre, so it always cuts cleanly through the
// inner cavity wall) out to +len along +dir. It is OUTWARD-ONLY by
// design: the previous symmetric (centred) bore punched holes through
// BOTH sides of the shell, which is what created the mystery "holes on
// a lot of the vertices" reported in PR #35 comment 4514072758.
module bore_along(dir, d, len) {
    yaw   = atan2(dir[1], dir[0]);
    pitch = atan2(sqrt(dir[0]*dir[0] + dir[1]*dir[1]), dir[2]);
    rotate([0, 0, yaw])
        rotate([0, pitch, 0])
            translate([0, 0, -0.5])
                cylinder(h=len + 0.5, d=d);
}

// ---- Captive-core joint: PLA outer shell at vertex V ----------------------
// Hollow PLA sphere with a teardrop-blend toward the strut axis (the
// strut emerges from the teardrop bump, not through a punched hole, so
// the shell/strut intersection is smoothly filleted and there is no
// stress-concentration corner). The shell is hollowed by the inner
// cavity (where the TPU captive core lives) and pierced by one
// cylindrical exit bore per outgoing cable. With zero clearances the
// TPU core touches the inner shell wall and the TPU cable fills its
// bore exactly — the only "openings" in the shell are the three cable
// bores per vertex (PR #35 comment 4513722886 / 4514072758).
module joint_shell(V, strut_dir, cable_dirs) {
    translate(V) {
        difference() {
            // Outer shell + teardrop blend along the strut axis (the
            // bump where the strut cylinder will emerge — kept per
            // PR #35 comment 4514072758: "the teardrop shape was fine.
            // Stick with the teardrop style to reduce stresses").
            hull() {
                sphere(d=captive_shell_od);
                translate(strut_dir * (captive_shell_od/2 + captive_teardrop_z))
                    sphere(d=captive_teardrop_d);
            }
            // Inner cavity (the captive TPU core sits inside this and,
            // with captive_core_clear=0, touches the inner shell wall).
            sphere(d=captive_shell_id);
            // One outward-only exit bore per cable (see bore_along()).
            // With captive_bore_clear=0 the bore is exactly cable_d so
            // the TPU passes through the shell with no visible ring gap.
            for (d = cable_dirs)
                bore_along(d, captive_bore_d, captive_shell_od);
        }
    }
}

// ---- Captive-core joint: TPU core at vertex V -----------------------------
// Solid TPU sphere of diameter `captive_core_od`. Lives inside the cavity
// of the PLA shell, with a `captive_core_clear` print-in-place radial gap;
// merges seamlessly with the cable end-cap spheres so cables emerge through
// the shell bores as a continuous TPU thread. Because core_od > bore_d by
// at least 2*captive_bore_trap, the core cannot back out any single bore.
module joint_core(V) {
    translate(V) sphere(d=captive_core_od);
}

// ---- Accelerometer mount: rounded PLA "igloo" with a slide-in pocket -------
// Built in a local frame where +X is the outward (cable-exit / slide-in)
// direction, +Z is up (toward the acrylic plate). The pocket floor sits at
// local z=0; the solid body extends down to z=-(accel_floor+accel_sink) so
// its walls sink past the joint apex and fuse with the joint node, while the
// flat pocket floor stays a full accel_floor above the apex (so nothing from
// the rounded joint underneath pokes up through the floor — PR #35 comment
// 4805516634). The rounded crown rises to z = pocket_z + accel_dome and the
// pocket is open on +X only.
module accel_mount_local() {
    px  = accel_pocket_x();
    py  = accel_pocket_y();
    pz  = accel_pocket_z();
    bx0 = -accel_wall;                  // back wall outer face
    bx1 = px;                           // front face (flush with the open pocket mouth)
    byh = py / 2 + accel_wall;          // body half-width (side walls)
    bz0 = -(accel_floor + accel_sink);  // body underside (sinks accel_sink past the joint apex)
    bz1 = pz;                           // top of the straight walls (crown springs from here)
    cx  = (bx0 + bx1) / 2;
    rcrown = min(bx1 - bx0, 2 * byh) / 2;
    difference() {
        // Solid igloo: straight walled body + a rounded crown hulled from the
        // body's top rim up to a crowning sphere (rounded top, less friction).
        union() {
            translate([cx, 0, (bz0 + bz1) / 2])
                cube([bx1 - bx0, 2 * byh, bz1 - bz0], center=true);
            hull() {
                translate([cx, 0, bz1 - 0.5])
                    cube([bx1 - bx0, 2 * byh, 1], center=true);
                translate([cx, 0, bz1 + accel_dome - rcrown])
                    sphere(r=rcrown);
            }
        }
        // Pocket, OPEN on +X (cable exit / slide-in). The cut runs past the
        // front face so the mouth is fully open; the back, both sides, the
        // floor and the crown stay solid (three walls + floor + rounded top).
        // The cut bottom is at local z=0, so the floor is a full, flat
        // accel_floor-thick solid PLA slab regardless of the joint geometry
        // sunk in below it.
        translate([0, -py / 2, 0])
            cube([px + byh + 5, py, pz]);
    }
}

// Place an accelerometer mount on top of the joint at vertex V, with its open
// face (and the exiting cable) pointing outward along heading `ang` (degrees,
// measured in the XY plane). The pocket floor sits accel_floor above the
// joint apex (V[2]+joint_outer_r()) so the rounded joint can never poke up
// into the pocket, while the body walls still sink accel_sink past the apex
// so the PLA fuses solidly. Works for any design because the seat height is
// derived from joint_outer_r() (PR #35 comment 4805516634).
//
// A "skirt" hulls the body's underside footprint down onto the rounded joint
// surface so PLA runs continuously from the joint up to the underside of the
// igloo, filling the outer void and removing the thin overhanging lip that
// would otherwise be an unsupported stress riser (PR #35 comment 4813200802).
// `cable_dirs` are the outgoing cable directions at this vertex; the skirt
// re-applies the joint shell's cavity and cable-bore subtractions so the
// captive TPU core and the cable exits stay open.
module accel_mount(V, ang, cable_dirs) {
    z0  = V[2] + joint_outer_r() + accel_floor;
    cx  = (-accel_wall + accel_pocket_x()) / 2;
    bz0 = -(accel_floor + accel_sink);         // body underside (matches accel_mount_local)
    blen = accel_pocket_x() + accel_wall;      // body length  (bx1 - bx0)
    byw  = accel_pocket_y() + 2 * accel_wall;  // body width   (2 * byh)
    translate([V[0], V[1], z0])
        rotate([0, 0, ang])
            translate([-cx, 0, 0])
                accel_mount_local();
    // Skirt: convex-hull the body's underside footprint down to the joint
    // sphere, then re-cut the joint cavity + cable bores so the captive TPU
    // core and cable exits remain (mirrors joint_shell()).
    difference() {
        hull() {
            translate([V[0], V[1], z0])
                rotate([0, 0, ang])
                    translate([-cx, 0, 0])
                        translate([cx, 0, bz0 + 0.5])
                            cube([blen, byw, 1], center=true);
            translate(V) sphere(d = 2 * joint_outer_r());
        }
        if (use_captive_core) {
            translate(V) sphere(d = captive_shell_id);
            // Re-cut the cable bores. The skirt thickens the shell wall in the
            // fillet region, so the bore must run further than joint_shell's
            // (captive_shell_od) to always punch through and keep each cable
            // exit — and the captive-core cavity — open.
            translate(V)
                for (d = cable_dirs)
                    bore_along(d, captive_bore_d,
                               captive_shell_od + accel_pocket_x()
                                   + accel_pocket_y() + 2 * accel_wall);
        }
    }
}

// ---- TPU z-anchor (cable-STL bounding-box parity) -------------------------
// When the cables STL is rendered separately from the struts STL and both
// are imported into Bambu Studio, the slicer's "place on bed" routine
// lifts each part individually so its own lowest world-Z point sits on
// the bed. Because the strut STL's lowest point is the bottom-vertex
// shell underside at z=-captive_shell_od/2 while the cables STL's lowest
// point is the bottom-cable cylinder underside at z=-cable_d/2, the two
// parts ended up shifted by (shell_od - cable_d)/2 mm in z and the
// cables visually dropped relative to the joints — exactly the
// "horizontal cables too low at top and bottom" issue reported in PR #35
// (immediately above PR #35 comment 4511036510). The fix is to give the
// cables STL the same world-Z extents as the struts STL by emitting a
// pair of zero-XY-area axial spikes at the geometric centre that span
// the strut STL's z-range. The spikes add a negligible amount of TPU
// (< 0.01 mm^2 cross-section * span) but pin the cables STL's bounding
// box so Bambu's auto-bed-placement applies the SAME world-Z offset to
// both parts, keeping cables and joint shells aligned to their original
// SCAD coordinates.
module cables_z_anchor() {
    // The extreme bottom point of the strut STL is the bottom-vertex
    // joint shell's underside at z = -captive_shell_od/2; the extreme
    // top point is the top-vertex shell at z = H + captive_shell_od/2,
    // plus the accelerometer-mount crown (when enabled), which sits on
    // top of the top-vertex shells and makes the struts STL taller.
    z_lo = -captive_shell_od / 2;
    z_hi = H + captive_shell_od / 2 + (add_accel_mount ? accel_rise() : 0);
    eps  = 0.005;  // 5 micron, well below FDM extrusion width
    // Use the prism's centroid in XY so the anchor is geometry-only and
    // never collides with cables or scaffold pillars.
    translate([0, 0, z_lo])
        cube([eps, eps, z_hi - z_lo], center=false);
}

// ---- T3-prism assembly -----------------------------------------------------
module t3_prism_struts() {
    union() {
        // Joint nodes (bottom + top). With `use_captive_core` (default),
        // each node is a hollow PLA shell with a teardrop blend toward the
        // strut and one cylindrical exit bore per outgoing TPU cable; the
        // captive TPU mass that holds the cables in place lives inside the
        // shell cavity and is emitted by `t3_prism_cables()`. Otherwise we
        // fall back to a solid joint sphere (legacy behaviour).
        for (i = [0:2]) {
            if (use_captive_core) {
                joint_shell(bottom_pt(i),
                            vertex_strut_dir_b(i),
                            vertex_cable_dirs_b(i));
                joint_shell(top_pt(i),
                            vertex_strut_dir_t(i),
                            vertex_cable_dirs_t(i));
            } else {
                translate(bottom_pt(i)) sphere(d=joint_d);
                translate(top_pt(i))    sphere(d=joint_d);
            }
        }
        // Struts: B_i -> T_i  (compression members)
        for (i = [0:2]) member(bottom_pt(i),   top_pt(i),         strut_d);
        // Accelerometer mounts on top of each top vertex (PLA, so they travel
        // with the rigid struts half in the multi-material variant). The open
        // face points radially outward (heading = the top vertex's polar
        // angle) so the cable feeds away from the structure.
        if (add_accel_mount) {
            for (i = [0:2])
                accel_mount(top_pt(i), 90 + 120*i + twist,
                            vertex_cable_dirs_t(i));
        }
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
        // Captive TPU cores inside each PLA shell cavity — these are what
        // mechanically anchor the cables (the cores are too large to back
        // out any single shell bore). Omitted in legacy solid-joint mode.
        if (use_captive_core) {
            for (i = [0:2]) {
                joint_core(bottom_pt(i));
                joint_core(top_pt(i));
            }
            // Bounding-box anchor so the cables STL inherits the same
            // world-Z extents as the struts STL (keeps Bambu Studio's
            // per-part auto-bed-placement from de-aligning the parts).
            cables_z_anchor();
        }
    }
}

module t3_prism() {
    union() {
        t3_prism_struts();
        t3_prism_cables();
    }
}

// ---- PLA scaffold pillars under the TPU cables ----------------------------
// One vertical pillar up to a touch-point on a cable. The pillar fuses into
// the cable at the top (no air gap) so a slice of PLA cradles the TPU;
// PLA-TPU bond is weak enough to break away cleanly post-print.
//
// IMPORTANT: the bottom of the pillar sits at SCAD z = -joint_d/2 — the same
// height as the underside of the bottom-triangle joint spheres, which is the
// lowest point of the strut/cable model. Bambu Studio (and the BambuStudio
// CLI's `--arrange 1`) lifts the imported assembly so its lowest point sits
// on the build plate; with the pillars rooted at the same z as the joint
// undersides, every pillar reaches the bed instead of floating ~joint_d/2 mm
// above it (PR #35 comment 4464399849).
module pillar_to(target) {
    // Root the pillars at the bottom of the bed-lowest part of the model.
    // In captive-core mode the joint shells are the lowest feature; in
    // legacy solid-joint mode the joint spheres are. Either way the pillar
    // base must sit at the same z as the lowest model point so that when
    // Bambu Studio lifts the assembly to put its lowest point on the bed,
    // every pillar base touches the build plate (PR #35 comment 4464399849).
    z_base = use_captive_core ? -captive_shell_od / 2 : -joint_d / 2;
    z_top  = target[2] - scaffold_d_top * 0.4;  // sink the cone tip slightly into the cable
    h      = z_top - z_base;
    if (h >= scaffold_min_h) {
        translate([target[0], target[1], z_base])
            cylinder(h=h, d1=scaffold_d_bot, d2=scaffold_d_top);
    }
}

module t3_prism_scaffold() {
    // Touch-points at k/(n+1) for k=1..n along each cable. Bottom-triangle
    // cables sit on the bed (z = 0) so their pillars are filtered out by
    // the `scaffold_min_h` cutoff inside `pillar_to`. The remaining 6
    // cables (3 top-triangle + 3 saddle) each get `n_scaffolds` PLA props.
    union() {
        for (i = [0:2]) {
            for (k = [1:n_scaffolds]) {
                t = k / (n_scaffolds + 1);
                pillar_to(bottom_pt(i)     + t * (bottom_pt((i+1)%3) - bottom_pt(i)));
                pillar_to(top_pt(i)        + t * (top_pt((i+1)%3)    - top_pt(i)));
                pillar_to(bottom_pt((i+1)%3) + t * (top_pt(i)        - bottom_pt((i+1)%3)));
            }
        }
    }
}

if      (part == "struts")          translate([offset_x, offset_y, offset_z]) t3_prism_struts();
else if (part == "cables")          translate([offset_x, offset_y, offset_z]) t3_prism_cables();
else if (part == "scaffold")        translate([offset_x, offset_y, offset_z]) t3_prism_scaffold();
else if (part == "struts_scaffold") translate([offset_x, offset_y, offset_z])
                                        union() { t3_prism_struts(); t3_prism_scaffold(); }
else if (part == "all_scaffold")    translate([offset_x, offset_y, offset_z])
                                        union() { t3_prism(); t3_prism_scaffold(); }
else                                translate([offset_x, offset_y, offset_z]) t3_prism();
