Question: This is a THIRD follow-up literature query for the egg-drop tensegrity
demonstration project. Prior Edison tasks on this thread have already
covered topology, fracture mechanics, instrumentation, and a drag-free
V/m-constrained benchmark — please do NOT re-derive that material. Focus
exclusively on the SUPERball v2 actuator question and its tech-transfer
implications below.

CONTEXT FROM PRIOR EDISON FINDING (Vespignani et al. 2018):
   "A 2-meter diameter, 36 kg, fully actuated six-bar tensegrity robot
    with 24 actuators and compliant nylon cables (up to 15% stretch).
    Designed to survive impact velocities upward of 8 m/s, with
    simulations analyzing up to 15 m/s impacts. Cable stiffness
    ~4000 N/m produced lowest peak cable forces (~950 N)."

OUR CURRENT STUDY (the work we are positioning against this prior art):
   - Six-bar tensegrity unit cell, ~10–20× smaller than SUPERball v2
     (bounding sphere O(0.2 m) rather than 2 m).
   - Multi-material FFF print on a Bambu H2D: PETG struts +
     TPU 85A tendons (NinjaFlex-class, E ~12 MPa secant).
   - **Passive** structure: no motors, no on-board electronics, no
     active cable retraction. Tendons are pre-tensioned only by the
     printed geometry / assembly preload, not by actuators.
   - Many tendon-to-strut connections are presently treated as
     "largely untensioned" in modeling and as printed
     mechanical-interlock joints in hardware (see prior joint-design
     work in this repo: dovetail B + anchor-bulb A primary).
   - Intended demo is a drag-free egg drop onto a rigid floor (per
     the previous Edison follow-up benchmark, task f41b7034).

QUESTIONS TO ANSWER (cite peer-reviewed sources, give numbers with units):

1. **What are SUPERball v2's actuators? Explain simply.**
   Plain-English description of the 24 actuators in SUPERball v2:
     - Type (DC brushless motor + spool? linear screw? series-elastic?
       cable-driven reel?), make/model if Vespignani 2018 names one,
       and where on the robot they are mounted (inside the rigid
       struts? at the nodes? off-board?).
     - What each actuator physically does at a stroke level: does it
       reel cable in/out, change resting length, apply a torque, or
       something else? What is the stroke range / max force / max
       speed reported?
     - Why 24 (= 4 × 6 struts, or = number of actuated cables, or
       = 24 of the 30 cables, etc.) — i.e., the cable-actuation
       topology choice.
     - Role during landing vs role during locomotion: are the
       actuators *passive compliant* (acting like springs / dampers)
       at impact, or are they *active* (commanded to back-drive,
       reel out, or shed energy) during the touchdown event itself?
       Cite the Vespignani 2018 / Agogino 2018 / SunSpiral / Caluwaerts
       publications that document this.

2. **How does this relate to our passive PETG+TPU tensegrity?**
   Concrete contrast table or paragraph covering:
     - Cable / tendon material and stiffness: SUPERball v2 nylon
       (15% stretch, k ≈ 4000 N/m, peak force ~950 N at landing) vs
       our printed TPU 85A tendons (E ≈ 12 MPa, derive an order-of-
       magnitude k for a representative L = 100 mm × Ø 3 mm tendon
       and compare).
     - Pre-tension: SUPERball v2 actively servoed pretension from the
       motors vs our passive print-set / preload-only pretension.
     - Length adaptivity: SUPERball v2 can change cable resting length
       in flight / on impact vs ours which cannot.
     - Energy-dissipation pathway: where does kinetic energy go in
       each system at touchdown (motor back-EMF / friction / cable
       hysteresis / strut-floor contact / TPU hysteresis)?

3. **How does the lack of actuators limit the usefulness of our study?**
   Honest list of tech-transfer concerns to a SUPERball-v2-style
   actuated lander:
     - Cable preload uncertainty (passive print-set vs servoed setpoint)
       and how that propagates into peak-g and h_crit predictions.
     - Inability to reproduce Vespignani's "cable stiffness ~4000 N/m
       gives lowest peak cable force" finding without actuators (since
       our k is fixed by geometry and TPU choice, we cannot sweep k
       on the same hardware).
     - Inability to test active-landing strategies (variable-impedance
       control, motor back-driving as damper, payload-mass-aware
       pre-tension scheduling).
     - Scaling: Does anything go wrong physically when scaling a
       passive 6-bar tensegrity from 2 m / 36 kg down to 0.2 m /
       O(0.5 kg)? (Strain rate at impact is ~10× higher for the same
       drop height; TPU dynamic modulus increases with strain rate;
       tendon mass fraction shifts; strut Euler buckling load changes
       with L^-2.)
     - Reusability: SUPERball v2 explicitly tests N>1 landings — how
       many landings did our prior-art tensegrity references survive,
       and what failure modes appeared first (cable yield, cable creep,
       strut buckling, joint pull-out)?

4. **How could/should the passive design be adjusted to be more
   amenable to future actuated tensegrity work?**
   Specific, actionable design changes the project should make
   *now* so that the passive PETG+TPU drop demo cleanly extrapolates
   to an actuated SUPERball-v2-class lander later. Examples to evaluate:
     - Replace one or more printed TPU tendons with a removable
       bowden / nylon cable routed through a printed eyelet, so that
       a future revision can add a motorized spool at the strut end.
     - Print struts as **hollow** with an internal cavity and an
       end-cap interface sized for an off-the-shelf brushless motor +
       gearhead (e.g., a typical SUPERball-class motor envelope).
     - Standardize anchor geometry so a single anchor accepts either
       a printed TPU tendon (passive) OR a swaged steel/nylon cable
       termination (active), so the hardware can be retrofitted
       without re-printing the whole cell.
     - Add one or two "instrumented" tendons that include an inline
       load cell (or a printed strain-gauge channel) so that one-off
       cable-force traces can be captured without redesigning the
       cell.
     - Choose a strut diameter and node geometry that *already*
       satisfy the class-1 condition (strut Ø < closest-approach
       distance) at the larger SUPERball v2 scale, so the same
       topology survives a scale-up without rework.
     - Pre-instrument the payload cradle so an ADXL375 + ESP32 +
       DAQ can move from passive demo to actuated future revision
       unchanged.
   For each suggestion, state what concrete tech-transfer concern it
   alleviates and whether it imposes any cost (mass, printability,
   complexity) on the immediate passive demo.

