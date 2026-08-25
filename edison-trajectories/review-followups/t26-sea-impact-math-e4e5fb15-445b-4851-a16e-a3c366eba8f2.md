# Edison trajectory -- t26-sea-impact-math

Task ID: `e4e5fb15-445b-4851-a16e-a3c366eba8f2`  
Status: success

---

Question: 
I am writing a mechanical-engineering manuscript on multi-material 3D-printed
tensegrity-inspired energy absorbers, characterized with (i) quasi-static
compression on a benchtop load frame and (ii) drop-weight impact on an
instrumented drop tower. Please sanity-check the following metric definitions and
methodology, and recommend best practice with citations.

Reported quasi-static metrics (F = force, delta = displacement, m = specimen
mass, delta_d = densification displacement, F_max = peak transmitted force):

  SEA = (1/m) * integral_0^{delta_d} F(delta) d(delta)              [specific energy absorption]
  eta_c = integral_0^{delta_d} F(delta) d(delta) / (F_max * delta_d) [compaction efficiency]

Questions:
(a) Are these the standard textbook definitions of specific energy absorption and
    compaction (stroke / cushioning) efficiency for cellular / architected energy
    absorbers? Flag any sign, normalization, or limit-of-integration issues, and
    give the canonical references (e.g., Gibson & Ashby; Avalle; Tan; SAE/ISO/ASTM
    cushioning standards).
(b) For the drop-weight impact test, what is the correct way to define and extract
    the "peak transmitted force" / peak acceleration from an instrumented drop?
    Specifically address: anti-alias / low-pass filtering per SAE J211 (CFC-60 /
    CFC-180 / CFC-1000), the danger of reporting a raw (ringing-dominated) global
    peak vs. a windowed peak search around the true impact event, sensor
    saturation/clipping, and single-axis vs. tri-axis resultant.
(c) Our own drop-test analysis found that a windowed peak search (around the
    impact event, ~first few ms) with CFC-180 filtering changes the answer
    substantially relative to a naive global 0.2 s maximum (which can be dominated
    by post-impact mount oscillation), and that an analog-saturating single-axis
    sensor should be replaced with a higher-range one. Is this consistent with
    best practice, and how should SEA / peak-force be related to the
    accelerometer-derived signals?

Give a concise, citable verdict for each point.


# Sanity-Check of Metric Definitions and Impact-Test Methodology for Multi-Material 3D-Printed Tensegrity Energy Absorbers

## (a) Quasi-Static Metrics: SEA and Compaction Efficiency

### Specific Energy Absorption (SEA)

The reported definition — SEA = (1/m) ∫₀^{δ_d} F(δ) dδ — is **correct and standard**. The canonical form in the cellular-materials literature expresses volumetric absorbed energy as the area under the stress–strain curve, W(ε) = ∫₀^{ε_d} σ(ε) dε, and specific (mass-normalized) energy absorption as that quantity divided by apparent density (equivalently, force–displacement integral divided by specimen mass) (avalle2001characterizationofpolymeric pages 1-5, avalle2001characterizationofpolymeric pages 5-8). Tan et al. define absorbed energy per unit volume as W = ∫₀^{ε_a} σ dε and use it as the basis for efficiency calculations (tan2005dynamiccompressivestrength pages 15-17). Avalle, Belingardi & Montanini use the same integral and energy-absorption diagrams to characterize polymeric foams under quasi-static and impact loading (avalle2001characterizationofpolymeric pages 8-11, avalle2001characterizationofpolymeric pages 5-8). There is no sign or normalization issue provided compression force and displacement are taken as positive magnitudes and the upper limit is the densification displacement.

**Key caveat – upper integration limit.** The densification displacement δ_d (or equivalently densification strain ε_d) must be defined objectively. The most widely accepted method, following Tan et al. (2005), is to locate the strain at which the energy-absorption efficiency–strain curve reaches a stationary maximum, i.e. dη/dε|_{ε=ε_d} = 0 (tan2005dynamiccompressivestrength pages 15-17). Michailidis et al. corroborate this and note alternative criteria including the tangent-intersection method and the strain at which stress rises to 1.3–1.5× the plateau stress (michailidis2011deformationandenergy pages 2-3, michailidis2011deformationandenergy pages 1-2). The efficiency-maximum method is recommended as the most objective and reproducible.

