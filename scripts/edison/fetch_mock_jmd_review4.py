#!/usr/bin/env python3
"""Poll and fetch the fourth-round mock-JMD-review Edison ANALYSIS task.

Reads the ``mock-jmd-review-4-SUBMITTED.json`` placeholder, polls the task until
terminal, and writes ``mock-jmd-review-4-<task_id>.md`` (answer + query),
``mock-jmd-review-4-<task_id>.json`` (full model_dump_json), and, when present,
``mock-jmd-review-4-<task_id>.ipynb`` (the ANALYSIS notebook artifact) per the
repo convention of committing all artifacts associated with a trajectory.

Run::

    python scripts/edison/fetch_mock_jmd_review4.py
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

TRAJ = HERE / "edison-trajectories" / "mock-jmd-review-4"
SUBMITTED = TRAJ / "mock-jmd-review-4-SUBMITTED.json"
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
    if d.get("answer"):
        return str(d["answer"])
    ef = (d.get("environment_frame") or {}).get("state") or {}
    for path in (("state", "answer"), ("info", "answer")):
        node = ef
        for key in path:
            node = (node or {}).get(key) if isinstance(node, dict) else None
        if node:
            return str(node)
    return ""


def _notebook(task) -> dict | None:
    try:
        d = json.loads(task.model_dump_json())
    except Exception:  # noqa: BLE001
        return None
    if isinstance(d.get("notebook"), dict):
        return d["notebook"]
    ef = (d.get("environment_frame") or {}).get("state") or {}
    state = ef.get("state") if isinstance(ef, dict) else None
    if isinstance(state, dict) and isinstance(state.get("nb_state"), dict):
        return state["nb_state"]
    return None


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
            query = d.get("query") or ""
            body = f"# Edison trajectory -- {slug}\n\nTask ID: `{tid}`  \nStatus: {st}\n\n"
            if query:
                body += f"## Query\n\n{query}\n\n---\n\n## Answer\n\n{ans}\n"
            else:
                body += f"---\n\n{ans}\n"
            (TRAJ / f"{slug}-{tid}.md").write_text(body, encoding="utf-8")
            nb = _notebook(task)
            if nb is not None:
                (TRAJ / f"{slug}-{tid}.ipynb").write_text(
                    json.dumps(nb, indent=1), encoding="utf-8"
                )
                print(f"{slug}: wrote notebook artifact")
            print(f"{slug}: wrote trajectory ({len(ans)} chars)")
            break


if __name__ == "__main__":
    main()