5. **One-off validations to alleviate the tech-transfer concern.**
   Recommend a small set (3–6) of single-shot or low-replicate
   experiments that can be performed *on the passive PETG+TPU article*
   to directly de-risk the eventual jump to an actuated SUPERball-v2-
   class system. Each validation should:
     - Be doable with the already-recommended instrumentation
       (ADXL375 + ESP32 @ 3.2 kHz, ≥5000 fps high-speed video,
       photogate-TTL sync, optional inline tendon load cell).
     - Produce a number that can be directly compared against a
       Vespignani / Caluwaerts / Agogino / Zhang published number
       (peak cable force, peak payload g, energy ratio, recovery
       time, residual strain after N drops).
     - Be feasible at ~0.2 m scale with O(0.5 kg) mass.
   Concrete candidates to evaluate (and add others as appropriate):
     (a) **Single-tendon force trace** — instrument one tendon with
         an inline miniature load cell and measure peak cable force
         at h = 1, 2, 3 m drops. Compare per-tendon force normalized
         by (m·g·sqrt(2h/g)) to the Vespignani ~950 N at 8 m/s.
     (b) **Cable-stiffness sensitivity sweep** — print 3 specimens
         with TPU tendon Ø ∈ {1.5, 2.5, 4.0} mm (so k spans a
         decade) and check whether peak g vs k follows the
         Vespignani-style optimum, at the smaller scale.
     (c) **Pre-tension sensitivity** — assemble the same cell at
         3 different print-set pretensions (slack, nominal, taut)
         and measure peak g, residual strain, and cable hysteresis.
     (d) **N-drop reusability test** — drop the same specimen N=20
         times at h = 3 m and report cumulative residual strain and
         the drop number at first failure (mirrors Pajunen 2019
         protocol, cited in prior follow-up).
     (e) **Worst-case orientation** — test vertex-down, face-down,
         and edge-down landings to compare orientation-sensitivity
         envelope against the Zhang 2022 22″ tensegrity numbers.
     (f) **Quasi-static vs impact stiffness gap** — measure
         quasi-static k of one tendon on an Instron-class machine
         and compare to the apparent dynamic k inferred from the
         drop, to bound the rate-dependence of TPU 85A.
   Indicate which one or two of these are the *highest-leverage*
   single experiments for tech-transfer credibility.

6. **Bottom-line recommendation.**
   In one short paragraph, recommend whether the passive PETG+TPU
   tensegrity drop demo should explicitly position itself as
   "passive scale-model precursor to SUPERball-v2-class actuated
   landers" (with the design changes above) or as a standalone
   passive impact-absorber benchmark (and citing SUPERball v2 only
   as the canonical actuated reference). State the recommended
   *minimum viable* design changes (from question 4) and the
   *minimum viable* one-off validations (from question 5) needed
   to support that positioning in a future ASME JMD or RA-L
   submission.

Please cite specific peer-reviewed papers, conference proceedings,
NASA technical reports, and product datasheets where applicable.

# SUPERball v2 Actuator Analysis and Tech-Transfer Implications for a Passive PETG+TPU Tensegrity Egg-Drop Demo

---

## 1. SUPERball v2 Actuators — Plain-English Description

### Type and Make/Model

The SUPERball platform uses **brushless DC (BLDC) motor–driven cable-spool actuators** configured as series-elastic actuators (SEAs). The specific motor is a **100 W Maxon EC 22 mm (part no. 386674)** paired with a **Maxon 109:1 planetary gearbox (part no. 370784)** (sabelhaus2014hardwaredesignandb pages 4-6, sabelhaus2014hardwaredesignanda pages 4-6). The motor drives a **30 mm diameter POM (acetal) spindle** that winds a **1.4 mm Vectran cable** (Cortland 7012 Vectran HT, Type 150, rated breaking strength 2227 N) (sabelhaus2014hardwaredesignandb pages 4-6, sabelhaus2014hardwaredesignanda pages 4-6). The spindle sits between two smooth POM spool caps with a 0.5 mm gap to reduce friction and allow multidirectional cable sliding (sabelhaus2014hardwaredesignandb pages 4-6, sabelhaus2014hardwaredesignanda pages 4-6).

### Mounting Location

Each actuator is housed in a **modular "end cap"** — a self-contained unit that slides into each end of a hollow aluminum strut tube. SUPERball is composed of **12 fully independent, autonomous end-cap units** (two per strut, six struts total), each containing the motor, gearbox, spindle, cable routing, motor driver, embedded computing, battery, IMU, and sensors (sunspiral2015superballbotstructures pages 80-83, sunspiral2015superballbotstructuresa pages 80-83, sabelhaus2014hardwaredesignandb pages 1-2, sabelhaus2014hardwaredesignand pages 1-2). The motor mount floats in a 1 mm gap within the bottom cap to avoid loading the integrated torque sensor (sabelhaus2014hardwaredesignandb pages 4-6, sabelhaus2014hardwaredesignanda pages 4-6).

### Stroke-Level Function

Each actuator **reels cable in and out** to change the effective resting length of one cable in the tensegrity's outer shell. Because each actuated cable passes through a compression spring housed inside a neighboring strut, the assembly functions as a **series-elastic actuator (SEA)** — the motor sets cable length, and the spring provides passive compliance. Cable force is measured by an in-line compressive force sensor, and motor torque is sensed on the motor mount for local closed-loop tension control (sabelhaus2015systemdesignand pages 3-4, sabelhaus2015systemdesignand pages 1-2).

### Performance Specifications

- **Nominal cable retraction speed:** 0.42 m/s (sabelhaus2014hardwaredesignandb pages 4-6, sabelhaus2014hardwaredesignanda pages 4-6)
- **Actuator stroke (Δl_act):** 0.42 m (sunspiral2015superballbotstructuresb pages 80-83, sunspiral2015superballbotstructures pages 80-83, sunspiral2015superballbotstructuresa pages 80-83)
- **Nominal cable tension:** ~140 N (2014 prototype) to ~250 N (2015 design) (sabelhaus2014hardwaredesignandb pages 4-6, sabelhaus2014hardwaredesignanda pages 4-6, sunspiral2015superballbotstructuresa pages 80-83, sabelhaus2015systemdesignand pages 1-2)
- **Passive spring-cable stiffness (k_passive):** ~613 N/m (2014) to ~998 N/m (2015) (sunspiral2015superballbotstructuresa pages 80-83, sunspiral2015superballbotstructures pages 80-83, sabelhaus2015systemdesignand pages 1-2)
- **Vectran cable breaking strength:** 2227 N (sabelhaus2014hardwaredesignandb pages 4-6)

An alternative v2 actuator concept explored by Bruce et al. (2014) used **parallel-pulley blocks driven by power screws** (Daewoo SFK00801, 8 mm diameter, 5 mm pitch) paired with the same Maxon 386674 motors, predicting cable forces of ~98.5 N at 3000 rpm and cable output speeds near 1 m/s (bruce2014superballexploringtensegrities pages 4-6, lu2014superballexploringtensegrities pages 4-6).

### Why 24 Actuators

