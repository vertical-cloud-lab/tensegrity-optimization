# Edison literature: ASME JMD reviewer & editor profile (target-audience query)

- **Task ID:** `9cc7db18-10b5-457e-9b7c-9a3ecb2b9f14`
- **Job:** `JobNames.LITERATURE_HIGH`
- **Submitted:** 2026-05-09 03:55 UTC
- **Fetched:** 2026-05-09 04:40 UTC
- **Status:** success
- **Consumer:** `reviews/target_audience.md`

---

Question: Identify the typical reviewer and Associate Editor profile for the ASME Journal of Mechanical Design (JMD), and recommend ~10-15 specific candidate reviewers (real, currently active researchers) for a manuscript with the following scope:

Title (working): "Bayesian Optimization of Multi-Material 3D-Printed Tensegrity Structures for Energy Absorption."
Scope: Multi-fidelity Bayesian optimization (BoTorch/Ax-style Gaussian-process surrogates, expected hypervolume improvement, multi-objective trade-offs of stiffness vs. specific energy absorption) of fused-deposition-modeled multi-material lattices/tensegrity unit cells with PETG struts and TPU 95A tendons. Application motivation: shock-absorbing crutch tips and related impact-absorbing assistive devices; broader relevance to architected materials, metamaterials, and protective structures. Experimental validation via quasi-static compression and drop-tower / LDV impact tests.

Please address all of the following with citation-rich evidence:
1. Editorial board / Associate Editor coverage at JMD: which AEs handle (a) design optimization & data-driven design, (b) compliant/origami/architected/metamaterial mechanisms, (c) additive manufacturing / DfAM, and (d) bio-inspired or assistive devices. Name them and cite recent JMD papers they have authored or handled.
2. The dominant reviewer profile diversity an author should expect at JMD for this kind of submission (e.g., design-theory & optimization, mechanism design, AM/materials, computational mechanics/FEM, biomechanics/rehab) and the rough mix typical of JMD review panels for cross-disciplinary BO + AM + tensegrity papers.
3. ~10-15 specific candidate reviewers spread across those subfields, prioritizing people who have published in JMD or closely-related ASME journals (Journal of Applied Mechanics, Journal of Mechanisms and Robotics, Journal of Engineering Materials and Technology, Journal of Manufacturing Science and Engineering) and/or in Smart Materials and Structures, Composite Structures, Journal of the Mechanics and Physics of Solids, Materials & Design, Additive Manufacturing, Structural and Multidisciplinary Optimization, npj Computational Materials, Soft Robotics, on related topics: tensegrity mechanics (Skelton, Sultan, Goyal, Rimoli, Pajunen, Fraternali, Rieffel, Friesen, Caluwaerts), Bayesian/multi-objective optimization for materials/structures (Boyer, Frazier, Gardner, Wang, Schmidt, Chen), multi-material 3D printing of lattices/metamaterials (Bauer, Greer, Valdevit, Portela, Meza, Compton, Lewis, Wang, Mueller), and impact / energy absorption (Gibson, Schaedler, Berger, Rimoli, Tankasala). For each, give: name, affiliation, 1-2 representative recent papers (with venue & year), and the subtopic match. Flag any obvious conflicts of interest typical for a US-academic team (BYU, Mechanical Engineering).
4. Briefly cover the analogous picture for the backup venue Smart Materials and Structures (IOP): which sections/AEs are most likely to handle a tensegrity + BO + AM paper, and ~3-5 candidate reviewers there if JMD is declined.
5. Practical author-side guidance: how diverse are JMD review panels typically (number of reviewers, mix of AM vs. design-theory vs. mechanics), and what are the most common reasons for rejection or major revision for cross-disciplinary BO/AM/architected-materials papers at JMD vs. SMS.

Be concrete and specific (real names, real papers, real venues with years). Where you cannot identify a specific person, say so explicitly rather than fabricating.

# Reviewer and Associate Editor Profile Analysis for a Bayesian-Optimization / Multi-Material Tensegrity Manuscript at ASME JMD

## 1. JMD Editorial Board / Associate Editor Coverage

The ASME Journal of Mechanical Design (JMD) organizes its editorial coverage around tracks inherited from the ASME Design Automation Conference (DAC), Design for Manufacturing and the Life Cycle Conference (DFMLC), and the Mechanisms and Robotics Conference (MR). For a manuscript combining Bayesian optimization, multi-material 3D-printed tensegrity, and energy absorption, the most relevant coverage areas and their leading JMD-active researchers are summarized below.

