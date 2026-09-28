"""Rubber-duck the objective-definition history against Edison ANALYSIS.

Triggered by PR #33 comment (@sgbaird, 2026-08-24): "rubber duck against
Edison" plus "I feel that I'm getting a bit beyond what I can keep
altogether in mind and trust. Might require some more careful combing
through the extensive history of conversations around defining the
objectives."  So the query below reconstructs the whole objective-definition
chain, states the newly proposed second-objective swap (``e_rebound`` ->
``peak_tendon_strain``), and asks Edison to audit the chain for
contradictions and to critique the swap before the re-run campaign's
results are trusted.

Uploaded: the candidate screening (script + CSVs + figure), the ringdown
analysis, the drop-tower analogue source, the campaign write-up, and the
measured drop results.
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
OUT = SIM / "outputs"
OUT_DIR = REPO_ROOT / "edison-trajectories" / "objective-rubber-duck"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BUNDLE_DIR = pathlib.Path(
    os.environ.get("EDISON_BUNDLE_DIR", "/tmp/edison_objective_duck_bundle")
)

STATIC_FILES = [
    SIM / "pr102_objective_screen.py",
    SIM / "drop_tower_sim.py",
    SIM / "zeta_analysis.md",
    SIM / "pr102_sim_campaign.md",
    SIM / "data" / "pr102" / "t3-prism-bo-batch-drop-results.csv",
    OUT / "pr102_objective_screen.csv",
    OUT / "pr102_objective_screen_summary.csv",
    OUT / "pr102_objective_screen.png",
]


QUERY = """
# Rubber-duck request: audit our objective-definition history and critique a swap

We are optimizing 3D-printed class-1 tensegrity T3 prisms (3 PLA struts, 9 TPU
85A tendons, ~20 g printed) as impact absorbers. A bench campaign (drop tower,
Lansmont M23, 60 in drop onto a 1/2 in PU mat, ~101 drops per article, n = 9
articles) and a simulation-only mirror campaign (MuJoCo drop-tower analogue,
`drop_tower_sim.py`, attached) share a 2-objective formulation. The objective
definition has been revised repeatedly, and the operator has asked us to lay
out the full chain so a fresh reviewer can spot inconsistencies. Please act as
that reviewer.

## The chain of objective definitions, in order, with what killed each

1. Regime sims (earlier work, not attached): minimize F_peak, maximize
   SEA_J_per_g, maximize eta under two application regimes. Killed for the
   bench-mirror campaign because F_peak at the rigid-strut tier was a static
   support-load proxy (crutch median F_peak/(m g) = 1.002), SEA was a peak
   ELASTIC strain-energy proxy (~10^3 below incoming KE/mass), and the twist
   axis was never consumed by the model plumbing.
