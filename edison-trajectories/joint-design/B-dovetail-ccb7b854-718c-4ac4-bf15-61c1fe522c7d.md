Question: ## Joint design idea: Co-printed mechanical interlock (PETG dovetail/T-slot strut tip + TPU dovetail/T-head cable head)

The PETG strut terminates in a 7 mm wide x 4 mm tall x 5 mm deep T-slot
(or asymmetric dovetail) that opens transverse to the strut axis. The TPU
cable terminates in a matching co-printed T-head / dovetail head. During
the same multi-material H2D print, the TPU dovetail is laid down inside
the PETG slot (TPU first, then PETG closes around the back face on the
next layer), creating a positive mechanical interlock that resists pullout
along the cable axis but allows free rotation. No fasteners, no post-print
assembly. The dovetail geometry is sized so that even at TPU 95A's
~30-40 MPa yield, the head must shear before pulling free. Closest analog:
overmolded furniture inserts, T-slot extrusion fasteners, the mechanical
interlocks used in PolyJet multi-material soft-rigid demonstrators.


CONTEXT (this repository / project):
- Hardware: Bambu Lab H2D IDEX dual-extruder FDM, 0.4 mm nozzle. Single printer in the lab.
- Materials: PETG (struts, compression members, ~6 mm diameter cylinders) and TPU 95A
  (cables, tension members, ~2.4 mm diameter cylinders). PETG and TPU have very poor
  inter-layer chemical adhesion — any PETG-TPU bond essentially has to be mechanical.
- Target structure: T3-prism (3 struts, 9 cables, 60 deg twist) and larger n-bar prisms /
  tensegrity icosahedra. See attached t3-prism README + .scad + iso.png. Currently the
  whole structure is printed as a single fused PETG part with 7 mm joint spheres at each
  vertex; the move to PETG+TPU multi-material is what motivates this joint study.
- Each vertex node has 4 cylindrical members converging on it: 1 PETG strut +
  3 TPU cables (2 along the end-triangle perimeter + 1 saddle/vertical).
- Validation: Lansmont M23 drop tower (5,000 g max, 0.25 ms min half-sine pulse,
  0.1 - 9.8 m/s impact, 80 lb / 36 kg payload envelope) and Polytec QTec single-point
  LDV (sub-pm displacement, +/- 30 m/s velocity, ~100 kHz). Crutch-tip regime
  (75 kg user, 1.4 m/s, 8 g HAVS target) and NASA-lander regime (5 kg payload,
  9.8 m/s, 1500 g GEVS target).
- Simulators we run today (MuJoCo, PyBullet, PyChrono — see attached simulations
  README): rigid struts + ideal massless 1-D tendons. Tendons attach at point sites
  on rigid bodies; joint stiffness is Inf, joint damping is 0, joint mass is 0.

QUESTION: Please give critical feedback on the proposed joint design above for a
PETG (struts) + TPU (cables) tensegrity-like 3D-printed multi-material assembly on the
H2D. In particular:

(1) Is this joint design *manufacturable* on a 0.4 mm nozzle IDEX H2D in a single
    print, given the 6 mm strut / 2.4 mm cable / 7 mm joint sphere envelope, the
    angles members converge at, and the lack of soluble support?
(2) What are the most likely *failure modes* under a single-impact drop test
    (peak force, pull-out, delamination, hinge yielding, TPU creep)? Please give
    rough quantitative bounds where possible (estimated pull-out force, fatigue
    cycles to debond, plateau stress).
(3) How well does it preserve the *modeling assumption* that struts are rigid and
    cables are ideal massless 1-D tendons — i.e. how much of the joint compliance
    leaks into the simulation gap?
(4) What *cited prior art* (papers, theses, patents, well-known
    open-source CAD repos) most closely realize this joint, and what did they
    measure / conclude?
(5) Concrete *numerical recommendations* for first-pass geometry + slicer
    parameters (PETG infill / wall count / layer height; TPU shore / infill /
    walls; overlap or interlock dimensions; H2D IDEX filament-map ordering;
    print orientation).


### Technical assessment of the proposed co-printed PETG–TPU captive dovetail/T-slot joint

#### Summary (what is strong vs. risky)
Your joint concept (TPU “T-head” printed in-place inside a PETG transverse slot that then closes over it) is directionally consistent with how multi-material AM achieves strength when chemical adhesion is poor: by turning the interface into a geometric, positive mechanical interlock rather than a bonded plane. This principle is supported by hard–soft interlock literature: (i) distributed, printable undercuts can raise otherwise-negligible bonding to ~0.6–0.8 MPa average peak stress in silicone–thermoplastic systems, with failure shifting from pull-out to internal fracture when embedment is sufficient, and (ii) millimeter-scale “tooth” interlocking in dual-nozzle FDM can yield ~6–7 MPa tensile and ~18–24 MPa shear strengths in rigid–flexible joints and reveals characteristic pull-out vs tooth-fracture transitions with depth. (rossing2020bondingbetweensilicones pages 13-16, zhang2026mechanicalperformanceof pages 1-2, zhang2026mechanicalperformanceof pages 11-13)

The main risks are *print-in-place mechanics* (roof bridging/ooze, unintended fusing, trapped strings) rather than the interlock concept itself, and *local stress concentrations* (PETG roof/cheek cracking, TPU head/neck tearing) under high-g single-impact loading.

---

## (1) Manufacturability on a 0.4 mm nozzle IDEX H2D (single print, no soluble support)

### Feasibility: likely manufacturable, but only if designed as a “print-in-place captive joint”
Evidence-based manufacturability constraints from FDM interlock work include: minimum printable features near the nozzle diameter (~0.4 mm), need for continuous toolpaths, and overhangs that must bridge between supported points; small features also print *larger* than CAD (e.g., 0.4 mm beams measuring ~0.5 mm), and sagging/inconsistent cross-section is common in small unsupported spans. (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10)

Your geometry (7 mm × 4 mm × 5 mm cavity scale) is in a favorable regime: it is *well above* the 0.4–0.5 mm “feature-resolution” limit, unlike micro-interlocks, so it should be printable if the PETG “roof” closure span is kept short and the cavity is vented. (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10)

