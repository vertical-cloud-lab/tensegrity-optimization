# Edison LITERATURE_HIGH — High-speed (or slow-motion phone) video of the drop event for DIC-style strain mapping and densification tracking

- task_id: `7d6b43bf-d948-4e13-aea5-4a89ec12ed49`
- slug: `02-high-speed-camera` (data source 02 of 5)
- job: `LITERATURE_HIGH`
- status: `success`
- fetched_at: `2026-05-21T15:18:29Z`
- source issue: vertical-cloud-lab/tensegrity-optimization#51 (parent #36 comment 4509305026)

---

Question: High-speed (or slow-motion phone) video of the drop event for DIC-style strain mapping and densification tracking.

Data source 2 of 5 — High-speed video of the drop / crush event on the M23.

Two tiers are available:
  * High end: a high-speed camera checked out from the PSC (typical
    spec: monochrome, global shutter, 1-5 kfps at usable resolution,
    LED area lights).
  * Preliminary: a smartphone slow-motion setting (typically 240-960 fps
    rolling shutter, color, ~1080p).

Use cases we care about:
  * Visual confirmation of failure mode (strut fracture vs. tendon
    snap vs. joint pull-out vs. plate spall-back).
  * Frame-by-frame measurement of densification strain / crush
    displacement of the specimen plate-to-plate gap, then sync that
    against the accelerometer-derived force-displacement curve.
  * Optional 2D digital image correlation (DIC) on a speckle-painted
    face of the specimen to estimate full-field strain and bar
    buckling onset.
  * Reusability / re-deployability scoring: did the specimen return
    to its original shape between drops? Frame-comparison metric.

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



# Data Source 2 of 5: High-Speed / Slow-Motion Video for DIC-Style Strain Mapping and Densification Tracking on a Tensegrity Energy Absorber

---

## (a) Raw Observables and Derived Physical Quantities

The high-speed (or slow-motion phone) video of the M23 drop event produces a time-indexed sequence of grayscale (or color) images of one face of the tensegrity specimen as it undergoes impact, crush, and rebound. The primary raw observables are:

1. **Pixel intensity fields I(x, y, t)** — the gray-level image at each frame, from which DIC algorithms extract displacement fields u(x, y) and v(x, y) by subset-based cross-correlation between a reference image and each deformed image (xing2017highspeedphotographyand pages 24-25).
2. **Plate-to-plate gap d(t)** — the apparent distance between the top and bottom platens (or between the top face node and the base), trackable frame-by-frame even without full DIC, by edge detection or fiducial marker tracking.
3. **Qualitative failure-mode sequence** — visual identification of which structural member fails first (strut fracture, tendon snap, joint pull-out, plate spall-back) and the temporal order of events.

**Derived quantities and integration/filtering steps:**

- **Densification strain ε_d**: Defined as the engineering strain at which stress rises above the transmitted stress level and continues to rise (schaedler2014designingmetallicmicrolattices pages 1-2). Operationally, it can be taken as the strain corresponding to the global maximum of energy absorption efficiency (schaedler2014designingmetallicmicrolattices pages 6-7). From video, it is computed as ε_d = 1 − d_min/d_0, where d_min is the minimum plate gap observed and d_0 is the initial gap. This requires temporal low-pass filtering (e.g., Gaussian smoothing over ~5–25 frames) to suppress vibration noise (vinel2021metrologicalassessmentof pages 23-24).

- **Crush displacement δ(t)**: Time-resolved plate gap reduction, obtained by differencing the tracked platen positions. When synced against the accelerometer-derived force signal F(t), this yields the force–displacement curve F(δ) from which energy absorption is computed as E_a = ∫ F dδ (costas2014amultiobjectivesurrogatebased pages 1-2).

- **Full-field 2D strain maps ε_xx, ε_yy, ε_xy(x, y, t)** (optional, DIC-only): Obtained by spatial differentiation of DIC displacement fields over a virtual strain gauge (VSG) window. Requires Tikhonov or spatial regularization over several elements to control noise (vinel2021metrologicalassessmentof pages 23-24). These maps identify bar-buckling onset as localized compressive strain concentrations and distinguish bending-dominated from stretch-dominated collapse mechanisms (pajunen2019designandimpact pages 5-7).

- **Residual strain / shape recovery δ_residual**: Measured by comparing pre-drop and post-rebound frames. Pajunen et al. reported average remaining strain after 24 impacts of ~2.28%, with per-impact residual <0.2% that partially relaxed within one minute via viscoelastic recovery (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8).

- **Rebound coefficient of restitution e**: Extractable from the ratio of rebound to incoming velocity of the top face or the striker, measured by frame-to-frame tracking. Zhang reported e = 0.50–0.57 for tensegrity lander drop tests (zhang2022designofimpactresistant pages 33-37).

---

## (b) Derived Quantities as Bayesian-Optimization Objectives

The following table summarizes the main video-derivable quantities and their suitability as BO objectives:

| Quantity | Definition/Formula | Role (Objective/Constraint) | Typical Range in Literature | Units | Notes |
|---|---|---|---|---|---|
| Densification strain, `ε_d` | Strain at onset of densification; defined either where stress rises above transmitted stress and continues to rise, or operationally at a specified stress threshold; can also be taken at the global maximum of absorption efficiency (schaedler2014designingmetallicmicrolattices pages 1-2, andrew2021energyabsorptionand pages 10-13, schaedler2014designingmetallicmicrolattices pages 6-7) | Usually objective to maximize; sometimes constraint lower-bound to ensure usable stroke before bottom-out | ~0.48 for 3D-printable tensegrity-inspired structures; ~0.55 for Duocel foam; ~0.60–0.70 for CF/PEEK lattices; ~0.65–0.72 for polymer foams / TPU systems (schaedler2014designingmetallicmicrolattices pages 2-3, pajunen2019designandimpact pages 4-5, andrew2021energyabsorptionand pages 13-18) | strain or % | One of the most directly defensible video-derived quantities because it is observable plate-to-plate from frames and aligns naturally with force–displacement sync. |
| Specific energy absorption, `SEA` | `SEA = (1/ρ) ∫_0^{ε_d} σ(ε) dε`; equivalently `VEA/ρ_s`, where `VEA` is area under stress–strain curve up to `ε_d` (cronau2025energyabsorptionof pages 2-4, andrew2021energyabsorptionand pages 10-13) | Primary objective to maximize | In crashworthiness optimization, typical design-space values reported span roughly ~7.1 to 35.1 for one lattice family and ~8.8 to 33.5 for another (baykasoglu2020multiobjectivecrashworthinessoptimization pages 13-13) | J/g or MJ/m^3 normalized by density | Video alone gives `ε_d` and displacement; SEA becomes robust when synced with force from accelerometer/load cell rather than inferred optically. |
| Energy absorption efficiency, `η` | `η = U/U_max`, where `U_max` is ideal constant-stress absorption at the transmitted stress level; volumetric efficiency metric (schaedler2014designingmetallicmicrolattices pages 1-2, schaedler2014designingmetallicmicrolattices pages 2-3) | Good secondary objective to maximize; can also be used as a screening constraint | Bustihan reports ~36–47% over repeated compressions for reusable TPU honeycombs; microlattice/foam comparisons use efficiency-maximizing `ε_d` and often report optimums near densification (schaedler2014designingmetallicmicrolattices pages 2-3, bustihan2025reusable3dprintedthermoplastic pages 12-14) | dimensionless or % | Strong modality-specific metric because video identifies `ε_d`, which strongly affects `η`. |
| Peak transmitted force, `F_peak` | Maximum force during impact; from synced accelerometer/load-cell force history, or from striker acceleration if mass is known (pajunen2019designandimpact pages 4-5, pajunen2019designandimpact pages 5-7, baykasoglu2020multiobjectivecrashworthinessoptimization pages 13-13) | Primary objective to minimize; also natural hard/chance constraint | Optimization studies explicitly minimize PCF/peak crash force; tensegrity lander examples report impact-force scales ~360–524 N depending on orientation (zhang2022designofimpactresistant pages 33-37, baykasoglu2020multiobjectivecrashworthinessoptimization pages 13-13) | N | High-speed video does not measure force directly but gives failure mode and crush state at the instant of `F_peak`, improving interpretation of ringing or multi-peak events. |
| Crush load efficiency, `CLE` | Ratio of mean crush stress/load to maximum crush stress/load; values closer to 1 are better (bustihan2025reusable3dprintedthermoplastic pages 14-17, bustihan2025reusable3dprintedthermoplastic pages 5-7) | Secondary objective to maximize; can also be lower-bound constraint | Up to ~72–73.5% reported for twisted TPU honeycombs; lower and more rapidly degrading values seen in non-twisted or damaged samples (bustihan2025reusable3dprintedthermoplastic pages 14-17) | dimensionless or % | Useful for reusable absorbers because it rewards stable plateau crushing rather than one large first peak. |
| Force overshoot, `O` | `O = σ_p / σ_pl`, ratio of peak stress to plateau stress; ideal absorber has `O = 1` (cronau2025energyabsorptionof pages 2-4) | Usually objective to minimize; can be an upper-bound constraint | Ideal = 1; larger than 1 indicates undesirable initial spike; Cronau defines it explicitly for stochastic lattices (cronau2025energyabsorptionof pages 2-4) | dimensionless | Particularly relevant for cane-tip / payload-protection use-cases where first-hit spike matters more than total absorbed energy. |
| Residual strain / shape recovery / `N_reuse` proxy | Residual strain after unloading or after a fixed post-impact wait; can also be tracked over repeated impacts as retained geometry or stable metrics across cycles (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8, bustihan2025reusable3dprintedthermoplastic pages 7-9, desole2024energyabsorptionof pages 19-21) | Constraint for reusable designs; also candidate objective to minimize residual strain or maximize reuse count | Pajunen: average remaining strain after 24 impacts ~2.28%, average per-impact ~0.11%, with <0.2% after each impact in many tests and ~3% short-term residual relaxing toward ~0%; some PLA architectures survive 5 load-recovery cycles before failure; TPU studies commonly compare 3 cycles (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8, bustihan2025reusable3dprintedthermoplastic pages 14-17, desole2024energyabsorptionof pages 19-21) | strain, %, or count | This is the most uniquely video-native BO metric for this modality: frame comparison before/after impact directly measures recoverability. |
| Load ratio, `LR` | `LR = P_peak / P_m`, with `P_m = E_a/δ`; contrasts initial peak against mean crushing load (costas2014amultiobjectivesurrogatebased pages 1-2) | Objective to minimize; often paired with maximizing SEA | No universal threshold reported in gathered evidence; used directly as a crashworthiness objective in surrogate optimization (costas2014amultiobjectivesurrogatebased pages 1-2) | dimensionless | Closely related to overshoot/CLE; include only if force–displacement is well synchronized. |
| Plateau stress, `σ_pl` | Average stress between yield strain `ε_y` and densification strain `ε_d` (cronau2025energyabsorptionof pages 2-4) | Usually constraint band or secondary objective, depending on application | No single universal value across architectures; used together with `σ_p`, `ε_d`, and SEA to characterize absorber quality (cronau2025energyabsorptionof pages 2-4) | MPa | For direct human-contact absorbers, transmitted stress limits on the order of ~1 MPa have been cited as injury-related design bounds (schaedler2014designingmetallicmicrolattices pages 1-2). |


*Table: This table summarizes the main quantities obtainable or supportable from high-speed video and DIC for tensegrity drop testing, with formulas, optimization roles, and literature ranges. It is useful for deciding which video-derived measurements should become Ax/BoTorch objectives versus constraints.*

**Discussion of specific metrics:**

- **Peak transmitted force / g_max (min F_peak):** Not directly measurable from video alone; requires synchronization with the accelerometer channel. However, video provides the failure mode and crush state at the instant of F_peak, which is essential for interpreting ringing or multi-peak force traces. For human-body-contact absorbers, the injury criterion sets transmitted stress on the order of ~1 MPa (schaedler2014designingmetallicmicrolattices pages 1-2).

- **Specific energy absorption SEA (max SEA):** The most defensible primary objective for crashworthiness optimization. Multi-objective studies explicitly maximize SEA while minimizing peak force (baykasoglu2020multiobjectivecrashworthinessoptimization pages 13-13, costas2014amultiobjectivesurrogatebased pages 1-2). SEA requires force data from the accelerometer and displacement from video, making it a fused objective. Typical design-space spans are 7–35 J/g for lattice-filled tubes (baykasoglu2020multiobjectivecrashworthinessoptimization pages 13-13).

- **Crush efficiency η (max η):** Defined as U/U_max, where U_max is the ideal constant-stress absorption over the full stroke (schaedler2014designingmetallicmicrolattices pages 1-2, schaedler2014designingmetallicmicrolattices pages 2-3). This is a volumetric efficiency metric. Bustihan et al. report 36–47% for TPU honeycombs across repeated compressions (bustihan2025reusable3dprintedthermoplastic pages 12-14). Because η depends strongly on ε_d, it is naturally supported by video-derived crush displacement.

- **Densification strain ε_d:** Directly measurable from video. Typical values range from ~0.48 for tensegrity-inspired structures (pajunen2019designandimpact pages 4-5) to 0.55–0.72 for foams and polymer lattices (schaedler2014designingmetallicmicrolattices pages 2-3, andrew2021energyabsorptionand pages 13-18). Defensible as a secondary objective to maximize usable stroke.

