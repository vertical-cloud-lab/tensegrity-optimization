// =============================================================================
// TA-R0 — Axis C (release sleeve) specimen: 0.2 mm PVA sleeve in the bore
// Hypothesis: a sacrificial water-soluble sleeve (PVA / BVOH) printed via the
// AMS Pro 3rd nozzle as an annulus between the PLA bore wall and the TPU
// cable gives a clean pre-tension release after a brief water soak. The TPU
// cable extruder is dedicated, so PVA must come from a separate AMS slot.
// Sweep 0.2 mm wall to find the thinnest sleeve that still gives clean
// release without leaving the cable rattling in an oversized bore.
// =============================================================================
include <_common.scad>
specimen_A1(id = "TA-R0", gap_r = 0.0, pause_z = 0, sleeve_t = 0.2);
