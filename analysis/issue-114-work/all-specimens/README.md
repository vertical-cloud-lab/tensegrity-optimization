# Peak work near 40 ms for every corny specimen (issue #114)

Justin asked on 2026-10-06 for his updated work code to be run on every drop
of every specimen, with the peak of the total work near 40 ms taken as each
drop's value, and for the mean and standard deviation of that value per
specimen. corny7's batch is corny1 to corny9: nine specimens, 20 drops each,
60 in onto the 1/2 in polyurethane (PU) mat, recorded 2026-09-12 and
2026-09-14 with the same four accelerometer channels.

## Result

Justin's peak finder works on corny6, corny7, corny8 and corny9: every drop
from 3 to 20 has a clear peak inside his 25 to 45 ms window, and no drop
needed a corrected search. corny1 to corny5 have no peak in any drop, so all
five specimens are left out (details below).

| Specimen | Mean (J/kg) | Standard deviation (J/kg) |
|---|---|---|
| corny6 | -1.270 | 0.240 |
| corny7 | -2.599 | 0.133 |
| corny8 | -0.875 | 0.145 |
| corny9 | -2.022 | 0.152 |

Each value is over drops 3 to 20 (n = 18), the drops Justin's loop uses. The
standard deviation uses n - 1. The units are joules per kilogram of top mass,
because Justin's code sets m = 1.

![Mean peak work per specimen](figures/01_mean_peak_work_by_specimen.png)

## How each drop was checked

- The work curve is Justin's `numaric_work`, compiled straight out of
  [`justin/implimatation_or_work_2026-10-06.py`](justin/implimatation_or_work_2026-10-06.py)
  and called exactly as his loop calls it (CH4 as the top, CH5 as the bottom,
  m = 1, g = 9.81, v0 = -5.46). The corny7 mean comes out at -2.599 J/kg, the
  same as his plot.
- His peak is `max(work_z[1250:2250])`, the largest total work between 25
  and 45 ms. A pick counts as a peak only if it sits at least 0.5 ms inside
  the window and stands at least 0.5 J/kg above the curve on both sides (its
  prominence). If a pick failed, the script looked for the most prominent
  peak between 15 and 70 ms instead. That fallback was never needed.
- The 0.5 J/kg cutoff sits in a wide gap: the peaks on corny6 to corny9 stand
  0.96 to 1.31 J/kg proud, while the largest bump anywhere on a corny1 to
  corny5 curve between 15 and 70 ms is 0.31 J/kg.

![Work curves for all nine specimens](figures/02_work_curves_all_specimens.png)

## Why corny1 to corny5 have no peak

- Their total work never dips at the impact (-0.26 to 0.00 J/kg at its
  lowest, against -2.7 to -4.3 J/kg for corny6 to corny9) and then climbs for
  the rest of the record. Justin's window maximum lands on the 45 ms edge of
  the window in nearly every drop, at +1.3 to +1.9 J/kg.
- CH4 is the vertical axis on all nine specimens, so the channel is not the
  cause. Over the first 15 ms CH4 picks up 10 to 13 % more velocity than the
  base plate's CH5 on corny1 to corny5, against 0 to 3 % on corny6 to corny9.
  The top therefore moves up relative to the base from the start, and the
  work goes positive.
- A massless spring under a point mass cannot give back more energy than it
  took in, so positive work means that model does not fit these five tall,
  40 degree twist designs (they are also the five with T180 above 1). A
  likely reason is that the specimen's own 20 g of struts and cables drives
  the 0.8 g sensor, which the model leaves out.

## Other things worth knowing

- **The peak time depends on the specimen.** corny9 peaks at 29.7 ms,
  corny6 at 34.1 ms, corny8 at 40.1 ms and corny7 at 41.0 ms. All four fall
  inside 25 to 45 ms, but a future specimen could peak outside it, so a
  prominence check like the one in `work_all_specimens.py` is safer than a
  fixed window.
- **corny6's peak has two humps** (near 33.5 and 36.5 ms). Three of its 18
  drops (15, 17, 18) take the later hump because it is higher there. corny6
  also scatters most from drop to drop, as its T180 does (coefficient of
  variation 2 %, the batch's highest).
- **The peak work ranks the four specimens in the same order as T180**:
  corny7 loses the most energy and has the lowest T180, then corny9, corny6
  and corny8. That is four specimens, so treat it as a lead. Within one
  specimen the drop-to-drop scatter does not follow T180.
- The warm-up drops 1 and 2 are left out of the averages, as in Justin's loop,
  but they are in the per-drop table.

![Peak work against T180](figures/03_peak_work_vs_t180.png)

## Files

| File | What it holds |
|---|---|
| [`results/peak_work_summary.csv`](results/peak_work_summary.csv) | The table above |
| [`results/specimen_details.csv`](results/specimen_details.csv) | All nine specimens: drops with a peak, mean peak time, lowest work at the impact, the CH4 to CH5 velocity ratio, the window maximum Justin's code returns, and T180 |
| [`results/per_drop_peak_work.csv`](results/per_drop_peak_work.csv) | All 180 drops, with each drop's peak status, value, time and prominence |
| [`waveforms/`](waveforms/) | The 50 kHz waveform CSV of each specimen, in the same format as the corny7 export, so Justin's script runs on any of them after changing the file name |
| [`work_all_specimens.py`](work_all_specimens.py) | Runs the analysis and draws the figures |
| [`fetch_waveforms.py`](fetch_waveforms.py) | Downloads the 180 captures from Box (about 1.7 GB) and writes `waveforms/`. Its corny7 output is byte-identical to the issue #110 export |
| [`box-ids/`](box-ids/) | Box file ids of each session, copied from the corny check-in on PR #86 |
| [`justin/`](justin/) | Justin's script as uploaded on 2026-10-06 |

To reproduce: `python fetch_waveforms.py --raw <scratch folder>`, then
`python work_all_specimens.py`.
