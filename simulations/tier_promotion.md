# High-tier simulations of the printed articles (Tier B and Tier A)

Requested in PR #33 (comment, 2026-08-24): run the high-tier promotions,
until now listed as future work, on the structures that have been measured
or are about to be measured. That is both print batches: the 12 batch-1
prints (specs 0 to 8 plus the S0 reference, 8 of them with drop-tower
results) and the 9 round-2 prints (`r2d2c1` to `r2d2c9`, trials 10 to 18
from the PR #102 BO suggestions; 3 measured so far, 21 drops each).
21 articles in total, every one simulated at its as-printed geometry and
weighed mass.

## What each tier adds

| tier | script | struts | tendons | rig |
|---|---|---|---|---|
| C (baseline) | `drop_tower_sim.py` | rigid capsules | dead-band spring + modal-dial damper | carriage + calibrated mat |
| **B (new)** | `drop_tower_tierB.py` | **6-segment chains, ball-joint bending springs** `k = E_bend I / L_seg` | dead-band spring + **Kelvin-Voigt dashpot** from the TPU loss tangent | same carriage + same calibrated mat |
| **A (new)** | `polyfem_tierA.py` | **volumetric NeoHookean FEM** (welded gmsh mesh) | volumetric NeoHookean TPU | rigid floor through IPC contact, **strain-rate viscous damping (`psi`) in both materials** |

Material inputs are derived, not tuned to the bench: the bending modulus is
a wall-aware composite of solid perimeter walls and Gibson-Ashby infill
(2.8 to 3.2 GPa depending on strut diameter, `bending_modulus_MPa`), the
strut mass is split into printed-density capsules plus vertex-lumped joint
masses so the flexural inertia distribution is right, and the loss factors
(PLA eta = 0.05, TPU tan delta = 0.25) are mid-range literature values
mapped to dashpots at the measured ringdown band center (380 Hz). Tier A
converts the same loss tangents to continuum shear viscosities
(about 430 Pa s for TPU, 27 kPa s for PLA) and gives each article the mesh
density that makes it weigh what the scale said. Tier A additionally
consumes the twist axis in the mesh (`tprism_mesh` gained a `twist`
parameter), which no earlier PolyFEM run did.

## Tier-B results across the 21 articles

`outputs/tierB_articles.csv`, figure
`outputs/tier_promotion_comparison.png`, stats
`outputs/tier_promotion_stats.csv`.

The promotion does what it was supposed to do to the dead observables:

* **The flexural mode family now exists.** The flexural-band ringdown fit
  lands at 150 to 441 Hz across the articles, overlapping the measured
  294 to 468 Hz band. Tier C's ringdown lived at 22 to 96 Hz (rigid-body
  swing) with nothing above it.
* **`t180` spans 0.32 to 0.99** across the roster (Tier C: a few percent),
  and on the clean batch-1 comparison it rank-correlates with the measured
  `t180` at **rho = +0.75 (p = 0.052, n = 7)**. Pooling in the three
  measured round-2 articles destroys the correlation (rho = -0.10,
  n = 10); see the data-integrity note below before reading that as
  physics.
* **Ringdown damping is design-responsive but biased low**: flexural-band
  zeta 0.4 to 13 percent simulated vs 6.4 to 31 measured. The untuned
  eta = 0.05 PLA loss factor under-damps the clean flexural fits
  (about 1 to 1.5 percent); no rank signal at n = 8
  (rho = -0.26). The sim-to-bench damping gap is therefore roughly a
  factor 4 to 10, which is the size of the loss the rig paths
  (mount, glue, rails) plus material nonlinearity would have to supply.
* **Restitution is still not article-controlled** at Tier B
  (e_rebound 0.61 within 1 percent across all 21): the calibrated mat
  still owns the loss budget, exactly as the zeta study predicted. The
  article-side restitution needed Tier A.
* Simulated `t180` still cannot exceed 1.0 in this configuration even with
  flexure present; the measured amplification (7 of 8 batch-1 articles
  sit at 0.98 to 1.06) needs either the mount compliance or a resonance
  overlap with the input pulse that the calibrated mat pulse does not
  excite here.

Per-article numbers, including both the unrestricted dominant-line fit and
the flexural-band fit with their R^2 and band-energy fractions, are in the
CSV.

## Tier-A results (PolyFEM + IPC, viscoelastic)

`outputs/tierA_articles.csv` plus one `outputs/tierA_<print_id>.npz`
time-series per article; comparison panel
`outputs/tier_promotion_tierA.png`, correlation rows (`tA_*`) appended to
`outputs/tier_promotion_stats.csv`. Scope: the article alone impacting a
rigid floor at the measured 5.30 m/s, so its observables are
article-intrinsic (no mat to hide behind): peak top-vertex acceleration,
article-side restitution, and the free-flight ringdown after the bounce.
Runs are incremental: re-running `python polyfem_tierA.py` resumes with
whatever is not yet ok in the CSV. Status after the 2026-08-25 session:
19 of 21 articles completed (8 of the 10 measured articles and all 11
not-yet-measured ones); `9hhbkp` and `r2d2c2` are the two holdouts
described below.

