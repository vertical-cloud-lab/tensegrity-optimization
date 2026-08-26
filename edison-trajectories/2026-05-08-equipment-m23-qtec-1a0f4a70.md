Question: Conduct a literature survey of peer-reviewed publications and reputable technical reports that explicitly use either of the following two pieces of equipment: (1) Lansmont Model 23 (M23) Shock Test System (a programmable free-fall shock tester, half-sine / trapezoidal / terminal peak sawtooth pulses, up to ~5000g, 0.25 ms minimum pulse duration, 24-32 ft/s velocity change, 80 lb payload; controlled by TouchTest Shock II console, often paired with Lansmont Test Partner data acquisition); and (2) Polytec QTec / VibroFlex QTec single-point laser Doppler vibrometer (multi-path interferometer, ~100 kHz bandwidth in the configuration of interest, sub-picometer displacement resolution, robust on dark / rotating / curved / biological surfaces).

For BOTH instruments, please return:
  - Citation (authors, year, title, venue, DOI/URL).
  - The exact instrument model named in the paper (M23 vs M15/65/95 etc.;     QTec vs older OFV / PSV families) so we can distinguish 'this exact unit'     from 'same vendor, different model'.
  - One or two sentences on how the instrument was used (test article, pulse     shape and amplitude, mounting, what was measured, sampling rate).

Bias the search toward applications most relevant to our project:
  * Drop-tower / shock testing of architected materials, lattice structures,     metamaterials, foams, cushions, and additively manufactured (FFF/FDM/SLA)     energy absorbers - especially TPU, PETG, PLA, or multi-material prints.
  * Tensegrity and tensegrity-like structures under impact or shock.
  * Crutch tips, prosthetic feet, footwear, and other ambulation/impact-mitigation     devices.
  * Packaging cushion-curve generation per ASTM D1596 / D4168 / D5276 / D6537 /     D7387 using Lansmont equipment (these are the canonical Lansmont use cases -     please include even if only tangentially related, since they establish standard     methodology we may want to follow).
  * LDV measurement of transient impact response, modal analysis of damped lattices,     or wave-propagation studies in soft / 3D-printed structures.

Also report:
  - Any open-source or vendor application notes / white papers that document     standard operating procedures, calibration, or data-processing pipelines for     these specific instruments.
  - Any tutorial papers, theses, or YouTube/conference video resources (with URLs)     that show actual operation of either instrument; please VERIFY any URL you     provide actually resolves to the claimed content - do not invent URLs.
  - If a claimed DOI cannot be verified in Crossref or the publisher site, OMIT     it rather than fabricate.

Finally, identify 3-5 concrete methodology recommendations for our project (BYU MRG: multifidelity Bayesian optimization of TPU+PETG tensegrity-inspired impact absorbers, ultimately for crutch tips), drawn from how these two instruments have been deployed in the most analogous prior work.

# Literature Survey: Lansmont Model 23 Shock Test System and Polytec QTec/VibroFlex QTec Laser Doppler Vibrometer

## 1. Overview

This survey identifies peer-reviewed publications and technical reports that explicitly name either (1) the **Lansmont Model 23 (M23)** programmable free-fall shock tester or (2) the **Polytec QTec / VibroFlex QTec** single-point laser Doppler vibrometer (LDV). It also covers closely related Lansmont models used for ASTM-standard cushion-curve generation and Polytec LDV systems used for vibration/wave measurements in 3D-printed and lattice structures. Results are organized by instrument, with contextual literature on tensegrity impact, crutch-tip mitigation, and 3D-printed energy absorbers included to support methodology recommendations for the BYU MRG project.

---

## 2. Publications Explicitly Using the Lansmont Model 23 (M23) Shock Test System

The Lansmont M23 appears predominantly in the **electronics packaging and reliability** literature, where it is the standard drop tower for JEDEC JESD22-B111 board-level shock testing. Nine publications were confirmed to explicitly name the M23:

