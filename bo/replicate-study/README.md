# Replicate study and dran3 reprint: print files

Prepared on 2026-09-28 for @achris0520, as requested by @me-madsen on
PR #102 (comment 5873581840). There are four print jobs from two files:

| Print job | File to open in Bambu Studio | Articles | Filament settings |
|---|---|---|---|
| Replicate plates 1, 2 and 3: one gcode, printed three times | [`t3-prism-replicate-sne-plate1.H2D-MM-PLAstruts-TPUcables.3mf`](t3-prism-replicate-sne-plate1.H2D-MM-PLAstruts-TPUcables.3mf) | 1sne## on the first print, 2sne## on the second, 3sne## on the third (nine per plate) | PLA 226 C at 29.5 mm3/s, TPU 236 C at 2.6 mm3/s |
| dran3 reprint | [`t3-prism-dran3.H2D-MM-PLAstruts-TPUcables.3mf`](t3-prism-dran3.H2D-MM-PLAstruts-TPUcables.3mf) | dran31 to dran39 | PLA 217 C at 20.5 mm3/s, TPU 244 C at 3.6 mm3/s |

**Plates 2 and 3 print the same gcode as plate 1, in the same
orientation** (@achris0520 on PR #102, 2026-10-13). Every article on
plates 2 and 3 sits exactly where the plate-1 article with the same last
two digits sits: 2sne73 and 3sne73 print where 1sne73 does. The package
first shipped on 2026-09-28 with separate files for plates 2 and 3 that
moved the designs to different positions; those two files were removed on
2026-10-13, and the plate-1 file is unchanged.

Each replicate plate holds three copies of each of the three designs picked
in the [replicate study plan](../t3-prism-replicate-study-plan.md): corny7
(trial 37, on the Pareto front), corny8 (trial 39, further away) and corny2
(trial 38, furthest away). The dran3 plate is a third print of the round-3
plate that was printed as drran1-9 and again as 2dran1-9.

Every file here was built from the slicer project each design was first
printed from, so the geometry, the per-part infill and the filament settings
are the ones that produced corny7, corny8, corny2, drran and 2dran. Nothing
was re-rendered.

## Article IDs on the replicate plates

`[plate]sne[design digit][copy]`, where the plate digit is the print (first,
second or third print of the gcode), the design digit is 7 for corny7, 8
for corny8 and 2 for corny2, and the copy digit is the row: 1 = back row,
2 = middle row, 3 = front row. Example: `2sne73` is plate 2, corny7, front
row. The objects in the 3mf carry the plate-1 IDs (1sne71 and so on), and
the printer shows those names on every print: on plates 2 and 3, the object
called 1sne73 is the article you label 2sne73 or 3sne73. The `gcode_object`
column of the print key gives this for every article.

![Plate maps for the three replicate plates](t3-prism-replicate-sne-plate-maps.png)

Positions as seen from the front of the printer (left and right as you face
the door). The layout is the same on all three plates; only the plate digit
changes:

| Plate 1 | left | center | right |
|---|---|---|---|
| back | 1sne71 | 1sne81 | 1sne21 |
| middle | 1sne82 | 1sne22 | 1sne72 |
| front | 1sne23 | 1sne73 | 1sne83 |

| Plate 2 | left | center | right |
|---|---|---|---|
| back | 2sne71 | 2sne81 | 2sne21 |
| middle | 2sne82 | 2sne22 | 2sne72 |
| front | 2sne23 | 2sne73 | 2sne83 |

| Plate 3 | left | center | right |
|---|---|---|---|
| back | 3sne71 | 3sne81 | 3sne21 |
| middle | 3sne82 | 3sne22 | 3sne72 |
| front | 3sne23 | 3sne73 | 3sne83 |

Every row and every left/center/right column holds one article of each
design, so a front-to-back or left-to-right difference across the bed
affects all three designs equally on every plate. Because the plates are
identical, each design also prints in the same three positions every time:
corny2 holds the center and the back-right and front-left corners, corny7
the back-left corner, corny8 the front-right corner. A bed effect that is
not a simple front-to-back or left-to-right trend (center against corners,
for example) would therefore count toward the design difference. In
exchange, every position gets the same supports and the same toolpath on
all three plates, so the plates differ only by print job (spool, humidity,
bed condition).

**Required: label every article from the plate map before it comes off the
plate, using the plate digit of that print, and photograph the labeled
plate.** The three plates are identical, so the label is the only record of
which print an article came from. corny7 and corny8 also look almost the
same (same wide, high-twist family; the main difference is TPU infill, 21
vs 34 percent), and with three copies of each on a plate there is no way to
tell them apart after the fact.

## Print settings for the three replicate plates

These are the round-4 (corny) plate settings, already written into the
file. All three designs come from that one plate, so a single set of
filament settings reproduces each design's original print. (Nozzle
temperature and max volumetric speed are per filament, so a plate can only
carry one value of each; that is why the picks were kept within round 4.)

