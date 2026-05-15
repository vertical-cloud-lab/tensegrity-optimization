# Instron Stiffness Testing — Edison Trajectories

Edison Scientific (FutureHouse) literature-search outputs supporting issue
**#49 — Run initial Instron tests for stiffness testing**.

## Files

| File | Purpose |
| ---- | ------- |
| `SUBMITTED.json` | Placeholder written when a task is submitted but not yet fetched in the same session. Contains `task_id`, `job_name`, submission timestamp, and the full query text. Removed automatically once the answer is fetched. |
| `instron-stiffness-<task_id>.md` | Human-readable Edison answer (formatted markdown with inline citations). |
| `instron-stiffness-<task_id>.json` | Full raw `TaskResponseVerbose` dump (status, agent trace, references). |

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
