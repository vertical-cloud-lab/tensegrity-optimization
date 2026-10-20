# Edison LITERATURE_HIGH — Accelerometer-based shock + ringdown measurement on a Lansmont M23 drop tower

- task_id: `cfd30f3e-20e8-43b4-b055-29f9fc4f121f`
- slug: `01-accelerometer` (data source 01 of 5)
- job: `LITERATURE_HIGH`
- status: `success`
- fetched_at: `2026-05-21T15:18:29Z`
- source issue: vertical-cloud-lab/tensegrity-optimization#51 (parent #36 comment 4509305026)

---

Question: Accelerometer-based shock + ringdown measurement on a Lansmont M23 drop tower.

Data source 1 of 5 — Accelerometer-based shock + free-decay measurement on
a Lansmont Model 23 (M23) shock test system.

Configuration as discussed with Jeff in the 2026-05-21 walkthrough:
  * One accelerometer rigidly mounted to the M23 drop table / waveform-
    programmer plate.
  * A second accelerometer mounted to a custom plate that sits on top of
    the tensegrity specimen, sandwiching the specimen between the two
    plates (analogous to ASTM D1596 / D4168 / D5276 / D6537 cushion-test
    geometry).
  * Lansmont Test Partner DAQ + TouchTest Shock II controller.
  * Specimen mass ~5-30 g (PETG+TPU cells well below the 80 lb / 36 kg
    payload limit), worst-case drop height 0.61 m (24 in) per ASTM D5276
    "free fall on hard surface" baseline, ramping up to 3 m for the
    egg-drop framing.
  * Critically: we want BOTH the initial ~200 ms half-sine shock pulse
    (peak g, pulse duration, DeltaV) AND the subsequent ~10 s of free
    decay / ringdown to extract damping and the lowest specimen
    eigenfrequencies. The default Lansmont post-trigger window is too
    short for the ringdown portion -- comment on appropriate capture
    length and sample-rate settings.

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



# Accelerometer-Based Shock + Ringdown Measurement on a Lansmont M23 Drop Tower for Tensegrity Energy Absorbers

## (a) Raw Observables and Derived Physical Quantities

The Lansmont M23 shock test system generates a controlled half-sine (or haversine) acceleration pulse via a drop table impacting a waveform-programmer pad (farris2008droptestreliability pages 2-3, nelsen2017advancedandexploratory pages 8-13). In the described two-accelerometer configuration, the raw observables are:

1. **Table-reference acceleration time history, a_table(t)** — the acceleration waveform at the programmer plate, measured by the rigidly mounted reference accelerometer. This characterizes the input shock pulse.
2. **Specimen-top acceleration time history, a_specimen(t)** — the waveform at the top plate sandwiching the tensegrity specimen, capturing both the transmitted shock and the subsequent free-decay (ringdown) oscillation.

Both signals are analog voltages proportional to acceleration (in g or m/s²), digitized by the Lansmont Test Partner DAQ at the configured sampling rate.

**Derived quantities and their processing steps:**

- **Peak transmitted acceleration (g_max):** Direct extraction from the maximum of a_specimen(t) after baseline correction and low-pass filtering. For the haversine input, the peak amplitude A defines the pulse severity (nelsen2017advancedandexploratory pages 8-13).
- **Pulse duration (T):** Width of the half-sine pulse at zero crossings or half-maximum of a_table(t) (nelsen2017advancedandexploratory pages 8-13, kennedy2021controlledpyroshocktest pages 31-32).
- **Velocity change (ΔV):** Single integration of the acceleration pulse: ΔV = ∫a(t)dt over the pulse window. For a haversine, ΔV = A·T/2 (nelsen2017advancedandexploratory pages 8-13). Integration requires DC-offset removal and high-pass detrending to avoid drift, particularly for piezoelectric sensors with finite low-frequency time constant τ (walterUnknownyearselectingaccelerometersfor pages 5-7, walterUnknownyearselectingaccelerometersfor pages 7-9).
- **Displacement:** Double integration of acceleration with appropriate baseline correction.
- **Shock Response Spectrum (SRS):** Computed by driving a bank of SDOF oscillators (spanning a range of natural frequencies, typically with Q = 10) with the measured a(t) and recording each oscillator's peak response (eriksson1999measuringandanalysis pages 58-63, kucukbayram2021analysisandverification pages 144-145). The SRS can be computed for both the table input and the transmitted signal; their ratio gives a broadband transmissibility characterization.
- **Transmissibility T(f):** Frequency-domain ratio |A_specimen(f)| / |A_table(f)|, computed via FFT of synchronized channels (monkova2021mechanicalvibrationdamping pages 6-8, fayyaz2025dampingoptimizationand pages 11-13).
- **Damping ratio (ζ) and logarithmic decrement (δ):** Extracted from the ringdown portion of a_specimen(t) following the shock pulse. The free-decay envelope decays as A·exp(−ζωₙt); successive-peak logarithmic decrement δ = ln(xₖ/xₖ₊ₙ)/n yields ζ = δ/√(4π² + δ²) (mohamad2017vibrationaldampingbehaviors pages 3-6, murcinkova2019dampingpropertiesof pages 6-7, murcinkova2019dampingpropertiesof pages 1-2). Alternatively, the half-power bandwidth method in the frequency domain yields loss factor η ≈ (ω₂ − ω₁)/ωₙ ≈ 2ζ for lightly damped systems (fayyaz2025dampingoptimizationand pages 11-13).
- **Natural frequency (fₙ):** From FFT peak identification or peak-to-peak period in the ringdown (monkova2021mechanicalvibrationdamping pages 6-8, murcinkova2019dampingpropertiesof pages 1-2).
- **Settling time (tₛ):** Time from pulse onset until the filtered specimen response remains within a preset threshold band.
- **Approximate specific energy absorption (SEA):** If specimen mass m is known, the energy dissipated during the shock event can be estimated from ΔV as E ≈ m(ΔV)²/2 for the haversine case (nelsen2017advancedandexploratory pages 8-13); however, a more accurate SEA requires force-displacement integration, ideally from a companion load cell or from the quasi-static cushion-curve protocol per ASTM D1596.

The following table summarizes each derived quantity, its processing route, and its role in the BO campaign:

| Derived Quantity | Symbol/Units | Derivation from Raw Data | BO Role (Objective/Constraint/Characterization) | Notes |
|---|---|---|---|---|
| Peak transmitted acceleration | g_max, g | Peak of specimen-top accelerometer time history after baseline correction and anti-alias filtering | Objective to minimize; also safety constraint | Direct proxy for transmitted shock; sensitive to clipping, sensor resonance, and mounting compliance (nelsen2017advancedandexploratory pages 8-13, kennedy2021controlledpyroshocktest pages 31-32, walterUnknownyearselectingaccelerometersfor pages 5-7) |
| Velocity change | ΔV, m/s | Integrate acceleration over the shock pulse after detrending and baseline correction | Characterization; possible secondary objective | Verifies achieved pulse severity; integration is vulnerable to zero-shift and DC drift (nelsen2017advancedandexploratory pages 8-13, eriksson1999measuringandanalysis pages 58-63, walterUnknownyearselectingaccelerometersfor pages 5-7, walterUnknownyearselectingaccelerometersfor pages 7-9) |
| Specific energy absorption | SEA, J/g | Absorbed energy up to densification divided by specimen mass; requires force-displacement or stress-strain reconstruction | Objective to maximize | Best fused with load-cell or displacement data; typical 3D-printed polymer lattice SEA is about 2 to 6 J/g in-plane and up to 47.9 J/g out-of-plane for PEEK or CF-PEEK lattices (andrew2021energyabsorptionand pages 10-13, andrew2021energyabsorptionand pages 23-25, bustihan2025enhancingmechanicalenergy pages 14-16, bustihan2025enhancingmechanicalenergy pages 25-26) |
| Crush or plateau efficiency | η, dimensionless | Mean crush force or plateau stress divided by peak force or stress over the crush interval | Objective to maximize; may also be a constraint | Measures closeness to ideal constant-force absorption; not reliable from acceleration alone unless force is reconstructed well (bustihan2025enhancingmechanicalenergy pages 9-11, bogahawaththage2025dynamicresponseand pages 64-68) |
| Densification strain | ε_d, dimensionless | Strain or displacement at onset of steep stress or force upturn | Constraint or characterization | Definition must be fixed across the campaign; literature uses first force maximum or a stress threshold such as 10 MPa (andrew2021energyabsorptionand pages 10-13, bustihan2025enhancingmechanicalenergy pages 9-11) |
| Shock response spectrum | SRS, g vs Hz | SDOF bank driven by measured acceleration time history; record peak response versus natural frequency | Characterization; possible constraint | More informative than g_max when pulse shapes differ; compare table and transmitted spectra (kucukbayram2021analysisandverification pages 144-145, eriksson1999measuringandanalysis pages 58-63, kennedy2021controlledpyroshocktest pages 31-32) |
| Transmissibility | T, dimensionless | Frequency-domain ratio of specimen-top to table acceleration amplitude | Objective to minimize in protected band; characterization elsewhere | Requires dual accelerometers and synchronization; useful for lowest modes and isolation behavior (monkova2021mechanicalvibrationdamping pages 6-8, fayyaz2025dampingoptimizationand pages 11-13) |
| Damping ratio | ζ, dimensionless | From ringdown using logarithmic decrement or half-power bandwidth near resonance | Objective to maximize for fast settling; also characterization | One of the most valuable outputs of the long ringdown capture window (fayyaz2025dampingoptimizationand pages 11-13, mohamad2017vibrationaldampingbehaviors pages 3-6, murcinkova2019dampingpropertiesof pages 6-7, murcinkova2019dampingpropertiesof pages 1-2) |
| Logarithmic decrement | δ, dimensionless | Compute from successive ringdown peaks using the decay envelope over n cycles | Characterization; can be transformed into damping objective | Time-domain damping metric often easier to estimate robustly than ζ in noisy data (murcinkova2019dampingpropertiesof pages 6-7, murcinkova2019dampingpropertiesof pages 1-2) |
| Settling time | t_s, s | Time from pulse onset until filtered specimen response remains within a preset band | Objective to minimize; also operational constraint | Threshold must be frozen before BO; useful for rebound suppression framing (mohamad2017vibrationaldampingbehaviors pages 3-6, murcinkova2019dampingpropertiesof pages 6-7) |
| Natural frequency | f_n, Hz | FFT of ringdown, autocorrelation, or peak-to-peak period of filtered free decay | Characterization; possible constraint | Lowest mode is a key sim-to-test calibration target and aids transmissibility interpretation (monkova2021mechanicalvibrationdamping pages 6-8, mohamad2017vibrationaldampingbehaviors pages 3-6, murcinkova2019dampingpropertiesof pages 1-2) |
| Loss factor | tanδ, dimensionless | From half-power bandwidth or approximately 2ζ for lightly damped linear response | Characterization; possible objective to maximize | Useful bridge to viscoelastic and vibration-control literature (fayyaz2025dampingoptimizationand pages 11-13, murcinkova2019dampingpropertiesof pages 1-2) |
| Peak force | F_peak, N | Approximate from effective moving mass times acceleration only if fixture and impacting mass are well characterized; otherwise use force transducer in companion modality | Primary objective to minimize; hard constraint | Important BO target, but accelerometer-only force estimates are model-based and can be biased by fixture compliance (nelsen2017advancedandexploratory pages 8-13, xu2016crashperformanceand pages 9-12) |
| Reuse count | N_reuse, integer | Number of drops or compressions until failure criterion is exceeded | Objective to maximize or constraint | Failure criterion can be g_max threshold, permanent set, crack, SEA drop, or damping or frequency drift (bustihan2025enhancingmechanicalenergy pages 14-16, bustihan2025enhancingmechanicalenergy pages 25-26) |
| Energy absorption efficiency | η_abs, dimensionless | Absorbed energy divided by ideal rectangular energy up to densification | Objective to maximize | Useful for ranking architectures that spread load uniformly through the stroke (bustihan2025enhancingmechanicalenergy pages 9-11, bogahawaththage2025dynamicresponseand pages 64-68) |


*Table: This table maps each quantity derivable from dual-accelerometer shock and free-decay data to its signal-processing route and its defensible role in Bayesian optimization. It helps separate true BO objectives from constraint metrics and calibration-only characterization outputs.*

## (b) Defensible Bayesian-Optimization Objectives

The most defensible BO objectives extractable from this dual-accelerometer modality are:

1. **Peak transmitted acceleration g_max (minimize).** This is the single most important output of a cushion-test or shock-protection evaluation. It maps directly to injury criteria (e.g., egg-drop survival) and packaging fragility thresholds (nelsen2017advancedandexploratory pages 8-13, kennedy2021controlledpyroshocktest pages 31-32). Noise floors depend on accelerometer type and range; a 500 g range piezoresistive sensor at 100 kS/s will typically resolve ≲0.5 g noise floor. Repeatability (CoV) for 3D-printed polymer lattices under quasi-static compression is generally <5% when printing quality is controlled (bustihan2025enhancingmechanicalenergy pages 11-14), though dynamic CoV may be larger (5–15%) owing to rate-sensitivity and orientation variability.

