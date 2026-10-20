Question: This is a FOLLOW-UP literature query for an undergraduate-mentored research
demonstration (PR comment from project lead). The original Edison
LITERATURE_HIGH task (1b90208d-3555-4479-9db0-512d67e69f5f) covered egg
fracture mechanics, tensegrity topology selection, and instrumentation for a
drop test of a raw chicken egg on a multi-material 3D-printed
(PETG strut + TPU 85A tendon) tensegrity. Please do NOT re-derive that
material — focus only on the new questions below.

NEW SCOPE (from the project lead):
We want to mimic a planetary-lander touchdown as closely as possible
(NASA SUPERball-style: rigid payload pod suspended inside a tensegrity shell)
and we want a "rooftop drop" — i.e. NO drag-based slowing (no parachute,
no streamers, no flutter wings, no balloons, no inflated bags that work
primarily by drag/aerodynamic deceleration). The egg sits in a printable
PETG cradle inside the tensegrity. The structure must absorb the impact
purely by elastic / plastic / hyperelastic deformation of the protector
itself on contact with a rigid floor.

QUESTIONS TO ANSWER

1. **Drag-free baseline survey.** What is the published "state of the
   practice" for protecting a fragile payload (egg or egg-equivalent ~30–80 g
   shell-fragile object) in a free-fall drop where drag is intentionally
   excluded as the deceleration mechanism? Survey the engineering-education
   and applied-mechanics literature for drop-tower / building-drop / rooftop
   egg-protector designs whose mechanism of deceleration is one of:
   (a) Crushable foam / honeycomb / lattice / metamaterial cushion (single-
       use plastic deformation),
   (b) Elastic / hyperelastic recoverable cushion (TPU lattice, silicone,
       rubber spring, elastomeric foam),
   (c) Spring / mechanical isolator stack (coil, leaf, bellows, MR damper),
   (d) Granular / particle damper (sand, beads, gels),
   (e) Tensegrity / cable-strut shell (NASA SUPERball lineage,
       icosahedron drone shells),
   (f) Bio-inspired analogues (woodpecker beak, pomelo peel, owl-feather
       sandwich), if any have been demonstrated as drop protectors,
   (g) Anything else with published quantitative survival data.
   For each category, name the canonical reference(s) and report the
   reported survival drop-height, peak deceleration, payload mass, and
   bounding volume / footprint where available.

2. **What is the current "best in class"?** Of the drag-free egg-protection
   designs above, which has the best published combination of
   (i) maximum survivable drop height for an egg-mass payload,
   (ii) lowest specific volume V/m_payload, and
   (iii) lowest specific mass m_protector / m_payload?
   Please give a short ranked shortlist (3–5 designs) with the headline
   numbers and citations, distinguishing single-use vs reusable and
   Earth-gravity vs Mars/Moon-relevant data. Identify any standardized
   "egg-drop benchmark" / "fragile-payload benchmark" used in the
   pedagogy or planetary-lander literature that we could adopt as
   our baseline.

3. **Apples-to-apples benchmark protocol.** Recommend a fair benchmarking
   protocol so that a PETG+TPU tensegrity (with internal PETG egg cradle)
   can be quantitatively compared against the drag-free baselines under
   shared constraints. Please specify:
   - Constraint set: e.g. fixed bounding volume V_max (cite a sensible
     default, e.g. inscribed in a 200 mm sphere or a 200×200×200 mm cube),
     fixed total system mass m_sys, fixed payload mass m_egg ≈ 55 g,
     fixed landing surface (rigid concrete floor per ASTM D5276),
     fixed drop orientation policy (worst-case or random).
   - Primary scalar figure of merit (e.g. critical drop height h_crit at
     which P_survive = 0.5; peak g_max at h = 1 m; specific energy
     absorbed SEA = E_abs / m_protector; volumetric efficiency
     E_abs / V; reusability count N_impact_to_failure).
   - Secondary figures of merit and how to plot them.
   - Statistical replicate count and recommended dose-response design
     (drop-height ladder, n per height, fresh egg per drop).
   - Any existing standards (ASTM D5276 free-fall drop, ASTM F1292
     impact attenuation, ISTA series, MIL-STD-810, etc.) we should
     cite as the methodological backbone.

4. **Where does a tensegrity actually win?** Under each of the proposed
   benchmark constraint sets (bounded V, bounded m, bounded both),
   identify the regime(s) — drop height, payload mass, reusability
   requirement, omnidirectionality requirement — in which a
   PETG+TPU tensegrity is *expected* (per the published mechanics)
   to dominate the baselines. Cite quantitative comparisons where they
   exist (e.g. Bauer 2021 tensegrity vs octet/Kelvin lattices,
   Pajunen 2019 reusability, Zhang 2018 six-bar SUPERball drop,
   Zha 2020/2024 icosahedron drone collision data, Skelton/Sultan
   class-1 tensegrity lander concepts, NASA Tensegrity Robotics
   Toolkit / SUPERball publications). Identify regimes where a
   conventional crushable foam or TPU lattice is expected to beat
   the tensegrity, so the recommended demonstration is honestly
   framed.

5. **Recommended single-figure demo plot.** Propose ONE publication-
   quality figure that would make the strongest case for the tensegrity
   protector under the benchmark of question 3. The figure should
   compare the PETG+TPU tensegrity against 2–4 named baseline designs
   (one per category from question 1) on a common axis pair (e.g.
   peak g vs drop height with a survivability band; or specific energy
   absorbed vs bounding volume with iso-mass contours). Include:
   - Axis specification with units and recommended range.
   - Which baselines to plot and where the published data points sit.
   - The hypothesized location of the tensegrity data and the qualitative
     argument for why it should fall in the winning region.
   - Any caveats / failure modes the figure should disclose.

6. **Quick-look references / suppliers / reproducibility.** Provide a
   short bibliography of the most useful primary sources, plus, where
   relevant, named commercial parts (foams, lattices, MR dampers,
   accelerometer breakouts) so an undergraduate team can reproduce
   the baseline measurements.

Please cite specific peer-reviewed papers, conference proceedings,
NASA technical reports, ASTM/ISTA/MIL standards, and product datasheets
where applicable. Quantitative claims should include units and a primary
source.

# Drag-Free Fragile-Payload Protection: Literature Survey, Benchmarking, and Tensegrity Positioning

## 1. Drag-Free Baseline Survey

The following survey covers published mechanisms for protecting a fragile payload (~30–80 g, shell-fragile) in free-fall drop where aerodynamic drag is intentionally excluded as the deceleration mechanism. The comprehensive summary is provided in the table below.

