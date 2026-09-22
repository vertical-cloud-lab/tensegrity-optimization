// Section view (cut at Y=0) for variant A4_lobed. Keep -Y half so the camera
// at -Y sees the cut face. Apply intersection per-color part so the
// PETG/TPU colours survive the CSG operation.
include <_common_variants.scad>
use <A4_lobed.scad>

module half_cube_negY() { translate([-30, -30, -40]) cube([60, 30, 60]); }

petg() intersection() { designA4_petg(); half_cube_negY(); }
tpu()  intersection() { designA4_tpu();  half_cube_negY(); }
