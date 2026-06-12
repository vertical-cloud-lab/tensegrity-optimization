# PR #20 Context Consolidation - Issue #75

This document consolidates all context from Issue #19 (Manuscript venues and template) and PR #20 (Populate ASME Journal of Mechanical Design manuscript draft) into a single reference document for Issue #75.

## Issue #19: Manuscript venues and template

**Opened**: 2026-05-08 16:55:15
**Title**: Manuscript venues and template
**State**: Open
**Assignees**: sgbaird, Copilot

### Issue Description

Likely targeting ASME Journal of Mechanical Design. Begin by finding and downloading all author guidelines and requirements for this. Find a latex template for it, if it's not available, then a word template and convert to latex. Create a lorem ipsum style template. Don't add technical content yet.

(aside: also considering Smart Materials and Structures)

### Comments on Issue #19
No comments yet.

---

## PR #20: Populate ASME Journal of Mechanical Design manuscript draft

**Number**: 20
**Base**: main
**Head**: copilot/create-manuscript-template
**State**: Open (Partially completed work)

### Overview

Stands up the journal-manuscript skeleton called for in Issue #19 and populates it from existing repo context (proposal narrative, Edison literature trajectories across PR branches). Primary venue is ASME Journal of Mechanical Design (JMD); Smart Materials and Structures (SMS) is documented as a backup. Quantitative results remain `\todo{}` placeholders pending experimental data.

### Key Components Added

#### `manuscript/` directory
- `manuscript-body.tex` — shared IMRaD body using the `asmejour` class (CTAN; auto-installed by MiKTeX, not vendored). Uses actual class macros, JMD-formatted abstract, contributions list, Background/Methods/Results sections
- `manuscript.tex` — wrapper with `\def\TODOOPTS{disable}` for clean PDF
- `manuscript-todos.tex` — wrapper leaving `\TODOOPTS` empty for review PDF with annotations
- `references.bib` — consolidated working bibliography aggregating Edison-derived literature
- `references-full.bib` — master synthesized library (813 unique references, 592 with DOIs)
- `README.md` — documentation of JMD limits, abstract rules, IMRaD requirements

#### Placeholder System
- `todonotes` package wired through single `\TODOOPTS` flag for shared manuscript-body.tex
- `\figplaceholder` and `\tabplaceholder` macros for figure/table locations
- All content gaps flagged with `\todo{...}` for review

#### Build Infrastructure
- `Makefile` with `manuscript` / `manuscript-todos` / `manuscript-all` targets
- `.gitignore` updates for manuscript artifacts

#### Edison Mock Peer Review
- Submitted draft to Edison ANALYSIS (task `6c140449-0426-490d-8fc2-67bcfdd0d1d9`)
- Mock decision: **Reject and Resubmit**
- Venue fit confirmed for ASME JMD as Research Paper

### Commits on PR #20 Branch

From `copilot/create-manuscript-template` (latest commits first):

1. **b2a27aa** - Write query field directly in submit script SUBMITTED.json for reproducibility
2. **906807c** - Add Edison round-2 mock-JMD-review trajectory (task 3fde560e); decision: Major Revision
3. **243e30f** - Rebuild manuscript PDFs (clean 7pp, todos 10pp, diff 9pp) reflecting pretensioning removal
4. **211a29d** - Remove pretensioning reference from current design parameters
5. **21186c7** - Add preview composite of Fig 2 + Fig 3 with real photos
6. **4021398** - Wire example figures + real repo photos into manuscript (Figs 2-8)
7. **02b8fc7** - Narrow integration fallback to ImportError; tidy caption f-string
8. **93d14c7** - Revise mechanistic data-figure example per Edison ANALYSIS feedback
9. **5fd41ef** - Centralize Ax internal-API access in example figure generator
10. **a2ee483** - Add Ax-generated example fills for manuscript's empty data-figure slots
11. **ab0d457** - Fetch Edison ANALYSIS feedback on mechanistic data-figure example
12. **148fcc5** - Submit mechanistic data-figure example to Edison ANALYSIS for feedback
13. **c261dbc** - Merge branch 'copilot/create-manuscript-template'
14. **4647c2c** - github copilot cli session with Marcus
15. **997897c** - Clarify TP4 capture reference in figure example docstring
16. **a138300** - Add standalone mechanism-oriented data figure example (mock-up, synthetic)
17. **447f64b** - Switch manuscript to two-column ASME JMD layout (7 pp); submit T24 figure feedback
18. **a9283c9** - Track fab-workflow figure source/PDF; drop stray manuscript-body.pdf

(Additional commits available on branch)

---

## Critical Feedback on PR #20

### Comment ID: 4687197892
**From**: @sgbaird
**Created**: 2026-06-12 03:50:28

This comment contains critical feedback that triggered errors in the previous Copilot agent. **Wait before addressing this comment as per Issue #75**.

#### Feedback Summary

**1. Scope drift — title/abstract/intro frame**
- Issue: Title/abstract/intro frame a general energy absorber while crutch-tip only appears in Discussion
- Decision: Crutch tip only in future work. Planetary lander as motivating use case

**2. Table 1 ↔ D3 parameterization inconsistency**
- Issue: Text says D3 collapses 12 diameter axes to 4 orbit axes (1 strut + 3 cable), but Table 1 lists only one d_s and one d_t
- Decision: Defer to whatever actually is written in the BO code from PR #35

**3. Tendon-diameter conflict**
- Issue: Categorical {1.2, 1.8, 2.4, 3.0, 4.5} mm vs Table 1's continuous 3.0–5.5 mm
- Decision: Should be continuous. Make consistent. Double check BO script.

**4. BO method under-specified**
- Issue: Kernel/ARD, transforms, noise, batch q, budget T, stopping rule, seed policy not documented
- Clarification: Categorical variables not used with just T3 prism
- Decision: ARD, model-inferred noise, 10 batches of 5 prints. Placeholders for Zenodo version.

**5. Novelty vs Pajunen 2019 / Intrigila 2022 / Mo 2023**
- Issue: Asserted but not demonstrated
- Decision: Make comparison table

**6. Language & terminology**
- Issue: Soften "ensure cyclic interface durability" until data exists; standardize FDM vs FFF; abstract ~147 words (<150–200 target)
- Decision: Use FDM throughout. Omit crutch tip motivation.

### Agent Errors on PR #20

Comments 4687198740, 4687200856, and 4687203019 all show the same error:
- Error ID: `42b0b6fe-5158-4055-b20e-390e2a27d200`
- The Copilot agent encountered an unexpected error while processing @sgbaird's feedback comment
- These errors suggest the previous agent may have had difficulty handling the complex feedback

---

## Status

**This Issue #75 exists to:**
1. Create a clean slate for addressing the PR #20 feedback
2. Consolidate all context from Issue #19 and PR #20
3. Provide a working document for the next phase of manuscript development
4. Address the feedback in comment 4687197892 in a fresh session

**Next Steps** (when ready to proceed):
- Address the 6 major feedback items from comment 4687197892
- Update manuscript files accordingly
- Rebuild PDFs and commit changes
