"""
Submit a LITERATURE_HIGH Edison Scientific query asking how the inclusion (or
omission) of a payload inside a drop-tested tensegrity affects the real-world
applicability of both the simulations and the planned experiments.

Context (passed verbatim to Edison so it can reason against project facts):

- Repo: vertical-cloud-lab/tensegrity-optimization
- We are running offscreen MuJoCo / Newton(Warp) / PolyFEM+IPC drop simulations
  of a class-1 T-prism (3 PETG/PLA struts + 9 TPU 85A tendons) onto a rigid
  floor. Latest render-only MuJoCo regime sims (b8c1aa9) actually look
  reasonable when the payload is *attached to the struts as distributed inertia*
  (axial loading model, like a crutch tip), and look wildly non-physical when
  the payload is *suspended inside the cage by 6 internal tendons*
  (SUPERball/NASA-TBR style) — soft TPU 85A (E ~ 12 MPa) suspension oscillates
  wildly at impact and yanks the 0.7 g prism through the floor.
- Two regimes are encoded in `simulations/regimes.py`:
  - `crutch_tip` (issue #18): 75 kg payload @ 1.4 m/s through Ø24x25 mm cell,
    HAVS target peak <= 8 g, pulse >= 5 ms.
  - `nasa_lander` (issues #14/#16): 5 kg payload @ 9.8 m/s (Lansmont M23 max
    delta-V from #28) through Ø200x200 mm cell, GEVS peak <= 1500 g.
- Existing Edison content on payload/egg-drop is at PR #47 (egg-drop
  tensegrity, drag-free baseline, BEAR baseline, SUPERball-v2 actuators) and
  issue #46. Existing standards/protocol Edison content is at PR #50
  (Instron stiffness, ASTM standards) and issue #49.
- Drop-test standards already surfaced in the repo Edison artifacts:
  ASTM D5276 (free fall drop of loaded containers, rigid concrete floor),
  ASTM F1292 (impact attenuation playground surfaces), ASTM F2971 (AM test
  reporting), ISTA 1A, MIL-STD-810H 516.8 shock. GSFC GEVS in #16.
- Drop modes we are debating: (a) axially-loaded strut tip (crutch use case),
  (b) payload rigidly clamped to a strut (e.g. instrumented mass + ADXL375 on
  a strut), (c) payload suspended inside the cage by additional TPU tendons
  (SUPERball architecture, applicable to lander/egg-drop demo), (d) bare cell
  (no payload) — a "pure topology screen" with a fictitious added inertia.
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
OUT_DIR = REPO_ROOT / "edison-trajectories"
OUT_DIR.mkdir(parents=True, exist_ok=True)


QUERY = """
We are running tensegrity drop simulations (MuJoCo, Newton/Warp, PolyFEM+IPC)
and planning matching physical drop tests on a class-1 T-prism: 3 PLA struts
(rho ~ 1240 kg/m^3, E ~ 3.5 GPa) and 9 TPU 85A tendons (NinjaFlex-class:
E ~ 12 MPa secant, sigma_break ~ 26 MPa, rho ~ 1200 kg/m^3). Two regimes are
clamped to a Lansmont M23 envelope:

- `crutch_tip` (issue #18): 75 kg static payload through a Ø24 mm x 25 mm cell,
  impact velocity 1.4 m/s (~0.1 m drop), peak target <= 8 g (HAVS),
  pulse >= 5 ms.
- `nasa_lander` (issues #14, #16): 5 kg payload through a Ø200 mm x 200 mm cell,
  impact velocity 9.8 m/s (M23 max delta-V), peak target <= 1500 g (GSFC GEVS).

We have struggled with visualisation/simulation realism when the payload is
included. With the SUPERball / NASA-TBR architecture (payload sphere suspended
inside the cage by 6 additional TPU tendons), the soft 12 MPa TPU 85A
suspension oscillated wildly at impact and yanked the 0.7 g prism through the
rigid floor in MuJoCo. With the payload distributed across the struts as added
inertia (axial-load model, matching a crutch tip), the renders are stable and
look physical. The bare prism (no payload, just intrinsic strut/tendon mass)
is also stable. A reviewer therefore asked: **for these drop-tests, can we
just leave the payload off in the simulations**, and what does that cost us in
real-world applicability?

Please produce an in-depth, citation-rich brief that answers:

# 1. Physics of payload inclusion in drop simulations

  (a) Which impact-response metrics are dominated by the payload (mass,
      mounting, suspension stiffness) and which are dominated by the
      tensegrity cell itself? Cover at minimum: peak deceleration (g_max),
      pulse FWHM, specific energy absorption (SEA = E_abs / m_protector),
      volumetric efficiency (eta_V), force-time history shape, contact-
      patch evolution, tendon strain energy distribution, and modal
      response (drum-mode of suspended payload vs cell breathing mode).

  (b) For each of these four mounting modes, give the expected physical
      regimes in which the simulation/experiment **with no payload** is
      a faithful surrogate, and the regimes in which it is misleading
      (state explicit thresholds where possible):

      A. Axially-loaded strut tip (crutch use case, payload via tip).
      B. Payload rigidly clamped to one strut (instrumented accelerometer
         mass on a strut, common in tensegrity-robotics drop logs).
      C. Payload suspended inside the cage by additional TPU tendons
         (SUPERball v1/v2 + NASA-TBR planetary lander style).
      D. Bare cell + fictitious added inertia ("topology screen").

  (c) Quantify the regime where a no-payload simulation can be rescaled
      post-hoc to predict the payload-laden response (e.g. via lumped
      Maxwell/Kelvin models, m_eff = m_payload + alpha*m_strut, or
      shock-response-spectrum convolution). Cite analytic and empirical
      precedents.

  (d) For TPU 85A tendons specifically (E ~ 12 MPa, very soft), what
      stiffness/mass ratio thresholds set the boundary between "cell-
      dominated" and "payload-dominated" response? Provide closed-form or
      tabulated guidance keyed to k_cable, m_payload, drop height.

# 2. Real-world applicability and standards mapping

  (a) Which ASTM and equivalent standards explicitly require the payload
      to be in the load path during the drop, and which permit (or
      require) bare-package drops? Cover at minimum: ASTM D5276 (free-fall
      drop of loaded containers, **rigid concrete or steel impact surface**,
      preconditioning, drop orientations), ASTM F1292 (playground impact
      attenuation, instrumented headform), ASTM F2971 (AM test reporting),
      ISTA 1A/1H, MIL-STD-810H Method 516.8 (transit/crash hazard),
      GSFC GEVS-STD-7000B (spacecraft), and any applicable JEDEC (#28
      Lansmont M23 family), ANSI/AAMI, ISO 4180. For each, list:
      load condition, impact surface specification (concrete vs steel vs
      compliant plate), required payload representation (real vs surrogate
      mass vs mass-and-CG), instrumentation, and acceptance criteria.

  (b) What is the convention in published tensegrity drop literature on
      reporting payload-vs-no-payload? Cover Zhang 2018 (icosahedron,
      114.9 g -> 40.9-46.5 g, 1 m), Zhang 2022 (22-inch, 235 g peak, 20 m,
      20-drop life), Agogino 2018 NASA SUPERball, Vespignani 2018 SUPERball
      v2, Anand 2022 (75 m biodegradable), Pajunen 2019 (24-impact reuse),
      Bauer 2021 (octet vs tensegrity localisation), MER airbag papers,
      and BEAR / Snapp 2024 / Gongora 2020-2022. Indicate where the
      drop was with or without a representative payload, and what
      mass-and-CG surrogate (if any) was used.

  (c) For our two regimes specifically: does ASTM D5276 (for crutch /
      packaging) or GEVS (for the NASA-lander regime) require a
      representative payload? On what impact surface (we currently model
      a rigid MuJoCo floor; the standards typically call out a *rigid
      concrete pad >= 150 mm thick on a >= 1 m^3 concrete or steel
      base*)?

  (d) Egg-drop demo path (#46/#47): can the payload-free simulation be
      defended publicly as predictive of the egg-laden drop, or must we
      bring the egg/cradle into both the simulation and the experiment?
      The PR #47 follow-up (`f41b7034`) protocol shared a Ø 200 mm bounding
      sphere, m_sys <= 500 g, m_egg = 55 ± 5 g, rigid concrete floor per
      ASTM D5276; how should that protocol be amended if we want to use
      bare-cell simulations as the screening tier?

# 3. Recommendations and decision rules

  (a) State an explicit rule-of-thumb for when each of the four mounting
      modes (A-D above) is appropriate at simulation-tier C
      (MuJoCo/NTRT rigid screening), tier B (DiffPD/Newton mid-fidelity),
      and tier A (PolyFEM+IPC high-fidelity).

  (b) Give 5-10 concrete simulation/experimental design changes to our
      current setup that would maximise the predictive value of *bare-cell*
      drop simulations while leaving the eventual *payload-laden* drop
      experiment defensible (e.g. always co-report m_eff = m_cell +
      m_payload, always run a 2-point payload-sensitivity sweep, always
      simulate on a rigid concrete-equivalent floor with stated E and rho,
      tie GEVS / D5276 floor surface specs to MuJoCo solref/solimp, etc.).

  (c) For the rigid floor model: what concrete-pad parameters should we
      use in MuJoCo / PolyFEM+IPC to be representative of the ASTM D5276
      and GEVS floor? Give: target Young's modulus, density, restitution,
      friction, surface roughness, contact stiffness in MuJoCo's
      solref/solimp normalisation (current is solref="0.002 1",
      solimp="0.98 0.999 0.0001"), and PolyFEM dhat / IPC barrier
      parameters.

  (d) Provide a one-paragraph defensible answer we can paste into the PR
      saying "yes, leave the payload off for now in the sim because X,
      but plan to bring it in at tier B/A and at the physical drop because
      Y, and here is the floor surface spec we are using to match D5276 /
      GEVS".

Please cite peer-reviewed sources for every numerical claim and explicitly
flag where the answer is engineering judgement vs literature-grounded.
""".strip()


def main() -> None:
    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY")
    if not api_key:
        raise SystemExit("EDISON_PLATFORM_API_KEY / EDISON_API_KEY env var not set")

    client = EdisonClient(api_key=api_key)

    submitted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{submitted_at}] submitting LITERATURE_HIGH payload-vs-no-payload query")

    submitted = client.create_task(
        task_data={"name": JobNames.LITERATURE_HIGH, "query": QUERY},
    )
    trajectory_id = getattr(submitted, "trajectory_id", None) or str(submitted)
    print(f"  trajectory_id: {trajectory_id}")

    pointer = OUT_DIR / f"payload-vs-no-payload-{trajectory_id}-SUBMITTED.json"
    pointer.write_text(
        json.dumps(
            {
                "trajectory_id": trajectory_id,
                "submitted_at": submitted_at,
                "job": "LITERATURE_HIGH",
                "topic": "payload vs no-payload in tensegrity drop sims",
                "related_issues": [46, 47, 50, 16, 28, 18, 49, 14, 45],
            },
            indent=2,
        )
    )
    print(f"  pointer: {pointer.relative_to(REPO_ROOT)}")

    # Poll for up to ~45 min, bounded so the session does not stall.
    deadline = time.time() + 45 * 60
    poll_every = 30
    last_status = None
    while time.time() < deadline:
        status_resp = client.get_task_status(trajectory_id=trajectory_id)
        status = getattr(status_resp, "status", None) or str(status_resp)
        if status != last_status:
            print(f"  [{datetime.now(timezone.utc).strftime('%H:%M:%S')}] status: {status}")
            last_status = status
        if str(status).lower() in {"success", "failed", "error", "cancelled"}:
            break
        time.sleep(poll_every)

    # Fetch
    try:
        result = client.get_task(trajectory_id=trajectory_id, verbose=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  fetch failed: {exc!r}")
        return

    md_path = OUT_DIR / f"payload-vs-no-payload-{trajectory_id}.md"
    json_path = OUT_DIR / f"payload-vs-no-payload-{trajectory_id}.json"
    formatted = getattr(result, "formatted_answer", None) or ""
    md_path.write_text(
        f"# Edison literature brief: payload vs no-payload in tensegrity drop "
        f"sims/experiments\n\n"
        f"- **Task ID:** `{trajectory_id}`\n"
        f"- **Job:** `LITERATURE_HIGH`\n"
        f"- **Submitted:** {submitted_at}\n"
        f"- **Fetched:** {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- **Status:** {getattr(result, 'status', 'unknown')}\n"
        f"- **Related issues/PRs:** #46, #47, #50, #16, #28, #18, #49, #14, #45\n\n"
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
