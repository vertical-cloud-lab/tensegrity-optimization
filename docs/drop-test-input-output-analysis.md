# Input-output accelerometer drop-test analysis (T3 prisms)

Analysis of @ctrhjk's **input-output (transmissibility)** drop series
([PR #67](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/67#issuecomment-4804858562),
drop height 13 in). A single-axis accelerometer on the **bottom acrylic plate**
is the **input** sensor (CH5, now the triggered channel) and a tri-axis
accelerometer hot-glued to the **top vertex** is the **output** sensor
(CH2/CH3/CH4). Four distinct-geometry specimens (`practice`, `n0jdwk`, `yqpmx1`,
`h8Lbev`) were each dropped **five times**. **The bungees were removed for this
series (pretension off)**, so the bungee-driven lift-off that contaminated the
earlier drops is gone.

Raw data + channel map: [`data/drop-tests/input-output/`](../data/drop-tests/input-output/).
Reproduce with:

```bash
pip install numpy scipy matplotlib
python scripts/analysis/drop_test_input_output_analysis.py
```

## Method

- **Channels / roles.** CH5 = single-axis sensor on the base plate = **input**
  (full scale 9442.9 G; trigger moved here, 1000 G). CH2/CH3/CH4 = tri-axis
  sensor on the top vertex = **output**; the output is taken as the tri-axis
  resultant magnitude √(CH2²+CH3²+CH4²).
- **Windowed peak search.** The impact is located on the triggered CH5 channel
  within the first 10 ms (lands at t ≈ 3.9 ms, consistent with the 2 %/4 ms
  pre-trigger), and peaks are taken in a ±1.5 ms window around it — not a global
  0.2 s max (which is usually a later mount/ringdown lobe).
- **SAE J211 filtering.** Raw peaks on a lightly damped lattice are dominated by
  sensor ringing (PSD energy out past 10 kHz), so the CFC-180 (≈300 Hz) column
  is the physically meaningful structural number; CFC-1000 (≈1650 Hz) shown for
  reference.
- **Transmissibility.** `T = output / input` on the CFC-180 peaks — this is the
  candidate single-number objective the input-output design is meant to yield.

## Results

### Per-specimen aggregates (mean ± 1σ over 5 drops; CV %)

| specimen | input CH5 CFC-180 (G) | output CFC-180 (G) | **T = OUT/IN** | input CV | output CV | T CV |
|---|--:|--:|--:|--:|--:|--:|
| `practice` | 244 ± 2 | 285 ± 4 | **1.17 ± 0.01** | 0.7 % | 1.3 % | 0.8 % |
| `n0jdwk`   | 244 ± 3 | 290 ± 10 | **1.19 ± 0.05** | 1.3 % | 3.5 % | 4.6 % |
| `yqpmx1`   | 241 ± 4 | 230 ± 2 | **0.96 ± 0.02** | 1.6 % | 0.7 % | 2.1 % |
| `h8Lbev`   | 235 ± 4 | 256 ± 1 | **1.09 ± 0.02** | 1.7 % | 0.5 % | 2.0 % |

All **20/20 drops triggered cleanly** (vs. the 3/4 *failures* in the prior
acrylic series and 0/8 in the clip-height sweep).

### Per-drop detail (CFC-180, G)

| specimen | drop | input | output | T |
|---|--:|--:|--:|--:|
| `practice` | 1–5 | 242–246 | 278–287 | 1.15–1.17 |
| `n0jdwk`   | 1–5 | 239–247 | 273–298 | 1.11–1.24 |
| `yqpmx1`   | 1–5 | 238–248 | 228–233 | 0.93–0.98 |
| `h8Lbev`   | 1–5 | 231–241 | 254–257 | 1.05–1.11 |

Full per-drop table (raw / CFC-1000 / CFC-180, pulse width, Δv) is printed by
the script.

### Figures

- `figures/01_input_output_impact.png` — input (base CH5) vs output (vertex
  tri-axis) CFC-180 traces, all five drops overlaid per specimen.
- `figures/02_transmissibility_bars.png` — transmissibility per specimen
  (mean ± 1σ), with CV annotated.
- `figures/03_input_repeatability.png` — input CFC-180 peak per drop — the
  bungee-free strike is now reproducible (≈235–248 G everywhere).
- `figures/04_output_psd.png` — output PSD per specimen (raw peaks are
  ringing-dominated, justifying CFC-180).

## Findings

1. **The input-output design works.** Every drop triggered and gave a clean
   impact, the input (base-plate) peak is nearly constant across all specimens
   and drops (235–248 G CFC-180, ≤1.7 % CV), and the output and the derived
   transmissibility are repeatable within a specimen (T CV 0.8–4.6 %). Removing
   the bungees is what makes the input controlled and reproducible.

2. **Transmissibility now discriminates geometry.** Unlike the prior vertex-only
   peaks (229–284 G, indistinguishable), `T` separates the four specimens:
   `yqpmx1` is the only **attenuator** (T ≈ 0.96, vertex sees less than the
   base), `h8Lbev` ≈ 1.09, and `practice`/`n0jdwk` ≈ 1.17–1.19. Because the
   input is held constant, this between-specimen spread is a genuine
   structural-response difference, not input scatter — i.e. `T` (or
   equivalently the output peak at fixed input) is a usable BO objective.

3. **A mild within-run drift across the five drops.** For `n0jdwk`, T climbs
   1.11 → 1.24 over drops 1–5 (output rises while input holds); `h8Lbev` and
   `practice` show a smaller upward creep that then plateaus. This is most
   likely progressive seating/loosening of the hot-glued vertex mount or minor
   cyclic softening of the structure — worth watching for the planned 20-drop
   cyclic tests, and an argument for a rigid z-aligned mount over hot glue.

## Caveats

- **n = 1 specimen per geometry** (five repeat *drops*, not five specimens), so
  the between-geometry T differences need replicate specimens before they back a
  BO model.
- `practice` is an uncatalogued shakedown structure; treat its numbers as a
  method check only.
- **Output = tri-axis resultant** assumes the vertex sensor's three axes are
  orthogonal and well seated; the hot-glue mount is not a verified orthonormal
  frame, so the resultant is robust to mount rotation but the per-axis split is
  not yet trustworthy.
- 200 ms window only — Δv here is the partial-pulse value over the ±1.5 ms
  impact window (≈2.8–3.0 m/s, consistent across specimens), not the full
  ringdown.
- Geometry IDs (`n0jdwk`, `yqpmx1`, `h8Lbev`) still need to be tied back to the
  original tensegrity design parameters (an Audrey/Achris question) before the
  T values can be regressed against geometry.
