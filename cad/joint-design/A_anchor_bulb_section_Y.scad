// Section view of Design A — anchor-bulb spherical node cut at Y=0 (keep
// -Y half so the camera at -Y sees the cut face). Apply intersection
// per-color part so PETG/TPU colors survive the CSG operation.
include <_common.scad>
use <A_anchor_bulb.scad>

module half_cube_negY() { translate([-30, -30, -40]) cube([60, 30, 60]); }

petg() intersection() { designA_petg(); half_cube_negY(); }
tpu()  intersection() { designA_tpu();  half_cube_negY(); }
