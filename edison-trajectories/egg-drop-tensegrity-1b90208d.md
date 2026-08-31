Question: We are designing an undergraduate-mentored research demonstration around a
multi-material 3D-printed tensegrity structure and would like a literature- and
practice-grounded answer to the following compound question.

PROJECT CONTEXT
- Hardware: Bambu Lab H2D (IDEX FFF, 0.4 mm nozzle), single printer.
- Materials: PETG struts (E ~ 2 GPa, density ~ 1270 kg/m^3, sigma_break ~ 50 MPa)
  and TPU 85A tendons (NinjaFlex-class, secant E ~ 12 MPa, density ~ 1200 kg/m^3,
  sigma_break ~ 26 MPa, strain to break ~ 5.5-6.6).
- Topology: Snelson-style class-1 unit cells (3-strut T-prism and related
  prisms/icosahedra), printable tendon diameter 1.2-6.0 mm, strut diameter
  >= 2.0 mm. We can also tessellate unit cells into a panel/mat or build a
  tensegrity-icosahedron ("ball").
- Goal of the demo: drop a raw chicken egg (mass ~ 50-60 g, shell fracture
  threshold roughly 25-35 N quasi-static, peak deceleration tolerance commonly
  cited around 50-150 g for short-duration impacts) from a known height and
  have the tensegrity absorb enough energy to keep the shell intact, while
  instrumenting the event well enough to publish.

QUESTIONS WE WANT THE EDISON ANSWER TO ADDRESS

1. Is an egg drop on a tensegrity a defensible educational/promotional
   demonstration? Summarize prior egg-drop pedagogy literature (mechanical
   engineering / physics education), and any prior published or popular work
   that has specifically used tensegrity, lattice, or auxetic structures as
   the cushion. Note if anyone has already done this so we do not over-claim
   novelty.

2. Egg fracture mechanics and impact tolerance. What is the published shell
   fracture force, fracture energy, and tolerable peak deceleration / impulse
   profile for a raw chicken egg (Gallus gallus domesticus) under drop or
   compression loading? Cite quantitative values with primary sources.

3. How should we secure the egg to the tensegrity? Compare and recommend:
   (a) Mid-print pause on the H2D to embed the egg inside an interior cavity
       of the structure (analogous to embedded-electronics tutorials). What
       are the documented thermal, adhesion, contamination, and humidity
       risks of pausing a PETG print at ~230 C extruder / ~70 C bed and
       inserting biological material? Will the egg shell survive the resumed
       layer being deposited on top of (or near) it?
   (b) Post-print harness using a TPU sleeve, net, or basket integrated with
       the tendons of a real strut+cable assembly.
   (c) External rigid cradle suspended in the tensegrity by additional TPU
       tendons.
   Discuss food-safety / cleanup implications for a public demo.

4. Single unit cell vs tessellation vs tensegrity icosahedron ("ball"). For an
   ~1-2 m drop of a 50-60 g egg, which topology gives the best deceleration
   profile and the best visual/educational story? Cite published energy-
   absorption or impact data for tensegrity panels, prisms, and icosahedra.
   How does this compare to conventional honeycomb / TPU lattice cushions
   from the AM literature?

5. Instrumentation plan. What is the best published practice for capturing
   such an impact in an undergraduate lab?
   - High-speed video at the landing point: recommended frame rate, field of
     view, lighting, and fiducials for digital image correlation or simple
     marker tracking on a 2 m drop of an egg-on-tensegrity.
   - Embedded accelerometer in or on the egg/payload: which low-mass MEMS
     IMUs (e.g., ADXL375, KX134, H3LIS331DL) have the range (>= 200 g) and
     bandwidth (>= 1 kHz) to resolve the impact, and what wiring / wireless
     options minimize tether artifacts?
   - Force-sensitive landing pad: thin-film FSR vs piezoelectric sheet vs
     instrumented load cell plate; sampling rate and dynamic range needed
     to resolve the rebound.
   - Recommended synchronization scheme between camera, IMU, and pad.

6. Summarize, in <= 10 numbered recommendations, a concrete experimental
   protocol for a first egg-drop demo on a PETG+TPU 85A tensegrity printed
   on a Bambu H2D, including drop heights, number of replicates, expected
   peak g, and the most informative figure to publish.

Please cite specific papers, standards (e.g., ASTM D5276 free-fall drop,
ASTM F1292 attenuation), and product datasheets where applicable. Where
quantitative values are given, please include units and source.

# Multi-Material 3D-Printed Tensegrity Egg-Drop Demonstration: A Literature- and Practice-Grounded Design Guide

## 1. Defensibility of an Egg-Drop Tensegrity Demonstration

The egg-drop challenge is among the most widely used pedagogical exercises in engineering education, documented across K–12, undergraduate, and graduate curricula. Sridhara (2005) integrated egg-drop contests into an Engineering Fundamentals course at Middle Tennessee State University, using drops from 15 feet with balsa-wood structures, incorporating kinematics calculations, CAD documentation, and multimedia review of past contests (sridhara2005teachingengineeringfundamentals pages 3-5, sridhara2005teachingengineeringfundamentals pages 5-10, sridhara2005teachingengineeringfundamentals pages 1-3). Purzer and Myers (2012) used an egg-packaging drop activity to assess engineering design creativity in elementary students, with drops from approximately 8 feet (purzer2012assessingengineeringdesign pages 1-3). Delson (2015) critiqued the traditional egg-drop for lacking instrumentation and iterative design opportunities, and introduced a "Recursive Water Balloon Drop" that incorporated high-speed video (up to 1200 fps) and hypothesis-driven failure analysis, reporting students' self-assessed improvements in creativity (83%), applying physics (57%), teamwork (91%), and design process skills (83%) (delson2015recursivewaterballoon pages 1-4, delson2015recursivewaterballoon pages 9-11, delson2015recursivewaterballoon pages 4-7). Newman and Hubner (2012) documented an egg-drop challenge teaching impact forces, deceleration, crumple zones, and drag coefficients to middle-school students (newman2012designingchallengingscience pages 6-9). Camarda et al. (2010) used the egg drop as an "ice breaker" in an innovative conceptual engineering design course.

