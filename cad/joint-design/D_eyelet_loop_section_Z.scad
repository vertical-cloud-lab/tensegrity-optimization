// Section view of Design D — cut at the Z=0 plane, keep +Z half above the joint mid-plane (cut at Z=-2).
// Apply intersection per-color part so PETG/TPU colors survive the CSG.
include <_common.scad>
use <D_eyelet_loop.scad>

module half_cube_Z() { translate([-30, -30, -2]) cube([60, 60, 60]); }

petg() intersection() { designD_petg(); half_cube_Z(); }
tpu()  intersection() { designD_tpu();  half_cube_Z(); }