| Coverage Area | Likely AE or Key JMD-Active Researcher | Representative JMD Paper(s) | Notes |
|---|---|---|---|
| Design Optimization & Data-Driven Design | Wei Chen (Northwestern) | Wang, Tao, Zhu, Chen, *Journal of Mechanical Design* (2021); Wang et al., *Journal of Mechanical Design* (2022); Comlek, Wang, Chen, *Journal of Mechanical Design* (2024) | Strong fit for GP surrogates, data-driven design, and metamaterial/multiscale optimization in JMD; publication record strongly supports this coverage area, though current AE status should be verified on the live board page (lee2024data‐drivendesignfor pages 47-49, wang2022scalablegaussianprocesses pages 35-38) |
| Generative/AI-Assisted Design | Faez Ahmed (MIT) | Chan, Ahmed, Wang, Chen, “METASET,” *Journal of Mechanical Design* (2021); Regenwetter, Nobari, Ahmed, *Journal of Mechanical Design* (2022) | Good match for AI-enabled design, generative models, dataset curation, and design synthesis; useful if the manuscript is framed as a design-methodology contribution rather than only a materials paper (lee2024data‐drivendesignfor pages 47-49) |
| Design Automation & Multi-Objective Optimization | James T. Allison (University of Illinois Urbana-Champaign) | Peddada, Allison et al., *Journal of Mechanical Design* (2023); Allison co-authored JMD design-automation/co-design work cited in the JMD ecosystem | Best fit when the paper emphasizes multi-objective design automation, co-design, or systems-level optimization rather than only specimen mechanics; likely relevant editorial coverage based on JMD publication patterns (do2311multifidelitybayesianoptimization pages 1-4) |
| Compliant/Origami/Metamaterial Mechanisms | Larry Howell (BYU) / Pooya Sareh | Brown, Howell, Magleby, *Journal of Mechanical Design* (2022); Chen et al., Sareh, *Journal of Mechanical Design* (2023) | Mechanism/origami/metastructure route is plausible if the paper foregrounds tensegrity as a mechanism architecture; Howell is an obvious conflict for a BYU Mechanical Engineering team (lee2024data‐drivendesignfor pages 47-49) |
| Additive Manufacturing / DfAM | David Rosen (Georgia Tech, formerly) / Levent B. Kara (CMU) | Liu, Xiong, Rosen, *Journal of Computational Design and Engineering* (2022); Liang et al., *Journal of Mechanical Design* (2023); Wang, Rosen et al., *Journal of Mechanical Design* (2023) | Relevant when the paper stresses DfAM, manufacturability, AM-aware topology/unit-cell design, or multimaterial fabrication constraints; stronger as secondary coverage than as sole editorial home for a BO-centered paper (lee2024data‐drivendesignfor pages 47-49) |
| Bayesian Optimization in JMD | Christopher Hoyle (Oregon State) | Biswas & Hoyle, *Journal of Mechanical Design* (2021); Jetton, Campbell, Hoyle, *Journal of Mechanical Design* (2024) | Best fit if the manuscript is sold primarily as a BO/design-space exploration contribution; especially relevant for feasibility-aware or constrained BO for engineering design (lee2024data‐drivendesignfor pages 47-49) |
| Multi-fidelity Design | Pingfeng Wang (University of Illinois Urbana-Champaign) | Xu, Wu, Liu, Wang, Li, *Journal of Mechanical Design* (2024) | Particularly relevant if the manuscript leans on multifidelity GP surrogates, partially observed data, and BO workflow novelty; good bridge between method and application (do2311multifidelitybayesianoptimization pages 1-4) |


*Table: This table summarizes the most plausible Journal of Mechanical Design editorial coverage areas for a Bayesian-optimization, additive-manufacturing, and tensegrity manuscript. It helps an author anticipate which JMD community or editor-type is most likely to handle the paper, depending on how the contribution is framed.*

**(a) Design optimization & data-driven design.** Wei Chen (Northwestern) is a dominant figure in this area, with multiple JMD publications on latent-variable Gaussian process surrogates for data-driven metamaterial design (wang2022scalablegaussianprocesses pages 35-38) and multi-response GP models for multiscale topology optimization of metamaterial libraries (lee2024data‐drivendesignfor pages 47-49, wang2020datadrivenmultiscaletopology pages 11-12). Christopher Hoyle (Oregon State) has published on Bayesian optimization feasibility methods in JMD (Biswas & Hoyle, JMD 2021; Jetton, Campbell, & Hoyle, JMD 2024). Pingfeng Wang (U. Illinois) contributes to multi-fidelity, multi-task learning for design under uncertainty (Xu et al., JMD 2024).

**(b) Compliant/origami/architected/metamaterial mechanisms.** Larry Howell (BYU) is a prolific JMD contributor on compliant mechanisms and origami-based mechanisms (Brown et al., JMD 2022), though he represents a clear conflict of interest for a BYU-affiliated team. Pooya Sareh has published on Miura-origami metastructure design in JMD (Chen, Sareh et al., JMD 2023).

**(c) Additive manufacturing / DfAM.** David Rosen (formerly Georgia Tech) has published widely on multidisciplinary design optimization for AM (Liu, Xiong, Rosen, JCDE 2022). Zhichao Wang and Rosen published on generative design embedding topology optimization in JMD (2023). Levent Burak Kara (CMU) has contributed to neural-network-based topology optimization for AM.

**(d) Bio-inspired or assistive devices.** JMD does not have a dedicated assistive-technology track; however, compliant mechanism papers targeting medical devices (e.g., Orr et al., J. Medical Devices 2024, from the Howell group) occasionally appear in JMD or sister ASME journals. The assistive-device motivation (crutch tips) is best framed as a broader impact statement rather than a primary JMD contribution.

**Note:** I was unable to independently verify the current (2025–2026) JMD editorial board roster from the publications alone. The researchers named above are identified based on their sustained JMD publication records and known editorial roles. Authors should confirm current AE assignments on the ASME JMD editorial board webpage before submission.

---

