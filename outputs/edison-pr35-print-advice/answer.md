Question: 
We are 3D-printing small tensegrity structures (T3 prism, ~80 mm footprint x ~104 mm tall) on a Bambu Lab H2D
dual-extruder FFF printer: rigid PLA struts (extruder 1) plus flexible TPU 85A tendons/cables (extruder 2,
"Direct Drive TPU High Flow" nozzle slot), printed together in one job with breakaway PLA support pillars.
The TPU tendons are thin near-vertical cylinders (~4.8 mm diameter, up to ~100 mm tall, tilted ~20 deg from vertical).

Recurring print-quality problems we need literature-backed advice on:

1) Moisture bubbling in TPU 85A: diagonal/vertical TPU tendons show severe bubbles and surface imperfections
   whenever filament humidity exceeds ~10% RH; we already dry-cycle the filament repeatedly and wait for <8% RH
   before printing, but ambient humidity is high in summer and the problem recurs mid-print. What does the
   literature/industry practice say about (a) drying protocols for TPU shore 85A (temperature, duration, desiccant
   dry-box feeding during the print, PTFE feed path), (b) print-parameter mitigation of moisture foaming (nozzle
   temperature, volumetric flow, retraction, pressure advance), and (c) quantitative moisture-content thresholds
   for polyurethane elastomer extrusion (e.g. wt% water where foaming onsets)?

2) Mechanical instability of thin, tall flexible columns during printing: a ~4.8 mm diameter TPU column resting on
   the build plate wobbles when the nozzle touches it; the nozzle visibly pushes the printed tendon around,
   producing lateral offsets and surface defects. What stabilization strategies are documented (sacrificial cages,
   guide pillars, draft shields, printing sequence changes, z-hop, reduced flow/speed for thin columns,
   part cooling), and are there published models or simulations of nozzle-part interaction forces for compliant
   thin-walled or slender features in FFF?

3) Scale effects: we recently scaled the structure down, which worsened printability. Are there published
   printability/feature-size limits for TPU 85A thin cylinders in FFF (minimum diameter vs height, slenderness
   limits), and guidance on how much upscaling improves success probability?

4) Process simulation: what physics-based simulation approaches are used to predict FFF print failures for
   slender/flexible features BEFORE printing — e.g. layer-by-layer thermo-mechanical FEA (element activation),
   simplified beam/buckling models of partially printed columns, nozzle-impact lateral deflection models,
   viscoelastic sag models for elastomers, moisture-diffusion/outgassing models for foaming defects — and which
   are practical for a small research team to run headlessly (open-source preferred, e.g. CalculiX, Elmer, FEniCS)?

Please give concrete, actionable recommendations (parameter ranges, drying setpoints, geometric rules of thumb,
simulation methods with references) prioritized by expected impact on our failure modes.


# Literature-backed process plan for TPU-85A tensegrity printing

## Executive conclusion

Your two dominant mechanisms are probably **(1) moisture re-uptake during the job** and **(2) lateral compliance of the partially printed tendon under nozzle contact**. Treat them independently: first create a continuously dry filament path, then mechanically stabilize the tendon or ensure the nozzle never touches it. Parameter tuning alone is unlikely to cure a 4.8 mm × 100 mm TPU column whose height/diameter ratio is about 21.

The most useful immediate actions are summarized below.

