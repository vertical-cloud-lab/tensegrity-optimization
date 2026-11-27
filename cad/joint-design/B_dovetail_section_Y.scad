// Section view of Design B — dovetail captive joint cut at Y=0 (keep -Y
// half), color preserved by per-part intersection.
include <_common.scad>
use <B_dovetail.scad>

module half_cube_negY() { translate([-30, -30, -40]) cube([60, 30, 60]); }

petg() intersection() { designB_petg(); half_cube_negY(); }
tpu()  intersection() { designB_tpu();  half_cube_negY(); }
