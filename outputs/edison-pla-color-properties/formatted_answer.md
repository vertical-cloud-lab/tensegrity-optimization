Question: We 3D-print small tensegrity structures on a Bambu Lab H2D FFF printer using Bambu Lab "PLA Basic"
filament. We need to know whether filament COLOR alone (white vs black, same product line, same
nominal base resin, differing only in the colour masterbatch) produces measurably different
mechanical behaviour in the printed part. Specifically:

1) Stiffness and strength: do pigments/colorants change the tensile/flexural elastic modulus, yield
   and ultimate strength, elongation at break, and layer-to-layer (interlayer/Z-direction) bond
   strength of FFF-printed PLA? Please give quantitative spreads reported in the literature between
   colours of the same nominal PLA grade (percent differences, standard deviations), and say whether
   colour-to-colour differences are larger or smaller than batch-to-batch, moisture, and
   print-parameter (temperature, speed, cooling) variability.

2) Damping / shock and vibration transmission: does colour change the viscoelastic response of
   printed PLA, i.e. loss factor tan(delta), storage modulus E' from DMA, damping ratio, impact
   strength (Izod/Charpy), coefficient of restitution, or wave/shock transmission and attenuation?
   Are there DMA or vibration studies comparing pigmented PLA grades (particularly titanium dioxide
   white and carbon black) against natural/unpigmented PLA?

3) Mechanism: what is known about how common colorants act on PLA — TiO2 (rutile/anatase) and
   carbon black as nucleating agents changing crystallinity and crystallisation kinetics; particle
   loading levels typical for commercial filament masterbatch (wt%); effects on melt viscosity/MFI
   and thus on extrusion and interlayer welding; effects on optical absorption, emissivity and
   thermal conductivity that change cooling rate and therefore crystallinity and layer bonding;
   possible photodegradation/UV and thermal-ageing differences (TiO2 is photocatalytic, carbon black
   is a UV stabiliser).

4) Practical guidance for a research group running a design-of-experiments/Bayesian-optimisation
   campaign on printed structures: is filament colour a variable that must be held fixed or
   randomised/blocked, or is it negligible relative to other noise sources? If measurable, which
   direction do white (TiO2) and black (carbon black) typically differ in modulus, strength,
   impact/damping, and dimensional accuracy? Are there any known anomalies (e.g. specific colours
   of specific vendors testing significantly weaker/stronger)?

Please give concrete numbers with citations wherever available, distinguish peer-reviewed data from
community/hobbyist test data, and state explicitly where the evidence is thin or contradictory.

# Effect of filament colour on FFF-printed PLA

## Executive conclusion

**Colour should not be assumed mechanically negligible.** Peer-reviewed, same-manufacturer PLA experiments have found colour-associated differences in printed ultimate tensile strength (UTS) approaching **29–31%**, as well as strong colour interactions with nozzle temperature and layer height. However, those studies generally did not identify the pigments chemically, did not separate masterbatch carrier/additive effects from pigment effects, and did not test Bambu Lab PLA Basic. They therefore demonstrate a potentially important **formulation/colour-SKU effect**, not a universal intrinsic law that white PLA is stronger or weaker than black PLA. (frunzaverde2023theinfluenceof pages 2-3)

For a research DOE or Bayesian-optimisation campaign, use one colour and preferably one lot throughout. If both white and black will be used, treat **colour/SKU as a categorical factor or block**, randomize run order within blocks, and test a colour × nozzle-temperature interaction. Moisture, orientation, raster direction, layer geometry, and thermal history must also be controlled; several of these can equal or exceed reported colour effects.

