Question: Context. We are building a printable Snelson-class tensegrity (PETG struts,
TPU 85A tendons, fabricated on a Bambu H2D IDEX printer) and running a
Bayesian-optimization loop over geometry (strut + tendon diameters,
prestress, topology) for two parallel application threads:
  (1) an assistive crutch-tip / impact-absorber under quasi-static and
      drop-impact loading; and
  (2) a SUPERball-lineage drag-free egg-drop demo, using h_crit (Bruceton
      staircase, n>=20) as the primary FoM and peak g_max @ 3 m + SEA +
      reusability (N_reuse) as secondaries.
Open technical issues across our PRs include: (i) no peer-reviewed
PETG-TPU interface bond data exists, so our PETG-TPU joint geometry
(barbed TPU rebar / dovetail / anchor-bulb variants) is currently
literature-extrapolated from PLA-TPU; (ii) rigid-strut tensegrity sims
in MuJoCo/PyBullet show peak-g is dominated by floor-contact stiffness
rather than cable stiffness, suggesting we need DiffPD or PolyFEM+IPC
for quantitative impact predictions; (iii) the closest published egg-drop
analogs are Anand 2022 (biodegradable, 75 m, single-use), Zhang 2022
(22 in / 20 m / 235 g, reusable, best instrumented dataset) and the NASA
SUPERball NIAC report (Agogino + SunSpiral 2018), but none target the
"reusable, omnidirectional, low-rho_rel, FFF-printable, BO-optimized"
quadrant we occupy.

We have drafted an outreach contact list (reviews/target_audience.md
section 3d-prime) that includes Julian Rimoli (Georgia Tech, AIAA SciTech
2016 lander), Adrian Agogino (NASA Ames, NIAC SUPERball Phase 2 2018),
Vytas SunSpiral (formerly NASA Ames), Mark Mueller (UC Berkeley HiPeRLab,
IEEE/ASME T-Mech 2024 collision-resilient icosahedron), Andrew Zhang +
Brian Cera (UC Berkeley, Agogino lineage), Massimo Vespignani (SUPERball
v2 2018), Robert Skelton + Cornel Sultan (TAMU / Virginia Tech,
class-1 lander theory), Jamshid Bayandor (Virginia Tech CRASH Lab,
TANDEM 2017), Jing Zhang et al. (Harbin Institute of Technology,
Aerospace 2025), and Madhumati Anand (biodegradable 75 m, 2022).

Question. For a first-contact email to each of the above researchers,
enumerate -- with peer-reviewed citations to their own published work
where possible:

(a) Highest-leverage technical / scientific feedback aspects to surface
    (5-8 archetype clusters; ~2 sentences each), e.g. "FFF tensegrity
    impact-mechanics fidelity gap (rigid-strut vs DiffPD vs experiment)",
    "PETG-TPU multi-material interface characterization", "Bruceton
    h_crit as a transferable benchmark across the SUPERball / Zhang /
    Anand lineage", "BO acquisition function choice for noisy impact
    objectives", "scaling and orientation-isotropy validation against
    Vespignani / Bayandor scaled-up tensegrities", etc.

(b) Tech-transfer / commercialization angles worth raising
    (e.g. NIAC successor, NASA SBIR/STTR space-systems topics, DoT/FAA
    drone-cargo airdrop, biomedical orthotics OEMs, defense-payload
    landers, IEEE Spectrum / Sci. Am. demo).

(c) Immediate "gotchas" an experienced practitioner is most likely to
    flag on first read of our setup, e.g. "your floor-contact stiffness
    swamps your cable signal", "TPU 85A creep will shift prestress
    between drops", "Bambu H2D filament-swap interface is the most
    likely failure mode", "Bruceton staircase needs randomized
    orientations to be defensible", "tensegrity classification (class-1
    vs class-2) depends on strut closest-approach distance".

(d) Collaborative contribution mechanisms compatible with each
    archetype: external validation against their published datasets,
    inter-lab specimen exchange, instrument-time swaps (e.g. Lansmont
    M23 drop tower + Polytec / QTec LDV), shared standardized
    egg-drop benchmark protocol, GitHub-hosted reproducible BO loop,
    co-supervised undergraduate / capstone projects, joint conference
    workshop or invited session, cross-citation in revision, etc.

(e) For each named lander-pool contact above, recommend WHICH one or
    two of the (a)-(d) asks is best-suited to that person, anchored
    to the specific paper of theirs that would motivate the ask.

Format. Markdown, with a short opening summary table mapping
{archetype cluster -> 2-sentence pitch -> best contact -> citation}.
Then the per-archetype detail. Then the per-contact recommendations.
Then a "stretch" section on collaborative-contribution mechanisms we
might not have considered. Inline citations to the actual peer-reviewed
papers we should reference in the email body.


# Outreach Strategy for Printable Snelson-Class Tensegrity: Archetype Clusters, Per-Contact Recommendations, and Collaborative Mechanisms

## Opening Summary Table

The following table maps each of the seven highest-leverage technical feedback clusters to a two-sentence email pitch, the best-matched contact(s), and the anchoring peer-reviewed citation to reference in the email body.

