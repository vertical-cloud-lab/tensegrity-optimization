Question: This is a follow-up to Edison task `fad054b3-fef3-4249-a7d3-151d170efe19` (LITERATURE_HIGH, 2026-05-09, "tensegrity designs canonical or not").  That prior survey, together with the STL models we have now committed in `models/stl/` of github.com/vertical-cloud-lab/tensegrity-optimization, covers the following 13 design families:

(1) Snelson n-prism (T3 / T4 / T6) with stable twist theta = pi/2 - pi/n;
(2) Stacked T3 mast / Snelson "Needle Tower" (alternating chirality);
(3) Tibert & Pellegrino deployable mast (multi-bay alternating chirality);
(4) 6-strut tensegrity icosahedron rendered as Jessen's orthogonal icosahedron / expanded octahedron (SUPERball class);
(5) Rimoli & Pajunen truncated-octahedron tensegrity unit cell (energy-absorbing metamaterial);
(6) Liu, Zegard, Pratapa & Paulino (2019) cuboctahedron tensegrity tessellation;
(7) Geiger radial cable-dome (Seoul Olympic Hall / Georgia Dome topology);
(8) Levin / Flemons biotensegrity spine (stacked Jessen-icosahedron vertebrae; basis for Berkeley ULTRA-Spine);
(9) NASA SUPERball with inner payload icosahedron (planetary-lander robot);
(10) Knight, Duffy & Crane US Pat. 6,441,801 B1 hexagonal parallel-platform deployable antenna;
(11) Intrigila et al. (2022) bistable double-prism unit cell (Additive Manufacturing 57:102946);
(12) Skelton class-k (T-bar / D-bar / class-2 columns) -- documented but not built;
(13) Sabouni-Zawadzka simplex lattices -- documented but not built.

QUESTION
What other MAJOR tensegrity design families (canonical, non-canonical, recently published, or in patents / grey literature) are we still MISSING?  In particular, please identify families that:
(a) are mechanically or topologically *distinct* from the 13 above (i.e. not just a reparameterization of an n-prism or icosahedron);
(b) have at least one peer-reviewed or patented description with enough geometric detail (nodal coordinates, connectivity, prestress state) to be reconstructed as a parametric STL;
(c) would be plausibly relevant to a PETG-strut + TPU-tendon FFF-printed crutch-tip / impact-absorber project on a Bambu H2D printer, OR are otherwise canonical enough to be worth cataloguing for completeness.

For each missing family, please provide:
  - Canonical name and one-line description (what makes it distinct);
  - Original / definitive reference (paper, patent number, or technical report) with DOI / patent-office link where available;
  - Approximate counts (number of struts, number of cables, number of nodes for a minimal unit cell);
  - Whether the geometry is class-1, class-2, class-3, or "tensegrity-like" (struts touching);
  - Why we should care (mechanical property, application domain, mathematical interest);
  - If you know of an open-source code/CAD/STL release, name the repo or supplementary materials archive.

