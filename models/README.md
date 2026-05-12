# Tensegrity reference designs / models

This directory collects **3D models for canonical tensegrity structures**
that the MRG project will use as starting points for CAD review,
slicing, FEM import, Bayesian-optimization parameterization, and
fabrication validation.

Closes [#21](https://github.com/vertical-cloud-lab/byu-mentored-research-tensegrity/issues/21).

![Preview of generated tensegrity models](../figures/tensegrity_models_preview.png)

The 7 additional design families from the Edison literature survey
(cable-domes, biotensegrity, robots, deployable masts, patents, bistable,
cuboctahedron metamaterials) are rendered in
[`figures/tensegrity_models_extended_preview.png`](../figures/tensegrity_models_extended_preview.png):

![Extended preview of additional tensegrity design families](../figures/tensegrity_models_extended_preview.png)

A second follow-up Edison literature survey (task
`6226a551-b46a-49b4-936a-bca600cd8d30`, May 2026; see
[`edison-trajectories/2026-05-12-tensegrity-design-gaps-6226a551-b46a-49b4-936a-bca600cd8d30.md`](../edison-trajectories/2026-05-12-tensegrity-design-gaps-6226a551-b46a-49b4-936a-bca600cd8d30.md))
identified 18 additional design families missing from the original
survey.  The 4 most reconstructable-from-first-principles members of
that gap list are committed here as parametric STLs (Snelson planar
X-module, Pugh diamond pattern, Pugh zig-zag pattern, Rhode-Barbarigos
pentagonal ring); the remaining families require source-paper
figures/tables/supplementary materials and are listed under
"Caveats and clarifications needed" below.

![Gap-followup preview](../figures/tensegrity_models_gapfollowup_preview.png)

## Contents

| File | Structure | Nodes | Struts | Cables | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| [`stl/3bar_prism.stl`](stl/3bar_prism.stl)   | 3-bar tensegrity prism (T3, "Snelson simplex") | 6 | 3 | 9 | Smallest non-trivial 3D tensegrity. Twist `θ = π/2 − π/3 = 30°`. |
| [`stl/4bar_prism.stl`](stl/4bar_prism.stl)   | 4-bar tensegrity prism (T4)                    | 8 | 4 | 12 | Twist `θ = π/2 − π/4 = 45°`. |
| [`stl/6bar_prism.stl`](stl/6bar_prism.stl)   | 6-bar tensegrity prism (T6)                    | 12 | 6 | 18 | Twist `θ = π/2 − π/6 = 60°`. Building block for stacked masts. |
| [`stl/icosahedron.stl`](stl/icosahedron.stl) | 6-strut tensegrity icosahedron (Jessen's orthogonal icosahedron / "expanded octahedron") | 12 | 6 | 24 | Strut/cable length ratio `√(8/3) ≈ 1.633`. Used in NASA SUPERball lineage and most "tensegrity-ball" designs. |
| [`stl/stacked_t3_column.stl`](stl/stacked_t3_column.stl) | Stacked 3-bay T3 column (Snelson "Needle Tower" / mast topology) | 12 | 9 | 21 | 3 stacked T3 bays with alternating chirality (Snelson 1968–69; Tibert & Pellegrino deployable masts). |
| [`stl/truncated_octahedron.stl`](stl/truncated_octahedron.stl) | Truncated-octahedron tensegrity (Rimoli/Pajunen unit cell) | 24 | 12 | 36 | Space-tileable energy-absorbing metamaterial cell. Rank-#1 BYU recommendation for impact absorption (Pajunen et al. 2019; Bauer et al. 2021). |
| [`stl/geiger_cable_dome.stl`](stl/geiger_cable_dome.stl) | Geiger radial cable-dome (Seoul Olympic Hall topology) | 73 | 36 | 132 | 3 concentric rings × 12 radial ribs + apex hub. Cable-dome (not pure class-1); per Fu (2005), Geiger US Pat. 4,736,553. |
| [`stl/biotensegrity_spine.stl`](stl/biotensegrity_spine.stl) | Biotensegrity spine (4 stacked Jessen-icosahedron vertebrae) | 48 | 24 | 108 | Levin/Flemons stacked-icosahedron spinal-column model; basis for Berkeley ULTRA-Spine. |
| [`stl/superball_with_payload.stl`](stl/superball_with_payload.stl) | NASA SUPERball with inner payload icosahedron | 24 | 12 | 60 | 6-strut outer + inner mini-icosahedron + 12 payload-suspension cables (SunSpiral et al. 2015). |
| [`stl/tibert_pellegrino_mast.stl`](stl/tibert_pellegrino_mast.stl) | Tibert/Pellegrino deployable mast (6-bay) | 21 | 18 | 39 | Slender alternating-chirality stacked-prism mast (Tibert & Pellegrino, *Int. J. Space Struct.* 2003). |
| [`stl/patent_us6441801_antenna.stl`](stl/patent_us6441801_antenna.stl) | Knight et al. tensegrity antenna (US 6,441,801 B1) | 12 | 6 | 18 | Hexagonal upper platform / hexagonal lower base + 6 strut-tie pairs. Knight, Duffy, Crane US Pat. 6,441,801 B1 (2002). |
| [`stl/bistable_double_prism.stl`](stl/bistable_double_prism.stl) | Bistable double-prism unit cell | 9 | 6 | 15 | Two T3 prisms joined at a shared compliant hinge ring (Intrigila et al., *Add. Manuf.* 2022). |
| [`stl/cuboctahedron_tessellation.stl`](stl/cuboctahedron_tessellation.stl) | Cuboctahedron tessellation cell (simplified) | 13 | 6 | 36 | Single-block representation of Liu et al.'s 13-strut/96-cable bandgap-tunable tessellation (J. Mech. Phys. Solids 2019). |
| [`stl/snelson_x_module.stl`](stl/snelson_x_module.stl) | Snelson planar X-module | 4 | 2 | 4 | Smallest planar tensegrity, seed of Snelson's X-piece weave / X-column compositions (Snelson US Pat. 3,169,611, 1965). Struts are z-offset so the two diagonals don't touch. |
| [`stl/pugh_diamond_column.stl`](stl/pugh_diamond_column.stl) | Pugh "diamond" stacked column (3-bay T3) | 12 | 9 | 30 | Two saddle cables per strut → diamond-shaped side panels (Pugh 1976, ch. 3). |
| [`stl/pugh_zigzag_column.stl`](stl/pugh_zigzag_column.stl) | Pugh "zig-zag" stacked column (3-bay T3) | 12 | 9 | 21 | Single saddle per strut with a "skip-1" jump → Z-fold side panels (Pugh 1976, ch. 3). |
| [`stl/pentagonal_tensegrity_ring.stl`](stl/pentagonal_tensegrity_ring.stl) | Pentagonal tensegrity-ring module (Rhode-Barbarigos 2010, simplified) | 10 | 5 | 15 | Closed-ring "hollow-rope" module; basis for EPFL deployable tensegrity footbridge (Rhode-Barbarigos et al., Eng. Struct. 2010). |

All STL files are **binary STL**, units in millimetres, with struts
rendered as 5 mm-diameter cylinders (PLA / PETG) and cables rendered
as **2.4 mm-diameter** cylinders (TPU — these are not literal strings;
the eventual fabricated cables are printed in TPU and need a
realistic finite cross-section, matching the cable diameter used in
[`cad/t3-prism/`](../cad/t3-prism/)). Default sizes are chosen to fit
within a typical 200 mm-cube print bed.

## Regenerating the STL files

The geometry is authored from first principles in
[`generate_stl.py`](generate_stl.py) (Python ≥ 3.7, standard library
only — no `numpy`, no `numpy-stl`, no licence encumbrance):

```bash
python models/generate_stl.py
# optional flags:
#   --out-dir models/stl          # output directory
#   --strut-radius 2.5            # strut cylinder radius (mm)
#   --cable-radius 1.2            # cable cylinder radius (mm; ~TPU)
#   --segments 24                 # cylinder facet count
```

The script also exposes `n_bar_prism(n, radius, height)`,
`six_strut_icosahedron(scale)`, `stacked_prism(n, bays, radius,
bay_height)`, `truncated_octahedron_tensegrity(scale)`,
`geiger_cable_dome(n_radial, rings, strut_lengths, apex_height)`,
`biotensegrity_spine(vertebrae, scale, spacing)`,
`superball_with_payload(scale, payload_scale)`,
`tibert_pellegrino_mast(n, bays, radius, bay_height)`,
`patent_us6441801_antenna(n_sides, bottom_radius, top_radius, height)`,
`bistable_double_prism(radius, bay_height)`, and
`cuboctahedron_tessellation(scale)` for direct use as design seeds in
the Bayesian optimization loop (`(nodes, struts, cables)` tuples that
map directly onto the BO parameterization in the proposal).

## Caveats and clarifications needed

The 7 extended-preview families are emitted as **first-principles
parametric STLs reconstructed from the geometric specifications stated
in the cited papers/patents**.  They are intended as topology-correct
visual / FEM-import seeds; for fully validated geometry — especially
prestress states and equilibrium-shape coordinates — the following
source PDFs would be needed (and a domain expert may need to confirm):

- **Geiger cable-dome**: full prestress-state coordinates require
  Geiger's US Pat. 4,736,553 (1988) or Fu (2005).  Best contact:
  Feng Fu (City, Univ. of London) for cable-dome design.
- **Biotensegrity spine / ULTRA-Spine**: detailed inter-vertebral
  cable connectivity and prestress states require Sabelhaus et al.
  IEEE RA-L 5(3):3982-3989 (2020) or the Berkeley ULTRA-Spine repo
  (<https://github.com/BerkeleyExpertSystemTechnologiesLab/ultra-spine-simulations>).
  Best contact: Andrew Sabelhaus (Boston Univ.).
- **NASA SUPERball v2 with payload**: the inner spring-cable count and
  payload-cable routing was reported as "12 inner spring-cable
  assemblies" but the per-node connectivity needs the SunSpiral 2015
  NASA tech report or the NTRT JSON
  (<https://github.com/NASA-Tensegrity-Robotics-Toolkit/NTRTsim>).
- **Tibert/Pellegrino mast**: only topology is reproduced here; the
  full equilibrium-manifold deployment trajectory needs Sultan &
  Skelton (2003) or Bel Hadj Ali et al. (2010).
- **US 6,441,801 B1 (Knight et al. antenna)**: Figs. 2–4 of the
  patent give exact strut/tie ratios and the screw-motion deployment
  schedule; not all variables are determined by topology alone.
  Patent PDF: <https://patents.google.com/patent/US6441801B1>.
- **Bistable double-prism**: the snapping-mechanism hinge
  cross-sections and triggering-force calibration are reported in
  Intrigila et al. *Add. Manuf.* 57:102946 (2022), Figs. 6–9.
- **Cuboctahedron tessellation (Liu et al.)**: the full 13-strut /
  96-cable / 12-prestress-state form-finding requires the Liu et al.
  *J. Mech. Phys. Solids* 131:147–166 (2019) paper and (ideally) the
  tessellation force-density matrix; the STL committed here is a
  **simplified single-block representation** of just the cuboctahedron
  + central tension hub.

If full validated geometries (with form-found coordinates and prestress
states) are needed for any of the above, please flag and either
(a) point at the relevant supplementary material, or
(b) name a contact whose published code we can integrate.

### Source materials needed for the remaining gap-followup families

The Edison gap-followup survey (task `6226a551`) recommended 18 new
families.  Four were buildable from first-principles geometric
specifications alone and are committed in
`figures/tensegrity_models_gapfollowup_preview.png`; the remaining
high-priority ones require the following specific figures / tables /
supplementary materials before they can be emitted as faithful STLs
(direct links provided for convenience):

- **Oster 2021 reentrant 3-periodic auxetic tensegrity** — needs the
  vertex coordinates and connectivity tables from the supplementary
  material of Oster, M. *et al.* "Reentrant 3-periodic tensegrity
  metamaterials with auxetic response", paper preferred figures:
  **Fig. 1 (unit-cell schematic), Fig. 2 (vertex-coordinate table),
  Fig. S1-S4 (SI: full strut/cable connectivity)**.  Likely venue:
  *Adv. Funct. Mater.* / *Sci. Adv.*; cited in our Edison survey as
  Oster 2021.  Verified DOIs in the area:
  doi:[10.1126/sciadv.abj6737](https://doi.org/10.1126/sciadv.abj6737)
  (Fraternali et al., *Science Advances* 2021, "Reentrant tensegrity:
  A three-periodic, chiral, tensegrity structure that is auxetic").
  Please confirm which
  Oster paper is intended and send the PDF + SI.
- **Pajunen 2019 impact-absorbing tensegrity cell** — needs the full
  prestress-state ratios from Pajunen, K., Johanns, P., Pal, R. K.,
  Rimoli, J. J., Daraio, C., "Design and impact response of
  3D-printable tensegrity-inspired structures", *Mater. Design*
  182:107966, 2019.  Required: **Fig. 2 (unit-cell geometry table),
  Fig. 4 (strut/cable diameter ratios), Table 1 (prestress states)**.
  PDF: doi:[10.1016/j.matdes.2019.107966](https://doi.org/10.1016/j.matdes.2019.107966)
  (also on arXiv as 1812.10468).
- **Rhode-Barbarigos pentagonal ring (full deployable variant)** —
  the committed STL is a 1-layer 10-node simplification.  The full
  15-node / 30-cable two-layer deployable hollow-rope module needs
  Rhode-Barbarigos, L., Bel Hadj Ali, N., Motro, R., Smith, I. F. C.,
  "Designing tensegrity modules for pedestrian bridges", *Eng.
  Struct.* 32(4):1158-1167, 2010 — **Fig. 2 (module geometry),
  Fig. 3 (node-numbering scheme), Table 1 (element lengths)**.
  doi:[10.1016/j.engstruct.2009.12.042](https://doi.org/10.1016/j.engstruct.2009.12.042).
  Companion paper: Rhode-Barbarigos *et al.*, *J. Struct. Eng.* 138(5):
  539-548, 2012, doi:[10.1061/(ASCE)ST.1943-541X.0000491](https://doi.org/10.1061/(ASCE)ST.1943-541X.0000491)
  (deployment trajectory).
- **Hanaor double-layer tensegrity grid** — needs Hanaor, A.,
  "Double-layer tensegrity grids as deployable structures", *Int. J.
  Space Struct.* 8(1-2):135-143, 1993 — **Fig. 3 (square-base unit),
  Fig. 7 (grid-assembly node connectivity)**.
  doi:[10.1177/0266351193008001-214](https://doi.org/10.1177/0266351193008001-214).
  Also: Hanaor, Kanchanasaratool 1991 *J. Struct. Eng.* (Part I/II),
  doi:[10.1061/(ASCE)0733-9445(1991)117:6(1660)](https://doi.org/10.1061/(ASCE)0733-9445(1991)117:6(1660)),
  doi:[10.1061/(ASCE)0733-9445(1991)117:6(1675)](https://doi.org/10.1061/(ASCE)0733-9445(1991)117:6(1675)).
- **Levy/Suspen-dome** (Tianjin-arena lineage) — needs Levy, M. P.,
  "Floating fabric over Georgia Dome", *Civ. Eng. ASCE* 61(11):34-37,
  1991 (architectural drawing) and Kang, W. *et al.*, "Static and
  seismic performance of suspen-domes", *Eng. Struct.* 25(13):
  1685-1695, 2003 — **Fig. 2 (radial-vs-spatial cable layout),
  Table 1 (cable-prestress vector)**.
  doi:[10.1016/S0141-0296(03)00149-4](https://doi.org/10.1016/S0141-0296(03)00149-4).
- **Tensegrity torus** — needs Kim, K., Agogino, A. K., Toghyan, A.,
  Moon, D., Taneja, L., Agogino, A. M., "Robust learning of tensegrity
  robot control for locomotion through form-finding", IROS 2015 —
  **Fig. 2 (torus topology), Fig. 4 (node coords)**.
  doi:[10.1109/IROS.2015.7354168](https://doi.org/10.1109/IROS.2015.7354168).
- **DNA-origami tensegrity** — Liedl, T., Hogberg, B., Tytell, J.,
  Ingber, D. E., Shih, W. M., "Self-assembly of three-dimensional
  prestressed tensegrity structures from DNA", *Nat. Nanotechnol.*
  5:520-524, 2010 — **Fig. 1c (strut/tendon coordinates),
  Fig. S5-S7 (SI: scaffold routing)**.  Nano-scale; we'd only use
  for topology, not for printing.
  doi:[10.1038/nnano.2010.107](https://doi.org/10.1038/nnano.2010.107).
- **US20240351370A1 six-bar wheel** (Skelton patent, 2024) —
  the published US patent application PDF gives complete strut/cable
  connectivity in Fig. 3 + Fig. 5: <https://patents.google.com/patent/US20240351370A1>.
  No paywall; can be added in next pass without a request.

If you can grab any of those PDFs / SI ZIPs (or share via the repo
under `papers/`), the corresponding STL is then a 1-2 hour update —
flag which subset is highest priority.

## Literature survey

A high-effort Edison Scientific literature survey of canonical and
non-canonical tensegrity designs (T-bar/D-bar class-k cells, polyhedral
tensegrities, Geiger/Levy cable-domes, Snelson Needle Tower, NASA
SUPERball/ULTRA-Spine, Rimoli/Pajunen truncated-octahedron metamaterial,
Liu et al. cuboctahedron tessellation, bistable double-prism, Levin/
Ingber biotensegrity, deployable masts, and topology-generation methods)
is committed at
[`edison-trajectories/2026-05-09-tensegrity-designs-fad054b3.md`](../edison-trajectories/2026-05-09-tensegrity-designs-fad054b3.md)
along with the structured references file
[`...-references.md`](../edison-trajectories/2026-05-09-tensegrity-designs-fad054b3-references.md)
and the full task JSON. The 3 new designs added in this update
(T6 prism, stacked T3 column, truncated-octahedron cell) are the most
promising buildable additions identified in that survey for the
PETG-strut + TPU-tendon BO workflow.

## Geometric definitions

### n-bar prism (Tn)

For a regular `n`-prism with bottom-polygon radius `r` and height `h`,
the relative twist between top and bottom polygons that yields a
**self-equilibrated (stable)** tensegrity is

```
θ = π/2 − π/n
```

(Connelly & Whiteley, 1996; Skelton & de Oliveira, 2009, ch. 2). The
cable network consists of the bottom polygon (n cables), the top
polygon (n cables), and `n` saddle cables joining bottom node `i` to
top node `(i+1) mod n`. Struts join bottom node `i` to top node `i`.

### 6-strut tensegrity icosahedron

The equilibrium shape of the canonical "tensegrity ball" is **Jessen's
orthogonal icosahedron** (Jessen, 1967). Its 12 vertices are the
cyclic permutations of `(0, ±1, ±2)`. The 6 struts (length 4) are
the long edges of the three mutually orthogonal 2 × 4 rectangles. The
24 cables (length √6) are the inter-rectangle vertex pairs. This is
the topology used by the NASA SUPERball ([NTRTsim](https://github.com/NASA-Tensegrity-Robotics-Toolkit/NTRTsim))
and most spherical tensegrity rovers and impact-absorbing payloads.

## Additional external sources

The following permissively-licensed external resources are recommended
for deeper / more elaborate reference designs:

- **NASA Tensegrity Robotics Toolkit (NTRTsim)** — Apache 2.0.
  Includes parameterized simulation models (no STL, but
  Bullet-physics + JSON / C++ that re-emit geometry) for the 3-bar
  prism, the 6-strut SUPERball, ULTRA-Spine, T6, T12, and biological
  tensegrity vertebra / spine models.
  <https://github.com/NASA-Tensegrity-Robotics-Toolkit/NTRTsim>
- **NASA SUPERball CAD / EE files** — public domain (US Govt).
  <https://github.com/kcaluwae/tensegrity-powerboard>
- **Berkeley ULTRA-Spine** — MIT.
  <https://github.com/BerkeleyExpertSystemTechnologiesLab/ultra-spine-simulations>
- **Tensegrity_gen** (Jiang Wong et al., classroom project) — generates
  parametric STL files for n-prism and class-1/2 tensegrities.
  <https://github.com/leenegnojw/Tensegrity_gen>
- **MOTES** (Modeling of Tensegrity Structures, MATLAB) — BSD-style
  research code with parameterized geometry generators.
  <https://github.com/ramaniitrgoyal92/Modeling_of_Tensegrity_Structures_MOTES>
- **Kenneth Snelson archive** — visual reference for the original
  hand-built sculptures (T-bar, X-piece, Needle Tower, etc.).
  <https://kennethsnelson.net/>
- **GrabCAD / Thingiverse / Printables** — community-uploaded STL
  files for hobbyist tensegrity tables and demonstration models;
  licences vary (Creative Commons), inspect each model.

## References

- Snelson, K. *Continuous tension, discontinuous compression
  structures.* US Patent 3,169,611 (1965).
- Pugh, A. *An Introduction to Tensegrity.* University of California
  Press (1976), ch. 3 (icosahedral tensegrity).
- Jessen, B. "Orthogonal Icosahedra." *Nordisk Matematisk Tidsskrift*
  15 (1967), 90–96.
- Connelly, R., and Whiteley, W. "Second-order rigidity and prestress
  stability for tensegrity frameworks." *SIAM J. Discrete Math.* 9
  (1996), 453–491.
- Skelton, R. E., and de Oliveira, M. C. *Tensegrity Systems.*
  Springer (2009), §2.3 (n-prisms), §2.4 (icosahedron).
- Sabelhaus, A. P., et al. "System design and locomotion of SUPERball,
  an untethered tensegrity robot." *IEEE ICRA* (2015).
