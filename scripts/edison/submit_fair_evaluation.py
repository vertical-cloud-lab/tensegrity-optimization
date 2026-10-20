"""
Submit an ANALYSIS (data-analysis-crow-high) Edison Scientific query asking for
mock feedback on our *thinking* about how to make the tensegrity-absorber
objective evaluations FAIR with respect to mass, volume, and contact area --
especially for the scaled-up lander module.

Triggered by PR comment 4760939061 (@sgbaird): "Not sure to what extent any of
these are 'fair' tasks. I.e., primarily in terms of mass, volume, and contact
area. Suggest ways to make these evaluations for the different objectives fair,
especially for the lander problem. ... Would we normalize the objectives ad-hoc
or change the way the search space is represented so that certain constraints are
always met? E.g., constant mass, fixed contact area, volume, etc. Send to Edison
for mock feedback on the thinking."

Uploaded context (bundled as a single Edison data collection):
  analysis
    - fair_evaluation_analysis.md : our fairness write-up (the thinking under
                                    review) + recommended routes
    - pareto_render_campaign.md   : the dense Tier-C Pareto-front campaign whose
                                    "fat/short/large-radius wins" result motivates
                                    the fairness question
    - sobol_t3_diagnostics.md     : artifact-vs-physics diagnostics (F_peak is a
                                    support-load/contact proxy; SEA is an elastic
                                    proxy)
    - regimes.py                  : the crutch / nasa_lander loading + envelope
                                    definitions and the Lansmont M23 test box
    - bo_evaluator.py             : the sim->BO bridge defining F_peak/SEA/eta
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import time
from datetime import datetime, timezone

os.environ.setdefault(
    "EDISON_PLATFORM_API_KEY",
    os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY", ""),
)

from edison_client import EdisonClient, JobNames  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SIM = REPO_ROOT / "simulations"
OUT_DIR = REPO_ROOT / "edison-trajectories" / "fair-evaluation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BUNDLE_DIR = pathlib.Path(
    os.environ.get("EDISON_BUNDLE_DIR", "/tmp/edison_fair_eval_bundle")
)

STATIC_FILES = [
    SIM / "fair_evaluation_analysis.md",
    SIM / "pareto_render_campaign.md",
    SIM / "sobol_t3_diagnostics.md",
    SIM / "regimes.py",
    SIM / "bo_evaluator.py",
]


QUERY = """
# Project context

We design and 3D-print class-1 tensegrity cells (3 rigid PLA struts, E=3.5 GPa,
rho=1240 kg/m^3; 9 soft TPU 85A tendons, E~12 MPa) in a T3 triangular-prism
topology as compact, tunable impact absorbers, and run a simulation +
Bayesian-optimization framework to find good designs that we then validate on a
3D printer + drop-tower + Instron. We study two loading regimes that reuse the
same unit cell: crutch_tip (75 kg @ ~1.4 m/s; HAVS peak constraint <= 8 g) and
nasa_lander (5 kg @ ~9.8 m/s; GSFC GEVS peak constraint <= 1500 g). Three
objectives: peak transmitted force F_peak_N (minimize), specific energy
absorption SEA_J_per_g (maximize), and compaction/stroke efficiency eta
(maximize). The drop-tower is a Lansmont M23 (<= 5000 g, >= 0.25 ms, <= 9.8 m/s,
<= 36 kg payload).

# The concern we want feedback on

Our Sobol / Pareto / BO campaigns draw designs from a 5-D box
(R_mm in [25,40], H_mm in [60,110], twist_deg in [40,80], strut_d_mm in [6,12],
cable_d_mm in [3.0,5.5]) and score them with a fixed loading scenario per regime.
But every corner of that box is a physically DIFFERENT-SIZED object: across the
box the cell mass varies 6.2x (9.5 -> 59 g), the circumscribing envelope volume
4.7x (118 -> 553 cm^3), and the strut-tip footprint area 4.0x (85 -> 339 mm^2).
So when the campaign reports "fat, short, large-radius cells win on SEA," that is
partly a tautology -- those cells simply have more material, volume, and contact
area. Of our three objectives only SEA is mass-normalized (SEA = strain_energy *
payload_mass / cell_mass); none control for volume or footprint; and F_peak at
our cheap Tier-C fidelity is a support-load / contact-area proxy (it tracks the
static support load), so it is contact-area- and stiffness-dominated rather than
mechanics-dominated. The crutch tolerates this (loose envelope) but for the
LANDER, mass and volume are the BINDING constraints, so letting the optimizer
"win by getting bigger" breaks the problem.

# What we are proposing (the thinking under review -- see fair_evaluation_analysis.md)

