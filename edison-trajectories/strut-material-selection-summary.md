# Strut Material Selection — Findings & Recommendation

**Issue:** "What is the right strut material? PLA vs. PETG vs. something else
(e.g., HF-reinforced), considering the difficulty of multi-material in this case."

**Source:** Edison Scientific `LITERATURE_HIGH` query, task
`5bb5e5d3-b386-4ece-a894-9c87f0d67036`, submitted and fetched
2026-05-09. Full artifacts:

- [`strut-material-selection-5bb5e5d3-b386-4ece-a894-9c87f0d67036.md`](strut-material-selection-5bb5e5d3-b386-4ece-a894-9c87f0d67036.md) — verbatim formatted answer (Question + Answer + 38 numbered references with DOIs)
- [`strut-material-selection-5bb5e5d3-b386-4ece-a894-9c87f0d67036.json`](strut-material-selection-5bb5e5d3-b386-4ece-a894-9c87f0d67036.json) — full structured response
- [`strut-material-selection-5bb5e5d3-b386-4ece-a894-9c87f0d67036-references.md`](strut-material-selection-5bb5e5d3-b386-4ece-a894-9c87f0d67036-references.md) — extracted references section
- Submission script: [`scripts/edison/submit_strut_material.py`](../scripts/edison/submit_strut_material.py)

The Edison query returned no separate file/data artifacts (no
`environment_config.data_storage_uris`, no plot/CSV attachments); the
full Edison output is contained in the three files above.

---

## TL;DR

**Keep PLA as the baseline strut material; treat PETG as a justified Phase-2
upgrade that is gated on experimentally measuring the PETG–TPU interface;
defer CF-reinforced and continuous-fiber options.** "HF-reinforced" most
likely means hemp-fiber-reinforced PLA, which is *not* a competitive
candidate for an energy-absorbing strut.

| Rank | Material | When to choose it |
|------|----------|-------------------|
| **1** | **PLA** | Default. Only rigid–TPU pairing with quantitative interface data (6.5–7.4 MPa tensile, up to 24 MPa shear with mechanical interlocking). Highest stiffness among neat commodity FDM polymers (E ≈ 2.2–2.5 GPa, σ_c ≈ 82 MPa) → ~2× Euler-buckling resistance vs. PETG. Best fatigue, best UV (PLA loses ~5–9% UTS, PETG loses 36–38% under UV-C/UV-B). Easiest H2D print, lowest cost. |
| **2** | **PETG** | If thermal margin is a hard requirement (HDT 74 °C vs. PLA's 53 °C, e.g., in-car / hot environments), or if greater ductility is needed. **Conditional on validating the PETG–TPU interface in our actual joint geometry — there is no peer-reviewed PETG–TPU bond-strength number in the literature.** |
| **3** | **CF-PETG** | Only as a Phase-2 upgrade if strut buckling becomes the dominant failure mode after baseline characterization. Stiffness ~3× neat PETG (4.8–6.1 GPa) and ~22% higher energy density to densification, but requires a hardened nozzle, likely degrades the (already weak) TPU interface, costs ~2×, and has zero peer-reviewed CF/TPU bond data. |
| 4 | CF-PLA | Big stiffness gain (E ≈ 12.5–14.7 GPa) but reduces ductility and almost certainly degrades the TPU interface; PLA's brittleness is amplified. |
| 5 | ABS | Best impact toughness of the commodity polymers, but warp/enclosure issues on H2D and weak TPU-interface evidence. |
| 6 | Continuous CF/Nylon (Markforged) | Performance leader (E up to 51 GPa) but **not compatible with the Bambu H2D** and cannot co-print TPU tendons in the same build. Out of scope for an MRG / undergraduate-mentored project. |
| — | "HF-reinforced" (hemp fiber PLA) | The only meaningful HF interpretation in the FDM literature. Raises flexural modulus modestly but **drops impact strength (~69.8 → 42.9 J/m) and increases porosity (5.8 → 17.9%)** — the opposite of what an energy absorber needs. Hollow-fiber and high-flow are not established acronyms in this context; halloysite-NT is a TPU-side filler, not a strut material. **Not recommended.** |

## Why the PETG–TPU interface is the decisive constraint

Multi-material FDM struts/tendons live or die at the interface. The Edison
synthesis surfaced exactly **one** rigid/flexible pair with published
quantitative bond data:

| Pair | Test | Strength | Source |
|------|------|----------|--------|
| PLA–TPU | butt-interface tensile | 6.5 ± 0.4 MPa | Lopes 2018 (doi:10.1016/j.addma.2018.06.027) |
| PLA–TPU | alternate-deposition tensile | 7.42 ± 0.33 MPa | Zhang 2026 (doi:10.1007/s00170-026-17902-3) |
| PLA–TPU | shear (mech. interlock, θ=22.5°, h=4 mm) | 24.47 ± 1.99 MPa | Zhang 2026 |
| PLA–TPU laminate | UTS, 67/33 PLA/TPU/PLA | 33.5 MPa | Ruwais 2025 |
| **PETG–TPU** | **anything** | **no peer-reviewed value** | — |
| **CF-X / TPU** | **anything** | **no peer-reviewed value** | — |

This is why PETG is conditional, not a drop-in replacement: switching from
PLA to PETG *adds* thermal margin and ductility but throws away the only
material pair we can cite in the proposal.

## Novelty (Recommendation 5 from Edison)

Edison found **no peer-reviewed paper that uses a PETG-strut + TPU-tendon
(or any fiber-reinforced strut + TPU-tendon) tensegrity / tensegrity-inspired
energy absorber.** Closest prior art is Pajunen et al. 2019 (single-material
SLS PA2200) and Santos 2023 (FDM tensegrity dissipator, materials not
specified). A multi-material PLA-or-PETG-strut + TPU-tendon co-printed
tensegrity is a publishable contribution as proposed.

## Action items for this proposal

1. **Keep PLA as the baseline in `proposal.tex` / `idetc-abstract.tex`** —
   it is the only material with citable PLA–TPU interface numbers, and the
   proposal's claim of robust mechanical interlocking is now backed by
   Lopes 2018, Zhang 2026, and Ruwais 2025.
2. **Add a single sentence in the proposal flagging PETG as a Phase-2
   alternative** with thermal/ductility upside and an interface-validation
   gate. (Optional, low-priority for the MRG submission.)
3. **Add to `references.bib`**: at minimum
   `lopes2018multimaterial`, `zhang2026rigidflexible`, `ruwais2025layered`,
   `martins2024plapetg`, `pajunen2019tensegrity`, `popa2022izodplapetg`,
   `amza2021uvaging` — these are now the canonical citations for
   PLA-vs-PETG strut choice and PLA–TPU interface strength.
4. **Open a follow-up issue** to experimentally measure PETG–TPU
   butt-tensile and lap-shear in our actual H2D co-print geometry; this
   would close the only literature gap that blocks a PETG upgrade.

## Caveats / what Edison did not answer

- No PETG–TPU or CF/TPU peer-reviewed bond numbers exist (as of the search
  date), so any quantitative ranking that includes those pairs is currently
  un-cite-able.
- "HF-reinforced" was disambiguated to hemp-fiber as the dominant academic
  interpretation; if a project insider meant something else (e.g., a
  vendor-specific blend), re-query with the exact product name.
- All FDM property numbers above are print-direction-dependent and assume
  ≥0.2 mm layers and stock 0.4 mm nozzle; final part properties on the H2D
  should be verified on coupons before locking in the strut material.
