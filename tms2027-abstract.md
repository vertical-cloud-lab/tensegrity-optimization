# TMS 2027 Abstract — Tensegrity-Inspired Lattices for Orientation-Invariant Impact Protection

Revised per the review feedback in
[Issue #78](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/78)
(two Edison Scientific literature reviews plus the Symposium 105
Cordero/Hofmann mock-reviewer personas), then tightened to the
**150-word limit** with **no result placeholders**: experimental results
will not exist by the submission deadline, so the abstract states the
*planned campaign* (25 batches × 4 designs = 100 experiments) and
*targeted* performance against a published, numbered baseline
(Bates et al. 2016: FDM TPU honeycombs absorb up to 0.34 J/cm³).

- **Primary target:** Symposium 105 — *Accelerating Innovation in Materials
  and Manufacturing* (Cordero/Hofmann). Also suitable for 021
  (*AI-Enabled Materials Processing*) and 022 (*AI/ML/Data Informatics for
  Materials Discovery*).

---

## Title

> **Closed-Loop Bayesian Optimization of 3D-Printed Tensegrity-Inspired
> Lattices for Orientation-Invariant Impact Protection**

Alternates, depending on venue emphasis:

1. *Accelerated Design of Multi-Material Tensegrity-Inspired Energy
   Absorbers via Closed-Loop Bayesian Optimization and Drop Testing* —
   mirrors Symposium 021/105 "accelerating innovation" language.
2. *Landing on Any Face: Bayesian-Optimized 3D-Printed Lattices for
   Omnidirectional Impact Protection* — punchier variant for the
   Symposium 105 pitch-competition format.

---

## Authors

> Audrey Christiansen\*; Marcus Madsen\*; Jinkwan Han\*; Jeffrey R. Hill†
> (presenting); Sterling G. Baird† — Department of Mechanical Engineering,
> Brigham Young University, Provo, UT, USA
>
> \* Equal contribution. † Equal contribution.

Copied from the author block in
[PR #73](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/73)
(`tms-2027-abstract.md`), reordered per @sgbaird: Audrey, Marcus, Jinkwan,
Jeff, Sterling. Equal-contribution markers (\* students, † advisors) and the
presenting-author designation are unchanged.

---

## Abstract (submission-ready; 148 words by `wc -w`, 150 if the two em-dash-joined compounds are split — at or under the limit either way)

> Planetary landers cannot dictate their impact orientation, yet
> conventional energy absorbers—honeycombs crushed in-plane, thin-walled
> crash tubes loaded obliquely, corrugated cores loaded
> transversely—degrade sharply off-axis. We present a closed-loop
> design-print-test framework using Bayesian optimization to design
> tensegrity-inspired lattices with orientation-insensitive energy
> absorption: hexagonal cells whose rigid PLA struts carry compression
> in a continuous TPU tension network, co-printed by multi-material
> fused deposition modeling (FDM). Nine design variables span strut
> diameter and length, tension-element cross-section, strut count,
> connectivity, tiling, and FDM processing (nozzle temperature, print
> speed). Candidates are drop-tested across orientations; peak
> transmitted acceleration, specific energy absorption, and
> cross-orientation variation update a noise-aware Gaussian-process
> surrogate selecting the next batch. The campaign comprises 25 batches
> of four designs (100 experiments), targeting energy absorption
> exceeding 0.34 J/cm³ (matched-density FDM TPU honeycombs; Bates et
> al., 2016) with minimal orientation-dependence of peak acceleration.
> This terrestrial demonstrator centers the optimization framework;
> future work targets flight-relevant materials.

If a couple of words must be freed for late edits: drop the
"; Bates et al., 2016" citation (–4), delete "loaded" before
"transversely" (–1), or "conventional" (–1) — each removal leaves the
surrounding sentence grammatical.

---

## Notes on this revision

| Constraint (from @sgbaird) | How it is handled |
|---|---|
| **150-word limit** | Abstract is 148 words by `wc -w` (150 if the two em-dash-joined compounds are counted as separate words) — at or under the limit either way. |
| **Lead with the space application (planetary-lander opening)** | Opening sentence is now *"Planetary landers cannot dictate their impact orientation, yet conventional energy absorbers—honeycombs crushed in-plane, thin-walled crash tubes loaded obliquely, corrugated cores loaded transversely—degrade sharply off-axis."* The three grounded off-axis examples move inside the em-dashes, and the closing sentence drops its now-redundant "Motivated by planetary-lander payload protection," lead-in to pay for the longer opening. The honest terrestrial-demonstrator framing still closes the abstract. |
| **No placeholders — results won't exist by the deadline** | All `[N]/[M]/[X%/Y J/g]` slots removed. The abstract states targets and campaign scope, not outcomes; no "preliminary results" claim remains. |
| **Targeted results vs. numbered baselines** | Target framed against Bates et al. (2016): FDM TPU honeycombs at up to **0.34 J/cm³** — the baseline with published numbers flagged in both Edison reviews (Cordero-persona Q1). Volumetric (J/cm³) rather than mass-specific (J/g) is used so the target is directly comparable to the published figure. |
| **25 batches × 4 designs = 100 experiments** | Stated verbatim in the abstract; also demonstrates the sample-efficiency/batch-BO framing reviewers asked for (Cordero-persona W5). |
| **Ground the off-axis opening claim with examples** | Parenthetical added to sentence 1 with three canonical, literature-backed cases (see below). Offsetting trims elsewhere keep the abstract ≤150 words. |
| **Restore the tensegrity-inspired framing (unit cells sounded bland)** | The unit-cell sentence now states the tensegrity mechanics explicitly: *"hexagonal cells whose rigid PLA struts carry compression in a continuous TPU tension network"* — compression-carrying struts inside a continuous tension network is the defining tensegrity load path, so the cells are framed by their mechanics rather than just their hexagonal shape. |
| **State the number of design variables** | "Nine design variables": strut diameter (1), strut length (2), tension-element width (3) and thickness (4) [= cross-section], strut count (5), connectivity topology (6), tiling pattern (7) — the seven from the IDETC design-space section — plus nozzle temperature (8) and print speed (9). **Caveat:** if temperature/speed are set per material (PLA and TPU separately), the count becomes eleven — change the one word "Nine" → "Eleven". |
| **Include FDM processing parameters (heat, speeds)** | "…and FDM processing (nozzle temperature, print speed)" added to the design-variable list. Note this supersedes the IDETC abstract's statement that print parameters are *held fixed* within a batch — the TMS campaign optimizes over them. |

### Grounding for the opening-sentence examples

Each example in the new parenthetical is a well-documented case of
orientation-dependent energy absorption, so a reviewer can verify the
claim immediately:

1. **Honeycombs crushed in-plane** — honeycomb out-of-plane crush
   strength scales ~(t/l) while in-plane strength scales ~(t/l)², an
   order-of-magnitude (or more) gap at typical relative densities
   (Gibson & Ashby, *Cellular Solids: Structure and Properties*, 2nd
   ed., 1997, ch. 4). This is also why lander crushable honeycomb
   (Viking/InSight legs) is oriented for axial loading.
2. **Thin-walled crash tubes loaded obliquely** — energy absorption of
   axially efficient square aluminum extrusions collapses when a small
   load angle (≳5–10°) switches the mode from progressive axial folding
   to global bending (Han & Park, *Comput. Struct.* 73, 1999 — critical
   load angle; Reyes, Langseth & Hopperstad, *Int. J. Mech. Sci.* 44,
   2002 — oblique quasi-static tests showing sharply reduced mean
   load/energy vs. axial).
3. **Corrugated cores loaded transversely** — prismatic corrugated
   sandwich cores are strong along the corrugation/normal directions
   but much weaker in transverse shear/crush, a known anisotropy of
   prismatic topologies (Côté, Deshpande, Fleck & Evans, *Int. J.
   Solids Struct.* 43, 2006).

Retained from the previous revision: "tensegrity-inspired" terminology,
orientation-invariance as the explicit optimization objective, the named
design variables and noise-aware GP surrogate, the honest
terrestrial-demonstrator framing with Mars as motivation only, and the
flight-materials roadmap as future work.

Word-count check: `sed -n '/^> Planetary landers/,/^> future work targets/p' tms2027-abstract.md | sed 's/^> //' | wc -w`

### Original abstract (for reference)

> We present an exploration of non-prismatic tensegrity configurations in
> order to improve the impact absorption capabilities of tensegrity
> structures. We currently use a hexagon-based, tensegrity-like lattice
> arrangement and FDM fabrication to create a prototype TPU and PLA
> structure capable of protecting a payload under high-impact conditions.
> To improve payload protection for future Mars landers, our goal is to
> supplement future Mars exploration techniques through impact absorption
> in a Mars lander using Bayesian optimization of lattice base-unit
> geometry. The designs are validated using controlled drop testing
> devices, as well as real-world field demonstrations in which we use high
> fidelity materials for testing these structures. Structures are dropped
> from different angles to evaluate their anisotropic properties. The
> prototype is being optimized for consistent impact absorption regardless
> of landing orientation. Preliminary experimental results demonstrate
> successful payload protection across a range of testing conditions and
> design parameters.
