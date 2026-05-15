// =============================================================================
// TA-L2 — Axis B (pause+lubricant) specimen: pause well at upper-bore plane
//         (Z = 25.0 mm — pause just before the frustum upset is laid down,
//          so the *upset/node interface* (not the bore) is what gets the
//          lubricant film).
// Tests whether breaking the upset-to-node fusion (rather than the bore-to-
// cable fusion) is the right place to put the release agent — the cable
// would then drag the bonded bore section down with it as a single sleeve.
// =============================================================================
include <_common.scad>
specimen_A1(id = "TA-L2", gap_r = 0.2, pause_z = 25.0, sleeve_t = 0);
