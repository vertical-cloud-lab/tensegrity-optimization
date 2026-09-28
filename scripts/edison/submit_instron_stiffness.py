"""Submit a high-effort Edison LITERATURE_HIGH query on Instron stiffness
testing best practices and applicable ASTM standards for the multi-material
3D-printed (PETG/PLA struts + TPU 85A tendons) tensegrity-inspired structures
in this repository.

Triggered by issue #49: "Run initial instron tests for stiffness testing".

The script is non-blocking by default: it submits the task, polls for a
bounded period, and writes whatever artifact is available to
``edison-trajectories/instron-stiffness/``.  Re-running the script after the
task completes will fetch and overwrite the placeholder with the final answer.

Auth note: edison-client >= 0.12 reads ``EDISON_PLATFORM_API_KEY``; we shim
``EDISON_API_KEY`` to that name for backward compatibility with the
copilot-instructions documentation.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# ---- Auth shim -------------------------------------------------------------
if "EDISON_API_KEY" in os.environ and "EDISON_PLATFORM_API_KEY" not in os.environ:
    os.environ["EDISON_PLATFORM_API_KEY"] = os.environ["EDISON_API_KEY"]

from edison_client import EdisonClient, JobNames  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "edison-trajectories" / "instron-stiffness"
OUT_DIR.mkdir(parents=True, exist_ok=True)

QUERY = """
We are kicking off the **first round of Instron stiffness tests** for a
multi-material 3D-printed *tensegrity-inspired* unit-cell program (BYU
Mentored Research Grant; PIs Hill & Baird; repo
``vertical-cloud-lab/tensegrity-optimization``; tracking issue #49). The
overall campaign is a closed-loop **design -> print -> test -> Bayesian
optimization** workflow targeting energy-absorption / cushioning
applications (impact-protective gear, packaging, planetary-lander egg-drop
analog). Initial tests are *quasi-static* on an Instron-class screw-driven
load frame; later phases add drop-weight impact and (potentially) wave
propagation.

**Specimens (initial batch):**
* Architecture: Snelson-class 3-bar / 6-bar tensegrity prisms and
  tensegrity-inspired truncated-octa / icosa unit cells, single cell and
  small (2x2x2) tilings. Bounding cube ~25-50 mm, mass ~5-30 g.
* Materials: rigid struts in **PETG** (E ~= 2 GPa, sigma_b ~= 50 MPa,
  rho ~= 1.27 g/cc) — also PLA as a baseline; tension elements in **TPU 85A**
  (NinjaFlex-class, secant E ~= 12 MPa, sigma_b ~= 26 MPa, strain-to-break
  ~600 %, rho ~= 1.20 g/cc). Co-printed multi-material on a Bambu H2D dual-
  toolhead FFF system (0.4 mm nozzle, layer 0.2 mm, 3-perimeter min on TPU
  tendons -> minimum tendon Ø 1.2 mm, strut Ø ≥ 2.0 mm).
* Joinery between PETG and TPU follows the joint-design study in this repo
  (anchor-bulb / dovetail / TPU-rebar variants); peer-reviewed PETG–TPU
  interface strength data does **not** exist, so joint integrity is itself
  an experimental unknown.

**What we want from this query (be specific and prescriptive):**

1. **Applicable ASTM / ISO standards** for stiffness characterization of
   this exact specimen class.  For each, please give the standard number,
   title, what it actually measures, sample-geometry requirements,
   strain-rate / crosshead-speed requirements, and the *gap* between the
   standard and our 3D-printed cellular tensegrity-inspired specimens (i.e.
   what we have to adapt or report as a deviation).  Please cover at minimum:
     * **Bulk plastic compression** (ASTM D695, ISO 604) — for PETG/PLA
       coupons that bracket the strut material;
     * **Cellular / cushioning compression** (ASTM D1621, ASTM D3574,
       ASTM D7726, ASTM F1614, ASTM D575/ISO 7743 for rubber-like cells) —
       these are the closest analogs to a tensegrity unit cell;
     * **Sandwich-core / lattice compression** (ASTM C365, ASTM C297) for
       through-thickness modulus of repeating unit cells;
     * **Polymer tension** (ASTM D638, ISO 527) and **elastomer tension**
       (ASTM D412, ISO 37) for material-card coupons of PETG and TPU 85A
       (FFF-printed, with build-orientation reporting per ASTM F2971 / ISO/ASTM
       52921 / 52900);
     * **Additive-manufacturing-specific** standards: **ISO/ASTM 52900,
       52902, 52921, 52939, 52941**, and any newly-issued ASTM F42 work
       items addressing stiffness / energy-absorption testing of
       AM lattice / cellular parts.
   Please flag which of these are *normative* (must follow) vs.
   *informative* (good practice) for a peer-reviewed AM-tensegrity paper at
   ASME JMD / IDETC level, and give the most-cited published examples that
   followed each standard for a similar geometry/material.

2. **Best practices / pitfalls** for the actual Instron test.  Specifically:
     * Crosshead speed and strain rate (and how to report them — true
       vs. nominal, gauge length, machine-compliance correction).
     * Platen choice (flat, spherically seated, lubricated, anti-friction
       film, parallelism tolerance) and how it affects measured *initial*
       stiffness of soft-cell specimens.
     * **Machine compliance correction** — protocol for measuring the load-
       string compliance and subtracting it from the specimen
       displacement.  This is *critical* at low loads where TPU tendons
       dominate.  Please cite the canonical references.
     * Preload / contact-find protocol; toe-region removal per ASTM E111.
     * Use of a non-contact extensometer (DIC / video) vs. crosshead
       displacement for sub-mm compliance regimes.
     * Conditioning: **Mullins effect** in TPU — number of preconditioning
       cycles, soak time, humidity (TPU is hygroscopic; PETG less so but
       not zero), temperature.
     * Definition of "stiffness" we should report: tangent vs. secant
       modulus, what strain window, structural stiffness k = dF/ddelta vs.
       effective E, and how to non-dimensionalize across specimens of
       different bounding volume / relative density (Gibson–Ashby
       framework, rho* / rho_s scaling).
     * Number of replicates and statistical reporting (mean ± SD, 95 % CI,
       Weibull for failure-related quantities).
     * Documentation of build orientation, infill, raster angle, layer
       height, nozzle/bed temperatures, post-processing (annealing? we are
       *not* annealing initially), per ASTM F2971 / ISO/ASTM 52921.

3. **A concrete first-test protocol** we can hand to the undergraduate
   running the Instron next week, in checklist form: pre-test (specimen
   conditioning, geometry/mass measurement, photographs), mounting,
   alignment, contact-find / preload, preconditioning cycles, monotonic
   loading to a defined strain or load limit (please recommend limits for a
   tensegrity-inspired cell that is *not* meant to be loaded to
   densification on the first run), unloading, hysteresis quantification,
   post-test inspection, data export and metadata schema (CSV columns,
   units, sample-rate). Include a recommended **specimen ID / metadata
   schema** that will play nicely with a downstream Bayesian-optimization
   loop (BoTorch/Ax) operating on experimental data — i.e., what fields
   should be captured per specimen so that BO can later fit a GP surrogate
   to stiffness and SEA simultaneously.

4. **Stiffness-specific vs. strength-specific** test design.  The issue
   title is *stiffness testing*, not *energy absorption*.  Please be
   explicit about the differences in (a) load limits, (b) strain windows,
   (c) preconditioning, (d) replicate counts, and (e) reportable metrics
   between an *initial small-strain stiffness characterization* and the
   later energy-absorption tests (peak transmitted force, SEA,
   compaction efficiency η). Recommend whether stiffness should be measured
   in a *separate* test campaign or extracted from the unloading branch of
   the energy-absorption tests.

5. **Multi-material FFF-specific** considerations for stiffness data
   quality:
     * Layer-stack orientation effect on apparent strut stiffness (Z vs
       XY) — what build orientations should we test?
     * PETG–TPU interface integrity at the joint — how to *detect* joint
       slippage in the load–displacement curve and not mistakenly report
       it as material non-linearity.
     * Mass / dimensional check protocol: scale precision (0.01 g),
       caliper precision (0.01 mm), CT or laser-scan if available.
     * Aging / printing-batch effects — recommendation for a "control"
       specimen retested every N tests (matches our existing campaign
       protocol per ``idetc-abstract.tex``).

6. **Closest published analogs** (5–15 papers) with named author /
   journal / DOI / year, prioritized by similarity to our specimens
   (Snelson tensegrity, FFF multi-material, PETG/PLA + TPU, energy
   absorption / cushioning).  For each, summarize: standard cited (if
   any), specimen geometry, machine + crosshead speed, modulus / stiffness
   reported, and any reproducibility caveats.  Please also flag any of
   these papers that explicitly *deviated* from a standard and explained
   why — that justification language is what we want to model.

7. **Optional: equipment-specific** (Instron 5965 / 5969 / ElectroPuls /
   MTS Insight) recommendations for load cell range (we have a 5 kN cell
   available; is that the right choice for ~5–30 g tensegrity specimens
   loaded at small strains?), load-cell selection rules (ASTM E4
   verification class), and data-acquisition rate recommendations.

Please return a **single, structured technical brief** with section
headings matching items 1–7 above, plus a final "**Open questions / things
the lab should decide before the first test**" section.  Cite extensively;
prefer ASTM, ISO, ASME, peer-reviewed journals (Composite Structures,
Additive Manufacturing, IJSS, J. Mech. Phys. Solids, Materials & Design,
Polymer Testing) and clearly-attributed standards-development
publications.  When ASTM and ISO standards overlap, recommend which one
to cite.

Cross-references in this repository that may inform the answer:
* ``idetc-abstract.tex`` (quasi-static + drop-weight protocol, F_peak / SEA / η metrics)
* ``proposal.tex`` (campaign scope, materials, BO loop)
* prior Edison memos in ``edison-trajectories/`` on egg-drop, joint design,
  strut material, tensegrity design families.
"""


def main() -> int:
    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY")
        or os.environ.get("EDISON_API_KEY")
    )
    task = {"name": JobNames.LITERATURE_HIGH, "query": QUERY.strip()}

    print("Submitting LITERATURE_HIGH task ...", flush=True)
    submitted = client.create_task(task)
    # edison-client RestClient.create_task returns the trajectory_id as a
    # plain string (not a TaskResponse object).
    if isinstance(submitted, str):
        task_id = submitted
    else:
        task_id = (
            getattr(submitted, "task_id", None)
            or getattr(submitted, "trajectory_id", None)
            or getattr(submitted, "id", None)
        )
        if task_id is None and isinstance(submitted, dict):
            task_id = (
                submitted.get("task_id")
                or submitted.get("trajectory_id")
                or submitted.get("id")
            )
    print(f"task_id = {task_id}", flush=True)

    submission_record = {
        "task_id": str(task_id),
        "job_name": "LITERATURE_HIGH",
        "issue": 49,
        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "query": QUERY.strip(),
    }
    (OUT_DIR / "SUBMITTED.json").write_text(
        json.dumps(submission_record, indent=2)
    )

    # Bounded poll: wait up to ~28 minutes for completion so we can save the
    # full answer in this session.  If still in progress at the deadline we
    # leave SUBMITTED.json on disk for a follow-up session to fetch.
    deadline = time.time() + 28 * 60
    interval = 30
    response = None
    while time.time() < deadline:
        try:
            response = client.get_task(task_id, verbose=True)
        except Exception as exc:  # noqa: BLE001
            print(f"poll error (will retry): {exc}", flush=True)
            time.sleep(interval)
            continue
        status = (
            getattr(response, "status", None)
            or (response.get("status") if isinstance(response, dict) else None)
            or "unknown"
        )
        print(f"  status={status}", flush=True)
        if str(status).lower() in {"success", "completed", "failed", "error"}:
            break
        time.sleep(interval)

    if response is None:
        print("No response retrieved; placeholder SUBMITTED.json kept.")
        return 0

    # Persist full JSON dump
    try:
        payload = response.model_dump()
    except AttributeError:
        try:
            payload = response.dict()
        except AttributeError:
            payload = dict(response) if isinstance(response, dict) else {
                "raw": str(response)
            }

    out_json = OUT_DIR / f"instron-stiffness-{task_id}.json"
    out_json.write_text(json.dumps(payload, indent=2, default=str))
    print(f"wrote {out_json}")

    formatted = (
        getattr(response, "formatted_answer", None)
        or payload.get("formatted_answer")
        or payload.get("answer")
        or ""
    )
    if formatted:
        out_md = OUT_DIR / f"instron-stiffness-{task_id}.md"
        out_md.write_text(
            f"# Edison LITERATURE_HIGH — Instron stiffness testing best "
            f"practices & ASTM standards\n\n"
            f"- Task ID: `{task_id}`\n- Issue: #49\n- Job: `LITERATURE_HIGH`\n\n"
            f"---\n\n{formatted}\n"
        )
        print(f"wrote {out_md}")

    status = (
        getattr(response, "status", None)
        or payload.get("status")
        or "unknown"
    )
    if str(status).lower() in {"success", "completed"}:
        # Successful fetch — drop the placeholder
        try:
            (OUT_DIR / "SUBMITTED.json").unlink()
        except FileNotFoundError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
