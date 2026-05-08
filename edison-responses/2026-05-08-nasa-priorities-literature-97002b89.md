# Edison Literature Query — NASA Space Priorities Tie-In to Tensegrity MRG Framework

- **Task ID:** `97002b89-5bad-4112-a1e0-7b924a2b66c1`
- **Job:** `LITERATURE`
- **Submitted:** 2026-05-07
- **Fetched:** 2026-05-08
- **Status:** success
- **Related issues:** #12 (this issue), #13 (NASA Space Grant proposal), #14 (LaTeX scaffold PR)

> Single high-effort literature query connecting the multi-material 3D-printed tensegrity / Bayesian-optimization energy-absorption framework to NASA / aerospace / space exploration priorities. See PR description for the full submitted prompt and section structure.

---

Question: High-effort literature synthesis tying a multi-material 3D-printed tensegrity-inspired energy-absorption research framework to NASA / aerospace / space exploration priorities.

CONTEXT (project framework to map onto NASA priorities):
- Two-year undergraduate-mentored experimental research program.
- Multi-material fused deposition modeling (FDM) using rigid PLA struts coupled with elastomeric TPU tension members to fabricate tensegrity-inspired lattices/cellular architectures.
- Closed-loop, high-throughput physical experimentation (50-100+ specimens) under quasi-static compression AND drop-weight impact, using Bayesian optimization (BO) to recommend the next designs.
- TPU's rate-dependent viscoelastic damping is treated as a feature for impact energy absorption rather than a deviation from idealized cable behavior.
- Goal: tunable, lightweight, deployable, load-limiting protective structures.

REQUEST: Provide a comprehensive, citation-rich literature review (with DOIs / arXiv / NASA TRS / NTRS IDs where possible) that connects this framework to current and emerging NASA / aerospace / space mission needs. Specifically address each of the following, with supporting peer-reviewed and NASA-published references and short critical commentary on relevance, gaps, and opportunities:

1. NASA strategic priorities and roadmaps where tensegrity, deployable, or lightweight energy-absorbing structures are explicitly called out (e.g., NASA Strategic Plan, Space Technology Mission Directorate (STMD) roadmaps, ESI/ECI/NIAC selections, OTPS priorities, Moon-to-Mars architecture, Artemis surface systems, CLPS lunar payloads, Mars Sample Return / EDL, asteroid science, on-orbit servicing/assembly/manufacturing OSAM, in-space manufacturing).

2. NASA-funded and NASA-affiliated tensegrity work — including but not limited to NASA Ames Super Ball Bot / Tensegrity Robotics (Vytas SunSpiral, Adrian Agogino, Atil Iscen), TT-3, planetary surface exploration rovers, landing-impact attenuation concepts — with the most recent (post-2020) follow-on work and any active NIAC / STTR / SBIR awards.

3. Impact and landing-load attenuation for planetary EDL, landers, and crew/cargo payloads: how tensegrity-inspired or 3D-printed cellular/lattice energy absorbers compare to conventional crushable honeycomb, foam, and airbag systems used historically by NASA (e.g., MER airbags, Mars 2020, Orion crew module). Quantitative metrics: specific energy absorption (SEA, J/g), crush efficiency, plateau stress, peak/mean force ratio, strain-rate sensitivity, repeatability/multi-hit.

4. In-space manufacturing (ISM) and on-orbit / lunar surface additive manufacturing relevance: state of multi-material FDM (PLA, TPU, PEEK, ULTEM, ABS) on ISS (Made In Space / Redwire AMF, Refabricator) and prospects for printing tensegrity / lattice energy absorbers on-demand from feedstock; design-for-AM constraints in microgravity / partial gravity.

5. Materials behavior in space-relevant environments: thermal cycling (-150 to +120 C), vacuum outgassing (ASTM E595 for PLA, TPU, TPE), atomic oxygen, UV, ionizing radiation degradation of FDM thermoplastics; published guidance for selecting/ qualifying TPU and PLA for LEO, lunar surface, and cislunar use.

6. Deployable and morphing structures for spacecraft (booms, antennas, solar sails, habitats, shock isolators, MMOD shielding, planetary protection containers) where tensegrity principles or compliant 3D-printed lattices have been proposed or flown; comparison to inflatables (BEAM/LIFE) and origami-inspired structures.

7. Micrometeoroid and orbital debris (MMOD) / hypervelocity impact protection: literature on the role of cellular, lattice, and sandwich structures (including additively manufactured) as Whipple shield enhancements, and any work using tensegrity-inspired multi-stage stand-offs.

8. Bayesian optimization, sequential design of experiments, active learning, and digital-twin-assisted experiment-driven design for aerospace structures and materials — with emphasis on examples published by NASA, AFRL, DARPA, or in AIAA/SciTech, that use BO for lattice, lattice-truss, or energy absorber design. Highlight published BO-for-impact-absorber and BO-for-lattice studies and what objective functions (SEA, peak force, mass) they use.

9. Mentored undergraduate research alignment with NASA workforce / STEM priorities: NASA Space Grant Consortium goals, Artemis Generation workforce pipeline, Established Program to Stimulate Competitive Research (EPSCoR), MUREP, and how a hands-on print-test-optimize loop maps to these objectives.

10. Concrete, defensible "NASA framing" recommendations: 5-10 candidate mission scenarios / use cases (with citations) where a 3D-printed multi-material tensegrity-inspired energy absorber optimized via BO would be most differentiated from incumbent solutions (e.g., lunar lander leg crush cores, CubeSat deployable shock isolators, sample return capsule attenuators, surface habitat impact liners, EVA tool/payload crash structures, rover wheel suspension, planetary penetrator nose cones).

For each of the 10 areas, please provide: (a) 5-15 highly relevant primary citations with DOIs/NTRS IDs, (b) a 1-2 paragraph synthesis, (c) explicit identification of open research gaps that the proposed framework is well-positioned to fill, and (d) suggested NASA program(s) / solicitation(s) the work could target (NIAC Phase I, STMD ECF/ESI, EPSCoR, SBIR/STTR topics, Space Grant fellowship). Emphasize peer-reviewed sources, NASA Technical Reports Server (NTRS) entries, and recent (2018-2025) literature. Where claims are NASA-roadmap or strategy statements, cite the specific NASA document and section.

Deliverable: a single, well-structured, citation-dense report suitable for direct use in (i) a BYU NASA Space Grant Fellowship undergraduate proposal narrative (3-5 pages) and (ii) a revision of an MRG proposal that more explicitly motivates aerospace / space relevance.

## Technical literature synthesis: multi-material FDM tensegrity-inspired energy absorbers aligned to NASA / aerospace priorities (2018–2025 emphasis)

### Executive framing
Your proposed framework—multi-material FDM (rigid PLA struts + viscoelastic TPU tension members) tensegrity-inspired lattices, tested in high-throughput quasi-static and drop-weight impact with Bayesian optimization (BO) recommending next designs—maps onto three recurring NASA needs evidenced in the retrieved corpus: (i) *packable/deployable lightweight structures that also protect payloads from uncertain impacts* (tensegrity NIAC lander/rover line), (ii) *mission resilience via on-demand, in-space additive manufacturing (AM) and recycling* (ISS AMF, Refabricator, FabLab concepts), and (iii) *mass-efficient energy management* across landing/impact attenuation and protection contexts (airbags, crushable honeycomb, deployable energy absorbers, MMOD shielding cores). (caluwaerts2014superballexploringtensegrities pages 1-2, agogino2014hardwaredesignand pages 1-2, adams2004marsexplorationrover pages 1-3, prater2019nasasinspacemanufacturing pages 2-4)

