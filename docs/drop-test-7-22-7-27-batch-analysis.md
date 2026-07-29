# 7-22 → 7-27 second-batch campaigns: consistency check + batch-to-batch transmissibility

**Data:** [`data/drop-tests/7-22 - 7-27 Drop Tests/`](../data/drop-tests/7-22%20-%207-27%20Drop%20Tests/) (PR #86, posted by @me-madsen)
**Script:** [`scripts/analysis/drop_test_722_727_batch_analysis.py`](../scripts/analysis/drop_test_722_727_batch_analysis.py)
**Figures/metrics:** [`data/drop-tests/7-22 - 7-27 Drop Tests/figures/`](../data/drop-tests/7-22%20-%207-27%20Drop%20Tests/figures/)

Four new ~100-drop campaigns at the 60 in / 4 felt + 1 cardboard operating
point, re-running three previously campaigned specimens plus `RW5F61`'s
first 60 in session. "Batch 1" below is the first round of 60 in campaigns
(`7xadt6`/`9GMQYQ` on 07-20, `prc1kn` on 07-21); "batch 2" is this upload.

## 1. The batch at a glance

| session | date | captures | export format | CH5 CFC-180 (stabilized) | CH5 raw %FS (median → max) |
|---|---|--:|---|--:|--:|
| `prc1kn` | 07-22 | 100/100 real | CH2–CH5, 200 ms @ 125 kHz | 477.2 G (CV 0.71 %) | **83 % → 91 %** |
| `RW5F61` | 07-23 | 101/101 real | **CH5 only**, 20 ms @ 1.25 MHz | 420.0 G (CV 3.69 %) | 39 % → 57 % |
| `7xadt6` | 07-27 | 100/100 real | **CH5 only**, 20 ms @ 1.25 MHz | 445.2 G (CV 1.66 %) | 57 % → 70 % |
| `9GMQYQ` | 07-27 | 101/101 real | **CH5 only**, 20 ms @ 1.25 MHz | 461.3 G (CV 0.65 %) | 67 % → 77 % |

All 402 captures triggered as real drops (CH5 raw ≥ 200 G); zero spurious
captures. Cadence 40–47 s median, matching the ~42 s/drop planning figure
(`7xadt6` has one 14.3 min pause).

## 2. ⚠️ Three of the four sessions have no top-vertex channel

The `RW5F61`, `7xadt6` and `9GMQYQ` exports contain a **single column, CH5**
(the base-plate single-axis input), recorded at 1.25 MHz over a 20 ms
window — versus the standard 4-channel 125 kHz / 200 ms format that the
`prc1kn` 07-22 session (and every batch-1 campaign) used. The 10× sample
rate and the shortened window indicate the TP4 ran with only CH5 enabled at
capture time, not merely that the export dropped columns — but that is
worth confirming on the DAQ side.

Consequences:

* **Transmissibility T = TOP/CH5 cannot be computed** for those three
  sessions — there is no output channel. The requested batch-to-batch T
  comparison is therefore only possible for `prc1kn` (§4).
* If the TP4 event database (`EventDatabase.TP4_db`) still holds CH2–CH4
  for these sessions, a re-export recovers everything; if only CH5 was
  recorded, the sessions measure input repeatability only and the T
  re-comparison needs a re-run with the tri-axis connected.
* `RW5F61` is the highest-value re-run: it is the program's only remaining
  sub-1.0 T candidate (T ≈ 0.945–0.957 at 5/13 in), and this was its first
  60 in campaign.

The 20 ms window also truncates the ringdown (impact lands ~0.6–0.7 ms into
the record, so ~19 ms of post-impact data vs ~196 ms in the standard
format); peak/pulse/Δv metrics are unaffected.

## 3. Input-channel consistency: batch 1 vs batch 2

Stabilized-phase CH5 CFC-180 input (same burn-in convention as batch 1;
figure `03_input_batch_comparison.png`):

| specimen | batch 1 | batch 2 | diff | Welch p |
|---|--:|--:|--:|--:|
| `prc1kn` | 472.2 G (CV 0.65 %) | 477.2 G (CV 0.71 %) | **+1.0 %** | 8.8e-21 |
| `7xadt6` | 446.2 G (CV 1.66 %) | 445.2 G (CV 1.66 %) | **−0.2 %** | 0.34 (n.s.) |
| `9GMQYQ` | 462.7 G (CV 0.81 %) | 461.3 G (CV 0.65 %) | **−0.3 %** | 4.8e-3 |
| `RW5F61` | — (no 60 in prior) | 420.0 G (CV 3.69 %) | — | — |

**The rig reproduces the filtered input to within ~1 % across sessions a
week apart** — `7xadt6`'s batch-2 mean is statistically indistinguishable
from batch 1, and `9GMQYQ`'s −0.3 % is negligible even where n ≈ 100 makes
it "significant". This is strong validation of test consistency at the
CFC-180 level, despite the raw spike varying ×3 with stack wear (§5).

`RW5F61`'s lower level (420 G) and higher CV (3.69 %) reflect a
rested/re-set stack plus a specimen-specific level: its input climbs
+0.125 %/drop all session (R² = 0.89) as the stack re-compacts — the same
campaign-scale burn-in the 07-20 evening showed. The specimen effect and
stack state cannot be separated with the input channel alone (see the
[compaction analysis](drop-test-compaction-analysis.md) §1).

## 4. Transmissibility: batch 1 vs batch 2 (the requested comparison)

| specimen | batch 1 T | batch 2 T | change |
|---|--:|--:|---|
| `prc1kn` | 1.011 (CV 0.51 %, 07-21) | **1.026** (CV 0.57 %, 07-22) | +1.53 % (Welch p = 4.5e-46, d = 2.8) |
| `7xadt6` | 1.034 (CV 0.12 %, 07-20) | — | not computable (CH5-only export) |
| `9GMQYQ` | 1.027 (CV 0.45 %, 07-20) | — | not computable (CH5-only export) |
| `RW5F61` | 0.945–0.957 (5/13 in, different height) | — | not computable (CH5-only export) |

What the one available comparison says (figure
`04_prc1kn_transmissibility.png`):

* **Within-session precision reproduces beautifully** — CV 0.51 % → 0.57 %
  over ~95 stabilized drops in both campaigns. The TOP output also stayed
  put in absolute terms (477.4 → 489.8 G, +2.6 %).
* **The absolute T level shifted +1.5 % between back-to-back days on the
  same specimen.** Decomposition: TOP +2.6 % vs CH5 +1.0 %, so about a
  third of the T shift is the input side (stack state: raw spike 45→79 %
  FS on 07-21 vs 74→91 % on 07-22) and the rest is output-side coupling
  (mount re-seating). This is squarely inside the known session-to-session
  envelope (the 500drops pair moved 3.7 % from CH5 tape re-coupling alone).
* **Implication for ranking:** the batch-1 three-way gaps (prc1kn 1.011 vs
  9GMQYQ 1.027 vs 7xadt6 1.034, spanning 2.3 %) are the same size as this
  one-day same-specimen shift. Batch 2's prc1kn (1.026) lands on top of
  batch 1's 9GMQYQ (1.027). **Cross-session T differences of ≲2 % should
  not be read as geometry differences** — rank specimens within one session
  under one SOP, or normalize with a reference specimen dropped in every
  session. Within-session resolution (CV ~0.5 %, n ≈ 95) remains far finer
  than the ≥10 % differences the BO campaign targets.

## 5. Stack wear: the 07-22 session nearly saturated the input sensor

`prc1kn` 07-22 continued the same absorber stack's trajectory from the
07-20/07-21 evenings: CH5 raw spike **median 83 % FS, peaking at 91 %**
(8.6 kG of the 9,442.9 G full scale) — the closest any campaign has come to
clipping the input. The stack was *not* replaced before 07-23 — the lab
owns only the one stack (issue #88) — but its raw-spike growth largely
reset (`RW5F61` restarts at ~15–20 % FS after a 52 % first-drop
transient; part specimen effect, part recovery/re-handling — see the
[compaction analysis](drop-test-compaction-analysis.md)), then it
recompacted through 07-23 → 07-27 (7xadt6 ends at 70 %, 9GMQYQ at 77 %).
Meanwhile the CFC-180 input moved ≤1 % (§3) — compaction adds
high-frequency spike content, not low-frequency severity, exactly as the
07-20 campaign found.

Standing recommendations unchanged, now with harder evidence: refresh the
stack when CH5 raw exceeds FS/3 ≈ 3.1 kG (every batch-2 session except
RW5F61's first ~40 drops ran beyond it), and procure spare felt — see
[`drop-test-absorber-alternatives.md`](drop-test-absorber-alternatives.md)
for the durable-pad replacement that would end this treadmill.

## 6. Caveats

* The `prc1kn` batch-2 zips are byte-identical to
  `data/drop-tests/7-22-2026 prc1kn 100drops/` (same upload, committed
  twice); this analysis uses the batch-folder copy.
* Whether CH2–CH4 exist in the TP4 database for the three CH5-only sessions
  is unconfirmed (§2) — if they do, a re-export upgrades this analysis.
* The CH5-only sessions cannot separate specimen effects from stack state
  on the input channel; their per-specimen input differences (420–461 G)
  largely track stack wear order, not geometry.
* n = 1 physical article per geometry, as throughout the program.
* Session ID inside the batch-2 `9GMQYQ` files reads `9GMGYQ` (typo) and
  the `prc1kn` session ID (`prc1kn 100drops`) omits the stack composition;
  folder names carry the authoritative labels.
