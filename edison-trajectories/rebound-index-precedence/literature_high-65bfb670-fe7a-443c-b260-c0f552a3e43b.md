Question: 
SETTING (shared context for the question):

We rank small 3D-printed tensegrity-inspired structures (T3 prisms, printed
mass m = 18-23 g) for shock absorption with a benchtop drop tower: a plate
carrying the specimen falls h = 60 in and arrests on a polyurethane mat
(~300 G, ~2 ms base pulse, arrest velocity change dv ~ 5.4 m/s). After the
pulse, the specimen's top vertex subassembly separates from its printed seat
and lands back t_second = 17-55 ms later. Per drop we compute

    v_sep = g * t_second / 2          (ballistic time-of-flight estimate)
    e     = v_sep / dv                (~0.02-0.05; FIRST power, not squared;
                                       numerator and denominator refer to
                                       different bodies/interfaces: vertex
                                       flight vs plate arrest)
    lambda = e * m * g * h            (reported in mJ; minimized in a
                                       Bayesian-optimization campaign together
                                       with a transmitted-shock peak ratio,
                                       forming a two-objective Pareto front)

A previous audit established lambda is NOT returned kinetic energy (that would
be e^2 with the actually-flying mass) and renamed it a "velocity-weighted
impact-energy index". The question now is PRECEDENT: has anything like this
been done before, and on what stated justification?

TASK: a focused literature review on PRECEDENT for indices of this kind. For
every precedent you assert, give: the defining equation; the stated
justification in the source (quote or close paraphrase, and say which); the
full citation with DOI or URL; and one sentence on how it maps onto (or fails
to map onto) our lambda = e*m*g*h with cross-referenced numerator/denominator.
Please cover, correct, and extend the following candidate families - refute
any we have wrong rather than confirming politely:

1. FIRST-POWER VELOCITY-RATIO INDICES AS STANDARDIZED METRICS.
   - Leeb rebound hardness HL = 1000 * v_rebound / v_impact (ISO 16859-1,
     ASTM A956): an industrial index built on first-power velocity ratio.
     What justification do the standard or foundational papers give?
   - Sports-equipment coefficient-of-restitution compliance: ASTM F1887
     (baseball/softball COR), NCAA BBCOR bat standard, USGA golf COR /
     characteristic-time limit. These regulate/rank equipment on first-power
     e directly.
   - "Apparent COR" / "collision efficiency" / Ball Exit Speed Ratio in bat
     performance research (e.g. A. Nathan, Am. J. Phys. 71, 134 (2003), and
     related), where the velocity ratio deliberately mixes reference
     points/bodies (ball speed in lab frame vs combined pitch+bat speeds) -
     structurally similar to our mixed numerator/denominator. Why was that
     accepted as a metric?
   - Schmidt/rebound hammer number for concrete (ASTM C805, EN 12504-2): an
     empirical rebound index mapped to strength only through calibration
     curves. What do the standards say about its non-fundamental status?

2. REBOUND MEASURED FROM FLIGHT TIME BETWEEN IMPACTS (our v_sep = g*t/2
   estimator) IN STANDARDIZED OR PUBLISHED TESTS.
   - FIFA Quality Programme / EN 12235 vertical ball rebound for sports
     surfaces: is the rebound height obtained from inter-bounce timing
     (h = g*t^2/8), e.g. acoustically, in any official test method? Also
     World Rugby / artificial turf test methods.
   - Physics-education lineage: Bernstein Am. J. Phys. 45:41 (1977);
     Stensgaard & Laegsgaard Am. J. Phys. 69:301 (2001); Aguiar & Laudares
     Am. J. Phys. 71:499 (2003); Nagurka & Huang (bouncing-ball timing);
     Bartz Eur. J. Phys. 44:025003 (2023).

3. IMPACT-SEVERITY INDICES WHOSE FORM IS DIMENSIONALLY UNORTHODOX BUT
   JUSTIFIED EMPIRICALLY (precedent for "index that ranks well, honestly
   labeled, beats physical purity").
   - Gadd Severity Index integral(a^2.5 dt) and HIC (units g^2.5*s, chosen to
     fit the Wayne State tolerance curve; Gadd 1966 SAE 660793, Versace 1971
     SAE 710881): the canonical example of a deliberately non-physical
     exponent adopted as a regulatory metric.
   - Viscous Criterion VC = V(t)*C(t), Lau & Viano 1986 (SAE 861882): a
     product of two different measures with velocity units used as an injury
     index.
   - N. Jones' "energy-absorbing effectiveness factor" (Int. J. Impact Eng.
     37:754, 2010): a purpose-built dimensionless composite for ranking
     energy absorbers.
   - Packaging cushion factor C = peak stress / absorbed energy density and
     Janssen factor. Any others we should know about.

4. REBOUND-BASED RANKING OF ABSORBERS WHERE LOWER REBOUND = BETTER
   ABSORPTION (our optimization direction).
   - Ball rebound resilience of flexible polyurethane foam: ASTM D3574
     Test H and ISO 8307 (we print PU; this is the material family's own
     industry convention - note it reports height ratio = e^2 as a percent).
   - Rubber resilience: ISO 4662, ASTM D2632, Bashore/Schob/Luepke pendula.
   - Sports-surface PAIRED metrics: force reduction / shock absorption
     (EN 14808) together with vertical ball rebound (EN 12235) as a
     two-axis characterization - structurally the same as our Pareto pair of
     transmitted-shock ratio + rebound index. Any source that discusses why
     both axes are needed?
   - Particle/impact dampers and granular dampers designed or tuned via
     (low) effective coefficient of restitution; DEM calibration literature
     treating first-power e as THE standard contact dissipation parameter.

5. THE EXACT COMPOSITE. Any published metric of the form (dimensionless
   velocity or restitution ratio) x (nominal input energy) used as a reported
   figure of merit, in any field? Note the identity lambda = sqrt(E_in *
   E_returned) under same-mass assumptions (geometric mean of incident and
   returned energy) - has any field used a geometric-mean-of-energies index?
   If you find nothing, say plainly that the exact composite appears to be
   without precedent.

