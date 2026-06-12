#!/usr/bin/env python3
"""Submit the two Edison (LITERATURE_HIGH) follow-up tasks requested in the
PR #20 manuscript review (@sgbaird):

  T4  -- citation classification: are ye2023multimaterial / khatri2024energy
         genuinely "tensegrity-inspired", or merely related multi-material AM
         works? (review thread at manuscript-body.tex L171)
  T26 -- double-check the SEA / compaction-efficiency equations and the
         drop-impact peak-transmitted-force methodology, in the context of the
         accelerometer impact-window findings (PR #67, issue #71, PR #74).

Both are submitted non-blocking; each task id is recorded in a ``*-SUBMITTED.json``
placeholder so the result can be fetched next session via
``client.get_task(task_id).model_dump_json()`` and folded back into the draft,
matching the repo's Edison-trajectory convention.

Run::

    python scripts/edison/submit_review_followups.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    """Best-effort load of repo-root .env (KEY=VALUE per line) into os.environ."""
    env = HERE / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


_load_dotenv()
# edison-client >= 0.12 reads EDISON_PLATFORM_API_KEY; map the documented
# EDISON_API_KEY onto it if only the old name is set.
if os.environ.get("EDISON_API_KEY") and not os.environ.get("EDISON_PLATFORM_API_KEY"):
    os.environ["EDISON_PLATFORM_API_KEY"] = os.environ["EDISON_API_KEY"]

from edison_client import EdisonClient, JobNames  # noqa: E402
from edison_client.models import TaskRequest  # noqa: E402

TRAJ = HERE / "edison-trajectories" / "review-followups"
TRAJ.mkdir(parents=True, exist_ok=True)

T4_QUERY = """\
I am writing a mechanical-engineering manuscript on Bayesian-optimization-driven,
multi-material 3D-printed *tensegrity-inspired* structures (rigid PLA struts +
soft TPU tension elements) for energy absorption / impact protection.

In my Background I currently group two references under multi-material rigid-soft
3D printing and imply they are "tensegrity-inspired":

1. Ye et al., "Multimaterial 3D printing of thick-panel origami" (Nature
   Communications, 2023). This work appears to be about thick-panel ORIGAMI with
   rigid panels (PLA, and in some demonstrations ABS or CFRP) connected by soft
   TPU hinges -- not tensegrity. It does not seem to use the word "tensegrity".
2. Khatri et al. (2024) on energy-absorbing multi-material structures (a Sage /
   3D Printing and Additive Manufacturing article that appears to use ABS + TPU,
   no PLA, and again may not be tensegrity).

Questions:
(a) For EACH of these two papers, is it accurate to call the work
    "tensegrity-inspired", or are they merely "related" multi-material additive
    manufacturing / architected-material works? Quote any explicit use (or
    absence) of "tensegrity" in each paper.
(b) What materials does each actually use (PLA / ABS / CFRP / TPU / other), and
    does either give a stated rationale for choosing one rigid material over
    another?
(c) Recommend more accurate framing language and, if appropriate, suggest a few
    genuinely tensegrity (or tensegrity-inspired) 3D-printed multi-material
    references I should cite instead of or alongside these, with full
    bibliographic details and DOIs.

Be precise and ground every claim in the actual papers.
"""

T26_QUERY = r"""
I am writing a mechanical-engineering manuscript on multi-material 3D-printed
tensegrity-inspired energy absorbers, characterized with (i) quasi-static
compression on a benchtop load frame and (ii) drop-weight impact on an
instrumented drop tower. Please sanity-check the following metric definitions and
methodology, and recommend best practice with citations.

Reported quasi-static metrics (F = force, delta = displacement, m = specimen
mass, delta_d = densification displacement, F_max = peak transmitted force):

  SEA = (1/m) * integral_0^{delta_d} F(delta) d(delta)              [specific energy absorption]
  eta_c = integral_0^{delta_d} F(delta) d(delta) / (F_max * delta_d) [compaction efficiency]

Questions:
(a) Are these the standard textbook definitions of specific energy absorption and
    compaction (stroke / cushioning) efficiency for cellular / architected energy
    absorbers? Flag any sign, normalization, or limit-of-integration issues, and
    give the canonical references (e.g., Gibson & Ashby; Avalle; Tan; SAE/ISO/ASTM
    cushioning standards).
(b) For the drop-weight impact test, what is the correct way to define and extract
    the "peak transmitted force" / peak acceleration from an instrumented drop?
    Specifically address: anti-alias / low-pass filtering per SAE J211 (CFC-60 /
    CFC-180 / CFC-1000), the danger of reporting a raw (ringing-dominated) global
    peak vs. a windowed peak search around the true impact event, sensor
    saturation/clipping, and single-axis vs. tri-axis resultant.
(c) Our own drop-test analysis found that a windowed peak search (around the
    impact event, ~first few ms) with CFC-180 filtering changes the answer
    substantially relative to a naive global 0.2 s maximum (which can be dominated
    by post-impact mount oscillation), and that an analog-saturating single-axis
    sensor should be replaced with a higher-range one. Is this consistent with
    best practice, and how should SEA / peak-force be related to the
    accelerometer-derived signals?

Give a concise, citable verdict for each point.
"""

TASKS = [
    ("t4-citation-classification", T4_QUERY),
    ("t26-sea-impact-math", T26_QUERY),
]


def main() -> None:
    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY")
        or os.environ.get("EDISON_API_KEY")
    )
    for slug, query in TASKS:
        task = TaskRequest(name=JobNames.LITERATURE_HIGH, query=query)
        submitted = client.create_task(task)
        task_id = getattr(submitted, "task_id", None) or (
            submitted if isinstance(submitted, str) else None
        )
        out = TRAJ / f"{slug}-SUBMITTED.json"
        out.write_text(json.dumps({
            "slug": slug,
            "task_id": str(task_id),
            "job": str(JobNames.LITERATURE_HIGH),
            "note": "non-blocking; fetch next session via client.get_task(task_id)",
        }, indent=2))
        print(f"{slug}: submitted task_id={task_id} -> {out}")


if __name__ == "__main__":
    main()