| Comparison/source type | Material/colors and controls | Endpoint | Quantitative result | Interpretation/limitations |
|---|---|---|---|---|
| Peer-reviewed direct color comparison | Verbatim PLA, natural vs black, same manufacturer; print temperature varied 200–240 °C; layer thickness 0.2 mm; 100% infill; 5 tensile specimens per color-temperature condition | Ultimate tensile strength (UTS) | Natural PLA: minimum reported UTS 47.43 MPa at 220 °C; maximum 50.41 MPa at 230 °C. Black PLA: UTS decreased from 52.41 MPa at 200 °C to 43.23 MPa at 240 °C. Black was stronger than natural at 200–210 °C, then weaker at higher temperature: a clear color–temperature crossover. (frunzaverde2022theinfluenceof pages 7-9, frunzaverde2022theinfluenceof pages 5-7) | Strong evidence that color can shift optimum nozzle temperature and strength ranking even within one vendor line. Study reported UTS only; no modulus, yield, elongation, impact, or direct Z-bond data. Pigment identity not chemically verified. |
| Peer-reviewed direct color comparison | Same Verbatim natural vs black study and controls as above | Dimensional accuracy | Best overall dimensional accuracy was black PLA; maximum volumetric deviation 1.96% for black (at 230 °C) versus 5.50% for natural (at 240 °C). (frunzaverde2022theinfluenceof pages 7-9, frunzaverde2022theinfluenceof pages 5-7) | Black gave tighter dimensions under these settings, but not uniformly better strength. Suggests color changes melt flow/cooling enough to affect both geometry and mechanics. |
| Peer-reviewed direct color comparison | Verbatim PLA natural/black/red/grey; same manufacturer; layer height varied 0.05–0.20 mm; 210 °C, 50 mm/s, 0.40 mm nozzle, 100% infill; 5 tensile specimens per color-layer condition | UTS and ANOVA effect size | Grey PLA had the highest UTS, 57.10–59.82 MPa across layer heights. UTS decreased with increasing layer height for all colors. Black showed the strongest layer-height sensitivity: 23.41% spread between extreme UTS values; grey only 4.77%; natural 6.73%; red 6.37%. Two-way ANOVA: color η² = 97.3%, layer height η² = 85.5%, interaction η² = 80.0%. (frunzaverde2023theinfluenceof pages 1-2, frunzaverde2023theinfluenceof pages 10-12, frunzaverde2023theinfluenceof pages 3-5, frunzaverde2023theinfluenceof pages 7-10) | Strong controlled evidence that color can be a first-order factor for UTS in a given vendor/product family. Still limited to UTS; no modulus/yield/elongation/impact/interlayer test values extracted here. |
| Peer-reviewed direct color comparison | Same Verbatim 4-color study as above | Dimensional accuracy and mesostructure | Width deviations ranged 0.17% (black, 0.05 mm) to 4.10% (red, 0.15 mm); thickness deviations 2.32% (grey, 0.10 mm) to 12.19% (red, 0.20 mm). Cross-section difference between red and black prints ranged 3.94% at 0.10 mm to 11.23% at 0.20 mm. Black and natural gave better dimensional accuracy but lower strength than grey/red. (frunzaverde2023theinfluenceof pages 5-7, frunzaverde2023theinfluenceof pages 7-10) | Supports mechanism that color changes apparent viscosity/cooling: red showed over-extrusion tendencies; black under-extrusion at thick layers. Vendor-specific and not automatically transferable to Bambu PLA Basic. |
| Peer-reviewed process-variability benchmark | Printed PLA, literature synthesis from controlled parameter studies | Temperature, speed, raster, layer, orientation effects on tensile properties/interlayer quality | Nozzle temperature increase 200→220 °C improved tensile strength by about 9–12%; increasing feed rate 40→60 mm/s reduced strength/modulus by about 6–7%; raster angle 0°→90° reduced tensile strength by 40% and modulus by 29%; lower layer thickness improved strength about 12% in one study; orientation effects reached about 91% in strength and 40% in modulus between favorable and upright builds. (gajjar2025effectsofkey pages 1-2, gajjar2025effectsofkey pages 8-10, gonabadi2020theeffectof pages 1-2) | For many setups, color effects are comparable to temperature/speed effects and smaller than the largest orientation/raster effects. Thus color is not negligible in DOE, but usually not the dominant source once geometry/orientation are unconstrained. |
| Peer-reviewed moisture benchmark | Multiple PLA grades and PLA/PBS blends; filament humidity conditioning before FDM | Strength/MFI degradation from moisture | Moisture caused up to 20% reduction in filament tensile strength and ~50% increase in MFI for moisture-sensitive PLA 4043D; ASTM tensile samples from PLA grades stored at room conditions for 3 months showed 24–36% strength loss. (quader2024characterizingtheeffect pages 36-40, quader2024characterizingtheeffect pages 40-44) | Moisture can equal or exceed reported color effects. Drying/handling control is essential before attributing differences to black vs white. Grade dependence is large. |
| Peer-reviewed moisture benchmark | Three PLA filament grades under moisture exposure | Modulus/strength sensitivity | PLA grades were classified as low, moderate, or high water sensitivity; linearized fits showed grade-to-grade variation in initial modulus (1.962–2.716 GPa) and initial tensile strength (27.415–50.505 MPa), with moisture-dependent property reductions ranging from low to >10% class depending on grade. (aniskevich2023moisturesorptionand pages 12-14) | Direct lot-to-lot or SKU-to-SKU comparisons remain scarce, but grade dependence shows that uncontrolled material differences can confound color conclusions. |
| Peer-reviewed mechanism support | Controlled color studies plus PLA nucleation review | Plausible mechanisms | Color studies attributed differences to altered thermal conductivity, glass-transition/melting behavior, viscosity, cooling rate, voiding, and interlayer adhesion; separate PLA nucleation literature shows particulate additives can greatly accelerate crystallization (e.g., crystallization half-time reductions from 4.1 to 1.8 min or to <1 min for strong nucleants, depending on additive). (gao2024theeffectsof pages 8-10, frunzaverde2023theinfluenceof pages 7-10, frunzaverde2022theinfluenceof pages 7-9) | Mechanism is plausible, but the studies did not chemically confirm whether black = carbon black or white = TiO2, nor pigment loading. Use mechanistic direction only cautiously for commercial filament. |
| Evidence gap | Printed PLA damping/DMA/impact by color | tan(delta), E', damping ratio, restitution, wave/shock transmission, Izod/Charpy | No same-grade, same-manufacturer white-vs-black or pigmented-vs-natural FFF PLA study was found that directly reports color effects on DMA storage modulus/loss factor, damping ratio, coefficient of restitution, impact strength, or shock attenuation. General DMA studies exist for printed PLA, but not as controlled color comparisons. (struz2024wearanddynamic pages 12-15, struz2024wearanddynamic pages 8-10) | The evidence for dynamic/vibration behavior is thin. Do not infer damping behavior from static tensile data alone. |
| Evidence gap / applicability to user case | Bambu Lab PLA Basic, white vs black, on Bambu H2D | Direct relevance to user’s material | No direct peer-reviewed white-vs-black data were found for Bambu Lab PLA Basic specifically. (frunzaverde2022theinfluenceof pages 1-2, frunzaverde2023theinfluenceof pages 2-3) | Best current inference is from analogous commercial PLA color studies, not from the exact Bambu product. For a research campaign, color should be held fixed or blocked/randomized rather than assumed negligible. |


