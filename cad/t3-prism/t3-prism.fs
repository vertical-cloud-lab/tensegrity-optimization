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
const T3_R_BOUNDS = { (meter) : [1e-4, 0.025, 1], (centimeter) : 2.5, (millimeter) : 25, (inch) : 1 } as LengthBoundSpec;
const T3_H_BOUNDS = { (meter) : [1e-4, 0.070, 1], (centimeter) : 7.0, (millimeter) : 70, (inch) : 2.75 } as LengthBoundSpec;
const T3_STRUT_BOUNDS = { (meter) : [1e-5, 0.006, 0.5], (centimeter) : 0.6, (millimeter) : 6, (inch) : 0.236 } as LengthBoundSpec;
const T3_CABLE_BOUNDS = { (meter) : [1e-5, 0.003, 0.5], (centimeter) : 0.3, (millimeter) : 3, (inch) : 0.118 } as LengthBoundSpec;
const T3_JOINT_BOUNDS = { (meter) : [1e-5, 0.007, 0.5], (centimeter) : 0.7, (millimeter) : 7, (inch) : 0.276 } as LengthBoundSpec;
const T3_WALL_BOUNDS = { (meter) : [1e-5, 0.0016, 0.1], (centimeter) : 0.16, (millimeter) : 1.6, (inch) : 0.063 } as LengthBoundSpec;
const T3_TRAP_BOUNDS = { (meter) : [1e-5, 0.0015, 0.1], (centimeter) : 0.15, (millimeter) : 1.5, (inch) : 0.059 } as LengthBoundSpec;
const T3_BLEND_BOUNDS = { (meter) : [1e-5, 0.002, 0.1], (centimeter) : 0.2, (millimeter) : 2, (inch) : 0.079 } as LengthBoundSpec;
const T3_POCKET_BOUNDS = { (meter) : [1e-4, 0.0062, 0.1], (centimeter) : 0.62, (millimeter) : 6.2, (inch) : 0.244 } as LengthBoundSpec;
const T3_POCKETZ_BOUNDS = { (meter) : [1e-4, 0.0068, 0.1], (centimeter) : 0.68, (millimeter) : 6.8, (inch) : 0.268 } as LengthBoundSpec;
const T3_AWALL_BOUNDS = { (meter) : [1e-4, 0.002, 0.05], (centimeter) : 0.2, (millimeter) : 2, (inch) : 0.079 } as LengthBoundSpec;
const T3_AFLOOR_BOUNDS = { (meter) : [1e-4, 0.0015, 0.05], (centimeter) : 0.15, (millimeter) : 1.5, (inch) : 0.059 } as LengthBoundSpec;
const T3_ADOME_BOUNDS = { (meter) : [1e-4, 0.003, 0.05], (centimeter) : 0.3, (millimeter) : 3, (inch) : 0.118 } as LengthBoundSpec;
const T3_AROOF_BOUNDS = { (meter) : [0, 0.002, 0.05], (centimeter) : 0.2, (millimeter) : 2, (inch) : 0.079 } as LengthBoundSpec;
const T3_AFLAT_BOUNDS = { (meter) : [1e-4, 0.002, 0.05], (centimeter) : 0.2, (millimeter) : 2, (inch) : 0.079 } as LengthBoundSpec;
const T3_ASINK_BOUNDS = { (meter) : [1e-4, 0.002, 0.05], (centimeter) : 0.2, (millimeter) : 2, (inch) : 0.079 } as LengthBoundSpec;
const T3_AGAP_BOUNDS = { (meter) : [1e-5, 0.001, 0.05], (centimeter) : 0.1, (millimeter) : 1, (inch) : 0.039 } as LengthBoundSpec;
const T3_AHOVER_BOUNDS = { (meter) : [1e-5, 0.002, 0.05], (centimeter) : 0.2, (millimeter) : 2, (inch) : 0.079 } as LengthBoundSpec;
const T3_TWIST_BOUNDS = { (degree) : [0, 60, 360], (radian) : 1.0472 } as AngleBoundSpec;
// S0 sizing = 1.5 x 0.7692 (PR #35, @achris0520). Kept as the default here so a
// freshly-inserted feature reproduces the specimen the team is printing today.
const T3_SCALE_BOUNDS = { (unitless) : [0.05, 1.1538, 20] } as RealBoundSpec;

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
            // Bore lengths follow the SCAD exactly. They must be long enough to
            // clear the thickened (skirted) shell wall but SHORTER than the
            // triangle edge (R * sqrt(3) = 49.96 mm at S0), or a bottom bore
            // would tunnel into the neighbouring joint.
            const boreLenTop = shellOD + definition.pocketX + definition.pocketY + 2 * definition.accelWall;
            const boreLenBot = shellOD + 2 * (rOff + blen / 2);

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
