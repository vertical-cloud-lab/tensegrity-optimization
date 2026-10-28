Question: 
We are running our first instrumented crush / drop tests on small (~50 mm
edge) multi-material 3D-printed tensegrity unit cells (PLA or PETG struts,
TPU 85A tendons; ~10-50 g per cell) on a benchtop drop tower with an
electromagnetic-hoist release.

Setup (also see attached `docs/drop-test-protocol.md`):
 - Drop tower with rigid steel base plate; magnet-release hoist.
 - Accelerometer #1 mounted on the steel base plate (input shock).
 - Accelerometer #2 mounted on a small acrylic "top plate" that sits on
   the specimen (transmitted shock). Manuals are the Vishay/PCB
   TP4 Quick Start (W20000-98-15) and TP4 User's Guide (W20000-98-14).
 - A "cage" of two 1/4"-thick acrylic plates separated by four ~18 in
   threaded steel rods (cut + threaded in-house) is meant to keep the
   top plate captive over the specimen.
 - Slow-motion video on a phone (high-speed camera from PSC available
   as an upgrade).

Observed failure modes from the first instrumented drop:
 1. Specimen / bottom acrylic plate separation during descent: the
    tensegrity cell lifts off the lower plate before impact, so it is
    no longer aligned under the top plate.
 2. Cage tilt: the rod-to-hole clearance lets the top plate tilt ~25 deg
    off horizontal, biasing the transmitted-acceleration measurement and
    risking off-axis loading of the accelerometer.
 3. Slow-mo framing starts after hoist release, so the initial descent
    is out of frame.
 4. Data is only being saved for the initial ~200 ms shock window; we
    actually want the full ~10 s ringdown.

Quantities of interest the drop tower must feed into our Bayesian
optimization stack (see companion `edison-trajectories/objective-functions/`
work):
 - Peak transmitted g_max on the top plate (minimize)
 - Specific energy absorption (SEA) inferred from drop height,
   specimen mass, and input-vs-transmitted impulse difference
 - Full ~10 s ringdown waveform (secondary modes, damping)
 - Reusability / number of drops to failure N_reuse
 - Slow-mo or high-speed displacement field of the deforming struts

Please produce a HIGH-EFFORT literature synthesis aimed specifically at
*troubleshooting and de-risking this benchtop drop-tower workflow for
small 3D-printed lattice / tensegrity specimens*. Cite peer-reviewed and
standards literature throughout. Use the section skeleton below; keep
each subsection self-contained so the lab team can read just the part
they need.

(a) **Best-practice benchtop drop-tower workflows** for sub-100 g 3D-printed
    cellular / lattice / tensegrity specimens:
    - ASTM / ISO standards that apply or have to be adapted (e.g.
      ASTM D5276 free-fall package drop, ASTM D7136 instrumented drop-weight,
      ISO 6603 puncture, ISO 1683 reference levels, ASTM D3332 cushioning
      cushion-curve, MIL-STD-810 method 516, ASTM E1820 if fracture).
      For each: what it covers, what has to be adapted for our small
      tensegrity samples, and the key reported metrics.
    - Recommended impact velocities, drop heights, repeat counts, and
      Bruceton-style sensitivity protocols seen in the literature for
      similar specimen mass / size.
    - Conditioning (humidity, temperature, anneal) for PLA + PETG + TPU
      85A specimens before mechanical test.

(b) **Specimen-retention fixtures**. Survey published fixturing that
    addresses our failure mode #1 (specimen lift-off before impact) and
    failure mode #2 (off-axis tilt) for cellular and tensegrity samples.
    Specifically discuss:
    - Linear bushings vs. plain holes on guide rods: what tolerance
      class / clearance is typical, what tilt angle that implies for a
      cage of our geometry, and recommended sleeve bearing classes
      (e.g. IGUS DryLin J / R; LM linear bushings).
    - Light retention clips, magnets, or elastic preload that hold the
      top plate seated on the specimen until impact without significantly
      pre-loading the specimen.
    - Methods of bonding / mechanically anchoring the specimen to the
      bottom plate without changing its compliance (double-sided
      transfer tape, register pins through tensegrity nodes, V-block
      cradles, vacuum chuck).
    - Vertex-mounted accelerometer schemes (sensor bonded to one
      tensegrity node) and how they manage cable strain relief and
      survivability under repeated drops.

(c) **Instrumentation and signal acquisition** specific to small,
    lightly damped lattice samples:
    - Sensor selection: ADXL375 / Endevco / PCB 350-series ranges and
      bandwidths suitable for ~kHz shock; required full-scale (e.g.
      +-200 g vs +-500 g) given expected g_max for our specimen mass.
    - Mounting: adhesive vs stud vs wax, and the resonance shift /
      mass-loading bias each introduces on a thin acrylic top plate.
    - Sample rate (>= 10x the highest frequency of interest) and
      anti-alias filtering recommendations from ISO 5347 / SAE J211.
    - **Long-window capture** (the ~10 s ringdown): trigger / pre-trigger
      settings, ring-buffer length, and how groups have separated the
      initial shock from the slow decay in published drop-tower work.
    - Synchronizing slow-mo (or high-speed) video with the accelerometer
      stream (photogate / LED-flash / TTL / SMPTE).

(d) **High-speed and phone-slow-mo imaging** of cellular impact:
    - Minimum frame rate / shutter / lighting recommended for ~1-3 m/s
      impact on a 50 mm specimen.
    - DIC (digital image correlation) on tensegrity / lattice impact:
      speckle prep on PLA/PETG, software (Ncorr, GOM, DICe), reported
      strain-rate / displacement uncertainty.
    - When a modern phone's slow-mo (240-960 fps) is and isn't adequate
      relative to a checked-out high-speed camera (Photron / Phantom).

(e) **Data reduction and uncertainty** for the BO objective stack:
    - How to convert raw a(t) -> g_max, SEA, cushion-curve, and
      attenuation transfer function in published drop-tower studies.
    - Reproducibility / specimen-to-specimen scatter reported for FFF
      lattice impact -> sets the experimental noise floor BO has to see.
    - Typical confidence-interval reporting (n, std, IQR) for these
      metrics.

(f) **Common gotchas** specifically called out in the drop-tower
    literature for cellular / lattice / tensegrity specimens:
    - Plate-bounce contamination of g_max (our failure mode that the
      cage is meant to solve).
    - Strain-rate effects in TPU 85A tendons at impact rates vs the
      quasi-static rate where E ~ 12 MPa is measured.
    - Anisotropy from FFF layer orientation under impact.
    - Frame ringing / fixture resonance polluting the high-frequency
      tail of a(t).
    - Magnet-release jerk / residual hoist swing.

(g) **Closely related published drop-tower datasets** on 3D-printed
    lattices / tensegrity / cellular impact that we should benchmark
    against (Zhang 2018, Davami 2025, Intrigila 2022, Pajunen 2019,
    Khatri-Egan 2024, Anand 2022, and any others you find). For each:
    specimen geometry, material, instrumentation, drop heights, reported
    g_max / SEA / N_reuse, and how their fixture handled the
    specimen-retention problem.