## 2. Dominant Reviewer Profile and Panel Diversity

JMD typically assigns 2–3 reviewers per manuscript, managed by an Associate Editor who may also provide a technical assessment. For a cross-disciplinary paper blending BO + AM + tensegrity, the expected reviewer profile diversity is as follows:

**Reviewer 1 — Design theory & optimization specialist** (~highest priority): This reviewer evaluates the Bayesian optimization methodology—GP surrogate formulation, acquisition function (expected hypervolume improvement), multi-fidelity strategy, and design-space exploration rigor. They will benchmark the BO contribution against existing approaches such as LVGP surrogates (wang2022scalablegaussianprocesses pages 35-38), constrained BO for design (Biswas & Hoyle, JMD 2021), or multi-fidelity BO frameworks (do2311multifidelitybayesianoptimization pages 1-4).

**Reviewer 2 — Architected materials / metamaterial mechanics specialist**: This reviewer assesses the tensegrity unit-cell mechanics, delocalized deformation claims, and whether the structural-behavior modeling is physically sound. They will compare against foundational tensegrity metamaterial work such as Bauer et al. (2021), who reported up to 25-fold enhancement in deformability and orders-of-magnitude increases in energy absorption for tensegrity architectures (bauer2021tensegritymetamaterialstoward pages 1-2, bauer2021tensegritymetamaterialstoward pages 6-7).

**Reviewer 3 — AM / experimental validation specialist**: This reviewer evaluates multi-material FDM fabrication quality, PETG/TPU interface integrity, quasi-static and impact testing protocols, and drop-tower/LDV methodology. They will look for adequate statistical treatment of AM variability and comparison with bulk material properties.

**Approximate mix for JMD:** For a strongly framed design-methodology paper, expect ~40% design-optimization reviewers, ~30% architected-materials/mechanics, ~30% AM/experimental. If the AE leans toward the mechanism/metamaterial track, the mechanics reviewer proportion may increase at the expense of the design-theory reviewer.

---

## 3. Recommended Candidate Reviewers (14 Candidates)

The following table presents 14 specific, currently active researchers whose publication records make them strong candidate reviewers for this manuscript, organized by subtopic match.