| Priority | Intervention | Concrete starting settings/design | Expected mechanism/benefit | Evidence strength or caveat |
|---|---|---|---|---|
| 1 | Continuous dry feed during the entire print | Feed TPU 85A from a sealed heated/desiccant dry-box, not open air; keep a sealed PTFE guide path from dry-box to extruder inlet; minimize exposed path length; recharge desiccant aggressively in summer | Prevents mid-print moisture re-uptake, the most likely cause of bubbles/voids on long TPU tendons; PTFE guidance also improves compliant-filament feeding stability | Strong practical basis for TPU FFF; 85A study recommends humidity control, drying, and PTFE guides; TPU/polyester urethanes are hygroscopic and humidity-sensitive (abboodi2026designmanufacturingand pages 6-8, tian2016microstructurechangesin pages 5-8, tian2016microstructurechangesin pages 1-3) |
| 2 | Dry TPU by an evidence-based protocol before loading | Start with either 50 C for 5 h or 80 C for 16 h under vacuum, choosing the highest temperature compatible with spool/manufacturer limits; if spool cannot tolerate 80 C, use the lower setting plus longer time and immediate transfer to sealed dry-box | Reduces absorbed water before melt processing, lowering bubble formation and hydrolytic damage | Both settings are reported in peer-reviewed TPU/85A contexts; 80 C/16 h is closer to polymer-processing practice, 50 C/5 h is directly reported for 85A FFF. Not a universal rule for every brand/spool (yeh2021effectofextrusion pages 2-4, abboodi2026designmanufacturingand pages 6-8) |
| 3 | Verify dryness by moisture measurement, not ambient RH alone | Use spool mass tracking before/after drying and, if available, Karl Fischer moisture testing on filament samples; treat box RH only as a process indicator, not proof of low polymer moisture | RH in the enclosure does not directly equal water wt% in the polymer; measurement-based acceptance avoids false confidence when summer humidity is high | Important caveat: no universal foaming-onset wt% was found in the retrieved literature, so direct moisture verification is more defensible than relying on RH thresholds alone (yeh2021effectofextrusion pages 2-4, tian2016microstructurechangesin pages 5-8, tian2016microstructurechangesin pages 1-3) |
| 4 | Conservative TPU melt temperature | Start tendon printing at 225-235 C; if flow remains stable, step down in 5 C increments to the lowest temperature that still gives smooth extrusion and bonding; avoid running unnecessarily hot | Lower melt temperature can reduce moisture-driven outgassing severity and thermal degradation while preserving flow | 85A-related sources report 200 C in extrusion and 225-240 C in FFF depending on setup; exact optimum is machine/material specific, so this is a practical starting window, not a universal setpoint (yeh2021effectofextrusion pages 2-4, abboodi2026designmanufacturingand pages 6-8) |
| 5 | Slow tendon wall speed and cap volumetric flow | Start at 10-15 mm/s on tendon perimeters/walls; cap TPU volumetric flow conservatively relative to your nozzle and layer height; keep acceleration/jerk low on tendon moves | Reduces pressure spikes, nozzle contact severity, and dynamic wobble of slender hot columns; gives more time for layer cooling | Strong generic FFF troubleshooting support for slowing small/thin features; 85A study found ~15 mm/s optimal for its setup. The exact volumetric-flow cap is an engineering start point (abboodi2026designmanufacturingand pages 6-8, loh2020anoverviewof pages 19-22, loh2020anoverviewof pages 14-17, loh2020anoverviewof pages 17-19) |
| 6 | Use moderate cooling after first layers | Disable or reduce fan for first layers if needed for adhesion, then run ~30-40% fan on TPU tendon printing; if columns still smear, increase cooling incrementally while checking interlayer bonding | Faster skin solidification raises local stiffness and reduces nozzle-induced dragging/buckling of tall TPU features | 30-40% fan is reported for 85A TPU printing; generic FFF literature supports more cooling and lower speed for small features. Exact fan optimum remains printer- and duct-dependent (abboodi2026designmanufacturingand pages 6-8, loh2020anoverviewof pages 14-17, loh2020anoverviewof pages 17-19) |
| 7 | Minimize or disable TPU retraction; tune pressure advance carefully | Start with retraction disabled or minimal; then calibrate pressure advance/linear advance cautiously to reduce ooze without pressure oscillation; avoid aggressive retract/unretract on flexible filament | Reduces filament stretching, under/over-pressure pulses, and nozzle dwell/contact disturbances on the slender tendon | Direct 85A TPU evidence recommends disabling retraction; pressure-advance tuning is an engineering extension consistent with the same mechanism but not directly quantified in the retrieved papers (abboodi2026designmanufacturingand pages 6-8) |
| 8 | Add sacrificial PLA stabilization geometry around each tendon | Add a light PLA sacrificial cage or 3-4 guide towers around each tendon with sparse breakaway ties every 10-20 mm in Z; add a small brim/foot at the tendon base if geometry allows | Raises effective lateral support during printing, reducing wobble, Euler-type instability, and nozzle knock-off on compliant columns | Mechanism is strongly supported by beam/buckling logic and generic support guidance, but the exact cage/tie geometry is an engineering solution rather than a published universal recipe for TPU cylinders (he2026investigationonbridging pages 15-17, he2026investigationonbridging pages 4-6, loh2020anoverviewof pages 19-22, loh2020anoverviewof pages 5-9) |
| 9 | Avoid nozzle collisions by path planning | Enable z-hop around 0.4-0.8 mm for travel over printed tendons; avoid travel paths that cross tendons; prefer outer-to-inner or sequence choices that keep the nozzle off hot TPU whenever possible | Reduces direct nozzle-part contact, the visible source of lateral offsets and surface scars | Z-hop is directly recommended in FFF troubleshooting; the 0.4-0.8 mm range is a practical starting value for a 0.4 mm nozzle, not a published universal limit (loh2020anoverviewof pages 19-22) |
| 10 | Increase effective layer cooling time | Print multiple identical structures, dummy cooling towers, or sacrificial features so each TPU tendon layer has more time to stiffen before the nozzle returns | Longer interlayer time increases modulus before the next contact/pass, reducing smear and wobble | Supported by generic FFF guidance to print multiple parts/smaller-feature cooling strategies; especially relevant for your near-vertical repeated columns (loh2020anoverviewof pages 17-19, loh2020anoverviewof pages 14-17) |
| 11 | Respect scale effects; upsize critical tendons first | If allowable, test tendon diameters in the 6-8 mm range or add lateral ties/intermediate braces; if not, increase local base diameter or use periodic PLA ties; prioritize scaling diameter over minor height changes because bending stiffness scales as d^4 for a circular column | Small diameter reductions rapidly collapse lateral stiffness and increase sensitivity to nozzle touch; modest diameter increases can greatly improve print success | The d^4 scaling is standard beam mechanics; no universal published diameter/height printability limit for 85A TPU cylinders was found, so these are engineering rules of thumb informed by mechanics and TPU geometry studies (kumar2022energyabsorptionand pages 4-7, he2026investigationonbridging pages 15-17) |
| 12 | Use nozzle-multiple-aware geometry and bead layout | Keep wall/feature dimensions aligned with nozzle/bead width multiples; avoid under-resolved thin segments; if using 0.4 mm nozzle, ensure slicer can realize the tendon shell plan cleanly | Prevents unstable bead placement and inconsistent thin-wall toolpaths that worsen defects on slender features | Strong generic FFF evidence for thin-feature reliability; not TPU-specific but highly relevant to small tendon geometry (loh2020anoverviewof pages 19-22, loh2020anoverviewof pages 14-17, loh2020anoverviewof pages 17-19) |
| 13 | Simulation ladder: start simple, escalate only if needed | First: reduced-order beam/contact model for partial-height tendon with estimated nozzle lateral load and time-evolving modulus; Second: G-code-driven thermo-mechanical FEA with element activation; Third: moisture diffusion/outgassing model only if drying/process controls still fail | Gives a practical pre-print failure screen with the best effort-to-value ratio for a small team | Strong evidence exists for reduced-order cooling/buckling models and for thermo-mechanical FEA; moisture-foaming simulation is much less turnkey in the retrieved literature (he2026investigationonbridging pages 19-22, he2026investigationonbridging pages 17-19, he2026investigationonbridging pages 4-6, farh2025thermomechanicalapproachto pages 13-15, farh2025thermomechanicalapproachto pages 1-2, farh2025thermomechanicalapproachto pages 12-13) |
| 14 | Open-source simulation implementation path | Implement reduced-order beam/contact in Python/FEniCS first; use CalculiX or Elmer for transient thermal + structural element-activation workflows driven by parsed G-code; reserve full viscoelastic TPU constitutive modeling for later using an Ogden-type hyperelastic model plus simple time dependence | Allows headless, automatable screening without starting from the heaviest coupled model | The FEA validation evidence is from ABAQUS, not open-source; mapping to CalculiX/Elmer/FEniCS is a practical recommendation, while Ogden-plus-viscoelastic TPU modeling is supported conceptually by published TPU FE work (farh2025thermomechanicalapproachto pages 1-2, farh2025thermomechanicalapproachto pages 7-9, farh2025thermomechanicalapproachto pages 9-10, kumar2022energyabsorptionand pages 8-11, kumar2022energyabsorptionand pages 14-16) |


