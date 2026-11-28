"""
Submit an ANALYSIS (data-analysis-crow-high) Edison Scientific query that hands
Edison the *results of the simulation-only Bayesian-optimization campaign*
(`simulations/sim_bo_campaign.py`) — the campaign script, the per-(tier, regime,
seed) trial CSVs, the convergence / Pareto / LOO-CV figures, and our write-up —
and asks for mock-reviewer feedback, an analysis of where the surrogate is and
is not learning predictive signal, and recommendations on how to incorporate
*contextual information* into the Bayesian-optimization campaign.

Triggered by PR comment 4760173539 (@sgbaird): "send all of these figures/data
to Edison analysis for mock reviewer feedback and analysis of where signal is or
isn't and provide recommendations on what this means for incorporating
contextual information into the Bayesian optimization campaign. Fetch this
session. Report back findings. Implement any follow-up recommendations".

Uploaded context (bundled as a single Edison data collection):
  scripts
    - sim_bo_campaign.py   : the tier/seed-parameterized closed-loop driver
                             (Ax AxClient: Sobol -> BOTORCH_MODULAR qNEHVI at
                             Tier-C, single-objective F_peak at Tier-B).
    - bo_evaluator.py      : sim->BO bridge (PR #35 schema -> PrintableDesign
                             -> run_regimes.simulate -> {F_peak, SEA, eta}).
  data (one CSV per (tier, regime); + the feasible Pareto subset)
    - sim_bo_C_crutch.csv, sim_bo_C_lander.csv      (MuJoCo tier-C, 3 obj)
    - sim_bo_B_crutch.csv, sim_bo_B_lander.csv      (Newton tier-B, F_peak)
    - sim_bo_<tier>_<regime>_pareto.csv
  figures
    - sim_bo_<tier>_<regime>_convergence.png        (mean running-best +-1 sigma)
    - sim_bo_<tier>_<regime>_seed<k>_convergence.png
    - sim_bo_<tier>_<regime>_seed<k>_pareto.png
    - sim_bo_<tier>_<regime>_seed<k>_cv.png         (Ax LOO cross-validation)
  analysis
    - sim_bo_campaign.md, bo_integration.md
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import time
from datetime import datetime, timezone

# edison-client reads EDISON_PLATFORM_API_KEY; fall back to EDISON_API_KEY.
os.environ.setdefault(
    "EDISON_PLATFORM_API_KEY",
    os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY", ""),
)

from edison_client import EdisonClient, JobNames  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SIM = REPO_ROOT / "simulations"
OUT = SIM / "outputs"
OUT_DIR = REPO_ROOT / "edison-trajectories" / "sim-bo-review"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BUNDLE_DIR = pathlib.Path(
    os.environ.get("EDISON_BUNDLE_DIR", "/tmp/edison_sim_bo_bundle")
)

# Static (always-attached) files, relative to REPO_ROOT. Missing files are
# skipped (the branch may be a shallow/grafted clone).
STATIC_FILES = [
    SIM / "sim_bo_campaign.py",
    SIM / "bo_evaluator.py",
    SIM / "sim_bo_campaign.md",
    SIM / "bo_integration.md",
]

# Glob every sim-BO data/figure artifact the campaign emitted.
GLOB_PATTERNS = [
    "sim_bo_*.csv",
    "sim_bo_*.png",
]


QUERY = """
# Project context and why we are exploring this

We are designing and 3D-printing class-1 tensegrity cells (3 rigid PLA struts,
E=3.5 GPa, rho=1240 kg/m^3; 9 soft TPU 85A tendons, E~12 MPa secant) in a
T3-triangular-prism topology as compact, tunable impact-absorbers. The program
goal is to build a simulation + Bayesian-optimization (BO) framework that (1)
generalizes to more advanced tensegrity structures and (2) yields real,
experimentally-validated "best" T3-prism designs on the bench (3D printer +
drop-tower + Instron). We study two impact regimes: crutch_tip (75 kg @
~1.4 m/s, anti-vibration HAVS peak constraint <= 8 g) and nasa_lander (5 kg @
~9.8 m/s, GEVS peak constraint <= 1500 g). The three objectives are peak
transmitted force (F_peak_N, minimize), specific energy absorption
(SEA_J_per_g, maximize), and compaction/stroke efficiency (eta, maximize).