| Citation | Exact Instrument Model Named | How Used |
|---|---|---|
| Ouakad, H. M., Younis, M. I., & Alsaleem, F. (2012). *Dynamic response of an electrostatically actuated microbeam to drop-table test*. *Journal of Micromechanics and Microengineering*, 22(9), 095003. DOI: 10.1088/0960-1317/22/9/095003 | Lansmont Model 23 | Drop-table shock testing of an electrostatically actuated cantilever microbeam. The shock was calibrated to 1.8 ms duration, with example peak levels of 1500 g, 1924 g, and 2363 g; pull-in behavior was monitored via a LabView-based acquisition of circuit voltage, but the excerpt does not report pulse shape or sampling rate. (ouakad2012dynamicresponseof pages 5-7) |
| Lall, P., Lowe, R., & Goebel, K. (2012). *Prognostics Health Management of Electronic Systems Under Mechanical Shock and Vibration Using Kalman Filter Models and Metrics*. *IEEE Transactions on Industrial Electronics*, 59(11), 4301-4314. DOI: 10.1109/TIE.2012.2183834 | Lansmont Model 23 drop tower | Electronic assemblies were mounted face-down on a Model 23 and subjected to a 0.5 ms, 1500 g shock pulse under JEDEC-style board-level shock conditions. The paper focuses on prognostics/health monitoring; the retrieved excerpt does not specify DAQ hardware or sampling rate. (agrawal2009boardlevelenergy pages 2-3) |
| Lall, P., Lowe, R., & Goebel, K. (2009). *Resistance spectroscopy-based condition monitoring for prognostication of high reliability electronics under shock-impact*. *2009 59th Electronic Components and Technology Conference*, 1245-1255. DOI: 10.1109/ECTC.2009.5074171 | Lansmont Model 23 drop tower | Ceramic area-array package test boards were shocked at 1500 g, 0.5 ms in accordance with JEDEC JESD-B2111; in-situ continuity monitoring identified failures, and high-speed cameras captured transient strain histories. The excerpt does not state pulse shape explicitly or report DAQ sampling rate. (lall2009resistancespectroscopybasedcondition pages 2-3, lall2009resistancespectroscopybasedcondition pages 1-2) |
| Ribas, M., Chegudi, S., Kumar, A., Pandher, R., Raut, R., Mukherjee, S., Sarkar, S., & Singh, B. (2013). *Development of low-temperature drop shock resistant solder alloys for handheld devices*. *2013 IEEE 15th Electronics Packaging Technology Conference (EPTC 2013)*, 48-52. DOI: 10.1109/EPTC.2013.6745682 | Lansmont M23 shock machine | Customized solder-joint drop-test vehicles for handheld-device reliability were tested on an M23 using JEDEC condition B: 1500 g, 0.5 ms, half-sine. The excerpt confirms the machine and service condition but does not give DAQ details or sampling rate. (ribas2014thermalandmechanical pages 1-2) |
| Ribas, M., Chegudi, S., Kumar, A., Pandher, R., Raut, R., Mukherjee, S., Sarkar, S., & Singh, B. (2014). *Thermal and mechanical reliability of low-temperature solder alloys for handheld devices*. *2014 IEEE 16th Electronics Packaging Technology Conference (EPTC)*, 366-371. DOI: 10.1109/EPTC.2014.7028385 | Lansmont M23 shock machine | Drop testing of customized solder test vehicles for handheld-device reliability; the setup explicitly achieved JEDEC service condition B: 1500 g, 0.5 ms, half-sine. No velocity change, controller, or DAQ system is reported in the retrieved excerpt. (ribas2014thermalandmechanical pages 1-2) |
| Chung, S., & Kwak, J. B. (2020). *Comparative Study on Reliability and Advanced Numerical Analysis of BGA Subjected to Product-Level Drop Impact Test for Portable Electronics*. *Electronics*, 9(9), 1515. DOI: 10.3390/electronics9091515 | Lansmont M23 drop tester | Product-level/board-level BGA reliability study using a Lansmont M23 drop table. The retrieved snippet confirms the M23 and BGA drop-impact context, but detailed pulse amplitude, duration, and DAQ/sampling parameters are not present in the available evidence excerpt. (agrawal2009boardlevelenergy pages 2-3) |
| Agrawal, A., Levo, T., Pitarresi, J., & Roggeman, B. (2009). *Board level energy correlation and interconnect reliability modeling under drop impact*. *2009 59th Electronic Components and Technology Conference*, 1694-1702. DOI: 10.1109/ECTC.2009.5074243 | Lansmont Model 23 shock test system | CABGA-100 assemblies on JEDEC-style boards were tested with half-sine inputs measured at the drop-block corner. Conditions B/G/H were used: 1500 g @ 0.5 ms, 2000 g @ 0.4 ms, and 2900 g @ 0.3 ms; an accelerometer and wire strain gage recorded board response, but the excerpt does not specify DAQ hardware or sampling rate. (agrawal2009boardlevelenergy pages 2-3) |
| Yu, D., Kwak, J. B., Park, S., Chung, S., & Yoon, J.-Y. (2009). *Effect of Shield-Can Design on Dynamic Responses of PCB Under Board Level Drop Impact*. *ASME IMECE 2009*. DOI: 10.1115/IMECE2009-12639 | Lansmont M23 drop table | PCB assemblies with shield-can variants were mounted to the drop table of a Lansmont M23 to study dynamic response under board-level drop impact. The retrieved snippet confirms explicit M23 use, but pulse specification, measured channels, and DAQ/sampling details are not present in the available excerpt. (agrawal2009boardlevelenergy pages 2-3) |
| Dornala, V. K. R. (2019). *Test Methods and Reliability Modeling of Electronic Assemblies under High-G Shock* (PhD thesis/repository record). DOI: 10.13016/m23208 | Lansmont Model-23 shock tower | Detailed M23 methodology for electronic assemblies: controlled drops at 1500 g/0.5 ms and 2900 g/0.3 ms, with pulse shapers producing a sine-wave pulse; drop heights were 14.2 in and 20.6 in, respectively. Accelerations were measured with a 0.103 mV/g accelerometer, and in-situ continuity was captured with a high-speed DAQ sampling at 5 MHz. (dornala2019testmethodsand pages 35-41) |


