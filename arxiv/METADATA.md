# arXiv metadata for the preprint

Copy each field into the arXiv submission form. Nothing here has been
submitted.

## Title

Experiment-Driven Bayesian Optimization of the Impact Response of Multi-Material 3D-Printed Tensegrity-Inspired Structures

## Authors

In the manuscript's order, in arXiv's "Firstname Lastname, ..." form with
the shared affiliation in parentheses:

```
Marcus E. Madsen (Brigham Young University), Audrey K. Christiansen (Brigham Young University), Jinkwan Han (Brigham Young University), Jeffrey R. Hill (Brigham Young University), Sterling G. Baird (Brigham Young University)
```

The PDF marks M. E. Madsen, A. K. Christiansen and J. Han as equal
contributors, J. R. Hill and S. G. Baird as equal contributors, and Hill
and Baird as corresponding authors (jeff.hill@byu.edu,
sterling.baird@byu.edu). arXiv's author field has no place for these marks.

## Abstract

Plain text, 200 words, 1,445 characters (limit 1,920). It is the
manuscript's abstract with the repository macro written out. Paste it as one
paragraph:

```
Tensegrity-inspired structures of rigid and soft members could cushion impacts, but their transmitted shock is hard to predict by simulation. We report a drop-test-driven Bayesian optimization campaign over three-strut prisms printed in one piece from polylactic acid (PLA) and thermoplastic polyurethane (TPU). The search space has five geometry variables, plus infill and filament settings from the third batch. We scale each candidate to a common mass target before printing, then 3D print and drop-test it repeatedly. We score designs by transmissibility (a ratio of filtered top-to-base peak accelerations) and a mass-weighted rebound index (specimen mass times the square of a timing-based rebound fraction), both minimized. Most specimens amplify the peak shock. Across a quasi-random initial batch and three model-recommended batches (36 specimens), the dominated hypervolume grew 56 percent. Over a third of that gain comes from the final batch's best-predicted design, which lowered transmissibility to 0.803, 10 percent below the best initial-batch specimen, and awaits a re-test. We printed one batch three times to measure repeatability. Excluding sessions that failed a seating or drift check, which produced every large deviation, print-to-print scatter in transmissibility was near 1 percent, so single-print extremes stay provisional. Code and data are available at https://github.com/vertical-cloud-lab/tensegrity-optimization.
```

## Comments

```
28 pages, 6 figures, 4 tables. Supplementary Information (25 pages) is an ancillary file. Code and data: https://github.com/vertical-cloud-lab/tensegrity-optimization
```

## Categories

| Role | Category | Why |
|---|---|---|
| Primary | `physics.app-ph` (Applied Physics) | Its scope names advanced materials and metamaterials, and the paper reports the measured impact response of 3D-printed architected (tensegrity-inspired) cells |
| Cross-list | `cond-mat.mtrl-sci` (Materials Science) | Its scope includes mechanical properties. The paper measures those of an architected, multi-material printed structure and optimizes them by Bayesian optimization over physical experiments |
| Cross-list | `cs.CE` (Computational Engineering, Finance, and Science) | The contribution is an engineering design-optimization workflow (surrogate model, acquisition, batch recommendations), plus the simulation-only benchmark against space-filling baselines |
| Cross-list, optional | `stat.AP` (Applications) | Applied statistics in engineering: a known-variance noise model, replicate prints, intraclass correlation, permutation tests and leave-one-design-out cross-validation |

Not recommended: `cs.LG` or `stat.ML`. The paper applies existing
Bayesian-optimization methods and does not propose a new one, so moderators
may move or drop it.

arXiv asks a first-time submitter to a category for an endorsement. If the
submitting account has no endorsement for `physics.app-ph`, swap the first
two rows: `cond-mat.mtrl-sci` primary, `physics.app-ph` cross-list.

## Licence

**arXiv.org perpetual, non-exclusive license 1.0**
(<http://arxiv.org/licenses/nonexclusive-distrib/1.0/>). It gives arXiv the
right to distribute the paper and nothing else, so the authors keep the
copyright and can transfer it to a journal later. ASME says that posting a
preprint is not considered prior publication and advises authors not to
assign copyright at the preprint stage
([ASME, Open Access](https://www.asme.org/publications-submissions/journals/information-for-authors/open-access)).
A Creative Commons licence would also be allowed, but it cannot be withdrawn
and some publishers object to it.

## Other fields

- **Journal reference, DOI:** leave empty (not published).
- **Report number, MSC class, ACM class:** leave empty.
- **Files:** upload `tensegrity-bo-arxiv-source.tar.gz` as is. It holds
  `main.tex`, `main.bbl`, the six figures and `anc/supplementary.pdf`.
  arXiv compiles `main.tex` with pdflatex and lists the SI under
  "Ancillary files".