| Area | Key NASA / aerospace need statement(s) | Most relevant references from gathered evidence | Proposed PLA–TPU FDM tensegrity/BO contribution | Key gaps / opportunities |
|---|---|---|---|---|
| 1. NASA priorities / roadmaps | NASA ISM/FabLab work frames on-demand, multi-material manufacturing as enabling “more sustainable and safer exploration,” while in-orbit manufacturing can remove launch-volume and deployable-mechanism constraints; OSAM-2 and related concepts emphasize larger structures made in space rather than stowed-and-deployed hardware (prater2019nasasinspacemanufacturing pages 1-2, prater2017nasa’sinspacemanufacturing pages 12-14, hastie2025onorbitmanufacturingusing pages 12-16) | Prater et al. 2017 AIAA 2017-5277 / DOI:10.2514/6.2017-5277; Prater et al. 2019 IAC-19.D3.2B.5; OSAM-2 NTRS citation 20220007646 as cited by Hastie 2025; NASA R3 RFAs on in-space manufacturing / AM (RFA-015/016/019) (prater2017nasa’sinspacemanufacturing pages 3-5, hastie2025onorbitmanufacturingusing pages 77-81, valcoUnknownyearaeronauticresearchmission pages 9-13) | Positions the project as a dual-use technology for lightweight protective structures and eventually printable, tunable infills/lattices for mission hardware, directly aligning with NASA’s push toward on-demand fabrication and reduced launch packaging penalties | Need stronger direct linkage to official NASA Strategic Plan / STMD roadmap language on deployable protective structures; opportunity to cite section-level roadmap wording in proposal revision |
| 2. NASA-funded tensegrity work | NASA Ames/NIAC SUPERball work explicitly targets combined entry-descent-landing and surface mobility, with packability, payload protection, and impact attenuation central to the concept (caluwaerts2014superballexploringtensegrities pages 1-2, agogino2014hardwaredesignand pages 1-2, agogino2018superballbotstructures pages 4-7) | Caluwaerts et al. 2014 “SUPERball: Exploring Tensegrities for Planetary Probes”; Agogino et al. 2014 hardware paper; Agogino et al. 2018 NIAC final report “Super Ball Bot—Structures for Planetary Landing and Exploration”; Gebara et al. 2019 AIAA SciTech DOI:10.2514/6.2019-0868; Deitrich et al. 2022 Titan rideshare tensegrity rover concept (caluwaerts2014superballexploringtensegrities pages 1-2, agogino2018superballbotstructures pages 1-4, deitrich2022aridesharetensegrity pages 1-6) | Extends NASA tensegrity heritage from robotic macro-structures to manufacturable, specimen-scale architected absorbers that can be systematically tuned, drop-tested, and optimized for protective performance rather than locomotion alone | Post-2020 literature still lacks high-throughput physical design maps for tensegrity-inspired absorbers, especially multi-material printed realizations and rate-dependent polymer members; opportunity for publishable benchmark datasets |
| 3. Planetary landing / impact attenuation | NASA heritage uses airbags, crushable honeycomb, and deployable energy absorbers to limit loads for MER, Orion, and passive entry vehicles; impact metrics include crush stress, mean crushing force, floor acceleration, landing loads, and survivability across terrains (jackson2011experimentalandanalytical pages 86-89, adams2004marsexplorationrover pages 1-3, jackson2014simulatingtheresponse pages 1-2) | Cadogan et al. 2002 Acta Astronautica DOI:10.1016/S0094-5765(01)00215-6; Adams 2004 AIAA 2004-1795 DOI:10.2514/6.2004-1795; Tutt et al. 2009 AIAA 2009-2922 / 2009-2923; Jackson et al. 2014 J. Aerospace Eng. DOI:10.1061/(ASCE)AS.1943-5525.0000357 and 0000358; Cloutier 1966 JSR DOI:10.2514/3.28743 (cloutier1966landingimpactenergy pages 1-2, adams2004marsexplorationrover pages 1-3, jackson2014simulatingtheresponse pages 1-2) | Offers a lightweight alternative with tunable peak-force moderation, recoverable deformation modes, and explicit exploitation of TPU rate dependence under quasi-static and drop-weight loads; BO can optimize SEA / peak force / mass trade spaces faster than one-factor-at-a-time design | Direct apples-to-apples benchmarking versus honeycomb, foam, and airbags is sparse for tensegrity-inspired lattices; need standardized metrics such as SEA, crush efficiency, peak/mean force ratio, multi-hit performance, and terrain sensitivity |
| 4. In-space manufacturing relevance | ISS demonstrations show multimaterial polymer AM, recycling, custom infill generation, and aerospace-grade feedstock development are active NASA priorities; FFF is considered largely compatible with microgravity and useful for tailored infills/foams (prater2019nasasinspacemanufacturing pages 2-4, prater2017nasa’sinspacemanufacturing pages 1-3) | Prater et al. 2017 AIAA 2017-5277 DOI:10.2514/6.2017-5277; Prater et al. 2019 IAC-19.D3.2B.5; Prater et al. 2018 “High Frontier”; Aliberti et al. 2026 Materials Horizons DOI:10.1039/d5mh01403d (prater2019nasasinspacemanufacturing pages 2-4, prater2018thehighfrontier pages 10-17, aliberti2026additivemanufacturingof pages 19-20) | Supports a future vision of on-demand printing of sacrificial or reusable protective cores, shock isolators, and deployable lattice inserts from stocked polymer filaments, with geometric tuning learned terrestrially and later ported to space-capable feedstocks | PLA/TPU themselves are not flight-qualified ISS standards; opportunity is to use low-cost PLA/TPU as terrestrial surrogates to establish geometry/algorithm/design principles transferrable to Ultem/PEEK/PEKK systems |
| 5. Materials in space environments | NASA MISSE work and related reviews show UV, thermal cycling, AO, outgassing, and radiation can alter AM polymer properties; qualification relies on bakeout, mass loss, optical/mechanical post-flight characterization, and environment-specific exposure histories (finckenor2023spaceenvironmentaleffects pages 6-12, finckenor2023spaceenvironmentaleffects pages 12-17, rashed2024ultraperformancepolymerand pages 51-54) | Finckenor & McElderry 2023 MISSE-9/10 NASA TM; Rashed 2024 DOI:10.25439/rmt.27602931; Tserpes 2025 Aerospace DOI:10.3390/aerospace12030215 (finckenor2023spaceenvironmentaleffects pages 6-12, tserpes2025advancesincomposite pages 9-10, rashed2024ultraperformancepolymerand pages 51-54) | Lets the project argue honestly that PLA/TPU are discovery-stage materials for ground analog research, while the real contribution is mechanistic understanding of architecture + viscoelastic member behavior under impact | Major gap: very limited direct PLA/TPU qualification data for LEO/lunar/cislunar service; strong opportunity for follow-on thermal-vacuum, UV, AO, and ASTM E595 screening once topologies are identified |
| 6. Deployable / morphing structures | Space systems need compact stowage with large deployed volume/area; literature covers deployable cabins, booms, hinges, anisogrid lattice spokes, and inflatable protective systems for habitats and robotics (tserpes2025advancesincomposite pages 18-19, dinkel2024inflatableandexpandable pages 14-19, tserpes2025advancesincomposite pages 12-13) | Tserpes 2025 Aerospace DOI:10.3390/aerospace12030215; Dinkel 2024 thesis on inflatable/expandable systems; Hastie 2025 solid-foam in-orbit manufacturing thesis (hastie2025onorbitmanufacturingusing pages 12-16, dinkel2024inflatableandexpandable pages 1-5, tserpes2025advancesincomposite pages 13-15) | Tensegrity-inspired lattices provide a middle ground between rigid deployables and inflatables: compact, lightweight, mechanically robust, and potentially load-limiting without gas retention systems | Few studies compare compliant lattices/tensegrities directly against inflatables or origami for shock protection and deployment robustness; opportunity for mission-specific comparison papers |
| 7. MMOD / hypervelocity protection | Spacecraft sandwich structures and Whipple-like shields benefit from architectures that disperse debris clouds; honeycomb can channel fragments, while open-cell foams and AM cellular cores improve cloud expansion and multifunctionality (schubert2019multifunctionalloadbearingaerostructures pages 8-8, cherniaev2021modelingofhypervelocity pages 1-2, carriere2021hypervelocityimpactson pages 2-4) | Schubert et al. 2018 DOI:10.1051/matecconf/201823300019; Schubert & Dafnis 2019 DOI:10.1051/matecconf/201930407003; Cherniaev 2021 IJIE DOI:10.1016/j.ijimpeng.2021.103901; Singh & Kumar 2024 DOI:10.1007/s12046-024-02467-2 (schubert2018multifunctionalandlightweight pages 3-5, cherniaev2021modelingofhypervelocity pages 1-2, singh2024protectionofwhipple pages 1-2) | While not a hypervelocity shield directly, the framework is relevant to secondary shock/isolation layers, stand-off architectures, and multifunctional interior protective liners that could complement MMOD systems | Virtually no validated tensegrity-inspired stand-off MMOD concepts in the gathered set; opportunity for low-velocity / fragment-cloud analog studies before true HVI testing |
| 8. Bayesian optimization / active learning | BO is sample-efficient for expensive black-box AM experiments and has already been applied to mechanical metamaterials, AM process tuning, and lattice/impact-related design objectives such as stiffness-to-weight or injury/volume tradeoffs (zhang2021bayesianoptimisationfor pages 8-11, zhang2021bayesianoptimisationfor pages 11-14) | Zhang et al. 2021 arXiv DOI:10.48550/arXiv.2107.12809; cited therein: Sharpe et al. constrained BO for mechanical metamaterials; Hertlein et al. weighted objective combining head injury criterion and part volume; Gongora et al. BO reducing experiments ~60× (zhang2021bayesianoptimisationfor pages 8-11, zhang2021bayesianoptimisationfor pages 31-35, zhang2021bayesianoptimisationfor pages 1-4) | Strongly validates the proposed closed-loop print-test-optimize methodology: BO can choose next specimens to maximize information gain or multiobjective performance on SEA, peak force, stiffness, mass, damping, or repeatability | NASA-specific published BO examples for impact absorbers remain limited; opportunity to contribute one of the clearest aerospace-relevant closed-loop datasets linking lattice architecture, rate effects, and protective metrics |
| 9. Workforce / STEM alignment | NASA documents emphasize future workforce development for the Artemis generation, and NASA EPSCoR/Space Grant-type mechanisms value research tied to NASA-relevant topics and student pipelines (valcoUnknownyearaeronauticresearchmission pages 9-13, hastie2025onorbitmanufacturingusing pages 12-16) | Noble et al. 2024 “Implementation Plan for a NASA Integrated Lunar Science Strategy in the Artemis Era”; NASA EPSCoR 2022 R3 NOFO; NASA career / workforce documents retrieved in conversation (hastie2025onorbitmanufacturingusing pages 12-16, valcoUnknownyearaeronauticresearchmission pages 9-13) | A mentored undergraduate loop of CAD–print–test–analyze–BO naturally builds hands-on skills in structures, materials, instrumentation, coding, data science, and mission framing—exactly the cross-training NASA workforce programs seek | Opportunity to sharpen proposal language around Space Grant/EPSCoR outcomes: student ownership of experiments, NASA-relevant dissemination, and pipeline building toward graduate study / aerospace careers |
| 10. Candidate mission scenarios / differentiated use cases | Best-fit scenarios are those needing lightweight, tunable, load-limiting, possibly deployable protection under uncertain impacts: Titan / small-body tensegrity landers, CLPS-class payload protection, lander-leg crush cores, sample-return attenuators, rover payload isolation, habitat liners, CubeSat deployable shock isolators, multifunctional sandwich inserts (caluwaerts2014superballexploringtensegrities pages 1-2, deitrich2022aridesharetensegrity pages 1-6, schubert2019multifunctionalloadbearingaerostructures pages 8-8) | Gebara et al. 2019 AIAA SciTech DOI:10.2514/6.2019-0868; Agogino et al. 2018 NIAC final report; Deitrich et al. 2022 Titan rideshare concept; Jackson et al. 2011/2014 deployable absorber studies; Schubert & Dafnis 2019 DOI:10.1051/matecconf/201930407003 (agogino2018superballbotstructures pages 1-4, jackson2011experimentalandanalytical pages 86-89, schubert2019multifunctionalloadbearingaerostructures pages 1-3) | Most differentiated where incumbent solutions are either single-use crushables, gas-dependent inflatables, or difficult-to-manufacture complex absorbers. The proposed framework enables rapid tailoring of geometry and damping for mission-specific load envelopes | Mission pull is clear, but translation requires: environmental screening, higher-performance feedstocks, validated FE/digital twins, and quantitative benchmarking against incumbent crushable honeycomb / airbag systems |


