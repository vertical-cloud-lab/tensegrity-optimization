# Edison trajectory: 06-abstract-feedback

- **Task ID:** `74ac013b-8ce9-41ab-89ce-13c3e6f5ad33`
- **Job:** `job-futurehouse-paperqa3-high`
- **Status:** `success`
- **Successful answer:** `True`
- **Created at:** `2026-07-01T20:07:35.360446Z`
- **Edison platform link:** https://platform.edisonscientific.com/tasks/74ac013b-8ce9-41ab-89ce-13c3e6f5ad33
- **Summary:** Critical peer-review of this PR's TMS 2027 crutch-tip abstract (`crutch-tip-abstract.md`) for the *Biomedical Materials and Devices: From Laboratory to Market* symposium. Edison fact-checks every quantitative/factual claim, flags overstatements, stress-tests the novelty and FDA Class I / ISO 11334-1 regulatory claims, ranks the top missing context a reviewer would expect, evaluates the title's "vibration attenuation" promise vs. the impact-focused body, and proposes concrete citation-backed edits within the 150-word limit.

> The block below is the verbatim `formatted_answer` returned by the Edison client, which includes the original Question, the cited Answer, and the full numbered References list. The raw JSON dump of the response is in the sibling `*.json` file.

---

Question: Act as a critical peer reviewer for a materials-science / biomedical-device conference (TMS 2027, Biomedical Materials and Devices: From Laboratory to Market symposium). Below is a 150-word abstract. Provide a rigorous, literature-grounded review.

Abstract title: "Bayesian-Optimized Multi-Material 3D-Printed Tensegrity Crutch Tips for Impact and Vibration Attenuation."

Abstract text: "Long-term crutch users bear repeated ground-reaction forces of roughly 0.5 body weights per crutch and experience high rates of upper-extremity overuse injury, including crutch palsy, shoulder impingement, and carpal tunnel syndrome, yet commercial crutch tips still rely on simple rubber ferrules or bulky springs. We present a shock-absorbing crutch-tip insert built from multi-material fused-filament-fabrication tensegrity-inspired lattices that pair rigid PETG struts with elastomeric TPU tension elements, exploiting load-limiting buckling and rate-dependent damping. Because the standard 19 to 25 mm ferrule envelope severely limits stroke, we co-optimize unit-cell topology, strut diameter, relative density, and prestress using closed-loop multi-objective Bayesian optimization, maximizing specific energy absorption while minimizing peak transmitted force across quasi-static compression and drop-weight impact tests. A prior-art survey confirms that no existing crutch tip applies tensegrity architectures, and an FDA Class I, ISO 11334-1 regulatory pathway is clear. This demonstrator advances miniaturized, patient-tunable energy absorbers for assistive and protective devices."

Please address each of the following:

1. Claim fact-checking. For each quantitative or factual claim, state whether the literature supports it, and give citations: (a) peak ground-reaction force approximately 0.5 body weights per crutch; (b) high rates / clinical significance of upper-extremity overuse injuries in long-term crutch users (crutch palsy, shoulder impingement, carpal tunnel syndrome); (c) that commercial crutch tips are still limited to rubber ferrules or bulky springs; (d) that buckling tensegrity lattices provide a load-limiting plateau and rate-dependent damping; (e) that the standard ferrule envelope is 19-25 mm and that this severely limits absorber stroke; (f) that no existing crutch tip applies tensegrity architectures (novelty); (g) that the U.S. regulatory pathway is FDA Class I and that ISO 11334-1 is the governing standard.
2. Overstatements. Identify any claim that is stronger than the evidence supports, or any word ("clear," "confirms," "severely," "high rates") that a reviewer could challenge, and suggest more defensible phrasing.
3. Missing context. What would a materials/biomedical reviewer most expect to see that is absent - e.g. whether results are simulated vs. experimental, sample size, baseline/control, specific energy-absorption or force-reduction numbers, fatigue life over gait cycles, the PETG-TPU interface durability risk, or slip-resistance validation? Rank the top 3-5 gaps by how much they would affect acceptance.
4. Vibration claim. The title promises "vibration attenuation," but the body emphasizes impact. Does the literature support a distinct, measurable vibration/HAVS benefit through crutch tips, or should the vibration framing be softened? Cite.
5. Novelty & framing for a "Laboratory to Market" symposium. Is the lab-to-market / commercialization framing adequately supported for this venue, and what single sentence would most strengthen the translational angle?
6. Concrete rewrite suggestions. Propose 3-5 specific, citation-backed edits (word- or sentence-level) that would make the abstract more accurate and more compelling within a 150-word limit.

