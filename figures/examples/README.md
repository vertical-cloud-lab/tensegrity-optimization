# Example figures (mock-ups, not manuscript content)

Standalone illustrative figures explored as side-tasks. They are **not** wired into
the manuscript build and use **synthetic** data unless stated otherwise.

## `mechanistic-data-figure-example.{png,pdf}`

A worked example (PR review comment 4664748222) of the kind of *mechanism-oriented*
data figure the manuscript currently lacks: processed drop-test deceleration curves
annotated with callouts that link the measured signal to the specific structural
features being exercised. Intended as a template/discussion piece, not a result.
Revised per Edison ANALYSIS feedback (task `e0c4e062-15c7-4a62-b931-1746211fe8b1`,
folded back via PR comment 4664958219).

What this figure contains:

- **(a) Processed response** — rigid control vs. tensegrity, SAE J211 **CFC-180**
  filtered, with the raw 125 kHz tensegrity trace shown faintly to motivate filtering;
  a peak-reduction callout; **event-based phase** shading (i first contact, ii strut
  rotation + cable redistribution, iii peak compression plateau, iv rebound/unloading,
  keyed via an off-curve legend); ±1 s.d. replicate bands; and three numbered markers
  (1 contact, 2 plateau, 3 rebound) that key the frames at right.
- **(a2) Cumulative-impulse subpanel** — sharing panel (a)'s x-axis, showing that the
  control and tensegrity traces transfer the **same mass-normalized Δv** (impulse
  consistency), so the lower tensegrity peak comes from spreading the same impulse over
  time rather than from inconsistent loading.
- **(b)–(d) Synchronized frames** — T3 prism schematics at the three marker times (with
  timestamps), red PLA struts (compression) and blue TPU cables (tension). In the real
  article these are replaced by high-speed-camera / DIC stills registered to the curve.
- **(e) Joint callout** — the cables anchoring *inside* the strut end (the strut acting
  as a rigid cage with discrete cable outlets), i.e. the load path responsible for
  flattening the peak.

The curves are **synthetic**: the control is anchored to the documented control
CFC-180 peak (~1792 G, impact ~4.2 ms) and the tensegrity shoulder is then scaled to
the *same impulse*, so its peak (~403 G ⇒ ~78 % reduction, within the documented
~370–463 G / 74–79 % range) and the matched Δv are *outputs* of the conservation
constraint, not arbitrary inputs. The filtering, alignment, and replicate basis live
in the figure caption; a visible watermark marks the mock-up. Optionally uses SciPy
for cumulative integration (falls back to a NumPy trapezoid if SciPy is absent).

Regenerate:

```sh
python scripts/figures/mechanistic_data_figure_example.py
```

## `ax-{loocv,sensitivity,convergence,pareto}-example.{png,pdf}`

Drop-in example fills (PR review comment 4673509625) for the four **empty**
data-figure slots in `manuscript/manuscript-body.tex` that are currently rendered
as blank boxes via `\figplaceholder`:

| slot (`\label`)     | example file                  | shows |
|---------------------|-------------------------------|-------|
| `fig:loocv`         | `ax-loocv-example`            | leave-one-out cross-validation of the GP surrogate (predicted vs. observed SEA and peak force, with model error bars and $R^2_{\rm LOO}$) |
| `fig:sensitivity`   | `ax-sensitivity-example`     | parameter-sensitivity ranking (model length-scale-based importances per objective) |
| `fig:convergence`   | `ax-convergence-example`     | best-so-far SEA vs. number of experiments, BO vs. an independent random-search baseline, Sobol-init region shaded |
| `fig:pareto`        | `ax-pareto-example`          | Pareto front in (peak transmitted force, SEA) space with all evaluated designs |

Unlike the mechanistic example above, these are produced by a **real Ax
Bayesian-optimization loop** (Sobol initialization + BoTorch model-based trials,
the SAASBO/qNEHVI-style machinery the manuscript describes) over a
tensegrity-flavoured search space (strut diameter, twist, pretension, and the
categorical cable diameter $\in\{1.2,1.8,2.4,3.0,4.5\}$ mm). Only the **objective
values are synthetic** — produced by a closed-form surrogate in `evaluate()`, not
from any experimental file — so the diagnostics are genuine Ax/BoTorch output on
dummy outcomes. Every panel carries an "ILLUSTRATIVE EXAMPLE — synthetic data"
watermark. Replace `evaluate()` with real measured outcomes before any of these
is used as a result. `ax-placeholder-figures-contact-sheet.png` is a 2×2 preview.

Requires `ax-platform` (pulls in `botorch`/`torch`). Regenerate:

```sh
python scripts/figures/ax_placeholder_figures_example.py
```
