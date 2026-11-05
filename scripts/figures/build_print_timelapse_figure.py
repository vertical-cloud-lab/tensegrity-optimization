#!/usr/bin/env python3
"""Build the print-timelapse figure: three frames of replicate plate 1.

Source video: YouTube ``EmCLms7-Bd8``, "TT3_01 1sne## plate", uploaded
2026-10-12 by BYU Vertical Cloud Lab (15.7 s, 1680 x 1080, 24 fps; the
description carries the printer's timelapse file stamp
``video 2026 10 03 06 17 10``). It is the Bambu Lab H2D chamber-camera
timelapse of the first replicate-study plate (specimens 1sne21 to 1sne83,
print key ``bo/replicate-study/t3-prism-replicate-print-key.csv`` on the
campaign branch). The printer parks the toolhead at the rear of the
chamber for each timelapse frame, so no frame shows it over the
specimens. It is the only plate timelapse in the record without the
toolhead in view.

The script only seeks, crops and down-scales. It applies no color,
contrast or sharpening edits. Only the extracted frames are committed;
the video itself stays out of the repository (see ``.gitignore``).

YouTube blocks most datacenter IP ranges, so ``--download`` may fail on a
CI runner. In that case fetch the video on a residential connection
(format 137, H.264 1680 x 1080) and pass it with ``--video``.

Requirements: ``ffmpeg`` on PATH, Pillow, and ``yt-dlp`` for ``--download``.

Usage:
  python scripts/figures/build_print_timelapse_figure.py --video EmCLms7-Bd8.mp4
  python scripts/figures/build_print_timelapse_figure.py --download

Outputs (relative to the repository root):
  figures/photos/timelapse/plate1-01-first-layers.jpg
  figures/photos/timelapse/plate1-02-mid-height.jpg
  figures/photos/timelapse/plate1-03-final-layers.jpg
  figures/photos/print-timelapse-plate1.jpg   (three frames side by side)
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

VIDEO_ID = "EmCLms7-Bd8"
VIDEO_URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"
YTDLP_FORMAT = "137"  # H.264 1680 x 1080, 24 fps, about 7.6 MB

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "figures", "photos", "timelapse")
COMPOSITE = os.path.join(ROOT, "figures", "photos", "print-timelapse-plate1.jpg")

# (output name, seek time in s, crop, panel label). Times chosen by
# inspecting the frames: 0.75 s is the first frame after the chamber light
# settles that shows the bottom TPU tendon triangles and strut-end
# housings; 7.0 s has the struts at about half height; 15.5 s is the last
# full frame, with the top tendon triangles complete.
#
# Crops are (left, top, right, bottom) pixels in the 1680 x 1080 source,
# all at the same 12:7 aspect ratio. The bed drops as the print grows, so
# early layers sit near the top of the frame and get a tighter crop. Each
# crop leaves out most of the parked toolhead and gantry at the top and
# the chamber walls at the sides.
FRAMES = [
    ("plate1-01-first-layers.jpg", 0.75, (240, 215, 1440, 915),
     "(a) First layers"),
    ("plate1-02-mid-height.jpg", 7.0, (120, 240, 1560, 1080),
     "(b) Mid-height"),
    ("plate1-03-final-layers.jpg", 15.5, (120, 240, 1560, 1080),
     "(c) Final layers"),
]
FRAME_WIDTH = 960  # px after down-scaling (about 1.47:1 aspect)
JPEG_QUALITY = 88

LABEL_STRIP = 54  # px of white margin under each frame for its label
GUTTER = 14  # px between panels
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def download(dest_dir: str) -> str:
    """Fetch the video with yt-dlp into ``dest_dir`` and return its path."""
    out = os.path.join(dest_dir, f"{VIDEO_ID}.mp4")
    cmd = ["yt-dlp", "-f", YTDLP_FORMAT, "--no-part", "-o", out, VIDEO_URL]
    subprocess.run(cmd, check=True)
    return out


def grab(video: str, t: float, dest: str) -> None:
    """Write the frame at ``t`` seconds to ``dest`` as a lossless PNG."""
    cmd = [
        "ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video,
        "-frames:v", "1", dest,
    ]
    subprocess.run(cmd, check=True)


def load_font(size: int) -> ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--video", help="path to a local copy of the video")
    src.add_argument("--download", action="store_true",
                     help="fetch the video with yt-dlp into a temp dir")
    args = ap.parse_args()

    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found on PATH")

    os.makedirs(OUT_DIR, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        video = download(tmp) if args.download else args.video
        panels = []
        for name, t, crop, label in FRAMES:
            raw = os.path.join(tmp, f"frame-{t:.2f}.png")
            grab(video, t, raw)
            im = Image.open(raw).convert("RGB")
            if im.size != (1680, 1080):
                sys.exit(f"unexpected frame size {im.size}; expected 1680 x 1080")
            im = im.crop(crop)
            h = round(im.height * FRAME_WIDTH / im.width)
            im = im.resize((FRAME_WIDTH, h), Image.LANCZOS)
            path = os.path.join(OUT_DIR, name)
            im.save(path, quality=JPEG_QUALITY, optimize=True)
            print(f"wrote {os.path.relpath(path, ROOT)} (t = {t:.2f} s)")
            panels.append((im, label))

    # Composite: frames side by side, labels in a white strip underneath.
    w, h = panels[0][0].size
    canvas = Image.new(
        "RGB", (3 * w + 2 * GUTTER, h + LABEL_STRIP), "white")
    draw = ImageDraw.Draw(canvas)
    font = load_font(34)
    for i, (im, label) in enumerate(panels):
        x0 = i * (w + GUTTER)
        canvas.paste(im, (x0, 0))
        tw = draw.textlength(label, font=font)
        draw.text((x0 + (w - tw) / 2, h + 8), label, fill="black", font=font)
    canvas.save(COMPOSITE, quality=JPEG_QUALITY, optimize=True)
    print(f"wrote {os.path.relpath(COMPOSITE, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