Ground every assessment in the peer-reviewed / patent literature and provide a numbered reference list.

# Peer Review: "Bayesian-Optimized Multi-Material 3D-Printed Tensegrity Crutch Tips for Impact and Vibration Attenuation"

**Venue:** TMS 2027 — Biomedical Materials and Devices: From Laboratory to Market

---

## 1. Claim Fact-Checking

The following table summarizes the literature assessment of each factual or quantitative claim in the abstract.

| Claim | Verdict | Key Evidence | Suggested Revision |
|---|---|---|---|
| (a) Peak ground-reaction force is ~0.5 body weights per crutch | Partially Supported | 0.5 BW is supported as an instructed partial-weight-bearing target in instrumented forearm-crutch testing, but the broader crutch-gait literature shows much higher dynamic upper-limb/crutch loads during swing-through gait, including 1.14-3.36 BW at the hands; thus the number is gait- and task-dependent rather than generally representative of long-term crutch use (chamorromoriana2016acompactforearm pages 5-8, chamorromoriana2016acompactforearm pages 8-10, CA2287886A1 pages 9-11, orishimo2021comparisonofhip pages 2-3) | “During prescribed partial-weight-bearing gait, users may load a crutch to roughly 0.5 BW, although peak dynamic loads vary substantially with gait pattern.” |
| (b) Long-term crutch users experience clinically significant upper-extremity overuse injuries | Supported | Polio survivors showed 80% electrophysiologic upper-extremity entrapment neuropathies, with cane/crutch use an independent risk factor (OR 6.2-13.7); crutch-related shoulder pain, impingement/nerve compression, carpal tunnel syndrome, and focal nerve palsies are documented in the literature and case reports (tsai2009prevalenceandrisk pages 3-5, tsai2009prevalenceandrisk pages 1-2, CA2287886A1 pages 9-11) | “Long-term mobility-aid users have substantial upper-extremity overuse and compression-neuropathy burden, including shoulder pain/impingement and median or ulnar neuropathies.” |
| (c) Commercial crutch tips are still limited to rubber ferrules or bulky springs | Partially Supported | The mass market is indeed dominated by rubber ferrules and spring-based shock-absorbing concepts, but prior art also includes bellows, gas-spring, viscoelastic, and hybrid ferrule designs, so the statement is too reductive if read literally (US11712394B1 pages 1-4) | “Commercial crutch tips still predominantly rely on rubber ferrules or relatively bulky spring/bellows-based shock-absorbing concepts.” |
| (d) Buckling tensegrity lattices provide a load-limiting plateau and rate-dependent damping | Partially Supported | Tensegrity-inspired lattices clearly show post-buckling, load-limiting plateau behavior and strong energy absorption; however, the cited tensegrity literature attributes dissipation mainly to material hysteresis/viscoelasticity, not to an inherent tensegrity-specific rate-dependent damping mechanism (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 1-2, pajunen2019designandimpact pages 7-8, pajunen2021prestraininducedbandgaptuning pages 1-2, khatri2024energyabsorptionof pages 10-11) | “...exploiting a buckling-induced load-limiting plateau, with damping arising primarily from TPU viscoelastic hysteresis.” |
| (e) The standard ferrule envelope is 19-25 mm and this severely limits absorber stroke | Unverified | 19-25 mm is plausible for crutch shaft outer diameter / ferrule bore sizing, but available sources do not verify it as the full ferrule envelope; cited ferrule outer diameters in prior art are larger (32-47 mm), and no peer-reviewed source was found substantiating that this dimension “severely” limits stroke (CA2287886A1 pages 11-14) | “Because common crutch shafts use ~19-25 mm tip interfaces, the available insert volume is limited; this constrains achievable stroke within standard ferrules.” |
| (f) No existing crutch tip applies tensegrity architectures | Partially Supported | No directly matching tensegrity crutch-tip patent/art was identified, although tensegrity concepts have appeared in adjacent assistive-device domains such as prosthetic/orthotic joints and feet; novelty is plausible, but “confirms” implies an exhaustive search beyond what an abstract should claim (US11712394B1 pages 1-4) | “A prior-art search suggests that tensegrity architectures have not yet been reported for crutch-tip energy absorbers.” |
| (g) The U.S. regulatory pathway is FDA Class I and ISO 11334-1 is the governing standard | Supported | Crutch/cane/walker tips and pads are identified under FDA Class I regulation (21 CFR 890.3790), and ISO 11334-1 is used as the relevant walking-aid standard in recent crutch-development literature; however, calling the pathway “clear” overstates certainty for a novel insertable absorber design (mottaghi2025opensource3dprintable pages 21-24) | “An anticipated U.S. pathway is FDA Class I under 21 CFR 890.3790, with ISO 11334-1 as a key performance standard.” |