*Table: This table maps the 10 requested review areas to the most relevant NASA and aerospace need statements, the best-supported references from the gathered evidence, the specific contribution of the proposed multi-material FDM tensegrity-plus-BO framework, and the clearest research gaps. It is designed to be dropped into a proposal or literature review to make the NASA framing concise and defensible.*

---

## 1) NASA strategic priorities/roadmaps explicitly calling out deployable/lightweight or AM-enabled structures

### (a) Highly relevant primary citations (from gathered evidence)
- NASA In-Space Manufacturing (ISM) FabLab concept for ISS (AIAA) (doi:10.2514/6.2017-5277). (prater2017nasa’sinspacemanufacturing pages 3-5, prater2017nasa’sinspacemanufacturing pages 1-3)
- NASA ISM update (IAC-19.D3.2B.5) describing AMF, custom infill, and ISS packaging foams for launch-load survival. (prater2019nasasinspacemanufacturing pages 2-4)
- “High Frontier” NASA ISM overview describing the roadmap toward ISS “Multi-Material” and “FabLab (Metals, Elec.)”. (prater2018thehighfrontier pages 1-6, prater2018thehighfrontier pages 10-17)
- OSAM-2 cited as “first demonstration of structural manufacturing in space” (NTRS citation 20220007646, via secondary reference). (hastie2025onorbitmanufacturingusing pages 77-81)
- In-orbit manufacturing thesis explicitly stating that an in-space-made structure “would not have to deploy” and could be “significantly larger than a traditional deployable structure.” (hastie2025onorbitmanufacturingusing pages 12-16)
- NASA NOFO/R3 content listing “In Space Manufacturing/On Demand Manufacturing of Electronics (ODME)” and AM RFAs (RFA-015/016/019). (valcoUnknownyearaeronauticresearchmission pages 9-13)

### (b) Synthesis (relevance to the proposed framework)
NASA’s ISM/FabLab documentation and associated roadmapping language consistently frames additive manufacturing and recycling as *enabling*, not merely convenient, for sustainable exploration. The Prater et al. NASA/AIAA FabLab paper explicitly sets the goal of expanding on-orbit manufacturing capabilities and highlights manufacturing of large-scale structures “not constrained by launch requirements (i.e. volume),” along with the SBIR-driven ecosystem of polymer, metal, and electronics AM modalities that would populate a future multi-material fabrication lab. (prater2017nasa’sinspacemanufacturing pages 3-5, prater2017nasa’sinspacemanufacturing pages 12-14)

Separately, the in-orbit manufacturing literature in this retrieved set makes an unusually direct and proposal-usable argument about *deployables*: manufacturing a structure in space removes the need for complex deployable mechanisms (and their ground-test burden) and allows larger final geometries. That logic is a natural top-level NASA framing for tensegrity-inspired lattices: they are inherently packable, but they also become *intrinsically manufacturable as lattices/infill* once ISM is mature, making them a credible “bridge technology” between launch-packaged deployables and future “made-to-size” structures. (hastie2025onorbitmanufacturingusing pages 12-16)

### (c) Open gaps your framework fills
- NASA-usable *design maps* linking lattice/tensegrity geometry + multi-material damping to impact/landing metrics are thin in the NASA AM/ISM documents; your high-throughput, BO-driven physical campaign is well positioned to create such datasets and surrogate models. (prater2019nasasinspacemanufacturing pages 2-4, zhang2021bayesianoptimisationfor pages 8-11)
- A key gap in these roadmapping/ISM documents is explicit treatment of *rate-dependent elastomers as functional “cables”* for energy absorption; your approach makes TPU viscoelasticity a design variable rather than a nuisance parameter.

### (d) Candidate NASA programs/solicitations to target
- NIAC Phase I (mission-enabling structure concepts; ties strongly to Super Ball Bot heritage and lander protection concepts). (agogino2018superballbotstructures pages 1-4)
- STMD ISM/OSAM-relevant calls (conceptual alignment evidenced by ISM roadmaps; OSAM-2 cited as structural manufacturing demo). (hastie2025onorbitmanufacturingusing pages 77-81, hastie2025onorbitmanufacturingusing pages 12-16)
- NASA EPSCoR / Rapid Response Research (R3) or jurisdictional EPSCoR calls with AM/materials themes (example NOFO text retrieved). (valcoUnknownyearaeronauticresearchmission pages 9-13)

---

## 2) NASA-funded / NASA-affiliated tensegrity work (Ames SUPERball / Super Ball Bot and follow-ons)

