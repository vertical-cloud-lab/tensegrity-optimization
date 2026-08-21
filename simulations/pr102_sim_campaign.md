# The T-3_01 campaign in simulation: matching PR #102, and what correlates

PR #102 runs a two-objective SAASBO campaign whose objective function is a
print plus a 101-drop session on the Lansmont M23. This note is the
simulation-side counterpart: the same search space, the same two objectives,
the same batch size and generation strategy, with `drop_tower_sim` in place
of the drop tower, plus the thing that decides whether any of it is useful --
a correlation study of every simulated observable in this directory against
the eight articles that were actually tested.

Files:

| file | what it does |
|---|---|
| [`print_infill.py`](print_infill.py) | sub-100 % PLA infill: printed mass, effective strut density and modulus, the PR #35 constant-mass projection |
| [`drop_tower_sim.py`](drop_tower_sim.py) | MuJoCo analogue of the 60 in / PU-mat drop; returns `t180` and `e_reb_mJ` |
| [`pr102_correlation.py`](pr102_correlation.py) | scores the tested articles with every candidate observable and rank-correlates against the measured objectives |
| [`pr102_sim_campaign.py`](pr102_sim_campaign.py) | the closed-loop simulation-only campaign, one run per seed |
| [`workflows-staged/sim-bo-pr102-matrix.yml`](workflows-staged/sim-bo-pr102-matrix.yml) | parallel seed matrix for Actions (staged; move it into `.github/workflows/`) |
| `data/pr102/*.csv` | snapshots of PR #102's batch table, print key and campaign summary |

## 1. Sub-100 % PLA infill

The articles are not solid. PR #86 section 7 regressed the weighed articles
on their per-material solid masses and found the PLA prints at about 57 % of
solid density and the TPU at about 99 %. `print_infill.fit_solidity()`
re-derives that from the committed CSVs and gets 0.556 / 0.995 (n = 9,
R^2 = 0.66), so the constants in the module are the published 0.565 / 0.986
and the refit agrees.

Two consequences are wired into the simulator:

* **Strut density.** `effective_pla_density_kgm3()` = 700.6 kg/m^3 instead of
  1240. Every strut capsule in `drop_tower_sim` is built at that density, so
  the article's inertia -- the thing that sets a base-excited structure's
  transmissibility -- matches the scale.
* **Effective modulus.** `effective_pla_modulus_MPa()` applies the
  Gibson-Ashby scaling `E_eff/E_s = phi^n`. The bracket is 1980 MPa (n = 1,
  stretch-dominated) to 1117 MPa (n = 2, bending-dominated), 1486 MPa at the
  n = 1.5 default. Tier C treats struts as rigid so only the mass channel
  bites here; the modulus is for the tiers that let the strut deform.

A second correction was needed before the masses came out right. The
idealized volume model used elsewhere in this directory (three capsules plus
nine cylinders at the vertical-cable length) is not the printed CAD, which
also carries PLA joints, housings and the modeled-in scaffold. Regressing
the batch table's reference-STL per-material masses on the model volumes
gives one factor per material, 1.68 for PLA and 0.68 for TPU, with 9 % and
6 % scatter across the nine designs. With both corrections in place the
predicted as-printed masses land within 0.7 g mean absolute error of the
scale readings across the batch (18.8 to 22.6 g predicted, 18.5 to 22.3 g
measured), and the constant-mass projection reproduces the batch table's own
`scale` column to about 2 %.

That projection matters on its own: the campaign's search space is the
*base* Sobol coordinates, and PR #35 prints the uniform rescale of them that
hits a fixed solid-CAD mass. Across the batch the scale runs 0.74 to 1.08,
so simulating the base coordinates would simulate an article up to a quarter
of a size away from the one on the bench. `evaluate_pr102` projects first.

## 2. The drop-tower analogue