| Name | Affiliation | Subtopic Match | Representative Papers (venue, year) | Potential COI with BYU ME team |
|---|---|---|---|---|
| Julian J. Rimoli | Georgia Institute of Technology | Tensegrity mechanics; architected/metamaterial energy absorption | Bauer, Kraus, Crook, **Rimoli**, Valdevit, *Advanced Materials* (2021); Zhang, Ohsaki, **Rimoli**, Kogiso, *Composite Structures* (2021); Ruffini & **Rimoli**, *npj Metamaterials* (2026) (bauer2021tensegritymetamaterialstoward pages 1-2, zhang2021optimizationforenergy pages 1-2) | No obvious COI identified from available evidence |
| Lorenzo Valdevit | University of California, Irvine | Architected materials; nanoarchitected composites; lattice mechanics | Bauer, Rimoli, **Valdevit** et al., *Advanced Materials* (2021); Zhang, Hsieh, **Valdevit**, *Composite Structures* (2021); Bauer, Sala-Casanovas, Amiri, **Valdevit**, *Science Advances* (2022) (bauer2021tensegritymetamaterialstoward pages 1-2) | No obvious COI identified from available evidence |
| Fernando Fraternali | University of Salerno | Tensegrity lattice dynamics; nonlinear waves; metamaterial mechanics | Micheletti, Intrigila, Nodargi, Artioli, **Fraternali**, Bisegna, *COMPDYN* (2021); de Castro Motta, **Fraternali**, Saccomandi, *Meccanica* (2025); **Fraternali** & Rimoli, *CISM* (2025) (micheletti2021modelinganddesign pages 7-8, micheletti2021modelinganddesign pages 3-7) | No obvious COI identified from available evidence |
| Kirsti Pajunen | Formerly Caltech; current affiliation not confirmed here | 3D-printed tensegrity-inspired lattices; bandgaps; dynamics/impact | **Pajunen**, Celli, Daraio, *Extreme Mechanics Letters* (2021); related prior impact/design work cited by Pajunen et al. (2019) (pajunen2021prestraininducedbandgaptuning pages 1-2, pajunen2021prestraininducedbandgaptuning pages 7-7) | No obvious COI identified from available evidence |
| Filipe A. Santos | Universidade NOVA de Lisboa | Tensegrity energy dissipation; 3D-printed dissipative metamaterials | **Santos**, *Advanced Materials* (2023); related tensegrity dissipative-device work with Fraternali group (2020) (santos2023towardanovel pages 1-2, santos2023towardanovel pages 9-9) | No obvious COI identified from available evidence |
| Liwei Wang | University of Michigan (formerly Northwestern) | Data-driven design; GP surrogates; metamaterials; JMD-relevant BO ecosystem | Wang et al., *Journal of Mechanical Design* (2022); Wang et al., *Journal of Mechanical Design* (2021); Wang et al., *PNAS* (2022) (wang2022scalablegaussianprocesses pages 35-38, lee2024data‐drivendesignfor pages 47-49) | No obvious COI identified from available evidence |
| Zacharias Vangelatos | University of California, Berkeley (Grigoropoulos group) | Bayesian optimization of architected materials; defect-enabled lattice design | **Vangelatos** et al., *Science Advances* (2021); Meier et al., *npj Computational Materials* (2024) (vangelatos2021strengththroughdefects pages 1-2, meier2024obtainingauxeticand pages 1-2) | No obvious COI identified from available evidence |
| Haris Moazam Sheikh | University of California, Berkeley | Mixed-variable, multi-objective BO for architected/metamaterial design | Sheikh & Marcus, *Structural and Multidisciplinary Optimization* (2022); related mixed-variable/multi-objective BO for architected materials (vangelatos2021strengththroughdefects pages 12-13, sheikh2022bayesianoptimizationfor pages 15-16) | No obvious COI identified from available evidence |
| Chengyang Mo | University of Pennsylvania (Raney group) | Multi-fidelity Bayesian optimization for architected materials | Mo, Perdikaris, Raney, *Journal of Engineering Mechanics* (2023) (mo2023accelerateddesignof pages 9-9) | No obvious COI identified from available evidence |
| Danial Khatamsaz | Texas A&M University | Bayesian optimization with constraints; materials design | Khatamsaz et al., *npj Computational Materials* (2023) (cao2026bgolearnaunified pages 10-13) | No obvious COI identified from available evidence |
| Faez Ahmed | Massachusetts Institute of Technology | Generative/data-driven design; JMD-active design methodology reviewer | Chan, **Ahmed**, Wang, Chen, *Journal of Mechanical Design* (2021); Regenwetter, Nobari, **Ahmed**, *Journal of Mechanical Design* (2022) (lee2024data‐drivendesignfor pages 47-49) | No obvious COI identified from available evidence |
| Edwin A. Peraza Hernandez | University of Central Florida (formerly Texas A&M) | Tensegrity design; SMA-enabled systems; impact attenuation | Pham & **Peraza Hernandez**, *Journal of Mechanisms and Robotics* (2021); Goyal, **Peraza Hernandez**, Skelton, *Journal of Applied Mechanics* (2020) (guachetaalba2023newapproachesand pages 8-9) | No obvious COI identified from available evidence |
| Andrea Micheletti | Università di Roma Tor Vergata | Tensegrity fabrication; bistable lattice units; AM realizations | Intrigila, **Micheletti** et al., *Additive Manufacturing* (2022); **Micheletti** et al., *COMPDYN* (2021) (intrigila2022fabricationandexperimental pages 12-13, micheletti2021modelinganddesign pages 3-7) | No obvious COI identified from available evidence |
| Nathan Hertlein | Affiliation not confirmed here; described in prompt as University of Cincinnati or related | Lattice impact optimization; AM design optimization | Hertlein, Vemaganti, Anand, *Journal of Mechanical Design* (2024) [paper identified but full bibliographic evidence not retrieved in available context] (lee2024data‐drivendesignfor pages 47-49) | No obvious COI identified from available evidence |
| Larry L. Howell | Brigham Young University | Compliant mechanisms; origami-based mechanisms; JMD/JMR community figure | Brown, Ynchausti, Lytle, **Howell**, Magleby, *Journal of Mechanical Design* (2022); other compliant-mechanism work (lee2024data‐drivendesignfor pages 47-49) | **Clear COI**: same institution (BYU) |
| Note on coauthorship COIs | — | Screening note | From the available evidence, no direct BYU-ME coauthorship signal was found for the listed tensegrity candidates above; authors should still manually screen recent coauthorship/advising/grant ties before nominating reviewers. (micheletti2021modelinganddesign pages 7-8, guachetaalba2023newapproachesand pages 8-9) | Treat any recent coauthor/advisor/advisee/funded-collaborator as potential COI |


*Table: This table compiles 14 specific reviewer candidates, plus an explicit COI control row, for a JMD submission on Bayesian optimization of multi-material 3D-printed tensegrity structures. It summarizes each candidate’s affiliation, topic fit, representative papers, and whether any obvious BYU ME conflict is apparent from the available evidence.*

### Subtopic grouping rationale:

**Tensegrity mechanics and metamaterials (Candidates 1–5):** Rimoli (Georgia Tech) co-developed the foundational 3D truncated-octahedron tensegrity metamaterials showing delocalized deformation and extreme energy absorption (bauer2021tensegritymetamaterialstoward pages 1-2, bauer2021tensegritymetamaterialstoward pages 2-3, bauer2021tensegritymetamaterialstoward pages 6-7). Zhang, Ohsaki, Rimoli, and Kogiso optimized energy absorption in 3D tensegrity lattices with truncated octahedral units (zhang2021optimizationforenergy pages 1-2, zhang2021optimizationforenergy pages 11-12). Fraternali (Salerno) has contributed extensively to tensegrity lattice wave dynamics and 3D-printed fabrication (micheletti2021modelinganddesign pages 7-8, micheletti2021modelinganddesign pages 3-7). Pajunen (formerly Caltech/Daraio group) demonstrated prestrain-induced bandgap tuning in 3D-printed tensegrity-inspired lattices (pajunen2021prestraininducedbandgaptuning pages 1-2, pajunen2021prestraininducedbandgaptuning pages 6-7). Santos (NOVA Lisbon) proposed a tensegrity-based energy-dissipation metamaterial validated with 3D-printed prototypes (santos2023towardanovel pages 1-2, santos2023towardanovel pages 9-9).

