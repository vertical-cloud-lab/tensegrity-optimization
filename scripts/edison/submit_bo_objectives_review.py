"""Submit an Edison Scientific ANALYSIS task that ADVERSARIALLY REVIEWS the
BO objective choice for the T-3_01 prism campaign (bo/t3_prism_bo_campaign.py).

Driven by sgbaird PR #102 comment 5365684075:
> verify this with Edison scientific. Socratic method or something? Whatever
> you did before where you didn't just ask it to confirm or deny

"This" is the claim block in the Honegumi campaign hand-off comment:
minimize t180 and minimize e_rebound per the campaign analysis doc and the
PR #97 energy-absorption framing; the trade-off is genuine in the 8-specimen
data (best attenuator 6lhxfy hops hardest, e_rebound 0.050) so the Pareto
front is informative; noise is passed as per-drop SEM with the ~2 percent
print-to-print floor noted but not modeled.

The precedent is Edison task d9092c5a (PR #86, commits b43fb02/b6a296e): give
Edison the underlying data and ask it to attack and independently re-derive,
never to confirm or deny. That review overturned the PU arrangement B
recommendation, which is why the same structure is used again here. On top of
the adversarial sections this one opens Socratically: Edison is asked to
derive its own objective set from the numeric files alone, and commit to it
in writing, BEFORE engaging with the sections that reveal what we chose.

Bundle inputs live on three branches, so this script fetches them by ref
instead of assuming a checkout:

- this branch (claude/issue-98-20260821-0103): the BO script, its ingest CSV,
  suggestions, design table, print key
- copilot/add-drop-test-protocol-again: campaign analysis doc + script,
  per-drop campaign_metrics.json, partial-session metrics, params.json,
  dataset README, 10 per-session TP4 series tables, print-defect floor study
- claude/issue-94-20260806-2349: the PR #97 energy-absorption review

Idempotent: records the task id in bo-objectives-SUBMITTED.json and reuses it.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "bo-objectives"
OUT.mkdir(parents=True, exist_ok=True)
SUBMITTED = OUT / "bo-objectives-SUBMITTED.json"

COPILOT_REF = "origin/copilot/add-drop-test-protocol-again"
PR97_REF = "origin/claude/issue-94-20260806-2349"

api_key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
if not api_key:
    raise SystemExit("EDISON_API_KEY (or EDISON_PLATFORM_API_KEY) not set")
client = EdisonClient(api_key=api_key.strip())

PROMPT = r"""
ADVERSARIAL REVIEW REQUEST, with a Socratic opening. Please try to BREAK the
objective-function choice below, not to confirm it. We are about to print a
second batch of nine 3D-printed tensegrity specimens whose designs were
suggested by a Bayesian-optimization model built on this choice; we would
rather learn now that the objectives or the noise model are wrong than after
another 900 drops. Where you agree, say so briefly; spend your effort on what
is wrong, unsupported, ill-posed, or confounded.

IMPORTANT ORDERING INSTRUCTION (this is the Socratic part): Section A below
asks you to derive your own answer FROM THE NUMERIC DATA FILES ONLY (the
CSVs and the two metrics JSONs) plus the rig description in this prompt,
and to commit to it in writing, BEFORE you read our analysis markdown files
or the later sections of this prompt. Our own reasoning documents are in the
attached bundle and you will need them for sections B onward, but your
section-A answer must be recorded first and must not be revised afterwards:
if your view changes after reading our documents, record the change as an
explicit diff ("after reading, I would change X because Y"), so we can see
what the data alone supports versus what our framing talked you into.

=== CONTEXT: THE RIG AND THE CAMPAIGN ===

We drop-test small 3D-printed tensegrity unit cells ("T3 prism", ~50-100 mm
tall, 18-22 g printed, PLA struts + TPU 85A tendons) as impact attenuators.
A carriage drops 60 in onto a 1/2 in polyurethane mat. Instrumentation
(Vishay/PCB TP4): CH5, single-axis accelerometer on the bottom acrylic plate
(the INPUT, 150 G trigger); CH2/CH3/CH4, tri-axis accelerometer wax-seated in
a printed key-seat at the specimen's TOP vertex (the OUTPUT). Captures are
1.25 MHz, 100 ms records, 2 ms pre-trigger. SAE J211 phaseless Butterworth
filtering; CFC-180 is the primary band.

Round 1 of a Bayesian-optimization campaign is done: 9 designs from a scrambled
Sobol batch over 5 geometric parameters (base radius R 25-40 mm, height H
60-110 mm, twist 40-80 deg, strut diameter 6-12 mm, cable diameter 3-5.5 mm),
all projected to constant solid-CAD mass, printed once each (n = 1 article per
design), plus one off-Sobol reference design. 8 specimens tested so far, 101
drops each, first 2 drops discarded as warm-up.

