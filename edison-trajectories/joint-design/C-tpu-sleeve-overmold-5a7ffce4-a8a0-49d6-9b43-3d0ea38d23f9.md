Question: ## Joint design idea: TPU overmolded sleeve over a knurled / grooved PETG strut tip (Ye 2023 / Khatri 2024-style PETG-TPU wrap)

The last 6-10 mm of each PETG strut tip is knurled (helical or annular
ribs, 0.6 mm peak-to-valley, 1.0 mm pitch — slicer-printable on a 0.4 mm
nozzle) to dramatically increase mechanical interlock surface. The TPU
cable is printed continuous from one strut tip to the next, but as it
approaches the tip it flares into a 1.0-1.5 mm wall thickness *sleeve*
that wraps over the strut tip for 6-10 mm of axial overlap, gripping by
hoop tension + ribbed friction. Inspired by Ye 2023 and Khatri 2024
PETG-TPU wrap composites cited in the TPU+PETG variables Edison
literature search (attached, _ctx_tpu-petg-vars.md). Closest analog:
overmolded grips on hand tools, swaged cable terminations, fiber-reinforced
composite end-fittings.


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


## Critical review of the proposed PETG–TPU knurled-tip + TPU sleeve joint

### Summary judgement
A knurled/grooved PETG tip with a flared TPU sleeve can be made to work as a *mechanically locked* termination, and the overall design direction (increase real contact area + enforce mechanical engagement + keep interface hot/compacted) is consistent with published multimaterial FFF joint studies. However, a **pure friction/hoop-tension sleeve without a true undercut** is at high risk of **progressive slip/pull-out** under impact and under time-dependent TPU relaxation; the highest-leverage improvement is to add at least one **positive mechanical lock feature** (barb/undercut/shoulder) so the load path must shear/tear TPU rather than rely on interface friction alone. Evidence from PLA/TPU interface-geometry studies shows that U- and dovetail-type interfaces can slide apart along the interface, while a T-shaped interlock prevented sliding and shifted failure elsewhere. (catana2024bicomponentadditivemanufacturing pages 6-7)


## (1) Manufacturability on a 0.4 mm nozzle IDEX (single print, no soluble support)

### 1.1 Feature size and knurl printability
* **Ribs at 1.0 mm pitch and 0.6 mm peak-to-valley** are within the general printable scale for 0.4 mm nozzles if you avoid sharp peaks and use generous root radii; published rigid–flexible joint studies report printed trace widths on the order of ~0.42–0.45 mm. (zhang2026mechanicalperformanceof pages 4-6)
* Your *6–10 mm axial overlap* is aligned with bio-inspired interlock work where *short overlaps may not engage the intended interlocking failure mode* and longer overlaps are needed; Zhang (2021) explicitly contrasted short vs longer overlaps in interlocking composites. (zhang20213dprintingof pages 38-44)

### 1.2 Sleeve manufacturability without support
The main risk is not “can you print a sleeve,” but **can you print it without trapping unsupported ceilings** or causing tool access/collision issues inside a small 7 mm node envelope.

**What is likely manufacturable:**
* A sleeve built as **concentric perimeters** around the PETG tip, with the sleeve thickness coming from wall count (rather than sparse infill), is generally straightforward.

**What is likely to fail without support (unless redesigned):**
* A “closed-end” overmold that requires printing **unsupported TPU bridges** over a cavity (TPU bridges poorly; also TPU is prone to delamination). TPU is reported to have weak layer adhesion and potential delamination, and print integrity improves when contours/perimeters are used. (lopes2024interfaceboundarymechanical pages 37-40)

**Practical IDEX/toolchange constraints:**
* Multi-material printing interruptions can reduce interface quality. Toolchange/filament-change pauses increase risk of molten polymer **drooling** and inconsistent deposition; mitigation includes adjusting retraction during pauses and avoiding the highest temperatures. (lopes2024interfaceboundarymechanical pages 40-45)
* TPU itself is challenging: it can **buckle**, is **moisture sensitive**, and poor control can cause printing stoppage. (lopes2024interfaceboundarymechanical pages 33-37)

