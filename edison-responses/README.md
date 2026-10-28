# Edison Scientific responses

Verbatim responses from [Edison Scientific](https://edisonscientific.com/)
(formerly FutureHouse) literature / analysis / precedent / molecule queries
submitted from this repository.

For each query we commit two files with matching basenames:

- `<date>-<topic>-<job>-<task-id-prefix>.md` — verbatim `formatted_answer`
  (Question + cited Answer + numbered References) prepended with a short
  metadata header (task ID, job name, submitted/fetched dates, status, related
  issues).
- `<date>-<topic>-<job>-<task-id-prefix>.json` — full structured task object
  (`task.model_dump_json()`) for reproducibility (raw `answer`,
  `answer_reasoning`, cost, cited sources, etc.).

## Index

| Date | Job | Topic | Related issues | Files |
| --- | --- | --- | --- | --- |
| 2026-05-09 | `LITERATURE` | Funding venues for a larger-scale grant proposal — initial scoping | [#42](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/42), [#16](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/16), [#18](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/18) | [.md](2026-05-09-funding-venues-literature-ff9cb91e.md) / [.json](2026-05-09-funding-venues-literature-ff9cb91e.json) |
| 2026-05-09 | `LITERATURE_HIGH` | Funding venues — agency-by-agency follow-up (NSF/DOE/NIH/DoD/NASA/DOT/NIST + prior-award table) | [#42](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/42) | [.md](2026-05-09-funding-venues-literature-high-5c3afc89.md) / [.json](2026-05-09-funding-venues-literature-high-5c3afc89.json) |
| 2026-05-09 | `LITERATURE_HIGH` | Named program officers + contact info / outreach norms for the shortlisted venues (NSF CMMI / DMREF / Convergence Accelerator, NASA NIAC / STMD, NIH NIBIB / NCMRR / NIA / NIOSH, DARPA YFA + DSO, ARO / ONR / AFOSR YIP + portfolios, CDMRP, DOT / NIST / FDA, Sloan) | [#42](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/42) | [.md](2026-05-09-funding-program-officers-literature-high-c668cd19.md) / [.json](2026-05-09-funding-program-officers-literature-high-c668cd19.json) |

Older Edison runs from sibling branches / PRs (NASA priorities tie-in, project
naming, TPU+PETG variables, sim-survey, crutch-tip prior art, etc.) are
catalogued in their respective PRs and will be merged into this index as they
land on `main`.

## Re-running / fetching

Edison tasks are submitted with `JobNames.LITERATURE` (≈10 min) or
`JobNames.LITERATURE_HIGH` (≈20–40 min) and are non-blocking. The repository
convention is:

```python
from edison_client import EdisonClient, JobNames
client = EdisonClient()
task_id = client.create_task({"name": JobNames.LITERATURE_HIGH, "query": "..."})
# ... later (same or different session) ...
t = client.get_task(task_id)
(p / f"{date}-<topic>-<job>-{task_id[:8]}.md").write_text(header + t.formatted_answer)
(p / f"{date}-<topic>-<job>-{task_id[:8]}.json").write_text(t.model_dump_json(indent=2))
```

The Edison API key is read from the `EDISON_PLATFORM_API_KEY` environment
variable (note: `edison-client` 0.12.0 does **not** read `EDISON_API_KEY` — set
`EDISON_PLATFORM_API_KEY="$EDISON_API_KEY"` if your secret is named the latter
way).
