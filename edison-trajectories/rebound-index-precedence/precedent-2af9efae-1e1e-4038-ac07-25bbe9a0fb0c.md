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

Has anyone used a first-power coefficient-of-restitution-like velocity ratio
(rebound-to-incident velocity, NOT squared into an energy fraction), or such a
ratio multiplied by a nominal impact energy scale like m*g*h, as a
standardized index, figure of merit, or optimization objective for ranking
impact-absorbing or shock-attenuating materials, structures, equipment, or
surfaces? Examples might live in rebound hardness testing, sports-equipment
and sports-surface compliance testing, packaging/cushioning, granular or
particle damping, discrete-element-model calibration, or architected-material
impact studies. Cite specific standards or papers, give the equation each one
uses, and state the justification its authors give for using a velocity ratio
(or an unorthodox composite) rather than a true energy quantity.


Yes. # Precedent for first-power restitution indices

## Bottom line

**Yes—there is strong precedent for using a first-power rebound/incident velocity ratio as a standardized index or engineering ranking variable.** The clearest formal example is **Leeb rebound hardness**, defined as

\[
HL=1000\frac{v_r}{v_i}=1000e,
\]

and standardized in the ASTM A956, DIN 50156, and ISO 16859 family. Sports-ball tests, protective-equipment studies, gravel-cushion design, surface characterization, and impact-model calibration likewise use \(e=v_r/v_i\) directly to compare rebound or attenuation behavior. These uses are justified because the ratio is dimensionless, experimentally convenient, repeatable under a fixed protocol, and sensitive to deformation, damping, and material or system construction—not because \(e\) is an energy fraction. (haron2012coefficientofrestitution pages 1-4, zsigovicsUnknownyearsurfacehardnessand pages 52-54, perkins2019effectofpneumatic pages 32-33, zhu2018theeffectsof pages 2-3)

**I did not find a verified standard or paper in the searched literature that establishes \(e\,mgh\), with first-power \(e\), as returned energy or as a standard impact-absorption metric.** Sources that explicitly convert a velocity COR into energy use \(e^2\), or \(1-e^2\) for dissipated kinetic energy. Thus, the T3 quantity

\[
\lambda=\left(\frac{v_{\rm sep}}{\Delta v_{\rm plate}}\right)mgh
\]

has defensible precedent as an **empirical velocity-weighted index**, but not as an energy quantity. It is more unconventional than ordinary COR because its numerator and denominator belong to different bodies or interfaces and because its energy scale uses the whole printed specimen mass rather than the actually flying subassembly.