*Table: This table evaluates the seven central factual and quantitative claims in the abstract against the retrieved literature and patent record. It highlights which claims are well supported, which need narrowing, and how each could be revised to be more defensible in conference-review context.*

### Detailed Discussion

**(a) ~0.5 BW per crutch.** This figure is consistent with instructed partial-weight-bearing loads tested at 50% BW per crutch in instrumented crutch studies (chamorromoriana2016acompactforearm pages 5-8, chamorromoriana2016acompactforearm pages 8-10). However, the biomechanics literature shows substantially higher peak dynamic loads during swing-through gait: hand forces of 1.14–3.36 times body weight have been reported (CA2287886A1 pages 9-11), and vertical ground-reaction forces during axillary crutch ambulation are approximately 25% greater than during normal gait (orishimo2021comparisonofhip pages 2-3, orishimo2021comparisonofhip pages 3-5). The 0.5 BW figure is therefore a context-dependent lower bound—appropriate for prescribed partial weight-bearing but not representative of all crutch-gait patterns. The abstract should specify the gait scenario.

**(b) Upper-extremity overuse injuries.** This claim is well supported. Tsai et al. (2009) found 80% electrophysiological prevalence of upper-extremity entrapment neuropathies in 97 polio survivors, with crutch/cane use as an independent risk factor (OR 6.2–13.7 for median and ulnar neuropathies) (tsai2009prevalenceandrisk pages 3-5, tsai2009prevalenceandrisk pages 1-2). Shoulder pain prevalence of 30% in paraplegics (with 70% of that subgroup showing nerve impingement), carpal tunnel syndrome from repetitive wrist trauma, and crutch palsy from brachial plexus compression are all documented (CA2287886A1 pages 9-11). However, the phrase "high rates" is imprecise; prevalence varies substantially by population.

**(c) Commercial tips limited to rubber ferrules or springs.** This characterization is broadly accurate for the mass market but oversimplified. The patent record reveals additional approaches including compression-spring ferrules (US11712394B1), bellows and gas-spring designs (AU2008294554B2), spiral-spring ferrules (JP2007105364A), and viscoelastic materials (US11712394B1 pages 1-4). The phrase "predominantly rely on" would be more defensible.

**(d) Load-limiting plateau and rate-dependent damping.** The load-limiting plateau from buckling in tensegrity-inspired lattices is strongly supported: Pajunen et al. (2019) experimentally demonstrated post-buckling stress plateaus, high strain energy capacity, and reusability under repeated impacts (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 1-2, pajunen2019designandimpact pages 7-8). However, "rate-dependent damping" is an overstatement of the tensegrity-specific literature. Pajunen et al. (2019) attribute energy dissipation primarily to material hysteresis in the base polymer rather than to an inherent rate-dependent structural mechanism (pajunen2019designandimpact pages 7-8). In stiff polymers, damping is explicitly noted as minimal (pajunen2021prestraininducedbandgaptuning pages 1-2). The rate-dependency in the proposed design would arise from the TPU elastomeric elements—a material property, not a tensegrity-specific mechanism. The abstract should attribute damping to TPU viscoelasticity rather than to the tensegrity architecture itself.

**(e) 19–25 mm ferrule envelope.** The 19–25 mm range is plausible as the crutch shaft outer diameter (and therefore ferrule bore), consistent with common aluminum crutch tubing sizes. However, ferrule outer diameters documented in patent literature are significantly larger (32–47 mm) (CA2287886A1 pages 11-14). The abstract conflates shaft bore with overall ferrule envelope. Furthermore, no peer-reviewed source was found substantiating that this dimension "severely limits absorber stroke."

