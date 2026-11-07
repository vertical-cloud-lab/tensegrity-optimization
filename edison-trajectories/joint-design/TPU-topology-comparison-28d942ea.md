# Edison ANALYSIS — TPU-inside vs TPU-outside topology comparison

**Task ID**: `28d942ea-bc9e-4e7a-b32d-b7dd967ddda6`  
**Status**: `success`  
**Job**: `job-futurehouse-data-analysis-crow-high`

## Answer

Best-supported answer: for the lander / egg-drop use case, Strategy B (your captive-core, TPU inside PLA) is the better fit. For a mostly axial crutch-tip load path, I would still favor a geometry-led joint like your dovetail Design B for the working cable connection, but between the two topologies you asked about, Strategy B is still the safer choice if reuse and bond-independence matter. The reason is simple: the strongest evidence I could verify says PLA–TPU FDM adhesion is weak and variable, while your captive-core design removes that interface from the primary retention path.

1. Which topology is better?

(i) Lander / egg-drop, omnidirectional impact, Bruceton n≥20 reuse
- Recommend: Strategy B, captive-core.
- Why: repeated drop impact will load the strut-cable transition off-axis, so a TPU-on-the-outside skin is exposed to peel and fatigue at the rigid-soft interface. Your captive-core instead retains the tendon by geometry: 7.0 mm TPU core through a 2.8 mm bore gives a 2.5× diameter pull-out ratio from your attached Design F files (`F_captive_core.md`, `F_captive_core.scad`). That means retention does not depend on PLA–TPU chemical bonding.
- The best quantitative PLA–TPU interface paper I could verify for FDM is Brancewicz-Steinmetz and Sawicki, who reported mean adhesion strengths of 0.37 MPa for PLA/TPU and 0.39 MPa for TPU/PLA, with strong dependence on print order and surface pattern: DOI 10.3390/ma14216464.
- A newer IJAMT study also found that PLA–TPU adhesion is sensitive to layer height and thermal history; peak lap-shear loads ranged about 150–350 N depending on settings, and failure could occur either in internal PLA layers or at the TPU–PLA interface: DOI 10.1007/s00170-025-17099-x.
- For a reusable drop article, that variability is the wrong thing to trust.

(ii) Uni-axial crutch-tip, primarily axial cable loading
- Between A and B only: lean B again, but with less margin than for the lander.
- Why: if loading is mostly axial and controlled, a wrapped outer TPU skin can work mechanically, but it still asks the PLA–TPU interface to survive sustained cyclic strain. B avoids that dependency.
- That said, your own project context already points to the dovetail co-print geometry as the preferred crutch-tip option. So the more precise answer is: for the crutch-tip, use the axial-load-optimized dovetail as the main joint, and keep captive-core logic where you need bond-independent anchoring.

2. Mechanical performance from the literature

(a) Pull-out / peel strength for Ye-style core-wrapping topology, PLA+TPU FDM
- I could not verify a peer-reviewed Ye tensegrity paper matching the manuscript claim as written.
- Important correction: the DOI mentioned in your workspace context, 10.1016/j.jmps.2023.105392, is not a Ye tensegrity paper. CrossRef resolves it to Filla et al., “A multiscale framework for modeling fibrin fiber networks,” Journal of the Mechanics and Physics of Solids 179, 105392 (2023). It is unrelated.
- The closest verifiable Ye paper I found is Ye et al., “Effects of process parameters on mechanical properties and interface of 3D printed bamboo-inspired CCFR-PLA/TPU composites,” Polymer Composites (2023), DOI 10.1002/pc.27770. This is a multi-matrix PLA/TPU composite paper, not a tensegrity paper, and I did not find direct pull-out or peel values for a strut wrapped by TPU skin.
- So I cannot give a verified pull-out number for “Ye et al. core-wrapping tensegrity PLA+TPU” because I could not verify that exact source.

(b) Published data on print-in-place TPU-in-PLA encapsulation pull-out resistance
- I could not find a peer-reviewed paper giving direct pull-out force data for a print-in-place TPU knot fully encapsulated inside a PLA shell with a small exit bore, i.e. your exact Design F concept.
- So the 2.5× pull-out ratio is currently supported by your attached geometry, not by a matched literature test series.

