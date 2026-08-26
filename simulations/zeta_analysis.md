# Ringdown damping (`zeta_pct`): measured signal, and what the simulation can resolve

Script: [`zeta_analysis.py`](zeta_analysis.py). Outputs:
`outputs/zeta_measured_correlations.csv`, `outputs/zeta_articles_sim.csv`,
`outputs/zeta_damping_transfer.csv`, `outputs/zeta_sobol_response.csv`,
`outputs/zeta_article_inversion.csv`, `outputs/zeta_cross_checks.csv`,
`outputs/zeta_analysis.png`.

Context: `zeta_pct` (the article's modal damping ratio, fit to the
post-impact ringdown of the top vertex) was proposed as a replacement second
objective for `e_reb_mJ`. Two follow-up questions from PR #33 discussion
(2026-08-24): what does the measured `zeta_pct` actually correlate with, and
how well can the drop-tower analogue (`drop_tower_sim.py`) resolve it?

## 1. The measured channel

Across the batch (7 articles with a ζ, 6 of them design-mapped):
`zeta_pct` spans 6.4 to 31.0 % (4.9x), with within-article sd 0.66 to 2.36
(so the between-article spread is roughly 7.5x the pooled repeat noise).
Nothing reaches significance against it at this n
(`zeta_measured_correlations.csv`):

| observable | n | Spearman rho | p |
|---|--:|--:|--:|
| `fn_hz` | 7 | -0.61 | 0.15 |
| `R_mm` | 6 | -0.54 | 0.27 |
| `cable_d_mm` | 6 | +0.31 | 0.54 |
| `t180` | 7 | +0.07 | 0.88 |

Two readings. First, the strongest (still insignificant) partner is the
ringdown frequency itself, negatively: the softer-ringing articles damp
more, which is what a lossy-material mode family would do. Second, the
near-zero correlation with `t180` is the property that made ζ attractive as
a second objective, and it survives this closer look.

