# Visual reference images for the five candidate joint designs

This file lists curated public-domain or open-access reference images and
publication figures matching each of the five candidate PETG+TPU joint
designs explored under `edison-trajectories/joint-design/`. The intent is
to let a human reviewer **visually compare** our OpenSCAD models in
`cad/joint-design/renders/` against published / community examples of
similar geometry.

> **Caveat.** Most of the directly-relevant peer-reviewed figures
> (Pajunen 2019, Ermolai 2024, Yavas 2022, Mortensen 2025, Khatri 2024,
> Ye 2023) are behind publisher paywalls or in pre-publication state. For
> those, only the DOI / landing page is linked here — if you have
> institutional access, the figures referenced in the Edison trajectories
> are the canonical visual benchmarks. Where a fully-open analog exists
> (Wikimedia, arXiv preprint, GitHub repo), it is linked directly.

---

## A — Anchor-bulb spherical node

| URL | Caption | Source |
| --- | --- | --- |
| <https://commons.wikimedia.org/wiki/File:Tensegrity_3-Prism.jpg> | Photograph of a 3-strut tensegrity prism — the exact topology our PETG sphere-with-bores anchors at each of the 6 vertices. The cable termination bulbs visible at each end are the macroscopic analog of our printed-in-place TPU bulb. | Wikimedia Commons |
| <https://commons.wikimedia.org/wiki/File:NASA_SUPERball_Tensegrity_Lander_Prototype.jpg> | NASA SUPERball tensegrity lander prototype — directly relevant to the `nasa_lander` regime in our drop-test matrix; visible spherical end-caps and cable terminations are the macroscale analog of Design A. | Wikimedia Commons |
| <https://commons.wikimedia.org/wiki/File:Icosahedral_tensegrity_structure.png> | Icosahedral tensegrity rendering — useful for visualising the multi-cable-per-node loading pattern that an anchor-bulb joint must redirect. | Wikimedia Commons |
| <https://doi.org/10.1016/j.matdes.2019.107839> | Pajunen et al. 2019, *Materials & Design* — SLS PA2200 spherical tensegrity nodes; figures show the spherical-node-with-through-bores geometry directly (cited from Edison `0b5d7ba2-…`). | DOI landing page (paywalled) |

## B — Co-printed dovetail / T-slot mechanical interlock

| URL | Caption | Source |
| --- | --- | --- |
| <https://commons.wikimedia.org/wiki/File:Finished_dovetail.jpg> | Finished wood-joinery dovetail — exactly the wide-bottom, narrow-mouth captive profile our `B_dovetail.scad` extrudes (slot mouth 6.4 mm, slot inner 7.4 mm, depth 5.0 mm, flank 25°). | Wikimedia Commons |
| <https://commons.wikimedia.org/wiki/File:EB1911_Joinery_-_Fig._3.%E2%80%94Dovetails.jpg> | Encyclopædia Britannica 1911 dovetail-joint cross-section diagram — useful as the canonical engineering drawing of the through-dovetail captive geometry. | Wikimedia Commons, public domain |
| <https://doi.org/10.3390/polym16040497> | Ermolai et al. 2024, *Polymers* — multi-material FDM mechanical interlocks (T-slot / dovetail) for PLA+TPU; reports 6–11 MPa tensile and up to 24 MPa shear strength. Figures 3–6 are the closest published match to our B geometry (cited from Edison `ccb7b854-…`). | DOI landing page |
| <https://doi.org/10.1016/j.matdes.2021.109612> | Zhang et al. 2021, *Materials & Design* — T-shape and dovetail hierarchical interlock geometries for multi-material FFF. | DOI landing page |

## C — TPU overmolded sleeve over knurled / grooved rigid tip

| URL | Caption | Source |
| --- | --- | --- |
| <https://commons.wikimedia.org/wiki/File:Hose_clamp.jpg> | Hose clamp on a barbed fitting — the macroscale analog of TPU hoop-tension over a grooved/knurled PETG strut tip; the alternating ribs and clamp wrap are the visual reference for our `C_tpu_sleeve_overmold.scad`. | Wikimedia Commons |
| <https://commons.wikimedia.org/wiki/File:Two_spring_Hose_Clamps_-_small.jpg> | Spring hose clamp — closest visual analog to a TPU sleeve providing constant hoop tension over a barbed fitting (rather than a discrete clamping screw). | Wikimedia Commons |
| <https://doi.org/10.3390/polym15102275> | Ye et al. 2023, *Polymers* — PETG+TPU multi-material wrap; figures show the hoop-tensioned overmold geometry (cited from Edison `5a7ffce4-…`). | DOI landing page |

## D — Captive TPU loop through PETG eyelet (chain-link)

| URL | Caption | Source |
| --- | --- | --- |
| <https://commons.wikimedia.org/wiki/File:Chain_Link_Fence.jpg> | Chain-link fence — the topological constraint our PETG eyelet + TPU loop replicates: each link is captive in the next without bonding. The 0.25–0.35 mm clearance our `D_eyelet_loop.scad` leaves is the print-in-place analog. | Wikimedia Commons |
| <https://www.printables.com/search/models?q=print+in+place+chain> | Printables.com community library of "print-in-place chain" models — visual reference for the PETG eyelet ring + captive flexible loop assembly and for the typical clearance values needed to avoid fusing. | Printables, hobbyist license varies |
| <https://doi.org/10.1016/j.addma.2024.104419> | Mortensen 2025 (preprint citation in Edison `727a449d-…`), *Additive Manufacturing* — PETG+TPU loop-on-pin print-in-place captive joints. | DOI landing page (in-press) |

## E — TPU "rebar" embedded in PETG strut tip (barbed / smooth)

| URL | Caption | Source |
| --- | --- | --- |
| <https://commons.wikimedia.org/wiki/File:Rusty_rebar_nets.jpg> | Steel rebar net before pour — the load-transfer analogy our `E_tpu_rebar.scad` realizes at FDM scale: load is transferred from the embedded element to the surrounding rigid matrix via interface shear and (when barbed) mechanical interlock. | Wikimedia Commons |
| <https://commons.wikimedia.org/wiki/File:Loop_of_rebar_sticking_out_of_concrete.jpg> | Rebar loop projecting from cured concrete — direct visual reference for the embed-and-emerge geometry of TPU passing into and out of a PETG strut tip. | Wikimedia Commons |
| <https://commons.wikimedia.org/wiki/File:Anchor_bolt_with_anchor_plate.svg> | Anchor-bolt SVG diagram — macroscale barbed-pullout analog with asymmetric flanks (sharp pull-out face, shallow insertion face), matching the 35° / 55° asymmetric-flank geometry in our barb cross-section. | Wikimedia Commons, public domain |
| <https://doi.org/10.1016/j.compositesa.2022.107023> | Yavas et al. 2022, *Composites Part A* — shell-core lattices with embedded compliant inserts (1.0–2.7 MPa interfacial shear); the closest published prior art for E (cited from Edison `ae373eb5-…` and the LITERATURE_HIGH `be6768ab-…`). | DOI landing page |

---

## How these references were chosen

Edison Phase-1 and Phase-2 trajectories (`edison-trajectories/joint-design/`)
already cite the peer-reviewed papers by full DOI in their `formatted_answer`
and `references` sections; the table above adds **at least one
publicly-viewable Wikimedia / community image per design** so a reviewer
can compare our OpenSCAD geometry against an everyday or canonical visual
example without hitting a paywall.

If a link above 404s or the publisher has moved a paper, the canonical
reference of record is the DOI plus the citation as captured in the JSON
sidecar of the corresponding Edison task (`*-{taskid}.json`).
