# SOBOL + S0 BO-campaign drop tests (data pending)

Staging area for the optimization-campaign batch announced on PR #86
(08-19-2026): every specimen of the SOBOL + S0 batch run through the
standing SOP —

- 60 in drop height
- arrangement B: 1/2 in polyurethane mat alone
  ([material/specs](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/88#issuecomment-5094675931))
- 101 drops per specimen (first 2 discarded as warm-up at analysis time)
- capture: CH2–CH4 top-vertex tri-axis + CH5 base-plate input, 1.25 MHz,
  125,000 samples = 100 ms, 2 ms pre-trigger, 150 G trigger on CH5 —
  the settings verified after the 08-18 TP4 reset
  (see [`calibration-check/`](../calibration-check/) and the committed
  settings screenshot)
- 3 slow-motion videos per specimen (960 fps; landscape camera-original
  files with XML sidecars preferred)

Raw data lives on Box (~0.9 GB per 101-drop specimen); fetch each
specimen's session into a subfolder of `raw/` (loose `*_Signal<k>.csv`
files or the TP4 zips as uploaded — both are read directly). The specimen
ID is taken from the first word of the subfolder name, lowercased, e.g.
`raw/bpx68c 60in 101drops/`.

## Analysis

```bash
pip install numpy scipy matplotlib
python scripts/analysis/drop_test_campaign_analysis.py            # defaults to this folder
# optional: map specimen IDs to design parameters for the BO hand-off
python scripts/analysis/drop_test_campaign_analysis.py --params params.json
```

Per specimen this emits stabilized mean/CV/drift for T (CFC-180 and
CFC-1000), output/input peaks, pulse width, Δv (with the rig-health
verdict against the settled 4.55–4.66 m/s band and the healthy-tower
5.28–5.35 m/s bar), specimen-hop delay `t_second`, `e_rebound`, and
r²-gated ringdown `f_n`/ζ; campaign-level it runs the cross-specimen
ANOVA/pairwise comparison and writes:

- `figures/campaign_metrics.json` — full record (per-drop rows included)
- `figures/campaign_summary.csv` — one row per specimen (objectives ±
  sd, plus design parameters if `--params` was given): the BO ingest file
- `figures/01_campaign_series.png`, `figures/02_campaign_ranking.png`

`params.json` format: `{"<specimen id>": {"<param>": value, ...}, ...}`
(IDs case-insensitive).
