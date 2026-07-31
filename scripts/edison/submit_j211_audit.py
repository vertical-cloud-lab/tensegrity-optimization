"""Submit an Edison Scientific ANALYSIS task that CHECKS OUR SIGNAL PROCESSING
against the standards we cite, rather than checking our conclusions.

Driven by sgbaird issue #94:
> we'd like to better understand the analysis that you're taking with #86 ...
> it was surprising to me that you went from CFC-180 to suggesting something
> else (CFC-1080 or something like that?) ... it would be best for us to
> spot-check your work ... especially backed up by real-sources (cross-checked
> via Edison)

The adversarial review in ``edison-trajectories/pu-configs/`` attacked the
*conclusions* of ``docs/drop-test-pu-configs-analysis.md``. This task attacks
one layer lower: the three primitives that every drop-test script in this repo
is built on --

  1. ``cfc_filter()``  -- our SAE J211 channel-frequency-class implementation,
  2. the baseline / zero-offset correction, and
  3. ``T = peak(output)/peak(input)`` as an objective,

with the specific numeric claims we have published from them. We already have
an in-repo finding for (1) that we want independently confirmed or refuted --
it is stated openly in the prompt so the reviewer can disagree with it.

Idempotent: records the task id in j211-audit-SUBMITTED.json and reuses it.
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "j211-audit"
OUT.mkdir(parents=True, exist_ok=True)
SUBMITTED = OUT / "j211-audit-SUBMITTED.json"

api_key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
if not api_key:
    raise SystemExit("EDISON_API_KEY (or EDISON_PLATFORM_API_KEY) not set")
client = EdisonClient(api_key=api_key.strip())

PROMPT = r"""
STANDARDS / IMPLEMENTATION AUDIT. This is a narrow, checkable request: verify or
refute specific numeric claims about signal-processing primitives against the
published standards. Please do not spend effort on our experimental conclusions
-- a previous task already reviewed those. Cite clause/appendix numbers where
you can, and say explicitly where you are inferring rather than quoting.

=== SETTING ===

Benchtop drop tower for 3D-printed tensegrity unit cells. A carriage with a
bottom acrylic plate is dropped onto a polyurethane absorber stack. Two
accelerometer groups: CH5, single-axis on the bottom plate (the INPUT and the
trigger channel), and CH2/CH3/CH4, a tri-axis wax-mounted at the specimen's top
vertex (the OUTPUT). Recent exports are 1.25 MHz sample rate over a 20 ms
record; older ones are 125 kHz over 200 ms. Every analysis in the repository
reduces a drop to

    T = peak( sqrt(CH2^2 + CH3^2 + CH4^2) )  /  peak( CH5 )

with both sides low-pass filtered to an SAE J211 channel frequency class, and
compares T across absorber configurations and specimen geometries. Typical
published T values are 0.94-1.22 with within-block CVs of 0.3-1.5 %, i.e. the
effects we act on are a few percent.

=== QUESTION 1 (the main one): IS OUR CFC FILTER A CORRECT J211 CFC FILTER? ===

Our implementation, used unchanged by ~30 analysis scripts, is exactly this
(Python / SciPy; attached as cfc_filter_excerpt.py):

    def cfc_filter(x, fs, cfc):
        cutoff = {1000: 1650.0, 600: 1000.0, 180: 300.0, 60: 100.0}[cfc]
        b, a = signal.butter(2, cutoff / (fs / 2.0), btype="low")
        return signal.filtfilt(b, a, x)

`scipy.signal.butter(2, Wn)` returns a 2-pole Butterworth whose SINGLE-PASS
-3 dB point is at Wn. `scipy.signal.filtfilt` applies it forward and backward,
so the overall amplitude response is the SQUARE of the single-pass response.

Our reading of SAE J211-1 Appendix C is that the CFC digital filter is a 2-pole
Butterworth with

    wd = 2*pi*CFC*2.0775 ,   wa = tan(wd*T/2)  (T = sample interval)
    a0 = wa^2 / (1 + sqrt(2)*wa + wa^2),  a1 = 2*a0,  a2 = a0
    b1 = -2*(wa^2 - 1) / (1 + sqrt(2)*wa + wa^2)
    b2 = (-1 + sqrt(2)*wa - wa^2) / (1 + sqrt(2)*wa + wa^2)

applied forward and then backward (phaseless), and that the factor 2.0775
exists precisely so that the FORWARD-BACKWARD PAIR is -3 dB at 1.65*CFC, i.e.
2.0775 is the SINGLE-PASS corner and 1.65*CFC is the TWO-PASS corner.