What the promotion delivers, stated against the reason it was run: the
observables that were dead at Tiers B and C are design-responsive here.

* **Peak top-vertex acceleration spans 264 to 3667 g** (14x) across the
  completed articles, where Tier C was support-load-flat.
* **Article-side restitution spans 0.00 to 0.29**, where Tier B sat at
  0.61 within 1 percent for every article because the calibrated mat
  owned the loss budget. The compliant articles genuinely bounce
  (e_rebound 0.06 to 0.29) while the ones that land and stay read
  0.00 to 0.01.
* **The flexural ringdown lands at 60 to 450 Hz**, overlapping the
  measured 294 to 468 Hz band for the stiffer articles (Tier C sat at
  22 to 96 Hz rigid-body swing); damping fits span 0 to 67 percent,
  though several fits are multi-modal with low R^2 (kept in
  `ringdown_r2` rather than hidden).

Rank agreement with the bench at this sample size: none detectable.
fn rho = -0.37 (p = 0.47, n = 6), zeta rho = +0.09 (n = 6), article
restitution vs rig restitution rho = -0.38 (n = 8). The derived, untuned
material inputs make the channels move; they do not yet order the
articles the way the bench does, and n = 6 to 8 cannot separate a weak
signal from none. One single-article observation worth carrying:
`6lhxfy`, the bench's only genuine attenuator and its highest-rebound
article, is also Tier A's highest batch-1 peak-g and zeta article.

Two articles resist the current pipeline (both left as honest failures
in the CSV):

* `9hhbkp` meshes only at the finer lc fallback and then fails the solve
  (GradientDescent line-search failure at an impact step) even with the
  rescue settings; it likely needs a smaller dt.
* `r2d2c2` meshes at every inset but IPC rejects the initial state
  ("initial solution has intersections"): the welded gmsh mesh
  self-intersects at that geometry (twist 40 deg, strut 8.3 mm), so it
  needs a mesh-level fix rather than a solver knob.

Engine-version notes (June-era script vs today's PolyFEM/polysolve HEAD),
all fixed in `polyfem_tierA.py` in the 2026-08-25 session:

* vtu `points` now hold rest positions; displacement, velocity and
  acceleration arrive as point_data. The old parse therefore read a
  motionless article (peak 0.0 g and byte-identical ringdown "fits"
  across different articles). `extract_observables` applies the
  displacement field and prefers the solver's own velocity and
  acceleration fields over finite differences.
* polysolve renamed `grad_norm` to `grad_norm_tol` and tightened the
  default to 1e-10, which is what killed a third of the roster at Newton
  iteration limits. The config now sets `grad_norm_tol = 1e-7` with
  `allow_out_of_iterations = true` for the contact-impact steps, which
  also made the stepping roughly 4x faster.
* a failed gmsh inset retry can leave a truncated .msh ($Entities but no
  $Elements, PolyFEM "Invalid dimension"); the ladder now validates the
  written file, finalizes gmsh between attempts, and falls back to a
  0.75x lc scale on PLC intersection errors.

## Data-integrity note found on the way (round 2)

The round-1 drop-results table
(`data/pr102/t3-prism-bo-round1-drop-results.csv`, from the PR #102
branch) carries geometry columns that disagree with the photo-confirmed
print-key mapping:

* `r2d2c2` is spec 02 (trial 12) per the confirmed key, but the table's
  geometry columns are a uniform 0.899 x rescale of **trial 14 (spec 04)**;
* `r2d2c3` is spec 06 (trial 16) per the key, but the geometry matches
  **trial 10 (spec 00)** at 0.803 x;
* `r2d2c1`'s geometry columns match no round-2 trial at any uniform scale.

The measured channels (t180, zeta, e_rebound) are physical per-article
numbers and are unaffected; what is in question is which *design* each
measured article corresponds to. This directory simulates the
photo-confirmed mapping (suggestions print dims + weighed masses). If the
drop-results join is the correct one instead, the three round-2 comparison
points move, and the pooled correlations above change. Worth resolving on
the PR #102 side before round-2 results feed the campaign GP.

## Reproduce

```bash
python simulations/drop_tower_tierB.py                 # 21 articles, ~3 min
python simulations/tier_promotion_analysis.py          # comparison + figure
# Tier A (after the ~30 min PolyFEM source build, README "Edison Rec A"):
export POLYFEM_BIN=.../PolyFEM_bin POLYFEM_DATA_DIR=.../polyfem-data
python simulations/polyfem_tierA.py --workers 3
```
