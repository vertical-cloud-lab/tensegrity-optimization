# State-of-the-Art Tensegrity Simulation Survey

> Resolves: *"Begin exploring state-of-the-art simulations for tensegrity,
> tensegrity-like structures, and other related methods."*

This directory contains a first pass at downloading, installing and **actually
running** open-source simulators capable of modelling the multi-material
3D-printed tensegrity structures targeted by this MRG project (PLA struts
+ TPU tendons, optimised for impact / energy absorption).

A complementary high-effort literature survey was submitted to Edison
Scientific (FutureHouse) — the [survey response is committed at
`edison-trajectories/2026-05-08-sim-survey-782657e0.md`](../edison-trajectories/2026-05-08-sim-survey-782657e0.md)
(task `782657e0-0818-4755-9e18-60c8039b2ccd`, status *success*) —
together with the application-regime sweeps described in
[§ Application regimes](#application-regimes-issues-18--14--16--28).

## Engines exercised

| Engine | Version | Install | Status | Notes |
|---|---|---|---|---|
| **MuJoCo** (DeepMind) | 3.8.0 | `pip install mujoco` | ✅ runs | Native `<spatial>` tendon primitive (Hookean + damping). Ideal first stop. |
| **PyBullet** (Bullet 3) | 3.x (May 2026 build) | `pip install pybullet` | ✅ runs | No native tendon; cables implemented as unilateral spring forces applied via `applyExternalForce`. This is the same approach used historically by NASA's NTRTsim. |
| **PyChrono** (Project Chrono 10.0) | 10.0 | `conda install -c projectchrono -c conda-forge pychrono` | ✅ runs | First-class `ChLinkTSDA` springs; FEA cable elements (`ChElementCableANCF`) and IGA beams also available for higher fidelity. **Do not** install the homonymous PyPI package `pychrono` — it is unrelated. |
| **Newton** (NVIDIA, on Warp) | 1.1.0 | `pip install newton` | ✅ runs (Edison Rec B / DiffPD-tier) | Differentiable GPU-accelerated multi-physics. We use it as the all-particle XPBD stand-in for DiffPD: TPU-85A tendons are explicit Hookean springs in series with the impact load path (payload internally suspended from all 6 prism nodes), so peak g and SEA respond to tendon Ø, unlike the rigid-strut engines above. |
| **DiffPD** (MIT GFX, SIGGRAPH 2021) | `mit-gfx/diff_pd_public` HEAD | source build (CMake + SWIG; no Pangolin/OpenGL needed for the sim core) | ✅ runs (Edison Rec B) | Original projective-dynamics differentiable solver. We drop a TPU-85A NeoHookean hex cube against a planar barrier; see `diffpd_drop.py`. |
| **PolyFEM + IPC** (NYU CIMS) | `polyfem/polyfem` HEAD | source build (CMake; ~25 min, ~10 GB build dir, ~160 MB binary) | ✅ runs (Edison Rec A) | Reference high-fidelity contact (IPC barrier method, intersection-free). PyPI `polyfempy` sdist is broken; `simulations/polyfem_drop.py` shells out to the built `PolyFEM_bin` with a NeoHookean TPU-85A cube + ground-plane drop JSON. |

All three reproduce the same baseline experiment (a 3-bar Snelson T-prism
dropped from 1 m onto a flat floor). Cross-engine agreement: settled COM
height 0.094–0.106 m and peak kinetic energy 0.95–1.04 J (≈ `m·g·h ≈ 1 J`).

## Files

```
simulations/
├── tprism_geometry.py    # 3-bar Snelson prism node/edge generator (no deps beyond numpy)
├── tprism_mesh.py        # gmsh OCC volumetric mesher: 3 PLA struts + 9 TPU tendons fused
├── mujoco_drop.py        # MuJoCo MJCF + drop simulation (✅ baseline)
├── pybullet_drop.py      # PyBullet rigid-body + manual spring cables (✅)
├── pychrono_drop.py      # Project Chrono ChLinkTSDA (✅, conda install required)
├── newton_drop.py        # NVIDIA Newton (Warp) all-particle XPBD; tendons in load path
├── mujoco_sweep.py       # 1-D parameter sweep --> BO objective stub
├── regimes.py            # Application regime dataclasses (crutch + NASA) + Lansmont M23 envelope
├── run_regimes.py        # Drives MuJoCo through both regimes; produces 4 figures + 2 CSVs
├── printable_design.py   # PLA strut + TPU 85A tendon material model + class-1 check
├── printable_sweep.py    # 2D sweep over printable vars (tendon Ø × prestrain) for both regimes
├── bo_evaluator.py       # PR #30/#35 parameterization -> Tier-C objective bridge
├── sim_bo_campaign.py    # closed-loop sim-only Ax/qNEHVI BO over the PR #35 T3 box (mirror of #35, sim objectives)
├── sim_bo_hybrid_campaign.py # *fair* closed-loop BO: Route A constant-mass shape-ratio manifold + Route B intensive objectives & envelope/footprint outcome constraints (constrained qNEHVI)
├── sobol_t3_campaign.py  # PR #35 Sobol T3-prism batch -> C→B→A ladder (MuJoCo/PyBullet/PyChrono + Newton + PolyFEM) + analysis
├── sobol_t3_violins.py   # Plotly violin plots (jittered raw points) of the Sobol campaign measurements
├── sobol_t3_diagnostics.py # Edison-review ablations: base-reaction force, CFC on/off, constant-mass strut sweep, twist plumbing audit
├── pareto_render_campaign.py # dense Tier-C Pareto-front search + 3D renders of best/worst/mediocre designs as Pareto-graph callouts
├── render_utils.py       # OSMesa offscreen-render helper (lights, sky, strain colour map)
├── render_mujoco_drop.py # 3D GIF/MP4 of the basic 1 m prism drop
├── render_regimes.py     # 3D GIF/MP4 of both regime drops (suspended payload)
├── render_spotchecks.py  # Sanity-check renders: capsule, bare prism, suspended payload
└── outputs/
    ├── mujoco_drop_energy.png
    ├── mujoco_drop_data.npz
    ├── pybullet_drop_energy.png
    ├── pybullet_drop_data.npz
    ├── pychrono_drop_energy.png
    ├── pychrono_drop_data.npz
    ├── mujoco_sweep.csv
    ├── mujoco_sweep.png
    ├── regime_crutch_tip_timeseries.png
    ├── regime_crutch_tip_sweep.{png,csv}
    ├── regime_nasa_lander_timeseries.png
    ├── regime_nasa_lander_sweep.{png,csv}
    ├── regime_crutch_tip_printable_{heatmap,pareto}.png
    ├── regime_crutch_tip_printable.csv
    ├── regime_nasa_lander_printable_{heatmap,pareto}.png
    └── regime_nasa_lander_printable.csv
```

Run any script directly:

```bash
# MuJoCo / PyBullet (system Python)
python simulations/mujoco_drop.py
python simulations/pybullet_drop.py
python simulations/mujoco_sweep.py
python simulations/run_regimes.py     # both application regimes, MuJoCo
python simulations/printable_sweep.py # PLA/TPU printable-design sweep, MuJoCo

# PR #35 T3-prism Sobol batch through the simulators + analysis
#   Full C→B→A ladder on PR #35 T3-prism Sobol variations:
#   Tier-C MuJoCo (all N) + PyBullet + PyChrono (rigid cross-engines),
#   Tier-B Newton/Warp XPBD, Tier-A PolyFEM+IPC (welded PLA/TPU prism).
#   PyChrono needs PYCHRONO_PYTHON; PolyFEM needs POLYFEM_BIN/POLYFEM_DATA_DIR.
python simulations/sobol_t3_campaign.py --n 512 --n-tierb 24 \
    --n-tiera 8 --n-pybullet 32 --n-pychrono 16
# -> outputs/sobol_t3_{tierC,tierB,tierA,pybullet,pychrono}.csv
# -> outputs/sobol_t3_{pareto,sensitivity,tierC_vs_tierB,engine_ladder,tierA}.png
# -> sobol_t3_analysis.md  (results & interpretation)

# Violin plots (jittered raw points) of the campaign measurements:
#   plotly.express.violin(..., points="all", box=True) with jitter.
python simulations/sobol_t3_violins.py
# -> outputs/sobol_t3_violin_{objectives,engines}.{png,html}

# Tier-C artifact-vs-physics diagnostics (Edison ff8faab3 follow-up):
#   base-reaction force vs payload accel, CFC-180 on/off, constant-mass
#   strut-diameter sweep, and the twist plumbing audit.
python simulations/sobol_t3_diagnostics.py --n 48
# -> outputs/sobol_t3_diag_{base_reaction,cfc,constmass}.csv
# -> outputs/sobol_t3_diagnostics.png + sobol_t3_diagnostics.md

# Closed-loop simulation-only Bayesian optimization over the PR #35 T3 box
#   (Ax/qNEHVI, objectives = Tier-C MuJoCo sim; mirror of #35's hardware loop).
#   Each regime is plotted separately; multiple --seeds give a std-dev band;
#   --tiers adds the Newton (Tier-B) loop; LOO-CV plots check predictive signal.
python simulations/sim_bo_campaign.py --tiers C --seeds 0 1 2 --n-iter 30
python simulations/sim_bo_campaign.py --tiers B --seeds 0 1 --n-iter 15  # Newton
# -> outputs/sim_bo_<tier>_<regime>.csv + *_pareto.csv
# -> outputs/sim_bo_<tier>_<regime>_seed<k>_{convergence,pareto,cv}.png
# -> outputs/sim_bo_<tier>_<regime>_convergence.png (mean ± std band)
# -> sim_bo_campaign.md

# *Fair* closed-loop BO — the hybrid (Route A + Route B in ONE campaign/regime)
#   (PR comment 4815305004; the hybrid is defined in fair_evaluation_analysis.md
#    §3-4).  Route A: search dimensionless shape ratios (H/R, H/strut_d,
#    cable_d/strut_d, twist) at a FIXED cell mass m* (constant-mass manifold), so
#    the optimiser can only trade shape, never size.  Route B: score intensive
#    objectives (impact F — base floor-reaction for the lander —, SEA_J_per_g,
#    SEA_J_per_cm3, eta) under envelope/footprint Ax outcome constraints
#    (constrained qNEHVI).  Seeded with the 3 printed PR #35 cells projected onto
#    the manifold; per-regime, per-seed; LOO-CV checks predictive signal.
python simulations/sim_bo_hybrid_campaign.py --regime both --seeds 0 1 2 --n-iter 30
python simulations/sim_bo_hybrid_campaign.py --regime lander --mass-g 25 \
    --envelope-max-cm3 200 --footprint-min-mm2 110 --footprint-max-mm2 190
# -> outputs/sim_bo_hybrid_<regime>.csv + *_pareto.csv + *_cv_summary.csv
# -> outputs/sim_bo_hybrid_<regime>_seed<k>_{convergence,pareto,cv}.png
# -> outputs/sim_bo_hybrid_<regime>_{convergence,feasibility}.png
# -> sim_bo_hybrid_campaign.md

# PyChrono (conda Python; install per table above)
/usr/share/miniconda/bin/python simulations/pychrono_drop.py

# Dense Tier-C Pareto-front search + renders of the picks (PR comment 4760877672)
#   Sobol-maps the true 3-objective Pareto front over the PR #35 box (sims are
#   cheap, so no cost-aware/multi-fidelity needed) and renders the Pareto-best,
#   worst, and mediocre cells as 3D stills dropped onto the Pareto graph as
#   callout thumbnails (+ best/worst drop GIFs).
MUJOCO_GL=osmesa python simulations/pareto_render_campaign.py --n 2048
# -> outputs/pareto_<regime>.csv  (every design + objectives + pareto flag)
# -> outputs/pareto_<regime>_annotated.png  (Pareto scatter w/ render callouts)
# -> outputs/pareto_<regime>_render_<tag>.png  +  *_{best,worst}_drop.{gif,mp4}
# -> outputs/pareto_summary.md

# The PR #102 bench campaign, matched in simulation (PR comment 5365740315)
#   Sub-100 % PLA infill -> printed mass / effective strut density + modulus.
python simulations/print_infill.py
#   The constant-*printed*-mass projection from base coords to the article
#   that is actually printed (PR #102 commit 2f1ca2e), calibrated here from
#   the committed batch table + print key.  Replaces the constant-*solid*-mass
#   projection in the objective path: holding solid mass constant leaves
#   printed mass free, and e_reb_mJ is proportional to mass, so the objective
#   became the mass (rho = 0.9999 over the reference sweep).
python simulations/pr102_mass_model.py
# MuJoCo analogue of the 60 in / PU-mat drop, in the bench's own two
# objectives (CFC-180 transmissibility t180, rebound energy e_reb_mJ).
python simulations/drop_tower_sim.py --calibrate   # refit the mat to the rig
python simulations/drop_tower_sim.py --spec 1      # one Sobol article
# Which simulated observable actually tracks the measured objectives?
python simulations/pr102_correlation.py
# -> outputs/pr102_sim_vs_measured.csv, pr102_correlations.csv,
#    pr102_correlation.png
# Closed-loop simulation-only campaign, one independent run per seed
# (SAASBO by default, matching PR #102).  --init sobol, the default, redraws
# round 0 from each repeat's own seed, so a repeat is a whole campaign rather
# than one re-roll of the surrogate; --init printed reproduces PR #102's
# shared round 0.  --jobs runs repeats concurrently, one process each.
# Parallel seed matrix for Actions:
#   simulations/workflows-staged/sim-bo-pr102-matrix.yml (move into
#   .github/workflows/ to run it; this PR's app cannot write there).
# --space ratios (the default) is the 2026-08-22 re-parameterization: no
# mass parameter; the four scale-free shape ratios are searched, the overall
# scale is solved so printed mass is exactly 20.23 g, the second objective is
# the dimensionless e_rebound, and printability (printed cable >= 3.0 mm,
# envelope <= 250 cm^3) enters as Ax outcome constraints.  --space slab6
# reproduces the earlier PR #102-style six-parameter space.
python simulations/pr102_sim_campaign.py --model botorch \
    --seeds 0 1 2 3 4 5 6 7 8 9 --rounds 4 --jobs 4
# -> outputs/pr102_sim_bo_<model>[_ratios]_<init>_seed<k>.{csv,png}
# -> outputs/pr102_sim_bo_<model>[_ratios]_<init>_aggregate.png + _summary.csv
# Baselines and a reference optimum for that campaign (PR comment 5376310081).
#   The reference is a 65,536-design Sobol sweep plus a Nelder-Mead polish of
#   21 weightings: the ceiling every trace is drawn against.  The baselines
#   run at the campaign's own 36-design budget over the same ten seeds.
# Baselines take the same --space flag; ratio-space files carry a _ratios
# suffix, and unprintable projections are excluded from fronts/hypervolumes
# but kept in the CSVs.
python simulations/pr102_baselines.py --reference --jobs 4
python simulations/pr102_baselines.py \
    --strategies random sobol lhs heuristic --seeds 0 1 2 3 4 5 6 7 8 9 --jobs 4
# -> outputs/pr102_reference_cloud[_ratios].csv.gz  (every evaluation)
# -> outputs/pr102_reference_front[_ratios].csv + _summary + _front.png
# -> outputs/pr102_baseline_<strategy>[_ratios]_seed<k>.csv
# -> outputs/pr102_baselines_comparison[_ratios].png, _objective_space,
#    _summary
```

## Matching the PR #102 bench campaign in simulation

[`pr102_sim_campaign.md`](pr102_sim_campaign.md) — the write-up: the infill
model and its calibration against the weighed articles, the drop-tower
analogue and what its mat is (and is not) calibrated on, the correlation
study against the eight tested articles, and the repeat-seed campaign. The
headline: the purpose-built `t180` analogue is *not* the best simulated
predictor of measured `t180` (rho = +0.46, n = 7); `lander_eta` from the
existing Tier-C regime sims is (rho = -0.96), and no simulated observable
predicts measured `e_reb_mJ` yet. Section 5 adds the baselines: against a
68,944-evaluation reference front, the 36-design BO reaches 97 % of the
ceiling while compass search reaches 80 %, Sobol 66 %, Latin hypercube 65 %
and random search 60 %, every one of them completely separated from the BO
over ten seeds.

## Fair-evaluation analysis (PR comment 4760939061)

[`fair_evaluation_analysis.md`](fair_evaluation_analysis.md) — a thinking
document on *fairness* of the objective evaluations: across the PR #35 box the
cell mass varies 6.2×, envelope volume 4.7×, and strut-tip footprint 4.0×, so
designs are compared at very different sizes. It lays out the real scaled-up
lander-module constraints (mass budget, stowed volume, footprint/ground
pressure, stroke) and two routes to fairness — (A) re-parameterise to a
constant-mass / constant-envelope / scale-free-ratio manifold so the budget is
met by construction, and (B) keep the box but use intensive objectives
(`SEA_J_per_g`, `SEA_J_per_cm³`, base-reaction peak g) with mass/volume/footprint
as outcome constraints in constrained qNEHVI — plus a recommended hybrid. Sent to
Edison ANALYSIS for mock feedback
([`edison-trajectories/fair-evaluation/`](../edison-trajectories/fair-evaluation/)).
The recommended **hybrid is now implemented** as a runnable closed-loop campaign
in [`sim_bo_hybrid_campaign.py`](sim_bo_hybrid_campaign.py) — see
[`sim_bo_hybrid_campaign.md`](sim_bo_hybrid_campaign.md) (PR comment 4815305004).

## Baseline experiment

3-bar regular T-prism, equilibrium twist 5π/6 (Snelson), `r = 0.10 m`,
`h = 0.20 m`, struts modelled as PLA-density (1240 kg/m³) capsules of
`Ø12 mm`, nine cables with linear stiffness `k = 8 kN/m`, damping
`c = 5 N·s/m`, and rest length `= L0` (no pre-tension; cables act
unilaterally). Result on each engine:

| Metric                 | MuJoCo | PyBullet | PyChrono |
|------------------------|-------:|---------:|---------:|
| Total mass (kg)        | 0.106  | 0.103    | 0.103    |
| Settled COM z (m)      | 0.106  | 0.094    | 0.102    |
| Peak |COM accel| (g)   | 37.2   |  —       |  —       |
| Peak kinetic E (J)     | 1.04   | 0.95     | 1.01     |
| Peak strain E (J)      | 0.004  | 0.150    | 0.084    |

The kinetic-energy peaks all sit at ≈ `m·g·h ≈ 1 J`, which is the expected
upper bound for an undamped fall, confirming the three independent
implementations agree.

The 1-D `mujoco_sweep.py` then sweeps cable stiffness 0.5–50 kN/m and writes
`outputs/mujoco_sweep.csv` + `outputs/mujoco_sweep.png` — exactly the kind of
black-box objective evaluation a future BO loop will call. As expected, peak
deceleration is dominated by ground-contact stiffness in this minimal demo
and the cable-stiffness sweep is nearly flat (40 ± 1 g across two decades);
making the metric BO-meaningful will require also varying strut length,
prism height, drop height and softer/explicit ground compliance, plus
reporting an integrated metric such as `∫ a(t) dt` or jerk.

### 3D animations (offscreen renders)

`render_mujoco_drop.py` and `render_regimes.py` re-run the same MJCF
scenes through `mujoco.Renderer` (OSMesa offscreen) and write GIF + MP4
animations with the cables recoloured every frame by their tensile
strain (red = tensioned, blue = slack), so the videos visualise both
the rigid-body deformation on impact and the time-dependent cable
stress gradient.

`render_spotchecks.py` produces three sanity-check renders that should
be eyeballed first whenever the render pipeline is touched (per PR
comment 4427560261, the original `render_regimes.py` had penetration
and free-plate punch-through bugs that were obvious in motion but
hard to catch from time-series numbers alone): a single capsule drop,
a bare T-prism drop, then the prism + suspended payload.

| Scene | Output stem | Notes |
|---|---|---|
| 1 m drop, basic prism | `outputs/mujoco_drop.{gif,mp4}` | 60 fps, 1.5 s of sim, tracks COM. |
| Spot-check 1: single capsule | `outputs/spotcheck_capsule.{gif,mp4}` | Validates floor + camera + OSMesa. |
| Spot-check 2: bare T-prism | `outputs/spotcheck_bare_prism.{gif,mp4}` | Validates struts + tendons render with no penetration. |
| Spot-check 3: suspended payload | `outputs/spotcheck_suspended_plate.{gif,mp4}` | Validates the SUPERball-style internal-payload model used by `render_regimes.py`. |
| Crutch-tip regime | `outputs/regime_crutch_tip_drop.{gif,mp4}` | 75 kg payload suspended inside Ø 24 mm cell; dropped from rest at low height. |
| NASA-lander regime | `outputs/regime_nasa_lander_drop.{gif,mp4}` | 5 kg payload suspended inside Ø 200 mm cell; dropped from rest at low height. |

The two regime renders deliberately use a *visualisation-only* model
(see `build_render_xml` in `render_regimes.py`) that lifts the prism
clear of the floor and suspends the payload via 6 internal TPU tendons
(SUPERball / NASA TBR architecture, also used in `newton_drop.py`). For
*quantitative* metric extraction (peak g, pulse FWHM, SEA, BO sweep),
use `run_regimes.py` instead — it intentionally skips the free-fall by
starting at impact velocity to keep nsteps small.

Run via `MUJOCO_GL=osmesa python3 render_mujoco_drop.py` (or
`render_regimes.py` / `render_spotchecks.py`).  Requires
`imageio[ffmpeg]` for the MP4; the GIF falls back to Pillow.

## Application regimes (issues #18 / #14 / #16 / #28)

`regimes.py` defines two application-grade simulation envelopes informed
by the project's two target use-cases and constrained to the **Lansmont
M23** hardware envelope from issue #28 (peak ≤ 5,000 g, half-sine pulse
≥ 0.25 ms, ΔV ≤ 9.8 m/s, payload ≤ 36 kg):

