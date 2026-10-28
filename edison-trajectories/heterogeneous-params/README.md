# Heterogeneous (per-member) BO parameter axes — Edison literature trajectory

Source: PR #24 comment
[4520542433](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/24#issuecomment-4520542433)
(sgbaird relaying @me-madsen):

> noting that we could also allow for diameters of individual struts/cables
> to vary, rather than assuming a fixed diameter. Similar for other
> parameters perhaps. Mostly thinking in context of #35 right now

PR #35 currently sweeps a single `strut_d_mm` and a single `cable_d_mm` per
T3-prism specimen (all 3 struts and all 9 cables tied to one diameter each).
The proposal is to expand selected scalar parameters into vector / per-member
parameters — taking the per-specimen design vector from ~5-D to O(12-30+) D.

## Trajectory

| File | Notes |
| --- | --- |
| `heterogeneous-params-5191cf4d-873a-4e3e-9077-9565a2602ba1.md` | Verbatim `formatted_answer` from Edison `LITERATURE_HIGH` task `5191cf4d-873a-4e3e-9077-9565a2602ba1` (job: `LITERATURE_HIGH`, status: `success`). 466 lines covering (a) precedent in Skelton/Nagase/Goyal/Zegard/Pajunen/Xu/Zhang minimal-mass tensegrity sizing, (b) form-finding / bistability / energy-absorption implications under D3 symmetry, (c) FFF manufacturability on Bambu H2D, (d) high-dim BO methodology (SAASBO, TuRBO, ALEBO, additive GPs, hierarchical search spaces, equivariant GPs, MTGP), (e) symmetry exploitation under C3/D3, (f) numeric recommendations + Ax/BoTorch recipe, (g) ranked failure modes, (h) numbered references. |
| `heterogeneous-params-5191cf4d-873a-4e3e-9077-9565a2602ba1.json` | Full structured `model_dump_json` for reproducibility. |
| `../../scripts/edison/submit_heterogeneous_params.py` | Idempotent submission + polling driver (reads `EDISON_PLATFORM_API_KEY` or mirrors `EDISON_API_KEY`; uses `client.get_task(task_id=...)` polling; writes a `-SUBMITTED.json` placeholder so a follow-up session can resume on wall-clock timeout). |

## Headline recommendation (Edison §f)

For the first heterogeneous PR #35 follow-on batch on a single T3-prism:

- **Keep scalar:** `R_mm`, `H_mm`, `twist_deg`, infill %.
- **Expand to per-orbit (not per-member)** the strut and cable diameters,
  exploiting the T3-prism `C3 → D3` symmetry that decomposes the 9 cables
  into 3 orbits (saddle / top / bottom triangles): one `strut_orbit_d_mm`
  continuous axis ∈ [3.5, 9.0] mm + three `cable_orbit_d_mm` categorical
  axes ∈ {1.2, 1.8, 2.4, 3.0, 4.5} mm (FFF-resolvable bins on a 0.4 mm
  nozzle, per Tuncel 2024 dimensional-accuracy data).
- **Expand to fully per-member** only the per-cable prestress fraction
  simplex (sum = 1), per Skelton's minimal-mass prestress optimization
  (Nagase & Skelton 2014; Goyal, Skelton & Peraza Hernandez 2020).
- **BO engine:** SAASBO for ≤25-D campaigns (Eriksson & Jankowiak 2021),
  escalate to TuRBO + qNEHVI for tilings that push into O(100+) D
  (Eriksson 2019; Daulton 2020). Initialize with stratified Sobol (≥3
  specimens per topology family / orbit configuration).
- **Symmetry handling:** hard-enforce orbit symmetry as the default
  search space (Approach (i) in §e); only relax to per-member axes if
  the symmetric Pareto front is exhausted, since the lab budget is
  50–100 specimens.

## Cross-references

- PR #24 hierarchical search space synthesis:
  [`../tpu-petg-bo-variables-additions-from-pr22.md`](../tpu-petg-bo-variables-additions-from-pr22.md)
  §D recasts the topology axes as an Ax `HierarchicalSearchSpace` per
  [facebook/Ax#140](https://github.com/facebook/Ax/issues/140). This per-member
  expansion nests one level *below* that hierarchy — inside any chosen
  `topology_family` branch, selected scalar parameters expand into
  per-orbit / per-member vector parameters.
- PR #35 (`bo/t3_prism_sobol_batch.py`) is the concrete target for the
  Edison §f recipe.
- PR #33 sim-ladder (MuJoCo → Newton/Warp XPBD → PolyFEM+IPC / DiffPD) is
  the recommended host for the MTGP / multifidelity escalation discussed
  in Edison §d.
