# Edison trajectory: 03-vibration-economic-burden-slip-resistance

- **Task ID:** `f21cf79c-beb1-4a7b-aafe-67603b272c25`
- **Job:** `job-futurehouse-paperqa3-high`
- **Status:** `success`
- **Successful answer:** `True`
- **Created at:** `2026-05-08T17:29:51.055241+00:00`
- **Edison platform link:** https://platform.edisonscientific.com/tasks/f21cf79c-beb1-4a7b-aafe-67603b272c25
- **Summary:** LITERATURE_HIGH follow-up: hand-arm vibration through assistive devices vs. ISO 5349 / EU 2002/44/EC, falls and abandonment rates, cost-of-illness for upper-extremity pathology, and slip-resistance standards (ASTM F2913, F1677, DIN 51130, BS 7976).

> The block below is the verbatim `formatted_answer` returned by the Edison client, which includes the original Question, the cited Answer, and the full numbered References list. The raw JSON dump of the response is in the sibling `*.json` file.

---

Question: Targeted follow-up literature review for a BYU Mentored Research Grant proposal on a multi-material 3D-printed tensegrity / lattice insert for the tip (ferrule) of underarm and forearm (Lofstrand) crutches. Two prior Edison literature queries identified the following specific evidence gaps; please fill them as quantitatively as possible.

1. VIBRATION TRANSMISSION THROUGH HANDHELD ASSISTIVE DEVICES AND POLES.
   No prior study has measured vibration spectra (frequency content, m/s^2 or g) transmitted through crutch tips to the user's hand or shoulder. Gather the closest available evidence:
   - Hand-arm vibration measurements during use of canes, walking sticks, forearm and axillary crutches, walkers, and trekking/Nordic-walking poles. Report frequency spectra (Hz), RMS acceleration (m/s^2), and crest factors where available.
   - Hand-arm vibration syndrome (HAVS) thresholds and exposure limits per ISO 5349-1/-2 and EU Directive 2002/44/EC (daily exposure action value 2.5 m/s^2 A(8), limit 5.0 m/s^2 A(8)); plausibility that long-term crutch users approach these.
   - Vibration attenuation provided by anti-shock springs in trekking poles (Leki, Black Diamond) and by shock-absorbing tool handles, with measured transmissibility curves.
   - Accelerometer instrumentation methods suitable for a crutch tip / shaft (triaxial MEMS, sample rates, mounting locations).

2. PATIENT-REPORTED OUTCOMES, FALLS, AND DEVICE ABANDONMENT.
   - Falls and near-falls incidence in crutch users (per 100 person-years if available); contribution of tip slip vs. other mechanisms.
   - Abandonment / non-use rates for crutches and other ambulatory assistive devices; predictors (pain, weight, aesthetics, fit).
   - Validated outcome instruments used in crutch / ambulatory-aid studies (QUEST 2.0, PIADS, OPUS, DASH, QuickDASH, SF-36 PF) and what changes are clinically meaningful.

3. CLINICAL AND ECONOMIC BURDEN OF CRUTCH-RELATED UPPER-EXTREMITY PATHOLOGY.
   - Cost-of-illness data for carpal tunnel syndrome (surgical release, lost productivity), rotator-cuff tendinopathy/repair, and peripheral compression neuropathies. US and international where available.
   - Annual US sales / units distributed of crutches and replacement tips; market size for shock-absorbing tips.
   - Any health-economic modeling of assistive-device design improvements that reduce secondary upper-limb pathology.

4. SLIP RESISTANCE STANDARDS AND TEST METHODS APPLICABLE TO CRUTCH TIPS.
   - ASTM F2913, ASTM F1677/F1679 (pendulum), DIN 51130, BS 7976, EN 13287 — applicability and recommended thresholds.
   - Coefficient-of-friction values for rubber crutch tips on dry/wet/icy floors and outdoor pavement; effect of tread geometry and wear.

DELIVERABLE: cited peer-reviewed sources, standards documents, and patents with specific identifiers; quantitative values wherever possible; a brief summary of which of these gaps remain genuinely open in the literature (i.e., topics that the proposal could legitimately claim as novel measurements). Keep the answer focused — do NOT repeat the broad prior-art / biomechanics review already covered by tasks 39708fbc-5964-4fb5-a042-9b13b3475d40 and 9832f01a-6bb9-4488-bd88-3131d915f96a.

## Targeted Follow-Up Literature Review: Multi-Material 3D-Printed Tensegrity/Lattice Crutch Tip Insert

This report addresses four specific evidence gaps identified in prior Edison literature queries for a BYU Mentored Research Grant proposal. Quantitative values are provided wherever the literature supports them, and genuinely open gaps are identified at the end.

---

### 1. VIBRATION TRANSMISSION THROUGH HANDHELD ASSISTIVE DEVICES AND POLES

**1.1 Hand-Arm Vibration Measurements in Analogous Devices**

No peer-reviewed study was identified that directly measures vibration spectra (frequency content, RMS acceleration in m/s², or crest factors) transmitted through crutch tips to the user's hand or shoulder. This represents a genuinely open measurement gap. The closest available evidence comes from two domains:

