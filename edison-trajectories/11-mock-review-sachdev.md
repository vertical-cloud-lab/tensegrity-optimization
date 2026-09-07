# Edison trajectory 11 — Mock reviewer: Anil Sachdev

- **Task ID:** `8c0ea7de-507d-49de-bd6c-98c086238d40`
- **Job type:** `LITERATURE` (low-effort, round-2 organizer-persona mock review)
- **Status:** `success`
- **Edison link:** https://platform.edisonscientific.com/tasks/8c0ea7de-507d-49de-bd6c-98c086238d40

Second-round mock program-committee review of [`crutch-tip-abstract.md`](../crutch-tip-abstract.md),
in the voice of TMS 2027 *Biomedical Materials and Devices: From Laboratory to Market* organizer
**Anil Sachdev**. Verbatim `formatted_answer` below; full structured response in the sibling `.json`.

---

Question: You are Dr. Anil Sachdev (University of North Texas; long career at General Motors R&D), an expert in structural materials, mechanical behavior, deformation/fatigue, and manufacturing scale-up for real products. You care about fatigue life over realistic duty cycles (10^5-10^6 gait cycles), anisotropy of AM parts, reproducibility, quality control, and whether a lab demonstrator can be manufactured at scale and survive service loads.

Act as THIS SPECIFIC named reviewer on the TMS 2027 symposium program committee and give a candid, in-voice mock review of the abstract below. Provide: (1) a scorecard (novelty, technical merit, fit-to-symposium-scope, clarity, lab-to-market strength, evidence sufficiency, each /5) with a one-line accept/borderline/reject leaning; (2) the single most-likely question you would ask at the podium, in your voice and area of expertise; (3) the top improvement you would want, grounded in your expertise; (4) a short fact-check / overstatement flag on any claim that would bother you; (5) a scope-fit judgment (does this belong in this symposium, and how to reposition it to fit your priorities); (6) 2-3 concrete drop-in rewrite suggestions (each <=25 words) that keep the abstract within the 150-word TMS limit. Cite literature where useful.

TARGET SYMPOSIUM: TMS 2027 "Biomedical Materials and Devices: From Laboratory to Market". Scope (verbatim): Innovation in biomaterials and medical devices has saved millions of lives, but a big disconnect exists between academic laboratory research and bringing devices to market; the symposium focuses on knowledge transfer among academia, industry, regulatory bodies, and end users (physicians, funding agencies). Topics include intelligent manufacturing methods, applications of AI/ML in manufacturing biomedical devices, and innovative characterization tools that better correlate in-vitro to in-vivo performance. Named challenges skew toward implants: mitigating implant infection, minimizing anisotropy of additively manufactured materials, improving fatigue resistance of AM metallic implants, biodegradable metallic implant alloys, biocompatibility of alloys, natural medicinal compounds, bioprinting personalized implants, high-strength biodegradable ceramics, and smart charge-generating implants. It also runs multidisciplinary panel discussions. NOTE: this abstract is a polymer fused-filament-fabrication ASSISTIVE-DEVICE (external, skin-contact crutch tip), which is scope-ADJACENT to that implant-heavy list; assess fit candidly.

IMPORTANT CONSTRAINT: We do NOT yet have measured experimental data (SEA in J/g, %-force-reduction); the abstract is due tonight. The abstract deliberately states the benchmark it aims to EXCEED (a rubber ferrule that transmits >95% of applied load) rather than claiming any measured result. Please review it as an intent/design-study abstract on that basis; do NOT penalize it for lacking a specific measured number, but DO advise how to frame the not-yet-measured performance most defensibly.

TITLE: Closed-Loop Bayesian Optimization of Multi-Material 3D-Printed Tensegrity Crutch-Tip Impact Absorbers

