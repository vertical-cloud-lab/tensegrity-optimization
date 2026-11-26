# Where the project page's files come from

`docs/index.html` is a single hand-editable HTML file with no build step and no
CSS or JavaScript framework. Everything it shows is in this folder, except the
talk recording (YouTube [`EhCbsQ58AGo`](https://youtu.be/EhCbsQ58AGo), the
IDETC-CIE 2026 talk at the lab's group meeting on 21 Sep 2026), which loads
from YouTube only when someone presses play. The page loads YouTube's
thumbnail for it (`maxresdefault.jpg`, 1280 × 720).

| File | Source |
|---|---|
| `images/fig1_overview_loop.png` | `figures/overview-loop.png` on the manuscript branch of #76 (`copilot/vertical-cloud-labtensegrity-optimization`, [`624e868`](https://github.com/vertical-cloud-lab/tensegrity-optimization/tree/624e868/figures)), byte for byte. Fig. 1 of the manuscript. |
| `images/fig2_design_space.png` | `figures/design-space.png` at `624e868`, byte for byte. Fig. 2. From Request B (#120). |
| `images/fig3_print_timelapse.jpg` | `figures/photos/print-timelapse-plate1.jpg` at `624e868`, byte for byte. Fig. 3: frames of replicate plate 1 from YouTube [`EmCLms7-Bd8`](https://youtu.be/EmCLms7-Bd8). From Request D (#119). |
| `images/fig4_transmissibility_trace.png` | `figures/analysis/transmissibility-trace-57vqhX-drop50.png` at `624e868`, byte for byte. Fig. 4. From Request D (#119). |
| `images/fig5_replicate_specimens.jpg` | `figures/photos/replicate-specimens-panel.jpg` at `624e868`, byte for byte. Fig. 5: the replicate photos from #119. |
| `images/fig6_front_evolution.png` | `figures/bo/t3-prism-bo-front-evolution.png` at `624e868`, byte for byte. Fig. 6, in the m·e² form of #126. |
| `images/fig7_seed_designs.png` | `figures/bo/fig-seed-designs.png` at `624e868`, byte for byte. Fig. 7. From #120. |
| `images/fig8_batch4_predicted_vs_measured.png` | `figures/bo/t3-prism-bo-round4-predicted-vs-actual.png` at `624e868`, byte for byte. Fig. 8. From #120. |
| `images/fig9_three_prints.png` | `figures/analysis/round3-three-print.png` at `624e868`, byte for byte. Fig. 9, in the m·e² form of #126. |
| `images/figS4_sim_campaign.png` | `figures/sim/sim-campaign.png` at `624e868`, byte for byte. Fig. S4 of the supplementary information. From Request E (#123). |
| `images/surrogate_parity.png` | `analysis/bo-review/figures/logocv-parity-noise.png` on #121's branch (`claude/request-c-tables-logocv-ai-20261027`, [`ef7f2d9`](https://github.com/vertical-cloud-lab/tensegrity-optimization/tree/ef7f2d9/analysis/bo-review/figures)), byte for byte. Drawn by `analysis/bo-review/plot_fixes.py` from the committed run records ([comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/121#issuecomment-7155009556), "paper candidate 1"). Not in the manuscript at `624e868`: a candidate to replace SI Fig. S3, whose run is its top row. |
| `images/surrogate_importance.png` | `analysis/bo-review/figures/feature-importance-noise.png` at `ef7f2d9`, byte for byte, by the same script ("paper candidate 2"). Not in the manuscript at `624e868`: a candidate to replace or follow SI Fig. S2. |
| `images/printed_specimen.jpg` | `figures/photos/printed-specimen-light-bg.jpg` at `624e868`, byte for byte: a printed T3 prism (white PLA, orange TPU). |
| `videos/teaser.mp4`, `images/teaser.jpg` | [`make_teaser.py`](make_teaser.py), from two clips already in this repository (below). The poster is the frame at 4.4 s. |
| `screenshots/` | The page in headless Chrome at 1280 px and 390 px wide, its Talk section, its *Checking the surrogate* section at both widths (`surrogate.png`, `surrogate-phone.png`), and the teaser's storyboard, for the pull requests. The page doesn't link to them. |

The figure numbers and captions on the page follow the compiled manuscript
(`manuscript/manuscript.pdf` at `624e868`, built 5 Nov 2026 from
`manuscript-body.tex` and `supplementary.tex`). That branch already merges
Requests A to E (#122, #120, #121, #119, #123) and the m·e² follow-ups
#125, #126 and #127. On the page, the first sentence of each caption shows and
the rest is folded under *Full caption*; section, table and equation numbers
in the captions are the paper's. Table 1 is copied from the manuscript's
`tab:design-vars`. The title, abstract and author list are from
`manuscript-body.tex` at `624e868`. If the manuscript's figures or captions
change, update the page to match.

The exception is the *Checking the surrogate* section, which is a re-analysis
from #121 that the manuscript at `624e868` doesn't have yet. Its two figures
have no paper numbers. Their captions, the numbers in the text and the
*Held-out skill* table come from `analysis/bo-review/README.md` at `ef7f2d9`
(section "Figures: the surrogate with the fixes applied") and from the #121
comment linked above. The page links the interactive plotly version of the
two figures, `analysis/bo-review/figures/index.html`, through htmlpreview,
pinned to the full hash of `ef7f2d9` so that it matches the PNGs; that page
loads `plotly-4.1.1.min.js` from the same folder, so nothing comes from a
CDN. If those figures go into the paper, give them the paper's numbers and
captions here.

### The teaser

10 s, 1280 × 720, no audio, two panels at the same time:

| Panel | Clip | Source | Edit |
|---|---|---|---|
| Left | `presentation/media/clip-print-timelapse.mp4` on #84's branch ([`e08f890`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/e08f890/presentation/media/clip-print-timelapse.mp4)) | The talk's 16 s cut of the TT3_01 build-chamber timelapse, YouTube [`nQNmi-NiL5I`](https://youtu.be/nQNmi-NiL5I) (14 Jul 2026), posted on #84 | sped up 1.6×; 636 px wide crop that keeps the prism and the prime tower |
| Right | `data/drop-tests/prc1kn-60in-5felt/video/prc1kn_video1_slomo.mp4` on #86's branch ([`011c8e1`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/011c8e1/data/drop-tests/prc1kn-60in-5felt/video/prc1kn_video1_slomo.mp4)) | Specimen prc1kn dropped from 60 in onto five felt pads, filmed at 959 fps (the talk's `clip-our-slomo-drop.mp4` is cut from the same prc1kn footage) | 3.3 s to 13.3 s of the file: the carriage comes in, lands and settles; 1080 × 1223 crop scaled to 636 × 720 |

The labels are burned in with ffmpeg's `drawtext` (DejaVu Sans), and the clip
fades in and out over 0.4 s so the loop restarts cleanly. To rebuild it (needs
ffmpeg with libx264):

```bash
python docs/static/make_teaser.py fetch     # the two source clips into /tmp/teaser-src
python docs/static/make_teaser.py render    # videos/teaser.mp4 and images/teaser.jpg
python docs/static/make_teaser.py contact   # screenshots/teaser_storyboard.jpg
```

Footage considered and left out of the teaser: the replicate-plate timelapse
behind Fig. 3 (YouTube only; YouTube refuses the runner's IP, and the lab Pi
used as a relay elsewhere didn't answer on the tailnet on 24 Nov 2026), the
wide shot of the drop tower (`clip-drop-afar.mp4`, a busy lab background), the
960 fps clip of specimen 7xadt6 (`clip-drop-highspeed.mp4`, dim), the
support-removal clip (a single-material print), and the drop-and-plot
comparison videos on #86 and #114 (analysis views rather than footage).
