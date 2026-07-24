# How many ms of accelerometer data catch the full deformation? (issue #89)

Answers @sgbaird's follow-up on
[issue #89](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/89):
given that the quantity of interest is the deformation over the 100s of ms
after impact, how long does an accelerometer record need to be?

## Inputs

- `prc1kn - set 1 - 1.zip` (repo root): 25 TP4 captures, 200 ms @ 125 kHz,
  CH2–4 top-vertex tri-axis, CH5 base plate, session
  "prc1kn 60in - 4 felt 1 cardboard" (2026-07-21)

## Method

1. Impact = raw base-plate peak (the captures hold ~4 ms pre-trigger,
   ~196 ms post).
2. Band-pass the top-vertex tri-axis resultant to 10–100 Hz — the band that
   carries the visible deformation (see
   `analysis/issue-89-postimpact-minfps` on the
   `claude/issue-89-20260724-0512` branch) — and take a 5 ms moving-RMS
   envelope (last 8 ms of each record discarded as filter/window edge).
3. Convert the envelope to a displacement-equivalent amplitude,
   x = a / (2πf)² at the dominant f ≈ 30 Hz. This is an order-of-magnitude
   equivalence (in-band content at 100 Hz displaces 11× less than at 30 Hz),
   but it matches the video-tracked amplitudes: ±4–6 mm early snap-back,
   ~1 mm level mid-record.
4. "Full deformation captured" = residual motion below a threshold.
   Crossing times are measured directly where they occur in-record and
   extrapolated with the fitted post-brake exponential decay
   (τ ≈ 34 ms median) otherwise.

## Key results (`figures/accel_window_metrics.json`)

- Impact pulse ~3000 g peak at the top vertex; **brake catch at
  +104.2 ± 0.7 ms** (466–986 g) re-excites the structure, so the transient
  end is set by the brake event plus its decay, not by the impact.
- Residual-motion crossing times after impact (median / p95 over 25 drops):
  0.5 mm → 166 / 171 ms · 0.2 mm → 185 / 203 ms · 0.1 mm → 207 / 237 ms ·
  0.05 mm → 231 / 271 ms · 0.02 mm → 263 / 316 ms · 0.01 mm → 287 / 351 ms.
- The current 200 ms window (4 ms pre-trigger) therefore catches everything
  down to ~0.2 mm residual and truncates the final ~1–2 decay constants.
- Recommendation: **~50 ms pre-trigger + 350–400 ms post-impact
  (≈ 400–450 ms total)** contains the entire deformation transient to below
  0.01 mm residual in every drop, with margin for brake-timing drift, and
  gives double-integration workflows quiet baseline at both ends.

## Reproduce

```bash
pip install numpy scipy matplotlib
unzip "prc1kn - set 1 - 1.zip" -d /tmp/daq
python accel_window.py --daq-dir /tmp/daq --out figures
```
