# Activating Pre-Tension in Additively Manufactured Tensegrity Structures

**Context:** Issue [#87](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/87), motivated by Dr. Filipe Santos' feedback on [PR #41](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/41#issuecomment-5060966013): our printed-as-one-unit structures lack the pre-stress that defines true tensegrity behavior. Dr. Santos suggested exploring "activation" processes — e.g., heat applied to a shrinking material — so a structure printed in a relaxed state becomes pre-tensioned after printing (4D printing).

This survey covers documented, currently available methods, ordered roughly by compatibility with our existing FDM workflow.

---

## 1. Exploiting FDM residual stress in commodity filaments (lowest barrier to entry)

FDM printing inherently "programs" pre-strain into parts: polymer chains are drawn and aligned along the deposition direction, then frozen by rapid cooling. Heating the part above the glass transition temperature (Tg ≈ 60–65 °C for PLA) releases this stored strain, causing **contraction along the printing direction and slight expansion transverse to it** — no specialty filament required.

- **Thermorph** (CMU, CHI 2018) demonstrated self-folding of flat FDM prints into 3D shapes using off-the-shelf PLA, with the contraction ratio *controlled by print speed and layer thickness* ([paper](https://www.researchgate.net/publication/324668209_Thermorph_Democratizing_4D_Printing_of_Self-Folding_Materials_and_Interfaces), [HCII summary](https://www.hcii.cmu.edu/news/thermorph-flat-materials-self-fold-when-heated)). Contraction along the raster of tens of percent is achievable at high print speeds.
- **Shrink & Morph** (ACM TOG 2023) extends this to self-shaping shells actuated by the same shape-memory effect ([paper](https://dl.acm.org/doi/10.1145/3618386)).
- **Pattern transformation of heat-shrinkable polymer by 3D printing** (Sci. Rep. 2015) shows the released strain can be spatially programmed via raster patterns ([paper](https://www.nature.com/articles/srep08936)).
- Residual-stress programming via printing patterns is characterized for ABS and wood–plastic composites as well ([JMMP 2024](https://www.mdpi.com/2504-4494/8/2/77)).

**Application to our structures:** print tendons in PLA with 100% aligned (longitudinal) infill at high print speed; struts in a material/orientation that resists shrinkage (or thick enough cross-sections). A post-print oven cycle at ~70–90 °C shrinks the tendons a controlled amount, drawing the structure into a self-stressed state. The activation temperature, raster orientation, and print speed become new design/optimization variables — a natural fit for our Bayesian optimization framework.

**Caveats:** recovery (blocked) stress of glassy polymers near Tg is modest (order 0.1–10 MPa), and the tendons are hot and compliant during activation; the achievable locked-in pre-tension after cooling must be characterized (and simulated — see §7). Creep/relaxation of PLA under sustained load is a known issue.

## 2. Dedicated shape-memory polymer (SMP) filaments and blends — "true" 4D printing

Purpose-made SMP feedstocks give better-controlled activation temperatures and recovery ratios than commodity PLA:

- **PLA/TPU blends** are the most directly relevant to us, since TPU is already in our workflow. A recent dual-stimuli PLA/APHA/TPU blend activates at **≈ 39.5 °C with ~100% shape fixity and > 92% recovery** ([PMC 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12590943/)). Systematic studies of PLA-TPU blends map the shape-memory effect vs. blend ratio, loading mode, and programming temperature ([J. Mater. Sci. 2023](https://link.springer.com/article/10.1007/s10853-023-08460-0)).
- **TPU-PLA SMPs and nanocomposites for deployable structures** were demonstrated at AIAA SciTech 2024 ([paper](https://arc.aiaa.org/doi/10.2514/6.2024-2149)) — deployable-structure framing is close to the tensegrity use case.
- FDM process parameters themselves tune the shape-memory response of plain PLA ([J. Manuf. Process. 2020](https://www.sciencedirect.com/science/article/abs/pii/S1526612520308276)).
- Commercial SMP filaments exist (e.g., polyurethane-based SMP such as SMP Technologies' MM-series); two-layer composite strategies with commercial filaments are documented ([Polymers 2022](https://doi.org/10.3390/POLYM14245446)).

**Note on physics:** the *shape-memory-effect* route (deform/"program" the part above Tg, cool, later reheat to recover) requires a programming step after printing, whereas the §1 route uses strain programmed *by the printing process itself* — the latter preserves our print-as-one-assembled-unit goal.

## 3. SMP tensegrity — the closest published precedents

Two papers essentially prototype what Dr. Santos described:

- **"Programmable Deployment of Tensegrity Structures by Stimulus-Responsive Polymers"** (Liu, Wu, Paulino, Qi — Sci. Rep. 2017): tensegrity with 3D-printed SMP struts that store elastic energy in a compacted state and **deploy into a self-stressed tensegrity on heating** ([coverage](https://www.futurity.org/3d-printed-tensegrity-structure-1459522/), [3DPI](https://3dprintingindustry.com/news/research-uses-3d-printer-create-shape-shifting-tensegrity-structures-116165/)). Here the *struts* are the active element; tendons are elastomeric and get tensioned by strut deployment — an alternative to shrinking the tendons.
- **"3D-printed programmable tensegrity for soft robotics"** (Lee et al., Sci. Robotics 2020): PLA struts with magnetic-elastomer tendons made by 3D-printed sacrificial molding; **pre-tension is introduced by fabricating tendons shorter than the geometric distance between attachment points** ([paper](https://www.science.org/doi/abs/10.1126/scirobotics.aay9024), [PubMed](https://pubmed.ncbi.nlm.nih.gov/33022636/)).
- A 2025 Springer chapter, **"On the Additive Manufacturing of Tensegrity Systems"** ([link](https://link.springer.com/chapter/10.1007/978-3-031-82283-4_9)), reviews AM routes for tensegrity specifically and is worth acquiring for `literature/`.

## 4. Reduced-length / geometrically pre-strained tendons (no smart material)

Pre-tension can be purely geometric: print the tendon network shorter than the strut-to-strut distance and stretch it during a (minimal) assembly step, as in the Sci. Robotics work above, or print the whole structure in a deformed (e.g., flattened or twisted) configuration held by thin sacrificial tabs/supports — cutting or dissolving them releases stored elastic energy into pre-tension. Caltech's tensegrity-inspired lattices similarly rely on elastic pre-compression to tune dynamics ([Pajunen, Celli, Daraio — arXiv:2011.00167](https://arxiv.org/abs/2011.00167), [EML 2021](https://www.sciencedirect.com/science/article/abs/pii/S2352431621000390)), showing pre-strain is also a *tuning knob* for wave/impact response, which connects directly to our drop-test objectives. This route sacrifices some of the "fully printed-and-activated" elegance but needs no new materials.

## 5. Shape-memory alloy (SMA / nitinol) tendons — Dr. Santos' own domain

SMA wires deliver what polymers cannot: **recoverable strains of ~6–8% with actuation stresses of hundreds of MPa**, repeatably. Dr. Santos has published extensively on exactly this — e.g., an [adaptive shape-morphing tensegrity with frequency self-tuning using SMAs](https://iopscience.iop.org/article/10.1088/0964-1726/24/10/105008), [tensegrity with actuator and pseudoelastic SMAs](https://www.researchgate.net/publication/349361881_Tensegrity_Structures_Incorporating_Actuator_and_Pseudoelastic_Shape_Memory_Alloys), and [superelastic tensegrity braces](https://www.researchgate.net/publication/336203654_Mechanical_modeling_of_superelastic_tensegrity_braces_for_earthquake-proof_structures). SMA tendons cannot be co-printed in polymer FDM (insertion post-print, or print-pause-embed), so this is a hybrid AM route — but it gives by far the highest and most controllable pre-tension, and collaborating on it would play to Dr. Santos' expertise.

## 6. Other activation stimuli (further out)

- **Magnetic:** PLA/TPU/Fe₃O₄ magneto-responsive SMPs recover shape in ~40 s under an alternating field, with recovery ratio > 91% ([Composites B 2022](https://www.sciencedirect.com/science/article/abs/pii/S1359836822007557)) — remote, spatially selective activation without an oven.
- **Light/photothermal:** fillers (CNTs, gold nanorods) enable light-triggered heating of specific members ([review](https://www.tandfonline.com/doi/full/10.1080/19475411.2025.2458833)).
- **Moisture/solvent:** hygroscopic filaments (wood-fill, hydrogels) swell/shrink with humidity — generally too weak and slow for structural pre-tension.

## 7. Comparison and recommended path

| Route | Active element | Activation | Est. recoverable strain | Est. recovery stress | Fits print-as-one-unit? | Effort |
|---|---|---|---|---|---|---|
| §1 PLA residual stress | tendons | oven ~70–90 °C | up to ~10–30% (speed-dependent) | low (≲ a few MPa) | **yes** | low |
| §2 SMP/PLA-TPU blends | tendons (or struts) | ~40–70 °C | 10s of % | low–moderate | yes (needs programming step unless print-programmed) | medium |
| §3 SMP struts deploy | struts | heat | large (deployment) | moderate | partially (compact print state) | medium |
| §4 Geometric pre-strain | tendons | mechanical release/assembly | design-defined | material-defined | partially | low |
| §5 SMA tendons | tendons | Joule/oven heating | ~6–8% | ~100s of MPa | no (hybrid embed) | high |
| §6 Magnetic/light SMP | either | field / light | 10s of % | low | yes | medium-high |

**Suggested near-term experiments** (aligned with Dr. Santos' advice to do FEA before physical testing):

1. **Characterization coupons:** print PLA tendon-like strips at several print speeds/temperatures with aligned raster; measure free shrinkage strain and constrained (blocked) recovery force vs. oven temperature. This yields the material inputs for FEA.
2. **FEA of the activated state:** impose the measured tendon eigenstrain (thermal-contraction analog) on our existing structure models to predict the achievable self-stress state and check strut buckling — before any drop testing.
3. **Two-material demonstrator:** a single printed tensegrity-inspired cell with PLA tendons (high-speed, aligned raster) and stiffer/thicker struts (or TPU struts, exploiting the modulus mismatch), oven-activated; compare natural frequency or stiffness before/after activation as a simple pre-tension metric — mirroring the frequency-tuning metric in Dr. Santos' SMA tower paper.
4. **Longer term:** evaluate a PLA/TPU blend or commercial SMP filament for lower, sharper activation temperatures, and discuss an SMA-tendon hybrid variant with Dr. Santos.

---

## References (key)

1. An et al., *Thermorph: Democratizing 4D Printing of Self-Folding Materials and Interfaces*, CHI 2018. https://www.researchgate.net/publication/324668209
2. Jourdan et al., *Shrink & Morph: 3D-Printed Self-Shaping Shells Actuated by a Shape Memory Effect*, ACM TOG 2023. https://dl.acm.org/doi/10.1145/3618386
3. Zhang et al., *Pattern Transformation of Heat-Shrinkable Polymer by 3D Printing*, Sci. Rep. 5, 8936 (2015). https://www.nature.com/articles/srep08936
4. Liu, Wu, Paulino, Qi, *Programmable Deployment of Tensegrity Structures by Stimulus-Responsive Polymers*, Sci. Rep. 7, 3511 (2017).
5. Lee et al., *3D-printed programmable tensegrity for soft robotics*, Sci. Robotics 5, eaay9024 (2020). https://www.science.org/doi/abs/10.1126/scirobotics.aay9024
6. Pajunen, Celli, Daraio, *Prestrain-induced bandgap tuning in 3D-printed tensegrity-inspired lattice structures*, Extreme Mech. Lett. 44 (2021). https://arxiv.org/abs/2011.00167
7. Amarante dos Santos et al., *Design and experimental testing of an adaptive shape-morphing tensegrity structure, with frequency self-tuning capabilities, using shape-memory alloys*, Smart Mater. Struct. 24, 105008 (2015). https://iopscience.iop.org/article/10.1088/0964-1726/24/10/105008
8. *Dual-Stimuli Responsive and Sustainable PLA/APHA/TPU Blend for 4D Printing* (2025). https://pmc.ncbi.nlm.nih.gov/articles/PMC12590943/
9. *4D printing of PLA-TPU blends: effect of PLA concentration, loading mode, and programming temperature*, J. Mater. Sci. (2023). https://link.springer.com/article/10.1007/s10853-023-08460-0
10. *4D printing of mechanically robust PLA/TPU/Fe₃O₄ magneto-responsive shape memory polymers*, Composites Part B (2022). https://www.sciencedirect.com/science/article/abs/pii/S1359836822007557
11. *On the Additive Manufacturing of Tensegrity Systems*, Springer (2025). https://link.springer.com/chapter/10.1007/978-3-031-82283-4_9
12. *Interrelations between Printing Patterns and Residual Stress in FDM for 4D Printing*, J. Manuf. Mater. Process. 8, 77 (2024). https://www.mdpi.com/2504-4494/8/2/77