Please specifically check for, but do not limit yourself to, the following candidates that we suspect may be missing:
  - Snelson X-Module / X-tensegrity (the "Snelson cross") and Snelson planar-weave tensegrity;
  - Kenneth Snelson "Tetra-Tensegrity" and "V-Expander";
  - Motro 3-bar simplex with alternative cable patterns (saddle vs. diagonal);
  - Pugh's "diamond" and "zig-zag" patterns (Anthony Pugh, 1976, *An Introduction to Tensegrity*);
  - Class-2 / class-3 Skelton minimum-mass columns and beams;
  - C-bar / Y-bar / D-bar Skelton compound elements;
  - Burkhardt's "tetrahedron" and "octahedron" tensegrity (Tensegrity_gen);
  - Hexagonal anti-prism tensegrity (and other higher-rotational-symmetry tensegrities);
  - Tensegrity tori / Mobius tensegrities (Connelly & Whiteley 1996; Murakami 2001);
  - Class-theta double-helix DNA-like tensegrities;
  - Tensegrity catenoids / saddle-surface tensegrities (Hanaor 1992);
  - Hyperboloid / single-sheet ruled-surface tensegrities;
  - Geodesic-tensegrity hybrids (Motro's "tensegrity grids", Hanaor's double-layer tensegrity grids -- distinct from cable-domes);
  - Sabouni-Zawadzka 6V / 4V tensegrity Geodesic domes;
  - Sultan's "saddle tensegrity" and class-2 saddle masts;
  - Pneumatic / inflatable tensegrities (Kanchanasaratool & Williamson; rolling tensegrities);
  - Tensegrity wheels and rovers (Iscen TT-3, Caluwaerts TT-4);
  - Tensegrity robots beyond SUPERball: ULTRA-Spine v2/v3, ReCTeR, TT-Beam, Mountaineer, Vytas;
  - Anand 2022 biodegradable tensegrity (75 m drop survival);
  - Zhang 2018 / Zhang 2022 22" tensegrity (instrumented egg-drop, 60-65% peak-g reduction);
  - DNA / molecular tensegrities (Liedl et al. 2010);
  - Tensegrity-cytoskeleton models (Stamenovic, Ingber) -- biological;
  - 3D-printed monolithic tensegrities (Goh et al. 2022; Liu et al. 2024 4D-printed);
  - Auxetic tensegrity metamaterials (negative-Poisson's-ratio cells);
  - Bistable / multistable tensegrity beams beyond Intrigila (Schenk & Guest 2014; Micheletti 2022);
  - Origami-tensegrity hybrids ("tensegrity-augmented origami", Yasuda et al.);
  - Class-2 minimum-mass T-bar / D-bar Skelton bridges and roofs;
  - Tensegrity domes other than Geiger: Levy dome, Heki dome, Suspen-dome (Kawaguchi 1999);
  - Tensegrity bridges (Rhode-Barbarigos et al. 2010, "tensegrity-ring footbridge");
  - Tensegrity towers other than Snelson Needle Tower: Skelton's tensegrity tower, Sultan & Skelton 2003 tower;
  - Higher-class compound tensegrities: di-tensegrities, tri-tensegrities (Skelton & de Oliveira 2009 ch. 5);
  - Convex / non-convex hull tensegrities and "tensegrity star" forms;
  - Tensegrity arches and tensegrity barrel-vaults (Pellegrino-style);
  - Schek / Linkwitz force-density-method-generated free-form tensegrities;
  - Hawkins / Walker mechanism-based deployable tensegrities;
  - Class-1 tensegrity exoskeleton-like wearables (Hu & Skelton; Yin et al. 2024).

Please also flag anything published in 2023-2026 that didn't make the prior survey.

Where multiple variants of the same family exist, give the *most-distinct* one and note the variants briefly.  If you find more than ~10 missing families, please rank them by likely usefulness to our PETG+TPU/H2D impact-absorber project (best to worst), and call out which one is the single most-buildable next addition.


## Missing Tensegrity Design Families: Gap Analysis and Ranked Recommendations

Below is a systematic identification of major tensegrity design families absent from your current 13-family catalog, ranked by likely usefulness to the PETG-strut + TPU-tendon FFF-printed crutch-tip / impact-absorber project on a Bambu H2D printer, with canonical-for-completeness entries at the bottom.

| Rank | Family Name | One-line Description | Definitive Reference (DOI / patent) | Struts / Cables / Nodes (minimal unit cell) | Class | Why We Should Care | Open-Source CAD / Code |
|---:|---|---|---|---|---|---|---|
| 1 | Snelson X-Module / X-piece | Planar crossed-strut module that seeds planar weaves, hybrid T-prisms, and free-form lattices; topologically distinct from prisms and icosahedra | Motro, *Structural morphology of tensegrity systems*; Snelson patent lineage; summarized in Cowcher 2015 (10.1177/026635119601-228) | Approx. 2 struts / 8 cables / 4 nodes for bare cross-module; larger weave cells vary | Class-1 | Probably the single most buildable next addition: flat-printable, easy PETG+TPU assembly, good for layered pads and shear-compliant impact mats, and historically canonical (cowcher2015designandanalysis pages 120-124, cowcher2015designandanalysis pages 11-15, micheletti2022seventyyearsof pages 3-6) | No canonical STL found; Cowcher thesis tables/figures appear sufficient for reconstruction |
| 2 | 3D-printable tensegrity-inspired truncated-octahedron cell | Buckling-inspired impact cell that behaves like tensegrity but is monolithic / spherical-jointed rather than pure pin-jointed tensegrity | Pajunen et al., *Materials & Design* 2019, 10.1016/j.matdes.2019.107966 | 12 / 36 / ~24 | Tensegrity-like | Directly relevant to crutch-tip / impact absorber work: reusable under impacts, low relative density, good energy-absorption efficiency, STL-friendly periodic lattice cell (pajunen2019designandimpact pages 8-9, pajunen2019designandimpact pages 2-3, pajunen2019designandimpact pages 1-2, pajunen2019designandimpact pages 4-5, pajunen2019designandimpact pages 3-4) | No official STL noted; paper geometry is reconstructable |
| 3 | Reentrant auxetic 3-periodic tensegrity | Chiral cubic periodic tensegrity with re-entrant vertices and auxetic response | Oster et al., *Science Advances* 2021, 10.1126/sciadv.abj6737 | 36 struts / 24 elastic filaments / 24 vertices in cubic unit cell | Class-1 periodic tensegrity | High-value metamaterial family for cushioning: negative Poisson ratio, periodic tessellation, mathematically distinct from prisms/icosahedra, very current and canonical in metamaterials (oster2021reentranttensegritya pages 2-4, oster2021reentranttensegritya pages 1-2, oster2021reentranttensegritya pages 4-7) | No STL found; reconstruction should be feasible from unit-cell data and supplementary geometry |
| 4 | Pentagonal tensegrity-ring module | Hollow ring module with a single strut circuit; basis for deployable footbridges | Rhode-Barbarigos et al., *Engineering Structures* 2010, 10.1016/j.engstruct.2009.12.042; *J. Struct. Eng.* 2012, 10.1061/(ASCE)ST.1943-541X.0000491 | 15 / 30 / 15 | Class-2 | Distinct topology with open central void, deployment by cable change, and nice annular geometry that could inspire compliant protective rings / toe guards / crutch collars (rhodebarbarigos2010designingtensegritymodules pages 3-6, rhodebarbarigos2012mechanismbasedapproachfor pages 3-4, rhodebarbarigos2012atransformabletensegrityring pages 1-3, rhodebarbarigos2010designoftensegrity pages 3-6) | No public STL found; geometry is explicit enough to rebuild |
| 5 | Pugh diamond pattern | Prism-derived family where adjacent triangles are reinforced by paired tendons; canonical morphology separate from simple prism parameter changes | Pugh, *An Introduction to Tensegrity* (1976); summarized in later reviews | Minimal cell usually 3 / 9 / 6 for simplex-derived realizations, but pattern family varies | Class-1 | Canonical-for-completeness and useful as a low-part-count reference family for stacked, graded, or crushable columns (park2013applicationofdesign pages 90-94) | No official repo found |
| 6 | Pugh zig-zag pattern | Alternating tendon-path family with distinct reinforcement lines relative to diamond pattern | Pugh, *An Introduction to Tensegrity* (1976); summarized in reviews | Minimal repeating cell varies; simplex-derived stacks commonly around 3 / 9 / 6 | Class-1 | Worth cataloguing because it is a named canonical morphology and could yield anisotropic crush / bending responses unlike diamond stacking (park2013applicationofdesign pages 90-94) | No official repo found |
| 7 | Tensegrity torus / toroidal modules | Closed-loop torus assembled from X-modules and T-prisms rather than domes or prisms | Murakami 2001, 10.1016/S0020-7683(00)00233-X; modular torus discussed in Cowcher 2015 | Example modular torus: 6 X-modules + 6 T-prisms; exact member count depends on chosen module geometry | Mixed; often Class-1 or Class-2 hybrid modular assemblies | Geometrically distinct ring-like energy absorber; attractive for donut/crutch-tip forms and canonical in tensegrity morphology (cowcher2015designandanalysis pages 11-15, cowcher2015designandanalysis pages 138-143) | No STL found |
| 8 | Hanaor double-layer tensegrity grid | Double-layer modular grid / dome family using tensegrity units rather than cable-dome radial nets | Hanaor & Liao 1991, 10.1061/(ASCE)0733-9445(1991)117:6(1660); Hanaor 1993, 10.1177/0266351193008001-214 | Module counts vary by square/trihex/X-module assembly | Usually Class-1 or Class-2 depending module choice | Major architectural family missing for completeness; also relevant if you want printable multilayer pads with decoupled face-sheet and core behavior (micheletti2022seventyyearsof pages 21-23, charalambides2017squarebasedoublelayertensegrity pages 15-15, cowcher2015designandanalysis pages 138-143, cowcher2015designandanalysis pages 134-138, cowcher2015designandanalysis pages 120-124) | Parametric relations in Charalambides & Liapi 2017; no STL located |
| 9 | Square-base double-layer tensegrity unit | Algorithmic square-base modular unit for flat plates, vaults, and domes | Charalambides & Liapi 2017, 10.1061/(ASCE)AE.1943-5568.0000265 | Varies by assembly method; minimal square-base module not explicitly counted in retrieved excerpt | Class-1 / mixed modular | More printable than large domes: square periodicity is CAD-friendly, packs efficiently, and is relevant to shoe/crutch sole lattices (charalambides2017squarebasedoublelayertensegrity pages 15-15) | Parametric generation method described; no repo cited |
| 10 | Levy / Suspen-dome cable-strut family | Dome family coupling a cable dome with struts / hoop system; distinct from Geiger radial cable domes already in your set | Olofin & Liu 2017, 10.2174/1874149501711010131; Chen et al. 2015, 10.1260/0266-3511.30.1.37 | Large-scale roof system; not naturally a small minimal cell | Tensegrity-like / metatensegrity | Mostly canonical-for-completeness rather than bench-top relevance; still important because Levy / Suspen-dome are major named dome lineages absent from your catalog (elipe2020tensegritiesandtensioned pages 6-7, micheletti2022seventyyearsof pages 13-16, ding2018experimentalstudyand pages 15-16) | No open STL expected |
| 11 | DNA three-strut prestressed prism | Nanoscale DNA-origami tensegrity prism with ssDNA tension springs | Liedl et al., *Nature Nanotechnology* 2010, 10.1038/nnano.2010.107 | 3 / 9 / 6 (one description) | Class-1 | Not relevant to FFF printing, but canonical enough that a complete tensegrity catalog should mention it as the molecular-scale proof of prestressed self-assembly (liedl2010selfassemblyofthreedimensional pages 2-3, liedl2010selfassemblyofthreedimensional pages 1-2) | caDNAno design lineage exists in DNA-nano community; no STL relevance |
| 12 | DNA tensegrity triangle crystal | Threefold-symmetric DNA motif assembling into 3D crystal lattices | Seeman lineage; reviewed in Kong et al. 2023, 10.1002/advs.202302021 | Molecular motif rather than macroscale strut/cable count; crystal motif built from 3 DNA strands in 3:3:1 stoichiometry review context | Molecular tensegrity | Completeness item only; historically important as a literal tensegrity crystal family distinct from macroscopic prisms and domes (kong2023exploringthepotential pages 3-5) | DNA design files in nanotech literature, not STL-oriented |
| 13 | Tensegrity wheel / shape-changing 6-bar icosahedral wheel | Wheel robot using a 6-bar icosahedral tensegrity with a central collapse cable and hubs | US20240351370A1 | 6 / 24 (+ 1 axial actuation cable) / 12 outer rod-end nodes plus hub interfaces | Class-1 core + actuation hybrid | Relevant if you want annular, shock-absorbing, shape-changing protectors; also a concrete patent-family missing from the 13 (US20240351370A1 pages 41-44, US20240351370A1 pages 7-10, US20240351370A1 pages 1-4, US20240351370A1 pages 44-46) | Patent drawings only; no repo found |
| 14 | Zero-stiffness / bistable tensegrity arch-beam family | Prestress-tuned tensegrity-derived mechanisms exhibiting snap-through, zero stiffness, or multistability | Schenk & Guest 2014, 10.1177/0954406213511903 | Not a single canonical count; often paired-arch or clustered cell assemblies | Usually tensegrity-like / prestress mechanism family | Strongly relevant to impact attenuation and load limiting; more of a behavior family than a single topology, but worth cataloguing because it points to printable snap-through absorbers (micheletti2022seventyyearsof pages 21-23) | No canonical STL found |
| 15 | D-bar / class-k auxetic tensegrity metamaterials | Skelton-derived compound-bar cells used for negative Poisson ratio and shock resistance | Ding et al. 2025, *Smart Materials and Structures* 34:055023, 10.1088/1361-665X/add22d | Count depends on chosen D-bar motif; compound-bar rather than single-bar primitive | Class-2 / class-k | One of the best 2025 additions for your use-case: explicitly targets energy absorption and shock resistance and is mechanically distinct from simple prisms (recent citation from search output) | No repo identified |
| 16 | Sabouni-Zawadzka auxetic tensegrity-like lattice | Additively manufactured modular lattice with negative Poisson’s ratio | Sabouni-Zawadzka et al. 2025, *Materials & Design* 258:114513, 10.1016/j.matdes.2025.114513 | Modular lattice; cell counts vary by chosen motif | Tensegrity-like | Directly relevant to printed impact absorbers and fills the gap between canonical tensegrity cells and practical AM auxetic lattices | No repo identified in retrieved evidence |
| 17 | Clustered tensegrity multistable structure | Locally elastically connected clustered tensegrity with tunable multistability | Hao et al. 2026, *Smart Materials and Structures* 35:025017, 10.1088/1361-665X/ae3ff8 | Cluster-based; exact unit count depends on chosen clustered cell | Clustered / tensegrity-like | Good forward-looking family for programmable impact absorbers and adaptive stiffness, though probably a second-wave addition after simpler X-modules and truncated-octa cells | No repo identified |
| 18 | Star-shaped tensegrity-inspired impact lattice | Additively manufactured star-shaped cell optimized for energy absorption and shape recovery | Simmons et al. 2026, *Engineering Research Express* (search hit), 10.1088/2631-8695/ae3530 | Varies by star cell; not provided in retrieved excerpt | Tensegrity-inspired | Very relevant recent impact-absorber direction for FFF, but less canonical than X-modules / ring modules / auxetic periodic tensegrities | No repo identified |


*Table: This table ranks major tensegrity families missing from the current 13-family catalog, emphasizing designs that are either highly relevant to PETG+TPU FFF impact absorbers or canonical enough to include for completeness. It prioritizes families with reconstructable geometry, distinct topology, and credible literature or patent support.*

### Detailed Discussion of Top Candidates

---

#### 1. SINGLE MOST-BUILDABLE NEXT ADDITION: Snelson X-Module / X-Piece

The X-module is Snelson's fundamental planar crossed-strut unit, which is topologically distinct from n-prisms and icosahedra. Three X-modules can be reconfigured into a tensegrity space truss by expanding a central triangle into a T-prism and stabilising with additional cables; the resulting "hybrid T-prism" comprises two concentric T-prisms with a ~π/3 phase difference (cowcher2015designandanalysis pages 120-124). The hybrid T-prism encloses approximately 8× the volume of a basic T-prism for the same strut dimensions, has a high cable-to-strut ratio, and exhibits resilient multi-directional stiffness when prestressed (cowcher2015designandanalysis pages 120-124). X-modules can be clustered in 2D into large-span double-layer grids or geodesic tensegrity domes using alternating left- and right-handed screwed T-prisms (cowcher2015designandanalysis pages 138-143). For your project, the X-module is flat-printable, has low part count (≈2 struts, ≈8 cables, 4 nodes in its bare form), and can be stacked into shear-compliant pads ideal for impact absorption. The definitive description traces through Snelson's patent lineage and Motro's morphological classification (micheletti2022seventyyearsof pages 3-6).

**Recommendation:** This should be the next STL you add.

---

#### 2. 3D-Printable Tensegrity-Inspired Truncated-Octahedron Cell (Pajunen et al. 2019)

This monolithic single-material cell (12 struts, 36 cables, ~24 nodes) was specifically designed for 3D-printable impact absorption. Pajunen et al. fabricated specimens via SLS in polyamide PA2200 and also noted compatibility with SLA, FDM, DLP, and 2-photon polymerization (pajunen2019designandimpact pages 3-4). The spherically-jointed variant achieved the best energy absorption efficiency (Wmin) among tested geometries, with ultra-low relative density (<0.1) and reusability under multiple impacts (pajunen2019designandimpact pages 8-9). Modified designs with 2% prestress absorbed 3.1× the strain energy of the baseline at only 3.6% mass increase (pajunen2019designandimpact pages 4-5). This cell is directly relevant to your PETG+TPU crutch-tip project—it tessellates in 3D and provides post-buckling stability, resilience, and load-limitation (pajunen2019designandimpact pages 1-2). DOI: 10.1016/j.matdes.2019.107966.

---

#### 3. Reentrant Auxetic Three-Periodic Chiral Tensegrity (Oster et al. 2021)

This is a three-periodic, chiral tensegrity derived from the Π+ (β-Mn) helical cylinder packing with I4132 space-group symmetry. The cubic unit cell contains 24 vertices and 36 edges with degree-3 connectivity and re-entrant vertex geometry yielding negative Poisson's ratios of approximately −1.1 and −0.75 depending on direction (oster2021reentranttensegritya pages 2-4, oster2021reentranttensegritya pages 4-7). FEM simulations and a 3D-printed rubber-like prototype confirmed auxetic behavior with cables in tension and struts in compression (oster2021reentranttensegritya pages 4-7). This family is mathematically and topologically distinct from all 13 families in your catalog and represents the state of the art in periodic tensegrity metamaterials. DOI: 10.1126/sciadv.abj6737.

---

#### 4. Pentagonal Tensegrity-Ring Module (Rhode-Barbarigos et al. 2010)

The pentagonal ring module consists of 15 struts in a single circuit, 30 cables, and 15 nodes arranged in three pentagonal layers (rhodebarbarigos2012atransformabletensegrityring pages 1-3). It is classified as a class-2 tensegrity (struts joined end-to-end in circuits) (rhodebarbarigos2012mechanismbasedapproachfor pages 3-4). This module has no infinitesimal mechanisms and six independent states of self-stress (rhodebarbarigos2010designingtensegritymodules pages 3-6). Ring modules were developed for deployable tensegrity footbridges by Rhode-Barbarigos, Motro, and Smith at EPFL, with full-scale deployment demonstrated (rhodebarbarigos2010designingtensegritymodules pages 3-6, rhodebarbarigos2012atransformabletensegrityring pages 1-3). The annular hollow geometry could inspire compliant protective rings or crutch collars. DOI: 10.1016/j.engstruct.2009.12.042.

---

#### 5–6. Pugh Diamond and Zig-Zag Patterns

Anthony Pugh's 1976 classification introduced three canonical cable patterns on spherical tensegrity shells: diamond (where two adjacent triangles are interconnected by two tendons in addition to a strut), zig-zag (with alternating tendon reinforcement lines), and circuit (polygonal circuits of compression struts, fitting class-2 tensegrity) (park2013applicationofdesign pages 90-94). These are distinct morphological families rather than mere reparameterizations of n-prisms. For your project, diamond and zig-zag patterns on small polyhedral shells could yield anisotropic crush responses useful for directional impact management.

---

#### 7. Tensegrity Torus

A tensegrity torus can be assembled from 6 X-modules and 6 T-prisms into a closed ring topology (cowcher2015designandanalysis pages 138-143). This is geometrically distinct from open-ended prisms or spherical icosahedra and could serve as an annular crutch-tip bumper. Murakami (2001) provided quasi-static analysis of cyclic cylindrical tensegrity modules relevant to toroidal assemblies (DOI: 10.1016/S0020-7683(00)00233-X).

---

#### 8. Hanaor Double-Layer Tensegrity Grids

Hanaor's double-layer tensegrity grids (DLTGs) use tensegrity units assembled into flat or curved double-layer configurations, distinct from single-layer cable domes (cowcher2015designandanalysis pages 138-143, cowcher2015designandanalysis pages 134-138). Class-II X-trihex lattices are noted to be more efficient than Class I because struts lie along continuous geodesic curves and are shorter (cowcher2015designandanalysis pages 138-143). Charalambides & Liapi (2017) provided parametric generation methods for square-base double-layer tensegrity units suitable for flat plates, vaults, and domes (charalambides2017squarebasedoublelayertensegrity pages 15-15). DOI: 10.1061/(ASCE)0733-9445(1991)117:6(1660).

---

#### 9–10. Levy Dome / Suspen-Dome

The Levy cable dome uses a triangulated hoop/diagonal cable pattern rather than the radial pattern of the Geiger dome already in your catalog. The Suspen-dome (Kawaguchi 1999) is a hybrid coupling a single-layer reticulated shell with a cable-strut tensegrity system beneath (ding2018experimentalstudyand pages 15-16). These are primarily large-scale architectural systems and less directly relevant to bench-top printing, but are important for catalog completeness.

---

#### 11–12. DNA Tensegrity Prism and Triangle Crystal

Liedl et al. (2010) demonstrated self-assembly of a three-strut DNA tensegrity prism from 13-helix DNA bundles (57 nm long) and nine ssDNA springs, sustaining prestress forces up to 14 pN (liedl2010selfassemblyofthreedimensional pages 2-3, liedl2010selfassemblyofthreedimensional pages 1-2). The DNA tensegrity triangle crystal (Seeman lineage) is a distinct threefold-symmetric motif forming 3D lattices (kong2023exploringthepotential pages 3-5). These are molecular-scale families important for catalog completeness but not for FFF printing.

---

#### 13. Tensegrity Wheel (US 2024/0351370 A1)

This patent describes a 6-bar icosahedral tensegrity wheel with 6 rigid rods (carbon fiber, ~130 mm) and 24 elastic cables (3D-printed TPU), with a central actuation cable enabling collapse/expansion for shape-changing locomotion (US20240351370A1 pages 41-44, US20240351370A1 pages 7-10). The structure weighs ~17 g and provides shock absorption. This is a concrete patent family topologically based on the 6-bar icosahedron but functionally distinct due to the hub/deployment mechanism.

---

#### 14. Zero-Stiffness / Bistable Tensegrity Mechanisms

Schenk & Guest (2014) showed that prestress-tuned tensegrity structures can exhibit zero stiffness, snap-through bistability, and energy-trapping behavior relevant to load-limiting impact absorbers (micheletti2022seventyyearsof pages 21-23). This is more of a behavioral family than a single topology, but it directly informs the design of printable snap-through absorbers for your project.

---

#### 15–18. Recent (2023–2026) Additions

Several recent publications fill gaps:
- **D-bar auxetic tensegrity metamaterials** (Ding et al. 2025, Smart Mater. Struct. 34:055023): Skelton-derived compound-bar cells targeting energy absorption and shock resistance with negative Poisson's ratio.
- **Sabouni-Zawadzka auxetic tensegrity-like lattice** (2025, Materials & Design 258:114513): Additively manufactured modular lattice with experimentally verified negative Poisson's ratio — directly relevant to your FFF project.
- **Multistable clustered tensegrity** (Hao et al. 2026, Smart Mater. Struct. 35:025017): Tunable multistability for programmable impact response.
- **Star-shaped tensegrity-inspired impact lattice** (Simmons et al. 2026, Eng. Res. Express): AM-fabricated star cells optimized for energy absorption and shape recovery.
- **High strain rate tensegrity response** (Almeida et al. 2025, Int. J. Solids Struct.): Dynamic characterization of 3D-printable tensegrity-inspired structures under impact — fills a key data gap for your application.

---

### Summary of Recommendations

1. **Immediate next build (Rank 1):** The **Snelson X-module** is the single most-buildable next addition — it is flat-printable, historically canonical, low part count, and directly useful as a shear-compliant impact pad.

2. **Best impact-absorber candidate (Rank 2):** The **Pajunen truncated-octahedron cell** was explicitly designed for 3D-printed impact absorption with demonstrated reusability and low density, making it the most directly applicable to your PETG+TPU crutch-tip project (pajunen2019designandimpact pages 8-9, pajunen2019designandimpact pages 2-3).

3. **Best metamaterial candidate (Rank 3):** The **Oster reentrant auxetic tensegrity** provides a three-periodic auxetic unit cell that is mathematically rigorous, topologically novel, and could be the basis for a tunable-stiffness crutch tip (oster2021reentranttensegritya pages 2-4).

4. **For catalog completeness:** Pugh diamond/zig-zag patterns, tensegrity torus, Hanaor DLTGs, Levy/Suspen-dome, and DNA tensegrities should be documented even if they are not immediate build priorities.

5. **Recent literature to watch:** The 2025–2026 publications on D-bar auxetic metamaterials, Sabouni-Zawadzka auxetic lattices, multistable clustered tensegrities, and star-shaped impact cells represent active research directions that may yield new printable designs within your project timeline.

References

1. (cowcher2015designandanalysis pages 120-124): DT Cowcher. Design and analysis of geodesic tensegrity structures with agriculture applications. Unknown journal, 2015.

2. (cowcher2015designandanalysis pages 11-15): DT Cowcher. Design and analysis of geodesic tensegrity structures with agriculture applications. Unknown journal, 2015.

3. (micheletti2022seventyyearsof pages 3-6): Andrea Micheletti and Paolo Podio-Guidugli. Seventy years of tensegrities (and counting). Archive of Applied Mechanics, 92:2525-2548, Jul 2022. URL: https://doi.org/10.1007/s00419-022-02192-4, doi:10.1007/s00419-022-02192-4. This article has 76 citations and is from a peer-reviewed journal.

4. (pajunen2019designandimpact pages 8-9): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

5. (pajunen2019designandimpact pages 2-3): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

6. (pajunen2019designandimpact pages 1-2): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

7. (pajunen2019designandimpact pages 4-5): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

8. (pajunen2019designandimpact pages 3-4): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

9. (oster2021reentranttensegritya pages 2-4): Mathias Oster, Marcelo A. Dias, Timo de Wolff, and Myfanwy E. Evans. Reentrant tensegrity: a three-periodic, chiral, tensegrity structure that is auxetic. Science Advances, Dec 2021. URL: https://doi.org/10.1126/sciadv.abj6737, doi:10.1126/sciadv.abj6737. This article has 26 citations and is from a highest quality peer-reviewed journal.

10. (oster2021reentranttensegritya pages 1-2): Mathias Oster, Marcelo A. Dias, Timo de Wolff, and Myfanwy E. Evans. Reentrant tensegrity: a three-periodic, chiral, tensegrity structure that is auxetic. Science Advances, Dec 2021. URL: https://doi.org/10.1126/sciadv.abj6737, doi:10.1126/sciadv.abj6737. This article has 26 citations and is from a highest quality peer-reviewed journal.

11. (oster2021reentranttensegritya pages 4-7): Mathias Oster, Marcelo A. Dias, Timo de Wolff, and Myfanwy E. Evans. Reentrant tensegrity: a three-periodic, chiral, tensegrity structure that is auxetic. Science Advances, Dec 2021. URL: https://doi.org/10.1126/sciadv.abj6737, doi:10.1126/sciadv.abj6737. This article has 26 citations and is from a highest quality peer-reviewed journal.

12. (rhodebarbarigos2010designingtensegritymodules pages 3-6): Landolf Rhode-Barbarigos, Nizar Bel Hadj Ali, René Motro, and Ian F.C. Smith. Designing tensegrity modules for pedestrian bridges. Engineering Structures, 32:1158-1167, Apr 2010. URL: https://doi.org/10.1016/j.engstruct.2009.12.042, doi:10.1016/j.engstruct.2009.12.042. This article has 205 citations and is from a highest quality peer-reviewed journal.

13. (rhodebarbarigos2012mechanismbasedapproachfor pages 3-4): L. Rhode-Barbarigos, C. Schulin, N. Bel Hadj Ali, R. Motro, and I. F. C. Smith. Mechanism-based approach for the deployment of a tensegrity-ring module. Journal of Structural Engineering-asce, 138:539-548, Apr 2012. URL: https://doi.org/10.1061/(asce)st.1943-541x.0000491, doi:10.1061/(asce)st.1943-541x.0000491. This article has 65 citations.

14. (rhodebarbarigos2012atransformabletensegrityring pages 1-3): L Rhode-Barbarigos, R Motro, and IFC Smith. A transformable tensegrity-ring footbridge. Unknown journal, 2012.

15. (rhodebarbarigos2010designoftensegrity pages 3-6): Landolf Rhode-Barbarigos, Himanshu Jain, Prakash Kripakaran, and Ian F. C. Smith. Design of tensegrity structures using parametric analysis and stochastic search. Engineering with Computers, 26:193-203, Apr 2010. URL: https://doi.org/10.1007/s00366-009-0154-1, doi:10.1007/s00366-009-0154-1. This article has 44 citations and is from a peer-reviewed journal.

16. (park2013applicationofdesign pages 90-94): P Park. Application of design synthesis technology in architectural practice. Unknown journal, 2013.

17. (cowcher2015designandanalysis pages 138-143): DT Cowcher. Design and analysis of geodesic tensegrity structures with agriculture applications. Unknown journal, 2015.

18. (micheletti2022seventyyearsof pages 21-23): Andrea Micheletti and Paolo Podio-Guidugli. Seventy years of tensegrities (and counting). Archive of Applied Mechanics, 92:2525-2548, Jul 2022. URL: https://doi.org/10.1007/s00419-022-02192-4, doi:10.1007/s00419-022-02192-4. This article has 76 citations and is from a peer-reviewed journal.

19. (charalambides2017squarebasedoublelayertensegrity pages 15-15): Jason Charalambides and Katherine Liapi. Square-base double-layer tensegrity structures: geometric relations for modular tensegrity assemblies. Journal of Architectural Engineering, 23:04017011, Sep 2017. URL: https://doi.org/10.1061/(asce)ae.1943-5568.0000265, doi:10.1061/(asce)ae.1943-5568.0000265. This article has 3 citations and is from a peer-reviewed journal.

20. (cowcher2015designandanalysis pages 134-138): DT Cowcher. Design and analysis of geodesic tensegrity structures with agriculture applications. Unknown journal, 2015.

21. (elipe2020tensegritiesandtensioned pages 6-7): Mª Dolores Álvarez Elipe. Tensegrities and tensioned structures. ArXiv, 3:10-16, Aug 2020. URL: https://doi.org/10.30564/jaeser.v3i3.2155, doi:10.30564/jaeser.v3i3.2155. This article has 2 citations.

22. (micheletti2022seventyyearsof pages 13-16): Andrea Micheletti and Paolo Podio-Guidugli. Seventy years of tensegrities (and counting). Archive of Applied Mechanics, 92:2525-2548, Jul 2022. URL: https://doi.org/10.1007/s00419-022-02192-4, doi:10.1007/s00419-022-02192-4. This article has 76 citations and is from a peer-reviewed journal.

23. (ding2018experimentalstudyand pages 15-16): Mingmin Ding, Bin Luo, Jie Pan, and Zhengxin Guo. Experimental study and comparative analysis of a geiger-type ridge-beam cable dome structure. International Journal of Civil Engineering, 16:1739-1755, Jun 2018. URL: https://doi.org/10.1007/s40999-018-0331-y, doi:10.1007/s40999-018-0331-y. This article has 16 citations and is from a peer-reviewed journal.

24. (liedl2010selfassemblyofthreedimensional pages 2-3): Tim Liedl, Björn Högberg, Jessica Tytell, Donald E. Ingber, and William M. Shih. Self-assembly of three-dimensional prestressed tensegrity structures from dna. Nature Nanotechnology, 5:520-524, Jun 2010. URL: https://doi.org/10.1038/nnano.2010.107, doi:10.1038/nnano.2010.107. This article has 483 citations and is from a highest quality peer-reviewed journal.

25. (liedl2010selfassemblyofthreedimensional pages 1-2): Tim Liedl, Björn Högberg, Jessica Tytell, Donald E. Ingber, and William M. Shih. Self-assembly of three-dimensional prestressed tensegrity structures from dna. Nature Nanotechnology, 5:520-524, Jun 2010. URL: https://doi.org/10.1038/nnano.2010.107, doi:10.1038/nnano.2010.107. This article has 483 citations and is from a highest quality peer-reviewed journal.

26. (kong2023exploringthepotential pages 3-5): Huating Kong, Bo Sun, Feng Yu, Qisheng Wang, Kai Xia, and Dawei Jiang. Exploring the potential of three‐dimensional dna crystals in nanotechnology: design, optimization, and applications. Advanced Science, Jun 2023. URL: https://doi.org/10.1002/advs.202302021, doi:10.1002/advs.202302021. This article has 25 citations and is from a peer-reviewed journal.

27. (US20240351370A1 pages 41-44): Sydney Spiegel. Mobile robots with shape-changing tensegrity structures. Patent (US), 2024.

28. (US20240351370A1 pages 7-10): Sydney Spiegel. Mobile robots with shape-changing tensegrity structures. Patent (US), 2024.

29. (US20240351370A1 pages 1-4): Sydney Spiegel. Mobile robots with shape-changing tensegrity structures. Patent (US), 2024.

30. (US20240351370A1 pages 44-46): Sydney Spiegel. Mobile robots with shape-changing tensegrity structures. Patent (US), 2024.