// Design F — section cut at Z=0 (equator). Top-down view that most clearly
// shows the staggered PETG/TPU interlock teeth meshing radially in the
// print-in-place gap between shell ID and core OD.
include <_common.scad>
use <F_captive_core.scad>

difference() {
    designF();
    translate([-50, -50, 0]) cube([100, 100, 50]);
}
