# Why the raw-peak saturation audit is bandwidth-dependent (issue #89)

Follow-up to `analysis/issue-89-min-sample-rate`, quantifying its caveat
that "the spike reads ~1,900 g at 25 kHz vs ~6,000 g at 125 kHz" and what
that means for the saturation audit / FS-3 head-room rule that qualified
the BO campaign operating point (`docs/drop-test-felt-sheet-analysis.md`,
`scripts/analysis/drop_test_60in_5felts_analysis.py` @ 32b009f).

## Data

The 25 TP4 captures in `prc1kn - set 1 - 1.zip` (repo root): 200 ms @
125 kHz, CH2–4 top-vertex tri-axis, CH5 plate input/trigger (full scale
9,442.9 g), session "prc1kn 60in - 4 felt 1 cardboard", 2026-07-21.

## What is measured

1. **Crest-attenuation curve** — the CH5 raw impact peak of the same 25
   events re-read through low-pass cutoffs from the native 18.75 kHz
   passband down to 100 Hz. The "raw peak" is not a physical invariant:
   it is the peak of the band-limited rendering, and the contact spike's
   energy extends to several kHz, so the recorded peak scales strongly
   with the recording bandwidth.
2. **TP4 rate ladder** — the same peaks re-recorded TP4-style (low-pass
   at the 0.15·fs passband, then subsample) at each selectable rate:
   recorded peak, % of full scale, apparent head-room, and the factor by
   which the FS/3 threshold would have to be rescaled at that rate.
3. **Silent-clipping demonstration** — every capture's CH5 scaled ×2 so
   the true 125 kHz peak exceeds full scale on 24/25 captures,
   hard-clipped at ±FS (the analog rail), then viewed at each rate: does
   the audit's over-FS / clip-run detection fire, and how much does the
   clipping bias the CFC-180 peak (and hence T = TOP/CH5)?

## Results

| rate | recorded CH5 raw peak (median) | % FS | apparent head-room | clip detection (×2 demo) |
|--:|--:|--:|--:|--:|
| 125 kHz | 6,043 g | 64 % | ×1.6 | 24/25 over-FS, 23/25 clip-run |
| 50 kHz | 2,955 g | 31 % | ×3.2 | 0/25 |
| 25 kHz | 1,874 g | 20 % | ×5.0 | 0/25 |
| 5 kHz | 977 g | 10 % | ×9.7 | 0/25 |

- The attenuation factor at 25 kHz spans 0.29–0.40 across 25 nominally
  identical drops, so a rescaled threshold (FS/3 → ~975 g at 25 kHz) is
  only order-of-magnitude stable, and it depends on the spike's spectral
  shape (contact materials/stiffness) — it does not transfer across
  operating points.
- In the clipping demo the CFC-180 peak is depressed 4.4 % (median),
  inflating T ×1.05 — identical at every rate, because the corruption is
  baked in at the analog stage while its *detectability* dies with the
  recording bandwidth. The campaign's drop-to-drop CV of T is ~0.5 %, so
  even this mild clipping (~22 % of the spike chopped) is a ~10σ
  systematic bias; the felt-sheet sweep's real clipping produced T = 2.28
  vs ~1.0.
- Even 125 kHz is itself a band-limited view (18.75 kHz passband): the
  recorded peak is a lower bound on the true analog peak, so recorded
  head-room is an upper bound on real head-room. The FS/3 rule's factor
  of 3 absorbs some of this, but only at 125 kHz.

## Conclusion

Sample rate should be chosen per purpose: production campaign drops can
run at 25 kHz (per `analysis/issue-89-min-sample-rate`), but the
saturation audit is only meaningful at 125 kHz — qualification of any new
operating point (height, felt count, stiffer specimen class) and periodic
sentinel checks should stay at 125 kHz, and FS-fraction / head-room
numbers must never be compared across rates.

## Files

- `raw_peak_bandwidth.py` — reproducible analysis
  (`python raw_peak_bandwidth.py --zip "prc1kn - set 1 - 1.zip" --out figures`)
- `figures/raw_peak_bandwidth_metrics.json` — per-rate ladder, clip-demo
  detection/bias summaries
- `figures/01_crest_attenuation.png` — peak vs bandwidth + what the audit
  would report per rate
- `figures/02_silent_clipping.png` — the ×2 clipping demo at 125 vs 25 kHz