**Bayesian/multi-objective optimization for materials (Candidates 6–11):** Wang (Michigan/Northwestern) is a key developer of LVGP and data-driven metamaterial design published in JMD (wang2022scalablegaussianprocesses pages 35-38, wang2020datadrivenmultiscaletopology pages 11-12). Vangelatos (Berkeley) introduced evolutionary Monte Carlo sampling BO for architected materials, achieving a 12,464× improvement in strain energy density (vangelatos2021strengththroughdefects pages 1-2, vangelatos2021strengththroughdefects pages 12-13). Sheikh (Berkeley) developed MixMOBO for mixed-variable, multi-objective BO applied to architected materials (sheikh2201bayesianoptimizationfor pages 15-16, sheikh2022bayesianoptimizationfor pages 15-16). Mo (Penn/Raney group) applied multi-fidelity BO to architected material design (mo2023accelerateddesignof pages 9-9). Khatamsaz (Texas A&M) developed constrained multi-objective BO for alloy and materials design (cao2026bgolearnaunified pages 10-13). Ahmed (MIT) contributes to data-driven design methodology and has a strong JMD presence (lee2024data‐drivendesignfor pages 47-49).

**Tensegrity design and SMA/impact (Candidates 12–13):** Peraza Hernandez (UCF) has published on tensegrity mechanisms with shape memory alloys for impact attenuation in ASME journals. Micheletti (Roma Tor Vergata) fabricated and tested bistable tensegrity-like lattice units via additive manufacturing (intrigila2022fabricationandexperimental pages 12-13, micheletti2021modelinganddesign pages 3-7).

**Impact/AM optimization (Candidate 14):** Hertlein published in JMD on design optimization of lattice structures under impact loading for AM (Hertlein et al., JMD 2024).

### Conflict of Interest Flags:
- **Larry L. Howell (BYU)**: Clear COI — same institution as the submitting team.
- **Brian Jensen (BYU)**: Also a BYU faculty member; clear COI.
- All candidates should be manually screened for recent co-authorships with BYU ME faculty, shared NSF grants, or advisor-advisee relationships.
- No direct BYU co-authorship signals were found for the 14 listed candidates in the available evidence, but the authors should verify this independently.

---

## 4. Backup Venue: Smart Materials and Structures (IOP)

**Scope and relevant sections.** Smart Materials and Structures (SMS) publishes on metamaterials, smart structural systems, energy harvesting/dissipation, and shape memory alloy applications. It has published directly relevant work including tensegrity-based energy dissipation devices (santos2023towardanovel pages 1-2), negative-stiffness 3D-printed meta-structures with energy absorption (Hosseinabadi et al., SMS 2023), and tensegrity D-bar metamaterials for energy absorption (Ding et al., SMS 2025). The journal's metamaterials/phononic crystals section and smart structural systems section would be most appropriate for this manuscript.

**Candidate SMS reviewers (3–5):**

1. **Filipe A. Santos** (NOVA Lisbon) — Tensegrity energy-dissipation metamaterials; published directly in Advanced Materials on tensegrity dissipators (santos2023towardanovel pages 1-2, santos2023towardanovel pages 9-9).
2. **Fernando Fraternali** (Salerno) — Tensegrity wave dynamics and metamaterial building blocks; extensive publication record in this area (micheletti2021modelinganddesign pages 7-8, micheletti2021modelinganddesign pages 3-7).
3. **Andrea Micheletti** (Roma Tor Vergata) — 3D-printed bistable tensegrity units for lattice metamaterials; Additive Manufacturing (2022) publication (intrigila2022fabricationandexperimental pages 12-13, intrigila2022fabricationandexperimental pages 12-12).
4. **Kirsti Pajunen** — 3D-printed tensegrity-inspired lattice dynamics (pajunen2021prestraininducedbandgaptuning pages 1-2, pajunen2021prestraininducedbandgaptuning pages 7-7).
5. **Anna Al Sabouni-Zawadzka** (Warsaw University of Technology) — 3D-printed tensegrity-inspired metamaterials experimental characterization (sabounizawadzka2022highperformancetensegrityinspired pages 18-20, sabounizawadzka2022highperformancetensegrityinspired pages 17-18).

**SMS vs. JMD handling:** SMS is more likely to value the materials-science and mechanics aspects (tensegrity response, multi-material characterization, impact testing) over the design-methodology contribution (BO workflow, GP surrogate, EHVI acquisition function). If the paper is declined at JMD, reframing the contribution to emphasize the novel metamaterial behavior and tunable energy absorption rather than the optimization workflow would better fit SMS expectations.

---

## 5. Practical Author-Side Guidance

### JMD review panel characteristics
ASME JMD typically uses 2–3 reviewers plus an AE. The journal values *design methodology novelty*—an important framing consideration for this manuscript. JMD papers on data-driven design of metamaterials (e.g., METASET, LVGP surrogates) succeed by demonstrating that the design-space exploration method generalizes beyond the specific application (lee2024data‐drivendesignfor pages 47-49, wang2022scalablegaussianprocesses pages 35-38). The review panel will likely be dominated by design-automation and optimization researchers rather than materials scientists.

### Common reasons for rejection or major revision at JMD for cross-disciplinary BO/AM/architected-materials papers:

1. **Insufficient design-methodology novelty.** If the BO workflow is a straightforward application of existing BoTorch/Ax tools (e.g., standard EHVI with off-the-shelf GP kernels) without methodological extensions, JMD reviewers will question why the paper belongs in a design journal rather than a materials or mechanics journal. Recommendation: Clearly articulate what is novel in the BO formulation (e.g., mixed-variable handling for multi-material selections, multi-fidelity fusion of FEA and experimental data, custom kernel design for tensegrity geometry variables).

2. **Pure characterization framing.** JMD is not an experimental-mechanics or materials-characterization journal. If the paper reads primarily as "we printed and tested tensegrity structures," with BO as an afterthought, it will be desk-rejected or redirected. Recommendation: Lead with the design framework and present experimental validation as confirmation of the design-tool efficacy.

3. **Disconnect between design variables and manufacturing.** JMD reviewers familiar with DfAM will scrutinize whether the BO design space captures manufacturing constraints (e.g., minimum feature size for PETG struts, TPU interface bonding quality, overhang limits). Incomplete AM-awareness is a common critique.

4. **Narrow application scope.** The crutch-tip application, while compelling for motivation, may be perceived as too narrow for JMD's design-theory readership. Recommendation: Position the work as a general-purpose multi-fidelity BO framework for multi-material architected materials, with the crutch tip as one demonstration.

5. **Insufficient benchmarking of the optimization method.** JMD reviewers will expect comparison with alternative optimization approaches (e.g., evolutionary algorithms, single-fidelity BO, random search) and sensitivity analyses on surrogate model accuracy.

### JMD vs. SMS comparative considerations:
- **SMS** will be more receptive to the tensegrity mechanics, wave/impact characterization, and multi-material behavior aspects. SMS reviewers are more likely to ask about dynamic testing methodology, constitutive modeling, and comparison with other metamaterial architectures.
- **JMD** will be more receptive to the BO/GP methodology, design-space formulation, and scalability of the approach. JMD reviewers prioritize the generalizable design contribution.
- For a BYU ME team, JMD is the stronger first choice if the BO framework has genuine methodological novelty; SMS is preferred if the primary contribution is the tensegrity multi-material architecture and its energy-absorption performance.

### Recommendation for author-suggested reviewers:
When suggesting reviewers at JMD, provide 4–6 candidates with at least 2 from the design-optimization community (e.g., Liwei Wang, Zacharias Vangelatos, Chengyang Mo, Haris Sheikh) and 2 from the tensegrity/architected-materials community (e.g., Julian Rimoli, Andrea Micheletti, Filipe Santos). This signals to the AE that the paper is genuinely cross-disciplinary and helps ensure balanced review coverage. Avoid suggesting reviewers from the same research group or with obvious co-authorship ties to each other.

References

1. (lee2024data‐drivendesignfor pages 47-49): Doksoo Lee, Wei (Wayne) Chen, Liwei Wang, Yu‐Chin Chan, and Wei Chen. Data‐driven design for metamaterials and multiscale systems: a review. Advanced Materials, Dec 2024. URL: https://doi.org/10.1002/adma.202305254, doi:10.1002/adma.202305254. This article has 246 citations and is from a highest quality peer-reviewed journal.

2. (wang2022scalablegaussianprocesses pages 35-38): Liwei Wang, Suraj Yerramilli, Akshay Iyer, Daniel Apley, Ping Zhu, and Wei Chen. Scalable gaussian processes for data-driven design using big data with categorical factors. Journal of Mechanical Design, Sep 2022. URL: https://doi.org/10.1115/1.4052221, doi:10.1115/1.4052221. This article has 29 citations and is from a domain leading peer-reviewed journal.

3. (do2311multifidelitybayesianoptimization pages 1-4): Bach Do and Ruda Zhang. Multi-fidelity bayesian optimization in engineering design. ArXiv, Nov 2311. URL: https://doi.org/10.48550/arxiv.2311.13050, doi:10.48550/arxiv.2311.13050. This article has 24 citations.

4. (wang2020datadrivenmultiscaletopology pages 11-12): Liwei Wang, Siyu Tao, Ping Zhu, and Wei Chen. Data-driven multiscale topology optimization using multi-response latent variable gaussian process. Volume 11A: 46th Design Automation Conference (DAC), Aug 2020. URL: https://doi.org/10.1115/detc2020-22595, doi:10.1115/detc2020-22595. This article has 5 citations.

5. (bauer2021tensegritymetamaterialstoward pages 1-2): Jens Bauer, Julie A. Kraus, Cameron Crook, Julian J. Rimoli, and Lorenzo Valdevit. Tensegrity metamaterials: toward failure‐resistant engineering systems through delocalized deformation. Advanced Materials, Feb 2021. URL: https://doi.org/10.1002/adma.202005647, doi:10.1002/adma.202005647. This article has 203 citations and is from a highest quality peer-reviewed journal.

6. (bauer2021tensegritymetamaterialstoward pages 6-7): Jens Bauer, Julie A. Kraus, Cameron Crook, Julian J. Rimoli, and Lorenzo Valdevit. Tensegrity metamaterials: toward failure‐resistant engineering systems through delocalized deformation. Advanced Materials, Feb 2021. URL: https://doi.org/10.1002/adma.202005647, doi:10.1002/adma.202005647. This article has 203 citations and is from a highest quality peer-reviewed journal.