| Archetype Cluster | 2-Sentence Pitch | Best Contact(s) | Key Citation(s) |
|---|---|---|---|
| FFF tensegrity impact-mechanics fidelity gap (rigid-strut vs DiffPD vs experiment) | Our current rigid-strut MuJoCo/PyBullet models appear useful for fast screening, but published tensegrity-lander work and modern differentiable deformable solvers suggest that buckling, contact, and post-buckling energy storage must be modeled more faithfully before claiming quantitative peak-g accuracy. We would value guidance on the minimum experiment-plus-simulation stack needed to bridge from reduced-order or rigid models to validated impact predictions for printed PETG/TPU hardware. | Julian Rimoli; Jamshid Bayandor | Garanger et al. 2021; Du et al. 2021; Huang et al. 2024; Bayandor et al. 2017 (garanger2021softtensegritysystems pages 12-14, du2021diffpddifferentiableprojective pages 1-2, huang2024differentiablesolverfor pages 2-3, bayandor2017lightweightmultifunctionalplanetary pages 24-27) |
| PETG-TPU multi-material interface characterization | We have not found peer-reviewed PETG-TPU bond data, so our joint concepts are extrapolated from broader multi-material FFF and PLA-TPU interface literature, where adhesion is highly geometry- and process-dependent and mechanical interlocking can dominate apparent bond strength. A first-pass characterization matrix on barb/dovetail/anchor-bulb joints would likely be more valuable than bulk coupon testing alone. | Madhumati Anand; Robert Skelton | Lopes et al. 2018; Lopes 2024 interface review (lopes2024interfaceboundarymechanical pages 37-40) |
| Bruceton h_crit as transferable benchmark across SUPERball / Zhang / Anand lineage | A Bruceton up-and-down h_crit protocol could give the egg-drop thread a compact, statistically defensible primary figure of merit that is more transferable than isolated “max survived height” anecdotes across different tensegrity morphologies. We would especially value feedback on whether orientation randomization, step-size choice, and binary failure definition are sufficient to make h_crit comparable to SUPERball-lineage and humanitarian-drop demonstrations. | Andrew Zhang; Madhumati Anand | Fuh 2021 Bruceton design analysis; Anand et al. 2022 (anand2212takingoffwith pages 1-2) |
| BO acquisition function choice for noisy impact objectives | Because impact outcomes are stochastic, multi-objective, and expensive to evaluate, the optimizer likely matters almost as much as the geometry parameterization; crashworthiness literature suggests reliability-aware and multi-objective formulations are often needed once peak-g, SEA, and mass/reuse trade off strongly. We would value advice on whether to privilege robust expected improvement, constrained BO, or a reliability-based formulation for repeated-drop objectives with orientation and floor variability. | Julian Rimoli; Adrian Agogino | Fang et al. 2017; Goyal et al. 2019 (goyal2019tensegritysystemdynamics pages 1-3) |
| Scaling and orientation-isotropy validation | Several lander papers emphasize that scaling and impact orientation can dominate conclusions: TANDEM reports near-omnidirectional protection only after broad orientation sweeps, while recent spherical tensegrity studies tune prestress, bar area, and damping against rebound/cushioning tradeoffs. We would appreciate feedback on how many orientations, scales, and repeats are needed before we can defensibly claim “omnidirectional” or “isotropic enough” behavior for a printable Snelson-class design. | Jamshid Bayandor; Massimo Vespignani; Jing Zhang | Bayandor et al. 2017; Vespignani et al. 2018; Zhang et al. 2025 (bayandor2017lightweightmultifunctionalplanetary pages 31-35, zhang2025designandcushioning pages 19-21, zhang2025designandcushioning pages 18-19) |
| Floor-contact stiffness dominance and sim-to-real gap | Our preliminary simulations suggest floor-contact stiffness may swamp cable-stiffness effects, which aligns with recent collision-resilient robot work where contact modeling and controller recovery logic are central to observed behavior. We would value advice on how to separate structure-driven attenuation from test-surface artifacts and whether a learned or differentiable contact model is the most practical path to sim-to-real fidelity. | Mark Mueller; Kun Wang / Kostas Bekris | Zha et al. 2024; Wang et al. 2021 (zha2024designandcontrol pages 9-11, wang2021sim2simevaluationof pages 1-2) |
| TPU 85A creep/prestress drift and FFF joint reliability | Printed TPU shows substantial stress relaxation over hours and strong dependence on print strategy, so drop-to-drop prestress drift may be one of the biggest hidden variables in both crutch-tip and egg-drop testing. We would value feedback on how to treat prestress as a state variable to be measured and refreshed, rather than a fixed design input, and on whether joint failures should be interpreted primarily as material-interface, geometric-interlock, or viscoelastic preload-loss problems. | Robert Skelton / Cornel Sultan; Mark Mueller | Bruère et al. 2023; Skelton & Oliveira 2009 (bruere2023theinfluenceof pages 1-2, oliveira2009tensegritysystems pages 1-15) |


*Table: This table maps the seven highest-leverage outreach themes to a concise two-sentence email pitch, the best-matched contact person(s), and supporting citations. It is useful as a compact front-end for customizing first-contact emails across the lander, robotics, and materials communities.*

---

## (a) Highest-Leverage Technical / Scientific Feedback Clusters

### Cluster 1: FFF Tensegrity Impact-Mechanics Fidelity Gap (Rigid-Strut vs. DiffPD vs. Experiment)

Your current MuJoCo/PyBullet rigid-strut simulations are useful for fast topology screening but cannot capture the post-buckling energy storage and distributed deformation that dominate real tensegrity impact behavior. Garanger et al. (2021) showed that even reduced-order tensegrity models require careful calibration of buckling and ground-friction coupling to predict horizontal travel and energy partition during hopping maneuvers (garanger2021softtensegritysystems pages 12-14). Bayandor's TANDEM work demonstrated that rigid compression-member models predict peak decelerations within ~12.5% of deformable models for most orientations but can falsely predict contacts, requiring deformable-model confirmation runs at ~4× computational cost (bayandor2017lightweightmultifunctionalplanetary pages 31-35, schroeder2017acomprehensiveentry pages 90-94). On the differentiable-simulation side, DiffPD offers 4–19× speedups over Newton's method for soft-body inverse design with penalty-based or complementarity-based contact (du2021diffpddifferentiableprojective pages 1-2, du2021diffpddifferentiableprojective pages 9-11), while PolyFEM+IPC provides intersection-free contact handling with analytical adjoint gradients and supports shape, material, and friction optimization simultaneously—capabilities DiffPD lacks (huang2024differentiablesolverfor pages 2-3, huang2024differentiablesolverfor pages 14-16). Wang et al. (2021) demonstrated the first differentiable physics engine specifically for tensegrity robots, achieving sim2sim transfer to MuJoCo with only 0.25% of ground-truth data (wang2021sim2simevaluationof pages 7-8, wang2021sim2simevaluationof pages 1-2). The key ask is: what is the minimum experiment-plus-simulation stack needed to move from rigid-strut screening to validated peak-g predictions for printed PETG/TPU hardware?

### Cluster 2: PETG-TPU Multi-Material Interface Characterization

