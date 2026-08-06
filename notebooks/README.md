# Notebooks

Tutorial / audit notebooks that pull raw data straight from GitHub, so they run
in Colab with no repo checkout and no local setup.

## `drop_tower_spot_check.ipynb`

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vertical-cloud-lab/tensegrity-optimization/blob/claude/issue-94-20260731-1759/notebooks/drop_tower_spot_check.ipynb)

Companion to [issue #94](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/94)
("better understanding the drop tower analysis"). Downloads the 40 raw
polyurethane-arrangement captures and rebuilds
`docs/drop-test-pu-configs-analysis.md` from first principles, so its numbers can
be checked without trusting any code in this repo.

Three parts, one per primitive the whole drop-test pipeline rests on:

| Part | Primitive | Finding |
|---|---|---|
| **A** | the SAE J211 CFC filter | `cfc_filter()` is ~20 % narrow in every class — "CFC-180" is really ≈ CFC-146. The published "CFC-180 attenuates 550 Hz by 12×" is the bug's number; J211's is 5.7×. |
| **B** | the baseline / zero offset | with only ~0.35 ms of pre-trigger, `T` moves by up to 38 % depending on the baseline window. The effects under discussion are 1–3 %. |
| **C** | `T = peak(out)/peak(in)` | the published table reproduces exactly; the baseline error is worth ~10× the filter error. |

Data is pinned by commit hash
([`b6a296e`](https://github.com/vertical-cloud-lab/tensegrity-optimization/tree/b6a296ebee685b8eec29c1440b4a80c863c1abaa))
rather than by branch, so re-running it later cannot silently read different data.
Downloads ≈ 21 MB; runs in ~3 min on a free Colab CPU runtime.

Regenerate with `python notebooks/build_spot_check_notebook.py` — the `.ipynb` is
built from `build_spot_check_notebook.py` so the notebook stays reviewable as
source rather than as a wall of JSON.

### Related

* `scripts/analysis/cfc_verification.py` — Part A as a standalone script, no data
  download needed.
* `scripts/edison/submit_j211_audit.py` / `fetch_j211_audit.py` — the independent
  Edison Scientific standards audit of the same three primitives.