Real scaled-up lander-module constraints: (1) a hard MASS budget (absorber mass
is a fraction of landed mass -- single-digit %); (2) stowed/deployed ENVELOPE
VOLUME (fairing / CubeSat-U allocation); (3) FOOTPRINT / contact area setting
ground pressure on regolith and the tip-over stability cone (both a cap and a
floor); (4) crush STROKE long enough to hold peak g under GEVS at 9.8 m/s but
short enough to fit the deployed envelope; (5) SEA specified per unit mass AND
per unit volume.

Two routes to fairness (plus a hybrid we lean toward):
  Route A -- RE-PARAMETERIZE the search space so the budget is met by
  construction: a constant-mass manifold (fix total cell mass m*, solve one axis
  like cable_d or strut_d to hit it), a constant-envelope manifold (fix pi*R^2*H),
  a constant-footprint manifold, or scale-free SHAPE RATIOS (H/R, H/strut_d,
  cable_d/strut_d, twist) plus ONE explicit scale variable (mass or size) that is
  either fixed by the budget or carried as a separately-costed axis.
  Route B -- keep the box but make the OBJECTIVES/CONSTRAINTS size-aware: report
  intensive objectives (SEA_J_per_g AND SEA_J_per_cm^3, base-reaction peak g
  instead of the payload-accel proxy, ground pressure = reaction/footprint), and
  add cell_mass <= m*, envelope_vol <= V*, footprint in [A_min, A_max] as Ax
  OUTCOME CONSTRAINTS solved with constrained qNEHVI; or carry mass/volume as a
  cost (cost-aware acquisition) or an explicit 4th objective.
  Hybrid (recommended for the lander): Route A on the binding mass budget +
  scale-free shape ratios, with envelope volume and footprint as outcome
  constraints, scoring intensive objectives.

# What we need from you (act as a rigorous mock reviewer; cite where possible)

A. Is our diagnosis correct that the current campaign is size-confounded and that
   this specifically breaks the LANDER objective comparison? Anything we have
   mischaracterized about which objective normalizes what?
B. For a scaled-up tensegrity lander crush-core / shock-isolator module, what ARE
   the real design constraints and typical budget VALUES we should target (mass
   fraction of landed mass, J/g and J/cm^3 specific-absorption figures of merit,
   ground-pressure / footprint limits on regolith, stroke/standoff)? Cite
   heritage crush-core / airbag / honeycomb / SUPERball / MER / GEVS numbers
   where you can.
C. NORMALIZE THE OBJECTIVES (ad hoc) vs RE-PARAMETERIZE THE SEARCH SPACE (so
   constraints always hold): which is methodologically sounder for fair
   multi-objective BO, and when? Is a constant-mass / constant-volume MANIFOLD
   (lower-dimensional feasible set) preferable to a rectangular box with outcome
   constraints, given GP modeling and qNEHVI behavior on constrained vs
   manifold-restricted domains? Cite the relevant BO / design-of-experiments /
   dimensional-analysis (Buckingham-pi / similitude) literature.
D. If we DO use outcome constraints, how should mass/volume/footprint and the
   HAVS (<= 8 g) / GEVS (<= 1500 g) peak-g limits be encoded -- hard constraints,
   soft penalties, or a feasibility-weighted (constrained qNEHVI) acquisition --
   and how does that interact with our biased cheap Tier-C simulator?
E. A prioritized, actionable list: the 3-5 highest-value changes to make the
   evaluations fair (especially for the lander), and which to implement first.