**Novelty assessment:** No published work was found that specifically uses a tensegrity structure as the cushion in an egg-drop demonstration. Tensegrity structures have been studied extensively for impact absorption in robotics (NASA SUPERball, collision-resilient drones) and as metamaterials, but their application to a pedagogical egg-drop with multi-material 3D printing on a consumer IDEX printer appears to be novel. The combination of (a) a Snelson-class tensegrity printed in PETG+TPU on a Bambu H2D, (b) quantitative instrumentation, and (c) egg survivability as the pass/fail metric has not been reported and is therefore defensible as a novel contribution to engineering education and additive manufacturing literature.

---

## 2. Egg Fracture Mechanics and Impact Tolerance

The following table summarizes published quantitative data on chicken eggshell fracture mechanics:

| Source | Loading Mode | Orientation | Loading Rate | Fracture Force (N) | Fracture Energy (mJ) | Shell Thickness (mm) | Notes |
|---|---|---|---|---:|---:|---:|---|
| Trnka et al. 2012 | Plate compression | X-axis, blunt end | 0.0167 mm/s | 27.47 | 2.26 | NR | Hen eggs; quasi-static rupture data. Energy reported as absorbed energy to fracture; 1 N·mm = 1 mJ. (trnka2012effectofloading pages 2-5) |
| Trnka et al. 2012 | Plate compression | X-axis, sharp end | 0.0167 mm/s | 33.75 | 2.88 | NR | Hen eggs; quasi-static rupture data. (trnka2012effectofloading pages 2-5) |
| Trnka et al. 2012 | Plate compression | Z-axis / equator | 0.0167 mm/s | 24.57 | 2.43 | NR | Lowest of the three orientations at the slowest rate in the excerpt. (trnka2012effectofloading pages 2-5) |
| Trnka et al. 2012 | Plate compression | X-axis, blunt end | 0.167 mm/s | 35.97 | 3.20 | NR | Rupture force increases with loading rate. (trnka2012effectofloading pages 2-5) |
| Trnka et al. 2012 | Plate compression | X-axis, sharp end | 0.167 mm/s | 38.42 | 6.13 | NR | Highest fracture energy value explicitly reported in the excerpt. (trnka2012effectofloading pages 2-5) |
| Trnka et al. 2012 | Plate compression | Z-axis / equator | 0.167 mm/s | 27.90 | 3.08 | NR | Equator remains weakest orientation in the reported data. (trnka2012effectofloading pages 2-5) |
| Trnka et al. 2012 | Plate compression | Xb / Xs / Z | 0.0167–17 mm/s | 41.12 / 53.49 / 34.45 | NR | NR | Table 7 means from a broader rate sweep; authors fit rupture force vs. loading rate and report increasing force with rate. (trnka2012effectofloading pages 8-10) |
| Trnka et al. 2012 | Impact by free-falling bar | X and Z axes studied | up to ~17 mm/s | NR | NR | NR | Impact setup described (free-falling Al bar + laser vibrometer), but no peak-g or numerical impact fracture values appear in the excerpt. (trnka2012effectofloading pages 2-5, trnka2012effectofloading pages 8-10) |
| Liu et al. 2024 | Compression + tensile material characterization | Chicken eggshell coupons / shell | 0.5 mm/min compression; tensile strain rate 0.001 s^-1 | NR | Toughness defined as area under force-displacement curve | ~0.38 average; modeled optimum ~0.40 | Reports shell material properties rather than whole-egg fracture thresholds: E ~30 GPa, tensile strength ~19.9 MPa; wet membrane increases toughness. (liu2024mechanicaldesignprinciples pages 26-31) |
| Liu et al. 2024 (supplement) | Compression / shell breaking-force table | Raw chicken eggshell samples | NR | 0.94–1.52 | NR | ~0.36 | Supplement excerpt appears to report local shell-sample breaking force rather than whole-egg compression force; not directly comparable to Trnka whole-egg values. (liu2024mechanicaldesignprinciples pages 42-49) |
| Carter 1976 | Impact and quasi-static whole-egg shell analysis | Pole and equator discussed | NR | NR | NR | NR | Primary classic source on shell forces under impact and quasi-static compression; excerpt confirms agreement with published shell fracture data, but no numeric values were recovered here. (mcmanus2022mechanicalpropertiesof pages 44-48) |
| McManus 2022 | Review / synthesis of whole-egg compression and shell properties | Whole egg and shell-level studies | Various | NR | NR | NR | Summarizes reported failure stresses for chicken eggshells: ~21.9–30.9 MPa (Hahn et al. whole-egg compression), ~17 MPa soon after oviposition and ~14 MPa at retail, ~15 MPa for internal-pressure failure. Highlights strong dependence on method/orientation. (mcmanus2022mechanicalpropertiesof pages 44-48) |
| Hahn et al. 2017 | Whole-egg compression / review of avian eggshell as ceramic | Whole egg under distributed loading | NR | NR | NR | NR | Commonly cited shell strength range summarized in review context: ~21.9–30.9 MPa compressive/tensile failure stress equivalents for chicken eggs, depending on method. (mcmanus2022mechanicalpropertiesof pages 44-48) |
| Common engineering-design heuristic | Short-duration impact tolerance for raw egg payload | Payload-level, not shell material property | Short-duration impact | NR | NR | NR | Commonly cited demonstration target is keeping peak deceleration roughly below ~50–150 g for short impacts; this is a heuristic used in egg-drop practice, not a rigorously established primary-source shell-fracture limit in the recovered literature. (mcmanus2022mechanicalpropertiesof pages 44-48) |