Per-drop metrics available in the bundle (campaign_metrics.json has every
drop; campaign_summary.csv aka t3-prism-bo-batch-drop-results.csv has
per-specimen mean and sd; the 10 series-table CSVs are the TP4 instrument's
own independent per-event peak/duration/delta-v):

  t180        peak(CFC-180 top resultant) / peak(CFC-180 base input), per drop
  t1000       same at CFC-1000
  out_180_g   filtered output peak, G      in_180_g   filtered input peak, G
  in_dv_ms    input delta-v, m/s (full-pulse integral)
  t_second_ms time from the main impact to a second impact event, ms
  e_rebound   g * t_second / (2 * delta_v), dimensionless
  fn_hz, zeta_pct  ringdown fit of the top-vertex decay (usable on only
              5 of 8 specimens; treat as opportunistic)

Known replication scales, measured on this rig in earlier studies (documents
in the bundle): repeat drops of one article within a session give T CV
0.2-0.5 percent; re-mounting the same article across sessions moves T up to
~2 percent (measured twice in this campaign: 0.13 and 0.58 percent); printing
the same geometry again moves T by ~2 percent (five nominally identical
prints, print-defect study attached). The largest design-to-design spread in
this campaign is 16.8 percent in t180 and 2.5x in e_rebound.

One tested specimen (amdjwm, the second-best t180 at 0.980) cannot be mapped
to any design and its parameters are unknown; it is excluded from the BO
training set. Its t_second/e_rebound values are also flagged unreliable in
this session.

=== A. SOCRATIC OPENING: DERIVE, DO NOT REVIEW (numeric files + this context
       only; do this before reading our markdown documents) ===

The engineering goal: find the design that best protects a payload from a
single impact of this severity. The BO loop prints 9 new designs per round.

 A1. From the per-drop data, which measured quantity or quantities would YOU
     optimize? One objective or several? For each candidate in the list
     above (and any derived quantity you would construct from them), say
     whether it is (a) a valid objective, (b) a constraint or diagnostic,
     or (c) unusable, and why. Consider at least: ratio vs absolute output
     peak given the input varies (in_180_g spans 202-236 G across specimens);
     what e_rebound = g*t_second/(2*dv) physically is (note: is it an energy
     ratio, a velocity ratio, or something else? does its label matter?);
     and whether t180 and e_rebound are independent enough pieces of physics
     to justify a Pareto treatment, or two projections of one underlying
     compliance axis.
 A2. From the 8 specimens' data, is a MULTI-objective (Pareto) formulation
     warranted, or does one objective dominate/subsume the other? Quantify:
     what is the correlation structure between the candidate objectives
     across specimens and how sensitive is it to any single specimen?
 A3. What noise magnitude would you attach to each per-design observation
     handed to a Gaussian-process-based optimizer, given the three
     replication scales above and n = 1 article per design? Give a number
     or a formula, and justify the replication unit you chose.
 A4. Record your committed answers to A1-A3 in a clearly-marked block.

=== WHAT WE ACTUALLY DID (read only after committing section A) ===

Our BO script (bundle: t3_prism_bo_campaign.py) runs Ax/BoTorch SAASBO with
qNEHVI, two objectives, both MINIMIZED: t180 and e_rebound. Noise per design
is passed as the per-drop SEM: sd of the ~99 valid drops divided by sqrt(99),
i.e. ~0.0004 on t180 (~0.04 percent of the value) and ~1e-4 on e_rebound. The
~2 percent print-to-print floor is acknowledged in a comment and NOT modeled.
7 completed observations were attached (6 mapped Sobol designs + the
reference design), amdjwm was skipped, and the 3 printed-but-untested designs
were attached as pending so the acquisition avoids them. The resulting round-2
suggestions put 8 of 9 designs at the 12 mm strut-diameter bound and 7 of 9 at
the 60 mm height bound.

The claim under review, verbatim from our hand-off comment:

  "Objectives: minimize t180 and minimize e_rebound, per the BO hand-off
  section of the campaign analysis doc and the #97 energy-absorption framing.
  The multi-objective assumption holds in the data: they genuinely trade off
  (best attenuator 6lhxfy hops hardest at e_rebound 0.050), so the Pareto
  front is informative. Noise is passed as per-drop SEM; the ~2 percent
  print-to-print floor (n = 1 article per design) is noted but not modeled."

