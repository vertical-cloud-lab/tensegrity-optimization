Question: We are optimizing small 3D-printed tensegrity structures (T3 prisms, printed
mass 18 to 23 g) for impact energy absorption using a drop tower. The
instrumented plate carrying the specimen falls h = 60 in (1.524 m) and arrests
on a polyurethane mat stack, producing a ~300 G, ~1.6 ms half-sine base pulse
with velocity change dv = integral of base acceleration ~ 5.4 m/s (free-fall
speed). The specimen rides the plate, responds elastically, rings down at
f_n ~ 300-550 Hz with damping ratio zeta ~ 6-11 percent, and its top vertex
separates from its seat and lands back t_second = 17-55 ms later (detected as
an envelope burst in the accelerometer record).

From this we define, per drop:

1. e_rebound = v_sep / dv = g * t_second / (2 * dv), where v_sep = g*t_second/2
   is the ballistic separation velocity inferred from the flight time (the
   time-between-bounces method of Bernstein, Am. J. Phys. 45:41, 1977).
   Measured values: e_rebound = 0.02 to 0.05 across our batch. We interpret it
   as a kinematic coefficient-of-restitution-like quantity for the top-vertex/
   seat interaction.

2. A Bayesian-optimization objective named "rebound energy":
   e_reb_mJ = e_rebound * m_printed * g * h, in millijoules (6 to 14 mJ across
   the batch), described in our code as "absolute rebound energy returned to
   the payload per drop", with a docstring sentence claiming "the raw
   e_rebound is a fraction of the impact energy". It is minimized together
   with a transmitted-shock ratio objective. Its measurement noise model is
   SEM_rel = hypot(e_sem/e_mean, mass_sd/m).

Questions to audit, in order of importance:

A. Physics check: is e_reb_mJ = e * m * g * h a defensible quantity to call
   "rebound energy"? Standard impact mechanics (Stronge) says the kinetic
   energy returned by a contact with kinematic restitution e is
   KE = e^2 * (1/2 m v^2) = e^2 * m * g * h, which for our numbers is
   ~0.1-0.7 mJ (microjoule scale), a factor 1/e ~ 20-50 smaller than the
   published e*m*g*h values. Is there ANY standard framework (packaging,
   cushioning, rebound resilience, sports-equipment COR testing, seismic
   pounding, robotics) in which a first-power-of-e times impact-energy
   quantity has an accepted name or use? Or is e*m*g*h only defensible as an
   ad hoc scalarization (a velocity-weighted index)?

B. What could e_rebound itself actually be measuring in our setup? The body
   that flies is the top vertex of the tensegrity (plus a 0.8 g accelerometer
   and its printed seat and cable tail), not the whole printed mass, and the
   "seat" is a printed key-seat joint. Candidate physical interpretations:
   (i) a genuine restitution coefficient of the vertex-seat contact;
   (ii) a measure of how much post-pulse vibrational/elastic energy the
   structure channels into vertex separation (structure property);
   (iii) a fixture/interface property (seating, wax mount) rather than a
   design property. What experiments distinguish these (we have a
   restrained-vs-unrestrained check scheduled)? Are there literature
   precedents for using secondary-impact timing of a substructure as a
   dissipation metric?

C. Consequences if the naming/physics is wrong: (1) does using e vs e^2 change
   a Pareto-front minimization's ranking in general (we verified it does not
   for our current batch, where the e spread of 2.5x dwarfs the mass spread of
   1.2x, but want the general statement)? (2) The uncertainty model: under
   e^2*m*g*h the delta method gives SEM_rel = hypot(2*e_sem/e, mass_sd/m); is
   that correct? (3) Are there downstream dangers of an objective whose name
   over-claims (e.g., reporting "mJ returned to payload" in papers or to
   stakeholders when the true returned KE is ~40x smaller)?

D. Literature: please identify the most relevant published work for
   (i) coefficient of restitution measured from bounce/flight timing;
   (ii) rebound-based energy metrics in materials testing, e.g. rubber rebound
   resilience (ISO 4662, ASTM D2632 vertical rebound, Bashore/Schob pendulum,
   Leeb hardness), where resilience = h_return/h_drop = e^2, and whether any
   standard uses first-power e as an energy fraction;
   (iii) tensegrity or lattice/metamaterial impact testing where rebound or
   restitution was an optimization or characterization objective (e.g.
   Pajunen, Johanns, Pal, Rimoli, Daraio, Materials & Design 182:107966,
   2019; Rimoli AIAA 2016-1511 tensegrity planetary landers; SUPERball);
   (iv) drop-test/cushioning standards language for what may legitimately be
   called rebound energy (ASTM D1596, D3332, MIL-STD-810, Lalanne).

