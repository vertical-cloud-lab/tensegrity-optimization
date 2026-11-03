"""Submit Edison LITERATURE_HIGH query for articles similar to Davami et al. 2025.

Per repository memory pattern (scripts/edison/ on other branches): map
EDISON_API_KEY -> EDISON_PLATFORM_API_KEY shim, then submit and poll.
"""
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault(
    "EDISON_PLATFORM_API_KEY", os.environ.get("EDISON_API_KEY", "")
)

from edison_client import EdisonClient, JobNames  # noqa: E402

QUERY = """\
Find peer-reviewed articles closely related to:

Davami, K., Rowe, R., Gulledge, B., Tavangarian, F., Beck, S., Park, J.,
Beheshti, A., Palazotto, A. (2025). "Dynamic analysis of additively
manufactured tensegrity structures." International Journal of Impact
Engineering, 198, 105208. https://doi.org/10.1016/j.ijimpeng.2024.105208

Davami et al. fabricate bistable, single-material "tensegrity-like"
double-T3 prism unit cells and 20-cell lattices by SLA vat
photopolymerization (Formlabs Tough 2000 resin) with designed relative
density 20% and twist angle phi = 19 deg, then characterize them under
quasi-static compression (~0.005 1/s) and high-strain-rate direct-impact
SHPB at ~134-226 1/s, observing reliable bistable snap-buckling and
energy absorption without needing prestress.

Please return a ranked, annotated list of CLOSELY-RELATED published
articles spanning the following themes, with full citations and DOIs:

  (a) High-strain-rate / SHPB / drop / impact testing of additively
      manufactured tensegrity, tensegrity-inspired, or tensegrity-like
      lattice metamaterials (Rimoli, Pajunen, Daraio, Fraternali,
      Amendola, Micheletti, Skelton groups in particular).
  (b) Bistable / snap-through tensegrity or tensegrity-like prism
      cells designed for energy absorption.
  (c) Multi-material additively-manufactured tensegrity lattices (e.g.
      rigid struts + flexible TPU tendons, PLA/TPU, PETG/TPU, resin
      + elastomer dual-cure), and how their dynamic response differs
      from single-material tensegrity-like compliant mechanisms.
  (d) Optimization (especially Bayesian / multifidelity / topology
      optimization) of tensegrity geometry, prestress, or material
      assignment for impact energy absorption.
  (e) Reviews of tensegrity metamaterials covering wave propagation,
      solitary waves, and dynamic stability.

For each article also indicate: (i) whether it is single-material or
multi-material, (ii) AM process (SLA/DLP/FDM/SLS/EBM/etc.), (iii)
loading regime (quasi-static vs. high-strain-rate / SHPB / drop),
(iv) whether actual flexible tendons or only rigid struts are used,
(v) what optimization (if any) was performed.

The downstream goal is to position a forthcoming BYU MRG / IDETC
project on multi-material FDM-printed (PLA struts + TPU tendons)
tensegrity lattices optimized for energy absorption via multifidelity
Bayesian optimization, distinguishing it from Davami et al. and from
prior single-material tensegrity-like impact work.
"""


def main() -> int:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("edison-trajectories/davami2025-followup")
    out_dir.mkdir(parents=True, exist_ok=True)

    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY")
        or os.environ.get("EDISON_API_KEY")
    )

    task = {"name": JobNames.LITERATURE, "query": QUERY}

    submitted = client.create_task(task)
    task_id = (
        submitted if isinstance(submitted, str) else getattr(submitted, "task_id", None)
    ) or str(submitted)
    print(f"submitted task_id={task_id}", flush=True)

    submitted_path = out_dir / f"SUBMITTED-{task_id}.json"
    submitted_path.write_text(json.dumps({"task_id": task_id, "query": QUERY}, indent=2))

    # Poll up to ~25 min
    poll_max = 25 * 60
    sleep_s = 20
    elapsed = 0
    last_status = None
    while elapsed < poll_max:
        try:
            results = client.get_task(task_id)
        except Exception as e:  # noqa: BLE001
            print(f"poll error: {e}", flush=True)
            results = None
        status = getattr(results, "status", None) if results is not None else None
        if status != last_status:
            print(f"[{elapsed}s] status={status}", flush=True)
            last_status = status
        if status in {"success", "crashed", "failed", "fail"}:
            break
        time.sleep(sleep_s)
        elapsed += sleep_s

    if last_status != "success":
        print(f"final status={last_status} after {elapsed}s; leaving SUBMITTED marker", flush=True)
        return 0

    fa = getattr(results, "formatted_answer", "") or ""
    (out_dir / f"davami2025-followup-{task_id}.md").write_text(fa)
    try:
        raw = results.model_dump() if hasattr(results, "model_dump") else results.dict()
    except Exception:  # noqa: BLE001
        raw = {"repr": repr(results)}
    (out_dir / f"davami2025-followup-{task_id}.json").write_text(json.dumps(raw, indent=2, default=str))
    submitted_path.unlink(missing_ok=True)
    print(f"SAVED md+json to {out_dir} (len(md)={len(fa)})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
