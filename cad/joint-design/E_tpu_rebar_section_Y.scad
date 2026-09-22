// Section view of Design E — TPU rebar embedded in PETG strut tip, cut at
// Y=0 (keep -Y half), color preserved by per-part intersection.
include <_common.scad>
use <E_tpu_rebar.scad>

module half_cube_negY() { translate([-30, -30, -40]) cube([60, 30, 60]); }

petg() intersection() { designE_petg(); half_cube_negY(); }
tpu()  intersection() { designE_tpu();  half_cube_negY(); }
