# Campaign data snapshots used by the manuscript

All `t3-prism-bo-*` files are verbatim copies of the committed campaign
record, taken 2026-09-15 from branch `claude/issue-98-20260821-0103` at
commit `e25ebf5` (directory `bo/`). File-name convention on that branch:
`batch` = the Sobol seed batch (physical batch 1); `round1` = the first
model-recommended batch (`r2d2c*`, physical batch 2); `round3` = the
`drran*` batch (physical batch 3, Ax trials 28 to 36); `round4` = the
`corny*` batch (physical batch 4, Ax trials 37 to 45). The manuscript
numbers physical batches 1 to 4.

`round2-as-printed-solid-mass-projection.csv` and
`round3-candidate-constant-printed-mass.csv` are the two archived
recommendation sets discussed in the SI printed-mass section (provenance
fixed during the 2026-08-22 referee pass).

The dummy dataset `round2-measured-DUMMY.csv` and its generator were
removed on 2026-09-15: the real batch-2, 3, and 4 measurements above
supersede them.
