# Conference abstract — Tensegrity crutch-tip impact absorber

Derived from this PR's Edison literature exploration (`edison-trajectories/01`–`09`)
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
  `constrains`; `high rates`→`substantial`. Remaining fact-checks resolved in Edison
  trajectories `07`–`08`.
- **Edison organizer-persona mock review (trajectory `09`, task `6e00f3ca…`) applied** —
  a mock program-committee pass in the voices of the four TMS 2027 *Biomedical Materials
  and Devices: From Laboratory to Market* organizers (Bandyopadhyay, Sachdev, Rodgers,
  Bose); overall *borderline / weak accept*, verdict *submit-with-substantial-revisions*.
  Its top scope-fit lever — **foreground the closed-loop Bayesian-optimization / AI-driven
  design angle** — is now applied: retitled to lead with *Closed-Loop Bayesian
  Optimization* and the method sentence now opens with the BO framework (the symposium
  explicitly calls for AI/ML in biomedical-device manufacturing). Also softened the
  prior-art claim (acknowledging US 11,712,394 B1 and other shock-absorbing ferrule prior
  art rather than implying a technological vacuum); narrowed novelty to `no
  tensegrity-based crutch-tip absorber` (tensegrity impact structures exist elsewhere);
  reframed the regulatory line to `an anticipated Class I pathway … and ISO 11334-1
  framework guide verification`; and added a lab-to-market clause (`crutch abandonment
  exceeds 30%, motivating distributed, patient-tunable manufacturing`).
- **No measured performance numbers yet — the abstract names the benchmark to *exceed*, not a
  placeholder.** We do not yet have measured SEA / peak-force-reduction values, and (per the
  Jul 1 2026 request, with the abstract due that night) we deliberately avoid a bracketed
  placeholder. Instead the abstract states the control we intend to beat: a solid rubber
  ferrule that **transmits >95% of applied load** (deforms <1.3 mm under 445 N → essentially
  no shock absorption; trajectory `07`). The design goal is to exceed that baseline; for
  context, miniaturized architected TPU / multi-material absorbers report **SEA ≈ 1–8 J/g**
  (trajectory `07`), which is the performance envelope we are targeting. Replace with our
  measured value once quasi-static/drop-weight tests are run.

## Title

**Closed-Loop Bayesian Optimization of Multi-Material 3D-Printed Tensegrity Crutch-Tip Impact Absorbers**

## Authors

Marcus Madsen\*, Audrey Christiansen\*, Jinkwan Han\*, Jeffrey R. Hill† (presenting), Sterling G. Baird†

Department of Mechanical Engineering, Brigham Young University, Provo, UT

\* equal contribution &nbsp;·&nbsp; † equal contribution

## Abstract (150 words)

Long-term crutch users load each crutch to ~0.5 body weights during
partial-weight-bearing gait and experience substantial upper-extremity overuse
injury, including crutch palsy, shoulder impingement, and carpal tunnel
syndrome; commercial crutch tips predominantly use rubber ferrules, while
existing spring-loaded dampers add bulk without architected tunability. We
apply closed-loop, multi-objective Bayesian optimization to design a crutch-tip
insert from multi-material fused-filament-fabrication tensegrity-inspired
lattices, pairing rigid PETG struts with elastomeric TPU elements to exploit
buckling-induced load-limiting plateaus and TPU viscoelastic hysteresis. Within
the standard 19–25 mm crutch-shaft interface, we co-optimize unit-cell topology,
strut diameter, relative density, and prestress to maximize specific energy
absorption and minimize peak transmitted force across quasi-static compression
and drop-weight impact, aiming to exceed a rubber-ferrule baseline that
transmits over 95% of applied load. Prior-art review identified no
tensegrity-based crutch-tip absorber; an anticipated Class I (21 CFR 890.3790),
ISO 11334-1 pathway guides verification. Crutch abandonment exceeds 30%,
motivating distributed, patient-tunable manufacturing.

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
- **Benchmark-to-exceed basis (`07`):** a solid rubber ferrule deforms <1.3 mm under 445 N and
  transmits >95% of applied load (essentially no shock absorption) — this is the control the
  abstract names as the bar to beat. For context, miniaturized architected TPU / multi-material
  absorbers report SEA ≈ 1–8 J/g, defining the performance envelope we target; a ~30–60%
  peak-force reduction versus the rubber baseline is the internal design goal, stated in the
  abstract as "exceed a rubber-ferrule baseline that transmits over 95% of applied load" rather
  than a specific unmeasured number. Replace with our measured value once tests are run.
- **Honest gaps to acknowledge in Q&A (`08`):** no high-cycle (10⁵–10⁶) fatigue data exist
  for *any* co-printed rigid/soft polymer interface, and PETG–TPU mode-I toughness is
  un-measured — interfacial delamination is the dominant risk; a bare glassy PETG lattice
  will not meet a COF ≥ 0.4 traction threshold, so a co-printed TPU tread is needed; and no
  study quantifies vibration/HAVS transmissibility through a crutch tip (crutch impact is a
  ~1–2 Hz transient, unlike sustained HAVS vibration) — hence the impact-only framing.
- **Lab-to-market hooks (`03`, `05`, `09`):** crutch/assistive-device abandonment ≈ 31%
  (Sugawara 2018) and desktop FFF enables distributed, patient-tunable point-of-care
  manufacturing (Mottaghi 2025) — the basis for the closing translational clause.
- **Scope-fit / organizer-persona review (`09`):** foreground the closed-loop BO / AI-driven
  design methodology (the symposium's AI/ML-in-manufacturing theme is the strongest hook);
  likely organizer questions center on PETG–TPU interface integrity (Bandyopadhyay),
  fatigue/durability over gait cycles (Sachdev), design controls / FDA classification of a
  novel insert (Rodgers), and skin-contact biocompatibility / wear debris (Bose).