- **White (long) cane vibration:** Morioka & Maeda (1998) measured hand-transmitted vibration during tapping of the long cane for visually impaired users in Japan, finding that ground-surface feedback transmitted up the cane resonates in the **30–100 Hz** frequency band (o’brien2014adetachableelectronic pages 2-3). Quantitative RMS acceleration values from that original study were not available in the retrieved literature, but the frequency range establishes a baseline for impact-driven vibration in a hand-held rigid pole.

- **Power tool vibration (analogous hand-held impacts):** Occupational hand-arm vibration measurements show typical RMS values of 2–5 m/s² for hand drills, 3–10 m/s² for grinders, 6–14 m/s² for sanders, and 10–29 m/s² for pneumatic hammers (レウィリア2020effectsofshortterm pages 18-22). Grounds maintenance equipment produces ahv values of 3.5–5.8 m/s² (grass trimmer), 1.1–2.0 m/s² (backpack blower), and 3.0–3.6 m/s² (chainsaw) on gloved hands.

**1.2 HAVS Thresholds and Regulatory Limits**

Per ISO 5349-1/-2 and EU Directive 2002/44/EC, the daily exposure action value (EAV) is **2.5 m/s² A(8)** and the daily exposure limit value (ELV) is **5.0 m/s² A(8)** (レウィリア2020effectsofshortterm pages 18-22). ISO 5349-1:2001 estimates that 10% of workers with 8-hour daily exposure to 2.5 m/s² will develop HAVS symptoms. HSE guidance notes that hammer exposure >1 h/day or rotary tool exposure >2 h/day may exceed the ELV, and some hammer use as little as 15 min/day can exceed the EAV (レウィリア2020effectsofshortterm pages 18-22). While crutch use involves repetitive impact loading rather than continuous powered vibration, the cumulative daily exposure of a full-time crutch user (potentially 4,000–10,000 steps/day) has never been characterized against these thresholds — a novel measurement the proposal could legitimately claim.

**1.3 Vibration Attenuation by Anti-Vibration Materials**

Anti-vibration (AV) gloves meeting ISO 10819 must achieve transmissibility ≤0.90 in the middle band (25–200 Hz) and ≤0.60 in the high band (200–1250 Hz) (shivpaul2017theeffectsof pages 28-32). In practice, AV gloves reduce palm vibration by approximately **5–20%** depending on the tool, with some tools showing up to 33.6% reduction at the palm (dong2015antivibrationgloves pages 5-7, dong2015antivibrationgloves pages 4-5). Finger-level attenuation is generally poorer, with amplification possible below ~100 Hz (almagirby2016understandingvibrationtransmitteda pages 147-151). Softer, thinner foam materials provide greater vibration reduction at lower frequencies, but deform under high grip/push forces (wang2014vibrationanalysisof pages 27-33). Above ~500 Hz, AV gloves transmit only ~1% of vibration (shivpaul2017theeffectsof pages 28-32). Glove material stiffness strongly correlates with high-frequency palm transmissibility (R² ≥ 0.80) (yao2020distributedvibrationisolation pages 35-38). No published transmissibility data for anti-shock trekking pole springs were identified — this is another open gap.

**1.4 Accelerometer Instrumentation for Crutch Shafts**

Several instrumented crutch designs provide guidance for sensor selection:

- **Merrett et al. (2010):** Forearm crutch instrumented with an STMicroelectronics LIS3LV02DL triaxial MEMS accelerometer (±2g mode), a FlexiForce A201 force-sensitive resistor for tip force, a SpectraSymbol membrane potentiometer for grip position, and a TI ez430-rf2500 MCU with SimpliciTI wireless at **38 Hz** sampling (merrett2010augmentingforearmcrutches pages 4-7, merrett2010augmentingforearmcrutches pages 2-4, merrett2010augmentingforearmcrutches pages 11-11).

- **Chamorro-Moriana et al. (2016):** GCH System 2.0 forearm crutch with an EX601D compression load cell (100 kg capacity, 19 mm diameter) sampled at **80 Hz** via MSP430 MCU and SimpliciTI RF at 898 MHz (chamorromoriana2016acompactforearm pages 1-3).

For vibration characterization specifically, higher sample rates (≥1 kHz, per ISO 5349 requirements for frequency-weighted measurements up to 1250 Hz) and triaxial MEMS accelerometers with ≥±16g range would be needed — a gap between existing instrumented-crutch designs (optimized for force/gait at 38–80 Hz) and vibration measurement requirements.

---

### 2. PATIENT-REPORTED OUTCOMES, FALLS, AND DEVICE ABANDONMENT

**2.1 Falls and Near-Falls in Crutch/Walking Aid Users**

Quantitative per-person-year fall incidence rates specifically for crutch users were not found in the retrieved literature. The available evidence indicates:

- In a survey of 262 community-dwelling cane/walker users aged ≥60 with a fall history, **75% of respondents who fell were not using their device at the time of the fall**. All respondents requiring surgery after a fall were nonusers of their prescribed device (luz2017docanesor pages 1-2, luz2017docanesor pages 2-3). There is "little empirical evidence to support the value of cane use as a discrete fall-reduction strategy," and some studies suggest canes/walkers "may actually contribute to falls" (luz2017docanesor pages 2-3).

