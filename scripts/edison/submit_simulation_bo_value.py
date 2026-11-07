"""
Submit an ANALYSIS (data-analysis-crow-high) Edison Scientific query asking how
our multi-fidelity drop simulations can feed value into both (a) the PR #35
T3-prism Bayesian-optimization campaign and (b) the high-fidelity manual
validation measurements (drop-tower / Instron), plus what useful information the
simulations could surface for the PLA-strut + TPU-85A-tendon structures that the
printer and bench tests cannot cheaply provide.

Triggered by PR comment 4663414812 (@sgbaird): "how would these simulation
results feed into the BO campaign from PR #35 ... afterwards send an Edison
query (ANALYSIS) with the relevant files uploaded (the BO script, a sim script,
the manuscript draft)."

Uploaded context (bundled as an Edison data collection):
  - t3_prism_sobol_batch.py   : PR #35 single-batch Sobol design generator
                                 (the BO entry point this work plugs into).
  - bo_evaluator.py           : our sim->BO bridge (PR #30/#35 schema ->
                                 PrintableDesign -> run_regimes.simulate ->
                                 {F_peak_N, SEA_J_per_g, eta}); includes the
                                 +120 deg CAD->sim twist-convention fix.
  - run_regimes_simulation.py : the MuJoCo tier-C regime simulator the bridge
                                 calls (crutch_tip / nasa_lander).
  - manuscript-body.tex       : current manuscript draft (for framing/claims).
"""

from __future__ import annotations

import json
import os
import pathlib
import time
from datetime import datetime, timezone

# edison-client reads EDISON_PLATFORM_API_KEY; fall back to EDISON_API_KEY.
os.environ.setdefault(
    "EDISON_PLATFORM_API_KEY",
    os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY", ""),
)

from edison_client import EdisonClient, JobNames  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "edison-trajectories" / "simulation-bo-value"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Directory holding the files to attach to the task (assembled by the caller).
BUNDLE_DIR = pathlib.Path(
    os.environ.get("EDISON_BUNDLE_DIR", "/tmp/edison_bundle")
)


QUERY = """
We have a multi-fidelity simulation stack for drop-impact response of class-1
tensegrity cells (3 PLA struts E=3.5 GPa rho=1240; 9 TPU 85A tendons, E~12 MPa
secant, sigma_break~26 MPa; T3-prism topology) for two regimes: crutch_tip
(75 kg @ 1.4 m/s, ~Ø24x25 mm cell, HAVS peak <= 8 g) and nasa_lander
(5 kg @ 9.8 m/s, ~Ø200x200 mm cell, GEVS peak <= 1500 g). Tiers: (C) MuJoCo
rigid-strut + tendon screening (~0.1 s/design on 1 CPU core); (B) NVIDIA Newton
(Warp XPBD, differentiable) + DiffPD; (A) PolyFEM+IPC NeoHookean on a welded
strut+tendon volumetric mesh.

We are wiring tier-C into the PR #35 T3-prism Bayesian-optimization campaign
(t3_prism_sobol_batch.py). That script currently only emits a Sobol design set
with a *placeholder* objective and reports no data back. Our bridge
(bo_evaluator.py) maps the PR #35 parameter schema (R_mm[25,40], H_mm[60,110],
twist_deg[40,80], strut_d_mm[6,12], cable_d_mm[3.0,5.5]) -> a PrintableDesign ->
run_regimes.simulate(regime) -> objectives {F_peak_N, SEA_J_per_g, eta}
(eta = compaction/stroke efficiency). The same objective space is what the
drop-tower experiments (PR #74 accelerometer + SAE J211 CFC-180 filtered peak g;
PR #67 drop protocol) and Instron tests measure, so simulated and measured rows
can attach to the same Ax/BoTorch model.

We need a rigorous, citation-backed analysis answering:

# 1. Value of cheap simulation inside the BO loop
Given tier-C costs ~0.1 s/design vs. days per printed+drop-tested specimen, how
should we best use the simulator inside a sequential / batch BO campaign? Cover
concretely: (a) multi-fidelity / multi-task BO formulations (e.g.,
MF-MES, trace-aware knowledge gradient, BoTorch SingleTaskMultiFidelityGP /
Ax multi-task) that fuse cheap-sim + expensive-experiment observations on the
shared {F_peak, SEA, eta} objective space; (b) using the simulator to seed /
warm-start the GP prior or as a cheap "screening" pre-filter before committing a
specimen to print; (c) cost-aware acquisition (cost per fidelity) and when the
expected value of a tier-C / tier-B eval exceeds its cost; (d) the risk of model
discrepancy / bias between sim and bench, and the standard ways to correct it
(discrepancy/bias GP a la Kennedy-O'Hagan, delta-modelling, autoregressive
co-kriging). Cite the BO + multi-fidelity literature.

# 2. What the simulations can tell us that the printer/bench cannot cheaply
Enumerate specific quantities the sims expose per design that are hard or
expensive to measure experimentally and would improve the campaign: e.g.,
full-field strut/tendon strain history, contact sequence / buckling onset, energy
partition (tendon vs. strut vs. contact), sensitivity gradients (Newton/DiffPD
differentiability) for gradient-informed BO, and the class-1 feasibility / strut
self-collision screen. Which of these are trustworthy at tier C vs. require
tier A/B?

# 3. Value for the high-fidelity manual validation measurements
How should simulation outputs shape the *experimental* program (drop-tower /
Instron)? e.g., which designs to physically test first (max-information / D-
optimal under the surrogate), what instrumentation to add (where peak strain
localizes), what loading rate / drop height brackets the regimes, and how to set
up the sim-vs-experiment comparison so the bench data can recalibrate the sim
(which scalar + which curves to compare; SAE J211 filtering parity).

# 4. Objective trade-offs and regime handling
We see peak-force vs. SEA vs. compaction-efficiency (eta) trade-offs that differ
sharply by regime (lander: F_peak ~kN, eta ~0.7; crutch: eta ~0.96, cushion-
limited). Should we run one BO campaign per regime or a single multi-objective /
multi-task campaign? Recommend the objective formulation (scalarization vs. EHVI
Pareto) and any constraints (HAVS <= 8 g, GEVS <= 1500 g) to encode.

# 5. Concrete recommendations
A prioritized, actionable list: the specific BoTorch/Ax components to use, the
order of operations to integrate bo_evaluator.py into t3_prism_sobol_batch.py,
and 3-5 immediate next experiments. Flag where advice is engineering judgement
vs. literature-grounded, with citations.

Use the attached files (the PR #35 BO script, our sim->BO bridge, the tier-C
simulator, and the manuscript draft) as ground truth for what we have built.
""".strip()


