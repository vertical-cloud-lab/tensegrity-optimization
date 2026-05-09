"""Submit an Edison LITERATURE_HIGH query on strut material selection for the
multi-material 3D-printed tensegrity project (PLA vs PETG vs fiber-reinforced),
wait for completion, and persist the verbatim formatted answer (md), the full
structured response (json), and a references list (md).

Context: BYU MRG proposal — multi-material FDM tensegrity (currently PLA struts
+ TPU 95A tendons) for energy absorption, printed on a Bambu Lab H2D (IDEX).
Issue: "What is the right strut material? PLA vs. PETG vs. something else
(e.g., HF-reinforced), considering the difficulty of multi-material in this case."

Outputs (under edison-trajectories/):
  - strut-material-selection-<task_id>.md
  - strut-material-selection-<task_id>.json
  - strut-material-selection-<task_id>-references.md
"""

from __future__ import annotations

import json
from pathlib import Path

from edison_client import EdisonClient, JobNames

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "edison-trajectories"
OUT_DIR.mkdir(parents=True, exist_ok=True)

QUERY = r"""
We are designing a multi-material 3D-printed tensegrity-inspired energy-absorbing
structure for a BYU Mentored Research Grant. The current baseline uses PLA for
the rigid compression members (struts) and TPU 95A for the flexible tension
elements (tendons), co-printed in a single build on a Bambu Lab H2D (IDEX,
0.4 mm nozzle) FDM printer. Strut diameters are >= 2 mm, tendon diameters
1.2--6 mm. Loading regime is impact / energy-absorption (drop, compaction).

Question: What is the most appropriate filament for the rigid STRUT in this
multi-material FDM tensegrity, given the constraints below? Compare and
quantitatively rank the leading candidates and explicitly justify the
recommendation. Cite peer-reviewed sources wherever possible.

Candidates to compare (add others if the literature supports them):
  1. PLA (current baseline)
  2. PETG
  3. Short-fiber-reinforced filaments (e.g., PLA-CF, PETG-CF, PA-CF, PAHT-CF)
  4. Continuous-fiber-reinforced filaments (e.g., Markforged-style continuous
     CF / glass / Kevlar in a Nylon/Onyx matrix) -- noting that these typically
     require dedicated hardware (Markforged, Anisoprint), not a Bambu H2D
  5. Other engineering thermoplastics worth considering on an H2D
     (PA6-GF, PC, ABS, HIPS, ASA) if relevant
  6. "HF-reinforced" interpretations (Hemp Fiber? Hollow Fiber? Halloysite?
     High-Flow? please disambiguate the leading academic interpretation in
     this context and assess it)

Required comparison axes (please give numerical ranges with citations where
possible, not just qualitative claims):
  (a) Stiffness: tensile / flexural modulus (GPa) along the print direction
      and transverse, including knockdown vs. injection-molded reference
  (b) Strength: tensile / flexural / compressive strength (MPa); buckling
      capacity for slender struts (Euler / Johnson) given the modulus
  (c) Toughness / energy absorption per unit mass (J/g) under impact, and
      strain-rate sensitivity if reported
  (d) Density (g/cm^3) and resulting specific stiffness / specific strength
  (e) Glass-transition / heat-deflection temperature -- relevant for in-car
      / outdoor / sterilization use cases
  (f) UV / moisture / fatigue durability for repeated impact cycling
  (g) Print processability on a stock 0.4 mm nozzle FDM (warp, bed adhesion,
      stringing, required nozzle hardness, enclosure/chamber needs)
  (h) MULTI-MATERIAL INTERFACE STRENGTH WITH TPU 95A in a single co-printed
      build (this is the critical constraint -- many materials have poor
      adhesion to TPU). Cite any peer-reviewed lap-shear / pull-off / T-peel
      data or qualitative reports for PLA-TPU, PETG-TPU, PA-CF / TPU,
      and any fiber-reinforced / TPU pairing
  (i) Cost per kg and availability on Bambu AMS / H2D-compatible spools

Please then synthesize:
  1. A ranked recommendation (1st choice, 2nd choice, fallback) of strut
     material specifically for a PLA/PETG-vs-X strut + TPU 95A tendon
     tensegrity-inspired energy absorber printed on a Bambu Lab H2D.
  2. Whether moving from PLA to PETG (the immediately practical alternative)
     is justified by the literature, and what is gained / lost.
  3. Whether short-fiber CF/GF reinforcement (CF-PETG, CF-PLA, CF-PA) is
     worth the added cost, hardened-nozzle requirement, and possible
     reduction in interfacial adhesion to TPU.
  4. Whether continuous-fiber reinforcement is worth the platform change
     away from a Bambu H2D for this specific (energy-absorption / undergrad
     mentored-research) use case.
  5. Whether any cited multi-material study specifically used a PETG- (or
     fiber-reinforced-) strut + TPU tendon architecture, or if our work
     would be the first.

Please return numbered references at the end with DOIs where available so we
can ingest them into a BibTeX file.
""".strip()


def main() -> None:
    client = EdisonClient()
    task = {"name": JobNames.LITERATURE_HIGH, "query": QUERY}
    print("Submitting LITERATURE_HIGH task (blocking)...")
    responses = client.run_tasks_until_done(task)
    t = responses[0]
    task_id = getattr(t, "task_id", None) or getattr(t, "id", "unknown")
    print(f"Task complete. task_id={task_id}")

    stem = f"strut-material-selection-{task_id}"
    md_path = OUT_DIR / f"{stem}.md"
    json_path = OUT_DIR / f"{stem}.json"
    refs_path = OUT_DIR / f"{stem}-references.md"

    md_path.write_text(t.formatted_answer or "", encoding="utf-8")

    payload = json.loads(t.model_dump_json())
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Best-effort references extraction
    refs_lines = ["# References (extracted)\n"]
    for key in ("references", "bibliography", "citations"):
        val = payload.get(key)
        if val:
            refs_lines.append(f"## {key}\n")
            if isinstance(val, list):
                for i, r in enumerate(val, 1):
                    refs_lines.append(f"{i}. {r}")
            else:
                refs_lines.append(str(val))
            refs_lines.append("")
    if len(refs_lines) == 1:
        refs_lines.append(
            "(No structured references field returned; see the numbered "
            "References section at the bottom of the .md formatted answer.)"
        )
    refs_path.write_text("\n".join(refs_lines), encoding="utf-8")

    print(f"Wrote: {md_path}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {refs_path}")


if __name__ == "__main__":
    main()
