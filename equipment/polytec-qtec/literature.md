# Literature — Polytec VibroFlex QTec

The full literature survey for the Polytec QTec (and the related instruments
covered in §4 of the Edison answer: tensegrity impact, crutch tips, 3D-printed
energy absorbers) is in:

- [`../../edison-trajectories/2026-05-08-equipment-m23-qtec-1a0f4a70.md`](../../edison-trajectories/2026-05-08-equipment-m23-qtec-1a0f4a70.md) — the verbatim Edison `formatted_answer` (Edison `LITERATURE_HIGH` task `1a0f4a70-3297-44d1-860a-dfcdd551e561`, 2026-05-08).
- [`../../edison-trajectories/2026-05-08-equipment-m23-qtec-1a0f4a70.json`](../../edison-trajectories/2026-05-08-equipment-m23-qtec-1a0f4a70.json) — the full structured task object for reproducibility.

## Highlights for the QTec / VibroFlex QTec

- **Most instrumentation-detailed paper:** Grétarsson & Lindell (2023),
  *ICHAV 2023*, [doi:10.3390/proceedings2023086010](https://doi.org/10.3390/proceedings2023086010)
  — VFX-I-160 sensor head + VFX-O-SRI short-range lens + Connect VXF-F-110
  front end at **100 kHz** bandwidth, NI 9223 DAQ at **1 MS/s**, used to
  measure hand-held impact-wrench vibration propagating into finger tissue.
  This matches the bandwidth of the unit on site, so its setup can be a
  template for ours.
- **Most analogous NDT / material-characterization use:** Geimer & Delorey (2025),
  [doi:10.2172/2589838](https://doi.org/10.2172/2589838) — VibroFlex QTec (SWIR)
  with a 2-axis scanning mirror, used for resonant ultrasound spectroscopy
  / mode-shape imaging of graphite components; **5 M samples at 250 kHz over 20 s**,
  spectra to **100 kHz**.
- **Quantified QTec advantage:** Martarelli et al. (2026),
  [doi:10.13052/97887-438-0151-1\_2](https://doi.org/10.13052/97887-438-0151-1_2)
  — comparative continuous-scanning LDV showing **~8 dB SNR improvement** with
  QTec multipath interferometry on a clamped aluminium plate. Argues for using
  QTec on our dark / curved / compliant TPU-PETG specimens *without* applying
  retroreflective tape.
- **No QTec publication was found on 3D-printed lattices or soft polymers.**
  Earlier Polytec families (OFV-5000/505, PSV-400) were used by Mohseni 2022
  on PLA metamaterials and by Amorusi 2018 on PolyJet phononic metamaterials.
  Combining Lansmont shock testing + LDV transient response on the *same*
  specimen is also unprecedented in the survey — flagged as a methodological
  contribution we can claim.
- **QTec-specific tutorial papers:** Eichenberger & Sauer 2022,
  [doi:10.1007/978-3-031-04098-6_1](https://doi.org/10.1007/978-3-031-04098-6_1)
  ("Introduction to multipath Doppler vibrometry"), and Shambaugh et al. 2023,
  [doi:10.1007/978-3-031-34910-2_14](https://doi.org/10.1007/978-3-031-34910-2_14)
  (multi-path strain measurement for very-high-cycle fatigue). Both authored
  with Polytec staff, useful as primary references for the QTec principle.

See §5 of the Edison answer for the five concrete methodology recommendations
the survey distilled for our project.