### Compaction (Crushing / Ideality) Efficiency (η_c)

The reported formula — η_c = ∫₀^{δ_d} F(δ) dδ / (F_max · δ_d) — is **correct in form**, matching the "ideality" or "crush efficiency" ratio used in the literature: the ratio of absorbed energy to the area of the ideal rectangular absorber having the same peak force and stroke (michailidis2011deformationandenergy pages 2-3, avalle2001characterizationofpolymeric pages 8-11). An ideal (perfectly plastic) absorber yields η_c = 1.

**Important distinction.** Some authors define a running efficiency E(ε_f) = ∫₀^{ε_f} σ dε / σ(ε_f), which is a function of the current strain and is used to locate densification onset, not to report a single-number crush efficiency (ozturk2009energyabsorptioncalculations pages 2-4, tan2005dynamiccompressivestrength pages 15-17). The user's definition is the final ideality ratio evaluated at densification, not the running form. These must not be conflated. In the user's formula, F_max must be the maximum force recorded within the integration window [0, δ_d]; using a post-densification peak or a global maximum from outside this interval would underestimate efficiency.

The following table summarizes the comparison of the user's definitions against the canonical literature:

| Metric / issue | User definition | Canonical / standard definition in literature | Verdict |
|---|---|---|---|
| SEA (specific energy absorption) | \(SEA=\frac{1}{m}\int_0^{\delta_d}F(\delta)\,d\delta\) | Canonically, absorbed energy is the area under the force–displacement curve up to a specified deformation limit; mass-normalized SEA is that energy divided by specimen mass. In stress–strain form, \(W=\int_0^{\varepsilon_d}\sigma(\varepsilon)\,d\varepsilon\), and mass-normalized SEA follows by dividing by apparent density or mass. Using \(\delta_d\) as the upper limit is standard when reporting SEA up to densification; equivalently \(\delta_d=\varepsilon_d H_0\). (avalle2001characterizationofpolymeric pages 5-8, avalle2001characterizationofpolymeric pages 1-5, tan2005dynamiccompressivestrength pages 15-17) | **Correct.** No sign issue if compression force and displacement are taken as positive magnitudes. State explicitly that the upper limit is the densification displacement, or report SEA to a fixed strain if not using densification. |
| \(\eta_c\) compaction / crushing / ideality efficiency | \(\eta_c=\frac{\int_0^{\delta_d}F(\delta)\,d\delta}{F_{\max}\,\delta_d}\) | A standard “ideality” / crush-efficiency form is absorbed energy divided by the rectangle defined by the **maximum force within the interval** and the crush stroke: in stress–strain form \(\eta=\frac{\int_0^{\varepsilon_d}\sigma(\varepsilon)\,d\varepsilon}{\sigma_{\max}\,\varepsilon_d}\). This is equivalent to your expression in force–displacement variables. However, some papers define a **running efficiency** as \(E(\varepsilon_f)=\frac{\int_0^{\varepsilon_f}\sigma d\varepsilon}{\sigma(\varepsilon_f)}\) or related forms, which is used to locate densification and is not the same quantity as your final compaction efficiency. (michailidis2011deformationandenergy pages 2-3, avalle2001characterizationofpolymeric pages 8-11, ozturk2009energyabsorptioncalculations pages 2-4, michailidis2011deformationandenergy pages 1-2) | **Correct if** \(F_{\max}\) is defined as the **maximum force on \([0,\delta_d]\)**, not a raw post-densification or post-impact global peak outside the interval. Clarify terminology because some authors use “efficiency” for the running quantity rather than the final ideality ratio. |
| Densification strain / displacement \((\varepsilon_d,\delta_d)\) | Implicitly assumes \(\delta_d\) is known | Recommended objective method: determine \(\varepsilon_d\) at the maximum of the efficiency–strain curve, i.e. where \(d\eta/d\varepsilon=0\); then convert to displacement by \(\delta_d=\varepsilon_d H_0\). Alternatives used in the literature include tangent-intersection constructions and approximate criteria such as stress rising to about 1.3–1.5 times plateau stress. (tan2005dynamiccompressivestrength pages 15-17, michailidis2011deformationandenergy pages 2-3, michailidis2011deformationandenergy pages 1-2) | **Best practice:** use the **efficiency-maximum method** as primary, and if desired report a sensitivity check versus tangent-intersection or plateau-stress criteria. This is the most objective and reproducible way to define \(\delta_d\). |


