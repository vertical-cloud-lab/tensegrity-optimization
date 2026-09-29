"""Poll and fetch the Edison ANALYSIS task reviewing Justin's work analysis
(see submit_work_review.py).

Writes the markdown answer and the full JSON dump. Polls in the
foreground on purpose (see CLAUDE.md), and prints any new comments on issue
#114 while it waits so they can be picked up. Every file the trajectory
created (Edison's script, CSV, figures, notebook) goes to artifacts/.

Run from the repository root:
    python analysis/issue-114-work/edison/fetch_work_review.py --poll-minutes 30
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from edison_client import EdisonClient

OUT = Path(__file__).resolve().parent
TASK_ID = json.loads((OUT / "_task_id.json").read_text())["task_id"]
PREFIX = f"edison-{TASK_ID[:8]}"


def client() -> EdisonClient:
    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY")
    if not api_key:
        raise SystemExit("EDISON_PLATFORM_API_KEY not set")
    return EdisonClient(api_key=api_key.strip())


def extract_answer(dump: dict) -> str:
    for key in ("formatted_answer", "answer"):
        if dump.get(key):
            return dump[key]
    ef = dump.get("environment_frame") or {}
    try:
        return ef["state"]["state"]["answer"] or ""
    except (KeyError, TypeError):
        return ""


def new_comments(seen: set[int]) -> list[str]:
    try:
        out = subprocess.run(
            ["gh", "api", "repos/vertical-cloud-lab/tensegrity-optimization/issues/114/comments",
             "--jq", '.[] | [.id, .user.login, .created_at, .body[0:300]] | @json'],
            capture_output=True, text=True, timeout=30, check=True,
        ).stdout
    except Exception:
        return []
    lines = []
    for raw in out.splitlines():
        cid, user, created, body = json.loads(raw)
        if cid not in seen:
            seen.add(cid)
            lines.append(f"{created} {user}: {body!r}")
    return lines


def fetch_artifacts(c: EdisonClient) -> None:
    """Download every file the trajectory created, via the provenance API."""
    dest_dir = OUT / "artifacts"
    dest_dir.mkdir(exist_ok=True)
    done: set[str] = set()
    for entry in c.list_files(TASK_ID).get("data", []):
        ds = entry.get("data_storage") or {}
        sid, name = entry.get("data_storage_id"), ds.get("name")
        if not name or sid in done or ds.get("is_collection"):
            continue
        done.add(sid)
        try:
            res = c.fetch_data_from_storage(sid)
        except Exception as exc:
            print(f"fetch failed for {name}: {type(exc).__name__}")
            continue
        dest = dest_dir / Path(name).name
        if isinstance(res, Path):
            shutil.copy(res, dest)
        elif isinstance(res, list):
            for path in res:
                shutil.copy(path, dest_dir / Path(path).name)
            continue
        elif res is not None and getattr(res, "content", None) is not None:
            content = res.content
            dest.write_bytes(content) if isinstance(content, bytes) else dest.write_text(content)
        else:
            print(f"nothing returned for {name}")
            continue
        print(f"wrote artifacts/{dest.name} ({dest.stat().st_size} bytes)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--poll-minutes", type=float, default=30.0)
    ap.add_argument("--interval-seconds", type=float, default=120.0)
    args = ap.parse_args()

    c = client()
    seen: set[int] = set()
    new_comments(seen)  # mark what is already there
    deadline = time.time() + 60 * args.poll_minutes
    while True:
        dump = c.get_task(TASK_ID, verbose=True).model_dump()
        status = str(dump.get("status", "")).lower()
        print(time.strftime("%H:%M:%S", time.gmtime()), "status:", status, flush=True)
        for line in new_comments(seen):
            print("NEW COMMENT", line, flush=True)
        if any(s in status for s in ("success", "fail", "cancel", "error", "truncat")):
            break
        if time.time() >= deadline:
            print("poll window elapsed; task still running. Re-run to fetch later.")
            return 1
        time.sleep(args.interval_seconds)

    (OUT / f"{PREFIX}.json").write_text(json.dumps(dump, indent=2, default=str))
    answer = extract_answer(dump)
    if answer:
        (OUT / f"{PREFIX}-answer.md").write_text(answer)
        print(f"wrote answer ({len(answer)} chars)")
    fetch_artifacts(c)
    notebook = dump.get("notebook")
    if notebook:
        (OUT / f"{PREFIX}-notebook.ipynb").write_text(json.dumps(notebook, indent=1, default=str))
        n_fig = 0
        for cell in notebook.get("cells", []):
            for outp in cell.get("outputs", []) or []:
                png = (outp.get("data") or {}).get("image/png")
                if png:
                    n_fig += 1
                    (OUT / f"{PREFIX}-fig{n_fig}.png").write_bytes(base64.b64decode(png))
        print(f"notebook saved, {n_fig} figures extracted")
    print("final status:", dump.get("status"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