**Geometry recommendation to make “no-support” plausible:**
* Make the sleeve **open-ended** and avoid any internal “roof.”
* Add a **2–3 layer lead-in chamfer** at the sleeve start (e.g., 30–45°) so TPU builds on PETG gradually (no sudden overhang).
* Keep minimum TPU wall features ≥ ~0.45 mm (≈ one line); Zhang (2021) had to tune extrusion heavily to get ~0.4–0.6 mm TPU regions to form reliably and to avoid air gaps. (zhang20213dprintingof pages 44-52)


## (2) Likely failure modes under single-impact drop test (and rough quantitative bounds)

### 2.1 Most likely failure modes
Ranked from most to least likely for your *friction + ribbed* concept:

1) **Progressive slip/pull-out of TPU sleeve from the PETG knurl**
   * PLA/TPU joints frequently fail by **interfacial sliding** when the interface is not positively locked. (zhang2026mechanicalperformanceof pages 15-17, catana2024bicomponentadditivemanufacturing pages 6-7)
   * In pull-out style tests on TPU/CB-TPU interfaces, a progressive pull-out region with gradual stress drop followed by sudden complete fracture was observed—mechanistically similar to what you should expect if your sleeve relies on friction and shallow ribs. (lopes2024interfaceboundarymechanical pages 105-108)

2) **TPU tearing at sleeve mouth / stress concentration zone**
   * If you add any undercut/shoulder, failure may move to tearing near the transition, analogous to the way mechanical interlocking shifts failure away from pure sliding. (catana2024bicomponentadditivemanufacturing pages 6-7, zhang2026mechanicalperformanceof pages 15-17)

3) **PETG strut-tip shear at knurl roots (notch effect)**
   * The knurl is a stress concentrator; if you use sharp valleys, PETG can locally shear/crack at rib roots under peak impact bending.

4) **TPU layer delamination within the sleeve itself**
   * TPU is reported to have weak layer adhesion and can delaminate; process parameters (speed/temperature/nozzle height) strongly control this. (lopes2024interfaceboundarymechanical pages 37-40)

5) **Time-dependent relaxation/creep → loss of hoop tension** (may not show in a single hit, but will reduce retention before the hit)
   * TPU is viscoelastic and shows cyclic hysteresis; time dependence is inherent. (lopes2024interfaceboundarymechanical pages 33-37)

### 2.2 Rough pull-out force bounds (engineering estimate)
Because direct PETG–TPU sleeve pull-out data were not retrieved, the bounds below use *analog joint strengths* from rigid–flexible FDM literature and convert MPa-scale interface strength to force using plausible engaged areas.

**(A) Conservative bound using “effective interfacial shear strength” 0.5–2 MPa**
*This corresponds to “poor compatibility / mostly sliding” regimes seen in multi-material systems (e.g., very weak PLA/PETG butt joints were ~1.6 MPa; PLA/TPU also readily slides without interlock). (zatloukal2025optimizinginterfacialadhesion pages 4-6, catana2024bicomponentadditivemanufacturing pages 6-7)*

Assume PETG tip diameter d ≈ 6 mm, overlap L = 6–10 mm.
Engaged area A ≈ π d L ≈ π·6·(6 to 10) ≈ 113 to 188 mm².
Force F ≈ τ A ≈ (0.5 to 2) N/mm² · (113 to 188) mm² ≈ **60–380 N**.

**(B) Optimistic bound if you achieve a true interlock-like load path (6–8 MPa class)**
Mechanical interlocking PLA/TPU tensile strengths are on the order of ~6–7 MPa in some tested geometries. (zhang2026mechanicalperformanceof pages 1-2)
If your knurl + sleeve behaves closer to a “tooth interlock” than friction, an upper bound might be:
F ≈ (6 to 8) N/mm² · (113 to 188) mm² ≈ **680–1500 N**.

Interpretation: without a positive undercut, **expect the lower range** (order 10² N) because sliding is the bottleneck in rigid–flexible joints. (zhang2026mechanicalperformanceof pages 15-17, catana2024bicomponentadditivemanufacturing pages 6-7)

### 2.3 Impact-specific concerns (peak force, hinge yielding)
A single drop can drive high peak tension in a subset of cables. The weak link will usually be whichever converts that tension into either:
* interface shear (sleeve slip), or
* local stress concentration (TPU tear at sleeve mouth; PETG rib-root crack).