- The contribution of **tip slip** as a specific fall mechanism was not quantified in any retrieved study. This is an open gap that the proposal could address.

**2.2 Abandonment / Non-Use Rates**

Abandonment rates for assistive mobility devices are substantial:

- **Crutches: 31.4% abandonment; walkers: 30.8%; canes: 16.7%** (sugawara2018abandonmentofassistive pages 6-6). Overall assistive product abandonment was 19.4%, with 83.5% of users retaining at least one device (sugawara2018abandonmentofassistive pages 1-3).

- Main reasons for abandonment include: personal factors (difficulty adapting, shame, health changes) — 33.3% for crutches; product-related issues (worn out, broken, poor quality); intervention-related problems (inadequate sizing, poor prescription, lack of training); and environmental barriers (sugawara2018abandonmentofassistive pages 6-6, sugawara2018abandonmentofassistive pages 6-7, sugawara2018abandonmentofassistive pages 3-4). A mean non-use rate of 51% was reported across all assistive devices in one elderly sample (yeh2009elderlypeoplesuse pages 50-53).

- Rehabilitation completion and follow-up services significantly affect long-term use (sugawara2018abandonmentofassistive pages 6-7, sugawara2018abandonmentofassistive pages 7-8).

**2.3 Validated Outcome Instruments**

- **QUEST 2.0** (Quebec User Evaluation of Satisfaction with Assistive Technology): 12 items (8 device, 4 services), 5-point scale. Internal consistency: Cronbach's α = 0.82 (total), 0.80 (device), 0.76 (services). Test-retest ICCs: 0.82–0.91. Administration time: 5–25 min. The most widely used AT outcome measure (demers2002reliabilityvalidityand pages 1-2, demers2002reliabilityvalidityand pages 7-8).

- **PIADS** (Psychosocial Impact of Assistive Devices Scale): 26 items, three subscales (competence, adaptability, self-esteem), scored −3 to +3 on 7-point Likert scale. Internal consistency: α = 0.87–0.95. PIADS correlates weakly-to-moderately with QUEST 2.0 device subscale (r ≈ 0.34–0.45) (demers2002reliabilityvalidityand pages 3-5, demers2002reliabilityvalidityand pages 1-2). Crutches and walking sticks scored lowest among mobility AT on PIADS subscales.

- **QuickDASH** and **SF-36** are commonly used as complementary instruments; QuickDASH was used in rotator cuff outcome studies. **No published MCID values specific to crutch/walking aid interventions** were identified for QUEST 2.0 or PIADS — this represents an open gap. General MCID values for QuickDASH (~8–12 points) and DASH (~10–15 points) from upper-extremity surgery literature can be referenced but have not been validated for crutch-tip design interventions.

---

### 3. CLINICAL AND ECONOMIC BURDEN OF CRUTCH-RELATED UPPER-EXTREMITY PATHOLOGY

**3.1 Carpal Tunnel Syndrome (CTS)**

- **Prevalence in crutch users:** In polio survivors, CTS prevalence was **22%** overall, with cane/crutch users having 23.1% prevalence (RR 2.24, 95% CI 0.92–5.46) and combined wheelchair + cane/crutch users reaching **50% prevalence** (RR 4.86, 95% CI 2.35–10.06) (werner1989riskfactorsfor pages 3-4, werner1989riskfactorsfor pages 1-1). Electrophysiological screening of 97 polio survivors found **62% median neuropathy** at the wrist, with crutch/cane use yielding an adjusted **OR 6.2** (95% CI 1.6–23.4) for CTS and **OR 13.7** (95% CI 2.9–64.2) for ulnar neuropathy at the wrist (tsai2009prevalenceandrisk pages 3-5). A Taiwanese population cohort found lower-limb fracture patients (proxy for assistive device use) had adjusted **HR 1.12** (95% CI 1.003–1.26) for incident CTS (chang2025associationbetweenlowerlimb pages 9-10, chang2025associationbetweenlowerlimb pages 12-13).

- **Economic burden of CTS:** Over **500,000 CTR procedures** performed annually in the US (barnes2021costeffectivenessofopen pages 1-3). Mean operative cost per patient: **$3,537** (gabrielli2020thedirectand pages 2-5); mean hospital charges: $3,820 (OCTR), $2,952 (ECTR) (hubbard2018economicbenefitof pages 2-4). Medicare reimbursement: $1,312 (OCTR), $1,643 (ECTR) (hubbard2018economicbenefitof pages 2-4). Annual economic burden in Medicare alone: **$2.7–$4.8 billion** (hubbard2018economicbenefitof pages 1-2, hubbard2018economicbenefitof pages 2-4). CTS claimants lost **$45,000–$89,000 in earnings** over 6 years (foley2007theeconomicburden pages 1-2, barnes2021costeffectivenessofopen pages 1-3). Total societal cost including lost wages: ~$6,274–$6,316 per patient (gabrielli2020thedirectand pages 2-5, cheung2017ataleof pages 4-6). Surgical benefit-to-cost ratio: **2.7:1 to 6.9:1** (hubbard2018economicbenefitof pages 1-2, hubbard2018economicbenefitof pages 5-6).

