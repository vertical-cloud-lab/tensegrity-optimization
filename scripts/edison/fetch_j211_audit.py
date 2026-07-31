"""Poll + fetch the Edison Scientific standards audit (see submit_j211_audit.py).

Writes the markdown answer, the full JSON dump, the notebook, and any inline
base64 figures into ``edison-trajectories/j211-audit/``.

Per CLAUDE.md the wait must happen inside a single blocking Python call -- the
``time.sleep`` loop below is that wait; do not background this script.
"""
from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

from edison_client import EdisonClient

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "j211-audit"
SUBMITTED = OUT / "j211-audit-SUBMITTED.json"

api_key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
if not api_key:
    raise SystemExit("EDISON_API_KEY (or EDISON_PLATFORM_API_KEY) not set")
api_key = api_key.strip()

task_id = json.loads(SUBMITTED.read_text())["task_id"]
WAIT_MIN = int(os.environ.get("J211_WAIT_MIN", "35"))


def poll_once():
    """One status poll. The client authenticates lazily on first use and the
    login endpoint 403s if it is hit too often, so build a fresh client per
    poll and let the caller back off rather than dying on a transient 403."""
    return EdisonClient(api_key=api_key).get_task(task_id).model_dump()


def extract_answer(dump: dict) -> str:
    if dump.get("answer"):
        return dump["answer"]
    ef = dump.get("environment_frame") or {}
    try:
        return ef["state"]["state"]["answer"] or ""
    except (KeyError, TypeError):
        return ""


def main() -> int:
    deadline = time.time() + 60 * WAIT_MIN
    dump = None
    while True:
        try:
            dump = poll_once()
            status = str(dump.get("status", "")).lower()
            print(f"status: {status}", flush=True)
            if any(s in status for s in ("success", "fail", "cancel", "truncat", "error")):
                break
        except Exception as exc:  # transient auth/rate-limit; back off and retry
            print(f"poll failed ({type(exc).__name__}: {str(exc)[:80]}), retrying",
                  flush=True)
        if time.time() >= deadline:
            print("deadline reached without a terminal status", flush=True)
            break
        time.sleep(120)

    if dump is None:
        print("no successful poll; re-run this script to fetch")
        return 1

    (OUT / f"j211-audit-{task_id}.json").write_text(json.dumps(dump, indent=2, default=str))

    answer = extract_answer(dump)
    if answer:
        (OUT / f"j211-audit-{task_id}.md").write_text(answer)
        print(f"wrote answer ({len(answer)} chars)")

    notebook = dump.get("notebook")
    if notebook:
        (OUT / f"j211-audit-{task_id}-notebook.ipynb").write_text(
            json.dumps(notebook, indent=2, default=str)
        )
        n_fig = 0
        for cell in notebook.get("cells", []):
            for outp in cell.get("outputs", []):
                png = (outp.get("data") or {}).get("image/png")
                if png:
                    n_fig += 1
                    (OUT / f"j211-audit-{task_id}-fig{n_fig}.png").write_bytes(
                        base64.b64decode(png)
                    )
        if n_fig:
            print(f"extracted {n_fig} figures")

    print(f"final status: {dump.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
