FeatureScript 2534;
import(path : "onshape/std/geometry.fs", version : "2534.0");

/*
 * ============================================================================
 * T3-prism (3-strut tensegrity) — native Onshape custom feature.
 * ============================================================================
 *
 * This is the FeatureScript port of `cad/t3-prism/t3-prism.scad` (issue #95,
 * "route C": drive Onshape directly so the team gets a LIVE FEATURE TREE with
 * named, editable dimensions instead of an imported dumb solid).
 *
 * Push it into Onshape with:
 *     python3 cad/t3-prism/onshape_featurescript_t3prism.py
 *
 * What this buys over importing an STL / STEP
 * -------------------------------------------
 *   * Every dimension is a named parameter in the feature dialog. "Make the
 *     accel pocket 0.2 mm deeper" is a number you type, then Regenerate.
 *   * The geometry is TRUE B-rep: spheres are spherical faces, struts are
 *     cylindrical faces, and the joint/strut blends are REAL FILLETS.
 *   * Rollback, feature-tree edit and version history all work.
 *
 * Deliberate differences from the SCAD (see cad/t3-prism/README-parametric.md)
 * ---------------------------------------------------------------------------
 *   * OpenSCAD's 10 `hull()` calls have no Parasolid equivalent. The teardrop
 *     joint blend, the igloo skirt and the bottom key-seat skirt are
 *     re-expressed as boolean unions followed by `opFillet` on the
 *     boolean-created edges. That is a smoother, lower-stress transition than
 *     the convex hull, and it is what a CAD engineer would have drawn.
 *   * `$fn = 48` is gone. There is no tessellation parameter — the faces are
 *     analytic.
 *   * `cables_z_anchor()` is omitted. It exists only to pin the bounding box
 *     of a separately-exported STL for Bambu Studio's per-part bed placement;
 *     inside one Part Studio both parts already share a coordinate system.
 *
 * The PLA (struts/joints/housings) and TPU (cables/captive cores) halves are
 * emitted as two SEPARATE parts in the same Part Studio, in the same world
 * coordinates, exactly as `render_print.sh` emits two co-located STLs.
 *
 * Implementation notes for anyone editing this file
 * -------------------------------------------------
 *   * Bound constants are `T3_`-prefixed because the std library already
 *     exports several of the obvious names (`BLEND_BOUNDS` lives in
 *     onshape/std/fillet.fs) and a redeclaration silently kills the whole
 *     Feature Studio's compile with no error message anywhere in the API.
 *   * `opSphere` is used rather than `fSphere`: the `f*` wrapper takes its
 *     centre as a Query (a vertex / mate connector), while the `op*` builder
 *     takes a plain Vector, which is what a generated model wants.
 *   * Operation ids are all flat siblings of `id`. FeatureScript rejects a
 *     parent id used at two non-contiguous points in the operation history, so
 *     the PLA bodies and the cut tools cannot live under two interleaved
 *     prefixes; bodies are collected into query arrays instead.
 * ============================================================================
 */