*Table: This table prioritizes the highest-impact interventions for your 85A TPU tensegrity print, from moisture control to geometric stabilization and simulation. It separates literature-backed settings from engineering starting points where the published evidence is indirect or no universal limit was found.*

## 1. Moisture bubbling

### 1.1 Drying and handling

Two peer-reviewed protocols bracket a reasonable starting range:

* A TPU extrusion study specifically processed **85A and 90A grades after vacuum drying at 80°C for 16 h**; 85A/90A were extruded at 200°C to avoid degradation. Water was deliberately excluded because it acts as a co-blowing agent. This is the stronger polymer-processing protocol, provided the filament spool and additives tolerate 80°C. (yeh2021effectofextrusion pages 2-4)
* A TPU-85A FFF study used **50°C for 5 h**, recommended humidity below 20%, and used PTFE guidance; its printing window was 225–240°C. (abboodi2026designmanufacturingand pages 6-8)

For your long summer prints, drying and then exposing the spool to room air is insufficient. Transfer the dried spool directly into a **sealed desiccant or actively heated dry box and print from that box**. Continue the PTFE tube as close to the extruder inlet as practical, seal its box penetration, and minimize exposed filament. The PTFE path should have generous bend radii and low drag because 85A filament can buckle or stretch in a restrictive path.

