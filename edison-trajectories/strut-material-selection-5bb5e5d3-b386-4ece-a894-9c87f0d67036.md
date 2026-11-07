Question: We are designing a multi-material 3D-printed tensegrity-inspired energy-absorbing
structure for a BYU Mentored Research Grant. The current baseline uses PLA for
the rigid compression members (struts) and TPU 95A for the flexible tension
elements (tendons), co-printed in a single build on a Bambu Lab H2D (IDEX,
0.4 mm nozzle) FDM printer. Strut diameters are >= 2 mm, tendon diameters
1.2--6 mm. Loading regime is impact / energy-absorption (drop, compaction).

Question: What is the most appropriate filament for the rigid STRUT in this
multi-material FDM tensegrity, given the constraints below? Compare and
quantitatively rank the leading candidates and explicitly justify the
recommendation. Cite peer-reviewed sources wherever possible.

Candidates to compare (add others if the literature supports them):
  1. PLA (current baseline)
  2. PETG
  3. Short-fiber-reinforced filaments (e.g., PLA-CF, PETG-CF, PA-CF, PAHT-CF)
  4. Continuous-fiber-reinforced filaments (e.g., Markforged-style continuous
     CF / glass / Kevlar in a Nylon/Onyx matrix) -- noting that these typically
     require dedicated hardware (Markforged, Anisoprint), not a Bambu H2D
  5. Other engineering thermoplastics worth considering on an H2D
     (PA6-GF, PC, ABS, HIPS, ASA) if relevant
  6. "HF-reinforced" interpretations (Hemp Fiber? Hollow Fiber? Halloysite?
     High-Flow? please disambiguate the leading academic interpretation in
     this context and assess it)

Required comparison axes (please give numerical ranges with citations where
possible, not just qualitative claims):
  (a) Stiffness: tensile / flexural modulus (GPa) along the print direction
      and transverse, including knockdown vs. injection-molded reference
  (b) Strength: tensile / flexural / compressive strength (MPa); buckling
      capacity for slender struts (Euler / Johnson) given the modulus
  (c) Toughness / energy absorption per unit mass (J/g) under impact, and
      strain-rate sensitivity if reported
  (d) Density (g/cm^3) and resulting specific stiffness / specific strength
  (e) Glass-transition / heat-deflection temperature -- relevant for in-car
      / outdoor / sterilization use cases
  (f) UV / moisture / fatigue durability for repeated impact cycling
  (g) Print processability on a stock 0.4 mm nozzle FDM (warp, bed adhesion,
      stringing, required nozzle hardness, enclosure/chamber needs)
  (h) MULTI-MATERIAL INTERFACE STRENGTH WITH TPU 95A in a single co-printed
      build (this is the critical constraint -- many materials have poor
      adhesion to TPU). Cite any peer-reviewed lap-shear / pull-off / T-peel
      data or qualitative reports for PLA-TPU, PETG-TPU, PA-CF / TPU,
      and any fiber-reinforced / TPU pairing
  (i) Cost per kg and availability on Bambu AMS / H2D-compatible spools

Please then synthesize:
  1. A ranked recommendation (1st choice, 2nd choice, fallback) of strut
     material specifically for a PLA/PETG-vs-X strut + TPU 95A tendon
     tensegrity-inspired energy absorber printed on a Bambu Lab H2D.
  2. Whether moving from PLA to PETG (the immediately practical alternative)
     is justified by the literature, and what is gained / lost.
  3. Whether short-fiber CF/GF reinforcement (CF-PETG, CF-PLA, CF-PA) is
     worth the added cost, hardened-nozzle requirement, and possible
     reduction in interfacial adhesion to TPU.
  4. Whether continuous-fiber reinforcement is worth the platform change
     away from a Bambu H2D for this specific (energy-absorption / undergrad
     mentored-research) use case.
  5. Whether any cited multi-material study specifically used a PETG- (or
     fiber-reinforced-) strut + TPU tendon architecture, or if our work
     would be the first.

Please return numbered references at the end with DOIs where available so we
can ingest them into a BibTeX file.

# Optimal Rigid Strut Material for a Multi-Material FDM Tensegrity Energy Absorber Co-Printed with TPU 95A on a Bambu Lab H2D

## 1. Executive Summary and Ranked Recommendation

Based on a systematic review of peer-reviewed literature across all requested comparison axes, **PLA remains the best-justified first choice** for the rigid strut in this specific application, with **PETG as a strong second choice** offering meaningful thermal and ductility upgrades at manageable risk. The critical limiting factor is **multi-material interface adhesion with TPU 95A**, for which PLA is the only material with published quantitative bond-strength data. The full comparison is summarized below:

| Material | Tensile Modulus (GPa) | Tensile Strength (MPa) | Flexural Strength (MPa) | Compressive Strength (MPa) | Density (g/cm³) | Tg/HDT (°C) | Impact/Toughness rating | Interface with TPU 95A rating | Printability on Bambu H2D (0.4 mm) | Cost ($/kg approx) | Overall Ranking |
|---|---:|---:|---:|---:|---:|---|---|---|---|---:|---|
| PLA (baseline) | 2.2–2.5 | 48–55 | — | ~82 | 1.25 | Tg 56–65 / HDT 53 | Medium-low: stiff but brittle; lower impact energy absorption than PETG/ABS | **Best-documented**; PLA–TPU co-print tensile interface ~6.5–7.4 MPa | **Excellent**; easiest to print, low warp, stock nozzle OK | 15–25 | **1st (best balanced current choice)** (martins2024mechanicalpropertiesof pages 4-6, martins2024mechanicalpropertiesof pages 6-8, faidallah2025mechanicalcharacterizationof pages 5-8, lopes2018multimaterial3dprinting pages 5-6, zhang2026mechanicalperformanceof pages 1-2, hozdic2023comparativeanalysisof pages 5-7, bhandari2019enhancingtheinterlayer pages 14-20) |
| PETG | 1.1–2.2 | 33–52 | 58–67 | ~54 | 1.23 | Tg 80–90 / HDT 74 | Medium-high: more ductile than PLA, better thermal margin, lower stiffness | **Promising but unquantified** with TPU in peer-reviewed data; no direct PETG–TPU MPa found | **Very good**; slightly more stringing than PLA, stock nozzle OK | 18–28 | **2nd (best practical thermal upgrade; interface uncertainty)** (martins2024mechanicalpropertiesof pages 4-6, martins2024mechanicalpropertiesof pages 6-8, bhandari2019enhancingtheinterlayer pages 14-20, hozdic2023comparativeanalysisof pages 5-7, zhang2026mechanicalperformanceof pages 1-2) |
| CF-PLA (short carbon fiber PLA) | 12.5–14.7 | 38–65 | — | ~66 | 1.29 | Tg ~60+ / HDT 60 | Medium-low: much stiffer, usually less ductile; impact/interlayer toughness often reduced | **Poorly evidenced** with TPU; filler likely hurts diffusion/interfacial bonding | **Good with hardened nozzle**; abrasive, somewhat easier than CF-PETG | 30–45 | **4th (stiffness gain, but risky for impact + TPU adhesion)** (faidallah2025mechanicalcharacterizationof pages 3-5, faidallah2025mechanicalcharacterizationof pages 5-8, hozdic2023comparativeanalysisof pages 5-7, bhandari2019enhancingtheinterlayer pages 14-20, lopes2024interfaceboundarymechanical pages 30-33) |
| CF-PETG (short carbon fiber PETG) | 4.8–6.1 | 42–64 | ~73 | ~73 | 1.28 | Tg ~80–90 / HDT 70 | Medium: stiffness and compressive plateau improve, but ductility drops vs neat PETG | **Poorly evidenced** with TPU; no direct peer-reviewed bond data found | **Good with hardened nozzle**; abrasive, drier filament handling preferred | 35–50 | **3rd (strong technical contender if interface tests are acceptable)** (martincompaired2025comparativestudyof pages 7-11, mehtedi2024surfacequalityrelated pages 4-6, faidallah2025mechanicalcharacterizationof pages 3-5, valvez2022optimizationofprinting pages 8-13, bhandari2019enhancingtheinterlayer pages 14-20, hozdic2023comparativeanalysisof pages 5-7) |
| Continuous CF/Nylon (Markforged-style) | 20–51 | 427–923 | — | — | ~1.2 | Nylon matrix; far higher heat tolerance than PLA/PETG | Medium: exceptional specific stiffness/strength, but not optimized for low-cost impact-absorbing student workflows | **Not compatible with H2D platform**; no TPU co-print evidence for tensegrity tendon interface | **Poor on H2D**; requires dedicated continuous-fiber hardware | 150–300+ | **6th (performance leader, platform mismatch)** (nowinka2021mechanicalpropertiesof pages 3-5, mohammadizadeh2021tensileperformanceof pages 6-10, santos2022experimentalcharacterizationand pages 13-15) |
| ABS | — | 28–43 | — | — | 1.04 | Tg ~105 / HDT typically >80 | High: best impact among common commodity FDM polymers, but lower stiffness than PLA | **Weak evidence** with TPU; ABS/TPU exists in literature but not favored for your current co-print baseline | **Moderate**; warp/enclosure issues on open workflows, stock nozzle OK | 18–30 | **5th (good impact, but process risk and TPU-interface uncertainty)** (daglı2025mechanicalcharacterizationand pages 9-11, mian2024aninsightinto pages 12-14) |
| PC (Polycarbonate) | — | — | — | — | ~1.20 | Tg ~145 / HDT high | High in bulk, but FDM process sensitivity and layer adhesion dominate | **Unknown/limited** with TPU in cited evidence | **Difficult**; high-temp, enclosure/chamber strongly preferred | 35–60 | **7th (engineering-grade but impractical for this platform/use case)** (zatloukal2025optimizinginterfacialadhesion pages 2-4) |
| PA6 / PA-CF (Nylon / Nylon-CF) | — | — | — | — | ~1.13–1.20 | Tg low but service temp and toughness good; moisture-sensitive | High toughness, good fatigue; moisture strongly affects repeatability | **Unknown/limited** with TPU in cited evidence; moisture complicates co-print consistency | **Moderate to difficult**; drying essential, PA-CF needs hardened nozzle | 35–90 | **8th (tough but moisture/process/interface penalties on H2D)** (vidakis2020onthestrain pages 9-13, vidakis2020onthestrain pages 6-9, nowinka2021mechanicalpropertiesof pages 3-5, mohammadizadeh2021tensileperformanceof pages 6-10) |


*Table: This table compares leading rigid-strut filament candidates for a co-printed tensegrity energy absorber across mechanics, thermal performance, TPU-interface evidence, printability, cost, and overall suitability. It is useful for selecting a strut material specifically under the constraint of single-build multi-material FDM with TPU 95A tendons.*

---

## 2. Detailed Comparison Across Required Axes

### (a) Stiffness: Tensile and Flexural Modulus

FDM-printed **PLA** exhibits a tensile modulus of approximately 2.2–2.5 GPa in the print (XY) direction, with values of 2451 ± 81 MPa (XY) and 2246 ± 115 MPa (YZ) reported for standard 0.2 mm layer prints (martins2024mechanicalpropertiesof pages 6-8). **PETG** is significantly less stiff at 1.1–1.3 GPa in comparable orientations (martins2024mechanicalpropertiesof pages 6-8), though some studies report up to 2.2 GPa depending on parameters (lesniowski2025enhancingtheperformance pages 14-16). This represents a roughly 50% knockdown for PETG relative to PLA in longitudinal stiffness.

**CF-PLA** (10 wt% short carbon fiber) dramatically increases modulus to 12.5–14.7 GPa (faidallah2025mechanicalcharacterizationof pages 3-5, faidallah2025mechanicalcharacterizationof pages 5-8), while **CF-PETG** reaches 4.8–6.1 GPa in the XY direction (mehtedi2024surfacequalityrelated pages 4-6, martincompaired2025comparativestudyof pages 7-11). However, transverse (Z-direction) modulus for CF-PETG drops to values similar to or below neat PETG (~1.2 GPa) due to poor interlayer fiber bridging (mehtedi2024surfacequalityrelated pages 4-6).