| Category (a-g) | Mechanism | Canonical Reference(s) | Payload Type & Mass | Max Survivable Drop Height or Impact Velocity | Peak Deceleration (g) | Bounding Volume / Footprint | Single-Use vs Reusable | Key Notes |
|---|---|---|---|---|---|---|---|---|
| (a) | Crushable foam / honeycomb / cellular cushion | Khatri & Egan 2024; EPS/EPP packaging literature | Varies; no egg-mass standardized fragile-payload drop benchmark found in the retrieved corpus | Not reported in retrieved egg-specific rooftop-drop literature | Not reported | Not reported | Primarily single-use / limited-use for crush-based protection | Multimaterial ABS+TPU honeycombs under compression: out-of-plane energy absorption 2.2-11.5 kN·mm (square) and 2.9-15.1 kN·mm (hexagonal) depending on ABS/TPU mix; good tunability but the retrieved source does not report egg rooftop-drop survival data (bustihan2025reusable3dprintedthermoplastic pages 24-25, bustihan2025reusable3dprintedthermoplastic pages 2-4) |
| (b) | Elastic / hyperelastic recoverable TPU lattice / honeycomb | Bates et al. 2016; Bustihan et al. 2025 | Lattice specimens; no egg payload in retrieved studies | Compression/cyclic loading rather than building-drop survival | Not reported | Sample-scale coupons; not reported as lander envelope | Reusable | 3D-printed TPU honeycombs show volumetric energy absorption 0.01-0.34 J/cm^3 up to densification with elastic recovery; TPU 95A hexagonal honeycomb reported 47% energy-absorption efficiency and best balance of elasticity/integrity across repeated cycles (bates20163dprintedpolyurethane pages 18-22, bustihan2025reusable3dprintedthermoplastic pages 5-7, bustihan2025reusable3dprintedthermoplastic pages 2-4) |
| (c) | Spring / mechanical isolator stack | MIL-STD-810H Method 516; general shock-isolation practice | No published egg-payload rooftop-drop exemplar identified in retrieved corpus | No directly comparable drag-free egg-drop result found | Not reported | Not reported | Usually reusable | Relevant as methodological backbone for shock isolation, but the retrieved literature did not yield a canonical spring-stack egg protector with rooftop-drop survival numbers under the stated no-drag constraint (mojzes2018dropperformanceof pages 3-5) |
| (d) | Granular / particle damper | Simonian et al. 2008 (AIAA) | Spacecraft payload shock attenuation context; no egg-specific payload found | No egg-specific free-fall rooftop-drop data found | Not reported | Not reported | Potentially reusable depending on enclosure | Particle damping is discussed as a concept for shock/acoustic attenuation of payloads, but the retrieved source does not provide egg-equivalent drop height, peak-g, or compact-protector benchmark data (lengas2025parameterstudyof pages 65-70) |
| (e) | Tensegrity 6-bar shell / suspended payload pod (SUPERball lineage) | Agogino et al. 2018; Vespignani et al. 2018; Zhang 2022; Zha 2020/2024; Anand et al. 2022; Zhang et al. 2025 | Egg proxy payload (mass not stated) in Agogino; 22 in lander total mass 1.103 kg in Zhang 2022; 252 g total aerial vehicle in Zha 2020; fragile medical payload ~300-500 g in Anand | Agogino: egg survived ~31.67 ft (~9.65 m), structure impact ~13.7 m/s; Zhang 2022: 10 m and 20 m drops; Zha 2020: survived 6.5 m/s collision; Zha 2024: survived 7.8 m/s collision and 7 m drop at 11.7 m/s; SUPERball v2 designed for 8+ m/s and studied up to 15 m/s; Anand 2022: survived drops up to 75 m onto pavement; Zhang 2025: spherical tensegrity with egg survived 5 m, failed at 6 m | Agogino simulation: payload <25 g; Zhang 2022: 155 g at 10 m, 235 g at 20 m | Zhang 2022: 22 in diameter; SUPERball v2: ~2 m diameter, ~36 kg; Zha 2020 rod length 20 cm; Anand footprint not reported | Mostly reusable; Anand biodegradable tensegrity limited to ~4-5 drops before rebuild | Strongest drag-free published family for omnidirectional reusable protection; key tradeoff is larger volume than dense foam/lattice solutions, but superior reusability and orientation tolerance (agogino2018superballbotstructures pages 73-77, vespignani2018designofsuperball pages 1-2, vespignani2018designofsuperball pages 2-4, zhang2022designofimpactresistantc pages 49-52, zhang2022designofimpactresistantb pages 49-52, zha2024designandcontrol pages 9-11, zha2020acollisionresilientaerial pages 1-2, anand2212takingoffwith pages 1-2, zhang2025designandcushioning pages 19-21, zhang2025designandcushioning pages 18-19) |
| (f) | Bio-inspired cellular cushion (pomelo-peel analogue) | Thielen 2013; Speck et al. 2018; Solak 2026 | Natural pomelo fruit; bio-inspired honeycomb simulation specimens | Whole pomelos dropped from several meters onto concrete in cited biomechanical literature; explicit height values not given in retrieved excerpts | Not reported in retrieved excerpt | Fruit-scale; not reported numerically | Natural system reusable only as biological exemplar; engineered analogues vary | Pomelo peel has highly porous graded mesocarp (~80% porosity) and reported energy absorption up to ~1.5 kJ; pomelo-peel-inspired honeycomb simulation reached SEA 7.88 J/g (lazarus2022impactresistancein pages 40-48, speck2018biomechanicsandfunctional pages 407-410, speck2018biomechanicsandfunctional pages 410-413) |
| (f) | Bio-inspired woodpecker analogue implemented as tensegrity fuselage | Aloui et al. 2025 | Winged drone fuselage/payload avionics; mass not reported in retrieved excerpt | Survived controlled impact tests; exact speed not provided in retrieved excerpt | Not reported | Drone fuselage scale | Reusable | Demonstrates translation of woodpecker-inspired head-protection logic into a tensegrity-protected flying robot, but retrieved excerpt lacks compact quantitative drop/peak-g numbers for egg-scale benchmarking (zha2024designandcontrol pages 9-11) |
| (e) | Tensegrity metamaterial lattice / delocalized deformation architecture | Bauer et al. 2021; Pajunen et al. 2019 | Printed lattice specimens: Pajunen sample mass 3.75-5.75 g, sample height 48.3 mm | Pajunen drop-weight repeated impacts; Bauer compression/failure tests rather than rooftop drops | Not reported as payload g; force-plateau/load-limiting behavior shown | Sample height 48.3 mm in Pajunen; relative density 2.5-12% across studies | Reusable | Bauer: up to 25× higher deformability than octet and ~13× more absorbed energy before failure, with delocalized deformation; Pajunen: 24 impacts with average cumulative residual strain 2.28% (<3%), Em = 320 mJ, showing load-limiting and repeatability (bauer2021tensegritymetamaterialstoward pages 6-7, bauer2021tensegritymetamaterialstoward pages 2-3, pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 4-5) |


*Table: This table summarizes the drag-free fragile-payload protection literature across the main mechanism classes relevant to the user's benchmark. It highlights which categories have true drop-test evidence, which only have material-level compression data, and where tensegrity currently has the strongest published case.*

