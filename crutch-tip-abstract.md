# Conference abstract — Tensegrity crutch-tip impact absorber

Derived from this PR's Edison literature exploration (`edison-trajectories/01`–`05`)
and kept consistent with the author order / plain-text format established for the
TMS 2027 abstract in #73.

## Submission metadata (adjust per target venue)

- **Format:** plain-text, ≤150 words (matches TMS; trim/expand for others as noted below).
- **Presentation preference:** oral (poster acceptable).
- **Materials as converged in-project:** rigid **PETG** + elastomeric **TPU 95A**, multi-material FFF (Bambu H2D).

## Title

**Bayesian-Optimized Multi-Material 3D-Printed Tensegrity Crutch Tips for Impact and Vibration Attenuation**

## Authors

Marcus Madsen\*, Audrey Christiansen\*, Jinkwan Han\*, Jeffrey R. Hill† (presenting), Sterling G. Baird†

Department of Mechanical Engineering, Brigham Young University, Provo, UT

\* equal contribution &nbsp;·&nbsp; † equal contribution

## Abstract (150 words)

Long-term crutch users bear repeated ground-reaction forces of roughly 0.5 body
weights per crutch and experience high rates of upper-extremity overuse injury,
including crutch palsy, shoulder impingement, and carpal tunnel syndrome, yet
commercial crutch tips still rely on simple rubber ferrules or bulky springs. We
present a shock-absorbing crutch-tip insert built from multi-material
fused-filament-fabrication tensegrity-inspired lattices that pair rigid PETG
struts with elastomeric TPU tension elements, exploiting load-limiting buckling
and rate-dependent damping. Because the standard 19 to 25 mm ferrule envelope
severely limits stroke, we co-optimize unit-cell topology, strut diameter,
relative density, and prestress using closed-loop multi-objective Bayesian
optimization, maximizing specific energy absorption while minimizing peak
transmitted force across quasi-static compression and drop-weight impact tests.
A prior-art survey confirms that no existing crutch tip applies tensegrity
architectures, and an FDA Class I, ISO 11334-1 regulatory pathway is clear. This
demonstrator advances miniaturized, patient-tunable energy absorbers for
assistive and protective devices.

## Evidence base (for reviewer questions / longer versions)

- Peak vertical GRF ≈ 0.52 BW per crutch; spring-loaded designs cut GRF rise
  rate ~33% and early impulse 13–26% (`01`, MacGillivray 2016; Segura 2007).
- Broad overuse-injury burden (crutch palsy, rotator-cuff, CTS) documented across
  60 studies / 622 individuals (`01`–`02`, Manocha 2021).
- No prior art applies tensegrity to crutch tips; buckling tensegrities give a
  load-limiting plateau, <0.2% residual strain/impact, and BO-tunable stiffness
  (`01`, Pajunen 2019; Santos 2023).
- PETG/TPU FFF engineering data and a starting Bayesian-optimization design space
  in `04`.