### (a) Highly relevant primary citations
- NASA Ames DTRL: SUPERball NIAC concept; packability + dual-use landing and mobility; drop-test validation; NTRT simulation toolkit. (caluwaerts2014superballexploringtensegrities pages 1-2, agogino2014hardwaredesignand pages 1-2)
- NIAC final report: “Super Ball Bot – Structures for Planetary Landing and Exploration” (NASA Ames). (agogino2018superballbotstructures pages 1-4, agogino2018superballbotstructures pages 4-7)
- Impact attenuation claims and test/simulation program (e.g., survivability to ~15 m/s class impacts; payload protection “like an airbag”). (agogino2014hardwaredesignand pages 1-2, agogino2018superballbotstructures pages 7-11)
- AIAA SciTech: “Tensegrity Ocean World Landers” (doi:10.2514/6.2019-0868) mentioning NIAC/Ames links. (from retrieved paper list; evidence of NIAC/Ames mention in snippet). (gebara2019tensegrityoceanworld)
- NASA TM (2022) rideshare tensegrity rover concept for Titan with NIAC Phase II acknowledgement and NASA LaRC + Ames involvement. (deitrich2022aridesharetensegrity pages 1-6)

### (b) Synthesis
NASA’s strongest explicit, mission-coupled tensegrity line in the retrieved evidence is the Ames NIAC SUPERball/Super Ball Bot effort: tensegrity is framed as a *system-level architecture* that merges landing impact attenuation, payload protection, and post-landing mobility, while remaining compactly stowed for launch and robust to arbitrary landing orientations. (agogino2014hardwaredesignand pages 1-2, agogino2018superballbotstructures pages 4-7)

The key transfer to your project is conceptual but technically direct: NASA’s tensegrity lander claims depend on compliance, multi-path load sharing, and controlled deformation to dissipate impact energy. Your research framework operationalizes this into a materials-and-architecture “knob set” suitable for statistical design (50–100+ specimens) and BO, shifting the tensegrity narrative from single-prototype demonstrations to *experimentally learned design rules* that can be repurposed for NASA protective structures beyond robotics. (caluwaerts2014superballexploringtensegrities pages 1-2, zhang2021bayesianoptimisationfor pages 8-11)

### (c) Open gaps & opportunities
- Post-2018 NASA tensegrity evidence in this retrieval is largely concept reports; there is a gap in *systematic, high-throughput* experimental characterization of tensegrity-inspired unit cells/architectures under both quasi-static and impact loads.
- Little public evidence (in this run) of NASA-ready qualification pathways for polymeric tension members (creep, thermal-vacuum, UV/AO) in tensegrity landers—an opportunity for your framework to generate “early TRL” risk-reduction datasets and to propose a materials transition plan (PLA/TPU → PEI/PEKK/PEEK-class). (finckenor2023spaceenvironmentaleffects pages 12-17, rashed2024ultraperformancepolymerand pages 51-54)

### (d) Target programs
- NIAC Phase I/II (direct lineage). (agogino2018superballbotstructures pages 1-4, deitrich2022aridesharetensegrity pages 1-6)
- SBIR/STTR topics in in-space manufacturing, structures, or autonomous systems (the ISM/FabLab ecosystem is heavily SBIR-linked). (prater2017nasa’sinspacemanufacturing pages 3-5, prater2018thehighfrontier pages 10-17)

---

## 3) Impact and landing-load attenuation (EDL, landers, payloads): tensegrity/lattice vs. heritage honeycomb/foam/airbags

### (a) Primary citations (heritage + quantitative benchmarks)
- MER airbag landing loads testing: 52 vacuum-chamber drop tests, up to ~25 m/s, Mars-like pressure, rock hazards; measured peak linear acceleration, angular rates, tendon loads, stroke. (doi:10.2514/6.2004-1795). (adams2004marsexplorationrover pages 1-3)
- Pathfinder airbag development/evaluation (doi:10.1016/S0094-5765(01)00215-6). (cadogan2002developmentandevaluation)
- Orion land-landing airbag impact attenuation development (doi:10.2514/6.2009-2922) and related Orion airbag work. (tutt2009asummaryof)
- Crushable material framework: crushing stress vs density, usable strain; anisotropy tradeoffs; payload fraction optimization (doi:10.2514/3.28743). (cloutier1966landingimpactenergy pages 1-2, cloutier1966landingimpactenergy pages 7-7)
- Composite honeycomb deployable energy absorber (DEA): designed ~20 psi crush stress, measured ~19.8 psi average; drop tests targeted 20 g floor acceleration and achieved average floor accelerations below limit; terrain dependence noted. (jackson2011experimentalandanalytical pages 86-89)
- Simulation/testing of composite honeycomb energy absorber and multi-terrain impacts (doi:10.1061/(ASCE)AS.1943-5525.0000357). (jackson2014simulatingtheresponse pages 1-2)
- Planetary payload landing system analysis using honeycomb/corrugated crush tubes; drop simulations 50–100 ft/s; honeycomb cell redesign yielded ~62% reduction in peak acceleration (doi:10.1061/9780784485736.045). (mennu2024analysisofa pages 1-13)

### (b) Synthesis
NASA’s heritage landing attenuation toolbox in the retrieved set spans (i) airbags (Pathfinder/MER, and Orion studies), (ii) crushable honeycombs and anisotropic crushables as a general “crush stress–density–stroke” design space, and (iii) deployable honeycomb energy absorbers validated in multi-terrain drops with explicit acceleration limits. These systems define the benchmark metrics NASA cares about: peak/mean acceleration (or floor acceleration), stroke-out avoidance, multi-terrain robustness, and quantifiable crush stress/mean crushing force design targets. (jackson2011experimentalandanalytical pages 86-89, mennu2024analysisofa pages 1-13, adams2004marsexplorationrover pages 1-3)

Tensegrity-inspired and architected lattice absorbers offer a different “control surface” than classic honeycomb: you can program deformation paths via topology and by distributing compliance between struts and tension members. Your explicit decision to treat TPU’s rate-dependent viscoelasticity as a *feature* is aligned with the need to moderate peak forces and shape the force–displacement (or force–time) response in impacts. The best NASA-relevant comparison point is therefore not a purely static crush curve, but a multiobjective trade space (SEA or absorbed energy per mass, peak/mean force ratio, rebound, repeatability/multi-hit) across quasi-static and drop-weight regimes. (cho2025designoflatticebased pages 4-7, adams2004marsexplorationrover pages 1-3)

### (c) Gaps your framework can fill
- Standardized cross-comparisons between tensegrity-inspired lattices and heritage systems (honeycomb, airbags) using a shared metric set (EA/MCF, SEA, peak/mean force ratio, crush efficiency, multi-hit) remain underdeveloped in the NASA-facing literature retrieved here.
- Heritage systems rely on extensive test campaigns (e.g., MER’s 52 vacuum drop tests); your BO-driven approach can reduce test counts by prioritizing designs likely to improve objectives or reduce uncertainty, which is particularly valuable when tests are costly (drop tower, thermal-vac). (adams2004marsexplorationrover pages 1-3, zhang2021bayesianoptimisationfor pages 8-11)

### (d) Target programs
- NIAC Phase I (novel attenuation architectures for planetary landers and ocean worlds). (agogino2018superballbotstructures pages 1-4, caluwaerts2014superballexploringtensegrities pages 1-2)
- STMD technology maturation calls focused on EDL/landing technologies (not retrieved as a roadmap document in this run, but strongly implied by heritage and NIAC linkages).

---

## 4) In-space manufacturing (ISM) / on-orbit and lunar-surface AM: multi-material FDM relevance

### (a) Primary citations
- NASA FabLab multimaterial development for ISS (AIAA 2017-5277) including discussion of powder hazards and preference for wire/foil/ingot; hybrid additive/subtractive systems. (prater2017nasa’sinspacemanufacturing pages 3-5)
- NASA ISM update with explicit feedstocks including ULTEM 9085, ABS, HDPE, PLA, PC; custom slicing/infill; 3D-printed foams/packaging for launch-load survival; rack power/mass/volume constraints. (prater2019nasasinspacemanufacturing pages 2-4)
- “High Frontier” roadmap highlighting “ISS: Multi-Material” and “FabLab (Metals, Elec.)” planning, recycling, and “just in time” manufacturing framing. (prater2018thehighfrontier pages 1-6, prater2018thehighfrontier pages 10-17)
- ISS FFF/AMF and Refabricator context summarized in aerospace review, including PLA/ABS and higher-performance PEI/PEEK/Ultem feedstocks and thermal constraints. (doi:10.1039/d5mh01403d). (aliberti2026additivemanufacturingof pages 19-20)