2. **Damping ratio ζ (maximize) or equivalently settling time tₛ (minimize).** Extracted from the 10 s ringdown window, this is a unique and high-value output of the extended capture. Higher ζ means faster energy dissipation and smaller post-impact oscillations. Units are dimensionless; typical values for polymer lattice structures fall in the range 0.01–0.15, with TPU-based structures at the high end (monkova2021mechanicalvibrationdamping pages 6-8, fayyaz2025dampingoptimizationand pages 11-13, murcinkova2019dampingpropertiesof pages 6-7).

3. **Specific energy absorption SEA (maximize, J/g).** While best measured with a force transducer, an accelerometer-only estimate via ΔV provides a useful proxy. Literature values for FDM polymer lattices range from ~1–6 J/g in-plane (andrew2021energyabsorptionand pages 10-13, bustihan2025enhancingmechanicalenergy pages 14-16, bustihan2025enhancingmechanicalenergy pages 25-26) and up to 47.9 J/g out-of-plane for CF/PEEK hexagonal lattices (andrew2021energyabsorptionand pages 23-25). For TPU-class materials, SEA of 1–3 J/g is a reasonable expectation.

4. **Crush/plateau efficiency η (maximize, dimensionless).** Defined as η = F_mean/F_peak (or equivalently E_abs/(F_peak · d)), this measures how uniformly the structure absorbs energy across its stroke (bustihan2025enhancingmechanicalenergy pages 9-11, bogahawaththage2025dynamicresponseand pages 64-68). Values of 40–60% are typical for good FDM lattice absorbers (bustihan2025enhancingmechanicalenergy pages 14-16).

5. **Reuse count N_reuse (maximize, integer).** Defined as the number of successive drops before a failure criterion (e.g., g_max exceeds threshold, permanent set exceeds a limit, or SEA degrades by a specified fraction). TPU structures can show up to 99.5% geometric recovery after compression, suggesting good reusability (bustihan2025enhancingmechanicalenergy pages 14-16).

Other metrics—transmissibility, natural frequency, densification strain, SRS—are valuable for characterization but are more naturally treated as constraints or calibration targets rather than direct BO objectives.

## (c) Quantities Best Cast as Constraints

The following are better expressed as hard cutoffs or chance-constraints in a qNEHVI/NEHVI formulation:

- **g_max ≤ threshold.** For the egg-drop demo, survival requires g_max below the egg's fragility limit (~50–80 g for a chicken egg at 55 g). For packaging applications, ASTM D5276 implies a fragility-based G-level ceiling. In JEDEC JESD22-B111 board-level testing, 1500 g at 0.5 ms is the standard severity (farris2008droptestreliability pages 2-3, kang2017astudyon pages 1-3, karppinen2012shockimpactreliability pages 6-7); for the tensegrity egg-drop, a constraint of g_max ≤ 60 g is a defensible starting point.
- **Densification strain ε_d ≥ threshold.** The structure must not bottom out within the available stroke. A minimum ε_d of 0.3–0.5 (relative to initial height) is typical for effective foam/lattice absorbers. Literature defines densification using either the energy-efficiency peak method or a stress threshold (e.g., 10 MPa for PEEK lattices) (andrew2021energyabsorptionand pages 10-13, bustihan2025enhancingmechanicalenergy pages 9-11).
- **Specimen integrity / N_reuse ≥ N_min.** A hard constraint that the specimen survives at least N drops without catastrophic failure. For the multi-use crutch-tip framing, N_reuse ≥ 1000 might be targeted; for the egg-drop demo, N_reuse ≥ 3 (for repeated demonstration) is a practical floor.
- **Specimen mass ≤ 500 g** and **bounding sphere ≤ 200 mm:** geometric packaging constraints from the project specification.
- **Peak force F_peak ≤ F_fragility** where F_fragility is defined by the protected payload (egg mass × g_max limit).
- **Crush efficiency η ≥ 0.3.** Multi-objective crashworthiness studies typically constrain η or CFE (crush force efficiency) to a minimum to avoid structures that have a sharp initial peak followed by negligible plateau (xu2016crashperformanceand pages 9-12).

## (d) Recommended Characterization Settings

The following table provides specific DAQ and instrumentation recommendations:

| Parameter | Recommended Value | Justification/Source |
|---|---:|---|
| Sampling rate (shock window) | **≥ 100 kS/s per channel** | Shock DAQ guidance recommends sampling at **>10× maximum analysis frequency (MAF)**; for a short half-sine shock with meaningful kHz content, a 100 kS/s class setting is a defensible minimum and aligns with the more general recommendation to sample about **10× the highest frequency of interest** when time-history fidelity matters. (yan2020structuralresponseunder pages 36-38, walterUnknownyearselectingaccelerometersfor pages 1-3) |
| Sampling rate (ringdown window) | **2–5 kS/s per channel** | Ringdown on these specimens is expected to be dominated by low modes (order 10–200 Hz). Sampling still must exceed **2× highest frequency**, and ~10× highest frequency is preferred for waveform fidelity; 2–5 kS/s comfortably resolves low-order modal decay while reducing file size for 10 s captures. (walterUnknownyearselectingaccelerometersfor pages 1-3, monkova2021mechanicalvibrationdamping pages 6-8) |
| Anti-alias filter cutoff | **One octave below Nyquist** | Recommended shock/pyroshock DAQ practice is to place the analog anti-alias filter cutoff **one octave below the Nyquist frequency, or lower**. (yan2020structuralresponseunder pages 36-38) |
| Anti-alias filter roll-off | **> 60 dB/octave** | Recommended analog anti-alias filter roll-off for shock DAQ is **steeper than 60 dB/octave**. (yan2020structuralresponseunder pages 36-38) |
| Accelerometer type (table reference) | **Piezoresistive, DC-coupled reference accelerometer preferred** | Piezoresistive accelerometers have response down to **0 Hz**, making them preferable when integrating to velocity and when concern exists about baseline/droop. Piezoelectric sensors can suffer low-frequency droop and zero-shift under severe shock. (walterUnknownyearselectingaccelerometersfor pages 5-7, walterUnknownyearselectingaccelerometersfor pages 3-5, walterUnknownyearselectingaccelerometersfor pages 1-3) |
| Accelerometer type (specimen response) | **Piezoresistive, low-mass DC-coupled accelerometer preferred** | For the specimen-top plate, the need to observe both the initial shock and the subsequent free decay favors **DC response** and minimal low-frequency distortion; low sensor mass is also important to limit mass loading of the light specimen. (walterUnknownyearselectingaccelerometersfor pages 5-7, walterUnknownyearselectingaccelerometersfor pages 3-5, eriksson1999measuringandanalysis pages 12-18) |
| Accelerometer range | **At least ±500 g; preferably ±1000 g if higher-height testing is planned** | The exact range must exceed expected peak table/specimen acceleration without clipping. Comparable Lansmont/JEDEC half-sine tests commonly use **1500 g, 0.5 ms** environments, so using a several-hundred-g to 1000-g-class sensor is prudent for drop-shock work as the program escalates. (farris2008droptestreliability pages 2-3, kang2017astudyon pages 1-3, karppinen2012shockimpactreliability pages 6-7) |
| Accelerometer resonant frequency requirement | **Choose sensor so pulse duration ratio satisfies T/Tn > 5; preferably ~10; equivalently avoid use above ~1/5 of sensor resonance** | Walter’s shock-measurement guidance gives **T/Tn > 5** for <~10% peak error and **T/Tn ≈ 10** for near-perfect reproduction; also, do not use an accelerometer above **1/5 of its resonant frequency**. For a ~200 ms pulse this criterion is easy to satisfy, but it still governs selection and mounting. (walterUnknownyearselectingaccelerometersfor pages 5-7, walterUnknownyearselectingaccelerometersfor pages 3-5) |
| Mounting method | **Rigid stud/screw mounting to flat, stiff plates; avoid adhesive wax/tape for quantitative shock work** | Shock literature emphasizes proper mechanical mounting on flat surfaces and minimizing mass loading; poor mounting corrupts high-frequency response and SRS. (eriksson1999measuringandanalysis pages 12-18, walterUnknownyearselectingaccelerometersfor pages 3-5) |
| Pretrigger length | **10–20 ms** | No source in the retrieved set gives a universal numeric pretrigger requirement; a short pretrigger is recommended here to establish baseline and catch any trigger jitter while remaining negligible relative to a 10 s record. This is a project recommendation consistent with the need to baseline-correct acceleration before integration. (walterUnknownyearselectingaccelerometersfor pages 1-3, walterUnknownyearselectingaccelerometersfor pages 5-7) |
| Shock capture window | **0.3–0.5 s** | This comfortably contains the full initial pulse and immediate post-impact transients while preserving enough baseline around the event for QC and integration. The system is intended to capture a nominal ~200 ms pulse plus short post-impact ringing. (nelsen2017advancedandexploratory pages 8-13, kennedy2021controlledpyroshocktest pages 31-32) |
| Ringdown capture window | **10 s** | Free-decay/modal studies extract damping and natural frequency from many cycles; a 10 s window is appropriate for low-frequency, lightly damped polymer-lattice response and is much longer than default short shock windows. (mohamad2017vibrationaldampingbehaviors pages 3-6, murcinkova2019dampingpropertiesof pages 6-7, murcinkova2019dampingpropertiesof pages 1-2) |
| Total capture length | **10.3–10.5 s** | Total record should include pretrigger + shock window + full ringdown. This is the practical implication of combining the above settings in one acquisition. (mohamad2017vibrationaldampingbehaviors pages 3-6, murcinkova2019dampingpropertiesof pages 6-7, walterUnknownyearselectingaccelerometersfor pages 1-3) |
| Trigger level | **Table/reference accelerometer threshold set above noise floor, e.g. 5–10 g rising-edge** | Retrieved sources stress adequate SNR and proper triggering but do not prescribe a universal numeric level. A modest rising-edge threshold above baseline noise is appropriate so the record starts on impact rather than on pre-impact vibration. (walterUnknownyearselectingaccelerometersfor pages 1-3) |
| Relevant standards | **ASTM D5276; ASTM D1596; ASTM D4168; JEDEC JESD22-B111; IEST RP-DTE011.1** | D5276 governs free-fall drop testing; D1596 and D4168 cover dynamic cushioning/distribution environments; JESD22-B111 provides a well-established half-sine drop-shock reference environment; Walter explicitly points to **IEST RP-DTE011.1** for shock transducer selection guidance. (farris2008droptestreliability pages 2-3, kang2017astudyon pages 1-3, walterUnknownyearselectingaccelerometersfor pages 3-5) |


*Table: This table summarizes recommended DAQ and accelerometer settings for capturing both the initial shock pulse and the long ringdown on a Lansmont M23. It is useful as a test-setup checklist and ties each recommendation to the retrieved evidence base.*

**Key justifications:**

- **Sampling rate:** Shock DAQ specifications recommend sampling at >10× the maximum analysis frequency (MAF) (yan2020structuralresponseunder pages 36-38, walterUnknownyearselectingaccelerometersfor pages 1-3). For the shock window with meaningful content up to ~10 kHz, this yields ≥100 kS/s. For the ringdown window (modes below ~500 Hz), 2–5 kS/s suffices. A practical approach on the Lansmont Test Partner DAQ is to acquire the entire 10+ second record at 50–100 kS/s if storage permits, or to implement a dual-rate scheme if the DAQ supports it.
- **Anti-alias filter:** Set the analog anti-alias cutoff one octave below the Nyquist frequency, with roll-off >60 dB/octave (yan2020structuralresponseunder pages 36-38).
- **Accelerometer selection:** Piezoresistive (DC-coupled) sensors are strongly preferred for this application because they provide response to 0 Hz, enabling clean integration to velocity and faithful capture of the slow ringdown without droop artifacts (walterUnknownyearselectingaccelerometersfor pages 5-7, walterUnknownyearselectingaccelerometersfor pages 3-5, walterUnknownyearselectingaccelerometersfor pages 1-3). The accelerometer natural frequency should satisfy T/Tₙ > 5 (walterUnknownyearselectingaccelerometersfor pages 5-7); for a ~200 ms cushion pulse, this means fₙ > 25 Hz, which is trivially satisfied by any shock-class sensor but becomes important for accurate capture of very short secondary impacts.
- **Capture length:** The default Lansmont post-trigger window is typically a few hundred milliseconds—sufficient for the shock pulse but far too short for ringdown. A total capture of ~10.3–10.5 s (10 ms pretrigger + 0.3 s shock window + 10 s ringdown) is recommended (mohamad2017vibrationaldampingbehaviors pages 3-6, murcinkova2019dampingpropertiesof pages 6-7). This may require exporting the trigger signal from the Lansmont controller to an external DAQ (e.g., National Instruments PXIe-4480/4481 (kucukbayram2021analysisandverification pages 144-145)) that can record the extended window, or configuring the Test Partner for a custom long-record acquisition.
- **Standards:** The test protocol should reference ASTM D5276 (free-fall drop testing), ASTM D1596/D4168 (dynamic cushion curves), and IEST RP-DTE011.1 (shock transducer selection) (walterUnknownyearselectingaccelerometersfor pages 3-5, farris2008droptestreliability pages 2-3). For the egg-drop framing, ASTM D5276's worst-case flat-drop orientation on a rigid surface at specified heights provides the baseline severity.

## (e) Integration into the BO Campaign (PR #30 + PR #33)

