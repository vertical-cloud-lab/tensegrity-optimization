# Edison trajectory: 04-tpu-petg-engineering-and-bayesian-optimization

- **Task ID:** `7a21d00e-6fe8-409f-b05d-4b581cc4fa15`
- **Job:** `job-futurehouse-paperqa3-high`
- **Status:** `success`
- **Successful answer:** `True`
- **Created at:** `2026-05-08T17:29:52.613452+00:00`
- **Edison platform link:** https://platform.edisonscientific.com/tasks/7a21d00e-6fe8-409f-b05d-4b581cc4fa15
- **Summary:** LITERATURE_HIGH follow-up: engineering gaps for the TPU+PETG pair (PETG fatigue, PETG-TPU interface, miniaturization to 19-25 mm envelope, prior Bayesian/multi-objective optimization of architected absorbers, integrated lattice + slip-resistant tread).

> The block below is the verbatim `formatted_answer` returned by the Edison client, which includes the original Question, the cited Answer, and the full numbered References list. The raw JSON dump of the response is in the sibling `*.json` file.

---

Question: Targeted follow-up literature review for a BYU Mentored Research Grant proposal on Bayesian-optimized, multi-material 3D-printed tensegrity / lattice inserts for shock-absorbing crutch tips and related small-envelope assistive-device applications. The project is converging on TPU (elastomeric) + PETG (rigid) as the preferred FFF material pair (NOT PLA+TPU as initially scoped). Two prior queries (39708fbc-5964-4fb5-a042-9b13b3475d40, 9832f01a-6bb9-4488-bd88-3131d915f96a) covered the medical motivation and broad prior art; please fill the following engineering gaps quantitatively.

1. PETG MECHANICAL AND FATIGUE PROPERTIES FOR FFF.
   - Quasi-static tensile, compressive, and flexural strength/modulus of FFF PETG as a function of layer height, raster angle, and infill.
   - Fatigue endurance limit (S-N) of FFF PETG at 10^5–10^6 cycles; comparison to FFF PLA endurance (~7–11 MPa) reported in Ezeh & Susmel 2018.
   - Creep, stress relaxation, and moisture/temperature sensitivity relevant to outdoor crutch use.

2. PETG–TPU MULTI-MATERIAL FFF INTERFACE.
   - Mode I and mode II interfacial fracture toughness of PETG–TPU (analogous to Yavas et al. 2022 for PLA–TPU at ~48 J/m^2 mode I, ~220 J/m^2 mode II).
   - Interfacial strength under cyclic compressive and shear loading; delamination behavior; effect of build orientation and interface geometry (saw-tooth, interlocking).
   - Print-process recommendations for strong PETG–TPU adhesion (nozzle temps, bed temp, retraction, purge) on common FFF platforms (Bambu, Prusa, Voron, IDEX).
   - Any published TPU+PETG architected lattices or impact absorbers.

3. MINIATURIZATION OF ARCHITECTED / TENSEGRITY ABSORBERS INTO SMALL ENVELOPES.
   - Smallest published TPU/PETG/PLA tensegrity, octet, gyroid, or auxetic unit cells (target: cells small enough to fit several within a 19–25 mm diameter, <= ~30 mm tall envelope).
   - Size-dependent effects on energy absorption efficiency, densification strain, and load-limiting plateau when miniaturizing FFF lattices to ~5–10 mm cell sizes.
   - Practical FFF resolution limits for small TPU struts/tendons; recommended minimum strut diameter and aspect ratio.

4. BAYESIAN AND MULTI-OBJECTIVE OPTIMIZATION OF ARCHITECTED ABSORBERS.
   - Published applications of Bayesian optimization, Gaussian-process surrogates, or evolutionary multi-objective optimization (NSGA-II/III) to lattice / tensegrity / TPMS / auxetic structures for energy absorption.
   - What design variables are typically used (relative density, strut diameter, unit-cell topology, cell size, prestress, multi-material distribution)?
   - What objective functions and constraints (maximize SEA, minimize peak force or transmitted acceleration; constraint on mass, envelope, manufacturability)?
   - Reported sample-efficiency: number of FE simulations or physical experiments per Pareto-front iteration.
   - Any open-source frameworks used (BoTorch, Ax, GPyOpt, OpenMDAO, Honegumi).

5. INTEGRATED SHOCK-ABSORPTION + SLIP-RESISTANCE / TREAD DESIGN.
   - Examples of multi-material 3D-printed parts that combine an internal energy-absorbing lattice with an external high-friction tread (footwear midsoles, tire treads, robotic feet).
   - Co-printing of TPU outsoles with rigid cores; bonding strategies to elastomeric outer rubber.