Use the filament manufacturer's limit if it is lower than 80°C. A practical qualification procedure is:

1. Dry at **50–55°C for 6–8 h** in moving dry air as the low-risk baseline.
2. If bubbling remains, test **70–80°C under vacuum or very dry air for 8–16 h**, after verifying spool dimensional stability.
3. Weigh the spool before drying, after drying, and after a standardized ambient exposure. A 0.1 g balance is useful for comparative control, although spool mass makes this less sensitive than Karl Fischer titration.
4. For defensible moisture specification, send filament snips for **Karl Fischer water analysis**. Box RH is a gas-phase measurement and does not establish polymer water concentration.

Polyester polyurethane is particularly vulnerable to humidity-driven hydrolysis: exposure at increasing RH caused progressively greater chain scission and microphase reorganization, with severe molecular-weight loss under 80% RH/70°C aging. That is longer-term aging rather than an FFF foaming threshold, but it confirms that repeated hot/wet exposure can damage the polymer as well as create bubbles. (tian2016microstructurechangesin pages 5-8, tian2016microstructurechangesin pages 1-3)

### 1.2 Moisture-content threshold

The retrieved literature did **not** establish a universal wt% water at which commercial TPU-85A begins visibly foaming in FFF. Such a threshold depends on polyester versus polyether TPU chemistry, additives, residence time, melt temperature, pressure drop, nozzle geometry, and the detection criterion. Therefore, do not translate your observed “10% RH” directly into a water wt% threshold.

A suitable internal acceptance study is to condition samples to several known moisture levels, measure each by Karl Fischer, and extrude a fixed single-wall coupon at fixed temperature and flow. Record mass loss, acoustic popping, optical bubble count, and extrudate density. This will generate a threshold for your exact filament/nozzle system rather than importing an uncertain resin-pellet specification.

### 1.3 Printing parameters

Use the lowest temperature that produces continuous, well-bonded flow. Begin at **225–230°C**, then change in **5°C increments**. The 85A FFF study found 235°C optimal and 225–240°C acceptable, whereas resin extrusion at lower throughput used 200°C; this difference demonstrates why temperature must be qualified on the actual machine. (yeh2021effectofextrusion pages 2-4, abboodi2026designmanufacturingand pages 6-8)

For the tendon perimeter, start with:

* **10–15 mm/s wall speed**;
* low acceleration on the tendon, approximately **300–800 mm/s²** as an engineering starting range;
* a conservative volumetric-flow cap established by a dry-filament flow ladder;
* **30–40% part cooling** after the adhesion-critical first layers;
* retraction disabled, or the minimum that a stringing trial proves necessary;
* pressure advance recalibrated with dry TPU and reduced if corners exhibit pressure pulses.

The published 85A work found approximately 15 mm/s optimal, 30–40% fan, and recommended disabling retraction because stretching and pressure disturbances impaired flexible-filament delivery. (abboodi2026designmanufacturingand pages 6-8) Lower temperature can reduce vapor expansion and thermal degradation, but it cannot compensate for wet polymer. Likewise, reducing volumetric flow mainly improves pressure and thermal uniformity; it is not a substitute for dry feeding.

## 2. Stabilizing the tall TPU tendons

### 2.1 Geometry and toolpath changes

The strongest intervention is a **sacrificial PLA guide structure**, not merely a draft shield. Use three or four thin PLA towers surrounding each tendon, connected to one another as a cage and connected to the TPU by tiny breakaway contacts every approximately **10–20 mm vertically**. Locate contacts where removal marks are acceptable. Make each neck only as large as required to resist lateral motion and experimentally tune the PLA–TPU contact, since intermaterial adhesion varies.

Alternative geometries are:

* two opposed PLA guide pillars with small collars or tabs around the tendon;
* a temporary helical cage that stays clear of the tendon except at sparse breakaway points;
* a broad TPU base flare or brim, trimmed afterward;
* temporary TPU-to-PLA lateral ties located at future cable attachment nodes.

A free-standing draft shield improves thermal conditions but supplies almost no lateral restraint unless connected; therefore, call it a **cage or guide**, not simply a shield.

Enable collision avoidance:

* **Z-hop 0.4–0.8 mm** on travel as a starting trial;
* prohibit or minimize travel across the tendons;
* avoid combing through TPU features;
* keep seam placement consistent and preferably toward a supported side;
* inspect sliced G-code for every tool change and purge/prime move near a tendon.

Z-hop, reduced speed, increased cooling, and dimensions matched to nozzle-width multiples are documented general FFF remedies for scars, vibration, and small-feature deformation. Printing multiple objects or cooling towers also increases the time available for a small layer to stiffen. (loh2020anoverviewof pages 19-22, loh2020anoverviewof pages 14-17, loh2020anoverviewof pages 17-19)

Sequence the job so the nozzle does not repeatedly shuttle between widely separated tendons if this creates crossing moves. Conversely, if a single tendon overheats because each layer is extremely short, rotate among several tendons or a cooling tower. The optimal sequence is therefore the one that provides sufficient layer time **without crossing completed columns**.

### 2.2 Mechanical interpretation

For a circular cantilever, lateral tip compliance under force is

\[
\delta=\frac{F L^3}{3EI},\qquad I=\frac{\pi d^4}{64}.
\]

Thus lateral stiffness scales as \(d^4/L^3\). At fixed height, increasing diameter from 4.8 to 6.0 mm multiplies bending stiffness by about **2.44**; increasing to 7.2 mm multiplies it by about **5.06**. Conversely, a 20% geometric downscale reduces lateral stiffness, relative to a similarly applied force and unchanged modulus, to \(0.8^4=0.41\) if only diameter is considered. This explains the abrupt loss of printability after scaling.

The relevant modulus is not room-temperature catalog modulus: the top layers are hot and time-dependent. Published reduced-order FFF models combine transient cooling, temperature-dependent modulus, thermal stress, beam deflection, and Euler-type instability; one analytical framework obtained temperature-fit \(R^2\) around 0.94 and curvature \(R^2\) around 0.83. (he2026investigationonbridging pages 19-22, he2026investigationonbridging pages 15-17) Although developed for PLA bridges rather than TPU columns, the modeling architecture is directly transferable after calibrating TPU modulus versus temperature and time.

Direct, validated literature on **nozzle-contact force against free-standing TPU-85A cylinders** appears sparse. Most nozzle-flow models address melt pressure or bead formation, not accidental mechanical impact. Accordingly, measure the effective force experimentally: mount a short printed tendon or instrumented surrogate on a small load cell, reproduce a known lateral nozzle overlap at several speeds, and fit peak force and contact duration. Even a rough measured force is much better than an assumed value.

## 3. Feature-size and scale limits

No universal published minimum diameter-versus-height envelope was found for vertical TPU-85A cylinders. A TPU lattice study printed with a 0.4 mm nozzle, 0.2 mm layers, 230°C, and about 18.3 mm/s and reported a 0.2 mm minimum wall in its particular lattice design; that is not evidence that a 0.2 mm wall can form a stable 100 mm free-standing column. (kumar2022energyabsorptionand pages 4-7)

Generic FFF guidance recommends making thin walls multiples of nozzle/extrusion width and increasing features that fall below the printable bead dimension. (loh2020anoverviewof pages 19-22, loh2020anoverviewof pages 14-17) For your case, resolution is not the controlling limit: **structural compliance and repeated nozzle contact are**.

Use an empirical printability map rather than a single minimum diameter. Print cylinders at, for example:

* diameters **4.8, 6.0, 7.2, and 8.0 mm**;
* heights **25, 50, 75, and 100 mm**;
* both vertical and 20°-tilted configurations;
* with and without one intermediate guide at 50 mm.

Score completion, maximum centerline error, surface roughness, and peak wobble from video. Based on \(d^4\) scaling, **6–7.2 mm** is the first rational upscaling trial if the tensegrity mechanics permit it. If diameter cannot change, an intermediate lateral tie effectively reduces unsupported length: halving free length theoretically raises bending stiffness against a tip-type disturbance by approximately **8×** through the \(L^{-3}\) relationship.

## 4. Practical pre-print simulation hierarchy

### Level 1 — Python beam/contact screening

This offers the highest value for a small team. Represent each partially printed tendon as an inclined Timoshenko or Euler–Bernoulli beam whose length grows layer by layer. Apply:

* gravity;
* measured lateral nozzle force or prescribed nozzle interference/contact stiffness;
* base rotational compliance;
* temperature- and age-dependent \(E(z,t)\);
* optional geometric nonlinearity.

At each layer, calculate maximum deflection, nozzle clearance, and a buckling margin. Use Newton cooling initially,

\[
T(t)=T_\infty+(T_0-T_\infty)e^{-kt},
\]

