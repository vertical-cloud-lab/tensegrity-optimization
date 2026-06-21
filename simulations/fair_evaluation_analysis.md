# Making the objective evaluations *fair* (mass, volume, contact area)

Addresses PR comment **4760939061**:

> Not sure to what extent any of these are "fair" tasks. I.e., primarily in terms
> of mass, volume, and contact area. Suggest ways to make these evaluations for
> the different objectives fair, especially for the lander problem. I.e., what are
> the actual design constraints for a scaled-up lander module? How would those be
> relaxed in the campaign here? Would we normalize the objectives ad-hoc or change
> the way the search space is represented so that certain constraints are always
> met? E.g., constant mass, fixed contact area, volume, etc.

This is a *thinking* document. It states the problem precisely, quantifies how
unfair the current campaign is, lays out the real lander-module constraints, and
proposes concrete fixes — both the ad-hoc objective-normalisation route and the
search-space-reparameterisation route — with a recommendation. It is the brief
we sent to Edison ANALYSIS for mock feedback
(`edison-trajectories/fair-evaluation/`).

---

## 1. Why the current evaluations are *not* a fair comparison

The Sobol / Pareto / BO campaigns (`pareto_render_campaign.py`,
`sobol_t3_campaign.py`, `sim_bo_campaign.py`) all draw designs from the same
PR #35 box and score them with `bo_evaluator.evaluate_design`:

| axis        | range          |
|-------------|----------------|
| `R_mm`      | 25 – 40        |
| `H_mm`      | 60 – 110       |
| `twist_deg` | 40 – 80        |
| `strut_d_mm`| 6 – 12         |
| `cable_d_mm`| 3.0 – 5.5      |

The problem is that **every corner of that box is a physically different-sized
object.** Sweeping the corners (at the equilibrium twist, prestrain 0) gives:

| derived quantity                                   | min   | max   | spread |
|----------------------------------------------------|------:|------:|-------:|
| cell mass (3 PLA struts + 9 TPU tendons)           | 9.5 g | 59.2 g| **6.2×** |
| circumscribing envelope volume (`π R² H`)          | 118 cm³| 553 cm³| **4.7×** |
| strut-tip footprint area (3 × `π (d/2)²`)          | 85 mm²| 339 mm²| **4.0×** |

So when the campaign reports that *"fat, short, large-radius cells win on SEA"*
(`pareto_render_campaign.md`), it is partly reporting a tautology: those cells
have up to 6× more material, 5× more volume, and 4× more contact area. The
optimiser is free to "win" by simply **building a bigger, heavier part**, which
is not a design insight and — for the lander especially — is not even allowed.

Look at each objective through that lens:

* **`SEA_J_per_g`** *is* mass-normalised by construction
  (`sea = strain_energy · payload_mass / cell_mass`,
  `bo_evaluator.py:362`). So SEA is the *one* objective that is already fair on
  mass. But it is **not** normalised on volume or footprint, and its numerator
  is a *peak elastic strain-energy proxy* (orders of magnitude below the incoming
  KE; see `sobol_t3_diagnostics.md`), so it ranks designs rather than predicting
  absorbed joules.
* **`F_peak_N` = peak\_g · g · payload\_mass** — the payload mass is held fixed
  per regime (`bo_evaluator.py:353`), so the *normalisation* is fine; the problem
  is the **observable**. At Tier-C the crutch peak\_g is essentially the **static
  support load** (`sobol_t3_diagnostics.md`: ratio ≈ 1.002; 712–739 N ≈ 75 kg·g =
  736 N), so for the crutch `F_peak` reads support load, not impact attenuation.
  The **lander** peak\_g is *not* that degenerate — 4628–4790 N over a 5 kg
  payload is a real ~94–98 g transient — but the diagnostics show the
  **base/floor-reaction** channel (≈ 103× static weight) is the physically better
  transmitted-load observable. So the precise claim is: crutch `F_peak` ≈
  support-load proxy; lander `F_peak` is a real transient but base reaction is the
  right bench-matched metric. Either way it is *not* size-normalised, so a "win"
  can come from a bigger / stiffer footprint rather than better mechanics.
* **`eta`** (mean/peak over the pulse) is dimensionless and intrinsically
  normalised — the fair one — but at Tier-C the lander `eta` is pinned to
  ~0.733 (it is currently not a discriminating axis).