Please give a clear verdict per question, with citations, and state
explicitly if any claim above is wrong or unsupported.

# Technical audit of the rebound objectives

## Executive verdict

1. **`e_reb_mJ = e_rebound m_printed g h` is not a defensible physical estimate of “absolute rebound energy returned to the payload.”** It is dimensionally an energy, but mechanically it is an **impact-energy scale weighted by a velocity ratio**. No standard framework located in impact mechanics, rebound resilience, sports testing, hardness testing, cushioning, robotics, seismic impact, or tensegrity testing treats first-power kinematic restitution, `e`, as a returned-energy fraction.

2. **The code statement that “raw `e_rebound` is a fraction of the impact energy” is wrong.** A Newtonian coefficient of restitution is a relative-velocity ratio. Under the restrictive one-body/rigid-seat assumptions, the translational rebound-energy fraction is `e²`, not `e` (fracasso2025numericalanddatadriven pages 24-28, aldahir2015utilizationoftifgrandbermudagrassfor pages 29-33, berencsi2021analyzingtheeffect pages 2-5).

3. Even `e² m_printed g h` is **not automatically the physically returned rebound energy in this experiment**, because the body observed in ballistic flight is the vertex–seat–sensor–tail subassembly, not the complete 18–23 g structure. The most direct energy estimate is

   `K_vertex = ½ m_flying v_sep² = m_flying g² t_second²/8`,

   where `m_flying` is the dynamically participating detached mass. Rewriting this as `e² m g h` is justified only if the denominator used in `e` is the actual incident relative speed of that same mass at the relevant interaction.

4. At present, `e_rebound = v_sep/dv` should be called a **normalized vertex-separation velocity**, **apparent restitution index**, or **system restitution index**. It has not yet been demonstrated to be the local vertex/seat COR.