then fit \(k\) from infrared or thermocouple data. Comparable analytical FFF work used time-varying temperature and modulus plus beam/buckling equations and validated them against imaging. (he2026investigationonbridging pages 19-22, he2026investigationonbridging pages 17-19, he2026investigationonbridging pages 13-15)

This can be implemented headlessly in NumPy/SciPy, FEniCSx, or a small custom finite-element code. Run parameter sweeps over diameter, tie spacing, nozzle force, cooling time, and toolpath order.

### Level 2 — Structural contact FEA

Use CalculiX or FEniCSx for a geometrically nonlinear beam/solid model. Activate tendon segments layer-by-layer, include a rigid nozzle surface with penalty contact, and assign a cooling-dependent elastic or hyperelastic modulus. This directly predicts whether a toolpath produces recoverable bending, accumulated offset, or contact with neighboring features.

For room-temperature TPU behavior, published FE work has used a **second-order Ogden hyperelastic model plus a time-dependent hysteresis network**. (kumar2022energyabsorptionand pages 8-11) For printing, this must be recalibrated at elevated temperature and short time scales; the published model itself lacked temperature dependence and did not perfectly capture all nonlinear TPU behavior. (kumar2022energyabsorptionand pages 14-16)

### Level 3 — Layer-by-layer thermo-mechanical FEA

A validated FFF framework parses G-code into time-resolved element activation, solves transient conduction with convection/radiation, and transfers temperature to a mechanical analysis for residual stress and warpage. It explicitly models printing, cooling, and detachment and achieved about **10.6% average displacement deviation** in its PLA validation. (farh2025thermomechanicalapproachto pages 1-2, farh2025thermomechanicalapproachto pages 12-13)

The governing thermal equation is

\[
\rho c\frac{\partial T}{\partial t}=\nabla\cdot(k\nabla T)+q,
\]

with elements activated when the deposition path reaches them. One element per filament cross-section produced less than approximately 2.1% mesh-related variation in that study, although this is not necessarily sufficient near local nozzle contact. (farh2025thermomechanicalapproachto pages 7-9, farh2025thermomechanicalapproachto pages 12-13)

**Open-source allocation:**

* **Elmer**: convenient for transient heat transfer; script activation/material state from G-code.
* **CalculiX**: useful for Abaqus-like structural input, nonlinear geometry, and contact; element activation will require generated step files or model-change scripting.
* **FEniCSx**: most flexible for custom activation, evolving domains, and moisture PDEs, but requires the most development.

None is a turnkey open-source FFF simulator. For this failure mode, couple Elmer thermal output to CalculiX structural analysis only after the reduced-order model proves that temperature history materially affects the decision.

### Level 4 — Moisture diffusion and foaming

Begin with Fickian radial diffusion in the filament,

\[
\frac{\partial C}{\partial t}=\nabla\cdot[D(T,C)\nabla C],
\]

using sorption-boundary data measured at relevant RH. Couple the computed nozzle-entry concentration to a lumped hot-end model containing desorption, vaporization, residence time, pressure, and bubble growth. Polyester-PU humid-aging evidence supports diffusion-coupled hydrolytic change, but it does not provide a ready-made FFF bubble-nucleation law. (tian2016microstructurechangesin pages 5-8, tian2016microstructurechangesin pages 8-10)

This model is lower priority because its necessary inputs—sorption isotherm, \(D(T,C)\), gas solubility, nucleation density, hot-end pressure history, and extensional rheology—are difficult to obtain. A Karl-Fischer-conditioned extrusion experiment will give useful operating limits much sooner.

## Recommended first experimental iteration

1. Vacuum/dry-air dry the TPU using the strongest spool-safe protocol, then transfer it without ambient exposure into a sealed actively dried feed box.
2. Use a sealed, low-drag PTFE path to the TPU extruder.
3. Print at **225–230°C, 10–15 mm/s tendon walls, 30–40% fan after the initial layers, minimal retraction**, and freshly calibrated pressure advance.
4. Add a three- or four-post PLA cage with breakaway ties at approximately **10–20 mm Z intervals** and a stabilized tendon foot.
5. Use **0.4–0.8 mm Z-hop**, remove crossing travels, and inspect tool-change moves.
6. If geometry may change, test **6.0 mm tendon diameter** first; it gives approximately 2.4× the bending stiffness of 4.8 mm at equal height.
7. Record dry-box RH, spool mass, print time, bubble onset height/time, nozzle temperature, and video-derived lateral displacement. These data support both root-cause separation and a useful reduced-order model.