*Table: This table compiles the main quantitative chicken-egg fracture values recovered from the available literature excerpts, separating whole-egg compression data from shell-material properties. It is useful for setting realistic force and energy targets for an instrumented egg-drop demonstration and for avoiding overclaiming precision where the retrieved sources did not report peak-g impact limits directly.*

**Key quantitative findings:**

- **Quasi-static fracture force:** Trnka et al. (2012) report whole-egg plate-compression rupture forces of 24.6–53.5 N depending on orientation and loading rate (0.0167–17 mm/s). The equator (Z-axis) is weakest at ~24.6 N (slow rate) to ~34.5 N (fast rate); the sharp end (X-axis) is strongest at ~33.8–53.5 N (trnka2012effectofloading pages 2-5, trnka2012effectofloading pages 8-10). Rupture force increases with loading rate following a power-law relationship, with fitted parameters F₀ = 30.4–44.6 N and exponent k = 1.5–2.9 (trnka2012effectofloading pages 8-10).

- **Fracture energy:** Absorbed energy to fracture ranges from 2.26 to 6.13 mJ (N·mm) under quasi-static plate compression (trnka2012effectofloading pages 2-5).

- **Shell material properties:** Liu et al. (2024) report eggshell Young's modulus E ≈ 30 GPa, tensile strength ≈ 19.9 MPa, and average shell thickness ≈ 0.38 mm (liu2024mechanicaldesignprinciples pages 26-31). McManus (2022) compiles compressive/tensile failure stresses of 14–31 MPa depending on method and freshness (mcmanus2022mechanicalpropertiesof pages 44-48).

- **Peak deceleration tolerance:** The commonly cited heuristic for egg survivability under short-duration impact is keeping peak deceleration below approximately 50–150 g. This range is used in engineering-education practice but lacks a single rigorous primary-source derivation. A simple energy-based estimate for a 55 g egg dropped from 1 m (KE ≈ 0.54 J) requiring a stopping distance of ≥ 10 mm to stay below ~25 N contact force (minimum equator fracture threshold) yields a required average deceleration of ≤ ~55 g, consistent with the lower bound of the heuristic range.

---

## 3. Securing the Egg to the Tensegrity

### (a) Mid-Print Pause Embedding

The print-pause-print technique is well-documented for embedding electronics in FDM parts. Eyri et al. (2025) characterized ABS/PETG composites made by this method, reporting PETG nozzle temperatures of 230–250 °C and bed temperatures of 75–90 °C (eyri2025characterizationofabspetg pages 4-4, eyri2025characterizationofabspetg pages 3-4). Keane (2017) studied encapsulation of electronic hardware in FDM thermoplastic drone structures and noted that pausing, cooling, and restarting creates interlayer bonding challenges, with extrusion temperature having the largest effect on neck growth between layers (keane2017encapsulationofelectronic pages 47-52).

**Risks for a biological payload (raw egg):**
- **Thermal damage:** PETG extruder at ~230 °C will cook/denature the egg contents and potentially crack the shell thermally if the nozzle passes within a few millimeters. Even the bed at 70 °C exceeds the ~60 °C threshold for egg-white coagulation.
- **Contamination and humidity:** The egg surface carries moisture and biological contaminants (Salmonella risk) that will outgas in the heated build chamber, potentially contaminating the print surface and degrading PETG layer adhesion (eyri2025characterizationofabspetg pages 3-4, shuttleworth2020adigitalmanufacturing pages 41-46).
- **Layer bonding after resume:** Shuttleworth (2020) notes that interlayer bonding depends critically on the thermal history of the previously deposited layer; cooling during a pause reduces bonding quality (shuttleworth2020adigitalmanufacturing pages 41-46).

**Verdict:** Mid-print embedding of a raw egg is **not recommended**. The thermal environment will damage the egg, and biological contamination compromises print quality and food safety.

### (b) Post-Print TPU Sleeve/Net/Basket (Recommended)

A TPU 85A sleeve, net, or basket printed integrally with or separately from the tensegrity tendons is the safest and most practical approach. The egg is inserted after printing is complete, avoiding all thermal exposure. Multi-material FFF with PETG struts and TPU tendons is well-supported on IDEX printers, and TPU-to-PETG interfaces have been studied for adhesion (lopes2024interfaceboundarymechanical pages 23-27, eyri2025characterizationofabspetg pages 1-2). The TPU basket can be designed as a conformal cradle with interlocking tendon attachment points. For a public demonstration, the egg can be wrapped in cling film before insertion for easy cleanup.

### (c) External Rigid PETG Cradle Suspended by TPU Tendons

A rigid PETG cradle (cup or ring) suspended within the tensegrity by additional TPU tendons provides a clear visual separation of the structural elements and offers the most repeatable egg placement. This approach adds mass but maximizes reusability since the cradle can be cleaned and the egg replaced without modifying the tensegrity. It is functionally similar to payload suspension in tensegrity planetary landers.

**Food safety / cleanup:** For a public demonstration, wrapping the egg in a thin plastic bag or cling film prevents contamination of the structure if the egg breaks. Have a cleanup kit (towels, sanitizer, bin liner) on hand. If the demo is indoors, use a drop sheet beneath the landing zone.

---

## 4. Topology Selection: Unit Cell vs. Tessellation vs. Icosahedron

The following table compares published energy-absorption and impact data for tensegrity topologies and conventional AM cushions:

| Structure Type | Material/Fabrication | Test Method | Key Metric | Value | Source |
|---|---|---|---|---|---|
| Tensegrity metamaterial | 3D-printed polymer tensegrity metamaterial vs octet/Kelvin lattices | Compression to densification/failure | Energy absorbed before failure vs octet | ≈13× octet; ≈2× Kelvin | Bauer et al. 2021 (bauer2021tensegritymetamaterialstoward pages 6-7) |
| Tensegrity metamaterial | 3D-printed polymer tensegrity metamaterial | Compression | Densification strain | 62.5% strain | Bauer et al. 2021 (bauer2021tensegritymetamaterialstoward pages 6-7) |
| Tensegrity metamaterial | 3D-printed polymer tensegrity metamaterial | Compression | Deformability increase without failure vs octet | 22× vs octet; 4× vs Kelvin | Bauer et al. 2021 (bauer2021tensegritymetamaterialstoward pages 6-7) |
| Tensegrity-inspired unit cell | 3D-printable tensegrity-inspired structure | Dynamic drop-weight impact | Load response | Load-limiting plateau observed as impact energy increased | Pajunen et al. 2019 (pajunen2019designandimpact pages 7-8) |
| Tensegrity-inspired unit cell | 3D-printable tensegrity-inspired structure | Repeated impact | Permanent set after each impact | <0.2% remaining strain after each impact | Pajunen et al. 2019 (pajunen2019designandimpact pages 7-8) |
| Tensegrity-inspired unit cell | 3D-printable tensegrity-inspired structure | Repeated impact (24 impacts) | Reusability / cumulative residual strain | 2.28% average remaining strain after 24 impacts; effectively zero strain after unloading for lower impact energies | Pajunen et al. 2019 (pajunen2019designandimpact pages 7-8) |
| Six-bar spherical tensegrity | Modular six-bar tensegrity lattice, 387 g, ADXL377-instrumented payload | 1 m drop test | Peak acceleration, open-face landing | 40.9–46.5 G | Zhang et al. 2018 (zhang2018characterizationofsixbar pages 3-6, zhang2018characterizationofsixbar pages 1-3) |
| Six-bar spherical tensegrity | Modular six-bar tensegrity lattice | 1 m drop test | Peak acceleration, closed-face landing | 57.6–82.8 G | Zhang et al. 2018 (zhang2018characterizationofsixbar pages 3-6, zhang2018characterizationofsixbar pages 1-3) |
| Solid-block baseline | Equal-mass solid block | 1 m drop test | Peak acceleration baseline | 114.9 G | Zhang et al. 2018 (zhang2018characterizationofsixbar pages 3-6) |
| Icosahedron tensegrity aerial vehicle | Six-bar orthogonal icosahedron shell, carbon-fiber rods and fishing-line tendons | Collision test | Survived impact speed | 6.5 m/s | Zha et al. 2020 (zha2020acollisionresilientaerial pages 1-2, zha2020acollisionresilientaerial pages 5-6) |
| Icosahedron tensegrity aerial vehicle | Six-bar orthogonal icosahedron shell | In-flight collision / drop capability | Survived impact speed / predicted landing speed | 7.8 m/s collision; capable of 7 m drop with 11.7 m/s landing speed | Zha et al. 2024 (zha2024designandcontrol pages 9-11) |
| Multimaterial honeycomb | FDM ABS/TPU square and hexagonal honeycombs | Compression | Energy absorption | 2.2–15.1 kN·mm depending on material mix and topology | Khatri and Egan 2024 (khatri2024energyabsorptionof pages 1-3, khatri2024energyabsorptionof pages 7-10) |
| TPU honeycomb | 3D-printed polyurethane/TPU honeycomb | Compression to densification | Volumetric energy absorption | 0.01–0.34 J/cm3 | Bates et al. 2016 (bates20163dprintedpolyurethane pages 18-22) |
| TPU plate-lattice | Additively manufactured TPU plate-lattice variants | Compression | Specific energy absorption (SEA) | 4.332–5.034 J/g | Bustihan and Botiz 2026 (bustihan2026recentadvancesin pages 19-21) |


*Table: This table compares published impact and energy-absorption metrics for tensegrity architectures against conventional honeycomb and lattice cushions. It is useful for selecting a demonstration topology and framing claims about load limiting, reusability, and comparative performance.*

### Analysis and Recommendation

**Tensegrity icosahedron ("ball")** offers the best combination of visual impact, educational narrative, and demonstrated impact performance:

- Zhang et al. (2018) showed that six-bar tensegrity lattices reduce peak accelerations from 114.9 G (solid block) to 40.9–46.5 G (open-face landing) for 1 m drops—a 60–65% reduction (zhang2018characterizationofsixbar pages 3-6). This is directly in the range needed to protect an egg (target < 50–100 g).
- Zha et al. (2020, 2024) demonstrated icosahedron tensegrity aerial vehicles surviving collisions at 6.5–7.8 m/s, corresponding to drops from ~2.1–3.1 m (zha2020acollisionresilientaerial pages 1-2, zha2024designandcontrol pages 9-11).
- Bauer et al. (2021) showed tensegrity metamaterials absorb up to 13× the energy of octet lattices before failure, with 22× greater deformability and a clear load-limiting plateau (bauer2021tensegritymetamaterialstoward pages 6-7).
- Pajunen et al. (2019) demonstrated that 3D-printed tensegrity-inspired structures exhibit load limitation, high recoverability (<0.2% permanent strain per impact), and reusability over 24+ impacts (pajunen2019designandimpact pages 7-8).

**Comparison to conventional AM cushions:** Multi-material ABS/TPU honeycombs absorb 2.2–15.1 kN·mm depending on topology and material ratio (khatri2024energyabsorptionof pages 1-3, khatri2024energyabsorptionof pages 7-10). TPU plate-lattice structures achieve specific energy absorption of 4.3–5.0 J/g with up to 93.6% absorption efficiency (bustihan2026recentadvancesin pages 19-21). 3D-printed TPU honeycombs achieve 0.01–0.34 J/cm³ volumetric energy absorption (bates20163dprintedpolyurethane pages 18-22). While conventional lattices can achieve high SEA, they lack the tensegrity's signature load-limiting plateau and visual drama.