### Primary print risks specific to PETG-over-TPU capture
1. **Roof/bridge droop and PETG stringing into the slot**: PETG must bridge/roof over a void that contains TPU (and possibly TPU strings). Small droop is acceptable if you preserve clearance for rotation, but severe droop can fuse the head or create notch-like stress risers in the roof.
2. **Unintended PETG–TPU “weld points”**: You *want* no chemical reliance, but accidental touch points will add friction and lock rotation; also they create unpredictable stress paths.
3. **Cavity cleanliness / venting**: prior interlock work emphasizes cavity venting/fillability (for silicone casting); in print-in-place, the analog is providing escape paths for ooze and a way to avoid pressure/trapped debris in closed cavities. (rossing2020bondingbetweensilicones pages 5-7)
4. **Dimensional drift vs. CAD**: because small walls and beams print thicker than designed (0.4→0.5 mm reported), you must include explicit clearances on non-load-bearing faces. (rossing2020bondingbetweensilicones pages 7-10)

### Converging member angles and lack of support
A transverse-opening slot is beneficial because it avoids deep, downward-facing overhangs inside the joint sphere. The key is to orient the node so that the PETG “closure” is a short bridge in XY, not a long unsupported ceiling. This is consistent with the “overhangs must bridge between supported points” constraint used in prior FDM interlock design. (rossing2020bondingbetweensilicones pages 5-7)

**Manufacturability conclusion:** the joint is manufacturable on a 0.4 mm IDEX system if you (i) cap bridge span, (ii) reserve clearance and seams away from the rotation path, and (iii) enforce a TPU-first / PETG-close sequencing. (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10, zhang2026mechanicalperformanceof pages 2-4)

---

## (2) Likely failure modes under single-impact drop tests (with rough quantitative bounds)

### Material property bounds relevant to your PETG strut and TPU tendon/head
- **FFF PETG (baseline):** ultimate tensile strength ~25–54 MPa and Young’s modulus ~0.9–2.28 GPa (wide range across print conditions/architectures). (lesniowski2025enhancingtheperformance pages 16-18, lesniowski2025enhancingtheperformance pages 14-16)
- **FFF TPU 95A (typical commercial TPU):** ultimate tensile strengths ~9.75–15.17 MPa with extremely high elongation; modulus at 50% strain ~3.8–4.7 MPa for one 95A-grade TPU study. (bruere2023theinfluenceof pages 4-5, bruere2023theinfluenceof pages 2-4)
- **TPU/PCU 95A fatigue context:** 95A PCU (hard-segment TPU-like) can show very high monotonic tensile failure stress (~54 MPa) and shear failure stress ~31 MPa in a specific medical-grade formulation/architecture; 1e6-cycle runouts occur at median cyclic stresses ~3.35–3.66 MPa (strain-controlled fatigue), highlighting that allowable long-life stress is far below monotonic strength. (miller2017fatigueandcyclic pages 86-96, miller2017fatigueandcyclic pages 104-108)

Because filament brands differ, the most defensible “first-pass” numbers for *your* printed cable are the 10–15 MPa UTS and ~4–5 MPa tangent/secant modulus range from the FFF TPU elastomer study, unless you use a PCU-like 95A. (bruere2023theinfluenceof pages 4-5, bruere2023theinfluenceof pages 2-4)

### Dominant joint failure modes (ranked)
1. **TPU head/neck tear or shear (most likely first in pure pull-out)**
   - The mechanical interlock should force failure through TPU bulk shear/tear rather than interface slip.
   - A sanity bound for a 2.4 mm diameter cable: cross-sectional area \(A\approx \pi(1.2\,\mathrm{mm})^2\approx 4.5\,\mathrm{mm}^2\). If the cable UTS is ~12 MPa, straight cable break force is \(F\approx \sigma A\approx 12\,\mathrm{MPa}\times 4.5\,\mathrm{mm}^2\approx 54\,\mathrm{N}\). (bruere2023theinfluenceof pages 2-4)
   - Therefore, **a joint that “beats the cable” should aim for pull-out >~100 N** (≈2× margin) to make the cable, not the joint, the limiting element. This target is consistent with using geometry to exceed the raw tendon strength.
2. **PETG cheek splitting / roof breakout (impact-driven)**
   - PETG is notch-sensitive in printed parts; roof/cheek regions around slots are classic crack initiators under bending and shock.
   - If your interlock becomes “too strong,” the failure may migrate into PETG around the slot, consistent with multimaterial joint studies where strengthening the interface shifts fracture outside the interface due to local cross-sectional reductions/stress concentration. (zatloukal2025optimizinginterfacialadhesion pages 6-10)
3. **Interfacial sliding / pull-out due to shallow capture depth or print defects**
   - In Rossing et al., shallow interlock depth (\(\hat d=0.4\,\mathrm{mm}\)) led to pull-out at the silicone surface, whereas deeper embedment (\(\hat d=0.8\,\mathrm{mm}\)) shifted failure to beam fracture or silicone tensile failure and increased stiffness. This is a direct analog: insufficient “back face” capture (or insufficient PETG roof thickness) will produce pull-out rather than TPU shear. (rossing2020bondingbetweensilicones pages 13-16)
4. **TPU creep / stress relaxation leading to slack cables (system-level failure)**
   - TPU shows viscoelastic stress relaxation with characteristic times spanning ~0.1 to 10^4 s, with half the relaxation occurring in ~50–90 s and equilibrium approached over days in one Maxwell-fit study. (bruere2023theinfluenceof pages 7-8)
   - Under high-g transient impact (0.25 ms half-sine), creep during the pulse is negligible, but **post-impact tension loss / set** can be substantial over minutes–hours, changing prestress and modal properties.

### Rough quantitative joint-strength bounds (what literature suggests is plausible)
- **Soft–rigid interlock interface stresses:** Rossing et al. achieved ~0.6–0.805 MPa mean peak stress in pull-apart tests of silicone mechanically captured by printed thermoplastic interlocks; without interlock, strength was essentially zero. This provides a conservative lower bound on “geometry-only” joining when chemistry is absent. (rossing2020bondingbetweensilicones pages 13-16)
- **Rigid–flexible FDM joint strengths with millimeter teeth:** A dual-nozzle PLA/TPU study reports tensile strengths ~6.6–7.4 MPa and shear strengths up to ~24.5 MPa for interlocking/alternate-deposition strategies, with depth-dependent transitions from pull-out to tooth fracture. These values are for a bonded interface plus interlock, but they indicate what is achievable in FDM when you deliberately enlarge contact area and add tooth-like capture. (zhang2026mechanicalperformanceof pages 1-2, zhang2026mechanicalperformanceof pages 11-13)

Because your joint is a *single, large captive head* (not an array), the correct stress metric is not the same as “bond stress over a flat area.” A practical approach is to **design pull-out capacity to exceed the straight cable break force**, then treat PETG roof/cheek and TPU head/neck as the competing failure sections.

---

