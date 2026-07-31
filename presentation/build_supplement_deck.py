"""Rebuild the IDETC supplement deck: message titles, big type, real video.

Design rules enforced here (the v1 deck broke all of them):
  * one full-sentence message per slide, in the title, <= 2 rendered lines
  * body text >= 24 pt, <= ~160 characters per slide
  * the visual owns the slide; text does not
  * every media slot holds a real clip or figure, not a dashed placeholder

Sterling's EMC 2026 Bayesian-optimization block is carried over untouched
(byte-identical slide XML, animations intact) from the v1 supplement deck.

Usage:  python presentation/build_supplement_deck.py
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).parent
DECKS = HERE / "Slide Decks"
MEDIA = HERE / "media"
# Read from the pristine EMC block, never from the output deck: SRC == OUT
# made the build non-idempotent, and a second run silently sliced its own
# freshly-written slides 4-14 out in place of the BO explainer.
SRC = HERE / "emc-bo-block.pptx"
OUT = DECKS / "IDETC Supplement Slides (BO block + gap + video + accel).pptx"

# EMC slides to keep from SRC (1-indexed): the whole BO explainer block.
KEEP = list(range(1, 12))

NAVY = RGBColor(0x0E, 0x28, 0x41)
BLUE = RGBColor(0x15, 0x60, 0x82)
ORANGE = RGBColor(0xE9, 0x71, 0x32)
GRAY = RGBColor(0x59, 0x59, 0x59)

SW, SH = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.55)
TITLE_TOP = Inches(0.35)
TITLE_H = Inches(1.30)
BODY_TOP = Inches(1.90)
BODY_BOTTOM = Inches(6.95)


def title_only(prs):
    return prs.slides.add_slide(prs.slide_layouts[1])


def set_message(slide, text, size=30):
    """Put the slide's one message in the title placeholder, Doumont-style."""
    ph = slide.shapes.title
    ph.left, ph.top = MARGIN, TITLE_TOP
    ph.width, ph.height = SW - 2 * MARGIN, TITLE_H
    tf = ph.text_frame
    tf.word_wrap = True
    tf.text = text
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    for r in p.runs:
        r.font.size = Pt(size)
        r.font.color.rgb = NAVY
    return ph


def textbox(slide, left, top, width, height, lines, size=24, color=NAVY,
            bold_first=False, space=10, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.alignment = align
        p.space_after = Pt(space)
        for r in p.runs:
            r.font.size = Pt(size)
            r.font.color.rgb = color
            r.font.bold = bold_first and i == 0
    return box


def credit(slide, text, left=None, top=None, width=None):
    left = MARGIN if left is None else left
    top = Inches(7.02) if top is None else top
    width = SW - 2 * MARGIN if width is None else width
    box = slide.shapes.add_textbox(left, top, width, Inches(0.34))
    tf = box.text_frame
    tf.word_wrap = True
    tf.text = text
    for r in tf.paragraphs[0].runs:
        r.font.size = Pt(12)
        r.font.color.rgb = GRAY
        r.font.italic = True
    return box


def fit(box_l, box_t, box_w, box_h, native_w, native_h):
    """Letterbox a native-aspect asset into a box, centered."""
    scale = min(box_w / native_w, box_h / native_h)
    w, h = int(native_w * scale), int(native_h * scale)
    return (int(box_l + (box_w - w) / 2), int(box_t + (box_h - h) / 2), w, h)


def add_video(slide, stem, native, box, poster=None):
    left, top, w, h = fit(*box, *native)
    return slide.shapes.add_movie(
        str(MEDIA / stem), Emu(left), Emu(top), Emu(w), Emu(h),
        poster_frame_image=str(MEDIA / poster) if poster else None,
        mime_type="video/mp4",
    )


def add_image(slide, name, box):
    from PIL import Image

    with Image.open(MEDIA / name) as im:
        native = im.size
    left, top, w, h = fit(*box, *native)
    return slide.shapes.add_picture(str(MEDIA / name), Emu(left), Emu(top),
                                    Emu(w), Emu(h))


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def strip_to_emc_block(prs):
    """Delete every v1 slide except the imported EMC block, preserving XML."""
    id_lst = prs.slides._sldIdLst
    entries = list(id_lst)
    keep_ids = {entries[i - 1] for i in KEEP}
    for entry in entries:
        if entry not in keep_ids:
            rid = entry.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/"
                "relationships}id"
            )
            id_lst.remove(entry)  # unlink first so the rel refcount drops to 0
            prs.part.drop_rel(rid)
    # python-pptx names a new slide part slide<count+1>.xml rather than filling
    # gaps, so the survivors must be renumbered 1..n or new slides collide with
    # them and the package ends up with duplicate zip entries.
    from pptx.opc.packuri import PackURI

    for i, slide in enumerate(prs.slides, start=1):
        slide.part.partname = PackURI(f"/ppt/slides/slide{i}.xml")
    return len(keep_ids)