| Precedent / source / domain | Exact equation | How used | Authors’ stated justification | Relationship to true energy | Closeness to T3 lambda |
|---|---|---|---|---|---|
| **Leeb rebound hardness**; ASTM A956, DIN 50156, ISO 16859 family | `HL = 1000(vr/vi) = 1000e` | Standardized hardness index for metals; also used empirically to rank rocks and estimate strength. | The rebound-to-incident velocity quotient provides a rapid, portable measure sensitive to surface hardness; standardization fixes the impact device and procedure. | It is a first-power velocity index. For the same impactor, the rebound kinetic-energy fraction would be `(vr/vi)^2 = e^2`, not `e`. | **Strong precedent for scaling a first-power velocity ratio into an index; weak precedent for lambda.** HL is dimensionless and concerns one impactor and interface. (zsigovicsUnknownyearsurfacehardnessand pages 52-54, yamamoto2012proofexaminationon pages 1-2) |
| **Sports-ball normal-impact COR**; Haron and Ismail (2012); regulatory examples include ASTM F1887, BS 5993, and ITF rigid-block methods | `e = vr/vi`; for an ideal no-drag drop, `e = sqrt(hr/hi)` | Ball or ball–surface rebound characterization and comparison; approval rules often specify rebound-height ranges. | COR is a compact descriptor of normal rebound, material or construction effects, and collision-model behavior. A rigid reference surface improves repeatability and attributes most deformation loss to the ball. | The returned translational-energy fraction is `e^2 = hr/hi`. The literature distinguishes Newton’s velocity COR from energy-based restitution. | **Strong precedent for ranking with first-power COR, but not for multiplying it by nominal energy.** Incident and rebound velocities normally describe the same ball and interface. (haron2012coefficientofrestitution pages 1-4, lubarda2024inelasticbouncingof pages 9-11, collins2011parametricimpactcharacterisation pages 36-40) |
| **Pneumatic boxing gloves**; Perkins et al. (2019) | `ek = vr,max/vi,max` | Experimental ranking of conventional and pneumatic gloves across drop heights; lower COR was interpreted as greater dissipation. | Retained rebound velocity distinguished glove constructions and impact regimes. The vented pneumatic glove was most dissipative at low-to-moderate energies, but not at the highest energies. | COR is not itself energy. A same-mass kinetic-energy comparison would depend on `ek^2`; the qualitative interpretation does not make `ek` an energy fraction. | **Moderately close application precedent:** protective equipment is ranked with first-power rebound COR, but no `e mgh` objective is used. (perkins2019effectofpneumatic pages 32-33) |
| **Gravel cushions for rockfall protection**; Zhu et al. (2018) | `VCOR = V1/V`; `Rn = Vn1/Vn`; `Rt = Vt1/Vt`; energy coefficient `ETCOR = VCOR^2` under the stated approximation | COR was an orthogonal-test evaluation index for ranking cushion thickness, particle size, release height, and block radius; minimum COR identified favorable buffering conditions. | Lower COR denotes less rebound and stronger buffering. Thickness was the primary design variable; particle size required balancing attenuation against cushion damage and stability. | The authors square velocity COR when forming an energy coefficient and also consider translational and rotational energy. They do not use `e mgh`. | **Very close in engineering purpose** because an impact cushion is ranked by first-power COR, but **contrary as energy precedent** because conversion to energy uses `e^2`. (zhu2018theeffectsof pages 2-3, zhu2018theeffectsof pages 1-2, zhu2018theeffectsof pages 10-12) |
| **Hoof-wall impacts on steel, concrete, and asphalt**; Zhao et al. (2020) | `en = abs(vn,after)/abs(vn,before)` | Surface ranking by mean COR: steel `0.84`, concrete `0.72`, asphalt `0.51`. | Smaller COR was interpreted as less rebound and greater dissipation into the surface; COR also informed the compression–restitution contact model. | Physical kinetic-energy partition is quadratic in speed. The retrieved text does not treat `e` as an energy fraction or use `e mgh`. | **Moderate precedent for ranking surfaces by first-power COR; weak analogy to lambda** because the same hoof supplies both measured velocities. (zhao2020impactofhorse pages 9-11, zhao2020impactofhorse pages 3-5) |
| **Sports-ball spring–damper impact model**; Collins (2011) | `COR = vr/vi = exp[-cTc/(2m)]`; therefore `c = -(2m/Tc) ln(COR)` | Model parameterization: measured COR and contact time determine equivalent viscous damping for predicting ball behavior. | COR converts an observable rebound-speed ratio into a damping parameter, supporting prediction, prototype selection, and ball–surface or equipment models. | COR is a constitutive or calibration parameter, not energy. Corresponding energy fractions involve `COR^2`. | **Useful precedent for operational use of first-power COR rather than energetic use; no precedent for `COR mgh`.** (collins2011parametricimpactcharacterisation pages 250-253, collins2011parametricimpactcharacterisation pages 69-73) |
| **Overall result of the targeted search** | T3 index: `lambda = (vsep/delta-v) mgh` | Dimensional optimization and ranking index combining a vertex-flight velocity ratio with the specimen’s nominal drop-energy scale. | Such a composite can be presented as an empirical scalarization or velocity-weighted severity index if its repeatability, ranking utility, and normalization are demonstrated; it should not be called returned kinetic energy. | Because the numerator and denominator concern different bodies or interfaces, even `e^2 mgh` would not automatically equal returned energy. Verified energy treatments use the actually moving mass and squared speed. | **No verified standard or paper in the searched domains used first-power `e mgh` as a standard returned-energy measure or established absorption objective.** The closest precedents support standalone first-power COR indices, not this dimensional composite. (haron2012coefficientofrestitution pages 1-4, lubarda2024inelasticbouncingof pages 9-11, zsigovicsUnknownyearsurfacehardnessand pages 52-54, zhu2018theeffectsof pages 2-3) |


