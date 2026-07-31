# Supplement deck → Draft 1 map

The supplement deck **adds to** `IDETC Tensegrity Slides Draft 1.pptx`. Nothing in
Draft 1 is replaced or deleted by it. Where an earlier review recommended hiding
one of @me-madsen's slides, that recommendation is withdrawn — the content is
restored below, with the media it was waiting for.

| Supplement slide | Draft 1 slide it serves | Status |
|---|---|---|
| 2 — tensegrity lander hook (Titan descent clip) | 2 (hook) | fills the "just the fall" video that the presenter note asked for |
| 3 — what tensegrity is (Steve Mould 2D clip) | **3 (was hidden)** | **restored.** The mechanism argument keeps its own slide instead of being spoken over slide 2 |
| 4 — baby toy → landing robot (NASA 360 clip, **with sound**) | 2 / 3 | new: the origin story in the researcher's own words — he throws a tensegrity baby toy at the floor and calls it a landing robot |
| 5 — reusability (SUPERball 3.4 m drop clip) | 2 / 4 | new: the "survives repeated drops" argument, which nothing in Draft 1 carried |
| 6 — prior work | — | new: the missing prior-work beat |
| 7 — the gap | 4 (need) | new: the motivation → gap → solution transition |
| 8–18 — EMC Bayesian-optimization block | **5 (was hidden)**, 7 | **restored.** Sterling's originals, animations intact |
| 19 — tensegrity-inspired caveat | 8 (multi-material printing) | plays immediately after slide 8, in the same breath |
| 20 — print timelapse (H2D, two materials, one build) | 8 | new; **same clip also opens the background addendum — keep one copy** |
| 21 — supports still come off by hand | 8 | new: challenge/mitigation beat for the AM section |
| 22 — the whole experiment in real time (**with sound**) | 9 | new: the from-afar drop @sgbaird supplied |
| 23 — phone slow motion (**with sound**) | 9 | new: the cheap instrument, and what it cannot do |
| 24 — what the 960 fps camera is actually for | 9 | fills the "slo motion of drop test" placeholder |
| 25 — elastic snap-back at 0.7× impact speed | 9 → 12 | new: reusability argued with **our** data, not NASA's |
| 26 — impact sequence montage | 9 | fills the "looped gif of drop test at 60 in" placeholder |
| 27 — camera vs. DAQ: which instrument owns the pulse | 9 → 11 | new: measured evidence, sets up the results block |
| 28 — drop tower and payload instrumentation | 9 | fills the setup half of the slide |
| 29 — SAE J211 filtering → three objectives | 7 / 9 | connects the measurement to the objective function |
| **30–35 — the issue #94 block** | 9 / Q&A | new: opens the drop-tower analysis to spot-checking — see [`issue-94-analysis-slides.md`](issue-94-analysis-slides.md) |
| 36–37 | — | working slides; delete before the talk |

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
| `clip-tensegrity-2d.mp4` | Steve Mould, "Tensegrity Explained" | 18 s | — |
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

**Three clips are played with the sound on** — the NASA 360 origin story
(slide 4), the whole-room drop (slide 22) and the phone slow-mo (slide 23). On
the two drops the bang is doing real work: it conveys how violent a
millisecond-scale event this is before any plot appears. Everything else plays
silently.

## Still needed

Drop-tower photo, and the campaign ledger / Pareto-front
figures once the campaign closes, and the Colab notebook owed to issue #94.
Slide 37 tracks these.

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
python presentation/background_slides.py
python presentation/set_presenter.py      # run last; it stamps the built decks
```
