// =============================================================================
// Full tensioning test array — all 12 specimens on a single build plate.
//
// Layout: 3 rows x 4 columns, 35 mm pitch in X and 20 mm pitch in Y.
//   Row Y- : Axis A (air gap)        — TA-G0  TA-G1  TA-G2  TA-G3
//   Row Y0 : Axis A continued + B    — TA-G4  TA-G5  TA-L0  TA-L1
//   Row Y+ : Axis B + Axis C         — TA-L2  TA-R0  TA-R1  TA-R2
//
// A single multi-material print of this plate yields one specimen of every
// candidate interface treatment.  After the print, soak the PVA-sleeve row
// (TA-R0..TA-R2) in tap water for 30-60 min, then pull-test every specimen
// with a hand-held force gauge gripping the TPU pull handle above the
// frustum and the PLA tab clamped in a vise (see README.md).
// =============================================================================
include <_common.scad>

pitch_x = 35;
pitch_y = 20;

// Axis A (air gap) — 6 specimens at 0.0 .. 0.6 mm radial
axisA_gaps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.6];

// Axis B (pause+lubricate) — 3 specimens at lower / mid / upper bore
axisB_pause = [18.5, 20.75, 25.0];

// Axis C (sacrificial sleeve) — 3 specimens at 0.2 / 0.4 / 0.6 mm wall
axisC_sleeve = [0.2, 0.4, 0.6];

// Render rows --------------------------------------------------------------
// Row 1 (Y = -pitch_y): TA-G0 .. TA-G3
for (i = [0:3])
    translate([(i - 1.5) * pitch_x, -pitch_y, 0])
        specimen_A1(id = str("TA-G", i),
                    gap_r = axisA_gaps[i], pause_z = 0, sleeve_t = 0);

// Row 2 (Y = 0): TA-G4, TA-G5, TA-L0, TA-L1
translate([-1.5 * pitch_x, 0, 0])
    specimen_A1(id = "TA-G4", gap_r = axisA_gaps[4], pause_z = 0,            sleeve_t = 0);
translate([-0.5 * pitch_x, 0, 0])
    specimen_A1(id = "TA-G5", gap_r = axisA_gaps[5], pause_z = 0,            sleeve_t = 0);
translate([ 0.5 * pitch_x, 0, 0])
    specimen_A1(id = "TA-L0", gap_r = 0.2,           pause_z = axisB_pause[0], sleeve_t = 0);
translate([ 1.5 * pitch_x, 0, 0])
    specimen_A1(id = "TA-L1", gap_r = 0.2,           pause_z = axisB_pause[1], sleeve_t = 0);

// Row 3 (Y = +pitch_y): TA-L2, TA-R0, TA-R1, TA-R2
translate([-1.5 * pitch_x,  pitch_y, 0])
    specimen_A1(id = "TA-L2", gap_r = 0.2, pause_z = axisB_pause[2], sleeve_t = 0);
translate([-0.5 * pitch_x,  pitch_y, 0])
    specimen_A1(id = "TA-R0", gap_r = 0.0, pause_z = 0, sleeve_t = axisC_sleeve[0]);
translate([ 0.5 * pitch_x,  pitch_y, 0])
    specimen_A1(id = "TA-R1", gap_r = 0.0, pause_z = 0, sleeve_t = axisC_sleeve[1]);
translate([ 1.5 * pitch_x,  pitch_y, 0])
    specimen_A1(id = "TA-R2", gap_r = 0.0, pause_z = 0, sleeve_t = axisC_sleeve[2]);