DELIVERABLE: cited peer-reviewed sources and patents with specific identifiers, quantitative values wherever possible, and a short concluding summary of: (i) the highest-priority unknowns the BYU project should resolve experimentally for the TPU+PETG pair, and (ii) a recommended starting point for the Bayesian-optimization design space (variables, ranges, and objectives) for a 19–25 mm crutch-tip insert. Do NOT re-derive the medical motivation or broad prior-art summaries already covered by the two earlier tasks.

# Targeted Engineering Literature Review: Bayesian-Optimized Multi-Material (TPU+PETG) FFF Lattice Inserts for Shock-Absorbing Crutch Tips

This review addresses five quantitative engineering gaps for a BYU Mentored Research Grant proposal on TPU (elastomeric) + PETG (rigid) FFF-printed tensegrity/lattice inserts for crutch-tip shock absorption.

---

## 1. PETG Mechanical and Fatigue Properties for FFF

### 1.1 Quasi-Static Properties

FFF-printed PETG exhibits significant sensitivity to process parameters. Algarni & Ghazali (2021) report that raster angle produces modest UTS variation (highest UTS ~45.7 MPa longitudinal, lowest ~41.6 MPa diagonal), with Young's modulus ranging ~1.48–1.62 GPa depending on raster orientation. Infill percentage is the dominant factor: UTS drops from ~32.1 MPa at 100% infill to ~17.4 MPa at 20% (a ~45% reduction). Layer thickness also strongly affects tensile properties, with UTS falling ~30% when layer height increases from 0.1 to 0.2 mm (algarni2021comparativestudyof pages 13-16).

For flexural performance, Tunçel et al. (2024) report optimized PETG flexural strength of 39.55 MPa and flexural modulus of 1344.60 MPa, with values spanning roughly 12.5–79.2 MPa depending on reinforcement, infill, layer height, and raster angle. ANOVA results indicate that layer height predominantly affects flexural modulus, while nozzle temperature significantly impacts flexural strength (tuncel2024optimizationofflexural pages 2-3). Compression properties increase with increasing printing temperature, though the compression response shows pronounced tensile-compression asymmetry (hsueh2021effectofprinting pages 6-8).

### 1.2 Fatigue Endurance

Martins et al. (2024) provide S–N data for FFF PETG (45° raster, R = 0.2, 7 Hz). The fitted power-law relationship is Δσ = 297.74·N^(−0.308) (R² = 0.8931). This yields approximate stress ranges of **Δσ ≈ 8.6 MPa at 10⁵ cycles** and **Δσ ≈ 4.2 MPa at 10⁶ cycles**. For comparison, FFF PLA follows Δσ = 87.46·N^(−0.192), giving Δσ ≈ 9.6 MPa and 6.2 MPa at the same cycle counts. PETG has a steeper S–N slope, meaning its fatigue performance degrades faster than PLA at high cycle counts (martins2024mechanicalpropertiesof pages 8-9). Bakhtiari et al. (2023) note that PETG fatigue rankings depend on raster angle, with 0° prints outperforming others at high stress and 45° prints at lower stress levels (bakhtiari2023effectof3d pages 12-13). For the crutch-tip application (targeting ~10⁵–10⁶ cycles), PETG's endurance limit is comparable to but slightly below PLA, and raster angle selection should be optimized for the dominant loading direction.

### 1.3 Creep, Stress Relaxation, and Environmental Sensitivity

Gama et al. (2026) demonstrate that FFF-printed PETG exhibits low water uptake (<1%) after 10 weeks of immersion at 70°C in distilled and saline water, indicating good dimensional stability for outdoor/marine use. Under UV exposure (up to 1000 h), PETG remained amorphous with only minor molecular-level changes (subtle carbonyl growth, ~2.5°C Tg shift). Tensile strength modestly increased under moderate aging, attributed to partial stress relaxation and improved interlayer cohesion (gama2026structure–propertyrelationshipsof pages 14-17, gama2026structure–propertyrelationshipsof pages 1-2). However, UV exposure increases creep compliance, while elevated temperature and humidity were reported to decrease creep compliance—a competing effect (gama2026structure–propertyrelationshipsof pages 2-4). Hydrolytic chain scission at elevated temperatures can reduce tensile strength by ~6.4% after 21 days at 30°C, with more severe effects at higher temperatures. Prolonged UV-C can cause >30% loss in tensile and compressive properties (gama2026structure–propertyrelationshipsof pages 2-4). These findings indicate PETG is suitable for outdoor crutch use but may benefit from UV-stabilizing additives or protective coatings for long-term deployment.

---

## 2. PETG–TPU Multi-Material FFF Interface

### 2.1 Interfacial Fracture Toughness (PLA–TPU Baseline)

**No published PETG–TPU interfacial fracture toughness data were found in the literature—this is a critical gap the BYU project must resolve experimentally.**