| item | verdict | correct expression/condition | recommended wording |
|---|---|---|---|
| `e_rebound` interpretation | Not yet a demonstrated contact COR. As defined from secondary flight time, it reliably estimates the launched subassembly speed only if the top vertex undergoes ballistic flight with negligible drag and the timing truly spans takeoff-to-relanding. Because Newtonian COR is a ratio of relative separation to relative approach speed at a contact, your current ratio to base-pulse `dv` is best treated as a system-level normalized separation-speed metric, potentially influenced by structure, seat geometry, fixture, added sensor mass, and excitation history rather than a local joint property alone (fracasso2025numericalanddatadriven pages 24-28, bartz2023gravityeffectsin pages 9-13, martinovs2017determinationconstantsof pages 2-4, basson2013coefficientofrestitution pages 8-10) | `v_sep = g t_second / 2`, then current metric `e_rebound = v_sep / dv`. It approximates a true restitution coefficient only if `dv` is the actual pre-separation relative approach speed for the same rebounding mass and contact, with negligible other energy pathways (fracasso2025numericalanddatadriven pages 24-28, martinovs2017determinationconstantsof pages 2-4) | `normalized vertex separation velocity`; if you want a softer COR-like label: `apparent restitution index` or `system restitution index` |
| `e*m*g*h` | Dimensionally an energy, but not standard rebound energy and not a defensible estimate of returned kinetic energy in the usual impact-mechanics sense. Across rebound-resilience and COR frameworks, energy return scales with `e^2`, not `e`; no retrieved standard treated first-power `e` as an energy fraction. First-power velocity-ratio metrics do exist as indices, e.g. Leeb-type rebound/impact velocity measures, but they are not called returned energy (aldahir2015utilizationoftifgrandbermudagrassfor pages 29-33, berencsi2021analyzingtheeffect pages 2-5, ghabeche2015degradationofplastic pages 6-9) | `e m g h` is an ad hoc scalarization: impact-energy scale `mgh` weighted by a velocity ratio `e`. It is not the translational KE returned to the rebounding body (aldahir2015utilizationoftifgrandbermudagrassfor pages 29-33, berencsi2021analyzingtheeffect pages 2-5) | `velocity-weighted impact-energy index`; if keeping units explicit: `normalized rebound index in mJ` |
| Physically returned KE using printed mass | Usually wrong for your setup, because the rebounding body is not the whole printed prism. Using full printed mass overstates returned translational KE unless essentially all printed mass leaves contact and rebounds together with speed `v_sep` (unsupported by your description) | `KE_return = (1/2) m_printed v_sep^2 = m_printed g h e^2` only if `m_printed` is the actual rebounding mass and `dv` is that mass's incident relative speed (fracasso2025numericalanddatadriven pages 24-28, aldahir2015utilizationoftifgrandbermudagrassfor pages 29-33, berencsi2021analyzingtheeffect pages 2-5) | `upper-bound whole-specimen returned translational KE` only if explicitly caveated; otherwise avoid |
| Physically returned KE using moving vertex-subassembly mass | This is the physically relevant translational rebound-energy estimate if the flying body is the top vertex + seat + accelerometer + cable tail and `v_sep` is measured from the ballistic interval. This still estimates only translational KE of that subassembly, not total elastic energy released in the structure or dissipated at reseating (martinovs2017determinationconstantsof pages 2-4, fracasso2025numericalanddatadriven pages 24-28) | `KE_return,vertex = (1/2) m_vertex v_sep^2 = m_vertex g h_vertex = m_vertex g h e^2` if `e = v_sep / v_in` and `v_in = dv` is the actual approach speed of that same subassembly relative to the seat just before separation; otherwise use `(1/2) m_vertex v_sep^2` directly and do not rewrite as `e^2 mgh` (fracasso2025numericalanddatadriven pages 24-28, martinovs2017determinationconstantsof pages 2-4) | `returned translational KE of detached vertex subassembly` |
| Pareto ranking | Replacing `e` by `e^2` does **not** in general preserve rankings when mass varies, because `m e` and `m e^2` are not monotone transforms of one another. Ranking is preserved only if mass is constant, or if all compared points share the same positive multiplicative factor. Your current batch may be unaffected empirically, but that is dataset-specific | Objective 1: `J1 = m e`; Objective 2: `J2 = m e^2`. Since `J2 ≠ f(J1)` for a strictly monotone scalar `f` when `m` varies across designs, pairwise ordering and Pareto membership can change | State explicitly: `current batch ranking unchanged empirically; not guaranteed in general` |
| Uncertainty | Your present relative-SEM form is correct for `e m g h` if `g,h` are treated exact and `e,m` independent. For the physically returned KE form based on `e^2`, the delta-method relative SEM doubles the contribution from `e`. If covariance between `e` and mass, or uncertainty in `dv`, `t_second`, or vertex mass matters, include those terms | For `Y = e m g h`: `SEM_rel(Y) ≈ sqrt[(SEM_e/e)^2 + (SEM_m/m)^2]`. For `Y = e^2 m g h`: `SEM_rel(Y) ≈ sqrt[(2 SEM_e/e)^2 + (SEM_m/m)^2]`. Equivalently from direct variables, with `Y=(1/2)m(g t_second/2)^2`, propagate from `m` and `t_second` if that is what you actually measure | `relative SEM of index` for `e m g h`; `relative SEM of returned-KE estimate` for `e^2`-based or direct-`v_sep` energy |
| Recommended names | The current labels over-claim energy return. To align with standards language: reserve `restitution` for a velocity ratio tied to a specified contact and rebounding mass; reserve `rebound resilience`/`energy return` for `e^2`-type energy fractions; reserve `returned KE` for `(1/2) m v^2` of the actual rebounding body (fracasso2025numericalanddatadriven pages 24-28, aldahir2015utilizationoftifgrandbermudagrassfor pages 29-33, berencsi2021analyzingtheeffect pages 2-5, steele2006developmentofa pages 2-3, pajunen2019designandimpact pages 7-8) | Suggested naming map: `e_rebound` → `normalized vertex separation velocity` or `apparent/system restitution index`; `e_reb_mJ` → `velocity-weighted impact-energy index`; `(1/2) m_vertex v_sep^2` → `returned translational KE of detached vertex subassembly` | Use names that encode what is actually measured, not what is hoped to be inferred |


*Table: This table summarizes the main audit findings for your rebound metrics, including what each quantity can legitimately mean, the conditions under which energy formulas are physically valid, and safer terminology for reporting and optimization.*

## A. Physics and terminology

### A1. Governing mechanics

Newtonian COR is

`e_N = |v_relative,separation| / |v_relative,approach|`.

The literature explicitly defines it as relative separation velocity divided by relative approach velocity and emphasizes dependence on geometry, velocity, and material/system properties (fracasso2025numericalanddatadriven pages 24-28). Sports-impact work likewise defines COR as rebound velocity divided by incident velocity (berencsi2021analyzingtheeffect pages 2-5).

For a mass whose incident speed is `v_i` and rebound speed is `v_r=e v_i`,

`K_r/K_i = (½m v_r²)/(½m v_i²) = e²`.

For free fall through `h`, `½m v_i²=mgh`, hence

`K_r = e²mgh`.

