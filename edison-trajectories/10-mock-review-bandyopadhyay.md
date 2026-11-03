# Edison trajectory 10 — Mock reviewer: Amit Bandyopadhyay

- **Task ID:** `5b6de9f1-f1e6-454b-9196-ffac673c0ffb`
- **Job type:** `LITERATURE` (low-effort, round-2 organizer-persona mock review)
- **Status:** `success`
- **Edison link:** https://platform.edisonscientific.com/tasks/5b6de9f1-f1e6-454b-9196-ffac673c0ffb

Second-round mock program-committee review of [`crutch-tip-abstract.md`](../crutch-tip-abstract.md),
in the voice of TMS 2027 *Biomedical Materials and Devices: From Laboratory to Market* organizer
**Amit Bandyopadhyay**. Verbatim `formatted_answer` below; full structured response in the sibling `.json`.

---

Question: You are Prof. Amit Bandyopadhyay (Washington State University), an expert in additive manufacturing of biomaterials, multi-material and functionally graded AM, laser/directed-energy-deposition processing, and natural medicinal compounds in medical devices. You care about multi-material interface integrity, compositional/architectural gradients, processing-structure-property relationships, and whether the multi-material FFF PETG-TPU interface is mechanically and biologically sound.

Act as THIS SPECIFIC named reviewer on the TMS 2027 symposium program committee and give a candid, in-voice mock review of the abstract below. Provide: (1) a scorecard (novelty, technical merit, fit-to-symposium-scope, clarity, lab-to-market strength, evidence sufficiency, each /5) with a one-line accept/borderline/reject leaning; (2) the single most-likely question you would ask at the podium, in your voice and area of expertise; (3) the top improvement you would want, grounded in your expertise; (4) a short fact-check / overstatement flag on any claim that would bother you; (5) a scope-fit judgment (does this belong in this symposium, and how to reposition it to fit your priorities); (6) 2-3 concrete drop-in rewrite suggestions (each <=25 words) that keep the abstract within the 150-word TMS limit. Cite literature where useful.

TARGET SYMPOSIUM: TMS 2027 "Biomedical Materials and Devices: From Laboratory to Market". Scope (verbatim): Innovation in biomaterials and medical devices has saved millions of lives, but a big disconnect exists between academic laboratory research and bringing devices to market; the symposium focuses on knowledge transfer among academia, industry, regulatory bodies, and end users (physicians, funding agencies). Topics include intelligent manufacturing methods, applications of AI/ML in manufacturing biomedical devices, and innovative characterization tools that better correlate in-vitro to in-vivo performance. Named challenges skew toward implants: mitigating implant infection, minimizing anisotropy of additively manufactured materials, improving fatigue resistance of AM metallic implants, biodegradable metallic implant alloys, biocompatibility of alloys, natural medicinal compounds, bioprinting personalized implants, high-strength biodegradable ceramics, and smart charge-generating implants. It also runs multidisciplinary panel discussions. NOTE: this abstract is a polymer fused-filament-fabrication ASSISTIVE-DEVICE (external, skin-contact crutch tip), which is scope-ADJACENT to that implant-heavy list; assess fit candidly.

IMPORTANT CONSTRAINT: We do NOT yet have measured experimental data (SEA in J/g, %-force-reduction); the abstract is due tonight. The abstract deliberately states the benchmark it aims to EXCEED (a rubber ferrule that transmits >95% of applied load) rather than claiming any measured result. Please review it as an intent/design-study abstract on that basis; do NOT penalize it for lacking a specific measured number, but DO advise how to frame the not-yet-measured performance most defensibly.

TITLE: Closed-Loop Bayesian Optimization of Multi-Material 3D-Printed Tensegrity Crutch-Tip Impact Absorbers

ABSTRACT (150 words): Long-term crutch users load each crutch to ~0.5 body weights during partial-weight-bearing gait and experience substantial upper-extremity overuse injury, including crutch palsy, shoulder impingement, and carpal tunnel syndrome; commercial crutch tips predominantly use rubber ferrules, while existing spring-loaded dampers add bulk without architected tunability. We apply closed-loop, multi-objective Bayesian optimization to design a crutch-tip insert from multi-material fused-filament-fabrication tensegrity-inspired lattices, pairing rigid PETG struts with elastomeric TPU elements to exploit buckling-induced load-limiting plateaus and TPU viscoelastic hysteresis. Within the standard 19-25 mm crutch-shaft interface, we co-optimize unit-cell topology, strut diameter, relative density, and prestress to maximize specific energy absorption and minimize peak transmitted force across quasi-static compression and drop-weight impact, aiming to exceed a rubber-ferrule baseline that transmits over 95% of applied load. Prior-art review identified no tensegrity-based crutch-tip absorber; an anticipated Class I (21 CFR 890.3790), ISO 11334-1 pathway guides verification. Crutch abandonment exceeds 30%, motivating distributed, patient-tunable manufacturing.


