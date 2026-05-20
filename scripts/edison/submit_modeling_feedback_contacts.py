"""
Submit a LITERATURE_HIGH Edison Scientific query to identify named researchers,
research groups, simulator maintainers, and standards/test-lab contacts the
project should reach out to for feedback on our multi-fidelity tensegrity drop
modelling approach (sanity checks, spot checks, recommendations).

Context (passed verbatim to Edison so it can reason against project facts):

- Repo: vertical-cloud-lab/tensegrity-optimization, PR "Add runnable tensegrity
  simulation demos (MuJoCo, PyBullet, PyChrono, Newton, DiffPD, PolyFEM+IPC) +
  3D animated renders + Edison survey + regime-aware sweeps + PLA/TPU 85A
  printable-design model".
- Multi-fidelity stack (per Edison sim-survey 782657e0):
  - Tier A: PolyFEM + IPC (barrier-method contact, NeoHookean), built from
    source; T-prism mesh (3 PLA struts + 9 TPU 85A tendons welded via gmsh OCC
    fragment) running end-to-end (commit 124bba2).
  - Tier B: NVIDIA Newton 1.1 (Warp XPBD, differentiable) + DiffPD source
    build (Du et al. SIGGRAPH 2021).
  - Tier C: MuJoCo (rigid-strut + tendon screening), PyBullet, PyChrono.
- Material constants: PLA struts E=3.5 GPa, rho=1240; TPU 85A tendons
  (NinjaFlex-class) E=12 MPa secant, sigma_break=26 MPa, rho=1200.
- Two regimes encoded (Lansmont M23 envelope from #28):
  - crutch_tip: 75 kg @ 1.4 m/s, Ø24x25 mm cell, HAVS peak <= 8 g (issue #18).
  - nasa_lander: 5 kg @ 9.8 m/s, Ø200x200 mm cell, GEVS peak <= 1500 g
    (issues #14, #16).
- Existing relevant Edison content already in repo:
  - sim survey 782657e0 (three-tier recommendation).
  - payload-vs-no-payload 37ae0665.
  - outreach-topics f18aca01 (7 archetype clusters, 8 collab mechanisms, 12
    lander-pool contacts) -> reviews/target_audience.md.
  - industry-partners c18a2313.
  - ASME JMD reviewers 9cc7db18.
  - tensegrity-designs fad054b3 + design-gaps 6226a551.
  - egg-drop 1b90208d + follow-up f41b7034.
"""

from __future__ import annotations

import json
import os
import pathlib
import time
from datetime import datetime, timezone

# edison-client >= 0.12 reads EDISON_PLATFORM_API_KEY, not EDISON_API_KEY.
os.environ.setdefault(
    "EDISON_PLATFORM_API_KEY",
    os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY", ""),
)

from edison_client import EdisonClient, JobNames  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "edison-trajectories" / "modeling-feedback-contacts"
OUT_DIR.mkdir(parents=True, exist_ok=True)