=== B. ATTACK e_rebound AS AN OBJECTIVE ===

 B1. Dimensional and physical audit of e_rebound = g*t_second/(2*delta_v).
     Derive what this quantity actually is for a ballistic hop. Is calling
     it "rebound ENERGY ratio" correct? If it is really a velocity ratio,
     does the mislabeling change the optimizer's behavior (monotone
     transforms preserve a Pareto set), the noise model (SEM of v vs v^2),
     or only the physical interpretation and thresholds?
 B2. WHAT is hopping, and whose energy is it? t_second is the delay to a
     second impact event. Establish from the data (series tables, per-drop
     records) whether the second event is the specimen leaving the plate and
     landing again, the carriage bouncing on the mat, or something else,
     and whether that distinction survives across specimens. If the hop is
     substantially the carriage/mat restitution rather than the specimen's,
     minimizing it optimizes the fixture, not the design.
 B3. Direction-of-goodness. For a payload-protection objective, argue both
     sides: (i) rebound energy returned to the payload is injury/damage
     energy, minimize it; (ii) a specimen that stores impact energy
     elastically and returns it as a hop has diverted it from the
     transmitted-peak path, which is exactly what the best attenuator did,
     so penalizing the hop double-counts against the mechanism that works.
     Which is right FOR THIS RIG, where the "payload" surrogate is the
     top-vertex accelerometer and the specimen itself hops?
 B4. amdjwm's e_rebound is flagged unreliable because its t_second detection
     was unstable (sd 15.7 ms vs <1 ms for others). How fragile is the
     t_second detector generally, and does e_rebound remain a usable
     objective for designs whose second impact is soft or split?

=== C. ATTACK THE TRADE-OFF / PARETO CLAIM ===

 C1. With 8 specimens (7 in the training set), quantify the association
     between t180 and e_rebound and its dependence on single points. Redo it
     without 6lhxfy, without bag26v, and rank-based. Does "they genuinely
     trade off" survive?
 C2. Even if anti-correlated across THESE 8 designs, is that a trade-off in
     the decision-relevant sense (a Pareto FRONT of mutually non-dominated
     optima), or a 1-D physical coupling (softer tendon path -> lower
     transmitted peak AND bigger hop) along which one direction is simply
     better? What would each hypothesis predict for the round-2 batch, and
     what in the existing data discriminates them?
 C3. If the trade-off is not supported: what does the qNEHVI acquisition do
     when handed two near-deterministic, strongly-coupled objectives, and
     does that explain the suggested batch collapsing onto the strut/height
     bounds (8 of 9 at strut 12 mm, 7 of 9 at H 60 mm)?

=== D. ATTACK THE NOISE MODEL. This is our biggest worry. ===

 D1. The observation handed to the GP for a design is one printed article's
     101-drop mean with SEM ~0.04 percent, but the design-level replication
     floor (print-to-print) is ~2 percent, i.e. the stated noise understates
     the decision-relevant noise by roughly 50x. Work through what this does
     to a SAASBO fit on 7 points in 5-D and to qNEHVI: interpolation of
     print-lottery noise as signal, overconfident Pareto membership,
     boundary-seeking suggestions? Connect to the actual round-2 batch.
 D2. Is the ~2 percent floor itself well-founded? Audit the attached
     print-defect study (5 nominally identical prints): is 2 percent a sd,
     a spread, a CV; on which metric; does it transfer to e_rebound (what is
     the print-to-print floor for e_rebound, and can the bundle's two
     double-session specimens bound the re-mount contribution)?
 D3. Give the correct noise treatment for round 2 concretely: e.g. pass
     SEM combined in quadrature with a design-level floor per objective
     (state the numbers you would use), or let the GP infer noise instead
     of fixing it, or model article and session as hierarchy. Which is
     defensible in the Ax Service API with fewer than 10 points, and what
     do you predict changes in the suggestions when the fix is applied?
 D4. n = 1 article per design and 101 drops per article: given the three
     replication scales, was that the right allocation, and what allocation
     (articles x drops) should round 2 use for the same total effort?

=== E. ATTACK t180 ITSELF, IN LIGHT OF NEW EVIDENCE ===

An earlier adversarial review on this rig (of a mat-arrangement sweep, 20 ms
truncated records, different mat states) concluded near-unity T was likely a
rigid-body pulse-transmission ratio and questioned peak-ratio T as a BO
objective. Since then: records are 100 ms with 2 ms pre-trigger and a
validated tail re-baseline, and this campaign measured t180 0.893-1.062 with
within-specimen CV 0.2-0.5 percent and clean cross-session transfer (0.13 and
0.58 percent), while t1000 does NOT transfer across sessions.

 E1. Does the 16.8 percent design spread with sub-percent repeatability
     settle the earlier objection that T does not see the structure, or can
     a mount/seating artifact still produce a specimen-STABLE, design-
     correlated t180? What in the bundle discriminates?
 E2. Peak-ratio vs alternatives now practically available in these 100 ms
     records (SRS ratio at the payload band, band-limited transmissibility,
     transmitted impulse ratio, output peak at measured input): would any
     change the RANKING of these 8 specimens? If the ranking is invariant,
     say so; that is a defense of t180 we would like tested, not assumed.