The closest analog is PLA–TPU, characterized by Yavas et al. (2022) using DCB (mode I) and ENF (mode II) tests: mode I fracture toughness **G_Ic = 48 ± 10 J/m²** (steady-state), with crack nucleation energy ~40–60 J/m²; mode II fracture toughness **G_IIc = 220 ± 70 J/m²**, approximately 3–4× the mode I value. Cohesive strengths were σ̂ = 1.0 ± 0.2 MPa (mode I) and τ̂ = 2.7 ± 0.5 MPa (mode II) (yavas2022designandfabrication pages 6-7, yavas2022designandfabrication pages 7-9).

### 2.2 Interface Enhancement Strategies

Altuntaş et al. (2023) demonstrated that sutural/interlocking interface morphology (protrusions created by varying slicer overlap distance from 0–200 µm) can produce a **16–18-fold increase in PLA–TPU interfacial toughness** compared to flat baseline interfaces, with a linear correlation between protrusion amplitude and toughness (altuntas2023enhancinginterfacialtoughness pages 1-4). For CFPA–TPU, Jafor et al. (2024) showed that a hot air gun applied near the nozzle during printing increased mean mode I G_Ic from **12.3 kJ/m² to 33.4 kJ/m²**, with ironing + hot air reducing interfacial void volume fraction by 24% (jafor2024systematicevaluationof pages 1-2, jafor2024systematicevaluationof pages 9-11). Macroscopic mechanical interlocking (T-shaped joints) outperforms microscopic chemical bonding (U-shaped or dovetail joints) for PLA–TPU (catana2024bicomponentadditivemanufacturing pages 6-7). Laminated PLA–TPU interfaces can sustain several MPa of shear stress before debonding (ruwais2025mechanicalperformanceof pages 14-17).

### 2.3 Print-Process Recommendations

Based on the PLA–TPU and CFPA–TPU literature, recommended strategies for strong PETG–TPU adhesion include: (i) increased interface temperature via hot air gun or elevated bed temperature; (ii) sutural/interlocking interface geometries controlled through slicer overlap parameters; (iii) PLA was printed at 200°C, TPU at 223°C on Ultimaker S5 dual-extruder systems (altuntas2024fracturemechanicsbasedinvestigation pages 52-58); (iv) layer height of 0.2 mm and 60°C bed temperature. For PETG–TPU specifically, PETG nozzle temperatures of 230–265°C (higher than PLA) should promote better thermal history at the interface.

### 2.4 Published Multi-Material Architected Lattices

Yavas et al. (2022) demonstrated PLA–TPU multi-material hexagonal lattices with strut thickness t = 3 mm and strut length l = 10 mm. Multi-material struts provided 2–3× greater energy absorption than single-material equivalents, with a progressive failure mode that prevented catastrophic collapse (yavas2022designandfabrication pages 1-2, yavas2022designandfabrication pages 7-9). Khatri & Egan (2024) fabricated ABS–TPU multi-material honeycombs with unit cells of 3.1–3.6 mm, wall thickness 0.4 mm, on an Ultimaker S3. Out-of-plane energy absorption ranged from 2.2 kN·mm (TPU only) to 15.1 kN·mm (ABS only), with hexagonal cells providing 30–66% higher absorption than square cells (khatri2024energyabsorptionof pages 1-3, khatri2024energyabsorptionof pages 7-10). **No published TPU+PETG architected lattice or impact absorber was found.**

---

## 3. Miniaturization of Architected Absorbers into Small Envelopes

### 3.1 Smallest Published FFF Lattice Cells

The smallest published multi-material FFF unit cells found were ABS–TPU honeycombs with unit cell lengths of ~3.1–3.6 mm and wall thickness of 0.4 mm, printed with a 0.4 mm nozzle at 0.2 mm layer height (khatri2024energyabsorptionof pages 3-5). PLA gyroid TPMS lattices with 10 × 10 × 10 mm unit cells have been widely tested (alemayehu2024enhancedenergyabsorption pages 4-6). For the 19–25 mm diameter crutch-tip envelope, 3–4 unit cells of ~5–7 mm could fit across the diameter.

### 3.2 FFF Resolution Limits and Minimum Strut Dimensions

FDM dimensional tolerances are ±0.1–0.2 mm, with typical layer heights of 0.1–0.3 mm and nozzle diameters of 0.4 mm (bustihan2026recentadvancesin pages 6-7). The practical minimum strut/wall thickness is governed by the nozzle diameter: **minimum ~0.4 mm for a 0.4 mm nozzle** (single-wall extrusion). For TPU specifically, reduced print speed (25 mm/s vs. 55 mm/s for rigid materials) and careful retraction are required due to material compliance (khatri2024energyabsorptionof pages 3-5). For reliable structural performance, a minimum strut diameter of 0.8–1.0 mm (2× nozzle diameter) with aspect ratios ≤10:1 is recommended based on the printability studies reviewed.

