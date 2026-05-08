Question: ## Joint design idea: Anchor-bulb spherical node (PETG sphere with through-holes; TPU cable terminated in a printed-in-place TPU bulb)

A spherical PETG joint node (~7-10 mm Ø) at each vertex of the T3-prism. The
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


## Technical assessment of the anchor‑bulb spherical node joint for PETG struts + TPU cables

### Executive summary
The anchor‑bulb concept is a sound direction for PETG+TPU tensegrity because it routes the load path through geometry (a TPU “button” behind a PETG hole) rather than through PETG↔TPU chemical adhesion, which is known to be weak in many multi‑material FDM combinations (zhang2026mechanicalperformanceof pages 1-2, catana2024bicomponentadditivemanufacturing pages 6-7). The design is manufacturable in a single IDEX print, but the current 7 mm sphere + 2.6 mm bores is likely *too tight* for reliable printing and for impact robustness. A first‑pass that is much more likely to succeed uses (i) a larger node (≈8.5–9 mm OD), (ii) larger cable bores (≈2.8–3.0 mm for a 2.2–2.4 mm TPU cable), (iii) generous fillets/chamfers at hole mouths, and (iv) strict seam control and purge control to prevent bore blockage and notch‑like crack initiation (US10953609B1 pages 96-97, EP3221128B1 pages 29-30).

---

## (1) Manufacturability on a 0.4 mm nozzle IDEX H2D (single print, no soluble support)

### 1.1 Primary printability risks
1. **Undersized / partially closed TPU routing holes**: A nominal 2.6 mm PETG bore with a 2.4 mm TPU “cable” leaves only 0.2 mm diametral clearance (0.1 mm per side). In real FDM, angled holes often print undersized due to stair‑stepping and sag; PETG/TPU contamination at tool changes can further reduce ID. That clearance is commonly insufficient for a continuous TPU filament to pass cleanly without bonding/rubbing and creating a “weld bead” that prevents free passage.
2. **Unsupported bore roofs and bulb formation**: Any near‑horizontal hole segment behaves like a small bridge/overhang inside the sphere. PETG sag or droop into the hole can create a burr that either blocks cable printing or becomes a cutting edge under load.
3. **Geometric crowding in a 7 mm node**: A 6 mm strut socket plus three ~2.6–3.0 mm cable bores leaves very thin PETG ligaments. Thin ligaments are notch‑sensitive under impact, and they are also difficult to print cleanly (minimum feature size ≈2–3 bead widths).
4. **Stacked seams near hole mouths**: Mark’s patents on routing reinforcement around holes emphasize that entrance/exit seams and “Y‑junction” stress concentrations can stack through “tens or even hundreds of layers,” creating persistent crack initiators; they recommend moving seams and avoiding sharp corners around holes (US10953609B1 pages 96-97, EP3221128B1 pages 29-30).

### 1.2 What makes it manufacturable
The approach becomes very plausible if you treat the sphere as a *precision routing/anchoring component* rather than a decorative joint sphere:
- **Increase node OD** to restore ligaments and reduce stress concentration (artifact-00).
- **Oversize through‑holes** to give realistic clearance for TPU and for toolchange contamination (artifact-00).
- **Chamfer/fillet hole mouths** (both for stress reduction and to improve print success) (US10953609B1 pages 96-97, EP3221128B1 pages 29-30).
- **Orient the print** so at least one hole is near vertical and none of the three cable holes has a long horizontal roof segment (artifact-00).
- **Print‑sequence discipline** (PETG defines the cavity first, TPU routes next, bulb is grown only after there is a stable local top surface) (artifact-00).

**Conclusion for (1):** Yes, manufacturable in a single print on an IDEX 0.4 mm system *if* you enlarge the node and bores and design for FDM tolerances; a 7 mm sphere with 2.6 mm bores is a high‑risk starting point (US10953609B1 pages 96-97, EP3221128B1 pages 29-30).

---

## (2) Likely failure modes under single‑impact drop testing (with rough quantitative bounds)

