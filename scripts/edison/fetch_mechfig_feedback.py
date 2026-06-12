#!/usr/bin/env python3
"""Poll and fetch the mechanistic-data-figure Edison ANALYSIS task.

Reads the ``mechfig-feedback-SUBMITTED.json`` placeholder, polls the task until
terminal, and writes ``mechfig-feedback-<task_id>.md`` (answer + query) and
``mechfig-feedback-<task_id>.json`` (full model_dump_json) per repo convention.

Run::

    python scripts/edison/fetch_mechfig_feedback.py
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    env = HERE / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


_load_dotenv()
if os.environ.get("EDISON_API_KEY") and not os.environ.get("EDISON_PLATFORM_API_KEY"):
    os.environ["EDISON_PLATFORM_API_KEY"] = os.environ["EDISON_API_KEY"]

from edison_client import EdisonClient  # noqa: E402

TRAJ = HERE / "edison-trajectories" / "mechfig-feedback"
SUBMITTED = TRAJ / "mechfig-feedback-SUBMITTED.json"
TERMINAL = {"success", "failed", "cancelled", "error", "crashed", "truncated", "fail"}


def _status(task) -> str:
    st = getattr(task, "status", None)
    return str(getattr(st, "value", st) or "").lower()


def _answer(task) -> str:
    for attr in ("formatted_answer", "answer"):
        val = getattr(task, attr, None)
        if val:
            return str(val)
    # ANALYSIS (Finch) tasks keep the answer deeper in the environment frame.
    try:
        d = json.loads(task.model_dump_json())
    except Exception:  # noqa: BLE001
        return ""
    ef = (d.get("environment_frame") or {}).get("state") or {}
    for path in (("state", "answer"), ("info", "answer")):
        node = ef
        for key in path:
            node = (node or {}).get(key) if isinstance(node, dict) else None
        if node:
            return str(node)
    return ""


def main() -> None:
    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY")
        or os.environ.get("EDISON_API_KEY")
    )
    d = json.loads(SUBMITTED.read_text())
    slug, tid = d["slug"], d["task_id"]

    first = True
    while True:
        if not first:
            time.sleep(300)
        first = False
        try:
            task = client.get_task(tid)
        except Exception as exc:  # noqa: BLE001
            print(f"{slug}: get_task error {exc}")
            continue
        st = _status(task)
        print(f"{slug} ({tid}): status={st}")
        if st in TERMINAL:
            (TRAJ / f"{slug}-{tid}.json").write_text(
                task.model_dump_json(indent=2), encoding="utf-8"
            )
            ans = _answer(task)
            (TRAJ / f"{slug}-{tid}.md").write_text(
                f"# Edison trajectory -- {slug}\n\n"
                f"Task ID: `{tid}`  \nStatus: {st}\n\n---\n\n{ans}\n",
                encoding="utf-8",
            )
            print(f"{slug}: wrote trajectory ({len(ans)} chars)")
            break


if __name__ == "__main__":
    main()
