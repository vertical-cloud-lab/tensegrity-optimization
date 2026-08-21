# Guide-rod cleaning/greasing A/B — does impact velocity recover? (2026-08-10)

**Data:** [`data/drop-tests/pre-post-grease/`](../data/drop-tests/pre-post-grease/)
(Box `m3jsyavz2h2c7ck8pe496j6x8utm8bll`, TP4 session "Drop Speed Decay") ·
**Script:** [`scripts/analysis/drop_test_pre_post_grease_analysis.py`](../scripts/analysis/drop_test_pre_post_grease_analysis.py) ·
**Requested by:** @me-madsen (PR #86). Ten drops at 60 in, arrangement B
(1/2 in PU), specimen 2: Signals 1–5 before cleaning/greasing the guide
rods, Signals 6–10 after (6.4 min maintenance gap). Same `B2` cell and
capture settings as the abc123 blind crossover, so that campaign supplies
matched references: healthy tower (08-04) Δv = 5.276–5.347 m/s; damaged
tower (08-05/06, B blocks) 4.27–4.38 m/s.

> **Correction (08-21, SOBOL-campaign analysis §2):** the absolute Δv
> levels here are mild **underestimates** (TP4 series table: 4.62 m/s mean
> vs the pipeline's 4.44/4.68 split) because the pre-trigger baseline was
> starting to ride the mat-contact foot. The greasing *step* is real and
> confirmed on the TP4 numbers; the "still ~28 % of the deficit
> outstanding" framing understated the recovery, which continued with
> traffic — by campaign week (08-19/20) the tower was at 5.3–5.5 m/s,
> effectively healthy. See
> [`drop-test-sobol-campaign-analysis.md`](drop-test-sobol-campaign-analysis.md) §3.

## 1. Answer: yes — a real +5.4 % velocity step, but only ~28 % of the damage deficit

| | before (S1–5) | after (S6–10) | change | p (Welch) |
|---|--:|--:|--:|--:|
| **base-plate impact Δv (m/s)** | **4.439 ± 0.057** | **4.679 ± 0.053** | **+5.4 %** | 1.3e-4 |
| specimen-hop delay `t_second` (ms) | 18.01 ± 0.07 | 18.94 ± 0.06 | **+5.1 %** | 1.8e-8 |
| input pulse FWHM (ms) | 2.228 ± 0.053 | 2.415 ± 0.054 | +8.4 % | 5.4e-4 |
| CH5 input CFC-180 (G) | 219.0 ± 6.4 | 211.4 ± 6.7 | −3.5 % | 0.11 (n.s.) |
| `T` = TOP/CH5 (CFC-180) | 1.0348 ± 0.0020 | 1.0297 ± 0.0018 | −0.5 % | 3.2e-3 |
| `e_rebound` | 0.0199 ± 0.0003 | 0.0198 ± 0.0003 | −0.3 % | 0.77 (n.s.) |

([Δv figure](../data/drop-tests/pre-post-grease/figures/01_dv_pre_post.png) ·
[witness channels](../data/drop-tests/pre-post-grease/figures/02_witness_channels.png))

Referenced to the healthy-tower `B2` level (5.31 m/s):

| | est. arrival speed | % of free fall (5.47 m/s) | energy delivered | equivalent height |
|---|--:|--:|--:|--:|
| before | 4.57 m/s | 83.6 % | 70 % | **41.9 in** |
| after | 4.82 m/s | 88.1 % | 78 % | **46.6 in** |
| healthy (08-04) | 5.31 m/s | 97 % | 94 % | 56.6 in |

The greasing recovered **(4.679 − 4.439)/(5.31 − 4.439) ≈ 28 %** of the
deficit the pin break opened up. The tower is distinctly better than the
08-05/06 state (the pre block itself sits at/just above that 4.27–4.38
band) but still delivers only ~78 % of the nominal 60 in drop energy — the
issue #92 pin/rail repair remains the main event; grease alone does not
close the gap.

## 2. Why the +5.4 % is a genuine arrival-velocity gain (not a mat or pause artifact)

The intervention is confounded with a 6.4 min pause, and PU mats recover
with rest — so the Δv step alone would be ambiguous. Two independent
witnesses resolve it:

- **The specimen-hop delay reproduces the step.** `t_second` (the ballistic
  top-vertex hop found in the abc123 analysis) scales with arrival velocity
  and lives on the *output* sensor, independent of the base-plate rebound.
  It steps **+5.1 %** exactly where Δv steps +5.4 % — two channels, one
  number. Consistently, `e_rebound = g·t_second/(2Δv)` is unchanged
  (0.0199 → 0.0198), and matches the 0.019 measured for specimen 2 in the
  blind crossover — the specimen constant survives a third session.
- **The mat state did not reset at the pause.** The input pulse FWHM grows
  monotonically 2.15 → 2.48 ms straight through the maintenance gap
  (+1.4 %/drop on both sides, no step down after the rest). If the Δv jump
  were mat recovery, the width would have reset too. It didn't — the mat
  kept softening on its own trajectory while Δv jumped.

So: rails faster, mat unchanged in its behavior. (The −3.5 % in filtered
input peak despite higher speed is the softening mat trading peak for
duration — another reason peak G is not a velocity metric.)

## 3. The within-block decline is mostly the mat, not the rails re-degrading

Both blocks show a significant Δv decline (−0.79 and −0.70 %/drop,
p = 0.005 each) — presumably what motivated the session name "Drop Speed
Decay". But the arrival-velocity witness says the *carriage* isn't slowing:
`t_second` is flat within both blocks (p = 0.45–0.48), while pulse width
grows +1.4 %/drop. A Δv decline with flat hop delay and a lengthening pulse
is a **rebound-side (mat softening) effect** — the warming PU returns a
little less velocity each hit — not friction re-eating the greasing gain.
Within these 5-drop blocks the greasing benefit shows no sign of eroding.

Practical corollary: when tracking rig health, read **Δv together with
`t_second` and pulse width**. Δv alone conflates arrival speed (rails) with
restitution (mat state).

## 4. On the proposed 100-drop run — yes, worth it, with three specifics

> **Outcome (08-11/08-12):** the run happened — 55 + 100 drops, analyzed in
> [`drop-test-speed-decay-analysis.md`](drop-test-speed-decay-analysis.md).
> Headline: no decay with drop count in steady state (the 100-drop session
> is flat at Δv slope p = 0.75); a one-time ~3 % settling transient in the
> first ~39 drops after the greasing; the gain largely held (steady
> 4.55–4.66 m/s vs 4.44 pre-grease).

A 100-drop campaign is the right way to answer what 5+5 cannot: whether the
greasing gain holds at campaign scale (grease migrating/collecting debris
is exactly the WD-40 failure mode from the hook episode). Suggestions:

1. **Track `t_second` (or Δv corrected by pulse width) as the rail-health
   series**, not raw Δv — §3 shows Δv drifts ~0.8 %/drop from the mat
   alone, which would masquerade as "velocity decay" over a long run.
2. **Expect the mat trend to dominate the raw series.** Extrapolated
   naively, the mat-side drift would eat the entire +0.24 m/s step in ~7
   drops of Δv reading — while the actual arrival velocity stays put. Log a
   pause or two mid-run (~5 min) to watch the width partially reset.
3. **The bar for "healthy" is 5.28–5.35 m/s Δv in this exact
   configuration** (B2, 60 in). Anything under ~5.2 m/s at session start
   means the tower is still eating energy — the post-grease 4.68 m/s says
   that gauge will stay red until the pin/rail repair. A first block that
   *reaches* ~5.3 m/s after the repair is the acceptance test.

## 5. Caveats

- n = 5 per condition, one session, one specimen/arrangement — the step is
  decisive (p ≤ 1e-4 on two independent channels) but its magnitude is a
  single-session estimate.
- Δv→arrival calibration assumes the healthy-session restitution
  (Δv/arrival = 0.971); the softer post-grease mat state shifts that ratio
  slightly, which is why the `t_second` corroboration matters more than the
  third significant figure of the arrival estimates.
- The pre block was already above the 08-05/06 damaged floor — either the
  rails partially recovered with 4 days of rest, or earlier handling
  (issue #92 traffic) helped; there's no instrumented drop from
  immediately before this session to pin the starting state.
- Ringdown fits are incidental here; S3's fit is flagged unusable
  (r² collapse from the secondary event), consistent with the known
  fit-window limitation.
