
I re-analyzed all 20 attached TP4 CSVs end-to-end and produced a self-contained markdown report at `/workspace/fe044079-a179-4b74-ac72-17bfdf1042d4/edison-trajectories/input-output/input-output-report.md`, plus a per-drop metrics CSV (`per_drop_results.csv`). The report's bottom line:

A. The numbers reproduce. With my independent SAE-J211-style implementation (zero-phase Butterworth, fc = 1.65·CFC), pre-impact baseline, CH5 impact located within 10 ms then ±1.5 ms windowed peaks, I get CFC-180 means of:
- practice: input 242 ± 1.6 G, output 282 ± 3.6 G, T = 1.17 ± 0.01 (CV 0.9%)
- n0jdwk: input 241 ± 3.0 G, output 287 ± 10.0 G, T = 1.19 ± 0.05 (CV 4.6%)
- yqpmx1: input 238 ± 3.9 G, output 228 ± 1.6 G, T = 0.96 ± 0.02 (CV 2.1%)
- h8Lbev: input 233 ± 4.0 G, output 253 ± 1.3 G, T = 1.09 ± 0.02 (CV 2.0%)

These reproduce your T values exactly to two decimals; absolute G values sit ~2–3 G below yours, consistent with small filter-implementation differences. All 20/20 drops triggered cleanly at t ≈ 3.92–3.95 ms. Input pulse FWHM is 336–352 µs.

Free-fall reference from 13 in (0.330 m): v = √(2gh) = 2.545 m/s. My ±1.5 ms CFC-1000 integration of CH5 gives partial-pulse Δv = 3.44–3.65 m/s (not 2.8–3.0 m/s — please recheck your script; the value is sensitive to window length and filter choice). Either way, Δv ≥ 2.55 m/s is physically consistent with a free bungee-removed drop — the excess just reflects partial rebound (e ≈ 0.38 at Δv ≈ 3.5 m/s; e ≈ 0.14 at Δv ≈ 2.9 m/s). No bungee assist is needed to explain it.

B. T = OUT/IN is a defensible first-pass screening objective for BO under fixed drop conditions but has known weaknesses you should call out:
(i) it's a peak ratio of two scalars whose peaks may not coincide in time or frequency, so it's a shock-severity heuristic, not a true transfer function. Once you have simultaneous input+output, an FRF/SRS-band metric is more physical;
(ii) T > 1 in 3 of 4 specimens is unsurprising for a stiff vertex-to-vertex load path and rules out cushioning claims at that point — only yqpmx1 attenuates;
(iii) resultant √(CH2² + CH3² + CH4²) is robust to tri-axis rotation but doesn't fix mount rocking, mass loading, or per-axis decomposition;
(iv) for BO, use heteroscedastic noise from within-specimen replicates (T-SD ≈ 0.010–0.054 here; output-SD ≈ 1.3–10 G), and treat these as an upper bound on observation noise until you add specimen replication and order randomization.

Better BO objective hierarchy: output peak at fixed input (near-equivalent to T here, easier to interpret), then SRS-band reduction or FRF transmissibility once mounting + record length are upgraded; transmitted-impulse Δv ratio if you standardize the window; avoid SEA — you lack the instrumentation.

C. The drift is real but most likely mount-driven. Regressing T against drop number gives positive slopes for all four specimens (n0jdwk +0.033/drop, p=0.011; yqpmx1 +0.012, p=0.019; h8Lbev +0.012, p=0.080; practice +0.004, p=0.286), and a pooled demeaned T trend of +0.015/drop (p=0.0001). The mechanism — output rising while input nudges down — fits progressive seating/creep of the hot-glued vertex sensor better than monotone material softening over only 5 cycles. To separate mount artifact from physics: re-seat-and-repeat on one specimen, swap to a rigid keyed seat, interleave specimens in randomized order, precondition each mount with sacrificial drops, and log mount events. Do NOT begin 20-drop or to-failure campaigns on hot glue and then call trends fatigue.

D. Prioritized recommendations (full text in report):
1. Replace hot-glue mount with a z-aligned rigid seat (ISO 5347 mounting practice); quantify sensor mass-loading on the vertex.
2. Keep the bungees removed permanently.
3. Extend capture beyond 200 ms to cover ringdown (or add a decimated long tail).
4. Replicate at the specimen level: n ≥ 5 distinct prints per geometry, 2–3 analyzed drops each after preconditioning, randomized order.
5. Use a metric hierarchy: CFC-180 output peak / T now, FRF + SRS-band reduction later. Don't use raw peaks.
6. Anchor SOP in SAE J211 (filtering), ISO 5347 (mounting), ASTM D3332 (cushion-style framing); use D7136 only with scope caveats; reference SRS practice.
7. To regress T against geometry, also capture specimen mass, local vertex/sensor mass, strut/tendon dimensions, print orientation, pretension confirmation, low-rate stiffness, multiple drop heights, longer ringdown for damping, and a defined sensor orientation per cell.

Discretionary decisions:
- Approximated SAE J211 CFC filters as 2-pole zero-phase Butterworth via scipy filtfilt with cutoff fc = 1.65·CFC (≈297 Hz for CFC-180, ≈1650 Hz for CFC-1000); other implementations of J211 differ slightly in coefficient design and padding, which explains ~2–3 G offsets vs the attached analysis.
- Baseline correction used the mean of the pre-impact segment t < 3 ms rather than the full pre-trigger 4 ms.
- Impact location found as argmax|CH5_CFC1000| on t < 10 ms, then peaks/Δv extracted in a ±1.5 ms window (matching the attached analysis).
- Partial-pulse Δv integrated CH5_CFC1000 (not raw, not CFC-180) over the ±1.5 ms window using np.trapezoid with g = 9.80665 m/s².
- Pulse width reported as CFC-1000 full-width at half-maximum within the local window.
- Tri-axis output reported as the resultant √(CH2² + CH3² + CH4²) of baseline-corrected, CFC-filtered per-axis traces (filter-then-resultant, not resultant-then-filter).
- Within-run drift assessed by per-specimen OLS linear regression of T on drop index (1–5), and by a pooled demeaned regression across specimens; α = 0.05, no multiple-comparison correction applied across the 4 specimen regressions.
- T CV reported as 100·SD/mean over the 5 within-specimen drops (n = 5, sample SD with ddof = 1).
- Drop height converted as 13 in × 0.0254 m/in = 0.3302 m for the free-fall reference.