The drying values, TPU process windows, cooling/retraction advice, generic thin-feature remedies, and thermo-mechanical modeling architecture have literature support. The cage spacing, Z-hop range, acceleration range, and 6–8 mm diameter trials are engineering starting points because the literature does not provide a validated universal printability envelope for 100 mm-tall TPU-85A cylinders.

References

1. (abboodi2026designmanufacturingand pages 6-8): Mohammed Abboodi and Marc Doumit. Design, manufacturing, and testing of a novel omnidirectional soft sleeve actuator. Scientific Reports, Feb 2026. URL: https://doi.org/10.1038/s41598-026-40604-5, doi:10.1038/s41598-026-40604-5. This article has 2 citations and is from a peer-reviewed journal.

2. (tian2016microstructurechangesin pages 5-8): Qiang Tian, Ivan Krakovský, Guanyun Yan, Liangfei Bai, Jiahui Liu, Guangai Sun, László Rosta, Bo Chen, and László Almásy. Microstructure changes in polyester polyurethane upon thermal and humid aging. Polymers, 8:197, May 2016. URL: https://doi.org/10.3390/polym8050197, doi:10.3390/polym8050197. This article has 45 citations.

3. (tian2016microstructurechangesin pages 1-3): Qiang Tian, Ivan Krakovský, Guanyun Yan, Liangfei Bai, Jiahui Liu, Guangai Sun, László Rosta, Bo Chen, and László Almásy. Microstructure changes in polyester polyurethane upon thermal and humid aging. Polymers, 8:197, May 2016. URL: https://doi.org/10.3390/polym8050197, doi:10.3390/polym8050197. This article has 45 citations.

4. (yeh2021effectofextrusion pages 2-4): Shu-Kai Yeh, Raghavendrakumar Rangappa, Ting-Hao Hsu, and Stephen Utomo. Effect of extrusion on the foaming behavior of thermoplastic polyurethane with different hard segments. Journal of Polymer Research, Jun 2021. URL: https://doi.org/10.1007/s10965-021-02604-z, doi:10.1007/s10965-021-02604-z. This article has 21 citations and is from a peer-reviewed journal.

5. (loh2020anoverviewof pages 19-22): Giselle Hsiang Loh, Eujin Pei, Joamin Gonzalez-Gutierrez, and Mario Monzón. An overview of material extrusion troubleshooting. Applied Sciences, 10:4776, Jul 2020. URL: https://doi.org/10.3390/app10144776, doi:10.3390/app10144776. This article has 170 citations.

6. (loh2020anoverviewof pages 14-17): Giselle Hsiang Loh, Eujin Pei, Joamin Gonzalez-Gutierrez, and Mario Monzón. An overview of material extrusion troubleshooting. Applied Sciences, 10:4776, Jul 2020. URL: https://doi.org/10.3390/app10144776, doi:10.3390/app10144776. This article has 170 citations.

7. (loh2020anoverviewof pages 17-19): Giselle Hsiang Loh, Eujin Pei, Joamin Gonzalez-Gutierrez, and Mario Monzón. An overview of material extrusion troubleshooting. Applied Sciences, 10:4776, Jul 2020. URL: https://doi.org/10.3390/app10144776, doi:10.3390/app10144776. This article has 170 citations.

8. (he2026investigationonbridging pages 15-17): Hao He, Zhi Zhu, Y. X. Zhang, and Richard (Chunhui) Yang. Investigation on bridging defects in 3d-printed polylactic acid beams using fused filament fabrication. Polymers, 18:261, Jan 2026. URL: https://doi.org/10.3390/polym18020261, doi:10.3390/polym18020261. This article has 0 citations.

9. (he2026investigationonbridging pages 4-6): Hao He, Zhi Zhu, Y. X. Zhang, and Richard (Chunhui) Yang. Investigation on bridging defects in 3d-printed polylactic acid beams using fused filament fabrication. Polymers, 18:261, Jan 2026. URL: https://doi.org/10.3390/polym18020261, doi:10.3390/polym18020261. This article has 0 citations.

10. (loh2020anoverviewof pages 5-9): Giselle Hsiang Loh, Eujin Pei, Joamin Gonzalez-Gutierrez, and Mario Monzón. An overview of material extrusion troubleshooting. Applied Sciences, 10:4776, Jul 2020. URL: https://doi.org/10.3390/app10144776, doi:10.3390/app10144776. This article has 170 citations.

