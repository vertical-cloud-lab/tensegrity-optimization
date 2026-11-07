"""
Submit an ANALYSIS (data-analysis-crow-high) Edison Scientific query that hands
Edison the *actual results* of the PR #35 T3-prism Sobol simulation campaign —
the campaign scripts, the measured CSV data, and the analysis figures — together
with context about the project and why we are exploring it, and asks for an
interpretation / critique and recommendations.

Triggered by PR comment 4713093337 (@sgbaird): "send these results (scripts,
data, figures) to edison analysis along with context about this project and why
we're exploring this, fetch, report back".

Uploaded context (bundled as a single Edison data collection):
  scripts
    - sobol_t3_campaign.py   : draws an N-point Sobol set over the PR #35
                               T3-prism design box and runs it through the
                               C->B->A engine ladder (MuJoCo / PyBullet /
                               PyChrono / Newton-Warp / PolyFEM+IPC).
    - sobol_t3_violins.py     : Plotly violin (jittered raw points) renderer.
    - bo_evaluator.py         : sim->BO bridge (PR #35 schema -> PrintableDesign
                               -> run_regimes.simulate -> {F_peak, SEA, eta}).
    - run_regimes.py          : the MuJoCo tier-C regime simulator.
  data (measured this campaign)
    - sobol_t3_tierC.csv      : 512 designs x both regimes (MuJoCo).
    - sobol_t3_tierB.csv      : Newton/Warp XPBD subset.
    - sobol_t3_tierA.csv      : PolyFEM+IPC welded T-prism subset.
    - sobol_t3_pybullet.csv   : PyBullet rigid subset.
    - sobol_t3_pychrono.csv   : PyChrono rigid subset.
  figures
    - sobol_t3_pareto.png, sobol_t3_sensitivity.png,
      sobol_t3_tierC_vs_tierB.png, sobol_t3_engine_ladder.png,
      sobol_t3_tierA.png, sobol_t3_violin_objectives.png,
      sobol_t3_violin_engines.png
  analysis
    - sobol_t3_analysis.md, bo_integration.md
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
OUT_DIR = REPO_ROOT / "edison-trajectories" / "sobol-t3-results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BUNDLE_DIR = pathlib.Path(os.environ.get("EDISON_BUNDLE_DIR", "/tmp/edison_sobol_bundle"))

# Files to attach, relative to REPO_ROOT. Missing files are skipped (the repo on
# this branch may be a shallow/grafted clone).
BUNDLE_FILES = [
    SIM / "sobol_t3_campaign.py",
    SIM / "sobol_t3_violins.py",
    SIM / "bo_evaluator.py",
    SIM / "run_regimes.py",
    SIM / "sobol_t3_analysis.md",
    SIM / "bo_integration.md",
    OUT / "sobol_t3_tierC.csv",
    OUT / "sobol_t3_tierB.csv",
    OUT / "sobol_t3_tierA.csv",
    OUT / "sobol_t3_pybullet.csv",
    OUT / "sobol_t3_pychrono.csv",
    OUT / "sobol_t3_pareto.png",
    OUT / "sobol_t3_sensitivity.png",
    OUT / "sobol_t3_tierC_vs_tierB.png",
    OUT / "sobol_t3_engine_ladder.png",
    OUT / "sobol_t3_tierA.png",
    OUT / "sobol_t3_violin_objectives.png",
    OUT / "sobol_t3_violin_engines.png",
]


QUERY = """
# Project context and why we are exploring this

We are designing and 3D-printing class-1 tensegrity cells (3 rigid PLA struts,
E=3.5 GPa, rho=1240 kg/m^3; 9 soft TPU 85A tendons, E~12 MPa secant, sigma_break
~26 MPa; T3-triangular-prism topology) as compact, tunable impact-absorbers. The
overarching goal is twofold: (1) build a simulation+Bayesian-optimization
framework that generalizes to more advanced tensegrity structures, and (2)
obtain real, experimentally-validated "best" T3-prism designs on the bench. We
study two impact regimes: crutch_tip (75 kg @ ~1.4 m/s, ~Ø24x25 mm cell, anti-
vibration HAVS-style peak constraint <= 8 g) and nasa_lander (5 kg @ ~9.8 m/s,
~Ø200x200 mm cell, GEVS-style peak constraint <= 1500 g). We care about the
trade-off between peak transmitted force (F_peak), specific energy absorption
(SEA, J/g), and compaction/stroke efficiency (eta).

# What we actually ran (attached)

We swept the exact PR #35 T3-prism design box with a scrambled Sobol sequence
(scipy.stats.qmc.Sobol): R_mm in [25,40], H_mm in [60,110], twist_deg in [40,80],
strut_d_mm in [6,12], cable_d_mm in [3.0,5.5]. Each design is scored through a
C->B->A simulation fidelity ladder (sobol_t3_campaign.py):
  - Tier C (rigid screening): MuJoCo (512 designs x both regimes,
    ~0.2 s/design, CFC-180 filtered F_peak); plus PyBullet and PyChrono rigid
    subsets as cross-engine checks.
  - Tier B (deformable, differentiable): NVIDIA Newton / Warp XPBD subset, TPU
    tendons explicitly in the load path.
  - Tier A (high fidelity): PolyFEM + IPC NeoHookean on a welded PLA/TPU
    volumetric T-prism mesh subset.
The objectives map onto exactly what our drop-tower (PR #74 accelerometer +
SAE J211 CFC-180) and Instron experiments measure, so simulated and measured
rows can attach to the same Ax/BoTorch model.

