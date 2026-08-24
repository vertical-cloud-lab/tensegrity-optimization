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
time-series per article. Scope: the article alone impacting a rigid floor
at the measured 5.30 m/s, so its observables are article-intrinsic
(no mat to hide behind): peak top-vertex acceleration, article-side
restitution, and the free-flight ringdown after the bounce. See the PR
comment for the run-status table; runs are incremental, so re-running
`python polyfem_tierA.py` resumes where the last session stopped.

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
