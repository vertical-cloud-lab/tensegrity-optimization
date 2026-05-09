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
python scripts/edison/submit_egg_drop.py
```

The script writes `egg-drop-tensegrity-<short_task_id>.{md,json}` into this
folder.