// ---- Parameter bounds ------------------------------------------------------
// These are the per-parameter limits the dialog enforces as you type. They are
// deliberately much tighter than "any positive length": the previous 0.05-1 m
// maxima let you put a 500 mm strut diameter on a 70 mm prism, or a 50 mm dome
// on a 8.2 mm housing (issue #95, @me-madsen -- the floating crown). A bound
// spec can only see ONE parameter though, so the genuinely coupled limits are
// checked in the feature body; see "Parameter constraints" below.
//
// The MINIMA on wall-like dimensions are one 0.4 mm nozzle width: thinner than
// that is not something the printer can make, and it is also where Parasolid
// starts producing slivers.
const T3_R_BOUNDS = { (meter) : [0.002, 0.025, 0.3], (centimeter) : 2.5, (millimeter) : 25, (inch) : 1 } as LengthBoundSpec;
const T3_H_BOUNDS = { (meter) : [0.002, 0.070, 0.5], (centimeter) : 7.0, (millimeter) : 70, (inch) : 2.75 } as LengthBoundSpec;
const T3_STRUT_BOUNDS = { (meter) : [0.0005, 0.006, 0.05], (centimeter) : 0.6, (millimeter) : 6, (inch) : 0.236 } as LengthBoundSpec;
const T3_CABLE_BOUNDS = { (meter) : [0.0005, 0.003, 0.05], (centimeter) : 0.3, (millimeter) : 3, (inch) : 0.118 } as LengthBoundSpec;
const T3_JOINT_BOUNDS = { (meter) : [0.0005, 0.007, 0.05], (centimeter) : 0.7, (millimeter) : 7, (inch) : 0.276 } as LengthBoundSpec;
const T3_WALL_BOUNDS = { (meter) : [0.0004, 0.0016, 0.01], (centimeter) : 0.16, (millimeter) : 1.6, (inch) : 0.063 } as LengthBoundSpec;
const T3_TRAP_BOUNDS = { (meter) : [0, 0.0015, 0.01], (centimeter) : 0.15, (millimeter) : 1.5, (inch) : 0.059 } as LengthBoundSpec;
const T3_BLEND_BOUNDS = { (meter) : [1e-5, 0.002, 0.01], (centimeter) : 0.2, (millimeter) : 2, (inch) : 0.079 } as LengthBoundSpec;
const T3_POCKET_BOUNDS = { (meter) : [0.001, 0.0062, 0.04], (centimeter) : 0.62, (millimeter) : 6.2, (inch) : 0.244 } as LengthBoundSpec;
const T3_POCKETZ_BOUNDS = { (meter) : [0.001, 0.0068, 0.04], (centimeter) : 0.68, (millimeter) : 6.8, (inch) : 0.268 } as LengthBoundSpec;
const T3_AWALL_BOUNDS = { (meter) : [0.0004, 0.002, 0.01], (centimeter) : 0.2, (millimeter) : 2, (inch) : 0.079 } as LengthBoundSpec;
const T3_AFLOOR_BOUNDS = { (meter) : [0.0004, 0.0015, 0.01], (centimeter) : 0.15, (millimeter) : 1.5, (inch) : 0.059 } as LengthBoundSpec;
const T3_ADOME_BOUNDS = { (meter) : [0.0002, 0.003, 0.02], (centimeter) : 0.3, (millimeter) : 3, (inch) : 0.118 } as LengthBoundSpec;
const T3_AROOF_BOUNDS = { (meter) : [0, 0.002, 0.02], (centimeter) : 0.2, (millimeter) : 2, (inch) : 0.079 } as LengthBoundSpec;
const T3_AFLAT_BOUNDS = { (meter) : [0.0004, 0.002, 0.02], (centimeter) : 0.2, (millimeter) : 2, (inch) : 0.079 } as LengthBoundSpec;
const T3_ASINK_BOUNDS = { (meter) : [0.0002, 0.002, 0.02], (centimeter) : 0.2, (millimeter) : 2, (inch) : 0.079 } as LengthBoundSpec;
const T3_AGAP_BOUNDS = { (meter) : [0, 0.001, 0.01], (centimeter) : 0.1, (millimeter) : 1, (inch) : 0.039 } as LengthBoundSpec;
const T3_AHOVER_BOUNDS = { (meter) : [0, 0.002, 0.02], (centimeter) : 0.2, (millimeter) : 2, (inch) : 0.079 } as LengthBoundSpec;
const T3_TWIST_BOUNDS = { (degree) : [0, 60, 360], (radian) : 1.0472 } as AngleBoundSpec;
// S0 sizing = 1.5 x 0.7692 (PR #35, @achris0520). Kept as the default here so a
// freshly-inserted feature reproduces the specimen the team is printing today.
// The accelerometer housings are ABSOLUTE mm (they hold a physical sensor) and
// deliberately do not scale, so far outside this range the housing stops being
// in any sensible proportion to the joint it sits on.
const T3_SCALE_BOUNDS = { (unitless) : [0.2, 1.1538, 5] } as RealBoundSpec;

/** Format a length for an error message, e.g. "8.2 mm". */
function mmStr(v is ValueWithUnits) returns string
{
    return toString(round(v / millimeter * 100) / 100) ~ " mm";
}

/** Which half of the multi-material model to emit. Mirrors the SCAD `part`. */
export enum T3Part
{
    annotation { "Name" : "Both (PLA struts + TPU cables)" }
    BOTH,
    annotation { "Name" : "Struts only (PLA)" }
    STRUTS,
    annotation { "Name" : "Cables only (TPU)" }
    CABLES
}

// ---- Vertex positions ------------------------------------------------------
// B_i = (R cos(90 + 120 i), R sin(90 + 120 i), 0)
// T_i = (R cos(90 + 120 i + twist), R sin(90 + 120 i + twist), H)
function bottomPt(R is ValueWithUnits, i) returns Vector
{
    const a = (90 + 120 * i) * degree;
    return vector(R * cos(a), R * sin(a), R * 0);
}

function topPt(R is ValueWithUnits, H is ValueWithUnits, twist is ValueWithUnits, i) returns Vector
{
    const a = (90 + 120 * i) * degree + twist;
    return vector(R * cos(a), R * sin(a), H);
}

/** Outgoing (away-from-vertex) unit directions of the three cables at B_i. */
function cableDirsB(R is ValueWithUnits, H is ValueWithUnits, twist is ValueWithUnits, i) returns array
{
    const V = bottomPt(R, i);
    return [
            normalize(bottomPt(R, (i + 1) % 3) - V),
            normalize(bottomPt(R, (i + 2) % 3) - V),
            normalize(topPt(R, H, twist, (i + 2) % 3) - V)
        ];
}

