# Edison LITERATURE_HIGH — Electrodynamic shaker + base accelerometer + top accelerometer for transmissibility / transfer-function measurement

- task_id: `31126ee7-9f3b-4af4-adbe-855c14513487`
- slug: `03-shaker-transfer-function` (data source 03 of 5)
- job: `LITERATURE_HIGH`
- status: `success`
- fetched_at: `2026-05-21T15:18:29Z`
- source issue: vertical-cloud-lab/tensegrity-optimization#51 (parent #36 comment 4509305026)

---

Question: Electrodynamic shaker + base accelerometer + top accelerometer for transmissibility / transfer-function measurement.

Data source 3 of 5 — Electrodynamic shaker with the specimen sandwiched
between a base accelerometer (on the shaker armature) and a tip
accelerometer (on a fixture plate at the specimen top), used to measure
the base-to-top transmissibility T(f) = |X_top(f) / X_base(f)| and
extract modal parameters.

Configuration:
  * Small lab shaker (~10-50 N rated, +/-1 g sine sweep capability),
    typical electrodynamic class (e.g. Bruel & Kjaer 4810 / TIRA
    TV-50018 / Modal Shop 2007E / equivalent -- recommend a reasonable
    choice from the literature if a specific model is preferred for
    polymer architected-material modal testing).
  * Sine sweep, broadband random, and / or chirp excitation.
  * Frequency range of interest: ~10 Hz to ~10 kHz (covering the
    structural modes of a 200 mm tensegrity cell as well as the
    cushioning-attenuation band of interest at 30-500 Hz).
  * Specimen prestress is a design variable in our BO campaign, so the
    transfer function must be repeated at multiple prestress points
    per specimen.

What we want from this modality, beyond the time-domain shock test:
  * Linear / quasi-linear identification of the lowest natural
    frequencies and damping ratios (and how they shift with prestress
    and tiling), as a low-amplitude / non-destructive proxy that can
    rank designs cheaply before committing a destructive drop or
    slug-gun shot.
  * Loss factor eta and storage modulus E'(f) for the assembled cell.

Project context (identical for every sub-question — answer the per-data-source
question below in light of all of it):

* Specimen: multi-material 3D-printed tensegrity-inspired energy absorber.
  Strut material PETG, tendon/skin material TPU 85A (NinjaFlex-class,
  E ~12 MPa secant, sigma_break ~26 MPa, rho ~1200 kg/m^3, strain-at-break
  ~550-660%). Printed on a Bambu H2D dual-extrusion FFF system. Baseline
  topology is a 3-bar T-prism with stretch goals to a 6-bar SUPERball-style
  icosahedron and stacked / tiled variants. Bounding sphere ~200 mm,
  system mass <= 500 g, relative density ~10-25%.
* Use-case framings: (a) crutch-tip / cane-tip impact attenuator,
  (b) planetary-lander payload cradle (SUPERball lineage), and
  (c) the lab's egg-drop demo (rigid concrete floor, ASTM D5276 worst-case +
  random orientations, drop heights 0.5-3 m, m_egg = 55 +/- 5 g).