**Net:** of the three objectives, only `SEA` controls for mass and *none*
control for volume or footprint. To be precise (per the Edison mock review,
§ "Edison mock-review refinements" below): `SEA_J_per_g` is fair on mass but
incomplete for the lander (ignores volume / footprint / stroke); `eta` is
intrinsically normalised but currently non-discriminating; and `F_peak`'s
*observable* is the main problem. Comparisons across the box are therefore
confounded by size. The crutch tolerates this (its envelope ceiling is generous
relative to a 24 mm tip), but **for the lander it breaks the problem**, because
mass and volume are the binding constraints, not free lunches. (Note: the
current Tier-C lander front is not *wrong* — it is a valid exploratory study over
a variable-size family; it just answers "which design wins when size is free?"
rather than the fair fixed-budget question we want.)

---

## 2. What the *actual* scaled-up lander-module constraints are

A deployable tensegrity crush-core / shock-isolator module (issues #14, #16;
heritage MER airbags, SUPERball, GEVS) lives under hard systems-engineering
budgets. The relevant ones, and how each maps onto our design axes:

1. **Mass budget (the binding one).** Every gram of absorber is a gram of
   payload the lander cannot carry. Landing-system mass is quoted as a *fraction
   of landed mass* (single-digit % for crush cores). This is a **hard cap on
   total absorber mass**, i.e. on `(R, H, strut_d, cable_d)` jointly — exactly
   the quantity that currently floats 6.2× across the box.
2. **Stowed / envelope volume.** The module must fit the launch-fairing or
   CubeSat-U allocation when stowed and the deployed standoff when landing.
   That caps `π R² H` (and, for a deployable, the stowed-vs-deployed ratio).
3. **Footprint / contact area & ground pressure.** The landing-pad contact area
   sets ground pressure on (possibly soft / sloped) regolith and the
   tip-over / stability cone. Too small → sinkage and instability; too large →
   mass and stowage penalties. This caps (and *floors*) the strut-tip footprint
   and the radius `R`.
4. **Stroke / standoff.** The crush stroke (≈ `H` minus solid height) must be
   long enough to keep peak g under the **GEVS ≤ 1500 g** requirement *proxy* at
   9.8 m/s, but short enough to fit the deployed envelope. A constant-force ideal
   absorber needs at least `s ≥ v²/(2·a_max) = 9.8²/(2·1500·9.81) ≈ 3.3 mm`
   stroke for the 1500 g cap; with `eta ≈ 0.73` and margin the practical floor is
   ~4.5–6 mm — far below the `H = 60–110 mm` box, so **height is mostly a
   packaging / shape variable here, not forced by the peak-g cap.** This is a
   coupled stroke↔envelope↔peak-g constraint.
5. **Specific energy absorption per unit mass *and* per unit volume.** Heritage
   crush cores are specified by *both* J/g and J/cm³; a fair lander objective
   has to respect the volumetric budget, not just the gravimetric one.
6. **Bench-test reachability.** The Lansmont M23 envelope (`regimes.M23`: ≤ 5000 g,
   ≥ 0.25 ms, ≤ 9.8 m/s, ≤ 36 kg) is a *validation* constraint on the loading,
   not the design, but it bounds what we can ever confirm experimentally.

The crutch tip has an analogous but looser set: a ≤ 24 mm OD envelope
(`regimes.py`), a per-strike mass that rides in the user's swing inertia (small
mass penalty), and an internal **peak-acceleration target (≤ 8 g) chosen to be
conservative relative to HAVS concerns** (ISO 5349 HAVS is frequency-weighted and
exposure-duration based, so the 8 g figure is a requirement proxy, not a literal
ISO scalar) rather than GEVS.

> **GEVS / HAVS wording.** Both the lander 1500 g and crutch 8 g figures are used
> here as *engineering requirement proxies*, not literal one-number standards:
> GSFC GEVS is normally expressed through shock response spectra / qualification
> environments, and ISO 5349 HAVS through frequency-weighted, exposure-based
> metrics. We optimise against the proxies but cite them as chosen study targets.

---

## 3. How to make the evaluations fair — two routes (and a hybrid)

There are two clean ways to remove the size confound, plus the do-nothing
baseline. They are not mutually exclusive.

### Route A — *Re-parameterise the search space* so the constraints are always met

Change variables so that the binding budget is **held constant by construction**,
and the optimiser can only trade *shape*, not *size*.

* **Constant-mass manifold.** Fix total cell mass `m*` (set per regime from the
  real mass budget) and drop one degree of freedom to satisfy it. E.g. keep
  `(R, H, twist, strut_d)` free and **solve `cable_d` (or `strut_d`) so the cell
  mass equals `m*`**. Then every design the GP sees weighs the same, and SEA's
  denominator is constant — the campaign becomes a pure *shape-for-fixed-mass*
  search. This is the cleanest analogue of how a lander team actually works:
  "you get `m*` grams of absorber; spend them well."
