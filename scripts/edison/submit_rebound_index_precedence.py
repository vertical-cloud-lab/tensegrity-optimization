"""Submit two Edison Scientific literature tasks on PRECEDENT for our rebound index.

Driven by me-madsen on issue #94:
> run a literature review and report if there is any precedence for using an
> index such as this, particularly in this sort of application. Report briefly
> with links to that precedence, preferably papers, with brief summaries (i.e.
> equation used in a previously unorthodox way, their justification, how it
> relates, etc.).

"An index such as this" is the drop-tower objective
    lambda = e * m_printed * g * h        (minimized, alongside a transmitted-
                                           shock peak ratio)
with e = v_sep / dv a FIRST-POWER restitution-like velocity ratio whose
numerator comes from vertex hop flight time (v_sep = g*t_second/2) and whose
denominator is the base plate's arrest velocity change. The #97 Edison audit
(edison-trajectories/rebound-energy-audit/) already established what lambda is
NOT (returned energy, which would be e^2 with the flying mass). This task asks
the complementary question: what published precedent EXISTS for indices of
this kind, so the group can decide whether to keep, rename, or replace it.

Two jobs:
  * PRECEDENT ("has anyone...") - the sharp yes/no form of the question.
  * LITERATURE_HIGH - deep review across the candidate precedent families,
    each with equation, stated justification, and mapping to our index.

Idempotent: records task ids in rebound-index-precedence-SUBMITTED.json and
refuses to double-submit.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from edison_client import EdisonClient, JobNames, TaskRequest

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "edison-trajectories" / "rebound-index-precedence"
OUT.mkdir(parents=True, exist_ok=True)
SUBMITTED = OUT / "rebound-index-precedence-SUBMITTED.json"

api_key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
if not api_key:
    raise SystemExit("EDISON_API_KEY (or EDISON_PLATFORM_API_KEY) not set")
client = EdisonClient(api_key=api_key.strip())

SETTING = r"""
SETTING (shared context for the question):

We rank small 3D-printed tensegrity-inspired structures (T3 prisms, printed
mass m = 18-23 g) for shock absorption with a benchtop drop tower: a plate
carrying the specimen falls h = 60 in and arrests on a polyurethane mat
(~300 G, ~2 ms base pulse, arrest velocity change dv ~ 5.4 m/s). After the
pulse, the specimen's top vertex subassembly separates from its printed seat
and lands back t_second = 17-55 ms later. Per drop we compute

    v_sep = g * t_second / 2          (ballistic time-of-flight estimate)
    e     = v_sep / dv                (~0.02-0.05; FIRST power, not squared;
                                       numerator and denominator refer to
                                       different bodies/interfaces: vertex
                                       flight vs plate arrest)
    lambda = e * m * g * h            (reported in mJ; minimized in a
                                       Bayesian-optimization campaign together
                                       with a transmitted-shock peak ratio,
                                       forming a two-objective Pareto front)

A previous audit established lambda is NOT returned kinetic energy (that would
be e^2 with the actually-flying mass) and renamed it a "velocity-weighted
impact-energy index". The question now is PRECEDENT: has anything like this
been done before, and on what stated justification?
"""

PRECEDENT_QUERY = (
    SETTING
    + r"""
Has anyone used a first-power coefficient-of-restitution-like velocity ratio
(rebound-to-incident velocity, NOT squared into an energy fraction), or such a
ratio multiplied by a nominal impact energy scale like m*g*h, as a
standardized index, figure of merit, or optimization objective for ranking
impact-absorbing or shock-attenuating materials, structures, equipment, or
surfaces? Examples might live in rebound hardness testing, sports-equipment
and sports-surface compliance testing, packaging/cushioning, granular or
particle damping, discrete-element-model calibration, or architected-material
impact studies. Cite specific standards or papers, give the equation each one
uses, and state the justification its authors give for using a velocity ratio
(or an unorthodox composite) rather than a true energy quantity.
"""
)

LITERATURE_QUERY = (
    SETTING
    + r"""
TASK: a focused literature review on PRECEDENT for indices of this kind. For
every precedent you assert, give: the defining equation; the stated
justification in the source (quote or close paraphrase, and say which); the
full citation with DOI or URL; and one sentence on how it maps onto (or fails
to map onto) our lambda = e*m*g*h with cross-referenced numerator/denominator.
Please cover, correct, and extend the following candidate families - refute
any we have wrong rather than confirming politely:

1. FIRST-POWER VELOCITY-RATIO INDICES AS STANDARDIZED METRICS.
   - Leeb rebound hardness HL = 1000 * v_rebound / v_impact (ISO 16859-1,
     ASTM A956): an industrial index built on first-power velocity ratio.
     What justification do the standard or foundational papers give?
   - Sports-equipment coefficient-of-restitution compliance: ASTM F1887
     (baseball/softball COR), NCAA BBCOR bat standard, USGA golf COR /
     characteristic-time limit. These regulate/rank equipment on first-power
     e directly.
   - "Apparent COR" / "collision efficiency" / Ball Exit Speed Ratio in bat
     performance research (e.g. A. Nathan, Am. J. Phys. 71, 134 (2003), and
     related), where the velocity ratio deliberately mixes reference
     points/bodies (ball speed in lab frame vs combined pitch+bat speeds) -
     structurally similar to our mixed numerator/denominator. Why was that
     accepted as a metric?
   - Schmidt/rebound hammer number for concrete (ASTM C805, EN 12504-2): an
     empirical rebound index mapped to strength only through calibration
     curves. What do the standards say about its non-fundamental status?