### Category (a): Crushable Foam / Honeycomb / Lattice / Metamaterial Cushion

Multimaterial 3D-printed honeycombs (ABS + TPU) have been characterized under compression by Khatri & Egan (2024), showing out-of-plane energy absorption of 2.2–15.1 kN·mm depending on the ABS/TPU ratio and cell geometry (bustihan2025reusable3dprintedthermoplastic pages 24-25). However, no published drag-free egg-drop survival data with quantitative drop heights were identified in the retrieved literature for this category. Crushable foams (EPS, EPP) are ubiquitous in packaging but their use as standalone egg protectors in a standardized rooftop-drop benchmark has not been formally published with quantitative survival heights in the peer-reviewed corpus.

### Category (b): Elastic / Hyperelastic Recoverable Cushion

3D-printed TPU honeycombs and lattices represent the closest reusable baseline. Bates et al. (2016) reported volumetric energy absorption of 0.01–0.34 J/cm³ for FDM-printed TPU honeycombs with relative densities 0.18–0.49, with full elastic recovery after compression (bates20163dprintedpolyurethane pages 18-22). Bustihan et al. (2025) tested TPU 70A, 85A, and 95A honeycombs, finding that TPU 95A hexagonal honeycombs achieved 47% energy-absorption efficiency and the best balance of reusability across multiple compression cycles (bustihan2025reusable3dprintedthermoplastic pages 5-7, bustihan2025reusable3dprintedthermoplastic pages 2-4). These materials are directly relevant as a baseline for the PETG+TPU tensegrity comparison, though published rooftop-drop survival heights with egg payloads were not found.

### Category (c): Spring / Mechanical Isolator Stack

No published drag-free egg-drop protector using a purely spring/damper mechanism was identified. MIL-STD-810H Method 516.8 (Shock) provides the methodological backbone for shock isolation testing and instrumentation guidance (mojzes2018dropperformanceof pages 3-5).

### Category (d): Granular / Particle Damper

Simonian et al. (2008) discussed particle damping for spacecraft payload shock attenuation, demonstrating the concept for vibration and acoustic environments, but no egg-equivalent fragile-payload free-fall drop data were reported (lengas2025parameterstudyof pages 65-70).

### Category (e): Tensegrity / Cable-Strut Shell

This is the most extensively documented drag-free category:

- **NASA SUPERball lineage (Agogino et al. 2018):** A 6-bar tensegrity with a centrally suspended egg payload survived drops from approximately 9.65 m (31.67 ft). The structure impacted at ~13.7 m/s while the egg experienced an equivalent local impact of ~2 m/s. Simulation indicated payload decelerations below 25 G even at 15 m/s landing speeds (agogino2018superballbotstructures pages 73-77, agogino2018superballbotstructuresa pages 73-77).

- **SUPERball v2 (Vespignani et al. 2018):** A 2-meter diameter, 36 kg, fully actuated six-bar tensegrity robot with 24 actuators and compliant nylon cables (up to 15% stretch). Designed to survive impact velocities upward of 8 m/s, with simulations analyzing up to 15 m/s impacts. Cable stiffness ~4000 N/m produced lowest peak cable forces (~950 N) (vespignani2018designofsuperball pages 1-2, vespignani2018designofsuperball pages 2-4).

- **Zhang (2022) 22″ tensegrity lander:** Drop tests from 10 m (impact velocity 11.8 m/s, peak payload acceleration 155 g) and 20 m (14.3 m/s, 235 g). Robot mass 1.103 kg. All tests remained within a 500 g safety threshold for payload electronics. Spring stiffness of 740 N/m (interior) improved operational life to ~20 drops before spring replacement (zhang2022designofimpactresistantc pages 49-52, zhang2022designofimpactresistantb pages 49-52, zhang2022designofimpactresistant pages 52-58, zhang2022designofimpactresistant pages 49-52).

- **Zha et al. (2020, 2024) icosahedron drone:** A 252 g total-mass aerial vehicle with icosahedron tensegrity shell (rod length 20 cm) survived collisions up to 6.5 m/s (2020) and a 7 m drop at 11.7 m/s (2024). Monte Carlo simulations showed the tensegrity shell produced up to 7.12× lower maximum stress than a conventional propeller guard (zha2024designandcontrol pages 9-11, zha2020acollisionresilientaerial pages 1-2, zha2024designandcontrol pages 4-5).

- **Anand et al. (2022) biodegradable tensegrity:** Wicker/bamboo struts with jute strings and coir padding protected fragile medical payloads (300–500 g) in drops from 25 m up to 75 m onto hard pavement. Limited reuse: 4–5 drops before string degradation required rebuilding (anand2212takingoffwith pages 1-2).

- **Zhang et al. (2025) spherical tensegrity:** A class-II spherical tensegrity with centrally suspended egg payload survived drops up to 5 m; failure occurred at 6 m. Maximum spring internal forces ranged from 13.31 N (2 m) to 50.24 N (6 m, failure) (zhang2025designandcushioning pages 19-21, zhang2025designandcushioning pages 18-19).

- **Rimoli (2016):** Virtual drop test of a 0.5 m diameter tensegrity lander at 6 m/s impact velocity demonstrated bar buckling followed by elastic rebound without catastrophic failure (rimoli2016ontheimpact pages 5-8).

- **Bayandor et al. (2017) TANDEM:** Simulated 180 kg and 260 kg payloads in 1 m diameter tensegrity landers at 10–30 m/s. Peak payload g-loads: 35.3–224.4 g depending on mass and velocity. Nearly all orientations produced peak loads below 120 g (bayandor2017lightweightmultifunctionalplanetarya pages 31-35, bayandor2017lightweightmultifunctionalplanetary pages 31-35).

- **Tensegrity metamaterials (Bauer et al. 2021):** Space-tileable tensegrity metamaterials exhibited up to 25× enhancement in deformability and 13× more energy absorption before failure compared to octet truss lattices, and 4× and 2× versus Kelvin foam, respectively. At 4% relative density, tensegrity retained 70% of initial stiffness at 70% strain while octet retained only 7% (bauer2021tensegritymetamaterialstoward pages 6-7, bauer2021tensegritymetamaterialstoward pages 2-3).

- **Pajunen et al. (2019):** 3D-printed tensegrity-inspired lattices (mass 3.75 g, height 48.3 mm, relative density 2.5%) demonstrated load-limiting behavior under repeated drop-weight impacts. After 24 impacts, cumulative residual strain averaged only 2.28%, with per-impact residual strain of ~0.11%. Maximum pre-densification strain energy was 320 mJ (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 4-5).

### Category (f): Bio-Inspired Analogues