### (b) Synthesis
NASA’s ISM documents in this retrieved set establish that fused filament fabrication (FFF/FDM) is already operationally relevant on ISS (AMF) and that NASA is actively exploring recycling loops (Refabricator) and a future integrated FabLab combining polymer, metal, and electronics manufacturing. Importantly for your work, NASA’s own ISM update explicitly discusses the ability to generate *custom infill structures* and prints “foams with various infill patterns,” connecting directly to your architected-lattice energy absorber concept. (prater2019nasasinspacemanufacturing pages 2-4)

From a proposal standpoint, this enables a defensible pathway narrative: (1) perform terrestrial discovery on inexpensive PLA/TPU to learn topology–performance relationships and validate BO/closed-loop protocols, then (2) port the learned design principles to NASA-relevant ISM polymers (PEI/Ultem, PEKK/PEEK) that are actively being tested in ISS and MISSE campaigns. (prater2019nasasinspacemanufacturing pages 2-4, finckenor2023spaceenvironmentaleffects pages 12-17)

### (c) Gaps
- The NASA ISM sources retrieved here do not yet provide application-specific “design-for-ISM” rules for impact/energy absorbers (e.g., minimum printable wall angles, joint strategies for multi-material tension members, or microgravity-specific quality control for elastomers). Your high-throughput loop can identify which geometric features are robust to printing variability, and which require process control.

### (d) Target programs
- STMD/OSAM and ISM technology calls; OSAM-2 is explicitly cited as a structural manufacturing demo in the retrieved set. (hastie2025onorbitmanufacturingusing pages 77-81)
- SBIR/STTR topics aligned to multi-material manufacturing, recycling, and on-orbit repair (FabLab ecosystem). (prater2017nasa’sinspacemanufacturing pages 3-5, prater2018thehighfrontier pages 10-17)

---

## 5) Materials behavior in space-relevant environments: thermal cycling, vacuum/outgassing, AO/UV/radiation

### (a) Primary citations
- MISSE-9/10 AM-materials exposure/qualification workflow (NASA TM): thermal-vac bakeout (~60 °C, ~1×10−6 torr, 24 h) and “>1% mass loss” as limited-use flag; AO/UV exposure contexts; pre/post optical, electrical, mechanical characterization; materials include Ultem 1010/9085, PEKK variants, PC-ISO. (finckenor2023spaceenvironmentaleffects pages 12-17, finckenor2023spaceenvironmentaleffects pages 6-12)
- Space-environment mechanisms for polymers/composites: chain scission/crosslinking, AO oxidation, microcracking under thermal cycling; long-duration exposure effects. (doi:10.3390/aerospace12030215). (tserpes2025advancesincomposite pages 9-10)
- Review emphasizing limited simulated-space testing of FFF polymers and listing thermal cycling defect modes (delamination/microcracks) and radiation/UV/AO surface-dominated degradation. (doi:10.25439/rmt.27602931). (rashed2024ultraperformancepolymerand pages 51-54)

### (b) Synthesis
NASA’s MISSE-9/10 results and methodologies provide the most proposal-useful “qualification language” in this retrieved set: thermal-vac bakeout practices, mass-loss screening thresholds, and the suite of pre/post measurements that matter for polymers in LEO. Even though MISSE polymers in these excerpts are higher-performance (Ultem, PEKK, PC-ISO) rather than PLA/TPU, the methodology is directly transferrable as a future risk-reduction plan for any polymeric energy absorber intended for space. (finckenor2023spaceenvironmentaleffects pages 12-17)

For your framework, the key materials insight is that TPU’s viscoelastic damping and PLA’s stiffness are performance drivers under impact—but their suitability is environment-dependent. A defensible NASA framing is to treat PLA/TPU as *ground analog discovery materials* for architecture learning, while planning a migration to NASA-tested AM polymers (Ultem/PEKK/PEEK class) once topologies are selected. (aliberti2026additivemanufacturingof pages 19-20, rashed2024ultraperformancepolymerand pages 51-54)

### (c) Gaps
- Direct PLA/TPU space-environment qualification (ASTM E595 values, AO erosion rates, UV embrittlement, thermal-cycling hysteresis under repeated impacts) is not present in the retrieved evidence set; this is a concrete open need if the material pair is intended for flight.

### (d) Target programs
- STMD materials and structures maturation efforts, and MISSE-like exposure experiments (proposal can reference MISSE protocol as the next-phase screening approach). (finckenor2023spaceenvironmentaleffects pages 12-17)

---

## 6) Deployable and morphing structures: tensegrity principles, compliant lattices, inflatables/origami comparisons

### (a) Primary citations
- Deployable structures overview for space: booms, antennas, solar panels/sails; composite hinges; deployable booms; anisogrid lattice spokes for deployable reflectors (review). (tserpes2025advancesincomposite pages 12-13, tserpes2025advancesincomposite pages 13-15)
- Inflatable/expandable protective concepts (thesis): inflatable protection jacket using regolith for shielding; inflatable trailer for night/dust storms; inflatable antenna concepts. (dinkel2024inflatableandexpandable pages 14-19)
- In-orbit manufacturing argument that making structures in space reduces deployable mechanism reliance and required ground testing. (hastie2025onorbitmanufacturingusing pages 12-16)

### (b) Synthesis
Space deployables span rigidized booms/hinges and inflatables; both classes share the core need of high deployed size from small stowed volume. Tensegrity offers a third path: a load-bearing network whose compliance can be tuned, and which can protect payloads during deployment mishaps or impacts. NASA’s own tensegrity NIAC work is explicitly built around this “pack–deploy–land–protect” paradigm. (agogino2014hardwaredesignand pages 1-2, agogino2018superballbotstructures pages 4-7)

Your multi-material tensegrity-inspired lattices are particularly relevant to the “deployable protective structure” niche: they can act as deployable shock isolators, bumpers, or liners that do not require gas retention (unlike inflatables) and can be designed for controlled load limiting (unlike many stiff deployables). (agogino2018superballbotstructures pages 4-7, jackson2011experimentalandanalytical pages 86-89)

### (c) Gaps
- The retrieved deployable/inflatable literature does not yet provide strong, quantitative comparisons between compliant lattice/tensegrity protective structures and inflatable protective structures under impact and repeated use; your drop-weight + quasi-static campaign could generate such comparative datasets.

### (d) Target programs
- NIAC (deployable/morphing structures for exploration systems). (agogino2018superballbotstructures pages 1-4)
- STMD structures/deployables and manufacturing calls (ISM/FabLab pathway). (prater2018thehighfrontier pages 1-6)

---

## 7) MMOD / hypervelocity impact protection: lattices/cellular structures as Whipple enhancements

### (a) Primary citations
- Honeycomb channeling effect in sandwich structures and advantage of open-cell foams for multishock fragment–ligament interactions; CT-based realistic foam geometry modeling; comparisons to NASA experimental data. (doi:10.1016/j.ijimpeng.2021.103901). (cherniaev2021modelingofhypervelocity pages 1-2)
- Additively manufactured aluminum cellular cores in CFRP sandwich panels can improve debris shielding without weight penalty; truss/lattice cores promote debris cloud expansion; need more tests. (doi:10.1051/matecconf/201930407003). (schubert2019multifunctionalloadbearingaerostructures pages 8-8, schubert2019multifunctionalloadbearingaerostructures pages 1-3)
- Conventional honeycomb cores can perform worse than Whipple due to channeling; AM cores enable graded density and local inserts (e.g., tungsten/polyethylene) for shielding. (doi:10.1051/matecconf/201823300019). (schubert2018multifunctionalandlightweight pages 3-5)
- Review of Whipple shield enhancements (e.g., foams, UHMWPE stuffing, STFs); highlights cellular and foam components as protective elements. (doi:10.1007/s12046-024-02467-2). (singh2024protectionofwhipple pages 1-2)

### (b) Synthesis
The MMOD literature retrieved here contains a clear message that is relevant to your “architected cellular protection” framing even though your tests are low-velocity: *core topology controls fragmentation/energy spreading*. Honeycomb “channeling” is repeatedly flagged as a weakness, while open-cell foams and AM cellular cores can improve cloud expansion and multishock interactions, increasing protective capability at comparable areal density. (schubert2018multifunctionalandlightweight pages 3-5, cherniaev2021modelingofhypervelocity pages 1-2)