If you want a joint that survives “NASA-lander regime,” you should design such that *the first failure mode is controlled TPU yielding/energy absorption*, not debonding/pull-out.


## (3) How well it preserves the “rigid struts + ideal tendons” modeling assumption

### 3.1 Joint compliance sources you are introducing
1) **Axial compliance in the termination** (TPU sleeve shear + micro-slip on ribs)
   * If the interface can slide, the joint behaves like a *nonlinear frictional damper*; Zhang (2026) explicitly identifies interlayer sliding as a dominant failure/bottleneck for PLA/TPU joints in some joint strategies. (zhang2026mechanicalperformanceof pages 15-17)

2) **Viscoelasticity and hysteresis**
   * TPU shows hysteresis in cyclic loading due to viscoelasticity. (lopes2024interfaceboundarymechanical pages 33-37)

3) **Local bending hinge**
   * The cable transitions from 2.4 mm to a flared sleeve and wraps around the node; this forms a compliant “hinge” region that will add rotational compliance and damping.

### 3.2 Order-of-magnitude stiffness estimate (simulation gap)
TPU Young’s modulus in one FDM study was ~33.6 MPa (PLA ~3427 MPa), indicating TPU is ~100× more compliant than PLA. (zhang2026mechanicalperformanceof pages 4-6)

For a 2.4 mm diameter TPU cable, cross-sectional area A ≈ 4.52 mm².
Cable axial stiffness k ≈ EA/L.
If effective free length is ~100 mm, k ≈ 33.6 N/mm²·4.52/100 ≈ **1.5 N/mm**.

A termination slip of even **0.2–0.5 mm** under load (plausible if sliding initiates) corresponds to an apparent compliance comparable to several centimeters of “ideal tendon” lengthening, and it will be *load-path dependent and hysteretic*. This is a substantial simulation gap unless you explicitly add a joint spring/damper element.

Practical modeling suggestion: represent each cable with a **Kelvin–Voigt element + frictional slip** at the node (piecewise: stiff until a slip threshold, then lower stiffness with hysteresis).


## (4) Cited prior art closest to this joint (and what they measured/concluded)

The closest *mechanism* analogs in the retrieved literature are rigid–flexible mechanical interlocks and tooth/area-amplified multimaterial joints.

