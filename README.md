# BYU Mentored Research Grant Proposal: Tensegrity Structures for Energy Absorption

**Bayesian Optimization of Tensegrity Structures for Energy Absorption: A Simulation-Guided Experimental Approach**

BYU College of Engineering — Mentored Research Grant Proposal

## Overview

- **Duration:** 2 years
- **Budget:** $25,000
- **Students:** 2–3 undergraduates (+ graduate co-mentor)
- **Focus:** Undergraduate mentored research

This proposal develops a closed-loop framework integrating physics-based simulations with Bayesian optimization to design tensegrity structures optimized for energy absorption. Undergraduate students fabricate and experimentally validate optimized designs through controlled impact testing.

## Repository Structure

```
├── proposal.tex          # Main LaTeX document
├── references.bib        # BibTeX bibliography
├── sections/
│   └── budget.tex        # Budget table and justification
├── figures/              # Figures and diagrams
├── Makefile              # Build commands
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

## Key Sections

- **Research Objectives** — Parameterize tensegrity unit cells, build simulations, run Bayesian optimization, fabricate & test
- **Technical Approach** — Three phases: simulation development, fabrication & validation, analysis & dissemination
- **Mentoring Plan** — Weekly meetings, progressive responsibility, skills development across experimental, computational, and communication domains
- **Budget** — $25k split across student stipends, graduate mentoring, materials, sensors, travel

## TODO

- [ ] Fill in PI name and department
- [ ] Add PI qualifications section
- [ ] Update placeholder bibliography entries with exact citations
- [ ] Add figures (tensegrity schematic, BO loop diagram, test setup)
- [ ] Review against grant submission guidelines for page/format requirements
- [ ] Get feedback from co-PI / collaborators
