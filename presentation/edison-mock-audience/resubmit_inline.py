"""Resubmit the mock-audience analysis with documents inlined in the query.

Two prior submissions with file uploads failed with no failure_reason and a
null environment_frame (sandbox died before the agent ran), so this variant
embeds the three small documents directly in the query text instead of
attaching them.

Usage: python resubmit_inline.py
Requires EDISON_PLATFORM_API_KEY (or EDISON_API_KEY) in the environment.
"""

import os
import re
import sys
from pathlib import Path

from edison_client import EdisonClient, JobNames
from edison_client.models import TaskRequest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "presentation"))
from edison_mock_audience_job import QUERY  # noqa: E402

DOCS = {
    "doumont-presentation-template.md": REPO
    / "presentation"
    / "doumont-presentation-template.md",
    "idetc-abstract.tex": REPO / "idetc-abstract.tex",
    "doumont-video-notes.md": REPO / "presentation" / "doumont-video-notes.md",
}

query = re.sub(r"Attached files:", "Documents (inlined below):", QUERY)
parts = [query, "\n\n---\n\nDOCUMENTS\n"]
for name, path in DOCS.items():
    parts.append(f"\n===== BEGIN {name} =====\n")
    parts.append(path.read_text())
    parts.append(f"\n===== END {name} =====\n")
full_query = "".join(parts)

api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ["EDISON_API_KEY"]
client = EdisonClient(api_key=api_key)
task_data = TaskRequest(name=JobNames.ANALYSIS, query=full_query)
task_ids = client.create_task(task_data)
task_id = task_ids[0] if isinstance(task_ids, (list, tuple)) else task_ids
(HERE / "task-id.txt").write_text(str(task_id) + "\n")
print(f"submitted task {task_id}", flush=True)
