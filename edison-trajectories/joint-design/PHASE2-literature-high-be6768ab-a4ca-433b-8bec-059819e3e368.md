Question: High-effort, citation-dense literature survey (peer-reviewed papers, dissertations,
patents, and well-documented open-source CAD/code where applicable).

GOAL: Identify *prior published examples* of each of the following five candidate
joint designs for connecting TPU cables to PETG struts in a 3D-printed (FDM, IDEX
dual-extruder, 0.4 mm nozzle) tensegrity-like structure. For each design, give
(a) the closest-matching published implementation(s), (b) the materials and
fabrication route used (multi-material FDM vs. polyjet vs. assembly), (c) measured
mechanical performance (pull-out force, cyclic durability, energy absorbed under
impact, hysteresis), and (d) any reported limitations or failure modes. Focus on
work in tensegrity, soft robotics, architected metamaterials, energy absorbers,
and 3D-printed compliant mechanisms.

The five joint design ideas being evaluated:
  (A-anchor-bulb) Anchor-bulb spherical node (PETG sphere with through-holes; TPU cable terminated in a printed-in-place TPU bulb)
  (B-dovetail) Co-printed mechanical interlock (PETG dovetail/T-slot strut tip + TPU dovetail/T-head cable head)
  (C-tpu-sleeve-overmold) TPU overmolded sleeve over a knurled / grooved PETG strut tip (Ye 2023 / Khatri 2024-style PETG-TPU wrap)
  (D-eyelet-loop) Captive TPU loop threaded through a printed PETG eyelet (chain-link, topological constraint only)
  (E-tpu-rebar) TPU 'rebar' embedded several mm into the PETG strut tip (mechanical pullout, 'rebar in concrete')

Description of each idea (verbatim from the 1-credit literature queries that just
ran):

(A-anchor-bulb) A spherical PETG joint node (~7-10 mm Ø) at each vertex of the T3-prism. The
sphere has 4 through-holes (one per converging member): a 6.2 mm Ø axial blind
hole that accepts the PETG strut tip (printed in the same pass), and three
2.6 mm Ø through-holes oriented along the bottom-cable, top-cable, and
saddle-cable directions. Each TPU cable is printed as a continuous filament
that passes *through* the through-hole and terminates in a 4-5 mm Ø TPU
'bulb' (printed-in-place after a few additional layers above the sphere top
surface, so the bulb cannot pull back through the 2.6 mm hole). Bulbs at
both ends of the cable provide bilateral mechanical anchoring without
relying on PETG-TPU chemical adhesion. Closest analog: clew/socket joints
in rigging, button-knot terminations on bungee cord, and 'bone-shaped'
co-printed inserts in compliant mechanism literature.

(B-dovetail) The PETG strut terminates in a 7 mm wide x 4 mm tall x 5 mm deep T-slot
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