### 2.1 Failure modes specific to the anchor‑bulb scheme
Below are the failure modes most consistent with the load path and with known rigid–flexible joint behavior.

#### A. TPU bulb pull‑through (geometric failure)
**Mechanism:** Bulb plastically compresses and “necks” through the hole, or the bulb was under‑extruded / not fully fused.

**First‑order bound:** if the bulb OD exceeds hole OD by ~1.6–2.4 mm (e.g., 4.8–5.2 mm bulb behind a 2.8–3.0 mm hole) you are no longer in adhesion‑limited behavior; the limiting event becomes TPU yielding/tearing in the neck region or PETG ligament fracture (artifact-00).

A conservative estimate for *tensile* capacity of a 2.4 mm solid TPU cable, if it fails by cable rupture rather than pull‑through:
- Area A ≈ π(1.2 mm)^2 ≈ 4.52 mm².
- If printed TPU strength is on the order of ~12 MPa (reported for TPU filament in PLA/TPU joint work) then F ≈ σA ≈ 12 MPa × 4.52 mm² ≈ 54 N (zhang2026mechanicalperformanceof pages 6-8).
This is not a guarantee for your TPU (brands differ), but it sets the right *order of magnitude*: tens of newtons per cable before TPU rupture if the print is good.

If instead the **neck** is intentionally reduced (say 1.6–2.0 mm diameter, as a “fuse”), then A_neck ≈ 2.0–3.1 mm² and rupture loads scale down proportionally (artifact-00).

#### B. TPU tear‑through / cutting at PETG hole edge
**Mechanism:** Under shock, the cable is pulled at an angle; contact pressure concentrates at the hole mouth; a sharp PETG edge or seam ridge acts as a knife.

**Design implication:** The Mark patents explicitly emphasize avoiding sharp corners around holes and smooth looping/radii to reduce stress concentrations, and avoiding seam stacking (US10953609B1 pages 96-97, EP3221128B1 pages 29-30). Translating that to your joint means: add ≥0.4–0.8 mm fillet/chamfer at both ends of the cable bore and keep seams away from bore mouths (artifact-00).

#### C. PETG ligament cracking / node splitting (brittle rigid failure)
**Mechanism:** Local hoop stress around the bore plus bending moment from off‑axis cable tension cracks the thinnest ligament; cracks often initiate at a seam stack or at a “Y” intersection between bores.

**Why likely in your envelope:** A 7 mm sphere with a 6 mm socket plus three 2.6 mm bores leaves minimal ligament thickness—often below ~1 mm. Under impact, this is a classic notch‑sensitive condition.

**Qualitative support:** Interfacial/joint studies on rigid–flexible parts show that geometry‑driven stress concentrations can control failure (tooth root fracture vs sliding) (zhang2026mechanicalperformanceof pages 15-17).

#### D. Strut root hinge yielding / delamination within PETG
**Mechanism:** The strut behaves like a cantilever into the sphere; impact causes a bending moment that concentrates at the strut‑sphere junction.

**Mitigation:** Increase strut root fillet (≈0.8–1.2 mm) and make the node region solid with high perimeter count (artifact-00).

#### E. Time‑dependent losses: TPU creep + frictional wear
**Mechanism:** TPU under sustained preload creeps (increasing effective tendon length), and cyclic micro‑slip at the hole produces abrasion and heating. Soft robotics literature emphasizes that tendon friction and viscoelasticity introduce hysteresis and wear, and designers often avoid distal tendon routing to reduce stress concentrations and damage (favaro2026investigationofoctopus pages 24-29). Under impact, the *first* event is usually not creep, but creep will change your baseline pre‑tension and dynamic response.