### 3.3 Size-Dependent Effects

Smaller FFF lattice cells improve deformation uniformity and energy absorption efficiency, though at higher manufacturing complexity. Energy absorption varies by nearly two orders of magnitude (0.02–1.80 MJ/m³) depending on strut length, radius, and density (bustihan2026recentadvancesin pages 23-25). At the targeted 5–10 mm cell scale, surface quality and accuracy issues may not be fully resolved, but printed lattices can still bear compressive loads effectively (alemayehu2024enhancedenergyabsorption pages 4-6).

---

## 4. Bayesian and Multi-Objective Optimization of Architected Absorbers

### 4.1 Published BO Applications

Vangelatos et al. (2021, *Science Advances*) applied Bayesian optimization with an EMCS (Evolutionary Monte Carlo Sampling) framework to a 17-dimensional design space for defected microlattices. The objective was to maximize strain energy density (using critical buckling load P_c as a computationally cheaper proxy). Their BO found the global optimum in a space of ~8.58 × 10⁹ combinations using only **~250 FE evaluations** (initialized with 50 random + 5 intuitive solutions)—an order of magnitude fewer than genetic algorithms. The optimized structure achieved strain energy density 12,464× that of the defect-free baseline (vangelatos2021strengththroughdefects pages 3-4, vangelatos2021strengththroughdefects pages 7-9, vangelatos2021strengththroughdefects pages 1-2).

Mo et al. (2023) used **multifidelity Bayesian optimization** with 16 design variables (half-strut widths, bounded 0.5–1 mm) to optimize energy absorption of triangular lattices. Objectives included maximizing energy absorption (E_ab = area under stress–strain curve to densification) and minimizing plateau stress variation (SD(σ_pl)/σ̄_pl). They combined >3,000 low-fidelity simulations with 120 high-fidelity experiments, demonstrating improved sample efficiency over single-fidelity approaches (mo2023accelerateddesignof pages 1-2, mo2023accelerateddesignof pages 2-4).

### 4.2 Design Variables, Objectives, and Constraints

Typical design variables include: strut/wall thickness, unit-cell topology (categorical), cell orientation, relative density, and (for multi-material) core-to-shell thickness ratio (vangelatos2021strengththroughdefects pages 3-4, mo2023accelerateddesignof pages 1-2, yavas2022designandfabrication pages 1-2). Objective functions include: maximize specific energy absorption (SEA) or strain energy density; minimize peak transmitted force or plateau stress variance; constrain total mass and envelope volume. Acquisition functions used include Expected Improvement (EI), Probability of Improvement (PI), Upper Confidence Bound (UCB), and the novel SMC acquisition (vangelatos2021strengththroughdefects pages 4-5).

### 4.3 Frameworks

The studies reviewed referenced scikit-optimize (GP_skopt, RF_skopt, GBRT_skopt), SMAC3, and Hyperopt (TPE) for benchmarking (vangelatos2021strengththroughdefects pages 4-5). BoTorch, Ax, and GPyOpt were **not explicitly used** in the retrieved lattice-optimization literature, though BoTorch/Ax would be natural choices for the BYU project given their modern GP implementations and multi-objective capabilities.

---

## 5. Integrated Shock-Absorption + Slip-Resistance / Tread Design

### 5.1 Industry Precedents

Adidas' 4D midsole uses Carbon's DLS process to create lattice structures for energy absorption in footwear. Nike's Flyprint and other commercial examples demonstrate FDM-printed TPU shoe components (janke20253dprintingfunctional pages 46-50). Dwyer et al. (2023) evaluated hybrid multi-material lattices (SIL30 elastomer + Ultimaker TPU) for impact protection across a broad energy range, demonstrating that hybrid configurations outperform single-material ones (dwyer2023impactperformanceof pages 1-2).

### 5.2 Co-Printing Strategies

**No published study was found that explicitly co-prints an internal energy-absorbing FFF lattice with an external high-friction tread in a single build.** Janke (2025) notes that practical sneaker prototypes favor separate prints for upper, midsole, and outsole components to accommodate different materials (janke20253dprintingfunctional pages 46-50, janke20253dprintingfunctional pages 35-38). Multi-material lattice reinforcement studies (rosa2024designandcharacterization pages 12-13) and TPU lattice customization for therapeutic products (rosa2024designandcharacterization pages 14-14) provide relevant methodologies that could be adapted. Bonding TPU outsoles to rigid cores remains primarily a post-processing adhesive/thermal-bonding challenge in FFF.

### 5.3 Patent Landscape

