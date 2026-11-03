# Edison Scientific ANALYSIS — input-output (transmissibility) drop series

Edison Scientific **ANALYSIS** (`job-futurehouse-data-analysis-crow-high`) task
[`fe044079-a179-4b74-ac72-17bfdf1042d4`](input-output-fe044079-a179-4b74-ac72-17bfdf1042d4.md),
driven by sgbaird PR comment 4804945090:

> analyze the data that @ctrhjk provided in [PR #67 comment 4804858562] … Then,
> send to edison for feedback when you're done analyzing. Fetch this session.
> Summarize and reply.

The series (PR comment 4804858562) is @ctrhjk's **input-output** instrumentation
design: a single-axis accelerometer on the bottom plate (INPUT, triggered CH5)
and a tri-axis accelerometer on the top vertex (OUTPUT, CH2/CH3/CH4), bungees
removed, four distinct-geometry specimens × five drops at 13 in. The 20 raw
CSVs plus our README, analysis markdown and figures were uploaded as a single
zipped collection and the data-analysis crow was asked to verify our numbers and
critique transmissibility as a Bayesian-optimization objective.

## Files

| file | description |
|---|---|
| `input-output-SUBMITTED.json` | submission record (task id, uploaded collection uri) |
| `input-output-fe044079-….md` | the markdown analysis report |
| `input-output-fe044079-….json` | full `get_task` model dump |
| `input-output-fe044079-…-notebook.ipynb` | the analysis notebook the crow executed |

Driver: [`scripts/edison/submit_input_output.py`](../../scripts/edison/submit_input_output.py)
· fetch: [`scripts/edison/fetch_input_output.py`](../../scripts/edison/fetch_input_output.py).

## Headline

Edison **independently reproduced our transmissibility values exactly to two
decimals** from the raw CSVs (practice 1.17, n0jdwk 1.19, yqpmx1 0.96, h8Lbev
1.09; absolute G ~2–3 G below ours, attributed to small CFC filter-design
differences), with all **20/20 drops triggered cleanly** at t ≈ 3.92–3.95 ms.

Key feedback:
- **Δv check:** its ±1.5 ms CFC-1000 integration of CH5 gives partial-pulse
  Δv ≈ 3.4–3.7 m/s (vs free-fall 2.55 m/s from 0.33 m) — the excess is rebound
  (e ≈ 0.4), **no bungee assist needed** to explain it (bungees were removed).
  It flags that Δv is sensitive to the window/filter choice and ours (half-
  amplitude window on CFC-180) reads lower (~2.85–2.96 m/s) — both are valid
  *partial-pulse* numbers over different spans.
- **T as a BO objective:** a defensible first-pass *screening* metric under
  fixed drop conditions, but a peak ratio of two scalars whose peaks need not
  coincide — a shock-severity heuristic, not a true transfer function. Once a
  simultaneous input+output pair exists, an FRF / SRS-band reduction is more
  physical. T > 1 for 3 of 4 specimens (stiff vertex-to-vertex path → amplifies)
  rules out "cushioning" claims; only `yqpmx1` attenuates. Use **output peak at
  fixed input** as the easy-to-interpret near-equivalent; feed within-specimen
  SD as heteroscedastic BO noise (upper bound until specimen replication).
- **Within-run drift is real and most likely mount-driven:** OLS of T on drop
  index is positive for all four specimens (pooled demeaned +0.015/drop,
  p = 0.0001); output rising while input holds fits hot-glue seating/creep
  better than material softening over only 5 cycles. **Do not start 20-drop /
  to-failure campaigns on hot glue and call the trend fatigue.**
- **Prioritized SOP fixes:** replace hot glue with a z-aligned rigid keyed seat
  (ISO 5347), keep bungees removed, extend capture past 200 ms for ringdown,
  replicate at the specimen level (n ≥ 5 prints/geometry, randomized order,
  precondition mounts), use a CFC-180 output-peak/T metric now → FRF + SRS-band
  later (never raw peaks), anchor in SAE J211 / ISO 5347 / ASTM D3332 (D7136
  with scope caveats), and log specimen/sensor mass + geometry to later regress
  T against the design parameters.