No peer-reviewed PETG-TPU interface bond data currently exists in the multi-material FFF literature (lopes2024interfaceboundarymechanical pages 37-40). The closest analogs are PLA-TPU studies, where adhesion is highly geometry- and process-dependent and mechanical interlocking (e.g., T-shape joints) can dominate apparent bond strength over diffusion-based adhesion alone (lopes2024interfaceboundarymechanical pages 37-40). Your barbed TPU rebar / dovetail / anchor-bulb joint variants are well-motivated by this literature, but a first-pass PETG-TPU characterization matrix (varying interface geometry, extrusion temperature, and nozzle height) would be more valuable than bulk coupon testing, given the absence of baseline data.

### Cluster 3: Bruceton h_crit as a Transferable Benchmark Across the SUPERball / Zhang / Anand Lineage

The Bruceton staircase (up-and-down) method, originally formalized by Dixon & Mood (1948), is the standard sensitivity-testing protocol for binary-outcome experiments and is well-suited to egg-drop h_crit determination. Anand et al. (2022) reported drop tests up to 75 m with biodegradable tensegrities but found reusability limited to 4–5 drops before jute strings frayed (anand2212takingoffwith pages 1-2), while Zhang et al. (2022, AIAA) provided the best-instrumented reusable tensegrity lander dataset (22 in / 20 m / 235 g). A standardized Bruceton protocol with randomized orientations, defined step size, and explicit binary failure criteria (egg intact/broken) would make h_crit comparable across these lineages and your FFF-printable designs.

### Cluster 4: BO Acquisition Function Choice for Noisy Impact Objectives

Impact outcomes are stochastic (orientation-dependent, floor-surface-dependent), multi-objective (h_crit, peak g_max, SEA, N_reuse), and expensive to evaluate physically. The crashworthiness optimization literature emphasizes that reliability-aware and multi-objective formulations are typically required when peak-g, SEA, and mass/reuse trade off strongly. Goyal et al. (2019) derived analytical energy-absorption equations for D-bar tensegrity systems that could serve as cheap surrogate models within a BO loop (goyal2019tensegritysystemdynamics pages 1-3). The key question for experienced practitioners is whether robust expected improvement, constrained BO, or a reliability-based formulation is most appropriate given the orientation and floor variability inherent in repeated-drop testing.

### Cluster 5: Scaling and Orientation-Isotropy Validation

Bayandor's TANDEM work established that tensegrity lander mass scales approximately linearly with impact velocity for a given payload mass, and that a broad "impact globe" orientation sweep is needed before claiming omnidirectional protection—most orientations yielded peak payload accelerations under ~120 g, but outliers reached ~224 g (bayandor2017lightweightmultifunctionalplanetary pages 31-35). Zhang et al. (2025) showed that compressive stiffness grows with bar cross-sectional area but with diminishing returns beyond 600 mm², and that cable prestress improves cushioning up to a peak at ~1.5ε before declining (zhang2025designandcushioning pages 19-21, zhang2025designandcushioning pages 14-16). Vespignani et al. (2018) validated SUPERball v2 locomotion and compliance at scale. The ask is: how many orientations, scales, and repeats are needed before claiming "omnidirectional" or "isotropic enough" behavior for a printable Snelson-class design?

### Cluster 6: Floor-Contact Stiffness Dominance and Sim-to-Real Gap

Zha et al. (2024) modeled their collision-resilient icosahedron tensegrity drone as point masses in a network of spring-damper rods, using Monte Carlo randomized collision orientations against a wall with specified stiffness ko, and found that the tensegrity shell disperses loads as tension/compression rather than bending (zha2024designandcontrol pages 4-5, zha2024designandcontrol pages 2-3). This supports your observation that floor-contact stiffness may swamp cable-stiffness effects. Wang et al. (2021) showed that a differentiable tensegrity-specific simulator can learn approximate contact dynamics with very limited ground-truth data (wang2021sim2simevaluationof pages 7-8). The ask is how to separate structure-driven attenuation from test-surface artifacts and whether a learned or differentiable contact model is the most practical path.

### Cluster 7: TPU 85A Creep/Prestress Drift and FFF Joint Reliability

Printed TPU shows substantial stress relaxation—approximately 40–50% stress drop during multi-hour holds, with equilibrium not reached within 12 hours (paiva2023experimentalinvestigationof pages 149-154). Bruère et al. (2023) found that contour lines are essential for part integrity and that alternating infill orientations improve structural consistency, while fully unidirectional 90° prints without outlines suffer delamination and reduced tensile strength (bruere2023theinfluenceof pages 1-2, paiva2023experimentalinvestigationof pages 250-251). Skelton & Oliveira (2009) formalize prestress as a structural state variable that determines both stiffness and stability (oliveira2009tensegritysystems pages 1-15). The implication is that drop-to-drop prestress drift may be one of the biggest hidden variables in both crutch-tip and egg-drop testing, and prestress should be treated as a measured, refreshable state rather than a fixed design input.

---

## (b) Tech-Transfer / Commercialization Angles

1. **NASA NIAC/SBIR/STTR Successor:** The SUPERball NIAC Phase 2 program (Agogino, SunSpiral & Atkinson 2018) established tensegrity planetary landers as a credible NASA concept (sunspiral2015superballbotstructures pages 80-83). A printable, BO-optimized tensegrity demonstrator could be positioned as a low-cost rapid-prototyping complement to future NIAC proposals, or as an SBIR/STTR topic in "Entry, Descent, and Landing Systems" or "Autonomous Systems for Space Exploration."

2. **DoT/FAA Drone-Cargo Airdrop:** Mueller's collision-resilient tensegrity drone work (zha2024designandcontrol pages 9-11, zha2024designandcontrol pages 1-2) and Anand's humanitarian delivery demonstration (anand2212takingoffwith pages 1-2) together define a clear drone-cargo airdrop pathway. A reusable, printable tensegrity impact absorber rated to specific h_crit values could serve as a certifiable cargo-protection module for last-mile drone delivery.

3. **Biomedical Orthotics OEMs:** The crutch-tip / impact-absorber thread maps directly onto assistive-device markets. PETG-TPU multi-material printing on an IDEX platform like the Bambu H2D could enable patient-specific geometry and tunable compliance, positioned as a custom orthotic component with quasi-static and impact-rated performance data.

