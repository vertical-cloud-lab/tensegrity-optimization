# IDETC Presentation — Doumont Presentation Structure Template

Transcribed from Jean-luc Doumont's presentation-structure template
([TM&Th-3.2-template.pdf](https://principiae.be/pdfs/TM&Th-3.2-template.pdf)),
adapted from *Trees, maps, and theorems* (Principiae, 2009). © 2009 by Principiae.
All rights reserved. Can be downloaded from <https://www.treesmapsandtheorems.com>.

> To design your presentation, write down your ideas for each component below.
> If useful, you can then further develop your body afterwards (the "back of the sheet").

**Draft 2** — transcribed from @me-madsen's
[Presentation Outline Draft 1 (7-17-2026).pdf](https://github.com/user-attachments/files/30140592/Presentation.Outline.Draft.1.7-17-2026.pdf)
with the review feedback from PR #84 applied. A summary of what changed from
Draft 1 is at the [bottom of this file](#changes-from-draft-1).

## Opening

### Attention getter

*A way to lead the audience to the need efficiently*

Tensegrity provides robust solutions to issues posed by planetary landings —
and to problems closer to home.

One or two sentences of setup, then let the Super Ball Bot image (or a short
clip) do the work:

> Landing a payload on another planet means surviving an impact in conditions
> where parachutes and retrorockets struggle — thin atmospheres, rough
> terrain. NASA's Super Ball Bot concept answers this with a tensegrity
> structure: the lander *is* the energy absorber.

Candidate Super Ball Bot videos to show (verified links):

- [Super Ball Bot](https://www.youtube.com/watch?v=ZBSRdGlAh5s) — NASA Video
  (official channel); the canonical overview.
- [NASA Demonstrates Super Ball Bot Prototype](https://www.youtube.com/watch?v=L2cJej3EmcA)
  — Wall Street Journal; prototype drop footage.
- [HET2 SUPERball Bot Task NIAC Mission concept](https://www.youtube.com/watch?v=1wce-mB69mE)
  — NASA Video; mission-concept animation (Titan descent) — strong hook material.

<!-- Optional aside, kept for future-work tie-in only (per manuscript scope in
#75/#76): the tensegrity crutch tip from the paper Dr. Hill found. -->

### Need

*A difference between actual and desired situations*

**Actual situation** (a two-sided pincer):

- Simulation can't be trusted for these structures: FDM interfacial defects
  and TPU rate-dependence make calibrated finite-element models expensive and
  unreliable.
- The design space is too big to brute-force physically: even modest parameter
  resolutions yield thousands of candidates, each costing print and test time.
- Idealized cable–strut tensegrities are also difficult to assemble by hand.

**Desired situation:**

- Trustworthy performance data without hand assembly (easy creation of
  tensegrity structures).
- Quick iteration and testing — find good designs in dozens of experiments,
  not thousands.

### Task

*What I decided/was asked to do to address the need*

Build a closed-loop design–print–test workflow that optimizes a parametric
family of tensegrity-inspired energy absorbers directly from real, measured
impact data — maximizing energy absorbed per gram (specific energy
absorption) and compaction efficiency while capping the peak force
transmitted to the payload.

### Main message

*The one sentence I want my audience to remember*

By closing the loop between multi-material 3D printing and Bayesian
optimization, we can optimize tensegrity energy absorbers directly from real
impact data — in dozens of prints, not thousands.

### Preview

*A map of the body (ideally three points, max. five)*

1. Simulation-first design of printed tensegrity structures is unreliable, and
   physical trial-and-error is intractable — so the measured experiment must
   be the source of truth.
2. Bayesian optimization makes physical experimentation affordable: it handles
   noisy measurements, small batches, and the multi-objective trade-off
   between energy absorption and transmitted force.
3. Multi-material additive manufacturing closes the loop: monolithic
   PLA–TPU prints turn each proposed design into test data in hours, with no
   assembly.

## Body

### Point 1

Simulation-first design of printed tensegrity structures is unreliable, and
physical trial-and-error is intractable.

- Why current methods fall short (not just *that* they do): high-fidelity FE
  simulation struggles with FDM interfacial slip and TPU rate-dependence, so
  simulated objectives can't be trusted for these builds.
- The alternative — sweeping the design space physically — fails on cost:
  thousands of candidate designs, each needing print + test time.
- Therefore: treat the physical experiment as the source of truth, and be
  ruthless about *which* experiments to run.

### Transition

If every data point must be a real experiment, we need a method that extracts
the most from every specimen — we need to make the process radically more
sample-efficient.

### Point 2

Bayesian optimization makes physical experimentation affordable, even with
limited, noisy data.

- (DAC-10 audience already believes optimization works — spend the time on
  what's specific here, not BO 101.)
- Noisy physical measurements: TPU batch-to-batch variation and print defects
  motivate noise-aware acquisition (qNEHVI) over standard expected
  improvement.
- Small parallel batches: the surrogate proposes the next batch of specimens
  to print, balancing exploration and exploitation.
- Multi-objective by construction: maximize specific energy absorption and
  compaction efficiency subject to a peak transmitted-force bound — the
  Pareto front *is* the design deliverable.

### Transition

The optimizer is no longer the bottleneck — the limit is now providing real
data quickly enough.

### Point 3

Multi-material additive manufacturing supplies that data fast — and
eliminates assembly entirely.

- Monolithic PLA–TPU co-printing: rigid struts and flexible tension network
  in a single build — no hand assembly, which closes the "easy creation" gap
  from the Need.
- Rapid iteration: each BO-proposed candidate goes from parameter vector to
  tested specimen (quasi-static compression + instrumented drop-weight impact)
  in hours.
- Now we have the data we need to complete the loop.

### Evidence / results

*What we found — ground the conclusion in shown data*

<!-- Placeholder while the campaign is in progress. Candidates:
- Drop-test force–time traces (raw data the audience can see is real).
- Sobol / first-batch results (PR #35 / PR #67).
- Measured or expected Pareto front: SEA vs. peak transmitted force.
- Photos/video of printed specimens and impact testing.
-->

## Closing

### Review

*A recap of the body, leading into the conclusion*

Using real, measured impact data from additively manufactured
tensegrity-inspired structures — parametric designs proposed by a Bayesian
optimization routine — we rapidly iterate toward better energy absorbers.
This feedback loop makes tensegrity optimization dramatically faster: dozens
of prints instead of thousands of candidates.

### Conclusion

*What the above means to the audience in the end*

Because the loop runs on physical measurements, it works precisely where
simulation fails — and the same closed-loop pattern transfers to any
additively manufactured architecture whose performance is dominated by
hard-to-simulate effects. Faster, trustworthy optimization of tensegrity
structures brings them within reach for payload protection on other planets
and for safety hardware here on Earth (e.g., the crutch tip, as future work).

### Close

*A way to end the presentation clearly and elegantly*

Return to the opening image: the next planetary lander's energy absorber
doesn't have to take years of hand-built prototypes — with this loop, it can
be designed, printed, and proven against real impacts in weeks. What limits
our ventures is rarely whether we can do them, but how quickly — and every
method that compresses that time moves humankind forward.

---

## Changes from Draft 1

Feedback from the PR #84 review, applied above:

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
   inevitable answer.
6. **Point 1 given its own content** (the *why* behind the inefficiency)
   instead of restating the Need.
7. **Point 2 adapted to the DAC-10 audience**: skips BO advocacy, focuses on
   the specifics (noise-aware acquisition, small batches, multi-objective).
8. **Point 3 explicitly closes the "easy assembly" loop** from the Need
   (monolithic printing = no assembly).
9. **Evidence/results slot added** before the Closing, so the Conclusion is
   grounded in shown data rather than three hedged "may"s.
10. **Attention getter compressed** to 1–2 sentences of setup plus the Super
    Ball Bot visual; verified video links included.
11. **Close bookends the opening** (the next lander's absorber, designed in
    weeks) before the broader humankind line.
12. **Spelling**: Doumont (was "Duomont").