*Table: This table condenses the strongest peer-reviewed evidence and the main evidence gaps relevant to whether PLA filament color changes printed-part behavior. It is useful for comparing the magnitude of color effects against moisture and process-parameter variability, and for judging how much confidence to place in extrapolation to Bambu PLA Basic white versus black.*

## 1. Stiffness, strength, elongation, and interlayer bonding

### Direct peer-reviewed colour comparisons

The strongest controlled evidence comes from Verbatim PLA studies in which printing parameters and manufacturer were held constant.

In a natural-versus-black experiment at 200–240 °C, 0.20-mm layers, 100% infill and five replicates per colour-temperature condition, black PLA decreased from **52.41 MPa at 200 °C to 43.23 MPa at 240 °C**, a 17.5% decline. Natural PLA had a reported minimum of **47.43 MPa at 220 °C** and maximum of **50.41 MPa at 230 °C**. Black was stronger at 200–210 °C but weaker above that range. Thus, colour changed not merely the mean strength but the apparent optimum printing temperature. (frunzaverde2022theinfluenceof pages 7-9, frunzaverde2022theinfluenceof pages 5-7)

A second study used natural, black, red, and grey Verbatim PLA at 210 °C, 50 mm/s, 100% infill, and layer heights from 0.05 to 0.20 mm, again with five tensile specimens per cell. Grey produced the highest UTS, **57.10–59.82 MPa**. The UTS spread caused by layer height was **23.41% for black**, compared with 4.77% for grey, 6.73% for natural, and 6.37% for red. Two-way ANOVA reported very large effect sizes: colour η² = **97.3%**, layer height η² = **85.5%**, and their interaction η² = **80.0%**. These η² values describe variance in that specific factorial experiment and should not be interpreted as percentages of all real-world PLA variability. (frunzaverde2023theinfluenceof pages 1-2, frunzaverde2023theinfluenceof pages 10-12, frunzaverde2023theinfluenceof pages 3-5, frunzaverde2023theinfluenceof pages 7-10)

The papers calculated standard deviations and 95% confidence intervals from five specimens per condition, but the machine-readable text did not expose all numerical SD values. Consequently, it is not possible here to give a reliable pooled colour-specific coefficient of variation. The effects were nevertheless statistically resolved by the authors. (frunzaverde2023theinfluenceof pages 3-5, frunzaverde2022theinfluenceof pages 5-7)

### Properties for which direct evidence is missing

The controlled colour literature located here primarily reports **UTS**, not a complete constitutive characterization. There is insufficient same-grade colour-controlled evidence to assign quantitative white-versus-black differences in:

- tensile or flexural elastic modulus;
- tensile yield stress or flexural strength;
- elongation at break;
- fracture toughness;
- direct Z-direction or interlaminar tensile/shear strength.

One broader commercial-filament study found differences among coloured materials, including lower strength for some coloured PLA than natural PLA and a white-versus-green PLA/PHA difference, but unknown proprietary compositions prevented attribution to pigment alone; fracture strains could be within one standard deviation. (bhardwaj2022mechanicalpropertiesof pages 6-10)

### Interlayer bonding

Although no direct colour-controlled Z-tension value was found, microscopy supplies indirect evidence. The four-colour study observed colour-dependent over-extrusion, under-extrusion, air gaps, and delamination. Black and natural specimens had better dimensional accuracy but lower UTS than grey/red in that experiment, attributed by the authors to faster cooling and weaker road-to-road adhesion. Black also showed the largest layer-height sensitivity. These observations establish that colour formulation can affect weld quality, but they do not quantify an intrinsic Z-bond strength. (frunzaverde2023theinfluenceof pages 5-7, frunzaverde2023theinfluenceof pages 7-10)

### Relative magnitude of other sources of variation

Colour differences are **comparable to ordinary thermal/process changes**, but usually smaller than extreme orientation effects:

- nozzle temperature 200→220 °C: approximately **9–12%** strength increase in one controlled study;
- speed 40→60 mm/s: approximately **6–7%** reduction in strength/modulus;
- raster 0°→90°: **40%** strength and **29%** modulus reduction;
- layer-thickness changes: about **12%** in one range, with larger effects reported in other ranges;
- favourable versus upright build orientation: approximately **91%** difference in tensile strength and **40%** in modulus; shear strength was 36 versus 18 MPa. (gajjar2025effectsofkey pages 1-2, gajjar2025effectsofkey pages 8-10, gonabadi2020theeffectof pages 1-2)

Moisture is also a first-order confounder. Moisture-sensitive PLA 4043D showed about **20% lower filament tensile strength and 50% higher MFI**, while printed samples from four PLA grades stored under room conditions for three months lost **24–36%** strength. The response was strongly grade-dependent. (quader2024characterizingtheeffect pages 36-40, quader2024characterizingtheeffect pages 40-44)

Direct repeated-lot studies of an otherwise identical PLA colour SKU are sparse. Therefore, the literature does **not** support a universal statement that colour variability is larger or smaller than lot-to-lot variability. It does show that colour effects can exceed typical temperature/speed effects, while moisture and orientation can equal or exceed them.

## 2. Damping, impact, and shock/vibration transmission

This is the largest evidence gap. General DMA studies of printed PLA measure storage modulus, loss modulus, and tan δ; one example reported a PLA transition onset near 57 °C and Tg estimates around 59–64 °C under its particular DMA method. It did **not** compare colours. (struz2024wearanddynamic pages 12-15, struz2024wearanddynamic pages 8-10)

No convincing same-manufacturer pigmented-versus-natural PLA comparison was found for:

- storage modulus E′ or loss modulus E″;
- tan δ or modal damping ratio;
- Izod or Charpy impact energy;
- coefficient of restitution;
- wave speed, shock transmission, or attenuation;
- specifically TiO₂-white versus carbon-black PLA.

Accordingly, no evidence-based direction can be assigned to white versus black damping. A modest filler-induced increase in stiffness, crystallinity, or interface friction could alter E′ and tan δ, while colour-dependent porosity and interlayer welding could dominate structure-level damping in the opposite direction. **Static UTS cannot be used as a proxy for damping or impact resistance.**

For tensegrity structures, measured vibration transmission may be more sensitive to strand geometry, prestress, joint compliance, print anisotropy, and small mass/dimensional errors than to the polymer's bulk tan δ. This must be tested at the structure level.

## 3. Mechanisms and what can—and cannot—be inferred about TiO₂ and carbon black

### Pigment identity and loading

It is reasonable chemically to expect a white masterbatch to contain rutile TiO₂ and a black masterbatch to contain carbon black, but this was **not verified for Bambu Lab PLA Basic** in the evidence found. Commercial formulations may also differ in carrier resin, dispersant, stabilizer, lubricant, nucleant, and chain modifier. “Same nominal base resin” therefore does not mean that pigment is the only molecular or processing difference.