For every recommendation in (a)-(g), please cite peer-reviewed papers,
standards, or manufacturer documentation -- no uncited claims. Where
quantitative values are given (g, fps, kHz, MPa, mm, deg), include the
source and the original measurement context.

Output: a single self-contained markdown report we can drop into
`edison-trajectories/drop-test/` alongside this PR's
`docs/drop-test-protocol.md`.


# Drop-Tower Workflow for Small 3D-Printed Tensegrity / Lattice Specimens: Literature Synthesis & Troubleshooting Guide

*Companion document for `edison-trajectories/drop-test/`. Revision 1.0.*

---

## (a) Best-Practice Benchtop Drop-Tower Workflows

### Applicable Standards and Necessary Adaptations

**ASTM D7136 / D7136M** ("Measuring the Damage Resistance of a Fiber-Reinforced Polymer Matrix Composite to a Drop-Weight Impact Event") is the most frequently cited standard for instrumented drop-weight impact on small planar specimens. Al Rifaie et al. (2019) built an in-house drop tester conforming to ASTM D7136 for 50 × 50 × 20 mm ABS lattice blocks (rifaie2019dropweightimpactbehavior pages 1-2). Wickeler (2022) followed ASTM D7136 / D7766 for origami-core impact testing with a hemispherical 16 mm impactor at 1.1 kg, measuring peak force beneath the sample with a Dytran 1060v load sensor (wickeler2022origamiinspiredmechanicalmetamaterials pages 111-115). **Adaptation for tensegrity cells:** The standard prescribes a hemispherical tup and rectangular clamped plate; for a 50 mm unit cell that sits freely on a base plate, the clamping ring must be replaced with a captive cage or guided flat platen. The key reported metric is peak force vs. impact energy.

**ASTM D3763** ("Standard Test Method for High Speed Puncture Properties of Plastics Using Load and Displacement Sensors") was used by Kabir et al. (2021) for drop-weight impact on 60 × 60 × 3 mm continuous-fiber-reinforced cellular composites on an Instron CEAST 9350 (kabir2021impactresistanceand pages 3-4). This standard specifies a pneumatic clamp and instrumented tup; adaptation to a tensegrity cell requires replacing the puncture tup with a flat platen.

**ASTM D3332** ("Standard Test Methods for Mechanical-Shock Fragility of Products, Using Shock Machines") provides the cushion-curve methodology. The procedure drops a known mass onto a cushion specimen from a known height and records the peak transmitted acceleration (G_max) as a function of static stress (σ_st = W/A). This produces the characteristic concave valley-shaped cushion curve (gao2018researchonproperties pages 31-37). For tensegrity cells, the "cushion" is the unit cell and the mass is the top plate + accelerometer assembly. Each (drop height, cell-design) combination produces one point on the curve.

**ASTM D1621 / ISO 13314:2011** are referenced for quasi-static compression of rigid cellular plastics and porous metals, respectively (habib2024developmentofhigh pages 53-59). These establish plateau stress, densification strain, and volumetric energy absorption (VEA) which are compared with dynamic values.

**ASTM D638-14 / D695-15** are the baseline tensile and compressive property standards for material characterization of the strut (PLA/PETG) and tendon (TPU) materials (habib2024developmentofhigh pages 53-59, sun2025experimentalstudyon pages 4-6, bhandari2019enhancingtheinterlayer pages 11-14). Print coupons in x, y, and z orientations per Wickeler (2022) to capture FFF anisotropy (wickeler2022origamiinspiredmechanicalmetamaterials pages 34-38).

**MIL-STD-810 Method 516** (Shock) prescribes mechanical-shock profiles for equipment qualification. It defines half-sine, sawtooth, and trapezoidal pulses at specified peak g-levels and durations. For benchtop-scale tensegrity cells, Method 516 Procedure I free-fall shock from specified heights provides a templated approach (anas2024comprehensivemethodologyfor pages 4-5). Adaptation: the standard targets ruggedized electronics; for compliant lattice specimens, ensure the programmed pulse duration (1–20 ms typical) is compatible with the specimen's natural period.

### Recommended Impact Velocities, Drop Heights, and Repeat Counts

Published lattice-impact studies use velocities from ~1 m/s to 5 m/s corresponding to drop heights of ~5 cm to ~125 cm (dwyer2023impactperformanceof pages 5-7, cronau2025energyabsorptionof pages 2-4). Dwyer et al. (2023) stepped heights in 5 cm increments up to 20 cm, then 10 cm increments to 60 cm, generating impact energies from 2.6 J to 31.2 J with a 4.8 kg flat impactor (dwyer2023impactperformanceof pages 5-7). Cronau & Engstler (2025) tested at 5 m/s, equivalent to bicycle-helmet test speeds (cronau2025energyabsorptionof pages 2-4). For your ~10–50 g cells with a lightweight top plate, target 0.5–3 m/s (drop heights 1–50 cm) to stay below densification. Pajunen et al. (2019) applied 24 repeated impacts per sample and demonstrated <0.2% permanent strain per impact, supporting a protocol of ≥20 drops per specimen to characterize N_reuse (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8). For cushion-curve generation per ASTM D3332, five impacts per condition with 2-minute intervals is standard (gao2018researchonproperties pages 99-105).

### Conditioning for PLA, PETG, and TPU 85A

Sun et al. (2025) conditioned FFF specimens (including PLA, PETG, and TPU) at 15%, 45%, and 95% relative humidity (RH) for at least 24 h in a programmable environmental chamber, monitoring mass change to equilibrium (sun2025experimentalstudyon pages 6-8, sun2025experimentalstudyon pages 4-6). The water-uptake ranking was Nylon > PETG > PLA ≈ ABS > TPU ≈ PEEK (sun2025experimentalstudyon pages 4-6). Filaments were pre-dried in a PrintDry Filament Dryer PRO 3 before printing (sun2025experimentalstudyon pages 4-6). For mechanical testing, ASTM D570 was applied for moisture uptake assessment (sun2025experimentalstudyon pages 4-6). Bhandari et al. (2019) annealed PETG and PLA specimens at 120 °C (above PETG T_g ≈ 80.7 °C) for 0–480 min and observed significant interlayer tensile strength improvement; PLA was also annealed at 90 °C (bhandari2019enhancingtheinterlayer pages 11-14). **Recommendation:** Condition all specimens at 23 ± 2 °C, 50 ± 5% RH for ≥40 h per ASTM D618 (standard conditioning). Pre-dry filaments. Consider annealing PLA/PETG struts at 90–120 °C for 30–240 min to stabilize crystallinity if long-term property consistency is required (bhandari2019enhancingtheinterlayer pages 11-14).

---

## (b) Specimen-Retention Fixtures

### Linear Bushings vs. Plain Holes on Guide Rods