/** Outgoing (away-from-vertex) unit directions of the three cables at T_i. */
function cableDirsT(R is ValueWithUnits, H is ValueWithUnits, twist is ValueWithUnits, i) returns array
{
    const V = topPt(R, H, twist, i);
    return [
            normalize(topPt(R, H, twist, (i + 1) % 3) - V),
            normalize(topPt(R, H, twist, (i + 2) % 3) - V),
            normalize(bottomPt(R, (i + 1) % 3) - V)
        ];
}

/**
 * Capsule = cylinder with hemispherical end caps (the SCAD `member` module).
 * Returns a query matching every body it created.
 */
function capsule(context is Context, id is Id, p1 is Vector, p2 is Vector, r is ValueWithUnits) returns Query
{
    fCylinder(context, id + "shaft", { "topCenter" : p2, "bottomCenter" : p1, "radius" : r });
    opSphere(context, id + "capA", { "center" : p1, "radius" : r });
    opSphere(context, id + "capB", { "center" : p2, "radius" : r });
    return qCreatedBy(id, EntityType.BODY);
}

/**
 * Outward-only cable exit bore, the SCAD `bore_along` module. Starts a hair
 * BEHIND the vertex centre so it always breaks through the inner cavity wall,
 * and runs out to `len` along `dir`. Outward-only by design: a centred bore
 * punches a second, unwanted hole out the far side of the shell (the mystery
 * "holes on a lot of the vertices", PR #35 comment 4514072758).
 */
function boreAlong(context is Context, id is Id, V is Vector, dir is Vector, d is ValueWithUnits, len is ValueWithUnits) returns Query
{
    fCylinder(context, id, {
                "bottomCenter" : V - dir * (0.5 * millimeter),
                "topCenter" : V + dir * len,
                "radius" : d / 2
            });
    return qCreatedBy(id, EntityType.BODY);
}

/**
 * Accelerometer housing body, built axis-aligned at the origin exactly like the
 * SCAD `accel_mount_local`: +X is the open (slide-in / cable-exit) face and the
 * pocket floor is at local z = 0. `domed` picks the rounded igloo crown (top
 * vertices, low friction against the acrylic drop plate) over the flat cap
 * (bottom key-seats).
 *
 * The pocket cutter is NOT made here — the caller makes it under its own id so
 * it can be routed into the single global subtraction.
 */
function accelMountBody(context is Context, id is Id, definition is map, domed is boolean) returns Query
{
    const px = definition.pocketX;
    const py = definition.pocketY;
    const bx0 = -definition.accelWall;
    const bx1 = px;
    const byh = py / 2 + definition.accelWall;
    const bz0 = -(definition.accelFloor + definition.accelSink);
    const zero = px * 0;
    // Top of the straight walls. On the DOMED top mounts the body is carried
    // `accelRoof` past the pocket ceiling first: the pocket mouth is flush with
    // the body's front face (bx1 == px), so the pocket's top-front edge *is* the
    // body's top-front edge and a crown springing straight off that rim feathers
    // out to nothing there (issue #95 -- measured 0.085 mm at the mouth vs
    // 2.99 mm at the centre). The FLAT bottom key-seats already carry a uniform
    // `accelFlat` slab, so they keep bz1 == pocketZ and are unchanged.
    const bz1 = definition.pocketZ + (domed ? definition.accelRoof : zero);
    const cx = (bx0 + bx1) / 2;

    fCuboid(context, id + "box", {
                "corner1" : vector(bx0, -byh, bz0),
                "corner2" : vector(bx1, byh, bz1)
            });

    if (domed)
    {
        // SCAD hulls the top rim up to a sphere. Union + fillet gives the same
        // "rounded thing on top" with a tangent-continuous crown instead.
        const rcrown = min(bx1 - bx0, 2 * byh) / 2;
        opSphere(context, id + "crown", {
                    "center" : vector(cx, zero, bz1 + definition.accelDome - rcrown),
                    "radius" : rcrown
                });
    }
    else
    {
        fCuboid(context, id + "cap", {
                    "corner1" : vector(bx0, -byh, bz1),
                    "corner2" : vector(bx1, byh, bz1 + definition.accelFlat)
                });
    }
    return qCreatedBy(id, EntityType.BODY);
}

/** The pocket cutter for `accelMountBody`: three walls + floor + cap, open +X. */
function accelMountCutter(context is Context, id is Id, definition is map) returns Query
{
    const px = definition.pocketX;
    const py = definition.pocketY;
    const byh = py / 2 + definition.accelWall;
    const zero = px * 0;
    fCuboid(context, id, {
                "corner1" : vector(zero, -py / 2, zero),
                "corner2" : vector(px + byh + 5 * millimeter, py / 2, definition.pocketZ)
            });
    return qCreatedBy(id, EntityType.BODY);
}

