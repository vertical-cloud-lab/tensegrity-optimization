"""Fetch a completed Edison analysis task and save all artifacts.

Usage: python fetch_task.py <task_id>
Requires EDISON_PLATFORM_API_KEY (or EDISON_API_KEY) in the environment.
"""

import json
import os
import sys
from pathlib import Path

from edison_client import EdisonClient

OUTDIR = Path(__file__).resolve().parent


def hunt(node):
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            if (
                k in ("answer", "formatted_answer", "final_answer")
                and isinstance(v, str)
                and len(v) > 200
            ):
                found.append(v)
            found.extend(hunt(v))
    elif isinstance(node, list):
        for v in node:
            found.extend(hunt(v))
    return found


def main() -> None:
    task_id = sys.argv[1]
    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ["EDISON_API_KEY"]
    client = EdisonClient(api_key=api_key)

    status = str(client.get_task(task_id).status).lower()
    print(f"status: {status}", flush=True)
    if not any(s in status for s in ("success", "fail", "cancel", "error")):
        sys.exit(3)  # still running

    verbose = client.get_task(task_id, verbose=True, history=True)
    payload = verbose.model_dump(mode="json")
    (OUTDIR / "task-response.json").write_text(
        json.dumps(payload, indent=2, default=str)
    )

    candidates = hunt(payload)
    if candidates:
        answer = max(candidates, key=len)
        (OUTDIR / "mock-audience-feedback.md").write_text(answer)
        print(f"answer saved ({len(answer)} chars)", flush=True)
    else:
        print("no answer field found; inspect task-response.json", flush=True)

    try:
        files = client.list_files(task_id)
        (OUTDIR / "trajectory-files.json").write_text(
            json.dumps(files, indent=2, default=str)
        )
        print(f"trajectory files: {files}", flush=True)
    except Exception as exc:
        print(f"list_files failed: {exc}", flush=True)

    print("done", flush=True)


if __name__ == "__main__":
    main()