A six-bar tensegrity has **24 exterior cables** connecting the strut endpoints. The built SUPERball prototype (v1/2015) used only **12 actuators for 24 spring-cable assemblies** due to packaging constraints from the 100 W motors (sunspiral2015superballbotstructures pages 80-83, sunspiral2015superballbotstructuresa pages 80-83, sabelhaus2015systemdesignand pages 2-3, sunspiral2015superballbotstructuresb pages 80-83). The 12 actuators were arranged in a symmetric **"actuated triangles" topology**: four of the eight equilateral triangular faces were fully actuated (4 faces × 3 edges = 12 cables), while the remaining four faces were passive. This was chosen to conservatively guarantee basic motion primitives (e.g., punctuated "Flop and Roll") while halving the actuator count (sunspiral2015superballbotstructures pages 80-83, sunspiral2015superballbotstructuresa pages 80-83, sabelhaus2015systemdesignand pages 2-3). The Vespignani 2018 SUPERball v2 design goal was to **fully actuate all 24 cables** (one actuator per cable) for greater mobility and agility (sunspiral2015superballbotstructuresb pages 90-95, sunspiral2015superballbotstructuresa pages 90-95, sunspiral2015superballbotstructures pages 90-95).

### Role During Landing vs. Locomotion

The SUPERball physical prototype was **explicitly not hardened for high-speed landing scenarios**; the NIAC Phase 2 report states the team was "ignoring high-speed landing scenarios for this physical prototype" (sunspiral2015superballbotstructuresa pages 80-83, sunspiral2015superballbotstructuresb pages 80-83). During impact, the structure relies on **passive compliance** from the spring-cable assemblies — the springs act as elastic energy absorbers, and the cables carry only tensile loads (sunspiral2015superballbotstructuresa pages 80-83, sunspiral2015superballbotstructures pages 80-83, zhang2022designofimpactresistant pages 22-25, zhang2022designofimpactresistanta pages 22-25). The literature does not document active reel-out, back-drive, or energy-shedding actuator commands during touchdown for the tested prototype (sunspiral2015superballbotstructuresa pages 80-83, sunspiral2015superballbotstructures pages 80-83, sunspiral2015superballbotstructuresb pages 80-83). The actuators were designed primarily for **locomotion** — changing cable resting lengths to shift the center of gravity and induce rolling (sunspiral2015superballbotstructures pages 80-83, sabelhaus2015systemdesignand pages 2-3). However, the SEA architecture means that if an impact event back-drives the motor through the gearbox, the geartrain friction and motor back-EMF would passively dissipate some energy; this pathway is not quantified in the literature.

Zhang (2022) explicitly notes the design tension between locomotion and impact resilience: locomotion prefers low cable pretension and adds actuator mass that increases impact forces, while impact resilience benefits from higher pretension and mass-optimized springs (zhang2022designofimpactresistanta pages 22-25, zhang2022designofimpactresistant pages 22-25, zhang2022designofimpactresistanta pages 93-97, zhang2022designofimpactresistant pages 93-97).

---

## 2. Comparison: SUPERball v2 vs. Passive PETG+TPU Tensegrity

The following table provides a comprehensive parameter-by-parameter comparison:

| Parameter | SUPERball v2 / NASA reference | Passive PETG+TPU article | Tech-transfer implication |
|---|---|---|---|
| Bounding diameter | ~2 m class robot (user-provided prior-art context for Vespignani 2018) | ~0.2 m class six-bar cell | ~10× geometric down-scaling changes strain rate, buckling margin, and tendon mass fraction; do not assume dynamic similarity |
| Total mass | 36 kg (user-provided prior-art context for Vespignani 2018); earlier SUPERball hardware/prototypes reported ~21 kg for 1.7 m strut system (sunspiral2015superballbotstructures pages 80-83, sunspiral2015superballbotstructuresb pages 80-83) | ~0.5 kg target article mass | Absolute impact energy scales down strongly, but local strain rates and printed-joint effects may scale the wrong way |
| Tendon material | Vespignani 2018 context: compliant nylon cables with up to 15% stretch; earlier SUPERball hardware used 1.4 mm Vectran cable with 2227 N break strength in series-elastic spring-cable assemblies (sabelhaus2014hardwaredesignandb pages 4-6, sabelhaus2014hardwaredesignanda pages 4-6) | Printed TPU 85A / NinjaFlex-class tendon; manufacturer-scale properties around E ≈ 12 MPa, elongation at break ≈ 660%, tensile strength ≈ 26 MPa (bustihan2025reusable3dprintedthermoplastic pages 2-4) | Your passive article is materially much softer and more viscoelastic than the cited SUPERball hardware; it is closer to a soft passive absorber than to a spool-actuated cable robot |
| Cable / tendon stiffness | Vespignani 2018 context: ~4000 N/m gave lowest peak cable force; earlier SUPERball 2015 passive spring-cable stiffness reported ~998 N/m (sunspiral2015superballbotstructuresa pages 80-83, sunspiral2015superballbotstructures pages 80-83, sabelhaus2015systemdesignand pages 1-2) | For representative TPU tendon, L = 100 mm, d = 3 mm, A = πd²/4 = 7.07 mm², E = 12 MPa gives k = EA/L ≈ 12e6×7.07e-6/0.1 ≈ 848 N/m ≈ 0.85 kN/m; if effective printed secant stiffness is lower or gauge length longer, order can drop toward ~10² N/m | Your tendon is same order as earlier passive spring-cable stiffness, but well below the 4000 N/m Vespignani simulation optimum; hardware stiffness sweeps will require geometry/material swaps, not control changes |
| Peak cable force at impact | ~950 N at ~8 m/s in Vespignani 2018 context; earlier SUPERball requirements/prototypes cited ~200–250 N peak/nominal cable tensions depending on configuration (sunspiral2015superballbotstructuresa pages 80-83, sunspiral2015superballbotstructures pages 80-83, sabelhaus2015systemdesignand pages 1-2) | Not yet measured; for 0.5 kg dropped 3 m, impact speed is v = √(2gh) ≈ 7.67 m/s, so per-tendon loads are plausibly O(5–50 N) but should be treated as TBD until measured | A single inline tendon load cell is the cleanest bridge metric to SUPERball literature |
| Pre-tension method | Active motor-set cable length / motor position control; series-elastic spring-cable assemblies with local sensing and closed-loop actuation (sabelhaus2015systemdesignand pages 3-4, sabelhaus2015systemdesignand pages 1-2) | Passive print-set geometry and assembly preload only; no motorized setpoint | Preload uncertainty will be larger and less repeatable, so h_crit and peak-g confidence intervals will be wider |
| Length adaptivity | Yes; BLDC motor + gearbox + spindle changes cable length/rest length during operation (sabelhaus2014hardwaredesignandb pages 4-6, sabelhaus2014hardwaredesignanda pages 4-6) | None; tendon length fixed by printed geometry except elastic stretch | You cannot reproduce active landing or stiffness scheduling with current hardware |
| Actuation hardware | BLDC motorized cable actuator in end caps: 100 W Maxon EC 22 mm motor (part 386674) + 109:1 gearbox + 30 mm POM spindle/spool; end caps slide into hollow struts; later v2 goal is full 24-cable actuation (sabelhaus2014hardwaredesignandb pages 4-6, sunspiral2015superballbotstructures pages 80-83, sabelhaus2014hardwaredesignanda pages 4-6, sunspiral2015superballbotstructuresa pages 90-95) | None | Strongest gap versus SUPERball-style lander: missing the mechanism that sets tension, changes geometry, and potentially dissipates energy electromechanically |
| Number of actuated cables | Current early SUPERball prototype: 12 actuators for 24 spring-cable assemblies in actuated-triangle topology; future / v2 goal: fully actuate all 24 exterior cables (sunspiral2015superballbotstructures pages 80-83, sabelhaus2015systemdesignand pages 2-3, sunspiral2015superballbotstructuresa pages 90-95) | 0 | Your article benchmarks passive tensegrity impact absorption, not cable-actuated tensegrity landing control |
| Touchdown energy dissipation pathway | Primarily passive compliance in spring-cable assemblies during landing; literature does not document active reel-out/back-drive touchdown control for the tested prototype; losses likely include spring hysteresis, cable friction, structural damping, and possibly motor/geartrain losses if back-driven (sunspiral2015superballbotstructuresa pages 80-83, sunspiral2015superballbotstructures pages 80-83, sabelhaus2015systemdesignand pages 3-4) | TPU viscoelastic hysteresis, printed-joint micro-slip, strut-floor friction/contact loss, air damping, and any local plasticity at printed anchors | Even if gross kinematics match, the loss channels differ, so restitution and rebound timing may not transfer directly |
| Impact velocity rating | Vespignani 2018 context: designed to survive >8 m/s, analyzed up to 15 m/s; earlier NIAC/SUPERball work reported tensegrity survivability to ~15 m/s in analysis and favorable scaling with larger size (sunspiral2015superballbotstructures pages 80-83, sunspiral2015superballbotstructuresb pages 80-83) | Drag-free 3 m drop gives v ≈ 7.67 m/s | Your benchmark is relevant to the lower end of SUPERball’s landing-speed envelope, but only as a passive analog |
| Dynamic modulus / rate effect | Nylon/Vectran cable systems have some rate sensitivity, but SUPERball literature emphasizes structural/cable compliance more than polymer viscoelastic amplification (sunspiral2015superballbotstructures pages 80-83, sunspiral2015superballbotstructuresb pages 80-83) | TPU 85A shows dynamic modulus ≈ 27 MPa vs quasi-static ≈ 13.5 MPa in compression, i.e. ~2× stiffer at high rate (trzaskowski2025physicomechanicalpropertiesof pages 13-14) | Small-scale drops may appear artificially “stiffer” than quasi-static coupon data would predict; quasi-static-to-impact calibration is essential |


