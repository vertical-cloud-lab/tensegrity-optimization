// =============================================================================
// H-S0G4 — A3 countersunk specimen: node Ø 7.5 mm, radial air gap 0.6 mm
//          (bore Ø = 3.6 mm vs. 2.4 mm cable)
// Horizontal-cable orientation: the cable axis lies in the build plate (+Y),
// so this specimen exercises the worst-case "TPU bridges the bore horizontally
// against gravity" failure mode flagged in PR #84 review (comment 4462368734).
// =============================================================================
include <_common.scad>
specimen_A3(id = "H-S0G4", node_d = 7.5, gap_r = 0.6);
