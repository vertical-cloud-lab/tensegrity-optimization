"""Submit an Edison Scientific ANALYSIS task for feedback on the MEASURED
round-2 results of the T-3_01 prism BO campaign (PR #102 comment 5402810247).

Driven by sgbaird PR #102 comment (2026-08-25):
> send these results to Edison for feedback

"These results" = the full round-2 drop campaign (all nine r2d2c articles,
172 stabilized drops), the predicted-vs-measured comparison against the
frozen 7a048ee model predictions, the SAASBO refit on all 18 tested
articles, and the suggested round-3 batch.

This is a follow-up to Edison task 3e398131 (adversarial objectives review,
submitted 8/21, fetched 8/25). That review said "do not print the round-2
suggestions as-is; drop e_rebound; use article-level noise." The batch was
printed anyway under time pressure, and the measured outcomes now exist, so
this task asks Edison to (a) audit the calibration of the frozen
predictions, (b) test its own earlier recommendations against the new data,
(c) attack the claims we plan to present, and (d) rule on the round-3 batch
before anything else is printed. The prior review is included in the bundle
so Edison can hold itself to its own committed positions.

File-naming note: repo files named `t3-prism-bo-round1-*` describe the BO's
first suggested batch, which is the SECOND physical round (print IDs
r2d2c1..c9). The bundle renames everything to sobol-round1-* / round2-* /
round3-* so the reviewer cannot trip on that.

Idempotent: records the task id in round2-results-SUBMITTED.json and reuses it.
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "round2-results"
OUT.mkdir(parents=True, exist_ok=True)
SUBMITTED = OUT / "round2-results-SUBMITTED.json"

api_key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
if not api_key:
    raise SystemExit("EDISON_API_KEY (or EDISON_PLATFORM_API_KEY) not set")
client = EdisonClient(api_key=api_key.strip())

# bundle-name -> repo path (bundle names disambiguate the round-numbering clash)
BUNDLE_FILES = {
    # physical round 1: the Sobol batch (9 designs + reference, tested 8/19-8/21)
    "sobol-round1-drop-results.csv": "bo/t3-prism-bo-batch-drop-results.csv",
    "sobol-round1-per-drop-metrics.csv": "bo/t3-prism-per-drop-metrics.csv",
    "sobol-round1-design-table.csv": "bo/t3-prism-bo-batch.csv",
    "sobol-round1-print-key.csv": "bo/t3-prism-bo-batch-print-key.csv",
    # physical round 2: the BO-suggested batch (r2d2c1..c9, tested 8/24)
    "round2-measured-drop-results.csv": "bo/t3-prism-bo-round1-drop-results.csv",
    "round2-per-drop-metrics.csv": "bo/t3-prism-bo-round1-per-drop-metrics.csv",
    "round2-as-printed-designs.csv": "bo/t3-prism-bo-round1-designs.csv",
    "round2-frozen-predictions.csv": "bo/t3-prism-bo-round1-predictions.csv",
    "round2-print-key.csv": "bo/t3-prism-bo-round1-print-key.csv",
    # proposed round 3 (refit on all 18 articles; NOT yet printed)
    "round3-suggested-batch.csv": "bo/t3-prism-bo-suggestions-round2.csv",
    # cross-cutting analysis artifacts
    "objectives-mass-normalized.csv": "bo/t3-prism-bo-objectives-mass-normalized.csv",
    "loocv-round1-fit.csv": "bo/t3-prism-bo-round1-loocv.csv",
    "loocv-round1-fit-diagnostics.json": "bo/t3-prism-bo-round1-loocv-diagnostics.json",
    "drop-count-sensitivity.csv": "bo/t3-prism-drop-count-sensitivity.csv",
    # code
    "t3_prism_bo_campaign.py": "bo/t3_prism_bo_campaign.py",
    "t3_prism_mass_model.py": "bo/t3_prism_mass_model.py",
    "bo-README.md": "bo/README.md",
    # Edison's own prior review of this campaign's objectives
    "prior-edison-adversarial-objective-review.md": (
        "edison-trajectories/bo-objectives/adversarial-objective-review.md"
    ),
}

PROMPT = r"""
FOLLOW-UP REVIEW REQUEST: measured outcomes are in for the batch your prior
review told us not to print.

You (Edison) previously produced the attached
prior-edison-adversarial-objective-review.md for this exact campaign
(2026-08-21). Its decision: do not print the nine round-2 suggestions as-is;
drop e_rebound as an objective; replace per-drop SEM with article-level noise
(~0.72 percent CV floor); reallocate to 3 articles x 10-12 drops. For
schedule reasons the batch was printed and tested anyway (one article per
design, short sessions). All nine articles have now been measured, so your
predictions about what the mis-specified model would do are testable. We are
asking for feedback on these RESULTS, not a re-litigation of the setup: what
do the measured outcomes actually establish, which of our conclusions
survive, and what exactly should round 3 be? A project presentation is on
2026-08-25, so lead with what changes what we present and print next.

