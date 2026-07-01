# TMS 2027 Symposium Fit Analysis — Tensegrity-Inspired Lattice Abstract

Re-evaluation of symposium targets for the tensegrity-inspired hexagonal-lattice /
FDM (PLA + TPU) / Bayesian-optimization / impact-absorption abstract (Issue #78).

**Meeting:** TMS 2027, Mar 14–18, 2027, Orlando, FL.
**⚠ Abstract submissions due: July 1, 2026 (per every flyer's "KEY DATES").**
Source: [ProgramMaster TMS2027](https://www.programmaster.org/TMS2027) ·
CFA flyers at `https://www.tms.org/tms2027/downloads/flyers/TMS2027-CFA-Flyer-<ID>.pdf`.

Organizer data: `tms2027_symposium_organizers.csv` (106 symposia, 682 organizer rows).

---

## 1. Verdict on flyer 070 (Materials and Manufacturing in Space) — POOR FIT

The user's instinct is correct. Flyer 070's scope is **manufacturing *in* space**, not
landing-impact protection. Its solicited topics:

- materials *synthesized* in low-earth-orbit microgravity (pharma, semiconductors);
- space-environment effects (vacuum, atomic oxygen, radiation) on materials;
- **welding / forming / additive manufacturing performed in microgravity**;
- building large structures (solar arrays) in orbit; autonomous/robotic in-space mfg.

Nothing about impact absorption, energy dissipation, crushable structures, or landers.
The "Mars" mention refers to a Lunar/Mars **surface reactor** and in-situ manufacturing,
not descent/landing loads.

**Organizing committee is metals-/in-space-manufacturing-oriented, not impact/architected-materials:**

| Organizer | Affiliation | Background |
|---|---|---|
| David Williams | Ohio State | Electron microscopy / characterization |
| Antonio Ramirez | Ohio State | Welding & joining |
| Alan Luo | Ohio State | Mg / lightweight alloys, ICME (casting) |
| Wolfgang Windl | Ohio State | Computational materials |
| Boyd Panton | Ohio State | Joining / solidification |
| Jonathan Volk | Voyager Technologies – Starlab | Commercial space station |
| W. Jud Ready | Georgia Tech | Nanomaterials, energy, space |
| Jeffrey Sowards | NASA Marshall | Welding & metallurgy |

Committee sponsor is the **TMS Solidification Committee** — a strong tell that this is a
metals-processing-in-microgravity forum. **Recommend dropping 070** unless the abstract is
re-pitched around *fabricating* the lattice in space (not its impact performance), which
is not the project's thesis.

---

## 2. Revised ranking (existing + newly suggested)

### Tier 1 — Method bullseye (lowest risk, most method-agnostic)

**#1 · Flyer 021 — AI-Enabled Materials Processing: Integrating Accelerated Experimental
Workflows and Processing-Aware Machine Learning** (Data-Driven & Computational Design)
The scope statement *explicitly* names **"Bayesian optimization for process tuning; and
closed-loop experimental workflows that integrate synthesis, processing, characterization,
testing, and iterative model-guided refinement."** That is a verbatim description of the
design→print→drop-test→BO loop.
*Caveat:* framed around processing→microstructure→property (heat treatment, casting, AM
process params). Reframe print/geometry parameters as the "processing history" design
variables to land cleanly.
Organizers: Sreenivas Raguraman (JHU), Maitreyee Sharma Priyadarshini (Virginia Tech),
Timothy Weihs (JHU), Thomas Voisin (LLNL), **Allison Beese (Penn State — mechanical
behavior of AM materials)**, Samantha Webster (Colorado School of Mines).

**#2 · Flyer 022 — AI/ML/Data Informatics for Materials Discovery: Bridging Experiment,
Theory, and Modeling** (Data-Driven & Computational Design)
Most method-agnostic home. Explicitly welcomes **sparse, noisy, heterogeneous experimental
data** and physics+AI — a good match for stochastic drop-test data and few-shot BO.
Organizers include two standouts (see §3): **James Saal (Citrine Informatics — sequential
learning / BO for materials)** and **Taylor Sparks (Univ. Utah — materials informatics)**.

### Tier 2 — Strategic / application venue (NEW suggestion)

**#3 · Flyer 105 — Accelerating Innovation in Materials and Manufacturing** (Special Topics)
*New suggestion, and arguably the best audience for the application angle.* Organized by
**Zachary Cordero (MIT)** and **Douglas Hofmann (NASA JPL)** — see §3; Cordero's group is a
near-exact research twin (architected lattices for energy absorption / impact).
**Format caveat:** this is a one-day **panel + pitch** symposium (invited talks, moderated
panels, and a **midday pitch competition for students / postdocs / early-career
researchers**), not a standard contributed-podium technical symposium. That pitch
competition is an excellent, low-barrier venue for a student-led project, and it puts the
work directly in front of Cordero and Hofmann. Themes explicitly include space,
accelerated materials development, and advanced manufacturing.

### Tier 3 — Traditional AM (fits, but skews metals/process)

**#4 · Flyer 003 — Additive Manufacturing Modeling, Simulation, and Artificial Intelligence:
Microstructure, Mechanics, and Process.** AM + AI + mechanics, but organizers/scope skew
metallic process–structure. Usable if the mechanics + BO is foregrounded; more competitive
against metals abstracts.

### Demote / drop (previously listed, weaker on closer reading)

- **Flyer 013 — 3D Printing of Scaffolds and Porous Materials** — despite the "porous/lattice"
  surface match, the scope is squarely **biomaterials / tissue engineering** (bioinks,
  scaffolds, drug delivery, organ-on-chip, cell–biomaterial interaction). Not an
  energy-absorption venue. *Demote.* (Contact of note: Heinz Palkowski, Clausthal — works on
  metal/polymer sandwich & lightweight energy-absorbing structures — but the symposium framing
  is biomedical.)
- **Flyer 001 — AM and Innovative Feedstock Processing for Multifunctional Materials** —
  "multifunctional" here means **magnetic/functional** materials (soft/hard magnets,
  magnetocaloric, shape-memory) via powder/wire metallurgy, *not* energy-absorbing
  multifunctionality. *Drop.*
- **Flyer 005 — Designing Complex Microstructures Through AM** — about **metal-alloy
  microstructure/solidification** via fusion AM; not architecture/geometry or polymers. *Drop.*

### Other new candidates considered (weaker, mention only)

- **024 · AI Applications in ICME (AI-ICME)** — computational/ICME emphasis; contact of note
  **Pinar Acar (Virginia Tech)** does optimization / UQ of microstructures (BO-adjacent).
- **029 · Computational Discovery and Design of Materials** — computational emphasis; contact
  of note **Suhas Eswarappa Prameela (Univ. Utah)** works on mechanical behavior of lightweight
  / architected metals.
- **019 · Computational Modeling and ML for Bio-Related and Sustainable Materials** — only if
  reframed around sustainability; contact **Zhao Qin (Syracuse)** models architected/mechanical
  materials with ML.

> **Honest caveat:** TMS 2027 has **no dedicated architected-/cellular-materials or
> mechanical-metamaterials symposium.** The cleanest homes are the two AI/ML method symposia
> (021, 022); 105 is the best *audience/application* venue via its pitch competition.

---

## 3. Standout organizers likely to be interested

Ranked by directness of research overlap with the project:

1. **Zachary Cordero — MIT, Aero/Astro (Aerospace Materials & Structures Lab)** — *symp 105.*
   **The strongest match on the entire committee list.** Directly publishes on architected
   lattices for energy absorption and their quasi-static **and dynamic/impact** behavior in
   additively manufactured cellular materials:
   - "Architected Lattices with Adaptive Energy Absorption" ([arXiv:1909.05231](https://arxiv.org/pdf/1909.05231))
   - "Quasi-static and Dynamic Behavior of Additively Manufactured Metallic Lattice Cylinders" ([arXiv:1801.05378](https://arxiv.org/pdf/1801.05378))
   - "Process parameter sensitivity of the energy-absorbing properties of AM metallic cellular materials" ([arXiv:2212.00438](https://arxiv.org/pdf/2212.00438))
   - Interpenetrating lattices with tailorable energy absorption (Acta Materialia, 2021).
   Profile: [MIT AeroAstro](https://aeroastro.mit.edu/people/zachary-cordero/) · [Lab](https://cordero.mit.edu/prof-cordero/).

2. **Douglas Hofmann — NASA JPL (Principal Scientist)** — *symp 105.* Spacecraft materials,
   additive manufacturing, and metal-matrix composites/BMG for space hardware (PECASE for
   "metal-matrix composites for spacecraft"; co-founder of Amorphology for planetary/strain-wave
   gears). Bridges the Mars-lander application framing to a credible aerospace-materials
   audience. Profile: [JPL](https://www.jpl.nasa.gov/site/research/hofmann/) ·
   [Scholar](https://scholar.google.com/citations?user=f3dhjoYAAAAJ&hl=en).

3. **James Saal — Citrine Informatics** — *symp 022.* Citrine is built on **sequential
   learning / Bayesian optimization for materials & formulations** — the exact methodology of
   this project. A natural reviewer/contact for the BO angle.

4. **Taylor Sparks — University of Utah** — *symp 022.* A prominent, engaged
   materials-informatics researcher/educator (ML for materials, benchmark datasets). Likely
   receptive to an experimental BO design-build-test story.

5. **Secondary contacts:** Allison Beese (Penn State, symp 021 — AM mechanical behavior);
   Pinar Acar (Virginia Tech, symp 024 — optimization/UQ); Suhas Eswarappa Prameela (Utah,
   symp 029 — mechanical behavior of architected/lightweight metals); Heinz Palkowski
   (Clausthal, symp 013 — energy-absorbing lightweight sandwich structures).

---

## 4. Recommended action

- **Submit to 021 and 022** (method-agnostic, deadlines permitting) — reframe the print/geometry
  parameters as the design/"processing" variables and lead with a headline energy-absorption
  metric so it reads as an *experimental* BO closed loop, not a bare application.
- **Consider the 105 pitch competition** for the student/early-career angle and direct exposure
  to Cordero + Hofmann.
- **Drop 070** (in-space manufacturing ≠ landing-impact protection) and **013/001/005**
  (biomaterials / magnetics / alloy-microstructure mismatches).
- Mind the **July 1, 2026 abstract deadline**.
