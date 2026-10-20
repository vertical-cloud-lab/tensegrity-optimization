# IDETC 2026 plain-language teaching slides for the drop-test section

Created for issue #94 (request: add the necessary instruction to the audience,
avoiding jargon, into the current IDETC presentation).

## What was added to the deck

Two slides, inserted directly **after the sensors slide** ("We use
accelerometers and slow-motion capture…") and before the data-comparison slide,
so the audience learns how to read the data right between "here is the
hardware" and "here is what the data tells us":

1. **"Each drop tells a two-part story: the jolt going in, and the ringing
   that follows."** (`fig1_one_drop_two_parts.png`): how to read one real
   drop: the sharp jolt at the bottom sensor, what arrives at the top sensor,
   then the struck-bell ringing (about 560 wobbles/second) whose fade-out is
   the structure soaking up energy.
2. **"Every recording gets the same standard treatment, and each drop boils
   down to one score."** (`fig2_smoothing_and_score.png`): why every lab
   smooths shock recordings (raw trace spikes past 5,000 G from the metal
   parts/sensor, not the structure), that we use the crash-test-lab standard
   recipe (SAE J211), and the score = biggest jolt at top divided by biggest
   jolt at bottom (below 1 = softened).

Per the PR #100 review on 2026-08-20, fig1's jolt panel carries no in-panel
callout text (the space is kept clear for annotation on the slide), its axis
labels are the short "time (ms)" and "acceleration (G)", and the background is
pure white. `fig1_part1_only.png` is that panel alone: the exact crop that
slides 18 and 19 of `idetc-2026.pptx` display. The web editor's Change Picture
re-crops a swapped image to fill its shape, so deck swaps use this pre-cropped
file rather than the full two-panel figure.

Both new slides carry full speaker-note talk tracks (see
`add_teaching_slides.py`), including the honest caveats from the issue #86/#94
audits: the quoted peak depends on the smoothing recipe (hence a fixed
standard), the score ranks structures but is **not** "energy absorbed in
joules", and the official campaign logs falling mass / drop height / extra
pre-jolt quiet time.

The drop-video slide's placeholder note ("Need more information about the drop
tests…") was replaced with an actual plain-language talk track describing the
rig (60-inch drop onto felt, two accelerometers, one on the plate and one in
the printed pocket at the top vertex per PR #35, 1.25 M readings/s for 20 ms,
about a minute per drop).

Wording note: all slide text, note text, and figure text avoids spaced hyphens
and dashes entirely (colons, commas, parentheses instead). This matches the
repo style guide, and it is also load-bearing for the web-editor insertion:
PowerPoint's autocorrect converts a typed " - " into an en dash mid-note, and
typed non-ASCII characters are silently dropped, so text that needs to be
typed into the editor must be plain ASCII with no spaced hyphens.

## Where it went

Applied to **`idetc-2026.pptx`** (the deck issue #94 targets, reachable
through the `PPT_EDIT_LINK` workflow secret, which as of 2026-08-17 grants
edit) as slides 12 and 13, via the Office web editor per the PR #100 thread.
An earlier pass had also applied the same slides to "IDETC Tensegrity Slides
Draft 1.pptx" (v31.0, 2026-08-17, slides 11 and 12 there) when the link still
resolved to that file read-write and to `idetc-2026.pptx` read-only.

To apply the same insertion to any other copy or future revision:

```bash
python make_teaching_figures.py          # rebuilds the two PNGs from raw CSVs
python add_teaching_slides.py in.pptx out.pptx
```

The insertion anchors on slide titles, not slide numbers, so it works on any
revision of the deck.

## Two-specimen comparison graphs (PR #100 follow-up, 2026-08-22)

`make_comparison_figures.py` builds `fig3_compare_6lhxfy.png` and
`fig3_compare_bag26v.png`: one clean single-panel graph per specimen for the
slide that contrasts a strong attenuator with an amplifier from the SOBOL + S0
campaign. Style follows the same cleanup rules as fig1 (short axis labels,
no titles, no in-panel callouts, pure white background); the specimen ID lives
only in the file name so the slide author labels the panels however they like.
Both graphs share identical axis limits and tick marks, so they can sit side
by side at the same size and be compared directly.

Each graph is one representative drop: the stabilized drop whose CFC 180
transmissibility is closest to the specimen's session mean (6lhxfy Signal 64,
bag26v Signal 47). Unlike fig1/fig2, the traces and the printed
transmissibility use the **campaign pipeline exactly** (`analyze_capture` with
the tail baseline and the pipeline's CFC 180 filter, vendored from
`scripts/analysis/drop_test_abc123_blind_analysis.py` on the
`copilot/add-drop-test-protocol-again` branch), so the peak ratio visible in
each graph equals the official campaign `t180` for that drop; the script
asserts the match against `campaign_metrics.json`. Raw Signal CSVs stay on
Box (repo convention) and are auto-fetched into the uncommitted `raw_cache/`
using the file IDs from the committed `box-ids.json` manifests.

| specimen | this drop | session mean (101 drops) |
|---|---|---|
| 6lhxfy | 0.893 | 0.893 (sd 0.004) |
| bag26v | 1.062 | 1.062 (sd 0.005) |

## Data and processing

Figures are built from one real capture in this repo:
`57vqhX_Signal50.csv` (session "57vqhX 60 in - 4 felt 1 crdbrd", 2026-07-28;
1.25 MHz, 20 ms; CH2 to CH4 = tri-axis top vertex, CH5 = base). Baseline is
the median of the quiet pre-trigger window. CFC filtering uses the
**corrected** SAE J211 implementation from the issue #94 Edison audit,
`butter(2, 2.0775*CFC, fs=fs)` + `filtfilt` (per-pass corner 2.0775·CFC, pair
corner 1.6667·CFC), not the roughly 20 %-narrow `1.65·CFC` variant in the
older analysis scripts. Colors are the validated 2-slot colorblind-safe pair
(blue #2a78d6 = bottom sensor, orange #eb6834 = top sensor).