**Ax Metric/Objective shape:** In the Ax/BoTorch framework, each specimen drop produces a vector of scalar outcomes. The primary objectives for the qNEHVI acquisition function are: minimize g_max, maximize SEA (or its ΔV-based proxy), and maximize ζ (or minimize tₛ). These map to three `Metric` objects in Ax, with the first negated for minimization. Crush efficiency η and N_reuse are candidate secondary objectives or can be promoted to the Pareto set if the dimensionality budget allows; qNEHVI handles 2–4 objectives efficiently (mamun2025accelerateddevelopmentof pages 12-15, mamun2025accelerateddevelopmentof pages 15-19, mamun2025accelerateddevelopmentof pages 4-8).

**Observation noise model:** Given the inherent variability of FDM specimens (printing defects, orientation sensitivity), qNEHVI (the noisy variant of qEHVI) is the appropriate acquisition function (mamun2025accelerateddevelopmentof pages 12-15, mamun2025accelerateddevelopmentof pages 15-19). Heteroscedastic noise modeling is preferred because: (a) g_max has relatively low noise at a fixed drop height but increases at higher heights due to rate sensitivity; (b) SEA and ζ depend on specimen quality and show higher CoV (~5–15%). In Ax, this can be implemented by passing per-observation standard errors or by fitting a heteroscedastic GP. The noisy variant qNEHVI properly integrates over posterior uncertainty rather than just using the posterior mean (mamun2025accelerateddevelopmentof pages 12-15).

**Per-trial cost and wall-clock budget:** Each Lansmont drop takes ~2–5 minutes including setup, data collection (10.5 s), and specimen repositioning. Data post-processing is ~1 minute per drop with automated scripts. A realistic throughput is 10–15 drops per hour. With 5–10 design parameters, an initial space-filling batch of ~20–30 specimens (Latin hypercube) followed by 30–50 BO-guided iterations is a practical budget, totaling 50–80 drops over 1–2 lab sessions.

**Fidelity tier:** In the multifidelity simulation ladder, the Lansmont accelerometer data occupy the highest-fidelity experimental tier (Tier 0). MuJoCo (Regime C) predictions of g_max and ζ form the lowest-cost surrogate; NVIDIA Newton/Warp (Regime B) provides intermediate fidelity; and PolyFEM+IPC (Regime A) approaches experimental accuracy. A MultiTaskGP or multi-fidelity knowledge-gradient acquisition function can fuse these tiers, using the Lansmont data to calibrate and anchor the simulation ladder (mamun2025accelerateddevelopmentof pages 15-19, mamun2025accelerateddevelopmentof pages 4-8).

**Complementarity with other modalities:** The Lansmont shock data provide the definitive impact-protection metric (g_max) that the LDV (which gives velocity/displacement at a single point) and shaker (which provides steady-state transmissibility) cannot directly replicate at realistic impact severities. The high-speed camera provides qualitative deformation mode validation but not quantitative acceleration. The gas-gun setup enables higher-velocity impacts beyond the M23's 3 m drop height. Together, the five modalities cover quasi-static (shaker/LDV), moderate-rate (Lansmont), and high-rate (gas gun) regimes, with the Lansmont data serving as the primary BO objective source for the egg-drop and crutch-tip framings.

## (f) Top Gotchas, Failure Modes, and Cross-Talk Artifacts

Ranked by likelihood and severity for this specific test configuration:

1. **Piezoelectric accelerometer zero-shift under shock.** If IEPE/ICP sensors are used instead of piezoresistive ones, resonance excitation of the ceramic element can produce a DC zero-shift that corrupts the baseline and makes velocity integration unreliable (walterUnknownyearselectingaccelerometersfor pages 5-7, walterUnknownyearselectingaccelerometersfor pages 7-9). *Mitigation:* Use piezoresistive (DC-coupled) accelerometers; if IEPE must be used, apply mechanical isolation filters and post-process with zero-shift correction algorithms.

2. **Insufficient ringdown capture window.** The default Lansmont Test Partner post-trigger record is optimized for the short shock pulse (~50–200 ms) and will truncate the free-decay data needed for damping extraction (mohamad2017vibrationaldampingbehaviors pages 3-6, murcinkova2019dampingpropertiesof pages 6-7). *Mitigation:* Configure a custom long record (≥10 s) or route the trigger to an external DAQ with extended capture capability.

3. **Accelerometer resonance ringing.** If significant energy exists near the accelerometer's resonant frequency (typically 20–100 kHz for shock-class sensors), the sensor will amplify that content by up to 1000:1 for undamped MEMS devices, producing spurious high-frequency oscillations superimposed on the true response (walterUnknownyearselectingaccelerometersfor pages 5-7, walterUnknownyearselectingaccelerometersfor pages 3-5). *Mitigation:* Obey the 1/5 fₙ rule—do not use accelerometer data above 1/5 of the sensor's resonant frequency; apply digital low-pass filtering post-acquisition.

4. **Mass loading of the lightweight specimen.** The tensegrity specimens weigh only 5–30 g; a 10 g accelerometer on the top plate adds significant parasitic mass (33–200% of specimen mass), altering the dynamic response and biasing g_max and ζ downward (eriksson1999measuringandanalysis pages 12-18). *Mitigation:* Use the lightest available accelerometer (e.g., ≤2 g); account for sensor+plate mass in all derived calculations; validate with LDV as a non-contact cross-check.

5. **Low-frequency droop in IEPE circuits.** The RC time constant of IEPE conditioning (typically τ = 0.5–10 s) causes baseline droop and long return-to-zero oscillations over hundreds of milliseconds, which directly corrupt the ringdown portion (walterUnknownyearselectingaccelerometersfor pages 7-9). *Mitigation:* Select piezoresistive sensors or choose IEPE sensors with τ ≫ 10 s; verify τ/T > 10 for the longest expected excursion (walterUnknownyearselectingaccelerometersfor pages 5-7).

6. **Anti-alias filter inadequacy or absence.** Without proper analog anti-aliasing (cutoff one octave below Nyquist, >60 dB/octave), high-frequency noise and accelerometer resonance content fold into the measurement band and corrupt both the shock pulse and the ringdown (yan2020structuralresponseunder pages 36-38). *Mitigation:* Verify the DAQ's analog filter specifications before testing; never rely solely on digital post-filtering.

7. **Specimen orientation and contact variability.** ASTM D5276 calls for worst-case flat-face and edge/corner orientations. Tensegrity structures have no flat face—contact geometry changes with orientation, producing high CoV in g_max. *Mitigation:* Define and fixture a repeatable orientation for BO; add random-orientation drops as a separate robustness evaluation.

