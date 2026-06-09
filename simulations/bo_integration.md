# Wiring this simulation pipeline into the PR #30 BO campaign

PR #30 (`copilot/scaffold-bayesian-optimization-script`, `bo/tensegrity_campaign.py`)
ships a 12-axis Ax/qNEHVI multi-objective campaign with three outcomes —
`F_peak_N`, `SEA_J_per_g`, `eta` — backed today by an analytical dummy
evaluator (`simulate_specimen`).  This document is the concrete wiring plan
for replacing that dummy with the simulation stack landed in this PR, with
a T3-prism (#35) initial batch per @sgbaird PR comment 4500844340.

## TL;DR

1. **Drop-in replacement** for `simulate_specimen` already lives at
   `simulations/bo_evaluator.py::evaluate_design(parameterization, regime, fidelity)`.
2. **Seed batch** is the three printed T3-prism designs returned by
   `simulations.bo_evaluator._t3_seed_designs()` — these are the parts
   already on the bench from PR #35 (Bambu H2D PETG, scale 1.0× and 1.5×,
   cable_d ∈ {1.5, 3.0, 4.5} mm).
3. **Multi-fidelity ladder** uses the three Edison-recommended tiers from
   the sim survey: tier-C MuJoCo (now, ~1 s), tier-B Newton/Warp (~30 s,
   planned), tier-A PolyFEM+IPC (~5 min, planned).
4. **Validation** is governed by `simulations/validation_experiments.md` —
   minimum three Instron + drop-tower tests *before* the BO loop turns on
   in service of real fabrication budget.

## Simulation cost (PR comment 4663414812)

Measured with `simulations/benchmark_costs.py` on an **AMD EPYC 7763**
(2 cores / 4 logical threads allotted to the runner), MuJoCo 3.9, NumPy:

| Tier | Engine | One objective eval (1 design × 1 regime) | Hardware | Status |
|---|---|---|---|---|
| C | MuJoCo rigid-body + tendon springs | **~75–120 ms raw**, **~190 ms with SAE J211 CFC-180 filtering** (crutch 118 ms, lander 73 ms, +~75 ms filter) | any modern x86 core, no GPU | wired (`bo_evaluator.evaluate_design`) |
| B | Newton / Warp XPBD | ~10–30 s | CUDA GPU strongly preferred | script exists (`newton_drop.py`), not yet a per-design entry point |
| A | PolyFEM + IPC (welded volumetric T-prism) | ~50–60 s/run **after** a ~25 min one-time source build | multi-core CPU, ~10 GB build dir | run end-to-end once (124bba2), not yet parametric |

So the **tier-C objective the BO actually calls costs ≈0.1–0.2 CPU-second
per design** (~0.1 s raw, ~0.2 s with the CFC-180 filter on). A full
PR #35 9-specimen Sobol batch is ~1–2 s single-threaded, and even a
1,000-design tier-C sweep is a few CPU-minutes — i.e. tier-C is
effectively free relative to a single
physical print+drop, which is the entire point of using it as the bulk
evaluator and reserving tier-B/A (and the real drop tower) for the
high-reward Pareto front. These numbers are what a cost-aware /
multi-fidelity acquisition function (Frazier 2018 `MultiFidelityAcquisition`)
should be fed as the per-tier evaluation cost.

## Wiring into the PR #35 T3-prism batch (`bo/t3_prism_sobol_batch.py`)

PR #35's `bo/t3_prism_sobol_batch.py` emits a Sobol design set but reports
**no objectives back** (its `objectives={"placeholder": ...}` is a stub).
`bo_evaluator` now accepts the PR #35 schema directly so those specimens can
be scored without re-printing:

```python
from simulations.bo_evaluator import evaluate_batch_csv
# Score every specimen the batch generator wrote:
rows = evaluate_batch_csv("bo/t3-prism-bo-batch.csv", regime=CRUTCH)
# each row = the design columns + {F_peak_N, SEA_J_per_g, eta}
```