## (3) Impact on the modeling assumption (rigid struts + ideal massless 1-D tendons)

### What the joint changes vs. the ideal tendon-site attachment
Your current simulation assumes: (i) tendon attaches at a point site with infinite stiffness, (ii) joint has no mass, no damping, no compliance.

A print-in-place captive TPU head introduces at least four non-idealities:
1. **Axial tendon compliance is large and nonlinear**: TPU 95A shows modulus at 50% strain ~4.4–4.7 MPa in one FFF study; ultimate stress ~11–12 MPa with very high elongation. (bruere2023theinfluenceof pages 2-4)
2. **Time dependence (stress relaxation) is large**: relaxation times spanning ~0.1–10^4 s and equilibrium approached over days implies your tendon force is history-dependent; any prestress will decay measurably over minutes–hours. (bruere2023theinfluenceof pages 7-8)
3. **Joint rotational friction/hysteresis**: even if “free rotation” is designed in, any incidental PETG–TPU contact, seam bulges, or roof droop will create Coulomb-like friction and energy loss not present in the model.
4. **Finite joint mass and offset moment arms**: the TPU head is small but not massless; more importantly, its geometry defines an effective lever arm from strut centerline to tendon line-of-action.

### How much compliance “leaks” into the sim gap?
- If you treat each tendon as a 1-D spring, an approximate small-signal stiffness is \(k \approx EA/L\). Using \(E\sim 4.5\,\mathrm{MPa}\) (TPU at 50% strain), \(A\sim 4.5\,\mathrm{mm}^2\), and \(L\sim 100\,\mathrm{mm}\) (example cable), gives \(k\sim 4.5\times 10^6\,\mathrm{Pa}\times 4.5\times 10^{-6}\,\mathrm{m}^2 / 0.1\,\mathrm{m} \approx 200\,\mathrm{N/m}\) (order-of-magnitude). This is low enough that tendon stretch will materially change structure stiffness compared with “ideal tendon.” (bruere2023theinfluenceof pages 2-4)
- For dynamic modeling, a generalized Maxwell (Prony series) is defensible: equilibrium stress ~1.2–1.3 MPa and relaxation times 10^-1–10^4 s. (bruere2023theinfluenceof pages 7-8)

**Recommendation for simulation closure:** add tendon axial stiffness and viscoelastic relaxation (Maxwell/Prony) and optionally a small rotational friction at the node to match measured hysteresis; otherwise the model will over-predict stiffness and under-predict damping. (bruere2023theinfluenceof pages 7-8, miller2017fatigueandcyclic pages 86-96)

---

## (4) Cited prior art most closely realizing this joint and their conclusions

| Reference | Process / materials | Interlock geometry concept | Key quantitative results | Manufacturability constraints | Relevance to PETG/TPU tensegrity joint |
|---|---|---|---|---|---|
| Rossing et al., 2020, *Materials & Design* | Hybrid fabrication: FDM-printed thermoplastic hard part + cast RTV silicone (Shore A40) | Repeating 3D-printed mechanical interlock cell with vertical beams + crossover beam; functionally analogous to distributed undercuts / dovetails | Best measured joint stress 0.805 MPa for \^b = 2 mm, \^h = 1.2 mm, \^d = 0.8 mm; ~0.6 MPa for 1.2 mm cells; >5.5× stronger than commercial primer (~0.146 MPa); failure transitions from pull-out at shallow depth (\^d = 0.4 mm) to beam breakage or silicone tensile failure at deeper cells; benchmark with no interlock fell apart before measurable load (rossing2020bondingbetweensilicones pages 16-22, rossing2020bondingbetweensilicones pages 13-16, rossing2020bondingbetweensilicones pages 1-5) | Designed around 0.4 mm nozzle limits; minimum printable feature targeted at 0.4 mm; overhangs had to bridge between supported points; printed 0.4 mm beams came out closer to ~0.5 mm; incomplete cells 0.67-5.3%; toolpath continuity and cavity venting/fillability were explicit constraints (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10, rossing2020bondingbetweensilicones pages 13-16) | Closest direct precedent for a mechanically captive soft-rigid interface when chemical adhesion is poor. Strongly supports using geometry, not chemistry, and warns that small printed undercuts deviate from CAD and fail first by pull-out if embedment is too shallow. |
| Zhang et al., 2026, *Int. J. Adv. Manuf. Technol.* | Dual-nozzle FDM rigid-flexible joints: PLA/TPU and PLA/Soft PLA; 0.4 mm nozzle, 0.16 mm layers, 100% infill | Two strategies: tooth-like mechanical interlocking and alternate deposition; interlock parameterized by tooth angle \(\theta\) and depth \(h\) | PLA/TPU tensile strength peaked at 6.58 ± 0.33 MPa for mechanical interlocking (\(\theta=45^\circ, h=2\) mm); alternate deposition reached 7.42 ± 0.33 MPa at large deposition width; max shear for PLA/TPU interlocking 24.47 ± 1.99 MPa at \(\theta=22.5^\circ, h=4\) mm; failure modes included TPU tooth pull-out at lower depth and tooth fracture / shear at larger depth; alternate deposition often failed by interlayer sliding (zhang2026mechanicalperformanceof pages 8-11, zhang2026mechanicalperformanceof pages 1-2, zhang2026mechanicalperformanceof pages 15-17, zhang2026mechanicalperformanceof pages 11-13) | Demonstrated on a 0.4 mm dual-nozzle FDM setup; geometry varied in coarse millimeter-scale teeth (2-4 mm depth, 0-45° angle), which is well within H2D capability and more robust than sub-nozzle features (zhang2026mechanicalperformanceof pages 2-4, zhang2026mechanicalperformanceof pages 6-8, zhang2026mechanicalperformanceof pages 4-6) | Most directly relevant FDM evidence for TPU-like soft-rigid joints. Suggests your captive dovetail should be sized so TPU fails in bulk or tooth shear, not by interfacial slip; also suggests shallow tooth angles reduce shear stress concentration. |
| Hamilton, 2023, University of Glasgow thesis | Printed mechanically interlocking adherends bonded with adhesive; rigid microstructured surfaces | Microstructured interlocking arrays with varying aspect ratio (AR = 0.5, 1, 2) and hybrid AR layouts | Interlocking surfaces increased load capacity up to ~3× over roughened planar control; AR = 1 gave highest load capacity; AR = 2 traded some strength for more strain-to-failure and work-to-failure; hybrid AR=2 edges + AR=1 center improved toughness while reducing bulk fracture risk (hamilton2023analysisofadhesive pages 154-159) | Effective printing resolution ~200 µm; inter-feature resolution limit ~350-400 µm; printed features were wider than designed, requiring empirical corrections; deeper/slender features were less stiff and more defect-sensitive (hamilton2023analysisofadhesive pages 150-154, hamilton2023analysisofadhesive pages 154-159) | Useful design lesson for your node: avoid very aggressive, thin dovetail teeth. Moderate aspect ratio and compliant-edge / stiff-center thinking can reduce stress concentrations at the PETG slot cheeks and TPU head root. |
| Zatloukal et al., 2025, *Materials* | Multimaterial material-extrusion joints among rigid thermoplastics (PC, PETG, PLA, ASA) | Increased-contact-area "tooth" interface and interlayer bonding pressure; not soft-rigid, but directly studies geometric joint strengthening in MEX | Standard PC/PETG-type joint ~15.2 MPa; tooth strategy raised PC/PETG-class joints to ~28.2 MPa; interlayer-pressure strategy to ~29.9 MPa; one tooth-interlock case reached ~35 MPa with >7% elongation; failure often shifted outside interface when geometry was strong enough (zatloukal2025optimizinginterfacialadhesion pages 6-10, zatloukal2025optimizinginterfacialadhesion pages 4-6) | Emphasizes that increased real contact area and deposition pressure matter; abrupt cross-section reductions caused stress concentration and off-interface fracture; not nozzle-limited in the cited excerpt but compatible with standard MEX geometries (zatloukal2025optimizinginterfacialadhesion pages 6-10, zatloukal2025optimizinginterfacialadhesion pages 4-6) | Even though materials were rigid-rigid, it reinforces two points for PETG/TPU: geometric enlargement of the interface works, and the weakest point may move into the PETG strut tip if the dovetail is too aggressive or notchy. |
| Hasanov et al., 2021 review | Review of multimaterial AM interfaces across FDM/PolyJet and graded hard-soft structures | Surveys direct interfaces, graded transitions, and compliant joints rather than one specific tooth geometry | Reports that graded transitions improved T-peel average force / energy release rate by 62% over direct transitions; notes failures typically occur at interfaces and depend strongly on material pairing and print orientation (hasanov2021reviewonadditive pages 19-21) | Highlights generic MMAM constraints: dissimilar materials are hard to bond, dimensional accuracy and size limits matter, and simultaneous multimaterial processing is challenging (hasanov2021reviewonadditive pages 19-21) | Supports your premise that PETG/TPU should be treated as a mechanically joined, not chemically bonded, system; also suggests that any local grading or compliant transition around the node could help if manufacturable. |
| US11548211B2, "Joiners, methods of joining, and related systems for additive manufacturing" | Additive manufacturing concept patent for depositing an anchor/joiner of one material into a receptacle of another | Bulk-deposited second-material anchor inside first-material receptacle; general anchor-in-pocket concept | No published mechanical values in the excerpt, but the claimed method is directly analogous to printing a TPU anchor/head in a PETG receptacle during the same build (US11548211B2 pages 1-2, 2-7) | Conceptually depends on sequencing material deposition so the joiner is printed before the receptacle closes; useful precedent for print-order logic rather than feature-scale data | Useful legal / conceptual prior art analog for your TPU-head-in-PETG-slot idea, even though it does not provide the validation data that the journal papers do. |