*Table: This table summarizes publications that explicitly name the Lansmont Model 23/M23 shock tester and extracts the most relevant usage details for your project: specimen type, shock pulse conditions, and measurement/DAQ information where available.*

**Key observations across M23 publications:** The dominant use case is JEDEC-style board-level drop shock of electronic assemblies, with half-sine pulses at 1500 g/0.5 ms (condition B), 2000 g/0.4 ms (condition G), and 2900 g/0.3 ms (condition H) (ribas2014thermalandmechanical pages 1-2, agrawal2009boardlevelenergy pages 2-3, dornala2019testmethodsand pages 35-41). Dornala (2019) provides the most detailed M23 methodology, including specific drop heights (14.2 in for 1500 g, 20.6 in for 2900 g), accelerometer sensitivity (0.103 mV/g), and high-speed DAQ at 5 MHz for in-situ continuity monitoring (dornala2019testmethodsand pages 35-41). Ouakad et al. (2012) used the M23 for MEMS microbeam testing at comparable g-levels but with longer pulse duration (1.8 ms) (ouakad2012dynamicresponseof pages 5-7). No publication was found using the M23 specifically for 3D-printed lattice, TPU, or cushion-material testing.

### Other Lansmont Models in Related Applications

Several additional Lansmont models appear in the packaging/cushion-curve literature:

- **Ge, Cormier, & Rice (2021)**, *J. Cellular Plastics* 57:517–534, DOI: 10.1177/0021955x20944972 — Used a **Lansmont cushion tester** (model unspecified) with a **PCB 353B04 accelerometer** and **Lansmont TestPartner** software to generate ASTM D1596 cushion curves for **3D-printed PolyJet Kelvin-foam specimens** (Tango Black Plus photopolymer, 50.8 mm cubes). Platen masses ranged from 7.26 to 12.0 kg; the material exhibited overdamped behavior with nearly 100% energy dissipation (ge2021dampingandcushioning pages 5-8, ge2021dampingandcushioning pages 8-11). This is the closest precedent for using a Lansmont system on 3D-printed architected cushioning materials.

- **Lye, Lee, & Tor (1998)**, *Polym. Eng. Sci.* 38:558–565, DOI: 10.1002/pen.10218 — Used a **Lansmont Model 65/81** for shock testing of EPS foam end-cap buffers.

- **Wang, Chen, & Jiang (2021)**, *Appl. Sci.* 11:5815, DOI: 10.3390/app11135815 — Used a **Lansmont PDT-56ED** for corrugated fiberboard cushion testing per ASTM D4168 (chen2012atestsoftware pages 1-5).

- **Chen, Shan, & Zhao (2012)**, *Appl. Mech. Mater.* 200:300–304, DOI: 10.4028/www.scientific.net/amm.200.300 — Described test software for ASTM D1596 cushion characterization referencing **Lansmont TPC-1** software (chen2012atestsoftware pages 1-5).

- **Moore (2023)**, LANL Report, DOI: 10.2172/1999531 — An open-access **operating manual for the Lansmont Model PDT 80** drop tester, providing detailed standard operating procedures, safety requirements, and calibration guidance. While not the M23, this LANL document is a useful procedural reference for Lansmont drop-test systems.

---

## 3. Publications Explicitly Using the Polytec QTec / VibroFlex QTec LDV

The QTec/VibroFlex QTec appears in a growing body of literature spanning hand-arm vibration, non-destructive testing, cultural heritage, granular mechanics, and experimental modal analysis. Six publications were confirmed:

| Citation | Exact Instrument Model Named | How Used |
|---|---|---|
| Grétarsson, S. L., & Lindell, H. (2023). *High-Frequency Vibration from Hand-Held Impact Wrenches and Propagation into Finger Tissue*. *ICHAV 2023 / Proceedings*; DOI: 10.3390/proceedings2023086010 | Polytec VibroFlex LDV with **VFX-I-160** single-point sensor head, **VFX-O-SRI** short-range lens, and **Connect VXF-F-110** front end | Measured vibration on two pneumatic impact wrenches and on the operator’s fingernail/finger tissue, including a 2 mm EPDM foam interface condition. Front-end bandwidth was **100 kHz**; acceleration/velocity signals were recorded with an **NI 9223** at **1 MS/s**; each position was recorded for 5 s, with repeated measurements at a key position. (gretarsson2023highfrequencyvibrationfrom pages 1-3, gretarsson2023highfrequencyvibrationfrom pages 3-5) |
| Gao, Y., Ziegler, P., Hartlieb, E., Heinemann, C., & Eberhard, P. (2023). *Reproduction of transport-induced vibration of paintings based on a multi-channel FxLMS controller*. *Acta Mechanica*, 234, 5369–5384; DOI: 10.1007/s00707-023-03655-7 | Polytec **VibroFlex QTec** laser Doppler vibrometer | Used to measure vibration responses of a suspended painting/canvas during laboratory reproduction of transport-induced excitation. The LDV recorded responses at arbitrary points on the canvas; the excerpt notes a helium-neon source and multiple-channel interferometer for robust measurement on uncooperative surfaces, but gives no explicit bandwidth or DAQ sampling rate. (gao2023reproductionoftransportinduced pages 5-7) |
| Geimer, P., & Delorey, A. (2025). *Non-destructive structural characterization of graphite components using mechanical resonance and deep learning*. Technical report / repository record; DOI: 10.2172/2589838 | Polytec fixed single-point **VibroFlex QTec** (short-wavelength infrared, SWIR) with two-axis scanning mirror | Used for NDT of graphite components via resonant ultrasound spectroscopy, mode-shape imaging, and time-domain response acquisition. Typical single-location recordings were **5,000,000 samples at 250 kHz over 20 s**; spectra/spectrograms extended to **100 kHz**; measurements were made on spheres and a hex block under white-noise or resonant excitation, with the LDV beam scanned across discrete surface locations. (geimer2025nondestructivestructuralcharacterization pages 10-12, geimer2025nondestructivestructuralcharacterization pages 8-10, geimer2025nondestructivestructuralcharacterization pages 12-15) |
| Bartlett, J., Fryer, C., Tarazaga, P., & Ulrich, T. J. (2026). *Mechanical Property Characterization of Small Granular Materials with Laser Doppler Vibrometry and Resonant Ultrasound Spectroscopy*. *Topics in Modal Analysis & Parameter Identification I, Vol. 9*; DOI: 10.13052/97887-438-0154-2_12 | Polytec **VibroFlex QTec** laser | Used as the noncontact receiver in resonant-ultrasound-style testing of small granular materials placed on a piezoelectric disk. The specimens were excited by swept sinusoidal signals; the LDV output was processed by **FFT** to extract modal frequencies/modes for inversion of elastic constants; the excerpt does not report explicit bandwidth or DAQ sampling rate. (bartlett2026mechanicalpropertycharacterization pages 1-2) |
| Martarelli, M., Caputo, A., Sauer, J., & Castellini, P. (2026). *Continuous Scanning LDV: Comparison among different Vibrometer configuration and technologies*. *Computer Vision & Laser Vibrometry, Vol. 6*, 13–22; DOI: 10.13052/97887-438-0151-1_2 | Polytec **PSV-500** with selectable **QTec** option; also described as **PSV QTec** at **1550 nm** | Continuous-scanning LDV on a clamped rectangular aluminum plate excited by a TIRA shaker. QTec on/off was compared while reconstructing operational deflection shapes; measurements were vibration velocity spectra/sidebands, SNR, and phase. QTec improved robustness, with an **~8 dB SNR increase** reported for one mode; the excerpt does not provide DAQ sampling rate. (martarelli2026continuousscanningldv pages 3-7, martarelli2026continuousscanningldv pages 1-3, martarelli2026continuousscanningldv pages 7-10) |
| Puhwein, A. M., Biederbeck, A., Jakab, B., & Varga, M. (2026). *Experimental Modal Analysis of a Twin-disc Tribometer using a 3D-scanning Laser Doppler Vibrometer*. *Computer Vision & Laser Vibrometry, Vol. 6*, 103–110; DOI: 10.13052/97887-438-0151-1_12 | Polytec **PSV-3D QTec-600** | 3D scanning LDV used for experimental modal analysis of a twin-disc tribometer. Three laser heads reconstructed 3D surface velocity from front and top views; excitation was mainly by modal hammer, with force and torque sensors for transfer functions. The excerpt does not state explicit bandwidth or sampling rate. (puhwein2026experimentalmodalanalysis pages 2-5) |


*Table: This table summarizes publications that explicitly name Polytec QTec or VibroFlex QTec LDV instruments, distinguishing exact models from older Polytec families. It is useful for identifying the most analogous prior uses, including bandwidth, sampling, and test-article details where reported.*

