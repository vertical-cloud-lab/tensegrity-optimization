# Cover letter (draft for the authors to edit; nothing has been sent)

Drafted 2026-11-27. Bracketed items need an author decision before
submission. The paragraph on AI tools depends on how the authors handle
ASME's AI position statement (see the readiness review,
`reviews/2026-11-27-jmd-readiness/README.md`).

---

Dear Editor,

We submit "Experiment-Driven Bayesian Optimization of the Impact Response of
Multi-Material 3D-Printed Tensegrity-Inspired Structures" by Marcus E.
Madsen, Audrey K. Christiansen, Jinkwan Han, Jeffrey R. Hill, and Sterling
G. Baird (Department of Mechanical Engineering, Brigham Young University)
for consideration as a Research Paper in the ASME Journal of Mechanical
Design.

The paper reports a design campaign in which every evaluation is a physical
experiment. We parameterize a family of tensegrity-inspired unit cells
printed in one piece from polylactic acid (PLA) struts and thermoplastic
polyurethane (TPU) tendons, scale every candidate to a common mass before
printing, drop-test each specimen repeatedly, and let a fully Bayesian
Gaussian-process surrogate with a multi-objective acquisition function
choose the next batch of nine designs. The paper contributes:

1. a family of multi-material unit cells printed in one piece, with TPU
   in place of the tension elements and the tendons anchored inside the
   PLA strut ends, and a constant-mass projection that scales every
   candidate to a common material budget before printing;
2. a characterized drop-tower protocol and two per-specimen impact
   objectives, peak-acceleration transmissibility and a mass-weighted
   rebound index, with a video check of what the rebound index measures;
3. an experiment-driven Bayesian-optimization loop that recommended three
   batches after the Sobol seed batch. Over the four measured batches (35
   specimens), every member of the final Pareto front came from a
   recommended batch. The predictions archived before each recommended
   batch was printed, and a cross-validated audit, show where the
   surrogate had skill and how its noise specification limited it;
4. a measured error budget from printing one nine-design batch three
   times, which shows that print-to-print and seating variation exceed the
   within-session scatter, and the replication rule that follows from it;
5. a simulation-only benchmark of the optimizer against random, Sobol,
   Latin hypercube, and compass-search baselines at a matched budget.

We think the paper fits the journal's design automation area
(data-driven design and design optimization under noisy, expensive
evaluations), with a design-for-manufacturing component. Its keywords
come from the journal's list (design optimization, data-driven design,
design of experiments, metamodeling, design of engineered materials
system). The paper states its limits: the physical campaign has no
budget-matched baseline, most specimens amplify the peak shock, the
record specimen awaits a re-test, and the rebound index is a ranking
score rather than a measured energy.

[Prior dissemination. Confirm and keep one:] An extended abstract of
earlier campaign results was presented at the ASME IDETC-CIE 2026
conference (Track DAC-10, Design of Engineering Materials and
Structures) [and does / does not appear in the conference proceedings;
if it does, give its paper number here and at the end of the title, as
JMD requires]. The manuscript has not been published elsewhere and is
not under consideration by another journal.

[AI tools. Keep only after the authors decide how to handle ASME's AI
position statement:] We used AI tools throughout this work, as the
Methods section ("Use of AI Tools") and the Acknowledgment describe, and
the project repository lists every session. Because ASME's position
statement restricts AI-generated text and analysis, we would welcome the
Editor's guidance on how it applies to this submission.

The data and code behind every table and figure are available at
https://github.com/vertical-cloud-lab/tensegrity-optimization, and we will
archive a versioned release with a Zenodo DOI at acceptance. The authors
declare no conflict of interest.

Suggested reviewers are listed below. [Confirm current affiliations and
e-mail addresses, and screen each name for co-authorship, advising, or
shared grants with any author in the last four years.]

Sincerely,

Jeffrey R. Hill and Sterling G. Baird (corresponding authors)
Department of Mechanical Engineering, Brigham Young University, Provo, UT
84602, USA. jeff.hill@byu.edu, sterling.baird@byu.edu

---

## Suggested reviewers (verify before use)

Drawn from `reviews/target_audience.md` (branch
`copilot/who-is-the-target-audience`) and the JMD reference check of
2026-11-27. Affiliations come from those sources and may be out of date.

| Name | Affiliation (verify) | Why | Representative paper |
|---|---|---|---|
| Julian J. Rimoli | Georgia Institute of Technology (verify) | Tensegrity mechanics, tensegrity landers, printed tensegrity metamaterials | Bauer et al., Adv. Mater. 2021, 10.1002/adma.202005647 |
| Christopher Hoyle | Oregon State University (verify) | Bayesian and multi-objective optimization in JMD | Biswas, Fuentes, Hoyle, J. Mech. Des. 2022, 10.1115/1.4051787 |
| Nathan Hertlein | (verify; JMD 2024 paper lists the University of Cincinnati group) | BO for impact-loaded additively manufactured lattices | Hertlein, Vemaganti, Anand, J. Mech. Des. 2024, 10.1115/1.4065065 |
| Chengyang Mo | (verify; formerly University of Pennsylvania, Raney group) | Multifidelity BO of architected materials | Mo, Perdikaris, Raney, J. Eng. Mech. 2023 |
| Andrea Micheletti | University of Rome Tor Vergata (verify) | Fabrication and testing of printed tensegrity-like cells | Intrigila et al., Addit. Manuf. 2022 |
| Kirsti Pajunen | (verify; public records stop at Caltech, Daraio group, around 2021) | Printed tensegrity-inspired cells and lattices under impact | Pajunen et al., Mater. Des. 2019; Extreme Mech. Lett. 2021 |
| Lorenzo Valdevit (alternate) | University of California, Irvine (verify) | Architected materials, printed tensegrity metamaterials | Bauer et al., Adv. Mater. 2021, 10.1002/adma.202005647 |

A web search on 2026-11-27 could not confirm current affiliations for
Chengyang Mo (last public record: his 2022 University of Pennsylvania
thesis) or Kirsti Pajunen; prefer the confirmed names if those two
cannot be reached.

Do not suggest: Larry L. Howell or Brian D. Jensen (same department), or
anyone else at Brigham Young University.
