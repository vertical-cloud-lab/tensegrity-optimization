#!/usr/bin/env python3
"""Phase-4 dual Edison submission (PR comment 4427608763, @sgbaird-yolo):

  (1) LITERATURE_HIGH — project-context recommendation. Given the now-fetched
      Phase-1/2/3 outputs *and* the project-context constraints (PLA per #45,
      TPU 85A, omnidirectional egg-drop / planetary-lander demo per #16, H2D
      IDEX), which single joint design (A-E) is the right choice and what is
      the exact dimensional spec to print first?

  (2) ANALYSIS — vision review using INDIVIDUAL panels and INDIVIDUAL
      cross-section tiles for A-E (no merged mosaics — the prior mosaics
      hindered the vision model). Specifically asks the model to check
      whether D-eyelet's "two-rings-printed-into-each-other" chain-link
      topology and B-dovetail's slot-axis cable continuity actually read
      correctly from the per-design iso + section_{X,Y,Z} tiles.

Both submissions are non-blocking; task IDs are recorded in
edison-trajectories/joint-design/PHASE4-{context,vision}-SUBMITTED.json so
the next session can fetch via the same task IDs.
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

from edison_client import EdisonClient, JobNames

REPO = Path(__file__).resolve().parents[2]
JD = REPO / "cad" / "joint-design"
RD = JD / "renders"
ED = REPO / "edison-trajectories" / "joint-design"

DESIGNS = ["A_anchor_bulb", "B_dovetail", "C_tpu_sleeve_overmold",
           "D_eyelet_loop", "E_tpu_rebar"]

CONTEXT_PROMPT = """\
Goal: Given the now-fetched joint-design Edison trajectories for the H2D
multi-material PETG/PLA + TPU 85A tensegrity project, and the project's
specific application context, recommend ONE joint design (A-E) as the
single first-print recommendation, plus a one-paragraph rationale.

Project-context constraints to weight heavily:

(a) Strut material has been switched from PETG to PLA per repo issue #45
    (PETG/PLA-TPU interface data: peer-reviewed PLA-TPU figures exist
    (Lopes 2018, Zhang 2026, Ruwais 2025: butt 6.5 MPa, alt-deposition
    7.4 MPa, mech-interlock shear ~24 MPa); peer-reviewed PETG-TPU
    figures do NOT exist).

(b) TPU is 85A (NinjaFlex-class, NOT 95A): E approx 12 MPa secant,
    sigma_break approx 26 MPa, ~2x softer per unit cross-section than
    TPU 95A. Use this for any FFF-tendon stiffness derivation
    k = E*A/L.

(c) Lead demo per repo issue #16 is a drag-free omnidirectional egg-drop
    / planetary-lander (NASA SUPERball-lineage 6-bar tensegrity + TPU
    85A payload cradle, m_sys <= 500 g, m_egg = 55 +/- 5 g, bounding
    sphere D = 200 mm, rigid concrete floor per ASTM D5276, n>=20
    Bruceton drops, FoM h_crit + N_reuse). Worst-case AND random
    orientations — joints see arbitrary incident tendon angles.
    See egg-drop-tensegrity-1b90208d.md and egg-drop-followup-f41b7034.md.

(d) Printer is Bambu Lab H2D IDEX (0.4 mm nozzle, 0.20 mm layer,
    >=3 perimeters, manual filament map).

(e) Five candidate joints, refined per Edison Phase-3 (task 19e0c868)
    against published prior art:
      A — Anchor-bulb spherical node: node 9.5, bore 2.8, bulb 4.8 mm
          (1.71x pull-through ratio).
      B — Co-printed dovetail/T-slot: node 12.0, slot_mouth 5.4,
          slot_inner 7.06, slot_height 4.0, slot_depth 6.0, flank 22.5
          deg, clear_lat 0.20, clear_roof 0.30, mouth_fillet 0.5 mm.
      C — TPU sleeve overmold (Ye 2023 / Khatri 2024 wrap).
      D — Captive TPU loop through PETG/PLA eyelet (chain-link only —
          two rings printed into each other, linking number +/-1, with
          0.30 mm print-in-place clearance and 2-3 mm of slack/deadband
          before tension transmits).
      E — Embedded TPU rebar (Yavas 2022 1-2.7 MPa rebar-shear analog).

