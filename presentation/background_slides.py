"""Background section for the IDETC supplement deck.

Sterling asked for the 2D-tensegrity teaching clip from the Box folder to be
part of the *background*, not a passing visual. That means three slides that
run before the need/gap argument:

  1. the full 35 s Steve Mould 2D demonstration, played with sound
  2. a labelled anatomy figure built from a still of the same model
  3. the print timelapse of one of our own tensegrity-inspired specimens

This module is deliberately importable rather than inlined, so it can be
developed while another job is editing ``build_supplement_deck.py``.

  python presentation/background_slides.py     # standalone preview deck
  from background_slides import BACKGROUND     # inlay into the supplement deck
"""

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches

from build_supplement_deck import (
    BODY_TOP,
    MARGIN,
    SW,
    add_image,
    add_video,
    credit,
    notes,
    set_message,
    title_only,
)

HERE = Path(__file__).parent
MEDIA = HERE / "media"
BARE = HERE / "emc2026-bare-template.pptx"
PREVIEW_OUT = HERE / "Slide Decks" / "IDETC Background Addendum.pptx"

# RGB tuples for Pillow, matching the EMC theme accents used on the slides.
ORANGE = (0xE9, 0x71, 0x32)
NAVY = (0x0E, 0x28, 0x41)
GRAY = (0x59, 0x59, 0x59)

MOULD_URL = "youtube.com/watch?v=0onncd0_0-o"
TIMELAPSE_URL = "youtube.com/watch?v=nQNmi-NiL5I"

# Composite figure geometry. The photo is a 750x770 crop of a frame from the
# Steve Mould clip; the callouts are drawn at canvas resolution so the label
# text lands at ~26 pt once the figure is placed 12 in wide on the slide.
CANVAS = (1600, 800)
PHOTO_BOX = (30, 45, 700)  # left, top, height in canvas px
LABEL_X = 800

# (anchor x, anchor y) in photo-native px; label top; heading; sub-line
CALLOUTS = [
    ((300, 165), 150, "Struts", "carry compression only"),
    ((360, 263), 320, "No strut touches another",
     "load passes through the cables"),
    ((600, 400), 500, "Cables", "carry tension only"),
]


def build_anatomy_figure(out=None):
    """Draw the labelled anatomy figure from the 2D-model still."""
    from PIL import Image, ImageDraw, ImageFont

    out = Path(out or MEDIA / "fig-tensegrity-anatomy.png")
    photo = Image.open(MEDIA / "photo-tensegrity-2d-model.jpg").convert("RGB")
    left, top, height = PHOTO_BOX
    scale = height / photo.height
    photo = photo.resize((int(photo.width * scale), height), Image.LANCZOS)

    canvas = Image.new("RGB", CANVAS, "white")
    canvas.paste(photo, (left, top))
    draw = ImageDraw.Draw(canvas)

    font_dir = "/usr/share/fonts/truetype/dejavu"
    bold = ImageFont.truetype(f"{font_dir}/DejaVuSans-Bold.ttf", 52)
    plain = ImageFont.truetype(f"{font_dir}/DejaVuSans.ttf", 44)

    for (ax, ay), ly, head, tail in CALLOUTS:
        cx, cy = left + ax * scale, top + ay * scale
        draw.line([(LABEL_X - 30, ly + 34), (cx, cy)], fill=ORANGE, width=7)
        r = 13
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ORANGE)
        draw.text((LABEL_X, ly), head, font=bold, fill=NAVY)
        draw.text((LABEL_X, ly + 66), tail, font=plain, fill=GRAY)
        for text, font in ((head, bold), (tail, plain)):
            right = LABEL_X + draw.textlength(text, font=font)
            if right > CANVAS[0] - 20:
                raise ValueError(f"callout overruns the canvas: {text!r}")

    canvas.save(out)
    return out


# --------------------------------------------------------------------------
# slide builders
# --------------------------------------------------------------------------