### 2.2 Relating to published rigid–flexible joint strengths (contextual bounds)
While not your exact geometry, the following numbers help bracket what *interface‑level* stresses look like in multi‑material FDM when load transfer is not purely geometric:
- PLA/TPU mechanical‑interlocking joints: maximum tensile strength ~6.6 MPa and maximum shear strength ~24.5 MPa (zhang2026mechanicalperformanceof pages 1-2, zhang2026mechanicalperformanceof pages 15-17).
- PETG and TPU used as “adhesives” in lap shear: PETG average shear stress ~16.9 MPa; TPU ~10.0 MPa, with TPU showing large displacement/energy absorption (oz2025acomprehensiveexperimental pages 13-15, oz2025acomprehensiveexperimental pages 15-16).
Your bulb anchor is intended to avoid operating in this adhesion‑limited regime; however, these values are still useful as *sanity checks* when estimating PETG ligament shear stress around the hole.

---

## (3) How well it preserves “rigid struts + ideal massless tendons” assumptions

### 3.1 Where compliance leaks in
Even if cables are treated as ideal tendons, your joint introduces at least four compliance elements in series/parallel:
1. **TPU axial compliance of the cable** (dominant; TPU modulus is orders of magnitude lower than rigid plastics). PLA/TPU joint studies report TPU modulus ~7.9 MPa (specimen-level) (zhang2026mechanicalperformanceof pages 6-8) and other work reports TPU modulus in the tens of MPa range (zhang2026mechanicalperformanceof pages 4-6). This will dominate stiffness relative to PETG.
2. **Bulb/neck compliance**: the transition from 2.4 mm cable to bulb and any intentional necking adds a local “soft spring,” and during impact it may act like a strain‑rate‑dependent damper.
3. **Hole contact / friction**: off‑axis loading creates normal force at the hole mouth; the tendon can micro‑slip. Mark’s work emphasizes hole entrance/exit stress concentrations and seam stacks, consistent with the idea that the entrance region is a special mechanical element (US10953609B1 pages 96-97, EP3221128B1 pages 29-30).
4. **Node micro‑rotation**: the PETG node is not infinitely stiff—especially if ligaments are thin. Under load you can get a small rotation that effectively changes tendon length (apparent compliance).

### 3.2 Practical modeling parameterization for simulators
To preserve your existing tendon abstraction while capturing dominant nonidealities:
- Model each cable as a tendon with **axial spring k_t** (from TPU modulus and area) and **axial damping c_t**.
- Add a *series* “attachment compliance” spring **k_attach** at each node capturing bulb/neck stretch plus local PETG compliance.
- Add a **friction slider** at each hole: Coulomb friction + small viscous term to model hysteresis. Soft-robotics tendon routing reports friction‑driven hysteresis and non‑repeatability as common issues (favaro2026investigationofoctopus pages 24-29).
- Add a failure criterion based on **maximum tension** (TPU rupture) and **maximum bearing stress** at the hole mouth (PETG crack initiation).

You can get an order‑of‑magnitude for stiffness from unrelated but illustrative lap‑joint data: PETG SLJ failure load 10,561 N at ~1.81 mm displacement implies an effective stiffness scale k~5.8 kN/mm for that specific steel‑adherend joint geometry (not directly transferable, but it shows that stiff polymer joints can be far stiffer than your TPU cable, so cable + neck will dominate) (oz2025acomprehensiveexperimental pages 10-13).

---

## (4) Cited prior art closest to this joint concept

### 4.1 Mechanical interlocking dominates over chemical bonding (relevant principle)
- A review of multi‑material PLA/TPU interface types reports that macroscopic mechanical interlocks (e.g., T‑shape) are stronger than “microscopic” chemical bonding interfaces, and that U‑shape/dovetail interfaces tended to separate along the interface for PLA‑TPU (catana2024bicomponentadditivemanufacturing pages 6-7). This supports your design choice to avoid relying on PETG‑TPU adhesion.

### 4.2 Quantified rigid–flexible FDM joint strengths and failure modes
- Zhang et al. measured tensile and shear strengths for PLA/TPU rigid–flexible joints under two strategies (alternate deposition and mechanical interlocking), with shear strengths up to ~24.5 MPa and explicit failure observations: interlocking tends to fail by **tooth shear fracture** with minimal sliding, while alternate deposition fails by **interlayer sliding** (zhang2026mechanicalperformanceof pages 1-2, zhang2026mechanicalperformanceof pages 15-17). This maps cleanly onto your “geometry‑anchored” vs “adhesion‑anchored” design intent.