Pomelo peel (Citrus maxima) is the canonical bio-inspired impact absorber. Thielen et al. (2013) and Speck et al. (2018) performed free-fall tests of whole pomelos dropped from several meters onto concrete floors and instrumented platforms, demonstrating fruit survival. The mesocarp has up to 80% porosity and can absorb up to 1.5 kJ of impact energy through pore-collapse plateau mechanisms, with densification beginning at ~55% compressive strain (lazarus2022impactresistancein pages 40-48, speck2018biomechanicsandfunctional pages 410-413, speck2018biomechanicsandfunctional pages 407-410). Pomelo-peel-inspired honeycomb simulations achieved SEA of 7.88 J/g (Solak 2026). Aloui et al. (2025) implemented woodpecker-brain-inspired tensegrity structures as collision-resilient fuselages for winged drones.

### Category (g): Other

The SUPERball NIAC Phase 2 report compared tensegrity lander performance against MER (Mars Exploration Rover) airbag data, showing that at 12 m/s the tensegrity matched airbag capability, and at higher speeds the tensegrity was projected to outperform (sunspiral2015superballbotstructures pages 80-83, sunspiral2015superballbotstructures pages 72-75).

---

## 2. Best in Class: Ranked Shortlist

Based on the published drag-free literature, the following designs represent the best published combinations of maximum survivable drop height, specific volume, and specific mass:

1. **Biodegradable tensegrity + coir padding (Anand et al. 2022):** Survived 75 m drops onto pavement with fragile medical payloads. However, this is effectively single-use (4–5 drops), uses non-standardized natural materials, and lacks accelerometer data. The 75 m figure is the highest published drag-free survival height for a fragile payload (anand2212takingoffwith pages 1-2).

2. **NASA SUPERball-lineage 6-bar tensegrity (Agogino et al. 2018):** Egg payload survived ~10 m free-fall drops, with payload deceleration limited to <25 G (simulation) at 15 m/s impact. Reusable structure. This remains the canonical peer-reviewed egg-specific tensegrity demonstration (agogino2018superballbotstructures pages 73-77).

3. **Zhang (2022) 22″ tensegrity lander:** Survived 20 m drops with peak payload acceleration of 235 g (below 500 g electronics threshold). Mass 1.103 kg, operational life ~20 drops. Best instrumented tensegrity drop-test dataset (zhang2022designofimpactresistantc pages 49-52, zhang2022designofimpactresistant pages 52-58).

4. **Tensegrity metamaterial lattice (Bauer et al. 2021 / Pajunen et al. 2019):** Not tested as a complete drop protector, but offers the strongest material-level case: 25× deformability over octet, reusable over 24+ impacts with <3% residual strain. Represents the material building-block for the most mass-efficient tensegrity cushion (bauer2021tensegritymetamaterialstoward pages 6-7, pajunen2019designandimpact pages 5-7).

5. **TPU 95A honeycomb lattice (Bustihan et al. 2025 / Bates et al. 2016):** Reusable, 3D-printable, 47% energy-absorption efficiency. Not tested as a complete egg protector, but provides the strongest elastic-foam baseline for mass-normalized comparison (bates20163dprintedpolyurethane pages 18-22, bustihan2025reusable3dprintedthermoplastic pages 5-7).

**Standardized egg-drop benchmark:** No formal standardized "egg-drop benchmark" was identified in the peer-reviewed or planetary-lander literature. The Agogino et al. (2018) SUPERball NIAC report egg-drop protocol (incremental 1-foot height increases with egg break as failure criterion) is the closest to a repeatable benchmark and could be adopted as the baseline protocol (agogino2018superballbotstructuresa pages 69-73, agogino2018superballbotstructures pages 73-77).

---

## 3. Apples-to-Apples Benchmark Protocol

The following protocol enables fair quantitative comparison of the PETG+TPU tensegrity against drag-free baselines:

| Section | Parameter | Recommended specification | Purpose / note |
|---|---|---|---|
| Constraint set | Bounding volume | Inscribed in 200 mm diameter sphere, \(V_{max}=4.19\times10^{-3}\,\mathrm{m^3}\) | Gives a compact, packaging-like common envelope and prevents trivial size scaling; consistent with ASTM-style free-fall benchmarking logic (paine1992evaluationandtesting pages 6-9, ralisnawati2025developmentofa pages 4-6) |
| Constraint set | Total system mass | \(m_{sys}\le 500\,\mathrm{g}\) including protector + payload + onboard instrumentation | Forces apples-to-apples comparison on lightweight protectors rather than unlimited-mass designs (mojzes2018dropperformanceof pages 3-5) |
| Constraint set | Payload mass | \(m_{egg}=55\pm5\,\mathrm{g}\) fresh chicken egg | Representative large raw egg benchmark for fragile shell-dominated payloads; use fresh egg for every survival test replicate |
| Constraint set | Landing surface | Rigid concrete floor, minimum 50 mm thick, flat impact surface | Conservative rigid-floor condition aligned with free-fall package-drop practice; disclose any steel plate overlay if used (paine1992evaluationandtesting pages 6-9, ralisnawati2025developmentofa pages 4-6, mojzes2018dropperformanceof pages 3-5) |
| Constraint set | Orientation policy | Worst-case orientation from 3-orientation screening (vertex-down, face-down, edge-down) **and** random orientation set of 3 drops | Captures both deterministic vulnerability and omni-directional robustness, which is especially relevant for tensegrity claims (zhang2022designofimpactresistantc pages 33-37, zhang2022designofimpactresistantb pages 33-37, zhang2022designofimpactresistant pages 33-37) |
| Constraint set | Drop height range | 1 m to 15 m, Bruceton staircase step size \(\Delta h=0.5\,\mathrm{m}\) | Covers classroom-to-rooftop regime and matches literature where tensegrities show transitions in performance (agogino2018superballbotstructures pages 73-77, zhang2022designofimpactresistantc pages 49-52) |
| Primary figure of merit | Critical survival height | \(h_{crit}\): height at which \(P_{survive}=0.50\), estimated by Bruceton up-down method | Best single scalar benchmark because it folds fragility, orientation sensitivity, and protector mechanics into one directly interpretable result (paine1992evaluationandtesting pages 6-9) |
| Primary figure of merit | Reference shock severity | Peak payload acceleration \(g_{max}\) at \(h=3\,\mathrm{m}\) using onboard accelerometer in the egg cradle | Lets reusable and nonreusable concepts be compared at a shared sub-failure reference severity (zhang2022designofimpactresistantc pages 49-52, zhang2022designofimpactresistanta pages 49-52) |
| Secondary figures of merit | Specific energy absorption | \(SEA=E_{abs}/m_{protector}\) in J/g at \(h=3\,\mathrm{m}\) | Rewards light protectors; directly comparable to lattice/metamaterial literature (wu2026energyabsorptionand pages 11-12, bates20163dprintedpolyurethane pages 18-22) |
| Secondary figures of merit | Volumetric efficiency | \(\eta_V=E_{abs}/V_{protector}\) in J/cm³ | Rewards compactness; important because tensegrity often trades volume for stroke (bates20163dprintedpolyurethane pages 18-22) |
| Secondary figures of merit | Reusability count | \(N_{reuse}\): number of drops from \(h=3\,\mathrm{m}\) until first egg failure | Key discriminator where tensegrity and elastic lattices may outperform crushable foams (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8) |
| Secondary figures of merit | Specific mass ratio | \(m_{protector}/m_{egg}\) | Simple efficiency metric for undergraduate comparisons |
| Secondary figures of merit | Specific volume ratio | \(V_{protector}/m_{egg}\) | Captures bulk penalty per payload mass |
| Statistical design | Staircase survival test | Bruceton staircase with fresh egg each drop, \(n\ge20\) eggs per design, \(\Delta h=0.5\,\mathrm{m}\) | Minimum practical design for estimating \(h_{crit}\) with uncertainty bounds (paine1992evaluationandtesting pages 6-9) |
| Statistical design | Fixed-height reference test | \(n=5\) drops at \(h=3\,\mathrm{m}\) per design, fresh egg each drop | Generates directly comparable \(g_{max}\), rebound, deformation, and absorbed-energy summaries |
| Statistical design | Reusability test | Single protector specimen with one egg at a time, repeat drops from \(h=3\,\mathrm{m}\) until failure; \(n\ge3\) protector specimens | Separates one-shot survival from repeat-impact durability (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8, anand2212takingoffwith pages 1-2) |
| Applicable standards | ASTM D5276-98(2017) | Standard Test Method for Drop Test of Loaded Containers by Free Fall | Core methodological backbone for free-fall apparatus, release accuracy, and rigid-surface drop practice (ralisnawati2025developmentofa pages 4-6, mojzes2018dropperformanceof pages 3-5) |
| Applicable standards | ASTM F1292 | Standard Specification for Impact Attenuation of Surfacing Materials | Useful template for reporting impact attenuation and peak deceleration, even though originally surfacing-focused |
| Applicable standards | ISTA 1A | Non-Simulation Integrity Performance Tests | Useful companion standard for package-style handling and reporting discipline (ralisnawati2025developmentofa pages 4-6) |
| Applicable standards | MIL-STD-810H Method 516.8 | Shock | Best citation for instrumentation, shock event capture, and ruggedized test reporting when using onboard sensors |
| Reporting output | Minimum published plots | Plot \(g_{max}\) vs. height, survival fraction vs. height, and \(N_{reuse}\) distribution | These three plots make cross-category comparison transparent and publication-ready |
| Reporting output | Minimum disclosed hardware data | Protector mass, protector volume, egg mass, orientation, accelerometer sampling rate/range, video frame rate, and visible damage mode | Needed to interpret whether failure is due to shell fracture, cradle collision, tendon failure, or shell bottoming-out (agogino2018superballbotstructures pages 73-77) |