4. **Defense-Payload Landers:** TANDEM's 38% mass reduction versus ADEPT-VITaL (bayandor2017lightweightmultifunctionalplanetary pages 1-5, bayandor2017lightweightmultifunctionalplanetarya pages 1-5) and the linear velocity-mass scaling relationship provide a template for positioning printable tensegrities as low-cost, expendable payload protection for military airdrop applications.

5. **IEEE Spectrum / Scientific American Demo:** The egg-drop benchmark is inherently media-friendly. A Bruceton-staircase-validated, BO-optimized, FFF-printed tensegrity egg-drop demonstration with a GitHub-reproducible BO loop would be an excellent candidate for a public-facing demonstration piece.

6. **STEM Education / Capstone Kits:** The combination of printable hardware, open-source BO loop, and a standardized egg-drop protocol has natural appeal as a university capstone or maker-community project.

---

## (c) Immediate "Gotchas" an Experienced Practitioner Is Most Likely to Flag

1. **Floor-contact stiffness swamps cable signal.** As observed in your simulations and consistent with Zha et al. (2024), the contact model between the tensegrity and the impact surface often dominates peak-g predictions, making cable-stiffness effects secondary (zha2024designandcontrol pages 4-5). Any quantitative peak-g claim requires specifying floor stiffness, coefficient of restitution, and contact model.

2. **TPU 85A creep will shift prestress between drops.** Stress relaxation of ~40–50% over hours has been measured in FFF-printed TPU (paiva2023experimentalinvestigationof pages 149-154), meaning that prestress in tendons will drift significantly between drops and within a Bruceton staircase sequence. Without measuring and resetting prestress, N_reuse and h_crit data will conflate structural degradation with viscoelastic drift.

3. **Bambu H2D filament-swap interface is the most likely failure mode.** Multi-material FFF interface adhesion is geometry- and process-dependent, and no standardized test exists (lopes2024interfaceboundarymechanical pages 37-40). The PETG-TPU interface is untested in the literature; the joint geometry (barbed/dovetail/anchor-bulb) will likely fail before bulk material, making interface characterization the critical-path experiment.

4. **Bruceton staircase needs randomized orientations to be defensible.** Bayandor's TANDEM orientation-sweep study showed that peak g varies dramatically with impact orientation, with some outlier orientations producing nearly double the median acceleration (bayandor2017lightweightmultifunctionalplanetary pages 31-35). A Bruceton protocol that does not randomize orientation at each step will measure a biased h_crit.

5. **Tensegrity classification (class-1 vs. class-2) depends on strut closest-approach distance.** Skelton's formal definition requires that class-1 structures have no compressive members touching at any node (goyal2019tensegritysystemdynamics pages 1-3, williamson2003generalclassof pages 1-2). If your PETG struts contact each other through printed geometry (e.g., at node junctions), you may technically have a class-k structure, which changes the applicable equilibrium and stability theory.

6. **Rigid-strut simulations cannot predict post-buckling energy storage.** Garanger et al. (2021) showed that post-buckling behavior of compression members is a key energy-storage mechanism in tensegrity landing (garanger2021softtensegritysystems pages 12-14), and Bayandor's work confirmed that beam-element FEM was infeasible for impact kinematics due to numerical noise (bayandor2017lightweightmultifunctionalplanetary pages 24-27). Rigid models are conservative first-pass tools but should not be trusted for SEA or energy-partition claims.

7. **Print orientation and infill of PETG struts will dominate strut buckling behavior.** PETG is anisotropic as-printed; buckling critical load (Euler Pcr) depends on effective cross-section and interlayer adhesion, not just nominal geometry. SUPERball v2 hardware testing revealed that even machined Delrin components failed at flanges under impact (sabelhaus2014hardwaredesignand pages 8-10).

---

## (d) Collaborative Contribution Mechanisms

1. **External validation against published datasets:** Request access to Zhang et al. (2022) lander drop-test accelerometer traces and Bayandor TANDEM 1/3-scale prototype data (schroeder2017acomprehensiveentry pages 98-102) for sim-vs-experiment comparison.

2. **Inter-lab specimen exchange:** Send printed PETG-TPU tensegrity specimens to Zhang (Harbin) and Vespignani for testing on their existing instrumented drop setups; receive cable-actuated SUPERball v2 hardware data in return.

3. **Instrument-time swaps:** Offer Bambu H2D IDEX printing capacity in exchange for access to drop towers (e.g., Lansmont M23) or laser Doppler vibrometry (Polytec / QTec LDV) for high-speed deformation measurement.

4. **Shared standardized egg-drop benchmark protocol:** Co-develop with Zhang, Anand, and Cera a Bruceton-staircase egg-drop protocol specifying orientation randomization, step size, binary failure criterion, and instrumentation requirements. Publish as a standalone methods paper.

5. **GitHub-hosted reproducible BO loop:** Release the full Bayesian optimization code, geometry parameterization, and Bruceton analysis scripts as an open-source repository. Invite co-authorship from researchers who contribute validation data or alternative acquisition functions.

6. **Co-supervised undergraduate / capstone projects:** Propose joint capstone or REU projects with Rimoli (Georgia Tech), Mueller (UC Berkeley), or Skelton (TAMU) focused on specific sub-problems (e.g., PETG-TPU interface testing, DiffPD tensegrity impact validation, prestress monitoring).

7. **Joint conference workshop or invited session:** Propose an AIAA SciTech or IEEE IROS special session on "Printable Tensegrity Structures for Impact Absorption: From Planetary Landers to Terrestrial Applications," co-organized with Rimoli, Agogino, and Mueller.

8. **Cross-citation in revision:** Offer explicit cross-citation of each contact's work in your next submission in exchange for review feedback on the manuscript draft.

---

## (e) Per-Contact Recommendations

The following table provides the specific recommended ask(s) for each named contact, anchored to their own published work.