*Table: This table contrasts the actuator-enabled SUPERball architecture with the proposed passive PETG+TPU six-bar article on the exact Q2 dimensions most relevant to tech transfer. It highlights where the passive demo is a useful precursor and where missing actuation, preload control, and rate-dependent TPU behavior limit direct comparison.*

### Key Derived Number: TPU Tendon Stiffness

For a representative TPU 85A tendon with gauge length L = 100 mm, diameter d = 3 mm, cross-sectional area A = π(3)²/4 = 7.07 mm², and manufacturer secant modulus E ≈ 12 MPa (bustihan2025reusable3dprintedthermoplastic pages 2-4):

**k = EA/L = (12 × 10⁶)(7.07 × 10⁻⁶) / 0.1 ≈ 850 N/m**

This is remarkably close to the SUPERball 2015 passive spring-cable stiffness of ~998 N/m (sunspiral2015superballbotstructuresa pages 80-83, sabelhaus2015systemdesignand pages 1-2), but well below the Vespignani 2018 simulation-optimal 4000 N/m. However, the TPU stiffness is **rate-dependent**: dynamic compressive modulus is approximately **2× the quasi-static value** (~27 MPa vs. ~13.5 MPa at room temperature) (trzaskowski2025physicomechanicalpropertiesof pages 13-14), meaning the effective impact stiffness could approach ~1700 N/m — still below 4000 N/m but closer. Under elevated temperature (50 °C, plausible from repeated impact self-heating), dynamic stresses drop 30–45%, partially reversing this stiffening (trzaskowski2025physicomechanicalpropertiesof pages 13-14).

### Energy Dissipation Pathways

- **SUPERball:** Spring hysteresis, cable-on-endcap friction, structural damping, geartrain friction if back-driven, and motor back-EMF. The spring-cable architecture is deliberately series-elastic to distribute and absorb impact energy (sabelhaus2015systemdesignand pages 3-4, sunspiral2015superballbotstructures pages 80-83).
- **Passive PETG+TPU article:** TPU viscoelastic hysteresis (the dominant mechanism — TPU 85A shows significant loading/unloading hysteresis), printed-joint micro-slip, strut-floor contact friction, and air damping. No electromechanical dissipation pathway exists.

---

## 3. Limitations of the Passive Study for Tech Transfer

### 3.1 Cable Preload Uncertainty

SUPERball's actuators servo cable tension to known setpoints via motor position control and in-line force sensors (sabelhaus2015systemdesignand pages 3-4, sabelhaus2015systemdesignand pages 1-2). The passive PETG+TPU article relies on print-set geometry and assembly preload, which is subject to printer tolerance, TPU creep, ambient temperature, and assembly variability. This propagates directly into uncertainty in effective structural stiffness (k_P = Σ k_i cos²θ_i), which governs peak payload deceleration and critical drop height (zhang2022designofimpactresistant pages 22-25, zhang2022designofimpactresistanta pages 22-25).

### 3.2 Inability to Sweep Cable Stiffness In Situ

Vespignani 2018's key finding — that cable stiffness ~4000 N/m produced the lowest peak cable forces — was obtained by parametrically varying k in simulation. The passive article's k is fixed by TPU material properties and tendon geometry. Sweeping k requires printing new specimens with different tendon diameters, which is a between-specimen comparison rather than a within-specimen parametric sweep, introducing confounds from fabrication variability.

### 3.3 No Active Landing Strategies

The passive article cannot test variable-impedance control, motor back-driving as a damper, payload-mass-aware pre-tension scheduling, or in-flight cable length adjustment. These are the central capabilities that differentiate SUPERball-class robots from passive structures (sunspiral2015superballbotstructuresa pages 80-83, zhang2022designofimpactresistanta pages 93-97, zhang2022designofimpactresistant pages 93-97).

