# Edison trajectory — fifth-round mock JMD peer review

Per PR comment 4700329518 (@sgbaird-yolo: *"yes"* — approving the round-4 ask to
integrate the already-flagged tensegrity additive-manufacturing references), the
further-revised manuscript draft was submitted to Edison **ANALYSIS** for a fifth
round of mock peer review. This follows round 1 (task `6c140449`,
Reject-and-Resubmit), round 2 (`…-3fde560e…`, Major Revision), round 3
(`…-d17a2155…`, Major Revision but improving), and round 4 (`…-a81649dc…`, Major
Revision and closer to publishable form).

## What changed since round 4

The round-4 Associate-Editor letter confirmed all four round-3 citation gaps
(SAASBO, TuRBO, SEA/densification metrics, SAE J211) were closed and asked only
that the already-flagged tensegrity-AM works be integrated once verified. Each
DOI was verified against Crossref and the following are now cited in the
manuscript background (replacing the prior `\todo{}` placeholder note):

- Bauer et al. 2021, *Adv. Mater.* 33(10):2005647 (doi:10.1002/adma.202005647)
- Pajunen et al. 2021, *Extreme Mech. Lett.* 44:101236
  (doi:10.1016/j.eml.2021.101236)
- Sabouni-Zawadzka et al. 2024, *Arch. Civ. Eng.* 70(2):343–357
  (doi:10.24425/ace.2024.150987)
- Almeida et al. 2025, *Int. J. Solids Struct.* 322:113590
  (doi:10.1016/j.ijsolstr.2025.113590)
- Davami et al. 2025, *Int. J. Impact Eng.* 198:105208
  (doi:10.1016/j.ijimpeng.2024.105208)
- Wang et al. 2026, *Addit. Manuf.* 118:105107 (doi:10.1016/j.addma.2026.105107)

(Santos 2023, *Adv. Mater.*, doi:10.1002/adma.202300639, was already cited.)

## What was sent

`bundle/` (zipped into `mock-jmd-review-5-bundle.zip` and uploaded as a single
collection, which ANALYSIS requires; the bundle/zip are regenerable build
artifacts and are not committed):

- `manuscript.pdf` — clean reader PDF (todonotes hidden)
- `manuscript-todos.pdf` — review PDF with margin `\todo{}` notes + `\listoftodos`
- `supplementary.pdf` — Supplementary Information
- `manuscript-body.tex`, `manuscript.tex`, `manuscript-todos.tex`,
  `supplementary.tex`, `references.bib`, `README.md`

## Reproduce

```bash
python scripts/edison/submit_mock_jmd_review5.py   # uploads bundle, submits ANALYSIS
python scripts/edison/fetch_mock_jmd_review5.py    # polls + writes the trajectory
```

The fetched review (`mock-jmd-review-5-<task_id>.md` / `.json` / `.ipynb`) is
committed alongside this README.
