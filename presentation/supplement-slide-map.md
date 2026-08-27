# Supplement deck → Draft 1 map

The supplement deck **adds to** `IDETC Tensegrity Slides Draft 1.pptx`. Nothing in
Draft 1 is replaced or deleted by it. Where an earlier review recommended hiding
one of @me-madsen's slides, that recommendation is withdrawn — the content is
restored below, with the media it was waiting for.

| Supplement slide | Draft 1 slide it serves | Status |
|---|---|---|
| 2 — tensegrity lander hook (Titan descent clip) | 2 (hook) | fills the "just the fall" video that the presenter note asked for |
| **3 — what tensegrity is (Steve Mould 2D teaching clip, 35 s, with sound)** | **3 (was hidden)** | **restored, and now the background block.** The full teaching excerpt, not the 18 s silent crop that cut off the push-and-recovery |
| **4 — anatomy: struts in compression, cables in tension** | 3 | new: the mechanism visual the mock audience said the grad student needed |
| 5 — baby toy → landing robot (NASA 360 clip, **with sound**) | 2 / 3 | new: the origin story in the researcher's own words — he throws a tensegrity baby toy at the floor and calls it a landing robot |
| 6 — reusability (SUPERball 3.4 m drop clip) | 2 / 4 | new: the "survives repeated drops" argument, which nothing in Draft 1 carried |
| 7 — prior work | — | new: the missing prior-work beat |
| 8 — the gap | 4 (need) | new: the motivation → gap → solution transition |
| 9–19 — EMC Bayesian-optimization block | **5 (was hidden)**, 7 | **restored.** Sterling's originals, animations intact |
| 20 — tensegrity-inspired caveat | 8 (multi-material printing) | plays immediately after slide 8, in the same breath |
| 21 — print timelapse (H2D, two materials, one build) | 8 | new: our own 16 s timelapse, pulled through the lab Pi |
| 22 — supports still come off by hand | 8 | new: challenge/mitigation beat for the AM section |
| 23 — the whole experiment in real time (**with sound**) | 9 | new: the from-afar drop @sgbaird supplied |
| 24 — phone slow motion (**with sound**) | 9 | new: the cheap instrument, and what it cannot do |
| 25 — what the 960 fps camera is actually for | 9 | fills the "slo motion of drop test" placeholder |
| 26 — elastic snap-back at 0.7× impact speed | 9 → 12 | new: reusability argued with **our** data, not NASA's |
| 27 — impact sequence montage | 9 | fills the "looped gif of drop test at 60 in" placeholder |
| 28 — camera vs. DAQ: which instrument owns the pulse | 9 → 11 | new: measured evidence, sets up the results block |
| 29 — drop tower and payload instrumentation | 9 | fills the setup half of the slide |
| 30 — SAE J211 filtering → three objectives | 7 / 9 | connects the measurement to the objective function |
| **31–36 — the issue #94 block** | 9 / Q&A | new: opens the drop-tower analysis to spot-checking — see [`issue-94-analysis-slides.md`](issue-94-analysis-slides.md) |
| 37–38 | — | working slides; delete before the talk |

Draft 1 slide 6 (specimen information value / experiment-first) stays a slide of
its own. It is the pre-emptive answer to the sharpest predicted Q&A challenge,
and merging it into slide 4 would bury it.

## Media

Everything on these slides is real and embedded — no dashed placeholders, no
internet needed at the podium. Sources and crops are in
[`build_supplement_deck.py`](build_supplement_deck.py); the clips themselves are
in [`media/`](media/).

| Clip | Source | Length | Audio |
|---|---|---|---|
| `clip-titan-descent.mp4` | NASA Super Ball Bot / NIAC Titan concept | 20 s | — |
| `clip-tensegrity-2d-teaching.mp4` | Steve Mould, "Tensegrity Explained" | 35 s | **yes** |
| `clip-nasa-toy-lander.mp4` | Adrian Agogino, "NASA 360 Talks: Super Ball Bot" | 16 s | **yes** |
| `clip-superball-3m-drop.mp4` | SUPERball v2, IEEE Spectrum / NASA Ames | 10 s | — |
| `clip-print-timelapse.mp4` | our own print timelapse, TT3_01 (`nQNmi-NiL5I`) | 16 s | — |
| `clip-support-removal.mp4` | our own footage, manual support removal (PR #35, 2026-06-09) | 12 s | — |
| `clip-drop-afar.mp4` | our own footage, whole-room drop (@sgbaird attachment `b16e3d32`) | 7 s | **yes** |
| `clip-drop-phone-audio.mp4` | our own phone slow-mo, specimen `n0jdwk`, 13 in (PR #67) | 3.3 s | **yes** |
| `clip-our-slomo-drop.mp4` | our own 959 fps footage, prc1kn 60 in / 5 felt | 9 s | — |
| `clip-drop-highspeed.mp4` | our own 960 fps footage, specimen `7xadt6`, 60 in / 5 felt (PR #86 branch) | 6 s | — |

The four external clips carry an on-slide credit line. The NASA footage needs
only "Credit: NASA"; the Steve Mould and IEEE Spectrum clips are copyrighted and
keep channel + title + URL on screen while they play. The six clips of our own
work carry a provenance line pointing at the campaign they came from.

**Four clips are played with the sound on** — the 2D teaching model
(slide 3), the NASA 360 origin story (slide 5), the whole-room drop (slide 23)
and the phone slow-mo (slide 24). On the teaching clip the narration *is* the
explanation, so say nothing over it. On the two drops the bang is doing real
work: it conveys how violent a millisecond-scale event this is before any plot
appears. Everything else plays silently.

One figure is generated rather than photographed:
`media/fig-tensegrity-anatomy.png`, the labelled anatomy on slide 4, is drawn by
`build_anatomy_figure()` in `build_supplement_deck.py` from a still of the same
teaching model (`media/photo-tensegrity-2d-model.jpg`).

## Still needed

Drop-tower photo, and the campaign ledger / Pareto-front
figures once the campaign closes, and the Colab notebook owed to issue #94.
Slide 38 tracks these.

## Title slide

The presenter is **Marcus Madsen, Research Assistant**. That block sits on Draft 1
slide 1, but the EMC template also keeps a presenter block on the *Title Slide
layout* and the talk title on the *slide master* — which is why Draft 1 slide 14
used to show Sterling's EMC title and affiliation. `set_presenter.py` stamps the
right identity onto every deck and onto both build sources (`emc-bo-block.pptx`,
`emc2026-bare-template.pptx`), so a rebuild cannot bring the EMC text back.

Rebuild with:

```bash
python presentation/build_supplement_deck.py
python presentation/set_presenter.py      # run last; it stamps the built decks
```