### 3.4 Scaling Concerns (2 m → 0.2 m)

Several physical effects change adversely when scaling a passive six-bar tensegrity down by 10×:

- **Strain rate at impact:** For the same drop height h, impact velocity v = √(2gh) is scale-independent, but the characteristic deformation time scales as L/v, so nominal strain rate scales as ~v/L. At 0.2 m scale, strain rate is approximately **10× higher** than at 2 m for the same v. Because TPU 85A dynamic modulus is ~2× the quasi-static value (trzaskowski2025physicomechanicalpropertiesof pages 13-14), the small structure will appear disproportionately stiff and will transmit higher peak g to the payload.

- **Strut Euler buckling load:** P_cr ∝ EI/L² (zhang2022designofimpactresistanta pages 19-22, zhang2022designofimpactresistant pages 19-22). For geometrically similar scaling (strut diameter ∝ L), moment of inertia I ∝ d⁴ ∝ L⁴, so P_cr ∝ L². The mass scales as L³, so the gravitational load scales as L³ while buckling capacity scales as L², meaning **smaller structures have a higher buckling margin relative to self-weight** — this is favorable.

- **Tendon mass fraction:** At 0.2 m scale, TPU tendons are a larger fraction of total mass because motor/electronics mass is absent. This shifts the modal behavior and may alter the energy partition between tendon stretch and strut deformation.

- **Cable stroke as fraction of bounding sphere:** SunSpiral et al. (2015) simulations show larger tensegrities provide longer cable stroke relative to impact energy, reducing peak forces; smaller structures require stiffer cables and produce larger payload accelerations (sunspiral2015superballbotstructuresb pages 75-80).

### 3.5 Reusability

SUPERball v2 is designed for multiple landings. Prior tensegrity drop-test literature shows mixed reusability: Pajunen et al. (2019) achieved 24 repeated impacts on a 3D-printed tensegrity-inspired structure with only 2.28% total residual strain (average 0.11% per impact) (pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 5-7). By contrast, Zhang (2022) found that tensegrity prototypes with silicone rubber lattices survived **no more than five drops before failure** (payload fracture, lattice damage), and prototypes with steel springs showed **noticeable plastic deformation after approximately ten drops** (spring end-hook deformation) (zhang2022designofimpactresistant pages 25-29, zhang2022designofimpactresistanta pages 25-29). Rod fractures were also observed in experiments (zhang2022designofimpactresistant pages 73-77). The passive PETG+TPU article's reusability is unknown and depends on whether TPU tendon creep, PETG strut fatigue, or joint pull-out emerges first as the limiting failure mode.

---

## 4. Design Changes for Future Actuated Compatibility

The following table details specific, actionable design modifications that should be implemented now to ensure the passive demo cleanly extrapolates to a future actuated system:

| Design change description | Tech-transfer concern it alleviates | Cost/impact on immediate passive demo (mass, printability, complexity) | Priority |
|---|---|---|---|
| Replace one or more printed TPU tendons with a **removable Bowden/nylon cable routed through a printed eyelet** so a future end-cap spool can reel the same line in/out | Creates a direct migration path from passive fixed-length tendons to SUPERball-style cable actuation; reduces reprint burden when testing servoed pretension, resting-length changes, and cable-force repeatability; also lets you compare printed-TPU vs reel-driven cable behavior on the same cell (sabelhaus2014hardwaredesignandb pages 4-6, sabelhaus2014hardwaredesignanda pages 4-6, sabelhaus2014hardwaredesignandb pages 1-2, sabelhaus2014hardwaredesignand pages 1-2) | Small mass increase; moderate print complexity because eyelets must avoid abrasion and stress concentration; possible local friction and wear; minor reduction in “all-printed” simplicity | **Essential** |
| Print **hollow struts with an internal cavity and standardized end-cap motor interface** sized around a SUPERball-class actuator envelope (e.g., Maxon EC 22 mm / 100 W class with gearbox and spindle clearance) | Preserves a clean upgrade path to rod/end-cap-mounted motorized spools rather than forcing a total strut redesign later; directly addresses the biggest hardware discontinuity between the passive article and SUPERball-family robots, whose actuators are packaged in modular end-caps or rod-centered modules (sabelhaus2014hardwaredesignandb pages 4-6, sunspiral2015superballbotstructures pages 80-83, sabelhaus2014hardwaredesignanda pages 4-6, chen2017softsphericaltensegrity pages 3-5, sabelhaus2014hardwaredesignandb pages 1-2, sabelhaus2014hardwaredesignand pages 1-2) | Moderate mass penalty if walls are overbuilt; may improve print time but complicate stiffness tuning and crush resistance; requires support/bridging strategy and careful end-cap tolerancing | **Essential** |
| Standardize a **dual-purpose anchor geometry** so one anchor accepts either a printed TPU tendon or a swaged/knotted nylon/Vectran/steel cable termination | Reduces lock-in to one tendon technology; makes it possible to retrofit active cables, test alternative cable stiffnesses, and compare passive vs actuated hardware without rebuilding nodes/struts; also addresses joint-failure uncertainty by concentrating design effort on a single validated interface (sabelhaus2014hardwaredesignandb pages 4-6, sabelhaus2014hardwaredesignand pages 4-6, sabelhaus2014hardwaredesignanda pages 4-6, chen2017softsphericaltensegrity pages 6-7, sabelhaus2014hardwaredesignanda pages 1-2) | Very low mass cost; slight CAD complexity; may require larger local fillets or metal inserts to avoid pull-out; strongly positive for experimental flexibility | **Essential** |
| Add **one or two instrumented tendons** with either an inline miniature load cell bay or a printable strain-sensor/gauge channel | Directly de-risks the missing cable-force data problem and enables comparison to SUPERball/Vespignani-style peak cable-force metrics; also improves model calibration for preload uncertainty, hysteresis, and orientation effects (sabelhaus2015systemdesignand pages 3-4, zhang2022designofimpactresistanta pages 33-37, zhang2022designofimpactresistant pages 33-37) | Small to moderate mass and wiring penalty; added assembly complexity; one tendon may become locally stiffer/heavier than others, so symmetry should be preserved with a dummy-mass counterpart if needed | **Recommended** |
| Choose **strut diameter and node geometry that satisfy the class-1 condition at larger scale** (strut diameter less than closest-approach distance) and preserve cable clearance for future routing | Avoids topology/packaging dead ends when scaling the same unit cell upward; reduces future rod-rod interference, cable rubbing, and routing congestion that become critical once active cable paths, end-caps, and larger deflections are introduced; aligns with tensegrity scaling and buckling concerns (zhang2022designofimpactresistanta pages 19-22, zhang2022designofimpactresistant pages 19-22, sunspiral2015superballbotstructuresb pages 75-80) | No major mass penalty if considered early; may constrain aesthetic freedom and require slimmer nodes/struts; could modestly reduce immediate robustness if diameters are minimized too aggressively | **Recommended** |
| Build a **pre-instrumented payload cradle** with mounting, power, and cable-management provisions for ADXL375 + ESP32 + DAQ from the first passive revision | Makes passive and future actuated tests share the same payload, sensor frame, and synchronization workflow; directly supports apples-to-apples peak-g, recovery-time, and orientation comparisons across revisions; also reduces the chance that a later electronics integration changes the mass distribution and invalidates baseline data (zhang2022designofimpactresistant pages 81-86, zhang2022designofimpactresistanta pages 81-86, zhang2022designofimpactresistant pages 73-77) | Small mass increase and packaging overhead; minimal printability penalty; highly favorable because instrumentation is already planned for the passive demo | **Essential** |


