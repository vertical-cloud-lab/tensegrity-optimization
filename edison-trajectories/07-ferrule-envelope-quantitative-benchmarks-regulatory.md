# Edison trajectory: 07-ferrule-envelope-quantitative-benchmarks-regulatory

- **Task ID:** `98a30884-4ba4-4b26-b59c-af5779b44479`
- **Job:** `job-futurehouse-paperqa3-high` (`LITERATURE_HIGH`)
- **Status:** `queued` / `in progress` (at time of commit)
- **Edison platform link:** https://platform.edisonscientific.com/tasks/98a30884-4ba4-4b26-b59c-af5779b44479
- **Motivation:** Follow-up to the Edison abstract peer-review (trajectory `06`, task `74ac013b…`), which flagged three fact-checks the abstract could not yet defend with numbers: (i) the ferrule geometry claim conflated crutch-**shaft bore** (~19–25 mm) with the ferrule **outer envelope** (patents cite 32–47 mm) and never substantiated "severely limits stroke"; (ii) the abstract reports **no quantitative performance result** (no SEA in J/g, no %-force-reduction, no rubber-ferrule baseline); and (iii) "FDA Class I … pathway is clear" overstated regulatory certainty for a *novel multi-material insertable absorber*.
- **Summary:** Asks Edison to (1) resolve the ferrule/tip dimensional envelope (shaft bore vs. ferrule OD) and estimate the realistic internal volume and axial **stroke** available to an insertable absorber, so "severely limits stroke" can be corrected/quantified; (2) compile representative **SEA (J/g)**, **peak-force-reduction (%)**, and transmitted-impulse ranges for miniaturized TPU / PETG / TPU+PETG (and TPU+ABS) architected/lattice/tensegrity/honeycomb/gyroid absorbers under quasi-static and drop-weight impact, with the relative density / cell size at which they occur, to give the abstract a defensible target number; (3) characterize a **conventional rubber-ferrule baseline** (peak force / loading rate / energy absorption) as the control the insert must beat; and (4) confirm the **21 CFR 890.3790 Class I / 510(k)** status and **ISO 11334-1** scope, and assess whether a novel multi-material insertable component could change the classification, with precedent 510(k)s / predicate devices.

> _Placeholder file — task is still `queued`/`in progress` at commit time. Will be refreshed next session with the full `formatted_answer` (Question + cited Answer + numbered References) plus a sibling `*.json` `model_dump_json()` dump, following the same pattern as trajectories 01–04 / 06 in this directory._

To re-fetch:

```python
import json, os
from edison_client import EdisonClient
c = EdisonClient(api_key=os.environ["EDISON_API_KEY"])
t = c.get_task("98a30884-4ba4-4b26-b59c-af5779b44479")
print(t.status)
print(t.formatted_answer)
open("07-ferrule-envelope-quantitative-benchmarks-regulatory.md", "w").write(t.formatted_answer)  # then prepend this header
open("07-ferrule-envelope-quantitative-benchmarks-regulatory.json", "w").write(t.model_dump_json())
```