Channel roles are from PR #67's input-output series: CH5 is a single-axis
sensor on the bottom acrylic plate (input), the tri-axis is hot-glued to the
top vertex (output), and `t180` is the ratio of their CFC-180 peaks. The
model is a carriage on a vertical slide joint (the tower's rails) carrying
the CH5 site, an explicit one-sided Hunt-Crossley PU mat, and the article
with its three bottom vertices ball-anchored to the carriage, nine TPU
tendons at the `printable_design` axial stiffness, and a 5 g accelerometer
mass on the measured top vertex.

`e_rebound` in the campaign summary is a restitution *velocity* ratio, not
an energy fraction: `t_second = 2 * e_rebound * v_in / g` reproduces every
specimen's second-impact time to three digits. The simulation therefore
reads it off the carriage's post-contact velocity, and `e_reb_mJ` is formed
exactly as PR #102 forms it, `e_rebound * m_printed * g * 1.524 m`.

**What the mat is calibrated on, and what it is not.** `--calibrate` fits
the two mat parameters to the measured input pulse: peak 208.4 G against a
measured 208.2 G, width 4.08 ms against the 4.08 ms implied by the measured
peak and delta-v. It is deliberately *not* fitted to the measured
restitution. A mat lossy enough to return only 2 % of the impact velocity in
this model peaks near 300 G, well above what the tower measures, because the
energy the rig actually loses leaves through paths the model does not carry
(guide rails, anvil and frame, the mount). Simulated `e_rebound` therefore
comes out around 0.6 against a measured 0.02 to 0.05, and is treated as a
rank proxy, not a prediction.

The same honesty applies to `t180` itself: the simulated S0 article reads
0.707 against a measured 1.011. Rigid struts have no bending modes, so the
model has no mechanism for the *amplification* every tested article except
`6lhxfy` shows. It can only attenuate. Absolute agreement was never
available at this tier; rank agreement is the question, and section 3
answers it.

## 3. Which simulated observable tracks the measured objectives

`pr102_correlation.py` scores the seven articles that have both a design
mapping and a weighed mass (`amdjwm` maps to no known print, so PR #102
skips it and so do we) with every candidate observable this thread has
produced, then rank-correlates against the two measured objectives.

At n = 7, Spearman needs |rho| >= 0.79 for p = 0.05 two-sided, and about 30
observables are screened, so read the table with the multiplicity in mind:
the leader clears Bonferroni, the rest of the top block does not.

**Measured `t180`.** `rel_span` is the observable's range over its mean
across the seven articles, and it is not decoration: it separates a real
design effect from a rank that rides on numerical structure.

| simulated observable | Spearman rho | p | rel_span |
|---|--:|--:|--:|
| `lander_eta` (compaction efficiency, lander regime) | **-0.96** | 0.0005 | **0.0013** |
| `lander_SEA_J_per_cm3` | **-0.93** | 0.003 | 2.38 |
| `crutch_SEA_J_per_cm3` | -0.89 | 0.007 | 1.86 |
| `lander_SEA_J_per_g` | -0.89 | 0.007 | 2.93 |
| `crutch_SEA_J_per_g` | -0.86 | 0.014 | 1.99 |
| `H_mm` (a design coordinate, for scale) | +0.79 | 0.036 | 0.47 |
| `sim_t180` (the drop-tower analogue itself) | +0.46 | 0.29 | 0.33 |
| `sim_in_180_g` | 0.00 | 1.00 | 0.001 |

**Measured `e_reb_mJ`:** nothing clears p = 0.05. The best are `R_mm`
(+0.71, p = 0.07), `sim_e_rebound` (-0.64, p = 0.12) and `sim_t180` (-0.57,
p = 0.18).

Three readings, in order of how much they should change what we do:

1. **The purpose-built analogue is not the best predictor; the incidental
   Tier-C observables are.** `sim_t180` lands at rho = +0.46 (p = 0.29)
   while the Tier-C observables built for the crutch and lander regimes --
   a completely different question -- rank the bench articles at -0.86 to
   -0.96. The sign is the physical part: articles whose simulated pulse is
   flatter and whose stored elastic energy per unit volume is higher are the
   articles that measured *lower* transmissibility.
   **The one worth attaching to the campaign GP is `SEA_J_per_cm3`**
   (rho = -0.93 for the lander regime, -0.89 for the crutch), not
   `lander_eta` despite its higher rho: eta moves 0.13 percent across the
   seven articles (0.7326 to 0.7334) while the volumetric SEA moves 240
   percent. A perfect ranking over a 0.1 percent span is a ranking of
   numerical structure until a perturbation study says otherwise, and the
   earlier Edison reviews in this thread already flagged Tier-C `eta` as a
   pinned observable. Take `lander_eta` as a lead to test, and
   `SEA_J_per_cm3` as the prior to use.
2. **The rebound objective has no simulated predictor yet.** Every candidate
   fails at n = 7. Given that the mat calibration explicitly gave up on
   restitution, this is the expected result rather than a surprising one,
   and it means `e_reb_mJ` should be modeled from bench data alone until a
   tier that carries the rig's loss paths exists.
3. **`sim_in_180_g` is rho = 0.00 by construction and that is a good sign.**
   The input peak is the rig, not the design; a calibrated mat should give
   the same input to every article, and it does. It is the null control for
   the rest of the table.

The infill correction is visible but not decisive at this n: `sim_solid_t180`
(the same model run at solid PLA density) correlates identically at rho =
+0.46 for `t180` but moves from -0.57 to -0.43 for `e_reb_mJ`. Where it
matters unambiguously is the mass channel, which is what `e_reb_mJ` is built
from: solid density puts every article's mass out by a factor 1.7, so the
objective it feeds is wrong by that factor before any physics happens.

## 4. The closed-loop simulation-only campaign

`pr102_sim_campaign.py` mirrors PR #102's structure: the nine printed
articles are attached as completed trials (scored in simulation), then the
loop proposes 9 more per round. Objectives, search space, batch size and the
`mass_g` tracking metric are identical; the generation strategy defaults to
the same SAASBO step.

Repeat seeds are the point of running it in simulation, and they are what
the staged workflow parallelizes. Each matrix leg is one seed, which is
worth doing because SAASBO's per-round NUTS fit, not the 0.3 s simulation,
is the wall-clock.

Three seeds were run in-session (`--model botorch`, 3 rounds of 9 after the
printed batch, 36 simulated designs each):

| seed | final hypervolume | best `t180` | best `e_reb_mJ` |
|---|--:|--:|--:|
| 0 | 17.79 | 0.4869 | 170.05 |
| 1 | 17.59 | 0.4942 | 170.04 |
| 2 | 17.59 | 0.4945 | 170.01 |

The nine printed articles score `t180` 0.584 to 0.827 in simulation, so the
loop improves on the best of them by about 17 % and the three seeds agree to
under 2 %. All three walk to the same corner of the box: `R` at its maximum
40 mm, `H` at its minimum 60 mm, `twist` at its minimum 40 deg and `cable_d`
at its minimum 3.0 mm, with `strut_d` the only loose axis (6.6 to 8.0 mm).
Short, wide, thin-cabled.

Two things to notice before reading that as a recommendation. It agrees with
the measured campaign on thin cables -- `6lhxfy`, the one article that
genuinely attenuated on the bench, is the thin-cable corner -- and disagrees
on twist, where `6lhxfy` sits at the box maximum. And unlike the
regime sims, this model *does* consume the twist axis (the geometry is built
at the supplied twist), so a twist result here is a physical claim rather
than the un-consumed plumbing `sobol_t3_diagnostics.md` documents for
`run_regimes`. Given that the model cannot amplify at all (section 2), the
disagreement is more likely the model's than the bench's.

One SAASBO seed was also run to check that path (the default, matching
PR #102): one round of 3 designs took 570 s on a contended runner core
against 0.3 s per simulation, which is exactly why the staged workflow
parallelizes over seeds rather than running them in series.

Per-seed convergence and objective-space plots are in
`outputs/pr102_sim_bo_botorch_seed*.png`, the cross-seed mean with a
+/- 1 sd band is `outputs/pr102_sim_bo_botorch_aggregate.png`, and the
per-seed trial tables are the matching CSVs.

## 5. Caveats

* Seven articles. Every correlation in section 3 is a small-n rank
  statistic screened across about 30 candidates; treat the leader as a
  hypothesis to test on the next batch, not as an established transfer
  function.
* `lander_eta`'s 0.13 percent span has not been perturbation-tested (vary
  the timestep, the prestrain, the payload mass, and see whether the ranking
  survives). That test is the first thing to run before anyone leans on it.
* The simulated `t180` cannot exceed 1 by much: rigid struts cannot
  resonate, so the amplifying articles have no mechanism in this model.
  Tier B (Newton) or Tier A (PolyFEM) is where that would come from.
* Simulated `e_rebound` is a rank proxy at roughly 20x the measured value,
  for the reason given in section 2.
* The infill solidity is one effective scalar per material, absorbing wall
  count, infill density and pattern. The exact per-profile answer would come
  from the BambuStudio CLI's sliced per-filament grams, as PR #86 section 7
  notes.
* `amdjwm` is excluded (no design mapping). If it is identified, both the
  correlation study and PR #102's ingest gain a point, and it is the
  second-best measured article, so it matters.