8. **Cable capacitance and connector artifacts.** Long cables between the accelerometer and signal conditioner increase capacitance, reducing the high-frequency bandwidth of IEPE circuits and potentially introducing connector-impact transients (walterUnknownyearselectingaccelerometersfor pages 7-9). *Mitigation:* Use short, low-capacitance cables; secure cables to prevent whip-induced signals; use inline charge converters near the sensor if cable runs are unavoidable.

9. **Integration drift during ΔV computation.** Even small DC offsets or low-frequency noise accumulate during numerical integration, producing fictitious velocity and displacement trends (walterUnknownyearselectingaccelerometersfor pages 5-7, nelsen2017advancedandexploratory pages 8-13). *Mitigation:* Apply high-pass baseline correction (e.g., piecewise polynomial detrending) before integration; cross-validate ΔV with the known free-fall velocity v = √(2gh) from the programmed drop height.

10. **Specimen damage between drops corrupting N_reuse assessment.** TPU-based structures can recover up to 99.5% of their geometry (bustihan2025enhancingmechanicalenergy pages 14-16), but micro-damage accumulates invisibly. If specimens are reused without inspection, gradual degradation silently shifts g_max and ζ across the BO campaign. *Mitigation:* Photograph and weigh each specimen before and after every drop; define explicit go/no-go criteria for reuse based on permanent set, mass loss, or visible cracking.

## (g) Numbered References

1. Eriksson, J. & Kropp, W. "Measuring and analysis of pyrotechnic shock." Master's thesis, Chalmers University of Technology, 1999. (eriksson1999measuringandanalysis pages 12-18, eriksson1999measuringandanalysis pages 58-63)

2. Küçükbayram, A. İ. "Analysis and verification of a pyroshock test system." Master's thesis, 2021. (kucukbayram2021analysisandverification pages 144-145)

3. Nelsen, N. H., Kolb, J. D., Kulkarni, A., et al. "Advanced and Exploratory Shock Sensing Mechanisms." Sandia National Laboratories, SAND2017-9700, 2017. DOI: 10.2172/1395438 (nelsen2017advancedandexploratory pages 8-13)

4. Walter, P. L. "Selecting Accelerometers for and Assessing Data from Mechanical Shock Measurements." PCB Piezotronics / Endevco Technical Paper. (walterUnknownyearselectingaccelerometersfor pages 5-7, walterUnknownyearselectingaccelerometersfor pages 3-5, walterUnknownyearselectingaccelerometersfor pages 7-9, walterUnknownyearselectingaccelerometersfor pages 1-3) — References IEST RP-DTE011.1.

5. Kennedy, M. "Controlled Pyroshock Test Transients Can Be Used To Better Match Operational Shock Transients." 91st SAVE Symposium, 2021. DOI: 10.2172/1819729 (kennedy2021controlledpyroshocktest pages 31-32)

6. Yan, Y. "Structural Response under Shock Environment." PhD thesis, 2020. (yan2020structuralresponseunder pages 36-38)

7. Farris, A., Pan, J., Liddicoat, A., et al. "Drop test reliability of lead-free chip scale packages." *Proc. 58th ECTC*, pp. 1173–1180, 2008. DOI: 10.1109/ectc.2008.4550124 (farris2008droptestreliability pages 2-3)

8. Kang, T. M., et al. "A study on the correlation between experiment and simulation board level drop test for SSD." *Proc. 18th EuroSimE*, pp. 1–6, 2017. DOI: 10.1109/eurosime.2017.7926215 (kang2017astudyon pages 1-3)

9. Karppinen, J., et al. "Shock impact reliability characterization of a handheld product in accelerated tests and use environment." *Microelectron. Reliab.*, 52:190–198, 2012. DOI: 10.1016/j.microrel.2011.09.001 (karppinen2012shockimpactreliability pages 6-7)

10. Andrew, J. J., et al. "Energy absorption and self-sensing performance of 3D printed CF/PEEK cellular composites." *Mater. Des.*, 208:109863, 2021. DOI: 10.1016/j.matdes.2021.109863 (andrew2021energyabsorptionand pages 10-13, andrew2021energyabsorptionand pages 23-25)

11. Bustilhan, A., et al. "Enhancing Mechanical Energy Absorption of Honeycomb and TPMS Lattice Structures Produced by FDM in Reusable Polymers." *Polymers*, 17:1111, 2025. DOI: 10.3390/polym17081111 (bustihan2025enhancingmechanicalenergy pages 9-11, bustihan2025enhancingmechanicalenergy pages 14-16, bustihan2025enhancingmechanicalenergy pages 11-14, bustihan2025enhancingmechanicalenergy pages 25-26)

12. Monkova, K., et al. "Mechanical Vibration Damping and Compression Properties of a Lattice Structure." *Materials*, 14:1502, 2021. DOI: 10.3390/ma14061502 (monkova2021mechanicalvibrationdamping pages 6-8)

13. Fayyaz, et al. "Damping Optimization and Energy Absorption of Mechanical Metamaterials for Enhanced Vibration Control Applications: A Critical Review." *Polymers*, 17:237, 2025. DOI: 10.3390/polym17020237 (fayyaz2025dampingoptimizationand pages 20-21, fayyaz2025dampingoptimizationand pages 11-13)

14. Mohamad, N., et al. "Vibrational damping behaviors of graphene nanoplatelets reinforced NR/EPDM nanocomposites." *J. Mech. Eng. Sci.*, 11:3274–3287, 2017. DOI: 10.15282/jmes.11.4.2017.28.0294 (mohamad2017vibrationaldampingbehaviors pages 3-6)

15. Murčinková, Z., et al. "Damping properties of fibre composite and conventional materials measured by free damped vibration response." *Adv. Mech. Eng.*, 11(5), 2019. DOI: 10.1177/1687814019847009 (murcinkova2019dampingpropertiesof pages 6-7, murcinkova2019dampingpropertiesof pages 1-2)

16. Xu, P., et al. "Crash performance and multi-objective optimization of a gradual energy-absorbing structure for subway vehicles." *Int. J. Mech. Sci.*, 107:1–12, 2016. DOI: 10.1016/j.ijmecsci.2016.01.001 (xu2016crashperformanceand pages 9-12)

17. Mamun, O., Bause, M. & Hai, B. S. M. E. "Accelerated development of multi-component alloys in discrete design space using Bayesian multi-objective optimisation." *Mach. Learn.: Sci. Technol.*, 6:015001, 2025. DOI: 10.1088/2632-2153/ada47d (mamun2025accelerateddevelopmentof pages 12-15, mamun2025accelerateddevelopmentof pages 15-19, mamun2025accelerateddevelopmentof pages 4-8)