QUERY = """
We have built a multi-fidelity simulation stack to model drop-impact response
of class-1 tensegrity cells (3 PLA struts + 9 TPU 85A tendons; T-prism
topology) for two application regimes (crutch tip @ 1.4 m/s / 75 kg, NASA-
lander-style @ 9.8 m/s / 5 kg, both inside the Lansmont M23 envelope). The
stack comprises: (Tier C) MuJoCo / PyBullet / PyChrono rigid-strut + cable
screening; (Tier B) NVIDIA Newton (Warp XPBD, differentiable) and DiffPD
(Du et al. 2021, differentiable projective dynamics); (Tier A) PolyFEM + IPC
(barrier-method contact, NeoHookean, built from source) on a welded
strut+tendon volumetric mesh (gmsh OCC fragment). We have run:

- MuJoCo bare-prism 1 m drop + regime sweeps (k_cable swept ~3 decades).
- Newton XPBD all-particle T-prism with payload-suspension tendons in load
  path; tendon-Ø sweep (1.5, 3.0, 5.0 mm).
- DiffPD soft-cube smoke test.
- PolyFEM+IPC NeoHookean cube drop, then welded T-prism drop end-to-end
  (5481 tets / 2168 nodes, ImplicitEuler dt=0.5 ms x 80 steps, dhat=5e-5 m).
- Printable-design module with class-1 (strut-strut closest-approach) check,
  Bambu H2D printability bounds, 7x5 (tendon-Ø, prestrain) sweep -> Pareto.
- 3D offscreen renders with tendon strain-coloured cables (OSMesa MuJoCo).

We need to identify **specific people and groups to reach out to** for
feedback / sanity checks / spot checks / recommendations on this modelling
approach. Please produce a citation-rich, prioritised, *contact-level*
brief organised as follows:

# 1. Tensegrity dynamics + drop / impact mechanics (academic)

Named researchers (with current affiliation, role, email/lab URL where
publicly listed, recent papers, why they are well-placed to critique our
approach, and a specific 1-2 sentence "ask"). Group into:

  (a) Tensegrity structural mechanics + form-finding (e.g., Skelton, Sultan,
      Caluwaerts, Goyal, Tibert, Pellegrino, Motro, de Oliveira, Bel Hadj
      Ali).
  (b) Tensegrity robotics / SUPERball / lander lineage (NASA Ames Intelligent
      Robotics Group: Vytas SunSpiral, Adrian Agogino, Brian Tietz Mirletz,
      Massimo Vespignani; UC Berkeley AHMCT / BEST Lab; Alice Agogino).
  (c) Impact-attenuation / drop-test mechanics of soft/architected materials
      (Pajunen, Bauer, Anand, Snapp, Gongora, Valdevit, Greer, Schaedler).
  (d) Tensegrity + 3D-printing (e.g., Davami 2025; Liu 2023; Intrigila 2022;
      Yavas 2022; Rieffel; Hiller & Lipson).

# 2. Simulator maintainers + differentiable physics

For each of the simulators we use, identify the active maintainer(s) and the
right channel (GitHub discussions / issues / mailing list) to ask for
modelling sanity-checks. Cover:

  (a) PolyFEM + IPC: Teseo Schneider (Victoria, NYU), Daniele Panozzo (NYU
      Courant), Zachary Ferguson, Minchen Li (CMU), Chenfanfu Jiang (UCLA);
      ipc-toolkit maintainers.
  (b) DiffPD: Tao Du (Tsinghua), Wojciech Matusik (MIT CSAIL GFX).
  (c) NVIDIA Newton / Warp: Miles Macklin, Matthias Mueller-Fischer, the
      Newton GitHub org maintainers; Omniverse Isaac Lab tensegrity-robot
      examples (if any).
  (d) MuJoCo: Emo Todorov (Roboti / UW), Yuval Tassa (DeepMind), the
      MuJoCo-MJX team; relevant tendon/cable contact issues on the
      google-deepmind/mujoco issue tracker.
  (e) PyBullet / Bullet3: Erwin Coumans; soft-body deformable contact
      maintainers.
  (f) PyChrono: Alessandro Tasora (Parma), Dario Mangoni; Project Chrono
      community.
  (g) NTRT (NASA Tensegrity Robotics Toolkit) maintainers and any active
      fork curators.

# 3. Materials + AM characterisation

  (a) Researchers who have published PLA-TPU multi-material FDM interface
      data (Lopes 2018, Zhang 2026, Ruwais 2025) - whose feedback would help
      us trust the welded PolyFEM material model.
  (b) NinjaFlex / TPU 85A characterisation labs (Fenner/Lubrizol contacts;
      academic groups with published TPU 85A secant moduli and Mullins-
      effect curves).
  (c) PLA shock / impact characterisation (Charpy / Izod / drop-weight)
      contacts.

# 4. Standards bodies + test labs

People who can audit our standards mapping (we currently target ASTM D5276,
F1292, F2971, ISTA 1A/1H, MIL-STD-810H 516.8, GSFC GEVS-STD-7000B, JEDEC for
M23). For each, give the standards-committee secretariat and a recognised
academic/practitioner with active publications. Include drop-test lab
contacts (Lansmont, MTS, Instron application engineers; NASA GSFC; Sandia;
Aberdeen Test Center) and a one-paragraph note on how to engage them
(formal RFP vs. informal email vs. conference Q&A).

# 5. Bayesian optimisation + multi-fidelity surrogates

Researchers we should ping for sanity checks on the BO + multi-fidelity
strategy that consumes these simulators (e.g., Frazier, Wang, Garnett,
Letham, Bakshy / BoTorch / Ax; Frazier's group at Cornell; Wang's group at
UMich; Acceleration Consortium SDL community; Bran Selic / Adam Stevens
multi-fidelity comp sci contacts).

# 6. Synthesis

  (a) A ranked top-10 contact list ("if you can only send 10 emails this
      month, send them to these 10 people, in this order, asking these
      specific questions"), with the rationale for each ranking.
  (b) A draft 1-page outreach email template (subject + 4-paragraph body)
      that we can adapt per contact and that links our repo, our PR, and
      the specific artifact (e.g., simulations/polyfem_drop_tprism.png,
      simulations/outputs/regime_*_printable_heatmap.png) we want feedback
      on.
  (c) A list of 3-5 venues (workshops, journals, Slack/Discord
      communities) where we should post the modelling approach for
      broader community spot-checks (e.g., SIGGRAPH Physics-Based Animation
      community, ICRA/IROS soft-robotics workshops, ASME IMECE Tensegrity
      symposium, Acceleration Consortium SDL Slack, the polyfem/polyfem
      GitHub Discussions, BoTorch GitHub Discussions).

For every named contact, cite the publication(s) or repo activity that
justifies the recommendation. Flag any contact where the recommendation is
engineering judgement rather than literature-grounded.
""".strip()