**On degradation.** The working hypothesis (PR #33, 2026-08-24) is that
there is no article degradation under current conditions, and that
differences across repeated drops come from the repeated, mostly elastic
compression of the PU mat. The committed summary CSV cannot test drop-order
drift (it carries means and sds, not the per-drop sequence), so this
analysis neither supports nor contradicts the hypothesis; what it can say
is that the within-article ζ scatter (CV 6 to 22 %) is the largest of any
channel, consistent with fit-window sensitivity of a ringdown fit rather
than any monotone article change, and that the three `dv_health = settled`
flags are the mat/seating story's expected signature. A direct test needs
the per-drop streams: regress each channel on drop index within an article,
which is a PR #102-side ingest task, not a simulation one. Note the
simulation embodies the hypothesis by construction: its Hunt-Crossley mat
is stateless, so simulated repeat drops are bit-identical.

## 2. How the simulated ringdown is extracted

`drop_tower_sim.simulate` now returns the **raw** (unfiltered) acceleration
channels and takes `cable_zeta` (the tendon material-damping dial, formerly
hard-coded at 0.02) and `duration_s`. The extraction
(`zeta_analysis.simulate_ringdown`):

* run the drop with a 0.20 s window; after the mat releases the carriage
  (~8 ms) everything is ballistic for ~0.6 s, so the tail is clean free
  vibration with only the article's own dampers active;
* fit the relative acceleration `a_top - a_ch5` on the raw traces. This
  matters: the CFC-180 corner sits at ~300 Hz, on top of the measured 294
  to 468 Hz band, so filtered traces cannot carry a ringdown fit;
* bench-style modal fit: dominant FFT line, zero-phase band-pass (0.5x to
  2x the line), trim filter edges and the decayed tail, then a damped
  cosine `A exp(-s t) cos(2 pi f t + phi)`;
  `zeta = s / sqrt(s^2 + (2 pi f)^2)`. Fit R^2 is 0.7 to 0.95 on the
  articles, and the in-band energy fraction is reported so multi-modal
  decays are visible.

## 3. Results: the simulation cannot resolve `zeta_pct`

Four independent failures, each visible in `zeta_analysis.png`:

1. **Wrong mode family.** Simulated ringdown frequencies are 22 to 96 Hz
   (rigid-strut bodies swinging on the tendon network); measured are 294 to
   468 Hz, which the `drop_tower_sim` docstring already attributes to strut
   flexure. The two clouds in panel (d) do not overlap. A rigid-strut model
   has no strut bending modes, so the thing the bench ringdown fit measures
   does not exist in the model.
2. **No cross-article signal.** At the fixed `cable_zeta = 0.02`,
   Spearman(sim ζ, measured ζ) = **-0.54** (n = 6, p = 0.27) and
   Spearman(sim fn, measured fn) = -0.37. The sign is wrong and the n is
   small: read it as zero signal, not anti-signal.
3. **A damping floor above two of the articles.** Sweeping the material
   dial on the S0 design (`zeta_damping_transfer.csv`): below
   `cable_zeta ~ 0.05` the emergent modal ζ pins at ~12 %, independent of
   the dial. That floor comes from everything else that dissipates in the
   model (equality-constraint stabilization, the implicitfast integrator,
   energy leaking between modes), and it sits **above** the measured autv5r
   (6.4 %) and at 6lhxfy (10.1 %): the least-damped articles are not
   representable at any dial setting. Above ~0.2 the transfer goes
   non-monotone (the mode being fit changes), so the top of the measured
   band is reachable only ambiguously; the per-article inversion
   (`zeta_article_inversion.csv`) converges for 4 of 6 articles and fails
   at both ends (autv5r below the floor, nvxsrv above the usable range).
4. **Design response is scatter, not physics.** Across 48 Sobol designs at
   the fixed dial, sim ζ spans 7 to 79 %, but no design axis explains it
   (max |rho| = 0.21, `strut_d_mm`): which rigid-body mode dominates the
   top-vertex decay changes chaotically with geometry. A huge span with no
   coherent driver is mode-structure noise, not a resolvable design effect.

**And the injection idea does not propagate.** The earlier recommendation
(fit ζ(design) from the measured ringdown and put it in the tendons) was
tested directly: setting each article's `cable_zeta` so the simulated modal
ζ matches its measured `zeta_pct` changes simulated `t180` by a median
0.12 % (max 3.9 %) and simulated `e_rebound` by a median 0.009 % (max
0.12 %) (`zeta_cross_checks.csv`). The mat owns the loss budget in this
model, so no amount of article-damping tuning moves the objectives at
Tier C. That closes the cheapest branch of the "make simulated rebound
design-responsive" plan: it is not a calibration problem, it is a
missing-mechanism problem.

## 4. Verdict and what it would take

Tier C cannot resolve `zeta_pct`, for structural reasons rather than
tuning reasons: the measured mode family (strut flexure at 294 to 468 Hz)
does not exist with rigid struts, the model's own parasitic dissipation
floors the emergent ζ above the best articles, and tendon damping is
decoupled from both campaign objectives because the calibrated mat carries
essentially all of the loss.

To make ζ a simulated observable, the article needs *bending* and a
*lossy material*, together:

1. **Tier B (Newton/Warp)**: discretize each strut as a chain of particles
   with bending stiffness (or use rigid segments + rotational springs), and
   give the TPU tendons Kelvin-Voigt damping fit per-shore-hardness rather
   than per-article. This is the cheapest route to a 300+ Hz flexural mode.
2. **Tier A (PolyFEM)**: viscoelastic material models (Prony series for
   TPU, and PLA's own loss factor) make ζ a genuine material-and-geometry
   output. Expensive, but it is the same upgrade already flagged for the
   missing `t180 > 1` amplification, so one tier promotion serves all
   three dead observables (amplification, rebound, ringdown damping).

Until then the standing recommendation from the objective discussion holds:
`zeta_pct` is a **bench-only** channel. It is article-intrinsic, repeatable,
and independent of `t180`, so it works as a second objective on the bench,
but no current simulation tier can supply a prior for it.

Reproduce:

```bash
python simulations/zeta_analysis.py --n-sobol 48
```