**(f) Novelty.** Our patent search identified no tensegrity-based crutch-tip design, supporting the novelty claim. Tensegrity concepts have appeared in adjacent assistive-device domains (e.g., prosthetic feet, US20110093091A1), but not in crutch tips specifically. The word "confirms" is, however, too strong—no abstract-level survey can be exhaustive.

**(g) FDA Class I and ISO 11334-1.** Crutch tips fall under 21 CFR 890.3790 (Class I, generally 510(k)-exempt), as confirmed by Mottaghi et al. (2025) (mottaghi2025opensource3dprintable pages 21-24). ISO 11334-1 is the applicable walking-aid standard used in recent crutch development work. Both identifications are correct, but the claim that the pathway is "clear" overstates regulatory certainty for a novel multi-material insertable device that may raise questions about intended-use classification.

---

## 2. Overstatements

Several words or phrases in the abstract are stronger than the available evidence supports:

- **"clear" (regulatory pathway):** FDA Class I is the expected pathway, but novel multi-material energy absorbers could face additional scrutiny. Replace with "anticipated" or "expected."
- **"confirms" (prior-art survey):** An abstract cannot claim exhaustive prior-art coverage. Replace with "suggests" or "indicates."
- **"severely limits" (ferrule stroke):** No quantitative source verifies severity. Replace with "constrains" or "limits."
- **"high rates" (of UE injury):** Prevalence varies widely by population and condition (tsai2009prevalenceandrisk pages 3-5, CA2287886A1 pages 9-11). Replace with "substantial" or cite a specific prevalence figure.
- **"rate-dependent damping":** The tensegrity literature attributes dissipation to material hysteresis, not rate-dependent structural damping (pajunen2019designandimpact pages 7-8). Reframe as "viscoelastic damping provided by the TPU elements."

---

## 3. Missing Context

The following table ranks the most critical gaps that would affect acceptance at a materials/biomedical-device symposium.

| Rank | Missing Element | Why It Matters | Impact on Acceptance |
|---|---|---|---|
| 1 | No quantitative performance results reported | The abstract gives no specific energy absorption, peak-force reduction, transmitted impulse, or mass-normalized metrics. Without even preliminary numbers, it reads more like a design concept than a results-driven materials paper; TMS reviewers will expect measurable performance outcomes from the claimed optimization and testing workflow (mo2023accelerateddesignof pages 1-1, mo2023accelerateddesignof pages 4-5, mo2023accelerateddesignof pages 2-4) | High |
| 2 | Experimental vs. simulated results unclear | The text mentions “quasi-static compression and drop-weight impact tests” but never makes explicit whether reported findings are already experimentally demonstrated, are simulation-guided only, or are still planned. That ambiguity directly affects how mature and credible the contribution appears (mo2023accelerateddesignof pages 1-1, mo2023accelerateddesignof pages 6-7, mo2023accelerateddesignof pages 2-4) | High |
| 3 | PETG-TPU interface durability / fatigue life | Multi-material FFF interfaces are often failure-limiting, and literature shows interfacial adhesion strongly governs structural integrity. For a crutch tip, repeated cyclic loading could drive debonding, creep, or crack initiation, yet no fatigue or interface durability data are mentioned (khatri2024energyabsorptionof pages 10-11, yilmaz2026investigationofmechanical pages 12-13, yilmaz2026investigationofmechanical pages 10-11, yilmaz2026investigationofmechanical pages 9-9, ramasamy2026characterizationofpcabs pages 19-20) | High |
| 4 | Slip resistance / traction validation | Crutch-tip safety depends not only on shock attenuation but also on wet/dry traction and stability. Prior art emphasizes ferrule grip and the consequences of worn or altered contact surfaces; a lattice-based insert could change contact compliance and therefore frictional behavior, but no slip testing is described (CA2287886A1 pages 11-14) | Medium |
| 5 | Comparison to baseline/control | There is no explicit benchmark against a standard rubber ferrule or an existing shock-absorbing tip. Without a control, reviewers cannot judge whether the tensegrity insert delivers meaningful improvement over incumbent devices in force attenuation, durability, or usability (US11712394B1 pages 1-4, CA2287886A1 pages 11-14) | Medium |