Where you agree, say so briefly; spend your effort on what is wrong,
unsupported, or confounded. Recompute from the numeric files rather than
trusting our summaries; flag any claim of ours you cannot reproduce.

=== WHAT HAPPENED SINCE YOUR REVIEW (timeline, for orientation) ===

- Your review was submitted 8/21 but only retrieved 8/25 (our fault); the
  round-2 plate was printed 8/22-8/24 from the FROZEN model predictions in
  round2-frozen-predictions.csv (SAASBO/qNEHVI, objectives min t180 and min
  e_reb_mJ = e_rebound * m_printed * g * h, per-drop-SEM noise, the exact
  formulation you reviewed).
- The nine articles (print IDs r2d2c1..c9, mapping and masses in
  round2-print-key.csv, as-printed geometry in round2-as-printed-designs.csv)
  were drop-tested 8/24: ~21 captures each, first 2 discarded, so ~19
  stabilized drops vs ~99 in round 1. Same rig, same pipeline, input dv
  5.29-5.41 m/s, zero invalid captures.
- Round 1 also gained its 9th specimen (ajhby6) since your review; the
  round-1 files here supersede the ones you saw. amdjwm remains unmapped and
  excluded.
- A 6-D refit on all 18 tested articles (printed mass added as a parameter,
  fit_out_of_design, generation space pinned at 20.23 g printed) produced the
  round3-suggested-batch.csv. NOTHING from round 3 has been printed.

Geometry caveat: round-2 articles were re-projected to constant solid mass,
which scaled them 20-30 percent smaller in every dimension than the
coordinates the model was trained on for round 1. The five "base"
coordinates fix shape, not size.

=== A. CALIBRATION AUDIT (do this from the numbers, before reading our
       interpretation in bo-README.md) ===

Join round2-frozen-predictions.csv (pred mean and sd per trial; sd is the
model posterior sd of the noise-free mean) to round2-measured-drop-results.csv
via round2-print-key.csv.

 A1. Compute standardized residuals for t180 and e_reb_mJ (measured minus
     predicted over predicted sd) for all nine articles, plus whatever
     calibration diagnostics you consider standard for a 9-point batch from
     a GP (coverage of nominal intervals, sign test, mean bias).
 A2. Our reading: every t180 landed at or ABOVE prediction (+0.04 to +0.42,
     up to ~5.8 sd), while 8 of 9 e_reb_mJ landed at or BELOW prediction,
     within its (huge) bands. Verify or correct. Is this the signature of
     (i) the noise mis-specification you predicted (interpolating print-
     lottery as signal -> overconfident, optimistic extrapolation), (ii) the
     20-30 percent re-projection shrink making articles systematically
     stiffer than the round-1 training data implied (a covariate-shift bias
     your review did not consider), (iii) both, or (iv) something else?
     What in the data discriminates? Note the two failure modes have
     different round-3 remedies (fix noise vs fix the training
     representation), so this attribution is the single most decision-
     relevant question in this review.
 A3. Your review predicted the mis-specified model's batch would be
     overconfident and boundary-collapsed. Score your own predictions
     against the outcome honestly, including anything the data now REFUTES
     in your prior review. Self-consistency is not the goal; we want to know
     where the 8/21 analysis was wrong, not just where it was right.

=== B. THE e_rebound QUESTION, REVISITED WITH NEW DATA ===

Your review demoted e_rebound to a diagnostic (unvalidated event identity,
velocity not energy, fragile detector). The new data complicates that:

 B1. In round 2 the rebound channel showed clean design-to-design structure
     (4.07 to 12.17 mJ, tight per-drop sd, stable detectors, no amdjwm-like
     failures) and it is the axis on which the batch delivered its only
     unambiguous improvements (r2d2c6 at 4.07 mJ vs prior floor 6.2). Does
     a channel this well-behaved and this design-discriminating stay a
     "diagnostic only", or does the new evidence move it to a valid
     objective or constraint? Be specific about what it would take, and
     whether the round-2 data itself supplies any of the validation your
     review said was missing (e.g. detector stability across nine new
     geometries).
 B2. The t180-vs-e_rebound trade-off you called leverage-fragile at n=7:
     recompute the correlation structure at n=18. Does a genuine Pareto
     front exist now, or is the "front" of {6lhxfy, r2d2c7, r2d2c1, r2d2c2,
     r2d2c6} still a 1-D compliance axis plus noise? Note r2d2c2 carries a
     T-drift flag (see D2) and sits on the front.
 B3. objectives-mass-normalized.csv holds both the absolute (mJ) and
     per-gram framings. We claim the front membership of {6lhxfy, r2d2c7,
     r2d2c1, r2d2c6} is robust to the choice. Verify, and say which framing
     you would present.

=== C. ATTACK THE CLAIMS WE PLAN TO PRESENT ON 8/25 ===