*Table: This table gives a shared, standards-anchored benchmark protocol for comparing a PETG+TPU tensegrity egg protector against drag-free baselines. It defines common constraints, figures of merit, replicate counts, and standards so the comparison is quantitatively fair and reproducible.*

Key details:

- **Constraint set:** All protectors must fit within a 200 mm diameter bounding sphere (V_max ≈ 4.19 × 10⁻³ m³), with total system mass ≤ 500 g (protector + egg + instrumentation), payload m_egg = 55 ± 5 g, onto a rigid concrete floor per ASTM D5276 practice (paine1992evaluationandtesting pages 6-9, ralisnawati2025developmentofa pages 4-6). Orientation policy should include both worst-case (vertex/face/edge) and random orientations to test omnidirectionality claims.

- **Primary scalar figure of merit:** h_crit, the critical drop height at which P_survive = 0.50, determined by the Bruceton up-down staircase method (n ≥ 20 fresh eggs, Δh = 0.5 m). This is the single most informative number. A secondary primary metric is peak g_max at a reference height of h = 3 m (paine1992evaluationandtesting pages 6-9, zhang2022designofimpactresistantc pages 49-52).

- **Secondary figures of merit:** SEA = E_abs/m_protector (J/g); volumetric efficiency η_V = E_abs/V_protector (J/cm³); reusability count N_reuse (number of successful drops from h = 3 m until first egg failure); specific mass m_protector/m_egg; specific volume V_protector/m_egg.

- **Plotting:** (1) Survival fraction vs. drop height (logistic dose-response curve); (2) Peak g_max vs. drop height with egg-fracture threshold band (~130–300 g); (3) N_reuse histogram by design category.

- **Statistical replicates:** Bruceton staircase requires n ≥ 20 fresh eggs per design. Fixed-height comparison at h = 3 m requires n = 5 fresh eggs. Reusability test uses n ≥ 3 protector specimens, each dropped repeatedly until failure.

- **Standards backbone:** ASTM D5276-98(2017) for free-fall drop apparatus and protocol; ASTM F1292 for impact attenuation reporting template; ISTA 1A for packaging integrity testing discipline; MIL-STD-810H Method 516.8 for shock instrumentation and data capture guidance (ralisnawati2025developmentofa pages 4-6, mojzes2018dropperformanceof pages 3-5).

---

## 4. Where Does a Tensegrity Actually Win?

### Regimes Where PETG+TPU Tensegrity Dominates

**Reusability under repeated impacts:** This is the tensegrity's strongest published advantage. Pajunen et al. (2019) demonstrated that 3D-printed tensegrity-inspired lattices survived 24 impacts with only 2.28% cumulative residual strain, recovering most deformation viscoelastically within one minute (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8). Crushable foams and octet/Kelvin lattices fail catastrophically after first localization — Bauer et al. (2021) showed octet truss localized damage above just 2.6% strain, while tensegrity structures maintained >90% delocalization efficiency throughout compression (bauer2021tensegritymetamaterialstoward pages 6-7, bauer2021tensegritymetamaterialstoward pages 2-3).

**Omnidirectionality:** The 6-bar tensegrity geometry provides inherently isotropic impact response. Zhang (2022) characterized three landing orientations and showed that while stiffness varies (k = 7.0–15.4 kN/m), the structure absorbs impacts from all orientations without catastrophic failure (zhang2022designofimpactresistantc pages 33-37, zhang2022designofimpactresistantb pages 33-37). Foam blocks and lattice cushions are typically unidirectional.

**Low-density regime (ρ_rel < 5%):** Bauer et al. (2021) showed that at relative densities below ~4%, tensegrity metamaterials absorbed up to 26× more energy before failure than octet truss and 4× more than Kelvin foam. Reducing relative density from 4% to 0.5% increased the tensegrity energy advantage to ~225× over octet (bauer2021tensegritymetamaterialstoward pages 6-7). This is the operating regime of a practical PETG strut + TPU tendon tensegrity.

**Moderate drop heights (3–15 m) with reuse requirement:** The SUPERball egg tests showed survival to ~10 m (agogino2018superballbotstructures pages 73-77), and Zhang (2022) demonstrated 10–20 m drops with the structure remaining functional for ~20 drops (zhang2022designofimpactresistant pages 52-58). A reusable PETG+TPU tensegrity at the 200 mm scale should target h_crit in the 5–10 m range.