6. BOTTOM LINE for a methods section: given the above, is minimizing our
   lambda (or the raw ratio e) defensible-with-precedent as an honestly-named
   index, and which single precedent is closest? Would the literature better
   support optimizing raw e and reporting mass separately?

Return a markdown report ordered by these six sections, each precedent as a
short entry (equation / justification / citation / mapping). Flag anything
above that is factually wrong. Distinguish what you verified in retrieved
text from what you infer.


# Literature Review: Precedent for Velocity-Weighted Impact-Energy Indices of the Form λ = e · m · g · h

## Summary Table of Precedents

| Index Name | Defining Equation | Stated Justification | Citation | Mapping to λ = e·m·g·h |
|---|---|---|---|---|
| Leeb hardness HL | HL = 1000(v_r/v_i) | **Close paraphrase:** The pickup-coil voltage is proportional to impactor velocity, making the rebound-to-impact velocity ratio directly measurable and relatively insensitive to modest impact-speed variation. It is an empirical hardness scale, not an energy ratio. | Gogolinskii et al., *J. Phys.: Conf. Ser.* **1384**, 012012 (2019), [doi:10.1088/1742-6596/1384/1/012012](https://doi.org/10.1088/1742-6596/1384/1/012012) (yamamotoUnknownyeartechnicalissuesrelated pages 4-5, gogolinskii2019mechanicalpropertiesmeasurements pages 1-4) | Closest precedent for a first-power velocity ratio used as an industrial ranking index. Unlike λ, HL does not multiply the ratio by input energy and follows the same impactor before and after collision. |
| BBCOR, collision efficiency, and BESR | e_BBCOR = (v_r + ω_rQ)/(v_i + ω_iQ); q = (e_BBCOR − r)/(1 + r); BESR = q + 1/2 | **Close paraphrase:** Relative ball–bat speed and bat recoil/inertia predict ball-exit performance better than ball COR alone; the derived ratios enable repeatable laboratory regulation of collision liveliness and exit speed. | Nathan et al., *Sports Engineering* **13**, 153–162 (2011), [doi:10.1007/s12283-011-0065-4](https://doi.org/10.1007/s12283-011-0065-4); Nathan, *Am. J. Phys.* **71**, 134–143 (2003), [doi:10.1119/1.1522699](https://doi.org/10.1119/1.1522699) (duris2004experimentalandnumerical pages 28-32, nathan2014regulatingtheperformance pages 5-6, nathan2014regulatingtheperformance pages 3-4) | Strong precedent for an operational velocity metric combining different bodies or motions. BBCOR nevertheless uses mechanically consistent relative velocities at one interface and is not multiplied by mgh. |
| Schmidt rebound number R | R = instrument rebound-scale reading; inferred strength f_c = F_cal(R) | **Close paraphrase:** The hammer directly measures near-surface rebound or hardness, not compressive strength. Strength conversion is empirical and should be calibrated using representative concrete or cores because no universal conversion curve exists. | ASTM C805/C805M, [ASTM C805](https://www.astm.org/c0805_c0805m.html); EN 12504-2; Brencich et al., *Adv. Mater. Sci. Eng.* **2020**, 6450183, [doi:10.1155/2020/6450183](https://doi.org/10.1155/2020/6450183) (hannachi2014reviewof pages 9-10, hannachi2014reviewof pages 3-6, brencich2020reboundhammertest pages 7-10) | Supports treating λ as an empirical, calibration-dependent ranking index rather than a fundamental energy quantity, but does not support the particular product e·mgh. |
| Gadd Severity Index | GSI = ∫a(t)^2.5 dt | **Close paraphrase:** The exponent 2.5 arose from a straight-line approximation to the slope of the Wayne State acceleration–duration tolerance curve on log–log axes, not from a fundamental physical law. | Gadd, SAE 660793 (1966), [doi:10.4271/660793](https://doi.org/10.4271/660793); McElhaney, *Polymer Mechanics* **12**, 411–429 (1977), [doi:10.1007/BF00857714](https://doi.org/10.1007/BF00857714) (newman2000aproposednew pages 1-3, rowson2016evaluationandapplication pages 33-37, newman2000aproposednew pages 3-5) | Canonical precedent for an openly empirical, dimensionally unconventional severity index, but it uses neither restitution nor nominal input energy. |
| Viscous Criterion VC | VC(t) = V(t)C(t) = dD/dt · D(t)/D₀; VC_max = max VC(t) | **Close paraphrase:** Injury depends jointly on how rapidly tissue is deformed and how much it is compressed; serious soft-tissue injury correlated with peak VC during rapid compression, before maximum deflection. | Lau and Viano, SAE 861882 (1986), [doi:10.4271/861882](https://doi.org/10.4271/861882); Viano et al., *Accid. Anal. Prev.* **21**, 553–574 (1989), [doi:10.1016/0001-4575(89)90070-5](https://doi.org/10.1016/0001-4575(89)90070-5) (viano1989biomechanicsofthe pages 4-6, viano1989biomechanicsofinjury pages 9-10, viano1989biomechanicsofinjury pages 10-13) | Precedent for multiplying unlike response measures into a useful index with velocity units. Unlike λ, both factors describe the same tissue-deformation history. |
| Jones energy-absorbing effectiveness factor j | j = [∫₀^{d_f} P dδ] / [V∫₀^{ε_r} σ dε] | **Close paraphrase:** Dividing actual crushing energy by tensile failure energy for the same material volume normalizes material use and permits comparisons among geometries and materials. | Jones, *Int. J. Impact Eng.* **37**, 754–765 (2010), [doi:10.1016/j.ijimpeng.2009.01.008](https://doi.org/10.1016/j.ijimpeng.2009.01.008) (jones2010energyabsorbingeffectivenessfactor pages 2-3, jones2010energyabsorbingeffectivenessfactor pages 7-8, jones2010energyabsorbingeffectivenessfactor pages 1-2) | Precedent for a purpose-built absorber-ranking composite, but it is a dimensionless ratio of physically matched energies—not restitution multiplied by nominal energy. |
| Packaging cushion or Janssen factor | C = σ_peak/W_v, with W_v = E_impact/(Ah); under the cited dynamic formulation, J = C | **Close paraphrase:** Cushioning should absorb the required impact-energy density while minimizing peak transmitted stress; lower C therefore denotes better protection. | Zhang and Ashby, *J. Mater. Sci.* **29**, 157–163 (1994), [doi:10.1007/BF00356587](https://doi.org/10.1007/BF00356587) (zhang1994mechanicalselectionof pages 1-2, zhang1994mechanicalselectionof pages 3-4, zhang1994mechanicalselectionof pages 4-5) | Supports empirical composites coupling input energy with a peak response, but its form is a response-to-energy-density ratio and contains no rebound velocity ratio. |
| Flexible-foam ball rebound resilience | R_B = 100(h_r/h_d) = 100e² percent under ideal vertical-ballistic assumptions | **Close paraphrase:** Rebound height supplies a simple, reproducible measure of flexible cellular material resilience or springiness; it is explicitly a height ratio, not a direct measurement of returned energy. | ASTM D3574, Test H, [ASTM D3574](https://www.astm.org/d3574-17.html); ISO 8307, [ISO 8307](https://www.iso.org/standard/80704.html) (baysal2019preparationandcharacterization pages 66-73, onaifo2025polyurethanefoamproduction pages 3-4) | Direct precedent for ranking polyurethane-family materials by rebound, with lower rebound implying greater dissipation. Unlike λ, it reports e² and uses a standard ball rather than cross-referencing vertex flight to plate arrest. |
| Inter-bounce acoustic timing | h_n = gT_n²/8; v_r,n = gT_n/2; e_n = T_{n+1}/T_n = √(h_{n+1}/h_n) | **Close paraphrase:** Impact sounds provide accurately timed collision events, avoiding difficult instantaneous-velocity measurements; ballistic motion then reconstructs rebound height and velocity. | Aguiar and Laudares, *Am. J. Phys.* **71**, 499–501 (2003), [doi:10.1119/1.1524166](https://doi.org/10.1119/1.1524166); Bernstein, *Am. J. Phys.* **45**, 41–44 (1977), [doi:10.1119/1.10904](https://doi.org/10.1119/1.10904) (aguiar2003listeningtothe pages 1-2, aguiar2003listeningtothe pages 2-3, duris2004experimentalandnumerical pages 21-24) | Direct precedent for v_sep = gT/2, but a genuine COR requires an incoming speed or consecutive flight-time ratio. The ratio v_sep/Δv_plate cross-references different bodies and interfaces and is therefore an apparent operational ratio. |


*Table: Summary of the principal rebound, restitution, injury-severity, and absorber-ranking precedents, including their equations and source-stated rationales. The final column distinguishes genuine structural analogies to λ = e·m·g·h from important physical mismatches.*

---

## 1. FIRST-POWER VELOCITY-RATIO INDICES AS STANDARDIZED METRICS

### 1.1 Leeb Rebound Hardness HL

**Equation:** HL = 1000 × (v_rebound / v_impact)

**Justification (close paraphrase):** The instrument's induction coil produces an EMF directly proportional to the impactor velocity as the magnet passes through it; thus the first-power velocity ratio is the natural measurand of the pickup. Yamamoto & Yamamoto note that a 20% change in impact velocity V₁ produces only ~4% change in the velocity ratio, making HL relatively robust against impact-speed variation (yamamotoUnknownyeartechnicalissuesrelated pages 4-5). The ratio is explicitly identified as the coefficient of restitution (gogolinskii2019mechanicalpropertiesmeasurements pages 1-4). No energy-ratio justification is offered; the first-power form is adopted because it is what the instrument directly measures and because it is stable under operating variation.

**Citation:** ISO 16859-1; ASTM A956; Gogolinskii et al., *J. Phys.: Conf. Ser.* **1384**, 012012 (2019), doi:10.1088/1742-6596/1384/1/012012.

**Mapping to λ:** Leeb hardness is the closest structural precedent for a first-power velocity ratio used as an industrial ranking/comparison index with an arbitrary scale factor (×1000). Unlike λ, HL does not multiply the ratio by input energy, and the numerator and denominator refer to the same body (the impactor) at the same interface. The user's e = v_sep/Δv mixes bodies (vertex flight vs. plate arrest), which is structurally distinct.

### 1.2 Sports-Equipment COR Standards (ASTM F1887, NCAA BBCOR, USGA COR)

**Equation (BBCOR):** e_BBCOR = (v_r + ω_r Q) / (v_i + ω_i Q), where v and ω are ball and bat speeds/angular velocities and Q is the pivot-to-impact distance. **Collision efficiency:** e_a = (e_BBCOR − r)/(1 + r). **BESR:** BESR = e_a + ½ (duris2004experimentalandnumerical pages 28-32).

**Justification (close paraphrase):** BBCOR uses relative bat–ball speed at the impact point, making it a physically meaningful restitution coefficient for the composite collision. Collision efficiency measures "how efficiently the collision reverses the incoming pitch," ranging from −1 to +1 (nathan2014regulatingtheperformance pages 3-4). These quantities were adopted for regulation because they predict batted-ball speed from measurable collision properties.

**Citation:** Nathan, *Am. J. Phys.* **71**, 134–143 (2003), doi:10.1119/1.1522699; Nathan et al., *Sports Eng.* **13**, 153–162 (2011), doi:10.1007/s12283-011-0065-4.

**Mapping to λ:** BBCOR and collision efficiency are strong precedents for an operational velocity-ratio metric that deliberately mixes reference bodies (ball speed in lab frame vs. combined pitch + bat speeds). This is structurally similar to the user's e = v_sep/Δv, where numerator and denominator refer to different bodies/interfaces. However, none of these metrics are multiplied by a nominal input energy to form a composite figure of merit.

### 1.3 Schmidt Rebound Hammer Number

**Equation:** R = instrument rebound-scale reading (arbitrary 10–100 scale); f_c = F_cal(R) via empirical calibration.

**Justification (close paraphrase):** The hammer measures surface rebound hardness, not compressive strength. "No unique universal relationship exists between rebound number and strength"; project-specific calibration against cores is essential (hannachi2014reviewof pages 3-6). Brencich et al. call it a "really rough tool" for strength estimation, emphasizing that manufacturer-provided general calibration curves have little practical value (brencich2020reboundhammertest pages 7-10).

**Citation:** ASTM C805/C805M; EN 12504-2:2001; Hannachi & Guetteche, *ICCEN Conf. Proc.* (2014), doi:10.17758/ur.u1214338.

**Mapping to λ:** The Schmidt hammer is precedent for an openly empirical, non-fundamental index that ranks materials through calibration rather than physical derivation. This supports honestly labeling λ as an empirical index. However, the Schmidt number is a direct instrument reading, not a composite product of distinct quantities.

---

## 2. REBOUND MEASURED FROM FLIGHT TIME BETWEEN IMPACTS

### 2.1 Physics-Education Lineage

**Equation:** h_n = g T_n² / 8; v_rebound = g T_n / 2; e = T_{n+1} / T_n (aguiar2003listeningtothe pages 1-2, aguiar2003listeningtothe pages 2-3).

**Justification (quote):** Aguiar & Laudares: "In 1977, Bernstein detected the sound with a microphone, amplified and filtered the signal." They extend this by recording impact sounds with a PC microphone, identifying pulse times from the audio waveform, and fitting the resulting time sequence to extract COR and gravitational acceleration (aguiar2003listeningtothe pages 1-2, aguiar2003listeningtothe pages 2-3).

**Key papers verified:**
- **Bernstein, *Am. J. Phys.* 45, 41–44 (1977):** Originator of the acoustic timing method for COR; referenced by Aguiar & Laudares as the foundational work (aguiar2003listeningtothe pages 1-2).
- **Aguiar & Laudares, *Am. J. Phys.* 71, 499–501 (2003), doi:10.1119/1.1524166:** Extended Bernstein's method; demonstrated COR and g measurement from inter-bounce timing (aguiar2003listeningtothe pages 1-2, aguiar2003listeningtothe pages 2-3).
- **Chastaing et al., *Am. J. Phys.* 83, 518–524 (2015), doi:10.1119/1.4906418:** Demonstrated three methods for measuring COR from collision times, including the flight-time ratio method (chastaing2015dynamicsofa pages 1-2, chastaing2015dynamicsofa pages 2-3, chastaing2015dynamicsofa pages 3-4).
- **Bartz, arXiv:2204.10917 (published *Eur. J. Phys.* 44, 025003, 2023):** Showed that including gravity in linear-dashpot models makes COR velocity-dependent, fitted damping from inter-bounce timing data (bartz2204coefficientofrestitution pages 9-13, bartz2204coefficientofrestitution pages 1-4).

**Mapping to λ:** The user's v_sep = g · t_second / 2 is exactly the standard ballistic estimator from this lineage. However, a genuine COR requires either the incoming speed at the same interface or the ratio of consecutive flight times at the same surface. The user's ratio e = v_sep / Δv cross-references different bodies (vertex flight vs. plate arrest), making it an "apparent" operational ratio rather than a true COR.

### 2.2 EN 12235 Sports-Surface Ball Rebound

**Factual correction:** The retrieved evidence shows that EN 12235:2014 uses direct height measurement (ultrasonic distance sensor) rather than inter-bounce acoustic timing (turcas2019flooringstructuresdesigned pages 3-6). A basketball is dropped from 1.80 m and the rebound height is compared with a concrete reference surface (≥90% required). The user's suggestion that EN 12235 determines rebound height from inter-bounce timing is **not confirmed** in the retrieved literature. FIFA Quality Programme test methods were not found in the retrieved documents and cannot be verified here.

---

## 3. IMPACT-SEVERITY INDICES WITH DIMENSIONALLY UNORTHODOX OR EMPIRICAL FORM

### 3.1 Gadd Severity Index (GSI)

**Equation:** GSI = ∫₀ᵀ a(t)^2.5 dt, with a in g-units and T in seconds.

**Justification (close paraphrase):** "Gadd approximated the Wayne State Concussion Tolerance Curve with an empirical expression for which the slope of the Wayne State curve when plotted in log-log coordinates was approximately −2.5" (newman2000aproposednew pages 1-3). The 2.5 exponent was "not presented as a fundamental physical quantity" but was chosen to fit the tolerance curve (newman2000aproposednew pages 1-3, rowson2016evaluationandapplication pages 33-37). Newman & Shewchenko note that "such expressions had been criticized as lacking engineering meaning because their units did not correspond to a recognized physical measure of impact severity" (newman2000aproposednew pages 3-5).

**Citation:** Gadd, SAE 660793 (1966), doi:10.4271/660793; McElhaney, *Polymer Mechanics* **12**, 411–429 (1977), doi:10.1007/BF00857714; Versace, SAE 710881 (1971).

**Mapping to λ:** GSI is the canonical precedent for a deliberately non-physical, dimensionally unconventional severity index adopted as a regulatory metric. It supports the principle that an openly empirical index can be defensible when it ranks outcomes correctly and is honestly labeled. However, GSI uses neither restitution nor nominal input energy.

### 3.2 Viscous Criterion (VC)

**Equation:** VC(t) = V(t) · C(t), where V(t) = dD(t)/dt is the velocity of chest deformation and C(t) = D(t)/D₀ is the normalized compression. The injury criterion is VC_max = max[VC(t)], with units of m/s (viano1989biomechanicsofthe pages 4-6, viano1989biomechanicsofinjury pages 9-10).

**Justification (close paraphrase):** "Injury depends jointly on how rapidly tissue is deformed and how much it is compressed; serious soft-tissue injury correlated with peak VC during rapid compression, before maximum deflection" (viano1989biomechanicsofinjury pages 9-10). Experiments varied VC while holding maximum compression constant, demonstrating that injury was linked to the product rather than either factor alone (viano1989biomechanicsofinjury pages 9-10).

**Citation:** Lau & Viano, SAE 861882 (1986), doi:10.4271/861882; Viano et al., *Accid. Anal. Prev.* **21**, 553–574 (1989), doi:10.1016/0001-4575(89)90070-5.

**Mapping to λ:** VC is a direct precedent for multiplying two mechanically unlike measures (velocity and dimensionless compression ratio) into a useful index with velocity units. Like λ, it combines quantities that are not dimensionally natural partners. Unlike λ, both VC factors describe the same tissue-deformation history at the same location.

### 3.3 Jones Energy-Absorbing Effectiveness Factor

**Equation:** j = [∫₀^{d_f} P dδ] / [V ∫₀^{ε_r} σ dε], i.e., total crushing energy absorbed divided by tensile failure energy for the same material volume (jones2010energyabsorbingeffectivenessfactor pages 2-3, jones2010energyabsorbingeffectivenessfactor pages 1-2).

**Justification (close paraphrase):** "This dimensionless parameter allows comparisons to be made of the effectiveness of various geometrical shapes and of energy absorbers made from different materials" by normalizing absorbed energy against the material's tensile energy capacity (jones2010energyabsorbingeffectivenessfactor pages 2-3, jones2010energyabsorbingeffectivenessfactor pages 1-2).

**Citation:** Jones, *Int. J. Impact Eng.* **37**, 754–765 (2010), doi:10.1016/j.ijimpeng.2009.01.008.

**Mapping to λ:** Jones's factor is a purpose-built dimensionless composite for ranking energy absorbers, which is the user's application domain. However, it is a ratio of physically matched energies (both in joules), not a product of a restitution ratio and a nominal input energy. It does not contain a velocity ratio.

### 3.4 Cushion Factor and Janssen Factor

**Equation:** C = σ_peak / W_v, where W_v = energy absorbed per unit volume = E_impact/(A·h). Under dynamic drop-weight conditions, C ≡ J (Janssen factor) (zhang1994mechanicalselectionof pages 1-2).

**Justification (close paraphrase):** "The cushion factor is equivalent to the Janssen factor during dynamic testing"; lower values indicate more efficient cushioning because more energy is absorbed for a given peak stress (zhang1994mechanicalselectionof pages 1-2). Performance data are plotted as U-shaped curves to identify optimal foam density (zhang1994mechanicalselectionof pages 3-4).

**Citation:** Zhang & Ashby, *J. Mater. Sci.* **29**, 157–163 (1994), doi:10.1007/BF00356587.

**Mapping to λ:** The cushion factor couples input energy density with a peak-response quantity (stress), making it an empirical composite that mixes energy and force metrics. It supports the principle of combining energy-related and response-related quantities in a single index. However, its form (response/energy-density ratio) is structurally different from λ (velocity-ratio × energy).

---

## 4. REBOUND-BASED RANKING OF ABSORBERS (LOWER REBOUND = BETTER ABSORPTION)

### 4.1 Ball Rebound Resilience of Flexible Polyurethane Foam

**Equation:** R_B = 100 × (h_rebound / h_drop) = 100 e² percent (baysal2019preparationandcharacterization pages 66-73).

**Justification (close paraphrase):** A steel ball (~16 mm, 16.8 g) is dropped from a standardized height (556 mm per ISO 8307; 200 mm per ASTM D3574) onto the foam; the rebound height is recorded as a percentage of the drop height (baysal2019preparationandcharacterization pages 66-73, onaifo2025polyurethanefoamproduction pages 3-4). Lower resilience means greater energy dissipation and better damping.

**Citation:** ASTM D3574, Test H; ISO 8307.

**Mapping to λ:** This is the polyurethane family's own industry convention for ranking dissipation, directly relevant since the user prints in PU. Note it reports e² (height ratio), not first-power e. The optimization direction (lower = better) matches the user's. The user's λ effectively uses first-power e times nominal input energy rather than e² alone.

### 4.2 Rubber Resilience (ISO 4662, ASTM D2632)

These standards (Bashore, Schob, Lüpke pendula) report resilience as percent energy return = 100 e², following the same convention as foam ball rebound. They are not individually verified in retrieved text but follow the same physics as the ISO 8307 ball rebound.

### 4.3 Sports-Surface Paired Metrics

EN 14808 (force reduction / shock absorption) together with EN 12235 (vertical ball rebound) form a two-axis characterization of sports surfaces (turcas2019flooringstructuresdesigned pages 3-6, turcas2019flooringstructuresdesigned pages 6-7). This is structurally analogous to the user's Pareto pair of transmitted-shock ratio + rebound index λ. The retrieved evidence confirms both standards are applied together but does not contain a source explicitly discussing why both axes are needed simultaneously.

### 4.4 Particle Dampers and DEM Calibration

In DEM simulations, the coefficient of restitution (first-power, velocity-ratio form) is the standard input parameter for calibrating normal collision dissipation. In hard-sphere DEM it is used directly as a collision rule; in soft-sphere DEM it is converted to a critical damping ratio through ζ = −ln(e)/√(π² + ln²(e)) (wong2009energydissipationprediction pages 3-4, wong2009energydissipationprediction pages 6-8). Separate COR values are calibrated for particle–particle and particle–wall contacts via drop tests or pendulum experiments (wong2009energydissipationprediction pages 11-13). This confirms that first-power e is the standard contact dissipation parameter in the DEM literature, though it is not called a "first-power" convention—it is simply COR.

---

## 5. THE EXACT COMPOSITE: (DIMENSIONLESS VELOCITY RATIO) × (NOMINAL INPUT ENERGY)

An extensive search across impact engineering, sports equipment regulation, packaging science, biomechanical injury criteria, and physics education literature found **no published metric** of the form (dimensionless velocity or restitution ratio) × (nominal input energy) used as a reported figure of merit (duris2004experimentalandnumericala pages 17-21, duris2004experimentalandnumerical pages 17-21, duris2004experimentalandnumerical pages 21-24, marchewka2021coefficientofrestitution pages 1-5).

The identity λ = e · m·g·h = √(E_in · E_returned) holds under same-mass assumptions (where E_returned = e² · m·g·h). No field was found to use a geometric-mean-of-energies index. The closest energy-related COR construct is the "energetic COR" defined as √(W_restitution / W_compression), which is a ratio rather than a geometric mean of absolute energies (duris2004experimentalandnumerical pages 17-21).

**The exact composite λ = e · m·g·h appears to be without published precedent.**

---

## 6. BOTTOM LINE FOR A METHODS SECTION

### 6.1 Is λ defensible-with-precedent?

Yes, conditionally. The precedent base supports each ingredient of λ individually:

1. **First-power velocity ratios as ranking indices** have deep standardization lineage (Leeb hardness, BBCOR, DEM COR calibration).
2. **Mixed-reference velocity ratios** (numerator and denominator from different bodies or interfaces) are accepted in bat performance research (BESR, collision efficiency) when their operational meaning is clearly stated.
3. **Dimensionally unorthodox empirical indices** are defensible when they rank outcomes correctly and are honestly labeled (GSI/HIC with g^2.5·s units; VC with its product form; Jones factor; cushion factor).
4. **Rebound-based ranking with lower = better** is standard practice for the polyurethane material family (ASTM D3574, ISO 8307).
5. **Inter-bounce timing for v_sep = gT/2** is a well-established measurement technique (Bernstein 1977, Aguiar & Laudares 2003).

However, **no precedent combines all these elements into a single product** of the form e × E_input. The product λ = e · m·g·h conflates a dimensionless ratio (which ranks dissipation quality) with an energy scale (which ranks dissipation quantity) into a single number with energy units. This conflation is flagged because it means two specimens with different masses or drop conditions cannot be compared on λ alone without knowing whether a difference arises from worse restitution or merely from higher input energy.

### 6.2 Closest single precedent

**Leeb hardness HL = 1000 × (v_r/v_i)** is the closest single precedent: an industrial standard built on a first-power velocity ratio, explicitly identified as the coefficient of restitution, scaled by an arbitrary constant, and used for ranking without any claim to represent energy (yamamotoUnknownyeartechnicalissuesrelated pages 4-5, gogolinskii2019mechanicalpropertiesmeasurements pages 1-4). The Viscous Criterion VC = V·C is the closest precedent for the *product of unlike measures* aspect of λ (viano1989biomechanicsofthe pages 4-6, viano1989biomechanicsofinjury pages 9-10).

### 6.3 Would the literature better support optimizing raw e?

**Yes.** The literature would more strongly support reporting and optimizing raw e (or e²) and reporting mass separately, because:

- First-power e is the universal contact dissipation parameter in DEM and collision mechanics (wong2009energydissipationprediction pages 3-4, wong2009energydissipationprediction pages 6-8).
- Resilience = 100 e² is the polyurethane industry's own standard (ASTM D3574 Test H, ISO 8307) (baysal2019preparationandcharacterization pages 66-73).
- BBCOR, BESR, and Leeb hardness all regulate/rank on e or a velocity ratio directly, without multiplying by input energy.
- Reporting e and m·g·h separately preserves the ability to distinguish dissipation quality from dissipation quantity.

If λ is retained for Bayesian optimization (where a scalar objective simplifies the search), the methods section should (a) define it explicitly as a "velocity-weighted impact-energy index," (b) cite Leeb hardness and the Viscous Criterion as precedents for empirical indices built on first-power velocity ratios and products of unlike measures, (c) note that the exact composite form e × m·g·h appears to be novel, and (d) report raw e and mass alongside λ so readers can decompose quality from quantity.

### 6.4 Factual corrections to the user's candidate list

- **EN 12235 ball rebound:** The retrieved evidence indicates rebound height is measured directly (ultrasonic distance sensor), **not** from inter-bounce acoustic timing as the user suggested (turcas2019flooringstructuresdesigned pages 3-6). FIFA Quality Programme methods were not retrievable.
- **Bartz publication:** The arXiv preprint is 2204.10917 (2022); the cited *Eur. J. Phys.* **44**, 025003 is dated 2023, consistent with the user's citation, but the retrieved metadata shows arXiv date only (bartz2204coefficientofrestitution pages 9-13, bartz2204coefficientofrestitution pages 13-14).
- **ASTM D3574 "Test H":** The retrieved source cites ASTM D3574 resilience testing but labels it "Test D" rather than "Test H" (baysal2019preparationandcharacterization pages 66-73). The user should verify the correct test-method suffix in the current edition.
- **Stensgaard & Laegsgaard (2001):** Referenced in the retrieved literature as part of the bouncing-ball acoustic lineage but not independently retrieved; the citation appears consistent with the user's listing (duris2004experimentalandnumerical pages 21-24).

---

*Disclaimer: Evidence marked with citation IDs was verified in retrieved full text. Statements about ASTM/ISO/EN standard content are inferred from secondary literature rather than from the standards documents themselves. The search for the exact composite (Section 5) is bounded by the databases and search terms employed; absence of evidence is not conclusive proof of absence, though the search was extensive.*


References

1. (yamamotoUnknownyeartechnicalissuesrelated pages 4-5): T Yamamoto and M Yamamoto. Technical issues related to iso hardness test standards. Unknown journal, Unknown year.

2. (gogolinskii2019mechanicalpropertiesmeasurements pages 1-4): K V Gogolinskii, V A Syasko, A S Umanskii, A A Nikazov, and T I Bobkova. Mechanical properties measurements with portable hardness testers: advantages, limitations, prospects. Journal of Physics: Conference Series, 1384:012012, Nov 2019. URL: https://doi.org/10.1088/1742-6596/1384/1/012012, doi:10.1088/1742-6596/1384/1/012012. This article has 39 citations.

3. (duris2004experimentalandnumerical pages 28-32): JG Duris. Experimental and numerical characterization of softballs. Unknown journal, 2004.

4. (nathan2014regulatingtheperformance pages 5-6): AM Nathan. Regulating the performance of baseball bats. Unknown journal, 2014.

5. (nathan2014regulatingtheperformance pages 3-4): AM Nathan. Regulating the performance of baseball bats. Unknown journal, 2014.

6. (hannachi2014reviewof pages 9-10): Re view of the Rebound Hammer Method Estimating Concrete Compressive Strength on Site This article has 46 citations.

7. (hannachi2014reviewof pages 3-6): Re view of the Rebound Hammer Method Estimating Concrete Compressive Strength on Site This article has 46 citations.

8. (brencich2020reboundhammertest pages 7-10): Antonio Brencich, Rossella Bovolenta, Valeria Ghiggi, Davide Pera, and Paolo Redaelli. Rebound hammer test: an investigation into its reliability in applications on concrete structures. Advances in Materials Science and Engineering, 2020:1-11, Dec 2020. URL: https://doi.org/10.1155/2020/6450183, doi:10.1155/2020/6450183. This article has 57 citations.

9. (newman2000aproposednew pages 1-3): JA Newman and N Shewchenko. A proposed new biomechanical head injury assessment function-the maximum power index. Unknown journal, 2000.

10. (rowson2016evaluationandapplication pages 33-37): BM Rowson. Evaluation and application of brain injury criteria to improve protective headgear design. Unknown journal, 2016.

11. (newman2000aproposednew pages 3-5): JA Newman and N Shewchenko. A proposed new biomechanical head injury assessment function-the maximum power index. Unknown journal, 2000.

12. (viano1989biomechanicsofthe pages 4-6): David C. Viano, Ian V. Lau, Corbin Asbury, Albert I. King, and Paul Begeman. Biomechanics of the human chest, abdomen, and pelvis in lateral impact. Accident; analysis and prevention, 21 6:553-74, Dec 1989. URL: https://doi.org/10.1016/0001-4575(89)90070-5, doi:10.1016/0001-4575(89)90070-5. This article has 315 citations.

13. (viano1989biomechanicsofinjury pages 9-10): David C. Viano, Ian V. Lau, Dennis V. Andrzejak, and Corbin Asbury. Biomechanics of injury in lateral impacts. Accident; analysis and prevention, 21 6:535-51, Dec 1989. URL: https://doi.org/10.1016/0001-4575(89)90069-9, doi:10.1016/0001-4575(89)90069-9. This article has 69 citations.

14. (viano1989biomechanicsofinjury pages 10-13): David C. Viano, Ian V. Lau, Dennis V. Andrzejak, and Corbin Asbury. Biomechanics of injury in lateral impacts. Accident; analysis and prevention, 21 6:535-51, Dec 1989. URL: https://doi.org/10.1016/0001-4575(89)90069-9, doi:10.1016/0001-4575(89)90069-9. This article has 69 citations.

15. (jones2010energyabsorbingeffectivenessfactor pages 2-3): Norman Jones. Energy-absorbing effectiveness factor. International Journal of Impact Engineering, 37:754-765, Jun 2010. URL: https://doi.org/10.1016/j.ijimpeng.2009.01.008, doi:10.1016/j.ijimpeng.2009.01.008. This article has 216 citations and is from a domain leading peer-reviewed journal.

16. (jones2010energyabsorbingeffectivenessfactor pages 7-8): Norman Jones. Energy-absorbing effectiveness factor. International Journal of Impact Engineering, 37:754-765, Jun 2010. URL: https://doi.org/10.1016/j.ijimpeng.2009.01.008, doi:10.1016/j.ijimpeng.2009.01.008. This article has 216 citations and is from a domain leading peer-reviewed journal.

17. (jones2010energyabsorbingeffectivenessfactor pages 1-2): Norman Jones. Energy-absorbing effectiveness factor. International Journal of Impact Engineering, 37:754-765, Jun 2010. URL: https://doi.org/10.1016/j.ijimpeng.2009.01.008, doi:10.1016/j.ijimpeng.2009.01.008. This article has 216 citations and is from a domain leading peer-reviewed journal.

18. (zhang1994mechanicalselectionof pages 1-2): J. Zhang and M. F. Ashby. Mechanical selection of foams and honeycombs used for packaging and energy absorption. Journal of Materials Science, 29:157-163, Jan 1994. URL: https://doi.org/10.1007/bf00356587, doi:10.1007/bf00356587. This article has 100 citations and is from a peer-reviewed journal.

19. (zhang1994mechanicalselectionof pages 3-4): J. Zhang and M. F. Ashby. Mechanical selection of foams and honeycombs used for packaging and energy absorption. Journal of Materials Science, 29:157-163, Jan 1994. URL: https://doi.org/10.1007/bf00356587, doi:10.1007/bf00356587. This article has 100 citations and is from a peer-reviewed journal.

20. (zhang1994mechanicalselectionof pages 4-5): J. Zhang and M. F. Ashby. Mechanical selection of foams and honeycombs used for packaging and energy absorption. Journal of Materials Science, 29:157-163, Jan 1994. URL: https://doi.org/10.1007/bf00356587, doi:10.1007/bf00356587. This article has 100 citations and is from a peer-reviewed journal.

21. (baysal2019preparationandcharacterization pages 66-73): P Baysal. Preparation and characterization of combustion modified polyurethane. Unknown journal, 2019.

22. (onaifo2025polyurethanefoamproduction pages 3-4): JO Onaifo, GO Otabor, and GE Onaiwu. Polyurethane foam: production processes and advanced material characterization. Tropical Journal of Chemistry, Jan 2025. URL: https://doi.org/10.71148/tjoc/v1i1.5, doi:10.71148/tjoc/v1i1.5. This article has 4 citations.

23. (aguiar2003listeningtothe pages 1-2): C. E. Aguiar and F. Laudares. Listening to the coefficient of restitution and the gravitational acceleration of a bouncing ball. American Journal of Physics, 71:499-501, Apr 2003. URL: https://doi.org/10.1119/1.1524166, doi:10.1119/1.1524166. This article has 70 citations and is from a peer-reviewed journal.

24. (aguiar2003listeningtothe pages 2-3): C. E. Aguiar and F. Laudares. Listening to the coefficient of restitution and the gravitational acceleration of a bouncing ball. American Journal of Physics, 71:499-501, Apr 2003. URL: https://doi.org/10.1119/1.1524166, doi:10.1119/1.1524166. This article has 70 citations and is from a peer-reviewed journal.

25. (duris2004experimentalandnumerical pages 21-24): JG Duris. Experimental and numerical characterization of softballs. Unknown journal, 2004.

26. (chastaing2015dynamicsofa pages 1-2): Jean-Yonnel Chastaing, E. Bertin, and Jean-Christophe G'eminard. Dynamics of a bouncing ball. American Journal of Physics, 83:518-524, Jun 2015. URL: https://doi.org/10.1119/1.4906418, doi:10.1119/1.4906418. This article has 39 citations and is from a peer-reviewed journal.

27. (chastaing2015dynamicsofa pages 2-3): Jean-Yonnel Chastaing, E. Bertin, and Jean-Christophe G'eminard. Dynamics of a bouncing ball. American Journal of Physics, 83:518-524, Jun 2015. URL: https://doi.org/10.1119/1.4906418, doi:10.1119/1.4906418. This article has 39 citations and is from a peer-reviewed journal.

28. (chastaing2015dynamicsofa pages 3-4): Jean-Yonnel Chastaing, E. Bertin, and Jean-Christophe G'eminard. Dynamics of a bouncing ball. American Journal of Physics, 83:518-524, Jun 2015. URL: https://doi.org/10.1119/1.4906418, doi:10.1119/1.4906418. This article has 39 citations and is from a peer-reviewed journal.

29. (bartz2204coefficientofrestitution pages 9-13): Sean P. Bartz. Coefficient of restitution of a linear dashpot on a rigid surface. Text, Jan 2204. URL: https://doi.org/10.48550/arxiv.2204.10917, doi:10.48550/arxiv.2204.10917. This article has 1 citations and is from a peer-reviewed journal.

30. (bartz2204coefficientofrestitution pages 1-4): Sean P. Bartz. Coefficient of restitution of a linear dashpot on a rigid surface. Text, Jan 2204. URL: https://doi.org/10.48550/arxiv.2204.10917, doi:10.48550/arxiv.2204.10917. This article has 1 citations and is from a peer-reviewed journal.

31. (turcas2019flooringstructuresdesigned pages 3-6): OM ȚURCAȘ, A Fotin, and C COȘEREANU. Flooring structures designed for sports-halls and investigated for the ball rebound test. Unknown journal, 2019.

32. (turcas2019flooringstructuresdesigned pages 6-7): OM ȚURCAȘ, A Fotin, and C COȘEREANU. Flooring structures designed for sports-halls and investigated for the ball rebound test. Unknown journal, 2019.

33. (wong2009energydissipationprediction pages 3-4): C.X. Wong, M.C. Daniel, and J.A. Rongong. Energy dissipation prediction of particle dampers. Journal of Sound and Vibration, 319:91-118, Jan 2009. URL: https://doi.org/10.1016/j.jsv.2008.06.027, doi:10.1016/j.jsv.2008.06.027. This article has 288 citations and is from a domain leading peer-reviewed journal.

34. (wong2009energydissipationprediction pages 6-8): C.X. Wong, M.C. Daniel, and J.A. Rongong. Energy dissipation prediction of particle dampers. Journal of Sound and Vibration, 319:91-118, Jan 2009. URL: https://doi.org/10.1016/j.jsv.2008.06.027, doi:10.1016/j.jsv.2008.06.027. This article has 288 citations and is from a domain leading peer-reviewed journal.

35. (wong2009energydissipationprediction pages 11-13): C.X. Wong, M.C. Daniel, and J.A. Rongong. Energy dissipation prediction of particle dampers. Journal of Sound and Vibration, 319:91-118, Jan 2009. URL: https://doi.org/10.1016/j.jsv.2008.06.027, doi:10.1016/j.jsv.2008.06.027. This article has 288 citations and is from a domain leading peer-reviewed journal.

36. (duris2004experimentalandnumericala pages 17-21): JG Duris. Experimental and numerical characterization of softballs. Unknown journal, 2004.

37. (duris2004experimentalandnumerical pages 17-21): JG Duris. Experimental and numerical characterization of softballs. Unknown journal, 2004.

38. (marchewka2021coefficientofrestitution pages 1-5): Avi Marchewka. Coefficient of restitution: derivation of newton’s experimental law from general energy considerations. Physics Education, 56:025009, Jan 2021. URL: https://doi.org/10.1088/1361-6552/abca78, doi:10.1088/1361-6552/abca78. This article has 5 citations and is from a peer-reviewed journal.

39. (bartz2204coefficientofrestitution pages 13-14): Sean P. Bartz. Coefficient of restitution of a linear dashpot on a rigid surface. Text, Jan 2204. URL: https://doi.org/10.48550/arxiv.2204.10917, doi:10.48550/arxiv.2204.10917. This article has 1 citations and is from a peer-reviewed journal.