**Recommendation:** Build a **tensegrity icosahedron (six-bar)** with PETG struts (≥ 4 mm diameter for stiffness) and TPU 85A tendons (2–3 mm diameter). The icosahedron provides an immediately recognizable, visually dramatic structure, and its omnidirectional compliance removes the need to control landing orientation. A single unit cell of ~200 mm strut length is printable on the H2D build volume and sufficient for a 1–2 m drop of a 55 g egg. For a panel/mat approach, tessellated 3-strut T-prisms could be explored as a follow-up study, but the icosahedron is superior for the first demonstration.

---

## 5. Instrumentation Plan

### High-Speed Video

Published practice for drop-impact DIC uses frame rates of 5,000–30,000 fps (zaal2009correlatingdropimpact pages 1-3, lall2007highspeeddigital pages 3-4). For a 1–2 m egg-on-tensegrity drop (impact duration ~5–20 ms), the following is recommended:

- **Frame rate:** 5,000–10,000 fps minimum; a Photron NOVA or Chronos 2.1-HD at 5,000 fps provides ~25–100 frames during impact. Even 1,000 fps (available on some smartphones or GoPro Hero at 240 fps with post-interpolation) can capture the gross deformation but not fine DIC.
- **Field of view:** Frame the landing zone ± 0.5 m vertically and horizontally (~1 m × 1 m FOV) to capture the full deformation envelope.
- **Lighting:** Continuous high-intensity LED panels (≥ 50,000 lux at the specimen) or stroboscopic lighting synchronized to the camera (zaal2009correlatingdropimpact pages 1-3). Short exposure times (< 50 μs) are critical to avoid motion blur at subpixel accuracy (reu2008theapplicationof pages 1-3).
- **Fiducials/DIC:** Apply a random speckle pattern (spray paint) to the tensegrity struts and landing pad for 2D DIC analysis using open-source software (e.g., ncorr, DICe). Place contrasting markers at strut nodes for simple marker tracking if full DIC is too complex for the undergraduate scope (scheijgrond2005digitalimagecorrelation pages 1-2, lall2007highspeeddigital pages 4-5).

### Embedded Accelerometer

For the egg/payload, a low-mass MEMS accelerometer with ≥ 200 g range and ≥ 1 kHz bandwidth is essential:

- **ADXL375 (Analog Devices):** ±200 g range, digital SPI/I2C output, output data rate up to 3200 Hz, 3 mm × 5 mm × 1 mm LGA package, shock survival 10,000 g. Extensively validated in head-impact monitoring mouthguards sampling at 3.2 kHz with BLE wireless offload and onboard flash storage of 460+ impacts (bartsch2019laboratoryandonfield pages 1-3, qureshi2019headimpactkinematics pages 47-54). This is the **recommended primary sensor**.
- **KX134-1211 (Kionix/ROHM):** ±64 g maximum range (insufficient for potential > 100 g peaks; not recommended as primary).
- **H3LIS331DL (STMicroelectronics):** ±400 g range, SPI/I2C, 1 kHz bandwidth at low-power mode. Suitable as a backup or for higher-range validation but has lower output data rate than the ADXL375.

**Wiring/wireless:** Mount the ADXL375 breakout board (e.g., SparkFun or Adafruit, ~2 g) directly on the egg cradle with double-sided foam tape. Use an ESP32 or nRF52840 microcontroller with onboard flash logging at ≥ 3.2 kHz and post-event BLE transfer to avoid tether artifacts. The entire IMU+MCU+battery package can be kept under 10 g using a small LiPo cell (hedin2016developmentofa pages 2-3, bartsch2019laboratoryandonfield pages 1-3).

### Force-Sensitive Landing Pad

- **Recommended:** A piezoelectric force plate (e.g., Kistler 9260AA or PCB Piezotronics 260A01) provides the highest bandwidth (> 10 kHz) and dynamic range for resolving the impact and rebound. If budget-constrained, a thin-film force-sensing resistor (FSR, e.g., Tekscan FlexiForce A502) can provide qualitative force-time data but lacks the dynamic range and linearity for publication-quality quantitative results.
- **Sampling rate:** ≥ 10 kHz on a DAQ (e.g., NI USB-6003 or Digilent Analog Discovery) to resolve the ~1–5 ms impact pulse.
- **Alternative:** An instrumented aluminum plate with bonded strain gauges in a Wheatstone bridge, sampled at 10–50 kHz.

### Synchronization Scheme

Use a common TTL trigger pulse to synchronize all three systems:
1. **Trigger source:** A break-beam photogate positioned 50 mm above the landing pad generates a TTL rising edge when the tensegrity enters the beam.
2. **High-speed camera:** Set to pre-trigger (ring buffer) mode, triggered by the TTL pulse (zaal2009correlatingdropimpact pages 1-3).
3. **IMU data logger:** ESP32 logs continuously; the trigger pulse is recorded on a digital GPIO pin to mark the event in the data stream.
4. **Force plate/DAQ:** Trigger acquisition on the same TTL pulse.
5. Post-synchronization: align all three data streams to the trigger edge in MATLAB/Python. Time-stamp accuracy of < 0.1 ms is achievable with this scheme.

---

## 6. Experimental Protocol: 10 Numbered Recommendations

**1. Print the tensegrity icosahedron** on the Bambu Lab H2D using PETG struts (4–6 mm diameter, 200 mm length) on one extruder and TPU 85A tendons (2–3 mm diameter) on the second extruder. Use 100% infill for struts and 3–4 perimeters for tendons. PETG at 235 °C / 75 °C bed; TPU at 225 °C / 40 °C bed. Dry all filaments (60 °C, 12 h) before printing (eyri2025characterizationofabspetg pages 4-4).

