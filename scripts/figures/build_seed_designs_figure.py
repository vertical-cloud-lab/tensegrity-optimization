#!/usr/bin/env python3
"""Nine Sobol seed designs at one millimetre scale (fig:seed-designs).

Reads the as-printed (post-projection) geometry of specs 00 to 08 from
manuscript/data/t3-prism-bo-batch-print-key.csv and draws each with
t3_prism_render on one set of equal-aspect axes, 3 x 3, portrait, labelled
with the spec number and article ID, plus a shared 20 mm scale bar. Writes
figures/bo/fig-seed-designs.{pdf,png}.

Usage:  python3 scripts/figures/build_seed_designs_figure.py
"""
from __future__ import annotations

import math
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from campaign_data import INK, REPO, STYLE, seed_designs  # noqa: E402
from t3_prism_render import draw_prism  # noqa: E402

AZIM, ELEV = -20.0, 10.0
CELL_W = 86.0      # mm per grid column (widest seed ~ 84 mm projected)
LABEL_MM = 13.0    # one label line below each drawing
GAP_MM = 4.0       # between a label and the drawing below it


def _height(d):
    """Projected height of a design above its base point, in mm."""
    return (d["H"] * math.cos(math.radians(ELEV))
            + d["R"] * math.sin(math.radians(ELEV)) + 5.1)


def main() -> int:
    designs = seed_designs()
    assert len(designs) == 9
    rows = [designs[0:3], designs[3:6], designs[6:9]]
    # each row is as tall as its tallest drawing plus one label line
    row_h = [max(_height(d) for d in r) + 10.5 + LABEL_MM + GAP_MM for r in rows]
    total_h = sum(row_h)
    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(3.35, 3.35 * (total_h + 8.0) / (3 * CELL_W)))
        top = total_h
        for r, h in zip(rows, row_h):
            base = top - h + LABEL_MM + 10.5
            for col, d in enumerate(r):
                cx = (col + 0.5) * CELL_W
                draw_prism(ax, d["R"], d["H"], d["twist"], d["d_s"], d["d_t"],
                           x0=cx, y0=base, azim=AZIM, elev=ELEV)
                label = f"Spec {d['spec']}  {d['print_id']}"
                if not d["tested"]:
                    label += "*"
                ax.text(cx, base - 12.0, label, ha="center", va="top",
                        fontsize=7.5, color=INK)
            top -= h
        # 20 mm scale bar and the footnote for untested specs, below the grid
        x1 = 3 * CELL_W - 4.0
        ax.plot([x1 - 20.0, x1], [-3.0, -3.0], color=INK, lw=1.2, solid_capstyle="butt")
        ax.text(x1 - 22.5, -3.0, "20 mm", ha="right", va="center", fontsize=6.5, color=INK)
        ax.text(2.0, -3.0, "* printed, not drop-tested", ha="left", va="center",
                fontsize=6.5, color=INK, style="italic")
        ax.set_xlim(0, 3 * CELL_W)
        ax.set_ylim(-8.0, total_h)
        ax.set_aspect("equal")
        ax.axis("off")
        out = REPO / "figures" / "bo" / "fig-seed-designs"
        for ext in ("pdf", "png"):
            fig.savefig(f"{out}.{ext}", bbox_inches="tight", pad_inches=0.01,
                        facecolor="white",
                        metadata={"CreationDate": None} if ext == "pdf" else None)
        plt.close(fig)
    for d in designs:
        print(d["spec"], d["print_id"], d["R"], d["H"], d["twist"], d["d_s"], d["d_t"])
    print(f"wrote {out}.pdf and .png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
