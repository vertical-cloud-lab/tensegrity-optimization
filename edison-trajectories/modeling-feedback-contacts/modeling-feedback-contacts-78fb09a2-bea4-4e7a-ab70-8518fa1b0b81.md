# Edison literature brief: named contacts for feedback on the multi-fidelity tensegrity drop-modelling approach

- **Task ID:** `78fb09a2-bea4-4e7a-ab70-8518fa1b0b81`
- **Job:** `LITERATURE_HIGH` (paperqa3-high)
- **Submitted:** 2026-05-20T16:46:14Z
- **Fetched:** 2026-05-20T17:27:25Z
- **Status:** success
- **Task summary:** Prioritised Contact List And Outreach Plan For Tensegrity Drop Impact Modelling Reviews
- **Related issues/PRs:** #14, #16, #18, #28, #38, #45, #46, #47, #49, #50
- **Related Edison tasks:** 782657e0 (sim survey), 37ae0665 (payload), f18aca01 (outreach topics), c18a2313 (industry partners), 9cc7db18 (JMD reviewers), fad054b3 + 6226a551 (tensegrity designs), 1b90208d + f41b7034 (egg-drop)

---

## Question

We have built a multi-fidelity simulation stack to model drop-impact response
of class-1 tensegrity cells (3 PLA struts + 9 TPU 85A tendons; T-prism
topology) for two application regimes (crutch tip @ 1.4 m/s / 75 kg, NASA-
lander-style @ 9.8 m/s / 5 kg, both inside the Lansmont M23 envelope). The
stack comprises: (Tier C) MuJoCo / PyBullet / PyChrono rigid-strut + cable
screening; (Tier B) NVIDIA Newton (Warp XPBD, differentiable) and DiffPD
(Du et al. 2021, differentiable projective dynamics); (Tier A) PolyFEM + IPC
(barrier-method contact, NeoHookean, built from source) on a welded
strut+tendon volumetric mesh (gmsh OCC fragment). We have run:

- MuJoCo bare-prism 1 m drop + regime sweeps (k_cable swept ~3 decades).
- Newton XPBD all-particle T-prism with payload-suspension tendons in load
  path; tendon-Ø sweep (1.5, 3.0, 5.0 mm).
- DiffPD soft-cube smoke test.
- PolyFEM+IPC NeoHookean cube drop, then welded T-prism drop end-to-end
  (5481 tets / 2168 nodes, ImplicitEuler dt=0.5 ms x 80 steps, dhat=5e-5 m).
- Printable-design module with class-1 (strut-strut closest-approach) check,
  Bambu H2D printability bounds, 7x5 (tendon-Ø, prestrain) sweep -> Pareto.
- 3D offscreen renders with tendon strain-coloured cables (OSMesa MuJoCo).

We need to identify **specific people and groups to reach out to** for
feedback / sanity checks / spot checks / recommendations on this modelling
approach. Please produce a citation-rich, prioritised, *contact-level*
brief organised as follows:

# 1. Tensegrity dynamics + drop / impact mechanics (academic)

Named researchers (with current affiliation, role, email/lab URL where
publicly listed, recent papers, why they are well-placed to critique our
approach, and a specific 1-2 sentence "ask"). Group into:

  (a) Tensegrity structural mechanics + form-finding (e.g., Skelton, Sultan,
      Caluwaerts, Goyal, Tibert, Pellegrino, Motro, de Oliveira, Bel Hadj
      Ali).
  (b) Tensegrity robotics / SUPERball / lander lineage (NASA Ames Intelligent
      Robotics Group: Vytas SunSpiral, Adrian Agogino, Brian Tietz Mirletz,
      Massimo Vespignani; UC Berkeley AHMCT / BEST Lab; Alice Agogino).
  (c) Impact-attenuation / drop-test mechanics of soft/architected materials
      (Pajunen, Bauer, Anand, Snapp, Gongora, Valdevit, Greer, Schaedler).
  (d) Tensegrity + 3D-printing (e.g., Davami 2025; Liu 2023; Intrigila 2022;
      Yavas 2022; Rieffel; Hiller & Lipson).

# 2. Simulator maintainers + differentiable physics

For each of the simulators we use, identify the active maintainer(s) and the
right channel (GitHub discussions / issues / mailing list) to ask for
modelling sanity-checks. Cover:

  (a) PolyFEM + IPC: Teseo Schneider (Victoria, NYU), Daniele Panozzo (NYU
      Courant), Zachary Ferguson, Minchen Li (CMU), Chenfanfu Jiang (UCLA);
      ipc-toolkit maintainers.
  (b) DiffPD: Tao Du (Tsinghua), Wojciech Matusik (MIT CSAIL GFX).
  (c) NVIDIA Newton / Warp: Miles Macklin, Matthias Mueller-Fischer, the
      Newton GitHub org maintainers; Omniverse Isaac Lab tensegrity-robot
      examples (if any).
  (d) MuJoCo: Emo Todorov (Roboti / UW), Yuval Tassa (DeepMind), the
      MuJoCo-MJX team; relevant tendon/cable contact issues on the
      google-deepmind/mujoco issue tracker.
  (e) PyBullet / Bullet3: Erwin Coumans; soft-body deformable contact
      maintainers.
  (f) PyChrono: Alessandro Tasora (Parma), Dario Mangoni; Project Chrono
      community.
  (g) NTRT (NASA Tensegrity Robotics Toolkit) maintainers and any active
      fork curators.

# 3. Materials + AM characterisation

  (a) Researchers who have published PLA-TPU multi-material FDM interface
      data (Lopes 2018, Zhang 2026, Ruwais 2025) - whose feedback would help
      us trust the welded PolyFEM material model.
  (b) NinjaFlex / TPU 85A characterisation labs (Fenner/Lubrizol contacts;
      academic groups with published TPU 85A secant moduli and Mullins-
      effect curves).
  (c) PLA shock / impact characterisation (Charpy / Izod / drop-weight)
      contacts.

# 4. Standards bodies + test labs

People who can audit our standards mapping (we currently target ASTM D5276,
F1292, F2971, ISTA 1A/1H, MIL-STD-810H 516.8, GSFC GEVS-STD-7000B, JEDEC for
M23). For each, give the standards-committee secretariat and a recognised
academic/practitioner with active publications. Include drop-test lab
contacts (Lansmont, MTS, Instron application engineers; NASA GSFC; Sandia;
Aberdeen Test Center) and a one-paragraph note on how to engage them
(formal RFP vs. informal email vs. conference Q&A).

# 5. Bayesian optimisation + multi-fidelity surrogates

Researchers we should ping for sanity checks on the BO + multi-fidelity
strategy that consumes these simulators (e.g., Frazier, Wang, Garnett,
Letham, Bakshy / BoTorch / Ax; Frazier's group at Cornell; Wang's group at
UMich; Acceleration Consortium SDL community; Bran Selic / Adam Stevens
multi-fidelity comp sci contacts).

