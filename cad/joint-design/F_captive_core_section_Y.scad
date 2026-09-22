// Design F — section cut at Y=0 (slot/cable plane). Reveals the captive TPU
// core inside the PETG/PLA shell, the teardrop strut/shell fillet, and the
// cable exit bore on +X.
include <_common.scad>
use <F_captive_core.scad>

difference() {
    designF();
    // remove everything in +Y so we see the X-Z plane interior
    translate([-50, 0, -50]) cube([100, 50, 100]);
}
