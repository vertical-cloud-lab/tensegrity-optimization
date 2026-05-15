# Instron Stiffness Testing — Edison Trajectories

Edison Scientific (FutureHouse) literature-search outputs supporting issue
**#49 — Run initial Instron tests for stiffness testing**.

## Files

| File | Purpose |
| ---- | ------- |
| `SUBMITTED.json` | *(absent once fetched)* Placeholder written when a task is submitted but not yet fetched in the same session. |
| `instron-stiffness-<task_id>.md` | Human-readable Edison brief: 8-objective plan + three structured artifacts (standards comparison table, first-test protocol checklist, published-analogs table). |
| `instron-stiffness-<task_id>.json` | Full raw `TaskResponseVerbose` dump (status, agent trace, references). ~2 MB. |
| `instron-stiffness-<task_id>.references.bib` | 81 unique BibTeX entries auto-extracted from the agent trajectory, ready for inclusion in the project bibliography. |

## Headline findings (issue #49 — first-round Instron stiffness tests)

The Edison `LITERATURE_HIGH` task `9f68e71e-c552-4333-aa5c-37de18c8eefd`
returned a 122 KB technical brief.  Recommended **citation stack** for
the first paper out of this campaign:

> ASTM D638 (PETG/PLA tensile coupons) + ASTM D412 (TPU 85A tensile
> coupons) + **ASTM D1621 *or* ASTM C365 (adapted, with deviations
> disclosed)** for compression of unit cells / tiled lattices +
> **ASTM E111** for modulus extraction (toe correction, tangent vs.
> chord) + **ASTM F2971** + **ISO/ASTM 52900 / 52921** for AM specimen
> reporting; mention **ISO 527 / ISO 37 / ISO 604 / ISO 13314** as
> recognized alternatives.

Other key recommendations for the *first* test, paraphrased from
Artifact 2 (protocol checklist) and Artifact 3 (analogs):

* Run a **machine-compliance calibration** (steel-on-steel platen-only
  curve) and subtract from specimen displacement before reporting any
  tendon-dominated stiffness.
* Use a **non-contact extensometer / DIC** rather than crosshead
  displacement at sub-mm compliance — closely matches the Bauer 2021,
  Pahari 2024 and Bates 2016 analogs.
* For **TPU 85A** tendons: **5–10 preconditioning cycles at the planned
  test strain** (Mullins-effect equilibration), report any humidity
  conditioning, and quote **secant** modulus over a clearly stated
  strain window rather than tangent.
* Bound the *first* monotonic loading to **well below densification**
  (target ≤30 % nominal strain or a force ceiling that protects the
  joint); reserve full load-to-densification for the later
  energy-absorption campaign.
* Adopt a **Gibson–Ashby non-dimensional reporting frame**
  (E*/E_s, ρ*/ρ_s) so single-cell and 2×2×2 tiled results are
  comparable.
* Capture **build orientation, raster, layer height, nozzle/bed temps,
  cooling, retraction, and feedstock lot** per ASTM F2971 in the
  per-specimen metadata schema (recommended fields are itemized in
  Artifact 2 and are designed to feed directly into the BoTorch/Ax
  surrogate).
* Include a **PETG–TPU joint-slip diagnostic** (DIC strain field on the
  joint, or load-drop signature analysis) so that interface failure is
  not mis-recorded as material non-linearity — this is currently an
  *open* peer-reviewed-data gap for PETG–TPU and it must be quantified
  in-house.
* Use an **ASTM E4-class load cell** sized close to the expected
  range; the lab's 5 kN cell is likely *over-ranged* for ~5–30 g
  tensegrity cells in the small-strain regime — borrow / order a
  **100 N–500 N** cell for stiffness tests and reserve the 5 kN cell
  for densification / impact follow-ups.

See the `*.md` brief for the full standards comparison table, full
checklist, all 12 published analogs (Bauer 2021, Pajunen 2019,
Sabouni-Zawadzka 2024, Bates 2016, Solyaev 2023, Raghavendra 2021,
Maskery 2015, Habib 2024, Pahari 2024, Lee 2020, Rossiter 2020,
Arifvianto 2022), and the eight "open questions before the first test"
items.

## Submission script

`scripts/edison/submit_instron_stiffness.py` submits a single
`LITERATURE_HIGH` task and polls for up to ~28 min for completion. If the
task is still in progress when the polling deadline is hit, only
`SUBMITTED.json` is left on disk and a follow-up session can re-run the
script (or call `EdisonClient.get_task(task_id, verbose=True)`) to fetch
the final answer.

The query asks specifically for:

1. Applicable ASTM / ISO / AM-specific standards for stiffness
   characterization of FFF-printed PETG/PLA + TPU 85A
   tensegrity-inspired unit cells.
2. Best-practice protocol (crosshead speed, machine compliance, platen
   choice, preconditioning, Mullins effect, stiffness definition,
   replicates).
3. A concrete first-test checklist for the undergraduate running the
   Instron, plus a metadata schema compatible with our downstream BO loop.
4. How a stiffness-only campaign should differ from the later
   energy-absorption campaign.
5. Multi-material FFF-specific data-quality considerations (build
   orientation, joint slippage, dimensional QA).
6. 5–15 closest published analogs with DOIs.
7. Equipment-specific load-cell / DAQ guidance.