A defensible NASA framing for your work is therefore not that PLA/TPU tensegrity lattices are hypervelocity shields, but that they can serve as (i) interior secondary impact/fragment catch layers, (ii) stand-off and load-limiting spacers, and (iii) multifunctional cores that also provide vibration/impact attenuation for sensitive payloads inside a spacecraft bus. Your BO-driven methodology can be repurposed to optimize geometric features (cell topology, gradients, multi-stage stand-offs) that MMOD studies identify as critical. (schubert2019multifunctionalloadbearingaerostructures pages 8-8, zhang2021bayesianoptimisationfor pages 8-11)

### (c) Gaps
- The retrieved MMOD sources call for more testing and clearer rankings among cellular core types; there is minimal evidence of “tensegrity-inspired” multi-stage stand-offs being systematically studied.

### (d) Target programs
- NASA spacecraft structures/protection programs and SBIR topics related to MMOD shielding and multifunctional structures (AM cores + fabrics are explicitly discussed as emerging directions). (schubert2019multifunctionalloadbearingaerostructures pages 1-3)

---

## 8) Bayesian optimization / sequential DoE / active learning for aerospace structures & materials

### (a) Primary citations
- BO for sequential experimental design in AM (arXiv:2107.12809; doi:10.48550/arXiv.2107.12809), including limited but explicit BO-in-AM landscape and metamaterial/lattice design examples (stiffness-to-weight, head injury criterion + volume). (zhang2021bayesianoptimisationfor pages 8-11, zhang2021bayesianoptimisationfor pages 11-14)
- BO framing as sample-efficient, balancing exploration/exploitation via acquisition functions (EI/UCB/KG), with batch BO and “ask-tell” workflows suitable for physical test loops. (zhang2021bayesianoptimisationfor pages 4-8)

### (b) Synthesis
The retrieved BO review is directly supportive of your proposed methodology: it motivates BO precisely for “expensive” experiments and emphasizes that AM design spaces are large and nonlinear. It also identifies prior BO applications to metamaterial/lattice design, including objectives that combine injury metrics with volume—conceptually close to NASA impact attenuation goals where peak acceleration (or injury risk proxy) must be traded against mass and packaging. (zhang2021bayesianoptimisationfor pages 8-11)

Your specific contribution is to execute an unusually proposal-ready closed-loop experiment system: print → test (quasi-static + impact) → update surrogate → recommend next design, with objectives explicitly tied to NASA-relevant metrics such as absorbed energy/SEA per mass, peak-to-mean force ratio, stroke utilization/crush efficiency, and repeatability/multi-hit behavior.

### (c) Gaps
- BO literature is rich in process optimization but thinner (in this retrieved set) in *experiment-driven BO for impact absorbers* with fully physical drop-weight testing and multiobjective constraints. Your project would be publishable as a benchmark dataset and methodology paper.

### (d) Target programs
- STMD / NASA center collaborations emphasizing “autonomy” and “on-demand manufacturing” and DOE/ML workflows (supported generally by BO-in-AM framing). (zhang2021bayesianoptimisationfor pages 8-11)

---

## 9) Mentored undergraduate research alignment with NASA workforce/STEM priorities (Space Grant/EPSCoR/MUREP framing)

### (a) Primary citations
- NASA EPSCoR R3 NOFO (retrieved) as a direct example of NASA-sponsored research mechanisms and evaluation framing. (valcoUnknownyearaeronauticresearchmission pages 9-13)
- Artemis-era NASA Integrated Lunar Science Strategy implementation plan includes explicit “Artemis generation” workforce development language in the retrieved snippet. (hastie2025onorbitmanufacturingusing pages 12-16)

### (b) Synthesis
Within the retrieved NASA documents, workforce development is explicitly framed as critical for the Artemis era and the “Artemis generation.” A mentored undergraduate program with hands-on design, fabrication, instrumentation, and data/optimization aligns with the kind of cross-disciplinary, applied skill building NASA consistently seeks: systems thinking, experimental rigor, software/data skills, and mission relevance. (hastie2025onorbitmanufacturingusing pages 12-16)

Additionally, EPSCoR-style mechanisms (as represented by the retrieved R3 NOFO) are structurally aligned with projects that produce publishable research while building regional NASA-relevant capacity and student pipelines. Your closed-loop print-test-optimize workflow is especially well suited to undergraduate ownership because each cycle yields a concrete artifact (specimen + data + model update) and can be modularized into student-led subprojects (fixture design, sensing, FE calibration, BO implementation). (valcoUnknownyearaeronauticresearchmission pages 9-13)

### (c) Gaps
- The retrieved set does not include a Space Grant program guide or MUREP-specific solicitation text; proposal writers should add these primary NASA education program citations in the next literature pass.

### (d) Target programs
- BYU NASA Space Grant fellowship framing (to be supplemented with direct Space Grant documents in the next pass).
- NASA EPSCoR (R3 and standard EPSCoR calls). (valcoUnknownyearaeronauticresearchmission pages 9-13)

---

## 10) Concrete “NASA framing” recommendations: differentiated mission scenarios/use cases

### (a) Mission scenarios grounded in retrieved NASA/aerospace evidence
1. **Tensegrity lander/rover payload protection for ocean worlds / Titan rideshare concepts**: directly aligned to NIAC tensegrity lander/rover line and Titan rideshare rover concept; your work supplies unit-cell/architecture datasets and load-limiting inserts for payload bays. (caluwaerts2014superballexploringtensegrities pages 1-2, deitrich2022aridesharetensegrity pages 1-6)
2. **CLPS-class payload shock isolators / packaging inserts**: NASA ISM work explicitly treats printed foams/infill structures as launch-load protection for ISS hardware; your tuned lattices are a more designable successor. (prater2019nasasinspacemanufacturing pages 2-4)
3. **Lander leg crush cores / passive attenuators (Moon/Mars small payloads)**: honeycomb and crush-tube systems are analyzed for planetary payloads with speed/pitch trade studies; your approach could optimize “low-peak-force, high-stroke” responses with multi-material damping. (mennu2024analysisofa pages 1-13, cloutier1966landingimpactenergy pages 1-2)
4. **Sample return capsule internal attenuators** (analogous to passive entry vehicles): NASA and aerospace literature on crushable honeycomb energy absorbers and externally deployable DEAs provide the benchmark context. (jackson2011experimentalandanalytical pages 86-89, jackson2014simulatingtheresponse pages 1-2)
5. **On-orbit manufactured sacrificial bumpers / interior protective liners**: AMF/FabLab documents show multi-material polymer printing and recycling; your framework supplies geometry libraries optimized for energy absorption per mass/volume. (prater2017nasa’sinspacemanufacturing pages 1-3, prater2019nasasinspacemanufacturing pages 2-4)
6. **CubeSat / smallsat multifunctional sandwich inserts** (vibration + impact + MMOD-adjacent benefits): MMOD literature shows core topology matters and AM cores are attractive for graded density and localized inserts; your low-velocity optimization can target “secondary shock” mitigation layers. (schubert2018multifunctionalandlightweight pages 3-5, schubert2019multifunctionalloadbearingaerostructures pages 1-3)

### (b) What is most differentiated vs incumbents
- **Multi-hit / reusable protection** versus single-use crushables: tensegrity-inspired architectures can be designed for recoverable deformation, especially when TPU is used intentionally for damping and hysteresis, potentially enabling repeated impacts in handling/operations scenarios.
- **Load limiting / peak-force control** using architecture + rate dependence rather than only geometry or only material.
- **Closed-loop design under uncertainty**: BO enables rapid convergence to designs that meet acceleration limits across variable impact conditions with fewer tests than traditional parametric sweeps. (zhang2021bayesianoptimisationfor pages 8-11, adams2004marsexplorationrover pages 1-3)

### (c) Research gaps that make these scenarios defensible proposal opportunities
- Lack of standardized performance datasets for tensegrity-inspired multi-material lattices under both quasi-static and drop-weight loads using NASA-relevant metrics.
- Need for an explicit “materials transition plan” from PLA/TPU to ISS/space-qualified polymers (Ultem/PEKK/PEEK) plus screening via MISSE-like protocols. (finckenor2023spaceenvironmentaleffects pages 12-17)