def move_block_after(prs, block_len, position):
    """Move the leading `block_len` slides to sit after `position` slides."""
    id_lst = prs.slides._sldIdLst
    entries = list(id_lst)
    block, rest = entries[:block_len], entries[block_len:]
    order = rest[:position] + block + rest[position:]
    for e in entries:
        id_lst.remove(e)
    for e in order:
        id_lst.append(e)


# --------------------------------------------------------------------------
# slide builders
# --------------------------------------------------------------------------

def s_readme(prs):
    s = title_only(prs)
    set_message(s, "How to use this supplement (delete before the talk)", 28)
    textbox(s, MARGIN, BODY_TOP, SW - 2 * MARGIN, Inches(4.4), [
        "Slides 8–18 are Sterling's EMC 2026 originals — animations intact. "
        "Copy with “Keep Source Formatting.”",
        "Every video on these slides is a real embedded clip; click to play, "
        "no internet needed.",
        "Working slides (this one, and the last two) are planning aids, not "
        "talk slides.",
    ], size=22, color=NAVY)
    notes(s, "Not a talk slide. Built by presentation/build_supplement_deck.py.")
    return s


def s_hook(prs):
    s = title_only(prs)
    set_message(s, "A tensegrity lander can hit the ground at highway speed, "
                   "bounce, and still get up.")
    add_video(s, "clip-titan-descent.mp4", (1280, 720),
              (Inches(2.15), BODY_TOP, Inches(9.0), Inches(5.0)),
              poster="poster-titan.jpg")
    credit(s, "NASA Super Ball Bot / NIAC Titan mission concept — 20 s excerpt. "
              "Credit: NASA.")
    notes(s, "Open here. Play the clip silently, say nothing for the first "
             "five seconds. Then the scope line: a printed PLA-TPU T3 prism is "
             "our proxy for developing the workflow, not flight hardware.")
    return s


def s_what_is_tensegrity(prs):
    s = title_only(prs)
    set_message(s, "Tensegrity: rigid struts that never touch each other, "
                   "held apart by cables in pure tension.")
    add_video(s, "clip-tensegrity-2d.mp4", (1280, 719),
              (Inches(2.15), BODY_TOP, Inches(9.0), Inches(5.0)),
              poster="poster-mould.jpg")
    credit(s, "Steve Mould, “Tensegrity Explained” (youtube.com/watch?v="
              "0onncd0_0-o) — 18 s excerpt, used with on-screen credit.")
    notes(s, "The 2D teaching model is the fastest way to make the mechanism "
             "obvious: push it, it springs back, nothing is glued. Say out "
             "loud that load paths are tension-only in the cables.")
    return s


def s_toy_to_lander(prs):
    s = title_only(prs)
    set_message(s, "NASA's idea started with a baby toy: throw it at the floor, "
                   "nothing breaks — that is a landing robot.")
    add_video(s, "clip-nasa-toy-lander.mp4", (1280, 720),
              (Inches(2.15), BODY_TOP, Inches(9.0), Inches(5.0)),
              poster="poster-nasa-toy.jpg")
    credit(s, "Adrian Agogino, NASA Ames — “NASA 360 Talks: Super Ball Bot” "
              "(youtube.com/watch?v=0eC4A2PXM-U), first 16 s. Credit: NASA.")
    notes(s, "PLAY THIS ONE WITH SOUND — the audio is the slide. He holds a "
             "tensegrity baby toy, says they are made as baby toys because they "
             "are almost impossible to break, throws it at the floor, and lands "
             "on “hey, that's a landing robot.” Say nothing over it; pick up "
             "with our own version of that idea. He reaches “planetary landers” "
             "verbatim a few seconds later in the source video if you ever want "
             "the longer cut (24.5-31 s).")
    return s


