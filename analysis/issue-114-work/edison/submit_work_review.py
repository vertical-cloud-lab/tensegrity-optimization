"""Submit an Edison Scientific ANALYSIS task that audits Justin's
work-done-by-the-specimen analysis of the corny7 drops (issue #114).

Driven by the issue #114 thread (2026-09-29): Justin asked "@claude analyze
this work and provide your thoughts on how valid this is for our
application. Look for any potential errors in modeling but also acknowledge
if there are none or few. Do an edison review on it." and Marcus replied
"@claude do as Justin says."

The bundle holds Justin's two scripts, his handwritten derivation (PDF plus a
transcription), his two plots, his stated intent, and the corny7 export from
issue #110 (branch claude/issue-110-20260928-2047, commit 5cc4b1e).

Idempotent: records the task id in _task_id.json and reuses it.
Run from the repository root:  python analysis/issue-114-work/edison/submit_work_review.py
"""
from __future__ import annotations

import json
import os
import shutil
import urllib.request
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
OUT = HERE
SUBMITTED = OUT / "_task_id.json"

CORNY7_RAW = (
    "https://raw.githubusercontent.com/vertical-cloud-lab/tensegrity-optimization/"
    "5cc4b1e/data/drop-tests/corny7-export/"
)

BUNDLE_FILES = {
    "justin_numarical_work.py": WORK / "justin" / "numarical_work.py",
    "justin_implimatation_or_work.py": WORK / "justin" / "implimatation_or_work.py",
    "justin_work_derivation.pdf": WORK / "justin" / "work-derivation-2026-09-29.pdf",
    "justin_derivation_transcribed.md": WORK / "justin" / "derivation_transcribed.md",
    "justin_intent.md": WORK / "justin" / "intent.md",
    "justin_plot_drop1.png": WORK / "justin" / "corny7_trial1_work.png",
    "justin_plot_drop2.png": WORK / "justin" / "corny7_trial2_work.png",
}
CORNY7_FILES = ["corny7_waveforms_50kHz.csv", "corny7_drops.csv", "README.md"]

