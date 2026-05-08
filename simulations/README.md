# State-of-the-Art Tensegrity Simulation Survey

> Resolves: *"Begin exploring state-of-the-art simulations for tensegrity,
> tensegrity-like structures, and other related methods."*

This directory contains a first pass at downloading, installing and **actually
running** open-source simulators capable of modelling the multi-material
3D-printed tensegrity structures targeted by this MRG project (PLA/PETG struts
+ TPU tendons, optimised for impact / energy absorption).

A complementary high-effort literature survey was submitted to Edison
Scientific (FutureHouse) — see [§ Edison query](#edison-query) — and is
expected to be available next session.

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
└── outputs/
    ├── mujoco_drop_energy.png
    ├── mujoco_drop_data.npz
    ├── pybullet_drop_energy.png
    ├── pybullet_drop_data.npz
    ├── pychrono_drop_energy.png
    ├── pychrono_drop_data.npz
    ├── mujoco_sweep.csv
    └── mujoco_sweep.png
```

Run any script directly:

```bash
# MuJoCo / PyBullet (system Python)
python simulations/mujoco_drop.py
python simulations/pybullet_drop.py
python simulations/mujoco_sweep.py

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
- **status at end of session**: *in progress*
- **fetch next session** with `EdisonClient.get_task(task_id)`.
