# Bayesian Optimization Scaffold

This directory hosts the Bayesian-optimization (BO) code for the
tensegrity-energy-absorption campaign described in `proposal.tex`. It is the
starting point that issue *“Scaffold the Bayesian optimization script based on
honegumi”* asked for.

The scaffold is **generated**, not hand-written, by the
[honegumi](https://honegumi.readthedocs.io/en/latest/) (骨組み, "skeleton")
package — a configurable starter-script generator for
[Ax](https://ax.dev/) / [BoTorch](https://botorch.org/). Picking the right
combination of honegumi options gives us a runnable, MOO + categorical +
existing-data + batch-evaluation BO loop tailored to the experimental cadence
of the project.

## Layout

| File | Purpose |
|------|---------|
| [`generate_scaffold.py`](generate_scaffold.py) | Wraps the `honegumi` Python API, declares our `CONFIG`, and writes `tensegrity_bo.py`. |
| [`tensegrity_bo.py`](tensegrity_bo.py) | **Generated** Ax/BoTorch BO loop. Has a Branin-style placeholder objective that must be replaced with the experimental energy-absorption measurement (see *Customization* below). |
| [`requirements.txt`](requirements.txt) | Pinned dependency set verified to render and run the scaffold without errors. |
| [`tests/test_generate_scaffold.py`](tests/test_generate_scaffold.py) | Smoke test that re-renders the script via honegumi and checks for the key sections. |

## Quick start

```bash
# 1. Install the pinned BO stack into a fresh environment
pip install -r bo/requirements.txt

# 2. Re-generate the scaffold (only needed if you change CONFIG or honegumi)
python bo/generate_scaffold.py

# 3. Verify the generated script runs end-to-end (≈ a few minutes; uses the
#    Branin placeholder objective so no experimental data is needed)
MPLBACKEND=Agg python bo/tensegrity_bo.py

# 3b. Faster verification: render and run a short variant (≈ 5 BO iterations)
python bo/generate_scaffold.py --smoke-test -o /tmp/smoke.py
MPLBACKEND=Agg python /tmp/smoke.py
```

## Honegumi configuration

`CONFIG` in `generate_scaffold.py` mirrors the toggles exposed at
<https://honegumi.readthedocs.io/en/latest/> and is currently set to:

| Option | Value | Why |
|--------|-------|-----|
| `objective` | `Multi` | Two competing goals: minimize peak transmitted force, maximize specific energy absorption (SEA). |
| `model` | `Default` | Ax's modular BoTorch GP — robust starting point. Switch to `Fully Bayesian` (SAASBO) once we have ≳ 30 high-dimensional observations. |
| `task` | `Single` | One physical experiment to start. Multi-task can re-enable cross-rig / cross-material transfer learning later. |
| `categorical` | `True` | Encodes a discrete knob such as base unit-cell topology (3-bar prism, octahedron, …) or TPU shore (85A/95A) — see PR #24. |
| `custom_threshold` | `True` | Ref-point thresholds for the MOO hypervolume objective so designs that fall outside acceptable bounds are penalised. |
| `existing_data` | `True` | Seeds the optimizer with previously measured / pilot designs. |
| `synchrony` | `Batch` | Matches the print-then-test batch cadence of an undergrad lab. |
| `visualize` | `True` | Writes the trace + Pareto-front plots that we will include in reports. |
| `*_constraint` | `False` | Off by default to keep the starter readable; flip `composition_constraint=True` if we move to mole-fraction-style design variables. |

Edit `CONFIG`, re-run `python bo/generate_scaffold.py`, and commit the
re-rendered `tensegrity_bo.py` together with the config change.

## Customization checklist

The generated script is intentionally a **scaffold** — the objective and
search space are honegumi's Branin demo. Once the experimental work begins,
replace the highlighted blocks in `tensegrity_bo.py`:

- [ ] Replace `obj1_name` / `obj2_name` with `peak_force` and `sea`
      (specific energy absorption).
- [ ] Replace `branin_moo(...)` with a function that either (a) returns the
      measured outcomes for a fabricated specimen or (b) calls a finite-element
      / surrogate model.
- [ ] Update the `parameters=[...]` block in `ax_client.create_experiment`
      with the design variables and bounds chosen in PR #24
      (strut L/D, prestress, TPU infill %, layer height, unit-cell topology …).
- [ ] Update the `ObjectiveProperties` thresholds with sensible reference
      values from the literature pulled by Edison.
- [ ] Replace the synthetic `X_train` rows with pilot-batch measurements when
      they become available.

These changes are deliberately *not* automated by `generate_scaffold.py`
because they depend on experimental decisions that should be reviewed in PR.

## Tutorial coverage

The picked configuration exercises the following honegumi tutorials/concepts
(see <https://honegumi.readthedocs.io/en/latest/curriculum/concepts/>):

* SOBO vs. MOBO (multi-objective)
* Single- vs. multi-task
* Custom thresholds for MOO
* Existing-data warm-start
* Single vs. batch evaluation
* Visualization of optimization traces / Pareto fronts

Other tutorials (sum / order / linear / composition constraints, fully
Bayesian / SAASBO, multi-fidelity) remain available as additional `CONFIG`
toggles and should be enabled as the campaign matures.