*Table: This table compares the manuscript’s SEA, compaction-efficiency, and densification definitions against canonical literature usage. It highlights that the formulas are essentially standard, while clarifying the key caveat about how F_max and densification should be defined.*

**Canonical references for (a):** Gibson & Ashby, *Cellular Solids* (Cambridge, 2nd ed., 1997); Avalle, Belingardi & Montanini, *Int. J. Impact Eng.* 25 (2001) 455–472 (avalle2001characterizationofpolymeric pages 8-11, avalle2001characterizationofpolymeric pages 5-8); Tan et al., *J. Mech. Phys. Solids* 53 (2005) 2174–2205 (tan2005dynamiccompressivestrength pages 15-17); Michailidis et al., *Mater. Sci. Eng. A* 528 (2011) 7222–7227 (michailidis2011deformationandenergy pages 1-2, michailidis2011deformationandenergy pages 2-3); Ozturk & Anlas, *Mater. Des.* 30 (2009) 15–22 (ozturk2009energyabsorptioncalculations pages 2-4). For packaging cushion testing, ASTM D1596 defines dynamic-cushion curves using peak deceleration vs. static stress (grabowskiUnknownyeardesignandevaluation pages 82-84).

---

## (b) Peak Transmitted Force / Peak Acceleration from an Instrumented Drop Test

### SAE J211 CFC filtering

SAE J211 specifies four Channel Frequency Classes (CFC) for low-pass filtering impact acceleration signals: CFC-60, CFC-180, CFC-600, and CFC-1000. The Butterworth −3 dB corner frequency equals CFC/0.6, so CFC-60 → 100 Hz, CFC-180 → 300 Hz, CFC-600 → 1000 Hz, and CFC-1000 → 1650 Hz (alem1995designofdigital pages 5-8, alem1995designofdigital pages 8-13). The standard specifies a 4th-order (24 dB/octave roll-off) Butterworth filter, implemented as two cascaded second-order sections (alem1995designofdigital pages 28-33, alem1995designofdigital pages 15-18). A phaseless (zero-phase, forward-backward) implementation is recommended for post-processing to avoid time shifts (alem1995designofdigital pages 8-13).

| CFC designation | Butterworth corner frequency (−3 dB) | Typical application / measurement type | Roll-off slope |
|---|---:|---|---:|
| CFC-60 | 100 Hz | Low-bandwidth crash / shock channels; often associated with vehicle deceleration and other relatively low-frequency impact-response measurements (alem1995designofdigital pages 5-8, alem1995designofdigital pages 8-13, alem1995designofdigital pages 15-18) | 24 dB/octave, 4th-order Butterworth (alem1995designofdigital pages 5-8, alem1995designofdigital pages 8-13, alem1995designofdigital pages 15-18) |
| CFC-180 | 300 Hz | Intermediate-bandwidth impact acceleration channels; commonly used where impact duration is a few milliseconds and moderate smoothing is needed without excessive attenuation of the main event (alem1995designofdigital pages 5-8, alem1995designofdigital pages 8-13, gellner2024optimalheadimpacta pages 23-26, gellner2024optimalheadimpact pages 30-32) | 24 dB/octave, 4th-order Butterworth (alem1995designofdigital pages 5-8, alem1995designofdigital pages 8-13, alem1995designofdigital pages 15-18) |
| CFC-600 | 1000 Hz | Higher-bandwidth impact force / acceleration channels where sharper transient content must be retained (alem1995designofdigital pages 5-8, alem1995designofdigital pages 21-24, arteagaperez2018filtrodecapacitores pages 2-4) | 24 dB/octave, 4th-order Butterworth (alem1995designofdigital pages 5-8, alem1995designofdigital pages 8-13, arteagaperez2018filtrodecapacitores pages 2-4) |
| CFC-1000 | 1650 Hz | Very high-bandwidth impact channels / reference accelerometer processing where maximum transient fidelity is needed before stronger post-processing choices (alem1995designofdigital pages 5-8, alem1995designofdigital pages 8-13, alem1995designofdigital pages 21-24, gellner2024optimalheadimpacta pages 23-26) | 24 dB/octave, 4th-order Butterworth (alem1995designofdigital pages 5-8, alem1995designofdigital pages 8-13, arteagaperez2018filtrodecapacitores pages 2-4) |