Published masterbatches commonly contain concentrated pigment and are let down into polymer, but the final pigment fraction is proprietary and cannot be inferred reliably from colour alone. White generally requires appreciably more pigment than black because TiO₂ has a lower tinting strength by mass than carbon black. A plausible industrial order of magnitude is several wt% TiO₂ in opaque white versus sub-percent to roughly 1 wt% carbon black in black material, but **these are formulation heuristics, not measured Bambu values**, and should not be entered into a quantitative model without TGA/ash, XRF/ICP, microscopy, or supplier disclosure.

### Crystallization and nucleation

PLA crystallizes slowly under ordinary FFF cooling. Dispersed particles can provide heterogeneous nuclei, changing crystallization onset, half-time, spherulite density, and final crystallinity. The magnitude can be large for purpose-designed nucleants: one review reports a half-time reduction from **4.1 to 1.8 min** at 0.2 wt% nucleant, and another system from 28.5 min to under 1 min while increasing crystallinity from 1.5% to over 25.9%. These values show mechanistic potential but are not TiO₂/carbon-black colour-filament measurements. (gao2024theeffectsof pages 8-10)

Both TiO₂ and carbon black can nucleate PLA, but results depend on particle surface chemistry, agglomeration, PLA stereochemistry/molecular weight, thermal history, and loading. Greater crystallinity generally raises stiffness, heat resistance, and sometimes strength, while often lowering ductility and impact toughness. Under fast FFF cooling, however, enhanced nucleation may still produce little crystallinity unless the deposited road remains in PLA's crystallization window sufficiently long.

### Melt flow and interlayer welding

Particles may raise melt elasticity/viscosity through hydrodynamic and particle-network effects; alternatively, carrier resin, lubricants, moisture, or thermomechanical chain scission can lower viscosity and increase MFI. Thus neither “black is more viscous” nor “white is more viscous” is universal.

The controlled colour study observed red over-extrusion and black under-extrusion under identical settings, consistent with colour-specific rheology. Black also had a different strength-temperature curve, while moisture alone can raise MFI by approximately 50%. These findings show why a common slicer profile can create different void fractions and weld areas even when nominal PLA resin is the same. (quader2024characterizingtheeffect pages 40-44, frunzaverde2023theinfluenceof pages 5-7, frunzaverde2022theinfluenceof pages 7-9)

Interlayer welding requires intimate contact plus polymer-chain diffusion while both roads remain sufficiently hot. A colour formulation that increases viscosity may reduce wetting/contact; one that accelerates cooling shortens diffusion time; one that reduces molecular weight may flow readily but ultimately have weaker chains. These competing effects explain the lack of a universal colour ranking.

### Optical and thermal effects

Carbon black strongly absorbs visible and near-infrared radiation and generally raises optical emissivity. TiO₂ white strongly scatters visible light. Either can change radiative heat exchange, while particulate fillers can alter thermal conductivity and heat capacity. In the Verbatim studies, black was inferred to cool/contract differently, producing better dimensional accuracy but, under some settings, more bond defects and lower strength. Those thermal-conductivity explanations were not accompanied by direct conductivity measurements and should be regarded as plausible interpretation rather than proof. (frunzaverde2023theinfluenceof pages 5-7, frunzaverde2023theinfluenceof pages 7-10, frunzaverde2022theinfluenceof pages 7-9)

On an enclosed H2D, nozzle/contact conduction and forced convective cooling will usually dominate radiative exchange at small bead scale. Nevertheless, optical absorption can matter for infrared thermography and external radiant heating: a black and a white road can report different apparent IR temperatures unless emissivity is calibrated.

### UV and thermal ageing

Uncoated anatase TiO₂ is strongly photocatalytic and can accelerate oxidation and chain scission in adjacent PLA under UV. Pigment-grade white normally uses predominantly rutile TiO₂ with surface treatments intended to suppress photocatalysis, so white TiO₂ can instead act as an effective UV screen. Carbon black is usually a strong UV absorber/stabilizer when well dispersed, although its higher solar absorption can raise outdoor equilibrium temperature. Therefore:

- **carbon-black PLA would generally be expected to retain properties better under UV**, all else equal;
- **white PLA may either screen UV or accelerate degradation**, depending on TiO₂ phase, coating, dispersion, and stabilizer package;
- neither expectation establishes short-term indoor mechanical behaviour.

## 4. Expected direction for white versus black

There is **no defensible universal ordering** for Bambu PLA Basic based on the present literature.