ABSTRACT (150 words): Long-term crutch users load each crutch to ~0.5 body weights during partial-weight-bearing gait and experience substantial upper-extremity overuse injury, including crutch palsy, shoulder impingement, and carpal tunnel syndrome; commercial crutch tips predominantly use rubber ferrules, while existing spring-loaded dampers add bulk without architected tunability. We apply closed-loop, multi-objective Bayesian optimization to design a crutch-tip insert from multi-material fused-filament-fabrication tensegrity-inspired lattices, pairing rigid PETG struts with elastomeric TPU elements to exploit buckling-induced load-limiting plateaus and TPU viscoelastic hysteresis. Within the standard 19-25 mm crutch-shaft interface, we co-optimize unit-cell topology, strut diameter, relative density, and prestress to maximize specific energy absorption and minimize peak transmitted force across quasi-static compression and drop-weight impact, aiming to exceed a rubber-ferrule baseline that transmits over 95% of applied load. Prior-art review identified no tensegrity-based crutch-tip absorber; an anticipated Class I (21 CFR 890.3790), ISO 11334-1 pathway guides verification. Crutch abandonment exceeds 30%, motivating distributed, patient-tunable manufacturing.

# Mock Review — Dr. Anil K. Sachdev (University of North Texas; formerly General Motors R&D)

## TMS 2027 Symposium: "Biomedical Materials and Devices: From Laboratory to Market"

**Abstract under review:** *"Closed-Loop Bayesian Optimization of Multi-Material 3D-Printed Tensegrity Crutch-Tip Impact Absorbers"*

---

## (1) Scorecard

| Category | Score (/5) | One-line rationale |
|---|---:|---|
| Novelty | 4.0 | Tensegrity-based crutch-tip absorption appears genuinely novel, and Bayesian optimization of multi-material lattices is a timely design approach; prior-art gap claim looks credible (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 1-2). |
| Technical Merit | 3.0 | The buckling/load-limiting concept is well grounded in prior tensegrity literature, but the abstract does not yet address fatigue life, FFF anisotropy, or PETG/TPU interface durability under cycling (pajunen2019designandimpact pages 5-7, bakhtiari2023effectof3d pages 12-13, bakhtiari2023effectof3d pages 7-10, daglı2025mechanicalcharacterizationand pages 11-14). |
| Fit-to-Symposium-Scope | 2.5 | This is a biomedical device, but it is an external polymer assistive device rather than the implant-heavy metallic/biomaterials core emphasized by the symposium. |
| Clarity | 4.0 | The 150-word abstract is compact, logically organized, and technically specific; the problem, design variables, and intended verification pathway are easy to follow. |
| Lab-to-Market Strength | 3.0 | Regulatory awareness and manufacturability intent are positives, but I do not yet see a convincing plan for reproducibility, QC, lot-to-lot consistency, or long-cycle service durability. |
| Evidence Sufficiency | 2.5 | For a design-study abstract, it is acceptable to state targets rather than results, but some defensible durability target or analogous benchmark would strengthen credibility (bakhtiari2023effectof3d pages 12-13, bakhtiari2023effectof3d pages 4-7). |
| Overall leaning | BORDERLINE | Borderline accept, preferably as a poster, if revised to foreground fatigue/durability, anisotropy control, and why this belongs in a lab-to-market biomedical manufacturing session. |


*Table: This table summarizes the mock review scorecard in Dr. Anil Sachdev’s voice, with category-by-category scores and concise rationales. It is useful as a compact committee-style assessment anchored to the fatigue, anisotropy, and manufacturability issues most likely to matter for this symposium.*

**Overall Leaning: BORDERLINE — Accept as poster with revisions.** The concept is novel and the mechanics are grounded, but the abstract as written will not survive scrutiny from this committee without addressing cyclic durability and repositioning toward the symposium's AM-process themes.

---

## (2) Single Most Likely Podium Question (in Dr. Sachdev's voice)

> You have shown me a sensible quasi-static and impact design strategy, but I come from the fatigue-and-manufacturing side of this business: a real crutch tip does not see 20 impacts in the lab, it sees on the order of 10^5-10^6 gait cycles in service. In FFF polymers, fatigue life is strongly raster- and build-orientation-dependent, and cracks commonly initiate at interlayer defects and interfaces; that is exactly where I would worry in slender PETG members designed to buckle repeatedly. So my question is very simple: what is your target service life in gait cycles, and how will you demonstrate that repeated PETG buckling plus TPU viscoelastic set does not drift the load plateau, peak transmitted force, and dimensional fit over time? (bakhtiari2023effectof3d pages 12-13, bakhtiari2023effectof3d pages 7-10, gonabadi2020theeffectof pages 12-13, cuanurquizo2019characterizationofthe pages 3-6, daglı2025mechanicalcharacterizationand pages 11-14)