def s_reusable(prs):
    s = title_only(prs)
    set_message(s, "Crushable honeycomb absorbs one impact; a tensegrity "
                   "structure survives drop after drop.")
    add_video(s, "clip-superball-3m-drop.mp4", (1280, 722),
              (Inches(2.15), BODY_TOP, Inches(9.0), Inches(5.0)),
              poster="poster-superball.jpg")
    credit(s, "SUPERball v2 3.4 m drop — IEEE Spectrum / NASA Ames "
              "(youtube.com/watch?v=hkzeE6BVNIk), 10 s excerpt.")
    notes(s, "This is the reusability argument Sterling asked for: the same "
             "hardware takes the next drop. It is also why our own campaign "
             "can re-test a specimen instead of consuming it.")
    return s


def s_prior_work(prs):
    s = title_only(prs)
    set_message(s, "Tensegrity impact structures already exist — every one of "
                   "them was designed and assembled by hand.")
    textbox(s, MARGIN, BODY_TOP, Inches(11.5), Inches(4.4), [
        "NASA SUPERball v2 — hand-built, one design, no optimization loop",
        "Davami 2025 — printed tensegrity, characterized but not optimized",
        "Gu & Dotov — tensegrity crutch tip: the application pull is real",
    ], size=26)
    credit(s, "TODO before freeze: verify citations against "
              "manuscript/references.bib.")
    notes(s, "Three names, ten seconds. The point is not a literature review; "
             "it is that the design step is still manual everywhere.")
    return s


def s_gap(prs):
    s = title_only(prs)
    set_message(s, "Nobody closes the loop: print the structure, drop it, and "
                   "let the measured data choose the next design.")
    textbox(s, MARGIN, BODY_TOP, Inches(5.7), Inches(4.2), [
        "TODAY", "Hand-tuned geometry", "Simulation, rarely validated",
        "One-off demonstrations",
    ], size=26, color=GRAY, bold_first=True, space=14)
    textbox(s, Inches(7.0), BODY_TOP, Inches(5.7), Inches(4.2), [
        "THIS WORK", "The drop test is the objective",
        "Trade-offs learned from shock data", "One printer, one tower, one loop",
    ], size=26, color=BLUE, bold_first=True, space=14)
    arrow = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(6.05),
                               Inches(3.45), Inches(0.9), Inches(0.6))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = ORANGE
    arrow.line.fill.background()
    notes(s, "This is the motivation-to-gap transition. Do not read the "
             "columns; point left, point right, move on.")
    return s


def s_caveat(prs):
    s = title_only(prs)
    set_message(s, "Honest caveat, in the same breath: as printed, these are "
                   "tensegrity-inspired, not true tensegrity.")
    textbox(s, MARGIN, Inches(2.35), Inches(7.4), Inches(3.8), [
        "The black TPU members are not pre-tensioned — and they stretch.",
        "Next: pre-tensioned prints, plus hand-built true-tensegrity "
        "validation specimens.",
    ], size=26, space=26)
    add_image(s, "photo-specimen.jpg",
              (Inches(8.35), Inches(1.95), Inches(4.4), Inches(4.9)))
    credit(s, "Printed PLA–TPU T3 prism, prc1kn — frame from our own 959 fps "
              "drop footage.")
    notes(s, "Say this the moment multi-material printing appears — do not let "
             "the audience discover it in Q&A. Pair it with the path forward "
             "(issue #87 pre-tensioning) so it reads as scope, not weakness.")
    return s