| Contact Name | Affiliation | Recommended Ask(s) from (a)-(d) | Anchoring Publication | Specific Rationale |
|---|---|---|---|---|
| Julian Rimoli | Georgia Tech | (a) FFF tensegrity impact-mechanics fidelity gap; (a) BO acquisition function for noisy impact objectives; (d) co-supervised capstone / shared simulator configs | Rimoli & Pal, *Mechanical Response of 3-Dimensional Tensegrity Lattices* (2017); Garanger et al., *Soft Tensegrity Systems for Planetary Landing and Exploration* (2021) (garanger2021softtensegritysystems pages 12-14) | Best fit for advice on where reduced-order / rigid-member models stop being predictive, especially once post-buckling energy storage matters. His group’s planetary-landing and flexible-tensegrity work makes him the strongest contact for “what simulation fidelity is enough to trust BO outputs?” |
| Adrian Agogino | NASA Ames | (a) BO acquisition function / experimental design; (b) NIAC/SBIR successor and NASA transition path; (d) shared benchmark protocol | Agogino, SunSpiral & Atkinson, *Super Ball Bot-structures for Planetary Landing and Exploration* (2018); Caluwaerts, Agogino & SunSpiral, *SUPERball: Exploring Tensegrities for Planetary Probes* (2014) | As PI in the SUPERball lineage, he is the right person to ask how to frame a reusable printable tensegrity as a serious NASA-adjacent platform rather than a one-off demo. He is also well placed to advise on a benchmark that is useful both scientifically and programmatically. |
| Vytas SunSpiral | formerly NASA Ames | (a) Simulation-fidelity gap; (d) shared NTRT / legacy simulation configs and sim-to-real lessons | SunSpiral et al., *Super Ball Bot-structures for Planetary Landing and Exploration, NIAC Phase 2 Final Report* (2015); Bruce et al., *Design and Evolution of a Modular Tensegrity Robot Platform* (2014) (sunspiral2015superballbotstructures pages 80-83) | He co-developed both the SUPERball hardware stack and the simulation ecosystem around it, so he is uniquely credible on what abstractions were “good enough” in practice. If anyone can quickly flag whether your MuJoCo/PyBullet results are artifact-dominated, it is likely SunSpiral. |
| Mark Mueller | UC Berkeley HiPeRLab | (a) Floor-contact stiffness dominance; (a) TPU creep / joint reliability as hidden state variables; (b) drone cargo / collision-resilient deployment angle; (d) inter-lab instrument-time swap | Zha et al., *Design and Control of a Collision-Resilient Aerial Vehicle With an Icosahedron Tensegrity Structure* (2024) (zha2024designandcontrol pages 4-5, zha2024designandcontrol pages 9-11, zha2024designandcontrol pages 2-3, zha2024designandcontrol pages 1-2) | His collision-resilient tensegrity drone is the closest published analog to your “reusable, omnidirectional, impact-tolerant” objective, especially because it connects structural design to post-impact recovery. He is also a natural contact for translating the work toward drone-drop logistics and robust test instrumentation. |
| Andrew Zhang | UC Berkeley / Agogino lineage | (a) Bruceton h_crit benchmark transferability; (d) shared benchmark protocol; (d) GitHub BO loop / dataset comparison | Zhang et al., *Badminton-Inspired Self-Righting Tensegrity Landers* (2022) | Best contact for making your egg-drop thread comparable to the Berkeley self-righting lander lineage. Ask specifically how to define binary failure, orientation randomization, and instrumentation so h_crit can be defended as a transferable benchmark. |
| Brian Cera | UC Berkeley / Agogino lineage | (a) Bruceton benchmark transferability; (d) shared benchmark protocol; (d) GitHub BO loop / dataset comparison | Chen et al., *Inclined Surface Locomotion Strategies for Spherical Tensegrity Robots* (2017) | Cera is a good adjacent contact because he sits inside the SUPERball / Berkeley tensegrity experimental tradition and can likely comment on practical test design, actuation simplifications, and reproducibility. He is also a plausible bridge for specimen exchange or revisiting Berkeley instrumentation conventions. |
| Massimo Vespignani | NASA / SUPERball v2 lineage | (a) Scaling and orientation-isotropy validation; (d) inter-lab specimen exchange; (d) cross-citation / revision feedback | Vespignani et al., *Steerable Locomotion Controller for Six-strut Icosahedral Tensegrity Robots* (2018); SUPERball v2 impact-absorbing design lineage (zhang2025designandcushioning pages 19-21) | Because SUPERball v2 was explicitly framed around compliant operation and large-impact absorption, Vespignani is ideal for asking what counts as a meaningful comparison against cable-actuated hardware. He is also a strong fit for questions about orientation coverage and whether your printable design is “isotropic enough” to justify omnidirectional claims. |
| Robert Skelton | Texas A&M | (a) TPU creep / prestress drift; (a) class-1 vs class-2 classification; (d) cross-citation in revision | Skelton & Oliveira, *Tensegrity Systems* (2009); Williamson & Skelton, *General Class of Tensegrity Structures: Topology and Prestress Equilibrium Analysis* (2003) (goyal2019tensegritysystemdynamics pages 1-3, williamson2003generalclassof pages 1-2, oliveira2009tensegritysystems pages 1-15) | He is the foundational contact for topology, prestress, and tensegrity classification, so he is the right person to ask whether your structure is being labeled correctly and whether prestress is being treated rigorously. He is also a strong authority for interpreting drift in prestress as a structural-state issue rather than just a materials nuisance. |
| Cornel Sultan | Virginia Tech | (a) TPU creep / prestress drift; (a) class-1 vs class-2 classification; (d) cross-citation in revision | Williamson, Skelton & Han, *Equilibrium Conditions of Class 1 Tensegrity Structures* (2003) (williamson2003equilibriumconditionsof pages 19-20) | Sultan is especially well matched for equilibrium, prestress, and foldable/deployable tensegrity interpretation, making him a strong theory-side validator of your topology and pretension assumptions. A concise ask here is “are we even parameterizing the right prestress space for a printable Snelson-class impact absorber?” |
| Jamshid Bayandor | Virginia Tech CRASH Lab | (a) Scaling / orientation-isotropy validation; (a) simulation-fidelity gap; (d) shared drop-test methodology | Bayandor et al., *Lightweight Multifunctional Planetary Probe for Extreme Environment Exploration and Locomotion* (2017) (bayandor2017lightweightmultifunctionalplanetary pages 1-5, bayandor2017lightweightmultifunctionalplanetary pages 24-27, bayandor2017lightweightmultifunctionalplanetary pages 31-35, bayandor2017lightweightmultifunctionalplanetarya pages 31-35, bayandor2017lightweightmultifunctionalplanetarya pages 24-27) | Bayandor’s TANDEM work is directly relevant because it couples scaled-up tensegrity landing concepts with broad orientation sweeps and explicit impact-model simplifications. He is therefore the best person to ask how many orientations, what model fidelity, and what validation ladder are needed before impact claims are publishable. |
| Jing Zhang | Harbin Institute of Technology | (a) Scaling / orientation-isotropy validation; (d) inter-lab specimen exchange; (d) experimental egg-drop protocol | Zhang et al., *Design and Cushioning Performance Analysis of Spherical Tensegrity Structures* (2025) (zhang2025designandcushioning pages 1-2, zhang2025designandcushioning pages 19-21, zhang2025designandcushioning pages 18-19, zhang2025designandcushioning pages 12-14, zhang2025designandcushioning pages 14-16, zhang2025designandcushioning pages 2-4) | This is the most recent experimentally validated cushioning paper in the lander-adjacent literature, and it directly studies prestress, bar area, damping, rebound, and egg-payload protection. Ask for advice on which of their parameter sweeps and experimental observables would transfer cleanly into a printable egg-drop benchmark. |
| Madhumati Anand | independent / humanitarian delivery context | (a) Bruceton h_crit benchmark; (a) PETG-TPU interface and reusable-joint design; (b) humanitarian drone-delivery angle; (d) shared benchmark protocol | Anand et al., *Taking Off With Biodegradable Tensegrities: An Eco-friendly Emergency Medical Delivery Solution* (2022) (anand2212takingoffwith pages 1-2) | Anand is the only published contact in your set with a 75 m tensegrity drop-delivery demonstration, so she is the best comparator for height-driven humanitarian relevance. Her reported 4–5 drop reuse limit is exactly the opening to position your PETG/TPU printable system as a reusable successor rather than a competing one-off concept. |


