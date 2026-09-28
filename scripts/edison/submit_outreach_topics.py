"""Submit + fetch Edison LITERATURE_HIGH query on outreach-topics for the
named lander-style / drag-free egg-drop contacts surfaced in PR #47 and
the JMD reviewer pool surfaced in this PR (#46-ish; branch
copilot/who-is-the-target-audience).

Question framing is grounded in the project state visible across the
following PRs / branches:

- PR #20 manuscript: PETG strut + TPU 85A tendon Snelson-class tensegrity
  fabricated on a Bambu H2D IDEX printer; BO loop over geometry (strut/tendon
  diameters, prestress) targeting an assistive crutch-tip energy-absorber
  use case.
- PR #38 + #43 joint design: Phase-3 CAD review (Edison ANALYSIS 19e0c868)
  recommending B (dovetail) primary + A (anchor-bulb) backup PETG/TPU joints;
  no peer-reviewed PETG-TPU interface bond data exists in the literature.
- PR #28 instrumentation: Lansmont M23 drop tower + QTec/Polytec LDV; no
  prior peer-reviewed work combines shock + LDV on the same specimen.
- PR #47 egg-drop demo: drag-free SUPERball-lineage 6-bar + PETG payload
  cradle; Bruceton h_crit FoM; Anand 2022 (75 m biodegradable, single-use)
  and Zhang 2022 (22 in / 20 m / 235 g, reusable) as the published frontier.
- Mid-fidelity sim: NVIDIA Newton (Warp); rigid-strut peak-g is dominated by
  floor-contact stiffness (not cable stiffness); SEA varies with cable
  stiffness. DiffPD/PolyFEM+IPC is the next escalation tier.

Asks Edison to enumerate, per outreach-target archetype:

  (a) the highest-leverage technical / scientific feedback aspects to
      surface in a first-contact email (5-8 archetypes, ~2-sentence
      pitch each);
  (b) tech-transfer / commercialization angles worth raising;
  (c) immediate "gotchas" most likely to be flagged by an experienced
      practitioner;
  (d) collaborative-contribution mechanisms (external validation,
      shared specimens, instrument-time swaps, standard datasets,
      curriculum/outreach co-authorship, etc.);
  (e) which of the named lander-pool contacts (Rimoli, Agogino,
      SunSpiral, Mueller, Vespignani, Skelton/Sultan, Bayandor,
      Jing Zhang, Anand) are best-suited to which ask, with citations.

Saves md + json artifacts under
edison-trajectories/2026-05-12-outreach-topics-<task_id>.{md,json}.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# edison-client >= 0.12 reads EDISON_PLATFORM_API_KEY, not EDISON_API_KEY.
os.environ.setdefault(
    "EDISON_PLATFORM_API_KEY",
    os.environ.get("EDISON_API_KEY", ""),
)

from edison_client import EdisonClient, JobNames  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "edison-trajectories"

QUERY = """\
Context. We are building a printable Snelson-class tensegrity (PETG struts,
TPU 85A tendons, fabricated on a Bambu H2D IDEX printer) and running a
Bayesian-optimization loop over geometry (strut + tendon diameters,
prestress, topology) for two parallel application threads:
  (1) an assistive crutch-tip / impact-absorber under quasi-static and
      drop-impact loading; and
  (2) a SUPERball-lineage drag-free egg-drop demo, using h_crit (Bruceton
      staircase, n>=20) as the primary FoM and peak g_max @ 3 m + SEA +
      reusability (N_reuse) as secondaries.
Open technical issues across our PRs include: (i) no peer-reviewed
PETG-TPU interface bond data exists, so our PETG-TPU joint geometry
(barbed TPU rebar / dovetail / anchor-bulb variants) is currently
literature-extrapolated from PLA-TPU; (ii) rigid-strut tensegrity sims
in MuJoCo/PyBullet show peak-g is dominated by floor-contact stiffness
rather than cable stiffness, suggesting we need DiffPD or PolyFEM+IPC
for quantitative impact predictions; (iii) the closest published egg-drop
analogs are Anand 2022 (biodegradable, 75 m, single-use), Zhang 2022
(22 in / 20 m / 235 g, reusable, best instrumented dataset) and the NASA
SUPERball NIAC report (Agogino + SunSpiral 2018), but none target the
"reusable, omnidirectional, low-rho_rel, FFF-printable, BO-optimized"
quadrant we occupy.