*Table: This table summarizes the SAE J211 Channel Frequency Classes discussed in the evidence base, including the Butterworth −3 dB corner frequencies obtained from the CFC/0.6 relation and the standard 4th-order, 24 dB/octave roll-off. It is useful for choosing and reporting impact-test filtering consistently.*

**CFC class selection.** For structural impact testing of energy absorbers where impact duration is on the order of a few milliseconds, CFC-180 (300 Hz corner) provides an appropriate balance: it removes high-frequency ringing and fixture resonance while preserving the true impact pulse shape (gellner2024optimalheadimpacta pages 23-26, gellner2024optimalheadimpact pages 30-32). Gellner et al. (2024) systematically optimized filter cutoff frequencies for impact acceleration signals and found that 300 Hz (CFC-180) minimized both mean bias and variance in peak acceleration estimates for short-duration (3–7 ms) impacts (gellner2024optimalheadimpacta pages 23-26, gellner2024optimalheadimpact pages 26-30). CFC-1000 (1650 Hz) is typically used only for reference/ground-truth laboratory headform measurements (gellner2024optimalheadimpact pages 23-26).

### Raw global peak vs. windowed peak search

Reporting the raw (unwindowed) global maximum over the full acquisition record is **dangerous and non-standard**. Drop-weight accelerometer signals contain contributions from impactor ringing, structural vibration modes of the fixture, and post-impact rebound oscillations that can persist well after the contact event (aymerich2026aninstrumenteddropweight pages 4-8, found1998interpretationofsignals pages 1-2). Found et al. (1998) show that ringing is inherent in impact records, that ringing amplitude scales with impact velocity, and that a spring-mass model should guide separation of the impact impulse from fixture vibrations (found1998interpretationofsignals pages 1-2). They explicitly recommend saving unfiltered data and using model-guided filtering/windowing to isolate the true contact event (found1998interpretationofsignals pages 1-2). Gellner et al. (2024) demonstrated that different post-processing and peak-selection strategies can cause peak values to differ by up to 391% at the 95th percentile, with extreme outliers often being unrealistic fixture artifacts (gellner2024optimalheadimpact pages 116-121).

**Best practice:** Identify the impact event from the trigger or velocity-zero crossing, define a time window encompassing the primary contact pulse (typically the first few milliseconds for short-duration impacts), and extract the peak within that window after filtering.

### Sensor saturation and clipping

IEPE/ICP piezoelectric accelerometers undergo "soft-clipping" when their internal electronics exceed the rated output range (typically ±5 V), even though the data acquisition system may accept ±10 V without flagging an overload (zobel2026historyworkingprinciple pages 1-4, zobel2026historyworkingprinciple pages 9-11). Soft-clipping attenuates negative acceleration peaks, produces asymmetric waveforms, and requires several seconds of recovery time (zobel2026historyworkingprinciple pages 23-25, zobel2026historyworkingprinciple pages 11-13). In impact/shock tests, soft-clipping primarily affects the initial response peaks and can obscure rapidly decaying high-frequency modes (zobel2026historyworkingprinciple pages 13-16, zobel2026historyworkingprinciple pages 1-4). Because the DAQ system provides no overload warning when the sensor (not the system) is saturated, corrupted data can appear plausible (zobel2026historyworkingprinciple pages 9-11). A higher-range accelerometer (e.g., ±50 g instead of ±5 g) avoids this problem entirely (zobel2026historyworkingprinciple pages 13-16). Kargl et al. similarly warn that amplifier saturation during impact produces clipping, long transients, and biased peak readings (kargl2001accelerometrymeasurementsusing pages 4-5).

### Single-axis vs. tri-axis resultant