def s_video_capture(prs):
    s = title_only(prs)
    set_message(s, "At 960 fps one frame is 1.04 ms — so the camera is not "
                   "here for the impact.")
    add_video(s, "clip-our-slomo-drop.mp4", (720, 720),
              (Inches(7.35), BODY_TOP, Inches(5.4), Inches(5.0)),
              poster="poster-our-drop.jpg")
    textbox(s, MARGIN, Inches(2.35), Inches(6.3), Inches(4.4), [
        "Sony RX100 IV, 959 fps",
        "It is here for the 150 ms after: rebound, sag, recovery",
        "All of that lives below 100 Hz",
    ], size=26, space=40)
    credit(s, "Our own footage: prc1kn specimen, 60 in drop, 5-felt input "
              "(data/drop-tests/prc1kn-60in-5felt/video/).")
    notes(s, "Play it once, silently. Say the honest thing out loud: 960 fps "
             "cannot resolve a 1.6 ms pulse — one frame is 1.04 ms. The "
             "accelerometer owns the pulse; the camera owns everything after "
             "it, and everything after it is slow. Resolving specimen "
             "compression *during* the pulse would need >=5000 fps DIC "
             "(docs/drop-test-prc1kn-video-analysis.md, section 3).")
    return s


def s_video_processing(prs):
    s = title_only(prs)
    set_message(s, "One clean shock, an elastic rebound, and the brake catches "
                   "the carriage 79 ms later.")
    add_image(s, "fig-video-montage.png",
              (MARGIN, Inches(1.95), SW - 2 * MARGIN, Inches(4.9)))
    credit(s, "prc1kn drop 1, 959.04 fps — contact and turnaround are "
              "consecutive frames, 1.04 ms apart.")
    notes(s, "Walk it left to right in one sentence: entry, contact, "
             "turnaround, rebound, brake catch, hold. Do not claim the "
             "montage resolves the pulse — contact and turnaround are "
             "adjacent frames. What it does prove is rig physics and specimen "
             "integrity: one shock per drop, no plastic deformation, and the "
             "anti-rebound brake catching 150 mm above the stack.")
    return s


def s_instrument_split(prs):
    s = title_only(prs)
    set_message(s, "The camera brackets the pulse in one frame; the DAQ puts "
                   "190 samples inside it.")
    add_image(s, "fig-video-impact-zoom.png",
              (MARGIN, Inches(2.00), Inches(7.5), Inches(4.85)))
    textbox(s, Inches(8.35), Inches(2.35), Inches(4.4), Inches(4.3), [
        "Camera: 1.04 ms per frame",
        "DAQ: 8 µs per sample, 1.57 ms pulse",
        "Camera still earns its keep: e* = 0.45 and a 79 ms brake catch",
    ], size=25, space=24)
    credit(s, "prc1kn drop 1, 959 fps — the entire deceleration is the single "
              "step at t = 0; the TP4 samples at 125 kHz.")
    notes(s, "This is the credibility slide, and it works by conceding the "
             "limit rather than hiding it. Point at the step: there are no "
             "camera samples inside the pulse, only on either side of it. "
             "That is why the accelerometer, not the video, produces the "
             "objectives. The camera's own deliverable is the scale-free "
             "coefficient of restitution (0.45) — a free reusability metric — "
             "plus rig physics and specimen integrity. Do not say the two "
             "instruments 'agree on the same drop': the prc1kn videos were "
             "shot ~5.5 h before that DAQ campaign, so drop-level pairing is "
             "not possible (docs/drop-test-prc1kn-video-analysis.md).")
    return s


def s_accel_setup(prs):
    s = title_only(prs)
    set_message(s, "A drop tower with an instrumented payload measures the "
                   "force that actually reaches the payload.")
    textbox(s, MARGIN, BODY_TOP, Inches(12.2), Inches(3.6), [
        "Lansmont M23 tower · Dytran 3133A4 accelerometers",
        "TP4 DAQ at 125 kHz — this is the instrument that sees the pulse",
        "Standard test: 60 in drop onto 5 felts, repeated per specimen",
    ], size=26, space=16)
    credit(s, "Setup and standard conditions per the drop-test protocol "
              "(PR #86 branch); 25 kHz is the measured floor for the current "
              "pipeline (issue #89 sample-rate study).")
    notes(s, "Add a photo of the tower here before the talk if one is "
             "available; the text is a stand-in, not a design choice.")
    return s


