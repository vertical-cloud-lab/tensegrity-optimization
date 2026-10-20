# Strut curvature as a first-class design axis — exploration

Synthesis written to address the user request in the "Explore how curvature
of the struts could affect the future of this project" issue.

Companion to:

- `tpu-petg-bo-variables-additions-from-pr22.md` (PR #24) — extra BO axes
  prompted by the PR #22 design-gap survey.
- `tpu-petg-bo-variables-5ae24eaf-5b6e-45cf-9f6c-1c7fbd881738.md` — original
  Edison TPU+PETG BO variables / bounds / objectives table.
- `2026-05-12-tensegrity-design-gaps-6226a551-...md` — PR #22 design-gap
  survey ranking 18 missing tensegrity families (including bistable
  double-prism and Schenk & Guest mechanisms).
- Lab constraints: PETG struts + TPU **85A** tendons on Bambu H2D,
  printable tendon Ø ∈ [1.2, 6.0] mm, strut Ø ≥ 2.0 mm
  (`simulations/printable_design.py`, copilot-instructions.md).

Both the original 5ae24eaf table and the PR-#22 additions treat the strut
as a *straight* member parameterised only by length `L`, diameter `D`, and
slenderness `L/D`. The issue asks what *strut curvature* would buy us,
beyond the obvious width / slenderness sweep, and explicitly calls out the
creative idea of two nearby struts that buckle *together* into a locked,
bistable position. This document scopes that axis.

## 1. Why curvature is a different axis from width / slenderness

For a straight Euler column,

```
P_cr = π² E I / (k L)²
```

is an upper bound that real specimens never reach because of unavoidable
imperfections — the as-printed strut always has some out-of-straightness
`δ_0`. The Southwell / Perry-Robertson treatment shows that the
*post-buckling shape* and the *direction of collapse* are dictated by `δ_0`
long before the load reaches `P_cr`; the magnitude of `P_cr` itself is set
by `E·I` and therefore by width.

That separation is the point. Width / slenderness sets *how much* load
the strut can carry; **curvature sets *which way* it goes after it gives
up, and how reproducibly**. For a tensegrity assembled on a Bambu H2D
where every strut already has print-induced curvature in the layer plane,
treating that curvature as a deterministic *design variable* instead of an
unmeasured imperfection turns a noise source into a control knob:

1. **Programmed buckling direction.** A built-in arc of amplitude
   `δ/L = 0.5–3 %` deterministically picks which face the strut hinges
   toward, removing the random `±` sign that otherwise dominates
   class-1 prism collapse experiments.
2. **Lower, repeatable peak force.** A pre-curved strut yields earlier
   and more gently than a nominally straight one, which is exactly the
   load-limiting behaviour Pajunen 2019 highlights as the EA mechanism of
   the truncated-octahedron cell. Curvature is the cheapest way to *tune*
   the plateau stress without changing `D` or material.
3. **Geometric pre-stress.** A curved PETG strut bowed against TPU 85A
   tendons stores elastic energy at zero load, partially substituting
   tendon prestress (`f_pre,i` axis in §B of PR #24). On TPU 85A
   (E ≈ 12 MPa secant) the tendon prestress budget is small; geometric
   curvature is a way to add stiffness without driving the soft tendons
   toward their ~26 MPa breaking strength.
4. **Coupled-pair bistability** — the issue's explicit creative ask. See
   §3 below.

None of these effects are reachable by changing strut diameter alone.

## 2. New / refined BO axes

| Axis | Domain | Conditional on | Why |
|---|---|---|---|
| `strut_shape` | {`straight`, `single_arc`, `S_arc`, `helical`, `tapered_arc`} | always | Top-level categorical. Must be exposed before any continuous curvature parameter is meaningful. |
| `curvature_amplitude` `δ/L` | continuous, `[0, 0.05]` | `strut_shape ≠ straight` | Mid-span out-of-plane offset normalised by strut length. Upper bound 5 % keeps the strut inside a typical 0.4 mm-nozzle 3-perimeter envelope at strut Ø ≥ 2 mm. |
| `curvature_plane_φ` | continuous, `[0°, 90°]` | `strut_shape ∈ {single_arc, S_arc, tapered_arc}` | Angle between the curvature plane and the local triad of attached tendons. Couples directly to which tendon is loaded first on snap-through. |
| `helix_pitch_ratio` `p/L` | continuous, `[0.5, 4]` | `strut_shape = helical` | Helical struts (Snelson Needle Tower variants, compliant-mechanism literature) trade buckling stiffness for torsional compliance — useful for the chirality_pattern axis already proposed in PR #24 §A. |
| `taper_ratio` `D_end/D_mid` | continuous, `[0.6, 1.0]` | `strut_shape ∈ {tapered_arc, helical}` | Tapering toward the joint reduces the joint-bore stress concentration (issue #38 Phase-3 / Phase-4 dovetail and anchor-bulb designs both bottleneck at the bore). Cheap manufacturability win on H2D since wall count scales with diameter. |
| `pair_coordination` | {`independent`, `parallel_sign`, `antiparallel_sign`, `chiral_pair`} | `N_struts ≥ 2` per face | Sets whether two neighbour struts curve *toward* each other (parallel sign) or *apart* (antiparallel). Drives the §3 bistable mode. |
| `snap_through_target` (constraint, not axis) | continuous, `[0.05, 0.5]` of nominal `P_cr` | `bistable_mode ≠ monostable` (already in PR #24 §A) | Target depth of the second equilibrium well, expressed as fractional load drop. Acts as a constraint that the BO acquisition function must satisfy, not as a free axis. |

These slot in alongside (not in place of) the existing
`{D_PETG, D_TPU, L/D, prestress, twist, …}` axes from 5ae24eaf and the
PR #24 §A categoricals. With seven new axes a full grid is infeasible, but
a Sobol-warmstarted BoTorch / Ax campaign of 50–100 specimens (the budget
from the original 5ae24eaf §D recommendation) can absorb the extra
dimensionality if `strut_shape` is treated as a top-level partition and
the conditional axes are only activated within their parent partition.

## 3. The coordinated-pair bistable mode (the issue's creative ask)

> "two nearby struts when compressed buckle together for bistable modes
> (moves into a locked position)"

Mechanically, this is a printed analogue of the Schenk & Guest bistable
mechanism (PR #22 design-gap survey item #14) and of the cooperative
snap-through used in stacked-arch metamaterials (Restrepo et al. 2015,
Frenzel et al. 2016, Pan et al. 2023). The key requirements are:

1. **Two struts whose mid-span curvatures lie in a shared plane**, with
   the curvatures pointing the same way (`pair_coordination =
   parallel_sign`) so that an axial compression hump pushes them into
   contact at mid-span instead of away from each other.
2. **A snap-engaging feature at mid-span.** The cheapest H2D-printable
   option is a complementary TPU 85A bump-and-pocket pair printed as part
   of the strut surface; on snap-through the bump latches into the pocket,
   holding the structure in the post-buckled configuration even after the
   compressive load is removed. Cost: one extra TPU island per strut pair,
   no new material.
3. **A reset path.** Lateral squeeze on the strut pair (perpendicular to
   the contact plane) pops the bump back out of the pocket. For a
   crutch-tip / egg-drop demonstrator this is the human "re-arm" gesture;
   for an autonomously deploying lander it would need a small recovery
   actuator or a thermally-triggered TPU softening cycle.

Why this matters for the project:

- **Load-limiting with hysteresis.** Monostable buckling caps the peak
  force (Pajunen 2019); a bistable pair *also* dissipates the elastic
  return energy as the structure stays in the buckled well. For a single
  high-energy event (egg-drop / planetary lander, see egg-drop-followup
  memory) this can roughly halve the rebound velocity compared to a
  reversible, monostable design — the whole point of energy *absorption*
  vs. energy *storage*.
- **Discrete deployment states.** Two struts coordinated this way give
  the assembly a discrete "tall / short" pair of equilibria. Stacking
  several such pairs along a Snelson mast (`N_bay ≥ 2`,
  `chirality_pattern = alternating`) yields a `2^N_bay` programmable
  shape space without any actuators — a passive analogue of the
  shape-changing tensegrity work cited in PR #22 items #15–17.
- **Ties cleanly to PR #22 / #24.** The bistable_mode categorical was
  already proposed in PR #24 §A; this `pair_coordination` axis turns it
  from "the cell as a whole has a snap-through" into "we can place
  snap-through at the strut-pair level", which is much easier to hit
  with a small (50–100 specimen) BO budget because each cell hosts
  multiple independent pairs.

## 4. Manufacturability notes (PETG on Bambu H2D)

- **Curvature is essentially free to print.** The H2D's per-layer XY
  motion can trace any planar arc; for `δ/L ≤ 5 %` the per-layer travel
  per unit Z is well below the ~0.4 mm nozzle width, so no bridging or
  support is needed. Helical struts with `p/L ≥ 0.5` are also printable
  in-place but become support-dependent below `p/L ≈ 0.3`; that is why
  the recommended bound is `p/L ∈ [0.5, 4]`.
- **Layer adhesion is *better*, not worse, for curved struts.** Because
  consecutive layers no longer sit on top of one another at the same
  `(x, y)`, each layer's seam is offset, which on PETG empirically
  improves interlayer shear (relevant to Pajunen-style post-buckling
  recovery, where the strut must survive multiple snap-through cycles).
- **Joint-design coupling (issue #38).** Both the dovetail (B) and
  anchor-bulb (A) joints from joint-design Phase-3 / Phase-4 assume a
  *straight* strut entering the bore. A curved or tapered strut needs
  the bore axis to align with the local strut tangent — a one-parameter
  edit to `cad/joint-design/B_dovetail.scad` and
  `cad/joint-design/A_anchor_bulb.scad` (rotate the bore by the
  end-tangent angle `α = atan(2 δ / L)`). No new joint family is needed.
- **TPU 85A interface.** PETG–TPU peer-reviewed bond data is still
  thin (strut-material memory: PLA–TPU butt 6.5 MPa, alt-deposition
  7.4 MPa, mechanical-interlock shear ~24 MPa; no PETG–TPU values).
  Curving the strut adds geometric interlock at the joint *without*
  adding a new bond mode, which is conservative until interface tests
  are run.

## 5. Failure-mode consequences

- **Curved PETG strut → gentle hinge-yield, not Euler snap.** This is
  the same failure-mode flag PR #24 §C raised for the Oster reentrant
  auxetic cell. For curved struts the slenderness window
  `L/D ∈ [4, 30]` from 5ae24eaf is still appropriate, but the BO
  objective should *log the failure mode* (Euler / hinge-yield /
  layer-delamination) for each specimen so that the surrogate can learn
  which curvature amplitudes flip the dominant mode.
- **Bistable pair → cyclic fatigue.** Snap-through on PETG drives a
  finite-strain cycle at the hinge each time. For the `N_reuse`
  secondary objective (egg-drop benchmark memory) this is the dominant
  durability risk; a pre-campaign 100-cycle screening at one geometry is
  cheaper than letting BO discover it at specimen 80.
- **Class-2 contact at mid-span.** The bump-and-pocket latch in §3
  introduces a *strut-to-strut* contact at the snap-through latch — i.e.
  the cell becomes class-2 at the latched state. Per PR #24 §C this is
  pending issue #38 Phase-4 validation; for now, only enable
  `pair_coordination ∈ {parallel_sign, antiparallel_sign, chiral_pair}`
  if `tensegrity_class ≥ 2`.

## 6. Suggested next actions (no code committed in this PR)

1. **Sim hook.** `simulations/printable_design.py` currently builds
   straight struts. Add a `strut_shape` argument with a single-arc
   parameterisation (`δ/L`, `φ`) and re-run the existing Newton (Warp)
   prism-drop notebook from `simulations/newton_drop.py` (per
   tensegrity-simulators memory) to confirm the curvature axis changes
   peak transmitted force for the T3 baseline. Defer until BO search
   space is encoded.
2. **Edison follow-up.** Send a LITERATURE_HIGH query specifically on
   *coordinated-pair* bistable buckling in printed lattices
   (Restrepo 2015, Frenzel 2016, Pan 2023, Schenk & Guest, plus any
   tensegrity-specific work — Sabouni-Zawadzka 2024 already shows
   post-critical strut behaviour but not paired latching). Save to
   `edison-trajectories/strut-curvature-bistable-pair-<task_id>.{md,json}`.
3. **CAD axis.** Add the bore-tangent rotation `α = atan(2 δ / L)` to
   `cad/joint-design/B_dovetail.scad` and
   `cad/joint-design/A_anchor_bulb.scad` so a single curvature value
   propagates to both joint families. One-line OpenSCAD edit per file.
4. **BO encoding.** When the BO search space is first encoded
   (BoTorch / Ax JSON, or a LaTeX table in `proposal.tex` /
   `manuscript-body.tex`), consume the seven axes in §2 *in addition to*
   the original 5ae24eaf table and the PR #24 §A/§B additions. Treat
   `strut_shape` as a top-level partition; only activate the conditional
   continuous axes inside their parent partition.
5. **Constraint, not axis (for now).** Until joint-design Phase-4
   returns class-2-capable joints, hold `pair_coordination =
   independent` and `snap_through_target = 0`. Curvature amplitude
   `δ/L` and curvature plane `φ` can be exposed immediately because
   they require no joint-family change.
