# Edison standards audit — SAE J211 CFC filter, baseline, and "transmissibility"

Task `6af9d904-05e2-4e51-87ab-509a10eb85b1` (ANALYSIS), submitted 2026-07-31,
retrieved 2026-08-06 (status `success`). Raised from issue #94, which asked for the
drop-tower analysis to be spot-checkable rather than taken on faith.

## What was asked

An independent standards audit of four things claimed in-repo, framed so the
auditor could refute rather than confirm:

1. Whether `cfc_filter()` implements SAE J211 Appendix C, and what the correct
   corner frequencies and 550 Hz attenuation actually are.
2. What J211 / ISO 6487 actually require for baseline (zero-level) determination
   and minimum pre-trigger duration.
3. Whether a ratio of two CFC-filtered peaks is a recognised quantity called
   "transmissibility".
4. Whether ISO 5347 or ISO 5348 is the accelerometer mounting standard.

Prompt and driver: [`scripts/edison/submit_j211_audit.py`](../../scripts/edison/submit_j211_audit.py).

## Files

| file | contents |
|---|---|
| `j211-audit-6af9d904-…​.md` | the report (26 kB) |
| `j211-audit-6af9d904-…​.json` | full task dump, including the agent trajectory |
| `j211-audit-6af9d904-…​-notebook.ipynb` | the auditor's own computation notebook |
| `j211-audit-SUBMITTED.json` | task id + uploaded data-entry id |
| `cfc_verification.txt` | our pre-submission in-repo check |
| `verify_report_numbers.py` / `.txt` | independent re-derivation of every filter number in the report |

## Headline outcomes

- **CONFIRMED** — `cfc_filter()` is not the J211 Appendix C filter; 2.0775 is the
  per-pass corner and the filtfilt pair lands at 1.6667 × CFC, so passing
  `1.65 × CFC` to scipy's single-pass `Wn` makes every class ~20 % narrow. Correct
  CFC-180 attenuation at 550 Hz is **5.68×**, not the 12.3× published in
  `docs/drop-test-pu-configs-analysis.md`.
- **Refined** — the exact Appendix C pair corner is 1.6666604 × CFC, not 1.65, so
  the equivalent classes are CFC-48/144/481/794, not the CFC-49/146/486/802 we
  reported. Also: J211 §9.4.1 mandates Appendix C only for CFC-60 and CFC-180;
  CFC-600/1000 are corridor-defined and our use of the same shape there needs a
  numerical corridor check, not an assertion.
- **REFUTED** — no clause in SAE J211-1:1995 or ISO 6487:2015 specifies a baseline
  window or a minimum pre-trigger duration. Appendix C's 10 ms is *endpoint padding*
  guidance, not a zero-estimation rule. Any claim that a baseline choice is
  "standards-required" is unsupported.
- **REFUTED** — the ratio of two non-concurrent CFC-filtered peaks (one of them a
  tri-axial norm) is not "transmissibility" in any of J211, ISO 6487, ISO 18431,
  ASTM D3332, ASTM D7136 or MIL-STD-810 Method 516. Call it a *CFC-filtered
  output/input peak-acceleration ratio*.
- **CONFIRMED** — ISO 5348:2021 is the mounting standard; ISO 5347 was a
  calibration series, withdrawn and largely superseded by ISO 16063.
- **Raised on us** — our proposed ≥ 2 ms pre-trigger is under-specified: 2 ms is
  1.1 cycles at 550 Hz and shorter than the CFC-180 impulse-response decay
  (>1 % of peak out to ~3.3 ms). Specify **≥ 10 ms, preferably 20 ms** of verified
  quiet pre-trigger.
- **Also raised on us** — scipy's default `filtfilt` padlen is 9 samples (7.2 µs at
  1.25 MHz), far short of Appendix C's 10 ms endpoint-copy guidance for an event
  starting 0.35 ms into the record.

## Caveats stated by the auditor

- Clause text was verified against the publicly accessible **SAE J211-1:1995** and
  the **ISO 6487:2015** preview. The current edition (J211/1_202208) was not
  publicly accessible, so nothing is quoted from it as verified.
- The 40 waveform CSVs were **not** attached to this task (it was scoped to
  standards, not data), so the report could not reproduce our record-level
  percentages — the "<1 % change in T(CFC-180)" and "+9 % on T(CFC-1000)" numbers
  remain our own dataset-specific results.
- The ≥10 ms pre-trigger, the 8–10 (preferably ≥20) repeats per configuration, and
  the "analyse below 0.2 × measured mounted resonance" figures are the auditor's
  engineering recommendations, explicitly *not* quoted standard minima.