We have drafted an outreach contact list (reviews/target_audience.md
section 3d-prime) that includes Julian Rimoli (Georgia Tech, AIAA SciTech
2016 lander), Adrian Agogino (NASA Ames, NIAC SUPERball Phase 2 2018),
Vytas SunSpiral (formerly NASA Ames), Mark Mueller (UC Berkeley HiPeRLab,
IEEE/ASME T-Mech 2024 collision-resilient icosahedron), Andrew Zhang +
Brian Cera (UC Berkeley, Agogino lineage), Massimo Vespignani (SUPERball
v2 2018), Robert Skelton + Cornel Sultan (TAMU / Virginia Tech,
class-1 lander theory), Jamshid Bayandor (Virginia Tech CRASH Lab,
TANDEM 2017), Jing Zhang et al. (Harbin Institute of Technology,
Aerospace 2025), and Madhumati Anand (biodegradable 75 m, 2022).

Question. For a first-contact email to each of the above researchers,
enumerate -- with peer-reviewed citations to their own published work
where possible:

(a) Highest-leverage technical / scientific feedback aspects to surface
    (5-8 archetype clusters; ~2 sentences each), e.g. "FFF tensegrity
    impact-mechanics fidelity gap (rigid-strut vs DiffPD vs experiment)",
    "PETG-TPU multi-material interface characterization", "Bruceton
    h_crit as a transferable benchmark across the SUPERball / Zhang /
    Anand lineage", "BO acquisition function choice for noisy impact
    objectives", "scaling and orientation-isotropy validation against
    Vespignani / Bayandor scaled-up tensegrities", etc.

(b) Tech-transfer / commercialization angles worth raising
    (e.g. NIAC successor, NASA SBIR/STTR space-systems topics, DoT/FAA
    drone-cargo airdrop, biomedical orthotics OEMs, defense-payload
    landers, IEEE Spectrum / Sci. Am. demo).

(c) Immediate "gotchas" an experienced practitioner is most likely to
    flag on first read of our setup, e.g. "your floor-contact stiffness
    swamps your cable signal", "TPU 85A creep will shift prestress
    between drops", "Bambu H2D filament-swap interface is the most
    likely failure mode", "Bruceton staircase needs randomized
    orientations to be defensible", "tensegrity classification (class-1
    vs class-2) depends on strut closest-approach distance".

(d) Collaborative contribution mechanisms compatible with each
    archetype: external validation against their published datasets,
    inter-lab specimen exchange, instrument-time swaps (e.g. Lansmont
    M23 drop tower + Polytec / QTec LDV), shared standardized
    egg-drop benchmark protocol, GitHub-hosted reproducible BO loop,
    co-supervised undergraduate / capstone projects, joint conference
    workshop or invited session, cross-citation in revision, etc.

(e) For each named lander-pool contact above, recommend WHICH one or
    two of the (a)-(d) asks is best-suited to that person, anchored
    to the specific paper of theirs that would motivate the ask.

Format. Markdown, with a short opening summary table mapping
{archetype cluster -> 2-sentence pitch -> best contact -> citation}.
Then the per-archetype detail. Then the per-contact recommendations.
Then a "stretch" section on collaborative-contribution mechanisms we
might not have considered. Inline citations to the actual peer-reviewed
papers we should reference in the email body.
"""


def main() -> int:
    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get(
        "EDISON_API_KEY"
    )
    if not api_key:
        sys.stderr.write(
            "ERROR: set EDISON_PLATFORM_API_KEY (or EDISON_API_KEY)\n"
        )
        return 2

    client = EdisonClient(api_key=api_key)
    task_data = {"name": JobNames.LITERATURE_HIGH, "query": QUERY}

    # Submit non-blocking; the orchestrator will wait but with a generous
    # ceiling so we can capture the task_id even if it times out from
    # the agent's side.
    print("Submitting Edison LITERATURE_HIGH outreach-topics query ...")
    task_ids = client.create_task(task_data)
    if isinstance(task_ids, str):
        task_ids = [task_ids]
    task_id = task_ids[0]
    print(f"task_id = {task_id}")

    # Persist the task id immediately so we can fetch later if needed.
    submitted_path = OUT_DIR / "outreach-topics-SUBMITTED.json"
    submitted_path.write_text(
        json.dumps({"task_id": task_id, "name": "LITERATURE_HIGH"}, indent=2)
        + "\n"
    )
    print(f"wrote {submitted_path}")

    # Try to wait in-session.
    print("Waiting for task to complete (this may take several minutes) ...")
    results = client.get_task(task_id, verbose=True)
    if not isinstance(results, list):
        results = [results]
    t = results[0]
    print(f"status = {t.status}")

    md_path = OUT_DIR / f"2026-05-12-outreach-topics-{task_id}.md"
    json_path = OUT_DIR / f"2026-05-12-outreach-topics-{task_id}.json"
    md_path.write_text(getattr(t, "formatted_answer", "") or "")
    json_path.write_text(
        json.dumps(json.loads(t.model_dump_json()), indent=2) + "\n"
    )
    print(f"wrote {md_path}")
    print(f"wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
