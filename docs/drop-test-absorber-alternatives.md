# Durable alternatives to the felt stack — absorbers that don't need replacing

Answers @sgbaird's question on
[PR #86](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86):
*"suggest potential alternatives to felt that wouldn't require replacing."*

Context: the [60 in validation](drop-test-60in-5felts-analysis.md) showed the
current 4-felt + 1-cardboard stack is a consumable — cumulative compaction
tripled the raw CH5 base-plate spike (2.1 → 6.5 kG) over one 201-drop evening
and drove every OLS drift term — and the lab owns no spare felt, so the
"refresh every ~100 drops" rule can't currently be followed. A durable
absorber removes both the procurement problem and the drift.

## 1. What a replacement must reproduce

From the measured campaigns (60 in, ~5.5 m/s impact, carriage + acrylic plate):

| requirement | value | source |
|---|---|---|
| input pulse | ≈ half-sine, **~1.6 ms**, CFC-180 peak **~450–475 G** | 60 in validation §1–2 |
| CH5 raw head-room | worst-case raw \|peak\| **≤ FS/3 ≈ 3.1 kG** (9,442.9 G FS) | felt-sheet sweep §5 |
| trigger reliability | CFC-180 input comfortably above the trigger level on every drop | input-output analysis |
| stability | no monotonic drift over ≥ 100 drops/session (felt's failure mode) | 60 in validation §3 |
| output signal | preserve the ~460 G, CV ≤ 1.7 % top-vertex output — largely automatic, since the output is set by the specimen, not the input (306–462 G across a 7× input swing) | felt-sheet sweep §4 |

The raw-spike head-room requirement is the discriminating one: compacted
felt fails not by changing the CFC-180 input much (446 → 463 G over 100
drops) but by adding short high-frequency spike content that eats the raw
full-scale margin. Good replacements therefore need some **damping**, not
just compliance.

## 2. Candidates

Ordered roughly by fit. "Life" = expected shots before measurable change,
from vendor fatigue data and drop-tower practice.

| # | material / element | how it works | life | pulse effect vs felt | cost / sourcing | notes |
|--:|---|---|---|---|---|---|
| 1 | **Polyurethane elastomer pad** (solid PU sheet, ~40–80 Shore A, ½–1 in total) | elastic compression, moderate hysteresis | 10³–10⁴⁺ shocks | very similar; durometer + thickness tune peak/width | ~$20–40/ft² (McMaster PU sheet) | **This is the industry standard.** Commercial drop-shock machines (Lansmont, L.A.B., MTS) use urethane "programmers" precisely because they survive thousands of half-sine shocks with stable pulses. Buy 2–3 durometers and stack to tune. |
| 2 | **Sorbothane sheet** (Shore 00 50–70, ¼–½ in, ideally on top of a firmer PU/rubber base) | viscoelastic PU, very high damping (tan δ ≈ 0.5+) | rated ~10⁶ compressions | kills the high-frequency raw spike specifically — directly attacks the FS/3 head-room problem | ~$40–80/sheet (Sorbothane Inc., Amazon) | Best single-material answer to the raw-spike failure mode. Softer, so pulse widens somewhat; keep a firm layer beneath to avoid bottoming. |
| 3 | **Rubber sheet stack** (neoprene / EPDM / natural gum, ~½–1 in total; or a recycled-rubber horse-stall mat, ¾ in) | elastic + moderate damping | 10³–10⁴⁺ | similar to firm felt | stall mat ~$40–60 for 4×6 ft — cheapest per area by far | The pragmatic "buy it this week" option. Stall mats are made for years of repeated hoof impact; cut several 6×6 in pads from one mat and there are spares for a decade. |
| 4 | **Silicone rubber sheet** (30–50 Shore A) | elastic, best compression-set resistance of common elastomers | 10⁴⁺ | similar | ~$20–40/ft² | Most temperature-stable option if lab temperature swings become a concern (elastomers stiffen when cold). |
| 5 | **Microcellular PU foam** (PORON 4701 or similar) | engineered anti-compression-set foam | 10⁴⁺ (spec'd for repeated impact) | softer/longer pulse | ~$30–60/sheet (Rogers distributors) | The "felt-like feel without felt's compaction." Thinner sheets, so stack several. |
| 6 | **Metal springs** (die springs, Belleville washer stack, or wave springs under a striker plate) | purely elastic | effectively infinite | **changes the test**: pulse stretches to ~5–10+ ms, lower peak, near-zero damping → strong rebound | ~$20–50 | Zero wear and perfectly repeatable, but the pulse is no longer comparable to the felt-era half-sine, and the undamped rebound leans harder on the anti-rebound brake. Only worth it if a long-pulse input is ever wanted deliberately. |

**Not recommended:** EVA / polyethylene closed-cell foams (well-documented
compression set under repeated impact — same failure mode as felt, faster);
cork or cork-rubber (crumbles); crushable media (honeycomb, foam-in-place —
single-use by design).

## 3. Recommendation

1. **Primary: a two-layer permanent stack — firm polyurethane base
   (~½–¾ in, 60A-ish) + Sorbothane top layer (~¼–⅜ in).** The PU layer
   carries the load and sets the pulse width; the Sorbothane layer supplies
   the damping that felt currently provides, keeping the raw CH5 spike (not
   just the CFC-180 peak) inside the FS/3 budget. Total outlay roughly
   $60–120, once.
2. **Cheapest immediate fix: horse-stall-mat pads** (option 3). One mat
   yields many identical pads — even if an individual pad did slowly wear,
   swapping in a fresh identical pad is free, which *de facto* satisfies
   "doesn't require replacing" at the budget level.
3. Whatever is chosen, **tune empirically with a mini-sweep** (§4) rather
   than by durometer math — pad area, thickness, and carriage mass interact,
   and the felt-sheet sweep already provides the template.

Note that `T = TOP/CH5` already cancels most input drift, and a higher-range
base sensor remains the real long-term head-room fix (felt-sheet sweep §6) —
a durable stack is complementary to both, not a substitute.

## 4. Qualification / bridging protocol before switching the campaign

Any stack change re-anchors the input pulse, so historical comparability has
to be bought with a short bridging study:

1. **Mini-sweep** (felt-sheet-sweep template): 2–3 candidate thickness /
   durometer combinations × 5 drops at 60 in. Accept if CH5 raw worst case
   ≤ 3.1 kG, CFC-180 input within roughly ±20 % of the felt-era 450–475 G,
   pulse width ~1–2.5 ms, and TOP CV ≤ ~2 %.
2. **Burn-in + stability check:** elastomers soften slightly over their
   first load cycles (Mullins effect) and then stabilize — the opposite of
   felt's unbounded compaction. Run ~25 drops on the chosen stack and
   confirm the stabilized-OLS slope on CH5 and TOP is ≈ 0 (the existing
   analysis scripts do this out of the box). Keep the SOP's discarded
   warm-up drops.
3. **Bridge with a reference specimen:** re-run one already-characterized
   specimen (`prc1kn`, `7xadt6`, or `9GMQYQ`, n ≥ 25) on the new stack and
   log the offset in TOP and `T` vs its felt-era values, so pre- and
   post-switch campaigns can be compared.
4. **Ongoing monitor:** keep logging drops-on-stack; the CH5 raw-%FS trend
   (already emitted by the campaign scripts) is the wear alarm — on a good
   elastomer stack it should stay flat where felt climbed monotonically.

## 5. Caveats

- Life figures are from vendor fatigue data and shock-machine practice, not
  yet from this rig — the §4 burn-in check is what actually verifies "no
  drift" here.
- Elastomer stiffness is temperature-dependent (a cold lab morning reads as
  a harder hit); log lab temperature per session, or rely on `T` to cancel
  it as it does felt wear.
- Pad **area** matters as much as durometer: a smaller pad footprint is an
  easy stiffness/pulse-width tuning knob if the first sheet bought is too
  soft or too hard.
- Carriage + plate mass isn't recorded in the repo; weigh it once and note
  it in the protocol doc — it makes any future pulse-shape sizing (elastomer
  or spring) calculable instead of trial-and-error.