*Table: Comparison of standardized and application-specific first-power restitution measures with the proposed T3 velocity-weighted impact-energy index. It distinguishes operational velocity-ratio precedents from true energy calculations, which use squared velocity ratios.*

## Specific precedents and their justifications

### 1. Leeb hardness: an exact standardized first-power index

Leeb hardness is the strongest precedent for deliberately retaining the first power of a velocity ratio:

\[
HL=1000\frac{v_r}{v_i}.
\]

The multiplier 1000 creates a convenient hardness scale; it does not convert the quotient into energy. The method treats rebound response as an operational measure of surface hardness under a specified impactor and procedure. Its practical rationale is portable, rapid testing and empirical correlation with hardness or strength. The literature also stresses that impact velocity, plastic deformation, specimen mass, support, and surface heterogeneity can affect the result—hence the need for standardized devices and protocols. (zsigovicsUnknownyearsurfacehardnessand pages 52-54, yamamoto2012proofexaminationon pages 1-2, asiri2017standardizedprocessfor pages 24-29)

This is a close conceptual precedent for naming \(\lambda\) an **index**: Leeb hardness assigns engineering meaning to a scaled first-power velocity quotient without claiming that the quotient is an energy fraction. It is not, however, precedent for attaching joule units by multiplying that quotient by \(mgh\).

### 2. Sports balls and surfaces: COR as the standard rebound descriptor

Haron and Ismail define normal COR as

\[
e=\frac{v_{\rm rebound}}{v_{\rm incident}},
\]

and use it to compare golf, table-tennis, hockey, and cricket balls on different targets. Their justification is the traditional Newtonian one: COR compactly describes normal separation relative to approach and is associated with collision inelasticity, material construction, and plastic or viscoelastic losses. They explicitly distinguish this velocity definition from energy-based restitution, for which an energy ratio corresponds to \(e^2\). (haron2012coefficientofrestitution pages 1-4)

For an ideal drop test without aerodynamic losses,

\[
e=\sqrt{\frac{h_r}{h_i}},\qquad
\frac{E_r}{E_i}=\frac{h_r}{h_i}=e^2.
\]

Regulatory ball tests commonly specify rebound-height windows; Lubarda and Lubarda, for example, convert a tennis-ball rebound-height requirement into a COR interval. They separately write impact energy loss as

\[
E_{\rm loss,impact}=\frac12m(1-e^2)v_i^2,
\]

which confirms that first-power COR is the rebound-performance descriptor while the square enters energy accounting. (lubarda2024inelasticbouncingof pages 9-11)

Rigid reference targets are justified by repeatability and comparability: if the target is effectively noncompliant, most measured loss can be attributed to the ball. Collins identifies ASTM F1887, BS 5993, and the International Tennis Federation granite-block method as examples of this approach. Real sports surfaces introduce compliance, friction, moisture, preparation, and degradation effects, making measurements more system- and apparatus-specific. (collins2011parametricimpactcharacterisation pages 36-40)

### 3. Protective equipment: boxing gloves ranked by first-power COR

Perkins et al. computed a kinematic COR using peak rebound and pre-impact glove velocities,

\[
e_k=\frac{v_{r,\max}}{v_{i,\max}},
\]