### Regimes Where Conventional Designs Are Expected to Win

**Mass-critical single-use applications:** At low relative density, crushable foams and honeycombs offer higher single-shot SEA (J/g) than tensegrities because they can fully densify and absorb energy plastically across the entire volume. The Bauer (2021) data shows octet truss initial yield strength is ~9× higher than tensegrity (bauer2021tensegritymetamaterialstoward pages 6-7). For a one-time-use protector where mass is the binding constraint and reuse is irrelevant, a crushable foam or TPU lattice block will likely beat the tensegrity.

**Volume-critical applications:** Tensegrities require cable stroke distance (deformation gap) to function. A TPU foam block of the same bounding volume has ~100% of its volume actively absorbing energy, while a tensegrity shell may use only 30–50% of the bounding sphere as active deformation zone. For extremely compact packaging where V_protector/m_egg must be minimized, a dense foam or lattice is superior.

**Very low drop heights (h < 2 m):** At low impact energies, the tensegrity's cable network may not engage meaningfully, and a simple foam wrap provides adequate protection with less complexity. Zhang et al. (2025) showed their spherical tensegrity egg protector had modest advantage at 2–3 m drops, with failure occurring at 6 m — suggesting that at small scales, simple padding may suffice (zhang2025designandcushioning pages 19-21).

---

## 5. Recommended Single-Figure Demo Plot

**Proposed figure:** Peak payload acceleration (g_max) vs. drop height (h), with a horizontal egg-fracture survivability band, comparing 4 named designs.

**Axis specification:**
- X-axis: Drop height h (m), range 0–15 m, linear scale
- Y-axis: Peak payload acceleration g_max (g), range 0–500 g, linear scale
- Horizontal band: Egg fracture threshold zone, approximately 130–300 g (based on literature values of egg fracture at 1.7–3.4 m/s equivalent impact velocity)

**Baselines to plot:**
1. **Unprotected egg (control):** Based on Zhang (2022) standalone payload data: 121 g at 1 m, 392 g at 5 m, expected to exceed 500 g past 10 m (zhang2022designofimpactresistantc pages 49-52, zhang2022designofimpactresistant pages 49-52).
2. **TPU 95A honeycomb block** (category b baseline): Estimated from Bates (2016) and Bustihan (2025) compression data, scaled to drop-test conditions. Expected to flatten the g-curve but with orientation sensitivity.
3. **EPS foam shell** (category a baseline): Single-use, expected to show low g at first impact but catastrophic failure on reuse.
4. **PETG+TPU tensegrity** (test article): Hypothesized to track below the egg-fracture band up to h_crit ≈ 5–10 m based on SUPERball egg-drop data (agogino2018superballbotstructures pages 73-77) and Zhang (2022) scaling (zhang2022designofimpactresistantc pages 49-52). The tensegrity curve should show a gradual rise with a wide orientation-insensitive band, entering the fracture zone at higher heights than unidirectional baselines under random orientation.

**Hypothesized tensegrity advantage region:** The tensegrity data should fall below the fracture band over a wider range of heights than the foam/lattice baselines, especially under random orientation drops. The key visual argument is that the tensegrity's g_max curve crosses the fracture threshold at a higher h than the omnidirectional (worst-case) curves of the other designs.

**Caveats to disclose on figure:** (1) Tensegrity has larger bounding volume than foam baselines for same h_crit; (2) First-drop g_max for crushable foam may be lower than tensegrity at the same height; (3) Orientation variance should be shown as error bars or shaded bands; (4) Reusability advantage is not captured in this single-height plot — recommend an inset or companion panel showing N_reuse.

---

## 6. Quick-Look References, Suppliers, and Reproducibility

### Primary Literature Sources

| Topic | Key Reference | Citation |
|---|---|---|
| SUPERball egg drop tests | Agogino, SunSpiral & Atkinson (2018) NIAC Phase 2 Final Report | (agogino2018superballbotstructures pages 73-77) |
| SUPERball v2 design | Vespignani et al. (2018) IROS | (vespignani2018designofsuperball pages 1-2, vespignani2018designofsuperball pages 2-4) |
| SUPERball v1 system design | Sabelhaus et al. (2015) ICRA | (sabelhaus2015systemdesignand pages 1-2) |
| Tensegrity lander drop tests (22″) | Zhang (2022) PhD thesis, UC Berkeley | (zhang2022designofimpactresistantc pages 49-52, zhang2022designofimpactresistant pages 52-58, zhang2022designofimpactresistantc pages 33-37) |
| Tensegrity metamaterial vs. octet/Kelvin | Bauer et al. (2021) Advanced Materials | (bauer2021tensegritymetamaterialstoward pages 6-7, bauer2021tensegritymetamaterialstoward pages 2-3) |
| 3D-printed tensegrity impact/reusability | Pajunen et al. (2019) Materials & Design | (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 4-5) |
| Icosahedron drone collision resilience | Zha et al. (2020) IROS; Zha et al. (2024) IEEE/ASME Trans. Mech. | (zha2024designandcontrol pages 9-11, zha2020acollisionresilientaerial pages 1-2) |
| Biodegradable tensegrity 75 m drop | Anand, Ajith & Sreekumar (2022) arXiv:2212.11625 | (anand2212takingoffwith pages 1-2) |
| Spherical tensegrity cushioning | Zhang et al. (2025) Aerospace | (zhang2025designandcushioning pages 19-21, zhang2025designandcushioning pages 18-19) |
| Tensegrity lander virtual drop test | Rimoli (2016) AIAA SciTech | (rimoli2016ontheimpact pages 5-8) |
| TANDEM tensegrity lander | Bayandor, Schroeder & Samareh (2017) NASA NIAC | (bayandor2017lightweightmultifunctionalplanetarya pages 31-35, bayandor2017lightweightmultifunctionalplanetary pages 31-35) |
| TPU honeycomb energy absorption | Bates et al. (2016) Materials & Design | (bates20163dprintedpolyurethane pages 18-22) |
| TPU honeycomb reusability | Bustihan et al. (2025) Polymers | (bustihan2025reusable3dprintedthermoplastic pages 5-7) |
| ABS+TPU multimaterial honeycomb | Khatri & Egan (2024) 3D Print. Addit. Manuf. | (bustihan2025reusable3dprintedthermoplastic pages 24-25) |
| Pomelo peel biomechanics | Speck et al. (2018) in Plant Biomechanics; Thielen et al. (2013) Bioinsp. Biomim. | (speck2018biomechanicsandfunctional pages 410-413, speck2018biomechanicsandfunctional pages 407-410) |
| Woodpecker-inspired drone | Aloui et al. (2025) Adv. Robotics Res. | (zha2024designandcontrol pages 9-11) |
| ASTM D5276 drop test practice | Ralisnawati & Kurniawan (2025); Paine & Paine (1992) | (paine1992evaluationandtesting pages 6-9, ralisnawati2025developmentofa pages 4-6) |

