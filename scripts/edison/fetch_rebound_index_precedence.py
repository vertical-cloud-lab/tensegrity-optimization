"""Poll + fetch the two Edison precedent tasks (see submit_rebound_index_precedence.py).

Writes, per task, the full JSON dump and the answer markdown (plain and
formatted-with-references when available) into
``edison-trajectories/rebound-index-precedence/``.

Per CLAUDE.md the wait must happen inside a single blocking Python call -- the
``time.sleep`` loop below is that wait; do not background this script.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from edison_client import EdisonClient

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "rebound-index-precedence"
SUBMITTED = OUT / "rebound-index-precedence-SUBMITTED.json"

api_key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
if not api_key:
    raise SystemExit("EDISON_API_KEY (or EDISON_PLATFORM_API_KEY) not set")
api_key = api_key.strip()

TASKS = json.loads(SUBMITTED.read_text())["tasks"]
WAIT_MIN = int(os.environ.get("PRECEDENCE_WAIT_MIN", "40"))
TERMINAL = ("success", "fail", "cancel", "truncat", "error")


def poll_once(task_id: str) -> dict:
    """One status poll. The login endpoint 403s if hit too often, so build a
    fresh client per poll and let the caller back off on failure."""
    return EdisonClient(api_key=api_key).get_task(task_id).model_dump()


def extract_answers(dump: dict) -> tuple[str, str]:
    plain = dump.get("answer") or ""
    formatted = dump.get("formatted_answer") or ""
    if not plain:
        ef = dump.get("environment_frame") or {}
        try:
            plain = ef["state"]["state"]["answer"] or ""
        except (KeyError, TypeError):
            plain = ""
    return plain, formatted


def main() -> int:
    deadline = time.time() + 60 * WAIT_MIN
    done: dict[str, dict] = {}
    while len(done) < len(TASKS):
        for label, meta in TASKS.items():
            if label in done:
                continue
            try:
                dump = poll_once(meta["task_id"])
                status = str(dump.get("status", "")).lower()
                print(f"{label}: {status}", flush=True)
                if any(s in status for s in TERMINAL):
                    done[label] = dump
            except Exception as exc:  # transient auth/rate-limit; retry next round
                print(f"{label}: poll failed ({type(exc).__name__}: {str(exc)[:80]})",
                      flush=True)
        if len(done) == len(TASKS):
            break
        if time.time() >= deadline:
            print("deadline reached without all tasks terminal", flush=True)
            break
        time.sleep(120)

    for label, dump in done.items():
        task_id = TASKS[label]["task_id"]
        stem = f"{label}-{task_id}"
        (OUT / f"{stem}.json").write_text(json.dumps(dump, indent=2, default=str))
        plain, formatted = extract_answers(dump)
        if formatted:
            (OUT / f"{stem}.md").write_text(formatted)
            print(f"{label}: wrote formatted answer ({len(formatted)} chars)")
        elif plain:
            (OUT / f"{stem}.md").write_text(plain)
            print(f"{label}: wrote answer ({len(plain)} chars)")
        print(f"{label}: final status {dump.get('status')}")

    return 0 if len(done) == len(TASKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