For a uniaxial drop test where the specimen is loaded primarily along the drop axis, a single-axis accelerometer aligned with the drop direction is sufficient and commonly used — Pajunen et al. (2019) used this approach for 3D-printed tensegrity structures (pajunen2019designandimpact pages 4-5). However, if the specimen geometry induces off-axis forces (e.g., asymmetric buckling, lateral expansion), the single-axis reading will underestimate the true resultant peak. Where off-axis motion is suspected, a tri-axial accelerometer should be used and the resultant computed as a_R = √(a_x² + a_y² + a_z²). Gellner et al. (2024) compute peak resultant linear acceleration from tri-axial data as the primary metric (gellner2024optimalheadimpact pages 37-40, gellner2024optimalheadimpacta pages 23-26).

---

## (c) Validation of Windowed CFC-180 Analysis and Sensor Replacement

### Windowed peak search with CFC-180 filtering

The finding that a windowed peak search around the impact event (~first few ms) with CFC-180 filtering changes the answer substantially relative to a naive global 0.2 s maximum is **fully consistent with best practice**. Found et al. (1998) demonstrate that impact energy excites panel and fixture vibrations that "persist well after the impact event," meaning a global maximum over a long window will often capture mount/fixture oscillation rather than the true contact-event peak (found1998interpretationofsignals pages 4-7, found1998interpretationofsignals pages 1-2). The CFC-180 (300 Hz) filter is appropriate for removing high-frequency ringing while preserving the main impact pulse for events lasting a few milliseconds (gellner2024optimalheadimpacta pages 23-26, gellner2024optimalheadimpact pages 30-32). Gellner et al.'s systematic optimization specifically recommends CFC-180 as optimal for such short-duration impacts and notes that different processing strategies can change peak values by hundreds of percent (gellner2024optimalheadimpact pages 116-121, gellner2024optimalheadimpacta pages 23-26).

### Replacing a saturating sensor with a higher-range one

This is **correct and essential**. Zobel et al. (2026) provide detailed experimental evidence that IEPE sensors driven beyond their rated measurement range undergo soft-clipping that distorts peak readings — in particular, the ±5 g sensor showed progressive negative-peak attenuation and asymmetric distortion when exposed to ~10 g events, while the ±50 g reference sensor was unaffected (zobel2026historyworkingprinciple pages 13-16, zobel2026historyworkingprinciple pages 9-11). The soft-clipping occurs without any system-level overload warning, so data appear valid but are biased (zobel2026historyworkingprinciple pages 1-4). Replacing the sensor with one whose rated range exceeds the expected peak by a comfortable margin (at least 2–3×) eliminates this artifact entirely.

### Relating accelerometer signals to SEA and peak force

From the accelerometer mounted on the falling mass, the instantaneous transmitted force is obtained via Newton's second law: F(t) = m_striker · a(t), where a(t) is the filtered, windowed deceleration of the striker (grabowskiUnknownyeardesignandevaluation pages 276-279, wnuk1981designandapplication pages 5-6). Peak transmitted force is then F_peak = m_striker · a_peak. Energy absorbed by the specimen can be computed in two equivalent ways:

1. **Integration of force–displacement:** EA = ∫₀^{δ_d} F(δ) dδ, where displacement δ(t) is obtained by double-integrating the acceleration signal or from high-speed video tracking (aymerich2026aninstrumenteddropweight pages 1-4, pajunen2019designandimpact pages 4-5, wnuk1981designandapplication pages 5-6).

2. **Energy balance:** EA = ½ m_striker (v_impact² − v_rebound²), using measured impact and rebound velocities, which provides an independent check and is less sensitive to high-frequency noise (aymerich2026aninstrumenteddropweight pages 1-4, aymerich2026aninstrumenteddropweight pages 4-8).

SEA is then EA/m_specimen. Note that small force errors propagate into significant energy errors when integrating, so the energy-balance method provides a valuable cross-check (aymerich2026aninstrumenteddropweight pages 1-4, aymerich2026aninstrumenteddropweight pages 8-11). Pajunen et al. (2019) used this combined approach — accelerometer + independent force sensor + high-speed camera — for 3D-printed tensegrity structures and verified momentum consistency within 1% across equivalent-momentum tests (pajunen2019designandimpact pages 7-8, pajunen2019designandimpact pages 4-5).

---

## Summary of Recommendations

