# Davami et al. (2025) — Dynamic Analysis of Additively Manufactured Tensegrity Structures

**Citation.** Davami, K., Rowe, R., Gulledge, B., Tavangarian, F., Beck, S., Park, J.,
Beheshti, A., Palazotto, A. (2025). *Dynamic analysis of additively manufactured
tensegrity structures.* International Journal of Impact Engineering **198**, 105208.
DOI: [10.1016/j.ijimpeng.2024.105208](https://doi.org/10.1016/j.ijimpeng.2024.105208).
BibTeX key: `davami2025dynamic` (see `references.bib`). PDF archived at
[`literature/davami2025-dynamic-am-tensegrity.pdf`](davami2025-dynamic-am-tensegrity.pdf).

Thanks to Jeff Hill for sharing this article (issue
[#XX](../../../issues)).

## 1. Summary of the prior work

Davami et al. design, fabricate, and test a *bistable, tensegrity-like* compliant
mechanism inspired by the classical triangular tensegrity prism (T3). The work
sits in the well-established Rimoli / Daraio / Fraternali "tensegrity-inspired
3D-printed lattice" lineage (Pajunen 2019, Rimoli 2018, Amendola 2014, …) and
adds *high-strain-rate* characterization that prior small-scale, low-rate
studies had not delivered.

| Aspect | Davami et al. 2025 |
| --- | --- |
| **Unit cell** | Double-T3 prism (two stacked triangular prisms), twist angle φ = 19°, designed relative density ρ = 20 %. |
| **Lattice** | 20 double-T3 cells (10 top + 10 bottom layer); single unit and lattice both tested. |
| **Tensegrity class** | "Tensegrity-like" Class-1 compliant mechanism — **no actual flexible cables**; "bars" and "cables" are all rigid printed members of equal diameter, and bistable snap arises from geometry, not from prestressed tendons. |
| **Material** | **Single material**: Formlabs Tough 2000 photopolymer resin (E ≈ 295 MPa, σ\_UTS ≈ 42 MPa, ε\_y ≈ 19.5 %). |
| **Process** | SLA / **vat photopolymerization** on Formlabs Form 2 (50 µm layers, vertical orientation, IPA wash, 60 min 60 °C UV post-cure). |
| **Quasi-static** | MARK-10 ESM 303, 13 mm/min → ε̇ ≈ 4.5 × 10⁻³ s⁻¹ (unit) / 7.6 × 10⁻³ s⁻¹ (lattice), 20 Hz sampling. |
| **Dynamic** | REL Inc. **direct-impact SHPB** (304.8 mm × 38.1 mm Al bar, 78.9 kPa → 6.5 m/s), ε̇ ≈ 134 s⁻¹ (lattice) / 226 s⁻¹ (unit). Vision Research Phantom V611 at 55 000 fps for displacement tracking. |
| **Key observation** | Reliable, repeatable bistable *twisting + snap-through* mechanism activates in **both** regimes without any self-stress; structure ultimately collapses by snap-buckling. |
| **Optimization** | None: φ = 19° is chosen heuristically from Intrigila et al.'s 15°–22° bistable range "as it gave the most uniform response"; the only swept parameter is bar diameter *d* (set so ρ = 20 % to match comparable lattice data). |
| **Material-set search** | None — single resin only. |

The headline contribution is **demonstrating bistable snap-through in a
3D-printed tensegrity-like cell across five orders of magnitude in strain rate
(10⁻³ → 10² s⁻¹)** using SHPB-class instrumentation — extending earlier
small-scale, quasi-static tensegrity-inspired lattice work (Pajunen 2019,
Beauer 2022, Fraternali 2015) into a regime relevant to impact/ballistic
applications.

## 2. Why this is a high-relevance article for our MRG / IDETC project

It is the **closest published analog** to our proposed work along *several*
dimensions simultaneously: AM tensegrity, prism-based unit cell, lattice
tiling, impact loading, and energy-absorption framing. Anyone reviewing our
proposal (or the eventual journal manuscript) will reach for Davami et al.
first when asking "how is this different from what's already been done?"
We therefore need an explicit, defensible differentiation.

## 3. Differentiation vs. our proposed work

Our project (see `proposal.tex`, `idetc-abstract.tex`, README) develops a
**multifidelity Bayesian-optimization framework for multi-material FDM-printed
tensegrity lattices** with PLA struts + TPU 85A tendons, validated by
quasi-static compression and drop-tower experiments. Key points of departure
from Davami et al.:

### 3.1 Single-material rigid resin vs. genuinely multi-material rigid + elastomer

Davami's "cables" are rigid printed bars of the same diameter as the struts,
and the bistable response is a *purely geometric* compliant-mechanism effect.
Our design intentionally co-prints two materials with two-orders-of-magnitude
modulus contrast — **PLA struts (E ≈ 3.5 GPa)** and **TPU 85A tendons
(E ≈ 12 MPa secant)** — so that the tension elements are *actually flexible*
and recover under release, recapturing the constitutive ingredients of the
classical Skelton/Sultan tensegrity definition that SLA photopolymer
tensegrity-likes deliberately abandon. This is supported by recent work on
PLA/TPU multi-material printing (Ye 2023, Khatri & Egan 2024) cited in our
proposal. **TPU's rate-dependent viscoelastic damping** becomes an asset for
impact energy absorption rather than a complication.

### 3.2 SLA vat photopolymerization vs. multi-material FDM

Davami uses single-vat SLA. We use multi-material **FDM/FFF** (dual-extruder
on the Bambu H2D class of platforms), the only widely accessible AM process
today that can monolithically co-deposit a stiff thermoplastic and a soft
TPU in the same build. This unlocks rigid-strut + flexible-tendon designs
that no vat process can produce as a single part.

### 3.3 Heuristic geometric choice vs. multifidelity Bayesian optimization

Davami sweep essentially one parameter (bar diameter for ρ = 20 %) and fix
φ = 19° by hand from a bistable-friendly range reported in earlier work.
Our project treats the design space (strut diameter, strut length, tendon
cross-section, connectivity topology, unit-cell tiling, prestress, *and*
per-element material assignment) as a high-dimensional black-box and applies
**multifidelity Bayesian optimization** in the Mo et al. 2023 / Ament et al.
2023 line. Cheap fidelity = reduced-order tensegrity-network / FE
simulation; expensive fidelity = printed-and-tested specimens. The
deliverable is a *closed-loop pipeline*, not a single tested geometry.

### 3.4 Class-1 prism focus vs. broader connectivity-topology search

Davami restrict to one Class-1 double-T3 prism topology (and Intrigila et al.
2022, *Addit. Manuf.* 57:102946, already demonstrated the *quasi-static*
bistable response of essentially the same SLA Tough 2000 double-T3 unit —
so Davami's contribution over Intrigila is principally the high-rate SHPB
extension, not the geometry itself). Our framework instead includes
connectivity topology and unit-cell tiling as discrete design variables,
leveraging the much wider tensegrity-design landscape catalogued in our
earlier Edison literature surveys (Snelson X-module, Pajunen 2019
truncated-octa cell, Oster 2021 reentrant auxetic, Rhode-Barbarigos
pentagonal ring, Pugh diamond/zig-zag, tensegrity torus, Hanaor
double-layer grid; see `edison-trajectories/2026-05-12-tensegrity-design-gaps-…`
on related branches).

### 3.5 SHPB direct-impact vs. drop-tower + compression for *energy-absorbed-per-mass*

Davami's primary loading is **direct-impact SHPB** at ε̇ ≈ 134–226 s⁻¹,
which excels at well-controlled constitutive characterization but, per their
own discussion, is less representative of crash/drop scenarios. Our
testbeds are **(i) quasi-static compaction tests** and **(ii) drop-tower /
egg-drop survival benchmarks** (see related sibling issues on egg-drop), with
the optimization *objective* being specific energy absorption (J g⁻¹) under
fixed payload and bounding-volume constraints. The two work programs are
therefore **complementary on the loading axis** rather than redundant.

### 3.6 Engineering-only deliverable vs. mentored-research + open-source pipeline

Davami's contribution is an article + characterized specimens. Our MRG
deliverable is additionally an **undergraduate mentoring program** and an
**open-source data/code/CAD release** (simulation harness, BO loop,
print recipes, test data). This is invisible in a head-to-head technical
comparison but is the headline criterion for the BYU MRG and should be
acknowledged when differentiating *funded outputs*.

### Summary differentiation table

| Axis | Davami et al. 2025 | Our proposed work |
| --- | --- | --- |
| Materials | **Single** (Tough 2000 resin) | **Multi-material** (PLA + TPU 85A) |
| AM process | SLA / vat photopolymerization | Multi-material FDM (H2D) |
| Tendons | Rigid bars (compliant mechanism) | Actual flexible TPU tendons |
| Tensegrity class | "tensegrity-like" Class-1 | True multi-material tensegrity (Class-1 / Class-2 both in scope) |
| Topology search | Fixed double-T3 prism | Broad design space (≥ 8 candidate families) |
| Geometry tuning | Hand-picked φ = 19°, ρ = 20 % | Multifidelity Bayesian optimization |
| Loading | SHPB direct-impact + QS compression | Drop-tower + QS compression (impact-survival) |
| FoM | Snap behavior, force-disp curves | Specific energy absorption (J g⁻¹), survival/reuse |
| Deliverable | Article | Mentored UG research + open-source closed-loop pipeline |

## 4. Concrete take-aways to fold into proposal / abstract / manuscript

- **Background paragraph (proposal §Background).** Add Davami et al. 2025
  alongside Pajunen 2019 as the strongest published precedent for *dynamic*
  AM tensegrity, and explicitly note the single-material, SLA, hand-tuned
  nature of their design study.
- **Gap statement.** Reframe our novelty as: *(i)* genuine multi-material
  rigid-strut/flexible-tendon construction (vs. single-material compliant
  mechanism), *(ii)* multifidelity BO over a wider topology + material
  assignment space (vs. one prism, one ρ, one φ), and *(iii)* drop-tower /
  energy-absorption-per-mass framing (vs. SHPB constitutive
  characterization).
- **Mock-review robustness.** Pre-empt the obvious reviewer question
  "How is this different from Davami et al. 2025?" by citing this analysis
  doc in the response-to-reviewer template.

## 5. Edison high-effort literature follow-up

Per the issue, an Edison `LITERATURE_HIGH` query was submitted asking for
articles *similar to* Davami et al. 2025 across themes (a) high-strain-rate
AM tensegrity, (b) bistable snap-through tensegrity prisms, (c)
multi-material AM tensegrity / rigid + TPU, (d) optimization of tensegrity
for impact, (e) wave-propagation reviews. Submission script:
[`scripts/edison/submit_davami2025_followup.py`](../scripts/edison/submit_davami2025_followup.py);
fetched artifacts under
[`edison-trajectories/davami2025-followup/`](../edison-trajectories/davami2025-followup/).

- **Task ID:** `0944224d-2b57-47a9-a525-0a7da79b7a86` (status: **success**,
  formatted answer ≈ 36 KB, 16 ranked articles).
- **Artifacts:**
  [`davami2025-followup-0944224d-…md`](../edison-trajectories/davami2025-followup/davami2025-followup-0944224d-2b57-47a9-a525-0a7da79b7a86.md),
  [`…json`](../edison-trajectories/davami2025-followup/davami2025-followup-0944224d-2b57-47a9-a525-0a7da79b7a86.json).

### 5.1 Edison-ranked closest analogs (highlights)

The full ranked table (16 articles, themes a–e) is in the artifact; the most
useful additions for our differentiation argument:

| Rank | Article | Why it sharpens our positioning |
| --- | --- | --- |
| 1 | **Pajunen et al. 2019** *Mater. Des.* 182:107966 — SLS, drop-weight impact on monolithic tensegrity-inspired lattice | Cleanest *single-material AM + dynamic* baseline; together with Davami it forms the "monolithic AM tensegrity under impact" precedent we differentiate against. |
| 2 | **Amendola et al. 2018** *Front. Mater.* 5:22 — EBM Ti6Al4V struts + Spectra cables, drop impact | Confirms that **real flexible cables** materially change the dynamic response — but requires manual post-tensioning. Our PLA + TPU FDM approach is the *automated, monolithic-build* analog. |
| 4 | **Intrigila et al. 2022** *Addit. Manuf.* 57:102946 — SLA Tough 2000, bistable double-T3, **quasi-static only** | Closest possible analog: same resin, same unit cell, same φ-range as Davami, but no dynamic regime and no flexible tendons. Confirms Davami's *only* novel axis vs. Intrigila is the high-rate SHPB extension. |
| 5 | **Bauer et al. 2021** *Adv. Mater.* 33:2005647 — TPP monolithic, structural optimization of tension/compression members | Direct precedent that optimizing member-type assignment amplifies energy absorption — supports our multifidelity-BO framing. |
| 7 | **Yavas et al. 2022** *Mater. Des.* 217:110613 — **FFF PLA + TPU** coaxial-strut multi-material lattice | Validates the exact material system (PLA + TPU on FDM) for energy absorption, *but in a conventional lattice, not a tensegrity*. Our project = Yavas's material system × Davami's tensegrity architecture × BO. |
| 8 | **Amendola et al. 2015** *Compos. Struct.* 131:66 — bi-material EBM + post-tensioned Spectra | Shows the manufacturing burden of manual post-tensioning that monolithic dual-extrusion FDM eliminates. |
| 9 | **Zhang et al. 2021** *Compos. Struct.* 267:113903 — numerical optimization of truncated-octahedral tensegrity for E.A. | Numerical-only precedent for tensegrity E.A. optimization; we close the loop with experiments and a multifidelity surrogate. |
| 10–11 | **Goyal et al. 2019, 2020** — analytical mass-efficient tensegrity E.A. | Provides analytical low-fidelity baselines suitable for the *cheap fidelity* of our multifidelity stack. |
| 12 | **Pajunen et al. 2021** *Extreme Mech. Lett.* 44:101236 — prestrain-tunable bandgaps in monolithic tensegrity-inspired lattices | Hints that TPU-tendon prestress could become a *dynamic* design variable for our BO — beyond impact E.A. alone. |

The clearest "white space" the Edison survey confirms for us:
**no published article combines (i) true rigid + flexible-tendon tensegrity
architecture, (ii) monolithic multi-material FDM (PLA + TPU), (iii) impact /
high-strain-rate energy-absorption testing, and (iv) data-efficient
(multifidelity Bayesian) optimization of geometry, material assignment, and
prestress.** Yavas covers (ii); Amendola covers (i) but with manual
post-tensioning + EBM; Davami covers (iii) with monolithic SLA; Zhang /
Goyal cover (iv) numerically only. The union is open.
