# Edison trajectory — mechanistic data-figure feedback

Per PR review comment 4664873230 (@sgbaird: *"send this to edison analysis for
feedback"*, referring to the standalone mechanism-oriented data-figure example
created in PR comment 4664784933), the example figure was submitted to Edison
**ANALYSIS** for structured, actionable critique before real processed data and
high-speed-camera frames are swapped in.

## What was sent

`bundle/` (zipped into `mechfig-bundle.zip` and uploaded as a single collection,
which ANALYSIS requires):

- `mechanistic-data-figure-example.png` / `.pdf` — the rendered example
- `mechanistic_data_figure_example.py` — the matplotlib generator
- `README.md` — describes the figure as an illustrative mock-up (synthetic data)

The prompt asks for prioritized feedback on storytelling (linking signal to
mechanism), highest-value additional panels/quantities, camera-frame
registration, synthetic-vs-real honesty and uncertainty reporting, layout/color/
accessibility for ASME figures, and any physics red flags in the synthetic
curves.

## Task

- Job: `JobNames.ANALYSIS`
- Task ID: `e0c4e062-15c7-4a62-b931-1746211fe8b1` (see
  `mechfig-feedback-SUBMITTED.json`)
- Uploaded collection: `data_entry:78046c06-0f43-4144-8d8a-a2f7c1afd242`

## Reproduce

```sh
python scripts/edison/submit_mechfig_feedback.py   # submit (non-blocking)
python scripts/edison/fetch_mechfig_feedback.py    # poll + write trajectory
```

The fetch script writes `mechfig-feedback-<task_id>.{md,json}` once the task
reaches a terminal state.