Patent searches for "3D printed lattice crutch tip," "multi-material shock absorber walking aid," and "tensegrity energy absorber elastomer rigid polymer" returned no directly relevant patents. The application space for multi-material FFF lattice crutch-tip inserts appears clear of blocking intellectual property.

---

## Concluding Summary

### (i) Highest-Priority Unknowns for Experimental Resolution

1. **PETG–TPU interfacial fracture toughness (mode I and mode II):** No published data exist. The BYU team should conduct DCB and ENF tests per ASTM D5528 and D7905. As a baseline expectation, PLA–TPU gives G_Ic ≈ 48 J/m² and G_IIc ≈ 220 J/m² (yavas2022designandfabrication pages 6-7, yavas2022designandfabrication pages 7-9); PETG–TPU values may differ due to PETG's higher processing temperature and different surface energy.

2. **PETG fatigue at application-relevant conditions:** The endurance limit of ~4–9 MPa (Δσ at 10⁵–10⁶ cycles) should be validated at the specific print orientation and loading mode (compressive/flexural) relevant to the crutch tip (martins2024mechanicalpropertiesof pages 8-9).

3. **PETG–TPU interface durability under cyclic compressive/shear loading and environmental aging:** No cyclic interface fatigue data exist for any rigid–TPU FFF pair.

4. **Miniature lattice printability and performance at 5–7 mm cell size in PETG+TPU:** Size-dependent energy absorption and delamination behavior at this scale are uncharacterized.

5. **Co-printed tread integration:** Bonding an external high-friction TPU tread to a PETG lattice core in a single build has not been demonstrated.

### (ii) Recommended Bayesian-Optimization Starting Point for 19–25 mm Crutch-Tip Insert

**Design Variables (7–10 dimensions):**
- Unit-cell topology: categorical {honeycomb, gyroid TPMS, octet, re-entrant auxetic} (bustihan2026recentadvancesin pages 23-25, vangelatos2021strengththroughdefects pages 3-4)
- Cell size: 5–8 mm (continuous), constrained by envelope (khatri2024energyabsorptionof pages 3-5)
- PETG strut/wall thickness: 0.5–2.0 mm (continuous) (mo2023accelerateddesignof pages 1-2)
- TPU core-to-strut thickness ratio (c/t): 0–0.75 (continuous) (yavas2022designandfabrication pages 1-2, yavas2022designandfabrication pages 7-9)
- Relative density: 15–50% (continuous) (alemayehu2024enhancedenergyabsorption pages 4-6)
- Number of grading levels (axial): 1–3 (integer) (dwyer2023impactperformanceof pages 1-2)
- Interface overlap distance: 0–200 µm (continuous, for suture toughening) (altuntas2023enhancinginterfacialtoughness pages 1-4)