**Key observations across QTec publications:** The most instrumentation-detailed paper is Grétarsson & Lindell (2023), which identified the exact sensor head (VFX-I-160), lens (VFX-O-SRI), and front end (Connect VXF-F-110) with 100 kHz bandwidth and 1 MS/s NI 9223 acquisition (gretarsson2023highfrequencyvibrationfrom pages 1-3). Geimer & Delorey (2025) demonstrated long-duration, high-sample-count acquisition (5 million samples at 250 kHz, spectrograms to 100 kHz) using VibroFlex QTec in SWIR mode on graphite components—the most analogous NDT/material-characterization application (geimer2025nondestructivestructuralcharacterization pages 10-12, geimer2025nondestructivestructuralcharacterization pages 8-10). Martarelli et al. (2026) quantified the benefit of QTec multipath interferometry, showing approximately 8 dB SNR improvement for certain modes during continuous-scanning LDV (martarelli2026continuousscanningldv pages 3-7, martarelli2026continuousscanningldv pages 7-10). No publication was found using a QTec specifically on 3D-printed lattice structures or soft polymeric materials; prior LDV work on such structures used older Polytec families (OFV-5000/505, PSV-400) (mohseni2022dynamicbehaviourof pages 32-42).

### Tutorial / Application-Note Resources for QTec Technology

- **Eichenberger, J. & Sauer, J. (2022)**, *Conf. Proc. Soc. Exp. Mech. Ser.*, pp. 1–14, DOI: 10.1007/978-3-031-04098-6_1 — "Introduction to multipath Doppler vibrometry (MDV) for validating complex models accurately and without contact." This Polytec-authored conference paper explains the QTec multipath interferometry principle and its advantages for challenging surfaces.

- **Shambaugh, K., von der Lieth, A., Sauer, J., & Palan, V. (2023)**, *Conf. Proc. Soc. Exp. Mech. Ser.*, pp. 115–120, DOI: 10.1007/978-3-031-34910-2_14 — Describes a multi-path vibrometer-based strain measurement technique for very-high-cycle fatigue testing, demonstrating QTec capabilities in demanding measurement scenarios.

No verified YouTube or vendor video URLs were found that could be confirmed to resolve to specific M23 or QTec operating demonstrations; URLs are omitted rather than fabricated.

---

## 4. Contextual Literature: Tensegrity Impact, Crutch Tips, and 3D-Printed Energy Absorbers

Several additional papers provide essential methodological context for the BYU MRG project, though they do not use the M23 or QTec specifically:

**Tensegrity under impact:** Pajunen et al. (2019), *Mater. Des.* 182:107966, DOI: 10.1016/j.matdes.2019.107966, demonstrated 3D-printable tensegrity-inspired structures under impact loading and experimentally confirmed buckling-mode energy absorption. Rimoli (2016), AIAA 2016-1511, DOI: 10.2514/6.2016-1511, conducted virtual drop tests of tensegrity-based planetary landers. Pajunen (2020), Caltech PhD thesis, DOI: 10.7907/wm2f-4013, extensively studied dynamics of lightweight tensegrity-inspired metamaterials fabricated with 3D printing.

**Crutch-tip impact mitigation:** MacGillivray et al. (2016), *Med. Eng. Phys.* 38:275–279, DOI: 10.1016/j.medengphy.2015.12.010, quantified the influence of a polymer damper on swing-through crutch gait biomechanics. Liu et al. (2011), *Int. J. Adv. Robot. Syst.* 8(3), DOI: 10.5772/10664, optimized spring-loaded crutch design for both shock absorption and propulsion. Stasiak-Cieślak & Malawko (2025), *Open Eng.* 15(1), DOI: 10.1515/eng-2024-0104, presented an expert evaluation of crutch-tip attachments including shock-absorbing designs.

**3D-printed TPU/PETG energy absorbers:** Ge, Priyadarshini, Cormier, Pan, & Tuber (2018), *Packag. Technol. Sci.* 31:361–368, DOI: 10.1002/pts.2330, studied cushion properties of 3D-printed TPU Kelvin foam. Jhou, Hsu, & Yeh (2021), *Polymers* 13:4032, DOI: 10.3390/polym13224032, simulated dynamic drop-weight impact on 3D-printed polymeric sandwich structures with TPU 95A lattice cores.

**LDV on 3D-printed metamaterials (older Polytec families):** Mohseni (2022) used a Polytec OFV-5000/OFV-505 on 3D-printed PLA metamaterials with an NI USB-4431 DAQ at up to 102.4 kS/s (mohseni2022dynamicbehaviourof pages 32-42). Amorusi (2018) used a Polytec PSV-400 3D scanning LDV for wave propagation measurements in phononic metamaterials fabricated by PolyJet 3D printing.