| Setting | Value |
|---|---|
| Printer, nozzle | Bambu Lab H2D, 0.6 mm nozzles, Textured PEI plate |
| Process preset | `0.30mm Standard @BBL H2D 0.6 nozzle` (0.30 mm layers, 2 walls) |
| Struts (left nozzle) | `Bambu PLA Basic @BBL H2D 0.6 nozzle`, 226 C, max volumetric speed 29.5 mm3/s (about 159 mm/s) |
| Cables (right nozzle, TPU High Flow hotend) | `Bambu TPU 85A @BBL H2D`, 236 C, max volumetric speed 2.6 mm3/s (about 14 mm/s) |
| Sparse infill, set per part | corny7: struts 22 %, cables 21 %; corny8: struts 21 %, cables 34 %; corny2: struts 18 %, cables 34 % |
| Supports | off in the files; paint them on as for round 4 |
| Wipe tower | pre-placed at x = 287 mm, y = 110 mm, 10 mm wide (same as round 4) |

Before slicing (required; you slice once for all three plates):

1. Check the object list shows nine objects named by plate-1 article ID
   (1sne21 to 1sne83).
2. Select any part and confirm its settings list shows "Sparse infill
   density" with the value from the table above. A control slice showed the
   overrides are active in this file (deleting them saves 6.7 g of PLA per
   plate), but check anyway after the file opens.
3. Paint supports and slice once. Print that gcode three times, as three
   separate jobs (plates 1, 2 and 3), without re-slicing or moving anything
   in between. Use the same spools if possible, and note the relative
   humidity for each print.

Headless slice check on 2026-09-28 (Bambu Studio v02.07.01.62 command line,
the lab's version; record in
[`t3-prism-replicate-slice-check.json`](t3-prism-replicate-slice-check.json)):
the plate-1 file slices with exit code 0, all nine named objects sliced, no
conflict, out-of-area or nozzle errors, and one expected warning (a floating
cantilever on a corny2 copy, because supports are not painted yet). It
estimates about 14 h 55 min and 175 g PLA + 60 g TPU per print including the
wipe tower, flushing and brims, before supports, so about 45 h and 526 g PLA
+ 179 g TPU for the three prints. The record also keeps the passing checks
of the two removed plate-2 and plate-3 files.

## dran3 reprint

![dran3 plate map](t3-prism-dran3-plate-map.png)

**The articles of this print are labeled `dran31` to `dran39`.** These files
first named them `3dran1` to `3dran9` (commit cf667d8, 2026-09-28); the lab
labeled the printed articles `dran31` to `dran39` instead, and the files now
use the labels that are on the articles (@achris0520 on PR #102,
2026-10-01). `3dranN` and `dran3N` are the same article, so read `3dranN` in
anything older as `dran3N`.

dran3N is the same design as drranN and 2dranN. Masses for this print are
from the print log @ctrhjk posted on issue #98 on 2026-09-29:

| ID | Trial | Earlier prints (mass with label, g) | This print (mass with label, g) | Struts infill | Cables infill |
|---|--:|---|--:|--:|--:|
| dran31 | 36 | drran1 19.31, 2dran1 19.48 | 19.93 | 34 % | 26 % |
| dran32 | 33 | drran2 19.33, 2dran2 19.65 | 19.71 | 29 % | 16 % |
| dran33 | 31 | drran3 19.92, 2dran3 20.15 | 20.46 | 18 % | 21 % |
| dran34 | 29 | drran4 19.92, 2dran4 20.19 | 20.41 | 13 % | 31 % |
| dran35 | 28 | drran5 19.88, 2dran5 20.22 | 20.17 | 21 % | 29 % |
| dran36 | 34 | drran6 19.24, 2dran6 19.54 | 19.72 | 16 % | 34 % |
| dran37 | 32 | drran7 20.06, 2dran7 20.32 | 20.56 | 24 % | 13 % |
| dran38 | 35 | drran8 19.32, 2dran8 19.51 | 20.00 | 26 % | 24 % |
| dran39 | 30 | drran9 19.34, 2dran9 19.65 | 19.68 | 31 % | 18 % |

The photos in that log show each label on an article of the right design
family, and the masses repeat the pattern of the first two prints: the same
four designs are the heaviest, and dran35 is again the heaviest of the three
articles that share one shape (dran32, dran35, dran39). This print averages
0.21 g above 2dran and 0.48 g above drran. Two pairs cannot be told apart
from these photos or masses (dran31 and dran38, the two thin-cable designs,
which differ mainly in twist; dran32 and dran39, which share a shape), so
for those two pairs the label order rests on the plate positions the labels
were applied from.

