"""Crop each highlight from Audrey's annotated PDF, outline it in red, and
add a caption strip with her note, plus a numbered page-1 overview."""
import sys, textwrap
import pymupdf
from PIL import Image, ImageDraw, ImageFont

PDF, OUT = sys.argv[1], sys.argv[2]
DPI = 300
S = DPI / 72.0
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# reading order: (item number, slug, [annotation xrefs], crop x-range in pt, where)
ITEMS = [
    (1, "author-block-addresses", [914], (60, 222), "title block, left column"),
    (2, "abstract-pla", [918], (222, 582), "abstract, line iv"),
    (3, "abstract-tpu", [919], (222, 582), "abstract, line iv"),
    (4, "abstract-rescaled", [908], (222, 582), "abstract, line vi"),
    (5, "abstract-printed", [909], (222, 582), "abstract, line vi"),
    (6, "abstract-seed-article", [910], (222, 582), "abstract, lines vi to vii"),
    (7, "abstract-transmissibility-definition", [911], (222, 582), "abstract, lines vii to viii"),
    (8, "abstract-velocity-loss-index", [912], (222, 582), "abstract, line viii"),
    (9, "abstract-printed-articles", [913], (222, 582), "abstract, line ix"),
    (10, "abstract-35-articles", [920], (222, 582), "abstract, line x"),
    (11, "abstract-fourth-batch", [915], (222, 582), "abstract, line xii"),
    (12, "abstract-best-seed-article", [916], (222, 582), "abstract, line xiii"),
    (13, "abstract-three-prints-sentence", [917], (222, 582), "abstract, lines xiii to xv"),
    (14, "intro-defining-property", [921, 922], (50, 312), "Introduction, line 5"),
]

doc = pymupdf.open(PDF)
page = doc[0]
annots = {a.xref: a for a in page.annots()}

def quads(xref):
    v = annots[xref].vertices
    return [pymupdf.Quad(v[i:i + 4]).rect for i in range(0, len(v), 4)]

def note(xref):
    return (annots[xref].info.get("content") or "").strip()

pix = page.get_pixmap(dpi=DPI, annots=True)
full = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

def outline(draw, rects, width=5, color=(220, 30, 30)):
    for r in rects:
        draw.rectangle([r.x0 * S - 4, r.y0 * S - 3, r.x1 * S + 4, r.y1 * S + 3], outline=color, width=width)

font = ImageFont.truetype(FONT, 30)
fontb = ImageFont.truetype(FONTB, 30)
records = []
for num, slug, xrefs, (cx0, cx1), where in ITEMS:
    rects = [q for x in xrefs for q in quads(x)]
    y0 = min(r.y0 for r in rects); y1 = max(r.y1 for r in rects)
    pad_above, pad_below = (12, 12) if num == 1 else (22, 22)
    img = full.copy()
    d = ImageDraw.Draw(img)
    if num == 1:
        # outline the whole author block once rather than 56 line quads
        u = rects[0]
        for r in rects[1:]:
            u = u | r
        outline(d, [u])
    else:
        outline(d, rects)
    box = (int(cx0 * S), int(max(0, y0 - pad_above) * S), int(cx1 * S), int(min(page.rect.y1, y1 + pad_below) * S))
    crop = img.crop(box)
    # caption strip with the note text
    texts = [note(x) for x in xrefs if note(x)]
    wrap_w = max(30, int(crop.width / 17))
    if texts:
        cap = "Audrey's note: " + " ".join(texts[-1].split())
    else:
        cap = "Highlight only, no comment attached."
    lines = [f"Item {num} ({where})"] + textwrap.wrap(cap, wrap_w)
    lh = 40
    strip = Image.new("RGB", (crop.width, lh * len(lines) + 24), (255, 248, 220))
    sd = ImageDraw.Draw(strip)
    for i, ln in enumerate(lines):
        sd.text((14, 12 + i * lh), ln, fill=(20, 20, 20), font=fontb if i == 0 else font)
    out = Image.new("RGB", (crop.width, crop.height + strip.height), (255, 255, 255))
    out.paste(crop, (0, 0)); out.paste(strip, (0, crop.height))
    path = f"{OUT}/{num:02d}-{slug}.png"
    out.save(path, optimize=True)
    records.append((num, path, [round(v, 1) for v in (y0, y1)]))
    print(num, path, out.size)

# overview: whole page 1, every item outlined and numbered
ov = full.copy()
d = ImageDraw.Draw(ov)
fnum = ImageFont.truetype(FONTB, 34)
for num, slug, xrefs, _, _ in ITEMS:
    rects = [q for x in xrefs for q in quads(x)]
    if num == 1:
        u = rects[0]
        for r in rects[1:]:
            u = u | r
        rects = [u]
    outline(d, rects, width=4)
    r0 = rects[0]
    cx, cy = r0.x0 * S - 4, r0.y0 * S - 26
    if num == 1:
        cx, cy = r0.x0 * S - 60, r0.y0 * S + 10
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(220, 30, 30))
    tw = d.textlength(str(num), font=fnum)
    d.text((cx - tw / 2, cy - 20), str(num), fill="white", font=fnum)
ov = ov.crop((0, int(40 * S), ov.width, int(650 * S)))
ov = ov.resize((ov.width // 2, ov.height // 2), Image.LANCZOS)
ov.save(f"{OUT}/00-page1-overview.jpg", quality=88, optimize=True)
print("overview", ov.size)