### (d) Solicitations/programs to target (evidence-backed)
- **NIAC Phase I**: direct tensegrity-lander precedent and mission concept alignment. (agogino2018superballbotstructures pages 1-4, deitrich2022aridesharetensegrity pages 1-6)
- **SBIR/STTR**: FabLab/ISM ecosystem is SBIR-driven across polymers/metals/electronics and is a natural home for multi-material protective inserts and printing of tuned infills/lattices. (prater2017nasa’sinspacemanufacturing pages 3-5, prater2018thehighfrontier pages 10-17)
- **EPSCoR**: mechanism supports university-centered capability building aligned with NASA needs; an example NOFO is in the retrieved set. (valcoUnknownyearaeronauticresearchmission pages 9-13)

---

## Notes on evidence limitations (important for proposal defensibility)
1. This tool-based retrieval successfully captured substantial *NASA ISM/FabLab* and *NASA tensegrity NIAC* evidence, plus *heritage landing attenuation* (MER airbags; crushable honeycomb/DEA) and *MMOD core topology* evidence.
2. It did **not** retrieve (in this run) the full, official STMD Technology Roadmaps (TA documents), NASA Strategic Plan sections, Moon-to-Mars architecture docs, or detailed NIAC/STTR award listings post-2020. Those should be added in a follow-on NTRS- and TechPort-focused retrieval pass for maximum “explicit NASA roadmap” citation density.
3. PLA/TPU-specific space qualification evidence (ASTM E595 values, AO/UV/radiation degradation data) was not directly found here; MISSE protocols and high-performance polymer results were retrieved, so a credible plan is to treat PLA/TPU as terrestrial discovery materials and propose a follow-on qualification downselect.

---

### Short “drop-in” paragraph for NASA relevance (proposal-ready)
NASA has repeatedly invested in (i) *tensegrity-based deployable/packable structures for planetary entry, landing, and payload protection* through NIAC-funded SUPERball/Super Ball Bot work at NASA Ames, and (ii) *in-space manufacturing and recycling* on ISS through the Additive Manufacturing Facility, Refabricator, and planned multimaterial FabLab concepts. These efforts highlight a need for lightweight structures that can be tightly stowed or printed on demand, then reliably limit loads during uncertain impact events. The proposed two-year undergraduate-mentored program develops multi-material (PLA–TPU) tensegrity-inspired lattices and uses closed-loop, high-throughput quasi-static and drop-weight testing with Bayesian optimization to rapidly map and optimize energy absorption performance (absorbed energy/SEA, mean crushing force, peak-force moderation, and repeatability). The outcome is a validated design methodology and data library for tunable, load-limiting protective structures that directly complements NASA heritage impact attenuation systems (airbags and crushable honeycomb) while aligning with NASA’s emerging on-orbit manufacturing capabilities. (agogino2014hardwaredesignand pages 1-2, prater2019nasasinspacemanufacturing pages 2-4, adams2004marsexplorationrover pages 1-3, zhang2021bayesianoptimisationfor pages 8-11)

References

1. (caluwaerts2014superballexploringtensegrities pages 1-2): K Caluwaerts, AM Agogino, and V SunSpiral. Superball: exploring tensegrities for planetary probes. Unknown journal, 2014.

2. (agogino2014hardwaredesignand pages 1-2): AK Agogino, V SunSpiral, and AM Agogino. Hardware design and testing of superball, a modular tensegrity robot. Unknown journal, 2014.

3. (adams2004marsexplorationrover pages 1-3): Douglas Adams. Mars exploration rover airbag landing loads testing and analysis. 45th AIAA/ASME/ASCE/AHS/ASC Structures, Structural Dynamics &amp;amp; Materials Conference, Apr 2004. URL: https://doi.org/10.2514/6.2004-1795, doi:10.2514/6.2004-1795. This article has 22 citations.

4. (prater2019nasasinspacemanufacturing pages 2-4): T Prater, J Edmunson, M Fiske, and F Ledbetter. Nasa's in-space manufacturing project: update on manufacturing technologies and materials to enable more sustainable and safer exploration. Unknown journal, 2019.

5. (prater2019nasasinspacemanufacturing pages 1-2): T Prater, J Edmunson, M Fiske, and F Ledbetter. Nasa's in-space manufacturing project: update on manufacturing technologies and materials to enable more sustainable and safer exploration. Unknown journal, 2019.

6. (prater2017nasa’sinspacemanufacturing pages 12-14): Tracie J. Prater, Mary J. Werkheiser, Alexander Jehle, Frank Ledbetter, Quincy Bean, Mardi Wilkerson, Howard Soohoo, and Brent Hipp. Nasa’s in-space manufacturing project: development of a multimaterial fabrication laboratory for the international space station. ArXiv, Sep 2017. URL: https://doi.org/10.2514/6.2017-5277, doi:10.2514/6.2017-5277. This article has 38 citations.

7. (hastie2025onorbitmanufacturingusing pages 12-16): PGB Hastie. On-orbit manufacturing using solid foams. Unknown journal, 2025.

8. (prater2017nasa’sinspacemanufacturing pages 3-5): Tracie J. Prater, Mary J. Werkheiser, Alexander Jehle, Frank Ledbetter, Quincy Bean, Mardi Wilkerson, Howard Soohoo, and Brent Hipp. Nasa’s in-space manufacturing project: development of a multimaterial fabrication laboratory for the international space station. ArXiv, Sep 2017. URL: https://doi.org/10.2514/6.2017-5277, doi:10.2514/6.2017-5277. This article has 38 citations.

9. (hastie2025onorbitmanufacturingusing pages 77-81): PGB Hastie. On-orbit manufacturing using solid foams. Unknown journal, 2025.

10. (valcoUnknownyearaeronauticresearchmission pages 9-13): MJ Valco. Aeronautic research mission directorate (armd). Unknown journal, Unknown year.

11. (agogino2018superballbotstructures pages 4-7): AK Agogino, V SunSpiral, and D Atkinson. Super ball bot-structures for planetary landing and exploration. Unknown journal, 2018.

12. (agogino2018superballbotstructures pages 1-4): AK Agogino, V SunSpiral, and D Atkinson. Super ball bot-structures for planetary landing and exploration. Unknown journal, 2018.

13. (deitrich2022aridesharetensegrity pages 1-6): N Deitrich, KM Baldonado, A Khan, J Cook, and L Rizzo. A rideshare tensegrity rover concept to explore titan's lands and oceans. Unknown journal, 2022.

14. (jackson2011experimentalandanalytical pages 86-89): KE Jackson, S Kellas, LG Horta, and MS Annett. Experimental and analytical evaluation of a composite honeycomb deployable energy absorber. Unknown journal, 2011.

15. (jackson2014simulatingtheresponse pages 1-2): K. E. Jackson, E. L. Fasanella, and M. A. Polanco. Simulating the response of a composite honeycomb energy absorber. i: dynamic crushing of components and multiterrain impacts. Journal of Aerospace Engineering, 27:424-436, May 2014. URL: https://doi.org/10.1061/(asce)as.1943-5525.0000357, doi:10.1061/(asce)as.1943-5525.0000357. This article has 15 citations and is from a peer-reviewed journal.

16. (cloutier1966landingimpactenergy pages 1-2): GERALD J. CLOUTIER. Landing impact energy absorption using anisotropic crushable materials. Journal of Spacecraft and Rockets, 3:1755-1761, Dec 1966. URL: https://doi.org/10.2514/3.28743, doi:10.2514/3.28743. This article has 10 citations and is from a peer-reviewed journal.

17. (prater2017nasa’sinspacemanufacturing pages 1-3): Tracie J. Prater, Mary J. Werkheiser, Alexander Jehle, Frank Ledbetter, Quincy Bean, Mardi Wilkerson, Howard Soohoo, and Brent Hipp. Nasa’s in-space manufacturing project: development of a multimaterial fabrication laboratory for the international space station. ArXiv, Sep 2017. URL: https://doi.org/10.2514/6.2017-5277, doi:10.2514/6.2017-5277. This article has 38 citations.

18. (prater2018thehighfrontier pages 10-17): T Prater, N Werkheiser, and K Morgan. The high frontier: a new age of manufacturing in space. Unknown journal, 2018.

19. (aliberti2026additivemanufacturingof pages 19-20): Francesca Aliberti, Raffaele Longo, Marialuigia Raimondo, Roberto Pantani, Luigi Vertuccio, and Liberata Guadagno. Additive manufacturing of polymers and composites for applications in aerospace and aeronautics. Materials Horizons, 13:532-588, Jan 2026. URL: https://doi.org/10.1039/d5mh01403d, doi:10.1039/d5mh01403d. This article has 2 citations and is from a domain leading peer-reviewed journal.

