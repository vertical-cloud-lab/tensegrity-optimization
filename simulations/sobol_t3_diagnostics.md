# Tier-C diagnostics: setup-artifact vs physics ablations

Edison's ANALYSIS review of the Sobol T3-prism campaign
([`edison-trajectories/sobol-t3-results/`](../edison-trajectories/sobol-t3-results/sobol-t3-results-ff8faab3-9ea4-427d-b545-9d0255c38e9d.md),
task `ff8faab3`) argued that the strongest Tier-C conclusions in
[`sobol_t3_analysis.md`](sobol_t3_analysis.md) are likely dominated by
simulation *setup* choices rather than absorber physics, and listed the
specific tests that would settle it (its section 5). This file runs those
priority ablations on 48 feasible PR #35 designs and reports what they show.
Reproduce with `python simulations/sobol_t3_diagnostics.py --n 48`.

## 1. The payload-acceleration `F_peak` is *support load*, not impact load

Edison: median crutch Tier-C `F_peak` / (75 kg·g) = 1.002 — the observable is
reading the static support load after CFC-180, not a resolved impact peak,
because the sim starts payload + struts co-moving (no free-fall separation)
and observes payload-body acceleration rather than transmitted base load.

Re-measuring the **vertical floor-reaction force** (sum of strut↔floor contact
forces — what a sensorized drop-tower platen reports) on the same 48 designs:

| observable | crutch median / static-weight | lander median / static-weight |
|---|---|---|
| payload-accel `F_peak` (campaign default) | **1.002** | — |
| floor-reaction `F_peak` | **0.1** | **103.5** |

The floor reaction is the transmitted load through the base. For the **lander** the floor reaction is **~104×** the static weight — a genuine impact transient the payload-accel observable (~1× static weight) entirely misses. For the **crutch** the large soft cell barely loads the floor within the 25 ms window (floor reaction 0.05× static weight, low ΔV), so neither crutch Tier-C observable resolves an impact peak — the crutch regime needs a longer free-fall window or Tier-B/A.

Design spread (relative span across the subset, lander):

* payload-accel `F_peak` span: **3.2%**
* floor-reaction `F_peak` span: **3.6%**

**Takeaway:** the payload-acceleration `F_peak` should be treated as a
support-load proxy, not an impact peak. The base-reaction force (and its
impulse, in `sobol_t3_diag_base_reaction.csv`) is the Tier-C observable that
matches the bench transmitted-load measurement.

## 2. CFC-180's effect on the design spread

Edison: re-run with and without CFC-180; if the near-invariance disappears
unfiltered, the filter is hiding the only design-dependent transient.

Relative span of the payload-accel `F_peak` across the subset:

| regime | CFC-180 filtered | raw (unfiltered) |
|---|---|---|
| crutch | 0.4% | 0.8% |
| lander | 3.2% | 10.4% |

For the **lander** the *raw* span (10.4%) is ~3× the filtered span (3.2%), so CFC-180 **does** suppress part of the design-dependent transient at this regime — the filtered objective is even flatter than the underlying sim. For the crutch both spans are sub-percent. So the right fix is the *observable* (§1, base reaction), and any filtered-vs-raw comparison must be made against the **same** observable the bench reports (PR #74 applies CFC-180 to measured accel, so simulated peaks must too — but only after switching to base reaction).

## 3. The `strut_d` effect is largely an inertia confound

Edison's "smoking gun": lander `F_peak` rank-correlates ρ≈-0.976 with a strut
mass proxy `L·d²`. Sweeping `strut_d_mm` at the box-centre design, free-mass
(PLA density fixed, so strut mass ∝ d²) vs constant-mass (density ∝ 1/d²). The
sweep is monotonic either way (Spearman stays ≈±1), so the honest metric is the
**effect size** — the peak-g range over the full `strut_d` sweep:

| regime | peak-g range, free-mass | peak-g range, const-mass | shrink |
|---|---|---|---|
| crutch | 0.002 g | 0.000 g | 6.6× |
| lander | 2.445 g | 0.144 g | 17.0× |

Holding strut mass constant shrinks the lander `strut_d` effect by
17.0×, confirming
that most of the apparent `strut_d` leverage at Tier-C is rigid-body mass /
contact-geometry, not absorber mechanics. `strut_d` should not be reported as
"the dominant design lever for impact attenuation" at this fidelity.

## 4. Twist is simply not consumed at Tier-C (plumbing, not physics)

`tprism_geometry.tprism_nodes` *does* take a `twist` argument, and the geometry
responds strongly to it — max node deviation across the PR #35 twist range
(40–80°) when twist is actually supplied = **2.05e-02 m**
(non-trivial). But the Tier-C build path holds it fixed: the `Regime` dataclass
has a twist field = **False**, and
`run_regimes.build_xml` passes a twist kwarg = **False** —
so it calls `tprism_nodes(...)` at the default `EQUILIBRIUM_TWIST` and every
PR #35 `twist_deg` builds the *same* cell. The twist≈0 Tier-C Spearman is
therefore expected plumbing behaviour, not evidence that twist is physically
irrelevant; it must be re-tested at Tier-B with a twist-isolation sweep (fixed
R/H/strut_d/cable_d, only twist varied) before any physical conclusion.

## What this changes in `sobol_t3_analysis.md`

1. Relabel the Tier-C payload-accel `F_peak` as a **support-load proxy**; add
   the floor-reaction force as the impact observable that carries the signal.
2. Keep "F_peak near-invariant" only for the *payload-accel* observable, and
   note the floor-reaction span is ~4% (lander).
3. Demote `strut_d` from "dominant lever" to "mostly an inertia/contact
   confound at Tier-C".
4. Keep the twist≈0 result but frame it strictly as un-consumed plumbing.

## Files

* `sobol_t3_diagnostics.py` — this script.
* `outputs/sobol_t3_diag_base_reaction.csv` — payload-accel vs floor-reaction
  peak + impulse, both regimes.
* `outputs/sobol_t3_diag_cfc.csv` — filtered vs raw `F_peak`.
* `outputs/sobol_t3_diag_constmass.csv` — strut-diameter sweep, free vs const
  mass.
* `outputs/sobol_t3_diagnostics.png` — 3-panel summary figure.
