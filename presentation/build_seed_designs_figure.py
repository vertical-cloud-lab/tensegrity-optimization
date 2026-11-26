"""Build the nine-seed-designs figure for the IDETC slide deck.

All nine campaign seed designs (S0, then Sobol specimens 1 to 8, i.e.
the rows of bo/t3-prism-bo-batch.csv) on one full-bleed slide, drawn in
the same rendering style as the search-space GIFs, on one common mm
scale, in specimen order left to right, top to bottom. No dials and no
text, per PR #84 (me-madsen, 2026-08-20).

Geometry, colors, and the depth-sorted renderer come from
build_search_space_figure.py; the seed values from
build_designs_tour_gif.py, so the still and the tour GIF cannot drift
apart.

Output: presentation/media/fig-seed-designs.png (16:9, for a full slide).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from build_designs_tour_gif import SEEDS
from build_search_space_figure import (
    draw_structure,
    setup_axes,
    struct_center,
)

HERE = Path(__file__).resolve().parent
OUT = HERE / "media" / "fig-seed-designs.png"


def main():
    fig = plt.figure(figsize=(13.333, 7.5), dpi=200)
    fig.patch.set_facecolor("white")

    # 3 x 3 grid, specimen order left to right, top to bottom. Every cell
    # shares one mm scale: setup_axes picks the scale from the given span,
    # so the same span in every identical cell means the same mm/inch.
    cols, rows = 3, 3
    cw, ch = 1.0 / cols, 1.0 / rows
    for i, p in enumerate(SEEDS):
        r, c = divmod(i, cols)
        ax = fig.add_axes([c * cw + 0.012, (rows - 1 - r) * ch + 0.012,
                           cw - 0.024, ch - 0.024])
        cu, cv = struct_center(p)
        # Span sized so the tallest seed (H 104 mm plus twist overhang)
        # fits its cell; identical for all cells -> common scale.
        ppmm = setup_axes(ax, fig, (cu, cv), 125, 118)
        draw_structure(ax, p, ppmm)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor="white")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
