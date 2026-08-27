"""Poll + fetch the Edison Scientific ANALYSIS task for the clip-height /
accelerometer-check drop diagnostic (see submit_clip_height.py).

Writes the markdown answer, the full JSON dump, the notebook, and any inline
base64 figures into edison-trajectories/clip-height/.
"""
from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

from edison_client import EdisonClient

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "clip-height"
SUBMITTED = OUT / "clip-height-SUBMITTED.json"

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


def main() -> int:
    deadline = time.time() + 60 * 40
    dump = None
    while time.time() < deadline:
        resp = client.get_task(task_id)
        dump = resp.model_dump()
        status = str(dump.get("status", "")).lower()
        print(f"status: {status}")
        if any(s in status for s in ("success", "fail", "cancel", "truncat")):
            break
        time.sleep(20)

    if dump is None:
        raise SystemExit("no response")

    (OUT / f"clip-height-{task_id}.json").write_text(json.dumps(dump, indent=2, default=str))

    answer = extract_answer(dump)
    if answer:
        (OUT / f"clip-height-{task_id}.md").write_text(answer)
        print(f"wrote answer ({len(answer)} chars)")

    notebook = dump.get("notebook")
    if notebook:
        (OUT / f"clip-height-{task_id}-notebook.ipynb").write_text(
            json.dumps(notebook, indent=2, default=str)
        )
        # extract inline base64 figures from notebook cell outputs
        n_fig = 0
        for cell in notebook.get("cells", []):
            for outp in cell.get("outputs", []):
                data = outp.get("data", {})
                png = data.get("image/png")
                if png:
                    n_fig += 1
                    (OUT / f"clip-height-{task_id}-fig{n_fig}.png").write_bytes(
                        base64.b64decode(png)
                    )
        if n_fig:
            print(f"extracted {n_fig} figures from notebook")

    print(f"final status: {dump.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