| Regime | Source | Payload | ΔV | Cell size | Target peak | Target pulse |
|---|---|---:|---:|---:|---:|---:|
| `crutch_tip` | issue #18, follow-on tasks 39708fbc / 9832f01a / f21cf79c / 7a21d00e | 75 kg user¹ | 1.4 m/s | Ø 24 mm × 25 mm | ≤ 8 g hand-transmitted (HAVS) | ≥ 5 ms |
| `nasa_lander` | issues #14, #16; SUPERball, MER airbag, GSFC GEVS | 5 kg | 9.8 m/s (M23 max ΔV) | Ø 200 mm × 200 mm | ≤ 1500 g (GEVS) | ≥ 0.5 ms |

¹ The 75 kg user mass is correctly flagged by `assert_within_m23()` as
exceeding the M23's 36 kg payload limit; for benchtop validation a
proportionally reduced sample with a 30 kg surrogate mass would be used.

`run_regimes.py` drives the MuJoCo prism through both regimes and writes:

* `outputs/regime_<name>_timeseries.png` — payload acceleration, vertical
  velocity, and tendon strain energy vs. time for three illustrative
  cable-stiffness values (¼×, 1×, 4× the regime nominal).
* `outputs/regime_<name>_sweep.{png,csv}` — peak |a| (g) and specific
  energy absorbed (J/kg) over a 11-point geometric sweep of cable
  stiffness spanning ~3 decades.