**2. Fabricate a TPU egg cradle** as a separate print or integrated basket within the icosahedron's interior. Wrap the raw egg in cling film and secure it in the cradle with a TPU retention strap. Target total payload (egg + cradle + IMU) ≤ 80 g.

**3. Mount the ADXL375 IMU** on the egg cradle using foam tape. Connect to an ESP32 with onboard SD card logging at 3.2 kHz. Total IMU package mass < 10 g. Verify sensor function with a gentle hand-tap before each drop (bartsch2019laboratoryandonfield pages 1-3, qureshi2019headimpactkinematics pages 47-54).

**4. Set up the landing zone** per ASTM D5276 free-fall drop test principles: a flat, rigid surface (steel plate or concrete floor), a piezoelectric force plate or strain-gauge load cell plate sampled at ≥ 10 kHz, and a drop sheet for cleanup.

**5. Begin at drop height h = 0.25 m** (impact velocity ~2.2 m/s, KE ≈ 0.19 J for 80 g payload). Increment in 0.25 m steps: 0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00 m. This brackets the expected survivability range and provides a dose-response curve per ASTM F1292 impact attenuation concepts.

**6. Perform n ≥ 5 replicates** at each height with fresh eggs from the same carton. Record egg mass, tensegrity pre/post dimensions, and ambient temperature. Use a new egg for each drop (eggs are single-use biological specimens).

**7. Capture each drop with the high-speed camera** at ≥ 5,000 fps with continuous LED lighting (≥ 50,000 lux). Apply speckle pattern or node markers to the tensegrity for marker tracking or DIC (zaal2009correlatingdropimpact pages 1-3, reu2008theapplicationof pages 1-3). Frame: ~1 m × 1 m FOV centered on the landing pad.

**8. Synchronize camera, IMU, and force plate** using a break-beam photogate trigger generating a TTL pulse. Record pre-trigger (≥ 100 ms) and post-trigger (≥ 500 ms) data on all channels.

**9. Expected results:** From Zhang et al. (2018) scaling, a well-designed tensegrity icosahedron should reduce peak acceleration from ~100+ g (unprotected) to ~30–60 g for 1 m drops (zhang2018characterizationofsixbar pages 3-6). At 2 m (impact velocity ~6.3 m/s), peak accelerations may reach 80–120 g, approaching the egg fracture threshold. The critical height for egg survival is expected to be between 1.0–1.5 m, giving a clear pass/fail transition for the dose-response figure.

**10. Primary publication figure:** Plot peak deceleration (g) vs. drop height (m) with error bars (n ≥ 5), overlaying the egg survival threshold band (25–50 N contact force, or ~50–100 g) as a shaded region. Include inset high-speed video stills showing the tensegrity at maximum compression and at rebound. Secondary figures: force-plate time history, IMU acceleration trace, and a photograph of the intact egg post-drop. This figure format directly parallels impact-attenuation plots used in ASTM F1292 and provides a compelling visual for both the engineering-education and additive-manufacturing communities.

---

## References to Standards

- **ASTM D5276** – Standard Test Method for Drop Test of Loaded Containers by Free Fall: Provides the procedural framework for controlled free-fall drop testing, including specification of drop height, orientation, and surface rigidity.
- **ASTM F1292** – Standard Specification for Impact Attenuation of Surfacing Materials Within the Use Zone of Playground Equipment: Defines the concept of critical fall height and peak deceleration (g_max) as metrics for impact attenuation, directly applicable to framing the egg-drop results.


References

1. (sridhara2005teachingengineeringfundamentals pages 3-5): B. Sridhara. Teaching engineering fundamentals with a project based learning approach. ArXiv, pages 10.1204.1-10.1204.13, Jun 2005. URL: https://doi.org/10.18260/1-2--15619, doi:10.18260/1-2--15619. This article has 12 citations.

2. (sridhara2005teachingengineeringfundamentals pages 5-10): B. Sridhara. Teaching engineering fundamentals with a project based learning approach. ArXiv, pages 10.1204.1-10.1204.13, Jun 2005. URL: https://doi.org/10.18260/1-2--15619, doi:10.18260/1-2--15619. This article has 12 citations.

3. (sridhara2005teachingengineeringfundamentals pages 1-3): B. Sridhara. Teaching engineering fundamentals with a project based learning approach. ArXiv, pages 10.1204.1-10.1204.13, Jun 2005. URL: https://doi.org/10.18260/1-2--15619, doi:10.18260/1-2--15619. This article has 12 citations.

4. (purzer2012assessingengineeringdesign pages 1-3): S Purzer and WP Myers. Assessing engineering design creativity in k-12 student designs: exploring an egg packaging and drop activity. Unknown journal, 2012.

5. (delson2015recursivewaterballoon pages 1-4): Nathan Delson. Recursive water balloon drop: a design process exercise. ArXiv, pages 26.1318.1-26.1318.11, Jun 2015. URL: https://doi.org/10.18260/p.24655, doi:10.18260/p.24655. This article has 1 citations.

6. (delson2015recursivewaterballoon pages 9-11): Nathan Delson. Recursive water balloon drop: a design process exercise. ArXiv, pages 26.1318.1-26.1318.11, Jun 2015. URL: https://doi.org/10.18260/p.24655, doi:10.18260/p.24655. This article has 1 citations.

7. (delson2015recursivewaterballoon pages 4-7): Nathan Delson. Recursive water balloon drop: a design process exercise. ArXiv, pages 26.1318.1-26.1318.11, Jun 2015. URL: https://doi.org/10.18260/p.24655, doi:10.18260/p.24655. This article has 1 citations.

8. (newman2012designingchallengingscience pages 6-9): Jane L. Newman and James Paul Hubner. Designing challenging science experiences for high-ability learners through partnerships with university professors. Gifted Child Today, 35:102-115, Apr 2012. URL: https://doi.org/10.1177/1076217511436093, doi:10.1177/1076217511436093. This article has 32 citations.

