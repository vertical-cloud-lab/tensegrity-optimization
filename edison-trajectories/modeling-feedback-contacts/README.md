# Modeling-feedback contacts (Edison `78fb09a2`)

Edison `LITERATURE_HIGH` task `78fb09a2-bea4-4e7a-ab70-8518fa1b0b81` —
"Prioritised Contact List And Outreach Plan For Tensegrity Drop Impact
Modelling Reviews". Submitted 2026-05-20T16:46:14Z, fetched same session,
`status=success`. ~50 KB formatted answer over 6 sections (Tensegrity
dynamics, Simulator maintainers, Materials/AM, Standards/test labs, BO/MF,
Synthesis with ranked top-10 + email template + venues).

## Top-10 contacts (verbatim ordering from Edison §6(a))

| # | Name | Affiliation | Domain | Why first |
|---:|---|---|---|---|
| 1 | Teseo Schneider | Univ. Victoria / NYU GP | PolyFEM + IPC, contact-rich elastodynamics | Single best person to critique Tier-A IPC barrier (`dhat=5e-5`), implicit stepping (`dt=0.5 ms`), and welded PLA/TPU contact treatment (Schneider 2020; Li 2023). |
| 2 | Julian Rimoli | Georgia Tech | Tensegrity impact tolerance, planetary landing | Best literature anchor for tensegrity impact mechanics + landers; judges whether each tier preserves the mechanisms that matter under impact (Rimoli 2016/2018; Garanger 2021). |
| 3 | Vytas SunSpiral | NASA Ames lineage / IRG | SUPERball, NTRT, lander/EDL | Spot-check whether T-prism + payload-suspension interpretation captures the SUPERball/NTRT lineage; advice on when Bullet/NTRT cable abstractions break down (Caluwaerts 2014; Mirletz 2015). |
| 4 | Tao Du | Tsinghua / formerly MIT CSAIL | DiffPD, differentiable soft-body | Right person to say where DiffPD is a credible Tier-B surrogate vs where contact realism breaks (Du 2021). |
| 5 | Robert E. Skelton | UCSD (emeritus lineage) | Foundational tensegrity statics/dynamics | Foundational sanity-check on class-1 T-prism parameterisation + prestrain sweep (Sultan 2000; Goyal & Skelton 2019). |
| 6 | Keivan Davami | USAFA / AM impact mechanics | 3D-printed tensegrity, dynamic energy absorption | Bridges printable PLA/TPU geometry to validated crashworthiness claims (Davami 2019 + 2025 tensegrity-impact). |
| 7 | Peter I. Frazier | Cornell ORIE | Multi-fidelity Bayesian optimisation | Sanity-check fidelity ordering, cost-aware acquisition, and joint vs separate response models for the BO loop (Wu 2020; Xie 2024). |
| 8 | Daniele Panozzo | NYU Courant / GP Group | PolyFEM ecosystem, geometry processing | Critique gmsh OCC fragment → welded volumetric mesh workflow and meshing/validity checks (Schneider 2019/2022). |
| 9 | Alice M. Agogino | UC Berkeley | Tensegrity robotics, prototyping, hardware validation | Frames crutch-tip vs NASA-lander split for transferable insight; advises on minimum measurements that falsify the sim (Agogino 2014; Chen 2017). |
| 10 | Alessandro Tasora | Univ. Parma / Project Chrono | PyChrono, nonsmooth multibody dynamics | Decide whether PyChrono adds unique value in Tier-C screening or should be deprioritised (Benatti 2019; Mangoni 2019). |

## Recommended venues (Edison §6(c))

1. **SIGGRAPH / SCA Physics-Based Animation community + `polyfem/polyfem`
   GitHub Discussions** — Tier-A meshing / IPC / timestep sensitivity.
2. **ICRA / IROS soft-robotics / tensegrity workshops** — late-breaking
   abstracts; SUPERball/NTRT-style spot-checks.
3. **ASME IMECE / AIAA Earth-and-Space tensegrity sessions** — structural
   assumptions, prestrain, reduced-order vs volumetric.
4. **BoTorch GitHub Discussions / Ax community** — multi-fidelity BO loop
   sanity-check (fidelity ordering, acquisition, correlated outputs).
5. **Acceleration Consortium SDL Slack / hackathon channels** — broader
   spot-checks on the heterogeneous-simulator+hardware loop.

## Files

- `modeling-feedback-contacts-78fb09a2-...md` — full formatted answer
  (~58 KB; 6 sections + caveats + email template).
- `modeling-feedback-contacts-78fb09a2-...json` — raw Edison trajectory
  (~1.5 MB; agent_state + environment_frame + references).