Equivalently, rebound height satisfies `h_r/h=e²`, and rebound resilience is the squared COR in the ideal gravitational-bounce construction (aldahir2015utilizationoftifgrandbermudagrassfor pages 29-33). Thus, your claimed factor error is correct: relative to `e²mgh`, the reported `emgh` is too large by `1/e`, or about 20–50 for `e=0.05–0.02`.

Your quoted `0.1–0.7 mJ` range is broadly plausible, though the endpoints depend on the pairing of mass and `e`. Using all extrema independently,

- minimum: `(0.02)²(0.018)(9.81)(1.524) ≈ 0.108 mJ`;
- maximum: `(0.05)²(0.023)(9.81)(1.524) ≈ 0.860 mJ`.

Therefore, **“microjoule scale” is linguistically true but potentially misleading**: these are approximately 100–900 µJ, conventionally reported as tenths of a millijoule, not a few µJ.

### A2. Is there any accepted first-power-`e` energy framework?

**No accepted framework was found that calls `e E_impact` an energy returned or an energy fraction.** Rubber rebound resilience, drop-height resilience, pendulum rebound, and sports-ball rebound use returned/applied energy or rebound/drop height, corresponding to `e²` under ideal conditions (aldahir2015utilizationoftifgrandbermudagrassfor pages 29-33, chandrasekara2011epoxidizedvegetableoils pages 5-7, martinovs2017determinationconstantsof pages 2-4). Instrumented sports tests report COR itself as a velocity ratio, separately from energy loss or resilience (berencsi2021analyzingtheeffect pages 2-5).

There are accepted **first-power velocity-ratio indices**. Leeb hardness, for example, is based on rebound-to-impact velocity, but it is a hardness/rebound index—not returned energy. This provides a conceptual precedent for an index such as yours, not support for labeling it in joules as physical energy.

Accordingly:

- **Defensible:** “velocity-weighted impact-energy index,” explicitly defined as `J_v = e m_printed g h`.
- **Not defensible:** “absolute rebound energy,” “energy returned to payload,” or “fraction `e` of impact energy.”
- **Cleaner optimization variable:** use dimensionless `e_rebound` directly unless mass weighting has an independently justified design purpose. Multiplying by `mgh` creates an energy-looking unit without supplying an energy law.

### A3. Important qualification about `e²mgh`

The standard equation does not validate the choice `m=m_printed`. Returned translational energy is always `½m_moving v²` for the body whose velocity was measured. If only a vertex assembly flies, use its effective flying mass. If elastic modes throughout the structure retain energy, no single lumped-mass rebound formula measures the structure’s complete recovered or dissipated energy. Pajunen et al. instead obtained dissipation from dynamic stress–strain behavior and assessed peak-force load limitation; they also explicitly recognized hysteresis, plastic deformation, and test-fixture damping as possible energy sinks (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8).

## B. What `e_rebound` may measure

### B1. What the timing establishes

If the interval genuinely runs from loss of contact to return to the same elevation, the seat is effectively stationary during most of that interval, vertical motion is ballistic, and drag is negligible, then

`v_sep = g t_second/2`.

Rebound tests routinely infer speed from rebound height or flight intervals; pendulum work similarly uses `v=√(2gh)` after separation (bartz2023gravityeffectsin pages 9-13, martinovs2017determinationconstantsof pages 2-4). Therefore, the timing is a defensible estimator of the **vertex subassembly’s launch speed**.

It does **not by itself establish local contact COR**, because your denominator is the plate’s total pulse velocity change, not a measured relative approach speed of vertex versus seat immediately before their separating interaction. Furthermore, local COR normally characterizes an approach–compression–restitution contact event. Here, separation may result from delayed elastic vibration after the base pulse, rather than rebound from a discrete vertex/seat collision.

### B2. Candidate interpretations

#### (i) Genuine vertex–seat COR

This becomes credible only if measurements show a localized approach/contact/separation event at that joint, with

`e_joint = |v_vertex-v_seat|_after / |v_vertex-v_seat|_before`.

A key-seat joint can store/release elastic energy, slip, rotate, or exchange energy with the rest of the prism, so its apparent COR is an **assembly/contact COR**, not an intrinsic material constant. Published COR studies show strong dependence on shape, surface, penetration, rotation, impact speed, and other system variables; apparent values can even exceed one when unmeasured rotational/internal energy is converted to the observed translational direction (basson2013coefficientofrestitution pages 4-8, basson2013coefficientofrestitution pages 8-10, ryu2014analyticmodelof pages 1-4).

#### (ii) Structural energy-channeling metric