1. **SEA and η_c definitions are correct** as stated. Ensure F_max is the maximum within [0, δ_d], determine δ_d via the efficiency-maximum method of Tan et al. (2005), and distinguish the single-number ideality ratio from the running efficiency used to locate densification (tan2005dynamiccompressivestrength pages 15-17, michailidis2011deformationandenergy pages 2-3, avalle2001characterizationofpolymeric pages 8-11).

2. **For drop-weight impact:** apply a phaseless 4th-order Butterworth low-pass filter at CFC-180 (300 Hz corner) per SAE J211 (alem1995designofdigital pages 5-8, alem1995designofdigital pages 8-13, gellner2024optimalheadimpacta pages 23-26); extract peak force within a time window centered on the primary contact event (found1998interpretationofsignals pages 1-2, gellner2024optimalheadimpact pages 116-121); always save the raw unfiltered trace (found1998interpretationofsignals pages 1-2); verify the accelerometer operates well within its rated range to avoid soft-clipping (zobel2026historyworkingprinciple pages 1-4, zobel2026historyworkingprinciple pages 13-16); and use the energy-balance method as an independent check on integrated force–displacement energy (aymerich2026aninstrumenteddropweight pages 1-4, aymerich2026aninstrumenteddropweight pages 4-8).

3. **The user's own findings** — that windowed CFC-180 analysis differs substantially from naive global-maximum reporting, and that a saturating sensor must be replaced — are **fully supported by the literature** and represent correct experimental practice.

References

1. (avalle2001characterizationofpolymeric pages 1-5): M. Avalle, G. Belingardi, and R. Montanini. Characterization of polymeric structural foams under compressive impact loading by means of energy-absorption diagram. International Journal of Impact Engineering, 25:455-472, May 2001. URL: https://doi.org/10.1016/s0734-743x(00)00060-9, doi:10.1016/s0734-743x(00)00060-9. This article has 869 citations and is from a domain leading peer-reviewed journal.

2. (avalle2001characterizationofpolymeric pages 5-8): M. Avalle, G. Belingardi, and R. Montanini. Characterization of polymeric structural foams under compressive impact loading by means of energy-absorption diagram. International Journal of Impact Engineering, 25:455-472, May 2001. URL: https://doi.org/10.1016/s0734-743x(00)00060-9, doi:10.1016/s0734-743x(00)00060-9. This article has 869 citations and is from a domain leading peer-reviewed journal.

3. (tan2005dynamiccompressivestrength pages 15-17): P.J. Tan, S.R. Reid, J.J. Harrigan, Z. Zou, and S. Li. Dynamic compressive strength properties of aluminium foams. part i—experimental data and observations. Journal of The Mechanics and Physics of Solids, 53:2174-2205, Oct 2005. URL: https://doi.org/10.1016/j.jmps.2005.05.007, doi:10.1016/j.jmps.2005.05.007. This article has 492 citations and is from a highest quality peer-reviewed journal.

4. (avalle2001characterizationofpolymeric pages 8-11): M. Avalle, G. Belingardi, and R. Montanini. Characterization of polymeric structural foams under compressive impact loading by means of energy-absorption diagram. International Journal of Impact Engineering, 25:455-472, May 2001. URL: https://doi.org/10.1016/s0734-743x(00)00060-9, doi:10.1016/s0734-743x(00)00060-9. This article has 869 citations and is from a domain leading peer-reviewed journal.

5. (michailidis2011deformationandenergy pages 2-3): N. Michailidis, F. Stergioudi, and A. Tsouknidas. Deformation and energy absorption properties of powder-metallurgy produced al foams. Materials Science and Engineering A-structural Materials Properties Microstructure and Processing, 528:7222-7227, Sep 2011. URL: https://doi.org/10.1016/j.msea.2011.05.031, doi:10.1016/j.msea.2011.05.031. This article has 72 citations.

6. (michailidis2011deformationandenergy pages 1-2): N. Michailidis, F. Stergioudi, and A. Tsouknidas. Deformation and energy absorption properties of powder-metallurgy produced al foams. Materials Science and Engineering A-structural Materials Properties Microstructure and Processing, 528:7222-7227, Sep 2011. URL: https://doi.org/10.1016/j.msea.2011.05.031, doi:10.1016/j.msea.2011.05.031. This article has 72 citations.