18. Bogahawaththage, P. & Bogahawaththa, M. R. "Dynamic Response and Energy Absorption of Fractal Inspired Porous Structures." PhD thesis, 2025. (bogahawaththage2025dynamicresponseand pages 64-68)

19. Yu, M., et al. "Monolithically integrated triaxial high-performance high-g accelerometer for high shock vibration signal measurements." *Microsyst. Nanoeng.*, 11, 2025. DOI: 10.1038/s41378-025-01051-w (yu2025monolithicallyintegratedtriaxial pages 6-7)

20. Lamb, L. R. "Contribution of air flow to impact attenuation in chamber structures." MSc thesis, University of Ottawa, 2008. DOI: 10.20381/ruor-12180 (lamb2008contributionofair pages 66-71)

21. ASTM D5276: Standard Test Method for Drop Test of Loaded Containers by Free Fall.

22. ASTM D1596: Standard Test Method for Dynamic Shock Cushioning Characteristics of Packaging Material.

23. ASTM D4168: Standard Test Methods for Transmitted Shock Characteristics of Foam-in-Place Cushioning Materials.

24. JEDEC JESD22-B111: Board Level Drop Test Method of Components for Handheld Electronic Products.

25. IEST RP-DTE011.1: Selection of Transducers for Shock and Vibration Measurements.

References

1. (farris2008droptestreliability pages 2-3): Andrew Farris, Jianbiao Pan, Albert Liddicoat, Brian J. Toleno, Dan Maslyk, Dongkai Shangguan, Jasbir Bath, Dennis Willie, and David A. Geiger. Drop test reliability of lead-free chip scale packages. 2008 58th Electronic Components and Technology Conference, pages 1173-1180, May 2008. URL: https://doi.org/10.1109/ectc.2008.4550124, doi:10.1109/ectc.2008.4550124. This article has 42 citations.

2. (nelsen2017advancedandexploratory pages 8-13): Nicholas H. Nelsen, James D. Kolb, A. Kulkarni, Zachary Sorscher, Clayton D. Habing, Allen T. Mathis, and Z. Beller. Advanced and exploratory shock sensing mechanisms. ArXiv, Sep 2017. URL: https://doi.org/10.2172/1395438, doi:10.2172/1395438. This article has 0 citations.

3. (kennedy2021controlledpyroshocktest pages 31-32): Monty Kennedy. Controlled pyroshock test transients can be used to better match operational shock transients and reduce artificial pyroshock test failures [slides]. 91.Shock and Vibration Exchange (SAVE) Symposium, Orland, FL (United States), 19-23 Sep 2021, Aug 2021. URL: https://doi.org/10.2172/1819729, doi:10.2172/1819729. This article has 0 citations.

4. (walterUnknownyearselectingaccelerometersfor pages 5-7): PL Walter. Selecting accelerometers for and assessing data from mechanical shock measurements. Unknown journal, Unknown year.

5. (walterUnknownyearselectingaccelerometersfor pages 7-9): PL Walter. Selecting accelerometers for and assessing data from mechanical shock measurements. Unknown journal, Unknown year.

6. (eriksson1999measuringandanalysis pages 58-63): J Eriksson and W Kropp. Measuring and analysis of pyrotechnic shock. Unknown journal, 1999.

7. (kucukbayram2021analysisandverification pages 144-145): Aİ Küçükbayram. Analysis and verification of a pyroshock test system. Unknown journal, 2021.

8. (monkova2021mechanicalvibrationdamping pages 6-8): Katarina Monkova, Martin Vasina, Milan Zaludek, Peter Pavol Monka, and Jozef Tkac. Mechanical vibration damping and compression properties of a lattice structure. Materials, 14:1502, Mar 2021. URL: https://doi.org/10.3390/ma14061502, doi:10.3390/ma14061502. This article has 75 citations.

9. (fayyaz2025dampingoptimizationand pages 11-13): Fayyaz, Salem Bashmal, Aamer Nazir, Sikandar Khan, and Abdulrahman Alofi. Damping optimization and energy absorption of mechanical metamaterials for enhanced vibration control applications: a critical review. Polymers, 17:237, Jan 2025. URL: https://doi.org/10.3390/polym17020237, doi:10.3390/polym17020237. This article has 24 citations.

10. (mohamad2017vibrationaldampingbehaviors pages 3-6): N. Mohamad, J. Yaakub, H.E. Ab Maulod, A.R. Jeefferie, M.Y. Yuhazri, K.T. Lau, Q. Ahsan, M.I. Shueb, and R. Othman. Vibrational damping behaviors of graphene nanoplatelets reinforced nr/epdm nanocomposites. Journal of Mechanical Engineering and Sciences, 11:3274-3287, Dec 2017. URL: https://doi.org/10.15282/jmes.11.4.2017.28.0294, doi:10.15282/jmes.11.4.2017.28.0294. This article has 33 citations.

11. (murcinkova2019dampingpropertiesof pages 6-7): Zuzana Murčinková, Imrich Vojtko, Michal Halapi, and Mária Šebestová. Damping properties of fibre composite and conventional materials measured by free damped vibration response. Advances in Mechanical Engineering, May 2019. URL: https://doi.org/10.1177/1687814019847009, doi:10.1177/1687814019847009. This article has 36 citations and is from a peer-reviewed journal.

12. (murcinkova2019dampingpropertiesof pages 1-2): Zuzana Murčinková, Imrich Vojtko, Michal Halapi, and Mária Šebestová. Damping properties of fibre composite and conventional materials measured by free damped vibration response. Advances in Mechanical Engineering, May 2019. URL: https://doi.org/10.1177/1687814019847009, doi:10.1177/1687814019847009. This article has 36 citations and is from a peer-reviewed journal.

13. (andrew2021energyabsorptionand pages 10-13): J. Jefferson Andrew, Hasan Alhashmi, Andreas Schiffer, S. Kumar, and Vikram S. Deshpande. Energy absorption and self-sensing performance of 3d printed cf/peek cellular composites. Materials & Design, 208:109863, Oct 2021. URL: https://doi.org/10.1016/j.matdes.2021.109863, doi:10.1016/j.matdes.2021.109863. This article has 151 citations and is from a highest quality peer-reviewed journal.

14. (andrew2021energyabsorptionand pages 23-25): J. Jefferson Andrew, Hasan Alhashmi, Andreas Schiffer, S. Kumar, and Vikram S. Deshpande. Energy absorption and self-sensing performance of 3d printed cf/peek cellular composites. Materials & Design, 208:109863, Oct 2021. URL: https://doi.org/10.1016/j.matdes.2021.109863, doi:10.1016/j.matdes.2021.109863. This article has 151 citations and is from a highest quality peer-reviewed journal.

