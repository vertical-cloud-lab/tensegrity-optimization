# Additional BO design variables prompted by the PR #22 design-gaps survey

Companion to:
- `tpu-petg-bo-variables-5ae24eaf-5b6e-45cf-9f6c-1c7fbd881738.md` — original
  TPU+PETG variables / bounds / objectives (this PR #24).
- `2026-05-12-tensegrity-design-gaps-6226a551-b46a-49b4-936a-bca600cd8d30.md`
  — design-gap survey on PR #22 ranking 18 missing tensegrity families
  (Snelson X-module, Pajunen truncated-octa, Oster reentrant auxetic,
  Rhode-Barbarigos pentagonal ring, Pugh diamond / zig-zag, tensegrity torus,
  Hanaor double-layer grid, Levy / Suspen-dome, 6-bar wheel patent
  US20240351370A1, Schenk & Guest bistable, D-bar / Sabouni-Zawadzka /
  Hao auxetic + multistable AM lattices, etc.).
- Lab constraints: TPU **85A** (not 95A) tendons, PETG struts on Bambu H2D,
  printable tendon Ø ∈ [1.2, 6.0] mm, strut Ø ≥ 2.0 mm
  (`simulations/printable_design.py`, copilot-instructions.md).

The original 5ae24eaf table treated topology as the categorical
{T3, T4, simplex, expanded-octa, truncated-octa, …}.  The PR #22 catalog
surfaces several **new** axes that are worth exposing to the BO search
space (or pinning as fixed-but-explicit conditions) before launching a
~50–100-specimen campaign.

## A. New / expanded categorical search axes

| New axis | Domain | Why it matters | Source family |
|---|---|---|---|
| **`unit_cell` (extend list)** | add `snelson_x_module`, `pentagonal_ring_RB`, `pugh_diamond`, `pugh_zigzag`, `tensegrity_torus`, `oster_reentrant_auxetic`, `bistable_double_prism`, `superball_with_payload`, `hanaor_DLTG_square` | The 5ae24eaf list omitted X-module and the 2D weave / planar families that are the most "flat-printable" candidates on H2D, and omitted the auxetic / multistable cells most relevant to crutch-tip impact attenuation. | gaps survey items #1, #3, #4, #5–6, #7, #8, Pajunen #2 |
| **`chirality_pattern`** | {`left`, `right`, `alternating`, `mirrored_pair`} | Stacked T3 masts (Snelson Needle Tower, Tibert & Pellegrino) and ring modules show qualitatively different load paths and twist-coupling under alternating vs same-handed stacking. | gaps survey #4 (Tibert), #1 (X-module weaves) |
| **`cable_routing`** | {`prism_basic`, `diamond` (Pugh), `zig_zag` (Pugh), `circuit` (class-2)} | Pugh's three canonical tendon patterns sit on the *same* node set as a prism but yield distinct anisotropic crush responses — a free knob that costs nothing in print envelope. | gaps survey #5–6 |
| **`tensegrity_class`** | {1, 2, k} | Class-2 ring modules (Rhode-Barbarigos pentagon) and Skelton compound-bar (D-bar / T-bar) cells become eligible once joint design supports strut-to-strut contacts (issue #38 joint-design Phase-3 / Phase-4 work). Lets BO trade off class-1 manufacturability against class-k specific energy absorption. | gaps survey #4, #15 (Ding 2025 D-bar) |
| **`tendon_clustering`** | {`independent`, `clustered_axial`, `clustered_radial`} | Clustered (sliding) tendons (Hao 2026) enable programmable multistability and stiffness reuse — a TPU-printable analog of pulleyed cables. | gaps survey #17 |
| **`bistable_mode`** | {`monostable`, `bistable`, `multistable`} | Intrigila double-prism (already in #22) and Schenk & Guest mechanisms are the path to *load-limiting* impact attenuation (snap-through caps peak F). Trivial to expose as a discrete switch coupled to prestress level. | gaps survey #14, original #22 catalog item 11 |
| **`payload_carrier`** | {`none`, `inner_icosa_cradle`, `axial_hub`} | SUPERball-with-payload (in #22 STL set) and the 6-bar wheel patent (US20240351370A1) both attach a hub/cradle that *changes the boundary conditions* seen by the tendon network — needs to be a controlled categorical, not a hidden geometry choice. | gaps survey #13; #22 STL `superball_with_payload.stl` |
| **`tessellation_pattern`** | {`single_cell`, `1D_stack`, `2D_grid`, `3D_lattice`, `toroidal_ring`, `double_layer_grid`} | Original list only had `Nx·Ny·Nz`. Hanaor DLTGs and the tensegrity torus require *non-orthogonal* tilings; need an explicit tessellation type before tile counts make sense. | gaps survey #7, #8, #9 |

## B. New continuous variables (or refined bounds)

| Variable | Suggested bound | Reason |
|---|---|---|
| **Per-tendon prestress group fraction** `f_pre,i ∈ [0, 1]` for i ∈ {axial, hoop, diagonal} (sums to 1, scales the global 0–5 % prestress already in 5ae24eaf) | simplex on 3 groups | Pajunen reported 2 % prestress is the sweet spot, but only as a scalar. The auxetic (Oster) and ring (Rhode-Barbarigos) families need *non-uniform* prestress to even be stable — splitting the budget by tendon role lets BO rediscover those stability windows. |
| **Number of bays / stacked cells** `N_bay` ∈ {1, 2, 3, 4, 6} | discrete | Was implicit in `Nz`; calling it out separately matters because alternating-chirality stacks (axis "chirality_pattern") only make sense for `N_bay ≥ 2`. |
| **Re-entrancy angle** `θ_re ∈ [-30°, +30°]` (auxetic family only) | continuous, conditional | Drives Poisson's ratio sign in Oster-type cells; was not in 5ae24eaf because no auxetic family was in the original topology list. |
| **Ring radius / strut-circuit count** `(R_ring, N_circuit)` for ring/torus families | continuous + discrete, conditional | Defines the donut envelope when `unit_cell ∈ {pentagonal_ring_RB, tensegrity_torus}`; needed before tile counts are meaningful. |
| **Hub / cradle mass fraction** `m_hub / m_total ∈ [0, 0.5]` (when `payload_carrier ≠ none`) | continuous, conditional | Couples to the *fixed* test impactor mass (still a fixed loading parameter, per 5ae24eaf), so it needs its own BO axis. |

## C. Refined PETG vs PLA scope notes (no change to bounds, but new caveats)

- The auxetic Oster cell uses *rubber-like* prototypes; on PETG struts the
  re-entrant geometry tends to fail by hinge-yield rather than buckling, so
  **strut slenderness L/D should be revisited** for that family
  (5ae24eaf already gave L/D ∈ [4, 30] which is wide enough — keep but log
  failure mode).
- Bistable / clustered families need TPU 85A, not 95A, to keep the
  snap-through energy barrier within hand-deployable range (lab uses 85A
  per memory; 5ae24eaf had 85A/95A as a categorical — keep both).
- Class-2 contacts (Pugh `circuit`, ring modules, Skelton compound bars)
  require validated PETG–PETG sliding/abrasion at the strut-end joint; not
  yet experimentally characterised in this lab — flag as **constraint**,
  not search axis, until issue #38 Phase-4 returns joint designs that
  actually support strut-to-strut contact.

## D. Hierarchical search space (per @sgbaird-alt, ref. Ax issue #140)

Many of the §A/§B axes are **conditional** — they are only meaningful
when the parent categorical takes a specific value (e.g. `re_entrancy_angle`
is meaningless unless `unit_cell == oster_reentrant_auxetic`). Encoding
those as flat, always-active parameters wastes BO budget exploring
invalid combinations and fools the GP with phantom correlations. The
correct encoding is Ax's `HierarchicalSearchSpace` (parameter with
`dependents={value: [child_param_names]}`), introduced after
[facebook/Ax#140](https://github.com/facebook/Ax/issues/140) and
documented at
<https://ax.dev/tutorials/hss.html> (`ax.core.search_space.HierarchicalSearchSpace`,
`ChoiceParameter(dependents=...)`).

### D.1 Parameter tree

```
ROOT
├── topology_family  [choice; ROOT categorical, drives everything below]
│   values = {
│     "prism_stack",      # T3 / T4 / stacked-prism / Snelson mast / Pugh patterns
│     "icosa_class",      # 6-bar icosa / expanded-octa / SUPERball / Jessen
│     "trunc_octa",       # Pajunen 2019 + Zhang 2021 tessellations
│     "ring_torus",       # Rhode-Barbarigos pentagonal ring, tensegrity torus
│     "auxetic_periodic", # Oster 2021 reentrant chiral
│     "double_layer_grid",# Hanaor DLTG / Charalambides square-base
│     "bistable_cell",    # Intrigila double-prism, Schenk–Guest snap-through
│     "x_module_weave",   # Snelson X-module planar weaves
│   }
│
├── [always-on]  shared continuous axes from 5ae24eaf
│     strut_D, cable_D, L_over_D, prestress_global,
│     PETG_layer_h, PETG_infill_pct, TPU_shore (categorical 85A/95A),
│     TPU_wall_count, nozzle_T, bed_T, print_speed, wrap_thickness,
│     relative_density
│
├── dependents of topology_family
│   ├── "prism_stack"  →
│   │     unit_cell ∈ {T3, T4, T6, simplex, snelson_needle_tower,
│   │                   pugh_diamond, pugh_zigzag}
│   │     N_bay         ∈ {1, 2, 3, 4, 6}
│   │     twist_angle   ∈ [10°, 45°]
│   │     cable_routing ∈ {prism_basic, diamond, zig_zag, circuit}
│   │     chirality_pattern ∈ {left, right, alternating, mirrored_pair}
│   │         └── only active when N_bay ≥ 2
│   │
│   ├── "icosa_class" →
│   │     unit_cell ∈ {icosahedron_6bar, jessen_expanded_octa, superball}
│   │     payload_carrier ∈ {none, inner_icosa_cradle, axial_hub}
│   │         └── hub_mass_fraction ∈ [0, 0.5]  (active iff != none)
│   │
│   ├── "trunc_octa" →
│   │     tessellation_pattern ∈ {single_cell, 1D_stack, 2D_grid, 3D_lattice}
│   │     Nx, Ny, Nz ∈ {1..6}  (Nz=1 unless tessellation_pattern≠single_cell)
│   │     pre_axial_frac, pre_hoop_frac, pre_diag_frac  (simplex, sum=1)
│   │
│   ├── "ring_torus" →
│   │     unit_cell ∈ {pentagonal_ring_RB, tensegrity_torus}
│   │     ring_radius_mm ∈ [20, 120]
│   │     N_circuit      ∈ {5, 6, 8, 10, 12}
│   │     tensegrity_class ∈ {2, k}    # class-2 implies strut-to-strut contact;
│   │                                  # GATED on issue #38 Phase-4 joint validation
│   │
│   ├── "auxetic_periodic" →
│   │     re_entrancy_angle_deg ∈ [-30, +30]
│   │     pre_axial_frac, pre_hoop_frac, pre_diag_frac  (simplex)
│   │
│   ├── "double_layer_grid" →
│   │     dltg_module ∈ {square_base, x_trihex_class_II}
│   │     Nx, Ny ∈ {1..6}; Nz = 1 (single double-layer)
│   │
│   ├── "bistable_cell" →
│   │     unit_cell ∈ {intrigila_double_prism, schenk_snap_arch}
│   │     bistable_mode ∈ {monostable, bistable, multistable}
│   │     tendon_clustering ∈ {independent, clustered_axial, clustered_radial}
│   │
│   └── "x_module_weave" →
│         weave_dim ∈ {1D, 2D}
│         tile_count ∈ {1..36}
│         (twist_angle, chirality_pattern as in prism_stack)
```

### D.2 Constraint encoding

- `tensegrity_class` is **not** a free top-level axis; it is implied by
  `topology_family` (mostly class-1) and only escapes class-1 inside
  `ring_torus` (class-2) or `bistable_cell.tendon_clustering=clustered_*`
  (class-k). This avoids the §A row that previously listed it as
  unconditional.
- `chirality_pattern`, `cable_routing`, `payload_carrier`,
  `tessellation_pattern` and `bistable_mode` from §A all become **child**
  parameters of `topology_family` (not free axes), eliminating ~70 % of
  the otherwise-invalid combinations a flat Cartesian space would
  generate.
- The Phase-4 joint-design gate (issue #38) stays as a **fixed feature**
  on the Ax `Experiment` (e.g. `joint_validated_class2 ∈ {False, True}`),
  forcing the `ring_torus` branch out of the search space until the gate
  flips.
- Per-tendon prestress group fractions are encoded as a 3-element simplex
  child of any `topology_family` that has distinct tendon roles
  (`trunc_octa`, `auxetic_periodic`); families without role-separable
  tendons (`prism_stack` with a single tendon set) keep the original
  scalar `prestress_global` from 5ae24eaf.

### D.3 BO surrogate / acquisition implications

- Use Ax's flat-encoded surrogate over the hierarchical space
  (Ax injects `__INACTIVE__` for inactive child params and the default
  GP / SAASBO model handles it). No custom kernel required for ≲50 BO
  iters per branch.
- The 8 top-level `topology_family` values are most cheaply screened
  with an initial Sobol budget *stratified by family* (≥3 specimens
  per family) before turning on Bayesian optimisation, so the GP sees
  at least one within-family pair per child sub-space.
- If a single contextual GP across families is desired,
  consider Ax's `MultiTaskGP` with `topology_family` as the task
  feature (cheaper than HSS for the project's ~50–100-specimen budget).

## E. Suggested next action

No source-of-truth file (`proposal.tex`, an `Ax` search-space JSON, etc.)
yet exists in the repo to encode these axes against; this document is the
synthesis the user asked for in PR comment 4411373088 ("Worth seeing if
there are additional parameters to consider based on new results in #22").
When the BO search space is first encoded (Ax / BoTorch JSON, or a LaTeX
table in `proposal.tex` / `manuscript-body.tex`), it should consume:

1. The original 5ae24eaf table (continuous strut/cable diameters, L/D,
   prestress, twist, infill %, layer height, TPU shore, wrap thickness,
   nozzle/bed temps, speed, plus the topology categorical).
2. The eight new categorical axes in §A above, **demoted to children of
   `topology_family`** as shown in §D.1.
3. The five new (or conditional) continuous axes in §B above, attached
   to the matching branch in §D.1.
4. Constraints in §C (especially: defer class-2 / class-k topologies until
   Phase-4 joint designs are validated — encoded as the
   `joint_validated_class2` fixed feature in §D.2).
5. The hierarchical encoding in §D, using
   `ax.core.search_space.HierarchicalSearchSpace` with
   `ChoiceParameter(dependents=...)` per
   [facebook/Ax#140](https://github.com/facebook/Ax/issues/140).
