# Impact of Tendon-to-Print-Direction Angle Variation on Planned Tests

**Source issue:** "Explore Tendon/Cable Printing Angles" (PR #62, motivated by the T3-prism print in PR #35, comment 4502140147).

**Question:** In our print-in-place tensegrity specimens, the TPU tendons of a single
part are deposited at very different angles relative to their load direction —
roughly **0° (parallel)**, **45°**, and **90° (perpendicular)** can all co-occur on
the same specimen. *To what extent does this affect the tests we have planned
across the open PRs?*

**Short answer.** It matters, but in a structured way:

1. The variation is **a real and not-negligible source of within-specimen
   property scatter** — for a TPU 85A tendon printed at 90° the strength can
   plausibly fall to ~30–60% of its 0° value, with stiffness less affected
   (~70–90%). The exact ratio depends on bonding, line width, and infill /
   wall pattern.
2. For **scalar campaign FoMs** (peak g, SEA, h_crit) the effect is mostly
   *bias* and *noise*, not a confound — as long as we **fix orientation**
   across replicates, the BO loop sees the orientation-conditioned response and
   can optimize against it.
3. For **mechanistic claims** — "the bottom-ring tendons govern peak g",
   "buckling-limited vs. tendon-limited regime", "topology X beats topology Y"
   — the angle distribution **is** a confound, because two designs with
   identical CAD can present very different oriented-tendon populations after
   slicing, and the weakest tendon usually decides the failure path.
4. The cleanest test-side mitigation is **logging which tendon failed and what
   its print angle was** on every specimen, treating the angle distribution as
   a per-specimen feature, and (in parallel) **giving BO an orientation knob**
   so it can co-optimize geometry + build orientation.
5. PR #52 (anchor-bulb threading DOE) is the structural escape hatch: if we can
   pull-thread TPU tendons after printing, we **decouple tendon strength from
   slicer-decided angles entirely**, and the angle problem only affects the
   subset of co-printed tendons we still want.

The rest of this note unpacks (1)–(5) and assigns a severity rating per PR.

---

## 1. Why this happens

FFF (and especially multi-material FFF on a single H2D bed) deposits each TPU
tendon as a stack of beads laid down in the **slicer-chosen XY direction**,
joined by interlayer welds in Z. For a slender free-standing cylinder like a
tendon:

- A tendon whose **axis lies in the build plane and parallel to its bead
  direction** (≈ 0°) carries axial tension primarily along the continuous
  bead, with bead-to-bead welds only on the sides. This is close to the
  "in-line" tensile direction tested in coupon studies.
- A tendon at **≈ 45° in the XY plane** alternates wall passes and short
  diagonals across its cross-section; tension still crosses some interlayer or
  inter-bead welds.
- A tendon at **≈ 90° relative to the bead direction** (image 3 in the issue)
  carries tension *across* every bead boundary; failure becomes
  weld-controlled.
- A tendon whose **axis is roughly vertical (Z)** is the worst case for any
  FFF part: every cross-section is a single layer's worth of interlayer weld.

This is the classic FFF anisotropy problem, but two things make it sharper for
us than for a typical coupon study:

| Factor | Why it hurts the tensegrity case more |
|---|---|
| **Print-in-place geometry** | A T3-prism / 6-bar tensegrity *cannot* have all tendons coplanar and aligned. For any single build orientation, some tendons are at favorable angles and some are not — by construction, not by mistake. |
| **Slender cross-section** | Tendons are ~2.4–4.5 mm Ø (PR #35 sweep). Two or three wall lines plus a tiny infill core means weld density is high relative to bulk material, so anisotropy ratios are *worse* than they are for thick coupons. |
| **TPU 85A specifically** | The lab uses TPU 85A (not 95A), E ≈ 12 MPa, σ_break ≈ 26 MPa, ε_break ~550–660 % (memorized from PR #33 / `simulations/printable_design.py`). Soft TPUs print well but interlayer welding is finicky at the small-radius corners that the tendon-to-joint hull transitions create. |
| **Captive-core joints (PR #35)** | The new TPU captive-core spheres at every vertex put a *concentrated TPU mass* right where the tendons emerge, which is where the worst angles are clustered in the photos. The joint geometry largely controls the local bead direction the slicer picks for the tendon root. |

**Numerical bracket** (caveat: these are coupon-scale FFF-TPU averages from
the open literature, not measurements on our parts):

- σ_UTS, 90°/σ_UTS, 0° ≈ **0.3–0.6** for FFF TPU coupons; ε_break drops more
  aggressively than σ_break.
- E_90°/E_0° ≈ **0.7–0.9** — stiffness is much less anisotropic than strength
  because the elastic response is dominated by bulk modulus contributions and
  the welds are stiff *until* they crack.
- For the in-plane 0°→45°→90° sweep (what the issue photos actually show),
  the strength typically follows a roughly monotonic but **non-linear** curve;
  most of the drop happens between 60° and 90°, so the 45° case is closer to
  0° than to 90°.

The takeaway is that **stiffness is mostly preserved but ultimate strength and
elongation-to-break are not**, which lines up exactly with the issue's
intuition that perpendicular-printed tendons "will fail first".

## 2. Effect on the scalar campaign objectives

The validation experiments we have committed to (cross-referenced in PR #33's
`simulations/validation_experiments.md` and PR #60's per-modality briefs) all
roll up to one of three classes of FoM:

| FoM class | Examples | Effect of tendon-angle variation |
|---|---|---|
| **Stiffness-like** | Initial loading slope (Instron, PR #49/#50); transfer-function magnitude at low f (LDV / shaker, PR #28, PR #60-03); pretension F_pre (PR #52) | **Small.** Stiffness is the least-anisotropic property. Within-batch CoV from print-angle effects is probably ≲ 10–15%, which is below the ~20% CoV typical of FFF coupon programs anyway. |
| **Strength / first-failure** | First tendon snap on the Instron; minimum drop height for visible damage; tendon yield in the SHPB analog (PR #58 Davami follow-up); F_pre upper bound in PR #52 | **Large.** This is *the* property we expect to vary 2–3× across the angle distribution within a single specimen. The weakest tendon decides, so the *minimum*-strength tendon (often the 90° one) sets the result. |
| **Energy-absorption / impact** | SEA, η_V, h_crit, peak-g (drop tower, egg-drop demo PR #47, multifidelity sim ladder PR #33) | **Medium and load-path-dependent.** If the cell stays elastic, behaviour is stiffness-dominated and the effect is small. As soon as one tendon yields/snaps the rest of the cell redistributes, and the angle of *that specific* tendon controls when the redistribution starts. |

So the practical statement is:

> *Initial stiffness tests (PR #50, the first Instron run) will see this as
> noise; energy-absorption tests (PR #33 / #47 / #58) will see it as a
> first-failure bias; the strength-of-the-weakest-tendon tests (PR #52) will
> see it as the entire signal.*

## 3. Per-PR impact assessment

Severity legend: **L** = absorbed by replication; **M** = orientation-bin or
log-the-angle to control for it; **H** = co-optimize orientation or use
manual-threaded tendons.

| PR | Test / Deliverable | Severity | Why | Suggested mitigation |
|---|---|---|---|---|
| **#28** — Lansmont M23 drop tower + Polytec QTec LDV equipment doc | Equipment-only PR; no specimens | **L** | Doc work, not testing. | n/a |
| **#33** — Multi-fidelity sim ladder (MuJoCo / Newton / DiffPD / PolyFEM+IPC) | Sim, not physical | **L for the sim itself**, **H for sim-vs-experiment validation** | Sims assume isotropic TPU. The bias enters when we *compare* sim peak-g/SEA against measured peak-g/SEA. | Either (a) add an orientation-dependent stiffness multiplier per tendon in `printable_design.py`, or (b) restrict early sim-vs-experiment claims to *stiffness*-like FoMs where the effect is small. |
| **#35** — T3-prism parametric CAD + Bambu .gcode.3mf + BO Sobol batch | Generates the very specimens we're worried about | **H** | Print-in-place; current build orientation is `vertical` (frozen per PR #35 comment 4503109338). The 0°/45°/90° tendon split is fully determined by this fixed orientation. | Add a `build_orientation` design knob to `bo/t3_prism_sobol_batch.py` (currently in the frozen list); render at least one Sobol batch in an alternate orientation; per-specimen log the *measured* tendon-axis-to-bead angles from the sliced gcode. |
| **#39 / #52** — Anchor-bulb design + 15-cell air-gap × joint-size DOE | The DOE is *literally* a tendon-strength characterization | **L for the DOE itself, H for what we generalize from it** | PR #52 fixes the cable to **horizontal** orientation on the +Y axis, so all 15 cells share the *same* (worst-case bridging) angle by design. That removes angle as a confound *within* the DOE. The risk is generalizing F_pre ∈ [5,25 N] from this orientation to other tendons on a full T3 specimen, which may be printed at very different angles. | Run a sanity-check 3-cell sub-array at 0°/45°/90° relative to bead direction, even just at the middle (S1,G2) cell, before locking F_pre targets for the rest of the campaign. |
| **#45** — Strut material Edison survey (PLA/PETG/HF/CF) | Literature only, no specimens | **L** | Affects struts, not tendons. | n/a |
| **#47** — Egg-drop demo + drag-free baseline | Specimens are 6-bar tensegrity icosahedra (~115→45 g, Zhang 2018 scaling) | **M** | The icosahedron has 24 tendons; the angle distribution will be even *richer* than the T3-prism (no two tendons are parallel). Peak-g and h_crit are first-failure-influenced. | Repeat each h_crit Bruceton-staircase point at ≥2 different build orientations to bracket the angle-induced spread; report orientation as a column in the demo plot. |
| **#49 / #50** — Instron stiffness, initial run | Quasi-static, sub-densification | **L→M** | First-pass FoM is *stiffness* and the cap is ≤30 % strain (PR #50). Angle effects on stiffness are small. As soon as we extend to UTS/EA, severity moves up. | Use the brief's recommended **5–10 TPU preconditioning cycles** before the modulus window (already planned). Add an explicit "*which tendon snapped first*" log entry to the per-specimen sheet so the angle effect is auditable, not invisible. |
| **#54** — Strut-curvature design axis | Affects struts, not tendons | **L** | Curved struts redistribute moment but the tendons are still the failure path. | n/a directly, but: a curved-strut cell may *change* the angle population that the slicer picks for adjacent tendons; worth a single sliced-gcode angle audit when a curved-strut specimen is added to the Sobol plate. |
| **#56** — Build-kit / DIY-materials recommendations | Documentation | **L** | Doc work, not testing. | Mention the angle effect explicitly so kit replicators don't blame their printer for variance that is inherent to the geometry. |
| **#58** — Davami 2025 (dynamic AM tensegrity) analysis | Comparative analysis + Edison follow-up | **M (for the comparison)** | Davami 2025 used SLA Tough 2000, which is **isotropic at the print-axis level** — none of their tendons see anisotropy. Our FFF specimens will, so a head-to-head SEA comparison will under-state our cell's "true" capability if interpreted as material-property-limited. | When we report the FFF-vs-SLA delta, decompose it into "material" (TPU vs Tough 2000) and "process" (anisotropy ratio at the loaded tendon) terms rather than a single SEA number. |
| **#60** — Cross-modality objective synthesis (5 data sources) | Defines the Ax `MultiObjective`; pure analysis | **M** | If `F_peak_N`, `SEA_J_per_g`, `eta` are treated as scalars, the BO loop will absorb angle scatter as observation noise. That is *fine* up to a point — but the loop will also down-weight signal that is actually orientation-controlled rather than design-controlled. | Promote `build_orientation` from a "frozen context variable" to a *categorical design parameter* in the Ax search space, with at least {vertical, horizontal-A, horizontal-B} levels per topology. The synthesis brief's normalization stays unchanged; only the search space widens. |

## 4. Mitigation options, ranked by cost

These are not mutually exclusive; the recommended path is to do the cheap ones
now and the structural ones over the next 1–2 print cycles.

1. **Per-specimen tendon-angle log (zero hardware cost).** Modify the sliced
   `.gcode.3mf` post-processor (the existing `patch_mm_extruder.py` from
   PR #35 is the natural hook) to also dump, for each tendon segment, the
   angle between the tendon's CAD-axis and the local bead direction. Write the
   table next to the project `.3mf`. This is what makes everything else
   possible — without it, every later inference is hand-wavy.
2. **Replicate Sobol cells at ≥2 build orientations.** PR #35's `BO batch`
   uses `tiling=1x1x1, build_orientation=vertical` as a frozen context. We
   should run *at least one* extra batch at a 45°-rotated build orientation
   (still print-in-place, just a different setup orientation on the bed) and
   bin the resulting SEA / peak-g by orientation. The same `t3_prism_sobol_batch.py`
   can do this; only `build_orientation` needs to leave the frozen list.
3. **Add an orientation-dependent stiffness scalar to the printable-design
   model** (PR #33 `simulations/printable_design.py`). One extra parameter,
   `k_anisotropy(theta)`, applied to each tendon's `EA/L` based on the angle
   logged in (1). This lets the sim ladder predict the *ranking* of build
   orientations before we burn a 9-cell plate on it.
4. **Promote build_orientation into the BO search space** (PRs #30, #35, #60).
   Once (1)–(3) are in place, the BO loop can co-optimize geometry + the
   build orientation that maximizes SEA for that geometry. This is exactly the
   "optimize which tendons are printed at what angles so the high-stress
   tendons get ideal angles" framing of the issue.
5. **Decouple via post-print tendon threading** (PR #52, manual-threading
   alternative noted in its README "Notes / next steps"). The structural fix:
   anchor-bulb pre-tensioning lets us print struts + anchors only, then
   manually thread a uniformly-extruded TPU cable through every tendon
   channel. Every tendon is then in its "best-case" extrusion direction and
   the angle problem disappears for the threaded tendons. The trade-off is
   process complexity and the loss of the "single-pre-assembled-piece"
   demonstration.

## 5. Recommended near-term actions

- **PR #35 follow-up:** add the per-tendon angle dump to the gcode
  post-processor, and unfreeze `build_orientation` in the Sobol-batch
  generator (default still `vertical`, but settable).
- **PR #50 follow-up:** add "first-tendon-to-fail (ID + angle bin)" to the
  Instron per-specimen metadata schema. Cost is one extra column; payoff is
  the entire downstream angle analysis.
- **PR #52 follow-up:** add an explicit angle-sensitivity sanity check (3
  cells × {0°, 45°, 90°}) at the middle of the existing 5×3 grid, so the
  pre-tensioning DOE doesn't lock in numbers that turn out to be
  orientation-specific.
- **PR #33 / #60 follow-up:** plumb a single scalar `anisotropy_ratio` knob
  through `printable_design.py` and `bo_evaluator.py`, defaulted to 1.0; the
  literature bracket above (0.3–0.6 for strength, 0.7–0.9 for stiffness) is a
  reasonable starting interval for sensitivity analysis.
- **Manuscript framing (PR #20 manuscript / PR #58 Davami comparison):** be
  explicit that the multifidelity-BO objective *includes* build orientation,
  i.e. we are optimizing the joint design × topology × orientation product —
  not the topology alone. This is also a defensible novelty axis: Davami 2025
  did not need to consider it (SLA), and the BEAR / Snapp 2024 lattice work
  (PR #47 Brown-lab follow-up) tested at scales where bead-anisotropy was a
  rounding error.

## 6. What this does *not* invalidate

- The PR #35 captive-core joint geometry is unchanged — it solves a different
  problem (PLA shell ↔ TPU core mechanical capture) and the angle question is
  orthogonal.
- The PR #45 strut-material conclusion (PLA primary, PETG conditional) is
  unaffected; struts carry compression along their long axis and are far less
  weld-controlled than the slender tendons.
- The PR #50 Instron protocol (5–10 TPU preconditioning cycles, ≤30 % strain
  cap, secant modulus, machine-compliance baseline) is the *right* protocol
  regardless. We only need to **augment** the per-specimen metadata, not
  change the test plan.
- The PR #28 LDV resolution (~sub-pm at 100 kHz) is *more* than enough to
  detect tendon-by-tendon stiffness differences, so the existing
  instrumentation is actually well matched to investigating this effect later.

---

*Cross-references: PR #35 comment 4502140147 (the print that motivated this);
PR #33 `simulations/validation_experiments.md` and `simulations/printable_design.py`;
PR #50 `edison-trajectories/instron-stiffness/equipment-selection.md`;
PR #52 `cad/anchor-bulb-tensioning-array/README.md`;
PR #58 `literature/davami2025-analysis.md`;
PR #60 cross-modality synthesis (Edison ANALYSIS task `789de8ab-9c68-4782-a70c-0a5a4e10e268`).*
