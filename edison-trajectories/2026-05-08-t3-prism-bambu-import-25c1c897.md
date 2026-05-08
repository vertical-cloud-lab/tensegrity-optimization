# T3-prism Bambu H2D — `.gcode.3mf` import + cantilever risk (Edison ANALYSIS)

- task_id: `25c1c897-6d66-462f-bfdb-7df05ff12d9b`
- job_name: `job-futurehouse-data-analysis-crow-high`
- status: `success`
- created_at: `2026-05-08T18:22:37.440150Z`

## Query

We are preparing a Bambu Lab H2D PETG print of a T3-prism (3-strut
tensegrity, single-piece, pure PETG, no supports) and producing the
print-prep artifacts headlessly with the official BambuStudio
v02.06.00.51 Linux AppImage CLI under xvfb-run + software GL, following
the recipe verified in vertical-cloud-lab/powder-doser PR #23.

Two questions, please address both:

1. **Bambu Studio import error on the sliced `.gcode.3mf`.** When we
   try to drag/import `slices/t3-prism.H2D-PETG.gcode.3mf` (attached;
   produced by `bambu-studio --slice 1 --export-3mf` with
   `--filament-map-mode Manual --filament-map 1`), Bambu Studio shows
       "The file does not contain any geometry data"
       "Loading of a model file failed"
   The hand-made project `cad/t3-prism/t3-prism.3mf` (also attached,
   uploaded by Marcus from Bambu Studio GUI; currently printing
   without supports on the H2D) opens fine. Diff'ing the two zips:
   the GUI one has thumbnails (`Metadata/plate_*.png`) and NO
   `Metadata/plate_1.gcode`; the CLI one has `Metadata/plate_1.gcode`
   (the actual print job, ~3.97 MB) and NO thumbnails. The 3D model
   parts (`3D/3dmodel.model`, `3D/Objects/object_1.model`) are
   structurally identical (same UUIDs, same `<components>` ref).
   - Confirm or refute our hypothesis: Bambu Studio's drag/import
     code path treats `.gcode.3mf` as a printer-side artifact and
     refuses to re-import it as a model — and the correct workflow
     is to use *File → Open Project* (which still works on
     `.gcode.3mf`), or to load a separate project `.3mf` produced
     without `--slice` (we now also generate
     `slices/t3-prism.H2D.3mf` — attached — for that purpose).
   - Are there other plausible causes (corrupted `object_1.model`,
     missing `[Content_Types].xml` entry, missing thumbnails being
     load-blocking, etc.)? The CLI ran without GL (`glfwInit return
     error, code 65544` — Wayland not available) so thumbnails were
     never rendered; could that be the trigger?
   - Cite Bambu Lab community-forum / GitHub-issues threads if you
     find any that describe the same symptom and resolution.

2. **Print quality / risks for the in-progress H2D print.** The
   print is currently at ~13% (layer 26 / 385) on the H2D, no
   supports. The geometry has three angled struts (~70 mm tall,
   60° twist) and 9 thin (2.4 mm) cables — most of the cables are
   either at the bottom triangle (printed first), the top triangle
   (printed last as a small bridge), or saddles connecting the two
   (steep diagonals). Bambu Studio is showing a "cantilever
   warning" upcoming as the saddle/top features start.
   - Given 0.20 mm layer height, 25% gyroid infill, 3 walls,
     auto-orient (the part was placed flat), what is the highest-
     risk feature and at what layer (rough estimate) do we expect
     it? The total height is ~77 mm.
   - Is the top triangle a true bridge or a free cantilever
     (i.e., are the 60°-rotated saddles long enough to count as
     supports for the top cables)?
   - Recommendations to maximize success on the current print AND
     for the next iteration (orientation, layer height, support
     strategy, cable diameter, joint sphere diameter, etc.) —
     remembering the constraint is single-piece, single-material
     PETG, no manual support removal between materials.

Please be specific, cite forum threads / docs / papers where you
can, and reference the attached files explicitly when relevant
(filenames are in their attachment metadata).


## Answer

Here are the answers to both questions based on the part geometry, slicer mechanics, and Bambu Studio (BS) internal behavior.

### 1. Bambu Studio import error on the sliced `.gcode.3mf`

**Your hypothesis is correct:** Bambu Studio's drag-and-drop / normal "Open Project" code paths actively discriminate based on the `.gcode.3mf` extension, treating it as a **printer-bound artifact** rather than an editable project. 

The "no geometry data" error is a direct consequence of this branched logic, but the error message itself is highly misleading in your specific CLI context. Here is exactly what is happening:

* **Bambu Studio's dual file formats:** A standard BS project `.3mf` contains CAD geometry (the mesh in `3D/3dmodel.model`). However, when BS exports a sliced plate via the GUI (*Export plate sliced file*), it creates a `.gcode.3mf` that strips out the heavy mesh data entirely to save space for LAN/SD-card transfer, leaving only the raw G-code, settings, and thumbnails.
* **The CLI hybrid:** When you run `bambu-studio --slice 1 --export-3mf` and name the output `*.gcode.3mf` (or if the CLI auto-appends it), the CLI actually produces a "hybrid" file. Unlike the GUI export, it *keeps* the full mesh (your `object_1.model` is intact at ~1 MB with 6,526 vertices) *and* adds the G-code. 
* **The import failure:** When you drag a `.gcode.3mf` into BS, the internal `load_gcode_3mf_from_stream` function takes over. It expects the GUI-style "stripped" format and specifically looks for print metadata in `Metadata/slice_info.config` (e.g., a `<plate>` block with weight, time, and filament mapping). Because the CLI `slice_info.config` is missing this block, the G-code loader aborts. The loader never even attempts to read the `3D/3dmodel.model` mesh, resulting in the fallback error: "The file does not contain any geometry data."

**Refuting the thumbnail hypothesis:** The lack of a Wayland/GL display (`glfwInit error 65544`) did *not* block thumbnail generation. Your `xvfb-run` + software GL setup worked: the `Metadata/plate_1.png` inside your CLI `.gcode.3mf` is a valid 19.7 KB render of the prism. Thumbnails are not the cause of the import failure.

**Resolution / Workflow:**
Your current two-file workaround is the correct, intended workflow:
1. Generate `slices/t3-prism.H2D.3mf` (without `--slice`) to act as your editable project file for GUI work.
2. Generate `slices/t3-prism.H2D-PETG.gcode.3mf` (with `--slice`) strictly to be pushed headlessly to the printer via MQTT/FTP. Do not attempt to re-import this file into BS.

*(For related community documentation of this behavior, see GitHub Issues [BambuStudio #1479](https://github.com/bambulab/BambuStudio/issues/1479) where a maintainer explicitly states `.gcode.3mf` is a "print file for individual plate" and not a project file, and [#2930](https://github.com/bambulab/BambuStudio/issues/2930) documenting CLI-generated 3MF re-import issues).*

***

### 2. Print quality / risks for the in-progress H2D print

The T3-prism geometry is highly optimized for FDM, but it does contain one severe overhang risk. At 13% (layer 26 of 385), you have successfully cleared the bottom cables (which act as a ~2.3 mm-high bridge over the bed) and are currently building the lower halves of the struts and saddles. 

**The highest-risk feature:** 
The point of failure will not be the cantilevered saddles or the top joint spheres; **it will be the first few layers of the three top cables.** These begin printing at roughly **layer 362** (Z ≈ 72.3 mm in build coordinates).

**Is the top triangle a true bridge or a free cantilever?**
It is a **true bridge**.
* The struts ($B_i \to T_i$) and saddles ($B_{i+1} \to T_i$) both arrive at the top vertices ($T_i$) by layer 368.
* Because the top joint spheres start forming at layer 350 (growing outward as a dome supported perfectly by the strut beneath it), the $T_i$ anchor points are fully solid and established by the time the top cable starts.
* However, the top cable runs *horizontally* between two top joints ($T_i \to T_{i+1}$) across a span of **43.30 mm**. 

**Why it's high risk:**
Because the cable is a 2.4 mm horizontal cylinder, the very first layer of that 43.3 mm bridge is not the full 2.4 mm width—it is a tiny "sliver" chord of the cylinder's bottom edge, only about ~0.96 mm wide (roughly two perimeters). Suspending a <1 mm wide strand of PETG across a 43 mm gap with no underlying mass is notoriously difficult. If that first strand sags or snaps, the subsequent layers of the cylinder will have nothing to adhere to, leading to a "spaghetti" failure of the top tension ring.

**Recommendations for the next iteration (single-piece, no supports):**

1. **Bridge tuning (Current orientation):** If you keep the flat orientation, you must ensure your bridge settings are dialed in for PETG. High cooling (100% fan) and specific bridge speeds are mandatory for that 43 mm span. 
2. **Increase cable diameter:** Bumping the `cable_d` from 2.4 mm to 3.0 mm or 4.0 mm will dramatically increase the width of that critical first bridge layer, giving the slicer more perimeters to anchor across the gap.
3. **Change orientation (Best mechanical fix):** Flat orientation forces the top cables to be 43 mm bridges and the struts to be columns. If you orient the prism so that **one of the struts lies perfectly flat on the build plate**, you eliminate the long 43 mm bridges entirely. The cables will instead print at steep diagonals (roughly 30°–60°), which modern slicers handle easily as self-supporting overhangs. This also aligns the layer lines *along* the cables rather than perpendicular to them, vastly increasing the tensile strength of the PETG tension members.
4. **Slicer settings discrepancy:** Note that your CLI-generated `.gcode.3mf` used 2 walls and 15% grid infill, whereas your GUI print is using 3 walls and 25% gyroid. Your GUI settings are much stronger, but ensure your headless pipeline is actually applying the overrides you expect.
