#!/usr/bin/env python3
"""Submit the PR #20 review T24 figure-feedback task to Edison ANALYSIS.

Uploads the node-only fabrication-workflow diagram (figures/fab-workflow.pdf,
staged in edison-trajectories/review-followups/fabfig-bundle/) as a single
zipped collection (required for ANALYSIS) and asks for structured feedback on
the diagram before it is populated with real cropped photographs.

Non-blocking: the task id is written to a *-SUBMITTED.json placeholder for a
later fetch via client.get_task(task_id).

Run::

    python scripts/edison/submit_fabfig_feedback.py
"""
from __future__ import annotations

import json
import os
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

from edison_client import EdisonClient, JobNames  # noqa: E402
from edison_client.models import TaskRequest  # noqa: E402

TRAJ = HERE / "edison-trajectories" / "review-followups"
BUNDLE = TRAJ / "fabfig-bundle.zip"
SUBMITTED = TRAJ / "t24-fabfig-feedback-SUBMITTED.json"

QUERY = """\
Attached (fab-workflow.pdf) is a NODE-ONLY draft schematic of the fabrication +
characterization workflow for a study on multi-material 3D-printed
tensegrity-inspired energy absorbers (rigid PLA struts + soft TPU tension
elements, printed on a Bambu Lab H2D dual-nozzle printer, then tested under
quasi-static compression and drop-weight impact). The nodes are:
design parameters -> parametric CAD (OpenSCAD T3-prism) -> slicing (Bambu
Studio, manual TPU supports) -> multi-material print (H2D, PLA+TPU) ->
post-process & inspect -> mechanical testing.

This figure will be used in an ASME Journal of Mechanical Design manuscript.
Please give concrete, actionable feedback BEFORE we populate each node with real
cropped photographs:

1. Is the stage sequence correct and complete for a multi-material FFF tensegrity
   workflow? Are any stages missing (e.g., material drying, calibration, joint
   assembly / pretensioning, data acquisition, BO design proposal feedback loop)?
2. Should the diagram show the closed BO loop (testing feeding back to the next
   design proposal), or keep it as a linear pipeline distinct from the separate
   closed-loop "overview" figure? Recommend how to avoid redundancy between the
   two figures.
3. Labeling / wording: suggest concise, publication-quality node labels and any
   sub-annotations (key parameters or settings) worth showing.
4. Layout: single-row vs. wrapped vs. two-row; arrow/branch styling; what makes
   the clearest journal figure.
5. For each node, what KIND of photograph or render best communicates it (e.g.,
   CAD ISO render, sliced-plate preview, printed-specimen photo, drop-tower /
   load-frame photo), and any cropping/annotation guidance.

We have candidate images available in the repo to populate the nodes, including:
CAD ISO renders (cad/t3-prism/t3-prism-iso.png), sliced plate previews
(bo/t3-prism-bo-batch-plate.png), a joint-design montage
(cad/joint-design/renders/all_compare_montage.png), an anchor-bulb specimen
montage (cad/anchor-bulb-tensioning-array/renders/all_specimens_montage.png),
a Lansmont M23 drop-tower photo, and a filtered drop-impact trace. Recommend
which to use where.

Return a prioritized, itemized revision list we can implement directly.
"""


def main() -> None:
    client = EdisonClient(
        api_key=os.environ.get("EDISON_PLATFORM_API_KEY")
        or os.environ.get("EDISON_API_KEY")
    )
    resp = client.store_file_content(
        name="fabfig-bundle",
        file_path=str(BUNDLE),
        as_collection=True,
    )
    entry_id = resp.data_storage.id
    uri = f"data_entry:{entry_id}"
    print(f"uploaded collection -> {uri}")

    task = TaskRequest(name=JobNames.ANALYSIS, query=QUERY)
    submitted = client.create_task(task, files=[uri])
    task_id = getattr(submitted, "task_id", None) or (
        submitted if isinstance(submitted, str) else None
    )
    print(f"submitted ANALYSIS task_id={task_id}")

    SUBMITTED.write_text(json.dumps({
        "slug": "t24-fabfig-feedback",
        "task_id": str(task_id),
        "job": str(JobNames.ANALYSIS),
        "uploaded_collection": uri,
        "note": "non-blocking; fetch next session via client.get_task(task_id)",
    }, indent=2))
    print(f"wrote {SUBMITTED}")


if __name__ == "__main__":
    main()