2. REBOUND MEASURED FROM FLIGHT TIME BETWEEN IMPACTS (our v_sep = g*t/2
   estimator) IN STANDARDIZED OR PUBLISHED TESTS.
   - FIFA Quality Programme / EN 12235 vertical ball rebound for sports
     surfaces: is the rebound height obtained from inter-bounce timing
     (h = g*t^2/8), e.g. acoustically, in any official test method? Also
     World Rugby / artificial turf test methods.
   - Physics-education lineage: Bernstein Am. J. Phys. 45:41 (1977);
     Stensgaard & Laegsgaard Am. J. Phys. 69:301 (2001); Aguiar & Laudares
     Am. J. Phys. 71:499 (2003); Nagurka & Huang (bouncing-ball timing);
     Bartz Eur. J. Phys. 44:025003 (2023).

3. IMPACT-SEVERITY INDICES WHOSE FORM IS DIMENSIONALLY UNORTHODOX BUT
   JUSTIFIED EMPIRICALLY (precedent for "index that ranks well, honestly
   labeled, beats physical purity").
   - Gadd Severity Index integral(a^2.5 dt) and HIC (units g^2.5*s, chosen to
     fit the Wayne State tolerance curve; Gadd 1966 SAE 660793, Versace 1971
     SAE 710881): the canonical example of a deliberately non-physical
     exponent adopted as a regulatory metric.
   - Viscous Criterion VC = V(t)*C(t), Lau & Viano 1986 (SAE 861882): a
     product of two different measures with velocity units used as an injury
     index.
   - N. Jones' "energy-absorbing effectiveness factor" (Int. J. Impact Eng.
     37:754, 2010): a purpose-built dimensionless composite for ranking
     energy absorbers.
   - Packaging cushion factor C = peak stress / absorbed energy density and
     Janssen factor. Any others we should know about.

4. REBOUND-BASED RANKING OF ABSORBERS WHERE LOWER REBOUND = BETTER
   ABSORPTION (our optimization direction).
   - Ball rebound resilience of flexible polyurethane foam: ASTM D3574
     Test H and ISO 8307 (we print PU; this is the material family's own
     industry convention - note it reports height ratio = e^2 as a percent).
   - Rubber resilience: ISO 4662, ASTM D2632, Bashore/Schob/Luepke pendula.
   - Sports-surface PAIRED metrics: force reduction / shock absorption
     (EN 14808) together with vertical ball rebound (EN 12235) as a
     two-axis characterization - structurally the same as our Pareto pair of
     transmitted-shock ratio + rebound index. Any source that discusses why
     both axes are needed?
   - Particle/impact dampers and granular dampers designed or tuned via
     (low) effective coefficient of restitution; DEM calibration literature
     treating first-power e as THE standard contact dissipation parameter.

5. THE EXACT COMPOSITE. Any published metric of the form (dimensionless
   velocity or restitution ratio) x (nominal input energy) used as a reported
   figure of merit, in any field? Note the identity lambda = sqrt(E_in *
   E_returned) under same-mass assumptions (geometric mean of incident and
   returned energy) - has any field used a geometric-mean-of-energies index?
   If you find nothing, say plainly that the exact composite appears to be
   without precedent.

6. BOTTOM LINE for a methods section: given the above, is minimizing our
   lambda (or the raw ratio e) defensible-with-precedent as an honestly-named
   index, and which single precedent is closest? Would the literature better
   support optimizing raw e and reporting mass separately?

Return a markdown report ordered by these six sections, each precedent as a
short entry (equation / justification / citation / mapping). Flag anything
above that is factually wrong. Distinguish what you verified in retrieved
text from what you infer.
"""
)


def main() -> int:
    if SUBMITTED.exists():
        print("already submitted:", SUBMITTED.read_text())
        return 0

    tasks = {}
    for label, job, query in [
        ("precedent", JobNames.PRECEDENT, PRECEDENT_QUERY),
        ("literature_high", JobNames.LITERATURE_HIGH, LITERATURE_QUERY),
    ]:
        submitted = client.create_task(TaskRequest(name=job, query=query))
        task_id = submitted if isinstance(submitted, str) else str(submitted)
        tasks[label] = {"task_id": task_id, "job": job.name}
        print(f"submitted {label} ({job.name}): {task_id}")

    SUBMITTED.write_text(json.dumps({"tasks": tasks}, indent=2))
    (OUT / "query-precedent.md").write_text(PRECEDENT_QUERY)
    (OUT / "query-literature-high.md").write_text(LITERATURE_QUERY)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
