// Section view of Design C — sleeve overmold cut at Y=0 (keep -Y half),
// color preserved by per-part intersection.
include <_common.scad>
use <C_tpu_sleeve_overmold.scad>

module half_cube_negY() { translate([-30, -30, -40]) cube([60, 30, 60]); }

petg() intersection() { designC_petg(); half_cube_negY(); }
tpu()  intersection() { designC_tpu();  half_cube_negY(); }
