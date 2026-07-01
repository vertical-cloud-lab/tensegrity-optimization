# Edison Scientific trajectories — crutch-tip impact-absorber exploration

This directory archives the full responses ("trajectories") from non-blocking
Edison Scientific `LITERATURE_HIGH` queries that informed the
crutch-tip impact-absorber use-case for the multi-material 3D-printed
tensegrity (TPU + PETG) energy-absorption framework.

For each task we commit two artifacts:

- **`*.md`** — human-readable trajectory containing Edison's verbatim
  `formatted_answer`: the original Question, the cited Answer, and the
  full numbered References list.
- **`*.json`** — full `model_dump_json()` of the `PQATaskResponse` object
  (status, query, answer, formatted_answer, job_name, created_at,
  task_id, share_status, etc.) for reproducibility / programmatic reuse.

| # | Files | Task ID | Status | Edison link |
|---|-------|---------|--------|-------------|
| 1 | [`01-tensegrity-crutch-tip-feasibility.md`](01-tensegrity-crutch-tip-feasibility.md) / [`.json`](01-tensegrity-crutch-tip-feasibility.json) | `39708fbc-5964-4fb5-a042-9b13b3475d40` | success | https://platform.edisonscientific.com/tasks/39708fbc-5964-4fb5-a042-9b13b3475d40 |
| 2 | [`02-medical-motivation-and-prior-art-beyond-tensegrity.md`](02-medical-motivation-and-prior-art-beyond-tensegrity.md) / [`.json`](02-medical-motivation-and-prior-art-beyond-tensegrity.json) | `9832f01a-6bb9-4488-bd88-3131d915f96a` | success | https://platform.edisonscientific.com/tasks/9832f01a-6bb9-4488-bd88-3131d915f96a |
| 3 | [`03-vibration-economic-burden-slip-resistance.md`](03-vibration-economic-burden-slip-resistance.md) / [`.json`](03-vibration-economic-burden-slip-resistance.json) | `f21cf79c-beb1-4a7b-aafe-67603b272c25` | success | https://platform.edisonscientific.com/tasks/f21cf79c-beb1-4a7b-aafe-67603b272c25 |
| 4 | [`04-tpu-petg-engineering-and-bayesian-optimization.md`](04-tpu-petg-engineering-and-bayesian-optimization.md) / [`.json`](04-tpu-petg-engineering-and-bayesian-optimization.json) | `7a21d00e-6fe8-409f-b05d-4b581cc4fa15` | success | https://platform.edisonscientific.com/tasks/7a21d00e-6fe8-409f-b05d-4b581cc4fa15 |
| 5 | [`05-industry-partners-and-commercialization.md`](05-industry-partners-and-commercialization.md) | `c18a2313-1359-4f77-ac82-d8551d1fa8e1` | in progress — placeholder, refresh next session | https://platform.edisonscientific.com/tasks/c18a2313-1359-4f77-ac82-d8551d1fa8e1 |
| 6 | [`06-abstract-feedback.md`](06-abstract-feedback.md) / [`.json`](06-abstract-feedback.json) | `74ac013b-8ce9-41ab-89ce-13c3e6f5ad33` | success | https://platform.edisonscientific.com/tasks/74ac013b-8ce9-41ab-89ce-13c3e6f5ad33 |

To re-fetch / refresh any trajectory:

```python
import json, os
from edison_client import EdisonClient

c = EdisonClient(api_key=os.environ["EDISON_API_KEY"])
t = c.get_task("<task_id>")

# Human-readable trajectory (Question + Answer + References):
print(t.formatted_answer)

# Full structured response:
print(json.dumps(json.loads(t.model_dump_json()), indent=2, default=str))
```