This is currently the most defensible interpretation. The base pulse excites structural modes, and the eventual separation speed reflects how geometry, prestress, damping, modal phase, and joint nonlinearity channel stored vibrational energy into one local degree of freedom. Tensegrity literature treats these systems as storing, dissipating, and redirecting impact energy; one soft-tensegrity study explicitly models conversion between elastic, kinetic, and frictionally dissipated energy (garanger2021softtensegritysystems pages 7-12). Pajunen et al. observed stress-wave oscillations, face rotation, strut vibration, hysteresis, substantial impact-energy dissipation, and load limiting—not a simple lumped COR objective (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8).

#### (iii) Fixture/interface metric

This remains a serious alternative. Wax compliance, key-seat tolerances, cable-tail forces, sensor mass, plate motion, and seating repeatability can control the separation threshold and phase. COR literature repeatedly warns that measured restitution belongs to the entire impact system rather than a material alone (basson2013coefficientofrestitution pages 4-8, fracasso2025numericalanddatadriven pages 24-28, bartz2023gravityeffectsin pages 9-13). Pajunen et al. specifically performed alternate-mass tests to assess test-setup energy loss, illustrating the need for fixture controls in tensegrity impact experiments (pajunen2019designandimpact pages 7-8).

### B3. Discriminating experiments

Use a factorial sequence rather than only restrained versus unrestrained:

1. **Restrained/unrestrained vertex:** A light, slack-free guide or capture restraint that prevents lift-off without materially changing axial stiffness tests whether the secondary burst is re-impact. Suppression of the burst confirms the event assignment, but does not alone identify the energy source.
2. **Direct relative kinematics:** High-speed video, laser vibrometry, or two synchronized displacement/velocity channels on vertex and seat. Measure relative velocity immediately before and after separation. This is the decisive test for a local COR.
3. **Instrument the seat or joint:** Add a miniature force film/load cell, contact switch, electrical continuity path, or acoustic-emission sensor to establish exact contact-loss and recontact times independently of the accelerometer envelope.
4. **Rigid dummy-joint control:** Replace the tensegrity beneath the same vertex/seat with a rigid support. Persistence of similar timing implicates the interface; disappearance implicates structural dynamics.
5. **Joint-condition sweep:** Systematically vary seat clearance, print orientation, surface finish, wax amount, mount torque, and deliberate preload. Strong sensitivity indicates fixture/contact control.
6. **Structural sweep at fixed joint:** Exchange prisms while reusing a geometrically identical calibrated vertex/seat. Correlation with measured `f_n`, damping ratio, prestress, or mode shape supports a structural metric.
7. **Added-mass sweep:** Repeat with several known sensor/vertex masses. For fixed available elastic energy, `v_sep∝m^{-1/2}`; for a contact governed chiefly by velocity COR, a different trend may occur. Added accelerometers can themselves perturb nonlinear vibro-impact dynamics, so this test is especially important.
8. **Base-pulse equivalence tests:** Hold `dv` fixed while changing pulse duration/peak G, then hold peak G fixed while changing `dv`. A true simple COR should primarily follow local approach speed; a modal channeling metric will depend strongly on pulse spectrum and phase relative to 300–550 Hz modes. ASTM D3332-type shock work treats peak acceleration and velocity change as separate fragility coordinates, and defines velocity change as pulse area (steele2006developmentofa pages 2-3).
9. **Energy accounting:** Measure plate/base input, force–displacement hysteresis, residual vibration, and vertex trajectory. Compare `½m_flyingv_sep²` with modal energy and hysteretic loss rather than inferring total dissipation from one flight interval.
10. **Repeatability and remount study:** Conduct same-mount repeats, then remove/remount repeats. A large between-mount variance is direct evidence of fixture/interface sensitivity.

### B4. Literature precedent for secondary-impact timing

There is strong precedent for using successive flight intervals or bounce heights to infer COR and fit dissipative contact models (bartz2023gravityeffectsin pages 9-13). There is also pendulum-rebound precedent for fitting rheological parameters from rebound height (martinovs2017determinationconstantsof pages 2-4). However, I found **no clear published precedent that treats delayed secondary-impact timing of one substructure after a base-shock pulse as a validated scalar measure of whole-structure dissipation**. That specific interpretation is therefore **unsupported at present** and should be introduced, if retained, as a novel empirical system metric requiring validation.

## C. Optimization, uncertainty, and reporting consequences

### C1. Does replacing `e` by `e²` preserve ranking or Pareto membership?

**Not in general when mass varies.** The objectives are

`J_1 = m e`,  
`J_2 = m e²`.

There is no single strictly increasing function `J_2=f(J_1)` independent of `m`. A reversal occurs whenever two designs satisfy

`m_A e_A < m_B e_B` but `m_A e_A² > m_B e_B²`.

