# Absorber-stack compaction analysis (derived)

No raw data of its own — this folder holds the derived CH5-only analysis of
how the shared 4-felt + 1-cardboard absorber stack compacts with each drop,
answering @me-madsen's question on
[PR #86](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86)
(2026-07-29; physical compaction documented in
[issue #88](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/88#issuecomment-5121703763)):
*how does compaction grow per drop, when (if ever) does the stack become
unusable, and is transmissibility consistent across compaction levels?*

- Script: [`scripts/analysis/drop_test_compaction_analysis.py`](../../../scripts/analysis/drop_test_compaction_analysis.py)
- Writeup: [`docs/drop-test-compaction-analysis.md`](../../../docs/drop-test-compaction-analysis.md)
- `figures/compaction_metrics.json` — per-session wear/recovery metrics,
  clip projections, T-vs-compaction sensitivities.

Inputs are the per-drop records already committed by the campaign analyses
(704 drops on the stack, 07-20 → 07-27, seven 60 in sessions):
`60in-5felts-validation/figures/60in_5felts_metrics.json`,
`prc1kn-60in-5felt/figures/prc1kn_60in_metrics.json`, and
`7-22 - 7-27 Drop Tests/figures/batch_722_727_metrics.json`. Regenerate with:

```bash
pip install numpy scipy matplotlib
python scripts/analysis/drop_test_compaction_analysis.py
```
