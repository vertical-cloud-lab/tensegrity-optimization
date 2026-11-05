#!/usr/bin/env python3
"""Build the replicate-specimen photo panel (3 designs x 4 prints).

Rows are the three designs of the replicate study (corny7 / trial 37,
corny8 / trial 39, corny2 / trial 38). Columns are the batch-4 specimen
of each design (print log of 2026-09-11) and the front-row copy (copy 3) of
each design on replicate plates 1, 2 and 3 (print log of 2026-10-17).
Specimen IDs follow ``bo/replicate-study/t3-prism-replicate-print-key.csv``
on the campaign branch (``<plate>sne<design digit><copy>``).

Photos and weighed masses come from the print log on issue #98. The
script parses every ``ID:`` / ``Mass:`` / ``<img src>`` triplet of the
four comments below, so the masses printed under each cell are read from
the log rather than typed in here. The photos are only EXIF-transposed,
cropped, rotated and down-scaled; labels are drawn in the margins.

Usage::

    python -P scripts/figures/build_replicate_photo_panel.py \
        [--cache /tmp/replicate-photos] [--out figures/photos/replicate-specimens-panel.jpg]

    # Contact sheet of the uncropped (transposed) photos, for tuning CROPS:
    python -P scripts/figures/build_replicate_photo_panel.py --contact /tmp/contact.jpg

Downloads go to the cache directory (outside the repo); the full-size
phone photos are not committed. Comments are fetched with ``gh api``
(falls back to the GitHub REST API with ``GH_TOKEN`` / ``GITHUB_TOKEN``).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

REPO = "vertical-cloud-lab/tensegrity-optimization"
ROOT = Path(__file__).resolve().parents[2]

# Issue #98 print-log comments (provenance).
COMMENT_BATCH4 = 5637649574  # 2026-09-11, corny1 to corny9
COMMENT_PLATE1 = 6240858848  # 2026-10-17, 1sne21 to 1sne83
COMMENT_PLATE2 = 6241852209  # 2026-10-17, 2sne21 to 2sne83
COMMENT_PLATE3 = 6241963239  # 2026-10-17, 3sne21 to 3sne83
COMMENTS = (COMMENT_BATCH4, COMMENT_PLATE1, COMMENT_PLATE2, COMMENT_PLATE3)

# (design, trial, design digit used in the replicate IDs)
ROWS = [("corny7", 37, 7), ("corny8", 39, 8), ("corny2", 38, 2)]

COLUMNS = [
    ("Batch 4", "2026-09-11", lambda d, digit: d),
    ("Replicate 1", "2026-10-17", lambda d, digit: f"1sne{digit}3"),
    ("Replicate 2", "2026-10-17", lambda d, digit: f"2sne{digit}3"),
    ("Replicate 3", "2026-10-17", lambda d, digit: f"3sne{digit}3"),
]

# Crop boxes as fractions (left, top, right, bottom) of the EXIF-transposed
# photo, then an optional rotation in degrees (counter-clockwise, applied
# after cropping, multiples of 90 only so no resampling of the content).
CROPS: dict[str, tuple[tuple[float, float, float, float], int]] = {
    # Equal width and height fractions keep the photo's 3:4 aspect, so the
    # cell resize below only down-scales. All twelve photos are upright
    # after the EXIF transpose, so no rotation is needed.
    "corny7": ((0.140, 0.140, 0.920, 0.920), 0),
    "1sne73": ((0.093, 0.083, 0.908, 0.898), 0),
    "2sne73": ((0.080, 0.095, 0.880, 0.895), 0),
    "3sne73": ((0.065, 0.045, 0.875, 0.855), 0),
    "corny8": ((0.078, 0.113, 0.893, 0.928), 0),
    "1sne83": ((0.130, 0.160, 0.930, 0.960), 0),
    "2sne83": ((0.056, 0.029, 0.909, 0.882), 0),
    "3sne83": ((0.040, 0.030, 0.900, 0.890), 0),
    "corny2": ((0.075, 0.170, 0.885, 0.980), 0),
    "1sne23": ((0.070, 0.165, 0.900, 0.995), 0),
    "2sne23": ((0.065, 0.100, 0.875, 0.910), 0),
    "3sne23": ((0.048, 0.100, 0.868, 0.920), 0),
}

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
ENTRY_RE = re.compile(
    r"ID:\s*(?P<id>[A-Za-z0-9]+)\s*\n"
    r"Mass:\s*(?P<mass>[0-9.]+)\s*g.*?"
    r"<img[^>]*src=\"(?P<url>https://github\.com/user-attachments/assets/[0-9a-f-]+)\"",
    re.S,
)


def fetch_comment(cid: int, cache: Path) -> dict:
    path = cache / f"comment-{cid}.json"
    if not path.exists():
        url = f"repos/{REPO}/issues/comments/{cid}"
        if shutil.which("gh"):
            out = subprocess.run(["gh", "api", url], check=True, capture_output=True, text=True).stdout
        else:
            req = urllib.request.Request(f"https://api.github.com/{url}")
            tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
            if tok:
                req.add_header("Authorization", f"Bearer {tok}")
            out = urllib.request.urlopen(req, timeout=60).read().decode()
        path.write_text(out)
    return json.loads(path.read_text())


def parse_log(cache: Path) -> dict[str, dict]:
    """Map specimen ID -> {mass_g, url, comment, date} from the four comments."""
    entries: dict[str, dict] = {}
    for cid in COMMENTS:
        c = fetch_comment(cid, cache)
        body = c["body"].replace("\r\n", "\n")
        for m in ENTRY_RE.finditer(body):
            sid = m["id"]
            if sid in entries:
                raise SystemExit(f"duplicate print-log entry for {sid}")
            entries[sid] = {
                "mass_g": float(m["mass"]),
                "mass_str": m["mass"],
                "url": m["url"],
                "comment": cid,
                "date": c["created_at"][:10],
            }
    return entries


def download(url: str, dest: Path) -> Path:
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    headers = {"User-Agent": "tensegrity-optimization-figure-script"}
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    req = urllib.request.Request(url, headers=headers)
    try:
        data = urllib.request.urlopen(req, timeout=120).read()
    except Exception:
        if not tok:
            raise
        req.add_header("Authorization", f"token {tok}")
        data = urllib.request.urlopen(req, timeout=120).read()
    tmp = dest.with_suffix(".part")
    tmp.write_bytes(data)
    tmp.rename(dest)
    return dest


def load_photo(sid: str, entries: dict, cache: Path) -> Image.Image:
    e = entries[sid]
    raw = download(e["url"], cache / f"{sid}.img")
    with Image.open(raw) as im:
        im = ImageOps.exif_transpose(im)
        return im.convert("RGB")


def crop_photo(im: Image.Image, sid: str) -> Image.Image:
    (l, t, r, b), rot = CROPS[sid]
    w, h = im.size
    out = im.crop((round(l * w), round(t * h), round(r * w), round(b * h)))
    if rot:
        out = out.rotate(rot, expand=True)
    return out


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), size)


def text_center(draw, cx, y, s, f, fill=(0, 0, 0)):
    w = draw.textlength(s, font=f)
    draw.text((cx - w / 2, y), s, font=f, fill=fill)


def build_panel(entries: dict, cache: Path, out: Path) -> None:
    # Sized so the labels stay near 6 pt or more when the panel is set
    # one column (3.4 in) wide: 2240 px over 3.4 in is about 660 px/in.
    cell_w, cell_h = 520, 693  # 3:4 portrait cells
    gap = 14
    left = 96  # rotated row labels
    top = 150  # column headers (print and date)
    under = 140  # two-line label under each cell (ID, weighed mass)
    ncol, nrow = len(COLUMNS), len(ROWS)
    W = left + ncol * cell_w + (ncol - 1) * gap + 8
    H = top + nrow * (cell_h + under) + (nrow - 1) * gap + 14
    canvas = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(canvas)
    f_head, f_sub = font(66, True), font(56)
    f_id, f_mass = font(62, True), font(56)

    for j, (head, sub, _) in enumerate(COLUMNS):
        cx = left + j * (cell_w + gap) + cell_w / 2
        text_center(d, cx, 4, head, f_head)
        text_center(d, cx, 78, sub, f_sub, fill=(70, 70, 70))

    for i, (design, trial, digit) in enumerate(ROWS):
        y0 = top + i * (cell_h + under + gap)
        # Row label, rotated to read bottom to top in the left margin.
        row = f"{design}, trial {trial}"
        tw = int(d.textlength(row, font=f_head)) + 8
        strip = Image.new("RGB", (tw, 84), "white")
        ImageDraw.Draw(strip).text((4, 4), row, font=f_head, fill=(0, 0, 0))
        strip = strip.rotate(90, expand=True)
        canvas.paste(strip, (6, int(y0 + cell_h / 2 - tw / 2)))
        for j, (_, _, sid_of) in enumerate(COLUMNS):
            sid = sid_of(design, digit)
            if sid not in entries:
                raise SystemExit(f"{sid} missing from the print log")
            im = crop_photo(load_photo(sid, entries, cache), sid)
            im = ImageOps.fit(im, (cell_w, cell_h), method=Image.LANCZOS)
            x0 = left + j * (cell_w + gap)
            canvas.paste(im, (x0, y0))
            cx = x0 + cell_w / 2
            text_center(d, cx, y0 + cell_h + 6, sid, f_id)
            text_center(d, cx, y0 + cell_h + 72, f"{entries[sid]['mass_str']} g", f_mass)

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=88, optimize=True)
    print(f"wrote {out} ({canvas.size[0]}x{canvas.size[1]}, {out.stat().st_size / 1e6:.2f} MB)")


def contact_sheet(entries: dict, cache: Path, out: Path) -> None:
    ids = [sid_of(d, g) for (d, _, g) in ROWS for (_, _, sid_of) in COLUMNS]
    thumbs = []
    for sid in ids:
        im = crop_photo(load_photo(sid, entries, cache), sid)
        im.thumbnail((400, 533))
        thumbs.append((sid, im))
    W, H = 4 * 410, 3 * 573
    sheet = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(sheet)
    for k, (sid, im) in enumerate(thumbs):
        x, y = (k % 4) * 410, (k // 4) * 573
        sheet.paste(im, (x, y))
        d.text((x + 4, y + 535), sid, font=font(28, True), fill=(200, 0, 0))
    sheet.save(out, quality=85)
    print(f"wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cache", type=Path, default=Path("/tmp/replicate-photos"))
    ap.add_argument("--out", type=Path, default=ROOT / "figures/photos/replicate-specimens-panel.jpg")
    ap.add_argument("--contact", type=Path, help="write a contact sheet of the current crops and exit")
    args = ap.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)

    entries = parse_log(args.cache)
    for design, _, digit in ROWS:
        for _, _, sid_of in COLUMNS:
            sid = sid_of(design, digit)
            e = entries[sid]
            print(f"{sid:7s} {e['mass_str']:>6s} g  comment {e['comment']} ({e['date']})")

    if args.contact:
        contact_sheet(entries, args.cache, args.contact)
    else:
        build_panel(entries, args.cache, args.out)


if __name__ == "__main__":
    main()