*Table: This table summarizes the most relevant cited prior art for mechanically interlocked or co-printed soft–rigid joints, focusing on FDM-compatible geometries, measured strengths, failure modes, and manufacturing constraints. It is useful for benchmarking whether a PETG/TPU captive dovetail on the H2D is realistic and what failure modes to expect first.*

Two especially relevant takeaways:
- **Printability and scaling:** Rossing et al. explicitly targeted 0.4 mm nozzle manufacturability and found that “designed 0.4 mm” features can print closer to ~0.5 mm and that overhang/bridge constraints drive geometry choices. This is directly applicable to your clearance and undercut sizing. (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10)
- **Failure-mode control via embedment:** both Rossing et al. (depth-controlled pull-out vs internal fracture) and Zhang et al. (depth-controlled TPU tooth pull-out vs tooth fracture) show the same design rule: **shallow capture fails by pull-out/sliding; deeper capture pushes failure into bulk shear/tear.** (rossing2020bondingbetweensilicones pages 13-16, zhang2026mechanicalperformanceof pages 11-13)

Also, Hamilton’s thesis provides a generalizable design heuristic: moderate aspect-ratio interlocks maximize load capacity, while higher aspect ratios increase energy absorption/toughness but can reduce peak load and increase defect sensitivity—useful when you want shock tolerance rather than maximal static strength. (hamilton2023analysisofadhesive pages 154-159)

---

## (5) Concrete numerical recommendations (geometry + slicer + sequencing + orientation)

