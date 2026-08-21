# SOBOL + S0 BO-campaign drop tests

First batch of the optimization campaign (announced on PR #86, 08-19-2026):
8 of 9 specimens of the SOBOL + S0 batch, run through the standing SOP —

- 60 in drop height, arrangement B (1/2 in polyurethane mat,
  [material/specs](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/88#issuecomment-5094675931))
- 101 drops per specimen (first 2 discarded as warm-up at analysis time)
- capture: CH2–CH4 top-vertex tri-axis + CH5 base-plate input, 1.25 MHz,
  125,000 samples = 100 ms, 2 ms pre-trigger, 150 G trigger on CH5 —
  the settings verified after the 08-18 TP4 reset
  (see [`calibration-check/`](../calibration-check/))

Analysis writeup:
[`docs/drop-test-sobol-campaign-analysis.md`](../../../docs/drop-test-sobol-campaign-analysis.md).
Design parameters per specimen: [`params.json`](params.json) (joined from
the issue-#98 print key; `amdjwm` is unmapped — see the writeup §5).

## Sessions (raw data on Box, ~8.4 GB total)

One subfolder per session under [`raw/`](raw/), each holding the TP4
**series table** and a **`box-ids.json`** manifest (shared-link name +
per-file Box IDs) — the full Signal CSVs stay on Box and can be re-fetched
with `scripts/fetch_box_shared_folder.py <shared_name> <dest>`:

| session folder | captures | date | Box link |
|---|--:|---|---|
| `bag26v 8-13-2026 101drops` | 101 | 08-13 | [n5fkbur…](https://byu.box.com/s/n5fkbur86gzronh04rf3f00diw0yz2es) |
| `amdjwm-s1 8-17-2026 am 87drops` | 87 | 08-17 | [ig3vgyl…](https://byu.box.com/s/ig3vgyld9t4kbuf2tstvg8v3m2jrwns0) |
| `amdjwm 8-17-2026 pm 101drops` | 101 | 08-17 | [xd2ftvi…](https://byu.box.com/s/xd2ftvi3y57jopvxyg1pae7qx61jdsvu) |
| `bpx68c 8-17-2026 101drops` | 101 | 08-17 | [it5499h…](https://byu.box.com/s/it5499hkyw24twg7179smsn0fv0bodal) |
| `autv5r 8-19-2026 103signals` | 103 | 08-19 | [2uztrfb…](https://byu.box.com/s/2uztrfbblzzwhefmdelt523v4xi1exz0) |
| `6lhxfy-s1 8-19-2026 35drops` | 35 | 08-19 | [hkyw0nv…](https://byu.box.com/s/hkyw0nv9s2l27r893sapb6kxumk0l0d9) |
| `6lhxfy 8-20-2026 101drops` | 101 | 08-20 | [q5tyg1a…](https://byu.box.com/s/q5tyg1as1h0pgqrppa8nsuhnllbhjsnu) |
| `9hhbkp 8-20-2026 101drops` | 101 | 08-20 | [bbwutg2…](https://byu.box.com/s/bbwutg2r6a4l3q71vv2q84nvrue7h1h6) |
| `nvxsrv 8-20-2026 101drops` | 101 | 08-20 | [cym881r…](https://byu.box.com/s/cym881rlx1je5rec4eowj8khglopax2i) |
| `6nheas 8-20-2026 101drops` | 101 | 08-20 | [y7v10k0…](https://byu.box.com/s/y7v10k08mqb3f093dxfl4pn8wafq6n9i) |

`-s1` suffix = interrupted first session (kept as an independent
session-repeatability check; excluded from the campaign summary). `bpx68c`
08-17 is the same upload as the calibration-check "before" set.

## Outputs (committed under `figures/`)

- `campaign_summary.csv` — one row per specimen, objectives ± sd + design
  parameters: **the BO ingest file**
- `campaign_metrics.json` — full record incl. per-drop rows
  (`partial_sessions_metrics.json` for the two `-s1` sessions)
- `01_campaign_series.png`, `02_campaign_ranking.png`

## Reproducing

```bash
pip install numpy scipy matplotlib
# fetch each session listed above into a subfolder of raw/, then:
python scripts/analysis/drop_test_campaign_analysis.py --procs 4 \
    --params "data/drop-tests/sobol-campaign/params.json"
```

Note the pipeline uses the **tail baseline** (`analyze_capture(...,
baseline="tail")`): from 08-17 on, mat contact starts > 2 ms before the
150 G trigger, so the pre-trigger window rides a +10–20 G contact foot and
is not a valid zero. Validated against the TP4 series tables (writeup §2).
