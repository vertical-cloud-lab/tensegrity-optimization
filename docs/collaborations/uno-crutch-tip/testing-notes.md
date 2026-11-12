# Walking-stick tip collaboration with Dr. Dotov's lab: testing methods and ideas

**Brigham Young University (BYU):** Vertical Cloud Lab (Dr. Sterling Baird) and Smash Lab (Dr. Jeff Hill), Department of Mechanical Engineering

**University of Nebraska Omaha (UNO):** Dr. Dobromir Dotov's lab (Dr. Dotov and Jingxian Gu)

Notes on how the walking-stick tips will be tested, and on the testing ideas raised in the video meeting of November 6, 2026, with most of the detail on Dr. Dotov's. Owners and deadlines are in the companion document, [action-items.md](action-items.md). Discussion is tracked in [issue #135](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/135).

Times in parentheses, such as (18:28), point to the meeting transcript. The transcript labels speakers by device, not by person, so who said what comes from context (see [About the sources](#about-the-sources)). Three kinds of material did not come from the meeting, and are labeled where they appear: how UNO ran its earlier crutch study, from its preprint ([Gu et al., 2026](https://arxiv.org/abs/2605.02710)); background on the measures, with references; and suggestions for BYU's bench tests.

## Summary

- **UNO will judge the tips with people walking**, comparing tips of different stiffness on different terrain. Dr. Dotov named three levels of measurement (18:28 to 20:44): how stable participants say they feel (a questionnaire), how fast they choose to walk (measured with motion capture, which tracks markers on the body), and how stable their body motion is (upper-body sway, and the Lyapunov exponent, which measures how fast small disturbances to the walking motion grow). Jingxian Gu suggested adding a load cell, a force sensor, in the handle (20:44). That is optional and not decided.
- **Dr. Dotov's hypothesis:** a stiff tip suits flat, predictable ground, and a softer tip suits slippery or uneven ground, in the way people make their ankles more compliant on slippery ground (2:46 to 5:08).
- **Dr. Dotov's untested idea about slip:** a tip with several contact points that share the load evenly should slip less, because slip starts at whichever contact passes its friction limit first (11:54 to 13:07).
- **BYU's part before the trials** is bench testing: print one high-stiffness and one low-stiffness tip and test them at whatever loads BYU can reach (15:23, 24:56).
- **Not settled:** how much bending stiffness a tip needs (31:28), what loads BYU's bench tests should reach (10:05), and what counts as success when walking speed and stability disagree. See [Open questions about testing](#open-questions-about-testing).

## Dr. Dotov's testing methods and ideas

### The hypothesis: match the tip's stiffness to the terrain (2:46 to 5:08)

Dr. Dotov based the hypothesis on how people adjust their legs to the ground they walk on:

- On **flat, predictable ground**, a stiffer support is better. It is easier to use, probably returns more energy, and may allow faster walking.
- On **slippery ground, or ground with small obstacles** that the device has to absorb, a softer support is better.
- People on risky ground become "differentially stiff": they stiffen some muscles and relax others. As Dr. Dotov recalled it, they lower the stiffness of the ankle, so the foot conforms to the ground, and raise it at the hip, so the trunk responds more quickly. UNO's preprint cites [Whitmore et al. (2016)](https://doi.org/10.1109/TBME.2015.2497659) for a similar pattern on slippery walkways (a more compliant ankle, stiffer joints higher up the leg), and points to it in explaining why UNO put the compliance at the bottom of its crutch, where the tip plays the part of the ankle.

Applied to the first round of passive tips ([decision 3 in action-items.md](action-items.md#decisions)), the hypothesis predicts:

| | High-stiffness tip | Low-stiffness tip |
| --- | --- | --- |
| **Flat, predictable ground** | Better: easier to use, more energy returned, maybe faster | Worse |
| **Slippery or uneven ground** | Worse | Better: absorbs small irregularities. Slower walking, but more secure and more stable |

The larger study comes later, once a tip's stiffness can be adjusted: put participants on changing terrain and see whether they learn to use the adjustment, choosing a stiff setting on flat ground and a soft one on slippery or rugged ground. On that ground, with the soft setting, Dr. Dotov expects them to walk more slowly but to feel more secure and be more stable. He called this "a bigger study" (5:08). The adjustment can be manual, such as a knob the user turns after lifting the stick, and it only needs to change "when needed", not on every step (1:00, 5:32 to 5:52).

### How the trials will be set up

The second column is from the meeting. The third, for comparison, is how UNO ran its crutch study, from the preprint. A force plate, mentioned there, is a floor panel that measures the force applied to it.

| | Walking-stick study (November 6 meeting) | UNO's crutch study (preprint) |
| --- | --- | --- |
| **Participants** | Young, healthy adults, because they are quick to recruit (22:14-23:21) | 18 young, healthy adults. A knee brace held one leg off the ground to simulate an injury. |
| **Device** | Hiking-style walking stick with a screw-off tip. "Cane" in the meeting meant walking stick (29:44, 31:04). | Forearm crutches: rigid, spring-loaded, and tensegrity, weighted to match |
| **Conditions** | Several terrains crossed with several tips, compared condition by condition (18:28-19:09) | Every participant used all three crutches, in random-order blocks, walking straight and around a 90-degree turn at a speed they chose |
| **Terrain** | Flat and predictable; slippery; small obstacles such as a stone, or pavement with a slight slope (2:46, 11:09). Dr. Dotov said UNO's department "can do more interesting terrains" (17:44). | Flat lab floor over force plates. The preprint names uneven, unpredictable terrain as the test still to do. |
| **Tips** | One high and one low stiffness first. Adjustable stiffness later (14:50-15:59). | One tensegrity module, compared with two commercial crutches |
| **Who runs it, and where** | Jingxian Gu is too busy to run every study. A student of "the other Jeff", a psychology collaborator in Illinois, could run it, at UNO or in Illinois (16:47-18:02). | UNO |
| **When** | Spring 2027, with analysis in summer 2027, if the design is finished by December 31, 2026 (36:39) | Preprint submitted May 4, 2026 |

### Three levels of measurement (18:28 to 20:44)

BYU asked how UNO would measure success for a tip, since how well a tip grips the ground seemed hard to put a number on (18:02). Dr. Dotov answered with three levels, from the quickest to the most theoretical. The last column is from the preprint.

| Level | What it measures | How | In UNO's crutch study |
| --- | --- | --- | --- |
| **1. Questionnaire** | How stable participants feel. Dr. Dotov called this "the very quick first level". | Ratings after each condition | After each block of trials: perceived stability (-3 to 3), effort (Borg scale, 0-10), comfort (-3 to 3), pain (0-10), and the System Usability Scale (0-100) |
| **2. Walking speed** | How fast participants "allow themselves to go" on each combination of terrain and tip. UNO looks for the condition in which they walk fastest. | Motion capture | Speed from a marker on the back, tracked by 12 infrared cameras at 100 frames per second |
| **3. Stability of body motion** | Upper-body sway, side-to-side (mediolateral) sway, and the Lyapunov exponent of a point near the body's center of mass | Motion capture | Not reported yet. The preprint says the rest of the movement data will be reported separately. |

- **Motion capture** uses cameras to track reflective markers stuck on the body, which records its movement in three dimensions. The crutch study used 45 markers.
- **Sway** is the back-and-forth movement of the upper body while walking. Mediolateral sway is the side-to-side part of it.
- **The Borg scale** rates perceived effort from 0 (rest) to 10 (extremely hard). **The System Usability Scale** is a standard 10-item questionnaire scored from 0 to 100.

Dr. Dotov's caveat on level 3: "we always fight whether the mechanical stability of the body is actually the functional stability" (19:20). Level 3 rests on theory that is still argued over.

#### The Lyapunov exponent

Dr. Dotov described it as "applied math" that measures "how quickly a dynamic system diverges from its attractor" (19:20 to 20:42). Take a point close to the body's center of mass. While a person walks, it goes "left, right, left, right, a little like an 8", tracing nearly the same loop every stride. That repeated loop is the attractor. The question is whether the point stays on its loop or tends to drift away from it.

The standard definition is the rate at which two nearly identical states of the motion grow apart:

```math
d(t) \approx d_0 e^{\lambda t}
```

This is the exponential divergence of nearby states. Pick two moments in a recording of steady walking when the body's motion was almost the same: a small distance $d_0$ apart in state space, the space of positions and velocities together. After a time $t$ they are a distance $d(t)$ apart. The rate $\lambda$ is the Lyapunov exponent, in units of 1/time. A larger $\lambda$ means small disturbances grow faster, which is read as less stable walking.

Gait studies commonly estimate $\lambda$ from a measured signal, such as the velocity of a marker on the trunk, with the method of [Rosenstein et al. (1993)](https://doi.org/10.1016/0167-2789%2893%2990009-P). [Dingwell and Cusumano (2000)](https://doi.org/10.1063/1.1324008) applied it to human walking, and [Bruijn et al. (2013)](https://doi.org/10.1098/rsif.2012.0999) review it alongside other stability measures. The estimate needs long stretches of continuous walking, which bears on how long each terrain course has to be.

### Several contact points, and slip (11:09 to 13:07)

Dr. Dotov said that for a walking stick, the useful kind of stability is conforming to small irregularities, such as a stone or pavement with a slight slope (11:09). BYU added that a tensegrity tip could touch the ground at several points, so that if one misses, the others can still land (11:26).

Dr. Dotov's idea, which he said he has not tested (11:54): a tip whose contacts share the load evenly should slip less. He compared it to cars, which are designed to keep all four wheels on the ground with the load balanced between them, because that helps when turning and on slippery roads. His reasoning about slip (12:42 to 13:07) rests on the static friction limit at each contact:

```math
\lvert F_{t,i} \rvert \le \mu_s N_i
```

Contact $i$ holds while the sideways force on it, $F_{t,i}$, stays below the static friction coefficient $\mu_s$ times the normal force pressing it into the ground, $N_i$. Slip starts as soon as any one contact passes this limit. Once that contact slides, its friction drops to the lower sliding (kinetic) value, so the other contacts have to carry more of the sideways force, and they tend to slip as well. Keeping $N_i$ even across the contacts keeps each of them below its limit for longer.

UNO's preprint makes the same case. People UNO consulted while designing the crutch suggested several contact points for stability, and the four struts of the module's lower cell touch the ground separately and move independently. The authors expect the benefit to show "when balance is challenged, such as when walking on uneven and unpredictable terrain", which the crutch study did not test.

### Testing UNO's crutch module to failure (7:04 to 8:02)

UNO's crutch module is pre-stressed: its cables are tensioned during assembly, so it carries internal forces, above 1000 N, before any load is applied (7:04). When UNO loaded it to failure, the technician running the test put up a plexiglass shield and handed out helmets, because nobody knew what the module would throw into the air when it snapped (7:22). A walking-stick tip is less demanding, which allows faster prototyping (7:22 to 8:02).

The preprint reports those tests, run in axial compression on a universal testing machine (a load frame that records force and displacement):

| Quantity | Value |
| --- | --- |
| Failure load of a single cable with end loops | 1500-2000 N |
| Failure load of the whole two-cell module | 2000-4500 N, limited mainly by the cable loops and the 3D-printed joint pieces |
| Stiffness of the module | Rises with load: 16.3 kN/m at small loads, 121.3 kN/m at about 1000 N |
| Stiffness of a commercial spring-loaded crutch, for comparison | Constant 10.8 kN/m until about 3.5 cm of travel, where it bottoms out on its rubber tip |

These are crutch numbers at body-weight loads, not targets for a walking-stick tip. The preprint suggests that the rising stiffness and short travel helped the tensegrity crutch smooth the forces without the drawbacks of the spring-loaded crutch, which several participants found "bouncy" and which slowed them down.

## Jingxian Gu's ideas

Dr. Dotov noted that Jingxian Gu is an occupational therapist and thinks about what people who need mobility aids actually require (25:48).

- **A load cell in the handle (20:44 to 21:10).** Dr. Dotov passed this on as "Jing's suggestion": measure the force going into the hand. It is optional and not decided. BYU noted that the load depends on who uses the stick: a hiker probably leans on it a lot less than someone with balance problems who uses a cane to stand up, and a cane that carries more load would need a stiffer tip (21:14 to 22:14).
  - *Not from the meeting:* the crutch study measured crutch forces with force plates set into the floor, sampled 1000 times per second. A load cell in the stick would measure force on any terrain, including terrain that is not over a force plate. Its readings would also give BYU real walking loads to design and bench-test against, which BYU said it would need after the first round (24:56).
- **Bending stiffness (31:28 to 32:23).** Someone on the UNO side, probably Jingxian Gu, asked whether a tensegrity can only take vertical force. The reply, also from the UNO side, was that it does bend, but that nobody there has measured whether its bending stiffness is a useful amount. BYU said bending stiffness can be designed in, and that BYU is trying to make a tensegrity "elephant trunk" that can really move around (31:56).
- **A stick that shortens during the swing phase (32:23 to 35:28).** The swing phase is the part of each step when the stick is off the ground and moving forward. A stick or crutch that stays full length during swing makes the user lift the arm and shoulder to clear the ground, which costs energy. Dr. Dotov said this applies to any assistive device, and that pulling a cable could do it, but that it sounds very complicated (33:15). It was set aside for later.

## BYU's testing ideas from the meeting

- **BYU's current tests measure something else.** BYU's drop-tower tests apply a shock along one axis and measure how much a structure reduces it (10:05 to 11:07). BYU asked whether the tip should reduce shock, reduce vibration, or improve stability. Dr. Dotov answered stability (11:09).
- **Recorded data from real use.** BYU asked which recorded data would help it design tips with adjustable stiffness, for example acceleration (10:05). This was not answered.
- **Start with two stiffnesses.** Print one high-stiffness and one low-stiffness tip. If the trials show a difference, work out what stiffness is actually needed (15:23 to 15:59). Thermoplastic polyurethane (TPU), the flexible filament BYU prints tendons with, may be too soft (15:23).
- **Bench-test at the loads BYU can reach.** The first printed tips will probably not be load-bearing, meaning able to carry a person's full weight, but testing them under whatever load BYU can apply should show how much stiffness change is needed and which geometry gives stable contact. Recorded data from real use, and design for full loads, come after that (24:56 to 25:48).

## Testing requirements carried over from August 3, 2026

These were not discussed on November 6. Source: [Marcus Madsen's notes on PR #41](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/41#issuecomment-5171640386).

- UNO doubted that 3D-printed structures could be stiff enough, or could survive the repeated loading a crutch tip sees in regular use. That is why UNO proposed starting with walking-stick tips.
- A tip should not break after about three months of use.
- It should allow some movement, but not much, and not only along one axis the way a spring does.
- It should be light.

## Open questions about testing

Suggested for the next meeting. None of these were settled on November 6.

| Question | Why it matters | Transcript |
| --- | --- | --- |
| What counts as success when walking speed and stability disagree? | The hypothesis predicts slower but more stable walking with a soft tip on rough ground, while level 2 counts faster walking as better. | 2:46-5:08, 18:28-19:09 |
| Does every participant use every tip on every terrain, and in what order? | It sets how many tips BYU supplies and how many trials each must survive. In the crutch study, every participant used every crutch, in random order. | 18:28 |
| Which terrains, and how long is each course? | The Lyapunov exponent (level 3) needs long stretches of continuous walking. | 17:44, 19:20 |
| Will the handle have a load cell, and who supplies and mounts it? | If it does, it also gives BYU real walking loads to design against. | 20:44, 24:56 |
| What loads should BYU's bench tests reach? | BYU asked for recorded data and did not get an answer. | 10:05, 24:56 |
| How much bending stiffness should a tip have? | Neither group has measured it. | 31:28-32:23 |
| Should participants know which tip they are using? Not raised in the meeting. | Level 1 is self-reported, so knowing which tip is the soft one could color the rating. Tips that look alike would avoid this. | None |

## Possible bench tests at BYU

These are suggestions. They were not discussed in the meeting, and each one is tied to something that was. BYU's test frames are listed on [PR #50](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/50), and the drop tower is described on [PR #28](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/28) and [PR #86](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/86).

| Meeting point | Possible bench test | Transcript |
| --- | --- | --- |
| High versus low stiffness ([item B2](action-items.md#action-items)) | Compress each tip slowly and record the whole force-displacement curve, not a single stiffness number. UNO's preprint points to the shape of that curve (stiffness rising with load, short travel) as a likely reason its tensegrity crutch did better than the spring-loaded one. | 15:23 |
| Conforming to uneven ground | Compress the tip onto a plate with a step or a pebble under one contact, and compare with the flat-plate curve. UNO simulated the same case for its module: a 500 N load with two of the bottom contacts raised. Its modeling used [TsgFEM](https://doi.org/10.21105/joss.03390), a finite element toolbox for tensegrities. | 11:09 |
| Dr. Dotov's load-sharing idea | Load the tip at an angle on a smooth or wet surface and find the angle or side load at which it starts to slip. Compare a tip with several contacts against a plain rubber tip. | 11:54-13:07 |
| Bending | A walking stick meets the ground at an angle, so apply an angled or side load and measure the stiffness across the stick as well as along it. | 31:28 |
| Durability (August 3) | Cyclic compression at walking loads for many cycles, tracking how the stiffness drifts and when the tip fails. | August 3 notes |
| Shock (BYU's current tests) | Force over time on the drop tower (drop mass times measured deceleration) gives a loading rate, meaning how fast the force rises right after contact. Peak loading rate was the main force measure UNO's crutch study used to compare crutches. | 10:05 |
| Testing to failure | Use a shield, as UNO's technician did. A pre-stressed printed tip stores energy too. | 7:22 |

## About the sources

- **The meeting transcript:** the Microsoft Teams auto-transcript of the November 6, 2026 meeting (37 min 35 s), attached to [this comment on issue #135](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/135#issuecomment-6830092359). Every BYU voice appears as "Jinkwan Han" and every UNO voice as "Dobromir Dotov", so who said what comes from context. "Jing's suggestion" (20:44) identifies the load cell idea as Jingxian Gu's. The bending and swing-phase questions are attributed to her by their phrasing, which is less certain. Recording started partway into the meeting, so any testing ideas raised before that point are missing. [action-items.md](action-items.md#about-the-source) describes these limits in more detail.
- **UNO's crutch preprint:** the crutch study details above come from its Materials and Methods, Results, and Discussion sections ([Gu et al., 2026](https://arxiv.org/abs/2605.02710)).
- **The August 3, 2026 notes:** [PR #41](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/41#issuecomment-5171640386).

## References

- J. Gu, J. Spyra, A. Walski, L. Elsaesser, S. Bierner, D. Dotov, "Tensegrity crutches with compliance from a pre-stressed self-tensile module improve ground reaction force profiles, speed, effort, comfort, and perceived stability", preprint, [arXiv:2605.02710](https://arxiv.org/abs/2605.02710) (2026).
- M. W. Whitmore, L. J. Hargrove, E. J. Perreault, "Gait characteristics when walking on different slippery walkways", IEEE Transactions on Biomedical Engineering 63(1), 228-239 (2016), [doi:10.1109/TBME.2015.2497659](https://doi.org/10.1109/TBME.2015.2497659).
- M. T. Rosenstein, J. J. Collins, C. J. De Luca, "A practical method for calculating largest Lyapunov exponents from small data sets", Physica D 65(1-2), 117-134 (1993), [doi:10.1016/0167-2789(93)90009-P](https://doi.org/10.1016/0167-2789%2893%2990009-P).
- J. B. Dingwell, J. P. Cusumano, "Nonlinear time series analysis of normal and pathological human walking", Chaos 10(4), 848-863 (2000), [doi:10.1063/1.1324008](https://doi.org/10.1063/1.1324008).
- S. M. Bruijn, O. G. Meijer, P. J. Beek, J. H. van Dieën, "Assessing the stability of human locomotion: a review of current measures", Journal of the Royal Society Interface 10(83), 20120999 (2013), [doi:10.1098/rsif.2012.0999](https://doi.org/10.1098/rsif.2012.0999).
- S. Ma, M. Chen, R. E. Skelton, "TsgFEM: Tensegrity Finite Element Method", Journal of Open Source Software 7(75), 3390 (2022), [doi:10.21105/joss.03390](https://doi.org/10.21105/joss.03390).
