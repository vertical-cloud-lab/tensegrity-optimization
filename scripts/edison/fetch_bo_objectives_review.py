"""Poll + fetch the Edison Scientific ANALYSIS task that adversarially reviews
the BO objective choice for the T-3_01 prism campaign (see
submit_bo_objectives_review.py).

Writes the markdown answer, the full JSON dump, the notebook, and any inline
base64 figures into edison-trajectories/bo-objectives/. The polling loop runs
in the foreground on purpose (see CLAUDE.md, Edison section): pass
--poll-minutes to bound the wait, and re-run later to fetch if it times out.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import time
from pathlib import Path

from edison_client import EdisonClient

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "bo-objectives"
SUBMITTED = OUT / "bo-objectives-SUBMITTED.json"

api_key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
if not api_key:
    raise SystemExit("EDISON_API_KEY (or EDISON_PLATFORM_API_KEY) not set")
client = EdisonClient(api_key=api_key.strip())

task_id = json.loads(SUBMITTED.read_text())["task_id"]


def extract_answer(dump: dict) -> str:
    if dump.get("answer"):
        return dump["answer"]
    ef = dump.get("environment_frame") or {}
    try:
        return ef["state"]["state"]["answer"] or ""
    except (KeyError, TypeError):
        return ""


def thread_comment_count(pr_number: int) -> int | None:
    """Number of comments on the PR thread, so the agent session polling this
    script can notice new instructions between Edison status checks."""
    try:
        out = subprocess.run(
            ["gh", "api", f"repos/{{owner}}/{{repo}}/issues/{pr_number}"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout
        return json.loads(out).get("comments")
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--poll-minutes", type=float, default=40.0)
    ap.add_argument("--interval-seconds", type=float, default=120.0)
    ap.add_argument("--watch-pr", type=int, default=0, help="also report this PR's comment count each cycle")
    args = ap.parse_args()

    deadline = time.time() + 60 * args.poll_minutes
    dump = None
    while True:
        resp = client.get_task(task_id)
        dump = resp.model_dump()
        status = str(dump.get("status", "")).lower()
        line = f"status: {status}"
        if args.watch_pr:
            n = thread_comment_count(args.watch_pr)
            if n is not None:
                line += f"  (PR #{args.watch_pr} comments: {n})"
        print(line, flush=True)
        if any(s in status for s in ("success", "fail", "cancel", "truncat")):
            break
        if time.time() >= deadline:
            print("poll window elapsed; task still running. Re-run to fetch later.")
            return 1
        time.sleep(args.interval_seconds)

    if dump is None:
        raise SystemExit("no response")

    (OUT / f"bo-objectives-{task_id}.json").write_text(
        json.dumps(dump, indent=2, default=str)
    )

    answer = extract_answer(dump)
    if answer:
        (OUT / f"bo-objectives-{task_id}.md").write_text(answer)
        print(f"wrote answer ({len(answer)} chars)")

    notebook = dump.get("notebook")
    if notebook:
        (OUT / f"bo-objectives-{task_id}-notebook.ipynb").write_text(
            json.dumps(notebook, indent=2, default=str)
        )
        n_fig = 0
        for cell in notebook.get("cells", []):
            for outp in cell.get("outputs", []):
                png = (outp.get("data") or {}).get("image/png")
                if png:
                    n_fig += 1
                    (OUT / f"bo-objectives-{task_id}-fig{n_fig}.png").write_bytes(
                        base64.b64decode(png)
                    )
        if n_fig:
            print(f"extracted {n_fig} figures from notebook")

    print(f"final status: {dump.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