*Blockquote: This blockquote gives the single most likely podium question in Dr. Anil Sachdev's voice. It emphasizes long-cycle fatigue, interlayer failure, and viscoelastic drift—the key manufacturing and service-life risks for an FFF multi-material crutch tip.*

This is the question I would ask because it goes to the heart of whether a lab demonstrator can survive real service. Pajunen et al. demonstrated that SLS-printed tensegrity structures survive 24 impacts with only 2.28% remaining strain (pajunen2019designandimpact pages 7-8), but 24 impacts is not 350,000 gait cycles per year. Bakhtiari et al. show that FFF polymer fatigue life is strongly raster-orientation-dependent, with endurance limits as low as 0.5 MPa at unfavorable orientations, and failure initiating at interlayer bonds and internal voids (bakhtiari2023effectof3d pages 12-13, bakhtiari2023effectof3d pages 7-10). The abstract optimizes for quasi-static and single-impact performance but says nothing about how the optimized design degrades over a realistic duty cycle. In FFF parts, the Z-direction interlayer bond is the weakest link — upright-orientation PLA shows ~91% reduction in tensile strength versus on-edge orientation (gonabadi2020theeffectof pages 1-2) — and this weakness is structural, not intrinsic to the polymer (lesniowski2025enhancingtheperformance pages 4-6). For slender PETG struts designed to buckle repeatedly, fatigue crack initiation at layer interfaces is the governing failure mode.

---

## (3) Top Improvement Wanted

**Add a fatigue/durability framing sentence to the abstract.** Even without measured data yet, the abstract should state a target service life in gait cycles (e.g., ≥10⁵ cycles, corresponding to ~3–4 months of daily use) and acknowledge that cyclic validation of the PETG/TPU multi-material interface will be part of the verification plan. This is not asking for data that does not yet exist — it is asking the authors to show they understand the failure mode that will govern whether this device can move from lab to market. The fatigue literature on FFF polymers is clear that internal voids and interlayer bonds are the sites where cyclic failure initiates (bakhtiari2023effectof3d pages 4-7, bakhtiari2023effectof3d pages 7-10), and that thermal fatigue from hysteretic heating is a second concern in polymers with low thermal conductivity (bakhtiari2023effectof3d pages 4-7). One sentence acknowledging a cyclic-durability objective would dramatically strengthen the lab-to-market credibility of this abstract for this particular symposium.

---

## (4) Fact-Check / Overstatement Flags

**Flag 1 — "Crutch abandonment exceeds 30%."** The literature is inconsistent on this number. Brown et al. (2020) report assistive device abandonment as high as 75% for some device categories (brown2020commonproblemswith pages 1-7), while Bashir et al. (2022) found fewer than 23% of lower-limb assistive devices in possession were abandoned (bashir2022patientcompliancewith pages 14-15). The 30% figure is within the plausible range but is not a consensus number for crutches specifically. I would recommend softening to "assistive-device abandonment rates range from ~20% to over 50% depending on device type" or citing a specific source.

**Flag 2 — "21 CFR 890.3790."** This CFR code covers "Cane," not crutches. Crutches are classified under different product codes (e.g., 21 CFR 890.3420 for forearm crutches). The Class I exempt designation is almost certainly correct for an external assistive device accessory, but the specific regulatory citation should be verified before the presentation. A wrong CFR code in a lab-to-market symposium would undermine credibility.

**Flag 3 — "rubber-ferrule baseline that transmits over 95% of applied load."** This is a physically reasonable claim for a thin rubber cap with limited compliance, but I could not find a published measurement confirming this exact number. If this is the authors' own preliminary measurement, they should say so; if it is estimated, they should frame it as such. Stating it as fact without a citation is a minor overstatement.

**Flag 4 — Buckling-plateau mechanics via FFF.** The tensegrity load-limiting plateau concept is well-established in the literature, but the key demonstrations (Pajunen et al. 2019) used SLS with PA2200 polyamide, not multi-material FFF with PETG/TPU (pajunen2019designandimpact pages 2-3). The transfer from SLS (isotropic, no interlayer weakness) to FFF (anisotropic, interlayer bond-limited) is non-trivial and introduces additional concerns about whether the clean elastic buckling behavior will reproduce in FFF parts with layer-interface defects (gonabadi2020theeffectof pages 12-13, lesniowski2025enhancingtheperformance pages 4-6). The abstract does not acknowledge this process-transfer risk.

