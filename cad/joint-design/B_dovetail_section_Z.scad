// Section view of Design B — cut at the Z=0 plane, keep +Z half above the joint mid-plane (cut at Z=-2).
// Apply intersection per-color part so PETG/TPU colors survive the CSG.
include <_common.scad>
use <B_dovetail.scad>

module half_cube_Z() { translate([-30, -30, -2]) cube([60, 60, 60]); }

petg() intersection() { designB_petg(); half_cube_Z(); }
tpu()  intersection() { designB_tpu();  half_cube_Z(); }
