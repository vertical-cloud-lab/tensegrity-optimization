# Edison Scientific ANALYSIS — adversarial review of the PU arrangement sweep

Edison Scientific **ANALYSIS** task
[`d9092c5a-9675-461c-966f-29236fb9d84e`](pu-configs-d9092c5a-9675-461c-966f-29236fb9d84e.md),
driven by sgbaird PR #86 comment 5137645029:

> send to Edison to question the underpinnings of the analysis mentioned here

"The analysis mentioned here" is
[`docs/drop-test-pu-configs-analysis.md`](../../docs/drop-test-pu-configs-analysis.md)
— the re-derived recommendation to adopt **arrangement B** (1/2 in PU sheet
alone) as the transmissibility operating point. The task was framed
**adversarially**: *try to break this, not confirm it*. All 40 raw CSVs, the TP4
series table, our analysis markdown, our **analysis script** (so the method
itself could be audited), the metrics JSON and the figures were uploaded as one
zipped collection.

## Files

| file | description |
|---|---|
| `pu-configs-SUBMITTED.json` | submission record (task id, uploaded collection uri) |
| `pu-configs-d9092c5a-….md` | the task's returned message (points at the report bundle) |
| `pu-configs-d9092c5a-….json` | full `get_task` model dump |
| `pu-configs-d9092c5a-…-notebook.ipynb` | the analysis notebook the crow executed |
| `report/adversarial-review.md` | **the report** — the commit-ready markdown Edison produced |
| `report/independent_per_drop_metrics.csv` | Edison's independently recomputed 40-drop table |
| `report/independent_arrangement_summary.csv` | arrangement-level summary with descriptive CIs |

Driver: [`scripts/edison/submit_pu_configs.py`](../../scripts/edison/submit_pu_configs.py)
· fetch: [`scripts/edison/fetch_pu_configs.py`](../../scripts/edison/fetch_pu_configs.py).

## Verdict

> **Do not select B from this sweep. None of A–D is supported as the
> Bayesian-optimization operating point.** The supported answer is *"none of
> these; the sweep cannot decide."*

Of the four grounds given for B, **grounds 2 and 3 fail, ground 1 does not
survive as stated, and ground 4 partly survives** as a descriptive warning
against A.

## The decisive finding — verified independently in this repo

**The 20 ms exports contain ~0.39 ms of real pre-trigger data.** Raw CH5 first
crosses its trigger level at 0.348–0.390 ms and is only 0.09–2.6 % of peak at
`t = 0`. Our analysis script's module docstring asserts the opposite ("the
record starts *on* the trigger, so there is no clean pre-trigger window") and
therefore uses a **full-record median** as the baseline — a window that includes
the impact and ringdown.

The "CFC-180 CH5 already reads 22–53 % of its peak at t = 0" caveat in
[`drop-test-pu-configs-analysis.md`](../../docs/drop-test-pu-configs-analysis.md)
§8 is **acausal pre-ringing from zero-phase (`filtfilt`) filtering**, not
evidence of truncation.

Re-running with a pre-trigger baseline (median of the first 0.10 ms) changes the
headline numbers:

| CFC-180 T | A | B | C | D |
|---|--:|--:|--:|--:|
| published (full-record median) | 1.022 | 0.996 | 0.986 | 0.989 |
| **pre-trigger baseline** | **1.037** | **1.063** | **1.050** | **1.094** |
| published T CV | 0.43 % | 0.34 % | 0.95 % | 0.49 % |
| **pre-trigger T CV** | **0.54 %** | **1.18 %** | **1.22 %** | **2.48 %** |

This was reproduced independently in this repo on one drop per arrangement
(Signals 1/11/22/32 → T = 1.026 / 1.076 / 1.037 / 1.139, matching Edison's
per-drop table exactly). The mechanism is that the full-record median is
displaced by the post-impact ringdown by up to ~15 G on individual tri-axis
channels, which is several percent of these 155–265 G peaks, and it biases the
input and the vector-magnitude output differently.

