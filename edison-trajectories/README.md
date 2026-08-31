# Egg-drop demonstration on a 3D-printed tensegrity

This folder collects the Edison Scientific trajectories that explore the
"egg-drop" demonstration concept raised in
[issue: Explore the idea of using an egg drop](../../../issues).

## Concept

Drop a raw chicken egg (~50–60 g) from height onto / into a Snelson-class
tensegrity unit cell (or tessellation, or six-bar icosahedron "ball")
fabricated on the Bambu Lab H2D as PETG struts + TPU 85A tendons, and
quantify the cushioning with high-speed video, an embedded MEMS
accelerometer, and a force-sensitive landing pad. Intended as a
high-visibility educational / promotional demo and a plausible publishable
contribution: no prior published work has used a tensegrity as the cushion
in an instrumented egg-drop.

## Artifacts in this folder

- `egg-drop-tensegrity-1b90208d.md` — verbatim Edison `formatted_answer` for
  task `1b90208d-3555-4479-9db0-512d67e69f5f` (LITERATURE_HIGH), including
  the question, the cited answer, and the full numbered references list.
- `egg-drop-tensegrity-1b90208d.json` — full structured `model_dump_json`
  payload from the same task for reproducibility.
- `egg-drop-followup-f41b7034.md` / `.json` — follow-up LITERATURE_HIGH task
  `f41b7034-439e-45de-b97f-4bf1d85b9811` (PR comment 4413896231): rooftop /
  no-drag drop, planetary-lander-style PETG cradle inside the tensegrity,
  drag-free baseline survey, and a V/m-constrained apples-to-apples
  benchmark protocol.

## Headline findings (see the .md for citations)

1. **Defensible demo, novel framing.** Egg-drop pedagogy is well documented
   (Sridhara 2005, Delson 2015, Purzer & Myers 2012, Newman & Hubner 2012),
   but no published work uses a tensegrity as the cushion. The combination
   of PETG+TPU on H2D, instrumented egg survivability, and a tensegrity
   topology is a defensible novel contribution.
2. **Egg fracture thresholds.** Trnka et al. 2012 report whole-egg
   plate-compression rupture forces of 24.6–53.5 N (weakest at the equator);
   fracture energy 2.3–6.1 mJ. Heuristic survivable peak deceleration is
   ~50–150 g for short impacts.
3. **Securing the egg — DO NOT mid-print embed.** PETG nozzle at ~230 °C
   and bed at ~70 °C will cook the egg, and biological contamination
   compromises layer adhesion and food safety. Recommended approach: a
   post-print TPU 85A sleeve / basket / cradle integrated with the tendons,
   with the egg wrapped in cling film for cleanup.
4. **Topology choice — six-bar tensegrity icosahedron.** Zhang et al. 2018
   showed 60–65 % peak-g reduction (114.9 g solid → 40.9–46.5 g icosahedron)
   on 1 m drops. Bauer et al. 2021 report tensegrity metamaterials absorbing
   ~13× the energy of octet lattices with a clear load-limiting plateau,
   and Pajunen et al. 2019 demonstrated <0.2 % residual strain per impact
   over 24+ impacts. Tessellated T-prisms are a follow-up.
5. **Instrumentation.** High-speed video at ≥ 5,000 fps (Photron NOVA or
   Chronos 2.1-HD) with speckle/marker DIC; embedded **ADXL375** ±200 g
   IMU on the egg cradle logged via ESP32 at 3.2 kHz; piezoelectric force
   plate (Kistler 9260AA / PCB 260A01) at ≥ 10 kHz, all synchronized with
   a break-beam photogate TTL trigger.
6. **First protocol.** Drop heights 0.25 → 2.0 m in 0.25 m steps, n ≥ 5
   replicates per height, fresh egg per drop. Predicted egg-survival
   transition between 1.0–1.5 m. Primary publication figure: peak-g vs
   drop height with the 50–100 g survivability band overlaid (parallels
   ASTM F1292 impact-attenuation plots; ASTM D5276 for the drop method).

## Reproducing the query

```bash
export EDISON_PLATFORM_API_KEY=...   # or EDISON_API_KEY (auto-mapped)
pip install edison-client
python scripts/edison/submit_egg_drop.py            # original task 1b90208d
python scripts/edison/submit_egg_drop_followup.py   # follow-up task f41b7034
```

The scripts write `egg-drop-tensegrity-<short_task_id>.{md,json}` and
`egg-drop-followup-<short_task_id>.{md,json}` into this folder.

## Follow-up findings — drag-free baseline + V/m benchmark (task `f41b7034`)

