# T-3_01 Sobol batch: print key and slicer files

This directory holds the key linking each printed T3-prism specimen ID to its
Sobol design parameters, for use when parsing drop data during the testing
campaign (issue [#98](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98)).

## Files

- `t3-prism-bo-batch-print-key.csv`: one row per physical print. Maps the
  6-character print ID to its Sobol specimen number (0 to 8, or S0 for the
  reference prism), the plate in the slicer project, its role
  (official test article or rejected duplicate), documented mass, RH% at time
  of print, noted defects, and as-printed geometry.
- `t3-prism-bo-batch.csv`: the full Sobol batch design table (base and
  as-printed parameter values, mass and envelope constraint checks), copied
  from PR #35 commit `32addaf` so it is available on `main`.
- `slices/t3-prism-bo-batch.H2D-MM-PLAstruts-TPUcables.as-printed.3mf`: the
  Bambu Studio project actually used for the batch prints, uploaded by
  @me-madsen in issue #98. Plates 1 to 9 each hold one specimen and are named
  with the print IDs; plate 10 is an unnamed staging plate with six specimens
  and was not a print source of record.

## Provenance of the key

The print-ID-to-specimen mapping comes from the `.3mf` itself: each plate's
name records the print IDs and each plate carries exactly one specimen object
("Specimen 00" through "Specimen 08"). Masses, RH%, and defects come from the
print documentation comments in issue #98. Geometry columns are the
as-printed values from `t3-prism-bo-batch.csv`.

Known discrepancy, not yet resolved: for Specimen 08, the plate 1 label in
the `.3mf` marks `dea4ls` as official and `bag26v` as good, while the issue
#98 comment of 2026-08-12 marks `bag26v` as official. The key records the
`.3mf` labels and flags both rows; confirm which print is the test article
before analysis.

The S0 reference prism (`bpx68c`) is not part of the Sobol batch and is not
in this `.3mf`; its row is included because it is being tested alongside the
batch. Its geometry is the base T3 prism at scale factor 1.1538 (see the
issue #98 discussion of 2026-08-17).