Your current design uses four 1/4"-thick acrylic plates separated by threaded rods with through-holes, producing ~25° of tilt. Rajput et al. (2018) used adjustable sliders on guide rails with minimized play-vs-friction trade-off, and a composite crosshead that separates from the impactor at contact so vibrations from the tower are not transmitted to the load cell (rajput2018designandevaluation pages 5-7). Anas et al. (2024) recommend "guide rails, alignment pins, and adjustable supports" for precise alignment (anas2024comprehensivemethodologyfor pages 5-7). For your geometry (two plates ~18 in apart on four 1/4"-20 rods), replacing the plain drilled holes with recirculating ball linear bushings (e.g., IGUS DryLin R or LM6UU class for 6 mm shafts) would reduce clearance from ~0.5–1 mm radial (producing arctan(1/457) ≈ 0.13° per rod, but cumulative 4-rod slop can reach tens of degrees) to <0.05 mm radial play. With 457 mm rod spacing and <0.05 mm clearance per bushing, the maximum theoretical tilt drops below 0.01°. **Recommendation:** Replace acrylic plain holes with self-aligning polymer sleeve bearings (IGUS JUM-01-06 or equivalent) or recirculating steel ball bushings on hardened, ground shafts. Upgrade from threaded rod to ground precision rod (h6 tolerance, ≤6 µm roundness).

### Light Retention of the Top Plate on the Specimen

