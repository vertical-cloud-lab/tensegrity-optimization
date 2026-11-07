Question: You are the second-pass synthesis reviewer. A previous ANALYSIS task
(c38a2046-a37b-497f-aebb-efc2f35004de) ran the same synthesis with only 3 of the
5 1-credit LITERATURE replies attached (A-anchor-bulb and B-dovetail had not yet
finished at submission time). All five Phase-1 LITERATURE outputs are now
attached (A, B, C, D, E - both .md and .json), along with the parallel
LITERATURE_HIGH prior-art survey (be6768ab) and the previous ANALYSIS reply.

Please re-do the synthesis with the FULL Phase-1 evidence. Specifically:

(1) Re-rank all five joints (manufacturability on Bambu H2D / drop-test
    performance under Lansmont M23 / fidelity to rigid-strut + ideal-tendon
    simulators / BO-search-space compatibility). State explicitly where the
    inclusion of the now-available A and B replies changes the previous
    ranking, and where it does not.

(2) For each design, list specific simulator-assumption violations and propose
    minimum-overhead corrections (ChLinkTSDA series compliance, Kelvin-Voigt
    at tendon endpoint, Coulomb deadband, etc.). Cross-check against the prior
    ANALYSIS recommendations and flag disagreements.

(3) Drop-test design-of-experiments - propose a screening matrix of <=12
    specimens that disambiguates the top-ranked designs under M23 envelope
    (5 000 g / 0.25 ms / 9.8 m/s / 36 kg) and the two regimes (`crutch_tip`
    75 kg/1.4 m/s/8 g HAVS, `nasa_lander` 5 kg/9.8 m/s/1500 g GEVS). Map each
    measurement (accelerometer peak g, QTec LDV velocity, post-test failure
    mode) to the joint physics it constrains.