For example, let `(m_A,e_A)=(4,0.4)` and `(m_B,e_B)=(1,0.9)`. Then `J_1A=1.6>0.9=J_1B`, but `J_2A=0.64<0.81=J_2B`. Thus pairwise ranking reverses. With another objective present, domination and Pareto-front membership can consequently change.

Ordering is guaranteed to be preserved when mass is constant, because squaring is strictly increasing for `e≥0`. It may also happen to be preserved over a particular restricted dataset, as in your batch, but that is an empirical fact—not a general property.

### C2. Uncertainty propagation

For

`Y=e²mgh`,

with `g` and `h` treated as exact and independent estimates of `e` and `m`, first-order delta propagation gives

`(SEM_Y/Y)² ≈ (2 SEM_e/e)² + (SEM_m/m)²`.

So your proposed expression is correct under those assumptions.

More generally, include

`+ 4 Cov(e,m)/(em)`

inside the relative-variance expression if `e` and `m` are correlated. If `h` or `dv` varies materially, propagate those as well. Because the primitive measurement is `t_second`, the cleanest returned-energy estimator is

`Y = m_flying g²t_second²/8`,

which gives

`SEM_Y/Y ≈ sqrt[(SEM_m/m)² + (2SEM_t/t)²]`

under independence. This avoids hiding uncertainty in `dv` when `dv` is not actually needed to compute the flying body’s post-separation KE.

Also distinguish **SEM of repeat-drop measurement** from specimen-to-specimen design variability. Mass standard deviation should enter a measurement-noise model only if it represents uncertainty in the mass assigned to that observation; batch manufacturing variability is generally a design/population variance, not instrument uncertainty.

### C3. Downstream dangers

The principal risks are substantive:

- reporting a quantity 20–50 times too large as physical returned energy;
- implying an energy balance that was never measured;
- assigning the full printed mass to motion observed only in a small subassembly;
- allowing readers to infer payload risk, efficiency, or dissipation from a mislabeled index;
- training Bayesian optimization or surrogate models against a target whose units suggest physics it does not obey;
- creating traceability and credibility problems when stakeholders compare the result with force–displacement work or kinetic energy from measured velocity.

The remedy is not necessarily to discard the empirical objective. Rename it, preserve the raw historical data, and distinguish three columns:

1. `r_v = v_sep/dv`: normalized separation-speed index;
2. `J_v = r_v m_printedgh`: legacy velocity-weighted index, if continuity is required;
3. `K_vertex = ½m_flyingv_sep²`: physically interpretable translational KE of the flying subassembly.

## D. Literature and standards assessment

### D1. COR from bounce or flight timing

Bernstein’s 1977 time-between-bounces method is conceptually consistent with ballistic inference of rebound velocity. Although the original paper was identified, its full text was unavailable through the retrieval system, so I cannot quote it directly. Modern repeated-bounce modeling uses observed contact/flight intervals and successive bounce heights to fit COR, while showing that gravity and impact speed can make the inferred COR velocity-dependent (bartz2023gravityeffectsin pages 9-13). Bounce-height field methods likewise infer COR from drop/rebound behavior, but demonstrate strong dependence on body shape, surface, weight, rotation, and deformation (basson2013coefficientofrestitution pages 4-8, basson2013coefficientofrestitution pages 8-10).

One retrieved source writes a bounce-height COR formula as `h/H`; that notation conflicts with its own velocity-ratio definition and with standard mechanics, for which the velocity COR is `sqrt(h/H)` and the height/energy ratio is `e²` (basson2013coefficientofrestitution pages 1-4, aldahir2015utilizationoftifgrandbermudagrassfor pages 29-33). Thus, any literature or code using `h/H` itself as “COR” must be checked for a squared-COR convention.

### D2. Rubber, pendulum, vertical rebound, sports, and Leeb tests

The common structure is:

- **velocity COR:** `e=v_r/v_i`;
- **height ratio/rebound resilience:** `h_r/h_i=e²` under ideal ballistic conditions;
- **returned translational-energy fraction:** `K_r/K_i=e²`.

The sports-turf literature explicitly states these relationships (aldahir2015utilizationoftifgrandbermudagrassfor pages 29-33). Squash-ball impact work measures COR directly from rebound and incident velocities and discusses energy loss separately (berencsi2021analyzingtheeffect pages 2-5). Rubber literature describes rebound resilience as the ability to return applied energy and reports it as a percentage (chandrasekara2011epoxidizedvegetableoils pages 5-7). Schob-pendulum modeling converts rebound height to rebound speed through mechanical-energy conservation (martinovs2017determinationconstantsof pages 2-4).