def main() -> None:
    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY")
    if not api_key:
        raise SystemExit("EDISON_PLATFORM_API_KEY / EDISON_API_KEY env var not set")

    client = EdisonClient(api_key=api_key)

    submitted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{submitted_at}] submitting LITERATURE_HIGH modeling-feedback-contacts query")

    submitted = client.create_task(
        task_data={"name": JobNames.LITERATURE_HIGH, "query": QUERY},
    )
    trajectory_id = getattr(submitted, "trajectory_id", None) or str(submitted)
    print(f"  trajectory_id: {trajectory_id}")

    pointer = OUT_DIR / f"modeling-feedback-contacts-{trajectory_id}-SUBMITTED.json"
    pointer.write_text(
        json.dumps(
            {
                "trajectory_id": trajectory_id,
                "submitted_at": submitted_at,
                "job": "LITERATURE_HIGH",
                "topic": "named contacts for tensegrity drop-modelling feedback",
                "related_issues_prs": [14, 16, 18, 28, 38, 45, 46, 47, 49, 50],
                "related_edison_tasks": [
                    "782657e0",
                    "37ae0665",
                    "f18aca01",
                    "c18a2313",
                    "9cc7db18",
                    "fad054b3",
                    "6226a551",
                    "1b90208d",
                    "f41b7034",
                ],
            },
            indent=2,
        )
    )
    print(f"  pointer: {pointer.relative_to(REPO_ROOT)}")

    # Poll for up to ~40 min so we can fetch in the same session.
    deadline = time.time() + 40 * 60
    poll_every = 30
    last_status = None
    while time.time() < deadline:
        try:
            status_resp = client.get_task_status(trajectory_id=trajectory_id)
        except Exception as exc:  # noqa: BLE001
            print(f"  status poll failed: {exc!r}")
            time.sleep(poll_every)
            continue
        status = getattr(status_resp, "status", None) or str(status_resp)
        if status != last_status:
            print(f"  [{datetime.now(timezone.utc).strftime('%H:%M:%S')}] status: {status}")
            last_status = status
        if str(status).lower() in {"success", "failed", "error", "cancelled"}:
            break
        time.sleep(poll_every)

    try:
        result = client.get_task(trajectory_id=trajectory_id, verbose=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  fetch failed: {exc!r}")
        return

    md_path = OUT_DIR / f"modeling-feedback-contacts-{trajectory_id}.md"
    json_path = OUT_DIR / f"modeling-feedback-contacts-{trajectory_id}.json"
    formatted = getattr(result, "formatted_answer", None) or ""
    md_path.write_text(
        f"# Edison literature brief: named contacts for feedback on the "
        f"multi-fidelity tensegrity drop-modelling approach\n\n"
        f"- **Task ID:** `{trajectory_id}`\n"
        f"- **Job:** `LITERATURE_HIGH`\n"
        f"- **Submitted:** {submitted_at}\n"
        f"- **Fetched:** {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- **Status:** {getattr(result, 'status', 'unknown')}\n\n"
        f"---\n\nQuestion:\n\n{QUERY}\n\n---\n\n{formatted}\n"
    )
    try:
        json_path.write_text(result.model_dump_json(indent=2))
    except Exception:  # noqa: BLE001
        json_path.write_text(json.dumps(result, default=str, indent=2))
    print(f"  wrote {md_path.relative_to(REPO_ROOT)}")
    print(f"  wrote {json_path.relative_to(REPO_ROOT)}")
    if pointer.exists():
        pointer.unlink()


if __name__ == "__main__":
    main()
