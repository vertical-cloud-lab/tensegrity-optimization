// Design F — section cut at X=0 (perpendicular to cable). Reveals the ring
// of layer-interlock teeth (PETG inward + TPU outward) at the equator and
// the radial print-in-place clearance between core and shell.
include <_common.scad>
use <F_captive_core.scad>

difference() {
    designF();
    translate([0, -50, -50]) cube([50, 100, 100]);
}