ISO 4662, ASTM D2632, Bashore/Schob, and related tests therefore support your `e²` objection, not `eE_impact`. Exact wording from the copyrighted ISO and ASTM standards was not retrieved, so this conclusion is based on the published implementations and governing measurement physics rather than a verbatim clause audit. Leeb testing is the notable first-power velocity-ratio precedent, but the resulting number is a **hardness/rebound index**, not an energy fraction.

### D3. Tensegrity and architected-material impact literature

Pajunen et al. subjected 3D-printable tensegrity-inspired structures to repeated drop-weight impacts and characterized force–time response, wave-transmission delay, peak-force plateaus, dynamic stress–strain response, energy dissipation percentage, residual strain, and cushion-factor-based energy-absorption efficiency. They did not define `e mgh` as rebound energy or use COR as the principal optimization objective (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8).

The paper’s “resilience” refers to elastic recovery/reusability after severe deformation, not a first-power COR energy fraction. It attributes experimental energy dissipation chiefly to material hysteresis after finding little permanent deformation, while explicitly considering fixture damping as a possible confounder (pajunen2019designandimpact pages 7-8).

SUPERball and tensegrity-lander literature supports the broader idea that tensegrities tolerate impact, store pre-impact kinetic energy elastically, dissipate part through friction/internal mechanisms, and can potentially reuse retained energy for locomotion (garanger2021softtensegritysystems pages 7-12, bruce2014superballexploringtensegrities pages 4-6). The retrieved sources do **not** establish delayed vertex bounce timing or `e mgh` as a standard tensegrity objective.

### D4. Packaging, cushioning, fragility, and shock standards

Published use of ASTM D3332 describes transient shock in terms of **peak acceleration and velocity change**, with velocity change equal to the area under the acceleration pulse. Half-sine peak acceleration is related to pulse duration and velocity change through pulse integration (steele2006developmentofa pages 2-3). This directly supports your treatment of `dv` as a pulse descriptor, but does not make `dv` the pre-impact relative velocity at the vertex/seat joint.

Pajunen’s cushioning treatment uses dynamic stress–strain work, maximum stress, cushion factor, relative density, and energy-absorption efficiency—not rebound velocity times drop energy (pajunen2019designandimpact pages 7-8). That is representative of legitimate cushioning-energy terminology: “absorbed” or “dissipated” energy should come from work/energy accounting, and “returned kinetic energy” from `½mv²` of the identified moving body.

Direct authoritative text for ASTM D1596, MIL-STD-810, and Lalanne was not available in the retrieved corpus. Therefore, it would be unsupported to claim that those documents expressly prohibit the phrase `e mgh`; however, **no evidence was found that any of them accepts it as rebound energy**, and the standard shock/cushioning quantities that were retrievable do not support that usage.

## Required corrections

- **Wrong:** “The raw `e_rebound` is a fraction of impact energy.”
- **Wrong/overclaimed:** “`e_reb_mJ` is absolute rebound energy returned to the payload.”
- **Conditionally correct:** `e²mgh` is returned translational KE only when `m` is the actual rebounding mass and `√(2gh)` is that mass’s incident relative speed for the relevant contact.
- **Unsupported:** `e_rebound` is presently a genuine material or vertex-seat COR.
- **Unsupported:** secondary-impact timing alone measures whole-structure dissipation.
- **Supported:** flight timing can estimate the separated vertex’s launch speed under ballistic assumptions.
- **Supported:** `sqrt[(2SEM_e/e)²+(SEM_m/m)²]` is the independent-error delta-method relative SEM for `e²mgh`.
- **Supported but dataset-specific:** your current designs may retain the same ranking after replacing `e` by `e²`; this is not guaranteed generally.

The recommended publication-level terminology is **“normalized vertex separation velocity”** for `g t_second/(2dv)`, **“legacy velocity-weighted impact-energy index”** for `e m_printedgh`, and **“returned translational kinetic energy of the detached vertex subassembly”** only for `½m_flyingv_sep²`.

References

1. (fracasso2025numericalanddatadriven pages 24-28): R Fracasso. Numerical and data-driven modeling of an impact test facility for pyroshock qualification: development and validation of contact mechanics models. Unknown journal, 2025.

2. (aldahir2015utilizationoftifgrandbermudagrassfor pages 29-33): PCF Aldahir. Utilization of'tifgrand'bermudagrass for sports turf: wear tolerance, shade response, and quality improvement. Unknown journal, 2015.

3. (berencsi2021analyzingtheeffect pages 2-5): Bence Ferenc Berencsi and Attila Kossa. Analyzing the effect of temperature on squash ball impacts using high-speed camera recordings. Periodica Polytechnica Mechanical Engineering, 65:354-362, Sep 2021. URL: https://doi.org/10.3311/ppme.18381, doi:10.3311/ppme.18381. This article has 2 citations.