- **Cycle/reuse count N_reuse:** The most video-native BO metric for this modality. Frame comparison before and after each drop directly measures shape recoverability. Pajunen et al. showed <0.2% residual strain per impact over 24 impacts (pajunen2019designandimpact pages 7-8), while PLA metamaterials survived 5 load-recovery cycles before catastrophic failure (desole2024energyabsorptionof pages 19-21). This is a candidate secondary objective or constraint.

- **Noise floors and repeatability:** DIC displacement random error is typically ~0.1–0.5 pixels (i.e., ~5–17 µm at typical image scales) and strain error ~2 mm/m under well-controlled conditions (vinel2021metrologicalassessmentof pages 23-24, vinel2021metrologicalassessmentof pages 1-2). For dynamic fracture DIC, CoV on derived stress intensity factors reached ~19% (pagano2019dynamicfractureand pages 59-61). Crush-gap tracking from video is more robust than full-field DIC and should have lower CoV (estimated 3–8% for nominally identical specimens) when frame rate and lighting are adequate.

---

## (c) Derived Quantities as Constraints

Several quantities are better formulated as hard cutoffs or chance constraints in the qNEHVI framework:

- **F_peak / g_max (hard upper bound):** For the egg-drop scenario, the egg failure threshold (typically ~25–30 g for a commercial egg, based on packaging literature) sets the constraint g_max ≤ g_threshold. For human-body-contact absorbers, transmitted stress should remain below ~1 MPa (schaedler2014designingmetallicmicrolattices pages 1-2).

- **Densification strain ε_d (lower bound):** A minimum ε_d ensures the absorber has sufficient stroke before bottoming out. For the 200-mm bounding-sphere specimen with 0.5–3 m drop heights, a constraint ε_d ≥ 0.30–0.40 is conservative based on the ~0.48 reported for tensegrity structures (pajunen2019designandimpact pages 4-5).

- **Residual strain per impact (upper bound):** For reusable applications, δ_residual ≤ 5% per drop is a reasonable constraint, given Pajunen's data showing <0.2% per impact for well-designed structures (pajunen2019designandimpact pages 7-8). For the egg-drop demo, a softer constraint (δ_residual ≤ 10%) may suffice since reuse is less critical.

- **Force overshoot O (upper bound):** The ratio of peak to plateau stress. An ideal absorber has O = 1 (cronau2025energyabsorptionof pages 2-4). A practical constraint of O ≤ 1.5–2.0 prevents injurious initial spikes.

- **CLE (lower bound):** Crush load efficiency values above ~0.5 ensure a reasonably flat plateau. Bustihan et al. reported CLE up to 73.5% for optimized TPU honeycombs (bustihan2025reusable3dprintedthermoplastic pages 14-17).

---

## (d) Recommended Characterization Settings

The following table consolidates literature-grounded settings for both tiers (high-end PSC camera and smartphone fallback):

| Parameter | High-End Camera recommendation | Smartphone Fallback recommendation | Justification/Source |
|---|---|---|---|
| Frame rate | **1–5 kfps** for M23 drop events; use **~1 kfps** minimum for whole-event failure-mode confirmation, and **2–5 kfps** if 2D DIC / bar-buckling onset is a priority | **240 fps minimum**, **960 fps preferred if true high-speed mode is available**; use only for kinematics/failure-mode confirmation and coarse crush-gap tracking, not defensible DIC | Tensegrity drop tests were successfully captured at **1000 fps** (Pajunen), while dynamic impact/DIC studies span **~1,000–50,000 fps** for lower-velocity events and much higher for ballistic work; therefore 1–5 kfps is a defensible lab-scale target, with phones as preliminary only (pajunen2019designandimpact pages 4-5, ellis2020visualmethodsto pages 10-12, ellis2020visualmethodsto pages 3-5) |
| Exposure time | **Start at 25–50 µs**, shorten further if blur persists and lighting allows | Use the **shortest shutter the phone app permits in slow-motion mode**; if not user-settable, reject clips with visible blur for measurement use | Low-velocity impact DIC was run at **39,000 fps with 25 µs exposure**; dynamic DIC literature emphasizes minimizing exposure time to suppress motion blur (ramakrishnan2021experimentalassessmentof pages 5-8, ellis2020visualmethodsto pages 3-5) |
| Resolution | Prefer **≥0.5–1 MP ROI** after cropping; retain enough pixels for at least **3–5 px speckles** and **~20–30 px subsets** across the painted face | Use **1080p slow-motion** if available; crop minimally to keep the full specimen face and plate-to-plate gap visible | Dynamic DIC quality is set by the frame-rate/resolution tradeoff; examples include **786×786 at 39 kfps** and ultra-high-speed work using high-resolution cropped ROIs (ramakrishnan2021experimentalassessmentof pages 5-8, xing2017highspeedphotographyand pages 25-27, vinel2021metrologicalassessmentof pages 1-2) |
| Lens / FOV | Macro or short telephoto giving full view of one speckled specimen face plus both platens; target image scale that yields **3–5 px speckles** and **~20–30 px subsets** on structural members; avoid wide-angle distortion | Use the phone’s **main 1× camera**, not ultrawide; place far enough away to reduce perspective distortion while still filling most of frame with specimen and platen gap | Ramakrishnan used macro-zoom optics; Vinel used a **90 mm objective** with calibrated image scale; DIC guidance stresses matching optics/FOV to speckle and subset requirements (ramakrishnan2021experimentalassessmentof pages 5-8, vinel2021metrologicalassessmentof pages 23-24, saralaya2012insitugrainscale pages 44-48) |
| Aperture | Use **moderate stop (about f/4–f/8)** to balance depth of field and light; verify the full front face stays in focus through crush | Fixed by phone hardware; maximize lighting and back off distance slightly if depth-of-field causes edge blur | DIC practice recommends choosing f-stop to secure sufficient DOF without starving the sensor of light (saralaya2012insitugrainscale pages 44-48, reedlunn2013tipsandtricks pages 3-4) |
| Illumination | Use **high-output continuous LED area lights** or equivalent bright uniform lighting; aim for high-contrast matte images without saturation or glare | Very bright diffuse room/auxiliary lighting; avoid flickering LEDs and backlighting; if illumination is inadequate, do not use clip for DIC | Dynamic DIC requires strong, uniform illumination because short exposures otherwise destroy contrast; one impact study used about **15,000 lumens**; glare/noise strongly increase error (ramakrishnan2021experimentalassessmentof pages 5-8, ellis2020visualmethodsto pages 3-5, reedlunn2013tipsandtricks pages 3-4) |
| Speckle pattern size | Matte black-on-white random speckle with characteristic speckles **3–5 pixels** wide on the final image | Same target if attempting any coarse tracking; otherwise add high-contrast fiducial dots/markers instead of full DIC speckle | AM-polymer DIC reviews recommend **3–5 px speckles**; speckle must be random, isotropic, high-contrast, and well adhered (hachimi2026mechanicalcharacterizationand pages 6-8, hachimi2026mechanicalcharacterizationand pages 5-6) |
| DIC subset size | Start with **21–31 px** subset; if the pattern is coarse, move toward **23×23 to 33×33 px** | Not recommended for formal DIC with rolling-shutter smartphone footage; if attempted, use larger virtual extensometers / marker tracking instead | Saralaya reports **~3 px speckles** work well with **13×13** subsets, while **23×23 to 33×33** subsets perform better with larger speckles; dynamic studies commonly use subset scales around a few tens of pixels (saralaya2012insitugrainscale pages 44-48, pagano2019dynamicfractureand pages 45-49, vinel2021metrologicalassessmentof pages 23-24) |
| DIC step size | Start at **~1/2 subset** (e.g., **10–15 px** for 21–31 px subsets); reduce only if SNR remains acceptable | Not recommended for formal DIC; for fallback use plate-gap tracking or sparse marker tracking frame-by-frame | Example dynamic DIC settings used **31 px subset / 15 px step**; smaller step improves map density but increases noise sensitivity (pagano2019dynamicfractureand pages 45-49, hachimi2026mechanicalcharacterizationand pages 6-8) |
| Trigger / pretrigger | Hardware trigger tied to drop event / accelerometer / contact switch with **rolling buffer and pretrigger**; keep enough pre-event frames to capture release, impact onset, and a short post-event settling window | Start recording before release whenever possible; if app supports slow-motion buffering, enable it; otherwise accept that exact impact onset sync will be poor | Impact imaging studies used **FIFO rolling-buffer triggering** to retain pre-impact frames; synchronization is critical for aligning video-derived crush displacement with force/acceleration data (ramakrishnan2021experimentalassessmentof pages 5-8, ellis2020visualmethodsto pages 8-10, ellis2020visualmethodsto pages 22-23) |
| Relevant standards | Follow **ASTM D5276** for free-fall/drop protocol framing; for force/acceleration channel conditioning use **SAE J211 Class 1000** filtering where applicable; follow iDICs-style uncertainty reporting / calibration practice for DIC workflows | Same standards context applies, but smartphone data should be treated as preliminary/non-certification-grade optical evidence | ASTM D5276 is cited in drop-test studies; Schaedler reports **SAE J211 Class 1000** filtering in dynamic impact work; DIC uncertainty/calibration reporting is emphasized in industrial-good-practice literature (schaedler2014designingmetallicmicrolattices pages 6-7, hachimi2026mechanicalcharacterizationand pages 5-6) |


