#!/usr/bin/env python3
"""Fetch and process the real workflow/specimen photographs used in the
manuscript figures from the project's GitHub issue & PR comment history.

Each image was located by scanning every issue/PR comment body for image URLs
(GitHub ``user-attachments`` uploads and committed-blob ``?raw=true`` links).
The exact source comment for each photo is recorded in the ``SOURCES`` table
below and mirrored in ``figures/photos/README.md``.

The script re-downloads each original and re-applies the same crop / EXIF
orientation correction (phone photos carry EXIF orientation that ``pdflatex``
ignores, so it must be baked in) to regenerate the cropped copies in
``figures/photos/``.

Requirements:
  * the GitHub CLI (``gh``) authenticated against the repository, used only to
    mint a token for the authenticated downloads (``gh auth token``); set
    ``GH_TOKEN``/``GITHUB_TOKEN`` to skip the ``gh`` dependency.
  * Pillow (``pip install Pillow``).

Usage:
  python scripts/figures/fetch_repo_photos.py
"""
from __future__ import annotations

import io
import os
import subprocess
import sys

from PIL import Image, ImageChops, ImageOps

REPO = "vertical-cloud-lab/tensegrity-optimization"

# Destination relative to the repository root.
DST = os.path.join(os.path.dirname(__file__), "..", "..", "figures", "photos")

# Each entry: output file -> (source URL, source comment, crop/resize spec).
#   crop: optional (l, t, r, b) as fractions of width/height (None = no crop).
#   maxw: max output width in px.
SOURCES = {
    "cad-render.png": {
        "url": "https://github.com/vertical-cloud-lab/tensegrity-optimization"
               "/blob/d4431b0/cad/t3-prism/t3-prism-iso.png?raw=true",
        "comment": "PR #35 comment 4513151049 (OpenSCAD T3-prism iso render)",
        "trim_bg": (245, 245, 245),
        "maxw": 600,
    },
    "multimaterial-slice.png": {
        "url": "https://github.com/user-attachments/assets/"
               "9b03f81c-7343-4fcd-a027-d2a435c68f74",
        "comment": "PR #35 comment 4464541324 (Bambu Studio dual-nozzle slice)",
        "maxw": 1400,
    },
    "printing-in-progress.jpg": {
        "url": "https://github.com/user-attachments/assets/"
               "fae2c851-09d3-40ae-946c-8770fafdd387",
        "comment": "PR #35 comment 4519769283 (Bambu Lab H2D mid-print)",
        "maxw": 1400,
    },
    "printed-specimen.jpg": {
        "url": "https://github.com/user-attachments/assets/"
               "c2ee2b2d-db35-40d6-8122-78aa6196b94e",
        "comment": "PR #35 comment 4634008108 (single as-printed T3 prism)",
        "crop": (0.08, 0.22, 0.88, 0.72),
        "maxw": 1200,
    },
    "printed-batch.jpg": {
        "url": "https://github.com/user-attachments/assets/"
               "547f3657-002d-47e9-b9e9-6cf689a7b6af",
        "comment": "PR #35 comment 4634008108 (printed batch)",
        "maxw": 1400,
    },
    "drop-tower.jpg": {
        "url": "https://github.com/user-attachments/assets/"
               "cbca1c5f-5f4b-4e15-938e-ef43aa906813",
        "comment": "PR #36 comment 4509083060 (bungee-assisted drop tower)",
        "crop": (0.0, 0.02, 1.0, 0.97),
        "maxw": 1400,
    },
}


def _token() -> str:
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:  # pragma: no cover
        raise SystemExit(
            "No GH_TOKEN/GITHUB_TOKEN set and `gh auth token` failed; "
            "authenticate the GitHub CLI or export a token."
        ) from exc


def _download(url: str, token: str) -> Image.Image:
    # Committed-blob links (github.com/<repo>/blob/<ref>/<path>?raw=true) must be
    # fetched via raw.githubusercontent.com; the github.com host rejects token
    # auth on the raw redirect with HTTP 400.
    if "/blob/" in url and url.startswith("https://github.com/"):
        rest = url[len("https://github.com/"):].split("?", 1)[0]
        url = "https://raw.githubusercontent.com/" + rest.replace("/blob/", "/", 1)
    # Use curl -L: user-attachment URLs 302-redirect to a signed object-store
    # host that rejects the GitHub token, and curl (unlike urllib) drops the
    # Authorization header when the redirect crosses hosts.
    data = subprocess.check_output(
        ["curl", "-sL", "--fail", "-H", f"Authorization: token {token}", url]
    )
    return ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")


def _trim(img: Image.Image, bg_rgb, pad: int = 20) -> Image.Image:
    bg = Image.new("RGB", img.size, tuple(bg_rgb))
    bbox = ImageChops.difference(img, bg).getbbox()
    if not bbox:
        return img
    l, t, r, b = bbox
    return img.crop((max(0, l - pad), max(0, t - pad),
                     min(img.width, r + pad), min(img.height, b + pad)))


def _crop(img: Image.Image, frac) -> Image.Image:
    w, h = img.size
    l, t, r, b = frac
    return img.crop((int(w * l), int(h * t), int(w * r), int(h * b)))


def _save(img: Image.Image, name: str, maxw: int) -> None:
    if img.width > maxw:
        img = img.resize((maxw, round(img.height * maxw / img.width)),
                         Image.LANCZOS)
    path = os.path.join(DST, name)
    if name.endswith((".jpg", ".jpeg")):
        img.save(path, quality=88, optimize=True)
    else:
        img.save(path, optimize=True)
    print(f"  wrote {name} {img.size} ({os.path.getsize(path) // 1024} KB)")


def main() -> int:
    os.makedirs(DST, exist_ok=True)
    token = _token()
    for name, spec in SOURCES.items():
        print(f"{name}  <-  {spec['comment']}")
        img = _download(spec["url"], token)
        if "trim_bg" in spec:
            img = _trim(img, spec["trim_bg"])
        if "crop" in spec:
            img = _crop(img, spec["crop"])
        _save(img, name, spec["maxw"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