def s_accel_processing(prs):
    s = title_only(prs)
    set_message(s, "SAE J211 filtering turns raw ringing into the three "
                   "numbers the optimizer actually uses.")
    add_image(s, "fig-impact-zoom-cfc.png",
              (MARGIN, Inches(1.95), SW - 2 * MARGIN, Inches(2.7)))
    textbox(s, MARGIN, Inches(4.95), Inches(12.2), Inches(1.9), [
        "Peak transmitted force  ·  specific energy absorbed  ·  compaction "
        "efficiency",
    ], size=26, color=BLUE)
    credit(s, "Raw vs. CFC-1000 vs. CFC-180 on the same impact window.")
    notes(s, "Do not explain the filter classes. Say: raw data ring at "
             "mounting resonance, the standard filter removes it, and what "
             "survives is the objective function.")
    return s


def s_sensors_lied(prs):
    s = title_only(prs)
    set_message(s, "Our sensors lied to us first — cross-calibration caught a "
                   "5% error before it reached the optimizer.")
    textbox(s, MARGIN, BODY_TOP, Inches(12.2), Inches(3.6), [
        "A mis-entered sensitivity made channel 5 read 0.953× channel 4.",
        "Channel 1 was clipping at the highest drops and we could not see it.",
        "Fix: regress every channel against every other, every campaign.",
    ], size=25, space=16)
    credit(s, "Calibration story documented in PR #74.")
    notes(s, "This is the challenge slide Sterling asked to intersperse. It "
             "buys enormous credibility: we found our own error, and the "
             "cross-check is now routine.")
    return s


def s_challenges_map(prs):
    s = title_only(prs)
    set_message(s, "Working slide: challenges and where each one gets told", 28)
    textbox(s, MARGIN, BODY_TOP, Inches(12.2), Inches(4.6), [
        "Sensor sensitivity error → cross-calibration → own slide (25)",
        "Channel clipping at high drops → headroom check → spoken on slide 23",
        "No camera resolves the 1.6 ms pulse → DAQ owns it → slide 22",
        "Felt stack drifts with use → replace on schedule → spoken on slide 23",
        "Print defects confound specimens → replicates → Q&A backup",
        "Cables not in tension → pre-tensioned prints → slide 19",
    ], size=20, space=8)
    notes(s, "Planning aid. Delete before the talk.")
    return s


def s_media_shortlist(prs):
    s = title_only(prs)
    set_message(s, "Working slide: media inventory and what still needs "
                   "shooting", 28)
    textbox(s, MARGIN, BODY_TOP, Inches(12.2), Inches(4.6), [
        "EMBEDDED HERE: Titan descent · 2D tensegrity · NASA toy-to-lander "
        "(with sound) · SUPERball drop · our "
        "960 fps drop",
        "ONLINE: print timelapses on YouTube — Insert ▸ Video ▸ Online Video; "
        "keep a local copy as backup",
        "STILL NEEDED: drop-tower photo, printer bed shot, campaign ledger and "
        "Pareto-front figures",
    ], size=20, space=10)
    notes(s, "Planning aid. Delete before the talk.")
    return s


def main():
    prs = Presentation(str(SRC))
    kept = strip_to_emc_block(prs)
    print(f"kept {kept} EMC slides")

    builders = [
        s_readme, s_hook, s_what_is_tensegrity, s_toy_to_lander, s_reusable,
        s_prior_work, s_gap,
        # <- EMC block gets moved in here (position 7)
        s_caveat, s_video_capture, s_video_processing, s_instrument_split,
        s_accel_setup, s_accel_processing, s_sensors_lied,
        s_challenges_map, s_media_shortlist,
    ]
    for b in builders:
        b(prs)

    move_block_after(prs, kept, 7)
    prs.save(str(OUT))
    print(f"wrote {OUT} with {len(prs.slides.__iter__.__self__._sldIdLst)} slides")


if __name__ == "__main__":
    main()
