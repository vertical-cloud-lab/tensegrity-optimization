"""Poll + fetch the Edison ANALYSIS task reviewing the measured round-2
results (see submit_round2_results_review.py).

Writes the markdown answer, the full JSON dump, the notebook, inline base64
figures, AND any workspace report files the answer references (the previous
task's real report lived in data-storage entries named in the answer, not in
the answer text itself). Foreground polling on purpose (see CLAUDE.md).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import time
from pathlib import Path

from edison_client import EdisonClient

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "round2-results"
SUBMITTED = OUT / "round2-results-SUBMITTED.json"

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


def fetch_workspace_files(answer: str) -> None:
    """Pull data-storage entries whose file names appear in the answer."""
    names = set(re.findall(r"/workspace/[\w./-]*/([\w.-]+\.\w+)", answer))
    names |= set(re.findall(r"Download `([\w.-]+\.\w+)`", answer))
    for name in sorted(names):
        try:
            hits = client.search_data_storage(text_query=name, limit=5)
        except Exception as exc:
            print(f"search failed for {name}: {exc}")
            continue
        for h in hits:
            if h.get("name") != name:
                continue
            try:
                r = client.fetch_data_from_storage(h["id"])
            except Exception as exc:
                print(f"fetch failed for {name} ({h['id']}): {exc}")
                continue
            content = getattr(r, "content", None)
            dest = OUT / name
            if isinstance(content, bytes):
                dest.write_bytes(content)
            elif isinstance(content, str):
                dest.write_text(content)
            elif isinstance(r, Path):
                dest.write_bytes(Path(r).read_bytes())
            else:
                print(f"unhandled fetch type for {name}: {type(r)}")
                continue
            print(f"wrote workspace file {dest} ({dest.stat().st_size} bytes)")
            break


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--poll-minutes", type=float, default=40.0)
    ap.add_argument("--interval-seconds", type=float, default=120.0)
    ap.add_argument("--watch-pr", type=int, default=0)
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

    (OUT / f"round2-results-{task_id}.json").write_text(
        json.dumps(dump, indent=2, default=str)
    )

    answer = extract_answer(dump)
    if answer:
        (OUT / f"round2-results-{task_id}.md").write_text(answer)
        print(f"wrote answer ({len(answer)} chars)")
        fetch_workspace_files(answer)

    notebook = dump.get("notebook")
    if notebook:
        (OUT / f"round2-results-{task_id}-notebook.ipynb").write_text(
            json.dumps(notebook, indent=2, default=str)
        )
        n_fig = 0
        for cell in notebook.get("cells", []):
            for outp in cell.get("outputs", []):
                png = (outp.get("data") or {}).get("image/png")
                if png:
                    n_fig += 1
                    (OUT / f"round2-results-{task_id}-fig{n_fig}.png").write_bytes(
                        base64.b64decode(png)
                    )
        if n_fig:
            print(f"extracted {n_fig} figures from notebook")

    print(f"final status: {dump.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