Sent in response to PR comment 4413896231 ("rooftop drop, no drag, mimic
planetary lander, PETG holder; what's the best drag-free baseline, and can
the tensegrity win under shared volume / mass constraints?"). See
`egg-drop-followup-f41b7034.md` for citations.

1. **Drag-free baseline survey.** Categories with published quantitative
   drop data: (a) crushable foam / honeycomb / metamaterial cushion,
   (b) elastic / hyperelastic recoverable cushion (TPU lattice, silicone),
   (c) spring / mechanical isolator stack, (d) granular / particle damper,
   (e) tensegrity / cable-strut shell (NASA SUPERball lineage), (f) bio-
   inspired analogues (woodpecker, pomelo). Tensegrity and elastomeric
   foam are the only categories with peer-reviewed *reusable* fragile-
   payload drop data above ~3 m.
2. **Best in class (drag-free).** Ranked shortlist:
   1. Anand 2022 biodegradable tensegrity + coir padding — 75 m drops onto
      pavement (single-use, ~4–5 drops, no accelerometer data).
   2. Agogino 2018 NASA SUPERball six-bar tensegrity — egg payload survived
      ~10 m free-fall, peak <25 g (sim) at 15 m/s; reusable.
   3. Zhang 2022 22″ tensegrity lander — 20 m drops, peak 235 g, mass
      1.103 kg, ~20-drop life. **Best instrumented tensegrity drop dataset.**
   4. Bauer 2021 / Pajunen 2019 tensegrity metamaterial — material-level
      ceiling: 25× deformability of octet, 24+ impacts at <3% residual.
   5. Bates 2016 / Bustihan 2025 TPU 95A honeycomb — strongest reusable
      elastic-foam baseline (47% absorption efficiency).
   No formally standardized "egg-drop benchmark" exists in the peer-reviewed
   literature; the SUPERball NIAC 1-foot-staircase egg-drop protocol is the
   closest reusable analog and is what we should adopt as the baseline.
3. **Apples-to-apples benchmark.** Recommended shared constraints: bounding
   sphere Ø 200 mm (V_max ≈ 4.19 × 10⁻³ m³), m_sys ≤ 500 g
   (protector + egg + sensors), m_egg = 55 ± 5 g, rigid concrete floor
   per ASTM D5276, both worst-case (vertex/face/edge) and random
   orientations. **Primary FoM: h_crit** (50 % survival, Bruceton up-down
   staircase, n ≥ 20, Δh = 0.5 m). **Secondary**: g_max at h = 3 m
   (n = 5), SEA = E_abs/m_protector (J/g), η_V = E_abs/V_protector (J/cm³),
   N_reuse, m_protector/m_egg, V_protector/m_egg. Standards backbone:
   ASTM D5276-98(2017) + ASTM F1292 + ISTA 1A + MIL-STD-810H Method 516.8.
4. **Where the tensegrity actually wins.** *Reusability under repeated
   impacts* (Pajunen 2019: 24 impacts, 2.28% cumulative residual;
   Bauer 2021: octet localizes above 2.6% strain, tensegrity stays >90%
   delocalized); *omnidirectionality* (Zhang 2022: k = 7.0–15.4 kN/m
   across 3 orientations, no catastrophic failure); *low relative-density
   regime* (Bauer 2021: at ρ_rel < 4% tensegrity absorbs 26× more energy
   than octet, 225× at 0.5%); *moderate-to-high reusable drops* (3–15 m).
   **Where conventional designs win**: mass-critical *single-use* (foam
   densifies the whole volume — octet σ_yield ~9× tensegrity per Bauer
   2021), volume-critical packaging (foam uses ~100% of bounding volume
   vs ~30–50% for tensegrity stroke), and very low drops (h < 2 m, where
   the cable network barely engages).
5. **Recommended demo figure.** Peak g vs drop height (0–15 m × 0–500 g)
   with the 130–300 g egg-fracture band shaded, comparing four named
   designs: unprotected egg (Zhang 2022 baseline: 121 g @ 1 m, 392 g @
   5 m), TPU 95A honeycomb block (elastic baseline), EPS foam shell
   (single-use baseline), and the PETG+TPU tensegrity test article.
   The visual argument is that the tensegrity curve crosses the fracture
   threshold at a higher h than the worst-case curves of the unidirectional
   baselines, with reusability shown as a companion N_reuse panel.

The benchmark protocol in §3 is the recommended path forward: it lets the
PETG+TPU tensegrity be defended on h_crit, SEA, η_V, AND N_reuse against
named drag-free baselines under shared V_max and m_sys constraints.