Attached are the campaign script, the sim->BO bridge (bo_evaluator.py), the
tier-C simulator (run_regimes.py), the measured CSVs for every engine, the
analysis figures (Pareto fronts, parameter->objective Spearman sensitivity, the
Tier-C-vs-Tier-B and full engine-ladder rank-correlation scatter, the Tier-A
results, and the violin/jitter distributions), and our own write-up
(sobol_t3_analysis.md, bo_integration.md).

# Key empirical observations we want you to check and interpret

1. At Tier C, F_peak is near-invariant across the box (crutch span ~4%, lander
   ~3%); SEA and eta are the discriminating objectives at this fidelity, because
   in the rigid-strut model peak force is payload*dV-dominated.
2. Spearman sensitivity (feasible designs): dominant axes are strut_d_mm (~0.60)
   and H_mm (~0.49); R_mm (~0.15) and cable_d_mm (~0.10) are second-order;
   twist_deg ~ 0 — but honestly so, because the Tier-C regime override does not
   consume the twist axis (geometry is built at the fixed equilibrium twist), so
   twist can only surface at Tier B/A.
3. Cross-fidelity ranking vs Tier-C MuJoCo lander F_peak: PyChrono +0.70,
   Newton +0.60, PolyFEM +0.43, PyBullet ~ -0.02 (bare-prism peak is
   contact-dominated / design-invariant in PyBullet). Tier-A peak-g is ~1 g
   (prism settles below the IPC dhat barrier), so its discriminating observable
   is settled-COM height (68-112 mm).

# What we need from you (rigorous, citation-backed where possible)

A. Interpretation & critique of these specific results: are the conclusions in
   sobol_t3_analysis.md sound given the attached CSVs/figures? Where might the
   near-invariant Tier-C F_peak, the twist~0 sensitivity, or the cross-engine
   rank correlations be artifacts of model setup rather than physics, and how
   would we test that?
B. How best to use this cheap-sim Sobol data inside the PR #35 BO campaign:
   multi-fidelity / multi-task BO formulations that fuse cheap-sim + expensive-
   experiment observations on the shared {F_peak, SEA, eta} space; warm-starting
   / screening; cost-aware acquisition; and discrepancy/bias correction between
   sim and bench (Kennedy-O'Hagan, autoregressive co-kriging). Cite the
   multi-fidelity BO literature.
C. Which simulated quantities are trustworthy enough to act on at Tier C vs.
   which require Tier B/A, given the observations above.
D. Objective/constraint formulation and regime handling: one campaign per regime
   vs. a single multi-task / multi-objective (EHVI Pareto) campaign, and how to
   encode the HAVS (<=8 g) / GEVS (<=1500 g) constraints.
E. A prioritized, actionable next-steps list: which designs to physically print
   and drop-test first to maximize information, what to instrument, and the
   3-5 immediate analyses/experiments that would most improve the framework and
   give us a defensible experimental T3-prism "best".

Use the attached scripts, data, and figures as ground truth for what we have.
""".strip()


def _assemble_bundle() -> list[pathlib.Path]:
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    BUNDLE_DIR.mkdir(parents=True)
    copied = []
    for src in BUNDLE_FILES:
        if src.is_file():
            shutil.copy2(src, BUNDLE_DIR / src.name)
            copied.append(src)
        else:
            print(f"  skip missing {src.relative_to(REPO_ROOT)}")
    return copied


def _attach_bundle(client: EdisonClient) -> list[str]:
    print(f"  uploading bundle {BUNDLE_DIR} as a collection ...")
    resp = client.store_file_content(
        name="sobol-t3-results",
        file_path=str(BUNDLE_DIR),
        description=(
            "PR #35 T3-prism Sobol campaign: scripts, measured CSVs, analysis "
            "figures, and write-up across the C->B->A engine ladder"
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
        return formatted


def main() -> None:
    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get(
        "EDISON_API_KEY"
    )
    if not api_key:
        raise SystemExit("EDISON_PLATFORM_API_KEY / EDISON_API_KEY env var not set")

    client = EdisonClient(api_key=api_key)

    copied = _assemble_bundle()
    print(f"  bundled {len(copied)} files")
    files = _attach_bundle(client)

    submitted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{submitted_at}] submitting ANALYSIS sobol-t3-results query")

    submitted = client.create_task(
        task_data={"name": JobNames.ANALYSIS, "query": QUERY},
        files=files or None,
    )
    task_id = getattr(submitted, "trajectory_id", None) or str(submitted)
    print(f"  task id: {task_id}")

    pointer = OUT_DIR / f"sobol-t3-results-{task_id}-SUBMITTED.json"
    pointer.write_text(
        json.dumps(
            {
                "task_id": task_id,
                "submitted_at": submitted_at,
                "job": "ANALYSIS",
                "topic": "interpretation + critique of the PR #35 T3-prism Sobol "
                "simulation campaign and how to feed it into the BO program",
                "uploaded_files": [p.name for p in copied],
                "related_issues_prs": [30, 35, 67, 74],
                "pr_comment": 4713093337,
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

    md_path = OUT_DIR / f"sobol-t3-results-{task_id}.md"
    json_path = OUT_DIR / f"sobol-t3-results-{task_id}.json"
    formatted = _extract_answer(result)
    md_path.write_text(
        f"# Edison ANALYSIS brief: interpretation of the PR #35 T3-prism Sobol "
        f"simulation campaign\n\n"
        f"- **Task ID:** `{task_id}`\n"
        f"- **Job:** `ANALYSIS`\n"
        f"- **Submitted:** {submitted_at}\n"
        f"- **Fetched:** "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- **Status:** {getattr(result, 'status', 'unknown')}\n"
        f"- **PR comment:** 4713093337\n\n"
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
