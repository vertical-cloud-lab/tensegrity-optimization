// Section view (cut at Y=0) for variant A3_countersunk. Keep -Y half so the camera
// at -Y sees the cut face. Apply intersection per-color part so the
// PETG/TPU colours survive the CSG operation.
include <_common_variants.scad>
use <A3_countersunk.scad>

module half_cube_negY() { translate([-30, -30, -40]) cube([60, 30, 60]); }

petg() intersection() { designA3_petg(); half_cube_negY(); }
tpu()  intersection() { designA3_tpu();  half_cube_negY(); }