(C-tpu-sleeve-overmold) The last 6-10 mm of each PETG strut tip is knurled (helical or annular
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

(D-eyelet-loop) The PETG strut terminates in a closed eyelet ring (~5 mm outer Ø, 2.4 mm
inner Ø, 1.3 mm wall, plane normal to the cable direction). Each TPU
cable is printed as a *closed loop* (oval, ~12-15 mm long axis) that
passes through the PETG eyelet — exactly the way two chain links
interlink. The TPU cable and PETG eyelet are mechanically independent
parts after the print finishes (no shared interface), held together
purely by the topology of the closed-loop linkage, like a chain. This
sidesteps the PETG-TPU adhesion problem entirely. Trade-off: the
eyelet+loop pair adds geometric slack (~2-3 mm of free play) before the
cable becomes tensile-loaded. Closest analog: chain links, ring-and-loop
terminations on climbing slings, the welded-loop bungee terminations on
some camping cots.

(E-tpu-rebar) The TPU cable continues 8-12 mm *into* the body of the PETG strut at
each end (i.e. the cable end is buried inside the strut tip). The
embedded section may be a straight cylinder, a Christmas-tree/barb
profile (3 stacked truncated cones, base Ø 3.2 mm, neck Ø 2.4 mm,
spacing 2 mm), or a hook/J shape. Subsequent PETG layers are printed on
top of and around the embedded TPU, encapsulating it. Resistance to
pullout comes purely from mechanical interference + friction + (very
weak) PETG-TPU adhesion. Closest analog: rebar in concrete, tendon
anchorage zones in pre-stressed concrete beams, and the embedded
TPU lattice cores of dual-material drop-tower specimens reported in
recent additive manufacturing energy-absorber literature.

Please rank the five designs by *strength of prior art* (most-precedented to
least-precedented) and identify any closely related joint topologies we may have
missed (e.g. hybrid sleeve + bulb, fiber-reinforced TPU, post-print epoxy / heat
weld). Drop tests are central to our validation (Lansmont M23 + Polytec QTec) so
prioritize literature that reports impact / drop / dynamic loading rather than
pure quasi-static tension.


## Literature Survey: Prior Art for Five Candidate TPU-to-PETG Joint Designs in 3D-Printed Tensegrity Structures

### 1. Introduction and Scope

This survey identifies published precedents for five candidate joint designs intended to connect flexible TPU cables to rigid PETG struts in a dual-extruder FDM tensegrity-like structure. The literature was searched across peer-reviewed journals, dissertations, conference proceedings, and patents in the domains of multi-material additive manufacturing, soft robotics, tensegrity structures, architected metamaterials, and energy absorbers. Priority was given to sources reporting dynamic/impact loading data, though the vast majority of the multi-material FDM interface literature is quasi-static.

### 2. Prior Art Ranking (Most to Least Precedented)

The five designs are ranked below by strength of directly applicable published prior art. The comprehensive comparison table follows.

| Rank | Design ID and Name | Closest Published Prior Art | Materials & Fabrication Route | Best Measured Mechanical Performance | Reported Failure Modes / Limitations | Prior Art Strength Rating |
|---:|---|---|---|---|---|---|
| 1 | **B — Co-printed mechanical interlock (dovetail / T-slot / T-head)** | Closest matches are explicit multi-material mechanical interlocks: ASA–TPU dovetail, T-shape, omega profiles in **Ermolai 2024**; PLA–TPU dovetail bio-inspired interfaces in **Zhang 2021**; PLA–PET T-shape / “Mickey Mouse” in **Frascio 2024**; bi-material FDM mechanical interlocking joints in **Zhang 2026**. This is the most directly precedented of the five concepts. (ermolai2024mechanicalbehaviorof pages 4-6, ermolai2024mechanicalbehaviorof pages 6-9, ermolai2024mechanicalbehaviorof pages 9-10, zhang20213dprintingof pages 1-7, zhang20213dprintingofa pages 81-89, frascio2024investigatingenhancedinterfacial pages 4-7, frascio2024investigatingenhancedinterfacial pages 7-8, zhang2026mechanicalperformanceof pages 1-2) | Multi-material FDM / FFF throughout. ASA–TPU (Ermolai), PLA–TPU (Zhang 2021; Zhang 2026), PLA–PET on Prusa MMU (Frascio). Geometries were intentionally sized around printable filament widths and mechanical locking, not chemistry alone. (ermolai2024mechanicalbehaviorof pages 4-6, zhang20213dprintingof pages 1-7, frascio2024investigatingenhancedinterfacial pages 2-4, zhang20213dprintingofb pages 44-52) | Highest explicit joint strengths in the corpus: **10.22 ± 1.11 MPa** tensile for ASA–TPU T-shaped interface; dovetail and omega interfaces commonly **~8.1–9.6 MPa** tensile; PLA–TPU dovetail reached **11.46 MPa UTS** at 5° angle; PLA–TPU mechanical-interlock joints reached **6.58 ± 0.33 MPa tensile** and **24.47 ± 1.99 MPa shear**; shaped interfaces improved strength versus butt interfaces by up to **58%**. Energy absorption/toughness increased substantially in dovetail PLA–TPU systems; cyclic tests showed strain hardening and delayed failure for interlocked designs. (ermolai2024mechanicalbehaviorof pages 4-6, ermolai2024mechanicalbehaviorof pages 6-9, zhang20213dprintingof pages 1-7, zhang20213dprintingofa pages 81-89, frascio2024investigatingenhancedinterfacial pages 7-8, zhang2026mechanicalperformanceof pages 1-2, zhang20213dprintingofb pages 81-89) | Short-interface fracture, long-interface shearing, tablet pull-out, occasional rigid-part fracture, brittle male-part failure in sharp T interfaces, stress concentrations, printability/undercut constraints, and dependence on overlap / interlock side / angle. Performance remains sensitive to interfacial voids and material mismatch. (ermolai2024mechanicalbehaviorof pages 6-9, zhang20213dprintingof pages 1-7, zhang20213dprintingofa pages 81-89, frascio2024investigatingenhancedinterfacial pages 4-7, frascio2024investigatingenhancedinterfacial pages 1-2) | **Strong** |
| 2 | **C — TPU sleeve overmold over knurled / grooved PETG tip** | No exact PETG-knurled-sleeve tensegrity joint was found, but the closest published analogs are rigid-shell / soft-core and wrapped multi-material architectures: **Yavas 2022** PLA-shell/TPU-core lattices and struts; **Khatri 2024** ABS–TPU multimaterial honeycombs. These support the basic “soft material wrapped around / bonded to rigid substrate to tune energy absorption” idea. (yavas2022designandfabrication pages 10-12, yavas2022designandfabrication pages 12-12, khatri2024energyabsorptionof pages 7-10, khatri2024energyabsorptionof pages 5-7) | Multi-material FFF/FDM. Yavas used an Ultimaker 3 dual-extruder with PLA shell and TPU 95A core; Khatri used FDM ABS/TPU multimaterial honeycombs with a tunable TPU band. These are not end-fittings, but they are directly relevant soft-over-rigid interface exemplars. (yavas2022designandfabrication pages 1-2, yavas2022designandfabrication pages 2-3, khatri2024energyabsorptionof pages 1-3) | Best adjacent performance is in energy absorption rather than pull-out: Yavas reported PLA–TPU interfaces with mixed-mode strengths of about **1.0 ± 0.2 MPa (mode I)** and **2.7 ± 0.5 MPa (mode II)**, with multi-material lattices showing **~2–3×** higher energy absorption than monolithic counterparts; Khatri reported out-of-plane energy absorption up to **15.11 ± 0.48 kN·mm** for hexagonal ABS honeycombs and strong tunability with TPU-band thickness. (yavas2022designandfabrication pages 12-12, yavas2022designandfabrication pages 10-12, khatri2024energyabsorptionof pages 7-10, khatri2024energyabsorptionof pages 10-11) | Interface delamination, row-by-row collapse after interface failure, random interfacial voids, saw-tooth interfacial waviness, wall buckling, TPU-first deformation followed by rigid-phase yielding, and sensitivity to deposition order / thermal mismatch. No published direct pull-out data for a sleeve-over-knurl end-fitting was found. (yavas2022designandfabrication pages 10-12, yavas2022designandfabrication pages 12-12, khatri2024energyabsorptionof pages 7-10, khatri2024energyabsorptionof pages 5-7) | **Moderate** |
| 3 | **D — Captive TPU loop through PETG eyelet (topological / chain-link constraint)** | Closest matches are: TPU95 loop-on-pin tendon terminations on PET-G tensegrity connectors in **Mortensen 2025**; chain-based / link-based load-bearing lattices in **Xu 2024**; topologically self-interlocking FDM assemblies in **Hussey 2020**. This is strong topological prior art, but only partial direct precedent for a TPU loop through a printed PETG eyelet with no adhesive interface. (mortensen2025tensegritybasedrobotleg pages 2-3, xu2024chainbasedlatticeprinting pages 1-2, xu2024chainbasedlatticeprinting pages 7-9, hussey2020lightweightdefecttoleranttopologicallyselfinterlocking pages 1-4) | Mortensen: PET-G rigid parts + TPU95 tendons, printed separately and assembled/interlocked via loops over pins / screws. Xu: ABS nodes + ABS tubes + Spectra string in robotically assembled chain lattice. Hussey: FDM PCL topologically self-interlocking polymeric assemblies. Mostly assembly / topological coupling, not co-printed PETG/TPU fusion. (mortensen2025tensegritybasedrobotleg pages 2-3, xu2024chainbasedlatticeprinting pages 3-4, hussey2020lightweightdefecttoleranttopologicallyselfinterlocking pages 6-9) | Mortensen gives functional tensegrity-joint validation and shock reduction (**34.7%** reduction in sudden-shock impact force at the leg level, from the paper abstract retrieved earlier), but not pull-out force for the loop itself; Xu’s 3×3×2 chain lattice sustained **~992 N** peak compressive load; Hussey’s self-interlocking structures reached **4.68 MPa** maximum tensile stress and **~2.7 J/cm³** absorbed energy. These support feasibility of topological capture and repeated loading, though not eyelet-loop pull-out specifically. (xu2024chainbasedlatticeprinting pages 1-2, xu2024chainbasedlatticeprinting pages 7-9, hussey2020lightweightdefecttoleranttopologicallyselfinterlocking pages 1-4, mortensen2025tensegritybasedrobotleg pages 2-3) | Main limitations are slack / compliance, weak node coupling, wear and surface damage across cycles, dependence on pins / screws or added coupling hardware, and lack of direct published pull-out numbers for a pure PETG-eyelet/TPU-loop linkage. Xu identified node coupling as the dominant weakness; Mortensen relies on hardware retention rather than pure topological entrapment. (xu2024chainbasedlatticeprinting pages 7-9, mortensen2025tensegritybasedrobotleg pages 2-3) | **Moderate** |
| 4 | **A — Anchor-bulb spherical node (PETG sphere with TPU bulb termination through hole)** | Closest matches are the **spherically-jointed tensegrity node** of **Pajunen 2019**, cable-end / hole / sleeve / socket strategies surveyed in **Bernaards 2014**, and looped TPU tendon terminations in **Mortensen 2025**. The spherical-node half is precedented; the printed-in-place TPU bulb anchor through a hole appears largely unpublished. (pajunen2019designandimpact pages 2-3, pajunen2019designandimpact pages 7-8, bernaards2014developmentofa pages 40-44, mortensen2025tensegritybasedrobotleg pages 2-3) | Pajunen used single-material SLS PA2200 to make spherically jointed tensegrity-inspired cells; Bernaards surveys assembled tensegrity joints with holes, sleeves, sockets, thimbles, clamps, threaded ends; Mortensen uses PET-G + TPU95 with looped tendon terminations secured to rigid parts. No direct PETG-sphere + TPU-bulb printed-in-place FDM example was found. (pajunen2019designandimpact pages 2-3, bernaards2014developmentofa pages 40-44, mortensen2025tensegritybasedrobotleg pages 2-3) | Best available quantitative evidence is dynamic rather than pull-out: Pajunen’s spherically-jointed design showed drop-impact resilience with **<0.2% residual strain per impact**, **~2.28%** average remaining strain after **24 impacts**, substantial hysteretic energy dissipation, and load-limiting force plateaus under a **200 g** drop-weight setup. These data support spherical-node mechanics but not bulb pull-out capacity. (pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 4-5, pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 8-9) | Fixed-jointed printed tensegrity variants ruptured near **~0.3 strain** due to joint stress concentrations; spherical redesign reduced those concentrations. For the proposed bulb anchor specifically, no direct literature was found on failure by bulb shear-through, hole-edge cutting, or TPU creep-through in FDM tensegrity nodes. Hence the anchor-bulb termination looks materially novel despite adjacent precedent. (pajunen2019designandimpact pages 3-4, pajunen2019designandimpact pages 2-3, bernaards2014developmentofa pages 40-44) | **Weak–Moderate** |
| 5 | **E — TPU “rebar” embedded into PETG strut tip (straight / barb / hook embedment)** | Closest analogs are embedded soft-in-rigid lattices and root / anchor pull-out studies: **Yavas 2022** (soft TPU core within rigid PLA shell), **Kim 2026** (3D-printed TPU/PLA root-inspired pullout anchors), and the embedded-geometry discussion in **Beguhn 2020** noted during search. However, no direct PETG-strut/TPU-rebar end-anchorage paper was found. (yavas2022designandfabrication pages 12-12, yavas2022designandfabrication pages 1-2) | Adjacent fabrication routes include multi-material FFF for embedded soft cores inside rigid shells (Yavas) and 3D-printed PLA/TPU anchor geometries for pull-out in granular media (Kim, from search results). These are mechanistically relevant but not the same as TPU filament buried in a PETG strut tip during IDEX printing. (yavas2022designandfabrication pages 1-2, yavas2022designandfabrication pages 12-12) | Best nearby measured values come from adjacent embedded-interface systems, not exact TPU-rebar joints: Yavas measured interface strengths of about **1.0 ± 0.2 MPa** (mode I) and **2.7 ± 0.5 MPa** (mode II), with **~2–3×** higher lattice energy absorption for the multi-material system. Kim’s anchor study supports the principle that geometry and embedment depth can raise pull-out resistance, but no directly transferable PETG/TPU pull-out force was retrieved here. (yavas2022designandfabrication pages 12-12, yavas2022designandfabrication pages 10-12) | Expected limitations from adjacent literature are interfacial voids, premature interface fracture, dependence on embedment geometry, and low reliability if chemical affinity is weak. Because no exact PETG-encapsulated TPU barb/j-hook paper was found, uncertainty is highest for this concept’s true pull-out performance and failure mode under cyclic tension. (yavas2022designandfabrication pages 10-12, yavas2022designandfabrication pages 12-12) | **Weak** |


*Table: This table ranks the five TPU-to-PETG joint concepts by how directly they are supported by published prior art and summarizes the closest implementations, fabrication routes, best available mechanical data, and reported failure modes.*

### 3. Design-by-Design Analysis

#### 3.1 Design B — Co-Printed Dovetail / T-Slot Mechanical Interlock (Rank 1: STRONG)

This is the most extensively studied of the five concepts. Ermolai et al. (2024) systematically tested six macroscopic interlocking interface geometries (dovetail, omega, T-shape, adapted variants) for FDM-printed ASA–TPU specimens, reporting tensile strengths of 8.1–10.2 MPa and Charpy impact energies of 2.3–4.9 kJ/m² depending on configuration (ermolai2024mechanicalbehaviorof pages 4-6, ermolai2024mechanicalbehaviorof pages 6-9, ermolai2024mechanicalbehaviorof pages 9-10). The T-shaped interface achieved the highest measured tensile stress of 10.22 ± 1.11 MPa. Zhang (2021) fabricated bio-inspired nacre-like dovetail specimens from PLA tablets and TPU filler at angles from 0° to 9°, finding that a 5° dovetail achieved 11.46 MPa UTS and 495.96 MPa modulus, with multi-stage deformation including short-interface fracture, tablet pull-out, and long-interface shearing (zhang20213dprintingof pages 1-7, zhang20213dprintingofa pages 81-89). Cyclic tensile tests demonstrated strain hardening and substantially higher energy dissipation relative to non-interlocked (0°) controls, which failed by cycle 3 (zhang20213dprintingofb pages 81-89, zhang20213dprintingof pages 13-19). Frascio et al. (2024) compared T-shaped and lobate "Mickey Mouse" geometries for PLA–PET multi-material FDM specimens, reporting that the T-shape improved tensile strength by 58% over a butt interface and increased elongation at break by 516% (frascio2024investigatingenhancedinterfacial pages 4-7, frascio2024investigatingenhancedinterfacial pages 7-8, frascio2024investigatingenhancedinterfacial pages 1-2). Zhang et al. (2026) measured PLA–TPU mechanical interlocking joints at peak tensile strength of 6.58 ± 0.33 MPa and shear strength of 24.47 ± 1.99 MPa (zhang2026mechanicalperformanceof pages 1-2). Key failure modes include brittle T-head fracture, short-interface cracking, and sensitivity to interlock angle and overlap (ermolai2024mechanicalbehaviorof pages 6-9, zhang20213dprintingof pages 1-7).

#### 3.2 Design C — TPU Overmolded Sleeve over Knurled PETG Tip (Rank 2: MODERATE)

No exact PETG-knurled-sleeve end-fitting was found, but the shell-over-core architecture is well studied. Yavas et al. (2022) fabricated PLA-shell / TPU 95A-core honeycomb lattices on an Ultimaker 3 dual-extruder and reported interfacial fracture properties of σ_I ≈ 1.0 ± 0.2 MPa and σ_II ≈ 2.7 ± 0.5 MPa, with mode I fracture energy G_I ≈ 48 ± 10 J/m² and mode II G_II ≈ 220 ± 70 J/m² (yavas2022designandfabrication pages 12-12). Multi-material lattices showed ~2–3× higher energy absorption than monolithic counterparts (yavas2022designandfabrication pages 10-12, yavas2022designandfabrication pages 1-2). Khatri and Egan (2024) tested ABS–TPU multimaterial honeycombs, reporting tunable out-of-plane energy absorption from 2.9 kN·mm (TPU-only) to 15.1 kN·mm (ABS-only hexagonal), with multimaterial designs permitting intermediate control via TPU band thickness (khatri2024energyabsorptionof pages 7-10, khatri2024energyabsorptionof pages 1-3, khatri2024energyabsorptionof pages 10-11). Failure modes included interfacial delamination attributed to thermal/viscosity mismatch and deposition order, wall buckling, and row-by-row staged collapse (khatri2024energyabsorptionof pages 7-10, khatri2024energyabsorptionof pages 5-7). These results support the overmold-sleeve concept's feasibility but do not provide pull-out data for a hoop-tension sleeve end-fitting.

#### 3.3 Design D — Captive TPU Loop Through PETG Eyelet (Rank 3: MODERATE)

The topological-constraint approach has partial precedent. Most directly, Mortensen et al. (2025) built a tensegrity robot leg using PET-G rigid connectors and TPU 95A tendons, where each tendon was 3D-printed with three integral loops that physically interlock with the rigid tristar pivot and Y-connector arms, secured by pins and a screw connection (mortensen2025tensegritybasedrobotleg pages 2-3). This represents a real-world PETG/TPU95 loop-on-pin tensegrity joint with demonstrated shock absorption (34.7% reduction in impact force). Hussey et al. (2020) demonstrated topologically self-interlocking FDM assemblies in PCL, achieving up to 4.68 MPa tensile stress and ~2.7 J/cm³ energy absorption with defect tolerance—individual element failure did not cascade (hussey2020lightweightdefecttoleranttopologicallyselfinterlocking pages 1-4). Xu and Dollar (2024) demonstrated a chain-based lattice printing approach where 3D-printed ABS link chains sustained ~992 N peak compressive load, though node coupling was identified as the primary weakness (~10 N per-strut axial limit with magnetic coupling) (xu2024chainbasedlatticeprinting pages 1-2, xu2024chainbasedlatticeprinting pages 7-9). The pure topological-capture approach (no fasteners, no adhesion) for TPU-through-PETG-eyelet remains unpublished.

#### 3.4 Design A — Anchor-Bulb Spherical Node (Rank 4: WEAK–MODERATE)

The spherical node geometry is precedented by Pajunen et al. (2019), who designed a 3D-printable tensegrity-inspired unit cell with spherical joints (sphere diameter 8.72 mm, member sizes 1.8–3.32 mm) fabricated in PA2200 via SLS (pajunen2019designandimpact pages 3-4, pajunen2019designandimpact pages 2-3). Under drop-weight impact testing (200 g mass at velocities up to the structure's buckling threshold), these cells exhibited load-limiting plateaus, hysteretic energy dissipation, and excellent reusability with <0.2% per-impact residual strain over 24 consecutive impacts (pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 4-5, pajunen2019designandimpact pages 5-7). This is the best available dynamic/impact data for any of the five designs, directly relevant to the user's Lansmont M23 + Polytec QTec validation plan. However, Pajunen's design is single-material, not multi-material TPU–PETG. Bernaards (2014) surveyed tensegrity cable-strut connection methods including through-holes, sleeves, sockets, thimbles, nuts, and turnbuckles, providing a design morphology for cable anchoring (bernaards2014developmentofa pages 40-44). The specific concept of a printed-in-place TPU bulb anchor through a restrictive hole in a PETG sphere appears novel and was not found in the literature.

#### 3.5 Design E — TPU "Rebar" Embedded in PETG Strut Tip (Rank 5: WEAK)

No direct PETG-encapsulated TPU barb/J-hook end-anchorage study was found. The closest analogies are Yavas et al.'s (2022) PLA–TPU shell-core lattices, where interfacial properties (σ_I ≈ 1 MPa, σ_II ≈ 2.7 MPa) govern structural failure and random interfacial voids reduce reliability (yavas2022designandfabrication pages 10-12, yavas2022designandfabrication pages 12-12). Kim et al. (2026) tested 3D-printed TPU and PLA root-inspired anchors in centrifuge pullout, demonstrating that geometry, embedment depth, and material stiffness jointly govern pullout resistance—flexible anchors show longer sustained resistance and higher residual capacity. Zhang's (2021) dovetail pull-out observations (tablet pull-out as a primary failure mode) are mechanistically relevant to a barbed anchor (zhang20213dprintingof pages 1-7, zhang20213dprintingofa pages 81-89). However, the PETG–TPU chemical affinity is very low, and all available evidence suggests that purely adhesion-dependent embedded interfaces suffer from interfacial voids, delamination, and premature failure (yavas2022designandfabrication pages 10-12, khatri2024energyabsorptionof pages 7-10). The rebar concept's reliance on mechanical interference in a material pair with near-zero chemical bonding makes it the highest-risk design.

### 4. Impact/Dynamic Loading Data

The user's focus on drop-test validation is best served by Pajunen et al. (2019), who provide the only comprehensive drop-weight impact dataset found for 3D-printed tensegrity-inspired structures: 200 g striker, velocities up to the buckling threshold (E_m ≈ 320 mJ), wave speeds of 65–135 m/s, force plateaus demonstrating load-limiting behavior, and cyclic resilience over 24 impacts with ~2.28% cumulative residual strain (pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 4-5, pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 8-9). Nearly all multi-material FDM interface studies (Ermolai, Zhang, Frascio, Yavas, Khatri) report only quasi-static tensile or compression data. The dearth of published dynamic/impact data on multi-material FDM joints represents a significant gap that the user's planned Lansmont M23 testing would address.

### 5. Missed Joint Topologies and Hybrid Designs

The following related joint approaches were not among the five candidates but emerged from the literature and merit consideration:

1. **Hybrid sleeve + bulb**: Combining Design A (bulb) with Design C (sleeve) would pair the topology-independent bulb anchor with the hoop-tension sleeve, potentially yielding redundant load paths. No published example was found, but the combination is mechanistically sound.

2. **Alternate-deposition / woven interfaces**: Zhang et al. (2026) reported that alternate-deposition (zebra-striped) PLA–TPU interfaces can outperform mechanical interlocking for some configurations (~12.8% higher tensile strength for PLA–TPU), suggesting a printing-path-based enhancement that could supplement any of the five designs (zhang2026mechanicalperformanceof pages 1-2).

3. **Lobate "Mickey Mouse" interfaces**: Frascio et al. (2024) showed that lobate interlocks trade peak strength for toughness and progressive failure, with 183% higher elongation at break versus butt joints (frascio2024investigatingenhancedinterfacial pages 7-8). This geometry could provide more gradual failure for impact applications.

4. **Post-print heat welding / solvent bonding / epoxy**: Not directly studied for TPU–PETG in the retrieved corpus, but commonly mentioned in multi-material reviews as a way to improve interfacial adhesion. Given TPU–PETG's low chemical affinity, mechanical post-processing (e.g., heat staking the bulb, solvent vapor treatment) could supplement any design.

5. **Continuous fiber reinforcement through the TPU cable**: Carbon or aramid fiber co-printed within the TPU cable would dramatically increase tensile strength and reduce creep, addressing a key limitation of all five designs under sustained tension.

6. **Loop-on-pin with screw retention**: Mortensen et al. (2025) already demonstrated this for PETG–TPU95 tensegrity joints, combining printed TPU loops with mechanical pin/screw fasteners—a pragmatic hybrid that could be partially printed-in-place (mortensen2025tensegritybasedrobotleg pages 2-3).

### 6. Conclusions

Design B (dovetail/T-slot interlock) has by far the strongest published prior art, with multiple studies providing measured tensile strengths of 6–11 MPa, shear strengths up to 24 MPa, cyclic durability data, and well-characterized failure modes across several rigid–flexible polymer pairs. Designs C and D have moderate prior art from adjacent domains (shell-core lattices and topological interlocking, respectively) but lack direct pull-out test data for the specific end-fitting geometries proposed. Design A benefits from excellent impact data on spherical tensegrity nodes but the printed-in-place bulb anchor concept itself appears novel. Design E has the weakest prior art, relying on analogy to embedded interfaces with known vulnerability to interfacial voids and low adhesion.

For the planned drop-test validation, it is notable that virtually no published study has performed impact testing on multi-material FDM rigid–flexible joints at the component/joint level. The Pajunen et al. (2019) drop-weight data on single-material tensegrity cells represents the closest available dynamic benchmark (pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 5-7). The user's Lansmont M23 + Polytec QTec test campaign would generate first-of-kind data for multi-material TPU–PETG joint impact performance and should be designed to capture both peak force and energy dissipation per impact cycle.

References

1. (ermolai2024mechanicalbehaviorof pages 4-6): Vasile Ermolai, Alexandru Sover, Marius Andrei Boca, Andrei Marius Mihalache, Alexandru Ionuț Irimia, Adelina Hrițuc, Laurențiu Slătineanu, Gheorghe Nagîț, and Răzvan Cosmin Stavarache. Mechanical behavior of macroscopic interfaces for 3d printed multi-material samples made of dissimilar materials. Mechanics &amp; Industry, 25:24, Jan 2024. URL: https://doi.org/10.1051/meca/2024017, doi:10.1051/meca/2024017. This article has 8 citations and is from a peer-reviewed journal.

2. (ermolai2024mechanicalbehaviorof pages 6-9): Vasile Ermolai, Alexandru Sover, Marius Andrei Boca, Andrei Marius Mihalache, Alexandru Ionuț Irimia, Adelina Hrițuc, Laurențiu Slătineanu, Gheorghe Nagîț, and Răzvan Cosmin Stavarache. Mechanical behavior of macroscopic interfaces for 3d printed multi-material samples made of dissimilar materials. Mechanics &amp; Industry, 25:24, Jan 2024. URL: https://doi.org/10.1051/meca/2024017, doi:10.1051/meca/2024017. This article has 8 citations and is from a peer-reviewed journal.

3. (ermolai2024mechanicalbehaviorof pages 9-10): Vasile Ermolai, Alexandru Sover, Marius Andrei Boca, Andrei Marius Mihalache, Alexandru Ionuț Irimia, Adelina Hrițuc, Laurențiu Slătineanu, Gheorghe Nagîț, and Răzvan Cosmin Stavarache. Mechanical behavior of macroscopic interfaces for 3d printed multi-material samples made of dissimilar materials. Mechanics &amp; Industry, 25:24, Jan 2024. URL: https://doi.org/10.1051/meca/2024017, doi:10.1051/meca/2024017. This article has 8 citations and is from a peer-reviewed journal.

4. (zhang20213dprintingof pages 1-7): X Zhang. 3d printing of bio-inspired, multi-material structures to enhance stiffness and toughness. Unknown journal, 2021.

5. (zhang20213dprintingofa pages 81-89): X Zhang. 3d printing of bio-inspired, multi-material structures to enhance stiffness and toughness. Unknown journal, 2021.

6. (frascio2024investigatingenhancedinterfacial pages 4-7): M. Frascio, A. Zafferani, M. Monti, and M. Avalle. Investigating enhanced interfacial adhesion in multi-material filament 3d printing: a comparative study of t and mickey mouse geometries. Progress in Additive Manufacturing, 9:2113-2122, Feb 2024. URL: https://doi.org/10.1007/s40964-024-00570-8, doi:10.1007/s40964-024-00570-8. This article has 14 citations and is from a peer-reviewed journal.

7. (frascio2024investigatingenhancedinterfacial pages 7-8): M. Frascio, A. Zafferani, M. Monti, and M. Avalle. Investigating enhanced interfacial adhesion in multi-material filament 3d printing: a comparative study of t and mickey mouse geometries. Progress in Additive Manufacturing, 9:2113-2122, Feb 2024. URL: https://doi.org/10.1007/s40964-024-00570-8, doi:10.1007/s40964-024-00570-8. This article has 14 citations and is from a peer-reviewed journal.

8. (zhang2026mechanicalperformanceof pages 1-2): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

9. (frascio2024investigatingenhancedinterfacial pages 2-4): M. Frascio, A. Zafferani, M. Monti, and M. Avalle. Investigating enhanced interfacial adhesion in multi-material filament 3d printing: a comparative study of t and mickey mouse geometries. Progress in Additive Manufacturing, 9:2113-2122, Feb 2024. URL: https://doi.org/10.1007/s40964-024-00570-8, doi:10.1007/s40964-024-00570-8. This article has 14 citations and is from a peer-reviewed journal.

10. (zhang20213dprintingofb pages 44-52): X Zhang. 3d printing of bio-inspired, multi-material structures to enhance stiffness and toughness. Unknown journal, 2021.

11. (zhang20213dprintingofb pages 81-89): X Zhang. 3d printing of bio-inspired, multi-material structures to enhance stiffness and toughness. Unknown journal, 2021.

12. (frascio2024investigatingenhancedinterfacial pages 1-2): M. Frascio, A. Zafferani, M. Monti, and M. Avalle. Investigating enhanced interfacial adhesion in multi-material filament 3d printing: a comparative study of t and mickey mouse geometries. Progress in Additive Manufacturing, 9:2113-2122, Feb 2024. URL: https://doi.org/10.1007/s40964-024-00570-8, doi:10.1007/s40964-024-00570-8. This article has 14 citations and is from a peer-reviewed journal.

13. (yavas2022designandfabrication pages 10-12): Denizhan Yavas, Qingyang Liu, Ziyang Zhang, and Dazhong Wu. Design and fabrication of architected multi-material lattices with tunable stiffness, strength, and energy absorption. Materials &amp; Design, 217:110613, May 2022. URL: https://doi.org/10.1016/j.matdes.2022.110613, doi:10.1016/j.matdes.2022.110613. This article has 144 citations and is from a highest quality peer-reviewed journal.

14. (yavas2022designandfabrication pages 12-12): Denizhan Yavas, Qingyang Liu, Ziyang Zhang, and Dazhong Wu. Design and fabrication of architected multi-material lattices with tunable stiffness, strength, and energy absorption. Materials &amp; Design, 217:110613, May 2022. URL: https://doi.org/10.1016/j.matdes.2022.110613, doi:10.1016/j.matdes.2022.110613. This article has 144 citations and is from a highest quality peer-reviewed journal.

15. (khatri2024energyabsorptionof pages 7-10): Nava Raj Khatri and Paul F. Egan. Energy absorption of 3d printed abs and tpu multimaterial honeycomb structures. 3D Printing and Additive Manufacturing, 11:e840-e850, Apr 2024. URL: https://doi.org/10.1089/3dp.2022.0196, doi:10.1089/3dp.2022.0196. This article has 29 citations and is from a peer-reviewed journal.

16. (khatri2024energyabsorptionof pages 5-7): Nava Raj Khatri and Paul F. Egan. Energy absorption of 3d printed abs and tpu multimaterial honeycomb structures. 3D Printing and Additive Manufacturing, 11:e840-e850, Apr 2024. URL: https://doi.org/10.1089/3dp.2022.0196, doi:10.1089/3dp.2022.0196. This article has 29 citations and is from a peer-reviewed journal.

17. (yavas2022designandfabrication pages 1-2): Denizhan Yavas, Qingyang Liu, Ziyang Zhang, and Dazhong Wu. Design and fabrication of architected multi-material lattices with tunable stiffness, strength, and energy absorption. Materials &amp; Design, 217:110613, May 2022. URL: https://doi.org/10.1016/j.matdes.2022.110613, doi:10.1016/j.matdes.2022.110613. This article has 144 citations and is from a highest quality peer-reviewed journal.

18. (yavas2022designandfabrication pages 2-3): Denizhan Yavas, Qingyang Liu, Ziyang Zhang, and Dazhong Wu. Design and fabrication of architected multi-material lattices with tunable stiffness, strength, and energy absorption. Materials &amp; Design, 217:110613, May 2022. URL: https://doi.org/10.1016/j.matdes.2022.110613, doi:10.1016/j.matdes.2022.110613. This article has 144 citations and is from a highest quality peer-reviewed journal.

19. (khatri2024energyabsorptionof pages 1-3): Nava Raj Khatri and Paul F. Egan. Energy absorption of 3d printed abs and tpu multimaterial honeycomb structures. 3D Printing and Additive Manufacturing, 11:e840-e850, Apr 2024. URL: https://doi.org/10.1089/3dp.2022.0196, doi:10.1089/3dp.2022.0196. This article has 29 citations and is from a peer-reviewed journal.

20. (khatri2024energyabsorptionof pages 10-11): Nava Raj Khatri and Paul F. Egan. Energy absorption of 3d printed abs and tpu multimaterial honeycomb structures. 3D Printing and Additive Manufacturing, 11:e840-e850, Apr 2024. URL: https://doi.org/10.1089/3dp.2022.0196, doi:10.1089/3dp.2022.0196. This article has 29 citations and is from a peer-reviewed journal.

21. (mortensen2025tensegritybasedrobotleg pages 2-3): Erik Mortensen, Jan Petrš, Alexander Dittrich, and Dario Floreano. Tensegrity-based robot leg design with variable stiffness. 2025 IEEE 8th International Conference on Soft Robotics (RoboSoft), pages 1-6, Apr 2025. URL: https://doi.org/10.48550/arxiv.2504.19685, doi:10.48550/arxiv.2504.19685. This article has 2 citations.

22. (xu2024chainbasedlatticeprinting pages 1-2): Zhe Xu and Aaron M. Dollar. Chain-based lattice printing for efficient robotically-assembled structures. Communications Engineering, Nov 2024. URL: https://doi.org/10.1038/s44172-024-00305-1, doi:10.1038/s44172-024-00305-1. This article has 6 citations and is from a peer-reviewed journal.

23. (xu2024chainbasedlatticeprinting pages 7-9): Zhe Xu and Aaron M. Dollar. Chain-based lattice printing for efficient robotically-assembled structures. Communications Engineering, Nov 2024. URL: https://doi.org/10.1038/s44172-024-00305-1, doi:10.1038/s44172-024-00305-1. This article has 6 citations and is from a peer-reviewed journal.

24. (hussey2020lightweightdefecttoleranttopologicallyselfinterlocking pages 1-4): Blake Hussey, Peyman Nikaeen, Matthew D. Dixon, Moulero Akobi, Ahmed Khattab, Lianjun Cheng, Zongxing Wang, Junru Li, Tian He, and Pengfei Zhang. Light-weight/defect-tolerant topologically self-interlocking polymeric structure by fused deposition modeling. Composites Part B-engineering, 183:107700, Feb 2020. URL: https://doi.org/10.1016/j.compositesb.2019.107700, doi:10.1016/j.compositesb.2019.107700. This article has 17 citations.

25. (xu2024chainbasedlatticeprinting pages 3-4): Zhe Xu and Aaron M. Dollar. Chain-based lattice printing for efficient robotically-assembled structures. Communications Engineering, Nov 2024. URL: https://doi.org/10.1038/s44172-024-00305-1, doi:10.1038/s44172-024-00305-1. This article has 6 citations and is from a peer-reviewed journal.

26. (hussey2020lightweightdefecttoleranttopologicallyselfinterlocking pages 6-9): Blake Hussey, Peyman Nikaeen, Matthew D. Dixon, Moulero Akobi, Ahmed Khattab, Lianjun Cheng, Zongxing Wang, Junru Li, Tian He, and Pengfei Zhang. Light-weight/defect-tolerant topologically self-interlocking polymeric structure by fused deposition modeling. Composites Part B-engineering, 183:107700, Feb 2020. URL: https://doi.org/10.1016/j.compositesb.2019.107700, doi:10.1016/j.compositesb.2019.107700. This article has 17 citations.

27. (pajunen2019designandimpact pages 2-3): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

28. (pajunen2019designandimpact pages 7-8): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

29. (bernaards2014developmentofa pages 40-44): X Bernaards, IPMP Teuffel, and IADCA Pronk. Development of a tensegrity joint. Unknown journal, 2014.

30. (pajunen2019designandimpact pages 4-5): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

31. (pajunen2019designandimpact pages 5-7): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

32. (pajunen2019designandimpact pages 8-9): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

33. (pajunen2019designandimpact pages 3-4): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 98 citations and is from a highest quality peer-reviewed journal.

34. (zhang20213dprintingof pages 13-19): X Zhang. 3d printing of bio-inspired, multi-material structures to enhance stiffness and toughness. Unknown journal, 2021.