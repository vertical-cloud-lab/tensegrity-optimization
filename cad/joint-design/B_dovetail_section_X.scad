// Section view of Design B — cut at the X=0 plane, keep +X half (cut at X=0).
// Apply intersection per-color part so PETG/TPU colors survive the CSG.
include <_common.scad>
use <B_dovetail.scad>

module half_cube_X() { translate([0, -30, -40]) cube([60, 60, 60]); }

petg() intersection() { designB_petg(); half_cube_X(); }
tpu()  intersection() { designB_tpu();  half_cube_X(); }
