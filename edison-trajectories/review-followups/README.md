# PR #20 review follow-up Edison queries

Two `LITERATURE_HIGH` tasks submitted in response to the PR #20 manuscript
review (`manuscript/manuscript-body.tex`), via
`scripts/edison/submit_review_followups.py`. Both were submitted non-blocking;
fetch the results and commit the verbatim trajectories
(`<slug>-<task_id>.md` + `.json`) here, then fold the findings into the draft.

| Slug | Review thread | Task ID |
|------|---------------|---------|
| `t4-citation-classification` | Are `ye2023multimaterial` / `khatri2024energy` actually "tensegrity-inspired" or just related? (manuscript-body.tex ~L171) | `4ba95a0f-2263-40a5-8c8c-b5da2c550dcb` |
| `t26-sea-impact-math` | Double-check the SEA / compaction-efficiency equations and drop-impact peak-force methodology vs. PR #67, issue #71, PR #74 | `e4e5fb15-445b-4851-a16e-a3c366eba8f2` |

Fetch with:

```python
from edison_client import EdisonClient
client = EdisonClient(api_key=...)  # EDISON_PLATFORM_API_KEY
client.get_task("<task_id>").model_dump_json()
```