| Category | Parameter | Recommended range | Default pick | Why / notes | Citation |
|---|---|---:|---:|---|---|
| Joint geometry | Slot mouth width | 6.0-7.0 mm | 6.4 mm | Wide enough for 2 perimeter traces plus tolerance inside a 7 mm node envelope; avoid making mouth equal to full head width so PETG retains cheek thickness | (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10) |
| Joint geometry | Internal head width at undercut | 7.0-8.0 mm | 7.4 mm | Gives 0.5 mm capture per side relative to a 6.4 mm mouth; this is a practical first-pass undercut for 0.4 mm nozzle printing | (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 13-16) |
| Joint geometry | Slot internal height | 3.2-4.0 mm | 3.6 mm | Keeps feature printable at 0.16-0.20 mm layers while leaving enough PETG roof thickness above | (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10) |
| Joint geometry | Slot depth along strut axis | 4.0-6.0 mm | 5.0 mm | Depth below ~0.8 mm was weak in prior interlocks; 4-6 mm gives meaningful embedment and rotation room at this scale | (rossing2020bondingbetweensilicones pages 13-16, hamilton2023analysisofadhesive pages 154-159) |
| Joint geometry | Dovetail flank angle from pull axis | 20-35 deg | 25 deg | Moderate flank angle reduces stress concentration and is closer to the shear-optimal shallow tooth behavior seen in FDM interlocks than a steep T-head | (zhang2026mechanicalperformanceof pages 1-2, zhang2026mechanicalperformanceof pages 15-17) |
| Joint geometry | TPU head thickness (top-to-bottom) | 2.4-3.2 mm | 2.8 mm | Thick enough for multiple layers and to keep local TPU stress below bulk failure during pull-out | (bruere2023theinfluenceof pages 2-4, zhang2026mechanicalperformanceof pages 8-11) |
| Joint geometry | TPU neck diameter / thickness | 1.2-1.8 mm | 1.5 mm | About 3-4 nozzle widths; thinner risks tear at head-neck transition, thicker reduces rotation freedom | (rossing2020bondingbetweensilicones pages 5-7, bruere2023theinfluenceof pages 4-5) |
| Joint geometry | PETG cheek thickness each side of slot | 0.8-1.2 mm | 1.0 mm | Minimum ~2 line widths to avoid cheek splitting and to hold roof bridge edges | (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10) |
| Joint geometry | PETG roof thickness over captive head | 0.8-1.2 mm | 1.0 mm | Use at least 4-6 layers at 0.20/0.16 mm to avoid brittle roof peel-through during impact | (rossing2020bondingbetweensilicones pages 7-10, lesniowski2025enhancingtheperformance pages 16-18) |
| Joint geometry | Root fillet at slot corners | 0.6-1.0 mm | 0.8 mm | Reduces PETG notch sensitivity at the strut-tip transition | (hamilton2023analysisofadhesive pages 154-159, lesniowski2025enhancingtheperformance pages 16-18) |
| Joint geometry | TPU head-neck fillet | 0.5-0.8 mm | 0.6 mm | Reduces TPU tear initiation at highest local strain point | (bruere2023theinfluenceof pages 4-5, bruere2023theinfluenceof pages 8-9) |
| Joint geometry | Running clearance TPU-to-PETG on non-load-bearing faces | 0.20-0.35 mm per side | 0.25 mm | Needed because printed features deviate from CAD and PETG/TPU ooze can fuse if modeled at zero gap | (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10, hamilton2023analysisofadhesive pages 150-154) |
| Joint geometry | Intentional load-bearing interference / undercut overlap | 0.40-0.70 mm per side | 0.50 mm | Mechanical retention should come from geometry, not chemical bond; 0.5 mm/side is a conservative first capture | (rossing2020bondingbetweensilicones pages 13-16, zhang2026mechanicalperformanceof pages 8-11) |
| Joint geometry | Vent / purge escape opening from closed cavity | 0.8-1.2 mm dia or slot width | 1.0 mm | Prevents trapped ooze and pressure in captive cavity; also helps inspect whether PETG roof sealed cleanly | (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10) |
| Joint geometry | PETG unsupported roof bridge span | keep <=4 mm ideal, <=5 mm max | 4 mm | Above this, droop risk rises sharply for PETG over a soft TPU cavity without support | (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10) |
| Joint geometry | Minimum printable standalone feature | >=0.45-0.50 mm | 0.50 mm | Prior 0.4 mm designed beams printed closer to 0.5 mm; do not trust exact 0.4 mm CAD features | (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10) |
| PETG print | Layer height | 0.16-0.20 mm | 0.16 mm | Finer layers improve roof closure and slot dimensional control | (miller2017fatigueandcyclic pages 62-67, lesniowski2025enhancingtheperformance pages 16-18) |
| PETG print | Line width | 0.42-0.45 mm | 0.42 mm | Slightly over nozzle size improves inter-road bonding without overfilling small cavities | (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10) |
| PETG print | Walls / perimeters at strut and joint | 4-6 | 5 | High wall count is more useful than sparse infill in small nodes and strut tips | (miller2017fatigueandcyclic pages 62-67, lesniowski2025enhancingtheperformance pages 16-18, valvez2022optimizationofprinting pages 2-3) |
| PETG print | Infill in struts / nodes | 80-100% gyroid or rectilinear | 100% in node, 90% in strut | Impact-loaded joint zones benefit from near-solid sections; prior PETG strength improves with high infill | (valvez2022optimizationofprinting pages 2-3, v2024evaluationofmechanical pages 20-27) |
| PETG print | Nozzle temperature | 245-260 C | 250 C | Higher temperature improves PETG interlayer fusion and strength; avoid wet filament and overheating | (lesniowski2025enhancingtheperformance pages 16-18, hsueh2021effectofprinting pages 8-10, hsueh2021effectofprinting pages 6-8) |
| PETG print | Bed temperature | 75-90 C | 80 C | Supports dimensional stability and adhesion | (lesniowski2025enhancingtheperformance pages 16-18) |
| PETG print | Outer-wall speed near joint | 20-30 mm/s | 25 mm/s | Slow outer walls improve accuracy at slot mouth and roof | (lesniowski2025enhancingtheperformance pages 16-18, hsueh2021effectofprinting pages 6-8) |
| PETG print | Bridge speed for roof closure | 15-25 mm/s | 18 mm/s | Slower bridge over captive head reduces droop | (rossing2020bondingbetweensilicones pages 5-7, rossing2020bondingbetweensilicones pages 7-10) |
| PETG print | Cooling during roof bridge | 50-80% local bridge fan | 70% on bridge only | Extra bridge cooling helps PETG roof span the cavity while avoiding global embrittlement | (rossing2020bondingbetweensilicones pages 5-7, lesniowski2025enhancingtheperformance pages 16-18) |
| TPU 95A print | Layer height | 0.16-0.20 mm | 0.20 mm | 0.20 mm is robust for 95A and adequate for a 2.4 mm cable + head geometry | (zhang2026mechanicalperformanceof pages 2-4, bruere2023theinfluenceof pages 2-4) |
| TPU 95A print | Line width | 0.42-0.48 mm | 0.45 mm | Slightly larger width improves continuity in the head and cable | (miller2017fatigueandcyclic pages 62-67, zhang2026mechanicalperformanceof pages 2-4) |
| TPU 95A print | Walls / perimeters in cable and head | 2-3 | 3 | Contours materially improve integrity and reduce delamination in printed TPU | (bruere2023theinfluenceof pages 4-5, bruere2023theinfluenceof pages 8-9) |
| TPU 95A print | Infill | 100% | 100% | For a tendon, sparse infill only adds creep and variability; use solid roads | (bruere2023theinfluenceof pages 2-4, miller2017fatigueandcyclic pages 62-67) |
| TPU 95A print | Nozzle temperature | 220-235 C | 225 C | Matches successful 95A FDM studies and balances flow with stringing | (miller2017fatigueandcyclic pages 62-67, zhang2026mechanicalperformanceof pages 2-4, bruere2023theinfluenceof pages 2-4) |
| TPU 95A print | Bed temperature | 35-50 C | 40 C | Typical range for stable TPU deposition with limited spread | (miller2017fatigueandcyclic pages 62-67) |
| TPU 95A print | Print speed | 8-20 mm/s | 12 mm/s | Slow printing was used in TPU studies and improves consistency for viscoelastic filament | (bruere2023theinfluenceof pages 2-4) |
| TPU 95A print | Drying | 50-60 C for 4-8 h | 55 C for 6 h | Moisture increases bubbles/stringing and degrades dimensional control | (bruere2023theinfluenceof pages 2-4, lesniowski2025enhancingtheperformance pages 16-18) |
| Multi-material sequencing | Order within captive-joint layers | TPU head first, PETG roof/cheeks second | TPU first then PETG close | Matches additive anchor/joiner logic and avoids trying to stuff TPU into a sealed PETG cavity | (rossing2020bondingbetweensilicones pages 7-10, rossing2020bondingbetweensilicones pages 13-16, zhang2026mechanicalperformanceof pages 2-4) |
| Multi-material sequencing | Interface gap in slicer/model | 0.20-0.30 mm on free faces | 0.25 mm | Prevents accidental weld/drag while keeping geometric capture | (rossing2020bondingbetweensilicones pages 7-10, hamilton2023analysisofadhesive pages 150-154) |
| Multi-material sequencing | Prime/wipe strategy | aggressive wipe + purge before PETG roof layers | enable | PETG drool into the slot is a major print-in-place failure risk | (rossing2020bondingbetweensilicones pages 7-10, lesniowski2025enhancingtheperformance pages 16-18) |
| Multi-material sequencing | Ooze shielding | sacrificial shield/tower at same Z as joints | enable | Reduces PETG and TPU string carryover into tiny captive cavities | (rossing2020bondingbetweensilicones pages 7-10, hamilton2023analysisofadhesive pages 150-154) |
| Multi-material sequencing | Z-seam placement | move seam away from slot mouth | rear of strut tip | Keeps seam bulge out of rotation path and out of load-bearing capture faces | (hamilton2023analysisofadhesive pages 150-154, szykiedans2017selectedmechanicalproperties pages 1-6) |
| Multi-material sequencing | Print orientation | strut axis in XY, slot opening upward or sideways with roof bridge in XY | slot up | Best compromise for cable continuity and short PETG roof bridging; avoid slot opening downward | (rossing2020bondingbetweensilicones pages 5-7, szykiedans2017selectedmechanicalproperties pages 1-6) |
| Quick validation | Pull-out coupon | 5 repeats each geometry; quasi-static 5-20 mm/min | 10 mm/min | Screen head pull-out, TPU tear, PETG cheek split, and roof breakout before full node prints | (rossing2020bondingbetweensilicones pages 13-16, zhang2026mechanicalperformanceof pages 4-6) |
| Quick validation | First-pass acceptable pull-out load | >2x straight cable break load | target >=120 N | A 2.4 mm cable area is ~4.5 mm^2; even at ~12 MPa TPU UTS, straight break is ~54 N, so joint should exceed that comfortably | (bruere2023theinfluenceof pages 2-4) |
| Quick validation | Cyclic creep / relaxation test | 10-30% of monotonic failure load, 1 Hz, 10^4-10^5 cycles | 20%, 1 Hz, 10^4 cycles | TPU 95A shows significant viscoelastic relaxation and permanent set; this test quantifies tendon-length drift | (bruere2023theinfluenceof pages 7-8, miller2017fatigueandcyclic pages 86-96) |
| Quick validation | Hold-relaxation test | impose 5-10% cable strain for 10^3-10^4 s | 8% for 3600 s | Captures tension decay for simulation parameter fitting | (bruere2023theinfluenceof pages 7-8, bruere2023theinfluenceof pages 2-4) |
| Quick validation | Impact coupon test | drop / tower with isolated node coupon instrumented for high-speed video or force | start with isolated 1-strut/1-cable node | Use coupon before full tensegrity to distinguish roof breakout, cheek split, or TPU head shear | (lesniowski2025enhancingtheperformance pages 16-18, v2024evaluationofmechanical pages 20-27) |
| Quick validation | Rotation freedom check | free rotation under no load with no visible scraping/fusing | pass/fail | Confirms clearance and seam placement are adequate for a pin-like joint assumption | (rossing2020bondingbetweensilicones pages 7-10, hamilton2023analysisofadhesive pages 150-154) |