| Source (author/year) | Material pairs | Joint concept / geometry | Key quantitative results (strength MPa, depths/angles, temps) | Observed failure modes / process issues | Design takeaways for a TPU sleeve over a knurled rigid core |
|---|---|---|---|---|---|
| Zhang et al. 2026 | PLA/TPU; PLA/Soft-PLA | Mechanical interlocking teeth; alternate deposition | Interlocking tensile peak at 2 mm depth, 45°: 6.58 ± 0.33 MPa (PLA/TPU); shear peak at 4 mm depth, 22.5°: 24.47 ± 1.99 MPa. Alternate-deposition tensile plateau: 7.42 ± 0.33 MPa for PLA/TPU at deposition width ≥ 6 mm. Print guidance noted: higher platform temperature, higher print temperature, reduced layer thickness improve bonding. (zhang2026mechanicalperformanceof pages 1-2, zhang2026mechanicalperformanceof pages 4-6) | Interface is typically the weakest zone; process strongly sensitive to printing sequence/fill strategy and thermal history. (zhang2026mechanicalperformanceof pages 1-2) | A sleeve joint should rely on geometry, not chemistry alone; modest interlock depth can be effective, but too-shallow/too-short engagement is likely underpowered. Keep interface hot and well-consolidated. (zhang2026mechanicalperformanceof pages 1-2, zhang2026mechanicalperformanceof pages 4-6) |
| Catana et al. 2024 (review of Ribeiro et al.-type tests) | PLA/TPU | T-shape, U-shape, dovetail interfaces | Print settings reported for tested PLA/TPU samples: TPU 225 °C, PLA 200 °C, bed 60 °C, 0.4 mm nozzle, 0.2 mm layer, 100% infill, 20 mm/s, ±45° orientation. No interface strength numbers given in snippet. (catana2024bicomponentadditivemanufacturing pages 6-7) | PLA/TPU U-shaped and dovetail interfaces separated along the interface and slid over each other; T-shaped interlock kept parts linked and shifted failure to exit-geometry region. Review also notes delamination/localized cracking risks in dissimilar-material FFF. (catana2024bicomponentadditivemanufacturing pages 6-7, catana2024bicomponentadditivemanufacturing pages 4-6) | Pure wrap friction or smooth overlap is risky; add true undercut/anti-slip geometry so load must tear TPU or shear ribs rather than simply slide off. (catana2024bicomponentadditivemanufacturing pages 6-7, catana2024bicomponentadditivemanufacturing pages 4-6) |
| Zhang 2021 | PLA/TPU | Bio-inspired dovetail interlock with soft filler between rigid tablets | Geometry/process details: overlap length examples ~2.6 mm vs ~8 mm; dovetail angles 0°, 1°, 3°, 5°, 9°; tablet length 16 mm; filler thickness 0.6 mm, narrow section 0.4 mm; nozzle 215 °C, bed 80 °C; print speed 900 mm/min; final extrusion multipliers PLA 0.9, TPU 2.8. Prior interlocking analog cited as increasing energy dissipation/strength by ~50% vs flat tablets. (zhang20213dprintingof pages 38-44, zhang20213dprintingof pages 44-52) | Short overlaps may not engage the intended interlocking failure mode; TPU feed stoppages, air gaps, and extensive tuning were needed to fill the interface cleanly. (zhang20213dprintingof pages 38-44, zhang20213dprintingof pages 44-52) | Your proposed 6–10 mm overlap is directionally right: long engagement length matters. Expect substantial tuning to avoid voids in the sleeve and to ensure TPU actually fills knurl valleys. (zhang20213dprintingof pages 38-44, zhang20213dprintingof pages 44-52) |
| Zatloukal et al. 2025 | PETG with PC, ASA, PLA | Standard butt joint; increased-contact-area “tooth”; interlayer bonding / pressure-assisted interface | PC/PETG: 15.2 MPa (butt), 28.2 MPa (tooth), 29.9 MPa (interlayer bonding). ASA/PETG: 8.9 MPa (butt), 27.1 MPa (tooth), 23.6 MPa (interlayer bonding). PLA/PETG: 1.6 MPa (butt), 4 MPa (tooth), 25.4 MPa (interlayer bonding). Typical print settings included PETG 250 °C, 0.2 mm layer, 0.5 mm width, 100% infill. (zatloukal2025optimizinginterfacialadhesion pages 10-12, zatloukal2025optimizinginterfacialadhesion pages 4-6, zatloukal2025optimizinginterfacialadhesion pages 2-4, zatloukal2025optimizinginterfacialadhesion pages 12-14) | Standard flat interfaces performed worst; strength improved with more real contact area and with pressure/thermal assistance. For some pairs, fracture moved beyond the bonded interface due to geometry discontinuity. (zatloukal2025optimizinginterfacialadhesion pages 10-12, zatloukal2025optimizinginterfacialadhesion pages 6-10, zatloukal2025optimizinginterfacialadhesion pages 4-6) | Even though not PETG/TPU, this strongly supports using knurls/ribs/teeth to multiply contact area and lock the sleeve mechanically. Also suggests compaction/“squeezing” of TPU onto hot PETG will matter almost as much as geometry. (zatloukal2025optimizinginterfacialadhesion pages 10-12, zatloukal2025optimizinginterfacialadhesion pages 4-6, zatloukal2025optimizinginterfacialadhesion pages 2-4) |
| Lopes 2024 | TPU/CB-TPU; general TPU multi-material FFF discussion incl. TPU with rigid polymers | Discrete planar interface in pull-out tests; recommends future mechanical interlocking / gradient interface | Test method used pull-out at 10 mm/s with 2.5 kN load cell. Best interface stress occurred at 245 °C in tested TPU/CB-TPU system; constant parameters included 0.1 mm layer height, 3 perimeters, 100% infill, 45° fill angle. For TPU printing generally, 0.1 mm layer height and lower nozzle height improve packing; 240 °C and 20 mm/s reported as good for one TPU filament. (lopes2024interfaceboundarymechanical pages 49-55, lopes2024interfaceboundarymechanical pages 55-61, lopes2024interfaceboundarymechanical pages 33-37, lopes2024interfaceboundarymechanical pages 105-108) | Progressive pull-out followed by sudden final fracture; rougher surfaces could improve adhesion via mechanical interlocking. TPU printing challenges: buckling, moisture sensitivity, stoppages, weak layer adhesion/delamination, and interface degradation from filament-change pauses. Printing order matters in multi-material work. (lopes2024interfaceboundarymechanical pages 33-37, lopes2024interfaceboundarymechanical pages 37-40, lopes2024interfaceboundarymechanical pages 105-108) | For a sleeve joint, dry TPU aggressively, minimize pauses/toolchange cooling at the interface, and bias design toward perimeter-dominated load paths. Surface roughness/ribs on PETG are beneficial because the likely failure mode is progressive pull-out, not chemical debond alone. (lopes2024interfaceboundarymechanical pages 33-37, lopes2024interfaceboundarymechanical pages 37-40, lopes2024interfaceboundarymechanical pages 105-108) |
| Giani 2022 | General thermoplastics / TPU in FDM | Interfacial bonding theory rather than a specific joint geometry | No joint strengths reported; bonding depends on wetting, surface approach, diffusion, and reptation/chain entanglement across the interface. TPU properties vary strongly with chemistry and hardness. (giani2022productionandcharacterization pages 12-16, giani2022productionandcharacterization pages 51-55) | Dissimilar-material bonding is inherently difficult when interdiffusion is limited; this is especially relevant when relying on PETG–TPU chemical adhesion. (giani2022productionandcharacterization pages 12-16) | Supports the core premise that PETG–TPU should be treated as a mechanically locked joint. Use chemistry as a bonus only, not as the primary retention mechanism. (giani2022productionandcharacterization pages 12-16, giani2022productionandcharacterization pages 51-55) |


