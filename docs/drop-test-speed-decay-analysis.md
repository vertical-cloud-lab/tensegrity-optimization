# Does impact velocity decay over 100 drops? (2026-08-11 / 08-12)

**Data:** [`data/drop-tests/speed-decay/`](../data/drop-tests/speed-decay/)
(Box `i2hpksf19h9w84bk26ed2n91tf7i4cnm` = "Drop Speed Decay 2", 55 drops,
08-11; Box `cy7ijzs8cx4gkhic133z1zoaecwsl350` = "Drop Speed Decay 3",
100 drops, 08-12) ·
**Script:** [`scripts/analysis/drop_test_speed_decay_analysis.py`](../scripts/analysis/drop_test_speed_decay_analysis.py) ·
**Requested by:** @me-madsen (PR #86) — the 100-drop follow-up proposed in
the [greasing A/B analysis](drop-test-pre-post-grease-analysis.md). Both
sessions at 60 in, arrangement B (1/2 in PU), specimen 2 — the `B2`
reference cell, same capture settings as `abc123-blind` (100 ms record,
2 ms pre-trigger, 150 G trigger). 155/155 captures triggered cleanly at a
~41 s cadence; session 2 was interrupted by a **9.7 min pause after
drop 39**; session 3 ran uninterrupted.

> **Correction (08-21, SOBOL-campaign analysis §2):** the Δv values in this
> doc are **underestimates**. By these sessions the carriage was arriving
> fast enough that mat contact begins before the 2 ms pre-trigger window,
> so the pre-trigger baseline rides a contact foot that biases the Δv
> integral low (and increasingly so as the mat warms within a session).
> The TP4 series tables (committed in `raw/`) read 4.92 / 4.99 m/s for
> sessions 2/3 — ~0.3–0.4 m/s above the pipeline values below — and show
> session 2 *rising* slightly rather than declining, so the "one-time
> post-grease settling" in §2 is largely the foot artifact. The headline
> conclusion (no cumulative decay with drop count) is unchanged. See
> [`drop-test-sobol-campaign-analysis.md`](drop-test-sobol-campaign-analysis.md)
> for the corrected estimator and the tower's subsequent full recovery.

## 1. Answer: no decay with drop count in steady state

The 100-drop uninterrupted session is statistically **flat** in every
velocity channel ([trend figure](../data/drop-tests/speed-decay/figures/01_dv_trend.png)):

| session 3 (n = 100) | mean | CV | slope (%/drop) | end-to-end | p |
|---|--:|--:|--:|--:|--:|
| **impact Δv (m/s)** | **4.623** | **0.54 %** | **+0.0006** | **+0.1 %** | **0.75 (n.s.)** |
| hop delay `t_second` (ms) | 19.84 | 0.63 % | −0.001 | −0.1 % | 0.54 (n.s.) |
| input pulse FWHM (ms) | 2.580 | 1.7 % | −0.011 | −1.0 % | 0.03 |
| CH5 input CFC-180 (G) | 195.1 | 1.6 % | +0.020 | +1.9 % | 1.3e-3 |

This is the tightest Δv session on record at 60 in (CV 0.54 % over
100 drops), and both the primary channel and the arrival-velocity witness
agree: **the carriage arrives at the same speed on drop 100 as on
drop 2.** The "end velocity" at the close of each session confirms it —
session 3's last five drops (4.650 m/s) sit exactly on its session mean.
There is no wear-down trend for a longer campaign to worry about at this
scale.

Session 2 (the evening before) is the qualifier: it **did** decline —
Δv −2.8 % end-to-end (−0.053 %/drop, p = 9.6e-12) — but the decline lives
entirely in its first 39 drops (−0.069 %/drop, p = 3.8e-7); after the
9.7 min pause the remaining 16 drops are flat (slope p = 0.88). So the
two sessions together bracket the behavior: a **one-time settling
transient of ~3 % after rail maintenance, complete within ~40 drops, and
no ongoing decay afterwards.**

## 2. Reading the trend attribution

([witness figure](../data/drop-tests/speed-decay/figures/02_witness_channels.png))

- **Session 2's decline was (mostly) real arrival-velocity settling, not a
  mat artifact.** Unlike the within-block "decay" of the greasing session
  — where Δv fell while the hop delay stayed flat (mat rebound fading) —
  here `t_second` fell **with** Δv (−2.3 % vs −2.8 % over the session,
  `e_rebound` flat at p = 0.12). Two channels agreeing means the carriage
  genuinely arrived a little slower as the session progressed. The obvious
  candidate is the fresh grease film redistributing under traffic: this was
  the first campaign after the 08-10 cleaning/greasing, it started exactly
  at the post-grease level (first drops 4.77/4.69 vs the 08-10 post block's
  4.679), and the slide stopped for good ~40 drops in. Session 3 shows the
  settled regime: only drop 1 is elevated (4.748, after overnight rest),
  and drops 2–100 hold 4.622 ± 0.024 m/s.
- **The mat bedded in during session 2 and then stopped changing.** The
  input pulse FWHM grew +9.1 % (2.31 → 2.60 ms, saturating) while the raw
  CH5 contact spike fell **−44 %** (386 → ~245 G) — the classic
  fresh-elastomer bedding-in signature. Session 3 starts with a partial
  overnight width recovery (2.43 ms) that is erased within ~5 drops, then
  holds 2.58 ms all day with the raw spike flat at ~245 G. At 100-drop
  scale the 1/2 in PU mat has **no felt-style compaction treadmill**: it
  works in once and stays put, with CH5 never above 4.1 % of full scale.
- **Transmissibility, incidentally:** `T`(CFC-180) = 1.024 (session 2) /
  1.014 (session 3), with a tiny within-session drift (−0.5 % end-to-end,
  p = 4.7e-21, r² = 0.60 in session 3) of the familiar output-side kind.
  Nothing here changes the objective-metric picture.

## 3. Where the tower stands after greasing

Arrival estimates via the healthy-`B2` calibration (Δv/arrival = 0.971):

| state | Δv (m/s) | est. arrival | % free fall | equiv. height |
|---|--:|--:|--:|--:|
| pre-grease (08-10) | 4.439 | 4.57 | 83.6 % | 41.9 in |
| post-grease block (08-10) | 4.679 | 4.82 | 88.1 % | 46.6 in |
| session 2 steady (drops 40–55) | 4.553 | 4.69 | 85.7 % | 44.1 in |
| **session 3 (the settled regime)** | **4.623** | **4.76** | **87.0 %** | **45.4 in** |
| healthy reference (08-04) | 5.28–5.35 | 5.31 | 97 % | 56.6 in |

Two takeaways:

1. **The greasing gain held.** Steady state sits at 4.55–4.66 m/s across
   both days — about **75 % of the +0.24 m/s greasing step retained**
   (≈ 21 % of the pin-break deficit as a standing recovery, vs the 28 %
   measured immediately post-grease). No slide back toward the 4.44
   pre-grease level, and comfortably above the 4.27–4.38 damaged floor.
2. **The repair is still the main event.** 87 % of free-fall speed =
   ~76 % of the nominal drop energy (a 60 in hoist delivering a ~45 in
   drop). The acceptance bar from the greasing writeup is unchanged: a
   first block at ~5.3 m/s Δv in this configuration after the issue #92
   pin/rail repair.

## 4. One flag: the specimen-hop "constant" moved between sessions

`e_rebound` reads 0.0210 in both of these sessions vs 0.0198–0.0199 in the
08-10 greasing session and 0.019 in the blind crossover — a **+6 % shift**
in the quantity that had been transferring across sessions. Mechanically:
the hop delay lengthened (18.94 → 19.8 ms) without a matching Δv increase.
Within a session it is rock-stable (flat at p ≥ 0.12 in all three
sessions), so the suspects are the usual between-session ones — mount/
specimen re-seating, or accumulated wear on specimen 2, which is now
several hundred drops old. Consequence: **use `t_second` as an
arrival-velocity witness within a session** (its designed role); treat
cross-session hop comparisons with the same caution as cross-session `T`.
A fresh-specimen re-baseline would separate seating from specimen age
cheaply.

## 5. SOP notes coming out of this

1. **Warm-ups in steady operation: the existing 2-drop discard is enough.**
   Session 3's only transient was drop 1 (+2.7 % Δv, mat width low);
   by drop ~3 everything is on the session mean.
2. **After any rail maintenance, expect a ~40-drop settling window**
   (~3 % in Δv) before absolute levels stabilize — either burn it off or
   keep comparisons within the settled portion.
3. **Δv health gauge unchanged:** session-start Δv ≈ 4.6 m/s is the
   current (still-red) baseline; < 5.2 m/s means the tower is still eating
   energy; ~5.3 m/s is the post-repair acceptance bar.
4. **The mat is not a consumable at this scale** — no refresh logic needed
   for 100-drop campaigns on the 1/2 in PU sheet; just log a session-start
   width/raw-peak pair (both already in the metrics JSON) to catch a mat
   swap or state change.

## 6. Caveats

- One specimen, one arrangement, two sessions — the "no decay" result is
  for the settled-grease regime at 60 in; a session immediately after
  fresh maintenance will show the §1 transient instead.
- The arrival estimates inherit the healthy-session restitution
  calibration (as in the greasing analysis); the `t_second` within-session
  corroboration is the load-bearing evidence, not the third significant
  figure of the arrival column.
- Session 2's settling attribution (grease film vs mat-coupled pulse-shape
  effects on the hop) rests on the two witnesses moving together; a
  repeat after the pin repair (fresh grease, known-good rails) would
  separate them cleanly.
- `e_rebound`'s +6 % between-session shift (§4) is unexplained; until it
  is, hop-based quantities shouldn't be compared across sessions at the
  few-percent level.
