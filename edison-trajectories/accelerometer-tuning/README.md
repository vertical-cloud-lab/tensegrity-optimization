# Edison: accelerometer-tuning analysis (issue #71)

Edison `ANALYSIS` (data-analysis crow) task asking for independent feedback on
the drop-tower single-axis vs tri-axis accelerometer "tuning" analysis.

- **Task id:** `015f36e1-0a1c-4aed-a9a3-1d1924983c4a`
- **Job:** `JobNames.ANALYSIS` (`job-futurehouse-data-analysis-crow-high`)
- **Uploaded bundle:** `data_entry:de73d080-496a-4ff4-81cb-aaadfe58f024`
  (TP4 raw CSVs + `peak_summary.csv` + README, the analysis script, and the
  written findings/figures — staged as one collection via
  `store_file_content(..., as_collection=True)`).
- **Driver:** [`scripts/edison/submit_accelerometer_tuning.py`](../../scripts/edison/submit_accelerometer_tuning.py)
- **Status:** submitted, `in progress` at session end (non-blocking).

## Fetch next session

The task was submitted non-blocking. To retrieve the result in a later session:

```python
from edison_client import EdisonClient
client = EdisonClient()  # reads EDISON_PLATFORM_API_KEY
r = client.get_task(task_id="015f36e1-0a1c-4aed-a9a3-1d1924983c4a")
# ANALYSIS returns a FinchTaskResponse: answer + notebook (ipynb JSON)
```

Write the fetched artifacts to
`accelerometer-tuning-015f36e1-*.{md,json}` in this directory.