15. (bustihan2025enhancingmechanicalenergy pages 14-16): Alin Bustihan, Ioan Botiz, Ricardo Branco, and Rui F. Martins. Enhancing mechanical energy absorption of honeycomb and triply periodic minimal surface lattice structures produced by fused deposition modelling in reusable polymers. Polymers, 17:1111, Apr 2025. URL: https://doi.org/10.3390/polym17081111, doi:10.3390/polym17081111. This article has 11 citations.

16. (bustihan2025enhancingmechanicalenergy pages 25-26): Alin Bustihan, Ioan Botiz, Ricardo Branco, and Rui F. Martins. Enhancing mechanical energy absorption of honeycomb and triply periodic minimal surface lattice structures produced by fused deposition modelling in reusable polymers. Polymers, 17:1111, Apr 2025. URL: https://doi.org/10.3390/polym17081111, doi:10.3390/polym17081111. This article has 11 citations.

17. (bustihan2025enhancingmechanicalenergy pages 9-11): Alin Bustihan, Ioan Botiz, Ricardo Branco, and Rui F. Martins. Enhancing mechanical energy absorption of honeycomb and triply periodic minimal surface lattice structures produced by fused deposition modelling in reusable polymers. Polymers, 17:1111, Apr 2025. URL: https://doi.org/10.3390/polym17081111, doi:10.3390/polym17081111. This article has 11 citations.

18. (bogahawaththage2025dynamicresponseand pages 64-68): P Bogahawaththage and MR Bogahawaththa. Dynamic response and energy absorption of fractal inspired porous structures. Unknown journal, 2025.

19. (xu2016crashperformanceand pages 9-12): Ping Xu, Chengxing Yang, Yong Peng, Shuguang Yao, Dehong Zhang, and Benhuai Li. Crash performance and multi-objective optimization of a gradual energy-absorbing structure for subway vehicles. International Journal of Mechanical Sciences, 107:1-12, Mar 2016. URL: https://doi.org/10.1016/j.ijmecsci.2016.01.001, doi:10.1016/j.ijmecsci.2016.01.001. This article has 125 citations and is from a peer-reviewed journal.

20. (bustihan2025enhancingmechanicalenergy pages 11-14): Alin Bustihan, Ioan Botiz, Ricardo Branco, and Rui F. Martins. Enhancing mechanical energy absorption of honeycomb and triply periodic minimal surface lattice structures produced by fused deposition modelling in reusable polymers. Polymers, 17:1111, Apr 2025. URL: https://doi.org/10.3390/polym17081111, doi:10.3390/polym17081111. This article has 11 citations.

21. (kang2017astudyon pages 1-3): Tae Min Kang, Yong Chang Lee, Byung Kwon Bae, Won Seob Song, and Jae Sung Lee. A study on the correlation between experiment and simulation board level drop test for ssd. 2017 18th International Conference on Thermal, Mechanical and Multi-Physics Simulation and Experiments in Microelectronics and Microsystems (EuroSimE), pages 1-6, Apr 2017. URL: https://doi.org/10.1109/eurosime.2017.7926215, doi:10.1109/eurosime.2017.7926215. This article has 5 citations.

22. (karppinen2012shockimpactreliability pages 6-7): J. Karppinen, J. Li, J. Pakarinen, T.T. Mattila, and M. Paulasto-Kröckel. Shock impact reliability characterization of a handheld product in accelerated tests and use environment. Microelectron. Reliab., 52:190-198, Jan 2012. URL: https://doi.org/10.1016/j.microrel.2011.09.001, doi:10.1016/j.microrel.2011.09.001. This article has 37 citations.

23. (yan2020structuralresponseunder pages 36-38): Y Yan. Structural response under shock environment. Unknown journal, 2020.

24. (walterUnknownyearselectingaccelerometersfor pages 1-3): PL Walter. Selecting accelerometers for and assessing data from mechanical shock measurements. Unknown journal, Unknown year.

25. (walterUnknownyearselectingaccelerometersfor pages 3-5): PL Walter. Selecting accelerometers for and assessing data from mechanical shock measurements. Unknown journal, Unknown year.

26. (eriksson1999measuringandanalysis pages 12-18): J Eriksson and W Kropp. Measuring and analysis of pyrotechnic shock. Unknown journal, 1999.

27. (mamun2025accelerateddevelopmentof pages 12-15): Osman Mamun, Markus Bause, and Bhuiyan Shameem Mahmood Ebna Hai. Accelerated development of multi-component alloys in discrete design space using bayesian multi-objective optimisation. Jan 2025. URL: https://doi.org/10.1088/2632-2153/ada47d, doi:10.1088/2632-2153/ada47d. This article has 9 citations and is from a peer-reviewed journal.

28. (mamun2025accelerateddevelopmentof pages 15-19): Osman Mamun, Markus Bause, and Bhuiyan Shameem Mahmood Ebna Hai. Accelerated development of multi-component alloys in discrete design space using bayesian multi-objective optimisation. Jan 2025. URL: https://doi.org/10.1088/2632-2153/ada47d, doi:10.1088/2632-2153/ada47d. This article has 9 citations and is from a peer-reviewed journal.

29. (mamun2025accelerateddevelopmentof pages 4-8): Osman Mamun, Markus Bause, and Bhuiyan Shameem Mahmood Ebna Hai. Accelerated development of multi-component alloys in discrete design space using bayesian multi-objective optimisation. Jan 2025. URL: https://doi.org/10.1088/2632-2153/ada47d, doi:10.1088/2632-2153/ada47d. This article has 9 citations and is from a peer-reviewed journal.

30. (fayyaz2025dampingoptimizationand pages 20-21): Fayyaz, Salem Bashmal, Aamer Nazir, Sikandar Khan, and Abdulrahman Alofi. Damping optimization and energy absorption of mechanical metamaterials for enhanced vibration control applications: a critical review. Polymers, 17:237, Jan 2025. URL: https://doi.org/10.3390/polym17020237, doi:10.3390/polym17020237. This article has 24 citations.

31. (yu2025monolithicallyintegratedtriaxial pages 6-7): Mingzhi Yu, Xiaoyu Wu, Libo Zhao, Chen Jia, Yong Xia, Xiangguang Han, Tao Wang, and Guoxi Luo. Monolithically integrated triaxial high-performance high-g accelerometer for high shock vibration signal measurements. Microsystems &amp; Nanoengineering, Nov 2025. URL: https://doi.org/10.1038/s41378-025-01051-w, doi:10.1038/s41378-025-01051-w. This article has 1 citations and is from a domain leading peer-reviewed journal.

32. (lamb2008contributionofair pages 66-71): Leslie R Lamb. Contribution of air flow to impact attenuation in chamber structures. ArXiv, Nov 2008. URL: https://doi.org/10.20381/ruor-12180, doi:10.20381/ruor-12180. This article has 0 citations.