(4) Concrete recommendation - pick ONE primary + ONE backup joint for the
    FIRST PETG+TPU multi-material H2D print. Provide exact `t3-prism.scad`
    geometry numbers, BambuStudio CLI flags (filament-map ordering, walls,
    infill, layer height, temps, retraction, IDEX `--filament-map-mode
    Manual --filament-map ...`), and what to inspect on print 1 (issue #37).

(5) Bibliographic gaps - which designs still need follow-up after consulting
    the full LITERATURE_HIGH (be6768ab) reply? Suggest specific keyword/author
    queries.


Answer:

Based on the full set of five Phase-1 1-credit LITERATURE replies and the `LITERATURE_HIGH` prior-art survey, here is the updated synthesis and design-for-test recommendation.

### 1. Updated Joint Ranking

The arrival of the complete A (anchor-bulb), B (dovetail), and the `LITERATURE_HIGH` survey significantly reshuffles the prior analysis ranking. The prior ranking was: E > A > B > C > D. **The new ranking is: B > A > E > C > D.**

The primary driver for the shift is the *extreme strength of published prior art for B* juxtaposed against the *lack of any published prior art for E*. The `LITERATURE_HIGH` survey reveals that Design E relies on an analogy to shell-core lattices (Yavas 2022) which only hit ~1.0–2.7 MPa interfacial shear, far below the 10–25 MPa assumed in the previous analysis. Design B, meanwhile, matches extensively published macroscopic T-shaped interlocks (Ermolai 2024, Zhang 2021, Frascio 2024) demonstrating 6–11 MPa tensile and up to 24 MPa shear strength.

| Rank | Design | Manufacturability (H2D) | Drop-Test Performance | Sim Fidelity | BO Compatibility | Prior Art / Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1 (up)** | **B: Dovetail/T-slot** | Moderate. Requires bridging a 4 mm PETG roof over a TPU captive cavity. Purge tower and wipe strictness are critical to avoid fusing. | **High.** Dovetail/T-shapes force failure away from interface slip into TPU bulk shear or cable rupture. Literature (Ermolai, Zhang) proves this geometry routinely achieves 6–11 MPa UTS. | Good. Introduces lumped joint compliance and rotation hysteresis. | Excellent. Slot depth, overlap width, and flank angle are continuous BO variables. | **Strong (#1).** Extensive multi-material FDM data proving interlock prevents sliding. |
| **2 (held)** | **A: Anchor-bulb** | Moderate. Requires an enlarged node (~8.5–9.0 mm OD) and oversized bores (~2.8–3.0 mm) to avoid TPU binding during passage. | **Moderate-High.** The geometric constraint cleanly limits failure to TPU cable rupture or bulb pull-through (bounded at ~54–110 N given a 2.4 mm 95A TPU cross-section). Pajunen 2019 spherical nodes show <0.2% residual strain per impact. | Excellent. Closest to an ideal "point-attachment" assumption, provided the node doesn't micro-rotate. | Excellent. Bulb OD and node geometry map cleanly to BO. | **Moderate (#4).** No exact TPU-bulb FDM analog, but strong validation for spherical tensegrity nodes. |
| **3 (down)** | **E: TPU rebar (barbed)** | High. Straight or barbed embedment along the Z-axis is easily printed with minimal support risk. | Moderate-High. If PETG ligaments are thick enough (>1.2 mm), barbs will force PETG shear-out (~280 N limit for 3 barbs) or TPU rupture. But straight embeds risk premature sliding at <1 MPa. | Good. Adds linear series compliance + Coulomb slip. | Excellent. Embed length and barb count/pitch are clean BO variables. | **Weak (#5).** No direct PETG/TPU barb paper found. Shell-core analogs show very weak (1-2.7 MPa) mode-II sliding resistance. |
| **4 (held)** | **C: TPU sleeve overmold** | High. Stacked rings over a knurl are simple to extrude. | Low. Pure friction/hoop-tension without a hard geometric undercut fails early via progressive slip under impact. | Poor. Distributes attachment over ~8 mm, acting like a progressive frictional damper. | Excellent. Knurl pitch/overlap map well to BO. | Moderate (#2). Analogous to multimaterial soft-core/rigid-shell honeycombs. |
| **5 (held)** | **D: Eyelet + loop** | Low. Highly sensitive to first-layer/bridging tolerances; needs 0.25–0.35 mm clearance per side to avoid fusing. | Low. PETG eyelet acts as a brittle notch (60–150 N limit); edge bearing pressure will abrade the TPU during redirection. | **Very Poor.** Introduces 2–3 mm deadband slack (zero force transmission) plus frictional hysteresis. | Moderate. Clearance maps to BO, but physics violations dominate. | Moderate (#3). Mortensen 2025 demonstrated similar PETG+TPU loop-on-pin joints. |

### 2. Simulator Assumption Violations & Corrections

| Design | Violations of rigid-strut / ideal-1D-tendon model | Minimum-overhead correction | Conflict vs Prior Analysis? |
| :--- | :--- | :--- | :--- |
| **B (Dovetail)** | Joint compliance and rotational friction (head scraping inside the slot). | Add rotational friction / joint damping at the attachment node. | Agrees. |
| **A (Anchor-bulb)** | Node rotation/micro-slip; TPU bulb axial stretch. | Add a lumped series spring `k_attach` representing the bulb + a node-level Coulomb friction term for redirection. | Agrees, but A literature explicitly sizes the bulb compliance to be negligible vs the full 100mm TPU cable length. |
| **E (TPU rebar)** | Progressive sliding and local embed shear deformation. | Kelvin-Voigt element (local shear compliance) in series with a Coulomb-like slip threshold (activated at pull-out force). | Agrees, but with a warning: E literature shows slip onset happens much earlier than prior analysis assumed due to weak bonding (~1-2.7 MPa mode-II limit). |
| **C (Sleeve)** | Massive progressive slip; distributes the attachment point over an 8 mm span. | Treat as a non-linear progressive frictional damper rather than a spring. | Agrees. |
| **D (Eyelet-loop)** | 2-3 mm deadband slack (delayed force transmission); severe frictional routing penalty. | Explicit deadzone element (0 force for ΔL < 2-3 mm) before the spring engages + Coulomb hysteresis for sliding. | Agrees. |

### 3. Drop-Test Design-of-Experiments (Screening Matrix)

Given the Lansmont M23 envelope (5000 g, 0.25 ms, 9.8 m/s, 36 kg) and the two target regimes (`crutch_tip`: 1.4 m/s / 8 g HAVS; `nasa_lander`: 9.8 m/s / 1500 g GEVS), here is a 12-specimen matrix optimized to disambiguate **B (dovetail)** and **A (anchor-bulb)**, which now outrank E.

We use a 30 kg surrogate for the 75 kg `crutch_tip` user to remain strictly under the Lansmont M23's 36 kg payload limit.

| Specimen | Design | Test Article | Regime | Objective & Measurement Mapping |
| :--- | :--- | :--- | :--- | :--- |
| **1–3** | **B (dovetail)** | Node coupon (strut-tip with single captive head) | `crutch_tip` (1.4 m/s, 30 kg surrogate) | **Monotonic static pull (Instron) to failure.** Validates if TPU head shears before pulling free. Establishes the static threshold for the Coulomb slip model in MuJoCo. |
| **4–6** | **A (anchor-bulb)** | Node coupon (sphere with single cable bore/bulb) | `crutch_tip` (1.4 m/s, 30 kg surrogate) | **Static pull + 8 g half-sine drop.** LDV on the bulb face. Disambiguates whether the 8 g pulse causes the bulb to extrude through the 2.8 mm bore vs cable rupture. |
| **7–9** | **B (dovetail)** | Full T3-prism tensegrity | `nasa_lander` (9.8 m/s, 5 kg payload) | **High-speed dynamic impact.** Accel on payload measures peak g vs GEVS limit. QTec LDV measures relative node velocities to calculate Specific Energy Absorbed (SEA). Post-test inspection identifies if T-head cheeks sheared off. |
| **10–12** | **A (anchor-bulb)** | Full T3-prism tensegrity | `nasa_lander` (9.8 m/s, 5 kg payload) | **High-speed dynamic impact.** Peak g and SEA comparison against B. Monitor Pajunen-style cumulative residual strain (node tracking) across repeated drops to check for bearing-edge TPU cutting. |

### 4. Concrete Recommendation for First H2D Print

**Primary Joint:** B (Co-printed Dovetail / T-Slot). *Selected because it has the strongest peer-reviewed evidence (Ermolai 2024, Zhang 2021) for actually achieving mechanical lock in FDM rigid/soft pairings.*
**Backup Joint:** A (Anchor-bulb).

**Geometry parameters for `t3-prism.scad` (Design B):**
*   **Slot mouth width:** 6.4 mm (in a 7 mm node envelope).
*   **TPU Internal head width (undercut):** 7.4 mm (provides 0.5 mm mechanical capture per side).
*   **Slot internal height:** 3.6 mm.
*   **Slot depth:** 5.0 mm along the strut axis.
*   **Dovetail flank angle:** 25° (to reduce stress concentration relative to a steep 90° T-head).
*   **Running clearance:** 0.25 mm per side on non-load-bearing faces.

**BambuStudio CLI Flags & Process (`--filament-map`):**
*   **Filament mapping:** `--filament-map-mode Manual --filament-map 1 2` (Assuming PETG is slot 1, TPU 95A is slot 2).
*   **Layer height:** 0.16 mm (`layer_height=0.16`). This helps the 4 mm PETG roof closure over the TPU head.
*   **Line width:** 0.42 mm.
*   **Walls:** 5 perimeters (`wall_loops=5`). Density at the node must come from walls, not sparse infill, to resist cheek splitting.
*   **Infill:** 100% locally at the nodes (modifier mesh) / 80-90% bulk.
*   **Temperatures:** PETG at 250 °C (bed 80 °C); TPU at 225 °C.
*   **Print order:** TPU head first, PETG roof second per layer (forces the "receptacle" to close over the anchor).
*   **Issue #37 First-print inspection:** Examine the PETG roof bridge span for droop. Ensure the 0.25 mm clearance gap didn't fuse due to stringing. Manually verify the joint has rotational freedom before tensioning.

### 5. Bibliographic Gaps

With the return of the `LITERATURE_HIGH` prior-art survey, the bibliographic gap regarding Design A's "Mark patents" and rigid-flexible FDM benchmarks has been filled.

However, the survey highlighted one critical remaining gap: **there is virtually zero published dynamic/impact data on multi-material FDM rigid–flexible joints at the component/joint level.** Almost all cited literature (Ermolai, Zhang, Yavas) only performed quasi-static tensile tests. The exception was Pajunen 2019, but their drop-tests were on *single-material* SLS PA2200 nodes. Therefore, our planned Lansmont M23 campaign is venturing into an area with no direct benchmarking literature to bound expected dynamic pull-out strength or hysteresis. Future literature searches should specifically target "high strain rate testing of multi-material FDM interfaces" or "Kolsky bar testing TPU-PETG".

---
### Discretionary Analytical Decisions
*   **Primary Design Selection:** Selected Design B over Design E (the previous analyzer's choice). This was driven by prioritizing the strength of published quantitative evidence (multiple papers validating 6-24 MPa strengths for B's geometry) over the theoretical simplicity of E (which had zero direct literature validation and weak performance in adjacent shell-core analogs).
*   **Clearance Parameterization:** Assigned a 0.25 mm clearance for Design B's non-load-bearing faces rather than a zero-gap fit. This choice assumes standard 0.4 mm nozzle FDM dimensional overshoot would inadvertently fuse the joint if modeled line-to-line, prioritizing mechanical articulation over maximum theoretical packing density.
*   **DOE Structuring:** Retained the 30 kg surrogate mass from the previous analyzer for the 75 kg `crutch_tip` regime to ensure compliance with the Lansmont M23's 36 kg strict payload limit. Allocated half the test matrix to static isolated node tests before full dynamic drops to properly calibrate the MuJoCo static/kinetic slip thresholds identified in step 2.
*   **Simulation Model Patch:** Chose to model Design D's slack as a pure deadzone rather than a highly non-linear softening spring, and Design B's friction as Coulomb rather than purely viscous, to align with standard MuJoCo `<spatial>` and `<joint>` primitives with minimal overhead.