### 4.3 Hole/entrance stress concentration + seam stacking around holes
- Mark’s patents discuss routed continuous reinforcement around holes/negative contours and emphasize that entrance/exit corners create stress concentrations; stacked seams can extend through “tens or even hundreds of layers,” motivating seam relocation and avoidance of sharp corners (sharp corner radius defined as 0 to twice swath width) (US10953609B1 pages 96-97, EP3221128B1 pages 29-30). This is directly applicable to your PETG sphere: avoid seam placement at hole mouths and add radii/chamfers.

### 4.4 Tendon anchoring in soft robotics (hole + stopper knot analog)
- Favaro used a 3D‑printed support with a 0.8 mm through‑hole and a stopper knot to mechanically lock a fishing line tendon, explicitly to prevent slippage and transfer tensile load reliably (favaro2026investigationofoctopus pages 59-64). Your bulb is a printed-in-place analog of the knot/stopper.
- Sholl & Mohseni note weak adhesion to monofilament tendons can fail immediately and route tendons relative to embedded fibers to prevent tear‑through; their servos can apply up to 75 N, giving a relevant force scale for tendon-driven loads (sholl2024highstretchtendondrivenfiberreinforced pages 8-9).

---

## (5) Concrete first‑pass numerical recommendations (geometry + slicer/process)
The following artifact consolidates the recommended first-pass geometry, sequencing, and slicer settings.