*Table: This table ranks the missing context elements most likely to hurt acceptance by a materials/biomedical-device reviewer. It highlights where the abstract lacks the performance, validation, and benchmarking detail needed for a results-focused TMS submission.*

In brief: (1) the abstract provides no quantitative performance outcomes—no specific energy absorption (J/g), force-reduction percentages, or transmitted-impulse values—making it read as a design proposal rather than a results paper; (2) it is unclear whether the described tests are completed experiments or planned work; (3) PETG-TPU interface durability under cyclic loading is a known weak point in multi-material FFF (yilmaz2026investigationofmechanical pages 12-13, yilmaz2026investigationofmechanical pages 10-11, yilmaz2026investigationofmechanical pages 9-9) and is unaddressed; (4) slip-resistance/traction is safety-critical for crutch tips (CA2287886A1 pages 11-14) but absent; and (5) no baseline comparison against a standard rubber ferrule is mentioned.

---

## 4. Vibration Claim

The title promises "vibration attenuation," but the abstract body exclusively describes quasi-static compression and drop-weight impact tests—no frequency-domain measurements, transmissibility spectra, or vibration-specific testing is mentioned. The patent literature acknowledges that crutch walking transmits "shock and vibration" to the upper extremities (US20110240077A1 pages 23-25), but no peer-reviewed study was found quantifying vibration exposure or hand-arm vibration syndrome (HAVS) risk specifically from crutch use. While tensegrity lattices do exhibit tunable bandgap and wave-propagation properties (pajunen2019designandimpact pages 8-9, pajunen2021prestraininducedbandgaptuning pages 1-2), these have been demonstrated at frequencies and conditions far removed from crutch-gait impacts (~1–2 Hz strike rate). Without frequency-domain test data (e.g., transmissibility curves or accelerometer measurements during gait simulation), the "vibration attenuation" claim is unsupported. **Recommendation:** Either (i) remove "vibration" from the title and reframe as "Impact Attenuation," or (ii) add accelerometer-based transmissibility data to substantiate the vibration claim.

---

## 5. Novelty & Lab-to-Market Framing

The abstract's novelty in applying tensegrity architectures to crutch tips is plausible based on our patent and literature search. However, the "Laboratory to Market" framing is underdeveloped. The abstract mentions an FDA/ISO pathway but provides no information on: cost per unit, manufacturing cycle time, bill of materials, user-acceptance data, or clinical-trial pathway. For a symposium explicitly focused on translational readiness, the abstract would benefit greatly from at least one concrete translational metric.

**Recommended addition** (single sentence to strengthen translational angle): "The demonstrator can be fabricated in under 2 hours on a consumer-grade dual-extruder FFF printer at an estimated material cost below $X, positioning it for distributed manufacturing and patient-specific customization in clinical settings."

---

## 6. Concrete Rewrite Suggestions

1. **Replace "roughly 0.5 body weights per crutch"** with "up to 0.5 BW per crutch during prescribed partial-weight-bearing gait" — this qualifies the gait pattern and aligns with the instrumented-crutch literature (chamorromoriana2016acompactforearm pages 5-8, chamorromoriana2016acompactforearm pages 8-10).

2. **Replace "exploiting load-limiting buckling and rate-dependent damping"** with "exploiting buckling-induced load-limiting plateaus and TPU viscoelastic hysteresis" — this correctly attributes the plateau to the tensegrity mechanism and the damping to the elastomeric material, consistent with Pajunen et al. (2019) (pajunen2019designandimpact pages 5-7, pajunen2019designandimpact pages 7-8) and Khatri & Egan (2024) (khatri2024energyabsorptionof pages 10-11).

3. **Replace "A prior-art survey confirms that no existing crutch tip applies tensegrity architectures, and an FDA Class I, ISO 11334-1 regulatory pathway is clear"** with "A prior-art survey suggests that tensegrity architectures have not been applied to crutch tips, and an anticipated regulatory pathway is FDA Class I (21 CFR 890.3790) under ISO 11334-1" — this hedges appropriately on exhaustiveness and regulatory certainty (mottaghi2025opensource3dprintable pages 21-24).