7. (ozturk2009energyabsorptioncalculations pages 2-4): Umud Esat Ozturk and Gunay Anlas. Energy absorption calculations in multiple compressive loading of polymeric foams. Materials & Design, 30:15-22, Jan 2009. URL: https://doi.org/10.1016/j.matdes.2008.04.054, doi:10.1016/j.matdes.2008.04.054. This article has 85 citations and is from a highest quality peer-reviewed journal.

8. (grabowskiUnknownyeardesignandevaluation pages 82-84): TJ Grabowski. Design and evaluation of packages containing cushioned items, using peak acceleration versus static stress data. Unknown journal, Unknown year.

9. (alem1995designofdigital pages 5-8): N Alem and M Perry. Design of digital low-pass filters for time-domain recursive filtering of impact acceleration signals. Unknown journal, 1995.

10. (alem1995designofdigital pages 8-13): N Alem and M Perry. Design of digital low-pass filters for time-domain recursive filtering of impact acceleration signals. Unknown journal, 1995.

11. (alem1995designofdigital pages 28-33): N Alem and M Perry. Design of digital low-pass filters for time-domain recursive filtering of impact acceleration signals. Unknown journal, 1995.

12. (alem1995designofdigital pages 15-18): N Alem and M Perry. Design of digital low-pass filters for time-domain recursive filtering of impact acceleration signals. Unknown journal, 1995.

13. (gellner2024optimalheadimpacta pages 23-26): RA Gellner. Optimal head impact signal processing and the description and perception of head impact exposure in female adolescent ice hockey players. Unknown journal, 2024.

14. (gellner2024optimalheadimpact pages 30-32): RA Gellner. Optimal head impact signal processing and the description and perception of head impact exposure in female adolescent ice hockey players. Unknown journal, 2024.

15. (alem1995designofdigital pages 21-24): N Alem and M Perry. Design of digital low-pass filters for time-domain recursive filtering of impact acceleration signals. Unknown journal, 1995.

16. (arteagaperez2018filtrodecapacitores pages 2-4): VR Arteaga-Pérez and N Quiroz-Hernández. Filtro de capacitores conmutados para la adquisición de datos en pruebas de impacto automotriz. Unknown journal, 2018.

17. (gellner2024optimalheadimpact pages 26-30): RA Gellner. Optimal head impact signal processing and the description and perception of head impact exposure in female adolescent ice hockey players. Unknown journal, 2024.

18. (gellner2024optimalheadimpact pages 23-26): RA Gellner. Optimal head impact signal processing and the description and perception of head impact exposure in female adolescent ice hockey players. Unknown journal, 2024.

19. (aymerich2026aninstrumenteddropweight pages 4-8): F. Aymerich, P. Marcialis, Silvia Meili, and P. Priolo. An instrumented drop-weight machine for low-velocity impact testing. WIT Transactions on the Built Environment, 2026. URL: https://doi.org/10.2495/susi960221, doi:10.2495/susi960221. This article has 25 citations.

20. (found1998interpretationofsignals pages 1-2): M.S. Found, I.C. Howard, and A.P. Paran. Interpretation of signals from dropweight impact tests. Composite Structures, 42:353-363, Aug 1998. URL: https://doi.org/10.1016/s0263-8223(98)00080-4, doi:10.1016/s0263-8223(98)00080-4. This article has 67 citations and is from a domain leading peer-reviewed journal.

21. (gellner2024optimalheadimpact pages 116-121): RA Gellner. Optimal head impact signal processing and the description and perception of head impact exposure in female adolescent ice hockey players. Unknown journal, 2024.

22. (zobel2026historyworkingprinciple pages 1-4): Oliver M. Zobel, Johannes Maierhofer, Michael Kreutz, and Daniel J. Rixen. History, working principle, and pitfalls of iepe/icp piezoelectric sensors. Unknown journal, Jan 2026. URL: https://doi.org/10.21203/rs.3.rs-8564064/v1, doi:10.21203/rs.3.rs-8564064/v1.

