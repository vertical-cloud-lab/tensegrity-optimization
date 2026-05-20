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

## Mapping PR #30 BO parameters → simulation inputs

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
   crutch *and* lander regimes, or should each regime run its own
   campaign?  *(Skelton, Davami, Agogino)*
3. Should we expose the BO loop to the regime as a fourth categorical
   axis, or keep one campaign per regime?  *(Frazier, multifidelity
   trade-off; ties back into payload-vs-no-payload Edison brief
   37ae0665.)*