(c) Layer-interlock / mechanical-tooth features vs chemical adhesion under cyclic loading
- Direct PLA–TPU cyclic fatigue data on tooth-interlocked joints is sparse.
- The broad trend is still clear: when adhesion is weak or inconsistent, mechanical interlocking is the standard workaround.
- A useful prior-art anchor is Alsheghri et al., “Bio-inspired and optimized interlocking features for strengthening metal/polymer interfaces in additively manufactured prostheses,” Acta Biomaterialia 78 (2018): 301–311. DOI 10.1016/j.actbio.2018.09.029. Different material pair, but directly relevant on the point that geometry-based interlocks can outperform reliance on pure interface adhesion when joining dissimilar materials.
- For PLA–TPU specifically, the verified adhesion numbers are low: 0.37–0.39 MPa in Brancewicz-Steinmetz and Sawicki (2021), DOI 10.3390/ma14216464. That supports your choice to shift retention to teeth + captive geometry.

(d) Expected failure mode under repeated drop impact
- Strategy A, TPU outside / PLA inside:
  - Most likely failure sequence: progressive TPU-skin peel or interfacial delamination at the PLA–TPU boundary, then local tearing or crack initiation at the strut-to-cable transition.
  - Literature basis: weak/variable PLA–TPU adhesion in FDM (10.3390/ma14216464; 10.1007/s00170-025-17099-x) plus your loading case, which is peel-heavy rather than pure shear.
- Strategy B, TPU inside / PLA outside:
  - Most likely failure sequence: wear or local indentation at the bore lip, tooth shear / ratcheting if teeth are undersized, or shell cracking at the teardrop-shell junction if impact bending is high.
  - That is a better failure family for your lander because those are geometry/material-thickness problems you can tune, rather than bond chemistry you can’t reliably tune on PLA–TPU.

3. Printability on Bambu H2D, 0.4 mm nozzle, 0.2 mm layer, TPU 85A

(a) Strategy A, TPU on the outside of PLA
- Yes, print sequencing matters. Outer TPU skin means the soft material is exposed on the outer contour and must bridge or drape over previously printed rigid features depending on geometry.
- Known issue class: TPU bridges and unsupported outer skins sag more readily than rigid plastics. Even community-level print-in-place guidance treats TPU as the least forgiving common FDM material for bridging and articulated clearances.
- A practical print-in-place reference gives recommended sliding-joint clearances of about 0.30 mm for PLA, 0.40 mm for PETG, and 0.50 mm for TPU 95A, and explicitly says TPU bridging is “not recommended” for many print-in-place situations because of sag/flex sensitivity. Source: UAVMODEL print-in-place guide, retrieved via web. This is not peer-reviewed, so use it as engineering guidance, not as manuscript evidence.
- On an H2D/IDEX workflow, Strategy A is more exposed to tool-change ooze, outer-surface quality loss, and sagging if the TPU skin contains unsupported spans.

(b) Strategy B, TPU-inside-PLA with 0.5 mm radial gap
- Your 0.5 mm radial gap is plausible and close to current community best practice.
- The same print-in-place guide recommends 0.50 mm for TPU 95A sliding joints. Because TPU 85A is softer and typically more compliant/tacky than 95A, 0.5 mm should be treated as the minimum, not a generous margin.
- So: 0.5 mm is probably sufficient, but only barely. I would validate with a tolerance coupon before committing to full specimens.
- Your teardrop cavity choice is also good. Teardrop/flat bridge geometries are standard ways to reduce fusion risk versus circular-over-circular closures.

4. Hybrid approach?
- Yes, in principle. A hybrid could combine:
  - an internal captive TPU knot for bond-independent load retention, and
  - a thin external TPU skin for abrasion damping, impact softening, or local energy absorption.
- Mechanically that could work, but I did not find a verified paper on this exact hybrid in FDM tensegrity struts.
- The main downside is manufacturing complexity: more tool changes, more ooze management, and you reintroduce an outer PLA–TPU interface that may peel even if it is no longer structurally critical.
- So if you try a hybrid, keep the outer TPU skin non-structural. Let the inner captive core carry retention.

5. Manuscript correction for lines 378–395

Use something like this:

“Specimens are fabricated on a multi-material FDM printer using PLA for the rigid struts and TPU 85A for the soft tension elements. Unlike outer-overmolded rigid–soft architectures that rely on interfacial bonding between deposited polymers, the present design uses a captive-core joint in which a soft TPU anchor is fully enclosed within a rigid PLA shell. In the implemented geometry (Design F), a 7.0 mm TPU core is printed in place inside an 8.0 mm cavity within a 12.0 mm outer shell, with the tendon exiting through a 2.8 mm bore. Retention is therefore geometric rather than adhesive: the TPU anchor cannot pass back through the bore, giving a core-to-bore diameter ratio of 2.5. To further suppress axial slip without relying on PLA–TPU chemical adhesion, the shell and core incorporate staggered rings of radial interlock teeth. This approach was chosen because published FDM studies report relatively weak and process-sensitive PLA–TPU adhesion, with mean interfacial strengths on the order of 0.37–0.39 MPa depending on print order and surface pattern [Brancewicz-Steinmetz and Sawicki, 2021, DOI:10.3390/ma14216464], whereas geometry-based interlocks are a standard route for strengthening dissimilar-material interfaces [Alsheghri et al., 2018, DOI:10.1016/j.actbio.2018.09.029]. For impact-dominated use cases such as the reusable egg-drop lander, placing the TPU anchor inside the PLA shell protects the compliant tendon from external abrasion and moves the critical failure mode away from interface peel and toward shell or interlock failure, which is more directly tunable through geometry.”

What I can support strongly vs weakly
- Strongly supported:
  - PLA–TPU adhesion in FDM is weak and process-sensitive: 10.3390/ma14216464; 10.1007/s00170-025-17099-x.
  - Mechanical interlocking is a sound strategy when dissimilar-material adhesion is poor: 10.1016/j.actbio.2018.09.029.
  - Khatri 2024 is real, but it is ABS/TPU honeycomb energy absorption, not PLA/TPU strut wrapping: 10.1089/3dp.2022.0196.
  - The JMPS DOI in the workspace is wrong for Ye.
- Weak / not verified:
  - Direct pull-out data for Ye-style TPU-outside PLA-inside tensegrity struts.
  - Direct published pull-out data for print-in-place TPU-knot-inside-PLA-shell assemblies matching Design F.
  - A peer-reviewed paper on the exact hybrid “inner captive core + outer TPU skin” topology.

Citations
- Brancewicz-Steinmetz E, Sawicki J. The Influence of 3D Printing Parameters on Adhesion between Polylactic Acid (PLA) and Thermoplastic Polyurethane (TPU). Materials. 2021;14(21):6464. DOI: 10.3390/ma14216464.
- Bisicchia S, et al. On the interlaminar bonding adhesion of the PLA-TPU printed multimaterial. International Journal of Advanced Manufacturing Technology. 2025. DOI: 10.1007/s00170-025-17099-x.
- Harris CG, Jursik NJS, Rochefort WE, Walker TW. Additive Manufacturing With Soft TPU – Adhesion Strength in Multimaterial Flexible Joints. Frontiers in Mechanical Engineering. 2019;5:37. DOI: 10.3389/fmech.2019.00037.
- Alsheghri A, Alageel O, Mezour MA, Sun T, Yue S. Bio-inspired and optimized interlocking features for strengthening metal/polymer interfaces in additively manufactured prostheses. Acta Biomaterialia. 2018;78:301–311. DOI: 10.1016/j.actbio.2018.09.029.
- Khatri NR, Egan PF. Energy Absorption of 3D Printed ABS and TPU Multimaterial Honeycomb Structures. 3D Printing and Additive Manufacturing. 2024. DOI: 10.1089/3dp.2022.0196.
- Ye W, Dou H, Zhang D, Yang F, Cheng Y, Cai W. Effects of process parameters on mechanical properties and interface of 3D printed bamboo-inspired CCFR-PLA/TPU composites. Polymer Composites. 2023. DOI: 10.1002/pc.27770.

- Discretionary analytical decisions made during the analysis
- Treated the user’s “Strategy A / Strategy B” question as an engineering selection problem under uncertain literature coverage, rather than forcing a binary answer from incomplete direct-comparison data.
- Used verified peer-reviewed PLA–TPU adhesion papers as the main evidence base when exact tensegrity-specific sources could not be confirmed.
- Used a community print-in-place clearance guide only for printer-gap guidance, and not as primary evidence for manuscript-level mechanical claims.
- Interpreted likely failure modes mechanistically from the verified interface-strength literature plus the provided Design F geometry, because direct cyclic drop-fatigue papers on this exact joint were not found.
- Proposed manuscript replacement text that removes the unverified Ye tensegrity claim and anchors the paragraph to verified PLA–TPU adhesion literature and the attached Design F geometry.