### Named Commercial Parts for Baseline Reproduction

- **TPU 85A filament:** Sainsmart TPU 85A or NinjaTek NinjaFlex (85A shore) — 1.75 mm FDM filament for tendon/lattice printing
- **PETG filament:** Overture PETG or eSUN PETG — 1.75 mm FDM filament for strut/cradle printing
- **Accelerometer breakout:** Analog Devices ADXL377 (±200 g, 3-axis MEMS) on SparkFun or Adafruit breakout board — suitable for impact measurement up to 200 g; for higher ranges, use PCB Piezotronics 350B04 (±500 g)
- **Data logger:** Arduino Nano 33 IoT with onboard IMU (LSM6DS3, ±16 g) for low-g tests; for high-g, pair ADXL377 with Arduino Nano and SD card shield at ≥1 kHz sampling
- **High-speed camera:** Chronos 1.4 (1000+ fps) or smartphone slow-motion (240–960 fps) for contact time measurement
- **Force plate (optional):** Kistler 9260AA or budget alternative using HX711 + 4× 50 kg load cells
- **EPS foam baseline:** Generic expanded polystyrene packaging foam, 15–30 kg/m³ density, cut to fit bounding sphere
- **TPU lattice baseline:** Print gyroid or honeycomb infill block in TPU 95A at 20–50% infill density using standard FDM slicer

### Key Standards Documents

- ASTM D5276-98(2017): Standard Test Method for Drop Test of Loaded Containers by Free Fall
- ASTM F1292-22: Standard Specification for Impact Attenuation of Surfacing Materials Within the Use Zone of Playground Equipment
- ISTA 1A (2014): Non-Simulation Integrity Performance Tests
- MIL-STD-810H (2019): Environmental Engineering Considerations and Laboratory Tests, Method 516.8 (Shock)


References

1. (bustihan2025reusable3dprintedthermoplastic pages 24-25): Alin Bustihan, Razvan Hirian, and Ioan Botiz. Reusable 3d-printed thermoplastic polyurethane honeycombs for mechanical energy absorption. Polymers, 17:3035, Nov 2025. URL: https://doi.org/10.3390/polym17223035, doi:10.3390/polym17223035. This article has 3 citations.

2. (bustihan2025reusable3dprintedthermoplastic pages 2-4): Alin Bustihan, Razvan Hirian, and Ioan Botiz. Reusable 3d-printed thermoplastic polyurethane honeycombs for mechanical energy absorption. Polymers, 17:3035, Nov 2025. URL: https://doi.org/10.3390/polym17223035, doi:10.3390/polym17223035. This article has 3 citations.

3. (bates20163dprintedpolyurethane pages 18-22): Simon R.G. Bates, Ian R. Farrow, and Richard S. Trask. 3d printed polyurethane honeycombs for repeated tailored energy absorption. Materials & Design, 112:172-183, Dec 2016. URL: https://doi.org/10.1016/j.matdes.2016.08.062, doi:10.1016/j.matdes.2016.08.062. This article has 388 citations and is from a highest quality peer-reviewed journal.

4. (bustihan2025reusable3dprintedthermoplastic pages 5-7): Alin Bustihan, Razvan Hirian, and Ioan Botiz. Reusable 3d-printed thermoplastic polyurethane honeycombs for mechanical energy absorption. Polymers, 17:3035, Nov 2025. URL: https://doi.org/10.3390/polym17223035, doi:10.3390/polym17223035. This article has 3 citations.

5. (mojzes2018dropperformanceof pages 3-5): ÁKOS MOJZES, THOMAS TROST, and KATA VÖRÖSKÖI. Drop performance of dangerous goods packages in the aspect of parcel delivery standards. The 21st IAPRI World Conference on Packaging, Jul 2018. URL: https://doi.org/10.12783/iapri2018/24432, doi:10.12783/iapri2018/24432. This article has 1 citations.

6. (lengas2025parameterstudyof pages 65-70): N Lengas. Parameter study of impact targets in the drop test of packaging for dangerous goods. Unknown journal, 2025.

7. (agogino2018superballbotstructures pages 73-77): AK Agogino, V SunSpiral, and D Atkinson. Super ball bot-structures for planetary landing and exploration. Unknown journal, 2018.

8. (vespignani2018designofsuperball pages 1-2): Massimo Vespignani, Jeffrey M. Friesen, Vytas SunSpiral, and Jonathan Bruce. Design of superball v2, a compliant tensegrity robot for absorbing large impacts. 2018 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), pages 2865-2871, Oct 2018. URL: https://doi.org/10.1109/iros.2018.8594374, doi:10.1109/iros.2018.8594374. This article has 148 citations.

9. (vespignani2018designofsuperball pages 2-4): Massimo Vespignani, Jeffrey M. Friesen, Vytas SunSpiral, and Jonathan Bruce. Design of superball v2, a compliant tensegrity robot for absorbing large impacts. 2018 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), pages 2865-2871, Oct 2018. URL: https://doi.org/10.1109/iros.2018.8594374, doi:10.1109/iros.2018.8594374. This article has 148 citations.

10. (zhang2022designofimpactresistantc pages 49-52): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

11. (zhang2022designofimpactresistantb pages 49-52): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

12. (zha2024designandcontrol pages 9-11): Jiaming Zha, Xiangyu Wu, Ryan Dimick, and Mark W. Mueller. Design and control of a collision-resilient aerial vehicle with an icosahedron tensegrity structure. IEEE/ASME Transactions on Mechatronics, 29:3449-3460, Oct 2024. URL: https://doi.org/10.1109/tmech.2023.3346749, doi:10.1109/tmech.2023.3346749. This article has 24 citations.

13. (zha2020acollisionresilientaerial pages 1-2): Jiaming Zha, Xiangyu Wu, Joseph Kroeger, Natalia Perez, and Mark W. Mueller. A collision-resilient aerial vehicle with icosahedron tensegrity structure. 2020 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), pages 1407-1412, Mar 2020. URL: https://doi.org/10.48550/arxiv.2003.03417, doi:10.48550/arxiv.2003.03417. This article has 68 citations.

14. (anand2212takingoffwith pages 1-2): Madhumati Anand, Vyzag Ajith, and Sanjula Sreekumar. Taking off with biodegradable tensegrities: an eco-friendly emergency medical delivery solution. ArXiv, Dec 2212. URL: https://doi.org/10.48550/arxiv.2212.11625, doi:10.48550/arxiv.2212.11625. This article has 2 citations.

15. (zhang2025designandcushioning pages 19-21): Jing Zhang, Chuang Shi, Kun Geng, Yanzheng Chen, Hongwei Guo, Rongqiang Liu, and Ziming Kou. Design and cushioning performance analysis of spherical tensegrity structures. Aerospace, 12:453, May 2025. URL: https://doi.org/10.3390/aerospace12060453, doi:10.3390/aerospace12060453. This article has 2 citations.