**Objective Functions (multi-objective):**
- Maximize: Specific energy absorption (SEA, J/g) up to densification
- Minimize: Peak transmitted force (proxy for transmitted shock to user's hand)
- Minimize: Plateau stress coefficient of variation (for consistent cushioning) (mo2023accelerateddesignof pages 1-2, mo2023accelerateddesignof pages 2-4)

**Constraints:**
- Envelope: ≤25 mm diameter × ≤30 mm height
- Mass: ≤30 g (typical crutch-tip replacement mass)
- Minimum printable feature: ≥0.8 mm strut diameter (2× nozzle)
- Manufacturability: maximum overhang angle ≤45° without support

**Sample Efficiency Target:** Based on Vangelatos et al., expect convergence in ~100–250 FE evaluations with 30–50 initial random samples (vangelatos2021strengththroughdefects pages 7-9). Multifidelity BO (low-fidelity FEA + high-fidelity physical tests) per Mo et al. can further reduce required physical experiments to ~20–40 per Pareto-front iteration (mo2023accelerateddesignof pages 2-4).

**Recommended Framework:** BoTorch (PyTorch-based) with multi-objective acquisition (qNEHVI) for Pareto-front exploration, or Ax for experiment management. These were not found in the retrieved lattice studies but are the current state-of-the-art for multi-objective BO and would complement the scikit-optimize/SMAC3 tools previously used (vangelatos2021strengththroughdefects pages 4-5).

References

1. (algarni2021comparativestudyof pages 13-16): Mohammed Algarni and Sami Ghazali. Comparative study of the sensitivity of pla, abs, peek, and petg’s mechanical properties to fdm printing process parameters. Crystals, 11:995, Aug 2021. URL: https://doi.org/10.3390/cryst11080995, doi:10.3390/cryst11080995. This article has 283 citations.

2. (tuncel2024optimizationofflexural pages 2-3): Oğuz Tunçel, Çağlar Kahya, and Kenan Tüfekci. Optimization of flexural performance of petg samples produced by fused filament fabrication with response surface method. Polymers, 16:2020, Jul 2024. URL: https://doi.org/10.3390/polym16142020, doi:10.3390/polym16142020. This article has 37 citations.

3. (hsueh2021effectofprinting pages 6-8): Ming-Hsien Hsueh, Chao-Jung Lai, Shi-Hao Wang, Yu-Shan Zeng, Chia-Hsin Hsieh, Chieh-Yu Pan, and Wen-Chen Huang. Effect of printing parameters on the thermal and mechanical properties of 3d-printed pla and petg, using fused deposition modeling. Polymers, 13:1758, May 2021. URL: https://doi.org/10.3390/polym13111758, doi:10.3390/polym13111758. This article has 407 citations.

4. (martins2024mechanicalpropertiesof pages 8-9): Rui F. Martins, Ricardo Branco, Miguel Martins, Wojciech Macek, Zbigniew Marciniak, Rui Silva, Daniela Trindade, Carla Moura, Margarida Franco, and Cândida Malça. Mechanical properties of additively manufactured polymeric materials—pla and petg—for biomechanical applications. Polymers, 16:1868, Jun 2024. URL: https://doi.org/10.3390/polym16131868, doi:10.3390/polym16131868. This article has 36 citations.

5. (bakhtiari2023effectof3d pages 12-13): Hamed Bakhtiari, Muhammad Aamir, and Majid Tolouei-Rad. Effect of 3d printing parameters on the fatigue properties of parts manufactured by fused filament fabrication: a review. Applied Sciences, 13:904, Jan 2023. URL: https://doi.org/10.3390/app13020904, doi:10.3390/app13020904. This article has 135 citations.

6. (gama2026structure–propertyrelationshipsof pages 14-17): Mailyn Gama, Leonardo Santana, Danay Manzo Jaime, Lucas Binder, and Guilherme Mariz de Oliveira Barra. Structure–property relationships of fff-printed petg under uv radiation and water uptake. Journal of Polymer Research, Apr 2026. URL: https://doi.org/10.1007/s10965-026-04876-9, doi:10.1007/s10965-026-04876-9. This article has 0 citations and is from a peer-reviewed journal.

7. (gama2026structure–propertyrelationshipsof pages 1-2): Mailyn Gama, Leonardo Santana, Danay Manzo Jaime, Lucas Binder, and Guilherme Mariz de Oliveira Barra. Structure–property relationships of fff-printed petg under uv radiation and water uptake. Journal of Polymer Research, Apr 2026. URL: https://doi.org/10.1007/s10965-026-04876-9, doi:10.1007/s10965-026-04876-9. This article has 0 citations and is from a peer-reviewed journal.

8. (gama2026structure–propertyrelationshipsof pages 2-4): Mailyn Gama, Leonardo Santana, Danay Manzo Jaime, Lucas Binder, and Guilherme Mariz de Oliveira Barra. Structure–property relationships of fff-printed petg under uv radiation and water uptake. Journal of Polymer Research, Apr 2026. URL: https://doi.org/10.1007/s10965-026-04876-9, doi:10.1007/s10965-026-04876-9. This article has 0 citations and is from a peer-reviewed journal.

9. (yavas2022designandfabrication pages 6-7): Denizhan Yavas, Qingyang Liu, Ziyang Zhang, and Dazhong Wu. Design and fabrication of architected multi-material lattices with tunable stiffness, strength, and energy absorption. Materials &amp; Design, 217:110613, May 2022. URL: https://doi.org/10.1016/j.matdes.2022.110613, doi:10.1016/j.matdes.2022.110613. This article has 144 citations and is from a highest quality peer-reviewed journal.

10. (yavas2022designandfabrication pages 7-9): Denizhan Yavas, Qingyang Liu, Ziyang Zhang, and Dazhong Wu. Design and fabrication of architected multi-material lattices with tunable stiffness, strength, and energy absorption. Materials &amp; Design, 217:110613, May 2022. URL: https://doi.org/10.1016/j.matdes.2022.110613, doi:10.1016/j.matdes.2022.110613. This article has 144 citations and is from a highest quality peer-reviewed journal.

11. (altuntas2023enhancinginterfacialtoughness pages 1-4): UMUT ALTUNTAS, DEMIRKAN COKER, and DENIZHAN YAVAS. Enhancing interfacial toughness in 3d-printed soft-hard interfaces by fused filament fabrication. Proceedings of the 14th International Workshop on Structural Health Monitoring, Sep 2023. URL: https://doi.org/10.12783/shm2023/36727, doi:10.12783/shm2023/36727. This article has 1 citations.

12. (jafor2024systematicevaluationof pages 1-2): Md Abu Jafor, Neshat Sayah, Douglas E. Smith, Gianni Stano, and Trevor J. Fleck. Systematic evaluation of adhesion and fracture toughness in multi-material fused deposition material extrusion. Materials, 17:3953, Aug 2024. URL: https://doi.org/10.3390/ma17163953, doi:10.3390/ma17163953. This article has 12 citations.

13. (jafor2024systematicevaluationof pages 9-11): Md Abu Jafor, Neshat Sayah, Douglas E. Smith, Gianni Stano, and Trevor J. Fleck. Systematic evaluation of adhesion and fracture toughness in multi-material fused deposition material extrusion. Materials, 17:3953, Aug 2024. URL: https://doi.org/10.3390/ma17163953, doi:10.3390/ma17163953. This article has 12 citations.

14. (catana2024bicomponentadditivemanufacturing pages 6-7): M Catana, SN Mazurchevici, and C Cărăușu. Bicomponent additive manufacturing of polymers-a review. Unknown journal, 2024.

15. (ruwais2025mechanicalperformanceof pages 14-17): A Ruwais and N Naveed. Mechanical performance of layered pla–tpu composites using multi-material additive manufacturing. Unknown journal, 2025.

16. (altuntas2024fracturemechanicsbasedinvestigation pages 52-58): U Altuntaş. Fracture mechanics-based investigation of bioinspired soft-hard interfaces fabricated by multi-material additive manufacturing. Unknown journal, 2024.

17. (yavas2022designandfabrication pages 1-2): Denizhan Yavas, Qingyang Liu, Ziyang Zhang, and Dazhong Wu. Design and fabrication of architected multi-material lattices with tunable stiffness, strength, and energy absorption. Materials &amp; Design, 217:110613, May 2022. URL: https://doi.org/10.1016/j.matdes.2022.110613, doi:10.1016/j.matdes.2022.110613. This article has 144 citations and is from a highest quality peer-reviewed journal.

18. (khatri2024energyabsorptionof pages 1-3): Nava Raj Khatri and Paul F. Egan. Energy absorption of 3d printed abs and tpu multimaterial honeycomb structures. 3D Printing and Additive Manufacturing, 11:e840-e850, Apr 2024. URL: https://doi.org/10.1089/3dp.2022.0196, doi:10.1089/3dp.2022.0196. This article has 29 citations and is from a peer-reviewed journal.

19. (khatri2024energyabsorptionof pages 7-10): Nava Raj Khatri and Paul F. Egan. Energy absorption of 3d printed abs and tpu multimaterial honeycomb structures. 3D Printing and Additive Manufacturing, 11:e840-e850, Apr 2024. URL: https://doi.org/10.1089/3dp.2022.0196, doi:10.1089/3dp.2022.0196. This article has 29 citations and is from a peer-reviewed journal.

20. (khatri2024energyabsorptionof pages 3-5): Nava Raj Khatri and Paul F. Egan. Energy absorption of 3d printed abs and tpu multimaterial honeycomb structures. 3D Printing and Additive Manufacturing, 11:e840-e850, Apr 2024. URL: https://doi.org/10.1089/3dp.2022.0196, doi:10.1089/3dp.2022.0196. This article has 29 citations and is from a peer-reviewed journal.

21. (alemayehu2024enhancedenergyabsorption pages 4-6): Dawit Bogale Alemayehu and Masahiro Todoh. Enhanced energy absorption with bioinspired composite triply periodic minimal surface gyroid lattices fabricated via fused filament fabrication (fff). Journal of Manufacturing and Materials Processing, 8:86, Apr 2024. URL: https://doi.org/10.3390/jmmp8030086, doi:10.3390/jmmp8030086. This article has 27 citations.

22. (bustihan2026recentadvancesin pages 6-7): Alin Bustihan and Ioan Botiz. Recent advances in additively manufactured polymeric structures for mechanical energy absorption. Polymers, 18:1019, Apr 2026. URL: https://doi.org/10.3390/polym18091019, doi:10.3390/polym18091019. This article has 0 citations.

23. (bustihan2026recentadvancesin pages 23-25): Alin Bustihan and Ioan Botiz. Recent advances in additively manufactured polymeric structures for mechanical energy absorption. Polymers, 18:1019, Apr 2026. URL: https://doi.org/10.3390/polym18091019, doi:10.3390/polym18091019. This article has 0 citations.

24. (vangelatos2021strengththroughdefects pages 3-4): Zacharias Vangelatos, Haris Moazam Sheikh, Philip S. Marcus, Costas P. Grigoropoulos, Victor Z. Lopez, George Flamourakis, and Maria Farsari. Strength through defects: a novel bayesian approach for the optimization of architected materials. Science Advances, Oct 2021. URL: https://doi.org/10.1126/sciadv.abk2218, doi:10.1126/sciadv.abk2218. This article has 124 citations and is from a highest quality peer-reviewed journal.

25. (vangelatos2021strengththroughdefects pages 7-9): Zacharias Vangelatos, Haris Moazam Sheikh, Philip S. Marcus, Costas P. Grigoropoulos, Victor Z. Lopez, George Flamourakis, and Maria Farsari. Strength through defects: a novel bayesian approach for the optimization of architected materials. Science Advances, Oct 2021. URL: https://doi.org/10.1126/sciadv.abk2218, doi:10.1126/sciadv.abk2218. This article has 124 citations and is from a highest quality peer-reviewed journal.

26. (vangelatos2021strengththroughdefects pages 1-2): Zacharias Vangelatos, Haris Moazam Sheikh, Philip S. Marcus, Costas P. Grigoropoulos, Victor Z. Lopez, George Flamourakis, and Maria Farsari. Strength through defects: a novel bayesian approach for the optimization of architected materials. Science Advances, Oct 2021. URL: https://doi.org/10.1126/sciadv.abk2218, doi:10.1126/sciadv.abk2218. This article has 124 citations and is from a highest quality peer-reviewed journal.

27. (mo2023accelerateddesignof pages 1-2): Chengyang Mo, Paris Perdikaris, and Jordan R. Raney. Accelerated design of architected materials with multifidelity bayesian optimization. Journal of Engineering Mechanics, Jun 2023. URL: https://doi.org/10.1061/jenmdt.emeng-7033, doi:10.1061/jenmdt.emeng-7033. This article has 11 citations.

28. (mo2023accelerateddesignof pages 2-4): Chengyang Mo, Paris Perdikaris, and Jordan R. Raney. Accelerated design of architected materials with multifidelity bayesian optimization. Journal of Engineering Mechanics, Jun 2023. URL: https://doi.org/10.1061/jenmdt.emeng-7033, doi:10.1061/jenmdt.emeng-7033. This article has 11 citations.

29. (vangelatos2021strengththroughdefects pages 4-5): Zacharias Vangelatos, Haris Moazam Sheikh, Philip S. Marcus, Costas P. Grigoropoulos, Victor Z. Lopez, George Flamourakis, and Maria Farsari. Strength through defects: a novel bayesian approach for the optimization of architected materials. Science Advances, Oct 2021. URL: https://doi.org/10.1126/sciadv.abk2218, doi:10.1126/sciadv.abk2218. This article has 124 citations and is from a highest quality peer-reviewed journal.

30. (janke20253dprintingfunctional pages 46-50): Justin Daniel Janke. 3d printing functional materials for sneakers. Text, Jan 2025. URL: https://doi.org/10.7273/000004983, doi:10.7273/000004983. This article has 0 citations and is from a peer-reviewed journal.

31. (dwyer2023impactperformanceof pages 1-2): Charles Dwyer, J. Carrillo, J. D. L. De la Peña, Carolyn Carradero Santiago, E. MacDonald, Jerry Rhinehart, Reed M. Williams, Mark Burhop, B. Yelamanchi, and P. Cortes. Impact performance of 3d printed spatially varying elastomeric lattices. Dataset, Apr 2023. URL: https://doi.org/10.17632/9t3rzckcnj, doi:10.17632/9t3rzckcnj. This article has 21 citations.

32. (janke20253dprintingfunctional pages 35-38): Justin Daniel Janke. 3d printing functional materials for sneakers. Text, Jan 2025. URL: https://doi.org/10.7273/000004983, doi:10.7273/000004983. This article has 0 citations and is from a peer-reviewed journal.

33. (rosa2024designandcharacterization pages 12-13): Sergio de la Rosa, Pedro F. Mayuet, Cátia S. Silva, Álvaro M. Sampaio, and Lucía Rodríguez-Parada. Design and characterization of 3d-printed tpu-based lattice structures. application to methodology for the design of personalized therapeutic products. Rapid Prototyping Journal, 30:72-86, Mar 2024. URL: https://doi.org/10.1108/rpj-08-2023-0287, doi:10.1108/rpj-08-2023-0287. This article has 20 citations and is from a peer-reviewed journal.

34. (rosa2024designandcharacterization pages 14-14): Sergio de la Rosa, Pedro F. Mayuet, Cátia S. Silva, Álvaro M. Sampaio, and Lucía Rodríguez-Parada. Design and characterization of 3d-printed tpu-based lattice structures. application to methodology for the design of personalized therapeutic products. Rapid Prototyping Journal, 30:72-86, Mar 2024. URL: https://doi.org/10.1108/rpj-08-2023-0287, doi:10.1108/rpj-08-2023-0287. This article has 20 citations and is from a peer-reviewed journal.
