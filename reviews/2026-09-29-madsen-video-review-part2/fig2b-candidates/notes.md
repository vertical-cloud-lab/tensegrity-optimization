# Fig. 2(b) replacement candidates (for Marcus to check)

Comparison: `fig2b-candidates.jpg`. The callouts are TikZ, so the drop-in files
for `figures/photos/printed-specimen.jpg` are the clean photos
`candA_corny4_clean.jpg` and `candB_bgreplaced_clean.jpg` (1200 x 1333 px).

## Recommendation

Use **Candidate A** until a reshoot exists, and please check it. It is a real
photo of an untaped article on a light backdrop, with no compositing. The only
edits are a global gray balance, levels and gamma (0.72). Keep Candidate B as a
fallback.

## Candidate A: corny4

- Source: [issue #98 comment 5637649574](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5637649574) (2026-09-11, ctrhjk, 4th photo).
- Issues: the article is newer than panel (a). It has square strut-end cages
  and green TPU, while the CAD render has spherical nodes, so panel (a) and the
  caption ("PR #35", "orange") need updating. Its comment records pores on the
  diagonal tendons. A small "corny4" label is visible, and the back nodes are
  slightly soft.
- TikZ coordinates:
  - d_s: (0.15,0.90) to (0.335,0.50)
  - d_t: (0.43,0.93) to (0.445,0.785)
  - H: x = 0.86, from 0.305 to 0.71. H is on the right because the left is
    taken. It spans the left and right node planes, and perspective makes it
    approximate.

## Candidate B: background replaced

- Mask: rembg `isnet-general-use`. There are no jagged or lost tendons at 100%.
- Issues: it looks cut out, with no contact shadow. The PLA reads bluish, the
  edges have faint dark fringing, and the white nodes lose contrast. The
  background replacement must be disclosed in the caption.

## Current panel bug

The current d_t arrow tip (0.34,0.70) lands on the shaded back PLA strut, not a
tendon.

## Other sources checked

Details are in `photo_candidates.csv`.

- 6lhxfy, the photo Marcus showed: [issue #98 comment 5348529679](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5348529679) (2026-08-19, me-madsen). It is taped.
- bpx68c ([5334673614](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5334673614)) and ebdna8 ([5285048840](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98#issuecomment-5285048840)): untaped, but tightly cropped, with large marker labels.
- The drran, 2dran and other August articles are taped.
- PR #35, issues #85, #86 and #108, and PR #102 have nothing better.

## Reshoot checklist

- A raw, unlabeled article of the tested geometry. Put its ID in the file name.
- A white or light gray paper sweep.
- Diffuse light from softboxes or a window plus a white card. Keep a soft
  contact shadow.
- A camera angle 15 to 20 degrees above the top plane.
- No strut hiding another, and one top tendon unobstructed.
- A frame of 0.9 width to height, with the prism at about 75% of the height.
- f/8 to f/11 so the front and back nodes are both sharp.
- One frame with a ruler.
- A matching CAD view for panel (a).
