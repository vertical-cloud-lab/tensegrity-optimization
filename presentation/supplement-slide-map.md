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
| 20 — what the 960 fps camera is actually for | 9 | fills the "slo motion of drop test" placeholder |
| 21 — impact sequence montage | 9 | fills the "looped gif of drop test at 60 in" placeholder |
| 22 — camera vs. DAQ: which instrument owns the pulse | 9 → 11 | new: measured evidence, sets up the results block |
| 23 — drop tower and payload instrumentation | 9 | fills the setup half of the slide |
| 24 — SAE J211 filtering → three objectives | 7 / 9 | connects the measurement to the objective function |
| 25 — the calibration error we caught | — | new: challenge/mitigation beat |
| 26–27 | — | working slides; delete before the talk |

Draft 1 slide 6 (specimen information value / experiment-first) stays a slide of
its own. It is the pre-emptive answer to the sharpest predicted Q&A challenge,
and merging it into slide 4 would bury it.

## Media

Everything on these slides is real and embedded — no dashed placeholders, no
internet needed at the podium. Sources and crops are in
[`build_supplement_deck.py`](build_supplement_deck.py); the clips themselves are
in [`media/`](media/).

| Clip | Source | Length |
|---|---|---|
| `clip-titan-descent.mp4` | NASA Super Ball Bot / NIAC Titan concept | 20 s |
| `clip-tensegrity-2d.mp4` | Steve Mould, "Tensegrity Explained" | 18 s |
| `clip-nasa-toy-lander.mp4` | Adrian Agogino, "NASA 360 Talks: Super Ball Bot" | 16 s, **played with sound** |
| `clip-superball-3m-drop.mp4` | SUPERball v2, IEEE Spectrum / NASA Ames | 10 s |
| `clip-our-slomo-drop.mp4` | our own 959 fps footage, prc1kn 60 in / 5 felt | 9 s |

The four external clips carry an on-slide credit line. The NASA footage needs
only "Credit: NASA"; the Steve Mould and IEEE Spectrum clips are copyrighted and
keep channel + title + URL on screen while they play. Every clip plays silently
except the NASA 360 one, which is played *for* its audio.

## Still needed

Drop-tower photo, printer-bed shot, and the campaign ledger / Pareto-front
figures once the campaign closes. Slide 27 tracks these.

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