or from the CLI: `python simulations/bo_evaluator.py --batch-csv bo/t3-prism-bo-batch.csv`.

The PR #35 axes map straight onto the simulator:

| PR #35 axis (real mm, post-scale) | Range | Sim consumer |
|---|---|---|
| `R_mm` (circumscribing radius) | [25, 40] | `PrintableDesign.radius_m` → `Regime.radius_m` |
| `H_mm` (cell height) | [60, 110] | `PrintableDesign.height_m` → `Regime.height_m` |
| `twist_deg` (top vs bottom) | [40, 80] | `PrintableDesign.twist_rad` **+120° convention offset** (see below) |
| `strut_d_mm` (PLA strut Ø) | [6, 12] | `Regime.strut_radius_m` (×0.5) |
| `cable_d_mm` (TPU cable Ø) | [3.0, 5.5] | `tpu_cable_stiffness_Npm` → `Regime.cable_stiffness_Npm` |

**Twist convention.** The CAD/PR #35 strut connectivity is `B_i → T_i`
(equilibrium twist 60°, `cad/t3-prism/t3-prism.scad`), while the simulator's
`tprism_geometry.tprism_nodes` uses `B_i → T_{i+1}` (equilibrium 150°). They
describe the same prism when `sim_twist = scad_twist + 120°`;
`normalize_parameterization` applies that offset. Without it, every printed
T3-prism (twist ∈ [40°, 80°]) is mis-flagged class-2 because the struts
appear to cross the central axis. Verified: the full PR #35 twist range now
clears class-1 (strut gap 48–61 mm at the production R/H).

## What the simulations give the BO that the printer/drop-tower cannot (cheaply)

