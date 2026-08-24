"""Submit an Edison Scientific ANALYSIS task that ADVERSARIALLY REVIEWS our
polyurethane sheet-arrangement analysis (docs/drop-test-pu-configs-analysis.md).

Driven by sgbaird PR #86 comment 5137645029:
> send to Edison to question the underpinnings of the analysis mentioned here

"The analysis mentioned here" is the re-derived PU-config recommendation
(arrangement B, the 1/2 in sheet alone) that replaced an earlier recommendation
of arrangement A after the felt-continuity criterion was removed. The point of
this task is NOT to get the same answer back: it is to have an independent
analyst recompute from the raw CSVs and attack the assumptions the
recommendation rests on -- the 550 Hz "first mode", the f*tau <= 1.5
shock-regime criterion, the new CFC-1000 T-repeatability criterion that decided
A vs B, the band-energy fraction, the drop-level Welch statistics on
non-randomised sequential blocks, and the record-truncation confound introduced
by the mid-sweep trigger-level change.

Bundle: all 40 raw TP4 CSVs (4 arrangements x 10 drops, 1.25 MHz / 20 ms,
CH2-CH5), the TP4 series table, the dataset README, our analysis markdown, the
metrics JSON, our analysis script (so the method itself can be audited), and the
figures.

Idempotent: records the task id in pu-configs-SUBMITTED.json and reuses it.
"""
from __future__ import annotations

import json
import os
import shutil
import zipfile
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "pu-configs"
OUT.mkdir(parents=True, exist_ok=True)
SUBMITTED = OUT / "pu-configs-SUBMITTED.json"

# The repo's Copilot env injects the key as EDISON_API_KEY (older sessions saw
# EDISON_PLATFORM_API_KEY); read both, and strip a possible trailing newline.
api_key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
if not api_key:
    raise SystemExit("EDISON_API_KEY (or EDISON_PLATFORM_API_KEY) not set")
client = EdisonClient(api_key=api_key.strip())