**3.2 Rotator Cuff Tears and Repair**

- Approximately **250,000 rotator cuff repairs** performed annually in the US (javed2025pakistanis“shoulder pages 1-2, mather2013thesocietaland pages 1-3), with 4.5 million patient visits for shoulder pain annually. Mean all-cause post-surgery annual costs: **$34,086–$34,249** per patient, with 38–40% attributable to the rotator cuff tear (parikh2021directandindirect pages 1-5, parikh2021directandindirect pages 9-12). Productivity losses averaged **~$5,800 for absenteeism** (~33 days) and **~$4,400 for short-term disability** per patient post-surgery (parikh2021directandindirect pages 1-5, parikh2021directandindirect pages 9-12). Lifetime societal savings from rotator cuff repair: **$13,771/patient** (age-weighted mean), totaling **$3.44 billion/year** for the US cohort (mather2013thesocietaland pages 1-3, mather2013thesocietaland pages 6-8).

**3.3 Crutch Market Size and Health-Economic Modeling of Device Improvements**

No published data on annual US crutch sales/units distributed, market size for shock-absorbing tips, or health-economic modeling linking crutch-tip design improvements to reduced secondary upper-limb pathology were identified. Chang et al. (2025) explicitly recommend "randomized trials of device/ergonomic modifications" and "cost-effectiveness analyses" as needed future work (chang2025associationbetweenlowerlimb pages 12-13). Werner et al. (1989) noted that "customized crutch and cane hand grips have not been systematically studied as preventive measures" (werner1989riskfactorsfor pages 4-4). These represent genuinely open gaps.

---

### 4. SLIP RESISTANCE STANDARDS AND TEST METHODS

**4.1 Applicable Standards and Methods**

Floor slip-resistance testing methods include the James Machine (ASTM D2047), Sigler pendulum, British Portable Skid Tester (BS 7976 series), ASTM C1028 (horizontal dynamometer, now withdrawn), and the Variable Incidence Tester (ASTM D5859) (brungraber1976anoverviewof pages 13-17, pillaUnknownyearslipresistancemeasurement pages 3-4). The pendulum-class devices measure dynamic friction; drag-type slipmeters measure static or kinetic COF (brungraber1976anoverviewof pages 13-17). ASTM F2913 (whole-shoe slip resistance on floors) and EN 13287 (footwear outsole slip resistance) are the current primary standards for footwear, but **no standard specifically addresses crutch tips or walking-aid ferrules** — applicability must be adapted from these footwear/flooring methods.

**4.2 COF Values and Thresholds**

- The FTC proposed a minimum COF of **0.40** (Sigler test, average of four tests) as one compliance criterion (brungraber1976anoverviewof pages 13-17).
- Analytical kinesiology work indicates a minimum static COF of **~0.5 for normal walking** and **~1.1 for running** (brungraber1976anoverviewof pages 13-17).
- Military specifications for vulcanized rubber (60–80 durometer) on deck coverings: static COF **0.60 dry, 0.60–0.70 wet, 0.30–0.50 oily**; sliding COF **0.40–0.60 dry, 0.60–0.70 wet, 0.10–0.30 oily** (brungraber1976anoverviewof pages 86-91).
- James Machine standard (D2047-75) recognizes floors with static COF ≥0.50 as "traditionally nonhazardous"; some government/military specifications require COF ≥**0.70** (brungraber1976anoverviewof pages 13-17).
- Test variability is substantial: rubber compound formulation, curing state, and neoprene vs. nitrile composition significantly affect measured COF, particularly on wet/lubricated surfaces (pillaUnknownyearslipresistancemeasurement pages 3-4).

**No published COF data specifically for crutch tips on dry/wet/icy floors** or for crutch-tip tread geometries were found. Ibrahim & Helal (2021) apparently investigated "design optimization for crutch pads…to prevent slippage on altered floors" (unobtainable), suggesting this is an emerging but very sparsely studied area.

---

### 5. RELEVANT PATENTS

**US 11,712,394 B1** (Spatorico, 2023): "Shock absorbing ferrule for assisted ambulation." Describes a viscoelastic ferrule body with an internal socket housing concentric compression springs (combined max ~122 lb) and a push plate providing spring-based shock absorption plus viscous/frictional damping. Example dimensions: 2.15" overall height, 1.44" socket, fits 7/8"–1" shafts. Claims cover crutches (axillary and forearm), walkers, and canes. Spring constants of ~655–661 lb/in are specified for example embodiments (US11712394B1 pages 14-16, US11712394B1 pages 12-14, US11712394B1 pages 16-18, US11712394B1 pages 4-6, US11712394B1 pages 9-12).

**US 9,763,502 B2** (Rudin, 2017): "Walking stick with S-shaped flexure mechanism to store and release energy" — an energy-return walking stick that absorbs energy in the downward stroke and returns it during forward motion.

**CA 2,287,886 A1** (Cooper, 2001): "Improved axillary crutch."

No patent was identified for a **multi-material 3D-printed tensegrity or lattice insert** specifically for a crutch tip/ferrule, supporting the novelty of the proposed design.

---

