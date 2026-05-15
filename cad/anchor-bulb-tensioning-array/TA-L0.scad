// =============================================================================
// TA-L0 — Axis B (pause+lubricant) specimen: pause well at lower-bore plane
//         (Z = 18.5 mm; ~2.5 mm above the strut top — operator pauses just
//          before the cable enters the bore so lubricant can wick into the
//          full bore length on the next pass).
// Hypothesis: pausing the print, manually applying a thin film of PTFE / dry
// silicone / mineral oil to the partially-printed cable, then resuming gives
// a controllable interface release without any geometry change.
// =============================================================================
include <_common.scad>
specimen_A1(id = "TA-L0", gap_r = 0.2, pause_z = 18.5, sleeve_t = 0);
