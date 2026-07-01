# TMS 2027 Abstract — Tensegrity-Inspired Lattices for Orientation-Invariant Impact Protection

Revised per the review feedback in
[Issue #78](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/78):
the two Edison Scientific literature reviews and the Symposium 105
mock-reviewer personas (Cordero-style architected-materials reviewer;
Hofmann-style spacecraft-materials reviewer, both 2/5 "major revision").
The revision makes the **closed-loop BO design–print–test framework the
central contribution**; the Mars-lander application is motivation only, and
translation beyond FDM polymers (flight-relevant materials, environmental
qualification) is explicitly framed as future work.

- **Primary target:** Symposium 105 — *Accelerating Innovation in Materials
  and Manufacturing* (Cordero/Hofmann). Also suitable for 021
  (*AI-Enabled Materials Processing*) and 022 (*AI/ML/Data Informatics for
  Materials Discovery*).
- **Deadline note:** the TMS 2027 CFA flyers list abstracts due
  **July 1, 2026**.

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

## Abstract (submission-ready; ~245 words)

Bracketed values `[…]` are placeholders to fill from campaign data before
submission — see the fallback sentences below if numbers are not available
by the deadline.

> Impact-protection structures often perform well in one loading direction
> but degrade sharply off-axis — a critical limitation when impact
> orientation cannot be guaranteed. We present a closed-loop
> design–print–test framework that uses Bayesian optimization (BO) to
> design tensegrity-inspired lattice structures whose energy absorption is
> insensitive to impact orientation. Hexagon-based unit cells — rigid PLA
> struts co-printed with flexible TPU tension elements by multi-material
> fused deposition modeling (FDM) — are parameterized by strut geometry,
> tension-element cross-section, and unit-cell tiling. Each candidate is
> fabricated and evaluated in instrumented drop tests at multiple impact
> angles; measured peak transmitted acceleration, specific energy
> absorption (SEA), and their variation across orientations update a
> Gaussian-process surrogate whose noise-aware, multi-objective acquisition
> function proposes the next batch of designs. Because physical
> measurements — not calibrated simulation — drive the loop, the framework
> directly accounts for FDM process variability and rate-dependent TPU
> behavior. Preliminary results from [N] BO-selected designs and [M]
> replicate drop trials show [an X% reduction in the orientation-to-
> orientation variation of peak transmitted acceleration relative to the
> seed design, at an SEA of Y J/g], benchmarked against a matched-density
> FDM TPU honeycomb. This work is a terrestrial, low-TRL methodology
> demonstrator: PLA and TPU serve as rapid-iteration surrogate materials,
> and the contribution is the optimization framework itself. Motivated by
> payload protection for planetary landers, where terrain and attitude
> uncertainty demand orientation-robust energy absorption, future work will
> transfer the framework beyond FDM polymers to flight-relevant materials,
> processes, and environmental qualification.

### Fallback if quantitative results are not ready at submission

Replace the "Preliminary results…" sentence with:

> For every candidate we report peak transmitted acceleration, SEA, and
> their coefficient of variation across impact orientations, benchmarked
> under identical test conditions against a matched-density FDM TPU
> honeycomb.

---

## How each piece of feedback was implemented

| # | Feedback (source) | Implementation in the revision |
|---|---|---|
| 1 | "Non-prismatic tensegrity" undefined; "tensegrity-like" imprecise (both Edison rounds; Cordero W3) | Both terms removed; consistent **"tensegrity-inspired"** throughout, matching the IDETC abstract and Pajunen et al. (2019) usage. |
| 2 | Methodology should be the focus (trigger comment; Hofmann Q3; synthesis rev. 2) | The abstract now **opens and closes on the closed-loop BO framework**; the explicit thesis sentence is "the contribution is the optimization framework itself." |
| 3 | Mars framing overreaches TRL; PLA/TPU are not flight materials (Hofmann W1–W2) | Reframed as a **"terrestrial, low-TRL methodology demonstrator"** with PLA/TPU named as **surrogate materials**; Mars landers appear only as motivation. |
| 4 | Other materials/processes are "down the road" (trigger comment; Hofmann W7) | Final sentence is a forward-looking roadmap: transfer **beyond FDM polymers** to flight-relevant materials, processes, and environmental qualification. |
| 5 | Orientation-invariance should be the explicit BO objective, not a validation step (Cordero W5; first Edison round) | Orientation variation of peak transmitted acceleration is now stated as an **optimization objective** fed to the surrogate, not a post-hoc check. |
| 6 | BO loop under-specified (Cordero W5; synthesis rev. 4) | Names the design variables (strut geometry, tension-element cross-section, tiling), the GP surrogate, the noise-aware multi-objective acquisition, and batch selection. |
| 7 | No quantitative crashworthiness metrics (Cordero W1, W7; synthesis rev. 1) | Reports **peak transmitted acceleration, SEA (J/g), and cross-orientation variation** with placeholder slots for headline numbers and trial counts; fallback sentence provided. |
| 8 | No baseline comparison (Cordero W2; synthesis rev. 3) | Adds an explicit **matched-density FDM TPU honeycomb** benchmark (per Bates et al. 2016). |
| 9 | Drop tests are stochastic; "consistent" needs trial counts (Cordero W5; first Edison round) | "[M] replicate drop trials" placeholder plus "noise-aware" acquisition language acknowledge measurement stochasticity. |
| 10 | "High fidelity materials" / "real-world field demonstrations" vague (both Edison rounds; Hofmann W6) | Both phrases removed; testing described concretely as **instrumented drop tests at multiple impact angles**. |
| 11 | FDM variability and TPU rate-dependence ignored (Cordero W4, W6) | Called out directly: the experiment-driven loop "accounts for FDM process variability and rate-dependent TPU behavior." |
| 12 | Circular "supplement future Mars exploration techniques…" wording; "in order to"; mixed tense (first-round feedback) | Rewritten throughout; single present-tense narrative, motivation stated in one clause. |
| 13 | Title needed (@sgbaird, 2026-07-01) | Recommended title plus two alternates above; avoids "non-prismatic," "tensegrity-like," and unqualified "Mars lander," per the persona-review guidance. |

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
