# BYU Mentored Research Grant Proposal: Multi-Material 3D-Printed Tensegrity Structures

**Bayesian Optimization of Multi-Material 3D-Printed Tensegrity Structures for Energy Absorption**

BYU Ira A. Fulton College of Engineering — Mentored Research Grant Proposal

## Overview

- **PI:** Jeffrey R. Hill, Mechanical Engineering
- **Co-PI:** Sterling G. Baird, Mechanical Engineering
- **Duration:** 2 years
- **Budget:** $25,000
- **Students:** 2–3 undergraduates + 1 graduate co-mentor
- **Focus:** Undergraduate mentored research

This proposal develops a multifidelity Bayesian optimization framework to design multi-material 3D-printed tensegrity structures (PLA struts + TPU tension elements) optimized for energy absorption. Undergraduate students fabricate and experimentally validate optimized designs through compaction tests, drop tests, and wave propagation measurements.

## Repository Structure

```
├── proposal.tex              # Main LaTeX document
├── references.bib            # BibTeX bibliography
├── sections/
│   ├── coverpage.tex         # MRG cover page (abstract, budget table, external funding)
│   ├── budget.tex            # Budget table and justification
│   └── biosketch.tex         # PI and Co-PI biographical sketches
├── models/                   # Reference tensegrity STL models + generator (issue #21)
│   ├── stl/                  # Pre-generated binary STLs (3-bar, 4-bar, icosahedron)
│   ├── generate_stl.py       # Self-contained Python generator (stdlib only)
│   └── README.md             # Catalog, geometry, references, external links
├── figures/
├── Makefile                  # Build commands
├── .gitignore
└── README.md
```

## Building the Proposal

Requires a LaTeX distribution (e.g., TeX Live, MiKTeX) with `pdflatex` and `bibtex`.

```bash
# Using Make
make

# Or manually
pdflatex proposal
bibtex proposal
pdflatex proposal
pdflatex proposal
```

## Proposal Structure (≤5 pages + cover page, references, bio sketches)

- **Cover Page** — Title, PI/Co-PI, abstract, student counts, budget summary, relationship to external funding
- **Research Motivation & Overview** — Multi-material 3D-printed tensegrity + multifidelity BO
- **Background** — Tensegrity structures, Bayesian optimization, Mo et al. (2023) multifidelity framework
- **Student Research Project 1** — Simulation & Bayesian optimization
- **Student Research Project 2** — Fabrication, CAD, & experimental testing
- **Mentoring Environment** — Weekly meetings, graduate co-mentor, peer mentoring, progressive responsibility
- **Expected Research Outcomes** — UCUR, ASME IDETC, journal submission, NSF proposal
- **Potential Impact** — Protective equipment, packaging, aerospace applications
- **Timeline** — 4-semester project plan
- **Budget** — $25k (undergraduate wages, graduate wages, supplies, travel, other)
- **References** — (does not count toward page limit)
- **Bio Sketches** — Hill & Baird (does not count toward page limit)

## TODO

- [ ] Add figures (tensegrity schematic, BO loop diagram, test setup)
- [ ] Finalize PI/Co-PI bio sketch details (specific publications, appointments)
- [ ] Get feedback from co-PI / collaborators