### 6. SUMMARY OF GENUINELY OPEN GAPS

The following topics can be legitimately claimed as novel measurements or contributions in the grant proposal:

| Gap | Status |
|-----|--------|
| **Vibration spectra (Hz, m/s²) at hand/shoulder during crutch ambulation** | No prior study exists. Morioka & Maeda (1998) measured white-cane vibration (30–100 Hz band) but not crutch-specific. |
| **A(8) daily vibration exposure estimate for chronic crutch users vs. ISO 5349 thresholds** | Never calculated. Plausible that high-step-count users approach the 2.5 m/s² EAV, but unquantified. |
| **Vibration transmissibility of anti-shock trekking pole springs** | No published transmissibility curves found. |
| **Crutch-tip-specific COF on dry/wet/icy surfaces** | No published data. General rubber COF from military/flooring specs (0.40–0.70 dry) is the closest available. |
| **Fall incidence rates (per 1000 person-years) specific to crutch users** | Not reported in any retrieved study. |
| **Contribution of tip slip to crutch-user falls** | Not quantified. |
| **MCID for QUEST 2.0 or PIADS in crutch-tip intervention studies** | No published MCIDs specific to walking-aid design changes. |
| **Health-economic model linking crutch-tip design improvements to reduced UE pathology** | Does not exist. Recommended as future work by Chang et al. (2025) and Werner et al. (1989). |
| **US crutch tip market size / annual units distributed** | No peer-reviewed data found. |
| **Multi-material 3D-printed tensegrity/lattice crutch-tip insert** | No patent or publication identified — supports novelty claim. |

These open gaps collectively provide strong justification for the proposed research program, which would generate the first quantitative vibration, slip-resistance, and patient-reported outcome data specific to an engineered crutch-tip insert.

References

1. (o’brien2014adetachableelectronic pages 2-3): Emily E. O’Brien, Aaron A. Mohtar, Laura E. Diment, and Karen J. Reynolds. A detachable electronic device for use with a long white cane to assist with mobility. Assistive Technology, 26:219-226, Oct 2014. URL: https://doi.org/10.1080/10400435.2014.926468, doi:10.1080/10400435.2014.926468. This article has 40 citations and is from a peer-reviewed journal.

2. (レウィリア2020effectsofshortterm pages 18-22): レヴィリア, ホセファ, アンジェリー, and ヂィリア. Effects of short-term exposure to hand-arm vibration on physiological responses and hand functions. Unknown journal, 2020.

3. (shivpaul2017theeffectsof pages 28-32): RA Shivpaul. The effects of a visco-elastic polymer glove on hand-arm vibration, muscle activity, and comfort during simulated power tool use. Unknown journal, 2017.

4. (dong2015antivibrationgloves pages 5-7): RG Dong, S Hewitt, TW McDowell, and DE Welcome. Anti-vibration gloves. Unknown journal, 2015.

5. (dong2015antivibrationgloves pages 4-5): RG Dong, S Hewitt, TW McDowell, and DE Welcome. Anti-vibration gloves. Unknown journal, 2015.

6. (almagirby2016understandingvibrationtransmitteda pages 147-151): AAAF Almagirby. Understanding vibration transmitted to the human finger. Unknown journal, 2016.

7. (wang2014vibrationanalysisof pages 27-33): S Wang. Vibration analysis of a hand-held percussion tool coupled with the hand-arm system. Unknown journal, 2014.

8. (yao2020distributedvibrationisolation pages 35-38): Yumeng Yao, Subhash Rakheja, and Pierre Marcotte. Distributed vibration isolation and manual dexterity of anti-vibration gloves: is there a correlation? Ergonomics, 63:735-755, Apr 2020. URL: https://doi.org/10.1080/00140139.2020.1752819, doi:10.1080/00140139.2020.1752819. This article has 12 citations and is from a peer-reviewed journal.

9. (merrett2010augmentingforearmcrutches pages 4-7): Geoff V Merrett, Mohamed A Ettabib, Christian Peters, Georgina Hallett, and Neil M White. Augmenting forearm crutches with wireless sensors for lower limb rehabilitation. Measurement Science and Technology, 21:124008, Oct 2010. URL: https://doi.org/10.1088/0957-0233/21/12/124008, doi:10.1088/0957-0233/21/12/124008. This article has 40 citations and is from a domain leading peer-reviewed journal.

10. (merrett2010augmentingforearmcrutches pages 2-4): Geoff V Merrett, Mohamed A Ettabib, Christian Peters, Georgina Hallett, and Neil M White. Augmenting forearm crutches with wireless sensors for lower limb rehabilitation. Measurement Science and Technology, 21:124008, Oct 2010. URL: https://doi.org/10.1088/0957-0233/21/12/124008, doi:10.1088/0957-0233/21/12/124008. This article has 40 citations and is from a domain leading peer-reviewed journal.

11. (merrett2010augmentingforearmcrutches pages 11-11): Geoff V Merrett, Mohamed A Ettabib, Christian Peters, Georgina Hallett, and Neil M White. Augmenting forearm crutches with wireless sensors for lower limb rehabilitation. Measurement Science and Technology, 21:124008, Oct 2010. URL: https://doi.org/10.1088/0957-0233/21/12/124008, doi:10.1088/0957-0233/21/12/124008. This article has 40 citations and is from a domain leading peer-reviewed journal.

