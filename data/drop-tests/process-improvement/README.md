# Process-improvement scorecard (derived)

This folder has no raw data of its own. It holds the derived scorecard that
answers @ctrhjk on PR #86 (10-10): *how much has the test process improved
since the very first drop test, as a number?*

- Script: [`scripts/analysis/drop_test_process_improvement_analysis.py`](../../../scripts/analysis/drop_test_process_improvement_analysis.py)
- Writeup: [`docs/drop-test-process-improvement-analysis.md`](../../../docs/drop-test-process-improvement-analysis.md)
- `figures/01_process_improvement.png`: per-session drop-to-drop CV by era,
  and the smallest detectable design difference, first drops vs now.
- `figures/process_improvement_metrics.json`: every number in the writeup,
  per era, plus the resolution calculation.

Headline: the smallest design difference the test detects went from at least
25 % (05-22) to 3.3 % with one article per design, which is at least 7.6×
finer. With three prints per design it is 1.9 %. Per drop, the objective is
about 40× more repeatable (CV 11.1 % → 0.28 %).

The first-drop numbers are recomputed from `../raw/` (`Signal 10–14`) and the
input–output numbers from `../input-output/raw/`. Every other number comes
from committed `*_metrics.json` files: the sample-size meta-analysis, the
July campaigns, the seven BO-campaign `campaign_metrics.json` files and the
round-3 `three_print_comparison.json`. Regenerate with:

```bash
pip install numpy scipy matplotlib
python scripts/analysis/drop_test_process_improvement_analysis.py
```