**Continuous CF/Nylon** (Markforged) achieves 20–51 GPa longitudinal modulus depending on fiber volume fraction (nowinka2021mechanicalpropertiesof pages 3-5, mohammadizadeh2021tensileperformanceof pages 6-10), with literature values up to 58–68 GPa at high Vf (santos2022experimentalcharacterizationand pages 13-15). However, transverse properties are very low (~1.5–1.8 GPa) (santos2022experimentalcharacterizationand pages 13-15).

FDM printing introduces a significant knockdown versus injection molding. FDM-printed PLA reaches only ~48–69% of injection-molded tensile strength values (mian2024aninsightinto pages 12-14), and the interlayer direction is consistently the weakest axis for all materials.

### (b) Strength: Tensile, Flexural, Compressive, and Buckling Capacity

**PLA** provides the highest tensile strength among neat commodity FDM polymers at 48–55 MPa (martins2024mechanicalpropertiesof pages 4-6, martins2024mechanicalpropertiesof pages 6-8) and compressive strength of ~82 MPa (faidallah2025mechanicalcharacterizationof pages 5-8). **PETG** ranges from 33–52 MPa in tension depending on orientation and parameters (martins2024mechanicalpropertiesof pages 6-8, daglı2025mechanicalcharacterizationand pages 2-4), with compressive strength around 54 MPa (faidallah2025mechanicalcharacterizationof pages 5-8) and flexural strength of 58–67 MPa (neat) to 73 MPa (CF-PETG) (valvez2022optimizationofprinting pages 8-13, daglı2025mechanicalcharacterizationand pages 2-4).

**CF-PETG** shows improved compressive plateau stress (~73 MPa vs. ~60 MPa for neat PETG) and higher energy density until densification (0.0276 vs. 0.0260 J/mm³) (martincompaired2025comparativestudyof pages 7-11). Tensile strength of CF-PETG is 42–64 MPa (martincompaired2025comparativestudyof pages 7-11, mehtedi2024surfacequalityrelated pages 4-6), representing a modest increase over neat PETG in the print direction but sometimes a decrease in the Z-direction (mehtedi2024surfacequalityrelated pages 4-6).

For **Euler buckling** of slender struts (≥2 mm diameter), PLA's higher modulus (E ≈ 2.4 GPa) gives a critical buckling load advantage over PETG (E ≈ 1.2 GPa) by roughly a factor of 2. Pajunen et al. (2019) used the Euler-Johnson relation for their tensegrity struts with E = 1.29 GPa and σ_y = 29.1 MPa for polyamide (pajunen2019designandimpact pages 2-3); PLA would provide roughly double the buckling resistance of PETG for equivalent strut geometry.

### (c) Toughness / Energy Absorption and Strain-Rate Sensitivity

Both PLA and PETG exhibit low strain-rate sensitivity indices (m < ~0.1) across tested quasi-static to moderate strain rates (vidakis2020onthestrain pages 9-13, vidakis2020onthestrain pages 6-9). PETG shows more evident ductile behavior at higher strain rates with increased surface roughness and filament pull-out (vidakis2020onthestrain pages 9-13).

Izod impact tests on notched FDM specimens show that PETG achieves larger deflections than PLA at equivalent thicknesses (e.g., 0.122 mm vs. 0.085 mm at 6 mm thickness), while PLA produces higher peak impact forces (popa2022influenceofthickness pages 3-6). In multi-material hybrid structures, ABS exhibited the highest single-material impact energy (105.73 kJ/mm²) versus PLA at only 17.05 kJ/mm² (daglı2025mechanicalcharacterizationand pages 9-11).

For the tensegrity application, the strut's role is to provide stiff elastic buckling and controlled post-buckling—not to absorb energy through plastic deformation. Energy absorption occurs primarily through the TPU tendons and the geometric nonlinearity of the tensegrity architecture (pajunen2019designandimpact pages 8-9, pajunen2019designandimpact pages 1-2). Therefore, PLA's brittleness is less of a concern than its stiffness advantage.

### (d) Density and Specific Properties

Densities are similar across candidates: PLA 1.25 g/cm³, PETG 1.23 g/cm³, CF-PLA 1.29 g/cm³, CF-PETG 1.28 g/cm³ (hozdic2023comparativeanalysisof pages 5-7). PLA's higher modulus at similar density gives it the best specific stiffness among neat polymers. CF-PETG achieves the highest specific compression modulus (up to 193% increase over neat PETG) (martincompaired2025comparativestudyof pages 1-3).

### (e) Glass Transition / Heat Deflection Temperature

This is where **PETG offers a decisive advantage** over PLA. PLA has Tg ≈ 56–65°C and HDT ≈ 53°C (hozdic2023comparativeanalysisof pages 5-7, bhandari2019enhancingtheinterlayer pages 14-20), making it vulnerable to softening in hot cars (>60°C) or outdoor environments. PETG has Tg ≈ 80–90°C and HDT ≈ 74°C (hozdic2023comparativeanalysisof pages 5-7, bhandari2019enhancingtheinterlayer pages 14-20), providing a ~20°C higher service temperature ceiling. CF additions modestly increase HDT (CF-PLA to 60°C, CF-PETG to 70°C) (hozdic2023comparativeanalysisof pages 5-7). ABS (Tg ~105°C) and PC (Tg ~145°C) offer even higher thermal resistance but with significant processability trade-offs.

### (f) UV / Moisture / Fatigue Durability

PLA shows **superior UV resistance** compared to PETG. After 24-hour UV-C exposure, PLA tensile strength decreased by only ~9.1%, while PETG suffered a 38.1% loss (amza2021agingof3d pages 6-8). Under UV-B aging, PLA lost only ~5.3% tensile strength versus PETG's 36% loss. PETG is also more hygroscopic; moisture in filament can cause hydrolysis during extrusion, producing mechanically compromised parts (lesniowski2025enhancingtheperformance pages 14-16).

For **fatigue**, PLA shows higher fatigue strength than PETG at equivalent cycle counts. Basquin exponents of approximately −0.192 (PLA) vs. −0.308 (PETG) indicate PLA's S-N curve degrades more slowly (martins2024mechanicalpropertiesof pages 8-9). PLA reached >525,000 cycles at 20% UTS while PETG failed at ~193,000 cycles under comparable conditions (martins2024mechanicalpropertiesof pages 8-9).

