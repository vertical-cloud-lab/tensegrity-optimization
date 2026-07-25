# Minimum DAQ sample rate for the current drop-test analyses (issue #89)

Retroactive, synthetic downsampling study answering: *based on the data
collected so far, what is the minimum sampling frequency we could get away
with for the current analysis?*

## Data

The 25 TP4 captures in `prc1kn - set 1 - 1.zip` (repo root): 200 ms @
125 kHz, CH2–4 top-vertex tri-axis, CH5 plate (input + trigger), session
"prc1kn 60in - 4 felt 1 cardboard", 2026-07-21.

## Method

Each capture is re-recorded "as if" the TP4 had been set to a lower rate,
using the instrument's actual selectable ladder (User's Guide Table 2:
50 kHz, 25 kHz, 20 kHz, 10 kHz, 5 kHz, 2.5 kHz, 1.25 kHz; plus a
non-selectable 625 Hz point to show the collapse). Two simulation flavors
bracket the real acquisition chain (the TP4 specs a flat passband to
0.15·fs and a stop band at Nyquist):

- **TP4-style** — zero-phase 8th-order Butterworth low-pass at 0.15·fs
  before resampling (conservative);
- **ideal anti-alias** — polyphase resampling with a near-Nyquist FIR
  (optimistic).

At each rate, two metric families are computed per capture:

1. **As-implemented** — the exact per-capture pipeline of the campaign
   analyses (`cfc_filter`, `windowed_peak`, `ringdown_dom_freq`,
   `resultant` vendored unchanged from
   `scripts/analysis/drop_test_60in_5felts_analysis.py` @ 32b009f):
   raw peaks (saturation audit, 200 g real-impact floor, 300 g trigger),
   CFC-180 windowed peaks, T = TOP/CH5, half-max pulse width, Δv over the
   half-max window, ringdown dominant frequency.
2. **Rate-robust variants** — the same physical quantities with
   sample-granularity sensitivities removed: 3-point parabolic peak
   interpolation, Δv over a fixed −2/+6 ms window, linearly interpolated
   half-max crossings, and Welch `nperseg` scaled to keep the reference's
   30.5 Hz bin width.

The 10–100 Hz post-impact deformation quantities from
`analysis/issue-89-accel-window` (brake-catch timing, decay τ,
displacement-equivalent trace) are computed on a common 1 kHz processing
grid at every rate (the band only needs ≤100 Hz content; a fixed grid
keeps the band-pass numerically identical — `butter(4, 10–100 Hz)` is
ill-conditioned at some intermediate sample rates).

Acceptance (median |error| over the 25 drops vs the 125 kHz reference):
T ≤ 1 %, CFC-180 peaks ≤ 2 %, Δv ≤ 2 %, pulse width ≤ 5 %, ringdown
frequency ≤ 16 Hz (half a reference bin), brake timing ≤ 2 ms, and the
300 g trigger must fire on 25/25 captures.

## Results

| tier | minimum TP4 setting | limiting factor |
|---|---|---|
| current pipeline, unmodified | **25 kHz** | one-sample edge sensitivity of the half-max Δv window (≈3 %/sample) and width quantization — not information content |
| with the rate-robust tweaks | **5 kHz** | keeps the CFC-180 band (300 Hz) inside the 0.15·fs = 750 Hz flat passband |
| hard floor (any workflow) | **2.5 kHz** | 300 g trigger stops firing below this (TP4-style); CFC-180 is mathematically undefined at 1.25 kHz-and-below cutoffs relative to the band |

- The signals themselves are band-limited: 99 % of energy below ~8 kHz
  raw, and the analysis quantities live below 300 Hz (CFC-180).
- The deformation-band workflow (brake catch, τ, 10–100 Hz trace) is
  intact down to 1.25 kHz (RMSE ≤ 0.6 mm), but the trigger dies first.
- `ch5_1000_g` (CFC-1000, 1650 Hz cutoff) is the one metric that needs
  25 kHz (0.4 % error there, ~41 % at 5 kHz TP4-style).
- prc1kn's ringdown dominant mode is ~183 Hz; specimen campaigns show a
  ~549 Hz mode, which needs the ≥750 Hz flat passband of the 5 kHz
  setting — another reason not to go below 5 kHz for specimens.
- Campaign-level precision is unaffected: the CV of T across the 25
  drops is 0.46 % at 25 kHz and 0.33–0.49 % at all rates ≥ 2.5 kHz.

Free bonus: at a fixed 25,000-sample buffer, 25 kHz records **1 s** and
5 kHz records **5 s** — covering the 450 ms full-deformation window (and
at 5 kHz most of a ringdown) recommended in
`analysis/issue-89-accel-window` with no increase in file size.

## Caveats

- Single session (25 drops of the prc1kn calibration standard); specimen
  campaigns have the same pulse scale but a higher-frequency ringdown
  (see above).
- The raw-peak saturation audit is bandwidth-dependent by nature: the
  ~4,300–6,000 g contact spike attenuates to ~1,900 g at 25 kHz
  (TP4-style). Clipping physically happens at the analog front end
  regardless of rate, so headroom margins measured at a lower rate are
  not comparable to the 125 kHz ones.
- The TP4 trigger is assumed to act on the recorded samples; if it has a
  separate analog/high-rate path, the trigger floor is less restrictive
  than shown.

## Files

- `min_sample_rate.py` — reproducible analysis
  (`python min_sample_rate.py --daq-dir <extracted-zip-dir> --out figures`)
- `figures/min_sample_rate_metrics.json` — reference metrics, per-rate
  error aggregates, trigger retention, minimum-rate conclusions
- `figures/01_spectral_content.png` — where the signal energy lives
- `figures/02_pulse_vs_rate.png` — the CFC-180 pulse re-recorded at
  TP4 rates
- `figures/03_metric_errors_vs_rate.png` — 9-panel error-vs-rate sweep
- `figures/04_trigger_margin.png` — raw-peak attenuation and trigger
  retention
