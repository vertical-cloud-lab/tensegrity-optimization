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

## Headline finding (task 16895002-4776-4382-8c67-c08f47f42062)

As written, the abstract is a **partial fit (≈4/10)** for the current target
symposium **#021 "AI-Enabled Materials Processing"**, whose CFA demands
*processing history as a primary design variable* — but our optimization targets
geometry/topology, not process parameters.

- **Best home as written: AM-track symposium #003 "Additive Manufacturing
  Modeling, Simulation, and Artificial Intelligence: Microstructure, Mechanics,
  and Process"** (≈8.5/10, near-zero edits; just soften "processing-aware").
- **Keep #021 only by making processing real (≈7/10):** add 2–4 FDM process
  variables to the BO loop (interface overlap, PLA/TPU nozzle temperature, layer
  height, print speed) plus a process-sensitive response (interfacial-failure
  incidence / bond-strength proxy / void fraction / dimensional fidelity).
- Other backups: #023 "Algorithms Development in MSE" (method-first framing),
  #005 "Designing Complex Microstructures Through AM". No dedicated
  architected-materials, polymer-AM, or AM-mechanical-behavior symposium was
  found in the TMS 2027 flyer set.
- Abstract is ~141 words (≈9 of slack under the 150-word cap); ready-to-paste
  114-word Path-A and Path-B rewrites are given in the answer.