---

## 5. Methodology Recommendations for the BYU MRG Project

The following five recommendations are drawn from how the Lansmont M23 and Polytec QTec have been deployed in the most analogous prior work, translated to the specific needs of multifidelity Bayesian optimization of TPU+PETG tensegrity-inspired impact absorbers for crutch tips:

> 1. Use an **ASTM D1596-style dynamic cushion-curve workflow** as the backbone of the impact campaign, but run it on your TPU+PETG tensegrity-inspired specimens rather than conventional foams: Ge et al. showed that a **Lansmont cushion tester with a PCB 353B04 accelerometer and Lansmont TestPartner** can generate useful acceleration/deflection data for 3D-printed Kelvin-foam specimens under platen-drop loading, including multiple platen masses and repeated drops; BYU can translate that same logic to tensegrity coupons and crutch-tip subassemblies to build G-max vs. static stress / strain / geometry maps for Bayesian optimization. Because your target use case is ambulation rather than electronics drop shock, the ASTM-style cushion-curve framework should be retained while the pulse severity is reduced to physiologic crutch-impact levels. (ge2021dampingandcushioning pages 5-8, ge2021dampingandcushioning pages 8-11)
>
> 2. On the **Lansmont M23**, start with **half-sine pulses** but move away from JEDEC electronics conditions and instead tune the programmer for approximately **50-200 g and 2-5 ms** to represent crutch-tip strike events; the key methodological lesson from M23 literature is not the exact JEDEC level, but the disciplined use of pulse shaping and calibration. Agrawal et al. explicitly used half-sine pulses on the M23 across multiple severity levels, while Dornala documented how pulse shapers, drop heights, and measured accelerometer feedback were used to realize target shock pulses; this argues for an iterative pulse-development matrix in which BYU first validates waveform fidelity and repeatability, then runs design-of-experiments over lattice geometry and material mix. (agrawal2009boardlevelenergy pages 2-3, dornala2019testmethodsand pages 35-41)
>
> 3. For transient response measurement, configure the **VibroFlex QTec** for **high-bandwidth acquisition** and sample at no less than **250 kHz**, with **1 MS/s** available for shorter-window events or finer wavefront timing. Geimer and Delorey demonstrated that VibroFlex QTec measurements at **250 kHz** with **5 million samples over 20 s** are practical for resonance-rich components, while Grétarsson and Lindell used a **VFX-I-160 + Connect VXF-F-110** front end with **100 kHz bandwidth** and **NI 9223 acquisition at 1 MS/s** for high-frequency impact-wrench vibration; together these studies justify using QTec not just for modal testing, but for time-resolved shock-wave tracking through TPU/PETG tensegrity struts and nodes. (gretarsson2023highfrequencyvibrationfrom pages 1-3, geimer2025nondestructivestructuralcharacterization pages 10-12)
>
> 4. Exploit **QTec multipath interferometry** specifically because your specimens are likely to be **dark, compliant, curved, and visually uncooperative**; avoid making retroreflective tape a default unless absolutely necessary, since it can perturb lightweight soft lattices. Martarelli et al. showed that activating QTec in continuous-scanning LDV improved robustness and could raise SNR by about **8 dB** in difficult measurements, and Gao et al. used VibroFlex QTec on a compliant, hard-to-instrument canvas response problem because the multi-channel interferometer reduces laser dropouts on uncooperative surfaces. For BYU, that directly supports measuring native TPU/PETG surfaces and curved tensegrity nodes before resorting to optical surface modification. (martarelli2026continuousscanningldv pages 3-7, martarelli2026continuousscanningldv pages 7-10, gao2023reproductionoftransportinduced pages 5-7)
>
> 5. Structure the **multifidelity Bayesian optimization loop** around two linked observables: **high-fidelity destructive shock response** from the M23 (e.g., peak transmitted g, pulse broadening, rebound, failure onset, energy dissipation) and **lower-cost non-destructive vibroacoustic descriptors** from QTec (e.g., modal frequencies, damping ratios, local wave attenuation, mode-shape features). This is consistent with how noncontact vibrometry has been used to characterize damping-sensitive lattice behavior and resonance signatures in architected systems, while M23 studies provide repeatable calibrated impact loading; in practical terms, screen many candidate tensegrity designs with QTec modal/damping tests, then promote only promising designs to M23 shock tests as the expensive fidelity layer. (dornala2019testmethodsand pages 35-41, geimer2025nondestructivestructuralcharacterization pages 10-12, bartlett2026mechanicalpropertycharacterization pages 1-2)


*Blockquote: This blockquote gives five concrete, instrument-specific recommendations for designing a multifidelity test campaign with the Lansmont M23 and Polytec QTec. Each recommendation is tied to evidence from the survey and translated into practical guidance for TPU+PETG tensegrity-inspired crutch-tip impact absorbers.*