---

## (5) Scope-Fit Judgment

**Candid assessment: Scope-adjacent, not core.** This is an external polymer assistive device (skin-contact crutch tip), while the symposium's named challenges skew heavily toward metallic implants, biodegradable alloys, biocompatibility, and infection mitigation. The abstract is *not* about an implant, does not involve metals, and does not address biocompatibility or in-vivo/in-vitro correlation.

**However, it touches real symposium themes:** The symposium explicitly calls for "intelligent manufacturing methods," "applications of AI/ML in manufacturing biomedical devices," and "minimizing anisotropy of additively manufactured materials." Bayesian optimization of an AM biomedical device is squarely within those threads. The lab-to-market framing (regulatory pathway, distributed manufacturing, ISO verification) also aligns with the symposium's stated mission of bridging the academic-to-market disconnect.

**How to reposition:** The abstract should foreground the AM-process challenges (FFF anisotropy management, multi-material interface quality, Bayesian optimization as intelligent manufacturing) rather than leading with crutch biomechanics. Frame it as: "We demonstrate closed-loop Bayesian optimization as an intelligent manufacturing method for a Class I biomedical device, addressing AM anisotropy and fatigue challenges transferable to higher-risk implant applications." This puts the method and the manufacturing science first, with the crutch tip as the testbed — which is a more defensible positioning for a poster in this symposium.

---

## (6) Concrete Drop-In Rewrite Suggestions (each ≤25 words)

**Rewrite 1 — Replace the crutch-abandonment sentence:**
*Current:* "Crutch abandonment exceeds 30%, motivating distributed, patient-tunable manufacturing."
*Suggested:* "Assistive-device abandonment rates of 20–50% motivate distributed, patient-tunable FFF manufacturing with built-in cyclic-durability verification."
(24 words; adds durability nod, fixes the unsourced 30% claim.)

**Rewrite 2 — Add fatigue framing to the optimization objectives:**
*Current:* "…maximize specific energy absorption and minimize peak transmitted force across quasi-static compression and drop-weight impact…"
*Suggested:* "…maximize specific energy absorption and minimize peak transmitted force under quasi-static, impact, and cyclic gait loading (target ≥10⁵ cycles)…"
(21 words replacing the same clause; signals fatigue awareness without claiming data.)

**Rewrite 3 — Strengthen the scope-fit sentence toward AM process science:**
*Current:* "Prior-art review identified no tensegrity-based crutch-tip absorber; an anticipated Class I (21 CFR 890.3790), ISO 11334-1 pathway guides verification."
*Suggested:* "No prior tensegrity-based crutch-tip absorber exists; an anticipated Class I, ISO 11334-1 pathway guides verification including FFF anisotropy and interface durability."
(22 words; drops the potentially incorrect CFR code, adds AM-relevant scope language.)

---

## Summary

This is a creative and technically grounded design-study abstract. The tensegrity load-plateau concept is well-supported by Pajunen et al. (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 4-5, pajunen2019designandimpact pages 1-2), and the application of Bayesian optimization to multi-material lattice design is timely. The clinical motivation is real. However, from a manufacturing-and-service perspective, the abstract has three vulnerabilities: (a) no mention of fatigue life or cyclic durability, which is the failure mode that will determine whether this device survives real use (bakhtiari2023effectof3d pages 12-13, bakhtiari2023effectof3d pages 7-10); (b) FFF anisotropy and multi-material interface adhesion under cycling are unaddressed risks that the literature clearly identifies (gonabadi2020theeffectof pages 12-13, lesniowski2025enhancingtheperformance pages 4-6, daglı2025mechanicalcharacterizationand pages 11-14); and (c) scope fit to this implant-heavy symposium requires deliberate repositioning toward the AM-process and intelligent-manufacturing themes. With the three rewrite suggestions above — totaling fewer than 20 net additional words — the abstract would be substantially stronger and more defensible at this venue.

References

1. (pajunen2019designandimpact pages 5-7): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

2. (pajunen2019designandimpact pages 1-2): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

3. (bakhtiari2023effectof3d pages 12-13): Hamed Bakhtiari, Muhammad Aamir, and Majid Tolouei-Rad. Effect of 3d printing parameters on the fatigue properties of parts manufactured by fused filament fabrication: a review. Applied Sciences, 13:904, Jan 2023. URL: https://doi.org/10.3390/app13020904, doi:10.3390/app13020904. This article has 142 citations.