The file is the committed round-3 project
([`../slices/t3-prism-bo-round3.H2D-MM-PLAstruts-TPUcables.3mf`](../slices/t3-prism-bo-round3.H2D-MM-PLAstruts-TPUcables.3mf))
with only the object names changed (`Trial 36` became `dran31`, and so on)
and the plate label set. The build script checks that every other byte of the
project, including the meshes, the filament settings and the 18 infill
overrides, is unchanged.

Things to know before printing it:

- **The settings are not the replicate-plate settings.** PLA 217 C at 20.5
  mm3/s (about 110 mm/s), TPU 244 C at 3.6 mm3/s (about 19 mm/s). 244 C needs
  the `Bambu TPU 85A @BBL H2D` preset, not the `0.4 nozzle` variant; the file
  already carries the right one.
- **Print it the same way as 2dran.** If you still have the support-painted
  project you printed 2dran from, printing from that is the closest match to
  the earlier prints; use the table above to label. If you print from this
  file, paint the supports the way you did for drran and 2dran.
- **Please post whichever project you actually print from** on issue #98 or
  PR #102. The repo has no copy of the support-painted round-3 project, and
  this is the third print of that plate.
- For the record, not an action item: the command-line slicer stops on this
  file with "No valid nozzle found", and on the committed round-3 original
  too (checked 2026-09-28). The round-3 project was assembled before the
  generator started writing the H2D dual-nozzle machine state, which the GUI
  fills in from the printer; the GUI printed it twice. It is left unpatched
  so the third print uses the same file as the first two.

## Performance of the three picks

![Rebound energy vs shock transmissibility for corny7, corny8 and corny2](t3-prism-replicate-picks-performance.png)

Measured first articles, one print and one accelerometer seating each
(round-4 drop sessions of 2026-09-12 for corny2 and 2026-09-14 for corny7
and corny8):

| Design | Trial | t180 | Rebound energy (mJ per drop) | Mass (g) |
|---|--:|--:|--:|--:|
| corny7 | 37 | 0.803 | 9.37 | 19.62 |
| corny8 | 39 | 0.954 | 17.54 | 19.64 |
| corny2 | 38 | 1.085 | 9.22 | 20.21 |

The replicate plates exist to find out how much of that spread is the
design and how much is the individual print and seating. The pre-registered
predictions and the scoring rules are in the
[plan](../t3-prism-replicate-study-plan.md).

## Experiment parameters (set by @sgbaird on PR #102, 2026-09-23)

- Three characteristic designs roughly along the diagonal: one on the Pareto
  front (corny7), one further away (corny8), one furthest away (corny2).
- Three repeats of each design per plate (nine articles per plate), three
  plates, 27 articles in total.
- All three plates print one gcode with one layout (@achris0520,
  2026-10-13).
- The question: is there signal, do repeats help the campaign, and do the
  measured ranks follow the predictions (rank correlation).

Drop testing, from the plan (required unless marked optional):

- Record 22 valid captures per article, so that 20 count after the standard
  2-drop discard.
- Interleave designs within a session instead of testing all copies of one
  design back to back.
- Start and end each block with the same reference article (bpx68c, or one
  designated corny7 copy), and log the accelerometer re-seat (wax bed plus
  tape) for every article.
- Weigh and photograph every article, dran3 included.
- Optional: one 10 to 12 drop re-seat re-run of r2d2c3 in the same campaign.

## Other files

- [`t3-prism-replicate-print-key.csv`](t3-prism-replicate-print-key.csv):
  every article ID (27 replicate + 9 dran3) with design, trial, plate, row,
  slot, plate position, infill, filament settings, predicted printed mass,
  the earlier prints of the same design, and `gcode_object`, the name the
  article's object has in the 3mf and on the printer (the plate-1 ID for
  every replicate plate).
- [`stls/`](stls/): the struts and cables STLs for corny7, corny8 and corny2,
  and in [`stls/dran3/`](stls/dran3/) the nine round-3 designs named by dran3
  ID. These are byte copies of the committed per-trial STLs in
  [`../per-specimen-stls/`](../per-specimen-stls/). Struts are PLA, cables are
  TPU; load a pair together as one object with two parts so they stay
  aligned. The 3mf files above are the easier route.

Everything in this folder is rebuilt, byte for byte, by
[`../t3_prism_replicate_plates.py`](../t3_prism_replicate_plates.py):

```bash
python3 bo/t3_prism_replicate_plates.py
```