PROMPT = r"""
ADVERSARIAL REVIEW REQUEST. Please try to BREAK the analysis below, not to
confirm it. We would rather learn that our recommendation is unsupported now
than after we run a 20-design Bayesian-optimization campaign on it. Where you
agree, say so briefly; spend your effort on what is wrong, unsupported, or
confounded. State explicitly which conclusions survive and which do not.

=== CONTEXT ===

We are qualifying a benchtop drop tower that will supply the objective for
Bayesian optimization of small (~50 mm edge) 3D-printed tensegrity unit cells
(PLA/PETG struts, TPU 85A tendons; "T3 prism" geometry). A carriage carrying a
bottom acrylic plate is dropped from 60 in onto an absorber stack. Instrumented
with a Vishay/PCB TP4 system:

  CH2/CH3/CH4  tri-axis accelerometer, wax-seated in a printed key-seat at the
               specimen's TOP vertex  -- the OUTPUT
               full scale 14492.8 / 14992.5 / 13624.0 G
  CH5          single-axis accelerometer on the BOTTOM acrylic plate
               -- the INPUT, and the trigger channel; full scale 9442.9 G

These captures are 1.25 MHz sample rate, 20 ms record, and the record STARTS AT
THE TRIGGER (there is little or no usable pre-trigger in these exports).

The absorber has until now been a stack of 4 felt sheets + 1 cardboard sheet,
which compacts: over ~700 drops the raw CH5 spike grew until it reached 91 % of
the input sensor's full scale. We are replacing it with adhesive-backed
polyurethane rubber sheets. This dataset is the arrangement sweep, ONE specimen
(`bpx68c`), 40 drops, all on 2026-07-30:

  A  1/4 in sheet alone            Signals 1-10   13:08-13:15  trigger 300 G
  B  1/2 in sheet alone            Signals 11-20  13:18-13:24  trigger 300 G
  (Signal 21, 13:26, is a stray capture -- excluded by the operator)
  C  1/4 in over 1/2 in            Signals 22-31  14:42-15:01  trigger 150 G
  D  1/2 in over 1/4 in            Signals 32-41  15:03-15:10  trigger 150 G

Note the blocks were run in fixed order, not randomised or interleaved, C/D
came ~80 minutes after A/B, and THE TRIGGER LEVEL WAS CHANGED between B and C.

=== OUR METHOD (attached as scripts/drop_test_pu_configs_analysis.py) ===

SAE J211 phaseless (zero-phase, forward-backward) Butterworth filtering:
CFC 1000 ~= 1650 Hz, CFC 180 ~= 300 Hz. We locate the impact on the triggered
CH5, baseline-correct, take CH5 as the input and the tri-axis RESULTANT
sqrt(CH2^2+CH3^2+CH4^2) as the output, and define transmissibility as a ratio of
filtered PEAK magnitudes, T = peak(output) / peak(input), per drop.

=== OUR RESULTS (per arrangement, 10 drops each) ===

              CH5 raw  input CFC180  CV    width    TOP CFC180  T(CFC180)  CV     T(CFC1000)  CV      450-800 Hz
  A (1/4)     2050 G   370.6 G      1.45%  1.66 ms  378.8 G     1.022      0.43%  1.163       6.12%   16.6 %
  B (1/2)      543 G   261.4 G      1.45%  2.25 ms  260.5 G     0.996      0.34%  0.990       1.36%   22.5 %
  C (1/4+1/2)  279 G   174.3 G      1.68%  3.37 ms  171.9 G     0.986      0.95%  1.074       0.93%   10.8 %
  D (1/2+1/4)  236 G   183.5 G      1.76%  3.35 ms  181.4 G     0.989      0.49%  1.074       1.19%   13.0 %

"450-800 Hz" is the FRACTION of raw top-vertex output energy in that band.

=== OUR CONCLUSION, AND THE ASSUMPTIONS IT RESTS ON ===

We recommend arrangement B (1/2 in alone) as the operating point, on four
grounds. Each is an assumption we want attacked:

 (1) B has the most repeatable T under BOTH analysis bands, and this was the
     deciding criterion: A's T(CFC-1000) CV is 6.12 % vs B's 1.36 %. We
     introduced "T(CFC-1000) CV <= 2 %" as an acceptance criterion after the
     fact, when an earlier felt-referenced criterion was removed.
 (2) The specimens' first mode is at 519-549 Hz (from ringdown analyses of
     earlier campaigns on this rig), so we required the input pulse to stay in
     the "shock regime" for that mode: for a half-sine of duration tau driving
     a lightly damped SDOF at f, we asserted the maximax response stays near
     its plateau while f*tau <~ 1.5 and decays toward unit (quasi-static) gain
     beyond it, giving tau <= 2.7 ms. A (1.66 ms) and B (2.25 ms) pass; C and D
     (~3.35 ms) fail.
 (3) B puts the largest FRACTION of output energy (22.5 %) into 450-800 Hz, so
     it is the arrangement most "excited where geometry matters". We used this
     to overturn an earlier claim (based on A's higher spectral centroid,
     2370 Hz) that A was the one exciting the structure.
 (4) A's problem is physical, not a setting: A's raw CH5 peak has CV 14.5 % and
     climbs +4.6 %/drop (bedding-in) while its FILTERED input holds at CV
     1.45 %. We argue CFC-180 discards that variable high-frequency contact
     spike so A looks pristine, while CFC-1000 admits it into both channels and
     A's T scatters.

We also claim: T falls monotonically with pulse duration (A 1.022 > B 0.996 >
D 0.989 > C 0.986, all pairwise Welch p < 0.01 except C vs D, p = 0.47), so T is
stack-dependent and PU-era values are not comparable with felt-era values; and
that a separate earlier 5-drop PU run with bimodal input (CV 25.7 %) is
explained by the two sheets seating inconsistently, because those drops fall on
the same severity-duration curve as this sweep.

=== WHAT WE WANT YOU TO DO ===

A. RECOMPUTE INDEPENDENTLY from the 40 attached CSVs. Choose your own impact
   location, baseline correction, and peak extraction. Report raw / CFC-1000 /
   CFC-180 input and output peaks, T, pulse width, and captured delta-v per
   drop and per arrangement, with your own uncertainty treatment. Do our table
   and CVs reproduce? Where they do not, say which of our processing choices is
   responsible.

B. ATTACK THE RECORD TRUNCATION AND FILTERING. The 20 ms record starts at the
   trigger and the CFC-180 CH5 signal is already at 22-53 % of its peak at
   t = 0, i.e. the pulse onset is cut off. Questions we cannot answer ourselves:
   (i) Do zero-phase (filtfilt) Butterworth filters applied to a record that
       begins mid-pulse produce edge transients large enough to corrupt the
       peaks, and does this corruption differ between CFC-180 and CFC-1000?
   (ii) THE TRIGGER LEVEL WAS 300 G FOR A/B AND 150 G FOR C/D. A lower trigger
       starts the record earlier on the pulse and truncates a different amount.
       Is our A-vs-B/C-vs-D comparison -- and specifically the CFC-1000 T CV
       that decided the recommendation -- confounded with trigger level and
       hence with truncation? A and B share a trigger level, which is the
       comparison that matters most; does that rescue it, or does the differing
       pulse shape still cause differing truncation within that pair?
   (iii) Is our reported delta-v usable at all, and does the truncation bias the
       450-800 Hz energy-fraction estimate (a 20 ms window at 550 Hz is only
       ~11 cycles, and the window starts on a discontinuity)?

C. ATTACK THE 550 Hz "STRUCTURAL MODE". A tri-axial accelerometer is wax-seated
   on a printed key-seat at the top vertex of a small, light, compliant lattice.
   Is a 519-549 Hz resonance more plausibly (a) the specimen's first structural
   mode, or (b) the sensor-plus-mount resonance of an added mass on a compliant
   tip, or (c) a rigid-body mode of the specimen rocking on the plate? We do not
   have the sensor mass or the specimen mass recorded anywhere. If it is (b) or
   (c), then BOTH criterion (2) (the f*tau bound) and criterion (3) (the
   450-800 Hz band fraction) are anchored on an artifact and the recommendation
   loses two of its four legs. What measurement would settle this cheaply (tap
   test, sensor-off ringdown, mass-loading check, added-mass perturbation,
   comparing per-axis vs resultant)? Can you test any of it in the attached data
   -- e.g. does the 519-549 Hz feature shift between arrangements, appear on
   CH5 as well as the vertex, or scale with input severity in a way that
   discriminates structure from mount?

D. ATTACK THE SHOCK-REGIME CRITERION. Is our f*tau <= 1.5 statement a correct
   reading of the half-sine shock response spectrum? Our understanding is that
   maximax amplification for a half-sine peaks near f*tau ~ 0.8 (~1.7x), falls
   below 1 for f*tau << 1, and tends to 1 only for f*tau >> 1 -- if so, C and D
   at f*tau ~ 1.85 are not "quasi-static" at all and the criterion as written is
   not justified. Give the correct SRS-based criterion for choosing a pulse
   duration when the goal is MAXIMUM SENSITIVITY OF THE RESPONSE TO STRUCTURAL
   DIFFERENCES (not maximum response), including whether we should be targeting
   the knee of the SRS, and how damping and the non-half-sine actual pulse shape
   change the answer.

E. ATTACK THE SELECTION LOGIC ITSELF -- this is our biggest worry. We selected
   an arrangement by MINIMUM VARIANCE of T with n = 1 specimen. But the
   quantity that matters is DISCRIMINATION: between-geometry signal divided by
   within-specimen noise. Selecting on variance alone can systematically favour
   the arrangement that is least sensitive to the specimen (a stack so soft the
   vertex simply follows the base gives T -> 1 with tiny variance and zero
   information). Note B's T is 0.996 and 0.990 in the two bands -- the closest
   to unity of the four. Is our procedure vulnerable to exactly this failure?
   Is there ANYTHING in a single-specimen dataset that bounds sensitivity
   (e.g. response nonlinearity across the raw-severity range within a block,
   coherence between input and output, modal content, signal-to-noise in the
   structural band)? Propose a defensible selection statistic and, if the data
   cannot support one, say plainly that the recommendation is unsupported and
   specify the minimal experiment that would settle it. For scale: repeat drops
   of one article give T CV ~0.3-1 %, but print-to-print scatter across five
   nominally identical prints of the same geometry gives T CV 0.72 % and a
   1.95 % spread, while the largest between-geometry spread ever measured on
   this rig was ~24 % (four geometries, an earlier configuration) and a recent
   three-specimen ranking spanned only 2.3 %.

F. ATTACK THE STATISTICS. Our pairwise Welch tests treat the 10 drops in a
   block as independent replicates (p values down to 4.5e-11). But the blocks
   are sequential, unrandomised, separated in time, and at least arrangement A
   has a strong within-block trend (+4.6 %/drop in raw CH5). Quantify the
   autocorrelation / effective sample size, redo the comparisons correctly
   (e.g. block-level inference, trend-adjusted models, or treating arrangement
   as the unit with n = 1 block), and tell us which of the reported differences
   -- particularly the A-vs-B T(CFC-1000) CV gap that decided the
   recommendation -- survive. Is a variance-ratio comparison (F test / Levene)
   on 10 correlated, trending observations per arrangement even admissible?

G. ATTACK THE BAND-ENERGY CRITERION. We compare the FRACTION of output energy
   in 450-800 Hz. A produces far more total energy (harder hit, large contact
   spike), so a fraction penalises it by construction. Should we be comparing
   absolute band energy, band energy normalised by INPUT band energy (a
   band-limited transfer estimate), or coherence? Does the ordering
   (B 22.5 % > A 16.6 % > D 13.0 % > C 10.8 %) reverse under any defensible
   normalisation? If it does, criterion (3) collapses too.

H. ATTACK THE OBJECTIVE ITSELF. T is a ratio of peak magnitudes of two
   different quantities (single-axis base vs tri-axis resultant at a different
   point), possibly peaking at different instants and frequencies, on a sensor
   whose own mass may load the structure, in a record that truncates the
   ringdown. Is that a well-posed objective for Bayesian optimisation of impact
   energy absorption at all? Rank the alternatives for THIS rig, given a 20 ms
   window (which we can extend) and this sensor pair: true FRF / band-limited
   transmissibility, SRS ratio, transmitted impulse or delta-v ratio, energy
   dissipated per cycle, damping ratio extracted from ringdown, or output peak
   at fixed input. Say which requires hardware or capture changes and which is
   available from data we already take. Also: is the near-unity T we see on
   every specimen ever measured (0.94-1.22 across ~1400 drops) evidence that
   the metric is largely a rigid-body pulse-transmission ratio rather than a
   structural one, as we suspect, given CFC-180 is 3 dB down at 300 Hz and
   attenuates 550 Hz roughly 12x?

I. ATTACK THE SIDE INFERENCES. (i) We concluded that an earlier 5-drop PU run
   with bimodal input was the two sheets seating inconsistently, purely because
   those drops fall near this sweep's arrangements in (input peak, pulse width)
   space. Is that identifiable, or do other mechanisms (specimen re-seating,
   plate tilt, drop-height variation, partial contact area) produce the same
   2-D signature? (ii) We treat "C vs D is a null (p = 0.47)" as evidence that
   stacking order does not matter. What power does that test actually have?

J. VERDICT. State, in order: which of our numbers you could not reproduce;
   which of the four grounds for choosing B survive your scrutiny; whether the
   correct answer is B, A, C/D, "none of these -- the sweep cannot decide", or
   "the question is malformed"; and the single cheapest experiment that would
   most reduce our risk of optimising against a bad objective. Anchor
   recommendations in drop-tower / shock-testing practice where relevant
   (SAE J211, ISO 5347 and ISO 16063 mounting, ASTM D3332 / D7136, MIL-STD-810
   method 516 SRS practice, IEST shock practice) and say where standard
   practice contradicts what we did.

Attached: 40 raw CSVs (bpx68c_Signal1..41, Signal21 excluded; columns are
Time (sec), CH2, CH3, CH4, CH5 in G), the TP4 series table
(bpx68c_series_table.csv, the instrument's own peak/duration/delta-v per event),
the dataset README, our analysis markdown, our metrics JSON, our analysis
script, and our figures.

Output a single self-contained markdown report we can commit under
edison-trajectories/pu-configs/. Lead with the conclusions that CHANGE our
decision.
"""