4. (bakhtiari2023effectof3d pages 7-10): Hamed Bakhtiari, Muhammad Aamir, and Majid Tolouei-Rad. Effect of 3d printing parameters on the fatigue properties of parts manufactured by fused filament fabrication: a review. Applied Sciences, 13:904, Jan 2023. URL: https://doi.org/10.3390/app13020904, doi:10.3390/app13020904. This article has 142 citations.

5. (daglı2025mechanicalcharacterizationand pages 11-14): Salih Dağlı. Mechanical characterization and interface evaluation of multi-material composites manufactured by hybrid fused deposition modeling (hfdm). Polymers, 17:1631, Jun 2025. URL: https://doi.org/10.3390/polym17121631, doi:10.3390/polym17121631. This article has 12 citations.

6. (bakhtiari2023effectof3d pages 4-7): Hamed Bakhtiari, Muhammad Aamir, and Majid Tolouei-Rad. Effect of 3d printing parameters on the fatigue properties of parts manufactured by fused filament fabrication: a review. Applied Sciences, 13:904, Jan 2023. URL: https://doi.org/10.3390/app13020904, doi:10.3390/app13020904. This article has 142 citations.

7. (gonabadi2020theeffectof pages 12-13): H. Gonabadi, A. Yadav, and S. J. Bull. The effect of processing parameters on the mechanical characteristics of pla produced by a 3d fff printer. The International Journal of Advanced Manufacturing Technology, 111:695-709, Oct 2020. URL: https://doi.org/10.1007/s00170-020-06138-4, doi:10.1007/s00170-020-06138-4. This article has 318 citations.

8. (cuanurquizo2019characterizationofthe pages 3-6): Enrique Cuan-Urquizo, Eduardo Barocio, Viridiana Tejada-Ortigoza, R. Byron Pipes, Ciro A. Rodriguez, and Armando Roman-Flores. Characterization of the mechanical properties of fff structures and materials: a review on the experimental, computational and theoretical approaches. Mar 2019. URL: https://doi.org/10.3390/ma12060895, doi:10.3390/ma12060895. This article has 416 citations.

9. (pajunen2019designandimpact pages 7-8): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

10. (gonabadi2020theeffectof pages 1-2): H. Gonabadi, A. Yadav, and S. J. Bull. The effect of processing parameters on the mechanical characteristics of pla produced by a 3d fff printer. The International Journal of Advanced Manufacturing Technology, 111:695-709, Oct 2020. URL: https://doi.org/10.1007/s00170-020-06138-4, doi:10.1007/s00170-020-06138-4. This article has 318 citations.

11. (lesniowski2025enhancingtheperformance pages 4-6): Jakub Leśniowski, Adam Stawiarski, and Marek Barski. Enhancing the performance of fff-printed parts: a review of reinforcement and modification strategies for thermoplastic polymers. Materials, 18(22):5185, Nov 2025. URL: https://doi.org/10.3390/ma18225185, doi:10.3390/ma18225185. This article has 7 citations.

12. (brown2020commonproblemswith pages 1-7): Suzana Brown, Achilles Vairis, Ali M. Masoumifar, and Markos Petousis. Common problems with the conventional design of crutches: proposing a safer design and discussing the potential impact. Technology in Society, 60:101215, Feb 2020. URL: https://doi.org/10.1016/j.techsoc.2019.101215, doi:10.1016/j.techsoc.2019.101215. This article has 17 citations and is from a peer-reviewed journal.

13. (bashir2022patientcompliancewith pages 14-15): Ayisha Z. Bashir, Danae M. Dinkel, Iraklis I. Pipinos, Jason M. Johanning, and Sara A. Myers. Patient compliance with wearing lower limb assistive devices: a scoping review. Journal of manipulative and physiological therapeutics, 45:114-126, Jun 2022. URL: https://doi.org/10.1016/j.jmpt.2022.04.003, doi:10.1016/j.jmpt.2022.04.003. This article has 42 citations and is from a peer-reviewed journal.

14. (pajunen2019designandimpact pages 2-3): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

15. (pajunen2019designandimpact pages 4-5): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.