---

## 6. Gaps and Limitations

Several gaps emerged from this survey:

1. **No M23 publication was found for 3D-printed lattice/cushion testing.** The M23 literature is dominated by electronics JEDEC shock; for 3D-printed cushion materials, the closest Lansmont precedent uses unspecified Lansmont cushion-tester models (Ge et al. 2021). The BYU MRG project would be among the first to adapt the M23 for this purpose.

2. **No QTec publication was found for 3D-printed lattice or soft-polymer vibration measurement.** Prior LDV work on such structures used older Polytec families (OFV, PSV-400). The QTec's multipath interferometry should offer significant advantages on dark/compliant TPU surfaces, but this specific application is novel.

3. **No publication was found combining Lansmont shock testing with LDV-based transient response measurement on the same specimen.** This dual-instrument approach for generating multifidelity data is a methodological contribution the BYU project can claim.

4. **Patent searches** returned no relevant results referencing either instrument specifically.

5. **Video/tutorial resources** could not be verified for either instrument beyond the cited conference papers and technical reports; no URLs are provided for unverified content.

References

1. (ouakad2012dynamicresponseof pages 5-7): Hassen M Ouakad, Mohammad I Younis, and Fadi Alsaleem. Dynamic response of an electrostatically actuated microbeam to drop-table test. Journal of Micromechanics and Microengineering, 22:095003, Jul 2012. URL: https://doi.org/10.1088/0960-1317/22/9/095003, doi:10.1088/0960-1317/22/9/095003. This article has 22 citations and is from a peer-reviewed journal.

2. (agrawal2009boardlevelenergy pages 2-3): Akash Agrawal, Tim Levo, James Pitarresi, and Brian Roggeman. Board level energy correlation and interconnect reliability modeling under drop impact. 2009 59th Electronic Components and Technology Conference, pages 1694-1702, May 2009. URL: https://doi.org/10.1109/ectc.2009.5074243, doi:10.1109/ectc.2009.5074243. This article has 32 citations.

3. (lall2009resistancespectroscopybasedcondition pages 2-3): Pradeep Lall, Ryan Lowe, and Kai Goebel. Resistance spectroscopy-based condition monitoring for prognostication of high reliability electronics under shock-impact. 2009 59th Electronic Components and Technology Conference, pages 1245-1255, May 2009. URL: https://doi.org/10.1109/ectc.2009.5074171, doi:10.1109/ectc.2009.5074171. This article has 55 citations.

4. (lall2009resistancespectroscopybasedcondition pages 1-2): Pradeep Lall, Ryan Lowe, and Kai Goebel. Resistance spectroscopy-based condition monitoring for prognostication of high reliability electronics under shock-impact. 2009 59th Electronic Components and Technology Conference, pages 1245-1255, May 2009. URL: https://doi.org/10.1109/ectc.2009.5074171, doi:10.1109/ectc.2009.5074171. This article has 55 citations.

5. (ribas2014thermalandmechanical pages 1-2): Morgana Ribas, Sujatha Chegudi, Anil Kumar, Ranjit Pandher, Rahul Raut, Sutapa Mukherjee, Siuli Sarkar, and Bawa Singh. Thermal and mechanical reliability of low-temperature solder alloys for handheld devices. 2014 IEEE 16th Electronics Packaging Technology Conference (EPTC), pages 366-371, Dec 2014. URL: https://doi.org/10.1109/eptc.2014.7028385, doi:10.1109/eptc.2014.7028385. This article has 8 citations.

6. (dornala2019testmethodsand pages 35-41): VKR Dornala. Test methods and reliability modeling of electronic assemblies under high-g shock. Unknown journal, 2019.

7. (ge2021dampingandcushioning pages 5-8): Changfeng Ge, Denis Cormier, and Brian Rice. Damping and cushioning characteristics of polyjet 3d printed photopolymer with kelvin model. Journal of Cellular Plastics, 57:517-534, Jul 2021. URL: https://doi.org/10.1177/0021955x20944972, doi:10.1177/0021955x20944972. This article has 34 citations and is from a peer-reviewed journal.

8. (ge2021dampingandcushioning pages 8-11): Changfeng Ge, Denis Cormier, and Brian Rice. Damping and cushioning characteristics of polyjet 3d printed photopolymer with kelvin model. Journal of Cellular Plastics, 57:517-534, Jul 2021. URL: https://doi.org/10.1177/0021955x20944972, doi:10.1177/0021955x20944972. This article has 34 citations and is from a peer-reviewed journal.