If that reading is right, our code has an off-by-one-stage error: it puts
1.65*CFC at the single-pass corner, so the two-pass corner lands at
0.802 * 1.65 * CFC. We computed the consequences numerically and get:

    claimed class   spec two-pass -3 dB   our actual two-pass -3 dB   effective class
    CFC-60                 99 Hz                  80 Hz                  CFC-49
    CFC-180               297 Hz                 241 Hz                  CFC-146
    CFC-600               990 Hz                 802 Hz                  CFC-486
    CFC-1000             1650 Hz                1324 Hz                  CFC-802

    two-pass amplitude gain at 550 Hz:  correct CFC-180 0.176 ,  ours 0.081
    two-pass amplitude gain at 550 Hz:  correct CFC-1000 0.995 ,  ours 0.988

Please:
 (1a) State the correct J211 CFC filter definition from the standard, with the
      clause/appendix reference, including the 2.0775 factor, the 1.65*CFC
      -3 dB relation, and WHICH of those applies per pass vs to the pair.
      Confirm or refute our reading. If our reading is wrong, give the correct
      one and recompute the table above.
 (1b) Confirm or refute the numeric table. Is our filter really ~20 % narrow in
      frequency in every class, i.e. is what we have been calling "CFC-180"
      actually closer to CFC-146?
 (1c) We have published the claim that "CFC-180 is 3 dB down at 300 Hz, so at
      the specimens' ~550 Hz mode it attenuates by roughly 12x", and that claim
      was the stated motivation for adding a second, wider analysis band
      (CFC-1000) whose repeatability then decided which absorber arrangement we
      recommended. Under a CORRECT CFC-180 the attenuation at 550 Hz appears to
      be about 5.7x, not 12x -- i.e. our 12x figure looks like an artifact of
      the implementation error rather than a property of J211 CFC-180. Confirm
      or refute, and give the correct attenuation at 500 / 550 / 600 / 800 Hz
      for a correct CFC-180 and a correct CFC-1000.
 (1d) J211 also imposes requirements we may be violating independent of the
      corner frequency: sample-rate minimums relative to CFC, anti-alias
      filtering, and the handling of record ends for the phaseless pass. State
      them. In particular: what does the standard require for the data padding
      / initial conditions of the backward pass, and is SciPy's default
      `filtfilt` odd-reflection padding (`padtype='odd'`, `padlen=3*max(len(a),
      len(b))` = 9 samples here) adequate at 1.25 MHz for CFC-180? 9 samples is
      7.2 microseconds, versus a ~3.3 ms filter-relevant timescale.
 (1e) PRACTICAL IMPACT. Does a ~20 % error in the corner frequency materially
      change a ratio of PEAK values of two channels that are both filtered with
      the same wrong filter -- i.e. does the error largely cancel in T? Our own
      recomputation on 40 real drops says the effect on T(CFC-180) is under
      1 %, but on T(CFC-1000) it is up to +9 % on the harshest arrangement.
      Explain the mechanism and say for which of our reported quantities
      (peak G, pulse half-max width, delta-v by integration, T, band energy
      fractions) the error is and is not consequential.

=== QUESTION 2: BASELINE CORRECTION AND PRE-TRIGGER LENGTH ===

Our 1.25 MHz / 20 ms exports are triggered captures. We originally believed
they contained no pre-trigger data and used a FULL-RECORD MEDIAN as the zero
offset. They in fact contain about 0.35 ms of pre-trigger (first raw CH5
trigger crossing at 0.26-0.39 ms into the record, measured over 40 drops).