=== F. WHAT IS MISSING ===

 F1. Should anything measured but unused enter the formulation: absolute
     out_180_g as the objective with in_180_g as context/covariate; t1000 as
     a constraint (broadband amplifiers autv5r/nvxsrv hit 1.23-1.24); mass
     or printed-mass-normalized metrics, given constant solid mass produced
     an 18.5-22 g printed spread; fn/zeta where usable?
 F2. Excluding amdjwm (2nd-best t180) from training because its parameters
     are unknown: any way to use it (e.g. as an outcome-only observation,
     or measuring its geometry post hoc), and how much information is lost?

=== G. VERDICT ===

State, in order: (1) your section-A committed answer and whether reading our
documents changed it; (2) which of the three legs of the quoted claim survive
(objective pair; genuine trade-off/Pareto informativeness; per-drop-SEM noise
model); (3) the corrected formulation you would run for round 2, concretely
(objectives with directions, constraints, noise numbers, any re-allocation of
articles vs drops); (4) whether the committed round-2 suggestions should be
printed as-is, re-generated after fixes, or gated on a cheap intermediate
experiment, and if the latter, which experiment. Anchor in standard practice
where relevant (SAE J211 for filtering, shock-isolation practice for
transmissibility and SRS, coefficient-of-restitution practice for rebound
measurement, and the BO literature on noise handling: SAASBO, qNEHVI,
heteroskedastic/hierarchical noise).

Attached bundle: campaign_summary CSV (= t3-prism-bo-batch-drop-results.csv),
campaign_metrics.json (per-drop rows, 8 specimens), partial_sessions_
metrics.json (the two interrupted-session re-runs), 10 TP4 series-table CSVs
(instrument-independent per-event peaks/durations/delta-v), params.json and
dataset README, our campaign analysis doc and analysis script, the print-
defect study, the PR #97 energy-absorption review, the BO script, its round-2
suggestions CSV, the Sobol design table, and the print key.

Output a single self-contained markdown report we can commit under
edison-trajectories/bo-objectives/. Lead with the conclusions that CHANGE
what we print next.
"""


def git_show(ref: str, path: str, dest: Path) -> None:
    blob = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=REPO,
        check=True,
        capture_output=True,
    ).stdout
    dest.write_bytes(blob)


def main() -> int:
    # ---- assemble the upload bundle -------------------------------------
    bundle = OUT / "bundle"
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)

    # make sure the two source branches are fetchable
    for ref in (COPILOT_REF, PR97_REF):
        branch = ref.split("/", 1)[1]
        subprocess.run(
            ["git", "fetch", "--filter=blob:none", "origin", branch],
            cwd=REPO,
            check=True,
            capture_output=True,
        )

    # this branch: the BO side
    for name in (
        "t3_prism_bo_campaign.py",
        "t3-prism-bo-batch-drop-results.csv",
        "t3-prism-bo-suggestions-round1.csv",
        "t3-prism-bo-batch.csv",
        "t3-prism-bo-batch-print-key.csv",
    ):
        shutil.copy2(REPO / "bo" / name, bundle / name)

    # copilot branch: the campaign analysis side
    base = "data/drop-tests/sobol-campaign"
    for path, dest in (
        ("docs/drop-test-sobol-campaign-analysis.md", "drop-test-sobol-campaign-analysis.md"),
        ("scripts/analysis/drop_test_campaign_analysis.py", "drop_test_campaign_analysis.py"),
        ("docs/drop-test-print-defects-analysis.md", "drop-test-print-defects-analysis.md"),
        (f"{base}/figures/campaign_metrics.json", "campaign_metrics.json"),
        (f"{base}/figures/partial_sessions_metrics.json", "partial_sessions_metrics.json"),
        (f"{base}/params.json", "params.json"),
        (f"{base}/README.md", "sobol-campaign-data-README.md"),
    ):
        git_show(COPILOT_REF, path, bundle / dest)

    # the per-session TP4 series tables (instrument's own per-event numbers)
    listing = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", COPILOT_REF, f"{base}/raw"],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    for path in listing:
        if not path.endswith("series-table.csv"):
            continue
        session = Path(path).parent.name.replace(" ", "_")
        git_show(COPILOT_REF, path, bundle / f"series-table_{session}.csv")

    # PR #97 branch: the energy-absorption review
    git_show(
        PR97_REF,
        "docs/drop-tower-energy-absorption-review.md",
        bundle / "drop-tower-energy-absorption-review.md",
    )

    n = len(list(bundle.iterdir()))
    print(f"bundle: {n} files")

    if SUBMITTED.exists():
        task_id = json.loads(SUBMITTED.read_text())["task_id"]
        print("reusing task_id:", task_id)
        return 0

    # Edison ANALYSIS requires directory uploads as a single zipped collection.
    resp = client.store_file_content(
        name="t3-bo-objectives-review",
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
