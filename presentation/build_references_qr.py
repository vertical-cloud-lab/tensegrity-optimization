"""Generate the QR code for the slide reference list.

Regenerate after the PR merges so the code points at main instead of the
working branch:

    python presentation/build_references_qr.py --branch main
"""

import argparse

import qrcode
from qrcode.constants import ERROR_CORRECT_Q

REPO = "vertical-cloud-lab/tensegrity-optimization"
DOC = "presentation/slide-references.md"
OUT = "presentation/media/qr-slide-references.png"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", default="claude/issue-83-20260715-2018")
    args = parser.parse_args()

    url = f"https://github.com/{REPO}/blob/{args.branch}/{DOC}"
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=16, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(OUT)
    print(f"wrote {OUT} ({img.size[0]}x{img.size[1]} px) -> {url}")


if __name__ == "__main__":
    main()