*Table: This table summarizes literature-grounded settings for high-speed video and preliminary smartphone capture of the M23 drop event. It is useful for choosing camera, lighting, speckle, and triggering parameters that keep crush-gap tracking and optional 2D DIC defensible.*

**Key justifications:**

- **Frame rate:** Pajunen et al. used 1000 fps for tensegrity drop-weight impact successfully (pajunen2019designandimpact pages 4-5). For DIC with buckling-onset resolution, 2–5 kfps is recommended, consistent with the PSC camera's capability. Dynamic compression events in lattices occur within 5–10 ms (schaedler2014designingmetallicmicrolattices pages 2-3), so at 2 kfps one captures 10–20 frames during the active crush phase.

- **Exposure time:** Ramakrishnan et al. used 25 µs exposure at 39,000 fps for low-velocity impact DIC (ramakrishnan2021experimentalassessmentof pages 5-8). At the lower frame rates relevant here (1–5 kfps), 25–50 µs exposure is achievable with LED area lights and ensures sub-pixel motion blur per frame.

- **Speckle pattern:** Hachimi et al. recommend speckle sizes of 3–5 pixels to avoid aliasing during large deformations (hachimi2026mechanicalcharacterizationand pages 6-8, hachimi2026mechanicalcharacterizationand pages 5-6). For a ~200-mm specimen face at 1 MP, this corresponds to physical speckle features of ~0.5–1 mm. Use matte black-on-white spray paint with validated adhesion under impact (saralaya2012insitugrainscale pages 44-48).

- **DIC parameters:** Start with 21–31 px subsets and 10–15 px step sizes, consistent with dynamic DIC practice (pagano2019dynamicfractureand pages 45-49, saralaya2012insitugrainscale pages 44-48). Use normalized cross-correlation criteria (ZNSSD) to handle illumination variation (turrisi2016motionblurcompensation pages 26-29).

- **Standards:** Frame the drop protocol per ASTM D5276 for free-fall testing (referenced in multiple drop-test studies). Apply SAE J211 Class 1000 filtering to accelerometer data when syncing with video-derived displacement (schaedler2014designingmetallicmicrolattices pages 6-7). Follow iDICs good-practice guidelines for DIC uncertainty reporting and calibration (hachimi2026mechanicalcharacterizationand pages 5-6).

---

## (e) Integration into the BO Campaign (PR #30 + PR #33)

**Ax Metric / Objective shape:** Video-derived quantities should populate the following Ax metrics:
- `ε_d` → `Metric("densification_strain", lower_is_better=False)` — a maximize objective.
- `δ_residual` → `Metric("residual_strain_pct", lower_is_better=True)` — a minimize objective or constraint.
- `N_reuse` → `Metric("reuse_count", lower_is_better=False)` — if cyclic testing is performed.
- Force-displacement-synced metrics (SEA, η, F_peak) combine video displacement with accelerometer force and are joint observables.

**Observation noise model:** Homoscedastic noise is a reasonable starting point for ε_d and δ_residual (video-resolution-limited noise is approximately constant across designs), with estimated standard deviation ~0.01–0.02 strain for ε_d and ~0.5–1% for δ_residual. For DIC-derived full-field strain metrics, heteroscedastic noise may be necessary because DIC precision degrades with deformation magnitude and pattern quality (ellis2020visualmethodsto pages 3-5, turrisi2016motionblurcompensation pages 26-29).

**Per-trial cost / wall-clock budget:** Each M23 drop + high-speed capture + post-processing requires approximately 15–30 minutes wall clock (specimen mounting, camera setup/focus check, drop, data download, DIC processing). DIC processing adds ~5–15 minutes per specimen depending on ROI size and software. Phone captures reduce setup time (~5 minutes) but sacrifice metric quality.

**Fidelity tier:** In the multifidelity ladder, high-speed video operates at two sub-tiers:
- **Phone slow-motion (240–960 fps):** Lowest optical fidelity, suitable only for qualitative failure-mode classification and coarse crush-gap tracking. Maps to the MuJoCo regime-C fidelity level as a quick-look validation.
- **PSC high-speed camera (1–5 kfps, global shutter):** Mid-fidelity optical measurement. Provides defensible ε_d, δ_residual, and optional DIC strain. Complements the accelerometer (which gives F(t) and g_max) and the LDV (which gives point velocity with much higher bandwidth). Together, video + accelerometer constitute the primary experimental data tier, above MuJoCo simulation but below the full PolyFEM+IPC high-fidelity sim.

