# Edison trajectory -- mechfig-feedback

Task ID: `e0c4e062-15c7-4a62-b931-1746211fe8b1`  
Status: success

---

Top line: the figure is close to being a useful JMD mechanism figure, but right now it proves the performance contrast more clearly than it proves the mechanism. The strongest next move is to add one quantity that enforces mechanics consistency and one image sequence that shows the claimed load path at the same times marked on the curve.

1. Make the curve panel carry a stricter mechanics argument

Priority 1
- Replace the generic phase labels with event-based labels tied to observable kinematics. Right now A/B/C are plausible, but a reviewer can still say “that’s an interpretation pasted on top of a curve.” Rename them to things you can verify from video or DIC, for example:
  - A: first contact / cable engagement
  - B1: strut rotation + cable tension redistribution
  - B2: peak compression / force spreading plateau
  - C: rebound / unloading
- Add 2-4 registration markers directly on panel (a). Use small numbered or lettered dots on the blue curve at specific times, then show the matching frame labels in panels (b)-(d) or a frame strip. This turns the figure from a schematic story into evidence.
- State the measured variable more precisely. If this is carriage, impactor, or transmitted base acceleration, say so in the y-axis or caption. A mechanics reviewer will want the load path from specimen deformation to the measured sensor channel to be explicit.

What is missing for the load-path argument
- Evidence that the plateau corresponds to internal load redistribution rather than just a softer global response.
- Evidence that the cable network is actually engaging when the curve flattens.
- Evidence that the strut-end joint geometry is the specific reason load is spread in time.

To make that convincing, you need one of these links:
- measured or inferred force/impulse consistency plus synchronized images, or
- synchronized deformation/tension metrics showing cable engagement and strut compression during phase B.

2. Highest-value additions: pick these 2 first

Priority 2
- Add transmitted force or impulse-consistent quantity.
  - Best option: transmitted force vs time if you have instrumented force data or can derive it cleanly from measured acceleration and known effective mass.
  - If not, add cumulative impulse, J(t)=∫F dt, or equivalently mass-normalized velocity change from acceleration.
  - Why this is high value: it checks conservation-level consistency. For the same impact, the tensegrity should lower the peak mainly by spreading impulse over time, not by inventing or destroying impulse.
  - What to show: small subpanel below (a), same x-axis, with cumulative impulse for control and tensegrity. If the mechanism is “same event, lower peak, longer duration,” this panel makes that visible fast.
- Add synchronized phase-resolved high-speed frames with one quantitative overlay.
  - Best option: 3 frames at the curve markers: contact, mid-plateau, rebound.
  - Overlay either cable stretch, strut shortening, or 2-3 tracked distances/angles.
  - Why this is high value: it converts the mechanism claim from cartoon to observation.

If you can only add one more quantity beyond the frames, choose:
- DIC-based axial strut shortening / node displacement vs time, aligned to the acceleration trace.
That is better than a generic SEA panel for this specific figure because it directly supports the mechanism.

Lower-priority additions
- Force-displacement hysteresis: very useful, but better as a separate mechanics figure than a crowded add-on here.
- Specific energy absorption: important for the paper, but not the best single addition for this mechanistic figure.
- Cable tension vs strut compression: excellent if you actually have it, but many reviewers will accept tracked strain/displacement as a proxy if direct cable tension is unavailable.

3. Registration best practice

Priority 3
- Use explicit curve-to-image registration markers. Recommended format:
  - Put 3 small filled markers on the blue curve labeled 1, 2, 3.
  - Put the same labels on the corresponding frames.
  - Include timestamps on both, e.g. 4.6 ms, 6.8 ms, 11.2 ms.
- Use leader lines sparingly. One thin gray leader from each curve marker to its frame is enough. Avoid arrows crossing the whole figure.
- Keep the frames in chronological order left-to-right or top-to-bottom. Don’t make the reader decode the sequence.
- If using specimen photos instead of frames, crop tightly and keep the same view, scale, and orientation across frames.
- Add one persistent visual fiducial in every frame:
  - tracked node markers,
  - a circled joint,
  - or a colored overlay on the cable segment believed to engage.
- If space is tight, use a frame strip under panel (a) instead of separate right-side panels. That often reads cleaner for time registration.

4. Rigor and honesty

Priority 4
- Keep the watermark for the mock-up. Also put “synthetic illustrative curves” in the panel title or caption, not just as a watermark.
- In the real figure, report:
  - n for each condition
  - whether the trace shown is a representative replicate, mean, or median
  - spread metric: SD, SEM, or preferably a shaded mean ± SD or 95% CI band if replicates are aligned well
  - coefficient of variation for peak acceleration and impact duration if replicate count is small
- Filtering disclosure should be explicit in caption, not only in legend:
  - raw acquisition rate: 125 kHz
  - filter standard: SAE J211
  - channel class: CFC-180
  - whether zero-phase filtering was used
  - how impact time zero was defined
- If traces were time-aligned, say exactly how. Peak alignment, trigger alignment, and first-contact alignment are not equivalent.
- If panels (b)-(d) are photos or frames from one replicate while panel (a) is an average across replicates, say that clearly.

What a JMD reviewer will expect
- Enough metadata to know the signal processing was standard and not cherry-picked.
- Enough replicate information to know the dramatic reduction is robust.
- Enough registration clarity to know the photos correspond to the same event timing shown on the curve.

5. Layout, axes, color, accessibility