To prevent specimen lift-off (your failure mode #1) without pre-loading the cell, several approaches appear in the literature. Pajunen et al. (2019) applied a thin acetone layer between the specimen base and a glass sheet to reduce friction and ensure contact (pajunen2019designandimpact pages 4-5). Wickeler (2022) placed a 6.35 mm polycarbonate sheet atop the sample to distribute load and protect the sensor below (wickeler2022origamiinspiredmechanicalmetamaterials pages 111-115). **Practical options:** (i) Rare-earth disc magnets (≤0.5 N pull force each) embedded in the top plate corners that attract thin steel shims bonded to the specimen top nodes—this provides ~1–2 N total hold-down, far below the specimen's buckling load; (ii) thin elastic bands (orthodontic rubber bands, ~50 gf each) looped from the cage rods over the top plate; (iii) a light vacuum chuck (e.g., porous sintered metal plate connected to a hand vacuum pump) under the specimen, generating 0.1–0.5 N hold-down over a 50 × 50 mm area.

### Anchoring the Specimen to the Bottom Plate

Anas et al. (2024) prescribe custom fixtures tailored to complex geometries using "support pads, restraint bars, modular components" (anas2024comprehensivemethodologyfor pages 5-7). For tensegrity nodes, consider: (i) double-sided transfer tape (3M VHB 4910 or equivalent, ~1 mm thick, compliant enough not to stiffen the cell base); (ii) register pins through the base-plate that engage socket features printed into the tensegrity bottom nodes; (iii) a V-block cradle 3D-printed to match the cell's bottom face geometry. Avoid rigid adhesives (cyanoacrylate) that create stiff boundary conditions inconsistent with the designed compliance.

### Vertex-Mounted Accelerometer Schemes

The Zhang (2022) tensegrity lander embedded dual accelerometers (ADXL377 ± 200 g and H3LIS331DL ± 400 g) inside the payload housing at 1000 Hz, with cable strain relief managed by routing wires along tensile cables (zhang2022designofimpactresistant pages 44-49). Pajunen et al. (2019) mounted a 1.0 g triaxial ICP accelerometer directly on the striker with a counterweight opposite to balance mass distribution (pajunen2019designandimpact pages 4-5). For a vertex-mounted scheme on a 3.75 g specimen, the sensor mass must be ≤10% of the effective node mass to avoid mass-loading bias. Use a MEMS accelerometer (ADXL375, 0.16 g, ± 200 g) bonded with cyanoacrylate or dental wax to a flat printed pad at one node. Route the ribbon cable along a tendon to the base plate with a service loop to absorb deformation.

---

## (c) Instrumentation and Signal Acquisition

### Sensor Selection

For ~10–50 g specimens impacting at 1–3 m/s, expected peak g on the top plate may range from ~50 g to >500 g depending on cell stiffness. The Zhang (2022) tensegrity landers recorded 116–392 g at 5–20 m drops (zhang2022designofimpactresistant pages 49-52). Burgin & Aspden (2007) used a piezoelectric force transducer and accelerometer with data digitized at 50,000 samples/s for controlled biological tissue impacts (burgin2007adroptower pages 1-2). For your setup: a PCB 350-series IEP accelerometer (± 500 g, ~10 kHz bandwidth) for the base plate, and an ADXL375 MEMS (± 200 g, 1600 Hz bandwidth) or Endevco 7264 (± 500 g, built-in mechanical filter, ~10 kHz usable bandwidth) for the top plate. Chu (1988) noted that usable bandwidth should be limited to <1/5 of the sensor's seismic resonance to maintain linearity (chu1988problemsinhighshock pages 1-4).

### Mounting: Adhesive vs. Stud vs. Wax

Krelle (2011) documents that direct stud mounting (0.25" or 10-32 thread) with silicon grease provides the best high-frequency transmission, while added mechanical filters increase mass and affect dynamic response (krelle2011dropcalibrationof pages 16-20). For a thin acrylic top plate, threaded stud mounting may not be practical. Petro-wax mounting is adequate to ~5 kHz and can be appropriate for your ~1 kHz shock content on the top plate. Adhesive mounting (cyanoacrylate) provides good coupling to ~10 kHz but is semi-permanent. The key concern is mass loading: a 5 g accelerometer on a 20 g acrylic plate adds 25% mass, shifting the plate's effective natural frequency. Use the lightest sensor possible (ADXL375 at 0.16 g adds <1% mass).

### Sample Rate and Anti-Alias Filtering

SAE J211 specifies Channel Frequency Classes (CFC) with the most common for occupant protection being CFC 1000 (3 dB at 1650 Hz) and CFC 600 (3 dB at 1000 Hz), using 4-pole Butterworth low-pass filters (chu1988problemsinhighshock pages 4-5, chu1988problemsinhighshock pages 1-4). The sampling rate must be ≥10× the anti-alias filter corner; for CFC 1000 this means ≥16.5 kHz minimum. Dwyer et al. (2023) sampled at 200 kHz (dwyer2023impactperformanceof pages 5-7). Rajput et al. (2018) used an NI 9234 cDAQ at ~51.2 kHz with a 5th-order Butterworth at 5 kHz (rajput2018designandevaluation pages 5-7). **Recommendation:** Sample at ≥50 kHz with a hardware anti-alias filter at ~10 kHz; apply SAE J211 CFC 1000 digital filtering in post-processing.

### Long-Window Capture (10 s Ringdown)

Your current 200 ms window captures only the primary shock pulse. Rajput et al. (2018) implemented a DAQ UI with configurable pre-trigger (% of scan points), number of samples, and internal/external TTL triggering (rajput2018designandevaluation pages 13-18, rajput2018designandevaluation pages 18-24). At 50 kHz, a 10 s window requires 500,000 samples—well within modern DAQ ring-buffer capability (e.g., NI cDAQ supports continuous acquisition). **Recommendation:** Configure the DAQ for continuous ring-buffer acquisition with a trigger threshold on the base-plate accelerometer (e.g., >5 g); set 10% pre-trigger and 10 s post-trigger window. This captures the initial shock and full ringdown for modal/damping analysis.

### Synchronizing Video with Accelerometer Stream

Pajunen et al. (2019) time-synchronized a PHANTOM camera and oscilloscope using "a switch triggered at mass release" (pajunen2019designandimpact pages 4-5). A common approach is a TTL pulse from the DAQ trigger output routed to both the camera's external trigger input and an LED visible in the camera field of view. Alternatively, a photogate at the release point generates a simultaneous trigger for both systems.

---

## (d) High-Speed and Phone Slow-Mo Imaging

### Minimum Frame Rate, Shutter, and Lighting

For impacts at 1–3 m/s on a 50 mm specimen, the impact event lasts ~5–50 ms (dwyer2023impactperformanceof pages 5-7). To resolve the deformation with ≥20 frames during impact, a minimum of 1000 fps is needed for a 20 ms event. Pajunen et al. (2019) used 1000 fps with a PHANTOM camera (pajunen2019designandimpact pages 4-5). Dwyer et al. (2023) used 10,000 fps with an Olympus i-Speed 3 (dwyer2023impactperformanceof pages 5-7). Sharafisafa & Shen (2020) used a Photron FASTCAM SA5 at 100,000 fps for SHPB impact DIC (sharafisafa2020experimentalinvestigationof pages 3-5). Ellis & Hazell (2020) note that modern high-speed cameras achieve hundreds of thousands of fps, with LED illumination preferred to avoid thermal distortion from halogen sources (ellis2020visualmethodsto pages 3-5). **Recommendation:** Use ≥5000 fps with a shutter speed of ≤50 µs and continuous LED panel illumination for DIC-quality imaging of 1–3 m/s impacts.

### DIC on Tensegrity / Lattice Impact

Hachimi et al. (2026) recommend speckle sizes of ~3–5 pixels and either airbrushing or inkjet printing for textured AM surfaces; software options include open-source Ncorr, DICe, SUN-DIC, and commercial GOM/ARAMIS and Vic-2D/3D (hachimi2026mechanicalcharacterizationand pages 6-8). Yang et al. (2021) demonstrated 3D-printer-deposited speckle patterns achieving displacement accuracy of ~10⁻² pixels and strain accuracy of ~10⁻⁴ (yang2021smartdigitalimage pages 1-2). Quino et al. (2021) developed rapid-application speckle techniques using temporary tattoo paper and stamp kits that survive impact loads and large deformations (quino2021specklepatternsfor pages 11-11). For PLA/PETG struts: apply a white base coat, then spray fine black speckles (0.1–0.3 mm diameter) using an airbrush at ~20 cm standoff. Ellis & Hazell (2020) report random displacement errors on the order of 1/100 pixel for in-plane DIC (ellis2020visualmethodsto pages 3-5).

### When Phone Slow-Mo Is and Isn't Adequate

Modern phones offer 240–960 fps slow motion. At 960 fps with a 50 mm specimen impacting at 2 m/s, the specimen moves ~2 mm/frame—marginally adequate for qualitative deformation tracking but insufficient for DIC (which needs ≥10 pixels of motion per frame at sub-pixel accuracy). Phone cameras also lack global shutters (rolling shutter distorts fast motion) and have limited resolution at high fps (typically 720p at 960 fps). **Phone slow-mo is adequate** for: verifying that the specimen stays seated, checking for tilt, and qualitative mode-shape identification. **It is not adequate** for: quantitative DIC, measuring impact velocity to <5% accuracy, or resolving sub-millisecond events. Upgrade to a dedicated high-speed camera (Photron FASTCAM Mini or Phantom Miro) for any quantitative displacement field measurement.

---

## (e) Data Reduction and Uncertainty for the BO Objective Stack

### Raw a(t) → g_max, SEA, Cushion Curve, Transfer Function

**g_max:** The peak transmitted acceleration is extracted directly from the filtered top-plate accelerometer trace as max|a(t)|. Per ASTM D3332 / cushion-curve methodology, G_max is plotted against static stress (σ_st = W/A_specimen) for each drop height to produce the cushion curve (gao2018researchonproperties pages 31-37).

**SEA:** Al Rifaie et al. (2019) computed absorbed energy from the change in kinetic energy of the impactor before and after impact using accelerometer-derived velocity integration (rifaie2019dropweightimpactbehavior pages 1-2). Cronau & Engstler (2025) defined VEA as the area under the stress–strain curve up to densification strain ε_d, then SEA = VEA / ρ_s, where ρ_s is measured specimen density (cronau2025energyabsorptionof pages 2-4). Dwyer et al. (2023) combined load-cell force data with video-derived displacement to compute absorbed energy as the area under the force–displacement curve (dwyer2023impactperformanceof pages 5-7).

**Attenuation transfer function:** Compute T(f) = FFT[a_top(t)] / FFT[a_base(t)] to obtain the frequency-dependent transmissibility. The initial shock and 10 s ringdown provide sufficient spectral resolution (~0.1 Hz bins) for modal identification.

### Reproducibility and Scatter

Specimen-to-specimen variability in FFF lattice impact is a recognized challenge. Snapp et al. (2024) note that "unavoidable processing-dependent defects and specimen-to-specimen variability" are primary obstacles in predicting energy-absorbing efficiency from computational models alone, motivating their >25,000-experiment SDL campaign (snapp2024superlativemechanicalenergy pages 1-2). Pajunen et al. (2019) tested four samples at each condition and found absorbed momentum values within 1% between equivalent-momentum tests (100 g at 2.1 m/s vs. 200 g at 1.05 m/s), suggesting that test-fixture variability is small relative to specimen variability (pajunen2019designandimpact pages 7-8). Cronau & Engstler (2025) used Design of Experiments (DoE) with statistical analysis at the 95% significance level (cronau2025energyabsorptionof pages 2-4). **Recommendation:** Test n ≥ 5 specimens per condition; report mean, standard deviation, and coefficient of variation. For BO, the experimental noise floor is approximately the inter-specimen CV (expect 5–15% for FFF lattices based on the scatter acknowledged in multiple studies).

---

## (f) Common Gotchas

### Plate-Bounce Contamination of g_max

Abou-Ali et al. (2025) explicitly observed projectile bounce (velocity crossing below zero indicates elastic rebound) in drop-weight tests on lattice sandwich panels and noted that small projectile diameter relative to cell size can mask architectural effects (abouali2025impactdamagebehavior pages 13-19). Your cage design exists to prevent this, but with 25° tilt and specimen lift-off, the current cage is counterproductive. With proper linear bushings (Section b), the captive top plate eliminates rebound separation. Additionally, Wickeler (2022) used a polycarbonate distribution plate atop the specimen to ensure full-face contact and sensor protection (wickeler2022origamiinspiredmechanicalmetamaterials pages 111-115).

### Strain-Rate Effects in TPU 85A Tendons

TPU exhibits pronounced strain-rate dependence: it behaves in a rubbery manner at quasi-static rates (~10⁻³ to 10² s⁻¹) but transitions toward leathery or glassy response at high strain rates (~10³ s⁻¹) (yi2006largedeformationratedependent pages 1-2). Yi et al. (2006) showed that the storage-modulus glass transition shifts approximately linearly with strain rate, and SHPB tests at ~1612 s⁻¹ demonstrated significant stiffening relative to quasi-static behavior (yi2006largedeformationratedependent pages 6-6, yi2006largedeformationratedependent pages 9-10). Chen et al. (2020) confirmed that a model calibrated from quasi-static and DMA data can predict high-rate response, noting pronounced increases in flow stress magnitude (chen2020applicationoflinear pages 1-2). At your benchtop impact rates (~100–500 s⁻¹ estimated for 1–3 m/s on a 50 mm cell), the TPU 85A tendons will be measurably stiffer than quasi-static tensile data suggest (E_qs ~ 12 MPa). **Expect a factor of 2–5× increase in effective modulus at impact rates** based on the viscoelastic shift documented in polyurethane literature (yi2006largedeformationratedependent pages 6-6, yi2006largedeformationratedependent pages 1-2).

### FFF Layer-Orientation Anisotropy Under Impact

Wickeler (2022) printed tensile specimens in x, y, and z orientations to capture directional (orthotropic) material properties and modeled rigid PLA as orthotropic elastic in FEA (wickeler2022origamiinspiredmechanicalmetamaterials pages 34-38, wickeler2022origamiinspiredmechanicalmetamaterials pages 111-115). Kabir et al. (2021) identified build/shell orientation and raster angle as "primary determinants of impact properties that influence crack length and path" (kabir2021impactresistanceand pages 3-4). Alemayehu & Todoh (2024) printed PLA lattices flat in the X–Y plane; this orients layer lines normal to the Z (impact) axis, creating potential weak interlayer bonds in the loading direction (alemayehu2024enhancedenergyabsorption pages 4-6). **Recommendation:** Print struts with raster orientation aligned to the strut axis where possible. Report print orientation in all test documentation.

### Frame Ringing / Fixture Resonance

Rajput et al. (2018) performed experimental modal analysis of their drop-weight rig and found crosshead modes at 2–12 kHz, support table first mode at 6.4 kHz, and impactor strong peak at ~11 kHz; they applied a 5th-order Butterworth low-pass at 5 kHz to "avoid loss of significant impact content" while removing fixture-excited modes (rajput2018designandevaluation pages 5-7). Chu (1988) emphasizes that undamped accelerometer resonances (typically >130 kHz for piezoelectric sensors) can be excited by high-frequency transients, producing zero-shift and spurious signals; limiting usable bandwidth to <1/5 of resonance frequency is recommended (chu1988problemsinhighshock pages 1-4). **Recommendation:** Perform a tap-test modal analysis of your acrylic cage assembly. Filter accelerometer data below the first fixture mode (likely 2–5 kHz for your acrylic/threaded-rod cage).

### Magnet-Release Jerk / Residual Hoist Swing

Electromagnetic release provides precise timing but can impart a small transverse impulse or rotational jerk at the instant of demagnetization. Rajput et al. (2018) demagnetize an electromagnet controlled by the DAQ system; the crosshead separates from the impactor at contact so dynamic vibrations are not transmitted (rajput2018designandevaluation pages 5-7). Anas et al. (2024) note that the control system "orchestrates the activation of … electromagnetic release systems" and that velocity and acceleration profiles can be regulated (anas2024comprehensivemethodologyfor pages 4-5). **Recommendation:** Ensure the magnet releases cleanly with no residual magnetism (use an AC demagnetization pulse or a permanent-magnet shunt). Verify vertical alignment of the hoist release with a plumb bob or laser level. The pre-trigger window in the DAQ captures any release transient for post-hoc inspection.

---

## (g) Published Drop-Tower Benchmarks

The following table summarizes the most relevant published datasets for benchmarking your benchtop tensegrity/lattice drop-tower workflow:

| Reference | Specimen Geometry | Material/Process | Instrumentation | Drop Heights/Velocities | Key Metrics (g_max/SEA/N_reuse) | Fixture/Retention Notes |
|---|---|---|---|---|---|---|
| Pajunen et al. 2019 | Tensegrity-inspired spherically jointed unit; height 48.3 mm; relative density ~2.5%; specimen mass 3.75 g | PA2200 polyamide; SLS; also compared with earlier printable geometries | 100 g and 200 g steel strikers; triaxial ceramic shear ICP accelerometer on striker; quartz force sensor under glass support; PHANTOM camera at 1000 fps | Velocity set by drop height; repeated impacts with 200 g striker; additional 100 g at 2.1 m/s comparison | 24 impacts total; remaining strain <0.2% per impact and 2.28% average after 24 impacts; strong hysteretic dissipation and load-limiting plateau; no explicit g_max reported in excerpt (pajunen2019designandimpact pages 4-5, pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 2-3) | Low-friction vertical guide rod through specimen/striker center; specimen on glass sheet over force sensor; thin acetone layer used to reduce interface friction (pajunen2019designandimpact pages 4-5) |
| Al Rifaie et al. 2019 | 50 × 50 × 20 mm lattice blocks; 5 mm cubic unit cells; 1 mm truss diameter; BCC/BCCV/BCCA/BCCG variants | ABS; FDM/uPrint | In-house ASTM D7136 drop tester; accelerometer attached to impactor; acceleration post-processed to force, velocity, displacement, transferred energy | Low-velocity drop-weight impacts; exact heights/velocities not given in excerpt | Absorbed energy from change in impactor kinetic energy; compares lattice topologies; no explicit g_max or N_reuse in excerpt (rifaie2019dropweightimpactbehavior pages 1-2) | Fixture/retention details not reported in excerpt; standard cited as ASTM D7136 (rifaie2019dropweightimpactbehavior pages 1-2) |
| Dwyer et al. 2023 | 50 × 50 × 25 mm spatially varying elastomeric lattices | TPU via Ultimaker FFF and SIL30 elastomer via vat photopolymerization/Carbon | 4.8 kg flat impactor; dynamic load cell; Olympus i-Speed 3 high-speed camera at 10,000 fps; 200 kHz sampling | 5–60 cm drop heights in 5 cm increments to 20 cm then 10 cm; example 5 cm gives 2.6 J and 1.04 m/s | Energy absorbed from force–displacement curve; specific impact energy used; no explicit g_max or N_reuse in excerpt (dwyer2023impactperformanceof pages 5-7) | Custom free-fall rig with flat impactor; fixture/retention scheme not detailed in excerpt (dwyer2023impactperformanceof pages 5-7) |
| Cronau & Engstler 2025 | Stochastic Voronoi lattices | PA12; SLS | Self-built drop rig; Kistler force transducer; B&J accelerometer; Kistler 5011 charge amplifiers; transient recorder | 5 m/s impact speed | SEA computed from area under stress–strain curve to densification divided by measured density; DoE/statistical analysis at 95% significance; no explicit g_max or N_reuse in excerpt (cronau2025energyabsorptionof pages 2-4) | Fixture details not given in excerpt; focus is on force/stress reduction and statistical design space mapping (cronau2025energyabsorptionof pages 2-4) |
| Zhang 2022 | Six-bar tensegrity landers; examples include 22 in class robot with rod length 47 cm, cable length 27 cm | Carbon-fiber rods, springs/cables, TPU endcaps/payload shell; assembled tensegrity robots | ADXL377 and H3LIS331DL accelerometers at 1000 Hz; force plate up to 10 kHz; video verification | Drops from 1–20 m in controlled tests and up to 122 m by drone; also 183 m helicopter and >305 m fixed-wing deployment discussed | Peak payload acceleration examples for 22 in robot: 116 g at 5 m, 155 g at 10 m, 235 g at 20 m; unprotected payload 121 g at 1 m and 392 g at 5 m; operational life improved to ~20 drops before spring replacement (zhang2022designofimpactresistant pages 49-52, zhang2022designofimpactresistant pages 40-44, zhang2022designofimpactresistant pages 52-58, zhang2022designofimpactresistant pages 44-49) | Orientation-sensitive impact; force plate and onboard sensors used; no benchtop captive top-plate fixture—free-drop lander configuration instead (zhang2022designofimpactresistant pages 44-49, zhang2022designofimpactresistant pages 33-37) |
| Wickeler 2022 | Origami-inspired cores; example 75 × 75 mm; impact specimens tested between plates | FDM PLA / flexible PLA; MakerBot/FFF | ASTM D7136/D7766-style drop test; 1.1 kg hemispherical impactor (16 mm); Dytran 1060v load sensor | 1.06 m drop in one study variant; another excerpt reports 67 cm with 1.104 kg striker | Maximum impact force measured; no explicit g_max, SEA, or N_reuse in excerpt (wickeler2022origamiinspiredmechanicalmetamaterials pages 111-115, wickeler2022origamiinspiredmechanicalmetamaterials pages 34-38) | Sensor protected by metal plate; 6.35 mm polycarbonate sheet placed atop sample to distribute load; samples sandwiched between plates, which may influence bounce/coupling (wickeler2022origamiinspiredmechanicalmetamaterials pages 111-115, wickeler2022origamiinspiredmechanicalmetamaterials pages 34-38) |
| Snapp et al. 2024 | Generalized cylindrical shells; specimens ~19.5 mm tall, 27.9 mm wide, 0.5 mm wall thickness | Additively manufactured polymers by FFF; seven polymers explored in SDL campaign | Automated self-driving lab; >25,000 physical experiments with Bayesian optimization-guided selection | Large automated campaign over broad design space rather than a single reported benchtop drop matrix in excerpt | Best reported energy-absorbing efficiency 75.2%; dataset intended to quantify variability, though excerpt does not report explicit CV/noise floor or g_max/N_reuse (snapp2024superlativemechanicalenergy pages 8-8, snapp2024superlativemechanicalenergy pages 1-2) | High-throughput experimental workflow; fixture specifics for individual tests not given in excerpt; useful as BO benchmark for experimental-scale data generation (snapp2024superlativemechanicalenergy pages 8-8, snapp2024superlativemechanicalenergy pages 1-2) |


*Table: This table summarizes the main published drop-tower and related impact datasets most relevant to benchmarking small 3D-printed lattice and tensegrity specimens. It highlights specimen scale, materials, instrumentation, loading conditions, reported metrics, and the limited but important fixture details available from the cited sources.*

### Key Comparisons for Your Setup

**Pajunen et al. (2019)** is the closest published analogue to your experiment: SLS-printed tensegrity-inspired unit cells (48.3 mm tall, 3.75 g, ~2.5% relative density) tested on a guided drop tower with a 200 g striker, ICP accelerometer, quartz force sensor, and PHANTOM camera at 1000 fps. They demonstrated 24 repeated impacts with <0.2% permanent strain per impact and strong hysteretic energy dissipation (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8). Their low-friction guide rod through the specimen center, combined with a glass base-plate and acetone friction reduction, is a lightweight fixture approach suitable for sub-10 g specimens (pajunen2019designandimpact pages 4-5).

**Zhang (2022)** provides large-scale tensegrity drop data (22" robots, ~1 kg total mass, drops from 1–122 m) with ADXL377 and H3LIS331DL accelerometers at 1000 Hz. Peak payload accelerations of 116–235 g were measured for 5–20 m drops. The operational life was ~20 drops before requiring spring replacement (zhang2022designofimpactresistant pages 49-52, zhang2022designofimpactresistant pages 52-58). This dataset is valuable for validating scaling laws between your 50 mm cells and larger tensegrity systems.

**Dwyer et al. (2023)** tested TPU and SIL30 elastomeric lattices (50 × 50 × 25 mm) very similar to your specimen size, with a 4.8 kg impactor, 200 kHz force-cell sampling, and 10,000 fps imaging. Their stepped-height protocol (5–60 cm) is directly transferable to your setup (dwyer2023impactperformanceof pages 5-7).

**Snapp et al. (2024)** is the most relevant BO-in-the-loop benchmark, having performed >25,000 automated compression experiments on FFF polymer structures with Bayesian optimization, demonstrating that process-dependent scatter is the primary noise source and that an 11-dimensional parameter space can be efficiently explored with the SDL approach (snapp2024superlativemechanicalenergy pages 8-8, snapp2024superlativemechanicalenergy pages 1-2). Their open dataset provides empirical noise-floor estimates for FFF mechanical testing.

---

## Summary of Actionable Recommendations

1. **Replace plain acrylic holes with linear sleeve bearings** on hardened ground rods to eliminate the 25° tilt (Section b).
2. **Add light magnetic or elastic hold-down** to the top plate to prevent specimen lift-off during descent (Section b).
3. **Extend the DAQ capture window to 10 s** using ring-buffer mode with pre-trigger, capturing the full ringdown (Section c).
4. **Start video recording before hoist release** using a TTL-synchronized trigger to the camera's external input (Section c).
5. **Apply SAE J211 CFC 1000 filtering** in post-processing and characterize fixture modal frequencies via tap test (Section c, f).
6. **Condition specimens at 23 °C / 50% RH for ≥40 h**; pre-dry filaments; consider annealing PLA/PETG struts at 90–120 °C (Section a).
7. **Account for TPU strain-rate stiffening** (2–5× modulus increase at impact rates) when comparing drop-test SEA to quasi-static predictions (Section f).
8. **Test n ≥ 5 specimens per condition** and report CV to establish the noise floor for Bayesian optimization (Section e).
9. **Upgrade to ≥5000 fps dedicated high-speed camera** for any quantitative DIC work; reserve phone slow-mo for qualitative checks only (Section d).
10. **Benchmark against Pajunen 2019 and Dwyer 2023** as the closest published analogues to your specimen scale and test configuration (Section g).


References

1. (rifaie2019dropweightimpactbehavior pages 1-2): M. Al Rifaie, A. Mian, P. Katiyar, P. Majumdar, and R. Srinivasan. Drop-weight impact behavior of three-dimensional printed polymer lattice structures with spatially distributed vertical struts. Journal of Dynamic Behavior of Materials, pages 1-9, Jun 2019. URL: https://doi.org/10.1007/s40870-019-00199-7, doi:10.1007/s40870-019-00199-7. This article has 28 citations and is from a peer-reviewed journal.

2. (wickeler2022origamiinspiredmechanicalmetamaterials pages 111-115): A Wickeler. Origami-inspired mechanical metamaterials. Unknown journal, 2022.

3. (kabir2021impactresistanceand pages 3-4): S M Fijul Kabir, Kavita Mathur, and Abdel-Fattah M. Seyam. Impact resistance and failure mechanism of 3d printed continuous fiber-reinforced cellular composites. The Journal of The Textile Institute, 112:752-766, Jun 2021. URL: https://doi.org/10.1080/00405000.2020.1778223, doi:10.1080/00405000.2020.1778223. This article has 84 citations.

4. (gao2018researchonproperties pages 31-37): Y Gao. Research on properties and design methods of cushion packaging materials for consumer electronics. Unknown journal, 2018.

5. (habib2024developmentofhigh pages 53-59): Fatah Nasih Habib. Development of high performing 3d printed polymeric cellular structures for wearable impact protection. Text, Jan 2024. URL: https://doi.org/10.25916/sut.26281492, doi:10.25916/sut.26281492. This article has 2 citations and is from a peer-reviewed journal.

6. (sun2025experimentalstudyon pages 4-6): Qian Sun, Xiaojun Tan, Jianhao Man, Shuai Li, Zeeshan Ali, Kaiyang Yin, Bo Cao, and Christoph Eberl. Experimental study on the effect of humidity on the mechanical properties of 3d-printed mechanical metamaterials. Polymers, 17:2938, Nov 2025. URL: https://doi.org/10.3390/polym17212938, doi:10.3390/polym17212938. This article has 2 citations.

7. (bhandari2019enhancingtheinterlayer pages 11-14): Sunil Bhandari, Roberto A. Lopez-Anido, and Douglas J. Gardner. Enhancing the interlayer tensile strength of 3d printed short carbon fiber reinforced petg and pla composites via annealing. Dec 2019. URL: https://doi.org/10.1016/j.addma.2019.100922, doi:10.1016/j.addma.2019.100922. This article has 473 citations and is from a highest quality peer-reviewed journal.

8. (wickeler2022origamiinspiredmechanicalmetamaterials pages 34-38): A Wickeler. Origami-inspired mechanical metamaterials. Unknown journal, 2022.

9. (anas2024comprehensivemethodologyfor pages 4-5): S. M. Anas, Mohd Shariq, Mehtab Alam, Zamira Masharipova, and Boxodir Azizov. Comprehensive methodology for low-velocity drop weight impact testing of structural slabs: instruments, procedures, and analysis. E3S Web of Conferences, 563:02032, Jan 2024. URL: https://doi.org/10.1051/e3sconf/202456302032, doi:10.1051/e3sconf/202456302032. This article has 4 citations and is from a peer-reviewed journal.

10. (dwyer2023impactperformanceof pages 5-7): Charles Dwyer, J. Carrillo, J. D. L. De la Peña, Carolyn Carradero Santiago, E. MacDonald, Jerry Rhinehart, Reed M. Williams, Mark Burhop, B. Yelamanchi, and P. Cortes. Impact performance of 3d printed spatially varying elastomeric lattices. Dataset, Apr 2023. URL: https://doi.org/10.17632/9t3rzckcnj, doi:10.17632/9t3rzckcnj. This article has 23 citations.

11. (cronau2025energyabsorptionof pages 2-4): J. Cronau and F. Engstler. Energy absorption of 3d printed stochastic lattice structures under impact loading – design parameters, manufacturing, and testing. Progress in Additive Manufacturing, 10:3145-3156, Apr 2025. URL: https://doi.org/10.1007/s40964-025-01094-5, doi:10.1007/s40964-025-01094-5. This article has 16 citations and is from a peer-reviewed journal.

12. (pajunen2019designandimpact pages 5-7): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

13. (pajunen2019designandimpact pages 7-8): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

14. (gao2018researchonproperties pages 99-105): Y Gao. Research on properties and design methods of cushion packaging materials for consumer electronics. Unknown journal, 2018.

15. (sun2025experimentalstudyon pages 6-8): Qian Sun, Xiaojun Tan, Jianhao Man, Shuai Li, Zeeshan Ali, Kaiyang Yin, Bo Cao, and Christoph Eberl. Experimental study on the effect of humidity on the mechanical properties of 3d-printed mechanical metamaterials. Polymers, 17:2938, Nov 2025. URL: https://doi.org/10.3390/polym17212938, doi:10.3390/polym17212938. This article has 2 citations.

16. (rajput2018designandevaluation pages 5-7): Moeen S. Rajput, Magnus Burman, Antonio Segalini, and Stefan Hallström. Design and evaluation of a novel instrumented drop-weight rig for controlled impact testing of polymer composites. Polymer Testing, 68:446-455, Jul 2018. URL: https://doi.org/10.1016/j.polymertesting.2018.04.022, doi:10.1016/j.polymertesting.2018.04.022. This article has 23 citations and is from a peer-reviewed journal.

17. (anas2024comprehensivemethodologyfor pages 5-7): S. M. Anas, Mohd Shariq, Mehtab Alam, Zamira Masharipova, and Boxodir Azizov. Comprehensive methodology for low-velocity drop weight impact testing of structural slabs: instruments, procedures, and analysis. E3S Web of Conferences, 563:02032, Jan 2024. URL: https://doi.org/10.1051/e3sconf/202456302032, doi:10.1051/e3sconf/202456302032. This article has 4 citations and is from a peer-reviewed journal.

18. (pajunen2019designandimpact pages 4-5): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

19. (zhang2022designofimpactresistant pages 44-49): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

20. (zhang2022designofimpactresistant pages 49-52): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

21. (burgin2007adroptower pages 1-2): Leanne V. Burgin and Richard M. Aspden. A drop tower for controlled impact testing of biological tissues. Medical engineering & physics, 29 4:525-30, May 2007. URL: https://doi.org/10.1016/j.medengphy.2006.06.002, doi:10.1016/j.medengphy.2006.06.002. This article has 63 citations and is from a peer-reviewed journal.

22. (chu1988problemsinhighshock pages 1-4): A Chu. Problems in high-shock measurement. Unknown journal, 1988.

23. (krelle2011dropcalibrationof pages 16-20): A Krelle. Drop calibration of accelerometers for shock measurement. Unknown journal, 2011.

24. (chu1988problemsinhighshock pages 4-5): A Chu. Problems in high-shock measurement. Unknown journal, 1988.

25. (rajput2018designandevaluation pages 13-18): Moeen S. Rajput, Magnus Burman, Antonio Segalini, and Stefan Hallström. Design and evaluation of a novel instrumented drop-weight rig for controlled impact testing of polymer composites. Polymer Testing, 68:446-455, Jul 2018. URL: https://doi.org/10.1016/j.polymertesting.2018.04.022, doi:10.1016/j.polymertesting.2018.04.022. This article has 23 citations and is from a peer-reviewed journal.

26. (rajput2018designandevaluation pages 18-24): Moeen S. Rajput, Magnus Burman, Antonio Segalini, and Stefan Hallström. Design and evaluation of a novel instrumented drop-weight rig for controlled impact testing of polymer composites. Polymer Testing, 68:446-455, Jul 2018. URL: https://doi.org/10.1016/j.polymertesting.2018.04.022, doi:10.1016/j.polymertesting.2018.04.022. This article has 23 citations and is from a peer-reviewed journal.

27. (sharafisafa2020experimentalinvestigationof pages 3-5): Mansour Sharafisafa and Luming Shen. Experimental investigation of dynamic fracture patterns of 3d printed rock-like material under impact with digital image correlation. Rock Mechanics and Rock Engineering, pages 1-19, Apr 2020. URL: https://doi.org/10.1007/s00603-020-02115-1, doi:10.1007/s00603-020-02115-1. This article has 61 citations and is from a domain leading peer-reviewed journal.

28. (ellis2020visualmethodsto pages 3-5): Chris L. Ellis and Paul Hazell. Visual methods to assess strain fields in armour materials subjected to dynamic deformation—a review. Applied Sciences, 10:2644, Apr 2020. URL: https://doi.org/10.3390/app10082644, doi:10.3390/app10082644. This article has 14 citations.

29. (hachimi2026mechanicalcharacterizationand pages 6-8): Taoufik Hachimi, Najat Zekriti, Fouad Ait Hmazi, Hamza Bagar, Hatim El Assad, and Nassima Naboulsi. Mechanical characterization and crack propagation in additively manufactured polymers using digital image correlation: a review. Fracture and Structural Integrity, 20:173-206, Apr 2026. URL: https://doi.org/10.3221/igf-esis.77.11, doi:10.3221/igf-esis.77.11. This article has 0 citations.

30. (yang2021smartdigitalimage pages 1-2): J. Yang, J. L. Tao, and C. Franck. Smart digital image correlation patterns via 3d printing. Experimental Mechanics, 61:1181-1191, Jun 2021. URL: https://doi.org/10.1007/s11340-021-00720-x, doi:10.1007/s11340-021-00720-x. This article has 30 citations and is from a peer-reviewed journal.

31. (quino2021specklepatternsfor pages 11-11): Gustavo Quino, Yanhong Chen, Karthik Ram Ramakrishnan, Francisca Martínez-Hergueta, Giuseppe Zumpano, Antonio Pellegrino, and Nik Petrinic. Speckle patterns for dic in challenging scenarios: rapid application and impact endurance. Measurement Science and Technology, 32:015203, Oct 2021. URL: https://doi.org/10.1088/1361-6501/abaae8, doi:10.1088/1361-6501/abaae8. This article has 95 citations and is from a domain leading peer-reviewed journal.

32. (snapp2024superlativemechanicalenergy pages 1-2): Kelsey L. Snapp, Benjamin Verdier, Aldair E. Gongora, Samuel Silverman, Adedire D. Adesiji, Elise F. Morgan, Timothy J. Lawton, Emily Whiting, and Keith A. Brown. Superlative mechanical energy absorbing efficiency discovered through self-driving lab-human partnership. Nature Communications, May 2024. URL: https://doi.org/10.1038/s41467-024-48534-4, doi:10.1038/s41467-024-48534-4. This article has 54 citations and is from a highest quality peer-reviewed journal.

33. (abouali2025impactdamagebehavior pages 13-19): Aliaa M. Abou-Ali, Chukwugozie J. Ejeh, Wesley J. Cantwell, Imad Barsoum, Shrinivas Bojanampati, and Rashid K. Abu Al-Rub. Impact damage behavior of additively manufactured stainless steel triply periodic minimal surface-lattice composite sandwich panels. ES Materials &amp; Manufacturing, Jan 2025. URL: https://doi.org/10.30919/mm1461, doi:10.30919/mm1461. This article has 7 citations.

34. (yi2006largedeformationratedependent pages 1-2): Jin-Hak Yi, M. Boyce, Geoffrey F. Lee, and E. Balizer. Large deformation rate-dependent stress–strain behavior of polyurea and polyurethanes. Polymer, 47:319-329, Jan 2006. URL: https://doi.org/10.1016/j.polymer.2005.10.107, doi:10.1016/j.polymer.2005.10.107. This article has 594 citations and is from a peer-reviewed journal.

35. (yi2006largedeformationratedependent pages 6-6): Jin-Hak Yi, M. Boyce, Geoffrey F. Lee, and E. Balizer. Large deformation rate-dependent stress–strain behavior of polyurea and polyurethanes. Polymer, 47:319-329, Jan 2006. URL: https://doi.org/10.1016/j.polymer.2005.10.107, doi:10.1016/j.polymer.2005.10.107. This article has 594 citations and is from a peer-reviewed journal.

36. (yi2006largedeformationratedependent pages 9-10): Jin-Hak Yi, M. Boyce, Geoffrey F. Lee, and E. Balizer. Large deformation rate-dependent stress–strain behavior of polyurea and polyurethanes. Polymer, 47:319-329, Jan 2006. URL: https://doi.org/10.1016/j.polymer.2005.10.107, doi:10.1016/j.polymer.2005.10.107. This article has 594 citations and is from a peer-reviewed journal.

37. (chen2020applicationoflinear pages 1-2): H. Chen, A.R. Trivedi, and C.R. Siviour. Application of linear viscoelastic continuum damage theory to the low and high strain rate response of thermoplastic polyurethane. Experimental Mechanics, 60:925-936, Jun 2020. URL: https://doi.org/10.1007/s11340-020-00608-2, doi:10.1007/s11340-020-00608-2. This article has 25 citations and is from a peer-reviewed journal.

38. (alemayehu2024enhancedenergyabsorption pages 4-6): Dawit Bogale Alemayehu and Masahiro Todoh. Enhanced energy absorption with bioinspired composite triply periodic minimal surface gyroid lattices fabricated via fused filament fabrication (fff). Journal of Manufacturing and Materials Processing, 8:86, Apr 2024. URL: https://doi.org/10.3390/jmmp8030086, doi:10.3390/jmmp8030086. This article has 27 citations.

39. (pajunen2019designandimpact pages 2-3): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

40. (zhang2022designofimpactresistant pages 40-44): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

41. (zhang2022designofimpactresistant pages 52-58): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

42. (zhang2022designofimpactresistant pages 33-37): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

43. (snapp2024superlativemechanicalenergy pages 8-8): Kelsey L. Snapp, Benjamin Verdier, Aldair E. Gongora, Samuel Silverman, Adedire D. Adesiji, Elise F. Morgan, Timothy J. Lawton, Emily Whiting, and Keith A. Brown. Superlative mechanical energy absorbing efficiency discovered through self-driving lab-human partnership. Nature Communications, May 2024. URL: https://doi.org/10.1038/s41467-024-48534-4, doi:10.1038/s41467-024-48534-4. This article has 54 citations and is from a highest quality peer-reviewed journal.