*Table: This table maps each outreach contact to the highest-leverage asks, the publication you should cite to personalize the email, and the specific reason that person is especially well matched to your current technical gaps.*

---

## Stretch Section: Collaborative-Contribution Mechanisms You Might Not Have Considered

1. **Digital-twin round-robin:** Establish a "tensegrity impact digital twin challenge" where each lab submits a simulation prediction for a standardized printed specimen before physical testing. This mirrors the NIST AM-Bench approach and would generate a high-value comparative dataset. Wang et al. (2021) demonstrated that even a tensegrity-specific differentiable simulator trained on 0.25% of ground-truth data can produce transferable policies (wang2021sim2simevaluationof pages 7-8), suggesting that even labs without physical test capacity could contribute simulation predictions.

2. **Materials-genome integration:** Connect your PETG-TPU interface characterization to the broader multi-material FFF community by structuring bond-strength data in a format compatible with materials databases. This would address the standardization gap noted by Lopes (2024), where no consensus test method exists for multi-material FFF interlayer bonding (lopes2024interfaceboundarymechanical pages 37-40).

3. **Citizen-science egg-drop campaign:** Leverage the educational appeal of the egg-drop benchmark by creating a downloadable STL/3MF kit with standardized printing instructions for commodity IDEX printers. Aggregate h_crit data from multiple sites to build a statistically powerful dataset at minimal per-lab cost.

4. **Prestress-monitoring IoT integration:** Embed low-cost strain gauges or piezoresistive elements in TPU tendons to create a "smart tensegrity" that reports real-time prestress state. This addresses the creep/drift gotcha directly and could produce a novel sensor-fusion dataset for differentiable-simulator calibration.