# What we actually ran (attached)

`sim_bo_campaign.py` is a CLOSED-LOOP, simulation-ONLY analogue of our PR #35
hardware Sobol batch: Ax (AxClient, Sobol -> BOTORCH_MODULAR) proposes a design
over the exact PR #35 design box (R_mm in [25,40], H_mm in [60,110],
twist_deg in [40,80], strut_d_mm in [6,12], cable_d_mm in [3.0,5.5]); a
simulation scores it; the result feeds straight back to the surrogate. We ran it
across a simulation FIDELITY ladder, per loading regime, with multiple random
seeds (seeded by the three already-printed PR #35 T3 cells):

  - Tier C (MuJoCo rigid-tendon regime sim, CFC-180-filtered axial accel,
    ~0.2 s/eval): 3-objective qNEHVI on {F_peak_N (min), SEA_J_per_g (max),
    eta (max)}; 3 seeds x ~33 evals per regime.
  - Tier B (NVIDIA Newton / Warp XPBD drop, TPU tendons in the dynamic load
    path, ~4 s/eval): SINGLE-objective min F_peak_N (Newton only exposes the
    payload-accel trace); 2 seeds x ~18 evals per regime.

The objectives map onto exactly what our drop-tower (PR #74 accelerometer +
SAE J211 CFC-180) and Instron experiments measure, so simulated and measured
trials can attach to the same Ax/BoTorch model.

Attached: the campaign driver (sim_bo_campaign.py), the sim->BO bridge
(bo_evaluator.py), one trial CSV per (tier, regime) plus the feasible Pareto
subset CSVs, and the figures: per-seed and mean+-1sigma convergence, per-seed
Pareto fronts, and the Ax leave-one-out cross-validation (LOO-CV) scatter for
each seed/model. Our own write-up is sim_bo_campaign.md (+ bo_integration.md).

# Key empirical observations we want you to check and interpret

1. Tier-C F_peak is near-invariant across the whole box (crutch span ~4.4%,
   lander ~3.5%) and sits at the static support load (crutch median
   F_peak/(75 kg*g) ~ 1.0); SEA is the live discriminator (crutch span ~27x,
   lander ~7.5x). So the Tier-C Pareto fronts are nearly vertical.
2. Tier-B (Newton) F_peak IS strongly design-dependent (~2.5x span), so its
   single-objective loop genuinely descends -- the elastic tendons resolve a
   design-dependent impact peak the rigid-contact tier cannot.
3. LOO-CV (R^2 / Spearman of CV-predicted vs observed, mean over seeds):
   Tier-C crutch SEA 0.97/0.96 (strong); Tier-C lander F_peak 0.91/0.95;
   Tier-B F_peak 0.99/0.91-0.92; but Tier-C lander eta 0.80/0.61 and Tier-C
   crutch F_peak 0.89/0.79 look weaker -- we believe the weak ones are because
   the OUTCOME ITSELF is nearly constant across the box (e.g. lander eta pinned
   at 0.732-0.734), not because the model failed to fit. Please confirm or
   refute from the CV figures/CSVs.
4. twist_deg carries ~0 signal at both tiers because neither the Tier-C regime
   override nor the Newton build consumes the twist axis (geometry is built at
   the fixed equilibrium twist) -- a plumbing limitation, not physics.

# What we need from you (act as a rigorous mock reviewer; cite where possible)

A. Mock-reviewer critique of this simulation-only BO campaign and the claims in
   sim_bo_campaign.md: are the conclusions sound given the attached CSVs and the
   LOO-CV figures? Flag over-claims and setup artifacts.
B. WHERE IS THERE PREDICTIVE SIGNAL AND WHERE IS THERE NOT? Use the LOO-CV data
   per (tier, regime, outcome, seed) to separate "the GP cannot learn this" from
   "this outcome is intrinsically near-constant so there is nothing to learn."
   Recommend better signal diagnostics if ours are insufficient.
C. RECOMMENDATIONS FOR INCORPORATING CONTEXTUAL INFORMATION INTO THE BO. This is
   the core ask. Given a cheap biased simulator (Tier-C), a costlier higher-
   fidelity simulator (Tier-B/A), two loading regimes, and eventual real bench
   data, how should we encode the available CONTEXT/SIDE-INFORMATION into the
   surrogate and acquisition? Specifically address: multi-fidelity / multi-task
   GPs (regime as a task, fidelity as a task/context); contextual / composite-
   objective BO; informative priors and physics-derived features (e.g. strut
   L*d^2 mass, equilibrium-twist plumbing) as inputs or mean functions;
   discrepancy/bias models (Kennedy-O'Hagan, autoregressive co-kriging) to fuse
   sim + bench; and cost-aware acquisition. Cite the relevant BO literature.
D. Objective/constraint formulation: one campaign per regime vs. a single
   multi-task / multi-objective (qNEHVI) campaign, and how to encode the HAVS
   (<= 8 g) / GEVS (<= 1500 g) constraints as outcome constraints.
E. A prioritized, actionable next-steps list: the 3-5 highest-information
   changes to the framework, and which designs to physically print/drop-test
   first to validate the simulated Pareto front.

Use the attached scripts, data, and figures as ground truth for what we have.
""".strip()


def _assemble_bundle() -> list[pathlib.Path]:
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    BUNDLE_DIR.mkdir(parents=True)
    copied: list[pathlib.Path] = []
    seen: set[str] = set()
    sources = list(STATIC_FILES)
    for pattern in GLOB_PATTERNS:
        sources.extend(sorted(OUT.glob(pattern)))
    for src in sources:
        if src.name in seen:
            continue
        if src.is_file():
            shutil.copy2(src, BUNDLE_DIR / src.name)
            copied.append(src)
            seen.add(src.name)
        else:
            print(f"  skip missing {src.relative_to(REPO_ROOT)}")
    return copied


def _attach_bundle(client: EdisonClient) -> list[str]:
    print(f"  uploading bundle {BUNDLE_DIR} as a collection ...")
    resp = client.store_file_content(
        name="sim-bo-review",
        file_path=str(BUNDLE_DIR),
        description=(
            "Simulation-only closed-loop BO campaign (sim_bo_campaign.py): "
            "driver + sim->BO bridge, per-(tier,regime) trial CSVs, "
            "convergence/Pareto/LOO-CV figures, and write-ups"
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
        # edison-client 0.14.0 surfaces the answer at the top level too.
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
    print(f"[{submitted_at}] submitting ANALYSIS sim-bo-review query")

    submitted = client.create_task(
        task_data={"name": JobNames.ANALYSIS, "query": QUERY},
        files=files or None,
    )
    task_id = getattr(submitted, "trajectory_id", None) or str(submitted)
    print(f"  task id: {task_id}")

    pointer = OUT_DIR / f"sim-bo-review-{task_id}-SUBMITTED.json"
    pointer.write_text(
        json.dumps(
            {
                "task_id": task_id,
                "submitted_at": submitted_at,
                "job": "ANALYSIS",
                "topic": "mock-reviewer feedback + predictive-signal analysis + "
                "contextual-information recommendations for the simulation-only "
                "closed-loop BO campaign",
                "uploaded_files": [p.name for p in copied],
                "related_issues_prs": [30, 35, 74],
                "pr_comment": 4760173539,
            },
            indent=2,
        )
    )
    print(f"  pointer: {pointer.relative_to(REPO_ROOT)}")

    # Poll up to ~45 min so we can fetch in the same session.
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

    md_path = OUT_DIR / f"sim-bo-review-{task_id}.md"
    json_path = OUT_DIR / f"sim-bo-review-{task_id}.json"
    formatted = _extract_answer(result)
    md_path.write_text(
        f"# Edison ANALYSIS brief: mock review of the simulation-only "
        f"closed-loop BO campaign\n\n"
        f"- **Task ID:** `{task_id}`\n"
        f"- **Job:** `ANALYSIS`\n"
        f"- **Submitted:** {submitted_at}\n"
        f"- **Fetched:** "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- **Status:** {getattr(result, 'status', 'unknown')}\n"
        f"- **PR comment:** 4760173539\n\n"
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
