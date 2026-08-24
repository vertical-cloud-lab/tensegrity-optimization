# Polyurethane rubber vs felt+cardboard: paired absorber A/B test

Analysis of the paired test posted by @me-madsen on PR #86: the same
specimen (**`bpx68c`**) dropped 5 times on the incumbent **4 felt +
1 cardboard** stack (session `bpx68c - 60 in - 4 flt 1 crdbrd`,
2026-07-30 11:19–11:23) and then 5 times on the **new polyurethane
rubber sheets** (session `bpx68c - Polyurethane Rubber`, 11:41–11:45)
— back-to-back, same mount, ~18 min apart. This is the first data on
the durable-absorber replacement proposed in
[`drop-test-absorber-alternatives.md`](drop-test-absorber-alternatives.md)
(issue #88), and it doubles as the **mini-sweep step (§4.1)** of that
doc's qualification protocol.

Data: `data/drop-tests/pu-vs-felt/raw/` (committed zips, full 4-channel
1.25 MHz / 20 ms exports); script:
`scripts/analysis/drop_test_pu_vs_felt_analysis.py`; metrics:
`data/drop-tests/pu-vs-felt/figures/pu_vs_felt_metrics.json`. Channel
map unchanged: CH2–CH4 = top-vertex key-seat tri-axis ("TOP" output),
CH5 = single-axis base plate (input + trigger). The PU session ID does
not state a height; the full-pulse Δv (§2) matches free fall from 60 in,
so both sessions are treated as 60 in.

Two convention notes forced by the 20 ms capture format (documented in
the script header): baseline = full-record median (the ~1 ms pre-trigger
is contaminated by the pulse onset), and the impact is located on the
CFC-180-filtered CH5 with a ±4 ms peak walk (the PU pulse peaks
1.6–3.5 ms into the record, far from the raw trigger spike, and its
half-max width alone is ~2.7 ms).

## 1. Head-room: the PU stack solves the saturation problem outright

| CH5 (base plate) | felt+cardboard | polyurethane | change |
|---|--:|--:|--:|
| raw \|peak\| | 1,293–1,584 G (13.7–16.8 % FS) | **371–496 G (3.9–5.2 % FS)** | **−71 %** |
| worst case vs FS/3 target (3,148 G) | 0.50× | **0.16×** | — |

The felt stack's failure mode — the high-frequency spike content that
compaction adds until the raw peak eats the 9,443 G full scale (worst
recorded: 91 % FS on 07-22) — is simply absent on the rubber. Every PU
drop sits at ~1/7 of the FS/3 head-room target
(`figures/03_headroom.png`). On raw head-room alone, PU retires both the
felt-wear refresh rule and the compaction-tracking overhead of
[`drop-test-compaction-analysis.md`](drop-test-compaction-analysis.md).

## 2. The PU stack is a much softer programmer: pulse ×2 longer, peak −54 %

Per-drop input metrics (CFC-180, `figures/01_input_pulses.png`):

| metric | felt+cardboard | polyurethane | Welch p |
|---|--:|--:|--:|
| CH5 input peak (G) | 407.6 (CV 2.8 %) | **186.2 (CV 25.7 %)** | 3.1e-04 |
| pulse width (ms, half-max) | 1.67 | 2.5–4.5 | 1.1e-02 |
| full-pulse Δv (m/s) | 6.21 (CV 0.2 %) | 5.55 (CV 4.2 %) | 3.0e-03 |
| TOP output peak (G) | 411.3 | 182.1 | 2.6e-04 |

The full-pulse Δv brackets free fall from 60 in (5.47 m/s) plus a small
rebound in both conditions — the same momentum is being absorbed, spread
over roughly twice the time. That is exactly what a softer elastomer
programmer should do; nothing here says the material is wrong, only that
**this particular stack (thickness/durometer/sheet count as tested) is a
substantially gentler operating point than the felt era**. The felt-era
comparability criterion from the qualification protocol (input within
~±20 % of 450–475 G) is missed by ~60 %.

Note the felt session itself shows textbook intra-session compaction
even in 5 drops: input 390 → 419 G (+7 %), raw 1,293 → 1,584 G — the
drift PU is meant to eliminate.

## 3. The one real problem: PU input repeatability (n = 5) is poor and bimodal

The five PU drops split into two clusters
(`figures/01_input_pulses.png`, lower left):

| cluster | drops | CH5 CFC-180 | width | Δv total |
|---|---|--:|--:|--:|
| "stiff" | S3, S5 | 234.7 / 238.1 G | 2.5 ms | 5.8 m/s |
| "soft" | S1, S2, S4 | 134–173 G | 3.3–4.5 ms | 5.3–5.5 m/s |

Within the stiff cluster the input repeats to 1 % — so the rubber *can*
deliver a tight pulse — but drop-to-drop the stack toggles state
(order: soft, soft, stiff, soft, stiff; cadence a uniform 47 s, so it is
not rest-time-driven). Momentum is conserved across all five (Δv CV
4.2 %), meaning the pulse *shape* changes, not the impact severity: the
stack's effective stiffness differs between drops. Prime suspects, in
order: **sheet seating/air gaps between loose sheets** (a slightly
bowed or laterally shifted sheet stack compresses very differently),
carriage/plate contact geometry, and early-cycle Mullins softening. The
TP4's own series table shows the same clustering, so it is not an
analysis artifact. The felt-era input CV at n = 5 was 0.2–2.1 %
(felt-sheet sweep); 25.7 % is not usable as a fixed input reference.

**Transmissibility absorbs almost all of it** — which is the strongest
argument yet for `T` as the objective: T CV is 1.3 % on PU (0.4 % on
felt) despite the 26 % input swing.

## 4. Transmissibility: T = 0.976 on PU vs 1.009 on felt — an input-spectrum effect

Per-drop `T = TOP/CH5` (`figures/02_transmissibility.png`):

| | felt+cardboard | polyurethane |
|---|--:|--:|
| T mean ± sd | 1.009 ± 0.004 (CV 0.4 %) | **0.976 ± 0.012 (CV 1.3 %)** |
| Welch | p = 2.4e-03, d = −3.6 | |

The same specimen, same mount, same morning, "attenuates" on rubber and
mildly amplifies on felt. This is not a specimen change — it is the
input spectrum: the PU pulse is ~2× longer, so its energy sits at lower
frequencies that excite the structure's resonances less. Two
consequences for the program:

1. **T values are only comparable within one absorber configuration.**
   The felt-era catalog (T = 0.94–1.22 across specimens/sessions) does
   not translate to the PU stack; switching absorbers re-anchors the
   objective, exactly as the bridging step (§4.3 of the alternatives
   doc) anticipated. `bpx68c`'s felt-stack T of 1.009 lands in the
   familiar near-unity band with `prc1kn` (1.011)/`9GMQYQ` (1.027).
2. Within the PU configuration T still discriminates finely (CV 1.3 %
   at n = 5, and even tighter — ~0.1 % — within the stiff cluster), so
   the objective survives the switch once the input state is stabilized.

A second-order observation worth tracking: on PU, per-drop T correlates
with the input level (softest drop S4: T = 0.959; stiffest S5: 0.987) —
at longer pulses the structure attenuates slightly more, which is the
frequency-response story again, now visible *within* a session.

## 5. Qualification verdict vs the §4 mini-sweep acceptance criteria

| criterion ([alternatives doc §4.1](drop-test-absorber-alternatives.md)) | result | verdict |
|---|---|---|
| CH5 raw worst case ≤ 3.1 kG | 496 G (6.3× margin) | ✅ pass |
| CFC-180 input within ~±20 % of 450–475 G | 186 G (−60 %) | ❌ too soft |
| pulse width ~1–2.5 ms | 2.5–4.5 ms | ⚠️ at/over the long edge |
| TOP CV ≤ ~2 % | 26.8 % (input-driven) | ❌ fail (T CV 1.3 % ✅) |

**Read: right material, wrong operating point + an unstabilized stack.**

> **Resolved (07-30 p.m.)** — the four-arrangement sweep in
> [`drop-test-pu-configs-analysis.md`](drop-test-pu-configs-analysis.md)
> ran steps 1–2 below and answers both open items: the **1/4 in sheet
> alone** lands the input at 371 G / 1.66 ms (vs felt's 408 G / 1.67 ms)
> and passes all seven criteria, and the bimodality here was the **two
> sheets stacked and seating inconsistently** — every drop in this run
> matches either the "both sheets" or the "1/2 in alone" point of that
> sweep. Properly seated, the same two-sheet stack gives input CV 1.7 %
> instead of 25.7 %; a single sheet avoids the interface entirely.

Recommended next iteration, in order:

1. **Stiffen the operating point** — remove sheets (or use a thinner /
   firmer-durometer pad) until the CFC-180 input lands back near
   ~350–450 G and the width near 1.5–2 ms. The felt-sheet sweep's ×0.36
   per-sheet model was for felt; the PU sheet count/thickness actually
   used here is not recorded (see open questions), so this is a 2–3
   condition mini-sweep of 5 drops each.
2. **Fix the stack state** — seat the sheets flat with no air gaps and
   restrain them laterally (tape/frame/dowel pins); loose rubber sheets
   sliding or bowing is the most likely cause of the soft/stiff
   toggling. Re-check: 5 drops with input CV back under ~3 % passes.
3. **Then run the §4.2 stability check** — ~25 drops, stabilized-OLS
   slope ≈ 0 (the campaign scripts do this out of the box). If the
   Mullins settling is real, the first few drops will soften slightly
   and then flatten — the opposite signature of felt.
4. **Check the CH5 trigger level before the next PU session** — PU raw
   peaks are 371–496 G; if the trigger is still at the felt-era
   300–500 G, the margin is as low as 1.2× and a slightly gentler
   configuration (step 1 notwithstanding) could fail to trigger. With
   the HF spike gone there is room to drop the trigger to ~150–200 G.
5. Once 1–3 pass, run the **§4.3 bridging campaign** (a characterized
   specimen, n ≥ 25) to anchor PU-era T against the felt-era catalog.

## 6. Caveats and open questions

- **n = 5 per condition, one specimen, one session each** — all
  comparisons are paired and decisive (|d| ≥ 2.8), but the PU
  repeatability diagnosis (bimodal, seating-driven) is a hypothesis
  from five points; the 25-drop check settles it.
- **PU stack composition not recorded** — sheet count, thickness, and
  durometer of the rubber as tested are not in the session metadata.
  @me-madsen: logging these (plus whether the sheets were loose-stacked
  or restrained) in the TP4 session ID would make the next mini-sweep
  interpretable, same as the felt-era honest-label convention.
- **PU session height assumed 60 in** from Δv; the session ID doesn't
  say.
- `bpx68c` has no prior campaigns in the repo, so there is no felt-era
  baseline for this specimen beyond the 5 felt drops taken here.
- The felt session's raw level (14–17 % FS) reflects a rested/fresh
  stack state; the felt numbers here are a *good-day* felt reference,
  not the worn-stack worst case (up to 91 % FS) that motivated the
  replacement.
