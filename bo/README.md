# T3-prism Bayesian-optimization batch generator

Single-iteration, **human-in-the-loop** first batch of T3-prism specimens
for the lab's BO campaign — issued in response to PR #35 comment
[`4503109338`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4503109338)
from @sgbaird.

This script is a *restricted* adaptation of the full multi-topology BO
scaffold on
[`copilot/scaffold-bayesian-optimization-script`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/copilot/scaffold-bayesian-optimization-script/bo/tensegrity_campaign.py)
(PR #30 / PR #24). The full scaffold sweeps every topology, tiling,
material pairing, and build orientation in the project's Edison-curated
literature table; this script freezes everything that isn't specific to
the **T3-prism** geometry, because the team has only confirmed printability
for T3-prisms so far (PRs #16 / #30 / #24 / #35).

## What's swept

| Variable      | Range          | Maps to `cad/t3-prism/t3-prism.scad` |
| ------------- | -------------- | ------------------------------------ |
| `R_mm`        | [25.0, 40.0]   | `R_base` (radius of each end cap)    |
| `H_mm`        | [60.0, 110.0]  | `H_base` (height between caps)       |
| `twist_deg`   | [40, 80]       | `twist`                              |
| `strut_d_mm`  | [6.0, 12.0]    | `strut_d_base` (PLA strut Ø)         |
| `cable_d_mm`  | [3.0, 5.5]     | `cable_d_base` (TPU cable Ø)         |

All five are continuous (`type: range`) so the Sobol sequence covers them
uniformly. The cable diameter lower bound of 3 mm is the empirical "Bambu
auto-support threshold" from PR #35 — below it the top-triangle TPU
bridges fail mid-print (the `cable_d = 2.4 mm` spaghetti event diagnosed
by Edison ANALYSIS `25c1c897`).

The Sobol coordinates above are the **design coordinates** (what the BO
model sees). The **as-printed** dimensions differ by a per-specimen uniform
scale, because every specimen is projected onto the constant-mass manifold —
see [Constraints](#constraints-constant-mass--max-envelope-volume) below.
After projection the as-printed `cable_d` can fall below the 3 mm bridge
floor; those specimens are flagged `cable_bridge_ok=False` in the CSV
(acceptable under the manual-painted-supports workflow — the floor only
matters for unsupported self-bridging).

## Constraints (constant mass + max envelope volume)

Per PR #35 comment `5132975378` (@sgbaird) the batch enforces the two
constraints of the PR #33 hybrid campaign
([`simulations/sim_bo_hybrid_campaign.py`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/copilot/explore-simulations-for-tensegrity/simulations/sim_bo_hybrid_campaign.py)):

* **Route A — constant cell mass `m*`.** Each specimen's `(R, H, strut_d,
  cable_d, joint_d)` are uniformly re-scaled (twist and all shape ratios
  preserved) until its estimated as-printed mass equals `m*`. The default
  `m*` is the solid-volume mass of the committed S0 reference design
  (`cad/t3-prism/t3-prism-{struts,cables}.stl` — the geometry of the most
  recent instrumented prints): `V_struts·1.24 g/cm³ + V_cables·1.21 g/cm³`.
  The sensor housings are absolute-size physical fixtures and do **not**
  scale, so the solve iterates on rendered STL volumes
  (`m(s) = m_housings + m_body(1)·s³`) until `|m − m*| ≤ 0.15 g` — the
  converged mass includes every real geometry feature (captive cores,
  teardrops, skirts, housings, boolean overlaps).
* **Route B — max envelope volume `V*`.** `envelope_cm3 = π·R_print²·H_print`
  (circumscribing cylinder of the prism, the
  `bo_evaluator.cell_geometry_metrics` definition) must be ≤ **250 cm³**
  (`sim_bo_hybrid_campaign.DEFAULT_ENVELOPE_MAX_CM3`). Because the uniform
  scale is consumed by the mass constraint, a shape whose envelope still
  exceeds `V*` at `m*` is **constraint-infeasible**: it is flagged
  `envelope_ok=False` in the CSV/JSON rather than silently dropped or
  re-scaled (printing it still yields a valid infeasibility observation
  for the BO model; excluding it from the plate is the team's call).

Both targets are CLI-overridable (`--mass-g`, `--envelope-max-cm3`).

## What's frozen (and why)

| Variable             | Value             | Reason |
| -------------------- | ----------------- | ------ |
| `topology`           | `t3_prism`        | Only printable family so far |
| `tiling`             | `1x1x1`           | Single unit cell |
| `struts_per_cell`    | `3`               | T3 by definition |
| `build_orientation`  | `vertical`        | Per comment: "maximize the number on the build plate" |
| `tpu_shore`          | `85A`             | NinjaFlex-class lab default |
| `strut_material`     | `PLA` (extruder 1)| Production target on this branch |
| `cable_material`     | `TPU` (extruder 2)| Production target on this branch |
| `supports`           | `manual_painted`  | Per comment: "@achris0520 will manually paint on supports" |
| `joint_d_mm`         | `7.0`             | minimum vertex shell diameter; captive-core upsizes to ≥ `cable_d + 5.4 mm` when needed (see [Captive TPU core](#captive-tpu-core-inside-pla-outer-shell-joints) below) |
| `use_captive_core`   | `true`            | every joint is a captive TPU core sphere inside a hollow PLA outer shell with a uniform spherical PLA wall and three cable-exit bores (PR #35 comment [`4511036510`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4511036510), bonded per [`4513722886`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4513722886)); identical geometry to `cad/t3-prism/t3-prism.scad` |

The slicer-side modeled-in PLA scaffold pillars from PR #35 commit
`5437366` are **not** emitted here — they were a workaround for the
slicer's auto-support gap on near-vertical TPU cables, and Audrey's
painted-supports approach in PR #35 comments `4502140147` /
`4502171087` supersedes them.

## Rendered from the canonical SCAD (sensor housings included)

Since PR #35 comment `5132975378` the generator no longer carries its own
embedded SCAD template. Each specimen is rendered **directly from
[`cad/t3-prism/t3-prism.scad`](../cad/t3-prism/t3-prism.scad)** via `-D`
parameter overrides (`R_base`, `H_base`, `twist`, `strut_d_base`,
`cable_d_base`, `joint_d_base`, `scale_factor`, `part`), so every specimen
automatically carries the **latest** joint and sensor-housing design and can
never drift out of sync with the single-specimen CAD again. At HEAD that
means: captive-core joints (bonded, teardrop blend), the three top-vertex
rounded "igloo" accelerometer mounts (A3 explicit 6.2 × 6.2 × 6.8 mm
pocket), and the three beside-mounted flat bottom key-seats hovering above
the plate. The housings are physical-part fixtures in absolute mm — they do
not scale with the specimen.

## Captive TPU core inside PLA outer shell joints

Every vertex of every specimen is a captive-core joint (mirrors
[`cad/t3-prism/t3-prism.scad`](../cad/t3-prism/t3-prism.scad) — see
"Captive TPU core inside PLA outer shell" there for the geometry
rationale and bond-mechanics motivation, PR #35 comment
[`4511036510`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4511036510)).
Per specimen, the SCAD template computes:

```
bore_d   = cable_d                                    # bonded — TPU fills bore (PR #35 comment 4513722886)
core_od  = max(bore_d + 2 * 1.5, joint_d)             # ≥ bore + 3 mm trap
shell_id = core_od                                    # bonded — TPU core touches PLA inner wall
shell_od = max(shell_id + 2 * 1.6, joint_d)           # 1.6 mm PLA wall
```

For the BO sweep's `cable_d ∈ [3.0, 5.5] mm`, shell_od therefore varies
from **10.0 mm** (small-cable specimens, clamped to `joint_d=7` → bore
3.8 → core 6.8 → still smaller than joint_d so shell_od defaults to
`bore + 5.4` = 9.2 mm; with the second `max(., joint_d)` clamp, shell_id
collapses to ≥7 mm and final shell_od to `max(8 + 3.2, 7)` = 11.2 mm)
to **13.2 mm** (`cable_d=5.5` specimens). The plate-grid cells are sized
from each specimen's **measured** STL footprint (joint shells, igloo
mounts, and beside-mounted bottom key-seats included), so every specimen
fits inside its own cell.

## How to run

```bash
sudo apt-get install -y openscad admesh xvfb \
    gstreamer1.0-plugins-base libsoup-3.0-0 libwebkit2gtk-4.1-0
python3 bo/t3_prism_sobol_batch.py        # default n=9, pinned first-batch designs
```

By default the 9 first-batch Sobol design coordinates are read back from
the committed `t3-prism-bo-batch.csv`, so re-running regenerates the same
physical designs against the current CAD (no `ax-platform` install
needed). Knobs:

* `--n N` — number of specimens (default `9`, packed `3 rows × 3 cols` on
  the 350×320 mm H2D plate with a 50 mm +X strip held back for the IDEX
  prime/flush tower and a 6 mm inter-cell air gap; since the constant-mass
  projection the grid uses **variable column widths / row heights** — the
  largest specimens share a column and a row — so 3×3 still fits inside
  the prime-tower-reduced usable area)
* `--resample` — draw a fresh Sobol batch via Ax instead of reusing the
  pinned designs (requires `pip install ax-platform`; `--seed S` applies)
* `--designs-csv PATH`: take the design coordinates from any CSV carrying
  the five swept columns instead of the pinned first-batch table. This is
  how a **model-based** round gets built: point it at the suggestion table
  written by `bo/t3_prism_bo_campaign.py`
  (`t3-prism-bo-suggestions-roundN.csv`), which uses the same column names.
  The row's `trial_index` is carried into the batch table as `source_trial`
  so each plate specimen traces back to its Ax trial.
* `--out-prefix NAME`: basename for every emitted artifact (default
  `t3-prism-bo-batch`). Use it so a BO round lands beside the pinned Sobol
  batch instead of overwriting it (e.g. `--out-prefix t3-prism-bo-round1`
  writes `t3-prism-bo-round1.csv`, `-struts.stl`, `-plate.png`,
  `slices/t3-prism-bo-round1.H2D-MM-PLAstruts-TPUcables.3mf`, and
  `per-specimen-stls/t3-prism-bo-round1-specNN-*.stl`).
* `--mass-g M` — override the Route-A constant mass m\* (default: computed
  from the committed S0 reference STLs)
* `--envelope-max-cm3 V` — override the Route-B envelope cap V\* (default 250)
* `--jobs J` — parallel OpenSCAD render workers (default 4)
* `--skip-render` — CSV/JSON with analytic scale estimates only (CI smoke test)
* `--skip-mm-3mf` — skip the BambuStudio CLI multi-material project assembly

## Outputs (next to this script)

* `t3-prism-bo-batch.csv`        — design table: one row per specimen with
  the original Sobol coordinates (`R_mm` … `cable_d_mm`), the constant-mass
  projection (`scale`, `*_print_mm` as-printed dimensions), the mass audit
  (`mass_g`, `pla_g`, `tpu_g`, `mass_target_g`, `mass_ok`), and the
  constraint flags (`envelope_cm3`, `envelope_max_cm3`, `envelope_ok`,
  `cable_bridge_ok`)
* `t3-prism-bo-batch.json`       — same data plus constraint + plate-layout metadata
* `t3-prism-bo-batch.scad`       — preview wrapper that `import()`s the
  plate-positioned per-specimen STLs, with a
  `part = "all"|"struts"|"cables"` switch (the geometry itself is rendered
  from `cad/t3-prism/t3-prism.scad`)
* `t3-prism-bo-batch.stl`        — packed STL, struts + cables fused
  (preview / single-material use only — Bambu Studio cannot split this
  into PLA and TPU after import)
* `t3-prism-bo-batch-struts.stl` — struts + captive-core PLA shells (uniform spherical wall) + per-cable bores at exactly `cable_d` so the TPU cable fills them without an air ring (extruder 1 / PLA, PR #35 comment [`4513722886`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4513722886))
* `t3-prism-bo-batch-cables.stl` — cables + captive TPU core spheres at every vertex (sized to contact the PLA inner wall so the two materials bond at the vertex) + a zero-width z-anchor that pins the cables-STL bounding box to the struts-STL bounding box (extruder 2 / TPU). The z-anchor fixes the "horizontal cables too low at top and bottom" misalignment reported above PR #35 comment [`4511036510`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4511036510).
* `per-specimen-stls/t3-prism-bo-specNN-{struts,cables}.stl` — one struts STL + one cables STL **per specimen**, used by the `--assemble` step so the final `.3mf` exposes one composite object per specimen with two part groups (PLA + TPU) rather than one giant composite with `2N` ungrouped parts (PR #35 comment [`4513722886`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4513722886))
* `t3-prism-bo-batch-plate.png`  — top-down build-plate preview
* `t3-prism-bo-batch-iso.png`    — iso preview
* `slices/t3-prism-bo-batch.H2D-MM-PLAstruts-TPUcables.3mf` — **production-target
  Bambu H2D multi-material project file.** Re-importable into Bambu Studio
  with each specimen exposing two parts (struts/PLA on extruder 1, cables/TPU
  on extruder 2) so the team can split-to-parts and assign filaments per
  PR #35 comment [`4503267471`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4503267471).
  Supports are intentionally OFF; @achris0520 paints them on per
  comment [`4502140147`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-4502140147).

## Round 1 (model-based, mass-aware) plate

The first model-based batch. Its nine designs are the round-1 suggestions
from the mass-aware campaign in PR #102 (comment
[`5365706779`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/102#issuecomment-5365706779)),
Ax trials 10 to 18, committed here verbatim as
`t3-prism-bo-suggestions-round1.csv`. Rebuild it with:

```bash
python3 bo/t3_prism_sobol_batch.py \
    --designs-csv bo/t3-prism-bo-suggestions-round1.csv \
    --out-prefix t3-prism-bo-round1
```

Everything else is unchanged from the Sobol batch: same constant-mass
projection onto m\* = 30.95 g, same 250 cm^3 envelope cap, same captive-core
joints and A3 sensor housings, same 3x3 plate with the 50 mm prime-tower
reserve, supports off for manual painting. Artifacts carry the
`t3-prism-bo-round1` prefix; the production file is
`slices/t3-prism-bo-round1.H2D-MM-PLAstruts-TPUcables.3mf`.

All nine clear the envelope cap and land within 0.15 g of the mass target.
Three (specimens 00, 02, 05 = trials 10, 12, 15) fall to an as-printed cable
diameter of 2.6 to 2.7 mm, below the 3.0 mm TPU self-bridging floor, and are
flagged `cable_bridge_ok=False` in the design table. That is the expected
consequence of holding mass constant on a thick-strut, thin-cable design
(12 mm struts and 3 mm cables at base scale), and it is workable under the
manual-painted-supports workflow, but those three need the most careful
support painting on the top-triangle cables.

### Manually-supported round-1 project (as prepared for printing)

`slices/t3-prism-bo-round1.H2D-MM-PLAstruts-TPUcables_manual-supports.3mf`
is @achris0520's Bambu Studio project for this plate, uploaded in PR #35
comment [`5374553137`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-5374553137).
It is the generated round-1 project with supports painted by hand on all
nine specimens and the printing presets applied, so it is the file that was
actually sent to the printer rather than a regenerated artifact.

| Setting | Value |
| --- | --- |
| Printer / process | Bambu Lab H2D 0.6 nozzle, 0.30mm Standard @BBL H2D 0.6 nozzle |
| Filaments | Bambu PLA Basic (ext 1, struts) + Bambu TPU 85A (ext 2, cables) |
| Filament map | Manual, `['1','2']` |
| Supports | `tree(manual)`, painted, `support_filament=1` (PLA), build-plate only |
| Prime tower | on, 60 mm |
| Infill / walls | 15% sparse, 2 walls |
| Bed | Textured PEI Plate |

Painted-support coverage is stored per object as `paint_supports` triangle
attributes: 16,628 painted facets across the nine `3D/Objects/object_*.model`
parts.

Slicing it headlessly (BambuStudio CLI v02.06.00.51) gives 13 h 58 m,
255.45 g PLA + 66.94 g TPU, with 198,567 support and 63,545
support-interface extrusion moves out of 883,256 total. Two provenance
renders of that g-code are committed next to the design table:
`t3-prism-bo-round1-manual-supports-sliced-iso.png` and
`-sliced-top.png`, both produced by

```bash
RS_MODEL_MAX=220000 python3 cad/t3-prism/render_supports.py \
    plate_1.gcode bo/t3-prism-bo-round1-manual-supports-sliced-iso.png
RS_MODEL_MAX=220000 RS_VIEW=89,-90 python3 cad/t3-prism/render_supports.py \
    plate_1.gcode bo/t3-prism-bo-round1-manual-supports-sliced-top.png
```

`RS_MODEL_MAX` raises the model-segment cap (the default 40,000 leaves a
nine-specimen plate looking like haze) and `RS_VIEW` sets `elev,azim`.
`t3-prism-bo-round1-manual-supports-bambu-plate.png` is Bambu Studio's own
plate thumbnail carried inside the project file.

The CLI run itself ends with `return_code=-102` ("G-code in unprintable area
of multi-extruder printers"), the same headless IDEX extruder-mapping
limitation documented in `cad/t3-prism/render_print.sh` `slice_bambu_mm`. It
writes valid toolpaths, which is what the renders above are drawn from, but
the printable job still has to come out of the Bambu Studio GUI.

## Onshape spot-check upload

The per-specimen STLs can be pushed to a public Onshape document so the
geometry can be inspected/measured in a browser before printing (PR #35
comment [`5133453991`](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35#issuecomment-5133453991)).
`cad/t3-prism/onshape_upload_t3prism.py` accepts an explicit STL list, a
document name, and a concurrency setting:

```bash
PREFIX=t3-prism-bo-round1   # or t3-prism-bo for the pinned Sobol batch
ARGS=""
for i in 00 01 02 03 04 05 06 07 08; do
  ARGS="$ARGS --stl spec$i-struts-PLA=bo/per-specimen-stls/$PREFIX-spec$i-struts.stl"
  ARGS="$ARGS --stl spec$i-cables-TPU=bo/per-specimen-stls/$PREFIX-spec$i-cables.stl"
done
python3 cad/t3-prism/onshape_upload_t3prism.py \
    --doc-name "T3-prism BO round 1 - constant mass (PR #35)" --jobs 6 $ARGS
```

Each import's bounding box is read back through the API and printed in mm as
a scale check — it should match the local STL extents exactly (the
`/partstudios/.../boundingboxes` endpoint reports millimetres, not metres).

## Reporting outcomes back

This first batch deliberately **does not** call `complete_trial(...)`.
The full closed-loop campaign lives in
[`bo/tensegrity_campaign.py`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/copilot/scaffold-bayesian-optimization-script/bo/tensegrity_campaign.py)
on the `copilot/scaffold-bayesian-optimization-script` branch; once
measured F_peak / SEA / η land for these nine specimens, hand them to the
closed-loop campaign as already-observed Sobol trials before requesting
the first model-based batch.