For each, state: survives / survives with a required caveat (give the
caveat verbatim) / does not survive.

 C1. "The batch genuinely improved the Pareto front: four of the five front
     points are round-2 articles; r2d2c1 strictly dominates the previous
     low-rebound anchor bpx68c; r2d2c6 cuts the low-rebound end from 6.2 to
     4.1 mJ." Consider measurement noise on front membership (19-drop
     sessions), the T-drift flag on r2d2c2, and whether "improved front on
     an objective your own review calls unvalidated" needs saying.
 C2. "The model was systematically optimistic on t180; plausible physics:
     re-projected articles print 20-30 percent smaller and stiffer, and the
     same stiffness that raises t180 lowers restitution." Is that physics
     story consistent with the per-drop data and the as-printed geometry,
     or is it a just-so story pasted over the noise mis-specification?
 C3. "The uncertainty bands did their job: measured rebound landed inside
     the (wide) predicted bands." Given A1's coverage numbers, is that a
     fair statement for a slide, or selective (right objective, wrong
     objective)?
 C4. Anything we are NOT claiming that the data does support and a
     presentation should say (e.g. about replication, about what one round
     of BO on n=1 articles can and cannot conclude).

=== D. DATA-QUALITY RULINGS NEEDED BEFORE ROUND 3 ===

 D1. r2d2c3 measured t180 = 1.334 (worst ever, 5.8 sd above prediction) with
     t1000/t180 = 1.86 against 1.00-1.20 for every other article ever
     tested. Two live hypotheses: a genuinely rigid design (thick struts +
     thick cables on the shortest prism), or an accelerometer seating/mount
     artifact (the lab asked exactly this on 8/24). From the committed
     per-drop metrics (stability, drift, the t1000 signature), which is
     better supported, can they be discriminated without re-testing, and if
     not, what is the minimal re-test? Should r2d2c3 enter the round-3
     training set as-is, deweighted, or held out pending re-test?
 D2. r2d2c2 is T-drift flagged (+0.25 percent/drop, +3.5 percent end to
     end, output-side). It sits on the claimed front. Ingest as-is with
     inflated sd, re-test, or exclude?
 D3. Short sessions: ~19 stabilized drops vs ~99. drop-count-sensitivity.csv
     replays round 1 truncated. Is the SEM-based downweighting adequate
     for mixed-length sessions, and should round-1 observations be
     re-windowed to the first ~19 drops for comparability (the drift data
     says a session mean is window-dependent)?

=== E. RULE ON THE ROUND-3 BATCH (round3-suggested-batch.csv) ===

The refit: 18 articles, 6-D (five shape coordinates + printed mass in
[18, 23] g, fit_out_of_design=True), generation pinned at 20.23 g, same two
objectives, same per-drop-SEM noise (your noise recommendation is NOT yet
implemented), qNEHVI batch of nine. The batch pivoted to low twist (8/9 at
40 deg) and thick cables (7/9 at 5.5 mm), with all t180 predictions ~1.0.

 E1. Diagnose the pivot: is the model now chasing the r2d2c6 low-rebound
     corner on one round of evidence, and are the ~1.0 t180 predictions
     genuine learning (nothing round-2 beat round 1's best attenuator) or
     the posterior mean collapsing toward the data mean once the optimistic
     extrapolation was punished?
 E2. Your prior review prescribed: single objective t180, article-level
     noise floor, 3 articles x 10-12 drops, input severity as covariate.
     Given everything measured since, write the round-3 formulation you
     would run NOW, concretely: objectives and directions, constraints,
     noise numbers (give the formula and the value per objective),
     search-space treatment of the mass parameter and the re-projection
     shift, allocation of the ~9 print slots (new designs vs replicates of
     which articles), and whether the committed round-3 batch should be
     printed as-is, partially, or regenerated. If partially: which trials.
 E3. The constant-printed-mass change means round-3 articles will not shrink
     the way round-2 articles did, but the round-1 and round-2 training
     points were built under a DIFFERENT (solid-mass) projection. Does the
     printed-mass parameter adequately absorb that representation shift for
     fitting, or do you recommend refitting on as-printed geometry
     (available for all 18 articles in the bundles' design files)?

=== F. VERDICT ===

In order: (1) the calibration attribution from A2 and what it implies;
(2) which of the C claims survive for the 8/25 presentation, with required
caveats verbatim; (3) the concrete round-3 prescription from E2; (4) the
one cheapest measurement that would most reduce decision uncertainty
(candidates: re-seat and re-test r2d2c3, replicate prints of a front
article, restrained/unrestrained video test from your prior review; pick
and justify). Anchor in standard practice where relevant (GP calibration
diagnostics, qNEHVI under model misspecification, covariate shift,
replication design).

Output a single self-contained markdown report we can commit under
edison-trajectories/round2-results/. Lead with the conclusions that CHANGE
what we present on 8/25 and print for round 3.
"""


def main() -> int:
    bundle = OUT / "bundle"
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)

    for dest, src in BUNDLE_FILES.items():
        shutil.copy2(REPO / src, bundle / dest)
    print(f"bundle: {len(list(bundle.iterdir()))} files")

    if SUBMITTED.exists():
        task_id = json.loads(SUBMITTED.read_text())["task_id"]
        print("reusing task_id:", task_id)
        return 0

    resp = client.store_file_content(
        name="t3-bo-round2-results-review",
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