*Table: This table gives starting geometry, print settings, sequencing tactics, and validation tests for a co-printed PETG/TPU captive dovetail joint on a 0.4 mm IDEX printer. It is intended as a conservative first-pass design basis grounded in multi-material interlock and FFF material behavior evidence.*

Key first-pass recommendations distilled:
- **Geometry:** enforce explicit clearances (~0.25 mm/side on non-load faces) because printed features deviate from CAD; keep PETG roof bridge span short (target ≤4 mm) and roof thickness ~1.0 mm; include fillets at slot roots and TPU head/neck. (rossing2020bondingbetweensilicones pages 7-10, hamilton2023analysisofadhesive pages 154-159)
- **Print order:** TPU head first, then PETG closes over it—this matches general “anchor in receptacle” logic and avoids trapping TPU in a sealed cavity. (rossing2020bondingbetweensilicones pages 7-10, zhang2026mechanicalperformanceof pages 2-4)
- **Material settings:** use slower TPU speeds and multiple perimeters (outlines) because perimeters strongly affect TPU integrity and reduce delamination; TPU tensile properties in FFF show strong dependence on contour presence. (bruere2023theinfluenceof pages 4-5, bruere2023theinfluenceof pages 8-9)
- **Validation coupons:** before printing full tensegrities, test isolated node coupons for pull-out, rotation freedom, and post-load relaxation; TPU shows strong relaxation across seconds→days, so tension drift must be quantified for your simulator closure. (bruere2023theinfluenceof pages 7-8, bruere2023theinfluenceof pages 2-4)

---

## Additional critical design notes (specific to your concept)

1. **Your “TPU must shear before pull-free” requirement is achievable, but only if PETG does not become the weak link.** If you push capture overlap too aggressively, you will likely shift the failure into PETG roof/cheeks (crack initiation at slot corners), consistent with multimaterial joint studies where strengthening the interface moved failure elsewhere due to stress concentrations and cross-section reductions. (zatloukal2025optimizinginterfacialadhesion pages 6-10)

2. **Consider replacing a true “T-slot” with a shallow-angle dovetail.** Tooth-angle studies show angle \(\theta\) strongly affects strength and failure; shallow angles can improve shear performance and reduce stress concentrations compared with steep hooks. (zhang2026mechanicalperformanceof pages 8-11, zhang2026mechanicalperformanceof pages 15-17)