and used it to compare conventional and pneumatic boxing gloves over multiple drop heights. Lower COR was interpreted operationally as greater dissipation: the vented pneumatic glove performed best at low-to-moderate impact energies, whereas the sealed pneumatic glove retained more rebound over much of the range. The rationale was that retained rebound velocity discriminated glove constructions and revealed changes with impact severity, including bladder-pressure and possible foam-degradation effects. (perkins2019effectofpneumatic pages 32-33)

This is a direct precedent for **ranking protective equipment using first-power COR**, but the study does not make \(e_k\) an energy fraction or multiply it by \(mgh\).

### 4. Gravel rockfall cushions: COR used as a design objective

Zhu et al. define

\[
V_{\rm COR}=\frac{V_1}{V},\qquad
R_n=\frac{V_{n1}}{V_n},\qquad
R_t=\frac{V_{t1}}{V_t},
\]

where the subscript 1 denotes rebound. They use COR as an evaluation index in an orthogonal experimental design to rank block radius, release height, cushion thickness, and gravel particle size. Their minimum-COR combination represented favorable buffering; cushion thickness had the largest influence, followed by particle size, release height, and block radius. Lower COR was justified as indicating less rebound and stronger buffering, while cushion damage and stability were evaluated separately. (zhu2018theeffectsof pages 1-2, zhu2018theeffectsof pages 10-12, zhu2018theeffectsof pages 9-10)

Crucially, when Zhu et al. introduce an energy coefficient, they use