def main() -> int:
    # ---- assemble the upload bundle -------------------------------------
    bundle = OUT / "bundle"
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)

    raw = REPO / "data" / "drop-tests" / "pu-configs" / "raw"
    # The raw captures are committed as one zip per arrangement; flatten them.
    for zpath in sorted(raw.glob("*.zip")):
        with zipfile.ZipFile(zpath) as zf:
            for member in zf.namelist():
                if not member.lower().endswith(".csv"):
                    continue
                name = Path(member).name
                if name.lower().startswith("__"):
                    continue
                with zf.open(member) as src, (bundle / name).open("wb") as dst:
                    shutil.copyfileobj(src, dst)
    series = raw / "bpx68c_series_table.csv"
    if series.exists():
        shutil.copy2(series, bundle / series.name)

    shutil.copy2(
        REPO / "data" / "drop-tests" / "pu-configs" / "README.md",
        bundle / "data-README.md",
    )
    for doc in (
        "drop-test-pu-configs-analysis.md",
        "drop-test-pu-vs-felt-analysis.md",
        "drop-test-absorber-alternatives.md",
    ):
        p = REPO / "docs" / doc
        if p.exists():
            shutil.copy2(p, bundle / doc)
    script = REPO / "scripts" / "analysis" / "drop_test_pu_configs_analysis.py"
    if script.exists():
        shutil.copy2(script, bundle / script.name)
    figs = REPO / "data" / "drop-tests" / "pu-configs" / "figures"
    for f in sorted(figs.glob("*.png")):
        shutil.copy2(f, bundle / f.name)
    metrics = figs / "pu_configs_metrics.json"
    if metrics.exists():
        shutil.copy2(metrics, bundle / metrics.name)

    n_csv = len(list(bundle.glob("*.csv")))
    print(f"bundle: {n_csv} csv + {len(list(bundle.glob('*.md')))} md")

    if SUBMITTED.exists():
        task_id = json.loads(SUBMITTED.read_text())["task_id"]
        print("reusing task_id:", task_id)
        return 0

    # Edison ANALYSIS requires directory uploads as a single zipped collection.
    resp = client.store_file_content(
        name="pu-configs-arrangement-sweep",
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