# Mock Review — Prof. Amit Bandyopadhyay (Washington State University)
## TMS 2027 "Biomedical Materials and Devices: From Laboratory to Market"

**Abstract Under Review:** "Closed-Loop Bayesian Optimization of Multi-Material 3D-Printed Tensegrity Crutch-Tip Impact Absorbers"

---

## (1) Scorecard

| Criterion | Score (/5) | Brief justification |
|---|---:|---|
| Novelty | 4.0 | Multi-material PETG-TPU tensegrity for a crutch-tip absorber appears genuinely new in the crutch literature/patent space; however, tensegrity energy absorption and Bayesian optimization of lattices are each already established separately (pajunen2019designandimpact pages 4-5, pajunen2019designandimpact pages 1-2). |
| Technical Merit | 3.5 | The mechanics premise is credible: buckling-induced load-limiting plateaus and reusable energy absorption are well supported in tensegrity-inspired structures. My concern is the PETG-TPU interface—rigid/soft FFF adhesion can be incomplete and process-sensitive, with delamination risk and no cyclic/fatigue evidence here yet (pajunen2019designandimpact pages 7-8, yilmaz2026investigationofmechanical pages 9-10, seregi2026investigationofpolymer pages 2-4). |
| Fit-to-Symposium-Scope | 2.5 | This symposium is primarily implant- and biomaterials-focused, especially metallic AM and translational implant challenges. A polymer FFF external crutch tip is adjacent rather than central, though the AI/ML manufacturing and pathway-to-market framing provide a partial fit. |
| Clarity | 4.0 | The abstract is concise, technically dense, and uses the 150-word limit efficiently. Regulatory framing and benchmark targeting are helpful; minor ambiguity remains around whether the design is truly tensegrity or only tensegrity-inspired. |
| Lab-to-Market Strength | 3.5 | Mention of the Class I device pathway, ISO 11334-1 relevance, and distributed manufacturing is a strength. Still missing are cost/manufacturability analysis, verification details tied to standards, and any user or clinician feedback plan (mottaghi2025opensource3dprintable pages 1-6). |
| Evidence Sufficiency | 2.5 | As a design-intent abstract, the lack of measured performance is acceptable if framed carefully. Still, the >95% rubber-ferrule benchmark is not well substantiated in the literature provided, and there are no experimental interface, impact, or durability data yet. |
| Overall leaning | Borderline Accept | I would lean **BORDERLINE ACCEPT**: interesting and potentially market-relevant, but marginal on symposium fit and presently weak on the most important materials question—the PETG-TPU interface integrity under repeated service loading. |


*Table: This table summarizes an in-voice scorecard for the abstract as Prof. Amit Bandyopadhyay might assess it, emphasizing novelty, scope fit, translational framing, and the unresolved PETG-TPU interface concern.*

**Overall Leaning: BORDERLINE ACCEPT.** The novelty of combining multi-material tensegrity with Bayesian optimization for an assistive device is legitimate, and the lab-to-market framing is commendable. However, scope fit is marginal for this implant-centric symposium, and the most critical materials science question—PETG-TPU interface integrity under cyclic loading—is not addressed.

---

## (2) The Single Most-Likely Podium Question (In Voice)

*"You are pairing a rigid PETG strut with an elastomeric TPU element in an FFF multi-material print. In our work on multi-material structures, we have consistently found that thermal expansion mismatch and cooling-rate differences at dissimilar-material interfaces are the principal failure-initiation sites* (bandyopadhyay2018additivemanufacturingof pages 3-6). *The literature on rigid/soft FFF interfaces shows that TPU with rigid polymers achieves only partial mechanical interlocking, with incomplete adhesion and a roughly 21% reduction in modulus at the interface* (yilmaz2026investigationofmechanical pages 9-10). *Your crutch tip will see tens of thousands of cyclic impacts per week. Have you characterized the PETG-TPU interface bond strength under cyclic fatigue loading? And if not, what is your plan to ensure that delamination at the rigid-elastomeric boundary does not become the life-limiting failure mode for this device, well before the tensegrity architecture itself fails?"*