def s_bg_2d_model(prs):
    """The teaching clip itself — the background beat, played with sound."""
    s = title_only(prs)
    set_message(s, "A tensegrity holds itself up with rigid struts that never "
                   "touch, floating in a net of cables.")
    add_video(s, "clip-tensegrity-2d-teaching.mp4", (1280, 718),
              (Inches(2.15), BODY_TOP, Inches(9.0), Inches(5.0)),
              poster="poster-mould-teaching.jpg")
    credit(s, f"Steve Mould, “Tensegrity Explained” ({MOULD_URL}) — 35 s "
              "excerpt, played with sound, used with on-screen credit.")
    notes(s,
          "BACKGROUND, first beat. Play the whole 35 s with the sound up and "
          "stay quiet — the narration does the teaching, and the 2D model is "
          "the fastest way to make the mechanism obvious to anyone who has "
          "never seen a tensegrity.\n\n"
          "Watch for: the model standing with nothing glued or hinged; the "
          "push; the spring back. That elastic return is the whole reason a "
          "tensegrity is interesting as an energy absorber.\n\n"
          "Source: Box folder shared on PR #84 (youtube-0onncd0_0-o.mp4). "
          "Embedded locally — no internet needed at the podium.")
    return s


def s_bg_anatomy(prs):
    """Freeze the same model and name its parts."""
    s = title_only(prs)
    set_message(s, "Every load path is either pure compression in a strut or "
                   "pure tension in a cable — nothing in between.")
    add_image(s, "fig-tensegrity-anatomy.png",
              (MARGIN, BODY_TOP, SW - 2 * MARGIN, Inches(4.85)))
    credit(s, f"Still from the same clip — Steve Mould, “Tensegrity "
              f"Explained” ({MOULD_URL}).")
    notes(s,
          "BACKGROUND, second beat. Freeze the model and name the parts, so "
          "the vocabulary is in place before the caveat slide later on.\n\n"
          "Say: this is why a tensegrity can be light and still stiff — no "
          "member ever sees a bending moment, and the cables set the "
          "stiffness. It is also why the geometry matters so much: change a "
          "strut length or a cable pre-tension and the whole response "
          "changes, which is exactly what makes it an optimization problem.\n\n"
          "This is the mechanism visual the mock audience said the grad "
          "student needed in order to tell a tensegrity from a lattice.")
    return s


def s_bg_print_timelapse(prs):
    """Our own specimen, printed in one build — the bridge out of background."""
    s = title_only(prs)
    set_message(s, "We print our version in one build: PLA struts and TPU "
                   "members laid down together, with no assembly.")
    add_video(s, "clip-print-timelapse.mp4", (1120, 720),
              (Inches(2.65), BODY_TOP, Inches(8.0), Inches(5.0)),
              poster="poster-print-timelapse.jpg")
    credit(s, f"BYU Vertical Cloud Lab — 16 s timelapse of a T3 specimen "
              f"({TIMELAPSE_URL}).")
    notes(s,
          "BACKGROUND, third beat, and the bridge into the method: this is "
          "the object every later slide is about. Black is PLA (the struts), "
          "orange is TPU (the tension members); the tall column at the back "
          "is the purge tower the printer needs when it swaps filaments.\n\n"
          "Say it in the same breath as the caveat slide: printed like this, "
          "the TPU members are not pre-tensioned and not inextensible, so "
          "these are tensegrity-INSPIRED structures, not true tensegrities. "
          "We are working on pre-tensioned prints and hand-built validation "
          "specimens (issue #87).\n\n"
          "Downloaded from our own YouTube channel through the lab Raspberry "
          "Pi; the file is embedded, so it plays with no internet.")
    return s


BACKGROUND = [s_bg_2d_model, s_bg_anatomy, s_bg_print_timelapse]


def main():
    build_anatomy_figure()
    prs = Presentation(str(BARE))
    for b in BACKGROUND:
        b(prs)
    PREVIEW_OUT.parent.mkdir(exist_ok=True)
    prs.save(str(PREVIEW_OUT))
    print(f"wrote {PREVIEW_OUT} with {len(prs.slides._sldIdLst)} slides")


if __name__ == "__main__":
    main()