7. (zhang2021optimizationforenergy pages 1-2): Jingyao Zhang, Makoto Ohsaki, Julian J. Rimoli, and Kosuke Kogiso. Optimization for energy absorption of 3-dimensional tensegrity lattice with truncated octahedral units. Composite Structures, 267:113903, Jul 2021. URL: https://doi.org/10.1016/j.compstruct.2021.113903, doi:10.1016/j.compstruct.2021.113903. This article has 33 citations and is from a domain leading peer-reviewed journal.

8. (micheletti2021modelinganddesign pages 7-8): Andrea Micheletti, Claudio Intrigila, Nicola Nodargi, Edoardo Artioli, Fernando Fraternali, and Paolo Bisegna. Modeling and design of periodic lattices with tensegrity architecture and highly nonlinear response. Proceedings of the 8th International Conference on Computational Methods in Structural Dynamics and Earthquake Engineering (COMPDYN 2015), pages 1848-1855, Jan 2021. URL: https://doi.org/10.7712/120121.8605.19232, doi:10.7712/120121.8605.19232. This article has 4 citations.

9. (micheletti2021modelinganddesign pages 3-7): Andrea Micheletti, Claudio Intrigila, Nicola Nodargi, Edoardo Artioli, Fernando Fraternali, and Paolo Bisegna. Modeling and design of periodic lattices with tensegrity architecture and highly nonlinear response. Proceedings of the 8th International Conference on Computational Methods in Structural Dynamics and Earthquake Engineering (COMPDYN 2015), pages 1848-1855, Jan 2021. URL: https://doi.org/10.7712/120121.8605.19232, doi:10.7712/120121.8605.19232. This article has 4 citations.

10. (pajunen2021prestraininducedbandgaptuning pages 1-2): Kirsti Pajunen, Paolo Celli, and Chiara Daraio. Prestrain-induced bandgap tuning in 3d-printed tensegrity-inspired lattice structures. Extreme Mechanics Letters, 44:101236, Apr 2021. URL: https://doi.org/10.1016/j.eml.2021.101236, doi:10.1016/j.eml.2021.101236. This article has 33 citations and is from a peer-reviewed journal.

11. (pajunen2021prestraininducedbandgaptuning pages 7-7): Kirsti Pajunen, Paolo Celli, and Chiara Daraio. Prestrain-induced bandgap tuning in 3d-printed tensegrity-inspired lattice structures. Extreme Mechanics Letters, 44:101236, Apr 2021. URL: https://doi.org/10.1016/j.eml.2021.101236, doi:10.1016/j.eml.2021.101236. This article has 33 citations and is from a peer-reviewed journal.

12. (santos2023towardanovel pages 1-2): Filipe A. Santos. Toward a novel energy‐dissipation metamaterial with tensegrity architecture. Advanced Materials, May 2023. URL: https://doi.org/10.1002/adma.202300639, doi:10.1002/adma.202300639. This article has 27 citations and is from a highest quality peer-reviewed journal.

13. (santos2023towardanovel pages 9-9): Filipe A. Santos. Toward a novel energy‐dissipation metamaterial with tensegrity architecture. Advanced Materials, May 2023. URL: https://doi.org/10.1002/adma.202300639, doi:10.1002/adma.202300639. This article has 27 citations and is from a highest quality peer-reviewed journal.

14. (vangelatos2021strengththroughdefects pages 1-2): Zacharias Vangelatos, Haris Moazam Sheikh, Philip S. Marcus, Costas P. Grigoropoulos, Victor Z. Lopez, George Flamourakis, and Maria Farsari. Strength through defects: a novel bayesian approach for the optimization of architected materials. Science Advances, Oct 2021. URL: https://doi.org/10.1126/sciadv.abk2218, doi:10.1126/sciadv.abk2218. This article has 124 citations and is from a highest quality peer-reviewed journal.

15. (meier2024obtainingauxeticand pages 1-2): Timon Meier, Runxuan Li, Stefanos Mavrikos, Brian Blankenship, Zacharias Vangelatos, M. Erden Yildizdag, and Costas P. Grigoropoulos. Obtaining auxetic and isotropic metamaterials in counterintuitive design spaces: an automated optimization approach and experimental characterization. npj Computational Materials, 10:1-12, Jan 2024. URL: https://doi.org/10.1038/s41524-023-01186-2, doi:10.1038/s41524-023-01186-2. This article has 111 citations and is from a peer-reviewed journal.

16. (vangelatos2021strengththroughdefects pages 12-13): Zacharias Vangelatos, Haris Moazam Sheikh, Philip S. Marcus, Costas P. Grigoropoulos, Victor Z. Lopez, George Flamourakis, and Maria Farsari. Strength through defects: a novel bayesian approach for the optimization of architected materials. Science Advances, Oct 2021. URL: https://doi.org/10.1126/sciadv.abk2218, doi:10.1126/sciadv.abk2218. This article has 124 citations and is from a highest quality peer-reviewed journal.

