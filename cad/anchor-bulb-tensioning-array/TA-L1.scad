// =============================================================================
// TA-L1 — Axis B (pause+lubricant) specimen: pause well at node-centre plane
//         (Z = 20.75 mm — pause halfway through the bore so lubricant goes on
//          the lower half of the cable but not the upper).
// Tests whether a partial-length lubricated zone is enough to break PLA-TPU
// fusion (smaller release zone may give better pre-tension control).
// =============================================================================
include <_common.scad>
specimen_A1(id = "TA-L1", gap_r = 0.2, pause_z = 20.75, sleeve_t = 0);
