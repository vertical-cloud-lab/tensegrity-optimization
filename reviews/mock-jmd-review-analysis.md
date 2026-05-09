# Analysis of Edison mock-JMD peer review

- **Source:** Edison ANALYSIS task `6c140449-0426-490d-8fc2-67bcfdd0d1d9`
- **Verbatim trajectory:** [`edison-trajectories/2026-05-09-mock-jmd-review-6c140449.md`](../edison-trajectories/2026-05-09-mock-jmd-review-6c140449.md)
  · [`.json`](../edison-trajectories/2026-05-09-mock-jmd-review-6c140449.json)
- **Inputs reviewed:** `manuscript/manuscript.pdf`, `manuscript-todos.pdf`,
  `manuscript-body.tex`, `manuscript.tex`, `manuscript-todos.tex`,
  `references.bib`, `manuscript/README.md`.
- **Mock decision:** **Reject and Resubmit** (three Major-Revision reviews
  synthesized by a mock JMD Associate Editor). Venue fit is confirmed for
  ASME JMD as a standard Research Paper; *Smart Materials and Structures*
  or *Additive Manufacturing* are flagged as alternatives if the BO
  methodology is deprioritized.

This file triages the four reviewer artifacts into concrete, actionable
items mapped to specific files / sections so a follow-up revision pass
can address them without re-reading the full Edison answer.

---

## 1. Verified actionable items (bugs caught by the reviewers)

### 1.1 PLA → PETG material consistency  *(blocker)*
Reviewer #3's largest call-out: the manuscript body says
"poly\-lactic acid (PLA) struts and TPU tension elements" while the
project scope is **PETG struts + TPU tension elements** on the
Bambu H2D (IDEX). Verified: `manuscript-body.tex` contains 19 `PLA`
mentions vs. only 3 `PETG` mentions; the Contributions block, the
Background AM subsection, the Methods fabrication subsection, and the
Discussion all reference PLA.

> **Fix:** global s/PLA/PETG/ pass in `manuscript-body.tex`, then update
> the framing of `\citet{ye2023multimaterial}` core-wrapping (TPU/PETG
> has substantially better innate FFF layer adhesion than TPU/PLA, so
> core-wrapping is a *durability* argument, not a *bond-failure-recovery*
> argument). Also retire `polylactic acid` and any `PLA`-specific
> material parameters in the search-space text.

### 1.2 Blank third Contributions bullet  *(formatting)*
Reviewer #1 flagged that the third bullet of the Contributions list
renders blank in the PDF. Likely cause: an `\item` containing only a
suppressed `\todo{}` macro when `\TODOOPTS=disable`.

> **Fix:** put non-todo prose in every `\item` under
> `\paragraph{Contributions.}` so the clean build is self-contained;
> keep `\todo{}` annotations as supplemental margin notes only.

### 1.3 `(author?)` markers in the bibliography  *(bibtex)*
Reviewer #1 noted the printed bibliography has `(author?)` artefacts.
Origin: a subset of entries in `references.bib` were imported with no
`author` field (or with the author block stripped during the
edison-trajectory parse).

> **Fix:** grep `references.bib` for entries lacking a usable `author =`
> field; restore from the original Edison trajectories or from the
> publisher metadata. Re-run `bibtex manuscript` and confirm the log is
> clean.

### 1.4 "Multifidelity" claim is unsupported  *(scope honesty)*
Reviewer #1 caught that the introduction claims a multifidelity-BO
contribution but the Methods describe only a single experimental
fidelity. Either (a) wire in a low-fidelity surrogate (e.g., the
MuJoCo / PyChrono rigid-strut + tendon sims already in
`simulations/`) and *fuse* it with the experimental loop, or (b)
remove "multifidelity" from the abstract / introduction / contributions
and reframe as single-fidelity Bayesian optimization with experimental
evaluations.

> Note: our own simulation README documents that rigid-strut tensegrity
> sims are unreliable for *quantitative* peak-g prediction (peak-g is
> dominated by floor contact, not cable stiffness), so option (a) would
> need DiffPD / PolyFEM+IPC. Option (b) is the safer near-term fix.

---

## 2. Methodological gaps to address before submission

### 2.1 BO rigor (Reviewer #1)
The Methods BO subsection currently lists only the libraries
(BoTorch / Ax) and acquisitions (LogEI, qNEHVI). The reviewer asks for:

- Kernel choice (Matérn-5/2 default vs. RBF; rationale).
- Handling of categorical connectivity variables (one-hot? mixed search
  space via `MixedSingleTaskGP`? Garrido-Merchán & Hernández-Lobato 2020?).
- Constraint formulation (peak transmitted force / printability) —
  output constraints in qNEHVI, or hard search-space constraints?
- Batch size $q$ and total budget $T$, justified against the search-space
  dimensionality.

### 2.2 Loading-protocol / clinical relevance (Reviewer #2)
The Lansmont M23 axial-drop protocol does not capture:
- Off-axis strike angle and shear loading at first ground contact.
- Double-peak GRF profile of crutch use.
- Cyclic fatigue / heat buildup over thousands of strides per day.

> **Fix:** either add a *cyclic compression* run on the M23 (or a servo
> hydraulic / electrodynamic frame) and an angled-strike configuration,
> or — if those are out of scope for this paper — explicitly de-scope
> the crutch-tip framing and re-position as a "general energy-absorbing
> tensegrity-inspired metamaterial study" with a follow-up paper for
> clinical translation.

