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

## D. Suggested next action

No source-of-truth file (`proposal.tex`, an `Ax` search-space JSON, etc.)
yet exists in the repo to encode these axes against; this document is the
synthesis the user asked for in PR comment 4411373088 ("Worth seeing if
there are additional parameters to consider based on new results in #22").
When the BO search space is first encoded (Ax / BoTorch JSON, or a LaTeX
table in `proposal.tex` / `manuscript-body.tex`), it should consume:

1. The original 5ae24eaf table (continuous strut/cable diameters, L/D,
   prestress, twist, infill %, layer height, TPU shore, wrap thickness,
   nozzle/bed temps, speed, plus the topology categorical).
2. The eight new categorical axes in §A above.
3. The five new (or conditional) continuous axes in §B above.
4. Constraints in §C (especially: defer class-2 / class-k topologies until
   Phase-4 joint designs are validated).