annotation { "Feature Type Name" : "T3 Prism (tensegrity)" }
export const t3Prism = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Emit" }
        definition.part is T3Part;

        annotation { "Group Name" : "Prism", "Collapsed By Default" : false }
        {
            annotation { "Name" : "Circumradius R (base)" }
            isLength(definition.RBase, T3_R_BOUNDS);

            annotation { "Name" : "Height H (base)" }
            isLength(definition.HBase, T3_H_BOUNDS);

            annotation { "Name" : "Twist" }
            isAngle(definition.twist, T3_TWIST_BOUNDS);

            annotation { "Name" : "Strut diameter (base)" }
            isLength(definition.strutDBase, T3_STRUT_BOUNDS);

            annotation { "Name" : "Cable diameter (base)" }
            isLength(definition.cableDBase, T3_CABLE_BOUNDS);

            annotation { "Name" : "Joint diameter (base)" }
            isLength(definition.jointDBase, T3_JOINT_BOUNDS);

            annotation { "Name" : "Scale factor (S0 = 1.5 x 0.7692)" }
            isReal(definition.scaleFactor, T3_SCALE_BOUNDS);
        }

        annotation { "Group Name" : "Captive-core joints", "Collapsed By Default" : true }
        {
            annotation { "Name" : "Captive TPU core inside a PLA shell" }
            definition.useCaptiveCore is boolean;

            if (definition.useCaptiveCore)
            {
                annotation { "Name" : "Shell wall thickness (base)" }
                isLength(definition.captiveWallBase, T3_WALL_BOUNDS);

                annotation { "Name" : "Bore trap (core radius over bore radius)" }
                isLength(definition.captiveBoreTrap, T3_TRAP_BOUNDS);
            }

            annotation { "Name" : "Joint/strut blend radius" }
            isLength(definition.blendRadius, T3_BLEND_BOUNDS);
        }

        annotation { "Group Name" : "Accelerometer housings", "Collapsed By Default" : true }
        {
            annotation { "Name" : "Domed igloo mounts on the top vertices" }
            definition.addAccelTop is boolean;

            annotation { "Name" : "Flat key-seats beside the bottom vertices" }
            definition.addAccelBottom is boolean;

            if (definition.addAccelTop || definition.addAccelBottom)
            {
                annotation { "Name" : "Pocket X (slide-in axis)" }
                isLength(definition.pocketX, T3_POCKET_BOUNDS);

                annotation { "Name" : "Pocket Y" }
                isLength(definition.pocketY, T3_POCKET_BOUNDS);

                annotation { "Name" : "Pocket Z (depth)" }
                isLength(definition.pocketZ, T3_POCKETZ_BOUNDS);

                annotation { "Name" : "Wall thickness" }
                isLength(definition.accelWall, T3_AWALL_BOUNDS);

                annotation { "Name" : "Floor thickness" }
                isLength(definition.accelFloor, T3_AFLOOR_BOUNDS);

                annotation { "Name" : "Sink past joint apex" }
                isLength(definition.accelSink, T3_ASINK_BOUNDS);
            }

            if (definition.addAccelTop)
            {
                annotation { "Name" : "Dome (crown) thickness" }
                isLength(definition.accelDome, T3_ADOME_BOUNDS);

                annotation { "Name" : "Roof over the pocket (under the crown)" }
                isLength(definition.accelRoof, T3_AROOF_BOUNDS);
            }

            if (definition.addAccelBottom)
            {
                annotation { "Name" : "Flat cap thickness" }
                isLength(definition.accelFlat, T3_AFLAT_BOUNDS);

                annotation { "Name" : "Radial gap to the joint sphere" }
                isLength(definition.accelSideGap, T3_AGAP_BOUNDS);

                annotation { "Name" : "Hover above the joint underside" }
                isLength(definition.accelHover, T3_AHOVER_BOUNDS);
            }
        }
    }
    {
        // ---- Derived dimensions (mirrors the SCAD's derived block) ---------
        const s = definition.scaleFactor;
        const R = definition.RBase * s;
        const H = definition.HBase * s;
        const twist = definition.twist;
        const strutR = definition.strutDBase * s / 2;
        const cableD = definition.cableDBase * s;
        const cableR = cableD / 2;
        const jointD = definition.jointDBase * s;

        // Captive-core sizing. Clearances are zero by design (PR #35 comment
        // 4513722886): the TPU core is bonded to the inner shell wall and the
        // cable fills its exit bore exactly, so there is no annular air ring.
        const boreD = cableD;
        const coreOD = max(boreD + 2 * definition.captiveBoreTrap, jointD);
        const shellID = coreOD;
        const shellOD = max(shellID + 2 * definition.captiveWallBase * s, jointD);
        const jointOuterR = definition.useCaptiveCore ? shellOD / 2 : jointD / 2;

        // Accelerometer-housing derived box dimensions.
        const blen = definition.pocketX + definition.accelWall;      // body length
        const byw = definition.pocketY + 2 * definition.accelWall;   // body width
        const cxLocal = (-definition.accelWall + definition.pocketX) / 2;
        const bz0 = -(definition.accelFloor + definition.accelSink);
        const rOff = jointOuterR + blen / 2 + definition.accelSideGap;
        const zeroLen = definition.pocketX * 0;

        // Cable exit bore lengths, hoisted out of the captive-core block below
        // so the tunnelling check can see them. They must clear the thickened
        // (skirted) shell wall but stay SHORTER than the triangle edge.
        const boreLenTop = shellOD + definition.pocketX + definition.pocketY + 2 * definition.accelWall;
        const boreLenBot = shellOD + 2 * (rOff + blen / 2);

        // ================= Parameter constraints ===========================
        // The bound specs above police each parameter in isolation. These are
        // the CROSS-parameter ones: every value is individually legal and the
        // combination still produces something that is not the model. Issue
        // #95, @me-madsen -- "some constraints will likely also need to be
        // implemented to avoid artifacts like this when playing with the
        // feature dialogue box."
        //
        // Note that some of these are specific to the B-rep ports. OpenSCAD
        // builds the crown as hull(top rim, sphere), which stays connected for
        // ANY dome height; Parasolid and OCCT have no convex hull, so both use
        // a plain union and the crown simply floats away once it clears the
        // body. Same model, a failure mode the mesh version cannot have.

        // -- The three compression members must stay mutually disconnected.
        //    That is the definition of a tensegrity, not a stylistic choice.
        const edge = R * sqrt(3);   // |B_i B_{i+1}| == |T_i T_{i+1}|
        if (2 * jointOuterR >= edge)
        {
            throw regenError("Joint spheres are " ~ mmStr(2 * jointOuterR) ~
                        " across but adjacent vertices are only " ~ mmStr(edge) ~
                        " apart, so the three struts fuse into a single body. A tensegrity requires that no two compression members touch. Reduce the joint diameter (or the shell wall) or increase R.",
                        ["jointDBase", "RBase"]);
        }

        // -- Domed top mounts: the crown has to stay attached to the housing.
        if (definition.addAccelTop)
        {
            const rcrown = min(blen, byw) / 2;
            const domeMax = 2 * rcrown;
            if (definition.accelDome >= domeMax)
            {
                throw regenError("Dome (crown) thickness must be under " ~ mmStr(domeMax) ~
                            " -- twice the crown radius, which is half the smaller of the housing's " ~
                            mmStr(blen) ~ " length and " ~ mmStr(byw) ~
                            " width. Above that the crown sphere lifts clear of the housing roof and is left floating in mid-air. Widen the pocket or the wall to buy more dome.",
                            ["accelDome", "pocketX", "pocketY", "accelWall"]);
            }
            // Circle where the crown meets the flat roof. Close to either
            // tangency (a shallow blister, or a ball balanced on a pin) that
            // rim is a knife edge -- the same defect class as the paper-thin
            // ceiling fixed earlier in this issue, and the same thing that
            // makes OCCT abort on a tangent fillet.
            const dmm = definition.accelDome / millimeter;
            const rcmm = rcrown / millimeter;
            const seatD = 2 * sqrt(dmm * (2 * rcmm - dmm)) * millimeter;
            if (seatD < rcrown)
            {
                reportFeatureWarning(context, id, "The crown meets the housing roof along a " ~
                            mmStr(seatD) ~ " circle, nearly tangent to it -- that rim is a knife edge. A dome between " ~
                            mmStr(rcrown * (1 - sqrt(0.75))) ~ " and " ~ mmStr(rcrown * (1 + sqrt(0.75))) ~
                            " gives it a proper seat.");
            }
            if (definition.accelRoof < 0.4 * millimeter)
            {
                reportFeatureWarning(context, id, "Roof over the pocket is " ~ mmStr(definition.accelRoof) ~
                            ", under two 0.2 mm layers. The pocket mouth is flush with the housing's front face, so the roof is the only thing stopping the ceiling feathering out to a knife edge there -- it measured 0.085 mm with no roof at all.");
            }
        }

        // -- Flat bottom key-seats: the seat and its skirt have to reach the
        //    joint sphere. The skirt's inner face sits at 0.4 * jointOuterR,
        //    where the sphere's upper surface is this far above the vertex.
        if (definition.addAccelBottom)
        {
            const jrmm = jointOuterR / millimeter;
            const hoverMax = (jrmm + sqrt(jrmm * jrmm - 0.16 * jrmm * jrmm)) * millimeter;
            if (definition.accelHover >= hoverMax)
            {
                throw regenError("Hover above the joint underside must be under " ~ mmStr(hoverMax) ~
                            " or the key-seat and its skirt lift clear of the " ~ mmStr(2 * jointOuterR) ~
                            " joint sphere and float free of the strut.",
                            ["accelHover", "jointDBase"]);
            }
        }

        // -- Cable exit bores must not tunnel into the NEXT vertex. This one
        //    is silent when it goes wrong: you get a clean-looking model with
        //    a hole drilled through a neighbouring joint shell.
        if (definition.useCaptiveCore)
        {
            const boreMax = edge - jointOuterR;   // where the neighbour's shell begins
            const boreLen = max(boreLenTop, boreLenBot);
            if (boreLen >= boreMax)
            {
                throw regenError("Cable exit bores run " ~ mmStr(boreLen) ~
                            " but the neighbouring joint's shell starts " ~ mmStr(boreMax) ~
                            " away along the triangle edge, so a bore would punch straight through it. Reduce the bottom key-seat's radial gap or the pocket size, or increase R.",
                            ["accelSideGap", "pocketX", "pocketY", "RBase"]);
            }

            const shellWall = (shellOD - shellID) / 2;
            if (shellWall < 0.8 * millimeter)
            {
                reportFeatureWarning(context, id, "The PLA shell around the captive TPU core is only " ~
                            mmStr(shellWall) ~ " thick, under two 0.4 mm extrusions. The core is bonded to it at zero clearance, so a shell this thin will split when the cable is tensioned.");
            }
        }

        if (definition.addAccelTop || definition.addAccelBottom)
        {
            if (definition.accelWall < 0.8 * millimeter || definition.accelFloor < 0.8 * millimeter)
            {
                reportFeatureWarning(context, id, "Pocket wall (" ~ mmStr(definition.accelWall) ~
                            ") or floor (" ~ mmStr(definition.accelFloor) ~
                            ") is under 0.8 mm, i.e. thinner than two 0.4 mm extrusions -- the housing prints as a single unsupported perimeter.");
            }
        }
        // =================== end parameter constraints =====================

        var plaBodies = [];   // everything that ends up as the PLA part
        var cutBodies = [];   // cavity spheres, cable bores and accel pockets
        var tpuBodies = [];   // cables and captive cores

        // ---- Joint nodes + struts -----------------------------------------
        for (var i = 0; i < 3; i += 1)
        {
            const B = bottomPt(R, i);
            const T = topPt(R, H, twist, i);
            const si = toString(i);

            opSphere(context, id + ("nodeB" ~ si), { "center" : B, "radius" : jointOuterR });
            plaBodies = append(plaBodies, qCreatedBy(id + ("nodeB" ~ si), EntityType.BODY));

            opSphere(context, id + ("nodeT" ~ si), { "center" : T, "radius" : jointOuterR });
            plaBodies = append(plaBodies, qCreatedBy(id + ("nodeT" ~ si), EntityType.BODY));

            // Strut i: B_i -> T_i (the compression member).
            plaBodies = append(plaBodies, capsule(context, id + ("strut" ~ si), B, T, strutR));
        }

        // ---- Accelerometer housings ---------------------------------------
        // Both variants are unioned straight into the joint sphere and then
        // filleted, which replaces the SCAD's hulled "skirt" with a real
        // tangent blend.
        if (definition.addAccelTop)
        {
            for (var i = 0; i < 3; i += 1)
            {
                const T = topPt(R, H, twist, i);
                const si = toString(i);
                const ang = (90 + 120 * i) * degree + twist;
                const z0 = T[2] + jointOuterR + definition.accelFloor;
                const xf = transform(vector(T[0], T[1], z0)) *
                    rotationAround(Z_AXIS, ang) *
                    transform(vector(-cxLocal, zeroLen, zeroLen));

                const bodyQ = accelMountBody(context, id + ("mtT" ~ si), definition, true);
                opTransform(context, id + ("mtTxf" ~ si), { "bodies" : bodyQ, "transform" : xf });
                plaBodies = append(plaBodies, bodyQ);

                const cutQ = accelMountCutter(context, id + ("mtTcut" ~ si), definition);
                opTransform(context, id + ("mtTcutxf" ~ si), { "bodies" : cutQ, "transform" : xf });
                cutBodies = append(cutBodies, cutQ);
            }
        }

        if (definition.addAccelBottom)
        {
            for (var i = 0; i < 3; i += 1)
            {
                const B = bottomPt(R, i);
                const si = toString(i);
                const ang = (90 + 120 * i) * degree;
                // Lift so the seat underside hovers `accelHover` above the joint
                // underside — the joint sphere, not the seat, is what touches
                // the plate (PR #35 comment 4859762053).
                const z0 = B[2] - jointOuterR + definition.accelHover - bz0;
                const seat = transform(vector(B[0], B[1], z0)) * rotationAround(Z_AXIS, ang);
                const xf = seat * transform(vector(rOff - cxLocal, zeroLen, zeroLen));

                const bodyQ = accelMountBody(context, id + ("mtB" ~ si), definition, false);
                opTransform(context, id + ("mtBxf" ~ si), { "bodies" : bodyQ, "transform" : xf });
                plaBodies = append(plaBodies, bodyQ);

                const cutQ = accelMountCutter(context, id + ("mtBcut" ~ si), definition);
                opTransform(context, id + ("mtBcutxf" ~ si), { "bodies" : cutQ, "transform" : xf });
                cutBodies = append(cutBodies, cutQ);

                // Skirt: a slab bridging the radial gap from the joint sphere to
                // the seat's inner face, so PLA runs continuously from the vertex
                // into the seat (no overhanging lip / stress riser). The SCAD
                // hulls this; here it is unioned and then filleted.
                fCuboid(context, id + ("skirt" ~ si), {
                            "corner1" : vector(jointOuterR * 0.4, -byw / 2, bz0),
                            "corner2" : vector(rOff - blen / 2 + 0.5 * millimeter, byw / 2, definition.pocketZ)
                        });
                opTransform(context, id + ("skirtxf" ~ si), {
                            "bodies" : qCreatedBy(id + ("skirt" ~ si), EntityType.BODY),
                            "transform" : seat
                        });
                plaBodies = append(plaBodies, qCreatedBy(id + ("skirt" ~ si), EntityType.BODY));
            }
        }

        // ---- Fuse the PLA half, then blend --------------------------------
        opBoolean(context, id + "plaUnion", {
                    "tools" : qUnion(plaBodies),
                    "operationType" : BooleanOperationType.UNION
                });

        // The teardrop. OpenSCAD hulls a small sphere out along the strut axis
        // to kill the re-entrant corner where the strut meets the shell;
        // Parasolid has a better tool for that, so use it. Fall back to
        // progressively smaller radii, and then to no blend at all, rather than
        // failing the whole feature on a geometry that will not take 2 mm.
        var blendR = definition.blendRadius;
        for (var attempt = 0; attempt < 4; attempt += 1)
        {
            const blendId = id + ("plaBlend" ~ toString(attempt));
            try silent
            {
                opFillet(context, blendId, {
                            "entities" : qCreatedBy(id + "plaUnion", EntityType.EDGE),
                            "radius" : blendR
                        });
            }
            if (size(evaluateQuery(context, qCreatedBy(blendId, EntityType.FACE))) > 0)
            {
                break;
            }
            blendR = blendR / 2;
        }

        // ---- Hollow the shells and punch the cable exit bores --------------
        if (definition.useCaptiveCore)
        {
            // boreLenTop / boreLenBot follow the SCAD exactly and are computed
            // up in the derived block, where the tunnelling check guards them.
            for (var i = 0; i < 3; i += 1)
            {
                const B = bottomPt(R, i);
                const T = topPt(R, H, twist, i);
                const si = toString(i);

                opSphere(context, id + ("cavB" ~ si), { "center" : B, "radius" : shellID / 2 });
                cutBodies = append(cutBodies, qCreatedBy(id + ("cavB" ~ si), EntityType.BODY));

                opSphere(context, id + ("cavT" ~ si), { "center" : T, "radius" : shellID / 2 });
                cutBodies = append(cutBodies, qCreatedBy(id + ("cavT" ~ si), EntityType.BODY));

                const dB = cableDirsB(R, H, twist, i);
                const dT = cableDirsT(R, H, twist, i);
                for (var k = 0; k < 3; k += 1)
                {
                    const sk = toString(k);
                    cutBodies = append(cutBodies,
                            boreAlong(context, id + ("boreB" ~ si ~ sk), B, dB[k], boreD, boreLenBot));
                    cutBodies = append(cutBodies,
                            boreAlong(context, id + ("boreT" ~ si ~ sk), T, dT[k], boreD, boreLenTop));
                }
            }
        }

        if (size(cutBodies) > 0)
        {
            opBoolean(context, id + "plaCut", {
                        "targets" : qUnion(plaBodies),
                        "tools" : qUnion(cutBodies),
                        "operationType" : BooleanOperationType.SUBTRACTION
                    });
        }

        // -- Topological invariant, the catch-all behind the closed-form
        //    checks above. Whatever combination someone types, the PLA half is
        //    3 solids: strut i plus its two joints and their housings, and the
        //    three of them never touch. Anything else is an artifact, and this
        //    catches the ones nobody has enumerated yet.
        const plaSolids = size(evaluateQuery(context, qUnion(plaBodies)));
        if (plaSolids != 3)
        {
            throw regenError("The PLA half regenerated as " ~ toString(plaSolids) ~
                        " solids, not 3. A T3 tensegrity has exactly three mutually disconnected compression members. More than 3 means a piece broke away from its strut (a floating accelerometer crown or key-seat is the usual cause); fewer means two struts have fused, which is no longer a tensegrity.");
        }

        // ---- TPU half: 9 cables + 6 captive cores -------------------------
        for (var i = 0; i < 3; i += 1)
        {
            const si = toString(i);
            // Bottom triangle: B_i -> B_{i+1}
            tpuBodies = append(tpuBodies, capsule(context, id + ("botC" ~ si),
                        bottomPt(R, i), bottomPt(R, (i + 1) % 3), cableR));
            // Top triangle: T_i -> T_{i+1}
            tpuBodies = append(tpuBodies, capsule(context, id + ("topC" ~ si),
                        topPt(R, H, twist, i), topPt(R, H, twist, (i + 1) % 3), cableR));
            // Saddle: B_{i+1} -> T_i. Strut i and saddle i meet at T_i but start
            // from different bottom vertices — the defining tensegrity property
            // (no two compression members touch).
            tpuBodies = append(tpuBodies, capsule(context, id + ("sadC" ~ si),
                        bottomPt(R, (i + 1) % 3), topPt(R, H, twist, i), cableR));

            if (definition.useCaptiveCore)
            {
                opSphere(context, id + ("coreB" ~ si), { "center" : bottomPt(R, i), "radius" : coreOD / 2 });
                tpuBodies = append(tpuBodies, qCreatedBy(id + ("coreB" ~ si), EntityType.BODY));

                opSphere(context, id + ("coreT" ~ si), { "center" : topPt(R, H, twist, i), "radius" : coreOD / 2 });
                tpuBodies = append(tpuBodies, qCreatedBy(id + ("coreT" ~ si), EntityType.BODY));
            }
        }

        opBoolean(context, id + "tpuUnion", {
                    "tools" : qUnion(tpuBodies),
                    "operationType" : BooleanOperationType.UNION
                });

        // The 9 cables and 6 captive cores meet at shared vertex points, so the
        // tension net is one connected body no matter what the numbers are.
        const tpuSolids = size(evaluateQuery(context, qUnion(tpuBodies)));
        if (tpuSolids != 1)
        {
            throw regenError("The TPU half regenerated as " ~ toString(tpuSolids) ~
                        " solids, not 1. The nine cables and six captive cores form a single connected tension net; more than one body means a cable has come away from its vertex.");
        }

        // ---- Part selection + naming --------------------------------------
        if (definition.part == T3Part.STRUTS)
        {
            opDeleteBodies(context, id + "dropTpu", { "entities" : qUnion(tpuBodies) });
        }
        else
        {
            setProperty(context, {
                        "entities" : qUnion(tpuBodies),
                        "propertyType" : PropertyType.NAME,
                        "value" : "t3-prism-cables (TPU)"
                    });
        }

        if (definition.part == T3Part.CABLES)
        {
            opDeleteBodies(context, id + "dropPla", { "entities" : qUnion(plaBodies) });
        }
        else
        {
            setProperty(context, {
                        "entities" : qUnion(plaBodies),
                        "propertyType" : PropertyType.NAME,
                        "value" : "t3-prism-struts (PLA)"
                    });
        }
    }, {
            part : T3Part.BOTH,
            RBase : 25 * millimeter,
            HBase : 70 * millimeter,
            twist : 60 * degree,
            strutDBase : 6 * millimeter,
            cableDBase : 3 * millimeter,
            jointDBase : 7 * millimeter,
            scaleFactor : 1.1538,
            useCaptiveCore : true,
            captiveWallBase : 1.6 * millimeter,
            captiveBoreTrap : 1.5 * millimeter,
            blendRadius : 2 * millimeter,
            addAccelTop : true,
            addAccelBottom : true,
            pocketX : 6.2 * millimeter,
            pocketY : 6.2 * millimeter,
            pocketZ : 6.8 * millimeter,
            accelWall : 2 * millimeter,
            accelFloor : 1.5 * millimeter,
            accelSink : 2 * millimeter,
            accelDome : 3 * millimeter,
            accelRoof : 2 * millimeter,
            accelFlat : 2 * millimeter,
            accelSideGap : 1 * millimeter,
            accelHover : 2 * millimeter
        });