**Complementarity with other data sources:** Video uniquely provides spatial failure-mode classification (which member failed how), full-field strain if DIC is applied, and direct shape-recovery measurement. The accelerometer provides force/acceleration with much higher temporal bandwidth (100+ kHz). The LDV provides point velocity/displacement at very high precision. The shaker/gas-gun provide controlled excitation for characterizing frequency-domain properties. Video's primary role is to supply the displacement axis δ(t) that, when fused with accelerometer F(t), yields the force-displacement curve from which SEA, η, and F_peak are computed.

---

## (f) Top Gotchas, Failure Modes, and Cross-Talk Artifacts

The following ranked list identifies the most critical artifacts that would silently corrupt BO objectives if ignored:

| Rank | Gotcha/Artifact | Mechanism | Impact on BO Objective | Mitigation |
|---|---|---|---|---|
| 1 | Smartphone rolling shutter | Line-by-line readout shears fast-moving platens/specimen edges, so apparent crush gap and local strain fields are time-skewed within a single frame | Biases densification strain, crush displacement, buckling-onset timing, and reuse/frame-comparison metrics; can create false asymmetry that BO may reward or punish incorrectly (ellis2020visualmethodsto pages 3-5, xing2017highspeedphotographyand pages 24-25) | Do not use phones for formal DIC; restrict phone footage to preliminary failure-mode confirmation only; use global-shutter high-speed camera for any BO metric ingestion |
| 2 | Motion blur from insufficient exposure control | Long exposure integrates motion over the frame, smearing speckles/edges and reducing subpixel correlation fidelity | Inflates displacement/strain noise, shifts apparent contact onset, and corrupts `ε_d`, residual strain, and bar-buckling localization; can also flatten detected peak displacement rate (ellis2020visualmethodsto pages 3-5, ramakrishnan2021experimentalassessmentof pages 5-8, turrisi2016motionblurcompensation pages 26-29) | Use shortest feasible exposure with strong lighting; reject blurred runs from DIC; verify blur on raw frames before analysis |
| 3 | Speckle pattern adhesion failure / delamination | Paint or applied speckle debonds, stretches independently, or flakes during large deformation/impact | Produces fictitious strain localization, false fracture maps, and unreliable recovery scoring; BO may select geometries that merely preserve paint better rather than structure better (ellis2020visualmethodsto pages 3-5, reedlunn2013tipsandtricks pages 3-4, saralaya2012insitugrainscale pages 44-48) | Use well-adhered matte patterns validated under impact; inspect post-test surface; mask damaged-pattern regions from DIC; prefer robust speckling methods for dynamic loading |
| 4 | Insufficient frame rate / temporal aliasing | Event is under-sampled, so contact onset, peak crush velocity, and short-lived failure transitions occur between frames | Underestimates peak crush rate, misplaces `ε_d`, misses tendon snap/joint pull-out sequence, and weakens sync to force–displacement curves; BO sees over-smoothed responses (xing2017highspeedphotographyand pages 25-27, ellis2020visualmethodsto pages 22-23, pajunen2019designandimpact pages 4-5) | Choose frame rate from event duration; for M23 drop use at least ~1 kfps for whole-event kinematics and 2–5 kfps when DIC/buckling timing matters; confirm enough frames span first contact to rebound |
| 5 | Poor illumination reducing effective bit depth / raising DIC noise floor | Low light forces high gain and low contrast; glare or sensor limitations collapse usable grayscale dynamic range | Raises displacement/strain uncertainty and degrades repeatability of `ε_d`, strain hotspots, and frame-comparison reuse metrics; may make nominally identical specimens look different (ellis2020visualmethodsto pages 3-5, saralaya2012insitugrainscale pages 44-48) | Use bright diffuse lighting, avoid glare, keep histogram off saturation, and maintain full grayscale contrast; use monochrome camera when possible |
| 6 | Out-of-plane motion causing virtual strain in 2D DIC | 2D DIC assumes planar motion; face rotation, bowing, or platen-induced tilt is interpreted as in-plane deformation | Creates false strain bands and wrong buckling onset, especially in tensegrity faces that rotate during crush; can corrupt any BO objective tied to full-field strain or mode classification (reedlunn2013tipsandtricks pages 3-4, xing2017highspeedphotographyand pages 24-25, pajunen2019designandimpact pages 5-7) | Keep analysis to near-planar face regions, use telephoto-like geometry to minimize perspective, or move to stereo/3D DIC if out-of-plane motion is significant |
| 7 | Trigger synchronization error between camera and accelerometer | Video and force/acceleration clocks are offset or drift relative to one another; pretrigger may be inadequate | Mis-registers force peak against crush displacement, making SEA, force-overshoot, and `F_peak` vs `x` curves wrong even when each sensor is internally correct (ramakrishnan2021experimentalassessmentof pages 5-8, ellis2020visualmethodsto pages 8-10, ellis2020visualmethodsto pages 22-23) | Use shared hardware trigger and pretrigger buffer; sync on a visible/measurable event (first contact); store timestamps and estimate sync uncertainty per run |
| 8 | Lens distortion and parallax in uncalibrated setups | Wide-angle optics, oblique views, and uncorrected distortion warp distances non-uniformly across the field | Biases crush-gap calibration, local strain gradients, and residual-shape comparison; BO may prefer specimens tested near field center or with favorable placement rather than better mechanics (vinel2021metrologicalassessmentof pages 23-24, reedlunn2013tipsandtricks pages 3-4, saralaya2012insitugrainscale pages 44-48) | Calibrate camera/lens, avoid ultrawide views, keep optical axis normal to the measured face, and use a scale/calibration target in the same plane as the specimen face |
| 9 | Camera-induced vibration / standoff vibration coupling | Tripod, stand, mirror, or lighting rig vibrates from impact or floor shock and moves relative to the specimen | Adds common-mode apparent displacement, contaminating crush displacement, DIC strain, and reuse/frame-difference metrics; especially dangerous if rig motion looks like specimen rebound (ellis2020visualmethodsto pages 8-10, saralaya2012insitugrainscale pages 44-48) | Isolate camera from machine/floor shocks, use rigid support away from impact frame, include static background fiducials to detect camera motion, and discard runs with background drift |
| 10 | Lossy image compression destroying speckle contrast | Codec quantization, temporal smoothing, sharpening, and phone post-processing alter speckle texture frame-to-frame | Degrades correlation quality, increases bias/variance, and can silently poison DIC-derived objectives while still looking visually acceptable to humans (reedlunn2013tipsandtricks pages 3-4, turrisi2016motionblurcompensation pages 26-29, hachimi2026mechanicalcharacterizationand pages 6-8) | Record raw or least-compressed grayscale imagery when possible; avoid consumer video enhancement modes; if compression is unavoidable, use footage only for qualitative failure-mode review, not BO metrics |