| Category | Parameter | First-pass recommendation | Notes / rationale |
|---|---|---:|---|
| Geometry | Sphere OD | 8.5-9.0 mm | 7 mm is likely too tight once 1 strut socket + 3 cable holes + ligaments + chamfers are included; enlarging the node improves printable ligaments and reduces PETG crack risk. |
| Geometry | PETG strut OD | 6.0 mm | Keep as designed if global prism geometry depends on it. |
| Geometry | PETG strut socket / blind hole ID | 6.15-6.30 mm | Start at 6.2 mm nominal; for same-pass printed continuity, avoid sharp root transitions. |
| Geometry | PETG strut embed depth into sphere | 2.0-2.8 mm | Enough to avoid a hinge at the sphere/strut junction without consuming all node volume. |
| Geometry | TPU cable OD | 2.2-2.4 mm | Prefer 2.2-2.3 mm if routing friction or crowding is problematic. |
| Geometry | TPU through-hole ID | 2.8-3.0 mm | 2.6 mm is likely too tight for reliable printed-in-place TPU passage on a 0.4 mm nozzle; target ~0.4-0.7 mm diametral clearance over cable OD. |
| Geometry | TPU bulb max OD | 4.6-5.2 mm | Gives ~1.6-2.4 mm OD oversize relative to a 2.8-3.0 mm hole for mechanical retention. |
| Geometry | TPU bulb axial thickness | 2.2-3.0 mm | Too thin risks necking/tear-through; too thick increases interference with neighboring members. |
| Geometry | TPU neck diameter at hole exit | 1.6-2.0 mm | Intentionally necked region localizes extension in TPU, but keep >~4 bead-widths to avoid weak single-road sections. |
| Geometry | PETG ligament: hole edge to outer sphere surface | >=1.2 mm preferred, 1.0 mm absolute minimum | Below ~1 mm, PETG around angled holes becomes notch-sensitive under impact. |
| Geometry | PETG ligament between adjacent cable holes / socket wall | >=1.0-1.4 mm | Important because three cable bores and one strut socket crowd the sphere; increase sphere OD if this is violated. |
| Geometry | Edge treatment at cable holes | 0.4-0.8 mm radius or 0.3-0.5 mm x 45° chamfer | Reduces TPU cutting at the PETG hole edge under shock and cyclic rubbing. |
| Geometry | Edge treatment at strut root | 0.8-1.2 mm fillet | Lowers PETG hinge stress where the strut emerges from the sphere. |
| Geometry | Lead-in cone for cable holes | 30-45° included angle, 0.4-0.8 mm deep on both faces | Improves TPU threading/bridging and reduces stress concentration at the bore mouth. |
| Geometry | Lead-in cone for strut socket | 0.3-0.6 mm chamfer | Helps slicer path quality and avoids elephant-foot interference inside the socket. |
| Geometry | Cable-hole centerline angular separation | Maximize; keep >=35-40° between neighboring exits if possible | If not achievable in a 7 mm node, enlarge the sphere or split the exits onto a teardrop/lobed node. |
| Orientation | Preferred print orientation | One cable hole as near-vertical as possible; strut axis ~horizontal to 20° up | Minimizes unsupported roof length in the cable bores and keeps bulbs printable above a local top surface. |
| Orientation | Avoid | Perfectly horizontal 2.6-3.0 mm bores intersecting near the sphere crown | High risk of sagging, blocked bores, and TPU dragging in unsupported cavities. |
| IDEX sequencing | Nozzle assignment | Tool 0 PETG; Tool 1 TPU 95A | Keep rigid/flexible assignments fixed through the job. |
| IDEX sequencing | Material order by layer | Print PETG shell/socket features first on each mixed layer, then TPU cable pass, then TPU bulb on layers where bulb appears | Lets PETG define the mechanical cavity and TPU occupy it without relying on chemical bonding. |
| IDEX sequencing | Bulb creation | Delay bulb enlargement until cable has already passed through the hole and at least 2-4 PETG/TPU layers establish the local top support region | Reduces chance of the slicer trying to form a floating TPU blob. |
| IDEX sequencing | Print strategy | Prefer printing a calibration coupon with 1 sphere + 1 cable anchor before full prism | Necessary because tolerances are dominated by real toolpath formation, not CAD. |
| PETG slicer | Layer height | 0.16-0.20 mm | 0.16 mm if maximizing hole fidelity; 0.20 mm for faster screening. |
| PETG slicer | Line width | 0.42-0.46 mm | Slightly over-nozzle improves sealing and local ligament strength. |
| PETG slicer | Walls / perimeters in sphere | 5-6 | Node should behave close to solid near holes; extra walls beat sparse infill in a tiny sphere. |
| PETG slicer | Top / bottom layers | 6-8 | Helps preserve local roof integrity around bores. |
| PETG slicer | Infill in sphere / strut root region | 100% in node and first 8-12 mm of strut; 40-60% beyond if desired | For a small node, just make it solid. |
| PETG slicer | Nozzle temperature | 245-255 °C | Start ~250 °C for good interlayer fusion. |
| PETG slicer | Bed temperature | 75-85 °C | Typical PETG window; tune to your plate. |
| PETG slicer | Outer wall speed | 25-35 mm/s | Better dimensional control at tiny bores. |
| PETG slicer | Inner wall / infill speed | 35-50 mm/s | Keep modest to avoid ringing in crowded node geometry. |
| PETG slicer | Fan | 15-35% after first layers | Enough to hold bore roofs without sacrificing bonding. |
| TPU slicer | Material | TPU 95A | Softer TPU increases damping but will worsen creep and print stability. |
| TPU slicer | Layer height | 0.20 mm | Robust default for 0.4 mm nozzle and 2.2-2.4 mm cable diameters. |
| TPU slicer | Line width | 0.42-0.48 mm | Helps fuse the cable into a dense cross-section. |
| TPU slicer | Walls in cable/bulb | 3-4 | On a solid cable, this is effectively most of the section. |
| TPU slicer | Infill | 100% | Tension member should be solid, not sparse. |
| TPU slicer | Nozzle temperature | 225-235 °C | Start ~230 °C; dry filament first. |
| TPU slicer | Bed temperature | 35-50 °C | Enough for placement without excessive smear. |
| TPU slicer | Print speed | 15-25 mm/s | Use 15-20 mm/s for the node region and bulbs. |
| TPU slicer | Travel speed | 120-180 mm/s | Keep high, but ensure pressure advance is tuned. |
| TPU slicer | Retraction | Minimal or off; if needed 0.4-0.8 mm at low speed | TPU is string-prone; excessive retraction causes jams and dimensional inconsistency. |
| TPU slicer | Fan | 30-60% | More fan than PETG helps bulb shape and bridge control. |
| Special settings | Wipe tower / prime tower | Yes, mandatory for PETG<->TPU swaps | TPU contamination in PETG holes and PETG contamination in TPU bulbs will ruin fit; use a generous tower. |
| Special settings | Prime / purge volume | Medium-high; tune empirically, start conservative | Mixed-material transitions are a major defect source in small anchor features. |
| Special settings | Z-hop | 0.2-0.4 mm on TPU travels | Reduces dragging across partially formed bulbs and hole exits. |
| Special settings | Minimum layer time | 6-10 s | Critical for bulb geometry and small sphere roof quality. |
| Special settings | Seam placement | Move seams away from hole mouths and strut root | Stacked seams at hole exits can seed PETG cracking (US10953609B1 pages 96-97, EP3221128B1 pages 29-30). |
| Special settings | Hole compensation | +0.10 to +0.20 mm horizontal expansion for TPU bores if test coupons print undersized | Small angled bores often close up in practice. |
| Special settings | Drying | Dry both filaments; TPU especially | Wet TPU causes bubbles, weak bulbs, and poor dimensional repeatability. |
| Acceptance check | Visual | Cable holes fully open; no PETG sag blocking bore; bulb fully formed and centered | Reject any node with partial blockage or asymmetric bulb. |
| Acceptance check | Dimensional | Printed cable-hole ID within +/-0.10 mm of target; bulb OD within +/-0.15 mm | Measure on coupons before prism build. |
| Acceptance check | Assembly-free retention test | Manual pull to seat both bulbs, then monotonic tensile test on single anchor coupon | First-pass goal: failure in TPU neck or cable body before simple pull-through. |
| Acceptance check | Early screening load target | Survive at least 2-3x expected nominal cable preload without pull-through | Because impact loads will far exceed static preload. |
| Acceptance check | Failure signature target | Prefer TPU elongation / necking or gross PETG sphere fracture over interfacial slide | Load path should be geometric, not adhesion-dominated (catana2024bicomponentadditivemanufacturing pages 6-7, zhang2026mechanicalperformanceof pages 15-17, zhang2026mechanicalperformanceof pages 1-2, sholl2024highstretchtendondrivenfiberreinforced pages 8-9, favaro2026investigationofoctopus pages 59-64) |