*Table: This table summarizes the retrieved evidence most relevant to designing a TPU sleeve mechanically locked onto a rigid printed core. It highlights what was measured, how joints failed, and which geometry/process features are most transferable to a PETG-tip knurl plus TPU-overmold concept.*

Key transferable conclusions:
* **Geometry dominates** when chemistry is weak: without a macroscopic lock, PLA/TPU interfaces can simply slide apart; T-shaped interlocks prevent sliding and force failure elsewhere. (catana2024bicomponentadditivemanufacturing pages 6-7)
* **Interfacial sliding is a primary bottleneck** in PLA/TPU shear performance; interlocking can reduce sliding but can introduce tooth-root stress concentrations. (zhang2026mechanicalperformanceof pages 15-17)
* **Increasing real contact area (“tooth strategy”) can ~2×** the strength of PETG combinations vs butt joints, and pressure/thermal consolidation can further increase strength for some material pairs. (zatloukal2025optimizinginterfacialadhesion pages 4-6, zatloukal2025optimizinginterfacialadhesion pages 10-12)
* Multi-material printing pauses can degrade quality via **drooling**, motivating careful toolchange/retraction management. (lopes2024interfaceboundarymechanical pages 40-45)

Limitations: I did not retrieve the specific “Ye 2023” / “Khatri 2024” PETG–TPU wrap papers you referenced, so any claims about their specific measured performance cannot be made here.


## (5) Concrete numerical recommendations (first pass)

### 5.1 Geometry (first prototypes)
1) **Add a positive lock (high priority):**
   * Keep your knurl, but add *one* circumferential **reverse shoulder/undercut** near the end of the overlap (e.g., 0.3–0.5 mm radial undercut with 45° lead-in). This converts pull-out into TPU shear/tear instead of frictional slip (consistent with interlock outperforming sliding interfaces). (catana2024bicomponentadditivemanufacturing pages 6-7, zhang2026mechanicalperformanceof pages 15-17)

2) **Knurl shape:**
   * Prefer **rounded annular ribs** over sharp helical threads to reduce PETG notch sensitivity.

3) **Overlap:**
   * Start with **L = 8 mm** (your range is 6–10 mm; longer overlap is favored in interlocking composites where short overlaps may not engage interlock failure modes). (zhang20213dprintingof pages 38-44)

4) **Sleeve thickness:**
   * Use thickness driven by perimeters: **1.2–1.6 mm** (≈3–4 perimeters at 0.4 mm) so load is carried by continuous walls rather than infill.