### Result and physical interpretation

| Regime | Best-fit cable k (N/m) | Peak (g) | Pulse (ms) | SEA (J/kg) |
|---|---:|---:|---:|---:|
| `crutch_tip`  | 5,798  |  16.3 | 7.5 | ~0      |
| `nasa_lander` | 5,060  | 102.8 | 7.9 | 0.06    |

The NASA-lander 100 g / 8 ms pulse comfortably clears the GSFC GEVS 1500 g
shock spectrum; the crutch 16 g pulse is ~2× the 8 g HAVS-friendly
target, but only marginally cable-sensitive in this rigid-strut model.
Across the full stiffness sweep, **peak g is essentially flat (±2 %)
because in a rigid-strut + tendon model the impulse is set by floor
contact stiffness, not the cable network**, while **SEA varies ~10× with
cable stiffness** (especially in the NASA case). This is exactly the
limitation the Edison survey predicts for "Recommendation C" engines —
NTRT/MuJoCo rigid-strut models are good for topology screening but
cannot resolve TPU-mediated energy absorption. Crutch design and
quantitative SEA optimization motivate moving to Edison's Recommendation B
(DiffPD) or A (PolyFEM + IPC) for the next iteration.

## PLA strut + TPU "string" printable design (Bambu H2D)

The lab fabricates the unit cell on a Bambu Lab H2D (0.4 mm nozzle,
PLA + TPU 85A in IDEX, per #45), so cable stiffness is not a free abstract
parameter — it is set by the printable tendon diameter `d_t` and the
TPU 85A modulus:

```
k = E_TPU * pi * (d_t / 2)^2 / L     with E_TPU ≈ 12 MPa (85A secant)
```

`simulations/printable_design.py` exposes this and three companion
checks the operator needs *before* printing:

1. **Class-1 / true-tensegrity check.** A genuine Snelson tensegrity is
   *class-1* — no two struts touch.  In an FDM build with finite strut
   diameter `d_s` the constraint becomes `d_s < d_min(r, h, twist)`,
   the closest-approach distance between any two of the three struts.
   `PrintableDesign.is_class_1` returns the boolean and
   `class_1_margin_m` the signed margin.  Both regime defaults pass:
   crutch margin 10.9 mm, lander margin 103 mm.  If the margin goes
   negative the structure is *tensegrity-like* (some load bypasses the
   tendons through strut-strut contact) and the BO objective stops
   reflecting the design intent — `printable_sweep.py` filters those
   designs out of its Pareto fronts.
2. **H2D printability bounds.**  Tendon Ø ∈ [1.2, 6.0] mm (3-perimeter
   minimum at 0.4 mm nozzle … switch to multi-strand above); strut Ø
   ≥ 2.0 mm.
3. **TPU break-stress bound.**  `prestrain × E_TPU < σ_break (~30 MPa)`,
   so prestrain ≲ 50 % is mechanically allowed — but we cap the sweep
   at 8 % since beyond that the small-strain `k = EA/L` model breaks
   down (Mullins effect dominates).

`simulations/printable_sweep.py` then runs a 7 × 5 grid over (`d_t`,
`prestrain`) for each regime, holding strut diameter at the regime
default, and writes a heatmap of peak |a| (g) and SEA (J/kg) plus a
Pareto cloud of peak vs SEA coloured by tendon Ø.  Findings:

| Regime | Best class-1 design (peak ≤ target, max SEA)               |
|---|---|
| `crutch_tip`  | **None** in this rigid-strut model — the printable k range ~1.1–28 kN/m at the 25 mm strut length still leaves the rigid-prism floor-contact impulse > 8 g. Confirms the same Edison Rec C limitation: design needs DiffPD/IPC or a redesigned cell (e.g. an underlying TPU shell carrying the contact load). |
| `nasa_lander` | `d_t = 4.0 mm`, prestrain 0 % → peak 92 g, SEA 1.03 J/kg, well under the 1500 g GEVS target. Comfortably printable. |

The point of this driver is not the rigid-strut peak g (we already know
that's contact-pinned) — it is to expose the **printable / class-1 /
H2D-feasible region** of the BO search space so that whoever wires up
the actual BO loop next session does it on the right axes (`d_t`,
`prestrain`, strut Ø) instead of an abstract `k`, and so the sim
warns them when their proposed design is not a true tensegrity.

## Mid-fidelity escalation: Newton (Warp) — Edison Rec B / DiffPD-tier

Per @sgbaird-yolo's request to "attempt running DiffPD and PolyFEM+IPC",
we escalated from the rigid-strut engines above to **NVIDIA Newton**
(`pip install newton`, built on Warp). Newton stood in for **Edison
Recommendation B (DiffPD)** because:

* DiffPD itself (MIT GFX, SIGGRAPH 2021) is not on PyPI — only as a
  C++/Pangolin-based source repo whose CMake build fails on the lab's
  Linux runners (no GPU drivers, no Pangolin).
* Newton provides the same critical capabilities DiffPD was wanted for:
  rigid + particle + spring + soft-body **co-simulation with full
  bidirectional coupling** (tendons actually in the load path), a
  GPU-accelerated XPBD/VBD/Featherstone solver stack with soft contact,
  and **autodiff via Warp tapes** for future BO-gradient access.

`simulations/newton_drop.py` builds the same Snelson T-prism as an
all-particle network: 6 prism nodes (mass 5 g each), 1 payload node
(1 kg), 3 stiff PLA strut springs, 9 TPU-85A tendon springs, and
**6 internal TPU-85A tendons suspending the payload from every prism
node** (the SUPERball / NASA TBR architecture). The whole thing is
dropped 100 mm onto Newton's ground plane with a soft-contact pipeline
(`soft_contact_ke = 5e4`).

A 3-point tendon-Ø mini-sweep at the lander cell shows the cables are
now genuinely in the load path (peak g monotonically responds to the
TPU 85A tendon Ø, in contrast to the rigid-strut engines where peak g
was floor-pinned at ±2 % across three decades of `k`):

| Tendon Ø | Newton peak \|payload accel\| (g) |
|---:|---:|
| 1.5 mm | ~2,400 |
| 3.0 mm | ~4,200 |
| 5.0 mm | ~11,400 |

Absolute numbers are still high (over the M23 5,000 g envelope at the
stiff end) because TPU 85A is very soft (E ≈ 12 MPa) and the payload
can free-fall deep into the prism before the suspension tendons engage,
giving a rope-snap profile. Two refinements still pending for
quantitative crutch-tip BO:

1. Add tendon prestrain so the suspension is taut at rest (current
   model is slack; matches the "rest = L0" cross-engine convention but
   a real assembly is sewn under tension).
2. Replace the all-particle prism with rigid bodies for the PLA struts
   (Newton supports `add_body` + `add_shape_capsule`); this removes the
   numerical PLA-spring impedance and lets the cable-network
   compliance dominate the integration.

Both are mechanical refinements rather than tooling escalations; the
key tooling step — getting from rigid-strut Tier C to coupled-soft
Tier B — is delivered by `newton_drop.py`.

### Edison Rec A (PolyFEM + IPC) — built and smoke-tested

`pip install polyfempy` fails on the runner (the PyPI sdist is missing its
`CMakeLists.txt`), so we build the C++ binary directly from
`polyfem/polyfem`. CMake fetches Eigen, libigl, Catch2, ipc-toolkit,
suite-sparse, hypre, hdf5 and friends through CPM; the configure step takes
~3.5 min and the parallel build (`-j4`) takes ~25 min and produces a
~160 MB `PolyFEM_bin` (~10 GB build dir).

```bash
git clone --depth 1 https://github.com/polyfem/polyfem.git
mkdir -p polyfem/build && cd polyfem/build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4 PolyFEM_bin
# meshes used by the smoke test (cube.msh + plane.obj):
git clone --depth 1 https://github.com/polyfem/polyfem-data.git
export POLYFEM_BIN=$(pwd)/PolyFEM_bin
export POLYFEM_DATA_DIR=$(realpath ../../polyfem-data)
python simulations/polyfem_drop.py
```

`simulations/polyfem_drop.py` writes a small JSON describing a NeoHookean
TPU-85A cube (E = 12 MPa, ν = 0.45, ρ = 1200 kg/m³) of the crutch-tip
prism cell size, drops it onto the bundled `plane.obj` ground obstacle
through PolyFEM's IPC barrier-method contact (`dhat = 1e-4 m`), and shells
out to `PolyFEM_bin -j drop.json`. The script then walks the per-step
`step_*.vtm`/`step_*.vtu` outputs through `meshio` to recover the COM
trajectory and writes `outputs/polyfem_drop.{png,npz}`. End-to-end runtime
on a 4-core x86_64 runner is ~3 min for 120 ms of simulated time.

#### T-prism geometry (`--geometry tprism`) — PLA struts + TPU 85A tendons

`simulations/tprism_mesh.py` uses gmsh's OCC kernel to build the actual
3-bar Snelson T-prism as three Ø3 mm PLA strut cylinders plus nine
Ø1.5 mm TPU 85A tendon cylinders connecting the canonical strut endpoints.
Each tendon is shortened by ~60 % of the strut diameter at each end so its
side wall fuses with the strut side wall (rather than coinciding with the
strut endcap, which trips a tetgen PLC error); `gmsh.model.occ.fragment`
then splits the overlap into shared-face sub-volumes. The resulting Gmsh
4.1 `.msh` carries two physical-volume groups (`1 = PLA_strut`,
`2 = TPU_tendon`) which PolyFEM picks up to apply per-element NeoHookean
materials (PLA E = 3.5 GPa, ρ = 1240; TPU 85A E = 12 MPa, ρ = 1200). Then
the same IPC barrier-method contact handles strut–floor and strut–strut
interactions in the same run:

```bash
python simulations/polyfem_drop.py --geometry tprism
# writes outputs/polyfem_drop_tprism.{png,npz}
```

Mesh stats at default settings: ~5.5 k tets, 15 PLA sub-volumes + 9 TPU
sub-volumes, drop time ~40 ms simulated.

Compared to the rigid-strut MuJoCo / PyBullet / PyChrono engines and the
particle-spring Newton stand-in, this gives the project the IPC-grade
contact response (intersection-free, penalty-free, friction-coupled)
needed for credible peak-g predictions at the prism-floor and
inter-strand interfaces — Edison Recommendation A's headline capability.

The original `pip install polyfempy` failure mode (kept for the next agent
who tries the PyPI wheel route):

```bash
$ pip install polyfempy
...
CMake Error: The source directory ".../polyfempy_..." does not appear to
contain CMakeLists.txt.
ERROR: Could not build wheels for polyfempy
```

### Edison Rec B (DiffPD) — built and smoke-tested

DiffPD (Du et al., SIGGRAPH 2021) is not on PyPI, only as the
`mit-gfx/diff_pd_public` C++/SWIG repo. The README warns about Pangolin /
OpenGL, but those are only needed by the bundled `pbrt-v3` *renderer*; the
projective-dynamics solver itself builds fine headless:

```bash
git clone --recursive https://github.com/mit-gfx/diff_pd_public.git
cd diff_pd_public/cpp/core/src && swig -c++ -python py_diff_pd_core.i
cd ../../ && mkdir -p build && cd build && cmake -DPARDISO_AVAILABLE=OFF .. && make -j4
cd .. && mv core/src/py_diff_pd_core.py ../python/py_diff_pd/core/
mv build/libpy_diff_pd_core.so ../python/py_diff_pd/core/_py_diff_pd_core.so
printf "root_path = '$(pwd)/..'\n" > ../python/py_diff_pd/common/project_path.py
export PYTHONPATH=$(pwd)/../python:$PYTHONPATH
python -c "import py_diff_pd.common.common"   # smoke-import
python <repo>/simulations/diffpd_drop.py
```

`simulations/diffpd_drop.py` drops a TPU-85A NeoHookean (corotated +
volume) hex cube of the crutch-tip cell size onto a planar frictional
boundary and reads back the COM trajectory through DiffPD's `PyForward`
(`pd_eigen` solver, BFGS line search). DiffPD predates NumPy 2.0
(`np.int` removed); the script monkey-patches that back at import time.

## Other notable simulators (not yet downloaded)

These came up in the literature scan and the Edison query but were not
installed in this session because they require either a build-from-source
(NTRT, SOFA, IPC), a license (ANSYS, Abaqus, COMSOL) or a much larger
ecosystem (Genesis, Warp, Brax, MJX). They are good candidates for a follow-up
session:

- **NTRTsim** — NASA Tensegrity Robotics Toolkit (C++/Bullet). Tensegrity-
  specific helpers but unmaintained since ~2019.
- **MoSeS / SuperBall** simulator — UC Berkeley fork of NTRT for the SuperBall
  rover.
- **SOFA Framework** — interactive multi-physics, supports cables and FEM.
- **Codim-IPC** / **C-IPC** — penalty-free, intersection-free contact for
  cable nets.
- **TsgFEM** (Bilkent) — MATLAB form-finding + dynamics.
- **DiffPD / JaxFEM / Warp / Brax / MJX / Genesis** — differentiable physics
  for gradient-based design (complementary to BO; could provide adjoints for
  multifidelity).
- **FEniCSx / COMSOL / ANSYS / Abaqus** — high-fidelity continuum FEM with
  hyperelastic TPU and explicit dynamics for impact.

## Edison query

A high-effort `JobNames.LITERATURE` task was submitted asking for an
in-depth, citation-rich survey of state-of-the-art tensegrity simulation
methods (formulation, license, large-deformation / hyperelastic / contact
support, Python bindings, validation, recommendations for our BO workflow).

- **task_id**: `782657e0-0818-4755-9e18-60c8039b2ccd`
- **status**: *success* (fetched 2026-05-08 18:36 UTC)
- **response**: [`edison-trajectories/2026-05-08-sim-survey-782657e0.md`](../edison-trajectories/2026-05-08-sim-survey-782657e0.md) (~50 kB; 26 references with DOIs)
- **structured dump**: [`edison-trajectories/2026-05-08-sim-survey-782657e0.json`](../edison-trajectories/2026-05-08-sim-survey-782657e0.json)

The survey's three-tier multi-fidelity stack recommendation
(IPC-based FEM ⇄ DiffPD ⇄ NTRT/MuJoCo rigid-strut) directly motivates
the layered approach already exercised here at the lowest tier and
reflected in `regimes.py`.