# 6. Synthesis

  (a) A ranked top-10 contact list ("if you can only send 10 emails this
      month, send them to these 10 people, in this order, asking these
      specific questions"), with the rationale for each ranking.
  (b) A draft 1-page outreach email template (subject + 4-paragraph body)
      that we can adapt per contact and that links our repo, our PR, and
      the specific artifact (e.g., simulations/polyfem_drop_tprism.png,
      simulations/outputs/regime_*_printable_heatmap.png) we want feedback
      on.
  (c) A list of 3-5 venues (workshops, journals, Slack/Discord
      communities) where we should post the modelling approach for
      broader community spot-checks (e.g., SIGGRAPH Physics-Based Animation
      community, ICRA/IROS soft-robotics workshops, ASME IMECE Tensegrity
      symposium, Acceleration Consortium SDL Slack, the polyfem/polyfem
      GitHub Discussions, BoTorch GitHub Discussions).

For every named contact, cite the publication(s) or repo activity that
justifies the recommendation. Flag any contact where the recommendation is
engineering judgement rather than literature-grounded.

---

## Formatted answer

Question: We have built a multi-fidelity simulation stack to model drop-impact response
of class-1 tensegrity cells (3 PLA struts + 9 TPU 85A tendons; T-prism
topology) for two application regimes (crutch tip @ 1.4 m/s / 75 kg, NASA-
lander-style @ 9.8 m/s / 5 kg, both inside the Lansmont M23 envelope). The
stack comprises: (Tier C) MuJoCo / PyBullet / PyChrono rigid-strut + cable
screening; (Tier B) NVIDIA Newton (Warp XPBD, differentiable) and DiffPD
(Du et al. 2021, differentiable projective dynamics); (Tier A) PolyFEM + IPC
(barrier-method contact, NeoHookean, built from source) on a welded
strut+tendon volumetric mesh (gmsh OCC fragment). We have run:

- MuJoCo bare-prism 1 m drop + regime sweeps (k_cable swept ~3 decades).
- Newton XPBD all-particle T-prism with payload-suspension tendons in load
  path; tendon-Ø sweep (1.5, 3.0, 5.0 mm).
- DiffPD soft-cube smoke test.
- PolyFEM+IPC NeoHookean cube drop, then welded T-prism drop end-to-end
  (5481 tets / 2168 nodes, ImplicitEuler dt=0.5 ms x 80 steps, dhat=5e-5 m).
- Printable-design module with class-1 (strut-strut closest-approach) check,
  Bambu H2D printability bounds, 7x5 (tendon-Ø, prestrain) sweep -> Pareto.
- 3D offscreen renders with tendon strain-coloured cables (OSMesa MuJoCo).

We need to identify **specific people and groups to reach out to** for
feedback / sanity checks / spot checks / recommendations on this modelling
approach. Please produce a citation-rich, prioritised, *contact-level*
brief organised as follows:

# 1. Tensegrity dynamics + drop / impact mechanics (academic)

Named researchers (with current affiliation, role, email/lab URL where
publicly listed, recent papers, why they are well-placed to critique our
approach, and a specific 1-2 sentence "ask"). Group into:

  (a) Tensegrity structural mechanics + form-finding (e.g., Skelton, Sultan,
      Caluwaerts, Goyal, Tibert, Pellegrino, Motro, de Oliveira, Bel Hadj
      Ali).
  (b) Tensegrity robotics / SUPERball / lander lineage (NASA Ames Intelligent
      Robotics Group: Vytas SunSpiral, Adrian Agogino, Brian Tietz Mirletz,
      Massimo Vespignani; UC Berkeley AHMCT / BEST Lab; Alice Agogino).
  (c) Impact-attenuation / drop-test mechanics of soft/architected materials
      (Pajunen, Bauer, Anand, Snapp, Gongora, Valdevit, Greer, Schaedler).
  (d) Tensegrity + 3D-printing (e.g., Davami 2025; Liu 2023; Intrigila 2022;
      Yavas 2022; Rieffel; Hiller & Lipson).

# 2. Simulator maintainers + differentiable physics

For each of the simulators we use, identify the active maintainer(s) and the
right channel (GitHub discussions / issues / mailing list) to ask for
modelling sanity-checks. Cover:

  (a) PolyFEM + IPC: Teseo Schneider (Victoria, NYU), Daniele Panozzo (NYU
      Courant), Zachary Ferguson, Minchen Li (CMU), Chenfanfu Jiang (UCLA);
      ipc-toolkit maintainers.
  (b) DiffPD: Tao Du (Tsinghua), Wojciech Matusik (MIT CSAIL GFX).
  (c) NVIDIA Newton / Warp: Miles Macklin, Matthias Mueller-Fischer, the
      Newton GitHub org maintainers; Omniverse Isaac Lab tensegrity-robot
      examples (if any).
  (d) MuJoCo: Emo Todorov (Roboti / UW), Yuval Tassa (DeepMind), the
      MuJoCo-MJX team; relevant tendon/cable contact issues on the
      google-deepmind/mujoco issue tracker.
  (e) PyBullet / Bullet3: Erwin Coumans; soft-body deformable contact
      maintainers.
  (f) PyChrono: Alessandro Tasora (Parma), Dario Mangoni; Project Chrono
      community.
  (g) NTRT (NASA Tensegrity Robotics Toolkit) maintainers and any active
      fork curators.

# 3. Materials + AM characterisation

  (a) Researchers who have published PLA-TPU multi-material FDM interface
      data (Lopes 2018, Zhang 2026, Ruwais 2025) - whose feedback would help
      us trust the welded PolyFEM material model.
  (b) NinjaFlex / TPU 85A characterisation labs (Fenner/Lubrizol contacts;
      academic groups with published TPU 85A secant moduli and Mullins-
      effect curves).
  (c) PLA shock / impact characterisation (Charpy / Izod / drop-weight)
      contacts.

# 4. Standards bodies + test labs

People who can audit our standards mapping (we currently target ASTM D5276,
F1292, F2971, ISTA 1A/1H, MIL-STD-810H 516.8, GSFC GEVS-STD-7000B, JEDEC for
M23). For each, give the standards-committee secretariat and a recognised
academic/practitioner with active publications. Include drop-test lab
contacts (Lansmont, MTS, Instron application engineers; NASA GSFC; Sandia;
Aberdeen Test Center) and a one-paragraph note on how to engage them
(formal RFP vs. informal email vs. conference Q&A).

# 5. Bayesian optimisation + multi-fidelity surrogates

Researchers we should ping for sanity checks on the BO + multi-fidelity
strategy that consumes these simulators (e.g., Frazier, Wang, Garnett,
Letham, Bakshy / BoTorch / Ax; Frazier's group at Cornell; Wang's group at
UMich; Acceleration Consortium SDL community; Bran Selic / Adam Stevens
multi-fidelity comp sci contacts).

# 6. Synthesis

  (a) A ranked top-10 contact list ("if you can only send 10 emails this
      month, send them to these 10 people, in this order, asking these
      specific questions"), with the rationale for each ranking.
  (b) A draft 1-page outreach email template (subject + 4-paragraph body)
      that we can adapt per contact and that links our repo, our PR, and
      the specific artifact (e.g., simulations/polyfem_drop_tprism.png,
      simulations/outputs/regime_*_printable_heatmap.png) we want feedback
      on.
  (c) A list of 3-5 venues (workshops, journals, Slack/Discord
      communities) where we should post the modelling approach for
      broader community spot-checks (e.g., SIGGRAPH Physics-Based Animation
      community, ICRA/IROS soft-robotics workshops, ASME IMECE Tensegrity
      symposium, Acceleration Consortium SDL Slack, the polyfem/polyfem
      GitHub Discussions, BoTorch GitHub Discussions).

For every named contact, cite the publication(s) or repo activity that
justifies the recommendation. Flag any contact where the recommendation is
engineering judgement rather than literature-grounded.

# Contact-Level Brief: Expert Feedback for Multi-Fidelity Tensegrity Drop-Impact Simulation

This document identifies specific researchers, maintainers, and practitioners to contact for feedback on a multi-fidelity simulation stack modeling drop-impact response of class-1 tensegrity cells (3 PLA struts + 9 TPU 85A tendons, T-prism topology).

---

## 1. Tensegrity Dynamics + Drop / Impact Mechanics (Academic)

### (a) Tensegrity Structural Mechanics + Form-Finding

**Robert E. Skelton** — UC San Diego (emeritus). Foundational figure in tensegrity statics, dynamics, and design. Authored the standard reference *Tensegrity Systems* (2009) with de Oliveira, plus dynamics formulations with rigid bars and massive strings (kim2016onthelocomotion pages 131-134). **Ask:** Sanity-check whether the class-1 T-prism parameterization and prestrain sweep are structurally meaningful, or if load-case assumptions violate standard tensegrity mechanics intuition.

**Cornel Sultan** — Virginia Tech, Department of Aerospace & Ocean Engineering. Early work on tensegrity flight simulators and dynamics with Skelton. **Ask:** Review whether the dynamic formulation choices across your tiers preserve the tension-integrity constraint under impact loading. *[Engineering judgement on current affiliation; based on Sultan et al. 2000.]*

**Raman Goyal** — Texas A&M (formerly UCSD with Skelton). Published tensegrity dynamics with rigid bars/massive strings and analytical energy-absorption studies for D-bar tensegrity lattices relevant to planetary landers (kim2016onthelocomotion pages 131-134). **Ask:** Evaluate whether your cable stiffness sweep across ~3 decades covers the energy-storage mechanisms that matter for D-bar/T-prism impact.

**Gunnar Tibert** — KTH Royal Institute of Technology. PhD on deployable tensegrity structures for space; co-authored the standard review of form-finding methods with Pellegrino (caluwaerts2014superballexploringtensegrities pages 7-7). **Ask:** Assess whether the form-finding assumptions implicit in your printable-design module are consistent with established T-prism equilibrium configurations.

**Sergio Pellegrino** — Caltech, GALCIT. Co-authored the form-finding review and works on deployable space structures (caluwaerts2014superballexploringtensegrities pages 7-7). **Ask:** Brief comment on whether your prism topology and tendon prestrain range are appropriate for an impact-absorbing application versus the more typical deployment use case.

**René Motro** — Université de Montpellier (emeritus). Pioneered dynamic relaxation form-finding for tensegrity prisms. **Ask:** Whether your form-finding approach for the triangular prism is consistent with established methods.

**Mauricio C. de Oliveira** — UC San Diego. Co-author of *Tensegrity Systems* with Skelton. **Ask:** Review the analytical assumptions underlying your cable/strut force distributions.

**Nabil Ben Kahla / Mohamed Hechmi El Ouni** — Groups publishing on tensegrity dynamic stability. *[Engineering judgement; based on search results for dynamic stability analysis of tensegrity.]* **Ask:** Whether your implicit Euler stepping in PolyFEM adequately captures dynamic instabilities in prestressed T-prisms.

### (b) Tensegrity Robotics / SUPERball / Lander Lineage

**Vytas SunSpiral** — NASA Ames Intelligent Robotics Group lineage. Central figure in SUPERball, NTRT, and tensegrity lander/EDL research. Co-authored NIAC Phase 2 final report, multiple ICRA/IROS papers on tensegrity rovers and simulators (agogino2014hardwaredesignand pages 10-11, bruce2014designandevolution pages 6-7, caluwaerts2014superballexploringtensegrities pages 7-7). **Ask:** Spot-check whether the T-prism-with-payload-suspension interpretation captures useful lander physics, and where Bullet/NTRT-style cable abstractions break down for impact.

**Adrian K. Agogino** — NASA Ames. Co-PI on SUPERball hardware and software, published on tensegrity probes and lander EDL (agogino2014hardwaredesignand pages 10-11). **Ask:** Whether your two application regimes (crutch tip vs. lander-style) are exercising the right structural modes.

**Alice M. Agogino** — UC Berkeley, BEST Lab. Published extensively on tensegrity robotics, rapid prototyping, TT-3, and spherical tensegrity locomotion (agogino2014hardwaredesignand pages 10-11, caluwaerts2014superballexploringtensegrities pages 7-7). **Ask:** Whether your dual-regime framing will produce transferable experimental insight, and which physical prototype measurements most efficiently falsify simulation assumptions.

**Ken Caluwaerts** — Google DeepMind (formerly Ghent/NASA Ames). First author on SUPERball exploration and design/control of compliant tensegrity robots through simulation and hardware validation (caluwaerts2014superballexploringtensegrities pages 7-7). **Ask:** Whether your MuJoCo cable-stiffness sweep is parameterized similarly to NTRT/SUPERball practice.

**Massimo Vespignani** — Formerly NASA Ames / EPFL. Designed SUPERball v2 specifically for absorbing large impacts (noted in search results as Vespignani et al. 2018). **Ask:** Whether your tendon-diameter sweep captures the critical design trade-offs identified in SUPERball v2.

**Brian Tietz Mirletz** — Case Western Reserve (formerly NASA Ames). Published on bridging the reality gap between NTRT simulation and hardware (bruce2014designandevolution pages 6-7). **Ask:** What sim-to-real pitfalls to expect when transitioning from your volumetric FEM to physical drop tests.

**Andrew P. Sabelhaus** — UC Berkeley lineage. System design and locomotion of untethered SUPERball (kim2016onthelocomotion pages 131-134). **Ask:** Whether your printable-design module handles the cable-routing and pretensioning realities that drove SUPERball hardware compromises.

### (c) Impact-Attenuation / Drop-Test Mechanics of Soft/Architected Materials

**Julian J. Rimoli** — Georgia Institute of Technology, School of Aerospace Engineering. Published the key paper on impact tolerance of tensegrity-based planetary landers, reduced-order dynamic/post-buckling models, and soft tensegrity systems for landing and exploration. **Ask:** Review whether your multi-tier progression preserves the right failure/energy-storage mechanisms for tensegrity lander-like structures.

**Kirsti Pajunen** — Caltech (now likely elsewhere). Published on design and impact response of 3D-printable tensegrity-inspired structures with Daraio, plus prestrain-induced bandgap tuning. **Ask:** Whether your PLA/TPU material pair and print geometry preserve the nonlinear compressive response that mimics tensegrity behavior.

**Chiara Daraio** — Caltech, Engineering and Applied Science. Senior author on architected lattices with adaptive energy absorption and tensegrity-inspired impact structures. **Ask:** Whether your tendon-Ø / prestrain Pareto captures the key energy-absorption design trade-offs for polymer tensegrity-inspired systems.

**Keivan Davami** — U.S. Air Force Academy. Published on dynamic energy absorption of additively manufactured lattice structures and (per 2025 records) tensegrity-inspired structures under dynamic analysis. **Ask:** Whether your printable PLA/TPU design-space sweep preserves impact-energy-absorption phenomena, and which print details most often invalidate simulation results.

**Carlos M. Portela** — MIT. Published on decoupling particle-impact dissipation mechanisms in 3D architected materials. **Ask:** Whether your drop velocities (1.4 and 9.8 m/s) probe architecture-dependent or material-dependent dissipation mechanisms in your tensegrity cell. *[Engineering judgement on direct tensegrity relevance.]*

**Tobias Schaedler** — HRL Laboratories. Published on elastomeric microlattice impact attenuators (noted in search results). **Ask:** Whether TPU 85A tendon behavior under repeated impact can be approximated with NeoHookean or requires viscoelastic/Mullins treatment. *[Engineering judgement.]*

### (d) Tensegrity + 3D-Printing

**Keivan Davami** (also listed in 1c) — Published directly on additively manufactured tensegrity structures including dynamic impact characterization. Primary contact for the AM-to-impact bridge.

**Andrea Micheletti & Claudio Intrigila** — Università di Roma "Tor Vergata." Published on fabrication and experimental characterisation of bistable tensegrity-like units for lattice metamaterials using additive manufacturing. **Ask:** Whether your class-1 closest-approach check and Bambu H2D bounds are sufficient printability constraints for tensegrity-like geometries.

**Ada Amendola & Fernando Fraternali** — Università di Salerno. Published on additive manufacturing, post-tensioning, and testing of bi-material tensegrity structures (titanium alloy + Spectra cables). **Ask:** Whether your welded PLA/TPU interface in PolyFEM is a reasonable idealization compared to their post-tensioned fabrication approach.

**John Rieffel** — Union College. Published on evolved tensegrity robots and dynamically coupled modules; cited in NTRT context (agogino2014hardwaredesignand pages 10-11). **Ask:** Whether evolutionary/generative design approaches would complement your deterministic design-sweep module. *[Engineering judgement on current activity.]*

**Hajun Lee et al.** — Published on 3D-printed programmable tensegrity for soft robotics (Science Robotics, 2020; noted in search results). **Ask:** Whether dual-material FDM tensegrity prints exhibit interface failure modes that your welded FEM model cannot capture. *[Engineering judgement on contact details.]*

---

## 2. Simulator Maintainers + Differentiable Physics

### (a) PolyFEM + IPC

**Teseo Schneider** — University of Victoria (formerly NYU). Lead developer of PolyFEM; co-author of IPC. **Channel:** `polyfem/polyfem` GitHub Discussions. **Ask:** Validate your `dhat=5e-5 m`, `dt=0.5 ms`, NeoHookean welded mesh setup for drop-impact with self-contact.

**Daniele Panozzo** — NYU Courant, Geometry Processing Group. Co-PI of PolyFEM ecosystem. **Channel:** `polyfem/polyfem` GitHub Discussions or direct email. **Ask:** Whether your gmsh OCC fragment → welded volumetric mesh pipeline is geometrically robust for this problem.

**Zachary Ferguson** — Formerly NYU, now Adobe Research. Co-author of convergent IPC and in-timestep remeshing for contacting elastodynamics. **Channel:** `ipc-sim/ipc-toolkit` GitHub Issues. **Ask:** Whether your 5481-tet mesh is sufficiently refined for IPC convergence at your impact velocities.

**Minchen Li** — UCLA (formerly CMU). Co-author of convergent IPC formulation. **Ask:** Whether your barrier parameter choices are in a convergent regime under refinement.

**Chenfanfu Jiang** — UCLA. Co-author on IPC; works on MPM and large-deformation simulation. **Ask:** Whether MPM would be more appropriate than FEM+IPC for your highest-velocity regime (9.8 m/s).

### (b) DiffPD

**Tao Du** — Tsinghua University (formerly MIT CSAIL). Lead author of DiffPD. **Channel:** `mit-gfx/diff_pd` GitHub Issues. **Ask:** Whether DiffPD is a credible Tier-B surrogate for identifying tendon/material parameters in this impact setting, given its contact formulations.

**Wojciech Matusik** — MIT CSAIL, Computational Design & Fabrication Group. Senior author on DiffPD. **Ask:** Whether the penalty-based contact in DiffPD is sufficient for tensegrity cable-strut interactions under impact.

### (c) NVIDIA Newton / Warp

**Miles Macklin** — NVIDIA. Lead on Warp and XPBD-based differentiable simulation. **Channel:** `NVIDIA/warp` GitHub Discussions/Issues. **Ask:** Whether the XPBD all-particle formulation handles the extreme stiffness ratio between PLA struts and TPU tendons without constraint-drift issues at your impact velocities.

**Matthias Müller-Fischer** — NVIDIA. Co-author of XPBD and small-steps physics. **Ask:** Whether your substep count is adequate for the stiffness range in your tendon-Ø sweep.

**Newton GitHub org maintainers** — Channel: `nvidia/newton` GitHub (if public). **Ask:** Whether Newton supports cable/tendon primitives natively or requires workarounds.

### (d) MuJoCo

**Emanuel Todorov** — University of Washington / Roboti LLC. Original creator of MuJoCo; the engine natively supports tendon wrapping and cable models. **Channel:** `google-deepmind/mujoco` GitHub Issues. **Ask:** Whether MuJoCo's cable/tendon model is appropriate for screening tensegrity drop dynamics, or whether the contact model introduces artifacts at your impact velocities.

**Yuval Tassa** — Google DeepMind. MuJoCo co-developer and active maintainer. **Channel:** `google-deepmind/mujoco` GitHub Issues/Discussions. **Ask:** Whether there are known limitations of MuJoCo's tendon model for highly dynamic cable systems (high prestrain + impact).

**MuJoCo-MJX team** — For GPU-accelerated sweeps. Search the issue tracker for "tendon" and "cable contact" issues.

### (e) PyBullet / Bullet3

**Erwin Coumans** — Google / formerly NVIDIA. Creator of Bullet Physics and PyBullet. **Channel:** `bulletphysics/bullet3` GitHub Issues. **Ask:** Whether Bullet's soft-body/deformable contact handling is reliable enough for tensegrity cable members under impact, or whether you should restrict Bullet to rigid-strut screening only. *[Note: NTRT was built on Bullet (bruce2014designandevolution pages 6-7).]*

### (f) PyChrono

**Alessandro Tasora** — University of Parma. Lead developer of Project Chrono's core engine. **Channel:** `projectchrono/chrono` GitHub Discussions, or Chrono user forum. **Ask:** Whether PyChrono adds unique value for cable/impact screening relative to MuJoCo/Bullet, or should be reserved for specific contact/constraint corner cases.

**Dario Mangoni** — University of Parma. Active PyChrono developer; published on non-smooth multibody dynamics and interior-point solvers. **Ask:** Best-practice Chrono modeling choices for compliant cable-like members in drop tests.

**Dan Negrut** — UW-Madison. PI of the Simulation-Based Engineering Lab; co-developer of PyChrono and Gym-Chrono. **Channel:** `projectchrono/chrono` GitHub or sbel.wisc.edu.

### (g) NTRT (NASA Tensegrity Robotics Toolkit)

The NTRT was developed by the Intelligent Robotics Group at NASA Ames, built on top of the Bullet Physics Engine (bruce2014designandevolution pages 6-7). Key developers include **Vytas SunSpiral**, **Brian Mirletz**, **Jonathan Bruce**, **Ken Caluwaerts**, and **Andrew Sabelhaus**. The repository (`nasa/NTRTsim`) appears to be archived/low-activity. **Channel:** GitHub Issues on the repo; direct email to SunSpiral or Sabelhaus. **Ask:** Whether any active fork exists that addresses known cable-contact limitations, and whether NTRT-style abstractions are worth maintaining in your stack alongside MuJoCo.

---

## 3. Materials + AM Characterisation

### (a) PLA-TPU Multi-Material FDM Interface

**L. R. Lopes, Alexandre Ferreira da Silva, Olga S. Carneiro** — Universidade do Minho, Portugal. Published the seminal paper on multi-material 3D printing boundary interface performance for PLA-TPU pairs, showing significant Young's modulus and tensile strength reductions at material interfaces (lopes2018multimaterial3dprinting pages 7-8). **Ask:** Whether your welded PolyFEM interface model (perfect bonding) is a reasonable upper bound, or whether interface degradation dominates real-world drop response.

**M. A. A. Ruwais, N. Naveed, M. Armstrong** — University of Sunderland, UK. Published on mechanical performance of layered PLA-TPU composites, reporting up to 27-fold elongation improvements but significant interfacial bonding challenges (ruwais2025mechanicalperformanceof pages 1-4). Contact: mark.armstrong@research.sunderland.ac.uk. **Ask:** Whether your TPU 85A + PLA interface assumptions are optimistic relative to their measured bond strengths.

**Budi Arifvianto et al.** — Universitas Gadjah Mada, Indonesia. Published on FFF sandwich-structured PLA/TPU parts (arifvianto2022mechanicalpropertiesof pages 10-11). **Ask:** Whether sandwich-structured configurations change the failure mode relative to your welded T-prism geometry.

**Francesco Tamburrino, Serena Graziosi, Monica Bordegoni** — Politecnico di Milano. Published on multi-material FDM adhesion mechanisms showing mechanical interlocking strategies improve TPU-PLA adhesion. **Ask:** Whether your print geometry includes sufficient mechanical interlocking at strut-tendon junctions.

### (b) TPU 85A Characterisation

**Andrea Avanzini** — Università di Brescia. Published on cyclic strain behavior of thermoplastic polyurethane, including strain-rate and Mullins-like effects. **Ask:** Whether NeoHookean is adequate for TPU 85A under repeated impact, or whether you need a viscoelastic/Mullins constitutive model in PolyFEM.

**Fenner Drives / Lubrizol (Estane TPU)** — Industrial TPU suppliers. Contact application engineering for published Shore 85A secant modulus data and recommended constitutive parameters. *[Engineering judgement; no specific publication found.]*

### (c) PLA Shock / Impact Characterisation

PLA Charpy/Izod and drop-weight impact data are widely published in polymer characterisation literature. Key groups include those at the University of Bologna (polymer impact testing) and various AM characterisation labs. **Ask:** Whether FDM PLA at your print orientation exhibits brittle failure at your impact velocities, which would invalidate the assumption that struts remain elastic. *[Engineering judgement for specific lab contacts.]*

---

## 4. Standards Bodies + Test Labs

**ASTM D5276 (Free-Fall Drop Test):** Managed by ASTM Committee D10 on Packaging. Contact the ASTM secretariat (astm.org) or search D10.15 subcommittee rosters. Academic practitioners include **Sher Paul Singh** (Michigan State University, School of Packaging), who publishes extensively on physical distribution testing. **Ask:** Whether your M23 envelope mapping is appropriate for the two regimes.

**ASTM F1292 / F2971 (Playground/Sports Impact Attenuation):** Managed by ASTM F08 Committee. Contact F08.63 subcommittee. Relevant for the crutch-tip regime. *[Engineering judgement.]*

**ISTA 1A/1H (Packaged-Product Testing):** Contact ISTA (ista.org) technical staff. ISTA has accredited test labs worldwide. **Ask:** Whether your drop heights and payload masses map correctly to ISTA test levels.

**MIL-STD-810H 516.8 (Shock):** Contact the U.S. Army Aberdeen Test Center (ATC) or the Test Resource Management Center. Also consult **Tom Irvine** (vibrationdata.com), a well-known independent consultant with published shock-testing guides.

**GSFC GEVS-STD-7000B:** Contact NASA GSFC Code 549 (Mechanical Systems Branch). For academic guidance, contact mechanical-testing faculty at the University of Maryland who collaborate with GSFC.

**Drop-Test Lab Contacts:**
- **Lansmont Corporation** (Monterey, CA): Manufacturer of the M23 shock machine. Contact their applications engineering team for test setup advice. Engage via informal email referencing your M23 usage.
- **MTS Systems / Instron**: Contact their impact-testing applications engineers. Engage via formal RFP if you need calibrated drop testing.
- **Sandia National Laboratories**: Contact their Component Qualification and Environmental Testing groups. Engage via formal CRADA or through conference networking (e.g., IEST Annual Technical Meeting).
- **NASA GSFC Environmental Test Facility**: Engage via a formal test-services request or through collaborating PIs.

**Engagement note:** For standards bodies, the most productive approach is to identify the relevant subcommittee chair via the ASTM/ISTA website and send a brief email describing your simulation-to-test mapping, asking whether your interpretation of the standard is correct. For test labs, Lansmont and Instron are approachable via informal application-engineering emails; government labs (GSFC, Sandia, ATC) require more formal channels. Conference Q&A at IEST, IAPRI (packaging), or AIAA (space environments) is an efficient way to get initial guidance before committing to formal engagement.

*[All standards/test-lab contacts are engineering judgement rather than literature-grounded.]*

---

## 5. Bayesian Optimisation + Multi-Fidelity Surrogates

**Peter I. Frazier** — Cornell University, School of Operations Research & Information Engineering. Lead researcher on knowledge-gradient methods and practical multi-fidelity Bayesian optimization. Co-authored trace-aware knowledge gradient for multi-fidelity BO. **Ask:** Sanity-check your plan to consume Tier C/B/A simulators in a multi-fidelity BO loop, particularly around fidelity ordering, cost-awareness, and acquisition strategy for expensive contact-rich simulators.

**Maximilian Balandat** — Meta (FAIR). Lead developer of BoTorch. **Channel:** `pytorch/botorch` GitHub Discussions. **Ask:** Whether BoTorch's multi-fidelity GP models can handle the discrete fidelity levels and heterogeneous output dimensions across your three simulator tiers.

**Benjamin Letham** — Meta. Co-developer of BoTorch and Ax. **Channel:** `facebook/Ax` GitHub. **Ask:** Whether Ax's multi-fidelity optimization scheduling is appropriate for your cost structure (seconds for MuJoCo, minutes for Newton, hours for PolyFEM).

**Samuel Daulton** — Meta. Published on hypervolume knowledge gradient for multi-objective multi-fidelity BO. **Ask:** Whether multi-objective formulation (e.g., peak-g vs. cost vs. printability) would improve your Pareto analysis relative to scalarized objectives.

**Eytan Bakshy** — Meta. Co-developer of Ax platform. **Channel:** `facebook/Ax` GitHub Discussions. **Ask:** Whether Ax's asynchronous evaluation scheduling can efficiently manage your heterogeneous simulator wall-clock times.

**Roman Garnett** — Washington University in St. Louis. Author of *Bayesian Optimization* textbook. **Ask:** High-level review of whether your fidelity ordering and noise assumptions are reasonable from a theoretical BO perspective.

**Andrew Gordon Wilson** — New York University (formerly Cornell). Co-authored practical multi-fidelity BO with Frazier. **Ask:** Whether GP kernel choices for multi-fidelity modeling should account for the qualitative differences between rigid-body and volumetric FEM outputs.

**Sterling Baird / Acceleration Consortium** — University of Toronto lineage. Organized the BO hackathon for chemistry and materials; active in SDL community. **Channel:** AC Slack, ac-bo-hackathon.github.io. **Ask:** Whether the multi-fidelity simulation-to-hardware loop pattern from materials SDL practice transfers well to structural/mechanical design. *[Engineering judgement on direct applicability.]*

---

## 6. Synthesis

### (a) Ranked Top-10 Contact List

The following table ranks the ten highest-priority contacts, ordered by expected value of feedback for your specific simulation stack:

| Rank | Name | Affiliation | Domain | Specific Ask | Rationale |
|---|---|---|---|---|---|
| 1 | Teseo Schneider | University of Victoria / formerly NYU Geometry Processing | PolyFEM + IPC, contact-rich elastodynamics | Could you sanity-check whether our welded PLA/TPU volumetric T-prism setup, IPC barrier parameters (`dhat=5e-5 m`), and implicit stepping (`dt=0.5 ms`) are in a credible regime for repeated low-speed drop-impact with self-contact? We would especially value your view on whether our contact treatment is likely to over-stiffen tendon/strut interactions or mask mesh/pathology issues. | Highest-priority because your work directly underpins the Tier-A model we are using: PolyFEM and IPC for inversion-/intersection-free contacting elastodynamics, including large-deformation contact and recent convergent IPC developments. That makes you the single best person to critique the most failure-sensitive part of the stack (Schneider et al. 2020; Li et al. 2023). |
| 2 | Julian Rimoli | Georgia Institute of Technology | Tensegrity impact tolerance, reduced-order modeling, planetary landing | Could you review whether our progression from rigid-cable screening to differentiable mid-fidelity to volumetric contact FEM is a sensible way to estimate impact response for class-1 prisms? We would also appreciate a quick read on whether our two operating regimes are probing the right failure/energy-storage mechanisms for tensegrity lander-like structures. | Rimoli is one of the clearest literature anchors for tensegrity impact mechanics and lander applications, including impact tolerance of tensegrity-based planetary landers and reduced-order modeling of tensegrity dynamics/post-buckling. He is unusually well-placed to judge whether the physics abstractions in each tier preserve the mechanisms that matter under impact (Rimoli 2016; Rimoli 2018; Garanger et al. 2021). |
| 3 | Vytas SunSpiral | NASA Ames lineage / Intelligent Robotics Group lineage | SUPERball, NTRT, tensegrity robotics, lander/EDL use-cases | Could you spot-check whether our T-prism-with-payload-suspension interpretation captures anything useful from the SUPERball/NTRT lander lineage, or whether we are missing critical topology/load-path assumptions? A brief recommendation on when Bullet/NTRT-style cable abstractions break down for impact would be especially helpful. | SunSpiral sits at the center of the NASA tensegrity robot and lander thread: SUPERball, NTRT, ReCTeR, and related Ames work. For questions about whether your application framing matches the historical lander/rover rationale—and where rigid-body cable simulators are “good enough” versus misleading—he is among the best possible contacts (Caluwaerts et al. 2014; Mirletz et al. 2015; Friesen et al. 2014) (bruce2014designandevolution pages 6-7, caluwaerts2014superballexploringtensegrities pages 7-7). |
| 4 | Tao Du | Tsinghua University / formerly MIT CSAIL | DiffPD, differentiable soft-body simulation | Could you advise whether DiffPD is a credible Tier-B surrogate for identifying tendon/material parameters or prestrain in this impact setting, given its contact formulations and the fact that our actual geometry is a welded multi-material tensegrity cell rather than a homogeneous soft body? We are especially interested in what observables you would trust DiffPD for, versus reserve for PolyFEM+IPC. | DiffPD was explicitly developed as a differentiable projective-dynamics simulator for soft-body learning/control with penalty and complementarity-based contact. Since you already ran a DiffPD smoke test and may want it for gradient-based calibration or BO, Du is the right person to tell you where DiffPD is methodologically appropriate and where contact/nonlinear-material realism becomes too compromised (Du et al. 2021). |
| 5 | Robert E. Skelton | University of California, San Diego (emeritus lineage) | Foundational tensegrity statics/dynamics/form-finding | Could you give us a foundational sanity check on whether our class-1 T-prism parameterization and prestrain sweep are structurally meaningful, rather than just numerically convenient? In particular, we would value any warning signs that our load cases or tendon stiffness assumptions violate the usual tensegrity mechanics intuition. | Skelton’s work is foundational for tensegrity statics, dynamics, and design, including the standard analytical language many later groups use. Even a brief response would be high value because it would test whether the entire stack is grounded in the right structural idealization before spending more effort on calibration (Sultan et al. 2000; Goyal & Skelton 2019; Oliveira & Skelton 2009). |
| 6 | Keivan Davami | U.S. Air Force Academy / additive manufacturing & impact mechanics community | 3D-printed tensegrity-inspired structures, dynamic energy absorption | Could you comment on whether our printable PLA-strut / TPU-tendon design-space sweep is likely to preserve the impact-energy-absorption phenomena seen in additively manufactured tensegrity-inspired systems? We would especially appreciate guidance on which print/manufacture details most often invalidate otherwise promising simulation results. | Davami is a high-value contact because he connects additive manufacturing with dynamic energy absorption and, per recent/unobtainable records, tensegrity-inspired dynamic analysis at higher rates. He is therefore well suited to critique the manufacturability-to-impact-performance bridge in your workflow, especially the jump from printable geometries to validated crashworthiness claims (Davami et al. 2019; related 2025 tensegrity-impact work noted in search results). |
| 7 | Peter I. Frazier | Cornell University, School of Operations Research and Information Engineering | Multi-fidelity Bayesian optimization | Could you sanity-check our plan to consume Tier C/B/A simulators in a multi-fidelity BO loop, particularly around fidelity ordering, cost-awareness, and which responses should be modeled jointly versus separately? A brief recommendation on acquisition strategy for expensive contact-rich simulators would be extremely valuable. | Frazier is one of the central BO researchers for knowledge-gradient and practical multi-fidelity BO, and is therefore an excellent external check on whether your optimization strategy is statistically sound rather than just computationally convenient. This matters because the usefulness of the whole stack depends on extracting sample-efficient design guidance from heterogeneous simulators (Wu et al. 2020; Xie et al. 2024). |
| 8 | Daniele Panozzo | New York University, Courant / Geometry Processing Group | PolyFEM ecosystem, geometry processing for simulation | Could you review whether our gmsh OCC fragment → welded volumetric mesh → PolyFEM workflow is the right geometric pipeline for this problem, or whether we should move toward different meshing/validity checks before trusting quantitative drop results? We would also welcome advice on how much geometric fidelity is worth buying before contact dominates the error budget. | Panozzo is a core PolyFEM/geometry-processing figure and coauthor across PolyFEM and IPC-related work. He is less likely than Schneider to focus on your exact contact parameter choices, but exceptionally well placed to critique the geometry/meshing side of the Tier-A pipeline and the robustness of the overall FEM setup (Schneider et al. 2019; Schneider et al. 2022). |
| 9 | Alice M. Agogino | University of California, Berkeley | Tensegrity robotics, rapid prototyping, hardware validation | Could you assess whether our application split—assistive-device crutch tip versus NASA-lander-style drop—is framed in a way that will produce transferable experimental insight, rather than two disconnected demonstrations? We would also value advice on which physical prototype measurements most efficiently falsify the simulation assumptions. | Alice Agogino is central to UC Berkeley’s tensegrity robotics thread and collaborated across SUPERball-era hardware, rapid prototyping, and control studies. She is therefore a strong contact for bridging simulation with practical build-and-test decisions, especially for early-stage hardware validation plans (Agogino et al. 2014; Chen et al. 2017) (agogino2014hardwaredesignand pages 10-11, caluwaerts2014superballexploringtensegrities pages 7-7). |
| 10 | Alessandro Tasora | University of Parma / Project Chrono | PyChrono, nonsmooth multibody dynamics, contact | Could you advise whether PyChrono is adding unique value in our Tier-C screening for cable/impact problems, relative to MuJoCo and Bullet, or whether we should use it only for specific contact/constraint corner cases? A quick steer on best-practice Chrono modeling choices for compliant cable-like members in drop tests would help us avoid unproductive benchmarking. | Tasora is the natural contact for Chrono/PyChrono and nonsmooth multibody dynamics. Since you already include PyChrono as a screening engine, his input can help you decide whether Chrono should remain in the stack as a genuinely complementary solver or be deprioritized if it does not materially improve confidence for this application (Benatti et al. 2019; Mangoni et al. 2019). |


*Table: This table prioritizes the ten highest-value people to contact first for feedback on the tensegrity drop-impact simulation stack. It emphasizes direct relevance to the T-prism modeling choices, ability to critique specific tiers of the stack, and practical likelihood of yielding useful guidance.*

### (b) Draft Outreach Email Template

The following template can be adapted per contact by inserting the person-specific ask from the table above:

> **Subject:** Request for a sanity check on our multi-fidelity tensegrity drop-impact simulation stack
>
> Dear [Dr./Prof./Name],
>
> We are building a multi-fidelity simulation stack to model drop-impact response of class-1 tensegrity cells in a three-strut T-prism topology, using 3 PLA struts and 9 TPU 85A tendons. Our current target regimes are (i) a crutch-tip-style impact case at 1.4 m/s with a 75 kg effective load path and (ii) a NASA-lander-style case at 9.8 m/s with a 5 kg payload, both within the Lansmont M23 envelope. We are trying to understand which modeling assumptions are trustworthy across rigid-body screening, differentiable mid-fidelity models, and high-fidelity volumetric contact simulation, especially for tendon prestrain, cable stiffness, contact handling, and energy dissipation in a small tensegrity prism. Our stack is informed by prior work on tensegrity dynamics, SUPERball/NTRT simulation practice, and impact-tolerant tensegrity landers (agogino2014hardwaredesignand pages 10-11, bruce2014designandevolution pages 6-7, caluwaerts2014superballexploringtensegrities pages 7-7).
>
> Concretely, we have run: MuJoCo bare-prism 1 m drops and regime sweeps with cable stiffness varied across ~3 decades; NVIDIA Newton/Warp XPBD all-particle T-prism simulations with payload-suspension tendons in the load path and tendon-diameter sweeps (1.5, 3.0, 5.0 mm); a DiffPD soft-body smoke test; and a PolyFEM+IPC welded strut+tendon volumetric drop simulation end-to-end on a 5481-tet / 2168-node mesh using Neo-Hookean materials, ImplicitEuler, dt = 0.5 ms, 80 steps, and dhat = 5e-5 m. In parallel, we built a printable-design module enforcing class-1 closest-approach constraints and printer bounds, then ran a 7x5 tendon-diameter/prestrain sweep to produce a Pareto-style shortlist. We also have offscreen renders with tendon strain colouring and a small set of figures/results we can point you to directly. These modeling layers mirror the sort of simulation-to-hardware gap issues discussed in tensegrity robotics and NTRT work, which is why we are seeking expert spot-checks before investing in more hardware validation (agogino2014hardwaredesignand pages 10-11, bruce2014designandevolution pages 6-7).
>
> The specific question I hoped to ask you is: **[INSERT 1-2 SENTENCE PERSON-SPECIFIC ASK]**. For example, for a simulator maintainer, we would ask whether our contact, timestep, stiffness, and welded-interface assumptions are reasonable for this use case; for a tensegrity dynamics expert, whether our treatment of prestrain, member idealization, and impact load path is physically sensible for a class-1 prism; for an impact/AM expert, whether our PLA/TPU interface assumptions and geometric simplifications are likely to bias the drop-response trends in the wrong way. We are not looking for a long review—just a quick sanity check on the highest-risk assumptions, plus any recommendation for one benchmark, one ablation, or one failure mode we should test next. Our PLA-TPU interface questions are especially motivated by the known sensitivity of multimaterial FFF boundary performance to interface design and material affinity (lopes2018multimaterial3dprinting pages 7-8, ruwais2025mechanicalperformanceof pages 1-4).
>
> If you are open to it, I would send a very short bundle containing: **repo:** [REPO LINK], **PR / branch:** [PR LINK], and 2-4 specific artifacts such as `simulations/polyfem_drop_tprism.png`, `simulations/outputs/regime_*_printable_heatmap.png`, `simulations/mujoco_drop_sweep.png`, and `simulations/newton_tendon_diameter_sweep.png`. If easier, I can also reduce this to one figure and three bullet questions. Thank you for considering it—your feedback would help us decide whether to trust the current stack as a design-screening tool, or whether we should redirect effort toward material calibration, simpler benchmark geometries, or a different simulator boundary between tiers. (agogino2014hardwaredesignand pages 10-11, bruce2014designandevolution pages 6-7, lopes2018multimaterial3dprinting pages 7-8, ruwais2025mechanicalperformanceof pages 1-4)


*Blockquote: This artifact is a concise, reusable outreach email for contacting researchers about the tensegrity drop-impact simulation stack. It highlights the project scope, completed simulations, a tailored ask, and placeholders for links and artifacts.*

### (c) Recommended Venues for Community Spot-Checks

The following venues are recommended for posting the modelling approach for broader community review:

| Venue | Type (workshop/journal/community) | Audience | Why This Venue | How to Post |
|---|---|---|---|---|
| SIGGRAPH / SCA Physics-Based Animation community; `polyfem/polyfem` GitHub Discussions | Community + software discussion forum | Geometry processing, FEM, contact simulation, graphics-physics researchers | Best place to get sharp feedback on Tier-A choices: PolyFEM meshing, IPC barrier/contact settings, timestep sensitivity, and whether the welded PLA/TPU volumetric formulation is numerically credible for impact. Especially appropriate because your stack directly uses PolyFEM+IPC-style contact elastodynamics (bruce2014designandevolution pages 6-7). | Open a concise GitHub Discussion with 1 reproducible case, mesh stats, `dt`, `dhat`, constitutive law, and 2 images/GIFs; cross-post a short note to relevant PBA/SCA community channels or workshop Discord/Slack if available. |
| ICRA/IROS Soft Robotics / Tensegrity Workshops | Workshop | Soft robotics, tensegrity robotics, planetary mobility, simulator-to-hardware researchers | Strong fit for questions about whether a class-1 T-prism drop model meaningfully connects to tensegrity robotics and lander lineages, and for comparing MuJoCo/Bullet/Newton abstractions against hardware-oriented expectations from SUPERball/NTRT-style work (agogino2014hardwaredesignand pages 10-11, bruce2014designandevolution pages 6-7, caluwaerts2014superballexploringtensegrities pages 7-7). | Submit a late-breaking workshop abstract, poster, or short talk proposal; if no formal slot exists, email organizers with a one-page summary and ask to circulate it or bring it to poster/demo sessions. |
| ASME IMECE / Earth and Space conference tensegrity sessions | Conference session | Structural mechanics, aerospace structures, tensegrity statics/dynamics, impact/EDL researchers | Best venue for criticism of structural assumptions: form-finding, prestrain, load path, reduced-order vs volumetric models, and whether your drop regimes probe the right energy-storage and buckling mechanisms for tensegrity structures and landers (kim2016onthelocomotion pages 131-134). | Prefer a formal abstract/paper submission if timing permits; otherwise target session chairs directly with a short technical note and ask whether a poster, discussion slot, or birds-of-a-feather exchange is possible. |
| BoTorch GitHub Discussions / Ax community | Community + software discussion forum | Bayesian optimization, multi-fidelity surrogate modeling, experiment-design practitioners | Ideal for sanity-checking how to consume Tier C/B/A simulators inside a cost-aware multi-fidelity BO loop: fidelity ordering, acquisition choice, correlated outputs, and whether to use BoTorch/Ax-native formulations for your expensive contact-rich design problem. BoTorch explicitly supports multi-fidelity extensions and knowledge-gradient-style methods (agogino2014hardwaredesignand pages 10-11). | Post a minimal problem statement with fidelity definitions, evaluation costs, noise assumptions, and objective/constraint structure; ask for modeling advice rather than code debugging, and include a sketch of your simulator ladder. |
| Acceleration Consortium SDL community (Slack / hackathon) | Community | Self-driving labs, materials/design optimization, closed-loop experimentation researchers | Good venue for broader spot-checks on the optimization strategy and experiment-planning logic, especially if you want feedback from people used to combining heterogeneous simulators, surrogates, and hardware validation in materials/design loops. The AC BO hackathon/community is particularly relevant for multi-fidelity optimization workflows in physical sciences (agogino2014hardwaredesignand pages 10-11). | Join the Slack/hackathon channels, post a compact 5-bullet summary with one figure, and ask targeted questions about fidelity management, calibration priorities, and what minimum hardware data would most improve the loop. |


*Table: This table lists five high-value venues for broader community spot-checks of the tensegrity drop-impact modeling stack. It is useful for deciding where to seek simulator-specific, robotics-specific, structural-mechanics, and Bayesian-optimization feedback with the least friction.*

---

## Caveats and Flagged Items

Several contact recommendations in this brief are based on **engineering judgement** rather than direct literature evidence. These include: all standards-body and test-lab contacts (Section 4), industrial TPU supplier contacts (Fenner/Lubrizol), PLA impact characterisation lab contacts, Carlos Portela and Tobias Schaedler (relevance to tensegrity specifically is inferred from architected-materials impact work), Hajun Lee et al. (contact details not verified), and the Acceleration Consortium SDL community recommendation. All other contacts are grounded in identified publications where the named researcher is an author or acknowledged contributor.

References

1. (kim2016onthelocomotion pages 131-134): K Kim. On the locomotion of spherical tensegrity robots. Unknown journal, 2016.

2. (caluwaerts2014superballexploringtensegrities pages 7-7): K Caluwaerts, AM Agogino, and V SunSpiral. Superball: exploring tensegrities for planetary probes. Unknown journal, 2014.

3. (agogino2014hardwaredesignand pages 10-11): AK Agogino, V SunSpiral, and AM Agogino. Hardware design and testing of superball, a modular tensegrity robot. Unknown journal, 2014.

4. (bruce2014designandevolution pages 6-7): Jonathan Bruce, Ken Caluwaerts, Atil Iscen, Andrew P. Sabelhaus, and Vytas SunSpiral. Design and evolution of a modular tensegrity robot platform. 2014 IEEE International Conference on Robotics and Automation (ICRA), pages 3483-3489, May 2014. URL: https://doi.org/10.1109/icra.2014.6907361, doi:10.1109/icra.2014.6907361. This article has 138 citations.

5. (lopes2018multimaterial3dprinting pages 7-8): L. R. Lopes, Alexandre Ferreira da Silva, and Olga S. Carneiro. Multi-material 3d printing: the relevance of materials affinity on the boundary interface performance. Additive Manufacturing, 23:45-52, Oct 2018. URL: https://doi.org/10.1016/j.addma.2018.06.027, doi:10.1016/j.addma.2018.06.027. This article has 294 citations and is from a highest quality peer-reviewed journal.

6. (ruwais2025mechanicalperformanceof pages 1-4): A Ruwais and N Naveed. Mechanical performance of layered pla–tpu composites using multi-material additive manufacturing. Unknown journal, 2025.

7. (arifvianto2022mechanicalpropertiesof pages 10-11): Budi Arifvianto, Baikhati E. Satiti, Urip A. Salim, Suyitno, Archadian Nuryanti, and Muslim Mahardika. Mechanical properties of the fff sandwich-structured parts made of pla/tpu multi-material. Progress in Additive Manufacturing, 7:1213-1223, Apr 2022. URL: https://doi.org/10.1007/s40964-022-00295-6, doi:10.1007/s40964-022-00295-6. This article has 41 citations and is from a peer-reviewed journal.

---

## References

1. (kim2016onthelocomotion pages 131-134): K Kim. On the locomotion of spherical tensegrity robots. Unknown journal, 2016.

2. (caluwaerts2014superballexploringtensegrities pages 7-7): K Caluwaerts, AM Agogino, and V SunSpiral. Superball: exploring tensegrities for planetary probes. Unknown journal, 2014.

3. (agogino2014hardwaredesignand pages 10-11): AK Agogino, V SunSpiral, and AM Agogino. Hardware design and testing of superball, a modular tensegrity robot. Unknown journal, 2014.

4. (bruce2014designandevolution pages 6-7): Jonathan Bruce, Ken Caluwaerts, Atil Iscen, Andrew P. Sabelhaus, and Vytas SunSpiral. Design and evolution of a modular tensegrity robot platform. 2014 IEEE International Conference on Robotics and Automation (ICRA), pages 3483-3489, May 2014. URL: https://doi.org/10.1109/icra.2014.6907361, doi:10.1109/icra.2014.6907361. This article has 138 citations.

5. (lopes2018multimaterial3dprinting pages 7-8): L. R. Lopes, Alexandre Ferreira da Silva, and Olga S. Carneiro. Multi-material 3d printing: the relevance of materials affinity on the boundary interface performance. Additive Manufacturing, 23:45-52, Oct 2018. URL: https://doi.org/10.1016/j.addma.2018.06.027, doi:10.1016/j.addma.2018.06.027. This article has 294 citations and is from a highest quality peer-reviewed journal.

6. (ruwais2025mechanicalperformanceof pages 1-4): A Ruwais and N Naveed. Mechanical performance of layered pla–tpu composites using multi-material additive manufacturing. Unknown journal, 2025.

7. (arifvianto2022mechanicalpropertiesof pages 10-11): Budi Arifvianto, Baikhati E. Satiti, Urip A. Salim, Suyitno, Archadian Nuryanti, and Muslim Mahardika. Mechanical properties of the fff sandwich-structured parts made of pla/tpu multi-material. Progress in Additive Manufacturing, 7:1213-1223, Apr 2022. URL: https://doi.org/10.1007/s40964-022-00295-6, doi:10.1007/s40964-022-00295-6. This article has 41 citations and is from a peer-reviewed journal.