5. **Topology-optimization collaboration with computational-mechanics groups:** The BO loop over topology could be supplemented by inviting computational mechanics groups (e.g., Panozzo's PolyFEM team) to contribute topology-optimized node geometries from their differentiable solvers (huang2024differentiablesolverfor pages 2-3, huang2024differentiablesolverfor pages 14-16, huang2024differentiablesolverfor pages 17-19), creating a parallel "design-by-analysis" track alongside the experimental BO track.

6. **ASTM / ISO standards pathway:** Engage with ASTM F42 (Additive Manufacturing) and ASTM D20 (Plastics) subcommittees to propose a standard test method for multi-material FFF interface bond strength in impact-loaded applications, leveraging the PETG-TPU characterization data as a pilot case.

7. **Cross-domain patent landscape scan:** The barbed/dovetail/anchor-bulb PETG-TPU joint geometries may have patentable novelty if the PETG-TPU material pair is genuinely uncharacterized. A freedom-to-operate search focused on multi-material FFF joint designs could identify both IP opportunities and constraints before publication.

8. **High-speed video sharing consortium:** Bayandor's TANDEM validation used 1/3-scale drop tests (schroeder2017acomprehensiveentry pages 98-102), and Zhang et al. (2025) used experimental models with egg payloads (zhang2025designandcushioning pages 18-19). Establishing a shared high-speed video repository with synchronized accelerometer data would enable cross-lab validation of contact dynamics and deformation modes that are difficult to capture from publications alone.


References

1. (garanger2021softtensegritysystems pages 12-14): Kévin Garanger, Isaac del Valle, Miriam Rath, Matthew Krajewski, Utkarsh Raheja, Marco Pavone, and Julian J. Rimoli. Soft tensegrity systems for planetary landing and exploration. Earth and Space 2021, pages 841-854, Apr 2021. URL: https://doi.org/10.1061/9780784483374.078, doi:10.1061/9780784483374.078. This article has 30 citations.

2. (du2021diffpddifferentiableprojective pages 1-2): Tao Du, Kui Wu, Pingchuan Ma, Sebastien Wah, Andrew Spielberg, Daniela Rus, and Wojciech Matusik. Diffpd: differentiable projective dynamics. ACM Transactions on Graphics, 41:1-21, Nov 2021. URL: https://doi.org/10.1145/3490168, doi:10.1145/3490168. This article has 197 citations and is from a highest quality peer-reviewed journal.

3. (huang2024differentiablesolverfor pages 2-3): Zizhou Huang, Davi Colli Tozoni, Arvi Gjoka, Zachary Ferguson, Teseo Schneider, Daniele Panozzo, and Denis Zorin. Differentiable solver for time-dependent deformation problems with contact. ACM Transactions on Graphics, 43:1-30, May 2024. URL: https://doi.org/10.1145/3657648, doi:10.1145/3657648. This article has 39 citations and is from a highest quality peer-reviewed journal.

4. (bayandor2017lightweightmultifunctionalplanetary pages 24-27): J Bayandor, K Schroeder, and J Samareh. Lightweight multifunctional planetary probe for extreme environment exploration and locomotion. Unknown journal, 2017.

5. (lopes2024interfaceboundarymechanical pages 37-40): LMA Lopes. Interface boundary mechanical resistance analysis in fff multi-material parts. Unknown journal, 2024.

6. (anand2212takingoffwith pages 1-2): Madhumati Anand, Vyzag Ajith, and Sanjula Sreekumar. Taking off with biodegradable tensegrities: an eco-friendly emergency medical delivery solution. ArXiv, Dec 2212. URL: https://doi.org/10.48550/arxiv.2212.11625, doi:10.48550/arxiv.2212.11625. This article has 2 citations.

7. (goyal2019tensegritysystemdynamics pages 1-3): Raman Goyal and Robert E. Skelton. Tensegrity system dynamics with rigid bars and massive strings. Multibody System Dynamics, 46:203-228, Feb 2019. URL: https://doi.org/10.1007/s11044-019-09666-4, doi:10.1007/s11044-019-09666-4. This article has 83 citations and is from a domain leading peer-reviewed journal.

8. (bayandor2017lightweightmultifunctionalplanetary pages 31-35): J Bayandor, K Schroeder, and J Samareh. Lightweight multifunctional planetary probe for extreme environment exploration and locomotion. Unknown journal, 2017.

9. (zhang2025designandcushioning pages 19-21): Jing Zhang, Chuang Shi, Kun Geng, Yanzheng Chen, Hongwei Guo, Rongqiang Liu, and Ziming Kou. Design and cushioning performance analysis of spherical tensegrity structures. Aerospace, 12:453, May 2025. URL: https://doi.org/10.3390/aerospace12060453, doi:10.3390/aerospace12060453. This article has 2 citations.

10. (zhang2025designandcushioning pages 18-19): Jing Zhang, Chuang Shi, Kun Geng, Yanzheng Chen, Hongwei Guo, Rongqiang Liu, and Ziming Kou. Design and cushioning performance analysis of spherical tensegrity structures. Aerospace, 12:453, May 2025. URL: https://doi.org/10.3390/aerospace12060453, doi:10.3390/aerospace12060453. This article has 2 citations.

11. (zha2024designandcontrol pages 9-11): Jiaming Zha, Xiangyu Wu, Ryan Dimick, and Mark W. Mueller. Design and control of a collision-resilient aerial vehicle with an icosahedron tensegrity structure. IEEE/ASME Transactions on Mechatronics, 29:3449-3460, Oct 2024. URL: https://doi.org/10.1109/tmech.2023.3346749, doi:10.1109/tmech.2023.3346749. This article has 24 citations.

12. (wang2021sim2simevaluationof pages 1-2): Kun Wang, Mridul Aanjaneya, and Kostas E. Bekris. Sim2sim evaluation of a novel data-efficient differentiable physics engine for tensegrity robots. 2021 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), pages 1694-1701, Sep 2021. URL: https://doi.org/10.1109/iros51168.2021.9636783, doi:10.1109/iros51168.2021.9636783. This article has 31 citations.

13. (bruere2023theinfluenceof pages 1-2): V. M. Bruère, A. Lion, J. Holtmannspötter, and M. Johlitz. The influence of printing parameters on the mechanical properties of 3d printed tpu-based elastomers. Progress in Additive Manufacturing, 8:693-701, Mar 2023. URL: https://doi.org/10.1007/s40964-023-00418-7, doi:10.1007/s40964-023-00418-7. This article has 58 citations and is from a peer-reviewed journal.

14. (oliveira2009tensegritysystems pages 1-15): Mauricio C. Oliveira and Robert E. Skelton. Tensegrity Systems. Springer US, Jan 2009. URL: https://doi.org/10.1007/978-0-387-74242-7, doi:10.1007/978-0-387-74242-7.

15. (schroeder2017acomprehensiveentry pages 90-94): KK Schroeder. A comprehensive entry, descent, landing, and locomotion (edll) vehicle for planetary exploration. Unknown journal, 2017.

16. (du2021diffpddifferentiableprojective pages 9-11): Tao Du, Kui Wu, Pingchuan Ma, Sebastien Wah, Andrew Spielberg, Daniela Rus, and Wojciech Matusik. Diffpd: differentiable projective dynamics. ACM Transactions on Graphics, 41:1-21, Nov 2021. URL: https://doi.org/10.1145/3490168, doi:10.1145/3490168. This article has 197 citations and is from a highest quality peer-reviewed journal.

17. (huang2024differentiablesolverfor pages 14-16): Zizhou Huang, Davi Colli Tozoni, Arvi Gjoka, Zachary Ferguson, Teseo Schneider, Daniele Panozzo, and Denis Zorin. Differentiable solver for time-dependent deformation problems with contact. ACM Transactions on Graphics, 43:1-30, May 2024. URL: https://doi.org/10.1145/3657648, doi:10.1145/3657648. This article has 39 citations and is from a highest quality peer-reviewed journal.

18. (wang2021sim2simevaluationof pages 7-8): Kun Wang, Mridul Aanjaneya, and Kostas E. Bekris. Sim2sim evaluation of a novel data-efficient differentiable physics engine for tensegrity robots. 2021 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), pages 1694-1701, Sep 2021. URL: https://doi.org/10.1109/iros51168.2021.9636783, doi:10.1109/iros51168.2021.9636783. This article has 31 citations.