* **Constant-envelope manifold.** Alternatively fix `π R² H = V*` (fairing /
  deployed-volume allocation) and let the optimiser trade slender-tall vs
  squat-wide at fixed volume.
* **Constant-footprint manifold.** Fix the strut-tip footprint (ground-pressure
  / stability) and trade the rest.
* **Dimensionless / similarity variables.** Re-cast the box in shape ratios that
  are scale-free: aspect ratio `H/R`, strut slenderness `H/strut_d`, tendon-to-
  strut diameter ratio `cable_d/strut_d`, twist. Then choose **one** absolute
  scale variable (mass `m*`, or a size `s`) that is either *fixed* (per the
  budget) or carried as a *separate, explicitly-costed* axis. This is the most
  general version of "constant mass / volume / area" and is what I'd build first.

*Pros:* the Pareto front is then an honest shape-trade at the real budget;
constraints can never be violated; SEA stops rewarding "just add mass." *Cons:*
introduces a solve step / nonlinear axis coupling; the feasible manifold is
lower-dimensional, so the BO box must be defined in the new (ratio + scale)
coordinates.

### Route B — *Normalise / constrain the objectives* (keep the box, fix the scoring)

Keep the current rectangular box but make the **objectives and constraints**
size-aware so size is no longer a free win.

* **Report intensive objectives only.** Use `SEA_J_per_g` (already mass-
  intensive) **and add `SEA_J_per_cm³`** (energy / envelope volume) so the
  volumetric budget is represented. Replace the size-confounded `F_peak` with the
  **base floor-reaction force** (`sobol_t3_diagnostics.py` already measures it via
  `mj_contactForce`) and/or **ground pressure = reaction / footprint** so contact
  area is divided out instead of rewarded.
* **Add mass / volume / footprint as explicit outcome constraints.** Encode the
  lander budgets as Ax **outcome constraints** (`cell_mass ≤ m*`,
  `envelope_vol ≤ V*`, `footprint ∈ [A_min, A_max]`) and run **constrained
  qNEHVI**. The optimiser then *may* use the whole box but is penalised /
  infeasible outside the budget — exactly the `_INFEASIBLE_*` mechanism in
  `bo_evaluator.py`, extended from printability to the lander budgets.
* **Add mass / volume as a *cost* (cost-aware acquisition or a 4th objective).**
  Minimise mass (or volume) alongside the mechanical objectives so the Pareto
  front explicitly shows the *mass-vs-protection* trade instead of hiding it.

*Pros:* minimal change to the search box and tooling; the constraints are
*explicit and auditable*; you still learn the full landscape including the
infeasible region (useful for the GP boundary). *Cons:* the optimiser wastes
samples in the infeasible region; "fairness" is enforced softly (post-hoc) rather
than structurally; ad-hoc normalisation constants can be argued with.

### Recommended hybrid

* **Lander:** Route A on the binding budget + Route B on the rest. Fix **mass**
  on a constant-mass manifold (the dominant lander constraint), re-express the
  remaining freedom as scale-free shape ratios (`H/R`, `H/strut_d`,
  `cable_d/strut_d`, `twist`), and carry **envelope volume and footprint as
  outcome constraints** (so stowage and ground-pressure are respected but mass is
  structurally fixed). Score on **intensive** objectives: `SEA_J_per_g`,
  `SEA_J_per_cm³`, base-reaction-force-derived peak g (vs payload-accel proxy),
  and `eta`. That makes the lander campaign a fair "best shape for a fixed mass /
  volume / footprint budget" search — which is the question a lander team
  actually asks.
* **Crutch:** the budgets are looser, so Route B alone (intensive objectives +
  the ≤ 24 mm envelope and ≤ 8 g HAVS as outcome constraints) is enough; a
  constant-mass manifold is optional here.

---

## 4. Concrete next steps (small, mostly already-instrumented)

1. Add `cell_mass_g`, `envelope_cm3`, `footprint_mm2`, and `SEA_J_per_cm3` to the
   `bo_evaluator.evaluate_design` return dict (all derivable from
   `PrintableDesign.nodes`, already computed for SEA) so every campaign can
   constrain / normalise on them without new physics.
2. Add a `constant_mass=` (and `constant_envelope=`) option to the design
   sampler that solves one axis to hit the budget, and a ratio-based box
   (`H/R`, `H/strut_d`, `cable_d/strut_d`, `twist`, `mass`) for Route A.
3. Wire the lander budgets (`m*`, `V*`, `[A_min, A_max]`) as Ax outcome
   constraints and switch the lander loop to **constrained qNEHVI**; set the
   numbers from the real module mass-fraction / fairing allocation (TBD with the
   systems-engineering side).
