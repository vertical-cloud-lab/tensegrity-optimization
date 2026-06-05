# Bibliography DOI verification

Artifacts for the one-by-one DOI verification / enrichment pass over
`manuscript/references-full.bib` (813 entries).

## What was done locally (committed in this PR)

`scripts/edison/verify_bib_dois.py` checked **every DOI** in the master library
against its authoritative registered metadata (CSL JSON via
`https://doi.org/<doi>` content negotiation) and:

* **Verified titles** -- 581 DOIs matched their registered title; a handful
  resolved to an *unrelated* paper (wrong DOI) or returned 404.
* **Added abstracts** -- 179 entries received the abstract from their own DOI's
  Crossref record (JATS/HTML stripped, `&` escaped). The library now carries
  393 abstracts (up from 213).
* **Fixed a wrong DOI** -- `zhang2015tensegrity` pointed at an unrelated
  squash-mode vibration paper; corrected to `10.1063/1.5040850` (the real
  *Tensegrity cell mechanical metamaterial with metal rubber*, APL 2018) with
  its abstract and year.
* **Filled missing DOIs** -- 12 entries that had no DOI were matched to a
  Crossref record (author + title manually confirmed) and given a DOI; the
  library now has 604 DOIs (up from 592).

## What was sent to Edison (fetch next session)

The references the public DOI APIs could **not** settle -- DOIs that resolve to
the wrong paper / 404 with no confident replacement, plus entries with no DOI --
were written to [`needs-list.md`](needs-list.md) and submitted as an Edison
`LITERATURE_HIGH` task asking for the correct DOIs and link verification.

| Field | Value |
| --- | --- |
| Task id | `dbd490f6-edbc-4b8e-8778-b41e166b42ca` |
| Job | `LITERATURE_HIGH` (`job-futurehouse-paperqa3-high`) |
| Attachment | `data_entry:4d09a434-1cc6-440e-b6ab-8d17b2c47397` (`needs-list.md`) |
| Driver | [`scripts/edison/submit_bib_doi_verification.py`](../../scripts/edison/submit_bib_doi_verification.py) |
| Status | submitted (non-blocking) |

Fetch next session and fold the verified DOIs back in:

```python
from edison_client import EdisonClient
c = EdisonClient()
open("bib-doi-verification-dbd490f6.json", "w").write(
    c.get_task("dbd490f6-edbc-4b8e-8778-b41e166b42ca").model_dump_json())
```

### Entries flagged with a wrong/unresolvable DOI (in `needs-list.md` §A)

| key | issue |
| --- | --- |
| `fraternali2015tensegrity` | DOI resolves to an unrelated ceramics paper |
| `witze2023osirisrex` | DOI resolves to an unrelated rural-health article |
| `wang2022bayesian` | DOI resolves to an unrelated polyelectrolyte-gel paper |
| `lee2023bayesian` | DOI returns 404 |
| `grosu2025methodsforassessing` | DOI returns 404 |
| `wang2024simbencharulebased` | DOI title differs (possible different SimBench paper) |
