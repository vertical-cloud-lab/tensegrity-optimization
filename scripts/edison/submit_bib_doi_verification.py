#!/usr/bin/env python3
"""Submit an Edison (LITERATURE_HIGH) task asking for DOIs / DOI verification
for the bibliography entries that the local Crossref pass could not resolve.

Input is ``edison-trajectories/bib-doi-verification/needs-list.md`` (generated
from ``manuscript/references-full.bib`` -- see PR discussion). The list has two
sections:

  A. entries whose stored DOI resolves to an unrelated paper or 404s, and
  B. entries that have no DOI at all.

The task is submitted non-blocking: the task id is recorded in a
``*-SUBMITTED.json`` placeholder so the result can be fetched next session
(``client.get_task(task_id).model_dump_json()``) and folded back into the bib,
matching the repo's Edison-trajectory convention.

Run::

    python scripts/edison/submit_bib_doi_verification.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

# edison-client >= 0.12 reads EDISON_PLATFORM_API_KEY; map the documented
# EDISON_API_KEY onto it if only the old name is set.
if os.environ.get("EDISON_API_KEY") and not os.environ.get("EDISON_PLATFORM_API_KEY"):
    os.environ["EDISON_PLATFORM_API_KEY"] = os.environ["EDISON_API_KEY"]

from edison_client import EdisonClient, JobNames  # noqa: E402
from edison_client.models import TaskRequest  # noqa: E402

HERE = Path(__file__).resolve().parents[2]
TRAJ = HERE / "edison-trajectories" / "bib-doi-verification"
NEEDS = TRAJ / "needs-list.md"
SUBMITTED = TRAJ / "bib-doi-verification-SUBMITTED.json"

QUERY = """\
I am cleaning a BibTeX bibliography for a mechanical-engineering manuscript on \
Bayesian-optimization-driven, multi-material 3D-printed tensegrity structures \
for impact protection. Attached (and inlined below) is a list of references \
that still need DOI work, in two groups:

(A) entries whose currently stored DOI is WRONG -- it resolves to an unrelated \
paper or returns a 404. For each, please find and return the CORRECT DOI for \
the cited work (matching author, title, year, and venue), or state clearly that \
the reference appears not to exist / cannot be verified.

(B) entries that have NO DOI. For each, please return the DOI if one exists, or \
state "no DOI" if the work genuinely has none (theses, standards, patents, \
preprints without a DOI, etc.).

For every DOI you return, please VERIFY that https://doi.org/<doi> resolves and \
that the landing page title matches the cited title (flag any mismatch). Return \
the results as a list keyed by the provided BibTeX key, each with: corrected/found \
DOI (or "no DOI" / "not found"), the verified title, and a one-line note on how \
you confirmed it. Where available, also include the abstract.

The list of references:

%s
""" % NEEDS.read_text()


def main() -> None:
    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY")
        or os.environ.get("EDISON_API_KEY")
    )

    files = []
    try:
        uri = client.upload_file(
            str(NEEDS),
            name="bib-doi-verification-needs-list.md",
            description="References needing DOI lookup/verification",
        )
        files = [uri]
        print(f"uploaded needs list -> {uri}")
    except Exception as exc:  # noqa: BLE001 - attachment is best-effort
        print(f"upload_file failed ({exc}); submitting query inline only")

    task = TaskRequest(name=JobNames.LITERATURE_HIGH, query=QUERY)
    submitted = client.create_task(task, files=files or None)

    task_id = getattr(submitted, "task_id", None) or (
        submitted if isinstance(submitted, str) else None
    )
    print(f"submitted task_id={task_id}")

    SUBMITTED.write_text(json.dumps({
        "task_id": str(task_id),
        "job": str(JobNames.LITERATURE_HIGH),
        "uploaded_files": files,
        "needs_list": str(NEEDS.relative_to(HERE)),
        "note": "non-blocking; fetch next session via client.get_task(task_id)",
    }, indent=2))
    print(f"wrote {SUBMITTED}")


if __name__ == "__main__":
    main()
