# Joint design exploration — PETG (struts) + TPU (cables)

Resolves issue [#38](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/38). Multi-stage Edison-driven exploration of how to physically connect TPU 95A tension cables to PETG compression struts in a 3D-printed (Bambu Lab H2D IDEX FDM, 0.4 mm nozzle) tensegrity-like assembly — tested today as the single-piece pure-PETG T3-prism in [`cad/t3-prism/`](../../cad/t3-prism/) (PR [#35](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35)) and validated against the Lansmont M23 drop tower envelope (PR [#28](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/28)) under the rigid-strut + ideal-massless-tendon simulator assumptions of PR [#33](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/33).

## What was fetched / submitted

### Pre-existing trajectories (per the issue)

| Edison task | Topic | Files |
| --- | --- | --- |
| `1400ca69-3ef4-4847-8b0a-f457e34617b1` | Commercial / collaborator landscape for tensegrity | [md](../1400ca69-3ef4-4847-8b0a-f457e34617b1.md), [json](../1400ca69-3ef4-4847-8b0a-f457e34617b1.json) |
| `3b9d76b5-af7f-45fd-9b52-590bf0f2fe80` | Academic conferences / venues for tensegrity work | [md](../3b9d76b5-af7f-45fd-9b52-590bf0f2fe80.md), [json](../3b9d76b5-af7f-45fd-9b52-590bf0f2fe80.json) |

Neither contained substantive joint-design discussion — `1400ca69` mentions Ekso Bionics' `US10350130B2` "tensegrity joint for human exoskeleton" patent, and `3b9d76b5` notes Valter Böhm at OTH Regensburg works on "compliant tensegrity joints" — but neither prescribes a specific PETG+TPU FDM joint topology, which is why we ran the dedicated five-design exploration below.

### Phase 1 — five 1-credit `LITERATURE` queries (one per joint design idea)

Each query attached the same eight context files (`proposal.pdf`, `MRG_2026.pdf`, `_ctx_t3-prism-README.md`, `_ctx_t3-prism.scad`, `_ctx_t3-prism-iso.png`, `_ctx_tpu-petg-vars.md`, `_ctx_lansmont-m23.md`, `_ctx_simulations.md`) and asked for critique on (1) H2D manufacturability, (2) drop-test failure modes with rough quantitative bounds, (3) preservation of the rigid-strut + ideal-tendon simulator assumption, (4) cited prior art, and (5) numerical geometry + slicer recommendations.

| # | Slug | Concept | Edison task | Files |
| --- | --- | --- | --- | --- |
| **A** | `A-anchor-bulb` | PETG sphere with through-holes; TPU cable terminates in a printed-in-place TPU bulb | `0b5d7ba2-847e-47b3-bddf-127e2ed170d3` | [md](A-anchor-bulb-0b5d7ba2-847e-47b3-bddf-127e2ed170d3.md), [json](A-anchor-bulb-0b5d7ba2-847e-47b3-bddf-127e2ed170d3.json) |
| **B** | `B-dovetail` | Co-printed PETG dovetail/T-slot strut tip + matching TPU dovetail/T-head cable head | `ccb7b854-718c-4ac4-bf15-61c1fe522c7d` | [md](B-dovetail-ccb7b854-718c-4ac4-bf15-61c1fe522c7d.md), [json](B-dovetail-ccb7b854-718c-4ac4-bf15-61c1fe522c7d.json) |
| **C** | `C-tpu-sleeve-overmold` | TPU overmolded sleeve over knurled / grooved PETG strut tip (Ye 2023 / Khatri 2024 PETG–TPU wrap style) | `5a7ffce4-a8a0-49d6-9b43-3d0ea38d23f9` | [md](C-tpu-sleeve-overmold-5a7ffce4-a8a0-49d6-9b43-3d0ea38d23f9.md), [json](C-tpu-sleeve-overmold-5a7ffce4-a8a0-49d6-9b43-3d0ea38d23f9.json) |
| **D** | `D-eyelet-loop` | PETG eyelet ring + captive printed-in-place TPU closed loop (chain-link, topological constraint only) | `727a449d-d2af-4540-acfa-9b964f98689f` | [md](D-eyelet-loop-727a449d-d2af-4540-acfa-9b964f98689f.md), [json](D-eyelet-loop-727a449d-d2af-4540-acfa-9b964f98689f.json) |
| **E** | `E-tpu-rebar` | TPU "rebar" (optionally barbed) embedded several mm into the PETG strut tip; PETG printed on top of and around the embedded TPU | `ae373eb5-90e3-4543-b354-9e9990d76042` | [md](E-tpu-rebar-ae373eb5-90e3-4543-b354-9e9990d76042.md), [json](E-tpu-rebar-ae373eb5-90e3-4543-b354-9e9990d76042.json) |

### Phase 2 — `LITERATURE_HIGH` + `ANALYSIS` fired in tandem

| Edison task | Job | Topic | Files |
| --- | --- | --- | --- |
| `be6768ab-a4ca-433b-8bec-059819e3e368` | `LITERATURE_HIGH` | High-effort prior-art survey ranking the five designs by **strength of published precedent** | [md](PHASE2-literature-high-be6768ab-a4ca-433b-8bec-059819e3e368.md), [json](PHASE2-literature-high-be6768ab-a4ca-433b-8bec-059819e3e368.json) |
| `c38a2046-a37b-497f-aebb-efc2f35004de` | `ANALYSIS` | Synthesis + design-for-test recommendation. **Caveat:** at submission time only Phase-1 outputs C, D, E were complete; A and B were attached as task-IDs with a "fetch from platform if you can" note. The agent fetched and inlined them anyway, but a follow-up ANALYSIS with the full set of Phase-1 outputs is queued (see below). | [md](PHASE2-analysis-c38a2046-a37b-497f-aebb-efc2f35004de.md), [json](PHASE2-analysis-c38a2046-a37b-497f-aebb-efc2f35004de.json) |
| `ce84ddf8-5930-4c61-a6ce-65cf9ee3a6fa` | `ANALYSIS` (follow-up) | Re-run of the synthesis with **all five Phase-1 outputs** plus the `LITERATURE_HIGH` reply and the prior `ANALYSIS` reply attached for cross-checking. **Non-blocking — fetch next session.** | (pending) |

`task_manifest.json` carries the full machine-readable list of submitted Edison tasks and which files were attached to each.

## Headline rankings (different objectives, different rankings)

The two Phase-2 jobs ranked the same five designs along different axes — that is the point of running both.

| # | Joint design | LITERATURE_HIGH `be6768ab` rank<br>(*strength of published precedent*) | ANALYSIS `c38a2046` rank<br>(*best for our use case*) |
| --- | --- | :---: | :---: |
| **A** | Anchor-bulb spherical node | 4 (Weak–Moderate) | **2** |
| **B** | Co-printed dovetail / T-slot | **1 (Strong)** | 3 |
| **C** | TPU overmolded sleeve | 2 (Moderate) | 4 |
| **D** | Captive TPU loop through PETG eyelet | 3 (Moderate) | 5 |
| **E** | Embedded TPU "rebar" (barbed) | 5 (Weak) | **1** |

The two rankings are nearly **inverted**: the most-precedented dovetail / sleeve / eyelet designs are well-studied because they were tried and reported on, but our application (drop-impact + rigid-strut/ideal-tendon simulator + 6 mm strut envelope) penalizes them on different criteria. The ANALYSIS prefers **E (barbed rebar)** for our use case because mechanical interlock dominates frictional/chemical bonds, **A (anchor-bulb)** as a clean second because it is closest to the ideal-point-attachment simulator assumption.

## Recommended next move (verbatim from `c38a2046`)

> **Primary:** E (TPU rebar embedded anchor, **barbed**). **Backup:** A (Anchor-bulb).
>
> Embed length **10–12 mm** along the strut axis. Anchor stem Ø **2.4 mm** (matching `cable_d`). Barbs **2–3** at 2.0 mm pitch, major Ø **3.0–3.2 mm**, step ≥ 0.4 mm; flank angles 30–45° on pull-out face, 45–60° on insertion face. Keep PETG ligament from barb crest to outer surface **≥ 1.0–1.2 mm**.
>
> Slice on the H2D at PETG **250 °C** (bed 80 °C), TPU **215–225 °C**, layer height **0.16 mm** or **0.20 mm**, line width **0.42–0.45 mm**, **4–6 walls**, **80–100 % gyroid** infill in nodes, TPU outer-wall speed **10–20 mm/s**, careful retraction at toolchanges to keep TPU ooze out of the embed cavity. Print 1 inspection: PETG roof droop on the embed cavity (orient as a vertical blind hole if possible), TPU stringing, and barb-step definition (must not fuse into a featureless blob).

## Drop-test screening matrix (verbatim from `c38a2046`)

12 specimens disambiguating the top two designs across the two regimes:

| Specimen | Design | Article | Regime | Measurement → Joint physics |
| --- | --- | --- | --- | --- |
| 1–3 | E (barbed) | Single-anchor coupon | `crutch_tip` (75 kg user / 1.4 m/s, 30 kg surrogate to fit M23) | Static pull-to-failure (Instron) — calibrates Coulomb-slip threshold |
| 4–6 | A (bulb) | Single-anchor coupon | `crutch_tip` | Static pull + 8 g half-sine; accel on payload, LDV on bulb face — disambiguates pull-through vs PETG ligament crack vs cable rupture |
| 7–9 | E (barbed) | Full T3-prism | `nasa_lander` (5 kg / 9.8 m/s / 1500 g GEVS) | Accel on payload, LDV on saddle cable, post-test CT/photo — peak g, SEA, joint survivability at 9.8 m/s |
| 10–12 | A (bulb) | Full T3-prism | `nasa_lander` | Same; compare repeatability across 3 drops vs E; monitor bulb migration / bearing-edge cutting |

## How drop-test (#28, #33) assumptions get violated

The full per-design list of which simulator assumption each joint design violates is in [`PHASE2-analysis-c38a2046…md`](PHASE2-analysis-c38a2046-a37b-497f-aebb-efc2f35004de.md) section (2). One-line summary:

| Design | Worst violation of "rigid struts + ideal massless 1-D tendons" |
| --- | --- |
| A | Off-axis bearing friction at the bulb / hole edge — Coulomb friction term + small bulb-stretch series compliance |
| B | Joint compliance + rotational hysteresis (TPU head scraping inside PETG slot) — rotational damping at the attachment node |
| C | **Distributed attachment** over an 8 mm sleeve overlap + progressive slip — non-linear stiffness + frictional damper |
| D | **Deadband (~2–3 mm) before tension transmits** + routing friction — explicit Coulomb deadzone + frictional routing penalty |
| E | Local embed compliance + non-linear slip — Kelvin-Voigt + Coulomb-slip element at ~100–200 N |

Note the existing `simulations/run_regimes.py` finding ([PR #33](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/33)) that **peak g is dominated by floor contact** and is essentially flat across three decades of cable stiffness in the rigid-strut model — but **SEA does vary ~10×**. The joint-physics corrections above only matter for SEA-driven optimization (i.e. *most* of what the BO loop in PR [#30](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/30) actually optimizes); peak g still requires the DiffPD / IPC fidelity escalation Edison "Recommendation B" called for.

## Outstanding work

- [ ] Fetch ANALYSIS follow-up `ce84ddf8-5930-4c61-a6ce-65cf9ee3a6fa` (re-run with all 5 Phase-1 outputs attached) and commit `.md` + `.json`
- [ ] Update [`cad/t3-prism/t3-prism.scad`](../../cad/t3-prism/t3-prism.scad) with primary (E, barbed rebar) and backup (A, anchor-bulb) joint geometry parameters once issue [#37](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/37) (H2D PETG+TPU IDEX setup) lands a working multi-material print
- [ ] Add explicit lumped joint-compliance elements to `simulations/regimes.py` per the per-design corrections table above so the rigid-strut sims can express the SEA effect of joint choice

## Appendix — context files attached to the queries

The eight `_ctx_*` files in this directory are the exact files uploaded to Edison alongside each of the seven Phase-1 / Phase-2 tasks: the proposal PDF (top-level `proposal.pdf`), the MRG document (top-level `MRG_2026.pdf`), the present T3-prism CAD/iso/README from PR #35's branch, the prior TPU+PETG variables literature search from PR #24's branch, the Lansmont M23 brochure summary from PR #28's branch, and the simulator README from PR #33's branch. They are committed here for reproducibility — re-uploading them in a future session yields different `data_entry:` URIs but the same content fingerprint.
