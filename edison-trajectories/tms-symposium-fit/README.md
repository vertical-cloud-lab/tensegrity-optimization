# TMS 2027 symposium-fit feedback (Edison ANALYSIS)

Asks Edison for candid feedback on whether the TMS 2027 abstract
(`tms-2027-abstract.md`) fits the **AI-Enabled Materials Processing:
Integrating Accelerated Experimental Workflows and Processing-Aware Machine
Learning** symposium, how to strengthen the processing/print-parameter angle,
and which other (additive-manufacturing / architected-materials) TMS symposia
might fit better.

- `bundle/` — files uploaded to Edison: the draft abstract, the symposium
  call-for-abstracts flyer (`TMS2027-CFA-Flyer.pdf`) and its extracted text.
- `tms-symposium-fit-SUBMITTED.json` — task id + uploaded-bundle URI (resumable).
- `tms-symposium-fit-<task_id>.md` / `.json` — fetched answer + full task dump.

Driver scripts: `scripts/edison/submit_tms_symposium_fit.py` (submit) and
`scripts/edison/fetch_tms_symposium_fit.py` (poll + fetch).
