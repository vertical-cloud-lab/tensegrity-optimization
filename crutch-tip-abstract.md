# Conference abstract — Tensegrity crutch-tip impact absorber

Derived from this PR's Edison literature exploration (`edison-trajectories/01`–`05`)
and kept consistent with the author order / plain-text format established for the
TMS 2027 abstract in #73.

## Submission metadata

- **Venue:** TMS 2027 Annual Meeting & Exhibition — Orlando, FL, March 14–18, 2027.
- **Target symposium:** *Biomedical Materials and Devices: From Laboratory to Market*
  (best fit for the clinical-motivation + device-demonstrator + FDA Class I / ISO 11334-1
  + commercialization story). Backups: *Additive Manufacturing and Innovative Feedstock
  Processing for Multifunctional Materials*, then *3D Printing of Scaffolds and Porous
  Materials*. Note: the AM/AI-methods symposia (*Additive Manufacturing Modeling,
  Simulation, and AI…* / *AI-Enabled Materials Processing…*) are the home of the sibling
  methods abstract in #73 — keep this application abstract in the biomedical track to
  avoid self-competition.
- **Format:** plain-text, ≤150 words (TMS limit).
- **Presentation preference:** oral (poster acceptable).
- **Materials as converged in-project:** rigid **PETG** + elastomeric **TPU 95A**, multi-material FFF (Bambu H2D).
- **Edison peer review (trajectory `06`, task `74ac013b…`) applied** — retitled to *Impact
  Attenuation* (vibration/HAVS deferred to future work: no study yet quantifies vibration
  transmissibility through a crutch tip); `0.5 BW` qualified to partial-weight-bearing gait
  (swing-through hand loads run 1.14–3.36 BW); damping re-attributed to TPU viscoelastic
  hysteresis (tensegrity supplies the load-limiting plateau, not rate-dependence);
  `confirms`→`found no`, `is clear`→`anticipated` + 21 CFR 890.3790; `severely limits`→
  `constrains`; `high rates`→`substantial`. Remaining fact-checks pushed to Edison
  trajectories `07`–`08` (fetch next session).

## Title

**Bayesian-Optimized Multi-Material 3D-Printed Tensegrity Crutch Tips for Impact Attenuation**

## Authors

Marcus Madsen\*, Audrey Christiansen\*, Jinkwan Han\*, Jeffrey R. Hill† (presenting), Sterling G. Baird†

Department of Mechanical Engineering, Brigham Young University, Provo, UT

\* equal contribution &nbsp;·&nbsp; † equal contribution

## Abstract (150 words)

Long-term crutch users load each crutch to roughly 0.5 body weights during
partial-weight-bearing gait and experience substantial upper-extremity overuse
injury, including crutch palsy, shoulder impingement, and carpal tunnel
syndrome, yet commercial crutch tips still predominantly rely on rubber ferrules
or bulky spring dampers. We present a shock-absorbing crutch-tip insert built
from multi-material fused-filament-fabrication tensegrity-inspired lattices that
pair rigid PETG struts with elastomeric TPU tension elements, exploiting
buckling-induced load-limiting plateaus and TPU viscoelastic hysteresis. Because
the standard 19 to 25 mm crutch-shaft interface constrains insert stroke, we
co-optimize unit-cell topology, strut diameter, relative density, and prestress
using closed-loop multi-objective Bayesian optimization, maximizing specific
energy absorption while minimizing peak transmitted force across quasi-static
compression and drop-weight impact tests. A prior-art survey found no crutch tip
applying tensegrity architectures, and an anticipated FDA Class I (21 CFR
890.3790) pathway under ISO 11334-1 applies. This design study advances
miniaturized, patient-tunable absorbers for assistive devices.

## Evidence base (for reviewer questions / longer versions)

- Peak vertical GRF ≈ 0.5 BW per crutch is a partial-weight-bearing figure
  (Chamorro-Moriana 2016); swing-through gait drives hand loads of 1.14–3.36 BW and
  axillary-crutch GRF ~25% above normal gait (`06`, Orishimo 2021) — hence the qualified
  wording. Spring-loaded designs cut GRF rise rate ~33% / early impulse 13–26% (`01`).
- Substantial upper-extremity overuse burden: 80% entrapment-neuropathy prevalence in
  polio survivors (cane/crutch OR 6.2–13.7), plus documented crutch palsy, impingement,
  and CTS (`02`, `06`; Tsai 2009, Manocha 2021).
- No prior art applies tensegrity to crutch tips; buckling tensegrities give a
  load-limiting *plateau* with <0.2% residual strain/impact, while dissipation is driven by
  TPU viscoelastic hysteresis rather than a tensegrity-specific rate-dependent mechanism
  (`01`, `06`; Pajunen 2019).
- FDA Class I under 21 CFR 890.3790 (generally 510(k)-exempt), ISO 11334-1 performance
  standard (`06`; Mottaghi 2025). Prior art richer than "rubber-or-springs" — spring,
  bellows, gas-spring, and viscoelastic ferrules exist (US11712394B1, `06`).
- PETG/TPU FFF engineering data and a starting Bayesian-optimization design space in `04`.
- **Open gaps → trajectories `07`–`08`:** ferrule bore-vs-envelope stroke budget,
  quantitative SEA (J/g) / peak-force-reduction benchmarks vs. a rubber-ferrule control,
  PETG–TPU interface fatigue over 10⁵–10⁶ gait cycles, printed-tip slip resistance, and
  whether any crutch-tip vibration/HAVS transmissibility benefit is measurable.