| Property | Cautious expectation | Confidence |
|---|---|---|
| Bulk modulus | Particles may raise modulus slightly; higher TiO₂ loading could make white stiffer, but crystallinity and additives may reverse this | Low |
| Printed tensile strength | Controlled data show colour-temperature crossovers; black may be stronger at one nozzle temperature and weaker at another | Moderate evidence for interaction, low for direction |
| Elongation/impact | Higher filler loading or crystallinity often reduces ductility, suggesting white could be more brittle, but no direct same-grade colour test supports this for Bambu | Very low |
| Interlayer strength | Determined by viscosity, cooling, and weld history; either colour may win after separate profile optimization | Low |
| Damping/tan δ | No reliable direction | Very low |
| Dimensional accuracy | Black was best in the cited Verbatim studies, with 1.96% maximum volumetric deviation versus 5.50% for natural in one experiment; this is vendor/profile-specific | Moderate for that system only |
| UV durability | Carbon black usually favourable; pigment-grade rutile white may also screen effectively | Moderate mechanistic, unverified for Bambu |

A particularly important anomaly is that black Verbatim PLA was strongest at the low end of the tested nozzle-temperature range but became weakest as temperature increased; grey, not natural or black, was strongest in the four-colour study. Red showed over-extrusion and the worst dimensional accuracy. These vendor-specific anomalies argue against treating colour as a simple monotonic pigment-loading variable. (frunzaverde2023theinfluenceof pages 5-7, frunzaverde2023theinfluenceof pages 7-10, frunzaverde2022theinfluenceof pages 7-9)

## 5. Recommended experimental strategy for the H2D tensegrity campaign

### If colour is not a scientific variable

1. **Fix colour, SKU, and lot** for the entire optimisation campaign. Purchase enough filament at once.
2. Record spool lot/production identifier, initial mass, drying history, storage RH, and cumulative open time.
3. Dry white and black identically before any comparison; print from controlled dry boxes if possible.
4. Keep printer, nozzle, build plate location, fan profile, enclosure state, layer time, and filament path fixed.
5. Randomize specimen position and run order to avoid conflating colour with machine drift.

### If structures may ultimately be printed in either colour

Use colour as a two-level categorical factor. At minimum, perform a screening experiment with:

- white and black;
- at least two independent spools/lots per colour if available;
- three or more replicate print jobs, not merely multiple coupons in one job;
- randomized run order;
- nozzle temperature at nominal and ±5–10 °C, because the literature indicates a colour × temperature interaction;
- mass and dimensional metrology on every structure.

Model spool/lot and print job as random effects, with colour, temperature, and their interaction as fixed effects. In Bayesian optimisation, either optimize within one colour or include colour as a categorical input; do not alternate colours while leaving colour unrecorded.

### Measurements suited to the application

Use both material coupons and complete tensegrity structures:

- ASTM/ISO tensile specimens in the dominant road direction and upright/Z orientation;
- flexural specimens if members bend appreciably;
- DSC for Tg, melting/cold-crystallization peaks and crystallinity;
- MFR/MFI or capillary rheology for flow differences;
- density or micro-CT/image analysis for void fraction;
- DMA at operating temperature and vibration frequency range;
- modal hammer or shaker tests for natural frequencies and damping ratios;
- drop/impulse tests with accelerometers for transmissibility and shock attenuation;
- prestress and member-dimension measurements, because they can dominate tensegrity dynamics.

A practical screening criterion is not merely statistical significance. Predefine an engineering equivalence margin—for example, ±3–5% for stiffness/frequency and a suitable margin for damping or peak acceleration. If the posterior colour effect lies inside that interval after accounting for lot and job, colour can subsequently be treated as negligible for that response and process window.

## Bottom line

The literature establishes that a commercial PLA **colour formulation can measurably alter UTS, dimensional accuracy, extrusion behaviour, and sensitivity to nozzle temperature/layer height**. Reported UTS spreads can approach 30%, so colour is not safely dismissed a priori. Conversely, evidence for modulus, elongation, direct Z-bond strength, impact, DMA damping, restitution, and shock transmission is too thin to predict white-versus-black behaviour—especially for Bambu Lab PLA Basic. The scientifically defensible policy is therefore: **hold colour and lot fixed during optimisation, or explicitly block/randomize colour and validate it experimentally; do not assume either white or black is universally stiffer, stronger, tougher, or better damped.**

References

1. (frunzaverde2023theinfluenceof pages 2-3): Doina Frunzaverde, Vasile Cojocaru, Nicoleta Bacescu, Costel-Relu Ciubotariu, Calin-Octavian Miclosina, Raul Rusalin Turiac, and Gabriela Marginean. The influence of the layer height and the filament color on the dimensional accuracy and the tensile strength of fdm-printed pla specimens. Polymers, 15:2377, May 2023. URL: https://doi.org/10.3390/polym15102377, doi:10.3390/polym15102377. This article has 109 citations.

