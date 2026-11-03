# First Drop-Test Data — Analysis

Analysis of the first instrumented drop-tower runs recorded **Friday, May 22**
and posted by @me-madsen in
[issue #36](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4568785386).

- **Raw data:** [`data/drop-tests/raw/`](../data/drop-tests/raw/) — five TP4
  Time-Domain export files (`Signal 10–14`).
- **Script:** [`scripts/analysis/drop_test_analysis.py`](../scripts/analysis/drop_test_analysis.py)
  (regenerates every figure and the metrics table below).
- **Figures:** [`data/drop-tests/figures/`](../data/drop-tests/figures/).

> ⚠️ These are first-light results: n = 1 for the control and PETG runs, three
> nominally repeated "audrey" runs, an **undocumented channel map**, and only
> the **initial 200 ms** window. Treat the numbers as indicative and read the
> caveats in §5 before quoting them.

## 1. File format

Each file is a TP4 export: a 4-line header followed by 25,000 samples at
**8 µs / 125 kHz** over a **0.2 s** window, four columns of acceleration in G
(`CH1–CH4`).

| Run | File | Specimen |
|---|---|---|
| Signal 14 | `Signal_14_control.txt` | **control** — no specimen, both acrylic plates |
| Signal 10 | `Signal_10_PETG.txt` | PETG specimen |
| Signal 11 | `Signal_11_audrey.txt` | "audrey" specimen, run 1 |
| Signal 12 | `Signal_12_audrey.txt` | "audrey" specimen, run 2 |
| Signal 13 | `Signal_13_audrey.txt` | "audrey" specimen, run 3 |

## 2. Channel map (inferred — please confirm)

| Channel | Behavior | Interpretation |
|---|---|---|
| **CH1** | Large impact transient (raw peak 2.4–10.7 kG), peak time varies 23–49 ms | **Primary impact accelerometer** — the channel of interest |
| CH2, CH3 | Low level (±120–230 G), no clear impact feature | Cross-axis / lightly-loaded / noise |
| **CH4** | A **fixed ~1.4 kG spike at t ≈ 4.20 ms in *every* run, including the control** | **Not the impact** — a common trigger / magnet-release artifact (see Fig. 5) |

CH4 producing the same ~1.4 kG transient at the same 4.2 ms offset across all
five runs (and in the no-specimen control) means it is locked to the
acquisition trigger / hoist-release event, not to specimen contact. It should
be excluded from any g_max / SEA reduction until the wiring is confirmed — this
is exactly the "magnet-release jerk" gotcha flagged in the
[Edison drop-tower review](../edison-trajectories/drop-test/drop-test-653d7d39-b9c4-4d3f-9ae1-a1bc8fabd877.md).

**Please confirm which physical sensor is on CH1 vs CH4** (base/input plate vs
top/transmitted plate). The reduction below assumes CH1 is the meaningful
impact channel.

## 3. Raw vs filtered peak acceleration

Raw peaks on a lightly damped lattice are dominated by accelerometer-resonance
ringing — the [PSD](../data/drop-tests/figures/04_ch1_psd.png) shows significant
energy out to ~20 kHz while the structural response peaks near **550 Hz**. Per
**SAE J211** the meaningful shock number comes from a phaseless Butterworth
channel-frequency-class (CFC) low-pass. CFC 1000 (≈1650 Hz) and CFC 180
(≈300 Hz) are reported here.

| Run | raw \|g\| | CFC 1000 | CFC 180 | t_peak (ms) | pulse width (ms) |
|---|--:|--:|--:|--:|--:|
| control (no specimen) | 10,625 | 6,070 | **1,792** | 24.8 | 1.9 |
| PETG | 10,511 | 5,870 | **1,299** | 49.1 | 1.6 |
| audrey #1 | 3,594 | 941 | **370** | 38.3 | 10.8 |
| audrey #2 | 2,448 | 1,037 | **424** | 50.0 | 2.2 |
| audrey #3 | 5,092 | 1,602 | **463** | 42.3 | 4.2 |

(`pulse width` = full width at half maximum of the CFC-180 pulse.)

See [`03_peak_g_comparison.png`](../data/drop-tests/figures/03_peak_g_comparison.png)
and the per-run impact zoom
[`02_impact_zoom_filtered.png`](../data/drop-tests/figures/02_impact_zoom_filtered.png).

## 4. What the data shows

1. **The "audrey" tensegrity specimen cushions; the PETG run did not.**
   On the structural (CFC 180) number the audrey specimen brings peak
   acceleration down to **~370–463 G** vs the **~1,792 G** no-specimen control
   — roughly a **74–79 % reduction**, comparable to the 60–65 % peak-g
   reductions reported for printed tensegrity (Zhang 2018). The PETG run only
   reached ~1,299 G (~27 % below control).

2. **The PETG run looks like a near-direct plate-on-plate impact**, which is
   strong evidence of the **bungee-driven lift-off** failure mode
   ([Jeff, issue #36](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4546364370)
   and `docs/drop-test-protocol.md` §3.1): its **raw** peak (10,511 G) is within
   ~1 % of the control's (10,625 G), i.e. the top plate hit essentially as hard
   as it does with no specimen at all. The PETG specimen most likely separated
   from the base during the bungee-accelerated descent and contributed little
   cushioning at the moment of impact.

3. **Repeatability is rough.** The three audrey runs agree to ~±12 % on
   CFC-180 peak (370 / 424 / 463 G) but their raw peaks scatter 2.4–5.1 kG and
   pulse widths 2–11 ms, so a single run is not yet a reliable point estimate.
   This sets the experimental noise floor the BO loop will see and supports the
   Edison recommendation of **n ≥ 5 per condition with CV reported**.

## 5. Caveats / data-quality issues

- **Channel map unconfirmed** (§2) — all of §3–4 assumes CH1 is the impact
  channel of interest.
- **CH4 trigger artifact** (§2, Fig. 5) must be excluded or explained.
- **No Δv / SEA quoted.** A trustworthy velocity change and specific-energy-
  absorption number needs (a) the confirmed input vs transmitted channel pair,
  (b) a clean pre-impact baseline, and (c) integration over the full event —
  not the 200 ms shock-only window here. The script computes a rough Δv but it
  is sensitive to baseline and window and is **not** reported as a result.
- **200 ms window only.** The "additional ~10 s ringdown"
  ([issue #36, 12:06](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4509305026))
  is not in these exports — the multi-bounce decay and damping cannot be
  recovered from this capture.
- **n = 1** for control and PETG.

## 6. Recommended next captures

These feed back into `docs/drop-test-protocol.md` and the Edison report:

1. **Constrain the specimen to the base** (or cap its upward travel) so the
   PETG-style lift-off is eliminated, then re-run PETG — its cushioning is
   currently unmeasurable because it separated.
2. **Confirm and label the channel map** in the export (which sensor is base
   vs top), and either fix or annotate CH4.
3. **Extend the capture to ≥10 s** with pre-trigger so the ringdown is kept.
4. **n ≥ 5 per specimen**; report mean ± CV of the CFC-180 peak.
5. Apply **CFC 180 / CFC 1000** filtering as standard reduction (done here);
   report the filtered peak, not the raw ringing peak.
6. Log **drop height / release configuration** so Δv and SEA can be normalized
   across runs.
