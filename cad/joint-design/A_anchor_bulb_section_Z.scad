// Section view of Design A — cut at the Z=0 plane, keep +Z half above the joint mid-plane (cut at Z=-2).
// Apply intersection per-color part so PETG/TPU colors survive the CSG.
include <_common.scad>
use <A_anchor_bulb.scad>

module half_cube_Z() { translate([-30, -30, -2]) cube([60, 60, 60]); }

petg() intersection() { designA_petg(); half_cube_Z(); }
tpu()  intersection() { designA_tpu();  half_cube_Z(); }