*Table: This table summarizes the most useful passive-design changes to preserve compatibility with future SUPERball-style actuation and instrumentation. It highlights which modifications most directly reduce tech-transfer risk and what they cost the near-term passive egg-drop demo.*

The three **essential** changes are: (i) at least one replaceable Bowden/nylon cable through a printed eyelet, (ii) hollow struts with a standardized end-cap motor interface sized for a Maxon EC 22 mm class actuator, and (iii) a dual-purpose anchor geometry that accepts either printed TPU tendons or swaged cable terminations. These directly mirror the modular end-cap architecture documented for SUPERball (sabelhaus2014hardwaredesignandb pages 1-2, sabelhaus2014hardwaredesignand pages 1-2, sabelhaus2014hardwaredesignanda pages 1-2) and the rod-centered actuation approach of TT-3 (chen2017softsphericaltensegrity pages 3-5, chen2017softsphericaltensegrity pages 6-7). The pre-instrumented payload cradle is also essential because it ensures identical sensor placement and mass distribution across passive and future actuated revisions.

---

## 5. One-Off Validation Experiments

The following table details six experiments executable on the passive article, ranked by tech-transfer leverage:

| Experiment | Instrumentation needed | Metric produced and literature comparator | Feasibility at 0.2 m scale | Tech-transfer concern addressed | Priority |
|---|---|---|---|---|---|
| **(a) Single-tendon force trace** — instrument one representative tendon with an inline miniature load cell and drop from **h = 1, 2, 3 m** | ADXL375 + ESP32 at 3.2 kHz; ≥5000 fps high-speed video; photogate-TTL sync; **inline tendon load cell** on one tendon | Peak tendon force **F_peak** vs drop height; normalize by impact momentum or by **mgh**; compare shape/order of magnitude against SUPERball v2’s reported **~950 N peak cable force at ~8 m/s** and earlier SUPERball cable-tension ranges (~200–250 N nominal/peak prototype values) (sunspiral2015superballbotstructures pages 80-83, sunspiral2015superballbotstructuresb pages 80-83, sunspiral2015superballbotstructuresa pages 80-83) | **High** — only one tendon must be modified; compatible with current article and existing instrumentation stack | Directly addresses the biggest transfer gap: whether the passive TPU article produces tendon-force histories remotely comparable, after normalization, to SUPERball-class landing loads | **Highest leverage** |
| **(b) Cable-stiffness sensitivity sweep** — print 3 specimens with TPU tendon **Ø = 1.5, 2.5, 4.0 mm** to span a large **k** range | ADXL375 + ESP32; ≥5000 fps video; photogate sync; optional single-tendon load cell | Peak payload/egg **g**, contact time, rebound, and optional **F_peak** vs inferred tendon stiffness **k**; compare whether an optimum appears, analogous to Vespignani’s finding that **~4000 N/m** minimized peak cable force; also compare trend direction to Zhang’s orientation-dependent effective stiffness values **7.0–15.4 kN/m** (sunspiral2015superballbotstructures pages 80-83, zhang2022designofimpactresistanta pages 33-37, zhang2022designofimpactresistant pages 33-37) | **High** — easiest hardware-variable sweep because tendon diameter can be changed without redesigning the whole topology | Tests whether a passive small-scale article can reproduce the key SUPERball-style design insight that landing severity is **non-monotonic in stiffness**, rather than “softer is always better” | **Highest leverage** |
| **(c) Pre-tension sensitivity** — assemble otherwise identical cells at **slack / nominal / taut** print-set preload | ADXL375 + ESP32; ≥5000 fps video; photogate sync; ruler/video metrology for residual strain; optional inline load cell | Peak **g**, rebound coefficient, residual tendon strain, and hysteresis area; compare qualitatively to literature emphasis that pretension increases stiffness but reduces energy-absorption margin and conflicts with locomotion needs (zhang2022designofimpactresistanta pages 22-25, zhang2022designofimpactresistant pages 22-25, zhang2022designofimpactresistanta pages 93-97, zhang2022designofimpactresistant pages 93-97) | **High** — no new fabrication method required beyond controlled assembly jigs or spacer shims | Quantifies preload uncertainty from passive assembly, the main difference from servo-set pretension in SUPERball | High |
| **(d) N-drop reusability** — same specimen, **N = 20** drops from **h = 3 m**, record cumulative damage and first failure | ADXL375 + ESP32; ≥5000 fps video; photogate sync; post-drop dimensional inspection; optional tendon load cell for first/last-drop comparison | Cumulative residual strain, drift in peak **g**, drop count at first failure; compare to **Pajunen 2019** repeated-impact benchmark (**2.28% total remaining strain after 24 impacts**, ~0.11% per impact average) and to Zhang 2022’s much lower repeated-drop durability (~5 drops for silicone-lattice prototypes, ~10 before notable steel-spring damage) (pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 5-7, zhang2022designofimpactresistant pages 25-29, zhang2022designofimpactresistanta pages 25-29) | **Moderate-high** — time-consuming but simple; no extra fabrication beyond one or two spare specimens | Addresses reusability, creep, joint pull-out, and whether passive printed TPU joints fail in a mode relevant to future actuated landers | High |
| **(e) Worst-case orientation** — test **vertex-down / face-down / edge-down** (or closest geometric analogs) | ADXL375 + ESP32; ≥5000 fps video; photogate sync | Orientation sensitivity envelope: peak **g**, contact time, rebound, apparent effective stiffness **k_eff** from video/accelerometer fit; compare against Zhang 2022’s 22 in lander orientation results, where **closed face** was softest (**k ≈ 7.0 kN/m, F ≈ 360 N**) and **double rod** stiffest (**k ≈ 15.4 kN/m, F ≈ 524 N**) (zhang2022designofimpactresistanta pages 33-37, zhang2022designofimpactresistant pages 33-37) | **High** — only requires a repeatable release fixture/orientation jig | Tests whether the passive cell’s landing performance is dominated by orientation, a major concern for extrapolation to lander use | Medium-high |
| **(f) Quasi-static vs impact stiffness gap** — measure one tendon quasi-statically, then infer dynamic **k** from drop response | Instron-class tensile test (or equivalent) for tendon coupon; ADXL375 + ESP32; ≥5000 fps video; photogate sync | Ratio **k_dynamic / k_quasi-static** for the same TPU tendon; compare with published TPU/NinjaFlex-like data showing dynamic modulus about **2×** quasi-static (**~27 MPa vs ~13.5 MPa** in compression) (trzaskowski2025physicomechanicalpropertiesof pages 13-14, bustihan2025reusable3dprintedthermoplastic pages 2-4, trzaskowski2025physicomechanicalpropertiesof pages 8-13) | **Moderate** — requires off-board mechanical test access, but only one coupon/tendon | Directly bounds rate-dependence, the main small-scale scaling problem when using TPU 85A instead of SUPERball’s cable system | Medium |


