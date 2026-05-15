"""Poll and fetch payload-vs-no-payload Edison task."""
from __future__ import annotations
import json, os, pathlib, time
from datetime import datetime, timezone

os.environ.setdefault(
    "EDISON_PLATFORM_API_KEY",
    os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY", ""),
)
from edison_client import EdisonClient  # noqa: E402

TRAJ_ID = "37ae0665-9ae7-4171-b366-099141098975"
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "edison-trajectories"

QUERY_FILE = REPO_ROOT / "scripts/edison/submit_payload_vs_no_payload.py"
SUBMITTED_AT = "2026-05-15T18:55:32Z"


def main() -> None:
    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY")
    )
    deadline = time.time() + 45 * 60
    last = None
    result = None
    while time.time() < deadline:
        try:
            result = client.get_task(task_id=TRAJ_ID, verbose=False)
        except Exception as exc:  # noqa: BLE001
            print(f"  poll err: {exc!r}")
            time.sleep(30)
            continue
        status = str(getattr(result, "status", "")).lower()
        if status != last:
            print(f"  [{datetime.now(timezone.utc).strftime('%H:%M:%S')}] status: {status}")
            last = status
        if status in {"success", "failed", "error", "cancelled"}:
            break
        time.sleep(30)

    result = client.get_task(task_id=TRAJ_ID, verbose=True)
    md_path = OUT_DIR / f"payload-vs-no-payload-{TRAJ_ID}.md"
    json_path = OUT_DIR / f"payload-vs-no-payload-{TRAJ_ID}.json"
    formatted = getattr(result, "formatted_answer", None) or ""
    # Read original question from submit script
    submit_text = QUERY_FILE.read_text()
    q_start = submit_text.find('QUERY = """\n') + len('QUERY = """\n')
    q_end = submit_text.find('""".strip()', q_start)
    question = submit_text[q_start:q_end].strip()
    md_path.write_text(
        f"# Edison literature brief: payload vs no-payload in tensegrity drop sims/experiments\n\n"
        f"- **Task ID:** `{TRAJ_ID}`\n"
        f"- **Job:** `LITERATURE_HIGH`\n"
        f"- **Submitted:** {SUBMITTED_AT}\n"
        f"- **Fetched:** {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- **Status:** {getattr(result, 'status', 'unknown')}\n"
        f"- **Related issues/PRs:** #46, #47, #50, #16, #28, #18, #49, #14, #45\n\n"
        f"---\n\nQuestion:\n\n{question}\n\n---\n\n{formatted}\n"
    )
    try:
        json_path.write_text(result.model_dump_json(indent=2))
    except Exception:
        json_path.write_text(json.dumps(result, default=str, indent=2))
    print(f"  wrote {md_path.relative_to(REPO_ROOT)}")
    print(f"  wrote {json_path.relative_to(REPO_ROOT)}")
    pointer = OUT_DIR / f"payload-vs-no-payload-{TRAJ_ID}-SUBMITTED.json"
    if pointer.exists():
        pointer.unlink()


if __name__ == "__main__":
    main()