2. (frunzaverde2022theinfluenceof pages 7-9): Doina Frunzaverde, Vasile Cojocaru, Costel-Relu Ciubotariu, Calin-Octavian Miclosina, Deian Dorel Ardeljan, Emil Florin Ignat, and Gabriela Marginean. The influence of the printing temperature and the filament color on the dimensional accuracy, tensile strength, and friction performance of fff-printed pla specimens. Polymers, 14:1978, May 2022. URL: https://doi.org/10.3390/polym14101978, doi:10.3390/polym14101978. This article has 106 citations.

3. (frunzaverde2022theinfluenceof pages 5-7): Doina Frunzaverde, Vasile Cojocaru, Costel-Relu Ciubotariu, Calin-Octavian Miclosina, Deian Dorel Ardeljan, Emil Florin Ignat, and Gabriela Marginean. The influence of the printing temperature and the filament color on the dimensional accuracy, tensile strength, and friction performance of fff-printed pla specimens. Polymers, 14:1978, May 2022. URL: https://doi.org/10.3390/polym14101978, doi:10.3390/polym14101978. This article has 106 citations.

4. (frunzaverde2023theinfluenceof pages 1-2): Doina Frunzaverde, Vasile Cojocaru, Nicoleta Bacescu, Costel-Relu Ciubotariu, Calin-Octavian Miclosina, Raul Rusalin Turiac, and Gabriela Marginean. The influence of the layer height and the filament color on the dimensional accuracy and the tensile strength of fdm-printed pla specimens. Polymers, 15:2377, May 2023. URL: https://doi.org/10.3390/polym15102377, doi:10.3390/polym15102377. This article has 109 citations.

5. (frunzaverde2023theinfluenceof pages 10-12): Doina Frunzaverde, Vasile Cojocaru, Nicoleta Bacescu, Costel-Relu Ciubotariu, Calin-Octavian Miclosina, Raul Rusalin Turiac, and Gabriela Marginean. The influence of the layer height and the filament color on the dimensional accuracy and the tensile strength of fdm-printed pla specimens. Polymers, 15:2377, May 2023. URL: https://doi.org/10.3390/polym15102377, doi:10.3390/polym15102377. This article has 109 citations.

6. (frunzaverde2023theinfluenceof pages 3-5): Doina Frunzaverde, Vasile Cojocaru, Nicoleta Bacescu, Costel-Relu Ciubotariu, Calin-Octavian Miclosina, Raul Rusalin Turiac, and Gabriela Marginean. The influence of the layer height and the filament color on the dimensional accuracy and the tensile strength of fdm-printed pla specimens. Polymers, 15:2377, May 2023. URL: https://doi.org/10.3390/polym15102377, doi:10.3390/polym15102377. This article has 109 citations.

7. (frunzaverde2023theinfluenceof pages 7-10): Doina Frunzaverde, Vasile Cojocaru, Nicoleta Bacescu, Costel-Relu Ciubotariu, Calin-Octavian Miclosina, Raul Rusalin Turiac, and Gabriela Marginean. The influence of the layer height and the filament color on the dimensional accuracy and the tensile strength of fdm-printed pla specimens. Polymers, 15:2377, May 2023. URL: https://doi.org/10.3390/polym15102377, doi:10.3390/polym15102377. This article has 109 citations.

8. (frunzaverde2023theinfluenceof pages 5-7): Doina Frunzaverde, Vasile Cojocaru, Nicoleta Bacescu, Costel-Relu Ciubotariu, Calin-Octavian Miclosina, Raul Rusalin Turiac, and Gabriela Marginean. The influence of the layer height and the filament color on the dimensional accuracy and the tensile strength of fdm-printed pla specimens. Polymers, 15:2377, May 2023. URL: https://doi.org/10.3390/polym15102377, doi:10.3390/polym15102377. This article has 109 citations.

9. (gajjar2025effectsofkey pages 1-2): Tusharbhai Gajjar, Richard Yang, Lin Ye, and Y. X. Zhang. Effects of key process parameters on tensile properties and interlayer bonding behavior of 3d printed pla using fused filament fabrication. Progress in Additive Manufacturing, 10:1261-1280, Jul 2025. URL: https://doi.org/10.1007/s40964-024-00704-y, doi:10.1007/s40964-024-00704-y. This article has 84 citations and is from a peer-reviewed journal.