23. (zobel2026historyworkingprinciple pages 9-11): Oliver M. Zobel, Johannes Maierhofer, Michael Kreutz, and Daniel J. Rixen. History, working principle, and pitfalls of iepe/icp piezoelectric sensors. Unknown journal, Jan 2026. URL: https://doi.org/10.21203/rs.3.rs-8564064/v1, doi:10.21203/rs.3.rs-8564064/v1.

24. (zobel2026historyworkingprinciple pages 23-25): Oliver M. Zobel, Johannes Maierhofer, Michael Kreutz, and Daniel J. Rixen. History, working principle, and pitfalls of iepe/icp piezoelectric sensors. Unknown journal, Jan 2026. URL: https://doi.org/10.21203/rs.3.rs-8564064/v1, doi:10.21203/rs.3.rs-8564064/v1.

25. (zobel2026historyworkingprinciple pages 11-13): Oliver M. Zobel, Johannes Maierhofer, Michael Kreutz, and Daniel J. Rixen. History, working principle, and pitfalls of iepe/icp piezoelectric sensors. Unknown journal, Jan 2026. URL: https://doi.org/10.21203/rs.3.rs-8564064/v1, doi:10.21203/rs.3.rs-8564064/v1.

26. (zobel2026historyworkingprinciple pages 13-16): Oliver M. Zobel, Johannes Maierhofer, Michael Kreutz, and Daniel J. Rixen. History, working principle, and pitfalls of iepe/icp piezoelectric sensors. Unknown journal, Jan 2026. URL: https://doi.org/10.21203/rs.3.rs-8564064/v1, doi:10.21203/rs.3.rs-8564064/v1.

27. (kargl2001accelerometrymeasurementsusing pages 4-5): Günter Kargl, Wolfgang Macher, Norbert I. Kömle, Markus Thiel, Christian Rohe, and Andrew J. Ball. Accelerometry measurements using the rosetta lander's anchoring harpoon: experimental set-up, data reduction and signal analysis. Planetary and Space Science, 49:425-435, Apr 2001. URL: https://doi.org/10.1016/s0032-0633(00)00136-7, doi:10.1016/s0032-0633(00)00136-7. This article has 26 citations and is from a peer-reviewed journal.

28. (pajunen2019designandimpact pages 4-5): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 99 citations and is from a highest quality peer-reviewed journal.

29. (gellner2024optimalheadimpact pages 37-40): RA Gellner. Optimal head impact signal processing and the description and perception of head impact exposure in female adolescent ice hockey players. Unknown journal, 2024.

30. (found1998interpretationofsignals pages 4-7): M.S. Found, I.C. Howard, and A.P. Paran. Interpretation of signals from dropweight impact tests. Composite Structures, 42:353-363, Aug 1998. URL: https://doi.org/10.1016/s0263-8223(98)00080-4, doi:10.1016/s0263-8223(98)00080-4. This article has 67 citations and is from a domain leading peer-reviewed journal.

31. (grabowskiUnknownyeardesignandevaluation pages 276-279): TJ Grabowski. Design and evaluation of packages containing cushioned items, using peak acceleration versus static stress data. Unknown journal, Unknown year.

32. (wnuk1981designandapplication pages 5-6): A. J. Wnuk, T. C. Ward, and J. E. McGrath. Design and application of an instrumented falling weight impact tester. Polymer Engineering and Science, 21:313-324, Apr 1981. URL: https://doi.org/10.1002/pen.760210602, doi:10.1002/pen.760210602. This article has 26 citations and is from a peer-reviewed journal.

33. (aymerich2026aninstrumenteddropweight pages 1-4): F. Aymerich, P. Marcialis, Silvia Meili, and P. Priolo. An instrumented drop-weight machine for low-velocity impact testing. WIT Transactions on the Built Environment, 2026. URL: https://doi.org/10.2495/susi960221, doi:10.2495/susi960221. This article has 25 citations.

34. (aymerich2026aninstrumenteddropweight pages 8-11): F. Aymerich, P. Marcialis, Silvia Meili, and P. Priolo. An instrumented drop-weight machine for low-velocity impact testing. WIT Transactions on the Built Environment, 2026. URL: https://doi.org/10.2495/susi960221, doi:10.2495/susi960221. This article has 25 citations.

35. (pajunen2019designandimpact pages 7-8): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 99 citations and is from a highest quality peer-reviewed journal.