PROMPT = r"""
You are reviewing an undergraduate's analysis for a research group that drop-tests 3D-printed tensegrity-inspired
energy absorbers (rigid PLA struts + flexible TPU cables, a "T3 prism", specimen mass 19.62 g, height 67.12 mm) on a
Lansmont drop tower. The specimen sits on a base plate that falls 60 in (1.524 m) onto a 1/2 in polyurethane mat.
CH5 is a single-axis accelerometer on the base plate (the input). CH2, CH3, CH4 are a triaxial accelerometer seated
at the specimen's top vertex (the output). The recorder samples 1.25 MHz for 100 ms per drop starting 2 ms before a
150 G trigger on CH5; the attached CSV is that data downsampled (with anti-aliasing) to 50 kHz, with NO zeroing and
NO filtering, in units of G. See corny7_README.md for the full description of the data and the lab's own metrics.
The lab currently ranks designs by transmissibility T180 (CFC-180 filtered output peak / input peak).

The student (Justin) wants a second metric: the total work done by the specimen, which he hypothesizes should be
negative and equal in magnitude to the energy the specimen dissipates. His model (see justin_work_derivation.pdf and
the transcription justin_derivation_transcribed.md): the specimen is a massless spring between the base plate
(bottom) and a point mass m at the top vertex; F_s = m (g + a_top); W = integral of F_s (v_top - v_bottom) dt,
approximated as sum F_s(t) (dx_top(t) - dx_bottom(t)), with v and x built by cumulative trapezoid integration of the
accelerations. He sets m = 1 kg (so the result is J per kg of top mass) and v0 = 0. justin_numarical_work.py tests
the integration scheme against a polynomial acceleration whose work integral is known in closed form, and fits an
empirical per-step "error" correction err = u*a(t) + v. justin_implimatation_or_work.py applies the method to
corny7 drops 1 and 2 and produces justin_plot_drop1.png and justin_plot_drop2.png. His stated intent is in
justin_intent.md.

Please do all of the following, running code on the attached data (Python, numpy/scipy) rather than reasoning only:

1. Audit the derivation. Is W = integral F_s (v_top - v_bottom) dt the right quantity for "energy dissipated by the
   specimen"? Are the signs, the free-body diagram, and the gravity term right, given what these accelerometers
   physically measure (kinematic acceleration versus specific force / proper acceleration; AC-coupled piezoelectric
   versus DC-response sensors)? State the conditions under which -W equals the dissipated energy.
2. Reproduce Justin's numbers by running his implementation script as written (drop 1 and drop 2), then audit it
   line by line: which data column is used for which physical quantity, which drop numbers are selected (the lab
   treats drops 1 and 2 as warm-up drops), the initial conditions, the treatment of sensor offsets, and the
   quadrature scheme.
3. Test physical plausibility of every intermediate quantity, especially the implied relative displacement
   x_top - x_bottom (the specimen is 67 mm tall), the implied relative velocity at the end of the record, and the
   magnitude of W against the kinetic-energy bound (about 0.5 * v_impact^2 per unit top mass, v_impact about
   5.2 to 5.5 m/s).
4. Audit justin_numarical_work.py: does the polynomial test validate what matters for the real data? Is the fitted
   u*a + v correction justified, or is it compensating for a specific quadrature choice? What would a clean
   verification look like?
5. Propose and implement a corrected pipeline (channel selection, zeroing/offset handling, integration window,
   drift correction or boundary conditions, effective top mass including the specimen's own distributed mass, and
   a force-deflection hysteresis-loop plot). Run it on drops 3 to 20 and report the per-drop energy with an
   uncertainty or sensitivity range. Save your figures and a CSV of per-drop results.
6. Give a verdict on how valid and useful this metric is for the group's application (ranking designs for energy
   absorption in a Bayesian-optimization campaign alongside T180), what it would take to make it trustworthy (for
   example a displacement or velocity measurement such as a laser vibrometer or high-speed video), and cite relevant
   standards and literature on energy absorption from drop/impact tests and on double-integration drift of shock
   accelerometer data (for example SAE J211, ASTM D1596 cushion testing, zero-shift in piezoelectric shock
   accelerometers).

Be specific and quantitative. Acknowledge what is correct in the student's work as clearly as what is wrong.
Finally, a first-pass reviewer made the claims below. Try to REFUTE each one with the data; report which survive:
  (a) CH4, not CH2, is the vertical axis of the top triaxial accelerometer;
  (b) the raw channels carry multi-G offsets that dominate the double integration, so the student's work curve is
      mostly drift;
  (c) the physics of the derivation (W = integral F_s dL with F_s = m(g + a_top), a_top kinematic) is sound.
"""


def main() -> int:
    if SUBMITTED.exists():
        print("reusing task_id:", json.loads(SUBMITTED.read_text())["task_id"])
        return 0

    api_key = os.environ.get("EDISON_PLATFORM_API_KEY") or os.environ.get("EDISON_API_KEY")
    if not api_key:
        raise SystemExit("EDISON_PLATFORM_API_KEY not set")
    client = EdisonClient(api_key=api_key.strip())

    bundle = OUT / "bundle"
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)
    for dest, src in BUNDLE_FILES.items():
        shutil.copy2(src, bundle / dest)
    for name in CORNY7_FILES:
        dest = bundle / ("corny7_README.md" if name == "README.md" else name)
        urllib.request.urlretrieve(CORNY7_RAW + name, dest)
    (bundle / "PROMPT.md").write_text(PROMPT.strip() + "\n")
    print("bundle:", sorted(p.name for p in bundle.iterdir()))

    resp = client.store_file_content(
        name="issue-114-work-review",
        file_path=str(bundle),
        as_collection=True,
    )
    uri = f"data_entry:{resp.data_storage.id}"
    print("uploaded collection:", uri)

    task = TaskRequest(name=JobNames.ANALYSIS, query=PROMPT.strip())
    submitted = client.create_task(task, files=[uri])
    task_id = submitted if isinstance(submitted, str) else str(submitted)
    print("submitted task_id:", task_id)
    SUBMITTED.write_text(
        json.dumps({"task_id": task_id, "uploaded_files": [uri], "task_type": "ANALYSIS"}, indent=2) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
