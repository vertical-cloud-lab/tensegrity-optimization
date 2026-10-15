// Section view of Design D — cut at the Y=0 plane, keep -Y half (cut at Y=0).
// Apply intersection per-color part so PETG/TPU colors survive the CSG.
include <_common.scad>
use <D_eyelet_loop.scad>

module half_cube_Y() { translate([-30, -30, -40]) cube([60, 30, 60]); }

petg() intersection() { designD_petg(); half_cube_Y(); }
tpu()  intersection() { designD_tpu();  half_cube_Y(); }