*Table: This table ranks the main optical and synchronization artifacts that can silently corrupt high-speed video and DIC measurements during M23 drop testing. It is useful for deciding which clips are safe to use for BO objectives and what mitigations are required before trusting video-derived metrics.*

---

## (g) References

1. Pajunen, K., Johanns, P., Pal, R. K., Rimoli, J. J., and Daraio, C. "Design and impact response of 3D-printable tensegrity-inspired structures." *Materials & Design*, 182:107966, 2019. doi:10.1016/j.matdes.2019.107966 (pajunen2019designandimpact pages 4-5, pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8).

2. Schaedler, T. A., Ro, C. J., Sorensen, A. E., Eckel, Z., Yang, S. S., Carter, W. B., and Jacobsen, A. J. "Designing metallic microlattices for energy absorber applications." *Advanced Engineering Materials*, 16:276–283, 2014. doi:10.1002/adem.201300206 (schaedler2014designingmetallicmicrolattices pages 1-2, schaedler2014designingmetallicmicrolattices pages 2-3, schaedler2014designingmetallicmicrolattices pages 6-7).

3. Ellis, C. L. and Hazell, P. "Visual methods to assess strain fields in armour materials subjected to dynamic deformation—a review." *Applied Sciences*, 10:2644, 2020. doi:10.3390/app10082644 (ellis2020visualmethodsto pages 3-5, ellis2020visualmethodsto pages 8-10, ellis2020visualmethodsto pages 22-23, ellis2020visualmethodsto pages 10-12).

4. Vinel, A., Seghir, R., Berthe, J., Portemont, G., and Réthoré, J. "Metrological assessment of multi-sensor camera technology for spatially-resolved ultra-high-speed imaging of transient high strain-rate deformation processes." *Strain*, 57(4), 2021. doi:10.1111/str.12381 (vinel2021metrologicalassessmentof pages 23-24, vinel2021metrologicalassessmentof pages 1-2, vinel2021metrologicalassessmentof pages 18-23).

5. Ramakrishnan, K. R., Corn, S., Le Moigne, N., Ienny, P., and Slangen, P. "Experimental assessment of low velocity impact damage in flax fabrics reinforced biocomposites by coupled high-speed imaging and DIC analysis." *Composites Part A*, 140:106137, 2021. doi:10.1016/j.compositesa.2020.106137 (ramakrishnan2021experimentalassessmentof pages 5-8).

6. Xing, H. Z., Zhang, Q. B., Braithwaite, C. H., Pan, B., and Zhao, J. "High-speed photography and digital optical measurement techniques for geomaterials: fundamentals and applications." *Rock Mechanics and Rock Engineering*, 50:1611–1659, 2017. doi:10.1007/s00603-016-1164-0 (xing2017highspeedphotographyand pages 25-27, xing2017highspeedphotographyand pages 24-25).

7. Cronau, J. and Engstler, F. "Energy absorption of 3D printed stochastic lattice structures under impact loading—design parameters, manufacturing, and testing." *Progress in Additive Manufacturing*, 10:3145–3156, 2025. doi:10.1007/s40964-025-01094-5 (cronau2025energyabsorptionof pages 2-4).

8. Andrew, J. J., Alhashmi, H., Schiffer, A., Kumar, S., and Deshpande, V. S. "Energy absorption and self-sensing performance of 3D printed CF/PEEK cellular composites." *Materials & Design*, 208:109863, 2021. doi:10.1016/j.matdes.2021.109863 (andrew2021energyabsorptionand pages 10-13, andrew2021energyabsorptionand pages 13-18).

9. Hachimi, T., Zekriti, N., Hmazi, F. A., Bagar, H., Assad, H. E., and Naboulsi, N. "Mechanical characterization and crack propagation in additively manufactured polymers using digital image correlation: a review." *Fracture and Structural Integrity*, 20(77):173–206, 2026. doi:10.3221/igf-esis.77.11 (hachimi2026mechanicalcharacterizationand pages 6-8, hachimi2026mechanicalcharacterizationand pages 5-6).

10. Bustihan, A., Hirian, R., and Botiz, I. "Reusable 3D-printed thermoplastic polyurethane honeycombs for mechanical energy absorption." *Polymers*, 17:3035, 2025. doi:10.3390/polym17223035 (bustihan2025reusable3dprintedthermoplastic pages 7-9, bustihan2025reusable3dprintedthermoplastic pages 2-4, bustihan2025reusable3dprintedthermoplastic pages 12-14, bustihan2025reusable3dprintedthermoplastic pages 14-17, bustihan2025reusable3dprintedthermoplastic pages 5-7).

11. Baykasoğlu, A., Baykasoğlu, C., and Cetin, E. "Multi-objective crashworthiness optimization of lattice structure filled thin-walled tubes." *Thin-Walled Structures*, 149:106630, 2020. doi:10.1016/j.tws.2020.106630 (baykasoglu2020multiobjectivecrashworthinessoptimization pages 13-13).

12. Costas, M., Díaz, J., Romera, L., and Hernández, S. "A multi-objective surrogate-based optimization of the crashworthiness of a hybrid impact absorber." *International Journal of Mechanical Sciences*, 88:46–54, 2014. doi:10.1016/j.ijmecsci.2014.07.002 (costas2014amultiobjectivesurrogatebased pages 1-2).

13. Reedlunn, B., Daly, S., Hector, L., Zavattieri, P., and Shaw, J. A. "Tips and tricks for characterizing shape memory wire part 5: full-field strain measurement by digital image correlation." *Experimental Techniques*, 37:62–78, 2013. doi:10.1111/j.1747-1567.2011.00717.x (reedlunn2013tipsandtricks pages 3-4).

14. Desole, M. P., Gisario, A., and Barletta, M. "Energy absorption of PLA-based metamaterials manufactured by material extrusion: dynamic loads and shape recovery." *International Journal of Advanced Manufacturing Technology*, 132:1697–1722, 2024. doi:10.1007/s00170-024-13430-0 (desole2024energyabsorptionof pages 19-21).

15. Zhang, A. S. "Design of Impact-Resistant Tensegrity Landers." Thesis, 2022. (zhang2022designofimpactresistant pages 33-37, zhang2022designofimpactresistant pages 40-44).

16. ASTM D5276, "Standard Test Method for Drop Test of Loaded Containers by Free Fall." ASTM International.

17. SAE J211, "Instrumentation for Impact Test." SAE International.

18. International Digital Image Correlation Society (iDICs), "A Good Practices Guide for Digital Image Correlation." Referenced in Jr., C. B. "Introduction to Digital Image Correlation (DIC) with annotated bibliography." OSTI Technical Report, 2025. doi:10.2172/3008384.