19. (zhang2025designandcushioning pages 14-16): Jing Zhang, Chuang Shi, Kun Geng, Yanzheng Chen, Hongwei Guo, Rongqiang Liu, and Ziming Kou. Design and cushioning performance analysis of spherical tensegrity structures. Aerospace, 12:453, May 2025. URL: https://doi.org/10.3390/aerospace12060453, doi:10.3390/aerospace12060453. This article has 2 citations.

20. (zha2024designandcontrol pages 4-5): Jiaming Zha, Xiangyu Wu, Ryan Dimick, and Mark W. Mueller. Design and control of a collision-resilient aerial vehicle with an icosahedron tensegrity structure. IEEE/ASME Transactions on Mechatronics, 29:3449-3460, Oct 2024. URL: https://doi.org/10.1109/tmech.2023.3346749, doi:10.1109/tmech.2023.3346749. This article has 24 citations.

21. (zha2024designandcontrol pages 2-3): Jiaming Zha, Xiangyu Wu, Ryan Dimick, and Mark W. Mueller. Design and control of a collision-resilient aerial vehicle with an icosahedron tensegrity structure. IEEE/ASME Transactions on Mechatronics, 29:3449-3460, Oct 2024. URL: https://doi.org/10.1109/tmech.2023.3346749, doi:10.1109/tmech.2023.3346749. This article has 24 citations.

22. (paiva2023experimentalinvestigationof pages 149-154): VMB de Carvalho Paiva. Experimental investigation of the thermomechanical properties and suitability of elastomers from additive manufacturing. Unknown journal, 2023.

23. (paiva2023experimentalinvestigationof pages 250-251): VMB de Carvalho Paiva. Experimental investigation of the thermomechanical properties and suitability of elastomers from additive manufacturing. Unknown journal, 2023.

24. (sunspiral2015superballbotstructures pages 80-83): V SunSpiral, A Agogino, and D Atkinson. Super ball bot-structures for planetary landing and exploration, niac phase 2 final report. Unknown journal, 2015.

25. (zha2024designandcontrol pages 1-2): Jiaming Zha, Xiangyu Wu, Ryan Dimick, and Mark W. Mueller. Design and control of a collision-resilient aerial vehicle with an icosahedron tensegrity structure. IEEE/ASME Transactions on Mechatronics, 29:3449-3460, Oct 2024. URL: https://doi.org/10.1109/tmech.2023.3346749, doi:10.1109/tmech.2023.3346749. This article has 24 citations.

26. (bayandor2017lightweightmultifunctionalplanetary pages 1-5): J Bayandor, K Schroeder, and J Samareh. Lightweight multifunctional planetary probe for extreme environment exploration and locomotion. Unknown journal, 2017.

27. (bayandor2017lightweightmultifunctionalplanetarya pages 1-5): J Bayandor, K Schroeder, and J Samareh. Lightweight multifunctional planetary probe for extreme environment exploration and locomotion. Unknown journal, 2017.

28. (williamson2003generalclassof pages 1-2): Darrell Williamson and Robert E. Skelton. General class of tensegrity structures: topology and prestress equilibrium analysis. Journal of Guidance Control and Dynamics, 26:685-694, Sep 2003. URL: https://doi.org/10.2514/2.5119, doi:10.2514/2.5119. This article has 14 citations and is from a domain leading peer-reviewed journal.

29. (sabelhaus2014hardwaredesignand pages 8-10): AP Sabelhaus, J Bruce, and K Caluwaerts. Hardware design and testing of superball, a modular tensegrity robot. Unknown journal, 2014.

30. (schroeder2017acomprehensiveentry pages 98-102): KK Schroeder. A comprehensive entry, descent, landing, and locomotion (edll) vehicle for planetary exploration. Unknown journal, 2017.

31. (williamson2003equilibriumconditionsof pages 19-20): Darrell Williamson, Robert E. Skelton, and JeongHeon Han. Equilibrium conditions of class 1 tensegrity structures. Revue Française de Génie Civil, 7:291-310, Mar 2003. URL: https://doi.org/10.1080/12795119.2003.9692496, doi:10.1080/12795119.2003.9692496. This article has 11 citations.

32. (bayandor2017lightweightmultifunctionalplanetarya pages 31-35): J Bayandor, K Schroeder, and J Samareh. Lightweight multifunctional planetary probe for extreme environment exploration and locomotion. Unknown journal, 2017.

33. (bayandor2017lightweightmultifunctionalplanetarya pages 24-27): J Bayandor, K Schroeder, and J Samareh. Lightweight multifunctional planetary probe for extreme environment exploration and locomotion. Unknown journal, 2017.

34. (zhang2025designandcushioning pages 1-2): Jing Zhang, Chuang Shi, Kun Geng, Yanzheng Chen, Hongwei Guo, Rongqiang Liu, and Ziming Kou. Design and cushioning performance analysis of spherical tensegrity structures. Aerospace, 12:453, May 2025. URL: https://doi.org/10.3390/aerospace12060453, doi:10.3390/aerospace12060453. This article has 2 citations.

35. (zhang2025designandcushioning pages 12-14): Jing Zhang, Chuang Shi, Kun Geng, Yanzheng Chen, Hongwei Guo, Rongqiang Liu, and Ziming Kou. Design and cushioning performance analysis of spherical tensegrity structures. Aerospace, 12:453, May 2025. URL: https://doi.org/10.3390/aerospace12060453, doi:10.3390/aerospace12060453. This article has 2 citations.

36. (zhang2025designandcushioning pages 2-4): Jing Zhang, Chuang Shi, Kun Geng, Yanzheng Chen, Hongwei Guo, Rongqiang Liu, and Ziming Kou. Design and cushioning performance analysis of spherical tensegrity structures. Aerospace, 12:453, May 2025. URL: https://doi.org/10.3390/aerospace12060453, doi:10.3390/aerospace12060453. This article has 2 citations.

37. (huang2024differentiablesolverfor pages 17-19): Zizhou Huang, Davi Colli Tozoni, Arvi Gjoka, Zachary Ferguson, Teseo Schneider, Daniele Panozzo, and Denis Zorin. Differentiable solver for time-dependent deformation problems with contact. ACM Transactions on Graphics, 43:1-30, May 2024. URL: https://doi.org/10.1145/3657648, doi:10.1145/3657648. This article has 39 citations and is from a highest quality peer-reviewed journal.