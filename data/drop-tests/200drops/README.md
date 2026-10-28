# 200-drop campaign — specimen `7xadt6`, 10 in, CH5 trigger

Posted by @ctrhjk in PR #67 (2026-07-13). First long campaign on a **fresh
intact print** (`7xadt6`) — all previous ≥30-drop campaigns used the failed
prints `prc1kn`/`RW5F61`.

## Setup

- Specimen: **`7xadt6`** (new print, unique ID assigned).
- Drop height: **10 in**. A practice run at 5 in engaged **neither a CH4 nor a
  CH5 trigger at 1000 G**, so the height was raised until triggering worked.
- Trigger: **CH5 (base plate single-axis), 1000 G** — moved back from CH4.
- 200 auto-drops; DAQ 200 ms / 125 kHz / 25,000 samples / 2 % (4 ms)
  pre-trigger, all channels ICP + AC coupling, same sensitivities as the
  previous campaigns.
- Uploaded as 8 zips of 25 CSVs each (per the SOP in
  `docs/drop-test-protocol.md` §6).

## Channel map

| channel | station | full scale | notes |
|---|---|--:|---|
| CH2, CH3, CH4 | tri-axis, **top-vertex key-seat** ("TOP", output) | 14,492.8 / 14,992.5 / 13,624.0 G | taped housing entrance + cable tie |
| CH5 | single-axis, **base plate** (taped) | 9,442.9 G | **trigger, 1000 G** |
| CH6, CH7, CH8 | low-range tri-axis, **bottom-vertex housing** ("BOT") | 1,002.0 / 991.1 / 989.1 G | taped entrance + cable tie |

## Files

- `raw/200drops_Signal{3..202}.csv` — 200 TP4 exports; **drop k =
  Signal k+2** (Signals 1–2 were the failed practice/trigger attempts and were
  not exported).
- `figures/` — full series, BOT dropout/headroom, CFC-180 series, stabilized
  OLS, damage indicators, per-axis migration + `200drops_metrics.json`
  (machine-readable per-capture metrics).

## Known data issues (see `docs/drop-test-200drops-analysis.md`)

1. **BOT (CH6–8) electrical dropout on Signals 61–173** (113/200 captures):
   CH6 rails at ~1,030 G for ~14 ms on Signal 60, then the whole BOT block
   collapses to the electrical noise floor (~0.01 G RMS) and self-recovers at
   Signal 174 — an ICP/cable intermittency, not a mechanical fall-off.
2. **CH7 and CH8 exceed full scale** on most BOT-alive captures at 10 in
   (median 97 % / 105 % FS) — all BOT quantities are qualitative only.
3. **CH5 mid-campaign excursion** around drops ~140–175 (dips to 210 G
   CFC-180 at drop 173, T spikes to ~1.16 at drops 170–176), coinciding with
   the BOT recovery and two impact-timing outliers — a transient disturbance
   of the plate sensor's tape coupling.
