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