---

## (3) Top Improvement Wanted

**Explicitly address the PETG-TPU interface as a processing–structure–property challenge.** In my experience with multi-material AM—whether metallic or polymeric—the interface is where the device lives or dies (bandyopadhyay2018additivemanufacturingof pages 2-3, bandyopadhyay2018additivemanufacturingof pages 6-7). Recent multi-material FFF literature shows that interfacial adhesion is governed by diffusion-driven bonding, mechanical interlocking, and weak boundary layer effects, all of which are process-parameter-sensitive (nozzle temperature, print speed, layer height) (seregi2026investigationofpolymer pages 2-4). For the talk, I would want to see: (a) interlaminar shear strength (ILSS) data for PETG-TPU printed under your specific process window; (b) a cyclic compression fatigue curve showing whether interface delamination or strut buckling failure dominates; and (c) consideration of functionally graded transition zones between PETG and TPU regions to mitigate the abrupt stiffness discontinuity—something that multi-material AM is uniquely positioned to achieve (bandyopadhyay2018additivemanufacturingof pages 15-15). Pajunen et al. (2019) demonstrated that single-material tensegrity-inspired structures survived 24 impacts with only 2.28% residual strain (pajunen2019designandimpact pages 5-7), but that was a monolithic PA structure with no interface to worry about. Your multi-material design introduces a fundamentally different failure mode that must be validated.

---

## (4) Fact-Check / Overstatement Flags

**Flag 1 — "rubber-ferrule baseline that transmits over 95% of applied load."** This claim would bother me. I cannot find a published source quantifying rubber ferrule force transmission at ">95%." While it is physically plausible that a thin rubber cap provides minimal energy absorption, presenting this as a firm benchmark without citation risks an overstatement. *Recommendation:* reframe as "a conventional rubber ferrule, which by geometry and material provides negligible energy absorption" or cite a specific test result if you have one.

**Flag 2 — "Crutch abandonment exceeds 30%."** The literature on mobility assistive device (MAD) non-adherence shows rates ranging from 6% to 80% depending on device type and population (bashir2022patientcompliancewith pages 1-3, bashir2022patientcompliancewith pages 3-5). One study reports ~75% non-adherence for older adults across all MADs (jahan2022psychosocialpredictorsof pages 5-11). However, "crutch abandonment" specifically at >30% is not documented as a distinct statistic—the literature conflates crutches with walkers, wheelchairs, and orthoses. This is a moderate overstatement. *Recommendation:* say "mobility-device abandonment" rather than "crutch abandonment," or cite the specific source.

**Flag 3 — "tensegrity-inspired" nomenclature.** Pajunen et al. (2019) carefully distinguish pin-jointed prestressed tensegrity from fixed-jointed "tensegrity-inspired" structures, noting that FFF-printed versions are technically the latter because they lack true pin joints and independent prestress states (pajunen2019designandimpact pages 2-3, pajunen2019designandimpact pages 3-4). Your abstract uses "tensegrity-inspired lattices" in the body but "tensegrity" in the title. This is a minor inconsistency but worth tightening for accuracy.

**Claims that check out:** The ~0.5 BW crutch loading is well-supported by biomechanics literature (liu2011optimalcontroland pages 1-2). The 21 CFR 890.3790 classification is correct for cane/crutch/walker tips—Class I, 510(k)-exempt. The ISO 11334-1 reference is appropriate. The novelty claim of no prior tensegrity-based crutch-tip absorber appears supported by my patent and literature searches.

---

## (5) Scope-Fit Judgment

**Candidly: this is scope-adjacent, not scope-central.** Our symposium's named topics—implant infection mitigation, AM metallic implant fatigue, biodegradable alloys, bioceramics, bioprinting personalized implants, natural medicinal compounds—are overwhelmingly about implanted devices and body-contacting biomaterials (bandyopadhyay2018additivemanufacturingof pages 2-3). A polymer FFF external assistive device (skin-contact crutch tip) does not fit the core implant mandate.

