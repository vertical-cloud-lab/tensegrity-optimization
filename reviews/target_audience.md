# Target audience: candidate reviewers, editors, and reviewer-profile diversity

> **Issue:** "Who is the target audience?" -- *Who should we suggest as potential
> reviewers? Which editors are most likely to be overseeing our submission? See
> #20 and all other PRs.*
>
> **Primary venue:** ASME Journal of Mechanical Design (JMD).
> **Backup venue:** Smart Materials and Structures (SMS, IOP).
> See `manuscript/README.md` (PR #20) for the venue selection rationale.

This document has two parts:

1. **Reviewer-profile diversity expected at JMD/SMS** for a cross-disciplinary
   *Bayesian optimization + multi-material additive manufacturing + tensegrity
   metamaterials + assistive devices* manuscript -- with the rough mix of
   reviewer subfields the editor will assemble, and the implication for which
   sections of the paper need to land for which reader.
2. **A candidate reviewer pool**, synthesized by walking every Edison trajectory
   committed across the repo's PR branches (literature, precedent, and analysis
   tasks) and the consolidated `manuscript/references.bib` from PR #20, then
   keeping authors who (a) appear two or more times in our existing bibliography
   and (b) match a relevant subfield. A second, longer pool of well-known
   senior names per subfield is included for completeness.

A separate, **non-blocking Edison `LITERATURE_HIGH` query** (task ID
`9cc7db18-10b5-457e-9b7c-9a3ecb2b9f14`) was submitted in this session asking
specifically for current JMD Associate Editors who handle data-driven design /
DfAM / architected mechanisms / assistive devices, plus 10-15 named candidate
reviewers with representative recent papers. The committed `.md` / `.json`
trajectory (and the corresponding update to this file) will land when that
task completes -- see the placeholder in *Section 3* below.

## 1. Why this question matters for our PR #20 manuscript

PR #20 stands up an `asmejour`-class IMRaD scaffold targeting **JMD as the
primary venue** with **SMS as a backup**. The scope is intentionally
cross-disciplinary:

- **Methods:** multi-fidelity Bayesian optimization (BoTorch / Ax-style GP
  surrogates, qNEHVI, multi-objective stiffness vs. specific-energy-absorbed
  trade-offs).
- **Manufacturing:** PETG struts + TPU 95A tendons on a Bambu Lab H2D IDEX
  printer (per the lab's hardware standard -- see the repo's hardware memory).
