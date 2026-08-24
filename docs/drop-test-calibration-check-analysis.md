# Post-reset sensitivity verification — `bpx68c` before vs after (08-17 / 08-19)

**Context.** The TP4's channel settings were cleared and re-entered by
hand on 08-18 ([settings screenshot](../data/drop-tests/calibration-check/tp4-settings-2026-08-18.jpg),
posted by @me-madsen on
[PR #86](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86)).
To verify the re-entered sensitivities, the same specimen (`bpx68c`,
low-defect small T3 prism) was re-run at the same operating point
(60 in, arrangement B = 1/2 in PU mat):
**before** = 101 drops on 08-17 under the original settings,
**after** = 30 drops on 08-19 ("calibration testing") under the
re-entered settings. Dataset:
[`data/drop-tests/calibration-check/`](../data/drop-tests/calibration-check);
script:
[`scripts/analysis/drop_test_calibration_check_analysis.py`](../../scripts/analysis/drop_test_calibration_check_analysis.py).

**Verdict: the re-entered settings are right.** Every observable that a
sensitivity error *must* move is continuous across the reset, and the
level shifts that are visible have the signature of mat/contact state,
not of channel gain.

## 1. The settings screen matches the canonical record exactly

Transcribing the screenshot against the channel map recorded since June
([`vertex-acrylic/README.md`](../data/drop-tests/vertex-acrylic/README.md),
originally from @ctrhjk's PR #67 channel-map post):

| setting | re-entered (08-18) | canonical record | |
|---|---|---|:--:|
| CH2 (tri-axis X) | 14,492.8 G / 0.690 mV/G / AC / ICP | 14,492.8 G / 0.69 mV/G / AC / ICP | ✅ |
| CH3 (tri-axis Y) | 14,992.5 G / 0.667 mV/G / AC / ICP | 14,992.5 G / 0.667 mV/G / AC / ICP | ✅ |
| CH4 (tri-axis Z) | 13,624.0 G / 0.734 mV/G / AC / ICP | 13,624.0 G / 0.734 mV/G / AC / ICP | ✅ |
| CH5 (single-axis input) | 9,442.9 G / 1.059 mV/G / AC / ICP, **trigger 150 G** | 9,442.9 G / 1.059 mV/G / AC / ICP, 150 G | ✅ |
| record | 100 ms, 1.25 MHz, 125,000 samples, 2 % = 2 ms pre-trigger | current SOP ([blind protocol](drop-test-ab-blind-protocol.md)) | ✅ |
| waveform analysis | Half Sine on CH2–CH5 | Half Sine | ✅ |

CH1/6/7/8 are inactive at the 10 mV/G default — consistent with the
retired BOT sensor staying disconnected. So the transcription is
correct; the remaining question is whether the *data* confirms the
entries took effect.

## 2. What a wrong sensitivity would look like

The TP4 reports G = volts / sensitivity, so a mis-entered channel is a
single multiplicative factor on that channel — it must scale the
filtered peak, the raw peak, the Δv integral, and the noise floor of
that channel **by the same factor**, while leaving every timing/shape
metric (pulse width, hop delay `t_second`, trigger-crossing time)
untouched. Conversely, ratios between channels (T = out/in, per-axis
share of the resultant) move only if channels are scaled *relative* to
each other. The check below exploits both directions.

## 3. Results

All 131 captures parse identically: 125,000 samples at 0.8 µs
(1.25 MHz, 100 ms), 4 channels (CH2–CH5), raw |CH5| first crosses the
150 G trigger at 2.05–2.06 ms in **both** sessions (2 ms pre-trigger +
the same ~55 µs detection latency) — capture settings verified
bit-for-bit equivalent.

Matched-state comparison (first 30 drops of 08-17, both sessions on a
rested mat, vs the 30 drops of 08-19):

| metric | before (08-17) | after (08-19) | ratio | reading |
|---|--:|--:|--:|---|
| **scale-cancelling / shape** | | | | |
| input Δv (full session) | 3.497 m/s | 3.501 m/s | **1.001** (p = 0.84) | CH5 gain unchanged |
| `e_rebound` (full session) | 0.0311 | 0.0308 | **0.990** (p = 0.16) | CH5 gain unchanged (scales as 1/k) |
| T = out/in (CFC-180) | 1.021 | 1.012 | **0.991** | top-resultant vs CH5 gain unchanged (within the known ~1.5 % session envelope) |
| hop delay `t_second` | 21.70 ms | 21.96 ms | 1.012 | same arrival velocity → sessions physically comparable |
| pulse FWHM | 2.477 ms | 2.272 ms | 0.917 | mat state changed (see §4) |
| peak × width (∝ impulse) | 493 G·ms | 500 G·ms | 1.014 | pulse reshaped, energy unchanged |
| **levels (physics + scale)** | | | | |
| CH5 input CFC-180 | 199.1 G | 220.2 G | 1.106 | |
| top resultant CFC-180 | 203.3 G | 222.8 G | 1.096 | |
| CH2 / CH3 / CH4 axis CFC-180 | 7.7 / 59.0 / 196.1 G | 8.8 / 68.5 / 213.4 G | 1.14 / 1.16 / 1.09 | |
| **pre-trigger noise floors** | | | | |
| CH2 / CH3 / CH4 / CH5 | 5.9 / 12.8 / 39.6 / 40.1 G | 2.7 / 7.3 / 22.9 / 28.2 G | **0.46 / 0.57 / 0.58 / 0.70** | *down* while peaks went *up* — impossible under a gain increase |

([continuity figure](../data/drop-tests/calibration-check/figures/01_continuity.png) ·
[per-channel ratios](../data/drop-tests/calibration-check/figures/02_channel_ratios.png))

### Candidate mis-entries, each excluded

| candidate | would produce | observed | verdict |
|---|---|---|---|
| a channel left at the 10 mV/G default | that channel ×0.07–0.10 | all channels within ±16 % | excluded outright |
| CH5 entered as 1.000 instead of 1.059 | CH5 ×1.059 on peak **and Δv and e_rebound** | Δv ×1.001, e_rebound ×0.990 | excluded to ≲1 % |
| CH4 (Z) value swapped with CH2 or CH3 | CH4 ×1.064 / ×1.100 incl. Δv-like coherence; T shifted the same | T ×0.991–0.997 | excluded to ≲1 % |
| CH2↔CH3 values swapped | CH2 ×**1.034**, CH3 ×**0.966** — opposite signs | both laterals moved *up together* relative to CH4 (+5.0 % / +6.7 %) | pattern not matched (see §5 for the honest bound) |

The strongest single fact: between 08-17 and 08-19 the CFC-180 peak rose
+10.6 % while the pulse narrowed −8.3 % and the impulse (peak × width),
Δv, `t_second` and `e_rebound` all stayed within ~1–2 %. A gain error
cannot narrow a pulse; a stiffer contact does exactly this.

## 4. What the +9–11 % level shift actually is

The after session hit harder and shorter at the same arrival energy —
the classic **rested / re-seated mat** state (2 days idle after 101
drops, likely repositioned during the settings work; the raw contact
spike grew even more, +18 %, i.e. added high-frequency content). The
same reshaping happened *within* the before session in reverse: its Δv
slid 3.96 → 3.11 m/s over 101 drops as the mat's rebound faded, exactly
the within-session mat drift documented in the
[speed-decay analysis](drop-test-speed-decay-analysis.md). And the
before session's CH5 level (197.5 G, 2.48 ms) lands right on the
08-11/12 record at this arrangement (195–201 G, 2.5–2.6 ms) — so the
pre-reset settings were also still the originals, and the verification
chain is continuous from the pre-reset era through the reset.

(`bpx68c`'s own constants differ from specimen 2's, as expected —
`e_rebound` 0.031 vs 0.021, hop 22.0 vs 19.7–19.8 ms — which is the
specimen telling us apart, not the rig.)

## 5. Bounds and caveats

- **The check pins CH5 and the resultant (≈ CH4) to ≲1 %** — an order
  of magnitude below the smallest plausible typo (3.4 %). The lateral
  axes CH2/CH3 are only bounded to ~±5–7 % because their small peaks
  (8, 68 G) are genuinely sensitive to seating/tilt and input hardness;
  the CH2↔CH3-swap candidate (±3.4 %, opposite signs) is below that
  noise floor in principle, but the observed same-sign shifts don't
  match it, and even if present it would move the campaign metric (the
  resultant, CH3 share² ≈ 0.08) by ≲0.3 %. A 5-minute definitive check
  remains available: photograph the sensors' model/serial labels and
  compare the factory calibration sheets — still the missing piece
  flagged in the calibration-record search answered on PR #86
  (08-18).
- **Noise floors are descent-vibration-dominated** (CV 17–41 % before),
  so they are used only directionally here: they fell ~30–58 % while
  peaks rose ~10 %, which no gain factor can do. (The quieter descent
  on 08-19 is itself consistent with the freshly maintained rails.)
- The before session shows two mid-session Δv steps (near drops 13 and
  31–38, mirrored in T) — within-session mat/seating state, same family
  as the drift in §4, not relevant to the calibration question.
- The screenshot's status bar shows the DB positioned on a session named
  **`ebdna8 - 60 in - 1/2" mat - 101 drops`** — a specimen ID that
  appears nowhere in the repo yet. If that's a completed campaign,
  it hasn't been uploaded.

## 6. Bottom line for the SOP

1. **Resume testing on the re-entered settings as-is** — transcription
   verified against the screenshot, capture format verified in-data,
   channel gains verified continuous to ≲1 % where it matters.
2. The screenshot is now committed as the canonical settings record
   (protocol doc §1 links it); re-take it whenever settings change.
3. Expect the **~+10 % harder input after any mat rest/re-seat** — one
   more reason ranking comparisons belong within a session, and why a
   warm-up discard stays in the SOP (the after session's input takes
   ~5–10 drops to settle onto its plateau, slightly longer than the
   usual 2-drop bedding).