4. **Add a quantitative result sentence**, even if preliminary, replacing generic claims. For example: "Preliminary experiments show a XX% reduction in peak transmitted force and specific energy absorption of X.X J/g at X% relative density" — this would dramatically strengthen the abstract for a results-oriented TMS audience, following the approach of Mo et al. (2023) who reported specific optimization outcomes from Bayesian frameworks (mo2023accelerateddesignof pages 1-1, mo2023accelerateddesignof pages 4-5).

5. **Modify the title** to "Bayesian-Optimized Multi-Material 3D-Printed Tensegrity Crutch Tips for Impact Attenuation" — removing "vibration" unless frequency-domain data are presented, or adding "and Vibration" only if transmissibility data will be shown (pajunen2019designandimpact pages 8-9, pajunen2021prestraininducedbandgaptuning pages 1-2).

---

## References

1. Chamorro-Moriana G, Sevillano J, Ridao-Fernández C. A compact forearm crutch based on force sensors for aided gait: reliability and validity. *Sensors*. 2016;16(6):925. doi:10.3390/s16060925.
2. Orishimo K, Shapira A, Kremenic I, McHugh M, Nicholas S. Comparison of hip and low back loads between normal gait, axillary crutch ambulation and walking with a hands-free crutch. *Int J Sports Phys Ther*. 2021;16(6):1454–1458. doi:10.26603/001c.29517.
3. Tsai HC, Hung TH, Chen CC, et al. Prevalence and risk factors for upper extremity entrapment neuropathies in polio survivors. *J Rehabil Med*. 2009;41(1):26–31. doi:10.2340/16501977-0290.
4. Macneal P, Crome CR, McNally S. Persistent anterior interosseous nerve palsy following forearm crutch use. *BMJ Case Rep*. 2017;2017:bcr2016218240. doi:10.1136/bcr-2016-218240.
5. Pajunen K, Johanns P, Pal RK, Rimoli JJ, Daraio C. Design and impact response of 3D-printable tensegrity-inspired structures. *Mater Des*. 2019;182:107966. doi:10.1016/j.matdes.2019.107966.
6. Pajunen K, Celli P, Daraio C. Prestrain-induced bandgap tuning in 3D-printed tensegrity-inspired lattice structures. *Extreme Mech Lett*. 2021;44:101236. doi:10.1016/j.eml.2021.101236.
7. Khatri NR, Egan PF. Energy absorption of 3D printed ABS and TPU multimaterial honeycomb structures. *3D Print Addit Manuf*. 2024;11(2):e840–e850. doi:10.1089/3dp.2022.0196.
8. Mo C, Perdikaris P, Raney JR. Accelerated design of architected materials with multifidelity Bayesian optimization. *J Eng Mech*. 2023;149(6). doi:10.1061/jenmdt.emeng-7033.
9. Mottaghi M, Woods MC, Danier L, et al. Open-source 3D printable forearm crutch. *PLOS ONE*. 2025;20. doi:10.1371/journal.pone.0318987.
10. Yilmaz S, Gul O, Coban O. Investigation of mechanical properties in layered multi-material 3D printing using commercial filaments. *J Vinyl Addit Technol*. 2026;32:484–498. doi:10.1002/vnl.70051.
11. Spatorico AL. Shock absorbing ferrule for assisted ambulation. US Patent US11712394B1. 2023.
12. Cooper B. Improved axillary crutch. CA Patent CA2287886A1. 2001.
13. Goodwin DM. Walking aids. AU Patent AU2008294554B2. 2013.
14. Rifkin J. Tensegrity joints for prosthetic, orthotic, and robotic devices. US Patent US20110093091A1. 2011.
15. Doherty S. Assistive mobility device. US Patent US20110240077A1. 2011.
16. Kawakami T. Ferrule member on tip of stick or crutch. JP Patent JP2007105364A. 2007.

References

1. (chamorromoriana2016acompactforearm pages 5-8): Gema Chamorro-Moriana, José Sevillano, and Carmen Ridao-Fernández. A compact forearm crutch based on force sensors for aided gait: reliability and validity. Sensors, 16:925, Jun 2016. URL: https://doi.org/10.3390/s16060925, doi:10.3390/s16060925. This article has 36 citations and is from a peer-reviewed journal.

