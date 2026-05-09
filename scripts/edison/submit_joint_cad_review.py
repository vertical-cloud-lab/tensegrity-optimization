#!/usr/bin/env python3
"""Submit a follow-up Edison ANALYSIS query attaching the 5 candidate-joint CAD
models, the rendered iso/section/comparison images, the curated public
reference images, and prior Edison Phase-2 followup trajectory.

Asks for visual review of the OpenSCAD geometry against the published prior
art and concrete CAD-refinement suggestions for the recommended primary
joint (B — co-printed dovetail/T-slot, per the `ce84ddf8` followup
reranking) before the first H2D PETG+TPU print.

Non-blocking submission: prints the task_id; the result file
`PHASE3-cad-review-SUBMITTED.json` records all attached file URIs so the
next session can fetch via the same task_id.
"""
from __future__ import annotations
import json, time
from pathlib import Path
from edison_client import EdisonClient, JobNames

REPO = Path(__file__).resolve().parents[2]
JD   = REPO / "cad" / "joint-design"
ED   = REPO / "edison-trajectories" / "joint-design"

PROMPT = """\
Goal: Visually + technically review the five candidate PETG+TPU joint CAD
models (attached as a zipped `cad/joint-design/` directory containing the
five `*.scad` source files and the rendered iso + section + side-by-side
reference comparison PNGs) against the already-completed Edison Phase-1
(5x LITERATURE), Phase-2 (LITERATURE_HIGH be6768ab + ANALYSIS c38a2046)
and the followup ANALYSIS ce84ddf8 (attached). Recommend concrete,
dimensioned CAD refinements for the new primary recommendation
**Design B — Co-printed Dovetail / T-Slot** (current geometry: slot
mouth 6.4 mm, slot inner 7.4 mm, depth 5.0 mm, flank 25 deg, clearance
0.25 mm/face, node 12 mm, strut 6 mm, cable 2.4 mm) for the first PETG
(struts) + TPU (cables) multi-material print on a Bambu Lab H2D IDEX
(0.4 mm nozzle, 0.20 mm layers, >=3 perimeters, manual filament map).

Attached artifacts (already on the data store):

1. cad-joint-design.zip — full cad/joint-design/ directory: 5 .scad
   source files (A_anchor_bulb, B_dovetail, C_tpu_sleeve_overmold,
   D_eyelet_loop, E_tpu_rebar), 4 _section.scad cutaway models,
   _common.scad shared parameters, render.sh, and renders/ containing
   13 PNG renders (iso + section_iso) plus 5 STL files plus three
   contact-sheet montages (all_iso_montage.png, all_section_montage.png,
   all_compare_montage.png), plus references/ containing the
   verified-200 Wikimedia/DOI links README and 5 downloaded JPEG
   reference images.
2. analysis-followup-ce84ddf8.md — the followup Edison ANALYSIS that
   inverted the primary recommendation from E (rebar) to B (dovetail).
3. joint-design-README.md — the existing synthesis README contrasting
   the two Phase-2 rankings.
4. task-manifest.json — full submission ledger.

Please answer the following, structured as numbered sections, with cited
references at the end:

(1) Visual sanity check — for each of the 5 designs (A bulb, B dovetail,
    C TPU sleeve, D eyelet+loop, E rebar), comment on whether the
    OpenSCAD geometry (see iso + section + compare_*.png views) is a
    faithful realization of the *intent* described in the corresponding
    Phase-1 reply. Flag any geometry that looks wrong, under-constrained,
    or not printable on H2D PETG+TPU.

(2) CAD refinements for Design B (the new primary) — recommend concrete
    dimensional changes (slot/head/clear/flank/depth/cable
    routing/print orientation), if any, to the values above. Cite
    Ermolai 2024, Zhang 2021, Frascio 2024 (and any newer published
    work) for each recommended value. Pay particular attention to:
      (a) optimal flank angle range for a print-in-place captive
          dovetail in PETG/TPU (we use 25 deg — Zhang 2021 Fig.6 was
          20-30 deg),
      (b) clear/face value (we use 0.25 mm — Ermolai 2024 reports
          0.15-0.30 mm depending on Z-orientation),
      (c) print orientation (slot-axis horizontal vs. vertical —
          affects interlayer adhesion at load-bearing flanks),
      (d) any anti-warp / stress-relief feature recommendations
          (chamfers, fillets at slot mouth, etc.).

(3) CAD refinements for Design A (the new backup) — concrete dimensional
    changes to the 9 mm node + 3.0 mm bore + 5.0 mm bulb geometry.
    Specifically: minimum bulb-to-bore-clear ratio for captive retention
    without bulb pull-through.

(4) Drop-test screening matrix update — does the inversion to B-primary
    / A-backup change the previously-recommended 12-specimen Lansmont
    M23 + Polytec QTec drop matrix (`crutch_tip` regime + `nasa_lander`
    regime, 2 cell sizes x 3 drop heights x 2 replicates)? If so,
    propose the updated matrix.

(5) Bibliographic gaps — list any directly-relevant publications from
    2024-2026 on FDM dovetail / T-slot multi-material joints, PETG+TPU
    interfacial adhesion, or print-in-place captive joints that the
    previous Phase-2 outputs missed.

Constraints:
- Use the attached files (do NOT re-derive design geometry from scratch).
- Cite every quantitative claim against either an attached artifact or a
  peer-reviewed reference (DOI). Place References at the end as a
  numbered list.
- Be concrete: recommend dimension values in mm, angles in degrees, and
  print parameters as Bambu Studio profile keys. Avoid vague phrasing
  like "consider" or "may want to."
"""