5) **Cable-to-sleeve transition:**
   * Use a **taper length ≥ 3 mm** to reduce stress concentration and to print without unsupported steps.

### 5.2 PETG slicer/process starting point (H2D)
* Nozzle: **250 °C**, bed: **~80 °C** (PETG setting used in multimaterial joint study). (zatloukal2025optimizinginterfacialadhesion pages 2-4)
* Layer height: **0.2 mm** for PETG bulk; consider **0.16 mm** around the knurl region if you need better rib definition (engineering recommendation).
* Perimeters: **≥3** at strut tips.
* Infill: **100%** locally in the last ~15 mm of strut tip (via modifier mesh) to avoid crushing rib roots.

### 5.3 TPU slicer/process starting point (95A)
Evidence-backed starting points:
* **Dry TPU** (moisture can stop printing). (lopes2024interfaceboundarymechanical pages 33-37)
* Layer height: **0.1 mm** (explicitly recommended in TPU parameter discussions; also used as a constant in TPU interface testing). (lopes2024interfaceboundarymechanical pages 37-40, lopes2024interfaceboundarymechanical pages 61-69)
* TPU nozzle temperature: start **240 °C**, explore **240–255 °C** (higher temperatures can improve tensile/interlayer adhesion; 240 °C cited as good). (lopes2024interfaceboundarymechanical pages 37-40)
* TPU speed: **10–20 mm/s** (20 mm/s recommended in TPU cube study; 10 mm/s implicated for dimensional accuracy; keep slow to avoid TPU feed issues). (lopes2024interfaceboundarymechanical pages 37-40)
* Perimeters/contours: **3–4 perimeters** for sleeve; perimeters reduce delamination sensitivity vs contourless parts. (lopes2024interfaceboundarymechanical pages 37-40)
* Nozzle height / “squeeze”: bias toward slightly lower nozzle height to improve packing and diffusion (“squeezing effect”). (lopes2024interfaceboundarymechanical pages 37-40)

### 5.4 Tool ordering / interface formation (IDEX)
* Minimize time where the PETG tip cools before TPU deposition; interface thermal history matters for bonding. (zatloukal2025optimizinginterfacialadhesion pages 6-10)
* Manage pauses to avoid drooling during toolchange; adjust retraction and avoid the highest temperatures during the pause. (lopes2024interfaceboundarymechanical pages 40-45)
* If possible, print so the TPU sleeve is deposited **immediately after** the PETG tip layers (z-local sequencing) to keep the PETG surface hot.

### 5.5 Print orientation
* Orient the part so that **the PETG strut tip axis is as close to vertical as feasible**, so knurl ribs are built as clean per-layer steps and the TPU sleeve is printed as stacked rings (best hoop continuity).
* Avoid orientations where the sleeve requires long bridging.


## Closing: what I would prototype first
1) A “coupon” test: a single PETG rod with your knurl + TPU sleeve overlap, pulled in tension to failure (to measure pull-out force and slip curve), then repeat after 24 h and after thermal cycling (to reveal viscoelastic relaxation).
2) Compare: (i) friction-only ribs, (ii) ribs + one undercut shoulder, (iii) ribs + through-hole cross-pin (TPU printed through a PETG hole) as a “hard” mechanical lock.

These will quickly determine whether your design is in the ~10² N pull-out regime (slip-dominated) or ~10³ N (interlock-dominated), and quantify how much joint compliance you must add back into MuJoCo/PyBullet/PyChrono models.


References

1. (catana2024bicomponentadditivemanufacturing pages 6-7): M Catana, SN Mazurchevici, and C Cărăușu. Bicomponent additive manufacturing of polymers-a review. Unknown journal, 2024.

2. (zhang2026mechanicalperformanceof pages 4-6): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

3. (zhang20213dprintingof pages 38-44): X Zhang. 3d printing of bio-inspired, multi-material structures to enhance stiffness and toughness. Unknown journal, 2021.

4. (lopes2024interfaceboundarymechanical pages 37-40): LMA Lopes. Interface boundary mechanical resistance analysis in fff multi-material parts. Unknown journal, 2024.

5. (lopes2024interfaceboundarymechanical pages 40-45): LMA Lopes. Interface boundary mechanical resistance analysis in fff multi-material parts. Unknown journal, 2024.