\[
ET_{\rm COR}=V_{\rm COR}^{2}

after the stated translational/rotational approximation—not first-power COR. Their physical rationale is that gravel absorbs rockfall energy and reduces loading on protective structures; their design rationale balances low COR against cushion durability and economic constraints. (zhu2018theeffectsof pages 2-3, zhu2018theeffectsof pages 12-13)

This is probably the closest precedent in **engineering purpose** to the T3 campaign: a shock-buffering structure is ranked and designed partly by minimizing a first-power rebound ratio. It is simultaneously evidence against interpreting \(e\,mgh\) as energy.

### 5. Surface compliance and attenuation

Zhao et al. compared hoof impacts on steel, concrete, and asphalt using COR. Mean values ranked steel \(0.84\), concrete \(0.72\), and asphalt \(0.51\). They interpreted the smaller asphalt value as less rebound and greater dissipation into the surface. The stated reasoning was an impact-energy partition between rebound motion and deformation or loss in the ground. COR was also useful for calibrating their compression–restitution contact model. (zhao2020impactofhorse pages 9-11, zhao2020impactofhorse pages 3-5)

Again, COR itself was the comparative response variable; it was not represented as an energy fraction.

### 6. COR as a model-calibration quantity

In a damped sports-ball impact model, Collins obtains

\[
COR=\frac{v_r}{v_i}=
\exp\!\left(-\frac{cT_c}{2m}\right),
\]

and therefore

\[
c=-\frac{2m}{T_c}\ln(COR).
\]

The justification is operational: measured rebound speed and contact time identify an equivalent damping parameter, enabling prediction, prototype selection, and ball–surface or equipment modeling. (collins2011parametricimpactcharacterisation pages 250-253, collins2011parametricimpactcharacterisation pages 69-73)

This is representative of DEM and impact-model practice: first-power COR is retained because collision laws act on relative velocities and because it is directly measurable. It is a constitutive or calibration parameter, not an energy measure.

## What the precedent supports—and does not support—for the T3 index

The literature supports the following claims:

1. **First-power velocity ratios are legitimate engineering indices.** Leeb hardness is an explicit standardized example; sports, cushioning, and protective-equipment studies use COR directly for comparison and design.
2. **A first-power ratio may be preferable operationally** because it is directly measured, monotonic with rebound, dimensionless, and often more convenient for calibration or acceptance limits than a derived energy estimate.
3. **Minimizing a first-power rebound ratio can be a valid empirical objective** when low rebound is one desired aspect of attenuation, as in gravel cushions and pneumatic gloves.
4. **Such a ratio should not be called an energy fraction.** Where the same mass has incident and rebound speeds \(v_i\) and \(v_r\), the rebound kinetic-energy fraction is \(e^2\), not \(e\). (haron2012coefficientofrestitution pages 1-4, lubarda2024inelasticbouncingof pages 9-11, zhu2018theeffectsof pages 2-3)

The literature does **not** establish that multiplying first-power COR by nominal drop energy creates a standardized energy metric. For the T3 experiment the mismatch is greater than in conventional restitution testing:

\[
e_{T3}=\frac{v_{\rm sep,vertex}}{\Delta v_{\rm plate}}
\]

is not Newtonian COR for one colliding pair, because the numerator is inferred from the later ballistic flight of a vertex subassembly while the denominator is the arrest velocity change of the carrier plate. Multiplication by whole-specimen \(mgh\) introduces another body/mass convention. Therefore neither \(e_{T3}\) nor \(e_{T3}^2\) automatically represents a returned-energy fraction.

## Recommended characterization

The most defensible description is:

> **Velocity-weighted impact-energy index:** an empirical, dimensional ranking metric obtained by weighting the nominal specimen drop-energy scale \(mgh\) by the measured vertex-separation/plate-arrest velocity ratio.

Its justification should be stated in measurement and optimization terms: it combines specimen mass with a monotonic measure of post-pulse vertex separation; it preserves sensitivity across the tested design family; and, together with transmitted-shock peak ratio, it supplies a second Pareto objective. It should be accompanied by the explicit disclaimer that it is **not returned kinetic energy, absorbed energy, or an energy fraction**.

Accordingly, the precedent is **strong for the first-power ratio as an index and ranking objective, moderate for its use in impact-absorber optimization, and absent in the verified literature for the exact composite \(e\,mgh\)**.

References

1. (haron2012coefficientofrestitution pages 1-4): Adli Haron and K A Ismail. Coefficient of restitution of sports balls: a normal drop test. IOP Conference Series: Materials Science and Engineering, 36:012038, Sep 2012. URL: https://doi.org/10.1088/1757-899x/36/1/012038, doi:10.1088/1757-899x/36/1/012038. This article has 68 citations.

2. (zsigovicsUnknownyearsurfacehardnessand pages 52-54): KSABI Zsigovics. Surface hardness and related properties of concrete. Unknown journal, Unknown year.

3. (perkins2019effectofpneumatic pages 32-33): Paul Perkins, Alex Jamieson, Wayne Spratford, and Allan Hahn. Effect of pneumatic boxing gloves on impact kinematics and their relationship to impact forces. World Journal of Engineering and Technology, 07:472-512, Jul 2019. URL: https://doi.org/10.4236/wjet.2019.73035, doi:10.4236/wjet.2019.73035. This article has 3 citations.

4. (zhu2018theeffectsof pages 2-3): Chun Zhu, Dongsheng Wang, Xing Xia, Zhigang Tao, Manchao He, and Chen Cao. The effects of gravel cushion particle size and thickness on the coefficient of restitution in rockfall impacts. Natural Hazards and Earth System Sciences, 18:1811-1823, Jun 2018. URL: https://doi.org/10.5194/nhess-18-1811-2018, doi:10.5194/nhess-18-1811-2018. This article has 39 citations and is from a peer-reviewed journal.

5. (yamamoto2012proofexaminationon pages 1-2): M Yamamoto, T Yamamoto, K Miyahara, and S Maki. Proof examination on small rebound hardness carried out with hld/hle standard blocks. Unknown journal, 2012.

6. (lubarda2024inelasticbouncingof pages 9-11): Marko V. Lubarda and Vlado A. Lubarda. Inelastic bouncing of a spherical ball in the presence of quadratic drag with application to sports balls. Proceedings of the Institution of Mechanical Engineers, Part P: Journal of Sports Engineering and Technology, 238:3-14, Apr 2024. URL: https://doi.org/10.1177/17543371221086190, doi:10.1177/17543371221086190. This article has 2 citations.

7. (collins2011parametricimpactcharacterisation pages 36-40): F Collins. Parametric impact characterisation of a solid sports ball, with a view to developing a standard core for the gaa sliotar. Unknown journal, 2011.

8. (zhu2018theeffectsof pages 1-2): Chun Zhu, Dongsheng Wang, Xing Xia, Zhigang Tao, Manchao He, and Chen Cao. The effects of gravel cushion particle size and thickness on the coefficient of restitution in rockfall impacts. Natural Hazards and Earth System Sciences, 18:1811-1823, Jun 2018. URL: https://doi.org/10.5194/nhess-18-1811-2018, doi:10.5194/nhess-18-1811-2018. This article has 39 citations and is from a peer-reviewed journal.

9. (zhu2018theeffectsof pages 10-12): Chun Zhu, Dongsheng Wang, Xing Xia, Zhigang Tao, Manchao He, and Chen Cao. The effects of gravel cushion particle size and thickness on the coefficient of restitution in rockfall impacts. Natural Hazards and Earth System Sciences, 18:1811-1823, Jun 2018. URL: https://doi.org/10.5194/nhess-18-1811-2018, doi:10.5194/nhess-18-1811-2018. This article has 39 citations and is from a peer-reviewed journal.

10. (zhao2020impactofhorse pages 9-11): Jing Zhao, Dan B. Marghitu, John Schumacher, and Wenzhong Wang. Impact of horse hoof wall with different solid surfaces. Applied Sciences, 10:8743, Dec 2020. URL: https://doi.org/10.3390/app10238743, doi:10.3390/app10238743. This article has 1 citations.

11. (zhao2020impactofhorse pages 3-5): Jing Zhao, Dan B. Marghitu, John Schumacher, and Wenzhong Wang. Impact of horse hoof wall with different solid surfaces. Applied Sciences, 10:8743, Dec 2020. URL: https://doi.org/10.3390/app10238743, doi:10.3390/app10238743. This article has 1 citations.

12. (collins2011parametricimpactcharacterisation pages 250-253): F Collins. Parametric impact characterisation of a solid sports ball, with a view to developing a standard core for the gaa sliotar. Unknown journal, 2011.

13. (collins2011parametricimpactcharacterisation pages 69-73): F Collins. Parametric impact characterisation of a solid sports ball, with a view to developing a standard core for the gaa sliotar. Unknown journal, 2011.

14. (asiri2017standardizedprocessfor pages 24-29): Y Asiri. Standardized process for filed estimation of unconfined compressive strength using leeb hardness. Unknown journal, 2017.

15. (zhu2018theeffectsof pages 9-10): Chun Zhu, Dongsheng Wang, Xing Xia, Zhigang Tao, Manchao He, and Chen Cao. The effects of gravel cushion particle size and thickness on the coefficient of restitution in rockfall impacts. Natural Hazards and Earth System Sciences, 18:1811-1823, Jun 2018. URL: https://doi.org/10.5194/nhess-18-1811-2018, doi:10.5194/nhess-18-1811-2018. This article has 39 citations and is from a peer-reviewed journal.

16. (zhu2018theeffectsof pages 12-13): Chun Zhu, Dongsheng Wang, Xing Xia, Zhigang Tao, Manchao He, and Chen Cao. The effects of gravel cushion particle size and thickness on the coefficient of restitution in rockfall impacts. Natural Hazards and Earth System Sciences, 18:1811-1823, Jun 2018. URL: https://doi.org/10.5194/nhess-18-1811-2018, doi:10.5194/nhess-18-1811-2018. This article has 39 citations and is from a peer-reviewed journal.