2. (chamorromoriana2016acompactforearm pages 8-10): Gema Chamorro-Moriana, José Sevillano, and Carmen Ridao-Fernández. A compact forearm crutch based on force sensors for aided gait: reliability and validity. Sensors, 16:925, Jun 2016. URL: https://doi.org/10.3390/s16060925, doi:10.3390/s16060925. This article has 36 citations and is from a peer-reviewed journal.

3. (CA2287886A1 pages 9-11): Barbara Cooper. Improved axillary crutch. Patent (US,CA), 2001.

4. (orishimo2021comparisonofhip pages 2-3): Karl Orishimo, Amir Shapira, Ian Kremenic, Malachy McHugh, and Stephen Nicholas. Comparison of hip and low back loads between normal gait, axillary crutch ambulation and walking with a hands-free crutch in a healthy population. International Journal of Sports Physical Therapy, 16:1454-1458, Dec 2021. URL: https://doi.org/10.26603/001c.29517, doi:10.26603/001c.29517. This article has 3 citations.

5. (tsai2009prevalenceandrisk pages 3-5): HC Tsai, TH Hung, CC Chen, FK Lieu, H Cho, TH Tung, and SF Chen. Prevalence and risk factors for upper extremity entrapment neuropathies in polio survivors. Journal of Rehabilitation Medicine, 41(1):26-31, Jan 2009. URL: https://doi.org/10.2340/16501977-0290, doi:10.2340/16501977-0290. This article has 32 citations and is from a domain leading peer-reviewed journal.

6. (tsai2009prevalenceandrisk pages 1-2): HC Tsai, TH Hung, CC Chen, FK Lieu, H Cho, TH Tung, and SF Chen. Prevalence and risk factors for upper extremity entrapment neuropathies in polio survivors. Journal of Rehabilitation Medicine, 41(1):26-31, Jan 2009. URL: https://doi.org/10.2340/16501977-0290, doi:10.2340/16501977-0290. This article has 32 citations and is from a domain leading peer-reviewed journal.

7. (US11712394B1 pages 1-4): Anthony L. Spatorico. Shock absorbing ferrule for assisted ambulation. Patent (US), 2023.

8. (pajunen2019designandimpact pages 5-7): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

9. (pajunen2019designandimpact pages 1-2): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

10. (pajunen2019designandimpact pages 7-8): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.

11. (pajunen2021prestraininducedbandgaptuning pages 1-2): Kirsti Pajunen, Paolo Celli, and Chiara Daraio. Prestrain-induced bandgap tuning in 3d-printed tensegrity-inspired lattice structures. Extreme Mechanics Letters, 44:101236, Apr 2021. URL: https://doi.org/10.1016/j.eml.2021.101236, doi:10.1016/j.eml.2021.101236. This article has 33 citations and is from a peer-reviewed journal.

12. (khatri2024energyabsorptionof pages 10-11): Nava Raj Khatri and Paul F. Egan. Energy absorption of 3d printed abs and tpu multimaterial honeycomb structures. 3D Printing and Additive Manufacturing, 11:e840-e850, Apr 2024. URL: https://doi.org/10.1089/3dp.2022.0196, doi:10.1089/3dp.2022.0196. This article has 35 citations and is from a peer-reviewed journal.

13. (CA2287886A1 pages 11-14): Barbara Cooper. Improved axillary crutch. Patent (US,CA), 2001.

14. (mottaghi2025opensource3dprintable pages 21-24): Maryam Mottaghi, Morgan C. Woods, Laura Danier, Anita So, Jacob M. Reeves, and Joshua M. Pearce. Open-source 3d printable forearm crutch. PLOS ONE, Nov 2025. URL: https://doi.org/10.1371/journal.pone.0318987, doi:10.1371/journal.pone.0318987. This article has 5 citations and is from a peer-reviewed journal.

15. (orishimo2021comparisonofhip pages 3-5): Karl Orishimo, Amir Shapira, Ian Kremenic, Malachy McHugh, and Stephen Nicholas. Comparison of hip and low back loads between normal gait, axillary crutch ambulation and walking with a hands-free crutch in a healthy population. International Journal of Sports Physical Therapy, 16:1454-1458, Dec 2021. URL: https://doi.org/10.26603/001c.29517, doi:10.26603/001c.29517. This article has 3 citations.

