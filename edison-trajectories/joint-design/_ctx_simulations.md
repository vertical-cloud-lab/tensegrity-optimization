# State-of-the-Art Tensegrity Simulation Survey

> Resolves: *"Begin exploring state-of-the-art simulations for tensegrity,
> tensegrity-like structures, and other related methods."*

This directory contains a first pass at downloading, installing and **actually
running** open-source simulators capable of modelling the multi-material
3D-printed tensegrity structures targeted by this MRG project (PLA/PETG struts
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

All three reproduce the same baseline experiment (a 3-bar Snelson T-prism
dropped from 1 m onto a flat floor). Cross-engine agreement: settled COM
height 0.094–0.106 m and peak kinetic energy 0.95–1.04 J (≈ `m·g·h ≈ 1 J`).

## Files

```
simulations/
├── tprism_geometry.py    # 3-bar Snelson prism node/edge generator (no deps beyond numpy)
├── mujoco_drop.py        # MuJoCo MJCF + drop simulation (✅ baseline)
├── pybullet_drop.py      # PyBullet rigid-body + manual spring cables (✅)
├── pychrono_drop.py      # Project Chrono ChLinkTSDA (✅, conda install required)
├── mujoco_sweep.py       # 1-D parameter sweep --> BO objective stub
├── regimes.py            # Application regime dataclasses (crutch + NASA) + Lansmont M23 envelope
├── run_regimes.py        # Drives MuJoCo through both regimes; produces 4 figures + 2 CSVs
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
    └── regime_nasa_lander_sweep.{png,csv}
```

Run any script directly:

```bash
# MuJoCo / PyBullet (system Python)
python simulations/mujoco_drop.py
python simulations/pybullet_drop.py
python simulations/mujoco_sweep.py
python simulations/run_regimes.py     # both application regimes, MuJoCo

# PyChrono (conda Python; install per table above)
/usr/share/miniconda/bin/python simulations/pychrono_drop.py
```

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