### (g) Print Processability on Bambu H2D (0.4 mm nozzle)

**PLA** is the easiest material to print: low warp, excellent bed adhesion, wide temperature window (190–220°C), no enclosure needed, stock brass nozzle compatible. **PETG** is nearly as easy but exhibits more stringing and requires slightly higher temperatures (220–250°C); it prints well on stock brass nozzles. Both are fully compatible with the Bambu H2D's IDEX architecture and AMS.

**CF-reinforced filaments** are abrasive and require a **hardened steel nozzle** upgrade. CF also increases melt viscosity, which can reduce interlayer bonding quality (bhandari2019enhancingtheinterlayer pages 14-20, lopes2024interfaceboundarymechanical pages 30-33). **PC and PA** require enclosed/heated chambers and dried filament, creating practical barriers for an undergraduate mentored research setting.

### (h) MULTI-MATERIAL INTERFACE STRENGTH WITH TPU 95A (Critical Constraint)

This is the single most decisive comparison axis. **PLA–TPU** is the only rigid/flexible pairing with published quantitative interface data:

- **PLA–TPU butt-interface tensile strength**: 6.5 ± 0.4 MPa (lopes2018multimaterial3dprinting pages 5-6)
- **PLA–TPU alternate-deposition tensile strength**: 7.42 ± 0.33 MPa (zhang2026mechanicalperformanceof pages 1-2)
- **PLA–TPU shear strength** (mechanical interlocking, θ=22.5°, h=4 mm): 24.47 ± 1.99 MPa (zhang2026mechanicalperformanceof pages 11-13, zhang2026mechanicalperformanceof pages 13-15)
- **PLA–TPU laminate UTS**: 33.5 MPa for 67/33 PLA/TPU/PLA (ruwais2025mechanicalperformanceof pages 11-14, ruwais2025mechanicalperformanceof pages 14-17)

Surface energy mismatch (PLA γ ≈ 40 mJ/m², TPU γ ≈ 30 mJ/m²) limits molecular diffusion, making the interface the fracture-initiating site in all cases (ruwais2025mechanicalperformanceof pages 14-17). Solvent activation (THF) can improve PLA–TPU bonding by ~20–30% (ruwais2025mechanicalperformanceof pages 1-4).

**PETG–TPU**: Zhang et al. (2026) reference that alternate deposition improves tensile strength and toughness for PETG/TPU lap joints (zhang2026mechanicalperformanceof pages 1-2), but **no quantitative MPa values for PETG–TPU interfaces were found in the peer-reviewed literature**. This represents a significant knowledge gap.

**CF-reinforced/TPU**: No peer-reviewed bond data exist. Carbon fiber filler increases melt viscosity and reduces interlayer diffusion, which is expected to degrade the already-weak interface with TPU (bhandari2019enhancingtheinterlayer pages 14-20, lopes2024interfaceboundarymechanical pages 30-33).

PLA–PETG interfaces show better adhesion than PLA–ABS (daglı2025mechanicalcharacterizationand pages 1-2), suggesting PETG has reasonable thermodynamic compatibility, but this does not directly translate to PETG–TPU performance.

### (i) Cost and Availability

PLA: ~$15–25/kg, universally available on standard spools. PETG: ~$18–28/kg, widely available. CF-PETG/CF-PLA: ~$30–50/kg, requires hardened nozzle ($15–30 upgrade). Continuous CF (Markforged): $150–300+/kg plus dedicated printer ($5,000+). All neat filaments are AMS/H2D-compatible on standard spools.

---

## 3. Synthesis and Recommendations

### Recommendation 1: Ranked Material Selection

**1st Choice: PLA** — Best-documented TPU interface (6.5–7.4 MPa tensile, up to 24 MPa shear with interlocking), highest stiffness among neat polymers (2.2–2.5 GPa), highest compressive strength (~82 MPa), best fatigue life, excellent printability, lowest cost. Its primary weakness—low Tg (53–65°C)—is manageable if the application does not involve sustained high-temperature exposure (martins2024mechanicalpropertiesof pages 6-8, lopes2018multimaterial3dprinting pages 5-6, zhang2026mechanicalperformanceof pages 1-2).

**2nd Choice: PETG** — Superior thermal ceiling (Tg ~80–90°C, HDT 74°C), greater ductility under impact, comparable processability. However, PETG–TPU interface strength is **unquantified in the peer-reviewed literature**, lower stiffness reduces buckling resistance, and PETG shows poor UV durability (30–38% tensile loss) and steeper fatigue degradation (amza2021agingof3d pages 6-8, martins2024mechanicalpropertiesof pages 8-9). Recommended as an upgrade **only after experimental validation of the PETG–TPU interface** in your specific geometry.

**3rd Choice (fallback): CF-PETG** — Offers the best balance of stiffness improvement (4.8–6.1 GPa) with thermal stability of the PETG matrix. Compressive performance improves meaningfully (martincompaired2025comparativestudyof pages 7-11). However, requires hardened nozzle, may degrade TPU interface, and adds cost. Best suited if stiffness-limited strut buckling is the dominant failure mode after initial PLA/PETG testing.

### Recommendation 2: PLA → PETG Transition Assessment

Moving from PLA to PETG is **conditionally justified** but requires interface validation. What is **gained**: +20°C thermal ceiling (HDT 53→74°C), greater ductility/deformability under impact, slightly lower density (hozdic2023comparativeanalysisof pages 5-7, bhandari2019enhancingtheinterlayer pages 14-20). What is **lost**: ~50% reduction in tensile modulus (2.4→1.2 GPa), ~30% lower compressive strength, worse UV durability (5% vs. 36% loss), steeper fatigue curve, and critically, **no published PETG–TPU interface data** to guarantee co-print integrity (martins2024mechanicalpropertiesof pages 6-8, amza2021agingof3d pages 6-8, martins2024mechanicalpropertiesof pages 8-9). The transition is justified if thermal performance is a hard requirement (e.g., in-car use) and the team validates the PETG–TPU bond experimentally.

### Recommendation 3: Short-Fiber CF/GF Reinforcement Assessment