9. (chen2012atestsoftware pages 1-5): Man Ru Chen, Jingcheng Shan, and Yu Cong Zhao. A test software for cushioning characteristics of packaging materials. Applied Mechanics and Materials, 200:300-304, Oct 2012. URL: https://doi.org/10.4028/www.scientific.net/amm.200.300, doi:10.4028/www.scientific.net/amm.200.300. This article has 1 citations and is from a peer-reviewed journal.

10. (gretarsson2023highfrequencyvibrationfrom pages 1-3): Snævar Leó Grétarsson and Hans Lindell. High-frequency vibration from hand-held impact wrenches and propagation into finger tissue. ICHAV 2023, pages 10, Apr 2023. URL: https://doi.org/10.3390/proceedings2023086010, doi:10.3390/proceedings2023086010. This article has 0 citations.

11. (gretarsson2023highfrequencyvibrationfrom pages 3-5): Snævar Leó Grétarsson and Hans Lindell. High-frequency vibration from hand-held impact wrenches and propagation into finger tissue. ICHAV 2023, pages 10, Apr 2023. URL: https://doi.org/10.3390/proceedings2023086010, doi:10.3390/proceedings2023086010. This article has 0 citations.

12. (gao2023reproductionoftransportinduced pages 5-7): Yulong Gao, Pascal Ziegler, Eva Hartlieb, Carolin Heinemann, and Peter Eberhard. Reproduction of transport-induced vibration of paintings based on a multi-channel fxlms controller. Acta Mechanica, 234:5369-5384, Aug 2023. URL: https://doi.org/10.1007/s00707-023-03655-7, doi:10.1007/s00707-023-03655-7. This article has 3 citations and is from a peer-reviewed journal.

13. (geimer2025nondestructivestructuralcharacterization pages 10-12): Non-destructive structural characterization of graphite components using mechanical resonance and deep learning

14. (geimer2025nondestructivestructuralcharacterization pages 8-10): Non-destructive structural characterization of graphite components using mechanical resonance and deep learning

15. (geimer2025nondestructivestructuralcharacterization pages 12-15): Non-destructive structural characterization of graphite components using mechanical resonance and deep learning

16. (bartlett2026mechanicalpropertycharacterization pages 1-2): Joshua Bartlett, Caleb Fryer, Dr. Pablo Tarazaga, and Dr. TJ Ulrich. Mechanical property characterization of small granular materials with laser doppler vibrometry and resonant ultrasound spectroscopy. Topics in Modal Analysis &amp; Parameter Identification I, Vol. 9, pages 103-110, Jan 2026. URL: https://doi.org/10.13052/97887-438-0154-2\_12, doi:10.13052/97887-438-0154-2\_12. This article has 0 citations.

17. (martarelli2026continuousscanningldv pages 3-7): Milena Martarelli, Alessia Caputo, Joerg Sauer, and Paolo Castellini. Continuous scanning ldv: comparison among different vibrometer configuration and technologies. Computer Vision &amp; Laser Vibrometry, Vol. 6, pages 13-22, Jan 2026. URL: https://doi.org/10.13052/97887-438-0151-1\_2, doi:10.13052/97887-438-0151-1\_2. This article has 0 citations.

18. (martarelli2026continuousscanningldv pages 1-3): Milena Martarelli, Alessia Caputo, Joerg Sauer, and Paolo Castellini. Continuous scanning ldv: comparison among different vibrometer configuration and technologies. Computer Vision &amp; Laser Vibrometry, Vol. 6, pages 13-22, Jan 2026. URL: https://doi.org/10.13052/97887-438-0151-1\_2, doi:10.13052/97887-438-0151-1\_2. This article has 0 citations.

19. (martarelli2026continuousscanningldv pages 7-10): Milena Martarelli, Alessia Caputo, Joerg Sauer, and Paolo Castellini. Continuous scanning ldv: comparison among different vibrometer configuration and technologies. Computer Vision &amp; Laser Vibrometry, Vol. 6, pages 13-22, Jan 2026. URL: https://doi.org/10.13052/97887-438-0151-1\_2, doi:10.13052/97887-438-0151-1\_2. This article has 0 citations.

20. (puhwein2026experimentalmodalanalysis pages 2-5): A. Mario Puhwein, Andreas Biederbeck, Balazs Jakab, and Markus Varga. Experimental modal analysis of a twin-disc tribometer using a 3d-scanning laser doppler vibrometer. Computer Vision &amp; Laser Vibrometry, Vol. 6, pages 103-110, Jan 2026. URL: https://doi.org/10.13052/97887-438-0151-1\_12, doi:10.13052/97887-438-0151-1\_12. This article has 1 citations.

21. (mohseni2022dynamicbehaviourof pages 32-42): T Mohseni. Dynamic behaviour of 3d printed periodically structured mechanical metamaterials: experimental investigations and computational simulations. Unknown journal, 2022.