#!/usr/bin/env python3
"""Poll and fetch the two PR #20 review follow-up Edison tasks, writing the
verbatim trajectories under edison-trajectories/review-followups/.

Reads the ``*-SUBMITTED.json`` placeholders, polls each task until terminal,
and writes ``<slug>-<task_id>.md`` (formatted answer + query) and
``<slug>-<task_id>.json`` (full model_dump_json) per the repo convention.

Run::

    python scripts/edison/fetch_review_followups.py
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

TRAJ = HERE / "edison-trajectories" / "review-followups"
TERMINAL = {"success", "failed", "cancelled", "error", "crashed", "truncated", "fail"}


def _status(task) -> str:
    st = getattr(task, "status", None)
    return str(getattr(st, "value", st) or "").lower()


def _answer(task) -> str:
    for attr in ("formatted_answer", "answer"):
        val = getattr(task, attr, None)
        if val:
            return str(val)
    return ""


def main() -> None:
    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY")
        or os.environ.get("EDISON_API_KEY")
    )
    jobs = []
    for sub in sorted(TRAJ.glob("*-SUBMITTED.json")):
        d = json.loads(sub.read_text())
        jobs.append((d["slug"], d["task_id"]))

    # LITERATURE_HIGH: start with a 15 min wait, then poll every 5 min.
    pending = {slug: tid for slug, tid in jobs}
    first = True
    while pending:
        time.sleep(900 if first else 300)
        first = False
        for slug, tid in list(pending.items()):
            try:
                task = client.get_task(tid)
            except Exception as exc:  # noqa: BLE001
                print(f"{slug}: get_task error {exc}")
                continue
            st = _status(task)
            print(f"{slug} ({tid}): status={st}")
            if st in TERMINAL:
                (TRAJ / f"{slug}-{tid}.json").write_text(task.model_dump_json(indent=2))
                ans = _answer(task)
                (TRAJ / f"{slug}-{tid}.md").write_text(
                    f"# Edison LITERATURE_HIGH -- {slug}\n\n"
                    f"Task ID: `{tid}`  \nStatus: {st}\n\n---\n\n{ans}\n"
                )
                print(f"{slug}: wrote trajectory ({len(ans)} chars)")
                pending.pop(slug)


if __name__ == "__main__":
    main()
