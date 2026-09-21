# Edison literature review: precedent for the rebound index

Requested by @me-madsen on
[issue #94](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/94)
(2026-09-21): "run a literature review and report if there is any precedence for
using an index such as this, particularly in this sort of application."

"An index such as this" is the drop-tower objective `e_reb_mJ = e * m * g * h`,
where `e = v_sep / dv` is a first-power restitution-like velocity ratio (vertex
hop flight time over plate arrest velocity change). The
[#97 audit](../rebound-energy-audit/) established what this index is not
(returned energy). This trajectory asks the complementary question: what
published precedent exists for indices of this kind.

## Tasks

Two tasks were submitted on 2026-09-21 by
[`scripts/edison/submit_rebound_index_precedence.py`](../../scripts/edison/submit_rebound_index_precedence.py)
and fetched the same session by
[`scripts/edison/fetch_rebound_index_precedence.py`](../../scripts/edison/fetch_rebound_index_precedence.py).
Both finished with status `success`.

| Task | Job type | Id | Question |
| --- | --- | --- | --- |
| precedent | PRECEDENT | `2af9efae-1e1e-4038-ac07-25bbe9a0fb0c` | Has anyone used a first-power restitution ratio, or such a ratio times `m*g*h`, as a standardized index or optimization objective for impact absorbers? |
| literature_high | LITERATURE_HIGH | `65bfb670-fe7a-443c-b260-c0f552a3e43b` | Deep review across six candidate precedent families, each entry with equation, stated justification, citation, and mapping to our index. |

## Files

- `query-precedent.md`, `query-literature-high.md`: the exact query texts.
- `precedent-2af9efae-....md` / `.json`: the PRECEDENT answer and full task dump.
- `literature_high-65bfb670-....md` / `.json`: the deep review and full task dump.
- `rebound-index-precedence-SUBMITTED.json`: task ids (idempotency record).

## Bottom line

Both tasks agree, and agree with an independent in-session web review:

1. First-power velocity ratios as standardized ranking indices have strong
   precedent (Leeb hardness HL = 1000 v_r/v_i per ISO 16859 and ASTM A956;
   sports COR compliance such as ASTM F1887 and NCAA BBCOR; Schmidt hammer).
2. Minimizing a first-power restitution ratio to rank a cushioning system has
   direct precedent (Zhu et al. 2018 gravel rockfall cushions; Perkins et al.
   2019 boxing gloves; Zhao et al. 2020 surfaces).
3. Our flight-time estimator `v_sep = g t / 2` is the standard time-between-
   bounces method (Bernstein 1977 lineage) and appears in official sports
   surface testing (FIFA Test Method 01 family, per Colino et al. 2020).
4. Dimensionally unorthodox impact indices adopted for empirical fit are
   accepted practice when honestly labeled (Gadd Severity Index and HIC,
   viscous criterion, Jones effectiveness factor, cushion factor).
5. The exact composite `e * m * g * h` has no published precedent found by
   either task or by the web review. Where sources convert restitution to
   energy they use e squared. The literature better supports optimizing raw e
   with mass reported separately, which matches the standing recommendation
   from the #97 audit thread.

## Corrections the review made to our framing

- EN 12235 implementations in the retrieved literature measure rebound height
  directly (ultrasonic sensor); the acoustic inter-bounce timing lives in the
  FIFA Quality Programme turf method (Test Method 01), per Colino et al.,
  Sensors 20:1688 (2020). Our claim that EN 12235 itself is timing-based was
  too broad.
- One retrieved source labels the ASTM D3574 resilience procedure "Test D"
  rather than "Test H"; verify the suffix against the current edition before
  citing it in the manuscript.
