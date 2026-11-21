# Drop-test troubleshooting — Edison Scientific LITERATURE_HIGH

**Trigger:** sgbaird PR comment 4546311380 — _"send to edison scientific (high
effort literature). Fetch this session. Commit all artifacts."_

**Task:** `653d7d39-b9c4-4d3f-9ae1-a1bc8fabd877`
(`job-futurehouse-paperqa3-high`, status `success`)

**Artifacts**

- [`drop-test-653d7d39-b9c4-4d3f-9ae1-a1bc8fabd877.md`](drop-test-653d7d39-b9c4-4d3f-9ae1-a1bc8fabd877.md)
  — formatted answer (~57 KB), section skeleton (a)–(g) plus an
  actionable-recommendations summary and ~40 references.
- `drop-test-653d7d39-b9c4-4d3f-9ae1-a1bc8fabd877.json` — full task dump
  (~100 KB) including raw answer, tool traces, and references.
- `drop-test-SUBMITTED.json` — submission record (task_id + attached
  `data_entry` URI for `docs/drop-test-protocol.md`).

**Driver:** [`scripts/edison/submit_drop_test.py`](../../scripts/edison/submit_drop_test.py)
(idempotent via the `*-SUBMITTED.json` placeholder).

## Headline recommendations (from §"Summary of Actionable Recommendations")

1. Replace plain acrylic holes with **linear sleeve bearings on hardened
   ground rods** to eliminate the ~25° cage tilt.
2. Add **light magnetic or elastic hold-down** to the top plate to stop
   specimen lift-off during descent.
3. **Extend DAQ capture to ≥10 s** with ring-buffer + pre-trigger to keep
   the full ringdown, not just the 200 ms shock.
4. **Start video before hoist release** with a TTL trigger to the camera
   so the initial descent is in frame.
5. Apply **SAE J211 CFC 1000** filtering in post-processing; tap-test the
   fixture to characterize modal frequencies.
6. **Condition specimens at 23 °C / 50 % RH for ≥40 h**; pre-dry filament;
   consider annealing PLA / PETG struts at 90–120 °C.
7. Account for **TPU 85A strain-rate stiffening** (2–5× modulus at impact
   rates) when comparing drop-test SEA to quasi-static predictions.
8. Run **n ≥ 5 specimens per condition**, report CV — sets the BO noise floor.
9. **Upgrade to ≥5000 fps high-speed camera** for any quantitative DIC
   work; phone slow-mo for qualitative checks only.
10. Closest published analogues to benchmark against: **Pajunen 2019**
    (3D-printed tensegrity impact, _Materials & Design_ 182:107966) and
    **Dwyer 2023** (spatially varying elastomeric lattices).

Standards stack surfaced by the report: ASTM D5276, D7136, D3332,
ISO 6603, ISO 1683, MIL-STD-810 method 516, SAE J211 (filtering),
ISO 5347 (accelerometer mounting / anti-alias).
