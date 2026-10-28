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
- **Status:** `success` — **fetched and committed**.

## Fetched artifacts

- [`accelerometer-tuning-015f36e1-….md`](accelerometer-tuning-015f36e1-0a1c-4aed-a9a3-1d1924983c4a.md) — the reviewer's written answer.
- [`accelerometer-tuning-015f36e1-….json`](accelerometer-tuning-015f36e1-0a1c-4aed-a9a3-1d1924983c4a.json) — full `FinchTaskResponse` dump.
- [`accelerometer-tuning-015f36e1-….ipynb`](accelerometer-tuning-015f36e1-0a1c-4aed-a9a3-1d1924983c4a.ipynb) — the analysis notebook (38 cells).
- `reviewer-artifacts/peak_summary_impact_window.csv` — reviewer's impact-windowed peak table.
- `reviewer-artifacts/reviewer_ch1_ch4_alignment.png` — reviewer's CH1-vs-CH4 alignment figure.

## Headline feedback (folded into the analysis)

1. **Peak detection was the global window maximum**, so for events 1 & 4 the CH1
   CFC-180 "peak" was a low-frequency post-impact mount oscillation at ~15.8 ms,
   not the impact. Restricting the search to a ±1 ms window around the CH4 impact
   drops the CH1/CH4 CFC-180 ratio from ~1.55 to **~1.10–1.12** — the sensors
   agree within ~10–12% on the rigid-body pulse.
2. **The ~4.2 ms CH4 peak is the real impact, not a trigger/magnet artifact** — in
   the aborted drops (events 6–8) CH4 is <0.5 G there; it just recurs at ~4.2 ms
   because the carriage free-fall time is repeatable. Do **not** gate it out.
3. CH1's ~8806 G ceiling is **analog** saturation (smooth ~180 µs compression),
   not a digital ADC clip; recommend a higher full-scale (e.g. 20,000 G) sensor.

To re-fetch in a later session: `client.get_task(task_id="015f36e1-0a1c-4aed-a9a3-1d1924983c4a")`.