19. Turrisi, S. "Motion blur compensation to improve the accuracy of Digital Image Correlation measurements." Thesis, 2016. (turrisi2016motionblurcompensation pages 26-29).

20. Saralaya, R. N. "In-situ grain scale strain measurements using digital image correlation." PhD Thesis, Drexel University, 2012. doi:10.17918/etd-4125 (saralaya2012insitugrainscale pages 44-48).

References

1. (xing2017highspeedphotographyand pages 24-25): H. Z. Xing, Q. B. Zhang, C. H. Braithwaite, B. Pan, and J. Zhao. High-speed photography and digital optical measurement techniques for geomaterials: fundamentals and applications. Rock Mechanics and Rock Engineering, 50:1611-1659, Feb 2017. URL: https://doi.org/10.1007/s00603-016-1164-0, doi:10.1007/s00603-016-1164-0. This article has 202 citations and is from a domain leading peer-reviewed journal.

2. (schaedler2014designingmetallicmicrolattices pages 1-2): Tobias A. Schaedler, Christopher J. Ro, Adam E. Sorensen, Zak Eckel, Sophia S. Yang, William B. Carter, and Alan J. Jacobsen. Designing metallic microlattices for energy absorber applications. Advanced Engineering Materials, 16:276-283, Mar 2014. URL: https://doi.org/10.1002/adem.201300206, doi:10.1002/adem.201300206. This article has 303 citations and is from a peer-reviewed journal.

3. (schaedler2014designingmetallicmicrolattices pages 6-7): Tobias A. Schaedler, Christopher J. Ro, Adam E. Sorensen, Zak Eckel, Sophia S. Yang, William B. Carter, and Alan J. Jacobsen. Designing metallic microlattices for energy absorber applications. Advanced Engineering Materials, 16:276-283, Mar 2014. URL: https://doi.org/10.1002/adem.201300206, doi:10.1002/adem.201300206. This article has 303 citations and is from a peer-reviewed journal.

4. (vinel2021metrologicalassessmentof pages 23-24): Adrien Vinel, Rian Seghir, Julien Berthe, Gérald Portemont, and Julien Réthoré. Metrological assessment of multi‐sensor camera technology for spatially‐resolved ultra‐high‐speed imaging of transient high strain‐rate deformation processes. Strain, May 2021. URL: https://doi.org/10.1111/str.12381, doi:10.1111/str.12381. This article has 13 citations and is from a peer-reviewed journal.

5. (costas2014amultiobjectivesurrogatebased pages 1-2): M. Costas, J. Díaz, L. Romera, and S. Hernández. A multi-objective surrogate-based optimization of the crashworthiness of a hybrid impact absorber. International Journal of Mechanical Sciences, 88:46-54, Nov 2014. URL: https://doi.org/10.1016/j.ijmecsci.2014.07.002, doi:10.1016/j.ijmecsci.2014.07.002. This article has 94 citations and is from a peer-reviewed journal.

6. (pajunen2019designandimpact pages 5-7): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

7. (pajunen2019designandimpact pages 7-8): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

8. (zhang2022designofimpactresistant pages 33-37): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

9. (andrew2021energyabsorptionand pages 10-13): J. Jefferson Andrew, Hasan Alhashmi, Andreas Schiffer, S. Kumar, and Vikram S. Deshpande. Energy absorption and self-sensing performance of 3d printed cf/peek cellular composites. Materials & Design, 208:109863, Oct 2021. URL: https://doi.org/10.1016/j.matdes.2021.109863, doi:10.1016/j.matdes.2021.109863. This article has 151 citations and is from a highest quality peer-reviewed journal.

10. (schaedler2014designingmetallicmicrolattices pages 2-3): Tobias A. Schaedler, Christopher J. Ro, Adam E. Sorensen, Zak Eckel, Sophia S. Yang, William B. Carter, and Alan J. Jacobsen. Designing metallic microlattices for energy absorber applications. Advanced Engineering Materials, 16:276-283, Mar 2014. URL: https://doi.org/10.1002/adem.201300206, doi:10.1002/adem.201300206. This article has 303 citations and is from a peer-reviewed journal.

11. (pajunen2019designandimpact pages 4-5): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

12. (andrew2021energyabsorptionand pages 13-18): J. Jefferson Andrew, Hasan Alhashmi, Andreas Schiffer, S. Kumar, and Vikram S. Deshpande. Energy absorption and self-sensing performance of 3d printed cf/peek cellular composites. Materials & Design, 208:109863, Oct 2021. URL: https://doi.org/10.1016/j.matdes.2021.109863, doi:10.1016/j.matdes.2021.109863. This article has 151 citations and is from a highest quality peer-reviewed journal.

13. (cronau2025energyabsorptionof pages 2-4): J. Cronau and F. Engstler. Energy absorption of 3d printed stochastic lattice structures under impact loading – design parameters, manufacturing, and testing. Progress in Additive Manufacturing, 10:3145-3156, Apr 2025. URL: https://doi.org/10.1007/s40964-025-01094-5, doi:10.1007/s40964-025-01094-5. This article has 16 citations and is from a peer-reviewed journal.

14. (baykasoglu2020multiobjectivecrashworthinessoptimization pages 13-13): Adil Baykasoğlu, Cengiz Baykasoğlu, and Erhan Cetin. Multi-objective crashworthiness optimization of lattice structure filled thin-walled tubes. Thin-Walled Structures, 149:106630, Apr 2020. URL: https://doi.org/10.1016/j.tws.2020.106630, doi:10.1016/j.tws.2020.106630. This article has 148 citations and is from a domain leading peer-reviewed journal.

15. (bustihan2025reusable3dprintedthermoplastic pages 12-14): Alin Bustihan, Razvan Hirian, and Ioan Botiz. Reusable 3d-printed thermoplastic polyurethane honeycombs for mechanical energy absorption. Polymers, 17:3035, Nov 2025. URL: https://doi.org/10.3390/polym17223035, doi:10.3390/polym17223035. This article has 3 citations.

16. (bustihan2025reusable3dprintedthermoplastic pages 14-17): Alin Bustihan, Razvan Hirian, and Ioan Botiz. Reusable 3d-printed thermoplastic polyurethane honeycombs for mechanical energy absorption. Polymers, 17:3035, Nov 2025. URL: https://doi.org/10.3390/polym17223035, doi:10.3390/polym17223035. This article has 3 citations.

17. (bustihan2025reusable3dprintedthermoplastic pages 5-7): Alin Bustihan, Razvan Hirian, and Ioan Botiz. Reusable 3d-printed thermoplastic polyurethane honeycombs for mechanical energy absorption. Polymers, 17:3035, Nov 2025. URL: https://doi.org/10.3390/polym17223035, doi:10.3390/polym17223035. This article has 3 citations.