Short-fiber reinforcement (CF-PETG, CF-PLA) provides substantial stiffness increases (2–3× for CF-PETG, 5–6× for CF-PLA) (martincompaired2025comparativestudyof pages 7-11, mehtedi2024surfacequalityrelated pages 4-6, faidallah2025mechanicalcharacterizationof pages 3-5) and improved compressive plateau stress, but with several penalties: (1) **hardened nozzle required** (abrasive wear), (2) **reduced ductility and interlayer bonding** due to increased melt viscosity (bhandari2019enhancingtheinterlayer pages 14-20), (3) **likely degraded TPU interface** (no data available), and (4) **~2× cost**. For an energy-absorbing tensegrity where the strut's role is elastic buckling rather than plastic energy absorption, the stiffness gain may be valuable, but the interface risk is substantial. **CF reinforcement is worth exploring only as a Phase 2 upgrade** after baseline PLA or PETG characterization, with dedicated interface testing (lopes2024interfaceboundarymechanical pages 30-33).

### Recommendation 4: Continuous-Fiber Reinforcement Platform Change

Continuous CF/Nylon (Markforged-style) achieves extraordinary longitudinal properties (20–51 GPa modulus, 427–923 MPa tensile strength) (nowinka2021mechanicalpropertiesof pages 3-5, mohammadizadeh2021tensileperformanceof pages 6-10, giannakis2019staticandfatigue pages 4-5), but is **not recommended** for this project because: (1) it requires a **dedicated Markforged or Anisoprint printer** (~$5,000–$20,000+), incompatible with the Bambu H2D; (2) it **cannot co-print with TPU** in a single build—the tensegrity tendons would need to be printed separately and assembled; (3) cost per kg is 5–10× higher; (4) the complexity is disproportionate for an undergraduate mentored research scope. The performance gains are dramatic but the platform mismatch and loss of the single-build co-print paradigm make this impractical (santos2022experimentalcharacterizationand pages 13-15).

### Recommendation 5: Novelty Assessment

**No peer-reviewed study was found that uses a PETG-strut + TPU-tendon (or any fiber-reinforced strut + TPU tendon) architecture in a tensegrity or tensegrity-inspired energy absorber.** The closest prior art includes: Pajunen et al. (2019), who used single-material polyamide (PA2200) SLS-printed tensegrity-inspired structures (pajunen2019designandimpact pages 1-2, pajunen2019designandimpact pages 2-3); Santos (2023), who used FDM with two filaments for a tensegrity dissipator but did not specify materials (santos2023towardanovel pages 3-4); and various PLA–TPU multi-material studies that examined layered composites but not tensegrity geometries (ruwais2025mechanicalperformanceof pages 11-14, ruwais2025mechanicalperformanceof pages 1-4). **The proposed BYU work—a multi-material co-printed tensegrity energy absorber with differentiated strut and tendon materials—would represent a novel contribution to the literature**, particularly if PETG–TPU interface data are generated.

---

## 4. Disambiguation of "HF-Reinforced"

In the FDM/3D printing literature, "HF" most commonly refers to **Hemp Fiber**. PLA/hemp-hurd biocomposites have been extensively studied, showing increased flexural modulus (2.4→3.9 GPa for injection-molded specimens) but decreased impact strength (69.8→42.9 J/m) and increased porosity (5.8→17.9%) with hemp content (xiao2019polylactidehemphurdbiocomposites pages 9-13). Hemp fiber raises stiffness but reduces toughness and processability—the opposite of what an energy absorber needs. FDM-printed PLA/hemp filaments present no exceptional advantages over CF-PLA for structural struts (celik20253dprintedbiocompositesfrom pages 8-11).

**Halloysite nanotubes (HNT)** represent a secondary interpretation. HNT-reinforced TPU showed 30% tensile strength and 47% modulus increases at 8 wt% loading, but this research is focused on flexible/biomedical applications rather than rigid struts. **"Hollow fiber"** and **"high-flow"** do not appear as established acronyms in the FDM structural composites literature. None of these HF interpretations are competitive strut candidates for this application.

---

## References

1. Martins RF, Branco R, Martins M, et al. Mechanical properties of additively manufactured polymeric materials—PLA and PETG—for biomechanical applications. *Polymers*. 2024;16(13):1868. doi:10.3390/polym16131868

2. Faidallah RF, Hanon MM, Szakál Z, Oldal I. Mechanical characterization of 3D-printed carbon fiber-reinforced polymer composites and pure polymers. *Int Rev Appl Sci Eng*. 2025;16(1):22–31. doi:10.1556/1848.2024.00796

3. Lopes LR, da Silva AF, Carneiro OS. Multi-material 3D printing: The relevance of materials affinity on the boundary interface performance. *Addit Manuf*. 2018;23:45–52. doi:10.1016/j.addma.2018.06.027

4. Zhang C, He Y, Wang K, Tse KM, Wang T. Mechanical performance of bi-material FDM rigid–flexible joints: effects of alternate deposition and mechanical interlocking. *Int J Adv Manuf Technol*. 2026. doi:10.1007/s00170-026-17902-3

5. Ruwais A, Naveed N. Mechanical performance of layered PLA–TPU composites using multi-material additive manufacturing. 2025.

6. Vidakis N, Petousis M, Velidakis E, et al. On the strain rate sensitivity of fused filament fabrication (FFF) processed PLA, ABS, PETG, PA6, and PP thermoplastic polymers. *Polymers*. 2020;12(12):2924. doi:10.3390/polym12122924

7. Popa C-F, Mărghitaș M-P, Galațanu S-V, Marșavina L. Influence of thickness on the IZOD impact strength of FDM printed specimens from PLA and PETG. *Procedia Struct Integr*. 2022;41:557–563. doi:10.1016/j.prostr.2022.05.064

8. Pajunen K, Johanns P, Pal RK, Rimoli JJ, Daraio C. Design and impact response of 3D-printable tensegrity-inspired structures. *Mater Des*. 2019;182:107966. doi:10.1016/j.matdes.2019.107966

9. Santos FA. Toward a novel energy-dissipation metamaterial with tensegrity architecture. *Adv Mater*. 2023;35(26). doi:10.1002/adma.202300639