The simulations and the manual high-fidelity drop tests (`docs/drop-test-protocol.md`,
PR #67 / #74) share **one objective space**: peak transmitted force/`g`,
specific energy absorption, and compaction efficiency. That shared space is
exactly what lets them combine in a multi-fidelity campaign:

- **Pre-screening / GP seeding.** Tier-C scores all 9 Sobol specimens in ~1 s,
  so the BO can rank-order the batch *before* committing ~hours of print +
  drop time. The objectives align with what the drop tower measures after
  SAE J211 CFC-180 filtering (PR #74): `peak_g` ↔ filtered peak `g`,
  `sea_Jpkg` ↔ measured SEA. To make that alignment exact, `bo_evaluator`
  applies the **same SAE J211 CFC-180 filter** (`_cfc_filter`, pure-NumPy
  4-pole-phaseless Butterworth, J211-1 appendix C) to the simulated axial
  acceleration before reading `F_peak`/`eta` — so a simulated row and a
  measured row are processed identically and can be attached to the *same*
  AxClient as different-fidelity observations (toggle with `cfc180=False`
  or `--raw-peak`). This was the top recommendation of Edison ANALYSIS
  task `4e74f66c` (see `edison-trajectories/simulation-bo-value/`).
- **Trade-off geometry.** The crutch-vs-lander split (PR comment / `regimes.py`)
  shows the F_peak ↔ SEA ↔ eta trade-off is regime-dependent: at the
  production R/H, the lander regime drives `F_peak` to ~5 kN with `eta`
  ~0.70, while the crutch regime sits near the soft-cushion limit (`eta`
  ~0.96). Rather than averaging the two (which destroys the regime signal) or
  running two fully independent campaigns (which throws away the shared
  structure), the preferred treatment is a **multi-task GP** that carries the
  regime as a task and lets the campaigns share information as soon as it is
  observed — see [Multi-task treatment of the regimes](#multi-task-treatment-of-the-regimes-crutch-and-lander) below.
- **Feasibility for free.** `PrintableDesign.check()` rejects class-2 strut
  overlap, unprintable cable diameters, and prestrain past TPU break before
  any sim runs, so the BO learns the printable-feasible boundary at zero
  fabrication cost.

The honest limits (all flagged to the reviewers in
`edison-trajectories/modeling-feedback-contacts/`): tier-C is rigid struts +
scalar tendon springs, so it does **not** capture PLA strut buckling, TPU
hyperelastic hysteresis, or strut–strut contact — those are precisely the
tier-B/A and physical-drop jobs. Tier-C is a *ranking* tool for the bulk of
the search, not a quantitative predictor of the absolute `g` a given printed
T3-prism will survive.

## Multi-task treatment of the regimes (crutch and lander)

In response to PR comment 4664686033, the recommended way to handle the two
impact regimes is **not** one isolated campaign per regime (the
one-campaign-per-regime suggestion from Edison sim-survey 782657e0), but a
single **multi-task Bayesian optimization (MTBO)** campaign in which the
regime is a *task* dimension and the two campaigns share information as soon
as it is available (per @sgbaird and the Honegumi multitask docs:
[concept](https://honegumi.readthedocs.io/en/latest/curriculum/concepts/multitask/multitask.html),
[tutorial](https://honegumi.readthedocs.io/en/latest/curriculum/tutorials/multitask/multitask.html)).

**Why MTBO fits here.** The crutch and lander regimes share the *same*
design space — identical PR #35 T3-prism axes (`R_mm`, `H_mm`, `twist_deg`,
`strut_d_mm`, `cable_d_mm`); they differ only in the load case
(`Regime` drop height / payload, `regimes.py`). The objectives are
*correlated but offset* (a softer cell helps both `eta` curves; only the
absolute level and the `F_peak` scale differ between regimes). That is
exactly the regime where a multi-task kernel
`K((x,t),(x',t')) = K_t(t,t') ∘ K_x(x,x')` shines: an evaluation in the
crutch task immediately informs the lander model and vice-versa, which is far
more sample-efficient than two independent GPs — and tier-C is cheap enough
(~0.1–0.2 s/design) to populate both tasks densely.

**Wiring.** Ax supports this through a `Task` parameter plus the
`ST_MTGP` transform / `Models.BOTORCH_MODULAR` generation strategy used in
the Honegumi tutorial. Concretely, the regime becomes a task choice and
`bo_evaluator.evaluate_design` is already regime-parameterized, so the
evaluator side needs no change — only the AxClient setup does:

```python
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.modelbridge.registry import Models, Specified_Task_ST_MTGP_trans
from simulations.bo_evaluator import evaluate_design
from simulations.regimes import CRUTCH, NASA_LANDER

REGIME_TASKS = {"crutch": CRUTCH, "nasa_lander": NASA_LANDER}

gs = GenerationStrategy(steps=[
    GenerationStep(Models.SOBOL, num_trials=8,
                   model_kwargs={"transforms": Specified_Task_ST_MTGP_trans}),
    GenerationStep(Models.BOTORCH_MODULAR, num_trials=-1,
                   model_kwargs={"transforms": Specified_Task_ST_MTGP_trans}),
])
# ... AxClient(generation_strategy=gs); add a "regime" Task parameter
# (values "crutch", "nasa_lander") alongside the PR #35 design axes, then:
resp = evaluate_design(params, regime=REGIME_TASKS[params["regime"]], fidelity="C")
```

**One caveat to watch (Honegumi "where multitask models go wrong").** The
Ax multitask kernel is purely multiplicative, so under extrapolation the
task models collapse toward a *common* mean. Because the crutch `eta` (~0.96)
and lander `eta` (~0.70) means genuinely differ, the two tasks should be kept
well-observed (don't let one task starve), and per-outcome standardization /
an intercept-aware kernel should be used so the mean offset is not washed
out. With both tasks fed by cheap tier-C evaluations this is easy to satisfy.

This MTBO framing also generalizes cleanly to the multi-fidelity ladder:
fidelity (C/B/A) is naturally a *second* task axis, so the same machinery
that shares information across regimes can share it across simulator tiers
and, eventually, the physical drop tower.



| BO axis (PR #30) | Sim consumer | Notes |
|---|---|---|
| `strut_diameter_mm` (range, 1.5–5.0) | `PrintableDesign.strut_diameter_m` → `Regime.strut_radius_m` (×0.5) | Direct |
| `strut_length_mm` (range, 15–50) | `PrintableDesign.height_m` → `Regime.height_m` | Drives buckling slenderness via `L/D` |
| `cable_diameter_mm` (range, 1.0–3.0) | `PrintableDesign.tendon_diameter_m` → `tpu_cable_stiffness_Npm(d, L)` → `Regime.cable_stiffness_Npm` | Tier-C reduces the cable to a scalar spring; tier-B (Newton) keeps the explicit cross-section |
| `twist_angle_deg` (range, 10–45) | `PrintableDesign.twist_rad` | Only matters for tier-B/A geometry; tier-C uses the equilibrium twist of the T3 |
| `prestress_pct` (range, 0–5) | `PrintableDesign.prestrain` → `Regime.cable_pretension_frac` | Used by every tier; capped by TPU break stress check in `PrintableDesign.check()` |
| `struts_per_cell` (3, 4, 6, 8, 12) | not yet wired | First batch is `=3` (T3 only); other values require generic mesher |
| `topology` (4-way categorical) | `bo_evaluator._topology_warning(...)` warns; T3 physics used regardless | Per @sgbaird comment 4500844340, T3 is the first-batch focus |
| `tiling` (5-way categorical) | not wired in tier-C | Tier-B Newton stacks particles; tier-A PolyFEM stacks meshes; for now BO will see no signal from this axis |
| `tpu_shore` (85A / 95A) | `bo_evaluator._TPU_E_MPA` | TPU 85A E=12 MPa, 95A E=25 MPa per memory |
| `petg_infill_pct` (40–100) | reduces `Regime.strut_density_kgm3` proportionally (planned) | Currently constant 1240 kg/m³ — small effect on tier-C peak-g |
| `petg_infill_pattern` (3-way) | not wired | Tier-A only; secondary axis |
| `interface_wrap_thickness_mm` (0.4–2.0) | not wired | Tier-A only; secondary axis |
| `build_orientation` (3-way) | not wired | Phase-2 / requires anisotropic strut material |

What this means in practice: with PR #30 + `bo_evaluator.evaluate_design`
the qNEHVI surrogate immediately gets *signal* on five axes (strut Ø/L,
cable Ø, prestress, TPU shore) and the remaining seven axes register as
nuisance dimensions until the higher tiers ship.  That is the right
ordering — the five wired axes are the ones our printable-design Pareto
heatmaps (`regime_*_printable_heatmap.png`) already showed dominate
peak-g and SEA at the T3 scale.

## Drop-in replacement for `simulate_specimen`

In `bo/tensegrity_campaign.py`, replace the call site::

    response = simulate_specimen(parameterization, rng=rng)

with::

    from simulations.bo_evaluator import evaluate_design
    from simulations.regimes import CRUTCH         # or NASA_LANDER
    response = evaluate_design(parameterization, regime=CRUTCH, fidelity="C")

`evaluate_design` returns exactly the `{F_peak_N, SEA_J_per_g, eta}` dict
shape that `simulate_specimen` returned, so the surrounding Ax loop /
Pareto plot code does not change.

## Seeding the campaign with the T3 designs we already printed (#35)

Per @sgbaird comment 4500844340, the first BO batch should cover the T3
prisms we already have hardware for.  `bo_evaluator._t3_seed_designs()`
returns three such designs (PR #35 default at scale 1.5×, baseline at
scale 1.0×, and a soft-tendon variant) as Ax-compatible dicts.

The recommended start-up sequence is then::

    from ax.service.ax_client import AxClient
    from simulations.bo_evaluator import _t3_seed_designs, evaluate_design

    ax_client = AxClient(...)   # PR #30 setup unchanged
    for params in _t3_seed_designs():
        # Run the *real* experiment for each printed T3 cell first
        observed = run_drop_tower(params)            # human-in-the-loop
        idx = ax_client.attach_trial(params)
        ax_client.complete_trial(idx, raw_data=observed)

    # Then let Ax pick the next batch, evaluated by simulation:
    for _ in range(N_ITERATIONS):
        for params, idx in ax_client.get_next_trials(...):
            ax_client.complete_trial(
                idx,
                raw_data=evaluate_design(params, regime=CRUTCH, fidelity="C"),
            )

That is, the **first 3 trials** anchor the GP on real measurements; the
**subsequent N_ITERATIONS · BATCH_SIZE trials** are driven by simulation
until the next batch of T3 prints is ready.  This is exactly the cost
ladder Frazier (2018) recommends for multi-fidelity BO and the multi-tier
recommendation from Edison sim-survey task 782657e0.

## Multi-fidelity escalation (planned)

`evaluate_design(..., fidelity="C")` is the only branch wired today.
The forward-compatible signature already accepts `"B"` and `"A"`; the work
to enable them is:

* **Tier-B (Newton):** `simulations/newton_drop.py` already builds the T3
  prism as an XPBD particle network with tendon springs.  Open task is to
  factor out a `simulate(design, regime)` function (similar to
  `run_regimes.simulate`) that returns the same `{peak_g, sea_Jpkg, ...}`
  dict so `bo_evaluator.evaluate_design` can dispatch on `fidelity`.
* **Tier-A (PolyFEM+IPC):** `simulations/polyfem_drop.py --geometry tprism`
  already meshes 3 PLA struts + 9 TPU tendons via gmsh OCC fragment.
  Open task is to add an explicit-velocity initial condition (per the
  PR description's open box) and a Python entry-point that takes a
  `PrintableDesign` + regime ΔV and returns the same observables dict.

Once both are wired, the Ax campaign can use `MultiFidelityAcquisition`
(cost-aware EHVI per Frazier 2018) to allocate trials by cost — tier-C
for the bulk of the search, tier-B/A for refining around the
high-reward Pareto front.

## Open questions for review

These are the questions to take to the contacts in
`edison-trajectories/modeling-feedback-contacts/` (PR comment
4500576843) before the BO loop runs against real drop-tower data:

1. Is the tier-C → tier-B agreement bound (factor ≤ 2 on peak-g) good
   enough to use tier-C as the bulk evaluator?  *(Schneider, Rimoli, Du,
   Frazier)*
2. Are `F_peak_N`, `SEA_J_per_g`, `eta` the right three outcomes for the
   crutch *and* lander regimes?  *(Skelton, Davami, Agogino)*
3. For handling both regimes, the current plan is a **multi-task GP** (regime
   as a task, information shared across campaigns — see
   [Multi-task treatment of the regimes](#multi-task-treatment-of-the-regimes-crutch-and-lander)),
   in preference to either averaging or fully independent per-regime
   campaigns. Open question: is the multiplicative multitask kernel's
   mean-collapse behavior acceptable given the crutch/lander `eta` offset, or
   do we need an intercept-aware kernel?  *(Frazier, multifidelity
   trade-off; ties back into payload-vs-no-payload Edison brief 37ae0665.)*

## Edison ANALYSIS query (PR comment 4663414812)

In response to PR comment 4663414812, an Edison `ANALYSIS`
(`data-analysis-crow-high`) task was submitted asking how these
multi-fidelity simulations should feed (a) the PR #35 T3-prism BO
campaign and (b) the high-fidelity manual validation (drop-tower /
Instron), and what information the sims surface that the printer/bench
cannot cheaply provide. The query bundled four files as ground truth:
the PR #35 BO script (`bo/t3_prism_sobol_batch.py`), this bridge
(`bo_evaluator.py`), the tier-C simulator (`run_regimes.py`), and the
manuscript draft. The submit script is
`scripts/edison/submit_simulation_bo_value.py`; the trajectory artifacts
land in `edison-trajectories/simulation-bo-value/`.
