Question: ## Joint design idea: Captive TPU loop threaded through a printed PETG eyelet (chain-link, topological constraint only)

The PETG strut terminates in a closed eyelet ring (~5 mm outer Ø, 2.4 mm
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


## Critical feedback on the proposed PETG eyelet + captive TPU loop joint

### Summary (what you gain / what you pay)
The chain-link/topological constraint is a strong idea specifically for PETG–TPU on FDM because it eliminates reliance on inter-material adhesion and turns the interface problem into a **purely geometric tolerance + wear** problem. The main trade-offs are (i) **print-in-place tolerance sensitivity** (risk of fusing), (ii) **deadband/slack** that can dominate dynamics, and (iii) **frictional redirection + abrasion** at the eyelet contact arc, which is a known issue with “smooth eyelet” cable routing in tensegrity mechanisms. (friesen2018atensegrityinspiredcompliant pages 3-5)


## (1) Manufacturability on H2D IDEX, 0.4 mm nozzle, no soluble support

### Feasibility: yes, but only with geometry changes and explicit tolerance management
A print-in-place interlinked PETG eyelet and TPU closed loop is manufacturable on a 0.4 mm nozzle **if** you treat it like a print-in-place mechanism: you must design for over-extrusion, first-layer distortion, and stringing, and include chamfers/tapers/clearance features that compensate those artifacts. The interlocking-mechanism literature emphasizes manufacturing-driven geometry (chamfers/tapers to avoid unintended contact and to compensate over-extrusion and first-layer effects) and shows that printed artifacts can strongly affect engagement behavior. (gloyer2023extrusionbasedadditivemanufacturingdriven pages 5-6, gloyer2023extrusionbasedadditivemanufacturingdriven pages 3-5, gloyer2023extrusionbasedadditivemanufacturingdriven pages 9-11)

### The key manufacturability risks for your specific dimensions
- **Your current eyelet ID (2.4 mm) equals the TPU cable diameter (2.4 mm).** If you literally keep those equal, the linkage cannot move freely after printing; it will fuse or bind from normal FFF dimensional error and TPU swelling. 
- **Unsupported circular bores**: if the eyelet hole axis is horizontal, the “ceiling” of the eyelet is a bridge. With no soluble support, the sagging/elephant-foot closure will reduce functional clearance and is likely to fuse the loop.

### Practical print-in-place rules for this design
- **Clearance**: start with **0.25–0.35 mm radial clearance per side** between TPU and PETG wherever they pass; add **0.4–0.6 mm Z clearance** where one material prints over/near the other.
- **Orientation**: orient the eyelet so the hole is printed **vertically** (stacked perimeters), or redesign the hole as a **teardrop/diamond** if you must print it as a span.
- **Anti-fuse features**: use **chamfers/tapers** at the eyelet entry/exit and consider a sacrificial “anti-string shield” where you can manually break it free during post-print “break-in.” Printing studies of interlocks add such geometric features specifically to avoid unintended contact and wear. (gloyer2023extrusionbasedadditivemanufacturingdriven pages 5-6, gloyer2023extrusionbasedadditivemanufacturingdriven pages 3-5)


## (2) Likely failure modes under single-impact drop testing (with rough bounds)
Because the loop is topologically captive, classical “pull-out” is not the governing mode; instead, you should expect **material failure at stress concentrators and contact/wear damage**.

### Dominant failure modes
1. **PETG eyelet cracking at the strut/eyelet root** (brittle notch-driven failure)
   - Your proposed ring (OD 5 mm, ID 2.4 mm) has net polymer area of ~7.4 mm². Using a realistic FFF PETG tensile strength order **25–40 MPa** (direction-dependent), a crude static section capacity is ~**180–300 N** before stress concentration. Under impact and notch effects (Kt ~2–3), a prudent single-hit design load per eyelet is closer to **~60–150 N** unless you thicken and fillet aggressively.
   - Tensegrity joint surveys note small-scale detailing challenges and that many traditional joints rely on more massive hardware and explicit cable management to avoid sliding/misrouting; scaling down tends to make joints more fragile. (bernaards2014developmentofa pages 34-40, bernaards2014developmentofa pages 40-44)

2. **TPU loop cut-through / tearing at the PETG edge (bearing pressure failure)**
   - For a 2.4 mm diameter TPU strand, area ~4.5 mm². If effective FFF TPU tensile strength is ~15–25 MPa, gross tensile break is ~**70–110 N**. However, local edge contact typically reduces usable impact load (stress concentration + abrasion), so a practical bound is **~30–70 N** unless you use generous PETG edge radii.
   - Eyelet routing friction is a known problem: Friesen et al. explicitly call **smooth eyelets “common but inadequate”** because friction causes hysteresis, reduces efficiency, and can cause unacceptable cable wear; they instead redirect load through a bearing-mounted pulley to eliminate most exit friction. (friesen2018atensegrityinspiredcompliant pages 3-5)

3. **Wear/hysteresis-driven performance drift (even if nothing “breaks” on the first drop)**
   - Expect frictional dissipation and abrasion at the contact arc, especially because your design allows angular change at the link. Friesen et al. highlight that friction at cable exits produces hysteresis and wear. (friesen2018atensegrityinspiredcompliant pages 3-5)

4. **Creep / prestress loss in TPU (longer-term, but can show quickly if highly prestrained)**
   - Tensegrity practice at larger scales often abandoned elastic/slipping tension elements because of slip/elasticity issues; e.g., Renner reports guy lines slipping under high tension and inadequate elasticity, leading to selection of steel cables. (renner2024tensegrityflaxseatexploring pages 10-12, rennerUnknownyeartensegrityflaxseat pages 10-13)

### Quantitative sanity check against a known printed interlock force scale
As a reference point for what small printed interlocking features can reliably hold, Gloyer et al. measured an average maximum holding force of about **10 N** (recommended conservative **8.5 N**) for a representative printed TPU snap-interlock element, with variability driven by print artifacts and alignment. (gloyer2023extrusionbasedadditivemanufacturingdriven pages 9-11)
Your chain-link concept is not a snap-fit, but this provides an “order of magnitude” caution: if you design any small printed retention features (anti-unthreading bumps, etc.), they may fail at **single-digit to tens of newtons** unless substantially scaled up.


## (3) Preservation of the “rigid struts + ideal massless tendons” assumption

### The deadband is the biggest modeling violation
You already identified **~2–3 mm of free play** before the TPU becomes tensile-loaded; this creates a **deadzone** in the tendon force–extension relationship. That deadzone will:
- delay force transmission during impact,
- increase peak acceleration when the slack is suddenly taken up,
- alter modal frequencies and damping.

### Additional non-idealities: friction + joint compliance + hysteresis
- **Friction/hysteresis** at the eyelet is expected; Friesen et al. explain that friction at the cable exit creates hysteresis in force measurement and reduces efficiency, and causes wear—exactly the kind of non-ideality an “ideal tendon” omits. (friesen2018atensegrityinspiredcompliant pages 3-5)
- Even after slack is removed, the loop behaves like a **compliant termination** (bending + local flattening around the eyelet), which adds series compliance compared with an ideal point-attachment.
- Real tensegrity cable systems often show an initial low-stiffness region compared with models; Zappetti notes that in the “stiff” cable state there was still **lower stiffness in the initial part of the load curve**, potentially explaining experiment–simulation mismatch. (zappetti2021variablestiffnesstensegritymodular pages 87-90)

### Recommended simulation patch (minimal but effective)
Model each cable as:
- **Deadzone**: 0 force for ΔL < δ (use δ ≈ 1.5 mm nominal; sweep 0.5–3 mm).
- Then **Kelvin–Voigt** (spring + damper) in series with the cable to capture termination compliance.
- Add a node-level **Coulomb friction** term for redirection hysteresis (treat as a first-order dissipation element).


## (4) Closest cited prior art (what they did / concluded)

1. **Cable attachment via rings/loops and cable-management slots in tensegrity joints**
   - Bernaards’ tensegrity joint development survey describes historic solutions including **cables connected to rings with a loop (washers)** and the use of **slots to orient cables and prevent lateral sliding**; it also notes scale/detailing issues and that much joint design knowledge sits in patents. (bernaards2014developmentofa pages 34-40, bernaards2014developmentofa pages 40-44, bernaards2014developmentofa pages 26-34)

2. **Tensegrity cable termination/attachment using eyelets, plus real-world issues with slip/elasticity**
   - Renner et al. document multiple attempted tension-member/attachment solutions and observed that some cable systems **slipped under high tension** and that elasticity could be inappropriate; final systems used steel cables and eyelet-based hardware and emphasized individual cable tension adjustment. (renner2024tensegrityflaxseatexploring pages 10-12, rennerUnknownyeartensegrityflaxseat pages 10-13)

3. **Eyelets as inadequate cable exits due to friction, hysteresis, and wear (and a better alternative)**
   - Friesen et al. state that **smooth eyelets are common but inadequate** because friction causes hysteresis, inefficiency, and unacceptable wear; they implement a **bearing-mounted pulley routing** that passively aligns to the cable direction and eliminates most exit friction. (friesen2018atensegrityinspiredcompliant pages 3-5)

4. **Printed interlocking mechanisms: tolerance sensitivity and force scale**
   - Gloyer et al. characterize an FFF-printed TPU snap interlock: its force–displacement curve has elastic, sliding/friction, and disengagement phases; the average maximum holding force is ~10 N and they recommend 8.5 N conservatively, and note sensitivity to print artifacts and alignment. (gloyer2023extrusionbasedadditivemanufacturingdriven pages 9-11)

These references do not exactly match a *topological catenane-style* PETG/TPU chain-link termination, but together they bound the two core phenomena your design relies on: (i) ring/loop tensegrity attachments, and (ii) print-in-place interlock tolerance sensitivity and friction/wear behavior.


## (5) Concrete numerical recommendations (geometry + slicer + process)

A compact “first-pass” design/print checklist is provided here:
| Topic | What to check / likely issue | Rough quantitative bound / first-pass recommendation | Why it matters | Evidence |
|---|---|---|---|---|
| Manufacturability: clearance | Print-in-place PETG eyelet and TPU closed loop need enough free gap to avoid welding/string-bridging, but not so much that slack becomes excessive | Start with **0.25-0.35 mm radial clearance per side** between TPU loop and PETG eyelet everywhere; **0.4-0.6 mm axial/Z clearance** where one material passes over the other; target total unloaded free play **<=1.0-1.5 mm at the link**, else system slack grows to multi-mm at the cable level | FFF variation, TPU swelling, and PETG over-extrusion can easily fuse tighter fits; too-large gaps create deadband before tensile load develops | Printed interlocks are highly sensitive to fit, over-extrusion, and alignment; chamfers/tapers were added specifically to compensate printing artifacts, and measured holding behavior varied with print defects (gloyer2023extrusionbasedadditivemanufacturingdriven pages 5-6, gloyer2023extrusionbasedadditivemanufacturingdriven pages 9-11, gloyer2023extrusionbasedadditivemanufacturingdriven pages 3-5) |
| Manufacturability: orientation | A horizontal eyelet bore without soluble support is risky; orient eyelet so the hole is built vertically or as a teardrop/diamond opening rather than a flat circular bridge | Prefer **eyelet plane vertical** so the eyelet hole prints as stacked perimeters; if horizontal hole is unavoidable, convert ID to **teardrop with 45-60 deg crown**; avoid unsupported bridges longer than about **1.5-2.0 mm** inside the captive region | Greatly reduces sag, elephant-foot closure, and accidental TPU/PETG contact inside the ring | FFF interlocks require manufacturing-driven geometry, compensation for over-extrusion, and careful printability constraints rather than nominal CAD alone (gloyer2023extrusionbasedadditivemanufacturingdriven pages 5-6, gloyer2023extrusionbasedadditivemanufacturingdriven pages 3-5, gloyer2023extrusionbasedadditivemanufacturingdriven pages 1-3) |
| Manufacturability: sacrificial anti-fuse features | The loop may snag on wisps or tiny accidental necks between materials during print | Add **0.15-0.20 mm sacrificial break tabs** or **single-line anti-string shields** at one noncritical location; chamfer PETG eyelet entry/exit **0.3-0.5 mm at 45 deg** | Lets the assembly survive print-in-place while still freeing after a quick manual break-in | Print artifacts and grooves materially changed the force-displacement response of printed interlocks; intentional tolerance-management features improved reliability (gloyer2023extrusionbasedadditivemanufacturingdriven pages 9-11, gloyer2023extrusionbasedadditivemanufacturingdriven pages 3-5) |
| Failure mode: PETG eyelet fracture | Eyelet root can crack at the strut interface under impulsive load, especially if layer lines run across the ligament | With your proposed **OD 5.0 / ID 2.4 mm**, net ring section is about **7.4 mm^2**; using PETG tensile strength **~25-40 MPa across realistic FFF directions** gives a crude static section capacity **~180-300 N** before stress concentration; with impact + notch factor **Kt ~2-3**, prudent single-hit design load is only **~60-150 N per eyelet** unless geometry is thickened | This is the most likely brittle failure if the TPU survives and the load localizes at one eyelet edge | Tensegrity joints routinely rely on rings/loops and slots, but small-scale detailing is challenging; strong post-assembly adjustment hardware is typically needed, and a prototype joint with improved metal inserts reached 87 kg working load only after substantial redesign (bernaards2014developmentofa pages 34-40, bernaards2014developmentofa pages 40-44, bernaards2014developmentofa pages 103-107) |
| Failure mode: TPU loop tear / cut-through | TPU 95A loop may not pull out topologically, but it can neck, creep, or be cut by PETG edge pressure | For **2.4 mm dia TPU**, area is **~4.5 mm^2**; if effective FFF tensile strength is **~15-25 MPa**, gross break load is roughly **70-110 N**, but local edge contact and dynamic stress concentration can reduce usable impact load to **~30-70 N**; use PETG edge radius **>=0.5 mm** and preferably **0.8 mm** where possible | In practice, local bearing/cutting usually limits before gross TPU tensile failure | Smooth eyelets were found inadequate in cable exits because friction and wear cause hysteresis, inefficiency, and unacceptable cable wear; low-friction redirection was preferred over simple eyelets (friesen2018atensegrityinspiredcompliant pages 3-5) |
| Failure mode: creep / permanent set | Closed TPU loop under sustained pretension or repeated impact can lengthen, increasing slack over time | Expect stress-relaxation and set to become noticeable above roughly **5-8% engineering strain** held for hours; for first tests, keep assembled pretension such that average cable strain stays **<=3-5%** and impact strain peaks **<=10-15%** | If the loop creeps, the tensegrity loses prestress and the simulation/model mismatch worsens every cycle | Prior tensegrity work reported that elastic/slipping cable solutions were unacceptable under high tension; stiffer, lower-creep cable systems were selected instead (rennerUnknownyeartensegrityflaxseat pages 10-13, renner2024tensegrityflaxseatexploring pages 10-12) |
| Failure mode: wear / hysteresis | Sliding TPU around PETG eyelet during impact introduces frictional losses and abrasion, especially with changing cable angle | Treat the joint as a frictional redirection point with effective **mu ~0.2-0.4** as a first model bound for dry TPU-on-PETG; inspect after the first **10-100 drop cycles** for whitening, burrs, or diameter loss at the contact arc | Repeated energy loss and wear will change both damping and cable length | Eyelets were explicitly called inadequate for cable routing because friction causes hysteresis and wear; printed interlocks also showed distinct sliding/friction phases and sensitivity to surface imperfections (friesen2018atensegrityinspiredcompliant pages 3-5, gloyer2023extrusionbasedadditivemanufacturingdriven pages 9-11) |
| Modeling implication: deadband | The topological link adds slack before the cable behaves like an ideal tendon | Replace each tendon with a **deadzone element**: zero/low force over **1-3 mm** extension, then linear or slightly nonlinear stiffness; for first simulation pass use deadband **1.5 mm nominal**, sweep **0.5-3.0 mm** | The deadband is the biggest violation of the ideal massless taut-tendon assumption | Prior tensegrity hardware shows real joints/cables introduce nonideal initial compliance and discrepancies with simulation, especially in the initial part of the load curve (zappetti2021variablestiffnesstensegritymodular pages 87-90, friesen2018atensegrityinspiredcompliant pages 3-5) |
| Modeling implication: added compliance | Even after slack is removed, the loop bends around the eyelet and acts like a short compliant termination | Add a **Kelvin-Voigt series element** at each node: extra compliance equivalent to about **0.5-2.0 mm** of additional TPU cable length, with damping tuned to match LDV ring-down; if cable axial stiffness is **k_c**, use joint stiffness first-pass **~2-10 k_c** rather than infinite | Prevents overprediction of natural frequency and peak transmitted acceleration | Low-friction routing and explicit series compliance were used in tensegrity-inspired joints specifically because routing and sensing compliance strongly affect behavior (friesen2018atensegrityinspiredcompliant pages 3-5) |
| Geometry: PETG eyelet | Current **5.0 OD / 2.4 ID / 1.3 wall** is printable but marginal for impact unless the root is strongly filleted | First pass: **OD 5.5-6.5 mm**, **ID 3.0-3.4 mm**, minimum ligament/root thickness **1.6-2.0 mm**, root fillet into 6 mm strut **>=1.2 mm**, contact edge radius **>=0.5 mm** | Slight upsizing buys much more root strength and larger printable clearances than keeping the very tight 2.4 mm bore | Small-scale tensegrity joints need finer detailing and tolerance management; ring/loop solutions exist but are scale-sensitive (bernaards2014developmentofa pages 34-40, bernaards2014developmentofa pages 40-44) |
| Geometry: TPU closed loop | Circular 2.4 mm section is workable, but a slightly flattened oval often prints more repeatably and wears less | First pass loop outside size **12-15 mm major axis, 6-8 mm minor axis**; section **2.2-2.6 mm wide x 1.8-2.2 mm thick** oval rather than perfectly round; keep local bend radius **>=1.2 mm** | Improves in-plane print stability and reduces sharp-strain zones at the link apex | Tensegrity practice favors looped cable terminations but warns about flexibility requirements at sharp bends; too-stiff or too-compliant tension members both caused problems (bernaards2014developmentofa pages 34-40, rennerUnknownyeartensegrityflaxseat pages 10-13, renner2024tensegrityflaxseatexploring pages 10-12) |
| Slicer: PETG | Need strong ring perimeters and tough root, not cosmetic speed | **0.16-0.20 mm layer height**, **5-6 walls**, **100% infill in node/eyelet region** or modifier mesh, **240-255 C nozzle**, **70-80 C bed**, fan **20-40%**, outer wall speed **25-35 mm/s** | Maximizes eyelet hoop continuity and reduces brittle root failure | Manufacturing-driven design and tight parameter control are important for consistent interlocking behavior (gloyer2023extrusionbasedadditivemanufacturingdriven pages 5-6, gloyer2023extrusionbasedadditivemanufacturingdriven pages 1-3) |
| Slicer: TPU 95A | TPU must print dimensionally stable enough to stay free inside the eyelet | **0.20 mm layer height**, **3-4 walls**, **100% infill** for the loop section, **220-235 C nozzle**, **35-50 C bed**, fan **30-60%**, speed **15-25 mm/s**, minimal retraction (**<=1 mm**) | Dimensional overshoot in TPU is a primary cause of fused captive joints | TPU interlocking features were chosen specifically for compliance/tolerance, but their performance remained sensitive to printing artifacts and settings (gloyer2023extrusionbasedadditivemanufacturingdriven pages 5-6, gloyer2023extrusionbasedadditivemanufacturingdriven pages 9-11) |
| IDEX sequencing / path strategy | Cross-contamination and parked-nozzle ooze can fuse the captive link late in the print | Print **all PETG for a layer first, then TPU**, with purge/wipe before TPU enters the captive region; place seam away from contact arc; disable ironing in joint region; if available, use object-specific slow-down near the node | Prevents PETG blobs or TPU strings from welding the linkage shut | Interlocking printed mechanisms showed significant variability from printer/batch/alignment artifacts, so sequencing and parameter discipline matter (gloyer2023extrusionbasedadditivemanufacturingdriven pages 9-11, gloyer2023extrusionbasedadditivemanufacturingdriven pages 1-3) |


*Table: This table summarizes manufacturability, failure risks, simulation implications, and first-pass geometry/slicer settings for a print-in-place PETG eyelet with a captive TPU loop. It is designed as a compact reference for deciding whether to prototype the concept on a 0.4 mm nozzle H2D and how to model its nonideal behavior.*

### Key geometry adjustments (strongly recommended)
- **Do not keep PETG eyelet ID = TPU diameter.** Increase eyelet ID to **3.0–3.4 mm** and/or reduce TPU loop local thickness at the link.
- Increase eyelet OD to **5.5–6.5 mm** and add a **root fillet ≥1.2 mm** into the strut to reduce notch-driven PETG cracking.
- Add a **contact edge radius ≥0.5 mm (preferably ~0.8 mm)** to mitigate TPU cut-through.

### Key slicer/process settings (first prototype)
- PETG: **0.16–0.20 mm layer height; 5–6 walls; 100% infill modifier in node/eyelet; slow outer walls (25–35 mm/s)**.
- TPU 95A: **0.20 mm layer height; 3–4 walls; 100% infill in loop; 15–25 mm/s; minimal retraction**.
- IDEX: print **PETG first then TPU per layer**, with aggressive purge/wipe before entering the captive region to avoid late-stage blobs welding the link.


## Bottom-line recommendation
Prototype this joint, but treat it as a **print-in-place mechanism** rather than a “cable through a hole” feature: upsize the eyelet ID and OD, aggressively fillet and round edges, and include clearance/tolerance compensation. Expect the joint to introduce a large, non-negligible **deadband + frictional hysteresis** relative to your current “ideal tendon” simulation; if you proceed, update the simulation with a deadzone + series compliance/friction model so that drop-test/LDV data can be reconciled to models. (friesen2018atensegrityinspiredcompliant pages 3-5, gloyer2023extrusionbasedadditivemanufacturingdriven pages 9-11, bernaards2014developmentofa pages 34-40)

References

1. (friesen2018atensegrityinspiredcompliant pages 3-5): Jeffrey M. Friesen, John L. Dean, Thomas Bewley, and Vytas Sunspiral. A tensegrity-inspired compliant 3-dof compliant joint. 2018 IEEE International Conference on Robotics and Automation (ICRA), pages 1-9, May 2018. URL: https://doi.org/10.1109/icra.2018.8460593, doi:10.1109/icra.2018.8460593. This article has 38 citations.

2. (gloyer2023extrusionbasedadditivemanufacturingdriven pages 5-6): Philip Gloyer, Lucca Nikita Schek, Hans Lennart Flöttmann, Paul Wüst, and Christina Völlmecke. Extrusion-based additive manufacturing-driven design and testing of the snapping interlocking metasurface mechanism shroomlock. Inventions, 8:137, Oct 2023. URL: https://doi.org/10.20944/preprints202310.0712.v1, doi:10.20944/preprints202310.0712.v1. This article has 9 citations.

3. (gloyer2023extrusionbasedadditivemanufacturingdriven pages 3-5): Philip Gloyer, Lucca Nikita Schek, Hans Lennart Flöttmann, Paul Wüst, and Christina Völlmecke. Extrusion-based additive manufacturing-driven design and testing of the snapping interlocking metasurface mechanism shroomlock. Inventions, 8:137, Oct 2023. URL: https://doi.org/10.20944/preprints202310.0712.v1, doi:10.20944/preprints202310.0712.v1. This article has 9 citations.

4. (gloyer2023extrusionbasedadditivemanufacturingdriven pages 9-11): Philip Gloyer, Lucca Nikita Schek, Hans Lennart Flöttmann, Paul Wüst, and Christina Völlmecke. Extrusion-based additive manufacturing-driven design and testing of the snapping interlocking metasurface mechanism shroomlock. Inventions, 8:137, Oct 2023. URL: https://doi.org/10.20944/preprints202310.0712.v1, doi:10.20944/preprints202310.0712.v1. This article has 9 citations.

5. (bernaards2014developmentofa pages 34-40): X Bernaards, IPMP Teuffel, and IADCA Pronk. Development of a tensegrity joint. Unknown journal, 2014.

6. (bernaards2014developmentofa pages 40-44): X Bernaards, IPMP Teuffel, and IADCA Pronk. Development of a tensegrity joint. Unknown journal, 2014.

7. (renner2024tensegrityflaxseatexploring pages 10-12): Markus Renner, Evgenia Spyridonos, and Hanaa Dahy. Tensegrity flaxseat: exploring the application of unidirectional natural fiber biocomposite profiles in a tensegrity configuration as a concept for architectural applications. Buildings, 14:2490, Aug 2024. URL: https://doi.org/10.3390/buildings14082490, doi:10.3390/buildings14082490. This article has 5 citations.

8. (rennerUnknownyeartensegrityflaxseat pages 10-13): M Renner, E Spyridonos, and H Dahy. Tensegrity flaxseat. Unknown journal, Unknown year.

9. (zappetti2021variablestiffnesstensegritymodular pages 87-90): Davide Zappetti. Variable-stiffness tensegrity modular robots. ArXiv, Jan 2021. URL: https://doi.org/10.5075/epfl-thesis-8083, doi:10.5075/epfl-thesis-8083. This article has 5 citations.

10. (bernaards2014developmentofa pages 26-34): X Bernaards, IPMP Teuffel, and IADCA Pronk. Development of a tensegrity joint. Unknown journal, 2014.

11. (gloyer2023extrusionbasedadditivemanufacturingdriven pages 1-3): Philip Gloyer, Lucca Nikita Schek, Hans Lennart Flöttmann, Paul Wüst, and Christina Völlmecke. Extrusion-based additive manufacturing-driven design and testing of the snapping interlocking metasurface mechanism shroomlock. Inventions, 8:137, Oct 2023. URL: https://doi.org/10.20944/preprints202310.0712.v1, doi:10.20944/preprints202310.0712.v1. This article has 9 citations.

12. (bernaards2014developmentofa pages 103-107): X Bernaards, IPMP Teuffel, and IADCA Pronk. Development of a tensegrity joint. Unknown journal, 2014.