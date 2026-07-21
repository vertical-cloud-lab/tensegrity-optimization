# Sample-size / variance meta-analysis (derived)

No raw data of its own — this folder holds the derived cross-dataset
**variance + sample-size + timing** analysis that answers @me-madsen's question
on [PR #82](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/82#issuecomment-5026945744)
(re-asked on PR #86, 2026-07-21):
*how many drops per specimen, how much variance so far, and how long a set
takes at ~42 s/drop at 60 in.*

- Script: [`scripts/analysis/drop_test_sample_size_analysis.py`](../../../scripts/analysis/drop_test_sample_size_analysis.py)
- Writeup: [`docs/drop-test-sample-size-analysis.md`](../../../docs/drop-test-sample-size-analysis.md)
- `figures/sample_size_metrics.json` — aggregated CVs, sample-size tables, plans, and batch timing.

The script reads the within-specimen CVs already emitted by the per-dataset
analyses (the large-campaign `figures/*_metrics.json` `stabilized_ols`, the
60 in / 5 felts validation, the 5-vs-10-in comparison, the felt-sheet
per-condition CVs, and the n = 5 mount-validation writeups) and derives the
recommendation; regenerate with:

```bash
pip install numpy scipy matplotlib
python scripts/analysis/drop_test_sample_size_analysis.py
```
