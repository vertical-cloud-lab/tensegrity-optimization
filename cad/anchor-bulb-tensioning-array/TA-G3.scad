// =============================================================================
// TA-G3 — Axis A (air-gap) specimen: 0.3 mm radial clearance
//          (bore Ø = 3.0 mm vs. 2.4 mm cable)
// Hypothesis: a thin air film between PLA bore wall and TPU cable is enough
// to break the layer-to-layer fusion that would otherwise weld them, so the
// cable can be pulled through under finite force. Sweep 0.3 mm to find the
// minimum gap that yields tractable pull-through without losing axial alignment.
// =============================================================================
include <_common.scad>
specimen_A1(id = "TA-G3", gap_r = 0.3, pause_z = 0, sleeve_t = 0);