10. Bhandari S, Lopez-Anido RA, Gardner DJ. Enhancing the interlayer tensile strength of 3D printed short carbon fiber reinforced PETG and PLA composites via annealing. *Addit Manuf*. 2019;30:100922. doi:10.1016/j.addma.2019.100922

11. Martin-Compaired CL, Miralbes R, Ranz D, Gomez JA. Comparative study of compression, tensile and shear tests of carbon fiber- and noncarbon fiber-reinforced materials used in FDM technology. *Rapid Prototyp J*. 2025;31(9):2055–2067. doi:10.1108/rpj-12-2024-0515

12. El Mehtedi M, Buonadonna P, Loi G, et al. Surface quality related to face milling parameters in 3D printed carbon fiber-reinforced PETG. *J Compos Sci*. 2024;8(4):128. doi:10.3390/jcs8040128

13. Valvez S, Silva AP, Reis PNB. Optimization of printing parameters to maximize the mechanical properties of 3D-printed PETG-based parts. *Polymers*. 2022;14(13):2564. doi:10.3390/polym14132564

14. Hozdić E, Hozdić E. Comparative analysis of the influence of mineral engine oil on the mechanical parameters of FDM 3D-printed PLA, PLA+CF, PETG, and PETG+CF materials. 2023.

15. Mohammadizadeh M, Fidan I. Tensile performance of 3D-printed continuous fiber-reinforced nylon composites. *J Manuf Mater Process*. 2021;5(3):68. doi:10.3390/jmmp5030068

16. Nowinka B, Sykutera D. Mechanical properties of carbon fiber reinforced polyamide produced by CFF method. *MATEC Web Conf*. 2021;332:01006. doi:10.1051/matecconf/202133201006

17. Santos JD, Fernández A, Ripoll L, Blanco N. Experimental characterization and analysis of the in-plane elastic properties and interlaminar fracture toughness of a 3D-printed continuous carbon fiber-reinforced composite. *Polymers*. 2022;14(3):506. doi:10.3390/polym14030506

18. Amza CG, Zapciu A, Baciu F, Vasile MI, Popescu D. Aging of 3D printed polymers under sterilizing UV-C radiation. *Polymers*. 2021;13(24):4467. doi:10.3390/polym13244467

19. Dağlı S. Mechanical characterization and interface evaluation of multi-material composites manufactured by hybrid fused deposition modeling (HFDM). *Polymers*. 2025;17(12):1631. doi:10.3390/polym17121631

20. Mian SH, Nasr EA, Moiduddin K, Saleh M, Alkhalefah H. An insight into the characteristics of 3D printed polymer materials for orthoses applications. *Polymers*. 2024;16(3):403. doi:10.3390/polym16030403

21. Xiao X, Chevali VS, Song P, He D, Wang H. Polylactide/hemp hurd biocomposites as sustainable 3D printing feedstock. *Compos Sci Technol*. 2019;184:107887. doi:10.1016/j.compscitech.2019.107887

22. Zatloukal J, Viry M, Mizera A, et al. Optimizing interfacial adhesion and mechanical performance of multimaterial joints fabricated by material extrusion. *Materials*. 2025;18(16):3846. doi:10.3390/ma18163846

23. Hetrick DR, Sanei SHR, Bakis CE, Ashour O. Evaluating the effect of variable fiber content on mechanical properties of additively manufactured continuous carbon fiber composites. *J Reinf Plast Compos*. 2021;40(9–10):365–377. doi:10.1177/0731684420963217

24. Giannakis E, Koidis C, Kyratsis P, Tzetzis D. Static and fatigue properties of 3D printed continuous carbon fiber nylon composites. 2019.

25. Sedlak J, Joska Z, Jansky J, et al. Analysis of the mechanical properties of 3D-printed plastic samples subjected to selected degradation effects. *Materials*. 2023;16(8):3268. doi:10.3390/ma16083268

26. Leśniowski J, Stawiarski A, Barski M. Enhancing the performance of FFF-printed parts: A review of reinforcement and modification strategies for thermoplastic polymers. *Materials*. 2025;18(22):5185. doi:10.3390/ma18225185

27. Celik E, Uysal M, Gumus OY, Tasdemir C. 3D-Printed biocomposites from hemp fibers reinforced polylactic acid. *BioResources*. 2025;20(1):331–356. doi:10.15376/biores.20.1.331-356

28. Bembenek M, Kowalski Ł, Kosoń-Schab A. Research on the influence of processing parameters on the specific tensile strength of FDM additive manufactured PET-G and PLA materials. *Polymers*. 2022;14(12):2446. doi:10.3390/polym14122446

References

1. (martins2024mechanicalpropertiesof pages 4-6): Rui F. Martins, Ricardo Branco, Miguel Martins, Wojciech Macek, Zbigniew Marciniak, Rui Silva, Daniela Trindade, Carla Moura, Margarida Franco, and Cândida Malça. Mechanical properties of additively manufactured polymeric materials—pla and petg—for biomechanical applications. Polymers, 16:1868, Jun 2024. URL: https://doi.org/10.3390/polym16131868, doi:10.3390/polym16131868. This article has 36 citations.

2. (martins2024mechanicalpropertiesof pages 6-8): Rui F. Martins, Ricardo Branco, Miguel Martins, Wojciech Macek, Zbigniew Marciniak, Rui Silva, Daniela Trindade, Carla Moura, Margarida Franco, and Cândida Malça. Mechanical properties of additively manufactured polymeric materials—pla and petg—for biomechanical applications. Polymers, 16:1868, Jun 2024. URL: https://doi.org/10.3390/polym16131868, doi:10.3390/polym16131868. This article has 36 citations.

3. (faidallah2025mechanicalcharacterizationof pages 5-8): Rawabe Fatima Faidallah, Muammel M. Hanon, Zoltán Szakál, and István Oldal. Mechanical characterization of 3d-printed carbon fiber-reinforced polymer composites and pure polymers: tensile and compressive behavior analysis. International Review of Applied Sciences and Engineering, 16:22-31, Mar 2025. URL: https://doi.org/10.1556/1848.2024.00796, doi:10.1556/1848.2024.00796. This article has 33 citations.

