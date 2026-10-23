"""Stack the head abstract (with Sterling's 95b331e edit) over the proposed
abstract, each labeled, for the review sheet."""
import sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
head_pdf, prop_pdf, out = sys.argv[1:4]
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fb = ImageFont.truetype(FONTB, 21)
def grab(pdf, clip):
    d = pymupdf.open(pdf)
    pix = d[0].get_pixmap(dpi=200, clip=clip)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
clip = pymupdf.Rect(222, 182, 582, 372)
a = grab(head_pdf, clip); b = grab(prop_pdf, clip)
def label(img, text, color):
    strip = Image.new("RGB", (img.width, 46), color)
    ImageDraw.Draw(strip).text((12, 8), text, fill="white", font=fb)
    out = Image.new("RGB", (img.width, img.height + 46), "white")
    out.paste(strip, (0, 0)); out.paste(img, (0, 46))
    return out
a = label(a, "Now: branch head 5f260c8, with the 95b331e edit (174 words)", (90, 90, 90))
b = label(b, "Proposed: Audrey's items, recommended options (196 words)", (30, 110, 60))
W = max(a.width, b.width)
canvas = Image.new("RGB", (W, a.height + b.height + 20), "white")
canvas.paste(a, (0, 0)); canvas.paste(b, (0, a.height + 20))
canvas.save(out, optimize=True)
# intro sentence comparison
clip2 = pymupdf.Rect(50, 0, 312, 0)
def grab_intro(pdf):
    d = pymupdf.open(pdf); p = d[0]
    hits = p.search_for("Tensegrity structures are assemblies")
    r = hits[0]
    c = pymupdf.Rect(50, r.y0 - 4, 312, r.y0 + 54)
    pix = p.get_pixmap(dpi=200, clip=c)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
c1 = label(grab_intro(head_pdf), "Head now", (90, 90, 90))
c2 = label(grab_intro(prop_pdf), "Proposed (item 14)", (30, 110, 60))
canvas2 = Image.new("RGB", (max(c1.width, c2.width), c1.height + c2.height + 16), "white")
canvas2.paste(c1, (0, 0)); canvas2.paste(c2, (0, c1.height + 16))
canvas2.save(out.replace(".png", "-intro.png"), optimize=True)
print("ok", canvas.size, canvas2.size)
