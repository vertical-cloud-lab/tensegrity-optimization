# Edison Scientific ANALYSIS — clip-height / accelerometer-check diagnostic

Edison Scientific **ANALYSIS** (`job-futurehouse-data-analysis-crow-high`) task
[`91e293a8-fe7e-480c-bc9a-423f47bb5df1`](clip-height-91e293a8-fe7e-480c-bc9a-423f47bb5df1.md),
driven by sgbaird PR comment 4794736130:

> have a look at the previous two comments. Send an Edison analysis query with
> the data, fetch this session, summarize interpretation, provide
> recommendations directly in your comment reply.

The "previous two comments" are @ctrhjk's clip-height sweep (no triggered data,
video only) and the base-plate accelerometer check (one triggered CSV). The one
available CSV plus our context/analysis markdown were uploaded as a single
zipped collection and the data-analysis crow was asked to verify the base-plate
numbers, diagnose the acrylic-plate "no trigger" failure, and recommend a path
to a trustworthy transmitted-g measurement.

## Files

| file | description |
|---|---|
| `clip-height-91e293a8-…-SUBMITTED.json` *(`clip-height-SUBMITTED.json`)* | submission record (task id, uploaded collection uri) |
| `clip-height-91e293a8-….md` | the markdown analysis report |
| `clip-height-91e293a8-….json` | full `get_task` model dump |
| `clip-height-91e293a8-…-notebook.ipynb` | the analysis notebook the crow executed |
| `clip-height-91e293a8-…-fig1.png` | base-plate diagnostic figure (inline notebook output) |

Driver: [`scripts/edison/submit_clip_height.py`](../../scripts/edison/submit_clip_height.py)
· fetch: [`scripts/edison/fetch_clip_height.py`](../../scripts/edison/fetch_clip_height.py).

## Headline

Edison independently reproduced our base-plate numbers from the CSV (CH4 raw
3071.7 G, CFC-1000 1154.4 G, CFC-180 276.9 G, Δv 3.36 m/s; CH4 dominates the
off-axis channels ~23–55× at CFC-180 → axis-aligned base-plate hit; Δv is
1.3–1.6× free-fall, consistent with the bungee-assisted tower). It confirms the
diagnostic separates cleanly into **"instrumentation works" vs "acrylic-plate
load path is broken,"** and that **0/8 triggers across a 0.5–2.0 in clip-height
sweep means a clip-only fix is insufficient** — the acrylic plate is seating on
/ damped by the bungee-restrained specimen so the strike is a slow, distributed,
sub-trigger load rather than a sharp shock. Prioritized fixes: drop/relocate the
1000 G trigger (trigger off the input channel or free-run), record simultaneous
input + transmitted channels, redesign the load path (captive plate on linear
bushings + hard top-stop + bungees slack at impact), and otherwise fall back to
the already-clean vertex-mounted CFC-180 peak-g for the BO objective.