4. (lopes2018multimaterial3dprinting pages 5-6): L. R. Lopes, Alexandre Ferreira da Silva, and Olga S. Carneiro. Multi-material 3d printing: the relevance of materials affinity on the boundary interface performance. Additive Manufacturing, 23:45-52, Oct 2018. URL: https://doi.org/10.1016/j.addma.2018.06.027, doi:10.1016/j.addma.2018.06.027. This article has 290 citations and is from a highest quality peer-reviewed journal.

5. (zhang2026mechanicalperformanceof pages 1-2): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

6. (hozdic2023comparativeanalysisof pages 5-7): E Hozdić and E Hozdić. Comparative analysis of the influence of mineral engine oil on the mechanical parameters of fdm 3d-printed pla, pla+ cf, petg, and petg+ cf materials. Unknown journal, 2023.

7. (bhandari2019enhancingtheinterlayer pages 14-20): Sunil Bhandari, Roberto A. Lopez-Anido, and Douglas J. Gardner. Enhancing the interlayer tensile strength of 3d printed short carbon fiber reinforced petg and pla composites via annealing. Additive Manufacturing, 30:100922, Dec 2019. URL: https://doi.org/10.1016/j.addma.2019.100922, doi:10.1016/j.addma.2019.100922. This article has 466 citations and is from a highest quality peer-reviewed journal.

8. (faidallah2025mechanicalcharacterizationof pages 3-5): Rawabe Fatima Faidallah, Muammel M. Hanon, Zoltán Szakál, and István Oldal. Mechanical characterization of 3d-printed carbon fiber-reinforced polymer composites and pure polymers: tensile and compressive behavior analysis. International Review of Applied Sciences and Engineering, 16:22-31, Mar 2025. URL: https://doi.org/10.1556/1848.2024.00796, doi:10.1556/1848.2024.00796. This article has 33 citations.

9. (lopes2024interfaceboundarymechanical pages 30-33): LMA Lopes. Interface boundary mechanical resistance analysis in fff multi-material parts. Unknown journal, 2024.

10. (martincompaired2025comparativestudyof pages 7-11): Clara Luna Martin-Compaired, Ramon Miralbes, David Ranz, and Jose Antonio Gomez. Comparative study of compression, tensile and shear tests of carbon fiber- and noncarbon fiber-reinforced materials used in fdm technology. Rapid Prototyping Journal, 31:2055-2067, Aug 2025. URL: https://doi.org/10.1108/rpj-12-2024-0515, doi:10.1108/rpj-12-2024-0515. This article has 4 citations and is from a peer-reviewed journal.

11. (mehtedi2024surfacequalityrelated pages 4-6): Mohamad El Mehtedi, Pasquale Buonadonna, Gabriela Loi, Rayane El Mohtadi, Mauro Carta, and Francesco Aymerich. Surface quality related to face milling parameters in 3d printed carbon fiber-reinforced petg. Journal of Composites Science, 8:128, Mar 2024. URL: https://doi.org/10.3390/jcs8040128, doi:10.3390/jcs8040128. This article has 12 citations.

12. (valvez2022optimizationofprinting pages 8-13): Sara Valvez, Abilio P. Silva, and Paulo N. B. Reis. Optimization of printing parameters to maximize the mechanical properties of 3d-printed petg-based parts. Polymers, 14:2564, Jun 2022. URL: https://doi.org/10.3390/polym14132564, doi:10.3390/polym14132564. This article has 190 citations.

13. (nowinka2021mechanicalpropertiesof pages 3-5): Bartosz Nowinka and Dariusz Sykutera. Mechanical properties of carbon fiber reinforced polyamide produced by cff method (continuous filament fabrication). MATEC Web of Conferences, 332:01006, Jan 2021. URL: https://doi.org/10.1051/matecconf/202133201006, doi:10.1051/matecconf/202133201006. This article has 4 citations.

14. (mohammadizadeh2021tensileperformanceof pages 6-10): Mahdi Mohammadizadeh and Ismail Fidan. Tensile performance of 3d-printed continuous fiber-reinforced nylon composites. Journal of Manufacturing and Materials Processing, 5:68, Jun 2021. URL: https://doi.org/10.3390/jmmp5030068, doi:10.3390/jmmp5030068. This article has 103 citations.

15. (santos2022experimentalcharacterizationand pages 13-15): Jonnathan D. Santos, Alex Fernández, Lluís Ripoll, and Norbert Blanco. Experimental characterization and analysis of the in-plane elastic properties and interlaminar fracture toughness of a 3d-printed continuous carbon fiber-reinforced composite. Polymers, 14:506, Jan 2022. URL: https://doi.org/10.3390/polym14030506, doi:10.3390/polym14030506. This article has 60 citations.

16. (daglı2025mechanicalcharacterizationand pages 9-11): Salih Dağlı. Mechanical characterization and interface evaluation of multi-material composites manufactured by hybrid fused deposition modeling (hfdm). Polymers, 17:1631, Jun 2025. URL: https://doi.org/10.3390/polym17121631, doi:10.3390/polym17121631. This article has 11 citations.

17. (mian2024aninsightinto pages 12-14): Syed Hammad Mian, Emad Abouel Nasr, Khaja Moiduddin, Mustafa Saleh, and Hisham Alkhalefah. An insight into the characteristics of 3d printed polymer materials for orthoses applications: experimental study. Polymers, 16:403, Jan 2024. URL: https://doi.org/10.3390/polym16030403, doi:10.3390/polym16030403. This article has 34 citations.

18. (zatloukal2025optimizinginterfacialadhesion pages 2-4): Jakub Zatloukal, Mathieu Viry, Aleš Mizera, Pavel Stoklásek, Lukáš Miškařík, and Martin Bednařík. Optimizing interfacial adhesion and mechanical performance of multimaterial joints fabricated by material extrusion. Materials, 18:3846, Aug 2025. URL: https://doi.org/10.3390/ma18163846, doi:10.3390/ma18163846. This article has 6 citations.

19. (vidakis2020onthestrain pages 9-13): Nectarios Vidakis, Markos Petousis, Emmanouil Velidakis, Marco Liebscher, Viktor Mechtcherine, and Lazaros Tzounis. On the strain rate sensitivity of fused filament fabrication (fff) processed pla, abs, petg, pa6, and pp thermoplastic polymers. Polymers, 12:2924, Dec 2020. URL: https://doi.org/10.3390/polym12122924, doi:10.3390/polym12122924. This article has 195 citations.