*Table: This table gives a compact first-pass specification for geometry, print sequencing, slicer settings, and inspection of a PETG spherical node with TPU through-hole bulb anchors. It is intended as a practical starting point for coupon fabrication on a dual-extrusion FDM system before committing to a full tensegrity print.*

Key deltas versus your current proposal (most important knobs):
- **Node OD:** start at **8.5–9.0 mm** (not 7 mm) to preserve PETG ligaments and reduce brittle splitting risk (artifact-00).
- **Cable bore ID:** start at **2.8–3.0 mm** (not 2.6 mm) for a 2.2–2.4 mm TPU cable (artifact-00).
- **Hole edge treatment:** add **0.4–0.8 mm** radii or chamfers at *both* bore mouths; control seam placement away from hole mouths (US10953609B1 pages 96-97, EP3221128B1 pages 29-30).
- **Bulb OD / thickness:** start at **4.6–5.2 mm OD** and **2.2–3.0 mm axial thickness**, and avoid printing it as a free‑space blob—grow it after a stable local top surface exists (artifact-00).

---

## Suggested minimal validation coupon set (before full T3 prints)
1. **Single‑hole retention coupon**: PETG block with one angled through‑hole (your target angle), TPU cable through it, bulbs at both ends. Measure monotonic pull‑out force and observe whether failure is (i) TPU neck rupture, (ii) bulb pull‑through, or (iii) PETG crack.
2. **Tri‑hole sphere coupon**: just the node region with three bores + strut socket stub. Inspect bore openness and ligament thickness after slicing.
3. **Impact coupon**: 3 nodes connected by 3 struts and 3 cables (a minimal tensegrity triangle) to observe whether failures localize at hole edges (cutting), at PETG ligaments (cracking), or in TPU (necking).

