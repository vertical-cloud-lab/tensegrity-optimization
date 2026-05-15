// =============================================================================
// Full tensioning test array — 15 A3-countersunk specimens (3 node sizes
// × 5 air gaps) on a single build plate, oriented for horizontal-cable
// printing.
//
// Layout: rows = node size (Y axis), columns = air gap (X axis).
//   Row Y- : node Ø  7.5 mm — H-S0G0 H-S0G1 H-S0G2 H-S0G3 H-S0G4
//   Row Y0 : node Ø  9.5 mm — H-S1G0 H-S1G1 H-S1G2 H-S1G3 H-S1G4
//   Row Y+ : node Ø 12.0 mm — H-S2G0 H-S2G1 H-S2G2 H-S2G3 H-S2G4
//
// All specimens share the cable orientation (+Y) so cables emerge from
// neighbouring rows on the same side of the plate — easier to clamp the
// row's worth of pull handles in a single jig if desired.
// =============================================================================
include <_common.scad>

pitch_x = 22;   // X spacing between gap columns
pitch_y = 60;   // Y spacing between size rows (room for cable handle + entry tail)

sizes      = [7.5, 9.5, 12.0];
size_lbls  = ["S0", "S1", "S2"];
gaps       = [0.1, 0.2, 0.3, 0.4, 0.6];
gap_lbls   = ["G0", "G1", "G2", "G3", "G4"];

for (si = [0:2]) {
    for (gi = [0:4]) {
        translate([(gi - 2) * pitch_x, (si - 1) * pitch_y, 0])
            specimen_A3(
                id     = str("H-", size_lbls[si], gap_lbls[gi]),
                node_d = sizes[si],
                gap_r  = gaps[gi]
            );
    }
}