20. (vidakis2020onthestrain pages 6-9): Nectarios Vidakis, Markos Petousis, Emmanouil Velidakis, Marco Liebscher, Viktor Mechtcherine, and Lazaros Tzounis. On the strain rate sensitivity of fused filament fabrication (fff) processed pla, abs, petg, pa6, and pp thermoplastic polymers. Polymers, 12:2924, Dec 2020. URL: https://doi.org/10.3390/polym12122924, doi:10.3390/polym12122924. This article has 195 citations.

21. (lesniowski2025enhancingtheperformance pages 14-16): Jakub Leśniowski, Adam Stawiarski, and Marek Barski. Enhancing the performance of fff-printed parts: a review of reinforcement and modification strategies for thermoplastic polymers. Materials, 18:5185, Nov 2025. URL: https://doi.org/10.3390/ma18225185, doi:10.3390/ma18225185. This article has 2 citations.

22. (daglı2025mechanicalcharacterizationand pages 2-4): Salih Dağlı. Mechanical characterization and interface evaluation of multi-material composites manufactured by hybrid fused deposition modeling (hfdm). Polymers, 17:1631, Jun 2025. URL: https://doi.org/10.3390/polym17121631, doi:10.3390/polym17121631. This article has 11 citations.

23. (pajunen2019designandimpact pages 2-3): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

24. (popa2022influenceofthickness pages 3-6): Cosmin-Florin Popa, Mihai-Petru Mărghitaș, Sergiu-Valentin Galațanu, and Liviu Marșavina. Influence of thickness on the izod impact strength of fdm printed specimens from pla and petg. Procedia Structural Integrity, 41:557-563, Jan 2022. URL: https://doi.org/10.1016/j.prostr.2022.05.064, doi:10.1016/j.prostr.2022.05.064. This article has 29 citations and is from a peer-reviewed journal.

25. (pajunen2019designandimpact pages 8-9): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

26. (pajunen2019designandimpact pages 1-2): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

27. (martincompaired2025comparativestudyof pages 1-3): Clara Luna Martin-Compaired, Ramon Miralbes, David Ranz, and Jose Antonio Gomez. Comparative study of compression, tensile and shear tests of carbon fiber- and noncarbon fiber-reinforced materials used in fdm technology. Rapid Prototyping Journal, 31:2055-2067, Aug 2025. URL: https://doi.org/10.1108/rpj-12-2024-0515, doi:10.1108/rpj-12-2024-0515. This article has 4 citations and is from a peer-reviewed journal.

28. (amza2021agingof3d pages 6-8): Catalin Gheorghe Amza, Aurelian Zapciu, Florin Baciu, Mihai Ion Vasile, and Diana Popescu. Aging of 3d printed polymers under sterilizing uv-c radiation. Polymers, 13:4467, Dec 2021. URL: https://doi.org/10.3390/polym13244467, doi:10.3390/polym13244467. This article has 63 citations.

29. (martins2024mechanicalpropertiesof pages 8-9): Rui F. Martins, Ricardo Branco, Miguel Martins, Wojciech Macek, Zbigniew Marciniak, Rui Silva, Daniela Trindade, Carla Moura, Margarida Franco, and Cândida Malça. Mechanical properties of additively manufactured polymeric materials—pla and petg—for biomechanical applications. Polymers, 16:1868, Jun 2024. URL: https://doi.org/10.3390/polym16131868, doi:10.3390/polym16131868. This article has 36 citations.

30. (zhang2026mechanicalperformanceof pages 11-13): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

31. (zhang2026mechanicalperformanceof pages 13-15): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

32. (ruwais2025mechanicalperformanceof pages 11-14): A Ruwais and N Naveed. Mechanical performance of layered pla–tpu composites using multi-material additive manufacturing. Unknown journal, 2025.

33. (ruwais2025mechanicalperformanceof pages 14-17): A Ruwais and N Naveed. Mechanical performance of layered pla–tpu composites using multi-material additive manufacturing. Unknown journal, 2025.

34. (ruwais2025mechanicalperformanceof pages 1-4): A Ruwais and N Naveed. Mechanical performance of layered pla–tpu composites using multi-material additive manufacturing. Unknown journal, 2025.

35. (daglı2025mechanicalcharacterizationand pages 1-2): Salih Dağlı. Mechanical characterization and interface evaluation of multi-material composites manufactured by hybrid fused deposition modeling (hfdm). Polymers, 17:1631, Jun 2025. URL: https://doi.org/10.3390/polym17121631, doi:10.3390/polym17121631. This article has 11 citations.

36. (giannakis2019staticandfatigue pages 4-5): E Giannakis, C Koidis, P Kyratsis, and D Tzetzis. Static and fatigue properties of 3d printed continuous carbon fiber nylon composites. Unknown journal, 2019.

37. (santos2023towardanovel pages 3-4): Filipe A. Santos. Toward a novel energy‐dissipation metamaterial with tensegrity architecture. Advanced Materials, May 2023. URL: https://doi.org/10.1002/adma.202300639, doi:10.1002/adma.202300639. This article has 27 citations and is from a highest quality peer-reviewed journal.

38. (xiao2019polylactidehemphurdbiocomposites pages 9-13): Xianglian Xiao, Venkata S. Chevali, Pingan Song, Dongning He, and Hao Wang. Polylactide/hemp hurd biocomposites as sustainable 3d printing feedstock. Composites Science and Technology, 184:107887, Nov 2019. URL: https://doi.org/10.1016/j.compscitech.2019.107887, doi:10.1016/j.compscitech.2019.107887. This article has 166 citations and is from a domain leading peer-reviewed journal.

39. (celik20253dprintedbiocompositesfrom pages 8-11): Esra Celik, Mesut Uysal, Omer Yunus Gumus, and Cagatay Tasdemir. 3d-printed biocomposites from hemp fibers reinforced polylactic acid: thermal, morphology, and mechanical performance. BioResources, 20:331-356, Nov 2025. URL: https://doi.org/10.15376/biores.20.1.331-356, doi:10.15376/biores.20.1.331-356. This article has 12 citations and is from a peer-reviewed journal.