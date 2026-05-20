# T3-prism Bayesian-optimization batch generator

Single-iteration, **human-in-the-loop** first batch of T3-prism specimens
for the lab's BO campaign — issued in response to PR #35 comment
[`4503109338`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4503109338)
from @sgbaird.

This script is a *restricted* adaptation of the full multi-topology BO
scaffold on
[`copilot/scaffold-bayesian-optimization-script`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/copilot/scaffold-bayesian-optimization-script/bo/tensegrity_campaign.py)
(PR #30 / PR #24). The full scaffold sweeps every topology, tiling,
material pairing, and build orientation in the project's Edison-curated
literature table; this script freezes everything that isn't specific to
the **T3-prism** geometry, because the team has only confirmed printability
for T3-prisms so far (PRs #16 / #30 / #24 / #35).

## What's swept

| Variable      | Range          | Maps to `cad/t3-prism/t3-prism.scad` |
| ------------- | -------------- | ------------------------------------ |
| `R_mm`        | [25.0, 40.0]   | `R_base` (radius of each end cap)    |
| `H_mm`        | [60.0, 110.0]  | `H_base` (height between caps)       |
| `twist_deg`   | [40, 80]       | `twist`                              |
| `strut_d_mm`  | [6.0, 12.0]    | `strut_d_base` (PLA strut Ø)         |
| `cable_d_mm`  | [3.0, 5.5]     | `cable_d_base` (TPU cable Ø)         |

All five are continuous (`type: range`) so the Sobol sequence covers them
uniformly. The cable diameter lower bound of 3 mm is the empirical "Bambu
auto-support threshold" from PR #35 — below it the top-triangle TPU
bridges fail mid-print (the `cable_d = 2.4 mm` spaghetti event diagnosed
by Edison ANALYSIS `25c1c897`).

## What's frozen (and why)

| Variable             | Value             | Reason |
| -------------------- | ----------------- | ------ |
| `topology`           | `t3_prism`        | Only printable family so far |
| `tiling`             | `1x1x1`           | Single unit cell |
| `struts_per_cell`    | `3`               | T3 by definition |
| `build_orientation`  | `vertical`        | Per comment: "maximize the number on the build plate" |
| `tpu_shore`          | `85A`             | NinjaFlex-class lab default |
| `strut_material`     | `PLA` (extruder 1)| Production target on this branch |
| `cable_material`     | `TPU` (extruder 2)| Production target on this branch |
| `supports`           | `manual_painted`  | Per comment: "@achris0520 will manually paint on supports" |
| `joint_d_mm`         | `7.0`             | t3-prism.scad default; held constant so vertex topology is comparable across specimens |

The slicer-side modeled-in PLA scaffold pillars from PR #35 commit
`5437366` are **not** emitted here — they were a workaround for the
slicer's auto-support gap on near-vertical TPU cables, and Audrey's
painted-supports approach in PR #35 comments `4502140147` /
`4502171087` supersedes them.

## How to run

```bash
pip install ax-platform numpy
sudo apt-get install -y openscad xvfb
python3 bo/t3_prism_sobol_batch.py        # default n=9, seed=0
```

Knobs:

* `--n N` — number of specimens (default `9`, packed `3×3` on the
  350×320 mm H2D plate)
* `--seed S` — Sobol seed (default `0`; bump to regenerate)
* `--skip-render` — skip the OpenSCAD STL/PNG passes (CI smoke test)

## Outputs (next to this script)

* `t3-prism-bo-batch.csv`        — design table (one row per specimen)
* `t3-prism-bo-batch.json`       — same data plus plate-layout metadata
* `t3-prism-bo-batch.scad`       — generated OpenSCAD wrapper that unions
  all specimens onto a centred grid on the H2D plate
* `t3-prism-bo-batch.stl`        — packed STL (drag into Bambu Studio,
  paint supports, slice plate, send to printer)
* `t3-prism-bo-batch-plate.png`  — top-down build-plate preview
* `t3-prism-bo-batch-iso.png`    — iso preview

## Reporting outcomes back

This first batch deliberately **does not** call `complete_trial(...)`.
The full closed-loop campaign lives in
[`bo/tensegrity_campaign.py`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/copilot/scaffold-bayesian-optimization-script/bo/tensegrity_campaign.py)
on the `copilot/scaffold-bayesian-optimization-script` branch; once
measured F_peak / SEA / η land for these nine specimens, hand them to the
closed-loop campaign as already-observed Sobol trials before requesting
the first model-based batch.
