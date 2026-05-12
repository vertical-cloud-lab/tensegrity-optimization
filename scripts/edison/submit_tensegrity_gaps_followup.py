"""Edison LITERATURE_HIGH follow-up: which major tensegrity design families
(canonical or non-canonical) are *missing* from the prior survey
(task fad054b3) and from the 13 STL design families we have built so far.

Prior coverage (PR #21):
  Snelson n-prisms (T3/T4/T6/stacked masts), Jessen icosahedron, expanded
  octahedron, truncated tetrahedron, Rimoli/Pajunen truncated-octahedron,
  Liu et al. cuboctahedron tessellation, Skelton class-k (T-bar/D-bar/
  class-2), Geiger/Levy cable-domes, biotensegrity (Levin/Ingber),
  tensegrity robots (NASA SUPERball v1/v2, Berkeley ULTRA-Spine, TT-3),
  deployable masts + patents (US 6,441,801; US 6,542,132; US 8,616,328),
  bistable double-prism (Intrigila 2022), Sabouni-Zawadzka simplex lattices,
  topology generation (Tibert/Pellegrino, GA, DNN, GNN).
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

# edison-client >= 0.12 reads EDISON_PLATFORM_API_KEY, not EDISON_API_KEY
os.environ.setdefault(
    "EDISON_PLATFORM_API_KEY", os.environ.get("EDISON_API_KEY", "")
)

from edison_client import EdisonClient, JobNames  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "edison-trajectories"
OUT_DIR.mkdir(parents=True, exist_ok=True)

QUERY = """This is a follow-up to Edison task `fad054b3-fef3-4249-a7d3-151d170efe19` (LITERATURE_HIGH, 2026-05-09, "tensegrity designs canonical or not").  That prior survey, together with the STL models we have now committed in `models/stl/` of github.com/vertical-cloud-lab/tensegrity-optimization, covers the following 13 design families:

(1) Snelson n-prism (T3 / T4 / T6) with stable twist theta = pi/2 - pi/n;
(2) Stacked T3 mast / Snelson "Needle Tower" (alternating chirality);
(3) Tibert & Pellegrino deployable mast (multi-bay alternating chirality);
(4) 6-strut tensegrity icosahedron rendered as Jessen's orthogonal icosahedron / expanded octahedron (SUPERball class);
(5) Rimoli & Pajunen truncated-octahedron tensegrity unit cell (energy-absorbing metamaterial);
(6) Liu, Zegard, Pratapa & Paulino (2019) cuboctahedron tensegrity tessellation;
(7) Geiger radial cable-dome (Seoul Olympic Hall / Georgia Dome topology);
(8) Levin / Flemons biotensegrity spine (stacked Jessen-icosahedron vertebrae; basis for Berkeley ULTRA-Spine);
(9) NASA SUPERball with inner payload icosahedron (planetary-lander robot);
(10) Knight, Duffy & Crane US Pat. 6,441,801 B1 hexagonal parallel-platform deployable antenna;
(11) Intrigila et al. (2022) bistable double-prism unit cell (Additive Manufacturing 57:102946);
(12) Skelton class-k (T-bar / D-bar / class-2 columns) -- documented but not built;
(13) Sabouni-Zawadzka simplex lattices -- documented but not built.

QUESTION
What other MAJOR tensegrity design families (canonical, non-canonical, recently published, or in patents / grey literature) are we still MISSING?  In particular, please identify families that:
(a) are mechanically or topologically *distinct* from the 13 above (i.e. not just a reparameterization of an n-prism or icosahedron);
(b) have at least one peer-reviewed or patented description with enough geometric detail (nodal coordinates, connectivity, prestress state) to be reconstructed as a parametric STL;
(c) would be plausibly relevant to a PETG-strut + TPU-tendon FFF-printed crutch-tip / impact-absorber project on a Bambu H2D printer, OR are otherwise canonical enough to be worth cataloguing for completeness.

For each missing family, please provide:
  - Canonical name and one-line description (what makes it distinct);
  - Original / definitive reference (paper, patent number, or technical report) with DOI / patent-office link where available;
  - Approximate counts (number of struts, number of cables, number of nodes for a minimal unit cell);
  - Whether the geometry is class-1, class-2, class-3, or "tensegrity-like" (struts touching);
  - Why we should care (mechanical property, application domain, mathematical interest);
  - If you know of an open-source code/CAD/STL release, name the repo or supplementary materials archive.