(f) Phase-2/3 ranking history (already fetched on disk):
    - LITERATURE_HIGH be6768ab (prior art only): B > C > D > A > E.
    - ANALYSIS c38a2046 (only 3/5 Phase-1 attached): E > A > B > C > D.
    - ANALYSIS ce84ddf8 (all 5 Phase-1 attached): B > A > E > C > D.
    - Phase-3 19e0c868: refined B and A dimensions; otherwise the
      ranking ce84ddf8 stands.
    - Current PR recommendation: B primary for the uni-axial crutch-tip
      print, A primary for the omnidirectional lander/egg-drop print.

Question (be concrete; cite every quantitative claim against an
attached file or peer-reviewed DOI):

(1) Pick ONE design (A-E) as the single first-print recommendation
    given (a)-(f). Justify in <=200 words.

(2) Give the exact printable dimension table for that design (node,
    bore, bulb / slot, flank, clear, fillet — whichever apply) for
    PLA + TPU 85A on H2D, including any deviations from the Phase-3
    refined values above. Material substitution matters: PLA's higher
    glass-transition (~60 deg C vs PETG's ~80) and lower impact
    resistance may shift the optimum.

(3) Print recipe (Bambu Studio profile keys): nozzle, layer height,
    perimeter count, infill %, supports, filament map, and print
    orientation (slot-axis vs strut-axis vertical).

(4) Bruceton n>=20 success criterion: estimated h_crit (m), N_reuse
    (drops to first joint failure), and dominant failure mode for the
    recommended joint at the m_sys, m_egg, D constraints above.

(5) Single sentence — what would you change in (1)-(4) if the project
    instead returned to PETG struts (i.e. #45 is reverted)?
"""

VISION_PROMPT = """\
Goal: Vision-only sanity check of the five candidate joint OpenSCAD
models. Each design's geometry is attached as FOUR INDIVIDUAL PNG tiles
(iso + section_X + section_Y + section_Z, never merged) plus the
corresponding .scad source, so the vision model can read each panel at
full resolution.

The two designs the PR reviewer flagged as visually confusing
(comment 4427608763) are B and D:

  - B — Co-printed dovetail / T-slot: the reviewer accepts the
        current B geometry but wants per-panel confirmation that the
        TPU cable head, the PETG/PLA slot, and the cable exiting the
        +X face of the node are all mechanically continuous (no
        air-gap, no floating geometry, no impossible overhang for FDM
        with the slot-axis printed horizontally).

  - D — Captive TPU loop through PETG/PLA eyelet: the reviewer asks
        "is this like printing two rings into each other?" — i.e. is
        the geometry actually chain-link (linking number +/-1) between
        an orthogonal PETG/PLA eyelet ring (axis along Y) and a TPU
        loop (axis along X) threaded through it ONCE, with the cable
        tangent on the +X side of the loop? In the rendering the loop
        appears partially detached from the eyelet — that is in fact
        the intended chain-link topology (the two rings are
        mechanically separate; they only constrain each other
        topologically). Please confirm.

Attached individual tiles (per design, 4 PNGs each):
  - {design}_iso.png            — perspective view, no cut
  - {design}_section_X_iso.png  — cut by plane X = 0
  - {design}_section_Y_iso.png  — cut by plane Y = 0
  - {design}_section_Z_iso.png  — cut by plane Z = -2

Also attached: 5 .scad source files (one per design) and the
_common.scad shared parameter file. No mosaics, no zip — every PNG is a
separate data_entry so the vision model can read each at full DPI.

Please answer per design (A, B, C, D, E), one section each, in this
order:

(i)   Does the iso view match the verbal description of the design's
      intent? (One sentence pass/fail.)

(ii)  From section_X, section_Y, section_Z, identify any non-physical
      geometry: floating bodies, missing material between named
      features, impossible-to-print overhangs (assuming the print
      orientation called out in the comment header of the .scad file),
      or interpenetration of PETG/PLA and TPU bodies. Be specific —
      cite the section plane that exposed the issue.

(iii) For B specifically: confirm the dovetail head, the slot, and the
      cable exit on the +X face of the node are all mechanically
      continuous in at least one of the three section planes.

(iv)  For D specifically: confirm (or refute) that the geometry is
      chain-link / "two rings printed into each other" topology
      (linking number +/-1) between the PETG/PLA eyelet (ring axis
      along Y) and the TPU loop (ring axis along X). If you cannot
      confirm from the section tiles, name which additional cut plane
      would unambiguously show the chain-link.

(v)   Print-orientation recommendation for each design (slot-axis or
      strut-axis vertical) given FDM-on-H2D constraints.

Constraints:
- Reference each finding by the specific PNG filename you read it from.
- If a tile renders ambiguously, say "tile ambiguous, recommend
  additional cut plane at <X|Y|Z>=<value>" instead of guessing.
"""


def upload_file(client: EdisonClient, name: str, path: Path,
                description: str) -> str:
    resp = client.store_file_content(
        name=name, file_path=str(path), description=description,
    )
    return f"data_entry:{resp.data_storage.id}"


def main() -> None:
    api_key = (os.environ.get("EDISON_PLATFORM_API_KEY")
               or os.environ.get("EDISON_API_KEY"))
    client = EdisonClient(api_key=api_key)

    # -----------------------------------------------------------------
    # (1) LITERATURE_HIGH — project-context recommendation
    # -----------------------------------------------------------------
    print("\n=== (1) LITERATURE_HIGH project-context recommendation ===",
          flush=True)
    context_files: list[str] = []
    context_files.append(upload_file(
        client, "joint-design-README", ED / "README.md",
        "Synthesis README — Phase-1/2/3 rankings, lander-context, PLA note.",
    ))
    context_files.append(upload_file(
        client, "task-manifest", ED / "task_manifest.json",
        "Ledger of every Edison task submitted in this joint-design batch.",
    ))
    context_files.append(upload_file(
        client, "phase3-cad-review", ED /
        "PHASE3-cad-review-19e0c868-3587-440d-ba4a-07da4dddf99a.md",
        "Phase-3 ANALYSIS that refined B and A dimensions against prior art.",
    ))
    # egg-drop benchmark file lives on the lander branch; not required —
    # the prompt already embeds the relevant constraints inline.
    print(f"  uploaded {len(context_files)} context files", flush=True)

    context_task_id = client.create_task(
        {"name": JobNames.LITERATURE_HIGH, "query": CONTEXT_PROMPT},
        files=context_files,
    )
    print(f"  SUBMITTED context task_id = {context_task_id}", flush=True)

    (ED / "PHASE4-context-SUBMITTED.json").write_text(json.dumps({
        "task_id": context_task_id,
        "name": "LITERATURE_HIGH",
        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "attached_files": context_files,
        "purpose": (
            "Project-context-aware single-joint recommendation "
            "(PLA per #45, TPU 85A, lander/egg-drop per #16, H2D)."
        ),
    }, indent=2) + "\n")

    # -----------------------------------------------------------------
    # (2) ANALYSIS — individual panel + cross-section vision review
    # -----------------------------------------------------------------
    print("\n=== (2) ANALYSIS per-design individual panel vision review ===",
          flush=True)
    vision_files: list[str] = []
    for design in DESIGNS:
        # SCAD source
        scad = JD / f"{design}.scad"
        if scad.exists():
            vision_files.append(upload_file(
                client, f"{design}-scad", scad,
                f"OpenSCAD source for design {design[0]} ({design}).",
            ))
        # iso + 3 section tiles
        for view in ["iso", "section_X_iso", "section_Y_iso",
                     "section_Z_iso"]:
            png = RD / f"{design}_{view}.png"
            if png.exists():
                vision_files.append(upload_file(
                    client, f"{design}-{view}", png,
                    (f"Individual tile, design {design[0]}, view {view} — "
                     "full-DPI PNG (not merged into a mosaic)."),
                ))
    # Common params + readme for context
    vision_files.append(upload_file(
        client, "_common-scad", JD / "_common.scad",
        "Shared OpenSCAD parameters (strut_d, cable_d, etc.).",
    ))
    vision_files.append(upload_file(
        client, "joint-design-README-v", ED / "README.md",
        "Synthesis README — has design intent + print-orientation notes.",
    ))
    print(f"  uploaded {len(vision_files)} individual tiles + .scad files",
          flush=True)

    vision_task_id = client.create_task(
        {"name": JobNames.ANALYSIS, "query": VISION_PROMPT},
        files=vision_files,
    )
    print(f"  SUBMITTED vision task_id = {vision_task_id}", flush=True)

    (ED / "PHASE4-vision-SUBMITTED.json").write_text(json.dumps({
        "task_id": vision_task_id,
        "name": "ANALYSIS",
        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "attached_files": vision_files,
        "purpose": (
            "Per-design individual tile vision review (no mosaics) — "
            "confirm B cable continuity and D chain-link topology."
        ),
    }, indent=2) + "\n")

    print("\nDONE. Two non-blocking tasks submitted:", flush=True)
    print(f"  context  task_id: {context_task_id}", flush=True)
    print(f"  vision   task_id: {vision_task_id}", flush=True)


if __name__ == "__main__":
    main()