Priority 5
- The current composition is readable, but the right side is underused and panel (a) is doing too much. Simplify panel (a) and make the evidence frames work harder.
- Move the phase key out of the data area. Put it in the caption or as a compact strip above the axis.
- Move the legend outside the plot or replace with direct line labels near the traces. Direct labeling is better here.
- Change the y-axis label from “Deceleration (G)” to the exact measured quantity and location if possible.
- Consider a colorblind-safer pair than red/blue if these colors also encode material roles elsewhere. A good option is dark gray for rigid control and blue-green for tensegrity, while keeping red/blue only inside specimen schematics if needed.
- The pastel phase shading is fine but should be lighter. Right now it competes with the data and watermark.
- Increase the visual prominence of registration markers relative to the phase shading.
- For single-column ASME width, this 4-panel layout is likely too dense unless the side panels are simplified. For single-column:
  - use panel (a) plus a 3-frame strip beneath it.
- For double-column:
  - current multi-panel concept works, but tighten whitespace and align the right-column panel widths.
- Font sizes look acceptable for a draft, but final target should survive reduction to journal width. Check that all labels remain legible at final printed size, especially panel (c) annotations.

6. Physics red flags in the synthetic curves

Priority 1 physics fix
- The biggest red flag is impulse inconsistency.
  - I checked the synthetic generators in the provided script.
  - The control trace integrates to about 8.92 m/s mass-normalized velocity change.
  - The tensegrity trace integrates to about 23.85 m/s.
  - That is 2.68× larger for the tensegrity case.
  - For the same drop event, that is not credible unless the measurement definitions differ drastically. A reviewer with impact mechanics intuition may spot that the low broad plateau is carrying too much total area.
- The tensegrity curve should reduce peak by spreading the event in time, but the area under the physically relevant force/acceleration history should stay broadly consistent with the same incoming momentum, modulo rebound and fixture effects.

Other red flags
- The tensegrity curve peaks too early relative to the claimed mechanism. If phase A is “cable pre-tension/contact,” the tensegrity should usually show a slower rise before the plateau, not essentially an immediate full-amplitude response.
- The tensegrity rebound is drawn as a positive bump. A true rebound/unloading feature often shows sign reversal or at least a clear unloading trend depending on the sensor definition.
- The control has a negative lobe around -101 G, while the tensegrity never goes negative. That asymmetry may look suspicious if both traces come from the same measurement definition.
- The control duration above 10% of peak is about 0.84 ms in the synthetic script, while the tensegrity stays above 10% of peak for about 10.89 ms. That contrast may be too extreme unless your real event truly has that long a tail.
- The plotted “phase B plateau” is not very plateau-like mathematically; it is more a broad decaying hump. If you want the visual to support redistribution, shape it as a delayed rise followed by a flatter shoulder, not a centered Gaussian.

Concrete tuning suggestions for the mock-up before substituting real data
- Reduce the total area under the tensegrity curve substantially or widen the control response if you are trying to preserve equal-impact impulse.
- Introduce a delayed rise and a flatter top for the tensegrity trace.
- Add a believable unloading/rebound sign change if the sensor channel should show one.
- Make phase boundaries follow kinematic events, not convenient time blocks.

Prioritized revision list you can implement directly

- 1) Add 3 synchronized curve markers and matching high-speed frames at those exact times.
- 2) Add a small transmitted-force or cumulative-impulse subpanel sharing the x-axis with panel (a).
- 3) Replace generic A/B/C labels with event names verified from images or DIC.
- 4) State exactly what acceleration is measured and where the sensor is located.
- 5) Report n, whether traces are representative or averaged, and show uncertainty bands or replicate spread in the real figure.
- 6) Put filtering details in the caption: 125 kHz raw, SAE J211, CFC-180, alignment method, and any zero-phase implementation.
- 7) Move the legend and phase key out of the data field; use direct line labels if possible.
- 8) Simplify the right-side panels into either a clean frame strip or larger photo insets with matching labels.
- 9) Tune the synthetic tensegrity curve so its impulse and rebound behavior look mechanically consistent.
- 10) Lighten phase shading and reduce watermark interference so the data and markers are the first thing the eye sees.

What an ideal version of this figure looks like

A strong final JMD figure has one main time-history panel showing rigid vs tensegrity response with 3 clearly marked event times, one compact lower panel showing force or cumulative impulse to prove the peak was reduced by temporal redistribution rather than by inconsistent loading, and 3 synchronized high-speed/DIC frames showing contact, plateau, and rebound with one tracked geometric metric overlaid. The caption states the measurement location, filtering, sampling rate, alignment method, and replicate basis. A reviewer should be able to look at it and say: yes, the tensegrity specimen engages a different internal load path, that engagement occurs exactly where the plateau appears, and the lower peak is mechanically consistent with the same impact event.

- Discretionary analytical decisions made during the analysis
- Reviewed the attached generator script and README, rather than relying on the rendered figure alone, to assess whether the synthetic signal shapes were mechanically self-consistent.
- Used impulse consistency via numerical integration of the synthetic acceleration histories as the primary physics sanity check, because that is the highest-value check for a peak-spreading impact claim.
- Treated the requested feedback as a design-review task rather than a formal statistical analysis task, since the attached figure uses synthetic illustrative data and no replicate dataset was provided.
- Prioritized transmitted force/cumulative impulse and synchronized kinematic frames as the top two additions, over SEA or hysteresis, because they most directly test the claimed load-redistribution mechanism in this figure.
- Recommended direct line labeling and externalized legends/phase keys to reduce data-field clutter, which is a valid layout choice rather than a required correction.