11. (kumar2022energyabsorptionand pages 4-7): Ajeet Kumar, Luca Collini, Chiara Ursini, and Jeng-Ywan Jeng. Energy absorption and stiffness of thin and thick-walled closed-cell 3d-printed structures fabricated from a hyperelastic soft polymer. Materials, 15:2441, Mar 2022. URL: https://doi.org/10.3390/ma15072441, doi:10.3390/ma15072441. This article has 40 citations.

12. (he2026investigationonbridging pages 19-22): Hao He, Zhi Zhu, Y. X. Zhang, and Richard (Chunhui) Yang. Investigation on bridging defects in 3d-printed polylactic acid beams using fused filament fabrication. Polymers, 18:261, Jan 2026. URL: https://doi.org/10.3390/polym18020261, doi:10.3390/polym18020261. This article has 0 citations.

13. (he2026investigationonbridging pages 17-19): Hao He, Zhi Zhu, Y. X. Zhang, and Richard (Chunhui) Yang. Investigation on bridging defects in 3d-printed polylactic acid beams using fused filament fabrication. Polymers, 18:261, Jan 2026. URL: https://doi.org/10.3390/polym18020261, doi:10.3390/polym18020261. This article has 0 citations.

14. (farh2025thermomechanicalapproachto pages 13-15): Mahmoud Farh and Viktor Gribniak. Thermo-mechanical approach to material extrusion process during fused filament fabrication of polymeric samples. Materials, 18:4537, Sep 2025. URL: https://doi.org/10.3390/ma18194537, doi:10.3390/ma18194537. This article has 3 citations.

15. (farh2025thermomechanicalapproachto pages 1-2): Mahmoud Farh and Viktor Gribniak. Thermo-mechanical approach to material extrusion process during fused filament fabrication of polymeric samples. Materials, 18:4537, Sep 2025. URL: https://doi.org/10.3390/ma18194537, doi:10.3390/ma18194537. This article has 3 citations.

16. (farh2025thermomechanicalapproachto pages 12-13): Mahmoud Farh and Viktor Gribniak. Thermo-mechanical approach to material extrusion process during fused filament fabrication of polymeric samples. Materials, 18:4537, Sep 2025. URL: https://doi.org/10.3390/ma18194537, doi:10.3390/ma18194537. This article has 3 citations.

17. (farh2025thermomechanicalapproachto pages 7-9): Mahmoud Farh and Viktor Gribniak. Thermo-mechanical approach to material extrusion process during fused filament fabrication of polymeric samples. Materials, 18:4537, Sep 2025. URL: https://doi.org/10.3390/ma18194537, doi:10.3390/ma18194537. This article has 3 citations.

18. (farh2025thermomechanicalapproachto pages 9-10): Mahmoud Farh and Viktor Gribniak. Thermo-mechanical approach to material extrusion process during fused filament fabrication of polymeric samples. Materials, 18:4537, Sep 2025. URL: https://doi.org/10.3390/ma18194537, doi:10.3390/ma18194537. This article has 3 citations.

19. (kumar2022energyabsorptionand pages 8-11): Ajeet Kumar, Luca Collini, Chiara Ursini, and Jeng-Ywan Jeng. Energy absorption and stiffness of thin and thick-walled closed-cell 3d-printed structures fabricated from a hyperelastic soft polymer. Materials, 15:2441, Mar 2022. URL: https://doi.org/10.3390/ma15072441, doi:10.3390/ma15072441. This article has 40 citations.

20. (kumar2022energyabsorptionand pages 14-16): Ajeet Kumar, Luca Collini, Chiara Ursini, and Jeng-Ywan Jeng. Energy absorption and stiffness of thin and thick-walled closed-cell 3d-printed structures fabricated from a hyperelastic soft polymer. Materials, 15:2441, Mar 2022. URL: https://doi.org/10.3390/ma15072441, doi:10.3390/ma15072441. This article has 40 citations.

21. (he2026investigationonbridging pages 13-15): Hao He, Zhi Zhu, Y. X. Zhang, and Richard (Chunhui) Yang. Investigation on bridging defects in 3d-printed polylactic acid beams using fused filament fabrication. Polymers, 18:261, Jan 2026. URL: https://doi.org/10.3390/polym18020261, doi:10.3390/polym18020261. This article has 0 citations.

22. (tian2016microstructurechangesin pages 8-10): Qiang Tian, Ivan Krakovský, Guanyun Yan, Liangfei Bai, Jiahui Liu, Guangai Sun, László Rosta, Bo Chen, and László Almásy. Microstructure changes in polyester polyurethane upon thermal and humid aging. Polymers, 8:197, May 2016. URL: https://doi.org/10.3390/polym8050197, doi:10.3390/polym8050197. This article has 45 citations.