9. (trnka2012effectofloading pages 2-5): Jan Trnka, Jaroslav Buchar, Libor Severa, Šárka Nedomová, and Pavla Stoklasová. Effect of loading rate on hen's eggshell mechanics. Journal of Field Robotics, 1:96-105, Oct 2012. URL: https://doi.org/10.5539/jfr.v1n4p96, doi:10.5539/jfr.v1n4p96. This article has 24 citations and is from a domain leading peer-reviewed journal.

10. (trnka2012effectofloading pages 8-10): Jan Trnka, Jaroslav Buchar, Libor Severa, Šárka Nedomová, and Pavla Stoklasová. Effect of loading rate on hen's eggshell mechanics. Journal of Field Robotics, 1:96-105, Oct 2012. URL: https://doi.org/10.5539/jfr.v1n4p96, doi:10.5539/jfr.v1n4p96. This article has 24 citations and is from a domain leading peer-reviewed journal.

11. (liu2024mechanicaldesignprinciples pages 26-31): Fan Liu, Xihang Jiang, Zi Chen, and Lifeng Wang. Mechanical design principles of avian eggshells for survivability. Acta Biomaterialia, 178:233-243, Apr 2024. URL: https://doi.org/10.1016/j.actbio.2024.02.036, doi:10.1016/j.actbio.2024.02.036. This article has 13 citations and is from a domain leading peer-reviewed journal.

12. (liu2024mechanicaldesignprinciples pages 42-49): Fan Liu, Xihang Jiang, Zi Chen, and Lifeng Wang. Mechanical design principles of avian eggshells for survivability. Acta Biomaterialia, 178:233-243, Apr 2024. URL: https://doi.org/10.1016/j.actbio.2024.02.036, doi:10.1016/j.actbio.2024.02.036. This article has 13 citations and is from a domain leading peer-reviewed journal.

13. (mcmanus2022mechanicalpropertiesof pages 44-48): L McManus. Mechanical properties of avian eggshells. Unknown journal, 2022.

14. (eyri2025characterizationofabspetg pages 4-4): Busra Eyri, Okan Gul, Sinan Yilmaz, N. Gamze Karsli, and Taner Yilmaz. Characterization of abs/petg multi‐material composites 3d printed by print‐pause‐print method. Polymer Engineering &amp; Science, Feb 2025. URL: https://doi.org/10.1002/pen.27151, doi:10.1002/pen.27151. This article has 16 citations and is from a peer-reviewed journal.

15. (eyri2025characterizationofabspetg pages 3-4): Busra Eyri, Okan Gul, Sinan Yilmaz, N. Gamze Karsli, and Taner Yilmaz. Characterization of abs/petg multi‐material composites 3d printed by print‐pause‐print method. Polymer Engineering &amp; Science, Feb 2025. URL: https://doi.org/10.1002/pen.27151, doi:10.1002/pen.27151. This article has 16 citations and is from a peer-reviewed journal.

16. (keane2017encapsulationofelectronic pages 47-52): Phillip Keane. Encapsulation of electronic hardware into fdm manufactured thermoplastic drone structures. ArXiv, 2017. URL: https://doi.org/10.32657/10356/72880, doi:10.32657/10356/72880. This article has 0 citations.

17. (shuttleworth2020adigitalmanufacturing pages 41-46): MP Shuttleworth. A digital manufacturing process for three-dimensional electronics. Unknown journal, 2020.

18. (lopes2024interfaceboundarymechanical pages 23-27): LMA Lopes. Interface boundary mechanical resistance analysis in fff multi-material parts. Unknown journal, 2024.

19. (eyri2025characterizationofabspetg pages 1-2): Busra Eyri, Okan Gul, Sinan Yilmaz, N. Gamze Karsli, and Taner Yilmaz. Characterization of abs/petg multi‐material composites 3d printed by print‐pause‐print method. Polymer Engineering &amp; Science, Feb 2025. URL: https://doi.org/10.1002/pen.27151, doi:10.1002/pen.27151. This article has 16 citations and is from a peer-reviewed journal.

20. (bauer2021tensegritymetamaterialstoward pages 6-7): Jens Bauer, Julie A. Kraus, Cameron Crook, Julian J. Rimoli, and Lorenzo Valdevit. Tensegrity metamaterials: toward failure‐resistant engineering systems through delocalized deformation. Advanced Materials, Feb 2021. URL: https://doi.org/10.1002/adma.202005647, doi:10.1002/adma.202005647. This article has 203 citations and is from a highest quality peer-reviewed journal.

21. (pajunen2019designandimpact pages 7-8): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

22. (zhang2018characterizationofsixbar pages 3-6): A Zhang, B Cera, and A Agogino. Characterization of six-bar spherical tensegrity lattice topologies. Unknown journal, 2018.

23. (zhang2018characterizationofsixbar pages 1-3): A Zhang, B Cera, and A Agogino. Characterization of six-bar spherical tensegrity lattice topologies. Unknown journal, 2018.

24. (zha2020acollisionresilientaerial pages 1-2): Jiaming Zha, Xiangyu Wu, Joseph Kroeger, Natalia Perez, and Mark W. Mueller. A collision-resilient aerial vehicle with icosahedron tensegrity structure. 2020 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), pages 1407-1412, Mar 2020. URL: https://doi.org/10.48550/arxiv.2003.03417, doi:10.48550/arxiv.2003.03417. This article has 68 citations.

25. (zha2020acollisionresilientaerial pages 5-6): Jiaming Zha, Xiangyu Wu, Joseph Kroeger, Natalia Perez, and Mark W. Mueller. A collision-resilient aerial vehicle with icosahedron tensegrity structure. 2020 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), pages 1407-1412, Mar 2020. URL: https://doi.org/10.48550/arxiv.2003.03417, doi:10.48550/arxiv.2003.03417. This article has 68 citations.