*Table: This table summarizes six low-replicate validation experiments that can be run on the passive PETG+TPU tensegrity article to strengthen tech-transfer claims toward SUPERball-style actuated landers. It highlights the metric each test yields, the literature comparator, the concern addressed, and which experiments are highest leverage.*

### Highest-Leverage Experiments

The two highest-leverage single experiments are:

**(a) Single-tendon force trace.** This produces the most directly comparable metric to the SUPERball literature — peak cable force as a function of impact velocity. Normalizing measured per-tendon force by m·g·√(2h/g) (or equivalently by impact momentum m·v) allows order-of-magnitude comparison against Vespignani's ~950 N at 8 m/s and the earlier SUPERball cable tension requirements of 75–250 N (sunspiral2015superballbotstructuresa pages 80-83, sunspiral2015superballbotstructures pages 80-83). For the passive article (m ≈ 0.5 kg, h = 3 m, v ≈ 7.67 m/s), total impact momentum is ~3.8 N·s; if distributed across ~6 engaged tendons, per-tendon impulse is ~0.6 N·s, suggesting peak forces of order 5–50 N depending on contact time and stiffness.

**(b) Cable-stiffness sensitivity sweep.** Printing three specimens with TPU tendon diameters Ø = {1.5, 2.5, 4.0} mm spans approximately a decade of stiffness (k ∝ d², giving approximately 210, 590, and 1510 N/m). Measuring peak payload g versus k tests whether the Vespignani-style **non-monotonic optimum** in landing severity versus cable stiffness exists at small scale, which is the single most transferable design insight from the SUPERball simulation literature (sunspiral2015superballbotstructures pages 80-83, sunspiral2015superballbotstructuresb pages 75-80).

Together, experiments (a) and (b) provide the cable-force and stiffness-sensitivity data that are the minimum viable bridge metrics between the passive demo and the SUPERball-class landing literature.

---

## 6. Bottom-Line Recommendation

The passive PETG+TPU tensegrity egg-drop demo should position itself as a **"passive scale-model precursor to SUPERball-v2-class actuated landers"** rather than a standalone impact-absorber benchmark, because the six-bar icosahedral topology, cable stiffness range (~850 N/m for a Ø 3 mm TPU tendon), and achievable impact velocities (~7.7 m/s at h = 3 m) place it squarely within the parameter space explored by SUPERball's NIAC-funded landing analyses (sunspiral2015superballbotstructures pages 80-83, sunspiral2015superballbotstructuresb pages 80-83, sunspiral2015superballbotstructuresb pages 75-80). However, this positioning is credible only if three **minimum viable design changes** are implemented now: (1) hollow struts with a standardized end-cap motor interface, (2) at least one dual-purpose anchor that accepts both printed TPU tendons and swaged cable terminations, and (3) a pre-instrumented payload cradle with ADXL375 + ESP32 provisions (sabelhaus2014hardwaredesignandb pages 1-2, sabelhaus2014hardwaredesignand pages 1-2, chen2017softsphericaltensegrity pages 3-5). The **minimum viable validations** are experiments (a) and (b) above — a single-tendon force trace at h = 1–3 m drops and a three-specimen cable-stiffness sweep — which together produce the normalized peak cable force and the stiffness-sensitivity curve needed to directly reference Vespignani et al. (2018) and SunSpiral et al. (2015) in a future ASME JMD or RA-L submission (sunspiral2015superballbotstructuresa pages 80-83, sunspiral2015superballbotstructuresb pages 75-80). Without these changes and measurements, the passive demo risks being cited only as a classroom demonstration rather than as a precursor dataset for actuated planetary lander design.

References

1. (sabelhaus2014hardwaredesignandb pages 4-6): AP Sabelhaus, J Bruce, and K Caluwaerts. Hardware design and testing of superball, a modular tensegrity robot. Unknown journal, 2014.

2. (sabelhaus2014hardwaredesignanda pages 4-6): AP Sabelhaus, J Bruce, and K Caluwaerts. Hardware design and testing of superball, a modular tensegrity robot. Unknown journal, 2014.

3. (sunspiral2015superballbotstructures pages 80-83): V SunSpiral, A Agogino, and D Atkinson. Super ball bot-structures for planetary landing and exploration, niac phase 2 final report. Unknown journal, 2015.

4. (sunspiral2015superballbotstructuresa pages 80-83): V SunSpiral, A Agogino, and D Atkinson. Super ball bot-structures for planetary landing and exploration, niac phase 2 final report. Unknown journal, 2015.

5. (sabelhaus2014hardwaredesignandb pages 1-2): AP Sabelhaus, J Bruce, and K Caluwaerts. Hardware design and testing of superball, a modular tensegrity robot. Unknown journal, 2014.

6. (sabelhaus2014hardwaredesignand pages 1-2): AP Sabelhaus, J Bruce, and K Caluwaerts. Hardware design and testing of superball, a modular tensegrity robot. Unknown journal, 2014.

7. (sabelhaus2015systemdesignand pages 3-4): Andrew P. Sabelhaus, Jonathan Bruce, Ken Caluwaerts, Pavlo Manovi, Roya Fallah Firoozi, Sarah Dobi, Alice M. Agogino, and Vytas SunSpiral. System design and locomotion of superball, an untethered tensegrity robot. 2015 IEEE International Conference on Robotics and Automation (ICRA), pages 2867-2873, May 2015. URL: https://doi.org/10.1109/icra.2015.7139590, doi:10.1109/icra.2015.7139590. This article has 287 citations.

8. (sabelhaus2015systemdesignand pages 1-2): Andrew P. Sabelhaus, Jonathan Bruce, Ken Caluwaerts, Pavlo Manovi, Roya Fallah Firoozi, Sarah Dobi, Alice M. Agogino, and Vytas SunSpiral. System design and locomotion of superball, an untethered tensegrity robot. 2015 IEEE International Conference on Robotics and Automation (ICRA), pages 2867-2873, May 2015. URL: https://doi.org/10.1109/icra.2015.7139590, doi:10.1109/icra.2015.7139590. This article has 287 citations.