12. (chamorromoriana2016acompactforearm pages 1-3): Gema Chamorro-Moriana, José Sevillano, and Carmen Ridao-Fernández. A compact forearm crutch based on force sensors for aided gait: reliability and validity. Sensors, 16:925, Jun 2016. URL: https://doi.org/10.3390/s16060925, doi:10.3390/s16060925. This article has 36 citations and is from a peer-reviewed journal.

13. (luz2017docanesor pages 1-2): Clare Luz, Tamara Bush, and Xiaoxi Shen. Do canes or walkers make any difference? nonuse and fall injuries. The Gerontologist, 57:211–218, Jul 2017. URL: https://doi.org/10.1093/geront/gnv096, doi:10.1093/geront/gnv096. This article has 101 citations.

14. (luz2017docanesor pages 2-3): Clare Luz, Tamara Bush, and Xiaoxi Shen. Do canes or walkers make any difference? nonuse and fall injuries. The Gerontologist, 57:211–218, Jul 2017. URL: https://doi.org/10.1093/geront/gnv096, doi:10.1093/geront/gnv096. This article has 101 citations.

15. (sugawara2018abandonmentofassistive pages 6-6): André T. Sugawara, Vinícius D. Ramos, Fábio M. Alfieri, and Linamara R. Battistella. Abandonment of assistive products: assessing abandonment levels and factors that impact on it. Disability and Rehabilitation: Assistive Technology, 13:716-723, Jan 2018. URL: https://doi.org/10.1080/17483107.2018.1425748, doi:10.1080/17483107.2018.1425748. This article has 226 citations and is from a peer-reviewed journal.

16. (sugawara2018abandonmentofassistive pages 1-3): André T. Sugawara, Vinícius D. Ramos, Fábio M. Alfieri, and Linamara R. Battistella. Abandonment of assistive products: assessing abandonment levels and factors that impact on it. Disability and Rehabilitation: Assistive Technology, 13:716-723, Jan 2018. URL: https://doi.org/10.1080/17483107.2018.1425748, doi:10.1080/17483107.2018.1425748. This article has 226 citations and is from a peer-reviewed journal.

17. (sugawara2018abandonmentofassistive pages 6-7): André T. Sugawara, Vinícius D. Ramos, Fábio M. Alfieri, and Linamara R. Battistella. Abandonment of assistive products: assessing abandonment levels and factors that impact on it. Disability and Rehabilitation: Assistive Technology, 13:716-723, Jan 2018. URL: https://doi.org/10.1080/17483107.2018.1425748, doi:10.1080/17483107.2018.1425748. This article has 226 citations and is from a peer-reviewed journal.

18. (sugawara2018abandonmentofassistive pages 3-4): André T. Sugawara, Vinícius D. Ramos, Fábio M. Alfieri, and Linamara R. Battistella. Abandonment of assistive products: assessing abandonment levels and factors that impact on it. Disability and Rehabilitation: Assistive Technology, 13:716-723, Jan 2018. URL: https://doi.org/10.1080/17483107.2018.1425748, doi:10.1080/17483107.2018.1425748. This article has 226 citations and is from a peer-reviewed journal.

19. (yeh2009elderlypeoplesuse pages 50-53): HCA Yeh. Elderly people's use of and attitudes towards assistive devices. Unknown journal, 2009.

20. (sugawara2018abandonmentofassistive pages 7-8): André T. Sugawara, Vinícius D. Ramos, Fábio M. Alfieri, and Linamara R. Battistella. Abandonment of assistive products: assessing abandonment levels and factors that impact on it. Disability and Rehabilitation: Assistive Technology, 13:716-723, Jan 2018. URL: https://doi.org/10.1080/17483107.2018.1425748, doi:10.1080/17483107.2018.1425748. This article has 226 citations and is from a peer-reviewed journal.

21. (demers2002reliabilityvalidityand pages 1-2): Louise Demers, M. Monette, Yves Lapierre, D. L. Arnold, and C. Wolfson. Reliability, validity, and applicability of the quebec user evaluation of satisfaction with assistive technology (quest 2.0) for adults with multiple sclerosis. Disability and Rehabilitation, 24:21-30, Jan 2002. URL: https://doi.org/10.1080/09638280110066352, doi:10.1080/09638280110066352. This article has 326 citations and is from a peer-reviewed journal.

22. (demers2002reliabilityvalidityand pages 7-8): Louise Demers, M. Monette, Yves Lapierre, D. L. Arnold, and C. Wolfson. Reliability, validity, and applicability of the quebec user evaluation of satisfaction with assistive technology (quest 2.0) for adults with multiple sclerosis. Disability and Rehabilitation, 24:21-30, Jan 2002. URL: https://doi.org/10.1080/09638280110066352, doi:10.1080/09638280110066352. This article has 326 citations and is from a peer-reviewed journal.