2. Bench campaign objectives (PR #102, still current on the bench): minimize
   t180 = CFC-180-filtered transmissibility (top-vertex peak / base-plate
   peak), and minimize e_reb_mJ = e_rebound * m_printed * g * h where
   e_rebound is the restitution VELOCITY ratio read off the time to second
   impact.
3. First simulated mirror held constant SOLID CAD mass, leaving printed mass
   free: over a 68,944-design sweep, rho(e_reb_mJ, mass_g) = 0.99993 while
   simulated e_rebound spanned 0.34 %. The objective was printed mass in
   disguise. Fixed by projecting onto constant PRINTED mass (20.23 g).
4. On the constant-mass manifold the confound is gone but the second
   objective died: simulated e_rebound spans < 1 % across the whole design
   space because the calibrated Hunt-Crossley mat owns the loss budget (it is
   deliberately calibrated to the measured input pulse, NOT to restitution:
   a mat lossy enough to match measured e ~ 0.02 peaks near 300 G, far above
   the tower's 208 G, because the rig loses energy through rails/anvil/mount
   paths the model does not carry). Also rho(sim e_rebound, sim t180) = +0.84
   concordant, so the campaign was effectively single-objective. Meanwhile
   MEASURED e_rebound is real (spans 2.46x, between-article spread ~15x
   within-article noise) but hints at ANTI-correlation with measured t180
   (rho = -0.57, n = 8, p = 0.14): the one genuinely attenuating article has
   the HIGHEST rebound.
5. Proposed bench replacement: maximize zeta_pct (the article's own modal
   damping from the post-impact ringdown; spans 6.4-31 %, independent of
   measured t180 at rho = +0.07, already measured per drop). Adopted as a
   bench-only channel.
6. Tier-C simulation CANNOT resolve zeta (zeta_analysis.md attached): the
   measured ringdown band (294-468 Hz) is strut flexure, which rigid struts
   do not have (sim modes sit at 22-96 Hz); the model has a parasitic damping
   floor (~12 %) above the least-damped articles; the design response of sim
   zeta is chaotic mode-swapping, not physics; and injecting measured
   per-article damping into the tendons moves the objectives by < 0.2 %
   because the mat owns the loss.
7. THE NEW STEP WE WANT CRITIQUED: swap the simulated campaign's second
   objective from e_rebound to peak_tendon_strain = max over time and cables
   of TPU tension strain above slack length (minimized), keeping minimize
   t180. Screening over 128 Sobol designs on the constant-mass ratio manifold
   (pr102_objective_screen*.csv attached; 78 printable):
     - e_rebound: rel span 0.65 % (dead, confirmed)
     - t1000, out_180_g: rho vs t180 = +1.00 (pure duplicates)
     - in_180_g (null control): span 0.10 % (calibrated mat working)
     - pulse_ms: span 0.5 % (dead)
     - peak_tendon_strain: span 63 %, rho vs t180 = -0.41, driven by
       cable_over_strut_d (-0.76) and twist (-0.32) -- the one candidate that
       consumes the twist axis
     - peak_tendon_energy_mJ: span 157 %, rho = -0.87 (near-mirror of t180)
     - stroke_mm: span 122 %, rho = -0.89 (near-mirror)
   Rationale for the winner: genuine trade-off (the compliant articles that
   shield the payload strain their tendons hardest -- the same sign as the
   bench's t180 vs rebound hint), direct physical reading (TPU break/fatigue
   margin; TPU 85A elongation at break is large but cyclic loading at 100+
   drops makes strain a survivability proxy), and moderate independence so
   the front has genuine 2-D structure rather than a sliver.

## What we want from you

A. AUDIT THE CHAIN (the rubber-duck part). Steps 1-7 were decided across many
   sessions. Are any of the steps mutually inconsistent, circular, or
   over-claimed given the attached data? In particular: is the argument in
   step 4 for "the mat owns the loss budget" compatible with the argument in
   step 6 item 4? Is the concordance rho = +0.84 (sim) vs anti-correlation
   -0.57 (bench) contradiction correctly attributed to the missing loss
   mechanism rather than to a sign error somewhere?
B. CRITIQUE THE SWAP. Is minimize peak_tendon_strain a defensible second
   objective, or should strain be an OUTCOME CONSTRAINT (strain <= TPU
   allowable) with the campaign single-objective in t180? When is each
   formulation right? Note the anti-correlation means minimizing strain
   pushes toward stiff articles, i.e. against t180 -- is a trade-off front
   between transmissibility and a survivability proxy decision-useful for
   choosing what to print next, or is it optimizing an unmeasured quantity?
C. SIM-BENCH ASYMMETRY. The bench pair would be (t180, zeta_pct) and the sim
   pair (t180, peak_tendon_strain) -- different second axes. For later
   sim+bench fusion (multi-task / discrepancy GPs), is it a problem that the
   two campaigns optimize different second objectives, and how would you
   structure the data model so the sim still contributes despite that?
D. ANYTHING WE MISSED. Given the attached measured channels (drop-results
   CSV: t180, t1000, e_rebound, fn_hz, zeta_pct, dv health flags) and the
   simulated observables in drop_tower_sim.py, is there a better
   sim-resolvable second objective we did not screen? Note strut flexure /
   material damping / rig loss paths are all absent at this tier by
   construction.

Answer from the attached files where possible; flag any claim of ours you
cannot verify from them.
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
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--poll-minutes", type=float, default=40.0)
    ap.add_argument("--task-id", default=None,
                    help="skip submission and fetch this task instead")
    args = ap.parse_args()

    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get(
        "EDISON_API_KEY"
    )
    if not api_key:
        raise SystemExit("EDISON_PLATFORM_API_KEY / EDISON_API_KEY env var not set")
    client = EdisonClient(api_key=api_key.strip())

    submitted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if args.task_id:
        task_id = args.task_id
    else:
        copied = _assemble_bundle()
        print(f"  bundled {len(copied)} files")
        resp = client.store_file_content(
            name="objective-rubber-duck",
            file_path=str(BUNDLE_DIR),
            description=(
                "Objective-definition audit bundle: candidate screening "
                "(script/CSVs/figure), zeta analysis, drop-tower analogue "
                "source, campaign write-up, measured drop results"
            ),
            as_collection=True,
        )
        storage_id = getattr(getattr(resp, "data_storage", None), "id", None)
        if storage_id is None:
            storage_id = getattr(resp, "id", None)
        print(f"  data_storage id: {storage_id}")
        files = [f"data_entry:{storage_id}"] if storage_id else None

        print(f"[{submitted_at}] submitting ANALYSIS objective-rubber-duck query")
        submitted = client.create_task(
            task_data={"name": JobNames.ANALYSIS, "query": QUERY},
            files=files,
        )
        task_id = getattr(submitted, "trajectory_id", None) or str(submitted)
        print(f"  task id: {task_id}")
        pointer = OUT_DIR / f"objective-rubber-duck-{task_id}-SUBMITTED.json"
        pointer.write_text(json.dumps({
            "task_id": task_id, "submitted_at": submitted_at,
            "job": "ANALYSIS",
            "topic": "objective-definition history audit + second-objective "
                     "swap critique (e_rebound -> peak_tendon_strain)",
            "uploaded_files": [p.name for p in copied],
        }, indent=2))

    deadline = time.time() + args.poll_minutes * 60
    last_status = None
    while time.time() < deadline:
        try:
            status_resp = client.get_task(task_id=task_id, lite=True)
        except Exception as exc:  # noqa: BLE001
            print(f"  status poll failed: {exc!r}")
            time.sleep(30)
            continue
        status = getattr(status_resp, "status", None) or str(status_resp)
        if status != last_status:
            print(f"  [{datetime.now(timezone.utc).strftime('%H:%M:%S')}] "
                  f"status: {status}", flush=True)
            last_status = status
        if str(status).lower() in {"success", "fail", "failed", "error",
                                   "cancelled"}:
            break
        time.sleep(30)

    result = client.get_task(task_id=task_id, verbose=True)
    md_path = OUT_DIR / f"objective-rubber-duck-{task_id}.md"
    json_path = OUT_DIR / f"objective-rubber-duck-{task_id}.json"
    formatted = _extract_answer(result)
    md_path.write_text(
        f"# Edison ANALYSIS brief: objective-definition rubber duck\n\n"
        f"- **Task ID:** `{task_id}`\n- **Job:** `ANALYSIS`\n"
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
    stale = OUT_DIR / f"objective-rubber-duck-{task_id}-SUBMITTED.json"
    if stale.exists() and str(getattr(result, "status", "")).lower() == "success":
        stale.unlink()


if __name__ == "__main__":
    main()