- **Mechanics:** tensegrity / tensegrity-like unit cells; quasi-static
  compression and drop-tower / single-point LDV impact testing
  (Lansmont M23 + Polytec QTec, see issue #28).
- **Application motivation:** shock-absorbing crutch tips and assistive
  devices (PR #18 prior-art trajectories).

That breadth is **exactly the failure mode JMD reviewers complain about most
often** for this kind of paper: "interesting, but who is it for?" A clean
reading of which reviewer subfields the AE will recruit -- and which
journal-aligned candidate names the editor can actually pick -- gives the
co-authors a checklist for what each section of the manuscript must explicitly
do for each reader.

## 2. Reviewer-profile diversity expected at JMD (and SMS)

**JMD typically assigns 2-3 reviewers per manuscript**, and for a paper that
spans BO + AM + architected materials + an assistive-device motivation, the AE
has incentive to pick **at least one reviewer from each of the four sub-camps
below**. Our manuscript needs to anticipate all four.

| Reviewer profile | What they will look for first | Likely concerns to pre-empt |
|---|---|---|
| **(A) Design optimization & data-driven design** -- BO/GP/multi-objective, design-of-experiments, surrogate modeling. Most likely to be the AE handler at JMD. | Acquisition function choice and justification (qNEHVI, qEHVI, qLogNEI), kernel/likelihood choices, how the multi-fidelity coupling between sim and experiment is formulated, batch sizing, baseline against random / LHS / one-shot DoE, calibration of GP uncertainties against held-out experimental data. | "BO is just a wrapper here -- where is the methodological contribution beyond applying off-the-shelf BoTorch?" Address by foregrounding the *multi-fidelity* coupling and the experimental-loop closure. |
| **(B) Mechanism design / compliant & architected mechanisms / metamaterials** -- people who publish on origami, lattices, tensegrity, mechanical metamaterials. | Topology rationale: why tensegrity vs. octet/honeycomb/auxetic? Class-1 vs. tensegrity-like distinction, prestress, stability under load, scaling laws, comparison to known impact-absorbing lattice families. | "Tensegrity-like" structures where struts contact the floor and bypass the tendons (see the repo's tensegrity-simulator memory) will draw fire. Be explicit about Class-1 vs. tensegrity-like and report both. |
| **(C) Additive manufacturing / DfAM / multi-material printing** -- materials and process side. | Print process window (H2D IDEX, 0.4 mm nozzle, 3-perimeter rule), interface bonding between PETG and TPU, repeatability across builds, characterization of as-printed vs. nominal geometry, fatigue/aging if cyclic loading is implied. | "Specimen-to-specimen variability swamps the BO signal." Need to report fabrication uncertainty and, ideally, fold it into the BO noise model. |
| **(D) Biomechanics / rehabilitation / assistive devices** -- usually the smallest slice at JMD but the AE will recruit one if the application motivation (crutch tips) is foregrounded; this is the *core* readership at SMS only if we frame around smart/responsive structures. | Realism of loading conditions vs. clinical use (vertical impact only? lateral? off-axis?), HAVS / vibration transmission (see PR #18 trajectory 03), fall risk / abandonment data (also trajectory 03), comparison to commercial crutch tips. | If the manuscript over-promises clinical impact from unit-cell tests, this reviewer will recommend rejection on impact-claim grounds. PR #20's mock review already flagged exactly this (`reviews/mock_reviews.md`, "Impact claims are overstated"). Pre-empt by framing as bench-level prior-art benchmarking, not a clinical study. |

**JMD vs. SMS profile mix** (rough expectation):

- **JMD** review panels skew (A)+(B), with one (C) usually present and (D)
  occasional. The AE handler is almost always from (A) or (B). Most common
  major-revision reasons for cross-disciplinary BO/AM/metamaterials papers at
  JMD: insufficient design-theoretic novelty beyond off-the-shelf BO; weak
  manufacturing-uncertainty quantification; over-broad application claims.
- **SMS** review panels skew (B)+(C) with the framing pivoted toward
  *smart/responsive* materials. A pure BO methods reviewer is less likely; an
  experimental smart-materials reviewer more likely. Most common concerns:
  "where is the smart/active behavior?" -- which is exactly why SMS is our
  *backup* venue, not primary, and the manuscript needs a different framing
  paragraph if we retarget.

## 3. Candidate reviewer pool

### 3a. Pool synthesized from existing Edison trajectories and `manuscript/references.bib`

These authors appear **two or more times** in our existing project bibliography
(PR #20's consolidated `references.bib`, plus the literature trajectories
committed across PR branches `copilot/explore-impact-absorption-crutches`,
`copilot/explore-tpu-petg-variables`, `copilot/explore-simulations-for-tensegrity`,
`copilot/explore-joint-design-for-petg-tpu`, `copilot/create-repo-project-name`,
and `copilot/create-manuscript-template`). Each is a candidate the AE could
plausibly assign **because they have already published in venues directly cited
by our paper**, which is the strongest objective signal of profile match. Do
**not** suggest authors with whom either PI has co-authored, advised, or been
advised by within the last 4 years (standard ASME COI window).

| Subfield | Author (last name)                | Existing-corpus venue overlap                                  |
|---|---|---|
| **(B) Tensegrity mechanics** | Skelton           | Composite Structures, Applied Physics Letters                  |
| **(B) Tensegrity mechanics** | Fraternali         | Composite Structures, Int. J. Solids and Structures, APL       |
| **(B) Tensegrity mechanics** | Amendola           | Composite Structures, Int. J. Solids and Structures            |
| **(B) Tensegrity mechanics** | Carpentieri        | Composite Structures, Int. J. Solids and Structures            |
| **(B) Tensegrity robotics**  | SunSpiral          | i-SAIRAS, ICRA, IROS (NASA Ames "tensegrity rover" lineage)     |
| **(B) Tensegrity robotics**  | Caluwaerts         | i-SAIRAS, ICRA                                                  |
| **(B) Tensegrity robotics**  | Bruce              | ICRA, IROS                                                      |
| **(B) Tensegrity robotics**  | Agogino            | i-SAIRAS, ICRA                                                  |
| **(A) BO / surrogate models** | Balandat          | NeurIPS, ICML (BoTorch core author)                             |
| **(A) BO / surrogate models** | Daulton           | NeurIPS, ICML (qNEHVI / qEHVI author)                           |
| **(A) BO / surrogate models** | Bakshy            | NeurIPS, ICML (Ax/BoTorch lead)                                 |
| **(A) BO / surrogate models** | Ament             | NeurIPS, arXiv 2310.18288 (sustainability of GP BO)             |
| **(A) Multi-fidelity surrogates** | Perdikaris    | Proc. Royal Soc. A, J. Eng. Mechanics                           |
| **(C) AM / FFF process & interfaces** | Vanaei      | Rapid Prototyping Journal (PETG / multi-material FFF)           |
| **(C) AM / data-driven materials**    | Khan        | npj Computational Materials, AIAA SciTech                       |
| **(D) Crutch biomechanics / assistive** | Sawatzky  | Medical Eng. & Physics, PM&R (shock-absorbing crutch tips)      |
| **(D) Crutch biomechanics / assistive** | MacGillivray | Medical Eng. & Physics, PM&R                                |
| **(D) Crutch / mobility-aid usage**     | Manocha   | PM&R (multiple), Medical Eng. & Physics                         |
| **(D) Stroke / mobility outcomes**      | Hachisuka | J. Stroke and Cerebrovascular Diseases (×2)                     |

A larger but lower-priority pool (Wang, Liu, Zhang, Cheng, Li, Lu, Wu, Jiang,
Xie, Adams) appears with high frequency but with surnames common enough that
the AE will need a specific paper anchor; we will let the pending Edison query
disambiguate those before listing them as recommendations.

### 3b. Senior / well-known additional names per subfield (*not yet in our bibliography*)

These are reviewer names the AE is statistically likely to consider for a
JMD submission of this type, based on the field's publication record. They are
**candidates for the manuscript "Suggested Reviewers" field**, pending the
pending Edison query's check for recency and COI flags.

- **(A) BO / data-driven design at JMD:** Frazier (Cornell), Gardner (NYU),
  Joseph F. Wang / Mark Fuge / Faez Ahmed (Maryland / MIT, JMD regulars on
  data-driven design), Doolen / Iyer.
- **(B) Architected materials & metamaterials:** Greer (Caltech), Valdevit
  (UC Irvine), Portela (MIT), Meza, Berger, Schaedler (HRL), Compton, Gibson
  (MIT), Tankasala. Tensegrity-specific: Rimoli (Georgia Tech), Goyal /
  Sultan (Texas A&M), Pajunen (CMU), Rieffel (Union), Friesen.
- **(C) Multi-material AM of polymers / lattices:** Lewis (Harvard), Mueller
  (Columbia / Apple), Bauer (KIT), Compton (ORNL), Boyer.
- **(D) Assistive-device biomechanics:** beyond the in-corpus authors above,
  the JMD AE will commonly recruit from the *J. Biomechanical Engineering*
  pool (a sister ASME journal); names should be drawn from the pending Edison
  query rather than guessed.

### 3c. Pending Edison query

> **Edison `LITERATURE_HIGH` task `9cc7db18-10b5-457e-9b7c-9a3ecb2b9f14`** was
> submitted in this session and is non-blocking. It asks Edison to (i) name the
> current JMD AEs whose published / handled portfolios cover (A)-(D) above,
> (ii) propose 10-15 specific candidate reviewers with one or two representative
> recent papers each (with venue and year), (iii) flag obvious COIs for a
> BYU-based author team, and (iv) repeat the exercise for SMS as the backup
> venue. The task `.md` (verbatim `formatted_answer`) and `.json`
> (`model_dump_json`) will be committed to `edison-trajectories/` next session,
> per the repo's Edison-trajectory convention, and Section 3a/3b above will be
> updated to reconcile the two pools.

## 4. Most-cited venues across our existing literature corpus (signal for AE assignment)

The AE handling our manuscript at JMD is almost certainly an active publisher
in one of the top venues from our own bibliography and trajectories. The table
below is the venue-frequency tally over all 19 Edison trajectory `.md` files
on PR branches plus the consolidated `manuscript/references.bib`; it is a
direct proxy for which JMD AE silo is the best fit.

| Frequency tier | Venues |
|---|---|
| **High (>=10 hits)** | Polymers; Materials & Design; Additive Manufacturing; Science / Science Advances; Assistive Technology |
| **Medium (4-10)**     | IEEE ICRA / IROS; Advanced Materials; Rapid Prototyping Journal; Journal of Biomechanics |
| **Low (1-3)**         | Composite Structures; Int. J. Solids and Structures; J. Mechanics and Physics of Solids; Smart Materials and Structures (×1); ASME J. Mechanisms and Robotics (×1); Structural and Multidisciplinary Optimization; Soft Robotics; Nature Communications; npj Computational Materials |

**Read of this table:** our existing literature pull is *materials- and
manufacturing-heavy* (Polymers, Mater. & Des., Addit. Manuf.) with a healthy
robotics/tensegrity slice (ICRA/IROS, Composite Structures) and an
assistive-device tail (Assistive Technology, J. Biomechanics). It is **light on
core ASME JMD venues** -- only one ASME J. Mechanisms and Robotics hit and one
SMS hit show up in this corpus. **Action item for the manuscript:** before
submission, run one more targeted Edison literature pass against JMD,
J. Mech. and Robotics, J. Applied Mechanics, and Structural and
Multidisciplinary Optimization to thicken the core-design-theory layer of the
bibliography. This will (i) make the manuscript read as if its authors are
talking to the JMD community and (ii) generate additional in-corpus reviewer
candidates for the table in Section 3a.

## 5. Sources

- `manuscript/references.bib` (PR #20, branch `copilot/create-manuscript-template`).
- `edison-trajectories/01..04*.md` (branch `copilot/explore-impact-absorption-crutches`,
  PR #18 lineage).
- `edison-trajectories/tpu-petg-bo-variables-5ae24eaf-*.md`
  (branch `copilot/explore-tpu-petg-variables`).
- `edison-trajectories/2026-05-08-sim-survey-782657e0.md`
  (branch `copilot/explore-simulations-for-tensegrity`).
- `edison-trajectories/joint-design/*.md` and
  `edison-trajectories/{1400ca69,3b9d76b5}*.md`
  (branch `copilot/explore-joint-design-for-petg-tpu`).
- `edison-trajectories/60470477-*-naming.md`
  (branch `copilot/create-repo-project-name`).
- `reviews/mock_reviews.md` (committee-style mock review of the proposal).
- Pending: Edison task `9cc7db18-10b5-457e-9b7c-9a3ecb2b9f14`
  (`LITERATURE_HIGH`, JMD AEs + named reviewer candidates + SMS analog).
