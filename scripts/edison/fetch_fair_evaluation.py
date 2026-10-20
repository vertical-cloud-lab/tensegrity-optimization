"""
Poll + fetch the ANALYSIS task submitted by submit_fair_evaluation.py
(PR comment 4760939061) and write the answer under
edison-trajectories/fair-evaluation/.

Task id is read from the *-SUBMITTED.json pointer in that directory, or from the
EDISON_TASK_ID env var.
"""

from __future__ import annotations

import glob
import json
import os
import pathlib
import time
from datetime import datetime, timezone

os.environ.setdefault(
    "EDISON_PLATFORM_API_KEY",
    os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY", ""),
)

from edison_client import EdisonClient  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "edison-trajectories" / "fair-evaluation"


def _resolve_task_id() -> str:
    tid = os.environ.get("EDISON_TASK_ID")
    if tid:
        return tid
    pointers = sorted(glob.glob(str(OUT_DIR / "*-SUBMITTED.json")))
    if not pointers:
        raise SystemExit("no SUBMITTED pointer found and EDISON_TASK_ID unset")
    return json.loads(pathlib.Path(pointers[-1]).read_text())["task_id"]


def _extract_answer(result) -> str:
    formatted = getattr(result, "formatted_answer", None) or ""
    try:
        ef = result.environment_frame
        ef_d = ef.model_dump() if hasattr(ef, "model_dump") else ef
        state = ef_d["state"]["state"]
        if isinstance(state.get("answer"), str) and state["answer"].strip():
            return state["answer"]
        answer = state["response"]["answer"]
        return answer.get("formatted_answer") or formatted
    except Exception:  # noqa: BLE001
        try:
            dump = result.model_dump()
            if isinstance(dump.get("answer"), str) and dump["answer"].strip():
                return dump["answer"]
        except Exception:  # noqa: BLE001
            pass
        return formatted


def main() -> None:
    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get(
        "EDISON_API_KEY"
    )
    if not api_key:
        raise SystemExit("EDISON_PLATFORM_API_KEY / EDISON_API_KEY env var not set")

    client = EdisonClient(api_key=api_key.strip())
    task_id = _resolve_task_id()
    print(f"polling task {task_id}")

    deadline = time.time() + 45 * 60
    poll_every = 30
    last_status = None
    while time.time() < deadline:
        try:
            status_resp = client.get_task(task_id=task_id, lite=True)
        except Exception as exc:  # noqa: BLE001
            print(f"  status poll failed: {exc!r}")
            time.sleep(poll_every)
            continue
        status = getattr(status_resp, "status", None) or str(status_resp)
        if status != last_status:
            print(
                f"  [{datetime.now(timezone.utc).strftime('%H:%M:%S')}] "
                f"status: {status}"
            )
            last_status = status
        if str(status).lower() in {"success", "failed", "error", "cancelled"}:
            break
        time.sleep(poll_every)

    result = client.get_task(task_id=task_id, verbose=True)
    formatted = _extract_answer(result)
    fetched = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    md_path = OUT_DIR / f"fair-evaluation-{task_id}.md"
    json_path = OUT_DIR / f"fair-evaluation-{task_id}.json"
    md_path.write_text(
        f"# Edison ANALYSIS brief: making the objective evaluations fair "
        f"(mass / volume / contact area)\n\n"
        f"- **Task ID:** `{task_id}`\n"
        f"- **Job:** `ANALYSIS`\n"
        f"- **Fetched:** {fetched}\n"
        f"- **Status:** {getattr(result, 'status', 'unknown')}\n"
        f"- **PR comment:** 4760939061\n\n"
        f"---\n\n{formatted}\n"
    )
    try:
        json_path.write_text(result.model_dump_json(indent=2))
    except Exception:  # noqa: BLE001
        json_path.write_text(json.dumps(result, default=str, indent=2))
    print(f"  wrote {md_path.relative_to(REPO_ROOT)} ({len(formatted)} chars)")
    print(f"  wrote {json_path.relative_to(REPO_ROOT)}")

    pointer = OUT_DIR / f"fair-evaluation-{task_id}-SUBMITTED.json"
    if pointer.exists() and formatted.strip():
        pointer.unlink()


if __name__ == "__main__":
    main()