20. (finckenor2023spaceenvironmentaleffects pages 6-12): MM Finckenor and JR McElderry. Space environmental effects on additively manufactured materials–results from misse-9 and misse-10. Unknown journal, 2023.

21. (finckenor2023spaceenvironmentaleffects pages 12-17): MM Finckenor and JR McElderry. Space environmental effects on additively manufactured materials–results from misse-9 and misse-10. Unknown journal, 2023.

22. (rashed2024ultraperformancepolymerand pages 51-54): Kaifur Rashed. Ultra-performance polymer and composites in extrusion based additive manufacturing with space applications. Text, Jan 2024. URL: https://doi.org/10.25439/rmt.27602931, doi:10.25439/rmt.27602931. This article has 1 citations and is from a peer-reviewed journal.

23. (tserpes2025advancesincomposite pages 9-10): Konstantinos Tserpes. Advances in composite materials for space applications: a comprehensive literature review. Aerospace, Mar 2025. URL: https://doi.org/10.3390/aerospace12030215, doi:10.3390/aerospace12030215. This article has 27 citations.

24. (tserpes2025advancesincomposite pages 18-19): Konstantinos Tserpes. Advances in composite materials for space applications: a comprehensive literature review. Aerospace, Mar 2025. URL: https://doi.org/10.3390/aerospace12030215, doi:10.3390/aerospace12030215. This article has 27 citations.

25. (dinkel2024inflatableandexpandable pages 14-19): A Dinkel. Inflatable and expandable systems for extraterrestrial exploration and protection. Unknown journal, 2024.

26. (tserpes2025advancesincomposite pages 12-13): Konstantinos Tserpes. Advances in composite materials for space applications: a comprehensive literature review. Aerospace, Mar 2025. URL: https://doi.org/10.3390/aerospace12030215, doi:10.3390/aerospace12030215. This article has 27 citations.

27. (dinkel2024inflatableandexpandable pages 1-5): A Dinkel. Inflatable and expandable systems for extraterrestrial exploration and protection. Unknown journal, 2024.

28. (tserpes2025advancesincomposite pages 13-15): Konstantinos Tserpes. Advances in composite materials for space applications: a comprehensive literature review. Aerospace, Mar 2025. URL: https://doi.org/10.3390/aerospace12030215, doi:10.3390/aerospace12030215. This article has 27 citations.

29. (schubert2019multifunctionalloadbearingaerostructures pages 8-8): Martin Schubert and Anthanasios Dafnis. Multifunctional load-bearing aerostructures with integrated space debris protection. MATEC Web of Conferences, 304:07003, Dec 2019. URL: https://doi.org/10.1051/matecconf/201930407003, doi:10.1051/matecconf/201930407003. This article has 14 citations.

30. (cherniaev2021modelingofhypervelocity pages 1-2): Aleksandr Cherniaev. Modeling of hypervelocity impact on open cell foam core sandwich panels. International Journal of Impact Engineering, 155:103901, Sep 2021. URL: https://doi.org/10.1016/j.ijimpeng.2021.103901, doi:10.1016/j.ijimpeng.2021.103901. This article has 32 citations and is from a domain leading peer-reviewed journal.

31. (carriere2021hypervelocityimpactson pages 2-4): Riley Carriere and Aleksandr Cherniaev. Hypervelocity impacts on satellite sandwich structures—a review of experimental findings and predictive models. Applied Mechanics, 2:25-45, Feb 2021. URL: https://doi.org/10.3390/applmech2010003, doi:10.3390/applmech2010003. This article has 26 citations.

32. (schubert2018multifunctionalandlightweight pages 3-5): Martin Schubert, Sara Perfetto, Anthanasios Dafnis, Heiko Atzrodt, and Dirk Mayer. Multifunctional and lightweight load-bearing composite structures for satellites. ArXiv, 233:00019, Jan 2018. URL: https://doi.org/10.1051/matecconf/201823300019, doi:10.1051/matecconf/201823300019. This article has 8 citations.

33. (singh2024protectionofwhipple pages 1-2): Pradeep Kumar Singh and Manoj Kumar. Protection of whipple shield against hypervelocity impact of space debris: a review. Sādhanā, Mar 2024. URL: https://doi.org/10.1007/s12046-024-02467-2, doi:10.1007/s12046-024-02467-2. This article has 7 citations.

34. (zhang2021bayesianoptimisationfor pages 8-11): Mimi Zhang, Andrew Parnell, Dermot Brabazon, and Alessio Benavoli. Bayesian optimisation for sequential experimental design with applications in additive manufacturing. Preprint, Jan 2021. URL: https://doi.org/10.48550/arxiv.2107.12809, doi:10.48550/arxiv.2107.12809. This article has 25 citations.

35. (zhang2021bayesianoptimisationfor pages 11-14): Mimi Zhang, Andrew Parnell, Dermot Brabazon, and Alessio Benavoli. Bayesian optimisation for sequential experimental design with applications in additive manufacturing. Preprint, Jan 2021. URL: https://doi.org/10.48550/arxiv.2107.12809, doi:10.48550/arxiv.2107.12809. This article has 25 citations.

36. (zhang2021bayesianoptimisationfor pages 31-35): Mimi Zhang, Andrew Parnell, Dermot Brabazon, and Alessio Benavoli. Bayesian optimisation for sequential experimental design with applications in additive manufacturing. Preprint, Jan 2021. URL: https://doi.org/10.48550/arxiv.2107.12809, doi:10.48550/arxiv.2107.12809. This article has 25 citations.

37. (zhang2021bayesianoptimisationfor pages 1-4): Mimi Zhang, Andrew Parnell, Dermot Brabazon, and Alessio Benavoli. Bayesian optimisation for sequential experimental design with applications in additive manufacturing. Preprint, Jan 2021. URL: https://doi.org/10.48550/arxiv.2107.12809, doi:10.48550/arxiv.2107.12809. This article has 25 citations.

38. (schubert2019multifunctionalloadbearingaerostructures pages 1-3): Martin Schubert and Anthanasios Dafnis. Multifunctional load-bearing aerostructures with integrated space debris protection. MATEC Web of Conferences, 304:07003, Dec 2019. URL: https://doi.org/10.1051/matecconf/201930407003, doi:10.1051/matecconf/201930407003. This article has 14 citations.

39. (prater2018thehighfrontier pages 1-6): T Prater, N Werkheiser, and K Morgan. The high frontier: a new age of manufacturing in space. Unknown journal, 2018.

40. (agogino2018superballbotstructures pages 7-11): AK Agogino, V SunSpiral, and D Atkinson. Super ball bot-structures for planetary landing and exploration. Unknown journal, 2018.

41. (cloutier1966landingimpactenergy pages 7-7): GERALD J. CLOUTIER. Landing impact energy absorption using anisotropic crushable materials. Journal of Spacecraft and Rockets, 3:1755-1761, Dec 1966. URL: https://doi.org/10.2514/3.28743, doi:10.2514/3.28743. This article has 10 citations and is from a peer-reviewed journal.

42. (mennu2024analysisofa pages 1-13): Matlock M. Mennu, Jacob B. Putnam, and Justin D. Littell. Analysis of a landing system for planetary payloads utilizing passive energy absorbing composite structure. Earth and Space 2024, pages 483-493, Oct 2024. URL: https://doi.org/10.1061/9780784485736.045, doi:10.1061/9780784485736.045. This article has 0 citations.

43. (cho2025designoflatticebased pages 4-7): Jaryong Cho, Eun Suk Lee, Jeong Ho Kim, Chang-Yull Lee, and Jin Yeon Cho. Design of lattice-based energy-absorbing structure for enhancing the crashworthiness of advanced air mobility. Aerospace, 12:332, Apr 2025. URL: https://doi.org/10.3390/aerospace12040332, doi:10.3390/aerospace12040332. This article has 7 citations.

44. (zhang2021bayesianoptimisationfor pages 4-8): Mimi Zhang, Andrew Parnell, Dermot Brabazon, and Alessio Benavoli. Bayesian optimisation for sequential experimental design with applications in additive manufacturing. Preprint, Jan 2021. URL: https://doi.org/10.48550/arxiv.2107.12809, doi:10.48550/arxiv.2107.12809. This article has 25 citations.