4. (bartz2023gravityeffectsin pages 9-13): Sean P. Bartz. Gravity effects in mass-spring-damper models of inelastic collisions. European Journal of Physics, 44:025003, Jan 2023. URL: https://doi.org/10.1088/1361-6404/acacd7, doi:10.1088/1361-6404/acacd7. This article has 5 citations and is from a peer-reviewed journal.

5. (martinovs2017determinationconstantsof pages 2-4): Andris Martinovs, Svetlana Polukoshko, Elvijs Apeinans, and Edgars Zaicevs. Determination constants of 4-element reological model with rebound resilience method. Engineering for Rural Development, May 2017. URL: https://doi.org/10.22616/erdev2017.16.n189, doi:10.22616/erdev2017.16.n189. This article has 5 citations.

6. (basson2013coefficientofrestitution pages 8-10): Frans Basson, Robert Humphreys, and Andi Temmu. Coefficient of restitution for rigid body dynamics modelling from onsite experimental data. ArXiv, pages 1161-1170, Sep 2013. URL: https://doi.org/10.36487/acg\_rep/1308\_82\_basson, doi:10.36487/acg\_rep/1308\_82\_basson. This article has 13 citations.

7. (ghabeche2015degradationofplastic pages 6-9): Wafia Ghabeche, Latifa Alimi, and Kamel Chaoui. Degradation of plastic pipe surfaces in contact with an aggressive acidic environment. Energy Procedia, 74:351-364, Aug 2015. URL: https://doi.org/10.1016/j.egypro.2015.07.625, doi:10.1016/j.egypro.2015.07.625. This article has 39 citations and is from a peer-reviewed journal.

8. (steele2006developmentofa pages 2-3): J. Steele and T. Biswas. Development of a shock & vibration spec for 300mm wafer amhs handling. The 17th Annual SEMI/IEEE ASMC 2006 Conference, pages 245-250, May 2006. URL: https://doi.org/10.1109/asmc.2006.1638762, doi:10.1109/asmc.2006.1638762. This article has 5 citations.

9. (pajunen2019designandimpact pages 7-8): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

10. (chandrasekara2011epoxidizedvegetableoils pages 5-7): Ganga Chandrasekara, M.K. Mahanama, D.G. Edirisinghe, and L. Karunanayake. Epoxidized vegetable oils as processing aids and activators in carbon-black filled natural rubber compounds. Journal of The National Science Foundation of Sri Lanka, 39:243, Oct 2011. URL: https://doi.org/10.4038/jnsfsr.v39i3.3628, doi:10.4038/jnsfsr.v39i3.3628. This article has 80 citations.

11. (pajunen2019designandimpact pages 5-7): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

12. (basson2013coefficientofrestitution pages 4-8): Frans Basson, Robert Humphreys, and Andi Temmu. Coefficient of restitution for rigid body dynamics modelling from onsite experimental data. ArXiv, pages 1161-1170, Sep 2013. URL: https://doi.org/10.36487/acg\_rep/1308\_82\_basson, doi:10.36487/acg\_rep/1308\_82\_basson. This article has 13 citations.

13. (ryu2014analyticmodelof pages 1-4): Hwan-Taek Ryu, Byung-Ju Yi, and Younghun Kwon. Analytic model of variable characteristic of coefficient of restitution and its application to soccer ball trajectory planning. Preprint, Jan 2014. URL: https://doi.org/10.48550/arxiv.1408.4225, doi:10.48550/arxiv.1408.4225. This article has 0 citations.

14. (garanger2021softtensegritysystems pages 7-12): Kévin Garanger, Isaac del Valle, Miriam Rath, Matthew Krajewski, Utkarsh Raheja, Marco Pavone, and Julian J. Rimoli. Soft tensegrity systems for planetary landing and exploration. Earth and Space 2021, pages 841-854, Apr 2021. URL: https://doi.org/10.1061/9780784483374.078, doi:10.1061/9780784483374.078. This article has 31 citations.

15. (basson2013coefficientofrestitution pages 1-4): Frans Basson, Robert Humphreys, and Andi Temmu. Coefficient of restitution for rigid body dynamics modelling from onsite experimental data. ArXiv, pages 1161-1170, Sep 2013. URL: https://doi.org/10.36487/acg\_rep/1308\_82\_basson, doi:10.36487/acg\_rep/1308\_82\_basson. This article has 13 citations.

16. (bruce2014superballexploringtensegrities pages 4-6): J Bruce, AP Sabelhaus, Y Chen, and D Lu. Superball: exploring tensegrities for planetary probes. Unknown journal, 2014.