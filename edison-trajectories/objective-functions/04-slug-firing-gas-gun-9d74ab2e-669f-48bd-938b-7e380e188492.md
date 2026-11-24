# Edison LITERATURE_HIGH — Pneumatic slug-firing / gas-gun system for longer-duration impulse on tiled small-cell specimens

- task_id: `9d74ab2e-669f-48bd-938b-7e380e188492`
- slug: `04-slug-firing-gas-gun` (data source 04 of 5)
- job: `LITERATURE_HIGH`
- status: `success`
- fetched_at: `2026-05-21T15:18:29Z`
- source issue: vertical-cloud-lab/tensegrity-optimization#51 (parent #36 comment 4509305026)

---

Question: Pneumatic slug-firing / gas-gun system for longer-duration impulse on tiled small-cell specimens.

Data source 4 of 5 — Pneumatic "slug firing" / gas-gun system observed
adjacent to the Polytec LDV in the lab walkthrough. Jeff noted this
system produces a LONGER shock impulse than the M23 drop tower (so it
probes a different time-scale regime), and that an interesting variant
would be a tessellated small-unit-cell specimen with a hard plate in
front (i.e. a sacrificial / armour-plate framing).

Configuration as we understand it:
  * Compressed-gas reservoir + barrel, firing a metallic or polymer
    "slug" at a target plate held in a catch frame.
  * Velocities typically ~10-200 m/s (intermediate / sub-ordnance
    regime between drop tower (~5-10 m/s) and split-Hopkinson /
    Taylor-impact (~100-2000 m/s)).
  * Diagnostics: in-line photogate or laser tripwire for slug
    velocity; force on backing plate via piezo load washer or
    derived from the LDV signal (data source 5); high-speed camera
    side view.