Use fair_evaluation_analysis.md as the primary artifact under review; regimes.py
and bo_evaluator.py are ground truth for the loading definitions and the
F_peak/SEA/eta math; pareto_render_campaign.md and sobol_t3_diagnostics.md show
the size-confounded result and the support-load/elastic-proxy caveats.
""".strip()


def _assemble_bundle() -> list[pathlib.Path]:
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    BUNDLE_DIR.mkdir(parents=True)
    copied: list[pathlib.Path] = []
    for src in STATIC_FILES:
        if src.is_file():
            shutil.copy2(src, BUNDLE_DIR / src.name)
            copied.append(src)
        else:
            print(f"  skip missing {src.relative_to(REPO_ROOT)}")
    return copied


def _attach_bundle(client: EdisonClient) -> list[str]:
    print(f"  uploading bundle {BUNDLE_DIR} as a collection ...")
    resp = client.store_file_content(
        name="fair-evaluation",
        file_path=str(BUNDLE_DIR),
        description=(
            "Fairness-of-objective-evaluation thinking (fair_evaluation_analysis.md) "
            "for the tensegrity impact-absorber BO campaign: mass/volume/contact-area "
            "confound, scaled-up lander constraints, normalize-vs-reparameterize routes"
        ),
        as_collection=True,
    )
    storage_id = getattr(getattr(resp, "data_storage", None), "id", None)
    if storage_id is None:
        storage_id = getattr(resp, "id", None)
    print(f"  data_storage id: {storage_id}")
    return [f"data_entry:{storage_id}"] if storage_id else []


def _extract_answer(result) -> str:
    formatted = getattr(result, "formatted_answer", None) or ""
    try:
        ef = result.environment_frame
        ef_d = ef.model_dump() if hasattr(ef, "model_dump") else ef
        state = ef_d["state"]["state"]
        if isinstance(state.get("answer"), str) and state["answer"].strip():
            return state["answer"]
        answer = state["response"]["answer"]
        return answer.get("formatted_answer") or formatted
    except Exception:  # noqa: BLE001
        try:
            dump = result.model_dump()
            if isinstance(dump.get("answer"), str) and dump["answer"].strip():
                return dump["answer"]
        except Exception:  # noqa: BLE001
            pass
        return formatted


def main() -> None:
    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get(
        "EDISON_API_KEY"
    )
    if not api_key:
        raise SystemExit("EDISON_PLATFORM_API_KEY / EDISON_API_KEY env var not set")

    client = EdisonClient(api_key=api_key.strip())

    copied = _assemble_bundle()
    print(f"  bundled {len(copied)} files")
    files = _attach_bundle(client)

    submitted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{submitted_at}] submitting ANALYSIS fair-evaluation query")

    submitted = client.create_task(
        task_data={"name": JobNames.ANALYSIS, "query": QUERY},
        files=files or None,
    )
    task_id = getattr(submitted, "trajectory_id", None) or str(submitted)
    print(f"  task id: {task_id}")

    pointer = OUT_DIR / f"fair-evaluation-{task_id}-SUBMITTED.json"
    pointer.write_text(
        json.dumps(
            {
                "task_id": task_id,
                "submitted_at": submitted_at,
                "job": "ANALYSIS",
                "topic": "mock feedback on making the objective evaluations fair "
                "(mass/volume/contact area) for the tensegrity impact-absorber BO, "
                "especially the scaled-up lander module",
                "uploaded_files": [p.name for p in copied],
                "related_issues_prs": [14, 16, 30, 35],
                "pr_comment": 4760939061,
            },
            indent=2,
        )
    )
    print(f"  pointer: {pointer.relative_to(REPO_ROOT)}")

    deadline = time.time() + 45 * 60
    poll_every = 30
    last_status = None
    while time.time() < deadline:
        try:
            status_resp = client.get_task(task_id=task_id, lite=True)
        except Exception as exc:  # noqa: BLE001
            print(f"  status poll failed: {exc!r}")
            time.sleep(poll_every)
            continue
        status = getattr(status_resp, "status", None) or str(status_resp)
        if status != last_status:
            print(
                f"  [{datetime.now(timezone.utc).strftime('%H:%M:%S')}] "
                f"status: {status}"
            )
            last_status = status
        if str(status).lower() in {"success", "failed", "error", "cancelled"}:
            break
        time.sleep(poll_every)

    try:
        result = client.get_task(task_id=task_id, verbose=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  fetch failed: {exc!r}")
        return

    md_path = OUT_DIR / f"fair-evaluation-{task_id}.md"
    json_path = OUT_DIR / f"fair-evaluation-{task_id}.json"
    formatted = _extract_answer(result)
    md_path.write_text(
        f"# Edison ANALYSIS brief: making the objective evaluations fair "
        f"(mass / volume / contact area)\n\n"
        f"- **Task ID:** `{task_id}`\n"
        f"- **Job:** `ANALYSIS`\n"
        f"- **Submitted:** {submitted_at}\n"
        f"- **Fetched:** "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- **Status:** {getattr(result, 'status', 'unknown')}\n"
        f"- **PR comment:** 4760939061\n\n"
        f"---\n\nQuestion:\n\n{QUERY}\n\n---\n\n{formatted}\n"
    )
    try:
        json_path.write_text(result.model_dump_json(indent=2))
    except Exception:  # noqa: BLE001
        json_path.write_text(json.dumps(result, default=str, indent=2))
    print(f"  wrote {md_path.relative_to(REPO_ROOT)}")
    print(f"  wrote {json_path.relative_to(REPO_ROOT)}")
    if pointer.exists() and formatted.strip():
        pointer.unlink()


if __name__ == "__main__":
    main()
