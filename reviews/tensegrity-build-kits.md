# Tensegrity Build-Kit & DIY-Materials Recommendations

> **Context.** Resolves the issue *"Feel free to buy tensegrity build kits for
> manual assembly."* The MRG project's primary fabrication path is multi-material
> FDM (PLA/PETG struts + TPU 85A tendons), but **physical hand-built models are
> still the fastest way to (a) build student/PI intuition for prestress and
> stability, (b) sanity-check a topology before committing print time, and
> (c) demo the project to reviewers, collaborators, and undergrads.** This doc
> lists kits that are worth buying off-the-shelf and a DIY bill-of-materials
> that lets the team rapidly hand-assemble arbitrary topologies (icosahedron
> 6-bar, 3-bar prism, Snelson-X, double-layer grids, etc.) outside the printer.
>
> **Prices below were fetched and verified against vendor pages on 2026-05-15.**
> All items fit inside the existing **Supplies** budget line
> ([`sections/budget.tex`](../sections/budget.tex), $1,000 over two years)
> without any reallocation.

---

## 1. Recommended commercial kits (rank-ordered for this project)

| # | Kit | Vendor | Verified price | Why it fits the MRG project |
|---|-----|--------|---------------:|------------------------------|
| 1 | **[Icosahedron Tensegrity Kit](https://www.tensegrityadventures.com/shop/p/icosahedron-tensegrity)** — 6 wood struts (9″ × ¼″), 24 elastic tendons, tendon assembly + removal tools | Tensegrity Adventures (direct) | **$27.00** (free US shipping) | Builds the **6-bar SUPERball / icosahedron** that anchors most of the project's drop-test and energy-absorption literature (Skelton; Zhang 2018). Same kit also makes a 2-strut cell pair, 5-strut prism, and 6-strut prism. Tendon tool + a [YouTube tutorial playlist](https://www.youtube.com/playlist?list=PLeHmdJdsrJ_8gA5egNpb9iIEjyut0JH8X) make it the lowest-friction way to onboard a new undergrad in <1 hr. **Buy 2–3** (one per student + one demo). |
| 2 | **[Tensologic Premium Kit](https://tensologic.com/products/)** — 12 long + 6 short pine sticks, 18 antimicrobial non-latex rubber bands, 24 PVC end-caps ([Amazon listing B091BFKXRR](https://www.amazon.com/dp/B091BFKXRR)) | PRODA TASARIM (Tensologic / Amazon) | **≈ $68 USD** (US$68 on eBay; £58.20 UK; AU$69.90; ¥12,642 JP) | 18-strut count covers prisms, 6-bar, **double-layer grids**, and Snelson-X demos with one kit. Heavier wooden dowels survive repeated assembly/disassembly during reading-group meetings. |
| 3 | **[Oriental Trading STEM Tensegrity Activity Pack](https://www.orientaltrading.com/stem-tensegrity-activity-learning-challenge-structure-stand-craft-kits-makes-12-a2-14474642.fltr)** — wood + self-adhesive foam + metal-tipped monofilament + rubber bands; makes 12 stands (≈ 4¼″ × 6″) | Oriental Trading | **$19.98** (was $21.99) for 12 | **Outreach use only:** UCUR booth, K-12 visits, ME open house. Cheap enough to give away to attendees. |
| 4 | **[UGEARS NASA Space Shuttle Discovery](https://ugears.us/products/ugears-nasa-space-shuttle-discovery)** — 1:96 wooden mechanical model with tensegrity "hover" stand | UGEARS US | **$68.99** | *Optional, lower priority.* Nice display piece for the lab; not directly research-relevant. Skip unless an outreach demo specifically needs it. |

**Suggested first purchase (≈ $122 total):** 2 × Icosahedron Adventures kits
($54.00) + 1 × Tensologic Premium ($68). Covers everything the team actually
needs to hand-assemble; everything else is DIY (Section 2).

> **Avoid for research purposes:** Clementoni "Floating Dragon," generic
> Walmart / "Wacky Company" / Amazon "anti-gravity table" novelty kits, and
> most Etsy decor kits. They are fixed-geometry novelty items with no usable
> strut count and non-standard connector geometry — fine as desk toys, useless
> for studying alternative topologies.

---

## 2. DIY bill-of-materials (build *any* topology, ≈ $40 one-time)

Off-the-shelf kits lock you into one or two topologies. For arbitrary
designs (3-bar prism, 4-bar, X-module, Pajunen truncated octa, double-layer
grids, etc.) the cheapest and most flexible option is a small DIY parts
inventory. Everything below is McMaster / Amazon / hardware-store stock.

### 2.1 Struts (compression members)

| Material | Spec | Use case | Indicative source |
|----------|------|----------|-------------------|
| **Birch hardwood dowels** | ⌀¼″ × 36″, cut to length | Default. Light, strong in compression, easy to drill end-caps or notch | Hardware store, ≈ $1.50 each |
| **Bamboo skewers / kebab sticks** | ⌀3 mm × 250 mm | Disposable rapid prototyping (3-bar prism, X-module) | Grocery store, ≈ $3 / 100 |
| **6061 Al tube** | ⌀⅜″ × 0.035″ wall × 36″ | Heavier, more realistic stiffness for instrumented benchtop demos | [McMaster 89965K85](https://www.mcmaster.com/89965K85/), ≈ $10 / ft |
| **CF rod** | ⌀3 mm × 1 m, pultruded | Stiff, light; good when you want to *not* be bottlenecked by strut buckling | Amazon / RC hobby, ≈ $4 each |

Cut all struts to a consistent length (e.g., 200 mm) so any strut can swap
into any topology. Lightly notch (or drill) ≈ 5 mm from each end for the
tendon to seat.

### 2.2 Tendons (tension members)

| Material | Spec | Notes |
|----------|------|-------|
| **Elastic shock cord** | ⌀1.5–2 mm braided polyester, ≈ $8 / 25 ft | Default. Easy to tie, forgiving prestress, color-coded options |
| **Latex / nitrile rubber bands** | #19 or #33 | Quick prototyping; replace often (UV/oil degrade them) |
| **Braided fishing line** | 30–50 lb test (Spectra/Dyneema) | Near-inextensible — use when you want the *kinematic* tensegrity (no spring response) |
| **TPU 85A printed tendons** | ⌀1.0–1.5 mm filament loops | Optional: gives a hand-build that uses the *same* tendon material as the printed specimens — useful for visualization |

### 2.3 Connectors / nodes

Three options, in order of cost vs. fidelity:

1. **Knots only** — tie the elastic directly into a loop around the strut
   end-notch. Fastest, $0.
2. **Mini cable ties / wire wraps** — anchor tendon ends with a 100 mm
   zip-tie around the strut. Tool-free.
3. **Printed PLA end-caps** with eyelet holes — STL takes <5 min to design;
   reuses the lab's existing FDM printers. Highest fidelity (matches the
   geometry of the Edison Phase-3/4 anchor-bulb / dovetail joints in
   `cad/joint-design/`).

### 2.4 Assembly tools (one-time)

- Small needle-nose pliers (required by the Adventures kit too)
- Razor saw or flush cutters (for trimming dowels)
- Digital calipers (already in lab)
- Tendon-tensioning tool (or improvise with a crochet hook)
- A printed paper template marking strut endpoints for the target topology
  (icosahedron / prism / X-module). Photocopy and reuse.

---

## 3. Suggested topologies to build first

These map 1-to-1 to the simulation / printed-design workflow already in the
proposal so a hand-built model exists for every key design family.

| Topology | # struts | # tendons | Why build it |
|----------|---------:|----------:|--------------|
| **3-bar T-prism** | 3 | 9 | Simplest stable tensegrity; first-day exercise |
| **6-bar icosahedron (SUPERball)** | 6 | 24 | Headline drop-test / energy-absorption topology |
| **Snelson X-module** | 4 | 12 | Building block of double-layer grids |
| **4-bar tensegrity prism** | 4 | 12 | Direct comparison to 3- and 6-bar |
| **Double-layer grid (2 × X-module)** | 8 | 24 | Demonstrates modularity — relevant to mat-style energy absorbers |
| **Truncated-octahedron (Pajunen 2019 impact cell)** | 12 | 36 | Stretch goal; matches Edison "design gaps" follow-up recommendation |

---

## 4. Budget impact

All of the above fits comfortably inside the existing $1,000 supplies
line in [`sections/budget.tex`](../sections/budget.tex):

- Commercial kits (recommended bundle: 2 × Icosahedron + 1 × Tensologic Premium): **≈ $122**
- DIY parts inventory (struts + tendons + connectors + tools): **≈ $40**
- **Total one-time spend: ≈ $162** (about 16% of the supplies budget, Year 1).

No budget reallocation or proposal edit is required; this is a normal
charge against "Filament, fasteners, consumables."

---

## 5. References / vendor links (verified 2026-05-15)

- Tensegrity Adventures — Icosahedron Kit ($27.00):
  <https://www.tensegrityadventures.com/shop/p/icosahedron-tensegrity>
- Tensegrity Adventures — assembly tutorials (YouTube playlist):
  <https://www.youtube.com/playlist?list=PLeHmdJdsrJ_8gA5egNpb9iIEjyut0JH8X>
- Tensologic (PRODA TASARIM) products page: <https://tensologic.com/products/>
- Tensologic Premium Kit (Amazon ASIN B091BFKXRR):
  <https://www.amazon.com/dp/B091BFKXRR>
- Oriental Trading — STEM Tensegrity Activity (item 14474642), $19.98 / 12 stands:
  <https://www.orientaltrading.com/stem-tensegrity-activity-learning-challenge-structure-stand-craft-kits-makes-12-a2-14474642.fltr>
- UGEARS US — NASA Space Shuttle Discovery ($68.99):
  <https://ugears.us/products/ugears-nasa-space-shuttle-discovery>
- McMaster-Carr aluminum tube 89965K85: <https://www.mcmaster.com/89965K85/>
- Skelton & de Oliveira, *Tensegrity Systems* (Springer, 2009) — canonical
  reference for the topologies in §3.