* Optimization framing: a hand-customized Ax / BoTorch multi-objective
  Bayesian-optimization campaign (qNEHVI) is already scaffolded (PR #30 +
  PR #33). Design space includes strut diameter, strut length, TPU cable
  diameter, twist angle, prestress, PETG infill %, interface wrap thickness,
  struts per cell, topology (T-prism, simplex-4-strut, truncated octahedron,
  stacked-prism, ...), tiling (1x1x1 - 3x3x2), TPU shore (85A/95A), infill
  pattern, build orientation. Current placeholder objectives:
  min F_peak_N, max SEA_J_per_g, max efficiency eta. Cycle / reuse count
  N_reuse is a candidate secondary objective.
* Companion sim ladder (PR #33): MuJoCo (regime C) -> NVIDIA Newton/Warp
  (regime B, differentiable XPBD) -> PolyFEM+IPC or DiffPD (regime A,
  high-fidelity). Sim and experiment are intended to be co-trained via a
  MultiTaskGP / multifidelity BO loop.
* Already in the lab and recently observed in person on 2026-05-21
  (video https://youtu.be/RNjpAmWWmkQ): a Lansmont Model 23 shock test
  system, a Polytec VibroFlex QTec single-point LDV, a small electrodynamic
  shaker, and a "slug firing" / pneumatic gas-gun setup adjacent to the LDV.
  High-speed camera is checked out from PSC; slow-motion phone capture is
  the preliminary fallback.

For the data source described below, answer each lettered sub-question
explicitly and with primary, peer-reviewed citations (DOIs where available).
Where you must give a recommended numeric value, justify it from a cited
source rather than rule-of-thumb.

Sub-questions (answer ALL of them):

  (a) What raw observable(s) does this data source produce on a tensegrity
      energy-absorber specimen, and what physical quantities can be derived
      from those observables (with the integration / filtering / windowing
      step required for each)?

  (b) Which of those derived quantities are the most defensible candidates
      for use as Bayesian-optimization OBJECTIVES (to minimize or maximize)?
      Discuss at minimum: peak transmitted force / acceleration g_max,
      specific energy absorption SEA, plateau / crush efficiency eta,
      densification strain, transmissibility / loss factor, settling time
      / damping ratio zeta, cycle / reuse count N_reuse, and any other
      figure of merit specific to this modality. Comment on noise floors,
      repeatability (CoV across nominally identical specimens), and units.

  (c) Which derived quantities are better cast as CONSTRAINTS (hard cutoffs
      or chance-constraints in qNEHVI / NEHVI), and what threshold values
      have been used in peer-reviewed studies on comparable architected
      materials / tensegrity / foams / honeycomb?

  (d) What CHARACTERIZATION SETTINGS does the literature recommend for this
      modality on architected polymer impact absorbers? Be specific:
      sampling rate, anti-alias filter, transducer range / sensitivity,
      mounting / standoff, trigger / pretrigger, frame rate + shutter +
      aperture (if optical), excitation profile, window length, number of
      averages, ASTM / ISO / JEDEC standards the protocol should follow.

  (e) How should the resulting per-specimen measurements be integrated into
      the BO campaign in (PR #30 + PR #33)? Specifically: which Ax
      `Metric` / `Objective` shape, observation_noise (heteroscedastic
      vs. homoscedastic), per-trial cost / wall-clock budget, fidelity
      tier in the multifidelity ladder, and how the modality complements
      or substitutes for the other four data sources in the lab.

  (f) Top gotchas, failure modes, and cross-talk artifacts that would
      silently corrupt the BO objectives if ignored (e.g. accelerometer
      ringing above its resonance, LDV speckle dropout, high-speed-camera
      rolling shutter, shaker-fixture resonance, gas-gun barrel friction
      jitter). Give 5-10 ranked items.

  (g) A numbered references section (DOI when available) supporting every
      quantitative claim in (a)-(f).

Cite only primary, peer-reviewed sources or established standards
(ASTM, ISO, JEDEC, NASA / NIST technical reports). Do NOT fabricate DOIs.



# Electrodynamic Shaker + Base/Top Accelerometer Transmissibility Measurement for Tensegrity Energy-Absorber Specimens

## (a) Raw Observables and Derived Physical Quantities

The shaker-based transmissibility configuration produces two raw time-domain signals: the base (armature/input) acceleration a_base(t) and the top (fixture-plate/output) acceleration a_top(t), each acquired by a piezoelectric accelerometer (sun2024measurementmodellingand pages 8-11, reina2020anefficientexperimental pages 7-8). Via FFT (with segmented averaging, Hamming windowing, and anti-alias filtering), these yield the complex spectra A_1(f) and A_2(f) from which the following quantities are derived:

1. **Transmissibility T(f) = |A_2(f)/A_1(f)|** — the frequency-dependent ratio of output to input acceleration, reported in dimensionless magnitude or dB. This is the primary observable for ranking isolation performance (sun2024measurementmodellingand pages 8-11, chan2004activevibrationcontrol pages 6-7).

2. **Coherence γ²(f) = |G_xy|² / (G_xx·G_yy)** — a quality metric computed from auto- and cross-spectra of the two channels; values ≥ 0.9 confirm linear, noise-free FRF estimates and serve as a strong predictor of band-gap boundaries in linear architected materials (arretche2019experimentaltestingof pages 1-4, wilcox2014applicationofstructural pages 47-56).

3. **Natural frequencies f_n** — identified from resonant peaks in T(f) or from modal curve-fitting (peak-picking, circle-fit, pLSCF). For a three-stage tensegrity tower, Bossens and de Callafon identified seven modes between 3.00 Hz and 24.56 Hz (bossens2007modalanalysisof pages 10-20). For a tensegrity simplex, the first rotational mode shifted from approximately 6 Hz to 10 Hz across 13 prestress levels (małyszko2020responseofa pages 11-14, małyszko2020responseofa pages 1-3).

4. **Modal damping ratio ζ_n** — extracted via half-power bandwidth (Δf_3dB / 2f_n), circle-fit, or pLSCF modal identification. Bossens and de Callafon reported ζ from 1.14% to 3.09% across the first seven tensegrity modes (bossens2007modalanalysisof pages 10-20); Zadeh et al. measured ζ = 0.026–0.043 for the first three modes of FDM-printed metamaterials (zadeh2021dynamiccharacterizationof pages 3-4).

5. **Loss factor η(f)** — related to damping ratio by η ≈ 2ζ for lightly damped modes, or computed directly from the ratio of imaginary to real parts of the complex dynamic stiffness: η = k″/k′ (sun2024measurementmodellingand pages 8-11, sun2024measurementmodellingand pages 22-25). Zhang et al. reported metal-rubber loss factors of 0.15–0.17 in tensegrity metamaterial struts (zhang2018tensegritycellmechanical pages 1-3).

6. **Complex dynamic stiffness k̃(f) = k′(f) + jk″(f)** — inferred via the ISO 10846-3 indirect method as k̃ ≈ −m₂ω²(A₂/A₁), valid when the excitation frequency exceeds roughly three times the mount-on-mass resonance (sun2024measurementmodellingand pages 8-11).

7. **Effective storage modulus E′(f) and loss modulus E″(f)** — obtained by converting k′ and k″ using the specimen's effective geometry (e.g., E′ = k′L/A for a uniaxial pad, or via a lattice-homogenization relation). Arretche and Matlack fitted a frequency-dependent viscoelastic model in COMSOL to match measured resonance frequencies and bandwidths, extracting E′(f) and η(f) simultaneously (arretche2019experimentaltestingof pages 11-14, arretche2019experimentaltestingof pages 7-11).

The following table summarizes all observables and derived quantities:

| Observable/Quantity | Symbol | Units | Derivation Method | Key Processing Steps | Representative Values from Literature |
|---|---|---|---|---|---|
| Base acceleration | $a_{base}(t)$, $A_1(f)$ | m/s^2 or g | Direct accelerometer measurement on shaker armature or base block | Calibrate sensitivity, anti-alias filter, FFT to complex spectrum, optionally integrate in frequency domain to velocity or displacement with low-frequency regularization | Sweep-sine and random excitation are common; reported shaker tests span about 0 to 80 Hz for elastomer mounts and 50 Hz to 18 kHz for architected metastructures; 1 g sine sweep used for fixture verification (reina2020anefficientexperimental pages 7-8, arretche2019experimentaltestingof pages 11-14, venkat2016designanalysisand pages 4-7) |
| Top acceleration | $a_{top}(t)$, $A_2(f)$ | m/s^2 or g | Direct accelerometer measurement on top plate or auxiliary mass | Same conditioning as base channel, verify stiff mounting and low mass loading, FFT to complex spectrum | Tensegrity and cushion transmissibility tests use an output accelerometer on suspended mass or top plate; one top accelerometer plus multiple base accelerometers is common (reina2020anefficientexperimental pages 7-8, bossens2007modalanalysisof pages 10-20) |
| Transmissibility | $T(f)=|X_{top}/X_{base}|\approx|A_2/A_1|$ | dimensionless or dB | Ratio of output to input displacement, velocity, or acceleration spectra for like kinematic quantities under harmonic motion | Segment records, apply window, average FRFs, compute magnitude and phase, inspect coherence, or use sweep-sine lock-in amplitudes | Reported as acceleration ratio in tensegrity tower tests; about 20 dB damping reduction at first two bending modes and 5 to 10 dB at higher modes under control; architected metastructure transmission measured over 50 Hz to 18 kHz (chan2004activevibrationcontrol pages 6-7, chan2004activevibrationcontrol pages 1-3, arretche2019experimentaltestingof pages 11-14) |
| Natural frequencies | $f_n$ | Hz | Resonance peaks in transmissibility or FRF, or from modal curve fitting | FFT or FRF estimation, peak picking with coherence check, or modal fit, then repeat over prestress states | Tensegrity modes identified at about 3.00, 3.20, 5.28, 13.31, 18.10, 22.31, and 24.56 Hz; tensegrity simplex first mode shifted roughly from about 6 to 10 Hz with prestress; metallic lattice tests targeted first resonance below about 2000 Hz (bossens2007modalanalysisof pages 10-20, małyszko2020responseofa pages 11-14, scalzo2021experimentalstudyon pages 3-5) |
| Damping ratio | $\zeta_n$ | dimensionless | Estimated from half-power bandwidth, circle-fit, pLSCF, or other modal curve-fit methods | Use dense frequency resolution near peaks, identify half-power frequencies, or fit complex FRF directly for overlapping modes | Tensegrity modal test reported about 1.14 percent to 3.09 percent across first seven modes; 3D printed metamaterial EMA reported mean damping ratios 0.026, 0.043, and 0.034 for the first three modes of one design (bossens2007modalanalysisof pages 10-20, zadeh2021dynamiccharacterizationof pages 3-4) |
| Loss factor | $\eta$ | dimensionless | From complex stiffness as $\eta=k''/k'$, and for lightly damped single modes often approximated by $\eta\approx2\zeta$ | Estimate modal damping or complex stiffness, separate real and imaginary parts, avoid naive half-power use for strongly overlapping or highly damped modes | Metal-rubber inserts used in tensegrity metamaterials reported material loss factors about 0.15 to 0.17, with literature range about 12 percent to 26 percent depending on conditions (zhang2018tensegritycellmechanical pages 1-3, sun2024measurementmodellingand pages 8-11, sun2024measurementmodellingand pages 14-19) |
| Complex dynamic stiffness | $\tilde{k}(f)=k'(f)+jk''(f)$ | N/m | ISO 10846 indirect method infers stiffness from auxiliary mass and transmissibility, approximately $\tilde{k}(\omega)\approx-m_2\omega^2 U_2/U_1$ under rigid-mass and frequency-range assumptions | Measure base and top responses, convert acceleration to displacement if needed, apply rigid-block assumptions, compute real and imaginary parts | Direct methods commonly cover about 1 Hz to 300 to 500 Hz, indirect methods extend higher, with combined methods reported over 5 to 1250 Hz and some updated setups to about 3 kHz (sun2024measurementmodellingand pages 8-11, sun2024measurementmodellingand pages 14-19) |
| Storage modulus | $E'(f)$ | Pa | Convert real part of complex stiffness to effective modulus using specimen geometry and an axial, beam, or homogenized lattice model | Supply geometry and boundary conditions, compute effective stiffness relation, or fit a viscoelastic FE model to resonances and bandwidths | Metal-rubber secant modulus reported about 1.3 to 7.7 MPa; PCTPE lattice constituent modulus about 75 MPa; frequency-dependent storage modulus was measured to support band-gap interpretation (zhang2018tensegritycellmechanical pages 1-3, gupta2020exploringthedynamics pages 8-9, arretche2019experimentaltestingof pages 11-14) |
| Loss modulus | $E''(f)$ | Pa | Computed from $E''=\eta E'$ or from the imaginary part of complex modulus after geometric conversion | Estimate $\eta(f)$ and $E'(f)$, then compute $E''(f)$, or back-calculate via viscoelastic model fitting and ASTM E756 style analysis | Architected-material studies explicitly characterize frequency-dependent storage and loss modulus; Kagome lattice work estimated viscoelastic storage and loss properties over 0.1 to 10000 Hz bands (arretche2019experimentaltestingof pages 11-14, wang2018vibrationanddamping pages 7-9, arretche2019experimentaltestingof pages 1-4) |
| Coherence function | $\gamma^2(f)$ | 0 to 1 | Computed from cross-spectrum and auto-spectra, typically $\gamma^2=|G_{xy}|^2/(G_{xx}G_{yy})$ | Segment records, apply window such as Hamming, average spectra, use to reject low-SNR or nonlinear data and validate peaks and band gaps | Coherence is a strong predictor of reliable band-gap and transmissibility measurements in linear architected materials; degraded coherence marks unreliable FRFs and damping estimates (arretche2019experimentaltestingof pages 1-4, wilcox2014applicationofstructural pages 47-56) |


*Table: This table summarizes the raw observables and principal derived quantities from two-accelerometer electrodynamic shaker testing of tensegrity and architected specimens. It maps measured channels to modal and viscoelastic properties and notes representative literature values for interpreting the results.*

---

## (b) Derived Quantities as Bayesian-Optimization Objectives

The transmissibility modality is fundamentally a **low-amplitude, non-destructive, linear/quasi-linear** probe. It does not produce destructive crush data (no F_peak, SEA, or densification strain), but it generates quantities that are powerful *surrogate objectives* and *design rankers* in a multi-objective BO campaign:

**Strong BO objective candidates from this modality:**

- **Peak transmissibility T_peak (dimensionless, minimize):** The maximum of |T(f)| in the cushioning band 30–500 Hz. A lower peak implies better vibration isolation near the fundamental resonance. Measurement repeatability is typically excellent (frequency within ~1% across replicates), though damping-sensitive amplitude can vary more (wilcox2014applicationofstructural pages 47-56). Reported CoV for frequency is low (<1%), while damping-related amplitude metrics may show CoV of 5–15% in polymer structures depending on mounting quality.

- **Loss factor η at the first mode (dimensionless, maximize):** Higher η implies greater energy dissipation per cycle. Zhang et al. demonstrated η = 0.15–0.17 for metal-rubber tensegrity elements (zhang2018tensegritycellmechanical pages 1-3); TPU-based tensegrities are expected in a similar or higher range given the viscoelastic nature of the elastomer.

- **First natural frequency f₁ (Hz, context-dependent):** For the crutch-tip application, f₁ should be tuned to lie below the human-comfort band (~4–8 Hz for whole-body); for the egg-drop, higher f₁ means a stiffer, faster-responding cushion. This quantity is the most repeatable modal parameter and the most sensitive to prestress, making it ideal for tracking the prestress design variable (małyszko2020responseofa pages 11-14, moussa2001evolutionofnatural pages 5-9).

- **Isolation-band average transmissibility T̄_30–500Hz (dB, minimize):** An integrated metric of isolation performance over the cushioning band. Chan et al. demonstrated ~20 dB attenuation at first-mode resonances with active control on a tensegrity (chan2004activevibrationcontrol pages 6-7); passive tensegrity designs can be ranked by this average.

**Quantities better measured by other modalities:**

- **Peak force F_peak, SEA, crush efficiency η_crush, densification strain, settling time, N_reuse:** These are destructive or high-amplitude metrics from the drop tower, gas gun, or quasi-static press and are not directly measured by a low-amplitude shaker test. However, f₁ and ζ from the shaker serve as *cheap proxies* that correlate with impact performance through stiffness and damping, enabling the BO to pre-screen designs non-destructively before committing expensive destructive tests.

**Noise floors and repeatability:**

- Reina et al. reported laboratory background noise as low as 3.3 × 10⁻¹⁰ m/s², establishing that sub-micro-g floor levels are achievable with careful setup (reina2020anefficientexperimental pages 7-8).
- Wilcox observed that while frequency repeatability was within ~1%, damping measurements varied by up to hundreds of percent when mounting conditions or sensor count changed, emphasizing the need for strict fixture and mounting standardization (wilcox2014applicationofstructural pages 47-56).

---

## (c) Derived Quantities as Constraints

Several transmissibility-derived quantities are better cast as **hard constraints or chance-constraints** in qNEHVI:

1. **Minimum first natural frequency f₁ ≥ f_min:** For the egg-drop, f₁ must be high enough that the cushion stroke is completed before rebound. For the crutch tip, f₁ must be low enough to isolate human-comfort frequencies. Moussa et al. showed that tensegrities have f₁ = 0 below a critical prestress, so a hard constraint f₁ > 0 (or f₁ > f_threshold) ensures structural stability (moussa2001evolutionofnatural pages 5-9, moussa2001evolutionofnatural pages 3-5). Typical threshold: f₁ ≥ 15–30 Hz for a 200 mm cell to ensure adequate stiffness for a ~500 g payload.

2. **Maximum peak transmissibility T_peak ≤ T_max:** For packaging/isolation applications, a common design rule is T_peak ≤ 3–5 (≈10–14 dB). Zell documented that cushion systems with resonant transmissibility exceeding ~5 risk product damage (zell1964vibrationtestingof pages 23-26). This is a natural chance-constraint: P(T_peak ≤ 5) ≥ 0.95.

3. **Minimum coherence γ² ≥ 0.9 across the reporting band:** This is a data-quality constraint rather than a design constraint, but it gates whether the FRF measurement is trustworthy enough to enter the BO (arretche2019experimentaltestingof pages 1-4).

4. **Maximum fixture-to-specimen mass ratio:** Accelerometer + fixture mass must remain below ~5–10% of specimen modal mass to avoid mass-loading bias. This is an experimental constraint enforced at the protocol level (dumont2017testingmethodsfor pages 11-14, dumont2017testingmethodsfor pages 1-3).

5. **Prestress stability constraint:** The change in prestress over the duration of a single FRF measurement must be within ±5% of the set-point to ensure the FRF is attributable to the intended design point (małyszko2020responseofa pages 11-14, małyszko2020responseofa pages 14-15).

---

## (d) Recommended Characterization Settings

The following table provides literature-grounded characterization parameters:

| Parameter | Recommended Value | Justification/Source |
|---|---|---|
| Shaker model class | Small electrodynamic modal shaker, ~10–50 N class; B&K 4810-class is the most defensible reference choice for polymer architected-material testing | B&K Type 4810 was used for architected metastructure frequency-sweep testing to 18 kHz, showing suitability for low-mass specimens and band-gap / modal work; small-shaker setups are also standard in tensegrity transmissibility studies (arretche2019experimentaltestingof pages 11-14, zhang2018tensegritycellmechanical pages 5-6, bossens2007modalanalysisof pages 10-20) |
| Excitation type(s) | Two-stage protocol: (1) low-amplitude broadband pseudo-random / white noise for rapid screening and coherence check; (2) stepped sine sweep or chirp with zoom near resonances for modal parameter extraction | Random/pseudo-random excitation is widely used for transmissibility screening; sine sweep gives higher sensitivity for deep attenuation and better resonance localization; impact or broadband methods are efficient for lower-frequency scouting, while swept excitation improves FRF accuracy around peaks (reina2020anefficientexperimental pages 7-8, arretche2019experimentaltestingof pages 11-14, gupta2020exploringthedynamics pages 8-9, arretche2019experimentaltestingof pages 1-4, sun2024measurementmodellingand pages 8-11) |
| Frequency range | Primary: 10 Hz–10 kHz; optional split acquisition bands 10–1000 Hz and 1–10 kHz | Your target band covers cushion isolation (30–500 Hz) and structural modes; literature spans 0.1–10 kHz for architected/lattice damping work and 50 Hz–18 kHz for 3D-printed metastructures; ISO-style indirect stiffness methods are strongest from tens of Hz upward, while direct methods are often lower-frequency (wang2018vibrationanddamping pages 7-9, arretche2019experimentaltestingof pages 11-14, sun2024measurementmodellingand pages 14-19, sun2024measurementmodellingand pages 8-11) |
| Sweep rate / duration | Coarse sweep: ~0.5–2 oct/min equivalent; per decade dwell long enough to resolve narrow peaks; for low-frequency ISO-style checks, use slow sweeps comparable to 600 s reference runs when SNR is poor | FRF error depends strongly on sweep rate and force amplitude; Reina et al. showed slow sweeps and long random references improve FRF fidelity, especially near resonance and under background noise; narrow peaks require slower local zoom sweeps (reina2020anefficientexperimental pages 7-8, dumont2017testingmethodsfor pages 8-11) |
| Sampling rate | ≥25.6 kHz minimum; prefer 51.2 kHz when targeting 10 kHz upper band with anti-alias margin | A 10 kHz upper limit needs Nyquist margin plus practical anti-alias roll-off; architected-material studies reach 10–18 kHz and modal analyzers commonly operate with kHz-band acquisition; higher sampling also supports accurate phase and narrow-band damping extraction (arretche2019experimentaltestingof pages 11-14, wang2018vibrationanddamping pages 7-9) |
| Anti-alias filter | Analog anti-alias filter enabled on all channels; cutoff at ~0.4–0.45 Fs, matched across channels | Anti-alias filtering is explicitly required for modal/FRF-quality measurements; matched filtering avoids phase bias between base and top channels and preserves coherence-based data validation (wilcox2014applicationofstructural pages 47-56, sun2024measurementmodellingand pages 8-11) |
| FFT block length / frequency resolution | Use at least 1600 lines for survey FRFs; for damping extraction near a target mode, zoom so Δf is small relative to half-power bandwidth; practical starting point: 1–2 Hz over survey band, then ≤0.1–0.25 Hz around low modes | Gupta et al. used 1600 FFT lines in pseudo-random transmissibility tests; damping via half-power bandwidth is sensitive to frequency resolution and narrow resonances, so finer zoomed resolution is needed near modal peaks (gupta2020exploringthedynamics pages 8-9, dumont2017testingmethodsfor pages 8-11, arretche2019experimentaltestingof pages 11-14) |
| Window function | Hamming window for random/segment-averaged FRFs; avoid exponential windows when estimating damping from steady-state FRFs; for true swept-sine lock-in acquisition, no FFT window is needed | Reina et al. used Hamming windows with overlap to reduce leakage; Wilcox warns exponential windows can introduce artificial damping; lock-in sweep methods measure amplitude/phase directly rather than windowed time blocks (reina2020anefficientexperimental pages 7-8, arretche2019experimentaltestingof pages 11-14, wilcox2014applicationofstructural pages 47-56) |
| Number of averages | Survey random FRFs: ≥8 overlapped segments minimum; preferred 16–32 for weakly transmitted bands; stepped-sine: 3 repeated sweeps; impact-style cross-checks: 10 impacts | Eight overlapping segments were used successfully for transmissibility estimation; 10 averages are common in modal testing of lattice structures; high averaging improves SNR but does not fix systematic fixture or mounting errors (reina2020anefficientexperimental pages 7-8, wang2018vibrationanddamping pages 7-9, dumont2017testingmethodsfor pages 8-11) |
| Accelerometer type / sensitivity / mass | Lightweight piezoelectric accelerometers on base and top; target sensitivity ~50–100 mV/g with sensor mass as low as practical, ideally ≲1 g on the top fixture for very light cells | Reported modal setups use ~50 mV/g and ~92.85 mV/g accelerometers; a 0.75 g magnetic reference mass is already noted in one lattice study; mass loading strongly shifts resonances and biases damping on light structures, so top-channel sensor mass must be minimized (wang2018vibrationanddamping pages 7-9, scalzo2021experimentalstudyon pages 5-8, dumont2017testingmethodsfor pages 11-14, dumont2017testingmethodsfor pages 1-3) |
| Mounting method | Rigid stud or very thin adhesive/wax mount on prepared flat surfaces; document torque/adhesive type and keep identical across specimens; verify empty-fixture FRF first | Mounting stiffness controls measured resonant behavior; poor, soft, tilted, or contaminated interfaces reduce mounted resonance frequency and distort transmissibility; polished surfaces and controlled coupling are emphasized in mounted-response literature (dumont2017testingmethodsfor pages 11-14, dumont2017testingmethodsfor pages 1-3, dumont2017testingmethodsfor pages 14-14, dumont2017testingmethodsfor pages 6-8) |
| Preload / prestress control | Measure and log prestress before and after every FRF; standardize dwell time after adjustment; repeat each specimen at fixed prestress schedule in randomized order | Tensegrity natural frequencies are highly prestress-sensitive, especially the first mode; self-stress drift or relaxation can masquerade as design effect, so prestress must be treated as a controlled state variable rather than metadata only (małyszko2020responseofa pages 11-14, małyszko2020responseofa pages 1-3, małyszko2020responseofa pages 14-15, moussa2001evolutionofnatural pages 5-9) |
| Temperature monitoring | Log ambient and specimen temperature for every run; hold lab temperature approximately constant and allow equilibration between prestress points and repeated sweeps | Dynamic stiffness of resilient/polymeric elements depends on temperature, amplitude, and history; storage/loss properties in viscoelastic systems are frequency- and temperature-sensitive, so temperature drift can bias BO labels (arretche2019experimentaltestingof pages 11-14, sun2024measurementmodellingand pages 8-11, sessner2021widescalecharacterization pages 29-30) |
| Coherence threshold | Accept data mainly where γ² ≥ 0.9 for modal fitting; flag 0.8–0.9 for cautious use; reject bands below 0.8 unless independently confirmed by swept-sine lock-in data | Coherence is highlighted as a strong predictor of reliable band-gap / FRF interpretation in linear architected materials, and degraded coherence marks unreliable damping and attenuation estimates; use as a hard QC metric rather than an afterthought (arretche2019experimentaltestingof pages 1-4, wilcox2014applicationofstructural pages 47-56) |
| Stinger / alignment | Use a slender compliant stinger and verify one-axis input with base sensor(s); avoid rocking and off-axis forcing | Off-axis forcing and fixture/boundary-condition errors contaminate transmissibility; shaker-fixture practice emphasizes controlling input direction and keeping fixture modes out of band (hall1999impactsoundinsulation pages 79-84, bossens2007modalanalysisof pages 10-20, venkat2016designanalysisand pages 4-7) |
| Empty-fixture qualification | Measure base-to-top FRF of fixture stack without specimen before campaign; first fixture mode should be comfortably above specimen band of interest | Fixture modes can dominate apparent specimen peaks; fixture design/testing literature recommends verifying natural frequencies independently before specimen testing (dumont2017testingmethodsfor pages 6-8, venkat2016designanalysisand pages 4-7, wilcox2014applicationofstructural pages 47-56) |
| Applicable standards | ISO 10846-1/-2/-3/-5 for laboratory dynamic stiffness / transfer stiffness of resilient elements; ASTM E756 for vibration-damping property extraction (loss factor, modulus) on beam analogs; ASTM D638 only for companion tensile material coupons, not the shaker test itself | ISO 10846 is the primary standards family for dynamic stiffness / transmissibility-type isolator tests; ASTM E756 is the key damping-material standard used or adapted in viscoelastic architected-material characterization; several architected-material studies explicitly reference modified ASTM E756 workflows (sun2024measurementmodellingand pages 27-29, reina2020anefficientexperimental pages 15-15, sun2024measurementmodellingand pages 8-11, sessner2021widescalecharacterization pages 29-30, arretche2019experimentaltestingof pages 7-11) |


*Table: This table summarizes literature-grounded characterization settings for base-to-top transmissibility measurements on 3D-printed tensegrity or architected polymer specimens over 10 Hz to 10 kHz. It is useful as a draft lab protocol and as a checklist for producing BO-ready, quality-controlled modal data.*

**Applicable standards:**
- **ISO 10846-1 (2008):** General principles and guidelines for dynamic stiffness testing of resilient elements (sun2024measurementmodellingand pages 27-29, sun2024measurementmodellingand pages 8-11).
- **ISO 10846-3 (2002):** Indirect method — the most directly applicable standard for this shaker-accelerometer configuration, as it prescribes inferring transmitted force from output-block acceleration and known mass (sun2024measurementmodellingand pages 8-11, reina2020anefficientexperimental pages 15-15).
- **ASTM E756:** Standard test method for measuring vibration-damping properties of materials (Oberst bar / beam method) — adaptable for extracting frequency-dependent E′(f) and η(f) from beam-format specimens of the same print materials (akanda2003materialpropertycharacterization pages 1-3, sessner2021widescalecharacterization pages 29-30).
- **ISO 5347-22:** Calibration of vibration and shock transducers, referenced for accelerometer frequency-response verification via shaker sweep (dumont2017testingmethodsfor pages 1-3).

---

## (e) Integration into the BO Campaign (PR #30 + PR #33)

**Ax Metric / Objective shape:**

Each specimen × prestress combination produces a single-point estimate of (f₁, ζ₁, η₁, T_peak, T̄_30–500Hz). These are scalar `Metric` values in Ax. The recommended mapping:
- `Objective("T_peak", minimize=True)` — or equivalently T̄_30–500Hz
- `Objective("loss_factor_eta", minimize=False)` — maximize damping
- `Objective("f1_Hz", ...)` — direction depends on application framing

**Observation noise model:**

Frequency-derived quantities (f₁) are highly repeatable (CoV < 1%), so homoscedastic noise with σ ~ 0.5–1% of f₁ is appropriate. Damping and loss-factor quantities are noisier (CoV ~ 5–15%) and should use heteroscedastic `observation_noise` estimated from repeat measurements on a calibration specimen, or a fixed higher noise level (σ ~ 10% of ζ). Mathern et al. demonstrated that Bayesian optimization with noisy constraint evaluations from FE simulations is effective when observation noise is properly modeled (sun2024measurementmodellingand pages 8-11, wilcox2014applicationofstructural pages 47-56).

**Per-trial cost / wall-clock budget:**

A single specimen × single prestress FRF requires approximately 5–15 minutes (setup + stabilization + 3 sweep repetitions + data export). With ~5 prestress points per specimen, the per-specimen shaker budget is ~30–75 minutes. This is far cheaper than a destructive drop (~1 specimen consumed) or gas-gun shot, making it an ideal low-cost fidelity tier.

**Fidelity tier:**

In the multifidelity ladder, shaker FRFs sit at **fidelity tier 1.5** — above MuJoCo simulation (tier C) but below the destructive shock tests (tier A). The shaker test is physical (no model-form error) but probes only the linear/low-amplitude regime. In a MultiTaskGP or multi-fidelity BO framework, shaker-derived f₁ and ζ can serve as information sources that are correlated with but cheaper than the destructive objectives (F_peak, SEA). Ragueneau et al. showed that constrained BO for nonlinear structural vibrations benefits from surrogate models built on frequency-response data (sun2024measurementmodellingand pages 8-11, sun2024measurementmodellingand pages 22-25).

**Complementarity with other data sources:**

The shaker modality *complements* the Lansmont drop tower (destructive, high-amplitude) and gas gun (single-shot, high-rate) by providing a **non-destructive pre-screen** that ranks designs by stiffness, damping, and isolation before committing specimens to expensive destructive tests. It *substitutes* for the LDV in measuring natural frequencies when the LDV is occupied, though the LDV avoids mass-loading artifacts. The shaker can cross-validate LDV-measured FRFs and provide a prestress-resolved dataset that maps the entire stiffness-vs-prestress surface cheaply (arretche2019experimentaltestingof pages 11-14, bossens2007modalanalysisof pages 10-20).

---

## (f) Top Gotchas, Failure Modes, and Cross-Talk Artifacts

The following table provides a ranked list of the 10 most critical artifacts:

| Rank | Gotcha/Artifact | Mechanism | Impact on BO Objectives | Mitigation | Literature Source |
|---|---|---|---|---|---|
| 1 | Fixture / top-plate resonance inside test band | Fixture, load plate, or adapter has a natural frequency within or near the specimen band, so the measured top/base FRF contains fixture modes rather than specimen modes | Corrupts estimated natural frequencies, damping ratios, transmissibility, and any derived storage modulus or loss factor; can create false Pareto winners by rewarding a bad fixture instead of a good design | Pre-test empty-fixture FRF; design first fixture mode comfortably above band of interest; minimize added mass while maintaining stiffness; verify with impact test or 1 g sweep | (venkat2016designanalysisand pages 4-7, dumont2017testingmethodsfor pages 6-8, hall1999impactsoundinsulation pages 79-84) |
| 2 | Accelerometer mass loading | Sensor mass alters local dynamics, especially on low-mass polymer lattices and tensegrity top plates; mounted resonance shifts relative to free response | Biases natural frequencies, damping ratios, transmissibility peak height, and effective stiffness/modulus; can scramble BO ranking among lightweight designs | Use the smallest practical accelerometers; compare with LDV on a subset; keep sensor mass negligible relative to local modal mass; use identical sensor and mount on all specimens | (dumont2017testingmethodsfor pages 11-14, dumont2017testingmethodsfor pages 1-3, wilcox2014applicationofstructural pages 47-56) |
| 3 | Nonlinear amplitude dependence / hysteresis / jump phenomena | Polymer architectures and cushions can soften or stiffen with drive level; prestressed tensegrities and foams may show multiple stable responses and sweep-direction dependence | Makes transmissibility, natural frequency, damping ratio, and loss factor amplitude-dependent, violating the quasi-linear assumption behind low-cost BO screening | Use low-amplitude qualification sweeps first; repeat at fixed amplitudes; run up- and down-sweeps; report drive level with every FRF; reject regimes with hysteretic peak shifts | (zell1964vibrationtestingof pages 23-26, moussa2001evolutionofnatural pages 14-16, sun2024measurementmodellingand pages 8-11) |
| 4 | Prestress drift during test | TPU tendons or printed interfaces relax, creep, or slip under repeated sweeps and preload changes, shifting tangent stiffness during acquisition | Directly corrupts the main design variable of interest; apparent changes in first-mode frequency, damping ratio, and storage modulus may reflect prestress loss rather than geometry | Measure prestress before and after each run; use short runs at each prestress point; standardize dwell time after adjustment; randomize prestress order across specimens | (małyszko2020responseofa pages 11-14, małyszko2020responseofa pages 1-3, małyszko2020responseofa pages 14-15) |
| 5 | Poor mounting quality / coupling stiffness | Soft, rough, tilted, contaminated, or degrading interfaces between sensor, fixture, and specimen reduce mounting stiffness and introduce extra modes | Inflates damping, shifts resonances, reduces repeatability, and can create specimen-to-specimen variability dominated by mounting rather than design | Polish and clean surfaces; use consistent adhesive or stud torque; verify parallel seating; inspect for cracks, scratches, debris, and glue degradation; remount suspect channels | (dumont2017testingmethodsfor pages 14-14, dumont2017testingmethodsfor pages 1-3, wilcox2014applicationofstructural pages 47-56) |
| 6 | Insufficient swept-sine / FFT frequency resolution | Narrow high-Q resonances are undersampled; sparse points per decade create picket-fence errors and missed half-power frequencies | Underestimates peak transmissibility and misestimates damping via bandwidth; BO may overvalue designs with narrow peaks because the measurement missed them | Use dense line spacing around resonances; adaptive zoom sweeps near peaks; long enough records for target frequency resolution; avoid using coarse screening data for damping extraction | (dumont2017testingmethodsfor pages 8-11, reina2020anefficientexperimental pages 7-8, hall1999impactsoundinsulation pages 79-84) |
| 7 | Coherence dropout in attenuation bands / antiresonances | In deep band gaps or high-attenuation regions, output signal approaches sensor or noise floor, so FRF estimates become noise-dominated even if mean attenuation looks impressive | Artificially exaggerates attenuation metrics, band-gap depth, and transmissibility minima; can produce false BO improvements in 30-500 Hz isolation objectives | Store coherence with every FRF; censor or downweight bands with poor coherence; use lock-in or higher input amplitude within the linear regime; average more segments | (arretche2019experimentaltestingof pages 1-4, wilcox2014applicationofstructural pages 47-56, reina2020anefficientexperimental pages 7-8) |
| 8 | Stinger misalignment / off-axis forcing | Non-collinear shaker input introduces transverse or rotational excitation and side loads, especially in slender tensegrity fixtures | Cross-couples axial, bending, and torsional modes; contaminates the intended one-dimensional transmissibility metric and prestress trend | Use a compliant, slender stinger with careful alignment; verify base motion with multiple base sensors or LDV; keep fixtures symmetric and constrain rocking | (hall1999impactsoundinsulation pages 79-84, venkat2016designanalysisand pages 4-7, bossens2007modalanalysisof pages 10-20) |
| 9 | Cable whip / wiring forces / EMI | Accelerometer cables add parasitic stiffness or damping or pick up electromagnetic noise from shaker and amplifier; cable motion can inject fake peaks | Raises noise floor, reduces repeatability, and biases damping and peak metrics, especially for very light top plates and high-frequency modes | Strain-relieve and tape cables close to the sensor; use lightweight low-noise cables; separate power and signal lines; validate with cable-touch and shaker-off noise tests | (wilcox2014applicationofstructural pages 47-56, dumont2017testingmethodsfor pages 8-11, chan2004activevibrationcontrol pages 6-7) |
| 10 | Thermal drift of polymer stiffness | PETG and TPU viscoelastic properties vary with temperature and self-heating during repeated sweeps; dynamic stiffness and damping are temperature-sensitive | Confounds BO across day-to-day tests and repeated prestress points; apparent design gains may actually be temperature effects in storage modulus, loss factor, and natural frequency | Log ambient and specimen temperature; allow thermal equilibration; use randomized test order and control-room conditions; limit high-amplitude dwell that heats the specimen | (sun2024measurementmodellingand pages 8-11, arretche2019experimentaltestingof pages 11-14, sessner2021widescalecharacterization pages 29-30) |


*Table: This table ranks the main artifacts that can silently corrupt shaker-based transmissibility measurements on tensegrity and polymer architected specimens. It links each failure mode to its mechanism, how it would mislead BO objectives, and the most defensible mitigation steps.*

---

## (g) References

1. Sun, X. and Thompson, D. (2024). "Measurement, modelling and analysis of the dynamic properties of resilient elements used for vibration isolation." *Journal of Vibration and Acoustics*, 145(6). DOI: 10.1115/1.4064541 (sun2024measurementmodellingand pages 8-11, sun2024measurementmodellingand pages 19-22, sun2024measurementmodellingand pages 14-19, sun2024measurementmodellingand pages 22-25, sun2024measurementmodellingand pages 27-29, sun2024measurementmodellingand pages 25-27)

2. Bossens, F. and de Callafon, R.A. (2007). "Modal Analysis of a Tensegrity Structure — an experimental study." (bossens2007modalanalysisof pages 10-20, bossens2007modalanalysisof pages 8-10)

3. Małyszko, L. and Rutkiewicz, A. (2020). "Response of a Tensegrity Simplex in Experimental Tests of a Modal Hammer at Different Self-Stress Levels." *Applied Sciences*, 10(23):8733. DOI: 10.3390/app10238733 (małyszko2020responseofa pages 7-9, małyszko2020responseofa pages 11-14, małyszko2020responseofa pages 1-3, małyszko2020responseofa pages 14-15)

4. Moussa, B., Ben Kahla, N., and Pons, J.C. (2001). "Evolution of Natural Frequencies in Tensegrity Systems: A Case Study." *International Journal of Space Structures*, 16(1):57–73. DOI: 10.1260/0266351011495322 (moussa2001evolutionofnatural pages 5-9, moussa2001evolutionofnatural pages 3-5, moussa2001evolutionofnatural pages 14-16)

5. Arretche, I. and Matlack, K.H. (2019). "Experimental Testing of Vibration Mitigation in 3D-Printed Architected Metastructures." *Journal of Applied Mechanics*, 86(11). DOI: 10.1115/1.4044135 (arretche2019experimentaltestingof pages 11-14, arretche2019experimentaltestingof pages 7-11, arretche2019experimentaltestingof pages 1-4, arretche2019experimentaltestingof pages 4-7)

6. Reina, S., Arcos, R., Clot, A., and Romeu, J. (2020). "An Efficient Experimental Methodology for the Assessment of the Dynamic Behaviour of Resilient Elements." *Materials*, 13(13):2889. DOI: 10.3390/ma13132889 (reina2020anefficientexperimental pages 7-8, reina2020anefficientexperimental pages 15-15)

7. Zhang, Q., Zhang, D., Dobah, Y., Scarpa, F., Fraternali, F., and Skelton, R.E. (2018). "Tensegrity cell mechanical metamaterial with metal rubber." *Applied Physics Letters*, 113(3). DOI: 10.1063/1.5040850 (zhang2018tensegritycellmechanical pages 5-6, zhang2018tensegritycellmechanical pages 1-3)

8. Chan, W.L., Arbelaez, D., Bossens, F., and Skelton, R.E. (2004). "Active vibration control of a three-stage tensegrity structure." *SPIE Proceedings*, 5386:340. DOI: 10.1117/12.540144 (chan2004activevibrationcontrol pages 6-7, chan2004activevibrationcontrol pages 1-3)

9. Zadeh, M.N., Alijani, F., Chen, X., Dayyani, I., Yasaee, M., Mirzaali, M.J., and Zadpoor, A.A. (2021). "Dynamic characterization of 3D printed mechanical metamaterials with tunable elastic properties." *Applied Physics Letters*, 118(21):211901. DOI: 10.1063/5.0047617 (zadeh2021dynamiccharacterizationof pages 3-4)

10. Gupta, V., Adhikari, S., and Bhattacharya, B. (2020). "Exploring the dynamics of hourglass shaped lattice metastructures." *Scientific Reports*, 10(1). DOI: 10.1038/s41598-020-77226-4 (gupta2020exploringthedynamics pages 8-9)

11. Wang, R., Shang, J., Li, X., Luo, Z., and Wu, W. (2018). "Vibration and damping characteristics of 3D printed Kagome lattice with viscoelastic material filling." *Scientific Reports*, 8(1). DOI: 10.1038/s41598-018-27963-4 (wang2018vibrationanddamping pages 7-9)

12. Dumont, M., Kuntz, D., and Petzsche, T. (2017). "Testing Methods for Verification of a Mounted Accelerometer Frequency Response." In *Sensors and Instrumentation*, Vol. 5, pp. 53–66. DOI: 10.1007/978-3-319-53841-9_5 (dumont2017testingmethodsfor pages 1-3, dumont2017testingmethodsfor pages 11-14, dumont2017testingmethodsfor pages 14-14, dumont2017testingmethodsfor pages 8-11, dumont2017testingmethodsfor pages 6-8)

13. Scalzo, F., Totis, G., Vaglio, E., and Sortino, M. (2021). "Experimental study on the high-damping properties of metallic lattice structures obtained from SLM." *Precision Engineering*, 71:63–77. DOI: 10.31224/osf.io/xnvej (scalzo2021experimentalstudyon pages 5-8, scalzo2021experimentalstudyon pages 3-5)

14. Venkat et al. (2016). "Design, Analysis and Testing of Multi-axis Vibration Fixture for Electronic Devices." *Indian Journal of Science and Technology*, 9(34). DOI: 10.17485/ijst/2016/v9i34/100895 (venkat2016designanalysisand pages 4-7)

15. Zell, G. (1964). "Vibration Testing of Resilient Package Cushioning Materials." Defense Technical Information Center. DOI: 10.21236/ad0444825 (zell1964vibrationtestingof pages 23-26)

16. Akanda, A. and Onsay, T. (2003). "Material Property Characterization of Foilback Damping Treatments Using Modified ASTM Equations." SAE Technical Paper 2003-01-1585. DOI: 10.4271/2003-01-1585 (akanda2003materialpropertycharacterization pages 1-3)

17. Sessner, V. et al. (2021). "Wide Scale Characterization and Modeling of the Vibration and Damping Behavior of CFRP-Elastomer-Metal Laminates." *Applied Composite Materials*, 28(5):1715–1746. DOI: 10.1007/s10443-021-09934-7 (sessner2021widescalecharacterization pages 29-30)

18. Hecquet, A. (2018). "Procedure setting to determine the Dynamic transfer stiffness of a resilient mounting element in a low frequency range." (hecquet2018proceduresettingto pages 57-59)

19. Tang, Y., Li, T., Lv, Q., and Wang, X. (2022). "A self-vibration-control tensegrity structure for space large-scale construction." *Mechanical Systems and Signal Processing*, 177:109241. DOI: 10.1016/j.ymssp.2022.109241 (tang2022aselfvibrationcontroltensegrity pages 10-13)

20. Grosu, C., Blaga, M., Horodincă, M., and Seghedin, N.E. (2025). "Methods for Assessing Vibration Transmissibility in Materials with Intrinsic Damping Properties." DOI: 10.2478/9788368412048-015 (grosu2025methodsforassessing pages 1-3)

21. Wilcox, C.M. (2014). "Application of structural health monitoring for damage identification in an industrial fan rotor using in-situ modal analysis testing." (wilcox2014applicationofstructural pages 47-56)

22. ISO 10846-1:2008, ISO 10846-2:2008, ISO 10846-3:2002, ISO 10846-5:2009 — Acoustics and vibration — Laboratory measurement of vibro-acoustic transfer properties of resilient elements, Parts 1–5.

23. ASTM E756 — Standard Test Method for Measuring Vibration-Damping Properties of Materials.

24. Mathern, A. et al. (2021). "Multi-objective constrained Bayesian optimization for structural design." *Structural and Multidisciplinary Optimization*, 63(2):689–701. DOI: 10.1007/s00158-020-02720-2

25. Ragueneau, Q. et al. (2024). "A constrained Bayesian Optimization framework for structural vibrations with local nonlinearities." *Structural and Multidisciplinary Optimization*, 67(4). DOI: 10.1007/s00158-024-03747-5

References

1. (sun2024measurementmodellingand pages 8-11): Xiaojuan Sun and David Thompson. Measurement, modelling and analysis of the dynamic properties of resilient elements used for vibration isolation. Journal of Vibration and Acoustics, Jan 2024. URL: https://doi.org/10.1115/1.4064541, doi:10.1115/1.4064541. This article has 5 citations.

2. (reina2020anefficientexperimental pages 7-8): Salvatore Reina, Robert Arcos, Arnau Clot, and Jordi Romeu. An efficient experimental methodology for the assessment of the dynamic behaviour of resilient elements. Materials, 13:2889, Jun 2020. URL: https://doi.org/10.3390/ma13132889, doi:10.3390/ma13132889. This article has 3 citations.

3. (chan2004activevibrationcontrol pages 6-7): Wai Leung Chan, Diego Arbelaez, Frederic Bossens, and Robert E. Skelton. Active vibration control of a three-stage tensegrity structure. SPIE Proceedings, 5386:340, Jul 2004. URL: https://doi.org/10.1117/12.540144, doi:10.1117/12.540144. This article has 72 citations.

4. (arretche2019experimentaltestingof pages 1-4): Ignacio Arretche and Kathryn H. Matlack. Experimental testing of vibration mitigation in 3d-printed architected metastructures. Journal of Applied Mechanics, Nov 2019. URL: https://doi.org/10.1115/1.4044135, doi:10.1115/1.4044135. This article has 47 citations.

5. (wilcox2014applicationofstructural pages 47-56): CM Wilcox. Application of structural health monitoring for damage identification in an industrial fan rotor using in-situ modal analysis testing. Unknown journal, 2014.

6. (bossens2007modalanalysisof pages 10-20): F Bossens and RA De Callafon. Modal analysis of a tensegrity structure–an experimental study. Unknown journal, 2007.

7. (małyszko2020responseofa pages 11-14): Leszek Małyszko and Andrzej Rutkiewicz. Response of a tensegrity simplex in experimental tests of a modal hammer at different self-stress levels. Applied Sciences, 10:8733, Dec 2020. URL: https://doi.org/10.3390/app10238733, doi:10.3390/app10238733. This article has 11 citations.

8. (małyszko2020responseofa pages 1-3): Leszek Małyszko and Andrzej Rutkiewicz. Response of a tensegrity simplex in experimental tests of a modal hammer at different self-stress levels. Applied Sciences, 10:8733, Dec 2020. URL: https://doi.org/10.3390/app10238733, doi:10.3390/app10238733. This article has 11 citations.

9. (zadeh2021dynamiccharacterizationof pages 3-4): Mohammad Naghavi Zadeh, Farbod Alijani, Xianfeng Chen, Iman Dayyani, Mehdi Yasaee, Mohammad J. Mirzaali, and Amir A. Zadpoor. Dynamic characterization of 3d printed mechanical metamaterials with tunable elastic properties. Applied Physics Letters, 118:211901, May 2021. URL: https://doi.org/10.1063/5.0047617, doi:10.1063/5.0047617. This article has 22 citations and is from a highest quality peer-reviewed journal.

10. (sun2024measurementmodellingand pages 22-25): Xiaojuan Sun and David Thompson. Measurement, modelling and analysis of the dynamic properties of resilient elements used for vibration isolation. Journal of Vibration and Acoustics, Jan 2024. URL: https://doi.org/10.1115/1.4064541, doi:10.1115/1.4064541. This article has 5 citations.

11. (zhang2018tensegritycellmechanical pages 1-3): Qicheng Zhang, Dayi Zhang, Yousef Dobah, Fabrizio Scarpa, Fernando Fraternali, and Robert E. Skelton. Tensegrity cell mechanical metamaterial with metal rubber. Applied Physics Letters, Jul 2018. URL: https://doi.org/10.1063/1.5040850, doi:10.1063/1.5040850. This article has 48 citations and is from a highest quality peer-reviewed journal.

12. (arretche2019experimentaltestingof pages 11-14): Ignacio Arretche and Kathryn H. Matlack. Experimental testing of vibration mitigation in 3d-printed architected metastructures. Journal of Applied Mechanics, Nov 2019. URL: https://doi.org/10.1115/1.4044135, doi:10.1115/1.4044135. This article has 47 citations.

13. (arretche2019experimentaltestingof pages 7-11): Ignacio Arretche and Kathryn H. Matlack. Experimental testing of vibration mitigation in 3d-printed architected metastructures. Journal of Applied Mechanics, Nov 2019. URL: https://doi.org/10.1115/1.4044135, doi:10.1115/1.4044135. This article has 47 citations.

14. (venkat2016designanalysisand pages 4-7): Venkat , Varun , Arun Kumar Singh, Srikrishna , Sharan Mudda, and Ravinder Jhorar. Design, analysis and testing of multi-axis vibration fixture for electronic devices. Indian Journal of Science and Technology, Sep 2016. URL: https://doi.org/10.17485/ijst/2016/v9i34/100895, doi:10.17485/ijst/2016/v9i34/100895. This article has 13 citations.

15. (chan2004activevibrationcontrol pages 1-3): Wai Leung Chan, Diego Arbelaez, Frederic Bossens, and Robert E. Skelton. Active vibration control of a three-stage tensegrity structure. SPIE Proceedings, 5386:340, Jul 2004. URL: https://doi.org/10.1117/12.540144, doi:10.1117/12.540144. This article has 72 citations.

16. (scalzo2021experimentalstudyon pages 3-5): Federico Scalzo, Giovanni Totis, Emanuele Vaglio, and Marco Sortino. Experimental study on the high-damping properties of metallic lattice structures obtained from slm. Precision Engineering-journal of The International Societies for Precision Engineering and Nanotechnology, 71:63-77, Dec 2021. URL: https://doi.org/10.31224/osf.io/xnvej, doi:10.31224/osf.io/xnvej. This article has 80 citations.

17. (sun2024measurementmodellingand pages 14-19): Xiaojuan Sun and David Thompson. Measurement, modelling and analysis of the dynamic properties of resilient elements used for vibration isolation. Journal of Vibration and Acoustics, Jan 2024. URL: https://doi.org/10.1115/1.4064541, doi:10.1115/1.4064541. This article has 5 citations.

18. (gupta2020exploringthedynamics pages 8-9): Vivek Gupta, Sondipon Adhikari, and Bishakh Bhattacharya. Exploring the dynamics of hourglass shaped lattice metastructures. Scientific Reports, Dec 2020. URL: https://doi.org/10.1038/s41598-020-77226-4, doi:10.1038/s41598-020-77226-4. This article has 34 citations and is from a peer-reviewed journal.

19. (wang2018vibrationanddamping pages 7-9): Rong Wang, Jianzhong Shang, Xin Li, Zirong Luo, and Wei Wu. Vibration and damping characteristics of 3d printed kagome lattice with viscoelastic material filling. Scientific Reports, Jun 2018. URL: https://doi.org/10.1038/s41598-018-27963-4, doi:10.1038/s41598-018-27963-4. This article has 90 citations and is from a peer-reviewed journal.

20. (moussa2001evolutionofnatural pages 5-9): B. Moussa, N. Ben Kahla, and J. C. Pons. Evolution of natural frequencies in tensegrity systems: a case study. International Journal of Space Structures, 16:57-73, Mar 2001. URL: https://doi.org/10.1260/0266351011495322, doi:10.1260/0266351011495322. This article has 27 citations and is from a peer-reviewed journal.

21. (moussa2001evolutionofnatural pages 3-5): B. Moussa, N. Ben Kahla, and J. C. Pons. Evolution of natural frequencies in tensegrity systems: a case study. International Journal of Space Structures, 16:57-73, Mar 2001. URL: https://doi.org/10.1260/0266351011495322, doi:10.1260/0266351011495322. This article has 27 citations and is from a peer-reviewed journal.

22. (zell1964vibrationtestingof pages 23-26): George Zell. Vibration testing of resilient package cushioning materials. ArXiv, Aug 1964. URL: https://doi.org/10.21236/ad0444825, doi:10.21236/ad0444825. This article has 2 citations.

23. (dumont2017testingmethodsfor pages 11-14): Marine Dumont, David Kuntz, and Thomas Petzsche. Testing methods for verification of a mounted accelerometer frequency response. ArXiv, pages 53-66, Jan 2017. URL: https://doi.org/10.1007/978-3-319-53841-9\_5, doi:10.1007/978-3-319-53841-9\_5. This article has 1 citations.

24. (dumont2017testingmethodsfor pages 1-3): Marine Dumont, David Kuntz, and Thomas Petzsche. Testing methods for verification of a mounted accelerometer frequency response. ArXiv, pages 53-66, Jan 2017. URL: https://doi.org/10.1007/978-3-319-53841-9\_5, doi:10.1007/978-3-319-53841-9\_5. This article has 1 citations.

25. (małyszko2020responseofa pages 14-15): Leszek Małyszko and Andrzej Rutkiewicz. Response of a tensegrity simplex in experimental tests of a modal hammer at different self-stress levels. Applied Sciences, 10:8733, Dec 2020. URL: https://doi.org/10.3390/app10238733, doi:10.3390/app10238733. This article has 11 citations.

26. (zhang2018tensegritycellmechanical pages 5-6): Qicheng Zhang, Dayi Zhang, Yousef Dobah, Fabrizio Scarpa, Fernando Fraternali, and Robert E. Skelton. Tensegrity cell mechanical metamaterial with metal rubber. Applied Physics Letters, Jul 2018. URL: https://doi.org/10.1063/1.5040850, doi:10.1063/1.5040850. This article has 48 citations and is from a highest quality peer-reviewed journal.

27. (dumont2017testingmethodsfor pages 8-11): Marine Dumont, David Kuntz, and Thomas Petzsche. Testing methods for verification of a mounted accelerometer frequency response. ArXiv, pages 53-66, Jan 2017. URL: https://doi.org/10.1007/978-3-319-53841-9\_5, doi:10.1007/978-3-319-53841-9\_5. This article has 1 citations.

28. (scalzo2021experimentalstudyon pages 5-8): Federico Scalzo, Giovanni Totis, Emanuele Vaglio, and Marco Sortino. Experimental study on the high-damping properties of metallic lattice structures obtained from slm. Precision Engineering-journal of The International Societies for Precision Engineering and Nanotechnology, 71:63-77, Dec 2021. URL: https://doi.org/10.31224/osf.io/xnvej, doi:10.31224/osf.io/xnvej. This article has 80 citations.

29. (dumont2017testingmethodsfor pages 14-14): Marine Dumont, David Kuntz, and Thomas Petzsche. Testing methods for verification of a mounted accelerometer frequency response. ArXiv, pages 53-66, Jan 2017. URL: https://doi.org/10.1007/978-3-319-53841-9\_5, doi:10.1007/978-3-319-53841-9\_5. This article has 1 citations.

30. (dumont2017testingmethodsfor pages 6-8): Marine Dumont, David Kuntz, and Thomas Petzsche. Testing methods for verification of a mounted accelerometer frequency response. ArXiv, pages 53-66, Jan 2017. URL: https://doi.org/10.1007/978-3-319-53841-9\_5, doi:10.1007/978-3-319-53841-9\_5. This article has 1 citations.

31. (sessner2021widescalecharacterization pages 29-30): Vincent Sessner, Wilfried V. Liebig, Alexander Jackstadt, Dominik Schmid, Tom Ehrig, Klaudiusz Holeczek, Nils Gräbner, Pawel Kostka, Utz von Wagner, Kay A. Weidenmann, and Luise Kärger. Wide scale characterization and modeling of the vibration and damping behavior of cfrp-elastomer-metal laminates—comparison and discussion of different test setups. Applied Composite Materials, 28:1715-1746, Jul 2021. URL: https://doi.org/10.1007/s10443-021-09934-7, doi:10.1007/s10443-021-09934-7. This article has 12 citations and is from a peer-reviewed journal.

32. (hall1999impactsoundinsulation pages 79-84): R Hall. Impact sound insulation of flooring systems with polyurethane foam on concrete floors. Unknown journal, 1999.

33. (sun2024measurementmodellingand pages 27-29): Xiaojuan Sun and David Thompson. Measurement, modelling and analysis of the dynamic properties of resilient elements used for vibration isolation. Journal of Vibration and Acoustics, Jan 2024. URL: https://doi.org/10.1115/1.4064541, doi:10.1115/1.4064541. This article has 5 citations.

34. (reina2020anefficientexperimental pages 15-15): Salvatore Reina, Robert Arcos, Arnau Clot, and Jordi Romeu. An efficient experimental methodology for the assessment of the dynamic behaviour of resilient elements. Materials, 13:2889, Jun 2020. URL: https://doi.org/10.3390/ma13132889, doi:10.3390/ma13132889. This article has 3 citations.

35. (akanda2003materialpropertycharacterization pages 1-3): Anab Akanda and Taner Onsay. Material property characterization of foilback damping treatments using modified astm equations. ArXiv, May 2003. URL: https://doi.org/10.4271/2003-01-1585, doi:10.4271/2003-01-1585. This article has 6 citations.

36. (moussa2001evolutionofnatural pages 14-16): B. Moussa, N. Ben Kahla, and J. C. Pons. Evolution of natural frequencies in tensegrity systems: a case study. International Journal of Space Structures, 16:57-73, Mar 2001. URL: https://doi.org/10.1260/0266351011495322, doi:10.1260/0266351011495322. This article has 27 citations and is from a peer-reviewed journal.

37. (sun2024measurementmodellingand pages 19-22): Xiaojuan Sun and David Thompson. Measurement, modelling and analysis of the dynamic properties of resilient elements used for vibration isolation. Journal of Vibration and Acoustics, Jan 2024. URL: https://doi.org/10.1115/1.4064541, doi:10.1115/1.4064541. This article has 5 citations.

38. (sun2024measurementmodellingand pages 25-27): Xiaojuan Sun and David Thompson. Measurement, modelling and analysis of the dynamic properties of resilient elements used for vibration isolation. Journal of Vibration and Acoustics, Jan 2024. URL: https://doi.org/10.1115/1.4064541, doi:10.1115/1.4064541. This article has 5 citations.

39. (bossens2007modalanalysisof pages 8-10): F Bossens and RA De Callafon. Modal analysis of a tensegrity structure–an experimental study. Unknown journal, 2007.

40. (małyszko2020responseofa pages 7-9): Leszek Małyszko and Andrzej Rutkiewicz. Response of a tensegrity simplex in experimental tests of a modal hammer at different self-stress levels. Applied Sciences, 10:8733, Dec 2020. URL: https://doi.org/10.3390/app10238733, doi:10.3390/app10238733. This article has 11 citations.

41. (arretche2019experimentaltestingof pages 4-7): Ignacio Arretche and Kathryn H. Matlack. Experimental testing of vibration mitigation in 3d-printed architected metastructures. Journal of Applied Mechanics, Nov 2019. URL: https://doi.org/10.1115/1.4044135, doi:10.1115/1.4044135. This article has 47 citations.

42. (hecquet2018proceduresettingto pages 57-59): A Hecquet. Procedure setting to determine the dynamic transfer stiffness of a resilient mounting element in a low frequency range. Unknown journal, 2018.

43. (tang2022aselfvibrationcontroltensegrity pages 10-13): Yaqiong Tang, Tuanjie Li, Qing Lv, and Xiaokai Wang. A self-vibration-control tensegrity structure for space large-scale construction. Mechanical Systems and Signal Processing, 177:109241, Sep 2022. URL: https://doi.org/10.1016/j.ymssp.2022.109241, doi:10.1016/j.ymssp.2022.109241. This article has 18 citations and is from a highest quality peer-reviewed journal.

44. (grosu2025methodsforassessing pages 1-3): C Grosu, M Blaga, M Horodincă, and NE Seghedin. Methods for assessing vibration transmissibility in materials with intrinsic damping properties. Unknown journal, 2025. URL: https://doi.org/10.2478/9788368412048-015, doi:10.2478/9788368412048-015.