16. (zhang2025designandcushioning pages 18-19): Jing Zhang, Chuang Shi, Kun Geng, Yanzheng Chen, Hongwei Guo, Rongqiang Liu, and Ziming Kou. Design and cushioning performance analysis of spherical tensegrity structures. Aerospace, 12:453, May 2025. URL: https://doi.org/10.3390/aerospace12060453, doi:10.3390/aerospace12060453. This article has 2 citations.

17. (lazarus2022impactresistancein pages 40-48): BS Lazarus. Impact resistance in biological materials as a source of inspiration for engineered designs. Unknown journal, 2022.

18. (speck2018biomechanicsandfunctional pages 407-410): Thomas Speck, Georg Bold, Tom Masselter, Simon Poppinga, Stefanie Schmier, Marc Thielen, and Olga Speck. Biomechanics and functional morphology of plants—inspiration for biomimetic materials and structures. ArXiv, pages 399-433, Jan 2018. URL: https://doi.org/10.1007/978-3-319-79099-2\_18, doi:10.1007/978-3-319-79099-2\_18. This article has 42 citations.

19. (speck2018biomechanicsandfunctional pages 410-413): Thomas Speck, Georg Bold, Tom Masselter, Simon Poppinga, Stefanie Schmier, Marc Thielen, and Olga Speck. Biomechanics and functional morphology of plants—inspiration for biomimetic materials and structures. ArXiv, pages 399-433, Jan 2018. URL: https://doi.org/10.1007/978-3-319-79099-2\_18, doi:10.1007/978-3-319-79099-2\_18. This article has 42 citations.

20. (bauer2021tensegritymetamaterialstoward pages 6-7): Jens Bauer, Julie A. Kraus, Cameron Crook, Julian J. Rimoli, and Lorenzo Valdevit. Tensegrity metamaterials: toward failure‐resistant engineering systems through delocalized deformation. Advanced Materials, Feb 2021. URL: https://doi.org/10.1002/adma.202005647, doi:10.1002/adma.202005647. This article has 203 citations and is from a highest quality peer-reviewed journal.

21. (bauer2021tensegritymetamaterialstoward pages 2-3): Jens Bauer, Julie A. Kraus, Cameron Crook, Julian J. Rimoli, and Lorenzo Valdevit. Tensegrity metamaterials: toward failure‐resistant engineering systems through delocalized deformation. Advanced Materials, Feb 2021. URL: https://doi.org/10.1002/adma.202005647, doi:10.1002/adma.202005647. This article has 203 citations and is from a highest quality peer-reviewed journal.

22. (pajunen2019designandimpact pages 5-7): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

23. (pajunen2019designandimpact pages 7-8): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

24. (pajunen2019designandimpact pages 4-5): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

25. (agogino2018superballbotstructuresa pages 73-77): AK Agogino, V SunSpiral, and D Atkinson. Super ball bot-structures for planetary landing and exploration. Unknown journal, 2018.

26. (zhang2022designofimpactresistant pages 52-58): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

27. (zhang2022designofimpactresistant pages 49-52): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

28. (zha2024designandcontrol pages 4-5): Jiaming Zha, Xiangyu Wu, Ryan Dimick, and Mark W. Mueller. Design and control of a collision-resilient aerial vehicle with an icosahedron tensegrity structure. IEEE/ASME Transactions on Mechatronics, 29:3449-3460, Oct 2024. URL: https://doi.org/10.1109/tmech.2023.3346749, doi:10.1109/tmech.2023.3346749. This article has 24 citations.

29. (rimoli2016ontheimpact pages 5-8): Julian J. Rimoli. On the impact tolerance of tensegrity-based planetary landers. ArXiv, Jan 2016. URL: https://doi.org/10.2514/6.2016-1511, doi:10.2514/6.2016-1511. This article has 69 citations.

30. (bayandor2017lightweightmultifunctionalplanetarya pages 31-35): J Bayandor, K Schroeder, and J Samareh. Lightweight multifunctional planetary probe for extreme environment exploration and locomotion. Unknown journal, 2017.

31. (bayandor2017lightweightmultifunctionalplanetary pages 31-35): J Bayandor, K Schroeder, and J Samareh. Lightweight multifunctional planetary probe for extreme environment exploration and locomotion. Unknown journal, 2017.

32. (sunspiral2015superballbotstructures pages 80-83): V SunSpiral, A Agogino, and D Atkinson. Super ball bot-structures for planetary landing and exploration, niac phase 2 final report. Unknown journal, 2015.

33. (sunspiral2015superballbotstructures pages 72-75): V SunSpiral, A Agogino, and D Atkinson. Super ball bot-structures for planetary landing and exploration, niac phase 2 final report. Unknown journal, 2015.

34. (agogino2018superballbotstructuresa pages 69-73): AK Agogino, V SunSpiral, and D Atkinson. Super ball bot-structures for planetary landing and exploration. Unknown journal, 2018.

35. (paine1992evaluationandtesting pages 6-9): Frank A. Paine and Heather Y. Paine. Evaluation and testing of transport packages. ArXiv, pages 464-476, Jan 1992. URL: https://doi.org/10.1007/978-1-4615-2810-4\_18, doi:10.1007/978-1-4615-2810-4\_18. This article has 0 citations.

36. (ralisnawati2025developmentofa pages 4-6): D Ralisnawati and MP Kurniawan. Development of a low-cost precision drop tester integrating digital height measurement and rapid release mechanism for academic packaging labs. Unknown journal, 2025.

37. (zhang2022designofimpactresistantc pages 33-37): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

38. (zhang2022designofimpactresistantb pages 33-37): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

39. (zhang2022designofimpactresistant pages 33-37): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

40. (zhang2022designofimpactresistanta pages 49-52): AS Zhang. Design of impact-resistant tensegrity landers. Unknown journal, 2022.

41. (wu2026energyabsorptionand pages 11-12): Yinjin Wu, Lvmanlin Wang, Zijian Yi, Qin Su, Yu-kun Qin, and B. Cui. Energy absorption and rebound behavior of 3d-printed tpu lattice structures. Scientific Reports, Mar 2026. URL: https://doi.org/10.1038/s41598-026-36271-1, doi:10.1038/s41598-026-36271-1. This article has 0 citations and is from a peer-reviewed journal.

42. (sabelhaus2015systemdesignand pages 1-2): Andrew P. Sabelhaus, Jonathan Bruce, Ken Caluwaerts, Pavlo Manovi, Roya Fallah Firoozi, Sarah Dobi, Alice M. Agogino, and Vytas SunSpiral. System design and locomotion of superball, an untethered tensegrity robot. 2015 IEEE International Conference on Robotics and Automation (ICRA), pages 2867-2873, May 2015. URL: https://doi.org/10.1109/icra.2015.7139590, doi:10.1109/icra.2015.7139590. This article has 287 citations.