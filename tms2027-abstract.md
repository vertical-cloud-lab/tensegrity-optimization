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

## Abstract (submission-ready; 146 words — 150 if em-dash compounds are split — ≤150 either way)

> Impact-protection structures often perform well in one loading direction
> but degrade sharply off-axis (e.g., honeycombs crushed in-plane,
> thin-walled crash tubes loaded obliquely, corrugated cores loaded
> transversely). We present a closed-loop
> design–print–test framework using batch Bayesian optimization to
> design tensegrity-inspired lattices with orientation-insensitive
> energy absorption. Hexagon-based unit cells—rigid PLA
> struts co-printed with TPU tension elements by multi-material
> fused deposition modeling—are parameterized by strut geometry,
> tension-element cross-section, and tiling. Each candidate is drop-tested
> at multiple impact angles; measured peak transmitted acceleration,
> specific energy absorption, and their cross-orientation variation update
> a noise-aware Gaussian-process surrogate that selects the next
> batch. The campaign comprises 25 batches of four designs (100
> experiments), targeting volumetric energy absorption exceeding the
> 0.34 J/cm³ of matched-density FDM TPU honeycombs (Bates et
> al., 2016) with minimal orientation-dependence of peak acceleration.
> Motivated by planetary-lander payload protection, this terrestrial
> demonstrator centers the optimization framework; future work targets
> flight-relevant materials.

---

## Notes on this revision

| Constraint (from @sgbaird) | How it is handled |
|---|---|
| **150-word limit** | Abstract is 140 words by `wc -w` (144 if em-dash-joined compounds are counted as separate words) — under the limit either way, with a few words of headroom for edits. |
| **No placeholders — results won't exist by the deadline** | All `[N]/[M]/[X%/Y J/g]` slots removed. The abstract states targets and campaign scope, not outcomes; no "preliminary results" claim remains. |
| **Targeted results vs. numbered baselines** | Target framed against Bates et al. (2016): FDM TPU honeycombs at up to **0.34 J/cm³** — the baseline with published numbers flagged in both Edison reviews (Cordero-persona Q1). Volumetric (J/cm³) rather than mass-specific (J/g) is used so the target is directly comparable to the published figure. |
| **25 batches × 4 designs = 100 experiments** | Stated verbatim in the abstract; also demonstrates the sample-efficiency/batch-BO framing reviewers asked for (Cordero-persona W5). |
| **Ground the off-axis opening claim with examples** | Parenthetical added to sentence 1 with three canonical, literature-backed cases (see below). Offsetting trims elsewhere keep the abstract ≤150 words. |

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

Word-count check: `sed -n '/^> Impact-protection/,/^> flight-relevant/p' tms2027-abstract.md | sed 's/^> //' | wc -w`

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