4. Replace the lander `F_peak` objective with the **base-reaction** peak g
   (`sobol_t3_diagnostics.floor_reaction_history`) so the impact channel — not a
   support-load/contact proxy — drives the optimisation.
5. Re-run the Pareto campaign on the constant-mass manifold and compare the new
   front to `pareto_render_campaign.md`; the expectation is the "just get bigger"
   winners disappear and a genuine shape-trade emerges.

These are deliberately scoped as *follow-on* work; this document + the Edison
mock review are the deliverable for comment 4760939061 (the ask was to *suggest*
the approach and get feedback on the thinking).

---

## 5. Edison mock-review refinements (ANALYSIS task `e43abed6`)

We sent this thinking + the supporting artifacts (`regimes.py`, `bo_evaluator.py`,
`pareto_render_campaign.md`, `sobol_t3_diagnostics.md`) to Edison ANALYSIS for a
rigorous mock review (`scripts/edison/submit_fair_evaluation.py`; full answer at
[`edison-trajectories/fair-evaluation/`](../edison-trajectories/fair-evaluation/)).
The reviewer **endorsed the diagnosis and the recommended hybrid** ("reparameterise
to fixed absorber mass, optimise in dimensionless shape variables, constrain volume
and footprint/pressure explicitly, replace payload-accel `F_peak` with base
reaction, report both `SEA_J_per_g` and `SEA_J_per_cm³`"), and independently
reproduced the size-confound magnitude (~6.6× mass / 4.69× volume / 4.0× footprint).
Refinements already folded into the sections above:

* **Don't over-claim `F_peak` for the lander.** The crutch payload-accel `F_peak`
  is a support-load proxy (ratio ≈ 1.002), but the **lander** `F_peak` is a *real*
  ~94–98 g transient (4628–4790 N over 5 kg) — base reaction is simply the
  *better* transmitted-load observable, not a fix for a degenerate one.
* **Not all three objectives are "unfair":** SEA is fair on mass (incomplete on
  volume/footprint/stroke); `eta` is normalised but non-discriminating; `F_peak`'s
  *observable* is the real issue.
* **GEVS / HAVS are requirement proxies**, not literal one-number standards.
* **The current Tier-C lander front is not wrong** — it is a valid variable-size
  exploratory study; it just answers a different question than the fair
  fixed-budget one.

Reviewer methodology points worth keeping:

* **Reparameterisation > outcome constraints for the mass budget.** A constant-mass
  manifold is effectively an *equality* constraint; constrained qNEHVI handles
  *inequalities* (`volume ≤ V*`, `footprint ∈ [A_min,A_max]`, `pressure ≤ p_max`,
  `peak_g ≤ g_max`) well but is a poor substitute for a thin equality-feasible
  slice you already know analytically. Solve one geometric variable from
  `cell_mass = m*` and search the lower-dimensional domain (better sample
  efficiency, cleaner GP). This is the Buckingham-π / similitude argument; cf.
  Senadeera et al., *Bayesian Optimisation with Dimensionless Groups* (Applied
  Sciences, 2025), which reports faster convergence + better interpretability in
  dimensionless BO space.
* **Don't impose hard constraints on a biased cheap observable.** Enforce geometry
  budgets (mass/volume/footprint) at all fidelities (trusted, analytic); use
  Tier-C base reaction for coarse feasibility screening; reserve final peak-g
  acceptance for Tier-B/A or the bench. Hard `_INFEASIBLE_*` penalties are fine for
  geometry/printability filters but distort the surrogate if used for physics
  constraints — prefer feasibility-weighted (constrained qNEHVI) acquisition.
* **First-pass lander budget bands** (engineering starting points, *not* audited
  mission requirements): absorber mass ≈ **2–5 %** of landed mass (single-digit %),
  i.e. for the 5 kg regime an aggressive **50–100 g** / practical **100–250 g** /
  exploratory-cap **500 g** module allowance — against which the current cell's
  9.5–59 g range wanders unaccounted. Report fronts at 2–3 fixed mass (and 2
  envelope) budgets rather than one smeared unconstrained sweep. Treat
  ground pressure (= base reaction / footprint), not footprint alone, as the
  stability/regolith constraint. Energy-absorption FoMs should be reported both
  gravimetrically (J/g) and volumetrically (J/cm³), per Lu & Yu and Jones.
* **Caveat from the reviewer:** it would not commit to single literature-grounded
  numeric targets (mass fraction, regolith pressure, volumetric SEA) without
  mission-specific systems requirements — the bands above are engineering starting
  points, and a source-traceable heritage benchmark table is the clean next step.