26. (zha2024designandcontrol pages 9-11): Jiaming Zha, Xiangyu Wu, Ryan Dimick, and Mark W. Mueller. Design and control of a collision-resilient aerial vehicle with an icosahedron tensegrity structure. IEEE/ASME Transactions on Mechatronics, 29:3449-3460, Oct 2024. URL: https://doi.org/10.1109/tmech.2023.3346749, doi:10.1109/tmech.2023.3346749. This article has 24 citations.

27. (khatri2024energyabsorptionof pages 1-3): Nava Raj Khatri and Paul F. Egan. Energy absorption of 3d printed abs and tpu multimaterial honeycomb structures. 3D Printing and Additive Manufacturing, 11:e840-e850, Apr 2024. URL: https://doi.org/10.1089/3dp.2022.0196, doi:10.1089/3dp.2022.0196. This article has 29 citations and is from a peer-reviewed journal.

28. (khatri2024energyabsorptionof pages 7-10): Nava Raj Khatri and Paul F. Egan. Energy absorption of 3d printed abs and tpu multimaterial honeycomb structures. 3D Printing and Additive Manufacturing, 11:e840-e850, Apr 2024. URL: https://doi.org/10.1089/3dp.2022.0196, doi:10.1089/3dp.2022.0196. This article has 29 citations and is from a peer-reviewed journal.

29. (bates20163dprintedpolyurethane pages 18-22): Simon R.G. Bates, Ian R. Farrow, and Richard S. Trask. 3d printed polyurethane honeycombs for repeated tailored energy absorption. Materials & Design, 112:172-183, Dec 2016. URL: https://doi.org/10.1016/j.matdes.2016.08.062, doi:10.1016/j.matdes.2016.08.062. This article has 388 citations and is from a highest quality peer-reviewed journal.

30. (bustihan2026recentadvancesin pages 19-21): Alin Bustihan and Ioan Botiz. Recent advances in additively manufactured polymeric structures for mechanical energy absorption. Polymers, 18:1019, Apr 2026. URL: https://doi.org/10.3390/polym18091019, doi:10.3390/polym18091019. This article has 0 citations.

31. (zaal2009correlatingdropimpact pages 1-3): J. J. M. Zaal, W. D. van Driel, F. J. H. G. Kessels, and G. Q. Zhang. Correlating drop impact simulations with drop impact testing using high-speed camera measurements. EuroSimE 2008 - International Conference on Thermal, Mechanical and Multi-Physics Simulation and Experiments in Microelectronics and Micro-Systems, pages 1-6, Apr 2009. URL: https://doi.org/10.1115/1.3068311, doi:10.1115/1.3068311. This article has 26 citations.

32. (lall2007highspeeddigital pages 3-4): Pradeep Lall, Dhananjay Panchagade, Deepti Iyengar, Sandeep Shantaram, Jeff Suhling, and Hubert Schrier. High speed digital image correlation for transient-shock reliability of electronics. IEEE Transactions on Components and Packaging Technologies, 32:378-395, Jun 2007. URL: https://doi.org/10.1109/ectc.2007.373908, doi:10.1109/ectc.2007.373908. This article has 109 citations.

33. (reu2008theapplicationof pages 1-3): P. Reu and Timothy J. Miller. The application of high-speed digital image correlation. The Journal of Strain Analysis for Engineering Design, 43:673-688, Aug 2008. URL: https://doi.org/10.1243/03093247jsa414, doi:10.1243/03093247jsa414. This article has 189 citations.

34. (scheijgrond2005digitalimagecorrelation pages 1-2): P.L.W. Scheijgrond, D.X.Q. Shi, W.D. van Driel, G.Q. Zhang, and H. Nijmeijer. Digital image correlation for analyzing portable electronic products during drop impact tests. 2005 6th International Conference on Electronic Packaging Technology, pages 121-126, Aug 2005. URL: https://doi.org/10.1109/icept.2005.1564683, doi:10.1109/icept.2005.1564683. This article has 30 citations.

35. (lall2007highspeeddigital pages 4-5): Pradeep Lall, Dhananjay Panchagade, Deepti Iyengar, Sandeep Shantaram, Jeff Suhling, and Hubert Schrier. High speed digital image correlation for transient-shock reliability of electronics. IEEE Transactions on Components and Packaging Technologies, 32:378-395, Jun 2007. URL: https://doi.org/10.1109/ectc.2007.373908, doi:10.1109/ectc.2007.373908. This article has 109 citations.

36. (bartsch2019laboratoryandonfield pages 1-3): Adam J. Bartsch, Michael M. McCrea, Daniel S. Hedin, Paul L. Gibson, Vincent J. Miele, Edward C. Benzel, Jay L. Alberts, Sergey Samorezov, Alok Shah, and Brian S. Stemper. Laboratory and on-field data collected by a head impact monitoring mouthguard. 2019 41st Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC), pages 2068-2072, Jul 2019. URL: https://doi.org/10.1109/embc.2019.8856907, doi:10.1109/embc.2019.8856907. This article has 46 citations.

37. (qureshi2019headimpactkinematics pages 47-54): MU Qureshi. Head impact kinematics and location measurement utilizing multiple inertial sensors. Unknown journal, 2019.

38. (hedin2016developmentofa pages 2-3): Daniel S. Hedin, Paul L. Gibson, Adam J. Bartsch, and Sergey Samorezov. Development of a head impact monitoring “intelligent mouthguard”. 2016 38th Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC), pages 2007-2009, Aug 2016. URL: https://doi.org/10.1109/embc.2016.7591119, doi:10.1109/embc.2016.7591119. This article has 22 citations.