Consequences: **no arrangement attenuates** (every T > 1); B is neither closest
to unity nor the most repeatable CFC-180 arrangement (A is); and the "T falls
monotonically with pulse duration" law disappears (Spearman ρ = 0.40, p = 0.60).

## The other findings

- **The 450–800 Hz band criterion is an estimator artifact.** The published
  Welch estimate has 305 Hz bin spacing — *one* bin in band — and takes the
  spectrum of the nonlinear vector magnitude. Under signed-axis linear energy
  the ordering reverses (A 30.7 %, B 7.0 %, C 1.4 %, D 1.5 %); absolute band
  energy favours A ~20×; input-normalised energy gives yet another ordering
  (D > A ≈ C > B). Ground 3 collapses.
- **The `f·τ ≤ 1.5` cutoff is wrong.** Numerically integrating a 5 %-damped SDOF
  under a half-sine gives maximax/input = 1.64 / 1.54 / 1.28 at
  `f·τ` = 0.91 / 1.23 / 1.84. C and D are **not** quasi-static, and the SRS peak
  has near-zero frequency slope — targeting it maximises *response* but can
  *minimise* frequency discrimination.
- **The 519–549 Hz "mode" is not identified.** CH3 carries the largest
  400–900 Hz output energy in all 40 drops (A 517 ± 6, B 533 ± 3, C 511 ± 37,
  D 477 ± 54 Hz), but CH5 — the *base* — has arrangement-dependent content in
  the same region, so forced response, rocking, and mount motion are not
  excluded. Correct mounting standard is **ISO 5348:2021**, not ISO 5347 as our
  docs cite.
- **All arrangement-level p-values are invalid.** One fixed-order block per
  arrangement; lag-1 autocorrelation up to 0.98 collapses several n = 10
  sequences toward one effective observation. After linear detrending, T CVs are
  A/B/C/D = 0.45/0.25/0.70/0.36 % (CFC-180) and 2.03/0.89/0.89/0.84 %
  (CFC-1000) — A remains worse broadband, but with zero arrangement-level
  degrees of freedom. "C vs D is a null" has 80 % power only for ≳1.1 % in T.
- **Peak-ratio T is not an energy-absorption objective.** It divides
  non-synchronous peaks of a single-axis base channel and a nonlinear tri-axis
  magnitude at another point, and ignores force, displacement and rebound
  kinetic energy. Ranked alternatives: input-conditioned output SRS → band-
  limited transfer function with coherence → output peak at fixed *measured*
  incident velocity → ringdown damping → incident/rebound KE loss (the direct
  metric, needs a photogate/encoder and known moving mass).
- **Δv is a processing-dependent descriptor**, not an impact velocity and not a
  lower bound; agreement with 5.47 m/s free fall is not validation.

## Cheapest risk-reduction experiment (Edison's recommendation)

A **20-drop randomized crossover**: two existing distinct geometries ×
arrangements A and B, 5 drops per cell, interleaved in randomized order, one
common trigger level, **≥ 2 ms pre-trigger and 50–100 ms post-impact capture**,
with input-conditioned SRS / band-transfer outcomes prespecified before
collection. This directly tests whether B's lower noise compensates for its much
lower absolute structural-band excitation — the trade-off the sweep cannot
resolve. It is a screen, not qualification: it cannot estimate print variance.

## Repo-wide follow-up

The full-record-median baseline is used by exactly the three scripts that read
the new 1.25 MHz / 20 ms exports:

- `scripts/analysis/drop_test_pu_configs_analysis.py`
- `scripts/analysis/drop_test_pu_vs_felt_analysis.py`
- `scripts/analysis/drop_test_print_defects_analysis.py`

All the older 125 kHz / 200 ms scripts already baseline on a pre-trigger window
(`ch[:nb]`), so they are unaffected. The two sibling 20 ms analyses **have not
yet been re-run** on a pre-trigger baseline; the print-defect study in
particular reports between-specimen T differences of ~2 %, the same order as the
baseline shift, so its conclusions need re-checking before they are relied on.