16. (mo2023accelerateddesignof pages 1-1): Chengyang Mo, Paris Perdikaris, and Jordan R. Raney. Accelerated design of architected materials with multifidelity bayesian optimization. Journal of Engineering Mechanics, Jun 2023. URL: https://doi.org/10.1061/jenmdt.emeng-7033, doi:10.1061/jenmdt.emeng-7033. This article has 12 citations.

17. (mo2023accelerateddesignof pages 4-5): Chengyang Mo, Paris Perdikaris, and Jordan R. Raney. Accelerated design of architected materials with multifidelity bayesian optimization. Journal of Engineering Mechanics, Jun 2023. URL: https://doi.org/10.1061/jenmdt.emeng-7033, doi:10.1061/jenmdt.emeng-7033. This article has 12 citations.

18. (mo2023accelerateddesignof pages 2-4): Chengyang Mo, Paris Perdikaris, and Jordan R. Raney. Accelerated design of architected materials with multifidelity bayesian optimization. Journal of Engineering Mechanics, Jun 2023. URL: https://doi.org/10.1061/jenmdt.emeng-7033, doi:10.1061/jenmdt.emeng-7033. This article has 12 citations.

19. (mo2023accelerateddesignof pages 6-7): Chengyang Mo, Paris Perdikaris, and Jordan R. Raney. Accelerated design of architected materials with multifidelity bayesian optimization. Journal of Engineering Mechanics, Jun 2023. URL: https://doi.org/10.1061/jenmdt.emeng-7033, doi:10.1061/jenmdt.emeng-7033. This article has 12 citations.

20. (yilmaz2026investigationofmechanical pages 12-13): Sinan Yilmaz, Okan Gul, and Onur Coban. Investigation of mechanical properties in layered multi‐material <scp>3d</scp> printing using commercial filaments: direct stacking of <scp>abs</scp> , <scp>pa</scp> , and compatibilizing layers. Journal of Vinyl and Additive Technology, 32:484-498, Dec 2026. URL: https://doi.org/10.1002/vnl.70051, doi:10.1002/vnl.70051. This article has 2 citations and is from a peer-reviewed journal.

21. (yilmaz2026investigationofmechanical pages 10-11): Sinan Yilmaz, Okan Gul, and Onur Coban. Investigation of mechanical properties in layered multi‐material <scp>3d</scp> printing using commercial filaments: direct stacking of <scp>abs</scp> , <scp>pa</scp> , and compatibilizing layers. Journal of Vinyl and Additive Technology, 32:484-498, Dec 2026. URL: https://doi.org/10.1002/vnl.70051, doi:10.1002/vnl.70051. This article has 2 citations and is from a peer-reviewed journal.

22. (yilmaz2026investigationofmechanical pages 9-9): Sinan Yilmaz, Okan Gul, and Onur Coban. Investigation of mechanical properties in layered multi‐material <scp>3d</scp> printing using commercial filaments: direct stacking of <scp>abs</scp> , <scp>pa</scp> , and compatibilizing layers. Journal of Vinyl and Additive Technology, 32:484-498, Dec 2026. URL: https://doi.org/10.1002/vnl.70051, doi:10.1002/vnl.70051. This article has 2 citations and is from a peer-reviewed journal.

23. (ramasamy2026characterizationofpcabs pages 19-20): Mahalingam Nainaragaram Ramasamy, Ales Sliva, Akash Nag, Quoc-Phu Ma, Ondrej Hilser, Marie Heliova, Grazyna Simha Martynkova, Silvie Brozova, and Jan Dizo. Characterization of pc-abs and petg multi-material laminates fabricated by mex method. Polymers, 18:763, Mar 2026. URL: https://doi.org/10.3390/polym18060763, doi:10.3390/polym18060763. This article has 1 citations.

24. (US20110240077A1 pages 23-25): Sarah Doherty. Assistive mobility device. Patent (WO,US,CA), 2011.

25. (pajunen2019designandimpact pages 8-9): Kirsti Pajunen, Paul Johanns, Raj Kumar Pal, Julian J. Rimoli, and Chiara Daraio. Design and impact response of 3d-printable tensegrity-inspired structures. Materials & Design, 182:107966, Nov 2019. URL: https://doi.org/10.1016/j.matdes.2019.107966, doi:10.1016/j.matdes.2019.107966. This article has 100 citations and is from a highest quality peer-reviewed journal.
