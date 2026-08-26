# Literature — Lansmont Model 23

The full literature survey for the Lansmont M23 (and the related instruments
covered in §4 of the Edison answer: tensegrity impact, crutch tips, 3D-printed
energy absorbers) is in:

- [`../../edison-trajectories/2026-05-08-equipment-m23-qtec-1a0f4a70.md`](../../edison-trajectories/2026-05-08-equipment-m23-qtec-1a0f4a70.md) — the verbatim Edison `formatted_answer` (Edison `LITERATURE_HIGH` task `1a0f4a70-3297-44d1-860a-dfcdd551e561`, 2026-05-08).
- [`../../edison-trajectories/2026-05-08-equipment-m23-qtec-1a0f4a70.json`](../../edison-trajectories/2026-05-08-equipment-m23-qtec-1a0f4a70.json) — the full structured task object for reproducibility.

## Highlights for the M23

- **Dominant use case in the literature is JEDEC-style board-level drop shock**
  of electronic assemblies, with half-sine pulses at 1500 g / 0.5 ms (cond. B),
  2000 g / 0.4 ms (cond. G), and 2900 g / 0.3 ms (cond. H).
  Confirmed M23 publications: Ouakad et al. 2012, Lall et al. 2012 / 2009, Ribas
  et al. 2013 / 2014, Chung & Kwak 2020, Agrawal et al. 2009, Yu et al. 2009,
  and Dornala 2019 (the most instrumentation-detailed reference: 5 MHz DAQ,
  0.103 mV/g accelerometer, drop heights of 14.2 in / 20.6 in for 1500 g / 2900 g).
- **No M23 paper was found for 3D-printed lattice / cushion testing.** The
  closest precedent is Ge, Cormier & Rice (2021), *J. Cellular Plastics*
  57:517–534, [doi:10.1177/0021955x20944972](https://doi.org/10.1177/0021955x20944972),
  which used an unspecified Lansmont cushion tester + PCB 353B04 +
  Lansmont TestPartner to generate ASTM D1596 cushion curves on PolyJet
  Kelvin-foam specimens. **The BYU MRG project will be among the first to
  adapt the M23 specifically for 3D-printed tensegrity / lattice cushion
  curves** — see Edison §6 ("Gaps and Limitations").
- **LANL has published an open-access operating manual** for the related
  Lansmont PDT 80 (Moore 2023, [doi:10.2172/1999531](https://doi.org/10.2172/1999531))
  — useful procedural reference for any Lansmont drop-tester SOP.

See §5 of the Edison answer for the five concrete methodology recommendations
the survey distilled for our project.