def _attach_bundle(client: EdisonClient) -> list[str]:
    """Upload the bundle dir as a collection; return create_task file refs."""
    if not BUNDLE_DIR.is_dir():
        print(f"  bundle dir {BUNDLE_DIR} missing; submitting without files")
        return []
    print(f"  uploading bundle {BUNDLE_DIR} as a collection ...")
    resp = client.store_file_content(
        name="simulation-bo-value-context",
        file_path=str(BUNDLE_DIR),
        description=(
            "PR #35 BO script, sim->BO bridge, tier-C simulator, manuscript draft"
        ),
        as_collection=True,
    )
    storage_id = getattr(getattr(resp, "data_storage", None), "id", None)
    if storage_id is None:
        storage_id = getattr(resp, "id", None)
    print(f"  data_storage id: {storage_id}")
    return [f"data_entry:{storage_id}"] if storage_id else []


def main() -> None:
    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get(
        "EDISON_API_KEY"
    )
    if not api_key:
        raise SystemExit("EDISON_PLATFORM_API_KEY / EDISON_API_KEY env var not set")

    client = EdisonClient(api_key=api_key)

    files = _attach_bundle(client)

    submitted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{submitted_at}] submitting ANALYSIS simulation-bo-value query")

    submitted = client.create_task(
        task_data={"name": JobNames.ANALYSIS, "query": QUERY},
        files=files or None,
    )
    trajectory_id = getattr(submitted, "trajectory_id", None) or str(submitted)
    print(f"  trajectory_id: {trajectory_id}")

    pointer = OUT_DIR / f"simulation-bo-value-{trajectory_id}-SUBMITTED.json"
    pointer.write_text(
        json.dumps(
            {
                "trajectory_id": trajectory_id,
                "submitted_at": submitted_at,
                "job": "ANALYSIS",
                "topic": "value of multi-fidelity sims for the PR #35 T3-prism BO "
                "campaign and the high-fidelity manual validation",
                "uploaded_files": [p.name for p in sorted(BUNDLE_DIR.glob("*"))]
                if BUNDLE_DIR.is_dir()
                else [],
                "related_issues_prs": [24, 30, 35, 67, 74],
                "pr_comment": 4663414812,
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
            status_resp = client.get_task(task_id=trajectory_id, lite=True)
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
        result = client.get_task(task_id=trajectory_id, verbose=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  fetch failed: {exc!r}")
        return

    md_path = OUT_DIR / f"simulation-bo-value-{trajectory_id}.md"
    json_path = OUT_DIR / f"simulation-bo-value-{trajectory_id}.json"
    formatted = getattr(result, "formatted_answer", None) or ""
    try:
        ef = result.environment_frame
        ef_d = ef.model_dump() if hasattr(ef, "model_dump") else ef
        state = ef_d["state"]["state"]
        # ANALYSIS (crow) jobs put the answer at state.state.answer;
        # paperqa jobs nest it under state.state.response.answer.formatted_answer.
        if isinstance(state.get("answer"), str) and state["answer"].strip():
            formatted = state["answer"]
        else:
            answer = state["response"]["answer"]
            formatted = answer.get("formatted_answer") or formatted
    except Exception:  # noqa: BLE001
        pass
    md_path.write_text(
        f"# Edison ANALYSIS brief: value of multi-fidelity simulations for the "
        f"PR #35 T3-prism BO campaign and high-fidelity validation\n\n"
        f"- **Task ID:** `{trajectory_id}`\n"
        f"- **Job:** `ANALYSIS`\n"
        f"- **Submitted:** {submitted_at}\n"
        f"- **Fetched:** "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
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