3. **Expect joint-to-joint variability from print artifacts.** Rossing et al. report incomplete cells (0.67–5.3%) and strength reductions from inconsistent beam thickness and voids; your analog is inconsistent PETG roof closure and small strings inside the slot. This pushes you toward conservative clearances and aggressive purge/wipe strategies. (rossing2020bondingbetweensilicones pages 13-16)

---

### Evidence images
Figures extracted from Rossing et al. show: (i) an interlock unit-cell geometry with parameterized dimensions and (ii) clear visual identification of failure modes (pull-out at one surface, silicone tensile failure at another, and plastic beam fracture), plus strength-vs-geometry maps; these provide a useful qualitative analog for how your joint will transition from pull-out to internal failure as capture depth increases. (rossing2020bondingbetweensilicones media 2e6c2a66, rossing2020bondingbetweensilicones media 4393c4ea, rossing2020bondingbetweensilicones media d84e9332)


References

1. (rossing2020bondingbetweensilicones pages 13-16): Lars Rossing, Rob B.N. Scharff, Bryan Chömpff, Charlie C.L. Wang, and Eugeni L. Doubrovski. Bonding between silicones and thermoplastics using 3d printed mechanical interlocking. Materials & Design, 186:108254, Jan 2020. URL: https://doi.org/10.1016/j.matdes.2019.108254, doi:10.1016/j.matdes.2019.108254. This article has 52 citations and is from a highest quality peer-reviewed journal.

2. (zhang2026mechanicalperformanceof pages 1-2): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

3. (zhang2026mechanicalperformanceof pages 11-13): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

4. (rossing2020bondingbetweensilicones pages 5-7): Lars Rossing, Rob B.N. Scharff, Bryan Chömpff, Charlie C.L. Wang, and Eugeni L. Doubrovski. Bonding between silicones and thermoplastics using 3d printed mechanical interlocking. Materials & Design, 186:108254, Jan 2020. URL: https://doi.org/10.1016/j.matdes.2019.108254, doi:10.1016/j.matdes.2019.108254. This article has 52 citations and is from a highest quality peer-reviewed journal.

5. (rossing2020bondingbetweensilicones pages 7-10): Lars Rossing, Rob B.N. Scharff, Bryan Chömpff, Charlie C.L. Wang, and Eugeni L. Doubrovski. Bonding between silicones and thermoplastics using 3d printed mechanical interlocking. Materials & Design, 186:108254, Jan 2020. URL: https://doi.org/10.1016/j.matdes.2019.108254, doi:10.1016/j.matdes.2019.108254. This article has 52 citations and is from a highest quality peer-reviewed journal.

6. (zhang2026mechanicalperformanceof pages 2-4): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

7. (lesniowski2025enhancingtheperformance pages 16-18): Jakub Leśniowski, Adam Stawiarski, and Marek Barski. Enhancing the performance of fff-printed parts: a review of reinforcement and modification strategies for thermoplastic polymers. Materials, 18:5185, Nov 2025. URL: https://doi.org/10.3390/ma18225185, doi:10.3390/ma18225185. This article has 2 citations.

8. (lesniowski2025enhancingtheperformance pages 14-16): Jakub Leśniowski, Adam Stawiarski, and Marek Barski. Enhancing the performance of fff-printed parts: a review of reinforcement and modification strategies for thermoplastic polymers. Materials, 18:5185, Nov 2025. URL: https://doi.org/10.3390/ma18225185, doi:10.3390/ma18225185. This article has 2 citations.

9. (bruere2023theinfluenceof pages 4-5): V. M. Bruère, A. Lion, J. Holtmannspötter, and M. Johlitz. The influence of printing parameters on the mechanical properties of 3d printed tpu-based elastomers. Progress in Additive Manufacturing, 8:693-701, Mar 2023. URL: https://doi.org/10.1007/s40964-023-00418-7, doi:10.1007/s40964-023-00418-7. This article has 58 citations and is from a peer-reviewed journal.

10. (bruere2023theinfluenceof pages 2-4): V. M. Bruère, A. Lion, J. Holtmannspötter, and M. Johlitz. The influence of printing parameters on the mechanical properties of 3d printed tpu-based elastomers. Progress in Additive Manufacturing, 8:693-701, Mar 2023. URL: https://doi.org/10.1007/s40964-023-00418-7, doi:10.1007/s40964-023-00418-7. This article has 58 citations and is from a peer-reviewed journal.

11. (miller2017fatigueandcyclic pages 86-96): AT Miller. Fatigue and cyclic loading of 3d printed soft polymers for orthopedic applications. Unknown journal, 2017.

12. (miller2017fatigueandcyclic pages 104-108): AT Miller. Fatigue and cyclic loading of 3d printed soft polymers for orthopedic applications. Unknown journal, 2017.

13. (zatloukal2025optimizinginterfacialadhesion pages 6-10): Jakub Zatloukal, Mathieu Viry, Aleš Mizera, Pavel Stoklásek, Lukáš Miškařík, and Martin Bednařík. Optimizing interfacial adhesion and mechanical performance of multimaterial joints fabricated by material extrusion. Materials, 18:3846, Aug 2025. URL: https://doi.org/10.3390/ma18163846, doi:10.3390/ma18163846. This article has 6 citations.

14. (bruere2023theinfluenceof pages 7-8): V. M. Bruère, A. Lion, J. Holtmannspötter, and M. Johlitz. The influence of printing parameters on the mechanical properties of 3d printed tpu-based elastomers. Progress in Additive Manufacturing, 8:693-701, Mar 2023. URL: https://doi.org/10.1007/s40964-023-00418-7, doi:10.1007/s40964-023-00418-7. This article has 58 citations and is from a peer-reviewed journal.

15. (rossing2020bondingbetweensilicones pages 16-22): Lars Rossing, Rob B.N. Scharff, Bryan Chömpff, Charlie C.L. Wang, and Eugeni L. Doubrovski. Bonding between silicones and thermoplastics using 3d printed mechanical interlocking. Materials & Design, 186:108254, Jan 2020. URL: https://doi.org/10.1016/j.matdes.2019.108254, doi:10.1016/j.matdes.2019.108254. This article has 52 citations and is from a highest quality peer-reviewed journal.

16. (rossing2020bondingbetweensilicones pages 1-5): Lars Rossing, Rob B.N. Scharff, Bryan Chömpff, Charlie C.L. Wang, and Eugeni L. Doubrovski. Bonding between silicones and thermoplastics using 3d printed mechanical interlocking. Materials & Design, 186:108254, Jan 2020. URL: https://doi.org/10.1016/j.matdes.2019.108254, doi:10.1016/j.matdes.2019.108254. This article has 52 citations and is from a highest quality peer-reviewed journal.