9. (sunspiral2015superballbotstructuresb pages 80-83): V SunSpiral, A Agogino, and D Atkinson. Super ball bot-structures for planetary landing and exploration, niac phase 2 final report. Unknown journal, 2015.

10. (bruce2014superballexploringtensegrities pages 4-6): J Bruce, AP Sabelhaus, Y Chen, and D Lu. Superball: exploring tensegrities for planetary probes. Unknown journal, 2014.

11. (lu2014superballexploringtensegrities pages 4-6): D Lu, K Morse, S Milam, and K Caluwaerts. Superball: exploring tensegrities for planetary probes. Unknown journal, 2014.

12. (sabelhaus2015systemdesignand pages 2-3): Andrew P. Sabelhaus, Jonathan Bruce, Ken Caluwaerts, Pavlo Manovi, Roya Fallah Firoozi, Sarah Dobi, Alice M. Agogino, and Vytas SunSpiral. System design and locomotion of superball, an untethered tensegrity robot. 2015 IEEE International Conference on Robotics and Automation (ICRA), pages 2867-2873, May 2015. URL: https://doi.org/10.1109/icra.2015.7139590, doi:10.1109/icra.2015.7139590. This article has 287 citations.

13. (sunspiral2015superballbotstructuresb pages 90-95): V SunSpiral, A Agogino, and D Atkinson. Super ball bot-structures for planetary landing and exploration, niac phase 2 final report. Unknown journal, 2015.

14. (sunspiral2015superballbotstructuresa pages 90-95): V SunSpiral, A Agogino, and D Atkinson. Super ball bot-structures for planetary landing and exploration, niac phase 2 final report. Unknown journal, 2015.

15. (sunspiral2015superballbotstructures pages 90-95): V SunSpiral, A Agogino, and D Atkinson. Super ball bot-structures for planetary landing and exploration, niac phase 2 final report. Unknown journal, 2015.

16. (zhang2022designofimpactresistant pages 22-25): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

17. (zhang2022designofimpactresistanta pages 22-25): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

18. (zhang2022designofimpactresistanta pages 93-97): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

19. (zhang2022designofimpactresistant pages 93-97): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

20. (bustihan2025reusable3dprintedthermoplastic pages 2-4): Alin Bustihan, Razvan Hirian, and Ioan Botiz. Reusable 3d-printed thermoplastic polyurethane honeycombs for mechanical energy absorption. Polymers, 17:3035, Nov 2025. URL: https://doi.org/10.3390/polym17223035, doi:10.3390/polym17223035. This article has 3 citations.

21. (trzaskowski2025physicomechanicalpropertiesof pages 13-14): Maciej Trzaskowski, Gen Tanabe, Hiroshi Churei, Toshiaki Ueno, Michał Ziętala, Bartłomiej Wysocki, Judyta Sienkiewicz, Agata Szczesio-Włodarczyk, Jerzy Sokołowski, Ewa Czochrowska, Małgorzata Zadurska, Elżbieta Mierzwińska-Nastalska, Jolanta Kostrzewa-Janicka, and Katarzyna Mańka-Malara. Physico-mechanical properties of 3d-printed filament materials for mouthguard manufacturing. Polymers, 17:2190, Aug 2025. URL: https://doi.org/10.3390/polym17162190, doi:10.3390/polym17162190. This article has 3 citations.

22. (zhang2022designofimpactresistanta pages 19-22): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

23. (zhang2022designofimpactresistant pages 19-22): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

24. (sunspiral2015superballbotstructuresb pages 75-80): V SunSpiral, A Agogino, and D Atkinson. Super ball bot-structures for planetary landing and exploration, niac phase 2 final report. Unknown journal, 2015.

25. (pajunen2019designandimpact pages 7-8): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

26. (pajunen2019designandimpact pages 5-7): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

27. (zhang2022designofimpactresistant pages 25-29): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

28. (zhang2022designofimpactresistanta pages 25-29): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

29. (zhang2022designofimpactresistant pages 73-77): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

30. (chen2017softsphericaltensegrity pages 3-5): Lee-Huang Chen, Kyunam Kim, Ellande Tang, Kevin Li, Richard House, Edward Liu Zhu, Kimberley Fountain, Alice M. Agogino, Adrian Agogino, Vytas Sunspiral, and Erik Jung. Soft spherical tensegrity robot design using rod-centered actuation and control. Journal of Mechanisms and Robotics, Mar 2017. URL: https://doi.org/10.1115/1.4036014, doi:10.1115/1.4036014. This article has 161 citations and is from a domain leading peer-reviewed journal.

31. (sabelhaus2014hardwaredesignand pages 4-6): AP Sabelhaus, J Bruce, and K Caluwaerts. Hardware design and testing of superball, a modular tensegrity robot. Unknown journal, 2014.

32. (chen2017softsphericaltensegrity pages 6-7): Lee-Huang Chen, Kyunam Kim, Ellande Tang, Kevin Li, Richard House, Edward Liu Zhu, Kimberley Fountain, Alice M. Agogino, Adrian Agogino, Vytas Sunspiral, and Erik Jung. Soft spherical tensegrity robot design using rod-centered actuation and control. Journal of Mechanisms and Robotics, Mar 2017. URL: https://doi.org/10.1115/1.4036014, doi:10.1115/1.4036014. This article has 161 citations and is from a domain leading peer-reviewed journal.

33. (sabelhaus2014hardwaredesignanda pages 1-2): AP Sabelhaus, J Bruce, and K Caluwaerts. Hardware design and testing of superball, a modular tensegrity robot. Unknown journal, 2014.

34. (zhang2022designofimpactresistanta pages 33-37): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

35. (zhang2022designofimpactresistant pages 33-37): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

36. (zhang2022designofimpactresistant pages 81-86): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

37. (zhang2022designofimpactresistanta pages 81-86): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

38. (trzaskowski2025physicomechanicalpropertiesof pages 8-13): Maciej Trzaskowski, Gen Tanabe, Hiroshi Churei, Toshiaki Ueno, Michał Ziętala, Bartłomiej Wysocki, Judyta Sienkiewicz, Agata Szczesio-Włodarczyk, Jerzy Sokołowski, Ewa Czochrowska, Małgorzata Zadurska, Elżbieta Mierzwińska-Nastalska, Jolanta Kostrzewa-Janicka, and Katarzyna Mańka-Malara. Physico-mechanical properties of 3d-printed filament materials for mouthguard manufacturing. Polymers, 17:2190, Aug 2025. URL: https://doi.org/10.3390/polym17162190, doi:10.3390/polym17162190. This article has 3 citations.