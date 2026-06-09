# Example figures (mock-ups, not manuscript content)

Standalone illustrative figures explored as side-tasks. They are **not** wired into
the manuscript build and use **synthetic** data unless stated otherwise.

## `mechanistic-data-figure-example.{png,pdf}`

A worked example (PR review comment 4664748222) of the kind of *mechanism-oriented*
data figure the manuscript currently lacks: processed drop-test deceleration curves
annotated with callouts that link the measured signal to the specific structural
features being exercised. Intended as a template/discussion piece, not a result.

What such a figure would contain:

- **(a) Processed response** — rigid control vs. tensegrity, SAE J211 **CFC-180**
  filtered, with the raw 125 kHz tensegrity trace shown faintly to motivate filtering;
  a peak-reduction callout; and shaded **mechanistic phases** A (contact / cable
  pre-tension), B (strut+cable load redistribution — the energy plateau), C (rebound).
- **(b) Specimen callout** — T3 prism schematic, red PLA struts (compression) and blue
  TPU cables (tension), with the detailed strut end circled.
- **(c) Joint callout** — the cables anchoring *inside* the strut end (the strut acting
  as a rigid cage with discrete cable outlets), i.e. the load path responsible for
  flattening the peak.
- **(d) Deformation snapshot** — specimen at the phase-B plateau.

In the real article each schematic callout would be replaced by a high-speed-camera
frame or specimen photograph registered to the corresponding point on the curve.

The curves are **synthetic**, generated from the documented qualitative behaviour of
the real campaign (issue #36: impact at ~4.2 ms, control CFC-180 peak ~1792 G,
tensegrity ~370–463 G ⇒ ~74–79 % reduction). A visible watermark marks the mock-up.

Regenerate:

```sh
python scripts/figures/mechanistic_data_figure_example.py
```