def main() -> None:
    client = EdisonClient()

    print("Uploading cad/joint-design/ as a zipped collection ...", flush=True)
    cad_resp = client.store_file_content(
        name="cad-joint-design",
        file_path=str(JD),
        description=(
            "Full cad/joint-design/ directory: 5 OpenSCAD source files for "
            "candidate joint designs A-E, 4 section/cutaway models, "
            "_common.scad shared params, render.sh, 13 PNG renders + 5 STL "
            "+ 3 contact-sheet montages, references/README.md with verified "
            "Wikimedia/DOI links and 5 JPEG reference images."
        ),
        as_collection=True,
        ignore_patterns=["__pycache__", "*.pyc"],
    )
    cad_uri = f"data_entry:{cad_resp.data_storage.id}"
    print(f"  cad zip URI: {cad_uri}", flush=True)

    followup_md = ED / "PHASE2-analysis-followup-ce84ddf8-5930-4c61-a6ce-65cf9ee3a6fa.md"
    print(f"Uploading {followup_md.name} ...", flush=True)
    followup_resp = client.store_file_content(
        name="analysis-followup-ce84ddf8",
        file_path=str(followup_md),
        description=(
            "Followup ANALYSIS (Edison task ce84ddf8) — re-ran c38a2046 "
            "with all 5 Phase-1 outputs attached, which inverted the "
            "primary-joint recommendation to B (dovetail) over E (rebar)."
        ),
    )
    followup_uri = f"data_entry:{followup_resp.data_storage.id}"
    print(f"  followup URI: {followup_uri}", flush=True)

    readme_resp = client.store_file_content(
        name="joint-design-README",
        file_path=str(ED / "README.md"),
        description=(
            "Synthesis README contrasting the two Phase-2 rankings "
            "(prior-art vs best-for-us) and giving the original "
            "primary/backup recommendation."
        ),
    )
    readme_uri = f"data_entry:{readme_resp.data_storage.id}"
    print(f"  README URI: {readme_uri}", flush=True)

    manifest_resp = client.store_file_content(
        name="task-manifest",
        file_path=str(ED / "task_manifest.json"),
        description=(
            "task_manifest.json — full ledger of every Edison task "
            "submitted in this joint-design batch and which files "
            "were attached to each."
        ),
    )
    manifest_uri = f"data_entry:{manifest_resp.data_storage.id}"
    print(f"  manifest URI: {manifest_uri}", flush=True)

    files = [cad_uri, followup_uri, readme_uri, manifest_uri]

    task = {"name": JobNames.ANALYSIS, "query": PROMPT}
    print("Submitting ANALYSIS task ...", flush=True)
    task_id = client.create_task(task, files=files)
    print(f"\nSUBMITTED task_id = {task_id}\n", flush=True)

    out = ED / "PHASE3-cad-review-SUBMITTED.json"
    out.write_text(json.dumps({
        "task_id": task_id,
        "name": "ANALYSIS",
        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "attached_files": {
            "cad-joint-design.zip": cad_uri,
            "analysis-followup-ce84ddf8.md": followup_uri,
            "joint-design-README.md": readme_uri,
            "task-manifest.json": manifest_uri,
        },
        "purpose": (
            "Visual + technical CAD review against published prior art; "
            "request concrete dimensional refinements for the new "
            "primary (Design B — dovetail) and backup (Design A — "
            "anchor-bulb) before the first H2D PETG+TPU multi-material print."
        ),
    }, indent=2) + "\n")
    print(f"Wrote {out}", flush=True)


if __name__ == "__main__":
    main()