This staged approach aligns with literature observations that multi‑material interfaces are highly sensitive to geometry, material compatibility, and stress concentrations, and that optimizing geometry is often more impactful than trying to improve chemistry in incompatible pairs (zhang2026mechanicalperformanceof pages 1-2, zhang2026mechanicalperformanceof pages 15-17, catana2024bicomponentadditivemanufacturing pages 6-7).


References

1. (zhang2026mechanicalperformanceof pages 1-2): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

2. (catana2024bicomponentadditivemanufacturing pages 6-7): M Catana, SN Mazurchevici, and C Cărăușu. Bicomponent additive manufacturing of polymers-a review. Unknown journal, 2024.

3. (US10953609B1 pages 96-97): Gregory Thomas Mark. Scanning print bed and part height in 3d printing. Patent (US), 2021.

4. (EP3221128B1 pages 29-30): Gregory Thomas Mark. Multilayer fiber reinforcement design for 3d printing. Patent (WO,EP,IL), 2021.

5. (zhang2026mechanicalperformanceof pages 6-8): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

6. (zhang2026mechanicalperformanceof pages 15-17): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

7. (favaro2026investigationofoctopus pages 24-29): A Favaro. Investigation of octopus arm tip behaviour for bio-inspired soft robotic arm control. Unknown journal, 2026.

8. (oz2025acomprehensiveexperimental pages 13-15): Özkan Öz and Fatih Huzeyfe Öztürk. A comprehensive experimental study of the potential use of 3d printable thermoplastic polymers as structural adhesives. The International Journal of Advanced Manufacturing Technology, 137:6073-6090, Apr 2025. URL: https://doi.org/10.1007/s00170-025-15532-9, doi:10.1007/s00170-025-15532-9. This article has 12 citations.

9. (oz2025acomprehensiveexperimental pages 15-16): Özkan Öz and Fatih Huzeyfe Öztürk. A comprehensive experimental study of the potential use of 3d printable thermoplastic polymers as structural adhesives. The International Journal of Advanced Manufacturing Technology, 137:6073-6090, Apr 2025. URL: https://doi.org/10.1007/s00170-025-15532-9, doi:10.1007/s00170-025-15532-9. This article has 12 citations.

10. (zhang2026mechanicalperformanceof pages 4-6): Chi Zhang, Yinchuan He, Kan Wang, Kwong Ming Tse, and Tingting Wang. Mechanical performance of bi-material fdm rigid–flexible joints: effects of alternate deposition and mechanical interlocking. The International Journal of Advanced Manufacturing Technology, Mar 2026. URL: https://doi.org/10.1007/s00170-026-17902-3, doi:10.1007/s00170-026-17902-3. This article has 0 citations.

11. (oz2025acomprehensiveexperimental pages 10-13): Özkan Öz and Fatih Huzeyfe Öztürk. A comprehensive experimental study of the potential use of 3d printable thermoplastic polymers as structural adhesives. The International Journal of Advanced Manufacturing Technology, 137:6073-6090, Apr 2025. URL: https://doi.org/10.1007/s00170-025-15532-9, doi:10.1007/s00170-025-15532-9. This article has 12 citations.

12. (favaro2026investigationofoctopus pages 59-64): A Favaro. Investigation of octopus arm tip behaviour for bio-inspired soft robotic arm control. Unknown journal, 2026.

13. (sholl2024highstretchtendondrivenfiberreinforced pages 8-9): Nick Sholl and Kamran Mohseni. High-stretch, tendon-driven, fiber-reinforced membrane soft actuators with multiple active degrees of freedom. Communications Engineering, Feb 2024. URL: https://doi.org/10.1038/s44172-023-00139-3, doi:10.1038/s44172-023-00139-3. This article has 10 citations and is from a peer-reviewed journal.