"""Submit Edison ANALYSIS task that synthesizes the 5 per-modality briefs.

Context: PR #60 comment 4511245383 — after fetching the 5 LITERATURE_HIGH
briefs (one per measurement modality, see ``submit_objective_functions.py``),
ask Edison ANALYSIS to cross-cut them into a single cohesive recommendation
document for the BO campaign in ``bo/tensegrity_campaign.py``.

Implementation:

* Upload each ``edison-trajectories/objective-functions/0{1..5}-*.md`` and
  ``.json`` artifact via ``client.upload_file`` -> ``data_entry:uuid``.
* ``create_task({"name": JobNames.ANALYSIS, "query": SYNTHESIS_PROMPT},
  files=[...])`` so the ANALYSIS agent has every prior trajectory in scope.
* The prompt also asks the normalization sub-question raised in the same
  PR comment: "would it make more sense during the optimization campaign to
  normalize by mass / volume?". Answers must reconcile per-design changes
  in *both* m_specimen and bounding volume from PR #35's design space.
* Idempotent: writes ``synthesis-SUBMITTED.json`` placeholder up front so a
  follow-up session can ``get_task(task_id=...)`` and overwrite with
  ``synthesis-<task_id>.{md,json}``.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

if os.environ.get("EDISON_API_KEY") and not os.environ.get("EDISON_PLATFORM_API_KEY"):
    os.environ["EDISON_PLATFORM_API_KEY"] = os.environ["EDISON_API_KEY"]

from edison_client import EdisonClient, JobNames  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "edison-trajectories" / "objective-functions"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SLUG = "synthesis"
PLACEHOLDER = OUT_DIR / f"{SLUG}-SUBMITTED.json"

SYNTHESIS_PROMPT = """\
Synthesize the five attached Edison LITERATURE_HIGH briefs (one per
measurement modality on a Bambu H2D-printed PETG-strut + TPU 85A-tendon
tensegrity energy absorber, parent PR #60 and source issue #51) into a
single cohesive recommendation document for the Bayesian-optimization
campaign defined in `bo/tensegrity_campaign.py` (PR #30 + PR #33).

The five attached briefs are:
  01 - Accelerometer on Lansmont M23 (base + top plate; 200 ms shock + ~10 s
       ringdown). LITERATURE_HIGH task cfd30f3e-20e8-43b4-b055-29f9fc4f121f.
  02 - High-speed / slow-mo phone video (failure-mode + DIC + shape recovery
       / N_reuse scoring). LITERATURE_HIGH task 7d6b43bf-d948-4e13-aea5-4a89ec12ed49.
  03 - Electrodynamic shaker transmissibility T(f) (cheap, non-destructive,
       prestress-swept modal pre-screen). LITERATURE_HIGH task
       31126ee7-9f3b-4af4-adbe-855c14513487.
  04 - Pneumatic slug-firing / gas gun (longer impulse + tiled-cell + plate,
       strain-rate extension beyond the M23 envelope). LITERATURE_HIGH task
       9d74ab2e-669f-48bd-938b-7e380e188492.
  05 - Polytec VibroFlex QTec single-point LDV (non-contact velocity cross-
       check; back-computes transmitted pressure on the gas-gun plate; poor-
       man's scanning LDV for ODS). LITERATURE_HIGH task
       f40e41a7-b41d-4158-a89f-f18a5ae81e5c.

Required output sections (use these exact headings, in this order):

# 1. Master objective / constraint matrix
Single ranked table with rows = candidate BO outcomes, columns = which of
the 5 modalities measure that outcome with what fidelity / cost / CoV. Mark
which modality is the canonical owner (the one whose value Ax should
attach as the trial's primary observation for that metric) and which are
auxiliary cross-checks. Reconcile any unit / definition disagreement
between the 5 briefs (e.g., is `eta` the crush-force efficiency
F_mean / F_peak or the energy-absorption efficiency E_abs / (F_peak * delta)?).

# 2. Recommended Ax `Metric` / `Objective` shape
Concrete pseudocode (Ax `MultiObjective` + `ObjectiveThreshold` +
`OutcomeConstraint`) for the BO loop in `bo/tensegrity_campaign.py`, with:
  - exactly which Metric is `lower_is_better=True` vs. `False`;
  - per-metric `observation_noise` (heteroscedastic vs. homoscedastic) with
    a reasonable starting value from the 5 briefs;
  - which metrics are *constraints* (chance-constrained or hard) vs.
    *objectives*; the lab can defensibly run qNEHVI on 2 to 4 objectives
    but no more.

# 3. Multifidelity / multi-task structure
How to slot the 5 modalities into the MuJoCo (C) -> Newton/Warp (B) ->
PolyFEM+IPC / DiffPD (A) sim ladder from PR #33. Concretely: which modality
plays the role of "high-fidelity ground-truth experiment" vs. "low-fidelity
cheap screen" in a MultiTaskGP / MFKG formulation, and how the same Ax
Experiment can pool data across them.

# 4. Normalization: should the BO objectives be normalized by mass and / or
#    bounding volume, given the PR #35 design space?
The PR #35 design variables (R_mm, H_mm, twist_deg, strut_d_mm,
cable_d_mm, joint_d, tiling, infill, build_orientation) simultaneously
change both the specimen mass m_specimen and its bounding-cylinder volume
V_bb on every BO trial. Answer the following sub-questions explicitly,
each with primary peer-reviewed citations (no fabricated DOIs):

  (a) Which of the candidate BO outcomes (F_peak / g_max, E_abs, SEA,
      VEA, sigma_plateau, eta, epsilon_d, transmissibility, zeta, N_reuse,
      W_min = C_min * rho_rel from Pajunen 2019, cushion-curve g_max(rho_T)
      from ASTM D1596 / D5276, etc.) are intrinsically *intensive* (already
      size-independent), which are *extensive* (must be normalized to make
      trials comparable), and which are ambiguous?
  (b) For the extensive ones, what is the defensible normalization choice
      in the published architected-material / foam / cushion / lattice
      literature? Compare at minimum:
        - mass normalization (SEA = E_abs / m_specimen, J/g)
        - volume normalization (VEA = E_abs / V_bb, MJ/m^3, or to the
          densified-up-to-epsilon_d volume V_d)
        - relative-density normalization (rho_rel = rho_specimen / rho_solid)
          and the Pajunen 2019 W_min = C_min * rho_rel composite figure of
          merit
        - cushion-curve normalization (g_max plotted against static stress
          rho_T = m_payload * g / A_footprint, per ASTM D1596 / D5276 /
          D4168 / D6537 cushion-test geometry)
        - Gibson-Ashby relative-density scaling (E* / E_s ~ (rho_rel)^n,
          sigma_pl* / sigma_ys ~ C * rho_rel^m) for cross-architecture
          comparison.
      For each, state when it is the *right* normalization (which design
      decision it makes invariant) and when it silently biases the Pareto
      front (e.g., SEA rewards low-mass cells even if they underperform per
      unit volume; VEA rewards filling the bounding box even if mass-
      inefficient; W_min ranks correctly across rho_rel but breaks down
      under different parent solids).
  (c) Concrete recommendation for this BO campaign: a *minimal sufficient*
      set of normalized objectives (target 2-3 primary + 1-2 constraints)
      that (i) is invariant under the PR #35 design-space changes that
      should not matter (e.g., uniform scaling of the cell), and (ii) is
      sensitive to the design-space changes that should matter
      (architecture, tendon stiffness, prestress, tiling). Recommend
      whether mass and / or bounding volume should themselves appear as
      *constraints* (e.g., m_specimen <= 500 g, V_bb <= V_bb_max, or even
      both) rather than as objectives or as denominators.
  (d) Practical: which of the 5 modalities can actually measure m_specimen
      and V_bb cheaply enough to compute the normalized quantity at every
      trial without an extra weigh-in / caliper / micro-CT step? Identify
      which lab measurement should be added to the per-trial workflow.
  (e) Edge cases / gotchas: if the BO loop is normalizing by m_specimen but
      the cell densifies (rho_rel -> 1 partially) during a non-destructive
      shaker sweep, does the normalization still hold? Are there
      strain-rate-dependent normalizations (e.g., Cowper-Symonds rho^*)
      that the gas-gun (modality 4) requires that the M23 drop (1) does
      not? How should reusability / N_reuse normalize across trials with
      different masses?

# 5. Cross-modality consistency checks
Top 5-10 quantitative cross-checks ("sanity equalities") that should hold
between modalities for the same specimen. E.g., the impulse integral of
the M23 accelerometer (1) should match m_top * (v_impact - v_rebound)
recovered from the QTec LDV (5); the lowest mode f_1 from the shaker
transmissibility (3) should match the dominant ringdown frequency from
the M23 (1) within a few percent for low prestress; the densification
displacement from high-speed video (2) should match the integrated LDV
velocity (5). For each, give the tolerance you expect and the most likely
single cause of a violation.

# 6. Open gaps / next Edison queries
What information is *still missing* after merging the 5 briefs that would
require a further query (LITERATURE_HIGH, PRECEDENT, or ANALYSIS) before
the BO campaign in `bo/tensegrity_campaign.py` can run with confidence
beyond the placeholder dummy evaluator. Rank by expected information value
relative to query cost.

# 7. References
A single, deduplicated, numbered references section across all sections
above, with DOIs where available. Do not fabricate citations; if a brief
already cited a reference, retain its exact identifier so the numbering
maps back to the source brief.

Constraints on the answer:
  * Treat every quantitative claim in the 5 attached briefs as ground
    truth unless you flag a specific disagreement; never silently
    contradict them.
  * If two briefs disagree (e.g., different g_max thresholds for
    "egg-survival" or different reasonable SEA targets), call out the
    disagreement in section 1 explicitly and give the resolution you
    recommend with a citation.
  * Cite only primary, peer-reviewed sources or established standards
    (ASTM, ISO, JEDEC, NASA / NIST). Do not invent DOIs.
"""


def _is_artifact(path: Path) -> bool:
    """Match the 5 per-modality briefs only (skip README, placeholders, self)."""
    name = path.name
    if name.startswith(("01-", "02-", "03-", "04-", "05-")):
        return path.suffix in {".md", ".json"} and not name.endswith("-SUBMITTED.json")
    return False


def main() -> int:
    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY")
        or os.environ.get("EDISON_API_KEY")
    )

    if PLACEHOLDER.exists():
        existing = json.loads(PLACEHOLDER.read_text())
        prior_id = existing.get("task_id")
        print(f"[skip] placeholder exists with task_id={prior_id}", flush=True)
        return 0

    artifacts = sorted([p for p in OUT_DIR.iterdir() if _is_artifact(p)])
    if not artifacts:
        print("[err] no per-modality briefs found to upload", flush=True)
        return 2
    print(f"[upload] {len(artifacts)} artifacts ->", flush=True)
    file_uris: list[str] = []
    for path in artifacts:
        uri = client.upload_file(
            file_path=path,
            name=path.name,
            description=(
                f"Per-modality Edison LITERATURE_HIGH brief "
                f"({path.stem}) from PR #60."
            ),
            tags=["objective-functions", "PR-60", "modality-brief"],
        )
        print(f"  - {path.name} -> {uri}", flush=True)
        file_uris.append(uri)

    task = {"name": JobNames.ANALYSIS, "query": SYNTHESIS_PROMPT}
    resp = client.create_task(task, files=file_uris)
    task_id = resp if isinstance(resp, str) else getattr(
        resp, "task_id", None
    ) or getattr(resp, "trajectory_id", None) or str(resp)
    print(f"[submit] ANALYSIS task_id={task_id}", flush=True)

    PLACEHOLDER.write_text(
        json.dumps(
            {
                "slug": SLUG,
                "headline": (
                    "Cross-modality synthesis of the 5 per-data-source "
                    "LITERATURE_HIGH briefs + normalization question"
                ),
                "task_id": task_id,
                "job": "ANALYSIS",
                "status": "submitted",
                "submitted_at": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                ),
                "uploaded_files": [
                    {"name": p.name, "uri": uri}
                    for p, uri in zip(artifacts, file_uris)
                ],
                "source_pr_comment": (
                    "https://github.com/vertical-cloud-lab/"
                    "tensegrity-optimization/pull/60#issuecomment-4511245383"
                ),
            },
            indent=2,
        )
        + "\n"
    )
    print(f"[done] wrote {PLACEHOLDER.name}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