18. (bustihan2025reusable3dprintedthermoplastic pages 7-9): Alin Bustihan, Razvan Hirian, and Ioan Botiz. Reusable 3d-printed thermoplastic polyurethane honeycombs for mechanical energy absorption. Polymers, 17:3035, Nov 2025. URL: https://doi.org/10.3390/polym17223035, doi:10.3390/polym17223035. This article has 3 citations.

19. (desole2024energyabsorptionof pages 19-21): Maria Pia Desole, Annamaria Gisario, and Massimiliano Barletta. Energy absorption of pla-based metamaterials manufactured by material extrusion: dynamic loads and shape recovery. The International Journal of Advanced Manufacturing Technology, 132:1697-1722, Mar 2024. URL: https://doi.org/10.1007/s00170-024-13430-0, doi:10.1007/s00170-024-13430-0. This article has 22 citations.

20. (vinel2021metrologicalassessmentof pages 1-2): Adrien Vinel, Rian Seghir, Julien Berthe, Gérald Portemont, and Julien Réthoré. Metrological assessment of multi‐sensor camera technology for spatially‐resolved ultra‐high‐speed imaging of transient high strain‐rate deformation processes. Strain, May 2021. URL: https://doi.org/10.1111/str.12381, doi:10.1111/str.12381. This article has 13 citations and is from a peer-reviewed journal.

21. (pagano2019dynamicfractureand pages 59-61): Dynamic Fracture and Fragmentation Investigations of Brittle Polymers and Composites

22. (ellis2020visualmethodsto pages 10-12): Chris L. Ellis and Paul Hazell. Visual methods to assess strain fields in armour materials subjected to dynamic deformation—a review. Applied Sciences, 10:2644, Apr 2020. URL: https://doi.org/10.3390/app10082644, doi:10.3390/app10082644. This article has 14 citations.

23. (ellis2020visualmethodsto pages 3-5): Chris L. Ellis and Paul Hazell. Visual methods to assess strain fields in armour materials subjected to dynamic deformation—a review. Applied Sciences, 10:2644, Apr 2020. URL: https://doi.org/10.3390/app10082644, doi:10.3390/app10082644. This article has 14 citations.

24. (ramakrishnan2021experimentalassessmentof pages 5-8): Karthik Ram Ramakrishnan, Stéphane Corn, Nicolas Le Moigne, Patrick Ienny, and Pierre Slangen. Experimental assessment of low velocity impact damage in flax fabrics reinforced biocomposites by coupled high-speed imaging and dic analysis. Composites Part A: Applied Science and Manufacturing, 140:106137, Jan 2021. URL: https://doi.org/10.1016/j.compositesa.2020.106137, doi:10.1016/j.compositesa.2020.106137. This article has 53 citations and is from a domain leading peer-reviewed journal.

25. (xing2017highspeedphotographyand pages 25-27): H. Z. Xing, Q. B. Zhang, C. H. Braithwaite, B. Pan, and J. Zhao. High-speed photography and digital optical measurement techniques for geomaterials: fundamentals and applications. Rock Mechanics and Rock Engineering, 50:1611-1659, Feb 2017. URL: https://doi.org/10.1007/s00603-016-1164-0, doi:10.1007/s00603-016-1164-0. This article has 202 citations and is from a domain leading peer-reviewed journal.

26. (saralaya2012insitugrainscale pages 44-48): In-situ Grain Scale Strain Measurements using Digital Image Correlation

27. (reedlunn2013tipsandtricks pages 3-4): B. Reedlunn, Samantha Daly, L. Hector, P. Zavattieri, and John A. Shaw. Tips and tricks for characterizing shape memory wire part 5: full-field strain measurement by digital image correlation. Experimental Techniques, 37:62-78, May 2013. URL: https://doi.org/10.1111/j.1747-1567.2011.00717.x, doi:10.1111/j.1747-1567.2011.00717.x. This article has 95 citations and is from a peer-reviewed journal.

28. (hachimi2026mechanicalcharacterizationand pages 6-8): Taoufik Hachimi, Najat Zekriti, Fouad Ait Hmazi, Hamza Bagar, Hatim El Assad, and Nassima Naboulsi. Mechanical characterization and crack propagation in additively manufactured polymers using digital image correlation: a review. Fracture and Structural Integrity, 20:173-206, Apr 2026. URL: https://doi.org/10.3221/igf-esis.77.11, doi:10.3221/igf-esis.77.11. This article has 0 citations.

29. (hachimi2026mechanicalcharacterizationand pages 5-6): Taoufik Hachimi, Najat Zekriti, Fouad Ait Hmazi, Hamza Bagar, Hatim El Assad, and Nassima Naboulsi. Mechanical characterization and crack propagation in additively manufactured polymers using digital image correlation: a review. Fracture and Structural Integrity, 20:173-206, Apr 2026. URL: https://doi.org/10.3221/igf-esis.77.11, doi:10.3221/igf-esis.77.11. This article has 0 citations.

30. (pagano2019dynamicfractureand pages 45-49): Dynamic Fracture and Fragmentation Investigations of Brittle Polymers and Composites

31. (ellis2020visualmethodsto pages 8-10): Chris L. Ellis and Paul Hazell. Visual methods to assess strain fields in armour materials subjected to dynamic deformation—a review. Applied Sciences, 10:2644, Apr 2020. URL: https://doi.org/10.3390/app10082644, doi:10.3390/app10082644. This article has 14 citations.

32. (ellis2020visualmethodsto pages 22-23): Chris L. Ellis and Paul Hazell. Visual methods to assess strain fields in armour materials subjected to dynamic deformation—a review. Applied Sciences, 10:2644, Apr 2020. URL: https://doi.org/10.3390/app10082644, doi:10.3390/app10082644. This article has 14 citations.

33. (turrisi2016motionblurcompensation pages 26-29): S Turrisi. Motion blur compensation to improve the accuracy of digital image correlation measurements. Unknown journal, 2016.

34. (vinel2021metrologicalassessmentof pages 18-23): Adrien Vinel, Rian Seghir, Julien Berthe, Gérald Portemont, and Julien Réthoré. Metrological assessment of multi‐sensor camera technology for spatially‐resolved ultra‐high‐speed imaging of transient high strain‐rate deformation processes. Strain, May 2021. URL: https://doi.org/10.1111/str.12381, doi:10.1111/str.12381. This article has 13 citations and is from a peer-reviewed journal.

35. (bustihan2025reusable3dprintedthermoplastic pages 2-4): Alin Bustihan, Razvan Hirian, and Ioan Botiz. Reusable 3d-printed thermoplastic polyurethane honeycombs for mechanical energy absorption. Polymers, 17:3035, Nov 2025. URL: https://doi.org/10.3390/polym17223035, doi:10.3390/polym17223035. This article has 3 citations.

36. (zhang2022designofimpactresistant pages 40-44): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.