#!/usr/bin/env python3
"""Poll one rubber-duck Edison task to completion and commit-ready artifacts.

Usage::

    python scripts/edison/fetch_rubberduck.py <iteration 1-5>

Blocks (time.sleep inside this process, per repo CLAUDE.md) until the task
reaches a terminal state, then writes the answer markdown, the full task JSON,
and any workspace artifacts (report markdown, notebook) into
``edison-trajectories/rubberduck-<n>/``.
"""
from __future__ import annotations

import json
import os
import sys
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


def _find_answer(o, depth=0):
    if depth > 6:
        return None
    if isinstance(o, dict):
        for k in ("answer", "formatted_answer", "final_answer"):
            v = o.get(k)
            if isinstance(v, str) and len(v) > 500:
                return v
        for v in o.values():
            r = _find_answer(v, depth + 1)
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = _find_answer(v, depth + 1)
            if r:
                return r
    return None


def main() -> None:
    n = int(sys.argv[1])
    traj = HERE / "edison-trajectories" / f"rubberduck-{n}"
    sub = json.loads((traj / f"rubberduck-{n}-SUBMITTED.json").read_text())
    task_id = sub["task_id"]

    client = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
    while True:
        task = client.get_task(task_id=task_id, verbose=True)
        status = str(task.status)
        print("status:", status, flush=True)
        if status in {"success", "fail", "failed", "cancelled", "error"}:
            break
        time.sleep(120)

    def ser(o):
        try:
            return o.model_dump()
        except Exception:
            return str(o)

    d = ser(task)
    (traj / f"rubberduck-{n}-{task_id}.json").write_text(
        json.dumps(d, indent=2, default=str)
    )
    ans = _find_answer(d)
    if ans:
        (traj / f"rubberduck-{n}-{task_id}.md").write_text(ans)
        print(f"answer: {len(ans)} chars")

    # workspace artifacts (report markdown, notebook)
    try:
        listing = client.list_files(task_id)
        import shutil
        for item in listing.get("data", []):
            ds = item.get("data_storage") or {}
            name = ds.get("name")
            dsid = ds.get("id")
            if not name or not dsid:
                continue
            try:
                r = client.fetch_data_from_storage(dsid)
            except Exception as e:  # noqa: BLE001
                print(f"  fetch {name}: {e!r}"[:200])
                continue
            content = getattr(r, "content", None)
            dest = traj / name
            if content is not None:
                mode = "wb" if isinstance(content, bytes) else "w"
                with open(dest, mode) as f:
                    f.write(content)
                print(f"  wrote {dest.name}")
            elif isinstance(r, (str, Path)) and Path(str(r)).exists():
                shutil.copy2(str(r), dest)
                print(f"  copied {dest.name}")
    except Exception as e:  # noqa: BLE001
        print("artifact listing failed:", repr(e)[:200])

    print("done; final status:", status)


if __name__ == "__main__":
    main()
