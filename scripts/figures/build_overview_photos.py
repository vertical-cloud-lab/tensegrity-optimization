#!/usr/bin/env python3
"""Crop the panels of the overview loop (fig:overview) from committed images.

Sources live in figures/photos/overview-src/ (downscaled copies of the
originals, provenance in figures/photos/README.md) plus the proposal's
overview figure, figures/overview-updated.png, whose Bayesian-optimization
panel is reused unchanged as the Design panel. Crops are fractions of each
source's width and height, so they survive re-downscaling. Writes
figures/photos/overview/*.jpg (and the BO panel as .png), which
figures/overview-loop.tex includes.

Usage:  python3 scripts/figures/build_overview_photos.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "figures" / "photos" / "overview-src"
OUT = REPO / "figures" / "photos" / "overview"

# name: (source, (left, top, right, bottom) as fractions, max output width px)
PANELS = {
    "design-bo-panel": (REPO / "figures" / "overview-updated.png",
                        (2080 / 6000, 85 / 5118, 5120 / 6000, 1248 / 5118), 1400),
    "make-plate-render": (SRC / "batch4-plate-render.png",
                          (0.2417, 0.2182, 0.7792, 0.7818), 700),
    "make-painted-supports": (SRC / "painted-supports-slice.png",
                              (0.2390, 0.1664, 0.8363, 1.0000), 700),
    "make-h2d-midprint": (SRC / "h2d-midprint-replicate-plate1.jpg",
                          (0.3125, 0.0714, 0.8646, 0.8036), 700),
    "test-taped-batch": (SRC / "taped-batch2.jpg",
                         (0.0887, 0.0980, 0.8917, 0.7003), 900),
    "test-carriage": (SRC / "carriage-specimen-mdt6ja.jpg",
                      (0.3137, 0.0172, 0.6853, 0.7118), 700),
}


def crop(src: Path, box, max_w: int) -> Image.Image:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    l, t, r, b = box
    im = im.crop((round(l * w), round(t * h), round(r * w), round(b * h)))
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    return im


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (src, box, max_w) in PANELS.items():
        im = crop(src, box, max_w)
        if name == "design-bo-panel":
            path = OUT / f"{name}.png"
            im.save(path, optimize=True)
        else:
            path = OUT / f"{name}.jpg"
            im.save(path, quality=90)
        print(f"{path.relative_to(REPO)}  {im.size}")
    # corny7 photo for fig:design-space, panel (c)
    im = crop(SRC / "corny7-asprinted.jpg", (0.1821, 0.1663, 0.8730, 0.8929), 900)
    path = REPO / "figures" / "photos" / "corny7-asprinted.jpg"
    im.save(path, quality=90)
    print(f"{path.relative_to(REPO)}  {im.size}")


if __name__ == "__main__":
    main()
