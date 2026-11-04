// =============================================================================
// H-S1G2 — A3 countersunk specimen: node Ø 9.5 mm, radial air gap 0.3 mm
//          (bore Ø = 3.0 mm vs. 2.4 mm cable)
// Horizontal-cable orientation: the cable axis lies in the build plate (+Y),
// so this specimen exercises the worst-case "TPU bridges the bore horizontally
// against gravity" failure mode flagged in PR #84 review (comment 4462368734).
// =============================================================================
include <_common.scad>
specimen_A3(id = "H-S1G2", node_d = 9.5, gap_r = 0.3);