10. (gajjar2025effectsofkey pages 8-10): Tusharbhai Gajjar, Richard Yang, Lin Ye, and Y. X. Zhang. Effects of key process parameters on tensile properties and interlayer bonding behavior of 3d printed pla using fused filament fabrication. Progress in Additive Manufacturing, 10:1261-1280, Jul 2025. URL: https://doi.org/10.1007/s40964-024-00704-y, doi:10.1007/s40964-024-00704-y. This article has 84 citations and is from a peer-reviewed journal.

11. (gonabadi2020theeffectof pages 1-2): H. Gonabadi, A. Yadav, and S. J. Bull. The effect of processing parameters on the mechanical characteristics of pla produced by a 3d fff printer. The International Journal of Advanced Manufacturing Technology, 111:695-709, Oct 2020. URL: https://doi.org/10.1007/s00170-020-06138-4, doi:10.1007/s00170-020-06138-4. This article has 329 citations.

12. (quader2024characterizingtheeffect pages 36-40): Raihan Quader, Evan Dramko, David Grewell, Jed Randall, and Lokesh Karthik Narayanan. Characterizing the effect of filament moisture on tensile properties and morphology of fused deposition modeled polylactic acid/polybutylene succinate parts. 3D Printing and Additive Manufacturing, 11:e1151-e1161, Jun 2024. URL: https://doi.org/10.1089/3dp.2022.0222, doi:10.1089/3dp.2022.0222. This article has 13 citations and is from a peer-reviewed journal.

13. (quader2024characterizingtheeffect pages 40-44): Raihan Quader, Evan Dramko, David Grewell, Jed Randall, and Lokesh Karthik Narayanan. Characterizing the effect of filament moisture on tensile properties and morphology of fused deposition modeled polylactic acid/polybutylene succinate parts. 3D Printing and Additive Manufacturing, 11:e1151-e1161, Jun 2024. URL: https://doi.org/10.1089/3dp.2022.0222, doi:10.1089/3dp.2022.0222. This article has 13 citations and is from a peer-reviewed journal.

14. (aniskevich2023moisturesorptionand pages 12-14): Andrey Aniskevich, Olga Bulderberga, and Leons Stankevics. Moisture sorption and degradation of polymer filaments used in 3d printing. Polymers, 15:2600, Jun 2023. URL: https://doi.org/10.3390/polym15122600, doi:10.3390/polym15122600. This article has 33 citations.

15. (gao2024theeffectsof pages 8-10): Peng Gao and Davide Masato. The effects of nucleating agents and processing on the crystallization and mechanical properties of polylactic acid: a review. Jun 2024. URL: https://doi.org/10.3390/mi15060776, doi:10.3390/mi15060776. This article has 64 citations.

16. (struz2024wearanddynamic pages 12-15): Jiri Struz, Miroslav Trochta, Lukas Hruzik, Daniel Pistacek, Sylwester Stawarz, Wojciech Kucharczyk, and Miroslaw Rucki. Wear and dynamic mechanical analysis (dma) of samples produced via fused deposition modelling (fdm) 3d printing method. Polymers, 16:3018, Oct 2024. URL: https://doi.org/10.3390/polym16213018, doi:10.3390/polym16213018. This article has 16 citations.

17. (struz2024wearanddynamic pages 8-10): Jiri Struz, Miroslav Trochta, Lukas Hruzik, Daniel Pistacek, Sylwester Stawarz, Wojciech Kucharczyk, and Miroslaw Rucki. Wear and dynamic mechanical analysis (dma) of samples produced via fused deposition modelling (fdm) 3d printing method. Polymers, 16:3018, Oct 2024. URL: https://doi.org/10.3390/polym16213018, doi:10.3390/polym16213018. This article has 16 citations.

18. (frunzaverde2022theinfluenceof pages 1-2): Doina Frunzaverde, Vasile Cojocaru, Costel-Relu Ciubotariu, Calin-Octavian Miclosina, Deian Dorel Ardeljan, Emil Florin Ignat, and Gabriela Marginean. The influence of the printing temperature and the filament color on the dimensional accuracy, tensile strength, and friction performance of fff-printed pla specimens. Polymers, 14:1978, May 2022. URL: https://doi.org/10.3390/polym14101978, doi:10.3390/polym14101978. This article has 106 citations.

19. (bhardwaj2022mechanicalpropertiesof pages 6-10): Nancy Bhardwaj, Hani Henein, and Tonya Wolfe. Mechanical properties of thermoplastic polymers in fused filament fabrication (<scp>fff</scp>). Aug 2022. URL: https://doi.org/10.1002/cjce.24562, doi:10.1002/cjce.24562. This article has 12 citations.
