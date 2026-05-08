# T3-prism (3-strut tensegrity) — Bambu PETG print

Resolves the issue [_"Get a bambu sliced print for a T3-prism"_](../../README.md):
parametric CAD + a single-piece, pure-PETG, Bambu-bound g-code for the
canonical 3-bar tensegrity prism shown on
[Wikipedia: Tensegrity](https://en.wikipedia.org/wiki/Tensegrity).

![T3-prism iso preview](t3-prism-iso.png)

## Geometry

A T3-prism has **3 compression members** ("struts") and **9 tension members**
("cables"): 3 around the bottom triangle, 3 around the top triangle, and 3
saddle/vertical cables connecting them. The two end triangles are
equilateral and inscribed in a circle of radius `R`; the top triangle is
rotated by `twist = 60°` relative to the bottom (the angle the issue calls
out and the relative twist visible in the Wikipedia reference image).

Connectivity (`i ∈ {0,1,2}`, mod 3):

| Member               | Endpoints       | Diameter |
| -------------------- | --------------- | -------- |
| Strut `i`            | `B_i  → T_i`    | 6.0 mm   |
| Bottom cable `i`     | `B_i  → B_{i+1}` | 2.4 mm   |
| Top cable `i`        | `T_i  → T_{i+1}` | 2.4 mm   |
| Saddle/vertical `i`  | `B_{i+1} → T_i` | 2.4 mm   |

Strut `i` and saddle `i` meet at top vertex `T_i` but originate from
*different* bottom vertices — the defining "no two compression members
touch" property of a tensegrity (the struts are kept apart by the cables).

Default parameters (editable at the top of [`t3-prism.scad`](t3-prism.scad)):

| Parameter  | Value | Notes |
| ---------- | ----- | --- |
| `R`        | 25 mm | end-triangle circumradius |
| `H`        | 70 mm | inter-triangle height |
| `twist`    | 60°   | top-triangle rotation |
| `strut_d`  | 6 mm  | compression member diameter |
| `cable_d`  | 2.4 mm | tension member diameter (≥ 2 × 0.4 mm nozzle) |
| `joint_d`  | 7 mm  | sphere at each vertex for clean joints |

Bounding box ≈ **50 × 50 × 77 mm**, volume ≈ **8.7 cm³** of solid material.
Comfortably fits every Bambu plate (X1C / P1S / A1 = 256², A1 mini = 180²).

## Single-piece, pure-PETG

Per the issue, this revision is a **single-material print in PETG** — both
struts and cables are unioned into one solid body, manifold-checked with
`admesh`. No multi-material assembly, no removable supports between
materials. PETG is an appropriate first pass: tougher than PLA (so the thin
"cable" features are less brittle when handled), prints cleanly on Bambu's
default Engineering Plate / Textured PEI, and matches the project's planned
move to TPU/PETG multi-material in later issues.

## Build & slice

```bash
# One-shot: STL + iso PNG + Bambu PETG g-code for X1C and A1 mini
bash cad/t3-prism/render_print.sh
```

Pre-reqs (Ubuntu): `sudo apt-get install -y openscad admesh prusa-slicer xvfb`.

Outputs (committed):

| File | What |
| ---- | ---- |
| [`t3-prism.scad`](t3-prism.scad) | parametric source |
| [`t3-prism.stl`](t3-prism.stl) | watertight binary STL (manifold, single part) |
| [`t3-prism-iso.png`](t3-prism-iso.png) | iso preview (above) |
| [`slices/t3-prism.X1C-PETG.gcode`](slices/t3-prism.X1C-PETG.gcode) | Bambu X1C / P1S / A1 (256×256 plate), PETG |
| [`slices/t3-prism.A1mini-PETG.gcode`](slices/t3-prism.A1mini-PETG.gcode) | Bambu A1 mini (180×180 plate), PETG |

Slice settings (mirror Bambu Lab's *Bambu PETG Basic @ X1C / 0.20mm
Standard* profile):

- 0.4 mm nozzle, 0.20 mm layers
- nozzle 255 °C, bed 70 °C
- 3 perimeters, 5 top / 4 bottom solid layers
- 25 % gyroid infill
- 4 mm brim, auto supports for the angled struts

Reported by PrusaSlicer at slice time: **~10.2 m / 24.5 cm³ PETG,
~3 h 15 min** print on the X1C profile.

### About "Bambu sliced"

PrusaSlicer's Marlin g-code dialect runs natively on Bambu firmware — the
included `.gcode` files can be SD-card / USB / LAN-loaded onto an X1C, P1S,
A1 or A1 mini and printed as-is. For the richer Bambu Studio Cloud workflow
(thumbnail, per-plate metadata, AMS slot mapping, *Send to printer*), open
[`t3-prism.stl`](t3-prism.stl) in **Bambu Studio**, pick the **Bambu PETG
Basic** preset and the **0.20mm Standard** process for your printer — the
geometry is identical and the parameter values above already match Bambu
Studio's defaults, so the resulting `.gcode.3mf` will closely track the
g-code committed here.

## References & related work

- Issue: ["Get a bambu sliced print for a T3-prism"](../../README.md)
- Programmatic-CAD pattern reused from
  [`vertical-cloud-lab/powder-doser` PR #16](https://github.com/vertical-cloud-lab/powder-doser/pull/16)
  (parametric `.scad` + headless OpenSCAD + slicer CLI).
- Programmatic-Bambu / meta-CAD survey:
  [`vertical-cloud-lab/powder-doser` PR #7](https://github.com/vertical-cloud-lab/powder-doser/pull/7).
- Reference image: [Wikipedia — T3-prism tensegrity](https://en.wikipedia.org/wiki/Tensegrity).