17. (zhang2026mechanicalperformanceof pages 8-11): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

18. (zhang2026mechanicalperformanceof pages 15-17): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

19. (zhang2026mechanicalperformanceof pages 6-8): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

20. (zhang2026mechanicalperformanceof pages 4-6): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

21. (hamilton2023analysisofadhesive pages 154-159): Alexander Andrew William Hamilton. Analysis of adhesive joints with mechanically interlocking microstructured adherends. Text, Jan 2023. URL: https://doi.org/10.5525/gla.thesis.83423, doi:10.5525/gla.thesis.83423. This article has 1 citations and is from a peer-reviewed journal.

22. (hamilton2023analysisofadhesive pages 150-154): Alexander Andrew William Hamilton. Analysis of adhesive joints with mechanically interlocking microstructured adherends. Text, Jan 2023. URL: https://doi.org/10.5525/gla.thesis.83423, doi:10.5525/gla.thesis.83423. This article has 1 citations and is from a peer-reviewed journal.

23. (zatloukal2025optimizinginterfacialadhesion pages 4-6): Jakub Zatloukal, Mathieu Viry, Aleš Mizera, Pavel Stoklásek, Lukáš Miškařík, and Martin Bednařík. Optimizing interfacial adhesion and mechanical performance of multimaterial joints fabricated by material extrusion. Materials, 18:3846, Aug 2025. URL: https://doi.org/10.3390/ma18163846, doi:10.3390/ma18163846. This article has 6 citations.

24. (hasanov2021reviewonadditive pages 19-21): Seymur Hasanov, Suhas Alkunte, Mithila Rajeshirke, Ankit Gupta, Orkhan Huseynov, Ismail Fidan, Frank Alifui-Segbaya, and Allan Rennie. Review on additive manufacturing of multi-material parts: progress and challenges. Journal of Manufacturing and Materials Processing, Nov 2021. URL: https://doi.org/10.20944/preprints202111.0277.v1, doi:10.20944/preprints202111.0277.v1. This article has 348 citations.

25. (bruere2023theinfluenceof pages 8-9): V. M. Bruère, A. Lion, J. Holtmannspötter, and M. Johlitz. The influence of printing parameters on the mechanical properties of 3d printed tpu-based elastomers. Progress in Additive Manufacturing, 8:693-701, Mar 2023. URL: https://doi.org/10.1007/s40964-023-00418-7, doi:10.1007/s40964-023-00418-7. This article has 58 citations and is from a peer-reviewed journal.

26. (miller2017fatigueandcyclic pages 62-67): AT Miller. Fatigue and cyclic loading of 3d printed soft polymers for orthopedic applications. Unknown journal, 2017.

27. (valvez2022optimizationofprinting pages 2-3): Sara Valvez, Abilio P. Silva, and Paulo N. B. Reis. Optimization of printing parameters to maximize the mechanical properties of 3d-printed petg-based parts. Polymers, 14:2564, Jun 2022. URL: https://doi.org/10.3390/polym14132564, doi:10.3390/polym14132564. This article has 190 citations.

28. (v2024evaluationofmechanical pages 20-27): Mr. Lakshman Sri S V, Mr. Karthick A, and M. Dinesh. Evaluation of mechanical properties of 3d printed petg and polyamide (6) polymers. Chemical Physics Impact, 8:100491, Jun 2024. URL: https://doi.org/10.1016/j.chphi.2024.100491, doi:10.1016/j.chphi.2024.100491. This article has 56 citations and is from a peer-reviewed journal.

29. (hsueh2021effectofprinting pages 8-10): Ming-Hsien Hsueh, Chao-Jung Lai, Shi-Hao Wang, Yu-Shan Zeng, Chia-Hsin Hsieh, Chieh-Yu Pan, and Wen-Chen Huang. Effect of printing parameters on the thermal and mechanical properties of 3d-printed pla and petg, using fused deposition modeling. Polymers, 13:1758, May 2021. URL: https://doi.org/10.3390/polym13111758, doi:10.3390/polym13111758. This article has 407 citations.

30. (hsueh2021effectofprinting pages 6-8): Ming-Hsien Hsueh, Chao-Jung Lai, Shi-Hao Wang, Yu-Shan Zeng, Chia-Hsin Hsieh, Chieh-Yu Pan, and Wen-Chen Huang. Effect of printing parameters on the thermal and mechanical properties of 3d-printed pla and petg, using fused deposition modeling. Polymers, 13:1758, May 2021. URL: https://doi.org/10.3390/polym13111758, doi:10.3390/polym13111758. This article has 407 citations.

31. (szykiedans2017selectedmechanicalproperties pages 1-6): Ksawery Szykiedans, Wojciech Credo, and Dymitr Osiński. Selected mechanical properties of petg 3-d prints ☆. Procedia Engineering, 177:455-461, Jan 2017. URL: https://doi.org/10.1016/j.proeng.2017.02.245, doi:10.1016/j.proeng.2017.02.245. This article has 218 citations and is from a peer-reviewed journal.

32. (rossing2020bondingbetweensilicones media 2e6c2a66): Lars Rossing, Rob B.N. Scharff, Bryan Chömpff, Charlie C.L. Wang, and Eugeni L. Doubrovski. Bonding between silicones and thermoplastics using 3d printed mechanical interlocking. Materials & Design, 186:108254, Jan 2020. URL: https://doi.org/10.1016/j.matdes.2019.108254, doi:10.1016/j.matdes.2019.108254. This article has 52 citations and is from a highest quality peer-reviewed journal.

33. (rossing2020bondingbetweensilicones media 4393c4ea): Lars Rossing, Rob B.N. Scharff, Bryan Chömpff, Charlie C.L. Wang, and Eugeni L. Doubrovski. Bonding between silicones and thermoplastics using 3d printed mechanical interlocking. Materials & Design, 186:108254, Jan 2020. URL: https://doi.org/10.1016/j.matdes.2019.108254, doi:10.1016/j.matdes.2019.108254. This article has 52 citations and is from a highest quality peer-reviewed journal.

34. (rossing2020bondingbetweensilicones media d84e9332): Lars Rossing, Rob B.N. Scharff, Bryan Chömpff, Charlie C.L. Wang, and Eugeni L. Doubrovski. Bonding between silicones and thermoplastics using 3d printed mechanical interlocking. Materials & Design, 186:108254, Jan 2020. URL: https://doi.org/10.1016/j.matdes.2019.108254, doi:10.1016/j.matdes.2019.108254. This article has 52 citations and is from a highest quality peer-reviewed journal.