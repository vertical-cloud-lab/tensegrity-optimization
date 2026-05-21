# Objective functions and outcome measurements — per-data-source Edison brief

Source issue: [#51 "Explore objective functions and outcome measurements of
interest"](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/51),
which extends [#36 comment 4509305026](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/36#issuecomment-4509305026)
(Jeff's 2026-05-21 drop-tower walkthrough — [YouTube](https://youtu.be/RNjpAmWWmkQ)).

For each of the five measurement modalities the lab plans to use on the
PETG-strut + TPU 85A-tendon (Bambu H2D) tensegrity energy-absorber program,
one `LITERATURE_HIGH` Edison query was submitted and fetched in the same
session. Every answer is structured identically (a-g) so they can be diffed
side-by-side when wiring the [`bo/tensegrity_campaign.py`](../../bo/tensegrity_campaign.py)
metric / objective / constraint shape:

| # | Data source | Task ID | Artifacts |
|---|-------------|---------|-----------|
| 1 | Accelerometer (M23 base + top plate; 200 ms shock + ~10 s ringdown) | [`cfd30f3e-…`](./01-accelerometer-cfd30f3e-20e8-43b4-b055-29f9fc4f121f.md) | [md](./01-accelerometer-cfd30f3e-20e8-43b4-b055-29f9fc4f121f.md) · [json](./01-accelerometer-cfd30f3e-20e8-43b4-b055-29f9fc4f121f.json) |
| 2 | High-speed camera / slow-mo phone (drop event + DIC) | [`7d6b43bf-…`](./02-high-speed-camera-7d6b43bf-d948-4e13-aea5-4a89ec12ed49.md) | [md](./02-high-speed-camera-7d6b43bf-d948-4e13-aea5-4a89ec12ed49.md) · [json](./02-high-speed-camera-7d6b43bf-d948-4e13-aea5-4a89ec12ed49.json) |
| 3 | Electrodynamic shaker + base/top accelerometers (transmissibility, modal) | [`31126ee7-…`](./03-shaker-transfer-function-31126ee7-9f3b-4af4-adbe-855c14513487.md) | [md](./03-shaker-transfer-function-31126ee7-9f3b-4af4-adbe-855c14513487.md) · [json](./03-shaker-transfer-function-31126ee7-9f3b-4af4-adbe-855c14513487.json) |
| 4 | Pneumatic slug-firing / gas gun (longer impulse, tiled-cell + plate) | [`9d74ab2e-…`](./04-slug-firing-gas-gun-9d74ab2e-669f-48bd-938b-7e380e188492.md) | [md](./04-slug-firing-gas-gun-9d74ab2e-669f-48bd-938b-7e380e188492.md) · [json](./04-slug-firing-gas-gun-9d74ab2e-669f-48bd-938b-7e380e188492.json) |
| 5 | Polytec VibroFlex QTec single-point LDV (non-contact velocity) | [`f40e41a7-…`](./05-polytec-qtec-ldv-f40e41a7-b41d-4158-a89f-f18a5ae81e5c.md) | [md](./05-polytec-qtec-ldv-f40e41a7-b41d-4158-a89f-f18a5ae81e5c.md) · [json](./05-polytec-qtec-ldv-f40e41a7-b41d-4158-a89f-f18a5ae81e5c.json) |

Every `.md` file contains the verbatim Edison `formatted_answer` with a YAML-
style header listing `task_id`, `slug`, `job`, `status`, and `fetched_at`.
Every `.json` file is the full `model_dump_json` of the `TaskResponse` for
reproducibility. The submission / poll-and-fetch driver is
[`scripts/edison/submit_objective_functions.py`](../../scripts/edison/submit_objective_functions.py)
and is idempotent — re-running it picks up existing `*-SUBMITTED.json`
placeholders so a follow-up session can resume polling without re-billing.

## Common (a-g) skeleton

Each answer covers the same seven sub-questions, in this order:

- **(a)** Raw observable(s) the sensor produces and the integration /
  filtering / windowing step needed to derive physical quantities from them.
- **(b)** Defensible Bayesian-optimization **objectives** (with noise floor,
  per-specimen CoV, units). Universally considered candidates: `g_max`,
  `SEA_J_per_g`, `eta` (crush / plateau efficiency), `epsilon_d`
  (densification strain), transmissibility / loss factor, settling-time /
  damping ratio `zeta`, cycle / reuse count `N_reuse`, plus modality-specific
  figures of merit.
- **(c)** Defensible **constraints** (hard cutoffs or chance-constraints for
  qNEHVI / NEHVI), with peer-reviewed threshold values.
- **(d)** Recommended **characterization settings**: sample rate, anti-alias
  filter, transducer range / sensitivity, mounting / standoff, trigger /
  pretrigger, frame rate / shutter / aperture (optical), excitation profile,
  window length, number of averages, and the applicable ASTM / ISO / JEDEC
  standards.
- **(e)** How the modality slots into the BO campaign in PR #30 + PR #33 —
  Ax `Metric` / `Objective` shape, observation-noise model (heteroscedastic
  vs. homoscedastic), per-trial cost / wall-clock budget, fidelity tier in
  the MuJoCo → Newton → PolyFEM+IPC ladder.
- **(f)** Top gotchas / failure modes / cross-talk artifacts that would
  silently corrupt the BO objectives.
- **(g)** Numbered, DOI-resolved references (no fabricated citations).

## Tied-in repository surfaces

- [`bo/tensegrity_campaign.py`](../../bo/tensegrity_campaign.py) — Ax MOO
  campaign whose current placeholder objectives (`F_peak_N`, `SEA_J_per_g`,
  `eta`) are recast against modalities 1, 4, and 5 of this brief.
- [`simulations/validation_experiments.md`](../../simulations/validation_experiments.md)
  — 10-row sim ↔ experiment table; modalities 1-5 here become the experiment
  axis of that table.
- [`equipment/lansmont-m23/`](../../equipment/lansmont-m23/) and
  [`equipment/polytec-qtec/`](../../equipment/polytec-qtec/) — instrument
  documentation surveyed in PR #28; modalities 1, 4, 5 here populate the
  optimization-campaign half of those READMEs.
- [`edison-trajectories/instron-stiffness/`](../instron-stiffness/) — the
  quasi-static counterpart to these dynamic-loading modalities (relevant for
  modality 3's quasi-linear / pre-prestress identification).

## Cross-modality picture (extracted by hand from the five answers)

The five modalities span three complementary time-scales / fidelities, and
the briefs converge on roughly the following BO role for each (see each
answer's `(b)` and `(e)` sections for the exact wording):

- **Modality 1 (accelerometer) — primary destructive objective generator.**
  Owns the canonical `F_peak_N` (via `m_top × a_top`), `SEA_J_per_g`, `eta`,
  and `epsilon_d` triple, plus a ringdown-derived `zeta` and `f_1`
  (eigenfrequency). Heteroscedastic homotopy with sim-fidelity tier C/B.
- **Modality 2 (high-speed video) — ground truth + non-objective scoring.**
  Provides densification displacement to close the energy integral for (1),
  plus categorical-objective signals (failure-mode classification, reuse /
  shape-recovery score for `N_reuse`). Best treated as auxiliary `Metric`s
  on the same trial.
- **Modality 3 (shaker transmissibility) — cheap pre-screening.**
  Non-destructive, repeatable per specimen across prestress sweeps;
  natural fit for a *low*-fidelity tier in a MultiTaskGP (cost in minutes
  per design, no consumable specimen).
- **Modality 4 (gas gun) — strain-rate-extension objective.**
  Generates BO data points beyond the M23 energy envelope on tiled / armour-
  framed cells; same metric shapes as (1) but on a different specimen class.
  Treat as a separate Ax `Experiment` (or task in a MultiTaskGP) rather than
  pooling with (1).
- **Modality 5 (Polytec QTec LDV) — non-contact cross-check + scanning ODS.**
  Removes the mass-loading / range bias of the contact accelerometer on the
  smallest / softest cells; on the gas gun, it back-computes transmitted
  pressure. Doubles as a poor-man's scanning LDV across multiple points per
  shot to enrich (3)'s modal identification.

## Reproducing / extending

```bash
pip install -q edison-client
export EDISON_API_KEY=...   # script auto-mirrors to EDISON_PLATFORM_API_KEY
python scripts/edison/submit_objective_functions.py
```

The script is idempotent: existing `<slug>-SUBMITTED.json` placeholders are
reused as the task ID, so partial fetches across multiple sessions converge
to the same artifacts.