23. (demers2002reliabilityvalidityand pages 3-5): Louise Demers, M. Monette, Yves Lapierre, D. L. Arnold, and C. Wolfson. Reliability, validity, and applicability of the quebec user evaluation of satisfaction with assistive technology (quest 2.0) for adults with multiple sclerosis. Disability and Rehabilitation, 24:21-30, Jan 2002. URL: https://doi.org/10.1080/09638280110066352, doi:10.1080/09638280110066352. This article has 326 citations and is from a peer-reviewed journal.

24. (werner1989riskfactorsfor pages 3-4): Robert A. Werner, Robert A. Werner, William P. Waring, William P. Waring, Gary Davidoff, and Gary Davidoff. Risk factors for median mononeuropathy of the wrist in postpoliomyelitis patients. Archives of physical medicine and rehabilitation, 70 6:464-7, Jun 1989. URL: https://doi.org/10.1016/0003-9993(89)90008-7, doi:10.1016/0003-9993(89)90008-7. This article has 56 citations and is from a highest quality peer-reviewed journal.

25. (werner1989riskfactorsfor pages 1-1): Robert A. Werner, Robert A. Werner, William P. Waring, William P. Waring, Gary Davidoff, and Gary Davidoff. Risk factors for median mononeuropathy of the wrist in postpoliomyelitis patients. Archives of physical medicine and rehabilitation, 70 6:464-7, Jun 1989. URL: https://doi.org/10.1016/0003-9993(89)90008-7, doi:10.1016/0003-9993(89)90008-7. This article has 56 citations and is from a highest quality peer-reviewed journal.

26. (tsai2009prevalenceandrisk pages 3-5): Hung-Chih Tsai, T. Hung, Chien-Cheng Chen, F. Lieu, Hsin Cho, T. Tung, and Szu-Fu Chen. Prevalence and risk factors for upper extremity entrapment neuropathies in polio survivors. Journal of rehabilitation medicine, 41 1:26-31, Jan 2009. URL: https://doi.org/10.2340/16501977-0290, doi:10.2340/16501977-0290. This article has 31 citations and is from a domain leading peer-reviewed journal.

27. (chang2025associationbetweenlowerlimb pages 9-10): Chun-Hui Chang, Hao-Yu Tseng, Wen-Tien Wu, Ru-Ping Lee, Jen-Hung Wang, and Kuang-Ting Yeh. Association between lower-limb fractures and carpal tunnel syndrome: a nationwide population-based cohort study. Healthcare, 13:2879, Nov 2025. URL: https://doi.org/10.3390/healthcare13222879, doi:10.3390/healthcare13222879. This article has 0 citations.

28. (chang2025associationbetweenlowerlimb pages 12-13): Chun-Hui Chang, Hao-Yu Tseng, Wen-Tien Wu, Ru-Ping Lee, Jen-Hung Wang, and Kuang-Ting Yeh. Association between lower-limb fractures and carpal tunnel syndrome: a nationwide population-based cohort study. Healthcare, 13:2879, Nov 2025. URL: https://doi.org/10.3390/healthcare13222879, doi:10.3390/healthcare13222879. This article has 0 citations.

29. (barnes2021costeffectivenessofopen pages 1-3): James I. Barnes, Gabrielle Paci, Thompson Zhuang, Laurence C. Baker, Steven M. Asch, and Robin N. Kamal. Cost-effectiveness of open versus endoscopic carpal tunnel release. The Journal of bone and joint surgery. American volume, 103 4:343-355, Dec 2021. URL: https://doi.org/10.2106/jbjs.19.01354, doi:10.2106/jbjs.19.01354. This article has 37 citations.

30. (gabrielli2020thedirectand pages 2-5): Alexandra S. Gabrielli, Alex C. Lesiak, and John R. Fowler. The direct and indirect costs to society of carpal tunnel release. HAND, 15:NP1-NP5, Nov 2020. URL: https://doi.org/10.1177/1558944718810855, doi:10.1177/1558944718810855. This article has 38 citations and is from a peer-reviewed journal.

31. (hubbard2018economicbenefitof pages 2-4): Zachary S. Hubbard, Tsun Yee Law, Samuel Rosas, Sarah C. Jernigan, and Harvey Chim. Economic benefit of carpal tunnel release in the medicare patient population. Neurosurgical focus, 44 5:E16, May 2018. URL: https://doi.org/10.3171/2018.1.focus17802, doi:10.3171/2018.1.focus17802. This article has 48 citations.

32. (hubbard2018economicbenefitof pages 1-2): Zachary S. Hubbard, Tsun Yee Law, Samuel Rosas, Sarah C. Jernigan, and Harvey Chim. Economic benefit of carpal tunnel release in the medicare patient population. Neurosurgical focus, 44 5:E16, May 2018. URL: https://doi.org/10.3171/2018.1.focus17802, doi:10.3171/2018.1.focus17802. This article has 48 citations.

33. (foley2007theeconomicburden pages 1-2): Michael Foley, Barbara Silverstein, and Nayak Polissar. The economic burden of carpal tunnel syndrome: long-term earnings of cts claimants in washington state. American journal of industrial medicine, 50 3:155-72, Mar 2007. URL: https://doi.org/10.1002/ajim.20430, doi:10.1002/ajim.20430. This article has 291 citations and is from a peer-reviewed journal.