6. (lopes2024interfaceboundarymechanical pages 33-37): LMA Lopes. Interface boundary mechanical resistance analysis in fff multi-material parts. Unknown journal, 2024.

7. (zhang20213dprintingof pages 44-52): X Zhang. 3d printing of bio-inspired, multi-material structures to enhance stiffness and toughness. Unknown journal, 2021.

8. (zhang2026mechanicalperformanceof pages 15-17): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

9. (lopes2024interfaceboundarymechanical pages 105-108): LMA Lopes. Interface boundary mechanical resistance analysis in fff multi-material parts. Unknown journal, 2024.

10. (zatloukal2025optimizinginterfacialadhesion pages 4-6): Jakub Zatloukal, Mathieu Viry, Aleš Mizera, Pavel Stoklásek, Lukáš Miškařík, and Martin Bednařík. Optimizing interfacial adhesion and mechanical performance of multimaterial joints fabricated by material extrusion. Materials, 18:3846, Aug 2025. URL: https://doi.org/10.3390/ma18163846, doi:10.3390/ma18163846. This article has 6 citations.

11. (zhang2026mechanicalperformanceof pages 1-2): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

12. (catana2024bicomponentadditivemanufacturing pages 4-6): M Catana, SN Mazurchevici, and C Cărăușu. Bicomponent additive manufacturing of polymers-a review. Unknown journal, 2024.

13. (zatloukal2025optimizinginterfacialadhesion pages 10-12): Jakub Zatloukal, Mathieu Viry, Aleš Mizera, Pavel Stoklásek, Lukáš Miškařík, and Martin Bednařík. Optimizing interfacial adhesion and mechanical performance of multimaterial joints fabricated by material extrusion. Materials, 18:3846, Aug 2025. URL: https://doi.org/10.3390/ma18163846, doi:10.3390/ma18163846. This article has 6 citations.

14. (zatloukal2025optimizinginterfacialadhesion pages 2-4): Jakub Zatloukal, Mathieu Viry, Aleš Mizera, Pavel Stoklásek, Lukáš Miškařík, and Martin Bednařík. Optimizing interfacial adhesion and mechanical performance of multimaterial joints fabricated by material extrusion. Materials, 18:3846, Aug 2025. URL: https://doi.org/10.3390/ma18163846, doi:10.3390/ma18163846. This article has 6 citations.

15. (zatloukal2025optimizinginterfacialadhesion pages 12-14): Jakub Zatloukal, Mathieu Viry, Aleš Mizera, Pavel Stoklásek, Lukáš Miškařík, and Martin Bednařík. Optimizing interfacial adhesion and mechanical performance of multimaterial joints fabricated by material extrusion. Materials, 18:3846, Aug 2025. URL: https://doi.org/10.3390/ma18163846, doi:10.3390/ma18163846. This article has 6 citations.

16. (zatloukal2025optimizinginterfacialadhesion pages 6-10): Jakub Zatloukal, Mathieu Viry, Aleš Mizera, Pavel Stoklásek, Lukáš Miškařík, and Martin Bednařík. Optimizing interfacial adhesion and mechanical performance of multimaterial joints fabricated by material extrusion. Materials, 18:3846, Aug 2025. URL: https://doi.org/10.3390/ma18163846, doi:10.3390/ma18163846. This article has 6 citations.

17. (lopes2024interfaceboundarymechanical pages 49-55): LMA Lopes. Interface boundary mechanical resistance analysis in fff multi-material parts. Unknown journal, 2024.

18. (lopes2024interfaceboundarymechanical pages 55-61): LMA Lopes. Interface boundary mechanical resistance analysis in fff multi-material parts. Unknown journal, 2024.

19. (giani2022productionandcharacterization pages 12-16): N Giani. Production and characterization of novel thermoplastic (nano) composite materials for additive manufacturing applications. Unknown journal, 2022.

20. (giani2022productionandcharacterization pages 51-55): N Giani. Production and characterization of novel thermoplastic (nano) composite materials for additive manufacturing applications. Unknown journal, 2022.

21. (lopes2024interfaceboundarymechanical pages 61-69): LMA Lopes. Interface boundary mechanical resistance analysis in fff multi-material parts. Unknown journal, 2024.