**Where it has a foothold:** The symposium also calls out "intelligent manufacturing methods," "applications of AI/ML in manufacturing biomedical devices," and the overarching theme of bridging laboratory research to market (bandyopadhyay2018additivemanufacturingof pages 15-15). The Bayesian optimization loop, the Class I regulatory pathway discussion, and the distributed-manufacturing angle all align with the "laboratory to market" spine of the symposium.

**How to reposition:** To strengthen fit, I would recommend the authors: (a) explicitly frame this as a case study in AI-driven manufacturing of a patient-tunable biomedical device that illustrates the lab-to-market pipeline the symposium seeks to discuss; (b) draw parallels to multi-material AM implant design challenges (interface integrity, compositional gradients, processing–property relationships) that the audience will immediately connect with; and (c) if possible, briefly mention skin-contact biocompatibility considerations (cytotoxicity of PETG and TPU under ISO 10993-5) to invoke the "biocompatibility of materials" thread. This would position the talk as a translational methodology contribution rather than purely a crutch-tip engineering paper.

---

## (6) Concrete Drop-In Rewrite Suggestions (each ≤25 words)

**Rewrite 1 — Replace the unsubstantiated ferrule benchmark:**

*Current:* "…aiming to exceed a rubber-ferrule baseline that transmits over 95% of applied load."

*Suggested:* "…aiming to substantially exceed the negligible energy absorption of a conventional rubber ferrule under ISO 11334-1 loading conditions."

(Removes the unsourced ">95%" number; anchors to the testable standard.)

**Rewrite 2 — Fix the abandonment claim:**

*Current:* "Crutch abandonment exceeds 30%, motivating distributed, patient-tunable manufacturing."

*Suggested:* "Mobility-device non-adherence reaches 30–75%, motivating distributed, patient-tunable manufacturing via desktop FFF."

(Broadens to the documented literature range and adds the manufacturing method; cf. Bashir et al. 2022 (bashir2022patientcompliancewith pages 1-3).)

**Rewrite 3 — Add interface integrity framing for symposium fit:**

*Current:* "…pairing rigid PETG struts with elastomeric TPU elements to exploit buckling-induced load-limiting plateaus and TPU viscoelastic hysteresis."

*Suggested:* "…pairing rigid PETG struts with elastomeric TPU via process-optimized interfaces, exploiting buckling-induced plateaus and viscoelastic hysteresis."