34. (cheung2017ataleof pages 4-6): Kevin Cheung, Manraj N. Kaur, Tyson Tolliver, Christopher J. Longo, Nash H. Naam, and Achilles Thoma. A tale of two health-care systems: cost-utility analysis of open carpal tunnel release in canada and the united states. Plastic Surgery, 25:13-7, Feb 2017. URL: https://doi.org/10.1177/2292550317693817, doi:10.1177/2292550317693817. This article has 14 citations.

35. (hubbard2018economicbenefitof pages 5-6): Zachary S. Hubbard, Tsun Yee Law, Samuel Rosas, Sarah C. Jernigan, and Harvey Chim. Economic benefit of carpal tunnel release in the medicare patient population. Neurosurgical focus, 44 5:E16, May 2018. URL: https://doi.org/10.3171/2018.1.focus17802, doi:10.3171/2018.1.focus17802. This article has 48 citations.

36. (javed2025pakistanis“shoulder pages 1-2): M Javed, S Mustafa, and Z Khan. Pakistan is “shoulder to shoulder” in sharing the economic burden of rotator cuff disease in the world: a review of the current literature. Unknown journal, 2025.

37. (mather2013thesocietaland pages 1-3): Richard C. Mather, Lane Koenig, Daniel Acevedo, Timothy M. Dall, Paul Gallo, Anthony Romeo, John Tongue, and Gerald Williams. The societal and economic value of rotator cuff repair. Journal of Bone and Joint Surgery, 95:1993-2000, Nov 2013. URL: https://doi.org/10.2106/jbjs.l.01495, doi:10.2106/jbjs.l.01495. This article has 490 citations.

38. (parikh2021directandindirect pages 1-5): Niraj Parikh, Diane J. Martinez, Isabelle Winer, Laurie Costa, Deeksha Dua, and Paul Trueman. Direct and indirect economic burden associated with rotator cuff tears and repairs in the us. Current Medical Research and Opinion, 37:1199-1211, May 2021. URL: https://doi.org/10.1080/03007995.2021.1918074, doi:10.1080/03007995.2021.1918074. This article has 63 citations and is from a peer-reviewed journal.

39. (parikh2021directandindirect pages 9-12): Niraj Parikh, Diane J. Martinez, Isabelle Winer, Laurie Costa, Deeksha Dua, and Paul Trueman. Direct and indirect economic burden associated with rotator cuff tears and repairs in the us. Current Medical Research and Opinion, 37:1199-1211, May 2021. URL: https://doi.org/10.1080/03007995.2021.1918074, doi:10.1080/03007995.2021.1918074. This article has 63 citations and is from a peer-reviewed journal.

40. (mather2013thesocietaland pages 6-8): Richard C. Mather, Lane Koenig, Daniel Acevedo, Timothy M. Dall, Paul Gallo, Anthony Romeo, John Tongue, and Gerald Williams. The societal and economic value of rotator cuff repair. Journal of Bone and Joint Surgery, 95:1993-2000, Nov 2013. URL: https://doi.org/10.2106/jbjs.l.01495, doi:10.2106/jbjs.l.01495. This article has 490 citations.

41. (werner1989riskfactorsfor pages 4-4): Robert A. Werner, Robert A. Werner, William P. Waring, William P. Waring, Gary Davidoff, and Gary Davidoff. Risk factors for median mononeuropathy of the wrist in postpoliomyelitis patients. Archives of physical medicine and rehabilitation, 70 6:464-7, Jun 1989. URL: https://doi.org/10.1016/0003-9993(89)90008-7, doi:10.1016/0003-9993(89)90008-7. This article has 56 citations and is from a highest quality peer-reviewed journal.

42. (brungraber1976anoverviewof pages 13-17): Robert J Brungraber. An overview of floor slip-resistance research with annotated bibliography :: addendum. ArXiv, Jan 1976. URL: https://doi.org/10.6028/nbs.tn.895, doi:10.6028/nbs.tn.895. This article has 33 citations.

43. (pillaUnknownyearslipresistancemeasurement pages 3-4): S Di Pilla and K Vidal. Slip-resistance measurement. Unknown journal, Unknown year.

44. (brungraber1976anoverviewof pages 86-91): Robert J Brungraber. An overview of floor slip-resistance research with annotated bibliography :: addendum. ArXiv, Jan 1976. URL: https://doi.org/10.6028/nbs.tn.895, doi:10.6028/nbs.tn.895. This article has 33 citations.

45. (US11712394B1 pages 14-16): Anthony L. Spatorico. Shock absorbing ferrule for assisted ambulation. Patent (US), 2023.

46. (US11712394B1 pages 12-14): Anthony L. Spatorico. Shock absorbing ferrule for assisted ambulation. Patent (US), 2023.

47. (US11712394B1 pages 16-18): Anthony L. Spatorico. Shock absorbing ferrule for assisted ambulation. Patent (US), 2023.

48. (US11712394B1 pages 4-6): Anthony L. Spatorico. Shock absorbing ferrule for assisted ambulation. Patent (US), 2023.

49. (US11712394B1 pages 9-12): Anthony L. Spatorico. Shock absorbing ferrule for assisted ambulation. Patent (US), 2023.
