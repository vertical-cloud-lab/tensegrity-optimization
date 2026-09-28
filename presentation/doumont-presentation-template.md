# IDETC Presentation — Doumont Presentation Structure Template

Transcribed from Jean-luc Doumont's presentation-structure template
([TM&Th-3.2-template.pdf](https://principiae.be/pdfs/TM&Th-3.2-template.pdf)),
adapted from *Trees, maps, and theorems* (Principiae, 2009). © 2009 by Principiae.
All rights reserved. Can be downloaded from <https://www.treesmapsandtheorems.com>.

> To design your presentation, write down your ideas for each component below.
> If useful, you can then further develop your body afterwards (the "back of the sheet").

**Draft 3** — applies the inline review comments from @sgbaird on PR #84 and the
priority revisions from the
[Edison mock-audience report](edison-mock-audience/mock-audience-feedback.md).
Summaries of what changed are at the bottom of this file
([Draft 2 → 3](#changes-from-draft-2), [Draft 1 → 2](#changes-from-draft-1)).

**Scope note (frame everything below with this):** the study presented is the
optimization of a **T3-prism tensegrity-inspired structure together with FDM
processing parameters** (e.g., nozzle temperature, print speed). PLA–TPU is a
**proxy system** — not flight material — used to prototype a self-driving-lab
style, near-autonomous workflow for optimizing tensegrity-inspired structures.
The planetary lander is *motivation*, not demonstrated readiness. Everything
beyond the T3 study (lattices, flight materials, crutch tip) is future work.

## Opening

### Attention getter

*A way to lead the audience to the need efficiently*

Tensegrity provides robust, **reusable** solutions to issues posed by planetary
landings — and to problems closer to home.

One or two sentences of setup, then let the Super Ball Bot image (or a short
clip) do the work:

> Landing a payload on another planet means surviving an impact in conditions
> where parachutes and retrorockets struggle — thin atmospheres, rough
> terrain. NASA's Super Ball Bot concept answers this with a tensegrity
> structure: the lander *is* the energy absorber. And unlike crushable
> aluminum honeycomb or sacrificial airbags, a tensegrity lander can take the
> hit **and get back up** — it survives multiple drops and keeps working.

Candidate Super Ball Bot videos to show (verified links):

- [Super Ball Bot](https://www.youtube.com/watch?v=ZBSRdGlAh5s) — NASA Video
  (official channel); the canonical overview.
- [NASA Demonstrates Super Ball Bot Prototype](https://www.youtube.com/watch?v=L2cJej3EmcA)
  — Wall Street Journal; prototype drop footage.
- [HET2 SUPERball Bot Task NIAC Mission concept](https://www.youtube.com/watch?v=1wce-mB69mE)
  — NASA Video; mission-concept animation (Titan descent) — strong hook material.

Immediately after the hook, state the present study scope in one sentence
(per the scope note above): *we study a printed PLA–TPU T3 prism as a proxy
system for prototyping an autonomous tensegrity-optimization workflow* — so
the planetary framing never outruns the demonstrated scope.

<!-- Optional aside, kept for future-work tie-in only (per manuscript scope in
#75/#76): the tensegrity crutch tip from the paper Dr. Hill found. -->

### Need

*A difference between actual and desired situations*

**Actual situation** (a two-sided pincer — stated as a scoped engineering
judgment, not an absolute):

- For these structures, obtaining trustworthy objective values from a
  validated high-fidelity model would require substantial calibration of
  interface, rate, contact, and defect behavior — and even heavy-duty
  simulation falls short of the experiments we are running: peak transmitted
  shock is a millisecond-scale transient that is notoriously difficult to
  resolve numerically. This holds even for idealized cable–strut tensegrities
  in their actual engineering materials (steel or similar), not just for
  printed PLA–TPU.
  <!-- TODO: justify the simulation–experiment gap with an Edison literature
  search, or alternatively present validation of our experimental results
  against simulated results (per review comment on the preview). -->
- Exhaustive physical search fails on cost: a traditional design of
  experiments over this relatively high-dimensional space (geometry + FDM
  process parameters) would demand hundreds of specimens, each costing print
  and test time.
- Assembly does not scale: a single T3 prism can be assembled by hand, but
  more complex structures — especially tensegrity *lattices* — become
  extremely difficult and ultimately infeasible to hand-build.

**Desired situation:**

- Trustworthy performance data without hand assembly (easy creation of
  tensegrity structures, scalable beyond a single prism).
- Quick iteration and testing — find good designs in dozens of experiments,
  not the hundreds a traditional design of experiments would require.

### Task

*What I decided/was asked to do to address the need*

Build a closed-loop design–print–test workflow that optimizes a **T3-prism
tensegrity-inspired energy absorber together with its FDM processing
parameters** (e.g., temperature, print speed) directly from real, measured
impact data — maximizing energy absorbed per gram (specific energy
absorption) and compaction efficiency, subject to a cap on the peak force
transmitted to the payload. Extensions beyond the T3 prism are future work.

### Main message

*The one sentence I want my audience to remember*

By closing the loop between multi-material 3D printing and Bayesian
optimization, we can optimize tensegrity-inspired energy absorbers directly
from real impact data — in dozens of prints, not the hundreds a traditional
design of experiments would demand.

<!-- This efficiency claim must be carried by the Evidence/results slides
(campaign ledger + budget-matched baseline). If the campaign cannot yet
support it, fall back to: "we evaluate whether noisy multi-objective Bayesian
optimization can substantially reduce the physical test budget." -->

### Preview

*A map of the body (ideally three points, max. five)*

1. When model calibration and exhaustive testing are both costly, each
   physical specimen must be chosen for its information value — so the
   measured experiment is our source of truth.
2. Bayesian optimization makes physical experimentation affordable: it handles
   noisy measurements, small batches, and the constrained multi-objective
   trade-off — and Honegumi let us scaffold it in minutes.
3. Multi-material additive manufacturing closes the loop: single-build PLA–TPU
   co-fabrication turns each proposed design into test data in hours, with no
   joining of parts.
4. *(Optional fourth point, if time allows)* The same closed loop points at
   what comes next: tensegrity lattices, flight-relevant materials, and
   safety hardware on Earth.

## Body

### Point 1

When model calibration and exhaustive testing are both costly, each physical
specimen must be chosen for its information value.

- Scoped, not absolute (do **not** say "simulation can't be trusted"): for
  these structures, a sufficiently calibrated multiphysics model is expensive
  to build relative to the design campaign itself — and the hardest quantity,
  peak transmitted shock, is a millisecond-scale transient that even
  heavy-duty simulation struggles to resolve. The gap persists in the actual
  engineering materials a real lander would use (steel struts and cables),
  so this is not merely an artifact of printed PLA–TPU.
- The alternative — sweeping the design space physically — fails on cost: a
  traditional design of experiments over geometry plus FDM process parameters
  would take hundreds of specimens, each needing print + test time.
- Therefore: treat the physical experiment as the authoritative source of
  objective values, and be ruthless about *which* experiments to run.
- Anticipate the FEA-veteran pushback ("inconvenient ≠ untrustworthy"): frame
  it as a cost-and-dependence decision, and keep a backup slide with the
  literature (or our own validation) on simulation–experiment discrepancy for
  impact transients.

### Transition

If every data point must be a real experiment, we need a method that extracts
the most from every specimen — we need to make the process radically more
sample-efficient.

### Point 2

Bayesian optimization makes physical experimentation affordable, even with
limited, noisy data.

- Two-level explanation (per mock-audience feedback): one plain sentence + one
  visual in the main talk; implementation detail goes to backup slides.
  Spoken version:
  > "After each batch, the model estimates both expected performance and
  > uncertainty across the design space. The acquisition rule selects a small
  > next batch that is most likely to expand the feasible trade-off frontier,
  > while accounting for noisy tests and print failures."
- Noisy physical measurements: TPU batch-to-batch variation and print defects
  motivate a noise-aware acquisition function (qNEHVI) rather than
  non-noise-aware alternatives. (Backup slide: how observation noise is
  actually modeled — replicates, noise identification — and budget-matched
  baselines such as Sobol/random sampling.)
- Small parallel batches: the surrogate proposes the next batch of specimens
  to print, balancing exploration and exploitation.
- Constrained multi-objective by construction: **objectives** = maximize
  specific energy absorption and compaction efficiency; **constraint** = peak
  transmitted force must stay under a cap; the deliverable is the *feasible*
  Pareto front between the two objectives among force-cap-satisfying designs.
  (Keep this formulation consistent everywhere — do not present "SEA vs. peak
  force" as the trade-off.)
- **Honegumi**: we scaffolded and adapted the Bayesian-optimization script for
  this advanced task (noisy, batched, constrained, multi-objective) in
  minutes using [Honegumi](https://honegumi.readthedocs.io/) — the audience
  can do the same for their own problems; show the code-template picker
  briefly so they see how low the barrier is.

### Transition

The optimizer is no longer the bottleneck — the limit is now providing real
data quickly enough.

### Point 3

Multi-material additive manufacturing supplies that data fast — single-build
co-fabrication, with no joining of parts.

- Single-build PLA–TPU co-fabrication: rigid struts and flexible tension
  network in one print — no joining or hand assembly of members, which closes
  the "easy creation" gap from the Need and is what makes future lattices
  feasible at all. (Be precise: if support removal, trimming, or conditioning
  remain, say "no joining of PLA and TPU members" rather than "zero
  assembly.")
- Show the mechanism, not just the word "tensegrity-inspired": a labeled
  as-printed specimen (rigid PLA struts, continuous TPU tension network,
  pre-tension status) plus a short deformation sequence — so the EDL engineer
  doesn't file it as a "crush structure" and the grad student can tell it from
  an ordinary lattice.
- Rapid iteration: each BO-proposed candidate goes from parameter vector to
  tested specimen (quasi-static compression + instrumented drop-weight impact)
  in hours. (Backup slide: representative print-to-result time breakdown and
  which steps remain manual — candidate selection is automated; slicing,
  handling, and testing are not yet.)
- Now we have the data we need to complete the loop.

### Point 4 (optional — future applications)

*Include if timing allows; otherwise fold into the Conclusion.*

The same closed loop transfers wherever tests are authoritative, each test is
costly, the design space is mixed, and several performance goals conflict:

- Tensegrity *lattices* and more complex architectures — exactly where hand
  assembly becomes infeasible and single-build co-fabrication pays off.
- Migration from the PLA–TPU proxy toward flight-relevant materials and
  impact regimes.
- Safety hardware on Earth (e.g., the tensegrity crutch tip — future work).
- Toward a self-driving lab: closing the remaining manual gaps (slicing,
  handling, testing) in the loop.

### Evidence / results

*What we found — ground the conclusion in shown data*

Build the talk around a quantitative three-slide sequence (per the
mock-audience report; insert observed values once the campaign completes):

1. **Campaign ledger** — "The campaign used N specimens across B adaptive
   batches under a fixed physical-test budget": initialization vs. adaptive
   batches, replicates, print failures, cycle time, and the numerical value
   (and rationale) of the force cap.
2. **Budget-matched baseline** — "Adaptive selection improved the feasible
   design set faster than [predeclared baseline]": performance vs. number of
   physical tests against Sobol/random sampling at the same budget, with
   uncertainty where available.
3. **Measured feasible Pareto front** — specific energy absorption vs.
   compaction efficiency among designs satisfying the force cap, with
   replicate spread, marked infeasible designs, and specimen photos or
   force–time traces for representative Pareto designs.

Supporting raw-data candidates: drop-test force–time traces, Sobol /
first-batch results (PR #35 / PR #67), printing and impact-test footage.

### Suggested 15-minute allocation

*(From the mock-audience report — results get the largest block.)*

| Time | Content |
|---|---|
| 1.5 min | Super Ball Bot hook + specimen + present study scope |
| 2 min | Why exhaustive physical search and high-fidelity calibration are both costly |
| 2.5 min | One visual of the closed loop + the one-sentence BO explanation |
| 2 min | Design variables, objectives, force constraint, failures, noise controls |
| 5 min | Measured results: ledger, baseline, Pareto front, specimens, failure modes |
| 1 min | Limitations and transfer conditions |
| 1 min | Measured conclusion + bookend |

Move kernel choices, encodings, and other implementation detail to backup
slides. For Q&A preparation, use the 17-row claims-vs-evidence table in the
[mock-audience report](edison-mock-audience/mock-audience-feedback.md#claims-needing-evidence-hedging-or-backup-slides).

## Closing

### Review

*A recap of the body, leading into the conclusion*

Using real, measured impact data from additively manufactured
tensegrity-inspired structures — parametric designs proposed by a Bayesian
optimization routine — we rapidly iterate toward better energy absorbers.
This feedback loop makes tensegrity optimization dramatically faster: dozens
of prints instead of the hundreds a traditional design of experiments over
this design space would require.

### Conclusion

*What the above means to the audience in the end*

Because the loop runs on physical measurements, it is useful precisely where
model calibration is not worth its cost — and the same closed-loop pattern
should transfer (a conditional claim, pending evidence) to other additively
manufactured architectures whose performance is dominated by
hard-to-simulate effects. Give the audience the deployment rule explicitly:
*use this loop when tests are authoritative, each test is costly, the design
space is mixed, and several performance goals conflict.* For tensegrity
specifically, it opens a path from this T3 proxy study toward lattices,
flight-relevant materials, payload protection on other planets, and safety
hardware here on Earth (e.g., the crutch tip, as future work).

### Close

*A way to end the presentation clearly and elegantly*

Return to the opening image: the next planetary lander's energy absorber — a
structure that has to survive not one impact but many — doesn't have to take
years of hand-built prototypes; with this loop, candidate designs can be
designed, printed, and tested against real impacts in weeks instead of months
or longer. End on the measured engineering result and its transfer condition,
then the bookend: every method that compresses design time moves our ventures
— on this planet and beyond — forward.

---

## Changes from Draft 2

Applied from @sgbaird's inline review comments on PR #84 and the
[Edison mock-audience report](edison-mock-audience/mock-audience-feedback.md):

**From the inline review comments:**

1. **Reusability in the hook** (line 22): the tensegrity lander survives
   multiple drops, unlike crushable/sacrificial alternatives.
2. **Proxy-system framing** (lines 49, 87): PLA–TPU would never fly; it is a
   proxy for prototyping a self-driving-lab-style workflow — stated in a
   scope note up front and re-stated right after the hook.
3. **"Expensive" de-emphasized** (line 52): the argument is now that even
   heavy-duty simulation falls short of the experiments (millisecond-scale
   peak shock), not that it merely costs too much.
4. **Assembly-scaling argument** (line 60): one T3 prism is hand-assemblable;
   complex structures and especially lattices are not.
5. **Task scoped** (line 70): T3 structure + FDM processing parameters
   (temperature, print speed, …) only; the rest is explicitly future work.
6. **Simulation-gap justification flagged** (line 87): TODO for an Edison
   literature search (or validation of experiments against simulation), plus
   the millisecond-resolution peak-shock argument.
7. **Optional Point 4 added** (line 97): future applications, with a note it
   can fold into the Conclusion if time is short.
8. **Steel-materials point** (line 104): simulations fall short for the
   actual engineering materials (steel struts/cables), not just printed
   PLA–TPU.
9. **Honegumi featured** (line 130): how it scaffolded the advanced BO script
   in minutes, pitched so the audience sees they can use it too.
10. **"Thousands" → "hundreds"** (line 173): baseline is now a traditional
    design of experiments over a high-dimensional space (hundreds), in the
    main message, Need, Point 1, and Review.
11. **"Weeks not years" softened** (line 191): now "weeks instead of months
    or longer" for candidate designs.

**From the mock-audience report's priority revisions:**

12. **Quantitative three-slide results sequence** (Priority 1): campaign
    ledger → budget-matched baseline → measured feasible Pareto front, with a
    fallback main-message wording if the campaign can't yet support the
    efficiency claim.
13. **Anti-simulation premise replaced with a scoped cost decision**
    (Priority 2): Point 1 retitled to the information-value message;
    "simulation can't be trusted" removed everywhere; FEA-veteran pushback
    anticipated with a backup slide.
14. **15-minute allocation table added** (Priority 3): 5 minutes on results;
    implementation detail moved to backup slides; Q&A prep pointed at the
    report's claims-vs-evidence table.
15. **Two-level BO explanation** (theme 3): plain spoken sentence + visual in
    the main talk, machinery in backup slides; the misleading
    "qNEHVI over standard expected improvement" comparison replaced with
    "noise-aware vs. non-noise-aware" plus proper budget-matched baselines.
16. **Tensegrity mechanism visual** (theme 4): labeled specimen + deformation
    sequence in Point 3, so the structure isn't remembered as a generic crush
    structure or lattice.
17. **"Eliminates assembly entirely" hedged** (theme + P3): now "single-build
    co-fabrication / no joining of parts," with a note to list remaining
    manual steps and an automation-status caveat.
18. **Objective formulation made consistent** (theme 7): objectives = SEA +
    compaction efficiency, constraint = force cap, deliverable = *feasible*
    Pareto front; the "SEA vs. peak force" evidence bullet corrected.
19. **Closing made concrete** (theme 8 + P6): explicit deployment rule, the
    transfer claim marked conditional, and the close ends on the measured
    result before the bookend.

## Changes from Draft 1

Feedback from the PR #84 review, applied in Draft 2:

1. **Main message** re-centered on speed + real data ("robust" → the
   dozens-not-thousands claim); body and message now carry the same story.
2. **"Combining real and simulated data" removed** (Review section) — the
   manuscript's positioning (#75/#76) is that the physical experiment is the
   source of truth, explicitly avoiding calibrated FE simulation.
3. **"Generative design" → "parametric designs"** to match the manuscript's
   parametric design space and avoid an over-claim to a design-automation
   audience.
4. **Objectives made explicit** (Task, Point 2, Review): maximize specific
   energy absorption and compaction efficiency, cap peak transmitted force.
5. **Need sharpened into the two-sided pincer**: simulation can't be trusted
   *and* the space is too big to brute-force — which makes BO + AM the
   inevitable answer. *(Draft 3 re-scopes the first side of this pincer; see
   above.)*
6. **Point 1 given its own content** (the *why* behind the inefficiency)
   instead of restating the Need.
7. **Point 2 adapted to the DAC-10 audience**: skips BO advocacy, focuses on
   the specifics (noise-aware acquisition, small batches, multi-objective).
8. **Point 3 explicitly closes the "easy assembly" loop** from the Need
   (monolithic printing = no assembly). *(Draft 3 hedges the wording; see
   above.)*
9. **Evidence/results slot added** before the Closing, so the Conclusion is
   grounded in shown data rather than three hedged "may"s.
10. **Attention getter compressed** to 1–2 sentences of setup plus the Super
    Ball Bot visual; verified video links included.
11. **Close bookends the opening** (the next lander's absorber, designed in
    weeks) before the broader humankind line.
12. **Spelling**: Doumont (was "Duomont").
