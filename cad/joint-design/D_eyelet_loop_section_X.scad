// Section view of Design D — cut at the X=0 plane, keep +X half (cut at X=0).
// Apply intersection per-color part so PETG/TPU colors survive the CSG.
include <_common.scad>
use <D_eyelet_loop.scad>

module half_cube_X() { translate([0, -30, -40]) cube([60, 60, 60]); }

petg() intersection() { designD_petg(); half_cube_X(); }
tpu()  intersection() { designD_tpu();  half_cube_X(); }