(Signals awareness of the multi-material interface challenge; resonates with the symposium's AM processing theme; cf. Bandyopadhyay & Heer 2018 (bandyopadhyay2018additivemanufacturingof pages 3-6).)

---

## Closing Note

This is a creative piece of work that combines several individually mature ideas—tensegrity energy absorption (pajunen2019designandimpact pages 4-5, pajunen2019designandimpact pages 1-2, santos2023towardanovel pages 1-2), Bayesian optimization of AM lattices, and multi-material FFF—into a genuinely novel application. The regulatory awareness and distributed-manufacturing framing show translational thinking that this symposium values. My reservation is primarily about scope fit and the elephant in the room for any multi-material AM researcher: the interface. If the authors can present even preliminary PETG-TPU ILSS data and frame the work as a translational AI/ML manufacturing case study, I would move from borderline to accept.


References

1. (pajunen2019designandimpact pages 4-5): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

2. (pajunen2019designandimpact pages 1-2): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

3. (pajunen2019designandimpact pages 7-8): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

4. (yilmaz2026investigationofmechanical pages 9-10): Sinan Yilmaz, Okan Gul, and Onur Coban. Investigation of mechanical properties in layered multi‐material <scp>3d</scp> printing using commercial filaments: direct stacking of <scp>abs</scp> , <scp>pa</scp> , and compatibilizing layers. Journal of Vinyl and Additive Technology, 32:484-498, Dec 2026. URL: https://doi.org/10.1002/vnl.70051, doi:10.1002/vnl.70051. This article has 2 citations and is from a peer-reviewed journal.

5. (seregi2026investigationofpolymer pages 2-4): Bálint Leon Seregi, Peter Ficzere, and Gabriella Zsoldos. Investigation of polymer adhesion of materials in multimaterial fff process. Polymers, 18(7):805, Mar 2026. URL: https://doi.org/10.3390/polym18070805, doi:10.3390/polym18070805. This article has 0 citations.

6. (mottaghi2025opensource3dprintable pages 1-6): Maryam Mottaghi, Morgan C. Woods, Laura Danier, Anita So, Jacob M. Reeves, and Joshua M. Pearce. Open-source 3d printable forearm crutch. PLOS ONE, Nov 2025. URL: https://doi.org/10.1371/journal.pone.0318987, doi:10.1371/journal.pone.0318987. This article has 5 citations and is from a peer-reviewed journal.

7. (bandyopadhyay2018additivemanufacturingof pages 3-6): Amit Bandyopadhyay and Bryan Heer. Additive manufacturing of multi-material structures. Materials Science and Engineering: R: Reports, 129:1-16, Jul 2025. URL: https://doi.org/10.1016/j.mser.2018.04.001, doi:10.1016/j.mser.2018.04.001. This article has 711 citations.

8. (bandyopadhyay2018additivemanufacturingof pages 2-3): Amit Bandyopadhyay and Bryan Heer. Additive manufacturing of multi-material structures. Materials Science and Engineering: R: Reports, 129:1-16, Jul 2025. URL: https://doi.org/10.1016/j.mser.2018.04.001, doi:10.1016/j.mser.2018.04.001. This article has 711 citations.

9. (bandyopadhyay2018additivemanufacturingof pages 6-7): Amit Bandyopadhyay and Bryan Heer. Additive manufacturing of multi-material structures. Materials Science and Engineering: R: Reports, 129:1-16, Jul 2025. URL: https://doi.org/10.1016/j.mser.2018.04.001, doi:10.1016/j.mser.2018.04.001. This article has 711 citations.

10. (bandyopadhyay2018additivemanufacturingof pages 15-15): Amit Bandyopadhyay and Bryan Heer. Additive manufacturing of multi-material structures. Materials Science and Engineering: R: Reports, 129:1-16, Jul 2025. URL: https://doi.org/10.1016/j.mser.2018.04.001, doi:10.1016/j.mser.2018.04.001. This article has 711 citations.

11. (pajunen2019designandimpact pages 5-7): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

12. (bashir2022patientcompliancewith pages 1-3): Ayisha Z. Bashir, Danae M. Dinkel, Iraklis I. Pipinos, Jason M. Johanning, and Sara A. Myers. Patient compliance with wearing lower limb assistive devices: a scoping review. Journal of manipulative and physiological therapeutics, 45:114-126, Jun 2022. URL: https://doi.org/10.1016/j.jmpt.2022.04.003, doi:10.1016/j.jmpt.2022.04.003. This article has 42 citations and is from a peer-reviewed journal.

13. (bashir2022patientcompliancewith pages 3-5): Ayisha Z. Bashir, Danae M. Dinkel, Iraklis I. Pipinos, Jason M. Johanning, and Sara A. Myers. Patient compliance with wearing lower limb assistive devices: a scoping review. Journal of manipulative and physiological therapeutics, 45:114-126, Jun 2022. URL: https://doi.org/10.1016/j.jmpt.2022.04.003, doi:10.1016/j.jmpt.2022.04.003. This article has 42 citations and is from a peer-reviewed journal.

14. (jahan2022psychosocialpredictorsof pages 5-11): Alhadi Mohamed Jahan. Psychosocial predictors of non-adherence to prescribed mobility assistive devices by community-dwelling older adults: development of a predictive model. Text, Sep 2022. URL: https://doi.org/10.20381/ruor-28266, doi:10.20381/ruor-28266. This article has 1 citations and is from a peer-reviewed journal.

15. (pajunen2019designandimpact pages 2-3): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

16. (pajunen2019designandimpact pages 3-4): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

17. (liu2011optimalcontroland pages 1-2): Guangyu Liu, Yanxin Zhang, Sheng-Quan Xie, and Anke Xue. Optimal control and biomechanics of ambulation with spring-loaded crunches. International Journal of Advanced Robotic Systems, Aug 2011. URL: https://doi.org/10.5772/10664, doi:10.5772/10664. This article has 32 citations.

18. (santos2023towardanovel pages 1-2): Filipe A. Santos. Toward a novel energy‐dissipation metamaterial with tensegrity architecture. Advanced Materials, May 2023. URL: https://doi.org/10.1002/adma.202300639, doi:10.1002/adma.202300639. This article has 29 citations and is from a highest quality peer-reviewed journal.