### 2.3 SEA → peak-transmitted-force mapping (Reviewer #2 minor)
The Discussion currently optimizes specific energy absorption (SEA) and
compaction efficiency. The clinically relevant metric is peak
transmitted force at the user's wrist/shoulder. Add a paragraph in the
Discussion bridging SEA to a peak-force estimate (or a transmissibility
TF derived from the LDV velocity record).

### 2.4 Process-control reporting (Reviewer #3)
Add an FFF process-parameter table to the Methods fabrication section:
nozzle diameter, layer height, extrusion temperature (TPU 230 °C / PETG
260 °C nominal), bed temperature, cooling, infill / wall counts, raster
angle, and IDEX manual filament map (we always run
`--filament-map-mode Manual --filament-map 1` on H2D).

### 2.5 Process alternatives (Reviewer #3 minor)
Brief paragraph in Background §AM: rationale for FFF vs. SLA/DLP
flexible-resin lattices and SLS/MJF TPU powders (Z-axis weakness vs.
isotropy, cost, multimaterial limits).

---

## 3. Bibliographic gaps the reviewers flagged

| Topic | Suggested addition |
|---|---|
| Crutch-tip slip/friction standards | ISO 11334-4 (walking aids); Basford et al. 1990. |
| TPU/PETG FDM interface adhesion | Caminero et al. 2019 (and successors) — *not* TPU/PLA. |
| Categorical-variable BO | Garrido-Merchán & Hernández-Lobato 2020; Ru et al. 2020 (BOCS). |
| FFF resolution limits for elastomeric lattices | studies mapping nozzle-Ø vs. minimum strut-Ø for TPU/PETG. |

These belong in `references.bib` as new entries plus inline `\citep`
calls in the relevant Background subsections.

---

## 4. Priority ordering for a revision pass

1. **(blocker)** §1.1 PLA → PETG sweep through `manuscript-body.tex`
   and the affected `references.bib` annotations.
2. **(blocker)** §1.3 fix `(author?)` bibtex artefacts.
3. **(blocker)** §1.4 remove "multifidelity" claims OR add fused
   sim-fidelity.
4. §1.2 backfill the third Contributions bullet.
5. §2.1 expand the BO Methods subsection with kernel / categorical /
   constraint / batch-size details.
6. §2.4 add the FFF process-parameter table.
7. §2.2 + §2.3 either expand the testing protocol or de-scope the
   crutch-tip framing; add SEA-to-peak-force mapping in Discussion.
8. §3 add the four bibliographic gap entries; update inline citations.

A second Edison ANALYSIS pass after #1–#5 is closed will give a clean
read on whether the remaining issues are still major or have dropped
to minor / editorial.

---

## Update: blocker fixes applied (this PR)

The following blockers from §3 have been addressed in source:

- **`(author?)` bibtex artefacts** — root cause was `\citet{...}` calls
  resolving against the `asmejour.bst` output, which emits raw author
  text without natbib's `\bibinfo{author}{...}` annotation. All eight
  `\citet{...}` calls in `manuscript-body.tex` were rewritten to
  inline-author form (e.g. `Pajunen et~al.~\cite{...}`). Verified via
  `pdftotext manuscript.pdf | grep '(author?)'` → 0 hits. Two
  pre-existing unescaped `&` in `references.bib` `journal` fields
  (`requejo2005upperextremitykinetics`, `macgillivray2016theinfluenceof`)
  were also fixed (`& physics` → `\& physics`).
- **Blank third Contributions bullet** — replaced the bare `\todo{}`
  bullet with a substantive third contribution describing the planned
  two-fidelity escalation path (pretensioned tensegrity assemblies with
  true cables / measured pretension); the choice between co-Kriging
  and nonlinear information-fusion surrogates is left as a
  `\todo{}` per Sterling's note that this is "somewhat TBD".
- **Bibliographic gaps from the AE letter** — added inline cites and
  bib entries for ISO 11334-4 (`iso11334-4`, walking-aid test methods,
  Methods §3.3 Drop-weight subsection); Caminero et~al. 2019
  (`caminero2019printingparameters`, FFF interface adhesion, Background
  §2.2); Garrido-Merch\'an \& Hern\'andez-Lobato 2020
  (`garridomerchan2020dealingwithcategorical`) and Baptista \&
  Poloczek 2018 BOCS (`baptista2018bocs`) — both cited in the BO
  Background and Methods subsections to address the categorical-variable
  treatment gap. (FFF resolution-limits ref was *not* added — left as a
  `\todo{}` placeholder pending a vetted citation; we did not want to
  guess.)
- **PLA → PETG global rewrite** — deferred to issue #45 per Sterling's
  comment.
- **Multifidelity claim** — kept, but reframed in the third Contribution
  as a *planned* two-rung escalation backed by pretensioned tensegrity
  assemblies (Sterling: "could be based on making an actual tensegrity
  structure out of it (pretensioned, actual cables, etc.). Somewhat
  TBD"); the fusion strategy is now an explicit `\todo{}`.

The methodological gaps (BO rigor table, FFF process-parameter table,
SEA→peak-force mapping, cyclic/off-axis loading) remain `\todo{}`
placeholders in `manuscript-body.tex` per Sterling's instruction not
to guess.
