# Simple experimental tests to validate the simulation pipeline

Recommended bench-top tests, ordered from cheapest / earliest to most
involved.  Each row pins a specific simulation output to a measurable lab
observable so the three tiers (C: MuJoCo, B: Newton/DiffPD, A: PolyFEM+IPC)
can be falsified independently.  The goal is *progressively tighter*
sanity-checks before we burn drop-tower time on the Lansmont M23.

The tests intentionally start with quasi-static, single-cell, no-payload
configurations so the Tier-C MuJoCo / printable-design model gets validated
first — that is the only tier currently driving the BO loop (PR #30) and
must be trustworthy before tiers B/A pile on cost.

| # | Test (≈cost / time) | Equipment we already have / need | Sim model it validates | Pass criterion |
|---|---|---|---|---|
| 1 | **Single-tendon TPU-85A tensile pull** to ≤ 50 % strain | Instron 5969 (lab) + 100–500 N load cell (per #49) | `printable_design.tpu_cable_stiffness_Npm(d, L)` — the `E·A/L` model that *every* tier inherits | Measured secant stiffness within ±20 % of `12 MPa · π(d/2)² / L` over 0–10 % strain; nonlinearity ≤ 30 % up to 50 % strain |
| 2 | **Single PLA strut 3-point bend / axial compression** | Instron + custom fixture | PLA `E = 3.5 GPa` constant used by every tier (`PLA` in `printable_design.py`) | Measured `E` within ±15 % of book value at the print orientation we ship the BO with (vertical) |
| 3 | **Quasi-static cell compression** of one printed T3 prism (per #35) between Instron platens, no payload, 1 mm/min, log force vs displacement to 60 % strain | Instron + #35 printed parts | `run_regimes.simulate(...)` *initial-loading slope* and onset of strut-strut contact (class-1 → class-2 transition predicted by `class_1_margin_m`) | Initial slope within ±25 % of MuJoCo k_eff; class-2 contact onset within ±2 mm of `class_1_margin_m` |
| 4 | **Free-fall drop of bare cell** from 100 mm onto rigid steel anvil instrumented with PCB 350B03 force ring (or a calibrated piezo plate) | Existing drop fixture from #28 + force ring | MuJoCo `peak_g`, `pulse_ms`, contact sequence in the bare-cell regime (no payload — matches §3 of the payload-vs-no-payload Edison brief) | Tier-C peak force within a **factor of 2** of measured; pulse-width within ±30 %; first-contact strut identity matches |
| 5 | **High-speed video** (≥ 1000 fps phone slow-mo is enough for tier-C; ≥ 5000 fps Phantom for tier-B) of test 4 | Phone + LED ring, or borrowed Phantom | Newton (Warp) deformation field; MuJoCo strain-coloured tendon GIFs (`render_regimes.py`) | Strut COM trajectory tracks within ±2 mm at 60 fps; tendon-stretch ordering (which tendons go taut first) matches the Newton sweep |
| 6 | **Repeat drops × 20 from h = 100 mm** to bound run-to-run scatter (Bruceton-style noise floor) | Same as #4 | Heteroscedastic noise model in `bo_evaluator.py` / `simulate_specimen` (PR #30) — needed for qNEHVI to be calibrated | σ(peak_g)/μ(peak_g) ≤ 0.15; no systematic drift across the 20 drops (cell does not creep / fatigue at this energy) |
| 7 | **ASTM D5276 drop** at h matching the regime ΔV (crutch: 0.10 m onto rigid plate; lander: 5 m or M23 max ΔV), bare cell first, then with a representative payload puck per Edison §3(d) | Lansmont M23 (#28) + ADXL375 ±200 g on payload (per egg-drop memory) | Tier-B (Newton) `peak_g` with payload in load path; Tier-C MuJoCo run as upper-bound sanity | Tier-B within ±50 % of measured peak; tier-C within a factor of 3 (consistent with Edison sim-survey's warning that Tier-C "cables lack contact modeling") |
| 8 | **T3 prism orientation sweep** — drop the same cell on each of its 3 distinct face-down orientations | Same as #7 | Cell-symmetry assumption baked into the sim (MuJoCo only renders one orientation) | Peak-g spread across orientations ≤ 25 %; otherwise, BO must expose orientation as a design variable instead of assuming worst-case |
| 9 | **Stack of N=2, 3, 5 T3 cells (#35)** quasi-static + drop | Instron + drop tower | `tiling` categorical in PR #30; SDOF stack model | Stack stiffness scales as 1/N within ±20 % (series-spring prediction) |
| 10 | **Cell after 100 cycles**, repeat #3 | Instron, cycle to 30 % strain | Cycle-life / SEA degradation not yet in any sim tier; informs whether `eta` (compaction efficiency objective in PR #30) can be measured once and trusted | SEA drift ≤ 20 % across 100 cycles; otherwise BO must add a cycle-count outcome |

## Minimum viable validation budget

If we only have time for **three** tests before the BO campaign turns on:

1. **Test 3** (quasi-static T3 compression) — anchors the printable-design
   `k = E·A/L` model that drives every tier.
2. **Test 4** (bare-cell drop onto force ring) — anchors the MuJoCo
   `simulate(...)` peak-g + pulse-width predictions that the
   `bo_evaluator.evaluate_design(fidelity="C")` call (see
   `bo_integration.md`) returns to Ax.
3. **Test 6** (drop ×20) — calibrates the heteroscedastic noise the BO
   loop needs to weight tier-C observations correctly.

These three are doable in one Instron session + one drop-tower morning with
the #35 prints we already have.

## Things to *not* do at this stage

* Don't validate Tier-A (PolyFEM+IPC) until Tier-C is calibrated — the
  T-prism PolyFEM result currently sits at 1 g peak under static gravity
  settling (open box in PR description), not impact, so there is nothing
  yet for an experiment to falsify.
* Don't drop with the real 75 kg crutch payload until the bare-cell tier-C
  numbers agree to within a factor of 2 — every experimentalist contact in
  `edison-trajectories/modeling-feedback-contacts/` flagged payload
  inclusion as the most common drop-test pitfall.
* Don't try to measure strut/tendon Cauchy stress directly — DIC + thin
  TPU geometry is a Phase-2 thesis project, not a sanity check.
