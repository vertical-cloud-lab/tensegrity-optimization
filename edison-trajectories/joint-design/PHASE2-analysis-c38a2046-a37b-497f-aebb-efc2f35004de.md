Question: You are reviewing five candidate joint designs for connecting TPU 95A cables
(2.4 mm Ø) to PETG struts (6 mm Ø) in a 3D-printed (Bambu Lab H2D IDEX FDM,
0.4 mm nozzle) tensegrity-like assembly (T3-prism today, n-bar prisms +
icosahedra later). The five designs and their full feedback from a parallel
batch of five 1-credit Edison LITERATURE queries are attached:

  (A-anchor-bulb) NOT YET COMPLETE — Edison task_id=0b5d7ba2-847e-47b3-bddf-127e2ed170d3 (please fetch from platform if you can)
  (B-dovetail) NOT YET COMPLETE — Edison task_id=ccb7b854-718c-4ac4-bf15-61c1fe522c7d (please fetch from platform if you can)
  (C-tpu-sleeve-overmold) ATTACHED as C-tpu-sleeve-overmold-5a7ffce4-a8a0-49d6-9b43-3d0ea38d23f9.md (Edison task 5a7ffce4-a8a0-49d6-9b43-3d0ea38d23f9)
  (D-eyelet-loop) ATTACHED as D-eyelet-loop-727a449d-d2af-4540-acfa-9b964f98689f.md (Edison task 727a449d-d2af-4540-acfa-9b964f98689f)
  (E-tpu-rebar) ATTACHED as E-tpu-rebar-ae373eb5-90e3-4543-b354-9e9990d76042.md (Edison task ae373eb5-90e3-4543-b354-9e9990d76042)

Plus repo context already attached: proposal.pdf, MRG_2026.pdf, the t3-prism
CAD README + scad source + iso PNG (the present single-piece pure-PETG print),
the prior TPU+PETG variables literature search, the Lansmont M23 drop-tower
specs, and the simulations README (MuJoCo / PyBullet / PyChrono — currently
all rigid-strut + ideal-massless-1D-tendon).

Please synthesize the five 1-credit replies into ONE coherent design-for-test
recommendation. Specifically:

(1) **Ranking** — rank the five joints on (a) manufacturability on the H2D
    today, (b) expected mechanical performance under the Lansmont M23 drop
    envelope (peak g, SEA, repeatability), (c) fidelity to the rigid-strut /
    ideal-tendon simulator assumptions, and (d) compatibility with our planned
    BO design variables (issue #23 / PR #24).

(2) **Assumption violations** — for each design, list the specific simulator
    assumptions it violates and, where possible, propose a minimum-overhead
    correction (e.g. lumped joint compliance ChLinkTSDA element, distributed
    spring at tendon endpoint, or a measurement to clamp the gap).

(3) **Drop-test design-of-experiments** — given Lansmont M23 limits (5,000 g,
    0.25 ms half-sine, 9.8 m/s ΔV, 36 kg payload) and the two regimes encoded
    in `simulations/regimes.py` (`crutch_tip` 75 kg/1.4 m/s/8 g HAVS;
    `nasa_lander` 5 kg/9.8 m/s/1500 g GEVS), propose a minimal screening
    matrix (≤ 12 specimens) that disambiguates the top-ranked designs. State
    how each measurement (peak g via accelerometer, surface velocity via QTec
    LDV, post-test failure mode) maps to the joint physics.

(4) **Concrete recommendation** — pick ONE primary joint design + ONE backup
    for the first PETG+TPU multi-material print on the H2D. Give us the
    geometry numbers we need to update `cad/t3-prism/t3-prism.scad`, the
    BambuStudio CLI flags (filament-map ordering, walls, infill, layer
    height, temps, retraction), and what to look for on the first print
    after the H2D PETG+TPU IDEX setup is dialed in (issue #37).

(5) **Bibliographic gap** — flag any design whose 1-credit reply was thin /
    speculative / poorly cited so we know which to follow up on after the
    parallel LITERATURE_HIGH query (`task_id=be6768ab-a4ca-433b-8bec-059819e3e368`) returns.


Answer:

I have synthesized the five Edison task replies against the Lansmont M23 and PyBullet/MuJoCo simulator constraints. The full fetched literature replies for A (partial but complete text) and B (completed) have been saved to your workspace as `A-anchor-bulb-fetched.md` and `B-dovetail-fetched.md`.

### (1) Ranking

Based on the evidence from multi-material FDM (specifically studies characterizing PLA/PETG rigid phases against TPU/silicone flexible phases), positive mechanical interlocking heavily outperforms frictional or chemical bonding.

| Rank | Design | Manufacturability (H2D) | Drop-Test Performance | Sim Fidelity | BO Compatibility |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **E: TPU rebar (barbed)** | High. Straight embed is easiest; undercuts/barbs add complexity but avoid bridging over soft gaps. | High. Predicted pull-out 250–700 N. Forces failure away from interface slip toward TPU bulk or PETG bulk. | Good. Adds linear series compliance + non-linear Coulomb slip. | Excellent. Embed length, barb count, and pitch are clean integer/continuous BO variables. |
| **2** | **A: Anchor-bulb** | Moderate. Requires enlarged node (~9 mm), wider bores (~3 mm), and strict seam/purge control to print a 2.4 mm cable freely. | Moderate-High. Replaces chemical bond with a purely geometric TPU failure limit (~50-60 N rupture limit). | Excellent. Closest to an ideal "point-attachment" assumption, if the hole doesn't micro-slip. | Excellent. Bulb OD and hole diameter map cleanly to BO search. |
| **3** | **B: Dovetail/T-slot** | Moderate. Print-in-place over a TPU cavity introduces PETG roof sag and ooze-fusion risks. | High. Similar geometries show ~18-24 MPa shear capacities and ~6-7 MPa tensile strength. | Good. Introduces lumped joint compliance and rotation hysteresis. | Excellent. Slot depth and flank angle map nicely to BO. |
| **4** | **C: TPU-sleeve overmold** | High. Very easy to print (stacked rings over a knurl). | Low. Pure friction/hoop-tension fails early via progressive slip/pull-out under shock and TPU relaxation. | Poor. Distributes the "attachment" over an 8 mm span and acts like a progressive frictional damper. | Excellent. Knurl pitch and overlap length map well to BO. |
| **5** | **D: Eyelet + loop** | Low. Interlinked print-in-place FDM rings are highly sensitive to tolerance/swelling, requiring 0.25-0.35 mm clearances. | Low. PETG eyelet forms a brittle notch (60-150 N bound); routing TPU through an eyelet causes contact cutting (30-70 N limit). | Very Poor. The required print clearances create 2-3 mm of deadband slack (delayed force transmission on impact) plus frictional hysteresis. | Moderate. Eyelet clearance maps to BO, but violates sim physics severely. |

### (2) Assumption violations & minimal sim corrections

The existing simulation logic (`mujoco_sweep.py`, PyBullet, etc.) assumes rigid struts and ideal massless 1-D tendons attached at a point, with Hookean stretch and linear damping.

- **E (TPU rebar):** Violates by adding progressive slip and local embed deformation. *Correction:* Add a Kelvin-Voigt element (local embed compliance) in series with a Coulomb-like slip element tuned to activate near ~100-200 N.
- **A (Anchor-bulb):** Violates by adding bulb stretch and off-axis bearing friction. *Correction:* Add a small series compliance (the bulb) and a Coulomb friction term at the node for off-axis redirection.
- **B (Dovetail):** Violates via joint compliance and rotational hysteresis (TPU head scraping inside PETG slot). *Correction:* Add rotational friction / joint damping at the attachment node.
- **C (Sleeve):** Violates via massive progressive slip and a distributed attachment point (the 8 mm overlap). *Correction:* Treat as a progressive frictional damper with a non-linear stiffness curve.
- **D (Eyelet-loop):** Violates via deadband and routing friction. *Correction:* Add an explicit deadzone (0 force for ΔL < 2 mm) before the spring engages, plus a frictional routing penalty.

### (3) Drop-test design-of-experiments

Given the M23 limits and the two application regimes (`crutch_tip` @ 1.4 m/s / 30 kg surrogate mass and `nasa_lander` @ 9.8 m/s / 5 kg payload), here is a 12-specimen matrix to disambiguate the top two designs (E and A).

| Specimen | Design | Article | Regime | Measurement → Joint Physics |
| :--- | :--- | :--- | :--- | :--- |
| **1-3** | E (barbed) | Node coupon (single anchor) | `crutch_tip` (8 g, 1.4 m/s, 30 kg payload surrogate) | Monotonic static pull to failure (Instron) to measure pull-out force and slip onset. (Calibrates the Coulomb slip sim threshold). |
| **4-6** | A (anchor-bulb) | Node coupon (single bulb through-hole) | `crutch_tip` | Static pull + 8 g half-sine. Accel on payload; LDV on bulb face. Disambiguates bulb pull-through vs. PETG ligament crack vs. cable rupture. |
| **7-9** | E (barbed) | Full T3-prism | `nasa_lander` (1500 g cap, 9.8 m/s ΔV, 5 kg payload) | Accel on payload; LDV on saddle cable; post-test CT/photo. Measures peak g, specific energy absorbed (SEA), and joint survivability at 9.8 m/s. |
| **10-12** | A (anchor-bulb) | Full T3-prism | `nasa_lander` | Same as above. Compare repeatability across 3 drops vs E; monitor bulb migration and bearing-edge cutting. |

### (4) Concrete recommendation

**Primary:** E (TPU rebar embedded anchor, **barbed**).
**Backup:** A (Anchor-bulb).

**Required SCAD Geometry Updates for E (Barbed):**
To update `t3-prism.scad`, replace the simple point-to-point member sphere with an embedment cavity.
- Embed length: **10–12 mm** along the strut axis.
- Anchor stem diameter: **2.4 mm** (matching `cable_d`).
- Barbs: **2–3 barbs** spaced at 2.0 mm pitch. Major diameter **3.0–3.2 mm**. Barb step height ≥ 0.4 mm.
- Flank angles: 30–45° on pull-out face; 45–60° on insertion face.
- Ligament: Keep PETG thickness from barb crest to outer surface **≥ 1.0–1.2 mm**.

**BambuStudio CLI Flags & Process:**
- **Filament mapping:** TPU 95A first (if using A or B, but for E's embed, order matters less since it's coaxial). If using the H2D, slice with `PETG` at **250 °C** (bed 80 °C) and `TPU` at **215–225 °C**.
- **Layer height:** **0.16 mm** or **0.20 mm** (finer layers help barb definition and roof bridging).
- **Line width:** **0.42–0.45 mm**.
- **Walls (perimeters):** Increase to **4–6 walls** (this dominates strength for small nodes).
- **Infill:** **80–100% gyroid** in the nodes.
- **Speeds:** Keep TPU outer wall speed slow (**10–20 mm/s**) to improve accuracy and packing.
- **Retraction:** Manage carefully during toolchanges to prevent TPU ooze from blocking the embed cavity.
- **What to look for on Print 1:** Look for PETG roof droop (if the embed cavity has a flat top, orient it vertically so the cavity prints as a vertical blind hole), TPU stringing crossing the gap, and ensuring the interface doesn't just fuse into a blob but forms the defined barb steps.

### (5) Bibliographic gap

The Edison LITERATURE query for **Design A (Anchor-bulb)** (`0b5d7ba2-847e-47b3-bddf-127e2ed170d3`) stalled at 25+ minutes of runtime and its partial answer contains placeholder citations like `(artifact-00, pqac-00000031, pqac-00000032)`. The mechanical reasoning in the reply is highly relevant, but the specific references are missing. This should be followed up on once the parallel `LITERATURE_HIGH` query (`be6768ab...`) completes to replace those placeholders with actual bibliographic entries for the "Mark patents" and rigid-flexible joint studies it mentions.

---

### Discretionary Analytical Decisions:
- **Design Feasibility Ranking:** Weighed positive mechanical interlock concepts (barbs, dovetails) significantly higher than friction-based or print-in-place topological concepts based on the provided Edison literature evidence that chemical/frictional PETG-TPU FDM bonds are intrinsically weak and prone to sliding separation.
- **Assumption Violation Categorization:** Decided to treat distributed attachments (Sleeve) and deadband (Eyelet) as severe violations, whereas non-linear stiffness (Barbs) or local stretch (Bulb) were categorized as correctable via standard lumped-parameter Kelvin-Voigt or Coulomb friction nodes in MuJoCo.
- **DOE Construction:** Reduced the physical DOE matrix to only test the top two ranked designs, and matched the payloads explicitly to the MRG/issue `#28` scaling laws (using a 30 kg surrogate for the 75 kg crutch user to comply with Lansmont M23 limits, and the explicit 5 kg MER/GSFC scale for the 9.8 m/s drop). Allocated tests sequentially: static coupon first (to calibrate MuJoCo slip thresholds), then full dynamic tensegrity drops.