Please specifically check for, but do not limit yourself to, the following candidates that we suspect may be missing:
  - Snelson X-Module / X-tensegrity (the "Snelson cross") and Snelson planar-weave tensegrity;
  - Kenneth Snelson "Tetra-Tensegrity" and "V-Expander";
  - Motro 3-bar simplex with alternative cable patterns (saddle vs. diagonal);
  - Pugh's "diamond" and "zig-zag" patterns (Anthony Pugh, 1976, *An Introduction to Tensegrity*);
  - Class-2 / class-3 Skelton minimum-mass columns and beams;
  - C-bar / Y-bar / D-bar Skelton compound elements;
  - Burkhardt's "tetrahedron" and "octahedron" tensegrity (Tensegrity_gen);
  - Hexagonal anti-prism tensegrity (and other higher-rotational-symmetry tensegrities);
  - Tensegrity tori / Mobius tensegrities (Connelly & Whiteley 1996; Murakami 2001);
  - Class-theta double-helix DNA-like tensegrities;
  - Tensegrity catenoids / saddle-surface tensegrities (Hanaor 1992);
  - Hyperboloid / single-sheet ruled-surface tensegrities;
  - Geodesic-tensegrity hybrids (Motro's "tensegrity grids", Hanaor's double-layer tensegrity grids -- distinct from cable-domes);
  - Sabouni-Zawadzka 6V / 4V tensegrity Geodesic domes;
  - Sultan's "saddle tensegrity" and class-2 saddle masts;
  - Pneumatic / inflatable tensegrities (Kanchanasaratool & Williamson; rolling tensegrities);
  - Tensegrity wheels and rovers (Iscen TT-3, Caluwaerts TT-4);
  - Tensegrity robots beyond SUPERball: ULTRA-Spine v2/v3, ReCTeR, TT-Beam, Mountaineer, Vytas;
  - Anand 2022 biodegradable tensegrity (75 m drop survival);
  - Zhang 2018 / Zhang 2022 22" tensegrity (instrumented egg-drop, 60-65% peak-g reduction);
  - DNA / molecular tensegrities (Liedl et al. 2010);
  - Tensegrity-cytoskeleton models (Stamenovic, Ingber) -- biological;
  - 3D-printed monolithic tensegrities (Goh et al. 2022; Liu et al. 2024 4D-printed);
  - Auxetic tensegrity metamaterials (negative-Poisson's-ratio cells);
  - Bistable / multistable tensegrity beams beyond Intrigila (Schenk & Guest 2014; Micheletti 2022);
  - Origami-tensegrity hybrids ("tensegrity-augmented origami", Yasuda et al.);
  - Class-2 minimum-mass T-bar / D-bar Skelton bridges and roofs;
  - Tensegrity domes other than Geiger: Levy dome, Heki dome, Suspen-dome (Kawaguchi 1999);
  - Tensegrity bridges (Rhode-Barbarigos et al. 2010, "tensegrity-ring footbridge");
  - Tensegrity towers other than Snelson Needle Tower: Skelton's tensegrity tower, Sultan & Skelton 2003 tower;
  - Higher-class compound tensegrities: di-tensegrities, tri-tensegrities (Skelton & de Oliveira 2009 ch. 5);
  - Convex / non-convex hull tensegrities and "tensegrity star" forms;
  - Tensegrity arches and tensegrity barrel-vaults (Pellegrino-style);
  - Schek / Linkwitz force-density-method-generated free-form tensegrities;
  - Hawkins / Walker mechanism-based deployable tensegrities;
  - Class-1 tensegrity exoskeleton-like wearables (Hu & Skelton; Yin et al. 2024).

Please also flag anything published in 2023-2026 that didn't make the prior survey.

Where multiple variants of the same family exist, give the *most-distinct* one and note the variants briefly.  If you find more than ~10 missing families, please rank them by likely usefulness to our PETG+TPU/H2D impact-absorber project (best to worst), and call out which one is the single most-buildable next addition.
"""


def main() -> None:
    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY")
    if not api_key:
        raise SystemExit("EDISON_API_KEY / EDISON_PLATFORM_API_KEY not set in env")
    client = EdisonClient(api_key=api_key)
    task = {"name": JobNames.LITERATURE_HIGH, "query": QUERY}
    print("Submitting Edison LITERATURE_HIGH follow-up task...")
    submitted = client.create_task(task)
    task_id = submitted.task_id if hasattr(submitted, "task_id") else submitted
    print(f"task_id = {task_id}")

    # Poll for completion (LITERATURE_HIGH ~ 15-45 min)
    deadline = time.time() + 60 * 60  # 60-minute cap
    last_status = None
    while time.time() < deadline:
        t = client.get_task(task_id)
        status = getattr(t, "status", None) or getattr(t, "task_status", None)
        if status != last_status:
            print(f"[{time.strftime('%H:%M:%S')}] status = {status}")
            last_status = status
        if status and str(status).lower() in {"success", "completed", "failed", "error"}:
            break
        time.sleep(30)

    t = client.get_task(task_id)
    payload = json.loads(t.model_dump_json())
    base = OUT_DIR / f"2026-05-12-tensegrity-design-gaps-{task_id}"
    with open(str(base) + ".json", "w") as fh:
        json.dump(payload, fh, indent=2)
    formatted = getattr(t, "formatted_answer", None) or payload.get("formatted_answer") or ""
    with open(str(base) + ".md", "w") as fh:
        fh.write(formatted)
    print(f"wrote {base}.md ({len(formatted)} bytes), {base}.json")


if __name__ == "__main__":
    main()