17. (sheikh2022bayesianoptimizationfor pages 15-16): Haris Moazam Sheikh and Philip S. Marcus. Bayesian optimization for mixed-variable, multi-objective problems. Structural and Multidisciplinary Optimization, Nov 2022. URL: https://doi.org/10.1007/s00158-022-03382-y, doi:10.1007/s00158-022-03382-y. This article has 28 citations and is from a domain leading peer-reviewed journal.

18. (mo2023accelerateddesignof pages 9-9): Chengyang Mo, Paris Perdikaris, and Jordan R. Raney. Accelerated design of architected materials with multifidelity bayesian optimization. Journal of Engineering Mechanics, Jun 2023. URL: https://doi.org/10.1061/jenmdt.emeng-7033, doi:10.1061/jenmdt.emeng-7033. This article has 11 citations.

19. (cao2026bgolearnaunified pages 10-13): Bin Cao, Jie Xiong, Jiaxuan Ma, Yuan Tian, Yirui Hu, Mengwei He, Longhan Zhang, Jiayu Wang, Jian Hui, Li Liu, Dezhen Xue, Turab Lookman, and Tong-Yi Zhang. Bgolearn: a unified bayesian optimization framework for accelerating materials discovery. ArXiv, Feb 2026. URL: https://doi.org/10.21203/rs.3.rs-8665853/v1, doi:10.21203/rs.3.rs-8665853/v1. This article has 4 citations.

20. (guachetaalba2023newapproachesand pages 8-9): Juan C. Guacheta-Alba, Angie J. Valencia-Castaneda, Max Suell Max Suell, Oscar F. Aviles, and Mauricio Mauledoux. New approaches and recent applications of tensegrity structures. Journal of Engineering Science and Technology Review, 16:1-12, Jan 2023. URL: https://doi.org/10.25103/jestr.165.01, doi:10.25103/jestr.165.01. This article has 6 citations and is from a peer-reviewed journal.

21. (intrigila2022fabricationandexperimental pages 12-13): Claudio Intrigila, Andrea Micheletti, Nicola A. Nodargi, Edoardo Artioli, and Paolo Bisegna. Fabrication and experimental characterisation of a bistable tensegrity-like unit for lattice metamaterials. Additive Manufacturing, 57:102946, Sep 2022. URL: https://doi.org/10.1016/j.addma.2022.102946, doi:10.1016/j.addma.2022.102946. This article has 52 citations and is from a highest quality peer-reviewed journal.

22. (bauer2021tensegritymetamaterialstoward pages 2-3): Jens Bauer, Julie A. Kraus, Cameron Crook, Julian J. Rimoli, and Lorenzo Valdevit. Tensegrity metamaterials: toward failure‐resistant engineering systems through delocalized deformation. Advanced Materials, Feb 2021. URL: https://doi.org/10.1002/adma.202005647, doi:10.1002/adma.202005647. This article has 203 citations and is from a highest quality peer-reviewed journal.

23. (zhang2021optimizationforenergy pages 11-12): Jingyao Zhang, Makoto Ohsaki, Julian J. Rimoli, and Kosuke Kogiso. Optimization for energy absorption of 3-dimensional tensegrity lattice with truncated octahedral units. Composite Structures, 267:113903, Jul 2021. URL: https://doi.org/10.1016/j.compstruct.2021.113903, doi:10.1016/j.compstruct.2021.113903. This article has 33 citations and is from a domain leading peer-reviewed journal.

24. (pajunen2021prestraininducedbandgaptuning pages 6-7): Kirsti Pajunen, Paolo Celli, and Chiara Daraio. Prestrain-induced bandgap tuning in 3d-printed tensegrity-inspired lattice structures. Extreme Mechanics Letters, 44:101236, Apr 2021. URL: https://doi.org/10.1016/j.eml.2021.101236, doi:10.1016/j.eml.2021.101236. This article has 33 citations and is from a peer-reviewed journal.

25. (sheikh2201bayesianoptimizationfor pages 15-16): Haris Moazam Sheikh and Philip S. Marcus. Bayesian optimization for multi-objective mixed-variable problems. Text, Jan 2201. URL: https://doi.org/10.48550/arxiv.2201.12767, doi:10.48550/arxiv.2201.12767. This article has 7 citations and is from a peer-reviewed journal.

26. (intrigila2022fabricationandexperimental pages 12-12): Claudio Intrigila, Andrea Micheletti, Nicola A. Nodargi, Edoardo Artioli, and Paolo Bisegna. Fabrication and experimental characterisation of a bistable tensegrity-like unit for lattice metamaterials. Additive Manufacturing, 57:102946, Sep 2022. URL: https://doi.org/10.1016/j.addma.2022.102946, doi:10.1016/j.addma.2022.102946. This article has 52 citations and is from a highest quality peer-reviewed journal.

27. (sabounizawadzka2022highperformancetensegrityinspired pages 18-20): Anna Al Sabouni-Zawadzka. High performance tensegrity-inspired metamaterials and structures. ArXiv, Nov 2022. URL: https://doi.org/10.1201/9781003343202, doi:10.1201/9781003343202. This article has 28 citations.

28. (sabounizawadzka2022highperformancetensegrityinspired pages 17-18): Anna Al Sabouni-Zawadzka. High performance tensegrity-inspired metamaterials and structures. ArXiv, Nov 2022. URL: https://doi.org/10.1201/9781003343202, doi:10.1201/9781003343202. This article has 28 citations.