Use cases we care about:
  * Probing strain-rate sensitivity of TPU 85A and PETG that is NOT
    observable on the M23 drop tower (the slug delivers a higher peak
    pressure and a longer impulse than free-fall from the M23's
    24-32 ft/s DeltaV).
  * Evaluating tiled / foam-like cell arrays (Pajunen-style or
    truncated-octahedron tilings from PR #24) as armour-style
    energy absorbers behind a sacrificial plate.
  * Generating a higher-energy data point for the multifidelity BO
    so the GP is informed beyond the M23 energy envelope.

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



# Pneumatic Slug-Firing / Gas-Gun System for Longer-Duration Impulse on Tiled Small-Cell Tensegrity Specimens

## (a) Raw Observables and Derived Physical Quantities

The pneumatic gas-gun system produces several categories of raw observables on a tensegrity energy-absorber specimen, each requiring specific processing to yield physically meaningful derived quantities.

**Primary raw observables and their processing:**

1. **Slug velocity** — measured via in-line laser photogates or a laser-line velocity sensor (LLVS). The LLVS photodiode intensity is calibrated to position and differentiated to yield a continuous velocity history; paired photogates yield average velocity from gate spacing divided by transit time (lee2006deformationrateeffects pages 6-10, fila2017impacttestingof pages 3-5). This is the most critical raw observable because all energy-normalized metrics depend on it.

2. **Transmitted force time history** — measured either by a piezoelectric load washer / dynamic load cell (e.g., Dytran 1060v5, 100 kN range) mounted behind the specimen (whisler2015experimentalandsimulated pages 2-4), or by strain gages on a transmission bar converted via one-dimensional elastic wave relations: F(t) = A₀ · E₀ · ε_t(t), where A₀ and E₀ are the bar cross-section and modulus and ε_t is transmitted strain (bhagavathula2018highratecompressive pages 8-12, lee2006deformationrateeffects pages 3-6). Anti-alias filtering and baseline correction are required before peak extraction.

3. **Specimen displacement and deformation** — obtained from high-speed camera imagery. Surface markers are tracked frame-to-frame and converted from pixels to physical coordinates; displacement d(t) yields engineering strain ε(t) = d(t)/L₀ and strain rate ε̇(t) = ḋ(t)/L₀ (rosso2020onthecompressive pages 3-6). Full-field DIC provides local strain maps and crush-front propagation speed (lee2006deformationrateeffects pages 3-6).

4. **LDV surface velocity** — when the Polytec LDV is aimed at the backing plate or specimen rear face, it provides a velocity-vs-time record that can be integrated for displacement or differentiated for acceleration. Combined with known backing mass, this yields a force surrogate (dattelbaum2019shockdrivendecompositionof pages 5-8).

5. **High-speed side-view video** — provides qualitative and quantitative records of deformation mode (buckling, shear band, densification front), rebound, and residual geometry (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8).

**Derived physical quantities** from synchronized force–displacement records include: peak transmitted force F_peak (N); impulse I = ∫F dt (N·s); absorbed energy E_abs = ∫F dδ (J); specific energy absorption SEA = E_abs / m_specimen (J/g); volumetric energy absorption VEA = ∫σ dε to densification (MJ/m³) (cronau2025energyabsorptionof pages 2-4); plateau/crush stress σ_pl; crush-force efficiency CFE = σ_pl / σ_peak (nasrullah2020designandoptimization pages 12-13); densification strain ε_d defined as the strain at which efficiency η(ε) peaks (rosso2020onthecompressive pages 10-13); cushion factor C_min and normalized energy metric W_min = C_min · ρ_rel (pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 8-9); damping ratio ζ and settling time from post-impact ring-down of the LDV or accelerometer signal; and residual strain from post-unload video or LDV integration (pajunen2019designandimpact pages 7-8).

The following table maps these observables to derived quantities in detail:

| Raw Observable | Sensor/Instrument | Derived Physical Quantity | Processing/Integration Step | Key Reference |
|---|---|---|---|---|
| Slug/projectile arrival times at two stations | Laser tripwire / through-beam photogates; LLVS photodiode | Slug velocity before impact; trigger time; estimated impact time | Compute velocity from gate spacing and interrupt times; optionally calibrate LLVS intensity to position, then differentiate position to get velocity history | (lee2006deformationrateeffects pages 6-10, fila2017impacttestingof pages 3-5) |
| Continuous slug/impactor position during approach | Laser-line velocity sensor (LLVS) | Velocity history, displacement history, nominal specimen strain and strain rate | Calibrate photodiode intensity to position; differentiate for velocity history; integrate or directly use position to obtain displacement; compute strain as displacement over initial length and strain rate as displacement-rate over initial length | (lee2006deformationrateeffects pages 6-10, lee2006deformationrateeffects pages 3-6) |
| Transmitted bar strain waveform | Foil strain gages on transmission bar / incident-transmission bars; high-bandwidth amplifiers and digitizer | Transmitted force history, specimen stress history, dynamic equilibrium check | Convert voltage to strain using gage factor; apply 1D elastic wave relations to compute force; divide by initial area for nominal stress | (bhagavathula2018highratecompressive pages 8-12, lee2006deformationrateeffects pages 3-6) |
| Direct force signal near specimen | Piezo/dynamic load cell, e.g. Dytran 1060v5 100 kN; frame-mounted load cells | Force-time history; peak transmitted force; impulse | Calibrate voltage to force; baseline-correct; low-pass/filter as needed; take peak over contact window; integrate force over time for impulse | (whisler2015experimentalandsimulated pages 2-4, vanderklok2018anexperimentalinvestigation pages 1-2) |
| Specimen marker positions in image sequence | High-speed camera with tracked surface markers; e.g. Phantom v2512, Shimadzu HPVX-2 | Displacement, axial strain, local deformation mode, crush velocity | Track markers frame-to-frame; convert pixels to length; differentiate displacement for velocity; compute engineering or true strain from gauge-length change | (rosso2020onthecompressive pages 3-6, bhagavathula2018highratecompressive pages 8-12) |
| Full-field deformation images | High-speed camera + DIC / profilometry / projection grating | Full-field displacement, strain localization, out-of-plane deformation, collapse mode | Correlate image subsets or reconstruct shape from profilometry; spatially smooth if needed; extract local strain fields, front motion, and mode maps | (lee2006deformationrateeffects pages 3-6, vanderklok2018anexperimentalinvestigation pages 1-2) |
| High-speed side-view video of specimen crush | High-speed camera, synchronized to impact trigger | Densification onset, crush-front propagation speed, rebound, residual strain, failure sequence | Time-window video around impact; identify first contact and densification frame; measure crush-front position versus time; compare unloaded height to initial height for residual strain | (whisler2015experimentalandsimulated pages 2-4, pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8) |
| Projectile initial and residual velocity from imaging | Dual high-speed cameras or pre/post-impact video frames | Energy absorbed by specimen; momentum transfer; ballistic-limit style metrics | Extract pre/post velocity from frame-to-frame motion; compute absorbed kinetic energy and momentum loss from projectile mass and velocity change | (vanderklok2018anexperimentalinvestigation pages 1-2, pajunen2019designandimpact pages 7-8) |
| Surface velocity time history | LDV / PDV / VISAR-style velocimetry on target/backing plate or specimen surface | Surface velocity, displacement, acceleration, ring-down frequency/damping; pressure/force surrogate if backing mass known | Baseline-correct velocity; integrate once for displacement, differentiate for acceleration; window free-decay tail for modal fit; combine with backing mass/impedance model if inferring force | (dattelbaum2019shockdrivendecompositionof pages 5-8) |
| Force-displacement loop from synchronized force and optical displacement | Combined load cell/bar gages + high-speed video / DIC / LDV | Absorbed energy, SEA, plateau force/stress, crush-force efficiency, densification strain | Synchronize channels on common trigger; resample to common time base; integrate area under force-displacement or stress-strain curve to densification; divide by specimen mass for SEA; compute mean/peak ratios for efficiency metrics | (whisler2015experimentalandsimulated pages 2-4, cronau2025energyabsorptionof pages 2-4, nasrullah2020designandoptimization pages 12-13) |
| Oscillatory unloading / ring-down after impact | Accelerometer, LDV, or video-tracked displacement | Settling time, damping ratio, restitution / rebound fraction | Window post-peak decay; use logarithmic decrement or envelope fit for damping ratio; compute settling time to specified band; compare rebound height/velocity to incident state | (pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 5-7) |
| DAQ waveforms from 16-bit digitizer / oscilloscope | 16-bit PCI-9826H up to 20 MHz; oscilloscope up to 500 MHz | Time-resolved, synchronized multimodal observables with quantified timing fidelity | Trigger on near photogate or incident strain signal; preserve pre-trigger segment; align force, velocity, and video timestamps before deriving cross-metrics | (fila2017impacttestingof pages 3-5, bhagavathula2018highratecompressive pages 8-12) |


*Table: This table maps the main raw signals available in a pneumatic slug-impact test to the physical quantities that can be derived from them. It is useful for planning instrumentation and for defining trustworthy BO metrics such as peak transmitted force, SEA, densification strain, and damping-related measures.*

## (b) Bayesian-Optimization Objectives

The gas-gun modality is uniquely suited to probing strain-rate–sensitive behavior that the M23 drop tower cannot access. TPU 85A exhibits clear strain-rate sensitivity: elastic modulus and flow stress increase significantly from quasi-static to intermediate rates (~40–270 s⁻¹) (he2021anovelmethodology pages 4-5, he2021anovelmethodology pages 5-7), and FDM-printed TPU shows a 12.4% compressive-strength increase at 100% vs. 80% infill at ~2500 s⁻¹ (chaudhry2020evaluatingfdmprocess pages 1-3). Dynamic compressive strength of 3D-printed cellular polymers can increase by up to 87% from quasi-static to gas-gun rates (rosso2020onthecompressive pages 17-19, rosso2020onthecompressive pages 1-3). These rate effects make gas-gun–derived metrics non-redundant with drop-tower data.

**Most defensible BO objectives from this modality:**

- **Peak transmitted force F_peak (N) — minimize.** Directly measurable from the load cell or bar gage. Noise floor is set by gage noise (~±1 µε on bar gages, corresponding to ~20% of initial yield strain for very compliant foams) (bhagavathula2018highratecompressive pages 8-12). For specimens generating substantial force, CoV is typically 5–10% across nominally identical printed specimens, driven by manufacturing variability.

- **Specific energy absorption SEA (J/g) — maximize.** Computed from the integrated force–displacement area divided by specimen mass. Literature values for optimized lattice absorbers range from ~24.6 J/g (bio-inspired curved-elliptical lattice at 8% relative density) (tuninetti2025biomimeticlatticestructures pages 12-14) to ~50 kJ/kg for tapered lattice subfloor components (nasrullah2020designandoptimization pages 12-13). For the tensegrity-inspired structures of Pajunen et al., the target performance region is W_min < 0.21 at relative density < 0.1, with the spherically-jointed design achieving the lowest W_min among tested polymer metamaterials (pajunen2019designandimpact pages 8-9).

- **Crush/plateau efficiency η = σ_mean / σ_peak — maximize.** Lattice-optimized designs achieve CFE values of 0.97–1.13 (nasrullah2020designandoptimization pages 12-13), far exceeding conventional tubes (CFE ~0.41). This metric is robust because it is a ratio and partially cancels systematic force-measurement offsets.

- **Densification strain ε_d — maximize (within envelope).** Defined as the strain at which the energy-absorption efficiency η(ε) peaks (rosso2020onthecompressive pages 10-13). Typical values for polymer cellular materials are 0.5–0.8 depending on relative density.

- **Damping ratio ζ / settling time** — derivable from post-impact LDV or accelerometer ring-down. Relevant to the crutch-tip and egg-drop use cases where rebound must be minimized. Units: dimensionless (ζ) or ms (settling time).

- **Reuse count N_reuse — maximize.** Pajunen et al. demonstrated 24 repeated impacts with average residual strain per impact of only ~0.11% and total accumulated strain of 2.28% (pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 5-7). This is a candidate secondary objective; it requires a protocol-defined residual-strain threshold (e.g., 5% permanent set) and a fixed post-impact readout schedule because TPU viscoelastic recovery can mask permanent set if measured too early (pajunen2019designandimpact pages 7-8).

**Repeatability considerations:** For bar-based force measurement, background noise of ~±1 µε was observed (bhagavathula2018highratecompressive pages 8-12). Camera-based displacement has ~1-pixel uncertainty over ~100 px gauge length (bhagavathula2018highratecompressive pages 8-12). These set the noise floors for force and strain channels respectively. Across nominally identical 3D-printed specimens, CoV of 5–15% is typical for energy-absorption metrics due to manufacturing scatter in FFF parts.

## (c) Constraints

Several derived quantities are better treated as hard or chance constraints rather than continuous objectives in the qNEHVI formulation:

- **F_peak ≤ F_threshold:** For the egg-drop demo, the transmitted force must not exceed the egg-shell fracture threshold. For human-body protective applications, EN 1621 requires transmitted force ≤ 35 kN (motorbike armor) and ≤ 18 kN (shoulder/elbow). For the crutch-tip use case, a peak deceleration constraint of ~150–200 g is typical for biomechanical safety.

- **Densification strain ε_d ≥ 0.5:** Specimens that densify prematurely transmit force spikes. A minimum densification strain ensures adequate stroke before lockup. Values of 0.5–0.7 are typical targets for cellular absorbers at 10–25% relative density (rosso2020onthecompressive pages 10-13).

- **Residual strain ≤ 5% after single impact:** For reusable absorbers, permanent deformation must stay below a threshold. Pajunen et al. showed <0.2% per impact for their tensegrity designs (pajunen2019designandimpact pages 7-8), so 5% is a conservative bound that allows for higher-energy gas-gun loading.

- **SEA ≥ SEA_min:** Linghu (2018) used a normalized SEA threshold of 0.7 (i.e., SEA ≥ 0.7 × SEA_max of the design space) as a constraint, noting "A higher SEA is desirable so the threshold was set as 0.7" (linghu2018effectoffea pages 33-40). For the present system, an absolute lower bound of ~5 J/g is a reasonable starting constraint based on literature benchmarks for polymer cellular materials.

- **CFE ≥ 0.5:** Crush-force efficiency below 0.5 indicates a large initial peak relative to plateau, which is undesirable for all three use cases. Optimized lattice designs achieve 0.97–1.13 (nasrullah2020designandoptimization pages 12-13).

- **Specimen mass ≤ 500 g** and **relative density 10–25%:** These are geometric/manufacturing constraints that bound the design space directly.

## (d) Characterization Settings

The following table consolidates recommended instrumentation and protocol settings drawn from peer-reviewed gas-gun, SHPB, and tensegrity-impact studies:

| Parameter | Recommended Value/Range | Justification/Source |
|---|---:|---|
| DAQ sampling rate | ≥1 MHz minimum; 20 MHz preferred for strain/photogate channels; up to 500 MHz oscilloscope-class capture when resolving very short transients | Fíla et al. recorded bar and trigger signals with a 16-bit digitizer at up to 20 MHz; Bhagavathula et al. used a 12-bit oscilloscope at 500 MHz for SHPB/gas-gun foam tests. For a pneumatic slug rig, use at least MHz-class sampling so force and velocity pulses are not under-resolved. (fila2017impacttestingof pages 3-5, bhagavathula2018highratecompressive pages 8-12) |
| Anti-alias filter | Analog low-pass set below Nyquist; if reporting shock-style force pulses, also archive a CFC 1000-filtered channel | The retrieved gas-gun papers specify high-rate acquisition but do not state anti-alias settings; defensible practice is to set analog filtering below Nyquist and, for force histories intended to be compared across impact tests, report a filtered channel consistent with crash/shock practice. This row is standards-informed rather than directly specified in the cited papers. (fila2017impacttestingof pages 3-5, bhagavathula2018highratecompressive pages 8-12) |
| Load cell / force transducer range | 100 kN class starting point for small polymer absorbers; increase only if saturation is observed | Whisler and Kim used a Dytran 1060v5 dynamic load cell rated to 100 kN in gas-gun polyurethane-foam testing; this is an existence proof for the regime and a reasonable starting range for tiled polymer absorbers with sacrificial plates. (whisler2015experimentalandsimulated pages 2-4) |
| Strain gage specification for bar-based force measurement | 350 Ω foil gages, e.g. CEA-13-250UN-350, GF ≈ 2.13 | Bhagavathula et al. used 350 Ω Micro-Measurements CEA-13-250UN-350 gages with gauge factor 2.130 ± 0.5% on Hopkinson bars; this is directly transferable if the pneumatic rig uses instrumented bars or washers in a similar bandwidth regime. (bhagavathula2018highratecompressive pages 8-12) |
| Amplifier gain / bandwidth | Gain 10–100 for general bar signals; higher gain (100–1000) for weak transmitted signals; bandwidth ≥15–20 MHz | Fíla et al. used low-noise differential amplification with gains of 10 or 100 and bandwidths of about 20/15 MHz; Bhagavathula et al. increased gain to 100–1000 on the transmission channel because the transmitted signal was small. (fila2017impacttestingof pages 3-5, bhagavathula2018highratecompressive pages 8-12) |
| High-speed camera frame rate | 100 kfps–1 Mfps, selected from expected event duration and field of view | Fíla et al. chose 100,000 fps as a DIC compromise; Rosso and Iannucci used 601,850 fps; Bhagavathula et al. used 1,000,000 fps. For 10–200 m/s slug impacts on small specimens, this is the defensible literature envelope. (fila2017impacttestingof pages 3-5, bhagavathula2018highratecompressive pages 8-12, rosso2020onthecompressive pages 3-6) |
| High-speed camera resolution | Approximately 128×64 to 400×250 px at the above frame rates | Rosso and Iannucci used 128×64 px at 601,850 fps; Bhagavathula et al. used 400×250 px at 1 Mfps. Resolution is traded directly against frame rate in this modality. (bhagavathula2018highratecompressive pages 8-12, rosso2020onthecompressive pages 3-6) |
| Exposure / shutter time | About 1–2 μs target; keep ≤ specimen-feature blur limit | Rosso and Iannucci used 1.125 μs exposure at 601,850 fps. Lee et al. reported 5–20 μs exposures for DIC in related high-rate cellular tests, but for a small fast slug/plate event the Rosso setting is the stronger target. (rosso2020onthecompressive pages 3-6, lee2006deformationrateeffects pages 3-6) |
| Slug velocity measurement | Dual laser photogates / through-beam sensors or laser-line velocity sensor immediately upstream of target | Fíla et al. measured projectile speed with paired laser through-beam sensors on the barrel; Lee et al. used a laser-line velocity sensor to obtain continuous impactor position/velocity and used it for triggering. This makes photogates/tripwires the most defensible primary velocity observable for the pneumatic rig. (fila2017impacttestingof pages 3-5, lee2006deformationrateeffects pages 6-10) |
| Trigger / pretrigger | Trigger from near-target photogate or incident gage; retain 10–20% pretrigger in record | The cited setups emphasize critical triggering because record lengths are limited and correlation between force and video is essential; the papers do not give a numeric pretrigger fraction, so 10–20% is a recommended implementation choice consistent with capturing baseline/noise before impact. (fila2017impacttestingof pages 3-5, bhagavathula2018highratecompressive pages 8-12) |
| Chamber / barrel air management | Pull vacuum where possible; target <100 mbar and preferably much lower if available | Rosso and Iannucci evacuated to 100 mBar before firing; Lee et al. emphasize chamber evacuation to suppress air-cushion effects. For compliant cellular specimens this is important because trapped air can distort early force rise and velocity. (rosso2020onthecompressive pages 3-6, lee2006deformationrateeffects pages 6-10) |
| Pulse shaping | Use pulse shaping when bar-based constant-strain-rate loading is desired; 0.25 mm paper shaper is a literature example | Fíla et al. used a 0.25 mm paper pulse shaper; Bhagavathula et al. also used pulse shaping to obtain a near-rectangular input pulse. For a direct slug-on-plate rig this is optional, but it is recommended if the apparatus is reconfigured into bar-mediated loading. (fila2017impacttestingof pages 3-5, bhagavathula2018highratecompressive pages 8-12) |
| Optical tracking / DIC markers | Apply high-contrast surface markers or speckle; track at least 2 points if full-field DIC is not feasible | Rosso and Iannucci tracked black dots with Video Gauge; Bhagavathula et al. tracked point markers in the high-speed images; Lee et al. used DIC to recover displacement and strain fields. This is the most defensible optical route for specimen crush/displacement. (rosso2020onthecompressive pages 3-6, bhagavathula2018highratecompressive pages 8-12, lee2006deformationrateeffects pages 3-6) |
| Specimens per condition | n ≥ 3 minimum; more if estimating CoV for BO noise models | Pajunen et al. tested each sample three times at each impact energy and reported repeated-impact behavior, making n=3 the strongest directly cited minimum for this project stage. (pajunen2019designandimpact pages 7-8) |
| Applicable standards | ASTM E23; ASTM D7136/D7136M; ISO 6603-2 | None of the retrieved gas-gun architected-material papers cite a single governing standard for this exact pneumatic slug modality. For protocol scaffolding, ASTM E23 covers pendulum impact principles, ASTM D7136/D7136M is the established instrumented drop-weight composite impact standard, and ISO 6603-2 covers instrumented puncture impact of plastics; use them as adjacent standards rather than exact one-to-one prescriptions. (pajunen2019designandimpact pages 7-8, whisler2015experimentalandsimulated pages 2-4) |


*Table: This table summarizes defensible measurement settings for pneumatic slug/gas-gun tests on architected polymer energy absorbers, using the closest peer-reviewed gas-gun, SHPB, and tensegrity-impact literature found in the evidence set. It is useful as a draft test protocol for selecting DAQ, optics, triggering, and replication settings before integrating the modality into BO.*

**Key setting justifications:**

- **DAQ sampling rate ≥ 1 MHz:** Fíla et al. used a 16-bit digitizer at up to 20 MHz for SHPB bar signals and photogate triggers (fila2017impacttestingof pages 3-5); Bhagavathula et al. recorded at 500 MHz on a 12-bit oscilloscope (bhagavathula2018highratecompressive pages 8-12). For the intermediate-velocity regime (10–200 m/s) with contact durations of ~0.1–5 ms, 1 MHz minimum is needed; 5 MHz is recommended to resolve rise times.

- **High-speed camera:** 100,000–1,000,000 fps. Rosso and Iannucci used a Phantom v2512 at 601,850 fps with 128×64 px resolution and 1.125 µs exposure for gas-gun Taylor-impact tests on cellular polymers (rosso2020onthecompressive pages 3-6). Bhagavathula et al. used a Shimadzu HPVX-2 at 1,000,000 fps with 400×250 px (bhagavathula2018highratecompressive pages 8-12). For DIC-quality imaging, Fíla et al. chose 100,000 fps as a resolution compromise (fila2017impacttestingof pages 3-5).

- **Force transducer:** Dytran 1060v5 (100 kN range) is the directly cited dynamic load cell for gas-gun foam testing (whisler2015experimentalandsimulated pages 2-4). For bar-based measurement, 350 Ω foil strain gages (CEA-13-250UN-350, GF ≈ 2.13) with differential amplifiers at gains of 100–1000 on the transmission channel are recommended (bhagavathula2018highratecompressive pages 8-12).

- **Chamber vacuum:** ≤100 mbar to suppress air-cushion artifacts, per Rosso and Iannucci (rosso2020onthecompressive pages 3-6) and Lee et al. (lee2006deformationrateeffects pages 6-10).

- **Specimens per condition:** n ≥ 3, following Pajunen et al. who tested each sample three times per energy level (pajunen2019designandimpact pages 7-8).

- **Applicable standards:** No single ASTM/ISO standard precisely governs this pneumatic slug modality. ASTM D7136/D7136M (instrumented drop-weight impact on composites) and ISO 6603-2 (instrumented puncture impact of plastics) provide the closest protocol scaffolding for force-channel data reduction and reporting.

## (e) Integration into the BO Campaign (PR #30 + PR #33)

**Ax Metric / Objective shape:** Each gas-gun shot produces a vector of scalar outcomes: {F_peak, SEA, η, ε_d, ζ, N_reuse_increment}. These map to Ax `Metric` objects with `lower_is_better=True` for F_peak and `lower_is_better=False` for SEA, η, ε_d. In the qNEHVI formulation, F_peak and SEA are primary objectives; η and ε_d are constraints; N_reuse is a secondary objective or constraint.

**Observation noise model:** The gas-gun modality has higher shot-to-shot variability than the M23 drop tower due to velocity jitter and manufacturing scatter. A heteroscedastic noise model is recommended, with the noise variance for each metric estimated from replicate shots (n ≥ 3). Mo et al. model separate Gaussian noise terms for low- and high-fidelity data: y_H = f_H(x) + ε_H with learned σ_H (mo2023accelerateddesignof pages 7-9). For gas-gun data, initial σ estimates should be set from the CoV of replicate measurements (~5–15% of the metric value).

**Fidelity tier:** The gas-gun sits at a **higher fidelity and higher cost** tier than the M23 drop tower. In the multifidelity ladder:
- Tier C (lowest cost): MuJoCo rigid-body sim
- Tier B: NVIDIA Newton/Warp differentiable sim
- Tier A-low: M23 drop tower (~5–10 m/s)
- **Tier A-high: Gas-gun (~10–200 m/s)**
- Tier A-max: PolyFEM/IPC high-fidelity FEA

The autoregressive multifidelity GP framework of Mo et al. is directly applicable: y_high(x) = ρ · y_low(x) + δ(x), where low-fidelity data from the drop tower or simulations inform the GP prior, and sparse gas-gun shots refine the high-fidelity residual δ(x) (mo2023accelerateddesignof pages 7-9, mo2023accelerateddesignof pages 1-2). Cordelier et al. report that a cost ratio of 10–30× between fidelity tiers is practical, but recommend capping the effective ratio at ~10× in the acquisition function to avoid excessive low-fidelity sampling (cordelier2026multifidelityapproachesfor pages 13-15).

**Per-trial cost / wall-clock budget:** Each gas-gun shot requires ~5–15 minutes of setup (specimen mounting, chamber evacuation, slug loading) plus ~10 minutes of data processing, for ~20–30 minutes per trial. This is roughly 3–5× the cost of an M23 drop, making a cost ratio of ~3–5 between gas-gun and drop-tower fidelities appropriate for the acquisition function.

**Complementarity with other data sources:** The gas-gun provides the unique capability of probing strain-rate sensitivity that the M23 cannot access. It delivers a higher peak pressure and longer impulse than the M23's ~7–10 m/s ΔV (he2021anovelmethodology pages 4-5, rosso2020onthecompressive pages 17-19). The LDV (data source 5) can be co-deployed with the gas-gun for velocity measurement. The high-speed camera is shared infrastructure. The shaker (data source 3) provides low-amplitude transmissibility data that characterizes the linear regime, while the gas-gun characterizes the nonlinear crash regime. Together, these four modalities span quasi-static through intermediate-rate loading.

## (f) Top Gotchas, Failure Modes, and Cross-Talk Artifacts

The following ranked table details the 10 most critical failure modes that would silently corrupt BO objectives:

| Rank | Failure Mode / Artifact | Mechanism | BO Objective(s) Corrupted | Mitigation |
|---|---|---|---|---|
| 1 | Air-cushion / trapped-gas effect ahead of slug or specimen | Residual air in barrel/chamber adds a pneumatic preload and softens/extends first contact, distorting early force rise and apparent impulse; especially problematic for compliant cellular absorbers (lee2006deformationrateeffects pages 6-10, rosso2020onthecompressive pages 3-6) | Peak transmitted force, impulse, plateau stress, damping/settling metrics | Evacuate chamber/barrel before firing; verify vacuum level shot-by-shot; keep target standoff fixed; reject shots with abnormal pre-contact force rise |
| 2 | Loss of dynamic force equilibrium | Inertia and wave transit in cellular specimens mean front/back forces are not equal during early crushing, so a single force sensor can misrepresent true specimen stress/plateau response (lee2006deformationrateeffects pages 6-10, lee2006deformationrateeffects pages 3-6, rosso2020onthecompressive pages 10-13) | F_peak, SEA, crush efficiency, densification strain | Measure both projectile velocity and backing force; use optical crush history; report contact-window force with equilibrium check; avoid interpreting pre-equilibrium peaks as material properties |
| 3 | Slug velocity scatter from barrel friction / diaphragm rupture variability | Projectile-barrel friction, incomplete diaphragm rupture, and shot hardware variability change actual launch speed and pulse shape even at the same reservoir pressure (abbas1988developmentofa pages 125-136, abbas1988developmentofa pages 107-115) | All energy-normalized objectives: SEA, F_peak, g_max, densification, N_reuse comparisons | Measure velocity every shot with photogates/laser tripwire; use measured impact energy/momentum as covariates; maintain barrel cleanliness and diaphragm preparation; discard off-velocity shots |
| 4 | Specimen / plate misalignment | Spurious transverse motion, off-axis launch, or frame skew causes eccentric loading and asymmetric collapse, changing apparent peak force and failure mode (lee2006deformationrateeffects pages 6-10, lee2006deformationrateeffects pages 3-6) | F_peak, plateau efficiency, densification strain, reuse count, mode classification | Use self-centering catch frame/sabot guidance; verify coaxiality with witness shots; inspect high-speed video for tilt/yaw; reject visibly off-axis impacts |
| 5 | Non-planar or tilted impact | If slug/plate contact is not planar, local first contact creates spatially varying stress waves and false local peaks; waveform may look like material nonlinearity when it is actually contact geometry error (abbas1988developmentofa pages 125-136) | F_peak, transmitted impulse, inferred damping, strain-field features | Machine flat impact faces; use witness foil/contact prints; inspect high-speed side/front views; replace damaged slugs/plates; avoid reusing battered impactors |
| 6 | Sensor ringing / inertial contamination in force chain | Load cell or pressure transducer dynamics, mounting compliance, and fixture inertia create overshoot/oscillation not belonging to specimen response; static calibration may not hold for ms-scale events (elkarous2011investigationongas pages 3-5, kingstedt2015effectsofmicroand pages 38-42) | F_peak, g_max, settling time, damping ratio, transmissibility | Mount sensors stiffly with minimal intermediate mass; perform dynamic calibration/checks; compare force to optical/LDV-derived momentum balance; filter only after preserving raw waveform |
| 7 | Camera frame-rate / exposure mismatch to event duration | If frame rate is too low or shutter too long, crush-front motion, rebound, and densification onset are aliased or blurred; event timing then shifts relative to force channel (fila2017impacttestingof pages 3-5, rosso2020onthecompressive pages 3-6) | Densification strain, crush velocity, settling time, residual strain, SEA from force-displacement integration | Size frame rate from expected contact duration; use ~100 kfps-1 Mfps regime and μs-class exposure when needed; keep common trigger to DAQ; validate pixel blur on calibration shots |
| 8 | DIC / marker tracking quantization error | With only ~100 px gauge length, 1 px tracking uncertainty can materially bias strain and strain-rate estimates, especially for small residual strains or early elastic response (bhagavathula2018highratecompressive pages 8-12, rosso2020onthecompressive pages 3-6) | Densification strain, residual strain, damping/ring-down displacement, SEA via stress-strain area | Increase optical magnification and contrast; use more markers/full-field DIC; report displacement uncertainty; avoid overinterpreting sub-pixel-scale residual strain changes |
| 9 | Pulse-shaping or input-waveform inconsistency | Missing or inconsistent pulse shaping changes rise time and loading history, so two shots at similar velocity can probe different effective strain-rate regimes (fila2017impacttestingof pages 3-5, bhagavathula2018highratecompressive pages 8-12) | Strain-rate sensitivity trends, F_peak, plateau stress, BO model fidelity assignment | Standardize slug geometry and any pulse-shaper layer; archive the input waveform/velocity history; treat waveform class as metadata or fidelity tag in BO |
| 10 | Viscoelastic recovery masking permanent set | TPU-rich specimens can show immediate residual strain after impact that relaxes substantially within seconds to minutes, so “residual strain” depends on when it is measured (pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 5-7) | N_reuse, permanent set constraint, residual deformation objective | Fix a post-impact readout schedule (e.g., immediate, 60 s, 10 min); store both instantaneous and relaxed residual strain; do not mix time bases across trials |


*Table: This table ranks the most important silent failure modes that can corrupt Bayesian-optimization metrics in pneumatic slug/gas-gun tests of polymer tensegrity and lattice absorbers. It maps each artifact to the BO objectives it biases and gives concrete mitigations grounded in the cited experimental literature.*

Key highlights from the literature:

1. **Air cushion:** Lee et al. emphasize that chamber evacuation to ~40 Pa is essential to prevent air from cushioning the impact and distorting early force response in cellular specimens (lee2006deformationrateeffects pages 6-10).

2. **Force equilibrium failure:** At gas-gun rates, stress waves traverse cellular specimens in ~100 µs, and front/back forces are not equal during this period. Del Rosso and Iannucci observed step-wise compression within the first ~100 µs due to low wave speeds in foam (rosso2020onthecompressive pages 10-13). A single rear-face force sensor will underestimate early peak stress.

3. **Velocity scatter:** Abbas documented that barrel friction, incomplete diaphragm rupture, and projectile machining differences produce shot-to-shot velocity variability (abbas1988developmentofa pages 125-136). Every shot must have independently measured velocity.

4. **Viscoelastic recovery of TPU:** Pajunen et al. observed that at E_i/E_m ≈ 0.81, immediate post-impact remaining strain of ~3% largely recovered within one minute (pajunen2019designandimpact pages 7-8). This means N_reuse and residual-strain metrics are protocol-dependent: a fixed readout schedule is mandatory.

5. **DIC pixel quantization:** With ~100 px gauge length, 1 px tracking error gives ~1% strain uncertainty, which is comparable to the per-impact residual strain of tensegrity structures (~0.11% per impact) (bhagavathula2018highratecompressive pages 8-12, pajunen2019designandimpact pages 7-8). Sub-pixel interpolation or increased magnification is essential for residual-strain measurement.

## (g) References

1. Lee, S., Barthelat, F., Moldovan, N., Espinosa, H. D., & Wadley, H. N. G. (2006). Deformation rate effects on failure modes of open-cell Al foams and textile cellular materials. *International Journal of Solids and Structures*, 43, 53–73. doi:10.1016/j.ijsolstr.2005.06.101

2. Whisler, D. & Kim, H. (2015). Experimental and simulated high strain dynamic loading of polyurethane foam. *Polymer Testing*, 41, 219–230. doi:10.1016/j.polymertesting.2014.12.004

3. Del Rosso, S. & Iannucci, L. (2020). On the compressive response of polymeric cellular materials. *Materials*, 13, 457. doi:10.3390/ma13020457

4. Bhagavathula, K. B., Azar, A., Ouellet, S., Satapathy, S., Dennison, C. R., & Hogan, J. D. (2018). High rate compressive behaviour of a dilatant polymeric foam. *Journal of Dynamic Behavior of Materials*, 4, 573–585. doi:10.1007/s40870-018-0176-0

5. Fíla, T., Zlámal, P., Jiroušek, O., Falta, J., Koudelka, P., Kytýř, D., Doktor, T., & Valach, J. (2017). Impact testing of polymer-filled auxetics using split Hopkinson pressure bar. *Advanced Engineering Materials*, 19(10). doi:10.1002/adem.201700076

6. Pajunen, K., Johanns, P., Pal, R. K., Rimoli, J. J., & Daraio, C. (2019). Design and impact response of 3D-printable tensegrity-inspired structures. *Materials & Design*, 182, 107966. doi:10.1016/j.matdes.2019.107966

7. He, H., Deng, Q., Wang, C. X., Li, J., Weng, K. X., & Miao, Y. G. (2021). A novel methodology for large strain under intermediate strain rate loading. *Polymer Testing*, 97, 107142. doi:10.1016/j.polymertesting.2021.107142

8. Chen, H., Trivedi, A. R., & Siviour, C. R. (2020). Application of linear viscoelastic continuum damage theory to the low and high strain rate response of thermoplastic polyurethane. *Experimental Mechanics*, 60, 925–936. doi:10.1007/s11340-020-00608-2

9. Chaudhry, M. S. & Czekanski, A. (2020). Evaluating FDM process parameter sensitive mechanical performance of elastomers at various strain rates of loading. *Materials*, 13, 3202. doi:10.3390/ma13143202

10. Mo, C., Perdikaris, P., & Raney, J. R. (2023). Accelerated design of architected materials with multifidelity Bayesian optimization. *Journal of Engineering Mechanics*, 149(6). doi:10.1061/jenmdt.emeng-7033

11. You, P., Chen, H., Bahmani, B., & Espinosa, H. D. (2026). A multi-fidelity Bayesian neural operator for mechanics of spinodal metamaterial. *npj Computational Materials*. doi:10.1038/s41524-026-02112-y

12. Cordelier, O., Diouane, Y., Bartoli, N., & Laurendeau, É. (2026). Multi-fidelity approaches for general constrained Bayesian optimization with application to aircraft design. *arXiv*. doi:10.48550/arxiv.2603.28987

13. Linghu, Z. (2018). Effect of FEA epistemic uncertainty on design of cellular metamaterials with non-linear mechanical behavior. Cornell University. doi:10.7298/x4930rdk

14. VanderKlok, A., Stamm, A., Dorer, J., Hu, E., Auvenshine, M., Pereira, J. M., & Xiao, X. (2018). An experimental investigation into the high velocity impact responses of S2-glass/SC15 epoxy composite panels with a gas gun. *International Journal of Impact Engineering*, 111, 244–254. doi:10.1016/j.ijimpeng.2017.10.002

15. Nasrullah, A. I. H., Santosa, S. P., & Dirgantara, T. (2020). Design and optimization of crashworthy components based on lattice structure configuration. *Structures*, 26, 969–981. doi:10.1016/j.istruc.2020.05.001

16. Tuninetti, V. et al. (2025). Biomimetic lattice structures design and manufacturing for high stress, deformation, and energy absorption performance. *Biomimetics*, 10, 458. doi:10.3390/biomimetics10070458

17. Cronau, J. & Engstler, F. (2025). Energy absorption of 3D printed stochastic lattice structures under impact loading. *Progress in Additive Manufacturing*, 10, 3145–3156. doi:10.1007/s40964-025-01094-5

18. Dattelbaum, D. M. & Coe, J. D. (2019). Shock-driven decomposition of polymers and polymeric foams. *Polymers*, 11, 493. doi:10.3390/polym11030493

19. Pajunen, K., Celli, P., & Daraio, C. (2021). Prestrain-induced bandgap tuning in 3D-printed tensegrity-inspired lattice structures. *Extreme Mechanics Letters*, 44, 101236. doi:10.1016/j.eml.2021.101236

20. Elkarous, L., Robbe, C., Pirlot, M., & Golinval, J.-C. (2016). Dynamic calibration of piezoelectric transducers for ballistic high-pressure measurement. *International Journal of Metrology and Quality Engineering*, 7, 201. doi:10.1051/ijmqe/2016004

References

1. (lee2006deformationrateeffects pages 6-10): Sungsoo Lee, François Barthelat, Nicolaie Moldovan, Horacio D. Espinosa, and Haydn N.G. Wadley. Deformation rate effects on failure modes of open-cell al foams and textile cellular materials. International Journal of Solids and Structures, 43:53-73, Jan 2006. URL: https://doi.org/10.1016/j.ijsolstr.2005.06.101, doi:10.1016/j.ijsolstr.2005.06.101. This article has 148 citations and is from a domain leading peer-reviewed journal.

2. (fila2017impacttestingof pages 3-5): Tomáš Fíla, Petr Zlámal, Ondřej Jiroušek, Jan Falta, Petr Koudelka, Daniel Kytýř, Tomáš Doktor, and Jaroslav Valach. Impact testing of polymer‐filled auxetics using split hopkinson pressure bar. Advanced Engineering Materials, May 2017. URL: https://doi.org/10.1002/adem.201700076, doi:10.1002/adem.201700076. This article has 102 citations and is from a peer-reviewed journal.

3. (whisler2015experimentalandsimulated pages 2-4): Daniel Whisler and Hyonny Kim. Experimental and simulated high strain dynamic loading of polyurethane foam. Polymer Testing, 41:219-230, Feb 2015. URL: https://doi.org/10.1016/j.polymertesting.2014.12.004, doi:10.1016/j.polymertesting.2014.12.004. This article has 65 citations and is from a peer-reviewed journal.

4. (bhagavathula2018highratecompressive pages 8-12): Kapil Bharadwaj Bhagavathula, Austin Azar, Simon Ouellet, Sikhanda Satapathy, Christopher R. Dennison, and James David Hogan. High rate compressive behaviour of a dilatant polymeric foam. Journal of Dynamic Behavior of Materials, 4:573-585, Sep 2018. URL: https://doi.org/10.1007/s40870-018-0176-0, doi:10.1007/s40870-018-0176-0. This article has 20 citations and is from a peer-reviewed journal.

5. (lee2006deformationrateeffects pages 3-6): Sungsoo Lee, François Barthelat, Nicolaie Moldovan, Horacio D. Espinosa, and Haydn N.G. Wadley. Deformation rate effects on failure modes of open-cell al foams and textile cellular materials. International Journal of Solids and Structures, 43:53-73, Jan 2006. URL: https://doi.org/10.1016/j.ijsolstr.2005.06.101, doi:10.1016/j.ijsolstr.2005.06.101. This article has 148 citations and is from a domain leading peer-reviewed journal.

6. (rosso2020onthecompressive pages 3-6): Stefano Del Rosso and Lorenzo Iannucci. On the compressive response of polymeric cellular materials. Materials, 13:457, Jan 2020. URL: https://doi.org/10.3390/ma13020457, doi:10.3390/ma13020457. This article has 26 citations.

7. (dattelbaum2019shockdrivendecompositionof pages 5-8): Dana M. Dattelbaum and Joshua D. Coe. Shock-driven decomposition of polymers and polymeric foams. Polymers, 11:493, Mar 2019. URL: https://doi.org/10.3390/polym11030493, doi:10.3390/polym11030493. This article has 61 citations.

8. (pajunen2019designandimpact pages 5-7): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

9. (pajunen2019designandimpact pages 7-8): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

10. (cronau2025energyabsorptionof pages 2-4): J. Cronau and F. Engstler. Energy absorption of 3d printed stochastic lattice structures under impact loading – design parameters, manufacturing, and testing. Progress in Additive Manufacturing, 10:3145-3156, Apr 2025. URL: https://doi.org/10.1007/s40964-025-01094-5, doi:10.1007/s40964-025-01094-5. This article has 16 citations and is from a peer-reviewed journal.

11. (nasrullah2020designandoptimization pages 12-13): Alvian Iqbal Hanif Nasrullah, Sigit Puji Santosa, and Tatacipta Dirgantara. Design and optimization of crashworthy components based on lattice structure configuration. Structures, 26:969-981, Aug 2020. URL: https://doi.org/10.1016/j.istruc.2020.05.001, doi:10.1016/j.istruc.2020.05.001. This article has 96 citations and is from a peer-reviewed journal.

12. (rosso2020onthecompressive pages 10-13): Stefano Del Rosso and Lorenzo Iannucci. On the compressive response of polymeric cellular materials. Materials, 13:457, Jan 2020. URL: https://doi.org/10.3390/ma13020457, doi:10.3390/ma13020457. This article has 26 citations.

13. (pajunen2019designandimpact pages 8-9): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

14. (vanderklok2018anexperimentalinvestigation pages 1-2): Andy VanderKlok, Andy Stamm, James Dorer, Eryi Hu, Matthew Auvenshine, J. Michael Pereira, and Xinran Xiao. An experimental investigation into the high velocity impact responses of s2-glass/sc15 epoxy composite panels with a gas gun. International Journal of Impact Engineering, 111:244-254, Jan 2018. URL: https://doi.org/10.1016/j.ijimpeng.2017.10.002, doi:10.1016/j.ijimpeng.2017.10.002. This article has 36 citations and is from a domain leading peer-reviewed journal.

15. (he2021anovelmethodology pages 4-5): H. He, Q. Deng, C.X. Wang, J. Li, K.X. Weng, and Y.G. Miao. A novel methodology for large strain under intermediate strain rate loading. Polymer Testing, 97:107142, May 2021. URL: https://doi.org/10.1016/j.polymertesting.2021.107142, doi:10.1016/j.polymertesting.2021.107142. This article has 20 citations and is from a peer-reviewed journal.

16. (he2021anovelmethodology pages 5-7): H. He, Q. Deng, C.X. Wang, J. Li, K.X. Weng, and Y.G. Miao. A novel methodology for large strain under intermediate strain rate loading. Polymer Testing, 97:107142, May 2021. URL: https://doi.org/10.1016/j.polymertesting.2021.107142, doi:10.1016/j.polymertesting.2021.107142. This article has 20 citations and is from a peer-reviewed journal.

17. (chaudhry2020evaluatingfdmprocess pages 1-3): Muhammad Salman Chaudhry and Aleksander Czekanski. Evaluating fdm process parameter sensitive mechanical performance of elastomers at various strain rates of loading. Materials, 13:3202, Jul 2020. URL: https://doi.org/10.3390/ma13143202, doi:10.3390/ma13143202. This article has 59 citations.

18. (rosso2020onthecompressive pages 17-19): Stefano Del Rosso and Lorenzo Iannucci. On the compressive response of polymeric cellular materials. Materials, 13:457, Jan 2020. URL: https://doi.org/10.3390/ma13020457, doi:10.3390/ma13020457. This article has 26 citations.

19. (rosso2020onthecompressive pages 1-3): Stefano Del Rosso and Lorenzo Iannucci. On the compressive response of polymeric cellular materials. Materials, 13:457, Jan 2020. URL: https://doi.org/10.3390/ma13020457, doi:10.3390/ma13020457. This article has 26 citations.

20. (tuninetti2025biomimeticlatticestructures pages 12-14): Víctor Tuninetti, Sunny Narayan, Ignacio Ríos, Brahim Menacer, Rodrigo Valle, Moaz Al-lehaibi, Muhammad Usman Kaisan, Joseph Samuel, Angelo Oñate, Gonzalo Pincheira, Anne Mertens, Laurent Duchêne, and César Garrido. Biomimetic lattice structures design and manufacturing for high stress, deformation, and energy absorption performance. Biomimetics, 10:458, Jul 2025. URL: https://doi.org/10.3390/biomimetics10070458, doi:10.3390/biomimetics10070458. This article has 39 citations.

21. (linghu2018effectoffea pages 33-40): Zelin Linghu. Effect of fea epistemic uncertainty on design of cellular metamaterials with non-linear mechanical behavior. Text, Jan 2018. URL: https://doi.org/10.7298/x4930rdk, doi:10.7298/x4930rdk. This article has 0 citations and is from a peer-reviewed journal.

22. (mo2023accelerateddesignof pages 7-9): Chengyang Mo, Paris Perdikaris, and Jordan R. Raney. Accelerated design of architected materials with multifidelity bayesian optimization. Journal of Engineering Mechanics, Jun 2023. URL: https://doi.org/10.1061/jenmdt.emeng-7033, doi:10.1061/jenmdt.emeng-7033. This article has 11 citations.

23. (mo2023accelerateddesignof pages 1-2): Chengyang Mo, Paris Perdikaris, and Jordan R. Raney. Accelerated design of architected materials with multifidelity bayesian optimization. Journal of Engineering Mechanics, Jun 2023. URL: https://doi.org/10.1061/jenmdt.emeng-7033, doi:10.1061/jenmdt.emeng-7033. This article has 11 citations.

24. (cordelier2026multifidelityapproachesfor pages 13-15): Oihan Cordelier, Y. Diouane, Nathalie Bartoli, and Éric Laurendeau. Multi-fidelity approaches for general constrained bayesian optimization with application to aircraft design. ArXiv, Mar 2026. URL: https://doi.org/10.48550/arxiv.2603.28987, doi:10.48550/arxiv.2603.28987. This article has 1 citations.

25. (abbas1988developmentofa pages 125-136): SF Abbas. Development of a low cost shock pressure sensor. Unknown journal, 1988.

26. (abbas1988developmentofa pages 107-115): SF Abbas. Development of a low cost shock pressure sensor. Unknown journal, 1988.

27. (elkarous2011investigationongas pages 3-5): L Elkarous, M Pirlot, and JC Golinval. Investigation on gas pressure measurement inside small caliber weapons with piezoelectric transducers. Unknown journal, 2011.

28. (kingstedt2015effectsofmicroand pages 38-42): O Kingstedt. Effects of micro-and nano-structure on the deformation response of a ag60cu40 lamellar and rod-in-matrix eutectic alloy. Unknown journal, 2015.