We then recomputed with a pre-trigger-mean baseline and found T moves a lot,
AND that it depends strongly on how much of that 0.35 ms you average. Using
windows of 0.05 / 0.10 / 0.20 / 0.30 ms ending 8 microseconds before the
crossing, mean T (CFC-180) for one arrangement runs 1.365 / 1.317 / 1.228 /
1.194, versus 0.989 under the full-record median. The between-arrangement
differences we were trying to resolve are 1-3 %.

 (2a) What do SAE J211-1 and ISO 6487 actually require for zero-offset / bias
      removal on an impact channel -- which window, what minimum pre-event
      duration, and is a full-record median ever admissible? Quote the clause.
 (2b) What minimum pre-trigger duration should we specify for a 550 Hz-ish
      structure sampled at 1.25 MHz, and on what basis (cycles of the lowest
      band of interest? filter settling time? a fixed multiple of the pulse
      duration?)? Is our proposed ">= 2 ms pre-trigger, 50-100 ms post-impact"
      adequate, over-specified, or under-specified?
 (2c) Given ONLY 0.35 ms of pre-trigger, is ANY baseline estimator defensible
      to the ~1 % level we need, or should we state plainly that this dataset
      cannot support a 1-3 % comparison and must be recollected? We would
      rather be told to recollect than to pick the least-bad estimator.
 (2d) A subtlety we want checked: the output side is a VECTOR MAGNITUDE
      sqrt(x^2+y^2+z^2). A per-axis DC offset error does not propagate linearly
      through that. Does that make the resultant systematically more
      baseline-sensitive than a single axis, and is a resultant peak a sound
      quantity to baseline-correct at all, or should the baseline be removed
      per axis before the magnitude (as we do) with some additional caveat?

=== QUESTION 3: IS FILTERED PEAK-RATIO "TRANSMISSIBILITY" A REAL METRIC? ===

 (3a) Is "T = ratio of CFC-filtered peak magnitudes at two points" a recognised
      quantity in shock/packaging/vibration practice (ASTM D3332, D7136,
      MIL-STD-810 method 516, ISO 18431, IEST shock practice), or is it a local
      coinage? If it appears in practice, under what name and with what stated
      validity conditions?
 (3b) The two peaks generally occur at different times and are dominated by
      different frequencies, and the numerator is a nonlinear function of three
      channels. Enumerate the conditions under which such a ratio is
      interpretable as a transmissibility, and say whether a drop tower with a
      soft polymer absorber and a light compliant specimen plausibly meets
      them.
 (3c) We are told the right replacements are an input-conditioned output SRS or
      a band-limited H1 transfer function with coherence. For a SINGLE
      transient per test (not a stationary process), how is coherence even
      estimated defensibly -- across repeat drops as the ensemble, or via
      segment averaging within one record? Give the standard practice and its
      minimum ensemble size.
 (3d) Sanity check on the mounting side, since it bounds every number above:
      for a wax-mounted tri-axial accelerometer on a small printed polymer
      part, what upper frequency is trustworthy, and what standard states it?
      Our documents have cited "ISO 5347" for mounting; we now believe the
      correct reference is ISO 5348 (mechanical mounting of accelerometers).
      Confirm which is correct and what each actually covers.

=== WHAT TO RETURN ===

A single self-contained markdown report. Structure it as: (i) a verdict table
with one row per numbered sub-question and a CONFIRMED / REFUTED / PARTIAL
column, (ii) the corrected filter definition and a corrected version of our
`cfc_filter` function that we can drop in, (iii) the standards clauses with
references, (iv) a short list of which of our published numbers must be
recomputed and which are safe. Lead with anything that means a number we have
already reported is wrong.

Attached: the exact filter excerpt as used (cfc_filter_excerpt.py), our
verification script and its output (cfc_verification.py, cfc_verification.txt),
the pu-configs analysis script that consumes it, and the analysis markdown.
"""


def main() -> int:
    bundle = OUT / "bundle"
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)

    for src, dst in [
        (REPO / "scripts" / "analysis" / "cfc_filter_excerpt.py", "cfc_filter_excerpt.py"),
        (REPO / "scripts" / "analysis" / "cfc_verification.py", "cfc_verification.py"),
        (OUT / "cfc_verification.txt", "cfc_verification.txt"),
    ]:
        if src.exists():
            shutil.copy2(src, bundle / dst)

    print(f"bundle: {sorted(p.name for p in bundle.iterdir())}")

    if SUBMITTED.exists():
        task_id = json.loads(SUBMITTED.read_text())["task_id"]
        print("reusing task_id:", task_id)
        return 0

    resp = client.store_file_content(
        name="j211-cfc-filter-audit",
        file_path=str(bundle),
        as_collection=True,
    )
    uri = f"data_entry:{resp.data_storage.id}"
    print("uploaded collection:", uri)

    task = TaskRequest(name=JobNames.ANALYSIS, query=PROMPT)
    submitted = client.create_task(task, files=[uri])
    task_id = submitted if isinstance(submitted, str) else str(submitted)
    print("submitted task_id:", task_id)

    SUBMITTED.write_text(
        json.dumps(
            {"task_id": task_id, "uploaded_files": [uri], "task_type": "ANALYSIS"},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
